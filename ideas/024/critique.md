# Critique — Idea 024: The capillary traffic jam hidden behind the same mean transit time

```
FATAL OBJECTION: The study has no subject and no instrument — no publicly
available trained ISLES'24 model consumes raw 4D CTP, and the proposed
nonparametric residue-variance estimator of CTH was explicitly considered and
rejected, for CT by name, by the originators of the CTH construct.
EVIDENCE: arXiv 2408.10966 (results table + team repos: raw-CTP teams released
no weights); Mouridsen et al. 2014, JCBFM, DOI 10.1038/jcbfm.2014.111.
REPAIRABLE WITHOUT CHANGING THE QUESTION? NO
DECISION: REJECT
```

---

## 0. What was verified for this critique

Two web-research passes were run this session (2026-08-17), with primary
sources fetched and quoted. Verification status is marked per claim below:
**[fetched]** = page/full text retrieved and quote checked; **[snippet]** =
search-result level only. Per collaborator rules, "I did not find it" claims
are marked as bounded-search absence, not proof.

## 1. Fatal objection A — the model the card proposes to freeze does not exist

The card's smallest decisive experiment says "freeze one already trained
raw-CTP model," and its compute envelope explicitly excludes retraining
("one frozen model, batch-size-one inference, and no retraining"). The card
listed this as an unverified claim. It is now inspected, and adverse:

- Of the twelve ISLES'24 finalist teams, three consumed raw 4D CTP: Ninjas
  (rank 3), HSK-CoreFinders (rank 6), MIPLAB-PrediCTP (rank 8). **None
  released trained weights.** The Ninjas repo
  (github.com/jaymoz/ISLES-Challenge-2024) contains training and inference
  code only, with instructions to train 5-fold from scratch **[fetched]**.
  The PrediCTP repo (github.com/kimberly-amador/ISLES24-PrediCTP) is
  code-and-configs only **[fetched]**. HSK-CoreFinders has no findable repo
  **[snippet-level absence]**.
- The only teams with downloadable weights — Kurtlab (rank 1) and
  AMC-Axolotls (rank 2), both via informal Google Drive links — consume
  **derived perfusion maps + CTA (+NCCT)**, not the raw 4D series
  **[fetched: both repos and the Kurtlab paper, arXiv 2505.18424]**.

So the audit subject must be trained from scratch on 149 public cases. That
is itself outside the card's stated compute envelope (a 4D nnU-Net 5-fold
training run is not "one Colab GPU session... no retraining") — the card is
internally inconsistent with the world as inspected.

### 1b. Worse: the premise inverts, not just the logistics

This is an entry-point-2 candidate, which requires "a model that merely
performs well." The inspected record says raw-CTP ISLES'24 models perform
*poorly*, absolutely and relatively:

- Challenge paper, verbatim: "models utilizing standard deconvolution-derived
  perfusion maps consistently outperform those trained directly on raw 4D
  CTP series" **[fetched, arXiv 2408.10966]**.
- PrediCTP (raw 4D CTP) reports Dice 0.20 on 143 ISLES'24 patients vs ~0.285
  for the map-based winner **[fetched repo; Springer chapter
  10.1007/978-3-031-81101-2_9 snippet]**.
- Independent cohort: Winder et al. 2022 (Front Neurosci, 145 patients) found
  raw-curve models not significantly different from map-based ones (Dice
  0.296 vs 0.287) **[fetched]**.

The card's motivating premise — that the raw time series carries usable
physiological information the released maps compress away — is exactly what
the existing evidence fails to support. A Dice-0.20 self-trained model is a
poor subject for detecting selective use of a *second moment* of the residue
function: any null is dominated by "this model barely uses anything," which
demotes the anticipated negative from sensitivity-limited to
**uninterpretable** (negative_result_value cap: 2, not the card's 3).

## 2. Fatal objection B — the instrument is construct-invalid, per the construct's inventors

The card's X is "the dispersion of deconvolved residue-function transit
times" from "one preregistered delay-insensitive [nonparametric] method,"
gated by stability across two regularizers and two AIF choices. The primary
literature on this is direct and adverse:

- Mouridsen, Hansen, Østergaard et al. 2014 (JCBFM, DOI
  10.1038/jcbfm.2014.111), the paper that operationalized CTH measurement,
  rejected exactly this estimator, naming CT: "Owing to the inherent
  signal-to-noise constraints of computerized tomography and DSC-MRI...
  the use of model-free approaches may be suboptimal because of the
  unphysiological oscillations in the estimated residue function, which
  would propagate to its derivative and thereby CTH" **[fetched]**. They
  adopted a parametric Bayesian gamma-family model instead.
- Same source: SVD-family regularization "may stabilize CBF estimates" but
  is "not optimized to detect salient features of the residue function";
  in their simulations sSVD/oSVD MTT bias under high CTH is ~6–7 s and
  **virtually independent of SNR** — i.e., a structural artifact of the
  estimator class, present even at SNR=100 **[fetched]**.
- Calamante et al. 2003 (MRM): "the deconvolved R shape obtained using SVD
  is dominated by oscillations and fails to characterize the shape in the
  presence of dispersion" **[fetched abstract]**.
- A DSC/DCE review states flatly: "The CNR of DSC-MRI data is insufficient
  to enable reliable estimation of h(t) and necessitates the use of a
  parametric estimation of the residue function" **[fetched,
  PMC6538021]** — and CTP CNR is generally worse than DSC-MRI (inference).

Two structural consequences for the card's design:

1. **The Stage-0 stability gate cannot detect this failure.** Both proposed
   regularizers (oscillation-index, Tikhonov-type) impose smoothness a
   priori; the recovered "shape" can be regularizer-dominated and therefore
   *concordant across regularizers* while carrying little microvascular
   information. The SNR-independence of the bias is precisely the property
   that makes a reliability gate blind to it. Stable-but-invalid passes the
   gate. The card's own alternative-explanation entry ("CTH is deconvolution
   noise → the stability gate is fatal if it fails") tests reliability and
   silently substitutes it for validity.
2. **h(t) = -dR/dt from an oscillating R(t) is not a distribution.** Negative
   lobes make its "variance" undefined without ad-hoc monotonization —
   a hidden model inside a supposedly model-free measurement (inference,
   from the fetched oscillation findings).

Bounded-search absence claim: no published paper was found computing CTH
from CTP via nonparametric residue-function variance, and no validation of
that surrogate in any modality. Every verifiable human CTH paper uses the
Aarhus parametric Bayesian estimator on MRI perfusion.

### 2b. The card's anchor precedent is misattributed

Potreck et al. 2019 (DOI 10.1007/s00330-019-06064-4), the card's closest
prior work and its implicit feasibility precedent for CTH-in-stroke, is a
**DSC-MRI (PWI) study, not CT perfusion**: "We retrospectively calculated
CTH maps for 131 consecutive patients... who had a relevant MRI PWI-DWI
mismatch" **[fetched abstract via Europe PMC]**; its reference chain and the
companion Heidelberg paper (Mundiyanapurath 2016, PLOS One, **[fetched]**)
point to the Aarhus parametric Bayesian pipeline (PGUI/penguin). The card's
`verified_fact` for Potreck is worded carefully enough to be technically
true, but the idea's plausibility rests on a CTP precedent that does not
exist. The keystone screen's residual ("the published clinical association
does not validate the measurement on ISLES'24") understated this: the
association is on a different modality with a different, parametric
estimator.

## 3. Objection C — dispersion masquerade blocks the deliverable sentence even with a valid estimator

The deliverable sentence names "capillary transit-time heterogeneity, a
dispersion property of **microvascular** passage." But macrovascular bolus
dispersion between the AIF site and the tissue produces an effective residue
function "whose shape reflects the distortion of the bolus as well as the
hemodynamic tissue status" (Willats, Connelly, Calamante 2006, MRM
**[fetched abstract]**), and dispersion manifests in deconvolution exactly as
a slower-decaying R(t) — i.e., inflated apparent transit-time variance
**[fetched, PMC9463354]**. Delay-insensitive (block-circulant) deconvolution
removes *delay* sensitivity only; no source claims it removes *dispersion*,
and Calamante 2000 states dispersion correction "requires a model for the
vasculature" **[fetched abstract]**. The ISLES'24 population is LVO stroke
with collateral routing — the setting in which macrovascular dispersion is
maximal precisely in the threatened tissue the card aggregates over
(Tmax>6 s region).

Consequence: even a clean dose-ordered response to dispersion edits would
identify "the model responds to transit-time dispersion in the tissue
curves," with micro- versus macro-vascular attribution unavailable. The
capillary claim in the deliverable sentence is unreachable on this data.
Under the 2026-08-10 claim-identity rule, fixing this changes the
deliverable sentence — which is REJECT (superseded), not
revision-in-place. This alone answers "repairable without changing the
question" with NO.

## 4. Objection D — the counterfactual is over-constrained and built with the broken tool

Secondary, recorded for any successor: the paired edits must alter
residue-time variance while *exactly* preserving curve integral, first
moment, peak time, Tmax>6/Tmax>10 volumes, and spatial support. The edits
can only be constructed by deconvolving, editing, and reconvolving through
the same estimator objection B invalidates; the edit magnitude ("natural
interquartile range" of CTH) is calibrated in units of an invalid
measurement; and the in-distribution gate (held-out real-versus-edit
discriminator "near chance" for 4D temporal edits) is a substantial
research project in itself, of the same kind the portfolio has repeatedly
flagged (idea 006's OOD lesson, idea 008's sham-tolerance gate). Also note
the released maps were generated by icobrain cva (FDA-cleared, closed)
**[fetched, arXiv 2408.10966]**, so "preserving the standard summaries" can
only mean preserving a *reimplementation's* summaries, not the released
maps.

## 5. Keystone audit — the wrong-keystone pattern, fourth occurrence

The keystone screen honestly returned UNVERIFIABLE on temporal adequacy, and
its residual-assumption check concluded the residual "is identical to the
stated keystone." That conclusion was wrong, in the charter's canonical
direction: temporal adequacy was the *nearest checkable thing*. The two
load-bearing assumptions sitting upstream were (1) a performant, obtainable
raw-CTP model exists to audit, and (2) residue-function variance from
nonparametric deconvolution is a valid estimator of CTH at all. Both were
checkable today from public sources; both, now inspected, are adverse. This
is the same error class as ideas 005 and 006: the easy adjacent fact
(4D CTP exists at 1 Hz — true) was inspected while the inference-bearing
facts were assumed.

## 6. Score corrections (for the record)

- `feasibility` 3 → 1: subject model must be trained from scratch, outside
  the stated compute envelope; instrument unvalidated anywhere.
- `identifiability` 3 → 1–2: dispersion masquerade is unaddressed by the
  design; the stability gate tests reliability, not validity.
- `negative_result_value` 3 → 2 (cap): null on a self-trained Dice-0.20
  model is uninterpretable.
- `prior_legwork` 4 → 2: the "existing" frozen model does not exist; the
  CTH construct's tooling is parametric, MRI-based, and not pinned as
  obtainable.
- `medical_relevance` 5 stands as motivation, but the challenge's own
  aggregate finding (maps ≥ raw CTP) is evidence *against* the premise that
  this dataset's models exploit temporal microstructure.
- `dies_like_prior`: the card named idea-016 (IDENTIFIABILITY_FAILURE).
  Partially right, but the primary kill is closer to DATA_ACCESS (no
  obtainable checkpoint — like idea 018) compounded by a mode this ledger
  has not yet named explicitly: **instrument invalidity** — X itself cannot
  be measured with any released, citable tool, which is a violation of the
  charter's hard constraint on X ("computed from the image by an existing,
  citable tool or a well-defined measurement"; a measurement the construct's
  originators rejected as unphysiological is not well-defined).

## 7. Easier-version search

Searched for explicitly, per the stage task:

1. **Audit the released map-based winners instead.** Kurtlab (rank 1) and
   AMC-Axolotls (rank 2) have downloadable weights and consume
   CBF/CBV/MTT/Tmax + CTA. This is genuine low-hanging fruit — public data,
   public weights, no training — but it cannot carry *this* question: CTH
   is by definition the temporal information the maps compressed away.
   Map-based model-use questions are already represented in the backlog
   (isles24-scout-002-c02 "healthy hemisphere is the ruler," shortlisted as
   idea 021; isles24-scout-002-c07 "Little's law," shortlisted as idea 023),
   and idea 022 (bolus truncation) holds the temporal-coverage territory.
   A new candidate here would duplicate existing backlog, not rescue 024.
2. **Parametric-Bayesian CTH measurement feasibility on ISLES'24.** Replace
   the estimator with the validated gamma-family Bayesian one and first ask
   only whether CTH is recoverable on 1-Hz resampled CTP. This repairs
   objection B but not A (still no raw-CTP model worth auditing), not C
   (dispersion masquerade is a physics problem, not an estimator problem —
   and in LVO it is worst where it matters), and adds an unverified
   dependency (PGUI/penguin availability; the CTP-capable implementation is
   commercialized by Cercare Medical **[snippet]**). The result would be a
   measurement-methods study with no model-use question attached — outside
   this program's deliverable.
3. **Cross-model disagreement (raw-CTP vs map-based) on shared cases.**
   Still requires training the raw-CTP model; inherits objection A.

No formulation was found in which data, labels, code, *and a subject model*
already exist for a transit-time-dispersion use question.

---

```
NEAREST DEFENSIBLE HIGH-VALUE QUESTION: Whether the released rank-1
map-based ISLES'24 model (public weights) uses a named, map-computable
hemodynamic quantity — territory already occupied by shortlisted ideas
021/023, not by a CTH successor.
RETAINS ORIGINAL MEDICAL MOTIVATION? NO — the microvascular-dispersion
question cannot be asked of models that only see first-moment maps, and
that is the only model class with released weights.
SHOULD IT BECOME A SEPARATE CANDIDATE? NO — it already exists in the
backlog as ideas 021 and 023; registering a CTH-flavored duplicate would
be homogenization (counterfactual-synthesis is already at x12), not
coverage.
IS IT ACTUALLY WORTH DOING? The map-based audits already shortlisted are
worth doing; a CTH-specific easier version is not, because on this dataset
the construct has no valid instrument, no auditable subject, and the
challenge's own aggregate result is evidence against the premise.
```
