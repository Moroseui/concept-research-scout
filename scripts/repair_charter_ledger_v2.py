#!/usr/bin/env python3
"""Repair v2 (2026-08-18 closeout): tombstone the six baseline rows the
cross-charter bug CREATED.

The v1 repair script's restoration silently failed: it looked for a
timestamp under 'ts'/'updated_at' while ledger events carry 'recorded_at',
so it read the corrupt SHORTLISTED event as the 'prior state' and
re-appended it with a note claiming restoration. External review caught
this; direct history inspection then showed the truer fact: none of the
six rows existed before 2026-08-17 at all. Old cycle 001 had six real
candidates and cycle 002 had four, so scout-001-c07, scout-002-c06, and
scout-002-c07 are phantoms outright, and the other three reference real
old candidates that were never ledger-tracked (early cycles predate
candidate backfilling). Restoring any of them to SCOUT_ONLY would inject
unaudited ancient entries into the live ranked backlog.

Correct action for all six: tombstone (status INVALID_ROW). Materialized
views (digest, index, backlog) exclude tombstones; history keeps every
event. Run once from the repo root, review the report, commit.
"""
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "orchestrator"))
import ledger as ledger_mod
ledger_mod.ROOT = ROOT
ledger_mod.LEDGER = ROOT / "ledger.jsonl"
ledger_mod.DIGEST = ROOT / "evidence" / "ledger_digest.md"

ROWS = {
    "scout-001-c05": "references real old candidate; never ledger-tracked before the bug",
    "scout-001-c06": "references real old candidate; never ledger-tracked before the bug",
    "scout-001-c07": "phantom: old cycle 001 had only six candidates",
    "scout-002-c02": "references real old candidate; never ledger-tracked before the bug",
    "scout-002-c06": "phantom: old cycle 002 had only four candidates",
    "scout-002-c07": "phantom: old cycle 002 had only four candidates",
}

def history(lid):
    import json as _json
    out = []
    for line in open(ledger_mod.LEDGER):
        try:
            e = _json.loads(line)
        except Exception:
            continue
        if e.get("ledger_id") == lid:
            out.append(e)
    return out

# Defensive preflight (external review, 2026-08-18): an audit repair must
# verify reality matches the incident record before rewriting semantics,
# and must be idempotent in history, not just in materialized state.
current = ledger_mod.load(include_invalid=True)
todo = {}
for lid, why in ROWS.items():
    hist = history(lid)
    if not hist:
        sys.exit(f"REFUSING: {lid} has no ledger history at all; the "
                 "incident record expected a bug-created row. Reality "
                 "differs -- investigate before repairing.")
    first = hist[0]
    if not str(first.get("recorded_at", "")).startswith("2026-08-17"):
        sys.exit(f"REFUSING: {lid}'s first event is dated "
                 f"{first.get('recorded_at')!r}, not 2026-08-17. This row "
                 "does not match the incident record; refusing to rewrite "
                 "its semantics automatically.")
    if current.get(lid, {}).get("status") == "INVALID_ROW":
        print(f"skip {lid}: already tombstoned (idempotent rerun)")
        continue
    todo[lid] = why

for lid, why in todo.items():
    ledger_mod.append({
        "ledger_id": lid,
        "status": "INVALID_ROW",
        "notes": f"TOMBSTONE 2026-08-18: row created in error by the "
                 f"cross-charter shortlist bug on 2026-08-17 ({why}). The v1 "
                 "repair's restoration failed (wrong timestamp field) and "
                 "re-asserted the corrupt state; this tombstone supersedes "
                 "both. Excluded from current state by ledger.load(); "
                 "history retained.",
    })
    print(f"tombstoned {lid}: {why}")
ledger_mod.digest()
print("digests and index regenerated (tombstones excluded by load()).")
