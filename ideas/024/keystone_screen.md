# Keystone screen — Idea 024

## Keystone as stated

> ISLES'24 raw CTP has sufficient temporal duration, signal-to-noise ratio, and post-bolus sampling to produce CTH estimates stable across plausible arterial-input-function choices and deconvolution regularization in a substantial fraction of the public cases.

This is the correct load-bearing fact. If transit-time dispersion is not recoverable and stable after the released temporal processing, the proposed X cannot be measured on this cohort and neither the observational nor counterfactual result can be interpreted as capillary transit-time heterogeneity.

## Primary sources inspected

I inspected the official ISLES'24 GitHub repository at commit `94b34863a099a8aeae6cf9b989c78ff2c767b80e`, including its complete tracked-file list and data schema. The schema confirms that a 4D CTP object is released:

> `+-- sub-strokecase0001_ses-0001_ctp.nii.gz`

Source: official ISLES'24 repository, `README.md`, line 22, commit `94b3486`: https://github.com/ezequieldlrosa/isles24/blob/94b34863a099a8aeae6cf9b989c78ff2c767b80e/README.md#L20-L22

The same official schema also confirms that standard perfusion maps accompany it:

> `+-- sub-strokecase0001_ses-0001_tmax.nii.gz`
>
> `+-- sub-strokecase0001_ses-0001_mtt.nii.gz`
>
> `+-- sub-strokecase0001_ses-0001_cbf.nii.gz`
>
> `+-- sub-strokecase0001_ses-0001_cbv.nii.gz`

Source: official ISLES'24 repository, `README.md`, lines 15–19, commit `94b3486`: https://github.com/ezequieldlrosa/isles24/blob/94b34863a099a8aeae6cf9b989c78ff2c767b80e/README.md#L15-L19

I also inspected the primary ISLES'24 challenge paper's Dataset methods. It states:

> “The 4D CTP series are motion-corrected through image co-registration and temporally resampled at 1 frame/second. Afterwards, perfusion maps are generated using a traditional tracer-kinetics deconvolution algorithm.”

Source: de la Rosa et al., *ISLES'24: Improving final infarct prediction in ischemic stroke using multimodal imaging and clinical data*, arXiv:2408.10966, Methods, “Dataset,” PDF page 3: https://arxiv.org/pdf/2408.10966

These sources verify the nearest checkable facts—availability of 4D CTP and resampling to 1 Hz—but do not report per-case acquisition duration, number of temporal samples, bolus arrival and tail coverage, signal-to-noise, or stability of a CTH estimate across AIF choices and regularizers. The official repository contains no released CTH calculation or validation. Absence of those results does not demonstrate that the keystone is false.

## Mandatory residual-assumption check

**If this card only verified the nearest checkable thing, what is it still assuming?**

It verified that motion-corrected 4D CTP exists at 1 frame/second, while still assuming that those time series retain enough pre-bolus and post-bolus support and effective temporal information to identify the *variance* of a deconvolved transit-time distribution—not merely its mean or a conventional Tmax/MTT value—and that this variance is stable to reasonable AIF and regularization choices in a substantial fraction of cases.

That residual is identical to the stated keystone, not a different hidden prerequisite. It cannot be settled from the public schema or methods text. It requires direct header/time-axis inspection across the released cases followed by the proposed multi-AIF, multi-regularizer stability experiment. Therefore the honest screen result is `UNVERIFIABLE`, not `PASS` and not `KILL`.

```json
{"verdict": "UNVERIFIABLE", "evidence": "The 4D CTP series are motion-corrected through image co-registration and temporally resampled at 1 frame/second. Afterwards, perfusion maps are generated using a traditional tracer-kinetics deconvolution algorithm.", "source": "https://arxiv.org/pdf/2408.10966 — Methods, Dataset, PDF page 3", "note": "Primary sources verify 4D CTP at 1 Hz but do not establish duration, tail coverage, SNR, or stable CTH recovery; direct released-case inspection is still required."}
```
