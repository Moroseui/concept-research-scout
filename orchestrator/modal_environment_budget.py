"""One no-patient item4 environment inventory in the existing asset ledger.

This grants no scientific allowance and does not reuse a completed owner. Its
full reservation counts in the original item4 smoke/total caps permanently.
"""
from datetime import datetime, timezone
from orchestrator import modal_native_synthetic as synthetic
from orchestrator import modal_native_successor as successor
import json
import re
from orchestrator.modal_item4_policy import (AUTHORITY, TEAM_AUTHORITY, SMOKE_CAP,
    TOTAL_CAP, USAGE_CEILING, SPEND_CEILING, quote)
from orchestrator.modal_billing import headroom
from orchestrator.modal_executor import canonical
from orchestrator.manual_executor import digest
from orchestrator.review_contract import strict_json

PURPOSE = "M4_ITEM4_ENVIRONMENT_INVENTORY"
OPERATION = "item4-scientific-environment-inventory-v1"
RUN = "sprint13b-environment-" + AUTHORITY[:24]
RESOURCES = {"gpu":None, "cpu":1, "memory_mib":4096, "timeout_seconds":300}
OVERHEAD_MICRO = 1_000_000
FIELDS = {"purpose", "operation_id", "authority_sha256", "team_authority_sha256",
    "run_id", "source", "installed_config_sha256", "image_id", "base_image",
    "worker_sha256", "envelope"}


def envelope(rates):
    return {"resources":dict(RESOURCES), "cost":quote(RESOURCES, rates, OVERHEAD_MICRO)}


def profile(value):
    from orchestrator import modal_pinned_image as image
    from orchestrator import modal_diagnostics_image as cpu
    if value.get('purpose')==synthetic.PURPOSE:return synthetic.PURPOSE,synthetic.OPERATION,synthetic.RUN,synthetic.envelope
    if value.get('purpose') == cpu.PURPOSE:return cpu.PURPOSE,cpu.OPERATION,cpu.RUN,image.envelope
    if value.get('purpose') == image.PURPOSE:
        return image.PURPOSE,image.OPERATION,image.RUN,image.envelope
    from orchestrator import modal_environment_closure_route as closure
    if value.get('purpose') == closure.PURPOSE:
        return closure.PURPOSE, closure.OPERATION, closure.RUN, lambda rates:closure.envelope(rates,value['closure']['selection']['wheels'])
    return PURPOSE, OPERATION, RUN, envelope


def validate_binding(binding):
    """Pure fixed-scope check; current billing rates are checked at reservation."""
    from orchestrator.modal_assets import BASE_IMAGE
    if not isinstance(binding, dict):raise ValueError('ENVIRONMENT_INVENTORY_BINDING')
    purpose, operation, run, make_envelope = profile(binding)
    from orchestrator import modal_pinned_image as image
    from orchestrator import modal_diagnostics_image as cpu
    is_cpu=purpose==cpu.PURPOSE
    fields = FIELDS | ({'owner_sha256'} if purpose in {image.PURPOSE,synthetic.PURPOSE} else set()) | ({'reviewed_requirements'} if is_cpu else set()) | ({'native_synthetic'} if purpose==synthetic.PURPOSE else {'image_build'} if image.is_build(purpose) else {'closure'} if purpose != PURPOSE else set())
    if purpose==synthetic.PURPOSE:
        selected=synthetic.selected(binding.get('native_synthetic'))
        if binding.get('image_id')!=selected['image_id'] or not re.fullmatch('[0-9a-f]{64}',str(binding.get('owner_sha256'))):
            raise ValueError('NATIVE_IMAGE_OWNER_BINDING')
    elif is_cpu:cpu.validate_selection(binding.get('image_build'),binding.get('reviewed_requirements'))
    elif purpose == image.PURPOSE:
        image.validate(binding.get('image_build'))
        if not re.fullmatch('[0-9a-f]{64}',str(binding.get('owner_sha256'))):raise ValueError('ITEM4_IMAGE_OWNER_BINDING')
        if image.worker.cpu(binding['image_build']):raise ValueError('ENVIRONMENT_INVENTORY_PURPOSE_CHANGED')
    elif purpose != PURPOSE:
        from orchestrator.modal_environment_closure_route import validate
        validate(binding.get('closure'))
    if (not isinstance(binding, dict) or set(binding) != fields
            or binding["purpose"] != purpose or binding["operation_id"] != operation
            or binding["authority_sha256"] != (cpu.policy.authority() if is_cpu else AUTHORITY) or binding["team_authority_sha256"] != TEAM_AUTHORITY
            or binding["run_id"] != run or binding["base_image"] != BASE_IMAGE
            or not isinstance(binding["image_id"], str) or not re.fullmatch("im-[a-zA-Z0-9]+", binding["image_id"])
            or any(not isinstance(binding[k], str) or not re.fullmatch("[0-9a-f]{64}", binding[k])
                   for k in ("installed_config_sha256", "worker_sha256"))
            or not isinstance(binding["source"], str) or not re.fullmatch("[0-9a-f]{40}", binding["source"])):
        raise ValueError("ENVIRONMENT_INVENTORY_BINDING")
    value = binding["envelope"]
    if (not isinstance(value, dict) or set(value) != ({"resources", "cost"} if purpose in {PURPOSE,synthetic.PURPOSE} else {'resources','proof_resources','cost'} if image.is_build(purpose) else {"resources","cost","wheel_bytes","retention_days","reserved_storage_days","receipt_egress_bound_bytes","storage_rates"})
            or not isinstance(value.get("cost"), dict) or not isinstance(value["cost"].get("rates"), dict)
            or value != make_envelope({**value["cost"]["rates"],**value.get("storage_rates",{})})):
        raise ValueError("ENVIRONMENT_INVENTORY_ENVELOPE")
    return binding


def owner(binding):
    validate_binding(binding)
    from orchestrator.modal_diagnostics_image import PURPOSE as CPU_IMAGE
    from orchestrator.modal_pinned_image import PURPOSE as ITEM4_IMAGE
    if binding['purpose'] in {ITEM4_IMAGE,synthetic.PURPOSE}:raise ValueError('ITEM4_IMAGE_REUSE_EXISTING_OWNER')
    if binding['purpose']==CPU_IMAGE:
        raise ValueError('DIAGNOSTICS_IMAGE_REUSE_EXISTING_OWNER')
    return {"purpose":binding["purpose"], "operation_id":binding["operation_id"], "authority_sha256":AUTHORITY,
        "team_authority_sha256":TEAM_AUTHORITY, "source":binding["source"],
        "binding_sha256":digest(canonical(binding)), "no_scientific_allowance":True}


def selected_asset(row):
    """Recognize only this operation; malformed claimed scope fails closed."""
    if successor.previous_asset(row):return True
    value = strict_json(row["binding"])
    from orchestrator.modal_environment_closure_route import PURPOSE as CLOSURE
    from orchestrator.modal_pinned_image import PURPOSE as IMAGE
    if value.get("purpose") not in {PURPOSE,CLOSURE,IMAGE,synthetic.PURPOSE}: return False
    validate_binding(value)
    if row["run"] != value["run_id"] or row["id"] != digest(canonical(value)):
        raise ValueError("ENVIRONMENT_INVENTORY_ASSET_BINDING")
    if row["reserved_micro_usd"] != value["envelope"]["cost"]["reserved_micro_usd"]:
        raise ValueError("ENVIRONMENT_INVENTORY_ASSET_COST")
    return True


def selected_operation(row):
    from orchestrator.modal_diagnostics_image import selected_asset as cpu_asset
    return selected_asset(row) or cpu_asset(row)


def _item4_runs(db, compute):
    result = set()
    for row in db.execute("SELECT id,binding FROM autonomy_runs"):
        value = strict_json(row["binding"]); scope = value.get("execution_scope", {})
        if ((value.get("backlog_item") == 4 and value.get("experiment_authority_sha256") == AUTHORITY)
                or (scope.get("item_number") == 4 and scope.get("authority_sha256") == AUTHORITY)):
            result.add(row["id"])
    for row in compute:
        value = strict_json(row["binding"]); scope = value.get("experiment", {})
        if value.get("purpose") == "M4_ITEM4" or scope.get("backlog_item") == 4:
            if (scope.get("backlog_item") != 4 or scope.get("authority_sha256") != AUTHORITY
                    or scope.get("team_authority_sha256") != TEAM_AUTHORITY):
                raise ValueError("ENVIRONMENT_INVENTORY_COST_SCOPE")
            result.add(row["run"])
    return result


def terminal_failed_compute(accounts):
    """Default admission qualifies no active rows; a reviewed image route may
    supply authenticated retained terminal failures without changing their rows.
    """
    return set()


def reserve(accounts, ident, run, binding, *, billing_snapshot, now=None):
    """Reserve once as the ledger owner; never create a provider or allowance."""
    now = now or datetime.now(timezone.utc)
    validate_binding(binding)
    purpose, operation, selected_run, make_envelope = profile(binding)
    from orchestrator import modal_pinned_image as image
    from orchestrator import modal_diagnostics_image as cpu
    is_cpu=purpose==cpu.PURPOSE
    if is_cpu:cpu.reviewed(binding['reviewed_requirements'])
    expected = make_envelope(billing_snapshot["rates"])
    if (run != selected_run or digest(canonical(binding)) != ident or binding["envelope"] != expected
            or billing_snapshot.get("workspace") != "moroseui"):
        raise ValueError("ENVIRONMENT_INVENTORY_COST_BINDING")
    from orchestrator import modal_terminal_cost
    # Preserve genuine high-water observations even if subsequent cap admission
    # refuses. Original reservations, charges and statuses are never changed.
    modal_terminal_cost.observe_billing(accounts, billing_snapshot, now)
    db = accounts.db; raw = canonical(binding).decode(); amount = expected["cost"]["reserved_micro_usd"]
    db.execute("BEGIN IMMEDIATE")
    try:
        if (accounts.batch.folder/"HALT").exists(): raise ValueError("AUTONOMY_BATCH_HALTED")
        old = db.execute("SELECT * FROM autonomy_assets WHERE id=?", (ident,)).fetchone()
        if old:
            if old["binding"] != raw or old["run"] != run or not selected_operation(old):
                raise ValueError("ENVIRONMENT_INVENTORY_EXISTING_BINDING")
            db.execute("COMMIT"); return False
        active = db.execute("SELECT * FROM autonomy_runs WHERE id=?", (run,)).fetchone()
        if active is None or active["status"] != "ACTIVE": raise ValueError("BATCH_ACTIVE_RUN_REQUIRED")
        if is_cpu:cpu.owner(accounts,binding)
        elif purpose in {image.PURPOSE,synthetic.PURPOSE}:image.item4_owner(accounts,binding)
        elif strict_json(active["binding"]) != owner(binding):
            raise ValueError("ENVIRONMENT_INVENTORY_OWNER_REQUIRED")
        from orchestrator.spending_continuation import closed_ids
        closed = closed_ids(accounts.batch, run)
        pending = db.execute("SELECT id FROM autonomy_calls WHERE status IN ('RUNNING','UNCERTAIN')").fetchall()
        if any(row["id"] not in closed for row in pending): raise ValueError("BATCH_UNCERTAIN_OR_RUNNING_CALL")
        assets = db.execute("SELECT * FROM autonomy_assets").fetchall()
        compute = db.execute("SELECT * FROM autonomy_compute").fetchall()
        prior_native = successor.qualify(accounts,binding) if purpose==synthetic.PURPOSE else set()
        # A fixed reviewed successor qualifies only its exact diagnosed terminal predecessor.
        # All other changed-source/price/image/config retries still refuse.
        if any(row["id"] not in prior_native and selected_operation(row) and strict_json(row["binding"])["purpose"] == purpose for row in assets):
            raise ValueError("ENVIRONMENT_INVENTORY_ALREADY_RESERVED_NO_RETRY")
        from orchestrator.modal_direct_recovery import resolved_failure_ids
        resolved = resolved_failure_ids(accounts, root=accounts.batch.filesystem_root) | prior_native
        if any(row["status"] != "READY" and row["id"] not in resolved for row in assets):
            raise ValueError("MODAL_UNCERTAIN_ASSET_PREPARATION")
        stopped=terminal_failed_compute(accounts) if purpose in {image.PURPOSE,synthetic.PURPOSE} else set()
        if not isinstance(stopped,set) or not stopped <= {row["id"] for row in compute}:
            raise ValueError("ENVIRONMENT_TERMINAL_COMPUTE_SCOPE")
        if any(row["id"] not in stopped and (row["status"]=="UNCERTAIN" or (row["status"] not in {"COLLECTED", "ACCOUNTED"} and not (is_cpu and strict_json(row["binding"]).get("purpose")=="M4_ITEM4"))) for row in compute):
            raise ValueError("MODAL_ACTIVE_OR_UNCERTAIN_COMPUTE")
        for row in [*assets, *compute]:
            if type(row["reserved_micro_usd"]) is not int or row["reserved_micro_usd"] < 0:
                raise ValueError("ENVIRONMENT_INVENTORY_COST_RECORD")
        from orchestrator.modal_pinned_image import PURPOSE as IMAGE
        if purpose not in {PURPOSE,IMAGE,cpu.PURPOSE,synthetic.PURPOSE}:
            from orchestrator.modal_environment_closure_route import local_wheels
            local_wheels(binding['closure'])
        from orchestrator.modal_direct_budget import selected_asset as selected_download
        item_runs = _item4_runs(db, compute)
        assets_cost = sum(row["reserved_micro_usd"] for row in assets
                          if row["run"] in item_runs or selected_download(row) or selected_asset(row))
        exposure = modal_terminal_cost.exposure(db, compute, billing_snapshot)
        total = assets_cost + sum(exposure["run_cost"].get(r, 0) for r in item_runs)
        smoke = assets_cost + sum(exposure["smoke_cost"].get(r, 0) for r in item_runs)
        item6_cost=None
        if is_cpu:
            item6_cost=sum(r['reserved_micro_usd'] for r in assets if r['run']==cpu.RUN)+sum(
                max(r['reserved_micro_usd'],r['actual_micro_usd'] or 0) for r in compute if r['run']==cpu.RUN)
            if any(r['run']==cpu.RUN for r in compute):raise ValueError('DIAGNOSTICS_IMAGE_BEFORE_EXECUTION_REQUIRED')
            if item6_cost+amount>cpu.policy.TOTAL_MICRO_USD:raise ValueError('DIAGNOSTICS_HARD_COST_CAP')
        elif total + amount > TOTAL_CAP or smoke + amount > SMOKE_CAP:
            raise ValueError("ITEM4_HARD_COST_CAP")
        if exposure["underestimated_apps"]: raise ValueError("ITEM4_COST_BOUND_BELOW_BILLING")
        commitments = ({'compute-reservation:'+r['id']:max(r['reserved_micro_usd'],r['actual_micro_usd'] or 0) for r in compute}
            if is_cpu else dict(exposure["commitments"]))
        commitments.update({"asset-reservation:"+row["id"]:row["reserved_micro_usd"] for row in assets})
        view = headroom(billing_snapshot, now=now, usage_limit_micro=USAGE_CEILING,
                        spend_limit_micro=SPEND_CEILING, commitments=commitments)
        if amount > min(view["usage_headroom_micro"], view["spend_headroom_micro"]):
            raise ValueError("ITEM4_PROVIDER_HEADROOM_WAIT")
        db.execute("INSERT INTO autonomy_assets VALUES(?,?,?,'RESERVED',?,NULL)", (ident, run, raw, amount))
        event = {"kind":"ITEM4_ENVIRONMENT_INVENTORY_RESERVED", "operation_id":operation,
            "binding_sha256":ident, "micro_usd":amount, "billing_snapshot":billing_snapshot,
            "headroom":view, "terminal_exposure":exposure, "scientific_calls":0,
            "caps":{"smoke":SMOKE_CAP, "total":TOTAL_CAP}, "prior_item4_smoke_micro_usd":smoke,
            "prior_item4_total_micro_usd":total,
            "scope":"No-patient infrastructure; full reservation counts in item4 smoke and total caps"}
        if is_cpu:
            event.update(kind='ITEM6_PINNED_IMAGE_RESERVED',caps={'total':cpu.policy.TOTAL_MICRO_USD},
                prior_item6_micro_usd=item6_cost,scope='No-patient CPU infrastructure; original item6 owner remains ACTIVE; full reservation in item6 cap')
            event.pop('prior_item4_smoke_micro_usd');event.pop('prior_item4_total_micro_usd')
        db.execute("INSERT INTO events VALUES(?,?,?)", (ident+":assets-reserved", run, canonical(event).decode()))
        db.execute("COMMIT"); return True
    except BaseException:
        db.execute("ROLLBACK"); raise
