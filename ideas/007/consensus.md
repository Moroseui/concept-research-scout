# Debate summary — idea 007

## Agreed

- The paired inhale/exhale breath-hold comparison is worthwhile and remains the primary estimand: measure how CT-CLIP finding scores change within the same patient and session as measured total lung volume changes (rounds 1–6).
- The ten 4DCT phases are not ten calibrated inflation levels and cannot serve as a mechanism-identifying dose response. Phase-binned 4DCT also introduces a different reconstruction process and phase-sorting artifacts (proposer conceded in round 2; reaffirmed in round 4).
- The study cannot identify parenchymal attenuation, vessel crowding, diaphragm position, or another individual image channel as the cue. Mean lung attenuation must not remain a co-primary, independently identified mechanism (rounds 2–5).
- A state-level X is acceptable here: “degree of inspiration,” measured by total lung volume in litres, bundles the anatomical and attenuation changes caused by lung inflation. On that definition, the paired acquisition estimates the total effect of a named physiological state rather than a specific voxel channel (proposed in round 4; accepted by the critic in round 5).
- The revised deliverable is: *The model is using degree of inspiration — the lung's inflation state, measured as total lung volume in litres — as a component of its emphysema, atelectasis and lung opacity scores.* This claim remains conditional on Stage 0 and the eventual results (rounds 4–6).
- The matched-volume opposite-limb 4DCT arm cannot bound full-excursion anatomical nuisance effects. At most it may provide an exploratory score-jitter floor at approximately equal lung volume; it is not an identification control (rounds 3–4).
- Mosaic attenuation must be removed because CT-CLIP has no such output head. The claim that a score shift means a patient receives a different diagnosis must also be removed (round 2, carried through round 4).
- A common scanner-coordinate crop does not by itself establish comparable model inputs. Comparable physical framing must be verified after the complete pinned preprocessing pipeline, including retained coverage, scale, crop, padding, and boundary contact (rounds 2, 5, and 6).
- The real keystone is that a prespecified sufficient number of actual inhale/exhale pairs are reconstruction-matched and yield comparable physical framing after the complete pinned CT-CLIP preprocessing. Its status is `NOT_INSPECTED`, so feasibility and novelty confidence remain capped at 3 (rounds 5–6).
- Stage 0 is a genuine go/no-go. The usable-pair threshold and tolerances must be fixed before model scores are computed (rounds 5–6).
- NBIA index inspection provides strong but incomplete evidence: all 20 patients have nominal 2.0 mm B70f inhale and exhale series; 18 are currently clean candidates, patient 05 has unequal slice counts, and patient 04 has different StudyInstanceUIDs. These index fields do not replace DICOM-tag or preprocessed-tensor inspection (round 6).
- B70f is a sharp-kernel distribution shift relative to the soft-to-medium CT-RATE reconstruction families already inspected. Because both arms share it, it need not bias the paired contrast, but it limits external validity to sharp-kernel radiotherapy-planning CT unless replicated (round 6).
- The respiratory-state audit is the conditional fallback of this candidate, not a separate candidate or spin-off (rounds 2, 4, and 5).

## Unresolved

There is no remaining stated disagreement between proposer and critic; the debate converged in round 6. The following empirical questions remain open and must not be mistaken for consensus that their answers are favorable.

### Do enough actual pairs pass the reconstruction and framing gate?

- **Proposer's position:** The keystone is `NOT_INSPECTED`; NBIA index evidence suggests 18 clean candidate pairs and two flagged pairs, but full DICOM and tensor inspection is still required.
- **Critic's position:** Same. Collection- and index-level evidence cannot establish reconstruction matching, coordinate consistency, or comparable inputs after pinned preprocessing.
- **What evidence would settle it:** Download and inspect every candidate pair. Before inspection, specify the minimum usable-pair count and tolerances for convolution kernel, slice thickness and increment, reconstruction diameter, contrast status, FrameOfReferenceUID, ImagePositionPatient, retained superior/inferior landmarks, physical scale, crop loss, padding fraction, lung boundary contact, and state-dependent resizing/cropping. Inspect the final preprocessed tensors as well as DICOM headers.

### Is a common physical box compatible with CT-CLIP preprocessing without state-dependent framing?

- **Proposer's position:** It is a Stage 0 hypothesis, not an eliminated confound. Expiratory scans may contain a different lung-voxel fraction and may be padded differently.
- **Critic's position:** Same; a common upstream box guarantees nothing if downstream preprocessing adapts crop, resize, or padding to anatomy.
- **What evidence would settle it:** Side-by-side quantitative inspection of physical scale, landmarks, padding, boundary contact, lung-voxel fraction, and retained coverage in the final model tensors for every retained pair, using prespecified tolerances.

### Is the optional matched-volume 4DCT jitter floor usable?

- **Proposer's position:** It can be used only to ask whether breath-hold score movement exceeds score movement when measured inflation barely changes; it cannot identify a channel or bound anatomical nuisance effects.
- **Critic's position:** The critic did not explicitly accept or reject this narrower role after round 4. Earlier objections establish that artifacts may make the arm noisy or uninformative.
- **What evidence would settle it:** Prespecify the volume-matching tolerance and jitter statistic, then inspect whether enough opposite-limb pairs exist with adequate reconstruction quality. If phase artifacts or heterogeneous changes make the reference unstable, delete the arm; its failure must not alter the primary paired audit.

## Positions that moved

- **Proposer, round 2:** Conceded in response to the critic's identifiability argument that 4DCT phase is not a calibrated dose response; volume and mean HU cannot be treated as two independently identified cues; and fixed-tensor crop/scale is a real differential.
- **Proposer, round 2:** Removed mosaic attenuation, the “different diagnosis” claim, and the ten-point slope; reduced claimed identifiability from 5 to 4. These were earned responses to the critic's endpoint and mechanism objections.
- **Critic, round 3:** Accepted that the round-2 amendment passed the identity check and still addressed the original question, although the critic rejected the proposed hysteresis control as identifying. This withdrew the round-1 demand for a separate candidate.
- **Proposer, round 4:** Conceded in response to the scale-mismatch and reconstruction arguments that the hysteresis arm identifies nothing and cannot extrapolate from millimetric hysteresis to full respiratory excursion. It was demoted to an optional jitter floor.
- **Proposer, round 4:** Withdrew the channel-level parenchymal-air-fraction claim and redefined X as the clinically named bundled physiological state “degree of inspiration,” measured by lung volume. Air fraction became interpretation only.
- **Critic, round 5:** Accepted the state-level X and the resulting total-effect interpretation. The critic agreed that the narrowed question retained the candidate's identity and did not require a spin-off.
- **Proposer, round 6:** Conceded the critic's wrong-keystone objection. The keystone changed from collection-level pair existence to sufficient actual pairs with matched reconstruction and comparable final model framing; status changed to `NOT_INSPECTED`, restoring the score caps and making Stage 0 a go/no-go.
- No concession was unearned. Each movement answered a new or sharpened argument, and the final concession included new index-level evidence without treating it as resolution of the keystone.

## Amendments made

At round zero, the idea claimed that CT-CLIP used total lung volume and mean parenchymal attenuation as co-primary cues for emphysema, mosaic attenuation, atelectasis, and lung opacity; that ten 4DCT phases identified a within-patient dose response; and that breath-hold differences could give a patient a different diagnosis. It asserted rung 3, identifiability 5, an `INSPECTED_TRUE` keystone, feasibility 4, and novelty confidence 4.

The converged idea claims only a state-level X: degree of inspiration, measured as total lung volume in litres, as a component of emphysema, atelectasis, and lung-opacity scores. The breath-hold pair is primary. Individual visual channels are not identified; mean HU and LAA%-950 are explanatory or magnitude context only. The 4DCT series is optional and exploratory, with matched-volume pairs serving at most as a jitter floor. Mosaic attenuation, ten-phase dose-response identification, “different diagnosis,” and any shared-mechanism robustness comparison with LAA%-950 are lost.

The idea is conditional rather than ready: the keystone is `NOT_INSPECTED`; feasibility and novelty confidence are capped at 3; identical framing is a testable Stage 0 hypothesis; and external validity is limited by sharp B70f reconstruction and the radiotherapy-planning population. The existing `idea_card.json` has not yet been updated to reflect these amendments.

## Recommendation

**REVISE.** Update the idea card to the converged state-level claim and corrected scores, then require Stage 0 before a probe contract. The single most important thing for the human to inspect is the prespecified DICOM-to-final-tensor comparability gate: whether enough inhale/exhale pairs truly retain matched reconstruction, coordinates, physical scale, and thoracic coverage through the complete pinned CT-CLIP preprocessing pipeline.
