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


### Executable handoff

Actual built-in preparation completed: approval adoption `240e11f18aec01dfccd28da927a389492f08ea02`,
build `aeef70c62f6de9509cf9f7230c3777e7aadfa484`, verification/executable source
`d6a1184b4378e849213fd887a6f7b103fb1a64d5`, notebook artifact
`1a81c037343598f4e4585153b11d761b87a9ae3a`. Both notebook schemas and all cells
validate/compile, have no saved outputs, and include the expected exact-pin
fetch. All 19 approved source/test hashes and the original approval receipt are
present at the executable source pin. The real verify command passed its
four synthetic tests and selected 99 cases/198 members without opening payloads.

The exact Colab links, minimal instructions and return requirements are in
P001_HANDOFF.md. No scientific result exists yet. The next operator action is
CPU Colab connection and Run All. Remote cleanup remains a separate explicit
approval; its c8124212 projection, preserved originals and unresolved 047
acceptance decisions are unchanged. The final metadata-only publication commit
will receive a complete pre-push audit; CHECKPOINT names the concrete prior tip
it attests rather than claiming an impossible self-referential Git hash.


### Published handoff and real GitHub acquisition check

The pilot push through `836aaa6981b6f3595f4b29b4e2f13881a5d93e86` succeeded.
Its complete outgoing audit covered 20 commits/143 artifact versions, manifest
`7416dcb0dae7a37a9937514935c9619e2129af76927c9eb3e6e11f96e8c7ebfe`.
The actual notebook acquisition cell then ran locally against GitHub (only its
/content destination changed to /tmp), fetched only d6a1184b, could not access
940293b6, verified the current review and selected 99/198 with zero payloads
opened. REMOTE_SOURCE_VERIFICATION.json preserves that result. This metadata
update changes no reviewed code, specification or notebook. Main stayed 4f5b6b1
and the unexecuted cleanup source stayed 940293b6 on remote reinspection.


### Colab MCP Windows/WSL diagnostics

At implementation HEAD 0be7ea44f95538a88c53a4d177f85d6ba82c5d2d, configured
only colab-pilot's Windows BROWSER and WSL variable forwarding. Homepage launch
was operator-confirmed and Windows-to-WSL IPv4 HTTP retrieval passed. The old
registered process did not reload its environment; official retry timed out
and notebook tools remain absent. Both diagnostic receipts preserve failure
and unexecuted remote stages. No scientific results, patient access or remote
rewrite. Next operator action: restart/resume Codex to retry the pinned synthetic
notebook through a fresh registered server. A successful full test is still
required before any patient MCP workflow.


### Corrected Windows browser handoff after registered retry

At abe4817aa2802526aabdcba03c8d91a7b79c4747, the refreshed server loaded
its configured WSL environment, but Explorer opened a file-manager window;
Google connection returned false and notebook tools remained absent. A scoped
Colab-only Windows Start-Process helper now passes the homepage test with
operator confirmation. Synthetic argument-preservation/rejection checks passed.
The corrected helper requires a fresh registered process; no remote synthetic
execution or retrieval has occurred. The next operator action is restart/resume.
All failures remain recorded; no token, patient data, Drive or GPU was used.


### Connected MCP, notebook tools unavailable — 2026-09-05

With the corrected Windows helper, the official registered connection returned
true; a second connection-status call also returned true. Codex 0.153.4 logged
receipt of the server tool-list-change notification. Repeated discovery in this
active turn still exposed only open_colab_browser_connection. This establishes
a working browser/MCP handshake but not a working notebook execution route.
The precise internal refresh failure remains undetermined. No remote notebook
was loaded, executed or retrieved. The exact notebook bytes at 1a81c037 were
rehash-verified locally without running its cells. The complete test has not
passed. COLAB_MCP_CONNECTED_TEST_20260905.json records results and a token-free
log excerpt. Next diagnostic: keep the connected tab open and check tool
availability on a new conversation turn, without another server restart.


### Complete remote Colab execution and retrieval — 2026-09-05

With the Claude Code client and the `colab-worker` server, a fresh browser
connection unlocked the full notebook tool set in the same turn. The exact
synthetic notebook at 1a81c037 was loaded into the connected blank session and
byte-verified before execution. Acquisition of source pin d6a1184b passed its
integrity checks remotely; the synthetic write and a separate retrieval both
returned exit 0. A labeled supplementary transport cell (read-only retrieve
only) carried the JSON back: returned text and SHA-256 equal the pinned
expectation 776c3a10f968497c0ced99011f78f8375079c6f7545dab2445921e298473a800, on a CPU-only Colab runtime (no nvidia-smi,
COLAB_RELEASE_TAG present). The acceptance test in COLAB_MCP.md has passed end
to end; receipt in COLAB_MCP_REMOTE_EXECUTION_20260905.json, token-free. No
Drive, patient data, GPU, paid provisioning, cleanup or branch change.


### Automated Claude Colab worker integration — 2026-09-05

Preserved the successful interactive receipt at 04385ed546189d942f7383b162e28de9e65dac37
without modification. Its notebook/source pins and returned text/hash verify.
Claude Code succeeded; Codex notebook-tool discovery remains unresolved.

Milestones: be7d67f3a13a2244257125f2b6d0b8aed5a39aad added the private
request/result adapter and P001 transport preparation; 31bc39b43d8f853ed946a6a2c72b6726e96ab125
added synthetic remote dispatch; 7ff038c29d32098c9826d20e11a058f3eafc38e5
hardened protocol validation after review. An actual automated remote replay
from that clean commit completed the three pinned cells and separate read-only
transport retrieval. Captured tool exchanges, source readback, subprocess exit
results and returned bytes were validated locally. This establishes orchestration,
not merely the earlier interactive session. Complete raw CLI protocol is private
under ~/.local/share/isles-colab-mcp/worker-runs-20260905; failed attempts remain.
Synthetic fd-level console missing from MCP was not reconstructed. P001 wrappers
capture both fd-level and Python output privately and preserve the original runner
console; those wrappers have synthetic tests, not patient execution evidence.

1456af5fbe443272463544c2c833a2d5b3bad613 fixed missing-output failure receipts
and strengthened transport provenance. A fresh independent Fable review APPROVED
that revision for synthetic execution and P001 preparation; original responses
for all three review rounds are versioned. Its non-blocking recommendations remain
in the response and integration receipt. There is no patient-dispatch command or
patient-dispatch approval implied by this adapter review. A separate worker session
performed execution; reviewer sessions used no Colab configuration or tools.

18 relevant tests pass in an isolated environment with pinned P001 dependencies.
P001's existing review remains valid; its preflight selected exactly 99/198 and
opened zero payloads. P001 notebook pin remains 1a81c037343598f4e4585153b11d761b87a9ae3a,
executable source d6a1184b4378e849213fd887a6f7b103fb1a64d5. Private execution
packets contain unchanged original cells and separately hashed transport wrappers.
No patient run, aggregate import, interpretation, or follow-up experiment occurred.
The user has not yet supplied the actual archive/staged-root path. Next action:
provide that Colab-accessible path so the bounded P001 execution handoff can be
finalized; browser/Drive authorization will be requested at the point of use.
Pending results-branch cleanup remains separately unapproved and unexecuted.
CLI usage estimates are recorded without claiming extra subscription charges;
human intervention time remains unavailable. See CLAUDE_WORKER_INTEGRATION_20260905.json.


## 2026-09-05: input discovery and reviewed patient dispatch

Continued from 85d2797f94e121ff6b216f8d1687925f00cb0d4d. Operator ran
plain Drive consent in the browser; remote checks confirmed an actual mounted
Drive and CPU runtime. Completed breadth-first filename metadata search found
only `/content/drive/MyDrive/staging-16731717/train.7z`, 99,022,114,670 bytes.
Pinned P001 expects 99,014,629,647 bytes and MD5
36ae28b9a17f7340b8bbef62b595cb57. This establishes an input identity mismatch,
not corruption: no content was opened to locate or assess that copy. The copy
is preserved. The initial depth-first search timed out; its incomplete result
was not treated as exhaustive. Resumable breadth-first search completed.

Patient dispatch implementation bf3f33d53d741d1ab7e153ed3d7f7231ac65056f and
regression correction aede8f0d4ee2568514d5ca8ad1a37532334d254b received Fable
approval, recorded at 67f81c37ed22031c26756f6459251b12bbfd67b4. Investigator
then identified and fixed a real-mount check needed before capture creates
output/log directories: 465a0c3b1f2e8486a13e68dfd2179b3bfd16840d. First
follow-up review failed with “API Error: Connection closed mid-response. The
response above may be incomplete.” It has no approval. A fresh retry completed
with actual claude-fable-5 APPROVE, source/response hashes validated, adopted at
4234ede (p001-dispatch-r2). Static reviews did not execute tests. Historical
scientific approval, notebook 1a81c037343598f4e4585153b11d761b87a9ae3a and source
d6a1184b4378e849213fd887a6f7b103fb1a64d5 remain unchanged and valid.

User reported previous archive corruption and fresh Colab downloads. Investigator
selected fresh record 16813698 acquisition, without weakening identity checks.
Remote storage check returned 220,654,030,848 local free bytes and
209,621,327,872 Drive free bytes. Preparation bdf4369996364511e8bd824d4711907fa5fb71ea
adds a separate CPU-only background download, private original console, size/MD5
verification before rename, four-hour limit, preserved partials, and refusal on
existing destinations. Separate completed Fable APPROVE is recorded at 79a013e.
Its changed-file bindings and the separate patient review gate both pass.
Acquisition is separately recorded; it is not a scientific experiment result.

29 relevant unittest tests pass, including synthetic 99-case execution, failure,
rerun, archive integrity rejection, private-output capture, and lifecycle checks.
Pytest was unavailable in the isolated environment; the project's unittest route
was used. No actual patient analysis, result import, or interpretation has run.
Original worker/review evidence is privately preserved outside Git under
~/.local/share/isles-colab-mcp/p001-handoff-20260905. Metadata-only execution
receipt: P001_INPUT_DISCOVERY_20260905.json. CLI usage/cost estimates are recorded;
actual additional charges and human intervention duration are not measured.
Codex notebook-tool discovery remains unresolved; execution client is Claude Code.
Pending public-history cleanup is still separately unapproved and unexecuted.


Acquisition actually dispatched through Claude Code; four separate status
retrievals returned RUNNING. Filename metadata showed 5,108,662,272 partial bytes,
last written one second before observation: active transfer, not completed
integrity validation. Original private logs and partials are retained. No P001
patient run has been claimed from these acquisition statuses.

Serial controller f0c2310fac9a91159fc4168b4eb0412ec77a792b initially tried to
rewrite latest.json through an exclusive writer. Investigator caught that real
bug; corrected at bdc42897adbcafb10b81ce188645124f456da8cb and added a test of
actual receipt writes. The initial Fable APPROVE assumed overwrites were allowed;
that superseded review is retained and not used as the gate. Fresh completed
Fable APPROVE of the corrected revision was adopted at 04c14d1. Four synthetic
controller tests pass (33 relevant tests total across this checkpoint).

The serial controller now runs detached locally, with evidence under
~/.local/share/isles-colab-mcp/p001-handoff-20260905/automatic-handoff. It polls
only fixed statuses, waits for archive VALIDATED, rechecks all three source-bound
approvals, dispatches the fixed-path P001 packet once, and polls its semantic
validation result. Failure, unknown status, or observation limit stops the chain;
no mutation is automatically retried. Successful patient validation stops at
NEEDS_PRIVATE_RETURN_TRANSFER. No import is possible until original console,
private checkpoints, and the aggregate return are transferred privately and
validated locally. Keep WSL and the connected CPU Colab runtime alive. This is
an active execution handoff, not a completed scientific result. The controller's
outcome.json is authoritative; a crashed controller may lack that file, and a
zero process exit code alone is not a success receipt.


Download recheck: original controller stopped at acquisition poll 2 when browser
connection returned false; it had never dispatched P001. Fresh read-only Claude
worker check confirmed RUNNING, 20,786,970,624 partial bytes (about 21%), zero
seconds since last write, and no final archive. This is active transfer, not
integrity success. Complete private evidence retained. All three review gates
pass; unchanged controller restarted in exclusive automatic-handoff-r2 directory
after verifying every prior event was acquisition-only. No download was restarted.
Receipt: P001_DOWNLOAD_RECHECK_20260905.json. Keep WSL and CPU Colab alive.
