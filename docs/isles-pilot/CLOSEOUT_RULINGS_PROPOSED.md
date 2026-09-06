# PR #2 closeout — proposed rulings, not ratified

The operator supplied the Fable Review Desk handoff dated 2026-09-06. Its
conditional normal-merge verdict covers head `1ecc3f9`, not the new closeout diff.
The operator's subsequent corrections control this proposal. No number, standing
capability, permission change, merge, patient launch or scientific landing is
ratified by this document. The new candidate still needs independent desk review
and an explicit operator signature. Internal author-operated Claude reviews are
useful cross-family checks, not independent desk approval.

## Corrected R1 — review and publication

Side branches are agent workspaces. During development, the author chooses when
to invoke internal model review. Each merge into main requires independent desk
review of the actual candidate and an operator signature; depth follows the diff,
with particular care for orchestration, workflows, scientific execution and
governance. Keep branches milestone-sized. Existing scientific contract and
opposing-family experiment gates remain in force.

Every authorized automation route must validate outgoing content **before** Git
publication, Actions artifact upload or Summary release, on every destination it
supports. All automation must use the controlled publisher, including checkpoint
pushes. A request inventory is not a privacy review or human signature. Post-push
CI is additional detection and cannot undo exposure. The present local admin
credential can bypass these scripts using Git or GitHub APIs, and main has no
server protection. Therefore universal pre-publication enforcement is **not yet
established**. Before claiming it, the operator must approve an exclusive,
restricted writer design and removal of direct credential bypass; no credential
scope or repository permissions change under this proposal.

## Corrected R2 — authorship

The 78 bootstrap pilot commits through `1ecc3f9` used the operator's Git identity
for agent work. That metadata is preserved; the task record identifies the Codex
implementation lead and separately attributed Claude workers/reviewers. It is not
proof that the operator authored or signed off on each change. Going forward,
Astra-authored commits identify `Astra (OpenAI agent)`; other agents identify their
own authorship. Operator review/sign-off is a separate recorded decision, never
inferred from committer email. No history rewrite.

## Corrected R3 — proposed standing capability and job-count limiter

Subject to ratification, Astra may dispatch the supported Actions controls using
the **existing Codex API-key arrangement and Claude subscription OAuth**. Claude
pipeline reviews consume the operator's subscription quota. **N remains the
operator's choice; recommendation N=48**, based on a measured daily peak of 12
and a four-times-peak allowance. This is a job-count loop detector, not a dollar
limit or new billing authorization. Existing experiment compute limits and all
reserved decisions remain in force. No new credentials, paid provisioning,
spending-cap changes or unrestricted cost experimentation are granted here.

Counting is repository-wide across main/pilot and all seven controls, by GitHub
run ID plus run attempt, in UTC calendar days. A new dispatch that replays an
artifact still counts; reruns with a new attempt count; retrying the same admission
identity does not count twice. Admission is before models and input validation,
so admitted invalid/failed/cancelled attempts are not refunded. Queued jobs that
never reach admission consume runner time but no model admission; direct unrelated
workflows/credential bypasses remain outside this limiter's enforcement boundary.

Admission N persists an operator notification and continues. At most 2N admissions
are allowed; admission 2N persists the hard notification and latches a halt for all
later admissions. Already admitted/running jobs are not cancelled. Ordinary daily
counts roll at 00:00 UTC, but the hard halt **survives midnight** until an explicit
operator reset. Reset starts a new counting epoch, preserves prior events/notices,
and needs the exact current sequence plus separately authorized operator evidence.
Policy/N changes also require reset; another branch cannot silently choose a
larger N against the same ledger. Duplicate admission recovery is distinct from
exactly-once scientific execution and does not authorize restarting patient work.

Notifications are a durable ledger outbox plus a validated Actions Summary/warning;
phone push/email delivery is not guaranteed. They may be repeated on recovery.
Activation needs a reviewed initialized metadata-only state ref and **separate
permission approval** for a narrowly isolated admission writer. Current workflow
permissions stay read-only. The implementation is configurable but PROPOSED/inactive;
merely merging it neither activates the limiter nor grants dispatch at will.

## Corrected R4 — reserved decisions

047 scientific acceptance/landing, public-results history cleanup and P001 launch
each require separate explicit operator approval. Merging infrastructure is none
of those approvals. The queued 047 registry is not scientific acceptance. Keep
original evidence, exclusion/disposition questions, missing-console gates and
validation/import/interpretation requirements intact. Do not begin the queued 047
landing merely because the infrastructure PR merged.

## Corrections to F4

`package-colab` generates the notebook, **not run.py**. Reproduction of the current
047 notebook gives equal cell sources and equal top-level metadata; all ten
random cell IDs differ, so byte identity is false. The disclosed historical
generator/source overlay is part of the reproduction inputs, not a reconstruction
of the original session. `run.py` has separate historical probe-build authoring
and opposing review records, plus a directly implemented staging-boundary change
reviewed afterward. No retrospective generation record is invented.

Published `2a-state` is already contained in main. The known project checkouts,
worktrees, stashes and ten 2a-state reflog tips show no unpublished 2a work. No
separate merge or merge-order choice is needed; undisclosed other machines are
outside this inspection.
