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
