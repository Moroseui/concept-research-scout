"""Actual local/global admission on synthetic execution plans; no model calls."""
from pathlib import Path
import copy,json
import pytest
from test_experiment_context import experiment,root
from test_manual_lane import policy
from orchestrator import analysis_revisions as rev,experiment_context as ec,private_records
from orchestrator.manual_executor import ManualExecutor,atomic,digest,Accounts
from orchestrator.autonomy_accounting import BatchAccounts
from orchestrator.manual_driver import Driver


def store_for(d):
    d.config.update(root=str(Path(__file__).resolve().parents[1]),context=str(d.context),policy=policy())
    atomic(d.state/'lane.json',d.config)
    batch=BatchAccounts(d.context/'batch',filesystem_root=d.context)
    batch.register_run(d.config['run_id'],{'state':'/lane'})
    d.store=ManualExecutor(d.state/'jobs.sqlite',batch=batch);d.store.initialize_allowance(policy())
    return d.store,batch


def as_item4(d):
    d.config.update(item_number=4,backend='modal',run_id=ec.ITEM4_RUN,idea_ids=[ec.TASKS[4]],
                    notebook_revision={'mode':'item4-execution-revision'})
    d.config['execution_scope'].update(item_number=4,run_id=ec.ITEM4_RUN,authority_sha256=ec.ITEM4_AUTHORITY)
    plan=json.loads((d.state/'preparation-plan.json').read_bytes())
    for k in ('item_number','idea_ids','execution_scope','notebook_revision'):plan[k]=d.config[k]
    private_records.write_text(d.state/'preparation-plan.json',json.dumps(plan))
    d.config['plan_sha256']=digest((d.state/'preparation-plan.json').read_bytes())


@pytest.mark.parametrize('item,cap',[(4,20),(6,30)])
def test_scoped_role_limits_and_global_local_charges_remain_shared(experiment,monkeypatch,item,cap):
    d,_=experiment
    if item==4:as_item4(d)
    store,batch=store_for(d)
    monkeypatch.setattr('orchestrator.connectivity.require',lambda *a,**k:{'synthetic_fixture':True})
    assert rev.enabled(store,d.config['run_id'])
    assert f"{cap}-call allowance" in rev.instructions(store,d.config['run_id'])
    for round_no in range(1,5):
        ident,n,receipt=store.reserve_call(d.config['run_id'],'run_spec_author','a'*40,'astra/manual-test',policy(),{})
        assert n==round_no and receipt['batch_accounting']['run_limit']==cap
        store.finish_call(ident,receipt,'COMPLETE')
    with pytest.raises(ValueError,match='^STEP_D_MODEL_CALL_LIMIT$'):
        store.reserve_call(d.config['run_id'],'run_spec_author','a'*40,'astra/manual-test',policy(),{})
    assert batch.db.execute('SELECT count(*) FROM autonomy_calls').fetchone()[0]==4
    assert store.db.execute('SELECT count(*) FROM manual_calls').fetchone()[0]==4
    assert Accounts(store).read()[1]['count']==4


def test_actual_input_gets_item6_policy_without_item2_no_execution_language(experiment):
    d,value=experiment;store_for(d)
    text,_=Driver.prepare_input(d,value,'run_spec_author',d.state/'with-policy')
    assert 'BACKLOG item 6:' in text and '30-call allowance' in text
    assert 'at most three author revision/re-review cycles' in text
    assert 'This reviews an analysis-only proposal' not in text
    assert 'within the sixteen-call item2 allowance' not in text


@pytest.mark.parametrize('defect',['plan','selection','policy','root','no-selection'])
def test_unbound_execution_cannot_extend_legacy_role_limit(experiment,defect):
    d,_=experiment;store,batch=store_for(d)
    if defect=='plan':private_records.write_text(d.state/'preparation-plan.json','{}')
    else:
        if defect=='selection':d.config['execution_scope']['plan_sha256']='f'*64
        elif defect=='policy':d.config['revision_policy']['max_revision_rounds']=4
        elif defect=='root':d.config['root']=str(d.context)
        else:d.config.pop('execution_scope')
        atomic(d.state/'lane.json',d.config)
    with pytest.raises((ValueError,FileNotFoundError)):rev.enabled(store,d.config['run_id'])
    assert store.db.execute('SELECT count(*) FROM manual_calls').fetchone()[0]==0


def test_uncertain_call_still_cannot_be_retried(experiment,monkeypatch):
    d,_=experiment;store,batch=store_for(d)
    monkeypatch.setattr('orchestrator.connectivity.require',lambda *a,**k:{'synthetic_fixture':True})
    ident,n,receipt=store.reserve_call(d.config['run_id'],'run_spec_author','a'*40,'astra/manual-test',policy(),{})
    store.finish_call(ident,receipt,'UNCERTAIN')
    with pytest.raises(ValueError,match='^UNCERTAIN_MODEL_CALL_NO_RETRY$'):
        store.reserve_call(d.config['run_id'],'run_spec_author','a'*40,'astra/manual-test',policy(),{})
    assert Accounts(store).read()[1]['count']==1


@pytest.mark.parametrize('stage',['run_spec_review','result_interpretation_review'])
def test_three_rounds_and_reserved_decisions_use_unchanged_transition(experiment,stage):
    d,_=experiment;store,_=store_for(d);assert rev.enabled(store,d.config['run_id'])
    review={'verdict':'REVISE','findings':[{'category':'metric/statistic'}]}
    for n in (1,2,3):assert rev.review_transition(review,stage,n)[0]==stage.replace('_review','_author')
    assert rev.review_transition(review,stage,4)[1]=='UNRESOLVED_AFTER_THREE_REVISIONS'
    for category in rev.RESERVED:
        review['findings']=[{'category':category}]
        assert rev.review_transition(review,stage,1)[1]=='REVIEW_REQUIRES_OPERATOR_DECISION'
    assert rev.review_transition({'verdict':'REJECT','findings':[]},stage,1)[1]=='REVIEW_REJECTED'
