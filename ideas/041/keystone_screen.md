# Keystone screen — Idea 041

## Keystone as stated

> Higuchi temporal fractal dimension is computable and nondegenerate on the released raw ISLES'24 time series, and differs across relevant tissue states.

This is a compound prerequisite: the exact feature must have been computed on ISLES'24 voxelwise CTP series, and it must vary across the tissue classes that motivate the proposed probe.

## What was inspected

### Primary feature paper

I inspected the publisher record for Ichikawa, Kondo, and Yokoyama, *Time series-derived fractal dimension of CT perfusion in acute ischemic stroke: a promising marker for hypoperfused tissue quantification*, DOI `10.1007/s11548-025-03500-3`, and its PubMed record, PMID `40824507`. The card incorrectly attributes this work to “Lim et al.”

The paper's Methods abstract states:

> “Fractal analysis was applied to voxel-wise time-series data from both simulated phantom datasets and 149 CTP images from the publicly available Ischemic Stroke Lesion Segmentation (ISLES) 2024 dataset. FD was calculated using optimized parameters determined through the phantom study.”

Source: [PubMed PMID 40824507](https://pubmed.ncbi.nlm.nih.gov/40824507/), Abstract, Methods.

The Results abstract supplies the nondegeneracy and tissue-state evidence:

> “In the patient study, FD differed significantly across tissue types (p < 0.001). For penumbra versus normal classification, FD achieved an AUC of 0.732, outperforming CBF and CBV (p < 0.001). In core versus penumbra classification, FD showed the highest AUC of 0.641 among all metrics.”

Source: [publisher article](https://doi.org/10.1007/s11548-025-03500-3), Abstract, Results.

These are direct primary-source statements that the named measurement was computed voxelwise in all 149 public cases and was nonconstant across core, penumbra, and normal tissue. The stated keystone therefore holds at the level needed for this screen.

### Primary dataset paper

I inspected the ISLES'24 dataset paper, DOI `10.1148/ryai.250603`, to check what “released raw time series” means. It confirms both public availability and the relevant preprocessing:

> “Four-dimensional CT perfusion series underwent image co-registration and temporal resampling (1 frame/sec)”

Source: [Riedel et al., ISLES'24 dataset paper](https://doi.org/10.1148/ryai.250603), Materials and Methods, “Data Preprocessing.”

It also states:

> “The training dataset (n = 149) is publicly available under the CC BY-SA-NC 4.0 license via Zenodo”

Source: same paper, “Data Repository and Storage.”

Thus the public data contain usable four-dimensional CTP series, but “raw” must not be read as untouched native acquisition time series: the documented released series were co-registered and resampled to one frame per second.

## Residual-assumption check

The nearest checkable fact is stronger than mere computability: the feature paper reports voxelwise Higuchi FD on the exact 149-case public cohort and reports separation among the named tissue states. It does **not**, however, establish that the card's proposed implementation will exactly reproduce the published values. The publisher states, verbatim, “The code created during this study is available from the corresponding author upon reasonable request” (publisher article, “Data availability”); no public code artifact was identified in the inspected primary record. Consequently, the remaining assumption is recipe reproducibility from the full paper or author-supplied code, including the optimized frame-count-dependent `kmax` choice. That uncertainty does not negate the demonstrated existence and nondegeneracy of the measurement, but it must be tested before treating an independent implementation as the paper's exact feature.

The paper also establishes association with tissue classes, not that temporal FD is a distinct physiological signal rather than a proxy for flow or preprocessing. That is explicitly outside this keystone and remains a downstream identification problem.

```json
{"verdict": "PASS", "evidence": "Fractal analysis was applied to voxel-wise time-series data from both simulated phantom datasets and 149 CTP images from the publicly available Ischemic Stroke Lesion Segmentation (ISLES) 2024 dataset.", "source": "https://pubmed.ncbi.nlm.nih.gov/40824507/ — Abstract, Methods", "note": "Exact-cohort computability and tissue-state variation are verified; exact recipe reproduction and the card's mistaken Lim et al. attribution remain to be corrected downstream."}
```
