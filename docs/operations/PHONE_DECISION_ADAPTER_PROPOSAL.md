# Phone decision route — proposed, not installed or authorized

Use the existing repository's Issues interface and GitHub Mobile. Proposed
credential: a dedicated GitHub App installed only on the research repository,
with Issues read/write and mandatory Metadata read, no Contents/Actions/
Administration write. Verify available permission granularity during operator
setup; this document does not assert an app or installation already exists.
No credential is to be created or installed under the current implementation batch.

A root-owned notification adapter, under a separate notification UID, receives
only publication-scanned decision packets from the protected controller. It may
create/update one issue per decision ID and post a checked operator mention.
It cannot publish Git commits, activate the limiter, reset counters, launch a
patient job or execute arbitrary comments. The private key remains inaccessible
to driver, reviewer and scientific-worker identities. Installation tokens are
short-lived and remain private. Root/admin can still bypass OS protections;
this design does not claim protection against the operator administrator.

Each packet binds repository, decision ID, source commit, immutable request hash,
allowed response enum, urgency and expiry. Before accepting a reply, retrieve the
comment through GitHub's authenticated API, verify the fixed operator numeric
account ID (not just display name), the exact packet version, and a fresh nonce.
Record comment ID/body hash and consume the nonce atomically. Edits or repeated
polls cannot reapply a decision; a changed request requires a new nonce. Anything
else is an inbox item, never shell text. Notification delivery is deduplicated
separately from decision consumption.

Acceptance sequence after permission approval: send a synthetic decision to the
operator, confirm actual device notification, accept one authenticated version-
bound reply, and test duplicate/stale/wrong-author responses. No phone delivery
or authenticated response is demonstrated yet. Routine items belong in a digest;
only time-sensitive exceptions justify immediate mentions. Schedule remains
unselected. A bot comment alone is insufficient proof of mobile delivery.

The eventual concrete permission decision must separately identify the App's
actual identity/installation, numeric operator ID and protected implementation
revision. Do not conflate this narrow notification permission with the still-
pending publication writer/reset design or 48/96 live admission activation.
