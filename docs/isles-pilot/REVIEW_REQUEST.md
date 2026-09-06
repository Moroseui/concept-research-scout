# Bounded Fable reviews — standing export authorization

Please review the implementation from baseline `4f5b6b1` through each request’s exact current commit (recorded in its execution manifest).
The continuation started at `495269bc6f72687f39d8c62ec9e2eb73162c390f`; completed
follow-up reviews cover `4339928a6fe8fe4539a7adc44c501f95ba5a9351`. Review
ranges never stop at the older 45c4a5d pin.
Read-only review; no execution, mutation, remote cleanup, patient-file access or
human ratification. This is an opposing-family review of Codex implementation.
Return concrete findings with severity and file references, then APPROVE or
REVISE separately for publication/lifecycle safeguards and the P001 experiment.

Start with CLEANUP_REVIEW.md (exact proposed operation), 047_LIFECYCLE.md
(unresolved acceptance decisions), and campaigns/isles24-pilot/CAMPAIGN.md.
For P001, review SPEC.md, investigator_decision.json, run.py and
validate_return.py alongside tests/test_prediction_p001.py. Focus on admission
input timing, frozen cohort enforcement, outcome leakage, evaluation/uncertainty,
checkpoint provenance, publication boundaries, stopping and failure semantics.
Synthetic tests are engineering evidence only, never scientific performance.

For the safeguards, review orchestrator/publication.py, publication_subset.py,
scout.py's package_colab/record_result changes, and the relevant synthetic tests.
The exact 047 raw source and original evidence remain private and are not part
of this code-review payload. Review the proposed cleanup script without invoking
its remote operation. No recommendation should be labeled a human decision.

If P001 is APPROVEd, its machine review receipt must identify `actor_type: agent`,
`family: claude`, `verdict: APPROVE`, the exact SHA-256 of SPEC.md and run.py,
bind the delegated decision, AGENTS.toml, executable dependencies and tests,
and reference the actual completed review text/CLI receipt. A receipt must be generated
from a real completed review, not filled in to bypass the gate. It is absent now.
After any revision, review must bind the revised bytes. Regenerate the notebook
to a commit containing the review receipt before a real Colab run.

The operator explicitly authorized repeated bounded reviews through the existing
Claude subscription CLI on continuation. Two independent review requests now
cover publication/lifecycle/cleanup and campaign/P001 validity separately. No
credentials, raw patient files, clinical values, private backups or unreviewed
logs are supplied. Each review records the exact revision and actual CLI model.
Follow-up requests must include all affected changes through their current pin.
The prior export rejection remains historical; it is not a current blocker.
