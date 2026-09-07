import copy
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime,timezone,timedelta
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from orchestrator.dispatch_limiter import GitLedger,admit,initial,reset,REF,validate

NOW=datetime(2026,9,6,12,tzinfo=timezone.utc)
def config(n=4):
    return {'status':'RATIFIED','operator_approval':'synthetic fixture only','state_write_permission':'OPERATOR_AUTHORIZED','n':n,'window':'UTC_CALENDAR_DAY','state_ref':REF,'reset_operators':['fixture-operator']}
def event(i,branch='main',attempt='1'):
    return {'run_id':str(i),'attempt':attempt,'source':'a'*40,'branch':branch}

class LimiterTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name)
        subprocess.run(['git','init','-q',str(self.root)],check=True)
        self.store=GitLedger(self.root);self.assertTrue(self.store.cas(None,initial()))
    def tearDown(self):self.tmp.cleanup()
    def test_thresholds_replays_reset_and_midnight(self):
        c=config(2)
        self.assertIsNone(admit(self.store,c,event(1),NOW)['notification'])
        r=admit(self.store,c,event(2,'astra/autonomous-isles-pilot'),NOW)
        self.assertEqual(r['notification'],'N');self.assertFalse(r['halted'])
        self.assertTrue(admit(self.store,c,event(2,'astra/autonomous-isles-pilot'),NOW)['duplicate_admission'])
        self.assertEqual(admit(self.store,c,event(2,'astra/autonomous-isles-pilot',attempt='2'),NOW)['count'],3)
        self.assertEqual(admit(self.store,c,event(3),NOW)['notification'],'2N')
        for now in [NOW,NOW+timedelta(days=1)]:
            self.assertEqual(admit(self.store,c,event(4),now)['status'],'HALTED_OPERATOR_RESET_REQUIRED')
        _,state=self.store.read();approval={'actor':'fixture-operator','role':'operator','decision_ref':'fixture','expected_sequence':state['sequence']}
        reset(self.store,c,approval,NOW)
        self.assertEqual(admit(self.store,c,event(4),NOW)['count'],1)
        self.assertEqual(admit(self.store,c,event(5),NOW+timedelta(days=1))['count'],1)
        with self.assertRaisesRegex(ValueError,'RESET_STATE_MOVED'):reset(self.store,c,approval,NOW)
    def test_concurrent_requests_one_shared_cross_branch_ceiling(self):
        c=config(4)
        def invoke(i):return admit(GitLedger(self.root),c,event(i,'main' if i%2 else 'astra/autonomous-isles-pilot'),NOW,max_retries=30)
        with ThreadPoolExecutor(max_workers=8) as pool:results=list(pool.map(invoke,range(1,25)))
        self.assertEqual(sum(r['status']=='ADMITTED' for r in results),8)
        _,s=self.store.read();self.assertEqual(s['count'],8);self.assertTrue(s['halted']);self.assertEqual(len(s['notifications']),2)
    def test_crash_after_cas_recovery_no_recharge_and_durable_notice(self):
        class Crash:
            def read(me):return self.store.read()
            def cas(me,old,new):
                ok=self.store.cas(old,new)
                if ok:raise RuntimeError('synthetic lost acknowledgement')
                return ok
        c=config(1)
        with self.assertRaises(RuntimeError):admit(Crash(),c,event(1),NOW)
        r=admit(GitLedger(self.root),c,event(1),NOW)
        self.assertTrue(r['duplicate_admission']);self.assertEqual(r['count'],1);self.assertEqual(r['pending_notifications'],['1:N'])
    def test_unratified_policy_change_corruption_and_retries_fail_closed(self):
        proposed={'status':'PROPOSED','n':None}
        with self.assertRaisesRegex(ValueError,'RATIFICATION'):admit(self.store,proposed,event(1),NOW)
        admit(self.store,config(2),event(1),NOW)
        with self.assertRaisesRegex(ValueError,'POLICY_CHANGE'):admit(self.store,config(4),event(2),NOW)
        with self.assertRaisesRegex(ValueError,'EVENT_IDENTITY'):admit(self.store,config(2),event(2,'results/private'),NOW)
        class Conflict:
            def read(me):return self.store.read()
            def cas(me,*_):return False
        with self.assertRaisesRegex(ValueError,'RETRY_EXHAUSTED'):admit(Conflict(),config(2),event(2),NOW,max_retries=2)
        state=initial();state['payload']='patient payload'
        with self.assertRaisesRegex(ValueError,'SCHEMA'):self.store.cas(self.store.read()[0],state)

    def test_remote_cas_transport_in_disposable_bare_repository(self):
        remote=self.root/'remote.git';subprocess.run(['git','init','-q','--bare',str(remote)],check=True)
        self.assertTrue(GitLedger(remote).cas(None,initial()))
        clients=[]
        for i in range(2):
            p=self.root/('client'+str(i));p.mkdir();subprocess.run(['git','init','-q',str(p)],check=True)
            subprocess.run(['git','-C',str(p),'remote','add','origin',str(remote)],check=True)
            clients.append(GitLedger(p,remote=True))
        old,a=clients[0].read();old2,b=clients[1].read();self.assertEqual(old,old2)
        a['sequence']=1;b['sequence']=2
        self.assertTrue(clients[0].cas(old,a));self.assertFalse(clients[1].cas(old2,b))
        self.assertEqual(clients[1].read()[1]['sequence'],1)
        r=admit(clients[1],config(2),event(1),NOW)
        self.assertEqual(r['count'],1)
        self.assertTrue(admit(clients[0],config(2),event(1),NOW)['duplicate_admission'])

    def test_initialization_requires_operator_and_never_overwrites(self):
        from orchestrator.dispatch_limiter import initialize
        c=config(2)
        with self.assertRaisesRegex(ValueError,'OPERATOR_INITIALIZATION'):
            initialize(self.store,c,{'actor':'agent','role':'agent','decision_ref':'none'})
        approval={'actor':'fixture-operator','role':'operator','decision_ref':'fixture setup'}
        old,_=self.store.read()
        with self.assertRaisesRegex(ValueError,'ALREADY_EXISTS'):initialize(self.store,c,approval)
        self.assertEqual(self.store.read()[0],old)


def test_notice_order_survives_git_json_roundtrip():
    from orchestrator.dispatch_limiter import pending_notifications
    state = initial()
    state['notifications'] = {str(n)+':N': {'threshold':'N','count':1,'day':'2026-09-06'}
                              for n in [2,9,10,48,96,101]}
    recovered = json.loads(json.dumps(state, sort_keys=True))
    assert pending_notifications(recovered) == ['10:N','48:N','96:N','101:N']
