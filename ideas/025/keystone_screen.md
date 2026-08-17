# Keystone screen

## Keystone as stated

> The released motion-corrected 4D CTP retains a measurable, patient-gradeable residual-motion signature (FD dynamic range above the re-registration noise floor).

This is not established by the primary sources inspected. It is also not contradicted by them, so the appropriate screen result is `UNVERIFIABLE`, not `KILL`.

## What I inspected

### Dataset paper (primary source)

I inspected the full-text Methods section of Riedel et al., *Radiology: Artificial Intelligence* 2026, DOI [10.1148/ryai.250603](https://doi.org/10.1148/ryai.250603), especially **Materials and Methods → Data Preprocessing**. The load-bearing description is:

> “Four-dimensional CT perfusion series underwent image co-registration and temporal resampling (1 frame/sec); perfusion maps (cerebral blood flow, cerebral blood volume, mean transit time, and time-to-maximum) were derived using the clinical, U.S. Food and Drug Administration–cleared software icobrain cva (version 1.5.0, icometrix).”

Source: [RSNA full text](https://pubs.rsna.org/doi/10.1148/ryai.250603), **Data Preprocessing**, lines 102–105 in the HTML text (quoted sentence at line 104).

This verifies the nearest adjacent fact: the released CTP has already undergone image co-registration and 1-Hz temporal resampling. The paper does not report residual framewise displacement, a motion-quality distribution, retained registration transforms, patient motion grades, or a validation showing that a post-correction image-derived statistic recovers original head motion.

### Official challenge repository (primary source)

I cloned the official repository, `ezequieldlrosa/isles24`, and inspected its README, evaluation notebook, evaluation utility, and included data tree. The README documents a CTP file in the released layout:

> “sub-strokecase0001_ses-0001_ctp.nii.gz”

Source: [official GitHub repository README](https://github.com/ezequieldlrosa/isles24/blob/main/README.md), **Data**, raw-data tree (repository README line 22).

The repository contains no CTP sample volume, motion parameters, motion grades, or correction implementation with which to inspect the stated property. Thus it verifies availability and layout, not residual-motion dynamic range or construct validity.

## Mandatory residual-assumption check

**If this card only verified the nearest checkable thing, what is it still assuming?**

It verified that the dataset supplies co-registered/resampled 4D CTP. It is still assuming that variation obtained by rigidly re-registering those already co-registered frames is (1) above registration and contrast-kinetic noise, (2) patient-gradeable, and, most importantly, (3) a valid trace of the patient's original head movement/restlessness rather than bolus-driven intensity change, interpolation residue, anatomy-dependent registration error, scanner artifact, or behavior of the unknown first-pass correction.

That third proposition is the deeper load-bearing keystone. A nonzero FD-like distribution alone would not verify it. The primary paper describes the preprocessing but provides neither original-to-corrected transforms nor a residual-motion validation. The official repository supplies neither the correction code nor motion provenance. Establishing the fact therefore requires direct inspection of released CTP volumes plus an independent validity check (for example, retained original motion transforms or paired uncorrected series); it cannot be settled from the inspected primary documentation.

```json
{"verdict":"UNVERIFIABLE","evidence":"Four-dimensional CT perfusion series underwent image co-registration and temporal resampling (1 frame/sec); perfusion maps (cerebral blood flow, cerebral blood volume, mean transit time, and time-to-maximum) were derived using the clinical, U.S. Food and Drug Administration–cleared software icobrain cva (version 1.5.0, icometrix).","source":"https://pubs.rsna.org/doi/10.1148/ryai.250603 — Materials and Methods, Data Preprocessing, HTML line 104","note":"Primary sources establish prior co-registration, but neither establish patient-gradeable residual motion nor validate post-correction FD as a trace of original patient movement."}
```
