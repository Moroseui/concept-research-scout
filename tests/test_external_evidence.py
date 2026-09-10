"""Offline contract tests: synthetic artifacts and fake receipted system stages only."""
import hashlib
import json
from pathlib import Path
import re
import shutil
from types import SimpleNamespace
import zipfile

import pytest

from orchestrator import external_evidence as external
from orchestrator import research_context as context
from orchestrator import scientific_authority as authority
from orchestrator.drive_science_intake import external_artifact, external_collected
from orchestrator.notebook_evidence import preserve_external

ROOT = Path(__file__).resolve().parents[1]


def dump(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(external.encoded(value) + b'\n')
    path.chmod(0o600)


@pytest.fixture
def fixture(tmp_path, monkeypatch):
    tmp_path.chmod(0o700)
    root = tmp_path / 'repo'
    root.mkdir(mode=0o700)
    for name in (authority.POLICY_PATH, 'docs/operations/SCIENTIFIC_DELEGATION_20260909.md'):
        target = root / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / name, target)
    notebook = tmp_path / 'supplied.ipynb'
    value = {'nbformat': 4, 'cells': [{'cell_type': 'code', 'source': ['print("aggregate")\n'],
        'execution_count': None, 'outputs': [
            {'output_type': 'stream', 'text': 'aggregate saved result; n=30\n'},
            {'output_type': 'stream', 'text': 'sub-strokecase0001 PRIVATE_CASE_VALUE\n'},
            {'output_type': 'display_data', 'data': {'text/html': '<table>private original</table>'}}]}]}
    dump(notebook, value)
    run_id = 'manual-sprint-20260909'
    profile = dict(external.PROFILES[run_id], notebook_sha256=external.digest(notebook.read_bytes()),
                   aggregate_streams=[(0, 0)])
    monkeypatch.setitem(external.PROFILES, run_id, profile)
    monkeypatch.setattr(external, 'charter_context',
        lambda root, charter: {'charter.txt': charter + ' independent charter context; no other scores'})
    intake = tmp_path / 'intake'
    external.prepare(notebook, intake, run_id)
    return SimpleNamespace(root=root, ROOT=root, notebook=notebook, intake=intake, run_id=run_id)


class Stages:
    def __init__(self, bad_review=False, defer=False, revise_once=False):
        self.calls = []
        self.bad_review = bad_review
        self.defer = defer
        self.revise_once = revise_once

    def __call__(self, sc, directory, family, stage, body, names):
        self.calls.append({'family': family, 'stage': stage, 'body': body})
        assert 'PRIVATE_CASE_VALUE' not in body
        if family == 'codex':
            match = re.search(r'expected context_sha256 is ([0-9a-f]{64})', body)
            transition, _ = json.JSONDecoder().raw_decode(body.split('exact transition is ', 1)[1])
            if self.defer:
                transition['to'] = 'DEFERRED'
            dump(directory / 'judgment.json', {'decision': 'DEFER' if self.defer else 'APPLY', 'rationale': 'Qualified model judgment.',
                'transition': transition, 'reconsideration': 'Reconsider with missing originals.',
                'context_sha256': match.group(1)})
            if 'interpretation.md' in names:
                (directory / 'interpretation.md').write_text(
                    'External exploratory saved aggregates only; 69/30 reused development split. '
                    'Missing originals limit reproduction. Next: inspect preprocessing differences.')
            if 'consideration.json' in names:
                charter = re.search(r'\nCHARTER: ([a-z0-9-]+)', body).group(1)
                dump(directory / 'consideration.json', {'charter': charter, 'disposition': 'USED',
                    'finding_references': ['saved stream cell 0 output 0'],
                    'limitations': ['Reused 30 cases'], 'contradictions': [],
                    'affected_questions': ['How does preprocessing affect comparison?'],
                    'rationale': 'A qualified context update.', 'next_action': 'Assess a linked preprocessing comparison.'})
        else:
            judgment_sha = re.search(r'EXACT judgment_sha256: ([0-9a-f]{64})', body).group(1)
            artifacts, _ = json.JSONDecoder().raw_decode(body.split('EXACT artifact_sha256: ', 1)[1])
            verdict = 'REVISE' if self.revise_once and sum(c['family'] == 'claude' for c in self.calls) == 1 else 'APPROVE'
            dump(directory / 'review.json', {'verdict': verdict, 'rationale': 'Independent review of cited evidence.',
                'judgment_sha256': '0' * 64 if self.bad_review else judgment_sha, 'artifact_sha256': artifacts})
        prompt = 'Synthetic test fixture, no model invocation.\n' + body
        path = directory / ('prompt_' + stage + '.md')
        path.write_text(prompt)
        value = {'family_effective': family, 'model_used': 'gpt-6-astra' if family == 'codex' else 'claude-fable-5',
            'exit_class': 'ok', 'run_id': 'fixture-' + str(len(self.calls)).zfill(6), 'stage': stage,
            'prompt_sha256': external.digest(prompt.encode())}
        dump(directory / 'stage_provenance.jsonl', value)
        return value


def test_intake_dedup_and_exact_projection(fixture):
    first = (fixture.intake / 'receipt.json').read_bytes()
    result = external.prepare(fixture.notebook, fixture.intake, fixture.run_id)
    assert result['origin'] == external.ORIGIN
    assert (fixture.intake / 'receipt.json').read_bytes() == first
    assert 'PRIVATE_CASE_VALUE' not in (fixture.intake / 'model-evidence.json').read_text()
    assert 'PRIVATE_CASE_VALUE' in (fixture.intake / 'notebook/cell-000-output-001.json').read_text()
    assert json.loads((fixture.intake / 'notebook/receipt.json').read_text())['saved_output_count'] == 3


def test_rebound_projection_cannot_change_original_evidence(fixture):
    path = fixture.intake / 'model-evidence.json'
    data = json.loads(path.read_text())
    data['code'] = 'changed source'
    dump(path, data)
    receipt_path = fixture.intake / 'receipt.json'
    receipt = json.loads(receipt_path.read_text())
    receipt['projection_sha256'] = external.digest(path.read_bytes())
    dump(receipt_path, receipt)
    with pytest.raises(ValueError, match='MODEL_PROJECTION_CHANGED'):
        external.checked_intake(fixture.intake)


def test_repeated_supplied_identity_change_refuses(fixture):
    fixture.notebook.write_text('{}')
    with pytest.raises(ValueError, match='NOTEBOOK_IDENTITY_CHANGED'):
        external.prepare(fixture.notebook, fixture.intake, fixture.run_id)


def test_formal_acceptance_two_charters_and_replay(fixture):
    stages = Stages()
    receipt = external.interpret(fixture, fixture.intake, stage_runner=stages)
    external.register_interpretation(fixture.root, receipt)
    before = len(stages.calls)
    assert external.interpret(fixture, fixture.intake, stage_runner=stages) == receipt
    assert len(stages.calls) == before
    for charter in ('isles24', 'isles24-prediction'):
        considered = external.consider(fixture, fixture.run_id, charter, stage_runner=stages)
        context.register_consideration(fixture.root, fixture.run_id, charter, considered)
        assert external.consider(fixture, fixture.run_id, charter, stage_runner=stages) == considered
        entry = context.evidence_context(fixture.root, charter)['entries'][0]
        assert entry['consideration']['record']['next_action']
        assert entry['exposure_history'] == external.EXPOSURE
    external.register_interpretation(fixture.root, receipt)
    assert len(stages.calls) == 6
    assert context.evidence_context(fixture.root, 'isles24', blind=True)['entries'] == []
    assert external.consider(fixture, fixture.run_id, 'isles24', blind=True)['model_calls'] == 0


def test_uncertain_stage_is_not_automatically_retried(fixture):
    stages = Stages()
    destination = fixture.root / 'evidence/external/test-run/stage'
    destination.mkdir(parents=True)
    intent = {'family': 'codex', 'stage': 'external_author', 'body_sha256': external.digest(b'body'),
              'names': ['interpretation.md']}
    dump(destination / 'intent.json', intent)
    with pytest.raises(ValueError, match='UNCERTAIN_RECONCILE_NO_RETRY'):
        external._stage_once(fixture, destination, 'codex', 'external_author', 'body', ['interpretation.md'], stages)
    assert stages.calls == []


def test_completed_original_stage_recovers_without_model_call(fixture):
    stages = Stages()
    receipt = external.interpret(fixture, fixture.intake, stage_runner=stages)
    author = fixture.root / Path(receipt['interpretation']).parent
    (author / 'returned.provenance.json').unlink()
    intent = json.loads((author / 'intent.json').read_text())
    body = stages.calls[0]['body']
    count = len(stages.calls)
    value = external._stage_once(fixture, author, 'codex', 'external_author', body, intent['names'], stages)
    assert value['run_id']
    assert len(stages.calls) == count
    assert json.loads((author / 'recovery.json').read_text())['model_calls'] == 0


def test_human_stop_and_resource_bound_preserved(fixture):
    stages = Stages()
    (fixture.root / 'HUMAN_STOP').write_text('Deliberate stop.')
    with pytest.raises(ValueError, match='HUMAN_STOP'):
        external.interpret(fixture, fixture.intake, stage_runner=stages)
    assert stages.calls == []
    (fixture.root / 'HUMAN_STOP').unlink()
    with pytest.raises(ValueError, match='REVIEW_ROUND_BOUND'):
        external.interpret(fixture, fixture.intake, max_rounds=3, stage_runner=stages)
    assert stages.calls == []


def test_review_must_bind_the_exact_original_judgment(fixture):
    stages = Stages(bad_review=True)
    with pytest.raises(ValueError, match='EXACT_OPPOSING_REVIEW_REQUIRED'):
        external.interpret(fixture, fixture.intake, stage_runner=stages)
    assert len(stages.calls) == 2
    assert not (fixture.root / 'evidence/external' / fixture.run_id / 'interpretation/receipt.json').exists()


def test_catalog_rejects_changed_reviewed_interpretation(fixture):
    stages = Stages()
    receipt = external.interpret(fixture, fixture.intake, stage_runner=stages)
    external.register_interpretation(fixture.root, receipt)
    (fixture.root / receipt['interpretation']).write_text('Changed.')
    with pytest.raises(ValueError, match='CONTEXT_BINDING_CHANGED'):
        context.evidence_context(fixture.root, 'isles24')


def test_archive_traversal_refused_before_extraction(tmp_path):
    path = tmp_path / 'figures.zip'
    with zipfile.ZipFile(path, 'w') as archive:
        archive.writestr('../escape', 'not extracted')
    path.chmod(0o600)
    with pytest.raises(ValueError, match='ARCHIVE_UNSAFE_MEMBER'):
        external_artifact(path, external.digest(path.read_bytes()))
    assert not (tmp_path.parent / 'escape').exists()


def test_external_drive_receipt_binding_is_specific(tmp_path):
    directory = tmp_path / 'external-request-01'
    directory.mkdir()
    raw = b'bounded original'
    (directory / 'original').write_bytes(raw)
    (directory / 'original').chmod(0o600)
    expected = external.digest(raw)
    dump(directory / 'receipt.json', {'status': 'PRIVATE_ORIGINAL_COLLECTED', 'sha256': expected,
         'bytes': len(raw), 'alias': 'external-result', 'implementation_sha256': 'a' * 64})
    result, receipt = external_collected(tmp_path, 'external-result', directory.name,
        implementation_sha256='a' * 64, expected_sha256=expected, maximum=100)
    assert result == raw and receipt['request_id'] == directory.name
    with pytest.raises(ValueError, match='COLLECTION_CHANGED'):
        external_collected(tmp_path, 'external-result', directory.name,
            implementation_sha256='b' * 64, expected_sha256=expected, maximum=100)


def test_model_deferral_preserves_originals_without_repeated_model_calls(fixture):
    stages = Stages(defer=True)
    for _ in range(2):
        with pytest.raises(ValueError, match='SCIENTIFIC_DECISION_DEFERRED'):
            external.interpret(fixture, fixture.intake, stage_runner=stages)
    assert len(stages.calls) == 2
    output = fixture.root / 'evidence/external' / fixture.run_id / 'interpretation'
    assert json.loads((output / 'deferred.json').read_text())['automatic_retry'] is False
    assert not (output / 'receipt.json').exists()


def test_one_bounded_review_revision_preserves_prior_stage_and_replays(fixture):
    stages = Stages(revise_once=True)
    result = external.interpret(fixture, fixture.intake, stage_runner=stages)
    assert len(stages.calls) == 4
    assert 'round-2' in result['interpretation']
    assert (fixture.root / 'evidence/external' / fixture.run_id / 'interpretation/round-1/author/interpretation.md').exists()
    assert external.interpret(fixture, fixture.intake, stage_runner=stages) == result
    assert len(stages.calls) == 4
