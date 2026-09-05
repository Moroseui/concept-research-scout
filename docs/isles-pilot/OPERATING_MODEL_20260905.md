# Pilot system operating model and checkpoint audit

Operator clarification, 2026-09-05: Codex implements and operates the system as
its delegated investigator. Scientific authoring, code, repair, discussion,
analysis and interpretation must run through receipted system stages. Outer
conversation diagnoses and records decisions; it does not substitute for stages.
This document supplements, and does not modify, the frozen campaign authority.

## Reconciliation and execution isolation

Local starting commit: 0770c7d. Origin pilot: 0be7ea44f95538a88c53a4d177f85d6ba82c5d2d.
Local is 24 commits ahead, zero behind. Origin main remains
4f5b6b1dc67084a7882c099fb30a6f9465991a31. Only the pilot ref was fetched.
No contaminated results history was merged. A detached local execution checkout
at /tmp/isles-p001-execution-0770c7d preserves every P001 binding. Notebook source
remains 1a81c037343598f4e4585153b11d761b87a9ae3a; executable source remains
d6a1184b4378e849213fd887a6f7b103fb1a64d5. No connection settings were changed.
Download check returned RUNNING, 78,223,769,600 bytes, last write one second old.

## Workflow audit

| Workflow | Finding | Autonomous pilot disposition |
|---|---|---|
| checks | Missing P001 dependency; shallow history hid governance objects | Install pinned P001 requirements; fetch full history; deterministic tests only |
| interpret | Hard-coded main pull/push | Explicit SHA/destination guard; legacy stage blocked before CLI/auth; push removed |
| confer | Hard-coded main pull/push | Same guard/block; use campaign discussion locally |
| actioner | Main checkout; dormant main PR path; broad staging | Main operations removed; legacy stage blocked before CLI/auth |
| scout-cycle | Scheduled generation and inferred destination | Pilot manual binding required; legacy stage blocked; no automatic push |
| idea-pipeline | Inferred destination; broad checkpoint staging | Explicit binding required; legacy stage blocked; no automatic push |
| librarian | Inferred destination | Explicit binding required; legacy stage blocked; no automatic push |
| results-validate | Main validator, raw-results PR to main | Historical route only; never invoke for campaign; use local validate/import |

Model workflows additionally require PILOT_REMOTE_RESEARCH_ENABLED=true and still
stop at the explicit campaign-route guard. This is not a functioning remote
campaign implementation. Enabling a repository variable cannot bypass that guard.
No API secret/auth step is reached by these pilot workflows. Remote legacy main
workflow versions remain unchanged until a separately authorized main merge.
Local publisher requires exact source/destination/before pins, complete outgoing
history audit, ancestry, and a normal fast-forward push. It never rebases or forces.

## CI attribution

Authenticated run 33961405934 at origin pilot failed because NumPy distribution
metadata was missing in test_campaign_lifecycle. Pinned P001 requirements address
that dependency. Run 33951379171 at main failed registry validation. Full local
history confirms a substantive pre-existing problem: idea 023 gov-0001 import
source 5aa8b5a183876a991ea7e307d7a6c8a8d3a34c7a lacks the approval marker claimed
for contract 0e223c82f9eb. State/registry checks remain red for this reason; no
historical ratification or artifact was edited to conceal it. Original CI logs
are private under /tmp/isles-ci-audit, not copied into model prompts.

## Capability inventory

| Capability | At start | Route in this batch |
|---|---|---|
| author/specification/code | Incomplete: probe-build only accepts existing reviewed code | campaign_pipeline propose/specify/code produces immutable reviewed proposals |
| investigator discussion/repair | Absent in campaign lane | campaign_pipeline discuss/repair, opposing families, at most one revision |
| adopt/amend scientific specification | Explicit decision and review required | Proposal is not adoption; active P001 never overwritten |
| execute P001 | Approved Colab adapters; brittle monitor | Preserve execution snapshot; persistent private job tracking |
| validation/import/interpretation | Existing campaign_lifecycle commands | Reuse validate-bundle, record-result, interpret-build; require private return |
| human ratification | Historical explicit gate | Unchanged; agent decisions never relabeled human |
| persistent recovery/inbox | Absent | SQLite job/event/lease/inbox store, bounded retries, ambiguous dispatch blocks |
| efficiency proposals | Existing, idea receipts only | Extend to campaign and permitted worker/job metadata |

The authoring pipeline writes proposal artifacts and review receipts, including
failed rounds. It does not create an experiment approval. Follow-up generation
requires the previous reviewed interpretation; baseline plus two comparisons
remains the envelope. New source adoption requires a new bound investigator
specification decision and the existing scientific review machinery.
