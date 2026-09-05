"""Synthetic command plumbing: fake agent/validator adapters never grant real approval."""
import argparse
import json
from pathlib import Path
import subprocess
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch
from orchestrator import campaign_lifecycle as c
from orchestrator.campaign import sha

class LifecycleTests(unittest.TestCase):
    def test_full_synthetic_command_path(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); exp=root/'campaigns/isles24-pilot/experiments/P001'; exp.mkdir(parents=True)
            base=exp.parents[1]; (base/'colab').mkdir()
            for path,body in [(base/'CAMPAIGN.md','synthetic'),(exp/'SPEC.md','synthetic'),(exp/'run.py','print("synthetic preflight")'),(exp/'review.json','{}'),(root/'AGENTS.toml','')]: path.write_text(body)
            d={'authority':'campaign_delegated_investigator','actor_type':'agent','family':'codex','model':'synthetic adapter','experiment':'P001','campaign_sha256':sha(base/'CAMPAIGN.md'),'spec_sha256':sha(exp/'SPEC.md'),'rationale':'synthetic plumbing only'}
            (exp/'investigator_decision.json').write_text(json.dumps(d))
            policy={'schema_version':1,'required':['summary.json'],'allowed':['summary.json']}
            (exp/'publication.json').write_text(json.dumps(policy))
            (exp/'requirements.txt').write_text('numpy==2.3.3\nnibabel==5.3.2\n')
            (root/'tests').mkdir(); (root/'tests/test_prediction_p001.py').write_text('import unittest\nclass T(unittest.TestCase):\n def test_synthetic(self): self.assertEqual(2+2,4)\n')
            (root/'.gitignore').write_text('__pycache__/\n')
            def git(*args): return subprocess.check_output(['git',*args],cwd=root,stderr=subprocess.PIPE).decode().strip()
            git('init','-q'); git('config','user.name','Synthetic'); git('config','user.email','synthetic@example.invalid'); git('add','.'); git('commit','-qm','synthetic fixture')
            sc=SimpleNamespace(ROOT=root,STATE=root/'ambient-state.json')
            sc.STATE.write_text('{"active_cycle": 1}')
            git('add','ambient-state.json'); git('commit','-qm','synthetic odd ambient cycle')
            sc._require_clean_tree=lambda stage: self.assertEqual(git('status','--porcelain'),'')
            sc._interpret_review_verdict=lambda e:{'verdict':'APPROVE'}
            def agent(prompt,family,stage,log_path):
                work=prompt.parent
                self.assertEqual(json.loads(sc.STATE.read_text())['active_cycle'],0)
                if family=='codex':
                    (work/'interpretation.md').write_text('Synthetic result only. No scientific finding.')
                    (work/'investigator_next_decision.json').write_text(json.dumps({'status':'PROPOSAL_ONLY','rationale':'synthetic test'}))
                else: (work/'interpret_review.md').write_text('Synthetic reviewer adapter, not actual Claude approval.\n```json\n{"verdict":"APPROVE"}\n```')
                log_path.write_text('synthetic console')
                (work/'stage_provenance.jsonl').write_text(json.dumps({'family_effective':family,'exit_class':'ok','ci':False,'synthetic_fixture':True})+'\n')
            sc.run_agent=agent
            bundle=root/'external'; bundle.mkdir(); (bundle/'summary.json').write_text('{"mean":1}')
            # Keep the external return outside the clean Git worktree.
            external=Path(td).with_name(Path(td).name+'-return'); bundle.rename(external)
            self.addCleanup(lambda: __import__('shutil').rmtree(external))
            args=argparse.Namespace(campaign='isles24-pilot',experiment='P001',idea=None,bundle=str(external),private='synthetic-private',console='synthetic-console')
            with patch.object(c,'require_review'),patch.object(c,'load_validator',return_value=SimpleNamespace(verify=lambda *a:{'status':'SYNTHETIC_ADAPTER','file_sha256':c.inventory(external)})):
                for command in ('probe-build','verify-probe','package-colab','validate-bundle','record-result','interpret-build'):
                    args.cmd=command; c.dispatch(sc,args)
                self.assertEqual(json.loads((exp/'interpretation_receipt.json').read_text())['status'],'AGENT_REVIEWED_NOT_HUMAN_RATIFIED')
                self.assertEqual(git('status','--porcelain'),'')
                self.assertEqual(len(git('log','--format=%H').splitlines()),7)
                self.assertEqual(json.loads(sc.STATE.read_text())['active_cycle'],1)
                self.assertFalse(any('HUMAN_APPROVED' in f.name for f in exp.rglob('*')))
                (exp/'run.py').write_text('changed')
                args.cmd='verify-probe'
                with self.assertRaisesRegex(ValueError,'stale'): c.dispatch(sc,args)

    def test_numbered_idea_cannot_take_campaign_route(self):
        with self.assertRaisesRegex(ValueError,'explicit campaign'):
            c.context(Path('.'),argparse.Namespace(campaign='isles24-pilot',experiment='P001',idea=47))
