"""Synthetic fixtures only: no live client, scientific judgment or admission."""
from copy import deepcopy
import hashlib
import json
import sqlite3
import pytest

from orchestrator import investigator_eligibility247_replacement as replacement
from orchestrator import investigator_eligibility_replacement as previous
from orchestrator import investigator_wakes as wakes, protected_investigator as protected
from orchestrator.handover_coordinator import digest
from orchestrator.hosted_cycle import encoded
from test_investigator_wakes import configured, protected_fixture, manifest, runtime, save_manifest


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
                 'operator_original': {'artifact': 'operator.txt', 'sha256': replacement.OPERATOR},
                 'approved_packet': {'artifact': 'packet.md', 'sha256': replacement.DECISION_PACKET}}}},
        {'identity': 'a'*64, 'event': 'APPLIED', 'payload': {'result_binding': {'source': configured['source']}}}]}
    monkeypatch.setattr('orchestrator.research_catalog.linked_change', lambda *args: history)
    return configured, history


def test_grant_requires_actual_authority_and_reviewed_current_source(reviewed, monkeypatch):
    config, history = reviewed
    assert replacement.grant(config)['authorized_event'] == replacement.AUTHORIZED
    for path, value in [(('actor', 'kind'), 'agent'), (('payload', 'operator_original_sha256'), '0'*64),
                        (('payload', 'approved_packet_sha256'), '0'*64)]:
        saved = deepcopy(history['events'][0])
        history['events'][0][path[0]][path[1]] = value
        with pytest.raises(ValueError, match='ACTUAL_OPERATOR'): replacement.grant(config)
        history['events'][0] = saved
    history['events'][1]['payload']['result_binding']['source'] = '0'*40
    with pytest.raises(ValueError, match='CURRENT_REPAIR'): replacement.grant(config)
    def reject(*args): raise ValueError('RESEARCH_CHANGE_REVIEW_PENDING')
    monkeypatch.setattr('orchestrator.research_catalog.linked_change', reject)
    with pytest.raises(ValueError, match='REVIEW_PENDING'): replacement.grant(config)


def test_missing_authority_or_original_reference_refuses(reviewed):
    config, history = reviewed
    history['events'][0]['payload']['authority_reference']['operator_original']['sha256'] = '0'*64
    with pytest.raises(ValueError, match='AUTHORIZATION_ORIGINALS'): replacement.grant(config)
    history['events'].pop(0)
    with pytest.raises(ValueError, match='ACTUAL_OPERATOR'): replacement.grant(config)


def test_only_two_exact_grants_are_routed(configured):
    bind(configured)
    assert previous.selected_candidate(configured) == replacement.candidate()
    configured['investigator']['template']['eligibility_replacement']['request_id'] = previous.REQUEST
    configured['investigator']['template_sha256'] = digest(configured['investigator']['template'])
    assert previous.selected_candidate(configured) == previous.candidate()
    configured['investigator']['template']['eligibility_replacement']['request_id'] = 'f'*64
    configured['investigator']['template_sha256'] = digest(configured['investigator']['template'])
    with pytest.raises(ValueError, match='KNOWN_REPLACEMENT'): previous.selected_candidate(configured)


@pytest.fixture
def originals(configured, monkeypatch):
    config = configured; runtime(config)
    db = sqlite3.connect(config['state']+'/coordinator.sqlite')
    db.execute('CREATE TABLE research_submissions(task_id TEXT PRIMARY KEY)'); db.commit(); db.close()
    wake = {'schema': wakes.WAKE, 'source': replacement.ORIGINAL_SOURCE,
        'template_sha256': '1'*64, 'day': '2026-09-22', 'events': [previous.candidate()]}
    wake['identity'] = digest(wake)
    monkeypatch.setattr(replacement, 'ORIGINAL_WAKE', wake['identity'])
    folder = save_manifest(config, wake)
    t = config['investigator']['template']
    task = {'task_id': 'investigator-'+wake['identity'], 'mode': 'investigate', 'purpose': 'CHARTER_SELECTION',
        'experiment': t['experiment'], 'request': t['request'], 'references': t['references']}
    event = {'turn_id': '4'*64, 'source': replacement.ORIGINAL_SOURCE, 'attempt': '1'}
    packet = {'reviewer_evidence': {'input_evidence': {'verified_events': [{'synthetic_parent': True}]}}}
    sha = hashlib.sha256(encoded(packet)).hexdigest(); monkeypatch.setattr(replacement, 'PACKET', sha)
    judgment = {'context_sha256':'5'*64,'decision':'APPLY','transition':{'from':'PROPOSED','to':'ELIGIBLE'},
        'rationale':'Synthetic completed author.', 'reconsideration':'Synthetic conditions.'}
    values = {'wake.json':wake, 'entry.json':{'request':{'task':task}},
        'authority/authority-transport.json':{'event':event,'packet':packet},
        'authority/round-1/judgment.json':judgment}
    replies = {}
    for stage in ('continuation','review'):
        answer = (json.dumps({'judgment.json':encoded(judgment).decode()}) if stage=='continuation'
            else 'Original prose before ```json\n{"review.json":"{}"}\n``` and after.')
        replies[stage] = {'status':'COMPLETE','answer':answer,'receipt':{'stage':stage,'synthetic':True},'packet_sha256':sha}
    monkeypatch.setattr(replacement, 'REPLIES', {s:{'answer_sha256':hashlib.sha256(v['answer'].encode()).hexdigest(),
        'receipt_sha256':hashlib.sha256(encoded(v['receipt'])).hexdigest()} for s,v in replies.items()})
    for name,value in values.items():
        target=folder/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(encoded(value))
    monkeypatch.setattr(replacement,'ORIGINAL_FILES',{n:hashlib.sha256(encoded(v)).hexdigest() for n,v in values.items()})
    monkeypatch.setattr('orchestrator.research_catalog.paths',lambda config:{})
    def checked(value,*args):
        if value.get('status') != 'COMPLETE': raise ValueError('SYNTHETIC_INCOMPLETE_PROVIDER')
        return value['answer'],value['receipt']
    monkeypatch.setattr('orchestrator.hosted_campaign.checked_reply',checked)
    monkeypatch.setattr('orchestrator.research_task_authority._provenance',lambda *args: {'synthetic':True})
    monkeypatch.setattr(previous, 'disposition_event',lambda *args: replacement.DISPOSITION)
    monkeypatch.setattr(previous, 'original',lambda *args:{'wake':{'events':[replacement.DISPOSITION]}})
    replies['disposition']={'status':'NOT_STARTED_RECONCILIATION_REQUIRED'}
    def client(socket,operation,body):
        if operation=='read_investigator_wake': return {'status':'RESERVED','wake':deepcopy(wake)}
        if operation=='stage_packet': return {'status':'COMPLETE','packet':packet,'packet_sha256':sha}
        if operation=='stage_status': return replies[body['stage']]
        pytest.fail('Unexpected launch/admission/write: '+operation)
    return config,folder,task,client,replies


def test_exact_originals_not_normalized_or_accepted(originals):
    config,folder,task,client,replies=originals
    before={str(p):p.read_bytes() for p in folder.rglob('*') if p.is_file()}
    proof=replacement.original(config,client)
    assert proof['original_author_judgment']['decision']=='APPLY'
    assert proof['original_unparsed_review']==replies['review']['answer']
    assert proof['scientific_acceptance'] is False and proof['original_retry'] is False
    assert 'packet' not in proof and 'original' not in proof
    assert before=={str(p):p.read_bytes() for p in folder.rglob('*') if p.is_file()}


@pytest.mark.parametrize('name',['authority.json','submitted.json','authority/receipt.json','authority/round-1/decision.json','authority-recovery'])
def test_existing_seal_or_recovery_forbids_replacement(originals,name):
    config,folder,task,client,_=originals
    target=folder/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_text('{}')
    with pytest.raises(ValueError,match='SEALED_OR_SUBMITTED|RECOVERY_REQUIRES'): replacement.original(config,client)


def test_registered_or_submitted_original_refuses(originals,monkeypatch):
    config,folder,task,client,_=originals
    monkeypatch.setattr('orchestrator.research_catalog.paths',lambda config:{task['task_id']:'existing'})
    with pytest.raises(ValueError,match='ALREADY_REGISTERED'):replacement.original(config,client)
    monkeypatch.setattr('orchestrator.research_catalog.paths',lambda config:{})
    db=sqlite3.connect(config['state']+'/coordinator.sqlite')
    db.execute('INSERT INTO research_submissions VALUES(?)',(task['task_id'],));db.commit();db.close()
    with pytest.raises(ValueError,match='ALREADY_SUBMITTED'):replacement.original(config,client)


@pytest.mark.parametrize('mutation',['answer','receipt','uncertain','downstream','file','scope','source','parent'])
def test_changed_or_uncertain_original_refuses(originals,monkeypatch,mutation):
    config,folder,task,client,replies=originals
    if mutation=='answer': replies['review']['answer']+=' changed'
    if mutation=='receipt': replies['review']['receipt']['changed']=True
    if mutation=='uncertain': replies['review']['status']='UNCERTAIN_MODEL_RECONCILE_NO_RETRY'
    if mutation=='downstream': replies['disposition']={'status':'COMPLETE'}
    if mutation=='file': (folder/'authority/round-1/judgment.json').write_text('{}')
    if mutation=='scope':
        config['investigator']['template']['request']+=' New patient execution'
        config['investigator']['template_sha256']=digest(config['investigator']['template'])
    if mutation=='source': config['source']=replacement.ORIGINAL_SOURCE
    if mutation=='parent': monkeypatch.setattr(previous,'disposition_event',lambda *args:None)
    with pytest.raises(ValueError):replacement.original(config,client)


def test_valid_or_different_failure_cannot_be_replaced(originals,monkeypatch):
    config,folder,task,client,replies=originals
    for answer,error in [(json.dumps({'review.json':'{}'}),'VALID_REVIEW_CANNOT'),('{}','EXACT_FORMAT_REFUSAL')]:
        replies['review']['answer']=answer
        monkeypatch.setitem(replacement.REPLIES['review'],'answer_sha256',hashlib.sha256(answer.encode()).hexdigest())
        with pytest.raises(ValueError,match=error):replacement.original(config,client)


def test_single_fixed_event_never_mixed(configured):
    with pytest.raises(ValueError,match='SINGLE_LOGICAL_EVENT'):
        wakes.verify_events(configured,[replacement.candidate(),wakes.event('TASK','1'*64,'2'*64)],None)
    with pytest.raises(ValueError,match='EXACT_ONE_SUCCESSOR'):
        replacement.verify(configured,{**replacement.candidate(),'identity':'1'*64},None)


def test_reservation_once_across_source_day_and_template(configured,protected_fixture):
    broker,checked,database=protected_fixture
    old=protected.handle(broker,'reserve_investigator',{'events':[previous.candidate()]})['wake']
    new=protected.handle(broker,'reserve_investigator',{'events':[replacement.candidate()]})['wake']
    configured['source']='f'*40
    configured['investigator']['template']['request']+=' Later day/source'
    configured['investigator']['template_sha256']=digest(configured['investigator']['template'])
    for _ in range(3):
        assert protected.handle(broker,'reserve_investigator',{'events':[replacement.candidate()]})=={
            'status':'NO_NEW_EVENTS','existing_wakes':[new['identity']],'models':0,'admissions':0}
    assert protected._read(broker,old['identity'])['wake']==old
    assert sqlite3.connect(database).execute('SELECT count(*) FROM wakes').fetchone()[0]==2
    with pytest.raises(ValueError,match='CONSUMED_EVENT_CHANGED'):
        protected.handle(broker,'reserve_investigator',{'events':[{**replacement.candidate(),'original_sha256':'e'*64}]})


def discovery_fixture(config,monkeypatch,reply):
    bind(config);rt=runtime(config);calls=[]
    monkeypatch.setattr('orchestrator.disposition_successors.status',lambda config:{'successors':[]})
    monkeypatch.setattr('orchestrator.continuing_operations.status',lambda config:{'completed':[]})
    monkeypatch.setattr('orchestrator.protected_scientific_jobs.read_observation',lambda config:{'events':[]})
    def client(socket,operation,body):
        if operation=='list_recorded_steering':return {'status':'COMPLETE','requests':[]}
        if operation=='reserve_investigator':
            calls.append(body['events'])
            if isinstance(reply,Exception):raise reply
            return reply
        pytest.fail(operation)
    monkeypatch.setattr(wakes,'_client',lambda runtime:client)
    return rt,calls


def test_refused_grant_has_no_bootstrap_fallback(configured,monkeypatch):
    rt,calls=discovery_fixture(configured,monkeypatch,ValueError('Changed original'))
    assert wakes._discover(rt)['status']=='ELIGIBILITY247_GRANT_REQUIRES_RECONCILIATION'
    assert calls==[[replacement.candidate()]]


@pytest.mark.parametrize('outcome',['failed','deferred','historical_failed','historical_deferred'])
def test_consumed_failed_or_deferred_has_no_bootstrap_fallback(configured,monkeypatch,outcome):
    bind(configured);m=manifest(configured,[replacement.candidate()])
    if outcome.startswith('historical'):
        m['source']='e'*40;m['identity']=digest({k:v for k,v in m.items() if k!='identity'})
    from orchestrator.operations_report import private_root
    private_root(configured['state'])
    folder=save_manifest(configured,m)
    if outcome.endswith('deferred'):(folder/'authority.json').write_bytes(encoded({'status':'AGENT_REVIEWED_DEFERRAL'}))
    else:(folder/'authority-started.json').write_text('{}')
    rt,calls=discovery_fixture(configured,monkeypatch,{'status':'NO_NEW_EVENTS','existing_wakes':[m['identity']]})
    assert wakes._discover(rt)['status']=='ELIGIBILITY247_REPLACEMENT_CONSUMED_NO_RETRY'
    assert calls==[[replacement.candidate()]]


def test_native_disposition_link_uses_same_scientific_original(configured):
    from orchestrator.disposition_context import _dispositions
    wake={'schema':wakes.WAKE,'source':replacement.ORIGINAL_SOURCE,
        'template_sha256':'b5479eef7512fa46eb4753bb0333b85eabe51a03e7dadf2efc36fe51ddd3f7b7',
        'day':'2026-09-22','events':[previous.candidate()]}
    wake['identity']=digest(wake)
    assert wake['identity']==replacement.ORIGINAL_WAKE
    proof={'wake':wake,'packet_sha256':replacement.PACKET,'original_file_sha256':replacement.ORIGINAL_FILES,
        'original_reply_sha256':replacement.REPLIES,'prior_wake':previous.ORIGINAL_WAKE,
        'prior_packet_sha256':previous.PACKET,'disposition_event':replacement.DISPOSITION,
        'scientific_acceptance':False,'original_retry':False}
    row={'event':replacement.candidate(),'eligibility_replacement':{
        'authorization':{'authorized_event':replacement.AUTHORIZED,'operator_original_sha256':replacement.OPERATOR,
            'decision_packet_sha256':replacement.DECISION_PACKET,'source':configured['source']},'original':proof},
        'linked_disposition':{'originals':{'origin_task':replacement.DISPOSITION['identity']},
            'result_sha256':replacement.DISPOSITION['original_sha256']}}
    value={'investigator_wake':manifest(configured,[replacement.candidate()]),'verified_events':[row]}
    assert _dispositions(value,configured['source'])==[(0,row['linked_disposition']['originals'])]
    for section,key in [('authorization','authorized_event'),('authorization','source'),
        ('original','packet_sha256'),('original','original_retry'),('original','prior_wake')]:
        changed=deepcopy(value);changed['verified_events'][0]['eligibility_replacement'][section][key]='wrong'
        with pytest.raises(ValueError,match='DISPOSITION_LINK_CHANGED'):_dispositions(changed,configured['source'])


def test_successful_submission_allows_genuinely_new_scientific_event(configured,monkeypatch):
    bind(configured);rt,calls=discovery_fixture(configured,monkeypatch,{})
    original=manifest(configured,[replacement.candidate()]);folder=save_manifest(configured,original)
    task='a'*64;(folder/'submitted.json').write_bytes(encoded({'submission':{'task':task}}))
    rt.q.db.execute('INSERT INTO tasks VALUES(?,?,?)',(task,'COMPLETE','{}'))
    newer=wakes.event('STEERING','1'*64,'2'*64)
    next_wake=manifest(configured,[newer])
    def client(socket,operation,body):
        if operation=='list_recorded_steering':return {'status':'COMPLETE','requests':[{
            'request_id':newer['identity'],'original_sha256':newer['original_sha256']}]}
        assert operation=='reserve_investigator';calls.append(body['events'])
        if body['events']==[replacement.candidate()]:return {'status':'NO_NEW_EVENTS','existing_wakes':[original['identity']]}
        assert body['events']==[newer]
        return {'status':'RESERVED','wake':next_wake}
    monkeypatch.setattr(wakes,'_client',lambda runtime:client)
    assert wakes._discover(rt)['wake']==next_wake['identity']
    assert calls==[[replacement.candidate()],[newer]]


def test_regeneration_preserves_raw_refusal_and_disposition_link(originals,reviewed,monkeypatch):
    config,folder,task,client,replies=originals
    # Same configured fixture is shared; native grant uses its exact synthetic history.
    proof=replacement.original(config,client)
    monkeypatch.setattr(replacement,'original',lambda *args:deepcopy(proof))
    monkeypatch.setattr(wakes,'_disposition',lambda *args:{'event':replacement.DISPOSITION,
        'references':[], 'linked_disposition':{'originals':{'origin_task':replacement.DISPOSITION['identity']},
            'result_sha256':replacement.DISPOSITION['original_sha256']}})
    result=wakes.regenerate(config,manifest(config,[replacement.candidate()]),client)
    assert result['task']['purpose']=='CHARTER_SELECTION'
    row=result['evidence']['verified_events'][0]
    assert row['eligibility_replacement']['original']['original_unparsed_review']==replies['review']['answer']
    assert row['linked_disposition']['result_sha256']==replacement.DISPOSITION['original_sha256']
