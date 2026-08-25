"""Deterministic per-idea state materialization (Patch 2a, part 1).

ideas/NNN/state.json is a VIEW, never an authority (round-4 audit). The
authorities are the append-only ledger events and the on-disk contract /
approval artifacts; this module derives the view from them and nothing
else. The governing invariant, enforced in CI via `scout.py state-verify`:

    delete state.json, regenerate it, and obtain exactly the committed
    bytes.

Consequences of that invariant, deliberately accepted:
  * No wall-clock timestamps. The audit's sketch included
    materialization.generated_at; a clock breaks byte-identical
    regeneration, so the event WATERMARK (sha256 over this idea's own raw
    ledger lines, in file order) carries recency instead. Same watermark,
    same bytes, always.
  * Nothing reads state.json yet. Part 1 only introduces the generated
    artifact plus its invariant; consumers flip to it in a later 2a part,
    after the invariant has held in CI.

The module is root-parametric and dependency-injected (charter resolver,
contract hasher) so it has no import cycle with scout.py and tests run
against throwaway fixture repos. The single-id latest-wins merge below
mirrors orchestrator/ledger.load() semantics (tombstones excluded, empty
values never overwrite) on purpose; if load() semantics ever change, change
_merged_current in the same commit.
"""

import hashlib
import json
import re
from pathlib import Path

SCHEMA_VERSION = 1
MATERIALIZER_VERSION = 1


def _idea_ledger_lines(root: Path, ledger_id: str) -> list[str]:
    """Raw ledger lines (verbatim) whose record names this ledger_id,
    in file order. Verbatim lines make the watermark sensitive to any
    change in this idea's history and blind to everyone else's."""
    ledger = Path(root) / 'ledger.jsonl'
    if not ledger.exists():
        return []
    out = []
    for ln in ledger.read_text().splitlines():
        ln = ln.strip()
        if not ln:
            continue
        try:
            rec = json.loads(ln)
        except json.JSONDecodeError:
            raise SystemExit(
                'LEDGER HEALTH FAILURE: malformed line in ledger.jsonl; '
                'restore it from git history before materializing state.')
        if rec.get('ledger_id') == ledger_id:
            out.append(ln)
    return out


def _merged_current(lines: list[str]) -> dict:
    """Single-id latest-wins merge, mirroring ledger.load(): tombstoned
    (status INVALID_ROW) event chains are excluded from current state;
    empty values never overwrite earlier substance."""
    merged: dict = {}
    tombstoned = False
    for ln in lines:
        rec = json.loads(ln)
        if rec.get('status') == 'INVALID_ROW':
            tombstoned = True
        for k, v in rec.items():
            if v not in (None, ''):
                merged[k] = v
    return {} if tombstoned else merged


def _approval(idea_dir: Path) -> dict | None:
    marker = idea_dir / 'HUMAN_APPROVED_PROBE'
    if not marker.exists():
        return None
    m = re.search(r'contract_blob:\s*([0-9a-f]{40})', marker.read_text())
    return {'contract_blob': m.group(1) if m else None}


def materialize(idea_no: str, root: Path, *, charter_resolver,
                contract_hasher, registry_resolver=None) -> dict:
    """Build the state dict for ideas/<idea_no> from authorities only.
    charter_resolver(idea_dir) and contract_hasher(idea_dir) are injected
    from scout.py (charter_for_target / _contract_hash) so charter and
    blob semantics have exactly one implementation."""
    root = Path(root)
    idea_dir = root / 'ideas' / idea_no
    ledger_id = f'idea-{idea_no}'
    lines = _idea_ledger_lines(root, ledger_id)
    cur = _merged_current(lines)
    contract_blob = contract_hasher(idea_dir)
    approval = _approval(idea_dir)
    if approval is not None:
        approval['stale'] = bool(contract_blob) and \
            approval.get('contract_blob') != contract_blob
    watermark = hashlib.sha256(
        ('\n'.join(lines)).encode('utf-8')).hexdigest() if lines else None
    artifact_files = sorted(
        p.name for p in idea_dir.iterdir()
        if p.is_file() and p.suffix in ('.md', '.json', '.yaml', '.csv')
        and p.name != 'state.json' and not p.name.startswith('prompt_')
        and not p.name.startswith('log_')) if idea_dir.exists() else []
    return {
        'schema_version': SCHEMA_VERSION,
        'idea_id': ledger_id,
        'idea_no': idea_no,
        'charter': charter_resolver(idea_dir),
        'title': cur.get('title'),
        'claim': cur.get('claim'),
        'status': cur.get('status'),
        'scrutiny': cur.get('scrutiny'),
        'kill_code': cur.get('kill_code'),
        'contract_blob': contract_blob,
        'approval': approval,
        'artifact_files': artifact_files,
        'registry': registry_resolver(idea_no) if registry_resolver else None,
        'pending_decisions': [],    # 2b: decision receipts
        'corrections': [],
        'materialization': {
            'materializer_version': MATERIALIZER_VERSION,
            'event_count': len(lines),
            'source_event_watermark': watermark,
        },
    }


def render(state: dict) -> str:
    """Canonical byte form: sorted keys, two-space indent, trailing
    newline. Byte-identical regeneration depends on this being the only
    serializer."""
    return json.dumps(state, sort_keys=True, indent=2) + '\n'


def write_state(idea_no: str, root: Path, **kw) -> Path:
    p = Path(root) / 'ideas' / idea_no / 'state.json'
    p.write_text(render(materialize(idea_no, root, **kw)))
    return p


def verify_state(idea_no: str, root: Path, **kw) -> list[str]:
    """Regenerate and compare bytes to the committed file. Empty list =
    invariant holds. This is the CI check the audit asked for."""
    p = Path(root) / 'ideas' / idea_no / 'state.json'
    if not p.exists():
        return [f'{p} missing (run state-materialize)']
    want = render(materialize(idea_no, root, **kw))
    have = p.read_text()
    if want != have:
        return [f'{p} is not a faithful materialization of the ledger '
                '(regenerated bytes differ); state.json is a view, never '
                'an authority -- re-run state-materialize, never hand-edit']
    return []
