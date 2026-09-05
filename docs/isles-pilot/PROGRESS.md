# ISLES24 autonomous pilot — durable progress

Campaign opened 2026-09-05. Implementation lead/investigator: Codex (agent).
Authority: operator's explicit campaign instruction in this session; local implementation,
tests, debugging, milestone commits and routine experimental decisions authorized.
Only checked code/tests/permitted documentation may be pushed to
`astra/autonomous-isles-pilot`. No results-branch/main push, remote rewrite,
branch deletion, visibility change, paid job or new API billing is authorized.
Preserve retinal records, prior scientific records, and the reserved cohort.
One prediction baseline and at most two evidence-selected follow-ups, restricted to
frozen eligible 99 development cases, exploratory throughout. Real compute initially
runs through operator-connected Colab. Cross-family review remains required.

## Starting identity and inventory

- Repository: https://github.com/Moroseui/concept-research-scout.git
- Branch: astra/autonomous-isles-pilot; clean starting tree.
- Starting HEAD and current remote main: 4f5b6b1dc67084a7882c099fb30a6f9465991a31.
- Remote 047 tip verified by ls-remote: 940293b6d562f2d3dd6bfd9d8d8281ccf01e4783.
- Parent verified: b652005fbcf6a87765a85e81b381a8596b4384ce.
- Fetched source objects only; no merge. No pilot remote branch initially.
- Read README, AGENTS.toml, both charters, collaborator rules, handoff,
  REVAMP roadmap, latest decisions and 047 Phase-A interpretation.
- Existing capabilities: launcher generator, staged download recovery, validated
  verbatim historical imports, experiment DAGs, contract approvals, cross-family
  interpretation, execution receipts, derived state and research cards.
- 047 registry missing. Phase A remains at probes/047/results/results_v2.
- Root cause: run.py stages inputs below OUTPUT_DIR; launcher copies entire output,
  force-adds it, deletes prior destination, and unconditionally clears Drive output.
- Source success tree: 17 top-level artifacts + 198 staged CSVs. Its diff also
  deletes the prior driver_console.log. Original failure evidence exists in parent.
- Successful-session sibling console log is not in that source tree.

## Measurement and pending work

No new scientific experiment has run. Agent wall time can be recorded; human
intervention time, subscription usage and monetary cost are not available here.
Cleanup requires final operator approval of concrete pinned operation. Exclusion
semantics and missing successful console remain acceptance issues, not decisions
ratified by this campaign. Never reconstruct an original console log.

## Milestone 1 implementation checks

219 tests passed under /tmp/isles-pilot-venv (declared dependencies installed).
The initial system-Python suite failed because PyYAML was unavailable; those
failures are not scientific results. Five new synthetic tests cover output
staging, checkpoint-preserving reruns, actual failure consoles, immutable
exports, symlink/raw-file refusal and executable generated export cells.
047 publication policy is blocked pending audit semantics and console evidence.
No dataset payload was executed by these tests.

## Milestone 2

Implemented a source-complete, byte-verified subset import declaration. Only
staged inputs may be excluded with preserved originals and explicit dispositions;
required scientific/audit outputs remain required. Added the two-node 047 registry
and corrected its Phase-B destination documentation. Registry schema validates.
Real Phase-A historical validation passed. Real 047 Phase-B top-level core
validation also passed, demonstrating that the legacy validator alone cannot
resolve the publication/audit issues. Actual record-result correctly refused on
the new publication policy, with no import or interpretation claim.

Fable review attempt was rejected by automatic approval review because sending
repository source/diffs to the external service lacked explicit export approval.
No Fable call executed. A bounded no-patient-data review request is pending with
the operator; independent implementation continues. No new API billing used.

## Milestone 3 and prediction preparation

Campaign authority and P001 specification fixed at ece94ea, before real execution.
Decision is explicitly attributed to Codex/GPT-6 Astra, not approved by human.
Campaign/spec drift, fabricated human attribution and same-family review are
rejected by tests. P001 preflight selected exactly 198 members for the frozen 99
cases, opened zero patient payloads and selected no reserved case. No real metric
has been computed. Cross-family review is pending the explicit CLI export decision.

## Prediction/MCP/efficiency implementation checks

P001 synthetic 99-case end-to-end execution passes; an identical rerun uses all
99 checkpoints without loading image arrays, and tampered checkpoint metrics
are refused. These are generated fixtures, not scientific results. The real
preflight selected the authorized cohort without opening payloads.

Official Colab MCP b9ab3899e0f1fa493390b1fd6d54aa2e464ecdf1, package 1.0.1,
started and completed an MCP initialize/list-tools handshake outside restricted
localhost permissions. Only the browser-connection tool is exposed before
connection. Actual Codex dynamic tool refresh, Colab execution and result
retrieval remain unverified and require operator browser/authentication.

Efficiency review read 158 receipt records; 96 contain duration measurements,
2 explicitly report errors, 62 lack exit status, and one identical prompt/stage
repeat is observed. Four evidence-bound proposals are written, none applied.
Human intervention time and comparable usage/cost data remain unavailable.

Final implementation validation before notebook packaging: 226 tests passed.
Global record-result now requires a contract-bound explicit publication policy
for every new import; old frozen bundles remain unchanged. The new requirement
has regression coverage through actual synthetic import transactions.

Cleanup originals are now also durably preserved, owner-only, at
/home/partho/concept-research-scout-v4/isles-pilot-private-evidence/ (outside this
checkout). The copied Git bundle passed verification. All 11 advertised refs
were checked for reachability of the 173 distinct raw blobs represented by the
198 staged files: only the named 047 results branch reaches them. The cleanup
operation/pins did not change. No remote rewrite or deletion has executed.

## Commit checkpoint

- 194cdcd491a6: M1 safeguards and cleanup rehearsal script.
- 62e310503f55: first pinned cleanup review package and safe 047 launcher.
- a69b044: M2 subset provenance and proposed 047 registry.
- ece94ea: M3 campaign authority and frozen P001 specification.
- bd99839: publication policy mandatory for all new imports.
- c429722: M4 baseline runner, return validator and synthetic tests.
- 45c4a5d3329b: M5 integration probe, proposal-only reviewer and publication audit.

Both generated pilot notebooks pin 45c4a5d3329b210eea4a3e1b11027b1bca261fe5;
nbformat validation and Python compilation of every code cell pass. P001 is
prepared but intentionally refuses real execution while its actual opposing-family
review receipt is absent. Synthetic notebook is ready for manual Run All.
Local synthetic write/retrieve returned exact expected bytes and SHA-256
776c3a10f968497c0ced99011f78f8375079c6f7545dab2445921e298473a800.
This does not claim Colab execution. Review request is documented separately.

Final consistency pass found pre-existing stale 047 state/card views. Regenerated
only those two derived views, preserving ledger, approvals, interpretations and
all result bytes. Both now verify byte-identically and visibly distinguish the
historically ratified Phase A from the new unratified registry (A STALE/B BLOCKED).
No new ratification was created. The outgoing-history guard has a synthetic
regression proving that adding then deleting a raw file still blocks publication.

## Continuation: independent reviews and lifecycle integration

Verified clean HEAD and remote pilot at 495269bc6f72687f39d8c62ec9e2eb73162c390f;
main and raw 047 ref unchanged. Operator explicitly authorized repeated bounded
Claude subscription reviews. Two separate tools-disabled Claude Fable reviews
were launched over baseline 4f5b6b1..495269b, including current relevant source,
diffs, specifications, dependency declarations, notebooks and synthetic tests.
No patient payload, private original evidence or credentials was supplied.
Both actual CLI review outputs are pending; no approval is inferred.

Independent reviews completed at 495269bc: cleanup APPROVE (no blockers), P001
REVISE (finite-Tmax ambiguity, notebook predating its receipt, broad source clone).
Actual responses and model usage are preserved under docs/isles-pilot/reviews.
Fable authored both; CLI also reports Haiku auxiliary calls. No API key was used.
The cleanup script now has optimization-safe explicit integrity checks, exact
path-diff verification and synthetic test coverage. Optimized real replay retains
the existing proposed c8124212 pin. Local metadata inspection clarifies that three
retained files carry case identifiers; raw-payload cleanup is not anonymization.

## Continued campaign integration and second review round

Cleanup review r2 at `3f0337b986dc52594f4347fdc7d99bb3e7c4a0a2` is APPROVE
for operator consideration only. Original response/actual model usage and source
manifest are retained in reviews/cleanup-r2.*. The c8124212 replacement is
unchanged; no rewrite was executed. The formal metadata disposition now names
all three retained identifier-bearing bookkeeping files as well as exclusions.

Implemented the explicit campaign lane through six existing scout commands,
with delegated agent attribution, opposing-family receipts and scoped commits.
Synthetic disposable Git tests traverse the complete lane; actual P001 runner
and return validator tests use synthetic volumes, checkpoints and aggregate
outputs. Resume after index/checkpoint interruption and unapproved extra output
fields are tested. No real patient execution has occurred.

P001 v1.1 clarifies the existing all-finite Tmax stopping rule before execution.
Review binding now covers the actual completed Claude response, decision and
all executable dependencies. Notebook source acquisition uses an exact-pin,
no-tags, depth-one fetch. Synthetic acquisition tests confirm the unwanted
results branch is absent and dirty/untracked reruns refuse nondestructively.
The notebooks in this revision remain review scaffolds: their source pin will
be regenerated only after a valid review receipt is committed, using the
reviewed generator. They are not yet the executable handoff.


### Follow-up review findings and bounded corrections

At `4339928a6fe8fe4539a7adc44c501f95ba5a9351`, P001 r2 and cleanup r3 both
returned APPROVE with no blockers. Original responses and source/model/usage
receipts are retained. No P001 approval receipt was adopted from that revision:
subsequent improvements require a review of their changed bytes first.

Corrections address ambiguous multi-verdict parsing, experiment-specific review
scope, ambient role rotation, dependency checks before synthetic verification,
empty Git commits, and source-byte continuity from validation through import.
Review bindings now also include AGENTS.toml and the relevant synthetic tests.
Failed interpretation evidence deliberately stays local for inspection; the
code no longer commits partial evidence and then appends a dirty failure event.
No partial interpretation can grant follow-up authority.

The expanded review found a pre-existing `.nomatch` extraction cell in the 047
notebook that could never meet its 800-file floor. It was regenerated through
built-in packaging with an empty suffix list (archive-only staging); its runner
owns selective extraction. The legacy generator now also fetches only its exact
pin and preserves existing source directories. Optional ungranted Colab secrets
are handled like missing secrets. This repairs packaging without running 047 or
changing its blocked acceptance/publication policy.

A live synthetic interpretation witness used the real built-in executor with
existing authenticated Codex and Claude CLIs: both succeeded and the synthetic
interpretation was approved. Codex console identified gpt-6-astra (the older
receipt parser left model_used null); Claude receipt identified claude-fable-5.
It contained only n=2, mean Dice=0.5 fixture numbers, not patient evidence. The
first witness used then-uncommitted integration fixes; a committed-source replay
will provide the durable exact-revision witness. Local smoke execution/retrieval
also returned the expected synthetic text/hash. Colab itself remains unverified.

## Final source approval and real campaign preparation

Final reviewed implementation: `469d29df002ea78f64146731244769d7c82330d6`.
Cleanup r4 and P001 r3 both returned actual APPROVE with no blocking findings.
P001's review.json was created from the original completed response and execution
manifest only after all 19 required source/test hashes verified. No reviewed code
or specification will be changed during receipt adoption and notebook packaging.

All 233 tests passed (61.384 s); the complete outgoing audit through 469d29d passed.
The committed-source synthetic executor replay succeeded with actual Codex and
Claude CLI calls; original inspected consoles/receipts are in reviews/live-stage-smoke/.
Claude auth status confirmed claude.ai/firstParty subscription authentication;
Codex login status confirmed ChatGPT authentication. No API billing was introduced.

Remaining nonblocking review advice (not silently represented as fixed): notebook
packaging reruns advance their source pin; interpretation review parsing and
untrusted-text framing can be tightened; follow-up gating can additionally
re-inventory its prior aggregate bundle; some diagnostic exceptions remain raw.
These do not permit running a follow-up without its own reviewed specification
and code. Partial failed interpretation evidence deliberately remains local for
inspection; this does not require new operator permission for authorized fixes.
Other cleanup advisories concern defense-in-depth path matching/timeouts, not
the unchanged leased operation. The actual 047 launcher source dependency entries
were verified locally and recorded in reviews/047-launcher-source-check.json.
