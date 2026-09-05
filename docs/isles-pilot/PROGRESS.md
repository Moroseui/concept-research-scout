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
