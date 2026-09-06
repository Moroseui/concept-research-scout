import tempfile
import unittest
from pathlib import Path
from orchestrator.job_store import Store


class JobTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.path=Path(self.tmp.name)/'jobs.db';self.s=Store(self.path);self.s.register('P001',{'pin':'synthetic'})

    def finish(self,event,result,now):
        self.s.complete_event('P001',event,result,now,lease=self.s.get('P001')['lease'])

    def test_recovery_deduplication_and_transfer_inbox(self):
        self.s.claim('P001',0);self.finish('a','VALIDATED',1)
        self.finish('a','VALIDATED',1)
        with self.assertRaises(ValueError):self.s.complete_event('P001','a','FAILED',1)
        self.s=Store(self.path)
        self.s.claim('P001',2);self.finish('b','DISPATCHED',3)
        self.s.claim('P001',4);self.finish('c','VALIDATED',5)
        self.assertEqual(self.s.inbox()[0]['reason'],'PRIVATE_RETURN_TRANSFER_REQUIRED')

    def test_unknown_dispatch_never_retried(self):
        self.s.claim('P001',0);self.finish('a','VALIDATED',1)
        self.s.claim('P001',2)
        self.assertIsNone(Store(self.path).claim('P001',1000))
        self.assertEqual(self.s.get('P001')['status'],'BLOCKED')

    def test_read_only_retry_cap_and_binding(self):
        with self.assertRaises(ValueError):self.s.register('P001',{'pin':'changed'})
        for n in range(3):
            self.s.claim('P001',n*1000);self.finish(str(n),'TRANSIENT',n*1000)
        self.assertEqual(self.s.get('P001')['status'],'BLOCKED')
        self.assertIsNone(self.s.claim('P001',99999))

    def test_late_completion_rejected_after_recovery(self):
        old=self.s.claim('P001',0)
        self.s.claim('P001',1000)
        with self.assertRaises(ValueError):self.s.complete_event('P001','late','VALIDATED',1001,lease=old['lease'])
