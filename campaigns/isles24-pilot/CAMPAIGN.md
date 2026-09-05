# ISLES24 autonomous prediction campaign

Operator authorization recorded 2026-09-05 in the initiating conversation.
Investigator: Codex, OpenAI agent family. This document records delegated
campaign authority, not a fresh human approval of any experiment result.

Purpose: improve the research system while preparing and completing reproducible,
readable prediction experiments. Local implementation, tests, debugging, commits
and routine design decisions are delegated. Decisions bind this campaign and an
exact experiment specification; agent decisions are attributed to the agent.
Historical human approvals remain historical and must never be relabeled.

Scope: one credible baseline and at most two follow-up comparisons on the frozen
eligible 99-case development cohort. The 49 reserved cases must not be extracted,
opened, trained on or evaluated. All findings are exploratory because development
outcomes were used in prior work. Predict follow-up infarct using inputs available
by completion of admission CT. Outcome-derived rankings, follow-up images,
outcomes and post-intervention information cannot be prospective features.

Every experiment requires a versioned specification (target, input timing,
patient evaluation, primary metric, baseline, compute cap, failure/stopping rules),
an agent-attributed decision binding its bytes, and opposing-family review of
specification and executable implementation before a real run. An amendment
changes the specification identity and invalidates old authorization. Changes
made after results are seen are labeled amendments or new comparisons, and all
attempts, failures and negative results remain on record. Follow-ups are selected
only after the baseline is returned and inspected; do not pre-run alternatives.

Compute: existing authenticated CLI subscriptions and existing Colab entitlement.
No new API billing, purchase, unbudgeted job or automatic cloud provisioning.
Initially the operator connects and runs the prepared Colab notebook. Preserve
manual Run All and use versioned scripts/configuration behind the notebook.

Publication: only checked code, tests and permitted documentation may go to
`astra/autonomous-isles-pilot`, after outgoing-history inspection. No patient
payload, private evidence backup, credential or contaminated results ancestry.
No main/results-branch pushes. Remote cleanup requires separate explicit approval.
047 publication/acceptance decisions are outside delegated routine research
choices. Preserve Phase A, retinal artifacts and existing scientific records.

Stopping rules: stop a run on identity/scope/input-integrity failure; keep actual
console and partial checkpoints. Stop scientific claims until invalid runs are
resolved. Stop for unavailable authentication, operator compute connection or
review authority. Exhaustion of baseline plus two comparisons ends this campaign's
experimental envelope. A proposal-only efficiency reviewer may recommend changes
with evidence and verification plans; it cannot execute those recommendations.

Measurement: record execution durations, failures, machine/agent identity and
available usage. Human intervention minutes, exact token consumption and dollar
cost are nullable, never invented. Each completed or failed experiment has a
short result card with the question, baseline/change, input timing, result and
uncertainty, limitations, artifact references and next decision.
