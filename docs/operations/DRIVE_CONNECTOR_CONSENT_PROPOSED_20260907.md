# Persistent Drive evidence connector — proposed consent, not an installed grant

Use Google's supported Python client and its hosted desktop Picker, with only
`https://www.googleapis.com/auth/drive.file`. Select the original 047 sibling console
and existing archive once. Register their returned actual IDs privately; a path,
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
3. Permit one dedicated non-root `research-drive` service to use that grant for
   the registered evidence operations. Root owns its source, configuration and
   credential originals. systemd LoadCredential gives only this identity runtime
   copies. Driver, reviewer and scientific workers receive no token or client file.
   The service can write its private evidence directory and read the controller's
   upload spool; it has no sudo, GitHub/model credentials or scientific launcher.
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
Responses contain allowed metadata/hashes, never console contents. Scientific
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
