"""Synthetic evidence parser fixtures, never production review receipts."""
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from orchestrator import campaign_review as r
from orchestrator.campaign import sha

class ReviewTests(unittest.TestCase):
    def test_incomplete_revised_and_stale_dependency_refused(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); docs=root/'docs/isles-pilot/reviews'; docs.mkdir(parents=True)
            exp=root/'campaigns/isles24-pilot/experiments/P001'; exp.mkdir(parents=True)
            for f in ('SPEC.md','run.py','investigator_decision.json'): (exp/f).write_text('SYNTHETIC FIXTURE')
            src=root/'dependency.py'; src.write_text('fixture v1')
            response=docs/'synthetic.response.json'; execution=docs/'synthetic.execution.json'
            obj={'subtype':'success','is_error':False,'modelUsage':{'claude-fable-5':{}},'result':json.dumps({'verdict':'APPROVE','scope':'p001','reviewed_commit':'synthetic','blocking_findings':[]})}
            def save():
                response.write_text(json.dumps(obj)); execution.write_text(json.dumps({'returncode':0,'reviewed_commit':'synthetic','response_sha256':sha(response),'input_file_sha256':{'dependency.py':sha(src)}}))
            save()
            with patch.object(r,'required_files',return_value={'dependency.py'}):
                receipt=r.make_receipt(root,exp,execution,response); r.verify_receipt(root,exp,receipt)
                src.write_text('fixture changed')
                with self.assertRaisesRegex(ValueError,'dependency'): r.verify_receipt(root,exp,receipt)
                src.write_text('fixture v1'); obj['is_error']=True; save()
                with self.assertRaisesRegex(ValueError,'incomplete'): r.make_receipt(root,exp,execution,response)
                obj['is_error']=False; obj['result']=obj['result'].replace('APPROVE','REVISE'); save()
                with self.assertRaisesRegex(ValueError,'approval'): r.make_receipt(root,exp,execution,response)

    def test_ambiguous_review_is_not_approval(self):
        obj={'verdict':'APPROVE','scope':'p001','reviewed_commit':'synthetic','blocking_findings':[]}
        response={'subtype':'success','is_error':False,'result':json.dumps(obj)+'\n'+json.dumps(obj)}
        with self.assertRaisesRegex(ValueError,'ambiguous'): r.verdict(response)
