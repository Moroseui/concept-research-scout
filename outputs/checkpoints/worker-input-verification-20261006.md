# Worker input verification checkpoint

The fit adapter previously streamed all preprocessed image data through the controller before every fit. Draft 983b5124f2ca03f01e41461061b4aca912fb3694 moves full byte verification into the actual read-only worker mount, before any reviewed scientific code starts. The controller still checks the authenticated complete file list and sizes before reservation, and still verifies package and wheel hashes.

A private, job-bound verification record is persisted before execution. Changed bytes, unexpected or missing files, aliases and duplicate launch attempts refuse. Collection requires the matching verification record. The same execution intent, timeout, confinement, cohort checks and spending controls remain.

361 focused tests and 14 subtests passed on the final draft commit. These include actual synthetic subprocess execution and verification-record consumption by the provider. They are not live Modal, GPU or patient-computation results. Full suites, independent review and deployment are still required before this draft is used.

The separately installed retrieval correction has passed its installed full pytest suite. Orchestration tests remain running; the existing gated watcher may enable retrieval only after all checks pass. No new scientific call or paid job ran in this checkpoint.

M4 remains incomplete: actual experiment initialization, executable packaging, admission, collection, validation, interpretation and final reporting still need their connections. No operator decision is pending. Implementation and the gate watcher still depend on the laptop. Private source history, evidence and patient material remain excluded from this public archive.
