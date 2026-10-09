"""Connect compute admission to the exact owner created by ExperimentDriver.

No new owner, allowance, approval or ledger transition is created here. The
legacy owner contract remains scoped to legacy callers; canonical item4 must
resolve the actual initialized lane and frozen preparation.
"""
import json
from pathlib import Path
from orchestrator import private_records as pr, experiment_context as context
from orchestrator.manual_executor import digest
from orchestrator.modal_item4_policy import AUTHORITY
from tools.deploy_manual_lane import bound


def verify_item4(batch, run, owner, execution):
    if run != context.ITEM4_RUN and 'execution_scope' not in owner:
        if owner.get('backlog_item') != 4 or owner.get('experiment_authority_sha256') != AUTHORITY:
            raise ValueError('ITEM4_SELECTED_RUN_REQUIRED')
        return
    fields = {'state', 'source', 'run_id', 'plan_sha256', 'review_sha256', 'execution_scope'}
    if (not isinstance(owner, dict) or set(owner) != fields or run != context.ITEM4_RUN
            or owner.get('run_id') != run or not isinstance(owner.get('state'), str)
            or not Path(owner['state']).is_absolute()):
        raise ValueError('ITEM4_EXPERIMENT_OWNER_REQUIRED')
    from orchestrator.spending_continuation import lane
    continued=lane(batch,run,owner,execution.get('source'))
    state = continued[0] if continued else bound(batch.filesystem_root, owner['state'])
    config = json.loads(pr.check(state/'lane.json').read_bytes())
    raw = pr.check(state/'preparation-plan.json').read_bytes()
    plan = json.loads(raw)
    if (config.get('owner_binding') != owner or config.get('run_id') != run
            or config.get('source') != (continued[1]['source'] if continued else owner['source'])
            or config.get('plan_sha256') != digest(raw) or owner['plan_sha256'] != digest(raw)
            or config.get('execution_scope') != owner['execution_scope']
            or (continued is None and config.get('engine_review', {}).get('sha256') != owner['review_sha256'])):
        raise ValueError('ITEM4_EXPERIMENT_OWNER_CHANGED')
    selected = context.validate_selection(config, plan,
        bound(batch.filesystem_root, config['context']))
    from orchestrator.experiment_plan_output import enabled
    execution_pin = selected["plan_sha256"]
    if enabled(config):
        import sqlite3
        from types import SimpleNamespace
        from orchestrator.experiment_approval import verify
        database = pr.check(state/"jobs.sqlite")
        db = sqlite3.connect(database.as_uri()+"?mode=ro", uri=True)
        db.row_factory = sqlite3.Row
        try:
            row = db.execute("SELECT payload FROM manual_state WHERE id=1").fetchone()
            if row is None: raise ValueError("ITEM4_EXPERIMENT_STATE_REQUIRED")
            driver = SimpleNamespace(state=state, config=config,
                context=bound(batch.filesystem_root, config["context"]),
                root=bound(batch.filesystem_root, config["root"]),
                store=SimpleNamespace(db=db))
            current = json.loads(row["payload"])
            approved = verify(driver, current)
            from orchestrator.item4_validation_admission import scope as validation_scope
            validation_scope(approved, execution, bound=True)
            if ("validation_admission" in approved and execution.get("execution", {}).get("approval_sha256")
                    != current["reviewed_execution"]["sha256"]):
                raise ValueError("ITEM4_VALIDATION_SPENDING_SEAL_CHANGED")
            execution_pin = approved["authored_execution_plan"]["sha256"]
            if (execution.get("spec_sha256") != digest(pr.check(Path(approved["spec"])).read_bytes())
                    or execution.get("review_sha256") != approved["review_sha256"]):
                raise ValueError("ITEM4_EXECUTION_OWNER_BINDING")
        finally:
            db.close()
    if (selected['item_number'] != 4 or selected['authority_sha256'] != AUTHORITY
            or execution.get('source') != config['source']
            or execution.get('execution_plan_sha256') != execution_pin):
        raise ValueError('ITEM4_EXECUTION_OWNER_BINDING')
