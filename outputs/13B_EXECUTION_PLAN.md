# 13B execution plan

Updated 12 October 2026, 22:07 UTC. New experiments first; repeats are parked. Scientific authors write the notebooks and analysis; Claude reviews them. Every arm needs a real nnU-Net trainer construction and at least one training iteration before full notebook delivery.

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

Smoothing saved-output CPU execution completed once: valid,304.77seconds,99development patients, zero excluded overlap,728input and4package hashes unchanged before/after,198equal-amount and792saved-table checks passed. Five private aggregate outputs validate. No new scientific efficacy conclusion is accepted.

Namespace repair03a42f24 passed178tests and independent APPROVE3ad83d54/report77aec8c0. It is installed, prepared and activated with15prior calls preserved and no added allowance. Both-family native transport/admission-stage probes passed without model calls. The subsequent actual author advance refused before reservation/client launch: IDEA2_INTERPRETATION_ALLOCATION_HISTORY_CHANGED. Unit is inactive, no running model row, local15/global115scientific calls unchanged.

Read-only diagnosis proves all109 frozen rows match their original compact-JSON hashes; the installed checker used spaced JSON. No historical row changed. Candidate33eb9bef changes only this serialization boundary and independent test fixtures;187tests pass, including actual normal reservation, caps and all changed-field/missing-row refusals. A red regression first reproduced the fault. Candidate is NOT installed or reviewed. Next: include exact safe installation/recovery and direction check in one necessary independent implementation review; keep every original pin, charge and refusal. Never rerun the completed CPU job or consumed preparation/start. Two analysis calls remain.

Item6 diagnostics, saved-results synthesis and Idea2 fixed3x3 interpretation are accepted. Sprint14's352rounded matches share saved fits/cohort, not independent retraining; the Idea2 review's inability to directly inspect its two largest tables remains disclosed.

Next arms are pnorm_v2 then L, with real A100 memory-fit evidence for L. Repeats parked; zscore/histeq held on coverage provenance. Compare provisionally against Sprint12A1 and do not interpret small differences until a later Colab repeat.

Meeting preparation retains the accepted six-slot case-selection rule. No cases/images selected. Inspected inventories establish CT/perfusion/reference labels and saved model outputs, but not follow-up MRI or clinical provenance; this is not proof of project-wide absence. An old metadata helper refused before credential access because its ephemeral runtime file was absent; the existing Drive service is inactive. No credential was created, copied, read or changed and no new patient payload was accessed. Resume only through the existing approved Drive route.

Timing diagnostic, author sandbox and opposite-family administrative review capability remain unfinished. No Swap point; pnormct is also running externally.

12OctoberUTC:62/100 calls, returning to50on13October without resetting history. Scientific batch115/128:7Colab,2analysis,4meeting remain. Known completed Claude charges $371.64940875; author dollar costs unavailable.

| Type | Count | Purpose |
|---|---:|---|
| Scientific author |14|Idea2 specification/interpretation, baseline and multiwin, pnormct corrections, smoothing specification; includes the preserved pre-client failure|
| Scientific reviewer |11|Idea2, baseline, multiwin, pnormct and smoothing scientific review|
| Administrative review |35|Admission/accounting repairs, packaging, dated policy, execution and interpretation integration|
| Standalone direction |2|Preserved disqualified attempt and qualified SIMPLIFY retry|

Item4 non-Colab stage1 exposure $115.516623/$150 = $24.487001 billed + $91.029622 retained reservations. Timing $5.405445/$25 is inside stage1; synthetic CPU $1.118950 awaits billing. Item4 total $1,275/projection gate $1,200 and item6 $100 cap unchanged. Colab is unmetered by operator decision. This continuation launched no new provider compute. Only confirmed closed provider billing can release excess reservations; uncertain/open obligations stay counted.

Current action: run13B_A1_multiwin_real_trainer_check_review11_PRIVATE.ipynb in a fresh default A100 session, Run all, no settings. Keep the other pnormct session running. This approved package runs authored unit fixtures then one real synthetic training iteration/checkpoint roundtrip, not a full fold. About10-25minutes, roughly1.13-2.82CU informational only. Final cell copies evidence privately, excluding caches; return printed status and folder. SHA25644902e1ebca592a796a5194bd05aa828af7748c18728b7d0f1c4e162f899877b.
