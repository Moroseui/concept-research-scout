# Critique — Idea 015: A breast-cancer risk model may be reading the arteries as a vascular clock

```
FATAL OBJECTION: NONE — but the card mis-states its keystone (it treats cohort/BAC-tool
  availability as the gate) and over-claims its endpoint ("vascular clock/vascular-age"),
  which the proposed design cannot reach.
EVIDENCE: Radiology:AI ryai.240417 (Mirai+EMBED feature-centric XAI, calcification features
  drive Mirai) — uncited; Mirai README (4-view Hologic "For Presentation" only); the "use"
  question needs no cancer-outcome labels, which the card never notices.
REPAIRABLE WITHOUT CHANGING THE QUESTION? YES
DECISION: ADVANCE TO REVISION
```

## What the question actually is, and what survives

The interesting, physician-legible core is real: **does Mirai's risk output respond to
breast arterial calcification (BAC) — the coarse, linear, tram-track medial calcium in
mammary arteries — as opposed to only the fine clustered microcalcification that signals
malignancy?** That is a Mode-B "unasked question" in the true sense: the two things that
should connect (a cardiovascular-disease imaging marker and a breast-cancer risk score
computed on the same pixels) have not been connected in print.

I verified the surrounding literature and the core survives adversarial checks on novelty,
circularity, and data existence. It does **not** survive as currently written on
identifiability wording and endpoint honesty. Both are repairable inside the same question.

## Novelty — survives, but the card is missing its closest prior work

The card's three citations are thin and one is nearly the wrong warning. The genuinely
threatening prior work, **not cited**, is:

- **Using Explainable AI to Characterize Features in the Mirai Model**, *Radiology: AI*,
  DOI 10.1148/ryai.240417. A feature-centric XAI pipeline over Mirai's 512 features on
  **29,374 EMBED screening exams (2013–2020)**. It selected 18 calcification features
  ("CalcMirai") and 18 mass features ("MassMirai") and showed Mirai implicitly learned
  **calcification** features for risk. This is the same model *and* the same cohort (EMBED)
  the idea proposes, and it already establishes "Mirai keys on calcification."

- The card's own cite arXiv:2606.26431 (*Revealing Mammographic Phenotypes…*): I read the
  abstract. Its risk-linked phenotypes are **dense tissue, microcalcifications, and clip
  artifacts** — no arteries, no vascular/medial calcification. The card's fear that this
  preprint "may already touch BAC" is unfounded for the abstract-level phenotype inventory.

**Net:** neither ryai.240417 nor 2606.26431 distinguishes *arterial* macrocalcification from
*lesion* microcalcification. The BAC-specific question is open. But ryai.240417 **sharpens the
central confound**: Mirai demonstrably uses "calcification" broadly, so any BAC effect must be
shown to be more than "Mirai counts benign arterial calcium among its suspicious-calcification
pixels." The revision must cite ryai.240417 and frame the delta as *arterial-vs-lesion
calcification*, not *does Mirai use calcification* (answered: yes).

## The keystone is misidentified

The card names the keystone as "an executable BAC quantifier transfers to Mirai-compatible
four-view mammograms with enough BAC-positive cases and age/density overlap." Two problems.

1. **The BAC tool is less of a gate than claimed.** Public BAC segmenters with code/weights
   exist — e.g. `github.com/dominicmaguire/bac-model-code` (Maguire 2025) and SCU-Net
   (medRxiv 2021.07.30.21261406). So "a transferable BAC quantifier exists" is close to
   INSPECTED_TRUE; residual transfer risk is real but modest.

2. **The load-bearing fact the card walks past:** the question *"does Mirai use BAC"* is
   answered by measuring **Mirai's own risk-score change under a BAC intervention** — it does
   **not require future-cancer outcome labels at all.** The card imports EMBED-style outcome
   linkage and screening-cohort requirements it does not need for rung 1. This both relaxes
   data (any obtainable four-view FFDM set with BAC present suffices) and re-centres the true
   keystone:

   > **Mirai runs end-to-end on the same obtainable mammograms the BAC segmenter runs on.**
   > Mirai's README requires all four **"For Presentation" Hologic** views (L/R CC/MLO) and
   > "may not properly convert dicoms from other manufacturers." EMBED is the cohort *proven*
   > compatible (ryai.240417 ran Mirai on it); mixed-vendor public sets (VinDr-Mammo) are the
   > transfer risk. That DICOM-to-Mirai-tensor + BAC-mask join is the fact that, if false,
   > makes the study impossible — and it is `NOT_INSPECTED`.

The "if I only verified the nearest checkable thing, what am I still assuming?" answer is:
*that a BAC mask computed in one image space is spatially registered to the exact PNG16 tensor
Mirai consumes, so an intervention deletes the same pixels the model reads.* State that.

## Identifiability — the design leads with its weakest instrument

The confirmatory design leads with **learning a BAC direction in Mirai's frozen embedding and
erasing it**, comparing against age/density/device directions. This is the weak version:

- BAC is strongly age-correlated (prevalence ~13%, rises steeply with age). In embedding
  space BAC and age directions will overlap; linear erasure of one degrades the other, and the
  "incremental beyond age" contrast has low power — exactly the sensitivity-limited null the
  card concedes. Direction erasure also shows only that BAC info is *linearly present and
  downstream-influential*, not that the model reads an anatomical structure.

**The stronger, and available, instrument is an image-space intervention.** You already have a
BAC segmentation mask. Inpaint/attenuate the segmented arterial calcium to local background,
re-run frozen Mirai, and measure the **paired risk-score change** — with a **sham control** that
removes an equal-area, equal-intensity *non-arterial* structure. This is spatially localized,
causal, assumption-light, and it dodges BAC-age entanglement. It is the same structural move
that let the one surviving prior candidate (idea-004) avoid labels: intervene on the image and
compare the model to itself. Make this the primary readout; demote embedding-erasure to a
secondary triangulation.

Even with the image-space test, one alternative is hard and must be stated plainly:
**lesion-mimicry.** Because Mirai provably uses calcification pixels (ryai.240417), removing
BAC may lower risk simply because benign calcium was being scored as suspicious calcium — not
because Mirai extracts *systemic vascular age*. The sham control and morphology separation
(coarse parallel tram-track vs fine pleomorphic clusters) address whether the effect is
BAC-specific, but they **do not** establish "vascular clock."

## Endpoint honesty — the deliverable sentence over-claims by one rung

The deliverable — *"Mirai is using BAC as a **vascular-age signal**"* — bundles an
interpretation the design cannot reach. The intervention can establish, at most, that
**Mirai's risk output specifically responds to breast arterial calcification** (rung 1, and
rung 2 if device/site controls hold). Calling it a *vascular clock / vascular-age signal*
asserts the model extracts systemic ageing, which would require showing the BAC effect tracks
an independent vascular/CVD-age axis beyond lesion-mimicry and beyond chronological age. This
is the same over-reach that got idea-007 demoted rung 3 → rung 1. Revise the deliverable to the
rung-1/2 claim; keep "vascular age" only as the named rung-3 target with its explicit
additional evidence requirement.

## Other adversarial checks (pass)

- **Circularity / leakage:** BAC is not Mirai's target; the future-cancer label is not printed.
  Passes. One real shortcut: **biopsy clips / CAD overlays** — ryai.240417 and 2606.26431 both
  found clip artifacts as risk phenotypes, so exclusion of prior-intervention markers is
  mandatory, as the card notes.
- **Compute:** Mirai inference on hundreds–few-thousand exams is a single-GPU afternoon. Passes.
- **Dies-like-prior:** does not repeat the annotation-provenance kills (BAC is computed, not
  annotator-rated) nor CIRCULARITY. Correct.
- **Data DUA:** EMBED is the compatible cohort but is credentialed/registration-gated; the
  charter forbids *unconfirmed* DUA-gated dependence. Stage 0 must confirm access terms, or
  identify a four-view Hologic "For Presentation" public alternative — noting Mirai's
  manufacturer sensitivity rules out casual substitution.

## Negative-result value

The card's "sensitivity-limited (2)" is correct **for the erasure design**. The image-space
sham-controlled intervention raises it: if deleting BAC moves Mirai's risk no more than the
matched sham deletion, that is a reasonably **decisive** "Mirai does not specifically use BAC,"
provided the BAC-positive sample clears a prespecified minimum-detectable-effect. Power is the
only threat (BAC sparse), so a prespecified MDE / equivalence margin is required to earn a 3.

## Required revisions before advancement

1. Cite ryai.240417; reframe novelty delta as **arterial vs lesion calcification**.
2. Make the **image-space BAC-inpainting intervention with a matched sham** the primary
   readout; demote embedding-direction erasure to secondary.
3. Reset the keystone to **Mirai-DICOM compatibility + spatial registration of the BAC mask to
   Mirai's input tensor** on an *obtainable, confirmed-compatible* cohort; drop the unneeded
   cancer-outcome/screening-linkage requirements for the rung-1 question.
4. Rewrite the deliverable sentence to the rung-1/2 claim ("Mirai's risk responds specifically
   to breast arterial calcification"); keep "vascular-age" as the labelled rung-3 target only.
5. Stage 0: confirm EMBED (or alternative) access terms and BAC prevalence in the usable sample.

---

```
NEAREST DEFENSIBLE HIGH-VALUE QUESTION: Does inpainting the segmented breast arterial
calcification out of a four-view mammogram change frozen Mirai's five-year risk score more than
a matched sham deletion of equal-area non-arterial calcific structure?
RETAINS ORIGINAL MEDICAL MOTIVATION? PARTLY — keeps "a breast-cancer model responds to a
cardiovascular imaging marker"; drops the unearned "reads systemic vascular age" interpretation.
SHOULD IT BECOME A SEPARATE CANDIDATE? NO — it is the same question done more identifiably; it
is the revision, not a fork.
IS IT ACTUALLY WORTH DOING? Yes — a clean, label-free, single-GPU causal test on public tools
(Mirai + a public BAC segmenter) that would tell radiologists whether a widely evaluated risk
score is partly reading benign vascular calcium, provided Stage 0 confirms the Mirai-cohort and
BAC-mask registration join.
```
