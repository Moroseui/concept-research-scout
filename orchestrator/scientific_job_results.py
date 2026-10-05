"""Preserve original completed-job aggregates for the formal interpretation stage.

Mechanical integrity and publication guards are not scientific validation. No
generated validator or scientific program is imported into this privileged path.
"""
import hashlib
import json
import os
from pathlib import Path

from orchestrator import linux_scientific_jobs as jobs
from orchestrator.hosted_cycle import encoded
from orchestrator.operations_report import private_root
from orchestrator.public_export import text
from orchestrator.remote_supervisor import lock
from orchestrator.scientific_materialization import immutable, _read

SCHEMA = 'prospective-scientific-result-import/v1'
STATUS = 'RESULT_BYTES_AVAILABLE_FOR_FORMAL_VALIDATION'


def context_files(core):
    prefix = 'campaigns/isles24-pilot/experiments/'+core['experiment']+'/'
    return {core['code'], core['spec'], core['settings'], core['requirements'],
            prefix+'validate_return.py', prefix+'publication.json'}


def export_result(registry, completion, *, original_client):
    """Internal root-broker operation; no request-supplied paths or proof callback."""
    if os.getuid() != 0: raise ValueError('SCIENTIFIC_RESULT_PROTECTED_BROKER_REQUIRED')
    jobs.pin(completion)
    row = registry.db.execute('SELECT * FROM events WHERE id=?', (completion,)).fetchone()
    if row is None: raise ValueError('SCIENTIFIC_ORIGINAL_COMPLETION_REQUIRED')
    event = json.loads(row['payload'])
    attempt = registry.db.execute('SELECT * FROM scientific_attempts WHERE id=?', (event['attempt'],)).fetchone()
    if attempt is None: raise ValueError('SCIENTIFIC_ORIGINAL_ATTEMPT_REQUIRED')
    request = json.loads(attempt['request']); binding = request['binding']; core = binding['core']
    config = binding['runtime_configuration']; folder = Path(config['outputs'])/request['attempt']
    outcome = json.loads(jobs.regular(folder/'outcome.json'))
    jobs.validate_outcome(request, folder, outcome)
    if (event['event'] != completion or jobs.digest(jobs.encoded(outcome)) != completion or
            event['job'] != attempt['job'] or event['job'] != core['job_id'] or
            event['execution_binding'] != core or event['outcome'] != outcome or
            event['core_sha256'] != jobs.digest(jobs.encoded(core)) or event['source'] != core['source'] or
            event['result_manifest_sha256'] != outcome['result_manifest_sha256'] or
            event['authority'] != binding['authority'] or event['scientific_acceptance'] is not False):
        raise ValueError('SCIENTIFIC_COMPLETION_BINDING_CHANGED')
    if outcome['status'] != 'COMPLETE':
        raise ValueError('SCIENTIFIC_FAILED_JOB_REQUIRES_DIAGNOSIS_NOT_RESULT_IMPORT')
    jobs.checked_capture(config, binding)
    current = jobs.verify_authority(config, core, binding['decision_path'], artifact_root=binding['artifact_root'],
        protocol_path=binding['protocol_path'], original_client=original_client)
    if current != binding['authority']: raise ValueError('SCIENTIFIC_ORIGINAL_EXECUTION_AUTHORITY_CHANGED')
    root = Path(binding['artifact_root']); name = 'campaigns/isles24-pilot/experiments/'+core['experiment']+'/publication.json'
    if name not in core['files'] or jobs.digest(jobs.regular(root/name)) != core['files'][name]:
        raise ValueError('SCIENTIFIC_EXECUTED_PUBLICATION_POLICY_CHANGED')
    policy = json.loads(jobs.regular(root/name)); bundle = folder/'artifacts/result'
    # Reuse the reviewed publication allowed/required policy against the already
    # checked streaming inventory. Do not call publication.validate here: its
    # unrestricted read_bytes would load a potentially large private result.
    manifest = json.loads(jobs.regular(folder/'result-manifest.json'))
    file_map = {name.removeprefix('result/'): info['sha256'] for name, info in manifest['files'].items() if name.startswith('result/')}
    if (policy.get('blocked') or not isinstance(policy.get('allowed'), list) or
            not isinstance(policy.get('required'), list)):
        raise ValueError('SCIENTIFIC_EXECUTED_PUBLICATION_POLICY_REQUIRED')
    allowed = set(policy['allowed']); required = set(policy['required'])
    for name in allowed: jobs.relative(name)
    if not required <= allowed or set(file_map)-allowed or required-set(file_map):
        raise ValueError('SCIENTIFIC_RESULT_PUBLICATION_FILE_SET_REQUIRED')
    if not file_map or len(file_map) > 32: raise ValueError('SCIENTIFIC_BOUNDED_AGGREGATE_SET_REQUIRED')
    aggregates = {}
    for name in file_map:
        if Path(name).suffix not in ('.json', '.csv', '.md', '.txt'):
            raise ValueError('SCIENTIFIC_TEXT_AGGREGATE_REQUIRED_PRIVATE_OUTPUT_PRESERVED')
        body = jobs.regular(bundle/name, 30000)
        if hashlib.sha256(body).hexdigest() != file_map[name]:
            raise ValueError('SCIENTIFIC_RESULT_CHANGED_DURING_IMPORT')
        aggregates[name] = text(body.decode(), limit=30000)
    if sum(len(raw.encode()) for raw in aggregates.values()) > 80000:
        raise ValueError('SCIENTIFIC_AGGREGATE_CONTEXT_BOUND')
    scientific_context = {}
    for name in sorted(context_files(core)):
        body = jobs.regular(root/name, 30000)
        if hashlib.sha256(body).hexdigest() != core['files'].get(name):
            raise ValueError('SCIENTIFIC_EXECUTED_INTERPRETATION_CONTEXT_CHANGED')
        scientific_context[name] = text(body.decode(), limit=30000)
    if sum(len(raw.encode()) for raw in scientific_context.values()) > 180000:
        raise ValueError('SCIENTIFIC_EXECUTED_CONTEXT_BOUND')
    # A second original inventory check covers concurrent alteration while the
    # permitted text was read. No files are moved, truncated or rewritten.
    jobs.validate_outcome(request, folder, outcome)
    return {'schema': SCHEMA, 'status': STATUS, 'completion': completion, 'event': event,
        'source': core['source'], 'experiment': core['experiment'],
        'request_sha256': jobs.digest(jobs.encoded(request)),
        'scientific_version': core['scientific_version'],
        'protocol_decision_sha256': core['protocol']['decision_sha256'],
        'result_manifest_sha256': outcome['result_manifest_sha256'],
        'aggregate_file_sha256': file_map, 'aggregates': aggregates, 'scientific_context': scientific_context,
        'validation_status': 'PENDING_FORMAL_SCIENTIFIC_VALIDATION',
        'scientific_acceptance': False, 'model_calls': 0, 'original_outputs_modified': False}


def validate_import(value, completion):
    jobs.pin(completion)
    if (value.get('schema') != SCHEMA or value.get('status') != STATUS or value.get('completion') != completion
            or value.get('scientific_acceptance') is not False or value.get('original_outputs_modified') is not False
            or value.get('model_calls') != 0 or value.get('validation_status') != 'PENDING_FORMAL_SCIENTIFIC_VALIDATION'
            or value.get('event', {}).get('event') != completion
            or value.get('source') != value.get('event', {}).get('source')
            or value.get('scientific_version') != value.get('event', {}).get('execution_binding', {}).get('scientific_version')
            or value.get('protocol_decision_sha256') != value.get('event', {}).get('execution_binding', {}).get('protocol', {}).get('decision_sha256')
            or not isinstance(value.get('aggregates'), dict) or not 1 <= len(value['aggregates']) <= 32
            or set(value['aggregates']) != set(value.get('aggregate_file_sha256', {}))):
        raise ValueError('SCIENTIFIC_ORIGINAL_RESULT_IMPORT_REQUIRED')
    for name, body in value['aggregates'].items():
        jobs.relative(name); text(body, limit=30000)
        if hashlib.sha256(body.encode()).hexdigest() != value['aggregate_file_sha256'][name]:
            raise ValueError('SCIENTIFIC_IMPORTED_AGGREGATE_CHANGED')
    if sum(len(body.encode()) for body in value['aggregates'].values()) > 80000:
        raise ValueError('SCIENTIFIC_AGGREGATE_CONTEXT_BOUND')
    core = value['event']['execution_binding']
    context = value.get('scientific_context')
    if not isinstance(context, dict) or set(context) != context_files(core):
        raise ValueError('SCIENTIFIC_EXECUTED_INTERPRETATION_CONTEXT_REQUIRED')
    for name, body in context.items():
        text(body, limit=30000)
        if hashlib.sha256(body.encode()).hexdigest() != core['files'].get(name):
            raise ValueError('SCIENTIFIC_EXECUTED_INTERPRETATION_CONTEXT_CHANGED')
    return value


def import_result(config, *, completion, original_client, by):
    """Same saved controller operation for agent and human; no new judgment."""
    from orchestrator.change_requests import actor
    actor(by); jobs.pin(completion)
    if os.getuid() != config['controller_uid'] or config['controller_uid'] <= 0:
        raise ValueError('SCIENTIFIC_RESULT_CONTROLLER_IDENTITY_REQUIRED')
    if not callable(original_client): raise ValueError('ORIGINAL_PROTECTED_RESULT_CLIENT_REQUIRED')
    reply = original_client(config['broker_socket'], 'scientific_job_result', {'completion': completion})
    value = validate_import(reply, completion)
    parent = private_root(Path(config['state'])/'scientific-results'); folder = parent/completion
    raw = encoded(value)
    with lock(parent/'.import.lock'):
        if folder.exists():
            if not (folder/'import.json').exists():
                raise ValueError('SCIENTIFIC_PARTIAL_RESULT_IMPORT_RECONCILIATION_REQUIRED')
            saved = json.loads(_read(folder/'import.json'))
            if _read(folder/'original-response.json') != raw or saved['original_response_sha256'] != hashlib.sha256(raw).hexdigest():
                raise ValueError('SCIENTIFIC_ORIGINAL_IMPORTED_RESULT_CHANGED')
            return {**saved, 'duplicate': True}
        private_root(folder)
        immutable(folder/'intent.json', encoded({'completion': completion, 'original_response_sha256': hashlib.sha256(raw).hexdigest()}))
        immutable(folder/'original-response.json', raw)
        receipt = {'schema': 'scientific-result-import-receipt/v1', 'status': STATUS,
            'completion': completion, 'source': value['source'], 'experiment': value['experiment'],
            'original_response_sha256': hashlib.sha256(raw).hexdigest(), 'import': value,
            'applied_by': by, 'scientific_acceptance': False, 'model_calls': 0,
            'interpretation_review_status': 'PENDING', 'original_outputs_modified': False}
        immutable(folder/'import.json', encoded(receipt))
        return {**receipt, 'duplicate': False}


SEMANTIC_OUTPUT_SCHEMA = 'scientific-semantic-validation-output/v1'
SEMANTIC_OUTPUT_MAX_BYTES = 30000
SEMANTIC_BINDING_FIELDS = frozenset({
    'completion', 'source', 'scientific_version', 'protocol_decision_sha256',
    'input_manifest_sha256', 'result_manifest_sha256', 'validator_sha256',
})


def semantic_validation_output(raw, expected_binding):
    """Check untrusted confined-validator evidence, never accept or adopt it.

    The caller must derive expected_binding from the authenticated executed
    completion and reviewed validator, not from this output. This pure parser
    neither executes code nor authenticates a caller's claimed provenance.
    A later formal reviewed decision is required even when status is VALID.
    """
    if type(raw) is not bytes or not 1 <= len(raw) <= SEMANTIC_OUTPUT_MAX_BYTES:
        raise ValueError('SEMANTIC_VALIDATION_OUTPUT_BYTE_BOUND')
    if type(expected_binding) is not dict or set(expected_binding) != SEMANTIC_BINDING_FIELDS:
        raise ValueError('SEMANTIC_VALIDATION_EXPECTED_BINDING_REQUIRED')
    for name, value in expected_binding.items():
        if type(value) is not str:
            raise ValueError('SEMANTIC_VALIDATION_EXPECTED_BINDING_REQUIRED')
        jobs.pin(value, 40 if name == 'source' else 64)

    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError('SEMANTIC_VALIDATION_DUPLICATE_KEY')
            result[key] = value
        return result

    def constant(value):
        raise ValueError('SEMANTIC_VALIDATION_NONFINITE_JSON')

    try:
        value = json.loads(raw.decode('utf-8'), object_pairs_hook=unique,
                           parse_constant=constant)
    except (UnicodeDecodeError, json.JSONDecodeError, RecursionError) as error:
        raise ValueError('SEMANTIC_VALIDATION_JSON_REQUIRED') from error
    if (type(value) is not dict or set(value) != {'schema', 'binding', 'status', 'reason', 'diagnostics'}
            or value['schema'] != SEMANTIC_OUTPUT_SCHEMA):
        raise ValueError('SEMANTIC_VALIDATION_CLOSED_SCHEMA_REQUIRED')
    binding = value['binding']
    if (type(binding) is not dict or set(binding) != SEMANTIC_BINDING_FIELDS
            or any(type(item) is not str for item in binding.values())
            or binding != expected_binding):
        raise ValueError('SEMANTIC_VALIDATION_EXECUTED_BINDING_CHANGED')
    if type(value['status']) is not str or value['status'] not in ('VALID', 'INVALID', 'DEFER'):
        raise ValueError('SEMANTIC_VALIDATION_STATUS_REQUIRED')
    reason = value['reason']
    if type(reason) is not str or not reason.strip():
        raise ValueError('SEMANTIC_VALIDATION_REASON_REQUIRED')
    text(reason, limit=2000)
    diagnostics = value['diagnostics']
    if type(diagnostics) is not list or len(diagnostics) > 32:
        raise ValueError('SEMANTIC_VALIDATION_DIAGNOSTIC_BOUND')
    for item in diagnostics:
        if (type(item) is not dict or set(item) != {'code', 'message'}
                or type(item['code']) is not str or not 1 <= len(item['code']) <= 64
                or any(char not in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_' for char in item['code'])
                or type(item['message']) is not str or not item['message'].strip()):
            raise ValueError('SEMANTIC_VALIDATION_DIAGNOSTIC_SCHEMA')
        text(item['message'], limit=1024)
    # Bind the literal response bytes, including whitespace, for exactly-once
    # receipt storage. VALID is only validator evidence, not scientific approval.
    return {'output': value, 'output_sha256': hashlib.sha256(raw).hexdigest(),
            'output_utf8_bytes': len(raw), 'scientific_acceptance': False,
            'adoption': False}


def semantic_validation_binding(imported):
    """Derive validator expectations from the already protected result import.

    This checks consistency, not origin authentication. The existing protected
    original-client/import path must supply imported; never use a validator's
    self-reported binding as the expected value. No generated code is imported.
    scientific_version binds the canonical complete descriptor (including its
    decision), not only its core SHA. This helper enables no execution or use.
    """
    if type(imported) is not dict or type(imported.get('completion')) is not str:
        raise ValueError('SEMANTIC_VALIDATION_ORIGINAL_IMPORT_REQUIRED')
    value = validate_import(imported, imported['completion'])
    core = value['event']['execution_binding']
    version = value['scientific_version']
    if (type(version) is not dict or set(version) != {
            'core_path', 'core_sha256', 'decision_path', 'decision_sha256'}):
        raise ValueError('SEMANTIC_VALIDATION_VERSION_DESCRIPTOR_REQUIRED')
    for key in ('core_path', 'decision_path'):
        jobs.relative(version[key])
    for key in ('core_sha256', 'decision_sha256'):
        jobs.pin(version[key])
    validator = 'campaigns/isles24-pilot/experiments/'+value['experiment']+'/validate_return.py'
    inputs = core.get('input_manifest')
    if (type(inputs) is not str or inputs not in core['files'] or
            core.get('protocol', {}).get('bindings', {}).get('input_manifest_sha256') != core['files'][inputs]):
        raise ValueError('SEMANTIC_VALIDATION_EXECUTED_INPUT_BINDING_REQUIRED')
    jobs.relative(inputs)
    outcome = value['event'].get('outcome', {})
    if (outcome.get('status') != 'COMPLETE' or outcome.get('scientific_acceptance') is not False
            or jobs.digest(jobs.encoded(outcome)) != value['completion']
            or outcome.get('result_manifest_sha256') != value['result_manifest_sha256']
            or value['event'].get('result_manifest_sha256') != value['result_manifest_sha256']):
        raise ValueError('SEMANTIC_VALIDATION_ORIGINAL_RETURN_BINDING_REQUIRED')
    binding = {'completion': value['completion'], 'source': value['source'],
        'scientific_version': hashlib.sha256(encoded(version)).hexdigest(),
        'protocol_decision_sha256': value['protocol_decision_sha256'],
        'input_manifest_sha256': core['files'][inputs],
        'result_manifest_sha256': value['result_manifest_sha256'],
        'validator_sha256': core['files'][validator]}
    for name, pin in binding.items():
        jobs.pin(pin, 40 if name == 'source' else 64)
    return binding


SEMANTIC_RESULT_SCHEMA = 'protected-semantic-validation-result/v1'
SEMANTIC_RESULT_MAX_BYTES = 80000


def checked_semantic_result(value, imported):
    """Validate a protected reader's return, not its origin or scientific merit.

    The protected validation reader must authenticate the completed
    confined execution before constructing this envelope. No caller may use
    a validator's self-reported binding as the expected executed identity.
    """
    keys = {'schema', 'execution_status', 'binding', 'attempt',
            'request_sha256', 'outcome_sha256', 'output',
            'scientific_acceptance', 'model_calls'}
    if (type(value) is not dict or set(value) != keys
            or value['schema'] != SEMANTIC_RESULT_SCHEMA
            or value['execution_status'] != 'COMPLETE'
            or value['scientific_acceptance'] is not False
            or type(value['model_calls']) is not int or value['model_calls'] != 0
            or type(value['output']) is not str):
        raise ValueError('SEMANTIC_VALIDATION_PROTECTED_RETURN_REQUIRED')
    for name in ('attempt', 'request_sha256', 'outcome_sha256'):
        jobs.pin(value[name])
    binding = semantic_validation_binding(imported)
    if value['binding'] != binding:
        raise ValueError('SEMANTIC_VALIDATION_EXECUTED_BINDING_CHANGED')
    raw = encoded(value)
    if len(raw) > SEMANTIC_RESULT_MAX_BYTES:
        raise ValueError('SEMANTIC_VALIDATION_RESPONSE_BYTE_BOUND')
    checked = semantic_validation_output(value['output'].encode('utf-8'), binding)
    return {'response_sha256': hashlib.sha256(raw).hexdigest(),
            'response_utf8_bytes': len(raw), **checked}


def import_semantic_validation(config, *, completion, original_client, by):
    """Save one original validator return for a later formal decision.

    Human and agent callers share this controller-owned boundary. It only reads
    protected originals; it cannot launch or retry validation. The protected
    scientific_validation_result operation authenticates the separate fixed-purpose
    worker attempt. The candidate still requires independent review before use. VALID, INVALID and DEFER all remain evidence only.
    """
    from orchestrator.change_requests import actor
    actor(by); jobs.pin(completion)
    # Authenticate the existing execution through the established import route;
    # do not trust a local file or the validator to supply the expected binding.
    imported = import_result(config, completion=completion,
                             original_client=original_client, by=by)
    value = original_client(config['broker_socket'], 'scientific_validation_result',
                            {'completion': completion})
    checked = checked_semantic_result(value, imported['import'])
    parent = private_root(Path(config['state'])/'scientific-results'/completion)
    folder = parent/'semantic-validation'
    raw = encoded(value); output = value['output'].encode('utf-8')
    with lock(parent/'.validation-import.lock'):
        def receipt(applied_by):
            return {'schema': 'semantic-validation-import-receipt/v1',
                'completion': completion,
                'original_import_sha256': imported['original_response_sha256'],
                'response_sha256': checked['response_sha256'],
                'output_sha256': checked['output_sha256'],
                'attempt': value['attempt'], 'outcome_sha256': value['outcome_sha256'],
                'binding': checked['output']['binding'],
                'validator_status': checked['output']['status'],
                'applied_by': applied_by, 'model_calls': 0,
                'scientific_acceptance': False, 'adoption': False,
                'formal_decision_status': 'PENDING'}
        if folder.exists():
            if not (folder/'import.json').exists():
                raise ValueError('SEMANTIC_VALIDATION_PARTIAL_IMPORT_RECONCILE_NO_RETRY')
            saved = json.loads(_read(folder/'import.json'))
            actor(saved.get('applied_by'))
            if (_read(folder/'original-response.json') != raw
                    or _read(folder/'validator-output.json') != output
                    or saved != receipt(saved['applied_by'])):
                raise ValueError('SEMANTIC_VALIDATION_IMPORTED_ORIGINAL_CHANGED')
            return {**saved, 'duplicate': True}
        private_root(folder)
        immutable(folder/'intent.json', encoded({
            'completion': completion, 'response_sha256': checked['response_sha256']}))
        immutable(folder/'original-response.json', raw)
        immutable(folder/'validator-output.json', output)
        result = receipt(by)
        immutable(folder/'import.json', encoded(result))
        return {**result, 'duplicate': False}
