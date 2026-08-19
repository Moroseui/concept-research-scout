# Critique — idea 039 (isles24-scout-005-c06): Does the model trust tissue that obeys the flow equation?

```
FATAL OBJECTION: The confirmatory contrast (residual-removal projection vs
equal-energy tangent shams) identifies directional sensitivity of a nonlinear
multichannel function, not use of the residual "as a hidden confidence map" —
the deliverable sentence is not identified by the stated design.
EVIDENCE: idea_card.json `use_vs_association` vs `deliverable_sentence`; a
residual-blind model reading raw MTT values can pass every stated gate (§1).
REPAIRABLE WITHOUT CHANGING THE QUESTION? YES
DECISION: ADVANCE TO REVISION
```

---

## 1. The decisive objection: anisotropy is not confidence

The card's use-versus-association move is: project the (CBF, CBV, MTT)
triplet onto the central-volume-consistent manifold, compare against
equal-per-channel-L2 perturbations tangent to the manifold, and read a
"selective, graded response to removing only the normal residual" as evidence
of use. The claimed estimand is stronger than that contrast can deliver.

Any smooth multichannel function responds anisotropically to input
perturbations. The normal direction to the constraint manifold is one
particular direction in input space, and — critically — the normal
*component* of a case's maps is a specific spatial pattern (concentrated
where noise, delay sensitivity, and regularization broke the identity).
A model with **no inconsistency computation of any kind** — say, one that
reads MTT values with a spatially varying learned weighting — will generically
respond more to the normal-direction edit than to a tangent sham, simply
because the normal component's spatial distribution differs from the sham's
and correlates differently with the lesion-relevant tissue. Matching
per-channel L2 energy equalizes edit *size*, not edit *placement* or
alignment with the model's local gradient. And monotone dose response is no
discriminator at all: a purely linear readout produces a perfectly monotone
response to graded removal of any fixed component.

So the experiment as designed licenses only: "the model's prediction depends
on the off-manifold component of the map triplet." That is the card's own
rung-1 wording ("selective use of the cross-map inconsistency residual"),
and it is a legitimate, testable claim. But the deliverable sentence — "using
violation of the central-volume identity **as a hidden confidence map** for
perfusion evidence" — asserts a functional role: that the model *discounts
perfusion evidence* where the residual is high. Nothing in the projection
contrast measures discounting. The deliverable sentence exceeds what the
design identifies, which is exactly the wrong-keystone/overclaim family this
pipeline has killed eleven candidates for.

**The repair, which preserves the question rather than changing it:** the
confidence-map claim is a claim about *interaction*, so test the interaction
directly. Add a confirmatory arm: at high-X and low-X locations matched on
perfusion severity (CBF, Tmax strata) and lesion distance, apply an identical,
small, fixed perfusion-evidence edit (e.g., a calibrated CBF-deficit
deepening) and compare the model's response magnitude. "Hidden confidence
map" predicts attenuated response at high-X sites; the anisotropy artifact of
§1 makes no such prediction. The projection/tangent contrast then demotes to
a supporting arm establishing residual dependence, and the interaction arm
carries the deliverable sentence. The question asked — is the model using
identity violation as a confidence signal for perfusion evidence? — is
unchanged; what changes is that the design now measures the "for perfusion
evidence" clause instead of assuming it. This stays revision-in-place under
the 2026-08-10 claim-identity rule: same deliverable sentence, strengthened
design.

## 2. Elevated triviality risk — flagged by the card's own citation

The card cites Konstas et al. (PMID 19270105) as supplying the invariant, and
its own `novelty_neighbors` relation text concedes the sting: the source
"explains that MTT is **calculated from** CBV/CBF." In common deconvolution
implementations CBV is the area and CBF the peak height of the flow-scaled
residue function, and MTT is then *defined* as CBV/CBF (area over height). If
icobrain cva 1.5.0 does this and stores the quotient, the residual X is
identically zero up to quantization, clipping, and any post-hoc per-map
smoothing — the candidate dies at Stage 0, as the card itself anticipates.
My search found no public documentation of icobrain cva's MTT derivation
(icometrix does not appear in the deconvolution-implementation literature I
could locate), so this cannot be resolved at critique time. Alternative
implementations (first moment of the residue function) would make MTT
genuinely independent, and post-processing applied per-map can break even a
by-construction identity; the keystone screen's UNVERIFIABLE verdict is
correct.

Not fatal — the card contains the kill gate — but the revision must sharpen
Stage 0 in two ways: (a) an **explicit algebraic-dependence test** (regress
stored MTT on stored CBV/CBF per case; near-perfect fit up to quantization =
kill), rather than only the rank-stability check; (b) a pre-committed ruling
that a residual dominated by quantization/rounding structure counts as
"collapses to a constant" and kills. Without (a), a residual that is 99%
rounding noise could pass a rank-correlation threshold across two masks and
launch a doomed intervention study.

## 3. A confound the card does not list: edit-induced cross-map incoherence

The projection edits CBF/CBV/MTT but leaves Tmax (and any other input
channels the surrogate sees, e.g. NCCT/CTA) untouched. MTT and Tmax are
strongly physiologically and algorithmically coupled. A residual-removal edit
that shifts MTT therefore *introduces* a new inconsistency — between edited
MTT and unedited Tmax — that did not exist in training data. A model
responding to that novel MTT–Tmax mismatch would masquerade as responding to
central-volume-residual removal. Tangent shams also perturb MTT, but there is
no reason their MTT–Tmax decorrelation is matched to the projection arm's.
The `alternative_explanations` list covers support/clipping artifacts and
generic edit sensitivity, but not this. Revision options, any one of which
suffices: report and match MTT–Tmax coherence disruption across arms; add a
sensitivity arm with a Tmax-free surrogate; or include Tmax in the projection
with its own consistency treatment. This must be addressed before the
projection arm is interpretable even at rung 1.

## 4. "The final-infarct model" is actually a Dice-0.20 2D surrogate

Verified: the ISLES'24 winning entry (Kurtlab, arXiv 2505.18424) is a
preprocessing pipeline plus 3D residual-encoder nnU-Net reaching **mean test
Dice 28.5 ± 21.27**, and neither the paper nor my search located a released
checkpoint or repository. So the card's fallback — a self-trained compact 2D
U-Net gated at held-out median Dice ≥ 0.20 — is not a fallback; it is the
plan. Two consequences:

- The deliverable sentence's definite article ("**The** final-infarct model")
  overstates. All rung-1 evidence will concern one weak self-trained
  surrogate. The winner's 28.5 Dice makes 0.20 for a compact 2D model a
  defensible performance floor, but the card and pitch must say "a
  representative multichannel surrogate," with model-family generalization
  explicitly deferred to rung 2 (the rung text already does this; the
  deliverable sentence and pitch do not).
- **Missing manipulation check:** a surrogate that has learned to ignore CBV
  or MTT (plausible — Tmax and CBF dominate clinical infarct prediction)
  cannot use their mutual residual, and every null becomes uninterpretable
  regardless of the sham positive control. The revision must add a frozen
  gate: per-channel occlusion/permutation reliance on the surrogate, with
  demonstrable reliance on at least two of the three identity-linked maps
  required before the intervention study proceeds.

## 5. Prior-work audit: citations check out; the gap survives a limited search

- **Kudo et al.** — verified exact: Radiology 2010;254(1):200-209, DOI
  10.1148/radiol.254082000, PMID 20032153; five commercial packages on
  identical acute-stroke source data produce significantly different maps.
  Supports the motivation (map values are implementation-contingent), though
  note it evidences *across-software* disagreement, not within-triplet
  identity violation (see §8).
- **ISP-Net** — verified exact: Comput Methods Programs Biomed 2022;215:106630;
  early fusion of native CTP, CBF, CBV, MTT, Tmax. The stated relation is
  accurate.
- **Konstas et al. Part 1** — verified (AJNR 2009, PMID 19270105); see §2 for
  the double edge.
- Adversarial search for the specific claim: the physics-informed-NN
  perfusion literature (e.g., arXiv 2011.12844, myocardial perfusion PINNs;
  arXiv 2410.19759, PINN CBF in infants) uses conservation laws as *fitting
  constraints during quantification* — the inverse direction. I found no work
  auditing whether a trained infarct-prediction model reads cross-map
  physical inconsistency as an uncertainty signal, and no ISLES'24
  map-consistency audit. "I did not find it" is not proof; novelty_confidence
  3 with NO_DUPLICATE_FOUND_LIMITED_SEARCH remains the honest ceiling, and
  the hard cap holds while the keystone is uninspected.

No prior-work rejection.

## 6. Data access and compute honesty

The keystone screen established the release is a single **99 GB `train.7z`**
archive (Zenodo record 16748089, files[0], 99,014,629,647 bytes). The card's
"modest download path" and data_readiness 4 ("with a modest download path")
are optimistic: the 10-case Stage 0 kill gate requires fetching and unpacking
the full archive first; on a Colab-class environment this is the dominant
cost and failure point of the whole card, ahead of the 10 GPU-hours. Not a
kill — the data are public and licensed for this — but the feasibility memo
must name the 99 GB up front and state where it will live. Data readiness is
better scored 3 than 4.

## 7. Endpoint discipline

Two gaps, both feasibility-memo-fixable:

- "Selective" and "residual-over-sham contrast" carry no frozen statistic or
  margin. This program has already been burned by threshold language left to
  interpretation time (idea-004, amended pin 2). The revision must commit
  that the memo freezes the exact paired statistic, the sham-comparison
  contrast, and pass/fail semantics before any model sees an edited map.
- Fitting k_case on "normal contralateral voxels" and reporting X inside the
  Tmax>6 s territory requires knowing the affected side per case. Say where
  laterality comes from (occlusion-site metadata vs the ground-truth mask).
  Using GT laterality is acceptable for an audit but must be declared; it is
  a mild endpoint dependence, not leakage, since no model training touches X.

## 8. Plain-pitch fidelity (opposite-family check) — two named defects

1. **"…yet stroke software can produce maps that locally disagree with it"**
   is stated as established fact. The card's verified support (Kudo) shows
   different *software packages* disagree with each other; local violation of
   the identity *within one package's released triplet* is precisely the
   unverified keystone (status NOT_INSPECTED, screen verdict UNVERIFIABLE,
   and §2's triviality risk runs the other way). The pitch asserts as
   background what the experiment's first gate exists to find out. It must
   hedge: "may locally disagree."
2. **"whether the prediction model notices"** mirrors the deliverable
   sentence's overclaim (§4): the tested object is a self-trained surrogate,
   not "the" model a reader will assume (a challenge winner or clinical
   tool). One added word fixes it ("a stroke prediction model trained on
   this data").

The remaining hedges survive translation ("asks whether," "could fail"), and
the software-change consequence is appropriately conditional.

## 9. What survives, and the revision bill

The kernel is genuinely good: an annotator-free, within-case, deterministic
invariant; a selectively removable signal; within-case interventions that
hold center/protocol/anatomy fixed; a designed sham positive control that
makes nulls meaningful; honest prohibited-conclusions. It is a real
differentiation from the dead site-signature ideas (037, 001-c08), because
the residual is computable and manipulable inside every case. The revision
must deliver, and only:

1. Interaction arm (matched-severity fixed perfusion-evidence edit at high-X
   vs low-X sites) as the carrier of the confidence-map deliverable; the
   projection/tangent contrast demoted to supporting evidence of residual
   dependence (§1).
2. Stage 0 algebraic-dependence test (stored MTT vs stored CBV/CBF) with a
   pre-committed quantization-only kill ruling (§2).
3. An MTT–Tmax (and other untouched channels) coherence treatment for the
   edit arms (§3).
4. Surrogate channel-reliance gate; "a representative surrogate" wording in
   card and pitch (§4).
5. 99 GB acquisition stated in feasibility; data_readiness 4 → 3 (§6).
6. Frozen selectivity statistic/margin commitment and declared laterality
   source (§7).
7. The two pitch hedges (§8).

---

```
NEAREST DEFENSIBLE HIGH-VALUE QUESTION: Does a multichannel ISLES'24 infarct
surrogate's prediction depend on the off-manifold (identity-violating)
component of the perfusion triplet, and does that component modulate its
response to matched perfusion-evidence edits?
RETAINS ORIGINAL MEDICAL MOTIVATION? YES
SHOULD IT BECOME A SEPARATE CANDIDATE? NO — it is idea 039 with the §1
interaction arm; splitting it would duplicate the card.
IS IT ACTUALLY WORTH DOING? YES — and its Stage 0 has a guaranteed floor:
whether ISLES'24's released MTT is algebraically dependent on CBF/CBV (three
channels, two degrees of freedom) is a publishable dataset-composition fact
for everyone fusing these maps, whichever way it comes out.
```

Note on the floor: the Stage 0 dependence audit is deliberately *not* spun
off as a separate candidate — it is this card's mandatory first gate, it
costs half a day plus the download, and registering it separately would spend
pipeline stages twice on the same measurement. If Stage 0 kills the
intervention (residual trivial), the dependence finding should then be
registered as a dataset-quality result under the charter's
benchmarking/dataset-quality lane rather than dying silently with the card.
