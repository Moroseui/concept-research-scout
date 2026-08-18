# Keystone screen — idea 030 (isles24-scout-004-c08)

**Idea:** The ground truth was drawn on a swollen brain
**Screen date:** 2026-08-18
**Verdict: PASS** (keystone verified true from primary sources; one auxiliary
citation not independently re-quoted — see §4)

## 1. The keystone as stated on the card

> "Ground-truth masks were transferred to acute NCCT space via affine-only
> registration of follow-up MRI acquired in the edema window, so mass-effect
> deformation is unmodeled by construction."

Card status claimed: `INSPECTED_TRUE`. This screen re-inspected every leg
independently against primary sources, plus the mandatory
nearest-checkable-thing follow-up (§4).

The keystone decomposes into four checkable legs:
(a) the follow-up MRI → NCCT registration is affine (a linear map, which
cannot represent local mass-effect deformation);
(b) the follow-up MRI was acquired in a window overlapping post-stroke
space-occupying edema;
(c) the released ground-truth masks live in the NCCT-registered space, i.e.
they actually passed through that transform;
(d) the masks were drawn on the follow-up MRI (not natively on acute NCCT).

## 2. What was inspected, with verbatim evidence

### 2a. Registration to NCCT space is linear; MRI specifically is affine

Source: arXiv 2408.10966v1 (ISLES'24 dataset paper), Dataset section,
https://arxiv.org/html/2408.10966v1 (fetched 2026-08-18 by this screen):

> "Preprocessing of the images has been performed by linearly interpolating
> and registering all the imaging series to the NCCT scans."

> "Except for the MRI scans, where affine transformations are used, all
> remaining images are registered following rigid transformations."

> "Registration is performed using the Elastix [48] and NiftyReg [49]
> toolboxes."

Both quotes match the card's `keystone_evidence` character-for-character
where they overlap. An affine transform is global and linear; local
deformation from mass effect is outside its model class by definition. No
deformable step is mentioned anywhere in the preprocessing description.
Leg (a) verified.

### 2b. Follow-up acquisition window

Same source and section:

> "Follow-up imaging data was acquired 2 to 9 days later and included DWI
> and ADC."

Leg (b), timing half: verified. (The "edema window" characterization —
that this overlaps peak space-occupying edema — is assessed in §4.)

### 2c. Released masks are in NCCT space, produced by linear co-registration

Source: Zenodo record 16731717, "ISLES'24 - A Real-World Longitudinal
Multimodal Stroke Dataset", version v7, https://zenodo.org/records/16731717
(fetched 2026-08-18 by this screen):

> "Derivatives include all modalities linearly co-registered to the NCCT
> space."

and the release includes

> "binary infarct masks derived from follow-up MRI (lesion-msk.nii.gz)"

with the mask filename in the derivatives tree carrying the space tag
explicitly: `sub-strokecase0001_ses-02_space-ncct_lesion-msk.nii.gz`.
The follow-up scans likewise appear as `space-ncct_dwi.nii.gz` and
`space-ncct_adc.nii.gz`. Legs (c) verified: the deliverable ground truth is
the NCCT-space derivative, and the release itself states the co-registration
is linear.

### 2d. Masks were drawn on follow-up DWI, not natively on acute NCCT

Source: arXiv 2408.10966v1, Dataset section (same fetch):

> "Lesion masks are derived from DWI images using the ISLES'22 ensemble
> algorithm."

> "Quality control and correction of the lesion masks are performed when
> needed by medical students (TAB, HPM) supervised by two neuroradiologists
> (JSK, BW) with more than 10 years of experience."

Leg (d) verified: annotation provenance is DWI-side. The QC quote is the
anchor for the card's stated residual (see §3 — the paper does not say in
which space corrections were made).

## 3. The card's stated residual assumption

The card already names the right residual: whether any manual mask
correction happened *after* transfer to acute-NCCT space. The paper's QC
sentence (§2d) specifies who corrected but not in which space, and the
Zenodo page adds no methodological detail on the derivation. This screen
confirms the residual is genuinely open in the primary sources — and
confirms the card's handling is sound: the stage-1 census *measures* the
surviving halo rather than assuming its size, and "experts corrected in
acute space, halo is small" is listed as an anticipated, still-valuable
outcome. The keystone as stated does not require the halo to be large; it
requires the construction to be affine-only, which is documented.

## 4. Wrong-keystone check: what is the card still assuming?

**Q: if this card only verified the nearest checkable thing, what is it
still assuming?**

1. **That the released `space-ncct` mask is the product of the documented
   linear transform applied to the DWI-space mask, not an independent
   re-annotation in NCCT space.** No primary source describes a native
   acute-space annotation pass, and the release explicitly labels all
   derivatives as "linearly co-registered." An undocumented manual edit in
   NCCT space is the only escape hatch, and that is exactly the residual in
   §3, measured (not assumed) by the design. Not a wrong-keystone error.

2. **That the NCCT is acute (pre-swelling), so displacement between the
   sessions is real.** The dataset's own structure states acute imaging
   (ses-01: NCCT/CTA/CTP at presentation) versus follow-up (ses-02, "2 to 9
   days later"). Verified by construction of the release.

3. **That the 2–9-day window overlaps peak space-occupying edema.** The
   2–9-day acquisition window is verbatim-verified (§2b). The specific
   "3–5-day peak" literature anchor (Stroke 2014, DOI
   10.1161/STROKEAHA.114.006884; Stroke 2023, DOI
   10.1161/STROKEAHA.123.045941) could NOT be independently re-quoted by
   this screen: ahajournals.org returns HTTP 403 to this environment, and
   the PubMed abstract of the 2014 paper (PMID 25336512, "Brain Edema
   Predicts Outcome After Nonlacunar Ischemic Stroke") confirms serial-MRI
   swelling measurement but does not state the day range in the abstract.
   Classification: **source-supported interpretation, not re-verified
   verbatim here.** This is auxiliary, not load-bearing: the keystone's
   falsifiable core is the affine-only transfer of masks derived from
   follow-up MRI acquired days after stroke; post-stroke edema evolving
   over the first week is settled physiology, and any first-week peak
   placement is inside the verified 2–9-day window. If critique wants the
   day-range quote on record, it needs a non-AHA mirror of either citation.

4. **That "affine" in the paper means affine for the transform actually
   applied to the *masks*, not just the images.** The masks are derived
   from DWI (§2d) and released in `space-ncct` (§2c); a mask can only reach
   NCCT space via some transform, and the only documented MRI→NCCT
   transform is the affine one. The alternative (a second, undocumented,
   deformable mask-transfer pipeline alongside the documented linear one)
   has no support in either source and would contradict the release's own
   "linearly co-registered" description.

No load-bearing assumption differs from the stated keystone. The stated
keystone is the right keystone, and it is documented in two independent
primary sources (the dataset paper and the data release).

## 5. Verdict

All four legs of the keystone are verbatim-verified. The single genuinely
open question (post-transfer manual correction) is the card's declared
residual, and the design measures it rather than resting on it.

```json
{"verdict": "PASS", "evidence": "Except for the MRI scans, where affine transformations are used, all remaining images are registered following rigid transformations.", "source": "https://arxiv.org/html/2408.10966v1, Dataset section; corroborated by https://zenodo.org/records/16731717 (v7): 'Derivatives include all modalities linearly co-registered to the NCCT space', mask released as sub-strokecase0001_ses-02_space-ncct_lesion-msk.nii.gz", "note": "Affine-only MRI-to-NCCT transfer of DWI-derived masks acquired 2-9 days post-stroke is documented in both the paper and the release; the only escape hatch (undocumented manual correction in acute space) is the card's declared residual, measured by stage 1."}
```
