"""Typed formal operations and immutable, independently reviewed successors.

This module supplies no scientific executor or alternative model runner. Proposal
construction uses campaign_pipeline; eligibility uses scientific_decision; the
protected receiver verifies original broker replies before installing an entry.
"""
import argparse
from copy import deepcopy
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import subprocess
import sys

from orchestrator.handover_coordinator import digest
from orchestrator.hosted_cycle import encoded
from orchestrator.public_export import text

TASK_SCHEMA = 'continuing-research-task/v1'
PROSPECTIVE_SCHEMA = 'prospective-research-task/v1'
SELECTION_SCHEMA = 'continuing-research-selection/v1'
MODES = frozenset(('charter', 'readiness', 'adoption', 'propose', 'specify',
                  'code', 'repair', 'discuss', 'brief', 'curate', 'interpret', 'investigate', 'code_bundle', 'protocol_proposal'))
EXPERIMENTS = frozenset(('P001', 'P002', 'P003'))
PROSPECTIVE_MODES = frozenset(('readiness', 'propose', 'specify', 'code_bundle', 'discuss',
                             'interpret', 'investigate'))


def reference(value):
    if (not isinstance(value, dict) or set(value) != {'task', 'artifact', 'sha256'}
            or not re.fullmatch('[0-9a-f]{64}', str(value['task']))
            or not re.fullmatch('[0-9a-f]{64}', str(value['sha256']))
            or not isinstance(value['artifact'], str)):
        raise ValueError('CONTINUING_ARTIFACT_REFERENCE_REQUIRED')
    path = Path(value['artifact'])
    if (path.is_absolute() or '..' in path.parts or str(path) != value['artifact']
            or not re.fullmatch(r'round-[12]/[A-Za-z0-9_.-]{1,120}', value['artifact'])):
        raise ValueError('CONTINUING_ARTIFACT_PATH_REQUIRED')
    return value


def task_contract(task):
    if isinstance(task, dict) and task.get('schema') == 'investigator-task/v1':
        from orchestrator.investigator_wakes import task_contract as investigator_contract
        return investigator_contract(task)
    if isinstance(task, dict) and task.get('schema') == 'protocol-proposal-task/v1':
        from orchestrator.protocol_proposals import task_contract as protocol_contract
        return protocol_contract(task)
    keys = {'schema', 'task_id', 'experiment', 'mode', 'request', 'references', 'selected_by'}
    prospective = isinstance(task, dict) and task.get('schema') == PROSPECTIVE_SCHEMA
    result = prospective and 'import_result' in task
    validation = prospective and 'semantic_validation' in task
    accepted = prospective and 'accepted_result' in task
    expected = keys | ({'protocol'} if prospective else set()) | ({'import_result'} if result else set()) | (
        {'semantic_validation'} if validation else set()) | ({'accepted_result'} if accepted else set())
    if (not isinstance(task, dict) or set(task) != expected
            or task['schema'] not in (TASK_SCHEMA, PROSPECTIVE_SCHEMA) or task['experiment'] not in EXPERIMENTS
            or task['mode'] not in MODES
            or not re.fullmatch('[a-z0-9][a-z0-9-]{0,79}', str(task['task_id']))
            or not isinstance(task['request'], str) or not task['request'].strip()
            or not isinstance(task['references'], list) or len(task['references']) > 16):
        raise ValueError('CONTINUING_FORMAL_TASK_REQUIRED')
    if prospective:
        if task['experiment'] not in ('P002', 'P003') or task['mode'] not in PROSPECTIVE_MODES:
            raise ValueError('PROSPECTIVE_OPERATION_SCOPE_REQUIRED')
        protocol_descriptor(task['protocol'])
        if task['protocol']['bindings'].get('experiment') != task['experiment']:
            raise ValueError('PROSPECTIVE_PROTOCOL_EXPERIMENT_CHANGED')
        if task['mode'] == 'interpret' and not result:
            raise ValueError('PROSPECTIVE_INTERPRETATION_IMPORT_REQUIRED')
        if result:
            from orchestrator.continuing_operations import operation_reference
            operation_reference(task['import_result'])
        if accepted:
            from orchestrator.continuing_operations import operation_reference
            operation_reference(task['accepted_result'])
            if task['mode'] not in ('readiness', 'propose', 'specify', 'code_bundle', 'discuss'):
                raise ValueError('ADOPTION_PROSPECTIVE_FOLLOWUP_SCOPE_REQUIRED')
        if validation:
            if not result or task['mode'] != 'interpret':
                raise ValueError('SEMANTIC_VALIDATION_REQUIRES_RESULT_INTERPRETATION')
            operation_reference(task['semantic_validation'])
    elif task['mode'] == 'code_bundle':
        raise ValueError('CODE_BUNDLE_REQUIRES_PROSPECTIVE_PROTOCOL')
    if task['mode'] == 'protocol_proposal':
        raise ValueError('PROTOCOL_PROPOSAL_TYPED_TASK_REQUIRED')
    text(task['request'], limit=8000)
    refs = [digest(reference(item)) for item in task['references']]
    if len(set(refs)) != len(refs):
        raise ValueError('CONTINUING_DUPLICATE_REFERENCE')
    if task['selected_by'] is not None:
        reference(task['selected_by'])
        if task['selected_by']['artifact'] != 'round-1/selection.json':
            raise ValueError('CONTINUING_SELECTION_REFERENCE_REQUIRED')
    return {'version': 2, 'experiment': task['experiment'], 'mode': task['mode'],
            'operation_sha256': digest(task)}


def protocol_descriptor(value):
    if (not isinstance(value, dict) or set(value) !=
            {'subject', 'bindings', 'decision_path', 'decision_sha256'}
            or not isinstance(value['subject'], str)
            or not re.fullmatch('[a-z0-9][a-z0-9-]{0,79}', value['subject'])
            or not isinstance(value['bindings'], dict)
            or not isinstance(value['decision_path'], str)
            or not Path(value['decision_path']).is_absolute()
            or '..' in Path(value['decision_path']).parts
            or not re.fullmatch('[0-9a-f]{64}', str(value['decision_sha256']))):
        raise ValueError('PROSPECTIVE_REVIEWED_PROTOCOL_REFERENCE_REQUIRED')
    return value


def artifact_contract(value):
    if (not isinstance(value, dict) or set(value) !=
            {'version', 'experiment', 'mode', 'operation_sha256'}
            or type(value['version']) is not int or value['version'] != 2
            or value['experiment'] not in EXPERIMENTS or value['mode'] not in MODES
            or not re.fullmatch('[0-9a-f]{64}', str(value['operation_sha256']))):
        raise ValueError('CONTINUING_FORMAL_ARTIFACT_CONTRACT')
    return value


def selection(task, value, *, protocols=()):
    """A reviewed selection is a proposal; it never supplies eligibility."""
    task_contract(task)
    if task['mode'] != 'investigate':
        raise ValueError('INVESTIGATOR_TASK_REQUIRED')
    if (not isinstance(value, dict) or set(value) !=
            {'schema', 'status', 'rationale', 'reconsideration', 'successor'}
            or value['schema'] != SELECTION_SCHEMA
            or value['status'] not in ('PROPOSE', 'DEFER')):
        raise ValueError('INVESTIGATOR_SELECTION_SCHEMA')
    for field in ('rationale', 'reconsideration'):
        if not isinstance(value[field], str) or not value[field].strip():
            raise ValueError('INVESTIGATOR_REASON_AND_RECONSIDERATION_REQUIRED')
        text(value[field], limit=8000)
    successor = value['successor']
    if value['status'] == 'DEFER':
        if successor is not None:
            raise ValueError('DEFERRED_SELECTION_CANNOT_DISPATCH')
        return value
    if task.get('purpose') == 'FAILURE_DIAGNOSIS' and (not isinstance(successor, dict)
            or successor.get('schema') != TASK_SCHEMA or successor.get('mode') != 'discuss'):
        raise ValueError('TRANSPORT_FAILURE_DISCUSSION_ONLY_NO_RETRY')
    if isinstance(successor, dict) and successor.get('schema') == 'continuing-operation/v1':
        from orchestrator.continuing_operations import validate_selection
        validate_selection(task, successor)
        return value
    task_contract(successor)
    if successor['mode'] == 'investigate':
        raise ValueError('MODEL_SELECTED_INVESTIGATOR_FORBIDDEN')
    if successor['selected_by'] is not None or successor['task_id'] == task['task_id']:
        raise ValueError('FRESH_SUCCESSOR_PROPOSAL_REQUIRED')
    available = {digest(item) for item in task['references']}
    if any(digest(item) not in available for item in successor['references']):
        raise ValueError('SUCCESSOR_REFERENCE_NOT_IN_INVESTIGATOR_CONTEXT')
    if (successor.get('schema') == PROSPECTIVE_SCHEMA and successor['protocol'] != task.get('protocol')
            and successor['protocol'] not in protocols):
        raise ValueError('SUCCESSOR_PROTOCOL_NOT_IN_INVESTIGATOR_CONTEXT')
    return value


def _read(path, maximum=1500000):
    path = Path(path).absolute()
    if any(p.is_symlink() for p in (path, *path.parents)):
        raise ValueError('CONTINUING_ORIGINAL_PATH_REQUIRED')
    info = path.stat()
    if not stat.S_ISREG(info.st_mode) or info.st_size > maximum:
        raise ValueError('CONTINUING_ORIGINAL_FILE_BOUND')
    raw = path.read_bytes()
    if len(raw) > maximum:
        raise ValueError('CONTINUING_ORIGINAL_FILE_BOUND')
    return raw


def read_reference(config, ref):
    """Read only a named scientific artifact in its saved disposition inventory.

    Fresh registration/submission also verifies the predecessor's original
    broker replies. This reader checks the immutable content projection again.
    """
    reference(ref)
    state = Path(config['state']).absolute()
    folder = state / 'tasks' / ref['task']
    disposition = json.loads(_read(folder / 'scientific-disposition.json'))
    if (disposition.get('task') != ref['task'] or disposition.get('status') != 'DISPOSITION_RECORDED'
            or disposition.get('artifact_sha256', {}).get(ref['artifact']) != ref['sha256']):
        raise ValueError('CONTINUING_ARTIFACT_DISPOSITION_BINDING')
    output = Path(disposition['campaign_output'])
    if (output.is_absolute() or '..' in output.parts
            or not (state / output).is_relative_to(folder)):
        raise ValueError('CONTINUING_ARTIFACT_OUTPUT_BOUNDARY')
    raw = _read(state / output / ref['artifact'], maximum=30000)
    if hashlib.sha256(raw).hexdigest() != ref['sha256']:
        raise ValueError('CONTINUING_ORIGINAL_ARTIFACT_CHANGED')
    text(raw.decode(), limit=30000)
    return raw


def read_protocol(config, task, *, original_client):
    from orchestrator import scientific_authority as authority
    from orchestrator.formal_decisions import original_transport, verify_original_decision
    from orchestrator.remote_supervisor import checked_source
    root = checked_source(config['source_root'], config['source'])
    protocol = protocol_descriptor(task['protocol'])
    path = Path(protocol['decision_path'])
    if not path.is_relative_to(Path(config['state']).absolute() / 'formal-decisions'):
        raise ValueError('PROSPECTIVE_PROTOCOL_OUTSIDE_RECORDED_STATE')
    if hashlib.sha256(authority.read(path)).hexdigest() != protocol['decision_sha256']:
        raise ValueError('PROSPECTIVE_PROTOCOL_DECISION_CHANGED')
    decision = verify_original_decision(root, path, action='authorize_protocol',
        subject=protocol['subject'], bindings=protocol['bindings'], original_client=original_client,
        expected_transition={'from': 'REVIEWED_PROTOCOL_PROPOSAL', 'to': 'PROTOCOL_ELIGIBLE'},
        source=config['source'])
    if decision['decision'] != 'APPLY':
        raise ValueError('PROSPECTIVE_PROTOCOL_NOT_ELIGIBLE')
    return {'descriptor': protocol, 'decision': decision,
            'original_request': original_transport(path.parent.parent)['packet']['formal_request']}


def require_code_inputs(config, task):
    """Code construction follows actual reviewed idea and specification artifacts."""
    if task['mode'] != 'code_bundle':
        return
    found = set()
    for ref in task['references']:
        expected = {'round-1/proposal.md': 'propose', 'round-1/SPEC.proposed.md': 'specify'}.get(ref['artifact'])
        if expected is None:
            continue
        folder = Path(config['state']) / 'tasks' / ref['task']
        disposition = json.loads(_read(folder / 'scientific-disposition.json'))
        packet = json.loads(_read(folder / 'packet.json'))
        if (disposition.get('review_verdict') != 'APPROVE'
                or disposition.get('acceptance_status') != 'APPROVED_PROPOSAL_ONLY'
                or packet.get('campaign_task', {}).get('mode') != expected
                or packet['campaign_task'].get('experiment') != task['experiment']):
            raise ValueError('CODE_BUNDLE_REVIEWED_PREDECESSOR_REQUIRED')
        if expected == 'specify' and (packet['campaign_task'].get('experiment') != task['experiment']
                or packet['campaign_task'].get('protocol') != task['protocol']):
            raise ValueError('CODE_BUNDLE_SPEC_PROTOCOL_CHANGED')
        read_reference(config, ref)
        found.add(expected)
    if found != {'propose', 'specify'}:
        raise ValueError('CODE_BUNDLE_REVIEWED_IDEA_AND_SPEC_REQUIRED')


def checked_result_import(task, imported):
    """Exact original result and protocol; pending validation is never acceptance."""
    from orchestrator.scientific_job_results import validate_import, STATUS
    if (not isinstance(imported, dict) or set(imported) != {'reference', 'receipt'}
            or imported['reference'] != task.get('import_result')):
        raise ValueError('PROSPECTIVE_IMPORT_REFERENCE_CHANGED')
    receipt = imported['receipt']
    if not isinstance(receipt, dict) or not isinstance(receipt.get('import'), dict):
        raise ValueError('PROSPECTIVE_ORIGINAL_IMPORT_BINDING_CHANGED')
    result = receipt['import']
    validate_import(result, receipt.get('completion'))
    if (receipt.get('schema') != 'scientific-result-import-receipt/v1' or receipt.get('status') != STATUS
            or receipt.get('scientific_acceptance') is not False or receipt.get('interpretation_review_status') != 'PENDING'
            or receipt.get('original_outputs_modified') is not False or receipt.get('model_calls') != 0
            or receipt.get('source') != result['source'] or receipt.get('experiment') != task['experiment']
            or result['experiment'] != task['experiment']
            or result['source'] != task['protocol']['bindings']['source']
            or result['protocol_decision_sha256'] != task['protocol']['decision_sha256']
            or result['result_manifest_sha256'] != result['event']['result_manifest_sha256']
            or hashlib.sha256(encoded(result)).hexdigest() != receipt.get('original_response_sha256')):
        raise ValueError('PROSPECTIVE_ORIGINAL_IMPORT_BINDING_CHANGED')
    return imported


def read_result_import(config, task, *, original_client, read_only=False):
    if type(read_only) is not bool:
        raise ValueError('PROSPECTIVE_IMPORT_RECOVERY_MODE_REQUIRED')
    from orchestrator.continuing_operations import read_operation_result
    operation = read_operation_result(config, task['import_result'], kinds=('IMPORT_RESULT',),
                                     current_review=not read_only)
    imported = checked_result_import(task, {'reference': task['import_result'], 'receipt': operation['result']})
    receipt = imported['receipt']; result = receipt['import']
    folder = Path(config['state'])/'scientific-results'/receipt['completion']
    if (_read(folder/'original-response.json') != encoded(result) or
            json.loads(_read(folder/'import.json')) != {k: v for k, v in receipt.items() if k != 'duplicate'}):
        raise ValueError('PROSPECTIVE_SAVED_IMPORT_ORIGINAL_CHANGED')
    reply = original_client(config['broker_socket'], 'scientific_job_result', {'completion': receipt['completion']})
    if reply != result:
        raise ValueError('PROSPECTIVE_PROTECTED_JOB_RESULT_CHANGED')
    return imported



def checked_validation_context(task, imported, value):
    """Authenticate the bounded semantic output against the same imported capture.

    The protected reader supplies execution authenticity; this deterministic
    verifier also runs on the exact copied context seen by both scientific roles.
    """
    from orchestrator.scientific_job_results import checked_semantic_result
    checked_result_import(task, imported)
    if (not isinstance(value, dict) or set(value) != {'reference', 'receipt', 'original'}
            or value['reference'] != task.get('semantic_validation')):
        raise ValueError('PROSPECTIVE_SEMANTIC_CONTEXT_REQUIRED')
    original = imported['receipt']['import']
    response = value['original']
    checked = checked_semantic_result(response, original)
    receipt = value['receipt']
    expected = {'schema': 'semantic-validation-import-receipt/v1',
        'completion': original['completion'],
        'original_import_sha256': hashlib.sha256(encoded(original)).hexdigest(),
        'response_sha256': checked['response_sha256'], 'output_sha256': checked['output_sha256'],
        'attempt': response['attempt'], 'outcome_sha256': response['outcome_sha256'],
        'binding': checked['output']['binding'], 'validator_status': checked['output']['status'],
        'model_calls': 0, 'scientific_acceptance': False, 'adoption': False,
        'formal_decision_status': 'PENDING'}
    from orchestrator.change_requests import actor
    if (not isinstance(receipt, dict)
            or set(receipt) not in (set(expected) | {'applied_by'}, set(expected) | {'applied_by', 'duplicate'})
            or encoded({k: receipt.get(k) for k in expected}) != encoded(expected)
            or 'duplicate' in receipt and type(receipt['duplicate']) is not bool):
        raise ValueError('PROSPECTIVE_SEMANTIC_IMPORT_CHANGED')
    actor(receipt['applied_by'])
    return value


def read_validation_context(config, task, imported, *, original_client, read_only=False):
    """Reuse the original job capture; retrieve only its separately bound validation."""
    if type(read_only) is not bool:
        raise ValueError('PROSPECTIVE_VALIDATION_RECOVERY_MODE_REQUIRED')
    from orchestrator.continuing_operations import read_operation_result
    operation = read_operation_result(config, task['semantic_validation'],
        kinds=('VALIDATE_RESULT',), current_review=not read_only)
    receipt = operation['result']
    completion = imported['receipt']['completion']
    response = original_client(config['broker_socket'], 'scientific_validation_result',
                               {'completion': completion})
    value = checked_validation_context(task, imported, {
        'reference': task['semantic_validation'], 'receipt': receipt, 'original': response})
    folder = Path(config['state'])/'scientific-results'/completion/'semantic-validation'
    if (_read(folder/'original-response.json') != encoded(response)
            or _read(folder/'validator-output.json') != response['output'].encode('utf-8')
            or json.loads(_read(folder/'import.json')) != {k: v for k, v in receipt.items() if k != 'duplicate'}):
        raise ValueError('PROSPECTIVE_SAVED_VALIDATION_CHANGED')
    return value


def observed_protocols(config, packet, *, client=None, desired=None, read_only=False, blocked=None):
    """Only exact completed protocol results supplied in the selecting packet."""
    from orchestrator.continuing_operations import read_operation_result
    if client is None:
        from orchestrator.handover_runtime import request_broker
        client = lambda socket, operation, body: request_broker(config['broker_socket'], operation, body)
    result = []
    from orchestrator.scientific_context_references import completed_rows, native_result
    for row in completed_rows(config, packet):
        if row.get('kind') != 'AUTHORIZE_PROTOCOL': continue
        descriptor = row.get('discovery', row.get('result', {})).get('protocol')
        if desired is not None and descriptor != desired: continue
        try:
            original = native_result(config, row, kinds=('AUTHORIZE_PROTOCOL',), current_review=not read_only)
            read_protocol(config, {'protocol': descriptor}, original_client=client)
        except (OSError,ValueError,KeyError,TypeError,AttributeError):
            if desired is not None or blocked is None: raise
            identity=row.get('reference',{}).get('operation')
            blocked.append({'operation':identity if re.fullmatch('[0-9a-f]{64}',str(identity)) else None,
                            'reason':'ORIGINAL_PROTOCOL_UNAVAILABLE_FOR_FRESH_SELECTION'})
            continue
        result.append(descriptor)
    return result


def supplemental_context(config, task, *, original_client=None, read_only=False, packet=None):
    if type(read_only) is not bool:
        raise ValueError('PROSPECTIVE_IMPORT_RECOVERY_MODE_REQUIRED')
    task_contract(task)
    values = [{'reference': ref, 'content': read_reference(config, ref).decode()}
              for ref in task['references']]
    value = {'task': task, 'references': values}
    if task['schema'] == 'investigator-task/v1':
        if not isinstance(packet, dict) or packet.get('campaign_task') != task:
            raise ValueError('INVESTIGATOR_ORIGINAL_PACKET_CONTEXT_REQUIRED')
        value['protocol_blocks']=[]
        value['eligible_protocols'] = observed_protocols(config, packet, client=original_client,
            read_only=read_only,blocked=value['protocol_blocks'])
    if task['schema'] == PROSPECTIVE_SCHEMA:
        if original_client is None:
            from orchestrator.handover_runtime import request_broker
            original_client = lambda socket, operation, body: request_broker(config['broker_socket'], operation, body)
        value['protocol'] = read_protocol(config, task, original_client=original_client)
        require_code_inputs(config, task)
        if 'import_result' in task:
            value['import_result'] = read_result_import(config, task, original_client=original_client, read_only=read_only)
        if 'semantic_validation' in task:
            value['semantic_validation'] = read_validation_context(config, task, value['import_result'],
                original_client=original_client, read_only=read_only)
    raw = json.dumps(value, sort_keys=True)
    text(raw, limit=500000)
    return {'continuing-research-inputs.json': raw}


def checked_supplement(task, context):
    """Bind the formal pipeline's copied context to the exact referenced bytes."""
    task_contract(task)
    if not isinstance(context, dict) or set(context) != {'continuing-research-inputs.json'}:
        raise ValueError('CONTINUING_CHECKED_CONTEXT_REQUIRED')
    raw = context['continuing-research-inputs.json']
    text(raw, limit=500000)
    value = json.loads(raw)
    prospective = task['schema'] == PROSPECTIVE_SCHEMA
    expected = ({'task', 'references', 'protocol'} if prospective else {'task', 'references'})
    if task['schema'] == 'investigator-task/v1': expected |= {'eligible_protocols','protocol_blocks'}
    if 'import_result' in task: expected |= {'import_result'}
    if 'semantic_validation' in task: expected |= {'semantic_validation'}
    if (not isinstance(value, dict) or set(value) != expected
            or value['task'] != task or not isinstance(value['references'], list)
            or len(value['references']) != len(task['references'])):
        raise ValueError('CONTINUING_INPUT_CONTEXT_CHANGED')
    if prospective and (value['protocol'].get('descriptor') != task['protocol']
            or value['protocol'].get('decision', {}).get('_decision_sha256') != task['protocol']['decision_sha256']
            or value['protocol'].get('decision', {}).get('decision') != 'APPLY'):
        raise ValueError('PROSPECTIVE_ORIGINAL_PROTOCOL_CONTEXT_REQUIRED')
    if 'import_result' in task:
        checked_result_import(task, value['import_result'])
    if 'semantic_validation' in task:
        checked_validation_context(task, value['import_result'], value['semantic_validation'])
    if 'eligible_protocols' in value:
        if not isinstance(value['eligible_protocols'], list):
            raise ValueError('INVESTIGATOR_PROTOCOL_CONTEXT_REQUIRED')
        for descriptor in value['eligible_protocols']: protocol_descriptor(descriptor)
        if not isinstance(value['protocol_blocks'],list) or any(not isinstance(row,dict)
                or set(row) != {'operation','reason'} or row['reason'] != 'ORIGINAL_PROTOCOL_UNAVAILABLE_FOR_FRESH_SELECTION'
                or row['operation'] is not None and not re.fullmatch('[0-9a-f]{64}',str(row['operation']))
                for row in value['protocol_blocks']):
            raise ValueError('INVESTIGATOR_PROTOCOL_BLOCK_CONTEXT_REQUIRED')
    for ref, item in zip(task['references'], value['references']):
        if (not isinstance(item, dict) or set(item) != {'reference', 'content'}
                or item['reference'] != ref or not isinstance(item['content'], str)
                or hashlib.sha256(item['content'].encode()).hexdigest() != ref['sha256']):
            raise ValueError('CONTINUING_INPUT_ARTIFACT_CHANGED')
    return context


def preserve_evidence(config, value):
    """Deterministic private intake; content is evidence, never an authority grant."""
    from orchestrator.operations_report import private_root
    from orchestrator.hosted_cycle import immutable
    if os.getuid() != config['controller_uid'] or not isinstance(value, dict):
        raise ValueError('CONTROLLER_EVIDENCE_INTAKE_REQUIRED')
    # Store the whole value without presentation whitespace; bind the actual bytes.
    raw = (json.dumps(value, sort_keys=True, separators=(',', ':'))+'\n').encode()
    text(raw.decode(), limit=750000)
    sha = hashlib.sha256(raw).hexdigest()
    folder = private_root(private_root(config['state']) / 'continuing-evidence')
    path = folder / (sha + '.json')
    immutable(path, raw)
    return {'evidence_file': str(path), 'evidence_sha256': sha}


def read_evidence(config, request):
    """New continuing inputs may live in the shared private, content-addressed store."""
    from orchestrator.handover_runtime import configuration
    path = Path(request['evidence_file']).absolute()
    folder = Path(config['state']).absolute() / 'continuing-evidence'
    expected = request['evidence_sha256']
    if path.parent != folder:
        return configuration(path, maximum=750000, expected_sha256=expected,
                             private_gid=config['controller_gid'])
    if path.name != expected + '.json':
        raise ValueError('CONTINUING_EVIDENCE_CONTENT_ADDRESS_REQUIRED')
    for item in (folder, path):
        info = item.stat()
        if info.st_uid != config['controller_uid'] or info.st_mode & 0o077:
            raise ValueError('CONTINUING_EVIDENCE_PRIVATE_OWNER_REQUIRED')
    raw = _read(path, maximum=750000)
    if hashlib.sha256(raw).hexdigest() != expected:
        raise ValueError('CONTINUING_EVIDENCE_CHANGED')
    value = json.loads(raw)
    if not isinstance(value, dict):
        raise ValueError('CONTINUING_EVIDENCE_OBJECT_REQUIRED')
    from orchestrator.git_publication import scan
    scan('continuing-evidence.json', raw)
    text(raw.decode(), limit=750000)
    return value


def investigator_instruction(task):
    """Exact schema instructions passed inside the existing scientific pipeline."""
    task_contract(task)
    if task.get('purpose') == 'FAILURE_DIAGNOSIS':
        return ('Inspect only the preserved ended transport failure and its unknown scientific outcome. '
            'Never retry the original task, assert scientific failure or success, or select a launch, '
            'protocol, implementation or investigator. Write selection.json with schema="'+SELECTION_SCHEMA+'", '
            'status="DEFER", rationale, reconsideration and successor=null; or status="PROPOSE" with one '
            'fresh successor having exactly schema="'+TASK_SCHEMA+'", task_id, experiment (P001/P002/P003), '
            'mode="discuss", request, references (a subset of the supplied exact references), selected_by=null. '
            'That discussion must diagnose the preserved transport evidence and propose a reasoned next step. '
            'It requires its own actual eligibility and independent review and grants no retry authority.')
    result = (
        'Choose one useful next formal operation for the current selected ISLES24 prediction charter, '
        'or record a reversible deferral. This is investigator/operator selection, not experimental '
        'approval, implementation, launch or interpretation acceptance. The successor goes through '
        'the existing scientific eligibility, independent review and immutable registration before '
        'admission. Use only the checked references in continuing-research-inputs.json. '
        'Preserve human stops, failed ideas, original source versions and prior criticism. '
        'Write selection.json with exactly schema="' + SELECTION_SCHEMA + '", status="PROPOSE" '
        'or "DEFER", rationale, reconsideration, and successor. DEFER requires successor=null. '
        'PROPOSE requires successor with exactly schema="' + TASK_SCHEMA + '", a fresh versioned '
        'task_id, experiment (P001/P002/P003), mode (' + ', '.join(sorted(MODES - {'investigate'})) + '), request, '
        'references (a subset of the supplied exact references) and selected_by=null. '
        'No command, runtime configuration, filesystem destination, credential or arbitrary stage '
        'can be selected. Scientific code remains a proposal until its applicable approval. '
        'Do not ask humans to decide ordinary delegated science. Explain the substantive next step '
        'and why it is useful; do not claim a completed successor merely by proposing it.'
    )
    if task['schema'] in (PROSPECTIVE_SCHEMA, 'investigator-task/v1'):
        result += (' For a prospective successor use schema="' + PROSPECTIVE_SCHEMA + '", preserve the exact '
            'supplied protocol descriptor, or an exact eligible protocol from the verified completed AUTHORIZE_PROTOCOL '
            'context, as an additional protocol field, and select only P002/P003 and '
            'these modes: ' + ', '.join(sorted(PROSPECTIVE_MODES - {'investigate'})) + '. Code_bundle requires the already '
            'reviewed idea and matching specification references; it produces a proposal, never a launch.')
        result += (' An interpret successor must also name import_result={operation,result_sha256} for one '
            'actually completed IMPORT_RESULT operation supplied in the saved continuing-operation context. '
            'Its original result protocol must equal the task protocol. Carry that exact import reference '
            'when proposing follow-up discussion or investigation of the same result. Result bytes remain '
            'pending formal scientific validation; process completion and interpretation review alone '
            'do not accept scientific claims. When a completed VALIDATE_RESULT operation for this same '
            'completion is supplied, an interpret successor may additionally bind '
            'semantic_validation={operation,result_sha256}. Both interpretation roles then receive its '
            'authenticated bounded output, including INVALID/DEFER reasons; this is not acceptance or adoption.')
    result += (' Before a prospective protocol exists, a successor may use schema="protocol-proposal-task/v1", '
        'the same task_id/experiment/request/references/selected_by fields, mode="protocol_proposal", '
        'and experiment P002 or P003. It constructs a methodology and evidence proposal only, grants no '
        'input access or execution, and must preserve DEFERRED when required original evidence is missing.')
    from orchestrator.continuing_operations import instructions
    return result + ' ' + instructions()


def selected_successor(config, investigator_task, *, client=None):
    """Read an actually reviewed saved selection, without constructing science."""
    folder = Path(config['state']) / 'tasks' / investigator_task
    packet = json.loads(_read(folder / 'packet.json'))
    task = packet.get('campaign_task')
    task_contract(task)
    disposition = json.loads(_read(folder / 'scientific-disposition.json'))
    if (disposition.get('task') != investigator_task
            or disposition.get('review_verdict') != 'APPROVE'
            or disposition.get('acceptance_status') != 'APPROVED_PROPOSAL_ONLY'):
        raise ValueError('INVESTIGATOR_OPPOSING_REVIEW_REQUIRED')
    ref = {'task': investigator_task, 'artifact': 'round-1/selection.json',
           'sha256': disposition.get('artifact_sha256', {}).get('round-1/selection.json')}
    proposed = json.loads(read_reference(config, ref))
    desired = (proposed.get('successor') or {}).get('protocol')
    value = selection(task, proposed, protocols=observed_protocols(config, packet, client=client, desired=desired) if desired else ())
    if value['status'] == 'DEFER':
        return {'status': 'DEFERRED', 'selection': value, 'task': None}
    successor = deepcopy(value['successor'])
    if successor.get('schema') == 'continuing-operation/v1':
        return {'status':'PROPOSED_OPERATION_PENDING_AUTHORITY', 'selection':value, 'task':None, 'operation':successor}
    successor['selected_by'] = ref
    return {'status': 'PROPOSED_PENDING_ELIGIBILITY', 'selection': value, 'task': successor}


def validate_registration(config, entry, *, client):
    """Fixed validator used under the controller identity by the protected entry.

    client is only an internal test/transport seam. protected_register supplies
    checked original replies fetched directly from the actual protected broker.
    """
    from orchestrator import handover_runtime as runtime_module
    from orchestrator.research_catalog import validate_entry, linked_change
    from orchestrator.research_task_authority import verify_eligibility
    task = entry['request']['task']
    task_contract(task)
    validate_entry(entry, task['task_id'])
    if (entry['source'] != config['source'] or
            Path(entry['source_root']).absolute() != Path(config['source_root']).absolute()):
        raise ValueError('CURRENT_SUCCESSOR_SOURCE_REQUIRED')
    if task['schema'] == 'investigator-task/v1':
        from orchestrator.investigator_wakes import verify_entry
        verify_entry(config, entry, client)
    else:
        if task['mode'] == 'investigate':
            raise ValueError('MODEL_SELECTED_INVESTIGATOR_FORBIDDEN')
        if task['selected_by'] is None:
            raise ValueError('ACTUAL_REVIEWED_INVESTIGATOR_SELECTION_REQUIRED')
        selected = selected_successor(config, task['selected_by']['task'], client=client)
        if selected['task'] != task:
            raise ValueError('SUCCESSOR_DIFFERS_FROM_ORIGINAL_REVIEWED_SELECTION')
        from orchestrator.scientific_adoption import require_registration
        require_registration(config, entry, original_client=client)
        predecessors = {row['task']: row for row in entry['predecessors']}
        required = {ref['task'] for ref in task['references']} | {task['selected_by']['task']}
        if not required <= set(predecessors):
            raise ValueError('SUCCESSOR_REFERENCES_REQUIRE_EXACT_PREDECESSORS')
        if predecessors[task['selected_by']['task']]['requires'] != 'APPROVED_PROPOSAL_ONLY':
            raise ValueError('SUCCESSOR_SELECTION_REQUIRES_ACCEPTED_PREDECESSOR')
    # Fixed implementation seam; do not accept a Runtime or verifier from input.
    original_client = runtime_module.request_broker
    try:
        runtime_module.request_broker = client
        runtime = runtime_module.Runtime(config)
        runtime.research_predecessors(entry)
    finally:
        runtime_module.request_broker = original_client
    linked_change(config, entry)
    eligibility = verify_eligibility(config, entry, client=client)
    if eligibility['status'] != 'ELIGIBLE' or eligibility['review_status'] != 'APPROVE':
        raise ValueError('SUCCESSOR_ACTUAL_ELIGIBILITY_REQUIRED')
    read_evidence(config, entry['request'])
    if task['schema'] != 'investigator-task/v1':
        supplemental_context(config, task, original_client=client)
    return {'status': 'VERIFIED_SUCCESSOR', 'entry_sha256': digest(entry),
            'eligibility': eligibility, 'selection': task['selected_by'],
            'model_calls': 0, 'admissions': 0}


def _original_key(event, stage):
    return digest({'event': event, 'stage': stage})


def _validate_originals_input(value):
    """Fixed subprocess route: only original read-only replies, never model calls."""
    required = {'config', 'entry', 'originals'}
    if not required <= set(value) or set(value) - required - {'result_originals', 'validation_originals'}:
        raise ValueError('PROTECTED_SUCCESSOR_VERIFIER_INPUT')
    def original_client(socket, operation, body):
        if operation == 'scientific_job_result' and set(body) == {'completion'}:
            if body['completion'] not in value.get('result_originals', {}):
                raise ValueError('REGISTRATION_ORIGINAL_RESULT_UNAVAILABLE')
            return value['result_originals'][body['completion']]
        if operation == 'scientific_validation_result' and set(body) == {'completion'}:
            if body['completion'] not in value.get('validation_originals', {}):
                raise ValueError('REGISTRATION_ORIGINAL_VALIDATION_UNAVAILABLE')
            return value['validation_originals'][body['completion']]
        if operation != 'stage_status':
            raise ValueError('REGISTRATION_FORBIDS_NEW_MODEL_OPERATIONS')
        key = _original_key(body['event'], body['stage'])
        if key not in value['originals']:
            raise ValueError('REGISTRATION_ORIGINAL_REPLY_UNAVAILABLE')
        return value['originals'][key]
    return validate_registration(value['config'], value['entry'], client=original_client)


def protected_register(broker, body):
    """Root broker entry: fixed config, fixed validator, original replies, one file.

    No model, shell, arbitrary caller validator, source change, submission or
    activation occurs. A root-protected controller configuration is required.
    """
    from orchestrator.handover_runtime import configuration
    from orchestrator.research_catalog import paths, validate_entry
    if os.getuid() != 0 or not isinstance(body, dict) or set(body) != {'entry'}:
        raise ValueError('PROTECTED_SUCCESSOR_REGISTRATION_REQUIRED')
    config_path = broker.config.get('research_controller_config')
    if not isinstance(config_path, str) or not Path(config_path).is_absolute():
        raise ValueError('PROTECTED_RESEARCH_CONTROLLER_CONFIG_REQUIRED')
    config = configuration(config_path)
    if (config['controller_uid'] != broker.config['controller_uid']
            or config['source'] not in broker.config['sources']
            or config['controller_uid'] <= 0):
        raise ValueError('PROTECTED_SUCCESSOR_CONTROLLER_SOURCE')
    entry = body['entry']
    validate_entry(entry, entry['request']['task']['task_id'])
    task_contract(entry['request']['task'])
    directory = Path(config['research_catalog']['directory'])
    paths(config)  # Existing root-owned catalog and path/mode checks.
    if (entry['request']['task'].get('schema') == 'investigator-task/v1'
            or 'accepted_result' in entry['request']['task']):
        from orchestrator.protected_investigator import verify_subprocess
        receipt = verify_subprocess(broker, config, 'entry', entry)
        if receipt.get('status') != 'VERIFIED_SUCCESSOR' or receipt.get('entry_sha256') != digest(entry):
            raise ValueError('SUCCESSOR_PROTECTED_VALIDATION_BINDING')
        return _install_entry(config, entry, receipt)
    # Originals come from the protected broker, not the requesting controller.
    decision = Path(entry['eligibility']['path']).absolute()
    if not decision.is_relative_to(Path(config['state']).absolute()):
        raise ValueError('SUCCESSOR_DECISION_OUTSIDE_CONTROLLER_STATE')
    transport = json.loads(_read(decision.parent.parent / 'authority-transport.json'))
    events = [(transport['event'], ('continuation', 'review'))]
    for prior in entry['predecessors']:
        events.append(({'turn_id': prior['task'], 'attempt': '1', 'source': prior['source'],
                       'branch': 'astra/infrastructure-milestone-record', 'kind': 'astra_turn'},
                       ('continuation', 'review', 'disposition')))
    task = entry['request']['task']
    if task['schema'] == PROSPECTIVE_SCHEMA:
        protocol_path = Path(task['protocol']['decision_path'])
        if not protocol_path.is_relative_to(Path(config['state']).absolute() / 'formal-decisions'):
            raise ValueError('PROSPECTIVE_PROTOCOL_OUTSIDE_RECORDED_STATE')
        original = json.loads(_read(protocol_path.parent.parent / 'authority-transport.json'))
        events.append((original['event'], ('continuation', 'review')))
    originals = {}
    for event, stages in events:
        for stage in stages:
            originals[_original_key(event, stage)] = broker.stage_status({'event': event, 'stage': stage})
    result_originals = {}; validation_originals = {}
    if 'import_result' in task:
        # Root reads only the named immutable operation bytes to locate its
        # completion; the controller child verifies the full operation/review.
        # Result authority comes from the actual protected job, not these local
        # metadata bytes or a caller-supplied approval assertion.
        ref = task['import_result']
        operation_path = Path(config['state'])/'continuing-operations'/ref['operation']/'result.json'
        raw = _read(operation_path)
        if hashlib.sha256(raw).hexdigest() != ref['result_sha256']:
            raise ValueError('REGISTRATION_IMPORT_OPERATION_CHANGED')
        result = json.loads(raw)['result']; completion = result['completion']
        if not re.fullmatch('[0-9a-f]{64}', str(completion)):
            raise ValueError('REGISTRATION_IMPORT_COMPLETION_REQUIRED')
        from orchestrator.protected_scientific_jobs import handle as job_operation
        result_originals[completion] = job_operation(broker, 'scientific_job_result', {'completion': completion})
        if 'semantic_validation' in task:
            validation_originals[completion] = job_operation(broker, 'scientific_validation_result', {'completion': completion})
    # The source code is the installed, checked broker source. Drop both IDs and
    # supplementary groups before any controller-private reads or DB handling.
    from orchestrator.remote_supervisor import checked_source
    root = checked_source(config['source_root'], config['source'])
    def controller_identity():
        os.setgroups([])
        os.setgid(config['controller_gid'])
        os.setuid(config['controller_uid'])
    payload = encoded({'config': config, 'entry': entry, 'originals': originals,
                       **({'result_originals': result_originals} if result_originals else {}),
                       **({'validation_originals': validation_originals} if validation_originals else {})})
    if len(payload) > 6000000:
        raise ValueError('SUCCESSOR_VERIFICATION_INPUT_BOUND')
    result = subprocess.run([sys.executable, '-B', '-m', 'orchestrator.continuing_research',
                             '--verify-originals'], input=payload, cwd=root,
        env={'PATH': '/usr/bin:/bin', 'PYTHONPATH': str(root), 'PYTHONDONTWRITEBYTECODE': '1',
             'GIT_NO_LAZY_FETCH': '1'}, capture_output=True, timeout=60, preexec_fn=controller_identity)
    if result.returncode or len(result.stdout) > 20000:
        raise ValueError('SUCCESSOR_PROTECTED_VALIDATION_FAILED')
    receipt = json.loads(result.stdout)
    if receipt.get('status') != 'VERIFIED_SUCCESSOR' or receipt.get('entry_sha256') != digest(entry):
        raise ValueError('SUCCESSOR_PROTECTED_VALIDATION_BINDING')
    return _install_entry(config, entry, receipt)


def _install_entry(config, entry, receipt):
    directory = Path(config['research_catalog']['directory'])
    if os.getuid() != 0:
        raise ValueError('PROTECTED_SUCCESSOR_INSTALL_REQUIRED')
    # A single protected socket driver serializes requests. This additional lock
    # makes repeated administrative entry safe without resetting any evidence.
    gate_path = directory.parent / (directory.name + '-registration.lock')
    if directory.parent.stat().st_uid != 0 or directory.parent.stat().st_mode & 0o022:
        raise ValueError('PROTECTED_CATALOG_PARENT_REQUIRED')
    if gate_path.is_symlink():
        raise ValueError('PROTECTED_CATALOG_LOCK_REQUIRED')
    with gate_path.open('a') as gate:
        os.chmod(gate_path, 0o600)
        fcntl.flock(gate, fcntl.LOCK_EX)
        target = directory / (entry['request']['task']['task_id'] + '.json')
        raw = encoded(entry)
        if target.exists():
            if _read(target) != raw:
                raise ValueError('IMMUTABLE_SUCCESSOR_IDENTITY_CONFLICT')
            return {**receipt, 'status': 'REGISTERED', 'duplicate': True,
                    'catalog_file_sha256': hashlib.sha256(raw).hexdigest()}
        # Exclusive durable creation preserves partial failures for inspection;
        # an interrupted/changed entry is never overwritten or silently retried.
        fd = os.open(target, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o640)
        with os.fdopen(fd, 'wb') as stream:
            os.fchown(stream.fileno(), 0, config['controller_gid'])
            os.fchmod(stream.fileno(), 0o640)
            stream.write(raw); stream.flush(); os.fsync(stream.fileno())
        fd = os.open(directory, os.O_RDONLY | os.O_DIRECTORY)
        try:
            os.fsync(fd)
        finally:
            os.close(fd)
    return {**receipt, 'status': 'REGISTERED', 'duplicate': False,
            'catalog_file_sha256': hashlib.sha256(raw).hexdigest()}


def register_and_submit(runtime, entry):
    """Use one human/agent path: verify, protected registration, saved submission.

    Admission occurs later through the normal paused/quota-controlled scheduler.
    The submitted actor is the actual saved scientific decision actor, never a
    fabricated investigator identity or an uncounted model call.
    """
    from orchestrator.handover_runtime import request_broker
    checked = validate_registration(runtime.config, entry, client=request_broker)
    registered = request_broker(runtime.config['broker_socket'], 'register_research', {'entry': entry})
    if registered.get('status') != 'REGISTERED' or registered.get('entry_sha256') != digest(entry):
        raise ValueError('SUCCESSOR_REGISTRATION_RECEIPT_REQUIRED')
    queued = runtime.submit_research(entry['request']['task']['task_id'],
                                    submitted_by=checked['eligibility']['actor'])
    return {'registration': registered, 'submission': queued, 'new_model_calls': 0}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--verify-originals', action='store_true', required=True)
    parser.parse_args()
    raw = sys.stdin.buffer.read(6000001)
    if len(raw) > 6000000:
        raise ValueError('SUCCESSOR_VERIFICATION_INPUT_BOUND')
    print(json.dumps(_validate_originals_input(json.loads(raw)), sort_keys=True))


if __name__ == '__main__':
    main()
