# Critique — Idea 016: The PE model may read contrast flowing backward as a pressure gauge

```
FATAL OBJECTION: NONE that kills the question — but the rung-3 deliverable ("sign of
  elevated right-sided pressure") is unreachable, because injection rate is a documented
  independent cause of identical IVC/hepatic reflux and the RSNA de-identified headers almost
  certainly lack injection metadata; and the primary instrument (embedding-direction erasure)
  cannot dissociate reflux from RV dilation, which are two readouts of ONE hemodynamic state.
EVIDENCE: Yeh et al., AJR 2004 (10.2214/ajr.183.5.1831227) — high injection rate is an
  independent predictor of retrograde IVC/hepatic opacification; reflux occurs in normal
  individuals at injection rates >3 mL/s. RSNA-STR is de-identified challenge DICOM with no
  released contrast-protocol field. No released frozen RV-strain checkpoint exists (only Kaggle
  solutions, e.g. KeremTurgutlu 13th place); hepatic-vein coverage is NOT_INSPECTED.
REPAIRABLE WITHOUT CHANGING THE QUESTION? YES
DECISION: ADVANCE TO REVISION
```

## What the question is, and what survives

The core is genuinely interesting and physician-legible: **does a CTPA model that outputs
right-heart-strain (RV/LV ≥ 1) read the refluxed contrast column in the IVC and hepatic veins,
rather than the chamber geometry the label nominally encodes?** Contrast reflux as a marker of
right-heart dysfunction is real, established, and named — I verified it. This is a legitimate
Mode-C shortcut question. It survives adversarial checks on mechanism plausibility and on
novelty. It does **not** survive as written on (a) the rung it claims, (b) the instrument it
leads with, and (c) two uninspected feasibility gates. All three are repairable inside the same
question, so the disposition is ADVANCE TO REVISION, hard-gated on Stage 0.

## The rung-3 mechanism is real — but that same literature contains the confound that blocks it

I verified the rung-3 claim is not fluent nonsense. Reflux of contrast into the IVC/hepatic
veins is an accepted first-pass sign of pulmonary hypertension and right-heart dysfunction;
reflux length correlates linearly with tricuspid-regurgitant jet velocity and with mPAP at
right-heart catheterisation (Yeh et al., AJR 2004, 10.2214/ajr.183.5.1831227; AJC 2011
S0002-9149(11)02948-1). The named quantity exists and a radiologist would recognise the
sentence. Good — this clears the "guard against fluent nonsense" bar and mechanism_clarity 5 is
defensible.

**But the same primary source is where the candidate's deliverable dies.** Yeh et al. found on
multivariate analysis that **injection rate is an *independent* predictor** of retrograde
IVC/hepatic opacification, and that reflux is seen **in normal individuals when injection rate
exceeds ~3 mL/s.** So a bright reflux column is produced by *at least two* fully sufficient
causes: pathologic back-pressure, and a brisk power-injector. These are not distinguishable from
the voxels alone. To claim rung 3 — "the model is using reflux *as a sign of elevated
right-sided pressure*" — you must exclude the injection-rate explanation for the specific scans
where reflux is present. That requires per-scan injection rate / saline-chaser / scan-delay
metadata. The RSNA-STR dataset is a de-identified competition corpus; contrast-protocol fields
are essentially never retained, and the card lists "injection metadata or a valid timing proxy
exists" as an *unverified* claim. **If that metadata is absent — the likely case — rung 3 is
unreachable, full stop**, and the deliverable sentence over-claims by one full rung. This is the
identical failure that demoted idea-007 (rung 3 → rung 1) and that the idea-015 critique flagged
as endpoint dishonesty. The card must demote its deliverable now, not discover this in Stage 0.

## The primary instrument cannot dissociate what it needs to dissociate

The confirmatory design leads with **learning reflux / RV-LV / clot / timing directions in the
frozen embedding and erasing each separately and jointly**, then claiming a decisive negative if
reflux-erasure is null while RV/LV-erasure moves the score. Two problems, one of them severe.

1. **Reflux and RV dilation are not confounds of each other — they are two readouts of one
   state.** Elevated right-sided pressure *causes* both the tricuspid regurgitation that drives
   reflux *and* the RV dilation that raises RV/LV. They are physiologically collinear, not
   merely correlated. Linear direction erasure asks the embedding to hold one fixed while
   removing the other; when the two directions are near-parallel, the "incremental beyond RV/LV"
   contrast has little residual variance to work with. That is a **sensitivity-limited** null,
   not a decisive one. The card scores negative_result_value = 5 ("decisive") on the strength of
   this comparison; that is over-stated for the erasure instrument and should be 2–3 absent an
   equivalence margin / minimum-detectable-effect. This is exactly the mistake the rubric warns
   about: "Non-rejection is not evidence of independence."

2. **Direction erasure shows only that reflux information is linearly present and
   downstream-influential — not that the model reads the anatomical reflux column.** It is the
   weak version of the test, the same one the idea-015 critique demoted in favour of an
   image-space intervention.

**The stronger, available instrument is the idea-004/idea-015 move: intervene in image space and
compare the model to itself.** Segment the refluxed contrast in the IVC/hepatic veins, inpaint it
to local venous blood-pool baseline, re-run the frozen model, and measure the **paired change in
the RV/LV-strain output**, against a **sham control** that removes an equal-volume, equal-HU
contrast collection elsewhere (e.g. a bland vein at the same craniocaudal level). This is
spatially localised, causal, label-free, and — critically — **it does not require injection
metadata for rung 1**: if erasing the reflux voxels moves the strain score more than the matched
sham, the model *uses* the reflux column, whatever produced it. Injection metadata is only needed
to promote that rung-1 fact to the rung-3 "pressure" interpretation. Make the image-space
sham-controlled intervention the primary readout; demote embedding-erasure to secondary
triangulation.

## Two uninspected feasibility gates, both load-bearing

The card is honest that keystone_status is NOT_INSPECTED. The keystone as written ("voxels needed
to measure reflux are consistently in frame, and bolus timing is recoverable") is correct in
spirit but bundles two separable gates that Stage 0 must clear independently:

- **Coverage.** CTPA scan range is targeted at the pulmonary arteries: apices to the
  costophrenic angles / lung bases. The hepatic-vein confluence and intrahepatic IVC sit near
  the diaphragm and are *often* in frame, but the infrahepatic IVC and the caudal extent of any
  reflux column are frequently truncated. The mechanism's whole point (per the card's own
  `if_analogy_dropped`) is a **normalized reflux *extent/length*** with a dose-like relationship —
  and extent is precisely what an inconsistent caudal cutoff destroys. Web search on the RSNA
  dataset returned no field-of-view spec; this must be measured on stratified scans, and the card
  should expect to fall back from "reflux extent" to "reflux presence at the diaphragm level,"
  which weakens the normalized-column argument that distinguishes this from a binary reflux label.

- **The model.** There is **no released, citable, frozen right-heart-strain checkpoint.** The
  RSNA-STR challenge produced Kaggle solutions (e.g. `github.com/KeremTurgutlu/RSNA-Pulmonary-Embolism-AI-Challenge`,
  13th place) whose weights are not maintained/packaged; the winning stacks are 2D-CNN +
  sequence models with a multi-task study-level `rv_lv_ratio_gte_1` head. "A frozen reproducible
  RV-strain checkpoint is available" is an *unverified* claim, and realistically means
  **reproducing/retraining a competition solution**, not downloading weights. That is a real
  cost (the card's "1 week to identify/reproduce a checkpoint" is optimistic) and it also changes
  the framing: you would be decoding a model *you* trained on a reader-measured RV/LV ratio.

## Framing honesty: this is entry point 2 with a weaker gap than the prose implies

The card correctly declares entry_point 2. But note the RV/LV ≥ 1 label is itself a
reader's caliper measurement of chamber geometry, so "the PE model" here is a model trained to
*reproduce a human measurement* — not a documented case of a model beating radiologists or
predicting something they cannot. There is no established performance gap anchoring this. That is
allowed under entry point 2, but it means the medical motivation is "does a strain classifier
shortcut via a benign-looking fluid-dynamic sign," which is a robustness/shortcut question, not a
discovery of unarticulated signal. The revision should state this plainly rather than leaning on
the more dramatic "reading a fleeting fluid-dynamic sign" framing.

## Adversarial checks that pass

- **Circularity / leakage:** Reflux is not the RV/LV target and is not printed in the label; X is
  computed from voxels; primary readout (revised) is the model's self-change under an image edit.
  Passes — and avoids the idea-010 CIRCULARITY kill, provided the design does not smuggle RV/LV
  geometry back in through the reflux mask. One residual: the IVC/hepatic segmentation must not
  incidentally include right-atrial or RV contrast, or the "reflux" edit becomes a chamber edit.
- **Dies-like-prior:** Does not repeat the annotation-provenance kills (reflux is computed, not
  annotator-rated). Does not repeat idea-006 (no patient deletion, no constant-fill OOD image) —
  the image-space inpaint-to-blood-pool edit is in-distribution *if* validated with a sham
  tolerance, which the revision must prespecify (same requirement idea-008 now carries).
- **Compute:** Frozen-model inference on hundreds–low-thousands of CTPA studies is single-GPU
  feasible. The cost is checkpoint reproduction, not inference.
- **Data DUA:** RSNA-STR is openly redistributed (AWS Open Data / Kaggle); no DUA gate. Passes.

## Required revisions before advancement

1. **Demote the deliverable** to rung 1 / conditional rung 2: "the model's strain output responds
   specifically to refluxed contrast in the IVC/hepatic veins." Keep "sign of elevated
   right-sided pressure" only as the labelled rung-3 target, explicitly gated on recovering
   injection-rate/protocol metadata to exclude the injection-artifact explanation.
2. **Switch the primary instrument** to a sham-controlled image-space reflux-erasure (inpaint to
   venous blood-pool baseline; matched equal-volume, equal-HU sham elsewhere); demote
   embedding-direction erasure to secondary. Correct negative_result_value down for the erasure
   arm and attach a prespecified MDE / equivalence margin to the image-space arm.
3. **Split the keystone into two inspectable gates** and run both in Stage 0: (a) hepatic-vein /
   intrahepatic-IVC coverage and caudal extent on ≥100 stratified scans, reporting the fraction
   admitting a *measurable reflux extent* vs. presence-only; (b) whether a runnable frozen
   RV-strain checkpoint can actually be obtained or must be reproduced, with the reproduction cost
   named.
4. **State the injection-rate confound up front** with Yeh et al. 2004 cited, and decide in
   advance whether rung 3 is even attemptable given metadata availability; if not, cap the study
   honestly at rung 1/2.

---

```
NEAREST DEFENSIBLE HIGH-VALUE QUESTION: Does inpainting the refluxed contrast out of the
IVC/hepatic veins on a CTPA change a frozen RV/LV-strain model's output more than a matched
equal-volume, equal-HU sham deletion elsewhere?
RETAINS ORIGINAL MEDICAL MOTIVATION? PARTLY — keeps "a strain model may key on a benign-looking
retrograde-contrast sign"; drops the unearned "as a gauge of right-sided pressure" until
injection metadata can exclude the power-injector explanation.
SHOULD IT BECOME A SEPARATE CANDIDATE? NO — it is the same question made identifiable and
honest about its rung; it is the revision, not a fork.
IS IT ACTUALLY WORTH DOING? Conditionally yes — a clean, label-free, single-GPU causal test that
would tell radiologists whether a PE strain classifier is partly reading refluxed contrast, but
only if Stage 0 confirms both that the hepatic-vein/IVC voxels are consistently in frame with
measurable extent and that a frozen RV-strain checkpoint can be obtained or reproduced at
acceptable cost; if either gate fails, it is not worth doing.
```
