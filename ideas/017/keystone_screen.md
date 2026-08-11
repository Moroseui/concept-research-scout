# Keystone screen

## Keystone as stated

> Sybil's final input tensor preserves tracheal cross-sectional geometry accurately enough for minimum tracheal index to be measured and encoded, and NLST contains enough low-index cases independent of sex, emphysema, lung volume, and reconstruction for a selective-use test.

This is a conjunction. Both tensor-level measurement fidelity and an adequate, non-collinear NLST subgroup must be true. Failure of either part makes the proposed selective-use experiment impossible or uninterpretable.

## What I inspected

### Official Sybil inference preprocessing

I inspected the official `reginabarzilaygroup/Sybil` repository at commit `d9fc81b93c1c6239a570c1c570c1f2a2e6266a4a`.

The released inference path explicitly resamples and then crops or pads:

> `x = self.resample_transform(x)`
>
> `x = self.padding_transform(x)`

Source: [official Sybil repository, `sybil/serie.py`, lines 161–167](https://github.com/reginabarzilaygroup/Sybil/blob/d9fc81b93c1c6239a570c1c570c1f2a2e6266a4a/sybil/serie.py#L161-L167).

The target physical spacing is explicitly isotropic in-plane:

> `VOXEL_SPACING = (0.703125, 0.703125, 2.5)`

Source: [official Sybil repository, `sybil/datasets/utils.py`, line 9](https://github.com/reginabarzilaygroup/Sybil/blob/d9fc81b93c1c6239a570c1c570c1f2a2e6266a4a/sybil/datasets/utils.py#L9).

The final tensor dimensions are fixed at 256×256×200:

> `"img_size": [256, 256],`
>
> `"num_images": 200,`

Source: [official Sybil repository, `sybil/serie.py`, lines 239–250](https://github.com/reginabarzilaygroup/Sybil/blob/d9fc81b93c1c6239a570c1c570c1f2a2e6266a4a/sybil/serie.py#L239-L250).

These quoted facts show that the pipeline uses physical-spacing-aware resampling with equal row and column target spacing. They do **not** directly show native-DICOM versus final-tensor agreement for minimum tracheal index, retention of the relevant intrathoracic tracheal segment after crop/pad, or that Sybil encodes the ratio.

### Primary Sybil cohort report

The primary paper states:

> “We applied for and were granted access to the radiologic and clinical data from a sample of 15,000 NLST participants”

Source: [Mikhael et al., *Journal of Clinical Oncology*, Materials and Methods, “NLST Data”](https://pmc.ncbi.nlm.nih.gov/articles/PMC10419602/#sec2).

This establishes the broad cohort size, not the number of low-index cases or their joint distribution with sex, emphysema, lung volume, and reconstruction. I found no primary-source table or released schema containing the automatically measured tracheal index needed to verify that part without running the proposed Stage 0 measurement on accessible images.

## Residual assumption check

Mandatory question: **If this card only verified the nearest checkable thing, what is it still assuming?**

It verified the adjacent fact that Sybil resamples scans to equal in-plane physical spacing. It still assumes that interpolation and center crop/pad preserve the *minimum* centerline-perpendicular transverse/AP ratio with acceptable error on actual NLST scans, that the relevant tracheal segment remains in-frame, and that enough low-index cases remain after matching or adjustment for sex, emphysema, lung volume, and reconstruction. Those are the load-bearing facts, and neither the implementation alone nor the published sample size verifies them.

The stated keystone is therefore correctly aimed at the real assumptions, but it cannot be resolved from the inspected primary sources. It requires direct paired measurement on native DICOM and final tensors plus a joint-distribution audit on obtainable NLST cases.

```json
{"verdict": "UNVERIFIABLE", "evidence": "x = self.resample_transform(x) / x = self.padding_transform(x)", "source": "https://github.com/reginabarzilaygroup/Sybil/blob/d9fc81b93c1c6239a570c1c570c1f2a2e6266a4a/sybil/serie.py#L161-L167", "note": "Official code verifies physical resampling and crop/pad, but no inspected primary source establishes final-tensor tracheal-index agreement or an adequate non-collinear NLST low-index subgroup."}
```
