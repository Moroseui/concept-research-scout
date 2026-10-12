# Research status

- Idea 2 is accepted; the reviewer's limited inspection of two large tables remains documented.
- Three baseline attempts failed before training. Verified inputs and saved preprocessing are preserved.
- Repeats are parked. New arms come first: multiwin and pnormct, then pnorm_v2, then L.
- Multiwin author 10 finished, but its synthetic integrity fixture failed. No corrected notebook is ready.
- The reader repair passed Claude review and its native zero-call check; scientific review 9 is now running.
- Identified billed item 4 compute is $24.487001; known completed Claude charges are $271.66746875, including the completed reader review.
- Action needed: none. Next expected result is a corrected, reviewed, genuinely integration-tested multiwin notebook; allow 2-4 active hours, conditional on corrections. [Execution plan](13B_EXECUTION_PLAN.md).

## Current direction and evidence

One preconfigured notebook per arm: preprocess once, then train and score folds 0-4 sequentially for 250 epochs each. Resume the current checkpoint and verify/skip completed folds. Use Colab's default runtime and A100, private Drive results, frozen hashes and development-99/excluded-49 membership checks. No per-fold delivery, Colab metering, separate smoke or supervised segments.

Multiwin and pnormct are first for two parallel human sessions; pnorm_v2 follows, then L with actual A100 memory-fit evidence. Zscore and histeq remain held. Sprint 12 A1 is the provisional comparator; small differences cannot be interpreted without a later Colab repeat.

Original baseline fold 0, fold 1 and a later fold-0 retry failed at nnU-Net trainer initialization with KeyError continue_training. Original hash/membership checks passed; preprocessing remains. Scientific author 10 supplied corrections, an arm-level notebook and a real trainer fixture. Its pure synthetic integrity test failed because the fixture's windowed values became constant. The author owns that correction; the protective nonconstant check stays in place. No actual trainer iteration has yet run.

Every arm needs actual nnU-Net trainer construction and at least one real training iteration before delivery. Static and mocked tests do not qualify. Subprocess failures must be printed. Historical notebook bytes and approvals remain preserved but held.

## Implementation and live work

Installed source 396a72b passed 199 tests and independent Claude APPROVE (84df2e51, report a0e88072). Its scoped batch-128 continuation preserved all original calls and the daily-50/run-20 limits. Author 10 is COMPLETE, not running.

Scientific review 9 stopped before admission on a dense-patch reader limit. There is no review-9 reservation, call or charge. Preserve its consumed start intent; never replay it blindly. Source fa687145 adds a lossless reading representation within the unchanged 100-line/16,000-byte limit, plus exact recovery of the pre-admission state. It passed 143 focused tests and reconstructed the actual patch exactly. The separate raw patch remains hash-bound; unrelated oversized JSON still refuses.

Administrative review dd297b56 returned genuine APPROVE with no findings, report 57b897b0. Source fa687145 is installed. The native zero-call full-input/transport probe passed without changing state, calls or allowances. Exact recovery preserved all 19 existing calls; the same scientific review 9 is now running as call 20/20. Its pending outcome must be reconciled, never relaunched blindly.

Claude's direction was SIMPLIFY, agreed: finish this review; if it returns scientific REVISE, park multiwin rather than add recovery layers, and admit a genuinely distinct pnormct/all-fold question through the normal lane. Per-run 20 and batch 128 remain unchanged. Obtain reviewed actual trainer integration before any delivery.

A draft GPU integration adapter is parked and uninstalled until scientific synthetic tests pass. No compute reservation was made for it. Timing, author sandbox and opposite-family administrative capability remain deferred; no Swap point.

## Accepted results and other workstreams

Idea 2's single saved-output CPU execution completed in about six minutes. Before/after hashes matched 728 frozen inputs and four package files; all 891 planned cells completed, with 99 development patients and zero excluded overlap. There were 792 saved-table checks with maximum error zero and 198 mask checks. Interpretation and normal finalization are accepted. The reviewer inspected smaller outputs but could not directly read the two largest tables; do not claim full independent numerical verification. See [accepted report and scope](idea2_fixed3x3/README.md).

Item 6 diagnostics and synthesis are accepted. The Sprint 14 comparison's 352 rounded matches use shared saved fits/cohort, not independent retraining. The next analysis intake preserves the author's proposed fixed-amount smoothing comparison. Meeting preparation uses the accepted fixed six-slot selection rule; real panels await asset provenance and geometry checks. No cases have been selected or private images opened for that plan. Model calls are currently serialized by the installed guard.

## Spending and daily calls

Item 4 non-Colab stage-1 exposure is $115.516623/$150: billed $24.487001 plus retained reservations $91.029622. Timing commitment is $5.405445/$25 within stage 1; $1.118950 synthetic CPU awaits billing. Item 6 cap $100; item 4 total $1,275 and full-training projection gate $1,200 remain unchanged. Colab is unmetered. Release excess reservations only after provider billing confirms a closed attempt's actual cost.

12 October UTC: 38/50 counted calls, including running scientific review 9.

| Type | Count | Purpose |
|---|---:|---|
| Scientific author | 9 | Idea 2 code/interpretation, baseline preparation and multiwin authoring |
| Scientific reviewer | 7 | Idea 2, baseline, multiwin review 8 and running review 9 |
| Administrative implementation review | 20 | Necessary repairs, including the completed reader bundle; failed/disqualified attempts retained |
| Standalone direction check | 2 | Next-arm direction: disqualified source-read attempt and qualified SIMPLIFY retry |

Known completed Claude charges: $271.66746875; running scientific review 9 is additional and unreconciled. Latest administrative review cost $4.43091975. Author dollar costs are unavailable. Scientific usage is 106/128; the operator-approved additional 24 calls are allocated up to 16 Colab, four analysis and four meeting. Daily 50 and run 20 are unchanged.

## Judgment log highlights

- Hold old notebooks after real runtime failures; preserve preprocessing, failed attempts and charges.
- Apply the latest one-arm format and new-arm ordering; scientific author owns every scientific correction.
- 12 October 09:45 UTC, one bundled direction round: SIMPLIFY, agreed. Finish review 9; on scientific REVISE park multiwin and move to a genuine pnormct question. No more recovery layers on this run.
- This review bundles reader/state/accounting scrutiny with the required direction check because estimates slipped and administrative overhead grew.
- Keep the original reader bounds and scientific guard; defer the GPU adapter until the authored tests pass.
- Preserve Idea 2's genuine acceptance and disclosed inspection limitation.

## Backup and exclusions

Last verified public backup before this update: bd202449bf27d56a49d6e9c0f9ad7789de5c636e. Current changes require privacy, secret and infrastructure scans before pushing. Latest measured C: free space is 17.23 GiB; server source transfer free space was 113.1531 GiB before and 113.0005 GiB after. Disk guard warns below 15 GiB and stops below 8 GiB. No larger disk requested.

Withhold evidence folders, review packets, ledgers, native streams, private operator records, raw private branch ancestry, patient rows/identifiers, membership maps, images, masks, weights/caches, credentials and infrastructure identifiers. Private bindings withheld include COLAB_MULTIWIN_RECOVERY_PRIVATE.json, COLAB_RUNTIME_FAILURES_PRIVATE.json and COLAB_PATCH_READING_FAILURE_PRIVATE.json. Returned executed notebooks/records and verbatim private approval bindings also stay private. Safe source/test projections are scanned separately. Never merge main or edit BACKLOG.
