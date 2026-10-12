# 13B execution plan

Updated 12 October 2026. The operator's latest Colab decision supersedes the earlier smoke, runtime-pin and metering plan. The old notebook is **superseded: do not run it**. Its A100 attempt stopped at the Python 3.12 check before installation or training; Partho disconnected it. A1_repeat replacement notebooks are now released after scientific review7; see [files and hashes](notebooks/A1_repeat/README.md). [Status](STATUS.md).

## Arms, folds and venues

Each fit is 250 epochs. The scientific author writes the notebooks; the scientific reviewer reviews each notebook's code before delivery. The first epochs of the real fit are the smoke test. Human Colab runs do not require a separate smoke, per-run review, segmented contract or metering gate.

| Arm | Folds | Venue / owner | Delivery order and hold |
|---|---|---|---|
| A1_repeat | 0, 1, 2, 3, 4 | **Partho on Colab**, default runtime, A100 | First; review7 released. Operator reports folds0/1 active;2/3next, then4. |
| A1_multiwin | 0, 1, 2, 3, 4 | **Partho on Colab**, default runtime, A100 | Second; first intervention arm, deliver as soon as reviewed |
| A1_pnormct | 0, 1, 2, 3, 4 | **Partho on Colab**, default runtime, A100 | Third, as soon as reviewed |
| A1_pnorm_v2 | 0, 1, 2, 3, 4 | **Partho on Colab**, default runtime, A100 | Fourth, as soon as reviewed |
| A1_L | 0, 1, 2, 3, 4 | **Partho on Colab**, A100 | Fifth; retain memory feasibility checks, no silent model reduction |
| A1_zscore | 0, 1, 2, 3, 4 | **Partho on Colab**, A100 | Held: coverage-source contract unverified; do not let it delay the released intervention arms |
| A1_histeq | 0, 1, 2, 3, 4 | **Partho on Colab**, A100 | Held: coverage-source contract unverified |
| A1_repeat2 | 0, 1, 2, 3, 4 | **Partho on Colab**, default runtime, A100 | Last; firm up training-noise estimate before final conclusions |

Start with **two A100 sessions**, A1_repeat folds 0 and 1, then use freed sessions for folds 2, 3 and 4. This is a conservative scheduling recommendation, not a claim about an account's quota. Colab limits vary; use the sessions the account permits. Deliver each subsequent arm immediately after its review, without waiting for all arms. Never run an all-fold notebook and a separate file for the same fold simultaneously.

In parallel: server CPU runs synthetic checks and the reviewed saved-output analyses. The Modal GPU CPU-starvation diagnostic remains parked at its diagnosed reader failure; resolving it does not block Colab. Its approved $25 bound and hard stops remain. No new Modal CPU job is needed. Private meeting-case planning remains separate.

## Comparison and interpretation

Operator decision12October: compare every Colab arm against the Colab A1_repeat baseline on the same platform; retain Sprint12 as an additional historical comparison. Run intervention arms before A1_repeat2. Use the final repeat to strengthen the training-noise estimate before final conclusions. The scientific author implements this in subsequent notebook/report revisions and the reviewer judges it. The running approved A1_repeat files remain byte-for-byte unchanged.

## Notebook contract for the scientific author

Target Colab's current default Python 3.13 and preinstalled CUDA/PyTorch on A100. Choose compatible additional packages and record actual versions; require an older runtime or exact torch replacement only for a demonstrated failure. Each notebook has its arm, folds and paths built in. The human selects A100 and Run all, plus normal Drive authorization.

Mount existing Drive, read inputs in place and verify frozen hashes and positive development-99/excluded-49 membership before use. Never read locked/reserve patient payloads. A1_repeat excludes 4D CTP. Preprocess, train 250 epochs, checkpoint regularly and automatically resume on rerun. Bind checkpoints to code, inputs, arm and fold; completed fits must not rerun silently. Use private results folders separated by arm and fold, prevent concurrent ownership of the same fit, score held-out patients and save metrics, timing, environment, input verification and run summary.

Package an all-fold file and per-fold files from the author's reviewed code; no editable settings for Partho. The reviewer sees the entire relevant notebook/pipeline, all materialized notebook variants, tests and actual test evidence, and reports all findings at once. Operator packaging must not invent scientific code or settings.

Results return in each notebook's built-in private Drive results folder. The system ingests and analyses them as they arrive. Exact filenames, hashes and result paths will be supplied with each reviewed delivery. No separate smoke, deliberate interruption, balance prompt, reservation or per-segment contract. Real disconnects exercise automatic resume.

## Estimates and money

Sprint 12 A1 measured 2.69-2.74 hours per 250-epoch fold, about 13.5 hours for a standard five-fold arm. At the operator-reported 6.77 CU/hour this is approximately 18.2-18.5 CU/fold or 91.4 CU/standard arm, before setup/preprocessing. Each notebook prints an upfront estimate and updates observed timing. These are estimates, not metering or admission limits.

The provisional full 40-fit plan is 130-140 GPU hours or 880-948 CU before overhead; the large arm's 35-45-hour estimate is unvalidated. The previously stated 1,001 units correspond to 147.86 A100 hours, but the balance does not constrain the plan and no balance is requested. Partho manages Colab subscription/top-ups; the system makes no purchases and creates no Colab reservations/accounting.

Other venue limits remain unchanged: item4 Modal stage1 $150, timing diagnostic $25 inside it, total $1,275 and full-training projection gate $1,200. Non-Colab stage1 exposure last reconciled at $115.516623, including identified billed compute $24.487001 and retained exposure $91.029622. Preserve the old $1.36 Colab estimate and original records as historical; actual cost is unknown. The operator reports that attempt terminated before installation/training. It is not a prospective Colab spending gate under the new decision.

## Next results

Author7's real reference-hash correction passed scientific review6. Author8 used the independently approved exact-deletion interface to remove the remaining inert fragment; synthetic tests pass. Scientific review7 approved the exact six notebook files with no findings. Every delivered variant passed the existing isolated synthetic suite; exact bytes are available in Downloads and under outputs/notebooks/A1_repeat. No additional final interpretation blocks a human Colab run.

Idea2's single saved-output CPU execution completed and validated. Its interpretation adapter was approved and installed, but activation stopped before any call on an obsolete reader expectation. Reader repair and the subsequent138-test stage-routing repair are approved/installed, with native checks passed. Scientific interpretation author2/review2 and ordinary finalization are COMPLETE, APPROVE with documented limitation: the reviewer could not directly inspect the two largest numerical tables. See [accepted report and scope](idea2_fixed3x3/README.md). No CPU rerun or new provider commitment. Timing/sandbox/rotation remain deferred; the swap gate is not met.

Operator report12October: folds0/1 started in two default-runtime A100 sessions, unedited review7 files; Drive mounted and250-epoch estimates printed. Input-check completion, epochs and results are not yet reported. Do not launch duplicate fits.

Current next step: reconcile multiwin scientific reviewer8. Author9 completed; all six exact variants passed the isolated synthetic suite. Verdict expected within about20minutes; deliver immediately if approved, with no post-review scientific edits. Proposed training estimate is3-4hours/fold (20.31-27.08CU) plus setup/scoring, unmeasured.

The installed104-call scientific batch is fully used/reserved by this review. A proposed24-call continuation for Colab,analysis and meeting work awaits the operator money decision. No caps have changed. Same-platform comparison and final repeat order remain bound to the author's proposal.

Analysis and meeting intakes are prepared in parallel; each needs one author/reviewer cycle after admission. Actual private case panels additionally need asset/provenance and geometry verification. Timing,sandbox and rotation remain deferred; no swap point.
