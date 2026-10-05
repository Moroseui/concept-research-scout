"""Real queue/pipeline recovery; OS ownership, models and eligibility are fixtures.

The injected eligibility verifier below is deliberately synthetic. These tests
never establish scientific authority, a real human action or provider approval.
"""
import copy
import hashlib
import json
import os
from pathlib import Path
import subprocess
from types import SimpleNamespace
from unittest.mock import patch

import pytest

from test_installed_research_request import prepared, Broker
from test_live_research_preparation import inputs, module as preparation
import orchestrator.handover_runtime as runtime
from orchestrator import research_catalog as catalog
from orchestrator.handover_coordinator import digest, encoded

ACTOR={'kind':'agent','family':'codex','model':'gpt-6-astra',
       'session_id':'explicitly-synthetic-catalog-test'}


def synthetic_eligibility(config,entry):
    return {'status':'ELIGIBLE','entry_sha256':digest(entry),
        'reference_sha256':entry['eligibility']['sha256'],'source':entry['source'],
        'actor':ACTOR,'review_status':'APPROVE','rationale':'Synthetic fixture only'}


@pytest.fixture
def installed(prepared,monkeypatch):
    # This fixture isolates catalogue/state semantics from installed policy files.
    # The real composed-input measurement is exercised in the dedicated input tests.
    # The original-only fixture has no Git HEAD or new presentation profile.
    legacy = prepared.root/'orchestrator/hosted_context.py'
    legacy.parent.mkdir(exist_ok=True)
    legacy.write_text('"""Synthetic original-only hosted context."""\n')
    def checked_fixture_source(path, pin):
        assert Path(path) == prepared.root and pin == prepared.config['source']
        return prepared.root
    monkeypatch.setattr('orchestrator.remote_supervisor.checked_source', checked_fixture_source)
    # disposition_successors imports the reader into its own namespace.
    # Extend the existing synthetic source boundary to that actual caller.
    monkeypatch.setattr('orchestrator.disposition_successors.checked_source', checked_fixture_source)
    monkeypatch.setattr('orchestrator.hosted_context.build',
        lambda root,state: {'task_state':state,'policy':'Synthetic fixed policy.'})
    folder=prepared.parent/'catalog';folder.mkdir(mode=0o750)
    observed_stat=Path.stat;observed_fstat=os.fstat
    def root_stat(value):
        fields=list(value);fields[4]=0
        return os.stat_result(fields)
    def stat_path(path,*args,**kwargs):
        result=observed_stat(path,*args,**kwargs)
        return root_stat(result) if path==folder else result
    def stat_fd(fd):
        result=observed_fstat(fd)
        try:path=Path(os.readlink('/proc/self/fd/'+str(fd)))
        except OSError:return result
        return root_stat(result) if path.parent==folder else result
    monkeypatch.setattr(Path,'stat',stat_path)
    monkeypatch.setattr(os,'fstat',stat_fd)
    prepared.config['research_catalog']={'directory':str(folder),
        'legacy_source':{k:prepared.config[k] for k in ('source','source_root')}}
    request=copy.deepcopy(prepared.config['research_request'])
    request['task']={'task_id':'next-discussion-v1','mode':'discuss',
        'request':'Explain the existing evidence limitation through the recorded discussion workflow.'}
    from orchestrator import change_requests as changes
    Path(prepared.config['state']).mkdir(mode=0o700)
    store=Path(prepared.config['state'])/'changes';prepared.config['change_request_store']=str(store)
    proposal=changes.submit(store,prepared.root,'research:next-discussion-v1',
        'Record the bounded scientific request for this synthetic test.',ACTOR,source=prepared.config['source'],
        scope_limits=['Synthetic test only; no scientific authority or actual provider review'])
    history=store/proposal['identity']
    changes.record(history,'AUTHORIZED',ACTOR,{'rationale':'Synthetic fixture',
        'authority_reference':'Synthetic fixture','review_policy':'Actual test state only'})
    applied=changes.record(history,'APPLIED',ACTOR,{'modification':'Synthetic proposed task version',
        'checks':'Synthetic fixture','result_binding':'Synthetic fixture','review_status':'PENDING'})
    changes.record(history,'REVIEW',{**ACTOR,'family':'claude','model':'claude-fable-5'},
        {'applied_event':applied['identity'],'verdict':'APPROVE','rationale':'Synthetic fixture only',
         'review_evidence':'No actual model call or authority is asserted'})
    entry={'schema':catalog.SCHEMA,'source':prepared.config['source'],
        'source_root':str(prepared.root),'request':request,
        'eligibility':{'path':str(prepared.parent/'not-an-actual-decision.json'),'sha256':'d'*64},
        'predecessors':[],'change_request':{'request_id':proposal['identity'],'applied_event':applied['identity']}}
    def save(value=entry):
        path=folder/(value['request']['task']['task_id']+'.json')
        path.write_bytes(encoded(value));path.chmod(0o640)
        return path
    save()
    return SimpleNamespace(**vars(prepared),folder=folder,entry=entry,save=save)


class MultiBroker:
    def __init__(self,verdict='APPROVE'):self.turns={};self.calls=[];self.verdict=verdict
    def __call__(self,socket,operation,body):
        event=body.get('event',body);identity=event['turn_id']
        broker=self.turns.setdefault(identity,Broker())
        result=broker(socket,operation,body)
        if operation=='model_stage' and body['stage']=='review' and self.verdict!='APPROVE':
            result['answer']=json.dumps({'review.json':json.dumps({'verdict':self.verdict,
                'rationale':'Synthetic criticism requires revision before acceptance.'})})
            result['receipt']['answer_sha256']=hashlib.sha256(result['answer'].encode()).hexdigest()
            broker.saved['review']=result
        self.calls.append((identity,operation,body.get('stage')))
        return result


def run_original(r,monkeypatch,verdict='APPROVE'):
    broker=MultiBroker(verdict);monkeypatch.setattr(runtime,'request_broker',broker)
    result=r.submit_research()
    assert r.q.tick()['status']=='COMPLETE'
    r.bookkeeping()
    return result,broker


def test_new_catalog_is_inspectable_but_no_declared_reference_authorizes_it(installed,monkeypatch):
    from orchestrator import scientific_authority, remote_supervisor
    source=Path(__file__).resolve().parents[1]
    for name in (scientific_authority.POLICY_PATH,scientific_authority.DIRECTION_PATH):
        target=installed.root/name
        target.parent.mkdir(parents=True,exist_ok=True)
        target.write_bytes((source/name).read_bytes())
    # Only the installed source identity is a fixture. The catalog now calls
    # the real decision verifier, which must refuse the absent original seal.
    monkeypatch.setattr(remote_supervisor,'checked_source',lambda path,pin:installed.root)
    r=runtime.Runtime(installed.config)
    monkeypatch.setattr(runtime,'request_broker',lambda *args:pytest.fail('No broker operation expected'))
    listing=r.research_list()
    assert len(listing['requests'])==2
    item=r.research_inspect('next-discussion-v1')
    assert item['eligibility_status']=='NOT_ELIGIBLE'
    assert item['reason']=='SCIENTIFIC_AUTHORITY_REGULAR_FILE_REQUIRED'
    assert item['saved'] is None and item['catalog_entry']==installed.entry
    with pytest.raises(ValueError,match='SCIENTIFIC_AUTHORITY_REGULAR_FILE_REQUIRED'):
        r.submit_research('next-discussion-v1',submitted_by=ACTOR)
    assert r.q.status()['tasks']==[]
    assert catalog.core(installed.entry)=={k:v for k,v in installed.entry.items() if k!='eligibility'}


@pytest.mark.parametrize('change,reason',[
    ('deferred','DEFERRED'),('pending','REVIEW_REQUIRED'),('negative','REVIEW_REQUIRED'),
    ('other_entry','EXACT_RESEARCH_ELIGIBILITY'),('other_reference','EXACT_RESEARCH_ELIGIBILITY')])
def test_eligibility_never_converts_deferred_or_negative_into_admission(installed,monkeypatch,change,reason):
    def verify(config,entry):
        value=synthetic_eligibility(config,entry)
        if change=='deferred':value['status']='DEFERRED'
        if change=='pending':value['review_status']='PENDING'
        if change=='negative':value['review_status']='REQUEST_CHANGES'
        if change=='other_entry':value['entry_sha256']='0'*64
        if change=='other_reference':value['reference_sha256']='0'*64
        return value
    monkeypatch.setattr(catalog,'verify_eligibility',verify)
    r=runtime.Runtime(installed.config)
    with pytest.raises(ValueError,match=reason):r.submit_research('next-discussion-v1',submitted_by=ACTOR)
    assert r.q.status()['tasks']==[]


def test_shared_queue_binds_actor_entry_and_both_role_contexts_then_quiesces(installed,monkeypatch):
    monkeypatch.setattr(catalog,'verify_eligibility',synthetic_eligibility)
    r=runtime.Runtime(installed.config)
    with pytest.raises(ValueError,match='SUBMITTER_ATTRIBUTION'):r.submit_research('next-discussion-v1')
    broker=MultiBroker();monkeypatch.setattr(runtime,'request_broker',broker)
    r.q.control({'id':'pause','action':'pause','expected_revision':0},authenticated_operator=True)
    first=r.submit_research('next-discussion-v1',submitted_by=ACTOR)
    original=r.submit_research()
    assert r.q.tick()=={'status':'PAUSED'} and broker.calls==[]
    folder=r.state/'tasks'/first['task'];packet=json.loads((folder/'packet.json').read_bytes())
    assert packet['research_catalog_entry']==installed.entry
    assert packet['research_eligibility']==synthetic_eligibility(installed.config,installed.entry)
    assert r.research_inspect('next-discussion-v1')['saved']['submitted_by']==ACTOR
    resumed=runtime.Runtime(installed.config)
    assert resumed.submit_research('next-discussion-v1',submitted_by=ACTOR)['task']==first['task']
    assert len(resumed.q.status()['tasks'])==2
    resumed.q.control({'id':'resume','action':'resume','expected_revision':1},authenticated_operator=True)
    with patch('orchestrator.campaign_pipeline.grounding',return_value={}),patch('orchestrator.research_context.evidence_context',return_value={}):
        assert resumed.q.tick()['status']=='COMPLETE';resumed.bookkeeping()
        assert resumed.q.tick()['status']=='COMPLETE';resumed.bookkeeping()
    assert resumed.q.tick()['status']=='WAITING_FOR_ELIGIBLE_WORK'
    assert len([x for x in broker.calls if x[1]=='model_stage'])==6
    assert resumed.submit_research()['task']==original['task']


def test_adding_entry_and_upgrading_source_preserves_original_recovery(installed,monkeypatch):
    r=runtime.Runtime(installed.config)
    with patch('orchestrator.campaign_pipeline.grounding',return_value={}),patch('orchestrator.research_context.evidence_context',return_value={}):
        original,broker=run_original(r,monkeypatch)
        task=r.state/'tasks'/original['task'];packet=(task/'packet.json').read_bytes()
        new_root=installed.parent/'new-source';new_root.mkdir()
        config=copy.deepcopy(installed.config);config.update(source='b'*40,source_root=str(new_root))
        # Historical source resolution is explicitly mocked; original workspace
        # inventory and every recovered artifact/protected reply are still checked.
        def checked(path,source):
            assert Path(path)==installed.root and source=='a'*40
            return installed.root
        monkeypatch.setattr('orchestrator.remote_supervisor.checked_source',checked)
        resumed=runtime.Runtime(config)
        assert resumed.submit_research()['task']==original['task']
        assert resumed.research_inspect()['eligibility_status']=='HISTORICAL_READ_ONLY'
        output=task/'campaign-workspace/campaigns/isles24-pilot/pipeline/hosted-original'
        (output/'receipt.json').unlink();(resumed.state/(original['task']+'-0.json')).unlink()
        resumed.q.db.execute("UPDATE tasks SET status='BLOCKED' WHERE id=?",(original['task'],))
        resumed.recover()
        assert resumed.q.status()['tasks'][0]['status']=='COMPLETE'
        assert (task/'packet.json').read_bytes()==packet
        assert len([x for x in broker.calls if x[1]=='model_stage'])==3
        binding=json.loads(resumed.q.db.execute('SELECT binding FROM tasks').fetchone()[0])
        with pytest.raises(ValueError,match='HISTORICAL_RESEARCH_SOURCE_READ_ONLY'):resumed.model(binding,0)


def test_negative_original_cannot_satisfy_acceptance_dependency(installed,monkeypatch):
    monkeypatch.setattr(catalog,'verify_eligibility',synthetic_eligibility)
    r=runtime.Runtime(installed.config)
    with patch('orchestrator.campaign_pipeline.grounding',return_value={}),patch('orchestrator.research_context.evidence_context',return_value={}):
        original,broker=run_original(r,monkeypatch,'REQUEST_CHANGES')
        path=r.state/'tasks'/original['task']/'scientific-disposition.json'
        outcome=json.loads(path.read_bytes())
        assert outcome['acceptance_status']=='NOT_ACCEPTED'
        installed.entry['predecessors']=[{'task':original['task'],'source':'a'*40,
            'disposition_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'requires':'APPROVED_PROPOSAL_ONLY'}]
        installed.save()
        with pytest.raises(ValueError,match='PREDECESSOR_NOT_ACCEPTED'):
            r.submit_research('next-discussion-v1',submitted_by=ACTOR)
        assert len(r.q.status()['tasks'])==1
        # Revised, not-yet-submitted fixture entry allows a discussion of the
        # criticism, without relying on acceptance of the preceding proposal.
        installed.entry['predecessors'][0]['requires']='DISPOSITION_RECORDED';installed.save()
        next_task=r.submit_research('next-discussion-v1',submitted_by=ACTOR)
        binding=json.loads(r.q.db.execute('SELECT binding FROM tasks WHERE id=?',(next_task['task'],)).fetchone()[0])
        assert binding['dependencies']==[original['task']]
        assert json.loads(path.read_bytes())['review_verdict']=='REQUEST_CHANGES'
        assert len([x for x in broker.calls if x[1]=='model_stage'])==3


def test_changed_version_cannot_reuse_saved_task_or_authority(installed,monkeypatch):
    monkeypatch.setattr(catalog,'verify_eligibility',synthetic_eligibility)
    r=runtime.Runtime(installed.config)
    first=r.submit_research('next-discussion-v1',submitted_by=ACTOR)
    installed.entry['request']['task']['request']='A changed scientific question.';installed.save()
    with pytest.raises(ValueError,match='IDENTITY_CONFLICT'):r.submit_research('next-discussion-v1',submitted_by=ACTOR)
    binding=json.loads(r.q.db.execute('SELECT binding FROM tasks WHERE id=?',(first['task'],)).fetchone()[0])
    with pytest.raises(ValueError,match='PACKET_CHANGED'):r.admit(binding)
    assert len(r.q.status()['tasks'])==1


def test_later_criticism_blocks_saved_queued_work_without_erasing_it(installed,monkeypatch):
    from orchestrator import change_requests as changes
    monkeypatch.setattr(catalog,'verify_eligibility',synthetic_eligibility)
    r=runtime.Runtime(installed.config)
    first=r.submit_research('next-discussion-v1',submitted_by=ACTOR)
    reference=installed.entry['change_request']
    folder=Path(installed.config['change_request_store'])/reference['request_id']
    changes.record(folder,'REVIEW',{**ACTOR,'family':'claude','model':'claude-fable-5'},
        {'applied_event':reference['applied_event'],'verdict':'REQUEST_CHANGES',
         'rationale':'Synthetic later criticism','review_evidence':'Synthetic fixture only',
         'affected_results':['Revalidate this exact queued task before dependent use']})
    binding=json.loads(r.q.db.execute('SELECT binding FROM tasks WHERE id=?',(first['task'],)).fetchone()[0])
    monkeypatch.setattr(runtime,'request_broker',lambda *args:pytest.fail('Criticism must stop before admission'))
    with pytest.raises(ValueError,match='RESEARCH_CHANGE_REQUIRES_CORRECTION'):r.admit(binding)
    assert r.research_inspect('next-discussion-v1')['saved']['status']=='QUEUED'
    assert r.research_inspect('next-discussion-v1')['reason']=='RESEARCH_CHANGE_REQUIRES_CORRECTION'


def test_new_pending_applied_version_is_not_approval(installed,monkeypatch):
    from orchestrator import change_requests as changes
    monkeypatch.setattr(catalog,'verify_eligibility',synthetic_eligibility)
    reference=installed.entry['change_request']
    folder=Path(installed.config['change_request_store'])/reference['request_id']
    changes.record(folder,'APPLIED',ACTOR,{'modification':'Synthetic new applied version',
        'checks':'Synthetic fixture','result_binding':'New fixture version','review_status':'PENDING'})
    with pytest.raises(ValueError,match='RESEARCH_CHANGE_REVIEW_PENDING'):
        runtime.Runtime(installed.config).submit_research('next-discussion-v1',submitted_by=ACTOR)


def test_historical_incomplete_turn_cannot_become_new_execution(installed,monkeypatch):
    r=runtime.Runtime(installed.config);first=r.submit_research()
    r.q.db.execute("UPDATE tasks SET status='BLOCKED' WHERE id=?",(first['task'],))
    config=copy.deepcopy(installed.config);config['source']='b'*40
    resumed=runtime.Runtime(config)
    monkeypatch.setattr(runtime,'request_broker',lambda *args:pytest.fail('No original stages exist'))
    resumed.recover()
    row=resumed.q.status()['tasks'][0]
    assert row['status']=='BLOCKED' and row['reason']=='HISTORICAL_STAGES_INCOMPLETE_NO_RETRY'
    assert resumed.q.tick()['status']=='WAITING_FOR_ELIGIBLE_WORK'


@pytest.mark.parametrize('bad',['../other','-other','a'*81,'--config','Uppercase'])
def test_bad_task_ids_refuse_before_catalog_read(installed,bad):
    with pytest.raises(ValueError,match='TASK_ID_REQUIRED'):catalog.selection(installed.config,bad)


def test_catalog_permissions_and_unexpected_names_refuse(installed):
    installed.folder.chmod(0o777)
    with pytest.raises(ValueError,match='PROTECTED_RESEARCH_CATALOG'):catalog.paths(installed.config)
    installed.folder.chmod(0o750)
    (installed.folder/'unexpected.txt').write_text('Synthetic fixture')
    with pytest.raises(ValueError,match='BOUNDED_RESEARCH_CATALOG'):list(catalog.paths(installed.config))


def test_retained_catalog_exceeds_schedule_bound_without_repeating_original(installed,monkeypatch):
    monkeypatch.setattr(catalog,'verify_eligibility',synthetic_eligibility)
    r=runtime.Runtime(installed.config)
    broker=MultiBroker();monkeypatch.setattr(runtime,'request_broker',broker)
    original=r.submit_research('next-discussion-v1',submitted_by=ACTOR)
    with patch('orchestrator.campaign_pipeline.grounding',return_value={}),patch('orchestrator.research_context.evidence_context',return_value={}):
        assert r.q.tick()['status']=='COMPLETE';r.bookkeeping()
    disposition=r.state/'tasks'/original['task']/'scientific-disposition.json'
    original_disposition=disposition.read_bytes()
    preserved={path.name:path.read_bytes() for path in installed.folder.iterdir()}
    for i in range(64):
        other=copy.deepcopy(installed.entry)
        other['request']['task']['task_id']='extra-'+str(i)
        installed.save(other)
    monkeypatch.setattr(runtime,'request_broker',lambda *args:pytest.fail('Catalog reads/reuse never admit or call a model'))
    resumed=runtime.Runtime(installed.config)
    assert resumed.submit_research('next-discussion-v1',submitted_by=ACTOR)['task']==original['task']
    assert len(resumed.q.status()['tasks'])==1
    assert resumed.q.status()['tasks'][0]['status']=='COMPLETE'
    assert disposition.read_bytes()==original_disposition
    assert len([call for call in broker.calls if call[1]=='model_stage'])==3
    listing=resumed.research_list()
    assert len(listing['requests'])==66  #65 retained entries plus the original legacy request.
    assert listing['catalog_history_limit'] is None and listing['scheduled_selection_bound']==32
    assert [x['task_id'] for x in listing['requests']]==sorted(x['task_id'] for x in listing['requests'])
    assert all((installed.folder/name).read_bytes()==raw for name,raw in preserved.items())
    assert catalog.selection(installed.config,'extra-63')[1]['request']['task']['task_id']=='extra-63'
    # Retention does not widen the explicitly configured selection per scheduler tick.
    configured={**installed.config,'research_schedule':{'task_ids':['extra-'+str(i) for i in range(33)]}}
    with pytest.raises(ValueError,match='FINITE_RESEARCH_SCHEDULE_REQUIRED'):runtime.research_schedule(configured)


def test_exact_lookup_does_not_enumerate_history_and_still_validates_bytes(installed,monkeypatch):
    def no_enumeration(path):
        pytest.fail('Exact ID lookup must not enumerate retained history')
    monkeypatch.setattr(Path,'iterdir',no_enumeration)
    assert catalog.selection(installed.config,'next-discussion-v1')[1]==installed.entry
    assert 'next-discussion-v1' in catalog.paths(installed.config)
    with pytest.raises(ValueError,match='UNKNOWN_INSTALLED_RESEARCH_TASK'):
        catalog.selection(installed.config,'missing-entry')
    changed=copy.deepcopy(installed.entry);changed['request']['task']['task_id']='different-version'
    (installed.folder/'next-discussion-v1.json').write_bytes(encoded(changed))
    with pytest.raises(ValueError,match='CATALOG_TASK_IDENTITY_MISMATCH'):
        catalog.selection(installed.config,'next-discussion-v1')


@pytest.mark.parametrize('kind',['symlink','directory'])
def test_exact_catalog_lookup_refuses_nonregular_entry(installed,kind):
    path=installed.folder/'invalid-entry.json'
    if kind=='symlink':path.symlink_to(installed.folder/'next-discussion-v1.json')
    else:path.mkdir()
    with pytest.raises(ValueError,match='PROTECTED_RESEARCH_CATALOG_ENTRY_REQUIRED'):
        catalog.selection(installed.config,'invalid-entry')


def test_human_wrapper_has_fixed_named_routes_and_refuses_extra_paths(tmp_path):
    live,controller,request=inputs()
    script=preparation().plan('c'*40,live,controller,request)['research-system-live-control.sh']
    # Authentication and exec are synthetic; run the actual generated shell.
    identity=tmp_path/'identity';identity.write_text('#!/bin/sh\necho 0\n');identity.chmod(0o700)
    script=script.replace('/usr/bin/id',str(identity))
    import sys
    dispatch=tmp_path/'dispatch'
    dispatch.write_text('#!'+sys.executable+'\nimport json,sys\nprint(json.dumps(sys.argv[1:]))\n');dispatch.chmod(0o700)
    script=script.replace('exec /usr/bin/env', 'exec '+str(dispatch))
    wrapper=tmp_path/'wrapper';wrapper.write_text(script)
    subprocess.run(['/bin/sh','-n',str(wrapper)],check=True)
    for args in (['research-list'],['research-inspect','next-discussion-v1'],['submit-research','next-discussion-v1'],['submit-research']):
        output=subprocess.run(['/bin/sh',str(wrapper),*args],capture_output=True,text=True,check=True)
        command=json.loads(output.stdout)
        assert command[-len(args):]==args
        assert '--config' in command and '/etc/research-system/live-research/controller.json' in command
        assert '--human' in command and 'orchestrator.handover_runtime' in command
    for args in (['research-list','x'],['research-inspect'],['research-inspect','../file'],
                 ['research-inspect','id','--config','/other'],['submit-research','-other']):
        refused=subprocess.run(['/bin/sh',str(wrapper),*args],capture_output=True,text=True)
        assert refused.returncode==2 and not refused.stdout


def test_fixed_transport_carries_actual_declared_submitter_separately(installed,monkeypatch):
    import pwd
    monkeypatch.setattr(runtime.os,'getuid',lambda:0)
    monkeypatch.setattr(pwd,'getpwuid',lambda uid:SimpleNamespace(pw_name='research-controller'))
    calls=[]
    def run(command,**kwargs):calls.append(command);return SimpleNamespace(stdout=b'{"models":0}')
    monkeypatch.setattr(runtime.subprocess,'run',run)
    runtime.controller_command(installed.config,'submit-research','/fixed/controller.json','next-discussion-v1',ACTOR)
    assert calls[0][-3]=='next-discussion-v1' and calls[0][-2]=='--submitter'
    assert json.loads(calls[0][-1])==ACTOR
    with pytest.raises(ValueError,match='TASK_ID_REQUIRED'):
        runtime.controller_command(installed.config,'submit-research','/fixed/controller.json','../file',ACTOR)
    assert len(calls)==1

def test_disposition_projection_refuses_before_queue_or_admission(installed, monkeypatch):
    from orchestrator.hosted_context import InputTooLarge
    monkeypatch.setattr(catalog, 'verify_eligibility', synthetic_eligibility)
    monkeypatch.setattr('orchestrator.hosted_context.build',
        lambda root, state: {'task_state': state, 'policy': 'x' * 900000})
    r = runtime.Runtime(installed.config)
    monkeypatch.setattr(r.q, 'submit', lambda *a: pytest.fail('queue reached before projection'))
    monkeypatch.setattr(runtime, 'request_broker', lambda *a: pytest.fail('broker reached before projection'))
    with pytest.raises(InputTooLarge):
        r.submit_research('next-discussion-v1', submitted_by=ACTOR)
    assert r.q.db.execute('SELECT count(*) FROM research_submissions').fetchone()[0] == 0
    retained = list(Path(installed.config['state']).glob('tasks/*/disposition-input-projection-refused.json'))
    assert len(retained) == 1
    refusal = json.loads(retained[0].read_text())
    assert refusal['models'] == refusal['admissions'] == 0
    assert refusal['measurement']['stage'] == 'disposition'
    assert (retained[0].parent/'packet.json').is_file()
