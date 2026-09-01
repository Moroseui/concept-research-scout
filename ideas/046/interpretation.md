# Interpretation — idea 046, contribution census (contract v2)

## Result card

- **Idea:** idea-046 — Which observed cases numerically carry the band-2/3
  reversal? (descriptive finite-population contribution census;
  revise-in-place ratified by the operator 2026-09-01, `unblock_ack.txt`
  on record)
- **Probe:** probe 046, contract v2 — the finite-population contribution
  census. Position in the experiment sequence: the second and final probe
  of the idea's primary rung. The completed v1 definition audit (contract
  v1, blob `3996009bccfcfa939984fed051ee303a29a960a0`; bundle
  `probes/046/results/results_v2`) established that the frozen definitions
  are coherent and well-posed; its positive pattern authorized drafting
  this census contract, which received fresh human approval and executed
  the census itself.
- **Dataset:** the imported idea-023 take-13 per-patient table,
  `probes/023/results/results_v2/per_patient.csv`, SHA-256
  `1d01551c888d77b6382f7cbe36e4bb68a6d2f2ef4b26e09832bfda45d2c40e0c`
  (contract-pinned). Upstream lineage: idea-023 take-13 (contract
  `03d4545fe293…`), derived from ISLES'24, Zenodo record 16813698. The
  probe read no ISLES'24 payload, image, phenotype, or cache file — only
  this one frozen CSV.
- **Primary metric:** `complete_finite_population_contribution_accounting`
  — the complete ordered per-case signed contribution table
  (`c_i = (d_i,band3 − d_i,band2)/99`) and the signed cumulative
  sequence, which must exactly account for the realized equal-patient
  band-3-minus-band-2 estimator (additive-identity residual ≤ 1e-12 under
  stable summation, enforced as an execution guard).
- **Contract blob:** `942e530737c90b666baa4c9985fd0329296ef140`
  (verified against `ideas/046/HUMAN_APPROVED_PROBE`, approved
  2026-09-01T22:37:49Z, and recorded by the run itself
  [cite: resolved_config.json | top-level | contract_blob]).
- **Results bundle:** `probes/046/results/results_v3`, 15 files, imported
  2026-09-01T22:53:56Z at commit
  `30c360113e669542397288437a8690a561f40eb1` (byte-manifest SHA-256
  `997914ac477909b4077c2fd0a18d3fbea3054e7df0cd058344422527aededd60`
  [cite: ../results_v3.import.json | top-level | manifest_sha256]);
  record-result transaction (PROBED event, digest, re-materialized state)
  at commit `0d36ee05c10f06c27ef1aba18840989f30914fa5`.
- **Families:** probe code authored by the codex family, probe review by
  the claude family (two rounds: round-1 REVISE on the missing v1
  lineage-guard comparison, round-2 APPROVE). This interpretation is
  authored by the claude family; cross-family review by the codex family
  is pending (round 1).
- **File-lineage note:** this document supersedes the v1 definition-audit
  interpretation at the working path `ideas/046/interpretation.md`,
  following the repository's standing working-file convention (already
  applied when contract v2 replaced v1 at `ideas/046/probe_contract.yaml`
  with the v1 text pinned by blob). The v1 interpretation is preserved
  verbatim at git blob `256437be57a10a78d404e2a66024b57033977e9f`, its
  cross-family review at `6cb38bb50889311c013f8c75e2fb8b26caf3a37f`, and
  its decision at `740effa34b9f201e06348f264337899bb4293157`, all
  committed before this stage wrote anything. No file of the v1 bundle
  `probes/046/results/results_v2/` was modified by the run or by this
  stage; the executed run additionally proved lineage continuity through
  the contract-mandated guard comparison (Layer B).
- **Out-of-scope warnings — this result must NOT be read as:**
  - a diffuse-versus-concentrated classification of the cohort or
    population, in any wording — the contract defines no such verdict and
    prohibits converting the frozen summaries into one;
  - a stable-carrier, patient-subtype, biological, clinical, causal,
    predictive, treatment, or model-use claim about any named case;
  - a claim that any case's contribution rank would recur under repeat
    measurement — the debate established that this dataset contains no
    replication unit for that question;
  - anything about idea-023's scientific interpretation beyond the exact
    arithmetic decomposition of its frozen estimator;
  - a population claim beyond these 99 observed cases, this frozen
    estimator, and this exact input table;
  - authorization for the optional clinical rung (phenotype join), which
    remains behind its own future contract and approval.

## Layer A — Finding

The frozen census completed (`CENSUS_COMPLETE`) and exactly accounts for
the realized band-3-minus-band-2 mean contrast of +0.0550774: the 99
signed per-case contributions reconstruct it with an additive residual of
6.94e-18 against the 1e-12 tolerance. The largest single contribution,
case sub-stroke0153, supplies 12.97% of the net gap; the five largest
supply 48.16%, the ten largest 79.29%, and the twenty largest 109.51% —
more than 100% because the remaining 79 cases sum to a net negative.
Of the 99 cases, 54 contribute positively (total +0.070661), 39
negatively (total −0.015584, canceling the positive mass down to the
net), and 6 contribute exactly zero; among the positive cases, the 8
largest reach 53.05% of positive mass and the 17 largest reach 80.76%.
By absolute contribution mass the largest case holds 8.28%, the ten
largest 50.64%, and the twenty largest 73.35%.
These are exact finite-population facts about this one realized
estimator — the single most important caveat is that, by contract, they
carry no diffuse-versus-concentrated verdict, no stable-carrier or
clinical reading, and no generalization beyond these 99 cases.

## Layer B — Derivation narrative

**Gates before execution.** The candidate reached this probe through: the
completed v1 definition audit (status `FEASIBLE_DEFINITION_AUDIT`,
interpretation cross-family APPROVED round 1, decision ADVANCE whose sole
authorized consequence was drafting this census contract); contract v2
drafting; fresh human approval at 2026-09-01T22:37:49Z binding blob
`942e530737c90b666baa4c9985fd0329296ef140`
(`ideas/046/HUMAN_APPROVED_PROBE`; the in-file `human_approved: false`
line is the standing marker-file convention). Probe code was built
cross-family: round-1 review (claude) returned REVISE on exactly one
blocking finding — the contract-mandated v1 lineage-guard comparison was
absent — and round 2 verified it closed exactly as specified and returned
APPROVE with no scope expansion. The harness verification passed
(`probes/046/verification.json`, `passed: true`, 2026-09-01T22:53:16Z),
following the round-2 review's attestation of the re-run smoke.

**The run (single authorized variant).** One real variant executed
(`variants: 1, gpu_minutes: 0, smoke: false`
[cite: resolved_config.json | top-level | variants, gpu_minutes, smoke])
under contract version 2 [cite: resolved_config.json | top-level |
contract_version], Python-stdlib-only environment
[cite: environment.txt | top-level | dependencies]. The declared seed
(20260901) exists for harness reproducibility only; the analysis consumes
no randomness. Order of operations as the contract requires: the
anonymous split manifest was frozen and hashed before the input CSV was
first opened [cite: split_manifest.json | top-level |
created_before_measurement, sha256], then the input identity gate passed
against the approved SHA-256
[cite: determinism_manifest_start.json | top-level | input_sha256].

**CONSORT-style flow.** In: 297 data rows, 99 unique cases
[cite: input_manifest.csv | input=per_patient.csv | rows, cases].
Excluded: 99 rows, all with reason `non_primary_band` — the band-1 rows,
source lines 2–296 [cite: exclusions.csv | reason=non_primary_band | all
99 data rows] ([cite: summary.json | top-level | excluded_rows]).
Analyzed: 198 rows forming 99 paired cases with identical band-2 and
band-3 case sets and unique keys (cohort gate; reflected in
[cite: summary.json | top-level | paired_cases]). Emitted: 99 per-case
contributions [cite: summary.json | top-level | per_case_outputs], a
99-row signed cumulative curve, a 100-row absolute Lorenz curve with
explicit endpoints, and a 54-row positive-mass curve
[cite: summary.json | top-level | signed_curve_rows,
absolute_lorenz_rows, positive_mass_rows]. Reserved cases accessed: 0
[cite: summary.json | top-level | reserved_cases_accessed].

**Lineage guard (contract `baselines[0]`).** After the census was
recomputed and before any status was written, the run compared its own
recomputed guard values against the frozen v1 definition-audit values:
status `MATCHED_V1_DEFINITION_AUDIT`, `compared: true`, tie counts
compared in delta space (`delta_before_division_by_99`), with observed
equal to expected on every guard — residual, paired cases, denominators
defined, deterministic orderings, sign counts 54/6/39, tie counts 5/5
[cite: census_summary.json | v1_lineage_guard_comparison | status,
compared, tie_count_space, observed, expected]. The invalidating lineage
class ("repeated v1 guard values disagree") did not fire.

**Measurement and close-out.** The additive-identity guard passed
(residual 6.938893903907228e-18 ≤ 1e-12
[cite: census_summary.json | top-level | additive_identity_residual,
additive_identity_within_1e-12]); all three denominators are finite and
nonzero [cite: census_summary.json | denominators | signed_net,
positive_mass, absolute_mass]; the status classifier selected the
contract's positive pattern [cite: summary.json | top-level | status] and
the primary metric passed [cite: summary.json | top-level |
primary_metric_pass]. Start and end determinism manifests are
byte-identical (verified by diff during this interpretation). All 14
contract-required outputs are present; the fifteenth bundle file
(`split_manifest.csv`) is the permitted anonymous-split extra. The
5-minute wall cap was enforced in-code and not exceeded (the run
completed with status and all outputs). No output or log line converts
the summaries into a classification; the run log's plain-language
template states the descriptive register verbatim.

**Import.** The bundle was imported through record-result's local lane
(`source_commit: null`, first-add ancestry;
[cite: ../results_v3.import.json | top-level | source_commit]) with 15
files [cite: ../results_v3.import.json | top-level | file_count],
validated under the contract-declared interface (summary `phase` absent,
tolerated per S2b), and the transactional tail recorded the PROBED
scrutiny event, digest, and re-materialized state at commit `0d36ee0`.

**Kill conditions approached: none.** No invalidating-failure class
(authority, input-identity, cohort, lineage, algebra/definition,
scope/leakage, analysis deviation, selective-output, output/provenance)
occurred or was neared. The contract defines no directional negative
pattern, and none is claimed.

## Layer C — Deep justification (claims table)

Bundle root: `probes/046/results/results_v3` at commit
`30c360113e669542397288437a8690a561f40eb1`. Every quantitative claim in
this document resolves to one of these rows, or is explicitly labeled as
derived from two cited values.

| # | Claim | Value | Citation |
|---|-------|-------|----------|
| 1 | Status is the contract's positive pattern | `CENSUS_COMPLETE` | [cite: summary.json \| top-level \| status] |
| 2 | Primary metric name | `complete_finite_population_contribution_accounting` | [cite: summary.json \| top-level \| primary_metric_name] |
| 3 | Primary metric passed | `true` | [cite: summary.json \| top-level \| primary_metric_pass] |
| 4 | Additive-identity residual | 6.938893903907228e-18 | [cite: census_summary.json \| top-level \| additive_identity_residual] |
| 5 | Residual within 1e-12 | `true` | [cite: census_summary.json \| top-level \| additive_identity_within_1e-12] |
| 6 | Direct band gap (mean d band 3 − mean d band 2) | 0.0550773631700778 | [cite: census_summary.json \| top-level \| direct_band_gap] |
| 7 | Net contribution (stable sum of all c_i) | 0.055077363170077796 | [cite: census_summary.json \| top-level \| net_contribution] |
| 8 | Signed-net denominator | 0.055077363170077796 | [cite: census_summary.json \| denominators \| signed_net] |
| 9 | Positive-mass denominator | 0.0706613032599503 | [cite: census_summary.json \| denominators \| positive_mass] |
| 10 | Absolute-mass denominator | 0.08624524334982282 | [cite: census_summary.json \| denominators \| absolute_mass] |
| 11 | Negative contribution total (derived: claim 8 − claim 9, sign reversed) | −0.015583940089872504 | derived from [cite: census_summary.json \| denominators \| signed_net, positive_mass] |
| 12 | Sign counts of contributions | positive 54, zero 6, negative 39 | [cite: census_summary.json \| sign_counts \| positive, zero, negative] |
| 13 | Exact-tie counts (delta space) | signed 5, absolute 5 | [cite: census_summary.json \| tie_counts \| signed, absolute] |
| 14 | Top-1 signed-head net-gap share | 0.12966704886255284 | [cite: census_summary.json \| top_k 1 \| signed_head_net_gap_share] |
| 15 | Top-5 signed-head net-gap share | 0.48163202301973784 | [cite: census_summary.json \| top_k 5 \| signed_head_net_gap_share] |
| 16 | Top-10 signed-head net-gap share | 0.7928912778985707 | [cite: census_summary.json \| top_k 10 \| signed_head_net_gap_share] |
| 17 | Top-20 signed-head net-gap share | 1.0951142730999406 | [cite: census_summary.json \| top_k 20 \| signed_head_net_gap_share] |
| 18 | Top-1 absolute-mass share | 0.08280710754594581 | [cite: census_summary.json \| top_k 1 \| absolute_mass_share] |
| 19 | Top-5 absolute-mass share | 0.3075766362974946 | [cite: census_summary.json \| top_k 5 \| absolute_mass_share] |
| 20 | Top-10 absolute-mass share | 0.5063509495830807 | [cite: census_summary.json \| top_k 10 \| absolute_mass_share] |
| 21 | Top-20 absolute-mass share | 0.7335301076368037 | [cite: census_summary.json \| top_k 20 \| absolute_mass_share] |
| 22 | Smallest positive prefix reaching 50% of positive mass | k = 8, achieved share 0.5305392350631275 | [cite: census_summary.json \| positive_mass_crossings 0.5 \| smallest_k, achieved_share] |
| 23 | Smallest positive prefix reaching 80% of positive mass | k = 17, achieved share 0.8076125481655062 | [cite: census_summary.json \| positive_mass_crossings 0.8 \| smallest_k, achieved_share] |
| 24 | Largest signed contribution | sub-stroke0153, c = 0.007141719141395045, rank 1 | [cite: per_case_contributions.csv \| case_id=sub-stroke0153 \| contribution, signed_rank] |
| 25 | Second and third largest | sub-stroke0002 c = 0.005930555633540115 (cumulative net fraction 0.2373438745527493); sub-stroke0166 c = 0.004849834482535765 (cumulative 0.3253988249605888) | [cite: per_case_contributions.csv \| case_id=sub-stroke0002, sub-stroke0166 \| contribution]; [cite: signed_cumulative_curve.csv \| rank=2, rank=3 \| signed_fraction_of_net] |
| 26 | Ten largest signed contributors, in rank order | sub-stroke0153, 0002, 0166, 0181, 0014, 0098, 0090, 0114, 0025, 0136 | [cite: per_case_contributions.csv \| signed_rank=1..10 \| case_id] |
| 27 | Two most negative contributions | sub-stroke0137 c = −0.0029141878799591753 (rank 99); sub-stroke0183 c = −0.002031107751158429 (rank 98) | [cite: per_case_contributions.csv \| case_id=sub-stroke0137, sub-stroke0183 \| contribution, signed_rank] |
| 28 | Six exact-zero contributions, each with d_band2 = 0.0 and d_band3 = 0.0 | sub-stroke0094, 0141, 0142, 0147, 0163, 0175 (signed ranks 55–60) | [cite: per_case_contributions.csv \| case_id=sub-stroke0094, sub-stroke0141, sub-stroke0142, sub-stroke0147, sub-stroke0163, sub-stroke0175 \| d_band2, d_band3, contribution] |
| 29 | Peak signed cumulative fraction (after the last positive case) | 1.282946372028552 at rank 54 (case sub-stroke0079), flat through the zero block (ranks 55–60) | [cite: signed_cumulative_curve.csv \| rank=54 \| signed_cumulative, signed_fraction_of_net] |
| 30 | Signed curve terminal values | rank 99 cumulative 0.055077363170077796, fraction 1.0 | [cite: signed_cumulative_curve.csv \| rank=99 \| signed_cumulative, signed_fraction_of_net] |
| 31 | Lorenz endpoints present | (0.0, 0.0) at rank 0; (1.0, 1.0) at rank 99 | [cite: absolute_lorenz_curve.csv \| rank=0, rank=99 \| population_fraction, absolute_share] |
| 32 | Positive-mass curve terminal | rank 54 (sub-stroke0079), share 1.0 | [cite: positive_mass_curve.csv \| rank=54 \| case_id, positive_mass_share] |
| 33 | v1 lineage guard comparison | `MATCHED_V1_DEFINITION_AUDIT`, compared true, tie space `delta_before_division_by_99`, observed = expected on all guards | [cite: census_summary.json \| v1_lineage_guard_comparison \| status, compared, tie_count_space] |
| 34 | Input identity | SHA-256 `1d01551c888d77b6382f7cbe36e4bb68a6d2f2ef4b26e09832bfda45d2c40e0c` | [cite: resolved_config.json \| top-level \| input_sha256]; identically in [cite: input_manifest.csv \| input=per_patient.csv \| sha256] |
| 35 | Input size | 297 rows, 99 cases | [cite: input_manifest.csv \| input=per_patient.csv \| rows, cases] |
| 36 | Rows excluded (band 1) | 99, all `non_primary_band` | [cite: summary.json \| top-level \| excluded_rows]; [cite: exclusions.csv \| reason=non_primary_band \| all 99 data rows] |
| 37 | Reserved cases accessed | 0 | [cite: summary.json \| top-level \| reserved_cases_accessed]; [cite: split_manifest.json \| top-level \| reserved_cases_accessed] |
| 38 | Split frozen before measurement, 99 opened-census slots, hashed | `true`, 99, SHA-256 `532b1060662957c88712e3fbc2f7f81bbcc427b2b6229827cac0939872a764cf` | [cite: split_manifest.json \| top-level \| created_before_measurement, opened_census_cases, sha256] |
| 39 | Governing contract blob and version recorded by the run | `942e530737c90b666baa4c9985fd0329296ef140`, version 2 | [cite: resolved_config.json \| top-level \| contract_blob, contract_version] |
| 40 | Caps honored | variants 1, gpu_minutes 0, smoke false | [cite: resolved_config.json \| top-level \| variants, gpu_minutes, smoke] |
| 41 | Determinism manifests identical | start = end (byte-identical) | [cite: determinism_manifest_start.json \| top-level \| all keys] vs [cite: determinism_manifest_end.json \| top-level \| all keys] |
| 42 | Import identity | 15 files, manifest SHA-256 `997914ac477909b4077c2fd0a18d3fbea3054e7df0cd058344422527aededd60`, 2026-09-01T22:53:56Z, source_commit null | [cite: ../results_v3.import.json \| top-level \| file_count, manifest_sha256, imported_utc, source_commit] |

Repo-level (non-bundle) anchors: approval timestamp and blob —
`ideas/046/HUMAN_APPROVED_PROBE`; harness verification —
`probes/046/verification.json` (`passed: true`, 2026-09-01T22:53:16Z);
bundle commit — `30c3601`; record-result transaction commit — `0d36ee0`;
v1 artifacts — blobs listed in the Result card's file-lineage note.

Derived-value discipline: claims 11 and the "remaining 79 cases sum to a
net negative" gloss (1 − 1.0951142730999406 = −0.0951142730999406 of the
net gap, i.e. about −0.005238 in absolute contribution) are arithmetic on
cited values (claims 8, 9, 17) and are labeled as such wherever used.
Percentages in prose are the cited fractions rounded to two decimals.

## Demonstrates

The procedure is deterministic and randomness-free (the declared seed is
unused), and the claim scope is the fully enumerated finite population
itself, so the seed rule does not apply and no sampling uncertainty
machinery is owed: within the stated scope — this realized estimator on
these 99 cases — the following are exact facts, not estimates. Their
hard boundary is that scope; nothing here extends to repeatability,
population structure, or any other dataset.

1. **The census is complete and exact.** All 99 signed contributions
   were emitted and reconstruct the realized band-3-minus-band-2 mean
   contrast of +0.0550774 with residual 6.938893903907228e-18 against
   the 1e-12 tolerance (claims 4–7, 30). No selective-output failure:
   every case, every curve coordinate, and every frozen summary is
   present (claims 1, 3, 31–32, 35–36).
2. **Exact share accounting of the realized net gap.** The single
   largest contribution (sub-stroke0153) accounts for 12.97% of the net
   gap; the five largest for 48.16%; the ten largest (claim 26 names
   them) for 79.29%; the twenty largest for 109.51% (claims 14–17, 24,
   26). The top-20 share exceeds 1 because the remaining 79 cases sum to
   a net negative (derived from claim 17, labeled above) — the signed
   fraction is defined on net contributions and is not a Lorenz share.
3. **Exact positive/negative/zero structure.** 54 cases contribute
   positively (total +0.070661), 39 negatively (total −0.015584,
   derived claim 11), 6 exactly zero (claims 9, 11, 12). The positive
   mass equals 1.28295 of the net gap at its peak (claim 29); the 8
   largest positive contributions reach 53.05% of positive mass and the
   17 largest reach 80.76% (claims 22–23).
4. **Exact absolute-mass accounting.** By absolute contribution mass the
   largest case holds 8.28%, the five largest 30.76%, the ten largest
   50.64%, and the twenty largest 73.35% (claims 18–21).
5. **The two largest opposing contributions are named.** sub-stroke0137
   (−0.0029142) and sub-stroke0183 (−0.0020311) are the most negative
   contributions (claim 27).
6. **Lineage continuity with v1 is proven, not assumed.** The run
   recomputed the v1 guard set and matched it exactly — residual
   bit-identical, sign counts 54/6/39, delta-space tie counts 5/5,
   99 paired cases, denominators defined, orderings deterministic
   (claims 12–13, 33).
7. **Discipline held.** Input identity exact, split frozen and hashed
   before the input was opened, zero reserved-case contact, one variant,
   zero GPU, determinism manifests byte-identical, all 14 required
   outputs plus the permitted split CSV (claims 34–42).

## Suggests

Each item below is a labeled post-hoc observation read from the emitted
artifacts — not a frozen summary of the contract — recorded for the
operator and any successor design. None may be extended into carrier,
subtype, stability, or population language.

1. **The head cases individually mirror the aggregate reversal.** Among
   the ten largest signed contributors (claim 26), all ten have negative
   band-2 d values and nine of ten have positive band-3 d values (the
   exception is sub-stroke0114, band-3 d = −0.04584335824840224)
   [cite: per_case_contributions.csv | signed_rank=1..10 | d_band2,
   d_band3]. A large positive contribution is, by construction,
   `d_band3 − d_band2 > 0`; the observation that the head achieves this
   mostly by pairing a negative band-2 value with a positive band-3
   value — rather than by moving within one sign — is a structural fact
   of this table only.
2. **The six zero contributions are zeros in both operands.** All six
   zero-contribution cases have d_band2 = 0.0 and d_band3 = 0.0 exactly
   (claim 28) — sharpening the v1 interpretation's inference (which
   could establish only that the operands were numerically equal). Why
   those six d values are exactly zero is not recorded in this bundle;
   it belongs to the parent take-13 artifacts, and any successor
   touching these cases should consult them there.
3. **The tiebreak arbitrated only the zero block.** The 5/5 delta-space
   tie counts (claim 13) together with the six both-band zeros mean the
   case_id tiebreak decided order only within signed ranks 55–60
   (claim 29's flat segment); every nonzero contribution has a unique
   value and magnitude in this table.

## Does not establish

- Whether the realized pattern should be called diffuse or concentrated,
  in any register — the contract defines no such classification and
  prohibits deriving one from these summaries.
- That any named case is a stable carrier, a repeatable high-contribution
  patient, a biological subtype, or a clinically distinct group; rank
  stability under repeat measurement has no replication unit in this
  dataset (the debate's converged finding).
- Any biological, clinical, causal, predictive, treatment, or model-use
  reading of contribution rank; any clinical difference between rank
  strata (the optional clinical rung was not run and is separately
  gated).
- Anything about idea-023's finding beyond the exact arithmetic
  decomposition of its frozen estimator; individual d values are taken
  as given from the parent bundle and are not explained here.
- Phenotype content-level completeness (populated NIHSS/mRS values for
  the 99 cases) — untouched by this probe.
- Transport beyond this exact table, this frozen estimator, and these 99
  observed cases.

## Validity failures

None. Walking the contract's invalidating-failure classes: authority
verified (fresh marker binding the exact v2 blob before execution);
input identity exact (claim 34); cohort gate clean (99 paired cases,
identical band sets, unique keys, claims 35–36); lineage intact (v1
bundle untouched; guard comparison MATCHED, claim 33); algebra and
definitions within tolerance with all denominators nonzero and orderings
unique (claims 4–5, 8–10, 13); no scope/leakage contact (no phenotype,
reserved-case, image, voxel, or cache read; claim 37); no analysis
deviation (one variant, frozen formulas, no randomness consumed, claim
40); no selective-output failure (all 99 cases and every frozen summary
emitted, claims 1, 30–32); all required outputs present with provenance
(claims 39–42). No run was invalidated and no result was reinterpreted.

## Positive and negative findings

- **Positive finding:** `CENSUS_COMPLETE` (claim 1) — the contract's
  positive pattern, which is a successful *descriptive* result
  regardless of curve shape and carries no directional or binary
  scientific label. The instantiated deliverable sentence, in the
  contract's permitted form: in the realized 99-case estimator, the ten
  largest signed contributions — sub-stroke0153, 0002, 0166, 0181,
  0014, 0098, 0090, 0114, 0025, 0136 — account for 79.29% of the net
  band-3-minus-band-2 contrast, and the single largest for 12.97%
  (claims 14, 16, 26).
- **Negative findings:** none, by construction — the contract defines no
  directional negative pattern, and no undefined summary, identity
  mismatch, or incomplete output occurred.

## Authorized variants (complete report)

The contract caps `maximum_variants: 1`. Exactly one real variant was
executed and is reported above (claims 1, 40). Additionally, the
probe-build harness smoke ran on synthetic input during verification
(status `SMOKE_ONLY`, attested via `probes/046/verification.json`); it is
not a contract variant, satisfies no contractual pattern by construction,
skips the lineage comparison visibly, and touched no real data. No other
execution of this probe exists.

## Next decision

**ADVANCE**, with narrow semantics: the idea's primary rung is now
delivered — the frozen census exists, is exact, and is imported under
the record-result gate — and no further computation is authorized under
this contract. Concretely, in order:

1. Cross-family review of this interpretation (codex, round 1), then
   operator ratification via `ratify-interpretation`.
2. At ratification, the operator chooses the ledger transition. The
   recommendation of this interpretation is **PAUSED**: the primary
   deliverable is complete and positive; the only remaining card scope —
   the optional clinical rung (phenotype join under the D3
   read-restriction and D4 joint-display rules) — is explicitly
   opportunistic on the next archive staging event and warrants no
   active work now.
3. Per the 2026-09-01 registry rollout rule, author
   `ideas/046/registry.yaml` covering both executed nodes — the v1
   definition audit (blob `3996009b…`, bundle results_v2) and this v2
   census (blob `942e5307…`, bundle results_v3) — and ratify it
   (`ratify-registry 46 --operator …`).
4. Any future stability, carrier, clinical, or model-use question about
   these cases enters as a separately registered successor with its own
   replication unit, citing this census and the idea-046 debate as
   motivation.
