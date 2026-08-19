# Keystone screen

Screened 2026-08-19 against the official ISLES'24 dataset record and the
primary dataset paper.

## Keystone as stated

> The released CBF, CBV, and MTT maps have meaningful common support and
> scaling such that a stable, nontrivial central-volume residual can be
> computed rather than merely rediscovering zeros, support edges, or arbitrary
> normalization.

This is a compound empirical prerequisite. It requires more than the three
maps being present and spatially registered: their stored voxel values must
have documented or inspectable scale, support, background, and clipping
semantics, and the proposed residual must be nontrivial away from excluded
artifacts.

## What I inspected

### Official dataset release

The Zenodo record confirms that the three maps are released alongside Tmax:

> “Admission imaging: non-contrast CT (NCCT), CT angiography (CTA), 4D CT
> perfusion (CTP) time series, and perfusion maps (Tmax, CBF, CBV, MTT).”

Source: official ISLES'24 Zenodo record 16748089, **Description**, admission
imaging bullet: https://zenodo.org/records/16748089 (concept DOI
10.5281/zenodo.16731717).

The same record says what “derivatives” means and lists all three maps in the
same target space:

> “'Derivatives' include all modalities linearly co-registered to the NCCT
> space.”

Source: official ISLES'24 Zenodo record 16748089, **Data structure**, followed
by the derivative filenames
`space-ncct_mtt.nii.gz`, `space-ncct_cbf.nii.gz`, and
`space-ncct_cbv.nii.gz`: https://zenodo.org/records/16748089.

This verifies co-location in a common coordinate space. It does **not** verify
meaningful common numeric support or scaling.

The release does not expose per-map sidecars or sample maps as separately
inspectable files. Its file inventory consists of one archive:

> “train.7z”

Source: official Zenodo Records API, record 16748089, `files[0].key` (size
99,014,629,647 bytes): https://zenodo.org/api/records/16748089.

### Primary dataset paper

The paper identifies a common producing implementation:

> “perfusion maps (cerebral blood flow, cerebral blood volume, mean transit
> time, and time-to-maximum) were derived using the clinical, U.S. Food and
> Drug Administration–cleared software icobrain cva (version 1.5.0,
> icometrix).”

Source: Riedel et al., *Radiology: Artificial Intelligence* 2026,
DOI 10.1148/ryai.250603, **Materials and Methods — Image Acquisition**, PDF
p. 3: https://pubs.rsna.org/doi/pdf/10.1148/ryai.250603.

It also confirms the registration operation:

> “CTA, CT perfusion (including derived perfusion maps), and DWI and/or
> apparent diffusion coefficient scans were linearly co-registered to the
> noncontrast CT space using rigid transformations for CT and affine
> transformations for MRI”

Source: same paper and section, PDF p. 3:
https://pubs.rsna.org/doi/pdf/10.1148/ryai.250603.

Neither the inspected release description nor the paper states the stored
units, scale factors, clipping bounds, background/invalid-voxel convention,
or whether icobrain cva stores MTT independently or as an algebraic derivative
of the stored CBF and CBV maps. No quoted primary-source evidence therefore
establishes that the proposed log residual is stable, spatially nontrivial, or
separable from support and clipping artifacts.

## Residual-assumption check (mandatory wrong-keystone question)

If the card only verified the nearest checkable thing, what is it still
assuming? The nearest checkable fact is that CBF, CBV, and MTT are all present,
were produced by one named software version, and have NCCT-space derivatives.
The load-bearing fact is different: actual released voxel arrays must overlap
on valid tissue and retain commensurate quantitative scales while exhibiting
a residual that is neither forced to zero by construction nor dominated by
invalid/background/clipped values.

That load-bearing fact remains unverified. It is not demonstrably false, so a
KILL would overstate the evidence. Resolving it requires inspecting headers and
voxel distributions from the released archive (including the proposed
10-case, two-mask stability check); publication-level modality and registration
statements cannot substitute for that measurement.

```json
{"verdict": "UNVERIFIABLE", "evidence": "'Derivatives' include all modalities linearly co-registered to the NCCT space.", "source": "https://zenodo.org/records/16748089, Data structure", "note": "Common coordinates are verified, but the released maps' units, valid support, clipping/background semantics, and nontrivial residual require direct voxel inspection of the monolithic archive."}
```
