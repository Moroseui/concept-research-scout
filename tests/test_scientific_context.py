"""Current shared rules must reach both actual transport paths with bound receipts."""
import json
from pathlib import Path
import shutil
from types import SimpleNamespace

import pytest

from orchestrator import scientific_authority as authority
from orchestrator import campaign_pipeline as pipeline

SOURCE = Path(__file__).resolve().parents[1]


@pytest.fixture
def root(tmp_path, monkeypatch):
    monkeypatch.delenv('SCOUT_CHANGE_REQUEST_STORE', raising=False)
    manifest = json.loads((SOURCE / 'configs/scientific-operating-context.json').read_text())
    for name in [*manifest['documents'], authority.POLICY_PATH,
                 'docs/operations/SCIENTIFIC_DELEGATION_20260909.md',
                 'configs/scientific-operating-context.json', 'configs/pilot/agents-unattended.toml']:
        path = tmp_path / name
        path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(SOURCE / name, path)
    return tmp_path


@pytest.mark.parametrize('family', ['codex', 'claude'])
@pytest.mark.parametrize('ci', [False, True])
def test_both_roles_receive_same_current_policy_on_local_and_ci_transport(root, monkeypatch, family, ci):
    out = root / 'stage'
    out.mkdir()
    seen = []
    sc = SimpleNamespace(ROOT=root, STATE=root / 'state.json')
    if ci:
        monkeypatch.setenv('SCOUT_CI', '1')
        def hosted(sc, directory, actual_family, stage, body, names):
            seen.append(body)
            return {'family_effective': actual_family}
        monkeypatch.setattr('orchestrator.actions_runner.system_stage', hosted)
    else:
        monkeypatch.delenv('SCOUT_CI', raising=False)
        def run_agent(prompt, actual_family, **kwargs):
            seen.append(prompt.read_text())
            (sc.ROOT / 'answer.md').write_text('synthetic stage output')
            record = {'family_effective': actual_family, 'run_id': 'synthetic0001',
                      'prompt_sha256': authority.digest(prompt.read_bytes())}
            (sc.ROOT / 'stage_provenance.jsonl').write_text(json.dumps(record) + '\n')
        sc.run_agent = run_agent
    pipeline.system_stage(sc, out, family, 'context_check', 'Bound stage question', ['answer.md'])
    assert sc.ROOT == root
    supplied = json.loads((out / 'context_context_check.json').read_text())
    current = supplied['shared_policy']['operating_context']
    assert current['manifest']['version'] == '20260909-continuation-v2'
    assert supplied['family'] == family
    assert supplied['role'] == current['manifest']['roles'][family]
    assert 'CURRENT SCIENTIFIC DELEGATION' in seen[0]
    assert (authority.encoded(supplied) + b'\n').decode() in seen[0]
    assert 'Pending review must never silently become approval.' in seen[0]
    if not ci:
        original = (out / 'prompt_context_check.md').read_bytes()
        record = json.loads((out / 'stage_provenance.jsonl').read_text())
        assert record['prompt_sha256'] == authority.digest(original)


def test_changed_directive_refuses_before_any_delivery(root):
    path = root / 'docs/operations/SHARED_WORKFLOW_CLARIFICATION_20260909.md'
    path.write_text(path.read_text() + '\nUnbound alteration')
    with pytest.raises(ValueError, match='OPERATING_CONTEXT_CHANGED'):
        authority.stage_context(root, root, 'codex', 'context_check')
    assert not (root / 'context_context_check.json').exists()


def test_completed_context_artifact_cannot_be_silently_replaced(root):
    authority.stage_context(root, root, 'codex', 'context_check')
    original = (root / 'context_context_check.json').read_bytes()
    with pytest.raises(FileExistsError):
        authority.stage_context(root, root, 'claude', 'context_check')
    assert (root / 'context_context_check.json').read_bytes() == original
