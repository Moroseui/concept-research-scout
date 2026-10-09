"""Actual scientific seal to incremental preprocessing and fit package.

Synthetic science and SDK fixture; the real source, review validator, worker,
collection ledger, dependency check and driver are used. Root provenance is
simulated only in the portable test, native in the separate root test.
"""
import copy,json,os
from pathlib import Path
import pytest
from orchestrator import private_records as pr,experiment_provisioning as provisioning
from orchestrator import experiment_preprocessing_dispatch as pd,experiment_dispatch as fd
from orchestrator.modal_executor import canonical,item4_job
from orchestrator.manual_executor import digest,inventory
from test_experiment_preprocessing_dispatch import (lane,connection,candidate,prepared,synthetic_provider,
    inventory_fixture,reviewed,root,experiment as original_experiment,fit_rows,tick)
from test_experiment_provisioning import root_identity

inventory_data=inventory
inventory=inventory_fixture


@pytest.fixture
def experiment(root,monkeypatch,connection):
    d,value=original_experiment.__wrapped__(root,monkeypatch,connection)
    path=root/'execution-plan.json';plan=json.loads(path.read_bytes());plan['dispatch_mode']='incremental'
    other=copy.deepcopy(plan['preprocessing'][0]);other['id']='coverage-dependent'
    plan['preprocessing'].append(other)
    plan['fits'][0]['preprocessing_id']=plan['preprocessing'][0]['id']
    fit=copy.deepcopy(plan['fits'][0]);fit.update(fit_id='fit-two',fold=1,preprocessing_id=other['id'])
    plan['fits'].append(fit);raw=canonical(plan);pr.write_bytes(path,raw)
    d.config['execution_scope']['plan_sha256']=digest(raw)
    prep=json.loads((d.state/'preparation-plan.json').read_bytes());prep['execution_scope']=d.config['execution_scope']
    prep['execution_plan']['sha256']=digest(raw);pr.write_bytes(d.state/'preparation-plan.json',canonical(prep))
    d.config['plan_sha256']=digest(canonical(prep))
    return d,value


def publish(ref,native):
    if native:return provisioning.publish(ref['path'],expected_sha256=ref['sha256'])
    record=provisioning.inspect(ref['path']);root=Path(record['config']['execution_provisioning'])
    pr.mkdir(root,exist_ok=True)
    pr.write_bytes(root/'wave-000001.json',canonical({'schema':'experiment-dispatch-wave/v1','index':1,
        'previous_sha256':None,'selection':record['selection'],'preparation':ref}))


def first_preprocessing(lane,native=False):
    d,rows,created,calls,stops,completed,_=lane
    ref=provisioning.prepare(d,d.current(),rows,d.state/'first-preparation',kind='preprocessing')
    publish(ref,native)
    for _ in range(3):tick(d)
    assert completed()['status']=='VALIDATED'
    tick(d);tick(d)
    assert len(created)==len(calls)==1
    assert d.current()['preprocessing_dispatch'][item4_job(rows[0]['binding'])]['phase']=='COMPLETE'
    return d


@pytest.mark.parametrize('reviewed',[4],indirect=True)
def test_missing_coverage_preprocessing_does_not_hold_independent_fit(lane):
    d=first_preprocessing(lane);rows=fit_rows(lane)
    before=[tuple(r) for r in d.store.batch.db.execute('SELECT * FROM autonomy_compute')]
    ref=provisioning.prepare(d,d.current(),rows,d.state/'first-fit');publish(ref,False)
    assert not pd.load(d,d.current())['complete_selection']
    tick(d)
    assert d.current()['fit_dispatch'][item4_job(rows[0]['binding'])]['phase']=='UPLOAD'
    assert not fd.load(d,d.current())['complete_selection']
    assert [tuple(r) for r in d.store.batch.db.execute('SELECT * FROM autonomy_compute')]==before
    assert d.current()['phase']=='EXECUTE_EXPERIMENT'


@pytest.mark.parametrize('reviewed',[4],indirect=True)
def test_fit_cannot_substitute_other_preprocessing_dependency(lane):
    d=first_preprocessing(lane);rows=fit_rows(lane)
    rows[0]['binding']['experiment']['fit_id']='fit-two'
    rows[0]['binding']['progress']['fit_id']='fit-two'
    rows[0]['binding']['progress']['fit_binding']['fold']=1
    with pytest.raises(ValueError,match='^EXPERIMENT_FIT_PREPROCESSING_CONNECTION$'):
        provisioning.prepare(d,d.current(),rows,d.state/'wrong-dependency')
    assert not (d.state/'wrong-dependency').exists()


@pytest.mark.parametrize('reviewed',[4],indirect=True)
@pytest.mark.skipif(os.geteuid()!=0,reason='Native root staged prerequisite publication checked separately')
def test_native_root_incremental_preprocessing_to_independent_fit(lane,root_identity):
    d=first_preprocessing(lane,native=True);pre=pd.directory(d.config);old=inventory_data(pre)
    rows=fit_rows(lane);ref=provisioning.prepare(d,d.current(),rows,d.state/'native-first-fit')
    publish(ref,True);tick(d)
    assert d.current()['fit_dispatch'][item4_job(rows[0]['binding'])]['phase']=='UPLOAD'
    assert old==inventory_data(pre)
    assert not pd.load(d,d.current())['complete_selection']
    assert all(p.stat().st_mode&0o777==0o440 for p in pre.iterdir())
