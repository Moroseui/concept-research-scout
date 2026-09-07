"""Explicit, hash-bound proposal context; never grants charter or launch authority."""
import hashlib
import json
from pathlib import Path


def checked(root, relative, expected=None):
    root=Path(root).resolve(); p=root/relative
    if p.is_symlink() or not p.resolve().is_relative_to(root) or any(x.is_symlink() for x in p.parents if x!=root and root in x.parents):
        raise ValueError('UNSAFE_CONTEXT_PATH')
    raw=p.read_bytes()
    if len(raw)>250000: raise ValueError('CONTEXT_SIZE')
    if expected and hashlib.sha256(raw).hexdigest()!=expected: raise ValueError('CONTEXT_BINDING_CHANGED')
    return raw.decode()


def proposal_context(root, relative):
    """Explicit preview only. No automatic selection, adoption or historical rewrite."""
    base=(Path(root)/'campaigns/isles24-pilot/pipeline').resolve()
    candidate=Path(root)/relative
    if '..' in Path(relative).parts or Path(relative).is_absolute() or not candidate.resolve().is_relative_to(base): raise ValueError('PROPOSAL_SCOPE')
    receipt=json.loads(checked(root,relative+'/receipt.json'))
    if receipt.get('status')!='REVIEWED_PROPOSAL_NOT_ADOPTED' or receipt.get('mode')!='charter':
        raise ValueError('REVIEWED_CHARTER_PROPOSAL_REQUIRED')
    for name,expected in receipt['input_sha256'].items():
        if name=='campaigns/isles24-pilot/CAMPAIGN.md' or name.startswith('campaigns/isles24-pilot/experiments/P001/'):
            checked(root,name,expected)
    prefix=f"round-{receipt['round']}/"
    names=['CHARTER.proposed.md','RUBRIC.proposed.md','PROMPTS.proposed.md','P001_ADOPTION.proposed.md','review.json']
    result={relative+'/receipt.json':checked(root,relative+'/receipt.json')}
    for name in names:
        key=prefix+name
        result[relative+'/'+key]=checked(root,relative+'/'+key,receipt['artifact_sha256'][key])
    if json.loads(result[relative+'/'+prefix+'review.json']).get('verdict')!='APPROVE': raise ValueError('CHARTER_REVIEW_NOT_APPROVED')
    result['context-disposition.json']=json.dumps({'status':'EXPLICIT_PROPOSAL_PREVIEW_ONLY','ratified':False,
        'origin':'externally_seeded_operator_delegated_P001','historical_approvals':'unchanged',
        'next_gate':'operator_charter_ratification_and_separate_patient_launch'})
    return result


def selected_prediction_context(root):
    """Load the explicitly recorded operator selection, not an inferred approval.

    The versioned decision is governance input under the normal branch/review
    boundary. This reader verifies bytes and scope; it cannot authenticate a human
    by itself and never grants patient execution.
    """
    relative = 'campaigns/isles24-pilot/prediction_selection.json'
    if not (Path(root) / relative).exists():
        return {}
    decision_text = checked(root, relative)
    decision = json.loads(decision_text)
    if decision.get('status') != 'OPERATOR_RATIFIED_CHARTER_CONDITIONAL_ADOPTION':
        raise ValueError('PREDICTION_SELECTION_NOT_RATIFIED')
    scope = decision.get('scope', {})
    if (scope.get('charter_ratified') is not True
            or scope.get('conditional_external_seed_adoption') is not True
            or any(scope.get(k) is not False for k in
                   ['patient_launch', 'new_backend_patient_transfer', 'reserved_cohort_access'])):
        raise ValueError('PREDICTION_SELECTION_AUTHORITY_SCOPE')
    result = proposal_context(root, decision['proposal'])
    for name, expected in decision['artifact_sha256'].items():
        checked(root, name, expected)
    required = set(result) - {'context-disposition.json'}
    if not required.issubset(decision['artifact_sha256']):
        raise ValueError('PREDICTION_SELECTION_INCOMPLETE_BINDING')
    result[relative] = decision_text
    result['context-disposition.json'] = json.dumps({
        'status': 'OPERATOR_SELECTED_CONDITIONAL_BASELINE', 'ratified': True,
        'origin': 'externally_seeded_operator_delegated_P001',
        'historical_approvals': 'unchanged', 'launch_authorized': False,
        'next_gate': 'eligible_input_preflight_then_separate_exact_launch_decision'})
    return result


def evidence_context(root, charter, *, blind=False):
    """Pending entries carry dependencies, never result prose. Scores stay local."""
    if blind: return {'status':'WITHHELD_DELIBERATE_BLINDING','entries':[]}
    catalog=Path(root)/'evidence/research_context.json'
    if not catalog.exists(): return {'status':'NO_CATALOG','entries':[]}
    data=json.loads(checked(root,'evidence/research_context.json')); entries=[]
    for row in data['entries']:
        if charter not in row['charters']: continue
        base={k:row[k] for k in ('id','tags','dependencies')}
        if row['status']!='REVIEWED_CONCLUSIONS':
            entries.append(dict(base,disposition='PENDING_EVIDENCE_NO_CONCLUSIONS')); continue
        # Explicit review receipt binds actual interpretation, critique and next decision.
        receipt=json.loads(checked(root,row['receipt'],row['receipt_sha256']))
        if receipt.get('status')!='AGENT_REVIEWED_NOT_HUMAN_RATIFIED': raise ValueError('EVIDENCE_NOT_REVIEWED')
        texts={}
        for key,name in [('interpretation_sha256','interpretation'),('review_sha256','review'),('proposal_sha256','next_decision')]:
            texts[name]={'source':row[name],'sha256':receipt[key], 'text':checked(root,row[name],receipt[key])}
        entries.append(dict(base,disposition='RELEVANCE_REVIEW_NOT_AMENDMENT',evidence=texts))
    return {'status':'BOUND_CONTEXT','entries':entries}
