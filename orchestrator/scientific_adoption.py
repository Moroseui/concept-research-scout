"""Prospective adoption of one reviewed successor, separate from acceptance.

This adapter grants no eligibility or execution. Saved-operation and protected
registration consumers must verify its exact application before dependent use.
"""
import hashlib
import json
import os
from pathlib import Path

from orchestrator.hosted_cycle import encoded, immutable
from orchestrator.operations_report import private_root
from orchestrator.remote_supervisor import lock
from orchestrator.scientific_materialization import _read

SCHEMA = 'prospective-followup-adoption/v1'
COMPATIBILITY = 'accepted-result-successor-compatibility/v1'
STATUS = 'AGENT_FOLLOWUP_ADOPTION_APPLIED'


def _sha(value):
    return hashlib.sha256(encoded(value)).hexdigest()


def prepare(config, acceptance, selection, *, original_client):
    from orchestrator import continuing_operations as ops, continuing_research as continuing
    from orchestrator.investigator_wakes import _operation, _task
    from orchestrator.research_catalog import linked_change
    from orchestrator.campaign import require_no_human_stop
    from orchestrator.remote_supervisor import checked_source
    ops.operation_reference(acceptance); continuing.reference(selection)
    if selection['artifact'] != 'round-1/selection.json':
        raise ValueError('ADOPTION_ORIGINAL_SELECTION_REQUIRED')
    root = checked_source(config['source_root'], config['source'])
    # This existing native reader revalidates the selecting roles, acceptance
    # decision, current interpretation/validation and exact application marker.
    observed = _operation(config, acceptance, original_client)['operation']
    if observed['kind'] != 'ACCEPT_RESULT':
        raise ValueError('ADOPTION_APPLIED_ACCEPTANCE_REQUIRED')
    accepted = observed['result']
    if (accepted['source'] != config['source'] or accepted.get('scientific_acceptance') is not True
            or accepted.get('adoption') is not False or accepted.get('execution_authorized') is not False):
        raise ValueError('ADOPTION_APPLIED_ACCEPTANCE_REQUIRED')
    path = ops._directory(config)/acceptance['operation']/'prepared.json'
    original_request = json.loads(_read(path))['formal_request']
    if _sha(original_request) != accepted['formal_request_sha256']:
        raise ValueError('ADOPTION_ACCEPTANCE_REQUEST_CHANGED')
    original = _task(config, selection['task'], original_client,
                     investigator=True, include_originals=True)
    packet = original['packet']
    if (selection not in original['references']
            or original['disposition']['source'] != config['source']
            or original['disposition']['acceptance_status'] != 'APPROVED_PROPOSAL_ONLY'):
        raise ValueError('ADOPTION_REVIEWED_SELECTION_REQUIRED')
    linked_change(config, packet['research_catalog_entry'])
    from orchestrator.scientific_context_references import completed_rows
    supplied = completed_rows(config, packet)
    if acceptance not in [row['reference'] for row in supplied]:
        raise ValueError('ADOPTION_ACCEPTANCE_NOT_IN_SELECTION_CONTEXT')
    proposed = json.loads(continuing.read_reference(config, selection))
    desired = (proposed.get('successor') or {}).get('protocol')
    protocols = continuing.observed_protocols(config, packet, client=original_client,
                                             desired=desired) if desired else ()
    continuing.selection(packet['campaign_task'], proposed, protocols=protocols)
    if proposed['status'] != 'PROPOSE':
        raise ValueError('ADOPTION_DEFERRED_SELECTION_CANNOT_APPLY')
    successor = proposed['successor']
    if (successor.get('schema') != continuing.PROSPECTIVE_SCHEMA
            or successor['mode'] not in ('readiness', 'propose', 'specify', 'code_bundle', 'discuss')
            or accepted['interpretation'] not in successor['references']
            or successor.get('accepted_result') != acceptance):
        raise ValueError('ADOPTION_TYPED_SUCCESSOR_REQUIRES_ACCEPTED_EVIDENCE')
    require_no_human_stop(root, successor['experiment'])
    protocol = continuing.read_protocol(config, successor, original_client=original_client)
    # Source/experiment/protocol compatibility is mechanically exact. A changed
    # reviewed protocol is visible to both judges, not presumed scientifically
    # equivalent. Formal reviewers decide whether the proposed change is sound.
    parent_result = json.loads(original_request['evidence']['original-result.json'])
    if successor.get('import_result') is not None:
        imported = continuing.read_result_import(config, successor, original_client=original_client)
        if imported['receipt']['completion'] != accepted['bindings']['completion']:
            raise ValueError('ADOPTION_SUCCESSOR_IMPORT_REFERS_TO_DIFFERENT_RESULT')
    compatibility = {
        'schema': COMPATIBILITY, 'source': config['source'],
        'acceptance': acceptance, 'acceptance_decision_sha256': accepted['decision_sha256'],
        'accepted_completion': accepted['bindings']['completion'],
        'parent_scientific_version_sha256': accepted['bindings']['scientific_version_sha256'],
        'parent_experiment': accepted['bindings']['experiment'],
        'parent_protocol_decision_sha256': accepted['bindings']['protocol_decision_sha256'],
        'successor_experiment': successor['experiment'], 'successor_mode': successor['mode'],
        'successor_task_sha256': _sha(successor),
        'successor_protocol_decision_sha256': successor['protocol']['decision_sha256'],
        'protocol_relation': ('SAME_REVIEWED_PROTOCOL' if
            successor['protocol']['decision_sha256'] == accepted['bindings']['protocol_decision_sha256']
            else 'DISTINCT_REVIEWED_PROTOCOL'),
        'execution_authorized': False}
    if (parent_result['completion'] != compatibility['accepted_completion']
            or _sha(parent_result['scientific_version']) != compatibility['parent_scientific_version_sha256']):
        raise ValueError('ADOPTION_ACCEPTED_RESULT_BINDING_CHANGED')
    bindings = {'source': config['source'], 'acceptance_sha256': _sha(acceptance),
        'acceptance_application_sha256': _sha({k: v for k, v in accepted.items() if k != 'duplicate'}),
        'selection': selection, 'selection_packet_sha256': _sha(packet),
        'successor_sha256': _sha(successor), 'compatibility_sha256': _sha(compatibility)}
    # Reuse the already authenticated immutable acceptance capture, once. The
    # complete history remains preserved elsewhere; no later-read claim is made.
    evidence = {**original_request['evidence'],
        'acceptance-application.json': encoded(accepted).decode(),
        'successor-selection.json': encoded(proposed).decode(),
        'successor-compatibility.json': encoded(compatibility).decode(),
        'successor-protocol.original.json': encoded(protocol).decode(),
        'successor-opposing-review.original.txt': original['original_answers']['review'],
        'successor-disposition.original.md': original['original_answers']['disposition'],
        'successor-provenance.json': encoded({'selection': selection,
            'packet_sha256': _sha(packet), 'stage_receipts': original['original_receipts']}).decode()}
    return {'action': 'adopt_followup', 'subject': 'adopt-' + _sha(bindings)[:56],
        'bindings': bindings,
        'transition': {'from': 'ACCEPTED_RESULT_AND_REVIEWED_SUCCESSOR', 'to': 'AGENT_ADOPTED'},
        'evidence': evidence,
        'request': ('Decide APPLY or DEFER for this exact reviewed follow-up grounded in the accepted result. '
            'Check scientific compatibility, interpretation limits, unresolved criticism, scope and charter. '
            'A DISTINCT_REVIEWED_PROTOCOL requires explicit assessment of methodological differences; '
            'mechanical compatibility never establishes scientific equivalence. Adoption does not grant '
            'task eligibility, materialization, execution, data access or publication. Name missing evidence '
            'and a concrete reconsideration condition when deferring. No legacy result or failed task is retried.')}


def _expected(config, acceptance, selection, request, decision_path, original_client, by):
    from orchestrator import formal_decisions as formal
    from orchestrator.change_requests import actor
    from orchestrator.research_catalog import linked_change
    actor(by)
    if (type(config['controller_uid']) is not int or config['controller_uid'] <= 0
            or os.getuid() != config['controller_uid']):
        raise ValueError('ADOPTION_CONTROLLER_IDENTITY_REQUIRED')
    fresh = prepare(config, acceptance, selection, original_client=original_client)
    formal.checked_request(request)
    if (request['source'] != config['source'] or request['workspace'] is not None
            or request['application'] is not None or any(request.get(k) != v for k, v in fresh.items())):
        raise ValueError('ADOPTION_CURRENT_FORMAL_REQUEST_CHANGED')
    linked_change(config, {'change_request': request['change_request']})
    path = Path(decision_path).absolute(); state = Path(config['state']).absolute()
    if (path.name != 'decision.json' or path.parent.name != 'round-1'
            or path.parent.parent.parent != state/'formal-decisions'):
        raise ValueError('ADOPTION_SAVED_FORMAL_DECISION_REQUIRED')
    if formal.original_transport(path.parent.parent, request)['packet']['formal_request'] != request:
        raise ValueError('ADOPTION_ORIGINAL_FORMAL_REQUEST_CHANGED')
    proof = formal.verify_original_decision(config['source_root'], path,
        action=fresh['action'], subject=fresh['subject'], bindings=fresh['bindings'],
        expected_transition=fresh['transition'], source=config['source'], original_client=original_client)
    if proof['decision'] != 'APPLY':
        raise ValueError('DEFERRED_FOLLOWUP_CANNOT_BE_ADOPTED')
    record = {'schema': SCHEMA, 'status': STATUS, 'source': config['source'],
        'acceptance': acceptance, 'selection': selection, 'bindings': fresh['bindings'],
        'compatibility': json.loads(fresh['evidence']['successor-compatibility.json']),
        'decision_path': str(path), 'decision_sha256': proof['_decision_sha256'],
        'formal_request_sha256': _sha(request), 'actor': proof['actor'], 'policy': proof['policy'],
        'transition': proof['transition'], 'applied_by': by,
        'adoption': True, 'execution_authorized': False, 'model_calls': 0}
    folder = state/'scientific-adoptions'/_sha({'acceptance': acceptance, 'selection': selection})
    return record, folder


def apply(config, acceptance, selection, request, decision_path, *, original_client, by, recover=False):
    """Apply only original authority; partial/corrupt records are never overwritten."""
    if type(recover) is not bool:
        raise ValueError('ADOPTION_RECOVERY_MODE_REQUIRED')
    record, folder = _expected(config, acceptance, selection, request, decision_path, original_client, by)
    parent = private_root(folder.parent)
    with lock(parent/'.adoption.lock'):
        if folder.exists():
            if recover and not list(folder.iterdir()):
                immutable(folder/'intent.json', encoded(record))
            if json.loads(_read(folder/'intent.json')) != record:
                raise ValueError('ADOPTION_EXISTING_ORIGINAL_PRESERVED')
            target = folder/'application.json'
            if target.exists():
                if json.loads(_read(target)) != record:
                    raise ValueError('ADOPTION_APPLICATION_CHANGED')
                return {**record, 'duplicate': True}
            if not recover:
                raise ValueError('ADOPTION_PARTIAL_APPLICATION_REQUIRES_RECONCILIATION')
        else:
            private_root(folder); immutable(folder/'intent.json', encoded(record))
        fresh, target_folder = _expected(config, acceptance, selection, request, decision_path, original_client, by)
        if fresh != record or target_folder != folder:
            raise ValueError('ADOPTION_ORIGINAL_CHANGED_DURING_APPLICATION')
        immutable(folder/'application.json', encoded(record))
        return {**record, 'duplicate': False}


def read_application(config, acceptance, selection, request, decision_path, *, original_client, by):
    record, folder = _expected(config, acceptance, selection, request, decision_path, original_client, by)
    if (json.loads(_read(folder/'intent.json')) != record
            or json.loads(_read(folder/'application.json')) != record):
        raise ValueError('ADOPTION_APPLICATION_CHANGED')
    return record


def accepted_dependency(config, task, packet, *, original_client):
    """Derive grounding from the original selecting context, never prose alone.

    A completed acceptance in that immutable context is a candidate dependency,
    not trusted authority: native _operation must validate its original judgment.
    Unknown or altered relevant acceptance refuses; ordinary pre-result tasks
    retain their existing route. No later receipt is inserted into this packet.
    """
    from orchestrator import continuing_operations as ops
    from orchestrator.investigator_wakes import _operation
    claimed = task.get('accepted_result')
    if claimed is not None:
        ops.operation_reference(claimed)
    from orchestrator.scientific_context_references import completed_rows
    supplied = completed_rows(config, packet)
    candidates = [row for row in supplied if row.get('kind') == 'ACCEPT_RESULT'
        and (row.get('reference') == claimed or
             row.get('discovery', row.get('result', {})).get('interpretation') in task.get('references', []))]
    matched = []
    for row in candidates:
        ref = row['reference']
        observed = _operation(config, ref, original_client)['operation']
        if observed['kind'] != 'ACCEPT_RESULT':
            raise ValueError('SUCCESSOR_NATIVE_ACCEPTANCE_REQUIRED')
        accepted = observed['result']
        if (accepted.get('source') != config['source']
                or accepted.get('scientific_acceptance') is not True
                or accepted.get('adoption') is not False
                or accepted.get('execution_authorized') is not False):
            raise ValueError('SUCCESSOR_NATIVE_ACCEPTANCE_REQUIRED')
        if accepted['interpretation'] in task.get('references', []):
            matched.append(ref)
    if not matched and claimed is None:
        return None
    if len(matched) != 1 or claimed != matched[0]:
        raise ValueError('SUCCESSOR_EXACT_ACCEPTED_RESULT_DEPENDENCY_REQUIRED')
    return claimed



def selected_operation(config, task, packet, selection, *, original_client):
    """One deterministic derivation shared by enqueue and native recovery."""
    from orchestrator import continuing_operations as ops
    acceptance = accepted_dependency(config, task, packet, original_client=original_client)
    if acceptance is None:
        return None
    return {'schema': ops.SCHEMA, 'operation_id': 'adopt-'+ops.digest(selection)[:48],
            'kind': 'ADOPT_FOLLOWUP', 'inputs': {'acceptance': acceptance, 'selection': selection}}


def require_applied(config, task, packet, selection, adoption, *, original_client):
    """Eligibility/registration consume the same native applied adoption."""
    from orchestrator import continuing_operations as ops
    from orchestrator.investigator_wakes import _operation
    dependency = accepted_dependency(config, task, packet, original_client=original_client)
    if dependency is None:
        if adoption is not None:
            raise ValueError('SUCCESSOR_UNRELATED_ADOPTION_REFUSED')
        return None
    if adoption is None:
        raise ValueError('SUCCESSOR_APPLIED_ADOPTION_REQUIRED')
    ops.operation_reference(adoption)
    value = _operation(config, adoption, original_client)['operation']
    if value['kind'] != 'ADOPT_FOLLOWUP':
        raise ValueError('SUCCESSOR_APPLIED_ADOPTION_REQUIRED')
    result = value['result']
    proposed = dict(task)
    proposed['selected_by'] = None
    if (result.get('status') != STATUS or result.get('source') != config['source']
            or result.get('adoption') is not True or result.get('execution_authorized') is not False
            or result.get('acceptance') != dependency or result.get('selection') != selection
            or result.get('bindings', {}).get('successor_sha256') != _sha(proposed)
            or result.get('compatibility', {}).get('successor_task_sha256') != _sha(proposed)
            or result['compatibility'].get('successor_protocol_decision_sha256') != task['protocol']['decision_sha256']):
        raise ValueError('SUCCESSOR_ADOPTION_COMPATIBILITY_CHANGED')
    return {'reference': adoption, 'application_sha256': _sha({k:v for k,v in result.items() if k != 'duplicate'})}


def require_registration(config, entry, *, original_client):
    """Re-read original selecting context and the saved authority's dependency."""
    from orchestrator import continuing_research as continuing
    task = entry['request']['task']
    selection = task['selected_by']
    packet = json.loads(_read(Path(config['state'])/'tasks'/selection['task']/'packet.json'))
    evidence = continuing.read_evidence(config, entry['request'])
    saved = evidence.get('selected_operation')
    adoption = None
    if saved is not None:
        from orchestrator import continuing_operations as ops
        original = ops._saved(ops._directory(config)/saved['identity'])
        if original != saved or original['source'] != config['source']:
            raise ValueError('SUCCESSOR_ORIGINAL_AUTHORITY_OPERATION_CHANGED')
        operation = original['operation']
        if operation['kind'] != 'AUTHORIZE_TASK' or operation['inputs']['selection'] != selection:
            raise ValueError('SUCCESSOR_ORIGINAL_AUTHORITY_SELECTION_CHANGED')
        adoption = operation['inputs'].get('adoption')
    return require_applied(config, task, packet, selection, adoption, original_client=original_client)
