"""Exact pre-model terminal continuation tests; synthetic histories, no real calls."""
import copy,json
from types import SimpleNamespace
import pytest
from orchestrator import preparation_interleaving as pi
import test_preparation_interleaving as previous
from test_preparation_interleaving import admitted_history

@pytest.fixture(autouse=True)
def inert(monkeypatch):
    monkeypatch.setattr(pi,'_PREMODEL',None)
    from orchestrator import stocktake_review_recovery
    monkeypatch.setattr(stocktake_review_recovery,'completion',stocktake_review_recovery.completion)


def exact_history():
    scope,rows=previous_history()
    scope['source_sha']=pi.PREMODEL_SOURCE
    scope['lanes']['aggregate_analysis'].update(run_id=pi.PREMODEL_RUN,registry_sha256='65217d48c21993e61f86e74006b5d6e4d34f65f4fd0bb7be753e2b8641eef930')
    return scope,rows
previous_history=previous.history

class FixtureProof:
    def __init__(self,row,local=None):self.row=copy.deepcopy(row);self.local=copy.deepcopy(local)
    def verify_global(self,scope,row):
        assert row==self.row
        return {'id':pi.PREMODEL_CALL,'model_client_launched':False,'proof_sha256':'a'*64}
    def verify_local(self,scope,row,item):
        assert self.local is not None and item==self.local
        return self.verify_global(scope,row)

def failed(scope):
    row=previous.new_row(scope,'aggregate_analysis');row['status']='FAILED'
    return row

def test_default_refuses_exact_failed_and_unknown_statuses():
    scope,rows=exact_history();row=failed(scope)
    with pytest.raises(ValueError,match='PREMODEL_EXACT_ROW'):pi.classify(scope,rows+[row])


def test_exact_failure_stays_failed_counted_and_original_rows_unchanged():
    scope,rows=exact_history();row=failed(scope);before=pi.canonical(rows+[row])
    pi.configure_premodel(FixtureProof(row))
    retained,selected,counts=pi.classify(scope,rows+[row])
    assert len(retained)==76 and selected==[pi.PREMODEL_CALL] and counts['aggregate_analysis']==1
    assert pi.canonical(rows+[row])==before and row['status']=='FAILED'
    with pytest.raises(ValueError,match='PREMODEL_PROOF_CONFIGURATION'):pi.configure_premodel(FixtureProof(row))

@pytest.mark.parametrize('field,value',[('id','0'*64),('status','RUNNING'),('status','UNCERTAIN'),('round',2),('change_id','other')])
def test_proof_does_not_allow_other_rows_or_uncertainty(field,value):
    scope,rows=exact_history();row=failed(scope);pi.configure_premodel(FixtureProof(row));row[field]=value
    with pytest.raises(ValueError):pi.classify(scope,rows+[row])


def test_no_fake_terminal_proof():
    scope,rows=exact_history();row=failed(scope)
    proof=FixtureProof(row);proof.verify_global=lambda *a:{'id':pi.PREMODEL_CALL,'model_client_launched':True,'proof_sha256':'a'*64}
    pi.configure_premodel(proof)
    with pytest.raises(ValueError,match='PREMODEL_TERMINAL_PROOF'):pi.classify(scope,rows+[row])


def test_real_failed_first_then_normal_author2_admission_keeps_every_count(request,monkeypatch):
    from orchestrator import connectivity
    monkeypatch.setattr(previous,'history',exact_history)
    scope,original,batch,locals,overlay=request.getfixturevalue('admitted_history')
    local=locals['aggregate_analysis'];local.batch=batch
    policy={'status':'RATIFIED','operator_approval':'synthetic','state_write_permission':'OPERATOR_AUTHORIZED','n':4,'window':'UTC_CALENDAR_DAY','state_ref':'refs/heads/automation/dispatch-state','manual_semantics':'OPERATOR_STEP_D_MAX_EIGHT'}
    local.initialize_allowance(policy)
    monkeypatch.setattr(connectivity,'require',lambda *a,**k:{'synthetic':True})
    with pytest.raises(ValueError,match='^MANUAL_ACCOUNTING_BINDING$'):
        local.reserve_call(pi.PREMODEL_RUN,'run_spec_author',pi.PREMODEL_SOURCE,'astra/workstream-b-aggregate-20261010',policy,{'synthetic':True})
    first=dict(local.db.execute('SELECT * FROM manual_calls').fetchone())
    assert first['status']=='BLOCKED_BEFORE_MODEL'
    assert batch.status(pi.PREMODEL_CALL)['status']=='RUNNING'
    account_before=local.db.execute('SELECT * FROM manual_account').fetchone()
    assert json.loads(account_before['payload'])['count']==0
    receipt={'id':pi.PREMODEL_CALL,'outcome':'FAILED_BEFORE_MODEL','model_client_launched':False,'synthetic':True}
    batch.finish_scientific(pi.PREMODEL_CALL,receipt,'FAILED')
    global_failed=dict(batch.db.execute('SELECT * FROM autonomy_calls WHERE id=?',(pi.PREMODEL_CALL,)).fetchone())
    proof=FixtureProof(global_failed,first);pi.configure_premodel(proof)
    class OriginalDriver:
        def model_round_number(self,value):return value.get('rounds',{}).get(value['phase'],0)+1
    module=SimpleNamespace(AnalysisDriver=OriginalDriver)
    pi.install_driver_hook(module,proof)
    driver=module.AnalysisDriver();driver.config={'run_id':pi.PREMODEL_RUN,'source':pi.PREMODEL_SOURCE};driver.store=local
    value={'phase':'run_spec_author','rounds':{}}
    assert driver.model_round_number(value)==2 and value['rounds']=={}
    ident,n,second=local.reserve_call(pi.PREMODEL_RUN,'run_spec_author',pi.PREMODEL_SOURCE,'astra/manual-preparation-aggregate-analysis-20261010',policy,{'synthetic':True})
    assert ident==pi.identity(pi.PREMODEL_RUN,'run_spec_author',2) and n==2
    assert second['accounting']['status']=='ADMITTED'
    assert local.db.execute('SELECT count(*) FROM manual_calls').fetchone()[0]==2
    assert batch.db.execute('SELECT count(*) FROM autonomy_calls').fetchone()[0]==78
    assert dict(local.db.execute('SELECT * FROM manual_calls WHERE id=?',(pi.PREMODEL_CALL,)).fetchone())==first
    assert dict(batch.db.execute('SELECT * FROM autonomy_calls WHERE id=?',(pi.PREMODEL_CALL,)).fetchone())==global_failed
    account=json.loads(local.db.execute('SELECT payload FROM manual_account').fetchone()[0])
    assert account['count']==1 and len(account['events'])==1
    # One real local successful admission and two retained reservation slots.
    assert value['rounds']=={}
    other=module.AnalysisDriver();other.config={'run_id':'other'}
    assert other.model_round_number({'phase':'run_spec_author','rounds':{}})==1


from test_aggregate_analysis_scope import aggregate_plan
from test_analysis_driver import analysis_lane
from test_manual_lane import lane,root,ROOT,private_copied_fixture

def test_whole_analysis_driver_failed_first_then_author2_review_and_completion(aggregate_plan,monkeypatch):
    from pathlib import Path
    import subprocess
    from orchestrator import analysis_driver,aggregate_analysis_scope,private_records as pr
    from orchestrator.manual_executor import atomic,read,digest,ManualExecutor
    from orchestrator import stocktake_recovery,stocktake_review_recovery,experiment_timeout_continuation,completed_run,autonomy_limits
    from test_analysis_driver import fake_model
    d,plan=aggregate_plan
    atomic(d.state/'preparation-plan.json',plan)
    run=aggregate_analysis_scope.run_id(plan)
    for key in ('private_intake','idea_ids','backlog','backlog_binding','operator','item_number','item_sha256','aggregate_analysis'):
        d.config[key]=plan[key]
    d.config.update(run_id=run,plan_sha256=digest((d.state/'preparation-plan.json').read_bytes()))
    owner={'state':str(d.state),'source':d.config['source'],'run_id':run,'plan_sha256':d.config['plan_sha256'],'review_sha256':'f'*64,'aggregate_analysis':plan['aggregate_analysis']}
    d.config['owner_binding']=owner
    d.store.batch.db.execute("UPDATE autonomy_runs SET status='COMPLETE'")
    aggregate_analysis_scope.register(d.store.batch,run,owner)
    # Synthetic identities and approval evidence; all actual driver/ledger rules run.
    monkeypatch.setattr(pi,'PREMODEL_RUN',run);monkeypatch.setattr(pi,'PREMODEL_CALL',pi.identity(run,'run_spec_author',1));monkeypatch.setattr(pi,'PREMODEL_SOURCE',d.config['source'])
    scope,history=previous_history();scope['source_sha']=d.config['source'];scope['ledger']=str(d.store.batch.folder)
    scope['lanes']['aggregate_analysis'].update(run_id=run,registry_sha256=plan['private_intake']['sha256'],state=str(d.state),plan=str(d.state/'preparation-plan.json'),plan_sha256=d.config['plan_sha256'])
    for row in history:
        row['day']='2026-09-30';d.store.batch.db.execute('INSERT INTO autonomy_calls VALUES(?,?,?,?,?,?,?,?)',tuple(row.values()))
    scope['frozen_rows']={r['id']:pi.sha(pi.canonical(r)) for r in history}
    old=d.state/'old-item4';pr.mkdir(old);pr.write_text(old/'lane.json',json.dumps({'source':'e'*40}));ManualExecutor(old/'jobs.sqlite').db.close()
    scope['item4_scope']['configuration']['path']=str(old/'lane.json')
    def verify(self):self.approval='f'*64;return {'verdict':'APPROVE','synthetic':True}
    monkeypatch.setattr(pi.Overlay,'verify',verify);monkeypatch.setattr(pi,'_ACTIVE',None)
    monkeypatch.setattr(autonomy_limits,'scientific_batch_allowance',lambda *a,**k:{'limit':79,'scoped_run_id':pi.ITEM4_RUN})
    monkeypatch.setattr(stocktake_recovery,'global_exception',lambda *a,**k:None)
    monkeypatch.setattr(stocktake_review_recovery,'admission',lambda *a,**k:None)
    monkeypatch.setattr(experiment_timeout_continuation,'global_exception',lambda *a,**k:None)
    monkeypatch.setattr(completed_run,'closed_ids',lambda *a,**k:[])
    pi.connect(scope,d.state/'synthetic-review')
    bad='astra/workstream-b-aggregate-20261010';subprocess.run(['git','checkout','-qb',bad],cwd=d.root,check=True);d.config['branch']=bad;atomic(d.state/'lane.json',d.config)
    backend=[]
    def model(*args):backend.append(args[1]);return fake_model(*args)
    d.runner=model
    result=d.advance()
    assert result['phase']=='BLOCKED' and result['reason']=='ValueError: MANUAL_ACCOUNTING_BINDING',result
    assert backend==[]
    first=dict(d.store.db.execute('SELECT * FROM manual_calls').fetchone())
    assert first['status']=='BLOCKED_BEFORE_MODEL'
    first_workspace={p.name:p.read_bytes() for p in (Path(json.loads(first['receipt'])['workspace'])).iterdir() if p.is_file()}
    d.store.batch.finish_scientific(pi.PREMODEL_CALL,{'id':pi.PREMODEL_CALL,'outcome':'FAILED_BEFORE_MODEL','model_client_launched':False,'synthetic':True},'FAILED')
    failed_row=dict(d.store.batch.db.execute('SELECT * FROM autonomy_calls WHERE id=?',(pi.PREMODEL_CALL,)).fetchone())
    good='astra/manual-preparation-aggregate-analysis-20261010';subprocess.run(['git','branch','-m',good],cwd=d.root,check=True);d.config['branch']=good;atomic(d.state/'lane.json',d.config)
    value=d.current();value.update(phase='run_spec_author',reason=None);d.save(value)
    proof=FixtureProof(failed_row,first);pi.configure_premodel(proof)
    monkeypatch.setattr(analysis_driver,'AnalysisDriver',analysis_driver.AnalysisDriver)
    pi.install_driver_hook(analysis_driver,proof)
    state=d.state;d.store.db.close();d.store.batch.db.close()
    d=analysis_driver.AnalysisDriver(state,runner=model)
    for expected in ['run_spec_review','COMMIT_SPEC','result_interpretation_author','result_interpretation_review','UPDATE_STATE','REPORT','COMPLETE']:
        result=d.advance();assert result['phase']==expected,result
    assert backend==['run_spec_author','run_spec_review','result_interpretation_author','result_interpretation_review']
    assert d.status()['calls_used']==5
    assert 'BLOCKED_BEFORE_MODEL (retained reservation; no model launched)' in (d.state/'REPORT.md').read_text()
    assert d.store.batch.db.execute('SELECT status FROM autonomy_runs WHERE id=?',(run,)).fetchone()[0]=='COMPLETE'
    assert dict(d.store.db.execute('SELECT * FROM manual_calls WHERE id=?',(pi.PREMODEL_CALL,)).fetchone())==first
    assert dict(d.store.batch.db.execute('SELECT * FROM autonomy_calls WHERE id=?',(pi.PREMODEL_CALL,)).fetchone())==failed_row
    assert {p.name:p.read_bytes() for p in (Path(json.loads(first['receipt'])['workspace'])).iterdir() if p.is_file()}==first_workspace
    assert (Path(json.loads(first['receipt'])['workspace']).parent/'run_spec_author-2/SPEC.proposed.md').is_file()
    assert d.store.batch.db.execute('SELECT count(*) FROM autonomy_calls').fetchone()[0]==81
    account=json.loads(d.store.db.execute('SELECT payload FROM manual_account').fetchone()[0]);assert account['count']==4
    assert d.current()['rounds']['run_spec_author']==2
    assert d.store.db.execute('SELECT count(*) FROM manual_packages').fetchone()[0]==0
    # The exact completion exception never excuses another unresolved row.
    d.store.batch.db.execute("INSERT INTO autonomy_calls VALUES(?,?,?,?,?,?,?,?)",('foreign','scientific',run,6,'2026-10-10','UNCERTAIN','{}',None))
    with pytest.raises(ValueError,match='BATCH_RUN_HAS_UNRESOLVED_CALL'):
        d.store.batch.complete_run(run,{'synthetic':'must refuse'})
