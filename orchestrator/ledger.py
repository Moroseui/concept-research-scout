"""Append-only idea ledger for Concept Research Scout.

Storage: ledger.jsonl at the repo root. One JSON object per line. Records are
never rewritten; an update is a new record with the same ledger_id, and the
latest record wins field-by-field (event-sourced merge). This keeps the file
git-friendly (appends only -> no merge conflicts across cycles) and preserves
full history.

The ledger is the system's institutional memory:
  * every scouted candidate gets a row at scrutiny=SCOUTED, so undebated ideas
    can never masquerade as clean ones;
  * every kill records a kill_code from a controlled taxonomy;
  * `digest()` renders evidence/ledger_digest.md, which is injected into every
    scout prompt -- the kill-code frequency table doubles as the generation-time
    checklist of known failure modes.
"""
from __future__ import annotations
import csv
import json
import re
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LEDGER = ROOT / 'ledger.jsonl'
DIGEST = ROOT / 'evidence' / 'ledger_digest.md'

SCRUTINY_ORDER = ['SCOUTED', 'CRITIQUED', 'DEBATED', 'PROBED']

STATUSES = ['SCOUT_ONLY', 'ACTIVE', 'SHORTLISTED', 'PAUSED', 'REJECTED', 'DONE']

# Controlled kill-reason taxonomy. Grow it deliberately: add a code here when a
# genuinely new failure pattern appears, not per idea.
TAXONOMY = {
    'USE_VS_ASSOCIATION': 'Studies what a model associates with X, not whether it causally uses X.',
    'ANNOTATION_PROVENANCE': 'Inference depends on who assigned labels / what they could see, and that is undocumented or contaminated.',
    'CIRCULARITY': 'The endpoint is a re-encoding of the input or of the thing being tested.',
    'DATA_INSUFFICIENT': 'The subset that actually supports the inference is too small or unreachable.',
    'DATA_ACCESS': 'Required data, checkpoints, or mappings are not obtainable in practice.',
    'EFFECT_UNREACHABLE': 'The claimed effect cannot exceed a published bound / measurement floor.',
    'FREE_BASELINE_WINS': 'A ground-truth-free structural baseline plausibly matches the learned approach.',
    'COMPUTE_INFEASIBLE': 'Cannot be tested inside one compute envelope (one Colab GPU session).',
    'DUPLICATE_PRIOR': 'Already done; no defensible delta to the closest prior work.',
    'NO_TESTABLE_KERNEL': 'No measurable quantity survives translation from the source idea (fiction-track exit).',
    'IDENTIFIABILITY_FAILURE': 'The design cannot separate the claimed mechanism from a co-varying acquisition, protocol, tool, or population factor in any obtainable cohort.',
    'UNCLASSIFIED': 'Kill reason recorded free-text only; classify when pattern recurs.',
}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec='seconds')


def _records() -> list[dict]:
    if not LEDGER.exists():
        return []
    out = []
    for ln in LEDGER.read_text().splitlines():
        ln = ln.strip()
        if not ln:
            continue
        try:
            out.append(json.loads(ln))
        except json.JSONDecodeError:
            continue  # never let one bad line poison the ledger
    return out


def load() -> dict[str, dict]:
    """Latest-wins merge of all records, keyed by ledger_id."""
    merged: dict[str, dict] = {}
    for rec in _records():
        lid = rec.get('ledger_id')
        if not lid:
            continue
        cur = merged.setdefault(lid, {})
        for k, v in rec.items():
            if v not in (None, ''):
                cur[k] = v
    return merged


def append(rec: dict) -> dict:
    rec = dict(rec)
    rec.setdefault('ledger_id', f"unset-{_now()}")
    rec['recorded_at'] = _now()
    kc = rec.get('kill_code')
    if kc and kc not in TAXONOMY:
        raise ValueError(f'Unknown kill_code {kc!r}. Known: {", ".join(sorted(TAXONOMY))}')
    sc = rec.get('scrutiny')
    if sc and sc not in SCRUTINY_ORDER:
        raise ValueError(f'Unknown scrutiny {sc!r}. Known: {", ".join(SCRUTINY_ORDER)}')
    LEDGER.parent.mkdir(parents=True, exist_ok=True)
    with LEDGER.open('a') as f:
        f.write(json.dumps(rec, ensure_ascii=False) + '\n')
    return rec


def raise_scrutiny(ledger_id: str, level: str, note: str = '') -> None:
    """Only ever raises the recorded scrutiny level, never lowers it."""
    cur = load().get(ledger_id, {})
    have = cur.get('scrutiny', 'SCOUTED')
    if SCRUTINY_ORDER.index(level) > SCRUTINY_ORDER.index(have):
        append({'ledger_id': ledger_id, 'scrutiny': level, 'notes': note})


# ---------------------------------------------------------------- migration

_KILL_HINTS = [
    ('annotation provenance', 'ANNOTATION_PROVENANCE'),
    ('same reader', 'CIRCULARITY'),
    ('re-encoding', 'CIRCULARITY'),
    ('too small', 'DATA_INSUFFICIENT'),
    ('not able to obtain', 'DATA_ACCESS'),
    ('association', 'USE_VS_ASSOCIATION'),
    ('baseline', 'FREE_BASELINE_WINS'),
]


def _guess_kill_code(text: str) -> str:
    low = text.lower()
    for hint, code in _KILL_HINTS:
        if hint in low:
            return code
    return 'UNCLASSIFIED'


def _decisions_by_idea() -> dict[str, dict]:
    """Best-effort parse of evidence/decisions.md into per-idea outcomes."""
    path = ROOT / 'evidence' / 'decisions.md'
    out: dict[str, dict] = {}
    if not path.exists():
        return out
    body = path.read_text()
    blocks = re.split(r'^## ', body, flags=re.M)[1:]
    for b in blocks:
        head, _, rest = b.partition('\n')
        m = re.search(r'Idea\s+(\d+)\s+(?:Stage\s*0\s+)?([A-Z]+)', head)
        if not m:
            continue
        idea, verdict = f'{int(m.group(1)):03d}', m.group(2)
        status = {'REJECTED': 'REJECTED', 'PAUSE': 'PAUSED', 'PAUSED': 'PAUSED',
                  'ADVANCE': 'ACTIVE', 'COMPLETE': 'ACTIVE'}.get(verdict)
        note = ' '.join(rest.split())[:400]
        entry = out.setdefault(idea, {})
        if status:
            entry['status'] = status
        entry.setdefault('notes', note)
        if status == 'REJECTED':
            entry['kill_reason'] = note
            entry['kill_code'] = _guess_kill_code(head + ' ' + note)
    return out


def _scrutiny_from_artifacts(d: Path, idea_no: str) -> str:
    if (ROOT / 'probes' / idea_no / 'results').exists():
        return 'PROBED'
    if (d / 'debate.md').exists():
        return 'DEBATED'
    if (d / 'critique.md').exists():
        return 'CRITIQUED'
    return 'SCOUTED'


def migrate(force: bool = False) -> int:
    """Backfill ledger.jsonl from ideas/NNN, portfolio/ideas.csv, decisions.md.

    Idempotent: skips ideas already present unless force=True.
    """
    have = set() if force else set(load())
    decisions = _decisions_by_idea()
    csv_rows: dict[str, dict] = {}
    pcsv = ROOT / 'portfolio' / 'ideas.csv'
    if pcsv.exists():
        with pcsv.open(newline='') as f:
            for row in csv.DictReader(f):
                csv_rows[row.get('idea_id', '').strip()] = row
    n = 0
    for d in sorted((ROOT / 'ideas').glob('[0-9][0-9][0-9]')):
        lid = f'idea-{d.name}'
        if lid in have:
            continue
        card = {}
        cpath = d / 'idea_card.json'
        if cpath.exists():
            try:
                card = json.loads(cpath.read_text())
            except json.JSONDecodeError:
                card = {}
        dec = decisions.get(d.name, {})
        dataset = card.get('dataset')
        if isinstance(dataset, dict):
            dataset = dataset.get('name') or dataset.get('id') or json.dumps(dataset)[:80]
        append({
            'ledger_id': lid,
            'title': card.get('title') or csv_rows.get(d.name, {}).get('title', ''),
            'claim': card.get('deliverable_sentence') or card.get('question', ''),
            'track': card.get('track', 'baseline'),
            'tags': card.get('tags', []),
            'dataset': dataset or '',
            'status': dec.get('status', 'ACTIVE'),
            'scrutiny': _scrutiny_from_artifacts(d, d.name),
            'kill_reason': dec.get('kill_reason', ''),
            'kill_code': dec.get('kill_code', ''),
            'notes': dec.get('notes', ''),
            'source': f'ideas/{d.name}',
        })
        n += 1
    digest()
    return n


# ------------------------------------------------------------------ digest

def digest() -> Path:
    entries = load()
    lines = ['# Ledger digest (auto-generated -- do not edit; run `python scout.py ledger digest`)',
             '', f'{len(entries)} tracked ideas. Latest state per idea; full history in ledger.jsonl.', '']
    kills: dict[str, int] = {}
    for e in entries.values():
        if e.get('kill_code'):
            kills[e['kill_code']] = kills.get(e['kill_code'], 0) + 1
    if kills:
        lines += ['## Known failure modes (kill-code frequency)',
                  '',
                  'Before proposing a candidate, check it against every pattern below.',
                  'A candidate that dies like a prior one must say what makes it different.', '']
        for code, cnt in sorted(kills.items(), key=lambda kv: -kv[1]):
            lines.append(f'- **{code}** x{cnt}: {TAXONOMY.get(code, "")}')
        lines.append('')
    entriesv = entries
    backlog = [(e.get('novelty_verdict','UNAUDITED'), e) for e in entriesv.values()
               if e.get('status') == 'SCOUT_ONLY']
    if backlog:
        vrank = {'NO_DUPLICATE_FOUND_HIGH_CONFIDENCE': 0, 'NOVEL_VERIFIED': 0,
                 'NO_DUPLICATE_FOUND_LIMITED_SEARCH': 1, 'NOVEL_UNVERIFIED': 1,
                 'UNAUDITED': 3, 'INCREMENTAL': 4,
                 'DUPLICATE_FOUND': 9, 'DUPLICATE_PRIOR': 9}
        backlog.sort(key=lambda ve: (vrank.get(ve[0], 5),
                                     -float(ve[1].get('scores_mean') or 0)))
        lines += ['## Candidate backlog (scouted, not yet shortlisted; ranked)', '']
        for v, e in backlog[:10]:
            lines.append(f"- **{e['ledger_id']}** [{v}"
                         + (f", score {e['scores_mean']:.1f}" if e.get('scores_mean') else '')
                         + (f", audited {e['audited_at'][:10]}" if e.get('audited_at') else '')
                         + f"] -- {e.get('title','')}")
        if len(backlog) > 10:
            lines.append(f'- ... and {len(backlog)-10} more (python scout.py backlog)')
        lines.append('')
    templates = {}
    for e in entries.values():
        dt = e.get('design_template')
        if dt:
            templates[dt] = templates.get(dt, 0) + 1
    if templates:
        lines += ['## Design-template concentration (homogenization watch)', '',
                  'The research GRAMMAR, not the nouns. High concentration means the',
                  'portfolio explores one scientific move with rotating vocabulary.', '']
        for k, v in sorted(templates.items(), key=lambda kv: -kv[1]):
            lines.append(f'- {k}: {v}')
        lines.append('')
    lines += ['## Ideas', '']
    for lid in sorted(entries):
        e = entries[lid]
        bits = [f"**{lid}** [{e.get('status','?')}/{e.get('scrutiny','?')}/{e.get('track','baseline')}]",
                (e.get('title') or '(untitled)')]
        if e.get('kill_code'):
            bits.append(f"killed: {e['kill_code']}")
        if e.get('dataset'):
            bits.append(f"data: {e['dataset']}")
        lines.append('- ' + ' -- '.join(bits))
    DIGEST.parent.mkdir(parents=True, exist_ok=True)
    DIGEST.write_text('\n'.join(lines) + '\n')
    return DIGEST


# ---------------------------------------------------------------- CLI glue

def cli(args) -> None:
    cmd = args.ledger_cmd
    if cmd == 'migrate':
        n = migrate(force=getattr(args, 'force', False))
        print(f'Migrated {n} idea(s). Digest: {DIGEST.relative_to(ROOT)}')
    elif cmd == 'digest':
        print(digest().relative_to(ROOT))
    elif cmd == 'list':
        for lid, e in sorted(load().items()):
            print(f"{lid:<14} {e.get('status','?'):<11} {e.get('scrutiny','?'):<10} "
                  f"{e.get('track','baseline'):<9} {e.get('kill_code','') or '-':<22} {e.get('title','')[:70]}")
    elif cmd == 'show':
        e = load().get(args.id)
        if not e:
            raise SystemExit(f'No ledger entry {args.id!r}. Try: python scout.py ledger list')
        print(json.dumps(e, indent=2, ensure_ascii=False))
    elif cmd == 'search':
        q = args.query.lower()
        hits = 0
        for lid, e in sorted(load().items()):
            hay = json.dumps(e, ensure_ascii=False).lower()
            if q in hay:
                hits += 1
                print(f"{lid:<14} {e.get('status','?'):<11} {e.get('title','')[:80]}")
        if not hits:
            print('No matches.')
    elif cmd == 'kill':
        if args.code not in TAXONOMY:
            raise SystemExit('Unknown kill code. Known:\n  ' + '\n  '.join(sorted(TAXONOMY)))
        append({'ledger_id': args.id, 'status': 'REJECTED',
                'kill_code': args.code, 'kill_reason': args.reason})
        digest()
        print(f'Recorded kill for {args.id} ({args.code}); digest refreshed.')
    elif cmd == 'set-status':
        if args.status not in STATUSES:
            raise SystemExit('Unknown status. Known: ' + ', '.join(STATUSES))
        if args.id not in load():
            raise SystemExit(f'No ledger entry {args.id!r}. Try: python scout.py ledger list')
        append({'ledger_id': args.id, 'status': args.status,
                'notes': getattr(args, 'note', '') or ''})
        digest()
        print(f'{args.id} -> {args.status}; digest refreshed.')
    elif cmd == 'taxonomy':
        for code, desc in TAXONOMY.items():
            print(f'{code:<22} {desc}')
