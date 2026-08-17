# Debate summary — idea 025

## Agreed

- The released ISLES'24 CTP series were already processed by a closed icobrain cva co-registration and temporal-resampling pipeline, and the release provides neither the original frames nor retained correction transforms or motion grades (round 1; accepted throughout).
- A post-correction temporal-inconsistency statistic can be computed without annotation, but a nonzero statistic alone does not establish that it represents patient movement or restlessness (round 1; proposer accepted the attribution gap and proposed an external bridge).
- Correction artifacts can be downstream traces of movement, and successful correction can attenuate a genuine motion signal; nevertheless, other causes of post-correction inconsistency remain possible and must be separated before making the behavioral claim (rounds 1–2).
- A same- or demonstrably equivalent-pipeline validation bridge would require paired pre-correction and corrected CTP plus motion ground truth, and would need to show both recovery of patient-motion rank and realistic reproduction of the motion-to-residue mapping (rounds 1–2).
- The proposed UniToBrain multi-pipeline bridge cannot establish how the untested closed icobrain cva 1.5.0 pipeline maps real motion into the released ISLES'24 residue (round 2; proposer conceded this point).
- The NIHSS, age, and onset-to-scan fingerprint is converging association rather than a causal bridge, because referral pathway, workflow, treatment selection, stroke subtype, and site can also generate that pattern (round 2; proposer conceded).
- Narrowing the deliverable to “the model uses a bolus-independent post-correction temporal-inconsistency signature” would change the claim's identity. It must therefore be a separately registered successor with idea 025 as parent, not a revision in place (rounds 1–2).
- The Stage-0 inconsistency census remains useful as a QC characterization and reusable covariate, but it is not deliverable-bearing evidence for the original actigraphy claim (rounds 1–2).

## Unresolved

### Is skull-anchored registration on uncorrected CTP an adequate independent measure of acquisition-level patient motion?

- **Proposer:** Yes, within measurable error. Displacement of the contrast-invariant skull in uncorrected frames measures head-in-scanner motion up to recorded table travel and a registration noise floor that can be bounded by synthetic recovery; prior CTP and fMRI motion studies use this instrument class.
- **Critic:** Not as the independent ground truth needed for this bridge. Agreement between related image-derived pre- and post-correction estimators may share anatomy-dependent registration error, table motion, or reconstruction artifacts.
- **Evidence that would settle it:** A validation cohort comparing skull-anchored estimates with independent external tracking, scanner or correction transforms validated against external tracking, or blinded acquisition-level motion grades with prespecified rank-recovery accuracy. This disagreement is empirical, but it no longer controls the recommendation because both sides agree that the unmatched closed icobrain pipeline is independently fatal to the current design.

## Positions that moved

- **Proposer, round 1:** Accepted the critic's claim that the original design lacked a causal bridge from post-correction inconsistency to patient behavior. In response, the proposer amended the design to require validation on uncorrected UniToBrain CTP across several correction pipelines before any ISLES'24 model work. This was an earned amendment prompted by the critic's specific attribution objection.
- **Proposer, round 2:** Conceded that multi-pipeline robustness on investigator-chosen implementations cannot bound the behavior of icobrain cva 1.5.0, the closed treatment that produced the ISLES'24 data. The proposer also conceded that the clinical-covariate fingerprint is association only. These concessions followed the critic's new, specific argument about treatment-pipeline mismatch and were not unearned.
- **Critic, round 2:** Explicitly accepted that the UniToBrain amendment preserved the original question's identity, even while rejecting it as an adequate identification bridge.

## Amendments made

At round zero, the idea claimed that a raw-CTP model could be tested for use of residual **patient head motion as behavior** by measuring FD-like residue in corrected ISLES'24 series and injecting synthetic motion followed by a standard correction step.

The round-1 amendment would have added a mandatory external Stage 0b: inspect UniToBrain for uncorrected CTP, estimate acquisition motion, process cases through several open rigid-correction and resampling pipelines, require robust recovery of original-motion rank, characterize kinetic false residue, and require synthetic edits to match the empirical motion-to-residue relationship. It also demoted the clinical fingerprint to supporting evidence and made failure of the bridge a pause condition.

After round 2, that amendment is not considered sufficient. The current original candidate retains its behavioral deliverable sentence but is paused because no obtainable evidence connects residue from the specific closed icobrain pipeline to patient movement. It does not narrow its claim in place.

What is lost is the actigraphy interpretation, including restlessness as a severity cue and the proposed sedation or intubation harm. A proposed successor may retain only the measurable index-level claim: that a model uses a bolus-independent post-correction temporal-inconsistency signature. The bone-anchored/off-bolus instrument, null-instrument and recovery checks, and Stage-0 census can transfer to that successor, which must re-enter through normal scouting.

## Recommendation

**PAUSE.** The single most important thing for the human to inspect is whether paired pre-correction and icobrain cva 1.5.0-corrected CTP, with independent motion ground truth or retained validated transforms, can be obtained for a representative cohort. Without that bridge, the original behavioral attribution is not identifiable; the index-level audit is a distinct successor rather than a repair.

```json
{"verdict": "PAUSE", "unblock": "Obtain paired pre-correction and icobrain cva 1.5.0-corrected CTP (or a source-verified bit-equivalent pipeline) with independent motion ground truth or retained validated transforms, and verify patient-motion rank recovery plus the real motion-to-residue mapping."}
```
