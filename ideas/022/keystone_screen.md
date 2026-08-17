# Keystone screen

## Keystone as stated

> A sufficient subset of ISLES'24 cases has complete long acquisitions that can be shortened to multiple still-clinically-plausible prefixes without changing sampling rate or preprocessing, and the frozen model accepts variable-length series or a masking scheme seen during training.

This is a compound prerequisite. Both the acquisition-duration/completeness clause and the model-input/masking clause must hold.

## What I inspected

1. **The primary dataset paper (full methods).** Riedel et al., *Radiology: Artificial Intelligence*, DOI [10.1148/ryai.250603](https://pubs.rsna.org/doi/full/10.1148/ryai.250603), “Data Preprocessing,” states:

   > “Four-dimensional CT perfusion series underwent image co-registration and temporal resampling (1 frame/sec)”

   This verifies a released, uniformly resampled 4D series. It does **not** report the number of frames per patient, acquisition durations, return-to-baseline/completeness, or how many cases could support 5-, 10-, and 15-second clinically plausible prefixes. The same paper's “Data Repository and Storage” reports a public training set of 149, but cohort size is not evidence of temporal completeness.

2. **The official data repository at the current commit.** The ISLES'24 repository, [`README.md` lines 8–22 at commit 94b34863a099a8aeae6cf9b989c78ff2c767b80e](https://github.com/ezequieldlrosa/isles24/blob/94b34863a099a8aeae6cf9b989c78ff2c767b80e/README.md#L8-L22), says:

   > “You can access the ISLES'24 data after registration to the challenge.”

   and lists `sub-strokecase0001_ses-0001_ctp.nii.gz`. This verifies release structure, not header-level time-axis adequacy. I also inspected the repository tree: it provides the evaluation notebook and metrics, but no frozen raw-CTP model loader, checkpoint, temporal-mask contract, or training augmentation showing that missing/padded prefixes were in distribution.

3. **The published winning-model methods.** Ren et al., arXiv:2505.18424v2, Table 1 and its caption, [“Intensity Windowing”](https://arxiv.org/html/2505.18424v2#S3.SS3), identify the inputs to the final nnU-Net:

   > “Windowing ranges for each CT modality used as input to the nnU-Net segmentation model for the final submission to the ISLES’24 challenge.”

   The table enumerates **CTA, CBF, CBV, MTT, and Tmax**. It does not enumerate raw 4D CTP. Thus the only readily identifiable published frozen winner cannot establish the card's raw-series variable-length/masking clause; its perfusion inputs are derived 3D maps.

4. **The official Zenodo record.** [Zenodo concept DOI 10.5281/zenodo.16731717](https://zenodo.org/records/17652035), description/Data structure, says:

   > “Admission imaging: non-contrast CT (NCCT), CT angiography (CTA), 4D CT perfusion (CTP) time series, and perfusion maps (Tmax, CBF, CBV, MTT).”

   The current archive is a single approximately 99-GB `train.7z`; its public record does not expose per-case NIfTI dimensions or curve-completeness summaries. Therefore the required subset count cannot be verified from the release schema alone.

## Residual assumption check

**Mandatory question:** “if this card only verified the nearest checkable thing, what is it still assuming?”

It verified the nearest facts—raw 4D CTP exists and was resampled to 1 frame/sec—but still assumes (a) enough individual curves extend beyond washout to support all proposed censoring points, and (b) an obtainable frozen **raw-CTP** model has a training-supported way to represent shorter prefixes without introducing an out-of-distribution padding or mask cue.

Clause (b) is the more load-bearing residual assumption. Even a favorable header census would not identify acquisition-boundary use if the intervention changes the model's tensor convention in a way absent from training. No model is named in the card, the official repository supplies no such model contract, and the published winner consumes derived maps rather than raw 4D curves. This is not evidence that no suitable model can be trained or exists; it means the stated keystone cannot presently be verified or falsified from the inspected primary artifacts. The proper screen outcome is therefore `UNVERIFIABLE`, not `KILL`.

```json
{"verdict": "UNVERIFIABLE", "evidence": "Windowing ranges for each CT modality used as input to the nnU-Net segmentation model for the final submission to the ISLES’24 challenge.", "source": "https://arxiv.org/html/2505.18424v2#S3.SS3, Table 1 caption; the table lists CTA, CBF, CBV, MTT, and Tmax, not raw 4D CTP", "note": "Raw 4D CTP release and 1-frame/sec resampling are verified, but neither sufficient complete long curves nor a frozen raw-CTP model with training-supported prefix masking/padding is verified."}
```
