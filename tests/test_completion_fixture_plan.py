"""Fixture migration cannot quietly become live or reuse an expanded allowance."""
import importlib.util
from pathlib import Path
import sys
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
