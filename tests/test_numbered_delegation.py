"""Real authority verification across numbered gates; no model or scientific runs."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil

import pytest
import scout
from orchestrator import scientific_authority as authority

SOURCE = Path(__file__).resolve().parents[1]


@pytest.fixture
def lane(tmp_path, monkeypatch):
    for name in (authority.POLICY_PATH, 'docs/operations/SCIENTIFIC_DELEGATION_20260909.md'):
        p = tmp_path / name
        p.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(SOURCE / name, p)
    d = tmp_path / 'ideas/047'
    d.mkdir(parents=True)
    (d / 'idea_card.json').write_text('{"title":"Synthetic descriptive study"}')
    (d / 'probe_contract.yaml').write_text('idea_id: idea-047\nrequired_outputs:\n  - resolved_config.json\n')
    (d / 'feasibility.md').write_text('Existing synthetic input, no resource expansion.\n')
    (tmp_path / 'ledger.jsonl').write_text(json.dumps({'ledger_id': 'idea-047', 'status': 'ACTIVE'}) + '\n')
    monkeypatch.setattr(scout, 'ROOT', tmp_path)
    monkeypatch.setattr(scout.ledger_mod, 'ROOT', tmp_path)
    monkeypatch.setattr(scout.ledger_mod, 'LEDGER', tmp_path / 'ledger.jsonl')
    monkeypatch.setattr(scout.ledger_mod, 'DIGEST', tmp_path / 'evidence/ledger_digest.md')
    monkeypatch.setattr(scout, '_require_clean_tree', lambda *_: None)
    commits = []
    monkeypatch.setattr(scout, '_commit_all', commits.append)
    return tmp_path, d, commits


def decision(root, *, action, bindings, before='ACTIVE', after='PAUSED', name='decision'):
    directory = root / 'ideas/047' / name
    directory.mkdir()
    context = authority.decision_context(root, action=action, subject='idea:047', bindings=bindings)
    judgment = {'context_sha256': authority.digest(authority.encoded(context)),
                'decision': 'APPLY', 'rationale': 'The original reviewed evidence supports this bounded transition.',
                'transition': {'from': before, 'to': after},
                'reconsideration': 'Consider a linked question if new relevant evidence arrives; retain the completed job.'}
    (directory / 'judgment.json').write_bytes(authority.encoded(judgment) + b'\n')
    (directory / 'review.json').write_bytes(authority.encoded({'verdict': 'APPROVE',
        'judgment_sha256': authority.digest((directory / 'judgment.json').read_bytes()),
        'rationale': 'The exact input scope and reversible transition are supported.'}) + b'\n')
    author = {'run_id': 'author047001', 'family_effective': 'codex', 'model_used': 'gpt-6-astra', 'exit_class': 'ok'}
    reviewer = {'run_id': 'review047001', 'family_effective': 'claude', 'model_used': 'claude-fable-5', 'exit_class': 'ok'}
    authority.seal(root, directory, action=action, subject='idea:047', bindings=bindings,
                   author=author, reviewer=reviewer)
    return directory / 'decision.json'


def interpreted(lane):
    root, d, _ = lane
    for name, text in [('interpretation.md', 'Original synthetic finding.\n'),
                       ('interpret_review.md', 'Original review.\n```json\n{"verdict":"APPROVE"}\n```\n'),
                       ('decision.md', 'Original proposed pause, preserved verbatim.\n')]:
        (d / name).write_text(text)
    b = root / 'probes/047/results/results_synthetic'
    b.mkdir(parents=True)
    (b / 'summary.json').write_text('{"idea_id":"idea-047","status":"DONE"}')
    (b / 'resolved_config.json').write_text(json.dumps({'contract_blob': scout._contract_hash(d)}))
    (b / 'provenance.json').write_text('{"seed":1}')
    return b


def test_agent_accepts_existing_review_once_without_human_attribution(lane):
    root, d, commits = lane
    b = interpreted(lane)
    original = {n: (d / n).read_bytes() for n in ('interpretation.md', 'interpret_review.md', 'decision.md')}
    path = decision(root, action='accept_interpretation', bindings=scout.interpretation_decision_bindings(47, b))
    args = argparse.Namespace(idea=47, status='PAUSED', agent_decision=str(path))
    scout.cmd_ratify_interpretation(args)
    once = (root / 'ledger.jsonl').read_bytes()
    scout.cmd_ratify_interpretation(args)
    assert (root / 'ledger.jsonl').read_bytes() == once
    event = json.loads(once.splitlines()[-1])
    assert event['kind'] == 'AGENT_INTERPRETATION_ACCEPTED'
    assert event['actor']['session_id'] == 'author047001'
    assert event['status'] == 'PAUSED' and 'operator ratified' not in event['notes']
    assert not (d / 'HUMAN_APPROVED_PROBE').exists()
    assert original == {n: (d / n).read_bytes() for n in original}
    receipt = json.loads((d / 'reviewed_context_receipt.json').read_text())
    assert receipt['status'] == 'AGENT_REVIEWED_NOT_HUMAN_RATIFIED'
    assert receipt['proposal_sha256'] == hashlib.sha256(original['decision.md']).hexdigest()
    assert scout.state_mod.verify_state('047', root, **scout._state_kwargs()) == []
    assert len(commits) == 1


def test_stale_result_cannot_apply_reviewed_decision(lane):
    root, d, commits = lane
    b = interpreted(lane)
    path = decision(root, action='accept_interpretation', bindings=scout.interpretation_decision_bindings(47, b))
    (b / 'summary.json').write_text('{"idea_id":"idea-047","status":"DONE","changed":true}')
    before = (root / 'ledger.jsonl').read_bytes()
    with pytest.raises(SystemExit, match='DELEGATED_SCIENTIFIC_DECISION_REFUSED'):
        scout.cmd_ratify_interpretation(argparse.Namespace(idea=47, status='PAUSED', agent_decision=str(path)))
    assert (root / 'ledger.jsonl').read_bytes() == before and not commits


def test_agent_probe_reference_is_current_and_human_marker_untouched(lane, monkeypatch):
    root, d, commits = lane
    marker = d / 'HUMAN_APPROVED_PROBE'
    marker.write_text('Historical human approval\ncontract_blob: ' + 'a' * 40 + '\n')
    original = marker.read_bytes()
    path = decision(root, action='approve_probe', bindings=scout.reg_mod.agent_probe_bindings('047', root),
                    before='UNAPPROVED', after='APPROVED')
    scout.approve_probe(argparse.Namespace(idea=47, agent_decision=str(path)))
    assert marker.read_bytes() == original
    approved = scout.reg_mod.agent_probe_approval('047', root)
    assert approved['actor']['kind'] == 'agent'
    assert scout.state_mod._approval(d)['actor_type'] == 'agent'
    assert approved['bindings']['contract_blob'] in scout.reg_mod._attested_hashes(d)
    monkeypatch.setattr(scout, 'write_prompt', lambda *_: root / 'unused-prompt')
    invoked = []
    monkeypatch.setattr(scout, 'run_agent', lambda *a, **kw: invoked.append(kw['stage']))
    monkeypatch.setattr(scout, '_check_scope', lambda *_: None)
    monkeypatch.setattr(scout, '_require_artifact', lambda *_: None)
    scout.run_stage(argparse.Namespace(stage='probe-code', idea=47, agent=None))
    assert invoked == ['probe-code']
    (d / 'probe_contract.yaml').write_text('idea_id: idea-047\nchanged: true\n')
    with pytest.raises((ValueError, SystemExit), match='AUTHORITY|CONTEXT|blocked'):
        scout.run_stage(argparse.Namespace(stage='probe-code', idea=47, agent=None))
    assert invoked == ['probe-code']


def test_reviewed_resume_preserves_human_stop_and_deduplicates(lane):
    root, d, commits = lane
    scout.ledger_mod.append({'ledger_id': 'idea-047', 'status': 'PAUSED', 'actor_type': 'agent'})
    path = decision(root, action='resume_science', bindings=scout.resume_science_bindings(47),
                    before='PAUSED', after='ACTIVE')
    args = argparse.Namespace(idea=47, status='ACTIVE', agent_decision=str(path))
    scout.resume_science(args)
    once = (root / 'ledger.jsonl').read_bytes()
    scout.resume_science(args)
    assert (root / 'ledger.jsonl').read_bytes() == once and len(commits) == 1
    scout.ledger_mod.append({'ledger_id': 'idea-047', 'status': 'PAUSED', 'actor_type': 'human', 'human_stop': True})
    path = decision(root, action='resume_science', bindings=scout.resume_science_bindings(47),
                    before='PAUSED', after='ACTIVE', name='second-decision')
    before = (root / 'ledger.jsonl').read_bytes()
    with pytest.raises(SystemExit, match='HUMAN_STOP_PRESERVED'):
        scout.resume_science(argparse.Namespace(idea=47, status='ACTIVE', agent_decision=str(path)))
    with pytest.raises(ValueError, match='HUMAN_STOP_PRESERVED'):
        scout.ledger_mod.append({'ledger_id': 'idea-047', 'actor_type': 'agent', 'status': 'ACTIVE'})
    assert (root / 'ledger.jsonl').read_bytes() == before


def test_model_kill_is_reversible_and_duplicate_observation_is_not_appended(lane):
    root, d, _ = lane
    (d / 'consensus.md').write_text('```json\n{"verdict":"KILL","kill_code":"DATA_ACCESS","unblock":"New public evidence resolving access."}\n```\n')
    stage = {'stage': 'debate_summary', 'family_effective': 'claude', 'model_used': 'claude-fable-5',
             'run_id': 'debate047001', 'exit_class': 'ok'}
    (d / 'stage_provenance.jsonl').write_text(json.dumps(stage) + '\n')
    scout._apply_consensus_verdict(47)
    once = (root / 'ledger.jsonl').read_bytes()
    scout._apply_consensus_verdict(47)
    assert (root / 'ledger.jsonl').read_bytes() == once
    event = json.loads(once.splitlines()[-1])
    assert event['status'] == 'PAUSED' and event['original_verdict'] == 'KILL'
    assert event['actor']['session_id'] == 'debate047001'
    assert event['policy']['version'] == authority.POLICY_VERSION
    assert event['reconsideration'] == 'New public evidence resolving access.'
    assert 'PRESERVED NEGATIVE/DEFERRAL' in scout._dossier_entry_idea(d, scout.ledger_mod.load())
    with pytest.raises(ValueError, match='AGENT_PERMANENT_REJECTION_FORBIDDEN'):
        scout.ledger_mod.append({'ledger_id': 'idea-047', 'actor_type': 'agent', 'status': 'REJECTED'})


def test_scientific_unblock_is_bound_and_replayed_revision_does_not_run(lane, monkeypatch):
    root, d, _ = lane
    scout.ledger_mod.append({'ledger_id': 'idea-047', 'actor_type': 'agent', 'status': 'PAUSED'})
    (d / 'consensus.md').write_text('```json\n{"verdict":"REVISE","unblock":"New scoped evidence reviewed."}\n```\n')
    path = decision(root, action='resume_science', bindings=scout.resume_science_bindings(47),
                    before='PAUSED', after='ACTIVE')
    invoked = []
    monkeypatch.setattr(scout, 'write_prompt', lambda *_: root / 'unused-prompt')
    monkeypatch.setattr(scout, 'run_agent', lambda *a, **kw: invoked.append(kw['stage']))
    monkeypatch.setattr(scout, '_check_scope', lambda *_: None)
    monkeypatch.setattr(scout, '_require_artifact', lambda *_: None)
    args = argparse.Namespace(stage='revise', idea=47, agent=None, agent_decision=str(path))
    scout.run_stage(args)
    assert scout._pending_human_unblock(d) is None
    assert not (d / 'unblock_ack.txt').exists()
    scout.run_stage(args)
    assert invoked == ['revise']
    (d / 'consensus.md').write_text('```json\n{"verdict":"REVISE","unblock":"A different unresolved condition."}\n```\n')
    assert scout._pending_human_unblock(d) == 'A different unresolved condition.'
