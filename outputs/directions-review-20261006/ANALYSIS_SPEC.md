# Phase1 — independent directions beyond Sprint13B
run_id: stocktake-132a97b7aef9935ec8469dbf
analysis_registry_sha256: 445ccafffed04129022543c4c29bd309af0766ef1130a4afb237d3912c110b80

Question: Which cheap tests clarify admission-image prediction?
Evidence: Accepted stock-take S and imported operator-run 13A aggregates A support investigating fusion and persistent small-lesion failure. Fusion's Dice gain accompanies worse lesion F1.
Limits: Exposed cohort, dependent fits, missing r4 source; no new computation or literature search. No novelty, causal, clinical-use or untouched-test claim.
Next: Independent review; tests1/2 first after separate authorization. Phase1 precedes operator-idea reveal.

## Inspected evidence

Keys: inspected originals, filename prefixes are SHA256.

S: `evidence/26abd688a46f9677af9a572fcdbe0958d711d8fe1b8ea9444ae8cb87a8f563c0-prior_results.txt`, accepted stock-take, sprint questions/numeric audit/uncertainty/original judgments.
A: `evidence/e5cb1b3e0bb35fdd8aa5cb613390951f5c4636c8fa59edf692737a1084344195-view.txt`, all six aggregate members. Inspected omission manifest `evidence/5a52ab34051166bc70aa9173f114034eca6b93045615dd92e5c2876878dee56c-omissions.json` withholds two opaque PNGs; no patient material selected.
B: `evidence/a74959ac4546a982af4ae13719108f93d50bc91e264200c48afeb660fae51b59-prior_results.txt`, current 13B scope.
P: `evidence/9ef811065c5db13634e16d493080070d6f7f167f0bdcf3c3704c205d9b427e4b-prior_results.txt`, completed item2 proposal, eight answers/cost assumptions.
C: `evidence/3a4ab141689f782ecd188134efe1f63f609e8888c1ddfdc77840276471497760-prior_results.txt`, recorded 2026-10-06 pricing. Older Function rates do not apply.
G: `evidence/97f0dce46af8a422dcacfd707b710cb37e7696b1d4b866ae4cab861ce7a34cbd-prior_results.txt`, source gaps/exclusions.

A's navigation/omission records were read. S is accepted synthesis, not new inspection of its patient-bearing sources. A validation is external; executed r4 source is missing. 
B covers repeats, normalization/windows and whole L preset. Preserve P's smaller-screen preference despite B's all-arm choice; neither authorizes item5 execution.
Current finding index in `prompt.md` is `[]`; no exact current finding/closure records are supplied. S/P judgments remain attributed history, not current blockers, fresh closures or proof of execution. Independent review is NOT_REVIEWED; no reviewer report edited.

## Ranked shortlist
Rank emphasizes feasibility, identifiability and negative-result value. Conditional amendments only; asset readiness NOT_INSPECTED beyond aggregate assertions.

### 1. Separate fusion's placement gain from its amount change
Value: Decide whether to invest in fusion or its volume rule.
For: A `paired.csv` fusion versus reported nnU-Net Dice +0.028 (97.5% interval +0.015,+0.042); versus self-volume nnU-Net +0.025 (95% +0.014,+0.038); versus tree +0.020 (+0.007,+0.033). Legwork: 13A rule swaps; S Sprint4/5/10 amount controls.
Against/unknown: Same self-volume rule does not mean same volume. Fusion versus tree loses lesion F1 −0.058 (−0.088,−0.031). A `complementarity.csv` reports Dice correlation 0.81/shared missed-truth fraction 0.671, not patient success rates. Support/smoothing/calibration may explain gain.
First test: Freeze tree, nnU-Net and equal-weight-average rankings, each selecting the tree's predicted voxel count per patient on saved split101/seed1. Common verified 2-mm domain, fixed common smoothing, deterministic ties; explicit zero extension outside legitimate support. Add common-support sensitivity without deleting scoring truth. Primary paired patient Dice: fusion minus tree; nnU-Net secondary. Report lesion F1, volume identity and original own-volume rows; no tuning.
Decision: Advance placement only if benefit persists without material lesion-detection harm; freeze numerical tolerances at protocol review. Otherwise prioritize amount/calibration. Negative limits this fusion, not all ensembles. Risk: annotation-assisted support/grid mismatch. Cost M 2–6 h, $3.81–11.42 ($4.95–14.85 contingency), 4–8 analyst h. FIRST; no training.

### 2. Diagnose small-lesion misses and component penalty
Value: Distinguish missing lesions, fragmentation and mergers before changing loss/resolution.
For: S reports 28 positive cases <5 ml, 50 at 5–<50, 20 ≥50, plus one empty truth outside bins. A fusion versus nnU-Net raises recall +0.067 but lowers lesion F1 −0.030 (−0.048,−0.015). Full-tree rule on nnU-Net raises lesion F1 +0.054 (+0.030,+0.081), Dice only +0.006. Existing legwork exposes the tradeoff.
Against/unknown: Matching/resampling can change lesion F1 without worse tissue localization. Outcome size bins cannot be routing inputs; MRI's 0.759 Dice in S uses future information, not an admission ceiling.
First test: Saved parent/fusion masks and truth, frozen official matching (A attributes IoU≥0.2; verify connectivity, one-to-one assignment/empty rules). Report unmatched components, mergers/splits by existing size bins and empty truth. Diagnostic endpoints: patient-averaged matched-lesion recall and false-positive components versus both parents, with Dice/F1. Compare existing threshold-before-resampling and resample-before-threshold masks as geometry sensitivity; no pruning/tuning or replacement by any-overlap matching.
Decision: Merger losses motivate separately reviewed component-preserving rules; shared absent lesions motivate representation work; matching artifacts require interpretation repair. Negative rejects simple topology explanation. Risks: small strata/geometry/post-hoc selection; report all bins. Cost M 3–8 h, $5.71–15.23 ($7.42–19.79), 6–12 analyst h. SECOND; share validated I/O, no automatic sweep.

### 3. Audit calibration separately from segmentation
Value: Check probability sums as volume estimates before relying on self-volume rules.
For: A tree Dice falls 0.208→0.121 at threshold 0.5, with five empty predictions. S Sprint5b calibration reduced signed bias; saved scores provide legwork.
Against/unknown: Sprint5b showed no clear Dice/absolute-error gain. Threshold sensitivity alone is not miscalibration; sampling, support and prevalence confound probability readings.
First test: Frozen-bin reliability, Brier score and probability-sum volume error for parents/fixed fusion, no fitted recalibrator. Average within patients then across patients. Separate modeled support/full-domain zero extension, show class-stratified contributions, preserve full truth/undefined denominators. A prevalence comparator must use outer-training-only statistics; omit if unavailable.
Decision: Only a consistent defect motivates later calibration fitted/tuned entirely within outer training data. Existing OOF meta-tuning is not independent. No defect stops this branch. Main risk: pooling unlike patient distributions. Cost M, 2–5 h: $3.81–9.52 ($4.95–12.37 contingency), 4–8 analyst h. Third: diagnosis, not another sweep.

### 4. Test centre/coverage sensitivity of normalization
Value: Assess fragility across acquisition contexts beyond B's average arm comparison.
For: S Sprint12b +0.008 Dice (printed interval +0.000,+0.015), positive in five arrangements; Sprint11 centre-linked missingness, counts 67/31/1. Saved repeated predictions supply legwork.
Against/unknown: Same hypothesis-selected patients; rounded zero does not establish positivity. Centre, lesion mix and missingness confound attribution. Site/local transforms were already explored; another sweep is redundant.
First test: Saved matched reference/normalization predictions, all common repeats, authorized provenance fields. Freeze centre groups plus unknown and one label-blind coverage indicator before outcome joins. Average repeat differences per patient; report centre effects, centre-balanced/patient-weighted summaries and descriptive interaction uncertainty. Verify current counts/coverage; retain sparse groups, no exclusions.
Decision: Heterogeneity motivates a later held-centre protocol, not adverse-centre tuning or causal scanner claims. Null heterogeneity is not equivalence/generalization. Missing provenance stops access expansion. Cost T, 1–3 h: $0.95–2.85 ($1.24–3.71), 4–8 analyst h. Fourth; no new fit.

### 5. Audit annotation-assisted representation
Value: Establish which predictor inputs can actually be constructed at admission.
For: S Sprint9/10 describe annotation-assisted caches; support diagnostics are not universal ceilings. Check availability before performance gains.
Against/unknown: Assistance alone does not prove follow-up leakage; admission-derived anatomy may impose only labor. Source-image methods did not clearly win. Inference-only feature removal is distribution shift, not a fair ablation.
First test: Desk audit of permitted code/configuration documentation, tracing masks/features/reference tissue to timing and construction dependencies: admission-observable, admission-derived but manually assisted, unavailable/unknown. No patient files; missing executed source stays unknown. Can the full pipeline be specified without outcome-derived construction?
Decision: Verified outcome dependence holds affected prospective claims and motivates a separately reviewed admission-only successor, preserving old results. Admission-derived assistance warrants qualification, not a leakage allegation. A negative narrows this concern without proving performance. Risk: mistaking names for provenance. Cost zero experiment compute, 6–12 analyst h; review dollars unknown. Recommendation: fifth for efficacy, prerequisite for operational-admission claims. New privacy/leakage decisions stop for the operator.

## Costs, inference and execution holds
C: Sandbox CPU $0.1419/core-h, RAM $0.024/GiB-h: T=4 cores/16 GiB=$0.9516/h; M=8/32=$1.9032/h. Unmeasured runtime ranges include I/O; parentheses add 30% contingency. Tests1+2 total $9.52–26.65 base, $12.37–34.64 contingency; no assumed shared-I/O saving. GPU cost zero. Storage/egress additional at recorded $0.09/GiB-month/$0.04/GiB. Assume existing private destination/no transfer; cost unknown sizes before execution.  Model dollars/remaining allowances unknown.
All tests PROPOSED ONLY. No patient access, probe code, notebooks, training, GPU/Modal jobs or additional model calls here. Future patient work requires a reviewed source-bound protocol on eligible99; final25/reserve24 untouched. Verify prediction/code/environment/partition identities, grids/coverage and unique complete matched rows/repeats. Retain failures/full truth; missing assets stop, never trigger gap-filling retraining. No executable fixed/tested here.
Freeze test1's primary; tests2–4 are descriptive with all contrasts reported. Resample patients after within-patient averaging; report valid denominators. Voxels/folds/repeats are not independent patients. Intervals condition on saved fits and exclude selection/shared-training/new-cohort uncertainty. Freeze multiplicity families before computation; post-result changes require new versions. Preserve empty/undefined conventions; distinguish median paired volume-error change from difference of medians. No confirmatory claims.
Author counterargument: shared missed signal on exposed patients may limit all postprocessing returns. Independent review must challenge this ranking.
Latest task authority 38b3f7298f64f53396318b2e460c0b2a80013dcef2bcbd30168444c5f24609ff: item5 16 calls, items3/4 20, UTC-day30 across roles, batch60; past/uncertain usage counts, GPU caps unchanged. Separate decision file is not staged. Reconcile actual usage before review; no remaining allowance assumed. Only independent APPROVE closes findings. REVISE returns to author within three cycles; REJECT/unresolved fourth review stops. Preserve each returned finding verbatim with evidence and explicit response. Privacy/secret, test-set/leakage and budget decisions remain held; correctable aggregate statistics/cost arithmetic use metric/statistic. Independent review pending; no substitute model call authorized here.
