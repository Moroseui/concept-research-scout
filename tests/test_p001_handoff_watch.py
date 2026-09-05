import unittest
import tempfile
from pathlib import Path
from unittest.mock import patch
from scripts import p001_handoff_watch as watch
from scripts.p001_handoff_watch import follow


class HandoffTests(unittest.TestCase):
    def test_main_writes_distinct_receipts_and_refuses_rerun(self):
        with tempfile.TemporaryDirectory() as d, patch.object(watch,'approval'), \
             patch.object(watch.time,'sleep'), \
             patch.object(watch.acquisition,'run',side_effect=[
                 {'status':'COMPLETE','remote':{'status':'RUNNING'}},
                 {'status':'COMPLETE','remote':{'status':'VALIDATED'}}]), \
             patch.object(watch.patient,'execution_packet',return_value={}), \
             patch.object(watch.patient,'worker',side_effect=[
                 {'status':'COMPLETE','job_status':'DISPATCHED_NOT_YET_VALIDATED'},
                 {'status':'COMPLETE','job_status':'VALIDATED'}]):
            destination=Path(d)/'controller'
            watch.main(destination)
            self.assertEqual(len(list(destination.glob('event-*.json'))),4)
            self.assertTrue((destination/'outcome.json').is_file())
            with self.assertRaises(FileExistsError):watch.main(destination)

    def test_only_validated_acquisition_dispatches_once(self):
        observations=iter(['RUNNING','VALIDATED']);dispatched=[];events=[]
        def dispatch():
            dispatched.append(True)
            return {'status':'COMPLETE','job_status':'DISPATCHED_NOT_YET_VALIDATED'}
        result=follow(lambda:{'status':'COMPLETE','remote':{'status':next(observations)}},
            dispatch,lambda:{'status':'COMPLETE','job_status':'VALIDATED'},
            lambda stage,value:events.append(stage),lambda:None)
        self.assertEqual(result,'NEEDS_PRIVATE_RETURN_TRANSFER')
        self.assertEqual(dispatched,[True])
        self.assertEqual(events,['acquisition','acquisition','dispatch','patient'])

    def test_failure_and_unknown_state_never_dispatch(self):
        for state in ['FAILED','NOT_VISIBLE','unknown']:
            result=follow(lambda:{'status':'COMPLETE','remote':{'status':state}},
                lambda:self.fail('must not dispatch'),lambda:self.fail('must not poll patient'),
                lambda *args:None,lambda:None)
            self.assertEqual(result,'ACQUISITION_STOPPED')

    def test_dispatch_failure_no_retry(self):
        result=follow(lambda:{'status':'COMPLETE','remote':{'status':'VALIDATED'}},
            lambda:{'status':'FAILED'},lambda:self.fail('must not poll'),lambda *args:None,lambda:None)
        self.assertEqual(result,'DISPATCH_BLOCKED')
