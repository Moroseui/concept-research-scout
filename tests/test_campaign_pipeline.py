import json
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch
from orchestrator import campaign_pipeline as p


class PipelineTests(unittest.TestCase):
    def test_system_author_review_repair_artifacts(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);base=root/'campaigns/isles24-pilot';base.mkdir(parents=True)
            (base/'CAMPAIGN.md').write_text('synthetic campaign')
            (root/'docs/operations').mkdir(parents=True)
            for name in ['REMOTE_OPERATING_DIRECTION.md','CLAUDE_REVIEWER_DIRECTIVE.md']:
                (root/'docs/operations'/name).write_text(name+' required human context')
            sc=SimpleNamespace(ROOT=root);seen=[]
            def fake(sc,out,family,stage,body,names):
                seen.append(family)
                self.assertIn('REMOTE_OPERATING_DIRECTION.md required human context',body)
                self.assertIn('CLAUDE_REVIEWER_DIRECTIVE.md required human context',body)
                for name in names:
                    (out/name).write_text(json.dumps({'verdict':'REVISE' if out.name=='round-1' else 'APPROVE','rationale':'synthetic'}) if name=='review.json' else 'Synthetic proposal')
                return {'family_effective':family,'exit_class':'ok','ci':False}
            with patch.object(p,'system_stage',side_effect=fake):
                result=p.execute(sc,'repair','P001','synthetic repair',base/'pipeline/test')
            self.assertEqual(seen,['codex','claude','codex','claude'])
            self.assertEqual(result['status'],'REVIEWED_PROPOSAL_NOT_ADOPTED')
            self.assertIn('docs/operations/CLAUDE_REVIEWER_DIRECTIVE.md',result['input_sha256'])
            self.assertTrue((base/'pipeline/test/round-1/run.proposed.py').exists())
            self.assertFalse((base/'experiments/P001/run.py').exists())

    def test_future_proposal_requires_previous_result(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(FileNotFoundError):p.grounding(Path(d),'P002')


class PredictionAuthoringTests(unittest.TestCase):
    def test_charter_route_proposes_external_adoption_without_changing_runner(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);base=root/'campaigns/isles24-pilot';exp=base/'experiments/P001';exp.mkdir(parents=True)
            (base/'CAMPAIGN.md').write_text('Frozen campaign')
            (root/'docs/operations').mkdir(parents=True)
            for name in ['REMOTE_OPERATING_DIRECTION.md','CLAUDE_REVIEWER_DIRECTIVE.md']:
                (root/'docs/operations'/name).write_text(name+' required human context')
            (exp/'run.py').write_text('# historical externally seeded runner')
            (root/'docs/science').mkdir(parents=True)
            (root/'docs/science/PREDICTION_READINESS_DIRECTION_20260906.md').write_text('Operator prediction goal')
            seen=[]
            def fake(sc,out,family,stage,body,names):
                seen.append(body)
                for name in names:
                    (out/name).write_text(json.dumps({'verdict':'APPROVE','rationale':'Synthetic review fixture'}) if name=='review.json' else 'PROPOSED synthetic charter artifact')
                return {'family_effective':family,'exit_class':'ok','ci':False}
            with patch.object(p,'system_stage',side_effect=fake):
                r=p.execute(SimpleNamespace(ROOT=root),'charter','P001','Draft prospective linkage',base/'pipeline/charter')
            self.assertEqual(r['status'],'REVIEWED_PROPOSAL_NOT_ADOPTED')
            self.assertIn('externally seeded',seen[0]);self.assertIn('Operator prediction goal',seen[0])
            self.assertIn('docs/science/PREDICTION_READINESS_DIRECTION_20260906.md',r['input_sha256'])
            self.assertEqual((exp/'run.py').read_text(),'# historical externally seeded runner')
            self.assertFalse((root/'charters/isles24-prediction/CHARTER.md').exists())
            self.assertEqual(len(list((base/'pipeline/charter/round-1').glob('*.proposed.md'))),4)


def test_missing_operating_context_blocks_before_model(tmp_path):
    base=tmp_path/'campaigns/isles24-pilot';base.mkdir(parents=True)
    (base/'CAMPAIGN.md').write_text('Synthetic campaign')
    import pytest
    with patch.object(p,'system_stage') as stage:
        with pytest.raises(FileNotFoundError,match='REQUIRED_OPERATING_CONTEXT'):
            p.execute(SimpleNamespace(ROOT=tmp_path),'discuss','P001','Question',base/'pipeline/missing')
        stage.assert_not_called()
    assert (base/'pipeline/missing/blocked.json').exists()


def test_direct_pipeline_cannot_overwrite_ratified_selection_with_preview(tmp_path):
    import pytest
    out=tmp_path/'campaigns/isles24-pilot/pipeline/refused'
    with patch.object(p,'grounding',return_value={}), patch('orchestrator.research_context.selected_prediction_context',return_value={'selected':'ratified'}), patch.object(p,'system_stage') as stage:
        with pytest.raises(ValueError,match='RATIFIED_CONTEXT_REFUSES_PROPOSAL_PREVIEW'):
            p.execute(SimpleNamespace(ROOT=tmp_path),'readiness','P001','question',out,proposal='stale')
        stage.assert_not_called()
    assert json.loads((out/'blocked.json').read_text())['reason']=='GROUNDING_FAILED'


def test_hosted_single_round_retains_negative_review_without_hidden_repair(tmp_path):
    import pytest
    out=tmp_path/'campaigns/isles24-pilot/pipeline/one-round'
    calls=[]
    def stage(sc,directory,family,name,body,names):
        calls.append(family)
        for filename in names:
            (directory/filename).write_text(json.dumps({'verdict':'REVISE','rationale':'Needs additional evidence'}) if filename=='review.json' else 'Bounded readiness proposal')
        return {'family_effective':family,'exit_class':'ok','ci':False}
    with patch.object(p,'grounding',return_value={}), patch('orchestrator.research_context.evidence_context',return_value={}):
        with pytest.raises(ValueError,match='revision limit'):
            p.execute(SimpleNamespace(ROOT=tmp_path),'discuss','P001','question',out,max_rounds=1,stage_runner=stage)
    assert calls==['codex','claude']
    assert (out/'round-1/review.json').exists() and (out/'blocked.json').exists()
    assert not (out/'round-2').exists()
    assert json.loads((out/'request.json').read_text())['max_rounds']==1
