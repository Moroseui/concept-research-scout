"""Synthetic-only scope/admission negatives; no patient records or model calls."""
import copy
import json
from pathlib import Path

import pytest
from orchestrator import aggregate_analysis_scope as scope, analysis_driver, autonomy_backlog, private_records
from orchestrator.manual_executor import digest, atomic, read
from test_analysis_driver import analysis_lane
from test_manual_lane import lane, root, ROOT, private_copied_fixture


@pytest.fixture
def aggregate_plan(analysis_lane):
    d = analysis_lane
    plan = read(d.state/'preparation-plan.json')
    backlog = b'# Backlog\n4. Approved thirteen B.\n6. Approved CPU diagnostics.\n'
    parts = autonomy_backlog.numbered_items(backlog)
    operator = b'Synthetic preserved backlog authority.'
    binding = {'schema':'operator-backlog/v1', 'backlog_sha256':digest(backlog), 'operator_sha256':digest(operator),
               'items':[{'number':n,'sha256':parts[n][1],'mode':m,'state':'AUTHORIZED','prerequisites':[]}
                        for n,m in ((4,'gpu'),(6,'cpu'))]}
    for key, name, raw in [('backlog','BACKLOG.md',backlog), ('operator','operator.txt',operator),
                           ('backlog_binding','backlog-binding.json',json.dumps(binding).encode())]:
        private_records.write_bytes(d.context/name, raw)
        plan[key] = {'path':name,'sha256':digest(raw)}
    decision = (ROOT/scope.DOCUMENT).read_bytes()
    private_records.write_bytes(d.context/'direction.txt', decision)
    registry = read(d.context/plan['private_intake']['path'])
    registry.update(task=scope.TASK, idea_ids=[scope.TASK,'post-result-synthesis-20261010'])
    atomic(d.context/'registry.json',registry)
    plan.update(item_number=4,item_sha256=parts[4][1],idea_ids=registry['idea_ids'],
        private_intake={'path':'registry.json','sha256':digest((d.context/'registry.json').read_bytes())},
        aggregate_analysis={'schema':scope.SCHEMA,'operator':{'path':'direction.txt','sha256':scope.AUTHORITY},
                            'related_items':{str(n):parts[n][1] for n in (4,6)}})
    private_copied_fixture(d.context)
    plan['context_files'] = {str(p.relative_to(d.context)):digest(p.read_bytes()) for p in d.context.rglob('*') if p.is_file()}
    return d,plan


def test_aggregate_plan_preserves_original_backlog_modes(aggregate_plan):
    d,p=aggregate_plan
    before=(d.context/'BACKLOG.md').read_bytes()
    backlog,item=analysis_driver.verify_plan(p)
    assert item.number==4 and item.mode=='gpu'
    assert (d.context/'BACKLOG.md').read_bytes()==before
    assert scope.run_id(p).startswith('aggregate-')
    assert 'no patient reads' in scope.instructions('run_spec_author',p)


@pytest.mark.parametrize('field,value',[('schema','other'),('related_items',{'4':'0'*64,'6':'0'*64})])
def test_scope_substitution_refuses(aggregate_plan,field,value):
    d,p=aggregate_plan;p['aggregate_analysis'][field]=value
    with pytest.raises(ValueError,match='AGGREGATE_ANALYSIS'):
        analysis_driver.verify_plan(p)


def test_operator_binding_refuses(aggregate_plan):
    d,p=aggregate_plan;p['aggregate_analysis']['operator']['sha256']='0'*64
    with pytest.raises(ValueError,match='AGGREGATE_ANALYSIS_OPERATOR_BINDING'):
        analysis_driver.verify_plan(p)


def test_unknown_execution_field_refuses(aggregate_plan):
    d,p=aggregate_plan;p['executor']='modal'
    with pytest.raises(ValueError,match='ANALYSIS_PLAN_FIELDS'):
        analysis_driver.verify_plan(p)


def test_per_patient_material_cannot_enter_through_artifact(aggregate_plan):
    d,p=aggregate_plan
    raw=('sub-'+'stroke0001,0.5').encode()
    private_records.write_bytes(d.context/'unsafe.txt',raw)
    p['artifacts']=[{'path':'unsafe.txt','sha256':digest(raw),'id':'unsafe','type':'prior_results','version':1}]
    p['context_files']['unsafe.txt']=digest(raw)
    with pytest.raises(ValueError,match='PATIENT_LEVEL_CLASSIFICATION_REQUIRED'):
        analysis_driver.verify_plan(p)


def test_register_rolls_back_if_unrelated_active_owner(aggregate_plan):
    d,p=aggregate_plan
    atomic(d.state/'preparation-plan.json',p)
    binding={'state':str(d.state),'source':'a'*40,'run_id':scope.run_id(p),
             'plan_sha256':digest((d.state/'preparation-plan.json').read_bytes()),'review_sha256':'b'*64,
             'aggregate_analysis':p['aggregate_analysis']}
    before=d.store.batch.db.execute('SELECT count(*) FROM autonomy_runs').fetchone()[0]
    with pytest.raises(ValueError,match='ONE_ACTIVE_RESEARCH_RUN'):
        scope.register(d.store.batch,scope.run_id(p),binding)
    assert d.store.batch.db.execute('SELECT count(*) FROM autonomy_runs').fetchone()[0]==before
    assert not d.store.batch.db.in_transaction


def test_registration_coexists_only_with_bound_item4_and_keeps_global_call_serialization(aggregate_plan):
    d,p=aggregate_plan
    from orchestrator.experiment_context import ITEM4_RUN
    from orchestrator.modal_item4_policy import AUTHORITY
    batch=d.store.batch
    batch.db.execute("UPDATE autonomy_runs SET status='COMPLETE'")
    old=d.state.parent/'synthetic-item4';private_records.mkdir(old)
    execution={'schema':'scientific-execution/v1','item_number':4,'run_id':ITEM4_RUN,
               'authority_sha256':AUTHORITY,'plan_sha256':'c'*64}
    original=json.dumps({'execution_scope':execution,'execution_plan':{'sha256':'c'*64}}).encode()
    private_records.write_bytes(old/'preparation-plan.json',original)
    owner={'state':str(old),'run_id':ITEM4_RUN,'plan_sha256':digest(original),'execution_scope':execution}
    atomic(old/'lane.json',{'owner_binding':owner,'execution_scope':execution,'run_id':ITEM4_RUN,'plan_sha256':digest(original)})
    batch.db.execute("INSERT INTO autonomy_runs VALUES(?,?,'ACTIVE')",(ITEM4_RUN,json.dumps(owner)))
    atomic(d.state/'preparation-plan.json',p)
    binding={'state':str(d.state),'source':'a'*40,'run_id':scope.run_id(p),
             'plan_sha256':digest((d.state/'preparation-plan.json').read_bytes()),'review_sha256':'b'*64,
             'aggregate_analysis':p['aggregate_analysis']}
    scope.register(batch,scope.run_id(p),binding)
    assert batch.db.execute("SELECT count(*) FROM autonomy_runs WHERE status='ACTIVE'").fetchone()[0]==2
    with pytest.raises(ValueError,match='EXISTING_ANALYSIS_OWNER_NO_NEW_ALLOWANCE'):
        scope.register(batch,scope.run_id(p),binding)
    # Registration never inserts a call, allowance or compute reservation.
    assert batch.db.execute('SELECT count(*) FROM autonomy_calls').fetchone()[0]==0
    batch.db.execute("INSERT INTO autonomy_calls VALUES(?,?,?,?,?,?,?,?)",
        ('pending-exact','scientific',ITEM4_RUN,1,'2026-10-10','RUNNING','{}',None))
    with pytest.raises(ValueError,match='BATCH_UNCERTAIN_OR_RUNNING_CALL'):
        batch.reserve_scientific('a'*64,scope.run_id(p),'run_spec_author','a'*40,{})


def test_scoped_four_stage_flow_reads_all_views_without_execution(aggregate_plan):
    d,p=aggregate_plan
    atomic(d.state/'preparation-plan.json',p)
    run=scope.run_id(p)
    for key in ('private_intake','idea_ids','backlog','backlog_binding','operator','item_number','item_sha256','aggregate_analysis'):
        d.config[key]=p[key]
    d.config.update(run_id=run,plan_sha256=digest((d.state/'preparation-plan.json').read_bytes()))
    atomic(d.state/'lane.json',d.config)
    d.store.batch.db.execute("UPDATE autonomy_runs SET status='COMPLETE'")
    binding={'state':str(d.state),'source':d.config['source'],'run_id':run,
             'plan_sha256':d.config['plan_sha256'],'review_sha256':'b'*64,'aggregate_analysis':p['aggregate_analysis']}
    scope.register(d.store.batch,run,binding)
    seen=[]
    from test_analysis_driver import fake_model
    def fake(work,stage,clients,expected):
        measurement=read(work/'input-measurement.json')
        assert len(measurement['private_scientific_views'])>0
        seen.append(stage)
        return fake_model(work,stage,clients,expected)
    d.runner=fake
    for phase in ['run_spec_review','COMMIT_SPEC','result_interpretation_author','result_interpretation_review','UPDATE_STATE','REPORT','COMPLETE']:
        result=d.advance()
        assert result['phase']==phase,result
    assert seen==['run_spec_author','run_spec_review','result_interpretation_author','result_interpretation_review']
    assert d.status()['calls_used']==4
    assert d.store.batch.db.execute("SELECT count(*) FROM autonomy_calls WHERE change_id=?",(run,)).fetchone()[0]==4
    assert not d.store.db.execute('SELECT 1 FROM manual_packages').fetchone()
    assert read(d.state/'validation.json')['execution_performed'] is False
