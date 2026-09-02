# Feasibility memo — idea 047

**Idea:** Aggregate clinical profile and support-share arithmetic of the frozen
idea-046 top ten.  
**Stage:** feasibility. **Date:** 2026-09-02.  
**Verdict:** **REVISE** — feasible after a material simplification; do not
approve the current draft contract.

This memo evaluates the post-debate, post-ruling card. Labels distinguish
directly verified facts, source-supported interpretations, and unresolved
assumptions. No phenotype row, lesion mask, or reserved case was opened during
this stage.

## 1. Decisive repository finding

**Verified fact:** the proposed support variable already exists in the
ratified take-13 bundle. `probes/023/results/results_v2/exclusions.csv`
(SHA-256
`58e9f8ab7cea38e6717319a26ea6a590dc7d1ad0d42d6b30dca648b0509a5a71`)
contains 99 `analyzed_case` rows, one for every case in the frozen idea-046
contribution table, and a populated integer `eroded_region_voxels` value for
each. The frozen take-13 code defines that field at `coordinate_arrays()` as
the eligible region after Tmax > 6 s thresholding, six-neighbor one-voxel
erosion, array-midline exclusion, per-patient CBV-p98 vessel exclusion, and
map finiteness/positivity filtering. This is exactly the card's `B_i`, not the
rejected q1+q4 proxy.

The extra manifest row for `sub-stroke0142` is explicitly an
`excluded_archive_lesion` bookkeeping row with blank support fields; filtering
on `record_type == analyzed_case` yields the unambiguous 99-row one-to-one
join. The contribution-table and census-summary hashes also reproduce their
contract pins.

**Consequence:** Phase A as drafted would selectively extract 693 archive
members, stage about 3 GB of maps, and rerun 99 cases merely to recreate an
already imported claim-bearing output. That is unnecessary and creates new
environment, extraction, and transcription failure surfaces. It also conflicts
with the collaborator rule to prefer the smallest decisive experiment. The
operator's ruling correctly rejected q1+q4 as total support; it did not make
the already recorded exact `eroded_region_voxels` invalid. Because the current
contract explicitly freezes map recomputation, changing this requires a
reviewed contract revision, not an informal execution choice.

## 2. Dataset, access, license, modalities, and labels

**Verified from the official Zenodo API for immutable record 16813698 on
2026-09-02:** `train.7z` is 99,014,629,647 bytes with MD5
`36ae28b9a17f7340b8bbef62b595cb57`; `clinical_data-description.xlsx` is
12,149 bytes with MD5 `c8d806a021614c6bb9f732756f9701d4`; the license is
CC BY-NC-SA 4.0. The record is openly retrievable without a DUA or account.
The held archive has already passed the same archive MD5 in the parent work.
Any released derivative must respect the noncommercial/share-alike terms.

**Verified from the official dataset paper** (Riedel et al., Radiology:
Artificial Intelligence, DOI `10.1148/ryai.250603`) and challenge report
(de la Rosa et al., arXiv `2408.10966`): ISLES'24 contains acute NCCT, CTA,
4-D CTP and derived perfusion maps, subacute follow-up MRI at 2–9 days, and
longitudinal clinical data. The published dataset comprises 245 cases across
two centers (149 released training cases and 96 held-out cases in the final
paper); earlier challenge documents state approximately 150/100, so payload
counts, not early prose, govern this study. Final-infarct delineations are
derived from follow-up MRI with automated segmentation and expert quality
control. The official challenge evaluates final-infarct segmentation with
Dice and absolute volume difference using case-level rank aggregation.

Those segmentation labels and official metrics are contextual here, not this
study's outcomes. **Source-supported interpretation:** the parent `c_i` values
are outcome-derived because idea 023 used the follow-up-infarct masks, but idea
047 neither rereads nor revalidates those masks. Its clinical variables are
released measurements, not new annotations. Consequently there is no fresh
annotation burden, but the analysis is necessarily exploratory and cannot be
an independent validation of the outcome-derived head.

## 3. Clinical schema and label availability

The official `clinical_data-description.xlsx` was downloaded by immutable
record-file URL and checksum-verified during this stage; only this dictionary
was read. **Verified fields** include `Age`, `Sex`, `NIHSS at admission`,
`NIHSS 24h`, `NIHSS discharge`, `MRS 3 months`, and `mTici
postinterventional`, with descriptions and data types. This resolves the
card's time-point uncertainty: the release documents both admission and 24-hour
NIHSS, so the lineage's 24-hour field need not be replaced by admission NIHSS.

The archive manifest contains one baseline-demographic and one outcome CSV for
each of the 149 released cases, with 99/99 file-level coverage of the analyzed
cohort. **Not verified by design:** case-row column spellings, actual
missingness, usable n per field, or whether all dictionary fields are populated
for these cases. Those facts require the D3-restricted phenotype read. The
dataset paper explicitly reports smaller denominators for some clinical
variables, so missingness is expected rather than hypothetical.

The minimum clinical schema gate in the draft contract therefore passes at the
documentation level. It does not establish statistical sensitivity in a
10-versus-89 comparison.

## 4. Sample structure and split unit

The analysis unit is the patient/case. The frozen table has 99 unique cases;
the head is the already ratified signed-rank 1–10 group and the comparison is
the remaining 89. No voxel may be treated as an independent clinical sample.
The 49 non-analyzed released cases remain an untouched reserve and are outside
this candidate; `sub-stroke0043` is already excluded for its documented corrupt
CBF member.

No train/validation/test split can make this confirmatory: the 99 imaging
outcomes were opened in idea 023 and the subgroup was selected from their
realized contributions. Freezing the phenotype analysis before the first
clinical-row read prevents analyst adaptation but does not undo this outcome
selection. Results are finite-population descriptions of these 99 cases only.

## 5. Closest work and exact gap

- **Closest clinical/perfusion error study:** Broocks et al., Radiology 2024,
  DOI `10.1148/radiol.231750`, PMID `39078297`, analyzed 721 thrombectomy
  patients and associated CTP core overestimation with baseline core volume and
  reperfusion. It clinically profiles threshold error, but not a frozen
  per-case contribution head from an ISLES'24 band estimator.
- **Closest ISLES'24 clinical secondary analysis found:** “Infarct-volume
  prognostic value depends on outcome ascertainment and validation design in
  public stroke MRI datasets,” European Journal of Radiology (online 2026),
  DOI `10.1016/j.ejrad.2026.113200`, uses ISLES'24 mRS and explicitly audits
  center and outcome-availability effects. This materially narrows the claimed
  gap: joining ISLES'24 imaging summaries to clinical outcomes is no longer an
  unpublished category. Its estimand is incremental prognostic value of infarct
  volume under center-held-out validation, not clinical description of the
  frozen idea-046 contribution head or absolute-contribution-share versus
  eligible-support-share arithmetic.
- Maier-Hein et al., Nature Communications 2018, DOI
  `10.1038/s41467-018-07619-7`, establish that challenge conclusions can change
  with cases, metrics, aggregation, and annotations. This supports the
  benchmark-audit motivation but is not an estimand-level predecessor.
- The ISLES'24 challenge report, arXiv `2408.10966`, uses clinical data as model
  inputs and reports segmentation performance; it does not publish this
  contribution census.

**Search result, not proof of novelty:** no exact duplicate of the frozen
top-ten clinical profile plus support-share decomposition was located. The card
must delete the broader statement that no ISLES'24 phenotype-join secondary
analysis was found and cite the 2026 EJR paper as the closest dataset-specific
neighbor. The exact gap remains narrow and repository-lineage-specific.

## 6. Existing assets, baselines, metrics, and compute

Existing assets are unusually strong: the contribution table, head membership,
absolute-mass share, exact eligible-support table, frozen region implementation,
archive manifest, D3/D4 governance, and checksum-pinned archive are all present.
No model, checkpoint, GPU, or new annotation is required.

The appropriate baselines are internal arithmetic identities, not challenge
segmentation scores:

1. exactly 99 analyzed support rows join one-to-one to 99 contribution rows;
2. frozen head membership and the previously ratified absolute-contribution
   share reproduce from the pinned contribution table;
3. the head's share of total `eroded_region_voxels` is computed once and shown
   beside the absolute-contribution share;
4. all 99 cases appear in the rank-discrepancy display, with fixed tie handling.

For the clinical clause, accepted descriptive outputs are group distributions,
missingness, and prespecified standardized/ordinal/binary contrasts. There is no
accepted benchmark metric for “clinical markedness,” and the contract correctly
prohibits such a verdict. The proposed random-relabeling “95% ranges” are not
sampling confidence intervals because neither group assignment nor the 99 cases
were randomized. They may be shown only as explicitly hypothetical
exchangeability references; a safer finite-population robustness display is
leave-one-head-case-out sensitivity. The uncertainty currency remains a human
decision and should be resolved in the revision before approval.

**Revised compute estimate:** Phase A can be a hash-and-join audit of four small
in-repo files and should take seconds, not 90 minutes. Phase B still requires a
selective read of 198 tiny phenotype members. If the held archive is locally
available and selective 7z extraction works, CPU time should be minutes; if the
archive must be reacquired, the honest worst case is the proven ~99 GB immutable
download plus integrity check (the parent origin-direct download took about 14
minutes on Colab, but this transfer time is environment-dependent). The current
3 GB map staging and 99-case image pass should be removed.

## 7. Leakage, confounds, and construct limits

The dominant confounds are not scanner or model leakage:

- **Selection/outcome coupling:** head membership comes from a final-infarct
  outcome-derived statistic. Later mRS and NIHSS share stroke severity,
  treatment, territory, and time pathways with that statistic. A positive
  clinical contrast cannot identify a subtype or explain dominance.
- **Eligible-support mediation:** larger eligible regions may mechanically
  increase absolute contribution and correlate with clinical severity. Showing
  every clinical contrast jointly with `B_i` reveals but does not remove this
  structure; no adjustment model is licensed with only ten head cases.
- **Center and missingness:** the official dataset is two-center, and the 2026
  EJR neighbor shows that outcome availability and center-held-out validation
  matter in ISLES'24. Center must therefore be included in the dictionary-frozen
  context if available, and missingness must be reported by group. With only ten
  head cases, this is descriptive context, not a corrected causal estimate.
- **Multiplicity/privacy:** every frozen variable must be displayed, no
  significance-selected headline is allowed, and small cells must remain
  suppressed. Aggregate output does not authorize patient-level clinical claims.

Concept validity is correspondingly bounded. mRS is global disability, NIHSS is
neurologic deficit severity at a named time point, and eligible support is the
take-13 estimator's analysis territory—not gross infarct volume, tissue at risk,
or biological “abundance.” The study measures association and arithmetic only.

## 8. Smallest probe of the riskiest remaining assumption

The map-reproduction gate is no longer the smallest probe because its intended
output is already present. The smallest decisive probe is phenotype-blind and
table-only:

1. hash `exclusions.csv`, `per_case_contributions.csv`, and
   `census_summary.json` against frozen identities;
2. filter `exclusions.csv` to `record_type == analyzed_case`;
3. require 99 unique case IDs and an exact set match to the contribution table;
4. require 99 finite positive integer `eroded_region_voxels` values and no
   duplicate analyzed rows;
5. verify from frozen code/blob and contract/blob that this field has exactly
   the `B_i` definition claimed; then freeze the support input hash.

That probe tests the real remaining support risk—provenance and join identity—
without touching maps or clinical rows. The riskiest assumption after it is
phenotype completeness. The smallest probe for that is the already planned
dictionary freeze followed, only after fresh authorization, by a D3-restricted
schema/missingness census of the 198 phenotype files before any contrast is
calculated. If fewer than seven head cases are nonmissing for a variable, that
row is descriptive but too weak for a bounded-null claim.

## 9. Required revision before GO

1. Replace map restaging/recomputation with the pinned, 99-row analyzed-case
   extract from `exclusions.csv`; add its SHA-256 and exact provenance checks.
2. Remove the 495 image/NCCT members from Phase A. Stage only the dictionary
   and, behind the Phase-B authority gate, the 198 phenotype members.
3. Update the dictionary freeze: both admission and 24-hour NIHSS are officially
   documented; choose the lineage-preserving 24-hour field as primary/contextual
   according to the revised analysis specification rather than treating its
   existence as unknown.
4. Resolve the clinical uncertainty display before approval. Do not label a
   random-relabeling range as confidence or sampling uncertainty; either retain
   it as an explicitly hypothetical reference plus leave-one-head-out sensitivity,
   or use only effect estimates and deterministic sensitivity displays.
5. Add center and per-group missingness to the mandatory context if the schema
   permits, and cite DOI `10.1016/j.ejrad.2026.113200`; narrow the novelty text.
6. Preserve the two-phase authority boundary: no phenotype row read before the
   amended contract receives fresh human approval.

This is a **REVISE**, not a pause or scientific no-go. All essential data exist,
the primary support quantity is already computed under the exact frozen method,
and the clinical schema is documented. The revision removes work and risk while
leaving both registered clauses intact.

## In plain terms

Yes, this study can be done, but the current plan is more expensive than it
needs to be. The exact imaging-support number is already stored for all 99
patients, so the imaging rerun should be replaced by a quick provenance and
join check; the remaining work is a restricted read of small clinical files
inside a checksum-pinned 99 GB archive. The biggest practical risk is that only
ten patients are in the dominant group and some clinical fields may be missing,
so an unremarkable comparison could be too imprecise to say much. **Verdict:
REVISE.**
