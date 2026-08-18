FATAL OBJECTION: The proposed “coherent triad” edit changes the putative collateral anatomy while freezing its perfusion consequences, so a model response cannot identify use of collateral-supported tissue viability rather than response to cross-modal inconsistency or synthesis artifacts.
EVIDENCE: PMID 25931460 reports ISE together with normal-to-increased CBV and prolonged Tmax; `ideas/027/idea_card.json` instead requires holding Tmax/CBF/CBV fixed while swapping CSF and vessel features.
REPAIRABLE WITHOUT CHANGING THE QUESTION? YES
DECISION: PAUSE

# Adversarial critique — idea 027

## 1. The confirmatory intervention does not instantiate the claimed mechanism

The suspected mechanism is a causal package: robust leptomeningeal filling produces visible engorged vessels, reduced sulcal CSF space, and a characteristic perfusion state while the underlying gray-white junction remains preserved. The primary series did not report the anatomical sign in isolation: all eight ISE cases had CTA-visible engorged/dilated leptomeningeal vessels and CTP with normal-to-increased CBV plus prolonged Tmax (PMID 25931460; DOI `10.1161/STROKEAHA.115.009304`). The later independent series likewise describes ISE as a marker of sufficient collateral status and increased CBV, and reports correlation with the rLMC collateral score (PMID 32912520; DOI `10.1016/j.jstrokecerebrovasdis.2020.105168`). These are verified primary-source facts.

The card proposes to swap sulcal-CSF fraction, pial-vessel occupancy, and preserved gray-white contrast while **holding Tmax/CBF/CBV fixed**. That is not a coherent collateral-engorgement intervention; it deliberately breaks the cross-modal relationship that motivates the claim. This is an identifiability failure, not merely an edit-realism nuisance. A response could be caused by (i) an impossible CTA/perfusion combination, (ii) boundary or texture artifacts from vessel/CSF synthesis, (iii) NCCT–CTA registration inconsistency, or (iv) genuine use of any one edited channel. Coherent-versus-incoherent component controls do not rescue the inference because the “coherent” arm is coherent only within the edited subset, not across the model's full input.

The repair is to design a source-verified intervention that moves the whole observed collateral phenotype—including its supported perfusion covariates—along the empirical joint distribution, or to abandon intervention and ask an association/error-stratification question. The former preserves the original use question but requires a learned conditional generator or natural matched examples plus much stronger validity gates. The latter changes the estimand and should be a separate candidate.

## 2. There is no defined model asset or endpoint

“An ISLES'24 multimodal model” and “the final-infarct model” do not identify a checkpoint, training split, input channels, preprocessing, or scalar response. That omission is load-bearing:

- The published winning system used a residual nnU-Net after SynthStrip and custom windowing (arXiv `2505.18424`). Its published final-input window table lists CTA, CBF, CBV, MTT, and Tmax, while NCCT is described as the source of the brain mask. On that account, gray-white differentiation and sulcal CSF on NCCT are not established model inputs. A model cannot “use” an NCCT sign it never receives.
- I found a public implementation for a 4D-CTP model, ISLES24-PrediCTP, but its reported performance is low (Dice 0.20; lesion-wise F1 0.02) and its input is raw CTP, not the proposed NCCT/CTA triad. It is not a low-hanging substitute for this question.
- The card says “after model training,” so neither a frozen checkpoint nor an untouched evaluation split presently exists. Training a model and developing the construct on all 149 public cases would create leakage. The hidden 96-case test set remains inaccessible except through challenge evaluation, and it cannot support bespoke per-case intervention analysis. The dataset publication verifies 149 public training and 96 hidden test cases (DOI `10.1148/ryai.250603`).
- “Survival-directed output change” is undefined. It could mean local mean infarct probability, predicted surviving volume inside the edited territory, Dice against follow-up mask, or a change in a thresholded segmentation. Those endpoints answer different questions. A paired, continuous, territory-level infarct-probability change is the least lossy candidate, but its sign, territory definition, aggregation, and exclusion of edit boundaries must be preregistered.

This alone warrants PAUSE: before a use claim, the study needs a frozen model that demonstrably consumes NCCT and CTA, non-trivial held-out performance, a frozen split, and an exact local endpoint.

## 3. The automatic construct is not a label-free solution

The card avoids new expert annotation by defining a computable triad, but that merely replaces an expert phenotype with an unvalidated proxy. It does not establish that low apparent sulcal CSF is sulcal effacement, that local HU contrast corresponds to preserved gray-white *delineation*, or that segmented CTA voxels are engorged pial collaterals rather than veins, normal arteries, bone/contrast contamination, or phase effects.

This creates concept-label circularity at the construct gate: “stronger ipsilateral pial-vessel occupancy without reduced gray-white contrast” is partly the operational definition of the candidate and is then proposed as evidence that the detector found the clinical sign. Registration perturbation tests stability, not semantic validity. The released Circle-of-Willis pseudolabels described in the dataset paper are not pial collateral labels; they do not validate the required distal-vessel measurement (DOI `10.1148/ryai.250603`, “Segmentation of the Circle of Willis for CTA Scans”).

At least a blinded expert audit of candidate-positive and candidate-negative territories is needed. Under the charter this is permissible but incurs fresh annotation burden. A small enrichment audit can estimate positive predictive value, but sensitivity requires reviewing an appropriate sample of detector-negative territories too. The card's “no annotator” claim is therefore unsupported at the rung needed for the clinical phrase.

## 4. Support and power are worse than the card implies

The keystone screen correctly computes an expectation of about 11 cases from 8/108, below the proposed gate of 15. A second primary series found ISE in 12/195 overall (6.2%) and 11.4% among proximal anterior-circulation occlusions (PMID 32912520). This supports reproducibility of the rare sign, but it does not imply 15 usable ISLES territories because ISLES also includes posterior-circulation cases and the automatic construct is stricter/different.

More importantly, `>=15 territories` is not a power calculation. Territories within a patient are clustered; edit effects from perhaps 8–15 positive patients cannot be treated as independent. The threshold is currently convenient rather than tied to a minimum detectable paired response, a precision target, or stability across folds/model seeds. A negative after this gate would remain sensitivity-limited and model-specific. The card appropriately caps negative-result value at 2, but its proposed two-week experiment still risks spending most effort to obtain an uninformative null.

## 5. Clinical relevance is overstated at the deliverable level

The clinical papers support the proposition that ISE should not be interpreted as irreversible injury and may mark favorable collaterals. They do not establish that a final-infarct segmentation model's response to a synthetic ISE edit changes treatment decisions. ISLES is restricted to successfully reperfused patients, so the model predicts post-treatment infarct in a selected cohort; it is not a thrombectomy-selection model. “Mistaking reversible tissue for core can affect treatment interpretation” is a plausible motivation, not a demonstrated consequence of this audit.

The medically relevant model question should instead be: does a deployed or benchmark model systematically overpredict infarction in real, expert-confirmed ISE territories after successful reperfusion? That error question is closer to clinical harm and easier to interpret than a synthetic use claim, although it still requires enough real ISE cases and per-case predictions.

## 6. Prior-work overlap and novelty status

No verified duplicate of the exact model-use experiment was found in the repository's targeted novelty audit. That is not proof of novelty. The clinical phenomenon itself is not new: it has at least the 2015 EVT series (PMID 25931460) and the 2020 IV-thrombolysis series (PMID 32912520). The second series is material closest work missing from the card's `closest_prior_work`; it measured ISE, ASPECTS, and rLMC collateral score and tested response/outcome associations in 195 patients.

The exact delta, if pursued, is therefore not discovery of ISE as a rescue sign. It is either (a) external validation of ISE against spatial follow-up MRI in a public successful-reperfusion cohort, or (b) a model audit asking whether a specified final-infarct model exploits or mishandles that already-described phenotype. Novelty confidence should remain low until the 2020 paper's citation neighborhood and later computational work are audited from primary full texts.

## 7. Leakage and evaluation controls required in any revision

A defensible revision must freeze patient splits before thresholds, detector tuning, or model comparison. Automatic-triad thresholds and synthesis/generator development belong only in training/development data. Expert construct validation and the model-use endpoint need separate held-out patients. If the expected support is only about 8–15 cases, this separation may make the study impossible within ISLES'24 alone; cross-validation cannot turn model-selection data into confirmatory evidence. Multiple territories from one patient must be patient-clustered, and every authorized model seed and edit arm must be reported.

## 8. Plain-pitch fidelity

The pitch mostly preserves the card's speculative wording (“may,” “asks whether,” and the conditional proceed language). One phrase overclaims: “if the pattern can be separated from ordinary edema and scan-timing effects.” The technical card explicitly says within-case ratios and the conjunction **cannot fully solve CTA phase**, and its keystone admits single-phase CTA may not distinguish the pattern without expert labels. The pitch turns mitigation into possible separation and omits the crucial fact that the expected support (~11) is below the proposed 15-territory gate. This is a named pitch-fidelity defect. Revise it to say the study proceeds only if a validated detector finds adequate support, while CTA phase remains a residual limitation.

## 9. Is there a genuinely easier version?

The low-hanging data are real: ISLES'24 already supplies registered admission NCCT/CTA/perfusion, follow-up-MRI infarct masks, vessel-occlusion masks, and outcome data for 149 public cases. The clinical construct also has two prior expert-rated cohorts. What does **not** already exist is equally important: no released ISE label, no validated automatic ISE detector, no pial-collateral label, and no verified frozen high-performing model consuming the required NCCT/CTA information. Thus there is no low-hanging model-*use* experiment.

The easiest scientifically interpretable study is an expert-confirmed observational replication: blind readers to follow-up, label ISE on admission NCCT/CTA, and compare voxelwise infarction within ISE territories against matched Tmax-delayed, non-ISE territories after adjustment/matching for perfusion and location. Existing follow-up masks make the endpoint cheap; new expert ISE annotation is the unavoidable burden. This would test whether the 2015 tissue-sparing result transports to ISLES'24, not whether a model uses the sign. It is worth doing only if a rapid blinded census yields enough patients for a prespecified precision target; otherwise it is merely a tiny third case series.

For a subsequent model audit, the lowest-complexity useful endpoint is error stratification on those same real territories: compare a frozen model's local predicted infarct probability and false-positive burden in expert-confirmed ISE versus matched non-ISE delayed tissue. That is an association/error audit, not a use claim, but avoids invalid image synthesis. A causal use study should wait for a model and a joint-distribution-preserving intervention.

## Required revision/unblock conditions

1. Name and freeze a final-infarct model, checkpoint, exact input channels, preprocessing, training data, and untouched evaluation patients; verify that NCCT and CTA intensities—not merely an NCCT-derived brain mask—reach the model.
2. Replace the current edit with a joint-distribution-preserving intervention that includes the perfusion correlates of collateral engorgement, or reduce the claim to real-case error association.
3. Define the primary local continuous endpoint, expected direction, unit of analysis, clustering, multiplicity, and an effect/precision-based support gate rather than `>=15 territories` by fiat.
4. Validate the automatic construct against blinded expert ISE judgments, including detector-negative cases; treat this as new annotation burden.
5. Freeze all construct and edit-validity gates on development patients before model-output inspection. If the cohort cannot support disjoint development and evaluation sets, pause rather than call cross-validated exploration confirmatory.
6. Add PMID 32912520 as closest prior work and complete the primary full-text/citation-neighborhood audit.

NEAREST DEFENSIBLE HIGH-VALUE QUESTION: In successfully reperfused ISLES'24 patients, are expert-confirmed ISE territories less likely to infarct than perfusion- and location-matched Tmax-delayed territories without ISE?
RETAINS ORIGINAL MEDICAL MOTIVATION? YES
SHOULD IT BECOME A SEPARATE CANDIDATE? YES
IS IT ACTUALLY WORTH DOING? Yes, as a spatial external validation with follow-up MRI if a blinded census meets a prespecified precision target; below that target it is not worth publishing as another underpowered case series.
