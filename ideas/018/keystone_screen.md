# Keystone screen

## Keystone as stated

> A runnable whole-head survival model retains extracranial temporalis in its exact input tensor, and enough longitudinal MRIs have stable tumor burden but measurable temporalis change to separate frailty from tumor progression.

This is a conjunctive prerequisite. I inspected both the GRASP model/input side and the longitudinal-cohort side. The first is only partly established; the second is not established.

## What I inspected

### GRASP primary paper: input and preprocessing

I inspected the full text of Chelliah et al., *Neuro-Oncology* 2024, DOI 10.1093/neuonc/noae017 (PMCID PMC11145448), especially **Methods → Imaging and Combined Models**. It states:

> “Whole-brain T1c and T2 images were coregistered and minimally preprocessed … Images were resampled to common voxel sizes (1 mm3), and subsequently cropped or padded to a final 3D array of shape 130 × 130 × 130 for inputs to deep learning models.”

Source: [Europe PMC full-text XML](https://www.ebi.ac.uk/europepmc/webservices/rest/PMC11145448/fullTextXML), **Methods → Imaging and Combined Models**.

The paper also explains why tumor-only bounding boxes were not used:

> “This was not pursued because (i) extracranial information is linked with overall survival; (ii) contrast-enhancing masses remote to the initial site signal recurrence (and shorter survival); (iii) data preprocessing that aligned with pretraining preprocessing was favored; and (iv) whole-brain images require minimal preprocessing (plausibly reducing barriers to translation).”

Source: [Europe PMC full-text XML](https://www.ebi.ac.uk/europepmc/webservices/rest/PMC11145448/fullTextXML), **Discussion**, paragraph beginning “Another limitation is that we used a small dataset.”

These quotes verify a whole-volume 130-cubed input and deliberate avoidance of tumor-only cropping. They do **not** directly verify that the bilateral temporalis survives the crop in the exact tensors used for inference. No example preprocessed tensor, crop-coordinate rule, or per-case field-of-view audit was released.

### Official GRASP repository: runnability and released assets

I cloned and inspected the publication-linked repository at commit `ba0a1ca0acba5467a3c24b127f39024c78c57bb7`. Its README describes only training:

> “Usage to train the model:”

followed by:

> “python train.py -m train_model/model_params.json -e train_model/environment.json -g 1”

Source: [official GitHub repository README, lines 16–20](https://github.com/lyshc/glioblastoma-survival-classifier/blob/ba0a1ca0acba5467a3c24b127f39024c78c57bb7/README.md#L16-L20).

The checked repository tree contains training code and configuration, but no model checkpoint, pretrained weights, inference entry point, image data, or `.npz` cohort file. The configuration instead expects local paths such as `pretrained_weights/t1_weights.pt`, `pretrained_weights/t2_weights.pt`, and `data/input_data/training_data.npz`. Thus a published recipe exists, but an obtainable frozen GRASP model was not verified as runnable.

### GRASP primary paper: longitudinal data availability

The study used the first post-radiotherapy MRI, not a released serial cohort. The discussion explicitly contrasts its intended approach with longitudinal imaging:

> “For now, a model that could translate most easily across centers would likely benefit from a pragmatic approach that requires collecting widely available nonimaging features and cross-sectional (rather than longitudinal) imaging.”

Source: [Europe PMC full-text XML](https://www.ebi.ac.uk/europepmc/webservices/rest/PMC11145448/fullTextXML), **Discussion**, paragraph beginning “While predictions did not improve.”

The data-availability statement is:

> “Data generated or analyzed during the study are available from the corresponding author by request.”

Source: [Europe PMC full-text XML](https://www.ebi.ac.uk/europepmc/webservices/rest/PMC11145448/fullTextXML), **Data Availability**.

Therefore, the primary GRASP source does not establish an openly obtainable longitudinal cohort, any count of serial pairs, stable automated tumor burden, measurable temporalis change, or linkage of such pairs to a runnable frozen model. “By request” also does not satisfy the charter’s requirement to avoid dependence on unconfirmed gated data.

## Residual-assumption check

**If this card only verified the nearest checkable thing, what is it still assuming?**

The nearest checkable facts are that GRASP consumes minimally processed whole-volume MRI arrays and that temporalis size has an automated prognostic literature. The card is still assuming three load-bearing facts: (1) the exact 130-cubed GRASP tensors retain enough bilateral temporalis for measurement/intervention; (2) the trained survival weights are obtainable and runnable; and (3) an obtainable serial, survival-linked cohort contains enough same-patient scans with stable automated tumor burden but meaningful temporalis change. None was directly established by the paper, repository, released files, or cohort schema inspected here.

The stated keystone is therefore the correct load-bearing keystone, but it remains unresolved rather than demonstrably false. The primary paper’s cross-sectional design and by-request data weaken the proposed route; they do not prove that no suitable model or independent public serial cohort can exist.

```json
{"verdict": "UNVERIFIABLE", "evidence": "Data generated or analyzed during the study are available from the corresponding author by request.", "source": "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC11145448/fullTextXML — Data Availability", "note": "Whole-volume inputs are verified, but exact temporalis retention, released runnable weights, and a sufficiently large obtainable tumor-stable longitudinal cohort are not."}
```
