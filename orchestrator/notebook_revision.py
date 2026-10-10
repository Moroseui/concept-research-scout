"""Bound safe-view notebook edits, never execution of an original notebook.

Only explicit visible-span replacements are accepted. The controller applies
them to an authenticated original in private memory, externalizes the one
already-omitted membership assignment, and writes a new scan-checked copy.
The original and every omitted byte remain preserved outside model workspaces.
"""
import ast
import copy
import difflib
import json
import re
from pathlib import Path

from orchestrator import scientific_intake as intake, private_records
from orchestrator.git_publication import scan as public_scan

SCHEMA = 'safe-notebook-patch/v1'
ORIGINAL = '73f656d542c033df30fdfca8a36d1bd2899fc1563d9d4effdf9ea634de164ef7'
VIEW = '04aeab89022993885cccf5438bb8fe3bf4604be3cdcab751e5f5cdaa1b2e2ce8'
EXTERNAL_PATH = '/content/drive/MyDrive/isles-pilot/sprint13-inputs-PRIVATE/excluded_cases.json'
SUCCESSOR_BASE = '9e62bec160153ae605d0e4f5a3121977256fbc08e5a25a9421279a127c169a46'
PATCH_LIMIT = 80000
REQUIRED_TESTS = ('test_fold_completeness', 'test_verdict_rule',
                  'test_coverage_handling', 'test_existing_unit_checks')


def strict_json(raw):
    def pairs(items):
        result = {}
        for k, v in items:
            if k in result:
                raise ValueError('NOTEBOOK_DUPLICATE_JSON_KEY')
            result[k] = v
        return result
    return json.loads(raw, object_pairs_hook=pairs,
                      parse_constant=lambda _: (_ for _ in ()).throw(ValueError('NOTEBOOK_NONFINITE_JSON')))


def scan(raw, cases):
    intake.scan(raw, cases, kind='code')
    public_scan('context/notebook-revision.txt', raw)


def partition(original, selection, cases, expected_view):
    view, manifest = intake.derive(original, selection, cases)
    if intake.sha(view) != expected_view:
        raise ValueError('NOTEBOOK_SAFE_VIEW_CHANGED')
    return view, manifest


def _external_assignment(chunk):
    """Never return the identifiers to a caller or a model-facing receipt."""
    tree = ast.parse(chunk.decode())
    if (len(tree.body) != 1 or not isinstance(tree.body[0], ast.Assign)
            or len(tree.body[0].targets) != 1
            or not isinstance(tree.body[0].targets[0], ast.Name)
            or tree.body[0].targets[0].id != 'EXCLUDED'):
        raise ValueError('NOTEBOOK_OMISSION_NOT_BOUND_MEMBERSHIP')
    values = ast.literal_eval(tree.body[0].value)
    if not isinstance(values, list) or not values or any(not isinstance(x, str) for x in values):
        raise ValueError('NOTEBOOK_MEMBERSHIP_LITERAL_SHAPE')
    payload = intake.canonical(values) + b'\n'
    pin = intake.sha(payload)
    loader = (
        '# Membership-only private input; never included in a model workspace.\n'
        'import hashlib as _membership_hashlib, json as _membership_json\n'
        f'_membership_bytes = open({EXTERNAL_PATH!r}, "rb").read()\n'
        f'assert _membership_hashlib.sha256(_membership_bytes).hexdigest() == {pin!r}, "Excluded membership hash changed"\n'
        'EXCLUDED = _membership_json.loads(_membership_bytes)\n'
        f'assert isinstance(EXCLUDED, list) and len(EXCLUDED) == {len(values)}, "Excluded membership count changed"\n'
        'del _membership_bytes\n'
    ).encode()
    return loader, {'path': EXTERNAL_PATH, 'sha256': pin, 'count': len(values),
                    'available_for_synthetic_tests': False}


def clean_source(source):
    lines = source.splitlines(keepends=True)
    magics = []
    if lines and lines[0].startswith('%%writefile '):
        if not re.fullmatch(r'%%writefile (?:-a )?/content/sprint13_pipeline.py\s*', lines[0]):
            raise ValueError('NOTEBOOK_UNREVIEWED_CELL_MAGIC')
        magics.append(lines[0].strip())
        lines[0] = '\n'
    if any(x.lstrip().startswith(('!', '%')) for x in lines):
        raise ValueError('NOTEBOOK_UNREVIEWED_SHELL_OR_MAGIC')
    return ''.join(lines), magics


def compile_notebook(raw):
    notebook = strict_json(raw)
    records = []
    for index, cell in enumerate(notebook['cells']):
        if cell['cell_type'] != 'code':
            continue
        source, magics = clean_source(''.join(cell['source']))
        try:
            compile(source, f'notebook-cell-{index}', 'exec', dont_inherit=True)
        except SyntaxError as error:
            records.append({'cell':index,'compile':'FAIL','line':error.lineno,'message':error.msg})
            continue
        records.append({'cell': index, 'source_sha256': intake.sha(source.encode()),
                        'compile': 'PASS', 'writefile_directives_not_executed': magics})
    return records


def apply(original, selection, patch_raw, cases, *, original_sha256=ORIGINAL, view_sha256=VIEW, patch_limit=PATCH_LIMIT):
    if intake.sha(original) != original_sha256:
        raise ValueError('NOTEBOOK_ORIGINAL_CHANGED')
    view, manifest = partition(original, selection, cases, view_sha256)
    if type(patch_limit) is not int or patch_limit not in {PATCH_LIMIT,96000}:
        raise ValueError('NOTEBOOK_PATCH_LIMIT_SCOPE')
    if len(patch_raw) > patch_limit:
        raise ValueError('NOTEBOOK_PATCH_LIMIT')
    scan(patch_raw, cases)
    patch = strict_json(patch_raw)
    if (not isinstance(patch, dict) or set(patch) != {'schema', 'original_sha256', 'view_sha256', 'edits'}
            or patch['schema'] != SCHEMA or patch['original_sha256'] != original_sha256
            or patch['view_sha256'] != view_sha256 or not isinstance(patch['edits'], list)
            or not 1 <= len(patch['edits']) <= 80):
        raise ValueError('NOTEBOOK_PATCH_BINDING')
    units = intake.notebook_units(original)
    changes = {}
    for edit in patch['edits']:
        if (not isinstance(edit, dict) or set(edit) != {'unit', 'start', 'end', 'before_sha256', 'replacement'}
                or not isinstance(edit['unit'], str)
                or not re.fullmatch(r'cells/[0-9]+/source', edit['unit'])
                or edit['unit'] not in units or type(edit['start']) is not int
                or type(edit['end']) is not int or not isinstance(edit['replacement'], str)):
            raise ValueError('NOTEBOOK_PATCH_EDIT_FIELDS')
        unit, start, end = edit['unit'], edit['start'], edit['end']
        raw, _ = units[unit]
        if not 0 <= start < end <= len(raw):
            raise ValueError('NOTEBOOK_PATCH_RANGE')
        if not any(s['keep'] and s['start'] <= start and end <= s['end'] for s in selection[unit]):
            raise ValueError('NOTEBOOK_PATCH_CROSSES_OMISSION')
        if intake.sha(raw[start:end]) != edit['before_sha256']:
            raise ValueError('NOTEBOOK_PATCH_BEFORE_CHANGED')
        raw[:start].decode(); raw[start:end].decode(); raw[end:].decode()
        replacement = edit['replacement'].encode()
        scan(replacement, cases)
        if any(start < e and end > s for s, e, _ in changes.get(unit, [])):
            raise ValueError('NOTEBOOK_PATCH_OVERLAP')
        changes.setdefault(unit, []).append((start, end, replacement))
    # One known non-public code span, already omitted by the approved intake.
    # Any newly encountered omission refuses; no general redaction heuristic.
    omitted_code = [s for s in manifest['spans'] if not s['keep'] and s['kind'] == 'code']
    if original_sha256 == SUCCESSOR_BASE:
        # The accepted item2 copy has already externalized membership. It is
        # wholly scan-safe source; never reinsert the historical literal or
        # allow a new hidden code span. Scope/approval remains controller-side.
        if omitted_code:
            raise ValueError('NOTEBOOK_SUCCESSOR_HIDDEN_CODE')
        scan(original, cases)
        omission = None
        membership = {'status': 'already externalized in reviewed base',
                      'base_sha256': SUCCESSOR_BASE,
                      'available_for_synthetic_tests': False}
    else:
        if len(omitted_code) != 1:
            raise ValueError('NOTEBOOK_MEMBERSHIP_OMISSION_COUNT')
        omission = omitted_code[0]
        if omission['unit'] != 'cells/4/source' or (omission['start'], omission['end']) != (2090, 2120):
            raise ValueError('NOTEBOOK_MEMBERSHIP_OMISSION_BINDING')
        raw = units[omission['unit']][0]
        loader, membership = _external_assignment(raw[omission['start']:omission['end']])
        changes.setdefault(omission['unit'], []).append((omission['start'], omission['end'], loader))
    before = strict_json(original)
    updated = copy.deepcopy(before)
    for unit, edits in changes.items():
        raw = units[unit][0]
        for start, end, replacement in sorted(edits, reverse=True):
            raw = raw[:start] + replacement + raw[end:]
        updated['cells'][int(unit.split('/')[1])]['source'] = raw.decode().splitlines(keepends=True)
    # Opaque notebook metadata/outputs were excluded by intake. No output is
    # copied or presented as newly computed. Code not edited above is unchanged.
    updated['metadata'] = {}
    for cell in updated['cells']:
        cell['metadata'] = {}
        cell.pop('attachments', None)
        cell.pop('id', None)
        if cell['cell_type'] == 'code':
            cell['outputs'] = []
            cell['execution_count'] = None
    derived = (json.dumps(updated, ensure_ascii=False, indent=1, allow_nan=False) + '\n').encode()
    scan(derived, cases)
    compile_results = compile_notebook(derived)
    # Diff the kept original source against revised source with the original
    # omitted region represented only by its hash, never its contents.
    diff_parts = []
    for i, cell in enumerate(updated['cells']):
        unit = f'cells/{i}/source'
        old = units[unit][0]
        for s in sorted((s for s in selection[unit] if not s['keep']), key=lambda s:s['start'], reverse=True):
            old = old[:s['start']] + ('# OMITTED ORIGINAL SPAN SHA256 '+intake.sha(old[s['start']:s['end']])+'\n').encode() + old[s['end']:]
        new = ''.join(cell['source'])
        if old.decode() != new:
            diff_parts.extend(difflib.unified_diff(old.decode().splitlines(True), new.splitlines(True),
                fromfile=f'original-safe/cell-{i}', tofile=f'revised/cell-{i}'))
    diff = ''.join(diff_parts).encode()
    scan(diff, cases)
    receipt = {'schema': 'notebook-patch-result/v1', 'original_sha256': original_sha256,
        'view_sha256': view_sha256, 'patch_sha256': intake.sha(patch_raw),
        'notebook_sha256': intake.sha(derived), 'diff_sha256': intake.sha(diff),
        'membership_input': membership, 'omitted_span_sha256': omission['sha256'] if omission else None,
        'compile': compile_results, 'original_unchanged': True,
        'scientific_approval': False, 'real_data_execution': False}
    return derived, diff, receipt


def instructions():
    return (
        '\nThe operator has expanded this same item2 to a NEW revised 13B notebook and synthetic-only CPU checks. '
        'The author writes SPEC.proposed.md and notebook.patch.json. The patch is JSON with exactly schema="safe-notebook-patch/v1", '
        f'original_sha256="{ORIGINAL}", view_sha256="{VIEW}", edits=[...]. Each edit has exactly unit '
        '("cells/N/source"), start,end (UTF-8 byte offsets in the ORIGINAL source unit), before_sha256 '
        '(hash of the exact replaced bytes), replacement (string). Use nonoverlapping edits wholly within one '
        'kept span of the bound safe view; no insertion into or crossing an omission. Replace a visible anchor '
        'if adding code. All rounds patch the same original, not a prior draft. Total patch at most80000bytes. '
        'The controller privately applies edits to the original, externalizes the already-omitted EXCLUDED '
        'membership assignment to a hash/count-checked private input, strips unexecuted metadata/outputs, '
        'scans and compiles a new copy, then runs synthetic tests without data or network. Never supply, '
        'guess, or request the omitted identifier. Original unchanged. No real notebook run is authorized. '
        'Make the actual executable paths resolve the current findings; expose the pure helpers required by '
        'notebook-synthetic-contract.md and use those SAME helpers in the notebook. Do not merely add test stubs. '
        'The independent reviewer inspects the actual diff, revised notebook and test receipts. '
        'Smoke execution, timing, baseline/environment receipts and real coverage provenance remain item4 '
        'preconditions, not evidence this item2 may fabricate and not blockers solely for being unexecuted. '
        'Any flaw in the revised code or synthetic tests remains a finding. Preserve these execution '
        'conditions explicitly in the proposal; the controller supplies carried-conditions.json. '
    )


AUTHORITY = '1a21e40fa29e7d4dec9f444b46604ab2d3b4167fa97f9f05fb21699f6ac90a42'


def bound(root, ref):
    from orchestrator.context_budget import relative_file
    if not isinstance(ref, dict) or set(ref) != {'path','sha256'}:
        raise ValueError('NOTEBOOK_CONFIG_REFERENCE')
    raw=relative_file(root,ref['path']).read_bytes()
    if intake.sha(raw)!=ref['sha256']:raise ValueError('NOTEBOOK_CONFIG_CHANGED')
    return raw


def validate_config(root, config):
    if isinstance(config,dict) and config.get('mode')=='item4-execution-revision':
        return validate_execution_config(root,config)
    from orchestrator.autonomy_backlog import load, require_item
    if not isinstance(config,dict) or set(config)!={
            'authority','selection','original','safe_view','environment','backlog','backlog_binding','item_sha256'}:
        raise ValueError('NOTEBOOK_REVISION_CONFIG_FIELDS')
    authority=bound(root,config['authority'])
    if intake.sha(authority)!=AUTHORITY:raise ValueError('NOTEBOOK_REVISION_AUTHORITY')
    backlog=load(bound(root,config['backlog']),strict_json(bound(root,config['backlog_binding'])),authority)
    require_item(backlog,2,config['item_sha256'],'analysis',completed_items=(1,))
    if config['original'].get('sha256')!=ORIGINAL or config['safe_view']['sha256']!=VIEW:
        raise ValueError('NOTEBOOK_REVISION_ORIGINAL_SELECTION')
    path=Path(config['original']['path'])
    if not path.is_absolute() or any(p.is_symlink() for p in (path,*path.parents)):
        raise ValueError('NOTEBOOK_REVISION_ORIGINAL_PATH')
    private_records.check(path)
    original=path.read_bytes()
    if intake.sha(original)!=ORIGINAL:raise ValueError('NOTEBOOK_ORIGINAL_CHANGED')
    selection=strict_json(bound(root,config['selection']))
    safe=bound(root,config['safe_view'])
    if intake.sha(safe)!=VIEW:raise ValueError('NOTEBOOK_SAFE_VIEW_CHANGED')
    if set(config['environment'])!={'environment_root','environment_sha256'}:
        raise ValueError('NOTEBOOK_SYNTHETIC_ENVIRONMENT')
    return original,selection


def carried_conditions(original_findings=()):
    return {
        'status':'HELD_FOR_BACKLOG_ITEM_4',
        'execution_authorized':False,
        'conditions':[
            'Operator-approved experiment and dollar budget in BACKLOG item4.',
            'Reviewed exact runnable package, development cohort and frozen five-fold split identities.',
            'Actual smoke execution, recovery proof and measured timing before full arms.',
            'Baseline and independent repeat identities, RNG and environment receipts.',
            'Actual finite/spatial coverage provenance; synthetic support is not patient evidence.',
            'Private excluded-membership file must match the new notebook hash/count before any future execution.'
        ],
        'source':'Operator notebook-revision decision; preserves execution aspects of F-SELF-REVIEW-NOT-OPPOSING.',
        'scientific_acceptance':False,
        'original_finding_records':list(original_findings)
    }


def prepare_artifacts(driver, value, pending, cases):
    from orchestrator.manual_executor import read, digest
    from orchestrator.manual_driver import write_once
    from orchestrator import notebook_synthetic
    cfg=driver.config['notebook_revision']
    original,selection=validate_config(driver.context,cfg)
    work=Path(pending['workspace'])
    patch=(work/'notebook.patch.json').read_bytes()
    limit=PATCH_LIMIT
    if (driver.config.get('run_id')=='experiment-a74959ac4546a982af4ae137' and
            (pending.get('stage'),pending.get('round'),pending.get('id'))==('run_spec_author',24,
             '4a171e924b528328d4a4827815113449b39d19143a8824b92f17dce0ecf0b8ca')):
        limit=96000
    notebook,diff,receipt=apply(original,selection,patch,cases,
        original_sha256=cfg['original']['sha256'],view_sha256=cfg['safe_view']['sha256'],patch_limit=limit)
    folder=driver.state/'notebook-revisions'/('author-'+str(pending['round']))
    write_once(folder/'revised.ipynb',notebook)
    write_once(folder/'notebook.diff',diff)
    write_once(folder/'patch-receipt.json',intake.canonical(receipt))
    options = {'execution':True} if cfg.get('mode')=='item4-execution-revision' else {}
    tests=(notebook_synthetic.run(folder/'synthetic',notebook,cfg['environment'],**options)
           if all(x['compile']=='PASS' for x in receipt['compile']) else
           {'status':'FAIL','reason':'COMPILE_FAILED_NO_EXECUTION','compile':receipt['compile'],
            'patient_data':False,'no_model_call':True})
    scan(intake.canonical(tests),cases)
    if cfg.get('mode')=='item4-execution-revision':
        # Preserve historical conditions verbatim. Current operator scope is a
        # separately bound artifact; this does not silently settle findings.
        conditions=bound(driver.context,cfg['carried_conditions'])
    else:
        from orchestrator.notebook_revision_transition import checkpoint, prior
        from tools.deploy_manual_lane import bound as host_path
        # Always retain the genuine second-review condition, even if a later
        # review only requests a code revision and does not repeat this condition.
        host=Path(read(driver.state/'notebook-continuation.json')['filesystem_root'])
        original_state=prior(host)[1]
        review_raw=host_path(host,original_state['review']).read_bytes()
        current_review=read(host_path(host,original_state['review']))
        if digest(review_raw)!=checkpoint()['review_sha256']:
            raise ValueError('NOTEBOOK_CARRIED_REVIEW_CHANGED')
        carried=[{'review_sha256':digest(review_raw),'finding':row,'scope':'BACKLOG item4 execution conditions'}
                 for row in current_review['findings'] if row['category']=='execution authority/provenance']
        conditions=intake.canonical(carried_conditions(carried))
    write_once(folder/'carried-conditions.json',conditions)
    for typ,name,raw in [
        ('notebook_source','revised-13B-'+str(pending['round'])+'.ipynb',notebook),
        ('notebook_diff','13B-diff-'+str(pending['round'])+'.patch',diff),
        ('notebook_patch','13B-patch-'+str(pending['round'])+'.json',patch),
        ('synthetic_tests','13B-tests-'+str(pending['round'])+'.json',intake.canonical(tests)),
        ('notebook_provenance','13B-provenance-'+str(pending['round'])+'.json',intake.canonical(receipt)),
        ('execution_conditions','13B-execution-conditions-'+str(pending['round'])+'.json',conditions)]:
        driver.artifact(value,typ,name,raw,pending['round'])
    value['notebook_revision_result']={
        'folder':str(folder),'notebook_sha256':digest(notebook),'diff_sha256':digest(diff),
        'tests_sha256':digest(intake.canonical(tests)),'synthetic_status':tests['status']}
    if intake.sha(Path(cfg['original']['path']).read_bytes())!=cfg['original']['sha256']:
        raise ValueError('NOTEBOOK_ORIGINAL_CHANGED_AFTER_PATCH')


def successor_instructions(view_sha256):
    """Contract for the item4 author's new copy; no scientific method prescribed."""
    if not isinstance(view_sha256,str) or not re.fullmatch('[a-f0-9]{64}',view_sha256):
        raise ValueError('NOTEBOOK_SAFE_VIEW_CHANGED')
    return (
        'The base is the preserved, reviewed item2 13B notebook copy, not its older original. '
        'Write SPEC.proposed.md and notebook.patch.json using safe-notebook-patch/v1, '
        f'original_sha256={SUCCESSOR_BASE}, view_sha256={view_sha256}. '
        'Each edit has unit=cells/N/source, start/end UTF-8 byte offsets, before_sha256, '
        'and replacement. Use nonoverlapping replacements inside visible source spans; '
        'replace a visible anchor when adding code. All revision rounds patch this same '
        'reviewed base. Limit the complete patch to80000bytes. The controller applies it '
        'to a NEW private copy and preserves the base, then scans, compiles and runs '
        'synthetic-only tests. Never reconstruct omitted membership or read patient data. '
        'You own the scientific rule and notebook code, including the coverage decision '
        'and Modal adaptation. Codex coverage survey/proposal is attributed collaborator '
        'input, not an approved method. Judge it independently against the original sources. '
        'The existing %%writefile /content/sprint13_pipeline.py cell and its -a append cells '
        'must emit one importable module, with main(input_root, output_root, contract), '
        'preprocess(input_root, output_root, contract), validate_preprocessing(output_root, contract), '
        'and synthetic_tests() returning a nonempty unittest.TestSuite. Put real work inside these functions, '
        'not at module import; use only declared input/output roots and the frozen operation contract. '
        'The controller exports those exact writefile bytes, imports them and runs your tests '
        'in the no-network synthetic sandbox, in addition to the existing notebook unit checks. '
        'Do not add a second overwrite cell. The reviewed module is the code later packaged for execution. '
        'Use the infrastructure execution/checkpoint interface without changing scientific '
        'choices merely to satisfy a test. The independent reviewer judges the actual '
        'notebook diff, rule and test evidence. No real-data, GPU or provider operation '
        'occurs in this author workspace; later execution requires the ordinary gates.'
    )


SUCCESSOR_VIEW = '576f1b5a7d5e9f1d901c3bbe9848b71b3cf49106b9389a90060f24aa8593e782'
SCIENTIFIC_OWNERSHIP = '763aaa061576a3d8fffab9e8fd93073a3e7db4c78ce963543ce770b349a537af'
CARRIED_CONDITIONS = '077b82acb5d028c1c645e9598e6abd4c472f6bce6027708752cb24362cd2d6d2'


def validate_execution_config(root, config):
    """Exact approved item4, existing reviewed base and preserved conditions.

    This authorizes preparing a new notebook copy, not training, upload or spend.
    Provider admission still requires the independently approved resulting spec.
    """
    from orchestrator.autonomy_backlog import load, require_item
    from orchestrator.modal_item4_budget import AUTHORITY as execution_authority
    expected={'mode','authority','scientific_ownership','selection','original',
              'safe_view','environment','backlog','backlog_binding','item_sha256','carried_conditions'}
    if not isinstance(config,dict) or set(config)!=expected or config['mode']!='item4-execution-revision':
        raise ValueError('NOTEBOOK_EXECUTION_CONFIG_FIELDS')
    authority=bound(root,config['authority'])
    if intake.sha(authority)!=execution_authority:
        raise ValueError('NOTEBOOK_EXECUTION_AUTHORITY')
    if intake.sha(bound(root,config['scientific_ownership']))!=SCIENTIFIC_OWNERSHIP:
        raise ValueError('NOTEBOOK_SCIENTIFIC_OWNERSHIP_CHANGED')
    backlog=load(bound(root,config['backlog']),strict_json(bound(root,config['backlog_binding'])),authority)
    require_item(backlog,4,config['item_sha256'],'gpu',completed_items=(1,2,3))
    if (not isinstance(config['original'],dict) or set(config['original'])!={'path','sha256'}
            or config['original']['sha256']!=SUCCESSOR_BASE or config['safe_view']['sha256']!=SUCCESSOR_VIEW):
        raise ValueError('NOTEBOOK_EXECUTION_REVIEWED_BASE_REQUIRED')
    path=Path(config['original']['path'])
    if not path.is_absolute() or any(p.is_symlink() for p in (path,*path.parents)):
        raise ValueError('NOTEBOOK_REVISION_ORIGINAL_PATH')
    private_records.check(path)
    original=path.read_bytes()
    if intake.sha(original)!=SUCCESSOR_BASE:
        raise ValueError('NOTEBOOK_ORIGINAL_CHANGED')
    selection=strict_json(bound(root,config['selection']))
    if intake.sha(bound(root,config['safe_view']))!=SUCCESSOR_VIEW:
        raise ValueError('NOTEBOOK_SAFE_VIEW_CHANGED')
    if intake.sha(bound(root,config['carried_conditions']))!=CARRIED_CONDITIONS:
        raise ValueError('NOTEBOOK_EXECUTION_CONDITIONS_CHANGED')
    if not isinstance(config['environment'],dict) or set(config['environment'])!={'environment_root','environment_sha256'}:
        raise ValueError('NOTEBOOK_SYNTHETIC_ENVIRONMENT')
    return original,selection
