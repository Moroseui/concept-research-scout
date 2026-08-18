# Keystone screen — idea 032 (isles24-scout-003-c03, "The arterial network's spare route")

Screened 2026-08-18. Network sources fetched live; Bash networking is
approval-gated in this runner, so no mask file could be downloaded and
opened. Everything below is documentary primary-source evidence with
verbatim quotes; the one inspection that would settle the keystone
outright (reading label values out of a released `cow-msk.nii.gz`) is
explicitly flagged as not performed.

## The keystone as stated

> "The released multilabel Circle-of-Willis masks accurately distinguish
> communicating-artery branches and calibers in enough cases for graph
> edits to represent real anatomic variants rather than segmentation
> artifacts."

Decomposition into checkable layers:

1. Do multilabel CoW masks exist in the ISLES'24 release at all?
2. Does their label taxonomy separate communicating arteries (Acom,
   Pcom) as distinct classes?
3. Is their branch-level accuracy documented anywhere — especially on
   this cohort, which is an LVO cohort with occluded proximal vessels?

## What was inspected

### 1. Existence and generation method — VERIFIED

Zenodo record 16813698 ("ISLES'24 - A Real-World Longitudinal
Multimodal Stroke Dataset", the current dataset release,
https://zenodo.org/records/16813698), description, annotations list:

> "the multi-labeled Circle of Willis anatomy generated with an
> automatic algorithm over CTA (cow-msk.nii.gz)"

alongside

> "binary infarct masks derived from follow-up MRI (lesion-msk.nii.gz),
> large vessel occlusion binary masks derived from CTA
> (lvo-msk.nii.gz)"

Cohort: "149 acute ischemic stroke cases" (public training set).
License: "Creative Commons Attribution Non Commercial Share Alike 4.0
International". The same record instructs:

> "If you use the Circle of Willis masks, please ALSO cite: Yang, K.,
> Musio, F., Ma, Y., ... & Menze, B. (2024). Benchmarking the cow with
> the topcow challenge: Topology-aware anatomical segmentation of the
> circle of willis for cta and mra."

So the masks exist, are multilabel, are **automatic** (no manual
verification or QC statement appears anywhere in the record), and are
TopCoW-lineage. The community Hugging Face mirror
(https://huggingface.co/datasets/hugging-science/isles24-stroke,
README) shows the per-case file
`"sub-stroke0001_ses-01_space-ncct_cow-msk.nii.gz"` described as
`"Circle of Willis anatomy (multi-label, auto-generated from CTA)"` —
note the masks are shipped in **NCCT space**, i.e. resampled off the
native CTA grid, which matters for the card's centerline-radius
(caliber) measurement.

### 2. Label taxonomy — VERIFIED at the taxonomy level, NOT verified in the released files

The TopCoW paper the release instructs users to cite (Yang et al.,
PMC10793481, Section 2.2 "Data Annotation",
https://pmc.ncbi.nlm.nih.gov/articles/PMC10793481/):

> "There were 13 CoW vessel components for the multiclass segmentation
> annotation: left and right internal carotid artery (ICA), left and
> right anterior cerebral artery (ACA), left and right middle cerebral
> artery (MCA), anterior communicating artery (Acom), left and right
> posterior communicating artery (Pcom), left and right posterior
> cerebral artery (PCA), and basilar artery (BA)."

The taxonomy therefore separates Acom and both Pcoms — the exact edges
the idea needs to edit. **Caveat:** I could not open a released mask to
confirm the files actually carry all 13 labels (runner networking for
raw downloads is approval-gated; the official archive is a 99 GB
compressed release). This is the cheapest remaining direct check and
belongs at the top of Stage 0.

### 3. Branch-level accuracy on this cohort — NOT DOCUMENTED; adjacent evidence cuts both ways

No QC, accuracy, or manual-review statement for the ISLES'24 CoW masks
exists in the Zenodo record, the HF mirror, or the dataset paper
abstract (arXiv 2408.11142 mentions only "vessel occlusion masks from
acute CT angiography and delineated infarction masks in follow-up
MRI"; the Radiology AI dataset paper, DOI 10.1148/ryai.250603, is
paywalled from this runner — 403). Which specific automatic algorithm
produced the released masks is likewise undocumented in every source I
could reach.

Adjacent primary evidence from the updated TopCoW paper (arXiv
2312.17670v4, https://arxiv.org/html/2312.17670v4):

**Favorable.** ISLES'24 was used as an external CTA test set, and top
algorithms generalized to it:

> "Two external CTA test sets were from the TUM University Hospital in
> Germany of the public ISLES'24 challenge training set (ISLES) and
> various hospitals in China of the public Large IA Segmentation
> dataset (LargeIA)."

> "The top teams were able to generalize to external test sets for both
> modalities, with above 80% median Dice for all test sets."

**Adverse, and load-bearing.** The external validation cohort was
constructed by excluding exactly the cases this idea centers on:

> "For ISLES, we chose 26 CTA patients whose CoW were not occluded
> within the ROI."

So the only published fidelity evidence for TopCoW-class algorithms on
ISLES'24 CTA covers 26 of 149 cases, selected for a **non-occluded**
CoW. ISLES'24 is an LVO cohort; the card's intervention explicitly
"remove[s] the occluded edge", i.e. it needs the masks to be faithful
in and around occluded CoWs — the stratum with zero published
validation, which even the TopCoW annotators stepped around.
Additionally, communicating arteries are the weakest classes even for
expert humans (TopCoW Supplementary S6):

> "Many CoW component classes had Dice scores of around 90% or above,
> while R-Pcom, L-Pcom, Acom, and 3rd-A2 had slightly lower Dice at
> 76-89%."

and CTA is the harder modality: "CTA tended to have lower metric scores
even when both modalities had the same number of training data."

## Residual-assumption check (mandatory follow-up)

The card's stated keystone is, unusually, already the right load-bearing
fact — the card itself warns that "the Zenodo description's existence
claim ... is not evidence of branch-level fidelity." The screen confirms
that warning is apt: existence is verified, fidelity is nowhere
documented. But the screen surfaces one assumption **deeper** than the
stated keystone: the card implicitly assumes the fidelity question is
uniform across cases, when the published evidence is stratified in the
worst possible way — the only external validation excluded occluded-CoW
cases, and per-branch accuracy is weakest precisely for Acom/Pcom. The
Stage 0 census must therefore stratify mask QA by occlusion location
(CoW-involving vs. distal LVO) rather than sampling 30 masks uniformly;
a uniform sample could pass QA on the easy stratum while the edited,
occlusion-adjacent stratum is unusable. Second residual: masks are in
NCCT space, so centerline minimum radii are measured on a resampled
grid — caliber stability under the card's one-voxel perturbation test
must be assessed in that space, not native CTA.

## Verdict

Existence, multilabel format, automatic generation, license, and the
communicating-artery taxonomy are verified. The load-bearing accuracy
claim — branch-level fidelity of Acom/Pcom and calibers, in enough
cases, including occlusion-adjacent anatomy — is not documented in any
reachable primary source and can only be established by the card's own
Stage 0 inspection. Nothing found demonstrates the keystone false, so
this is not a KILL; it is an honest UNVERIFIABLE with the risk now
sharply localized: the occluded-CoW stratum has zero published
validation and the needed branches are the hardest classes.

```json
{"verdict": "UNVERIFIABLE", "evidence": "For ISLES, we chose 26 CTA patients whose CoW were not occluded within the ROI.", "source": "TopCoW paper v4, Section 2.4 External Multi-Center Test Data, https://arxiv.org/html/2312.17670v4 (mask existence: https://zenodo.org/records/16813698, 'the multi-labeled Circle of Willis anatomy generated with an automatic algorithm over CTA (cow-msk.nii.gz)')", "note": "Masks exist, multilabel, TopCoW-taxonomy, auto-generated with no documented QC; the only published fidelity evidence on ISLES'24 CTA excluded occluded-CoW cases, so Stage 0 mask QA must stratify by occlusion location."}
```
