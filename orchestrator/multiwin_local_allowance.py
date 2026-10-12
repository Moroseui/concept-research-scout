"""Forward an already reviewed same-owner allowance to the existing CAS limiter.

This adapter does not alter amounts, numeric limits, counters, halt state, other
owners, or the dispatch algorithm. Runtime authority supplies a verified grant.
"""
from pathlib import Path
import hashlib
import json

RUN = "colab-1ad5fafc220b3d65f576ce08"
AUTHORITY = "a7fbba4b5c49426c099f1eb8d91e45489b454fc51a527f5df1566a60c1cabcb1"
ALLOWED = {("run_spec_author", 12), ("run_spec_review", 10), ("run_spec_review", 11)}


def require(ok, reason):
    if not ok:
        raise ValueError("MULTIWIN_LOCAL_ALLOWANCE_" + reason)


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def bind(config, scope_sha256, review_sha256, verify_grant):
    """Called only by the authenticated installed runtime, once per process."""
    from orchestrator import autonomy_limits as limits, item4_scoped_calls as scoped
    from orchestrator.manual_executor import ManualExecutor
    from orchestrator.autonomy_accounting import BatchAccounts

    require(config["run_id"] == RUN, "OWNER")
    for pin in (scope_sha256, review_sha256):
        require(isinstance(pin, str) and len(pin) == 64
                and all(c in "0123456789abcdef" for c in pin), "AUTHORITY_PIN")
    previous_allowance = limits.allowance
    previous_validate = scoped.validate_allowance
    previous_reserve = ManualExecutor.reserve_call
    previous_batch = BatchAccounts.reserve_scientific
    active = {}

    def amendment(store, run, policy):
        if run != RUN:
            return previous_allowance(store, run, policy)
        require(active.get("store") is store, "LOCAL_OWNER")
        require(limits.local_limit(store, run, policy) == 24, "EXISTING_LIMIT")
        verify_grant(store)
        row = store.db.execute("SELECT * FROM manual_calls WHERE id=?",
                               (active["id"],)).fetchone()
        require(row is not None and row["status"] == "RUNNING"
                and (row["stage"], row["attempt"]) == active["pair"], "RESERVED_LOCAL_CALL")
        return {"authority_sha256": AUTHORITY, "run_limit": 24,
                "scoped_run_id": RUN, "call_id": active["id"],
                "review_sha256": review_sha256, "checkpoint_sha256": scope_sha256}

    def validate(accounts, event, allowance):
        if allowance.get("scoped_run_id") != RUN:
            return previous_validate(accounts, event, allowance)
        store = active.get("store")
        require(store is not None and accounts.db is store.db, "ACCOUNT_CONNECTION")
        require(event == {"run_id": active["id"], "attempt": "1",
                          "source": config["source"], "branch": config["branch"]},
                "EXACT_EVENT")
        require(allowance == amendment(store, RUN, config["policy"]), "ALLOWANCE_BINDING")

    def reserve(store, run, stage, source, branch, policy, receipt):
        if run != RUN:
            return previous_reserve(store, run, stage, source, branch, policy, receipt)
        require(not active, "REENTRANT")
        require((source, branch, policy) ==
                (config["source"], config["branch"], config["policy"]), "SOURCE_POLICY")
        require(json.loads((Path(store.path).parent / "lane.json").read_bytes()) == config,
                "CONFIGURATION")
        verify_grant(store)
        number = store.db.execute("SELECT count(*) FROM manual_calls WHERE stage=?",
                                  (stage,)).fetchone()[0] + 1
        require((stage, number) in ALLOWED, "NEXT_UNUSED_CALL")
        ident = digest((RUN + ":" + stage + ":" + str(number)).encode())
        require(receipt.get("workspace") ==
                str(Path(config["workspace_root"]) / (stage + "-" + str(number))),
                "WORKSPACE")
        require(not store.db.execute("SELECT 1 FROM manual_calls WHERE id=?", (ident,)).fetchone(),
                "NO_REPLAY")
        active.update(store=store, id=ident, pair=(stage, number))
        try:
            return previous_reserve(store, run, stage, source, branch, policy, receipt)
        finally:
            active.clear()

    def batch_reserve(batch, ident, run, stage, source, receipt):
        if run == RUN:
            require(active.get("store") is not None
                    and active["store"].batch is batch
                    and (ident, stage, source) ==
                    (active["id"], active["pair"][0], config["source"]), "GLOBAL_CONNECTION")
        return previous_batch(batch, ident, run, stage, source, receipt)

    limits.allowance = amendment
    scoped.validate_allowance = validate
    ManualExecutor.reserve_call = reserve
    BatchAccounts.reserve_scientific = batch_reserve

    def restore():
        limits.allowance = previous_allowance
        scoped.validate_allowance = previous_validate
        ManualExecutor.reserve_call = previous_reserve
        BatchAccounts.reserve_scientific = previous_batch
    return restore
