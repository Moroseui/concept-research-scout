"""Agent-attributed campaign decisions; no human approval marker mutation."""
import hashlib
import json
from pathlib import Path


def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def verify_decision(campaign, spec, decision, review=None, code=None):
    d=json.loads(Path(decision).read_text())
    if d.get('authority')!='campaign_delegated_investigator' or d.get('actor_type')!='agent':
        raise ValueError('decision must identify delegated agent authority')
    if d.get('human_approved') is not None or d.get('approved_by_human') is not None:
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
    return d
