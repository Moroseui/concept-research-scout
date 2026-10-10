# 13B execution plan

Updated 10 October 2026. Owner: system author for scientific code and interpretation; independent reviewer for acceptance; Codex for packaging and infrastructure. This is the operational plan, not a scientific release or permission to bypass admission. [Status](STATUS.md).

## Arms, folds and venues

Each listed fold is a separate 250-epoch full fit. All full fits remain held until scientific smoke acceptance and an accepted projection within the $1,200 gate. The $1,275 total stays unchanged. Fold-0 smoke precedes each arm; coverage holds apply to smoke too.

| Arm | Full folds | Venue / owner | Next action or hold |
|---|---|---|---|
| A1_repeat | 0, 1, 2, 3, 4 | **Partho on Colab**, A100 | First handoff: matched fold-0 smoke; then full fits after gates |
| A1_repeat2 | 0, 1, 2, 3, 4 | **Partho on Colab**, A100 | Repeat control; compare with completed Modal B200 repeat |
| A1_multiwin | 0, 1, 2, 3, 4 | **Partho on Colab**, A100 | Author/reviewer release and arm smoke |
| A1_pnormct | 0, 1, 2, 3, 4 | **Partho on Colab**, A100 | Author/reviewer release and arm smoke |
| A1_pnorm_v2 | 0, 1, 2, 3, 4 | **Partho on Colab**, A100 | Author/reviewer release and arm smoke |
| A1_L | 0, 1, 2, 3, 4 | **Partho on Colab**, A100 40/80 GB | Memory feasibility unmeasured; retain original >=32 GB guard, no silent model reduction |
| A1_zscore | 0, 1, 2, 3, 4 | **Partho on Colab**, A100 | Held: unverified CTP coverage-source contract |
| A1_histeq | 0, 1, 2, 3, 4 | **Partho on Colab**, A100 | Held: unverified CTP coverage-source contract |

**In parallel:** Modal GPU runs the approved B200 CPU-starvation diagnostic (A:16 CPU/12 train+6 validation workers; B:32 CPU/24+12 workers; same arm/fold, 15 epochs, hard stops, B first if needed). It does not block Colab authoring or released Colab smoke. Server CPU handles synthetic author tests and aggregate analysis; no new Modal CPU job is needed for this handoff. Workstream B synthesizes item 6, three benchmarks, two smokes, Sprint 13A/14 and proposed ideas through author/reviewer debate. Workstream C specifies a private, preselected case review. Model calls may interleave under existing single-call admission while these workstreams progress independently.

## Colab handoff and return

Starting source: `isles24_sprint13b_nnunet_preprocessing_and_L.ipynb` (SHA256 starts 73f656d5). **The new reviewed notebook is not ready; do not run this old source as the new plan.** The scientific author must deliver a named/versioned notebook with `ARMS_ORDER=['A1_repeat']`, smoke fold 0, `RUN_SMOKE_FIRST=True`, `PAUSE_AFTER_SMOKE=True`, `EPOCHS_FULL=250`, and an explicit full-training gate. Match the frozen 99-development cohort, fold split, workload and model definition to Modal; the old 12-patient smoke is not a platform control. The author records exact torch/CUDA and package pins, resource settings and why any platform differences are acceptable. Later select one released arm and its explicit folds; no automatic coverage-arm fallback.

Return the executed notebook, aggregate metrics/timing, environment and input-hash receipts, interruption/resume evidence and a checksummed run summary through the existing private project/Drive intake. Predictions, clinical information and case images remain in the existing private research storage, never the public backup. The system verifies the return and obtains scientific review before releasing full training. First instructions will name the actual reviewed file, exact settings and private return location.

## Time, money and next result

Sprint 12 A1 measured 2.69-2.74 hours per 250-epoch fold, about 13.5 hours per five-fold standard arm. Using that baseline only: seven standard arms about 95 hours, plus the original notebook's unvalidated 35-45 hours for L gives roughly **130-140 Colab GPU hours for 40 fits**, before preprocessing, smoke and failures. This is a scheduling estimate, not a validated cross-arm projection. At an observed rate r compute units/hour, that is about 130r-140r units plus overhead; the available pool is **1,001 units**. The runtime rate is not yet known, so the notebook must record it and meter units before committing the full schedule. No additional Colab purchase is authorized.

Modal stage-1 commitment: **$114.397673/$150**; timing diagnostic: **$4.286495/$25**, inside stage 1. Identified provider compute actual: **$24.39800404**; model charges separate. The diagnostic has no automatic GPU retry. Existing all-Modal full-plan estimates of $2,963.89-$3,574.95 exceed the $1,200 gate and are not accepted steady-state estimates. Reproject deliberately using measured Colab units and Modal cost, retaining all open reservations until billing closes them.

Action needed from Partho now: none. Target first reviewed Colab smoke notebook in 2-4 hours, conditional on author/reviewer acceptance and the parallel-analysis admission patch; update the estimate if it slips. The first smoke's runtime must be estimated from the released workload, not from first-epoch benchmarks. Full arms are not held for the CPU diagnostic, but their unchanged scientific and money gates still apply.
