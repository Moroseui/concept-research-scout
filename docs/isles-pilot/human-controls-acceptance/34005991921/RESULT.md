# confer: REVIEWED_PROPOSAL

**Question:** How well does admission Tmax > 6 seconds predict the released follow-up infarct mask in the frozen 99 development cases?

**Evidence:** P001 is a fixed, approved baseline design. The supplied current status states that P001 remains **unexecuted and has no result**: no patient metric, import or interpretation exists. Synthetic workflow demonstrations and archive verification are not scientific results.

**Limitations:** This is exploratory research on previously used development outcomes. Admission hypoperfusion cannot determine treatment-dependent final infarct, and no external or clinical validation is available.

**Next decision:** No scientific decision is supported by a P001 result yet. This discussion grants no execution approval and proposes no follow-up or amendment.

The P001 v1.1 baseline predicts every voxel with admission Tmax strictly greater than 6.0 seconds as infarct, on the full released Tmax grid. It has no training, fitted parameters, erosion, connected-component filtering or lesion-dependent mask. Every Tmax voxel, including background, must be finite; a nonfinite value stops the run. The seconds convention is inherited from the prior implementation and remains a metadata assumption to report.

Inputs must be available by completion of admission CT. Prediction uses only the admission Tmax map in NCCT space. The target is the released binary MRI-derived follow-up infarct mask in NCCT space, after observed treatment. The supplied specification cites MRI timing of 2–9 days. Labels are opened for evaluation only after each prediction mask is written. Follow-up image intensities, outcomes, post-treatment variables and outcome-derived rankings do not enter prediction.

The primary metric is the arithmetic mean of per-patient volumetric Dice, with equal weight for all 99 patients. Dice is twice the overlapping positive volume divided by the sum of predicted and reference positive volumes. Both masks empty scores 1; exactly one empty scores 0. Secondary descriptive metrics are median Dice, mean absolute lesion-volume error in mL and mean signed prediction-volume error. The specified uncertainty estimate uses 2,000 patient bootstrap resamples, seed 20260905, and a central percentile 95% interval for mean Dice. No metric or interval has been measured.

The frozen cohort remains exactly 99 eligible development cases, selected only through the pinned table’s case_id column; its other columns and rankings are discarded. The 49 reserved cases remain excluded from access and evaluation. Original pins remain unchanged:

- Cohort table SHA-256: `aba525122f796618761e6c4d29b664647760e8dff4987932c3ff6ab5456faae9`.
- Archive member manifest git blob: `edb9a8c2ceb90df214cdd7ec167f0b1e8c858bb2`.
- Archive identity: 99,014,629,647 bytes; MD5 `36ae28b9a17f7340b8bbef62b595cb57`.
- Original snapshot: `0770c7dcabe781cbfb87de505755e7aafa758f2e`.
- Scientific source: `d6a1184b4378e849213fd887a6f7b103fb1a64d5`.
- Notebook commit: `1a81c037343598f4e4585153b11d761b87a9ae3a`.

The planned evaluation requires matching shape and affine, finite 3D arrays, binary labels and positive voxel volume. Geometry disagreement stops evaluation; no post hoc resampling or additional case exclusion is authorized. The existing budget remains one CPU Colab run with at most 60 analysis minutes, with archive verification and extraction separately receipted.

Follow-up infarct is a delayed imaging surrogate, not histological truth or untreated counterfactual infarct. Reperfusion and subsequent care are unmodeled. Hypoperfusion may include tissue that survives; small lesions and registration error may depress Dice. Cohort selection, prior outcome use, scanner/site differences and acquisition/reconstruction variability limit generalization. The bootstrap interval would describe only resampling variability within these selected development cases; it would not resolve these limitations or establish causal, biological or clinical claims.

The specification’s historical pending-review wording is distinguished from the current status, which records preserved reviewed scientific source and notebook. Neither constitutes execution evidence: the dispatch worker refused before Colab tools, and the coordinator remains blocked with zero retries and an open ambiguity inbox. This document is a bounded explanatory discussion based solely on supplied evidence, not an approval, executable amendment or human ratification.


## Independent system review
APPROVE: The discussion satisfies the request and stays within bounds. It leads with a readable result card (question, evidence, limitations, next decision) and plainly states that P001 remains unexecuted with no patient metric, import or interpretation, matching CURRENT_STATUS.md. The baseline is described faithfully to SPEC.md v1.1 and run.py: a fixed threshold predicting voxels with admission Tmax strictly greater than 6.0 seconds on the full released grid, no fitting, erosion, connected-component filtering or lesion-dependent mask, with the fail-on-nonfinite input rule and the inherited seconds-unit metadata assumption noted. Admission-only input timing, the MRI-derived follow-up infarct target in NCCT space (2–9 day surrogate, post-treatment), and label opening only after predictions are written are all stated correctly. The primary metric (arithmetic mean of per-patient volumetric Dice with the empty-mask conventions), the secondary descriptive metrics, and the bootstrap plan (2,000 resamples, seed 20260905, central percentile 95% interval) match the specification, and no value is invented or measured. Exploratory limitations mirror the campaign and specification: reused development outcomes, selected 99-case cohort with 49 reserved cases excluded, unmodeled treatment/reperfusion, registration and unit caveats, and no external, causal, biological or clinical claim. All original experiment pins are preserved verbatim: cohort table SHA-256 aba525122f796618761e6c4d29b664647760e8dff4987932c3ff6ab5456faae9, member-manifest blob edb9a8c2ceb90df214cdd7ec167f0b1e8c858bb2, archive size 99,014,629,647 bytes with MD5 36ae28b9a17f7340b8bbef62b595cb57, snapshot 0770c7dcabe781cbfb87de505755e7aafa758f2e, scientific source d6a1184b4378e849213fd887a6f7b103fb1a64d5, and notebook commit 1a81c037343598f4e4585153b11d761b87a9ae3a. It proposes no follow-up or amendment, grants no execution approval, manufactures no human ratification or review status (it correctly distinguishes the specification's pending-review wording from the preserved-review note in current status), and contains no patient data, fabricated literature or measurements. This review approves the discussion text only; it does not ratify, authorize execution, or amend any specification.

**Next action:** Review this proposal. Adoption, experiment execution and human ratification are separate gates.

Source: `9117de5e56b824e9bf03e7239518abfecc7a8b16`. Request: `5dc329b3a014cef063f0058793420717c6c79d5efbabd746222977a638b77380`.
