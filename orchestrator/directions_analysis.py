"""Item5: independent directions, then operator comparison, without an executor.

The two registries use the existing authenticated intake. The later registry
adds exactly the operator idea. Only model-workspace delivery changes by phase;
operator authority and the full backlog never become scientific artifacts.
"""
import json
from pathlib import Path
from orchestrator import context_budget, manual_context
from orchestrator.manual_executor import digest, read
from orchestrator.scientific_intake import load_views

TASK = 'research-directions'
DOCUMENT = 'docs/DIRECTIONS_OPERATOR_DECISION.txt'
AUTHORITY = 'b00e7a398e77e67ae2e23d877a072e8be6981984acc08c4059c0063114f71b97'
PHASE1 = ('run_spec_author', 'run_spec_review')
PHASE2 = ('result_interpretation_author', 'result_interpretation_review')


def authority(root=None):
    root = Path(root) if root is not None else Path(__file__).resolve().parents[1]
    path = root/DOCUMENT
    if path.is_symlink() or digest(path.read_bytes()) != AUTHORITY:
        raise ValueError('DIRECTIONS_OPERATOR_AUTHORITY_CHANGED')
    return AUTHORITY


def bound(root, ref):
    if not isinstance(ref, dict) or set(ref) != {'path', 'sha256'}:
        raise ValueError('DIRECTIONS_REFERENCE_REQUIRED')
    raw = context_budget.relative_file(root, ref['path']).read_bytes()
    if digest(raw) != ref['sha256']:
        raise ValueError('DIRECTIONS_EVIDENCE_CHANGED')
    return raw


def validate_plan(plan):
    authority()
    cfg = plan['directions']; root = Path(plan['context'])
    if (set(cfg) != {'phase2_intake', 'operator_idea', 'completed_item2'}
            or digest(bound(root, plan['operator'])) != AUTHORITY):
        raise ValueError('DIRECTIONS_CONFIGURATION_OR_AUTHORITY')
    prior = cfg['completed_item2']
    if set(prior) != {'run_id', 'report'} or prior['run_id'] != 'stocktake-6b556dba36d299c05b8b7770':
        raise ValueError('DIRECTIONS_ITEM2_PREDECESSOR')
    bound(root, prior['report'])
    before = json.loads(bound(root, plan['private_intake']))
    after = json.loads(bound(root, cfg['phase2_intake']))
    idea = bound(root, cfg['operator_idea'])
    rows_before = before['views']; rows_after = after['views']
    extra = [row for row in rows_after if row not in rows_before]
    if (any(row not in rows_after for row in rows_before) or len(extra) != 1
            or {k: extra[0][k] for k in ('path', 'sha256')} != cfg['operator_idea']
            or len(rows_after) != len(rows_before)+1):
        raise ValueError('DIRECTIONS_PHASE2_MUST_ADD_ONLY_OPERATOR_IDEA')
    for ref, stages in [(plan['private_intake'], PHASE1), (cfg['phase2_intake'], PHASE2)]:
        for stage in stages:
            descriptors, _ = load_views(root, ref, stage=stage, idea_ids=plan['idea_ids'])
            if any(row.get('per_patient_material') for row in descriptors):
                raise ValueError('DIRECTIONS_AGGREGATES_ONLY')
    # The reviewed selection, not arbitrary full history, is the phase1 input.
    # Deny known late material on all delivery paths (inline and file-backed).
    forbidden = [bound(root, plan['backlog']), bound(root, plan['operator']), idea]
    for stage in PHASE1:
        for artifact in manual_context.selected_artifacts(stage, plan['artifacts']):
            raw = bound(root, {k: artifact[k] for k in ('path', 'sha256')})
            if any(value in raw for value in forbidden):
                raise ValueError('DIRECTIONS_EARLY_OPERATOR_IDEA')
        _, files = load_views(root, plan['private_intake'], stage=stage, idea_ids=plan['idea_ids'])
        if any(value in raw for _, raw in files for value in forbidden):
            raise ValueError('DIRECTIONS_EARLY_OPERATOR_IDEA')
    return True


def require_item2_complete(batch, context, cfg):
    prior = cfg['completed_item2']; raw = bound(context, prior['report'])
    row = batch.db.execute('SELECT status FROM autonomy_runs WHERE id=?', (prior['run_id'],)).fetchone()
    event = batch.db.execute('SELECT payload FROM events WHERE id=?', (prior['run_id']+':accepted',)).fetchone()
    if (row is None or row['status'] != 'COMPLETE' or event is None
            or json.loads(event['payload']).get('report_sha256') != digest(raw)):
        raise ValueError('DIRECTIONS_ITEM2_NOT_COMPLETE')


def phase1_receipt(driver, value):
    """Bind genuine completed author/reviewer output and the committed snapshot.

    No arbitrary phase flag can authorize a reveal. Both completed native call
    receipts must bind the exact immutable spec and its approving review.
    """
    target = driver.acceptance_path('spec')
    spec = (target/'SPEC.md').read_bytes(); review = (target/'review.json').read_bytes()
    verdict = json.loads(review)
    if verdict.get('verdict') != 'APPROVE' or verdict.get('findings') != []:
        raise ValueError('DIRECTIONS_PHASE1_NOT_APPROVED')
    if digest(Path(value['spec']).read_bytes()) != digest(spec) or digest(Path(value['spec_review']).read_bytes()) != digest(review):
        raise ValueError('DIRECTIONS_PHASE1_OUTPUT_CHANGED')
    calls = {}
    for stage, name, raw in [('run_spec_author', 'SPEC.proposed.md', spec), ('run_spec_review', 'review.json', review)]:
        rows = driver.store.db.execute('SELECT * FROM manual_calls WHERE stage=? AND status=?', (stage, 'COMPLETE')).fetchall()
        matches = [row for row in rows if json.loads(row['receipt']).get('output_sha256', {}).get(name) == digest(raw)]
        if len(matches) != 1:
            raise ValueError('DIRECTIONS_PHASE1_NATIVE_BINDING_REQUIRED')
        calls[stage] = {'id': matches[0]['id'], 'receipt_sha256': digest(matches[0]['receipt'].encode())}
    commit = value.get('spec_commit')
    if not commit:
        raise ValueError('DIRECTIONS_PHASE1_COMMIT_REQUIRED')
    for name, raw in [('SPEC.md', spec), ('review.json', review)]:
        rel = str((target/name).relative_to(driver.root))
        # git helper strips text; use raw plumbing for byte-exact comparison.
        import subprocess
        saved = subprocess.check_output(['git', 'show', commit+':'+rel], cwd=driver.root)
        if saved != raw:
            raise ValueError('DIRECTIONS_PHASE1_COMMIT_CHANGED')
    return {'schema': 'independent-directions/v1', 'run_id': driver.config['run_id'],
            'spec_sha256': digest(spec), 'review_sha256': digest(review), 'commit': commit, 'calls': calls}


def registry(driver, value, stage):
    if stage in PHASE1:
        return driver.config['private_intake']
    if stage not in PHASE2:
        raise ValueError('DIRECTIONS_STAGE')
    receipt = phase1_receipt(driver, value)
    if read(driver.state/'independent-directions.json') != receipt:
        raise ValueError('DIRECTIONS_PHASE1_RECEIPT_CHANGED')
    return driver.config['directions']['phase2_intake']


def check_delivery(driver, stage, text, measurement, work):
    if stage not in PHASE1:
        return
    refs = [driver.config['backlog'], driver.config['operator'], driver.config['directions']['operator_idea']]
    forbidden = [bound(driver.context, ref) for ref in refs]
    supplied = [text.encode()]+[(Path(work)/row['path']).read_bytes() for row in measurement['workspace_files']]
    if any(value in raw for raw in supplied for value in forbidden):
        raise ValueError('DIRECTIONS_EARLY_OPERATOR_IDEA')


def instructions(stage):
    common = ('Analysis only for the ISLES infarct-prediction project. Use the accepted stock-take and imported '
        'operator-run Sprint13A aggregates. Do not train, run notebooks, submit GPU/Modal jobs, or access patient-level data. '
        'For each direction give supporting AND opposing evidence, uncertainties, the cheapest informative first test '
        '(prefer post-hoc saved-prediction or CPU work), estimated cost with assumptions, risks and a recommendation. '
        'Propose tests only; no test is executed here. Preserve scientific disagreement and original judgments. ')
    if stage in PHASE1:
        return common + ('Phase1: independently generate and rank directions beyond Sprint13B. No operator ideas are supplied '
            'in this phase. Record substantive directions now, not a plan to think about them later. Give a ranked shortlist '
            'and the one or two tests to try first. Review the scientific reasoning independently. ')
    return common + ('Phase2: the independent Phase1 directions are already recorded and must remain unchanged. '
        'Now inspect the registered operator idea, treating its factual claims as attributed claims to verify against '
        'original aggregate evidence. Judge the idea and compare it with the independent directions using the same criteria; '
        'challenge both where evidence warrants. Finish with a ranked shortlist and one or two proposed first tests. '
        'State what changed after seeing the operator idea and why. The next decision is stop for Partho, not execution. ')
