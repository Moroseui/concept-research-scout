"""Prospective result acceptance through existing scientific decisions.

Validation, interpretation, acceptance and adoption are distinct. This module
executes no science or model, rewrites no legacy experiment receipt, and grants
no successor authority. Native originals are required again for dependent use.
"""
import hashlib
import json
import os
from pathlib import Path

from orchestrator.hosted_cycle import encoded, immutable
from orchestrator.operations_report import private_root
from orchestrator.remote_supervisor import checked_source, lock
from orchestrator.scientific_materialization import _read

SCHEMA = 'prospective-result-acceptance/v1'
STATUS = 'AGENT_RESULT_ACCEPTANCE_APPLIED'


def _sha(value):
    return hashlib.sha256(encoded(value)).hexdigest()


def prepare(config, interpretation, *, original_client):
    from orchestrator import continuing_research as continuing
    from orchestrator.investigator_wakes import _task
    from orchestrator.research_catalog import linked_change
    from orchestrator.campaign import require_no_human_stop
    continuing.reference(interpretation)
    if interpretation['artifact'] != 'round-1/interpretation.md':
        raise ValueError('ACCEPTANCE_ORIGINAL_INTERPRETATION_REFERENCE_REQUIRED')
    root = checked_source(config['source_root'], config['source'])
    original = _task(config, interpretation['task'], original_client, include_originals=True)
    packet = original['packet']; task = packet['campaign_task']
    if (task.get('schema') != continuing.PROSPECTIVE_SCHEMA or task.get('mode') != 'interpret'
            or 'semantic_validation' not in task or 'import_result' not in task
            or interpretation not in original['references']
            or original['disposition']['source'] != config['source']
            or original['disposition']['acceptance_status'] != 'APPROVED_PROPOSAL_ONLY'):
        raise ValueError('ACCEPTANCE_VALIDATED_OPPOSING_REVIEWED_INTERPRETATION_REQUIRED')
    linked_change(config, packet['research_catalog_entry'])
    require_no_human_stop(root, task['experiment'])
    imported = continuing.read_result_import(config, task, original_client=original_client)
    validation = continuing.read_validation_context(config, task, imported, original_client=original_client)
    result = imported['receipt']['import']
    # Scientific protocol authority is freshly verified; stored hashes alone
    # cannot promote an obsolete or altered methodology decision.
    protocol = continuing.read_protocol(config, task, original_client=original_client)
    output = json.loads(validation['original']['output'])
    interpretation_text = continuing.read_reference(config, interpretation).decode()
    originals = original['original_answers']
    bindings = {'source': config['source'], 'experiment': task['experiment'],
        'completion': result['completion'], 'original_result_sha256': _sha(result),
        'semantic_response_sha256': validation['receipt']['response_sha256'],
        'semantic_output_sha256': validation['receipt']['output_sha256'],
        'interpretation_task': interpretation['task'], 'interpretation_packet_sha256': _sha(packet),
        'interpretation_sha256': interpretation['sha256'],
        'interpretation_review_sha256': hashlib.sha256(originals['review'].encode()).hexdigest(),
        'interpretation_disposition_sha256': hashlib.sha256(originals['disposition'].encode()).hexdigest(),
        'scientific_version_sha256': _sha(result['scientific_version']),
        'protocol_decision_sha256': result['protocol_decision_sha256']}
    return {'action': 'accept_interpretation',
        'subject': 'accept-' + _sha(bindings)[:56], 'bindings': bindings,
        'transition': {'from': 'VALIDATED_REVIEWED_INTERPRETATION', 'to': 'AGENT_ACCEPTED'},
        'evidence': {
            'original-result.json': encoded(result).decode(),
            'semantic-validation.json': encoded(validation).decode(),
            'interpretation.md': interpretation_text,
            'opposing-review.original.txt': originals['review'],
            'disposition.original.md': originals['disposition'],
            'protocol.original.json': encoded(protocol).decode(),
            'interpretation-provenance.json': encoded({
                'task': interpretation['task'], 'packet_sha256': _sha(packet),
                'references': original['references'],
                'disposition': original['disposition'],
                'stage_receipts': original['original_receipts']}).decode()},
        'request': ('Judge whether this exact prospective result and its reviewed interpretation may be '
            'accepted under the active charter. Independently assess the original semantic validation, '
            'protocol, executed version, aggregate evidence and interpretation limitations. '
            'Semantic status is ' + output['status'] + '. INVALID or DEFER requires DEFER, never APPLY. '
            'VALID is necessary but not sufficient. Acceptance does not adopt a follow-up, authorize '
            'execution or erase later criticism. Preserve a reasoned DEFER and name reconsideration evidence.')}


def _expected(config, interpretation, request, decision_path, original_client, by):
    from orchestrator import formal_decisions as formal
    from orchestrator.change_requests import actor
    from orchestrator.research_catalog import linked_change
    actor(by)
    if (type(config['controller_uid']) is not int or config['controller_uid'] <= 0
            or os.getuid() != config['controller_uid']):
        raise ValueError('ACCEPTANCE_CONTROLLER_IDENTITY_REQUIRED')
    fresh = prepare(config, interpretation, original_client=original_client)
    formal.checked_request(request)
    if (request['source'] != config['source'] or request['workspace'] is not None
            or request['application'] is not None
            or any(request.get(k) != v for k, v in fresh.items())):
        raise ValueError('ACCEPTANCE_CURRENT_FORMAL_REQUEST_CHANGED')
    linked_change(config, {'change_request': request['change_request']})
    path = Path(decision_path).absolute()
    state = Path(config['state']).absolute()
    if (path.name != 'decision.json' or path.parent.name != 'round-1'
            or path.parent.parent.parent != state/'formal-decisions'):
        raise ValueError('ACCEPTANCE_SAVED_FORMAL_DECISION_REQUIRED')
    # Exact original request includes the evidence and change authority, not just
    # a digest-looking action label or a locally manufactured approval receipt.
    if formal.original_transport(path.parent.parent, request)['packet']['formal_request'] != request:
        raise ValueError('ACCEPTANCE_ORIGINAL_FORMAL_REQUEST_CHANGED')
    proof = formal.verify_original_decision(config['source_root'], path,
        action=fresh['action'], subject=fresh['subject'], bindings=fresh['bindings'],
        expected_transition=fresh['transition'], source=config['source'], original_client=original_client)
    if proof['decision'] != 'APPLY':
        raise ValueError('DEFERRED_RESULT_CANNOT_BE_ACCEPTED')
    semantic = json.loads(fresh['evidence']['semantic-validation.json'])
    if semantic['receipt']['validator_status'] != 'VALID':
        raise ValueError('ACCEPTANCE_REQUIRES_SEMANTIC_VALID')
    record = {'schema': SCHEMA, 'status': STATUS, 'source': config['source'],
        'interpretation': interpretation, 'bindings': fresh['bindings'],
        'decision_path': str(path), 'decision_sha256': proof['_decision_sha256'],
        'formal_request_sha256': _sha(request), 'actor': proof['actor'], 'policy': proof['policy'],
        'transition': proof['transition'], 'applied_by': by,
        'scientific_acceptance': True, 'adoption': False, 'execution_authorized': False,
        'model_calls': 0}
    folder = state/'scientific-results'/fresh['bindings']['completion']/'acceptance'/interpretation['task']
    return record, folder


def apply(config, interpretation, request, decision_path, *, original_client, by, recover=False):
    """One immutable application; explicit recovery resumes only matching originals."""
    if type(recover) is not bool:
        raise ValueError('ACCEPTANCE_RECOVERY_MODE_REQUIRED')
    record, folder = _expected(config, interpretation, request, decision_path, original_client, by)
    parent = private_root(folder.parent)
    with lock(parent/'.acceptance.lock'):
        if folder.exists():
            # A crash after mkdir but before the first write has no application
            # effect. Explicit recovery may initialize only that empty directory.
            if recover and not list(folder.iterdir()):
                immutable(folder/'intent.json', encoded(record))
            intent = json.loads(_read(folder/'intent.json'))
            if intent != record:
                raise ValueError('ACCEPTANCE_EXISTING_ORIGINAL_PRESERVED')
            target = folder/'application.json'
            if target.exists():
                if json.loads(_read(target)) != record:
                    raise ValueError('ACCEPTANCE_APPLICATION_CHANGED')
                return {**record, 'duplicate': True}
            if not recover:
                raise ValueError('ACCEPTANCE_PARTIAL_APPLICATION_REQUIRES_RECONCILIATION')
        else:
            # The saved operation can stop before this adapter writes its own
            # intent. Reapplying authenticated originals creates no second model
            # call or external effect; the exclusive marker still wins once.
            private_root(folder)
            immutable(folder/'intent.json', encoded(record))
        # Reauthenticate before the final exclusive marker; no model or external
        # effect is retried during this explicit original-only reconciliation.
        fresh, target_folder = _expected(config, interpretation, request, decision_path, original_client, by)
        if fresh != record or target_folder != folder:
            raise ValueError('ACCEPTANCE_ORIGINAL_CHANGED_DURING_APPLICATION')
        immutable(folder/'application.json', encoded(record))
        return {**record, 'duplicate': False}


def read_application(config, interpretation, request, decision_path, *, original_client, by):
    """A saved marker never substitutes for current native evidence/authority."""
    record, folder = _expected(config, interpretation, request, decision_path, original_client, by)
    if (json.loads(_read(folder/'intent.json')) != record
            or json.loads(_read(folder/'application.json')) != record):
        raise ValueError('ACCEPTANCE_APPLICATION_CHANGED')
    return record
