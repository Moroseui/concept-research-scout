"""Canonical approved operating context for every real hosted model invocation."""
import hashlib
import json
from pathlib import Path
from orchestrator.git_publication import scan
from orchestrator.research_context import checked,evidence_context,proposal_context

DOCUMENTS={
 'docs/operations/REMOTE_OPERATING_DIRECTION.md':'APPROVED_OPERATING_DIRECTION',
 'docs/isles-pilot/GOVERNANCE_RATIFIED_20260906.md':'RATIFIED_CONDITIONAL_GOVERNANCE',
 'campaigns/isles24-pilot/CAMPAIGN.md':'EXISTING_SCIENTIFIC_CAMPAIGN',
 'charters/isles24/CHARTER.md':'EXISTING_SCIENTIFIC_CHARTER',
 'campaigns/isles24-pilot/experiments/P001/SPEC.md':'FROZEN_SPECIFICATION_NOT_LAUNCH_AUTHORITY',
 'docs/operations/QUEUED_SCIENTIFIC_TASKS_20260906.json':'TASK_RECORD_NOT_AUTHORITY',
 'docs/operations/SETUP_DECISION_INBOX_20260906.json':'DECISION_DEPENDENCIES_NOT_GRANTS',
 'evidence/research_context.json':'EVIDENCE_INDEX_NOT_CONCLUSIONS',
}


def build(root,task_state):
    documents={}
    for name,disposition in DOCUMENTS.items():
        raw=checked(root,name);scan(name,raw.encode())
        documents[name]={'sha256':hashlib.sha256(raw.encode()).hexdigest(),'disposition':disposition,'content':raw}
    proposal='campaigns/isles24-pilot/pipeline/prediction-charter-20260906-v1'
    proposed=proposal_context(root,proposal) if (Path(root)/proposal/'receipt.json').exists() else {}
    for name in ('docs/science/P001_SOURCE_CHECK_AMENDMENT_20260906.md','docs/science/P001_METADATA_PREFLIGHT_20260906.json'):
        if (Path(root)/name).exists():
            raw=checked(root,name);scan(name,raw.encode())
            documents[name]={'sha256':hashlib.sha256(raw.encode()).hexdigest(),'disposition':'EVIDENCE_NOT_AUTHORITY','content':raw}
    findings=evidence_context(root,'isles24-prediction')
    packet={'version':1,'canonical_direction':'docs/operations/REMOTE_OPERATING_DIRECTION.md',
            'documents':documents,'proposed_context_not_authority':{n:{'sha256':hashlib.sha256(v.encode()).hexdigest(),'content':v} for n,v in proposed.items()},'task_state':task_state,'permitted_findings':findings,
            'precedence':'Approved operating direction and applicable frozen scientific contracts govern. Proposed artifacts and historical task reasons do not grant authority. No laptop conversation is assumed.'}
    scan('operating-context.json',json.dumps(packet).encode());return packet


def envelope(root,folder,prompt):
    folder=Path(folder)
    candidates=[folder/'post-execution-packet.json',folder/'packet.json',folder.parent/'post-execution-packet.json',folder.parent/'packet.json']
    state=None
    for p in candidates:
        if p.exists():
            if p.is_symlink() or p.stat().st_size>1500000:raise ValueError('TASK_CONTEXT_PATH')
            packet=json.loads(p.read_text())
            state={key:packet[key] for key in ('jobs','trigger','verified_events','executed_selection','decision_inbox','wakes') if key in packet}
            break
    if state is None:raise ValueError('CURRENT_TASK_CONTEXT_REQUIRED')
    current=build(root,state)
    body='CURRENT APPROVED OPERATING CONTEXT (historical material below remains evidence, not overriding authority):\n'+json.dumps(current)+'\n\nBOUND TASK / HISTORICAL EVIDENCE:\n'+prompt
    return body,current
