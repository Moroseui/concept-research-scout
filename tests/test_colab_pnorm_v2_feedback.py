"""Initial schema feedback remains static, scoped and accounted normally."""
import json,os
from pathlib import Path
from types import SimpleNamespace as NS
import pytest
from orchestrator import colab_pnorm_v2_feedback as f,colab_arm_question as q
from test_colab_static_feedback import feedback,call

def test_real_checker_rejects_array_then_accepts_string_in_same_workspace(tmp_path):
    patch,folder=feedback(tmp_path)
    original=patch['edits'][0]['replacement']
    patch['edits'][0]['replacement']=[original]
    (tmp_path/'notebook.patch.json').write_text(json.dumps(patch))
    failed=call(tmp_path,folder)
    assert failed.returncode==1 and 'AUTHOR_PATCH_EDIT_SCHEMA' in failed.stdout
    patch['edits'][0]['replacement']=original
    (tmp_path/'notebook.patch.json').write_text(json.dumps(patch))
    passed=call(tmp_path,folder)
    assert passed.returncode==0 and 'FORMAT_PASS_NOT_SCIENTIFIC_APPROVAL' in passed.stdout
    assert not list(tmp_path.rglob('*.sqlite'))

class Base:
    def __init__(self,run=q.RUN):
        self.config={'run_id':run};self.store=object()
    def task(self,stage,value):return 'BASE TASK'
    def prepare_input(self,value,stage,work):
        return self.task(stage,value),{'workspace_files':[]}

def test_initial_author_gets_hashed_readonly_feedback_before_transport(tmp_path,monkeypatch):
    os.umask(0o077)
    monkeypatch.setattr(q,'validate',lambda store,run: {'run_id':run})
    files={'.colab-feedback/check.py':b'print("static")'+bytes([10])}
    monkeypatch.setattr(f,'feedback_files',lambda driver:files)
    driver=f.prepared(Base)()
    body,receipt=driver.prepare_input({},'run_spec_author',tmp_path)
    assert 'INITIAL AUTHOR SCHEMA FEEDBACK' in body and 'at most12' in body
    assert 'notebook.patch.json' in body and 'FILE-BASED submission' in body
    assert receipt['workspace_files']==[{'path':'.colab-feedback/check.py',
        'sha256':q.sha(files['.colab-feedback/check.py']),'bytes':len(files['.colab-feedback/check.py'])}]
    assert (tmp_path/'.colab-feedback/check.py').stat().st_mode&0o777==0o400
    assert not hasattr(driver,'_pnorm_v2_feedback')
    with pytest.raises(ValueError,match='FEEDBACK_EXISTS'):
        driver.prepare_input({},'run_spec_author',tmp_path)

@pytest.mark.parametrize('run,stage',[('other','run_spec_author'),(q.RUN,'run_spec_review')])
def test_unrelated_stage_and_run_unchanged(tmp_path,monkeypatch,run,stage):
    monkeypatch.setattr(f,'feedback_files',lambda driver:pytest.fail('wrong scope'))
    assert f.prepared(Base)(run).prepare_input({},stage,tmp_path)==('BASE TASK',{'workspace_files':[]})
    assert list(tmp_path.iterdir())==[]

def test_question_failure_refuses_before_workspace_files(tmp_path,monkeypatch):
    def refused(*args):raise ValueError('actual-question-refusal')
    monkeypatch.setattr(q,'validate',refused)
    with pytest.raises(ValueError,match='actual-question-refusal'):
        f.prepared(Base)().prepare_input({},'run_spec_author',tmp_path)
    assert not list(tmp_path.iterdir())

def test_scope_keeps_exhausted_old_question_and_new_question_distinct():
    scope=q.document()
    assert scope['arm']=='A1_L'
    assert scope['prior']['config']['run_id']!=q.RUN
    assert len(scope['prior']['local_calls'])==24
    old=json.loads(scope['prior']['state_row']['payload'])
    assert old['phase']=='BLOCKED' and old['reason']=='OUTPUT_VALIDATION_REFUSED: ANALYSIS_REVISION_ROUND'
    assert scope['execution_authorized'] is False

def test_actual_feedback_builder_executes_json_and_binding_path(tmp_path,monkeypatch):
    from orchestrator import notebook_revision as nr,scientific_intake as intake
    from orchestrator import colab_preparation_scope as scope
    os.umask(0o077)
    cases={'cases':['sub-stroke'+str(9000+i) for i in range(99)]}
    cohort=json.dumps(cases).encode()
    (tmp_path/'synthetic-cohort.json').write_bytes(cohort)
    monkeypatch.setattr(intake,'COHORT_SHA256',q.sha(cohort))
    registry=json.dumps({'cohort':'synthetic-cohort.json'}).encode()
    (tmp_path/'registry.json').write_bytes(registry)
    # Partition derivation/visibility is covered by the existing controller tests.
    # Exercise the actual complete builder here, never replace feedback_files.
    monkeypatch.setattr(scope,'validate_notebook_config',lambda root,cfg:(b'fixture',{}))
    monkeypatch.setattr(nr,'partition',lambda *args:(b'visible source',{'units':[]}))
    driver=NS(context=tmp_path,config={'notebook_revision':{},'private_intake':{
        'path':'registry.json','sha256':q.sha(registry)}})
    files=f.feedback_files(driver)
    binding=json.loads(files['.colab-feedback/binding.json'])
    assert binding['run_id']==q.RUN
    assert binding['analysis_registry_sha256']==q.sha(registry)
    assert files['.colab-feedback/view.txt']==b'visible source'
    assert files['.colab-feedback/check.py']
    assert not any('previous-' in name for name in files)
    assert not any(case.encode() in raw for case in cases['cases'] for raw in files.values())
