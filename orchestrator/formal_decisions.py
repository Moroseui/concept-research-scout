"""Existing scientific decisions over the protected, admitted two-role transport.

Selection, scientific judgment, recorded application and execution remain distinct.
The original provider protocol is retained; no courier-shaped evidence is invented.
"""
from copy import deepcopy
import hashlib
import json
import os
from pathlib import Path
import re
from types import SimpleNamespace

from orchestrator import scientific_authority as authority
from orchestrator.handover_coordinator import digest
from orchestrator.hosted_cycle import encoded, immutable
from orchestrator.handover_runtime import request_broker
from orchestrator.hosted_campaign import BrokerStages, artifact_files
from orchestrator.research_task_authority import DecisionStages, _provenance, _turn_guard, _recovery_mode

class FormalDecisionStages(DecisionStages):
    def preflight_bodies(self, root, body, max_rounds):
        # A generated scientific workspace intentionally has no Git carrier.
        # Provider composition uses the pinned installed source, just as the
        # protected dispatch does; prepare still binds the workspace science.
        return super().preflight_bodies(self.source_root, body, max_rounds)

    def hosted_policy_source(self, root):
        # Formal actions use their exact full policy in the saved decision body.
        # Prospective composition shares that same literal after validation;
        # never select the eligibility-only prepare(action) branch.
        return None


SCHEMA = 'formal-scientific-decision-request/v1'
ACTIONS = frozenset(('approve_probe', 'adopt_followup', 'accept_interpretation',
                     'authorize_protocol', 'launch_linux_job', 'approve_scientific_version'))
APPLICATION_ACTIONS = frozenset(('approve_probe', 'adopt_followup', 'accept_interpretation'))


def contract(value):
    if (not isinstance(value, dict) or set(value) !=
            {'version', 'action', 'subject', 'bindings_sha256'} or type(value['version']) is not int
            or value['version'] != 3 or value['action'] not in ACTIONS
            or not isinstance(value['subject'], str) or not value['subject'].strip()
            or len(value['subject']) > 200
            or not re.fullmatch('[0-9a-f]{64}', str(value['bindings_sha256']))):
        raise ValueError('FORMAL_SCIENTIFIC_DECISION_CONTRACT')
    return value


def checked_request(value):
    if (not isinstance(value, dict) or set(value) !=
            {'schema', 'source', 'action', 'subject', 'bindings', 'evidence', 'request',
             'transition', 'workspace', 'application', 'change_request'}
            or value['schema'] != SCHEMA or value['action'] not in ACTIONS
            or not re.fullmatch('[0-9a-f]{40}', str(value['source']))
            or not isinstance(value['bindings'], dict)
            or not isinstance(value['evidence'], dict) or not value['evidence']
            or len(value['evidence']) > 32
            or not isinstance(value['request'], str) or not value['request'].strip()):
        raise ValueError('FORMAL_SCIENTIFIC_REQUEST_REQUIRED')
    contract({'version': 3, 'action': value['action'], 'subject': value['subject'],
              'bindings_sha256': digest(value['bindings'])})
    transition = value['transition']
    if (not isinstance(transition, dict) or set(transition) != {'from', 'to'}
            or any(not isinstance(v, str) or not v.strip() for v in transition.values())):
        raise ValueError('FORMAL_SCIENTIFIC_TRANSITION_REQUIRED')
    for name, content in value['evidence'].items():
        if (not isinstance(name, str) or not re.fullmatch('[A-Za-z0-9_.-]{1,160}', name)
                or name == 'recorded-formal-request.json'
                or not isinstance(content, str) or not content.strip()):
            raise ValueError('FORMAL_SCIENTIFIC_EVIDENCE_REQUIRED')
    from orchestrator.public_export import text
    text(json.dumps(value), limit=1400000)
    change = value['change_request']
    if (not isinstance(change, dict) or set(change) != {'request_id', 'applied_event'}
            or any(not re.fullmatch('[0-9a-f]{64}', str(v)) for v in change.values())):
        raise ValueError('FORMAL_SCIENTIFIC_CHANGE_REFERENCE_REQUIRED')
    workspace = value['workspace']
    if workspace is not None and (not isinstance(workspace, str) or not re.fullmatch(
            r'scientific-versions/[0-9a-f]{64}/workspace', workspace)):
        raise ValueError('REGISTERED_SCIENTIFIC_WORKSPACE_REQUIRED')
    application = value['application']
    if application is not None:
        if (value['action'] not in APPLICATION_ACTIONS or not isinstance(application, dict)
                or set(application) != {'operation', 'experiment', 'proposal'}
                or application['operation'] != 'campaign-apply-decision'
                or application['experiment'] not in ('P001', 'P002', 'P003')):
            raise ValueError('FORMAL_CAMPAIGN_APPLICATION_REQUIRED')
        proposal = application['proposal']
        if proposal is not None:
            path = Path(proposal)
            if (not isinstance(proposal, str) or path.is_absolute() or '..' in path.parts
                    or not path.is_relative_to('campaigns/isles24-pilot/pipeline')):
                raise ValueError('FORMAL_CAMPAIGN_PROPOSAL_PATH_REQUIRED')
    return value


def scientific_root(config, request):
    from orchestrator.remote_supervisor import checked_source
    root = checked_source(config['source_root'], config['source'])
    if request['source'] != config['source']:
        raise ValueError('CURRENT_FORMAL_DECISION_SOURCE_REQUIRED')
    if request['workspace'] is None:
        return root
    workspace = Path(config['state']).absolute() / request['workspace']
    if any(p.is_symlink() for p in (workspace, *workspace.parents)) or not workspace.is_dir():
        raise ValueError('FORMAL_SCIENTIFIC_WORKSPACE_UNAVAILABLE')
    # Scientific artifacts may evolve; installed policy and role instructions may
    # not be replaced by a model-written workspace. No module is imported here.
    if authority.context(workspace) != authority.context(root):
        raise ValueError('SCIENTIFIC_WORKSPACE_POLICY_CHANGED')
    return workspace


def event(request):
    return {'turn_id': digest({'formal_decision': request}), 'attempt': '1',
            'source': request['source'], 'branch': 'astra/infrastructure-milestone-record',
            'kind': 'astra_turn'}


def _packet(config, request):
    from orchestrator.change_requests import load
    change = request['change_request']
    history = load(Path(config['change_request_store']) / change['request_id'])
    if not any(row['event'] == 'APPLIED' and row['identity'] == change['applied_event']
               for row in history['events']):
        raise ValueError('FORMAL_SCIENTIFIC_APPLIED_VERSION_REQUIRED')
    packet = {'version': 1, 'trigger': 'registered-formal-scientific-decision',
            'scientific_decision_artifacts': {
                'version': 3, 'action': request['action'], 'subject': request['subject'],
                'bindings_sha256': digest(request['bindings'])},
            'formal_request': request, 'recorded_changes': history}
    from orchestrator import current_scientific_input as current
    from orchestrator.scientific_evidence_runtime import enabled
    if (config.get('source_root') is not None and
            enabled(config['source_root'],request['source'],formal_current=True)
            and current.has_current_plan(config,packet)):
        return current.capture_history(config,packet)
    return packet


def original_transport(output, request=None):
    transport = json.loads(authority.read(Path(output) / 'authority-transport.json', limit=2000000))
    if set(transport) != {'event', 'packet'}:
        raise ValueError('FORMAL_ORIGINAL_TRANSPORT_REQUIRED')
    packet = transport['packet']
    from orchestrator.current_scientific_input import is_current
    base={'version','trigger','scientific_decision_artifacts','formal_request','recorded_changes'}
    if (not isinstance(packet,dict) or set(packet) not in (base,base|{'scientific_change_history'})
            or packet['version'] != 1 or packet['trigger'] != 'registered-formal-scientific-decision'
            or ('scientific_change_history' in packet and not is_current(packet))):
        raise ValueError('FORMAL_ORIGINAL_PACKET_REQUIRED')
    saved = checked_request(packet['formal_request'])
    if (transport['event'] != event(saved) or request is not None and saved != request
            or packet['scientific_decision_artifacts'] != {
                'version': 3, 'action': saved['action'], 'subject': saved['subject'],
                'bindings_sha256': digest(saved['bindings'])}):
        raise ValueError('FORMAL_ORIGINAL_REQUEST_CHANGED')
    return transport


def verify_original_decision(root, decision_path, *, action, subject, bindings,
                             original_client, expected_transition=None, source=None):
    """Read-only proof usable by protected capture; local seals alone cannot pass."""
    if not callable(original_client):
        raise ValueError('ORIGINAL_PROTECTED_MODEL_REPLIES_REQUIRED')
    decision_path = Path(decision_path)
    decision = authority.verify(root, decision_path, action=action, subject=subject,
        bindings=bindings, expected_transition=expected_transition, allow_deferred=True)
    directory = decision_path.parent
    transport = original_transport(directory.parent)
    request = transport['packet']['formal_request']
    if (request['action'] != action or request['subject'] != subject or request['bindings'] != bindings
            or source is not None and request['source'] != source
            or expected_transition is not None and request['transition'] != expected_transition):
        raise ValueError('FORMAL_ORIGINAL_DECISION_BINDING_CHANGED')
    reader = BrokerStages('protected-originals', transport['event'], transport['packet'],
                          client=original_client, recovery=True)
    for stage, family, artifact, provenance_key, label in (
            ('continuation', 'codex', 'judgment.json', 'author_provenance', 'scientific_decision'),
            ('review', 'claude', 'review.json', 'reviewer_provenance', 'scientific_decision_review')):
        answer, receipt = reader.call(stage, '')
        if authority.read(directory / artifact) != artifact_files(answer, [artifact])[artifact].encode():
            raise ValueError('FORMAL_ORIGINAL_REPLY_MISMATCH')
        if json.loads(authority.read(directory / (label + '.provider-receipt.json'))) != receipt:
            raise ValueError('FORMAL_ORIGINAL_PROVIDER_RECEIPT_CHANGED')
        provenance = json.loads(authority._artifact(directory, decision[provenance_key]))
        if provenance != _provenance(receipt, family, transport['event'], transport['packet']):
            raise ValueError('FORMAL_ORIGINAL_PROVIDER_ATTRIBUTION_CHANGED')
    return decision


def _application_request(root, request):
    application = request['application']
    if application is None:
        return
    from orchestrator.campaign import decision_request
    prepared = decision_request(root, application['experiment'], request['action'], application['proposal'])
    if any(request[key] != prepared[key] for key in ('action', 'subject', 'bindings', 'transition')):
        raise ValueError('FORMAL_CAMPAIGN_APPLICATION_INPUTS_CHANGED')


def execute_formal_decision(config, request, output, *, recover_from=None, client=request_broker):
    """Run the existing author, opposing reviewer and decision seal, never a job."""
    from orchestrator.scientific_decision import execute, prepare
    if type(config.get('controller_uid')) is not int or config['controller_uid'] <= 0 or os.getuid() != config['controller_uid']:
        raise ValueError('NONROOT_CONTROLLER_IDENTITY_REQUIRED')
    request = checked_request(deepcopy(request))
    root = scientific_root(config, request)
    authority.decision_context(root, action=request['action'], subject=request['subject'], bindings=request['bindings'])
    _application_request(root, request)
    output = Path(output).absolute()
    state = Path(config['state']).absolute()
    if output.parent != state / 'formal-decisions' or not re.fullmatch('[A-Za-z0-9_-]{1,100}', output.name):
        raise ValueError('PRIVATE_FORMAL_DECISION_OUTPUT_REQUIRED')
    from orchestrator.operations_report import private_root
    private_root(state)
    private_root(output.parent)
    prior = Path(recover_from).absolute() if recover_from is not None else None
    if prior is not None and (output.exists() or output.is_relative_to(prior)):
        raise ValueError('FRESH_FORMAL_RECOVERY_PROJECTION_REQUIRED')
    read_only = _recovery_mode(output, recover_from)
    failure = output.parent / (output.name + '.input-preflight-failure.json')
    if not read_only and failure.exists():
        raise ValueError('SCIENTIFIC_PREFLIGHT_REFUSAL_REQUIRES_RECONCILIATION')
    saved = prior if prior is not None else output if output.exists() else None
    packet = original_transport(saved, request)['packet'] if saved is not None else _packet(config, request)
    stages = FormalDecisionStages(config['broker_socket'], event(request), packet, client=client, recovery=read_only,
        source_root=config['source_root'], source=request['source'], evidence_config=config)
    from orchestrator.formal_input import evidence_for_packet
    evidence = evidence_for_packet(config['source_root'],packet,request['source'])
    instruction = (request['request'] + '\nRequired APPLY transition: ' + json.dumps(request['transition']) +
                   '. DEFER must preserve the same from state and use to=DEFERRED, with clear reconsideration.')
    if not read_only:
        from orchestrator.research_task_authority import preserve_preflight_failure
        try:
            prepared = prepare(root, action=request['action'], subject=request['subject'],
                bindings=request['bindings'], evidence=evidence, request=instruction, max_rounds=1)
            measured = stages.preflight_bodies(root, prepared['body'], 1)
        except ValueError as error:
            preserve_preflight_failure(output, error, source=request['source'], packet=packet)
            raise
        immutable(output.parent / (output.name + '.input-preflight.json'), encoded({
            'schema': 'formal-decision-input-preflight/v2', 'source': request['source'],
            'packet_sha256': hashlib.sha256(encoded(packet)).hexdigest(), 'stages': measured,
            'max_rounds': 1, 'provider_calls': 0, 'admissions': 0}))
    with _turn_guard(config, event(request), client, read_only=read_only):
        receipt = execute(SimpleNamespace(ROOT=root), action=request['action'], subject=request['subject'],
            bindings=request['bindings'], evidence=evidence, request=instruction,
            output=output, max_rounds=1, stage_runner=stages)
    decision_path = output / receipt['decision']
    decision = verify_original_decision(root, decision_path, action=request['action'],
        subject=request['subject'], bindings=request['bindings'],
        original_client=lambda socket, operation, body: client(config['broker_socket'], operation, body),
        source=request['source'])
    expected = request['transition'] if decision['decision'] == 'APPLY' else {
        'from': request['transition']['from'], 'to': 'DEFERRED'}
    if decision['transition'] != expected:
        raise ValueError('FORMAL_DECISION_TRANSITION_REQUIRED')
    if prior is not None:
        if authority.read(prior / 'request.json') != authority.read(output / 'request.json'):
            raise ValueError('FORMAL_RECOVERY_ORIGINAL_REQUEST_CHANGED')
        immutable(output / 'recovery.json', encoded({'status': 'RECOVERED_ORIGINAL_FORMAL_DECISION',
            'original_request_sha256': hashlib.sha256(authority.read(prior / 'request.json')).hexdigest(),
            'new_model_calls': 0, 'new_review': False, 'original_preserved': True}))
    return {**receipt, 'decision_path': str(decision_path), 'actor': decision['actor'],
            'new_model_calls': 0 if saved is not None or receipt['recovered_without_model_calls'] else 2,
            'application_status': 'NOT_APPLIED', 'scientific_execution': False}


def apply_formal_decision(config, request, decision_path, *, client=request_broker):
    """Apply only the existing campaign transaction after original review verification."""
    if os.getuid() != config['controller_uid'] or config['controller_uid'] <= 0:
        raise ValueError('NONROOT_CONTROLLER_IDENTITY_REQUIRED')
    checked_request(request)
    if request['application'] is None or request['workspace'] is None:
        raise ValueError('PRIVATE_CAMPAIGN_APPLICATION_REQUIRED')
    root = scientific_root(config, request)
    _application_request(root, request)
    original_transport(Path(decision_path).parent.parent, request)
    decision = verify_original_decision(root, decision_path, action=request['action'],
        subject=request['subject'], bindings=request['bindings'],
        original_client=lambda socket, operation, body: client(config['broker_socket'], operation, body),
        source=request['source'], expected_transition=request['transition'])
    if decision['decision'] != 'APPLY':
        raise ValueError('DEFERRED_FORMAL_DECISION_NOT_APPLICABLE')
    from orchestrator.research_catalog import linked_change
    linked_change(config, {'change_request': request['change_request']})
    from orchestrator.campaign_lifecycle import apply_decision
    application = request['application']
    return apply_decision(root, application['experiment'], request['action'], decision_path,
                          application['proposal'])
