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
POLICY_VERSION = '20260911-continuing-research-v3'
FINITE_POLICY_VERSION = '20260910-finite-preparation-v2'
LEGACY_POLICY_VERSION = '20260909-meeting-v1'
LEGACY_DIRECTION_SHA = 'd936c1b9e79360f0d48debb2c6b3379c7e8098167a541121aaac7ccfc8d9db2a'
LEGACY_ACTIONS = frozenset(('approve_probe', 'accept_interpretation', 'resume_science',
                     'adopt_followup', 'launch_p001', 'accept_external_evidence',
                     'assess_relevance'))
FINITE_ACTIONS = LEGACY_ACTIONS | {'authorize_research_task'}
ACTIONS = FINITE_ACTIONS | {'launch_linux_job', 'authorize_protocol', 'approve_scientific_version'}
DIRECTION_PATH = 'docs/operations/CONTINUING_RESEARCH_AUTHORIZATION_20260911.md'
DIRECTION_SHA = '3813037a2f51aa86b92a9cbc10bc95b8487c3b1c36ecf76a21b1d4d8546dec01'
FINITE_RESEARCH_TASK_SCOPE = {'experiment': 'P001', 'modes': ['discuss', 'readiness'],
                      'installed_finite_task_only': True, 'patient_execution': False,
                      'code_execution': False, 'new_data_access': False}
LEGACY_SCOPE = dict(existing_mission=True, new_dataset_access=False,
             reserved_cohort_access=False, new_paid_resources=False,
             public_private_data_export=False, main_merge=False,
             limiter_reset=False, unattended_activation=False,
             override_human_stop=False, permanent_idea_rejection=False)
# Prospective authority is conditional on separately reviewed protocol and launch
# decisions. The scope bit never substitutes for those executable gates.
SCOPE = {**LEGACY_SCOPE, 'reserved_cohort_access': True}
RESEARCH_MODES = ('adoption', 'brief', 'charter', 'code', 'code_bundle', 'curate', 'discuss',
                  'interpret', 'investigate', 'propose', 'protocol_proposal', 'readiness', 'repair', 'specify')
RESEARCH_TASK_SCOPE = {
    'charter': 'isles24-prediction', 'experiments': ['P001', 'P002', 'P003'],
    'modes': list(RESEARCH_MODES), 'installed_finite_task_only': False,
    'reviewed_successor_required': True, 'separate_execution_authority': True,
    'new_data_access': False}
METHODOLOGY_SCOPE = {
    'dataset': 'existing_authorized_isles24_data',
    'prospective_reviewed_protocol_required': True,
    'registry_membership_and_exposure_bound': True,
    'preserve_prior_partitions_and_results': True,
    'no_opportunistic_outcome_tuning': True,
    'no_untouched_claim_for_exposed_cases': True,
    'recorded_reserved_count': 49,
    'frozen_p001_preserved': True}
RUNTIME_SCOPE = {
    'autonomous_backend': 'linux', 'autonomous_actions_dispatch': False,
    'manual_actions': 'NOTIFY_FIRST_WAIT_FOR_PRE_ADMISSION',
    'automatic_shared_actions_accounting_installed': False,
    'existing_admission_limits_and_halt_preserved': True,
    'activation': 'EXISTING_CONDITIONAL_HUMAN_GRANT_AFTER_REVIEWED_CHECKS',
    'polling_and_control_model_calls': 0}


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


def _create_original(path, raw):
    """Never replace an original, including after a partial interrupted write."""
    try:
        with path.open('xb') as handle:
            handle.write(raw)
    except FileExistsError as exc:
        raise ValueError('SCIENTIFIC_AUTHORITY_ORIGINAL_EXISTS_RECONCILE') from exc
    path.chmod(0o600)


def policy(root):
    raw = read(Path(root) / POLICY_PATH)
    value = json.loads(raw)
    version = value.get('version')
    rules = {
        LEGACY_POLICY_VERSION: (LEGACY_ACTIONS, LEGACY_SCOPE,
            'docs/operations/SCIENTIFIC_DELEGATION_20260909.md', LEGACY_DIRECTION_SHA),
        FINITE_POLICY_VERSION: (FINITE_ACTIONS, LEGACY_SCOPE,
            'docs/operations/SCIENTIFIC_DELEGATION_20260909.md', LEGACY_DIRECTION_SHA),
        POLICY_VERSION: (ACTIONS, SCOPE, DIRECTION_PATH, DIRECTION_SHA)}
    if version not in rules:
        raise ValueError('CURRENT_SCIENTIFIC_DELEGATION_REQUIRED')
    actions, scope, direction_path, direction_sha = rules[version]
    if (value.get('schema') != 'research-scientific-delegation/v1' or
            value.get('status') != 'USER_DELEGATED_SCIENTIFIC_JUDGMENT' or
            value.get('scope') != scope or
            any(type(value['scope'][k]) is not bool for k in scope) or
            any(value.get(k) != v for k, v in P001_SCOPE.items()) or
            not isinstance(value.get('actions'), list) or
            len(value['actions']) != len(actions) or set(value['actions']) != actions or
            value.get('direction_path') != direction_path or
            value.get('direction_sha256') != direction_sha or
            digest(read(Path(root) / direction_path)) != direction_sha):
        raise ValueError('CURRENT_SCIENTIFIC_DELEGATION_REQUIRED')
    expected_sections = ({'research_task_scope': FINITE_RESEARCH_TASK_SCOPE}
                        if version == FINITE_POLICY_VERSION else
                        {'research_task_scope': RESEARCH_TASK_SCOPE,
                         'methodology_scope': METHODOLOGY_SCOPE,
                         'runtime_scope': RUNTIME_SCOPE} if version == POLICY_VERSION else {})
    for key, expected in expected_sections.items():
        # Canonical comparison also rejects bool/int substitutions in nested policy.
        if encoded(value.get(key)) != encoded(expected):
            raise ValueError('CURRENT_SCIENTIFIC_DELEGATION_REQUIRED')
    # Historical decisions still require their retained original root and exact
    # policy bytes. Recognizing the old version never upgrades its scope.
    return value, {'path': POLICY_PATH, 'sha256': digest(raw), 'version': version}


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
    changes = {'status': 'CHANGE_STORE_NOT_CONFIGURED',
        'meaning': 'No change-store observation was supplied by this route. This does not establish absence of pending review or later criticism; inspect any explicitly bound task change records before dependent use.'}
    store = os.environ.get('SCOUT_CHANGE_REQUEST_STORE')
    if store:
        from orchestrator.change_requests import context as changes_context
        path = Path(store)
        if not path.is_dir() or path.is_symlink():
            raise ValueError('CONFIGURED_CHANGE_STORE_UNAVAILABLE')
        changes = changes_context(path)
    operating = shared.get('operating_context', {})
    supplied = {'shared_policy': shared, 'family': family,
        'role': operating.get('manifest', {}).get('roles', {}).get(family, family),
        'recorded_changes': changes}
    raw = encoded(supplied) + b'\n'
    path = Path(directory) / ('context_' + stage + '.json')
    _create_original(path, raw)
    return ('CURRENT SCIENTIFIC DELEGATION AND TRUSTED SHARED ROLE CONTEXT: Follow the latest user '
            'clarification within its stated scope. Preserve complementary independent '
            'judgment, scientific workflow stages, human stops and reserved boundaries. '
            'Review-pending changes are not approved; address later criticism and identify '
            'affected results before further dependent use.\n' + raw.decode() + '\n')


def decision_context(root, *, action, subject, bindings):
    """Exact context whose digest the original model judgment must carry."""
    current, binding = policy(root)
    if action not in current['actions'] or not isinstance(subject, str) or not subject:
        raise ValueError('SCIENTIFIC_DECISION_ACTION_OR_SUBJECT')
    def pin(value, length):
        return isinstance(value, str) and re.fullmatch('[0-9a-f]{'+str(length)+'}', value)
    slug = re.fullmatch('[a-z0-9][a-z0-9-]{0,79}', subject)
    if action == 'authorize_research_task':
        base = {'catalog_core_sha256', 'source', 'experiment', 'mode'}
        legacy = isinstance(bindings, dict) and set(bindings) == base
        continuing = (current['version'] == POLICY_VERSION and isinstance(bindings, dict)
                      and (set(bindings) == base | {'operation_sha256'} or
                           set(bindings) == base | {'operation_sha256', 'template_sha256'}
                           and bindings.get('mode') == 'investigate' and pin(bindings.get('template_sha256'), 64)))
        valid_legacy = (legacy and bindings['experiment'] == 'P001'
                        and bindings['mode'] in ('discuss', 'readiness'))
        valid_continuing = (continuing and bindings['experiment'] in RESEARCH_TASK_SCOPE['experiments']
                            and bindings['mode'] in RESEARCH_MODES
                            and pin(bindings['operation_sha256'], 64))
        if (not (valid_legacy or valid_continuing) or not slug
                or not pin(bindings['catalog_core_sha256'], 64)
                or not pin(bindings['source'], 40)):
            raise ValueError('EXACT_REVIEWED_RESEARCH_OPERATION_AUTHORITY_REQUIRED'
                             if current['version'] == POLICY_VERSION else
                             'FINITE_P001_PREPARATION_AUTHORITY_ONLY')
    elif action in ('launch_linux_job', 'authorize_protocol', 'approve_scientific_version'):
        keys = {
            'launch_linux_job': {'job_core_sha256', 'source', 'experiment', 'spec_sha256', 'code_sha256'},
            'authorize_protocol': {'source', 'experiment', 'protocol_sha256', 'input_manifest_sha256',
                'partition_registry_sha256', 'exposure_history_sha256', 'literature_review_sha256',
                'methodology_review_sha256', 'prior_protocol_sha256'},
            'approve_scientific_version': {'source', 'experiment', 'scientific_version_sha256',
                'review_input_manifest_sha256', 'protocol_decision_sha256', 'proposal_sha256',
                'code_sha256', 'spec_sha256', 'requirements_sha256'}}[action]
        if (current['version'] != POLICY_VERSION or not isinstance(bindings, dict)
                or set(bindings) != keys or not slug
                or bindings['experiment'] not in RESEARCH_TASK_SCOPE['experiments']
                or not pin(bindings['source'], 40)
                or any(not pin(v, 64) for k, v in bindings.items()
                       if k not in ('source', 'experiment', 'prior_protocol_sha256'))
                or 'prior_protocol_sha256' in bindings and
                   bindings['prior_protocol_sha256'] is not None and
                   not pin(bindings['prior_protocol_sha256'], 64)):
            raise ValueError('EXACT_PROSPECTIVE_PROTOCOL_OR_LINUX_JOB_AUTHORITY_REQUIRED')
    return {'action': action, 'subject': subject, 'bindings': bindings,
            'policy': binding, 'scope': current['scope']}


def _artifact_path(name):
    if not isinstance(name, str):
        raise ValueError('SCIENTIFIC_DECISION_ARTIFACT_PATH')
    path = Path(name)
    if path.is_absolute() or '..' in path.parts or not path.parts:
        raise ValueError('SCIENTIFIC_DECISION_ARTIFACT_PATH')
    return path


def _artifact(directory, descriptor):
    if not isinstance(descriptor, dict) or set(descriptor) != {'path', 'sha256'}:
        raise ValueError('SCIENTIFIC_DECISION_ARTIFACT_BINDING_REQUIRED')
    path = _artifact_path(descriptor['path'])
    raw = read(Path(directory) / path)
    if digest(raw) != descriptor['sha256']:
        raise ValueError('SCIENTIFIC_DECISION_ARTIFACT_CHANGED')
    return raw


def _stage(directory, descriptor, family=None):
    return _stage_record(json.loads(_artifact(directory, descriptor)), family)


def _stage_record(rec, family=None):
    if (not isinstance(rec, dict) or
            rec.get('exit_class') != 'ok' or rec.get('family_effective') not in ('codex', 'claude') or
            family is not None and rec['family_effective'] != family or
            not re.fullmatch(r'[A-Za-z0-9_-]{6,128}', str(rec.get('run_id', ''))) or
            not isinstance(rec.get('model_used'), str) or not rec['model_used']):
        raise ValueError('SCIENTIFIC_DECISION_SUCCESSFUL_STAGE_REQUIRED')
    return rec


def actor(stage):
    value = {'kind': 'agent', 'family': stage['family_effective'],
            'model': stage['model_used'], 'session_id': stage['run_id'],
            'session_id_source': 'system_stage_run_id'}
    if (isinstance(stage.get('runner'), dict) and
            stage['runner'].get('adapter') == 'protected-scientific-decision-v1'):
        value.update(requested_model=stage['requested_model'], actual_model=stage['actual_model'],
                     model_identity_source='requested_model; actual_model retained separately',
                     session_id_source='original_provider_receipt')
    return value


def _judgment_preconditions(root, d, *, action, subject, bindings,
                            expected_transition=None, allow_deferred=False):
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


def _review_preconditions(author, reviewer, review, judgment_raw):
    if (not isinstance(review, dict) or
            reviewer['family_effective'] == author['family_effective'] or
            review.get('verdict') != 'APPROVE' or
            review.get('judgment_sha256') != digest(judgment_raw) or
            not isinstance(review.get('rationale'), str) or not review['rationale'].strip()):
        raise ValueError('OPPOSING_SCIENTIFIC_JUDGMENT_REVIEW_REQUIRED')


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
    current_value, current = policy(root)
    keys = {'schema', 'authority', 'actor', 'policy', 'action', 'subject', 'scope',
            'bindings', 'context_sha256', 'decision', 'rationale', 'transition', 'reconsideration',
            'author_provenance', 'reviewer_provenance', 'judgment', 'review'}
    if (set(d) != keys or d.get('schema') != 'delegated-scientific-decision/v1' or
            d.get('authority') != 'user_delegated_scientific_judgment' or
            action not in current_value['actions'] or d.get('action') != action or d.get('subject') != subject or
            d.get('bindings') != bindings or d.get('policy') != current or
            d.get('scope') != current_value['scope'] or
            any(type(d['scope'][k]) is not bool for k in current_value['scope'])):
        raise ValueError('EXACT_DELEGATED_SCIENTIFIC_AUTHORITY_REQUIRED')
    _judgment_preconditions(root, d, action=action, subject=subject, bindings=bindings,
                            expected_transition=expected_transition, allow_deferred=allow_deferred)
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
        _review_preconditions(author, reviewer, review, judgment_raw)
    return {**d, '_decision_sha256': digest(raw), '_decision_path': str(decision_path)}


def seal(root, directory, *, action, subject, bindings, author, reviewer,
         judgment='judgment.json', review='review.json'):
    """Bind original system outputs; never supply a judgment on a model's behalf.

    The stage adapter must preserve its original prompts/consoles/provenance. The
    two provenance files below are explicitly copies of returned system receipts.
    Existing destinations refuse; recovery verifies the original decision instead.
    Validate before writing, while still preserving a partial write after a crash
    or concurrent change for explicit reconciliation. This is not an atomic seal.
    """
    directory = Path(directory)
    current, binding = policy(root)
    judgment_raw = read(directory / _artifact_path(judgment))
    review_raw = read(directory / _artifact_path(review))
    proposal = json.loads(judgment_raw)
    if not isinstance(proposal, dict) or set(proposal) != {'context_sha256', 'decision', 'rationale', 'transition', 'reconsideration'}:
        raise ValueError('SCIENTIFIC_JUDGMENT_SHAPE')
    _judgment_preconditions(root, proposal, action=action, subject=subject, bindings=bindings,
                            allow_deferred=True)
    _stage_record(author)
    _stage_record(reviewer)
    _review_preconditions(author, reviewer, json.loads(review_raw), judgment_raw)
    destinations = ('decision-author.provenance.json', 'decision-reviewer.provenance.json', 'decision.json')
    if any((directory / name).exists() or (directory / name).is_symlink() for name in destinations):
        raise ValueError('SCIENTIFIC_AUTHORITY_ORIGINAL_EXISTS_RECONCILE')
    def write(name, value):
        path = directory / name
        _create_original(path, encoded(value) + b'\n')
        return {'path': name, 'sha256': digest(read(path))}
    record = {'schema': 'delegated-scientific-decision/v1',
              'authority': 'user_delegated_scientific_judgment', 'actor': actor(author),
              'policy': binding, 'action': action, 'subject': subject, 'scope': current['scope'],
              'bindings': bindings, **proposal,
              'author_provenance': write('decision-author.provenance.json', author),
              'reviewer_provenance': write('decision-reviewer.provenance.json', reviewer),
              'judgment': {'path': judgment, 'sha256': digest(judgment_raw)},
              'review': {'path': review, 'sha256': digest(review_raw)}}
    write('decision.json', record)
    return verify(root, directory / 'decision.json', action=action, subject=subject,
                  bindings=bindings, expected_transition=proposal['transition'], allow_deferred=True)
