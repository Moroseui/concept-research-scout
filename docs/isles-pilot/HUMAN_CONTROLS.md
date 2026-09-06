# Human controls and autonomous operator route

PR #2 is held for this usability amendment. Nothing authorizes a merge, public
history rewrite, P001 dispatch, or new paid provisioning. The operator authorized
bounded non-patient Actions acceptance runs using existing Actions authentication
and spending arrangements. This adapter reuses the existing Codex Actions API-key
arrangement and Claude subscription OAuth secret; it does not create an API key,
change a spending cap, or describe API usage as subscription usage. The frozen
campaign, scientific source, notebooks and older reviews remain unchanged.

## Phone operation

After the proposed merge, open the repository in a mobile browser → **Actions** →
one of the controls below → **Run workflow**. Select the branch deliberately;
main and `astra/autonomous-isles-pilot` are the supported sources. Choose P001,
a stage, and a short question without patient details. Leave source SHA blank to
bind the exact selected revision, or supply a full SHA to require a match. The
only destination is `actions-artifact`; no main/result Git publication occurs.
The request ID defaults to `default`. Repeat the same inputs and ID to retrieve
the existing result without another model pass. Change the ID deliberately after
repairing a blocked attempt or asking for another analysis.

Open the finished run's **Summary** for the phone-readable answer, critique and
next action. Download `human-control-<request digest>` for RESULT.md, receipt.json,
and evidence.json with the original permitted system proposal/review records.
Artifacts have 90-day retention. They are not private patient-data storage and are
not permanent Git checkpoints. Export permitted artifacts for longer retention;
original patient consoles/checkpoints must use the separate private route.

Before merging, acceptance uses the existing registered workflow names with the
pilot ref through GitHub's workflow_dispatch API. This is the same Actions event
as the button; it is not a claim that a person physically tapped the mobile UI.
The current main version still exposes its older form until the PR is merged.

## Previous functions and current replacements

| Existing button/workflow | Previous function | Supported human and Codex route | Result / exception |
|---|---|---|---|
| scout-cycle | Broad multi-track/nightly literature discovery and ranked backlog | `scout-cycle`, `propose`: campaign proposal through campaign_pipeline | Reviewed proposal; no adoption. Global multi-track generation, live literature search and nightly scheduling remain explicit exceptions; this bounded campaign control does not claim parity with them. |
| idea-pipeline | Global shortlist, critique, debate, revise and feasibility | `idea-pipeline`: choose specify, code or repair; campaign author then opposing reviewer, one revision maximum | Reviewed spec/code/repair proposal with original artifact contents in evidence.json. It never replaces frozen specifications or adopts code automatically. Global backlog mutation remains outside this route. |
| confer | Reviewed numbered-idea Q&A | `confer`, discuss: ask about the registered campaign using bound source/aggregate context | Answer plus independent review. Arbitrary numbered-idea Q&A remains an exception because its historical grounding can contain case-level records; the hosted adapter cannot export those wholesale. |
| actioner | Operator brief and optional improvement proposal/PR | `actioner`, brief: campaign evidence, blockers and next decisions through the author/reviewer pipeline | Reviewed readable brief. No automatic improvement PR or main push. |
| librarian | Whole-corpus connection mapping and novelty re-audit | `librarian`, curate: campaign evidence/gap curation through the same reviewed pipeline | Reviewed campaign curation. Whole-corpus ledger updates and new searched novelty verdicts are not claimed. |
| results-validate | Fetch raw results branch, validate, open import PR | `results-validate`, status: existing campaign grounding/import-integrity gate | Readable readiness result, including WAITING_FOR_RESULT. Private return transfer and full validate-bundle/record-result remain outside public Actions; no raw branch is fetched. |
| interpret | Adversarial interpretation after import | `interpret` invokes the shared campaign author/reviewer pipeline after existing scientific-review and aggregate-import integrity gates | Reviewed exploratory interpretation and proposed next decision; blocked on the currently missing P001 import. Adoption into the frozen acceptance lifecycle and human ratification remain separate. No CI receipt is relabeled local to satisfy the older acceptance engine. |
| checks | Deterministic validation | Push/PR checks remain active | Tests and state/registry verification. |
| Human ratification / Colab Run All | Explicit human decisions and notebook execution | Unchanged pinned notebook and authority commands | Not delegated to these buttons. No P001 execution in this amendment. |

The restored controls provide real scoped campaign operations, not complete legacy
corpus feature parity. These exceptions are deliberately visible. The present
milestone supports direct human campaign use, while future broader restoration
requires aggregate-safe grounding; the current hosted interpretation is a reviewed proposal, not an acceptance transaction.

## Shared system, attribution and execution provenance

Codex uses `python -m orchestrator.human_controls` with the same control/mode,
experiment, request, exact source, destination and request ID, declaring
`--initiator codex`. On Actions the dispatch input carries that declaration. The
receipt separately records the authenticated GitHub actor and the declared operator;
neither is called human ratification. The system's author remains Codex and its
opposing reviewer Claude. Both human and agent requests use campaign_pipeline and
scout.run_agent, not an outer conversational substitute.

The hosted stage adapter leaves SCOUT_CI set and requires github-actions-v1 runner
identity on both successful receipts. It does not call the local helper which
strips CI and credentials. The original local behavior is preserved. Hosted
metadata records source, run ID, attempt, workflow ref, initiator, CLI identity,
authentication class and the reviewed adapter. Tool-free structured output is
written by the trusted transport under a closed output schema; models cannot run
patient workflows or Git publication. The configured CLI versions are fixed.
Codex API authentication follows the [official authentication route](https://developers.openai.com/codex/auth).

Publication checks the complete export file set, content limits and retained
hashes before Summary/artifact release. No raw logs or private failure files are
uploaded. Original permitted proposal/review records are in evidence.json, including
failed-review rounds when publication-safe. Low-level CLI diagnostic streams stay
in ephemeral runner storage; their hashes/available usage are receipted, but their
long-term private retention is not claimed. Missing/unfunded/rejected credentials
produce a real blocked state; no new billing or permission bypass is attempted.

Artifact reuse requires exact source, request hash, original control workflow,
completed workflow_dispatch provenance and matching retained bytes. Cross-host
artifact redirects strip the GitHub authorization header. Jobs serialize repeated
requests; GitHub may cancel superseded pending runs, which are not successful runs.
After the 90-day artifact expiry a repeat can become a new execution, explicitly
limited by the source's reviewed execution caps (two rounds, four model calls,
30-minute job timeout). No unlimited retry loop is installed.

An incomplete replay lookup (over 100 same-name artifacts with no eligible result
on the inspected page) blocks rather than silently spending on a fresh execution.

## Demonstrated acceptance — 2026-09-06

At executable `9117de5e56b824e9bf03e7239518abfecc7a8b16`, a real
[confer dispatch](https://github.com/Moroseui/concept-research-scout/actions/runs/34005991921)
completed the shared Codex author / Fable reviewer pipeline and saved a readable
Summary, RESULT.md and original permitted evidence. [Read the preserved answer](human-controls-acceptance/34005991921/RESULT.md).
The [identical repeat](https://github.com/Moroseui/concept-research-scout/actions/runs/34006068840)
reused byte-identical evidence and prose with zero new model calls.
[Readiness](https://github.com/Moroseui/concept-research-scout/actions/runs/34006006493)
returned WAITING_FOR_RESULT; [invalid source](https://github.com/Moroseui/concept-research-scout/actions/runs/34006007378)
returned a saved SOURCE_MISMATCH refusal. Neither is counted as the positive
generative demonstration. These were API-triggered workflow_dispatch events on
the pilot; no physical phone tap or new main UI is claimed before merging.

All other generative control modes have meaningful synthetic shared-pipeline tests;
only confer has been exercised with real hosted models in this bounded batch.
P001 remains unexecuted. End-to-end patient operation independent of a laptop is
still unproven. See [acceptance receipt](HUMAN_CONTROLS_ACCEPTANCE_20260906.json).

Completed Fable reviews approved `6c4d066` and the affected follow-up `6859e97`.
Accepted limitations include a null model-call count on zero-call status reports,
replaying old BLOCKED results until the request ID changes, and a job timeout that
may expire before all four permitted model-stage timeouts. Raw CLI protocols are
ephemeral, not claimed as durably returned. CLI-reported subscription cost equivalents
are not billed charges; unavailable actual costs and intervention time remain null.
