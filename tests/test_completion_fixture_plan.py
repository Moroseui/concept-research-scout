"""Fixture migration cannot quietly become live or reuse an expanded allowance."""
import importlib.util
from pathlib import Path
import pytest


def module(monkeypatch):
    directory=Path(__file__).parents[1]/'deploy/research-system'
    monkeypatch.syspath_prepend(str(directory))
    spec=importlib.util.spec_from_file_location('completion_fixture',directory/'prepare_completion_fixture.py')
    result=importlib.util.module_from_spec(spec);spec.loader.exec_module(result);return result


def test_plan_preserves_old_and_bounds_new_turns(monkeypatch):
    m=module(monkeypatch)
    b={'mode':'SYNTHETIC_FIXTURE','model_mode':'SUPERVISED','writer_config':None,
       'max_model_turns':1,'sources':[m.OLD]}
    r={'source':m.OLD}
    new,config=m.planned(b,r,'a'*40,'/fixed/source')
    assert b['max_model_turns']==1 and r=={'source':m.OLD}
    assert new['max_model_turns']==3 and new['sources']==[m.OLD,'a'*40]
    assert config['report_schedule'] is None
    assert config['synthetic_execution']['pairs']=={'50-handover-aaaaaaa':'51-handover-aaaaaaa'}
    for key,value in [('mode','LIVE_APPROVED'),('writer_config','/key'),('max_model_turns',3),
                      ('model_mode','GOVERNED')]:
        with pytest.raises(ValueError,match='ORIGINAL_CONSUMED'):
            m.planned({**b,key:value},r,'a'*40,'/fixed/source')
    for changed in [{'source':'c'*40},{**r,'synthetic_execution':{}}]:
        with pytest.raises(ValueError,match='ORIGINAL_CONSUMED'):
            m.planned(b,changed,'a'*40,'/fixed/source')


def test_consumed_update_cannot_expand_model_or_writer_authority(monkeypatch):
    directory=Path(__file__).parents[1]/'deploy/research-system';monkeypatch.syspath_prepend(str(directory))
    spec=importlib.util.spec_from_file_location('fixture_update',directory/'update_consumed_handover_fixture.py')
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
    b={'mode':'SYNTHETIC_FIXTURE','model_mode':'SUPERVISED','writer_config':None,
       'sources':['a'*40],'max_model_turns':3,'policy':{'n':48}}
    r={'source':'a'*40,'purpose':'SUPERVISED_COMPLETION_ACCEPTANCE','report_schedule':None,
       'synthetic_execution':{'unchanged':'binding'}}
    new,config=m.plan(b,r,'a'*40,'b'*40,'/installed/source')
    assert new['max_model_turns']==3 and new['policy']==b['policy'] and new['writer_config'] is None
    assert config['synthetic_execution']==r['synthetic_execution']
    for changed in [{**r,'publication':{}},{**r,'report_schedule':{}},{**r,'purpose':'LIVE_APPROVED_HANDOVER'}]:
        with pytest.raises(ValueError,match='CONSUMED_SYNTHETIC'):
            m.plan(b,changed,'a'*40,'b'*40,'/installed/source')
