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


Second requested download recheck: fresh source-verified remote metadata returned
RUNNING, 73,165,438,976 partial bytes (about 74%), zero seconds since last write,
and no final archive. Integrity remains pending. Controller r2 stopped because
its second worker poll used get_cells without includeOutputs=false; protocol
validation rejected that call. This was not another failed browser connection.
No patient dispatch occurred. Controller remains stopped; do not claim automatic
handoff is active. Receipt: P001_DOWNLOAD_RECHECK2_20260905.json.

## 2026-09-05 system operating-model batch

Starting 0770c7d; origin pilot 0be7ea44f95538a88c53a4d177f85d6ba82c5d2d,
24 local commits ahead and zero behind. Only pilot history was fetched. Preserved
execution worktree /tmp/isles-p001-execution-0770c7d; all P001 scientific review
bindings still pass. Download metadata checks showed 78,223,769,600 then
91,108,671,488 bytes, actively writing. No archive restart or server setting change.

Milestones: dab59d3 workflow/CI boundaries; 2a841fe campaign pipeline/job store;
47c87dc snapshot driver/future profiles; 9a4e0bf review fixes and real discussion;
07c005a verified coordinator approval; 0e8c380 final profile/publication fixes;
7fde0a8 real scoped-profile execution and command reference; 27fefeb completed
workflow/publication approval. Exact reviewed pins: persistent jobs
9a4e0bf77fc1541e13ce7e0d04d38195f6b73601; publication/workflows and future profile
preparation 0e8c3802ca70df7c186d95dc7b9a44bbacf6ee0f. Actual independent reviewer:
claude-fable-5, fresh CLI sessions, no Colab config. All original REQUEST_CHANGES
rounds are retained. No incomplete review is treated as approval.

The real author/reviewer primitive completed three bounded campaign discussions
(the latter two verify evolving future profiles). All prompts, outputs, model
receipts and review JSON are under campaigns/isles24-pilot/pipeline. No scientific
result is inferred from those discussions. New propose/specify/code/repair routes
produce reviewed proposals; adoption and experiment execution remain separate
bound decisions. P002/P003 generation is blocked until prior reviewed results.

272 pytest tests passed; original 214-test orchestration suite also passed before
the final small hardening changes. Fish command sheet syntax checked. Future
MCP profile guard exercised locally with synthetic deny and malformed-input
fixtures; not activated on the current patient worker. Synthetic job demo reached
the private-return inbox. Production persistent coordinator runs from the reviewed
code with SQLite events/leases under ~/.local/share/isles-colab-mcp/
p001-system-jobs-20260905. It polls the frozen snapshot, caps read-only retries,
and never repeats an ambiguous dispatch. Registration and same-store recovery
are transactional; distinct stores must not be used to duplicate a job.

Authenticated CI diagnosis: missing NumPy dependency fixed by installing pinned
P001 requirements; history fetch restricted to checked source ancestry. Remaining
historical defect is idea 023's claimed approval marker absent from imported source
5aa8b5a183876a991ea7e307d7a6c8a8d3a34c7a. Full local state/registry validation
still refuses it; scientific records were not altered. Original logs/review
protocols are private under ~/.local/share/isles-colab-mcp/system-batch-20260905.

Full outgoing audit at 7fde0a8 checked 52 commits/330 artifact versions, with no
contaminated history reachable; commit messages separately scanned. Final push
runs the audit again with exact source/destination/before pins. Only pilot code,
tests, documentation and permitted stage evidence may be published. Main and
results branches, cleanup, and visibility are untouched.

PRIVATE_COORDINATOR_PLAN.md names proposed resources, credential boundaries and
cost estimates; PRIVATE_COORDINATOR_SETUP.fish only prints commands. Nothing
provisioned; approval and billing/project selection remain external prerequisites.
Efficiency review now includes campaign and explicit worker receipts, remains
proposal-only, and does not copy private fields. Available CLI estimates are not
claimed as new charges; human intervention duration remains unknown.

### Published CI and completed acquisition follow-through

Published audited pilot tip 7e016183396d6cc49aad3591807afc5912a689a4 from
0be7ea44f95538a88c53a4d177f85d6ba82c5d2d by append-only compare-and-swap.
GitHub run 33998753860 passed 214 orchestration tests, 272 pytest tests and
16 isolation tests, then reproduced the documented historical idea 023 approval
provenance failure. Run 33998753437 exposed a YAML colon quoting error in the
quarantined results workflow. Fix 9c35fd4002612e9912da143d1c138dc0313d8ffe
uses a block scalar and adds an all-workflow parse regression test (3 tests pass).
Fresh claude-fable-5 review APPROVE at that exact fix pin replaces the current
workflow receipt; prior rounds and original protocols remain preserved.

Remote metadata-only check reached 98,708,750,336 bytes of 99,014,629,647;
subsequently the original approved acquisition poll returned VALIDATED. The
reviewed persistent coordinator moved to dispatch with zero retries/no inbox.
P001 scientific metrics are still unavailable. Original remote evidence remains
private; permitted metadata is in P001_DOWNLOAD_SYSTEM_BATCH_20260905.json.
No main/results cleanup or paid provisioning was performed.

### Dispatch refusal preserved; final CI reproduced

P001 dispatch did not establish execution. Worker returned FAILED/OTHER before
any Colab tool call (only StructuredOutput); actual reported models included
claude-opus-5 rather than requested Fable. It objected to nested escaped transport
source and detached private capture. This was a worker refusal, not an automatic
approval-review rejection; existing scientific/adapter approval bytes remain valid.
Coordinator conservatively opened AMBIGUOUS_DISPATCH_CHECK_REMOTE_BEFORE_RETRY
and stopped with zero retries. No retry or permission bypass occurred.

Original protocol is retained in the private coordinator attempt directory; public
metadata is P001_DISPATCH_BLOCKED_20260905.json. A separate approved read-only
remote poll completed with NOT_VISIBLE, which cannot distinguish absent job
directory from absent Drive mount. It is not proof that Drive consent is missing.
System discuss author/reviewer completed dispatch-incident-20260905, preserving
its own prompts, review and receipts. The readable transport repair remains a
reviewed discussion proposal, not an implemented or approved execution change.
The existing operator Run All route remains available with the pinned notebook
and ARCHIVE=/content/isles-p001-input-16813698/train.7z, after reconciling remote
state; preserve console and checkpoints and never blindly rerun existing output.

Final code CI run 33999032538 at f4412ae89054e7d8e3fe906a89b2629a5ff73ec3 passed
273 pytest tests, 214 orchestration tests and 16 isolation tests. Only the same
historical idea 023 provenance check failed. The YAML workflow failure is fixed.
Acquisition reports validated; no P001 metric/result import/interpretation exists.

### Archive-preservation priority and corrected CI investigation (UTC 2026-09-06)

User placed archive re-verification/persistence ahead of all P001 dispatch.
P001 remains blocked; no dispatch performed. New system-owned archive route
uses exact MD5/size pins, opaque byte hashing (no extraction), exclusive Drive
copy/read-back, and separate fixed-path process/output/checkpoint metadata.
Independent Fable approved source 1381c84e7d036fc50aed1483f56c62d02f1d842f.
Actual remote launch completed in the original CPU Colab runtime, PID 87587,
job archive-preservation-ec3e76e9b91f40ca847b490f9b5f7bfa under MyDrive/isles-pilot.
Actual launch usage models: Haiku 4.5, Opus 5, Opus 4.8 (requested Fable).
A first read-only poll was refused before tools because its source context was
incomplete; no restart occurred. Fresh Fable approval at
973fd8d4832adbfd7512cdf0e319595c97046f82 covers the clarified read-only handoff;
the on-runtime verification script remains byte-identical. Final archive receipt
is still pending at this checkpoint; historical VALIDATED is not proof.

The previous CI diagnosis was WRONG: 5aa8b5a183876a991ea7e307d7a6c8a8d3a34c7a
was unavailable, not missing its approval marker. Exact retrieval verified the
marker and required binding. CI now fetches only reviewed full-SHA provenance
snapshots with blob:none filtering, then the required byte-pinned marker blob.
A real shallow synthetic fixture proves unrelated blob exclusion and unchanged
HEAD. Validator diagnostics now distinguish unavailable objects/path lookups
from absent contract text. Sanctioned state-materialize refreshed only two
derived fingerprints in each of 023/045/046; all scientific/approval fields and
authority bytes are preserved. 280 tests passed, all 47 state views verify, and
all four registries validate. Additional handoff test suite: 5 passed.
Fable requested changes at 99706ea; completed follow-up APPROVE at
4e584f5c72f90d0bd786f88c773fe57b46c5a74e covers final CI/retrieval fixes.
Original failed/review/worker evidence remains private under
~/.local/share/isles-colab-mcp/archive-preservation-20260906.

### Archive persistence verified and P001 held (UTC 2026-09-06)

Same archive job completed VERIFIED/FRESH_DRIVE_COPY_VERIFIED. Runtime-local
/content/isles-p001-input-16813698/train.7z was re-read and matched exactly
99,014,629,647 bytes and MD5 36ae28b9a17f7340b8bbef62b595cb57 at 00:15:27Z.
Fresh MyDrive/isles-pilot/archive-preservation-ec3e76e9b91f40ca847b490f9b5f7bfa/
train.7z matched the same size/MD5 after copy and destination read-back at
00:34:31Z. Original archive and older wrong-sized staging-16731717 copy remain
untouched. Reported mounted-filesystem free capacity before copying was
115,548,561,408 bytes (required with margin: 100,088,371,471).
Acquisition identity receipt exists and its expected binding matches.

Separate validated poll at 00:42:27Z observed the full-sized destination and no
remaining matching verification process. This is mounted-Drive close/fsync and
read-back verification, not independent provider API durability/quota proof.
Full original job console/receipt remain on Drive and original worker protocols
remain private locally. ARCHIVE_PRESERVATION_VERIFIED_20260906.json is the
token-free receipt; the earlier pending receipt remains as historical evidence.

P001 post-preservation metadata: no matching process observed, expected worker,
output, checkpoint and scientific-console paths absent. The existing coordinator
remains dispatch/BLOCKED, retries=0, with its ambiguity inbox item OPEN. No P001
launch, Run All, extraction, patient analysis, or reserved-case inspection occurred.
Observations are explicitly bounded to the known paths/process patterns.

Two failed polling transports remain FAILED: an initial worker refused missing
source context; another returned metadata but deleted a known initial blank and
changed terminal newlines. Review-approved supplementary-cell validation now
handles only these semantically inert differences, keeps exact write/read-back
identity and raw source hashes, and rejects substantive mutations. Scientific
and archive-start cells retain the original strict validator. The on-runtime
archive script never changed or restarted. Fresh Fable APPROVE at
91a0a5832b5d05167de23d4e1ecdba999963bcf3 covers final read-only liveness monitoring.

Published code pin 3de5fedb492662951aef29d88462e0ff147678f5 passed GitHub run
34001952505: 284 tests, 214 orchestration tests, 16 isolation tests, all 47 state
views and four registries. The earlier incorrect missing-approval diagnosis is
explicitly corrected; source object retrieval is exact-SHA, shallow and blob-filtered.
All historical approval/governance/scientific artifacts remain unchanged; only
three derived view fingerprint pairs were regenerated through the built-in command.

### Bounded main stabilization preparation (2026-09-06 UTC)

Started clean at 42b5252d55d240a0dd0209ff914894c7d95b9999; public pilot matched,
main remained 4f5b6b1dc67084a7882c099fb30a6f9465991a31 and was an ancestor.
Current pilot CI 34002142555 is green. New CURRENT_STATUS.md supersedes obsolete
runtime-local archive and pending CI instructions while frozen review-bound
handoff documents remain byte-identical. MAIN_INTEGRATION.md inventories all eight
workflows and changed user surfaces. Main intentionally keeps seven quarantines;
local system routes remain supported and pilot-only publication is unchanged.
New read-only integration verifier executes only closed diagnostic guards and
checks merge parents/tree and existing source review bindings. Initial tests: six
passed with three mutation subtests. Fresh independent review and isolated full
integration checks follow. No Colab connection, job restart, P001 run or paid service.

Ref cleanup refreshed all 12 advertised refs: only the 047 results branch reaches
173 raw blobs. A fresh private rehearsal reproduced c812421207b6ddcba6516444897c777d8440275a,
16 retained files and exact original failure/exclusions bytes; complete bundle
verified. Raw removal is not anonymization: three retained audit files contain
case-linked metadata. Their residual disposition and 047 acceptance remain explicit
separate decisions. No remote rewrite. First metadata traversal failed on intentionally
missing blobs; separate complete tree traversal plus explicit missing-blob accounting
resolved it without payload acquisition. Partial attempt retained privately.

Fable first review of 644bf488 found advisory verifier hardening and wording issues.
The full workflow filename inventory now rejects duplicate .yaml twins, checks CI
read-only permission/credential invariants, and tests mutation rejection. The test
root assumption and historical-vs-current ref-count wording are corrected. Existing
workflow and scientific source bytes remain unchanged. Follow-up review requested.

### Main stabilization verification complete

Fresh Fable follow-up APPROVE at b23e36d3399f7a343535229ccd83b724c53a1c27;
actual reviewer claude-fable-5, auxiliary Haiku usage separately recorded. Both
rounds completed source-only reviews, not reviewer test execution. No blocker.
Remaining advisory: verifier is not a complete workflow semantic security analyzer;
future CI steps/action pins/optional YAML keys still require source review. The
exact current workflow tree was independently reviewed and stays disabled/read-only
as documented. Inert actioner input remains a harmless legacy UI remnant.

Isolated main candidate 2e9d12f126cb31c71caace482d8f1f0667c1df3c has exact
parents 4f5b6b1... and b23e36d... and tree d03ebb2abe52ca67afdf87b25ab91dd605b13ae8.
288 tests and seven mutation subtests, 214 orchestration tests, 16 isolation tests,
47 state views and four registries passed. Scientific, patient adapter and archive
approval bindings verified; no patient execution. Complete outgoing audit covered
71 commits / 413 artifact versions at b23e36d. Final metadata-only receipt commit
will be audited again before publication. Cleanup replacement reaches zero of the
173 raw staged blobs; originals and prior failure evidence preserved privately.
See MAIN_INTEGRATION_VERIFIED_20260906.json for exact receipts and honest limits.
No human merge/cleanup approval is claimed. P001 unexecuted; no remote coordinator.

### Human usability amendment to held PR #2

Operator explicitly withdrew the previous merge direction. PR #2 converted to draft.
Starting source 0cfa2809d26d685b8cd194b6d08fe40aad697088; main unchanged at 4f5b6b1.
Inventory found real legacy functionality lost by the quarantine. New shared Actions
controls invoke campaign_pipeline/scout.run_agent with explicit request attribution,
source/destination bindings and honest hosted receipts. Existing local CI stripping
helper is not used on hosted stages. Scoped proposal/planning/repair/discussion/brief/
curation routes are implemented, with status/import and legacy-corpus exceptions
explicit in HUMAN_CONTROLS.md. No scientific acceptance or full feature parity claimed.
Original P001 patient/scientific review bindings still verify at 465a0c3... .

Initial synthetic verification: all generation modes traverse author/reviewer stages,
CI receipts remain CI, invalid inputs reject, exports verify bytes/closed paths,
cross-host redirects remove auth, and repeated matching artifacts replay without
model calls. Fresh Fable review and real non-patient workflow_dispatch acceptance
are required before this amendment is presented as usable. Existing Actions Codex
API authentication and Claude subscription OAuth are reused, without new credentials,
spending changes, paid provisioning, P001 dispatch, or cleanup.

Fable r1 completed APPROVE at 6c4d066 (actual claude-fable-5; source-only).
Non-blocking findings were addressed: accurate prompt-export documentation,
restoration of absent STATE, dead profile variable removal, bounded replay lookup
refusal and Claude unexpected-tool protocol checks. Interpretation drafting now
uses the same campaign author/reviewer pipeline after real import and existing
scientific-review gates; it remains a proposal, not adoption/ratification. Legacy
quarantine assertions were replaced with checks that still forbid improvement
publication and require pinned remote actions / exact caller-bound local workflow.
295 tests passed before the final two additional adapter cases. Follow-up review
and live acceptance remain pending; no success receipt fabricated.

### Human controls follow-up review — 2026-09-06

Fable completed APPROVE at `6859e97793bc62212340ec3d8949aeb7c65a4c91` (actual assistant claude-fable-5; auxiliary Haiku usage recorded separately). Original response and source-hashed execution receipt are preserved as human-controls.*. R1 remediations and the newly gated interpretation proposal path were verified source-only; no reviewer tests are claimed. Local full suite: 297 tests and 14 subtests passed; all 47 state views and four registries validate.

Accepted non-blocking limits: status receipts currently report unknown model-call count rather than explicit zero; replay retains a BLOCKED result until a new request ID; the 30-minute job cap can end a worst-case four-stage run before its per-stage timeouts, without a result artifact. Unsigned review receipts and supporting primitives remain protected by source review/CI rather than cryptographic signing. These limits do not authorize retries or new billing. Live Actions acceptance follows at the receipt-containing revision.

### Real human-controls Actions acceptance

Executed source `9117de5e56b824e9bf03e7239518abfecc7a8b16`: confer 34005991921 produced REVIEWED_PROPOSAL through two successful CI-attributed stages; repeat 34006068840 reused identical result/evidence with zero calls. Readiness 34006006493 saved WAITING_FOR_RESULT. Invalid-source 34006007378 saved SOURCE_MISMATCH and intentionally failed. Original validated exports are preserved in docs; original Actions logs remain private. Both push/PR checks passed (34005986667/34005990792). Isolated main candidate d2e732fc49965743674c8c43018dd1091feb4632 retained exact parents/tree and existing approval bindings; 297 tests/14 subtests passed there.

Final verifier tightening retains the earlier deterministic-CI no-secret, no-job-permission-override and nonpersistent-checkout checks alongside restored controls. Three mutation subtests confirm these cannot silently weaken. No hosted runtime file or scientific pin changed after the live demonstration. Fresh final review will cover this verifier and acceptance claims before PR update.

### Final integration review revision

Fable requested changes at 5a820d3: the historical no-secrets substring check missed indexed/whole-context expressions. The current check.yml contains no such access. The verifier now requires its exact reviewed SHA-256 before structural checks; tests reject dotted/indexed/whole-context secrets, extra steps, permission overrides and persisted credentials. No hosted execution or scientific source changed. The renderer is included in the 16 runtime review bindings, and actions_auth.py does export CODEX_HOME through GITHUB_ENV; the review's two conditional concerns are satisfied by existing source, supplied in follow-up. Module invocation is clarified.

The earlier HUMAN_CONTROLS_MAIN_TREE_20260906 receipt certifies only the demonstrated 9117de5 tree, not the eventual PR head. A fresh final-head receipt will supersede it for merge readiness without altering that original. The 5a820d3 isolated tree additionally passed 298 tests/17 subtests and 47-state/four-registry checks. Its provenance retrieval initially failed because the disposable origin URL was unset; after setting that URL, the bounded exact-object retrieval and state checks passed. Both failure logs remain private.

### Final integration follow-up completed

Actual Fable completed APPROVE at `ad3c4660320c8628a54f6562e118e5de07876177`; original response and source-bound receipt are human-controls-final.*. It confirmed the indexed-secret blocker resolved and the existing renderer and CODEX_HOME bindings. Full revised suite passed 298 tests/20 subtests. Runtime adapter approval remains 6859e97 and live executable remains 9117de5; no patient/scientific file changed.

Non-blocking review limits remain visible: exact CI bytes are the enforcement gate (updating its hash requires fresh source review), the renderer's alternate-root helper is safe only in the enforced own-checkout merge route, and a final exact-head candidate receipt is still required before merging. The runner's chained internal exception is caught by the common control and exposed only as a fixed failure code; direct unwrapped adapter use is not a supported human workflow. Stage directories are fresh per round. No raw exception or private log was exported by the demonstrated route. Current PR status remains held/draft pending the owner's decision.

### Bounded PR #2 closeout implementation (unratified governance)

Starting checkpoint 1ecc3f9, clean pilot, unchanged public main 4f5b6b1. Received the operator-supplied Fable desk handoff and applied the operator's corrections. Desk approval of 1ecc3f9 is not approval of this new diff. No new grants, N selection, merge, rewrite, P001 execution or 047 landing occurred.

Implemented pre-publication scan of commit metadata and every outgoing changed blob, including intermediate/deleted content and side histories, reusable exact-operation publisher, repaired legacy checkpoint push without implicit main/rebase, shared artifact/Summary validation, and configurable CAS admission ledger. Limiter remains PROPOSED/n=null with read-only Actions permissions; recommendation N=48 from recorded peak 12. Current local admin Git/API access can bypass scripts; post-push CI cannot prevent exposure. State-writer and stronger exclusive-publication permissions require explicit choices.

047 notebook reproduction used generator 469d29d with acquisition source 9216e6: all ten cell sources equal, top-level metadata equal, only random cell IDs differ. Exact bytes are not equal; run.py was not generated/changed. Separate authoring provenance binds Phase-B probe_code 285ab8f and opposing review 0bd8821 via receipts, parent commits and prompt hashes. The pilot's direct staging-expression change 194cdcd remains unchanged and matches the subsequent cleanup review hash. No original console was reconstructed.

Known local 2a-state branch/reflog tips (ten) all belong to main, no dirty/stashed local work, no merge order choice. Bootstrap authorship is recorded as agent work under operator Git identity; closeout commits use Astra (OpenAI agent), without an operator sign-off trailer.

Initial closeout full suite: 304 passed, one failure because changing scout.py correctly trips P001's current-source dependency gate. The missing-adapter-evidence test now isolates that later gate; the scientific gate itself is unchanged. Infrastructure verification separately verifies the original approved bytes at frozen source 1ecc3f9 and reports current-tree scientific execution blocked for scout.py dependency review. The original P001 files, receipts and executable/notebook pins remain unchanged. This is not fresh scientific approval.
