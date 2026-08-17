# Keystone screen

## Keystone as stated

> Per-case CBV, CBF, MTT, and Tmax maps coexist co-registered in a common (NCCT) space so mirror indices and joint channel edits run automatically on every case.

## What I inspected

I inspected the official ISLES'24 GitHub repository's data schema and the official Zenodo release record for the public training archive, rather than relying on an abstract or search result.

The official Zenodo record states that the release contains 149 training cases and then makes the per-case completeness claim explicitly:

> “For each case, the following data are included: Admission imaging: non-contrast CT (NCCT), CT angiography (CTA), 4D CT perfusion (CTP) time series, and perfusion maps (Tmax, CBF, CBV, MTT).”

Source: https://zenodo.org/records/16731717, **Description**, opening paragraph and first bullet under the case contents (record metadata inspected through https://zenodo.org/api/records/16731717 on 2026-08-17).

The same record defines the derivative-space relationship:

> “'Derivatives' include all modalities linearly co-registered to the NCCT space.”

Source: https://zenodo.org/records/16731717, **Data structure** paragraph.

Its displayed derivative schema places all four files under the same subject, acute session, and `perfusion-maps` directory, with `space-ncct` in every filename:

> “sub-strokecase0001_ses-0001_space-ncct_tmax.nii.gz”  
> “sub-strokecase0001_ses-0001_space-ncct_mtt.nii.gz”  
> “sub-strokecase0001_ses-0001_space-ncct_cbf.nii.gz”  
> “sub-strokecase0001_ses-0001_space-ncct_cbv.nii.gz”

Source: https://zenodo.org/records/16731717, **Data structure**, `derivatives/sub-strokecase0001/ses-0001/perfusion-maps/` listing. The same four-file layout is independently reproduced in the official repository at https://github.com/ezequieldlrosa/isles24/blob/main/README.md, lines 26–35.

These statements jointly verify the stated prerequisite: the four named maps coexist per case and derivative versions are in NCCT space. This is schema-level inspection of the official release, not a census of the headers inside the 99 GB `train.7z` archive.

## Residual-assumption check

**Mandatory question:** If this card only verified the nearest checkable thing, what is it still assuming?

The nearest fact would have been merely that the release contains four map *types*. The additional load-bearing facts are that they coexist for each case and that the derivative copies share NCCT physical space. The official release description explicitly verifies both, so the card did not stop at the nearest fact.

One narrower implementation assumption remains: “co-registered to NCCT space” does not verbatim promise byte-identical NIfTI dimensions, voxel sizes, or affine matrices across the four files. That does not overturn the stated keystone because common NCCT physical space permits deterministic resampling before voxelwise measurement or editing. A header census should nevertheless gate later work; missing files or irreconcilable affine/coverage differences would be a release-integrity exception, not evidence currently contradicting the official per-case schema.

The card also assumes that mirror estimation will be reliable and that the map values have usable joint support and scaling. Those are explicitly listed Stage 0 validity gates. They affect interpretability of the proposed experiment but are not substitutes for the present data-existence/co-registration keystone.

```json
{"verdict": "PASS", "evidence": "For each case, the following data are included: Admission imaging: non-contrast CT (NCCT), CT angiography (CTA), 4D CT perfusion (CTP) time series, and perfusion maps (Tmax, CBF, CBV, MTT).", "source": "https://zenodo.org/records/16731717 — Description, first case-contents bullet; paired with Data structure statement that derivatives include all modalities linearly co-registered to NCCT space", "note": "Official release schema verifies per-case coexistence and common NCCT space; exact NIfTI grid/header compatibility remains a cheap Stage 0 census."}
```
