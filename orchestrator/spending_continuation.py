"""Exact spending connection for the two preserved 2026-10-07 owners.

No ledger mutation, cap override, reservation, or scientific-approval transfer.
A separately reviewed runtime leaves the original lanes and their code intact.
"""
import json
from pathlib import Path
from orchestrator import private_records as pr
from orchestrator import experiment_timeout_continuation as continuation
from orchestrator.manual_executor import digest, read
from tools.deploy_manual_lane import bound

CHANGE = "spending-install-parent-repair-20261007"
SOURCE = "8e0423395d650bf757780c8c0877d7801815514a"
AUTHORITY = "72bdeef71955ec252021500ea50320008431248a6429c1e2a701473f917a7bcb"
RUNTIME = "dbd849b9267ece5ff231ca7d45710d1bdb24e9294caa8f2e0d694e7394dd595d"
POINTER = "/etc/research-system-manual-sprint10/selected-release.json"
RECORD = "/var/lib/research-system-manual-sprint10-deployment/spending-continuation-scope-20261007"


def require(ok, reason):
    if not ok: raise ValueError("SPENDING_CONTINUATION_" + reason)


def implementation(root=Path("/")):
    """Authenticate the independent approval and the complete installed runtime."""
    from orchestrator.manual_host_guard import trusted
    from orchestrator.autonomy_review import verify_result
    from tools.manual_promotion import manifest_check
    root=Path(root)
    path=bound(root, RECORD + "/installed.json")
    if root == Path("/"): trusted(path)
    installed=manifest_check(root, RECORD)
    require(installed.get("repair") == CHANGE and installed.get("scientific_source") == SOURCE,
            "INSTALL_SCOPE")
    release=bound(root,installed["layout"]["release"])
    require(Path(__file__).resolve() == release/"orchestrator/spending_continuation.py", "IMPORTED_RUNTIME")
    if root == Path("/"): trusted(release)
    selected=read(bound(root, POINTER))
    require(selected == installed["previous"], "SELECTED_RELEASE_CHANGED")
    require(selected["source"] == SOURCE and digest(bound(root, selected["runtime"]).read_bytes()) == RUNTIME,
            "SCIENTIFIC_RUNTIME_CHANGED")
    require(digest((release/"docs/SPENDING_CONTINUATION_AUTHORITY_20261007.txt").read_bytes()) == AUTHORITY,
            "AUTHORITY_CHANGED")
    approved=verify_result(bound(root, installed["review_folder"]))
    require((approved["change_id"],approved["verdict"],approved["source_sha"],approved["runtime_sha256"],approved["report_sha256"]) ==
        (CHANGE,"APPROVE",installed["source"],RUNTIME,installed["review_sha256"]), "IMPLEMENTATION_APPROVAL")
    manifest=read(bound(root,installed["review_folder"])/"packet-manifest.json")
    for name in installed["changed_files"]:
        require(digest((release/name).read_bytes()) == manifest["source_files"].get(name), "REVIEWED_SOURCE_CHANGED")
    return installed


def lane(batch, run, owner, source, *, image=False):
    """Return the genuine continued lane, or None for an ordinary old owner."""
    if source == owner.get("source"): return None
    require(run in {continuation.ITEM4, continuation.ITEM6}, "OWNER_SCOPE")
    installed=implementation(batch.filesystem_root)
    grant=continuation.binding(batch)
    require(grant is not None and grant["source"] == SOURCE, "GRANT_REQUIRED")
    require(source == SOURCE or image and source == installed["source"], "SOURCE")
    item="6" if run == continuation.ITEM6 else "4"
    row=batch.db.execute("SELECT * FROM autonomy_runs WHERE id=?",(run,)).fetchone()
    require(row is not None and row["status"] == "ACTIVE" and json.loads(row["binding"]) == owner,
            "ACTIVE_ORIGINAL_OWNER")
    require(continuation.sha(dict(row)) == continuation.checkpoint()["owners"][run], "ORIGINAL_OWNER_CHANGED")
    pin=grant["lanes"][item];state=Path(pin["state"])
    require(state.is_absolute() and state == bound(batch.filesystem_root,
        installed["previous"]["state"] + ("/lane" if item == "6" else "/item4/lane")), "STATE")
    config=read(pr.check(state/"lane.json"))
    require(continuation.sha(config) == pin["config_sha256"] and config["owner_binding"] == owner
        and config["source"] == SOURCE and config["run_id"] == run
        and config.get("timeout_continuation") == continuation.KEY, "CONFIG")
    require(not (state/"HALT").exists() and not (batch.folder/"HALT").exists(), "HALTED")
    raw=pr.check(state/"preparation-plan.json").read_bytes()
    require(digest(raw) == owner["plan_sha256"] == config["plan_sha256"]
        and config["execution_scope"] == owner["execution_scope"], "FROZEN_PLAN")
    return state,config


def closed_ids(batch, run):
    """Only add the original root-proven terminal timeout, retaining its charge."""
    from orchestrator.completed_run import closed_ids as completed
    closed=set(completed(batch,run,root=batch.filesystem_root))
    if run not in {continuation.ITEM4,continuation.ITEM6}: return closed
    # Ordinary installations and histories retain their existing admission.
    if batch.db.execute("SELECT 1 FROM events WHERE id=?",(continuation.KEY,)).fetchone() is None:
        return closed
    row=batch.db.execute("SELECT binding FROM autonomy_runs WHERE id=?",(run,)).fetchone()
    require(row is not None, "OWNER_REQUIRED")
    lane(batch,run,json.loads(row["binding"]),SOURCE)
    # binding() rechecks the exact original row hash, native terminal evidence,
    # and the genuine earlier continuation review on every admission.
    grant=continuation.binding(batch)
    require(grant is not None, "GRANT_REQUIRED")
    closed.add(continuation.FAILED)
    return closed
