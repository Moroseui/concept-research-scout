"""Synthetic boundary tests; no review is qualified and no scientific model runs."""
from copy import deepcopy
import hashlib
import json
import sqlite3
from types import SimpleNamespace

import pytest

from orchestrator import investigator_eligibility_replacement as replacement
from orchestrator import investigator_wakes as wakes, protected_investigator as protected
from orchestrator.handover_coordinator import digest
from orchestrator.hosted_cycle import encoded
from test_investigator_wakes import configured, protected_fixture, manifest


def bind(config):
    t = config['investigator']['template']
    t['eligibility_replacement'] = {'request_id': replacement.REQUEST, 'applied_event': 'a'*64}
    config['investigator']['template_sha256'] = digest(t)


@pytest.fixture
def reviewed(configured, monkeypatch):
    bind(configured)
    history = {'events': [
        {'identity': replacement.AUTHORIZED, 'event': 'AUTHORIZED', 'actor': {'kind': 'human'},
         'payload': {'operator_original_sha256': replacement.OPERATOR,
             'approved_packet_sha256': replacement.DECISION_PACKET,
             'authority_reference': {
                 'operator_original': {'artifact': 'evidence/operator.txt', 'sha256': replacement.OPERATOR},
                 'approved_packet': {'artifact': 'evidence/packet.md', 'sha256': replacement.DECISION_PACKET}}}},
        {'identity': 'a'*64, 'event': 'APPLIED', 'payload': {'result_binding': {'source': configured['source']}}}]}
    monkeypatch.setattr('orchestrator.research_catalog.linked_change', lambda *args: history)
    return configured, history


def test_grant_requires_actual_human_event_and_current_review(reviewed, monkeypatch):
    config, history = reviewed
    assert replacement.grant(config)['authorized_event'] == replacement.AUTHORIZED
    for path, value in [(('actor', 'kind'), 'agent'), (('payload', 'operator_original_sha256'), '0'*64),
                        (('payload', 'approved_packet_sha256'), '0'*64)]:
        original = deepcopy(history['events'][0])
        history['events'][0][path[0]][path[1]] = value
        with pytest.raises(ValueError, match='ACTUAL_OPERATOR'): replacement.grant(config)
        history['events'][0] = original
    history['events'][1]['payload']['result_binding']['source'] = '0'*40
    with pytest.raises(ValueError, match='CURRENT_REPAIR'): replacement.grant(config)
    def reject(*args): raise ValueError('RESEARCH_CHANGE_REVIEW_PENDING')
    monkeypatch.setattr('orchestrator.research_catalog.linked_change', reject)
    with pytest.raises(ValueError, match='REVIEW_PENDING'): replacement.grant(config)


def test_missing_authorization_or_altered_original_reference_fails(reviewed):
    config, history = reviewed
    history['events'][0]['payload']['authority_reference']['operator_original']['sha256'] = '0'*64
    with pytest.raises(ValueError, match='AUTHORIZATION_ORIGINALS'): replacement.grant(config)
    history['events'].pop(0)
    with pytest.raises(ValueError, match='ACTUAL_OPERATOR'): replacement.grant(config)


def test_one_event_is_global_across_source_template_and_repeated_reconciliation(configured, protected_fixture):
    broker, checked, database = protected_fixture
    original = wakes.event('DISPOSITION', 'b'*64, 'c'*64)
    old = protected.handle(broker, 'reserve_investigator', {'events': [original]})['wake']
    new = protected.handle(broker, 'reserve_investigator', {'events': [replacement.candidate()]})['wake']
    configured['source'] = 'f'*40
    configured['investigator']['template']['request'] += ' future configuration'
    configured['investigator']['template_sha256'] = digest(configured['investigator']['template'])
    for _ in range(3):
        assert protected.handle(broker, 'reserve_investigator', {'events': [replacement.candidate()]}) == {
            'status': 'NO_NEW_EVENTS', 'existing_wakes': [new['identity']], 'models': 0, 'admissions': 0}
    assert protected._read(broker, old['identity'])['wake'] == old
    assert protected._read(broker, new['identity'])['wake'] == new
    assert sqlite3.connect(database).execute('SELECT count(*) FROM wakes').fetchone()[0] == 2
    changed = {**replacement.candidate(), 'original_sha256': 'e'*64}
    with pytest.raises(ValueError, match='CONSUMED_EVENT_CHANGED'):
        protected.handle(broker, 'reserve_investigator', {'events': [changed]})


def test_cannot_mix_replacement_with_another_scientific_event(configured):
    with pytest.raises(ValueError, match='SINGLE_LOGICAL_EVENT'):
        wakes.verify_events(configured, [replacement.candidate(), wakes.event('TASK','1'*64,'2'*64)], None)
    with pytest.raises(ValueError, match='EXACT_ONE_SUCCESSOR'):
        replacement.verify(configured, {**replacement.candidate(), 'identity': '1'*64}, None)


@pytest.fixture
def original_fixture(configured, monkeypatch, tmp_path):
    config = configured; folder = wakes.directory(config) / replacement.ORIGINAL_WAKE
    folder.mkdir(parents=True)
    task = {'task_id': 'investigator-'+replacement.ORIGINAL_WAKE, 'mode': 'investigate',
            'purpose': 'CHARTER_SELECTION', 'experiment': config['investigator']['template']['experiment'],
            'request': config['investigator']['template']['request'], 'references': []}
    wake = {'identity': replacement.ORIGINAL_WAKE, 'events': [wakes.event('DISPOSITION','2'*64,'3'*64)]}
    event = {'turn_id': '4'*64, 'source': replacement.ORIGINAL_SOURCE, 'attempt': '1'}
    packet = {'synthetic_original': True}; packet_sha = hashlib.sha256(encoded(packet)).hexdigest()
    monkeypatch.setattr(replacement, 'PACKET', packet_sha)
    judgment = {'reconsideration': ['Synthetic invalid list'], 'decision': 'APPLY'}
    raw_judgment = encoded(judgment)
    review = {'verdict':'APPROVE', 'judgment_sha256':hashlib.sha256(raw_judgment).hexdigest()}
    values = {'wake.json': wake, 'entry.json': {'request': {'task': task}},
        'authority/authority-transport.json': {'packet': packet, 'event': event},
        'authority/round-1/judgment.json': judgment, 'authority/round-1/review.json': review}
    replies = {}
    for stage, name, label in [('continuation','judgment.json','scientific_decision'),
                               ('review','review.json','scientific_decision_review')]:
        receipt = {'stage':stage, 'synthetic':True}
        values['authority/round-1/'+label+'.provider-receipt.json'] = receipt
        answer = json.dumps({name:encoded(values['authority/round-1/'+name]).decode()})
        replies[stage] = {'status':'COMPLETE', 'answer':answer, 'receipt':receipt, 'packet_sha256':packet_sha}
    for name, value in values.items():
        f = folder/name; f.parent.mkdir(parents=True,exist_ok=True); f.write_bytes(encoded(value))
    monkeypatch.setattr(replacement, 'ORIGINAL_FILES', {n:hashlib.sha256(encoded(v)).hexdigest() for n,v in values.items()})
    monkeypatch.setattr('orchestrator.hosted_campaign.checked_reply',lambda value,*args:(value['answer'],value['receipt']))
    monkeypatch.setattr('orchestrator.research_task_authority._provenance',lambda *args: {'synthetic':True})
    monkeypatch.setattr('orchestrator.research_catalog.paths',lambda config:{})
    db = sqlite3.connect(config['state']+'/coordinator.sqlite')
    db.execute('CREATE TABLE research_submissions(task_id TEXT PRIMARY KEY)'); db.commit();db.close()
    def client(socket, operation, body):
        if operation == 'read_investigator_wake': return {'status':'RESERVED','wake':deepcopy(wake)}
        if operation == 'stage_packet': return {'status':'COMPLETE','packet':packet,'packet_sha256':packet_sha}
        if operation == 'stage_status': return replies[body['stage']]
        pytest.fail('Unexpected model/admission/write operation '+operation)
    return config, folder, task, client, replies


def test_exact_originals_remain_unsealed_and_both_judgments_are_carried(original_fixture):
    config, folder, task, client, _ = original_fixture
    before = {str(p):p.read_bytes() for p in folder.rglob('*') if p.is_file()}
    proof = replacement.original(config, client)
    assert isinstance(proof['invalid_judgment']['reconsideration'], list)
    assert proof['original_opposing_review']['verdict'] == 'APPROVE'
    assert proof['scientific_acceptance'] is False and proof['original_retry'] is False
    assert before == {str(p):p.read_bytes() for p in folder.rglob('*') if p.is_file()}


@pytest.mark.parametrize('name', ['authority.json','submitted.json','authority/receipt.json','authority/round-1/decision.json'])
def test_sealed_or_submitted_original_cannot_be_replaced(original_fixture, name):
    config, folder, task, client, _ = original_fixture
    p = folder/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text('{}')
    with pytest.raises(ValueError, match='SEALED_OR_SUBMITTED'): replacement.original(config, client)


def test_missing_changed_reply_or_changed_scope_cannot_qualify(original_fixture):
    config, folder, task, client, replies = original_fixture
    replies['review']['answer'] = json.dumps({'review.json':'{}'})
    with pytest.raises(ValueError, match='GENUINE_ORIGINAL_REPLY'): replacement.original(config, client)
    p = folder/'authority/round-1/judgment.json';p.write_text('{}')
    with pytest.raises(ValueError, match='ORIGINAL_BYTES_CHANGED'): replacement.original(config, client)
    p.unlink()
    with pytest.raises(ValueError, match='REGULAR_FILE_REQUIRED'): replacement.original(config, client)


def test_scope_and_source_do_not_grant_retries(original_fixture):
    config, folder, task, client, _ = original_fixture
    config['source'] = replacement.ORIGINAL_SOURCE
    with pytest.raises(ValueError, match='CHANGED_REVIEWED_SOURCE'): replacement.original(config, client)
    config['source'] = 'd'*40
    config['investigator']['template']['request'] += ' Added patient execution'
    config['investigator']['template_sha256'] = digest(config['investigator']['template'])
    with pytest.raises(ValueError, match='UNCHANGED_LOGICAL_RESEARCH_SCOPE'): replacement.original(config, client)


def test_existing_submission_refuses_replacement(original_fixture):
    config, folder, task, client, _ = original_fixture
    db=sqlite3.connect(config['state']+'/coordinator.sqlite')
    db.execute('INSERT INTO research_submissions VALUES(?)',(task['task_id'],));db.commit();db.close()
    with pytest.raises(ValueError, match='ALREADY_SUBMITTED'): replacement.original(config, client)


def linked_row(source):
    wake = {'schema': wakes.WAKE, 'source': replacement.ORIGINAL_SOURCE,
        'template_sha256':'7a9320e299c061164122e3f8112a4736dfca0310798f4e0dc92646308715e01a',
        'day':'2026-09-22','events':[wakes.event('DISPOSITION',
            '921aebca29e588fd368bf2f25d9102e230e810609040dee0296c2d15bc53b9fb',
            '2aa35827f9f93e63850258ed5995216501d44ac3222c47490283d0a5a9f5ff59')]}
    wake['identity']=digest(wake)
    return {'event':replacement.candidate(), 'eligibility_replacement':{
        'authorization':{'authorized_event':replacement.AUTHORIZED,'operator_original_sha256':replacement.OPERATOR,
            'decision_packet_sha256':replacement.DECISION_PACKET,'source':source},
        'original':{'wake':wake,'packet_sha256':replacement.PACKET,'original_file_sha256':replacement.ORIGINAL_FILES,
            'scientific_acceptance':False}},
        'linked_disposition':{'originals':{'origin_task':wake['events'][0]['identity']},
            'result_sha256':wake['events'][0]['original_sha256']}}


def test_same_fixed_link_drives_compact_context_and_retrieval(configured):
    from orchestrator.disposition_context import _dispositions
    row=linked_row(configured['source'])
    value={'investigator_wake':manifest(configured,[replacement.candidate()]),'verified_events':[row]}
    assert _dispositions(value,configured['source']) == [(0,row['linked_disposition']['originals'])]
    for section,key in [('authorization','authorized_event'),('authorization','source'),
                        ('original','packet_sha256'),('original','scientific_acceptance')]:
        changed=deepcopy(value);changed['verified_events'][0]['eligibility_replacement'][section][key]='wrong'
        with pytest.raises(ValueError,match='DISPOSITION_LINK_CHANGED'):_dispositions(changed,configured['source'])
    changed=deepcopy(value);changed['verified_events'][0]['linked_disposition']['result_sha256']='0'*64
    with pytest.raises(ValueError):_dispositions(changed,configured['source'])


def test_regeneration_and_entry_verification_carry_original_link_without_accepting_old_judgment(reviewed, monkeypatch):
    config, history = reviewed
    row=linked_row(config['source']);proof=row['eligibility_replacement']['original']
    proof.update(invalid_judgment={'reconsideration':['Unchanged invalid original']},original_opposing_review={'verdict':'APPROVE'})
    monkeypatch.setattr(replacement, 'original', lambda *args:deepcopy(proof))
    monkeypatch.setattr(wakes, '_disposition', lambda *args:{'event':proof['wake']['events'][0],
        'references':[], 'linked_disposition':row['linked_disposition']})
    m=manifest(config,[replacement.candidate()]);derived=wakes.regenerate(config,m,None)
    assert derived['task']['purpose']=='CHARTER_SELECTION'
    projected=derived['evidence']['verified_events'][0]
    assert projected['eligibility_replacement']['original']==proof
    history['events'][0]['actor']['kind']='agent'
    with pytest.raises(ValueError,match='ACTUAL_OPERATOR'):wakes.regenerate(config,m,None)
