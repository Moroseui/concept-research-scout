"""Root-only ownership tests; isolated temporary directories, no real ledger."""
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from orchestrator.dispatch_limiter import GitLedger

@unittest.skipUnless(os.geteuid()==0, 'requires real root ownership semantics')
class BookkeepingTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name)
        (self.root/'.git/objects').mkdir(parents=True,mode=0o700)
        self.path=self.root/'.git/shallow';self.path.write_bytes(b'old\n')
        self.path.chmod(0o600);os.chown(self.path,0,987)
        self.store=GitLedger(self.root,protected_owner_group=True)
    def tearDown(self):self.tmp.cleanup()
    def replace(self,path=None):
        path=path or self.path
        new=path.with_name(path.name+'.lock');new.write_bytes(b'new\n');new.chmod(0o600);os.chown(new,0,0);new.replace(path)
    def test_atomic_replacement_preserves_prior_group_and_new_contents(self):
        rows=self.store._bookkeeping_before();self.replace();self.store._bookkeeping_after(rows)
        self.assertEqual(self.path.stat().st_gid,987);self.assertEqual(self.path.read_bytes(),b'new\n')
    def test_unchanged_file_never_chowned(self):
        rows=self.store._bookkeeping_before()
        with patch('os.fchown',side_effect=AssertionError('gratuitous chown')):self.store._bookkeeping_after(rows)
    def test_old_wrong_group_is_not_repaired_by_producer(self):
        os.chown(self.path,0,0);rows=self.store._bookkeeping_before();self.replace();self.store._bookkeeping_after(rows)
        self.assertEqual(self.path.stat().st_gid,0)
    def test_symlink_and_hardlink_refused(self):
        other=self.root/'other';other.write_bytes(b'private');self.path.unlink();self.path.symlink_to(other)
        with self.assertRaisesRegex(ValueError,'LAYOUT'):self.store._bookkeeping_before()
        self.path.unlink();os.link(other,self.path)
        with self.assertRaisesRegex(ValueError,'LAYOUT'):self.store._bookkeeping_before()
    def test_writable_or_nonroot_metadata_refused(self):
        self.path.chmod(0o620)
        with self.assertRaisesRegex(ValueError,'LAYOUT'):self.store._bookkeeping_before()
        self.path.chmod(0o600);os.chown(self.path,997,987)
        with self.assertRaisesRegex(ValueError,'LAYOUT'):self.store._bookkeeping_before()
    def test_in_place_group_change_is_not_hidden(self):
        rows=self.store._bookkeeping_before();os.chown(self.path,0,0)
        with self.assertRaisesRegex(ValueError,'UNEXPECTED_GROUP'):self.store._bookkeeping_after(rows)
    def test_unexpected_replacement_group_mode_and_missing_file_refused(self):
        rows=self.store._bookkeeping_before();self.replace();os.chown(self.path,0,123)
        with self.assertRaisesRegex(ValueError,'UNEXPECTED_GROUP'):self.store._bookkeeping_after(rows)
        os.chown(self.path,0,0);self.path.chmod(0o644)
        with self.assertRaisesRegex(ValueError,'METADATA'):self.store._bookkeeping_after(rows)
        self.path.unlink()
        with self.assertRaises(FileNotFoundError):self.store._bookkeeping_after(rows)
    def test_fetch_head_replacement_refused(self):
        p=self.root/'.git/FETCH_HEAD';p.write_bytes(b'old');p.chmod(0o600);os.chown(p,0,987)
        rows=self.store._bookkeeping_before();self.replace(p)
        with self.assertRaisesRegex(ValueError,'UNEXPECTED_REPLACEMENT'):self.store._bookkeeping_after(rows)
    def test_failure_after_atomic_write_preserves_metadata_and_original_error(self):
        def failed(*a,**k):self.replace();raise RuntimeError('observed transport failure')
        with patch('orchestrator.dispatch_limiter.git_run',side_effect=failed):
            with self.assertRaisesRegex(RuntimeError,'observed transport failure'):self.store.git('fetch','origin')
        self.assertEqual(self.path.stat().st_gid,987)
    def test_symlink_parent_refused(self):
        target=self.root/'target';target.mkdir();(self.root/'.git/refs').symlink_to(target,target_is_directory=True)
        with self.assertRaisesRegex(ValueError,'SYMLINK'):self.store._bookkeeping_before()

if __name__=='__main__':unittest.main()
