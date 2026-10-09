# Item4 compute-owner connection

The experiment initializer and compute admission now consume the same owner
record. The canonical item4 run must resolve its private lane and immutable
preparation plan. Source, engine-review hash, execution scope, plan and lane
bindings must agree; each compute request carries the selected execution-plan
hash and source. The legacy two-field owner cannot stand in for this owner.
Legacy non-canonical callers retain their earlier contract.

The existing SQLite transaction, actual billing/rates, caps, uncertainty checks,
per-fit duplicate protection and original charges are unchanged. This connection
does not approve a package, reserve scientific calls, or grant another run.

`tests/test_experiment_compute_owner.py` initializes the actual lane, then invokes
the actual compute accounting without patching either consumer. Engine approval,
native preflight and scientific material use the existing explicitly synthetic
fixtures. No provider or model call occurs. Drift and uncertain calls refuse
before a spending row is written. Ordinary review and installation remain gates.
