# Interpretation review — idea 023, round 2

## 1. Citations resolve

I re-resolved every citation in `interpretation.md` against
`probes/023/results/results_v2/` and the approval marker. All quantitative
transcriptions are exact to the precision stated.

- `run_log.txt`, line 1, and `ideas/023/HUMAN_APPROVED_PROBE`: approval is
  bound to contract blob `03d4545fe293f0067c69ce9e9e696ec97b894d7b`; the
  marker timestamp is 2026-08-28T02:31:13.281441+00:00.
- `summary.json`: archive MD5 and Zenodo checksum, Phase-S output hash,
  released/census/analyzed/reserved case counts, `g_label_passed`, run status,
  all three identity-MAD values, both exclusion counts, tissue-audit row
  count, and split-manifest hash all match.
- `determinism_manifest_start.json`: the Phase-S CSV SHA-256 is
  `59069fa92399cd5c600c89e0d66bb4c7c12679e14f12824b54ae0ce6a6061ef4`;
  the start and end determinism manifests are byte-identical as stated.
- `per_stratum_summary.csv`: for strata 1–3, all cited patient counts, means,
  mean confidence limits and widths, medians, and median confidence limits
  match exactly. The reported signs and interval-exclusion descriptions also
  follow those rows.
- `resolved_config.json`: the 20-patient support floor, 100-voxel cell floor,
  0.15 maximum CI width, and seed 20260824 match.
- `identity_residual_summary.csv`: the three cited median absolute centered
  residuals match exactly.
- `exclusions.csv`: sub-stroke0043 is excluded for
  `source_corrupt_member`; the noncanonical sub-stroke0142 lesion member is
  excluded while the case has a separate analyzed-case row; sub-stroke0113
  records 302261 nonfinite MTT voxels; and sub-stroke0002 records a vessel CBV
  p98 of 29.140625.
- `per_patient.csv`: sub-stroke0002, stratum 1 has
  `d = -0.20385563685311792`.
- `bin_tissue_audit.csv`: every cited example resolves exactly:
  sub-stroke0092 stratum 1 Q1/Q4 medians 3.0/23.0; sub-stroke0057 stratum 1
  5.0/24.0; sub-stroke0189 stratum 1 6.0/25.0; sub-stroke0002 stratum 2
  21.0/21.0; sub-stroke0183 stratum 2 23.0/5.0; sub-stroke0109 stratum 3
  30.0/58.0; and sub-stroke0133 stratum 3 Q4 IQR 314.5.

No uncited quantitative result remains. The archive SHA-256 and member count
in the result card are also present in `provenance.json`; the primary metric,
three fixed bands, 2,000 bootstrap resamples, and gate conjunction reproduce
the contract and resolved configuration rather than introducing new results.

## 2. Claim bounds

The round-1 blocker is resolved. Cohort-frequency language such as “most
cases,” “often,” and “typical” has been removed. The HU discussion now labels
each observation as a cited row-level example and repeatedly states that no
cohort-level prevalence was computed. Likewise, the mean/median divergence is
limited to between-patient heterogeneity; the text explicitly says that no
contribution analysis exists and does not claim that a minority drives the
means.

The interpretation preserves the contract's scope: 99 analyzed census
patients, icobrain-cva maps, one frozen outcome census, no model-use claim,
no CBV-versus-MTT attribution, and no autoregulatory or causal upgrade. The
49 reserved cases and hidden test set remain out of scope. Uncertainty is
correctly case-level through the patient bootstrap, not seed-level. There is
no tier-2 endpoint, benchmark margin, anchor population, or baseline promoted
to a performance floor.

## 3. Completeness without cherry-picking

I checked all three rows of `per_stratum_summary.csv`, including the material
sign reversal between strata 2 and 3 and the stratum-1 interval containing
zero; all three median contrasts; all 297 `per_patient.csv` rows; all 594 HU
audit rows; the complete exclusions table; all three identity-residual rows;
and the support/configuration gates. The interpretation reports the opposing
directions, near-zero medians, authorized source-corrupt and duplicate-member
handling, tissue-audit limitations, and untouched reserved cases. No material
table feature contradicting a stated finding is omitted.

## 4. Verdict separation

“Demonstrates” is confined to the valid run, preregistered negative gate,
identity residual, and authorized exclusions. Per-band meaning, heterogeneity,
and tissue-composition implications remain under “Suggests” and are explicitly
exploratory or inferential. “Does not establish” correctly blocks broader
biological, physiological, model-use, channel-attribution, and generalization
claims. The PAUSE recommendation follows the contract's `negative_pattern`
without treating it as evidence that the joint state lacks biological value.

## 5. Plain-language fidelity

There is no separate plain-language summary. The closing positive/negative
recap and next-decision section retain the same scope limits as the technical
sections. In particular, the revised recap confines HU imbalance to cited
example cases and states that cohort prevalence was not quantified.

```json
{"verdict": "APPROVE"}
```
