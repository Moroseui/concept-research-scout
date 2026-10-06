"""Synthetic deterministic phase-delivery tests; no model calls or real data."""
import json
import sqlite3
import subprocess
from pathlib import Path
from types import SimpleNamespace
import pytest
from orchestrator import directions_analysis as da, manual_context, scientific_intake as intake
from orchestrator.manual_executor import digest
from test_context_budget import root
from test_scientific_intake import registered, selection, CASES


def put(root, name, raw):
    p=root/name; p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(raw)
    return {'path':name,'sha256':digest(raw)}


def make_plan(root, monkeypatch):
    ref, reg=registered(root,monkeypatch)
    reg.update(task=da.TASK,idea_ids=[da.TASK])
    ref=put(root,'registry-phase1.json',intake.canonical(reg))
    original=intake.canonical({'nbformat':4,'cells':[{'cell_type':'markdown','source':'OPERATOR IDEA FIXTURE: compare specialists with a single predictor.','outputs':[]}]})
    view, manifest=intake.derive(original,selection(original),CASES)
    idea=put(root,'operator-idea-view.txt',view)
    omission=put(root,'operator-idea-omissions.json',intake.canonical(manifest))
    row={'id':'operator-idea',**idea,'manifest':omission['path'],'manifest_sha256':omission['sha256'],'cohort_evidence':'Synthetic aggregate plan; no patient material.'}
    reg2={**reg,'views':reg['views']+[row]}
    phase2=put(root,'registry-phase2.json',intake.canonical(reg2))
    authority=Path(da.__file__).resolve().parents[1]/da.DOCUMENT
    operator=put(root,'operator.txt',authority.read_bytes())
    backlog=put(root,'BACKLOG.md',b'5. Synthetic directions including OPERATOR IDEA FIXTURE.\n')
    report=put(root,'completed-item2.md',b'Synthetic prior completed proposal.\n')
    return {'context':str(root),'item_number':5,'idea_ids':[da.TASK],'operator':operator,'backlog':backlog,
        'private_intake':ref,'artifacts':[], 'directions':{'phase2_intake':phase2,'operator_idea':idea,
        'completed_item2':{'run_id':'stocktake-6b556dba36d299c05b8b7770','report':report}}}


@pytest.fixture
def plan(root, monkeypatch):
    return make_plan(root, monkeypatch)


def test_both_phase1_roles_cannot_read_later_idea_or_full_backlog(plan):
    assert da.validate_plan(plan)
    root=Path(plan['context']);driver=SimpleNamespace(context=root,config=plan)
    for stage in da.PHASE1:
        work=root/'work'/stage
        text, measurement=manual_context.prepare(root,stage=stage,idea_ids=plan['idea_ids'],task=da.instructions(stage),
            artifacts=[],private_intake=plan['private_intake'],workspace=work,structured_review=True)
        da.check_delivery(driver,stage,text,measurement,work)
        all_bytes=text.encode()+b''.join(p.read_bytes() for p in work.rglob('*') if p.is_file())
        assert b'OPERATOR IDEA FIXTURE' not in all_bytes
        assert b'lesion-size' not in all_bytes
        assert len(text)<200000
        assert not (work/'BACKLOG.md').exists()


@pytest.mark.parametrize('field',['backlog','operator','idea'])
def test_inline_or_file_artifact_cannot_leak_later_material(plan,field):
    ref=plan['directions']['operator_idea'] if field=='idea' else plan[field]
    plan['artifacts']=[{'id':'leak','type':'prior_results','version':1,**ref}]
    with pytest.raises(ValueError,match='^DIRECTIONS_EARLY_OPERATOR_IDEA$'):da.validate_plan(plan)


def test_phase2_must_keep_all_originals_and_add_only_idea(plan):
    root=Path(plan['context']);reg=json.loads(da.bound(root,plan['directions']['phase2_intake']))
    reg['views']=reg['views'][1:]
    plan['directions']['phase2_intake']=put(root,'registry-phase2.json',intake.canonical(reg))
    with pytest.raises(ValueError,match='^DIRECTIONS_PHASE2_MUST_ADD_ONLY_OPERATOR_IDEA$'):da.validate_plan(plan)


def test_item2_completion_uses_actual_ledger_status_and_report_hash(plan):
    db=sqlite3.connect(':memory:');db.row_factory=sqlite3.Row
    db.executescript('CREATE TABLE autonomy_runs(id TEXT,status TEXT);CREATE TABLE events(id TEXT,payload TEXT);')
    batch=SimpleNamespace(db=db);cfg=plan['directions'];run=cfg['completed_item2']['run_id']
    with pytest.raises(ValueError,match='^DIRECTIONS_ITEM2_NOT_COMPLETE$'):da.require_item2_complete(batch,plan['context'],cfg)
    db.execute('INSERT INTO autonomy_runs VALUES(?,?)',(run,'COMPLETE'))
    db.execute('INSERT INTO events VALUES(?,?)',(run+':accepted',json.dumps({'report_sha256':'0'*64})))
    with pytest.raises(ValueError,match='^DIRECTIONS_ITEM2_NOT_COMPLETE$'):da.require_item2_complete(batch,plan['context'],cfg)
    db.execute('UPDATE events SET payload=?',(json.dumps({'report_sha256':cfg['completed_item2']['report']['sha256']}),))
    da.require_item2_complete(batch,plan['context'],cfg)
    db.execute("UPDATE autonomy_runs SET status='ACTIVE'")
    with pytest.raises(ValueError,match='^DIRECTIONS_ITEM2_NOT_COMPLETE$'):da.require_item2_complete(batch,plan['context'],cfg)


@pytest.fixture
def recorded(plan):
    root=Path(plan['context']);target=root/'accepted-spec';target.mkdir()
    spec=b'# Synthetic independent direction\nStudy measurement robustness.\n'
    review=b'{"verdict":"APPROVE","findings":[],"rationale":"Synthetic fixture only"}'
    (target/'SPEC.md').write_bytes(spec);(target/'review.json').write_bytes(review)
    subprocess.run(['git','init','-q',str(root)],check=True)
    for k,v in [('user.name','Synthetic fixture'),('user.email','fixture@invalid')]:subprocess.run(['git','-C',str(root),'config',k,v],check=True)
    subprocess.run(['git','-C',str(root),'add','accepted-spec'],check=True);subprocess.run(['git','-C',str(root),'commit','-qm','Synthetic phase1 fixture'],check=True)
    commit=subprocess.check_output(['git','-C',str(root),'rev-parse','HEAD'],text=True).strip()
    db=sqlite3.connect(':memory:');db.row_factory=sqlite3.Row
    db.execute('CREATE TABLE manual_calls(id TEXT,stage TEXT,status TEXT,receipt TEXT)')
    for stage,name,raw in [('run_spec_author','SPEC.proposed.md',spec),('run_spec_review','review.json',review)]:
        db.execute('INSERT INTO manual_calls VALUES(?,?,?,?)',(stage,stage,'COMPLETE',json.dumps({'synthetic':True,'output_sha256':{name:digest(raw)}})))
    cfg={**plan,'run_id':'synthetic-directions'}
    d=SimpleNamespace(root=root,context=root,state=root,config=cfg,store=SimpleNamespace(db=db),acceptance_path=lambda _:target)
    value={'spec':str(target/'SPEC.md'),'spec_review':str(target/'review.json'),'spec_commit':commit}
    return d,value


def test_phase2_requires_native_bindings_commit_and_preserved_phase1(recorded):
    d,value=recorded
    with pytest.raises(FileNotFoundError):da.registry(d,value,'result_interpretation_author')
    receipt=da.phase1_receipt(d,value);(d.state/'independent-directions.json').write_text(json.dumps(receipt))
    for stage in da.PHASE2:
        ref=da.registry(d,value,stage)
        body,measured=manual_context.prepare(d.context,stage=stage,idea_ids=d.config['idea_ids'],task=da.instructions(stage),artifacts=[],private_intake=ref,workspace=d.root/'work'/stage,structured_review=True)
        raws=[(d.root/'work'/stage/x['path']).read_bytes() for x in measured['workspace_files']]
        assert any(b'OPERATOR IDEA FIXTURE' in x for x in raws)
    d.store.db.execute("UPDATE manual_calls SET status='UNCERTAIN' WHERE stage='run_spec_review'")
    with pytest.raises(ValueError,match='^DIRECTIONS_PHASE1_NATIVE_BINDING_REQUIRED$'):da.registry(d,value,'result_interpretation_author')


def test_changed_phase1_or_missing_commit_refuses(recorded):
    d,value=recorded
    missing={**value,'spec_commit':None}
    with pytest.raises(ValueError,match='^DIRECTIONS_PHASE1_COMMIT_REQUIRED$'):da.phase1_receipt(d,missing)
    review=Path(value['spec_review']);review.write_text('{"verdict":"REVISE","findings":[{"id":"x"}]}')
    with pytest.raises(ValueError,match='^DIRECTIONS_PHASE1_NOT_APPROVED$'):da.phase1_receipt(d,value)


def test_item5_limit_is_sixteen_not_experiment_allowance():
    from orchestrator.autonomy_limits import selected_run_limit
    assert selected_run_limit({'run_id':'r','item_number':5,'backend':'analysis'},'r')==16
    assert selected_run_limit({'run_id':'r','item_number':5,'backend':'modal'},'r')==8


from test_analysis_driver import analysis_lane, item2_lane
from test_manual_lane import lane


def test_real_driver_four_stages_separate_phases_and_preserve_receipts(item2_lane,monkeypatch):
    from orchestrator import analysis_driver, autonomy_backlog, analysis_revisions, private_records
    from orchestrator.manual_executor import atomic, read
    from test_manual_lane import private_copied_fixture
    d=item2_lane;base=read(d.state/'preparation-plan.json');new=make_plan(d.context,monkeypatch)
    # Synthetic setup only: real phase delivery, ledger queries and transitions.
    backlog=b'1. Accepted stocktake.\n2. Completed proposal.\n3. Operator run DONE.\n4. GPU not approved.\n5. Directions; phase2 OPERATOR IDEA FIXTURE.\n'
    new['backlog']=put(d.context,'BACKLOG.md',backlog)
    parts=autonomy_backlog.numbered_items(backlog)
    binding={'schema':'operator-backlog/v1','backlog_sha256':digest(backlog),'operator_sha256':da.AUTHORITY,
        'items':[{'number':i,'sha256':parts[i][1],'mode':'gpu' if i==4 else 'analysis','state':'AUTHORIZED' if i==5 else 'NOT_AUTHORIZED','prerequisites':[1,2,3] if i==5 else []} for i in range(1,6)]}
    base.update(new,backlog_binding=put(d.context,'backlog-binding.json',json.dumps(binding).encode()),item_sha256=parts[5][1])
    base['artifacts']=[{'id':'operator-accepted-stocktake','type':'prior_results','version':1,**base['accepted_stocktake']['report']}]
    prior=base['directions']['completed_item2'];d.store.batch.db.execute('INSERT INTO autonomy_runs VALUES(?,?,?)',(prior['run_id'],'{}','COMPLETE'))
    d.store.batch.db.execute('INSERT INTO events VALUES(?,?,?)',(prior['run_id']+':accepted',prior['run_id'],json.dumps({'report_sha256':prior['report']['sha256']})))
    for document in (da.DOCUMENT, analysis_revisions.DOCUMENT):
        private_records.write_bytes(d.root/document,(Path(da.__file__).resolve().parents[1]/document).read_bytes())
    subprocess.run(['git','-C',str(d.root),'add',da.DOCUMENT,analysis_revisions.DOCUMENT],check=True);subprocess.run(['git','-C',str(d.root),'commit','-qm','Synthetic directions authority fixture'],check=True)
    private_copied_fixture(d.context)
    base['context_files']={str(p.relative_to(d.context)):digest(p.read_bytes()) for p in d.context.rglob('*') if p.is_file()}
    atomic(d.state/'preparation-plan.json',base)
    for key in ('operator','backlog','backlog_binding','private_intake','item_number','item_sha256','idea_ids','directions'):d.config[key]=base[key]
    d.config.update(plan_sha256=digest((d.state/'preparation-plan.json').read_bytes()),revision_policy=analysis_revisions.POLICY)
    atomic(d.state/'lane.json',d.config);value=d.current();value['artifacts']=base['artifacts'];d.save(value)
    assert analysis_driver.verify_plan(base)[1].number==5
    original_runner=d.runner;seen=[]
    def model(work,stage,*args):
        raw=(work/'prompt.md').read_bytes()+b''.join(p.read_bytes() for p in (work/'evidence').rglob('*') if p.is_file())
        assert (b'OPERATOR IDEA FIXTURE' in raw)==(stage in da.PHASE2)
        if stage in da.PHASE2:assert (d.state/'independent-directions.json').is_file()
        seen.append(stage)
        return original_runner(work,stage,*args)
    d.runner=model
    for expected in ['run_spec_review','COMMIT_SPEC','result_interpretation_author','result_interpretation_review','UPDATE_STATE','REPORT','COMPLETE']:
        result=d.advance();assert result['phase']==expected,result
    assert seen==list(da.PHASE1+da.PHASE2)
    assert d.status()['calls_used']==4 and d.status()['call_limit']==16
    assert d.advance()['calls_used']==4
    assert read(d.state/'independent-directions.json')==da.phase1_receipt(d,d.current())
    assert not d.store.db.execute('SELECT 1 FROM manual_packages').fetchone()
