#!/usr/bin/env python3
"""Exercise selected thresholds in disposable synthetic policy/state, never live authority."""
from datetime import datetime,timezone,timedelta
import json
from pathlib import Path
import subprocess
import tempfile
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from orchestrator.dispatch_limiter import GitLedger,admit,initial,reset,REF

def require(condition):
    if not condition:raise ValueError('SYNTHETIC_ADMISSION_CHECK_FAILED')

def main():
    with tempfile.TemporaryDirectory(prefix='synthetic-admission-') as tmp:
        p=Path(tmp);subprocess.run(['git','init','-q',str(p)],check=True)
        store=GitLedger(p);require(store.cas(None,initial()))
        config={'status':'RATIFIED','operator_approval':'SYNTHETIC_TEST_ONLY_NOT_LIVE_AUTHORITY','state_write_permission':'OPERATOR_AUTHORIZED','n':48,'window':'UTC_CALENDAR_DAY','state_ref':REF,'reset_operators':['synthetic-operator']}
        now=datetime(2026,9,6,12,tzinfo=timezone.utc)
        def event(i):return {'run_id':str(i),'attempt':'1','source':'a'*40,'branch':'main'}
        results=[admit(store,config,event(i),now) for i in range(1,97)]
        require(results[47]['notification']=='N' and not results[47]['halted'])
        require(results[95]['notification']=='2N' and results[95]['halted'])
        require(admit(GitLedger(p),config,event(1),now)['duplicate_admission'])
        require(admit(store,config,event(97),now+timedelta(days=1))['status']=='HALTED_OPERATOR_RESET_REQUIRED')
        _,state=store.read()
        denied=False
        try:reset(store,config,{'actor':'agent','role':'agent','decision_ref':'fixture','expected_sequence':state['sequence']},now+timedelta(days=1))
        except ValueError:denied=True
        require(denied)
        reset(store,config,{'actor':'synthetic-operator','role':'operator','decision_ref':'SYNTHETIC_RESET_ONLY','expected_sequence':state['sequence']},now+timedelta(days=1))
        require(admit(store,config,event(98),now+timedelta(days=1))['count']==1)
    print(json.dumps({'scope':'SYNTHETIC_POLICY_ONLY','n':48,'hard_threshold':96,'warning_halt_duplicate_midnight_reset_verified':True,'live_activation':False,'operator_authentication_proven':False,'state_removed_after_fixture':True}))

if __name__=='__main__':main()
