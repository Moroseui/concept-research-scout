import concurrent.futures
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import time
import unittest
from orchestrator.remote_supervisor import Controller,worker,PAYLOAD,SMOKE

class RemoteTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.base=Path(self.tmp.name);self.repo=self.base/'source';self.repo.mkdir()
        target=self.repo/SMOKE;target.parent.mkdir(parents=True);shutil.copyfile(Path(__file__).resolve().parents[1]/SMOKE,target)
        def git(*a):return subprocess.check_output(['git',*a],cwd=self.repo,text=True).strip()
        git('init','-q');git('config','user.name','Synthetic');git('config','user.email','synthetic@local.invalid');git('add','.');git('commit','-qm','frozen synthetic')
        self.pin=git('rev-parse','HEAD')
        self.state=self.base/'state';self.req=self.base/'requests';self.out=self.base/'outputs'
        for p in [self.state,self.req,self.out]:p.mkdir()
        self.s=Controller(self.state/'jobs.sqlite')
    def tick(self):self.s.tick(self.state,self.req,self.out,self.repo,self.pin)
    def work(self):return worker(self.req,self.out,self.repo,self.pin)
    def test_real_execution_separate_retrieval_duplicate_and_restart(self):
        self.s.submit('job',self.pin);self.tick();self.work()
        self.s.db.close();self.s=Controller(self.state/'jobs.sqlite')
        self.tick();self.tick()
        d=self.s.status();self.assertEqual(d['jobs'][0]['status'],'COMPLETE')
        self.assertEqual(len(d['wakes']),1);self.assertEqual(d['wakes'][0]['status'],'PENDING_AUTH')
        self.assertEqual(self.s.db.execute('SELECT count(*) FROM events').fetchone()[0],1)
        self.assertIsNone(self.work())
        self.assertEqual(next(self.out.glob('*/synthetic-result.txt')).read_bytes(),PAYLOAD)
        self.assertEqual(len(list(self.out.glob('*/console-*.stdout'))),2)
    def test_blocked_backend_and_failed_job_yield_to_independent_work(self):
        self.s.submit('a',self.pin,backend='colab');self.s.submit('b',self.pin,kind='synthetic_failure');self.s.submit('c',self.pin)
        self.tick();self.work();self.tick();self.work();self.tick()
        self.assertEqual([j['status'] for j in self.s.status()['jobs']],['BLOCKED','FAILED','COMPLETE'])
        self.assertEqual(len(self.s.status()['wakes']),2)
    def test_lost_request_recovered_without_duplicate_dispatch(self):
        self.s.submit('job',self.pin);self.tick();p=next(self.req.glob('*.json'));raw=p.read_bytes();p.unlink()
        self.tick();self.assertEqual(p.read_bytes(),raw)
        self.work();self.tick();self.assertEqual(self.s.status()['jobs'][0]['status'],'COMPLETE')
    def test_uncertain_attempt_is_blocked_not_retried(self):
        self.s.submit('job',self.pin);self.tick()
        self.s.tick(self.state,self.req,self.out,self.repo,self.pin,now=time.time()+1000)
        self.assertEqual(self.s.status()['jobs'][0]['status'],'BLOCKED')
        self.tick();self.assertEqual(len(list(self.req.glob('*.json'))),1)
    def test_parallel_ticks_only_one_active_job_and_tamper_refused(self):
        self.s.submit('a',self.pin);self.s.submit('b',self.pin)
        def tick(_):
            s=Controller(self.state/'jobs.sqlite');s.tick(self.state,self.req,self.out,self.repo,self.pin);s.db.close()
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:list(pool.map(tick,range(4)))
        self.assertEqual(len(list(self.req.glob('*.json'))),1)
        self.work();next(self.out.glob('*/synthetic-result.txt')).write_bytes(b'tampered')
        self.tick();self.assertEqual(self.s.status()['jobs'][0]['status'],'BLOCKED')
        self.work();self.tick();self.assertEqual(self.s.status()['jobs'][1]['status'],'COMPLETE')
    def test_no_arbitrary_patient_job_or_changed_binding(self):
        for kind in ['P001','shell','patient']:
            with self.assertRaises(ValueError):self.s.submit('job',self.pin,kind=kind)
        self.s.submit('job',self.pin)
        with self.assertRaises(ValueError):self.s.submit('job',self.pin,kind='synthetic_failure')
    def test_consistent_original_evidence_backup_restore(self):
        from orchestrator.operations_backup import backup,restore
        self.s.submit('job',self.pin);self.tick();self.work();self.tick()
        receipt=backup(self.state,self.out,self.base/'backup')
        result=restore(self.base/'backup',self.base/'restored')
        self.assertTrue(result['restored']);self.assertEqual(result['events'],1)
        self.assertFalse(receipt['provider_recovery_proven'])
        p=next((self.base/'backup').glob('outputs/*/synthetic-result.txt'));p.write_bytes(b'changed')
        with self.assertRaisesRegex(ValueError,'IDENTITY'):restore(self.base/'backup',self.base/'bad')
    def test_deployed_worker_boundary_is_separate_and_credential_free(self):
        import configparser
        base=Path(__file__).resolve().parents[1]/'deploy/research-system'
        config=configparser.ConfigParser(interpolation=None)
        config.read(base/'research-system-worker.service');s=config['Service']
        self.assertEqual(s['User'],'research-worker');self.assertEqual(s['PrivateNetwork'],'true')
        self.assertEqual(s['NoNewPrivileges'],'true');self.assertEqual(s['ProtectHome'],'true')
        self.assertEqual(s['ReadWritePaths'],'/var/lib/research-system/outputs')
        self.assertNotIn('sudo',s['ExecStart']);self.assertEqual(s['KillMode'],'control-group')
    def test_real_child_execution_does_not_inherit_model_or_git_environment(self):
        import os
        from unittest.mock import patch
        from orchestrator import remote_supervisor as module
        original=module.subprocess.run;environments=[]
        def observe(*a,**kw):
            if 'env' in kw:environments.append(kw['env'])
            return original(*a,**kw)
        self.s.submit('job',self.pin);self.tick()
        with patch.dict(os.environ,{'GH_TOKEN':'synthetic-canary','OPENAI_API_KEY':'synthetic-canary'}),patch.object(module.subprocess,'run',side_effect=observe):self.work()
        self.assertEqual(len(environments),2)
        for env in environments:
            self.assertNotIn('GH_TOKEN',env);self.assertNotIn('OPENAI_API_KEY',env)
        self.tick();self.assertEqual(self.s.status()['jobs'][0]['status'],'COMPLETE')

    def test_late_valid_outcome_resolves_only_ambiguity(self):
        self.s.submit('job',self.pin);self.tick();self.work()
        p=next(self.out.glob('*/outcome.json'));raw=p.read_bytes();p.unlink()
        self.s.tick(self.state,self.req,self.out,self.repo,self.pin,now=time.time()+1000)
        self.assertEqual(self.s.status()['jobs'][0]['status'],'BLOCKED')
        p.write_bytes(raw);self.tick()
        self.assertEqual(self.s.status()['jobs'][0]['status'],'COMPLETE')
        self.assertIsNone(self.s.status()['jobs'][0]['reason'])
        self.assertEqual(self.s.inbox()[0]['status'],'RESOLVED')
    def test_invalid_request_does_not_block_valid_request(self):
        self.s.submit('job',self.pin);self.tick()
        (self.req/'000-invalid.json').write_text('{}')
        self.work();self.tick()
        self.assertEqual(self.s.status()['jobs'][0]['status'],'COMPLETE')
        self.assertEqual(len(list((self.out/'rejected-requests').glob('*.json'))),1)
    def test_failed_receipt_cannot_claim_retrieval(self):
        from orchestrator.remote_supervisor import validate_receipt
        self.s.submit('job',self.pin,kind='synthetic_failure');self.tick();r=self.work()
        req=json.loads(next(self.req.glob('*.json')).read_text())
        for key,value in [('artifact_sha256','a'*64),('separate_retrieval',True)]:
            with self.assertRaisesRegex(ValueError,'FAILED_RESULT_FIELDS'):validate_receipt({**r,key:value},req)
    def test_nested_backup_manifest_is_verified(self):
        from orchestrator.operations_backup import backup,restore
        self.s.submit('job',self.pin);self.tick();self.work();self.tick()
        folder=next(p for p in self.out.iterdir() if p.is_dir())
        (folder/'manifest.json').write_text('original nested manifest')
        backup(self.state,self.out,self.base/'backup')
        next((self.base/'backup').glob('outputs/*/manifest.json')).write_text('changed')
        with self.assertRaisesRegex(ValueError,'IDENTITY'):restore(self.base/'backup',self.base/'restored')
