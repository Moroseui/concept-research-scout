# Sprint13B analysis specification / proposal
run_id: stocktake-6b556dba36d299c05b8b7770
analysis_registry_sha256: 67fd16e52ecbbed18a9ba6b4735a2a4a74dfb8a32dc3800a4d4809e360b06317

Question: smallest 13B study for admission-to-follow-up infarct prediction?
Recommendation: MODIFY / REVISE toward a normalization screen; reject automatic improvement claims. Exposed patients, training uncertainty and unmeasured 13B runtimes limit inference. Next decision: STOP FOR OPERATOR REVIEW; no execution authority.

## Sources, scope and status

C n/O m = original cell/output; C n = source. Keys resolve via navigation SHA256 629f3dc8af24ebf537b3209217f1819c4e5391354db609d19aae047a34a03087. Unique evidence/ filename hash prefixes:
S stock-take 26abd688a46f9677; B Sprint13B 04aeab8902299388; A earlier Sprint13A e353483cb2f8669c; E 13A aggregates e5cb1b3e0bb35fdd; N Sprint12-nnunet ccd74c0e954d7b2c; T Sprint12b 7ad63a2baf5cc627; R costs 0175d1c5f057e330; G limitations 97f0dce46af8a422. Hashes verified.

Navigation reports scans PASS/no patient material. Inspected omissions: metadata, B C4 bytes 2090:2120 and E PNGs; nothing reconstructed. Current scope supplies six external 13A aggregates; earlier “not run”/held wording is historical. Executed r4 source is absent (G); no unprovided results/rerun proposed.

Current finding index=[]; exact finding/closure files unavailable. S's historical 17 records/three closures are not today's register: no reopening/importing old blockers. Closure neither erases criticism nor proves later success. New findings cite B. Only text, hashes, cost arithmetic and document edits occurred; no patient work, experiments/notebooks, GPU/Modal, other model calls or dispatch. This is self-review, not opposing review.

## Eight answers

1. **Screen first:** repeat, zscore, histeq, all five frozen folds; preserve A1. Test rescaling in M, then stop for review. Screen outcomes cannot answer separate window/capacity questions or automatically advance them. Lean zscore+repeat is defensible; predeclare omissions and retain family four. No performance stopping between folds. Reject immediate all-arm commitment, especially costly L.

N C22/O0: Dice A1 0.200, no-CTA 0.195, normalized 0.203; normalization +0.003 [−0.015,+0.020], CTA +0.005 [−0.007,+0.016], n=99, exploratory 95% intervals. No improvement/equivalence established; a negative concerns these transforms only.

**Sprint12b overlap:** T C20/O0 tested reference tissues, ratios/ranks, validity, CT/HU, MTT, ablations/local/site normalization. Primary +0.008 [printed +0.000,+0.015], 15 predictions/patient (5 arrangements×3 seeds), positive 5/5; lesion F1 +0.009 [−0.004,+0.026]. Its 47 exploratory contrasts include MTT +0.014 [+0.006,+0.021]. MET/rounded zero is not independently verified strict positivity. Same exposed patients, not replication. 13B's delta is source-image nnU-Net/post-window transforms, not normalization novelty. Strict monotone fixed transforms preserve ideal tree ordering; clipping creates ties and patient transforms alter cross-patient order, qualifying the plan's tree-invariance claim.

2. **Second windows: retain fixed bundle, defer.** B C4: CT 20–50, CBF 0–100, CBV 0–4, MTT 0–12, Tmax 0–20, CTA 0–300. Wider CBF/Tmax/CTA recover clipped information; narrower channels re-express existing information. Twelve channels change parameters/storage, not six independent tests. N C20/O0 smoke upper-clipping medians: CBF 8%, Tmax 12%, CTA 10%, CT 10%, CBV 6%, MTT 3% (12 patients only). Saturation starts at 7, not throughout 6–7. Clinical/winner claims lack inspected primary literature. Require source units/coverage and label-blind clipping review; no outcome-guided tuning, changed windows need new version.

3. **Family/verdict/repeats: modify.** Keep four Dice contrasts and 98.75% paired patient-bootstrap intervals, 10,000 draws (tails 0.625/99.375%), even with unrun arms. This does not correct historical selection, shared training or winner selection. Report Dice/raw endpoints, counts/fold effects, lesion F1, precision/recall denominators and volume error. Missing/invalid rows stop interpretation.

Require frozen 99 unique patients, folds 0–4, matched receipts, unchanged scoring/empty-mask rules and complete comparisons to BOTH old A1 and contemporary repeat. Both intervals above zero: “screen-positive”; both below: “screen-negative”; otherwise inconclusive/discordant. The conjunction is a conservative joint requirement, not eight confirmatory discoveries. Crossing zero is not equivalence. No clinically meaningful Dice threshold is established; metric deterioration requires operator tradeoff review.

One repeat measures sensitivity, not variance; two baseline repeats leave candidate variability unknown. Prefer one, then separately approve a matched candidate+baseline repeat (26 h). Two paired realizations remain descriptive; repeats add no patients. B C16: train_seed=1 is pairing only, training was unseeded. Record RNG, environment/distinct repeat identities; existing receipts skip/resume. Remove effect/repeat-change ratios: near-zero denominators explode; one difference is not noise variance or a remedy for software drift.

4. **L: defer; prefer whole preset.** Record realized patch/spacing/batch/architecture/planner/hardware. Estimate preset performance, not size causality. Fixed M patch+L is a different architecture question; do not add both. Neither has measured timing; fixed patch is not necessarily M speed. B C12 imported M plans preserve configuration/rebuild channels; own L plans lack that control. A 32-GB guard does not prove fit.

5. **pnormct: defer.** Adds 13 h, overlaps T's HU work. Incremental comparator is A1_pnorm_v2 (B C22), whose gain in N is inconclusive. Require matched environment/plans and admission-only reference. Contemporary pnorm_v2 control could add 13 h if drift prevents isolation. Tree effects need not transfer.

6. **Coverage: agree in principle.** B C8's all-four-maps-zero after nan_to_num is only a proxy: single-channel non-finite values may enter statistics as window-floor values; true zero tissue may be excluded. Require label-blind finite/validity policy, coverage provenance and fallback/SD-floor/coverage reporting. Keep uncovered output zero/scoring support fixed; z-score zero also means average tissue. No extra factorial or claim of exact whole-brain recipe replication.

7. **13A: retain historical total-pipeline P1/P2; reject unbiased stacking language.** P1 includes resampling/rule changes; P2 adds fusion. E sprint13a_paired.csv: P1 +0.003 (97.5% +0.001,+0.004), P2 +0.028 (+0.015,+0.042), n=99. Same-rule fusion versus nnU-Net is exploratory +0.025 (95% +0.014,+0.038), not a new primary. P2 lesion F1 falls −0.030 [−0.048,−0.015]. E sprint13a_complementarity.csv: correlation 0.81/shared missed-truth fraction 0.671; errors are dependent. No Dice-only promotion.

A C6's meta-training OOF predictions come from models trained partly on the scored fold: excluding its rows does not eliminate dependence. Bias is unknown; E provenance corrects A C8's unsupported “small” claim. Keep tuning exploratory. Independent assessment needs nested base fitting inside outer training sets or a frozen rule under separately approved untouched evaluation; neither now. E validation's passed checks, 99 reused caches/297 rebuilds are external assertions. Its 0.9187 probability-mask Dice is not established as the older native-grid ≥0.99 check. Missing executed r4/cache provenance prevents reconciliation, not proof of success/failure. No rerun.

8. **Retain SynthStrip:** repair changes baseline/all arms. Preserve full truth/outside-mask misses; no case exclusions. N smoke minimum infarct-in-brain 83% is not a cohort anatomy estimate. Repair needs separate matched-baseline/label-blind-QC review; integrity failure means stop.

## Costs: assumptions, not measured runtimes or spending authority

R's official Modal prices (read 2026-10-05; not refreshed/Colab prices): A100-80GB $0.000694/s=$2.4984/h; 40GB $0.000583/s=$2.0988/h; physical CPU $0.0000131/core-s=$0.04716/core-h; RAM $0.00000222/GiB-s=$0.007992/GiB-h. One sequential 80GB GPU +8 cores/64 GiB=$3.387168/h; high-capacity sensitivity +12 cores/180 GiB=$4.50288/h. Sufficiency unverified; N's 179 GB/12 CPUs are not billing measurements.

B estimates M=13 h, L=35–45 h, smoke=2–3 h. N C20/O0 A1 smoke median 35.69 s/epoch extrapolates to 12.39 h for 250 epochs×5 folds; not measured full training. N C20/O2's 8.5 min is a skip. No measured 13B runtime. Multiwin assumed 13–18 h; default training totals 87–102 h versus plan's rounded 90–100.

Each standalone batch adds 1.5–3 h/arm preparation/scoring/I/O +2–3 h smoke, GPU allocated throughout. Upper bound adds 30% training slowdown/recovery.  Scenario ranges, not confidence intervals.

| Option | Training h | Occupied h | USD 8 cores/64 GiB | USD high capacity |
|---|---:|---:|---:|---:|
| Desk stop | 0 | 0 GPU | 0 experiment cost | 0 |
| Lean zscore+repeat | 26 | 31–42.8 | 105–145 | 140–193 |
| Preferred three-arm screen | 39 (~40) | 45.5–62.7 | 154–212 | 205–282 |
| Screen+second baseline repeat | 52 | 60–82.6 | 203–280 | 270–372 |
| All five defaults | 87–102 | 96.5–150.6 | 327–510 | 435–678 |
| Multiwin extension | 13–18 | 16.5–29.4 | 56–100 | 74–132 |
| L, own/fixed patch* | 35–45 | 38.5–64.5 | 130–218 | 173–290 |
| Extra M / pnormct | 13 | 16.5–22.9 | 56–78 | 74–103 |
| Candidate+control repeat | 26 | 31–42.8 | 105–145 | 140–193 |
| Two realizations/all screen arms | 78 | 89–122.4 | 301–415 | 401–551 |

*Fixed-patch L has only this conservative placeholder. Mask repair minimally adds a baseline+candidate pair at the pair-row cost, plus unknown QC/repair labor. Nested 13A requires new fits (e.g. 5 outer×4 inner=20/model plus outer fits); reject expansion without a costed contract. Preserving E costs zero experiment hours.

40GB saves $0.3996/h only at equal speed/capacity. Extra CPU analysis (4 cores/16 GiB) costs $0.316512/h: 1–3 h=$0.32–0.95, outside counted scoring only. Storage/egress/region premiums, queues, intervention, Colab units and funds are unknown/excluded. Entitlement is not zero resource cost. Screen ceiling: 65 occupied h (~$293 high-capacity), before exclusions; stop if exceeded. This authorizes no spending.

Scientific model calls, separate from fits: proposal author/review/disposition=3 including this author; revision cycle +2: desk 3–5. Code author/review/decision +3 and result interpretation/review/disposition +3 give 9–13 per hypothetical batch including up to two revision cycles, regardless of arm count. Separate screen+extension: 18–26; extra formal 13A interpretation: 3–5, no retraining. No other calls made here; token dollars/latency unavailable. Retain failed/uncertain charges and 48-warning/96-hard accounting.

## Findings and stop

F13B-01 — blocker for verdicts; verified static B C22, execution untested. N_ALL derives from editable FOLDS_TO_RUN: a subset can receive a non-provisional verdict. Freeze 99/five-fold membership independently of scheduling; require complete unique baseline/repeat joins and review subset/duplicate rejection.

F13B-02 — blocker for robustness claims; B C16/C22 verified plus statistical inference. One unseeded repeat/ratio cannot estimate noise; printed magnitude rule is not a coherent gate. Remove it; adopt the conjunctive screen rule and distinct environment/repeat identities.

F13B-03 — suggestion for coverage interpretation; verified B C8, impact untested. Zero/non-finite proxy does not prove coverage. Bind validity/provenance/limitations; no patient audit authorized.

Any finding, REVISE/REJECT, identity failure, uncertainty or cap stops this lane for the operator. No notebook changed. Missing: reviewed revised executable, baseline plans/environment receipts, coverage provenance and per-arm time/capacity evidence. Synthetic checks are attributed plan claims, not reproduced. Next decision: STOP FOR OPERATOR REVIEW, not execution authority.
