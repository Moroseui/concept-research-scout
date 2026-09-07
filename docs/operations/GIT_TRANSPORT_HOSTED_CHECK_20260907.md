# Bounded hosted transport verification

The original PR CI fetch exit 128 remains unexplained. The reviewed stderr
adapter is implemented; original failure evidence and the absence of its Git
stderr remain recorded. A passing new fixture cannot identify that old cause.

`deploy/research-system/verify_git_transport.py` reuses GitLedger with 24 requests
and eight worker threads with 24 independent client repositories against an isolated file-transport bare repository.
The synthetic N=4 policy gives eight admissions, two durable notices and a latched
halt. A fresh client recovers all admitted identities without another write and
checks that midnight does not clear the halt. Actual stderr is retained privately
for every Git invocation, including expected failed compare-and-swap pushes.
No model calls, credential use, external Git remote or live state are involved.

The attempt destination must be absent. A prior directory is an unresolved or
completed attempt to inspect, not something to overwrite or retry. At least 512 MiB
free capacity is required before creation. Hosted supervision additionally binds
non-root identity, immutable source, private durable output, network isolation,
CPU/memory/time limits and a single attempt. Originals are retained; no automatic
log deletion or new production retention policy is introduced.

Local development probe passed: eight admissions, no invocation errors, duplicate
recovery without a changed ledger pin and midnight halt; 947 private diagnostic
receipts with verified hashes/modes. This ran uncommitted fixture code against
library base `a94d886`; it is not the forthcoming committed hosted-source receipt.
Two refusal tests verify preserved existing attempts and insufficient capacity
before mutation. Fresh Claude review and actual hosted execution remain pending.

The [resume reconciliation](RESUME_RECONCILIATION_20260907.json) checks current
installed pins, sign-in status and existing jobs without retrying them. Previously
completed scientific-readiness and synthetic reviews are reused. The three
scientific tasks remain preserved; no patient launch/transfer or 047 import is
implied by this fixture. Shared live admission/reset, writer permissions and
unattended operation remain separately gated.

Actual hosted result: [receipt](GIT_TRANSPORT_HOSTED_RESULT_20260907.json).
The first attempt failed before fixture execution because the installation umask
made the source root 0700; originals are preserved. Explicit source-root chmod
allowed the unchanged reviewed bytes to run once under the worker identity in a
new attempt. Eight admissions, two notices, duplicate recovery with unchanged pin,
midnight halt and 947 private diagnostic hash/mode checks passed on Git 2.43.0.
Duplicate recovery returns the original admitted status even after halt; it does
not authorize another execution. No unknown failed attempt was replayed.

The successful transient unit was unloaded before property collection. Its returned
default properties do not establish runtime resources; requested limits are in the
private dispatch intent. Actual peak memory and CPU accounting were not retrieved.
This is an explicit evidence limitation, not a reason to repeat the passing test.
It is file-transport hosted proof, not GitHub credentialed enforcement, live
48/96 activation, or a diagnosis of the original PR CI error.

Follow-up to Claude’s coincidence question: the preserved local and hosted
original summaries independently both record 947 receipts and 56 failed CAS
iterations. Their outcomes SHA-256 identities differ (`ad67d4fa0a372f0f55734ff203fb21905de32d316d1b7cae915ddb2af438c5a0`
and `c5d6f1067fa63a1d2f8928f483afaeda6a8f7e47c96365750dcc8c9c78fe8efe`). This was verified against both original
files; no rerun or reuse of the local receipt as hosted evidence occurred. The
matching count is an observation, not an inferred shared cause or timing proof.
