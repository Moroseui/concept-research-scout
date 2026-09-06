import hashlib
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch
from orchestrator import git_publication as pub
from orchestrator.public_export import summary

class PublicationTests(unittest.TestCase):
    def test_summary_is_validated_before_any_write(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'summary'
            for value in ['sub-stroke'+'0123','ghp_'+'A'*32,'bad\x1boutput']:
                with self.assertRaises(ValueError):summary(value,p)
                self.assertFalse(p.exists())
            summary('Approved aggregate discussion.',p)
            self.assertIn('Approved aggregate',p.read_text())
    def test_complete_history_and_nonpilot_explicit_operation(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);repo=root/'work';remote=root/'remote.git'
            def git(*args):return subprocess.check_output(['git',*args],cwd=repo,text=True).strip()
            repo.mkdir();git('init','-q');git('config','user.name','Synthetic');git('config','user.email','fixture@local.invalid')
            (repo/'README.md').write_text('initial');git('add','.');git('commit','-qm','base');before=git('rev-parse','HEAD')
            subprocess.run(['git','init','-q','--bare',str(remote)],check=True)
            git('remote','add','origin',str(remote));git('push','-q','origin','HEAD:refs/heads/feature/synthetic')
            (repo/'README.md').write_text('reviewed change');git('commit','-qam','change');source=git('rev-parse','HEAD')
            inventory={source+':README.md':hashlib.sha256((repo/'README.md').read_bytes()).hexdigest()}
            req={'source':source,'before':before,'destination':'feature/synthetic','remote':str(remote),'inventory':inventory}
            with self.assertRaisesRegex(ValueError,'AUTHORITY'):pub.publish(repo,req)
            authority={k:req[k] for k in ['source','before','destination','remote']}
            git('config','remote.origin.pushurl',str(root/'wrong.git'))
            r=pub.publish(repo,req,authority);self.assertEqual(r['blob_versions'],1)
            (repo/'secret.txt').write_text('ghp_'+'A'*32);git('add','.');git('commit','-qm','unsafe')
            git('rm','-q','secret.txt');git('commit','-qm','delete before tip')
            with self.assertRaisesRegex(ValueError,'CONTENT_REJECTED'):pub.audit(repo,git('rev-parse','HEAD'),source,{})
            self.assertEqual(git('ls-remote','origin','refs/heads/feature/synthetic').split()[0],source)
    def test_legacy_checkpoint_never_pushes_without_binding(self):
        import scout
        with patch.dict('os.environ',{},clear=True),patch.object(scout,'_git') as raw:
            with self.assertRaisesRegex(SystemExit,'publication refused'):scout._push_checkpoint()
            raw.assert_not_called()

    def test_metadata_and_case_payload_scans(self):
        for suffix in ['.md','.ipynb','.yml','.toml','.sh','.service']:
            with self.assertRaises(ValueError):pub.scan('record'+suffix,('sub-stroke'+'0123').encode())
        for name,data in [('raw.json',b'{"case":"sub-stroke0123"}'),('payload.csv',b'synthetic'),('x.nii.gz',b'synthetic')]:
            with self.assertRaises(ValueError):pub.scan(name,data)
        with self.assertRaisesRegex(ValueError,'COMMIT_METADATA'):
            pub.scan_commit(b'message '+b'ghp_'+b'A'*32)

    def test_scanner_source_and_explicit_public_plan_are_not_private_payloads(self):
        root=Path(__file__).resolve().parents[1]
        for name in ['orchestrator/git_publication.py','orchestrator/human_controls.py','orchestrator/public_export.py','scripts/check_pilot_publication.py','docs/isles-pilot/PRIVATE_COORDINATOR_PLAN.md','docs/isles-pilot/PRIVATE_COORDINATOR_SETUP.fish']:
            pub.scan(name,(root/name).read_bytes())
        for kind in ['', 'RSA ', 'OPENSSH ', 'EC ']:
            with self.assertRaisesRegex(ValueError,'CONTENT_REJECTED'):
                pub.scan('bad.txt',('-----'+'BEGIN '+kind+'PRIVATE KEY-----').encode())

class CreationTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)/'work';self.root.mkdir()
        self.remote=Path(self.tmp.name)/'remote.git'
        self.run_git('init','-q');self.run_git('config','user.name','Synthetic')
        self.run_git('config','user.email','fixture@local.invalid')
        (self.root/'README.md').write_text('public baseline')
        self.run_git('add','.');self.run_git('commit','-qm','baseline')
        self.base=self.run_git('rev-parse','HEAD')
        subprocess.run(['git','init','-q','--bare',str(self.remote)],check=True)
        self.run_git('remote','add','origin',str(self.remote))
        self.run_git('push','-q','origin',self.base+':refs/heads/main')
        (self.root/'README.md').write_text('permitted record')
        self.run_git('commit','-qam','record')
        self.ref='refs/heads/astra/record'

    def run_git(self,*args):
        return subprocess.check_output(['git',*args],cwd=self.root,text=True).strip()

    def request(self):
        source=self.run_git('rev-parse','HEAD');inventory={}
        for commit in self.run_git('rev-list',self.base+'..'+source).splitlines():
            for name in self.run_git('diff-tree','--no-commit-id','--name-only','-r',commit).splitlines():
                if subprocess.run(['git','cat-file','-e',commit+':'+name],cwd=self.root,capture_output=True).returncode==0:
                    data=subprocess.check_output(['git','show',commit+':'+name],cwd=self.root)
                    inventory[commit+':'+name]=hashlib.sha256(data).hexdigest()
        return {'operation':'create','source':source,'audit_baseline':self.base,
                'baseline_ref':'refs/heads/main','destination':'astra/record',
                'remote':str(self.remote),'expected_destination':'absent','inventory':inventory}

    def publish(self,req=None):
        req=self.request() if req is None else req
        return pub.publish(self.root,req,{k:v for k,v in req.items() if k!='inventory'})

    def test_create_and_verify_with_separate_public_baseline(self):
        # A configured pushurl must not redirect this exact-repository operation.
        self.run_git('config','remote.origin.pushurl',str(Path(self.tmp.name)/'wrong.git'))
        r=self.publish()
        self.assertEqual(r['audit_baseline'],self.base)
        self.assertEqual(r['operation'],'create_if_absent')
        self.assertTrue(r['remote_verified'])
        self.assertEqual(self.run_git('ls-remote',str(self.remote),self.ref).split()[0],r['source'])
        with self.assertRaisesRegex(ValueError,'DESTINATION_ALREADY_EXISTS'):self.publish()

    def test_existing_other_tip_is_preserved(self):
        self.run_git('push','-q','origin',self.base+':'+self.ref)
        with self.assertRaisesRegex(ValueError,'DESTINATION_ALREADY_EXISTS'):self.publish()
        self.assertEqual(self.run_git('ls-remote','origin',self.ref).split()[0],self.base)

    def test_concurrent_creation_never_updates_or_claims_success(self):
        for same_source in (False,True):
            with self.subTest(same_source=same_source):
                req=self.request();other=req['source'] if same_source else self.base
                original=pub.git;attempts=[]
                def raced(root,*args,**kw):
                    if args[0]=='push':
                        attempts.append(args)
                        self.run_git('push','-q','origin',other+':'+self.ref)
                    return original(root,*args,**kw)
                with patch.object(pub,'git',side_effect=raced):
                    expected=ValueError if same_source else subprocess.CalledProcessError
                    with self.assertRaises(expected):self.publish(req)
                self.assertEqual(len(attempts),1)
                self.assertIn('--force-with-lease='+self.ref+':',attempts[0])
                self.assertEqual(self.run_git('ls-remote','origin',self.ref).split()[0],other)
                # Dispose only this synthetic fixture ref for the second case.
                subprocess.run(['git','--git-dir='+str(self.remote),'update-ref','-d',self.ref],check=True)

    def test_deleted_unsafe_history_rejected_before_creation(self):
        (self.root/'secret.txt').write_text('ghp_'+'A'*32)
        self.run_git('add','.');self.run_git('commit','-qm','unsafe intermediate')
        self.run_git('rm','-q','secret.txt');self.run_git('commit','-qm','remove')
        with self.assertRaisesRegex(ValueError,'CONTENT_REJECTED'):self.publish()
        self.assertFalse(self.run_git('ls-remote','origin',self.ref))

    def test_operation_inventory_and_baseline_bindings_fail_closed(self):
        req=self.request()
        with self.assertRaisesRegex(ValueError,'AUTHORITY'):pub.publish(self.root,req,{})
        for field,value,error in [('audit_baseline',req['source'],'PUBLIC_AUDIT_BASELINE_CHANGED'),
                                  ('expected_destination',self.base,'EXPECTED_ABSENCE_REQUIRED'),
                                  ('remote',str(self.remote)+'-other','REMOTE_IDENTITY_CHANGED'),
                                  ('destination','../main','INVALID_DESTINATION'),
                                  ('inventory',{},'INVENTORY_MISMATCH')]:
            with self.subTest(field=field):
                bad={**req,field:value}
                with self.assertRaisesRegex(ValueError,error):self.publish(bad)
        self.assertFalse(self.run_git('ls-remote','origin',self.ref))
