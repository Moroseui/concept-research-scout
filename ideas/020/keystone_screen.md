# Keystone screen

## Keystone as stated

> A counterfactual generator can alter connectedness/contact while preserving clinically salient Tmax intensity, territory and spatial-frequency distributions closely enough to remain in-distribution.

This is an existential and empirical claim about intervention validity. It is not established merely by showing that Tmax/CBF maps exist or that their topology can be changed computationally.

## Primary material inspected

I cloned the official ISLES'24 repository at commit `94b34863a099a8aeae6cf9b989c78ff2c767b80e` and inspected its complete tracked file list, README, evaluation code, and example notebook.

The official data schema directly confirms the nearest checkable fact: the release includes perfusion maps and their NCCT-space derivatives. The README lists, verbatim:

> `+-- sub-strokecase0001_ses-0001_tmax.nii.gz`
>
> `+-- sub-strokecase0001_ses-0001_cbf.nii.gz`

and later:

> `+-- sub-strokecase0001_ses-0001_space-ncct_tmax.nii.gz`
>
> `+-- sub-strokecase0001_ses-0001_space-ncct_cbf.nii.gz`

Source: official ISLES'24 repository, `README.md`, lines 15-18 and 29-33, commit `94b3486`: https://github.com/ezequieldlrosa/isles24/blob/94b34863a099a8aeae6cf9b989c78ff2c767b80e/README.md#L15-L18 and https://github.com/ezequieldlrosa/isles24/blob/94b34863a099a8aeae6cf9b989c78ff2c767b80e/README.md#L29-L33

The official example does not provide or validate the required generator. It says:

> `''' We'll generate a basic infarct segmentation algorithm by thresholding the (already-preprocessed) Tmax parameter map.  '''`

and:

> `# As an example, we'll segment Tmax by using a cutoff at 9 seconds.`
>
> `cutoff = 9`
>
> `segmented_image = tmax_image > cutoff`

Source: official ISLES'24 repository, `utils/isles24_evaluate.ipynb`, code cells 2 and 5, commit `94b3486`: https://github.com/ezequieldlrosa/isles24/blob/94b34863a099a8aeae6cf9b989c78ff2c767b80e/utils/isles24_evaluate.ipynb

The repository contains no generator implementation, topology-altering augmentation, real-versus-edit discriminator, or validation study establishing that such edits are in-distribution. This is a bounded statement about the inspected official repository, not proof that no suitable method exists elsewhere.

## Residual-assumption check

Mandatory question: **If this card only verified the nearest checkable thing, what is it still assuming?**

It verified that registered Tmax and CBF maps are supplied. It still assumes the load-bearing fact that one can change connectedness/core-contact while simultaneously holding the clinically salient intensity field, vascular territory, spatial-frequency structure, and other model-visible cues sufficiently fixed that a prediction change identifies topology rather than generator artifacts. It further assumes that a near-chance discriminator and summary-statistic checks are sensitive enough to certify that condition. The latter is part of the real keystone, not merely a downstream implementation detail.

No inspected primary source demonstrates either assumption. The official repository's thresholding example establishes computability of a mask, not validity of a topology-swapped counterfactual. Because failure has not been demonstrated, `KILL` would overstate the evidence; because the load-bearing fact has not been demonstrated, `PASS` is unavailable.

```json
{"verdict": "UNVERIFIABLE", "evidence": "''' We'll generate a basic infarct segmentation algorithm by thresholding the (already-preprocessed) Tmax parameter map.  '''", "source": "https://github.com/ezequieldlrosa/isles24/blob/94b34863a099a8aeae6cf9b989c78ff2c767b80e/utils/isles24_evaluate.ipynb, code cell 2", "note": "The official materials verify map availability but provide no primary evidence that topology-changing counterfactuals can be made in-distribution or that the proposed gates can certify them."}
```
