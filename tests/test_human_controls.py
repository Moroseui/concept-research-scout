import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from types import SimpleNamespace
from unittest.mock import patch
import urllib.request
from orchestrator import human_controls as h, campaign_pipeline as pipeline
from orchestrator.actions_runner import identity
from scripts.actions_agent import decode
from scripts.render_human_workflows import verify, documents


class HumanControlsTests(unittest.TestCase):
    def req(self,control='confer',mode='',**changes):
        args=dict(control=control,mode=mode,experiment='P001',text='Summarize evidence.',source='a'*40,destination='actions-artifact',key='acceptance',kind='human');args.update(changes)
        return h.request(**args)

    def test_routes_invalid_inputs_and_stable_identity(self):
        cfg=json.loads(h.CONFIG.read_text())
        for name,control in cfg['controls'].items():
            for mode in control['modes']:self.assertEqual(self.req(name,mode)['mode'],mode)
        self.assertEqual(self.req()['identity'],self.req()['identity'])
        self.assertNotEqual(self.req()['identity'],self.req(key='another')['identity'])
        for changes in [dict(mode='dispatch'),dict(experiment='P004'),dict(destination='main'),dict(source='main'),dict(key='../bad'),dict(text='sub-stroke9999'),dict(kind='Approved by human')]:
            with self.subTest(changes=changes),self.assertRaises(ValueError):self.req(**changes)

    def test_every_generation_control_traverses_real_pipeline(self):
        for mode in set(pipeline.MODES)-{'interpret'}:
            with self.subTest(mode=mode),tempfile.TemporaryDirectory() as d:
                root=Path(d);base=root/'campaigns/isles24-pilot';base.mkdir(parents=True)
                (base/'CAMPAIGN.md').write_text('Synthetic bounded campaign')
                sc=SimpleNamespace(ROOT=root);seen=[]
                def stage(sc,out,family,name,body,names):
                    seen.append(family)
                    for n in names:(out/n).write_text(json.dumps({'verdict':'APPROVE','rationale':'Synthetic review'}) if n=='review.json' else 'Synthetic system artifact')
                    return {'ci':True,'family_effective':family,'exit_class':'ok','runner':{'adapter':'github-actions-v1'}}
                with patch.dict(os.environ,{'SCOUT_CI':'1'}),patch.object(pipeline,'system_stage',side_effect=stage):
                    r=pipeline.execute(sc,mode,'P001','Synthetic question',base/'pipeline/run',initiator={'kind':'human'})
                self.assertEqual(seen,['codex','claude']);self.assertTrue(r['ci']);self.assertEqual(r['initiator']['kind'],'human')
                self.assertEqual(r['status'],'REVIEWED_PROPOSAL_NOT_ADOPTED')

    def test_ci_receipt_cannot_be_disguised_as_local(self):
        with self.assertRaises(ValueError),patch.dict(os.environ,{'SCOUT_CI':'1','GITHUB_ACTIONS':''}):identity()

    def test_export_integrity_and_unknown_file_refusal(self):
        with tempfile.TemporaryDirectory() as d:
            out=Path(d);r=self.req()
            h.save(out,r,'REVIEWED_PROPOSAL','Synthetic answer','Review it.',{'review':'Synthetic fixture'})
            self.assertEqual(h.validate_export(out)['status'],'REVIEWED_PROPOSAL')
            (out/'raw.csv').write_text('synthetic')
            with self.assertRaises(ValueError):h.validate_export(out)
            (out/'raw.csv').unlink();(out/'RESULT.md').write_text('changed')
            with self.assertRaises(ValueError):h.validate_export(out)

    def test_redirect_does_not_forward_auth_to_artifact_storage(self):
        req=urllib.request.Request('https://api.github.com/a',headers={'Authorization':'Bearer synthetic'})
        redirected=h.PrivateRedirect().redirect_request(req,None,302,'',{},'https://storage.example.test/a')
        self.assertFalse(redirected.has_header('Authorization'))

    def test_structured_outputs_cannot_write_arbitrary_paths(self):
        self.assertEqual(decode({'answer.md':'Synthetic'},['answer.md']),{'answer.md':'Synthetic'})
        for response,names in [({'../x':'bad'},['../x']),({'answer.md':'good','extra':'bad'},['answer.md']),({'answer.md':''},['answer.md'])]:
            with self.assertRaises(ValueError):decode(response,names)

    def test_workflows_are_reviewed_shared_wiring(self):
        self.assertEqual(verify(h.ROOT)['destination'],'actions-artifact')
        docs=documents()
        for name in json.loads(h.CONFIG.read_text())['controls']:
            job=docs[name+'.yml']['jobs']['control']
            self.assertEqual(job['uses'],'./.github/workflows/research-control.yml')
            self.assertEqual(job['with']['control'],name)
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);shutil.copytree(h.ROOT/'.github/workflows',root/'.github/workflows')
            p=root/'.github/workflows/confer.yml';p.write_text(p.read_text().replace('contents: read','contents: write'))
            with self.assertRaises(ValueError):verify(root)

    def test_repeated_submission_restores_verified_result_without_models(self):
        import io,zipfile
        req=self.req()
        with tempfile.TemporaryDirectory() as d:
            original=Path(d)/'original';original.mkdir()
            h.save(original,req,'REVIEWED_PROPOSAL','Synthetic answer','Review.',{'original':'Synthetic review'})
            buffer=io.BytesIO()
            with zipfile.ZipFile(buffer,'w') as z:
                for p in original.iterdir():z.writestr(p.name,p.read_bytes())
            artifact={'id':42,'expired':False,'name':'human-control-'+req['identity'],'size_in_bytes':len(buffer.getvalue()),'workflow_run':{'id':11}}
            run={'id':11,'head_sha':req['source'],'event':'workflow_dispatch','status':'completed','path':'.github/workflows/confer.yml'}
            for tamper in [False,True]:
                out=Path(d)/str(tamper);out.mkdir()
                r=dict(run,head_sha='b'*40) if tamper else run
                with patch.dict(os.environ,{'GH_TOKEN':'synthetic','GITHUB_REPOSITORY':'fixture/repo','GITHUB_RUN_ID':'12'}),patch.object(h,'api',side_effect=[{'artifacts':[artifact]},r]),patch('urllib.request.build_opener') as opener:
                    opener.return_value.open.return_value=io.BytesIO(buffer.getvalue())
                    restored=h.restore(req,out)
                self.assertEqual(restored,not tamper)
                if restored:
                    receipt=h.validate_export(out)
                    self.assertEqual(receipt['model_calls_this_submission'],0)
                    self.assertEqual(receipt['submission_run_id'],'12')

    def test_interpretation_requires_real_import_before_any_agent(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);base=root/'campaigns/isles24-pilot';base.mkdir(parents=True)
            with patch.object(pipeline,'system_stage') as stage:
                with self.assertRaisesRegex(ValueError,'RESULT_IMPORT_REQUIRED'):
                    pipeline.execute(SimpleNamespace(ROOT=root),'interpret','P001','Explain result',base/'pipeline/missing')
            stage.assert_not_called()
            self.assertTrue((base/'pipeline/missing/blocked.json').exists())

    def test_interpretation_uses_same_review_pipeline_after_import(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);exp=root/'campaigns/isles24-pilot/experiments/P001';exp.mkdir(parents=True)
            (exp/'import_receipt.json').write_text('{}')
            def stage(sc,out,family,name,body,names):
                for n in names:
                    value=json.dumps({'verdict':'APPROVE','rationale':'Synthetic review'}) if n=='review.json' else json.dumps({'status':'PROPOSAL_ONLY','rationale':'Synthetic next decision'}) if n.endswith('.json') else 'Synthetic aggregate interpretation'
                    (out/n).write_text(value)
                return {'ci':False,'family_effective':family,'exit_class':'ok'}
            with patch.object(pipeline,'grounding',return_value={'synthetic_aggregate':'fixture only'}),patch('orchestrator.campaign_lifecycle.require_review'),patch.object(pipeline,'system_stage',side_effect=stage),patch.dict(os.environ,{'SCOUT_CI':''}):
                r=pipeline.execute(SimpleNamespace(ROOT=root),'interpret','P001','Explain result',exp.parents[1]/'pipeline/synthetic-interpret')
            self.assertEqual(r['status'],'REVIEWED_PROPOSAL_NOT_ADOPTED')
            self.assertFalse((exp/'interpretation_receipt.json').exists())

    def test_incomplete_replay_lookup_blocks_before_new_execution(self):
        with tempfile.TemporaryDirectory() as d,patch.dict(os.environ,{'GH_TOKEN':'synthetic','GITHUB_REPOSITORY':'fixture/repo'}),patch.object(h,'api',return_value={'artifacts':[],'total_count':101}):
            with self.assertRaisesRegex(ValueError,'REPLAY_LOOKUP_LIMIT'):h.restore(self.req(),Path(d))

    def test_hosted_stage_restores_absent_state_and_preserves_ci(self):
        from orchestrator import actions_runner as runner
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);out=root/'out';out.mkdir();sc=SimpleNamespace(ROOT=root)
            def fake(prompt,family,stage,log_path):
                (sc.ROOT/'answer.md').write_text('Synthetic artifact')
                (sc.ROOT/'transport.json').write_text('{}')
                (sc.ROOT/'stage_provenance.jsonl').write_text(json.dumps({'ci':True,'family_effective':family,'exit_class':'ok'})+'\n')
            sc.run_agent=fake
            with patch.object(runner,'identity',return_value={'adapter':'github-actions-v1','ci':True}),patch.object(runner,'reviewed',return_value='synthetic fixture'):
                r=runner.system_stage(sc,out,'codex','synthetic','Synthetic prompt',['answer.md'])
            self.assertFalse(hasattr(sc,'STATE'));self.assertEqual(sc.ROOT,root)
            self.assertTrue(r['ci']);self.assertEqual((out/'answer.md').read_text(),'Synthetic artifact')
