"""Pure bridge from preserved inspection originals to material-gate evidence.

The request/execution metadata projections are explicitly derived, never provider
originals. The caller authenticates the bundle, bootstrap and host originals.
"""
import json
from orchestrator import deployment_review as gate
from orchestrator import change_requests
from orchestrator import inspection_review as inspection

PROFILE = 'direct-inspection/v1'
CONTEXT_START = '\nBEGIN_SHARED_OPERATING_CONTEXT\n'
CONTEXT_END = '\nEND_SHARED_OPERATING_CONTEXT\n'


def _require(ok, reason):
    if not ok:
        raise ValueError(reason)


def _json(raw):
    return inspection._json(raw)


def _full_read(name, raw, reads):
    lines = len(raw.decode('utf-8').splitlines(keepends=True))
    return name in reads and not inspection._coverage({name: [[1, lines]] if lines else []}, reads)


def validate_deployment_session(manifest_raw, attempts, view_files, required_files,
                                source, scope, proposal_raw, changes_raw, context_raw, *,
                                approved_policy_sources=None):
    """Validate a full material session; perform no file, model or state operation.

    attempts is [{originals: <inspection_review input>, response_raw: bytes,
                  execution_raw: bytes}, ...]. required_files maps exact view
    names to required raw bytes. Native mandatory source coverage is also derived
    independently from the proposal inventory and unchanged gate requirements.
    """
    manifest = inspection.validate_manifest(manifest_raw)
    _require(manifest['source'] == source and manifest['scope'] == scope == 'material-deployment', 'INSPECTION_MATERIAL_SCOPE')
    _require(isinstance(proposal_raw, bytes) and inspection.digest(proposal_raw) == manifest['proposal_sha256'], 'INSPECTION_PROPOSAL_DIGEST')
    proposal = _json(proposal_raw)
    _require(proposal.get('source') == source and proposal.get('review_profile') == PROFILE
             and 'review_plan_sha256' not in proposal and 'inspection_review_sha256' not in proposal, 'INSPECTION_EXPLICIT_PROFILE_REQUIRED')
    _require(isinstance(context_raw, bytes) and inspection.digest(context_raw) == manifest['context_sha256'], 'INSPECTION_OPERATING_CONTEXT_DIGEST')
    if approved_policy_sources is not None:
        from orchestrator.inspection_bootstrap import validate_context
        validate_context(context_raw, approved_policy_sources)
    _require(isinstance(changes_raw, bytes) and inspection.digest(changes_raw) == manifest['changes_sha256'], 'INSPECTION_CHANGE_CONTEXT_DIGEST')
    changes = _json(changes_raw)
    _require(isinstance(changes, list), 'INSPECTION_CHANGE_CONTEXT_LIST')
    _require(isinstance(attempts, list) and attempts, 'INSPECTION_ATTEMPTS_REQUIRED')
    for item in attempts:
        _require(isinstance(item, dict) and set(item) == {'originals', 'response_raw', 'execution_raw'}, 'INSPECTION_ATTEMPT_WRAPPER')
    session = inspection.validate_session(manifest_raw, [item['originals'] for item in attempts])
    _require(session['status'] == 'APPROVE', 'INSPECTION_FULL_TERMINAL_APPROVAL_REQUIRED')
    from orchestrator.inspection_canary import require_read_boundary
    access = _json(manifest['access_manifest_original'].encode('utf-8'))
    for item in attempts:
        require_read_boundary(_json(item['originals']['permission_probe']),
                              read_failure_policy=access.get('read_failure_policy'))
    _require(isinstance(view_files, dict) and set(view_files) == set(access['files']), 'INSPECTION_EXACT_VIEW_INVENTORY')
    for name, raw in view_files.items():
        identity = access['files'][name]
        _require(isinstance(raw, bytes) and inspection.digest(raw) == identity['sha256']
                 and len(raw) == identity['bytes'] and len(raw.decode('utf-8').splitlines(keepends=True)) == identity['line_count'], 'INSPECTION_VIEW_BYTES_CHANGED')
    _require(isinstance(required_files, dict) and required_files and set(required_files) <= set(view_files)
             and all(isinstance(raw, bytes) and view_files[name] == raw for name, raw in required_files.items()), 'INSPECTION_REQUIRED_BYTES_CHANGED')

    inventory = proposal.get('source_files')
    _require(isinstance(inventory, dict) and inventory, 'INSPECTION_PROPOSAL_SOURCE_INVENTORY')
    archived = {}
    for name, expected in inventory.items():
        _require(isinstance(name, str) and 'source/' + name in view_files, 'INSPECTION_SOURCE_FILE_UNAVAILABLE')
        raw = view_files['source/' + name]
        _require(inspection.digest(raw) == expected, 'INSPECTION_PROPOSAL_SOURCE_CHANGED')
        archived[name] = raw
    native_required, _ = gate.coverage_requirements(archived)
    mandatory = set(native_required) | gate.INTEGRATION_FILES
    _require({'source/' + name for name in mandatory} <= set(required_files), 'INSPECTION_NATIVE_REQUIRED_SOURCE_OMITTED')
    for name, raw in required_files.items():
        _require(name in manifest['required_ranges'] and _full_read(name, raw, session['reads']), 'INSPECTION_REQUIRED_FILE_NOT_FULLY_READ')

    # Only host-confirmed complete reads become gate evidence. Availability and
    # the model's own inspected-files declaration confer no evidence membership.
    full = {name: raw for name, raw in view_files.items() if _full_read(name, raw, session['reads'])}
    private = {inspection.digest(raw): raw for raw in full.values()}
    _require(private.get(manifest['proposal_sha256']) == proposal_raw, 'INSPECTION_PROPOSAL_NOT_READ')
    _require(private.get(manifest['changes_sha256']) == changes_raw, 'INSPECTION_CHANGES_NOT_READ')
    sidecar_raw = private.get(manifest['change_bindings_sha256'])
    _require(sidecar_raw is not None, 'INSPECTION_CHANGE_BINDINGS_NOT_READ')
    expected_sidecar = change_requests.review_bindings(source, inspection.digest(proposal_raw), proposal.get('changes'))
    _require(_json(sidecar_raw) == expected_sidecar, 'INSPECTION_CHANGE_BINDINGS_CHANGED')
    for field in ('targets', 'previous_files'):
        entries = proposal.get(field)
        _require(isinstance(entries, dict) and entries, 'INSPECTION_REQUIRED_CONFIG_INVENTORY')
        for metadata in entries.values():
            _require(isinstance(metadata, dict) and metadata.get('sha256') in private, 'INSPECTION_CONFIGURATION_NOT_READ')
    _require(proposal.get('recovery_sha256') in private, 'INSPECTION_RECOVERY_NOT_READ')

    actual = []
    for index, item in enumerate(attempts):
        originals = item['originals']
        request = _json(originals['request'])
        events = [_json(line) for line in originals['protocol'].splitlines() if line.strip()]
        result = next(event for event in events if event.get('type') == 'result')
        response, execution = _json(item['response_raw']), _json(item['execution_raw'])
        _require(response == result, 'INSPECTION_RESPONSE_IS_NOT_ORIGINAL_RESULT')
        if index == 0:
            framed = CONTEXT_START + context_raw.decode('utf-8') + CONTEXT_END
            _require(request['prompt'].count(framed) == 1, 'INSPECTION_CONTEXT_NOT_IN_FIRST_ACTUAL_PROMPT')
            if approved_policy_sources is not None:
                _require(request['prompt'].startswith(framed), 'INSPECTION_APPROVED_CONTEXT_NOT_FIRST')
        projection = {'schema': 'formal-inspection-execution/v1', 'reviewed_commit': source,
                      'requested_model': inspection.model_policy.requested_model(manifest.get('model_policy_version')),
                      'assistant_message_models': sorted({event['message']['model'] for event in events
                                                          if event.get('type') == 'assistant'}),
                      'actual_usage_models': list(response['modelUsage']),
                      'returncode': _json(originals['returned'])['returncode'],
                      'request_sha256': inspection.digest(originals['request']),
                      'response_sha256': inspection.digest(item['response_raw']),
                      'protocol_sha256': inspection.digest(originals['protocol']),
                      'prompt_sha256': inspection.digest(request['prompt'].encode('utf-8')),
                      'session_id': manifest['session_id'], 'runtime_sha256': manifest['pins']['runtime_sha256'],
                      'manifest_sha256': inspection.digest(manifest_raw), 'context_sha256': manifest['context_sha256']}
        _require(isinstance(execution, dict) and all(execution.get(key) == value for key, value in projection.items()), 'INSPECTION_EXECUTION_ORIGINAL_BINDING')
        actual.append({'request': request, 'response': response, 'execution': execution,
                       'execution_metadata_projection': projection,
                       'execution_original_sha256': inspection.digest(item['execution_raw'])})
    last = actual[-1]
    source_text = {name[len('source/'):]: raw.decode('utf-8') for name, raw in full.items() if name.startswith('source/')}
    metadata = {**last['request'], 'metadata_projection': 'DERIVED_FROM_VALIDATED_INSPECTION_ORIGINALS',
                'change_bindings_sha256': manifest['change_bindings_sha256'],
                'change_context_sha256': inspection.digest(json.dumps(changes, sort_keys=True).encode()),
                'shared_context_sha256': manifest['context_sha256'],
                'input_file_sha256': {name: inspection.digest(text.encode()) for name, text in source_text.items()}}
    review = {'request': metadata, 'request_metadata_projection': metadata, 'actual_request': last['request'],
              'response': last['response'], 'execution': last['execution'],
              'execution_metadata_projection': last['execution_metadata_projection'],
              'changes': changes, 'source_text': source_text, 'private_text': private,
              'inspection_session': session, 'inspection_profile': PROFILE,
              'actual_execution_file_sha256': last['execution_original_sha256'],
              'original_attempt_file_sha256': [{'request_sha256': entry['execution_metadata_projection']['request_sha256'],
                                               'response_sha256': entry['execution_metadata_projection']['response_sha256'],
                                               'protocol_sha256': entry['execution_metadata_projection']['protocol_sha256'],
                                               'execution_sha256': entry['execution_original_sha256']} for entry in actual],
              'approval_confers_deployment_authority': False}
    # The predecessor chain binds core protocol/host originals. Separately bind
    # the exact derived response/execution file encodings in the frozen sidecar.
    review['full_original_wrapper_index_sha256'] = inspection.digest(inspection.encoded(review['original_attempt_file_sha256']))
    if 'model_policy_version' in manifest:
        review['model_policy_version'] = manifest['model_policy_version']
    review['provider_model'] = review_model(review)
    gate.selected_review_applications(review, proposal_raw, source)
    return review


def review_model(review):
    """Attribute an already validated material session, never a requested model.

    Legacy receipts keep their original shape. New-policy receipts must bind the
    same final identity at the session, attempt and model-policy layers. This
    consumer does not replace original protocol, bootstrap or canary validation.
    """
    _require(review.get('inspection_profile') == PROFILE, 'INSPECTION_MODEL_PROFILE')
    session = review['inspection_session']
    last = session['attempts'][-1]
    _require(session['status'] == last['status'] == 'APPROVE'
             and session['session_id'] == review['response']['session_id']
             and session['source'] == review['execution']['reviewed_commit'], 'INSPECTION_MODEL_SESSION_BINDING')
    version = review.get('model_policy_version')
    if version is None:
        _require('model_policy_version' not in review
                 and 'model_policy_version' not in session and 'model_policy_version' not in last
                 and last['provider_model'] == inspection.MODEL, 'INSPECTION_LEGACY_MODEL_BINDING')
        return inspection.MODEL
    from orchestrator import inspection_model_policy as policy
    policy.version(version)
    requested = policy.requested_model(version)
    allowed = {requested} if version == policy.DIRECT_VERSION else {inspection.MODEL, policy.FALLBACK}
    model = session['provider_model']
    proof = last['model_policy']
    if version == policy.DIRECT_VERSION:
        _require(last['assistant_models'] == [requested], 'INSPECTION_DIRECT_FINAL_MODELS')
    _require(model in allowed
             and version == session['model_policy_version'] == last['model_policy_version']
             == proof['policy_version']
             and session['requested_model'] == last['requested_model'] == proof['requested_model'] == requested
             and model == last['provider_model'] == proof['provider_model']
             and model in last['assistant_models']
             and last['assistant_models'] == proof['assistant_models']
             and proof['session_id'] == session['session_id'], 'INSPECTION_FINAL_MODEL_BINDING')
    return model
