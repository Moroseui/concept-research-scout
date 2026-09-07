# Bounded hosted transport verification

The original PR CI fetch exit 128 remains unexplained. The reviewed stderr
adapter is implemented; original failure evidence and the absence of its Git
stderr remain recorded. A passing new fixture cannot identify that old cause.

`deploy/research-system/verify_git_transport.py` reuses GitLedger with 24 requests
and eight independent clients against an isolated file-transport bare repository.
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
