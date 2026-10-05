"""One operator-authorized eligibility237 successor over the normal wake store.

This fixed exception is not a generic retry permission. Original event ownership,
failed judgment, reviewer judgment and charge remain immutable. The new event's
identity is the actual AUTHORIZED event, independent of release/template/day.
"""
import hashlib
import json
from pathlib import Path
import sqlite3

from orchestrator.handover_coordinator import digest
from orchestrator.hosted_cycle import encoded

KIND = 'ELIGIBILITY237_REPLACEMENT'
REQUEST = 'dcb60bf21abdc32f7f535092ee95e192af58924acf4b9bf5dc9062de5ee54586'
AUTHORIZED = 'cbb08c7d616531a63ff2da0ac3e1b566b614395c7744393fb3fff2686fdb0e68'
OPERATOR = '8c97907ff26ea73eecf0b6d5b8dd2ef19406f4e782efd5eedaf6dfc2fc343b9b'
DECISION_PACKET = 'f74723f5f934ba701ed654837c57e60869dd7ead6f95b6e0857da50374ef5898'
ORIGINAL_WAKE = 'b7e9ab13295f0f3006008014dde1adeb33e61f4f18de3775790886b010735d07'
ORIGINAL_SOURCE = 'a472034dbf1444110ba0356379faf733796c6efc'
PACKET = 'af154221f87a2bf7c2adad8776b39bf33015b8fa71b05add12b7d25cf5abc98e'
FAILURE = 'ATTRIBUTED_RATIONALE_AND_RECONSIDERATION_REQUIRED'
ORIGINAL_FILES = {'authority-started.json': '8e882a4ca84916dfee399b11823a99874e565dfa87a5b886efa8895637cbe81c',
 'authority/authority-transport.json': '7e19bd1dd17d77d7e0962e529ef6751d246079dd770b2224fe53088d19f636f7',
 'authority/evidence.json': 'bf9fbaa70d4a195fe7a9012be40b426c7d3f189c0fbb0dc52d6ce2b05c7054e5',
 'authority/request.json': 'aacbdd8f00a3d7c135598ba530a71b21fd5c0c1a4a462e99a8e9cc6d9716c642',
 'authority/round-1/judgment.json': '2de0d97363490e829968fcb3a14ca5161eee51e5bcc594926a9f289300beab52',
 'authority/round-1/review.json': 'cadff1b5ad0fc45b487cbf1e50f9072cdab1156a737bbcf2d8b2f2d0b159fb68',
 'authority/round-1/scientific_decision.provider-receipt.json': 'da0a4c406d0f909cacd0a40bd84a8b5e98ebe0ae52b1dc5341be01219064150d',
 'authority/round-1/scientific_decision_review.provider-receipt.json': '1527becf421a4c220dc7a0650f5dba91670ab23f070a02402507a662513d8993',
 'authority/stopped.json': 'c38302b37555827d533a8da1094b495aa59a2c8124024a1c0891d434c826af7b',
 'entry.json': '8b540490df65afbd8f0f602d622e5856df90972afea1b1b94412657b1864361a',
 'wake.json': 'a07a7a5cfa50c5d2ad2b0ef285a28dbcc90a7d587fa2b6da358830fba8bda814'}


def candidate():
    from orchestrator.investigator_wakes import event
    return event(KIND, AUTHORIZED, OPERATOR)


def grant(config):
    from orchestrator.investigator_wakes import setting, pin
    from orchestrator.research_catalog import linked_change
    template = setting(config)['template']
    ref = template.get('eligibility_replacement')
    if (not isinstance(ref, dict) or set(ref) != {'request_id', 'applied_event'}
            or ref['request_id'] != REQUEST):
        raise ValueError('ELIGIBILITY237_EXACT_REVIEWED_GRANT_REQUIRED')
    pin(ref['applied_event'])
    history = linked_change(config, {'change_request': ref})
    authorization = next((e for e in history['events'] if e['identity'] == AUTHORIZED), None)
    if (authorization is None or authorization['event'] != 'AUTHORIZED'
            or authorization['actor']['kind'] != 'human'
            or authorization['payload'].get('operator_original_sha256') != OPERATOR
            or authorization['payload'].get('approved_packet_sha256') != DECISION_PACKET):
        raise ValueError('ELIGIBILITY237_ACTUAL_OPERATOR_AUTHORIZATION_REQUIRED')
    refs = authorization['payload'].get('authority_reference', {})
    for name, expected in (('operator_original', OPERATOR), ('approved_packet', DECISION_PACKET)):
        if refs.get(name, {}).get('sha256') != expected or not refs[name].get('artifact'):
            raise ValueError('ELIGIBILITY237_AUTHORIZATION_ORIGINALS_REQUIRED')
    applied = next(e for e in history['events'] if e['identity'] == ref['applied_event'])
    if applied['payload']['result_binding'].get('source') != config['source']:
        raise ValueError('ELIGIBILITY237_REVIEWED_CURRENT_REPAIR_REQUIRED')
    return {'request_id': REQUEST, 'authorized_event': AUTHORIZED,
            'operator_original_sha256': OPERATOR, 'decision_packet_sha256': DECISION_PACKET,
            'repair': ref, 'source': config['source']}


def _absent(config, folder, task_id):
    from orchestrator.research_catalog import paths
    for name in ('authority.json', 'submitted.json', 'authority/receipt.json',
                 'authority/round-1/decision.json'):
        p = folder / name
        if p.exists() or p.is_symlink():
            raise ValueError('ELIGIBILITY237_SEALED_OR_SUBMITTED_ORIGINAL_FORBIDDEN')
    if task_id in paths(config):
        raise ValueError('ELIGIBILITY237_ORIGINAL_ALREADY_REGISTERED')
    dbpath = Path(config['state']) / 'coordinator.sqlite'
    if dbpath.is_symlink() or not dbpath.is_file():
        raise ValueError('ELIGIBILITY237_EXISTING_COORDINATOR_REQUIRED')
    db = sqlite3.connect(dbpath.absolute().as_uri() + '?mode=ro', uri=True)
    try:
        if db.execute('SELECT 1 FROM research_submissions WHERE task_id=?', (task_id,)).fetchone():
            raise ValueError('ELIGIBILITY237_ORIGINAL_ALREADY_SUBMITTED')
    finally:
        db.close()


def original(config, client):
    """Exact original bytes plus protected transport, not a driver's conclusion."""
    from orchestrator import investigator_wakes as wakes
    from orchestrator.hosted_campaign import checked_reply, artifact_files
    from orchestrator import research_task_authority as authority
    folder = wakes.directory(config) / ORIGINAL_WAKE
    raws = {name: wakes.read(folder / name) for name in ORIGINAL_FILES}
    if {n: hashlib.sha256(v).hexdigest() for n, v in raws.items()} != ORIGINAL_FILES:
        raise ValueError('ELIGIBILITY237_ORIGINAL_BYTES_CHANGED')
    values = {n: json.loads(v) for n, v in raws.items()}
    wake = values['wake.json']; entry = values['entry.json']; task = entry['request']['task']
    _absent(config, folder, task['task_id'])
    if config['source'] == ORIGINAL_SOURCE:
        raise ValueError('ELIGIBILITY237_CHANGED_REVIEWED_SOURCE_REQUIRED')
    reserved = client('', 'read_investigator_wake', {'wake': ORIGINAL_WAKE})
    if reserved.get('status') != 'RESERVED' or reserved.get('wake') != wake:
        raise ValueError('ELIGIBILITY237_ORIGINAL_RESERVATION_CHANGED')
    transport = values['authority/authority-transport.json']; event = transport['event']
    packet = transport['packet']
    protected = client('', 'stage_packet', {'event': event})
    if (protected.get('status') != 'COMPLETE' or protected.get('packet') != packet
            or protected.get('packet_sha256') != PACKET
            or hashlib.sha256(encoded(packet)).hexdigest() != PACKET):
        raise ValueError('ELIGIBILITY237_PROTECTED_PACKET_CHANGED')
    for stage, family, name, label in (('continuation', 'codex', 'judgment.json', 'scientific_decision'),
                                      ('review', 'claude', 'review.json', 'scientific_decision_review')):
        answer, receipt = checked_reply(client('', 'stage_status', {'event': event, 'stage': stage}), stage, PACKET)
        if (artifact_files(answer, [name])[name].encode() != raws['authority/round-1/' + name]
                or receipt != values['authority/round-1/' + label + '.provider-receipt.json']):
            raise ValueError('ELIGIBILITY237_GENUINE_ORIGINAL_REPLY_CHANGED')
        authority._provenance(receipt, family, event, packet)
    # The pinned author/reviewer bytes are preserved, never repaired or sealed.
    judgment = values['authority/round-1/judgment.json']
    review = values['authority/round-1/review.json']
    if (not isinstance(judgment.get('reconsideration'), list)
            or review.get('judgment_sha256') != ORIGINAL_FILES['authority/round-1/judgment.json']):
        raise ValueError('ELIGIBILITY237_EXACT_SCHEMA_FAILURE_REQUIRED')
    template = wakes.setting(config)['template']
    if (template['experiment'] != task['experiment'] or template['request'] != task['request']
            or template['references'] != task['references'] or task['purpose'] != 'CHARTER_SELECTION'
            or task['mode'] != 'investigate' or len(wake['events']) != 1
            or wake['events'][0]['kind'] != 'DISPOSITION'):
        raise ValueError('ELIGIBILITY237_UNCHANGED_LOGICAL_RESEARCH_SCOPE_REQUIRED')
    return {'wake': wake, 'task': task, 'event': event,
            'packet_sha256': PACKET, 'original_file_sha256': ORIGINAL_FILES,
            'invalid_judgment': judgment, 'original_opposing_review': review,
            'failure': FAILURE, 'scientific_acceptance': False, 'original_retry': False}


def verify(config, value, client):
    if value != candidate():
        raise ValueError('ELIGIBILITY237_EXACT_ONE_SUCCESSOR_EVENT_REQUIRED')
    authorization = grant(config)
    proof = original(config, client)
    from orchestrator.investigator_wakes import verify_events
    underlying = verify_events(config, proof['wake']['events'], client)[0]
    return {**underlying, 'event': candidate(),
            'eligibility_replacement': {'authorization': authorization, 'original': proof,
                'scope': 'One fresh current-source eligibility, at most one author and one opposing reviewer. '
                         'A valid outcome continues only through ordinary scientific gates; no further retry.'}}


def disposition_event(row, source):
    """Resolve one fixed authenticated link for both presentation and retrieval.

    This is structural validation of an already authenticated packet, never an
    authorization or independent proof of the old result. Original broker checks
    remain in verify(); downstream capture reauthenticates the linked disposition.
    """
    value = row.get('event', {})
    if value.get('kind') == 'ELIGIBILITY263_RECONSIDERATION':
        from orchestrator.investigator_eligibility263_reconsideration import disposition_event as reconsider
        return reconsider(row, source)
    if value.get('kind') == 'ELIGIBILITY247_REPLACEMENT':
        from orchestrator.investigator_eligibility247_replacement import disposition_event as successor
        return successor(row, source)
    if value.get('kind') == 'DISPOSITION':
        return value
    if value.get('kind') != KIND:
        return None
    link = row.get('eligibility_replacement', {})
    authority = link.get('authorization', {})
    proof = link.get('original', {})
    wake = proof.get('wake', {})
    expected = {'kind':'DISPOSITION',
        'identity':'921aebca29e588fd368bf2f25d9102e230e810609040dee0296c2d15bc53b9fb',
        'original_sha256':'2aa35827f9f93e63850258ed5995216501d44ac3222c47490283d0a5a9f5ff59'}
    core = {k:v for k,v in wake.items() if k != 'identity'}
    if (value != candidate() or wake.get('identity') != ORIGINAL_WAKE
            or wake.get('source') != ORIGINAL_SOURCE or digest(core) != ORIGINAL_WAKE
            or wake.get('events') != [expected]
            or authority.get('authorized_event') != AUTHORIZED
            or authority.get('operator_original_sha256') != OPERATOR
            or authority.get('decision_packet_sha256') != DECISION_PACKET
            or authority.get('source') != source or proof.get('packet_sha256') != PACKET
            or proof.get('original_file_sha256') != ORIGINAL_FILES
            or proof.get('scientific_acceptance') is not False):
        raise ValueError('ELIGIBILITY237_DISPOSITION_LINK_CHANGED')
    return expected


def selected_candidate(config):
    """Fixed reviewed exceptions, never a caller-defined retry registry."""
    from orchestrator.investigator_wakes import setting
    ref = setting(config)['template']['eligibility_replacement']
    if ref['request_id'] == REQUEST:
        return candidate()
    from orchestrator import investigator_eligibility247_replacement as successor
    if ref['request_id'] == successor.REQUEST:
        return successor.candidate()
    from orchestrator import investigator_eligibility263_reconsideration as reconsider
    if ref['request_id'] == reconsider.REQUEST:
        return reconsider.candidate()
    raise ValueError('INVESTIGATOR_KNOWN_REPLACEMENT_GRANT_REQUIRED')
