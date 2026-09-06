# Deterministic reports and fresh-review queue

`python -m orchestrator.operations_report finalize --root PRIVATE_ROOT --source
FULL_SOURCE_SHA --day YYYY-MM-DD --receipts SANITIZED_RECEIPTS.json` creates one
immutable, digest-named Markdown report and a SQLite review request. `queue` and
`status --report-id SHA256` inspect the same state. The root is private, owned by
the current identity with mode 0700; output files use 0600. Publication is a later
controlled operation, never an implicit effect of report generation.

The phone-readable report summarizes completed, failed and blocked counts and a
compact job/resource table, followed by scientific-evidence limits and named
dependencies. The full normalized sanitized receipts are preserved separately as
an immutable `<SHA256>.receipts.json` primary-evidence file; its hash and relative
link appear in the report. Only explicitly synthetic receipts support saying the
record contains synthetic work exclusively. Operational success is not an
inferred scientific result. Unavailable measurements remain explicit.

The input is a list of closed-schema receipts: job_id and status are required;
source, attempt_id, wall_seconds, peak_rss_kib, cpu_seconds, artifact_sha256, kind,
backend and reason are optional. Missing values stay null. String identifiers
cannot contain paths or arbitrary console prose. Unknown fields, unsafe text,
invalid hashes and nonfinite measurements refuse before report creation. The
adapter must select sanitized receipts; this scanner does not prove arbitrary
clinical information is safe. No patient data or original console is accepted.

Repeating the same finalization produces the same report identity and one queued
review. A correction uses `--amendment-of ORIGINAL_REPORT_ID`, creating a new
immutable report while retaining the original. The source pin and report digest
bind each queue row. The proposed nightly schedule is **21:00 America/New_York**;
the operator has not selected it. This differs from the admission ledger's UTC
day. No scheduling service is installed by this module.

The execution adapter calls `Queue.claim` once per fresh Claude review attempt.
Concurrent claims and restart recovery cannot claim a REVIEWING row again. The
adapter reconciles an interrupted invocation using its private execution evidence
and calls `unavailable` with the original attempt identity if necessary. Failed
or unavailable reviews remain NOT_REVIEWED. Three explicit claims are permitted;
further attempts block. Deterministic polling consumes no model admissions, and
this queue never invokes a model itself. The caller must enforce the protected
admission policy for actual model execution and schedule retry delays.

After validating an actual completed Claude execution, the trusted adapter calls
`Queue.attach` with its claimed attempt, checked review text and exact receipt:
family, actual model, source, report_sha256, review_sha256,
execution_receipt_sha256, session_id and status COMPLETE. Original model evidence
remains private. The function checks these explicit bindings, not the authenticity
of a supplied execution receipt: that is the execution adapter's responsibility.
Synthetic tests use labeled fixtures and establish no real Claude execution.
The adapter must supply approved goals, the pinned report, permitted primary
receipts, relevant changes and unresolved prior findings to the fresh reviewer.

`Queue.disposition` saves Astra's checked response after review. Neither the
review nor disposition schedules another review, preventing recursive reviews.
This is internal cross-family quality review and grants neither scientific
acceptance nor independent main-merge approval.

Implemented here: deterministic report bytes, immutable amendments, source-bound
review queue, claim deduplication, honest unavailability, capped attempts and
checked result attachment. Still requiring separate demonstrated integration:
actual fresh Claude invocation and primary-evidence inspection, protected
publication, remote wake/disposition, chosen scheduling time, phone delivery and
authenticated operator response. A saved report does not prove any of those.
