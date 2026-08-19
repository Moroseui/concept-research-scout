# Keystone screen — Idea 040

## Keystone as stated

> Automated centerlines in the released CTA recover MCA and basilar paths with sufficient continuity and tortuosity variation across 149 cases.

This is an empirical image-and-algorithm performance claim. It combines: (1) the
existence of CTA and vessel segmentations for the public cohort, (2) continuity
of the named arterial paths after centerline extraction, and (3) enough
between-case tortuosity variation for the proposed analysis.

## What was inspected

### Primary dataset publication

The full-text ISLES'24 dataset paper, DOI
[10.1148/ryai.250603](https://pubs.rsna.org/doi/full/10.1148/ryai.250603),
states in the section **Segmentation of the Circle of Willis for CTA Scans**:

> “Circle of Willis segmentations used a two-stage extended U-Net (15) for arterial localization and segmentation, trained on cross-registered CT and MR angiography data.”

The same section states:

> “A three-model ensemble generated pseudolabel segmentations as nonexpert reference standards (Fig 2C; see TopCoW summary [17]).”

Figure 2's caption identifies relevant labeled structures, including:

> “yellow is the left anterior cerebral artery, light blue is the right anterior cerebral artery, gray is the anterior communicating artery, red is the left internal carotid artery, purple is the left middle cerebral artery, brown is the right internal carotid artery, pink is the right middle cerebral artery, orange is the left posterior cerebral artery, green is the right posterior cerebral artery, medium blue is the basilar artery.”

The paper's Key Points gives the realized cohort size:

> “With 245 patients, including a public training set of 149 and a hidden test set of 96 patients, this dataset forms the foundation of the ISLES’24 at the Medical Image Computing and Computer Assisted Intervention 2024”

These statements verify the nearest checkable facts: CTA-derived Circle-of-Willis
pseudolabels were generated, the label scheme includes bilateral MCA and basilar
arteries, and the public cohort contains 149 patients. They do not report
per-artery centerline completion rates, tortuosity distributions, or repeatability.

### Official repository

The official repository README under **Data** provides the per-case acute-image
schema and includes:

> “+-- sub-strokecase0001_ses-0001_cta.nii.gz”

Source: [official ISLES'24 repository, `README.md`, Data](https://github.com/ezequieldlrosa/isles24/blob/main/README.md#data).

This verifies that CTA is an intended per-case input. The displayed repository
sample/schema does not contain a cohort-wide centerline quality report or a
tortuosity table.

## Residual-assumption check

The card verified the nearest checkable thing—availability of CTA and generated
arterial pseudolabels—but the load-bearing assumption is stronger: those
pseudolabels must yield continuous bilateral MCA and basilar centerlines in at
least 80% of a 30-case sample, and the resulting tortuosity measurement must be
stable (the card proposes ICC at least 0.9) and variable enough for conditional
analysis. Neither inspected primary source reports any of those measurements.
The publication calls the masks “nonexpert reference standards”; that is not
evidence of centerline continuity or tortuosity validity. Resolving the keystone
therefore requires the card's proposed image-level Stage 0 on the released
volumes, including a prespecified repeatability construction; documentation
inspection alone cannot establish it.

```json
{"verdict": "UNVERIFIABLE", "evidence": "A three-model ensemble generated pseudolabel segmentations as nonexpert reference standards (Fig 2C; see TopCoW summary [17]).", "source": "https://pubs.rsna.org/doi/full/10.1148/ryai.250603 — section ‘Segmentation of the Circle of Willis for CTA Scans’", "note": "CTA vessel labels and the 149-case public cohort are verified, but MCA/basilar centerline continuity, TI repeatability, and usable tortuosity variation require image-level Stage 0 measurement."}
```
