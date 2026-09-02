# Revision — idea 047 (post-critique, post-debate, post-ruling)

Revised 2026-09-02 in response to `critique.md` (six decisive defects
D1–D6), the three-round debate (`debate.md`, `consensus.md`, verdict
REVISE), and the operator ruling recorded in
`ideas/047/unblock_ack.txt`, which resolved the debate's single open
code question:

> ruling: S_i in the frozen take-13 table is per-band quartile-cell
> voxel counts (q1_voxels plus q4_voxels), not total eligible support;
> freeze the exact-map recomputation branch: eroded Tmax>6s deficit
> voxel count per case from the held maps under the ratified take-13
> parameters. Adopt the round-3 finite-population design.

The revision narrows the card to one clean compound question (the same
two clauses the debate ruled identity-preserving), removes every piece
of architecture the gauntlet invalidated, and preserves a meaningful
negative outcome in both clauses.

## Material changes

### 1. The support variable: exact-map branch frozen (operator ruling; debate round 1)

- The round-1 `S_i` proxy (sum of q1+q4 quartile-cell counts) is
  **removed entirely** — not demoted to sensitivity display. The ruling
  establishes it is not total eligible support, so retaining it would
  reintroduce a discredited measure.
- The frozen burden variable is now `B_i` = exact eligible deficit
  support: the voxel count of the take-13 eligible analysis region
  (eroded Tmax>6s deficit under the ratified take-13 parameters,
  including the frozen midline-band, per-patient p98 vessel-exclusion,
  and finiteness rules), recomputed label-blind from the held maps.
- **New reproducibility gate** (answers critique D3's "reproducibility
  comparison against cached case counts"): before any `B_i` is used,
  the re-run region machinery must reproduce all 297 cached per-band
  `q1_voxels`/`q4_voxels` values in
  `probes/023/results/results_v2/per_patient.csv` exactly. A mismatch
  stops the support clause for escalation; no variant region may be
  silently substituted.

### 2. Burden-disproportionality currency (debate rounds 2–3)

- The random-10-subset permutation null and permutation intervals are
  **removed** (round-2 concession: the head is outcome-selected and
  nonexchangeable; the statistic partly rewards its own selection
  rule). No permutation machinery exists anywhere in the support
  clause.
- The **sole** disproportionality comparison is
  `sum_head |c_i| / sum_all |c_i|` beside
  `sum_head B_i / sum_all B_i` (round-3 freeze, adopted verbatim).
- The 79.29% net signed share is **demoted to separately labeled
  reversal accounting** with a frozen prohibition: neither it nor its
  difference from the support share may be read as contribution per
  unit support or as evidence of keystone-like dominance.
- The casewise `rank(|c_i|) − rank(B_i)` distribution (head's ten
  marked) and Spearman rho remain as descriptive displays only.
- The whole clause is finite-population arithmetic about the realized
  99 cases: no sampling story, no generalization, no is/is-not
  threshold language.

### 3. Residual subgroup and keystone endpoint removed (critique D2)

- "Residual of |c_i| on burden" and the "disproportionality
  top-decile" group are **deleted**. No fitted quantity, no
  analyst-defined subgroup, no leverage/functional-form discretion
  survives anywhere in the design.
- The borrowed ecological construct is demoted from endpoint to
  motivation; "keystone" is never a verdict, and "disproportionate" is
  licensed only as a comparison of the two exact shares.

### 4. Clinical clause: dictionary-first freeze and forward correction (critique D1, D5, D6)

- **D1:** the card no longer treats admission NIHSS as interchangeable
  with the lineage's frozen "NIHSS at 24 hours." The dictionary-only
  read of `clinical_data-description.xlsx` freezes exact field names,
  time points, coding, and missingness rules; if the release lacks a
  24-hour field, admission NIHSS enters as a documented forward
  correction, not as execution of idea-046's frozen list.
- **D5/D6:** the conditional "treatment fields if present" discretion
  is removed. At most three contextual fields may be predeclared at
  the dictionary step — one decision, made once, before any case row.
  Per-variable contrast statistics are also frozen at that step.
- The primary clinical deliverable is an **estimation table**: group
  distributions, standardized contrasts with exploratory-labeled
  uncertainty (descriptive calibration for the realized cohort, never
  sampling inference), and missingness; every row reported jointly; no
  significance-selected headline; small cells suppressed. The binary
  "does / does not differ" packaging is gone.

### 5. "Clinically silent" dichotomy removed throughout (critique D4 + plain-pitch defect)

- Title, question, deliverable sentence, audience_relevance,
  negative-result rationale, and plain pitch no longer contain
  "clinically silent," "clinically marked," or the exhaustive
  clinical-versus-imaging-geometry alternatives. The clinical null is
  reframed as bounded: the table reports how much separation a
  10-versus-89 comparison could have excluded.
- New title: "The keystone ten meet the clinic: aggregate clinical
  profile and support-share arithmetic of the census head."

### 6. Honest cost (critique D3)

- The "~50 kB, under five minutes" envelope is replaced: one
  selective-extraction staging event against the held md5-verified
  ~99 GB archive (the same event D3 phenotype staging requires),
  ~3 GB of maps (396 files), a CPU-only 99-case region pass, then
  minutes of table arithmetic. First result in days, not minutes.
  Feasibility and prior-legwork scores lowered accordingly.

### 7. New verification performed at this revision

- **Map coverage for the frozen exact-map branch** (now load-bearing):
  unique-case joins of the md5-verified archive manifest
  (`origin/results/probe-023-349af5ad0b3e:probes/023/results_v2/archive_manifest.csv`)
  against the 99 census ids give **99/99 for each of tmax, cbf, cbv,
  mtt, and the rawdata NCCT**. Verbatim row:
  `train/derivatives/sub-stroke0001/ses-01/perfusion-maps/sub-stroke0001_ses-01_space-ncct_tmax.nii.gz,6580435,bf32937b`.
  The one known source-defective member (sub-stroke0043 ses-01 cbf)
  belongs to a case already excluded from the 99. Keystone
  prerequisite (3) added and marked inspected on this evidence;
  `keystone_status` remains INSPECTED_TRUE.
- **The head's absolute-contribution share already exists in the
  ratified census**: `census_summary.json` `top_k.10.absolute_mass_share`
  = 0.5063509495830807. This is valid for the *signed-rank* head
  because the signed and absolute top-ten sets coincide: the largest
  negative magnitude (0.0029141878799591753) is smaller than the
  tenth-largest positive contribution (0.002976074880714717)
  (sorted-column check on `per_case_contributions.csv`, 2026-09-02).
  Round 3's predicted deflation is therefore already a fact of record:
  the honest share is 50.64%, against the 79.29% signed accounting
  figure. Only the support side of the comparison awaits computation.

### 8. Score changes

| dimension | before | after | why |
|---|---|---|---|
| feasibility | 5 | 4 | honest end-to-end envelope (staging event + map pass), per D3 |
| prior_legwork | 5 | 4 | the support table must be recomputed, not read |
| evaluation_readiness | 2 | 3 | support clause is exact arithmetic needing no custom metric |
| clarity | 4 | 4 | why updated: conditional treatment arm gone; residual openness is only the dictionary step |
| negative_result_value | 3 | 3 | why rewritten: support clause decisive at scope; clinical null bounded, never "silent" |

All other values unchanged; every `why` rewritten to match the revised
design.

## What is lost (stated plainly, from the debate's own accounting)

- The dramatic 79.29% figure can name the head but no longer judge it;
  the honest currency (50.64% absolute share) is known to be less
  striking.
- Any claim that the proportionality pattern or clinical profile would
  recur in new cases: the answer is a fact about the realized 99 and
  nothing more; a generalizing version requires a sampled cohort with
  unopened outcomes and would be a successor candidate.
- The phrase "deficit burden" for the support variable: `B_i` is
  estimator-eligible support (the take-13 analysis region), a subset
  of gross lesion burden, and the writeup must say so.
- The low-cost table-only path: ruled out by the operator's code
  inspection; the study pays for map restaging.
- The residual asymmetry is acknowledged: the clinical clause retains
  exploratory-labeled uncertainty displays (per D6) while the support
  clause has none; the writeup must not let clinical p-values imply an
  inferential license the support clause honestly refused.

## Claim retention

The original deliverable (ledger `deliverable_original`) asked, for the
same frozen 99-case cohort and the same frozen high-contribution
stratum, (i) whether the stratum differs in aggregate on released
clinical variables and (ii) whether its dominance is accounted for by
deficit burden, as an exploratory aggregate-only association-register
description under D3/D4. The revised deliverable answers exactly those
two clauses for exactly that cohort and stratum, with: binary
"does / does not" packaging replaced by estimation displays and exact
finite-population shares; "deficit burden" narrowed to the operational
eligible-deficit-support variable the ruling froze; the conditional
treatment arm replaced by a bounded dictionary-step predeclaration; and
generalization beyond the 99 explicitly renounced. Both debate identity
checks (rounds 2 and 3) found these repairs identity-preserving, the
operator ruling adopted the round-3 design, and per the standing
precedent (ideas 045 and 046 rulings) a card is not re-registered for
becoming more modest. This is a narrowing of the same claim.

```json
{"claim_retention": "narrowed"}
```
