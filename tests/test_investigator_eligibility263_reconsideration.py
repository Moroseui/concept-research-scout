"""Single-authorization routing and refusal contracts; synthetic, never live science."""
from copy import deepcopy
import sqlite3
from types import SimpleNamespace
import pytest
from orchestrator import investigator_eligibility263_reconsideration as reconsider
from orchestrator import investigator_eligibility_replacement as selection
from orchestrator import investigator_wakes as wakes, protected_investigator as protected
from orchestrator.handover_coordinator import digest
from orchestrator.hosted_cycle import encoded
from test_investigator_wakes import configured, protected_fixture, manifest, runtime, save_manifest


def bind(config):
    template=config['investigator']['template']
    template['eligibility_replacement']={'request_id':reconsider.REQUEST,'applied_event':'a'*64}
    config['investigator']['template_sha256']=digest(template)


@pytest.fixture
def reviewed(configured,monkeypatch):
    bind(configured)
    app={'identity':'a'*64,'event':'APPLIED','payload':{'result_binding':{'source':configured['source']}}}
    auth={'identity':reconsider.AUTHORIZED,'event':'AUTHORIZED','actor':{'kind':'human'},'payload':{
        'operator_original_sha256':reconsider.OPERATOR,'approved_packet_sha256':reconsider.DECISION_PACKET,
        'authority_reference':{'operator_original':{'artifact':'operator.txt','sha256':reconsider.OPERATOR},
            'approved_packet':{'artifact':'packet.md','sha256':reconsider.DECISION_PACKET}}}}
    primary={'identity':configured['investigator']['template']['change_request']['applied_event'],
        'event':'APPLIED','payload':{'result_binding':{'source':configured['source'],
        'runtime_prerequisites':[deepcopy(reconsider.PREREQUISITE)]}}}
    history={'events':[auth,app]};head={'events':[primary]}
    monkeypatch.setattr('orchestrator.research_catalog.linked_change',
        lambda cfg,entry:history if entry['change_request']['request_id']==reconsider.REQUEST else head)
    return configured,history,head


def test_actual_authority_and_primary_proof_guard_required(reviewed):
    cfg,h,p=reviewed
    assert reconsider.grant(cfg)['authorized_event']==reconsider.AUTHORIZED
    for field in ['operator_original_sha256','approved_packet_sha256']:
        old=h['events'][0]['payload'][field];h['events'][0]['payload'][field]='0'*64
        with pytest.raises(ValueError,match='ACTUAL_OPERATOR'):reconsider.grant(cfg)
        h['events'][0]['payload'][field]=old
    h['events'][0]['actor']['kind']='agent'
    with pytest.raises(ValueError,match='ACTUAL_OPERATOR'):reconsider.grant(cfg)
    h['events'][0]['actor']['kind']='human'
    p['events'][0]['payload']['result_binding'].pop('runtime_prerequisites')
    with pytest.raises(ValueError,match='PROOF_DELIVERY_GUARD'):reconsider.grant(cfg)


def test_guard_cannot_use_wrong_source_authorization_or_proof(reviewed):
    cfg,h,p=reviewed
    spec=p['events'][0]['payload']['result_binding']['runtime_prerequisites'][0]
    for field in ['source','authorization','event']:
        old=spec[field];spec[field]='f'*len(old)
        with pytest.raises(ValueError,match='PROOF_DELIVERY_GUARD'):reconsider.grant(cfg)
        spec[field]=old


def test_unapproved_application_still_refuses(reviewed,monkeypatch):
    cfg,_,_=reviewed
    def fail(*args):raise ValueError('RESEARCH_CHANGE_REVIEW_PENDING')
    monkeypatch.setattr('orchestrator.research_catalog.linked_change',fail)
    with pytest.raises(ValueError,match='REVIEW_PENDING'):reconsider.grant(cfg)


def test_exact_event_routing_and_no_mixed_batch(configured):
    bind(configured)
    assert selection.selected_candidate(configured)==reconsider.candidate()
    with pytest.raises(ValueError,match='SINGLE_LOGICAL_EVENT'):
        wakes.verify_events(configured,[reconsider.candidate(),wakes.event('TASK','1'*64,'2'*64)],None)
    with pytest.raises(ValueError,match='EXACT_ONE_RECONSIDERATION'):
        reconsider.verify(configured,{**reconsider.candidate(),'identity':'1'*64},None)


def test_single_protected_reservation_survives_source_and_day_changes(configured,protected_fixture):
    broker,checked,database=protected_fixture
    old=protected.handle(broker,'reserve_investigator',{'events':[reconsider.previous.candidate()]})['wake']
    new=protected.handle(broker,'reserve_investigator',{'events':[reconsider.candidate()]})['wake']
    configured['source']='f'*40
    configured['investigator']['template']['request']+=' New source template'
    configured['investigator']['template_sha256']=digest(configured['investigator']['template'])
    for _ in range(3):
        assert protected.handle(broker,'reserve_investigator',{'events':[reconsider.candidate()]})=={
            'status':'NO_NEW_EVENTS','existing_wakes':[new['identity']],'models':0,'admissions':0}
    assert protected._read(broker,old['identity'])['wake']==old
    assert sqlite3.connect(database).execute('SELECT count(*) FROM wakes').fetchone()[0]==2
    with pytest.raises(ValueError,match='CONSUMED_EVENT_CHANGED'):
        protected.handle(broker,'reserve_investigator',{'events':[{**reconsider.candidate(),'original_sha256':'e'*64}]})


@pytest.mark.parametrize('outcome',['refused','deferred','uncertain'])
def test_refusal_or_consumption_does_not_fall_back_to_bootstrap(configured,monkeypatch,outcome):
    bind(configured);rt=runtime(configured);calls=[]
    monkeypatch.setattr('orchestrator.disposition_successors.status',lambda config:{'successors':[]})
    monkeypatch.setattr('orchestrator.continuing_operations.status',lambda config:{'completed':[]})
    monkeypatch.setattr('orchestrator.protected_scientific_jobs.read_observation',lambda config:{'events':[]})
    m=manifest(configured,[reconsider.candidate()]);folder=save_manifest(configured,m)
    if outcome=='deferred':(folder/'authority.json').write_bytes(encoded({'status':'AGENT_REVIEWED_DEFERRAL'}))
    else:(folder/'authority-started.json').write_text('{}')
    def client(socket,operation,body):
        if operation=='list_recorded_steering':return {'status':'COMPLETE','requests':[]}
        if operation=='reserve_investigator':
            calls.append(body['events'])
            if outcome=='refused':raise ValueError('Unresolved binding')
            return {'status':'NO_NEW_EVENTS','existing_wakes':[m['identity']]}
        pytest.fail('Unexpected operation '+operation)
    monkeypatch.setattr(wakes,'_client',lambda runtime:client)
    assert wakes._discover(rt)['status']==('ELIGIBILITY263_GRANT_REQUIRES_RECONCILIATION' if outcome=='refused'
        else 'ELIGIBILITY263_RECONSIDERATION_CONSUMED_NO_RETRY')
    assert calls==[[reconsider.candidate()]]


@pytest.fixture
def originals(configured,monkeypatch):
    import hashlib
    config=configured; runtime(config)
    with sqlite3.connect(config['state']+'/coordinator.sqlite') as db:
        db.execute('CREATE TABLE research_submissions(task_id TEXT PRIMARY KEY)')
    wake={'schema':wakes.WAKE,'source':reconsider.ORIGINAL_SOURCE,
        'template_sha256':'1'*64,'day':'2026-09-23','events':[reconsider.previous.candidate()]}
    wake['identity']=digest(wake);monkeypatch.setattr(reconsider,'ORIGINAL_WAKE',wake['identity'])
    folder=save_manifest(config,wake);t=config['investigator']['template']
    task={'task_id':'investigator-'+wake['identity'],'mode':'investigate','purpose':'CHARTER_SELECTION',
          'experiment':t['experiment'],'request':t['request'],'references':t['references']}
    packet={'synthetic_original':True};sha=hashlib.sha256(encoded(packet)).hexdigest()
    monkeypatch.setattr(reconsider,'PACKET',sha)
    event={'turn_id':'4'*64,'source':reconsider.ORIGINAL_SOURCE,'attempt':'1'}
    vals={'wake.json':wake,'entry.json':{'source_root':str(folder),'request':{'task':task}},
          'authority/authority-transport.json':{'event':event,'packet':packet},
          'authority.json':{'status':'AGENT_REVIEWED_DEFERRAL'}}
    for name,value in vals.items():
        target=folder/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(encoded(value))
    monkeypatch.setattr(reconsider,'ORIGINAL_FILES',{k:hashlib.sha256(encoded(v)).hexdigest() for k,v in vals.items()})
    monkeypatch.setattr('orchestrator.research_catalog.paths',lambda cfg:{})
    sealed={'decision':'DEFER','_opposing_review_verdict':'APPROVE','_decision_sha256':reconsider.DECISION}
    seen=[]
    monkeypatch.setattr('orchestrator.research_task_authority._verify',lambda *a,**kw:seen.append(a) or sealed)
    monkeypatch.setattr(reconsider.previous,'original',lambda *a:{'preserved':True})
    replies={'downstream':{'status':'NOT_STARTED_RECONCILIATION_REQUIRED'}}
    def client(socket,operation,body):
        if operation=='read_investigator_wake':return {'status':'RESERVED','wake':wake}
        if operation=='stage_packet':return {'status':'COMPLETE','packet':packet,'packet_sha256':sha}
        if operation=='stage_status':return replies['downstream']
        pytest.fail('Unexpected model/admission/mutation: '+operation)
    return config,folder,task,client,replies,sealed,seen


def test_sealed_defer_preserved_and_original_verifier_is_historical(originals):
    config,folder,task,client,replies,sealed,seen=originals
    before={str(p):p.read_bytes() for p in folder.rglob('*') if p.is_file()}
    result=reconsider.original(config,client)
    assert result['decision']=='DEFER' and result['opposing_review']=='APPROVE'
    assert result['scientific_acceptance'] is False and result['original_retry'] is False
    assert seen[0][0]['source']==reconsider.ORIGINAL_SOURCE
    assert 'packet' not in result and 'rationale' not in result
    assert before=={str(p):p.read_bytes() for p in folder.rglob('*') if p.is_file()}


@pytest.mark.parametrize('mutation',['bytes','approved_instead','review_revised','decision_pin','downstream',
    'scope','submitted','registered','uncertain'])
def test_wrong_changed_or_submitted_deferral_refuses(originals,monkeypatch,mutation):
    config,folder,task,client,replies,sealed,seen=originals
    if mutation=='bytes':(folder/'authority.json').write_text('{}')
    if mutation=='approved_instead':sealed['decision']='APPLY'
    if mutation=='review_revised':sealed['_opposing_review_verdict']='REVISE'
    if mutation=='decision_pin':sealed['_decision_sha256']='0'*64
    if mutation=='downstream':replies['downstream']={'status':'COMPLETE'}
    if mutation=='scope':
        config['investigator']['template']['request']+=' Unrelated scientific scope'
        config['investigator']['template_sha256']=digest(config['investigator']['template'])
    if mutation=='submitted':(folder/'submitted.json').write_text('{}')
    if mutation=='registered':monkeypatch.setattr('orchestrator.research_catalog.paths',lambda c:{task['task_id']:'registered'})
    if mutation=='uncertain':
        def failed(*args,**kw):raise ValueError('UNCERTAIN_ORIGINAL_NO_RETRY')
        monkeypatch.setattr('orchestrator.research_task_authority._verify',failed)
    with pytest.raises(ValueError):reconsider.original(config,client)


def test_captured_criticism_and_required_proof_cannot_be_omitted(monkeypatch):
    from orchestrator import disposition_context,scientific_runtime_prerequisites as guard
    monkeypatch.setattr(disposition_context,'_selected_evidence',lambda *a:{'verified_events':[{'event':reconsider.candidate()}]})
    monkeypatch.setattr(reconsider,'disposition_event',lambda *a:reconsider.previous.DISPOSITION)
    with pytest.raises(ValueError,match='PROOF_DELIVERY_GUARD'):
        reconsider.verify_captured_originals({},'a'*40,{},[])
    with pytest.raises(ValueError,match='NOT_IN_CAPTURE'):
        reconsider.verify_captured_originals({},'a'*40,{'manifest':{'records':[]}},[reconsider.PREREQUISITE])


@pytest.mark.parametrize('failure',[None,'changed_packet','wrong_pin','incomplete','changed_prefix'])
def test_fixed_historical_capture_uses_native_prefix_and_original_packet(tmp_path,monkeypatch,failure):
    import hashlib
    from orchestrator import change_requests as changes, reviewed_history as history
    from orchestrator import disposition_context,scientific_evidence_access as access
    source='a'*40;store=tmp_path/'changes';actor={'kind':'human','identity':'synthetic'}
    req=changes.submit(store,tmp_path,'system:old-grant','Preserve original granted scope.',actor,
        source=source,scope_limits=['Synthetic only.'])
    folder=store/req['identity']
    changes.record(folder,'AUTHORIZED',actor,{'rationale':'Synthetic','authority_reference':{'test':True},'review_policy':'Synthetic'})
    state=changes.load(folder)
    prefix={k:v for k,v in history.boundary(state).items() if k in ('event_count','head_sha256','index_sha256')}
    old={'scientific_change_history':{'native_prefixes':{req['identity']:prefix}}}
    sha=hashlib.sha256(encoded(old)).hexdigest();monkeypatch.setattr(reconsider,'PACKET',sha)
    monkeypatch.setattr(reconsider.previous,'REQUEST',req['identity'])
    monkeypatch.setattr(disposition_context,'_selected_evidence',lambda *a:{'verified_events':[{'event':reconsider.candidate()}]})
    monkeypatch.setattr(reconsider,'disposition_event',lambda *a:reconsider.previous.DISPOSITION)
    reply={'status':'COMPLETE','packet':old,'packet_sha256':sha}
    if failure=='changed_packet':old['changed']=True
    if failure=='wrong_pin':reply['packet_sha256']='f'*64
    if failure=='incomplete':reply['status']='INCOMPLETE'
    if failure=='changed_prefix':
        prefix['head_sha256']='f'*64
        reply['packet_sha256']=hashlib.sha256(encoded(old)).hexdigest()
        monkeypatch.setattr(reconsider,'PACKET',reply['packet_sha256'])
    calls=[]
    def client(socket,operation,body):
        assert operation=='stage_packet';calls.append(body);return reply
    cap={'manifest':{'schema':access.SCHEMA,'source':source,'task_binding':'b'*64,
        'records':[],'request_heads':{}},'payloads':{}}
    if failure:
        with pytest.raises(ValueError):reconsider.capture_original_history({'change_request_store':str(store)}, {},source,cap,client)
    else:
        out=reconsider.capture_original_history({'change_request_store':str(store)}, {},source,cap,client)
        assert len(out['manifest']['records'])==3
        assert out['manifest']['request_heads'][req['identity']]['head_sha256']==state['head_sha256']
        assert encoded(old) in out['payloads'].values()
        assert cap['manifest']['records']==[]
        assert access.describe_capture(out)['record_count']==3
    assert len(calls)==1
