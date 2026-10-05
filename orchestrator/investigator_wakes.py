"""Fixed investigator templates over existing scientific tasks and decisions.

The controller proposes checked event identities. The protected broker reserves
each original event once, then ordinary eligibility and campaign stages do the
science. Polling, template instantiation and reservation invoke no model.
"""
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import sqlite3

from orchestrator.handover_coordinator import digest
from orchestrator.hosted_cycle import encoded, immutable
from orchestrator.operations_report import private_root
from orchestrator.remote_supervisor import lock

SCHEMA = 'investigator-task/v1'
TEMPLATE = 'investigator-template/v1'
WAKE = 'investigator-wake/v2'
KINDS = ('BOOTSTRAP', 'TASK', 'FAILURE', 'OPERATION', 'JOB', 'STEERING', 'DISPOSITION', 'ELIGIBILITY237_REPLACEMENT', 'ELIGIBILITY247_REPLACEMENT', 'ELIGIBILITY263_RECONSIDERATION')
OPERATION_KINDS = ('AUTHORIZE_PROTOCOL', 'MATERIALIZE_VERSION', 'APPROVE_VERSION', 'IMPORT_RESULT', 'VALIDATE_RESULT', 'ACCEPT_RESULT', 'ADOPT_FOLLOWUP')
MAX_EVENTS = 4
ERRORS = (OSError, ValueError, KeyError, TypeError, AttributeError, sqlite3.Error)


def pin(value):
    if not isinstance(value, str) or not re.fullmatch('[0-9a-f]{64}', value):
        raise ValueError('INVESTIGATOR_EXACT_PIN_REQUIRED')
    return value


def read(path):
    from orchestrator.scientific_authority import read as original
    return original(path, limit=2000000)


def setting(config):
    value = config.get('investigator')
    if value is None:
        return None
    if not isinstance(value, dict) or set(value) != {'template', 'template_sha256'}:
        raise ValueError('INVESTIGATOR_INSTALLED_TEMPLATE_REQUIRED')
    template = value['template']
    if (not isinstance(template, dict) or set(template) - {'eligibility_replacement'} != {'schema', 'template_id', 'experiment',
            'request', 'evidence_file', 'evidence_sha256', 'references', 'change_request'}
            or template['schema'] != TEMPLATE or template['experiment'] not in ('P001', 'P002', 'P003')
            or not re.fullmatch('[a-z0-9][a-z0-9-]{0,62}', str(template['template_id']))
            or not isinstance(template['request'], str) or not template['request'].strip()
            or not isinstance(template['references'], list) or len(template['references']) > 16
            or not isinstance(template['evidence_file'], str) or not Path(template['evidence_file']).is_absolute()):
        raise ValueError('INVESTIGATOR_TEMPLATE_CONTRACT')
    from orchestrator.continuing_research import reference
    from orchestrator.public_export import text
    text(template['request'], limit=8000)
    for ref in template['references']:
        reference(ref)
    change = template['change_request']
    if not isinstance(change, dict) or set(change) != {'request_id', 'applied_event'}:
        raise ValueError('INVESTIGATOR_TEMPLATE_CHANGE_REQUIRED')
    for value_pin in (*change.values(), template['evidence_sha256']):
        pin(value_pin)
    if 'eligibility_replacement' in template:
        replacement = template['eligibility_replacement']
        if not isinstance(replacement, dict) or set(replacement) != {'request_id', 'applied_event'}:
            raise ValueError('INVESTIGATOR_REPLACEMENT_CHANGE_REQUIRED')
        for bound in replacement.values(): pin(bound)
    if digest(template) != pin(value['template_sha256']):
        raise ValueError('INVESTIGATOR_TEMPLATE_CHANGED')
    return value


def service(config):
    return {'kind': 'service', 'identity': 'controller-uid:' + str(config['controller_uid']),
        'identity_source': 'authenticated_controller_uid', 'operation': 'installed_investigator_template',
        'source': config['source']}


def task_contract(task):
    if (not isinstance(task, dict) or set(task) != {'schema', 'task_id', 'experiment', 'mode',
            'request', 'references', 'selected_by', 'template_sha256', 'wake_sha256', 'purpose'}
            or task['schema'] != SCHEMA or task['mode'] != 'investigate' or task['selected_by'] is not None
            or task['purpose'] not in ('CHARTER_SELECTION', 'FAILURE_DIAGNOSIS')
            or task['task_id'] != 'investigator-' + pin(task['wake_sha256'])):
        raise ValueError('INVESTIGATOR_TEMPLATE_TASK_REQUIRED')
    pin(task['template_sha256'])
    from orchestrator.continuing_research import task_contract as normal
    base = {key: value for key, value in task.items() if key not in ('template_sha256', 'wake_sha256', 'purpose')}
    normal({**base, 'schema': 'continuing-research-task/v1'})
    return {'version': 2, 'experiment': task['experiment'], 'mode': 'investigate',
            'operation_sha256': digest(task)}


def grounding(root, task):
    """Inspect the adopted charter without fabricating a predecessor protocol."""
    task_contract(task)
    from orchestrator.campaign import require_no_human_stop
    from orchestrator.research_context import selected_prediction_context
    from orchestrator import scientific_authority
    require_no_human_stop(root, task['experiment'])
    selected = selected_prediction_context(root)
    if not selected: raise ValueError('INVESTIGATOR_SELECTED_CHARTER_REQUIRED')
    current = scientific_authority.context(root)
    names = ('campaigns/isles24-pilot/CAMPAIGN.md', current['binding']['path'],
        current['policy']['direction_path'], 'docs/operations/REMOTE_OPERATING_DIRECTION.md',
        'docs/operations/CLAUDE_REVIEWER_DIRECTIVE.md')
    return {**{name: read(Path(root)/name).decode() for name in names}, **selected,
        'investigator-scope.json': json.dumps({'status':'SELECTION_ONLY', 'task':task,
            'execution':False, 'scientific_approval':False}, sort_keys=True)}


def event(kind, identity, original_sha256):
    if kind not in KINDS:
        raise ValueError('INVESTIGATOR_EVENT_KIND_REQUIRED')
    return {'kind': kind, 'identity': pin(identity), 'original_sha256': pin(original_sha256)}


def event_key(value):
    if not isinstance(value, dict) or set(value) != {'kind', 'identity', 'original_sha256'}:
        raise ValueError('INVESTIGATOR_EVENT_CONTRACT')
    event(**value)
    # Deliberately excludes template, batch and observation time.
    return digest({'kind': value['kind'], 'identity': value['identity']})


def _model_event(identity, source):
    return {'turn_id': identity, 'source': source, 'attempt': '1',
            'branch': 'astra/infrastructure-milestone-record', 'kind': 'astra_turn'}


def _task(config, identity, client, *, investigator=False, include_originals=False):
    """Verify copied task artifacts against all three protected original replies."""
    if type(include_originals) is not bool:
        raise ValueError("INVESTIGATOR_ORIGINAL_ANSWER_MODE_REQUIRED")
    from orchestrator.hosted_campaign import checked_reply, artifact_files
    from orchestrator.campaign_pipeline import MODES
    from orchestrator.hosted_campaign_task import task_contract as contract
    folder = Path(config['state']) / 'tasks' / pin(identity)
    packet = json.loads(read(folder / 'packet.json'))
    disposition_raw = read(folder / 'scientific-disposition.json')
    disposition = json.loads(disposition_raw)
    source = disposition['source']
    model_event = _model_event(identity, source)
    original = client('', 'stage_packet', {'event': model_event})
    packet_sha = hashlib.sha256(encoded(packet)).hexdigest()
    if (original.get('status') != 'COMPLETE' or original.get('packet') != packet
            or original.get('packet_sha256') != packet_sha):
        raise ValueError('INVESTIGATOR_TASK_ORIGINAL_PACKET_CHANGED')
    task = packet['campaign_task']; contract(task)
    if (task['mode'] == 'investigate') != investigator:
        raise ValueError('INVESTIGATOR_SELF_TRIGGER_FORBIDDEN')
    answers = {}; receipts = {}
    for stage in ('continuation', 'review', 'disposition'):
        answers[stage], receipts[stage] = checked_reply(client('', 'stage_status', {'event': model_event, 'stage': stage}), stage, packet_sha)
        if receipts[stage].get('stage') != stage or not receipts[stage].get('session_id'):
            raise ValueError('INVESTIGATOR_ORIGINAL_PROVIDER_IDENTITY_REQUIRED')
    files = artifact_files(answers['continuation'], MODES[task['mode']])
    review = artifact_files(answers['review'], ['review.json'])['review.json']
    verdict = json.loads(review).get('verdict')
    if (verdict not in ('APPROVE', 'REVISE', 'REQUEST_CHANGES') or disposition.get('task') != identity
            or disposition.get('status') != 'DISPOSITION_RECORDED'
            or disposition.get('review_verdict') != verdict
            or disposition.get('acceptance_status') != ('APPROVED_PROPOSAL_ONLY' if verdict == 'APPROVE' else 'NOT_ACCEPTED')
            or disposition.get('reviewer', {}).get('session_id') != receipts['review']['session_id']
            or disposition.get('reviewer', {}).get('model') != receipts['review']['actual_model']
            or disposition.get('disposition_actor', {}).get('session_id') != receipts['disposition']['session_id']
            or disposition.get('disposition_sha256') != hashlib.sha256(answers['disposition'].encode()).hexdigest()):
        raise ValueError('INVESTIGATOR_ORIGINAL_TASK_DISPOSITION_CHANGED')
    refs = []
    for name, body in {**files, 'review.json': review}.items():
        relative = 'round-1/' + name; sha = hashlib.sha256(body.encode()).hexdigest()
        if disposition['artifact_sha256'].get(relative) != sha:
            raise ValueError('INVESTIGATOR_ORIGINAL_TASK_ARTIFACT_CHANGED')
        if name != 'review.json':
            refs.append({'task': identity, 'artifact': relative, 'sha256': sha})
    return {'event': event('TASK', identity, hashlib.sha256(disposition_raw).hexdigest()),
        'packet': packet, 'disposition': disposition, 'review': json.loads(review), 'references': refs,
        **({'original_answers': answers, 'original_receipts': receipts} if include_originals else {}),
        'predecessor': {'task': identity, 'source': source,
            'disposition_sha256': hashlib.sha256(disposition_raw).hexdigest(), 'requires': 'DISPOSITION_RECORDED'}}


def _failure(config, identity, client):
    """An ended transport attempt is evidence for discussion, never a retry."""
    pin(identity)
    path = Path(config['state'])/'coordinator.sqlite'
    if path.is_symlink() or not path.is_file(): raise ValueError('EXISTING_CONTROLLER_STATE_REQUIRED')
    db = sqlite3.connect(path.absolute().as_uri()+'?mode=ro', uri=True)
    try:
        row = db.execute('SELECT binding,status FROM tasks WHERE id=?', (identity,)).fetchone()
    finally: db.close()
    if row is None or row[1] != 'BLOCKED':
        raise ValueError('INVESTIGATOR_BLOCKED_ORIGINAL_TASK_REQUIRED')
    binding = json.loads(row[0])
    model_event = _model_event(identity, binding['source'])
    original = client('', 'stage_packet', {'event': model_event})
    packet = json.loads(read(Path(config['state'])/'tasks'/identity/'packet.json'))
    if (original.get('status') != 'COMPLETE' or original.get('packet') != packet
            or original.get('packet_sha256') != hashlib.sha256(encoded(packet)).hexdigest()):
        raise ValueError('INVESTIGATOR_TASK_ORIGINAL_PACKET_CHANGED')
    from orchestrator.hosted_campaign_task import task_contract as contract
    task = packet['campaign_task']; contract(task)
    if task['mode'] == 'investigate':
        raise ValueError('INVESTIGATOR_SELF_TRIGGER_FORBIDDEN')
    failure = client('', 'stage_failure', {'event': model_event})
    if (failure.get('status') != 'ENDED_WITHOUT_VALIDATED_STAGE'
            or failure.get('packet_sha256') != original['packet_sha256']
            or failure.get('scientific_acceptance') is not False or failure.get('retry_authorized') is not False):
        raise ValueError('INVESTIGATOR_ENDED_ORIGINAL_FAILURE_REQUIRED')
    return {'event':event('FAILURE',identity,digest(failure)), 'packet':packet,
        'transport_failure':failure, 'scientific_outcome':'UNKNOWN',
        'permitted_followup':'Discuss the preserved failure and a reasoned next step; do not retry or claim a scientific result.'}


def _steering(config, identity, client):
    from orchestrator.change_requests import encoded as request_bytes
    original = client('', 'read_recorded_steering', {'request_id':pin(identity)})
    if (not isinstance(original, dict) or set(original) != {'request_id','original_sha256','request','provenance'}
            or original['request_id'] != identity
            or hashlib.sha256(request_bytes({key:value for key,value in original.items() if key != 'original_sha256'})).hexdigest()
                != pin(original['original_sha256'])):
        raise ValueError('INVESTIGATOR_RECORDED_STEERING_ORIGINAL_REQUIRED')
    return {'event':event('STEERING',identity,original['original_sha256']),
        'recorded_proposal':original, 'proposal_only':True}


def _formal(config, decision_path, client):
    from orchestrator.formal_decisions import original_transport, verify_original_decision, scientific_root
    path = Path(decision_path)
    if (not path.is_absolute() or path.parent.name != 'round-1'
            or path.parent.parent.parent != Path(config['state']) / 'formal-decisions'):
        raise ValueError('INVESTIGATOR_FIXED_FORMAL_DECISION_REQUIRED')
    request = original_transport(path.parent.parent)['packet']['formal_request']
    checked = verify_original_decision(scientific_root(config, request), path,
        action=request['action'], subject=request['subject'], bindings=request['bindings'],
        source=config['source'], original_client=client)
    if checked['decision'] != 'APPLY':
        raise ValueError('INVESTIGATOR_FORMAL_DECISION_DEFERRED')
    return checked, request


def _operation(config, ref, client):
    """Fixed result readers retain the selecting model and actual authority proof."""
    from orchestrator import continuing_operations as ops
    from orchestrator.continuing_research import selection
    result = ops.read_operation_result(config, ref, kinds=OPERATION_KINDS)
    saved = ops._saved(ops._directory(config) / ref['operation'])
    selecting = _task(config, saved['selected_by']['task'], client, investigator=True)
    if selecting['disposition']['acceptance_status'] != 'APPROVED_PROPOSAL_ONLY':
        raise ValueError('INVESTIGATOR_OPERATION_SELECTION_NOT_ACCEPTED')
    from orchestrator.continuing_research import read_reference
    proposed = json.loads(read_reference(config, saved['selected_by']))
    desired = (proposed.get('successor') or {}).get('protocol')
    from orchestrator.continuing_research import observed_protocols
    protocols = observed_protocols(config, selecting['packet'], client=client, desired=desired) if desired else ()
    chosen = selection(selecting['packet']['campaign_task'], proposed, protocols=protocols)
    expected_operation = chosen['successor']
    if (chosen['status'] == 'PROPOSE' and saved['operation']['kind'] == 'ADOPT_FOLLOWUP'
            and chosen['successor'].get('schema') == 'prospective-research-task/v1'):
        from orchestrator.scientific_adoption import selected_operation
        expected_operation = selected_operation(config, chosen['successor'], selecting['packet'],
                                                saved['selected_by'], original_client=client)
    if chosen['status'] != 'PROPOSE' or expected_operation != saved['operation']:
        raise ValueError('INVESTIGATOR_OPERATION_DIFFERS_FROM_SELECTION')
    value = result['result']; kind = result['kind']
    inputs = saved['operation']['inputs']
    validation_evidence = None
    if kind == 'AUTHORIZE_PROTOCOL':
        proof, request = _formal(config, value['protocol']['decision_path'], client)
        from orchestrator.protocol_proposals import authorization_artifacts
        artifacts = {name: read_reference(config, ref).decode() for name, ref in inputs['artifacts'].items()}
        bundle = authorization_artifacts(inputs['protocol_id'], inputs['experiment'], inputs['artifacts'], artifacts)
        proposal = _task(config, bundle['task'], client)
        if proposal['disposition']['acceptance_status'] != 'APPROVED_PROPOSAL_ONLY':
            raise ValueError('INVESTIGATOR_PROTOCOL_PROPOSAL_NOT_ACCEPTED')
        prior = inputs['prior_protocol']
        previous = None if prior is None else ops.read_operation_result(config, prior,
            kinds=('AUTHORIZE_PROTOCOL',))['result']['protocol']['decision_sha256']
        expected = {'source':config['source'], 'experiment':inputs['experiment'],
            **{key:hashlib.sha256(raw.encode()).hexdigest() for key,raw in artifacts.items()},
            'prior_protocol_sha256':previous}
        if (request['action'] != 'authorize_protocol' or value['protocol']['bindings'] != request['bindings']
                or value['protocol']['subject'] != request['subject']
                or request['subject'] != inputs['protocol_id'] or request['bindings'] != expected
                or value['artifacts'] != inputs['artifacts']
                or request['evidence'] != {key+'.txt':raw for key,raw in artifacts.items()}
                or value['protocol']['decision_sha256'] != proof['_decision_sha256']):
            raise ValueError('INVESTIGATOR_PROTOCOL_RESULT_CHANGED')
    elif kind == 'MATERIALIZE_VERSION':
        from orchestrator.scientific_materialization import workspace
        from orchestrator.scientific_versions import verify_proposals
        artifact_root, core = workspace(config, value['scientific_version_sha256'])
        verify_proposals(core, original_client=client)
        protocol = ops.read_operation_result(config, inputs['protocol'], kinds=('AUTHORIZE_PROTOCOL',))['result']['protocol']
        if (value['workspace'] != str(artifact_root) or core['experiment'] != inputs['experiment']
                or core['version_id'] != inputs['version_id']
                or core['parent_version_sha256'] != inputs['parent_version_sha256']
                or {row['task'] for row in core['proposals']} != set(inputs['proposals'])
                or core['protocol_decision_sha256'] != protocol['decision_sha256']):
            raise ValueError('INVESTIGATOR_MATERIALIZATION_RESULT_CHANGED')
    elif kind == 'APPROVE_VERSION':
        from orchestrator.scientific_versions import verify_authority
        descriptor = value['attachment']['descriptor']
        material = ops.read_operation_result(config, inputs['materialization'], kinds=('MATERIALIZE_VERSION',))['result']
        artifact_root = Path(config['state'])/'scientific-versions'/descriptor['core_sha256']/'workspace'
        if value['attachment']['workspace'] != str(artifact_root):
            raise ValueError('INVESTIGATOR_FIXED_SCIENTIFIC_WORKSPACE_REQUIRED')
        version = verify_authority(artifact_root, descriptor, original_client=client)
        protocol = ops.read_operation_result(config, inputs['protocol'], kinds=('AUTHORIZE_PROTOCOL',))['result']['protocol']
        if (value['attachment']['status'] != 'SCIENTIFIC_VERSION_ELIGIBLE'
                or value['materialization'] != inputs['materialization']
                or descriptor['core_sha256'] != material['scientific_version_sha256']
                or version['protocol_decision_sha256'] != protocol['decision_sha256']):
            raise ValueError('INVESTIGATOR_VERSION_RESULT_CHANGED')
    elif kind == 'ADOPT_FOLLOWUP':
        from orchestrator.scientific_adoption import read_application
        prepared = json.loads(read(ops._directory(config)/ref['operation']/'prepared.json'))
        expected = read_application(config, inputs['acceptance'], inputs['selection'],
            prepared['formal_request'], value['decision_path'], original_client=client, by=saved['actor'])
        if type(value.get('duplicate')) is not bool or value != {**expected, 'duplicate': value['duplicate']}:
            raise ValueError('INVESTIGATOR_ADOPTION_ORIGINAL_CHANGED')
    elif kind == 'ACCEPT_RESULT':
        from orchestrator.scientific_acceptance import read_application
        prepared = json.loads(read(ops._directory(config)/ref['operation']/'prepared.json'))
        expected = read_application(config, inputs['interpretation'], prepared['formal_request'],
            value['decision_path'], original_client=client, by=saved['actor'])
        if type(value.get('duplicate')) is not bool or value != {**expected, 'duplicate': value['duplicate']}:
            raise ValueError('INVESTIGATOR_ACCEPTANCE_ORIGINAL_CHANGED')
    elif kind == 'VALIDATE_RESULT':
        from orchestrator.scientific_job_results import checked_semantic_result
        original = client('', 'scientific_job_result', {'completion': inputs['completion']})
        response = client('', 'scientific_validation_result', {'completion': inputs['completion']})
        checked = checked_semantic_result(response, original)
        expected = {'completion': inputs['completion'], 'original_import_sha256': hashlib.sha256(encoded(original)).hexdigest(),
            'response_sha256': checked['response_sha256'], 'output_sha256': checked['output_sha256'],
            'attempt': response['attempt'], 'outcome_sha256': response['outcome_sha256'],
            'binding': checked['output']['binding'], 'validator_status': checked['output']['status'],
            'scientific_acceptance': False, 'adoption': False, 'formal_decision_status': 'PENDING', 'model_calls': 0}
        if any(value.get(key) != item for key, item in expected.items()):
            raise ValueError('INVESTIGATOR_VALIDATION_ORIGINAL_CHANGED')
        validation_evidence = checked['output']
    else:
        original = client('', 'scientific_job_result', {'completion': value['completion']})
        if original != value['import'] or value['scientific_acceptance'] is not False or value['completion'] != inputs['completion']:
            raise ValueError('INVESTIGATOR_IMPORT_ORIGINAL_CHANGED')
    return {'event': event('OPERATION', ref['operation'], ref['result_sha256']),
            'operation': {'reference': ref, 'kind': kind, 'result': value,
                **({'semantic_validation': validation_evidence} if validation_evidence is not None else {})},
            'references': selecting['packet']['campaign_task']['references']}


def _disposition(config, identity, client):
    from orchestrator.disposition_successors import read_result
    value = read_result(config, pin(identity), client)
    from orchestrator.linked_disposition_input import for_template
    value = for_template(config, value)
    # The blocked task is evidence, never a completed task or artifact reference.
    refs = value['originals']['packet']['campaign_task']['references']
    if any(ref['task'] == identity for ref in refs):
        raise ValueError('LINKED_DISPOSITION_BLOCKED_TASK_REFERENCE_FORBIDDEN')
    return {'event': event('DISPOSITION', identity, value['result_sha256']),
            'linked_disposition': value, 'references': refs}


def _job(config, identity, client):
    original = client('', 'scientific_job_result', {'completion': pin(identity)})
    from orchestrator.scientific_job_results import validate_import
    validate_import(original, identity)
    observed = original['event']
    return {'event': event('JOB', identity, observed['result_manifest_sha256']),
            'completion': {**{key: observed[key] for key in ('event', 'job', 'attempt', 'source',
                'core_sha256', 'result_manifest_sha256', 'scientific_acceptance')},
                'outcome_status': observed['outcome']['status']}}


def verify_events(config, values, client):
    template = setting(config)
    if template is None or not isinstance(values, list) or not 1 <= len(values) <= MAX_EVENTS:
        raise ValueError('INVESTIGATOR_BOUNDED_EVENTS_REQUIRED')
    if any(value.get('kind') in ('ELIGIBILITY237_REPLACEMENT', 'ELIGIBILITY247_REPLACEMENT', 'ELIGIBILITY263_RECONSIDERATION') for value in values) and len(values) != 1:
        raise ValueError('ELIGIBILITY237_SINGLE_LOGICAL_EVENT_REQUIRED')
    if len({event_key(value) for value in values}) != len(values):
        raise ValueError('INVESTIGATOR_DUPLICATE_EVENT')
    from orchestrator.research_catalog import linked_change
    linked_change(config, {'change_request': template['template']['change_request']})
    checked = []
    for value in values:
        if value['kind'] == 'BOOTSTRAP':
            identity = digest({'source': config['source'], 'template_sha256': template['template_sha256']})
            item = {'event': event('BOOTSTRAP', identity, template['template_sha256'])}
        elif value['kind'] == 'TASK':
            item = _task(config, value['identity'], client)
        elif value['kind'] == 'FAILURE':
            item = _failure(config, value['identity'], client)
        elif value['kind'] == 'STEERING':
            item = _steering(config, value['identity'], client)
        elif value['kind'] == 'ELIGIBILITY237_REPLACEMENT':
            from orchestrator.investigator_eligibility_replacement import verify
            item = verify(config, value, client)
        elif value['kind'] == 'ELIGIBILITY263_RECONSIDERATION':
            from orchestrator.investigator_eligibility263_reconsideration import verify
            item = verify(config, value, client)
        elif value['kind'] == 'ELIGIBILITY247_REPLACEMENT':
            from orchestrator.investigator_eligibility247_replacement import verify
            item = verify(config, value, client)
        elif value['kind'] == 'DISPOSITION':
            item = _disposition(config, value['identity'], client)
        elif value['kind'] == 'OPERATION':
            item = _operation(config, {'operation': value['identity'], 'result_sha256': value['original_sha256']}, client)
        else:
            item = _job(config, value['identity'], client)
        if item['event'] != value:
            raise ValueError('INVESTIGATOR_EVENT_ORIGINAL_CHANGED')
        checked.append(item)
    return checked


def regenerate(config, manifest, client):
    """Exact deterministic task/evidence; no caller controls its request text."""
    installed = setting(config); template = installed['template']
    core = {key: value for key, value in manifest.items() if key != 'identity'}
    if (set(core) != {'schema', 'source', 'template_sha256', 'events', 'day'} or core['schema'] != WAKE
            or core['source'] != config['source'] or core['template_sha256'] != installed['template_sha256']
            or manifest['identity'] != digest(core)):
        raise ValueError('INVESTIGATOR_ROOT_WAKE_CHANGED')
    from datetime import date
    if date.fromisoformat(core['day']).isoformat() != core['day']:
        raise ValueError('INVESTIGATOR_WAKE_DAY_CHANGED')
    from orchestrator.handover_runtime import configuration, RESEARCH_EVIDENCE_MAXIMUM
    evidence = configuration(template['evidence_file'], maximum=RESEARCH_EVIDENCE_MAXIMUM,
                             expected_sha256=template['evidence_sha256'],
                             private_gid=config['controller_gid'])
    verified = verify_events(config, manifest['events'], client)
    candidates = [ref for item in verified for ref in item.get('references', [])] + template['references']
    # Carry the immediately preceding task's checked input references as well.
    candidates += [ref for item in verified if 'packet' in item
                   for ref in item['packet']['campaign_task'].get('references', [])]
    unique = list({digest(ref): ref for ref in candidates}.values())
    refs = unique[:16]
    predecessors = {}
    for ref in refs:
        item = _task(config, ref['task'], client)
        if ref not in item['references']:
            raise ValueError('INVESTIGATOR_REFERENCE_NOT_ORIGINAL_ARTIFACT')
        predecessors[ref['task']] = item['predecessor']
    for item in verified:
        if 'predecessor' in item:
            predecessors[item['predecessor']['task']] = item['predecessor']
    if len(predecessors) > 8:
        raise ValueError('INVESTIGATOR_PREDECESSOR_CONTEXT_BOUND')
    task = {'schema': SCHEMA, 'task_id': 'investigator-' + manifest['identity'],
        'experiment': template['experiment'], 'mode': 'investigate', 'request': template['request'],
        'references': refs, 'selected_by': None, 'template_sha256': installed['template_sha256'],
        'wake_sha256': manifest['identity'],
        'purpose':'FAILURE_DIAGNOSIS' if any(item['event']['kind'] == 'FAILURE' for item in verified) else 'CHARTER_SELECTION'}
    task_contract(task)
    projection = [{**{key:value for key,value in item.items() if key != 'packet'},
        **({'original_task':item['packet']['campaign_task'],
            'original_packet_sha256':hashlib.sha256(encoded(item['packet'])).hexdigest()}
           if 'packet' in item else {})} for item in verified]
    from orchestrator.disposition_context import encode_evidence
    original_evidence = {'installed_charter_evidence': evidence,
        'investigator_wake': manifest, 'verified_events': projection,
        'reference_projection': {'available': len(unique), 'supplied': len(refs), 'omitted': len(unique)-len(refs)},
        'request_origin': service(config), 'scientific_authority': 'Pending separate actual eligibility and investigator stages.'}
    return {'task': task, 'evidence': encode_evidence(original_evidence, config['source']),
        'predecessors': list(predecessors.values())}


def verify_entry(config, entry, client):
    task = entry['request']['task']; task_contract(task)
    # Raw and protected original clients share this fixed installed socket.
    bound_client = lambda socket, operation, body: client(config['broker_socket'], operation, body)
    response = bound_client('', 'read_investigator_wake', {'wake': task['wake_sha256']})
    if response.get('status') != 'RESERVED':
        raise ValueError('INVESTIGATOR_PROTECTED_EVENT_RESERVATION_REQUIRED')
    expected = regenerate(config, response['wake'], bound_client)
    from orchestrator.continuing_research import read_evidence
    if (task != expected['task'] or entry['predecessors'] != expected['predecessors']
            or read_evidence(config, entry['request']) != expected['evidence']
            or entry['request']['initiator'] != service(config)
            or entry['request']['day'] != response['wake']['day']
            or entry['change_request'] != setting(config)['template']['change_request']):
        raise ValueError('INVESTIGATOR_ENTRY_DIFFERS_FROM_ROOT_TEMPLATE_WAKE')
    return expected


def directory(config):
    return Path(config['state']) / 'investigator-wakes'


def _client(runtime):
    from orchestrator.handover_runtime import request_broker
    return lambda socket, operation, body: request_broker(runtime.config['broker_socket'], operation, body)


def _state(folder):
    manifest = json.loads(read(folder / 'wake.json'))
    if manifest['identity'] != folder.name:
        raise ValueError('INVESTIGATOR_WAKE_DIRECTORY_CHANGED')
    if (folder / 'submitted.json').exists():
        return {'wake': folder.name, 'status': 'SUBMITTED', 'submission': json.loads(read(folder / 'submitted.json'))}
    if (folder / 'authority.json').exists():
        value = json.loads(read(folder / 'authority.json'))
        if value.get('status') not in ('AGENT_REVIEWED_DECISION_READY', 'AGENT_REVIEWED_DEFERRAL'):
            raise ValueError('INVESTIGATOR_ORIGINAL_AUTHORITY_STATUS_REQUIRED')
        return {'wake': folder.name, 'status': 'REGISTRATION_PENDING' if value['status'] == 'AGENT_REVIEWED_DECISION_READY' else 'DEFERRED'}
    if (folder / 'authority-started.json').exists():
        return {'wake': folder.name, 'status': 'RECONCILIATION_REQUIRED',
                'reason': 'Inspect original authority replies; no automatic retry.'}
    return {'wake': folder.name, 'status': 'ELIGIBILITY_PENDING'}


def _rows(config):
    rows = []
    root = directory(config)
    if root.exists():
        for folder in sorted(root.iterdir()):
            if not folder.is_dir() and not folder.is_symlink(): continue
            try:
                row = _state(folder)
                if json.loads(read(folder/'wake.json'))['source'] != config['source']:
                    row = {**row, 'status':'HISTORICAL_READ_ONLY', 'original_status':row['status']}
                rows.append(row)
            except ERRORS:
                rows.append({'wake': folder.name, 'status': 'RECONCILIATION_REQUIRED',
                             'reason': 'Original wake record is incomplete or changed.'})
    return rows


def status(config):
    rows = _rows(config)
    path=directory(config)/'latest-observation.json'
    try: observation=json.loads(read(path)) if path.exists() else {'status':'NOT_OBSERVED','blocked':[]}
    except ERRORS: observation={'status':'RECONCILIATION_REQUIRED','blocked':[{'reason':'INVESTIGATOR_OBSERVATION_CHANGED'}]}
    return {'status': 'DISABLED' if setting(config) is None else 'SAVED_INVESTIGATOR_WORK' if rows else 'WAITING_FOR_NEW_EVIDENCE',
            'wakes': rows[-24:], 'wakes_total': len(rows), 'observation':observation, 'models': 0, 'admissions': 0}


def _pending(runtime):
    for row in _rows(runtime.config):
        if row['status'] in ('ELIGIBILITY_PENDING', 'REGISTRATION_PENDING'):
            return True
        if row['status'] == 'SUBMITTED':
            saved = runtime.q.db.execute('SELECT status FROM tasks WHERE id=?', (row['submission']['submission']['task'],)).fetchone()
            if saved is None or saved['status'] in ('QUEUED', 'RUNNING'):
                return True
    return False


def discover(runtime):
    if setting(runtime.config) is None: return {'status': 'DISABLED', 'models': 0}
    if os.getuid() != runtime.config['controller_uid']:
        raise ValueError('INVESTIGATOR_CONTROLLER_IDENTITY_REQUIRED')
    with lock(private_root(directory(runtime.config))/'.wake.lock'):
        result=_discover(runtime)
        from orchestrator.remote_supervisor import atomic
        blocked=result.get('blocked',[])
        atomic(directory(runtime.config)/'latest-observation.json',
            {**result,'blocked':blocked[:24],'blocked_total':len(blocked),
             'observed_at_utc':datetime.now(timezone.utc).isoformat()},mode=0o600)
        return result


def _discover(runtime):
    config = runtime.config; installed = setting(config)
    if installed is None: return {'status': 'DISABLED', 'models': 0}
    if os.getuid() != config['controller_uid']:
        raise ValueError('INVESTIGATOR_CONTROLLER_IDENTITY_REQUIRED')
    if runtime.q.status()['paused']: return {'status': 'PAUSED', 'models': 0}
    if _pending(runtime): return {'status': 'INVESTIGATOR_ALREADY_PENDING', 'models': 0}
    candidates = [event('BOOTSTRAP', digest({'source': config['source'],
        'template_sha256': installed['template_sha256']}), installed['template_sha256'])]
    if 'eligibility_replacement' in installed['template']:
        from orchestrator.investigator_eligibility_replacement import selected_candidate
        replacement = selected_candidate(config)
        # A failed or consumed247 exception must not fall through to a new-source
        # BOOTSTRAP and repeat the same science under a different event identity.
        if replacement['kind'] in ('ELIGIBILITY247_REPLACEMENT', 'ELIGIBILITY263_RECONSIDERATION'):
            candidates = []
        candidates.insert(0, replacement)
    blocked = []
    client = _client(runtime)
    for row in runtime.q.db.execute("SELECT id FROM tasks WHERE status='COMPLETE' ORDER BY rowid"):
        try:
            folder = Path(config['state']) / 'tasks' / row['id']
            packet = json.loads(read(folder/'packet.json'))
            if packet.get('campaign_task', {}).get('mode') in (None, 'investigate'): continue
            raw = read(folder/'scientific-disposition.json')
            candidates.append(event('TASK', row['id'], hashlib.sha256(raw).hexdigest()))
        except ERRORS: blocked.append({'task': row['id'], 'reason': 'ORIGINAL_TASK_REQUIRES_RECONCILIATION'})
    for row in runtime.q.db.execute("SELECT id FROM tasks WHERE status='BLOCKED' ORDER BY rowid"):
        try:
            packet=json.loads(read(Path(config['state'])/'tasks'/row['id']/'packet.json'))
            if packet.get('campaign_task',{}).get('mode') in (None,'investigate'): continue
            candidates.append(_failure(config,row['id'],client)['event'])
        except ERRORS: blocked.append({'task':row['id'],'reason':'ORIGINAL_ENDED_FAILURE_UNAVAILABLE_NO_RETRY'})
    from orchestrator import disposition_successors
    for row in disposition_successors.status(config)['successors']:
        if row['status'] == 'COMPLETE':
            candidates.append(event('DISPOSITION', row['origin_task'], row['result_sha256']))
    from orchestrator import continuing_operations
    for row in continuing_operations.status(config)['completed']:
        if row['kind'] in OPERATION_KINDS:
            candidates.append(event('OPERATION', row['reference']['operation'], row['reference']['result_sha256']))
    from orchestrator.protected_scientific_jobs import read_observation
    for row in read_observation(config)['events']:
        try: candidates.append(event('JOB', row['event'], row['result_manifest_sha256']))
        except ERRORS: blocked.append({'reason':'ORIGINAL_JOB_EVENT_REQUIRES_RECONCILIATION'})
    try:
        steering=client('','list_recorded_steering',{})
        if steering.get('status') != 'COMPLETE': raise ValueError('RECORDED_STEERING_ORIGINALS_REQUIRED')
        for row in steering['requests']:
            candidates.append(event('STEERING',row['request_id'],row['original_sha256']))
        blocked.extend(steering.get('blocked',[]))
    except ERRORS: blocked.append({'reason':'RECORDED_STEERING_REQUIRES_RECONCILIATION'})
    # One candidate per call isolates a changed historical original from other
    # useful evidence. The protected contract still tests per-event batch dedup.
    for candidate in candidates:
        try:
            reply = client('', 'reserve_investigator', {'events': [candidate]})
        except ERRORS:
            blocked.append({'event': event_key(candidate), 'reason':'ORIGINAL_EVENT_REQUIRES_RECONCILIATION'})
            if candidate['kind'] in ('ELIGIBILITY247_REPLACEMENT', 'ELIGIBILITY263_RECONSIDERATION'):
                return {'status': ('ELIGIBILITY263_GRANT_REQUIRES_RECONCILIATION' if candidate['kind'] == 'ELIGIBILITY263_RECONSIDERATION' else 'ELIGIBILITY247_GRANT_REQUIRES_RECONCILIATION'), 'models': 0, 'blocked': blocked}
            continue
        if reply.get('status') not in ('RESERVED', 'NO_NEW_EVENTS'):
            raise ValueError('INVESTIGATOR_PROTECTED_RESERVATION_REQUIRED')
        for identity in reply.get('existing_wakes', []):
            if not (directory(config)/pin(identity)).exists():
                original = client('', 'read_investigator_wake', {'wake': identity})
                immutable(private_root(directory(config)/identity)/'wake.json', encoded(original['wake']))
        if reply['status'] == 'RESERVED':
            manifest = reply['wake']; root = private_root(directory(config))
            immutable(private_root(root/pin(manifest['identity']))/'wake.json', encoded(manifest))
            return {'status': 'ELIGIBILITY_PENDING', 'wake': manifest['identity'], 'models': 0, 'blocked': blocked}
        if _pending(runtime): return {'status': 'ORIGINAL_RESERVATION_RECOVERED', 'models': 0}
        if candidate['kind'] in ('ELIGIBILITY247_REPLACEMENT', 'ELIGIBILITY263_RECONSIDERATION'):
            owners = reply.get('existing_wakes', [])
            if len(owners) != 1 or _state(directory(config)/pin(owners[0]))['status'] != 'SUBMITTED':
                return {'status': ('ELIGIBILITY263_RECONSIDERATION_CONSUMED_NO_RETRY' if candidate['kind'] == 'ELIGIBILITY263_RECONSIDERATION' else 'ELIGIBILITY247_REPLACEMENT_CONSUMED_NO_RETRY'), 'models': 0, 'blocked': blocked}
    return {'status': 'WAITING_FOR_NEW_EVIDENCE', 'models': 0, 'blocked': blocked}


def _entry(runtime, folder, manifest):
    from orchestrator.continuing_research import preserve_evidence
    config = runtime.config
    derived = regenerate(config, manifest, _client(runtime))
    evidence = preserve_evidence(config, derived['evidence'])
    return {'schema': 'installed-research-catalog-entry/v1', 'source': config['source'],
        'source_root': config['source_root'], 'request': {'task': derived['task'], **evidence,
            'day': manifest['day'], 'initiator': service(config)},
        'eligibility': {'path': str(folder/'authority/round-1/decision.json'), 'sha256': '0'*64},
        'predecessors': derived['predecessors'], 'change_request': setting(config)['template']['change_request']}


def advance(runtime):
    config = runtime.config
    if setting(config) is None: return {'status': 'DISABLED', 'models': 0}
    if os.getuid() != config['controller_uid']:
        raise ValueError('INVESTIGATOR_CONTROLLER_IDENTITY_REQUIRED')
    if runtime.q.status()['paused']: return {'status': 'PAUSED', 'models': 0}
    root = private_root(directory(config))
    with lock(root/'.wake.lock'):
        for row in _rows(config):
            if row['status'] not in ('ELIGIBILITY_PENDING', 'REGISTRATION_PENDING'): continue
            folder = root/row['wake']; manifest = json.loads(read(folder/'wake.json'))
            client = _client(runtime)
            if client('', 'read_investigator_wake', {'wake': row['wake']}).get('wake') != manifest:
                raise ValueError('INVESTIGATOR_RESERVED_ORIGINAL_CHANGED')
            if row['status'] == 'ELIGIBILITY_PENDING':
                entry = _entry(runtime, folder, manifest)
                immutable(folder/'entry.json', encoded(entry))
                immutable(folder/'authority-started.json', encoded({'entry_core_sha256': digest(entry),
                    'origin': service(config), 'status': 'ORIGINAL_ATTEMPT_REQUIRED'}))
                from orchestrator.research_task_authority import execute
                result = execute(config, entry, folder/'authority', client=client)
                immutable(folder/'authority.json', encoded(result))
                return {'status': 'ELIGIBILITY_RECORDED', 'wake': row['wake'], 'result': result}
            entry = json.loads(read(folder/'entry.json'))
            result = json.loads(read(folder/'authority.json'))
            entry['eligibility'] = result['eligibility']
            from orchestrator.continuing_research import register_and_submit
            submitted = register_and_submit(runtime, entry)
            immutable(folder/'submitted.json', encoded(submitted))
            return {'status': 'INVESTIGATOR_SUBMITTED', 'wake': row['wake'], 'submission': submitted, 'models': 0}
    return {'status': 'WAITING_FOR_NEW_EVIDENCE', 'models': 0}


def recover(runtime, identity):
    """Explicit original-only authority recovery; never restart a provider stage."""
    if os.getuid() != runtime.config['controller_uid']:
        raise ValueError('INVESTIGATOR_CONTROLLER_IDENTITY_REQUIRED')
    with lock(private_root(directory(runtime.config))/'.wake.lock'):
        return _recover(runtime,identity)


def _recover(runtime, identity):
    folder = directory(runtime.config)/pin(identity)
    if _state(folder)['status'] != 'RECONCILIATION_REQUIRED':
        raise ValueError('INVESTIGATOR_ORIGINAL_RECOVERY_NOT_REQUIRED')
    entry = json.loads(read(folder/'entry.json'))
    from orchestrator.research_task_authority import execute
    result = execute(runtime.config, entry, folder/'authority-recovery',
        recover_from=folder/'authority', client=_client(runtime))
    immutable(folder/'authority.json', encoded(result))
    return {'status': 'ORIGINAL_AUTHORITY_RECOVERED', 'wake': identity, 'models': 0}
