"""Known-case preparation and supervisor tests; no cache load or training."""
import hashlib
import importlib.util
import json
from pathlib import Path
from types import SimpleNamespace
import pytest
from orchestrator import private_records
from tools.prepare_sprint9_modal import prepare, NOTEBOOK_SHA256

ROOT=Path(__file__).resolve().parents[1]

def load(name):
    spec=importlib.util.spec_from_file_location('smoke_'+name,ROOT/'experiments/sprint9_modal'/f'{name}.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module


def test_generated_science_provenance_matches_committed_bytes():
    p=ROOT/'experiments/sprint9_modal';record=json.loads((p/'science-provenance.json').read_text())
    assert record['source_notebook_sha256']==NOTEBOOK_SHA256
    assert record['science_sha256']==hashlib.sha256((p/'science.py').read_bytes()).hexdigest()
    assert len(record['segments'])==44


def test_extraction_rejects_altered_original_without_executing(tmp_path):
    fake=tmp_path/'notebook.ipynb';fake.write_text('{"cells": []}')
    with pytest.raises(ValueError,match='NOTEBOOK_CHANGED'):prepare(fake,tmp_path/'output')
    assert not (tmp_path/'output').exists()


@pytest.fixture
def protocol(monkeypatch):
    w=load('worker');cases=[f'dev-{n:03}' for n in range(99)];train=cases[20:]
    cfg={'cases':cases,'cache_file_hashes':{x:'d'*64 for x in cases},'partitions':{'train':train,'held':cases[:20],'inner_val':train[:16],
         'inner_train':train[16:],'vol_folds':[train[j::3] for j in range(3)]},'cnn':w.CNN,'feature_cfg':w.FEATURE_CFG,'versions':w.VERSIONS,'source_notebook_sha256':NOTEBOOK_SHA256}
    contract={'cohort_sha256':w.sha(w.canonical(cases)),'cache_map_sha256':w.sha(w.canonical(cfg['cache_file_hashes'])),'split_sha256':w.sha(w.canonical(cfg['partitions']))}
    monkeypatch.setattr(w,'CONTRACT',contract)
    return w,cfg,contract


def test_bounded_smoke_protocol_accepts_only_bound_config(protocol):
    w,cfg,contract=protocol;assert w.validate_config(cfg,contract)==cfg
    cfg['cnn']={**cfg['cnn'],'max_epochs':3}
    with pytest.raises(ValueError,match='PROTOCOL'):w.validate_config(cfg,contract)

@pytest.mark.parametrize('damage',['cohort','cache','partition','leakage','inner','versions'])
def test_smoke_refuses_wrong_cohort_split_cache_and_environment(protocol,damage):
    w,cfg,contract=protocol
    if damage=='cohort':cfg['cases']=cfg['cases'][:-1]
    if damage=='cache':cfg['cache_file_hashes'][cfg['cases'][0]]='b'*64
    if damage=='partition':cfg['partitions']['held'].reverse()
    if damage=='leakage':cfg['partitions']['train'][0]=cfg['partitions']['held'][0]
    if damage=='inner':cfg['partitions']['inner_train'][0]=cfg['partitions']['inner_val'][0]
    if damage=='versions':cfg['versions']={**cfg['versions'],'torch':'changed'}
    with pytest.raises(ValueError):w.validate_config(cfg,contract)


@pytest.fixture
def supervisor(tmp_path):
    r=load('run');p=tmp_path/'package';p.mkdir();work=tmp_path/'work';work.mkdir()
    for name,raw in {'worker.py':b'# Synthetic only.','SPEC.md':b'synthetic spec','review.json':b'{"verdict":"APPROVE"}'}.items():(p/name).write_bytes(raw)
    files={x.name:r.sha(x.read_bytes()) for x in p.iterdir()}
    binding={'code_sha256':r.sha(r.canonical({'worker.py':files['worker.py']})),'spec_sha256':files['SPEC.md'],'review_sha256':files['review.json'],
             'resources':{'timeout_seconds':60},'outputs':['result.csv','console.log','started.json']}
    (p/'manifest.json').write_bytes(r.canonical({'schema':'modal-run/v1','binding':binding,'files':files}))
    calls=[]
    def execute(*args,**kwargs):
        calls.append((args,kwargs));out=work/'outputs';out.mkdir();(out/'result.csv').write_bytes(b'synthetic result');return SimpleNamespace(returncode=0)
    return r,p,work,r.sha(r.canonical(binding)),execute,calls


def test_supervisor_runs_once_and_preserves_outputs(supervisor):
    r,p,w,b,execute,calls=supervisor;result=r.supervise(p,w,b,execute=execute,prepare_environment=lambda p:{})
    assert result['status']=='COMPLETE' and len(calls)==1
    assert set(result['files'])=={'result.csv','console.log','started.json'}
    with pytest.raises(FileExistsError):r.supervise(p,w,b,execute=execute,prepare_environment=lambda p:{})
    assert len(calls)==1
    private_records.check_tree(w/'outputs')


def test_supervisor_package_change_is_before_start(supervisor):
    r,p,w,b,execute,calls=supervisor;(p/'worker.py').write_text('changed')
    with pytest.raises(ValueError,match='PACKAGE_HASH'):r.supervise(p,w,b,execute=execute,prepare_environment=lambda p:{})
    assert not calls and not (w/'started.json').exists()


def test_supervisor_failure_is_preserved_never_retried(supervisor):
    r,p,w,b,execute,calls=supervisor
    def failed(*args,**kwargs):calls.append('failed');return SimpleNamespace(returncode=1)
    with pytest.raises(ValueError,match='WORKLOAD_FAILED'):r.supervise(p,w,b,execute=failed,prepare_environment=lambda p:{})
    assert json.loads((w/'research-result.json').read_text())['status']=='FAILED'
    with pytest.raises(FileExistsError):r.supervise(p,w,b,execute=execute,prepare_environment=lambda p:{})
    assert calls==['failed'] and (w/'worker-console.log').exists()


def test_offline_install_checks_wheels_before_pip(tmp_path,monkeypatch):
    r=load('run');package=tmp_path/'package';package.mkdir();wheels=tmp_path/'wheels';wheels.mkdir();target=tmp_path/'installed'
    (wheels/'fixture.whl').write_bytes(b'synthetic');(package/'requirements.lock').write_text('synthetic==0 --hash=sha256:'+r.sha(b'synthetic'))
    (package/'wheels.json').write_text(json.dumps({'files':{'fixture.whl':{'sha256':r.sha(b'synthetic'),'bytes':9}}}))
    calls=[]
    monkeypatch.setattr(r.subprocess,'run',lambda args,**kw:calls.append((args,kw)))
    env=r.offline_environment(package,wheels,target)
    assert len(calls)==1 and env['PYTHONPATH']==str(target)
    for flag in ['--no-index','--no-deps','--require-hashes','--only-binary=:all:']:assert flag in calls[0][0]
    assert calls[0][1]['timeout']==180 and calls[0][1]['check']
    (wheels/'fixture.whl').write_bytes(b'changed')
    with pytest.raises(ValueError,match='WHEEL_HASH'):r.offline_environment(package,wheels,target)
    assert len(calls)==1


def test_smoke_workload_rejects_a_different_self_consistent_cohort(protocol):
    patched,cfg,contract=protocol
    # Fresh unpatched production module: internally matching arbitrary cohort
    # hashes must not acquire authority to access a different patient set.
    actual=load('worker')
    with pytest.raises(ValueError,match='KNOWN_COHORT_PIN'):actual.validate_config(cfg,contract)
