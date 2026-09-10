"""Synthetic campaign decisions: original model/review fixtures, no scientific launch."""
import copy
import json
from pathlib import Path
import shutil
from types import SimpleNamespace
from unittest.mock import patch

import pytest

from orchestrator import campaign as campaign
from orchestrator import campaign_lifecycle as lifecycle
from orchestrator import campaign_pipeline as pipeline
from orchestrator import scientific_authority as authority

SOURCE = Path(__file__).resolve().parents[1]


def copy_policy(root):
    for name in (authority.POLICY_PATH, 'docs/operations/SCIENTIFIC_DELEGATION_20260909.md'):
        destination = Path(root) / name
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(SOURCE / name, destination)


@pytest.fixture
def root(tmp_path):
    copy_policy(tmp_path)
    for name in ('REMOTE_OPERATING_DIRECTION.md', 'CLAUDE_REVIEWER_DIRECTIVE.md'):
        destination = tmp_path / 'docs/operations' / name
        shutil.copyfile(SOURCE / 'docs/operations' / name, destination)
    base = tmp_path / 'campaigns/isles24-pilot'
    exp = base / 'experiments/P001'
    exp.mkdir(parents=True)
    for name in ('SPEC.md', 'run.py', 'requirements.txt', 'publication.json',
                 'investigator_decision.json', 'review.json'):
        shutil.copyfile(SOURCE / 'campaigns/isles24-pilot/experiments/P001' / name, exp / name)
    shutil.copyfile(SOURCE / 'campaigns/isles24-pilot/CAMPAIGN.md', base / 'CAMPAIGN.md')
    return tmp_path


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(authority.encoded(value) + b'\n')


def proposal(root, experiment='P001'):
    path = root / 'campaigns/isles24-pilot/pipeline' / ('synthetic-adoption-' + experiment)
    folder = path / 'round-1'
    folder.mkdir(parents=True)
    (folder / 'adoption.proposed.md').write_text('Synthetic prospective adoption proposal only.')
    write(folder / 'review.json', {'verdict': 'APPROVE', 'rationale': 'Synthetic opposing proposal review.'})
    write(path / 'request.json', {'status': 'PROPOSAL_ONLY', 'mode': 'adoption', 'experiment': experiment})
    write(path / 'receipt.json', {'status': 'REVIEWED_PROPOSAL_NOT_ADOPTED', 'mode': 'adoption',
         'experiment': experiment, 'round': 1, 'author_family': 'codex', 'reviewer_family': 'claude',
         'artifact_sha256': {str(p.relative_to(path)): authority.digest(p.read_bytes())
                            for p in folder.iterdir()}})
    return path


def result(root, experiment='P001'):
    exp = root / 'campaigns/isles24-pilot/experiments' / experiment
    folder = exp / 'results/synthetic'
    write(folder / 'summary.json', {'synthetic_only': True})
    write(exp / 'import_receipt.json', {'spec_sha256': campaign.sha(exp / 'SPEC.md'),
         'review_sha256': campaign.sha(exp / 'review.json'), 'bundle': str(folder.relative_to(root)),
         'bundle_file_sha256': {'summary.json': campaign.sha(folder / 'summary.json')}})
    (exp / 'interpretation.md').write_text('Synthetic reviewed interpretation, no scientific finding.')
    (exp / 'interpret_review.md').write_text('Synthetic opposing review APPROVE.')
    write(exp / 'investigator_next_decision.json', {'status': 'PROPOSAL_ONLY',
                                                  'rationale': 'Synthetic next question.'})
    write(exp / 'interpretation_receipt.json', {'status': 'AGENT_REVIEWED_NOT_HUMAN_RATIFIED',
         'author_family': 'codex', 'reviewer_family': 'claude',
         'import_receipt_sha256': campaign.sha(exp / 'import_receipt.json'),
         'interpretation_sha256': campaign.sha(exp / 'interpretation.md'),
         'review_sha256': campaign.sha(exp / 'interpret_review.md'),
         'proposal_sha256': campaign.sha(exp / 'investigator_next_decision.json')})
    return exp


def judgment(root, experiment, action, proposed=None, *, directory='synthetic-decision'):
    request = campaign.decision_request(root, experiment, action, proposed)
    destination = root / directory
    destination.mkdir()
    write(destination / 'judgment.json', {
        'context_sha256': authority.digest(authority.encoded(request['decision_context'])),
        'decision': 'APPLY', 'rationale': 'Synthetic fixture selects this existing bounded question.',
        'transition': request['transition'], 'reconsideration': 'Revisit with a changed valid evidence base.'})
    write(destination / 'review.json', {'verdict': 'APPROVE', 'rationale': 'Synthetic opposing judgment review.',
         'judgment_sha256': campaign.sha(destination / 'judgment.json')})
    actor = {'run_id': 'synthetic-author-001', 'family_effective': 'codex',
             'model_used': 'synthetic-codex', 'exit_class': 'ok'}
    reviewer = {'run_id': 'synthetic-review-001', 'family_effective': 'claude',
                'model_used': 'synthetic-claude', 'exit_class': 'ok'}
    authority.seal(root, destination, action=action, subject=request['subject'],
                   bindings=request['bindings'], author=actor, reviewer=reviewer)
    return destination / 'decision.json'


def test_apply_adoption_is_separate_attributed_and_duplicate_safe(root):
    proposed = proposal(root)
    exp = campaign.experiment_root(root, 'P001')
    originals = {p: p.read_bytes() for p in [exp / 'investigator_decision.json', exp / 'run.py',
                 proposed / 'receipt.json', proposed / 'request.json']}
    decision = judgment(root, 'P001', 'approve_probe', proposed)
    receipt = lifecycle.apply_decision(root, 'P001', 'approve_probe', decision, proposed)
    assert receipt['actor']['model'] == 'synthetic-codex'
    assert receipt['actor']['session_id'] == 'synthetic-author-001'
    assert receipt['transition']['to'] == 'AGENT_ADOPTED'
    assert not receipt['duplicate']
    assert lifecycle.apply_decision(root, 'P001', 'approve_probe', decision, proposed)['duplicate']
    assert campaign.verify_experiment(root, 'P001')['authority'] == 'user_delegated_scientific_judgment'
    assert all(p.read_bytes() == raw for p, raw in originals.items())
    assert len(list((exp / 'delegated_decisions').iterdir())) == 1
    assert not list(root.rglob('HUMAN_APPROVED*'))


def test_changed_proposal_is_refused_before_application(root):
    proposed = proposal(root)
    decision = judgment(root, 'P001', 'approve_probe', proposed)
    (proposed / 'round-1/adoption.proposed.md').write_text('Changed proposal')
    with pytest.raises(ValueError, match='PROPOSAL_ARTIFACT_CHANGED'):
        lifecycle.apply_decision(root, 'P001', 'approve_probe', decision, proposed)
    assert not (campaign.experiment_root(root, 'P001') / 'delegated_decisions').exists()


def test_changed_spec_and_retargeted_decisions_refuse(root):
    proposed = proposal(root)
    decision = judgment(root, 'P001', 'approve_probe', proposed)
    exp = campaign.experiment_root(root, 'P001')
    (exp / 'SPEC.md').write_text('Changed scientific specification')
    with pytest.raises(ValueError, match='binding stale'):
        lifecycle.apply_decision(root, 'P001', 'approve_probe', decision, proposed)
    assert not (exp / 'agent_adoption.json').exists()


def test_interpretation_acceptance_preserves_original_proposal_and_review(root):
    exp = result(root)
    original = {name: (exp / name).read_bytes() for name in (
        'interpretation_receipt.json', 'interpretation.md', 'interpret_review.md',
        'investigator_next_decision.json')}
    decision = judgment(root, 'P001', 'accept_interpretation')
    receipt = lifecycle.apply_decision(root, 'P001', 'accept_interpretation', decision)
    assert receipt['transition']['to'] == 'AGENT_ACCEPTED'
    assert (exp / 'agent_interpretation_acceptance.json').is_file()
    assert all((exp / name).read_bytes() == raw for name, raw in original.items())
    assert json.loads((exp / 'investigator_next_decision.json').read_text())['status'] == 'PROPOSAL_ONLY'


def test_followup_needs_reviewed_predecessor_and_stays_inside_three_slots(root):
    p001 = campaign.experiment_root(root, 'P001')
    p002 = campaign.experiment_root(root, 'P002')
    shutil.copytree(p001, p002)
    (p002 / 'investigator_decision.json').unlink()
    proposed = proposal(root, 'P002')
    with pytest.raises(FileNotFoundError):
        campaign.decision_request(root, 'P002', 'adopt_followup', proposed)
    result(root)
    decision = judgment(root, 'P002', 'adopt_followup', proposed)
    lifecycle.apply_decision(root, 'P002', 'adopt_followup', decision, proposed)
    checked = campaign.verify_experiment(root, 'P002')
    assert checked['experiment'] == 'P002' and checked['session_id'] == 'synthetic-author-001'
    assert not (p002 / 'investigator_decision.json').exists()
    with pytest.raises(ValueError, match='ENVELOPE'):
        campaign.decision_request(root, 'P004', 'adopt_followup', proposed)
    with pytest.raises(ValueError, match='DISTINCT_ADOPTION'):
        campaign.decision_request(root, 'P002', 'approve_probe', proposed)


def test_partial_application_is_preserved_without_recopy_or_new_authority(root):
    proposed = proposal(root)
    decision = judgment(root, 'P001', 'approve_probe', proposed)
    exp = campaign.experiment_root(root, 'P001')
    directory = exp / 'delegated_decisions' / campaign.sha(decision)
    directory.mkdir(parents=True)
    (directory / 'original-partial').write_text('Preserved interrupted copy')
    with pytest.raises(FileExistsError):
        lifecycle.apply_decision(root, 'P001', 'approve_probe', decision, proposed)
    assert (directory / 'original-partial').read_text() == 'Preserved interrupted copy'
    assert not (exp / 'agent_adoption.json').exists()


@pytest.mark.parametrize('event', [
    {'actor_type': 'human', 'stage': 'PAUSED'},
    {'actor': {'kind': 'human'}, 'action': 'stop'},
    {'actor_type': 'operator', 'stage': 'OPERATOR_HALTED'},
])
def test_human_stop_survives_agent_resume_and_requires_human_release(root, event):
    path = campaign.experiment_root(root, 'P001') / 'lifecycle.jsonl'
    path.write_text(json.dumps(event) + '\n' + json.dumps({'actor_type': 'agent', 'stage': 'RESUMED'}) + '\n')
    with pytest.raises(ValueError, match='HUMAN_STOP_PRESERVED'):
        campaign.require_no_human_stop(root, 'P001')
    with path.open('a') as handle:
        handle.write(json.dumps({'actor_type': 'human', 'stage': 'RESUMED'}) + '\n')
    assert campaign.require_no_human_stop(root, 'P001')['status'] == 'NO_RECORDED_CAMPAIGN_HUMAN_STOP'


def test_agent_pause_proposal_and_pending_approval_do_not_fake_human_stop(root):
    path = campaign.experiment_root(root, 'P001') / 'lifecycle.jsonl'
    path.write_text(json.dumps({'actor_type': 'agent', 'stage': 'PAUSED', 'status': 'PROPOSAL_ONLY'}) + '\n' +
                    json.dumps({'status': 'PATIENT_LAUNCH_OPERATOR_DECISION_PENDING', 'model_mode': 'DISABLED'}) + '\n')
    assert campaign.require_no_human_stop(root, 'P001')['status'] == 'NO_RECORDED_CAMPAIGN_HUMAN_STOP'


def test_stop_after_model_judgment_blocks_before_application(root):
    proposed = proposal(root)
    decision = judgment(root, 'P001', 'approve_probe', proposed)
    exp = campaign.experiment_root(root, 'P001')
    (exp / 'lifecycle.jsonl').write_text(json.dumps({'actor_type': 'human', 'stage': 'STOPPED'}) + '\n')
    with pytest.raises(ValueError, match='HUMAN_STOP_PRESERVED'):
        lifecycle.apply_decision(root, 'P001', 'approve_probe', decision, proposed)
    assert not (exp / 'delegated_decisions').exists()


def test_fresh_grounding_binds_current_delegation_and_preserves_campaign(root):
    original = (root / 'campaigns/isles24-pilot/CAMPAIGN.md').read_bytes()
    context = pipeline.grounding(root, 'P001')
    assert authority.POLICY_PATH in context
    assert authority.DIRECTION_SHA == authority.digest(context['docs/operations/SCIENTIFIC_DELEGATION_20260909.md'].encode())
    assert (root / 'campaigns/isles24-pilot/CAMPAIGN.md').read_bytes() == original
    (root / authority.POLICY_PATH).unlink()
    with pytest.raises(ValueError, match='REGULAR_FILE'):
        pipeline.grounding(root, 'P001')


def test_direct_ci_stage_receives_current_policy_before_adapter(root):
    seen = []
    sc = SimpleNamespace(ROOT=root)
    with patch.dict('os.environ', {'SCOUT_CI': '1'}), patch(
            'orchestrator.actions_runner.system_stage', side_effect=lambda *a: seen.append(a[4])):
        pipeline.system_stage(sc, root, 'codex', 'synthetic', 'Question', ['answer.md'])
    assert 'CURRENT SCIENTIFIC DELEGATION' in seen[0]
    assert 'USER_DELEGATED_SCIENTIFIC_JUDGMENT' in seen[0]



def test_changed_frozen_p001_code_cannot_be_adopted(root):
    proposed = proposal(root)
    (campaign.experiment_root(root, 'P001') / 'run.py').write_text('changed scientific code')
    with pytest.raises(ValueError, match='P001_FROZEN_REVIEW_BINDING'):
        campaign.decision_request(root, 'P001', 'approve_probe', proposed)


def test_malformed_or_symlink_control_refuses_and_other_experiment_stop_is_scoped(root):
    exp = campaign.experiment_root(root, 'P001')
    path = exp / 'lifecycle.jsonl'
    path.write_text('not json')
    with pytest.raises(ValueError):
        campaign.require_no_human_stop(root, 'P001')
    path.write_text(json.dumps({'actor_type': 'human', 'stage': 'STOPPED', 'experiment': 'P002'}) + '\n')
    assert campaign.require_no_human_stop(root, 'P001')['status'] == 'NO_RECORDED_CAMPAIGN_HUMAN_STOP'
    elsewhere = root / 'control-copy.jsonl'
    path.rename(elsewhere)
    path.symlink_to(elsewhere)
    with pytest.raises(ValueError, match='REGULAR_FILE'):
        campaign.require_no_human_stop(root, 'P001')
