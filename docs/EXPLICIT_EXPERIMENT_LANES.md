# Explicit item 6 and item 4 lanes in one held release

The selected primary application is item 6 at `state/lane`. An optional companion is exactly item 4 at `state/item4/lane`. Both plans must be present by exact hash in the genuine administrative review before promotion. This adds no descendant-path exemption and creates no scientific allowance.

The promoter preserves each plan and selection, creates separate exact-source repositories, and installs two disabled service/timer pairs. The root-owned `experiment-lanes.json` binds source, runtime, review, both plan hashes, exact lane/repository paths and unit names. Its bytes, each plan and each service are in the selected release hash list. The root hook checks that binding and that the actual service commands address the selected lane. Unknown paths, aliases or changed map/plan/service bytes refuse.

The companion reuses the existing release, runtime, SDK and parent-state `ReadWritePaths`; client logins, model confinement, privacy controls and call/budget limits are unchanged. The driver still validates its own reviewed plan and unique accounting owner at initialization and every transition. Root does not open lane databases; the existing owner reader now observes up to the already-authorized maximum of 30 calls, refusing excess instead of silently truncating.

Promotion refuses initialized unfinished state in either location. Rollback checks both lanes and refuses if any of the four current units is active, then disables/removes only this release's unit files. Source, repositories, lane state, receipts and original units remain preserved. Prior one-lane releases retain their original path and layout.

Operate whole transitions serially, including the root preflight, and leave both timers disabled for this supervised launch. The existing host proof is invocation-bound but uses one shared receipt path; this change does not add concurrency or alter admission. A future operator-loop serialization lock is follow-up work.

Tests use explicitly synthetic approvals and scratch state. They exercise real promotion, both root selections, exact repositories, altered bindings, call-in-progress/no-reset refusals, all-unit rollback refusal and successful rollback without provider or model calls.
