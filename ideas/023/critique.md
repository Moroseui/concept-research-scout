# Critique — Idea 023 (isles24-scout-002-c07): Little's law in the penumbra

```
FATAL OBJECTION: NONE
EVIDENCE: ISLES'24 report arXiv:2408.10966 (maps from icobrain cva tracer-kinetics
deconvolution); Zenodo 16731717/16813698; winning-solution paper arXiv:2505.18424
REPAIRABLE WITHOUT CHANGING THE QUESTION? YES
DECISION: ADVANCE TO REVISION
```

No single objection kills this card. But three repairs are mandatory before a
feasibility memo, and one of them (the CBV/MTT degeneracy, §2) quietly narrows
what the deliverable sentence is allowed to mean. The card is unusually honest
about its residual assumptions; the problems below are the ones it did not list.

---

## 1. What I verified (sources checked this stage)

- **Map provenance.** The ISLES'24 report states CTP preprocessing used the
  FDA-cleared clinical software **icobrain cva**: motion correction, temporal
  resampling to 1 frame/s, then perfusion maps "generated using a conventional
  tracer-kinetics deconvolution algorithm" (arXiv:2408.10966). This is the fact
  that drives §2 below. The card never asks how the maps were made; it should.
- **Dataset schema.** Confirmed independently of the keystone screen: the Zenodo
  release contains 149 training cases with per-case Tmax/CBF/CBV/MTT derivatives
  co-registered to NCCT space, CC BY-NC-SA 4.0. **Version churn exists**: the
  record the keystone screen inspected (16731717) is one of several versions;
  16813698 is "v3" (2025-08-12) and itself points to a newer version. Schema is
  stable across the two versions inspected, so the keystone stands, but the
  record/version and file hashes must be pinned at Stage 0.
- **Winning solution.** arXiv:2505.18424: a residual-encoder nnU-Net with
  SynthStrip skull-stripping and custom intensity windowing. The paper does not
  state its exact input-channel configuration and releases no code or checkpoint
  I could find. The card's "self-trained nnU-Net stands in" assumption is
  therefore load-bearing (§4).
- **Prior work / novelty.** The counterfactual literature in this niche perturbs
  *clinical/treatment* variables (Robben et al. 2020, PMID 31683091; Amador et
  al., ScienceDirect S1532046423002885) or ablates whole input channels. I found
  no work that toggles the physiological state jointly encoded by the perfusion
  maps while preserving inter-map consistency. The novelty delta survives this
  critique. Amador's clinical-counterfactual line should be added to
  `novelty_neighbors` as the nearest methodological relative.

## 2. Principal objection: at fixed CBF, CBV and MTT are one channel, not two

A conventional tracer-kinetics deconvolution pipeline derives MTT from the
central volume theorem — MTT := CBV/CBF is typically an algebraic step of the
software, not an independent measurement. icobrain cva's internals are
proprietary, so Stage 0's identity-residual census is the right check, but the
card must face the dilemma it creates, because **both horns cost something**:

- **If the residual is ~0 (identity holds by construction):** the "Little's-law
  identity" is a tautology of the vendor pipeline, not a physiological manifold.
  Two consequences. (a) The "does the model check inter-map consistency" probe
  loses its physiological framing — it is a pure never-seen-input OOD probe
  (idea-006 shape; the card correctly quarantines it, but the "does the model
  know Little's law" interest hook deflates to nothing). (b) More important: the
  confirmatory co-edit moves CBV and MTT **in lockstep at fixed CBF — they carry
  identical information**. A positive result cannot attribute the response to
  "blood volume held up" versus "transit time prolonged." The deliverable
  sentence names the *blood-volume* reserve; the experiment can only ever
  establish use of the *compensation state* (the joint CBV/MTT configuration at
  matched flow deficit). These coincide physiologically but not as
  channel-attribution claims, and a reviewer will read the current sentence as
  the latter.
- **If the residual is large:** the maps do not live on the claimed manifold,
  the co-scaling rule is wrong, and the card's own fallback (edit along the
  empirical joint distribution) applies — which is fine, but then the entire
  Little's-law apparatus contributed nothing (see §6).

**Repair (within the same question):** keep the sentence's own definition —
"capillary volume held at or above mirror-normal while flow falls" is a *state*
description and can stand — but add an explicit prohibited-conclusion: no claim
that the model reads the CBV channel as opposed to the MTT channel; at matched
CBF they are not separable in principle when the identity holds. This is wording
honesty, not a new deliverable, so the claim-identity rule is not triggered.

## 3. The two-sided discriminator is under-designed for its main job

Alternative explanation 1 (the card's own) is the crux: reserve-construct reader
vs. generic monotone-CBV-severity reader. Work the signs through:

- Toggle compensated→collapsed (CBV↓, MTT↓, CBF and Tmax fixed): the construct
  reader predicts infarct probability **rises**. A monotone "low CBV = bad"
  channel reader predicts it **rises too**. Same sign. The toggles as listed in
  `smallest_decisive_experiment` (compensated↔collapsed at three magnitudes)
  therefore do **not** separate the two hypotheses — they separate both from
  "ignores CBV/MTT entirely."
- The separation the card gestures at ("including above-mirror values") requires
  an **explicit above-mirror arm**: push CBV *above* mirror-level at matched
  CBF. The construct reader predicts saturation (already compensated; no further
  benefit), the monotone reader predicts a continued response. That arm is
  mentioned in the alternatives list but absent from the experiment description,
  and it is the only part of the design that earns the word "construct" in the
  deliverable. It is also the arm with the weakest physiological cover story
  (post-ischemic hyperperfusion does occur in infarcted tissue) and the greatest
  OOD risk, so it needs its own empirical-support gate in Stage 0.
- One incidental gain: a monotone-MTT-severity reader ("long MTT = bad")
  predicts the *opposite* sign under the joint toggle, so the basic arm does
  falsify that particular generic reader. Worth stating — it is the one clean
  discrimination the basic toggles do achieve.

**Repair:** promote the above-mirror saturation arm into the confirmatory
design with a prespecified dose-response shape readout (response flattens above
rCBV_mirror = 1 vs. continues), or demote the claim from "uses the reserve
construct" to "uses the compensation state," which is still a finding but a
smaller one. Identifiability at 4 is not defensible until one of these happens;
as written it is a 3.

## 4. The missing Stage 0 gate: does the *label* even carry the interaction?

The card's premise is that "every training case showed the model the
consequence" of the compensated/collapsed difference. That is an assumption
about the ground truth, and it is checkable on CPU before any model exists: at
matched CBF decrement, do final-infarct membership rates actually differ
between compensated and collapsed voxels in the 149 released cases? This is
simultaneously (a) a re-litigation of Wintermark-vs-Campbell on a modern,
reperfusion-treated cohort — a citable side result on its own — and (b) the
precondition for the whole study: **if the labels do not encode the state's
prognostic value at matched CBF, the toggle null is preordained and
uninterpretable as a model finding.** Two aggravating factors make this gate
non-optional: the cohort is all-treated with heterogeneous reperfusion success
(penumbra fate is partly stochastic from the image alone), and n=149. Add it to
Stage 0 alongside the identity-residual and joint-support censuses. The
`anticipated_negative` classification ("decisive") is conditional on this gate
passing and should say so.

## 5. Scope honesty: whose model is being audited?

The deliverable and the anticipated negative speak of "the final-infarct model"
and "what benchmark models internalized." What will actually be probed is a
self-trained nnU-Net, because no challenge checkpoint is confirmed released
(§1). Three consequences:

1. The quotable-negative claim ("siding with the rCBF camp") must be scoped to
   *this model family under this training recipe*, not "benchmark models."
2. The shared-model input specification is silently load-bearing: the edits
   enter through the perfusion-map channels, so the cycle-shared model **must**
   take the four maps as inputs. A raw-4D-CTP model (Amador-style) or an
   NCCT/CTA-dominant model gives the probe no port of entry. This is
   controllable (we train it) but must be prespecified, and it couples c07 to
   every other candidate sharing that checkpoint.
3. With a multimodal input (NCCT+CTA+maps), a weak toggle response is ambiguous
   between "ignores the state" and "NCCT evidence dominates" — established
   hypodensity on NCCT will rationally cap how far a CBV edit can move the
   prediction. Cheap fix, worth adopting: train the maps-only configuration as
   well and run the probe on both; divergence between them is itself
   informative. The Tmax positive control calibrates channel sensitivity but
   not cross-channel dominance.

Stage 0 should also inventory released ISLES'24 participant repositories
(e.g., the official docker template, kimberly-amador/ISLES24-PrediCTP,
Mahsa0M/isles2024_docker) for released *weights*; if any trained submission is
public, probing it alongside the self-trained model materially strengthens the
"benchmark" framing at near-zero cost.

## 6. Analogy audit (charter test: what changes if dropped?)

The card's own answer is half-right. The two-sided deviation-from-mirror
prediction is genuinely load-bearing — but it comes from classical stroke
physiology (Wintermark's autoregulation account), not from control engineering.
Little's law adds nothing beyond the central volume principle, which the CTP
literature has cited under that name since the 1990s; and if §2's first horn
holds, the "manifold constraint" it supplies is the vendor pipeline's algebra.
The experiment would be identical with the queueing/control vocabulary deleted
and "autoregulatory compensation (Wintermark 2006) vs. flow-only (Campbell
2011)" put in its place. This is decoration on top of a real mechanism, not
fluent nonsense — the named quantity and measurement survive the deletion — so
the charter's remedy is rewrite-without-analogy, not discard. The revision
should do that; it will also make the card more legible to the stroke-imaging
reviewer the deliverable sentence is aimed at.

## 7. Kill-attempts that failed (recorded so they are not re-run)

- **Prior-work overlap:** searched; nearest neighbors are channel ablations and
  clinical-variable counterfactuals; no consistency-preserving state toggle
  found (§1). Novelty delta stands.
- **Circularity (idea-010 shape):** X is computed from the model's inputs, but
  the endpoint is output change under input intervention, not a re-encoding of
  the input. Not circular.
- **Label leakage:** ground truth from follow-up MRI; inputs are acute-phase
  only. No path.
- **Annotation provenance:** primary readout is label-free paired deltas; the
  GT enters only through the §4 gate and training, both with documented
  provenance (DOI 10.1148/ryai.250603). The dominant program failure mode does
  not apply.
- **Confounding (scanner/protocol/site):** within-case paired edits hold all of
  it fixed; the mirror ratio kills global scaling. The card's treatment is
  correct.
- **Excessive compute:** ~320 forward passes is trivial; the real costs are the
  one-time ~100 GB archive download (the 99 GB train.7z is monolithic — check
  at Stage 0 whether derivatives can be fetched separately) and the shared
  nnU-Net training, which is a cycle-level cost amortized across the ISLES
  candidates but should stop being invisible in this card's "cheapest wide
  candidate" claim.
- **Unavailable data:** public, CC BY-NC-SA 4.0, no DUA. Fine for this program.
- **idea-016 and idea-006 resemblance:** the card's `dies_like_prior` answers
  are adequate; the mirror ratio and empirical-range bounds are real structural
  differences, and the OOD-flavored identity-violating probe is quarantined.

## 8. Easier versions (low-hanging fruit, in ascending cost)

1. **Model-free, CPU-only (§4 gate as a result):** the GT-interaction census on
   149 cases. Data and labels already exist; no training. If it fails, the
   candidate dies for ~zero cost; if it passes, it is a citable observation
   about the Wintermark/Campbell debate in a treated cohort either way.
2. **Observational stratification (no edits):** once the shared model exists,
   compare its predicted-infarct probability for compensated vs. collapsed
   voxels at matched CBF. Confounded (state correlates with everything), so it
   cannot replace the toggles, but it costs one inference pass over held-out
   cases and yields the effect-size estimate the toggle arm needs for power.
3. **Released-submission probe:** if the Stage 0 checkpoint inventory (§5)
   finds any public trained ISLES'24 submission, run arms 1–2 on it before
   training anything.

These are stages of the same candidate, not separate candidates.

---

```
NEAREST DEFENSIBLE HIGH-VALUE QUESTION: Does a map-input final-infarct model
trained on ISLES'24 respond to the autoregulatory compensation state — the
joint CBV/MTT configuration at matched CBF decrement, with an explicit
above-mirror saturation arm — and does the cohort's ground truth even encode
that state's prognostic value at matched flow?
RETAINS ORIGINAL MEDICAL MOTIVATION? YES
SHOULD IT BECOME A SEPARATE CANDIDATE? NO — same deliverable sentence, narrowed
attribution; revision-in-place under the claim-identity rule.
IS IT ACTUALLY WORTH DOING? YES — the §8.1 census alone is worth running this
week on existing public data, and it decides for free whether the rest deserves
GPU time; the full study is worth doing only conditional on that gate.
```
