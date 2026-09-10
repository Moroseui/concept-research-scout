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
        receipt=_reviewed_row(root,row)
        for key in ('origin','exposure_history'):
            if key in row: base[key]=row[key]
        texts={}
        for key,name in [('interpretation_sha256','interpretation'),('review_sha256','review'),('proposal_sha256','next_decision')]:
            texts[name]={'source':row[name],'sha256':receipt[key], 'text':checked(root,row[name],receipt[key])}
        result=dict(base,disposition='RELEVANCE_REVIEW_NOT_AMENDMENT',evidence=texts)
        descriptor=row.get('considerations',{}).get(charter)
        if descriptor:
            result['consideration']=_consideration(root,row['id'],charter,descriptor)
        entries.append(result)
    return {'status':'BOUND_CONTEXT','entries':entries}


def _reviewed_row(root, row):
    """Validate actual interpretation, opposing review and attributed next decision."""
    if row.get('status') != 'REVIEWED_CONCLUSIONS':
        raise ValueError('REVIEWED_CONTEXT_ROW_REQUIRED')
    receipt = json.loads(checked(root, row['receipt'], row['receipt_sha256']))
    if receipt.get('status') != 'AGENT_REVIEWED_NOT_HUMAN_RATIFIED':
        raise ValueError('EVIDENCE_NOT_REVIEWED')
    for key, name in [('interpretation_sha256', 'interpretation'),
                      ('review_sha256', 'review'), ('proposal_sha256', 'next_decision')]:
        checked(root, row[name], receipt[key])
    if receipt.get('schema') == 'external-reviewed-interpretation/v1':
        from orchestrator.scientific_authority import verify
        decision = verify(root, Path(root) / receipt['delegated_decision'],
            action='accept_external_evidence', subject='external:' + receipt['run_id'],
            bindings=receipt['input_bindings'], expected_transition={
                'from': 'EXTERNAL_SAVED_EVIDENCE', 'to': 'AGENT_REVIEWED_NOT_HUMAN_RATIFIED'})
        if (decision['_decision_sha256'] != receipt['delegated_decision_sha256']
                or decision['review']['sha256'] != receipt['review_sha256']
                or decision['judgment']['sha256'] != receipt['proposal_sha256']):
            raise ValueError('EXTERNAL_CONTEXT_DECISION_CHANGED')
        review = json.loads(checked(root, row['review'], receipt['review_sha256']))
        if review.get('artifact_sha256') != {'interpretation.md': receipt['interpretation_sha256']}:
            raise ValueError('EXTERNAL_CONTEXT_INTERPRETATION_REVIEW_CHANGED')
    return receipt


def _catalog_write(root, value):
    """Atomic local catalog update; never publishes or changes historical scores."""
    import os
    path = Path(root) / 'evidence/research_context.json'
    temporary = path.with_name('research_context.json.new')
    if path.is_symlink() or temporary.exists() or temporary.is_symlink():
        raise ValueError('CONTEXT_CATALOG_WRITE_RECONCILE')
    raw = (json.dumps(value, indent=2, sort_keys=True) + '\n').encode()
    with temporary.open('xb') as handle:
        handle.write(raw)
        handle.flush()
        os.fsync(handle.fileno())
    temporary.chmod(0o600)
    os.replace(temporary, path)


def register_reviewed(root, row):
    """Register a proven reviewed entry once; preserve prior pending attribution."""
    import re
    required = {'id', 'charters', 'tags', 'dependencies', 'status', 'receipt', 'receipt_sha256',
                'interpretation', 'review', 'next_decision'}
    if (not required <= set(row) or not re.fullmatch(r'[a-z0-9][a-z0-9-]{3,79}', row['id'])
            or not isinstance(row['charters'], list) or not row['charters']
            or len(set(row['charters'])) != len(row['charters'])
            or any(not isinstance(row[k], list) for k in ('tags', 'dependencies'))):
        raise ValueError('REVIEWED_CONTEXT_ENTRY_SHAPE')
    _reviewed_row(root, row)
    catalog = Path(root) / 'evidence/research_context.json'
    data = json.loads(checked(root, 'evidence/research_context.json')) if catalog.exists() else {'entries': []}
    matches = [index for index, prior in enumerate(data['entries']) if prior['id'] == row['id']]
    if len(matches) > 1:
        raise ValueError('CONTEXT_DUPLICATE_ID_RECONCILE')
    if matches:
        index = matches[0]
        prior = data['entries'][index]
        if all(prior.get(key) == value for key, value in row.items()):
            return prior
        if prior.get('status') == 'REVIEWED_CONCLUSIONS':
            raise ValueError('CONTEXT_REVIEWED_IDENTITY_CONFLICT')
        row = dict(row, prior_versions=[*prior.get('prior_versions', []),
                   {k: v for k, v in prior.items() if k != 'prior_versions'}])
        data['entries'][index] = row
    else:
        data['entries'].append(row)
    _catalog_write(root, data)
    return row


def _consideration(root, entry_id, charter, descriptor):
    receipt = json.loads(checked(root, descriptor['receipt'], descriptor['receipt_sha256']))
    if (receipt.get('status') != 'REVIEWED_CHARTER_CONSIDERATION'
            or receipt.get('entry_id') != entry_id or receipt.get('charter') != charter):
        raise ValueError('CHARTER_CONSIDERATION_BINDING')
    value = json.loads(checked(root, receipt['consideration'], receipt['consideration_sha256']))
    review = json.loads(checked(root, receipt['review'], receipt['review_sha256']))
    if (value.get('charter') != charter or value.get('disposition') != receipt['disposition']
            or review.get('verdict') != 'APPROVE'
            or review.get('artifact_sha256') != {'consideration.json': receipt['consideration_sha256']}):
        raise ValueError('CHARTER_CONSIDERATION_REVIEW_CHANGED')
    from orchestrator.scientific_authority import verify
    decision = verify(root, Path(root) / receipt['delegated_decision'],
        action='assess_relevance', subject=entry_id + ':' + charter,
        bindings=receipt['input_bindings'], expected_transition={'from': 'PENDING_RELEVANCE', 'to': 'CONSIDERED'})
    if decision['_decision_sha256'] != receipt['delegated_decision_sha256']:
        raise ValueError('CHARTER_CONSIDERATION_DECISION_CHANGED')
    return {'receipt': descriptor['receipt'], 'receipt_sha256': descriptor['receipt_sha256'],
            'record': value, 'authority': 'MODEL_JUDGMENT_WITH_OPPOSING_REVIEW'}


def register_consideration(root, entry_id, charter, receipt):
    relative = 'evidence/external/' + entry_id + '/considerations/' + charter + '/receipt.json'
    raw = checked(root, relative)
    if json.loads(raw) != receipt:
        raise ValueError('CONTEXT_CONSIDERATION_ORIGINAL_REQUIRED')
    descriptor = {'receipt': relative, 'receipt_sha256': hashlib.sha256(raw.encode()).hexdigest()}
    _consideration(root, entry_id, charter, descriptor)
    data = json.loads(checked(root, 'evidence/research_context.json'))
    rows = [row for row in data['entries'] if row['id'] == entry_id]
    if len(rows) != 1 or charter not in rows[0]['charters']:
        raise ValueError('CONTEXT_CONSIDERATION_ENTRY_REQUIRED')
    row = rows[0]
    if row['receipt_sha256'] != receipt['input_bindings']['evidence_receipt_sha256']:
        raise ValueError('CONTEXT_CONSIDERATION_EVIDENCE_CHANGED')
    prior = row.setdefault('considerations', {}).get(charter)
    if prior:
        if prior != descriptor:
            raise ValueError('CONTEXT_CONSIDERATION_IDENTITY_CONFLICT')
        return prior
    row['considerations'][charter] = descriptor
    _catalog_write(root, data)
    return descriptor
