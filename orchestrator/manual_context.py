"""Step(d) manual-lane input builders. Pure assembly: never execute or admit work.

The driver/executor connection is step(d), not implemented by this module.
Unselected records remain at their original paths. Review findings are supplied
only by the exact-quote project register, never by a review transcript artifact.
"""
from pathlib import Path
import json
from orchestrator import private_records
from orchestrator import context_budget as budget
from orchestrator.manual_contract import NEXT_INSTRUCTION, READABILITY_INSTRUCTION
from orchestrator.git_publication import scan

STAGE_ARTIFACT_TYPES = {
    "run_spec_author": ("question", "run_spec", "notebook_source", "configuration", "metric_contract", "prior_results", "data_contract", "validator", "result_tables"),
    "run_spec_review": ("question", "run_spec", "notebook_source", "configuration", "metric_contract", "prior_results", "data_contract", "validator", "result_tables", "proposed_run_spec"),
    "result_interpretation_author": ("question", "run_spec", "notebook_source", "configuration", "metric_contract", "execution_manifest", "execution_receipt", "package_manifest", "result_tables", "validation_result", "prior_results"),
    "result_interpretation_review": ("question", "run_spec", "notebook_source", "configuration", "metric_contract", "execution_manifest", "execution_receipt", "package_manifest", "result_tables", "validation_result", "prior_results", "interpretation", "investigator_next_decision", "interpretation_original", "interpretation_format_repair"),
}
NOTEBOOK_TYPES = ("notebook_diff", "notebook_patch", "synthetic_tests", "notebook_provenance", "execution_conditions")
PROGRAM_TYPES = ("analysis_source", "analysis_tests", "analysis_provenance")
for _stage in STAGE_ARTIFACT_TYPES:
    STAGE_ARTIFACT_TYPES[_stage] += NOTEBOOK_TYPES + PROGRAM_TYPES

WORKSPACE_TYPES = {"notebook_source", "result_tables", "package_manifest", "interpretation",
                   "investigator_next_decision", "interpretation_original", *NOTEBOOK_TYPES, *PROGRAM_TYPES}

OUTPUTS = {
    "run_spec_author": ("SPEC.proposed.md",),
    "run_spec_review": ("review.json",),
    "result_interpretation_author": ("interpretation.md", "investigator_next_decision.json"),
    "result_interpretation_review": ("review.json",),
}
# Explicitly not model inputs, even if present in the artifact inventory.
OPERATOR_ONLY_TYPES = {"review_transcript", "unreviewed_tail", "old_prompt", "operator_configuration", "patient_data"}

JSON_PAGE_LINES = 100
JSON_PAGE_BYTES = 16000
JSON_READING = ('Read this JSON with offset and limit, at most 100 lines per read; '
                'continue through the relevant records. A readable_json copy preserves '
                'the original JSON values; its original_path and original_sha256 bind '
                'the unchanged original. Neither representation is a scientific judgment.')


def workspace_artifact(kind, *, artifact_id=None, private_intake=None, reference_prior_results=False):
    """One delivery rule shared by assembly and downstream evidence checks."""
    return (kind in WORKSPACE_TYPES or (reference_prior_results and kind=='prior_results')
            or (private_intake is not None and kind=='validation_result')
            or (kind=='configuration' and ((private_intake is not None and artifact_id in {
                'current-reviewed-notebook-selection','item4-current-backlog-selection',
                'item4-operator-document-1','item4-operator-document-2','item4-operator-document-3',
                'item4-operator-document-4','item4-operator-document-5','spec-size-guidance','provenance-guidance'})
                or artifact_id in {'authored-execution-plan','provenance-validators','current-six-item-backlog'}))
            or (kind=='validator' and artifact_id=='validator')
            or (kind in {'run_spec','proposed_run_spec'} and (artifact_id==kind or
                (kind=='run_spec' and artifact_id=='author5-original-SPEC.proposed.md'))))


def _pageable_json(raw):
    """Semantically identical JSON representation for line-based Read tools.

    Reject ambiguous/nonfinite JSON and oversized pages, rather than clipping
    evidence. The byte bound is conservative; it is not a measured token count.
    """
    def pairs(items):
        value = {}
        for key, item in items:
            if key in value:
                raise budget.ContextError('MANUAL_JSON_DUPLICATE_KEY')
            value[key] = item
        return value

    def constant(_):
        raise budget.ContextError('MANUAL_JSON_NONFINITE')

    value = json.loads(raw, object_pairs_hook=pairs, parse_constant=constant)
    pretty = (json.dumps(value, ensure_ascii=False, sort_keys=True,
                         indent=2, allow_nan=False) + '\n').encode('utf-8')
    lines = pretty.splitlines(keepends=True)
    lengths = [len(line) for line in lines]
    size = sum(lengths[:JSON_PAGE_LINES])
    largest = size
    for start in range(1, len(lines)):
        size -= lengths[start-1]
        if start+JSON_PAGE_LINES-1 < len(lines):
            size += lengths[start+JSON_PAGE_LINES-1]
        largest = max(largest, size)
    if largest > JSON_PAGE_BYTES:
        raise budget.ContextError('MANUAL_JSON_PAGE_TOO_LARGE')
    return pretty


def _json_reading_copy(descriptor, raw):
    pretty = _pageable_json(raw)
    scan('context/readable-metadata.json', pretty)
    pin = budget.sha(pretty)
    copy = {'id': descriptor['id'] + '-readable-json',
            'path': 'evidence/' + pin + '-' + budget.sha(descriptor['id'].encode('utf-8')) + '-readable.json', 'sha256': pin,
            'original_path': descriptor['path'], 'original_sha256': descriptor['sha256'],
            'bytes': len(pretty), 'characters': len(pretty.decode('utf-8')),
            'page_lines': JSON_PAGE_LINES, 'delivery': JSON_READING}
    descriptor['readable_json'] = copy
    return copy, pretty


def selected_artifacts(stage, artifacts):
    """Caller-saved logical identities and numeric revisions; never download suffix order.

    Equal revisions with different bindings are ambiguous and refuse. Unknown
    types refuse rather than silently hiding a misspelled required artifact.
    """
    if stage not in STAGE_ARTIFACT_TYPES:
        raise budget.ContextError("MANUAL_CONTEXT_STAGE")
    known = set().union(*map(set, STAGE_ARTIFACT_TYPES.values())) | OPERATOR_ONLY_TYPES
    latest = {}
    for row in artifacts:
        if set(row) != {"id", "type", "version", "path", "sha256"}:
            raise budget.ContextError("MANUAL_ARTIFACT_FIELDS")
        if (row["type"] not in known or not isinstance(row["id"], str) or not row["id"]
                or type(row["version"]) is not int or row["version"] < 1):
            raise budget.ContextError("MANUAL_ARTIFACT_ID_TYPE_VERSION")
        if row["type"] not in STAGE_ARTIFACT_TYPES[stage]:
            continue
        key = (row["type"], row["id"])
        old = latest.get(key)
        if old and row["version"] == old["version"] and old != row:
            raise budget.ContextError("MANUAL_ARTIFACT_AMBIGUOUS_VERSION")
        if old is None or row["version"] > old["version"]:
            latest[key] = row
    return [latest[key] for key in sorted(latest)]


def build(root, *, stage, idea_ids, task, artifacts, workspace=None, project="isles24-prediction", private_intake=None, structured_review=False, reference_prior_results=False, notebook_patch=False, execution_mode=None, analysis_program=False, execution_plan=False):
    """Complete file-writing model input, with scanner and final character bound.

    Artifact files must be source-bound current views or originals under root.
    Creating such a view does not interpret results or approve scientific use.
    No claims about absent artifacts are inferred from their omission.
    """
    if not idea_ids or any(not isinstance(x, str) or not x for x in idea_ids):
        raise budget.ContextError("MANUAL_CONTEXT_TARGET")
    if notebook_patch and (stage != "run_spec_author" or not structured_review or private_intake is None):
        raise budget.ContextError("NOTEBOOK_PATCH_OUTPUT_SCOPE")
    if execution_mode not in (None, "sprint13b-execution", "directions-diagnostics"):
        raise budget.ContextError("MANUAL_EXECUTION_MODE")
    if execution_mode is not None and (not structured_review or private_intake is None
            or idea_ids[0] != execution_mode):
        raise budget.ContextError("MANUAL_EXECUTION_SCOPE")
    if analysis_program and (stage != "run_spec_author" or
            execution_mode != "directions-diagnostics" or notebook_patch):
        raise budget.ContextError("ANALYSIS_PROGRAM_OUTPUT_SCOPE")
    if execution_plan and (stage != "run_spec_author" or execution_mode != "sprint13b-execution" or not notebook_patch):
        raise budget.ContextError("EXECUTION_PLAN_OUTPUT_SCOPE")
    selected = selected_artifacts(stage, artifacts)
    if execution_mode is not None and stage.startswith("result_interpretation"):
        required = {"run_spec", "execution_receipt", "execution_manifest", "package_manifest",
                    "validation_result", "result_tables"}
        missing = required - {row["type"] for row in selected}
        if missing:
            raise budget.ContextError("EXECUTION_EVIDENCE_REQUIRED:" + ",".join(sorted(missing)))
    outputs = OUTPUTS[stage] + (("notebook.patch.json",) if notebook_patch else ())
    outputs += (("analysis.program.json",) if analysis_program else ())
    outputs += (("execution.plan.json",) if execution_plan else ())
    pieces = []
    if stage in {'run_spec_review', 'result_interpretation_review'}:
        from orchestrator.scientific_search import INSTRUCTION
        pieces.append(INSTRUCTION)
    files = []
    private_descriptors = []
    private_index = None
    if private_intake is not None:
        if workspace is None:
            raise budget.ContextError('MANUAL_WORKSPACE_REQUIRED')
        from orchestrator.scientific_intake import load_views
        private_descriptors, private_files = load_views(root, private_intake,
            stage=stage, idea_ids=idea_ids)
        # Retain every registered original. Omission metadata may exceed native
        # Read's token limit on one line, so also deliver an authenticated copy.
        for descriptor, raw in list(private_files):
            if descriptor['path'].endswith('-omissions.json'):
                private_files.append(_json_reading_copy(descriptor, raw))
        # Full descriptor and omission metadata belongs in one authenticated
        # navigation file, not repeated in the initial context for every view.
        # This changes representation only: scan and bind every view first, keep
        # all files readable, and retain the full inventory in the measurement.
        index_raw = _pageable_json(budget.encoded({'schema': 'private-scientific-navigation/v1',
            'registry_sha256': private_intake['sha256'],
            'views': private_descriptors}).encode('utf-8'))
        index_sha = budget.sha(index_raw)
        scan('evidence/' + index_sha + '-private-index.json', index_raw)
        private_index = {'id': 'private-scientific-navigation',
            'path': 'evidence/' + index_sha + '-private-index.json', 'sha256': index_sha,
            'bytes': len(index_raw), 'characters': len(index_raw.decode('utf-8')),
            'registry_sha256': private_intake['sha256'], 'view_files': len(private_descriptors),
            'delivery': 'Read this index to discover all selected scientific views, exact origins, omissions and per-patient reasons. '
                'Then inspect the relevant bound files. Availability is not inspection or scientific acceptance. '
                + JSON_READING}
        pieces.append(budget.encoded(private_index))
        files.extend(private_files)
        files.append((private_index, index_raw))
    # A historical spec can still quote a formerly open finding. Deliver its
    # authenticated current status and exact cited resolution, rather than
    # making the model infer closure from a missing open-obligation entry.
    compact_navigation = (private_intake is not None and execution_mode == 'sprint13b-execution'
                          and stage in {'run_spec_author','run_spec_review'})
    finding_index = []
    _, _, register = budget.load(root)
    for row in register:
        if row['type'] != 'adverse finding' or not budget.in_scope(
                row, project, idea_ids, stage, include_closed=True):
            continue
        if workspace is None:
            raise budget.ContextError('MANUAL_WORKSPACE_REQUIRED')
        raw = budget.encoded(row).encode('utf-8')
        scan('context/current-finding.json', raw)
        h = budget.sha(raw)
        descriptor = {'id': row['id'], 'status': row['status'],
            'severity': row['severity'], 'source': row['source'],
            'resolution': ({k: v for k, v in row['disposition'].items() if k != 'text'}
                           if row['status'] == 'closed' else None),
            'path': 'evidence/' + h + '-finding.json', 'sha256': h,
            'bytes': len(raw), 'characters': len(raw.decode('utf-8')),
            'delivery': 'Exact finding and cited closure; read before judging historical claims.'}
        finding_index.append(descriptor)
        files.append((descriptor, raw))
    finding_navigation = finding_index
    if compact_navigation:
        raw = _pageable_json(budget.encoded(finding_index).encode('utf-8'))
        scan('context/current-findings-index.json', raw)
        pin = budget.sha(raw)
        finding_navigation = {'id':'current-findings-index', 'path':'evidence/'+pin+'-findings.json',
            'sha256':pin, 'bytes':len(raw), 'characters':len(raw.decode('utf-8')),
            'delivery':'Mandatory current finding status and exact closure index. Read completely. '+JSON_READING}
        files.append((finding_navigation,raw))
    approval_navigation = []
    for row in selected:
        raw = budget.relative_file(root, row["path"]).read_bytes()
        if budget.sha(raw) != row["sha256"]:
            raise budget.ContextError("MANUAL_ARTIFACT_CHANGED:" + row["id"])
        scan("context/current-artifact.txt", raw)
        if workspace_artifact(row["type"], artifact_id=row["id"], private_intake=private_intake, reference_prior_results=reference_prior_results):
            if workspace is None:
                raise budget.ContextError("MANUAL_WORKSPACE_REQUIRED")
            path = "evidence/" + row["sha256"] + "-" + budget.sha(row["id"].encode("utf-8")) + "-" + row["type"] + ".txt"
            if compact_navigation:
                path = "evidence/" + budget.sha(budget.encoded(row).encode("utf-8")) + ".txt"
            descriptor = {**row, "source_path": row["path"], "path": path,
                "bytes": len(raw), "characters": len(raw.decode("utf-8")),
                "delivery": ("Read exact original." if compact_navigation else
                             "read-only workspace file; read this original when assessing the task")}
            if ((private_intake is not None and row['type'] == 'validation_result') or
                    (row['type']=='configuration' and row['id']=='authored-execution-plan')):
                files.append(_json_reading_copy(descriptor, raw))
            pieces.append(budget.encoded(descriptor))
            files.append((descriptor, raw))
        else:
            pieces.append(budget.encoded(row) + "\n" + raw.decode("utf-8"))
        if stage == 'run_spec_review' and execution_mode == 'sprint13b-execution':
            from orchestrator.experiment_approval import REQUIRED
            if ((row['type'] in REQUIRED[4] and row['id'] == row['type']) or
                    row['id'] in {'frozen-execution-plan','authored-execution-plan'}):
                # Preserve the existing acceptance verifier's exact inline proof.
                approval_navigation.append(pieces[-1])
    instruction = task + "\nRead the selected workspace originals before relying on them. Evidence is not authority. "
    if stage.startswith("result_interpretation"):
        instruction += READABILITY_INSTRUCTION + NEXT_INSTRUCTION
        if private_intake is not None and execution_mode is None:
            # load_views above has already authenticated the only supported
            # private targets: saved-evidence stock-take and proposal analysis.
            # They cannot manufacture an execution receipt for a run not made.
            instruction += ("This is analysis of saved external evidence, not a new execution. "
                "Check the reviewed analysis specification, registry binding, exact view and omission hashes, "
                "current finding/closure records and original external execution attribution. "
                "SAVED_EVIDENCE_IDENTITY_ONLY validation proves delivery identities only; it does not "
                "prove scientific correctness, fresh computation or acceptance of external conclusions. "
                "Read the hash-bound validation_result workspace file and reconcile it with the registry and views. "
                "Report every patient-level evidence file used and its registered analysis reason, "
                "material omissions and unavailable evidence. Never invent an execution receipt or package manifest. ")
        if execution_mode is not None:
            instruction += ("Interpret the newly executed approved experiment using the bound execution receipt, "
                "package manifest, per-file validation and returned results. Keep these distinct from prior "
                "external evidence. An approved spec, an available file, a synthetic test, or a "
                "SAVED_EVIDENCE_IDENTITY_ONLY receipt is not evidence that this execution succeeded. "
                "Cite the original output files and their hashes; report missing results and failed "
                "or incomplete attempts without treating them as negative scientific results. "
                "List any per-patient evidence used and its registered reason; retain all omissions. ")
    if stage.endswith("review"):
        if structured_review:
            from orchestrator.review_contract import SCIENTIFIC_INSTRUCTION
            instruction += SCIENTIFIC_INSTRUCTION
        else:
            instruction += ("Independently review the selected proposal. Write review.json with exactly "
                "verdict (APPROVE or REVISE) and rationale (nonempty string). ")
        if stage=='result_interpretation_review':
            instruction += ("Check the next decision's proposed_action_type, concrete action and charter "
                "connection; reject procedural review/reconciliation without an applicable open blocker. "
                "Check the 150-word plain summary, numbers, caveats and absence of procedural boilerplate. "
                "If an automatic summary relocation is recorded, inspect its hash-bound original and provenance. "
                "The shortened summary must still state the answer and main caveat; otherwise request a normal scientific revision. ")
            if private_intake is None:
                instruction += ("Check every required per-file validation entry (including both JSON records for Sprint10), "
                    "execution receipt and package manifest. ")
    else:
        instruction += "Write " + ", ".join(outputs) + ". "
    instruction = "Work only in this stage workspace; do not execute experiments or other model calls.\n" + instruction
    instruction += ('\nHistorical statements about findings describe their original time. '
        'Use the current finding status index and inspect its exact finding/closure records. '
        'A closed finding is not an open blocker; a new concern requires its own evidence. '
        'Closure does not erase the original judgment or prove later execution succeeded.\n')
    # Keep every open obligation verbatim inline. The item4 author's long
    # interface/output instructions (and the exact review task) use scanned, read-only file
    # delivery as source artifacts, before final measurement and materialization.
    if stage in {'run_spec_author','run_spec_review'} and execution_mode == 'sprint13b-execution':
        if workspace is None:
            raise budget.ContextError('MANUAL_WORKSPACE_REQUIRED')
        raw = instruction.encode('utf-8')
        scan('context/scientific-author-instructions.txt', raw)
        pin = budget.sha(raw)
        role = 'author' if stage.endswith('author') else 'review'
        descriptor = {'id':'scientific-'+role+'-instructions',
            'path':'evidence/' + pin + '-'+role+'-instructions.txt', 'sha256':pin,
            'bytes':len(raw), 'characters':len(instruction),
            'delivery':'Mandatory exact scientific task, runtime interfaces and output requirements; read completely before this stage.'}
        files.append((descriptor,raw))
        pieces.append(budget.encoded(descriptor))
        instruction = ('Read the complete scientific-'+role+'-instructions file identified in CURRENT ARTIFACTS '
            'before this stage. It contains the exact task, scientific runtime interface and output schema. '
            'All open obligations remain verbatim below. Use only synthetic checks in this stage workspace; '
            'no patient computation, provider operations or other model calls. Scientific author owns code; '
            'independent review and ordinary execution admission remain required. No instruction was shortened '
            'or omitted: the bound file is mandatory task input, not optional evidence.')
    artifacts = "\n\n".join(pieces)
    if stage == 'run_spec_review' and execution_mode == 'sprint13b-execution':
        # Move exact navigation, never open findings, into a mandatory bound file.
        # This uses the existing immutable workspace route and reader byte bound.
        raw = artifacts.encode('utf-8')
        scan('context/scientific-review-artifact-index.txt', raw)
        lengths = [len(line) for line in raw.splitlines(keepends=True)]
        if any(size > JSON_PAGE_BYTES for size in lengths):
            raise budget.ContextError('MANUAL_ARTIFACT_NAVIGATION_LINE_TOO_LARGE')
        page_lines = JSON_PAGE_LINES
        while any(sum(lengths[i:i+page_lines]) > JSON_PAGE_BYTES for i in range(len(lengths))):
            page_lines -= 1
        pin = budget.sha(raw)
        descriptor = {'id':'scientific-review-artifact-index',
            'path':'evidence/' + pin + '-review-artifact-index.txt', 'sha256':pin,
            'bytes':len(raw), 'characters':len(artifacts), 'page_lines':page_lines,
            'delivery':'Mandatory complete artifact navigation, copied byte-for-byte. Read with offset and limit, '
                'at most ' + str(page_lines) + ' lines per read; follow every required source reference.'}
        files.append((descriptor,raw))
        artifacts = '\n\n'.join([budget.encoded(descriptor),*approval_navigation])
        instruction = ('First read the complete scientific-review-artifact-index file named in CURRENT ARTIFACTS. '
            'It contains the exact artifact navigation and mandatory instruction-file reference. ' +
            instruction.replace('identified in CURRENT ARTIFACTS', 'identified in that artifact index'))
    body, measured = budget.assemble(root, project=project, idea_ids=idea_ids, stage=stage,
        task=instruction, artifacts=artifacts,
        extra={'CURRENT FINDING STATUS (exact records in workspace)': budget.encoded(finding_navigation)})
    # No caller may append hidden history/schema after this final measurement.
    budget.dispatch_preflight(root, project=project, idea_ids=idea_ids, stage=stage, text=body)
    # No sendable input is returned, or workspace material delivered, on a stop.
    # Materialization is part of input preparation, not an executor or admission.
    delivered = _workspace_files(workspace, files) if files else []
    return body, {**measured, "stage": stage, "selected_artifacts": selected,
        "artifact_types": list(STAGE_ARTIFACT_TYPES[stage]), "outputs": list(outputs),
        "workspace_files": delivered, "finding_status": finding_index,
        **({"execution_mode": execution_mode} if execution_mode is not None else {}),
        **({'private_scientific_views': private_descriptors, 'private_scientific_index': private_index}
           if private_intake is not None else {})}


def _workspace_files(workspace, files):
    """Deliver exact scanner-checked bytes, never overwrite a differing file."""
    workspace = Path(workspace).absolute()
    for path in (workspace, *workspace.parents):
        if path.is_symlink():
            raise budget.ContextError("MANUAL_WORKSPACE_SYMLINK")
    private_records.mkdir(workspace,parents=True, exist_ok=True, mode=0o700)
    evidence = workspace / "evidence"
    if evidence.is_symlink():
        raise budget.ContextError("MANUAL_WORKSPACE_SYMLINK")
    private_records.mkdir(evidence,exist_ok=True, mode=0o700)
    for descriptor, raw in files:
        path = workspace / descriptor["path"]
        if path.is_symlink():
            raise budget.ContextError("MANUAL_WORKSPACE_SYMLINK")
        try:
            with private_records.open_file(path,"xb") as stream:
                stream.write(raw)
        except FileExistsError:
            private_records.check(path)
            if not path.is_file() or path.read_bytes() != raw:
                raise budget.ContextError("MANUAL_WORKSPACE_FILE_CHANGED")
        path.chmod(0o400)
        if budget.sha(path.read_bytes()) != descriptor["sha256"]:
            raise budget.ContextError("MANUAL_WORKSPACE_READBACK_CHANGED")
    return [descriptor for descriptor, _ in files]


def prepare(root, **kwargs):
    """Compatibility name; build itself always enforces the same preflight."""
    return build(root, **kwargs)


def open_blocker_ids(root,stage,idea_ids=None):
    rows=budget.obligations(root,'isles24-prediction',idea_ids or ['Sprint10'],stage)
    return [r['id'] for r in rows if r['type']=='stop' or (r['type']=='adverse finding' and r.get('severity')=='blocker')]
