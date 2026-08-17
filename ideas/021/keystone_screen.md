# Keystone screen

## Keystone as stated

> Per-case perfusion maps are co-registered into a common space where a hemisphere-restricted edit and an affected-side readout can be constructed automatically.

## What was inspected

I inspected the authors' official dataset record, the full methods section of the primary dataset paper, and a local clone of the authors' official challenge repository at commit `94b34863a099a8aeae6cf9b989c78ff2c767b80e`.

The official Zenodo record states, verbatim:

> “'Derivatives' include all modalities linearly co-registered to the NCCT space.”

Source: https://zenodo.org/records/16813698, **Data structure** (lines 53–55 in the rendered record). The same record enumerates NCCT-space derivative CBF, CBV, MTT, and Tmax files and an NCCT-space follow-up lesion mask (lines 67–82). This directly establishes that the released derivative perfusion maps and outcome mask have a shared named reference space within each case.

The primary dataset paper independently describes the processing:

> “CTA, CT perfusion (including derived perfusion maps), and DWI and/or apparent diffusion coefficient scans were linearly co-registered to the noncontrast CT space using rigid transformations for CT and affine transformations for MRI using Elastix (version 5.3.0; elastix.lumc.nl) and NiftyReg (version 1.5.69.6; github.com/KCL-BMEIS/niftyreg).”

Source: https://pubs.rsna.org/doi/full/10.1148/ryai.250603, **Data Preprocessing** (DOI `10.1148/ryai.250603`; paragraph beginning at rendered line 102).

The official repository provides a consistent file-level statement. Its README lists `space-ncct` CBF, CBV, MTT, and Tmax derivatives under the same per-subject session directory. Source: https://github.com/ezequieldlrosa/isles24/blob/94b34863a099a8aeae6cf9b989c78ff2c767b80e/README.md#L26-L37.

These are primary-source statements about the released data, not an inference from a search result. They verify the load-bearing availability of within-case, NCCT-referenced perfusion maps needed to define spatially disjoint hemisphere edits and readouts.

## Mandatory residual-assumption check

**If this card only verified the nearest checkable thing, what is it still assuming?**

The nearest checkable fact is that files named as NCCT-space derivatives exist. The inference additionally assumes that the actual NIfTI headers/arrays are mutually compatible after the eventual model's frozen preprocessing, that left-right orientation is preserved, and that a usable midsagittal plane and hemisphere masks can be derived case by case. I did not inspect the 99 GB `train.7z` archive's NIfTI headers, so exact voxel-grid congruence is not directly verified here. This is a real Stage-0 implementation/quality-control residual, but it is not a different cohort-level keystone: the authors explicitly say all modalities were co-registered to NCCT space, and exact grids can be resampled within that common physical coordinate system.

A separate nearby claim does **not** survive inspection: the card says an “official baseline recipe” exists, but the official repository at the inspected commit contains only the README, evaluation utilities, and an evaluation notebook—no training loader, model configuration, or nnU-Net recipe. That omission weakens the card's `existing_assets` and feasibility language, but it does not make the proposed study impossible because the card already specifies training a model rather than requiring a released checkpoint. It should not be mistaken for evidence about the registration keystone.

The edit's in-distribution validity and midsagittal-plane reliability remain empirical gates, as the card itself acknowledges. They are not established by co-registration and must not be treated as already verified.

```json
{"verdict": "PASS", "evidence": "'Derivatives' include all modalities linearly co-registered to the NCCT space.", "source": "https://zenodo.org/records/16813698, Data structure, lines 53-55", "note": "The common-space prerequisite is directly supported; exact header congruence, orientation QC, and automatic midline reliability remain Stage-0 checks, and no official training recipe was found."}
```
