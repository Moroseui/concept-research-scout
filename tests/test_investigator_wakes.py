"""Synthetic state/provenance fixtures; no actual model or science is run."""
from contextlib import contextmanager, nullcontext
from copy import deepcopy
import hashlib
import json
import os
from pathlib import Path
import sqlite3
from types import SimpleNamespace

import pytest

from orchestrator import investigator_wakes as wakes, protected_investigator as protected
from orchestrator import continuing_research as continuing
from orchestrator.handover_coordinator import digest
from orchestrator.hosted_cycle import encoded, immutable
from orchestrator.operations_report import private_root


@pytest.fixture
def configured(tmp_path, monkeypatch):
    tmp_path.chmod(0o700)
    template = {'schema':wakes.TEMPLATE, 'template_id':'synthetic-charter-v1', 'experiment':'P002',
        'request':'Choose a useful bounded action from the synthetic saved evidence.',
        'evidence_file':str(tmp_path/'evidence.json'), 'evidence_sha256':'a'*64,
        'references':[], 'change_request':{'request_id':'b'*64,'applied_event':'c'*64}}
    config = {'source':'d'*40, 'source_root':str(tmp_path/'source'), 'state':str(tmp_path/'state'),
        'controller_uid':os.getuid(), 'controller_gid':os.getgid(), 'broker_socket':'synthetic',
        'continuing_operations':{'enabled':True},
        'investigator':{'template':template,'template_sha256':digest(template)}}
    monkeypatch.setattr('orchestrator.research_catalog.linked_change',lambda *args: {'synthetic':True})
    monkeypatch.setattr('orchestrator.handover_runtime.configuration',lambda *args,**kwargs: {'synthetic_science':'preserved'})
    return config


def bootstrap(config):
    sha = config['investigator']['template_sha256']
    return wakes.event('BOOTSTRAP',digest({'source':config['source'],'template_sha256':sha}),sha)


def manifest(config, values=None):
    core = {'schema':wakes.WAKE, 'source':config['source'],
        'template_sha256':config['investigator']['template_sha256'], 'events':values or [bootstrap(config)], 'day':'2026-09-11'}
    return {**core,'identity':digest(core)}


def runtime(config):
    state = private_root(config['state'])
    db = sqlite3.connect(state/'coordinator.sqlite',isolation_level=None)
    db.row_factory = sqlite3.Row
    db.execute('CREATE TABLE tasks(id TEXT PRIMARY KEY,status TEXT,binding TEXT)')
    return SimpleNamespace(config=config,q=SimpleNamespace(db=db,status=lambda:{'paused':False}))


def save_manifest(config, original):
    folder=private_root(private_root(wakes.directory(config))/original['identity'])
    immutable(folder/'wake.json',encoded(original))
    return folder


def test_exact_template_task_and_service_are_separate_from_scientific_actor(configured):
    original=manifest(configured)
    value=wakes.regenerate(configured,original,lambda *args:pytest.fail('Bootstrap invokes no provider'))
    assert value['task']['schema']==wakes.SCHEMA
    assert value['task']['selected_by'] is None
    assert value['evidence']['request_origin']['kind']=='service'
    assert 'model' not in value['evidence']['request_origin']
    assert value['evidence']['installed_charter_evidence']=={'synthetic_science':'preserved'}
    changed=deepcopy(configured);changed['investigator']['template']['request']='Changed request'
    with pytest.raises(ValueError,match='TEMPLATE_CHANGED'):wakes.setting(changed)
    for mutation in ({'selected_by':{'task':'a'*64,'artifact':'round-1/selection.json','sha256':'b'*64}}, {'mode':'readiness'}):
        with pytest.raises(ValueError,match='TEMPLATE_TASK_REQUIRED'):
            wakes.task_contract({**value['task'],**mutation})


def test_model_cannot_select_investigator_even_with_a_fresh_name(configured):
    task=wakes.regenerate(configured,manifest(configured),None)['task']
    proposed={'schema':continuing.SELECTION_SCHEMA,'status':'PROPOSE','rationale':'Synthetic',
        'reconsideration':'Synthetic','successor':{**{k:v for k,v in task.items() if k not in ('template_sha256','wake_sha256','purpose')},
            'schema':continuing.TASK_SCHEMA,'task_id':'different-investigator'}}
    with pytest.raises(ValueError,match='MODEL_SELECTED_INVESTIGATOR_FORBIDDEN'):continuing.selection(task,proposed)
    assert 'mode (adoption' in continuing.investigator_instruction(task)


def task_original(config, *, verdict='APPROVE', mode='discuss'):
    identity='e'*64
    task={'schema':continuing.TASK_SCHEMA,'task_id':'synthetic-task-v1','mode':mode,'experiment':'P002',
        'request':'Synthetic task','references':[],'selected_by':None}
    packet={'campaign_task':task};sha=hashlib.sha256(encoded(packet)).hexdigest()
    author=json.dumps({'discussion.md':'Synthetic original scientific discussion.'})
    review=json.dumps({'verdict':verdict,'rationale':'Synthetic opposing criticism.'})
    answers={'continuation':author,'review':json.dumps({'review.json':review}),'disposition':'Synthetic disposition.'}
    original={'status':'COMPLETE','packet':packet,'packet_sha256':sha}
    replies={}
    for stage,answer in answers.items():
        model='claude-fable-5' if stage=='review' else 'gpt-6-astra'
        replies[stage]={'status':'COMPLETE','answer':answer,'packet_sha256':sha,
            'receipt':{'requested_model':model,'actual_model':model if stage=='review' else None,'returncode':0,
                'stage':stage,'session_id':'synthetic-'+stage,
                'answer_sha256':hashlib.sha256(answer.encode()).hexdigest(),'operating_context_sha256':'f'*64}}
    disposition={'task':identity,'source':config['source'],'status':'DISPOSITION_RECORDED',
        'review_verdict':verdict,'acceptance_status':'APPROVED_PROPOSAL_ONLY' if verdict=='APPROVE' else 'NOT_ACCEPTED',
        'reviewer':{'session_id':'synthetic-review','model':'claude-fable-5'},
        'disposition_actor':{'session_id':'synthetic-disposition'},
        'disposition_sha256':hashlib.sha256(answers['disposition'].encode()).hexdigest(),
        'artifact_sha256':{'round-1/discussion.md':hashlib.sha256(json.loads(author)['discussion.md'].encode()).hexdigest(),
            'round-1/review.json':hashlib.sha256(review.encode()).hexdigest()}}
    folder=private_root(private_root(private_root(config['state'])/'tasks')/identity)
    immutable(folder/'packet.json',encoded(packet));immutable(folder/'scientific-disposition.json',encoded(disposition))
    def reader(socket,operation,body):
        assert operation in ('stage_packet','stage_status')
        assert body['event']['turn_id']==identity
        return deepcopy(original if operation=='stage_packet' else replies[body['stage']])
    return identity,reader,replies,original,disposition


@pytest.mark.parametrize('verdict',['APPROVE','REVISE','REQUEST_CHANGES'])
def test_task_wake_requires_original_review_and_preserves_negative_as_evidence(configured,verdict):
    identity,reader,replies,packet,disposition=task_original(configured,verdict=verdict)
    result=wakes._task(configured,identity,reader)
    assert result['review']['verdict']==verdict
    assert result['predecessor']['requires']=='DISPOSITION_RECORDED'
    replies['review']['receipt']['actual_model']='unverified-reviewer'
    with pytest.raises(ValueError,match='REVIEW_MODEL'):wakes._task(configured,identity,reader)


def test_locally_edited_original_packet_or_artifact_cannot_wake(configured):
    identity,reader,replies,original,disposition=task_original(configured)
    path=Path(configured['state'])/'tasks'/identity/'packet.json'
    packet=json.loads(path.read_bytes());packet['campaign_task']['request']='Changed private copy'
    path.write_bytes(encoded(packet))
    with pytest.raises(ValueError,match='ORIGINAL_PACKET_CHANGED'):wakes._task(configured,identity,reader)


@pytest.fixture
def protected_fixture(configured,tmp_path,monkeypatch):
    path=tmp_path/'protected-synthetic.sqlite'
    def database(broker,**kwargs):
        db=sqlite3.connect(path,isolation_level=None);db.row_factory=sqlite3.Row
        db.executescript('CREATE TABLE IF NOT EXISTS wakes(identity TEXT PRIMARY KEY,original BLOB); CREATE TABLE IF NOT EXISTS events(identity TEXT PRIMARY KEY,original BLOB,wake TEXT);')
        return db
    monkeypatch.setattr(protected,'_database',database)
    monkeypatch.setattr(protected,'os',SimpleNamespace(getuid=lambda:0,read=os.read))
    monkeypatch.setattr('orchestrator.protected_scientific_jobs.controller_configuration',lambda broker:configured)
    monkeypatch.setattr('orchestrator.protected_scientific_jobs.admission_guard',lambda *args:nullcontext())
    checked=[]
    def verify(broker,config,mode,values):
        checked.extend(values)
        return {'status':'VERIFIED_EVENTS','source':config['source'],
            'template_sha256':config['investigator']['template_sha256'],'events':values}
    monkeypatch.setattr(protected,'verify_subprocess',verify)
    return SimpleNamespace(config={}),checked,path


def test_each_event_is_reserved_once_even_when_batches_overlap(configured,protected_fixture):
    broker,checked,path=protected_fixture
    one=wakes.event('TASK','1'*64,'2'*64);two=wakes.event('TASK','3'*64,'4'*64)
    first=protected.handle(broker,'reserve_investigator',{'events':[one]})
    second=protected.handle(broker,'reserve_investigator',{'events':[one,two]})
    assert first['wake']['events']==[one] and second['wake']['events']==[two]
    duplicate=protected.handle(broker,'reserve_investigator',{'events':[two,one]})
    assert duplicate['status']=='NO_NEW_EVENTS'
    assert set(duplicate['existing_wakes'])=={first['wake']['identity'],second['wake']['identity']}
    db=sqlite3.connect(path)
    assert db.execute('SELECT count(*) FROM events').fetchone()[0]==2
    assert protected.handle(broker,'read_investigator_wake',{'wake':first['wake']['identity']})['wake']==first['wake']
    changed={**one,'original_sha256':'5'*64}
    with pytest.raises(ValueError,match='CONSUMED_EVENT_CHANGED'):
        protected.handle(broker,'reserve_investigator',{'events':[changed]})


def test_reservation_transaction_rolls_back_all_new_claims_on_conflict(configured,protected_fixture):
    broker,_,path=protected_fixture
    one=wakes.event('TASK','1'*64,'2'*64);two=wakes.event('TASK','3'*64,'4'*64)
    protected.handle(broker,'reserve_investigator',{'events':[one]})
    with pytest.raises(ValueError,match='CONSUMED_EVENT_CHANGED'):
        protected.handle(broker,'reserve_investigator',{'events':[two,{**one,'original_sha256':'5'*64}]})
    assert sqlite3.connect(path).execute('SELECT count(*) FROM events').fetchone()[0]==1


def test_pause_stops_authority_and_does_not_claim_a_model_outcome(configured,monkeypatch):
    r=runtime(configured);original=manifest(configured);save_manifest(configured,original)
    r.q.status=lambda:{'paused':True}
    monkeypatch.setattr('orchestrator.research_task_authority.execute',lambda *args,**kwargs:pytest.fail('Paused authority'))
    assert wakes.advance(r)['status']=='PAUSED'
    assert wakes.status(configured)['wakes'][0]['status']=='ELIGIBILITY_PENDING'


def test_started_authority_is_never_implicitly_retried_but_new_evidence_remains_possible(configured,monkeypatch):
    r=runtime(configured);original=manifest(configured);folder=save_manifest(configured,original)
    immutable(folder/'authority-started.json',encoded({'synthetic_interruption':True}))
    monkeypatch.setattr('orchestrator.research_task_authority.execute',lambda *args,**kwargs:pytest.fail('No implicit retry'))
    assert wakes.advance(r)['status']=='WAITING_FOR_NEW_EVIDENCE'
    assert wakes.status(configured)['wakes'][0]['status']=='RECONCILIATION_REQUIRED'
    assert not wakes._pending(r)
    with pytest.raises(ValueError,match='REGULAR_FILE_REQUIRED'):wakes.recover(r,original['identity'])


def test_authority_then_registration_are_distinct_saved_steps(configured,monkeypatch):
    r=runtime(configured);original=manifest(configured);folder=save_manifest(configured,original)
    calls=[]
    monkeypatch.setattr(wakes,'_client',lambda runtime:lambda socket,op,body:{'wake':original})
    fake_entry={'request':{'task':{'task_id':'synthetic-next'}},'eligibility':{'path':'original','sha256':'0'*64}}
    monkeypatch.setattr(wakes,'_entry',lambda *args:deepcopy(fake_entry))
    outcome={'status':'AGENT_REVIEWED_DECISION_READY','eligibility':{'path':'original','sha256':'f'*64}}
    monkeypatch.setattr('orchestrator.research_task_authority.execute',lambda *args,**kwargs:calls.append('authority') or outcome)
    def submit(runtime,entry):
        assert entry['eligibility']==outcome['eligibility']
        calls.append('register-submit');return {'submission':{'task':'a'*64,'status':'QUEUED'}}
    monkeypatch.setattr(continuing,'register_and_submit',submit)
    assert wakes.advance(r)['status']=='ELIGIBILITY_RECORDED'
    assert calls==['authority']
    assert wakes.advance(r)['status']=='INVESTIGATOR_SUBMITTED'
    assert calls==['authority','register-submit']
    assert wakes.advance(r)['status']=='WAITING_FOR_NEW_EVIDENCE'
    assert (folder/'authority-started.json').is_file()


def test_deferral_and_historical_wake_do_not_rearm(configured,monkeypatch):
    r=runtime(configured);original=manifest(configured);folder=save_manifest(configured,original)
    immutable(folder/'authority.json',encoded({'status':'AGENT_REVIEWED_DEFERRAL'}))
    assert wakes.status(configured)['wakes'][0]['status']=='DEFERRED'
    changed={**configured,'source':'f'*40}
    assert wakes.status(changed)['wakes'][0]['status']=='HISTORICAL_READ_ONLY'
    monkeypatch.setattr('orchestrator.research_task_authority.execute',lambda *args,**kwargs:pytest.fail('No deferred retry'))
    assert wakes.advance(r)['status']=='WAITING_FOR_NEW_EVIDENCE'


def test_protocol_allowance_is_exact_and_still_requires_available_reference_membership(configured):
    task=wakes.regenerate(configured,manifest(configured),None)['task']
    protocol={'subject':'synthetic-protocol','bindings':{'experiment':'P002'},'decision_path':'/synthetic/decision.json','decision_sha256':'1'*64}
    successor={'schema':continuing.PROSPECTIVE_SCHEMA,'task_id':'synthetic-next','experiment':'P002',
        'mode':'propose','request':'Synthetic proposal','references':[],'selected_by':None,'protocol':protocol}
    proposal={'schema':continuing.SELECTION_SCHEMA,'status':'PROPOSE','rationale':'Synthetic','reconsideration':'Synthetic','successor':successor}
    with pytest.raises(ValueError,match='PROTOCOL_NOT_IN_INVESTIGATOR_CONTEXT'):continuing.selection(task,proposal)
    assert continuing.selection(task,proposal,protocols=[protocol])==proposal
    successor['references']=[{'task':'2'*64,'artifact':'round-1/proposal.md','sha256':'3'*64}]
    with pytest.raises(ValueError,match='REFERENCE_NOT_IN_INVESTIGATOR_CONTEXT'):
        continuing.selection(task,proposal,protocols=[protocol])


@pytest.mark.parametrize('verdict',['APPROVE','REQUEST_CHANGES'])
def test_new_template_uses_existing_pipeline_and_original_only_recovery(configured,tmp_path,monkeypatch,verdict):
    from orchestrator.hosted_campaign import BrokerStages,run_pipeline,recover_projection
    from orchestrator.hosted_campaign_task import completed_pipeline,task_contract
    from test_hosted_campaign import client_for
    task=wakes.regenerate(configured,manifest(configured),None)['task']
    source=Path(__file__).resolve().parents[1]
    context=wakes.grounding(source,task)
    assert not any('interpretation_receipt.json' in name for name in context)
    assert json.loads(context['investigator-scope.json'])['scientific_approval'] is False
    protocol={'subject':'synthetic-protocol','bindings':{'experiment':'P002'},
        'decision_path':'/synthetic/decision.json','decision_sha256':'1'*64}
    successor={'schema':continuing.PROSPECTIVE_SCHEMA,'task_id':'synthetic-next','experiment':'P002',
        'mode':'propose','request':'Synthetic next formal operation','references':[],'selected_by':None,'protocol':protocol}
    choice={'schema':continuing.SELECTION_SCHEMA,'status':'PROPOSE','rationale':'Synthetic','reconsideration':'Synthetic','successor':successor}
    supplement={'continuing-research-inputs.json':json.dumps({'task':task,'references':[],'eligible_protocols':[protocol],'protocol_blocks':[]},sort_keys=True)}
    packet={'campaign_task':task,'campaign_artifacts':task_contract(task)}
    client,calls=client_for([json.dumps({'selection.json':json.dumps(choice)}),
        json.dumps({'review.json':json.dumps({'verdict':verdict,'rationale':'Synthetic opposing review'})})])
    originals={}
    def capture(socket,operation,body):
        reply=client(socket,operation,body);originals[body['stage']]=reply;return reply
    monkeypatch.setattr('orchestrator.campaign_pipeline.grounding',lambda *args,**kwargs:context)
    monkeypatch.setattr('orchestrator.research_context.evidence_context',lambda *args,**kwargs:{})
    output=tmp_path/'pipeline-root/campaigns/isles24-pilot/pipeline/original'
    sc=SimpleNamespace(ROOT=tmp_path/'pipeline-root')
    receipt=run_pipeline(sc,'investigate',task['request'],output,BrokerStages('fixture',{},packet,client=capture),supplement=supplement)
    assert receipt['acceptance_status']==('APPROVED_PROPOSAL_ONLY' if verdict=='APPROVE' else 'NOT_ACCEPTED')
    completed_pipeline(sc.ROOT,output,packet,{},supplement=supplement)
    before={str(p.relative_to(output)):p.read_bytes() for p in output.rglob('*') if p.is_file()}
    def retrieve(socket,operation,body):
        assert operation=='stage_status';return {**originals[body['stage']],'duplicate':True}
    projected=output.parent/'recovered'
    recovered=recover_projection(sc,'investigate',task['request'],output,projected,
        BrokerStages('fixture',{},packet,client=retrieve,recovery=True),supplement=supplement)
    assert recovered['acceptance_status']==receipt['acceptance_status']
    assert calls==['continuation','review']
    assert {str(p.relative_to(output)):p.read_bytes() for p in output.rglob('*') if p.is_file()}==before


def test_completed_normal_task_wakes_once_after_prior_investigator_defers(configured,protected_fixture,monkeypatch):
    broker,_,database=protected_fixture
    r=runtime(configured)
    identity,task_reader,_,_,_=task_original(configured,verdict='REQUEST_CHANGES')
    r.q.db.execute('INSERT INTO tasks VALUES(?,?,?)',(identity,'COMPLETE','{}'))
    first=protected.handle(broker,'reserve_investigator',{'events':[bootstrap(configured)]})['wake']
    immutable(save_manifest(configured,first)/'authority.json',encoded({'status':'AGENT_REVIEWED_DEFERRAL'}))
    calls=[]
    def read(socket,operation,body):
        calls.append(operation)
        if operation in ('reserve_investigator','read_investigator_wake'):
            return protected.handle(broker,operation,body)
        if operation=='list_recorded_steering':return {'status':'COMPLETE','requests':[],'blocked':[]}
        return task_reader(socket,operation,body)
    def verify(broker,config,mode,values):
        wakes.verify_events(config,values,read)
        return {'status':'VERIFIED_EVENTS','source':config['source'],
            'template_sha256':config['investigator']['template_sha256'],'events':values}
    monkeypatch.setattr(protected,'verify_subprocess',verify)
    monkeypatch.setattr(wakes,'_client',lambda runtime:read)
    monkeypatch.setattr('orchestrator.protected_scientific_jobs.read_observation',lambda config:{'events':[]})
    result=wakes.discover(r);assert result['status']=='ELIGIBILITY_PENDING'
    folder=wakes.directory(configured)/result['wake']
    saved=json.loads((folder/'wake.json').read_bytes())
    derived=wakes.regenerate(configured,saved,read)
    assert derived['evidence']['verified_events'][0]['review']['verdict']=='REQUEST_CHANGES'
    assert derived['task']['references'][0]['task']==identity
    assert wakes.discover(r)['status']=='INVESTIGATOR_ALREADY_PENDING'
    immutable(folder/'authority.json',encoded({'status':'AGENT_REVIEWED_DEFERRAL'}))
    assert wakes.discover(r)['status']=='WAITING_FOR_NEW_EVIDENCE'
    assert sqlite3.connect(database).execute('SELECT count(*) FROM wakes').fetchone()[0]==2
    assert 'model_stage' not in calls and 'admit_server' not in calls
    assert wakes.status(configured)['observation']['status']=='WAITING_FOR_NEW_EVIDENCE'


def steering_original(identity='1'*64):
    from orchestrator.change_requests import encoded as request_bytes
    core={'request_id':identity,'request':{'text':'Assess this recorded synthetic proposal substantively.'},
          'provenance':{'comment':'synthetic-original','authority':'PROPOSAL_ONLY'}}
    return {**core,'original_sha256':hashlib.sha256(request_bytes(core)).hexdigest()}


def test_recorded_steering_reopens_deferral_once_and_superseded_original_cannot_authorize(configured,protected_fixture,monkeypatch):
    broker,_,database=protected_fixture;r=runtime(configured)
    prior=protected.handle(broker,'reserve_investigator',{'events':[bootstrap(configured)]})['wake']
    immutable(save_manifest(configured,prior)/'authority.json',encoded({'status':'AGENT_REVIEWED_DEFERRAL'}))
    original=steering_original();current=[original];calls=[]
    def read(socket,operation,body):
        calls.append(operation)
        if operation in ('reserve_investigator','read_investigator_wake'):return protected.handle(broker,operation,body)
        if operation=='list_recorded_steering':return {'status':'COMPLETE','requests':[
            {key:row[key] for key in ('request_id','original_sha256')} for row in current],'blocked':[]}
        if operation=='read_recorded_steering':
            if not current or body['request_id'] != current[0]['request_id']:
                raise ValueError('RECORDED_STEERING_SUPERSEDED')
            return deepcopy(current[0])
        pytest.fail('Unexpected operation '+operation)
    def verify(broker,config,mode,values):
        wakes.verify_events(config,values,read)
        return {'status':'VERIFIED_EVENTS','source':config['source'],
            'template_sha256':config['investigator']['template_sha256'],'events':values}
    monkeypatch.setattr(protected,'verify_subprocess',verify)
    monkeypatch.setattr(wakes,'_client',lambda runtime:read)
    monkeypatch.setattr('orchestrator.protected_scientific_jobs.read_observation',lambda config:{'events':[]})
    result=wakes.discover(r);assert result['status']=='ELIGIBILITY_PENDING'
    folder=wakes.directory(configured)/result['wake'];saved=json.loads((folder/'wake.json').read_bytes())
    derived=wakes.regenerate(configured,saved,read)
    assert derived['evidence']['verified_events'][0]['recorded_proposal']==original
    assert derived['evidence']['verified_events'][0]['proposal_only'] is True
    entry=wakes._entry(r,folder,saved)
    current[:]=[steering_original('2'*64)]
    with pytest.raises(ValueError,match='SUPERSEDED'):wakes.verify_entry(configured,entry,read)
    immutable(folder/'authority.json',encoded({'status':'AGENT_REVIEWED_DEFERRAL'}))
    edited=wakes.discover(r);assert edited['status']=='ELIGIBILITY_PENDING' and edited['wake']!=result['wake']
    immutable(wakes.directory(configured)/edited['wake']/'authority.json',encoded({'status':'AGENT_REVIEWED_DEFERRAL'}))
    assert wakes.discover(r)['status']=='WAITING_FOR_NEW_EVIDENCE'
    assert sqlite3.connect(database).execute('SELECT count(*) FROM events').fetchone()[0]==3
    assert 'model_stage' not in calls


def failure_original(config, tmp_path, *, mode='readiness'):
    from test_protected_handover import broker
    from test_server_admission import server
    b=broker(tmp_path);model_event={**server(7),'source':config['source']};b.config['sources']=[config['source']]
    packet={'campaign_task':{'schema':continuing.TASK_SCHEMA,'task_id':'synthetic-ended-task',
        'mode':mode,'experiment':'P002','request':'Inspect synthetic evidence.','references':[],'selected_by':None}}
    root=Path(b.config['turn_root']);folder=root/(model_event['turn_id']+'-1');folder.mkdir(parents=True)
    (root/'branch.lock').touch()
    raw=encoded(packet);packet_sha=hashlib.sha256(raw).hexdigest()
    (folder/'binding.json').write_bytes(encoded({'event':model_event,'packet_sha256':packet_sha}))
    (folder/'packet.json').write_bytes(raw)
    (folder/'continuation.started.json').write_bytes(encoded({'stage':'continuation','requested_model':'gpt-6-astra',
        'started_utc':'2026-09-11T00:00:00+00:00','timeout_seconds':600}))
    (folder/'continuation.ended.json').write_bytes(encoded({'returncode':-9,'ended_utc':'2026-09-11T00:10:00+00:00'}))
    for suffix in ('.input.md','.stdout','.stderr','.operating-context.json'):
        (folder/('continuation'+suffix)).write_bytes(b'Synthetic preserved transport bytes')
    local=private_root(private_root(private_root(config['state'])/'tasks')/model_event['turn_id'])
    immutable(local/'packet.json',raw)
    return b,model_event,folder


def test_ended_failure_original_is_discussion_only_and_no_provider_retry(configured,tmp_path,monkeypatch):
    r=runtime(configured);b,event,folder=failure_original(configured,tmp_path)
    r.q.db.execute('INSERT INTO tasks VALUES(?,?,?)',(event['turn_id'],'BLOCKED',json.dumps({'source':configured['source']})))
    calls=[]
    def reader(socket,operation,body):
        calls.append(operation)
        if operation=='stage_packet':return b.stage_packet(body)
        if operation=='stage_failure':return protected.stage_failure(b,body)
        pytest.fail('No stage retry or fabricated completion')
    result=wakes._failure(configured,event['turn_id'],reader)
    assert result['transport_failure']['ended']['returncode']==-9
    assert result['transport_failure']['actual_model'] is None and result['scientific_outcome']=='UNKNOWN'
    derived=wakes.regenerate(configured,manifest(configured,[result['event']]),reader)
    task=derived['task'];assert task['purpose']=='FAILURE_DIAGNOSIS'
    selected={'schema':continuing.SELECTION_SCHEMA,'status':'PROPOSE','rationale':'Synthetic diagnostic reason',
        'reconsideration':'Only a separately reviewed next version could proceed.',
        'successor':{'schema':continuing.TASK_SCHEMA,'task_id':'synthetic-diagnostic-discussion','experiment':'P002',
            'mode':'discuss','request':'Discuss the actual ended transport evidence.','references':[],'selected_by':None}}
    assert continuing.selection(task,selected)==selected
    changed=deepcopy(selected);changed['successor']['mode']='readiness'
    with pytest.raises(ValueError,match='DISCUSSION_ONLY_NO_RETRY'):continuing.selection(task,changed)
    changed['successor']={'schema':'continuing-operation/v1','kind':'LAUNCH_JOB'}
    with pytest.raises(ValueError,match='DISCUSSION_ONLY_NO_RETRY'):continuing.selection(task,changed)
    assert 'Never retry' in continuing.investigator_instruction(task)
    assert set(calls)=={'stage_packet','stage_failure'}
    (folder/'continuation.ended.json').rename(folder/'preserved-ended.json')
    with pytest.raises(ValueError,match='ENDED_ORIGINAL_FAILURE_REQUIRED'):wakes._failure(configured,event['turn_id'],reader)


def test_failure_reader_requires_idle_writer_and_cannot_wake_an_investigator(configured,tmp_path):
    import fcntl
    r=runtime(configured);b,event,folder=failure_original(configured,tmp_path,mode='investigate')
    r.q.db.execute('INSERT INTO tasks VALUES(?,?,?)',(event['turn_id'],'BLOCKED',json.dumps({'source':configured['source']})))
    with (folder.parent/'branch.lock').open('rb') as stream:
        fcntl.flock(stream,fcntl.LOCK_EX|fcntl.LOCK_NB)
        assert protected.stage_failure(b,{'event':event})['status']=='MODEL_WRITER_ACTIVE_RECONCILE_NO_RETRY'
    assert protected.stage_failure(b,{'event':event})['status']=='ENDED_WITHOUT_VALIDATED_STAGE'
    def reader(socket,operation,body):
        assert operation=='stage_packet';return b.stage_packet(body)
    with pytest.raises(ValueError,match='SELF_TRIGGER_FORBIDDEN'):wakes._failure(configured,event['turn_id'],reader)


def test_unusable_historical_protocol_is_visible_without_blocking_independent_context(configured,monkeypatch):
    task=wakes.regenerate(configured,manifest(configured),None)['task']
    descriptor={'subject':'historical','bindings':{'experiment':'P002'},'decision_path':'/historical/decision.json','decision_sha256':'1'*64}
    packet={'campaign_task':task,'continuing_context':{'continuing_operations':{'completed':[
        {'kind':'AUTHORIZE_PROTOCOL','reference':{'operation':'2'*64,'result_sha256':'3'*64},'result':{'protocol':descriptor}}]}}}
    def changed(*args,**kwargs):raise ValueError('CONTINUING_COMPLETED_OPERATION_BINDING_REQUIRED')
    monkeypatch.setattr('orchestrator.continuing_operations.read_operation_result',changed)
    context=continuing.supplemental_context(configured,task,packet=packet,original_client=lambda *args:pytest.fail('Unavailable old protocol'))
    value=json.loads(context['continuing-research-inputs.json'])
    assert value['eligible_protocols']==[] and value['protocol_blocks'][0]['operation']=='2'*64
    continuing.checked_supplement(task,context)
    with pytest.raises(ValueError,match='COMPLETED_OPERATION_BINDING_REQUIRED'):
        continuing.observed_protocols(configured,packet,desired=descriptor)


def test_ended_blocked_task_reserves_one_diagnostic_wake_without_retry(configured,protected_fixture,tmp_path,monkeypatch):
    broker,_,database=protected_fixture;r=runtime(configured)
    original_broker,model_event,folder=failure_original(configured,tmp_path)
    r.q.db.execute('INSERT INTO tasks VALUES(?,?,?)',(model_event['turn_id'],'BLOCKED',json.dumps({'source':configured['source']})))
    prior=protected.handle(broker,'reserve_investigator',{'events':[bootstrap(configured)]})['wake']
    immutable(save_manifest(configured,prior)/'authority.json',encoded({'status':'AGENT_REVIEWED_DEFERRAL'}))
    calls=[]
    def read(socket,operation,body):
        calls.append(operation)
        if operation in ('reserve_investigator','read_investigator_wake'):return protected.handle(broker,operation,body)
        if operation=='stage_packet':return original_broker.stage_packet(body)
        if operation=='stage_failure':return protected.stage_failure(original_broker,body)
        if operation=='list_recorded_steering':return {'status':'COMPLETE','requests':[],'blocked':[]}
        pytest.fail('No model or task retry')
    def verify(broker,config,mode,values):
        wakes.verify_events(config,values,read)
        return {'status':'VERIFIED_EVENTS','source':config['source'],
            'template_sha256':config['investigator']['template_sha256'],'events':values}
    monkeypatch.setattr(protected,'verify_subprocess',verify)
    monkeypatch.setattr(wakes,'_client',lambda runtime:read)
    monkeypatch.setattr('orchestrator.protected_scientific_jobs.read_observation',lambda config:{'events':[]})
    result=wakes.discover(r);assert result['status']=='ELIGIBILITY_PENDING'
    saved=wakes.directory(configured)/result['wake']
    assert json.loads((saved/'wake.json').read_bytes())['events'][0]['kind']=='FAILURE'
    immutable(saved/'authority.json',encoded({'status':'AGENT_REVIEWED_DEFERRAL'}))
    assert wakes.discover(r)['status']=='WAITING_FOR_NEW_EVIDENCE'
    assert sqlite3.connect(database).execute('SELECT count(*) FROM events').fetchone()[0]==2
    assert r.q.db.execute('SELECT status FROM tasks').fetchone()[0]=='BLOCKED'
    assert 'model_stage' not in calls and 'admit_server' not in calls


def test_fixed_verifier_pipe_runs_actual_child_and_only_original_reads(configured,tmp_path,monkeypatch):
    """Exercise real pipe/process framing; UID switching is a separate deployment check."""
    import subprocess
    from test_change_requests import case,authority,application,review
    _,store,folder,request=case.__wrapped__(tmp_path)
    authority(folder);applied=application(folder,tmp_path);review(folder,applied,tmp_path)
    config=deepcopy(configured);config['change_request_store']=str(store)
    config['investigator']['template']['change_request']={'request_id':request['identity'],'applied_event':applied['identity']}
    config['investigator']['template_sha256']=digest(config['investigator']['template'])
    original=steering_original();reads=[]
    def originals(broker,operation,body):
        reads.append(operation)
        assert operation=='read_recorded_steering' and body=={'request_id':original['request_id']}
        return original
    monkeypatch.setattr(protected,'original',originals)
    monkeypatch.setattr('orchestrator.remote_supervisor.checked_source',lambda *args:Path(__file__).resolve().parents[1])
    monkeypatch.setattr(protected,'os',SimpleNamespace(getuid=lambda:0,read=os.read))
    launch=subprocess.Popen
    def same_user_transport(args,**kwargs):
        assert args[-3:]==['-m','orchestrator.protected_investigator','--verify']
        assert callable(kwargs.pop('preexec_fn'))  # Cannot change IDs in this unprivileged fixture.
        return launch(args,**kwargs)
    monkeypatch.setattr(subprocess,'Popen',same_user_transport)
    events=[bootstrap(config),wakes.event('STEERING',original['request_id'],original['original_sha256'])]
    assert protected.verify_subprocess(None,config,'events',events)=={'status':'VERIFIED_EVENTS',
        'source':config['source'],'template_sha256':config['investigator']['template_sha256'],'events':events}
    assert reads==['read_recorded_steering']


def test_unrelated_operation_reconciliation_does_not_block_an_eligible_investigator(configured,monkeypatch):
    from orchestrator.handover_runtime import Runtime
    instance=SimpleNamespace(config=configured,deployment_status=lambda:{'status':'INSTALLED_REVIEW_VERIFIED'})
    monkeypatch.setattr('orchestrator.authority_replacements.advance',lambda runtime:
        {'status':'NO_REPLACEMENT_WORK','models':0})
    monkeypatch.setattr('orchestrator.continuing_operations.advance',lambda runtime:
        {'status':'OPERATIONS_REQUIRE_RECONCILIATION','blocked_operations':['e'*64]})
    monkeypatch.setattr(wakes,'advance',lambda runtime:{'status':'ELIGIBILITY_RECORDED','wake':'f'*64})
    result=Runtime.continuing_step(instance)
    assert result=={'status':'ELIGIBILITY_RECORDED','wake':'f'*64,'blocked_operations':['e'*64]}


@contextmanager
def native_original_socket(reply):
    """Actual local transport only; responses are synthetic original evidence."""
    import socket
    import tempfile
    import threading
    calls = []; errors = []; stopped = threading.Event()
    with tempfile.TemporaryDirectory(prefix='wake-socket-') as directory:
        path = str(Path(directory) / 'broker.sock')
        with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as server:
            server.bind(path); server.listen(); server.settimeout(0.1)
            def serve():
                while not stopped.is_set():
                    try:
                        connection, _ = server.accept()
                    except socket.timeout:
                        continue
                    try:
                        with connection:
                            connection.settimeout(2)
                            raw = b''
                            while not raw.endswith(b'\n'):
                                chunk = connection.recv(65536)
                                if not chunk: raise ValueError('Incomplete synthetic request')
                                raw += chunk
                            request = json.loads(raw); calls.append(request)
                            connection.sendall(encoded(reply(request['operation'], request['body'])))
                    except Exception as error:
                        errors.append(error)
                        return
            worker = threading.Thread(target=serve, daemon=True); worker.start()
            try:
                yield path, calls
            finally:
                stopped.set(); worker.join(timeout=3)
                assert not worker.is_alive()
                assert not errors


@pytest.mark.parametrize('route', ['register_and_submit', 'default_eligibility'])
def test_native_registration_routes_reach_protected_refusal(configured, route):
    from orchestrator import research_task_authority
    original = manifest(configured)
    entry = wakes._entry(runtime(configured), save_manifest(configured, original), original)
    submitted = []
    caller = SimpleNamespace(config=configured,
        submit_research=lambda *args, **kwargs: submitted.append((args, kwargs)))
    with native_original_socket(lambda operation, body: {'status': 'NOT_RESERVED'}) as (path, calls):
        configured['broker_socket'] = path
        # Keep both production validation entrypoints and the real AF_UNIX client.
        with pytest.raises(ValueError, match='INVESTIGATOR_PROTECTED_EVENT_RESERVATION_REQUIRED'):
            if route == 'register_and_submit':
                continuing.register_and_submit(caller, entry)
            else:
                research_task_authority.verify_eligibility(configured, entry)
        assert calls == [{'operation': 'read_investigator_wake',
                          'body': {'wake': original['identity']}}]
        assert submitted == []
        if route == 'register_and_submit':
            stale = deepcopy(entry); stale['source'] = 'f' * 40
            with pytest.raises(ValueError, match='CURRENT_SUCCESSOR_SOURCE_REQUIRED'):
                continuing.register_and_submit(caller, stale)
            assert len(calls) == 1  # Stale source is refused before transport.
            assert submitted == []


def test_native_verify_entry_binds_nested_original_reads(configured):
    from orchestrator.handover_runtime import request_broker
    identity, original_reader, _, _, _ = task_original(configured, verdict='REQUEST_CHANGES')
    checked_task = wakes._task(configured, identity, original_reader)
    original = manifest(configured, [checked_task['event']])
    def reply(operation, body):
        if operation == 'read_investigator_wake':
            assert body == {'wake': original['identity']}
            return {'status': 'RESERVED', 'wake': original}
        return original_reader('', operation, body)
    with native_original_socket(reply) as (path, calls):
        configured['broker_socket'] = path
        entry = wakes._entry(runtime(configured), save_manifest(configured, original), original)
        calls.clear()
        verified = wakes.verify_entry(configured, entry, request_broker)
        assert verified['task'] == entry['request']['task']
        assert verified['evidence']['verified_events'][0]['review']['verdict'] == 'REQUEST_CHANGES'
        assert calls[0]['operation'] == 'read_investigator_wake'
        assert {'stage_packet', 'stage_status'} <= {call['operation'] for call in calls}
        assert {call['operation'] for call in calls} <= {
            'read_investigator_wake', 'stage_packet', 'stage_status'}
