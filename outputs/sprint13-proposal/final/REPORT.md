# Sprint13 proposal ready for operator review

# Summary

Should Sprint13B run every proposed arm or start smaller? Modify it to a three-arm normalization screen: repeat, z-score and histogram equalization. Defer extra windows, the L preset and CT normalization. Estimated occupied runtime is 45.5–62.7 GPU hours, costing about $154–282 under the stated hardware scenarios; all five arms would cost about $327–678. These are estimates, not measured Sprint13B runtimes. Sprint12b already explored normalization on the same 99 patients. Supplied 13A fusion results improve Dice by 0.028 but reduce lesion F1 by 0.030. The revised notebook has independent approval and passing controller synthetic checks; full execution remains untested. Stop for operator review of the completed proposal.

# Details

The charter question is whether admission-available imaging can predict released follow-up infarct tissue, and whether a fitted predictor merits further investment. Clinical outcomes remain a later question. The recommendation is **MODIFY**, preserving the frozen A1 baseline and a small source-image normalization comparison. It is not an efficacy conclusion. The smallest useful comparison is repeat plus z-score; histogram equalization adds a distinct distribution-shape intervention for one additional M-arm cost. A negative screen answers only whether these transforms help this pipeline on these exposed development patients. It does not show that imaging is uninformative or that wider windows or a larger configuration cannot help.

The reviewed specification is `current/ANALYSIS-SPEC-3.md`, SHA256 `9de9e42208fe2bbf41b15230dccaf7738da70ab27978612b157b9f9fc0a24478`. Its exact supplied text, including the terminal newline, was recovered from `prompt.md` and hash-checked. This report updates its historical finding and receipt status; its scientific design and the approved notebook patch are preserved. No new performance calculation is presented.

Source keys below refer to the original staged safe views. C/O means notebook cell/output; L means line in that view. The registered source and omission identities are retained by the navigation index. Source-supported observations, methodological judgments and runtime assumptions are identified separately.

- **S:** [Accepted stock-take](/workspace/evidence/26abd688a46f9677af9a572fcdbe0958d711d8fe1b8ea9444ae8cb87a8f563c0-prior_results.txt), SHA256 `26abd688a46f9677af9a572fcdbe0958d711d8fe1b8ea9444ae8cb87a8f563c0`.
- **B:** [Original 13B safe view](/workspace/evidence/04aeab89022993885cccf5438bb8fe3bf4604be3cdcab751e5f5cdaa1b2e2ce8-view.txt), SHA256 `04aeab89022993885cccf5438bb8fe3bf4604be3cdcab751e5f5cdaa1b2e2ce8`.
- **A:** [Earlier 13A proposal safe view](/workspace/evidence/e353483cb2f8669c70d23591613d3b959806cdd6258ff782523344289be10c79-view.txt), SHA256 `e353483cb2f8669c70d23591613d3b959806cdd6258ff782523344289be10c79`.
- **E:** [Operator-run 13A aggregate outputs](/workspace/evidence/e5cb1b3e0bb35fdd8aa5cb613390951f5c4636c8fa59edf692737a1084344195-view.txt), SHA256 `e5cb1b3e0bb35fdd8aa5cb613390951f5c4636c8fa59edf692737a1084344195`.
- **N:** [Sprint12 nnU-Net safe view](/workspace/evidence/ccd74c0e954d7b2c21439873bb9bc9e7e8c415ed34804ce995c6204620e51706-view.txt), SHA256 `ccd74c0e954d7b2c21439873bb9bc9e7e8c415ed34804ce995c6204620e51706`.
- **T:** [Sprint12b safe view](/workspace/evidence/7ad63a2baf5cc627ab046438f67b1313fc5f499e3b4d23832e102b7005cf922f-view.txt), SHA256 `7ad63a2baf5cc627ab046438f67b1313fc5f499e3b4d23832e102b7005cf922f`.
- **R:** [Saved price evidence, 2026-10-05](/workspace/evidence/0175d1c5f057e3308444f17ef5ea9268dd4308381ada36c36f773aec5d799a57-prior_results.txt), SHA256 `0175d1c5f057e3308444f17ef5ea9268dd4308381ada36c36f773aec5d799a57`.
- **G:** [Item2 evidence limitations](/workspace/evidence/97f0dce46af8a422dcacfd707b710cb37e7696b1d4b866ae4cab861ce7a34cbd-prior_results.txt), SHA256 `97f0dce46af8a422dcacfd707b710cb37e7696b1d4b866ae4cab861ce7a34cbd`.
- **D:** [Controller actual notebook diff](/workspace/evidence/a67bb73a24409fae1277087c282d1f6b89a951a3563fb172b501d5441cb68435-notebook_diff.txt), SHA256 `a67bb73a24409fae1277087c282d1f6b89a951a3563fb172b501d5441cb68435`.
- **P:** [Controller patch/compile provenance](/workspace/evidence/2c2a241b17d18c5430e2a8d9e27fcae48b4f4ec34bd121a9b0d617b138d88f82-notebook_provenance.txt), SHA256 `2c2a241b17d18c5430e2a8d9e27fcae48b4f4ec34bd121a9b0d617b138d88f82`.
- **Y:** [Controller synthetic execution receipt](/workspace/evidence/b2a5ce6ae645ab2d91f8c388b8f525f6bc7214f58adf2b5659e72820a546adf3-synthetic_tests.txt), SHA256 `b2a5ce6ae645ab2d91f8c388b8f525f6bc7214f58adf2b5659e72820a546adf3`.
- **C:** [Carried execution conditions](/workspace/evidence/077b82acb5d028c1c645e9598e6abd4c472f6bce6027708752cb24362cd2d6d2-execution_conditions.txt), SHA256 `077b82acb5d028c1c645e9598e6abd4c472f6bce6027708752cb24362cd2d6d2`.

## Eight plan answers


1. **Screen first: MODIFY.** Repeat, zscore, histeq on five frozen folds; preserve A1. Reject immediate all-arm commitment. Lean repeat+zscore is defensible. No performance stopping mid-fold-set or automatic extension; negatives concern these transforms only. The screen reduces initial spending but is not a validated gate for discarding multiwin or L, which address different questions. Any later extension must retain the comparison history; keeping a four-arm family does not erase adaptive selection or repeated development-set exposure.

N C22/O0 L698–708: A1/no-CTA/normalized Dice 0.200/0.195/0.203; normalization +0.003 [−0.015,+0.020], CTA +0.005 [−0.007,+0.016], n=99, exploratory 95% intervals; neither superiority nor equivalence.

**Sprint12b overlap:** T C20/O0 L814–842: normalization +0.008 [printed +0.000,+0.015], 15 predictions/patient (5 arrangements×3 seeds), positive 5/5; lesion F1 +0.009 [−0.004,+0.026]. Rounded zero/MET does not verify strict positivity. Its 47 explorations include MTT +0.014 [+0.006,+0.021], reference tissue, ratios/ranks, validity/HU, ablation/local/site normalization. Same exposed patients, not replication. 13B adds source-image nnU-Net/post-window transforms, not normalization novelty. Tree invariance is qualified: clipping creates ties; patient transforms change cross-patient order.

2. **Second windows: defer bundle.** B C4 L711–713: CT 20–50 HU, CBF 0–100, CBV 0–4, MTT 0–12 s, Tmax 0–20 s, CTA 0–300 HU. Wider CBF/Tmax/CTA recover clipped information; narrow CT/CBV/MTT re-express it. Twelve channels change parameters/storage, not six isolated effects. N C20/O0 L469–470 smoke upper-clipping medians: CBF 8%, Tmax 12%, CTA 10%, CT 10%, CBV 6%, MTT 3%, only 12 patients. Tmax saturates above 7, not throughout 6–7. Require label-blind units/coverage/clipping review; clinical/winner rationales lack inspected primary literature. No outcome tuning; changed windows require review.

3. **Four primaries; conjunctive verdict; one repeat for sensitivity.** Retain 98.75% patient-percentile Dice intervals, 10,000 draws, 0.625/99.375 endpoints, with the four-arm family retained even when some arms are unrun; deterministic SHA256 seeds. Require frozen 99/folds 0–4, complete unique candidate/A1/repeat joins. Both vs-A1/vs-repeat intervals positive: better; both negative: worse; otherwise no clear difference. Missing: provisional; invalid: raise. Unrounded endpoints, unrun/failed attempts and secondary metrics must be reported. No equivalence, confirmation, clinical threshold or automatic promotion: intervals condition on fitted models and exclude training/history/shared-training uncertainty.

B C16 L359: train_seed=1 is a pairing label; training unseeded. Patch retains that fact and binds distinct realization/environment identities. Remove ratio/noise gates. Two baseline repeats leave candidate variance unknown; later candidate+baseline pair costs 26 training h; even two pairs remain descriptive. Seeded training requires another reviewed version; repeats cannot correct environment drift.

4. **L: defer; whole preset if revisited.** Tests configuration, not size causality. Record architecture/planner/spacing/patch/batch/steps/hardware. Fixed M patch+L is a different question; do not run both. Minimum 32 GB does not prove fit or timing.

5. **Defer pnormct.** Overlaps T's HU exploration; adds 13 training h. Comparator is A1_pnorm_v2 (B C22), not A1; environment/plans mismatch confounds CT effect. Contemporary pnorm_v2 costs another 13 h. Require admission-only reference/validity rules.

6. **Covered-brain statistics: agree; replace proxy.** B C8 L1433/1447/1482–1484 uses all-zero maps and coerces nonfinites before statistics. Patch helper uses raw finite values ∩ brain ∩ supplied coverage; keeps valid zeros. Without coverage it reports coverage_known=False; real perfusion transforms stop pending authenticated mask/loader. Zero outside support, unchanged full scoring truth. Empty/constant support returns finite helper zeros/metadata, then pipeline holds; retain SD floor 0.01 and 256 histogram bins. Actual coverage provenance/counts/fallbacks remain item4 evidence; patient coverage has not been audited here.

7. **13A: preserve P1/P2; no schedule/rerun.** E paired.csv: P1 +0.003 [97.5% +0.001,+0.004], P2 +0.028 [97.5% +0.015,+0.042], n=99. These are total pipeline changes including resampling/rule and, for P2, fusion. Same-rule fusion +0.025 [95% +0.014,+0.038] is exploratory. P2 lesion F1 −0.030 [−0.048,−0.015] opposes Dice-only promotion. E complementarity.csv: correlation 0.81/shared missed-truth 0.671, dependent errors.

OOF meta-training models were trained partly on the scored fold; excluding its rows does not remove dependence. E says size unknown, correcting A C8's “small” claim. Reject unbiased-stacking language. Nested base fitting or approved frozen-rule evaluation is needed for stronger claims, neither now. E validation asserts 99 reused caches/297 mask-rebuild checks; probability-mask Dice 0.9187 does not establish A's native-grid≥0.99 check. G: executed r4 source absent. No new validation claimed.

8. **Keep SynthStrip for comparability, conditional on integrity.** Repair changes baseline/all arms. Keep full truth/outside-mask misses; no exclusions. N smoke minimum 83% infarct-in-brain is not cohort anatomy. Repair needs label-blind QC and matched baseline/review; integrity failure stops comparison.

## Cost scenarios: estimates, not measured runtimes

R, Modal rates recorded 2026-10-05 (not refreshed/Colab rates): A100-80GB $0.000694/s=$2.4984/h; 40GB $0.000583/s=$2.0988/h; physical CPU $0.0000131/core-s=$0.04716/core-h; RAM $0.00000222/GiB-s=$0.007992/GiB-h. One sequential 80GB GPU +8 cores/64 GiB=$3.387168/h; +12 cores/180 GiB=$4.50288/h. Fit unknown; observed 179 GB/12 CPU is not billing.

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

Fixed-patch L timing is a placeholder. Mask repair: ≥pair-row cost plus unknown QC labor. Nested 13A: 25 fits/model; assumed 2.6 h/M-fold gives 65 h nnU-Net alone, excluding other models/overhead. This is at least $220–293 for nnU-Net alone at the two composite rates; the entire nested procedure is not costed and is rejected as an expansion. E reuse: zero experiment time.

40GB saves $0.3996/h at equal speed/fit. Separate CPU analysis 4 cores/16 GiB=$0.316512/h, 1–3 h=$0.32–0.95; avoid double-counting scoring. Storage/egress/premiums/queues/intervention/Colab units/token costs/funds unknown. Smoke counts against caps.

Scientific model calls (estimates, workflow-call scenarios; not training fits): author/review/disposition 3 + 2/revision = 3–9 within three cycles. A future executable author/review/decision (3) and result interpretation/review/disposition (3) add 6: 9–15 per standalone training option; screen plus a separately considered extension totals 18–30. These scenario totals include proposal work, rather than being additional calls to spend after this handoff. Reuse 13A: 0 extra; separate interpretation 3–9. Desk stop: 0 experiment calls. Token/subscription dollars unavailable. No remaining allowance assumed. Each M or L arm entails five full training fits, separate from scientific model calls: lean 10 fits, preferred screen 15, screen plus second baseline repeat 20, all defaults 25, and two realizations of all screen arms 30. Each additional arm also has a 12-case, five-epoch smoke stage in the original design; smoke/recovery is included in the runtime allowance, not counted as another full fit. A paired repeat adds 10 full fits. The 25-fit nested estimate assumes five outer fits plus four inner fits within each of five outer folds, per base model.

## Delivery identity, omissions and external attribution

The original validation file [b2485e2…](/workspace/evidence/b2485e2dcfdeeb10bcacf53d231b2d223781bdd2070f9a08477e182fdd69cdfa-validation_result.txt) reports `VALID`, `SAVED_EVIDENCE_IDENTITY_ONLY`, `execution_performed=false` and `scientific_acceptance=false`. Its registry binding is `67fd16e52ecbbed18a9ba6b4735a2a4a74dfb8a32dc3800a4d4809e360b06317`, matching the reviewed specification and navigation index `629f3dc8af24ebf537b3209217f1819c4e5391354db609d19aae047a34a03087`. All 170 registered delivery files matched their hashes; all validation descriptors matched navigation after removing the added readable-copy descriptor. This mechanical delivery check is not fresh scientific computation, verification of external conclusions, or a claim to have scientifically inspected all 170 files. The standalone registry is not staged; its bound identity and selected descriptors are available.

For the inspected views, registered secret and locked/unknown-identifier scans report PASS and `per_patient_material=[]`. **Patient-level evidence files used in this analysis: none; registered patient-level analysis reasons: not applicable.** S is an aggregate stock-take that itself used a wider historical packet; its listed patient-level sources are not imported into this analysis. G expressly withholds Sprint6, Sprint11, Sprint12-trees and the two anatomy documents `doc-b41b360a84877765` and `doc-4189b93d320498af`. Their historical summaries do not establish new patient inspection here.

The 13B original SHA256 is `73f656d542c033df30fdfca8a36d1bd2899fc1563d9d4effdf9ea634de164ef7`; safe view SHA256 is `04aeab89022993885cccf5438bb8fe3bf4604be3cdcab751e5f5cdaa1b2e2ce8`; omission manifest SHA256 is `fe9a05c826a2f3b210912e6d5342cb205a59cd3afd662b64db7ff52b74488dd2`. The excluded-membership span is `cells/4/source` bytes 2090:2120, hash `8ffa5399e3c59a3fee6bb8a4cca50b89b57fdcd62163dcbf20a5c289ffa0674c`. Its value was not supplied or reconstructed. The controller externalized it to a private hash/count-checked input. Metadata/non-text notebook units are also omitted.

N's omission manifest is `c0a5efde1281322c7718da784f3e5111b4713ad410a36d6a7a21a4d365ab597e` and T's is `8687544510a4929cc3cb0162817206b1efb6c2d69f4aa9a1eb5c135365a5dfea`; each binds its exact view and original, preserving excluded-membership and opaque metadata omissions. A's manifest is `f227358651440a59bf96eb2ee42cd06b6a7abf238e95d1225e9753642d2768c5`. These are restricted views, not replacements for the original executable notebooks.

E is an operator-run external archive, SHA256 `bdf0a546052899d0a82aee70676abe5ff22c949f88f73287249891bab517b9a3`, containing six selected aggregate text members. Its omission manifest `5a52ab34051166bc70aa9173f114034eca6b93045615dd92e5c2876878dee56c` binds the supplied view and withholds `sprint13a_precision_recall.png` (SHA256 `d7acb5fae690881aa6d09435cd6b0515051c7ec24199891e3ae9072172d8fb02`) and `sprint13a_dice_tree_vs_nnunet.png` (`db91a20d85a371dee9f3017f18c7d736ad5a474681eec8a2e13bc17a487fd4a9`). No figure interpretation is inferred. E's provenance specifies r4, split 101, seed 1 source products and 2,000 patient bootstrap draws, seed 0; it is distinct from the earlier A notebook and from proposed 13B's 10,000 draws. Executed r4 source and independently inspectable native-grid verification remain unavailable. Its reported 297 rebuild checks and 99 reused caches are external assertions, not checks performed in this analysis.

## Actual notebook changes, synthetic evidence and current findings

[notebook.patch.json](/workspace/notebook.patch.json) is the exact already-reviewed v3 patch, SHA256 `9d9a7d64a6ff125f550f2796c835f9f7c6f216e740f665cf2149dac351038492`, 40,736 bytes. Its six edits replace visible original spans in cells 0, 2, 4, 8, 20 and 22. Each replaced-byte hash was checked against B; every edit lies within one retained span, and the edits do not overlap. It uses the required original and view hashes and the `safe-notebook-patch/v1` schema. It is not a patch against an earlier draft.

[revised-13B.ipynb](/workspace/revised-13B.ipynb) is a byte-preserved copy of the controller-produced notebook, SHA256 `9e62bec160153ae605d0e4f5a3121977256fbc08e5a25a9421279a127c169a46`. No new code changes were made after that review. P binds the original, patch, notebook and actual diff `a67bb73a24409fae1277087c282d1f6b89a951a3563fb172b501d5441cb68435`, reports original unchanged, and lists compile PASS for 11 code cells. The evidence record is attributed to the controller, not a compilation performed here.

Y binds that exact notebook and harness `61739d4064c85ccecdf5085260ea125aaa453ca5914d2f01d19117dcb3659bbf`. It reports exit 0, 1.6802469019 seconds elapsed, isolation with no network/credentials/patient mounts, and four passing test groups: fold completeness (99 synthetic rows, five folds, seven negative cases), verdict rule (nine cases), finite/coverage/zero/fallback handling, and six original lesion fixtures. This elapsed time measures the synthetic harness only. It says actual pure functions were extracted by AST, with no top-level loading, training or driver execution. The separate harness source and `notebook-synthetic-contract.md` are not staged here; the supplied specification names contract hash `91deacb34d7cfa3c65b6add240ea174de3451ef266fb8ad8a21a0cc2c921484b`. Thus receipt contents and reviewed call sites can be inspected, but the entire harness cannot be independently re-audited from source here. A passing synthetic receipt does not prove full pipeline execution.

Both current finding records are **closed**, by the exact independent review `current/approval-STEPD-e53c2afe1f1a48c09da02332e43f91269b4e94a71713056b7cebec0ca689f04a-run_spec_review-3.json`, SHA256 `2bce3d6d24e9e4edc37f9424f2dfc32bbb3494e2ba271b138fca193c6a9647f2`, verdict APPROVE, findings empty. The original finding and embedded closure texts were read and their hashes verified in [record 1](/workspace/evidence/5bae00149f2f8cb765bc048fba80db8d238ee2ecff175ff1d7eb4dfdb837d933-finding.json) and [record 2](/workspace/evidence/920bba358d505ec6df34a50ec7046e5e8fc513056c29f16fb7d5f4fbac0065cd-finding.json). This is an attributed existing closure, not a new author disposition. The v3 specification's wording that F1/F2 are open and receipts absent describes its earlier point in time; it is not the current status. Original REVISE judgments remain intact.

| Original finding and criticism | Correction visible in actual notebook/diff; retained limit |
|---|---|
| F-VERDICT-FOLD-MEMBERSHIP, blocker: “a reduced FOLDS_TO_RUN ... would still satisfy the 'all N_ALL scored' gate” | Cell22 fixes N_ALL=99 and uses `validate_full_folds` in partition validation, arm tables, reference tables, comparison joins and primary reporting. It requires unique exact membership, five nonempty disjoint folds 0–4 and shuffle 101; joins are one-to-one outer joins. The independently supplied partition hash remains unset, so reporting stops before opening the partition. Reduced/invalid returned cohorts fail rather than become favorable verdicts. Y's fold tests support helper behavior, not real partition identity. |
| F-MAGNITUDE-RATIO-GATE, blocker: “One retraining realization is a point, not a variance estimate” | Cell22 removes magnitude/noise ratios and calls `verdict_from_intervals` from actual primary reporting. Both vs-A1 and vs-repeat intervals must exclude zero in the same direction. Malformed intervals fail; a missing repeat yields provisional. Full precision endpoints are saved. Candidate, baseline and repeat require distinct fingerprints/directories and environment records. This does not prove equivalent environments or independently controlled RNG; training remains unseeded. Y tests the rule, not real training independence. |
| F-COVERAGE-PROXY, suggestion: “the proxy does not establish true coverage” | Cell8 `prep_channel` passes the raw channel to `coverage_support` before statistics, retaining finite genuine zeros. The same z-score/histogram helpers use that support and zero the outside. The actual call currently supplies coverage=None, so perfusion transforms stop; no acquisition coverage is invented. Empty/constant support produces finite helper outputs but stops the real path. SD floor0.01/256 bins remain. The acquisition-mask loader and its geometry/provenance remain unfinished item4 work. |
| F-SELF-REVIEW-NOT-OPPOSING, blocker: “a real run requires source-bound opposing-family review of specification and executable bytes” | The independent v3 review inspected actual diff, executable and controller receipts and approved this proposal artifact. The execution portions remain carried in C: exact future runnable package, baseline/repeat/environment/RNG receipts, actual coverage, smoke/recovery and timing. Closure does not establish those future conditions or full execution. |

Cell2 defaults to repeat→zscore→histeq and stops before Drive mount. Cell22's partition hold and cell8's coverage hold are active code, not test stubs. They deliberately leave this reviewed copy unsuitable for real execution until its concrete missing inputs and implementation are addressed. The preserved code also continues to compare complete fold tables and baseline plan/run identities; a synthetic pure-helper pass is narrower than testing those I/O paths end to end.

## Remaining evidence and proposed disposition

[carried-conditions.json](/workspace/carried-conditions.json) is an unchanged copy of controller record C, SHA256 `077b82acb5d028c1c645e9598e6abd4c472f6bce6027708752cb24362cd2d6d2`. Item4 still needs the exact runnable package and frozen membership/split binding; baseline plans and independent-repeat/environment/RNG receipts; authenticated finite/spatial coverage and its real loader; hash/count-checked private membership input; actual smoke, recovery, timing, capacity and fit measurements; and a concrete dollar budget. These conditions are unfulfilled, not fabricated results or newly reopened findings on item2.

Historical source-image timing is a smoke measurement, not a full 13B measurement. CBF/CBV units, acquisition coverage, winner-specific recipe claims, full-cohort clipping/anatomy and current environment equivalence lack sufficient inspected evidence for stronger assertions. No new literature or novelty claim is made. S also preserves earlier unavailable export implementations, figure mappings and historical Sprint9/10 criticisms; the current two closures do not settle those separate histories or prove later execution succeeded.

For budgeting, the bound limit identity is `38b3f7298f64f53396318b2e460c0b2a80013dcef2bcbd30168444c5f24609ff`: item2 16 scientific calls, items3/4 20, UTC-day 30 across roles, batch 60. Exact past usage, remaining balances and unchanged GPU-dollar caps are unavailable. The call scenarios above are not estimates of remaining headroom. No claimed dollar feasibility depends on an invented balance.

The concrete next decision is **stop for operator review of the completed three-arm proposal and its alternatives**. There is no applicable open blocker in the supplied current finding index, so the decision uses `stop` and an empty blocker list. Repeating review/reconciliation as an automatic successor would not answer a new charter question. Preserve the operator-run 13A outputs; neither their missing r4 source nor future item4 receipts justify rerunning them here.


## Run record
Analysis plus a new notebook copy and isolated synthetic CPU tests only; no real-data notebook, GPU or Modal execution. Operator review is required before any next backlog item.
Calls: 8/16; elapsed seconds: 55138.7; rounds: {"run_spec_author": 3, "run_spec_review": 3, "result_interpretation_author": 1, "result_interpretation_review": 1}.

| Stage | Input characters | Outcome |
| --- | ---: | --- |
| run_spec_author | 102182 | COMPLETE |
| run_spec_review | 131663 | COMPLETE |
| run_spec_author | 126219 | COMPLETE |
| run_spec_review | 143511 | COMPLETE |
| run_spec_author | 145218 | COMPLETE |
| run_spec_review | 164977 | COMPLETE |
| result_interpretation_author | 125283 | COMPLETE |
| result_interpretation_review | 131711 | COMPLETE |
