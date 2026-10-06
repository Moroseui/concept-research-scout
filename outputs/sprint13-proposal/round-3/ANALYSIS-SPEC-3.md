# Sprint13B analysis specification — revised notebook proposal
run_id: stocktake-6b556dba36d299c05b8b7770
analysis_registry_sha256: 67fd16e52ecbbed18a9ba6b4735a2a4a74dfb8a32dc3800a4d4809e360b06317

MODIFY: normalization screen; reject all-arm commitment. Exploratory development evidence only. STOP FOR OPERATOR REVIEW; no execution authority.

Sources (unique evidence/ SHA256 filename prefixes): S=26abd688a46f9677 (accepted stock-take), B=04aeab8902299388 (13B), A=e353483cb2f8669c (earlier 13A), E=e5cb1b3e0bb35fdd (supplied 13A aggregates), N=ccd74c0e954d7b2c (Sprint12 nnU-Net), T=7ad63a2baf5cc627 (12b), R=0175d1c5f057e330 (prices), G=97f0dce46af8a422 (limitations), F1=ed4e52a7ba198d4e, F2=1806538e4e64fce6 (exact open findings). C/O=cell/output; L=view line.

Cited safe views/F1/F2 inspected and hashes verified; registered scans PASS. Omissions preserved. Scope6b1da45b permits a new copy, original untouched. No real runs, patient work, GPU/Modal, other model calls or dispatch. Keep25 final-evaluation/24 reserve untouched.

## Eight answers

1. **Screen first: MODIFY.** Repeat, zscore, histeq on five frozen folds; preserve A1. Reject immediate all-arm commitment. Lean repeat+zscore is defensible. No performance stopping mid-fold-set or automatic extension; negatives concern these transforms only.

N C22/O0 L698–708: A1/no-CTA/normalized Dice 0.200/0.195/0.203; normalization +0.003 [−0.015,+0.020], CTA +0.005 [−0.007,+0.016], n=99, exploratory95% intervals; neither superiority nor equivalence.

**Sprint12b overlap:** T C20/O0 L814–842: normalization +0.008 [printed +0.000,+0.015], 15 predictions/patient (5 arrangements×3 seeds), positive5/5; lesion F1 +0.009 [−0.004,+0.026]. Rounded zero/MET does not verify strict positivity. Its47 explorations include MTT +0.014 [+0.006,+0.021], reference tissue, ratios/ranks, validity/HU, ablation/local/site normalization. Same exposed patients, not replication. 13B adds source-image nnU-Net/post-window transforms, not normalization novelty. Tree invariance is qualified: clipping creates ties; patient transforms change cross-patient order.

2. **Second windows: defer bundle.** B C4 L711–713: CT20–50 HU, CBF0–100, CBV0–4, MTT0–12s, Tmax0–20s, CTA0–300 HU. Wider CBF/Tmax/CTA recover clipped information; narrow CT/CBV/MTT re-express it. Twelve channels change parameters/storage, not six isolated effects. N C20/O0 L469–470 smoke upper-clipping medians: CBF8%, Tmax12%, CTA10%, CT10%, CBV6%, MTT3%, only12 patients. Tmax saturates above7, not6–7. Require label-blind units/coverage/clipping review; clinical/winner rationales lack inspected primary literature. No outcome tuning; changed windows require review.

3. **Four primaries; conjunctive verdict; one repeat for sensitivity.** Retain98.75% patient-percentile Dice intervals,10,000 draws,0.625/99.375 endpoints even for unrun arms; deterministic SHA256 seeds. Require frozen99/folds0–4, complete unique candidate/A1/repeat joins. Both vs-A1/vs-repeat intervals positive: better; both negative: worse; otherwise no clear difference. Missing: provisional; invalid: raise. Unrounded endpoints, unrun/failed attempts and secondary metrics must be reported. No equivalence, confirmation, clinical threshold or automatic promotion: intervals condition on fitted models and exclude training/history/shared-training uncertainty.

B C16 L359: train_seed=1 is a pairing label; training unseeded. Patch retains that fact and binds distinct realization/environment identities. Remove ratio/noise gates. Two baseline repeats leave candidate variance unknown; later candidate+baseline pair costs26 training h; even two pairs remain descriptive. Seeded training requires another reviewed version; repeats cannot correct environment drift.

4. **L: defer; whole preset if revisited.** Tests configuration, not size causality. Record architecture/planner/spacing/patch/batch/steps/hardware. Fixed M patch+L is a different question; do not run both. Minimum32GB does not prove fit or timing.

5. **Defer pnormct.** Overlaps T's HU exploration; adds13 training h. Comparator is A1_pnorm_v2 (B C22), not A1; environment/plans mismatch confounds CT effect. Contemporary pnorm_v2 costs another13h. Require admission-only reference/validity rules.

6. **Covered-brain statistics: agree; replace proxy.** B C8 L1433/1447/1482–1484 uses all-zero maps and coerces nonfinites before statistics. Patch helper uses raw finite values ∩ brain ∩ supplied coverage; keeps valid zeros. Without coverage it reports coverage_known=False; real perfusion transforms stop pending authenticated mask/loader. Zero outside support, unchanged full scoring truth. Empty/constant support returns finite helper zeros/metadata, then pipeline holds; retain SD floor0.01 and256 histogram bins. Actual coverage provenance/counts/fallbacks remain item4 evidence; no patient audit here.

7. **13A: preserve P1/P2; no schedule/rerun.** E paired.csv: P1 +0.003 [97.5% +0.001,+0.004], P2 +0.028 [97.5% +0.015,+0.042], n99. These are total pipeline changes including resampling/rule and, for P2, fusion. Same-rule fusion +0.025 [95% +0.014,+0.038] is exploratory. P2 lesion F1 −0.030 [−0.048,−0.015] opposes Dice-only promotion. E complementarity.csv: correlation0.81/shared missed-truth0.671, dependent errors.

OOF meta-training models were trained partly on the scored fold; excluding its rows does not remove dependence. E says size unknown, correcting A C8's “small” claim. Reject unbiased-stacking language. Nested base fitting or approved frozen-rule evaluation is needed for stronger claims, neither now. E validation asserts99 reused caches/297 mask-rebuild checks; probability-mask Dice0.9187 does not establish A's native-grid≥0.99 check. G: executed r4 source absent. No new validation claimed.

8. **Keep SynthStrip for comparability, conditional on integrity.** Repair changes baseline/all arms. Keep full truth/outside-mask misses; no exclusions. N smoke minimum83% infarct-in-brain is not cohort anatomy. Repair needs label-blind QC and matched baseline/review; integrity failure stops comparison.

## Costs: estimated, not measured

R, Modal rates recorded 2026-10-05 (not refreshed/Colab rates): A100-80GB $0.000694/s=$2.4984/h; 40GB $0.000583/s=$2.0988/h; physical CPU $0.0000131/core-s=$0.04716/core-h; RAM $0.00000222/GiB-s=$0.007992/GiB-h. One sequential 80GB GPU +8 cores/64 GiB=$3.387168/h; +12 cores/180 GiB=$4.50288/h. Fit unknown; observed179GB/12CPU is not billing.

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

Fixed-patch L timing is a placeholder. Mask repair: ≥pair-row cost plus unknown QC labor. Nested13A: 25 fits/model; assumed2.6h/M-fold gives65h nnU-Net alone, excluding other models/overhead; reject uncosted expansion. E reuse: zero experiment time.

40GB saves $0.3996/h at equal speed/fit. Separate CPU analysis 4 cores/16 GiB=$0.316512/h, 1–3 h=$0.32–0.95; avoid double-counting scoring. Storage/egress/premiums/queues/intervention/Colab units/token costs/funds unknown. Smoke counts against caps.

Scientific model calls (estimates, separately admitted; not training fits): author/review/disposition3 +2/revision =3–9 within three cycles. Future executable review/decision and result interpretation/review/disposition add6:9–15 per standalone option; screen+extension18–30. Reuse13A:0 extra; separate interpretation3–9. Desk stop:0 experiment calls. Token/subscription dollars unavailable. No remaining allowance assumed.

Binding limit decision SHA256 38b3f7298f64f53396318b2e460c0b2a80013dcef2bcbd30168444c5f24609ff: item2 sixteen calls, experiment items3/4 twenty, UTC-day thirty across roles, scientific batch sixty; GPU dollar caps unchanged. Past/failed/uncertain calls stay counted. Remaining balances/exact dollar caps unavailable: no assumed headroom. Three revision cycles/stage is a maximum within remaining caps. No other model calls here.

## Finding responses and handoff

F1/F2 are open, disposition null, both original REVISE reports unchanged. Historical closures in S are not reopened or proof of later success. Author responses are not closure.

- F-VERDICT-FOLD-MEMBERSHIP (blocker): “a reduced FOLDS_TO_RUN ... would still satisfy the 'all N_ALL scored' gate” (B L455/563/601). Cell22 calls validate_full_folds on pinned membership, loaded tables and comparison operands: 99 unique members, five disjoint nonempty folds 0–4, shuffle101, exact assignments. Duplicate receipt folds/invalid tables raise; outer joins require complete equality. N_ALL=99, independent of schedule. Partition SHA256 unavailable: None stops reporting pending item4 binding; no guessed pin/identifier.
- F-MAGNITUDE-RATIO-GATE (blocker): “One retraining realization is a point, not a variance estimate” (B L359/658–662). Cell22 removes ratio/noise thresholds; real primary reporting calls verdict_from_intervals on both intervals. Invalid intervals raise; absent repeat is provisional. Unrounded endpoints saved. Distinct fingerprints/directories/environment required; new identity prevents original receipt reuse. Training remains unseeded.
- F-COVERAGE-PROXY (suggestion): “the proxy does not establish true coverage” (B L1433/1447/1482–1484). Cell8 coverage_support retains valid zeros, intersects raw finite values/brain/supplied coverage; unknown coverage is explicit. prep_channel uses it before statistics and holds perfusion transforms without coverage. Same transform helpers zero outside support; finite fallbacks hold the pipeline. Optional pnorm held; real coverage/impact remains item4.
- F-SELF-REVIEW-NOT-OPPOSING (blocker): “a real run requires source-bound opposing-family review of specification and executable bytes”. Retained. Latest notebook authority permits this patch; controller applies it to a new copy and reviewer inspects actual diff/tests. Opposing review, baseline plans/environment, coverage provenance, separately authorized smoke/recovery, measured timing/fit/capacity and admission remain item4 conditions. Their nonexecution here is not a demand to exceed item2.

Patch uses exact task bindings/kept spans; cell6 fixtures unchanged. Cell2 defaults to screen and stops before Drive mount. Later review must release holds.

Controller contract 91deacb34d7cfa3c65b6add240ea174de3451ef266fb8ad8a21a0cc2c921484b covers membership, verdict, coverage/transforms and lesion fixtures. No controller receipt or carried-conditions.json is present here: no compile/test PASS claimed. Controller must attach diff/notebook/compile/isolation/harness/exit/four-group receipts and carried-conditions.json; reviewer checks call sites. Synthetic success is not pipeline execution.

Only independent APPROVE closes findings. REVISE returns within three cycles/caps; REJECT or unresolved fourth review stops. Privacy/secret, test-set/leakage, budget or beyond-item2 decisions stop for operator; correctable aggregate/cost arithmetic is metric/statistic. STOP FOR OPERATOR REVIEW; no execution authority.
