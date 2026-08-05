# Debate summary — idea 008

## Agreed

- The same-acquisition reconstruction-pair arm cannot establish that Sybil uses biological emphysema: reconstruction changes the measurement channel while the patient's anatomy is fixed. It belongs in a separate reconstruction-sensitivity candidate, and the original deliverable must lose the claim that Sybil's emphysema readout survives kernel changes (critic round 1; proposer conceded in round 1).
- Removing that reconstruction arm does not replace the original fixed-kernel question. The remaining study still asks whether a fixed Sybil output depends on quantitative emphysema measured on the same scan (proposer round 1; critic accepted the identity check in round 2).
- Decomposing the low-attenuation tail into isolated voxels and spatially coherent clusters is a meaningful differential test of image-noise sensitivity versus coherent low-attenuation morphology (proposer round 1; critic accepted this in round 2).
- “CT-defined emphysema” is a defensible name for the measured exposure. The critic accepted both the PRM point that PRM-defined functional small-airways-disease voxels are above −950 HU on inspiration and the legitimacy of coherent low attenuation as a CT emphysema measurement (critic round 3). This agreement concerns the name and measurement, not whether Sybil uses it.
- A fixed-kernel between-patient association, even after phenotype matching, cannot by itself establish model use under the charter. Sybil may instead use another visible feature correlated with CT emphysema. Such an analysis supports only: “Sybil's score is associated with CT-defined emphysema after matching on measured competitors” (critic round 3; proposer conceded in round 3).
- The round-2 clause claiming that the matched score contrast was “not explained by” image noise, inflation, airway morphology, vascular volume, or nodule burden exceeded what matching could show and is withdrawn (critic round 3; proposer conceded in round 3).
- A use claim requires a within-image perturbation or another source of independent variation, with proper controls. The final proposal therefore makes the observational association a prerequisite and makes a controlled counterfactual edit the confirmatory test (critic's requested evidence in round 3; proposer adopted it in round 3).
- If the edit-validity gate fails—especially if the matched sham changes Sybil's score comparably to emphysema removal—the intervention is void and the claim must fall back to association only (proposer round 3; this implements the critic's round-3 condition).
- The revised candidate is materially harder and slower than the original card claimed. Its keystone remains uninspected, feasibility falls, and the original high regret/“about a week” framing no longer applies (proposer round 3; no contrary critic position remains).

## Unresolved

### Are the local parenchymal substitutions in-distribution for Sybil?

- **Question:** Can coherent <−950 HU clusters be removed or inserted without producing an edit artifact or an anatomically implausible image that independently changes Sybil's score?
- **Proposer's position:** This is unverified and must be a Stage 0 gate. Proposed checks are preservation of competitor summaries within tolerance, an edited-versus-unedited discriminator, and a dose-matched normal-parenchyma sham whose Sybil effect is small relative to the targeted edit. Existing generative nodule-edit work is encouragement, not validation of this operator.
- **Critic's position:** Only a prespecified, validated, in-distribution perturbation with reciprocal insertion, matched shams, and anatomy-preservation checks can support “use.” Without it, only the association statement is licensed.
- **What evidence would settle it:** Direct Stage 0 inspection and validation of the actual operator on held-out scans, using prespecified tolerances and failure rules. A sham effect comparable to the targeted effect settles it negatively for this operator. Passing the listed checks would support proceeding, although the debate did not define numerical tolerances or establish that those diagnostics are sufficient to detect every form of distribution shift.

### Does a score response isolate CT-emphysema geometry from remaining visible correlates?

- **Question:** If Sybil responds directionally to removal and reciprocal insertion, does that identify coherent low-attenuation geometry rather than regional hypoperfusion, vascular changes, or a generic HU/edit response?
- **Proposer's position:** Preserve airway, vessel, nodule, lung-volume, reconstruction, dose, and habitus voxels by identity; add a form-contrast arm comparing coherent clusters with diffuse attenuation change at identical voxel count and HU deficit. This should distinguish spatial form from total density and avoid reproducing the vascular co-signature of hypoperfusion.
- **Critic's position:** The critic requested essentially this class of controlled intervention but did not respond after the detailed four-arm operator was proposed. Therefore adequacy of the precise implementation was not explicitly accepted.
- **What evidence would settle it:** Directionally consistent, dose-responsive removal and reciprocal-insertion effects; a small matched-sham effect; a prespecified coherent-versus-diffuse form contrast; and verified preservation of competing anatomy. Failure of reciprocity, dose response, sham separation, or anatomy preservation would reject the use interpretation. Whether the full positive pattern excludes every correlated texture remains an empirical validation question, not settled by the transcript alone.

### Can the required held-out NLST cohort and covariates actually be recovered?

- **Question:** Do the Ardila/Sybil identifiers join to TCIA series, do the reported split counts reconcile, and is there enough fixed-kernel overlap and public covariate coverage for the prerequisite analysis?
- **Proposer's position:** These are Stage 0 go/no-go checks; `keystone_status` must be `NOT_INSPECTED` until they are performed.
- **Critic's position:** The preceding critique raised these as load-bearing feasibility defects; the debate did not revisit or resolve them.
- **What evidence would settle it:** Parse the actual XLSX, execute the identifier join, reconcile participant/exam/series counts, inspect the public schema, and tabulate eligible fixed-kernel cases and matching overlap. This is directly inspectable.

## Positions that moved

- **Proposer, round 1:** Conceded that reconstruction pairs test measurement-channel sensitivity, not emphysema use, in response to the critic's explanation that biological emphysema is unchanged across reconstructions. This was earned by a specific identifiability argument.
- **Proposer, round 1:** Conceded that pack-year adjustment was inadequate and replaced it with measured competing phenotypes, cluster morphology, matched discordant sets, and a zonal contrast, in response to the critic's list of correlated CT phenotypes. Earned, though the critic later showed that matching still did not identify use.
- **Critic, round 2:** Accepted that removing the reconstruction arm preserves the original fixed-kernel question and that cluster decomposition addresses much isolated-voxel noise. These movements followed the round-1 amendments.
- **Proposer, round 2:** Corrected the scope term to “CT-defined emphysema” and acknowledged regional hypoperfusion and residual patient-level correlation with small-airways disease as surviving alternatives. The critic accepted the terminology and PRM clarification in round 3 but not the use claim.
- **Critic, round 3:** Withdrew the narrower objection that PRM-defined gas-trapping voxels contaminate the inspiratory <−950 HU mask, after the proposer supplied the PRM threshold definition. The critic retained the broader correlated-feature objection.
- **Proposer, round 3:** Conceded that matched observational association does not reach rung 1 and that the “not explained by” clause was contradictory, in response to the critic distinguishing measurement validity from model-use identifiability. Both concessions were earned.
- **Proposer, round 3:** Adopted the critic's requested counterfactual perturbation with removal, dose-matched sham, reciprocal insertion, and preservation checks, and added a coherent-versus-diffuse form contrast. This is a substantive amendment, not capitulation recorded as evidentiary consensus.
- No concession in the transcript appears UNEARNED. The final “CONVERGED” label means agreement on the decision rule; it does not mean the critic validated the newly specified operator, because the critic had no subsequent turn.

## Amendments made

At round zero, the card claimed rung 3 from a fixed-kernel score association plus reconstruction-pair behavior: “Sybil is using emphysema” in a reconstruction-invariant way. It treated LAA%-950 and Perc15 as co-primary, made the radiologist-defined no-visible-future-cancer-nodule subgroup primary, assigned `INSPECTED_TRUE`, and described the work as short and highly feasible.

The final debated version instead claims:

- The reconstruction audit is a separate candidate and contributes no evidence that Sybil uses emphysema.
- “CT-defined emphysema” is operationalized as spatially coherent <−950 HU clusters, with isolated-voxel, cluster-geometry, and zonal measurements used to distinguish noise-like from lesion-like signal.
- The fixed-kernel observational analysis is only a prerequisite and effect-sizing step. Even a positive matched result licenses association, not use.
- The confirmatory use test is a four-arm within-image intervention: graded cluster removal, dose-matched sham replacement, reciprocal insertion, and coherent-versus-diffuse form contrast with equal voxel count and HU deficit.
- Rung 3 is conditional on the intervention passing an edit-validity gate and producing directional, reciprocal, dose-responsive, sham-separated results while competing anatomy remains within tolerance. If the gate fails, the precommitted fallback is the association-only sentence and no rung-1 use claim.
- `keystone_status` is `NOT_INSPECTED`. Split linkage, cohort overlap, and especially edit validity remain go/no-go prerequisites.

What was lost: the reconstruction-invariance clause; the claim that observational matching identifies model use; the assertion that named competitors are excluded merely by matching; the simple, annotation-free threshold-only experiment; the original feasibility, regret, identifiability, and priority scores; and the “about a week” execution estimate. The revised intervention introduces a new idea-006-like out-of-distribution risk and weeks of operator construction and validation.

## Recommendation

**REVISE.** The debate produced a coherent conditional design, but the current `idea_card.json` still describes the superseded reconstruction arm, rung-3 observational logic, `INSPECTED_TRUE` keystone, and obsolete scores. Before deciding whether to advance, the human should look most closely at whether the proposed tissue-for-tissue edit can be validated as in-distribution with a prespecified sham-effect tolerance; that is now the single fact separating a model-use study from an association-only study.
