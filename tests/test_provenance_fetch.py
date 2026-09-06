import hashlib
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from scripts.fetch_provenance import retrieve
from orchestrator.experiment_registry import _git_show_bytes

class ProvenanceFetchTests(unittest.TestCase):
    def test_exact_missing_object_retrieved_without_branch_history(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);source=root/'source';source.mkdir()
            def git(*args,cwd=source):return subprocess.check_output(['git',*args],cwd=cwd,stderr=subprocess.DEVNULL).decode().strip()
            git('init','-q');git('config','uploadpack.allowFilter','true');git('config','uploadpack.allowReachableSHA1InWant','true');git('config','user.email','fixture@example.test');git('config','user.name','fixture')
            (source/'unrelated.txt').write_text('unrelated payload excluded from provenance retrieval')
            p=source/'ideas/023/HUMAN_APPROVED_PROBE';p.parent.mkdir(parents=True);p.write_text('contract_blob: synthetic\n')
            git('add','.');git('commit','-qm','bound source');pin=git('rev-parse','HEAD')
            other_blob=git('rev-parse',pin+':unrelated.txt')
            p.unlink();(source/'unrelated.txt').unlink();git('add','.');git('commit','-qm','current');head=git('rev-parse','HEAD')
            target=root/'target';git('clone','-q','--depth=1',source.as_uri(),str(target))
            raw,error=_git_show_bytes(target,pin,'ideas/023/HUMAN_APPROVED_PROBE')
            self.assertIsNone(raw);self.assertIn('GIT_OBJECT_UNAVAILABLE',error)
            manifest=root/'manifest.json';manifest.write_text(json.dumps({'version':1,'objects':[{'commit':pin,'path':'ideas/023/HUMAN_APPROVED_PROBE','sha256':hashlib.sha256(b'contract_blob: synthetic\n').hexdigest()}]}))
            with self.assertRaisesRegex(ValueError,'GIT_OBJECT_UNAVAILABLE'):retrieve(target,manifest)
            self.assertTrue(retrieve(target,manifest,True)[0]['fetched'])
            local_objects=git('cat-file','--batch-all-objects','--batch-check=%(objectname)',cwd=target).splitlines()
            self.assertNotIn(other_blob,local_objects)
            self.assertEqual(git('rev-parse','HEAD',cwd=target),head)
            self.assertFalse(retrieve(target,manifest,True)[0]['fetched'])
            raw,error=_git_show_bytes(target,head,'ideas/023/HUMAN_APPROVED_PROBE')
            self.assertIn('GIT_PATH_UNAVAILABLE',error)
    def test_rejects_branch_name_and_wrong_artifact(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'m.json';p.write_text(json.dumps({'version':1,'objects':[{'commit':'main','path':'ideas/023/HUMAN_APPROVED_PROBE','sha256':'0'*64}]}))
            with self.assertRaises(ValueError):retrieve(d,p,True)

    def test_terminal_path_boundary_and_malformed_summary(self):
        from unittest.mock import patch
        import orchestrator.experiment_registry as er
        registry={'probes':[{'results_bundle':'results/047','terminal_statuses':['DONE']}]}
        with patch.object(er,'_load',return_value=(registry,None)),patch.object(er,'validate',return_value=[]),patch.object(er,'approved_registry_sha',return_value='same'),patch.object(er,'registry_sha',return_value='same'):
            self.assertIsNone(er.terminal_statuses_if_approved('047','.', 'myresults/047'))
            self.assertEqual(er.terminal_statuses_if_approved('047','.', '/repo/results/047'),['DONE'])
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'bundle';p.mkdir();(p/'summary.json').write_text('[]')
            self.assertEqual(er._bundle_summary(Path(d),'bundle'),{'status':'UNPARSEABLE'})
