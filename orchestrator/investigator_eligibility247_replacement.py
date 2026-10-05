"""One fixed, separately authorized successor to unsealed eligibility247.

Original237/247 outcomes are authenticated read-only, never repaired or accepted.
The ordinary protected reservation owns the new authorization across releases.
"""
import hashlib
import json

from orchestrator.handover_coordinator import digest
from orchestrator.hosted_cycle import encoded
from orchestrator import investigator_eligibility_replacement as previous

KIND = 'ELIGIBILITY247_REPLACEMENT'
REQUEST = 'b02a16db795f23b2d7e54194fdee19132eed5996b9d32c9b82c1b7bab3ca9b94'
AUTHORIZED = '040f2cce8b4e44c696808913becf9cbbd80bfc1e29e48fe9d4e7b9e6e65769a5'
OPERATOR = '960bf383171d4dd4b2649fa1387730f88c9d4a762523a9b597905fddb772712d'
DECISION_PACKET = '2dcf9a1f7a7d6fa4fffc1d2bada64c0823ccdee88e7a589c7bbc13a9eebc34d6'
ORIGINAL_WAKE = '684414320b9382731b871ba9e8e04231f73710c5e7a2c1e8c526dd1a984b4ff6'
ORIGINAL_SOURCE = 'a44a888764ea48b67581bab9ccff537488b2d782'
PACKET = 'b9f3e08d50b0b3f1f866a32913a34d4ae8aebd26ff99be85ce52d3ff28cbd65f'
FAILURE = 'HOSTED_CAMPAIGN_INVALID_JSON'
DISPOSITION = {'kind': 'DISPOSITION',
    'identity': '921aebca29e588fd368bf2f25d9102e230e810609040dee0296c2d15bc53b9fb',
    'original_sha256': '2aa35827f9f93e63850258ed5995216501d44ac3222c47490283d0a5a9f5ff59'}
ORIGINAL_FILES = {'authority-started.json': '922c8cf1bf8e15cecc168b6a143526e9f1975099f52e285d1cf68382664872f0', 'wake.json': '0f523c5469d420f3d6f5ac5c98be4991372782812c835db6c504fb7695d90b2b', 'entry.json': 'c9691314191866bdbd4bc920512f2adcf65b6f141ae58eb7076c3fb0b4069108', 'authority/stopped.json': 'c38302b37555827d533a8da1094b495aa59a2c8124024a1c0891d434c826af7b', 'authority/evidence.json': 'a86a1c8ce13283551c5a386a4190de71a97763186b638db449d8cb6e0ea507ad', 'authority/request.json': '8c603b4621ecc66e6225576d1a16797cae1ae4e9377861c879b7c4df41384c2a', 'authority/authority-transport.json': 'b8d403f4f37c176f8ad797fb44267e0d087c10291106fbb03a86712f8d3debaa', 'authority/round-1/scientific_decision.provider-receipt.json': '346c005ae5f77ecefccce85fe2155a5e0be685157e7a11f0b865b476f79bea94', 'authority/round-1/judgment.json': 'ac35027d7996ae87811ca849a4247667bdf416470bd069124ffa5db01d464d73'}
REPLIES = {'continuation': {'answer_sha256': '85556b3ad54cb5010cad6f888d5d3281d16d3b31ae631693afa24cbfe65694f5', 'receipt_sha256': '346c005ae5f77ecefccce85fe2155a5e0be685157e7a11f0b865b476f79bea94'}, 'review': {'answer_sha256': 'e3fa3bad6f3366cea150e18f79b2fb709bf7df9e073b4632b398a2a0b87c2b01', 'receipt_sha256': 'bbbb0dbbf87ef50fc274b34593b8207a675a98ccd8d0451d3b6908ea1bbb3f47'}}


def candidate():
    from orchestrator.investigator_wakes import event
    return event(KIND, AUTHORIZED, OPERATOR)


def grant(config):
    from orchestrator.investigator_wakes import setting, pin
    from orchestrator.research_catalog import linked_change
    ref = setting(config)['template'].get('eligibility_replacement')
    if (not isinstance(ref, dict) or set(ref) != {'request_id', 'applied_event'}
            or ref['request_id'] != REQUEST):
        raise ValueError('ELIGIBILITY247_EXACT_REVIEWED_GRANT_REQUIRED')
    pin(ref['applied_event'])
    history = linked_change(config, {'change_request': ref})
    event = next((e for e in history['events'] if e['identity'] == AUTHORIZED), None)
    if (event is None or event['event'] != 'AUTHORIZED' or event['actor']['kind'] != 'human'
            or event['payload'].get('operator_original_sha256') != OPERATOR
            or event['payload'].get('approved_packet_sha256') != DECISION_PACKET):
        raise ValueError('ELIGIBILITY247_ACTUAL_OPERATOR_AUTHORIZATION_REQUIRED')
    refs = event['payload'].get('authority_reference', {})
    for name, expected in [('operator_original', OPERATOR), ('approved_packet', DECISION_PACKET)]:
        if refs.get(name, {}).get('sha256') != expected or not refs[name].get('artifact'):
            raise ValueError('ELIGIBILITY247_AUTHORIZATION_ORIGINALS_REQUIRED')
    applied = next(e for e in history['events'] if e['identity'] == ref['applied_event'])
    if applied['payload']['result_binding'].get('source') != config['source']:
        raise ValueError('ELIGIBILITY247_REVIEWED_CURRENT_REPAIR_REQUIRED')
    return {'request_id': REQUEST, 'authorized_event': AUTHORIZED,
        'operator_original_sha256': OPERATOR, 'decision_packet_sha256': DECISION_PACKET,
        'repair': ref, 'source': config['source']}


def original(config, client):
    from orchestrator import investigator_wakes as wakes, research_task_authority as authority
    from orchestrator.hosted_campaign import checked_reply, artifact_files
    folder = wakes.directory(config) / ORIGINAL_WAKE
    raws = {name: wakes.read(folder / name) for name in ORIGINAL_FILES}
    if {name: hashlib.sha256(raw).hexdigest() for name, raw in raws.items()} != ORIGINAL_FILES:
        raise ValueError('ELIGIBILITY247_ORIGINAL_BYTES_CHANGED')
    values = {name: json.loads(raw) for name, raw in raws.items()}
    wake = values['wake.json']; entry = values['entry.json']; task = entry['request']['task']
    previous._absent(config, folder, task['task_id'])
    # A recovered projection is also a stop, never proof that another pair is safe.
    if (folder / 'authority-recovery').exists() or (folder / 'authority-recovery').is_symlink():
        raise ValueError('ELIGIBILITY247_RECOVERY_REQUIRES_RECONCILIATION')
    if config['source'] in (ORIGINAL_SOURCE, previous.ORIGINAL_SOURCE):
        raise ValueError('ELIGIBILITY247_CHANGED_REVIEWED_SOURCE_REQUIRED')
    core = {k: v for k, v in wake.items() if k != 'identity'}
    if (digest(core) != ORIGINAL_WAKE or wake['source'] != ORIGINAL_SOURCE
            or wake['events'] != [previous.candidate()]):
        raise ValueError('ELIGIBILITY247_ORIGINAL_WAKE_CHANGED')
    reservation = client('', 'read_investigator_wake', {'wake': ORIGINAL_WAKE})
    if reservation.get('status') != 'RESERVED' or reservation.get('wake') != wake:
        raise ValueError('ELIGIBILITY247_ORIGINAL_RESERVATION_CHANGED')
    transport = values['authority/authority-transport.json']; packet = transport['packet']; event = transport['event']
    protected = client('', 'stage_packet', {'event': event})
    if (protected.get('status') != 'COMPLETE' or protected.get('packet') != packet
            or protected.get('packet_sha256') != PACKET or hashlib.sha256(encoded(packet)).hexdigest() != PACKET):
        raise ValueError('ELIGIBILITY247_PROTECTED_PACKET_CHANGED')
    # Native historical reader authenticates the entire old packet without
    # embedding its administrative history again in the successor input.
    parent_row = packet['reviewer_evidence']['input_evidence']['verified_events']
    if len(parent_row) != 1 or previous.disposition_event(parent_row[0], ORIGINAL_SOURCE) != DISPOSITION:
        raise ValueError('ELIGIBILITY247_ORIGINAL_DISPOSITION_LINK_CHANGED')
    parent = previous.original(config, client)
    if parent['wake']['events'] != [DISPOSITION]:
        raise ValueError('ELIGIBILITY247_PREDECESSOR_SCOPE_CHANGED')
    answers = {}
    for stage, family in [('continuation', 'codex'), ('review', 'claude')]:
        answer, receipt = checked_reply(client('', 'stage_status', {'event': event, 'stage': stage}), stage, PACKET)
        if (hashlib.sha256(answer.encode()).hexdigest() != REPLIES[stage]['answer_sha256']
                or hashlib.sha256(encoded(receipt)).hexdigest() != REPLIES[stage]['receipt_sha256']):
            raise ValueError('ELIGIBILITY247_GENUINE_ORIGINAL_REPLY_CHANGED')
        authority._provenance(receipt, family, event, packet)
        answers[stage] = answer
    if artifact_files(answers['continuation'], ['judgment.json'])['judgment.json'].encode() != raws['authority/round-1/judgment.json']:
        raise ValueError('ELIGIBILITY247_ORIGINAL_AUTHOR_CHANGED')
    try:
        artifact_files(answers['review'], ['review.json'])
    except ValueError as error:
        if str(error) != FAILURE:
            raise ValueError('ELIGIBILITY247_EXACT_FORMAT_REFUSAL_REQUIRED') from error
    else:
        raise ValueError('ELIGIBILITY247_VALID_REVIEW_CANNOT_BE_REPLACED')
    if client('', 'stage_status', {'event': event, 'stage': 'disposition'}) != {'status': 'NOT_STARTED_RECONCILIATION_REQUIRED'}:
        raise ValueError('ELIGIBILITY247_UNEXPECTED_DOWNSTREAM_STAGE')
    template = wakes.setting(config)['template']
    if (template['experiment'] != task['experiment'] or template['request'] != task['request']
            or template['references'] != task['references'] or task['purpose'] != 'CHARTER_SELECTION'
            or task['mode'] != 'investigate'):
        raise ValueError('ELIGIBILITY247_UNCHANGED_LOGICAL_RESEARCH_SCOPE_REQUIRED')
    return {'wake': wake, 'event': event, 'packet_sha256': PACKET,
        'original_file_sha256': ORIGINAL_FILES, 'original_reply_sha256': REPLIES,
        'prior_wake': previous.ORIGINAL_WAKE, 'prior_packet_sha256': previous.PACKET,
        'disposition_event': DISPOSITION, 'original_author_judgment': values['authority/round-1/judgment.json'],
        'original_unparsed_review': answers['review'], 'failure': FAILURE,
        'scientific_acceptance': False, 'original_retry': False}


def verify(config, value, client):
    if value != candidate():
        raise ValueError('ELIGIBILITY247_EXACT_ONE_SUCCESSOR_EVENT_REQUIRED')
    authorization = grant(config)
    proof = original(config, client)
    from orchestrator.investigator_wakes import verify_events
    linked = verify_events(config, [DISPOSITION], client)[0]
    return {**linked, 'event': candidate(), 'eligibility_replacement': {
        'authorization': authorization, 'original': proof,
        'scope': 'One fresh current-source eligibility under the exact seven-condition decision. '
                 'At most one author and one opposing reviewer; no further retry or original normalization.'}}


def disposition_event(row, source):
    if row.get('event') != candidate():
        raise ValueError('ELIGIBILITY247_DISPOSITION_LINK_CHANGED')
    link = row.get('eligibility_replacement', {}); auth = link.get('authorization', {})
    proof = link.get('original', {}); wake = proof.get('wake', {})
    core = {k: v for k, v in wake.items() if k != 'identity'}
    if (auth.get('authorized_event') != AUTHORIZED or auth.get('operator_original_sha256') != OPERATOR
            or auth.get('decision_packet_sha256') != DECISION_PACKET or auth.get('source') != source
            or wake.get('identity') != ORIGINAL_WAKE or digest(core) != ORIGINAL_WAKE
            or wake.get('source') != ORIGINAL_SOURCE or wake.get('events') != [previous.candidate()]
            or proof.get('packet_sha256') != PACKET or proof.get('original_file_sha256') != ORIGINAL_FILES
            or proof.get('original_reply_sha256') != REPLIES or proof.get('disposition_event') != DISPOSITION
            or proof.get('prior_wake') != previous.ORIGINAL_WAKE or proof.get('prior_packet_sha256') != previous.PACKET
            or proof.get('scientific_acceptance') is not False or proof.get('original_retry') is not False):
        raise ValueError('ELIGIBILITY247_DISPOSITION_LINK_CHANGED')
    return DISPOSITION
