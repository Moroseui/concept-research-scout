"""Canonical approved operating context for every real hosted model invocation."""
import hashlib
import json
import re
from pathlib import Path
from orchestrator.git_publication import scan
from orchestrator.research_context import checked,evidence_context,proposal_context,selected_prediction_context

DOCUMENTS={
 'docs/operations/CLAUDE_REVIEWER_DIRECTIVE.md':'OPERATOR_REVIEWER_DIRECTIVE',
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
    selected=selected_prediction_context(root)
    if selected:
        proposed={}
        documents['charters/isles24/CHARTER.md']['disposition']='HISTORICAL_CHARTER_PRESERVED_PREDICTION_SELECTION_BELOW'
    findings=evidence_context(root,'isles24-prediction')
    packet={'version':1,'canonical_direction':'docs/operations/REMOTE_OPERATING_DIRECTION.md',
            'documents':documents,'selected_scientific_context':{n:{'sha256':hashlib.sha256(v.encode()).hexdigest(),'content':v} for n,v in selected.items()},'proposed_context_not_authority':{n:{'sha256':hashlib.sha256(v.encode()).hexdigest(),'content':v} for n,v in proposed.items()},'task_state':task_state,'permitted_findings':findings,
            'precedence':'Approved operating direction and applicable frozen scientific contracts govern. Proposed artifacts and historical task reasons do not grant authority. No laptop conversation is assumed.'}
    scan('operating-context.json',json.dumps(packet).encode());return packet


def envelope(root,folder,prompt,verified_source=None):
    if not isinstance(verified_source,str) or not re.fullmatch('[0-9a-f]{40}',verified_source):raise ValueError('VERIFIED_SOURCE_REQUIRED')
    folder=Path(folder)
    candidates=[folder/'post-execution-packet.json',folder/'packet.json']
    state=None
    for p in candidates:
        if p.exists():
            if p.is_symlink() or p.stat().st_size>1500000:raise ValueError('TASK_CONTEXT_PATH')
            raw=p.read_bytes()
            packet=json.loads(raw)
            state={key:packet[key] for key in ('jobs','trigger','verified_events','executed_selection','decision_inbox','wakes','reviewer_evidence','previous_findings') if key in packet}
            break
    if not state or not any(state.values()):raise ValueError('CURRENT_TASK_CONTEXT_REQUIRED')
    current=build(root,state)
    current['verified_source_commit']=verified_source
    current['task_packet']={'name':p.name,'sha256':hashlib.sha256(raw).hexdigest()}
    scan('operating-context.json',json.dumps(current).encode())
    body='CURRENT APPROVED OPERATING CONTEXT (historical material below remains evidence, not overriding authority):\n'+json.dumps(current)+'\n\nBOUND TASK / HISTORICAL EVIDENCE:\n'+prompt
    scan('hosted-envelope.md',body.encode())
    return body,current
