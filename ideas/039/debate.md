# Debate transcript

## Round 1 — CRITIC

**Position:** The proposed projection-versus-tangent contrast does not identify the original claim that a surrogate uses central-volume-law violation as a confidence map for perfusion evidence.

**Argument:** Removing the normal component of the (CBF, CBV, MTT) triplet and comparing it with equal-L2 tangent shams measures directional sensitivity of a nonlinear multichannel predictor. A residual-blind model that responds directly to MTT, or to the particular spatial locations where the normal residual is concentrated, can show a larger and monotone response to residual removal while never discounting perfusion evidence according to inconsistency. Energy matching does not match edit placement or alignment with the model gradient. Thus even a fully positive result supports only “prediction depends on the off-manifold component,” not the deliverable sentence’s stronger functional claim that violation acts as a hidden confidence map. Narrowing the deliverable to residual dependence would change the original question and therefore require a successor candidate under the claim-identity rule.

**What would change my mind:** Add a preregistered interaction arm that applies the same small calibrated perfusion-evidence edit at high-residual and low-residual locations matched on baseline CBF/Tmax severity, lesion distance, anatomy, and edit support, and show that response to that identical evidence edit is selectively attenuated at high-residual locations, with spatially matched null shams and an explicit test ruling out direct MTT-value sensitivity.

**Status:** OPEN

## Round 1 — PROPOSER

**Responding to:** The projection-versus-tangent contrast only shows that the
prediction depends on the off-manifold component of the map triplet. Any
smooth multichannel predictor is anisotropic, and the normal component has a
distinctive spatial placement, so a residual-blind model reading raw MTT (or
reading the locations where the residual happens to concentrate) can pass the
projection gates, the dose-response gate, and the equal-energy sham gate
without ever discounting perfusion evidence by inconsistency. The deliverable
sentence — violation used *as a hidden confidence map for perfusion evidence*
— asserts an interaction the design never measures.

**Response:** AMEND

**Argument:** The objection is technically correct and I will not contest it:
energy matching equalizes edit size, not edit placement or gradient
alignment, and monotone dose response is produced by any linear readout of a
fixed component. The projection contrast, standing alone, identifies
residual *dependence*, not a confidence-map *role*. The amendment adopts the
critic's interaction arm as the confirmatory carrier of the deliverable
sentence, with these specifics:

1. **Interaction arm (new, primary).** Within each held-out case, select
   voxel-site pairs (high-X, low-X) matched on baseline CBF and Tmax strata,
   distance to the Tmax>6 s boundary and to the eroded support edge, and
   tissue laterality. At both sites apply the identical small, calibrated
   perfusion-evidence edit (a fixed CBF-deficit deepening at frozen dose,
   inside a fixed-radius patch). Primary readout: paired difference in
   prediction response between high-X and low-X sites. The confidence-map
   hypothesis predicts selective attenuation at high-X sites; the anisotropy
   artifact the critic names makes no such prediction, because the edit —
   not the residual — is what varies, and it is identical at both sites.
2. **Direct-value-sensitivity discriminator (the critic's explicit test).**
   High-X and low-X sites matched only on (CBF, Tmax) can still differ
   systematically in raw MTT or CBV values, so a model reading MTT values
   directly could mimic the interaction. Therefore two preregistered
   matching strata: (a) sites additionally matched on MTT (residual
   difference then carried by CBV), and (b) sites additionally matched on
   CBV (residual difference carried by MTT). The confidence-map hypothesis
   predicts attenuation in **both** strata, since X is the same construct in
   each; direct value-reading of any single channel predicts an interaction
   in at most one. Concordance across strata is a frozen confirmatory
   requirement, not a post-hoc check.
3. **Null shams.** The same matched site pairs receive a zero-dose sham pass
   and an off-site same-dose sham, establishing the paired noise floor and
   the locality of the response before the interaction statistic is read.
4. **Demotion of the projection arm.** The projection/tangent contrast
   becomes a supporting gate — it establishes that the residual is seen at
   all (a model with zero off-manifold sensitivity cannot be using X as
   anything), and remains a required precondition for interpreting the
   interaction arm. It no longer carries the deliverable sentence.

**Identity check:** The one-sentence question — is the model using voxelwise
violation of the central-volume identity as a hidden confidence map for the
released perfusion estimates? — is unchanged. The amendment strengthens the
design so that the "for perfusion evidence" clause is measured (response to
an identical evidence edit, stratified by X) instead of presumed from
directional sensitivity. Same claim, stronger instrument; this is
revision-in-place under the 2026-08-10 rule, not a successor.

**What is lost, stated plainly:** First, the original card's
use-versus-association section was insufficient as confirmatory evidence and
is hereby admitted to have overclaimed; a positive projection result alone
can no longer support the deliverable sentence. Second, the interaction arm
has a real feasibility cost: it requires an inventory of matched
(high-X, low-X) site pairs satisfying the double-matching strata within the
20 test cases, and that inventory depends on the empirical joint
distribution of X with CBF/Tmax/MTT/CBV, which nobody has seen yet. Stage 0
therefore gains a frozen count requirement — a minimum number of qualifying
matched pairs per stratum (to be fixed in the feasibility memo before any
model sees an edit) — and an insufficient inventory kills the confirmatory
arm honestly rather than degrading the matching. Third, if the two strata
disagree (attenuation under MTT-matching but not CBV-matching, or vice
versa), the confirmatory claim fails and the result demotes to rung-1
residual dependence with a channel-specific caveat; that outcome is
preregistered as a negative for the deliverable sentence, not as a partial
success.

**Status:** OPEN

## Round 2 — CRITIC

**Position:** The amended high-X versus low-X interaction is still observational in X, so it cannot identify that the central-volume residual itself modulates trust in perfusion evidence.

**Argument:** The amendment answers the original question in name, but its instrument does not yet isolate the named mechanism. In the MTT-matched stratum, high-X and low-X sites must differ in CBV (or in the joint CBF-CBV configuration); in the CBV-matched stratum, they must differ in MTT (or in the joint CBF-MTT configuration). A multichannel surrogate with no residual or confidence computation can therefore show attenuated response to the identical CBF edit in both strata simply because its local CBF response is nonlinear and conditioned on the other perfusion channels. Concordance across the two strata does not rule this out: a network can have CBV-conditioned CBF saturation in one stratum and MTT-conditioned CBF saturation in the other. Matching baseline CBF, Tmax, anatomy, and distances also cannot match the full local receptive-field state that determines response. The off-site and zero-dose shams establish locality and numerical stability, not causal attribution to X. Thus a positive result would establish that naturally high-X tissue is an effect-modifier marker, but not that violation of CBV = CBF x MTT is the modifier the model uses. This is the same deliverable, so no identity failure occurs; the remaining failure is identifiability.

**What would change my mind:** At the same held-out sites, causally set X to preregistered high and low values with small, realism-gated edits that hold the chosen perfusion-severity coordinates fixed, then apply the identical CBF evidence edit in a crossed factorial design and test the within-site difference-in-differences. Include matched coordinate-preserving shams, and require the interaction to reverse or disappear when X is restored while the local receptive-field context is otherwise unchanged. That would manipulate the proposed confidence signal rather than compare sites where it co-varies with other channel values.

**Status:** OPEN

## Round 2 — PROPOSER

**Responding to:** The round-one interaction arm is observational in X.
High-X and low-X sites, however carefully matched on named coordinates,
necessarily differ in the unmatched channel values and in unmatchable local
receptive-field state, so a residual-blind surrogate whose CBF response is
nonlinearly conditioned on CBV in one stratum and on MTT in the other can
reproduce concordant attenuation. A positive result would show that
naturally high-X tissue is an effect-modifier marker, not that the
central-volume residual is the modifier the model uses. The fix the critic
names: manipulate X causally at the same site, crossed with the evidence
edit, and read the within-site difference-in-differences.

**Response:** AMEND

**Argument:** The objection stands and I adopt the critic's design, because
for this particular residual it is constructible rather than aspirational.
X = |log(CBV) - log(CBF) - log(MTT/60) - k_case| has, with CBF and Tmax
held fixed at the site, two remaining degrees of freedom (CBV, MTT) against
one residual coordinate — so X can be set to a preregistered value while
the severity coordinates the evidence edit acts on are bit-identical, and
it can be set through **either** free channel. The amendment:

1. **Within-site crossed factorial (new confirmatory carrier).** At each
   selected held-out site, a 2x2 design: X set to a preregistered low or
   high value (small fixed-radius, realism-gated edit holding CBF and Tmax
   voxelwise fixed) crossed with the identical calibrated CBF-deficit
   evidence edit (present/absent). Primary readout: within-site
   difference-in-differences in predicted lesion probability. Because the
   X-low cells sit in the same factorial at the same site, the critic's
   restore-and-reverse requirement is satisfied by construction: the same
   receptive field is observed under both X states, with and without the
   evidence edit, and the confidence-map hypothesis requires the evidence
   response to shrink in the X-high cells and recover in the X-low cells.
   Cross-site matching, and its unmatchable receptive-field confound, is
   no longer load-bearing; each site is its own control.
2. **Channel-carrier concordance, now causal.** Setting X consumes one
   degree of freedom, so it can be carried entirely by CBV (arm A) or
   entirely by MTT (arm B) with the other channel untouched. A
   confidence-map reader predicts the same attenuation in both arms at
   matched |delta-X|; the critic's round-two mechanism (CBV-conditioned
   saturation here, MTT-conditioned saturation there) must now produce
   the same interaction under two disjoint single-channel edits — a
   stronger coincidence than in the observational version, but, per the
   critic, still logically possible. Hence:
3. **Sign-symmetry discriminator (new, and specific to this invariant).**
   The residual is signed; X is its magnitude. At sites with r > 0,
   raising X via CBV means raising CBV; at sites with r < 0, raising X via
   CBV means **lowering** CBV — same |delta-X|, opposite raw-value motion.
   The confidence-map hypothesis is even in the sign of r: attenuation
   must track |delta-X| identically in both sign strata. Any mechanism
   conditioned on raw channel values (saturation in CBV, saturation in
   MTT, or any monotone conditioning) is generically odd under this flip:
   it predicts effects that follow the direction of the raw edit, not its
   |delta-X|. Frozen confirmatory requirement: concordant attenuation
   across carrier arms AND across residual-sign strata, at matched
   |delta-X| dose. Stage 0 gains a corresponding inventory gate: a frozen
   minimum count of eligible sites per (carrier x sign) cell, fixed in the
   feasibility memo before any model sees an edit; an empty cell (e.g.,
   the released maps turn out to have one-signed residuals) kills the
   sign stratum honestly and demotes the confirmatory claim to
   carrier-concordance only, preregistered as such.
4. **Realism gate for X-raising.** Removing X (projection) moves maps
   toward consistency; the factorial's X-high cells move away from it,
   which risks manufacturing out-of-distribution inconsistency. Frozen
   rule: set-points for X-high are drawn from within the observed
   same-case X distribution over comparable tissue (between fixed
   percentiles, to be frozen in the memo), never beyond it, and the
   existing nearest-neighbor feature-distance gate applies per cell. The
   zero-dose and off-site shams from round one carry over unchanged, now
   run per factorial cell.

**Identity check:** The one-sentence question — is the model using voxelwise
violation of the central-volume identity as a hidden confidence map for the
released perfusion estimates? — is unchanged, and the instrument now
manipulates the violation itself rather than sampling tissue where it
happens to vary. This is the most direct operationalization of the question
so far, not a narrowing of it.

**What is lost, stated plainly:** First, this is the second amendment, and
the confirmatory instrument is now the critic's design, not the original
card's; the card's contribution reduces to the invariant, the residual
construction, and the Stage 0 dataset audit, with the causal design
credited to the debate. Second, the factorial multiplies the edit budget
(4 cells x 2 carriers x 2 sign strata x shams per site) and adds two new
kill surfaces: the (carrier x sign) inventory gate and the X-raising
realism gate, either of which can honestly kill the confirmatory arm after
the download and surrogate training are already sunk. Third, a scope
limit the critic's own design implies and I make explicit rather than
hide: even the factorial identifies X functionally, not mechanistically —
a model passing carrier-concordance, sign-symmetry, and |delta-X| dose
response is behaving as an X-reader on the tested support, but rung 1
cannot say a residual is computed anywhere inside the network, and the
card's prohibited-conclusions list gains that sentence verbatim. If the
critic accepts that functional reading as what "uses X as a hidden
confidence map" means — which is what the deliverable sentence has meant
since the card was written — the designs have converged.

**Status:** OPEN

## Round 3 — CRITIC

**Position:** The proposed 2x2 factorial is not factorial because the CBF-deficit “evidence” edit itself changes the central-volume residual X, so the design does not hold the putative confidence signal fixed while measuring response to evidence.

**Argument:** The round-two amendment adequately repairs the observational-in-X objection by moving to within-site manipulation, and it still targets the original confidence-map question rather than changing claim identity. But its two factors are algebraically coupled. With signed residual r = log(CBV) - log(CBF) - log(MTT/60) - k_case and X = |r|, applying a CBF deepening of delta in log units changes r to r - delta and therefore changes X by an amount and direction that depend on the residual-sign stratum. Thus the nominal (X-low, evidence-present) cell is no longer X-low at its preregistered set-point, and the nominal (X-high, evidence-present) cell is no longer matched to the evidence-absent X-high cell. The resulting difference-in-differences mixes modulation of CBF sensitivity by X with the direct nonlinear response to moving X during the CBF edit; sign-symmetry does not rescue this, because the algebra predicts different X motion on opposite sides of zero. Carrier concordance also does not rescue it: whether X was initially set through CBV or MTT, the subsequent CBF edit perturbs the same residual. A positive interaction therefore still would not establish that a fixed high-X state attenuates otherwise identical perfusion evidence.

**What would change my mind:** Define all four cells jointly in residual/severity coordinates and show voxelwise that the evidence-present and evidence-absent cells retain exactly the same preregistered signed-r (or X plus sign) set-point by compensating the CBF edit through the designated carrier channel. Then add coordinate-matched shams for that compensatory channel motion and require the confidence interaction to replicate across CBV-carried and MTT-carried constructions without crossing r = 0; the feasibility memo must also show these jointly constructed cells pass the frozen realism gate.

**Status:** OPEN

## Round 3 — PROPOSER

**Responding to:** The 2x2 factorial is not factorial: a CBF deepening of
delta in log units moves the signed residual r by delta itself, so the
evidence-present cells no longer sit at their preregistered X set-points.
The difference-in-differences therefore mixes X-modulation of CBF
sensitivity with the model's direct nonlinear response to r being moved
during the edit; the sign-symmetry discriminator breaks because the CBF
edit moves |r| in opposite directions on opposite sides of zero; and
carrier concordance cannot help because the evidence edit perturbs the
same residual regardless of which channel set X.

**Response:** AMEND

**Argument:** The algebra is conceded outright: with
r = log(CBV) - log(CBF) - log(MTT/60) - k_case, any single-channel CBF
edit is also an r edit. The round-two "evidence" factor was itself an
X-manipulation — the design's own invariant makes a pure one-channel
perfusion edit off-manifold by construction, and I should have seen that
before the critic did. The amendment adopts the critic's compensated
construction in full, with one structural addition (role-disjoint channel
assignment) that closes the loophole the compensation would otherwise open:

1. **The evidence edit is redefined as r-preserving.** The confirmatory
   evidence edit is now the joint motion: log(CBF) lowered by delta AND the
   designated compensator channel moved by exactly the offsetting amount
   (log(CBV) lowered by delta, or log(MTT) raised by delta), voxelwise,
   inside the same patch. Signed r is bit-identical to its preregistered
   set-point in all four cells. Note what this actually is: lower CBF with
   proportionally lower CBV, or lower CBF with proportionally longer MTT,
   is precisely the covariation the central-volume identity mandates for a
   real flow deficit. The uncompensated round-two edit was manufacturing
   inconsistency while claiming to present evidence; the compensated edit
   is the physiologically coherent perfusion-worsening this study's own
   physics says evidence should look like. The repair is not a patch — it
   is the correct operationalization of "perfusion evidence" under the
   card's invariant, and it took three rounds to reach it.
2. **Role-disjoint arms.** Compensating through the X-carrier channel would
   let one channel do double duty and re-entangle the factors. Frozen
   assignment instead: arm A sets X through CBV and compensates the
   evidence edit through MTT; arm B sets X through MTT and compensates
   through CBV. Within each arm the three roles — evidence (CBF), X-carrier,
   compensator — are carried by three disjoint channels, and the roles swap
   across arms. A confidence-map reader predicts the same attenuation in
   both arms; any artifact driven by the compensator's raw motion must now
   reproduce itself under two disjoint compensator channels moving in
   different directions.
3. **Set-point verification gate.** Before any model inference, every cell
   is checked voxelwise: signed r must equal its preregistered set-point
   within a frozen numerical tolerance, and no voxel in any cell may cross
   r = 0. Per-cell maximum deviation is logged; a violating cell is
   invalid and discarded as such, never reinterpreted. The X-low set-point
   is frozen strictly positive in |r| with the site's native sign, so all
   four cells of a site live in one sign stratum by construction.
4. **Compensator-motion sham, per cell.** The critic's coordinate-matched
   sham: the compensator channel's motion applied alone, at the identical
   dose and support, with no CBF component. This isolates the model's
   direct response to the compensatory motion, and the confirmatory
   interaction must survive with this sham response subtracted or gated.
   The zero-dose and off-site shams carry over per cell.
5. **Sign-symmetry discriminator, rescoped.** With evidence edits now
   r-neutral, the sign test no longer applies to them (there is no X
   motion to be even in). It survives on the X-setting factor, where it
   belongs: raising X through a given carrier still moves that carrier's
   raw value in opposite directions in the r > 0 and r < 0 strata, and the
   confidence hypothesis still predicts attenuation tracking |delta-X|
   identically in both. Stated plainly: the discriminator's scope shrank
   from "both factors" to "the X factor," and the card must say so.
6. **Feasibility-memo obligations, per the critic.** The memo must show,
   before any model sees an edit: (a) that jointly constructed cells pass
   the frozen realism gate per cell — the nearest-neighbor feature-distance
   gate applied to the full joint edit, not per channel; (b) the inventory
   gate recount under the tighter eligibility — a site now needs dose
   headroom in three channels simultaneously (X-set-point motion, CBF
   delta, compensator delta) without leaving observed value ranges or
   hitting clipping bounds, per (carrier x sign) cell; frozen minimum
   counts as before, empty cells kill or demote preregistered.

**Identity check:** The one-sentence question — is the model using voxelwise
violation of the central-volume identity as a hidden confidence map for the
released perfusion estimates? — is unchanged. What changed is what counts
as "perfusion evidence": an identity-consistent worsening rather than a raw
single-channel push. That is a refinement toward the question, not away
from it: evidence that itself violates the identity was a defective probe
of whether identity violation modulates trust in evidence.

**What is lost, stated plainly:** First, this is the third amendment, and
the house rule says three amendments usually means the original idea was
wrong. The honest reading: the original confirmatory instrument was wrong,
three times, and the instrument now standing is entirely debate-built. What
survives of the card is the question, the invariant, the residual
construction, the Stage 0 dataset audit, and the kill-gate discipline. The
card's identifiability score of 4 was written for a dead design and must be
re-justified or lowered against the current one at revision time; the human
reviewer should weigh whether question-plus-invariant-plus-audit still
earns the shortlist slot given that the design had to be rebuilt from the
outside. Second, single-channel evidence sensitivity is now out of scope:
a reader asking "does the model discount a plain CBF drop at high-X sites?"
gets no answer from this design, because a plain CBF drop is not
r-neutral and cannot be — that question is unanswerable within this
factorial and the card must list it as such rather than imply it. Third,
the edit budget grows again (per site: 4 cells x 2 arms, each with
compensator, zero-dose, and off-site shams) and the inventory gate tightens
to three-channel dose headroom, adding a real probability that Stage 0
kills the confirmatory arm after the 99 GB download and surrogate training
are sunk. Fourth, the sign-symmetry discriminator covers less than round
two advertised, as stated in point 5.

If the critic accepts this construction, the disagreement is exhausted on
design grounds: every remaining kill surface (algebraic triviality of the
released residual, inventory counts, realism of joint edits, surrogate
channel reliance) is empirical and sits behind preregistered Stage 0 gates
rather than behind an unresolved identification argument.

**Status:** OPEN
