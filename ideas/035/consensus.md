# Debate summary — idea 035

## Agreed

- In round 1, both sides agreed that the released winning model consumes CBF, CBV, MTT, Tmax, and CTA rather than NCCT, so the proposed NCCT CSF-reserve and net-water-uptake interventions cannot reach that frozen model as specified.
- In round 1, both sides agreed that net water uptake is validated as an admission-NCCT attenuation measurement within ischemic tissue, not as a mechanically meaningful swelling dose in equalized CTA or perfusion-tensor space.
- In round 1, both sides agreed that changing CSF reserve while holding adjacent parenchymal inputs bit-identical does not create a physically possible compliance counterfactual: real changes in reserve entail changes in neighboring anatomy.
- In round 1, both sides agreed that ISLES'24 has no independent acute irreversible-injury measurement and no edema, mass-effect, deformation, or intracranial-pressure target with which to validate the proposed mechanical interpretation.
- In rounds 1–2, both sides agreed that a signed factorial interaction could exclude a purely additive age/atrophy main effect, but could not identify intracranial compliance or swelling because the edited factors fail to instantiate those constructs.
- In rounds 1–2, both sides agreed that narrowing the result to sensitivity to synthetic tensor patterns would change the deliverable's identity, as would replacing it with a reserve-stratified observational error audit. Either must enter the normal pipeline as a successor rather than an amendment to idea 035.
- In round 2, both sides agreed that the original idea should be rejected for an identifiability failure at the measurement-validity level.

## Unresolved

No substantive disagreement remained after round 1. The critic accepted the proposer's concession and identity analysis in round 2, and the proposer confirmed convergence.

The debate did not decide whether either proposed successor is worth prioritizing. The proposer regarded the reserve-stratified benchmark error audit as the stronger successor and the tensor-pattern interaction study as weaker; the critic did not contest that ordering, but neither proposal was debated on its own merits. Evidence that would settle their scientific value would require separate idea cards, primary-source novelty audits, and designs evaluated under the current charter.

## Positions that moved

- The proposer conceded in round 1 in response to the critic's construct-validity argument. Specifically, the proposer accepted that neither the post-equalization edema-like edit nor the parenchyma-preserving CSF edit can carry the physical construct named by the question, and that ISLES'24 lacks an independent target that could restore that interpretation. This concession was earned: it answered a concrete argument grounded in the released model inputs and the dataset's missing measurements.
- The critic moved to convergence in round 2 after finding that the proposer had accepted the fatal objection, preserved the limited statistical value of the interaction without overclaiming it, and correctly applied the claim-identity rule to the alternatives.
- The proposer confirmed convergence in round 2. This was not an unearned capitulation; no live disagreement remained to answer.

## Amendments made

No amendment was made to idea 035. The round-zero claim remained that the final-infarct model uses baseline intracranial CSF reserve as a geometric prior on expansion beyond acute tissue injury, and that claim was rejected.

Two possible replacements were identified but explicitly excluded from revision-in-place:

- An observational reserve-stratified benchmark error audit would ask whether held-out prediction error varies with baseline NCCT CSF/ICV after prespecified adjustment. It loses all claims about model use, compliance, edema, and causal mechanism.
- A tensor-pattern interaction-sensitivity study would test whether outputs respond nonlinearly to two prespecified synthetic input patterns. It loses the physical interpretation of those patterns as reserve and swelling.

Both retain only part of the original medical motivation and would need new candidate identities with `parent_id` idea-035.

## Recommendation

**REJECT.** The proposed experiment cannot identify the compliance-and-swelling mechanism it names because neither intervention validly measures its assigned construct in the winner's input space, and ISLES'24 provides no independent mechanical or edema/deformation target to validate the interpretation. The single most important thing for the human to examine is whether any natural paired or source-validated dataset can jointly provide independently measured intracranial compliance, mechanically observed swelling or deformation, controlled acute injury burden, and a model input that preserves those measurements; without that new evidence, this idea cannot be revived without changing its identity.

## In plain terms

This idea asks whether a stroke model treats the fluid space inside the skull as spare room for swelling when predicting the eventual infarct. It proposes changing apparent fluid reserve and injury-related image patterns to see whether the model's predicted lesion expands differently.

The debate concluded that those image changes do not actually create different physical levels of skull compliance or swelling. The model also does not consume the NCCT image on which the proposed measurements are defined, and ISLES'24 has no independent swelling, deformation, or pressure measurement that could validate the interpretation. A simpler error-by-fluid-reserve audit may still be useful, but it is a separate observational question.

The human is being asked to judge whether a different dataset or natural paired design now exists that measures compliance and swelling independently while controlling acute injury.

```json
{"verdict": "KILL", "kill_code": "IDENTIFIABILITY_FAILURE", "unblock": "Obtain a natural paired or source-validated design with independently measured intracranial compliance and mechanically observed swelling or deformation, acute injury burden held fixed, and an external edema, displacement, or pressure measurement that validates the claimed physical dose."}
```
