# Proposed one-off review route for the stock-take recovery

NOT APPROVED. No review or model call is launched by this proposal.

## Confirmed obstacle

The installed administrative reviewer (`autonomy_review_runner.py:39?40`, SHA256 9afadb267b6c36762d705734293e0c3f1ada19deba3aaf279faac677bdbadb32) refuses every new review when the shared ledger has a RUNNING or UNCERTAIN row. The only such row is the preserved scientific invocation 2019f1b1? for stocktake-c9deb31c7f8668b41df09ea8. Actual installed code reproduced `UNCERTAIN_OR_RUNNING_REVIEW_NO_NEW_CALL` against a private current-ledger snapshot without any charge or production-state change. The scientific recovery cannot be installed before independent approval, and the installed review route cannot admit that approval. The original row must not be cleared or relabelled.

## Smallest proposed decision

I authorize a one-off, separate manual Claude Code review of the stock-take transport/recovery integration on branch astra/m4-stocktake-transport-recovery-20261004, including the narrowly scoped manual-evidence qualification needed for this case, subject to these conditions:

1. Use the existing fixed blocker categories and bounded two-round engine-review process. The reviewer remains independent and may reject or leave the work incomplete. No equivalent rejected resubmission or extra retry is granted.
2. Preserve the genuine original report and available actual session/model evidence. Bind its exact reviewed source, unchanged runtime and analysis plan, scope and final verdict. Record it as operator-authorized one-off manual evidence, never as queue-qualified evidence. Count the review once under the existing limits; no refund or new scientific allowance.
3. The qualification implementation is part of the material reviewed before use. It applies only to the named stock-take recovery and this operator authorization. Missing or altered evidence, ambiguity, unresolved blockers or any non-APPROVE verdict refuse. The importer must not authorize itself.
4. Keep the installed administrative reviewer and its UNCERTAIN guard unchanged. Preserve the original scientific UNCERTAIN rows, charge, source and evidence, and every earlier review scope.
5. All seven conditions of the already approved transport recovery, including the installed full-path dry run of every connection, held promotion, live checks, both server suites and the one-replacement limit, remain in force. No deployment or scientific judgment is approved by this route decision.
6. Continue BACKLOG item1 only if all those gates pass; stop for operator review before item2. This sets no general manual-review or retry precedent.

## Prepared work and next action

The transport/recovery candidate is pinned below with deterministic checks. Its current qualification still requires the ordinary genuine queue result and therefore remains unable to qualify a manual report. If this route decision is approved, the smallest named manual-evidence binding will be prepared and included in the single manual review packet before any use. The packet will contain the exact diff, connected callers and deterministic receipts, excluding raw AI-session material and private scientific originals. No automatic reviewer admission exception, ledger reset or new review framework is proposed.

Candidate before this route decision: 26a3f3b3608844f8a53b9bba453bfd4dbdd1ae9c
