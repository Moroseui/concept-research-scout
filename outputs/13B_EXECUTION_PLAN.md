# 13B execution plan

Current checkpoint (11 October): scientific review4 APPROVE accepts the exact in-place notebook, with isolated synthetic PASS. The CPU-only input-check package and exact notebook/settings are delivered. All893 existing files are mapped; Colab must hash all payloads. Training reservation/runtime packaging remains pending one short Claude accounting consultation. The laptop copy stays stopped and preserved. Final interpretation follows smoke. Idea2 authoring has not started; timing remains parked.

Updated 11 October 2026. Owner: system author for scientific code and interpretation; independent reviewer for acceptance; Codex for packaging and infrastructure. This is the operational plan, not a scientific release or permission to bypass admission. [Status](STATUS.md).

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

Current reviewed notebook: `isles24_13B_A1_repeat_fold0_in_place_review4.ipynb`, SHA-256 `ec100c518196bdfae41d4510a2b19e20c906fa798ebcdee41aac4152eb6d93d6`. Review4 APPROVE accepts preparation; the isolated synthetic gate passed. The previous review3 notebook is preserved and superseded. First GPU run remains **A1_repeat, fold0, SMOKE only**, seed101, five epochs,250 train/50 validation iterations per epoch, workers2, `PAUSE_AFTER_SMOKE=True`, initial `RESUME=False`. FULL stays disabled. The delivered first input-check instructions instead select **CPU and PREFLIGHT_ONLY=True**, using the separately bound input-check contract, which cannot admit training. No scientific code change or new model call is needed for that supported preflight mode.

Read893 frozen files in place; no4DCTP. All891 payload paths exist at expected sizes; both baseline hashes match. Runtime hashes every used payload against the frozen inventory and checks development/exclusion membership. Only genuinely absent required files may be uploaded directly from the server; no missing files are established yet. Do not resume the stopped laptop copy. Return input-check reports privately, then use the separately admitted training contract. Actual environment and preprocessing evidence come from the smoke. Final interpretation is not a handoff gate.

Use Partho's A100 40/80 GB runtime with at least 2 CPUs and 16 GiB RAM, Python 3.12, CUDA 12.8 and the exact reviewed package pins. Deliberate interruption after epoch 1 precedes separately bound resume epochs 2-5. Stop after the smoke; never automatically launch full training or a coverage-held arm.

Return the executed notebook, aggregate metrics/timing, environment and input-hash receipts, interruption/resume evidence and a checksummed run summary through the existing private project/Drive intake. Predictions, clinical information and case images remain in the existing private research storage, never the public backup. The system verifies the return and obtains scientific review before releasing full training. First instructions will name the actual reviewed file, exact settings and private return location.

## Time, money and next result

Sprint 12 A1 measured 2.69-2.74 hours per 250-epoch fold, about 13.5 hours per five-fold standard arm. Using that baseline only: seven standard arms about 95 hours, plus the original notebook's unvalidated 35-45 hours for L gives roughly **130-140 Colab GPU hours for 40 fits**, before preprocessing, smoke and failures. This is a scheduling estimate, not a validated cross-arm projection. Partho reports **6.77 compute units/hour** for A100. The **1,001 units cover 147.86 A100 hours** at that rate. The provisional 130-140-hour plan costs **880.10-947.80 units**, leaving **53.20-120.90 units (7.86-17.86 hours)** for preprocessing, smoke and retries. This is a displayed rate reported by the operator; capture balance/time readings during smoke to check actual consumption. These estimates do not guarantee all 40 fits, especially the unmeasured L arm. No USD conversion or additional purchase is assumed.

The operator is willing to buy more units: the current 1,001-unit balance is not a ceiling and all 40 fits remain in the plan. Ask only when a concrete additional purchase is needed; do not purchase automatically. Execution priority among independently released arms: **A1_repeat -> A1_repeat2 -> A1_multiwin -> A1_pnormct -> A1_pnorm_v2 -> A1_L**. Finish each released arm's five folds before starting a lower-priority full arm; L first needs memory and timing qualification. **A1_zscore and A1_histeq remain held** for coverage sources and come last only after review resolves that hold. Recalculate after the first smoke and each completed arm, including required controls and retries and reporting any additional units needed. This is venue/budget sequencing, not permission to omit scientific comparisons or change the accepted analysis.

Modal stage-1 commitment: **$115.516623/$150**; timing diagnostic: **$5.405445/$25**, inside stage 1. Identified provider compute actual: **$24.39800404**; model charges separate. The diagnostic has no automatic GPU retry. Existing all-Modal full-plan estimates of $2,963.89-$3,574.95 exceed the $1,200 gate and are not accepted steady-state estimates. Reproject deliberately using measured Colab units and Modal cost, retaining all open reservations until billing closes them.

Action needed from Partho now: open the delivered review4 notebook and follow `isles24_13B_in_place_input_check_instructions.md` in Downloads on a CPU runtime. This only hashes inputs. The training contract and environment setup follow after the bounded accounting question is resolved. No A100 is needed yet. Colab input-check completion depends on human start and Drive throughput; training ETA remains conditional. Idea2 authoring is next; author timeout1800seconds is installed in this Colab lane, reviewers unchanged. Timing remains separate. Defer unrelated infrastructure.
