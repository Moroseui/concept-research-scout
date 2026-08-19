# Critique — Idea 041: The roughness of a heartbeat through starved tissue

```
FATAL OBJECTION: NONE
EVIDENCE: Keystone verified on the primary record (PMID 40824507); all three
  novelty_neighbors carry wrong author names but correct identifiers and
  correct content descriptions; no existing model-use test of this feature
  was located; the erasure estimand and the claim object are ambiguous.
REPAIRABLE WITHOUT CHANGING THE QUESTION? YES
DECISION: ADVANCE TO REVISION
```

## 1. What survives attack

The keystone is genuinely strong and genuinely inspected. The feature paper
(DOI 10.1007/s11548-025-03500-3, PMID 40824507) computed voxelwise Higuchi
fractal dimension on the exact 149-case public ISLES'24 cohort and reported
tissue-state separation (p < 0.001; penumbra-vs-normal AUC 0.732). That is a
verified fact, per the keystone screen's quoted primary sources. The
`INSPECTED_TRUE` status supporting feasibility 4 and novelty_confidence 4 is
legitimate under the hard-cap rule.

The novelty delta also survives. A targeted search (2026-08-19) for any
erasure, ablation-of-concept, or use-test of fractal dimension in a
CTP model found association work and ordinary architecture-ablation studies
only — nothing that intervenes on a trained model's representation of this
descriptor. Closest hits: the feature paper itself
([Springer](https://link.springer.com/article/10.1007/s11548-025-03500-3)),
the raw-temporal-network comparison
([Frontiers](https://www.frontiersin.org/journals/neuroscience/articles/10.3389/fnins.2022.1009654/full)),
and spatio-temporal outcome-prediction models
([MedIA](https://www.sciencedirect.com/science/article/abs/pii/S1361841522002389)).
"I did not find it" is not proof of absence, but the card's stated delta —
association exists, use-test does not — matched every source I could reach.

The card is also unusually honest in its own demotions: it concedes that
linear erasure removes X-correlated features generally, and pre-demotes the
positive conclusion to "dependence on an X-associated representation."

## 2. Objections, in decreasing order of severity

### 2.1 Fabricated author names on all three novelty neighbors (verified; repairable)

Every author attribution in `novelty_neighbors` is wrong; every identifier
and every content description is right:

- "Lim et al." → actually **Ichikawa, Kondo, Yokoyama** (PMID 40824507).
  Caught by the keystone screen; recurs throughout the card
  (`X_measurement`: "the frame-count-adapted kmax procedure of Lim et al.").
- "Robben et al." → DOI 10.3389/fnins.2022.1009654 is actually **Winder,
  Wilms, Amador, Flottmann, Fiehler, Forkert**, Front. Neurosci. 2022.
  Verified against the Frontiers page 2026-08-19. (Robben et al. is a
  different, real final-infarct paper — the confusion is plausible and
  therefore dangerous.)
- "van Os et al." → PMID 32501132 / PMC7922756 is actually **Klug, Dirren,
  Preti, Machi, Kleinschmidt, Vargas, Van De Ville, Carrera**, JCBFM 2020.
  Verified against PMC 2026-08-19.

The described *relations* all check out: Winder et al. does compare
concentration-time-curve networks against residue-curve networks and does
correlate learned temporal features with conventional maps (finding CTC
features "noticeably weaker" correlated — supporting the card's premise that
raw temporal encoders learn non-map information); Klug et al. does show
regional context improves infarct prediction (AUC 0.89 vs 0.78). So the
literature basis is sound but every name is invented. This is a systematic
citation-hygiene failure, not a novelty failure. Repair: replace all three
author strings; identifiers stand.

### 2.2 The claim object is ambiguous: "the final-infarct model" is a model the lab trains itself

The deliverable sentence says "**The** final-infarct model is using temporal
fractal dimension…" — definite article, as if an existing deployed or
challenge-winning model were being probed. The smallest decisive experiment
trains a **shallow 2D+time U-Net from scratch on 20 cases**. A positive
result therefore establishes: *a small raw-temporal network trained by us on
this cohort relies on an FD-associated direction*. That is a legitimate
existence proof (rung 1, as targeted), but it is a materially weaker
sentence than the deliverable implies, and the interest score of 5 is priced
against the stronger reading. The research question itself uses the
indefinite article ("Is **a** raw-CT-perfusion final-infarct model…"), so
the question is repairable without identity change: align the deliverable
sentence to "a raw-temporal final-infarct model trained on ISLES'24," and
state explicitly that no claim transfers to challenge-winning models without
the rung-2 replication.

### 2.3 The erasure estimand is stated in two incompatible spaces

`use_vs_association` says "replace only the component **of the time curve**
that predicts Higuchi fractal dimension using a cross-validated concept
direction **in the model's temporal encoder**." Input-space curve editing
and encoder-representation erasure are different interventions with
different confounds and different conclusions: an input-space edit must
demonstrate the edited curves stay in-distribution (the charter's standing
concern; cf. the idea-006 lesson), while a representation-space erasure
cannot literally "preserve curve area, peak time, peak height" — those are
input properties, and what is preserved in feature space is only their
decodable correlates. The card currently borrows the strengths of both
framings and the obligations of neither. Repair: pick one (the scores and
template say representation-erasure), restate the preserved-quantity list as
*decodability of the listed curve properties from the edited representation
is unchanged*, and add that check as an explicit gate.

### 2.4 Identifiability: the phantom result cuts against the card as much as for it

The same abstract that verifies the keystone reports FD–CBF correlation
**rho > 0.9** in the phantom after kmax optimization. If FD is that close to
a monotone function of flow, then within a CBF decile the residual FD
variance may be mostly noise-driven, and "erase FD while matching CBF" risks
being either vacuous (nothing decodable left to erase within strata) or a
noise-sensitivity test wearing a fractal costume. The patient-side result
(FD outperforms CBF for penumbra-vs-normal, p < 0.001) shows FD carries
*some* non-CBF information in real data, so the design is not doomed — but
the card needs a preregistered **within-stratum decodability gate**: before
any erasure is interpreted, show FD is decodable from the frozen encoder
*within CBF deciles* with nontrivial accuracy, else declare the study
sensitivity-limited. Without that gate this dies like the charter's eleven
IDENTIFIABILITY_FAILURE kills; with it, the failure mode is detected rather
than narrated. This is the single most important revision.

### 2.5 The performance gate is a real risk, not a formality

Winder et al. — the card's own architecture source — reached mean Dice
**0.296** with their best raw-CTC model on a full clinical cohort. The card
demands validation AUC ≥ 0.70 within Tmax > 6 s tissue from 20 training
cases. Voxelwise AUC within hypoperfused tissue is an easier target than
whole-lesion Dice, and 2D+time patches multiply effective samples, so the
gate is not obviously unreachable — but the most probable single failure
point of the whole experiment is this gate, and the card's feasibility 4
("first result in days") does not price it. The anticipated-negative
classification (decisive only if all gates pass) is correctly constructed;
the risk is not a validity flaw but a substantial probability of an
uninformative stop. State it as such in the card.

### 2.6 Prior-legwork score is inflated by one rubric level

`prior_legwork: 5` requires "data/code/labels/checkpoints ready." The
keystone screen established the opposite for code: the feature paper's code
is available "upon reasonable request" only — no public artifact. There are
no checkpoints; the model is trained from scratch; the Higuchi recipe (incl.
the optimized kmax) must be reproduced from methods text or author
correspondence. `X_measurement`'s phrasing "has already been run on all 149
public ISLES'24 perfusion studies" is true of the *paper* but connotes an
available asset. Honest value is 3 (some reusable assets). This moves the
priority score from 3.8 to ~3.6 — it does not change the decision, but the
rubric requires the correction.

### 2.7 Data-staging assumption unverified

The card claims a 25 GB staged subset out of the ~99 GB archive. Whether the
Zenodo release permits per-case (or per-file) download rather than a
monolithic archive pull was not verified anywhere in the card or screen. If
the release is monolithic, the honest cost is one ~99 GB download (disk and
bandwidth, not compute). Feasibility memo must verify download granularity
before the envelope is quoted. Not fatal; charter requires honest cost.

### 2.8 Plain-pitch fidelity (named defects)

Two failures against the card:

1. **Conclusion strength.** The pitch ends: "if selectively erasing its
   internal representation changes forecasts after ordinary blood flow,
   curve size, and scanner noise are controlled, **it does** [use that
   roughness]." The card itself demotes the positive conclusion to
   "dependence on an X-associated representation" because linear erasure
   removes correlated temporal features. The pitch's unconditional "it does"
   is exactly the hedge-dropping the fidelity rule prohibits.
2. **Claim object.** "This experiment asks whether **a prediction model**
   actually uses that roughness" invites the reading that an existing,
   externally meaningful model is being audited. The model is a small probe
   the lab trains itself (see 2.2). The pitch must say so.

### 2.9 Portfolio note (not a defect of this card)

This is the portfolio's seventh representation-erasure design (concentration
watch: 6 before this). The card is among the better-armed instances of the
template, but the homogenization signal belongs in the record: a positive
here and a positive on idea-039 or -042 would be three results resting on
the same linear-erasure epistemology and sharing its blind spot.

## 3. Easier versions examined

- **Association-only fruit (exists, mostly picked):** FD's incremental value
  over the standard map set for predicting the *final infarct mask* (rather
  than the feature paper's tissue-class discrimination) could be computed
  with logistic models on the already-measured feature — no GPU, no erasure.
  It is publishable-adjacent but is exactly the association-vs-use
  distinction the charter exists to police; as a standalone candidate it is
  a step backward. As a **Stage-0 byproduct** (it falls out of reproducing
  FD plus fitting baseline maps), it is nearly free and worth logging.
- **Input-space necessity arm (recommended addition, not replacement):**
  resynthesize each voxel curve from a smooth parametric fit (e.g.,
  gamma-variate) with moments/area/peak preserved, and measure model-output
  change — an information-necessity test at the input that does not inherit
  linear-erasure circularity. One caution the revision must carry: naive
  spectrum-preserving surrogates can *preserve* Higuchi FD (FD tracks
  spectral slope for many processes), so the resynthesis procedure must be
  validated to actually move FD while holding the moment set — that
  validation is cheap and itself diagnostic. This strengthens the same
  question; it is not a separate candidate.
- **No cheaper checkpoint-based version exists:** there is no public
  raw-4D-CTP final-infarct checkpoint (this is precisely why idea-022 is
  PAUSED), so "probe an existing model" is not an available shortcut; small
  self-training is genuinely the minimal instrument.

## 4. Constructive close

```
NEAREST DEFENSIBLE HIGH-VALUE QUESTION: Does a small raw-temporal
final-infarct network trained on ISLES'24 depend on an FD-associated
representation beyond CBF and curve moments — tested by representation
erasure gated on within-CBF-stratum decodability, plus an input-space
curve-resynthesis necessity arm?
RETAINS ORIGINAL MEDICAL MOTIVATION? YES
SHOULD IT BECOME A SEPARATE CANDIDATE? NO — it is this candidate, revised;
the question's indefinite article already covers it.
IS IT ACTUALLY WORTH DOING? YES — the expensive association legwork is
published on the exact cohort, the use-test is verified absent from the
literature, and either gated outcome (uses it / decodable-but-unused)
is informative about what raw-temporal stroke models extract; the
association-only smaller version is NOT worth doing as a standalone.
```

### Revision requirements (summary for the next stage)

1. Correct all three neighbor author attributions (Ichikawa; Winder; Klug)
   and every in-card "Lim et al." reference. Identifiers stand.
2. Align the deliverable sentence to the self-trained probe model; scope
   transfer claims to rung 2 explicitly.
3. Choose the representation-space erasure framing; restate preserved
   quantities as decodability-preservation gates.
4. Add the preregistered within-CBF-stratum FD-decodability gate (the
   anti-vacuity gate) ahead of any erasure interpretation.
5. Add the input-space curve-resynthesis necessity arm with its FD-movement
   validation check.
6. Lower prior_legwork to 3; reword "already been run" to "published on";
   recompute priority (~3.6).
7. Feasibility memo must verify Zenodo download granularity before quoting
   the 25 GB staging envelope, and must price the AUC-gate failure risk
   (Winder et al. Dice 0.296 as the sobering benchmark).
8. Rewrite the plain pitch: conditional conclusion ("depends on an
   FD-associated representation"), and name the probe model as self-trained.
