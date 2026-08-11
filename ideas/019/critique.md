# Critique — Idea 019: The fibrosis model may be counting holes at the pleural edge

```
FATAL OBJECTION: NONE that survives repair — but the card decodes a nonexistent
output: CT-CLIP has no "pulmonary fibrosis" score; the actual CT-RATE label is
"pulmonary fibrotic sequela," a report phrase dominated by post-infectious
scarring, and honeycombing-positive support in this cohort is unverified.
EVIDENCE: CT-RATE 18-label vocabulary (primary arXiv:2403.17834; exact list
quoted in arXiv:2603.06467 and arXiv:2607.02998); idea-007 precedent in evidence/decisions.md.
REPAIRABLE WITHOUT CHANGING THE QUESTION? YES
DECISION: ADVANCE TO REVISION
```

---

## 1. The endpoint is mislabeled, and it matters (strongest objection)

**Verified fact.** The CT-RATE label vocabulary that CT-CLIP's ClassFine head
is trained on contains 18 findings: medical material, arterial wall
calcification, cardiomegaly, pericardial effusion, coronary artery wall
calcification, hiatal hernia, lymphadenopathy, emphysema, atelectasis, lung
nodule, lung opacity, **pulmonary fibrotic sequela**, pleural effusion, mosaic
attenuation pattern, peribronchial thickening, consolidation, bronchiectasis,
interlobular septal thickening. There is no "pulmonary fibrosis" label.
Verification status: I could not fetch the primary PDF (arXiv:2403.17834) in
this session; the list is quoted identically by two independent papers that use
CT-RATE ([arXiv:2603.06467](https://arxiv.org/pdf/2603.06467),
[arXiv:2607.02998](https://arxiv.org/pdf/2607.02998)). Revision must confirm
against the primary label CSV header after dataset gating is accepted.

**Source-supported interpretation.** "Fibrotic sequela" is report language for
the residue of prior disease — post-infectious/post-inflammatory bands, apical
scarring, post-TB change — in a general Turkish hospital population (CT-RATE
originates from Istanbul Medipol University Mega Hospital, per the
[HF dataset card acknowledgments](https://huggingface.co/datasets/ibrahimhamamci/CT-RATE)).
That is a much broader and mostly *non-UIP* entity. The card's medical framing
(honeycombing changes UIP interpretation and prognosis; medical_relevance = 5)
presumes the score is an ILD/fibrosis score. It is not; it is a
"scarring-mentioned-in-report" score. Two consequences:

- **Prior plausibility drops.** If most positive labels are linear scarring
  without cysts, the model has little training pressure to encode honeycomb
  topology for this head. The hypothesis is not dead — honeycomb cases are a
  subset of label-positives and may be high-confidence ones — but the card's
  framing oversells it.
- **Prevalence/power is now the second keystone.** The 250-test-scan erasure
  plan assumes honeycombing-positive support. If honeycombing prevalence in a
  general hospital cohort is on the order of 1–3%, an unenriched 250-scan set
  contains a handful of positives. The card lists "enough thin-slice
  honeycombing" as an unverified claim; it is actually a gate that can be
  checked **for free** (section 6) and must be checked before any design work.

This is the exact error of idea 007 ("CT-CLIP has no mosaic attenuation head —
card claimed a nonexistent output," evidence/decisions.md 2026-08-05), which
was survivable there and is survivable here: the deliverable sentence names
CT-CLIP and honeycombing, not the phrase "fibrosis score," so renaming the
endpoint and downgrading the UIP framing repairs the card without changing the
question's identity under the 2026-08-10 claim-identity rule. But the repair is
mandatory, and medical_relevance = 5 does not survive it.

## 2. The primary rung-1 instrument (linear direction erasure) has weak causal semantics

Three distinct problems, none addressed by the card's nuisance-direction
controls:

- **Correlated-feature removal.** Erasing a linear direction removes everything
  correlated with it, not the concept alone; this is the standard critique of
  amnesic-probing/INLP-style interventions (Elazar et al., *Amnesic Probing*,
  TACL 2021; LEACE, arXiv:2306.03819 — both cited from memory, method-critique
  not medical claims). In a referral-enriched cohort, honeycomb topology is
  strongly correlated with overall fibrotic extent and severity. The learned
  "topology direction" will substantially overlap the severity axis, so
  "selective" erasure is likely ill-conditioned. Erasing matched nuisance
  directions *measures* the collinearity; it does not remove it.
- **Off-manifold embeddings.** A frozen classifier head applied to a
  projected-out embedding is being evaluated out of distribution. This is
  idea-006's fatal error (extreme intervention → OOD → neither direction
  identifies reliance) transplanted from voxel space into latent space. The
  portfolio has already rejected this move once; the card does not explain why
  latent-space OOD is more defensible than image-space OOD.
- **Consequence for the "decisive" negative.** The anticipated negative is
  classified decisive, with negative_result_value = 5. In the likely regime
  where topology and reticulation/severity directions are substantially
  collinear, a topology-null/reticulation-positive result is
  **sensitivity-limited, not decisive** — it may only mean the decomposition
  failed. Decisiveness requires prespecified encoding gates *and* a maximum
  admissible collinearity between frozen directions, neither of which is in
  the card. negative_result_value should be 3 pending those gates, and
  identifiability 4 → 3.

Portfolio note: representation-erasure is already at ×3 on the homogenization
watch. A revision that replaces or supplements erasure with a natural-paired
readout (section 6) is both scientifically and portfolio-wise better.

## 3. Mimic separability may be unverifiable even in Stage 0

The keystone screen honestly reports `UNVERIFIABLE`. But it treats the audit as
purely a preservation question. The harder half is the **reference problem**:
Stage 0 proposes to establish that the topology measure separates honeycombing
from paraseptal emphysema and traction bronchiolectasis "without human labels"
— separates it *against what ground truth*? With no reference standard, Stage 0
can show the measure is stable and non-degenerate, not that it measures
honeycombing. Two defensible escapes, both allowed by the charter's "existing,
citable tool" clause:

- An off-the-shelf honeycombing/fibrosis segmentation model with released
  weights (deep-learning honeycombing quantifiers exist, e.g. the AJRCCM 2024
  IPF progression work, [DOI 10.1164/rccm.202311-2185OC](https://www.atsjournals.org/doi/full/10.1164/rccm.202311-2185OC);
  CALIPER itself is proprietary/Imbio). Whether any has *public weights* is
  unverified and must be checked in revision — if one exists, it can serve as
  the convergent reference for the bespoke topology instrument, or replace it.
- Report-text mentions of "honeycomb" as an **exploratory-only** convergent
  check (reader-derived, so never the primary readout; see section 6).

Also unstated: excluding traction bronchiolectasis requires airway
segmentation, and distal airway segmentation on 0.75×0.75×1.5 mm resampled
routine CT of fibrotic lungs is exactly where such tools fail. The wall
completeness that distinguishes multilayer honeycombing from single-layer
paraseptal emphysema (~1 mm walls on 3–10 mm cysts) is the first casualty of
thick native slices; trilinear resampling to 1.5 mm cannot restore a wall a
5 mm native reconstruction never resolved. The thin-slice stratum is not a
robustness check — it is the only stratum where the instrument can work, and
its size is unknown.

## 4. Rung target 3 rests on unnamed external data

Rung 2 → 3 requires "external ILD replication" with no named, obtainable
dataset. OSIC (Kaggle) has fibrosis CTs but is a progression cohort with
domain shift for CT-CLIP; no other candidate is named. Under this program's
standards an unnamed replication resource is vapor: the honest target within
obtainable data is **rung 1** (the model uses subpleural cyst topology), with
rung 2 partially addressed by reconstruction-pair stability inside CT-RATE.
The card's `rung.move_up` should be rewritten accordingly.

## 5. Data access and compute — mostly fine, one stale ledger note corrected

**Verified fact.** Trained checkpoints are obtainable: the official CT-CLIP
README links `models/CT-CLIP-Related/CT-CLIP_v2.pt` inside the gated CT-RATE
HF repo, with CT-CLIP, VocabFine, and ClassFine variants. The 2026-08-04
ledger note "checkpoints are not on the authors HF account" is stale or
referred only to release assets; idea 004/013 planning already assumed local
inference, and the asset path is now confirmed. Gated-but-obtainable is
consistent with the standing treatment of CT-RATE (ideas 004, 006, 013).

Compute: 370 volumes ≈ 50–100 GB download plus inference plus cubical
persistence in "one Colab Pro+ session" is optimistic by maybe 2–3×, but this
is the same envelope class as approved ideas. Not a rejection ground.

## 6. The low-hanging fruit the card missed (and the easier version)

CT-RATE releases **English report text and per-volume RadBERT labels for free,
without downloading a single image**. That yields a Stage 0a that costs hours
and gates everything downstream:

- Regex the validation reports for honeycomb terms → direct measurement of
  honeycombing-mention prevalence, the power gate of section 1.
- Cross-tabulate honeycomb-mention against the fibrotic-sequela label →
  what fraction of label-positives are even candidate honeycomb cases.
- (Exploratory only, reader-derived, never the primary readout:) does the
  ClassFine fibrotic-sequela score separate honeycomb-mentioning fibrosis from
  fibrosis-without-honeycomb? A null here — score indifferent to the report's
  honeycomb mention — already substantially deflates the hypothesis before any
  topology instrument is built. Label-leakage caveat: this stratification uses
  report text, so it gates and motivates but cannot confirm.

Stage 0b is then the preservation audit on ~20 thin-slice honeycomb-mention
volumes (native vs final tensor), before committing to the 370-volume design.

**Easier rung-1 design that avoids erasure entirely:** idea 004 has already
identified 425 geometry-matched same-acquisition kernel pairs. Sharp vs soft
kernels change apparent wall completeness — the exact substrate of the topology
measure — while anatomy, patient, site, protocol, and positioning are held
fixed. Within pairs: does the change in fibrotic-sequela score track the change
in measured subpleural cyst topology beyond generic sharpness/noise metrics?
This is the charter's praised structural move (model compared to itself on
identical anatomy, no labels in the readout), reuses idea 004's Stage 0
inventory, and is a natural-paired design rather than a fourth
representation-erasure entry. Its limitation is honest: it identifies
sensitivity to reconstruction-rendered wall topology, not native honeycombing
use, so it complements rather than replaces a topology-association arm.

## 7. Checks that pass

- **Circularity:** X (deterministic voxel/graph topology) is not a re-encoding
  of the fibrotic-sequela label or of the score. Passes, unlike idea 010.
- **Annotation provenance:** the primary readout uses no reader labels; report
  text enters only as an exploratory gate. The dominant program failure mode
  does not apply — provided revision keeps the report-derived stratification
  out of the confirmatory claim.
- **Prior-work overlap:** bounded searches found no study testing a frozen
  foundation model's reliance on honeycomb topology. Closest new neighbor to
  add: persistent-homology analysis of longitudinal CT fibrotic features in
  COPD ([ERJ, early 2026](https://publications.ersnet.org/content/erj/early/2026/02/26/1399300301630-2025))
  — descriptive PH on lung CT, no model-reliance test; plus DL honeycombing
  quantification (section 3). The novelty delta survives; novelty_confidence
  stays capped at 3.
- **Keystone procedure:** the screen's `UNVERIFIABLE` verdict and
  residual-assumption check are honest and correctly identify preservation as
  the load-bearing fact. No wrong-keystone error here — though section 3 adds
  the reference-standard problem as a co-equal part of the same keystone.

## Required in revision

1. Rename the endpoint to the pulmonary-fibrotic-sequela score everywhere;
   verify the label list against the primary CSV; downgrade medical_relevance
   (5 → 3) and rewrite the UIP framing as conditional on honeycomb-positive
   support existing in CT-RATE.
2. Add free Stage 0a (report-text prevalence and stratification gate) before
   any image download; make its outcome a numbered kill condition.
3. Demote or replace linear erasure as the primary rung-1 instrument; if
   retained, prespecify encoding gates and a maximum admissible direction
   collinearity, and reclassify the anticipated negative as
   sensitivity-limited unless those gates pass (negative_result_value 5 → 3,
   identifiability 4 → 3).
4. Name the mimic-separability reference (released-weights honeycombing
   segmenter, verified, or convergent report-text check labeled exploratory).
5. Retarget rung 1 within CT-RATE; strike the unnamed external replication
   from the rung ladder.
6. Consider the kernel-pair natural-paired arm reusing idea 004's 425 pairs.

---

```
NEAREST DEFENSIBLE HIGH-VALUE QUESTION: Does CT-CLIP's pulmonary-fibrotic-
sequela score track measured subpleural cyst topology — gated first by a free
report-text prevalence check, and tested within geometry-matched kernel pairs
where anatomy is held fixed — rather than generic density or sharpness?
RETAINS ORIGINAL MEDICAL MOTIVATION? PARTLY — honeycombing-vs-mimic remains
the payload, but the UIP/prognosis framing shrinks to what a scarring-sequela
score can support.
SHOULD IT BECOME A SEPARATE CANDIDATE? NO — same deliverable sentence and
prohibited conclusions; this is narrowing and instrument repair, which is
revision-in-place under the 2026-08-10 claim-identity rule.
IS IT ACTUALLY WORTH DOING? YES — Stage 0a costs hours, uses already-released
text and labels, and either kills the idea cleanly (no honeycomb support) or
buys a genuinely novel, annotation-free model-decoding study; that
cost-to-decisiveness ratio is the best currently available in this idea.
```
