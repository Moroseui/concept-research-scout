# Debate summary — idea 014

## Agreed

- The original card incorrectly assumed that a runnable frozen Pierson checkpoint existed. The repository provides training and analysis code, not trained weights; therefore the published artifact cannot presently be probed as proposed (critic round 1; proposer conceded in round 1).
- A retrained model is not the published checkpoint. The defensible object, if reproduction succeeds, is a family of independently trained models following the published recipe and passing preregistered behavioral gates, with the conclusion explicitly restricted to that family (proposer round 1; critic accepted this repair in round 2).
- Reproduction is the live keystone: OAI access, preprocessing under realistic compute, and recovery of the published better-than-KLG pain performance and disparity signature must precede any model-decoding work. This remains `NOT_INSPECTED` and feasibility is lower than the original card reported (rounds 1–4).
- The original learned-direction erasure cannot isolate directional trabecular texture from continuous sclerosis/density, joint-space width, alignment, osteophytes, and acquisition sharpness. Random, KL, and JSN direction controls do not cure that estimand mismatch (critic round 2; proposer conceded in round 3).
- Merely comparing horizontal and vertical learned directions would not make the mechanobiology analogy load-bearing. The primary design must manipulate or otherwise isolate orientation-specific texture while controlling non-directional image content (rounds 2–3).
- A Fourier angular-power edit, even with DC and radial power fixed, is not by itself a biological counterfactual of trabecular thickening and rarefaction: phase, connectivity, spatial organization, boundary effects, ringing, and directional blur remain possible explanations (critic round 3; proposer conceded in round 4).
- The original deliverable sentence overclaimed biology relative to the declared image-computable X. At most, this experiment directly establishes use of a measured radiographic directional texture/fractal signature; any interpretation as trabecular thickening and rarefaction must be supported separately by verified primary literature and stated as inherited interpretation (proposer round 4).
- The proposed within-film left-versus-right analysis is a useful checkpoint-free premise gate but does not answer whether a model uses X. It should remain a separate candidate rather than be presented as a repair of Idea 014 (critic round 1; proposer agreed in round 1).
- A null response to a synthetic spectral edit is sensitivity-limited for the broad biological-texture claim because a model could use phase-coherent structure not changed by the edit. The round-3 claim of a decisive broad negative was withdrawn in round 4.
- The debate did not converge in one round: it exposed three distinct problems—model identity/availability, intervention identifiability, and biological validity of the manipulated quantity—and produced three substantive amendments.

## Unresolved

### Can the published model family be reproduced under the access and compute constraints?

- **Question:** Can at least two independent models trained from the released Pierson recipe on OAI pass preregistered gates for better-than-KLG pain prediction and the published disparity-reduction signature on a frozen evaluation split?
- **Proposer's position:** Yes in principle; a multi-seed, behavior-gated reproduction is a scientifically stronger object than one checkpoint and preserves the original gap-decoding question at the model-family level. The proposer nevertheless treats this as an uncertain Stage-0 gate.
- **Critic's position:** The family-level reformulation is legitimate, but no representation exists to study until reproduction is actually demonstrated; matching aggregate performance alone would not suffice unless the specified behavioral signatures and cross-seed mechanism replication are recovered.
- **What evidence would settle it:** Active OAI access; an executable, resource-accounted preprocessing and training pipeline; frozen split and tolerances registered before texture analysis; and at least two independent seeds that pass both behavioral reproduction gates. Failure to obtain access, train within the compute envelope, or pass the gates pauses or ends the model-decode study.

### Does the revised image edit identify use of the declared fractal-signature X rather than edit artifacts?

- **Question:** Does an FSA-calibrated, band-limited angular edit under radial-power/DC constraints and matched shams selectively change model pain scores because it changes directional fractal signature, rather than because it introduces detectable synthetic morphology or frequency-orientation artifacts?
- **Proposer's position:** The legitimate X is the image-computable directional fractal signature, not inaccessible 3-D trabecular architecture. Calibration in post-edit FSA units, an acquisition-matched real-versus-edited discriminator equivalence gate, an equal-norm isotropic-density sham, and a spectrum-preserving phase sham can make use of that radiographic statistic identifiable.
- **Critic's position:** The last critic turn did not assess these new safeguards. Its standing concern is that spectral manipulation can alter phase-coherent spatial realization and create CNN-salient artifacts; marginal statistic matching and equal norm are insufficient, and biological architecture would require independent structural validation or a validated generative counterfactual.
- **What evidence would settle it:** Before outcome testing, show at every planned edit magnitude that edited images are equivalent to real acquisition-matched images under a prespecified, adequately powered discriminator test; that the phase and isotropic shams isolate their intended quantities; that FSA changes by the prescribed amount while mean intensity, radial power, boundaries, geometry, and non-directional texture remain within preregistered tolerances; and that score effects are selective across every gate-passing seed. A paired radiograph–micro-CT/HR-pQCT validation or structurally conditioned generator would settle the stronger biological-counterfactual claim, but is not necessary for the narrower radiographic-statistic claim. Because the critic never responded to the round-4 amendment, consensus on sufficiency has not been reached.

### Is directional fractal signature a medically legitimate name for the model-used signal, and how much biological gloss may it carry?

- **Question:** Can the rung-3 sentence describe the radiographic fractal signature as directional trabecular thickening and rarefaction along load paths?
- **Proposer's position:** The experiment should claim direct use only of directional medial tibial subchondral radiographic texture. It may append the thickening/rarefaction interpretation if primary FSA literature directly validates that bridge; otherwise the biological gloss must be removed.
- **Critic's position:** A response to angular power does not establish genuine trabecular architecture. The stronger biological wording requires independent validation against 3-D bone structure or a validated structural counterfactual.
- **What evidence would settle it:** Direct inspection of the primary validation papers to determine exactly what radiographic FSA was validated against and with what acquisition and structural reference. If they validate only prognostic association or image-statistic repeatability, the sentence must stop at “directional radiographic texture/fractal signature.” If they directly establish the proposed structure–signature mapping in a relevant setting, the interpretation may be cited as source-supported rather than presented as a new experimental finding.

### Does discriminator equivalence adequately establish in-distribution editing?

- **Question:** Is chance-level or equivalence-bounded real-versus-edited discrimination sufficient to rule out OOD edit response?
- **Proposer's position:** An acquisition-matched discriminator evaluates the joint spatial realization and, together with phase and isotropic shams, is a practical hard gate that does not depend on an unverified paired 3-D dataset.
- **Critic's position:** Not stated after this amendment. Its prior standard asked for both acquisition-matched indistinguishability and independent structural validation; it may regard discriminator failure as sufficient to reject an editor but discriminator success as insufficient to validate biology.
- **What evidence would settle it:** A preregistered equivalence design with power calculations, held-out detectors of multiple architectures, and sham calibration can settle whether gross edit detectability is controlled. It cannot alone settle whether the image represents genuine altered bone architecture; that requires structural reference data. The distinction between the narrower radiographic-X claim and the stronger biological claim must therefore remain explicit.

## Positions that moved

- **Proposer, round 1:** Conceded that no published checkpoint is available and that “frozen Pierson model” was a misnomer, in response to the critic's repository and access evidence. Reframed the object as behavior-gated reproductions across at least two seeds and lowered feasibility. This concession was earned.
- **Critic, round 2:** Withdrew the model-identity objection to the amended family-level claim after the proposer specified independent seeds, preregistered behavioral reproduction gates, and an explicitly narrowed conclusion. This movement was earned.
- **Proposer, round 3:** Conceded that concept-direction erasure cannot identify directional architecture and that horizontal-versus-vertical probe comparison does not isolate orientation, in response to the critic's collinearity and estimand-mismatch argument. Replaced erasure as the primary identifier with an image-space intervention. This concession was earned.
- **Critic, round 3:** Accepted that angular/radial spectral separation numerically separates orientation anisotropy from isotropic spectral energy, but rejected the inference from that statistic to biological trabecular architecture because phase and spatial morphology remain unconstrained. This was a qualified movement based on the new intervention specification, not acceptance of the full claim.
- **Proposer, round 4:** Conceded that the Fourier edit is not a counterfactual of remodeled bone, that the earlier marginal and round-trip gates were inadequate, and that the claimed decisive negative applied only to the band-power hypothesis. This followed the critic's new phase/biological-validity argument and was earned.
- **Proposer, round 4:** Narrowed the deliverable to direct use of radiographic directional texture, making the thickening/rarefaction interpretation conditional on primary-source validation. This was an earned response to the distinction between image statistic and biological architecture.
- No concession appears UNEARNED. The final round's amendment was not answered by the critic, so it must not be recorded as accepted consensus.

## Amendments made

At round zero, the card claimed that the specific frozen Pierson pain model could be probed; that a validation-learned texture direction could be erased to establish model use; and that the result could support a direct sentence about directional thickening and rarefaction of load-bearing trabecular bone.

The amended idea instead claims:

- The object is a family of at least two independently trained models following the published recipe and passing preregistered better-than-KLG and disparity-signature reproduction gates. It makes no claim about Pierson's unreleased weights.
- Reproduction and resource feasibility are Stage 0, with `NOT_INSPECTED` keystone status. No texture probe or outcome-dependent editor development begins unless the behavioral gate passes.
- The primary proposed identifier is an image-space, band-limited anisotropy intervention calibrated by achieved change in the measured directional fractal signature. DC, radial power, low-frequency joint geometry, and prescribed nuisance quantities are held within tolerances.
- Controls now include an isotropic-density edit, a spectrum-preserving phase perturbation, zero/identity processing controls, and an acquisition-matched real-versus-edited discriminator equivalence gate at every used magnitude. Representation probing and erasure are exploratory corroboration only.
- The direct rung-3 claim is limited to use of directional medial tibial subchondral radiographic texture/fractal signature. “Thickening and rarefaction along load paths” is only a source-supported interpretation if primary literature directly validates it.

What was lost:

- Any claim about the exact published network.
- The original simple, relatively cheap erasure experiment and its stated two-week timeline.
- A direct experimental claim about 3-D trabecular architecture.
- Strong negative-result value for the broad biological hypothesis; a null remains sensitivity-limited unless the claim is narrowed to the exact manipulated radiographic statistic.
- Feasibility and evaluation readiness: the study now requires gated-data reproduction plus a bespoke, validated editor and realism/sham suite.

## Recommendation

**PAUSE.** The revised question remains scientifically coherent, but the rate-limiting model asset has not been reproduced, and the final edit-validity amendment has not been tested or answered by the critic. The single most important thing for the human to inspect before deciding is whether the released Pierson pipeline can, with available OAI access and the allowed compute, produce at least two independent models that pass preregistered better-than-KLG and disparity-signature gates on a frozen split. Without that, there is no model family to decode; editor validity is the next gate only after reproduction succeeds.

```json
{"verdict": "PAUSE", "unblock": "Demonstrate at least two independently trained Pierson-recipe models that pass preregistered pain-performance and disparity reproduction gates on a frozen OAI split within the available access and compute constraints."}
```
