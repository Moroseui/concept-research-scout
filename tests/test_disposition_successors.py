"""A linked disposition preserves old science and has no implicit retry path."""
from contextlib import contextmanager
from copy import deepcopy
import hashlib
import json
import os
import sqlite3
from pathlib import Path
from types import SimpleNamespace

import pytest

from orchestrator import disposition_successors as d, investigator_wakes as wakes
from orchestrator.hosted_cycle import encoded
from orchestrator.handover_coordinator import digest

OLD = 'a' * 64
SOURCE = '2' * 40
OLD_SOURCE = '1' * 40
HASH = 'b' * 64
sha = lambda raw: hashlib.sha256(raw).hexdigest()


def response(stage, content, packet_sha=HASH):
    return {'status':'COMPLETE','duplicate':True,'answer':content,'packet_sha256':packet_sha,
        'receipt':{'stage':stage,'requested_model':'claude-fable-5' if stage=='review' else 'gpt-6-astra',
            'actual_model':'claude-fable-5' if stage=='review' else None,'returncode':0,
            'session_id':'original-review-session' if stage=='review' else 'original-author-session',
            'model_evidence':'original provider protocol','answer_sha256':sha(content.encode()),
            'input_sha256':HASH,'operating_context_sha256':HASH}}


def original(verdict='APPROVE'):
    packet={'campaign_task':{'schema':'continuing-research-task/v1','mode':'discuss',
        'task_id':'comparison-v1','experiment':'P001','references':[]},'reviewer_evidence':{'limitation':'missing paired observations'}}
    request={'prompt_sha256':HASH}
    refusal={'status':'PREFLIGHT_INPUT_REFUSED','provider_calls':0,'automatic_retry':False,
        'measurement':{'stage':'disposition','family':'codex','characters':1048577,
            'limit_characters':1048576,'provider_calls':0,'input_sha256':HASH}}
    texts={'disposition.request.json':encoded(request).decode(),'disposition.input-refused.json':encoded(refusal).decode()}
    reply={'schema':'protected-disposition-refusal/v1','status':'PREFLIGHT_REFUSED_NO_PROVIDER',
        'event':d._event(OLD,OLD_SOURCE),'packet':packet,'packet_sha256':sha(encoded(packet)),
        'originals':texts,'file_sha256':{k:sha(v.encode()) for k,v in texts.items()},
        'stages':{s:response(s,json.dumps({name:body}),sha(encoded(packet))) for s,name,body in
            [('continuation','discussion.md','Original limited comparison.'),
             ('review','review.json',json.dumps({'verdict':verdict,'rationale':'Preserve missing evidence.'}))]},
        'active':False,'started':False,'answer_present':False,'receipt_present':False,'admissions':0}
    proof={'schema':'disposition-successor-original-proof/v1','origin_task':OLD,'origin_source':OLD_SOURCE,
        'origin_event':reply['event'],'packet':packet,'report':{'id':HASH,'text':'Original operational report'},
        'protected_original':{k:v for k,v in reply.items() if k!='packet'},
        'pipeline_receipt_sha256':HASH,'artifact_sha256':{},'eligibility':{'status':'ELIGIBLE'}}
    return packet,reply,proof


@pytest.fixture
def system(tmp_path,monkeypatch):
    state=tmp_path/'state';state.mkdir(mode=0o700)
    config={'state':str(state),'source':SOURCE,'source_root':str(tmp_path/'source'),
        'controller_uid':os.getuid(),'controller_gid':os.getgid(),'broker_socket':'fixed-socket'}
    by={'kind':'agent','family':'codex','model':'gpt-6-astra','session_id':'test-driver-original'}
    change={'request_id':'c'*64,'applied_event':'d'*64}
    history={'events':[{'identity':change['applied_event'],'event':'APPLIED',
        'payload':{'result_binding':{'source':SOURCE}}}],'request':{'identity':change['request_id']},'head_sha256':HASH}
    _,_,proof=original();calls=[];guards=[]
    monkeypatch.setattr(d,'_identity',lambda config:None)
    monkeypatch.setattr(d,'_change',lambda config,ref:deepcopy(history))
    monkeypatch.setattr(d,'_proof',lambda config,identity,client:deepcopy(proof))
    monkeypatch.setattr(d,'_measurement',lambda saved,value:({'input_sha256':HASH,'characters':700000},HASH))
    import orchestrator.campaign as campaign
    monkeypatch.setattr(campaign,'require_no_human_stop',lambda *args:None)
    def client(socket,operation,body):
        calls.append((operation,deepcopy(body)))
        if operation in ('model_stage','stage_status'):
            folder,saved,pr,h=d._load(config,OLD);value=d.packet(saved,pr,h)
            return response('disposition','Retain the proposal and its limitations; defer numerical ranking.',sha(encoded(value)))
        raise AssertionError(operation)
    monkeypatch.setattr(d,'_client',lambda runtime:client)
    import orchestrator.research_task_authority as authority
    @contextmanager
    def guard(*args,**kwargs):
        guards.append('admit');yield
    monkeypatch.setattr(authority,'_turn_guard',guard)
    runtime=SimpleNamespace(config=config,q=SimpleNamespace(status=lambda:{'paused':False}),deployment_status=lambda:None)
    return SimpleNamespace(runtime=runtime,config=config,by=by,change=change,history=history,proof=proof,
        client=client,calls=calls,guards=guards)


def save(s):
    return d.request(s.runtime,OLD,by=s.by,reason='Record the missing disposition only.',
        change_request=s.change,expected_source=SOURCE)


@pytest.mark.parametrize('verdict',['APPROVE','REVISE','REQUEST_CHANGES'])
def test_root_proof_preserves_actual_review(verdict):
    packet,reply,_=original(verdict)
    values=d._refusal(reply,d._event(OLD,OLD_SOURCE),packet)
    assert json.loads(values['review.json'])['verdict']==verdict


@pytest.mark.parametrize('field,value',[('active',True),('started',True),('answer_present',True),
    ('receipt_present',True),('admissions',1),('status','ENDED_WITHOUT_VALIDATED_STAGE'),('packet_sha256','e'*64)])
def test_refusal_near_misses_cannot_authorize_successor(field,value):
    packet,reply,_=original();reply[field]=value
    with pytest.raises(ValueError):d._refusal(reply,d._event(OLD,OLD_SOURCE),packet)


def test_exact_original_bytes_and_two_roles_required():
    packet,reply,_=original();reply['originals']['disposition.input-refused.json']+=' '
    with pytest.raises(ValueError,match='ORIGINAL_CHANGED'):d._refusal(reply,d._event(OLD,OLD_SOURCE),packet)
    packet,reply,_=original();reply['stages']['review']['receipt']['actual_model']=None
    with pytest.raises(ValueError,match='REVIEW_MODEL'):d._refusal(reply,d._event(OLD,OLD_SOURCE),packet)


def test_request_is_zero_model_deduplicated_and_conflicts_refuse(system):
    first=save(system);second=save(system)
    assert first['status']=='QUEUED' and second['duplicate'] and first['request']==second['request']
    assert system.calls==[] and system.guards==[]
    with pytest.raises(ValueError,match='ALREADY_SAVED'):
        d.request(system.runtime,OLD,by=system.by,reason='Different intent',change_request=system.change,expected_source=SOURCE)


def test_same_source_is_not_a_recovery_permission(system):
    system.proof['origin_source']=SOURCE
    with pytest.raises(ValueError,match='CHANGED_SOURCE'):save(system)
    assert not (d.directory(system.config)/OLD).exists()


def test_paused_advance_never_admits(system):
    save(system);system.runtime.q.status=lambda:{'paused':True}
    assert d.advance(system.runtime)['status']=='PAUSED'
    assert system.calls==[] and system.guards==[]


def test_one_disposition_then_typed_original_only_read(system):
    save(system);old=Path(system.config['state'])/'untouched-old-original';old.write_bytes(b'old scientific bytes')
    outcome=d.advance(system.runtime)
    assert outcome['status']=='COMPLETE' and outcome['new_model_calls']==1
    assert len(system.calls)==1 and system.calls[0][0]=='model_stage' and system.guards==['admit']
    assert d.advance(system.runtime)['status']=='NO_QUEUED_DISPOSITION_SUCCESSOR'
    value=d.read_result(system.config,OLD,system.client)
    assert value['result']['source']==SOURCE and value['result']['origin_source']==OLD_SOURCE
    assert value['result']['original_task_status']=='BLOCKED' and value['result']['new_scientific_authority'] is False
    assert system.calls[-1][0]=='stage_status' and old.read_bytes()==b'old scientific bytes'


def test_oversized_new_source_disposition_is_preserved_and_not_retried(system, monkeypatch):
    save(system)
    def oversized(socket, operation, body):
        system.calls.append((operation, deepcopy(body)))
        assert operation == 'model_stage'
        return response('disposition', 'x' * 30001, sha(encoded(body['packet'])))
    monkeypatch.setattr(d, '_client', lambda runtime: oversized)
    with pytest.raises(ValueError, match='DISPOSITION_ANSWER_CHARACTER_BOUND'):
        d.advance(system.runtime)
    folder = d.directory(system.config) / OLD
    assert (folder / 'started.json').exists() and (folder / 'failure.json').exists()
    assert not (folder / 'result.json').exists()
    assert d.status(system.config)['successors'][0]['status'] == 'RECONCILIATION_REQUIRED'
    assert d.advance(system.runtime)['status'] == 'NO_QUEUED_DISPOSITION_SUCCESSOR'
    assert len(system.calls) == len(system.guards) == 1


@pytest.mark.parametrize('answer', ['x' * 30000, 'x' * 24000 + '\u00e9' * 1000,
    'xx' + '\n' * 14999, '"' * 15000, '\\' * 15000, '\u00e9' * 5000, '\U0001f642' * 2500],
    ids=['ascii', 'mixed', 'newline', 'quote', 'backslash', 'unicode-bmp', 'unicode-non-bmp'])
def test_actual_result_checks_maximum_characters_without_truncation(system, answer):
    save(system); _, saved, proof, history = d._load(system.config, OLD)
    value = d.packet(saved, proof, history)
    result = d._result(saved, proof, value, response('disposition', answer, sha(encoded(value))))
    assert result['answer'] == answer
    assert d.DISPOSITION_ANSWER_CHARACTERS == 30000
    assert d.DISPOSITION_ANSWER_JSON_CHARACTERS == 30002
    assert len(json.dumps(answer, ensure_ascii=True)) == 30002
    assert 'at most 30000 characters and at most 30002 characters' in d.prompt(value)


@pytest.mark.parametrize('answer', ['x' + '\n' * 15000, 'x' + '"' * 15000,
    'x' + '\\' * 15000, 'x' + '\u00e9' * 5000, 'x' + '\U0001f642' * 2500,
    '\u00e9' * 12000], ids=['newline', 'quote', 'backslash', 'unicode-bmp', 'unicode-non-bmp', 'unicode-within80kb'])
def test_escaped_answer_within_old_limits_refuses_without_modification(system, answer):
    from orchestrator.hosted_campaign import checked_reply
    save(system); _, saved, proof, history = d._load(system.config, OLD)
    value = d.packet(saved, proof, history)
    reply = response('disposition', answer, sha(encoded(value)))
    before = encoded(reply)
    # These complete replies pass the real existing 80KB envelope guard. The
    # remaining serialized expansion, not a 180KB already-refused reply, matters.
    assert checked_reply(reply, 'disposition', sha(encoded(value)))[0] == answer
    assert len(answer) <= 30000 and len(json.dumps(answer, ensure_ascii=True)) > 30002
    with pytest.raises(ValueError, match='DISPOSITION_ANSWER_JSON_CHARACTER_BOUND'):
        d._result(saved, proof, value, reply)
    assert encoded(reply) == before


def test_existing_whole_reply_guard_still_refuses_180kb_unicode(system):
    save(system); _, saved, proof, history = d._load(system.config, OLD)
    value = d.packet(saved, proof, history)
    answer = '\u00e9' * 30000
    assert len(answer) == 30000 and len(json.dumps(answer)) == 180002
    with pytest.raises(ValueError, match='PUBLIC_TEXT_REJECTED'):
        d._result(saved, proof, value, response('disposition', answer, sha(encoded(value))))


def test_serialized_answer_refusal_preserves_start_and_never_retries(system, monkeypatch):
    save(system)
    reply_holder = []
    def oversized(socket, operation, body):
        system.calls.append((operation, deepcopy(body)))
        assert operation == 'model_stage'
        reply = response('disposition', 'x' + '\n' * 15000, sha(encoded(body['packet'])))
        reply_holder.append((reply, encoded(reply)))
        return reply
    monkeypatch.setattr(d, '_client', lambda runtime: oversized)
    with pytest.raises(ValueError, match='DISPOSITION_ANSWER_JSON_CHARACTER_BOUND'):
        d.advance(system.runtime)
    folder = d.directory(system.config) / OLD
    assert (folder / 'started.json').exists() and not (folder / 'result.json').exists()
    failure = json.loads((folder / 'failure.json').read_bytes())
    assert failure['reason'] == 'DISPOSITION_ANSWER_JSON_CHARACTER_BOUND' and not failure['automatic_retry']
    assert d.status(system.config)['successors'][0]['status'] == 'RECONCILIATION_REQUIRED'
    assert d.advance(system.runtime)['status'] == 'NO_QUEUED_DISPOSITION_SUCCESSOR'
    assert len(system.calls) == len(system.guards) == 1
    assert encoded(reply_holder[0][0]) == reply_holder[0][1]


def test_original_only_recovery_does_not_relax_serialized_answer_guard(system, monkeypatch):
    save(system); folder = d.directory(system.config) / OLD
    (folder / 'started.json').write_bytes(encoded({'request': d._load(system.config, OLD)[1]['identity']}))
    calls = []
    def original_reply(socket, operation, body):
        calls.append(operation)
        assert operation == 'stage_status'
        _, saved, proof, history = d._load(system.config, OLD)
        return response('disposition', '\u00e9' * 12000, sha(encoded(d.packet(saved, proof, history))))
    monkeypatch.setattr(d, '_client', lambda runtime: original_reply)
    with pytest.raises(ValueError, match='DISPOSITION_ANSWER_JSON_CHARACTER_BOUND'):
        d.recover(system.runtime, OLD)
    assert calls == ['stage_status'] and system.guards == []
    assert not (folder / 'result.json').exists()


def test_input_measurement_and_verified_prompt_bind_serialized_limit(tmp_path, monkeypatch):
    from orchestrator import hosted_context
    packet, _, _ = original()
    monkeypatch.setattr(d, 'checked_source', lambda *args: tmp_path)
    calls = []
    def composed(root, packet_raw, body, **kwargs):
        calls.append(body)
        return body, {'original_packet_sha256': sha(packet_raw)}
    monkeypatch.setattr(hosted_context, 'compose_input', composed)
    measurement, _ = d._measurement({'source_root': str(tmp_path), 'source': SOURCE}, packet)
    assert measurement['disposition_answer_characters'] == 30000
    assert measurement['disposition_answer_json_characters'] == 30002
    assert measurement['provider_calls'] == 0
    assert 'using ASCII escapes, including its enclosing quotes' in calls[0]


def test_launch_rejects_prompt_without_current_serialized_limit(system):
    save(system); _, saved, proof, history = d._load(system.config, OLD)
    value = d.packet(saved, proof, history)
    body = {'event': d.event(saved), 'stage': 'disposition', 'packet': value,
            'prompt': d.prompt(value).replace('at most 30002 characters', 'unlimited serialized characters')}
    with pytest.raises(ValueError, match='DISPOSITION_EXACT_PREPARED_LAUNCH_REQUIRED'):
        d.verify_launch(system.config, body, system.client)
    assert system.calls == system.guards == []


def test_imported_prior_reply_keeps_its_existing_larger_envelope():
    packet, reply, _ = original()
    # An imported review envelope can exceed30k while each original file remains
    # within its existing bound. The new disposition limit does not govern it.
    discussion = 'x' * 10000 + '\u00e9' * 5000
    reply['stages']['continuation'] = response('continuation',
        json.dumps({'discussion.md': discussion}), sha(encoded(packet)))
    assert len(reply['stages']['continuation']['answer']) > 30000
    assert d._refusal(reply, d._event(OLD, OLD_SOURCE), packet)['discussion.md'] == discussion


@pytest.mark.parametrize('verdict',['REVISE','REQUEST_CHANGES'])
def test_negative_original_review_stays_not_accepted(system,verdict):
    system.proof.update(original(verdict)[2]);save(system);d.advance(system.runtime)
    result=d.read_result(system.config,OLD,system.client)['result']
    assert result['review_verdict']==verdict and result['acceptance_status']=='NOT_ACCEPTED'


def test_final_preflight_failure_is_named_before_any_admission(system,monkeypatch):
    from orchestrator.hosted_context import InputTooLarge
    save(system)
    monkeypatch.setattr(d,'_measurement',lambda *args:(_ for _ in ()).throw(InputTooLarge({'characters':1048577})))
    with pytest.raises(InputTooLarge):d.advance(system.runtime)
    folder=d.directory(system.config)/OLD
    assert (folder/'preflight-failure.json').exists() and not (folder/'started.json').exists()
    assert system.calls==[] and system.guards==[]
    assert d.advance(system.runtime)['status']=='NO_QUEUED_DISPOSITION_SUCCESSOR'


def test_uncertain_successor_does_not_retry(system,monkeypatch):
    save(system)
    def fail(*args):raise ValueError('PRESERVED_MODEL_TIMEOUT')
    monkeypatch.setattr(d,'_client',lambda runtime:fail)
    with pytest.raises(ValueError,match='TIMEOUT'):d.advance(system.runtime)
    assert d.status(system.config)['successors'][0]['status']=='RECONCILIATION_REQUIRED'
    assert d.advance(system.runtime)['status']=='NO_QUEUED_DISPOSITION_SUCCESSOR'
    assert system.guards==['admit']


def test_recover_requires_actual_completed_original_and_never_model(system,monkeypatch):
    save(system);folder=d.directory(system.config)/OLD
    with pytest.raises(ValueError,match='NOT_STARTED'):d.recover(system.runtime,OLD)
    (folder/'started.json').write_bytes(encoded({'request':d._load(system.config,OLD)[1]['identity']}))
    monkeypatch.setattr(d,'_client',lambda runtime:lambda *args:{'status':'NOT_STARTED_RECONCILIATION_REQUIRED'})
    with pytest.raises(ValueError,match='BLOCKED_RECONCILE'):d.recover(system.runtime,OLD)
    assert not (folder/'result.json').exists()
    monkeypatch.setattr(d,'_client',lambda runtime:system.client)
    assert d.recover(system.runtime,OLD)['new_model_calls']==0
    assert [x[0] for x in system.calls]==['stage_status'] and system.guards==[]


@pytest.mark.parametrize('alter',['prompt','event','source','repair','original'])
def test_launch_rechecks_exact_current_source_and_evidence(system,alter):
    save(system);_,saved,proof,history=d._load(system.config,OLD);value=d.packet(saved,proof,history)
    body={'event':d.event(saved),'stage':'disposition','packet':value,'prompt':d.prompt(value)}
    assert d.verify_launch(system.config,body,system.client)['status']=='VERIFIED_LINKED_DISPOSITION_LAUNCH'
    if alter=='prompt':body['prompt']+='different instruction'
    elif alter=='event':body['event']['source']=OLD_SOURCE
    elif alter=='source':system.config['source']='3'*40
    elif alter=='repair':system.history['events'].append({'event':'DISPOSITION','identity':'f'*64})
    else:system.proof['report']['text']+='changed original'
    with pytest.raises(ValueError):d.verify_launch(system.config,body,system.client)


def test_saved_symlink_and_mutated_result_refuse(system):
    save(system);d.advance(system.runtime);folder=d.directory(system.config)/OLD
    value=json.loads((folder/'result.json').read_bytes());value['origin_source']=SOURCE
    (folder/'result.json').write_bytes(encoded(value))
    with pytest.raises(ValueError,match='RESULT_ORIGINAL_CHANGED'):d.read_result(system.config,OLD,system.client)
    original=folder/'request.json';target=folder/'request-moved.json';original.rename(target);original.symlink_to(target)
    assert d.status(system.config)['successors'][0]['status']=='RECONCILIATION_REQUIRED'


def test_consumer_is_explicit_event_not_old_task_predecessor(system,monkeypatch):
    monkeypatch.setattr('orchestrator.linked_disposition_input.enabled', lambda *args: False)
    save(system);d.advance(system.runtime)
    value=d.read_result(system.config,OLD,system.client)
    monkeypatch.setattr(d,'read_result',lambda *args:value)
    item=wakes._disposition(system.config,OLD,system.client)
    assert item['event']==wakes.event('DISPOSITION',OLD,value['result_sha256'])
    assert 'predecessor' not in item and 'packet' not in item and item['references']==[]
    assert item['linked_disposition']['originals']['packet']['reviewer_evidence']['limitation']=='missing paired observations'
    assert wakes.event_key(item['event'])!=wakes.event_key(wakes.event('TASK',OLD,value['result_sha256']))
    value['originals']['packet']['campaign_task']['references']=[{'task':OLD}]
    with pytest.raises(ValueError,match='BLOCKED_TASK_REFERENCE'):wakes._disposition(system.config,OLD,system.client)


def test_fresh_investigator_gets_inline_result_without_completing_old_task(system,monkeypatch):
    monkeypatch.setattr('orchestrator.linked_disposition_input.enabled', lambda *args: False)
    save(system);d.advance(system.runtime);value=d.read_result(system.config,OLD,system.client)
    monkeypatch.setattr(d,'read_result',lambda *args:value)
    template={'schema':'investigator-template/v1','template_id':'charter','experiment':'P001',
        'request':'Consider the charter and imported original evidence.','evidence_file':'/fixed/evidence.json',
        'evidence_sha256':HASH,'references':[],'change_request':system.change}
    config={**system.config,'investigator':{'template':template,'template_sha256':digest(template)}}
    import orchestrator.research_catalog as catalog
    import orchestrator.handover_runtime as runtime_module
    monkeypatch.setattr(catalog,'linked_change',lambda *args:system.history)
    monkeypatch.setattr(runtime_module,'configuration',lambda *args,**kwargs:{'charter':'existing scientific context'})
    monkeypatch.setattr(wakes,'_task',lambda *args,**kwargs:(_ for _ in ()).throw(AssertionError('Old blocked task must not be a predecessor')))
    core={'schema':wakes.WAKE,'source':SOURCE,'template_sha256':digest(template),
        'events':[wakes.event('DISPOSITION',OLD,value['result_sha256'])],'day':'2026-09-12'}
    prepared=wakes.regenerate(config,{**core,'identity':digest(core)},system.client)
    assert prepared['predecessors']==[] and prepared['task']['purpose']=='CHARTER_SELECTION'
    assert prepared['task']['selected_by'] is None
    assert prepared['evidence']['verified_events'][0]['linked_disposition']['result']['origin_task']==OLD
    wrong={**core,'events':[wakes.event('DISPOSITION',OLD,'f'*64)]}
    with pytest.raises(ValueError,match='EVENT_ORIGINAL_CHANGED'):
        wakes.regenerate(config,{**wrong,'identity':digest(wrong)},system.client)


@pytest.fixture
def originals_on_disk(tmp_path,monkeypatch):
    """Exercise the real read-only task proof; only catalog/eligibility transport is substituted."""
    state=tmp_path/'state';state.mkdir(mode=0o700)
    packet,reply,_=original()
    packet['campaign_task'].update(request='Discuss the retained evidence.',selected_by=None)
    from orchestrator.hosted_campaign_task import task_contract
    packet['campaign_artifacts']=task_contract(packet['campaign_task'])
    report_text=b'Original operational report.';report={'id':sha(report_text)}
    identity=digest({'source':OLD_SOURCE,'packet':packet,'report':report})
    binding={'id':identity,'source':OLD_SOURCE,'kind':'astra_turn','thread':'primary',
        'dependencies':[],'stages':['continuation','review','disposition']}
    folder=state/'tasks'/identity;folder.mkdir(mode=0o700,parents=True)
    (folder/'packet.json').write_bytes(encoded(packet));(folder/'report.json').write_bytes(encoded(report))
    (state/'reports').mkdir(mode=0o700);(state/'reports'/(report['id']+'.md')).write_bytes(report_text)
    reply['packet']=packet;reply['event']=d._event(identity,OLD_SOURCE);reply['packet_sha256']=sha(encoded(packet))
    for item in reply['stages'].values():item['packet_sha256']=reply['packet_sha256']
    db=sqlite3.connect(state/'coordinator.sqlite')
    db.executescript('CREATE TABLE tasks(id TEXT,binding TEXT,status TEXT); CREATE TABLE stages(task TEXT,position INTEGER,state TEXT);')
    db.execute('INSERT INTO tasks VALUES(?,?,?)',(identity,json.dumps(binding),'BLOCKED'))
    db.executemany('INSERT INTO stages VALUES(?,?,?)',[(identity,0,'COMPLETE'),(identity,1,'COMPLETE'),(identity,2,'STARTED')]);db.commit();db.close()
    relative=str(Path('tasks')/identity/'campaign-workspace/campaigns/isles24-pilot/pipeline/hosted-original')
    out=state/relative;(out/'round-1').mkdir(mode=0o700,parents=True);(out/'receipt.json').write_bytes(encoded({'status':'APPROVED_PROPOSAL_ONLY'}))
    from orchestrator.hosted_campaign import artifact_files
    for position,stage,name in [(0,'continuation','discussion.md'),(1,'review','review.json')]:
        (out/'round-1'/name).write_text(artifact_files(reply['stages'][stage]['answer'],[name])[name])
        output={**reply['stages'][stage],'campaign_output':relative,'campaign_receipt_sha256':sha((out/'receipt.json').read_bytes())}
        value={'binding':digest(binding),'position':position,'output':output,'output_sha256':digest(output)}
        (state/(identity+'-'+str(position)+'.json')).write_bytes(encoded(value))
    config={'state':str(state),'source':SOURCE,'source_root':'/current-source','broker_socket':'fixed'}
    import orchestrator.hosted_campaign_task as campaign_task
    import orchestrator.research_catalog as catalog
    import orchestrator.research_task_authority as authority
    monkeypatch.setattr(campaign_task,'installed_packet_task',lambda *args:packet['campaign_task'])
    monkeypatch.setattr(catalog,'selection',lambda *args:({'source':OLD_SOURCE},{'source':OLD_SOURCE}))
    calls=[]
    def eligibility(config,entry,client):
        calls.append(('original-eligibility',config['source']));return {'status':'ELIGIBLE','review_status':'APPROVE'}
    monkeypatch.setattr(authority,'verify_eligibility',eligibility)
    def client(socket,op,body):
        calls.append((op,body));assert op=='disposition_refusal';assert body=={'event':d._event(identity,OLD_SOURCE)}
        return deepcopy(reply)
    return SimpleNamespace(config=config,state=state,task=identity,folder=folder,output=out,packet=packet,reply=reply,client=client,calls=calls)


def test_actual_proof_reads_retained_source_and_complete_originals_only(originals_on_disk):
    s=originals_on_disk;before={str(p):p.read_bytes() for p in s.state.rglob('*') if p.is_file()}
    proof=d._proof(s.config,s.task,s.client)
    assert proof['origin_source']==OLD_SOURCE and proof['origin_task']==s.task
    assert proof['packet']==s.packet and 'packet' not in proof['protected_original']
    assert s.calls[0]==('original-eligibility',OLD_SOURCE)
    assert set(x[0] for x in s.calls)=={'original-eligibility','disposition_refusal'}
    assert before=={str(p):p.read_bytes() for p in s.state.rglob('*') if p.is_file()}


@pytest.mark.parametrize('mutation',['task-complete','review-incomplete','third-receipt','disposition','report','artifact','pipeline','local-reply','root-packet'])
def test_changed_or_completed_originals_cannot_be_imported(originals_on_disk,mutation):
    s=originals_on_disk
    if mutation in ('task-complete','review-incomplete'):
        db=sqlite3.connect(s.state/'coordinator.sqlite')
        if mutation=='task-complete':db.execute("UPDATE tasks SET status='COMPLETE'")
        else:db.execute("UPDATE stages SET state='STARTED' WHERE position=1")
        db.commit();db.close()
    elif mutation=='third-receipt':(s.state/(s.task+'-2.json')).write_bytes(b'{}')
    elif mutation=='disposition':(s.folder/'scientific-disposition.json').write_bytes(b'{}')
    elif mutation=='report':next((s.state/'reports').iterdir()).write_bytes(b'changed')
    elif mutation=='artifact':(s.output/'round-1/discussion.md').write_bytes(b'changed')
    elif mutation=='pipeline':(s.output/'receipt.json').write_bytes(b'{}')
    elif mutation=='root-packet':s.reply['packet_sha256']='e'*64
    else:
        path=s.state/(s.task+'-0.json');value=json.loads(path.read_bytes());value['output']['answer']='changed'
        value['output_sha256']=digest(value['output']);path.write_bytes(encoded(value))
    with pytest.raises(ValueError):d._proof(s.config,s.task,s.client)
