FATAL OBJECTION: The proposed experiment has no identified NCCT-consuming final-infarct checkpoint, and the released winning ISLES'24 pipeline cannot see dural-sinus HU; even a positive response in a newly trained model would identify use of edited sinus intensity, not use of an oxygen-carrying-capacity proxy.
EVIDENCE: Ren et al., arXiv:2505.18424v2, Methods 3.2–3.3 and Table 1; KurtLabUW/ISLES2024 `inference.py` lines 121–124 at commit `bb6c00c8a58cb57a5a33c133c02885776673d230`; Black et al., DOI 10.3174/ajnr.A2504.
REPAIRABLE WITHOUT CHANGING THE QUESTION? NO
DECISION: REJECT

# Adversarial critique

## 1. The target model does not presently exist in the card

The card moves among “an ISLES'24 model,” “the final-infarct model,” and a model that apparently remains to be trained. Those are not interchangeable experimental objects.

The most relevant released high-performing reference is actively incompatible with the proposed intervention. The winning-method paper says that an NCCT-derived SynthStrip mask was applied to the co-registered scans (Methods 3.2), thereby removing the superior sagittal and straight sinuses from the model field. More decisively, Table 1 enumerates the final model inputs as CTA, CBF, CBV, MTT, and Tmax; it does not include NCCT. The released inference program is narrower still: at repository commit `bb6c00c8a58cb57a5a33c133c02885776673d230`, lines 121–124 construct the four inference channels from preprocessed CBF, CBV, MTT, and Tmax. A Google Drive weights link exists in `model weights.txt`, but those weights do not turn this into an NCCT model. These are **verified facts** from the primary method paper and official implementation.

The public PrediCTP implementation (Amador et al., arXiv:2509.24420; official repository `kimberly-amador/ISLES24-PrediCTP`) consumes native 4D CTP rather than NCCT and reports Dice 0.20. It is not an easier target for a sinus-HU intervention. I found no primary source establishing an obtainable, validated ISLES'24 final-infarct checkpoint that ingests unmasked quantitative NCCT. That search result is not proof that none exists, but it invalidates the card's “three to five days after model training” presentation as data/model readiness. Training, selecting, and validating a new NCCT-inclusive model is the main study, not a preliminary chore; selection on the same 149 cases would also threaten an honest held-out intervention test.

The required repair is therefore: first obtain or preregister and train a quantitatively faithful, unmasked-NCCT model; freeze patient-level training/development/test splits before choosing it; demonstrate non-trivial held-out final-infarct performance and incremental NCCT use over otherwise identical CTP/CTA/clinical inputs; and only then test sinus edits on the untouched subset. This repairs feasibility but still does not repair the card's physiological question.

## 2. The intervention cannot identify the claimed meaning

Black et al. measured the torcular HU in 166 unenhanced head CT examinations and found correlation with contemporaneous hematocrit and hemoglobin (AJNR 2011; DOI 10.3174/ajnr.A2504; PMID 21566009). That is good prior legwork for a **measurement association**. It does not establish that a network's response to synthetic sinus intensities means the network represents hematocrit, anemia, arterial oxygen content, or oxygen delivery.

A signed response to editing only the sinus would establish, at best, causal sensitivity to that edited image region under that editor. The same response is compatible with learned site/protocol cues, reconstruction-kernel cues, partial-volume/skull-edge cues, global intensity calibration, or an anatomically remote brightness feature. Within-case editing fixes the case's acquisition but does not remove acquisition information encoded in the edited value. Site stratification and noise normalization test stability, not semantics. Equal-volume skull and extracranial-vein shams do not exhaust these alternatives because neither sham matches the sinus's location, boundary geometry, tissue interfaces, or training correlation structure.

The card itself recognizes this by declaring target rung 1 to be “use of sinus attenuation, not a claim of measured anemia.” But its question asks whether the model uses attenuation “as an image proxy for hematocrit and therefore oxygen-carrying capacity,” and its deliverable sentence asserts exactly that interpretation. This is an internal claim-identity failure. Narrowing the deliverable to “the model is sensitive to dural-sinus intensity” removes the oxygen-gauge question that makes the candidate interesting; under the program's claim-identity rule, that is a successor, not a revision.

Even measured hematocrit in an external cohort would calibrate the image measure, not reveal the ISLES model's interpretation. Physiologically, oxygen delivery depends on flow and arterial oxygen content; arterial oxygen content depends mainly on hemoglobin concentration and oxygen saturation, not hematocrit alone. The card's technical mechanism partially conditions this (“at the same CBF”), but neither the planned experiment nor the ISLES labels isolate that pathway from reperfusion, collateral state, treatment, time, and the many other determinants of final infarct.

## 3. The proposed edit is underspecified and likely out of distribution

“Replace only dural-sinus voxels with intensity-matched surrounding blood values” is not operationally coherent: surrounding the dural sinus is skull, dura, and brain, not a second pool of unenhanced blood. The secondary arterial-HU normalization also risks using small, partially volumed arteries and silently changes the construct from absolute blood attenuation to a venous/arterial ratio.

A constant or rescaled sinus fill changes noise texture, spatial gradients, partial-volume boundaries, and possibly vessel morphology. A three-dose curve can be monotone for an artifact detector. Physiologic-range marginal HU values do not make a conditional edit realistic. A defensible editor would need to preserve the subject's local noise power spectrum, boundary partial volume, and spatial variation, and pass blinded real-versus-edited discrimination or an equivalence gate. Those additions are not excessive compute, but they are essential construct-validity work absent from the card.

The automatic sinus segmentation asset is also merely asserted. Atlas transfer on acute, variably positioned, thick-slice NCCT near skull is not the same as a validated sinus-blood segmentation. The one-voxel erosion ICC measures estimator stability, not anatomical accuracy; two consistently misplaced masks can have ICC 1.0. Manual QC would be new annotation burden unless an independently validated public segmenter is identified. The ≥120/149 threshold, site SMD <0.5, and ICC ≥0.9 have no cited power, error, or biological rationale and could reward a stable but invalid measure.

## 4. Endpoint, leakage, and negative-result problems

“Affected-territory prediction changes” is not defined. The final-infarct ground truth is a post-treatment lesion, while the affected territory must be defined without using that future mask if the readout is meant to represent prospective prediction. Defining it from the label leaks outcome geometry into the endpoint; defining it from baseline perfusion requires a frozen threshold and creates a different selection estimand. The card specifies neither voxelwise statistic nor case aggregation, multiplicity handling across doses/regions, minimum effect, or whether accuracy must remain valid after editing.

A positive output delta need not improve or harm Dice, lesion-wise F1, absolute volume difference, or lesion-count difference—the official ISLES'24 measures in the organizers' repository. Thus the medical consequence is weak: output motion alone can be arbitrary sensitivity. Conversely, a negative remains weak even with theoretical receptive-field coverage. A nominal receptive field is not evidence of effective sensitivity, and failure could reflect model non-use, insufficient natural HU variation, weak NCCT contribution, editor invalidity, or low power. A positive control that merely alters a known salient input verifies the inference pipeline, not sensitivity to subtle remote blood-HU information. The card correctly scores negative-result value only 2, but its prose overstates the value of a gated null.

There is no concept-label circularity in the narrow sense: the follow-up infarct label was not generated from sinus HU. There is, however, semantic circularity in calling the manipulated scalar an “oxygen gauge” because the interpretation comes from the motivating association rather than an independent model-level measurement.

## 5. Prior-work and novelty position

The blood-HU/hematocrit relationship is established prior work, not a new result (Black et al., DOI 10.3174/ajnr.A2504). The official challenge paper and repository establish the dataset and evaluation setup (de la Rosa et al., arXiv:2408.10966; `https://github.com/ezequieldlrosa/isles24`). The winning pipeline and its strong preprocessing dependence are also published (Ren et al., arXiv:2505.18424v2). I did not find a primary paper that performs this exact model-use test in final-infarct prediction, but absence from a bounded search is not novelty evidence. More importantly, the unfilled gap is not yet a sound question because the experiment cannot distinguish proxy semantics from regional intensity use.

## 6. Plain-pitch fidelity

**Named defect: the pitch preserves the anemia disclaimer but drops two load-bearing qualifications.** “Their concentration affects how much oxygen reaches threatened brain tissue” omits the technical card's same-CBF condition and oxygen-saturation dependence. “A true result” then describes a graded lesion-prediction response as evidence for the “oxygen gauge,” although the rung statement concedes that such a response establishes only use of sinus attenuation. The pitch is therefore more physiological and more certain than the proposed evidence permits. A faithful version would say that red-cell concentration is associated with unenhanced blood HU and contributes to oxygen content, while a model response would show only sensitivity to edited sinus intensity unless independently validated.

## 7. Low-hanging fruit

There is no low-hanging-fruit formulation that preserves the original medical claim. Existing ingredients are individually ready—the 149 public training cases, official evaluation code, winner preprocessing/inference code, linked winner weights, and the published torcular-HU formula—but the available winner removes or never consumes the signal of interest. Measuring the ISLES sinus-HU distribution is a cheap dataset-quality audit, yet without laboratory hematocrit it cannot answer whether HU ranks the biological variable in this cohort, and by itself it is not a high-value medical-imaging-AI study.

The technically easiest model experiment would compare a frozen NCCT-inclusive model's outputs before and after texture-preserving sinus edits. No such validated frozen model was verified, and the result would only be a shortcut/sensitivity audit. The card explicitly says that version becomes uninteresting if the hematology link is dropped; I agree. It should not be kept alive merely because it is computable.

## Constructive alternative

The scientifically meaningful nearby study requires a different cohort: test whether measured admission hemoglobin (plus oxygen saturation) adds held-out predictive information for final infarct conditional on perfusion, treatment/reperfusion, and time, then test whether NCCT sinus HU mediates or substitutes for that laboratory signal. This directly evaluates the oxygen-delivery hypothesis and gives a negative result interpretable meaning. It needs patient-level labs and adequate multivariable support that have not been verified in ISLES'24, so ISLES'24 would no longer be load-bearing; it must be a separate candidate only after a suitable cohort is identified. That is harder, but it is worth doing in a sufficiently powered treatment-characterized cohort because it separates physiology from image shortcut.

NEAREST DEFENSIBLE HIGH-VALUE QUESTION: In a treatment-characterized acute-stroke cohort with admission hemoglobin, oxygen saturation, baseline perfusion, and final infarct, does measured oxygen-carrying capacity add held-out predictive information, and can quantitative NCCT sinus HU substitute for it without loss of calibration?
RETAINS ORIGINAL MEDICAL MOTIVATION? YES
SHOULD IT BECOME A SEPARATE CANDIDATE? YES
IS IT ACTUALLY WORTH DOING? Yes—if a sufficiently powered cohort with temporally aligned laboratory and reperfusion data is obtainable, because it directly tests the physiology that makes the image feature medically interesting rather than merely demonstrating sensitivity to a bright remote structure.
