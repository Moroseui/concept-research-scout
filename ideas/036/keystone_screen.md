# Keystone screen — idea 036 (Does the model bring a vascular map to the scan?)

Screened 2026-08-18 against primary sources, inspected first-hand where
possible: the arterial-territories atlas repository, cloned and read
(github.com/Chin-Fu-Liu/Arterial_Atlas, commit
`fbeb3fe70b6fb8185244d02f9c6b6e07c13235e0`); the official ISLES'24
challenge repository, cloned and read (github.com/ezequieldlrosa/isles24,
commit `94b34863a099a8aeae6cf9b989c78ff2c767b80e`); the winning team's
released inference code, cloned and read (github.com/KurtLabUW/ISLES2024,
commit `bb6c00c8a58cb57a5a33c133c02885776673d230`); the challenge results
paper (arXiv 2408.10966, abstract); the winning team's method paper
(arXiv 2505.18424v1); the dataset paper (arXiv 2408.11142, abstract); and
the Zenodo challenge record (zenodo.org/records/10991145).

## The keystone as stated

> "A frozen trained final-infarct model with continuous per-voxel output
> and non-trivial held-out performance exists, and atlas-to-CT
> registration is accurate to a few millimeters so border-straddling
> matched pairs are real."

Two components: (K1) the model, (K2) registration accuracy. The card's
own `keystone_residual_assumption` concedes that the verified-nearby fact
is only "the atlas is public and covers territories hierarchically" and
that K1/K2 are stage-0 gates. This screen verified everything
document-checkable in that chain and applied the mandatory wrong-keystone
follow-up (section 4).

## What was inspected

### 1. The matching channels exist and share one space (VERIFIED TRUE)

The design needs voxel pairs matched on "Tmax/CBF/CBV/MTT/NCCT-HU" in a
single coordinate frame. The official challenge repository's README
documents the per-case release, including a `derivatives` tree with all
four perfusion maps resampled into NCCT space:

> ```
> +-- derivatives
> |   +-- sub-strokecase0001
> |       +-- ses-0001
> |           +-- perfusion-maps
> |               +-- sub-strokecase0001_ses-0001_space-ncct_tmax.nii.gz
> |               +-- sub-strokecase0001_ses-0001_space-ncct_mtt.nii.gz
> |               +-- sub-strokecase0001_ses-0001_space-ncct_cbf.nii.gz
> |               +-- sub-strokecase0001_ses-0001_space-ncct_cbv.nii.gz
> ```
> — github.com/ezequieldlrosa/isles24 commit `94b34863`, README.md, "Data"

The repo also ships sample derivative files matching this schema exactly
(`utils/data/derivatives/sub-stroke0014/ses-01/perfusion-maps/
sub-stroke0014_ses-01_space-ncct_{cbf,cbv,mtt,tmax}.nii.gz`), with the
follow-up lesion mask in `ses-02`. Raw NCCT, CTA, and 4D CTP are in
`rawdata`. License per the same README: "The dataset is released under
the CC BY-NC (Attribution-NonCommercial) license." The dataset paper's
abstract confirms modality families and ground-truth provenance:
"(sub-)acute CT imaging with angiography and perfusion, follow-up MRI
after 2-9 days" with "delineated infarction masks in follow-up MRI"
(arXiv 2408.11142, abstract). So the five matching channels are released,
co-registered to the NCCT frame, and one atlas-to-NCCT transform per case
serves both the border geometry and the matching. Cohort per the results
paper abstract: "a train set of 150 cases" and "the hidden test set of 98
cases" (arXiv 2408.10966) — the card's "149 public multimodal cases" is
one off from the documented 150; immaterial here, flag for critique.

### 2. The atlas is real, public, hierarchical, deformable-format (VERIFIED TRUE)

From the cloned repository README:

> "This deformable 3D digital atlas allows automatic and reproducible
> exploration of large-scaled data." … "ArterialAtlas.nii: Image defining
> 30 arterial territories and ventricles." … "ArterialAtlas_level2.nii:
> The combination of ArterialAtlas.nii parcels in 4 major territories
> (ACA, MCA, PCA, VB)." … "Images in "Atlas" folder are in MNI
> coordinates in 181x217x181 mm^3"
> — github.com/Chin-Fu-Liu/Arterial_Atlas commit `fbeb3fe7`, README.md

The label table (`data/ArterialAtlasLables.txt`) lists all 30 level-1
territories with a level-2 rollup; the NIfTI files are present in the
clone (14.2 MB each). LICENSE is CC Attribution-ShareAlike 4.0. Two
facts the card understates: the repo contains **label maps only, no
registration template** — the atlas is MRI-derived and lives in MNI
space, so mapping it onto a patient NCCT requires a template-mediated,
**cross-modal** registration path (e.g. NCCT→CT-template→MNI), not a
direct "standard deformable registration" of atlas to CT. Probability
maps and border-zone ratio maps exist but are hosted separately on NITRC
per the README.

### 3. K1 — a frozen model with continuous per-voxel output (VERIFIED TRUE at document level, with a performance-ceiling caveat)

The card plans to train its own nnU-Net, but a public frozen
challenge-winning model also exists (first established by the idea-035
screen; re-verified first-hand here). The KurtLab repo's
`model weights.txt` contains a publicly resolving Google Drive link
(`https://drive.google.com/drive/folders/1ZoTjTzbMT5EHo5KJZp6CL2U8qBLMZbXu`),
and `inference.py:136-138` runs
`nnUNet.nnunetv2.inference.predict_from_raw_data -d 150 ... -p
nnUNetResEncUNetLPlans`. The vendored nnU-Net exposes continuous
per-voxel output by flag: `save_probabilities: bool = False`
(`nnUNet/nnunetv2/inference/predict_from_raw_data.py:165`) — the deployed
container writes a binary mask, but softmax probability export is
available from the same frozen weights by construction. Weights-file
integrity was not download-verified at this stage (same standing caveat
as the idea-035 screen; an idea-004-class load probe applies).

"Non-trivial held-out performance" now has a documented ceiling. The
results paper abstract:

> "a multimodal nnU-Net-based architecture" achieved "a Dice score of
> 0.285 (+/- 0.213) and an absolute volume difference of 21.2 (+/- 37.2)
> mL" — arXiv 2408.10966, abstract

and the authors state the results "underline the significant challenges
posed by this task." The best model in the challenge scores Dice ~0.29
with per-case standard deviation nearly as large as the mean; a locally
reproduced single nnU-Net trained on the 150 public cases will sit at or
below this. Not a kill — the keystone asks for "non-trivial," and the
discontinuity readout needs continuous output, not high Dice — but the
"non-trivial performance" bar MUST be prespecified numerically before
training, or it will be set post hoc around whatever emerges. If the
public frozen winner is used instead, note from its inspected
`inference.py:121-125`: it consumes cbf/cbv/mtt/tmax/CTA and **not
NCCT** (idea-035 screen finding, re-confirmed) — harmless to the matching
(matching covariates need not be model inputs) but the atlas transform
must land in that model's output space, and its deployed preprocessing
applies per-volume windowing plus global histogram equalization
(`preprocessing.py:21`), no skull-stripping.

### 4. K2 — few-mm registration on released stroke CT (UNVERIFIABLE at screen prices)

No document can settle registration accuracy on this data; it is an
empirical stage-0 gate, and the card already routes it there with a
perturbation-sensitivity analysis. Contributing unknowns recorded: the
defacing/skull status of the released NCCT is stated nowhere I fetched
(dataset paper abstract, Zenodo record, challenge README are all silent);
and the cross-modal MNI-to-CT path from section 2 is the specific
mechanism the QA census must exercise. Nothing found suggests
infeasibility; nothing found demonstrates the few-mm claim.

## Residual assumption check (mandatory follow-up)

If this card only verified the nearest checkable thing, it is still
assuming: (a) K2 wholesale — untestable from documents, correctly
gated at stage 0; (b) that "non-trivial performance" is meaningful under
a Dice-0.285 task ceiling — the bar must be frozen before training;
(c) that enough border-straddling voxel pairs survive five-channel
matching — a count the card already assigns to stage 0; (d) that the
cross-modal template-mediated registration path (not named in the card)
is the "standard deformable registration" it invokes. The card's stated
keystone and its actual load-bearing assumptions coincide — no
wrong-keystone substitution found; the checkable enabling chain
(channels, common space, atlas, frozen model, continuous output) is
verified true end to end.

## Verdict

Everything document-checkable is verified true, first-hand where
possible; the one unverifiable component (K2) is an empirical stage-0
gate the card itself prespecifies, and nothing inspected makes any
component demonstrably false.

```json
{"verdict": "PASS", "evidence": "a multimodal nnU-Net-based architecture ... a Dice score of 0.285 (+/- 0.213) and an absolute volume difference of 21.2 (+/- 37.2) mL", "source": "arXiv 2408.10966 abstract (https://arxiv.org/abs/2408.10966); frozen winner re-verified at github.com/KurtLabUW/ISLES2024 commit bb6c00c8 (weights link in 'model weights.txt', save_probabilities in vendored nnUNet predict_from_raw_data.py:165); matching channels verified at github.com/ezequieldlrosa/isles24 commit 94b34863 README 'space-ncct_{tmax,mtt,cbf,cbv}' derivatives", "note": "All checkable enabling facts true (atlas public/hierarchical/MNI, five evidence channels co-registered to NCCT space, public frozen winner with continuous-output flag); registration accuracy stays an honest stage-0 gate, and the non-trivial-performance bar must be prespecified against the Dice-0.285 challenge ceiling."}
```
