# Readiness implementation review disposition

The fresh author-operated Claude Fable review of `16c9f4d6da29acd83d18e078369050bf5091b59a`
returned REQUEST_CHANGES. Original protocol and rejected verdict are retained.

- Fixed proposal-directory traversal: canonical containment within the pipeline
  directory and explicit rejection of parent traversal precede loading a receipt.
- Fixed the pre-claim crash window: an existing attempt without a result blocks
  that task, leaving independent tasks eligible. Claim is checked before dispatch.
- Completion guards now read state inside their transaction; block/inbox writes
  are transactional both standalone and inside an existing transaction.
- Recovery verifies the original attempt binding and deterministic metadata
  contents before accepting a completion. It never retries an uncertain task.
- Local temporary profile directories are cleaned. The process-global stage
  primitive is explicitly single-writer; readiness worker threads cannot call it.
  Actions retains its separately reviewed hosted profile and runner provenance,
  not a falsely identical local profile.
- Legacy unqualified scouting now selects the baseline cycle rather than the
  lexically last cycle of another charter. Explicit cycle references are supported.
- Automated checkpoint commits use a neutral system identity. Stage receipts
  identify actual model authors; historical commit identities remain unchanged.

The review was source-only and did not run tests. New regression tests exercise
traversal rejection, the crash window with independent progress, actual scout
context/blinding, and charter-target separation. Follow-up review is required
before claiming this revision approved or deploying it.
