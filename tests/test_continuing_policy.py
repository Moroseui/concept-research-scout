"""Prospective authority must not upgrade old seals or omit exact execution inputs."""
import json
from pathlib import Path
import shutil
import subprocess

import pytest

from orchestrator import scientific_authority as a

ROOT = Path(__file__).resolve().parents[1]
OLD = '03a18ba15a7c7703b67ed0d14d6c2b25a2dc023c'


def policy_root(path, old=False):
    path.mkdir()
    names = [a.POLICY_PATH, 'docs/operations/SCIENTIFIC_DELEGATION_20260909.md'
             if old else a.DIRECTION_PATH]
    for name in names:
        dest = path / name
        dest.parent.mkdir(parents=True, exist_ok=True)
        raw = (subprocess.check_output(['git', 'show', OLD+':'+name], cwd=ROOT)
               if old else (ROOT/name).read_bytes())
        dest.write_bytes(raw)
    return path


def task_bindings():
    return dict(catalog_core_sha256='a'*64, source='b'*40, experiment='P002',
                mode='investigate', operation_sha256='c'*64)


def test_old_finite_policy_does_not_authorize_new_operation(tmp_path):
    old = policy_root(tmp_path/'old', True)
    new = policy_root(tmp_path/'new')
    assert a.policy(old)[1]['version'] == a.FINITE_POLICY_VERSION
    assert not a.policy(old)[0]['scope']['reserved_cohort_access']
    with pytest.raises(ValueError, match='FINITE_P001'):
        a.decision_context(old, action='authorize_research_task', subject='successor-v1', bindings=task_bindings())
    context = a.decision_context(new, action='authorize_research_task', subject='successor-v1', bindings=task_bindings())
    assert context['policy']['version'] == a.POLICY_VERSION
    changed = task_bindings() | {'operation_sha256': 'd'*64}
    assert a.digest(a.encoded(context)) != a.digest(a.encoded(a.decision_context(
        new, action='authorize_research_task', subject='successor-v1', bindings=changed)))


def test_old_seal_is_recoverable_only_with_original_policy(tmp_path):
    old = policy_root(tmp_path/'old', True)
    new = policy_root(tmp_path/'new')
    directory = tmp_path/'decision'
    directory.mkdir()
    kw = dict(action='accept_interpretation', subject='idea:047', bindings={'result_sha256':'a'*64})
    judgment = dict(context_sha256=a.digest(a.encoded(a.decision_context(old, **kw))),
                    decision='APPLY', rationale='Fixture: original reviewed disposition',
                    reconsideration='Fixture: distinct evidence', transition={'from':'ACTIVE','to':'PAUSED'})
    raw = a.encoded(judgment)+b'\n'
    (directory/'judgment.json').write_bytes(raw)
    (directory/'review.json').write_bytes(a.encoded(dict(verdict='APPROVE', rationale='Fixture review', judgment_sha256=a.digest(raw))))
    author = dict(run_id='fixture-author-01', family_effective='codex', model_used='gpt-6-astra', exit_class='ok')
    reviewer = dict(run_id='fixture-review-01', family_effective='claude', model_used='claude-fable-5', exit_class='ok')
    original = a.seal(old, directory, **kw, author=author, reviewer=reviewer)
    assert a.verify(old, directory/'decision.json', **kw)['_decision_sha256'] == original['_decision_sha256']
    before = (directory/'decision.json').read_bytes()
    with pytest.raises(ValueError, match='EXACT_DELEGATED'):
        a.verify(new, directory/'decision.json', **kw)
    assert (directory/'decision.json').read_bytes() == before


@pytest.mark.parametrize('change', [
    {'source':'short'}, {'operation_sha256':None}, {'experiment':'OTHER'},
    {'mode':'shell'}, {'unreviewed':True}])
def test_task_binding_requires_declared_typed_scope(tmp_path, change):
    root = policy_root(tmp_path/'new')
    with pytest.raises(ValueError, match='EXACT_REVIEWED'):
        a.decision_context(root, action='authorize_research_task', subject='successor-v1', bindings=task_bindings()|change)


def test_protocol_requires_all_prospective_evidence_bindings(tmp_path):
    root = policy_root(tmp_path/'new')
    bindings = dict(source='b'*40, experiment='P002', prior_protocol_sha256=None,
        **{key:'a'*64 for key in ('protocol_sha256','input_manifest_sha256',
            'partition_registry_sha256','exposure_history_sha256','literature_review_sha256','methodology_review_sha256')})
    context = a.decision_context(root, action='authorize_protocol', subject='protocol-v1', bindings=bindings)
    for key in bindings:
        with pytest.raises(ValueError, match='EXACT_PROSPECTIVE'):
            a.decision_context(root, action='authorize_protocol', subject='protocol-v1', bindings={k:v for k,v in bindings.items() if k!=key})
    assert context['scope']['reserved_cohort_access']
    assert context['policy']['version'] == a.POLICY_VERSION


def test_policy_rejects_unreviewed_count_or_actions_claim(tmp_path):
    root = policy_root(tmp_path/'new')
    path = root/a.POLICY_PATH
    original = path.read_bytes()
    for key, subkey, value in [('methodology_scope','recorded_reserved_count',50),
            ('runtime_scope','autonomous_actions_dispatch',True),
            ('runtime_scope','automatic_shared_actions_accounting_installed',True),
            ('research_task_scope','reviewed_successor_required',False)]:
        policy=json.loads(original)
        policy[key][subkey]=value
        path.write_text(json.dumps(policy))
        with pytest.raises(ValueError, match='CURRENT_SCIENTIFIC_DELEGATION'):
            a.policy(root)
    path.write_bytes(original)
    assert a.policy(root)[0]['runtime_scope']['manual_actions'] == 'NOTIFY_FIRST_WAIT_FOR_PRE_ADMISSION'


def test_linux_job_requires_actual_code_and_spec_binding(tmp_path):
    root = policy_root(tmp_path/'new')
    bindings = dict(source='a'*40, experiment='P002', job_core_sha256='b'*64,
                    code_sha256='c'*64, spec_sha256='d'*64)
    a.decision_context(root, action='launch_linux_job', subject='job-v1', bindings=bindings)
    for key in ('code_sha256', 'spec_sha256', 'job_core_sha256'):
        with pytest.raises(ValueError, match='EXACT_PROSPECTIVE'):
            a.decision_context(root, action='launch_linux_job', subject='job-v1', bindings=bindings|{key:None})


def test_scientific_version_requires_full_review_and_origin_bindings(tmp_path):
    root = policy_root(tmp_path/'new')
    bindings = dict(source='a'*40, experiment='P002', **{key:'b'*64 for key in
        ('scientific_version_sha256','review_input_manifest_sha256','protocol_decision_sha256',
         'proposal_sha256','code_sha256','spec_sha256','requirements_sha256')})
    a.decision_context(root, action='approve_scientific_version', subject='scientific-version-v1', bindings=bindings)
    for key in bindings:
        with pytest.raises(ValueError, match='EXACT_PROSPECTIVE'):
            a.decision_context(root, action='approve_scientific_version', subject='scientific-version-v1',
                               bindings={k:v for k,v in bindings.items() if k!=key})


def test_missing_change_observation_is_explicit_and_configured_loss_refuses(tmp_path, monkeypatch):
    monkeypatch.delenv('SCOUT_CHANGE_REQUEST_STORE', raising=False)
    output = tmp_path/'context'
    output.mkdir()
    prompt = a.stage_context(ROOT, output, 'codex', 'missing_change_observation')
    assert 'CHANGE_STORE_NOT_CONFIGURED' in prompt
    assert 'does not establish absence of pending review' in prompt
    monkeypatch.setenv('SCOUT_CHANGE_REQUEST_STORE', str(tmp_path/'missing-configured-store'))
    with pytest.raises(ValueError, match='CONFIGURED_CHANGE_STORE_UNAVAILABLE'):
        a.stage_context(ROOT, output, 'claude', 'missing_configured_store')
