"""Two fixed new-source replacements below an unsealed original operation.

Requesting is model-free. Runtime advances one normal authority/registration step.
Historical originals and their source remain unchanged; this is not recovery or
permission to retry an uncertain model. No caller supplies judgment or entry bytes.
"""
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re

from orchestrator import continuing_operations as ops
from orchestrator.handover_coordinator import digest
from orchestrator.hosted_cycle import encoded, immutable
from orchestrator.operations_report import private_root
from orchestrator.public_export import text
from orchestrator.remote_supervisor import lock

SCHEMA = 'linked-authority-replacement/v1'
DIRECTORY = 'replacement-1'
SECOND_DIRECTORY = 'replacement-2'
SECOND_SCHEMA = 'linked-authority-replacement/v2'
FAILURE = 'SCIENTIFIC_DECISION_OUTPUT_CONTEXT_MISMATCH'
SCOPE = ('Fresh current-source eligibility, not validation of the old judgment. DEFER remains available. '
         'Original scientific evidence limitations remain unchanged; no retry, launch or scientific acceptance.')


def _json(path):
    return json.loads(ops._read(path))


def _change(config, reference):
    from orchestrator.research_catalog import linked_change
    if not isinstance(reference, dict) or set(reference) != {'request_id', 'applied_event'}:
        raise ValueError('REPLACEMENT_CURRENT_CHANGE_REQUIRED')
    for value in reference.values(): ops.pin(value)
    history = linked_change(config, {'change_request': reference})
    applied = next(e for e in history['events'] if e['identity'] == reference['applied_event'])
    if applied.get('payload', {}).get('result_binding', {}).get('source') != config['source']:
        raise ValueError('REPLACEMENT_CURRENT_APPLIED_SOURCE_REQUIRED')
    return history


def _absent(runtime, task_id):
    from orchestrator.research_catalog import paths
    if task_id in paths(runtime.config) or runtime.q.db.execute(
            'SELECT 1 FROM research_submissions WHERE task_id=?', (task_id,)).fetchone():
        raise ValueError('REPLACEMENT_TASK_ALREADY_REGISTERED_OR_SUBMITTED')


def _proof(runtime, identity):
    """Recheck exact old-source inputs and protected replies, never admit a turn."""
    from orchestrator import research_task_authority as task_authority, scientific_authority as authority
    from orchestrator.continuing_research import selected_successor, read_reference
    from orchestrator.hosted_campaign import artifact_files, checked_reply
    ops.pin(identity)
    folder = ops._directory(runtime.config) / identity
    saved = ops._saved(folder)
    if saved['source'] == runtime.config['source']:
        raise ValueError('REPLACEMENT_REQUIRES_CHANGED_IMPLEMENTATION_SOURCE')
    state = ops._state(folder)
    if (saved['operation']['kind'] != 'AUTHORIZE_TASK' or state['position'] != 0
            or state['status'] != 'RECONCILIATION_REQUIRED'):
        raise ValueError('REPLACEMENT_UNSEALED_AUTHORIZE_TASK_REQUIRED')
    old = folder / 'authority'
    for name in ('receipt.json', 'round-1/decision.json', 'round-1/review.json'):
        if (old / name).exists() or (old / name).is_symlink():
            raise ValueError('REPLACEMENT_REFUSES_EXISTING_DECISION_OR_REVIEW')
    names = ('request.json', 'prepared.json', 'started-0.json', 'failure-0.json',
             'authority/authority-transport.json', 'authority/request.json', 'authority/evidence.json',
             'authority/stopped.json', 'authority/round-1/judgment.json',
             'authority/round-1/scientific_decision.provider-receipt.json')
    raws = {name: ops._read(folder / name) for name in names}
    values = {name: json.loads(raw) for name, raw in raws.items()}
    failure = values['failure-0.json']; stopped = values['authority/stopped.json']
    if (failure.get('status') != 'PRESERVED_ATTEMPT_REQUIRES_RECONCILIATION'
            or failure.get('exception') != 'ValueError' or failure.get('reason') != FAILURE
            or failure.get('automatic_retry') is not False
            or stopped.get('status') != 'PRESERVE_ORIGINAL_STAGES_RECONCILE_BEFORE_CONTINUATION'
            or stopped.get('exception_type') != 'ValueError' or stopped.get('automatic_retry') is not False):
        raise ValueError('REPLACEMENT_EXACT_OUTPUT_VALIDATION_FAILURE_REQUIRED')
    prepared = values['prepared.json']
    if set(prepared) != {'entry'}:
        raise ValueError('REPLACEMENT_ORIGINAL_PREPARATION_REQUIRED')
    started = values['started-0.json']
    if (started.get('operation') != identity or started.get('position') != 0
            or started.get('prepared_sha256') != hashlib.sha256(encoded(prepared)).hexdigest()):
        raise ValueError('REPLACEMENT_ORIGINAL_START_CHANGED')
    entry = prepared['entry']; task = entry['request']['task']
    # This first route is the unchanged ordinary discussion selection. Prospective
    # protocols/imports, readiness and executable scientific versions are separate.
    if (task.get('schema') != 'continuing-research-task/v1' or task.get('mode') != 'discuss'
            or entry['source'] != saved['source'] or entry['eligibility']['sha256'] != '0' * 64
            or Path(entry['eligibility']['path']) != old / 'round-1/decision.json'
            or task.get('selected_by') != saved['selected_by']
            or saved['operation']['inputs'] != {'selection': saved['selected_by']}
            or saved['operation']['operation_id'] != task['task_id']):
        raise ValueError('REPLACEMENT_UNCHANGED_DISCUSSION_SELECTION_REQUIRED')
    client = ops._client(runtime)
    selected = selected_successor(runtime.config, saved['selected_by']['task'], client=client)
    if selected.get('task') != task:
        raise ValueError('REPLACEMENT_ORIGINAL_SELECTED_TASK_CHANGED')
    predecessor, _ = ops._predecessor(runtime, saved['selected_by']['task'])
    if predecessor != saved['predecessor'] or predecessor not in entry['predecessors']:
        raise ValueError('REPLACEMENT_ORIGINAL_PREDECESSOR_CHANGED')
    required = {ref['task'] for ref in task['references']} | {saved['selected_by']['task']}
    if not required <= {row['task'] for row in entry['predecessors']}:
        raise ValueError('REPLACEMENT_EXACT_PREDECESSORS_REQUIRED')
    runtime.research_predecessors(entry)
    selection_raw = read_reference(runtime.config, saved['selected_by'])
    historical = {**runtime.config, 'source': entry['source'], 'source_root': entry['source_root']}
    root, subject, bindings = task_authority._identity(historical, entry)
    transport = task_authority._original_transport(historical, entry, bindings, old)
    if transport['packet']['reviewer_evidence']['input_evidence'].get('selected_operation') != saved:
        raise ValueError('REPLACEMENT_PROTECTED_ORIGINAL_OPERATION_CHANGED')
    original = values['authority/request.json']
    context = authority.decision_context(root, action=task_authority.ACTION, subject=subject, bindings=bindings)
    context_sha = authority.digest(authority.encoded(context))
    evidence = values['authority/evidence.json']
    if (original.get('context') != context or original.get('context_sha256') != context_sha
            or original.get('max_rounds') != 1
            or evidence != task_authority.evidence_for_packet(root, transport['packet'], entry['source'])
            or original.get('evidence_sha256') != {k: authority.digest(v.encode()) for k, v in evidence.items()}):
        raise ValueError('REPLACEMENT_ORIGINAL_AUTHORITY_CONTEXT_CHANGED')
    response = client('', 'stage_status', {'event': transport['event'], 'stage': 'continuation'})
    answer, receipt = checked_reply(response, 'continuation', hashlib.sha256(encoded(transport['packet'])).hexdigest())
    if (receipt != values['authority/round-1/scientific_decision.provider-receipt.json']
            or artifact_files(answer, ['judgment.json'])['judgment.json'].encode() != raws['authority/round-1/judgment.json']):
        raise ValueError('REPLACEMENT_PROTECTED_AUTHOR_ORIGINAL_CHANGED')
    task_authority._provenance(receipt, 'codex', transport['event'], transport['packet'])
    review = client('', 'stage_status', {'event': transport['event'], 'stage': 'review'})
    if review != {'status': 'NOT_STARTED_RECONCILIATION_REQUIRED'}:
        raise ValueError('REPLACEMENT_REVIEW_MUST_BE_ORIGINALLY_NOT_STARTED')
    judgment = values['authority/round-1/judgment.json']
    if (set(judgment) != {'context_sha256', 'decision', 'rationale', 'transition', 'reconsideration'}
            or not isinstance(judgment['context_sha256'], str) or judgment['context_sha256'] == context_sha):
        raise ValueError('REPLACEMENT_EXACT_CONTEXT_MISMATCH_REQUIRED')
    return {'schema': 'authority-replacement-original-proof/v1', 'operation': identity,
            'source': saved['source'], 'original_file_sha256': {k: hashlib.sha256(v).hexdigest() for k, v in raws.items()},
            'entry': entry, 'request': original, 'packet': transport['packet'],
            'event': transport['event'], 'selection': selection_raw.decode(),
            'invalid_judgment': raws['authority/round-1/judgment.json'].decode(),
            'failure': failure, 'stopped': stopped, 'provider_receipt': receipt,
            'review_original_status': review, 'scientific_acceptance': False}



def _input_refusal(reply, transport):
    """Check actual protected raw refusal bytes, never a controller manifest."""
    required = {'status','event','packet_sha256','packet','originals','file_sha256','input_characters',
                'active','answer_present','receipt_present','review_present','disposition_present'}
    if (not isinstance(reply, dict) or not required <= set(reply)
            or set(reply) - required - {'schema','version','limit_chars','scientific_acceptance','retry_authorized','admissions'}
            or reply['status'] != 'CONCLUSIVE_INPUT_REFUSAL'
            or ('schema' in reply and reply['schema'] != 'protected-input-refusal/v1')
            or ('version' in reply and reply['version'] != 1)
            or ('limit_chars' in reply and reply['limit_chars'] != 1048576)
            or ('scientific_acceptance' in reply and reply['scientific_acceptance'] is not False)
            or ('retry_authorized' in reply and reply['retry_authorized'] is not False)
            or ('admissions' in reply and reply['admissions'] != 0)
            or reply['event'] != transport['event'] or reply['packet'] != transport['packet']
            or reply['packet_sha256'] != hashlib.sha256(encoded(transport['packet'])).hexdigest()
            or any(reply[k] is not False for k in
                   ('active','answer_present','receipt_present','review_present','disposition_present'))):
        raise ValueError('REPLACEMENT_PROTECTED_INPUT_REFUSAL_REQUIRED')
    names = {'binding.json','continuation.request.json','continuation.started.json',
             'continuation.ended.json','continuation.process.json','continuation.process-identity.json',
             'continuation.stdout','continuation.stderr'}
    originals = reply['originals']; hashes = reply['file_sha256']
    if (not isinstance(originals, dict) or set(originals) != names or not isinstance(hashes, dict)
            or not names | {'packet.json','continuation.input.md','continuation.operating-context.json'} <= set(hashes)):
        raise ValueError('REPLACEMENT_PROTECTED_INPUT_ORIGINALS_REQUIRED')
    for name, value in hashes.items(): ops.pin(value)
    for name, value in originals.items():
        if (not isinstance(value, str) or len(value.encode()) > 30000
                or hashlib.sha256(value.encode()).hexdigest() != hashes[name]):
            raise ValueError('REPLACEMENT_PROTECTED_INPUT_ORIGINAL_CHANGED')
    binding = json.loads(originals['binding.json'])
    started = json.loads(originals['continuation.started.json'])
    ended = json.loads(originals['continuation.ended.json'])
    process = json.loads(originals['continuation.process.json'])
    thread = json.loads(originals['continuation.stdout'])
    prefix = ('Error: turn/start: turn/start failed: Input exceeds the maximum length of 1048576 '
              'characters. (code -32602), data: ')
    stderr = originals['continuation.stderr']
    if not stderr.startswith(prefix):
        raise ValueError('REPLACEMENT_EXACT_INPUT_TOO_LARGE_REQUIRED')
    refusal = json.loads(stderr[len(prefix):])
    if (set(refusal) != {'input_error_code','max_chars','actual_chars'}
            or refusal['input_error_code'] != 'input_too_large' or refusal['max_chars'] != 1048576
            or type(refusal['actual_chars']) is not int or refusal['actual_chars'] <= 1048576
            or reply['input_characters'] != refusal['actual_chars']
            or stderr != prefix + json.dumps(refusal, separators=(',', ':')) + '\n'
            or set(thread) != {'type','thread_id'} or thread['type'] != 'thread.started'
            or not re.fullmatch('[A-Za-z0-9_-]{6,128}', thread['thread_id'])
            or len(originals['continuation.stdout'].splitlines()) != 1):
        raise ValueError('REPLACEMENT_EXACT_INPUT_TOO_LARGE_REQUIRED')
    if (binding != {'event':transport['event'],'packet_sha256':reply['packet_sha256']}
            or hashes['packet.json'] != reply['packet_sha256']
            or type(ended.get('returncode')) is not int or ended['returncode'] != 1
            or type(process.get('returncode')) is not int or process['returncode'] != 1
            or process.get('stage') != 'continuation' or started.get('stage') != 'continuation'
            or process.get('requested_model') != 'gpt-6-astra'
            or started.get('requested_model') != process['requested_model']
            or datetime.fromisoformat(ended['ended_utc']) < datetime.fromisoformat(started['started_utc'])
            or any(process.get(field) != hashes[name] for field,name in (
                ('input_sha256','continuation.input.md'),('operating_context_sha256','continuation.operating-context.json'),
                ('stdout_sha256','continuation.stdout'),('stderr_sha256','continuation.stderr')))):
        raise ValueError('REPLACEMENT_ORIGINAL_INPUT_PROCESS_CHANGED')
    # Keep the complete science once. The packet remains root-original and is
    # compared above, but is not recursively copied into the next evidence.
    return {k:v for k,v in reply.items() if k != 'packet'}


def _input_proof(runtime, identity, previous_request):
    """Only fixed replacement2 after conclusive input refusal of replacement1."""
    from types import SimpleNamespace
    from orchestrator import research_task_authority as task_authority, scientific_authority as authority
    base = _proof(runtime, identity)
    parent = ops._directory(runtime.config) / identity
    first = parent / DIRECTORY
    previous = _load(first)
    if (previous['number'] != 1 or previous['identity'] != previous_request
            or previous['source'] == runtime.config['source']
            or previous['source'] == base['source'] or encoded(base) != ops._read(first / 'original-proof.json')):
        raise ValueError('REPLACEMENT_FIXED_SECOND_PREDECESSOR_REQUIRED')
    for name in ('step-0.json','step-1.json','result.json','started-1.json',
                 'authority/receipt.json','authority/round-1/judgment.json','authority/round-1/review.json',
                 'authority/round-1/decision.json','authority/round-1/scientific_decision.provider-receipt.json',
                 'authority/round-1/scientific_decision_review.provider-receipt.json'):
        if (first/name).exists() or (first/name).is_symlink():
            raise ValueError('REPLACEMENT_SECOND_REFUSES_ANSWER_OR_RESULT')
    first_state = _state(first)
    if first_state['status'] != 'RECONCILIATION_REQUIRED' or first_state['position'] != 0:
        raise ValueError('REPLACEMENT_FIXED_SECOND_PREDECESSOR_REQUIRED')
    names = ('request.json','prepared.json','original-proof.json','started-0.json','failure-0.json',
             'authority/authority-transport.json','authority/request.json','authority/evidence.json','authority/stopped.json')
    raws = {name:ops._read(first/name) for name in names}
    values = {name:json.loads(raw) for name,raw in raws.items()}
    if (values['started-0.json'] != {'request':previous_request,'position':0,'prepared_sha256':previous['prepared_sha256']}
            or values['failure-0.json'] != {'request':previous_request,'exception':'ValueError',
                'reason':'MODEL_FAILED_RECONCILE_PRIVATE_EVIDENCE','automatic_retry':False}
            or values['authority/stopped.json'] != {'status':'PRESERVE_ORIGINAL_STAGES_RECONCILE_BEFORE_CONTINUATION',
                'exception_type':'ValueError','automatic_retry':False}):
        raise ValueError('REPLACEMENT_SECOND_ORIGINAL_FAILURE_REQUIRED')
    entry = values['prepared.json']['entry']
    historical = {**runtime.config,'source':previous['source'],'source_root':entry['source_root']}
    root, subject, bindings = task_authority._identity(historical, entry)
    transport = task_authority._original_transport(historical, entry, bindings, first/'authority')
    _entry(SimpleNamespace(config=historical), previous, base, first, transport['packet']['recorded_changes'])
    original = values['authority/request.json']
    context = authority.decision_context(root, action=task_authority.ACTION, subject=subject, bindings=bindings)
    expected_evidence = task_authority.evidence_for_packet(root, transport['packet'], previous['source'])
    if (original.get('context') != context or original.get('context_sha256') != authority.digest(authority.encoded(context))
            or original.get('max_rounds') != 1 or values['authority/evidence.json'] != expected_evidence
            or original.get('evidence_sha256') != {k:authority.digest(v.encode()) for k,v in expected_evidence.items()}):
        raise ValueError('REPLACEMENT_SECOND_AUTHORITY_CONTEXT_CHANGED')
    refusal = _input_refusal(ops._client(runtime)('', 'stage_input_refusal', {'event':transport['event']}), transport)
    _absent(runtime, entry['request']['task']['task_id'])
    return {'schema':'authority-input-replacement-original-proof/v1','operation':identity,'source':previous['source'],
            'entry':entry,'base_original':base,'previous_request':previous,
            'previous_file_sha256':{k:hashlib.sha256(v).hexdigest() for k,v in raws.items()},
            'previous_reviewed_repair':transport['packet']['recorded_changes'],
            'input_refusal':refusal,'scientific_acceptance':False}


def _load(folder):
    request = _json(folder / 'request.json')
    core = {k: v for k, v in request.items() if k != 'identity'}
    if ((request.get('schema'), request.get('number'), folder.name) not in
            ((SCHEMA, 1, DIRECTORY), (SECOND_SCHEMA, 2, SECOND_DIRECTORY))
            or request.get('operation') != folder.parent.name
            or digest(core) != request.get('identity')):
        raise ValueError('REPLACEMENT_IMMUTABLE_REQUEST_CHANGED')
    if request['number'] == 2: ops.pin(request.get('previous_request'))
    elif 'previous_request' in request: raise ValueError('REPLACEMENT_IMMUTABLE_REQUEST_CHANGED')
    for field in ('source', 'original_source'): ops.pin(request[field], 40)
    for name, field in [('original-proof.json', 'original_proof_sha256'), ('prepared.json', 'prepared_sha256')]:
        if hashlib.sha256(ops._read(folder / name)).hexdigest() != request[field]:
            raise ValueError('REPLACEMENT_SAVED_INPUT_CHANGED')
    return request


def _entry(runtime, saved, proof, folder, history):
    """Reconstruct the only allowed entry; a rehashed local file is not authority."""
    from orchestrator.continuing_research import read_evidence
    prepared = _json(folder / 'prepared.json')
    if set(prepared) != {'entry'}: raise ValueError('REPLACEMENT_CURRENT_ENTRY_CHANGED')
    entry = prepared['entry']
    evidence = read_evidence(runtime.config, entry['request'])
    core = {k: v for k, v in saved.items() if k not in ('identity', 'prepared_sha256')}
    old_history = evidence.get('current_reviewed_repair', {})
    original_events = old_history.get('events', [])
    if (set(evidence) != {'linked_replacement', 'preserved_invalid_original', 'current_reviewed_repair', 'scope'}
            or evidence['linked_replacement'] != core or evidence['preserved_invalid_original'] != proof
            or evidence['scope'] != SCOPE
            or not original_events or history['events'][:len(original_events)] != original_events
            or history.get('request') != old_history.get('request')
            or not any(e.get('event') == 'REVIEW' and e.get('payload', {}).get('verdict') == 'APPROVE'
                       and e['payload'].get('applied_event') == saved['change_request']['applied_event']
                       for e in original_events)):
        raise ValueError('REPLACEMENT_EXACT_FAILURE_AND_REPAIR_EVIDENCE_CHANGED')
    expected = deepcopy(proof['entry'])
    expected.update(source=saved['source'], source_root=runtime.config['source_root'],
                    change_request=saved['change_request'], eligibility={
                        'path': str(folder / 'authority/round-1/decision.json'), 'sha256': '0' * 64})
    expected['request'].update(day=saved['created_at_utc'][:10], initiator=saved['by'],
        evidence_file=entry['request']['evidence_file'], evidence_sha256=entry['request']['evidence_sha256'])
    if expected != entry: raise ValueError('REPLACEMENT_CURRENT_ENTRY_CHANGED')
    return entry


def _state(folder):
    request = _load(folder)
    result = folder / 'result.json'
    row = {'operation': request['operation'], 'replacement': request['number'], 'source': request['source'],
           'original_source': request['original_source'], 'request': request['identity'],
           'reason': request['reason'], 'requested_by': request['by'],
           'directory': str(folder), 'models': 0, 'automatic_retry': False}
    if result.exists():
        value = _json(result)
        if (value.get('request') != request['identity'] or value.get('source') != request['source']
                or value.get('operation') != request['operation'] or value.get('replacement') != request['number']
                or value.get('scientific_acceptance') is not False
                or value.get('status') not in ('COMPLETE', 'DEFERRED')):
            raise ValueError('REPLACEMENT_RESULT_BINDING_CHANGED')
        return {**row, 'status': value['status'], 'position': 2, 'result': value['result']}
    if (folder / 'step-1.json').exists():
        return {**row, 'position': 2, 'status': 'FINALIZATION_PENDING', 'step': 'FINALIZE'}
    if (folder / 'step-0.json').exists() and _json(folder / 'step-0.json')['result'].get('status') == 'AGENT_REVIEWED_DEFERRAL':
        return {**row, 'position': 1, 'status': 'FINALIZATION_PENDING', 'step': 'FINALIZE_DEFERRAL'}
    position = 1 if (folder / 'step-0.json').exists() else 0
    uncertain = any((folder / (name + '-' + str(position) + '.json')).exists()
                    for name in ('started', 'preflight-failure'))
    return {**row, 'position': position, 'status': 'RECONCILIATION_REQUIRED' if uncertain else 'QUEUED',
            'step': 'REGISTER_AND_SUBMIT' if position else 'FRESH_CURRENT_SOURCE_AUTHORITY'}


def observed(folder):
    """Attach one readable linked state to the unchanged original operation row."""
    replacement = Path(folder) / SECOND_DIRECTORY
    if not replacement.exists() and not replacement.is_symlink(): replacement = Path(folder) / DIRECTORY
    if not replacement.exists() and not replacement.is_symlink(): return None
    try:
        result = _state(replacement)
        if result['replacement'] == 2:
            result['prior_replacement'] = _state(Path(folder) / DIRECTORY)
        return result
    except ops.STATE_ERRORS:
        return {'operation': Path(folder).name, 'replacement': 2 if replacement.name == SECOND_DIRECTORY else 1, 'status': 'RECONCILIATION_REQUIRED',
                'reason': 'REPLACEMENT_ORIGINALS_REQUIRE_RECONCILIATION', 'models': 0, 'automatic_retry': False}


def request(runtime, identity, *, by, reason, change_request, expected_source, previous_request=None):
    """Save exactly one attributable replacement intent. Never call a model."""
    from orchestrator.change_requests import actor
    from orchestrator.continuing_research import preserve_evidence
    ops._identity(runtime.config); ops.pin(identity); ops.pin(expected_source, 40); actor(by)
    if expected_source != runtime.config['source']:
        raise ValueError('REPLACEMENT_EXPECTED_CURRENT_SOURCE_CHANGED')
    if not isinstance(reason, str) or not reason.strip(): raise ValueError('REPLACEMENT_REASON_REQUIRED')
    text(reason, limit=2000)
    number = 1 if previous_request is None else 2
    if previous_request is not None: ops.pin(previous_request)
    root = ops._directory(runtime.config)
    with lock(root / '.operation.lock'):
        folder = root / identity / (DIRECTORY if number == 1 else SECOND_DIRECTORY)
        if folder.exists() or folder.is_symlink():
            saved = _load(folder)
            if any(saved[k] != v for k, v in {'by': by, 'reason': reason, 'change_request': change_request,
                                             'source': expected_source}.items()):
                raise ValueError('ONE_EXPLICIT_REPLACEMENT_ALREADY_RECORDED')
            if saved.get('previous_request') != previous_request:
                raise ValueError('REPLACEMENT_PREVIOUS_REQUEST_CHANGED')
            return {**_state(folder), 'duplicate': True, 'admissions': 0}
        runtime.deployment_status()
        history = _change(runtime.config, change_request)
        proof = _proof(runtime, identity) if number == 1 else _input_proof(runtime, identity, previous_request)
        if number == 2 and change_request == proof['previous_request']['change_request']:
            raise ValueError('REPLACEMENT_CHANGED_REVIEWED_APPLICATION_REQUIRED')
        _absent(runtime, proof['entry']['request']['task']['task_id'])
        core = {'schema': SCHEMA if number == 1 else SECOND_SCHEMA, 'operation': identity, 'number': number, 'source': expected_source,
                'original_source': proof['source'], 'by': by, 'reason': reason, 'change_request': change_request,
                'created_at_utc': datetime.now(timezone.utc).isoformat(),
                'original_proof_sha256': hashlib.sha256(encoded(proof)).hexdigest()}
        if number == 2: core['previous_request'] = previous_request
        folder = private_root(folder)
        immutable(folder / 'original-proof.json', encoded(proof))
        evidence = preserve_evidence(runtime.config, {
            'linked_replacement': core, 'preserved_invalid_original': proof,
            'current_reviewed_repair': history,
            'scope': SCOPE})
        entry = deepcopy(proof['entry'])
        entry.update(source=expected_source, source_root=runtime.config['source_root'], change_request=change_request,
                     eligibility={'path': str(folder / 'authority/round-1/decision.json'), 'sha256': '0' * 64})
        entry['request'].update(**evidence, day=core['created_at_utc'][:10], initiator=by)
        prepared = encoded({'entry': entry})
        immutable(folder / 'prepared.json', prepared)
        core['prepared_sha256'] = hashlib.sha256(prepared).hexdigest()
        immutable(folder / 'request.json', encoded({**core, 'identity': digest(core)}))
        return {**_state(folder), 'duplicate': False, 'admissions': 0}


def advance(runtime):
    """One step under existing operation/admission locks; uncertain starts stop."""
    from orchestrator.research_task_authority import execute
    from orchestrator.continuing_research import register_and_submit
    from orchestrator.campaign import require_no_human_stop
    ops._identity(runtime.config)
    root = private_root(ops._directory(runtime.config))
    with lock(root / '.operation.lock'):
        if runtime.q.status()['paused']: return {'status': 'PAUSED', 'models': 0}
        for parent in sorted(root.iterdir()):
            if not re.fullmatch('[0-9a-f]{64}', parent.name): continue
            folder = parent / SECOND_DIRECTORY
            if not folder.exists() and not folder.is_symlink(): folder = parent / DIRECTORY
            if not folder.exists() and not folder.is_symlink(): continue
            state = observed(parent)
            if state['status'] not in ('QUEUED', 'FINALIZATION_PENDING'): continue
            saved = _load(folder)
            if saved['source'] != runtime.config['source']: continue
            if state['status'] == 'FINALIZATION_PENDING':
                deferred = state['step'] == 'FINALIZE_DEFERRAL'
                result = _json(folder / ('step-0.json' if deferred else 'step-1.json'))['result']
                _finish(folder, saved, result, 'DEFERRED' if deferred else 'COMPLETE')
                return _state(folder)
            runtime.deployment_status(); history = _change(runtime.config, saved['change_request'])
            proof = (_proof(runtime, saved['operation']) if saved['number'] == 1 else
                     _input_proof(runtime, saved['operation'], saved['previous_request']))
            if encoded(proof) != ops._read(folder / 'original-proof.json'):
                raise ValueError('REPLACEMENT_HISTORICAL_ORIGINALS_CHANGED')
            entry = _entry(runtime, saved, proof, folder, history)
            _absent(runtime, entry['request']['task']['task_id'])
            require_no_human_stop(runtime.config['source_root'], entry['request']['task']['experiment'])
            position = state['position']
            if position == 0:
                from orchestrator.research_task_authority import preflight
                try:
                    preflight(runtime.config, entry, client=ops._client(runtime))
                except Exception as error:
                    immutable(folder / 'preflight-failure-0.json', encoded({
                        'request': saved['identity'], 'exception': type(error).__name__,
                        'reason': str(error) if re.fullmatch('[A-Z][A-Z0-9_]{1,160}', str(error)) else 'REPLACEMENT_PREFLIGHT_REFUSED',
                        'provider_calls': 0, 'admissions': 0, 'automatic_retry': False}))
                    raise
            immutable(folder / ('started-' + str(position) + '.json'), encoded({
                'request': saved['identity'], 'position': position, 'prepared_sha256': saved['prepared_sha256']}))
            try:
                if position == 0:
                    result = execute(runtime.config, entry, folder / 'authority', client=ops._client(runtime))
                else:
                    previous = _json(folder / 'step-0.json')['result']
                    if previous.get('status') != 'AGENT_REVIEWED_DECISION_READY':
                        raise ValueError('REPLACEMENT_ACTUAL_ELIGIBILITY_REQUIRED')
                    entry['eligibility'] = previous['eligibility']
                    result = register_and_submit(runtime, entry)
            except Exception as error:
                immutable(folder / ('failure-' + str(position) + '.json'), encoded({
                    'request': saved['identity'], 'exception': type(error).__name__, 'automatic_retry': False,
                    'reason': str(error) if re.fullmatch('[A-Z][A-Z0-9_]{1,160}', str(error)) else 'REPLACEMENT_FAILED'}))
                raise
            immutable(folder / ('step-' + str(position) + '.json'), encoded({'result': result}))
            if position == 1 or result.get('status') == 'AGENT_REVIEWED_DEFERRAL':
                _finish(folder, saved, result, 'COMPLETE' if position == 1 else 'DEFERRED')
            return {**_state(folder), 'step_result': result, 'models': result.get('new_model_calls', 0)}
    return {'status': 'NO_REPLACEMENT_WORK', 'models': 0}


def _finish(folder, saved, result, status):
    immutable(folder / 'result.json', encoded({'request': saved['identity'],
        'operation': saved['operation'], 'replacement': saved['number'], 'source': saved['source'],
        'status': status, 'result': result, 'scientific_acceptance': False,
        'original_operation_unchanged': True}))
