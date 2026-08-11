# fiction_pitch

## Claimed finding

Analysis of NLST baseline low-dose chest CT shows that the aortic-calcification head of CT-CLIP does not score calcification from the aorta when applied to whole volumes: occluding the aorta changes the score negligibly (0.91 to 0.89), while occluding the dome of the left hemidiaphragm collapses it (to 0.12), and the score rises monotonically as the diaphragm dome is synthetically translated upward. The volume-level score is dominated by inspiratory depth: deeper inspiration drags the aorta caudally and smears calcium across more axial slices, so the head functions as two fused detectors — a per-slice detector that genuinely reads plaque, and a cross-slice detector that reads breath-hold depth. Averaged over a volume, the breath signal drowns the plaque signal and inverts its sign: in 1,912 NLST participants with seven-year vital status, the slice-wise mean score predicts mortality as calcification should (adjusted hazard ratio 1.58 per standard deviation) while the whole-volume score is protective (adjusted hazard ratio 0.74), and the residual between the two scores correlates with diaphragm excursion at r = 0.81. In longitudinal follow-up, participants whose excursion shrinks between screening rounds show volume scores drifting toward "clean" even as thresholded calcium grows. This inversion is present in every published validation of the model, because validations score whole volumes and never slices.

## Materials

- NLST (National Lung Screening Trial) low-dose chest CT, accessed via the IDC (Imaging Data Commons) buckets.
- Cohort: 1,912 NLST participants with baseline low-dose CT and seven-year vital status; second screening round (T1) scans from the same participants, one year later, for longitudinal comparison.
- Model: CT-CLIP, specifically its aortic-calcification head, run in two modes:
  - Whole-volume score: the head applied to the full thorax.
  - Slice-wise mean score: the head applied independently to 3-millimeter axial sections, scores averaged.
- Ground-truth calcium measure: an Agatston-style threshold — count of voxels over 130 Hounsfield units inside a hand-tuned aortic mask — computed with no model involvement.
- Diaphragm excursion proxy: apex-to-dome distance (lung apex to left hemidiaphragm dome), computed with ITK.
- Residual score: whole-volume score minus slice-wise mean score, per patient.
- Occlusion/perturbation tooling: cylindrical air-density masking of anatomical structures (aorta, heart, spine, left hemidiaphragm dome) and synthetic translation of the diaphragm dome in 2-millimeter increments with all other content frozen; demonstrated on NLST participant 108644.
- Statistical model: Cox proportional-hazards regression adjusted for age, sex, pack-years, and the classical (thresholded) calcium score.

## Verification procedure

1. On a single case (NLST participant 108644), mask the descending aorta with air density and re-score with the CT-CLIP aortic-calcification head; the score moves from 0.91 to 0.89. Mask other structures one at a time — heart and spine produce no change; masking the left hemidiaphragm dome drops the score to 0.12.
2. Synthetically translate the diaphragm dome up and down in 2-millimeter increments, holding everything else frozen, and re-score at each position. Confirmation: the calcification score rises monotonically as the dome rises.
3. Compare previously computed slice-wise scores (3-millimeter axial sections scored independently and averaged) against whole-volume scores on the same patients. Observation taken forward: the disagreement is systematic, not noisy — patients called positive by the volume score are called clean by the slice-wise mean.
4. Assemble the cohort: 1,912 NLST participants with baseline low-dose CT and seven-year vital status from the IDC buckets.
5. Compute ground truth per patient with the model-free Agatston-style threshold (voxels over 130 Hounsfield units inside a hand-tuned aortic mask).
6. Compute three quantities per patient: the CT-CLIP whole-volume score, the mean of its slice-wise scores, and diaphragm excursion proxied as apex-to-dome distance.
7. Fit Cox regressions for seven-year mortality, adjusted for age, sex, pack-years, and the classical calcium score. Confirmation: the slice-wise mean has hazard ratio 1.58 per standard deviation with a confidence interval well clear of one, while the whole-volume score on the same patients and covariates has hazard ratio 0.74 (protective).
8. Compute the residual (volume score minus slice-wise mean) and correlate it with apex-to-dome distance. Confirmation: r = 0.81, with the scatter of residual against excursion lying along a straight line across all 1,912 points.
9. Repeat scoring on the second screening round (T1) in the same patients. Confirmation: participants whose apex-to-dome excursion shrank between rounds show volume scores drifting toward "clean" even as their thresholded calcium grows.
