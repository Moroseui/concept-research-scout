# Revision of idea 008

## Outcome

The idea is now one conditional model-use question: for one frozen Sybil risk horizon, does changing spatially coherent CT-emphysema geometry within the same image move the score beyond matched operation and density controls?

The observational score-emphysema analysis is retained only as a prerequisite for host selection and effect sizing. It cannot establish use. No code was written; the next work is a feasibility memo and a prospective Stage 0 specification.

## Material changes

1. **Narrowed the question to one output, one X, and one causal contrast.** The revised card freezes one Sybil horizon and tests coherent CT-emphysema clusters against paired controls. Cancer mediation, six horizons, reconstruction robustness, subgroup architecture, and broad phenotype-matching claims were removed.

2. **Replaced the superseded reconstruction experiment.** Same-acquisition kernel changes manipulate the measurement channel while biological emphysema remains fixed. They cannot establish emphysema use and now contribute no evidence to this candidate. Any reconstruction-sensitivity audit must remain a separate idea.

3. **Demoted observational association to a prerequisite.** Fixed-kernel association with coherent cluster burden may establish that the experiment has signal and may size the edit, but its only licensed sentence is association after measured conditioning. It is not rung 1 evidence and is not the confirmatory endpoint.

4. **Made the within-image perturbation confirmatory.** The primary estimand is the score response per unit of coherent-cluster burden edited within a host image. Removal and reciprocal insertion must agree directionally and monotonically. This implements the debate's requirement for independent variation in X.

5. **Collapsed the four-arm narrative into one controlled edit family.** The card no longer presents four semi-independent studies. Every targeted coherent edit has two paired controls: a normal-to-normal tissue sham matching operation dose, and a diffuse-density edit matching voxel count and total HU deficit. Reciprocal insertion is the reverse direction of the same intervention, not a separate exploratory architecture.

6. **Preserved a human-legible, independently measurable X.** X is now explicitly *CT-defined emphysema geometry*: spatially coherent lung-parenchyma clusters below -950 HU. It is computed from calibrated voxels and automatic masks without radiologist labels. The card distinguishes this CT measurement from microscopic proof of alveolar destruction.

7. **Corrected the rung.** The previous card claimed rung 3 before running a model-use test. Current rung is now 0. The design can conditionally reach rung 3 only after a valid perturbation establishes rung 1, artifact controls pass the rung-2 gate, and the named CT-emphysema measurement supports the rung-3 sentence.

8. **Replaced the keystone.** Downloadable weights, an automatic emphysema metric, and precedent for nodule editing are adjacent facts. The load-bearing fact is that this exact parenchymal tissue-for-tissue operator can alter X without supplying Sybil an operation signature or changing protected competing anatomy. That fact has not been inspected, so `keystone_status` is `NOT_INSPECTED`.

9. **Made edit validity a prospective stop gate.** Edit doses, donor matching, protected masks, boundary and spectrum tolerances, final-tensor checks, discriminator procedure, sham tolerance, and go/no-go thresholds must be frozen before targeted Sybil effects are examined. A detectable editor signature or material sham effect voids the intervention.

10. **Addressed the idea-006 failure directly without claiming immunity.** Local tissue substitution, reciprocal direction, matched sham, equal-HU form control, and preservation of airway, vessel, nodule, lung-volume, framing, and acquisition signals make this proposal different from deleting the whole patient. It can still die exactly like idea 006 if the edit-validity gate fails; the card now says so explicitly.

11. **Rewrote confound claims at the level the design supports.** Scanner, vendor, site, protocol, reconstruction, positioning, habitus, prevalence, and referral pathway are fixed within a host image. Airway, vessel, and nodule voxels are protected by identity. These controls isolate the declared signal only to the resolution of the editor; segmentation omissions, co-edited texture, and undetected operation signatures remain alternatives.

12. **Removed unsupported clinical and biological conclusions.** The card no longer says emphysema mediates cancer prediction, that Sybil learned a better emphysema measure, that clinicians should use emphysema alongside Sybil, or that score response proves biological reversal of alveolar destruction.

13. **Corrected cohort readiness.** The original `INSPECTED_TRUE` status relied on an unparsed supplementary split and unreconciled cohort counts. The actual identifier join, fixed-kernel overlap, host availability, and dependence on public rather than gated fields are now explicit Stage 0 checks.

14. **Preserved a meaningful negative.** After the validity gate passes, tight bounds excluding the preregistered minimum coherent-versus-sham and coherent-versus-diffuse effects in both removal and insertion are a decisive negative for material use of this X by the tested output. Non-significance, poor overlap, segmentation failure, or an invalid editor is not that negative.

15. **Removed the novelty claim.** The card records the exact delta from inspected close work but makes no claim of novelty until a broader primary-source audit, including conference proceedings, is completed.

16. **Updated scores and priority.** The uninspected editor reduces feasibility to 2 and evaluation readiness to 2. Identifiability is 3 because the controls are strong in design but unvalidated. Novelty confidence is capped at 3. The revised weighted priority score is 3.35, and regret falls from 5 to 3 because this is no longer a week-long threshold analysis.

## What was deliberately removed

- reconstruction-kernel invariance as evidence of biological emphysema use;
- LAA%-950 and Perc15 as co-primary observational endpoints;
- cancer-outcome mediation;
- the radiologist-defined future-cancer-nodule subgroup as a primary population;
- pack-year adjustment as a route to identifiability;
- claims that phenotype matching means alternatives are “not explained by” the data;
- the “FDA-adjacent,” immediate-clinical-interpretation, and one-week framing;
- multi-horizon and exploratory endpoint architecture from the confirmatory question.

## Next decision

Do not proceed to probe code. First produce a reviewed feasibility memo that resolves the held-out NLST join and specifies the edit-validity gate numerically. A probe contract and explicit human approval remain mandatory before any implementation.
