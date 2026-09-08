# Persistent Drive evidence connector — proposed consent, not an installed grant

Use Google's supported Python client and its hosted desktop Picker, with only
`https://www.googleapis.com/auth/drive.file`. Select the original 047 sibling console
and existing archive once. In the same batch, optionally select the existing P001
preflight receipt, console and admission-header JSON if present (five files total). Register their returned actual IDs privately; a path,
filename or placeholder ID is insufficient. Do not move or copy the 99 GB archive.
New notebooks and bounded run bundles go into one fresh private `research-system`
folder created by this app. New app-created outputs need no individual Picker grant.

Google enforces access to selected/app-created files. **The scope also permits
modifying/deleting selected originals:** our adapter enforces their read-only
role, archive metadata-only access, and the absence of delete/move/share methods.
It refuses archive downloads. New private uploads are limited to 32 MiB per run,
64 flat files, with console and receipt required together. This initial limit is
for evidence and notebooks, not permission to move bulk patient data/checkpoints.
The controller's protected upload spool supplies files; requests cannot name
arbitrary local paths or Drive IDs. Larger scientific transfers need their existing
authorization and a reviewed transport route.

## One setup/consent batch to approve

1. Use an operator-owned Google Cloud project (reuse one if suitable). Enable
   Google Drive API and Google Picker API; no paid product or billing account is
   needed for this proposal. Configure personal OAuth app `research-system` and
   a Desktop client. Set publishing status **In production**, not Testing.
2. Privately install that downloaded client JSON on the server. Run the one-time
   `scripts.drive_consent` helper through an SSH loopback tunnel. Its URL, callback,
   client secret and refresh token stay out of chat/Git. Select the actual original
   sibling console and existing archive in Google's Picker. No archive download.
   Optional existing P001 selections: the receipt and admission-header JSON inside
   the already-dispatched preflight's attempt directory, and its sibling preflight
   console. These can contain a case identifier and imaging-header metadata; they
   stay private. This proposed consent explicitly requests those small audit/header
   records (JSON capped at 64 KiB), not image/voxel data or execution on Linux.
   Missing files mean an unresolved attempt; do not retry the experiment.
3. Permit one dedicated non-root `research-drive` service to use that grant for
   the registered evidence operations. Root owns its source, configuration and
   credential originals. systemd LoadCredential gives only this identity runtime
   copies. Driver, reviewer and scientific workers receive no token or client file.
   The service can write its private evidence directory and read the controller's
   upload spool; it has no sudo, GitHub/model credentials or scientific launcher.
   The controller receives membership in the research-drive group solely for
   setgid staging (directories 2750, files 0640); credential and private evidence
   directories remain owner-only, so group membership does not expose them.
4. Permit creating the app-owned private output folder, collecting the original
   047 console, and a small synthetic storage/restart test. No sharing, publication,
   patient launch, archive transfer or unattended research activation is included.

The concrete App/client identity, actual file IDs, folder ID and installation
receipt will be recorded after consent, before activation. None exists in the
current registry yet. Do not mistake this proposed packet for those actual values.

## Persistence, recovery and enforcement limits

An offline refresh token survives service restarts in protected storage. Google's
client refreshes ordinary access tokens in memory. Testing-mode refresh grants
expire after seven days; that is unsuitable here. Production does not guarantee
an immortal grant: revocation, account policy or token expiry produce a durable
blocked task requiring reauthorization, without scope widening or paid fallback.
Provider error details and original evidence remain private.

Collection records original file version, size/checksum, before/after metadata,
private readback and receipt. Mutation during retrieval blocks acceptance.
Repeated request IDs return the preserved receipt; interrupted work is reconciled
instead of silently retried. Uploads use preallocated remote IDs recorded before
creation, require private owner-only destination permissions and verify readback.
An uncertain upload is held, not repeated under a new identity.

The protected source/UID/configuration boundaries must be installed and exercised
before claiming enforcement. Local fake-client tests are not proof of Google
consent, hosted credential isolation, token refresh, live storage or restart.

## Supported system operation

`python -m orchestrator.drive_evidence request --operation collect --alias
047-console --request-id 047-console-original-0001` uses the existing bounded,
peer-UID-checked broker exchange. `status` recovers that exact request; `metadata`
can inspect the registered archive's metadata. `store --alias run-artifacts` uses
a controller-produced bundle with console and receipt in its protected spool.
`stage --run-root PRIVATE_RUN --request-id RUN_ID` stages a bounded completed
bundle as the controller, with group-readable copies and unchanged originals.
`status --alias run-artifacts` reads a stored upload receipt even after spool
cleanup. Responses contain allowed metadata/hashes, never console contents. Scientific
acceptance and interpretation follow their existing pipelines after evidence gates.

Drive access is separate from Colab. The demonstrated Claude MCP bridge can execute
pinned cells and retrieve results while its browser/runtime connection is usable.
A new Colab connection/runtime or Drive mount can still require a browser. The
persistent Drive connector does not make fresh Colab compute unattended. Linux CPU
preparation continues independently; no browser automation workaround is proposed.

## Sources checked 2026-09-07

- [Google's hosted Picker OAuth flow](https://developers.google.com/workspace/drive/picker/guides/desktop-mobile-picker)
- [Drive scopes and refresh-token storage](https://developers.google.com/workspace/drive/api/guides/api-specific-auth)
- [OAuth refresh-token expiry conditions](https://developers.google.com/identity/protocols/oauth2)
- [Standard Drive API usage and quotas](https://developers.google.com/workspace/drive/api/guides/limits)
- [Preallocated upload IDs](https://developers.google.com/workspace/drive/api/guides/manage-uploads)

Current read-only host inspection found no Drive config, credentials or service at
the proposed locations, and no Google client libraries in the host's system Python.
This does not claim an exhaustive search of all private credentials. Existing Colab
mount authentication is not reused or exported as a server refresh grant.

## Review disposition

Author-operated Claude source review approved `0b427888`; the original review is
retained in DRIVE_CONNECTOR_REVIEW_R1_20260907.json. Its live-API uncertainties do
not supersede Google's explicit hosted Picker and preallocated-folder-ID
documentation. Real consent/storage/restart remain untested acceptance steps.
The upload-status recovery suggestion was implemented. A controller staging
command now provides the private group permissions required for actual service
access; the request does not require the operator to prepare each new output.
Source formatting was checked for AST equality. A stalled formatter process group
was terminated after edits; subsequent targeted tests passed.

## Concrete consent candidate

Core adapter review pin: `9468a7e79d84ab2592a99da7ad2b53ba919af4a6`.
Final executable/source grant pin: `6ea7566b7247286fac54c450ad8f388b129d130b`.
The registration-only extension was approved in DRIVE_REGISTRATION_REVIEW_20260908.json;
this document is not an activated grant. Fresh
author-operated Claude reviews approved the base, recovery/staging changes and
final small delta; see DRIVE_CONNECTOR_REVIEW_FINAL_20260908.json. Final tests:
11 adapter tests, plus two actual Google-library tests using fake providers.
No live credentials or services were installed. The separate grant must bind this
final implementation pin, capability `registered-drive-evidence-v1`, and only the
`drive.file` scope. Later documentation commits do not change that executable pin.

First operator action: approve the four-part setup/consent scope above. Then open
Google Cloud Console and select the operator-owned project to use; setup proceeds
one step at a time, with client/selected-file identities recorded privately.
No existing original needs moving. Previously unselected existing files may need a
one-time Picker grant later; new app-created outputs do not need individual grants.

Remaining minor limitations: a malformed private receipt fails closed with a
generic broker error, and staging-only IDs beginning with `upload-` are rejected
when submitted to the broker. Use the supported run IDs. The existing positive
status-after-spool-cleanup test passed; it was absent from the last review diff
only because it had not changed. These are not untested claims of live recovery.

Before registration, verify the existing controller/driver accounts and root-owned
private setup directory. Inspect registered aliases against the intended selections
before installation. If any setup attempt leaves a folder intent, reconcile that
original intent before using a fresh destination; do not create a replacement blindly.
The script permits fewer than all five files; an absent archive/preflight alias stays
unavailable. It does not establish that a missing preflight attempt never ran.
