# Debate summary — idea 036

## Agreed

- In round 1, both sides agreed that a prediction discontinuity at a registered population-atlas border cannot identify model use of an internal vascular map. The same pattern can arise when an evidence-driven model reads nonlocal, case-specific occlusion geometry from CTA and predicts downstream risk without containing an atlas prior.
- In round 1, both sides agreed that matching released local CBF, CBV, MTT, Tmax, and NCCT measurements, together with shifted-border placebos, contralateral controls, and registration perturbations, does not exclude that alternative mechanism. True patient-specific supply boundaries tend to lie nearer the atlas boundary than arbitrary shifted borders, while the relevant nonlocal evidence is absent from the matching set.
- In round 1, both sides agreed that the population atlas is not an independently measured patient-specific perfusion-territory map and therefore cannot provide the dissociation needed to separate a learned atlas prior from case-derived territorial reasoning.
- In rounds 1 and 2, both sides agreed that an out-of-fold audit of calibration and segmentation errors near registered border zones is defensible and potentially useful, but answers a different question. Under the claim-identity rule it must enter as a separate candidate with `parent_id` idea-036 and must not be described as evidence that the model uses a vascular map.
- In rounds 1 and 2, both sides agreed on the revival condition for the original question: held-out predictions in an obtainable cohort with independently measured patient-specific perfusion territories that dissociate from the population atlas, or a validated intervention on the alleged internal territory variable that holds case evidence fixed.

## Unresolved

There is no substantive disagreement left within the proposed design. The proposer and critic agree that the current estimand does not identify the original use claim and that the available ISLES'24 data do not supply the required patient-specific territory measurement.

One empirical condition remains open rather than disputed: whether a suitable external dissociation cohort or valid internal-variable intervention can become obtainable. Both sides take the position that either could revive the original question. Evidence that would settle it is direct documentation and inspection of such a cohort's independent territory measurement together with held-out audited-model predictions, or validation evidence showing that an intervention changes only the alleged internal territory variable while holding case evidence fixed.

## Positions that moved

- The proposer conceded in round 1, in direct response to the critic's argument that the atlas border assigns no treatment and cannot separate an internalized map from genuine border-zone physiology, spatial location, or nonlocal case evidence. This was an earned concession: the proposer supplied a concrete counterexample in which a model with no atlas prior passes the entire proposed gate battery.
- In round 2, the critic accepted the proposer's concrete null mechanism and the claim-identity analysis as closing the objection. This was convergence, not a retreat from the critic's original position.
- The proposer's round-2 concession added no new argument or evidence, but merely reaffirmed the substantively earned round-1 concession. It is not an independent consensus-producing move and should not be counted as new agreement; nor is it capitulation on a still-disputed point.

## Amendments made

No amendment was made to idea 036. At round zero, the idea claimed that a matched output jump at an atlas territory border would show that the final-infarct model uses arterial-territory membership as a spatial prior beyond case evidence. That claim is unchanged on the card but was rejected by both sides because the proposed observation is also produced by case-evidence-driven territorial reasoning.

The proposed out-of-fold border-zone error audit was explicitly separated as a spin-off. It retains part of the medical motivation and asks whether calibration or segmentation errors concentrate near registered atlas borders, but it loses the original internal-map use claim, the regression-discontinuity interpretation, and any claim that atlas knowledge overrides patient-specific evidence.

## Recommendation

REJECT. The proposed positive-result pattern cannot distinguish use of an internal vascular atlas from territorial predictions derived from nonlocal case evidence, so the test does not identify its deliverable claim. The single most important thing for the human to inspect is the agreed revival condition: whether an independently measured patient-specific perfusion-territory cohort that dissociates from the population atlas, or a valid internal-variable intervention, is genuinely obtainable. Absent that new evidence, idea 036 should close; the border-zone error audit should be registered separately through the normal scouting path.

## In plain terms

This idea asks whether a stroke-prediction model carries a textbook map of which arteries supply which brain regions. It proposed testing whether predictions jump at the borders of those mapped regions even when nearby tissue looks similar on the released scans.

The debate concluded that this test cannot answer that question. A model could create the same jumps by reading the patient's own clot and blood-flow evidence, without carrying a textbook map, and the available controls cannot separate those explanations. A simpler study of whether errors cluster near vascular borders may still be useful, but it is a different idea.

The human is being asked only whether new, independent patient-specific vascular-territory evidence or a valid intervention is actually obtainable; without it, the original idea should be rejected.

```json
{"verdict":"KILL","kill_code":"IDENTIFIABILITY_FAILURE","unblock":"Obtain held-out audited-model predictions on a cohort with independently measured patient-specific perfusion territories that dissociate from the population atlas, or validate an intervention on the internal territory variable that holds case evidence fixed."}
```
