import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from orchestrator.campaign import verify_decision

class CampaignTests(unittest.TestCase):
    def test_agent_identity_stale_spec_and_opposing_review(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)
            for n in ('campaign','spec','code'): (p/n).write_text(n)
            sha=lambda n:hashlib.sha256((p/n).read_bytes()).hexdigest()
            d={'authority':'campaign_delegated_investigator','actor_type':'agent','campaign_sha256':sha('campaign'),'spec_sha256':sha('spec'),'experiment':'P001','family':'codex','model':'fixture','rationale':'fixture'}
            (p/'decision').write_text(json.dumps(d))
            verify_decision(p/'campaign',p/'spec',p/'decision')
            r={'actor_type':'agent','family':'codex','verdict':'APPROVE','spec_sha256':sha('spec'),'code_sha256':sha('code')}
            (p/'review').write_text(json.dumps(r))
            with self.assertRaisesRegex(ValueError,'opposing'): verify_decision(p/'campaign',p/'spec',p/'decision',p/'review',p/'code')
            r['family']='claude'; (p/'review').write_text(json.dumps(r))
            verify_decision(p/'campaign',p/'spec',p/'decision',p/'review',p/'code')
            (p/'spec').write_text('amended after results')
            with self.assertRaisesRegex(ValueError,'stale'): verify_decision(p/'campaign',p/'spec',p/'decision')
            (p/'spec').write_text('spec'); d['human_approved']=True; (p/'decision').write_text(json.dumps(d))
            with self.assertRaisesRegex(ValueError,'manufacture'): verify_decision(p/'campaign',p/'spec',p/'decision')
