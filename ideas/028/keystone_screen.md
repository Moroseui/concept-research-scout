# Keystone screen — idea 028 (isles24-scout-003-c04, "The blood's grayscale oxygen gauge")

Screen date: 2026-08-18. Stage: keystone (pre-critique gate).

## Keystone as stated on the card

> "Released NCCT retains quantitative intravascular HU and contains enough
> artifact-free dural-sinus voxels for sinus attenuation to rank hematocrit
> rather than reconstruction/site."

Decomposed, this is three claims of different kinds:

- **K-a (document-checkable):** the ISLES'24 release contains NCCT volumes in
  which dural-sinus voxels physically survive with their acquired HU values —
  i.e., the released NCCT is not skull-stripped, brain-masked, intensity-
  windowed, or otherwise processed in a way that destroys intravascular HU.
- **K-b (document-checkable in part):** nothing in the documented pipeline
  (registration, resampling, defacing) is declared to alter NCCT intensities.
- **K-c (empirical, not document-checkable):** the surviving sinus voxels are
  numerous and artifact-free enough that sinus attenuation ranks hematocrit
  rather than reconstruction/site. This is exactly what the card's own Stage 0
  gates (≥120 measurable sinuses, between-site SMD < 0.5, erosion ICC ≥ 0.9)
  are prespecified to measure. No document can settle it.

## What I inspected

**1. The official Zenodo data release (the actual hosting page).**
Zenodo record 17652035, "ISLES'24 - A Real-World Longitudinal Multimodal
Stroke Dataset", open access, CC BY-NC-SA 4.0, single file `train.7z`
(99,022,114,670 bytes, MD5 `4959a5dd2438d53e3c86d6858484e781`), 149 training
cases. The description states, verbatim (confirmed via two independent
fetches of https://zenodo.org/records/17652035 and the API endpoint
https://zenodo.org/api/records/17652035):

> "'Raw_data' refers to the 'raw' acquired scans, which are released in their
> original space, just defaced."

and

> "'Derivatives' include all modalities linearly co-registered to the NCCT
> space."

Raw NCCT is released in original acquisition space with defacing as the only
stated modification. The derivatives are registered **to** NCCT space, i.e.,
the NCCT itself is the fixed reference and is not resampled in the
derivatives either.

**2. The official challenge repository (cloned and read).**
https://github.com/ezequieldlrosa/isles24, `README.md` lines 12–22: the
documented BIDS tree places the NCCT under the raw branch:

```
+-- rawdata
|   +-- sub-strokecase0001
|       +-- ses-0001
|           ...
|           +-- sub-strokecase0001_ses-0001_ncct.nii.gz
```

The repo's bundled sample data contains only perfusion maps and lesion masks
("Given data size constrains, only a few images for the sample case are
uploaded", README.md line 55), so no NCCT voxels could be inspected directly
without the 99 GB download.

**3. The challenge organizers' paper (arXiv 2408.10966, Methods/Dataset).**

> "The dataset is released in raw and preprocessed formats, thus allowing
> participants to devise algorithms with diverse degrees of freedom."

> "all scans are defaced based on brain and face masks obtained with
> TotalSegmentator"

No intensity windowing, clipping, or normalization of NCCT is documented
anywhere in the release description or the paper.

**4. Independent confirmation that released scans retain the skull (and
therefore the peri-cranial anatomy where the sinuses sit).**
The ISLES'24 winning team's paper (arXiv 2505.18424, Methods 3.2) describes
the released data they received:

> "The scans in the ISLES'24 brain imaging dataset contain non-brain
> structures such as the skull and background artifacts, which can hinder
> model training"

and they had to apply their own brain extraction:

> "We applied SynthStrip on the non-contrast CT (NCCT) scans to obtain a
> brain masks."

This is third-party, hands-on-the-data confirmation that the released NCCT is
**not** skull-stripped — the failure mode that would have deleted the
superior sagittal sinus (which lies against the inner table) and killed the
idea at this screen.

## Mandatory follow-up: what is the card still assuming?

"If this card only verified the nearest checkable thing, what is it still
assuming?" The nearest checkable thing was data availability; the residuals:

1. **Defacing does not clip the sinus region.** Defacing is face removal;
   the superior sagittal/straight sinuses are parieto-occipital and remote
   from any face mask. This is a source-supported inference from the stated
   method ("brain and face masks obtained with TotalSegmentator"), not a
   voxel-level verification. First contact with the actual volumes in Stage 0
   must confirm the vertex and torcular are intact.
2. **DICOM→NIfTI conversion preserved calibrated HU.** Standard and stated
   nowhere to be violated ("original space, just defaced"), but numeric
   fidelity per scanner is unverified until inspected. The card already
   lists "quantitative sinus HU fidelity" as unverified.
3. **K-c (sinus HU ranks hematocrit here, not reconstruction/site).**
   Untestable from documents by construction; the card's Stage 0 gates are
   the prespecified test and must remain mandatory.
4. **No hematocrit/hemoglobin field is documented in the released clinical
   tables** (documented variables: "demographics, patient history, admission
   NIHSS, 3-month functional outcome (mRS), etc."; laboratory variables carry
   ±5% de-identification noise per arXiv 2408.10966). The card is already
   consistent with this — it claims rung 1 (use of sinus HU) and defers
   hematocrit attribution to an external cohort — so this is a confirmation
   of the card's stated limits, not a new gap. If a hematocrit column does
   turn up in the phenotype CSVs, note the ±5% noise before any use.

The stated keystone and the load-bearing assumption coincide here: the study
is impossible only if sinus voxels or their HU values are absent from the
release. That is the fact verified above. No wrong-keystone substitution
found.

## Verdict

The document-checkable core (K-a, K-b) is verified with verbatim primary-
source evidence; the empirical tail (K-c) is precisely what the card's own
Stage 0 is designed to answer and cannot be decided at screen prices.
Nothing inspected falsifies the keystone.

```json
{"verdict": "PASS", "evidence": "'Raw_data' refers to the 'raw' acquired scans, which are released in their original space, just defaced.", "source": "https://zenodo.org/records/17652035 (ISLES'24 training-set release, description field; corroborated by github.com/ezequieldlrosa/isles24 README.md lines 12-22 rawdata/*_ncct.nii.gz and arXiv 2505.18424 Methods 3.2 'contain non-brain structures such as the skull')", "note": "Raw, defaced-only, non-skull-stripped NCCT for 149 cases is publicly released; sinus-voxel survival of defacing and HU fidelity remain Stage 0 first checks, and the rank-hematocrit clause is empirical by construction (card's Stage 0 gates are the test)."}
```
