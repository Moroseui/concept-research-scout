# Keystone screen — idea 035 (The skull is a fixed-volume pressure vessel)

Screened 2026-08-18 against primary sources: the ISLES'24 challenge paper
(arXiv 2408.10966v2), the winning team's method paper (arXiv 2505.18424v1),
and — decisively — the winning team's released inference code, cloned and
read directly (github.com/KurtLabUW/ISLES2024, commit
`bb6c00c8a58cb57a5a33c133c02885776673d230`).

## The keystone as stated

> "Small CSF-boundary edits can alter measured reserve while keeping every
> parenchymal model input bit-identical outside a narrow CSF boundary and
> passing anatomical-realism gates; the frozen model's receptive field must
> connect those spaces to the threatened territory."

Two components: (K1) edit feasibility with parenchymal bit-identity, and
(K2) receptive-field coverage of a frozen model. Both presuppose an
unstated third fact — that a frozen ISLES'24 final-infarct model is
publicly obtainable and that its inputs contain the CSF spaces the card
wants to edit. Per the mandatory follow-up, that unstated fact is the
truly load-bearing one, and it is what this screen inspected.

## What was inspected

### 1. A frozen winning model exists and is public (VERIFIED TRUE)

The challenge paper names the top-3 teams' code (section 4.3, "Solutions
employed by the top-3 teams"):

> "The algorithm employs a full-resolution 3D large residual encoder U-Net
> architecture based on nnU-Net (ResEnc L variant). Inputs included CTA for
> structural information and vessel localization, along with CTP-derived
> CBF, CBV, MTT, and Tmax scans for perfusion information."
> — arXiv 2408.10966v2, section 4.3 (Kurtlab), which adds: "The code is
> available at https://github.com/KurtLabUW/ISLES2024."

The repo's `README.md` instructs: "Download the model weights from the
'model weights.txt' file" — that file contains a Google Drive link
(`https://drive.google.com/drive/folders/1ZoTjTzbMT5EHo5KJZp6CL2U8qBLMZbXu`),
which resolves publicly and contains a folder
`Dataset150_ISLES2024_processedv3` (modified Sep 4, 2024), matching the
dataset id in the inference command (`inference.py:138`, `-d 150 ...
-p nnUNetResEncUNetLPlans`). Runner-up code is also public (AMC-Axolotls:
github.com/Mahsa0M/isles2024_docker; Ninjas:
github.com/jaymoz/ISLES-Challenge-2024). Weights-file integrity inside the
Drive folder was not download-verified at this stage.

### 2. NCCT is NOT an input to the winning model (VERIFIED — wrong-keystone finding)

The card measures reserve on NCCT ("Segment ventricles and sulcal CSF
automatically on NCCT") and implicitly assumes the model sees that image.
The deployed winner consumes exactly five channels, none of them NCCT.
`inference.py:121-125` (`nnunet_dataset_conversion`):

```python
move_file(glob(str(join(data_path, "preprocessed-cbf-map", "*.mha")))[0], "/tmp/raw/isles0000_0000.nii.gz")
move_file(glob(str(join(data_path, "preprocessed-cbv-map", "*.mha")))[0], "/tmp/raw/isles0000_0001.nii.gz")
move_file(glob(str(join(data_path, "preprocessed-mtt-map", "*.mha")))[0], "/tmp/raw/isles0000_0002.nii.gz")
move_file(glob(str(join(data_path, "preprocessed-tmax-map", "*.mha")))[0], "/tmp/raw/isles0000_0003.nii.gz")
move_file(glob(str(join(data_path, "preprocessed-CT-angiography", "*.mha")))[0], "/tmp/raw/isles0000_0004.nii.gz")
```

The NCCT loader exists in the same file only as commented-out template code
(`inference.py:45-47`). Consequence: visible CSF reserve can reach this
model only through the preprocessed CTA channel (CSF is hypodense on CTA)
and through near-zero CSF regions of the four perfusion maps. The card's
edit target must move from NCCT to the CTA channel; NCCT remains available
in the dataset for computing the stratification covariate outside the
model. This is a material design correction, not a kill: the card's
question is model-generic ("an ISLES'24 model") and the mechanism (visible
reserve as geometric prior) remains testable on the frozen winner.

### 3. Parenchymal bit-identity collides with two global intensity transforms (K1, PARTIALLY FALSE AS STATED, salvageable)

The winner's deployed preprocessing applies per-volume global histogram
equalization to every channel. `preprocessing.py:21`:

```python
equalized_data = exposure.equalize_hist(data_normalized, mask=(data_normalized > 0.0001))
```

with per-channel windows `'0000': (0, 35), '0001': (0, 10), '0002':
(0, 20), '0003': (0, 7), '0004': (0, 90)` (`preprocessing.py:60-66`).
Histogram equalization is a global transform: editing CSF voxels changes
the volume's histogram and therefore shifts post-equalization values at
every parenchymal voxel. In addition, nnU-Net applies per-image
normalization at inference; the channel names (`cbf, cbv, mtt, tmax, cta`,
`Dataset139_ISLES24.py:47`) are not in
`channel_name_to_normalization_mapping`, so they take the default:

> "If it is not found, use the default (ZScoreNormalization)"
> — `nnUNet/nnunetv2/preprocessing/normalization/map_channel_name_to_normalization.py:17-19`

So the keystone's "every parenchymal model input bit-identical" is FALSE
for edits made in raw image space. It remains achievable by construction
if edits are injected downstream of equalization with normalization
constants frozen from the unedited case — the exact maneuver this program
ratified for idea 021 (decision ledger, 2026-08-17). The cost is that the
"anatomical realism" gate must then be defined in equalized/normalized
space, which the critique stage should weigh.

### 4. Receptive field (K2, PLAUSIBLE, not yet verified)

The winning paper states:

> "For our submission, we used the 'large' 3D residual encoder nnU-Net with
> a [56, 320, 256] patch size" — arXiv 2505.18424v1, methods.

An in-plane patch of 320x256 voxels spans essentially the whole brain
in-plane, so ventricles/sulci and the threatened territory co-occur within
a patch in-plane; the 56-slice through-plane extent leaves distant (e.g.
vertex) sulcal reserve outside a basal lesion's patch. The effective
receptive field of the ResEnc-L network within that patch was not computed
here; it is exactly computable from the released plans file once weights
are downloaded. Not falsified; pinned as the Stage 0 check the card
already specifies.

## Residual assumption check

What the card is still assuming after this screen: (a) CSF reserve is
discernible to the model through windowed, histogram-equalized CTA at the
intensity resolution that survives equalization; (b) post-equalization
edits can pass a defensible realism gate; (c) the ResEnc-L effective
receptive field, not just patch size, spans reserve-to-lesion distances;
(d) the Drive-hosted weights load and reproduce challenge-level behavior
(same class of check as the idea-004 load probe); (e) follow-up mask
geometry actually contains edema-related expansion (unverifiable within
ISLES'24, already flagged by the card itself).

## Verdict

The unstated load-bearing fact (public frozen winner) is verified true;
the stated K1 is false as literally written but repairable by an
already-ratified program technique; the NCCT assumption is corrected from
primary source. No component is demonstrably fatal.

```json
{"verdict": "PASS", "evidence": "move_file(glob(str(join(data_path, \"preprocessed-cbf-map\", \"*.mha\")))[0], \"/tmp/raw/isles0000_0000.nii.gz\") ... [five channels: cbf, cbv, mtt, tmax, CTA — no NCCT]", "source": "https://github.com/KurtLabUW/ISLES2024 commit bb6c00c8, inference.py lines 121-125", "note": "Frozen public winner verified (code+weights); NCCT is NOT a model input so CSF edits must target the CTA channel, and global histogram equalization (preprocessing.py:21) plus default per-image z-scoring forces edits into post-equalization space with frozen normalization constants (idea-021 maneuver)."}
```
