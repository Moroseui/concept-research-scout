# Adversarial critique — Idea 014

## The knee-pain model may be reading trabecular stress architecture that KL grade throws away

```
FATAL OBJECTION: The design freezes and erases "the Pierson pain model," but no trained
  checkpoint exists — the repo ships training code only (Python 3.5.2, raw registration-
  gated OAI, reported terabyte-RAM preprocessing), so the frozen representation the entire
  readout depends on has to be reproduced from scratch, and that reproduction is unverified.
EVIDENCE: github.com/epierson9/pain-disparities README — only `train_models.py`
  (`train_best_model_continuous`), no weights; raw data at nda.nih.gov/oai/ is gated.
REPAIRABLE WITHOUT CHANGING THE QUESTION? YES (reproduce the model) — but feasibility unverified.
DECISION: PAUSE
```

The idea is genuinely interesting — it tries to decode a famous, real model-versus-human
gap (ALG-P predicts osteoarthritis pain beyond Kellgren–Lawrence and shrinks a racial pain
disparity) into a bone quantity a clinician recognizes, and two mature OAI literatures do sit
one experiment apart. That is why the header says PAUSE, not REJECT. But two things must be
settled before a probe contract, and the card currently under-states both.

---

## 1. The keystone is now partially inspected — and it fails as written

The card's keystone is: *"The frozen Pierson pain model or exactly reproducible checkpoint
can be run on OAI images…"* with `keystone_status: NOT_INSPECTED` and, in `unverified_claims`,
*"A runnable Pierson checkpoint is currently available."*

**Verified fact (inspected today):** it is not available. `github.com/epierson9/pain-disparities`
releases training code and analysis notebooks only. There is no weights file; reproduction is
`python train_models.py train_best_model_continuous` against raw OAI DICOMs downloaded from
`nda.nih.gov/oai/`, on a Python 3.5.2 environment, with preprocessing the authors say ran on
"a computer with several terabytes of RAM and hundreds of cores."

This changes the card in three ways the revision must absorb:

- **"Frozen Pierson model" is a misnomer.** Every downstream step — fit a probe from *frozen
  embeddings*, freeze the *validation-learned X direction*, *erase only it* — presumes a fixed
  published network. There is none. You would be probing *your* re-trained network. That is
  allowed, but then the deliverable sentence is about a reproduction, and its validity is
  gated on the reproduction reproducing the published ALG-P behaviour (better-than-KLG pain
  prediction; disparity reduction) on a frozen split. That equivalence check is a Stage-0 gate
  the card does not list.
- **Feasibility is below the current 3, not at it.** A legacy Python 3.5.2 stack, raw-DICOM
  reprocessing at the reported scale, and gated OAI access together exceed "first result in
  days" and strain the Colab-Pro+/single-GPU constraint for the *training* half (inference and
  the texture work are fine on a single GPU; the retraining and full-OAI preprocessing are the
  problem). The card's own `remaining_legwork` ("2 days to inspect checkpoint") is written as
  if a checkpoint were downloadable; it is not.
- **This is the loop's recurring wrong-keystone shape.** The easy adjacent fact ("Pierson and
  the texture literature both use OAI") was verified; the load-bearing fact ("there is a
  runnable frozen model to erase directions from") was assumed and is false as stated. Answer
  to the mandated question — *"if I have only verified the nearest checkable thing, what am I
  still assuming?"* — is: *that the model can be reproduced and will match the published gap.*
  That, not "texture varies within KL," is the real keystone.

Repairable? Yes — reproduce and validate the model. But until a reproduction is confirmed to
run and to recover ALG-P behaviour on a frozen split, there is literally nothing to erase, so
the study is blocked, not merely imperfect. Hence PAUSE.

## 2. Even granting a working model, the design does not identify the *directional* claim

The deliverable sentence is specifically *directional* — "directional thickening and
rarefaction," horizontal-versus-vertical fractal signatures, the load-path story from bone
mechanobiology. That directionality is the entire cross-domain content. The experiment as
written does not isolate it.

- **The readout erases one texture direction and compares to random / KL / JSN directions.**
  Subchondral trabecular texture, subchondral sclerosis, BMD, and joint-space narrowing are
  co-varying bone changes; the medial compartment darkens, scleroses, and narrows together.
  A KL/JSN "nuisance direction" is a coarse ordinal proxy and will not span the continuous
  sclerosis/density variation that rides along with texture. So a positive erasure effect that
  survives the JSN control still supports only *"the model uses medial subchondral bone
  texture/density"* — a named thing, but **a different named thing** than "directional
  load-path architecture," and one entangled with the disease severity the model is *expected*
  to read. That is the idea-009 estimand mismatch (REJECTED): a synthetic/representational
  deletion that does not map onto the specific naturally-occurring quantity named.
- **Apply the charter's own test — "what would be different if the analogy were dropped?"**
  As written: nothing. You would fit a probe to a fractal-signature scalar and erase it whether
  or not you believed the mechanobiology story. To make the analogy load-bearing, the *primary*
  readout must be directional specificity: erasing the **horizontal** signature harms pain
  prediction more than erasing an equal-norm **vertical** (or isotropic mean-density) signature.
  The card mentions horizontal-vs-vertical in `cross_domain` but does not commit it as the
  registered primary contrast, and does not list an isotropic-density nuisance direction among
  its controls. Without that, the directional claim is decoration on a generic-texture result.

## 3. The confound the card underweights: the measurement X is itself acquisition-sensitive

Fractal-signature / texture analysis of subchondral trabecular bone on **plain radiographs** is
well known to move with detector type (CR vs DR), pixel spacing, exposure, and focal-spot blur
(the OAI-adjacent literature the card leans on — e.g. tibial subchondral structure on plain
films, PMC5635082 — operates under exactly these constraints). OAI radiographs were acquired
across multiple clinical centres over years with fixed-flexion positioning but non-identical
equipment. So site/scanner leaks into **X itself**, contaminating both the probe target and,
potentially, what the network reads (echo of Gichoya: a bone-texture channel is exactly where a
site/race proxy could hide). The card's "site-held-out strata + external device replication"
is stated but not budgeted, and external device replication is not obviously available.

**The one strong structural move the card has, and should promote.** OAI's PA fixed-flexion
film images **both knees in a single exposure**; ALG-P is scored per knee. A **within-person,
within-film left-vs-right** contrast holds acquisition, exposure, habitus, and the patient's
systemic pain-reporting tendency fixed by construction, and asks whether the knee with the
greater directional subchondral texture asymmetry carries the higher ALG-P. This is the
"compare the model to itself" survivor move that the ledger explicitly says is under-used. It
is a cleaner identifier than embedding erasure and is nearly acquisition-immune. **Caveat to
verify in Stage 0:** it only works if the Pierson network scores single-knee crops from the
bilateral film (so left/right share one exposure). If the model ingests a differently framed
input, the acquisition-matching is lost. This should be inspected in the repo's
`image_processing.py`, not assumed.

## 4. Smaller marks (not decisive individually)

- **Domain fit.** The charter's emphasis is CT / 3D volumetric imaging; this is a 2D knee
  radiograph. Explicitly allowed as radiology, but off the stated centre of gravity. Minor.
- **Negative-result value is genuinely weak (score 2 is right).** A null erasure is
  sensitivity-limited (nonlinear coding survives); a positive erasure is ambiguous (collinear
  severity removed). Neither tail is a decisive type-1 negative. The bilateral-asymmetry
  association arm (below) has a cleaner negative: no KLG-independent texture-pain association ⇒
  the flagship is dead.
- **`dies_like_prior` is fair.** It does not repeat DATA_INSUFFICIENT (X is image-computable,
  not the sparse LIDC diagnosis join) or CIRCULARITY (X is neither the pain label nor KL). The
  provenance failure mode does not apply because X needs no annotator. Agreed. Its real risk is
  the idea-009 identifiability mismatch, which is a different, live danger.
- **"Fractal signature" is not off-the-shelf.** Janvier's variance-orientation-transform /
  validated semiautomated FNIH software is not a `pip install`. Reproducing a *stable,
  repeatable* directional signature (Stage-0 repeatability floor) is real, non-trivial legwork
  the card correctly flags but should not under-budget.

---

## Verdict rationale

PAUSE, not REJECT: the medical premise is real and the question is high-regret. PAUSE, not
ADVANCE-TO-REVISION: the load-bearing asset (a runnable frozen model) is verified-absent, and
the design's directional claim is not yet identifiable — both must be resolved before a probe
contract, and the first is an external feasibility fact the human should confirm rather than a
prose fix.

**Reopening conditions (all three):**
1. A reproduced Pierson model runs on a frozen OAI split and recovers the published ALG-P
   behaviour (better-than-KLG pain prediction; the disparity signature). Until then there is no
   representation to erase.
2. The primary readout is redesigned to test **directional** specificity (horizontal-vs-vertical /
   vs isotropic-density erasure), so the mechanobiology analogy is load-bearing, not decoration.
3. The **within-film left-vs-right** contrast is promoted to the primary identifying design, and
   `image_processing.py` is inspected to confirm the network scores acquisition-matched
   single-knee crops.

---

```
NEAREST DEFENSIBLE HIGH-VALUE QUESTION: In OAI, does directional medial-tibial subchondral
  fractal signature explain osteoarthritis pain that Kellgren–Lawrence misses — tested as a
  within-person, within-film left-vs-right asymmetry against the WOMAC/KLG-residual — using only
  OAI images, published FSA, and pain labels, with no neural network and no retraining?
RETAINS ORIGINAL MEDICAL MOTIVATION? PARTLY — it tests the substrate premise (does this bone
  texture carry KLG-independent pain signal at all) but drops the charter's core "what is the
  MODEL using" framing; it is a premise gate, not a model-decode.
SHOULD IT BECOME A SEPARATE CANDIDATE? YES — it needs no checkpoint, no legacy stack, and no
  concept-erasure calibration, so it is unblocked while Idea 014 waits on reproduction.
IS IT ACTUALLY WORTH DOING? Yes: it is a cheap, decisive gate — a null KLG-adjusted texture-pain
  association within person kills the flagship before anyone retrains a 2021 model, and a
  positive one is the strongest possible motivator for the harder model-decode study; the only
  real cost is reproducing a repeatable directional FSA, which is needed for Idea 014 regardless.
```
