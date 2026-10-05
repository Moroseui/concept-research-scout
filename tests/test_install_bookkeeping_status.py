"""Native status-call boundary; synthetic broker transport, real root ownership."""
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from contextlib import ExitStack
from orchestrator import install_reviewed_deployment as install

@unittest.skipUnless(os.geteuid()==0, 'requires real root ownership semantics')
class StatusBookkeepingTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name)
        (self.root/'.git/objects').mkdir(parents=True,mode=0o700)
        self.path=self.root/'.git/shallow';self.path.write_text('original\n');self.path.chmod(0o600);os.chown(self.path,0,987)
        self.source='a'*40
        self.broker={'sources':[self.source]}
        self.config={'state':str(install.CONTROLLER),'controller_uid':997,'controller_gid':987,'source':self.source,'source_root':'/fixture/source','broker_socket':'/fixture/socket'}
        self.value={'mode':'LIVE_APPROVED','sequence':202,'pin':'b'*40,'halted':False,'count':7,'day':'2026-09-21'}
    def tearDown(self):self.tmp.cleanup()
    def replacement(self):
        tmp=self.path.with_name('shallow.lock');tmp.write_text('updated\n');tmp.chmod(0o600);os.chown(tmp,0,0);tmp.replace(self.path)
    def invoke(self, transport):
        def read(path):
            if path==install.CONFIG/'controller.json':return json.dumps(self.config).encode()
            if path==install.CONFIG/'broker.json':return json.dumps(self.broker).encode()
            raise AssertionError('Unexpected private read')
        with ExitStack() as stack:
            stack.enter_context(patch.object(install.gate,'read',side_effect=read))
            checked=stack.enter_context(patch.object(install,'checked_source'))
            stack.enter_context(patch.object(install,'_ledger_path',return_value=self.root))
            cmd=stack.enter_context(patch.object(install,'command',side_effect=transport))
            try:return install.authenticated_ledger_status(self.broker)
            finally:
                checked.assert_called_once_with('/fixture/source',self.source)
                if cmd.called:
                    args=cmd.call_args.args[0]
                    self.assertEqual(args[:4],['/usr/sbin/runuser','-u','research-controller','--'])
                    self.assertIn('"status",{}',args[-2]);self.assertEqual(args[-1],'/fixture/socket')
    def test_old_broker_fetch_preserves_owner_and_exact_returned_status(self):
        def transport(*a,**k):self.replacement();return json.dumps(self.value).encode()
        self.assertEqual(self.invoke(transport),self.value);self.assertEqual(self.path.stat().st_gid,987)
        self.assertEqual(self.path.read_text(),'updated\n')
    def test_failed_status_still_preserves_owner_and_propagates_failure(self):
        def transport(*a,**k):self.replacement();raise RuntimeError('status unavailable')
        with self.assertRaisesRegex(RuntimeError,'status unavailable'):self.invoke(transport)
        self.assertEqual(self.path.stat().st_gid,987)
    def test_unexpected_group_is_refused_not_restored(self):
        def transport(*a,**k):self.replacement();os.chown(self.path,0,123);return json.dumps(self.value).encode()
        with self.assertRaisesRegex(ValueError,'UNEXPECTED_GROUP'):self.invoke(transport)
        self.assertEqual(self.path.stat().st_gid,123)
    def test_existing_drift_is_not_repaired(self):
        os.chown(self.path,0,0)
        def transport(*a,**k):self.replacement();return json.dumps(self.value).encode()
        self.assertEqual(self.invoke(transport),self.value);self.assertEqual(self.path.stat().st_gid,0)

if __name__=='__main__':unittest.main()
