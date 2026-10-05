# M1 fix batch

Purpose: make the accepted manual lane portable and recoverable before server CPU/GPU execution. No new scientific run, locked-patient access, old-unit change or budget reset is included.

| Required fix | Caller/implementation | Verification |
| --- | --- | --- |
| Startup Claude token-copy cleanup | Driver.advance and review runner's exclusive lock -> manual_isolation.cleanup_stale_claude_copies; exact per-call homes only; live process/alias/unreadable native process refuses | Stale token removed, host login unchanged, alias refused, live child prevents cleanup |
| Commit original interpretation and format repair | UPDATE_STATE copies authenticated original/repair artifact rows into the same acceptance commit | Existing sentence-boundary/readability tests plus provenance commit check |
| Deduplicate identical host refusals | manual_host_control.hook hashes stable cause; preserves first record and updates latest pointer | Repeated identical refusal yields one original with original timestamp |
| Host prerequisites before first write | deploy_manual_lane.host_prerequisites called by both new-lane installer and promoter | Account, executables, systemd, TLS/DNS files, package layout/pins; scratch promotion and missing-prerequisite checks |
| Newer Claude package layout | manual_runtime.claude_entry uses declared relative JS or executable ELF bin within actual package; all native command builders reuse it | Observed server2.1.222 uses bin/claude.exe; nested JS/native ELF works; escape/missing/private-root package still refuses |
| One recorded infrastructure reexecution | tools.manual_execution_recovery -> ManualExecutor.reemit_infrastructure_failure | Explicit terminal operator-bound evidence, same package/code, failure copy preserved, second/uncertain/changed/completed return refused, no model call |
| Network preflight before reservation/submission | connectivity.require in scientific/implementation admission and manual submit/reexecution | DNS subprocess5s plus HTTPS5s/provider; outages leave zero rows/charges; status records connectivity. Scientific phase stays unchanged only for pre-reservation network refusal |

Promotion after the completed RC6 run preserves it verbatim; only COMPLETE lanes whose calls are all COMPLETE may be retained while installing a new version. Live, uncertain, incomplete or malformed state still refuses. No migration or allowance initialization occurs. M2's separately authorized acceptance lane is initialized later under its own caps.

M0's first installations bound a fixed request list. `deploy_autonomy_review.register_request` now permits another immutable packet to use the already-installed reviewer source/runtime and the same accounting store. It adds only a new request binding and disabled unit from the existing template. Existing code, requests, reports and ledger are unchanged. The M1 review itself uses the previously installed8ff reviewer bytes; this new registration function is not used to approve itself.

Network success means DNS and HTTPS reachability, not credential validity or guaranteed model completion. HTTP401/403/404 prove reachability; rate limits/timeouts/5xx refuse. No API credential is used in preflight. A later disruption still leaves an uncertain call blocked under the existing no-retry rule. Nightly M5 reporting will use the same saved connectivity status.

All M0 adverse findings retain their original scope: planted candidate50b6ade4 is rejected and never installed. Current source retains whole-package pre-charge checks. Original RC6 format refusal remains FAILED in the ledger; the separate operator-authorized qualification receipt binds unchanged native/report bytes.
