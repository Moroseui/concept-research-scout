import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
PATH=Path(__file__).resolve().parents[1]/'scripts/efficiency_review.py'
spec=importlib.util.spec_from_file_location('efficiency',PATH); m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)

class ReviewerTests(unittest.TestCase):
    def test_unknown_is_not_failure_and_input_is_unchanged(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); d=root/'ideas/001'; d.mkdir(parents=True)
            f=d/'stage_provenance.jsonl'; original='{}\n'+json.dumps({'exit_class':'error','duration_s':2})+'\n'; f.write_text(original)
            result=m.review(root)
            self.assertEqual(f.read_text(),original)
            self.assertEqual(result['mode'],'proposal_only')
            self.assertEqual(result['proposals'][0]['supporting_evidence'],{'error':1})
            self.assertTrue(all(p['verification_method'] and p['status']=='PROPOSAL_ONLY' for p in result['proposals']))
