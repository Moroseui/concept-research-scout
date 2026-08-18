#!/usr/bin/env python3
"""One-time repair for the 2026-08-18 cross-charter promotion corruption.

What happened: _do_shortlist retired source candidates via _active_charter()
and wrote idempotence state under an unqualified cycle key. Six ISLES'24
promotions (ideas 020-025) therefore (a) falsely retired six BASELINE ledger
rows, (b) left the six true isles24 source rows available -- one of which
was re-promoted overnight as zombie idea-026 (a duplicate of killed
idea-020), and (c) collided state.shortlisted keys between charters.

What this script does (append-only; nothing is rewritten):
 1. Appends corrective events restoring the six baseline rows to their
    pre-corruption latest state (reconstructed from the ledger's own
    history, not guessed).
 2. Appends SHORTLISTED + promoted-to notes + charter to the six true
    isles24 source rows (canonical mapping; 026 noted as erroneous).
 3. Appends charter=isles24 and an evaluation-contamination marker to
    ideas 020-025 (their critique/debate/feasibility prompts carried the
    baseline charter -- see the decisions.md entry of this date).
 4. Appends REJECTED to idea-026 as a duplicate promotion.
 5. Migrates state.shortlisted keys "1"/"2" to "isles24-001"/"isles24-002"
    with the canonical idea numbers.
 6. Regenerates the per-charter digests.

Run once from the repo root, review the printed report, then commit.
"""
import json, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "orchestrator"))
import ledger as ledger_mod
ledger_mod.ROOT = ROOT
ledger_mod.LEDGER = ROOT / "ledger.jsonl"
ledger_mod.DIGEST = ROOT / "evidence" / "ledger_digest.md"

CANON = {
    "isles24-001": {5: 20, 7: 22, 6: 24},
    "isles24-002": {2: 21, 7: 23, 6: 25},
}
BAD_DATE = "2026-08-17"

def history(lid):
    out = []
    for line in open(ledger_mod.LEDGER):
        try:
            e = json.loads(line)
        except json.JSONDecodeError:
            continue
        if e.get("ledger_id") == lid:
            out.append(e)
    return out

def latest_before_corruption(lid):
    state = {}
    for e in history(lid):
        ts = str(e.get("ts", e.get("updated_at", "")))
        if str(e.get("notes", "")).startswith("promoted to idea-0") and ts.startswith(BAD_DATE):
            break
        state.update({k: v for k, v in e.items() if v not in (None, "")})
    return state

report = []
for cyc, mapping in CANON.items():
    cyc_no = int(cyc.split("-")[1])
    for cand, idea in mapping.items():
        base_lid = f"scout-{cyc_no:03d}-c{cand:02d}"
        isles_lid = f"isles24-scout-{cyc_no:03d}-c{cand:02d}"
        prior = latest_before_corruption(base_lid)
        if prior:
            ledger_mod.append({
                "ledger_id": base_lid,
                "status": prior.get("status", "SCOUT_ONLY"),
                "notes": (str(prior.get("notes") or "") +
                          " [corrective append 2026-08-18: falsely retired for "
                          f"isles24 idea-{idea:03d} by the cross-charter "
                          "shortlist bug; restored]").strip(),
            })
            report.append(f"restored {base_lid} -> {prior.get('status', 'SCOUT_ONLY')}")
        note = f"promoted to idea-{idea:03d}"
        if isles_lid.endswith("001-c05"):
            note += (" (canonical; idea-026 was an erroneous duplicate "
                     "promotion caused by the same bug and is REJECTED)")
        ledger_mod.append({"ledger_id": isles_lid, "status": "SHORTLISTED",
                           "notes": note, "charter": "isles24"})
        report.append(f"retired  {isles_lid} -> idea-{idea:03d}")
        ledger_mod.append({"ledger_id": f"idea-{idea:03d}", "charter": "isles24",
                           "charter_evaluation":
                           "contaminated_baseline_context_2026-08-18"})
        report.append(f"stamped  idea-{idea:03d} charter=isles24 (evaluation contaminated)")

ledger_mod.append({"ledger_id": "idea-026", "status": "REJECTED",
                   "charter": "isles24",
                   "notes": "duplicate promotion of isles24-scout-001-c05; the "
                            "canonical promotion is idea-020 (killed, "
                            "IDENTIFIABILITY_FAILURE). Zero stages were run. "
                            "Caused by the cross-charter shortlist bug; see "
                            "decisions.md 2026-08-18."})
report.append("rejected idea-026 (zombie duplicate of idea-020)")

state_path = ROOT / "orchestrator" / "state.json"
st = json.loads(state_path.read_text())
sh = st.get("shortlisted", {})
for old_key, new_key in (("1", "isles24-001"), ("2", "isles24-002")):
    if old_key in sh:
        sh[new_key] = {str(c): i for c, i in CANON[new_key].items()}
        del sh[old_key]
        report.append(f"state.shortlisted: {old_key} -> {new_key}")
st["shortlisted"] = sh
state_path.write_text(json.dumps(st, indent=2) + "\n")

ledger_mod.digest()
report.append("per-charter digests regenerated")
print("\n".join(report))
print(f"\n{len(report)} corrections applied (all ledger changes are appends).")
