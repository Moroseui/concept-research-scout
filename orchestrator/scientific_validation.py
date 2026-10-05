"""Fixed validator execution over a preserved scientific completion.

Reuse the scientific registry, worker and protected result importer. Generated
validator code runs only in the existing unprivileged worker, never in this
broker module. A valid validator output is evidence, not scientific acceptance.
"""
from copy import deepcopy
import json
import os
from pathlib import Path

from orchestrator import linux_scientific_jobs as jobs
from orchestrator import scientific_job_results as results
from orchestrator.hosted_cycle import encoded

ATTEMPT = 'linux-scientific-validation-attempt/v1'
MARKER = 'scientific-validation-execution-binding/v1'
INTERFACE = {
    'schema': 'scientific-semantic-validator-interface/v1',
    'arguments': ['--result-dir', '@result', '--data-root', '@input',
                  '--settings', '@settings', '--binding', '@binding', '--output', '@output'],
    'output_schema': results.SEMANTIC_OUTPUT_SCHEMA,
    'output_maximum_bytes': results.SEMANTIC_OUTPUT_MAX_BYTES,
}
OUTPUT = 'semantic-validation.json'


def author_instruction():
    return ('For the prospective Linux validation path, publication.proposed.json must include '
        'semantic_validation_interface with exactly this JSON: ' + json.dumps(INTERFACE, sort_keys=True) +
        '. In addition to the existing verify function, validate_return.proposed.py must implement '
        'that fixed CLI. The binding input is a root-preserved JSON object with exactly these fields: ' +
        ', '.join(sorted(results.SEMANTIC_BINDING_FIELDS)) + '. Preserve that object unchanged in output.binding; '
        'it identifies the actual prior execution, not a validator-generated identity. Write one JSON object '
        'with exactly schema=' + results.SEMANTIC_OUTPUT_SCHEMA + ', binding, status, reason, diagnostics. '
        'Status is VALID, INVALID or DEFER; reason is nonempty and at most 2000 characters; diagnostics is '
        'at most 32 objects with exactly code (1-64 uppercase ASCII letters/digits/underscore) and message '
        '(nonempty, at most 1024 characters). Entire output is at most 30000 UTF8 bytes. '
        'Derive status from the reviewed semantic requirements, not just file presence or exit zero. '
        'Keep diagnostics aggregate/nonpatient; unresolved evidence is DEFER, not invented validation. '
        'Do not modify the original result or input. No validator output grants acceptance, adoption or launch.')


def job_id(completion):
    jobs.pin(completion)
    # The store rejects a different complete binding even on a prefix collision.
    return 'validate-' + completion[:54]


def interface(binding):
    core = binding['core']
    prefix = 'campaigns/isles24-pilot/experiments/' + core['experiment'] + '/'
    root = Path(binding['artifact_root'])
    for name in ('publication.json', 'validate_return.py'):
        relative = prefix + name
        if (relative not in core['files']
                or jobs.file_digest(root / relative) != core['files'][relative]):
            raise ValueError('SEMANTIC_VALIDATION_REVIEWED_INTERFACE_REQUIRED')
    policy = json.loads(jobs.regular(root / (prefix + 'publication.json')))
    if jobs.encoded(policy.get('semantic_validation_interface')) != jobs.encoded(INTERFACE):
        raise ValueError('SEMANTIC_VALIDATION_REVIEWED_INTERFACE_REQUIRED')
    return prefix + 'validate_return.py'


def execution_binding(registry, completion, *, original_client):
    """Authenticate the old execution and derive a new fixed-purpose binding."""
    imported = results.export_result(registry, completion, original_client=original_client)
    return _binding_from_original(registry, imported)


def _binding_from_original(registry, imported):
    completion = imported['completion']
    row = registry.db.execute('SELECT request FROM scientific_attempts WHERE id=?',
                             (imported['event']['attempt'],)).fetchone()
    request = json.loads(row['request'])
    if request.get('schema') != 'linux-scientific-attempt/v1':
        raise ValueError('SEMANTIC_VALIDATION_ORIGINAL_EXPERIMENT_REQUIRED')
    binding = deepcopy(request['binding'])
    if 'semantic_validation' in binding or binding['runtime_configuration'] != registry.config:
        raise ValueError('SEMANTIC_VALIDATION_REGISTERED_CONFIGURATION_CHANGED')
    interface(binding)
    binding['semantic_validation'] = {
        'schema': MARKER, 'completion': completion, 'original_attempt': request['attempt'],
        'original_request_sha256': jobs.digest(jobs.encoded(request)),
        'binding': results.semantic_validation_binding(imported)}
    return binding


def decision_request(binding):
    core = binding['core']
    return {'action': jobs.ACTION, 'subject': job_id(binding['semantic_validation']['completion']),
        'bindings': {'job_core_sha256': jobs.digest(jobs.encoded(binding)), 'source': core['source'],
            'experiment': core['experiment'], 'spec_sha256': core['files'][core['spec']],
            'code_sha256': core['files']['campaigns/isles24-pilot/experiments/' + core['experiment'] + '/validate_return.py']},
        'transition': jobs.TRANSITION.copy()}



def launch_specification(registry, completion, *, original_client):
    """One authenticated capture supplies both formal scientific roles."""
    imported = results.export_result(registry, completion, original_client=original_client)
    binding = _binding_from_original(registry, imported)
    request = decision_request(binding)
    return {'schema': 'scientific-validation-launch-specification/v1',
        'source': registry.config['source'], 'completion': completion,
        'decision_request': {**request,
            'evidence': {'validation-execution-binding.json': jobs.encoded(binding).decode(),
                         'original-completed-result.json': encoded(imported).decode()},
            'request': 'Judge one fixed semantic-validation execution over this exact preserved completed '
                'result using its reviewed validator and explicit interface. This is a separate Linux '
                'execution decision, not reuse of the original experiment launch. Review actual validator '
                'code, specification, inputs/settings/version, original aggregates and resource limits. '
                'No experiment rerun, changed methodology, new data, dependency installation, network access '
                'or automatic retry. APPLY authorizes this validator attempt only. Missing scientific '
                'or operational justification requires DEFER; no acceptance or adoption follows from exit zero.'},
        'scientific_acceptance': False, 'model_calls': 0}


def checked_launch_specification(value, source, completion):
    if (not isinstance(value, dict) or set(value) != {'schema', 'source', 'completion',
            'decision_request', 'scientific_acceptance', 'model_calls'}
            or value['schema'] != 'scientific-validation-launch-specification/v1'
            or value['source'] != source or value['completion'] != completion
            or value['scientific_acceptance'] is not False
            or type(value['model_calls']) is not int or value['model_calls'] != 0):
        raise ValueError('SEMANTIC_VALIDATION_PROTECTED_SPECIFICATION_REQUIRED')
    request = value['decision_request']
    if (not isinstance(request, dict) or set(request) != {'action', 'subject', 'bindings',
            'transition', 'evidence', 'request'} or not isinstance(request['evidence'], dict)
            or set(request['evidence']) != {'validation-execution-binding.json', 'original-completed-result.json'}):
        raise ValueError('SEMANTIC_VALIDATION_PROTECTED_SPECIFICATION_CHANGED')
    binding = json.loads(request['evidence']['validation-execution-binding.json'])
    imported = json.loads(request['evidence']['original-completed-result.json'])
    expected_binding = results.semantic_validation_binding(imported)
    marker = binding['semantic_validation']
    if (imported['completion'] != completion or imported['source'] != source
            or binding['core'] != imported['event']['execution_binding']
            or marker['schema'] != MARKER or marker['binding'] != expected_binding
            or marker['completion'] != completion or marker['original_attempt'] != imported['event']['attempt']
            or marker['original_request_sha256'] != imported['request_sha256']
            or any(request.get(key) != value for key, value in decision_request(binding).items())):
        raise ValueError('SEMANTIC_VALIDATION_PROTECTED_SPECIFICATION_CHANGED')
    return request


def verify_launch_authority(config, binding, decision_path, *, original_client):
    from orchestrator.formal_decisions import verify_original_decision
    request = decision_request(binding)
    decision = verify_original_decision(config['source_root'], decision_path,
        action=request['action'], subject=request['subject'], bindings=request['bindings'],
        expected_transition=request['transition'], source=config['source'], original_client=original_client)
    if decision['decision'] != 'APPLY':
        raise ValueError('SEMANTIC_VALIDATION_LAUNCH_DEFERRED')
    return {'path': str(Path(decision_path).absolute()), 'decision_sha256': decision['_decision_sha256'],
        'actor': decision['actor'], 'policy': decision['policy'],
        'job_core_sha256': request['bindings']['job_core_sha256']}


def check_registered(registry, binding, *, original_client):
    fresh = execution_binding(registry, binding['semantic_validation']['completion'], original_client=original_client)
    authority = binding.get('validation_authority')
    if not isinstance(authority, dict) or set(authority) != {
            'path', 'decision_sha256', 'actor', 'policy', 'job_core_sha256'}:
        raise ValueError('SEMANTIC_VALIDATION_LAUNCH_AUTHORITY_REQUIRED')
    fresh['validation_authority'] = verify_launch_authority(registry.config, fresh,
        authority['path'], original_client=original_client)
    if fresh != binding:
        raise ValueError('SEMANTIC_VALIDATION_REGISTERED_BINDING_CHANGED')
    return fresh


def register(registry, completion, decision_path, *, original_client):
    binding = execution_binding(registry, completion, original_client=original_client)
    binding['validation_authority'] = verify_launch_authority(registry.config, binding,
        decision_path, original_client=original_client)
    job = job_id(completion)
    registry.register(job, binding)
    registry.db.execute("UPDATE jobs SET phase='scientific_validation' WHERE id=? AND phase='acquisition'", (job,))
    return {'job': job, 'completion': completion, 'status': registry.get(job)['status'],
            'scientific_acceptance': False, 'model_calls': 0}


def original_result(config, binding):
    """Worker-readable originals; no database, callbacks or caller-chosen paths."""
    marker = binding.get('semantic_validation')
    if (not isinstance(marker, dict) or set(marker) != {
            'schema', 'completion', 'original_attempt', 'original_request_sha256', 'binding'}
            or marker['schema'] != MARKER):
        raise ValueError('SEMANTIC_VALIDATION_EXECUTION_BINDING_REQUIRED')
    for name in ('completion', 'original_attempt', 'original_request_sha256'):
        jobs.pin(marker[name])
    original_path = jobs.protected(Path(config['requests']) / (marker['original_attempt'] + '.json'))
    original = json.loads(jobs.regular(original_path))
    expected_binding = {key: value for key, value in binding.items() if key not in ('semantic_validation', 'validation_authority')}
    if (original.get('schema') != 'linux-scientific-attempt/v1'
            or original.get('attempt') != marker['original_attempt']
            or original.get('binding') != expected_binding
            or jobs.digest(jobs.encoded(original)) != marker['original_request_sha256']
            or jobs.digest(jobs.encoded(expected_binding)) != original['attempt']):
        raise ValueError('SEMANTIC_VALIDATION_ORIGINAL_REQUEST_CHANGED')
    folder = Path(config['outputs']) / original['attempt']
    outcome = json.loads(jobs.regular(folder / 'outcome.json'))
    jobs.validate_outcome(original, folder, outcome)
    if outcome['status'] != 'COMPLETE' or jobs.digest(jobs.encoded(outcome)) != marker['completion']:
        raise ValueError('SEMANTIC_VALIDATION_ORIGINAL_RETURN_CHANGED')
    core = binding['core']
    validator = interface(binding)
    expected = {
        'completion': marker['completion'], 'source': core['source'],
        'scientific_version': jobs.digest(encoded(core['scientific_version'])),
        'protocol_decision_sha256': core['protocol']['decision_sha256'],
        'input_manifest_sha256': core['files'][core['input_manifest']],
        'result_manifest_sha256': outcome['result_manifest_sha256'],
        'validator_sha256': core['files'][validator]}
    if marker['binding'] != expected:
        raise ValueError('SEMANTIC_VALIDATION_EXECUTED_BINDING_CHANGED')
    return folder / 'artifacts/result', expected


def binding_path(config, attempt):
    jobs.pin(attempt)
    return Path(config['requests']) / (attempt + '.validation-binding.json')


def worker_argv(config, request, artifacts, inputs):
    """Only fixed reviewed validator/arguments; the old result stays read-only."""
    binding = request['binding']
    result, expected = original_result(config, binding)
    path = jobs.protected(binding_path(config, request['attempt']))
    if jobs.regular(path) != encoded(expected):
        raise ValueError('SEMANTIC_VALIDATION_BOUND_INPUT_CHANGED')
    root = Path(binding['artifact_root'])
    target = Path(artifacts) / 'result'
    target.mkdir(mode=0o700)
    aliases = {'@result': str(result), '@input': inputs['root'],
               '@settings': str(root / binding['core']['settings']),
               '@binding': str(path), '@output': str(target / OUTPUT)}
    return [config['python'], '-B', str(root / interface(binding)),
            *[aliases.get(arg, arg) for arg in INTERFACE['arguments']]]


def checked_output(config, request, artifacts):
    # Reauthenticate the original inventory after validator execution as well.
    _, expected = original_result(config, request['binding'])
    raw = jobs.regular(Path(artifacts) / 'result' / OUTPUT, results.SEMANTIC_OUTPUT_MAX_BYTES)
    results.semantic_validation_output(raw, expected)
    return raw


def export_result(registry, completion, *, original_client):
    """Protected original-only retrieval; never dispatch or retry a validator."""
    if os.getuid() != 0:
        raise ValueError('SEMANTIC_VALIDATION_PROTECTED_BROKER_REQUIRED')
    jobs.pin(completion)
    row = registry.db.execute('SELECT * FROM scientific_attempts WHERE job=?',
                             (job_id(completion),)).fetchone()
    if row is None:
        raise ValueError('SEMANTIC_VALIDATION_ORIGINAL_ATTEMPT_REQUIRED')
    request = json.loads(row['request'])
    binding = check_registered(registry, request['binding'], original_client=original_client)
    if (binding['semantic_validation']['completion'] != completion
            or request.get('schema') != ATTEMPT or request.get('binding') != binding
            or request.get('attempt') != row['id']
            or jobs.digest(jobs.encoded(binding)) != row['id']):
        raise ValueError('SEMANTIC_VALIDATION_REGISTERED_ATTEMPT_CHANGED')
    registered = jobs.regular(jobs.protected(Path(registry.config['requests']) / (row['id'] + '.json')))
    if json.loads(registered) != request:
        raise ValueError('SEMANTIC_VALIDATION_ORIGINAL_REQUEST_CHANGED')
    folder = Path(registry.config['outputs']) / row['id']
    outcome = json.loads(jobs.regular(folder / 'outcome.json'))
    jobs.validate_outcome(request, folder, outcome)
    if outcome['status'] != 'COMPLETE':
        raise ValueError('SEMANTIC_VALIDATION_FAILED_NO_RETRY')
    raw = checked_output(registry.config, request, folder / 'artifacts')
    jobs.validate_outcome(request, folder, outcome)
    result = {'schema': results.SEMANTIC_RESULT_SCHEMA, 'execution_status': 'COMPLETE',
        'binding': binding['semantic_validation']['binding'], 'attempt': row['id'],
        'request_sha256': jobs.digest(jobs.encoded(request)),
        'outcome_sha256': jobs.digest(jobs.encoded(outcome)), 'output': raw.decode('utf-8'),
        'scientific_acceptance': False, 'model_calls': 0}
    if len(encoded(result)) > results.SEMANTIC_RESULT_MAX_BYTES:
        raise ValueError('SEMANTIC_VALIDATION_RESPONSE_BYTE_BOUND')
    return result
