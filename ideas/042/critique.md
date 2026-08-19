# Critique — Idea 042: Delay is not dispersion

```
FATAL OBJECTION: NONE
EVIDENCE: The dispersion-edit constraint set (contract width while preserving
  area AND peak height) contradicts the card's own realism gate; the closest
  prior work (Amador et al., ISBI 2024, attention analysis of a raw-4D-CTP
  outcome model) is absent from the card despite being flagged in this
  program's own cycle-003 novelty audit; both are repairable.
REPAIRABLE WITHOUT CHANGING THE QUESTION? YES
DECISION: ADVANCE TO REVISION
```

## 1. What survives attack

The core question is genuine and well-posed. Delay and dispersion are
physically distinct transport properties (verified fact: Calamante et al.,
DOI 10.1002/mrm.20873, separates them explicitly and shows delay does not
determine dispersion), classical tissue predictors are sensitive to both
(Willats et al. 2012, DOI 10.1161/STROKEAHA.111.635888, found by the
cycle-005 audit as a closer neighbor than the card's own citations), and
raw-time networks exist that could in principle exploit post-alignment curve
shape (Winder et al., Front Neurosci 2022, DOI 10.3389/fnins.2022.1009654 —
full text confirmed by the cycle-005 audit to contain no perturbation or
curve-manipulation experiments). The novelty delta as stated — no located
work causally probes a trained raw-CTP model with transport-cost-matched,
factorized dispersion-only versus delay-only edits — survived my re-check
(see §3). The within-case paired design genuinely neutralizes the standing
IDENTIFIABILITY_FAILURE killers (center, scanner, injection, cardiac output
as *between-case* confounds), and the card's rung-1 cap with collateral
wording demoted to interpretation is the right instinct, though not carried
through to the deliverable sentence (§4).

The keystone screen's UNVERIFIABLE verdict is honest and correctly priced:
raw 4D CTP existence and 1 frame/sec cadence are verified; per-case
baseline/peak/washout coverage and within-delay dispersion variation are
not, and the card's Stage 0 gates (5 pre-arrival frames, peak ≥5 frames
before end, washout to ≤30% of peak, ICC ≥0.85, 90% of 20 cases) are
concrete and killable. Hard caps respected: feasibility 3 and
novelty_confidence 3 under NOT_INSPECTED.

## 2. Objections, in decreasing order of severity

### 2.1 The dispersion edit is over-constrained and collides with its own realism gate

`X_measurement`/`use_vs_association` specify a dispersion-only edit that
"contracts the aligned curve toward the arterial width while preserving
arrival time, area, peak height, and baseline noise power." This constraint
set is mathematically satisfiable only by driving the curve toward
flat-topped (boxcar-like) shapes: at fixed area and fixed peak height, the
minimum-variance curve is a boxcar, and if the arterial width lies below
that boxcar limit the edit is infeasible outright (inference from elementary
moment bounds; no source needed). Physically, a genuinely less-dispersed
bolus at the same delivered contrast (area ≈ CBV·k) has a **taller,
narrower** peak — the tissue curve is AIF ⊛ residue, a smooth gamma-like
family in which width and peak height are anticorrelated at fixed area.
The card's own realism gate is "interpolation between observed same-case
curves" plus nearest-neighbor feature distance — and observed same-case
curves live in exactly that physiological family. So the confirmatory arm
as specified either fails the realism gate (flat-topped curves have no
same-case neighbors) or the gate must be loosened until it stops binding.
The card contradicts itself.

The escape — let the peak rise as physics dictates — creates the confound
the constraint was built to avoid: the dispersion arm then differs from the
delay arm in peak height, a trivial intensity cue (peak concentration is
CBF-coupled), and "responds more to the dispersion edit" no longer isolates
width/skew use from peak-height use. The honest statement is that delay,
peak, and width cannot all be factorized within physiological realism,
because area conservation couples the latter two. The card must choose its
two-way contrast and say so.

**Repair options (any one suffices; the question is unchanged):**
(a) run both dispersion arms — area-preserving/peak-rising (physical) and
peak-preserving (shape-strained) — and require concordant dose-ordered
response, interpreting only the intersection; (b) add a peak-only control
arm (amplitude scaling at fixed width) so peak-height use is measured
rather than assumed away; (c) restate the estimand as "delay-independent
curve shape (width–peak bundle)" and drop the claim to have isolated width
specifically. Option (a)+(b) is strongest; option (c) is the honest floor.

### 2.2 The closest prior work is missing from the card — and this program already knew about it

This is a process failure with a substantive consequence. Scout cycle 003
produced candidate isles24-scout-003-c06, "The bolus spreads like dye in a
river" — the same core intervention (delay- and area-preserving curve
narrowing/broadening applied to a raw-CTP final-infarct model). Its novelty
audit (`ideas/scout-isles24-003/novelty_audit.md`, C6) identified
**Amador et al., ISBI 2024, "Unveiling the Temporal Patterns of a 4D CTP
Stroke Lesion Outcome Prediction Model Through Attention Analysis"
(DOI 10.1109/ISBI56570.2024.10635756)** as "the closest prior work, and
closer than anything cited on the card," downgraded C6 to LIMITED_SEARCH
solely because the paper could only be read at abstract level, and made a
full read a condition of advancement: a curve-shape perturbation in that
paper would make the candidate INCREMENTAL. Idea 042's card cites Amador
ISBI 2024 nowhere, its `dies_like_prior` field does not mention c06, and
the cycle-005 audit granted c08 HIGH_CONFIDENCE without surfacing either.

I re-checked what is publicly accessible (2026-08-19): the
[IEEE Xplore record](https://ieeexplore.ieee.org/document/10635756/) and
[abstract metadata](https://colab.ws/articles/10.1109/isbi56570.2024.10635756)
describe attention-weight analysis only — no perturbation, occlusion, or
curve manipulation — and report that the model "focuses on two specific
temporal patterns associated with observed variations in contrast
concentration dynamics," unnamed at abstract level. Source-supported
interpretation: the delta (causal, cost-matched perturbation versus
correlational attention) survives. But the delta must be *stated against
this paper*, the paper must be read in full before debate (the inherited
c06 condition — if one of the two attended "temporal patterns" is bolus
width, both motivation and priority change), and the card must acknowledge
c06 as a within-portfolio predecessor it supersedes. The same group
(Amador, Winder, Forkert) owns both the model class and the
interpretability question; they are one methods section away from this
experiment, which raises urgency and lowers novelty margin simultaneously.

### 2.3 The model to be interrogated does not exist, and the card's envelope hides that

The smallest decisive experiment reuses "the same frozen shallow raw-time
model and split discipline as c07" — that is idea 041, whose post-debate
revision (`ideas/041/revision.md`, items 11, 14) commits to a
**self-trained frozen surrogate** and records that "reusable code, a
checkpoint, a source generator, and a transport study are absent." No
public raw-CTP final-infarct checkpoint exists anywhere in this program's
records (idea-022 is PAUSED on exactly that gap). So 042's "one Colab
session, at most 10 GPU-hours" is the marginal cost conditional on idea
041 successfully training, gating, and freezing its surrogate — a
dependency the card never names. If 041 dies at feasibility or its
performance gate, 042 inherits model training, split governance, and the
performance-gate risk in full. The card lists "a qualifying raw-time
model" under `unverified_claims`, which is honest, but the costing is not.

Same section, second falsified number: the card budgets "25 GB staged
data." Idea 041's revision (item 14) records the inspected public release
as **approximately 99 GB and monolithic** — the identical 25 GB staging
assumption was explicitly removed from 041's card for that reason. 042
must inherit the correction, not the stale assumption.

### 2.4 The deliverable sentence overclaims relative to the card's own rung cap

"The final-infarct model is using delay-independent bolus dispersion **as a
collateral-route signal**" — the trailing clause is a source attribution
the design cannot establish, as the card itself concedes twice (`rung`:
"rung 2 requires validation against independently measured collateral
status, which ISLES'24 does not provide"; `standing_confounds_addressed`:
"None of this proves collateral anatomy caused X"). The program has just
litigated precisely this pattern: idea 041's debate forced the source words
out of the claim because "curve edits and encoder erasure identify a
quantity, not its source" (revision item 25), and idea 023's operator
ruling fixed claim language at the measurable construct. Dispersion in
real ISLES'24 curves can originate from collateral routes, but also from
motion-correction interpolation, 1 frame/sec temporal resampling, partial
volume, or local AIF misspecification — the edit shows the model uses
curve width; it cannot say which physical process wrote the width into the
data. Leaving "collateral-route signal" in the deliverable sentence
guarantees a debate round that ends in the same demotion; under the
claim-identity rule (decision ledger, 2026-08-10), changing that sentence
later risks REJECTED(superseded) bookkeeping. Fix it now: deliverable =
"using delay-independent bolus dispersion (post-alignment curve shape) as
a signal distinct from delay"; collateral stays in interpretation.

### 2.5 Measurement validity of the moments on this release is thinner than the card assumes

The keystone screen verified 1 frame/sec *resampling* of the CTP series.
That cuts both ways. If X is computed on the preprocessed series, every
curve has passed through temporal interpolation and co-registration —
operations that add spatially varying blur, i.e., synthetic dispersion
(inference; mechanism uncontested in the resampling literature and echoed
by 041's debate finding that preprocessing can write temporal structure
into curves). If X is computed on the raw archive, frame timing is
scanner-protocol-dependent and possibly nonuniform (several ISLES'24
scanner platforms are named in the dataset paper with no timing table —
keystone screen, Image Acquisition quote), and second/especially third
central moments are exquisitely sensitive to timestamp error and late-tail
truncation. The card's ICC gate (two AIF selections) measures reliability
against AIF choice only; it cannot detect a shared timing or interpolation
bias. Stage 0 must therefore also fix *which* series (raw versus
derivative) the moments and the model consume, verify per-frame timing
metadata exists for it, and — cheaply — report moment stability under
frame decimation. Third-moment (skew) stability at voxel level on ~30–60
noisy frames is speculation until measured; the card already marks skew
secondary, which is correct.

### 2.6 Smaller defects

- **Citation misattribution (already ordered fixed):** the Frontiers 2022
  paper is by Winder et al., not "Robben et al." — the cycle-005 audit
  verified content but ordered author correction at next revision. Robben
  et al., Med Image Anal 2020 (PMID 31683091) is a different paper and
  belongs in the neighbor list in its own right.
- **Positive control undefined.** `anticipated_negative` conditions
  decisiveness on "positive-control sensitivity," but no arm is designated.
  Presumably the delay arm (a Tmax-reading model must respond); say so, or
  the negative-result value of 3 is unearned.
- **No margin, no power statement.** Twelve cases, paired within-case
  voxel readout, monotone dose response — no effect-size floor or
  cluster-aware power sketch. Feasibility-memo material, but the card
  should not imply the readout is settled.
- **Template concentration.** This is another regional-substitution design
  (9 already, plus 10 counterfactual-synthesis) on the homogenization
  watch. Not a kill, but the portfolio is buying its tenth variation of
  one scientific move; noted for the shortlist ranking.

## 3. Novelty re-check performed for this critique

Beyond confirming the Amador ISBI 2024 abstract (attention-only;
[IEEE](https://ieeexplore.ieee.org/document/10635756/),
[metadata](https://colab.ws/articles/10.1109/isbi56570.2024.10635756)), I
searched for temporal-perturbation or occlusion analyses from the same
line of work ([TCN 2021](https://proceedings.mlr.press/v143/amador21a.html),
[spatio-temporal transformer, MedIA 2023](https://www.sciencedirect.com/science/article/abs/pii/S1361841522002389),
[clinical-context extension](https://www.sciencedirect.com/science/article/pii/S1532046423002885),
[Winder Frontiers 2022](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC9672821/)).
None describes curve-shape or dispersion-specific perturbation of a
trained model. "I did not find it" is not proof of absence; full-text
reading of Amador ISBI 2024 remains a binding pre-debate condition
inherited from the c06 audit.

## 4. Plain-pitch fidelity check (opposite-family duty)

The pitch is largely faithful: the delay/dispersion distinction, the
matched-cost comparison, and the closing hedge ("a separate dataset would
still be needed to prove that the model interprets dispersion as
collateral blood flow") all exist in the card at equal or greater
strength. Two defects, both minor but real:

1. "narrows **only** the spread of the curve" — given §2.1, "only" is not
   currently true of any realizable edit; the pitch inherits the card's
   over-constraint rather than exceeding it, and must be reworded when
   §2.1 is repaired.
2. "This study … compares" presumes a qualifying model exists; the card
   itself lists that model among `unverified_claims`. The pitch should
   carry the conditional ("in a model trained on these scans…") so it is
   not more certain than the card.

Note the asymmetry with §2.4: the pitch is actually *more* careful than
the card's deliverable sentence about collateral attribution. The card
should be brought up to the pitch's standard, not vice versa.

## 5. Required revisions (all before debate)

1. Repair the edit design per §2.1 (two-arm concordance plus peak
   control, or honest bundle restatement).
2. Add Amador et al. ISBI 2024 as closest prior work, read in full;
   add Willats 2012 and Robben 2020; correct Winder attribution;
   acknowledge isles24-scout-003-c06 in `dies_like_prior` as the
   superseded within-portfolio predecessor.
3. Rewrite the deliverable sentence without "collateral-route signal"
   (§2.4) — now, not after a debate forces it.
4. Name the idea-041 model dependency and the fallback cost if 041's
   surrogate never freezes; replace 25 GB with the inspected ~99 GB
   monolithic-archive fact.
5. Extend Stage 0 with series-provenance and timing-metadata gates and a
   frame-decimation moment-stability check (§2.5); designate the positive
   control.

---

```
NEAREST DEFENSIBLE HIGH-VALUE QUESTION: Does delay-independent bolus
dispersion, computed from the released ISLES'24 CTP curves, add voxel-level
final-infarct discrimination beyond Tmax/delay within-case — an
association-first study needing no trained model, no checkpoint, and no
curve edits?
RETAINS ORIGINAL MEDICAL MOTIVATION? PARTLY — it tests whether the
dispersion signal exists and matters in this cohort, not whether a model
uses it; use-versus-association is exactly the program's own distinction.
SHOULD IT BECOME A SEPARATE CANDIDATE? NO — fold it into 042's Stage 0 as
the decisive precondition: if dispersion carries no within-delay outcome
information in ISLES'24, the model-use question loses its motivation before
any model is trained; if it does, the result is independently reportable
(Willats 2012 predicts it should) and every measurement asset transfers.
IS IT ACTUALLY WORTH DOING? YES — it is one to two days of deterministic
computation on public data with existing ground truth, it is informative in
both directions, and it is the cheapest honest test of whether this card's
entire premise has empirical support in the actual release.
```
