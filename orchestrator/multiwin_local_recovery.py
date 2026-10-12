"""Exact positive pre-model proof; preservation and scoped recovery only."""
from pathlib import Path
import hashlib
import json
import sqlite3
import subprocess

DOCUMENT = "docs/MULTIWIN_LOCAL_ADMISSION_PRIVATE.json"
PIN = "6bbd33541c3ffaff9d4d4c1853e36fe9c6c73c496c803c43d279c73cd3198e02"
CALL = "8063ddd1d6a351f0b8369b067abb294085ecca0d43d18ffbf5057a9b8f20059b"
RUN = "colab-1ad5fafc220b3d65f576ce08"
UNIT = "research-multiwin-tonight-continuation-20261012.service"
OLD_ROOT = Path("/opt/research-system/manual-repair-helpers/multiwin-tonight-continuation-20261012")
EVENT = "multiwin-local-accounting-20261012"


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def require(ok, why):
    if not ok:
        raise ValueError("MULTIWIN_PREMODEL_" + why)


def document(root):
    from orchestrator.manual_host_guard import trusted
    raw = trusted(Path(root) / DOCUMENT).read_bytes()
    require(sha(raw) == PIN, "DOCUMENT_PIN")
    b = json.loads(raw)
    require(b["schema"] == "multiwin-local-admission-repair/v1"
            and b["call_id"] == CALL and b["run_id"] == RUN
            and b["run_limit"] == 24 and b["batch_limit"] == 128
            and b["original_calls"] == 20 and b["failed_extra_reservation"] == 1
            and b["max_remaining_calls"] == 3 and b["execution_authorized"] is False
            and b["allowed_next"] == [["run_spec_author",12],["run_spec_review",10],["run_spec_review",11]]
            and len(b["local_calls_pins"]) == len(b["global_calls_pins"]) == 21, "BOUND_SCOPE")
    return b


def terminal_receipt(b):
    return {"schema":"scientific-premodel-failure/v1", "id":CALL,
            "classification":"BLOCKED_BEFORE_MODEL", "reason":"LIMITER_STATE_INCONSISTENT",
            "model_client_launched":False, "proof_document_sha256":PIN,
            "original_global_row":b["global_failed"], "original_local_row":b["local_failed"],
            "accounting_units_preserved":1, "actual_model_usd":0}


def validate(b, row, local, global_rows, state, account, owner, config, unit, files, dirs):
    require(dict(row) == b["global_failed"] and row["status"] == "RUNNING"
            and row["receipt"] is None, "EXACT_RESERVED_ROW")
    require({r["id"]:sha(canonical(r)) for r in local} == b["local_calls_pins"], "LOCAL_HISTORY")
    require({r["id"]:sha(canonical(r)) for r in global_rows} == b["global_calls_pins"], "GLOBAL_HISTORY")
    require(state == b["state_row"] and account == b["account_row"] and owner == b["owner"],
            "STATE_ACCOUNT_OWNER")
    require(config == b["config"], "CONFIG")
    require(next(r for r in local if r["id"] == CALL) == b["local_failed"]
            and b["local_failed"]["status"] == "BLOCKED_BEFORE_MODEL", "LOCAL_REFUSAL")
    value = json.loads(state["payload"])
    require(value["phase"] == "BLOCKED"
            and value["reason"] == "ValueError: LIMITER_STATE_INCONSISTENT"
            and value["pending"] is None, "FAILURE_STATE")
    require(unit == b["unit"] and unit["MainPID"] == "0"
            and unit["ActiveState"] == unit["SubState"] == "failed"
            and unit["ControlGroup"] == "" and unit["ExecMainStatus"] == "1"
            and bool(unit["InvocationID"])
            and int(unit["ExecMainExitTimestampMonotonic"]) >
                int(unit["ExecMainStartTimestampMonotonic"]) > 0, "POSITIVE_TERMINAL")
    require(files == b["workspace_files"] and sorted(dirs) == b["workspace_dirs"], "WORKSPACE")
    require(not any(Path(n).name in {"console.log","sent-input.json","stage_provenance.jsonl",".git"}
                    or ".git" in Path(n).parts for n in [*files,*dirs]), "MODEL_EVIDENCE_PRESENT")
    binding = json.loads(row["binding"])
    require(binding["stage"] == "run_spec_author" and binding["source"] == config["source"]
            and binding["input"]["workspace"] ==
                str(Path(config["workspace_root"]) / "run_spec_author-11"), "CALL_BINDING")
    return {"id":CALL, "classification":"EXACT_PREMODEL_LOCAL_ALLOWANCE_REFUSAL",
            "model_client_launched":False, "proof_sha256":PIN, "scientific_successor":False}


def qualify(db, b, prior_runtime):
    """Same live global transaction used by admission, local read-only snapshot."""
    from orchestrator import private_records as pr
    # Verify the immutable receipts/source directly. This also works inside the
    # separate administrative engine without importing a second orchestrator package.
    from orchestrator.autonomy_review import verify_result
    from orchestrator.manual_host_guard import trusted
    deployments = (
        ("multiwin-tonight-continuation-20261012", b["prior_source"], b["prior_review_sha256"]),
        ("colab-simple-admission-20261012", "0770e23ac2bf257edc819b2e3f6e2a2693e12095",
         "93871cd5a9ccae13b9d68f5cd01457cff20b80aad3c55d457cbaa30777c7210d"))
    expected_receipts = set()
    for name, source, report in deployments:
        record_root = Path("/var/lib/research-system-manual-sprint10-deployment") / name
        source_root = Path("/opt/research-system/manual-repair-helpers") / name
        receipt_path = record_root / "INSTALLED.json"
        expected_receipts.add(str(receipt_path))
        raw = trusted(receipt_path).read_bytes()
        require(sha(raw) == b["installed_receipt_pins"][str(receipt_path)], "INSTALLED_RECEIPT_PIN")
        receipt = json.loads(raw)
        approval = verify_result(trusted(record_root / "review"))
        require(approval["source_sha"] == source and approval["report_sha256"] == report
                and approval["verdict"] == "APPROVE"
                and receipt["source"] == source and receipt["review_sha256"] == report, "INSTALLED_PRIOR_APPROVAL")
        manifest = json.loads(trusted(record_root / "review/packet-manifest.json").read_bytes())
        for relative, pin in receipt["files"].items():
            require(not Path(relative).is_absolute() and ".." not in Path(relative).parts, "SOURCE_PATH")
            require(manifest["source_files"][relative] == pin
                    and sha(trusted(source_root / relative).read_bytes()) == pin, "INSTALLED_SOURCE_PIN")
        require(sha(trusted(Path("/etc/systemd/system") / ("research-" + name + ".service")).read_bytes())
                == receipt["unit_sha256"], "INSTALLED_UNIT_PIN")
    require(set(b["installed_receipt_pins"]) == expected_receipts, "EXACT_DEPENDENCIES")
    props = ["LoadState","MainPID","ActiveState","SubState","ControlGroup","ExecMainStatus",
             "InvocationID","ExecMainStartTimestampMonotonic","ExecMainExitTimestampMonotonic"]
    cmd = ["systemctl","show",UNIT,"--no-pager"]
    for name in props:
        cmd += ["-p",name]
    unit = dict(x.split("=",1) for x in subprocess.check_output(cmd,text=True,timeout=15).splitlines())
    lane = Path(b["config"]["context"]).parent
    pr.check_tree(lane)
    with sqlite3.connect((lane/"jobs.sqlite").as_uri()+"?mode=ro",uri=True) as local:
        local.row_factory = sqlite3.Row
        local.execute("PRAGMA query_only=ON")
        local.execute("BEGIN")
        rows = [dict(r) for r in local.execute("SELECT * FROM manual_calls ORDER BY rowid")]
        state = dict(local.execute("SELECT * FROM manual_state WHERE id=1").fetchone())
        account = dict(local.execute("SELECT * FROM manual_account WHERE id=1").fetchone())
    global_rows = [dict(r) for r in db.execute("SELECT * FROM autonomy_calls WHERE change_id=? ORDER BY rowid",(RUN,))]
    row = dict(db.execute("SELECT * FROM autonomy_calls WHERE id=?",(CALL,)).fetchone())
    owner = dict(db.execute("SELECT * FROM autonomy_runs WHERE id=?",(RUN,)).fetchone())
    work = Path(b["config"]["workspace_root"]) / "run_spec_author-11"
    pr.check_tree(work)
    files = {str(p.relative_to(work)):{"sha256":sha(p.read_bytes()),"bytes":p.stat().st_size}
             for p in work.rglob("*") if p.is_file()}
    dirs = [str(p.relative_to(work)) for p in work.rglob("*") if p.is_dir()]
    return validate(b,row,rows,global_rows,state,account,owner,
                    json.loads(pr.check(lane/"lane.json").read_bytes()),unit,files,dirs)


def reconcile(accounts, b, prior_runtime):
    expected = terminal_receipt(b)
    row = dict(accounts.db.execute("SELECT * FROM autonomy_calls WHERE id=?",(CALL,)).fetchone())
    if row["status"] == "FAILED":
        require(row == {**b["global_failed"], "status":"FAILED",
                        "receipt":json.dumps(expected,sort_keys=True)}, "RECONCILIATION_CHANGED")
        event = accounts.db.execute("SELECT payload FROM events WHERE id=?",(CALL+":finished",)).fetchone()
        require(event is not None and json.loads(event[0]) == expected, "TERMINAL_EVENT")
        return {"status":"ALREADY_RECONCILED_NO_NEW_CALL", "id":CALL}
    qualify(accounts.db,b,prior_runtime)
    require([r["id"] for r in accounts.db.execute("SELECT id FROM autonomy_calls WHERE status='RUNNING'")] == [CALL],
            "OTHER_RUNNING_CALL")
    accounts.finish_scientific(CALL,expected,"FAILED")
    return {"status":"PREMODEL_FAILURE_RECONCILED","id":CALL,
            "accounting_units_preserved":1,"model_calls":0}


def next_state(b, approval):
    value = json.loads(b["state_row"]["payload"])
    require(value["rounds"]["run_spec_author"] == 10 and value["rounds"]["run_spec_review"] == 9, "ORIGINAL_ROUNDS")
    value.update(phase="run_spec_author",reason="REVIEWED_LOCAL_ALLOWANCE_FORWARDING",
                 pending=None)
    value["rounds"]["run_spec_author"] = 11
    value["interventions"].append({"kind":EVENT, "scope_sha256":PIN,
        "review_sha256":approval, "preserved_failed_call":CALL,
        "run_limit":24, "maximum_remaining_calls":3, "scientific_acceptance":False})
    return value


def record(b, approval):
    after = next_state(b, approval["report_sha256"])
    return {"scope_sha256":PIN, "source":approval["source_sha"],
            "review_sha256":approval["report_sha256"], "preserved_call":CALL,
            "preserved_local_calls":21, "run_limit":24, "batch_limit":128,
            "maximum_remaining_calls":3, "model_calls":0,
            "before_sha256":sha(canonical(json.loads(b["state_row"]["payload"]))),
            "after_sha256":sha(canonical(after))}


def guard(driver, b, approval):
    from orchestrator import private_records as pr
    expected = record(b, approval)
    folder = driver.state / EVENT
    require(json.loads(pr.check(folder/"COMPLETE.json").read_bytes()) == expected, "RECOVERY_COMPLETE")
    event = driver.store.db.execute("SELECT payload FROM events WHERE id=?",(EVENT,)).fetchone()
    require(event is not None and json.loads(event[0]) == expected, "RECOVERY_EVENT")
    require(driver.config == b["config"], "UNCHANGED_CONFIG")
    for ident, pin in b["local_calls_pins"].items():
        row = driver.store.db.execute("SELECT * FROM manual_calls WHERE id=?",(ident,)).fetchone()
        require(row is not None and sha(canonical(dict(row))) == pin, "PRESERVED_LOCAL")
    for ident, pin in b["global_calls_pins"].items():
        row = driver.store.batch.db.execute("SELECT * FROM autonomy_calls WHERE id=?",(ident,)).fetchone()
        require(row is not None, "PRESERVED_GLOBAL_MISSING")
        if ident == CALL:
            require(dict(row) == {**b["global_failed"],"status":"FAILED",
                "receipt":json.dumps(terminal_receipt(b),sort_keys=True)}, "PRESERVED_FAILED_RESERVATION")
        else:
            require(sha(canonical(dict(row))) == pin, "PRESERVED_GLOBAL")
    return expected


def recover(driver, b, approval, prior_runtime):
    """One explicit reviewed operation; preserve every call and local account."""
    from orchestrator import private_records as pr
    require(not (driver.state/"HALT").exists()
            and not (driver.store.batch.folder/"HALT").exists(), "HALT")
    folder = driver.state / EVENT
    expected = record(b, approval)
    if (folder/"COMPLETE.json").exists():
        guard(driver,b,approval)
        return {"status":"ALREADY_RECOVERED_NO_NEW_CALL","model_calls":0}
    require(not folder.exists() and not folder.is_symlink(), "INCOMPLETE_RECOVERY_RECONCILE")
    qualify(driver.store.batch.db,b,prior_runtime)
    require(driver.current() == json.loads(b["state_row"]["payload"]), "BEFORE_STATE")
    pr.mkdir(folder)
    pr.write_bytes(folder/"INTENT.json",canonical(expected))
    reconcile(driver.store.batch,b,prior_runtime)
    db = driver.store.db
    db.execute("BEGIN IMMEDIATE")
    try:
        require(dict(db.execute("SELECT * FROM manual_state WHERE id=1").fetchone()) == b["state_row"],
                "LOCAL_STATE_MOVED")
        require(dict(db.execute("SELECT * FROM manual_account WHERE id=1").fetchone()) == b["account_row"],
                "ACCOUNT_MOVED")
        for ident,pin in b["local_calls_pins"].items():
            require(sha(canonical(dict(db.execute("SELECT * FROM manual_calls WHERE id=?",(ident,)).fetchone())))==pin,
                    "LOCAL_CALL_MOVED")
        db.execute("INSERT INTO events VALUES(?,?,?)",(EVENT,RUN,canonical(expected).decode()))
        db.execute("UPDATE manual_state SET payload=? WHERE id=1",
                   (json.dumps(next_state(b,approval["report_sha256"]),sort_keys=True),))
        db.execute("COMMIT")
    except BaseException:
        db.execute("ROLLBACK")
        raise
    require(driver.current() == next_state(b,approval["report_sha256"]), "RECOVERY_READBACK")
    require(dict(db.execute("SELECT * FROM manual_account WHERE id=1").fetchone()) == b["account_row"],
            "ACCOUNT_PRESERVED")
    pr.write_bytes(folder/"COMPLETE.json",canonical(expected))
    guard(driver,b,approval)
    return {"status":"READY_AUTHOR12_QUALIFICATION","model_calls":0,
            "preserved_local_calls":21,"maximum_remaining_calls":3}
