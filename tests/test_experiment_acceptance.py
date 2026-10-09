"""Actual collection, input delivery, MCP submission, ledger and Git finalization.

Science and native events are explicitly synthetic; no model/patient/provider
call. Collection's existing fixture mocks provider and installed root selection.
"""
import json,subprocess
from pathlib import Path
import pytest
from orchestrator import experiment_acceptance as acceptance,experiment_collection as collection
from orchestrator import manual_context as mc,review_submission as rs,private_records as pr
from orchestrator.manual_driver import Driver,PROFILE
from orchestrator.manual_executor import digest
from test_experiment_collection import collected_lane,item4_dispatch,setup,root,private_test_environment
from test_scientific_intake import registered,save_registry


@pytest.fixture
def interpreted(collected_lane,monkeypatch,request):
    d,v,e,p,b,job=collected_lane
    ref,registry=registered(d.context,monkeypatch);registry.update(task='sprint13b-execution',idea_ids=['sprint13b-execution'])
    ref=save_registry(d.context,registry)
    collection.advance(d,v);collection.advance(d,v)
    assert collection.verified(d,v)['status']=='VALID'
    d.config.update(item_number=4,private_intake=ref,review_contract='bound-review/v1',execution_scope={},clients={'runtime_config_sha256':'b'*64},workspace_root=str(d.state/'scientific-workspaces'),
        idea_ids=['sprint13b-execution'],started_utc='2026-10-01T00:00:00+00:00')
    v.update(rounds={'result_interpretation_author':1},interventions=[])
    params=getattr(getattr(request.node,'callspec',None),'params',{})
    if params.get('close_finding'):
        from test_context_budget import add_obligation,save_manifest
        add_obligation(d.context,kind='adverse finding')
        path=d.context/PROFILE/'obligations.json';reg=json.loads(path.read_bytes())
        reg['obligations'][-1].update(severity='blocker',scope={'project':['isles24-prediction'],'idea_ids':['sprint13b-execution'],'stages':['*']})
        pr.atomic(path,reg);save_manifest(d.context)
    def workspace(stage):
        work=Path(d.config['workspace_root'])/(stage+'-1')
        text,measurement=mc.prepare(d.context,stage=stage,idea_ids=d.config['idea_ids'],task='Synthetic acceptance connection.',
            artifacts=v['artifacts'],workspace=work,private_intake=ref,structured_review=True,execution_mode='sprint13b-execution')
        pr.write_text(work/'prompt.md',text);pr.atomic(work/'input-measurement.json',measurement)
        ident=digest((d.config['run_id']+':'+stage+':1').encode())
        return work,text,ident
    author,prompt,aid=workspace('result_interpretation_author')
    text='# Summary\nThis synthetic fixture has an aggregate of 0.5. It is not a scientific result.\n# Details\nSynthetic only.\n'
    decision={'status':'PROPOSAL_ONLY','proposed_action_type':'stop','action':'Stop this synthetic fixture.',
        'rationale':'No actual experiment has run.','charter_basis':'','blocker_ids':[]}
    if params.get('close_finding'):decision.update(proposed_action_type='blocker_resolution',action='Resolve the synthetic discrepancy.',blocker_ids=['TEST-STOP'])
    pr.write_text(author/'interpretation.md',text);pr.write_bytes(author/'investigator_next_decision.json',rs.canonical(decision))
    receipt={'stage':'result_interpretation_author','workspace':str(author),'input_sha256':digest(prompt.encode()),
        'input_characters':len(prompt),'outcome':'COMPLETE','output_sha256':{name:digest((author/name).read_bytes()) for name in mc.OUTPUTS['result_interpretation_author']}}
    # Seed labelled synthetic call evidence; production accounting is unchanged.
    e.db.execute("INSERT INTO manual_calls VALUES(?,?,1,'COMPLETE',?)",(aid,'result_interpretation_author',json.dumps(receipt)))
    for kind,name in [('interpretation','interpretation.md'),('investigator_next_decision','investigator_next_decision.json')]:
        collection.artifact(d,v,kind,kind,name,(author/name).read_bytes())
    v.update(interpretation=str(author/'interpretation.md'),next_decision=str(author/'investigator_next_decision.json'))
    stage='result_interpretation_review';work,prompt,ident=workspace(stage)
    bindings={'call_id':ident,'run_id':d.config['run_id'],'stage':stage,'source_sha':d.config['source'],
        'runtime_sha256':d.config['clients']['runtime_config_sha256'],'input_sha256':digest(prompt.encode())}
    pins=rs.prepare(work,'scientific',bindings)
    verdict={'verdict':params.get('verdict','APPROVE'),'findings':[],'rationale':'Synthetic submission only; no real judgment.','bindings':bindings}
    ack=rs.submit(work,pins['config_sha256'],verdict)
    events=[{'type':'assistant','session_id':'synthetic','message':{'content':[{'type':'tool_use','id':'submit-1','name':rs.TOOL,'input':verdict}]}},
        {'type':'user','session_id':'synthetic','message':{'content':[{'type':'tool_result','tool_use_id':'submit-1','content':json.dumps(ack)}]}},
        {'type':'result','subtype':'success','is_error':False,'session_id':'synthetic'}]
    console=b'\n'.join(rs.canonical(x) for x in events);pr.write_bytes(work/'console.log',console)
    receipt={'stage':stage,'workspace':str(work),'input_sha256':digest(prompt.encode()),'input_characters':len(prompt),
        'submission_preflight':pins,'native':{'review_submission':rs.collect_scientific(work,console),'console_sha256':digest(console)},
        'outcome':'COMPLETE','output_sha256':{'review.json':digest((work/'review.json').read_bytes())}}
    e.db.execute("INSERT INTO manual_calls VALUES(?,?,1,'COMPLETE',?)",(ident,stage,json.dumps(receipt)))
    pending={'id':ident,'stage':stage,'round':1,'workspace':str(work)}
    v.update(pending=pending,review=str(work/'review.json'))
    d.finding_prefix=lambda stage:Driver.finding_prefix(d,stage)
    d.status=lambda:{'phase':v['phase'],'call_limit':20}
    return d,v,pending,p


def test_real_result_submission_seals_delivered_originals(interpreted):
    d,v,pending,provider=interpreted
    before=list(provider.calls)
    manifest=acceptance.record(d,v,pending)
    assert acceptance.verify(d,v)==manifest
    assert manifest['scientifically_reviewed'] and not manifest['successor_execution_authorized']
    assert manifest['fit_count']==1 and provider.calls==before
    assert d.store.db.execute('SELECT count(*) FROM manual_calls').fetchone()[0]==2


@pytest.mark.parametrize('damage',['result','validation','review','native','author','author_input','review_input','author_receipt','review_receipt','collection_ledger','local_ledger','collection_receipt','omitted_result'])
def test_modified_or_undelivered_evidence_never_accepts(interpreted,damage):
    d,v,pending,provider=interpreted;work=Path(pending['workspace']);job=next(iter(v['fit_collections']))
    if damage=='result':pr.write_text(d.state/'fit-results'/job/'aggregate.csv','changed')
    elif damage=='validation':pr.write_bytes(d.state/'validation.json',b'{}')
    elif damage=='review':pr.write_bytes(work/'review.json',b'{}')
    elif damage=='native':pr.write_bytes(work/'console.log',b'{}')
    elif damage=='author':pr.write_text(Path(v['interpretation']),'changed')
    elif damage in {'author_input','review_input'}:
        folder=Path(v['interpretation']).parent if damage=='author_input' else work
        pr.atomic(folder/'input-measurement.json',{'selected_artifacts':[],'workspace_files':[]})
    elif damage in {'author_receipt','review_receipt'}:
        stage='result_interpretation_author' if damage=='author_receipt' else 'result_interpretation_review'
        d.store.db.execute("UPDATE manual_calls SET status='UNCERTAIN' WHERE stage=?",(stage,))
    elif damage=='collection_ledger':d.store.batch.db.execute("UPDATE autonomy_compute SET status='RUNNING'")
    elif damage=='local_ledger':d.store.db.execute("UPDATE jobs SET status='RUNNING'")
    elif damage=='collection_receipt':pr.write_bytes(d.store._paths(job)/'collection-receipt.json',b'{}')
    else:v['artifacts']=[r for r in v['artifacts'] if r['type']!='result_tables']
    before=list(provider.calls)
    with pytest.raises(ValueError):acceptance.record(d,v,pending)
    assert 'reviewed_results' not in v and provider.calls==before


def git(root,*args):return subprocess.check_output(['git','-C',str(root),*args],text=True).strip()


@pytest.fixture
def committing(interpreted):
    d,v,pending,provider=interpreted
    d.root=d.state/'source';pr.mkdir(d.root)
    pr.copytree(d.context/PROFILE,d.root/PROFILE)
    git(d.root,'init','-b','astra/manual-synthetic-acceptance');git(d.root,'config','user.name','Synthetic Test');git(d.root,'config','user.email','synthetic@example.invalid')
    git(d.root,'add','.');git(d.root,'commit','-m','Synthetic initial state')
    d.config['profile_files']={str(p.relative_to(d.root)):digest(p.read_bytes()) for p in (d.root/PROFILE).rglob('*') if p.is_file()}
    acceptance.record(d,v,pending);v['phase']='UPDATE_STATE'
    return d,v,pending,provider


def test_actual_commit_report_and_repeat_finish_once_without_calls(committing):
    d,v,pending,p=committing
    calls=[tuple(r) for r in d.store.db.execute('SELECT * FROM manual_calls')];remote=list(p.calls)
    assert acceptance.prepare(d,v)['phase']=='REPORT'
    assert acceptance.finish(d,v)['phase']=='COMPLETE'
    head=git(d.root,'rev-parse','HEAD');report=(d.state/'REPORT.md').read_bytes();before=list(d.store.batch.db.iterdump())
    assert acceptance.finish(d,v)['phase']=='COMPLETE'
    assert git(d.root,'rev-parse','HEAD')==head and (d.state/'REPORT.md').read_bytes()==report
    assert list(d.store.batch.db.iterdump())==before
    assert [tuple(r) for r in d.store.db.execute('SELECT * FROM manual_calls')]==calls and p.calls==remote
    assert 'Reviewed experiment results' in (d.root/PROFILE/'STATE.md').read_text()
    assert 'Synthetic only.' in report.decode() and 'successor' in report.decode()
    assert d.store.batch.db.execute('SELECT status FROM autonomy_runs WHERE id=?',(d.config['run_id'],)).fetchone()[0]=='COMPLETE'


def test_resume_after_git_commit_uses_same_bytes(committing):
    d,v,pending,p=committing;acceptance.prepare(d,v)
    acceptance.commit(d,v);head=git(d.root,'rev-parse','HEAD')
    assert acceptance.finish(d,v)['phase']=='COMPLETE'
    assert git(d.root,'rev-parse','HEAD')==head


def test_unrelated_edit_never_swept_into_acceptance(committing):
    d,v,pending,p=committing;acceptance.prepare(d,v);head=git(d.root,'rev-parse','HEAD')
    pr.write_text(d.root/'unrelated.md','Keep this edit.\n')
    with pytest.raises(ValueError,match='^UNRELATED_EDITS_BEFORE_EXPERIMENT_ACCEPTANCE$'):acceptance.finish(d,v)
    assert git(d.root,'rev-parse','HEAD')==head and (d.root/'unrelated.md').read_text()=='Keep this edit.\n'


def test_actual_driver_approval_transition_records_the_result_seal(interpreted):
    d,v,pending,p=interpreted
    Driver._accept_completed(d,v)
    assert v['phase']=='UPDATE_STATE' and 'pending' not in v
    assert acceptance.verify(d,v)['scientifically_reviewed']


@pytest.mark.parametrize('verdict',['REVISE','REJECT'])
def test_genuine_nonapproval_submission_does_not_seal(interpreted,verdict):
    d,v,pending,p=interpreted
    with pytest.raises(ValueError,match='^EXPERIMENT_APPROVAL_REQUIRED$'):acceptance.record(d,v,pending)
    assert 'reviewed_results' not in v


@pytest.mark.parametrize('close_finding',[True])
def test_review_closure_preserves_author_time_proposal_binding(interpreted,close_finding):
    d,v,pending,p=interpreted
    manifest=acceptance.record(d,v,pending)
    from test_context_budget import save_manifest
    raw=Path(v['review']).read_bytes();path=d.context/'synthetic-finding-closure.json';pr.write_bytes(path,raw)
    registry=json.loads((d.context/PROFILE/'obligations.json').read_bytes())
    row=next(r for r in registry['obligations'] if r['id']=='TEST-STOP')
    row.update(status='closed',disposition={'path':path.name,'sha256':digest(raw),'start':0,'end':len(raw),'text':raw.decode()})
    pr.atomic(d.context/PROFILE/'obligations.json',registry);save_manifest(d.context)
    assert acceptance.verify(d,v)==manifest
    assert not mc.open_blocker_ids(d.context,'result_interpretation_review',d.config['idea_ids'])


def test_actual_driver_advance_routes_acceptance_without_legacy_fallthrough(committing):
    d,v,pending,provider=committing
    # The complete initializer/guard is exercised in test_experiment_driver;
    # this fixture binds real collection, submission and Git finalization.
    d.guard=lambda:None
    d.current=lambda:v
    before=list(provider.calls)
    assert Driver._advance(d)['phase']=='REPORT'
    assert Driver._advance(d)['phase']=='COMPLETE'
    head=git(d.root,'rev-parse','HEAD')
    assert Driver._advance(d)['phase']=='COMPLETE'
    assert git(d.root,'rev-parse','HEAD')==head and provider.calls==before


def test_missing_result_seal_refuses_before_repository_write(interpreted):
    d,v,pending,provider=interpreted
    before=list(provider.calls)
    with pytest.raises(ValueError,match='^EXPERIMENT_REVIEWED_RESULTS_REQUIRED$'):
        acceptance.prepare(d,v)
    assert not (d.state/'acceptance-commit').exists() and provider.calls==before
