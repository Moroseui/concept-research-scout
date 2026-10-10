"""Engineering bounds for the private Colab draft sibling, no scientific code."""
import json
from pathlib import Path
from types import SimpleNamespace
import pytest
from orchestrator import colab_preparation_scope as c


def fixture(tmp_path,monkeypatch):
    def put(name,raw):
        path=tmp_path/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(raw)
        return {'path':name,'sha256':c.digest(raw)}
    monkeypatch.setattr(c,'authority',lambda *args:c.AUTHORITY)
    operator=put('operator.txt',b'operator')
    monkeypatch.setattr(c,'AUTHORITY',operator['sha256'])
    original=put('original.ipynb',b'ORIGINAL');original['path']=str(tmp_path/'original.ipynb')
    monkeypatch.setattr(c.nr,'ORIGINAL',original['sha256'])
    view=put('view.txt',b'VIEW');monkeypatch.setattr(c.nr,'VIEW',view['sha256'])
    cfg={'mode':c.MODE,'authority':operator,'original':original,
        'selection':put('selection.json',b'{}'),'safe_view':view,
        'environment':{'environment_root':'/opt/example','environment_sha256':'a'*64},
        'carried_conditions':put('conditions.json',b'{"execution_authorized":false}')}
    from orchestrator import private_records
    monkeypatch.setattr(private_records,'check',lambda x:Path(x))
    manifest=put('manifest.json',b'{"per_patient_material":[]}')
    registry=put('registry.json',json.dumps({'cohort':'cohort.json','views':[{
        'manifest':manifest['path']}]}).encode());put('cohort.json',b'[]')
    monkeypatch.setattr(c.intake,'cohort',lambda raw:set())
    monkeypatch.setattr(c.intake,'load_views',lambda *args,**kwargs:([],{}))
    monkeypatch.setattr(c.intake,'scan',lambda *args,**kwargs:None)
    monkeypatch.setattr(c.nr,'partition',lambda *args:(b'',{}))
    item=SimpleNamespace(number=4,sha256='a'*64,mode='gpu',state='AUTHORIZED')
    plan={'context':str(tmp_path),'item_number':4,'item_sha256':item.sha256,
        'colab_preparation':{'schema':c.SCHEMA,'operator':operator,'item_number':4},
        'idea_ids':c.IDEAS.copy(),'private_intake':registry,'notebook_revision':cfg,'artifacts':[]}
    return plan,SimpleNamespace(items=[item]),put


def test_exact_scope_not_an_execution_permission(tmp_path,monkeypatch):
    plan,backlog,put=fixture(tmp_path,monkeypatch)
    assert c.validate(plan,backlog).number==4
    assert c.run_id(plan).startswith('colab-')
    text=c.instructions('run_spec_author',plan)
    for expected in ['Partho on Colab','notebook.patch.json','No full training',
                     'nonempty unittest.TestSuite','pending timing author24']:
        assert expected in text


@pytest.mark.parametrize('damage',['other_item','wrong_mode','not_authorized','mixed_scope','wrong_ideas',
    'operator_changed','original_changed','view_changed','execution_authority','env_extra','patient_manifest'])
def test_scope_and_privacy_refusals(tmp_path,monkeypatch,damage):
    plan,backlog,put=fixture(tmp_path,monkeypatch)
    if damage=='other_item':plan['item_number']=2
    elif damage=='wrong_mode':backlog.items[0].mode='analysis'
    elif damage=='not_authorized':backlog.items[0].state='PROPOSED'
    elif damage=='mixed_scope':plan['aggregate_analysis']={}
    elif damage=='wrong_ideas':plan['idea_ids'].append('unrelated')
    elif damage=='operator_changed':(tmp_path/'operator.txt').write_bytes(b'CHANGED')
    elif damage=='original_changed':(tmp_path/'original.ipynb').write_bytes(b'CHANGED')
    elif damage=='view_changed':(tmp_path/'view.txt').write_bytes(b'CHANGED')
    elif damage=='execution_authority':
        plan['notebook_revision']['carried_conditions']=put('changed.json',b'{"execution_authorized":true}')
    elif damage=='env_extra':plan['notebook_revision']['environment']['credentials']='forbidden'
    elif damage=='patient_manifest':(tmp_path/'manifest.json').write_text('{"per_patient_material":["forbidden"]}')
    with pytest.raises(ValueError):c.validate(plan,backlog)


def test_original_alias_refused(tmp_path,monkeypatch):
    plan,backlog,put=fixture(tmp_path,monkeypatch)
    alias=tmp_path/'alias.ipynb';alias.symlink_to(tmp_path/'original.ipynb')
    plan['notebook_revision']['original']['path']=str(alias)
    with pytest.raises(ValueError,match='ORIGINAL_PATH'):c.validate(plan,backlog)


def test_new_intake_gives_distinct_owner_without_changing_old(tmp_path,monkeypatch):
    plan,backlog,put=fixture(tmp_path,monkeypatch)
    before=c.run_id(plan);plan['private_intake']['sha256']='b'*64
    assert c.run_id(plan)!=before
    assert c.run_id(plan)!='experiment-a74959ac4546a982af4ae137'


@pytest.mark.parametrize('compile_pass',[True,False])
def test_artifact_hook_uses_isolated_exact_module_tests_and_keeps_holds(tmp_path,monkeypatch,compile_pass):
    plan,backlog,put=fixture(tmp_path,monkeypatch)
    workspace=tmp_path/'author';workspace.mkdir();(workspace/'notebook.patch.json').write_bytes(b'PATCH')
    monkeypatch.setattr(c,'validate_notebook_config',lambda *args:(b'ORIGINAL',{}))
    monkeypatch.setattr(c.nr,'apply',lambda *args,**kwargs:(b'NOTEBOOK',b'DIFF',
        {'compile':[{'compile':'PASS' if compile_pass else 'FAIL'}]}))
    monkeypatch.setattr(c.nr,'scan',lambda *args:None)
    from orchestrator import notebook_synthetic
    calls=[]
    def synthetic(*args,**kwargs):calls.append((args,kwargs));return {'status':'FAIL','reason':'fixture'}
    monkeypatch.setattr(notebook_synthetic,'run',synthetic)
    artifacts=[]
    driver=SimpleNamespace(config={'notebook_revision':plan['notebook_revision']},context=tmp_path,
        state=tmp_path/'state',artifact=lambda *args:artifacts.append(args))
    value={};c.prepare_notebook_artifacts(driver,value,{'workspace':str(workspace),'round':1},set())
    assert value['notebook_revision_result']['synthetic_status']=='FAIL'
    assert len(artifacts)==6
    if compile_pass:assert calls[0][1]=={'execution':True}
    else:assert not calls
    conditions=next(row for row in artifacts if row[1]=='execution_conditions')
    assert json.loads(conditions[3])['execution_authorized'] is False
