"""Finite P001 preparation authority through the existing scientific stages.

Two original provider replies produce the existing reviewed decision seal. The
seal is a recorded disposition, not a third model invocation or a launch grant.
Catalog dispatch rechecks both replies through the protected read-only broker.
"""
import argparse
import ast
from contextlib import contextmanager
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import sqlite3
from types import SimpleNamespace

from orchestrator import scientific_authority as authority
from orchestrator.handover_coordinator import digest
from orchestrator.handover_runtime import configuration, request_broker
from orchestrator.hosted_campaign import BrokerStages, artifact_files
from orchestrator.hosted_cycle import encoded, immutable

ACTION = 'authorize_research_task'
ADAPTER = 'protected-scientific-decision-v1'
BRANCH = 'astra/infrastructure-milestone-record'
EVIDENCE_VERSION = 2
HOSTED_PRESENTATION_VERSION = 1
ORIGINAL_TRANSPORT_MAXIMUM = 1500000


def evidence_version(root, source):
    """Choose from the exact checked source module, never the supplied packet."""
    from orchestrator.remote_supervisor import checked_source
    root = checked_source(root, source)
    raw = authority.read(Path(root) / 'orchestrator/research_task_authority.py')
    tree = ast.parse(raw)
    bindings = [node for node in ast.walk(tree) if isinstance(node, ast.Name)
                and node.id == 'EVIDENCE_VERSION' and isinstance(node.ctx, ast.Store)]
    definitions = [node for node in tree.body if isinstance(node, ast.Assign)
        and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name)
        and node.targets[0].id == 'EVIDENCE_VERSION']
    if not bindings:
        # Older immutable source modules predate the marker and have exactly v1.
        return 1
    if (len(bindings) != 1 or len(definitions) != 1
            or not isinstance(definitions[0].value, ast.Constant)
            or type(definitions[0].value.value) is not int or definitions[0].value.value != 2):
        raise ValueError('SOURCE_BOUND_AUTHORITY_EVIDENCE_VERSION_REQUIRED')
    return 2



def hosted_presentation_version(root, source):
    """Separate source profile; legacy evidencev2 and courier bytes stay unchanged."""
    from orchestrator.remote_supervisor import checked_source
    root = checked_source(root, source)
    tree = ast.parse(authority.read(Path(root) / 'orchestrator/research_task_authority.py'))
    bindings = [n for n in ast.walk(tree) if isinstance(n, ast.Name)
                and n.id == 'HOSTED_PRESENTATION_VERSION' and isinstance(n.ctx, ast.Store)]
    definitions = [n for n in tree.body if isinstance(n, ast.Assign)
        and len(n.targets) == 1 and isinstance(n.targets[0], ast.Name)
        and n.targets[0].id == 'HOSTED_PRESENTATION_VERSION']
    if not bindings: return 0
    if (len(bindings) != 1 or len(definitions) != 1
            or not isinstance(definitions[0].value, ast.Constant)
            or type(definitions[0].value.value) is not int or definitions[0].value.value != 1):
        raise ValueError('SOURCE_BOUND_HOSTED_PRESENTATION_VERSION_REQUIRED')
    return 1


def evidence_for_packet(root, packet, source):
    version = evidence_version(root, source)
    if version == 1:
        return {'installed-request-and-evidence.json': json.dumps(packet, sort_keys=True)}
    from orchestrator.hosted_context import same_prompt_reference
    reference = same_prompt_reference(encoded(packet), source)
    return {'installed-request-and-evidence.json': json.dumps(reference, sort_keys=True)}


def _instruction(bindings):
    continuing = ('Decide whether this exact versioned formal operation is eligible under the current '
        'selected ISLES24 charter and supplied reviewed investigator selection, or the exact protected '
        'template and wake for a new investigator. A template request is attributed to the controller service, '
        'not a scientific model judgment. This is the existing '
        'campaign workflow, not a generic executor. A code/specification/protocol artifact remains a '
        'proposal until its separate applicable approval; task eligibility grants no scientific launch, '
        'data access, spending, publication, main merge, activation or release of a human stop. '
        'Assess exact artifact references, predecessor dispositions, affected versions and all linked '
        'change criticism. Use transition PROPOSED to ELIGIBLE for APPLY or PROPOSED to DEFERRED for DEFER. '
        'Give a substantive reason and reconsideration conditions; do not perform the selected science.')
    return continuing if 'operation_sha256' in bindings else (
        'Decide whether this exact installed finite P001 preparation task is eligible. '
        'Only discussion or readiness analysis of the supplied evidence is in scope. '
        'Do not authorize code generation or execution, patient processing, new data access, '
        'spending, publication, main merge, activation or release of a human stop. '
        'Assess predecessor dispositions, affected versions and all linked change criticism. '
        'Use transition PROPOSED to ELIGIBLE for APPLY or PROPOSED to DEFERRED for DEFER. '
        'State the useful bounded task and reconsideration conditions; do not perform its science.')


def _preflight(root, source, packet, subject, bindings, stages):
    from orchestrator.scientific_decision import prepare
    if evidence_version(root, source) != 2:
        raise ValueError('FRESH_AUTHORITY_REQUIRES_INPUT_EVIDENCE_V2')
    transport_raw = _transport_bytes(stages.event, packet)
    prepared = prepare(root, action=ACTION, subject=subject, bindings=bindings,
        evidence=evidence_for_packet(root, packet, source), request=_instruction(bindings), max_rounds=1,
        hosted_policy_source=stages.hosted_policy_source(root))
    measured = stages.preflight_bodies(root, prepared['body'], 1)
    return {'schema': 'research-authority-input-preflight/v2', 'source': source,
        'packet_sha256': hashlib.sha256(encoded(packet)).hexdigest(), 'max_rounds': 1,
        'stages': measured, 'original_transport_bytes': len(transport_raw),
        'original_transport_sha256': hashlib.sha256(transport_raw).hexdigest(),
        'provider_calls': 0, 'admissions': 0}


def preflight(config, entry, *, client=None):
    """Read-only exact two-role projection; client is deliberately never called."""
    root, subject, bindings = _identity(config, entry)
    packet = _packet(config, entry, bindings)
    stages = DecisionStages(config['broker_socket'], _event(entry, bindings), packet,
        source_root=root,source=entry['source'],evidence_config=config)
    return _preflight(root, entry['source'], packet, subject, bindings, stages)


def preserve_preflight_failure(output, error, *, source, packet):
    from orchestrator.operations_report import private_root
    output = Path(output).absolute()
    parent = private_root(output.parent)
    path = parent / (output.name + '.input-preflight-failure.json')
    immutable(path, encoded({'schema': 'scientific-input-preflight-failure/v1', 'source': source,
        'packet_sha256': hashlib.sha256(encoded(packet)).hexdigest(), 'status': 'PRESERVED_PREFLIGHT_REFUSAL_REQUIRES_RECONCILIATION',
        'exception': type(error).__name__, 'reason': str(error), 'measurement': getattr(error, 'measurement', None),
        'provider_calls': 0, 'admissions': 0, 'automatic_retry': False}))


@contextmanager
def _turn_guard(config, event, client, *, read_only):
    """Reuse shared pause/admission semantics: an admitted turn may finish."""
    if read_only:
        yield
        return
    from orchestrator.operations_report import private_root
    state = Path(config['state'])
    database = state / 'coordinator.sqlite'
    if database.is_symlink() or not database.is_file():
        raise ValueError('EXISTING_CONTROLLER_STATE_REQUIRED')
    private_root(state)
    # Read the existing Coordinator control row without initializing a database
    # or replacing a missing control table with the default unpaused state.
    database_connection = sqlite3.connect(database.absolute().as_uri() + '?mode=ro', uri=True)
    try:
        with (state / 'branch.lock').open('a') as writer:
            try:
                fcntl.flock(writer, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError as error:
                raise ValueError('CONTROLLER_WRITER_BUSY') from error
            with (state / 'admission.lock').open('a') as gate:
                fcntl.flock(gate, fcntl.LOCK_EX)
                try:
                    control = database_connection.execute(
                        'SELECT revision,paused FROM controls WHERE singleton=1').fetchone()
                except sqlite3.Error as error:
                    raise ValueError('EXISTING_CONTROLLER_CONTROLS_REQUIRED') from error
                if control is None or control[1] not in (0, 1):
                    raise ValueError('EXISTING_CONTROLLER_CONTROLS_REQUIRED')
                if control[1]:
                    raise ValueError('SCIENTIFIC_AUTHORITY_SYSTEM_PAUSED')
                admitted = client(config['broker_socket'], 'admit_server', event)
                if admitted.get('status') != 'ADMITTED':
                    raise ValueError('SCIENTIFIC_AUTHORITY_ADMISSION_BLOCKED')
            # Pause remains responsive through admission.lock. As in Runtime,
            # it blocks the next turn, not this admitted review/disposition.
            yield
    finally:
        database_connection.close()


def _recovery_mode(output, recover_from):
    """A directory is not a completed attempt or permission to bypass admission."""
    if recover_from is not None:
        return True
    output = Path(output)
    if not output.exists() and not output.is_symlink():
        return False
    receipt = output/'receipt.json'
    if output.is_symlink() or receipt.is_symlink() or not receipt.is_file():
        raise ValueError('PARTIAL_AUTHORITY_OUTPUT_REQUIRES_EXPLICIT_ORIGINAL_RECOVERY')
    # Actual scientific_decision.execute rechecks the original receipt/decision.
    # The transport is original-read-only even if a supplied receipt is invalid.
    authority.read(receipt)
    return True


def _identity(config, entry):
    from orchestrator.research_catalog import core, validate_entry
    from orchestrator.remote_supervisor import checked_source
    validate_entry(entry, entry['request']['task']['task_id'])
    if (entry['source'] != config['source'] or
            Path(entry['source_root']).absolute() != Path(config['source_root']).absolute()):
        raise ValueError('CURRENT_INSTALLED_RESEARCH_AUTHORITY_SOURCE_REQUIRED')
    root = checked_source(entry['source_root'], entry['source'])
    subject = entry['request']['task']['task_id']
    from orchestrator.hosted_campaign_task import task_contract
    contract=task_contract(entry['request']['task'])
    bindings = {'catalog_core_sha256': digest(core(entry)), 'source': entry['source'],
                'experiment': contract['experiment'], 'mode': contract['mode']}
    if contract['version']==2:
        bindings['operation_sha256']=contract['operation_sha256']
    if entry['request']['task'].get('schema') == 'investigator-task/v1':
        bindings['template_sha256'] = entry['request']['task']['template_sha256']
    authority.decision_context(root, action=ACTION, subject=subject, bindings=bindings)
    return root, subject, bindings


def _evidence(config, entry):
    request = entry['request']
    if request['task'].get('schema') in ('continuing-research-task/v1','prospective-research-task/v1','protocol-proposal-task/v1','investigator-task/v1'):
        from orchestrator.continuing_research import read_evidence
        return read_evidence(config,request)
    return configuration(request['evidence_file'], maximum=750000,
                         expected_sha256=request['evidence_sha256'],
                         private_gid=config['controller_gid'])


def _event(entry, bindings):
    return {'turn_id': digest({'action': ACTION, 'bindings': bindings}), 'attempt': '1',
            'source': entry['source'], 'branch': BRANCH, 'kind': 'astra_turn'}


def _decision_contract(bindings):
    contract={'version':1,'action':ACTION,'experiment':bindings['experiment'],'mode':bindings['mode']}
    if 'operation_sha256' in bindings:
        contract.update(version=2,operation_sha256=bindings['operation_sha256'])
    return contract


def _packet(config, entry, bindings):
    from orchestrator.change_requests import load
    from orchestrator.research_catalog import core
    change = entry['change_request']
    state = load(Path(config['change_request_store']) / change['request_id'])
    if not any(e['event'] == 'APPLIED' and e['identity'] == change['applied_event']
               for e in state['events']):
        raise ValueError('RESEARCH_AUTHORITY_APPLIED_CHANGE_REQUIRED')
    evidence = _evidence(config, entry)
    from orchestrator.linked_disposition_input import enabled, prepare_primary_for_packet
    if enabled(config['source_root'], entry['source']):
        state = prepare_primary_for_packet(state, evidence, entry['source'], change['applied_event'])
    packet = {'version': 1, 'trigger': 'installed-research-eligibility',
            'scientific_decision_artifacts': _decision_contract(bindings),
            'reviewer_evidence': {'catalog_core': core(entry), 'input_evidence': evidence},
            'recorded_changes': state}
    from orchestrator.hosted_context import selected_history_profile
    if selected_history_profile(config['source_root'], entry['source']) == 1:
        from orchestrator.disposition_context import capture_current_history
        packet = capture_current_history(config, packet)
    from orchestrator.scientific_context_references import has_references
    from orchestrator.current_scientific_input import is_current
    if has_references(packet) and not is_current(packet):
        raise ValueError('SCIENTIFIC_CONTEXT_REVIEWED_CURRENT_PLAN_REQUIRED')
    return packet



def _transport_bytes(event, packet):
    """Match the existing private immutable/packet bound before any admission."""
    if not isinstance(event, dict) or not isinstance(packet, dict):
        raise ValueError('RESEARCH_AUTHORITY_TYPED_TRANSPORT_REQUIRED')
    raw = encoded({'event': event, 'packet': packet})
    if len(raw) > ORIGINAL_TRANSPORT_MAXIMUM or len(encoded(packet)) > ORIGINAL_TRANSPORT_MAXIMUM:
        raise ValueError('RESEARCH_AUTHORITY_ORIGINAL_TRANSPORT_BOUND')
    return raw


def _original_transport(config, entry, bindings, output, *, client=request_broker):
    return _authenticated_transport(config, entry, bindings, output, client=client)[0]


def _authenticated_transport(config, entry, bindings, output, *, client=request_broker):
    """Original inputs and their native retrieval, authenticated once per call."""
    retrieval = None
    from orchestrator.research_catalog import core
    raw = authority.read(Path(output) / 'authority-transport.json', limit=ORIGINAL_TRANSPORT_MAXIMUM)
    transport = json.loads(raw)
    if set(transport) != {'event', 'packet'} or transport['event'] != _event(entry, bindings):
        raise ValueError('RESEARCH_AUTHORITY_ORIGINAL_TURN_CHANGED')
    packet = transport['packet']
    exact = _transport_bytes(transport['event'], packet)
    if hosted_presentation_version(config['source_root'], entry['source']) == 1 and raw != exact:
        raise ValueError('RESEARCH_AUTHORITY_ORIGINAL_TRANSPORT_ENCODING_CHANGED')
    original_keys = {'version', 'trigger', 'scientific_decision_artifacts',
                     'reviewer_evidence', 'recorded_changes'}
    if 'scientific_change_history' in packet:
        from orchestrator.hosted_context import selected_history_profile
        from orchestrator.disposition_context import validate_current_history
        if selected_history_profile(config['source_root'], entry['source']) != 1:
            raise ValueError('SELECTED_HISTORY_SOURCE_PROFILE_REQUIRED')
        from orchestrator import current_scientific_input
        if not current_scientific_input.is_current(packet):
            validate_current_history(packet, entry['source'])
        from orchestrator.disposition_context import authenticate_report_references
        retrieval = authenticate_report_references(config, packet, entry['source'], original_client=client)
        original_keys.add('scientific_change_history')
    if (set(packet) != original_keys or
            packet['version'] != 1 or packet['trigger'] != 'installed-research-eligibility' or
            packet['scientific_decision_artifacts'] != _decision_contract(bindings) or
            packet['reviewer_evidence'] != {'catalog_core': core(entry), 'input_evidence': _evidence(config, entry)}):
        raise ValueError('RESEARCH_AUTHORITY_ORIGINAL_PACKET_CHANGED')
    evidence = json.loads(authority.read(Path(output) / 'evidence.json', limit=1000000))
    if evidence != evidence_for_packet(config['source_root'], packet, entry['source']):
        raise ValueError('RESEARCH_AUTHORITY_SOURCE_BOUND_EVIDENCE_CHANGED')
    return transport, retrieval


def _provenance(receipt, family, event, packet):
    session = receipt.get('session_id')
    if not isinstance(session, str) or not re.fullmatch('[A-Za-z0-9_-]{6,128}', session):
        raise ValueError('ORIGINAL_PROVIDER_SESSION_REQUIRED')
    if (receipt.get('stage') != ('review' if family == 'claude' else 'continuation') or
            receipt.get('actual_model') not in (None, receipt['requested_model'])):
        raise ValueError('ORIGINAL_PROVIDER_MODEL_OR_STAGE_CHANGED')
    # model_used is explicitly the requested identity. Actual resolution remains
    # separate, including null when the original protocol did not report it.
    return {'family_effective': family, 'exit_class': 'ok', 'ci': False,
            'runner': {'adapter': ADAPTER}, 'run_id': session,
            'model_used': receipt['requested_model'],
            'requested_model': receipt['requested_model'], 'actual_model': receipt.get('actual_model'),
            'model_evidence': receipt.get('model_evidence'),
            'model_receipt_sha256': hashlib.sha256(encoded(receipt)).hexdigest(),
            'operating_context_sha256': receipt['operating_context_sha256'],
            'original_protocol_private': True, 'event': event,
            'packet_sha256': hashlib.sha256(encoded(packet)).hexdigest()}


class DecisionStages(BrokerStages):
    """Only the existing scientific decision author's and reviewer's artifacts."""
    def hosted_policy_source(self, root):
        return self.event['source'] if hosted_presentation_version(root, self.event['source']) == 1 else None

    @staticmethod
    def prompt(body, names, *, evidence_enabled=False):
        return ('Return ONE JSON object with exactly these filenames as keys: ' + json.dumps(names)
                + '. Each value is the JSON object for that decision file, not a JSON-encoded string. '
                'The authenticated runner preserves this structured output and serializes each file deterministically. '
                + ('Only bound read-only scientific evidence tools are permitted; no actions. ' if evidence_enabled
                   else 'Do not use tools. ')
                + 'Keep each file below 30000 UTF-8 bytes and the whole reply below 80000.\n' + body)

    def preflight_bodies(self, root, body, max_rounds):
        if self.recovery: return []
        _transport_bytes(self.event, self.packet)
        # This protected adapter has exactly two stage slots; do not invent a
        # generic second-round admission route that it cannot actually execute.
        if type(max_rounds) is not int or max_rounds != 1:
            raise ValueError('FINITE_HOSTED_SCIENTIFIC_DECISION_ROUND_REQUIRED')
        from orchestrator.scientific_decision import projected_bodies
        from orchestrator.hosted_context import compose_input, measure_input, context_bytes
        from orchestrator.scientific_output import contract as output_contract
        rows = []
        for row in projected_bodies(body, max_rounds):
            options = self.evidence_options(row['stage'], root=root)
            prompt, context = compose_input(root, encoded(self.packet),
                self.prompt(row['body'], row['names'],evidence_enabled=bool(options)),
                verified_source=self.event['source'], family=row['family'], output_format='json',
                prepared_prompt=False, **options)
            rows.append({**measure_input(prompt, row['family'], row['stage'], task_state=self.packet, output_contract=output_contract(self.packet, row['stage'])), 'round': row['round'],
                'projection': 'WORST_CASE_BOUNDED_ARTIFACT_NOT_MODEL_OUTPUT',
                'operating_context_sha256': hashlib.sha256(context_bytes(root,context,self.event['source'])).hexdigest()})
        return rows

    def __call__(self, sc, directory, family, stage, body, names):
        index = len(self.completed)
        if (index >= 2 or (family, stage, names) !=
                (('codex', 'scientific_decision', ['judgment.json']),
                 ('claude', 'scientific_decision_review', ['review.json']))[index]):
            raise ValueError('FINITE_SCIENTIFIC_DECISION_STAGE_REQUIRED')
        options = self.evidence_options(('continuation','review')[index])
        prompt = self.prompt(body, names, evidence_enabled=bool(options))
        immutable(Path(directory).parent / 'authority-transport.json',
                  _transport_bytes(self.event, self.packet))
        answer, receipt = self.call(('continuation', 'review')[index], prompt)
        files = artifact_files(answer, names)
        provenance = _provenance(receipt, family, self.event, self.packet)
        immutable(Path(directory) / (stage + '.provider-receipt.json'), encoded(receipt))
        for name, content in files.items():
            immutable(Path(directory) / name, content.encode())
        return provenance


def _verify(config, entry, decision_path, *, client=request_broker):
    root, subject, bindings = _identity(config, entry)
    decision_path = Path(decision_path).absolute()
    decision = authority.verify(root, decision_path, action=ACTION, subject=subject,
                                bindings=bindings, allow_deferred=True)
    expected = {'from': 'PROPOSED', 'to': 'ELIGIBLE' if decision['decision'] == 'APPLY' else 'DEFERRED'}
    if decision['transition'] != expected:
        raise ValueError('FINITE_RESEARCH_AUTHORITY_TRANSITION_REQUIRED')
    directory = decision_path.parent
    transport, retrieval = _authenticated_transport(config, entry, bindings, directory.parent, client=client)
    packet = transport['packet']
    reader = BrokerStages(config['broker_socket'], transport['event'], packet, client=client, recovery=True)
    presented = hosted_presentation_version(root, entry['source']) == 1
    if presented:
        from orchestrator.scientific_decision import prepare, review_body
        prepared = prepare(root, action=ACTION, subject=subject, bindings=bindings,
            evidence=evidence_for_packet(root, packet, entry['source']), request=_instruction(bindings),
            max_rounds=1, hosted_policy_source=entry['source'])
        if json.loads(authority.read(directory.parent / 'request.json')) != prepared['original']:
            raise ValueError('RESEARCH_AUTHORITY_ORIGINAL_PRESENTATION_CHANGED')
    for stage, family, artifact, provenance_key, label in (
            ('continuation', 'codex', 'judgment.json', 'author_provenance', 'scientific_decision'),
            ('review', 'claude', 'review.json', 'reviewer_provenance', 'scientific_decision_review')):
        answer, receipt = reader.call(stage, '')  # stage_status only, never a model request
        if receipt.get('stage') != stage:
            raise ValueError('RESEARCH_AUTHORITY_ORIGINAL_STAGE_CHANGED')
        if presented:
            from orchestrator.hosted_context import compose_input, context_bytes
            body = (prepared['body'] if stage == 'continuation' else
                    review_body(prepared['body'], authority.read(directory / 'judgment.json')))
            from orchestrator.scientific_evidence_runtime import controller_options, _captured_options
            if retrieval is not None and retrieval['schema'] == 'authenticated-current-scientific-retrieval/v1':
                # Both original role inputs consumed the same immutable capture.
                # Reuse its authenticated descriptor, not a global/stale verdict.
                options = _captured_options(config, entry['source'], packet, stage, retrieval['capture'])
            else:
                options = controller_options(config, root, entry['source'], packet, stage, original_client=client)
            expected_input, expected_context = compose_input(root, encoded(packet),
                DecisionStages.prompt(body, [artifact],evidence_enabled=bool(options)), verified_source=entry['source'],
                family=family, output_format='json', prepared_prompt=False, **options)
            if (receipt.get('input_sha256') != hashlib.sha256(expected_input.encode()).hexdigest()
                    or receipt.get('operating_context_sha256') != hashlib.sha256(context_bytes(root,expected_context,entry['source'])).hexdigest()):
                raise ValueError('RESEARCH_AUTHORITY_ORIGINAL_PRESENTATION_CHANGED')
        if authority.read(directory / artifact) != artifact_files(answer, [artifact])[artifact].encode():
            raise ValueError('RESEARCH_AUTHORITY_ORIGINAL_REPLY_MISMATCH')
        original = json.loads(authority.read(directory / (label + '.provider-receipt.json')))
        if original != receipt:
            raise ValueError('RESEARCH_AUTHORITY_ORIGINAL_RECEIPT_CHANGED')
        provenance = json.loads(authority._artifact(directory, decision[provenance_key]))
        if provenance != _provenance(receipt, family, transport['event'], packet):
            raise ValueError('RESEARCH_AUTHORITY_PROVIDER_ATTRIBUTION_CHANGED')
    review = json.loads(authority.read(directory/'review.json'))
    if not isinstance(review, dict) or review.get('verdict') not in ('APPROVE','REVISE'):
        raise ValueError('RESEARCH_AUTHORITY_ORIGINAL_REVIEW_VERDICT_REQUIRED')
    return {**decision, '_opposing_review_verdict': review['verdict']}


def verify_eligibility(config, entry, *, client=request_broker):
    """Catalog seam: local seals alone never establish provider-backed authority."""
    if entry['request']['task'].get('schema') == 'investigator-task/v1':
        from orchestrator.investigator_wakes import verify_entry
        verify_entry(config, entry, client)
    reference = entry['eligibility']
    decision = _verify(config, entry, reference['path'], client=client)
    if decision['_decision_sha256'] != reference['sha256']:
        raise ValueError('RESEARCH_AUTHORITY_EXACT_DECISION_REQUIRED')
    return {'status': 'ELIGIBLE' if decision['decision'] == 'APPLY' else 'DEFERRED',
            'entry_sha256': digest(entry), 'reference_sha256': reference['sha256'],
            'source': entry['source'], 'actor': decision['actor'], 'review_status': decision['_opposing_review_verdict'],
            'rationale': decision['rationale']}


def execute(config, entry, output, *, recover_from=None, client=request_broker):
    """Record a decision; never install a catalog entry or dispatch its research.

    A prospective entry may use the desired decision path and an all-zero digest:
    eligibility is excluded from the core. Install only the returned actual pin.
    Explicit recovery writes a fresh projection from original broker replies;
    interrupted originals are preserved and an unavailable reply blocks recovery.
    """
    from orchestrator.scientific_decision import execute as decide
    if (type(config.get('controller_uid')) is not int or config['controller_uid'] <= 0 or
            os.getuid() != config['controller_uid']):
        raise ValueError('NONROOT_CONTROLLER_IDENTITY_REQUIRED')
    root, subject, bindings = _identity(config, entry)
    event = _event(entry, bindings)
    output = Path(output).absolute()
    read_only = _recovery_mode(output, recover_from)
    if not read_only and (output.parent / (output.name + '.input-preflight-failure.json')).exists():
        raise ValueError('SCIENTIFIC_PREFLIGHT_REFUSAL_REQUIRES_RECONCILIATION')
    packet = None
    if recover_from is not None:
        prior = Path(recover_from).absolute()
        if output.exists() or output.is_relative_to(prior):
            raise ValueError('FRESH_AUTHORITY_RECOVERY_PROJECTION_REQUIRED')
        packet = _original_transport(config, entry, bindings, prior, client=client)['packet']
    elif output.exists():
        packet = _original_transport(config, entry, bindings, output, client=client)['packet']
    if packet is None:
        if entry['request']['task'].get('schema') == 'investigator-task/v1':
            from orchestrator.investigator_wakes import verify_entry
            verify_entry(config, entry, client)
        packet = _packet(config, entry, bindings)
    stages = DecisionStages(config['broker_socket'], event, packet, client=client,
                            recovery=read_only,source_root=root,source=entry['source'],evidence_config=config)
    if not read_only:
        try:
            input_preflight = _preflight(root, entry['source'], packet, subject, bindings, stages)
        except ValueError as error:
            preserve_preflight_failure(output, error, source=entry['source'], packet=packet)
            raise
        immutable(output.parent / (output.name + '.input-preflight.json'), encoded(input_preflight))
    with _turn_guard(config, event, client, read_only=read_only):
        receipt = decide(SimpleNamespace(ROOT=root), action=ACTION, subject=subject, bindings=bindings,
            evidence=evidence_for_packet(root, packet, entry['source']), request=_instruction(bindings),
            output=output, max_rounds=1, stage_runner=stages)
    if recover_from is not None and authority.read(prior / 'request.json') != authority.read(output / 'request.json'):
        raise ValueError('AUTHORITY_RECOVERY_ORIGINAL_REQUEST_CHANGED')
    decision = _verify(config, entry, output / receipt['decision'], client=client)
    if recover_from is not None:
        immutable(output / 'recovery.json', encoded({'status': 'RECOVERED_ORIGINAL_MODEL_DECISION',
            'original_request_sha256': hashlib.sha256(authority.read(prior / 'request.json')).hexdigest(),
            'new_model_calls': 0, 'new_review': False, 'original_preserved': True}))
    return {**receipt, 'eligibility': {'path': str(output / receipt['decision']),
            'sha256': decision['_decision_sha256']},
            'new_model_calls': 0 if recover_from is not None or receipt['recovered_without_model_calls'] else 2,
            'disposition_kind': 'EXISTING_REVIEWED_DECISION_SEAL', 'catalog_installed': False,
            'research_dispatched': False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', type=Path, required=True)
    parser.add_argument('--entry', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--recover-from', type=Path)
    args = parser.parse_args()
    config = configuration(args.config)
    entry = configuration(args.entry, private_gid=config['controller_gid'])
    print(json.dumps(execute(config, entry, args.output, recover_from=args.recover_from), indent=2))


if __name__ == '__main__':
    main()
