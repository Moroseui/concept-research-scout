# Keystone screen — Idea 042: Delay is not dispersion

## Keystone as stated

> The released raw CTP captures baseline, arterial peak, and washout sufficiently to estimate delay-independent second and third moments without truncation, and dispersion has within-delay variation in affected tissue.

This is a compound empirical prerequisite. It requires (1) adequate temporal support in the released cases and (2) measurable dispersion variation after conditioning on delay. Merely establishing that a four-dimensional CTP file exists is not enough.

## What was inspected

### Primary dataset paper

The published ISLES'24 dataset paper confirms the modality and the preprocessing cadence. In **Materials and Methods → Data Preprocessing**, it states:

> “Four-dimensional CT perfusion series underwent image co-registration and temporal resampling (1 frame/sec); perfusion maps (cerebral blood flow, cerebral blood volume, mean transit time, and time-to-maximum) were derived using the clinical, U.S. Food and Drug Administration–cleared software icobrain cva (version 1.5.0, icometrix).”

Source: Riedel et al., *Radiology: Artificial Intelligence* (2026), DOI 10.1148/ryai.250603, [HTML, Data Preprocessing, lines 102–105](https://pubs.rsna.org/doi/10.1148/ryai.250603).

The same paper's **Image Acquisition** section names several scanners but gives no CTP acquisition duration, number of temporal frames, precontrast-frame count, injection timing, or washout/truncation statistic:

> “Imaging at two centers—University Hospital Munich and University Hospital Zurich—used various CT (Siemens Somatom Force, Somatom Xcite, Somatom AS+ and Philips Brilliance 64, Ingenuity) and MRI (3-T Philips Achieva, Ingenia; 3-T Siemens Verio, Trio and 1.5-T Avanto) systems.”

Source: same paper, [Image Acquisition, lines 94–100](https://pubs.rsna.org/doi/10.1148/ryai.250603).

### Primary dataset record/schema

The creator-authored dataset record confirms that the per-case release includes a CTP time-series file:

> “Admission imaging: non-contrast CT (NCCT), CT angiography (CTA), 4D CT perfusion (CTP) time series, and perfusion maps (Tmax, CBF, CBV, MTT).”

It also shows the concrete path `raw_data/.../sub-strokecase0001_ses-0001_ctp.nii.gz`, but publishes no temporal dimension or per-case timing table.

Source: official institutional dataset record for Zenodo DOI 10.5281/zenodo.16731717, [Description and Data structure, lines 35–46](https://research.tue.nl/en/datasets/isles24-a-real-world-longitudinal-multimodal-stroke-dataset/).

## Residual-assumption check

The nearest checkable fact is therefore **raw 4D CTP exists and a processed series was resampled to 1 frame/sec**. The card is still assuming that the series begins early enough, ends late enough, and has enough uncontaminated samples to support stable second and especially third central moments. A sampling interval does not determine acquisition duration or bolus coverage. Neither inspected primary source reports the card's proposed gates: five pre-arrival frames, arterial peak at least five frames before the end, venous downslope to at most 30% of peak, or passage of those gates in at least 90% of 20 cases.

The second half of the stated keystone—within-delay dispersion variation in affected tissue—is also a property of the voxel data, not established by the paper or schema. It requires direct case-level inspection. No primary-source statement found supplies that measurement.

The load-bearing assumption was correctly named in the card, but it was not verified by the nearest available release documentation. At this screen price, the evidence supports neither PASS nor KILL: the raw archive must be inspected case by case.

```json
{"verdict":"UNVERIFIABLE","evidence":"Four-dimensional CT perfusion series underwent image co-registration and temporal resampling (1 frame/sec); perfusion maps (cerebral blood flow, cerebral blood volume, mean transit time, and time-to-maximum) were derived using the clinical, U.S. Food and Drug Administration–cleared software icobrain cva (version 1.5.0, icometrix).","source":"https://pubs.rsna.org/doi/10.1148/ryai.250603 — Materials and Methods, Data Preprocessing (HTML lines 102–105)","note":"The sources verify raw 4D CTP and cadence, but not per-case baseline/peak/washout coverage or within-delay dispersion variation; direct archive inspection is required."}
```
