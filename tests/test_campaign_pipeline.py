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
            sc=SimpleNamespace(ROOT=root);seen=[]
            def fake(sc,out,family,stage,body,names):
                seen.append(family)
                for name in names:
                    (out/name).write_text(json.dumps({'verdict':'REVISE' if out.name=='round-1' else 'APPROVE','rationale':'synthetic'}) if name=='review.json' else 'Synthetic proposal')
                return {'family_effective':family,'exit_class':'ok','ci':False}
            with patch.object(p,'system_stage',side_effect=fake):
                result=p.execute(sc,'repair','P001','synthetic repair',base/'pipeline/test')
            self.assertEqual(seen,['codex','claude','codex','claude'])
            self.assertEqual(result['status'],'REVIEWED_PROPOSAL_NOT_ADOPTED')
            self.assertTrue((base/'pipeline/test/round-1/run.proposed.py').exists())
            self.assertFalse((base/'experiments/P001/run.py').exists())

    def test_future_proposal_requires_previous_result(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(FileNotFoundError):p.grounding(Path(d),'P002')
