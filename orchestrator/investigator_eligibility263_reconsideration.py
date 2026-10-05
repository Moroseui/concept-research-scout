"""One operator-authorized reconsideration of the sealed eligibility263 DEFER.

This is a fixed exception, not a general retry mechanism. The native protected
reservation consumes the authorization once across source, template and day.
"""
import hashlib
import json
import sqlite3
from pathlib import Path

from orchestrator import investigator_eligibility247_replacement as previous
from orchestrator.handover_coordinator import digest
from orchestrator.hosted_cycle import encoded

KIND = 'ELIGIBILITY263_RECONSIDERATION'
REQUEST = '7b39364ecb0929c54e77f2a630dde9eceeeb1c7852b32cd09ccf4479dced0d1e'
AUTHORIZED = 'e9e62ed3cf6b47f75f4de7501155ebe0f5b2ff212f8981f82b419279a3fab059'
OPERATOR = '46b34da2245357f97eb9b4675677c3886f632eada5f9dd0cfe79f34a9c32e9e7'
DECISION_PACKET = 'dedfa8578f5f5b31b3bbefcaa2f3b8f2c4dda01449c401d8c78918cf62cb4358'
ORIGINAL_WAKE = 'a6fca83a22673f608712c383386767f224c202877eb72016127e7512e09bc853'
ORIGINAL_SOURCE = 'dd6f815c7bd36e605a74be5aeea8b8546f6712b1'
PACKET = 'f33bd26ddf1326defef983b031249d24688409c4fe23240359818ce9f48200bb'
DECISION = '0e762f63dfd778c473be9e0ead69b4733f025a844b197f7f79811f3273d6ef56'
ORIGINAL_FILES = {'wake.json': '1e2ad1e97fad1db021def00493ea504ffda3087bae5a4577cbacee3c6ff7ec62', 'entry.json': 'd65c9affda167e9e7c1c809216d7b6695a744102692a76da6e081c7f33977755', 'authority-started.json': 'c8f642d98f2b7d5e6028eaeacbc3ab17fa4f0629e6e832aca39e9407aeadcab0', 'authority.input-preflight.json': '36bb9b040bd67125aabb85499d64f29278855aa381e6c6252f0bacbc5ef50c86', 'authority.json': 'e6a269420c4665e2118b410c94398c7eeefa6a919746a3108cc6092fa7fe736e', 'authority/receipt.json': '6c6d710eef1c568f7aeb26bdf9b8b89d813f42e974966ca8ba7190c38eb10985', 'authority/request.json': 'bd02f535e99013e0fbe1f89ea8295ee22122db980c245a8d1cda4ee4c8c069f3', 'authority/authority-transport.json': 'aff5db800730183c0b6b8eb5892a6aafc65d8abe7398467b7d33681288346ebe', 'authority/evidence.json': '50d32bd92020f18905fe05da5708b36df331f3530f474b4238f192ba78054265', 'authority/round-1/scientific_decision.provider-receipt.json': '1a8dee698a01cbb44a8255199bf2a7d11bd146eefd0617fa20691ac154afd353', 'authority/round-1/decision-author.provenance.json': '6c80a21d2fad334b99edb670478736af20cec156ad6334b57d668f80c06d6780', 'authority/round-1/judgment.json': '04f05a01c075b00cce07241e7862ff9b8c1d50a3e2b065cc4c09fcc2b070c21f', 'authority/round-1/decision-reviewer.provenance.json': '369b964f3660cad80882cb4c0ad7d9c5129a27da78a6488827f8c0e39e321c7d', 'authority/round-1/review.json': '4a8b71ea9aa65cf3d8afe27d735e689c0dbcb2b359175248c99293783ec2aeaf', 'authority/round-1/decision.json': '0e762f63dfd778c473be9e0ead69b4733f025a844b197f7f79811f3273d6ef56', 'authority/round-1/scientific_decision_review.provider-receipt.json': 'f5afa2236a0f9836703f7b7fa000576fa67fabdd9041a312a975d363ea17d989'}
ORIGINAL_JUDGMENTS = {'judgment': {'artifact': 'evidence/04f05a01c075b00cce07241e7862ff9b8c1d50a3e2b065cc4c09fcc2b070c21f-ELIGIBILITY263_authority__round-1__judgment.json', 'sha256': '04f05a01c075b00cce07241e7862ff9b8c1d50a3e2b065cc4c09fcc2b070c21f', 'size': 4892}, 'review': {'artifact': 'evidence/4a8b71ea9aa65cf3d8afe27d735e689c0dbcb2b359175248c99293783ec2aeaf-ELIGIBILITY263_authority__round-1__review.json', 'sha256': '4a8b71ea9aa65cf3d8afe27d735e689c0dbcb2b359175248c99293783ec2aeaf', 'size': 7200}, 'decision': {'artifact': 'evidence/0e762f63dfd778c473be9e0ead69b4733f025a844b197f7f79811f3273d6ef56-ELIGIBILITY263_authority__round-1__decision.json', 'sha256': '0e762f63dfd778c473be9e0ead69b4733f025a844b197f7f79811f3273d6ef56', 'size': 6740}}
PREREQUISITE = {'authorization': '040f2cce8b4e44c696808913becf9cbbd80bfc1e29e48fe9d4e7b9e6e65769a5', 'completed_original': {'artifact': 'evidence/3d4eee9f6db33ad896958eeefa9a9db0799479771c7286bdf80fb390ee409171-TECHNICAL262_POSTCHECK.stdout', 'sha256': '3d4eee9f6db33ad896958eeefa9a9db0799479771c7286bdf80fb390ee409171', 'size': 39846}, 'event': '14e41efb5bb6d3a8c8397aed1e3d3addc0b717ccd5c1d9c9ea8f15264e81a45d', 'request': '7b39364ecb0929c54e77f2a630dde9eceeeb1c7852b32cd09ccf4479dced0d1e', 'source': 'dd6f815c7bd36e605a74be5aeea8b8546f6712b1', 'status': 'LIVE_PINNED_CLIENT_STRUCTURED_OUTPUT_AND_RETRIEVAL_VERIFIED', 'technical_event': {'attempt': '1', 'branch': 'astra/infrastructure-milestone-record', 'kind': 'astra_turn', 'source': 'dd6f815c7bd36e605a74be5aeea8b8546f6712b1', 'turn_id': '71d129fc4d4f890fc17c999888223b2bc27469089acbf11a858a5edb1db0e3ac'}}


def candidate():
    from orchestrator.investigator_wakes import event
    return event(KIND, AUTHORIZED, OPERATOR)


def grant(config):
    from orchestrator.investigator_wakes import setting
    from orchestrator.research_catalog import linked_change
    template = setting(config)['template']
    ref = template.get('eligibility_replacement')
    if not isinstance(ref, dict) or ref.get('request_id') != REQUEST:
        raise ValueError('ELIGIBILITY263_EXACT_REVIEWED_GRANT_REQUIRED')
    history = linked_change(config, {'change_request': ref})
    event = next((e for e in history['events'] if e['identity'] == AUTHORIZED), None)
    if (event is None or event['event'] != 'AUTHORIZED' or event['actor']['kind'] != 'human'
            or event['payload'].get('operator_original_sha256') != OPERATOR
            or event['payload'].get('approved_packet_sha256') != DECISION_PACKET):
        raise ValueError('ELIGIBILITY263_ACTUAL_OPERATOR_AUTHORIZATION_REQUIRED')
    refs = event['payload'].get('authority_reference', {})
    for name, expected in [('operator_original', OPERATOR), ('approved_packet', DECISION_PACKET)]:
        if refs.get(name, {}).get('sha256') != expected or not refs[name].get('artifact'):
            raise ValueError('ELIGIBILITY263_AUTHORIZATION_ORIGINALS_REQUIRED')
    app = next(e for e in history['events'] if e['identity'] == ref['applied_event'])
    if app['payload']['result_binding'].get('source') != config['source']:
        raise ValueError('ELIGIBILITY263_REVIEWED_CURRENT_REPAIR_REQUIRED')
    primary = linked_change(config, {'change_request': template['change_request']})
    current = next(e for e in primary['events'] if e['identity'] == template['change_request']['applied_event'])
    if PREREQUISITE not in current['payload']['result_binding'].get('runtime_prerequisites', []):
        raise ValueError('ELIGIBILITY263_REQUIRED_PROOF_DELIVERY_GUARD_MISSING')
    return {'request_id': REQUEST, 'authorized_event': AUTHORIZED,
        'operator_original_sha256': OPERATOR, 'decision_packet_sha256': DECISION_PACKET,
        'repair': ref, 'source': config['source']}


def original(config, client):
    from orchestrator import investigator_wakes as wakes, research_task_authority as authority
    from orchestrator.research_catalog import paths
    folder = wakes.directory(config) / ORIGINAL_WAKE
    raws = {name: wakes.read(folder/name) for name in ORIGINAL_FILES}
    if {name: hashlib.sha256(raw).hexdigest() for name, raw in raws.items()} != ORIGINAL_FILES:
        raise ValueError('ELIGIBILITY263_ORIGINAL_BYTES_CHANGED')
    values = {name: json.loads(raw) for name, raw in raws.items()}
    wake = values['wake.json']; entry = values['entry.json']; task = entry['request']['task']
    if ((folder/'submitted.json').exists() or (folder/'submitted.json').is_symlink()
            or task['task_id'] in paths(config)):
        raise ValueError('ELIGIBILITY263_ORIGINAL_ALREADY_REGISTERED')
    dbpath = Path(config['state'])/'coordinator.sqlite'
    if dbpath.is_symlink() or not dbpath.is_file():
        raise ValueError('ELIGIBILITY263_EXISTING_COORDINATOR_REQUIRED')
    with sqlite3.connect(dbpath.absolute().as_uri()+'?mode=ro', uri=True) as db:
        if db.execute('SELECT 1 FROM research_submissions WHERE task_id=?', (task['task_id'],)).fetchone():
            raise ValueError('ELIGIBILITY263_ORIGINAL_ALREADY_SUBMITTED')
    if (config['source'] == ORIGINAL_SOURCE or wake['source'] != ORIGINAL_SOURCE
            or wake['events'] != [previous.candidate()]
            or digest({k:v for k,v in wake.items() if k != 'identity'}) != ORIGINAL_WAKE):
        raise ValueError('ELIGIBILITY263_EXACT_ORIGINAL_WAKE_REQUIRED')
    response = client('', 'read_investigator_wake', {'wake': ORIGINAL_WAKE})
    if response.get('status') != 'RESERVED' or response.get('wake') != wake:
        raise ValueError('ELIGIBILITY263_ORIGINAL_RESERVATION_CHANGED')
    transport = values['authority/authority-transport.json']
    protected = client('', 'stage_packet', {'event': transport['event']})
    if (protected.get('status') != 'COMPLETE' or protected.get('packet') != transport['packet']
            or protected.get('packet_sha256') != PACKET
            or hashlib.sha256(encoded(transport['packet'])).hexdigest() != PACKET):
        raise ValueError('ELIGIBILITY263_PROTECTED_ORIGINAL_CHANGED')
    historical = {**config, 'source': ORIGINAL_SOURCE, 'source_root': entry['source_root']}
    # Native original-only verifier authenticates the sealed DEFER, both replies,
    # actual provenance and original presentation. This issues no model request.
    decision = authority._verify(historical, entry, folder/'authority/round-1/decision.json', client=client)
    if (decision['decision'] != 'DEFER' or decision['_opposing_review_verdict'] != 'APPROVE'
            or decision['_decision_sha256'] != DECISION
            or values['authority.json']['status'] != 'AGENT_REVIEWED_DEFERRAL'):
        raise ValueError('ELIGIBILITY263_EXACT_REVIEWED_DEFERRAL_REQUIRED')
    if client('', 'stage_status', {'event': transport['event'], 'stage': 'disposition'}) != {
            'status': 'NOT_STARTED_RECONCILIATION_REQUIRED'}:
        raise ValueError('ELIGIBILITY263_UNEXPECTED_DOWNSTREAM_STAGE')
    template = wakes.setting(config)['template']
    if (any(template[k] != task[k] for k in ('experiment', 'request', 'references'))
            or task['purpose'] != 'CHARTER_SELECTION' or task['mode'] != 'investigate'):
        raise ValueError('ELIGIBILITY263_UNCHANGED_RESEARCH_SCOPE_REQUIRED')
    previous.original(config, client)  # Preserve the exact237/247 no-retry boundary too.
    return {'wake': wake, 'event': transport['event'], 'packet_sha256': PACKET,
        'original_file_sha256': ORIGINAL_FILES, 'decision_sha256': DECISION,
        'decision': 'DEFER', 'opposing_review': 'APPROVE',
        'original_judgments': ORIGINAL_JUDGMENTS,
        'unresolved_criticism': 'The completed technical prerequisite was absent from263 scientific capture. '
            'The original DEFER remains valid. Read the preserved author, opposing review and sealed decision '
            'before relying on this reconsideration; implementation proof is not scientific approval.',
        'scientific_acceptance': False, 'original_retry': False}


def verify(config, value, client):
    if value != candidate():
        raise ValueError('ELIGIBILITY263_EXACT_ONE_RECONSIDERATION_REQUIRED')
    authorization = grant(config)
    proof = original(config, client)
    from orchestrator.investigator_wakes import verify_events
    linked = verify_events(config, [previous.DISPOSITION], client)[0]
    return {**linked, 'event': candidate(), 'eligibility_reconsideration': {
        'authorization': authorization, 'original': proof,
        'runtime_prerequisite': PREREQUISITE,
        'scope': 'Exactly one fresh eligibility pair after reviewed prevention and all seven conditions. '
                 'Another DEFER, failure or incomplete outcome confers no retry.'}}


def disposition_event(row, source):
    link = row.get('eligibility_reconsideration', {}); auth = link.get('authorization', {})
    proof = link.get('original', {}); wake = proof.get('wake', {})
    if (row.get('event') != candidate() or auth.get('request_id') != REQUEST
            or auth.get('authorized_event') != AUTHORIZED or auth.get('operator_original_sha256') != OPERATOR
            or auth.get('decision_packet_sha256') != DECISION_PACKET or auth.get('source') != source
            or wake.get('identity') != ORIGINAL_WAKE or wake.get('source') != ORIGINAL_SOURCE
            or wake.get('events') != [previous.candidate()]
            or digest({k:v for k,v in wake.items() if k != 'identity'}) != ORIGINAL_WAKE
            or proof.get('packet_sha256') != PACKET or proof.get('decision_sha256') != DECISION
            or proof.get('original_file_sha256') != ORIGINAL_FILES
            or proof.get('original_judgments') != ORIGINAL_JUDGMENTS
            or proof.get('decision') != 'DEFER' or proof.get('opposing_review') != 'APPROVE'
            or link.get('runtime_prerequisite') != PREREQUISITE
            or proof.get('scientific_acceptance') is not False or proof.get('original_retry') is not False):
        raise ValueError('ELIGIBILITY263_DISPOSITION_LINK_CHANGED')
    return previous.DISPOSITION


def verify_captured_originals(packet, source, capture, prerequisites):
    """Keep the genuine adverse judgments readable, not only their hash index."""
    from orchestrator.disposition_context import _selected_evidence
    from orchestrator.scientific_runtime_prerequisites import _body
    evidence = _selected_evidence(packet, source)
    if evidence is None:
        return
    for row in evidence.get('verified_events', []):
        if row.get('event', {}).get('kind') != KIND:
            continue
        disposition_event(row, source)
        if PREREQUISITE not in prerequisites:
            raise ValueError('ELIGIBILITY263_REQUIRED_PROOF_DELIVERY_GUARD_MISSING')
        for ref in ORIGINAL_JUDGMENTS.values():
            raw = _body(capture, 'change/'+REQUEST+'/'+ref['artifact'], 'change_artifact')
            if hashlib.sha256(raw).hexdigest() != ref['sha256'] or len(raw) != ref['size']:
                raise ValueError('ELIGIBILITY263_ADVERSE_ORIGINAL_NOT_IN_CAPTURE')


def capture_original_history(config, packet, source, capture, original_client, *, owner=None):
    """Keep the consumed grant discoverable as historical evidence, not active state.

    The four current namespaces remain bounded. The exact263 packet authenticates
    the old247 namespace's original prefix, using the existing native reader.
    This reuses the original packet; it is not a new observation or model call.
    """
    from copy import deepcopy
    from orchestrator.disposition_context import _selected_evidence
    from orchestrator import scientific_evidence_access as access
    selected = _selected_evidence(packet, source)
    if selected is None or not any(row.get('event', {}).get('kind') == KIND
                                  for row in selected.get('verified_events', [])):
        return capture
    for row in selected['verified_events']:
        disposition_event(row, source)
    if not callable(original_client):
        raise ValueError('ELIGIBILITY263_ORIGINAL_READER_REQUIRED')
    event = {'turn_id': '002bdd14a7eba6c3ec6e610d4b5afa1f349251ab141066aa3106ccd0935afedd',
        'attempt': '1', 'source': ORIGINAL_SOURCE,
        'branch': 'astra/infrastructure-milestone-record', 'kind': 'astra_turn'}
    result = original_client('', 'stage_packet', {'event': event})
    original = result.get('packet')
    if (result.get('status') != 'COMPLETE' or result.get('packet_sha256') != PACKET
            or hashlib.sha256(encoded(original)).hexdigest() != PACKET):
        raise ValueError('ELIGIBILITY263_CAPTURE_ORIGINAL_PACKET_CHANGED')
    prefix = original['scientific_change_history']['native_prefixes'][previous.REQUEST]
    # A fixed historical request from the exact original packet, never a model
    # path or a broader current namespace. Native load checks every original byte.
    old = access.capture_changes(config['change_request_store'], [previous.REQUEST],
        source=source, task_binding=capture['manifest']['task_binding'],
        expected_prefixes={previous.REQUEST: prefix}, owner=owner)
    combined = deepcopy(capture); records = {r['name']: r for r in combined['manifest']['records']}
    for record in old['manifest']['records']:
        access._add(records, combined['payloads'], record['name'], record['kind'],
                    old['payloads'][record['sha256']], record['provenance'])
    for identity, head in old['manifest']['request_heads'].items():
        if identity in combined['manifest']['request_heads'] and combined['manifest']['request_heads'][identity] != head:
            raise ValueError('ELIGIBILITY263_HISTORICAL_PREFIX_CONFLICT')
        combined['manifest']['request_heads'][identity] = head
    access._add(records, combined['payloads'], 'eligibility/'+ORIGINAL_WAKE+'/packet.original.json',
        'task_packet_original', encoded(original), {'source': ORIGINAL_SOURCE,
            'packet_sha256': PACKET, 'meaning': 'Historical263 input, not current authority or a new retrieval.'})
    combined['manifest']['records'] = [records[name] for name in sorted(records)]
    return combined
