# Main integration contract — infrastructure only

Starting pilot: `42b5252d55d240a0dd0209ff914894c7d95b9999`.
Current public main: `4f5b6b1dc67084a7882c099fb30a6f9465991a31`.
Main is an ancestor of the pilot. This milestone proposes a **normal merge commit**
with those main and final reviewed pilot parents. Do not squash, rebase, cherry-pick,
or delete the pilot branch: scientific notebooks, reviews and execution receipts
refer to existing commit identities. The isolated candidate must have the same
tree as the reviewed pilot. If main or the PR head moves, repeat integration
verification before approval. No main merge is performed by this preparation.

## Human controls supersede blanket quarantine

The operator held PR #2 and required direct human/phone operation. See
[HUMAN_CONTROLS.md](HUMAN_CONTROLS.md) for every former button, its scoped pipeline
replacement, launch/result instructions and remaining exception. Seven named
controls now share a reviewed workflow_call runner. Main and pilot require
explicit workflow_dispatch; outputs go only to validated Actions artifacts and the
run Summary, with source/run/actor/review bindings. No Git write permission,
main/result push, patient input upload, P001 dispatch or automatic adoption is
introduced. Deterministic check.yml remains push/PR read-only.

The pipeline accepts CI only through the explicit github-actions-v1 adapter and
keeps ci=true in its evidence. The existing local helper is unchanged. Original
scientific source/notebook/review pins remain intact. Workflow generation is
versioned, exact wiring is tested, and fresh independent review is required before
hosted model execution. The main integration verifier now verifies this reviewed
wiring and the human-controls approval in addition to the prior scientific gates.
The separate pilot Git publisher remains pilot-only; it is not an Actions result
publisher or main merge tool.

## Other user-visible changes from main

| Surface | Resulting behavior |
|---|---|
| Numbered `package-colab` and regenerated 047 launcher | Exact pinned fetch, staging separate from publishable outputs, no unconditional deletion, actual sibling console capture, verified export rather than automatic Git push. Older frozen launchers are not retroactively rewritten; do not use them to bypass this route. |
| New `record-result` imports for numbered ideas | Require a contract-bound `publication.json` in addition to core validation. Older probes lacking a reviewed policy cannot make new imports until one is supplied; their existing immutable results remain intact. |
| `--publication-subset` | Full source inventory and retained byte identity; only explicitly bound staged-input exclusions, original private evidence required. Cannot omit required scientific/audit outputs to pass. |
| 047 registry and derived views | Two nodes, intended Phase-B path `results/results_v2-dc586665d0be`; Phase A currently derives STALE for missing historical registry attestation and Phase B BLOCKED. No revocation of historical science or fabricated attestation. |
| Historical registry diagnostics | Missing Git objects/path lookups are distinct from contract-binding failure. Only derived fingerprints were refreshed for 023/045/046 through state-materialize. |
| Campaign command lane | Explicit campaign/experiment arguments; agent-attributed decisions; existing numbered human-approval behavior preserved. Build/verify/package/validate/import/interpret routes and bounded author/reviewer proposal/repair/discussion artifacts. |
| P001 | Fixed reviewed baseline, synthetic tests and notebook; no measured patient result. The frozen notebook and executable are preserved, not regenerated just for merging. |
| Colab adapters | Claude worker synthetic execution/retrieval demonstrated; actual output/private evidence separated. Patient dispatch is still blocked after a worker refusal. Codex notebook-tool discovery unresolved. |
| Archive tools | Current on-disk size/MD5 verification, non-overwriting Drive copy and separate read-only status; no extraction/analysis implied. |
| Job tracking/profiles | Persistent leases, deduplication, capped read-only retries, ambiguity inbox; future bounded unattended profile tested. Not proof of unattended end-to-end patient execution. |
| Efficiency/coordinator | Receipt-based proposals only; private cloud deployment plan only. No resources provisioned. |
| README/status/attribution | Current supported routes replace stale Actions instructions. Dataset terms documented; no repository-wide license change. |

Retinal artifacts, historical approvals/ratifications, imported scientific bundles,
reserved cohort boundaries and the approved execution worktree remain unchanged.
No downloaded archive, private evidence backup, patient file or contaminated results
history is added to the pilot/main proposal.

## Verification and merge method

Use a fresh local repository, fetching **only the exact main and pilot commits**
from the local source. Create local `main` at the before pin and run
`git merge --no-ff --no-edit PILOT_SHA` there; never run this in the working pilot.
Run `python -m scripts.verify_main_integration --main MAIN_SHA --pilot PILOT_SHA`
from that isolated checkout. It checks ordered parents, tree identity, clean main,
current scientific/patient/archive review bindings, complete workflow inventory,
and verifies the exact reviewed human-control wiring without launching a hosted job. It never dispatches a job,
merges, pushes, or contacts Colab. Missing main commits or divergent main invalidate
this particular integration contract.

Run the CI test commands in that checkout, retrieving only the manifest's exact
provenance object if needed. Preserve the receipt with main/pilot/candidate/tree
pins and command outcomes. Synthetic lifecycle tests do not create real approvals.
GitHub's PR checks must also pass on the actual prospective merge ref. Approve a
normal merge commit only after reviewing the final PR head. Preserve the pilot
branch for notebook acquisition and commit references.

Public 047 cleanup is a separate leased ref replacement. This PR neither performs
nor authorizes it, and cleanup does not accept 047's scientific results.

## Closeout source-binding qualification

The original source receipts remain immutable. Because this batch repairs the
legacy push path in scout.py, the P001 review bound to that file cannot certify
current HEAD for patient execution. The candidate verifier now verifies the
original scientific/patient approval bytes at frozen source 1ecc3f9 and separately
requires the current scientific gate to report its actual dependency-review block.
It only tolerates the explicitly identified scout.py drift for infrastructure
readiness; unrelated scientific drift fails verification. This is not a scientific
approval upgrade or gate bypass. Existing P001 executable d6a1184 and notebook
1a81c037 remain preserved. A fresh current-tree execution review is separate.
