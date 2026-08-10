# Revision of idea 007

## Outcome

The idea is now one conditional, label-free question: after proving that the paired scans remain physically comparable through CT-CLIP's complete preprocessing, does the emphysema score change between inspiratory and expiratory breath-hold CT from the same patient as measured lung volume changes?

No code was written. The next action is Stage 0 inspection, not model inference.

## Material changes

1. **Narrowed the confirmatory question to one head and one acquired contrast.** Emphysema is the sole confirmatory head. Atelectasis and lung opacity are ordered secondary outcomes; all other heads are exploratory. This removes the previous multi-head architecture from the primary claim.

2. **Replaced the channel-level claim with the debate's agreed state-level X.** X is now *degree of inspiration*, measured as total lung volume in litres. Mean lung attenuation and LAA%-950 are descriptive context only. The card no longer claims to distinguish attenuation, vessel crowding, diaphragm position, dependent opacity, or another visual channel.

3. **Removed unsupported outputs and consequences.** Mosaic attenuation was deleted because CT-CLIP has no such ClassFine head. The statement that a patient would receive a different diagnosis was deleted because score movement is not a validated diagnostic decision or threshold crossing.

4. **Demoted the current claim from rung 3 to rung 1.** The deliverable sentence remains the prospective rung-3 target, explicitly conditional on Stage 0 and the result. The present evidence supports only a design capable of testing sensitivity to signal changing with respiratory state; it does not establish that the model uses X.

5. **Corrected the keystone and its status.** The former keystone verified the adjacent fact that paired acquisitions exist. The real keystone is that enough actual pairs have matched reconstruction and comparable coordinates, physical scale, thoracic coverage, crop loss, and padding at the *final model tensor*. Its status is now `NOT_INSPECTED`, so feasibility and novelty confidence are capped at 3.

6. **Made Stage 0 a prospective go/no-go.** The minimum usable-pair count and numeric tolerances must be frozen before any CT-CLIP score is computed. Stage 0 inspects DICOM reconstruction and geometry, final-tensor framing, and automatic lung-mask usability. Failure stops the experiment and is reported as a feasibility result, not reinterpreted as a biological null.

7. **Removed the 4DCT dose-response argument.** Respiratory phase is not a calibrated inflation level, and phase-binned reconstruction artifacts prevent mechanism identification. Optional matched-volume phase comparisons are retained only as exploratory jitter description and may be dropped without changing the primary study.

8. **Removed claims that controls identify the mechanism.** Calcification or other heads cannot prove emphysema-head specificity. The all-head panel can reveal broad instability but is exploratory; absence of movement in other heads does not identify the cue.

9. **Rewrote confound handling without claiming elimination prematurely.** Same-patient, same-session acquisition controls scanner, site, habitus, prevalence, referral pathway, and label leakage. Reconstruction, positioning, and preprocessing framing are now direct Stage 0 checks. The shared B70f sharp kernel is recognized as a distribution shift that limits external validity even if it does not alone explain a paired direction.

10. **Added explicit alternative explanations and their status.** The revised card separately treats preprocessing framing, DICOM mismatch, general score jitter, and constituent respiratory manifestations. It states which are prospectively testable, which are only reduced, and why constituent manifestations cannot support a channel-level claim.

11. **Preserved a meaningful negative outcome.** A simple failure to reject zero remains sensitivity-limited. A confidence interval wholly inside a preregistered, justified emphysema-logit equivalence band is a decisive negative for a material paired effect in this B70f cohort. Stage 0 failure is a feasibility finding, not an invariance result.

12. **Corrected novelty language.** The card no longer claims novelty. It records the exact delta from the closest inspected work and requires a final primary-source overlap search before describing the result as previously unreported.

13. **Updated scores and arithmetic.** Identifiability fell from 5 to 3; medical relevance from 5 to 4; feasibility from 4 to the keystone-capped 3; data readiness from 5 to 4; and novelty confidence from 4 to the capped 3. Negative-result value remains 3 because a prespecified equivalence test can be decisive. The recalculated priority score is 3.50.

## What did not change

- The experiment remains label-free and uses an independently computable X.
- The primary comparison remains within patient, within session, and between real acquired images.
- No synthetic image intervention, human annotation campaign, model training, or test-set tuning is proposed.
- The available TCIA pair remains promising: NBIA index inspection suggests 18 clean candidates and two flagged pairs, but this is not treated as resolution of the keystone.

## Next decision

Advance only to Stage 0. A feasibility memo and probe contract should follow only if the prespecified DICOM-to-final-tensor comparability gate passes. Explicit human approval is still required before any probe code is written.
