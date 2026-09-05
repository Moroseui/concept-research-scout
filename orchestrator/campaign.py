"""Agent-attributed campaign decisions; no human approval marker mutation."""
import hashlib
import json
from pathlib import Path


def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def verify_decision(campaign, spec, decision, review=None, code=None):
    d=json.loads(Path(decision).read_text())
    if d.get('authority')!='campaign_delegated_investigator' or d.get('actor_type')!='agent':
        raise ValueError('decision must identify delegated agent authority')
    allowed={'schema_version','authority','actor_type','family','model','experiment','campaign_sha256','spec_sha256','decision','rationale','human_intervention_minutes','usage_tokens','cost_usd'}
    if set(d)-allowed:
        raise ValueError('agent decision cannot manufacture human approval')
    if d.get('campaign_sha256')!=sha(campaign) or d.get('spec_sha256')!=sha(spec):
        raise ValueError('campaign/specification binding stale')
    if d.get('experiment') not in ('P001','P002','P003'):
        raise ValueError('experiment exceeds campaign envelope')
    if d.get('family') not in ('codex','claude') or not d.get('model') or not d.get('rationale'):
        raise ValueError('decision lacks attributable investigator identity/rationale')
    if review is not None:
        r=json.loads(Path(review).read_text())
        if r.get('actor_type')!='agent' or r.get('family') not in ('codex','claude') or r['family']==d['family']:
            raise ValueError('opposing-family review required')
        if r.get('verdict')!='APPROVE' or r.get('spec_sha256')!=sha(spec) or not code or r.get('code_sha256')!=sha(code):
            raise ValueError('review missing approval or current spec/code bindings')
        from orchestrator.campaign_review import verify_receipt
        exp=Path(spec).resolve().parent
        verify_receipt(exp.parents[3],exp,r)
    return d
