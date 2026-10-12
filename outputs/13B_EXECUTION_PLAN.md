# 13B execution plan

Updated 12 October 2026, 22:41 UTC. New experiments first; repeats are parked. Scientific authors write the notebooks and analysis; Claude reviews them. Every arm needs a real nnU-Net trainer construction and at least one training iteration before full notebook delivery.

| Order | Arm and folds | Venue and owner | Current release condition |
|---|---|---|---|
| First, session1 | A1_multiwin,0-4 | **Partho on Colab**, default runtime,A100 | Author12 and five synthetic groupsPASS; Synthetic-only package APPROVE/delivered; Partho runs freshA100check; fulltrainingheld until returned evidence is scientifically accepted |
| First, session2 | A1_pnormct,0-4 | **Partho on Colab**, default runtime,A100 | Delivered unchanged after real trainer PASS; Partho reports RUNNING |
| Next | A1_pnorm_v2,0-4 | **Partho on Colab**, default runtime,A100 | Author, scientific review and real integration |
| Then | A1_L,0-4 | **Partho on Colab**, default runtime,A100 | Same checks, plus actual A100 memory-fit evidence |
| Parked | A1_repeat and A1_repeat2,0-4 each | Partho on Colab later | New arms must have results first; saved preprocessing stays |
| Held | A1_zscore and A1_histeq,0-4 each | No run | Coverage-source provenance unresolved |

Each released arm gets one preconfigured notebook: preprocess once, train and score folds0-4 sequentially at250epochs, automatically resume the current checkpoint and verify/skip completed folds. Frozen file hashes and development99/excluded49 membership fail closed. Results stay in a distinct private Drive folder per arm. Subprocess errors print on failure. No per-fold files, Colab accounting, balance prompts or supervised segments.

**Current action for Partho:** run/return the delivered multiwin synthetic trainer check in a fresh A100 session; leave pnormct running. Pnormct's unedited all-fold notebook is already delivered and running, SHA25630bb6ba0d2904cff6f7725c40693dd5b7ef196989f23455e46d6814b12c986f6. Built-in estimate14hours/94.78CU. Return completion/error and executed notebook; private Drive outputs use the built-in arm folder.

Send each full training file immediately after its required checks pass. When both first arms are released, run two parallel Colab sessions, one per arm, each processing five folds sequentially. Exact filenames, hashes, built-in paths and result-return instructions accompany each delivery. The system verifies private Drive results and routes them to analysis as they arrive.

At Sprint12's measured36seconds/epoch,5folds x250epochs imply12.5training hours before preprocessing, validation and checkpoint overhead, or84.63CU at6.77CU/hour. This is a reference, not a new-arm measurement. Multiwin's prior15-20hour estimate and L's35-45hour estimate remain provisional; replace them with measured steady-state timing. Original1001units buy about147.86A100hours at that rate; the balance does not limit the plan and Partho manages purchases. Automatic resume handles session interruptions.

Compare each arm provisionally with Sprint12A1. Small differences are not interpretable without a later Colab repeat. Attribute changes to placement versus amount, size, region and fragmentation; no efficacy claim from code or integration tests.

**Server work:**

Smoothing saved-output CPU execution completed once: valid,304.77seconds,99development patients, zero excluded overlap,728input and4package hashes unchanged before/after,198equal-amount and792saved-table checks passed. Five private aggregate outputs validate. Scientific interpretation is now independently accepted; see the aggregate summary below.

Namespace repair03a42f24 remains installed and unchanged. Its original pre-client admission refusal is preserved. Read-only diagnosis proved all109 frozen ledger rows unchanged; the checker used spaced JSON where the frozen manifest used compact JSON.

Serialization recoveryd035b2a6 passed203tests and actual read-only verification of109rows,15prior calls and32pre-client workspace files. Independent Claude review23e5c998 returned APPROVE, reportf13b8abf, with PROCEED direction. It is installed. Recovery preserved the original workspace, state, calls, configuration and grant; no new allowance. The native check passed the corrected allocation boundary and author transport without model calls.

Smoothing interpretation author3 and scientific reviewer3 are COMPLETE. Reviewer3 returned qualified APPROVE with no findings; exact authored output and MCP submission hashes were verified. Normal runtime finalization recorded acceptance with report SHA256 4b45e7ce7c01782994ebab4e79e206aa4ebd56d00ffe69f75bf374cf2c4f30fd. Local17calls; global117scientific. No server model call remains running. Never replay these starts or rerun the completed CPU analysis. This bounded analysis grants no successor execution. [Accepted aggregate summary](SMOOTHING_RESULTS_20261012.md).

Item6 diagnostics, saved-results synthesis and Idea2 fixed3x3 interpretation are accepted. Sprint14's352rounded matches share saved fits/cohort, not independent retraining; the Idea2 review's inability to directly inspect its two largest tables remains disclosed.

Next arms are pnorm_v2 then L, with real A100 memory-fit evidence for L. Repeats parked; zscore/histeq held on coverage provenance. Compare provisionally against Sprint12A1 and do not interpret small differences until a later Colab repeat.

Meeting preparation retains the accepted six-slot rule; no cases/images selected. Existing Drive access was queried for root-folder metadata through its already-approved service lifecycle, then restored inactive. Zero roots named isles-pilot were visible through this narrow route; this does not establish project-wide absence of MRI or clinical data. No credential changes or patient payload access. Source provenance remains unresolved; do not broaden access.

Timing reconciliation confirms author24's real CPU integration PASS; do not repeat it. Later review16 failed before reservation because a separate confined read-only ledger access could not open its database. No reviewer16 call or GPU timing run occurred. A bounded reviewed repair of the actual admission path is needed; preserve all evidence and caps. Author sandbox and opposite-family administrative review capability remain unfinished. No Swap point; pnormct is also running externally.

12OctoberUTC:65/100 calls, returning to50on13October without resetting history. Scientific batch117/128:7Colab,0analysis,4meeting remain. Known completed Claude charges $380.62437450; author dollar costs unavailable.

| Type | Count | Purpose |
|---|---:|---|
| Scientific author |15|Idea2 specification/interpretation, baseline and multiwin, pnormct corrections, smoothing specification and accepted interpretation; includes the preserved pre-client failure|
| Scientific reviewer |12|Idea2, baseline, multiwin, pnormct and smoothing scientific review|
| Administrative review |36|Admission/accounting repairs, packaging, dated policy, execution and interpretation integration|
| Standalone direction |2|Preserved disqualified attempt and qualified SIMPLIFY retry|

Item4 non-Colab stage1 exposure $115.516623/$150 = $24.487001 billed + $91.029622 retained reservations. Timing $5.405445/$25 is inside stage1; synthetic CPU $1.118950 awaits billing. Item4 total $1,275/projection gate $1,200 and item6 $100 cap unchanged. Colab is unmetered by operator decision. This continuation launched no new provider compute. Only confirmed closed provider billing can release excess reservations; uncertain/open obligations stay counted.

Current action: run13B_A1_multiwin_real_trainer_check_review11_PRIVATE.ipynb in a fresh default A100 session, Run all, no settings. Keep the other pnormct session running. This approved package runs authored unit fixtures then one real synthetic training iteration/checkpoint roundtrip, not a full fold. About10-25minutes, roughly1.13-2.82CU informational only. Final cell copies evidence privately, excluding caches; return printed status and folder. SHA25644902e1ebca592a796a5194bd05aa828af7748c18728b7d0f1c4e162f899877b.

-22:38UTC: smoothing scientific APPROVE qualified and normal acceptance completed; reviewer charge $4.31079575 counted. No CPU retry or new allowance.
-22:33UTC: read-only Drive visibility and timing reconciliation completed without model calls; originals retained. Latest Claude direction remains PROCEED with simpler narrow-patch deployment.
