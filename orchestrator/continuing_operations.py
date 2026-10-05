"""Saved, typed operations selected by the existing opposing-reviewed investigator.

No request can select a command, implementation path, verification callback or
permission. Scientific judgments use the existing protected scientific_decision
stages; registration, materialization and execution remain separate saved steps.
"""
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re

from orchestrator.handover_coordinator import digest
from orchestrator.hosted_cycle import encoded, immutable
from orchestrator.operations_report import private_root
from orchestrator.remote_supervisor import lock

SCHEMA = 'continuing-operation/v1'
RESULT_SCHEMA = 'continuing-operation-result/v1'
KINDS = {'AUTHORIZE_TASK', 'AUTHORIZE_PROTOCOL', 'MATERIALIZE_VERSION',
         'APPROVE_VERSION', 'LAUNCH_JOB', 'IMPORT_RESULT', 'VALIDATE_RESULT', 'ACCEPT_RESULT', 'ADOPT_FOLLOWUP'}
PROTOCOL_ARTIFACTS = {'protocol_sha256', 'input_manifest_sha256', 'partition_registry_sha256',
                      'exposure_history_sha256', 'literature_review_sha256', 'methodology_review_sha256'}
STEPS = {'AUTHORIZE_TASK': ('authority', 'register_and_submit'),
         'AUTHORIZE_PROTOCOL': ('authority',), 'MATERIALIZE_VERSION': ('materialize',),
         'APPROVE_VERSION': ('authority', 'attach_review'),
         'LAUNCH_JOB': ('authority', 'register', 'dispatch'), 'IMPORT_RESULT': ('import',),
         'VALIDATE_RESULT': ('authority', 'register', 'dispatch', 'import'),
         'ACCEPT_RESULT': ('authority', 'apply_acceptance'),
         'ADOPT_FOLLOWUP': ('authority', 'apply_adoption')}
STATE_ERRORS = (OSError, ValueError, KeyError, TypeError, AttributeError)


def pin(value, length=64):
    if not isinstance(value, str) or not re.fullmatch('[0-9a-f]{' + str(length) + '}', value):
        raise ValueError('CONTINUING_OPERATION_EXACT_PIN_REQUIRED')
    return value


def operation_reference(value):
    if not isinstance(value, dict) or set(value) != {'operation', 'result_sha256'}:
        raise ValueError('CONTINUING_OPERATION_RESULT_REFERENCE_REQUIRED')
    for item in value.values(): pin(item)
    return value


def _slug(value):
    if not isinstance(value, str) or not re.fullmatch('[a-z0-9][a-z0-9-]{0,62}', value):
        raise ValueError('CONTINUING_OPERATION_NAME_REQUIRED')


def contract(value):
    from orchestrator.continuing_research import reference
    if (not isinstance(value, dict) or set(value) != {'schema', 'operation_id', 'kind', 'inputs'}
            or value['schema'] != SCHEMA or value['kind'] not in KINDS
            or not isinstance(value['inputs'], dict)):
        raise ValueError('CONTINUING_TYPED_OPERATION_REQUIRED')
    _slug(value['operation_id'])
    kind = value['kind']; inputs = value['inputs']
    required = {
        'AUTHORIZE_TASK': {'selection'},
        'AUTHORIZE_PROTOCOL': {'experiment', 'protocol_id', 'artifacts', 'prior_protocol'},
        'MATERIALIZE_VERSION': {'experiment', 'version_id', 'proposals', 'protocol', 'parent_version_sha256'},
        'APPROVE_VERSION': {'materialization', 'protocol'},
        'LAUNCH_JOB': {'job_id', 'version', 'protocol', 'settings'},
        'IMPORT_RESULT': {'completion'}, 'VALIDATE_RESULT': {'completion'},
        'ACCEPT_RESULT': {'interpretation'},
        'ADOPT_FOLLOWUP': {'acceptance', 'selection'}}[kind]
    if kind == 'AUTHORIZE_TASK' and 'adoption' in inputs:
        required = required | {'adoption'}
        operation_reference(inputs['adoption'])
    if set(inputs) != required:
        raise ValueError('CONTINUING_FIXED_OPERATION_INPUTS_REQUIRED')
    if kind in ('AUTHORIZE_TASK', 'ADOPT_FOLLOWUP'):
        if kind == 'ADOPT_FOLLOWUP': operation_reference(inputs['acceptance'])
        reference(inputs['selection'])
        if inputs['selection']['artifact'] != 'round-1/selection.json':
            raise ValueError('CONTINUING_TASK_SELECTION_REQUIRED')
    elif kind == 'ACCEPT_RESULT':
        reference(inputs['interpretation'])
        if inputs['interpretation']['artifact'] != 'round-1/interpretation.md':
            raise ValueError('ACCEPTANCE_ORIGINAL_INTERPRETATION_REFERENCE_REQUIRED')
    elif kind == 'AUTHORIZE_PROTOCOL':
        _slug(inputs['protocol_id'])
        if not isinstance(inputs['artifacts'], dict) or set(inputs['artifacts']) != PROTOCOL_ARTIFACTS:
            raise ValueError('CONTINUING_COMPLETE_PROTOCOL_EVIDENCE_REQUIRED')
        for ref in inputs['artifacts'].values(): reference(ref)
        if inputs['prior_protocol'] is not None: operation_reference(inputs['prior_protocol'])
    elif kind == 'MATERIALIZE_VERSION':
        _slug(inputs['version_id']); operation_reference(inputs['protocol'])
        if (not isinstance(inputs['proposals'], list) or len(inputs['proposals']) != 3
                or len(set(inputs['proposals'])) != 3):
            raise ValueError('CONTINUING_THREE_ORIGINAL_PROPOSALS_REQUIRED')
        for identity in inputs['proposals']: pin(identity)
        if inputs['parent_version_sha256'] is not None: pin(inputs['parent_version_sha256'])
    elif kind == 'APPROVE_VERSION':
        operation_reference(inputs['materialization']); operation_reference(inputs['protocol'])
    elif kind == 'LAUNCH_JOB':
        _slug(inputs['job_id']); operation_reference(inputs['version'])
        operation_reference(inputs['protocol']); reference(inputs['settings'])
    else:
        # Completion is a protected event identity, never a caller-supplied output path.
        pin(inputs['completion'])
    if 'experiment' in inputs and inputs['experiment'] not in ('P002', 'P003'):
        raise ValueError('CONTINUING_PROSPECTIVE_EXPERIMENT_SCOPE')
    from orchestrator.public_export import text
    text(json.dumps(value), limit=26000)
    return value


def referenced_artifacts(value):
    kind = value['kind']; inputs = value['inputs']
    if kind in ('AUTHORIZE_TASK', 'ADOPT_FOLLOWUP'): return [inputs['selection']]
    if kind == 'ACCEPT_RESULT': return [inputs['interpretation']]
    if kind == 'AUTHORIZE_PROTOCOL': return list(inputs['artifacts'].values())
    if kind == 'LAUNCH_JOB': return [inputs['settings']]
    return []


def referenced_operations(value):
    keys = {'AUTHORIZE_TASK': (('adoption',) if 'adoption' in value['inputs'] else ()),
            'AUTHORIZE_PROTOCOL': ('prior_protocol',), 'MATERIALIZE_VERSION': ('protocol',),
            'APPROVE_VERSION': ('materialization', 'protocol'), 'LAUNCH_JOB': ('version', 'protocol'),
            'ADOPT_FOLLOWUP': ('acceptance',)}
    return [value['inputs'][key] for key in keys.get(value['kind'], ()) if value['inputs'][key] is not None]


def validate_selection(task, value):
    """Called lazily by continuing_research.selection for an operation successor."""
    contract(value)
    if task.get('mode') != 'investigate':
        raise ValueError('CONTINUING_INVESTIGATOR_SELECTION_REQUIRED')
    available = {digest(ref) for ref in task['references']}
    if any(digest(ref) not in available for ref in referenced_artifacts(value)):
        raise ValueError('CONTINUING_OPERATION_ARTIFACT_NOT_IN_INVESTIGATOR_CONTEXT')
    if value['kind'] == 'MATERIALIZE_VERSION':
        tasks = {ref['task'] for ref in task['references']}
        if not set(value['inputs']['proposals']) <= tasks:
            raise ValueError('CONTINUING_OPERATION_PROPOSAL_NOT_IN_CONTEXT')
    return value


def instructions():
    return ('You may select one typed continuing-operation/v1 successor instead of a campaign task. '
        'Its exact keys are schema, operation_id (new lowercase slug), kind and inputs. '
        'Select only original artifacts and completed operation references present in your bound context. '
        'The separately saved continuing_context supplies continuing_operations.completed and scientific_completions; '
        'it does not change the catalog reviewer_evidence or grant new authority. '
        'No commands, source paths, raw scientific authority request or self-asserted permissions are accepted. '
        'AUTHORIZE_PROTOCOL inputs: experiment P002/P003, protocol_id, artifacts (exact keys '
        + ', '.join(sorted(PROTOCOL_ARTIFACTS)) + ', each an existing {task,artifact,sha256}), '
        'prior_protocol null or {operation,result_sha256}. All six protocol artifacts must belong to one '
        'reviewed protocol_proposal bundle with PROPOSED status and no missing evidence; DEFERRED cannot authorize. '
        'MATERIALIZE_VERSION inputs: experiment, '
        'version_id, proposals (three existing task identities for reviewed propose/specify/code_bundle), '
        'protocol {operation,result_sha256}, parent_version_sha256 null or original digest. '
        'APPROVE_VERSION inputs: materialization and protocol operation references. LAUNCH_JOB inputs: '
        'job_id, version and protocol operation references, settings artifact reference. IMPORT_RESULT '
        'inputs: completion (protected ANALYSIS_AVAILABLE event identity). VALIDATE_RESULT inputs: completion '
        '(same protected original event); this separately authorizes the exact reviewed validator, starts '
        'one confined attempt, waits without model calls and imports VALID/INVALID/DEFER as evidence only. '
        'The original result must declare the supported validator interface; no legacy inference or rerun. '
        'ACCEPT_RESULT inputs: interpretation {task,artifact,sha256}, where artifact is round-1/interpretation.md. '
        'It must be a reviewed prospective interpretation that consumed the exact bound semantic validation. '
        'Separate formal author/opposing-review authority decides APPLY or DEFER; only VALID may be applied. '
        'Acceptance does not adopt a successor or launch work. '
        'ADOPT_FOLLOWUP inputs: acceptance {operation,result_sha256} and selection '
        '{task,artifact,sha256} for an independently reviewed round-1/selection.json. '
        'The selection must explicitly use the applied acceptance and accepted interpretation. '
        'A separate adopt_followup decision assesses typed successor/protocol compatibility; '
        'APPLY records adoption only, while DEFER remains saved. Neither grants task eligibility or execution. '
        'A prospective follow-up grounded in an accepted interpretation must name accepted_result '
        '{operation,result_sha256}; discovery first derives ADOPT_FOLLOWUP. After its applied result '
        'is available, select a separate AUTHORIZE_TASK with selection plus adoption '
        '{operation,result_sha256}; it must refer to the exact original successor. '
        'AUTHORIZE_TASK inputs: selection '
        '(existing accepted selection.json reference). Every selection remains a proposal; the system '
        'then runs its applicable scientific authority, independent review and separate recorded steps. '
        'Choose DEFER with reasons when required evidence is missing; never fabricate an artifact or receipt.')


def _read(path, maximum=2000000):
    from orchestrator.scientific_authority import read
    return read(path, limit=maximum)


def _directory(config):
    return Path(config['state']).absolute() / 'continuing-operations'


def _saved(folder):
    value = json.loads(_read(folder / 'request.json'))
    core = {key: item for key, item in value.items() if key not in ('identity', 'created_at_utc')}
    if (set(core) != {'source', 'operation', 'selected_by', 'predecessor', 'actor', 'change_request'}
            or value.get('identity') != digest(core) or value['identity'] != folder.name):
        raise ValueError('CONTINUING_SAVED_REQUEST_CHANGED')
    contract(value['operation']); pin(value['source'], 40)
    return value


def enabled(config):
    value = config.get('continuing_operations')
    if value is None: return False
    if not isinstance(value, dict) or set(value) != {'enabled'} or type(value['enabled']) is not bool:
        raise ValueError('CONTINUING_OPERATIONS_CONFIGURATION_REQUIRED')
    return value['enabled']


def _identity(config):
    if not enabled(config): raise ValueError('CONTINUING_OPERATIONS_DISABLED')
    if os.getuid() != config['controller_uid'] or config['controller_uid'] <= 0:
        raise ValueError('CONTINUING_OPERATIONS_CONTROLLER_IDENTITY_REQUIRED')


def _client(runtime):
    from orchestrator.handover_runtime import request_broker
    return lambda socket, operation, body: request_broker(runtime.config['broker_socket'], operation, body)


def _predecessor(runtime, identity, *, accepted=True):
    pin(identity)
    path = Path(runtime.config['state']) / 'tasks' / identity / 'scientific-disposition.json'
    raw = _read(path); disposition = json.loads(raw)
    required = {'task': identity, 'source': disposition['source'],
        'disposition_sha256': hashlib.sha256(raw).hexdigest(),
        'requires': 'APPROVED_PROPOSAL_ONLY' if accepted else 'DISPOSITION_RECORDED'}
    runtime.research_predecessors({'predecessors': [required]})
    return required, disposition


def _selection(runtime, ref):
    from orchestrator.continuing_research import read_reference, selection, observed_protocols
    from orchestrator.hosted_campaign import checked_reply
    from orchestrator.research_task_authority import _provenance
    from orchestrator.scientific_authority import actor
    required, disposition = _predecessor(runtime, ref['task'])
    folder = Path(runtime.config['state']) / 'tasks' / ref['task']
    packet = json.loads(_read(folder / 'packet.json'))
    value = json.loads(read_reference(runtime.config, ref))
    desired = (value.get('successor') or {}).get('protocol')
    selection(packet['campaign_task'], value,
        protocols=observed_protocols(runtime.config, packet, client=_client(runtime), desired=desired) if desired else ())
    if value['status'] != 'PROPOSE': raise ValueError('CONTINUING_SELECTION_DEFERRED')
    if required['source'] != runtime.config['source']:
        raise ValueError('CONTINUING_FRESH_OPERATION_SOURCE_REQUIRED')
    event = {'turn_id': ref['task'], 'source': required['source'], 'attempt': '1',
             'branch': 'astra/infrastructure-milestone-record', 'kind': 'astra_turn'}
    response = _client(runtime)('', 'stage_status', {'event': event, 'stage': 'continuation'})
    _, receipt = checked_reply(response, 'continuation', hashlib.sha256(encoded(packet)).hexdigest())
    by = actor(_provenance(receipt, 'codex', event, packet))
    change = packet.get('research_catalog_entry', {}).get('change_request')
    if change is None: raise ValueError('CONTINUING_SELECTED_CHANGE_BINDING_REQUIRED')
    from orchestrator.research_catalog import linked_change
    linked_change(runtime.config, {'change_request': change})
    return value, packet, required, by, change


def read_operation_result(config, ref, *, kinds=(), current_review=True):
    """Verify originals; completed recovery may separately expose later criticism."""
    if type(current_review) is not bool:
        raise ValueError('CONTINUING_OPERATION_REVIEW_MODE_REQUIRED')
    operation_reference(ref)
    folder = _directory(config) / ref['operation']
    request = _saved(folder)
    raw = _read(folder / 'result.json'); value = json.loads(raw)
    if (hashlib.sha256(raw).hexdigest() != ref['result_sha256']
            or request['identity'] != ref['operation'] or value.get('operation') != ref['operation']
            or value.get('source') != config['source'] or value.get('schema') != RESULT_SCHEMA
            or value.get('status') != 'COMPLETE'
            or value.get('scientific_acceptance') is not (request['operation']['kind'] == 'ACCEPT_RESULT')
            or value.get('kind') != request['operation']['kind'] or kinds and value['kind'] not in kinds):
        raise ValueError('CONTINUING_COMPLETED_OPERATION_BINDING_REQUIRED')
    if current_review:
        from orchestrator.research_catalog import linked_change
        linked_change(config, {'change_request': request['change_request']})
    final = json.loads(_read(folder / ('step-' + str(len(STEPS[value['kind']]) - 1) + '.json')))['result']
    if value['kind'] == 'AUTHORIZE_PROTOCOL':
        expected = {key: item for key, item in value['result'].items() if key not in ('protocol', 'artifacts')}
    else:
        expected = value['result']
    if final != expected:
        raise ValueError('CONTINUING_ORIGINAL_STEP_RESULT_CHANGED')
    return value


def _observed_inputs(config, packet, operation, successor):
    """Fresh references must have reached both roles in the saved packet."""
    context = packet.get('continuing_context', {})
    from orchestrator.scientific_context_references import completed_rows, completion_rows
    supplied = completed_rows(config, packet)
    observed = {digest(item['reference']) for item in supplied}
    refs = list(referenced_operations(operation))
    imported = successor.get('import_result') if operation['kind'] == 'AUTHORIZE_TASK' else None
    if imported is not None:
        operation_reference(imported)
        refs.append(imported)
    validation = successor.get('semantic_validation') if operation['kind'] == 'AUTHORIZE_TASK' else None
    if validation is not None:
        operation_reference(validation)
        refs.append(validation)
    for ref in refs:
        if digest(ref) not in observed:
            raise ValueError('CONTINUING_OPERATION_RESULT_NOT_IN_ORIGINAL_CONTEXT')
        read_operation_result(config, ref, kinds=('IMPORT_RESULT',) if ref == imported else
                              ('VALIDATE_RESULT',) if ref == validation else
                              ('ACCEPT_RESULT',) if operation['kind'] == 'ADOPT_FOLLOWUP' else
                              ('ADOPT_FOLLOWUP',) if ref == operation['inputs'].get('adoption') else ())
    if operation['kind'] in ('IMPORT_RESULT', 'VALIDATE_RESULT'):
        completions = completion_rows(config, packet)
        if operation['inputs']['completion'] not in {item['event'] for item in completions}:
            raise ValueError('CONTINUING_COMPLETION_NOT_IN_ORIGINAL_CONTEXT')
    return refs



def _derived_operation(runtime, chosen, packet, selected_by):
    from orchestrator.continuing_research import TASK_SCHEMA, PROSPECTIVE_SCHEMA
    from orchestrator.protocol_proposals import TASK_SCHEMA as PROTOCOL_SCHEMA
    successor = chosen['successor']
    if successor.get('schema') not in (TASK_SCHEMA, PROSPECTIVE_SCHEMA, PROTOCOL_SCHEMA):
        operation = validate_selection(packet['campaign_task'], successor)
        if operation['kind'] == 'AUTHORIZE_TASK':
            original, original_packet, _, _, _ = _selection(runtime, operation['inputs']['selection'])
            task = original['successor']
            if task.get('schema') not in (TASK_SCHEMA, PROSPECTIVE_SCHEMA, PROTOCOL_SCHEMA):
                raise ValueError('CONTINUING_AUTHORIZE_TASK_SELECTION_REQUIRED')
            from orchestrator.scientific_adoption import require_applied
            require_applied(runtime.config, task, original_packet, operation['inputs']['selection'],
                            operation['inputs'].get('adoption'), original_client=_client(runtime))
        return operation
    from orchestrator.scientific_adoption import selected_operation
    adoption = selected_operation(runtime.config, successor, packet, selected_by,
                                  original_client=_client(runtime))
    if adoption is not None:
        return adoption
    return {'schema': SCHEMA, 'operation_id': successor['task_id'],
            'kind': 'AUTHORIZE_TASK', 'inputs': {'selection': selected_by}}


def enqueue(runtime, selected_by):
    """Only an actual accepted investigator selection can create an operation."""
    from orchestrator.continuing_research import reference, TASK_SCHEMA, PROSPECTIVE_SCHEMA
    from orchestrator.protocol_proposals import TASK_SCHEMA as PROTOCOL_SCHEMA
    _identity(runtime.config); reference(selected_by)
    chosen, packet, predecessor, by, change = _selection(runtime, selected_by)
    successor = chosen['successor']
    operation = _derived_operation(runtime, chosen, packet, selected_by)
    # Operation results are references to protected original state, not grants
    # asserted in model prose. They must also have reached the selecting roles.
    _observed_inputs(runtime.config, packet, operation, successor)
    core = {'source': runtime.config['source'], 'operation': operation,
            'selected_by': selected_by, 'predecessor': predecessor, 'actor': by, 'change_request': change}
    identity = digest(core)
    root = private_root(_directory(runtime.config))
    with lock(root / '.operation.lock'):
        for old in root.iterdir():
            if not old.is_dir() and not old.is_symlink(): continue
            try:
                prior = _saved(old)
            except STATE_ERRORS:
                if old.name == identity:
                    raise ValueError('CONTINUING_OPERATION_ORIGINALS_REQUIRE_RECONCILIATION') from None
                continue
            same_validation = (operation['kind'] in ('VALIDATE_RESULT', 'ACCEPT_RESULT', 'ADOPT_FOLLOWUP')
                and prior['operation']['kind'] == operation['kind']
                and prior['operation']['inputs'] == operation['inputs'])
            if prior['source'] == core['source'] and (same_validation
                    or prior['operation']['operation_id'] == operation['operation_id']):
                if not same_validation and prior['operation'] != operation:
                    raise ValueError('CONTINUING_OPERATION_VERSION_ID_CONFLICT')
                # A later selection can refer to the same saved work, not create
                # another model-bearing attempt for an unchanged operation.
                immutable(private_root(old / 'later-selections') / (digest(selected_by) + '.json'), encoded(selected_by))
                return {'operation': prior['identity'], 'status': _observed_state(old)['status'], 'duplicate': True,
                        'models': 0, 'admissions': 0}
        folder = root / identity
        if folder.exists() or folder.is_symlink():
            raise ValueError('CONTINUING_OPERATION_ORIGINALS_REQUIRE_RECONCILIATION')
        folder = private_root(folder)
        original = folder / 'request.json'
        if original.exists():
            saved = json.loads(_read(original))
            if {key: saved[key] for key in core} != core or saved['identity'] != identity:
                raise ValueError('CONTINUING_IMMUTABLE_OPERATION_CONFLICT')
        else:
            immutable(original, encoded({**core, 'identity': identity,
                'created_at_utc': datetime.now(timezone.utc).isoformat()}))
    return {'operation': identity, 'status': _state(folder)['status'], 'models': 0, 'admissions': 0}


def _check_saved(runtime, saved):
    from orchestrator.continuing_research import TASK_SCHEMA, PROSPECTIVE_SCHEMA
    from orchestrator.protocol_proposals import TASK_SCHEMA as PROTOCOL_SCHEMA
    chosen, packet, predecessor, by, change = _selection(runtime, saved['selected_by'])
    successor = chosen['successor']
    operation = _derived_operation(runtime, chosen, packet, saved['selected_by'])
    if (saved['operation'] != operation or saved['actor'] != by or saved['change_request'] != change
            or saved['predecessor'] != predecessor or saved['source'] != runtime.config['source']):
        raise ValueError('CONTINUING_OPERATION_DIFFERS_FROM_ORIGINAL_SELECTION')
    for ref in _observed_inputs(runtime.config, packet, operation, successor):
        prior = _saved(_directory(runtime.config) / ref['operation'])
        # Verify the prior selection independently without recursively executing
        # or projecting its dependencies. Its own provider-backed decision gate
        # is rechecked by the fixed consumer (version, protocol or job adapter).
        old, old_packet, required, actor, link = _selection(runtime, prior['selected_by'])
        if (_derived_operation(runtime, old, old_packet, prior['selected_by']) != prior['operation'] or prior['actor'] != actor
                or prior['change_request'] != link or prior['predecessor'] != required):
            raise ValueError('CONTINUING_PRIOR_OPERATION_ORIGINAL_CHANGED')
        read_operation_result(runtime.config, ref)


def _state(folder):
    request = _saved(folder)
    kind = request['operation']['kind']; step = 0
    path = folder / 'result.json'
    if path.exists():
        result = json.loads(_read(path))
        if (result.get('operation') != request['identity'] or result.get('source') != request['source']
                or result.get('status') not in ('COMPLETE', 'DEFERRED', 'BLOCKED') or result.get('kind') != kind):
            raise ValueError('CONTINUING_SAVED_RESULT_CHANGED')
        return {'operation': request['identity'], 'kind': kind, 'step': 'complete', 'position': len(STEPS[kind]),
                'status': result['status'], 'reason': result.get('reason')}
    for step, name in enumerate(STEPS[kind]):
        if not (folder / ('step-' + str(step) + '.json')).exists():
            started = (folder / ('started-' + str(step) + '.json')).exists()
            return {'operation': request['identity'], 'kind': kind, 'step': name, 'position': step,
                'status': 'RECONCILIATION_REQUIRED' if started else 'QUEUED',
                'reason': 'A saved attempt has no completion; inspect original receipts before continuation.' if started else None}
    return {'operation': request['identity'], 'kind': kind, 'step': 'finalize', 'position': len(STEPS[kind]),
            'status': 'FINALIZATION_PENDING', 'reason': None}


def _unreadable_operation(folder):
    return {'operation': folder.name if re.fullmatch('[0-9a-f]{64}', folder.name) else None,
        'entry_name_sha256': hashlib.sha256(folder.name.encode()).hexdigest(),
        'kind': None, 'step': None, 'position': None, 'status': 'RECONCILIATION_REQUIRED',
        'reason': 'CONTINUING_OPERATION_ORIGINALS_REQUIRE_RECONCILIATION'}


def _observed_state(folder):
    """Expose damaged originals without inventing a kind or repairing history."""
    try:
        pin(folder.name)
        return _state(folder)
    except STATE_ERRORS:
        return _unreadable_operation(folder)


def status(config):
    """Read-only status never initializes work or runs a model."""
    root = _directory(config); rows = []; completed = []
    if root.exists():
        for folder in sorted(root.iterdir()):
            if not folder.is_dir() and not folder.is_symlink(): continue
            row = _observed_state(folder)
            from orchestrator.authority_replacements import observed as replacement_status
            replacement = replacement_status(folder)
            if replacement is not None: row['linked_replacement'] = replacement
            if row['status'] == 'COMPLETE':
                try:
                    raw = _read(folder / 'result.json')
                    completed.append({'reference': {'operation': folder.name,
                        'result_sha256': hashlib.sha256(raw).hexdigest()}, 'kind': row['kind'],
                        'result': json.loads(raw)['result']})
                except STATE_ERRORS:
                    row = _unreadable_operation(folder)
            rows.append(row)
    return {'status': 'DISABLED' if not enabled(config) else 'SAVED_OPERATIONS' if rows else 'AWAITING_REVIEWED_SELECTION',
            'operations': rows, 'completed': completed, 'models': 0, 'admissions': 0,
            'exhaustion_is_not_authority': True}


def discover(runtime):
    if not enabled(runtime.config): return {'status': 'DISABLED', 'operations': [], 'models': 0}
    found = []; blocked_tasks = []
    for row in runtime.q.db.execute("SELECT id FROM tasks WHERE status='COMPLETE' ORDER BY rowid").fetchall():
        try:
            pin(row['id'])
            folder = Path(runtime.config['state']) / 'tasks' / row['id']
            packet = json.loads(_read(folder / 'packet.json'))
            if packet.get('campaign_task', {}).get('mode') != 'investigate': continue
            path = folder / 'scientific-disposition.json'
            if not path.exists(): continue
            disposition = json.loads(_read(path)); sha = disposition.get('artifact_sha256', {}).get('round-1/selection.json')
            if not sha or disposition.get('review_verdict') != 'APPROVE' or disposition.get('source') != runtime.config['source']:
                continue
            ref = {'task': row['id'], 'artifact': 'round-1/selection.json', 'sha256': sha}
            from orchestrator.continuing_research import read_reference
            if json.loads(read_reference(runtime.config, ref)).get('status') == 'DEFER': continue
            found.append(enqueue(runtime, ref))
        except STATE_ERRORS:
            blocked_tasks.append({'task': row['id'], 'status': 'RECONCILIATION_REQUIRED',
                'reason': 'CONTINUING_SELECTION_ORIGINALS_REQUIRE_RECONCILIATION'})
    blocked = [row for row in status(runtime.config)['operations'] if row['status'] == 'RECONCILIATION_REQUIRED']
    return {'status': 'DISCOVERED' if found else 'OPERATIONS_REQUIRE_RECONCILIATION' if blocked or blocked_tasks
            else 'AWAITING_REVIEWED_SELECTION', 'operations': found, 'blocked_operations': blocked,
            'blocked_tasks': blocked_tasks, 'models': 0}


def _reviewed_artifact(runtime, ref):
    from orchestrator.continuing_research import read_reference
    _predecessor(runtime, ref['task'])
    return read_reference(runtime.config, ref)


def _formal(runtime, saved, prepared, workspace=None):
    from orchestrator.formal_decisions import checked_request
    request = {'schema': 'formal-scientific-decision-request/v1', 'source': runtime.config['source'],
        **prepared, 'workspace': workspace, 'application': None, 'change_request': saved['change_request']}
    return checked_request(request)


def _protocol_request(runtime, saved):
    from orchestrator.protocol_proposals import authorization_artifacts, task_contract
    inputs = saved['operation']['inputs']
    artifacts = {key: _reviewed_artifact(runtime, ref).decode() for key, ref in inputs['artifacts'].items()}
    bundle = authorization_artifacts(inputs['protocol_id'], inputs['experiment'], inputs['artifacts'], artifacts)
    packet = json.loads(_read(Path(runtime.config['state']) / 'tasks' / bundle['task'] / 'packet.json'))
    if task_contract(packet['campaign_task'])['experiment'] != inputs['experiment']:
        raise ValueError('CONTINUING_PROTOCOL_PROPOSAL_EXPERIMENT_CHANGED')
    prior = inputs['prior_protocol']
    previous = None if prior is None else read_operation_result(runtime.config, prior,
        kinds=('AUTHORIZE_PROTOCOL',))['result']['protocol']['decision_sha256']
    bindings = {'source': runtime.config['source'], 'experiment': inputs['experiment'],
        **{key: hashlib.sha256(raw.encode()).hexdigest() for key, raw in artifacts.items()},
        'prior_protocol_sha256': previous}
    # Every input root is checked later again by the fixed job adapter before any
    # dependent payload read. This decision itself receives only saved evidence.
    prepared = {'action': 'authorize_protocol', 'subject': inputs['protocol_id'], 'bindings': bindings,
        'transition': {'from': 'REVIEWED_PROTOCOL_PROPOSAL', 'to': 'PROTOCOL_ELIGIBLE'},
        'evidence': {key + '.txt': raw for key, raw in artifacts.items()},
        'request': 'Judge this exact prospective protocol within the selected ISLES24 charter. '
            'Review the original literature and methodology evidence, input manifest, partition membership '
            'and exposure history together. Preserve all prior frozen versions and actual human stops. '
            'Require a defensible prospective method and honest prior exposure; defer missing or inconsistent '
            'evidence. This decision grants no job launch, new dataset, spending or public export.'}
    return _formal(runtime, saved, prepared)


def _prepared(runtime, saved, folder):
    """Fixed constructors derive authority inputs; no raw request is accepted."""
    config = runtime.config; operation = saved['operation']; inputs = operation['inputs']; kind = operation['kind']
    client = _client(runtime)
    if kind == 'AUTHORIZE_TASK':
        from orchestrator.continuing_research import selected_successor, preserve_evidence
        from orchestrator.research_catalog import paths, selection as installed_selection
        selected = selected_successor(config, inputs['selection']['task'])
        task = selected['task']
        if task['task_id'] in paths(config):
            _, existing = installed_selection(config, task['task_id'])
            if (existing is None or existing['source'] != config['source']
                    or existing['request']['task'] != task):
                raise ValueError('CONTINUING_EXISTING_TASK_VERSION_CONFLICT')
            from orchestrator.scientific_adoption import require_registration
            require_registration(config, existing, original_client=client)
            runtime.research_predecessors(existing)
            from orchestrator.research_task_authority import verify_eligibility
            if verify_eligibility(config, existing, client=client)['status'] != 'ELIGIBLE':
                raise ValueError('CONTINUING_EXISTING_TASK_NOT_ELIGIBLE')
            return {'entry': existing, 'reuse_original_authority': True}
        _, packet, predecessor, _, _ = _selection(runtime, inputs['selection'])
        # Explicit AUTHORIZE_TASK may name an earlier original selection. Check
        # that selection's own snapshot, not only the later operator's context.
        original_operation = deepcopy(operation)
        original_operation['inputs'].pop('adoption', None)
        _observed_inputs(config, packet, original_operation, task)
        from orchestrator.scientific_adoption import require_applied
        require_applied(config, task, packet, inputs['selection'], inputs.get('adoption'),
                        original_client=client)
        predecessors = {predecessor['task']: predecessor}
        for ref in task['references']:
            predecessors[ref['task']] = _predecessor(runtime, ref['task'])[0]
        from orchestrator import scientific_context_references as context_refs
        from orchestrator.current_scientific_input import is_current
        prior = (context_refs.predecessor(config, packet)
                 if is_current(packet) and context_refs.enabled(config['source_root'], config['source']) else
                 {'prior_packet_evidence': packet.get('reviewer_evidence', {}),
                  'prior_continuing_context': packet.get('continuing_context', {})})
        evidence = preserve_evidence(config, {'selected_operation': saved, **prior,
            'original_selection': json.loads(_reviewed_artifact(runtime, inputs['selection']))})
        decision = folder / 'authority/round-1/decision.json'
        return {'entry': {'schema': 'installed-research-catalog-entry/v1', 'source': config['source'],
            'source_root': config['source_root'], 'request': {'task': task, **evidence,
                'day': saved['created_at_utc'][:10], 'initiator': saved['actor']},
            'eligibility': {'path': str(decision), 'sha256': '0' * 64},
            'predecessors': list(predecessors.values()), 'change_request': saved['change_request']}}
    if kind == 'AUTHORIZE_PROTOCOL': return {'formal_request': _protocol_request(runtime, saved)}
    if kind == 'APPROVE_VERSION':
        from orchestrator import scientific_versions
        material = read_operation_result(config, inputs['materialization'], kinds=('MATERIALIZE_VERSION',))['result']
        protocol = read_operation_result(config, inputs['protocol'], kinds=('AUTHORIZE_PROTOCOL',))['result']['protocol']
        root = Path(material['workspace']); core = json.loads(_read(root / 'scientific-version.json'))
        prepared = scientific_versions.decision_request(root, core, protocol, original_client=client)
        workspace = root.relative_to(Path(config['state']).absolute()).as_posix()
        return {'formal_request': _formal(runtime, saved, prepared, workspace), 'materialization': inputs['materialization']}
    if kind == 'ADOPT_FOLLOWUP':
        from orchestrator.scientific_adoption import prepare
        return {'formal_request': _formal(runtime, saved, prepare(config,
            inputs['acceptance'], inputs['selection'], original_client=client))}
    if kind == 'ACCEPT_RESULT':
        from orchestrator.scientific_acceptance import prepare
        return {'formal_request': _formal(runtime, saved, prepare(config,
            inputs['interpretation'], original_client=client))}
    if kind == 'VALIDATE_RESULT':
        from orchestrator.scientific_validation import checked_launch_specification
        value = client('', 'scientific_validation_specification', {'completion': inputs['completion']})
        request = checked_launch_specification(value, config['source'], inputs['completion'])
        return {'formal_request': _formal(runtime, saved, request)}
    if kind == 'LAUNCH_JOB':
        from orchestrator.scientific_materialization import prepare_job
        from orchestrator.linux_scientific_jobs import decision_request
        prepared = prepare_job(config, version_ref=inputs['version'], protocol_ref=inputs['protocol'],
            settings_ref=inputs['settings'], job_id=inputs['job_id'], original_client=client, by=saved['actor'])
        core = prepared['core']; expected = decision_request(core)
        request = deepcopy(prepared['decision_request'])
        if any(request.get(key) != value for key, value in expected.items()) or not request.get('evidence'):
            raise ValueError('CONTINUING_PREPARED_JOB_DECISION_CHANGED')
        request.update(request='Judge this exact reviewed scientific version, protocol, settings, input manifest and installed '
                'environment/resource bounds for one Linux execution. The protected job adapter independently '
                'checks every seal and byte before launch. No retries, new data, dependency installs or network access.')
        return {'formal_request': _formal(runtime, saved, request), 'prepared_job': prepared}
    return {}


def _step(runtime, saved, folder, position, prepared):
    from orchestrator import formal_decisions
    config = runtime.config; operation = saved['operation']; inputs = operation['inputs']; kind = operation['kind']
    client = _client(runtime)
    previous = None if position == 0 else json.loads(_read(folder / ('step-' + str(position - 1) + '.json')))['result']
    if kind == 'AUTHORIZE_TASK':
        if position == 0:
            if prepared.get('reuse_original_authority') is True:
                from orchestrator.research_task_authority import verify_eligibility
                proof = verify_eligibility(config, prepared['entry'], client=client)
                if proof['status'] != 'ELIGIBLE': raise ValueError('CONTINUING_EXISTING_TASK_NOT_ELIGIBLE')
                return {'status': 'AGENT_REVIEWED_DECISION_READY', 'new_model_calls': 0,
                        'eligibility': prepared['entry']['eligibility'], 'original_authority_reused': True}
            from orchestrator.research_task_authority import execute
            return execute(config, prepared['entry'], folder / 'authority', client=client)
        from orchestrator.continuing_research import register_and_submit
        entry = deepcopy(prepared['entry']); entry['eligibility'] = previous['eligibility']
        return register_and_submit(runtime, entry)
    if kind in ('AUTHORIZE_PROTOCOL', 'APPROVE_VERSION', 'LAUNCH_JOB', 'VALIDATE_RESULT', 'ACCEPT_RESULT', 'ADOPT_FOLLOWUP') and position == 0:
        return formal_decisions.execute_formal_decision(config, prepared['formal_request'],
            Path(config['state']) / 'formal-decisions' / saved['identity'], client=client)
    if kind == 'ADOPT_FOLLOWUP':
        from orchestrator.scientific_adoption import apply
        return apply(config, inputs['acceptance'], inputs['selection'], prepared['formal_request'],
            previous['decision_path'], original_client=client, by=saved['actor'])
    if kind == 'ACCEPT_RESULT':
        from orchestrator.scientific_acceptance import apply
        return apply(config, inputs['interpretation'], prepared['formal_request'],
            previous['decision_path'], original_client=client, by=saved['actor'])
    if kind == 'MATERIALIZE_VERSION':
        from orchestrator.scientific_materialization import materialize
        from orchestrator.scientific_versions import PROPOSAL_FILES
        proposals = []
        for identity in inputs['proposals']:
            _, disposition = _predecessor(runtime, identity)
            packet = json.loads(_read(Path(config['state']) / 'tasks' / identity / 'packet.json'))
            mode = packet['campaign_task']['mode']
            if mode not in PROPOSAL_FILES: raise ValueError('CONTINUING_VERSION_PROPOSAL_MODE')
            proposals.append({'task': identity, 'source': disposition['source'], 'mode': mode,
                'packet_sha256': hashlib.sha256(encoded(packet)).hexdigest(),
                'artifacts': {'round-1/' + name: disposition['artifact_sha256']['round-1/' + name] for name in PROPOSAL_FILES[mode]}})
        protocol = read_operation_result(config, inputs['protocol'], kinds=('AUTHORIZE_PROTOCOL',))['result']['protocol']
        return materialize(config, experiment=inputs['experiment'], version_id=inputs['version_id'], proposals=proposals,
            protocol_decision_sha256=protocol['decision_sha256'], parent_version_sha256=inputs['parent_version_sha256'],
            original_client=client, by=saved['actor'])
    if kind == 'APPROVE_VERSION':
        from orchestrator.scientific_materialization import attach_review
        material = read_operation_result(config, inputs['materialization'], kinds=('MATERIALIZE_VERSION',))['result']
        attached = attach_review(config, scientific_version_sha256=material['scientific_version_sha256'],
            decision_path=previous['decision_path'], original_client=client, by=saved['actor'])
        return {'materialization': inputs['materialization'], 'decision': previous, 'attachment': attached}
    if kind == 'LAUNCH_JOB':
        if position == 1:
            return client('', 'register_scientific_job', {'core': prepared['prepared_job']['core'],
                'decision_path': previous['decision_path']})
        return client('', 'dispatch_scientific_job', {'job': inputs['job_id']})
    if kind == 'VALIDATE_RESULT':
        from orchestrator.scientific_validation import job_id
        if position == 1:
            return client('', 'register_scientific_validation', {'completion': inputs['completion'],
                'decision_path': previous['decision_path']})
        if position == 2:
            return client('', 'dispatch_scientific_job', {'job': job_id(inputs['completion'])})
        from orchestrator.scientific_job_results import import_semantic_validation
        return import_semantic_validation(config, completion=inputs['completion'],
                                         original_client=client, by=saved['actor'])
    if kind == 'IMPORT_RESULT':
        from orchestrator.scientific_materialization import import_result
        return import_result(config, completion=inputs['completion'], original_client=client, by=saved['actor'])
    raise ValueError('CONTINUING_FIXED_OPERATION_NOT_IMPLEMENTED')


def _blocked(result):
    return any(word in str(result.get('status', '')) for word in ('FAILED', 'BLOCKED', 'UNCERTAIN', 'RECONCILIATION'))


def _finalize(saved, folder, result):
    kind = saved['operation']['kind']; status = 'COMPLETE'
    if result.get('status') == 'AGENT_REVIEWED_DEFERRAL': status = 'DEFERRED'
    if _blocked(result): status = 'BLOCKED'
    if kind == 'ACCEPT_RESULT' and status == 'COMPLETE':
        from orchestrator.scientific_acceptance import STATUS
        if (result.get('status') != STATUS or result.get('scientific_acceptance') is not True
                or result.get('adoption') is not False or result.get('execution_authorized') is not False
                or result.get('model_calls') != 0):
            raise ValueError('CONTINUING_ACCEPTANCE_APPLICATION_REQUIRED')
    if kind == 'ADOPT_FOLLOWUP' and status == 'COMPLETE':
        from orchestrator.scientific_adoption import STATUS
        if (result.get('status') != STATUS or result.get('adoption') is not True
                or result.get('execution_authorized') is not False or result.get('model_calls') != 0):
            raise ValueError('CONTINUING_ADOPTION_APPLICATION_REQUIRED')
    if kind == 'AUTHORIZE_PROTOCOL' and status != 'BLOCKED':
        request = json.loads(_read(folder / 'prepared.json'))['formal_request']
        try:
            path = Path(result['decision_path'])
            output = path.parent.parent
            expected_parent = folder.parent.parent / 'formal-decisions'
            if (not path.is_absolute() or path != output / 'round-1/decision.json'
                    or output.parent != expected_parent
                    or output.name not in (saved['identity'], saved['identity'] + '-recovery')):
                raise ValueError('CONTINUING_PROTOCOL_DECISION_PATH_CHANGED')
            sealed_sha = hashlib.sha256(_read(path)).hexdigest()
            receipt = json.loads(_read(output / 'receipt.json'))
            if (receipt.get('decision') != 'round-1/decision.json'
                    or receipt.get('decision_sha256') != sealed_sha
                    or result.get('decision_sha256', sealed_sha) != sealed_sha):
                raise ValueError('CONTINUING_PROTOCOL_DECISION_CHANGED')
        except STATE_ERRORS:
            raise ValueError('CONTINUING_PROTOCOL_SEALED_ORIGINAL_MISSING_OR_CHANGED') from None
        result = {**result, 'protocol': {'subject': request['subject'], 'bindings': request['bindings'],
            'decision_path': result['decision_path'], 'decision_sha256': sealed_sha},
            'artifacts': saved['operation']['inputs']['artifacts']}
    value = {'schema': RESULT_SCHEMA, 'operation': saved['identity'], 'source': saved['source'],
        'kind': kind, 'status': status, 'result': result,
        'scientific_acceptance': kind == 'ACCEPT_RESULT' and status == 'COMPLETE'}
    immutable(folder / 'result.json', encoded(value))
    return value


def _validation_wait(runtime, saved, position):
    if saved['operation']['kind'] != 'VALIDATE_RESULT' or position != 3:
        return False
    from orchestrator.scientific_validation import job_id
    status = _client(runtime)('', 'scientific_job_status', {})
    expected = job_id(saved['operation']['inputs']['completion'])
    rows = [row for row in status['jobs'] if row['id'] == expected]
    if len(rows) != 1 or rows[0]['phase'] != 'scientific_validation':
        raise ValueError('CONTINUING_VALIDATION_REGISTERED_JOB_REQUIRED')
    # Terminal failure proceeds once to preserved import failure/reconciliation.
    # An unfinished job creates no import intent and consumes no model turn.
    return rows[0]['status'] in ('READY', 'RUNNING')


def advance(runtime):
    """At most one new saved step. Invoke outside Runtime's branch.lock."""
    _identity(runtime.config)
    root = private_root(_directory(runtime.config))
    with lock(root / '.operation.lock'):
        if runtime.q.status()['paused']:
            return {'status': 'PAUSED', 'reason': 'Saved pause blocks new operation steps.', 'models': 0}
        waiting_validation = []
        for folder in sorted(root.iterdir()):
            if not folder.is_dir() and not folder.is_symlink(): continue
            state = _observed_state(folder)
            if state['status'] not in ('QUEUED', 'FINALIZATION_PENDING'): continue
            try:
                saved = _saved(folder)
            except STATE_ERRORS:
                continue
            if saved['source'] != runtime.config['source']: continue
            _check_saved(runtime, saved)
            position = state['position']
            if _validation_wait(runtime, saved, position):
                waiting_validation.append(saved['identity'])
                continue
            if state['status'] == 'FINALIZATION_PENDING':
                previous = json.loads(_read(folder / ('step-' + str(position - 1) + '.json')))['result']
                return _finalize(saved, folder, previous)
            prepared_path = folder / 'prepared.json'
            prepared = json.loads(_read(prepared_path)) if prepared_path.exists() else _prepared(runtime, saved, folder)
            experiment = (prepared.get('entry', {}).get('request', {}).get('task', {}).get('experiment')
                or prepared.get('formal_request', {}).get('bindings', {}).get('experiment')
                or saved['operation']['inputs'].get('experiment'))
            if experiment is not None:
                from orchestrator.campaign import require_no_human_stop
                require_no_human_stop(runtime.config['source_root'], experiment)
            immutable(prepared_path, encoded(prepared))
            # Intent precedes any effect. A missing completion remains visible and
            # cannot be retried by polling; an operator inspects original receipts.
            immutable(folder / ('started-' + str(position) + '.json'), encoded({
                'operation': saved['identity'], 'position': position, 'step': state['step'],
                'prepared_sha256': hashlib.sha256(encoded(prepared)).hexdigest()}))
            try:
                result = _step(runtime, saved, folder, position, prepared)
            except Exception as error:
                immutable(folder / ('failure-' + str(position) + '.json'), encoded({
                    'status': 'PRESERVED_ATTEMPT_REQUIRES_RECONCILIATION', 'exception': type(error).__name__,
                    'reason': str(error) if re.fullmatch('[A-Z][A-Z0-9_]{1,160}', str(error)) else 'OPERATION_FAILED',
                    'automatic_retry': False}))
                raise
            immutable(folder / ('step-' + str(position) + '.json'), encoded({'result': result}))
            if _blocked(result) or result.get('status') == 'AGENT_REVIEWED_DEFERRAL' or position + 1 == len(STEPS[saved['operation']['kind']]):
                return _finalize(saved, folder, result)
            return {'status': 'STEP_COMPLETE', 'operation': saved['identity'], 'step': state['step'], 'result': result}
    if waiting_validation:
        return {'status': 'AWAITING_VALIDATION_COMPLETION', 'operations': waiting_validation, 'models': 0}
    waiting = status(runtime.config)
    blocked = [row['operation'] for row in waiting['operations'] if row['status'] == 'RECONCILIATION_REQUIRED']
    return {'status': 'OPERATIONS_REQUIRE_RECONCILIATION' if blocked else 'AWAITING_REVIEWED_SELECTION',
            'blocked_operations': blocked, 'models': 0}


def recover(runtime, identity):
    """Explicitly project complete original authority replies; never retry a model.

    Later criticism may block the dependent next step. It does not erase or stop
    this read-only recovery of the original reviewed judgment. Ambiguous job
    starts and partial artifact copies remain with their fixed adapter's original
    reconciliation path; this operation cannot replay those effects.
    """
    _identity(runtime.config); pin(identity)
    root = _directory(runtime.config); folder = root / identity
    if not root.is_dir():
        raise ValueError('CONTINUING_OPERATION_ORIGINALS_REQUIRE_RECONCILIATION')
    with lock(root / '.operation.lock'):
        try:
            saved = _saved(folder); state = _state(folder)
        except STATE_ERRORS:
            raise ValueError('CONTINUING_OPERATION_ORIGINALS_REQUIRE_RECONCILIATION') from None
        if saved['source'] != runtime.config['source']:
            raise ValueError('CONTINUING_HISTORICAL_OPERATION_REQUIRES_ORIGINAL_INSTALLED_CONTEXT')
        if state['status'] in ('COMPLETE', 'DEFERRED', 'BLOCKED'):
            return {'status': state['status'], 'operation': identity, 'models': 0, 'admissions': 0}
        if state['status'] == 'FINALIZATION_PENDING':
            previous = json.loads(_read(folder / ('step-' + str(state['position'] - 1) + '.json')))['result']
            return _finalize(saved, folder, previous)
        kind = saved['operation']['kind']
        if state['status'] == 'RECONCILIATION_REQUIRED' and state['position'] == 1 and kind in ('ACCEPT_RESULT', 'ADOPT_FOLLOWUP'):
            # The acceptance/adoption application has no external side effect. Explicitly
            # reconcile its exact original intent/receipt, never rerun authority.
            _check_saved(runtime, saved)
            if runtime.q.status()['paused']:
                return {'status': 'PAUSED', 'models': 0}
            prepared = json.loads(_read(folder/'prepared.json'))
            authority = json.loads(_read(folder/'step-0.json'))['result']
            inputs = saved['operation']['inputs']
            if kind == 'ACCEPT_RESULT':
                from orchestrator.scientific_acceptance import apply
                result = apply(runtime.config, inputs['interpretation'],
                    prepared['formal_request'], authority['decision_path'],
                    original_client=_client(runtime), by=saved['actor'], recover=True)
            else:
                from orchestrator.scientific_adoption import apply
                result = apply(runtime.config, inputs['acceptance'], inputs['selection'],
                    prepared['formal_request'], authority['decision_path'],
                    original_client=_client(runtime), by=saved['actor'], recover=True)
            immutable(folder/'recovery-1.json', encoded({'models': 0, 'admissions': 0,
                'kind': ('ORIGINAL_ACCEPTANCE_APPLICATION_RECONCILED' if kind == 'ACCEPT_RESULT'
                         else 'ORIGINAL_ADOPTION_APPLICATION_RECONCILED')}))
            immutable(folder/'step-1.json', encoded({'result': result}))
            return _finalize(saved, folder, result)
        if state['status'] != 'RECONCILIATION_REQUIRED' or state['position'] != 0 or kind not in (
                'AUTHORIZE_TASK', 'AUTHORIZE_PROTOCOL', 'APPROVE_VERSION', 'LAUNCH_JOB', 'VALIDATE_RESULT', 'ACCEPT_RESULT', 'ADOPT_FOLLOWUP'):
            raise ValueError('CONTINUING_EFFECT_REQUIRES_ORIGINAL_ADAPTER_RECONCILIATION')
        prepared = json.loads(_read(folder / 'prepared.json'))
        client = _client(runtime)
        def originals_only(socket, operation, body):
            if operation != 'stage_status':
                raise ValueError('CONTINUING_RECOVERY_FORBIDS_NEW_ADMISSION_OR_MODEL')
            return client(socket, operation, body)
        if kind == 'AUTHORIZE_TASK':
            from orchestrator.research_task_authority import execute
            original = folder / 'authority'; output = folder / 'authority-recovery'
            result = execute(runtime.config, prepared['entry'], output,
                recover_from=None if output.exists() else original, client=originals_only)
        else:
            from orchestrator.formal_decisions import execute_formal_decision
            original = Path(runtime.config['state']) / 'formal-decisions' / identity
            output = original.with_name(identity + '-recovery')
            result = execute_formal_decision(runtime.config, prepared['formal_request'], output,
                recover_from=None if output.exists() else original, client=originals_only)
        if result.get('new_model_calls') != 0:
            raise ValueError('CONTINUING_RECOVERY_MUST_USE_ORIGINAL_REPLIES')
        immutable(folder / 'recovery-0.json', encoded({'original_output': str(original),
            'projection': str(output), 'models': 0, 'admissions': 0, 'later_criticism_rechecked_before_next_step': True}))
        immutable(folder / 'step-0.json', encoded({'result': result}))
        if result.get('status') == 'AGENT_REVIEWED_DEFERRAL' or len(STEPS[kind]) == 1:
            return _finalize(saved, folder, result)
        return {'status': 'ORIGINAL_AUTHORITY_RECOVERED', 'operation': identity, 'models': 0, 'admissions': 0,
                'next_step': STEPS[kind][1], 'result': result}
