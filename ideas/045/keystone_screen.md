# Keystone screen — idea 045

## Keystone as stated

The card states a two-rung prerequisite:

1. The imported idea-023 bundle must contain a label-blind, case-by-band-by-cell NCCT attenuation audit that can support a governed cohort aggregate.
2. It must be possible to freeze an NCCT-only tissue-viability gate before outcome access, recalibrate support and precision under that gate, and run a tissue-gated census with adequate support.

This is not one presently verifiable fact. Rung 0a is an extant-artifact question; rung 0b combines an unvalidated measurement assumption with future empirical gates.

## What was inspected

### 1. The nearest checkable prerequisite is true

I directly inspected the imported scientific bundle at commit-local path `probes/023/results/results_v2/`.

`summary.json`, line 7, states verbatim:

> `"bin_tissue_audit_rows": 594,`

The header and first data row of `bin_tissue_audit.csv` state verbatim:

> `case_id,stratum,style_group,member_voxels,finite_hu_voxels,nonfinite_hu_voxels,median_hu,q25_hu,q75_hu,iqr_hu`
>
> `sub-stroke0002,1,Q1_low_CBV,3969,3969,0,16.0,11.0,18.0,7.0`

The cited motivating example is also present verbatim at lines 254–255:

> `sub-stroke0092,1,Q1_low_CBV,3371,3371,0,3.0,2.0,4.0,2.0`
>
> `sub-stroke0092,1,Q4_high_CBV,3374,3374,0,23.0,8.0,24.0,16.0`

Thus the 594-row input needed for Rung 0a exists and has the stated 99 × 3 × 2 structure. The cross-family interpretation review independently records: “I checked ... all 594 HU audit rows” (`ideas/023/interpret_review.md`, section 3). This establishes availability and prior validation of the artifact, not the validity of a viability threshold.

### 2. The primary dataset supports the required modality linkage

The official ISLES'24 release page says:

> “Admission imaging: non-contrast CT (NCCT), CT angiography (CTA), 4D CT perfusion (CTP) time series, and perfusion maps (Tmax, CBF, CBV, MTT).”

It also says:

> “Derivatives include all modalities linearly co-registered to the NCCT space.”

Source: official ISLES'24 Zenodo record 16813698, **Description → Data structure**, DOI 10.5281/zenodo.16813698: https://zenodo.org/records/16813698

This verifies that an NCCT-based voxel filter can be applied to the released perfusion-map coordinate system. It does not show that such a filter identifies viable tissue.

## Mandatory residual-assumption check

**If this card only verified the nearest checkable thing, what is it still assuming?**

It is still assuming that a prespecified absolute NCCT-HU window can separate established injury or partial-volume CSF from “viable-attenuation tissue” without becoming an outcome-proxy selection rule, and that enough voxels and patients will survive in every flow band for the recalibrated analysis.

That is the real load-bearing keystone. The file's existence, row count, co-registration, and selected case examples are only adjacent facts.

The primary clinical study *Assessing Brain Tissue Viability on Nonenhanced Computed Tomography After Ischemic Stroke* states in its Introduction:

> “There is, however, uncertainty in how early ischemic features on NECT translate to the different pathophysiological processes of acute ischemic brain injury. Specifically, whether NECT can be used to differentiate reversible from irreversible ischemic injury in the acute stroke phase...”

Source: Alzahrani et al., *Journal of the Belgian Society of Radiology* (2023), **Introduction**, PMCID PMC9855746: https://pmc.ncbi.nlm.nih.gov/articles/PMC9855746/

This evidence does not demonstrate that the proposed gate is impossible, so `KILL` would overstate the source. It does show that the gate's biological interpretation is not a settled property that can be certified from modality availability or a few HU examples. Adequate post-gate support is likewise a future Phase-S/census result. The load-bearing prerequisite therefore remains unverified at this screen.

```json
{"verdict": "UNVERIFIABLE", "evidence": "There is, however, uncertainty in how early ischemic features on NECT translate to the different pathophysiological processes of acute ischemic brain injury. Specifically, whether NECT can be used to differentiate reversible from irreversible ischemic injury in the acute stroke phase...", "source": "https://pmc.ncbi.nlm.nih.gov/articles/PMC9855746/ — Introduction", "note": "The 594-row audit and NCCT-space linkage are inspected true, but the real keystone—an outcome-independent viability gate with adequate retained support—requires prospective calibration and cannot be certified from current primary evidence."}
```
