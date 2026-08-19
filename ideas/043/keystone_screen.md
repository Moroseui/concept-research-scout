# Keystone screen — Idea 043

## Keystone as stated

> The released NCCT preserves local quantitative HU contrast closely enough that automated regional GWR is stable under registration and resampling.

This exact claim is **not verified** by the inspected primary sources. The dataset paper confirms availability and processing, but does not report an HU-fidelity or atlas-GWR repeatability experiment. It says:

> “The dataset is released in raw and preprocessed formats, thus allowing participants to devise algorithms with diverse degrees of freedom. For anonymization purposes, all scans are defaced based on brain and face masks obtained with TotalSegmentator.”

Source: ISLES'24 challenge report, arXiv:2408.10966v2, Methods—Dataset, lines 103–107: https://arxiv.org/html/2408.10966v2#S3

The same section says:

> “Preprocessing of the images has been performed by linearly interpolating and registering all the imaging series to the NCCT scans.”

Source: ISLES'24 challenge report, arXiv:2408.10966v2, Methods—Dataset, line 106: https://arxiv.org/html/2408.10966v2#S3

Those statements establish that NCCT is released and is the registration reference. They do not establish cross-scanner quantitative-HU preservation, GWR stability under atlas registration, or the card's proposed ICC/rank-correlation thresholds. The newer primary dataset descriptor likewise documents a multi-vendor acquisition: “Imaging at two centers—University Hospital Munich and University Hospital Zurich—used various CT (Siemens Somatom Force, Somatom Xcite, Somatom AS+ and Philips Brilliance 64, Ingenuity) … systems,” without reporting a GWR repeatability test (Radiology: Artificial Intelligence, DOI 10.1148/ryai.250603, Image Acquisition): https://pubs.rsna.org/doi/10.1148/ryai.250603

## What was inspected

- The ISLES'24 challenge report's dataset-processing description and participant-input table (arXiv:2408.10966v2).
- The winning team's method report and its final-submission input/window table (arXiv:2505.18424v2).
- The published ISLES'24 dataset descriptor's acquisition and repository sections (DOI 10.1148/ryai.250603).

## Mandatory residual-assumption check

The card verified the nearest checkable fact—availability of released NCCT—but it still assumes something more basic: that the winning model whose preprocessing gain motivates the card actually consumed NCCT. That load-bearing assumption is demonstrably false.

The organizer-authored challenge report lists the winning Kurtlab model's inputs as:

> “Kurtlab | Image clipping, histogram equalization, min-max normalization | ✗ | CTA CBF CBV Tmax MTT | ✗ | nnU-Net (3D, residual encoders …)”

Source: ISLES'24 challenge report, arXiv:2408.10966v2, Table 1, row “Kurtlab,” lines 148–160: https://arxiv.org/html/2408.10966v2#S4.T1

Its prose description is equally explicit:

> “Inputs included CTA for structural information and vessel localization, along with CTP-derived CBF, CBV, MTT, and Tmax scans for perfusion information.”

Source: ISLES'24 challenge report, arXiv:2408.10966v2, §4.3 “Kurtlab (#1),” lines 161–166: https://arxiv.org/html/2408.10966v2#S4.SS3

The winning team's own paper corroborates this in its final-submission window table: the columns are “CTA (HU), CBF (mL/100g/min), CBV (mL/100g), MTT (s), Tmax (s),” with no NCCT input (arXiv:2505.18424v2, Table 1): https://arxiv.org/html/2505.18424v2#S3.T1

Therefore gray-to-white attenuation measured on NCCT cannot be a signal used by the winning model: NCCT was used to obtain a brain mask, but it was not an input channel to the final infarct network. The reported preprocessing gain cannot be attributed to an NCCT gray/white “brain window.” A newly trained NCCT-consuming model would be a different study object and would not repair this card's stated winner-linked premise.

```json
{"verdict":"KILL","kill_code":"EFFECT_UNREACHABLE","evidence":"Inputs included CTA for structural information and vessel localization, along with CTP-derived CBF, CBV, MTT, and Tmax scans for perfusion information.","source":"https://arxiv.org/html/2408.10966v2#S4.SS3 — §4.3, Kurtlab (#1), lines 161–166; corroborated by Table 1 row Kurtlab","note":"Wrong keystone: the winner did not ingest NCCT, so its output cannot use NCCT gray-to-white attenuation; HU/GWR stability itself remains unverified."}
```
