# Bound provider Volume path and one exact linked recovery

The installed download stopped before receiving any data because Modal exposes
`/volume` as a provider alias. The private writer correctly refused a symlink
ancestor. The correction does not relax that writer. The controller passes the
recorded data Volume ID; the worker accepts only `/volume` resolving exactly to
`/__modal/volumes/<that ID>`, verifies canonical ancestors and stable identity,
then uses that canonical directory. Every child still uses the same owner-only,
no-symlink, no-hardlink writer. Wrong IDs/targets and unsafe children refuse.

The pinned SDK's `volume.py` uses this internal path. Provider documentation
(https://modal.com/docs/guide/volumes) specifies sync of the Volume mountpoint.
The old launcher committed a scope subdirectory. The corrected launcher commits
the bound mount root after every download checkpoint and at final completion.
The provider alias layout has been reproduced in a real local bubblewrap
namespace; the failed remote container's filesystem router is not used as proof
of a target stat. A live success remains required and will fail closed if the
actual mapping differs. There is no speculative paid capability probe.

Administrative recovery selects only mount-failure binding fab901a1 (full ID in
source), linked to original interpreter-failure binding db2121f0. Both original
UNCERTAIN rows, FAILED records, provider evidence and complete reservations stay
unchanged. Root-bound source/configuration/install/unit records authenticate the
entire chain. Immediately before a new reservation, the service account checks
both ledger rows and current authenticated provider terminal logs and empty
Volumes. The mount failure's output is compared by exact hash, not quoted in a
review packet. The original failure remains exact as previously reviewed.

The new package is fresh, independently verified, and changes executable bytes
only. Original plan references, all file hashes/sizes/source URLs, cohort bytes,
authority, attempt labels and retention deadline stay fixed. New source and fresh
state are required. Both prior reservations count in unchanged item4 smoke and
total caps and actual billing/headroom checks. No scientific allowance exists.
Any other uncertain row, pending new child, changed binding or changed content
refuses. A verified successful child closes only these two ancestor failures for
downstream admission. It never edits or refunds either row. A further failed
child stays blocking; no generic recovery rule is added.

Authority is the operator's existing item4 direct-download approval, dollar caps
and autonomy charter permitting infrastructure repairs through tests, automated
submit_review and held promotion. This draft is not installed and authorizes no
unreviewed launch. Required remaining gates: full server suites; private-copy
ledger/sidecar rehearsal; genuine ordinary approval; held promotion; installed
checks; fresh provider terminal/empty proof and actual billing before one launch.

Tests label synthetic cohort, SDK, HTTP and installation provenance explicitly.
Native tests run the actual emitted launcher, downloader and private writer, and
prove root commits and refusal of alternate aliases/unsafe children. Ledger tests
use actual parent selection, both rows, package verifier, provisioner and budget
transaction. They check duplicate admission, retained costs, unrelated failures,
limits and refusal without writes. No tests claim real data or paid execution.
