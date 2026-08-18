# Keystone screen — idea 029 (isles24-scout-004-c01)

**Idea:** The ground truth remembers the algorithm that drafted it
**Screen date:** 2026-08-18
**Verdict: PASS** (keystone verified true; residual assumption enlarged — see §4)

## 1. The keystone as stated on the card

> "The correction field is recoverable: the initializing segmenter is public
> and re-runnable on released follow-up MRI, so draft-versus-final
> disagreement can be computed per case."

Card status claimed: `INSPECTED_TRUE`. This screen re-inspected every leg of
that claim against primary sources, plus the mandatory nearest-checkable-thing
follow-up (§4).

## 2. What was inspected, with verbatim evidence

### 2a. The ground truth was drafted by the ISLES'22 ensemble and corrected "when needed"

Source: arXiv 2408.10966v1 (ISLES'24 dataset paper), Dataset section,
https://arxiv.org/html/2408.10966v1 (fetched 2026-08-18):

> "Lesion masks are derived from DWI images using the ISLES'22 ensemble
> algorithm. Quality control and correction of the lesion masks are performed
> when needed by medical students (TAB, HPM) supervised by two
> neuroradiologists (JSK, BW) with more than 10 years of experience."

This matches the card's quote exactly. The hybrid draft-then-correct
provenance — the object of study — is documented in the primary source.

### 2b. The initializing segmenter is public and containerized

Source: https://github.com/ezequieldlrosa/DeepISLES README (fetched
2026-08-18):

> "DeepISLES is an out-of-the-box software tool for processing MRI scans and
> segmenting ischemic stroke lesions, developed in collaboration with leading
> teams from the ISLES'22 MICCAI Challenge."

Docker image: `docker pull isleschallenge/deepisles`. Input requirements as
quoted from the README: DWI (b=1000) required; ADC required; FLAIR

> "Required for ensemble (optional for single algorithm outputs)"

Run-mode flag relevant to the FLAIR issue (README parameter table):
`fast` = "Run a single model for faster execution";
`save_team_outputs` = "Save outputs of individual models before ensembling".

### 2c. The weights are released

Source: https://zenodo.org/records/14026715 (fetched 2026-08-18):
title "Model weights- The ISLES'22 Ensemble Algorithm", version v1,
published 2024-11-01, single file `stroke_ensemble_weights.7z` (9.1 GB).
The record exists and is the one the card cites.

### 2d. The released dataset contains per-case follow-up DWI/ADC — and, decisively, on the SAME grid as the ground-truth mask

Source: https://zenodo.org/records/16731717 (ISLES'24 training data, fetched
2026-08-18): "149 acute ischemic stroke cases"; follow-up imaging includes
"post-treatment MRI (DWI and ADC)"; masks are "binary infarct masks derived
from follow-up MRI (lesion-msk.nii.gz)"; derivatives are "linearly
co-registered to the NCCT space". Per-case derivative files as listed in the
record's BIDS tree:

> `sub-strokecase0001_ses-02_space-ncct_dwi.nii.gz`
> `sub-strokecase0001_ses-02_space-ncct_adc.nii.gz`
> `sub-strokecase0001_ses-02_space-ncct_lesion-msk.nii.gz`

License: CC BY-NC-SA 4.0.

This resolves the question the card never asked (§4a): the follow-up DWI/ADC
and the ground-truth mask are released **in the same space on the same grid**
(`space-ncct`), so a DeepISLES rerun on the released DWI/ADC produces a draft
mask D directly comparable voxelwise to the released G. The disagreement
field D xor G is computable per case with no annotator and no registration
step of our own. The keystone's operational content is TRUE.

## 3. Verdict on the stated keystone

Every leg verified: provenance documented (2a), segmenter public and
containerized (2b), weights released (2c), follow-up MRI released per case
and grid-aligned with the mask (2d). **PASS.**

## 4. Mandatory follow-up: what is the card still assuming?

The card verified "the draft can be recomputed." The load-bearing assumption
underneath is stronger: **that the recomputed draft approximates the draft
the organizers actually produced.** The card acknowledges version drift as
its residual assumption; inspection shows that residual is real and has TWO
components, one of which the card did not name:

**(a) Processing-path drift (not on the card).** The paper states masks were
"derived from DWI images" and that follow-up series were registered to NCCT
with affine transformations. The organizers therefore ran the ensemble on
native-space DWI (or in an unspecified space) and the result reached NCCT
space through their registration; a rerun necessarily consumes the released,
already-resampled `space-ncct` DWI/ADC, because no native-space follow-up
data and no registration transforms appear in the release. Consequence: the
card's "bitwise-identical fraction" statistic is degraded by interpolation
alone and is a **lower bound** on draft survival, not an unbiased estimate.
This lands on the safe side of the card's own prespecified asymmetry (high
agreement remains robust evidence of imprint; low agreement was already
declared ambiguous), so it weakens power, not validity — but the analysis
plan should say "resampling" alongside "version drift" as a cause of
depressed agreement.

**(b) The FLAIR gap (partially on the card).** The released ensemble
requires FLAIR; ISLES'24 releases no follow-up FLAIR ("included DWI and
ADC"). Either the organizers ran a no-FLAIR configuration (consistent with
"derived from DWI images") or they used FLAIR that was never released. A
rerun must use the DWI/ADC-only path (single-algorithm outputs, or the
ensemble's no-FLAIR mode if its code permits — a stage-0 configuration
check). This is the card's stated residual assumption, confirmed as real and
narrowed to a concrete configuration question.

Neither component falsifies the keystone: the disagreement field is
computable and the prespecified asymmetric interpretation absorbs both drift
sources. They are recorded here so the stage-0/analysis plan inherits them
explicitly.

## 5. Classification of evidence

Verified fact: §2a–2d quotes and file listings. Source-supported
interpretation: same-grid comparability of D and G (filenames' shared
`space-ncct` label plus the record's co-registration statement). Inference:
processing-path drift in §4a (organizers ran on pre-registration images;
"derived from DWI images" + no transforms in release). Nothing in this
screen rests on memory.

```json
{"verdict": "PASS", "evidence": "Lesion masks are derived from DWI images using the ISLES'22 ensemble algorithm. Quality control and correction of the lesion masks are performed when needed by medical students (TAB, HPM) supervised by two neuroradiologists (JSK, BW) with more than 10 years of experience.", "source": "arXiv 2408.10966v1, Dataset section (https://arxiv.org/html/2408.10966v1); same-grid comparability from https://zenodo.org/records/16731717 derivative filenames (space-ncct dwi/adc/lesion-msk); segmenter at github.com/ezequieldlrosa/DeepISLES with weights zenodo.org/records/14026715", "note": "Keystone true and stronger than claimed (draft and GT share the released space-ncct grid); residual assumption enlarged to include resampling-induced drift alongside version drift — bitwise-identical fraction is a lower bound."}
```
