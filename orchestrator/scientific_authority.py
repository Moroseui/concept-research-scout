"""Shared attribution/scope checks for delegated scientific decisions.

Policy is operator direction; decisions remain model judgments. These checks bind
the existing system's stage receipts, not provider signatures. Callers retain
their contract, human-stop, resource, deduplication and transaction checks.
"""
import hashlib
import json
from pathlib import Path
import re

POLICY_PATH = 'configs/scientific-delegation-20260909.json'
POLICY_VERSION = '20260909-meeting-v1'
DIRECTION_SHA = 'd936c1b9e79360f0d48debb2c6b3379c7e8098167a541121aaac7ccfc8d9db2a'
ACTIONS = frozenset(('approve_probe', 'accept_interpretation', 'resume_science',
                     'adopt_followup', 'launch_p001', 'accept_external_evidence',
                     'assess_relevance'))
SCOPE = dict(existing_mission=True, new_dataset_access=False,
             reserved_cohort_access=False, new_paid_resources=False,
             public_private_data_export=False, main_merge=False,
             limiter_reset=False, unattended_activation=False,
             override_human_stop=False, permanent_idea_rejection=False)
P001_SCOPE = {'p001_exact_core_sha256': '0cf2f64120976bc46d8bb25a543318af22c3f2e8cd8cad9fbf953ae02b400dfc',
              'p001_combined_transfer_cap': 33554432,
              'p001_max_extracted_bytes': 8589934592}


def encoded(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def read(path, limit=250000):
    path = Path(path).absolute()
    if any(p.is_symlink() for p in (path, *path.parents)) or not path.is_file():
        raise ValueError('SCIENTIFIC_AUTHORITY_REGULAR_FILE_REQUIRED')
    raw = path.read_bytes()
    if len(raw) > limit:
        raise ValueError('SCIENTIFIC_AUTHORITY_SIZE_BOUND')
    return raw


def policy(root):
    raw = read(Path(root) / POLICY_PATH)
    value = json.loads(raw)
    if (value.get('schema') != 'research-scientific-delegation/v1' or
            value.get('version') != POLICY_VERSION or
            value.get('status') != 'USER_DELEGATED_SCIENTIFIC_JUDGMENT' or
            value.get('scope') != SCOPE or
            any(type(value['scope'][k]) is not bool for k in SCOPE) or
            any(value.get(k) != v for k, v in P001_SCOPE.items()) or
            set(value.get('actions', [])) != ACTIONS or
            value.get('direction_path') != 'docs/operations/SCIENTIFIC_DELEGATION_20260909.md' or
            value.get('direction_sha256') != DIRECTION_SHA or
            digest(read(Path(root) / value['direction_path'])) != DIRECTION_SHA):
        raise ValueError('CURRENT_SCIENTIFIC_DELEGATION_REQUIRED')
    return value, {'path': POLICY_PATH, 'sha256': digest(raw), 'version': POLICY_VERSION}


def context(root):
    """Current policy for fresh model prompts; historical prompts stay unchanged."""
    value, binding = policy(root)
    result = {'policy': value, 'binding': binding,
              'direction': read(Path(root) / value['direction_path']).decode()}
    manifest_path = Path(root) / 'configs/scientific-operating-context.json'
    # Immutable older snapshots retain their actually supplied policy. Fresh
    # deployments advertise and receipt the current shared operating manifest.
    if manifest_path.exists() or manifest_path.is_symlink():
        raw = read(manifest_path)
        manifest = json.loads(raw)
        if (set(manifest) != {'schema', 'version', 'authority_policy', 'documents', 'roles'} or
                manifest['schema'] != 'scientific-operating-context/v1' or
                manifest['authority_policy'] != binding or
                set(manifest['roles']) != {'codex', 'claude'}):
            raise ValueError('SCIENTIFIC_OPERATING_CONTEXT_MANIFEST')
        documents = {}
        for name, expected in manifest['documents'].items():
            relative = Path(name)
            if relative.is_absolute() or '..' in relative.parts:
                raise ValueError('SCIENTIFIC_OPERATING_CONTEXT_PATH')
            content = read(Path(root) / relative)
            if digest(content) != expected:
                raise ValueError('SCIENTIFIC_OPERATING_CONTEXT_CHANGED')
            documents[name] = {'sha256': expected, 'text': content.decode()}
        result['operating_context'] = {'manifest': manifest, 'manifest_sha256': digest(raw),
                                       'documents': documents}
    return result


def stage_context(root, directory, family, stage):
    """Same current policy/change state for both roles, with exact input receipt.

    The existing stage provenance binds the full prompt supplied to the model;
    this artifact makes its policy/role versions independently inspectable.
    """
    import os
    if family not in ('codex', 'claude') or not re.fullmatch(r'[a-zA-Z0-9_-]{1,100}', stage):
        raise ValueError('SCIENTIFIC_ROLE_CONTEXT_IDENTITY')
    shared = context(root)
    changes = {}
    store = os.environ.get('SCOUT_CHANGE_REQUEST_STORE')
    if store:
        from orchestrator.change_requests import context as changes_context
        changes = changes_context(Path(store))
    operating = shared.get('operating_context', {})
    supplied = {'shared_policy': shared, 'family': family,
        'role': operating.get('manifest', {}).get('roles', {}).get(family, family),
        'recorded_changes': changes}
    raw = encoded(supplied) + b'\n'
    path = Path(directory) / ('context_' + stage + '.json')
    with path.open('xb') as handle:
        handle.write(raw)
    path.chmod(0o600)
    return ('CURRENT SCIENTIFIC DELEGATION AND TRUSTED SHARED ROLE CONTEXT: Follow the latest user '
            'clarification within its stated scope. Preserve complementary independent '
            'judgment, scientific workflow stages, human stops and reserved boundaries. '
            'Review-pending changes are not approved; address later criticism and identify '
            'affected results before further dependent use.\n' + raw.decode() + '\n')


def decision_context(root, *, action, subject, bindings):
    """Exact context whose digest the original model judgment must carry."""
    _, binding = policy(root)
    if action not in ACTIONS or not isinstance(subject, str) or not subject:
        raise ValueError('SCIENTIFIC_DECISION_ACTION_OR_SUBJECT')
    return {'action': action, 'subject': subject, 'bindings': bindings,
            'policy': binding, 'scope': SCOPE}


def _artifact(directory, descriptor):
    if not isinstance(descriptor, dict) or set(descriptor) != {'path', 'sha256'}:
        raise ValueError('SCIENTIFIC_DECISION_ARTIFACT_BINDING_REQUIRED')
    path = Path(descriptor['path'])
    if path.is_absolute() or '..' in path.parts or not path.parts:
        raise ValueError('SCIENTIFIC_DECISION_ARTIFACT_PATH')
    raw = read(Path(directory) / path)
    if digest(raw) != descriptor['sha256']:
        raise ValueError('SCIENTIFIC_DECISION_ARTIFACT_CHANGED')
    return raw


def _stage(directory, descriptor, family=None):
    rec = json.loads(_artifact(directory, descriptor))
    if (rec.get('exit_class') != 'ok' or rec.get('family_effective') not in ('codex', 'claude') or
            family is not None and rec['family_effective'] != family or
            not re.fullmatch(r'[A-Za-z0-9_-]{6,128}', str(rec.get('run_id', ''))) or
            not isinstance(rec.get('model_used'), str) or not rec['model_used']):
        raise ValueError('SCIENTIFIC_DECISION_SUCCESSFUL_STAGE_REQUIRED')
    return rec


def actor(stage):
    return {'kind': 'agent', 'family': stage['family_effective'],
            'model': stage['model_used'], 'session_id': stage['run_id'],
            'session_id_source': 'system_stage_run_id'}


def verify(root, decision_path, *, action, subject, bindings,
           expected_transition=None, require_review=True, allow_deferred=False):
    """Verify exact current authority and original model/review artifact bindings.

    Absolute decision paths are allowed for private runtime decisions. Numbered
    persistent adapters additionally require a path within their private checkout.
    No action here changes lifecycle, dispatches work or clears a human stop.
    """
    decision_path = Path(decision_path).absolute()
    raw = read(decision_path)
    d = json.loads(raw)
    _, current = policy(root)
    keys = {'schema', 'authority', 'actor', 'policy', 'action', 'subject', 'scope',
            'bindings', 'context_sha256', 'decision', 'rationale', 'transition', 'reconsideration',
            'author_provenance', 'reviewer_provenance', 'judgment', 'review'}
    if (set(d) != keys or d.get('schema') != 'delegated-scientific-decision/v1' or
            d.get('authority') != 'user_delegated_scientific_judgment' or
            action not in ACTIONS or d.get('action') != action or d.get('subject') != subject or
            d.get('bindings') != bindings or d.get('policy') != current or
            d.get('scope') != SCOPE or any(type(d['scope'][k]) is not bool for k in SCOPE)):
        raise ValueError('EXACT_DELEGATED_SCIENTIFIC_AUTHORITY_REQUIRED')
    if d['context_sha256'] != digest(encoded(decision_context(
            root, action=action, subject=subject, bindings=bindings))):
        raise ValueError('ORIGINAL_SCIENTIFIC_DECISION_CONTEXT_CHANGED')
    if d['decision'] not in ('APPLY', 'DEFER') or d['decision'] == 'DEFER' and not allow_deferred:
        raise ValueError('SCIENTIFIC_DECISION_DEFERRED')
    for key in ('rationale', 'reconsideration'):
        if not isinstance(d[key], str) or not d[key].strip():
            raise ValueError('ATTRIBUTED_RATIONALE_AND_RECONSIDERATION_REQUIRED')
    transition = d['transition']
    if (not isinstance(transition, dict) or set(transition) != {'from', 'to'} or
            any(not isinstance(v, str) or not v for v in transition.values()) or
            transition['to'] in ('REJECTED', 'KILLED', 'DELETED', 'INVALID_ROW') or
            expected_transition is not None and transition != expected_transition):
        raise ValueError('SCIENTIFIC_DECISION_TRANSITION_MISMATCH_OR_TERMINAL_REJECTION')
    directory = decision_path.parent
    author = _stage(directory, d['author_provenance'])
    if d['actor'] != actor(author):
        raise ValueError('SCIENTIFIC_DECISION_ACTOR_MISMATCH')
    judgment_raw = _artifact(directory, d['judgment'])
    judgment = json.loads(judgment_raw)
    if judgment != {k: d[k] for k in ('context_sha256', 'decision', 'rationale', 'transition', 'reconsideration')}:
        raise ValueError('ORIGINAL_MODEL_JUDGMENT_CHANGED')
    if require_review:
        reviewer = _stage(directory, d['reviewer_provenance'])
        review = json.loads(_artifact(directory, d['review']))
        if (reviewer['family_effective'] == author['family_effective'] or
                review.get('verdict') != 'APPROVE' or
                review.get('judgment_sha256') != digest(judgment_raw) or
                not isinstance(review.get('rationale'), str) or not review['rationale'].strip()):
            raise ValueError('OPPOSING_SCIENTIFIC_JUDGMENT_REVIEW_REQUIRED')
    return {**d, '_decision_sha256': digest(raw), '_decision_path': str(decision_path)}


def seal(root, directory, *, action, subject, bindings, author, reviewer,
         judgment='judgment.json', review='review.json'):
    """Bind original system outputs; never supply a judgment on a model's behalf.

    The stage adapter must preserve its original prompts/consoles/provenance. The
    two provenance files below are explicitly copies of returned system receipts.
    Existing destinations refuse; recovery verifies the original decision instead.
    """
    directory = Path(directory)
    _, binding = policy(root)
    proposal = json.loads(read(directory / judgment))
    if set(proposal) != {'context_sha256', 'decision', 'rationale', 'transition', 'reconsideration'}:
        raise ValueError('SCIENTIFIC_JUDGMENT_SHAPE')
    def write(name, value):
        path = directory / name
        with path.open('xb') as handle:
            handle.write(encoded(value) + b'\n')
        path.chmod(0o600)
        return {'path': name, 'sha256': digest(read(path))}
    def artifact(name):
        return {'path': name, 'sha256': digest(read(directory / name))}
    record = {'schema': 'delegated-scientific-decision/v1',
              'authority': 'user_delegated_scientific_judgment', 'actor': actor(author),
              'policy': binding, 'action': action, 'subject': subject, 'scope': SCOPE,
              'bindings': bindings, **proposal,
              'author_provenance': write('decision-author.provenance.json', author),
              'reviewer_provenance': write('decision-reviewer.provenance.json', reviewer),
              'judgment': artifact(judgment), 'review': artifact(review)}
    write('decision.json', record)
    return verify(root, directory / 'decision.json', action=action, subject=subject,
                  bindings=bindings, expected_transition=proposal['transition'], allow_deferred=True)
