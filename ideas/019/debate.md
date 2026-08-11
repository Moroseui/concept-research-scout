# Debate transcript

## Round 1 — CRITIC

**Position:** The experiment currently decodes a nonexistent pulmonary-fibrosis output, and the available pulmonary-fibrotic-sequela head is not an interpretable surrogate unless CT-RATE contains enough honeycombing-bearing positives to give that head training pressure to use honeycomb topology.

**Argument:** CT-CLIP's CT-RATE vocabulary reportedly contains "pulmonary fibrotic sequela," not "pulmonary fibrosis." That distinction breaks the card's present endpoint and medical interpretation: a report-derived sequela label in a general hospital cohort can be driven by linear post-infectious or post-inflammatory scars, apical scarring, or other residual change without any connected multilayer subpleural cyst network. Even a technically clean topology perturbation would therefore be underidentified if honeycombing is rare: a null could mean the head was never trained on enough honeycombing, while a positive could reflect correlation with overall scar burden rather than the defining topology. The required identity check does not itself kill a repair—renaming the endpoint and conditionally asking whether that exact head uses honeycombing still tests the original deliverable sentence—but substituting a generic reconstruction-sensitivity claim would not. Before image-level work, the official label CSV/checkpoint schema must establish the exact output, and a frozen report-text audit must estimate honeycomb-mention prevalence and its overlap with fibrotic-sequela positives; report text may gate feasibility but cannot become the confirmatory X because it is reader-derived.

**What would change my mind:** Direct inspection of the released label CSV and checkpoint output mapping showing the pulmonary-fibrotic-sequela head, plus a prespecified report audit showing enough honeycomb-mentioning fibrotic-sequela-positive volumes in the obtainable validation/test partitions to meet a stated precision or power target for the planned within-pair analysis.

**Status:** OPEN

## Round 1 — PROPOSER

**Responding to:** The card decodes an output that does not exist. The real
head is "pulmonary fibrotic sequela" — report language for residual scarring
of any cause, mostly non-UIP in a general Turkish hospital cohort — and unless
CT-RATE demonstrably contains enough honeycombing-bearing sequela-positives,
the experiment is underidentified in both directions: a null could mean the
head never had training pressure to encode honeycomb topology, and a positive
could mean correlation with overall scar burden rather than the defining
topology. The endpoint identity and the prevalence audit must both be settled
before any image-level work.

**Response:** AMEND

**Argument:** The factual core of the objection is correct, and I have now
verified it by direct inspection rather than leaving it at the critic's
"reportedly." I cloned the official CT-CLIP repository at commit
`a2a155c601987820433c01db69b64d701d3d229d` — the same commit the keystone
screen inspected — and searched the released code:

- `scripts/CTCLIPTrainer.py:285` and `scripts/ct_lipro_inference.py:76` both
  hard-code the 18-item pathology list; it contains `'Pulmonary fibrotic
  sequela'` and no "pulmonary fibrosis" entry.
- `scripts/bootstrap_values.py:55-73` gives the explicit output-index mapping:
  `11: 'Pulmonary fibrotic sequela'`. This is the checkpoint output mapping
  the critic asked for, at the code level. The gated label CSV header remains
  to be confirmed after dataset access, but the released training and
  inference code is the authoritative statement of what the ClassFine head
  emits, and it settles the vocabulary question: the card's endpoint name was
  wrong. (Verified fact, this session.)

The amendment, in four parts:

1. **Endpoint rename, everywhere.** The decoded output is the
   pulmonary-fibrotic-sequela score (ClassFine index 11). The question
   becomes: *does CT-CLIP's pulmonary-fibrotic-sequela score use connected
   multilayer subpleural cyst topology, rather than generic peripheral
   high-frequency texture, on the subset of cases where that topology exists?*
   Identity check: the deliverable sentence named CT-CLIP and honeycombing,
   not the phrase "fibrosis score," so the amended design still answers the
   original one-sentence question about the same model, the same X, and the
   same prohibited conclusions. This is narrowing and instrument repair under
   the 2026-08-10 claim-identity rule, not a new study.

2. **What is lost — stated plainly.** The UIP/prognosis framing shrinks to
   what a scarring-sequela head can support: `medical_relevance` drops 5 → 3.
   A positive result no longer says "an ILD model reads honeycombing"; it says
   "a general-scarring head, when scored on honeycomb-bearing cases, uses the
   cyst network rather than scar burden alone." That is a weaker medical
   claim. It is still the physician-legible mechanism the idea was built on,
   and the conditional form is honest about the head's training distribution.

3. **Stage 0a becomes numbered kill condition K1, before any image
   download.** On the obtainable CT-RATE report text and RadBERT labels
   (released without image gating): (a) regex the validation/test partitions
   for honeycomb terms; (b) cross-tabulate mentions against
   fibrotic-sequela-positive labels. Prespecified floor: at least 30
   honeycomb-mentioning, sequela-positive volumes in the obtainable evaluation
   partitions, of which at least 15 fall in the thin-slice stratum the
   topology instrument requires. The floor of ~30 is chosen so a medium
   association (r ≥ 0.5) is detectable at 80% power, α = 0.05; the exact
   arithmetic for the within-pair arm goes in the revised card. Below the
   floor, the idea dies as DATA_INSUFFICIENT without a single volume
   downloaded. Report text gates and stratifies; it never becomes the
   confirmatory X — full agreement with the critic on that boundary.

4. **The positive-direction confound is absorbed, not dodged.** The critic's
   second horn — a positive could be scar-burden correlation — is the
   collinearity problem the critique round already flagged against linear
   erasure. The amended card adopts the corresponding repairs: prespecified
   encoding gates and a maximum admissible collinearity between the frozen
   topology and scar-burden/reticulation directions, with the anticipated
   negative reclassified as sensitivity-limited (`negative_result_value`
   5 → 3) unless those gates pass. A null on a head that Stage 0a has shown
   *does* have honeycomb-positive support, with encoding gates passed, is the
   only null the amended card counts as decisive.

Amendment count check: this is the first amendment, and it responds to a
verified factual error in the card, not to a feasibility squeeze. The
motivating question survives it intact; what does not survive is the inflated
medical framing, and that deflation is the repair working as intended.

**Status:** CONVERGED — the endpoint mapping is now directly inspected
(`bootstrap_values.py:67`, commit `a2a155c`), and the remaining half of the
critic's condition, the prevalence audit, is no longer a point of argument:
it is kill condition K1, prespecified with a floor and executed on free
report text before any image work. If K1 fails, the critic was right in the
strong sense and the idea dies cheaply.

## Round 2 — CRITIC

**Position:** The endpoint correction preserves the original question, but the proposed linear-direction erasure still cannot identify use of honeycomb topology because projection-induced score changes are inseparable from off-manifold embedding damage and removal of correlated scar severity.

**Argument:** I concede the Round 1 endpoint objection: direct inspection of the official CT-CLIP code establishes ClassFine index 11 as `Pulmonary fibrotic sequela`, and the conditional rename still asks the original question about whether CT-CLIP uses connected multilayer subpleural cyst topology. Making honeycomb prevalence a preregistered kill gate is also an adequate response to the support problem. The remaining causal instrument, however, is not repaired by promising an encoding gate and a maximum correlation between learned directions. A low pairwise correlation between linear topology and reticulation/scar-burden directions does not establish that subtracting one direction changes only topology information; nonlinear and distributed severity information can share the removed subspace, and the frozen ClassFine head has never been validated on projected embeddings. Thus a selective score decrease after projection can arise because the intervention moves honeycomb-bearing cases farther off the native embedding manifold, not because the head used X. Matched random or nuisance projections do not solve this unless they are matched for manifold displacement and local head sensitivity case by case. This is the latent-space version of idea 006's OOD-intervention failure, which the current `dies_like_prior` field incorrectly claims to avoid merely because erasure occurs internally. The geometry-matched kernel-pair arm is not a substitute for the claim either: it identifies sensitivity to reconstruction-rendered wall topology, while kernel changes also alter noise and generic high-frequency texture, so by itself it does not establish native honeycombing use. The idea remains scientifically plausible, but its primary rung-1 evidence is association plus an uninterpretable intervention.

**What would change my mind:** Show, before test-set use, a validated latent intervention whose projected embeddings remain within a prespecified native-neighborhood or density-equivalence margin and whose score effect is unchanged under case-matched sham projections equated for manifold displacement and local ClassFine-head sensitivity; alternatively, provide an image-space topology-specific edit that passes prespecified in-distribution and sham-effect gates while holding scar extent, density, emphysema, and reconstruction statistics fixed. Without one of those, demote the study to exploratory association and do not claim rung 1.

**Status:** OPEN

## Round 2 — PROPOSER

**Responding to:** The linear-direction erasure cannot support a rung-1 use
claim as designed. A score drop after projection has two explanations the
current controls cannot separate: the intervention pushed honeycomb-bearing
cases off the native embedding manifold that the frozen ClassFine head was
trained on — the latent-space version of idea 006's OOD failure, which the
card's `dies_like_prior` field wrongly claims to have avoided — and the
removed subspace carries nonlinear, distributed scar-severity information that
a low pairwise correlation between learned directions does not exclude. Sham
projections only help if matched, case by case, for manifold displacement and
local head sensitivity. The kernel-pair arm is complementary, not a
substitute: it identifies sensitivity to reconstruction-rendered wall
topology, not native honeycombing use. Either validate the intervention
against these gates before test use, or demote to exploratory association and
do not claim rung 1.

**Response:** AMEND

**Argument:** The core of the objection is conceded, and the amendment adopts
the critic's own disjunction as the design rather than approximating it.

**Conceded outright.** First, an ungated projection is an unvalidated
intervention: off-manifold is a property of the training distribution of the
head, not of the space the intervention happens to live in, so "erasure occurs
internally" earns nothing by itself. The `dies_like_prior` field is wrong as
written and will be rewritten in revision: the card does *not* structurally
avoid idea 006's failure mode; it must buy its way out with validation gates,
case by case, or it inherits that failure. Second, I do not contest the
characterization of the kernel-pair arm. It stays in the design as a
complementary associational arm (with the paired score change regressed on the
paired topology-measure change controlling for measured noise and spectral
band-power changes, which sharpens but does not transform it), and it is never
offered as the rung-1 instrument.

**The amendment — the critic's condition becomes the gate structure.**

1. **Instrument choice.** Naive orthogonal projection is replaced by
   minimal-displacement affine concept erasure in the LEACE family
   (arXiv:2306.03819 — method citation from memory, to be verified in
   revision), selected precisely because it minimizes the embedding
   displacement that gate G2a polices. If no released implementation is
   usable, the naive projection may still be evaluated — but only through the
   same gates, which it is then likely to fail, and that failure is the
   finding.

2. **Gate G2a — manifold validity, prespecified.** On validation embeddings
   only: projected embeddings must remain within a prespecified
   native-neighborhood margin — kNN distance to the native validation
   embedding cloud within a fixed quantile of native-to-native distances, plus
   a density-equivalence margin, both frozen before any test-set scoring.
   Failure means no erasure-based claim of any kind is made.

3. **Gate G2b — case-matched shams, prespecified.** For each case, sham
   directions are constructed to match, case by case, (i) the embedding
   displacement norm produced by the topology erasure and (ii) the local
   ClassFine-head sensitivity along the removed direction, measured as the
   magnitude of the head's directional derivative — computable exactly because
   the head is frozen and differentiable. Rung-1 evidence requires the
   topology-erasure score effect to exceed the sham-effect distribution at a
   prespecified quantile, with the nuisance battery (reticulation, density,
   emphysema directions erased separately) retained on top. This is the
   displacement-and-sensitivity-equated sham the critic specified, adopted
   verbatim, not a matched-random approximation.

4. **Automatic demotion, prespecified.** If either gate fails on validation,
   the confirmatory erasure arm is cancelled before the test set is touched.
   The study then reports the topology-score association and the kernel-pair
   arm, both labeled exploratory, claims rung 0, and its headline deliverable
   becomes the feasibility finding "linear erasure cannot be validated as an
   in-distribution intervention for this head" — which the charter counts as
   success (a feasibility result that prevents wasted effort) and which the
   ledger records so no later candidate spends the same instrument on CT-CLIP
   unvalidated. The critic's "demote and do not claim rung 1" branch is thus
   not a concession I might be forced into later; it is the prespecified else-
   branch of the design.

5. **The image-space alternative is noted, not adopted.** A topology-specific
   wall-breaking edit with in-distribution and sham-effect gates is the
   critic's other escape. It is not taken as primary here: validating
   synthetic subvoxel wall edits on 1.5 mm resampled tensors is a strictly
   heavier lift than the latent gates, and the portfolio already carries an
   edit-validity debate of exactly this shape (idea 008). If the latent gates
   fail, that edit is the natural successor and should enter as a spin-off
   candidate under the claim-identity rule, not as amendment three of this
   card.

**What is lost.** Rung 1 is now conditional, not promised: the card's rung
target within obtainable data becomes "rung 1 if gates G2a and G2b pass,
otherwise exploratory association only." Identifiability drops 4 → 3 and the
anticipated negative remains sensitivity-limited unless all gates pass, as
already set in amendment one. A residual limitation goes into the card
verbatim: even a fully gated positive identifies use of the information
carried along the validated linear topology direction — nonlinear encodings
sharing that subspace are not excluded — so the deliverable sentence acquires
the qualifier "as linearly encoded in the model's representation," and the
nuisance battery is what earns "rather than scar burden alone."

**Identity check.** The revised design still answers the original one-sentence
question — does CT-CLIP's (fibrotic-sequela) score use connected multilayer
subpleural cyst topology — about the same model, the same X, and the same
prohibited conclusions. What changed is the burden of proof imposed on the
instrument before the claim may be made, and the prespecified fallback when
that burden is not met.

**Amendment count.** This is amendment two. Per the rules, a third structural
amendment should be read as evidence the original design was wrong; I flag
that now so the next round can hold me to it.

**Status:** CONVERGED — the proposer adopts the critic's disjunction as the
design itself: rung 1 is claimable only through the exact validated-
intervention gates the critic specified (manifold margin plus case-matched
displacement-and-sensitivity-equated shams, established on validation before
any test use), and on gate failure the study self-demotes to exploratory
association with no rung-1 claim. The nonlinear-residual limitation is not
contested; it is recorded as a scope qualifier on the deliverable sentence.

## Round 3 — CRITIC

**Position:** The revised gates may validate an intervention on a topology-derived latent direction, but they still cannot establish that the independently computed X is honeycombing rather than a mixture of paraseptal emphysema, traction bronchiolectasis, and reconstruction-created wall closure.

**Argument:** The Round 2 amendment adequately answers the off-manifold objection conditionally: G2a and G2b make failure of intervention validation an explicit rung-0 outcome, and the amended positive still addresses the original question rather than substituting the kernel-pair question. The strongest remaining defect is upstream of LEACE. The card's deterministic recipe—3–10 mm air components, complete walls, adjacency, stacking, pleural distance, and Betti/Euler summaries—has no inspected reference establishing semantic specificity on CT-RATE's native images or final tensors. Requiring no airway connection does not exclude traction bronchiolectasis when distal airway segmentation fails in fibrotic lung, and complete-wall or multilayer criteria do not exclude juxtaposed paraseptal emphysema when trilinear resampling creates or closes thin walls. Native-to-tensor repeatability only shows that the same measurement survives preprocessing; it cannot show that the measurement denotes honeycombing. Likewise, report-text honeycomb mentions are suitable for prevalence gating but, under the charter, cannot validate the primary X because they are reader-derived and their annotation conditions are not an independent measurement method. Therefore even if the latent intervention passes G2a/G2b, the identified claim is only that CT-CLIP uses information aligned with the bespoke subpleural-airspace topology index. Calling that index “honeycombing” makes an unsupported rung-3 semantic leap. This does not die exactly like the prior annotation-provenance candidates—the primary analysis does not require their labels—but it inherits their lesson if report mentions are quietly used to confer construct validity. A third structural amendment is unnecessary: the study can remain sound at rung 1 with the X named literally as the computed topology index; the physician-level honeycombing sentence must remain out of scope until independent construct validation exists. The identity check therefore creates a real boundary: renaming X to a topology index narrows the original honeycombing claim, while retaining “honeycombing” without validation overclaims it.

**What would change my mind:** Directly inspect and run an obtainable, citable honeycombing quantifier with released weights that has external validation against the named mimics, then show prespecified agreement and failure-analysis results with the proposed topology measure on CT-RATE native and final tensors; alternatively, establish construct validity in an independent dataset with an existing adjudicated honeycombing reference and demonstrate transport of the frozen measurement thresholds to CT-RATE. Repeatability, report-term enrichment, or association with the fibrotic-sequela score alone would not suffice.

**Status:** OPEN

## Round 3 — PROPOSER

**Responding to:** Even with G2a/G2b passed, the study identifies use of
information aligned with the bespoke subpleural-airspace topology index — not
use of honeycombing. The index has no inspected reference establishing that it
separates honeycombing from paraseptal emphysema, traction bronchiolectasis,
and reconstruction-created wall closure on CT-RATE's native images or final
tensors; airway-exclusion fails exactly where distal airway segmentation fails,
and resampling can create or close the walls the criteria depend on.
Native-to-tensor repeatability shows survival, not denotation; report-text
mentions may gate prevalence but can never confer construct validity, because
they are reader-derived. Naming the index "honeycombing" is therefore an
unearned rung-3 semantic leap. No third structural amendment is needed: the
study is sound at rung 1 with X named literally, and the physician-level
honeycombing sentence stays out of scope until independent construct
validation exists.

**Response:** CONCEDE

**Argument:** The objection is correct, and I adopt the critic's own remedy —
which, as the critic says, is scope discipline rather than a structural
amendment. Every element of the design survives unchanged (K1 prevalence gate,
LEACE-family erasure, gates G2a/G2b, the nuisance battery, the automatic
demotion branch, the exploratory kernel-pair arm). What does not survive is
the name attached to a gated positive, and I concede each step of the
argument that removes it:

- **Repeatability is not denotation.** The Stage 0 native-to-tensor audit was
  the card's answer to the preservation keystone, and it answers only
  preservation: the same number computed twice. Nothing in the design ever
  checks what the number *means* against an independent reference, and I have
  no such reference to offer inside CT-RATE. The keystone screen's
  `UNVERIFIABLE` verdict already contained this — mimic separability was named
  as the unverifiable half — and the critic is right that no amount of latent
  gating downstream repairs a reference problem upstream.
- **The failure modes are concrete, not hypothetical.** Distal airway
  segmentation failing precisely in fibrotic lung (so "no airway connection"
  silently admits traction bronchiolectasis) and trilinear resampling to
  1.5 mm creating or closing ~1 mm walls (so "complete walls" tracks
  reconstruction as much as anatomy) are the two specific mechanisms by which
  the index becomes a mixture. Both were flagged in critique; neither has an
  in-design answer. At rung 1 that mixture is tolerable only because the claim
  is literally about the index, contamination included — which is exactly why
  the honeycombing name must come off the confirmatory claim.
- **Report mentions never validate X.** Full agreement, restated as a hard
  boundary: honeycomb-mention regexes gate prevalence (K1) and stratify, and
  appear nowhere in any construct-validity argument. This is the
  annotation-provenance lesson applied prospectively rather than learned
  retrospectively — the five prior kills happened because reader-derived
  language was load-bearing; here it is confined to feasibility gating.

**What this changes in the card (scope accounting, for the revision):**

1. **The confirmatory claim is restated at index level.** A fully gated
   positive supports: "CT-CLIP's pulmonary-fibrotic-sequela score uses
   information carried by the prespecified subpleural cyst-network topology
   index, as linearly encoded in its representation, beyond scar-burden,
   density, and emphysema nuisance directions." X is the index, named
   literally. It remains charter-compliant as an X — a deterministic, citable
   formula computable today on an unseen scan without asking anyone — but it
   is not yet a word a physician already has.
2. **Rung accounting.** `rung.target` within obtainable data drops 3 → 1.
   The honeycombing deliverable sentence is retained as the rung-3 *target*,
   explicitly out of scope for this study, per the charter's provision that a
   candidate may stop below rung 3 if it says so and names the move-up.
   `rung.move_up` is rewritten to the critic's disjunction verbatim: (a) an
   obtainable, citable honeycombing quantifier with released weights and
   external validation against the named mimics, run on CT-RATE native and
   final tensors with prespecified agreement and failure analysis against the
   index; or (b) construct validation in an independent dataset with an
   adjudicated honeycombing reference, plus transport of the frozen
   measurement thresholds to CT-RATE. Revision adds a bounded Stage 0c
   search for candidate (a) — the critique already named the AJRCCM 2024
   deep-learning honeycombing quantifier (DOI 10.1164/rccm.202311-2185OC) as
   a lead with released-weights status unverified; absence of a finding is
   recorded as absence, not as impossibility.
3. **Identity check, answered honestly.** The critic is right that this is a
   real boundary, and here is where I place the card relative to it: the
   original one-sentence question — does CT-CLIP use connected multilayer
   subpleural cyst topology — is still what the study asks, via the same
   measurement the card always specified; the deliverable sentence and
   prohibited conclusions are unchanged as targets. What changed is which
   rung the obtainable evidence can certify: the study now certifies "the
   model uses the topology index" (rung 1) and explicitly declines to certify
   "the index is honeycombing" (rung 3) until the named validation exists.
   That is rung honesty within the same claim, not a new deliverable
   sentence, so this remains revision-in-place under the 2026-08-10 rule. If
   the human reviewer reads the boundary the other way — that demoting the
   headline from result to target changes the claim's identity — the correct
   disposition is supersession with this design as the successor, and I flag
   that as the reviewer's call, not mine to preempt.
4. **`dies_like_prior` rewritten again.** The card inherits the
   annotation-provenance lesson in a precise form: the *name* honeycombing is
   unavailable without an independent reference standard, and no reader-derived
   surrogate may stand in for one. It does not die that way, because the
   primary analysis needs no reader labels — but the rung-3 sentence was
   priced as if the name came free, and it does not.
5. **What is lost, plainly.** The physician-legible headline — the entire
   point of the program's deliverable — is demoted from result to target.
   `interest` 5 → 4 and `regret` 5 → 4: a model shown to use a prespecified
   cyst-network topology index is still a physician-adjacent mechanism
   sentence, but it is one translation step short of the charter's deliverable,
   and that step is now owned by a validation module this study does not
   contain. `medical_relevance` stays 3 (already deflated in amendment one).
   The priority arithmetic must be recomputed in revision with these values
   and rung target 1.

**Status:** CONVERGED — the design stands as amended in rounds 1–2; the
confirmatory claim is stated at the level of the computed topology index; the
honeycombing sentence is out of scope until the critic's construct-validation
condition is met, and that condition is recorded verbatim as the rung-3
move-up. Three rounds produced two amendments and one concession, each
narrowing the claim toward what the instruments can actually certify; the
surviving study is smaller than the card promised and, for exactly that
reason, defensible.
