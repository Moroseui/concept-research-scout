# Recorded Issue6 steering and reconsideration

Issue6 intake records a plain-language request and sends a deterministic receipt.
That receipt is not Astra assessment. Nightly reports receive bounded change
context and can discuss it, but their free-text disposition is not a formal
investigator selection. A deferred investigator therefore needs the fixed
reconsideration route to receive a new recorded request.

`recorded_steering` supplies only the protected original reader for that route.
The existing broker must authenticate the caller and verify the current installed
setup before calling it as root with the installed controller configuration.
`list_recorded_steering(controller)` returns verified request IDs and proof hashes,
plus named blocked originals. `read_recorded_steering(controller, request_id)`
returns exactly `request_id`, `original_sha256`, `request`, and `provenance`.

Both functions read fixed `/etc/research-system/issue-intake.json`, the fixed
controller configuration, and `/var/lib/research-system/issue-intake`. They use
normal read-only SQLite snapshot semantics, immutable root intake files and the
existing root attestation reader. The saved controller-owned change request is
checked with the existing pure identity validator and must match the actual
numeric operator, comment/version/body, source and root-recorded outcome. A
declared human label or an agent-created change request is insufficient.

The proof hash is SHA256 of `change_requests.encoded` applied to the object with
`request_id`, `request` and `provenance`, excluding the proof's own hash. It includes
original file hashes but no observation time, bot receipt state, later change
events or mutable reply counters. Duplicate intake and acknowledgment delivery
therefore retain the same proof. Root per-event reservation in the existing
reconsideration route owns processing deduplication; this reader consumes nothing.

Only the latest genuine PROPOSAL-to-RECORDED version of a comment created after
intake enrollment can start new reconsideration. A plain proposal edit has a new
request ID, retains its earlier version and supersedes that version for fresh
use. Edits of controls/quotes need a new comment. Controls, bots, historical
comments and unrecorded or malformed requests cannot start this route. Preserved
older originals remain available through their existing intake/change records;
completed recovery must reuse its saved proof rather than re-admit old steering.

Discovery is bounded to300 current proposals and fails visibly if that inventory
requires reconciliation. It returns only IDs/digests and named blockers; prose is
returned only for the exact selected request. A symlink-resistant descriptor walk
protects reads through the controller-owned request tree. No notification key,
network call, model, permission change, task admission or state write occurs here.

The request always remains `request_only`. The installed reconsideration workflow
must perform its normal provider-backed eligibility, investigator/opponent stages,
recorded disposition, pause/halt checks and admissions. This helper neither adds
a generic comment event bus nor changes scientific or reserved human authority.
