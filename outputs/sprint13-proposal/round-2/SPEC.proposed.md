# Sprint13B revised analysis specification
run_id: stocktake-6b556dba36d299c05b8b7770
analysis_registry_sha256: 67fd16e52ecbbed18a9ba6b4735a2a4a74dfb8a32dc3800a4d4809e360b06317

Question: smallest admission-to-follow-up infarct study? MODIFY to a normalization screen; reject all-arm commitment. Exploratory exposed-cohort evidence only. STOP FOR OPERATOR REVIEW; no execution authority.

Sources: unique evidence/ filename SHA256 prefixes: S=26abd688a46f9677 (accepted stock-take), B=04aeab8902299388 (13B), A=e353483cb2f8669c (earlier 13A), E=e5cb1b3e0bb35fdd (supplied 13A aggregates), N=ccd74c0e954d7b2c (Sprint12 nnU-Net), T=7ad63a2baf5cc627 (12b), R=0175d1c5f057e330 (prices), G=97f0dce46af8a422 (limitations), F=ed4e52a7ba198d4e (current finding). Navigation: 629f3dc8af24ebf537b3209217f1819c4e5391354db609d19aae047a34a03087. C/O=cell/output; L=view line.

Cited originals read/hashes verified; navigation scans PASS/no patient material. B C4 2090:2120/E PNG omissions inspected (fe9a05c8/5a52ab34), not reconstructed. Views are not executables. No experiments/patient work/GPU/Modal/notebooks/model calls/dispatch. Keep 25 final-evaluation and 24 reserve untouched.

## Eight answers

1. **Screen first:** propose repeat, zscore, histeq, in that order, each on five frozen folds. Preserve old A1. Repeat first protects budget-stop interpretation. No performance stopping mid-fold-set. Lean zscore+repeat is defensible. No automatic extension; negatives concern these transforms only.

N C22/O0 L698–708: A1 Dice 0.200, no-CTA 0.195, normalized 0.203; normalization +0.003 [−0.015,+0.020], CTA +0.005 [−0.007,+0.016], n=99, exploratory 95% intervals. Neither superiority nor equivalence.

**Sprint12b overlap:** T C20/O0 L814–842: normalization +0.008 [printed +0.000,+0.015], 15 predictions/patient (5 arrangements×3 seeds), positive 5/5; lesion F1 +0.009 [−0.004,+0.026]. Rounded zero/MET cannot verify strict positivity. Its 47 explorations include MTT +0.014 [+0.006,+0.021], tissue reference, ratios/ranks, validity/HU, ablation/local/site normalization. Same exposed patients, not replication. 13B adds source-image nnU-Net/post-window transforms, not normalization novelty. Qualify tree invariance: clipping creates ties; patient transforms alter cross-patient order.

2. **Second windows: defer fixed bundle.** B C4 L711–713: CT 20–50 HU, CBF 0–100, CBV 0–4, MTT 0–12 s, Tmax 0–20 s, CTA 0–300 HU. Wider CBF/Tmax/CTA recover clipped information; narrow CT/CBV/MTT re-express it. Twelve channels change parameters/storage: one bundle, not six effects. N C20/O0 L469–470 smoke upper-clipping medians: CBF 8%, Tmax 12%, CTA 10%, CT 10%, CBV 6%, MTT 3%, only 12 patients. Tmax saturation starts at 7, not throughout 6–7. Require units/coverage and label-blind clipping review. Clinical/winner claims lack inspected primary literature. Changed windows need new review; no outcome tuning.

3. **Keep family four; modify verdict/repeat interpretation.** Four Dice contrasts: 98.75% paired patient-percentile intervals, 10,000 draws, endpoints 0.625/99.375%, even with unrun arms; freeze seed/draws. Intervals condition on fitted models, excluding historical selection/shared-training uncertainty.

Require frozen 99 members/folds 0–4, complete unique candidate/A1/repeat joins, unchanged scoring/empty-mask rules. Both candidate-vs-A1/vs-repeat intervals positive: screen-positive; both negative: screen-negative; otherwise inconclusive/discordant. Invalid/missing: no verdict. Report unrounded endpoints, attempts/unrun arms, folds, Dice, lesion F1, precision/recall denominators and volume errors. Zero-crossing is not equivalence. This joint screen is not confirmation; no clinical Dice threshold exists here. Tradeoffs block automatic promotion.

Prefer one repeat for sensitivity only; two baseline repeats leave candidate variance unknown. Later pair candidate+baseline (26 estimated training hours); report all repeats. Two pairs remain descriptive. B C16 L359 says train_seed=1 is a pairing label; training was unseeded. Bind RNG, environment and distinct repeat identities; prevent completed-receipt reuse. Remove ratio/noise gates; repeats do not correct drift.

4. **L: defer; prefer whole preset if revisited.** Whole preset tests configuration, not size causality. Record planner/architecture/spacing/patch/batch/steps/hardware. Fixed M patch+L is another question; do not add both. Own L plans lack M controls; 32 GB proves no fit/timing.

5. **Defer pnormct:** overlaps T's HU exploration; adds 13 training hours. Incremental comparator is A1_pnorm_v2 (B C22), not A1. Unmatched environment/plans confound CT effect; contemporary pnorm_v2 adds 13 h. Require admission-only reference/validity rules.

6. **Covered-brain statistics: agree, modify proposed implementation.** B C8 L1433,1447,1478–1484 uses all-four-maps-zero as coverage proxy and replaces non-finite values before statistics. Propose valid support before replacement/clipping: authenticated acquisition coverage ∩ brain ∩ per-channel finite values. Without a mask, require a reviewed proxy version, disclose genuine-zero exclusion and hold interpretation for operator review. Preserve valid zeros under fixed channel rules. Exclude invalids from statistics; zero outside support; retain full scoring truth. Record coverage provenance, counts and fallbacks. Empty/constant support produces logged zeros and holds the arm for review. Keep SD floor 0.01 and 256 histogram bins; z-score zero also means mean tissue. No patient audit here.

7. **13A: retain historical total-pipeline P1/P2; reject unbiased stacking.** No schedule/rerun. E paired.csv: P1 +0.003 (97.5% +0.001,+0.004), P2 +0.028 (+0.015,+0.042), n=99. P1 includes resampling/rule, P2 also fusion. Same-rule fusion +0.025 (95% +0.014,+0.038) is exploratory. P2 lesion F1 −0.030 [−0.048,−0.015] prevents Dice-only promotion. E complementarity.csv correlation 0.81/shared missed-truth 0.671 shows dependent errors.

OOF meta-training predictions come from models trained partly on the scored fold; row exclusion does not remove dependence. E says magnitude unknown, correcting A C8's “small” claim. Tuning stays exploratory; nested base fitting or approved frozen-rule evaluation would be needed, neither now. E validation asserts 99 reused caches/297 rebuilds; probability-mask Dice 0.9187 is not shown to be A's native-grid ≥0.99 check. G: executed r4 source absent. No new validation/results claimed.

8. **Keep SynthStrip, conditional on integrity.** Repair changes baseline/all arms. Retain full truth/outside-mask misses, no exclusions. N smoke minimum 83% infarct-in-brain is not cohort anatomy. Repair needs label-blind QC/matched baseline/review; integrity failure stops comparison.

## Costs: estimated, not measured

R, Modal rates recorded 2026-10-05 (not refreshed/Colab rates): A100-80GB $0.000694/s=$2.4984/h; 40GB $0.000583/s=$2.0988/h; physical CPU $0.0000131/core-s=$0.04716/core-h; RAM $0.00000222/GiB-s=$0.007992/GiB-h. One sequential 80GB GPU +8 cores/64 GiB=$3.387168/h; +12 cores/180 GiB=$4.50288/h. Fit unknown; N's 179 GB/12 CPU is not billing.

B estimates M=13 h, L=35–45 h, smoke=2–3 h. N L469 measured smoke 35.69 s/epoch extrapolates to 12.39 h (250 epochs×5 folds), not measured full training. N L548's 8.5 min is a skip. No measured 13B timing; multiwin assumed 13–18 h. Per batch add 1.5–3 h/arm prep/scoring/I/O +2–3 h smoke; upper adds 30% training slowdown/recovery. GPU allocated throughout. Scenarios, not CIs.

| Option | Training h | Occupied h | USD 8/64 | USD 12/180 |
|---|---:|---:|---:|---:|
| Desk stop / preserve 13A | 0 | 0 GPU | 0 experiment | 0 |
| Lean zscore+repeat | 26 | 31–42.8 | 105–145 | 140–193 |
| Preferred three-arm screen | 39 | 45.5–62.7 | 154–212 | 205–282 |
| Screen+second baseline repeat | 52 | 60–82.6 | 203–280 | 270–372 |
| All five defaults | 87–102 | 96.5–150.6 | 327–510 | 435–678 |
| Multiwin extension | 13–18 | 16.5–29.4 | 56–100 | 74–132 |
| L own/fixed-patch placeholder | 35–45 | 38.5–64.5 | 130–218 | 173–290 |
| Extra M / pnormct | 13 | 16.5–22.9 | 56–78 | 74–103 |
| Candidate+control repeat | 26 | 31–42.8 | 105–145 | 140–193 |
| Two realizations/all screen arms | 78 | 89–122.4 | 301–415 | 401–551 |

Fixed-patch L is a placeholder. Mask repair: ≥pair-row cost plus unknown QC labor; defer. Nested 13A: 5×4 inner+5 outer=25 fits/model; timing unknown, reject uncosted expansion. Retaining E: zero experiment time.

40GB saves $0.3996/h at equal speed/fit. Separate CPU analysis 4 cores/16 GiB=$0.316512/h, 1–3 h=$0.32–0.95; avoid double-counting scoring. Storage/egress/premiums/queues/intervention/Colab units/token costs/funds unknown. Estimates never raise caps, including smoke.

Model-call estimates (not fits/admissions): proposal author/review/disposition=3, +2/revision cycle, thus 3–9 with three cycles. Executable author/review/decision + result interpretation/review/disposition adds 6: batch nominal 9, 9–15 allowing three additional cycles total. Screen+extension: 18–30; retaining E: 0 extra; separate formal interpretation: 3–9. Upper estimates may exceed caps; no authority follows.

Binding limit decision SHA256 38b3f7298f64f53396318b2e460c0b2a80013dcef2bcbd30168444c5f24609ff: item2 sixteen calls, experiment items3/4 twenty, UTC-day thirty across roles, scientific batch sixty; GPU dollar caps unchanged. Past/failed/uncertain calls stay counted. Remaining balances/exact dollar caps unavailable: no assumed headroom. Three revision cycles/stage is a maximum within remaining caps. No other model calls here.

## Review response

F is open, disposition null; original review 78d2c082c82ae30e51a9582080ce18b4f9c48abad965c316cd97a16beea34cb0: REVISE. Prior empty-index statement was historical. S's closures stay closed, without proving later success. Report unchanged.

- **F-VERDICT-FOLD-MEMBERSHIP**, blocker: “a reduced FOLDS_TO_RUN ... would still satisfy the 'all N_ALL scored' gate”. Verified B L455,563,601,635–640. Propose schedule-independent frozen membership: exactly 99 unique patients/five disjoint folds; complete outer-join equality candidate/A1/repeat. Reject missing/extra/duplicate members, duplicate folds, overlaps and changed receipts. Future subset/duplicate/join tests required. No code fixed/tested; execution hold.
- **F-MAGNITUDE-RATIO-GATE**, blocker: “One retraining realization is a point, not a variance estimate”. Verified B L359,658–662. Code takes absolute mean repeat change: zero gives infinity, small denominators inflate ratios; negative signed change becomes absolute. Preserve criticism with this clarification. Answer 3 removes ratio/“not distinguishable from retraining” threshold, binds conjunction/repeat identity. Proposal correction only; executable hold.
- **F-COVERAGE-PROXY**, suggestion: “the proxy does not establish true coverage”. Verified B L1433,1447,1482–1484; possible transform bias, impact untested. Answer 6 binds pre-replacement finite support/provenance/fallbacks. Evidence missing, no patient audit; future implementation/interpretation hold.
- **F-SELF-REVIEW-NOT-OPPOSING**, blocker: “a real run requires source-bound opposing-family review of specification and executable bytes”. Retained limitation: revised executable review, baseline plans/environment receipts, coverage provenance and timing/capacity evidence absent. Analysis review cannot approve missing code. Future smoke needs separate scoped authority; measured projection then informs full-run decision. No execution authority or run-before-authorization requirement.

Responses are not closure; only independent APPROVE closes findings. No other model call here. REVISE returns to author within three cycles/caps; REJECT or unresolved fourth review stops. Privacy/secret, test-set/leakage, budget or beyond-item2 decisions stop for operator; correctable aggregate/statistical arithmetic is metric/statistic. No scope expansion needed; execution/patient access/dispatch held. STOP FOR OPERATOR REVIEW.
