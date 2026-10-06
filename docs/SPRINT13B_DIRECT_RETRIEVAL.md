# Direct development-input retrieval

Operator decision: SPRINT13B_DIRECT_RETRIEVAL_OPERATOR_DECISION.txt, SHA256 fa23a858ca16da34b768cd0ec2dc9cd49b0228a6ec21ebbf1d4acd33dfad84ca.

A CPU-only Modal container fetches the frozen 99 development patients directly into a private Volume. No imaging payload passes through the laptop or controller. The selected files are 99 registered 4D CTPs (47,772,428,991 bytes) and 693 original image/label files (6,551,367,410 bytes). The 99 derived brain masks are not part of this public-source route; they retain their existing separate identities and private transfer path. No locked or reserve patients are selected.

The source remains the previously reconciled 16813698/v3 release. The pinned per-file mirror revision is 7bead709cd9f60ed6bea866b7a994a8ecc83db16. Its advertised v2 archive and the official v3 archive have identical recorded archive size/checksum; the limitation remains explicit. CTP verification combines the pinned per-file SHA256 with official archive member size/CRC32. Image/label downloads must match the exact preserved extraction hashes. This is not an official per-file cryptographic signature for CTP.

## Implementation

- modal_ctp_download validates exact cohort/member sets and pinned metadata, permits only the selected HTTPS host family, streams into private partial files, verifies size/SHA256/CTP CRC32, rereads the saved bytes independently and commits each file. Partial failures and attempts are preserved. There is no automatic retry.
- modal_download_package includes only the required standard-library worker, private writer, frozen cohort and plans. The isolated launcher checks the entire package and manifest, then processes images and CTP in separate directories. It performs no scientific computation.
- modal_download_provider creates one bounded CPU Sandbox only after an existing asset reservation. Package upload contains code and metadata, never scans. The mounted package is read-only; data has its own Volume. No credentials, identity token, inbound ports or model tools enter the worker. The pinned client supports a domain allowlist and an empty outbound CIDR allowlist; only the download host family is selected.
- A durable create intent precedes each external mutation. A lost create response cannot cause another launch. Status is read-only and verifies terminal status, bound per-file receipts, every remote member and size, and the final completion record. It reads no image payload on the controller.
- modal_direct_budget uses the existing asset ledger, with no scientific allowance or call. The preparation reserve counts against item4's smoke and total budgets even when preparation and science use different owner records. Original charges remain preserved. The reserve includes six hours of hard-limited CPU/RAM, input storage, receipt transfer and image overhead; actual authenticated billing controls headroom.

## Remaining live gates

This is tested draft infrastructure, not an operational transfer. The server-owned preparation and retention controller is now implemented and tested on a scratch connection. Before launch, run both full server suites, obtain ordinary automated review, and perform held installation/live verification, including the actual new supervisor units. The reservation includes thirty days plus five days for storage deletion/billing lag; it does not authorize unlimited storage or discard scientific evidence. No data or paid job has been launched by this change.

The item4 scientific author/reviewer still own all notebook changes, coverage selection and Modal adaptation. Downloading verified inputs does not approve preprocessing or training.

## Evidence

110 focused tests pass (modal-download-provider-2). These use the real worker, package verifier, SQLite accounting and receipt consumer with synthetic data and simulated HTTP/Modal SDK operations. They are not live provider evidence. The selected real plans separately pass the unmocked frozen-source preflight. One earlier synthetic SQL fixture inserted provider_id in the cost column; explicit column names corrected it, with the original failing log retained.

Supported Modal documentation checked alongside the exact installed SDK 1.6.0 source:
- https://modal.com/docs/guide/volumes (v2 and deletion billing lag)
- https://modal.com/docs/guide/sandbox-networking (domain and CIDR controls)
- https://modal.com/docs/guide/security (persistent Volume lifetime)

## Server controller and release separation

`modal_direct_storage` registers an administrative preparation owner in the existing batch ledger, then reserves and launches once. It cannot reserve a scientific call. A lost provider response blocks instead of creating another container. Successful verification completes that owner, leaving the charge counted for item4. A root-bound additive service/timer runs as the service user with private writes, a read-only system and read-only home access (only the controller reads its existing dedicated Modal credential; no credential enters the worker). The installed release, configuration, package and live timer are checked before provider use.

After thirty days, the same timer removes only successful verified input copies, by exact path and per-file intent. It preserves all receipts, partial failures and charges; active compute or an incomplete attempt prevents removal and is visible in status. Metadata hashes are checked before removal. The downloader reads no training results or checkpoints. Storage cleanup is an existing temporary-copy discipline, not permission to discard original evidence.

The retrieval release excludes unfinished fit execution and notebook work. Its shared item4 policy contains the operator's unchanged caps and actual-rate quotation. The future fit controller's tests retain the check that preparation costs are included even with a different run owner.
