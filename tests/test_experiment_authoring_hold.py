"""Real package/qualifier/dispatch gate; only science and SDK fixtures synthetic."""
import json,os
from pathlib import Path
import pytest
from orchestrator import private_records as pr, experiment_package as package
from orchestrator import experiment_dispatch as dispatch, experiment_preprocessing_dispatch as pd
from test_experiment_preprocessing_dispatch import (lane,connection,candidate,prepared,synthetic_provider,
    inventory_fixture,reviewed,root,experiment as original_experiment)
from orchestrator.modal_executor import canonical
from orchestrator.manual_executor import digest
inventory=inventory_fixture


@pytest.fixture(params=['flat','incremental'])
def experiment(root,monkeypatch,connection,request):
    d,value=original_experiment.__wrapped__(root,monkeypatch,connection)
    if request.param=='incremental':
        path=root/'execution-plan.json';plan=json.loads(path.read_bytes())
        plan['dispatch_mode']='incremental';plan['fits'][0]['preprocessing_id']=plan['preprocessing'][0]['id']
        raw=canonical(plan);pr.write_bytes(path,raw);d.config['execution_scope']['plan_sha256']=digest(raw)
        prep=json.loads((d.state/'preparation-plan.json').read_bytes());prep['execution_scope']=d.config['execution_scope']
        prep['execution_plan']['sha256']=digest(raw);pr.write_bytes(d.state/'preparation-plan.json',canonical(prep))
        d.config['plan_sha256']=digest(canonical(prep))
    return d,value


@pytest.mark.skipif(os.geteuid()!=0,reason='Native root-owned dispatch holds exercised separately')
@pytest.mark.parametrize('reviewed',[4],indirect=True)
def test_actual_seal_and_root_empty_selections_never_construct_provider(lane,monkeypatch):
    d,_,created,calls,stops,_,_=lane
    root=Path(d.config['execution_provisioning']);other=pd.directory(d.config)
    pr.mkdir(other);os.chown(other,0,1003);other.chmod(0o550)
    assert root.stat().st_uid==other.stat().st_uid==0
    assert root.stat().st_mode&0o777==other.stat().st_mode&0o777==0o550
    assert not list(root.iterdir()) and not list(other.iterdir())
    def forbidden(*a,**k):pytest.fail('Provider constructed before root runtime publication')
    d.provider_factory=forbidden;monkeypatch.setattr(dispatch,'ModalProvider',forbidden)
    before_local=[tuple(row) for row in d.store.db.execute('SELECT * FROM manual_calls')]
    from orchestrator.modal_budget import ComputeAccounts
    ComputeAccounts(d.store.batch)
    before_compute=[tuple(row) for row in d.store.batch.db.execute('SELECT * FROM autonomy_compute')]
    value=d.current();original=json.dumps(value,sort_keys=True)
    for _ in range(2):
        result=package.advance(d,value)
        assert result['next_action']=='WAIT_PREPROCESSING_PREPARATION'
        assert result['provider_called'] is False
    assert json.dumps(value,sort_keys=True)==original
    assert [tuple(row) for row in d.store.db.execute('SELECT * FROM manual_calls')]==before_local
    assert [tuple(row) for row in d.store.batch.db.execute('SELECT * FROM autonomy_compute')]==before_compute
    assert created==calls==stops==[]
    assert not list(root.iterdir()) and not list(other.iterdir())
