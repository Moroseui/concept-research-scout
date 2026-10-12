"""Exact pre-model Colab failure: read-only proof and reviewed reconciliation.

No general terminal override. The global reservation remains counted. The local
failed attempt and every original byte remain unchanged.
"""
from pathlib import Path
import hashlib
import json
import sqlite3
import subprocess

DOCUMENT = "docs/COLAB_ADMISSION_FAILURE_PRIVATE.json"
PIN = "deec7515de786118abcc43285c4d4ed485fc75104c6151527a425fdb6837e2a0"
CALL = "8ae7bb5acd3a139232fc0c8d8e6aebc16a039e796aef183ad53071fcb9bf43cc"
UNIT = "research-colab-simple-local-terminal-20261012.service"
OLD_ROOT = Path("/opt/research-system/manual-repair-helpers/colab-simple-local-terminal-20261012")


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def require(ok, why):
    if not ok:
        raise ValueError("COLAB_PREMODEL_" + why)


def document(path=None):
    path = Path(path) if path else Path(__file__).resolve().parents[1] / DOCUMENT
    raw = path.read_bytes()
    require(not path.is_symlink() and sha(raw) == PIN, "DOCUMENT_CHANGED")
    value = json.loads(raw)
    require(value["id"] == CALL and value["schema"] == "exact-colab-premodel-terminal/v1", "SCOPE")
    return value


def receipt(value):
    frozen = value["original"]
    return {"schema": "scientific-premodel-failure/v1", "id": CALL,
            "classification": "BLOCKED_BEFORE_MODEL", "reason": "MANUAL_ACCOUNTING_BINDING",
            "model_client_launched": False, "proof_document_sha256": PIN,
            "original_global_row": next(x for x in frozen["global_calls"] if x["id"] == CALL),
            "original_local_row": next(x for x in frozen["local_calls"] if x["id"] == CALL),
            "accounting_units_preserved": 1, "actual_model_usd": None}


def validate(value, row, local_rows, state, config_raw, unit, files, source_pins):
    frozen = value["original"]
    expected = receipt(value)
    require(dict(row) == expected["original_global_row"] and row["status"] == "RUNNING"
            and row["receipt"] is None, "EXACT_RESERVED_ROW")
    require(local_rows == frozen["local_calls"] and state == frozen["parent_state_row"], "LOCAL_HISTORY")
    require(expected["original_local_row"]["status"] == "BLOCKED_BEFORE_MODEL", "LOCAL_REFUSAL")
    require(sha(config_raw) == frozen["config_sha256"]
            and json.loads(config_raw) == frozen["config"], "CONFIGURATION")
    require(unit == frozen["unit"] and unit["LoadState"] == "loaded"
            and unit["MainPID"] == "0" and unit["ControlGroup"] == ""
            and unit["ActiveState"] == "inactive" and unit["SubState"] == "dead"
            and unit["ExecMainStatus"] == "0", "NATIVE_NOT_TERMINAL")
    state_value = json.loads(state["payload"])
    require(state_value["phase"] == "BLOCKED"
            and state_value["reason"] == "ValueError: MANUAL_ACCOUNTING_BINDING", "FAILURE_REASON")
    require(source_pins == frozen["installed_source_files"]
            and files == frozen["workspace_files"], "SOURCE_OR_WORKSPACE_CHANGED")
    require(not any(name == ".git" or name.startswith(".git/") or
                    Path(name).name in {"sent-input.json", "stage_provenance.jsonl", "console.log"}
                    for name in files), "MODEL_EVIDENCE_PRESENT")
    binding = json.loads(row["binding"])
    require(binding["source"] == frozen["review"]["source_sha"]
            and binding["stage"] == "run_spec_author"
            and binding["input"]["workspace"] == frozen["workspace"], "CALL_BINDING")
    import re
    require(re.fullmatch('[0-9a-f]{64}', CALL) and
            re.fullmatch('[0-9a-f]{40}', binding['source']) and
            re.fullmatch('astra/manual-[a-z0-9-]+', frozen['config']['branch']) is None,
            "FAILURE_DIAGNOSIS")
    return {"id": CALL, "proof_sha256": PIN, "classification": "EXACT_PREMODEL_BRANCH_REFUSAL",
            "model_client_launched": False, "scientific_successor": False}


def qualify(row, value=None):
    """Read the frozen original service/lane; never write or start a process."""
    value = document() if value is None else value
    frozen = value["original"]
    from orchestrator.manual_host_guard import trusted
    from orchestrator.autonomy_review import verify_result
    folder = Path("/var/lib/research-system-manual-sprint10-deployment/colab-simple-local-terminal-20261012/review")
    approved = verify_result(trusted(folder))
    require(approved == frozen["review"] and approved["verdict"] == "APPROVE", "INSTALLED_APPROVAL")
    manifest = json.loads(trusted(folder / "packet-manifest.json").read_bytes())
    for name, pin in manifest["source_files"].items():
        require(sha(trusted(OLD_ROOT / name).read_bytes()) == pin, "INSTALLED_SOURCE_CHANGED")
    unit = dict(line.split("=", 1) for line in subprocess.check_output(
        ["systemctl", "show", UNIT, "-p", "LoadState", "-p", "ActiveState", "-p", "SubState",
         "-p", "MainPID", "-p", "ControlGroup", "-p", "ExecMainStatus"], text=True, timeout=15).splitlines())
    lane = Path(frozen["lane"])
    from orchestrator import private_records as pr
    pr.check_tree(lane)
    with sqlite3.connect((lane / "jobs.sqlite").as_uri() + "?mode=ro", uri=True) as db:
        db.row_factory = sqlite3.Row
        db.execute("PRAGMA query_only=ON")
        db.execute("BEGIN")
        rows = [dict(r) for r in db.execute("SELECT * FROM manual_calls ORDER BY id")]
        state = dict(db.execute("SELECT * FROM manual_state WHERE id=1").fetchone())
        config = pr.check(lane / "lane.json").read_bytes()
    work = Path(frozen["workspace"])
    pr.check_tree(work)
    files = {str(p.relative_to(work)): sha(p.read_bytes()) for p in work.rglob("*") if p.is_file()}
    pins = {name: sha(trusted(OLD_ROOT / name).read_bytes()) for name in frozen["installed_source_files"]}
    return validate(value, row, rows, state, config, unit, files, pins)


def reconcile(accounts):
    """Called only by the explicitly reviewed one-use reconciliation tool."""
    value = document()
    expected = receipt(value)
    row = dict(accounts.db.execute("SELECT * FROM autonomy_calls WHERE id=?", (CALL,)).fetchone())
    if row["status"] == "FAILED":
        require(row == {**expected["original_global_row"], "status": "FAILED",
                        "receipt": json.dumps(expected, sort_keys=True)}, "RECONCILIATION_CHANGED")
        event = accounts.db.execute("SELECT payload FROM events WHERE id=?", (CALL + ":finished",)).fetchone()
        require(event is not None and json.loads(event[0]) == expected, "TERMINAL_EVENT_REQUIRED")
        return {"status": "ALREADY_RECONCILED_NO_NEW_CALL", "id": CALL}
    qualify(row, value)
    require([r["id"] for r in accounts.db.execute("SELECT id FROM autonomy_calls WHERE status='RUNNING'")] == [CALL],
            "OTHER_RUNNING_CALL")
    accounts.finish_scientific(CALL, expected, "FAILED")
    return {"status": "PREMODEL_FAILURE_RECONCILED", "id": CALL,
            "accounting_units_preserved": 1, "model_calls": 0}


HISTORY_DOCUMENT = "docs/COLAB_HISTORICAL_EIGHT_PRIVATE.json"
HISTORY_PIN = "3edfff14ba202972688b03bf6e05a26fed46fd62784dafef4160b557e5787c64"


def historical_document(path=None):
    path = Path(path) if path else Path(__file__).resolve().parents[1] / HISTORY_DOCUMENT
    raw = path.read_bytes()
    require(not path.is_symlink() and sha(raw) == HISTORY_PIN, "HISTORICAL_DOCUMENT_CHANGED")
    value = json.loads(raw)
    require(len(value["local_calls"]) == len(value["global_calls"]) == 8, "HISTORICAL_EIGHT_REQUIRED")
    return value


def validate_historical(value, terminal, continuation, local, global_rows, state, config, plan):
    """Freeze the exact eight-call historical lane, not the whole future run.

    This function grants no successor and never discounts later calls. Normal
    admission separately checks every pending row, scope, owner and total cap.
    """
    require(value["parent_lane"] == terminal["lane"] == continuation["lane"], "HISTORICAL_LANE")
    require(local == value["local_calls"] and state == value["parent_state_row"], "HISTORICAL_LOCAL_CHANGED")
    require(sha(config) == value["config_sha256"] and sha(plan) == value["plan_sha256"], "HISTORICAL_INPUT_CHANGED")
    require(global_rows == value["global_calls"], "HISTORICAL_GLOBAL_CHANGED")
    require(terminal["local_row"] == continuation["local_rows"][-1]
            and terminal["global_row"] == continuation["global_rows"][-1]
            and terminal["state_sha256"] == continuation["original_state_sha256"]
            and sha(continuation["original_state_raw"].encode()) == terminal["state_sha256"],
            "HISTORICAL_TERMINAL_BINDING")
    require(terminal["local_row"] in local and terminal["global_row"] in global_rows,
            "HISTORICAL_TERMINAL_ROW")
    return terminal["local_row"], continuation["original_state_raw"]


def historical_read(db, terminal, continuation, value=None):
    value = historical_document() if value is None else value
    from orchestrator import private_records as pr
    lane = Path(value["parent_lane"])
    pr.check_tree(lane)
    with sqlite3.connect((lane / "jobs.sqlite").as_uri() + "?mode=ro", uri=True) as local:
        local.row_factory = sqlite3.Row
        local.execute("PRAGMA query_only=ON")
        local.execute("BEGIN")
        rows = [dict(r) for r in local.execute("SELECT * FROM manual_calls ORDER BY id")]
        state = dict(local.execute("SELECT * FROM manual_state WHERE id=1").fetchone())
    # Every original row is selected by its immutable identity and checked whole.
    # Later rows are not hidden from any admission query or cap calculation.
    global_rows = []
    for old in value["global_calls"]:
        row = db.execute("SELECT * FROM autonomy_calls WHERE id=?", (old["id"],)).fetchone()
        require(row is not None, "HISTORICAL_GLOBAL_MISSING")
        global_rows.append(dict(row))
    return validate_historical(value, terminal, continuation, rows, global_rows, state,
                               pr.check(lane / "lane.json").read_bytes(),
                               pr.check(lane / "preparation-plan.json").read_bytes())
