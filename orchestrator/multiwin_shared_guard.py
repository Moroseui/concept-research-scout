"""Keep all original preparation validation, using the authenticated continuation."""
RUN = "colab-1ad5fafc220b3d65f576ce08"


def bind(driver, verify_grant):
    from orchestrator import colab_simple_full as full, autonomy_limits as limits
    previous = full.validate

    def validate(store, run):
        if run != RUN:
            return previous(store, run)
        full.require(store is driver.store and driver.config["run_id"] == RUN,
                     "EXACT_CONTINUATION_STORE")
        # Exact approved recovery and preserved histories, before the new ceiling.
        verify_grant()
        selected = full._configuration(store, run)
        full.require(selected is not None, "PREPARED_CONTINUATION_REQUIRED")
        config, scope, root, approval = selected
        full.require(config == driver.config, "CONTINUATION_CONFIG")
        owner = full._originals(store.batch.db, scope, root)
        full.require(owner["status"] == "ACTIVE", "CANONICAL_OWNER_NOT_ACTIVE")
        row = store.batch.db.execute("SELECT job,payload FROM events WHERE id=?",
                                     (full.EVENT,)).fetchone()
        full.require(row is not None and row["job"] == RUN
                     and full.json.loads(row["payload"]) == full._grant(config, scope, approval),
                     "QUALIFIED_ACTIVATION_REQUIRED")
        ceiling = limits.global_limit(store.batch, run)
        full.require(type(ceiling) is int and ceiling == 24, "AUTHENTIC_CONTINUATION_CEILING")
        full.require(store.batch.db.execute(
            "SELECT count(*) FROM autonomy_calls WHERE kind='scientific' AND change_id=?",
            (run,)).fetchone()[0] <= ceiling, "SHARED_CALL_LIMIT")
        return scope

    full.validate = validate
    def restore():
        full.validate = previous
    return restore
