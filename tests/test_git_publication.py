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
        for name,data in [('raw.json',b'{"case":"sub-stroke0123"}'),('payload.csv',b'synthetic'),('x.nii.gz',b'synthetic')]:
            with self.assertRaises(ValueError):pub.scan(name,data)
        with self.assertRaisesRegex(ValueError,'COMMIT_METADATA'):
            pub.scan_commit(b'message '+b'ghp_'+b'A'*32)
