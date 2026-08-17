# Critique — Idea 020: A spreading front inside the perfusion deficit

```
FATAL OBJECTION: NONE — but the decisive experiment is gated on the same
uncertified edit-validity capability that ideas 006, 008, 011 and 014 are
already stuck on, and the card runs the expensive contingent step first.
EVIDENCE: evidence/portfolio_brief.md (008/011/014 unresolved edit-validity); ideas/020/keystone_screen.md (UNVERIFIABLE)
REPAIRABLE WITHOUT CHANGING THE QUESTION? YES
DECISION: ADVANCE TO REVISION
```

---

## 1. What survives adversarial scrutiny

Stated first so the objections below are read at the right scale.

- **Data access is verified, not assumed.** The scout cycle's dataset
  verification (ideas/scout-isles24-001/scout_candidates.json,
  `dataset_verification`) confirms from primary sources: 149 public training
  cases from two centers on Zenodo (DOI 10.5281/zenodo.16731717, CC BY-NC-SA
  4.0), with registered Tmax/CBF maps, raw 4D CTP, and final-infarct masks
  (Riedel et al., DOI 10.1148/ryai.250603). No DUA dependence. The 30-case
  decisive experiment fits inside the public release. This is a real
  strength relative to most of the backlog.
- **X passes the compute-today test.** Connected-component count, Euler
  characteristic, surface-to-volume, curvature, and core-contact fraction on
  thresholded Tmax are deterministic voxel morphology. No annotator anywhere
  in the primary readout, so the program's dominant historical failure
  (annotation provenance) genuinely does not apply. The final-infarct masks
  (ISLES'22-ensemble-initialized, student-corrected) enter only secondary
  analyses; the primary paired delta is label-free, which is the structural
  move the charter asks for.
- **The keystone screen is honest.** `UNVERIFIABLE` with the residual
  assumption correctly identified (certification sensitivity is part of the
  keystone, not an implementation detail). Feasibility 2 / novelty 2 respect
  the caps. No wrong-keystone error here — the card names the load-bearing
  fact rather than the adjacent checkable one.
- **Novelty holds up under re-attack.** The prior audit
  (ideas/scout-isles24-001/novelty_audit.md, C5:
  NO_DUPLICATE_FOUND_HIGH_CONFIDENCE, twelve queries) found the nearest
  neighbors — Lucas et al. 2018 (DOI 10.3389/fneur.2018.00989), which uses
  lesion shape as a *generative modeling constraint*, and the HIR literature
  (Olivot et al., DOI 10.1161/STROKEAHA.113.003857), which compresses severe
  delay to a *volume ratio*. My independent spot-check searches
  (perfusion-lesion shape radiomics; spatial fragmentation of Tmax lesions)
  surfaced the same neighbors and nothing closer. Nobody audits whether a
  trained infarct model *uses* deficit topology at fixed volumes. Standing
  caveat from the audit: unindexed challenge-supplement analyses cannot be
  excluded; "I did not find it" is not proof.

So: no prior-work kill, no leakage kill, no data-access kill, no
annotation-provenance kill. The objections are about ordering, an
under-specified readout, a missing named asset, and a portfolio-level
pattern.

## 2. The central objection: this is the portfolio's stuck move, attempted in a harder setting

The decisive experiment is counterfactual synthesis with an in-distribution
certificate — exactly the capability on which the portfolio is currently
0-for-3 in *easier* settings:

- **Idea 008** (Sybil / parenchymal substitution): unresolved — "Are the
  local parenchymal substitutions in-distribution for Sybil?" is the single
  fact separating a use study from an association study.
- **Idea 011** (costal cartilage deletion): PAUSED because no available
  control can separate native signal use from response to the edit
  operation.
- **Idea 014** (trabecular texture edit): PAUSED with edit validity as the
  next gate even after reproduction.
- **Idea 006** (patient deletion): PAUSED after the unblock check proved the
  intervention out-of-distribution.

The design-template concentration table shows counterfactual-synthesis at
12, the second-most-used grammar. This candidate re-enters that grammar
with *tighter* joint constraints than any predecessor: it must alter the
topology of a thresholded set while simultaneously preserving the value
histogram, the threshold volumes, the smoothness spectrum, territory, and
distance-to-occlusion — on a field that is the output of a deconvolution
pipeline and is physiologically tied to a vascular tree. Three specific
aggravations:

1. **The constraints may be close to mutually exclusive.** The topology of
   superlevel sets of a smooth random field is tightly coupled to its
   spatial covariance. Fragmenting a compact Tmax>10 region at fixed
   histogram and fixed smoothness spectrum is not obviously achievable even
   before realism enters; no synthetic-field demonstration exists. The card
   treats generator existence as legwork ("1-2 weeks to validate
   counterfactuals"); the portfolio record says this class of legwork has
   consumed ideas, not weeks.
2. **The certificate is one-sided.** A held-out discriminator near chance on
   ~30 cases × 10 edits has little power, and "near chance" without a
   prespecified equivalence margin certifies nothing (the rubric's own
   standard: non-rejection is not evidence). Failing the gate kills the
   study; passing it does not establish that the *frozen model* — which has
   seen every real map and may be sensitive to vascular-territory
   plausibility a small discriminator cannot learn — treats the edit as
   in-distribution. This is idea 011's objection recurring verbatim.
3. **A positive result inherits generator fingerprints as the first
   alternative explanation**, and the card's own alternatives list concedes
   this. Mode C protects hard; it does not protect an experiment whose
   positive and negative readings are both hostage to an unbuilt,
   uncertified instrument.

This is not fatal under Mode C rules — the study is falsifiable and the
gates are named — but it is the reason the card's own feasibility score is
2, and it makes the *ordering* error in §4 decisive for what revision must
do.

## 3. Design flaw: the readout as written cannot distinguish topology use from local-value use

"Measure local output changes" (smallest decisive experiment) is
under-specified in a way that threatens the whole inference. Any edit that
changes connectivity necessarily changes voxel values somewhere. A purely
local model — one that maps each voxel's Tmax neighborhood to a fate
probability with no use of topology whatsoever — will change its output at
and around every edited voxel. Paired prediction change at edited locations
therefore confirms only that the model reads Tmax values, which nobody
doubts. The sham arm does not rescue this: a topology-altering edit (break a
bridge, detach an island) and a topology-preserving sham are *different
local perturbations*, so their differential response confounds topology
with local edit structure.

The repair exists and should be mandatory in revision: the primary endpoint
must be prediction change at voxels whose entire model-visible neighborhood
(a prespecified radius standing in for the effective receptive field) is
bit-identical between the edited and unedited maps — e.g., sever a thin
connection far from a probe island and ask whether fate predictions *inside
the untouched island* move. That is a genuine topology readout: a local
model provably cannot respond there. Without this specification the
anticipated negative is uninterpretable and the positive is unidentifiable;
with it, the experiment actually tests the deliverable sentence.

## 4. Ordering error: a cheap observational prerequisite was skipped

The question field promises topology that "distinguish[es] tissue that will
die from tissue that will recover." Nothing in the card checks whether that
information exists in the data at all — and checking is nearly free. On the
149 public cases: compute the frozen topology statistics on real Tmax maps,
and test whether they carry incremental information about final infarct
(volume, or lesion-wise overlap with the Tmax>6 region) beyond threshold
volumes, HIR, and distance covariates, with center-held-out replication
across the two centers. Days of work, no model, no generator, standard
statistics.

- If **null with adequate sensitivity**: the fate-relevant version of the
  hypothesis is dead before any generator is built. The model-use question
  survives only in its low-value form ("the model responds to an
  outcome-irrelevant shape cue"), which is not the deliverable sentence and
  would not justify the apparatus. Roughly three weeks and 50 GPU-hours are
  saved.
- If **positive**: it is a small, publishable, clinically legible finding in
  its own right, it upgrades medical relevance from 3 with evidence, and it
  motivates the counterfactual stage from data rather than analogy.

Skipping this gate is the same shape of error the charter flags as
wrong-keystone thinking: the expensive contingent step is scheduled before
the cheap load-bearing check. It also partially answers the homogenization
concern — the first stage becomes conditional-observational, and the
counterfactual grammar is only invoked once the signal is known to exist.

## 5. Missing asset: the frozen model is unnamed

"After a frozen model" carries the study, and no model is named or
verified. The scout cycle verified the dataset thoroughly; it verified no
checkpoint. The hidden test set is evaluation-server-only, and no released
ISLES'24 top-team checkpoint has been inspected (sibling candidate c01
gestures at "the winning model" with the same gap). Revision must either
(a) verify a released challenge checkpoint or Docker that can be run
locally, with the specific artifact inspected, or (b) declare the target to
be a locally trained nnU-Net-class baseline on the 149 public cases and add
its training cost (order of tens of GPU-hours, feasible but currently
uncounted) to the budget — accepting that the claim then scopes to "a
representative ISLES'24-trained model," not "the winning model." Either is
acceptable; silence is not, because DATA_ACCESS is a known kill mode (x2)
and this is its checkpoint variant.

## 6. Smaller findings

- **Circularity check: passes.** X is computed from the model's *input*
  field; for a model-use claim this is the correct side. It would be
  circular only if X were derived from the model's output or the label.
- **Label quality: contained.** The student-corrected, ensemble-initialized
  masks are a real limitation of ISLES'24, but the primary paired readout
  never touches them; only the Stage-0 screen and secondary analyses do,
  and those tolerate label noise as outcome-measurement error.
- **Deconvolution-artifact alternative is honestly scoped but caps the
  rung.** "Map topology is software topology" cannot be excluded without
  the raw-CTP replication arm; until then even a fully gated positive is
  rung 1 about the *map*, not the physiology. The card says this; revision
  should keep it un-walked-back.
- **Cross-domain drop test: marginal but honest.** The card admits that
  dropping the reaction-front analogy leaves "a generic shape-use audit."
  The measurements are concrete either way, so this is tolerable under the
  fluent-nonsense guard, but the revision should not let the combustion
  language do any argumentative work the morphology does not.
- **Discriminator gate needs an equivalence margin** and the
  positive-control volume edit needs a prespecified minimum detectable
  effect, or the anticipated negative silently degrades from
  sensitivity-limited to uninterpretable — which would also trip the
  negative-result-value cap.
- **License:** CC BY-NC-SA 4.0 is compatible with this research use;
  noncommercial scope only. No action needed.

## 7. Required revisions (summary)

1. Prepend the Stage-0 observational topology screen (§4) as a mandatory
   gate with a prespecified sensitivity statement; kill or park on a
   sufficiently tight null.
2. Rewrite the primary endpoint as the nonlocal readout (§3):
   prediction change in regions whose model-visible neighborhood is
   identical across the edit.
3. Name and verify the frozen model (§5), with compute accounted.
4. Before the 30-case study, demonstrate on synthetic smooth fields that
   the histogram/spectrum/topology joint constraint set is satisfiable at
   all (§2.1); this is the cheapest possible test of the keystone.
5. Add the equivalence margin and positive-control MDE (§6).

None of these change the deliverable sentence — "the final-infarct model is
using the shape of the severe-delay front, not only perfusion volumes" —
so revision-in-place is permitted under the claim-identity rule.

---

```
NEAREST DEFENSIBLE HIGH-VALUE QUESTION: At exactly matched Tmax>6s and
Tmax>10s volumes, does the fragmentation and core-contact of the
severe-delay region carry incremental information about the final infarct
in ISLES'24's own labels, replicated across its two centers?
RETAINS ORIGINAL MEDICAL MOTIVATION? YES
SHOULD IT BECOME A SEPARATE CANDIDATE? NO — it is Stage 0 of this idea; the
deliverable sentence is unchanged and splitting it would orphan the
model-use question that gives it its point.
IS IT ACTUALLY WORTH DOING? YES — data, labels, metrics and morphology
tools are all released today, it is days of work, and either outcome is
decisive for whether the expensive counterfactual stage should exist.
```
