"""One new supervised fixture, no reset of the old allowance or live authority."""
import copy
import importlib.util
from pathlib import Path
import pytest

spec=importlib.util.spec_from_file_location('campaign_setup',Path(__file__).resolve().parents[1]/'deploy/research-system/prepare_campaign_acceptance.py')
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)


def configurations():
    source='a'*40
    broker={'mode':'SYNTHETIC_FIXTURE','model_mode':'SUPERVISED','writer_config':None,
            'max_model_turns':3,'sources':[source],'turn_root':'/private/broker/turns','ledger_repo':'/private/ledger',
            'policy':{'n':48,'status':'RATIFIED','operator_approval':'SYNTHETIC_FIXTURE_ONLY_NOT_LIVE'}}
    runtime={'source':source,'purpose':'SUPERVISED_COMPLETION_ACCEPTANCE','report_schedule':None,
             'synthetic_execution':{'authority':'OPERATOR_SUPERVISED_SYNTHETIC_ONLY','pairs':{'past':'past-next'},'source':'b'*40}}
    return broker,runtime,source


def test_one_fresh_turn_preserves_old_allowance_ledger_and_executor():
    broker,runtime,source=configurations();before=copy.deepcopy((broker,runtime))
    newbroker,newruntime=module.planned(broker,runtime,source)
    assert (broker,runtime)==before
    assert newbroker['max_model_turns']==1 and broker['max_model_turns']==3
    assert newbroker['turn_root']!=broker['turn_root']
    assert newbroker['ledger_repo']==broker['ledger_repo'] and newbroker['policy']==broker['policy']
    assert newruntime['synthetic_execution']['source']=='b'*40
    assert list(newruntime['synthetic_execution']['pairs'].values())==[None]
    assert newruntime['campaign_preparation']['mode']=='discuss'
    with pytest.raises(ValueError,match='CONSUMED_SYNTHETIC_CONFIGURATION_REQUIRED'):
        module.planned(newbroker,newruntime,source)


@pytest.mark.parametrize('change',[{'mode':'LIVE_APPROVED'},{'writer_config':'credential'},{'max_model_turns':4}])
def test_live_or_changed_allowance_refuses(change):
    broker,runtime,source=configurations();broker.update(change)
    with pytest.raises(ValueError,match='CONSUMED_SYNTHETIC_CONFIGURATION_REQUIRED'):
        module.planned(broker,runtime,source)


def test_partial_configuration_failure_restores_original_pair(tmp_path, monkeypatch):
    monkeypatch.setattr(module.os, 'chown', lambda *args: None)
    originals={'broker':b'old-broker', 'controller':b'old-controller'}
    replacements={'broker':b'new-broker','controller':b'new-controller'}
    for name,raw in originals.items():(tmp_path/name).write_bytes(raw)
    def fail_after_first_write():
        (tmp_path/'broker').write_bytes(replacements['broker'])
        raise RuntimeError('synthetic failure')
    with pytest.raises(RuntimeError,match='synthetic failure'):
        module.configuration_transaction(tmp_path,originals,replacements,fail_after_first_write)
    assert {n:(tmp_path/n).read_bytes() for n in originals}==originals


def test_recovery_preserves_concurrent_operator_edit(tmp_path):
    originals={'broker':b'old-broker','controller':b'old-controller'}
    replacements={'broker':b'new-broker','controller':b'new-controller'}
    for name,raw in originals.items():(tmp_path/name).write_bytes(raw)
    (tmp_path/'broker').write_bytes(b'operator edit')
    with pytest.raises(ValueError,match='CONCURRENT_CONFIGURATION_RECOVERY_HELD'):
        module.restore_configuration(tmp_path,originals,replacements)
    assert (tmp_path/'broker').read_bytes()==b'operator edit'
    assert (tmp_path/'controller').read_bytes()==originals['controller']


@pytest.mark.parametrize('state',['inactive','failed','activating','deactivating'])
def test_preparation_never_activates_previously_stopped_broker(state):
    with pytest.raises(ValueError,match='EXPECTED_ACTIVE_IDLE_BROKER_REQUIRED'):
        module.require_active_broker({'socket':'active','service':state})
    module.require_active_broker({'socket':'active','service':'active'})


def bounded_task(source,request='Assess the collected preflight without launch authority.'):
    import hashlib,json
    identity=hashlib.sha256(json.dumps({'source':source,'mode':'readiness','request':request},sort_keys=True).encode()).hexdigest()
    return {'mode':'readiness','request':request,'trigger_job':'61-assessment-'+identity[:32]}


def test_next_consumed_turn_is_request_bound_and_preserves_prior_configuration():
    b,r,source=configurations();b,r=module.planned(b,r,source)
    before=copy.deepcopy((b,r));task=bounded_task(source)
    nb,nr=module.planned(b,r,source,task)
    assert (b,r)==before and nb['max_model_turns']==1
    assert nb['turn_root']!=b['turn_root'] and nr['campaign_preparation']==task
    assert nb['ledger_repo']==b['ledger_repo'] and nb['policy']==b['policy']
    assert nr['synthetic_execution']['pairs']=={task['trigger_job']:None}
    with pytest.raises(ValueError,match='EXISTING_PREPARATION'):
        module.planned(nb,nr,source,task)


def test_new_task_cannot_reuse_identity_or_change_allowance():
    b,r,source=configurations();b,r=module.planned(b,r,source);task=bounded_task(source)
    task['request']='Changed request with old identity'
    with pytest.raises(ValueError,match='BOUND_TASK_IDENTITY'):
        module.planned(b,r,source,task)
    b['max_model_turns']=4
    with pytest.raises(ValueError,match='CONFIGURATION_REQUIRED'):
        module.planned(b,r,source,bounded_task(source))
