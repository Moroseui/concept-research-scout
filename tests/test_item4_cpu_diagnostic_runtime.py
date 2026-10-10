"""Retained scientific evidence and separately bound review/release identities."""
import json
from pathlib import Path
from types import SimpleNamespace as NS
import pytest
from tools import item4_smoke_response_runtime as route

@pytest.mark.parametrize('changed',[False,True])
def test_replay_authentic_historical_smoke_without_accepting_execution_drift(tmp_path,monkeypatch,changed):
    original={'spec':'original-author14','execution_package':{'sha256':'original'},'phase':'BLOCKED'}
    grant={'exact':'preserved consumed pair'}
    document={'original':original,'grant':grant}
    (tmp_path/'old.json').write_text(json.dumps(document))
    monkeypatch.setattr(route,'ROOT',tmp_path);monkeypatch.setattr(route,'trusted',Path)
    monkeypatch.setattr(route,'historical_response',lambda:'approved-original')
    checked=[]
    helper=NS(DOCUMENT='old.json',scope=lambda p,a:p['original'],
        granted=lambda store,p,a:checked.append(('grant',a)),proof=lambda p,a:p['grant'],
        protected_keys=lambda p:('execution_package',))
    current={**original,'spec':'legitimate-author15','post_smoke_response_scope':grant}
    if changed:current['execution_package']={'sha256':'forged'}
    def evidence(driver,value,p,a):
        assert value==original and value['spec']!='legitimate-author15'
        checked.append(('evidence',a));return ['original collected fit']
    smoke=NS(evidence=evidence);driver=NS(store=object())
    if changed:
        with pytest.raises(ValueError,match='RETAINED_EXECUTION_AUTHORITY'):
            route.retained_smoke_evidence(driver,current,smoke,{},'old-smoke-review',helper)
        assert checked==[('grant','approved-original')]
    else:
        assert route.retained_smoke_evidence(driver,current,smoke,{},'old-smoke-review',helper)==['original collected fit']
        assert checked==[('grant','approved-original'),('evidence','old-smoke-review')]
