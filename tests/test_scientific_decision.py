"""Decision recovery must consume original stages, never repeat uncertain work."""
import json
from pathlib import Path
import shutil
from types import SimpleNamespace

import pytest

from orchestrator import scientific_authority as authority
from orchestrator import scientific_decision as decisions


@pytest.fixture
def run(tmp_path):
    tmp_path.chmod(0o700)
    source = Path(__file__).resolve().parents[1]
    for name in (authority.POLICY_PATH, 'docs/operations/SCIENTIFIC_DELEGATION_20260909.md'):
        path = tmp_path / name
        path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source / name, path)
    kwargs = dict(action='accept_interpretation', subject='idea:047',
                  bindings={'interpretation_sha256': 'a' * 64},
                  evidence={'interpretation.md': 'Completed descriptive experiment; uncertainty remains.'},
                  request='Decide whether to accept the reviewed interpretation and pause the completed study.',
                  output=tmp_path / 'decision')
    return SimpleNamespace(ROOT=tmp_path), kwargs


class Stages:
    def __init__(self, verdicts=('APPROVE',), failed_author=False):
        self.calls = []
        self.verdicts = iter(verdicts)
        self.failed_author = failed_author

    def __call__(self, sc, directory, family, stage, body, outputs):
        self.calls.append((family, stage, body))
        if family == 'codex':
            original = json.loads((directory.parent / 'request.json').read_text())
            value = {'context_sha256': original['context_sha256'], 'decision': 'APPLY',
                     'rationale': 'Reviewed evidence supports a reversible disposition.',
                     'transition': {'from': 'ACTIVE', 'to': 'PAUSED'},
                     'reconsideration': 'Reconsider with new evidence or a distinct successor question.'}
        else:
            value = {'verdict': next(self.verdicts), 'rationale': 'Scope and evidence checked.',
                     'judgment_sha256': authority.digest((directory / 'judgment.json').read_bytes())}
        (directory / outputs[0]).write_bytes(authority.encoded(value) + b'\n')
        return {'family_effective': family, 'run_id': f'stage{len(self.calls):06}',
                'model_used': 'gpt-6-astra' if family == 'codex' else 'claude-fable-5',
                'exit_class': 'timeout' if family == 'codex' and self.failed_author else 'ok'}


def test_completed_delivery_recovers_original_without_a_model_call(run):
    sc, kwargs = run
    stages = Stages()
    first = decisions.execute(sc, **kwargs, stage_runner=stages)
    originals = {p: p.read_bytes() for p in kwargs['output'].rglob('*') if p.is_file()}
    second = decisions.execute(sc, **kwargs, stage_runner=stages)
    assert first['decision_sha256'] == second['decision_sha256']
    assert second['recovered_without_model_calls'] and len(stages.calls) == 2
    assert all(p.read_bytes() == raw for p, raw in originals.items())
    assert not first['human_ratification'] and not first['scientific_execution']


def test_changed_delivery_cannot_retarget_or_restart_completed_work(run):
    sc, kwargs = run
    stages = Stages()
    decisions.execute(sc, **kwargs, stage_runner=stages)
    kwargs['evidence'] = {'interpretation.md': 'Different evidence'}
    with pytest.raises(ValueError, match='IDENTITY_CHANGED'):
        decisions.execute(sc, **kwargs, stage_runner=stages)
    assert len(stages.calls) == 2


def test_lost_stage_response_is_preserved_and_not_retried(run):
    sc, kwargs = run
    calls = []
    def lost(sc, directory, family, stage, body, outputs):
        calls.append(stage)
        (directory / 'partial-original.txt').write_text('original incomplete model transport')
        raise TimeoutError('uncertain model stage')
    with pytest.raises(TimeoutError):
        decisions.execute(sc, **kwargs, stage_runner=lost)
    with pytest.raises(ValueError, match='REGULAR_FILE_REQUIRED'):
        decisions.execute(sc, **kwargs, stage_runner=lost)
    assert len(calls) == 1
    assert (kwargs['output'] / 'round-1/partial-original.txt').read_text() == 'original incomplete model transport'
    assert json.loads((kwargs['output'] / 'stopped.json').read_text())['automatic_retry'] is False


def test_one_review_revision_is_autonomous_and_preserves_both_rounds(run):
    sc, kwargs = run
    stages = Stages(('REVISE', 'APPROVE'))
    receipt = decisions.execute(sc, **kwargs, stage_runner=stages)
    assert receipt['round'] == 2 and len(stages.calls) == 4
    assert 'BOUNDED REVISION' in stages.calls[2][2]
    assert json.loads((kwargs['output'] / 'round-1/review.json').read_text())['verdict'] == 'REVISE'
    assert not (kwargs['output'] / 'round-1/decision.json').exists()


def test_revision_limit_stops_without_scientific_dispatch(run):
    sc, kwargs = run
    stages = Stages(('REVISE', 'REVISE'))
    with pytest.raises(ValueError, match='REVISION_LIMIT'):
        decisions.execute(sc, **kwargs, stage_runner=stages)
    assert len(stages.calls) == 4 and not (kwargs['output'] / 'receipt.json').exists()


def test_failed_author_does_not_spend_an_opposing_review(run):
    sc, kwargs = run
    stages = Stages(failed_author=True)
    with pytest.raises(ValueError, match='AUTHOR_STAGE_FAILED'):
        decisions.execute(sc, **kwargs, stage_runner=stages)
    assert len(stages.calls) == 1
