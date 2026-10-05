"""Prospective adoption fixtures; no fixture grants scientific authority."""
from copy import deepcopy
import hashlib
import json
from pathlib import Path
from types import SimpleNamespace

import pytest
from orchestrator import scientific_adoption as adopt, scientific_acceptance as accept
from orchestrator import formal_decisions as formal
from orchestrator.hosted_cycle import encoded
from test_scientific_acceptance import prepared
from test_semantic_validation_contract import checked_import, validation_import


@pytest.fixture
def adoption(prepared, monkeypatch):
    p = prepared
    accepted = accept.apply(p.config, p.ref, p.request, p.path, original_client=p.client, by=p.by)
    acceptance = {'operation': 'a'*64, 'result_sha256': 'b'*64}
    folder = Path(p.config['state'])/'continuing-operations'/acceptance['operation']
    folder.mkdir(parents=True)
    (folder/'prepared.json').write_bytes(encoded({'formal_request': p.request}))
    selection_id = 'd'*64
    task = deepcopy(p.task)
    task.update(task_id='fixture-adoption-investigator', mode='investigate', references=[p.ref], selected_by=None)
    task.pop('semantic_validation', None)
    successor = {k: v for k,v in task.items() if k != 'import_result'}
    successor.update(accepted_result=acceptance, task_id='fixture-followup', mode='propose',
        request='Fixture reviewed follow-up, no execution.')
    chosen = {'schema': 'continuing-research-selection/v1', 'status': 'PROPOSE',
        'rationale': 'Consider this distinct follow-up using the accepted fixture evidence.',
        'reconsideration': 'Defer if authority or compatibility is not established.', 'successor': successor}
    packet = {'campaign_task': task, 'research_catalog_entry': {'change_request': p.request['change_request']},
        'continuing_context': {'continuing_operations': {'completed': [
            {'reference': acceptance, 'kind': 'ACCEPT_RESULT', 'result': accepted}]}}}
    body = encoded(chosen).decode()
    review = json.dumps({'verdict':'APPROVE', 'rationale':'Independent fixture successor proposal review.'})
    answers = {'continuation':json.dumps({'selection.json':body}),
        'review':json.dumps({'review.json':review}), 'disposition':'Fixture proposal only; no adoption yet.'}
    sha = hashlib.sha256(encoded(packet)).hexdigest()
    replies = {}
    for stage,answer in answers.items():
        model = 'claude-fable-5' if stage == 'review' else 'gpt-6-astra'
        replies[stage] = {'status':'COMPLETE','answer':answer,'packet_sha256':sha,
            'receipt':{'requested_model':model,'actual_model':model,'returncode':0,'stage':stage,
                'session_id':'fixture-selection-'+stage,'answer_sha256':hashlib.sha256(answer.encode()).hexdigest(),
                'operating_context_sha256':'8'*64}}
    selection = {'task':selection_id,'artifact':'round-1/selection.json','sha256':hashlib.sha256(body.encode()).hexdigest()}
    disposition = {'task':selection_id,'source':p.config['source'],'status':'DISPOSITION_RECORDED',
        'review_verdict':'APPROVE','acceptance_status':'APPROVED_PROPOSAL_ONLY',
        'reviewer':{'session_id':'fixture-selection-review','model':'claude-fable-5'},
        'disposition_actor':{'session_id':'fixture-selection-disposition'},
        'disposition_sha256':hashlib.sha256(answers['disposition'].encode()).hexdigest(),
        'artifact_sha256':{'round-1/selection.json':selection['sha256'],
            'round-1/review.json':hashlib.sha256(review.encode()).hexdigest()},
        'campaign_output':'tasks/'+selection_id+'/pipeline'}
    original_folder = Path(p.config['state'])/'tasks'/selection_id
    (original_folder/'pipeline/round-1').mkdir(parents=True)
    (original_folder/'packet.json').write_bytes(encoded(packet))
    (original_folder/'scientific-disposition.json').write_bytes(encoded(disposition))
    (original_folder/'pipeline/round-1/selection.json').write_text(body)
    (original_folder/'pipeline/round-1/review.json').write_text(review)
    def client(socket, operation, value):
        if operation in ('stage_packet','stage_status') and value['event']['turn_id'] == selection_id:
            if operation == 'stage_packet':
                return {'status':'COMPLETE','packet':packet,'packet_sha256':sha}
            return deepcopy(replies[value['stage']])
        return p.client(socket,operation,value)
    def accepted_operation(config, ref, reader):
        assert ref == acceptance
        actual = accept.read_application(config,p.ref,p.request,p.path,original_client=reader,by=p.by)
        return {'operation': {'kind':'ACCEPT_RESULT','reference':ref,'result':{**actual,'duplicate':False}}}
    monkeypatch.setattr('orchestrator.investigator_wakes._operation', accepted_operation)
    monkeypatch.setattr('orchestrator.remote_supervisor.checked_source', lambda root,source:Path(root))
    # Native read_protocol uses an existing fixture transport; this fixture
    # supplies that separately reviewed protocol, not real authority.
    monkeypatch.setattr('orchestrator.continuing_research.observed_protocols',lambda *a,**kw:[successor['protocol']])
    request = {**adopt.prepare(p.config,acceptance,selection,original_client=client),
        'schema':formal.SCHEMA,'source':p.config['source'],'workspace':None,'application':None,
        'change_request':p.request['change_request']}
    decision_path = Path(p.config['state'])/'formal-decisions/adopt-fixture/round-1/decision.json'
    proof = {'decision':'APPLY','_decision_sha256':'e'*64,'actor':deepcopy(p.proof['actor']),
        'policy':deepcopy(p.proof['policy']),'transition':request['transition']}
    prior_transport = formal.original_transport
    prior_verify = formal.verify_original_decision
    def transport(folder, *a):
        if folder == decision_path.parent.parent:
            return {'packet':{'formal_request':request}}
        return prior_transport(folder,*a)
    def verify(root,path,**kw):
        if path == decision_path:
            for k in ('action','subject','bindings'): assert kw[k] == request[k]
            assert kw['expected_transition'] == request['transition']
            return deepcopy(proof)
        return prior_verify(root,path,**kw)
    monkeypatch.setattr(formal,'original_transport',transport)
    monkeypatch.setattr(formal,'verify_original_decision',verify)
    return SimpleNamespace(p=p,acceptance=acceptance,selection=selection,request=request,path=decision_path,
        proof=proof,client=client,packet=packet,replies=replies,folder=original_folder,
        selected=chosen,accepted_folder=folder,accepted_operation=accepted_operation)


def test_actual_selection_originals_and_acceptance_capture_reach_adoption(adoption):
    a=adoption
    req=adopt.prepare(a.p.config,a.acceptance,a.selection,original_client=a.client)
    assert req['action']=='adopt_followup'
    assert req['evidence']['original-result.json']==a.p.request['evidence']['original-result.json']
    assert 'successor-opposing-review.original.txt' in req['evidence']
    compatibility=json.loads(req['evidence']['successor-compatibility.json'])
    assert compatibility['protocol_relation']=='SAME_REVIEWED_PROTOCOL'
    assert compatibility['execution_authorized'] is False
    assert compatibility['accepted_completion']==a.p.request['bindings']['completion']
    assert req['transition']['to']=='AGENT_ADOPTED'


def test_adoption_separate_from_acceptance_and_duplicate_safe(adoption):
    a=adoption
    first=adopt.apply(a.p.config,a.acceptance,a.selection,a.request,a.path,original_client=a.client,by=a.p.by)
    assert first['adoption'] is True and first['execution_authorized'] is False
    assert first['actor']==a.proof['actor'] and first['applied_by']==a.p.by
    before={str(p):p.read_bytes() for p in Path(a.p.config['state']).rglob('*') if p.is_file()}
    again=adopt.apply(a.p.config,a.acceptance,a.selection,a.request,a.path,original_client=a.client,by=a.p.by)
    assert again=={**first,'duplicate':True}
    assert adopt.read_application(a.p.config,a.acceptance,a.selection,a.request,a.path,
        original_client=a.client,by=a.p.by)=={k:v for k,v in first.items() if k!='duplicate'}
    assert before=={str(p):p.read_bytes() for p in Path(a.p.config['state']).rglob('*') if p.is_file()}
    assert all(x not in ('model_stage','dispatch_scientific_job') for x in a.p.operations)


@pytest.mark.parametrize('changed', ['acceptance_request','selection_file','selection_reply','selection_disposition','accepted_receipt'])
def test_changed_originals_refuse_without_application(adoption,changed):
    a=adoption
    if changed=='acceptance_request':
        value=deepcopy(a.p.request);value['request']+=' altered'
        (a.accepted_folder/'prepared.json').write_bytes(encoded({'formal_request':value}))
    elif changed=='selection_file':
        (a.folder/'pipeline/round-1/selection.json').write_text('{}')
    elif changed=='selection_reply':
        a.replies['review']['answer']+='changed'
    elif changed=='selection_disposition':
        path=a.folder/'scientific-disposition.json';v=json.loads(path.read_bytes());v['review_verdict']='REQUEST_CHANGES';path.write_bytes(encoded(v))
    else:
        p=next((Path(a.p.config['state'])/'scientific-results').rglob('application.json'))
        p.write_text('{}')
    with pytest.raises(ValueError):
        adopt.apply(a.p.config,a.acceptance,a.selection,a.request,a.path,original_client=a.client,by=a.p.by)
    assert not (Path(a.p.config['state'])/'scientific-adoptions').exists()


def test_formal_defer_does_not_apply_or_delete_acceptance(adoption):
    a=adoption;a.proof['decision']='DEFER'
    with pytest.raises(ValueError,match='DEFERRED_FOLLOWUP'):
        adopt.apply(a.p.config,a.acceptance,a.selection,a.request,a.path,original_client=a.client,by=a.p.by)
    assert not (Path(a.p.config['state'])/'scientific-adoptions').exists()
    assert accept.read_application(a.p.config,a.p.ref,a.p.request,a.p.path,
        original_client=a.p.client,by=a.p.by)['scientific_acceptance'] is True


def test_partial_application_needs_explicit_recovery(adoption):
    a=adoption
    first=adopt.apply(a.p.config,a.acceptance,a.selection,a.request,a.path,original_client=a.client,by=a.p.by)
    target=next((Path(a.p.config['state'])/'scientific-adoptions').rglob('application.json'))
    target.unlink()
    with pytest.raises(ValueError,match='PARTIAL_APPLICATION'):
        adopt.apply(a.p.config,a.acceptance,a.selection,a.request,a.path,original_client=a.client,by=a.p.by)
    restored=adopt.apply(a.p.config,a.acceptance,a.selection,a.request,a.path,
        original_client=a.client,by=a.p.by,recover=True)
    assert restored==first
    assert json.loads(target.read_bytes())['adoption'] is True


@pytest.mark.parametrize('mutation',['request','decision_transport','criticism','human_stop','wrong_kind'])
def test_current_authority_and_evidence_fail_closed(adoption,monkeypatch,mutation):
    a=adoption;req=deepcopy(a.request)
    if mutation=='request':req['evidence']['successor-disposition.original.md']='changed'
    elif mutation=='decision_transport':
        old=formal.original_transport
        monkeypatch.setattr(formal,'original_transport',lambda folder,*args:
            {'packet':{'formal_request':{**req,'request':'changed'}}} if folder==a.path.parent.parent else old(folder,*args))
    elif mutation in ('criticism','human_stop'):
        def fail(*args):raise ValueError('FIXTURE_CURRENT_STOP')
        monkeypatch.setattr('orchestrator.research_catalog.linked_change' if mutation=='criticism'
            else 'orchestrator.campaign.require_no_human_stop',fail)
    else:
        def wrong(*args):
            result=a.accepted_operation(*args);result['operation']['kind']='IMPORT_RESULT';return result
        monkeypatch.setattr('orchestrator.investigator_wakes._operation',wrong)
    with pytest.raises(ValueError):
        adopt.apply(a.p.config,a.acceptance,a.selection,req,a.path,original_client=a.client,by=a.p.by)


def test_protected_investigator_can_read_semantic_original_but_cannot_execute(monkeypatch):
    from orchestrator import protected_investigator as protected
    broker=object(); calls=[]
    def original(actual,operation,body):
        assert actual is broker; calls.append((operation,body))
        return {'fixture':'original-semantic-response'}
    monkeypatch.setattr('orchestrator.protected_scientific_jobs.handle',original)
    assert protected.original(broker,'scientific_validation_result',{'completion':'a'*64}) == {
        'fixture':'original-semantic-response'}
    assert calls==[('scientific_validation_result',{'completion':'a'*64})]
    for operation in ('register_scientific_validation','dispatch_scientific_job','model_stage'):
        with pytest.raises(ValueError,match='ORIGINAL_READ_ONLY'):
            protected.original(broker,operation,{})
    assert len(calls)==1


def test_compatibility_changed_protocol_is_explicit_not_inferred_equivalent(adoption,monkeypatch):
    a=adoption
    # The original-task fixture is immutable; this unit seam supplies a different
    # already-reviewed successor to test relation classification, not live proof.
    from orchestrator import continuing_research as continuing, investigator_wakes as wakes
    native_task=wakes._task
    original=native_task(a.p.config,a.selection['task'],a.client,investigator=True,include_originals=True)
    proposed=deepcopy(a.selected);proposed['successor']['protocol']['decision_sha256']='f'*64
    monkeypatch.setattr(wakes,'_task',lambda config,identity,client,**kw:
        deepcopy(original) if identity==a.selection['task'] else native_task(config,identity,client,**kw))
    native_read=continuing.read_reference
    monkeypatch.setattr(continuing,'read_reference',lambda config,ref:
        encoded(proposed) if ref==a.selection else native_read(config,ref))
    monkeypatch.setattr(continuing,'observed_protocols',lambda *args,**kw:[proposed['successor']['protocol']])
    native_protocol=continuing.read_protocol
    monkeypatch.setattr(continuing,'read_protocol',lambda config,task,**kw:
        {'descriptor':task['protocol'],'decision':{'decision':'APPLY'},'original_request':{}}
        if task['task_id']=='fixture-followup' else native_protocol(config,task,**kw))
    req=adopt.prepare(a.p.config,a.acceptance,a.selection,original_client=a.client)
    assert json.loads(req['evidence']['successor-compatibility.json'])['protocol_relation']=='DISTINCT_REVIEWED_PROTOCOL'
    assert 'mechanical compatibility never establishes scientific equivalence' in req['request']


@pytest.mark.parametrize('mutation',['missing_acceptance','missing_interpretation','execution_successor','deferred','changed_import'])
def test_missing_or_incompatible_successor_refused(adoption,monkeypatch,mutation):
    a=adoption
    from orchestrator import continuing_research as continuing, investigator_wakes as wakes
    native_task=wakes._task
    original=native_task(a.p.config,a.selection['task'],a.client,investigator=True,include_originals=True)
    proposed=deepcopy(a.selected)
    if mutation=='missing_acceptance':
        original['packet']['continuing_context']['continuing_operations']['completed']=[]
    elif mutation=='missing_interpretation':proposed['successor']['references']=[]
    elif mutation=='execution_successor':
        proposed['successor']={'schema':'continuing-operation/v1','operation_id':'launch','kind':'IMPORT_RESULT',
            'inputs':{'completion':'a'*64}}
    elif mutation=='deferred':proposed.update(status='DEFER',successor=None)
    else:
        proposed['successor']['import_result']={'operation':'8'*64,'result_sha256':'9'*64}
        native_import=continuing.read_result_import
        monkeypatch.setattr(continuing,'read_result_import',lambda config,task,**kw:
            {'receipt':{'completion':'8'*64}} if task['task_id']=='fixture-followup'
            else native_import(config,task,**kw))
    monkeypatch.setattr(wakes,'_task',lambda config,identity,client,**kw:
        deepcopy(original) if identity==a.selection['task'] else native_task(config,identity,client,**kw))
    native_read=continuing.read_reference
    monkeypatch.setattr(continuing,'read_reference',lambda config,ref:
        encoded(proposed) if ref==a.selection else native_read(config,ref))
    with pytest.raises(ValueError):
        adopt.prepare(a.p.config,a.acceptance,a.selection,original_client=a.client)


def test_corrupt_partial_adoption_is_preserved(adoption):
    a=adoption
    adopt.apply(a.p.config,a.acceptance,a.selection,a.request,a.path,original_client=a.client,by=a.p.by)
    target=next((Path(a.p.config['state'])/'scientific-adoptions').rglob('application.json'))
    target.unlink();intent=target.with_name('intent.json');intent.write_text('{bad fixture')
    with pytest.raises(ValueError):
        adopt.apply(a.p.config,a.acceptance,a.selection,a.request,a.path,original_client=a.client,by=a.p.by,recover=True)
    assert intent.read_text()=='{bad fixture' and not target.exists()
