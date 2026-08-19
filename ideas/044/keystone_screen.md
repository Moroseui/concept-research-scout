# Keystone screen — Idea 044

## Keystone as stated

> A nontrivial subset of admission NCCTs contains automatically separable remote chronic infarct cavities rather than only nonspecific low attenuation.

The card operationalizes “nontrivial” more strongly in its smallest decisive experiment: among the first 30 cases, at least 15 must have a stable remote cavity volume of at least 1 mL.

## What was inspected

1. **Primary dataset publication.** Riedel et al., *Radiology: Artificial Intelligence* (2026), DOI 10.1148/ryai.250603, full text, “Data Repository and Storage” and “Data Structure.” The paper establishes the inspectable cohort and admission imaging:

   > “The training dataset (n = 149) is publicly available under the CC BY-SA-NC 4.0 license via Zenodo.”

   Source: https://pubs.rsna.org/doi/full/10.1148/ryai.250603, “Data Repository and Storage,” lines 120–124 in the HTML full text.

   The paper’s Table 1 reports atrial fibrillation, hypertension, diabetes, dyslipidemia, medications, and premorbid mRS, but it does not report prior-stroke history, chronic infarct cavities, encephalomalacia, or a cavity census. Its lesion statistics concern the follow-up DWI final infarct reference, not pre-existing lesions on admission NCCT.

2. **Primary dataset release page.** The official Zenodo record describes each case as including:

   > “Admission imaging: non-contrast CT (NCCT), CT angiography (CTA), 4D CT perfusion (CTP) time series, and perfusion maps (Tmax, CBF, CBV, MTT).”

   Source: https://zenodo.org/records/16813698, “Description,” list of data included for each case.

   This verifies that the images needed for a census exist. It does not establish that any admission NCCT contains a remote chronic cavity, much less that at least 15 of 30 do or that a deterministic rule separates those cavities from mimics.

3. **Released clinical-data dictionary.** The 12.1-kB `clinical_data-description.xlsx` was downloaded from the official Zenodo record and inspected. Its history fields describe atrial fibrillation, hypertension, diabetes, hyperlipidemia, anticoagulation, statins, and platelet aggregation inhibitors; it provides no prior-stroke or chronic-infarct variable. The closest potentially relevant entry is:

   > “mRS premorbid as stated by patient or relatives.”

   Source: https://zenodo.org/records/16813698/files/clinical_data-description.xlsx?download=1, “Supplementary Table 1,” `mRS premorbid` row.

   Premorbid disability is not evidence of a chronic infarct cavity and cannot supply the missing prevalence or imaging-specificity fact.

## Residual-assumption check

The nearest checkable fact is only that 149 public training cases contain admission NCCT. The load-bearing assumption remains two-part and unverified: (1) sufficiently many NCCTs contain contralateral remote cavity-like tissue loss of the card’s required size, and (2) the proposed automatic morphology rule distinguishes that phenotype from ventricles, enlarged perivascular spaces, arachnoid or surgical cavities, and severe leukoaraiosis. Neither the dataset paper, its cohort tables, the release description, nor the released clinical dictionary provides a chronic-lesion annotation or census. Verifying the actual keystone therefore requires inspection of the released NCCT voxels (and the card’s separability criterion requires a defensible reference assessment); the primary documentation alone cannot settle it.

```json
{"verdict": "UNVERIFIABLE", "evidence": "The training dataset (n = 149) is publicly available under the CC BY-SA-NC 4.0 license via Zenodo.", "source": "https://pubs.rsna.org/doi/full/10.1148/ryai.250603 — Data Repository and Storage, lines 120–124", "note": "Primary sources verify an inspectable NCCT cohort but provide no chronic-cavity prevalence or separability evidence; an image-level census remains necessary."}
```
