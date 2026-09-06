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
                (root/'docs/operations'/name).write_text('Human usability and maintenance are required')
            sc=SimpleNamespace(ROOT=root);seen=[]
            def fake(sc,out,family,stage,body,names):
                seen.append(family)
                self.assertIn('Human usability and maintenance are required',body)
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
