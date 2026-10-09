"""Controller connection with synthetic notebook/authority; no patient or model execution."""
import json
from pathlib import Path
from types import SimpleNamespace
import pytest
from orchestrator import notebook_revision as nr, scientific_intake as si
from orchestrator import private_records, modal_item4_budget, notebook_synthetic, autonomy_backlog
from orchestrator.manual_driver import Driver
from test_notebook_revision import ReviewedSuccessorTests


@pytest.fixture
def configured(tmp_path,monkeypatch):
    base,selection,patch=ReviewedSuccessorTests().fixture()
    view,_=si.derive(base,selection,set())
    root=tmp_path/'context';private_records.mkdir(root)
    def put(name,raw):
        if not isinstance(raw,bytes):raw=si.canonical(raw)
        private_records.write_bytes(root/name,raw)
        return {'path':name,'sha256':si.sha(raw)}
    authority=b'Synthetic item4 scope.';ownership=b'Synthetic author owns notebook changes.'
    conditions=b'{"conditions":["Preserve the unresolved synthetic finding."],"scientific_acceptance":false}'
    # These substitutions bind synthetic fixture bytes. Real immutable pins are
    # tested separately; no qualification or scientific judgment is manufactured.
    for obj,key,value in [(nr,'SUCCESSOR_BASE',si.sha(base)),(nr,'SUCCESSOR_VIEW',si.sha(view)),
                          (nr,'SCIENTIFIC_OWNERSHIP',si.sha(ownership)),(nr,'CARRIED_CONDITIONS',si.sha(conditions)),
                          (modal_item4_budget,'AUTHORITY',si.sha(authority))]:
        monkeypatch.setattr(obj,key,value)
    original=tmp_path/'reviewed-base.ipynb';private_records.write_bytes(original,base)
    backlog=b'1. Accepted stocktake.\n2. Accepted notebook.\n3. Completed operator run.\n4. Approved synthetic smoke.\n'
    parts=autonomy_backlog.numbered_items(backlog)
    binding={'schema':'operator-backlog/v1','backlog_sha256':si.sha(backlog),'operator_sha256':si.sha(authority),
      'items':[{'number':n,'sha256':parts[n][1],'mode':'gpu' if n==4 else 'analysis',
                'state':'AUTHORIZED' if n==4 else 'NOT_AUTHORIZED','prerequisites':[1,2,3] if n==4 else []} for n in parts]}
    cfg={'mode':'item4-execution-revision','authority':put('authority.md',authority),
         'scientific_ownership':put('ownership.md',ownership),'original':{'path':str(original),'sha256':si.sha(base)},
         'selection':put('selection.json',selection),'safe_view':put('safe-view.txt',view),
         'environment':{'environment_root':str(tmp_path/'synthetic-env'),'environment_sha256':'a'*64},
         'backlog':put('BACKLOG.md',backlog),'backlog_binding':put('binding.json',binding),
         'item_sha256':parts[4][1],'carried_conditions':put('conditions.json',conditions)}
    return root,cfg,patch,conditions


def test_author_patch_reaches_same_controller_and_review_artifacts(configured,tmp_path,monkeypatch):
    root,cfg,patch,conditions=configured;before=Path(cfg['original']['path']).read_bytes()
    work=tmp_path/'author';private_records.mkdir(work);private_records.write_bytes(work/'notebook.patch.json',si.canonical(patch))
    calls=[]
    def synthetic(folder,notebook,environment,*,execution=False):
        assert execution is True
        calls.append((notebook,environment));assert b'x = 3' in notebook
        return {'status':'PASS','fixture':'synthetic test-runner output only','patient_data':False,'no_model_call':True}
    monkeypatch.setattr(notebook_synthetic,'run',synthetic)
    driver=SimpleNamespace(context=root,state=tmp_path/'lane',config={'run_id':'item4-fixture','notebook_revision':cfg})
    driver.artifact=lambda *args:Driver.artifact(driver,*args)
    value={'artifacts':[]};nr.prepare_artifacts(driver,value,{'workspace':str(work),'round':1},set())
    assert len(calls)==1 and Path(cfg['original']['path']).read_bytes()==before
    assert value['notebook_revision_result']['synthetic_status']=='PASS'
    expected={'notebook_source','notebook_diff','notebook_patch','synthetic_tests','notebook_provenance','execution_conditions'}
    assert {x['type'] for x in value['artifacts']}==expected
    carried=next(x for x in value['artifacts'] if x['type']=='execution_conditions')
    assert (root/carried['path']).read_bytes()==conditions
    assert b'HIDDEN' not in b''.join((root/x['path']).read_bytes() for x in value['artifacts'])
    assert not value['notebook_revision_result'].get('scientific_acceptance')


@pytest.mark.parametrize('damage,code',[
 ('authority','NOTEBOOK_CONFIG_CHANGED'),('ownership','NOTEBOOK_CONFIG_CHANGED'),
 ('conditions','NOTEBOOK_CONFIG_CHANGED'),('base','NOTEBOOK_ORIGINAL_CHANGED'),
 ('scope','BACKLOG_ITEM_NOT_AUTHORIZED'),('extra','NOTEBOOK_EXECUTION_CONFIG_FIELDS')])
def test_execution_revision_refuses_before_any_controller_execution(configured,damage,code):
    root,cfg,patch,_=configured
    if damage in ('authority','ownership','conditions'):
        key={'authority':'authority','ownership':'scientific_ownership','conditions':'carried_conditions'}[damage]
        private_records.write_text(root/cfg[key]['path'],'altered')
    elif damage=='base':private_records.write_text(cfg['original']['path'],'altered')
    elif damage=='scope':
        path=root/cfg['backlog_binding']['path'];value=json.loads(path.read_bytes())
        value['items'][-1]['state']='WAIT_OPERATOR';raw=si.canonical(value);private_records.write_bytes(path,raw)
        cfg['backlog_binding']['sha256']=si.sha(raw)
    else:cfg['extra']='unexpected'
    with pytest.raises(ValueError,match=code):nr.validate_config(root,cfg)


def test_installed_target_pins_remain_exact():
    assert nr.SUCCESSOR_BASE=='9e62bec160153ae605d0e4f5a3121977256fbc08e5a25a9421279a127c169a46'
    assert nr.CARRIED_CONDITIONS=='077b82acb5d028c1c645e9598e6abd4c472f6bce6027708752cb24362cd2d6d2'
