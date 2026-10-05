from test_campaign_delegation import copy_policy
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
from scripts.render_human_workflows import verify, documents, MODEL_CONTEXT, MAIN_CONTEXT_GUARD


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
        for changes in [dict(mode='dispatch'),dict(experiment='P004'),dict(destination='main'),dict(source='main'),dict(key='../bad'),dict(text='sub-'+'stroke9999'),dict(kind='Approved by human')]:
            with self.subTest(changes=changes),self.assertRaises(ValueError):self.req(**changes)

    def test_every_generation_control_traverses_real_pipeline(self):
        for mode in set(pipeline.MODES)-{'interpret','investigate','code_bundle','protocol_proposal'}:
            with self.subTest(mode=mode),tempfile.TemporaryDirectory() as d:
                root=Path(d);base=root/'campaigns/isles24-pilot';base.mkdir(parents=True)
                (base/'CAMPAIGN.md').write_text('Synthetic bounded campaign')
                copy_policy(root)
                (root/'docs/operations').mkdir(parents=True,exist_ok=True)
                for name in ['REMOTE_OPERATING_DIRECTION.md','CLAUDE_REVIEWER_DIRECTIVE.md']:
                    (root/'docs/operations'/name).write_text(name+' synthetic context')
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

    def test_model_secrets_are_only_consumed_by_reviewed_main_environment_job(self):
        docs=documents();reusable=docs['research-control.yml'];jobs=reusable['jobs']
        self.assertNotIn('secrets',reusable['on']['workflow_call'])
        for name in json.loads(h.CONFIG.read_text())['controls']:
            self.assertNotIn('secrets',docs[name+'.yml']['jobs']['control'])
        self.assertEqual(jobs['run']['environment'],'research-models')
        self.assertEqual(jobs['run']['if'],MODEL_CONTEXT)
        self.assertEqual(jobs['run']['needs'],'admission')
        self.assertNotIn('environment',jobs['admission'])
        self.assertNotIn('secrets.',json.dumps(jobs['admission']))
        self.assertEqual(jobs['admission']['permissions'],{'contents':'read','actions':'read'})
        for job in jobs.values():
            review=next(i for i,step in enumerate(job['steps']) if step.get('name')=='Verify recorded adapter review')
            credential_steps=[i for i,step in enumerate(job['steps']) if 'secrets.' in json.dumps(step)]
            self.assertTrue(all(review<i for i in credential_steps))
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);shutil.copytree(h.ROOT/'.github/workflows',root/'.github/workflows')
            path=root/'.github/workflows/research-control.yml'
            path.write_text(path.read_text().replace('environment: research-models','environment: unrestricted'))
            with self.assertRaises(ValueError):verify(root)

    def test_credential_free_context_guard_rejects_nonmain_tags_forks_and_other_events(self):
        import shlex,sys
        command=shlex.split(MAIN_CONTEXT_GUARD);command[0]=sys.executable
        allowed={'GITHUB_REPOSITORY':'Moroseui/concept-research-scout','GITHUB_REF':'refs/heads/main',
                 'GITHUB_EVENT_NAME':'workflow_dispatch'}
        for changes in ({},{'GITHUB_REF':'refs/heads/astra/autonomous-isles-pilot'},
                        {'GITHUB_REF':'refs/tags/main'},{'GITHUB_REPOSITORY':'someone/fork'},
                        {'GITHUB_EVENT_NAME':'pull_request'},{'GITHUB_REF':''}):
            with self.subTest(changes=changes):
                result=subprocess.run(command,env={**os.environ,**allowed,**changes},capture_output=True,text=True,timeout=10)
                self.assertEqual(result.returncode,1 if changes else 0)
                self.assertIn('Use the reviewed main branch controls' if changes else 'Main control context verified',result.stdout)

    def test_result_status_canary_never_enters_model_pipeline(self):
        from orchestrator import actions_runner as runner
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);(root/'campaigns/isles24-pilot/experiments/P001').mkdir(parents=True)
            req=self.req('results-validate','status')
            with patch.object(h,'ROOT',root),patch.object(h.subprocess,'check_output',return_value='a'*40+'\n'),\
                    patch.dict(os.environ,{'SCOUT_CI':'1','GITHUB_REF':'refs/heads/main'}),\
                    patch.object(runner,'identity',return_value={'github_sha':'a'*40}),\
                    patch.object(runner,'reviewed',return_value='synthetic reviewed source'),\
                    patch.object(h,'restore',return_value=False),patch.object(pipeline,'grounding'),\
                    patch.object(pipeline,'execute') as models:
                result=h.execute(req,root/'status-result')
            self.assertEqual(result['status'],'WAITING_FOR_RESULT')
            models.assert_not_called()

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
        import tomllib
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);out=root/'out';out.mkdir();sc=SimpleNamespace(ROOT=root)
            def fake(prompt,family,stage,log_path):
                command=tomllib.loads((sc.ROOT/'AGENTS.toml').read_text())[family]['command']
                model=command[command.index('--model')+1]
                self.assertEqual(model,'gpt-6-astra')
                (sc.ROOT/'answer.md').write_text('Synthetic artifact')
                (sc.ROOT/'transport.json').write_text(json.dumps({'requested_model':model,'model_selection':'explicit_cli_argument'}))
                (sc.ROOT/'stage_provenance.jsonl').write_text(json.dumps({'ci':True,'family_effective':family,'exit_class':'ok','model_requested':model,'model_used':model})+'\n')
            sc.run_agent=fake
            with patch.object(runner,'identity',return_value={'adapter':'github-actions-v1','ci':True}),patch.object(runner,'reviewed',return_value='synthetic fixture'):
                r=runner.system_stage(sc,out,'codex','synthetic','Synthetic prompt',['answer.md'])
            self.assertFalse(hasattr(sc,'STATE'));self.assertEqual(sc.ROOT,root)
            self.assertTrue(r['ci']);self.assertEqual((out/'answer.md').read_text(),'Synthetic artifact')

    def test_transport_pins_actual_cli_and_distinguishes_response_identity(self):
        from scripts import actions_agent as transport
        for family,model in transport.MODELS.items():
            with self.subTest(family=family),tempfile.TemporaryDirectory() as d:
                root=Path(d);private=root/'private';private.mkdir()
                def process(command,**kwargs):
                    self.assertEqual(command[command.index('--model')+1],model)
                    self.assertIn('Supplied synthetic evidence',kwargs['input'])
                    self.assertEqual(kwargs['cwd'],private)
                    answer={'answer.md':'Synthetic artifact'}
                    if family=='codex':
                        (private/'answer.json').write_text(json.dumps(answer))
                        events=[{'type':'turn.completed','usage':{}}]
                    else:
                        events=[{'type':'assistant','message':{'model':model,'content':[]}},
                                {'type':'result','subtype':'success','structured_output':answer,'modelUsage':{}}]
                    return SimpleNamespace(returncode=0,stdout='\n'.join(json.dumps(e) for e in events),stderr='')
                original=Path.cwd()
                try:
                    os.chdir(root)
                    with patch.object(transport.tempfile,'mkdtemp',return_value=str(private)),patch.object(transport.subprocess,'run',side_effect=process):
                        transport.run(family,['answer.md'],'Supplied synthetic evidence',model=model)
                finally:os.chdir(original)
                receipt=json.loads((root/'transport.json').read_text())
                self.assertEqual(receipt['requested_model'],model)
                self.assertEqual(receipt['model_selection'],'explicit_cli_argument')
                self.assertEqual(receipt['response_models'],[model] if family=='claude' else [])
                self.assertEqual((root/'answer.md').read_text(),'Synthetic artifact')

    def test_wrong_model_refused_before_process_or_artifact_acceptance(self):
        from scripts import actions_agent as transport
        from orchestrator import actions_runner as runner
        with patch.object(transport.subprocess,'run') as process:
            with self.assertRaisesRegex(ValueError,'APPROVED_MODEL_REQUIRED'):
                transport.run('codex',['answer.md'],'Synthetic evidence',model='unapproved-model')
            process.assert_not_called()
        for wrong in ('stage','transport'):
            with self.subTest(wrong=wrong),tempfile.TemporaryDirectory() as d:
                root=Path(d);out=root/'out';out.mkdir();sc=SimpleNamespace(ROOT=root)
                def fake(prompt,family,stage,log_path):
                    (sc.ROOT/'answer.md').write_text('Unaccepted synthetic artifact')
                    (sc.ROOT/'transport.json').write_text(json.dumps({'requested_model':'unapproved-model' if wrong=='transport' else 'gpt-6-astra','model_selection':'explicit_cli_argument'}))
                    (sc.ROOT/'stage_provenance.jsonl').write_text(json.dumps({'ci':True,'family_effective':family,'exit_class':'ok','model_requested':'gpt-6-astra','model_used':None if wrong=='stage' else 'gpt-6-astra'})+'\n')
                sc.run_agent=fake
                with patch.object(runner,'identity',return_value={'adapter':'github-actions-v1','ci':True}),patch.object(runner,'reviewed',return_value='synthetic fixture'):
                    with self.assertRaisesRegex(ValueError,'HOSTED_STAGE_RECEIPT_INVALID|HOSTED_MODEL_BINDING_INVALID'):
                        runner.system_stage(sc,out,'codex','synthetic','Synthetic evidence',['answer.md'])
                self.assertFalse((out/'answer.md').exists())

    def test_review_binds_current_shared_policy_and_authority_dependencies(self):
        from orchestrator import actions_runner as runner
        names=runner.reviewed_files()
        self.assertIn('docs/operations/CONTINUING_RESEARCH_AUTHORIZATION_20260911.md',names)
        self.assertIn('docs/COLLABORATOR_RULES.md',names)
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            for name in names:
                target=root/name;target.parent.mkdir(parents=True,exist_ok=True)
                shutil.copyfile(runner.ROOT/name,target)
            prefix=root/'docs/isles-pilot/reviews/human-controls-handover'
            prefix.parent.mkdir(parents=True,exist_ok=True)
            response={'subtype':'success','structured_output':{'verdict':'APPROVE','scope':'human-controls','reviewed_commit':'a'*40}}
            raw=json.dumps(response).encode()
            Path(str(prefix)+'.response.json').write_bytes(raw)
            evidence={'returncode':0,'reviewed_commit':'a'*40,'assistant_message_models':['claude-fable-5'],
                      'response_sha256':hashlib.sha256(raw).hexdigest(),
                      'input_file_sha256':{name:hashlib.sha256((root/name).read_bytes()).hexdigest() for name in names}}
            Path(str(prefix)+'.execution.json').write_text(json.dumps(evidence))
            self.assertEqual(runner.reviewed(root),'a'*40)
            for name in ('orchestrator/scientific_authority.py','orchestrator/scientific_decision.py',
                         'orchestrator/change_requests.py','orchestrator/hosted_context.py',
                         'docs/operations/CONTINUING_RESEARCH_AUTHORIZATION_20260911.md',
                         'orchestrator/handover_runtime.py','orchestrator/handover_coordinator.py',
                         'orchestrator/protected_handover.py','orchestrator/hosted_campaign.py',
                         'orchestrator/hosted_campaign_task.py','orchestrator/hosted_cycle.py',
                         'orchestrator/research_context.py','orchestrator/publication_candidate.py',
                         'orchestrator/protected_writer.py','orchestrator/report_delivery.py',
                         'scripts/pilot_review.py','scripts/prepare_handover_snapshot.py',
                         'deploy/research-system/prepare_live_research.py',
                         'deploy/research-system/install_live_research.py',
                         'deploy/research-system/install_handover_fixture.py',
                         'deploy/research-system/install_live_handover.py',
                         'deploy/research-system/research-system-handover-live.socket'):
                with self.subTest(name=name):
                    path=root/name;original=path.read_bytes();path.write_bytes(original+b'\n')
                    try:
                        with self.assertRaises(ValueError):runner.reviewed(root)
                    finally:path.write_bytes(original)
            for omitted in ('docs/COLLABORATOR_RULES.md','orchestrator/handover_runtime.py',
                            'deploy/research-system/install_live_research.py'):
                expected=evidence['input_file_sha256'].pop(omitted)
                Path(str(prefix)+'.execution.json').write_text(json.dumps(evidence))
                with self.assertRaisesRegex(ValueError,'REVIEW_BINDING_CHANGED'):runner.reviewed(root)
                evidence['input_file_sha256'][omitted]=expected
