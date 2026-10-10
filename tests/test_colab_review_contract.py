"""Real Colab initialization/context composition; synthetic data, no model calls."""
import base64,copy,json,sqlite3
from pathlib import Path
from unittest.mock import patch
import pytest
from orchestrator import analysis_driver as a,colab_preparation_scope as c,notebook_revision as nr,scientific_intake as si,private_records as pr,cpu_isolation
from orchestrator.manual_executor import atomic,read,digest,ManualExecutor
from orchestrator.autonomy_accounting import BatchAccounts
from test_analysis_driver import initialization,analysis_lane
from test_aggregate_analysis_scope import aggregate_plan
from test_manual_lane import lane,root,ROOT,private_copied_fixture
from test_notebook_revision import fixture as notebook_fixture

@pytest.fixture
def initialized_colab(initialization,aggregate_plan,monkeypatch):
    d,review,receipt=initialization
    _,plan=aggregate_plan
    raw,selection,patchdata=notebook_fixture();view,_=si.derive(raw,selection,set())
    monkeypatch.setattr(nr,'ORIGINAL',digest(raw));monkeypatch.setattr(nr,'VIEW',digest(view))
    original=d.state/'synthetic-original.ipynb';pr.write_bytes(original,raw)
    def put(name,body):
        pr.write_bytes(d.context/name,body);return {'path':name,'sha256':digest(body)}
    cfg={'mode':c.MODE,'authority':{'path':'direction.txt','sha256':c.AUTHORITY},'original':{'path':str(original),'sha256':digest(raw)},
         'selection':put('selection.json',si.canonical(selection)),'safe_view':put('notebook-view.txt',view),
         'environment':{'environment_root':'/opt/synthetic-fixture','environment_sha256':'a'*64},
         'carried_conditions':put('conditions.json',si.canonical({'execution_authorized':False}))}
    registry=read(d.context/plan['private_intake']['path']);registry.update(task=c.TASK,idea_ids=c.IDEAS.copy());atomic(d.context/'registry.json',registry)
    plan.pop('aggregate_analysis');plan.update(idea_ids=c.IDEAS.copy(),private_intake={'path':'registry.json','sha256':digest((d.context/'registry.json').read_bytes())},
        colab_preparation={'schema':c.SCHEMA,'operator':{'path':'direction.txt','sha256':c.AUTHORITY},'item_number':4},notebook_revision=cfg)
    private_copied_fixture(d.context)
    plan['context_files']={str(p.relative_to(d.context)):digest(p.read_bytes()) for p in d.context.rglob('*') if p.is_file()}
    atomic(d.state/'colab-plan.json',plan)
    atomic(review.parent/'packet-manifest.json',{'files':{'evidence/colab-preparation-plan.json':digest((d.state/'colab-plan.json').read_bytes())}})
    d.store.batch.complete_run(d.config['run_id'],{'synthetic':True})
    target=d.state/'new-colab';result=a.initialize(d.root,target,review,d.state/'colab-plan.json')
    assert result['status']=='READY' and result['calls_used']==0
    monkeypatch.setattr(cpu_isolation,'verify_environment',lambda cfg: {'synthetic_environment':True})
    driver=a.AnalysisDriver(target)
    yield driver
    driver.store.db.close();driver.store.batch.db.close()

def test_real_initialized_colab_config_builds_author_and_reviewer_context(initialized_colab):
    d=initialized_colab
    assert d.config['review_contract']=='bound-review/v1'
    d.guard()
    for stage in ('run_spec_author','run_spec_review'):
        work=d.state/(stage+'-synthetic-input')
        body,measurement=d.prepare_input(d.current(),stage,work)
        assert body and measurement['stage']==stage
        assert ('notebook.patch.json' in measurement['outputs'])==(stage=='run_spec_author')
        assert list((work/'evidence').iterdir())
    assert not d.store.db.execute('SELECT 1 FROM manual_calls').fetchone()
    assert not d.store.batch.db.execute('SELECT 1 FROM autonomy_calls').fetchone()

@pytest.mark.parametrize('bad',[None,'legacy'])
def test_missing_or_wrong_contract_still_refuses(initialized_colab,bad):
    d=initialized_colab;d.config['review_contract']=bad
    with pytest.raises(ValueError,match='COLAB_BOUND_REVIEW_CONTRACT_REQUIRED'):d.guard()
    with pytest.raises(ValueError,match='NOTEBOOK_PATCH_OUTPUT_SCOPE'):
        d.prepare_input(d.current(),'run_spec_author',d.state/'must-not-exist')
    assert not (d.state/'must-not-exist').exists()

def test_unrelated_notebook_scope_is_not_enabled(initialized_colab):
    d=initialized_colab
    from orchestrator import manual_context
    for kwargs in [{'stage':'run_spec_review','structured_review':True,'private_intake':d.config['private_intake']},
                   {'stage':'run_spec_author','structured_review':True,'private_intake':None}]:
        with pytest.raises(ValueError,match='NOTEBOOK_PATCH_OUTPUT_SCOPE'):
            manual_context.prepare(d.context,idea_ids=d.config['idea_ids'],task='synthetic',artifacts=[],notebook_patch=True,**kwargs)
