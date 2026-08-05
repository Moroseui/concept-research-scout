# Debate transcript

## Round 1 — CRITIC

**Position:** The revised BrEaST descriptor-versus-category comparison cannot support a clean claim about the relative malignancy information in those representations unless differential outcome verification is neutralized.

**Argument:** BrEaST does not provide one uniform reference standard: the dataset paper reports that BI-RADS 1–3 cases may be verified by follow-up, whereas BI-RADS 4a–5 cases generally receive histology, and only 197 of 256 patients underwent biopsy. Because the recorded BI-RADS category helps determine the verification pathway, category is associated not only with malignancy risk but also with how the outcome label was established. A category-only model can therefore appear superior to a descriptor-only model partly because the evaluation endpoint and missing histology are conditioned on that same category. Stratifying the train/test split by verification type and reporting biopsy-only results as an exploratory sensitivity analysis does not fix this: conditioning on verification can introduce selection bias, and the biopsy-only subset is small and spectrum-enriched. With 98 malignant cases total, paired bootstrap intervals quantify sampling variability but not this label/selection mechanism. Thus even a statistically precise performance difference would remain ambiguous between representation quality and verification-process bias, weakening the proposed “decisive upper bound.”

**What would change my mind:** Show, from patient-level metadata and a prespecified analysis, that conclusions are directionally stable across the full cohort, the biopsy-verified subset, and a credible verification-bias sensitivity analysis (for example, explicit bounds over plausible malignancy misclassification among follow-up-verified cases); alternatively, use a public descriptor/category dataset with a uniform pathology reference standard.

**Status:** OPEN

## Round 2 — PROPOSER

**Responding to:** Because BrEaST's outcome label is established by a pathway that the BI-RADS category itself helps select — histology for the suspicious categories, interval follow-up for the low ones — the category-only arm may beat the descriptor-only arm partly because it predicts how the label was made rather than what the lesion is. Restricting to biopsied cases does not repair this, because that conditions on a category-driven selection variable and leaves a small, spectrum-enriched subset; paired bootstrap intervals cannot separate the two mechanisms.

**Response:** AMEND

**Argument:**

The objection is correct about the full cohort, and I am dropping the full-cohort "decisive upper bound" framing. But the patient-level metadata the critic asked for resolves the design question more favourably than either of us assumed, so the amendment is a change of primary analysis rather than an abandonment.

*Verified from the primary data descriptor* ([Pawłowska et al., *Sci Data* 11:148, 2024](https://pmc.ncbi.nlm.nih.gov/articles/PMC10830496/), DOI [10.1038/s41597-024-02984-z](https://doi.org/10.1038/s41597-024-02984-z), PMID 38297002): the released per-case table carries an explicit `Verification` column with exactly two values, "confirmed by biopsy" and "confirmed by follow-up care", alongside `BIRADS`, `Diagnosis`, `Classification`, and the descriptor fields `Shape, Margin, Echogenicity, Posterior_features, Halo, Calcifications, Skin_thickening`. Counts: 197 biopsy, 55 follow-up, 4 not applicable (normal). Category distribution: 1→4, 2→30, 3→37, 4a→44, 4b→46, 4c→49, 5→46. The descriptor is explicit that the 197 biopsies are what confirmed the 98 cancers.

Three consequences, and the third is the amendment.

1. **The uncertain-label mass is one-sided and small.** *Source-supported interpretation:* every case with a non-histologic reference standard is a label-**benign** case (55 follow-up + 4 normal); no malignant case rests on follow-up. The malignant class therefore already has a uniform histologic standard across the entire dataset. The critic's mechanism is real but it operates only on 55 of 154 benigns, all in categories 1–3.

2. **The critic's preferred remedy exists inside BrEaST.** The biopsy-verified subset *is* a public descriptor + category + uniform-histology dataset: n≈197, 98 malignant / 99 benign. That is a better-balanced comparison set than the full cohort, not a scrap of it. *Inference:* the subset is spectrum-enriched as the critic says, but the enrichment is a truncation of the **category** range specifically — verification was assigned on category, not on descriptors — so range restriction should attenuate the category arm, i.e. bias in the **opposite** direction from the full-cohort verification coupling. Full cohort favours category; biopsy subset penalises it. The two analyses bracket rather than agree, which is what makes directional stability across them informative. This is an inference about restriction of range, and it is directly testable by reporting both arms on both cohorts.

3. **Amendment.** The primary, prespecified endpoint moves to the **biopsy-verified subset only** (uniform histologic standard, patient-level frozen split). The full cohort becomes a secondary robustness analysis, not the headline. The third leg the critic asked for becomes a prespecified **tipping-point bound**: adversarially relabel the *k* follow-up-verified benigns that most favour the descriptor arm (lowest category-only score, highest descriptor-only score) as malignant, and report the smallest *k* that reverses the ordering, against the ACR anchor that BI-RADS 3 carries >0% but ≤2% likelihood of malignancy and BI-RADS 2 essentially 0% ([RadioGraphics 2024, 10.1148/rg.240169](https://pubs.rsna.org/doi/full/10.1148/rg.240169); primary anchor is the ACR BI-RADS Atlas 5th ed. and still needs a direct read). With 55 follow-up cases, 2% is ~1 case — so this bound is demanding, and I expect the full-cohort comparison to fail it. Saying so in advance is the point: the secondary analysis is prespecified to be discarded when *k* is small.

**What the amendment costs.** Three things, and none of them are cosmetic.

- *Population narrows.* Conclusions apply to the biopsied spectrum (predominantly 4a–5 plus some 3s), not to unselected diagnostic ultrasound. The category-only baseline is evaluated over a truncated category range, so its absolute AUROC is not comparable to published category-based figures. The biopsy decision boundary is where the descriptor-versus-category question is clinically live, which softens but does not remove this loss.
- *Power drops and the claim weakens with it.* 98 events over 197 cases means paired ΔAUROC intervals will be wide. The study can only detect a large descriptor deficit. A near-tie must be reported as underpowered, not as equivalence — so the gate on the downstream image-CBM work is now "descriptors lose **badly** on both bracket ends ⇒ stop", which is a weaker gate than the one I proposed.
- *"Decisive" is gone.* The honest label is a bracketed, power-limited upper bound. I am not claiming the verification mechanism is neutralised; I am claiming it is bounded in a stated direction with a stated tipping point.

**Not conceded:** that the comparison is ambiguous *in principle*. The ambiguity is one-sided and quantifiable here, which is different from irreducible.

**Spin-off (not pursued in this debate):** mixed reference standards are the norm in public breast ultrasound datasets, and verification pathway as a systematic confound for BUS model evaluation is its own study.

**Prerequisite before the feasibility memo:** read the released XLSX and confirm the `Verification` × `Classification` × `BIRADS` cross-tabulation directly, rather than relying on the descriptor's prose that the 197 biopsies confirmed the 98 cancers. If any malignant case turns out to be follow-up-verified, point 1 fails and this amendment must be revised again.

**Status:** OPEN

## Round 3 — CRITIC

**Position:** Even after the verification amendment, held-out performance of one fitted descriptor model versus a category score does not identify how much malignancy information the descriptors contain relative to BI-RADS category.

**Argument:** The proposer has adequately addressed my original objection at the level appropriate for a small study: making the uniform-histology subset primary, demoting the mixed-reference cohort, narrowing the target population, and refusing to interpret a near-tie as equivalence are substantive concessions. I therefore do not repeat the verification objection. The remaining problem is that the proposed estimands are being described as properties of the two representations, while the measured difference will also be a property of unequal decoding. BI-RADS category is already an ordered, malignancy-oriented judgement and can be evaluated almost directly as a scalar score. The seven BrEaST descriptors are multi-category variables whose joint state space is large relative to 197 biopsy-verified cases; converting them to risk requires choosing a model, coding rare levels, regularization, and tuning. A low-capacity model may underfit interactions the radiologist used when assigning category, while a more flexible model can overfit this dataset. Cross-validation and an untouched test set control optimism but cannot show that a descriptor deficit is informational rather than decoder- and sample-limited. This matters especially because the proposed stopping rule—descriptors lose badly, therefore stop before an image-to-descriptor CBM—could reject the intervention story for failure of the concept-to-label estimator, not failure of the vocabulary. The comparison can validly estimate the performance of prespecified deployable baselines on BrEaST; it cannot, without further analysis, support the stronger “descriptor-information upper bound” language.

**What would change my mind:** Reframe the primary claim as a comparison of prespecified prediction rules rather than representation information, or show that the conclusion is stable across a small preregistered decoder set spanning additive ordinal/categorical logistic regression and one interaction-capable model, with nested development-only tuning, identical frozen test cases, and a descriptor learning curve demonstrating that the observed deficit is not still strongly sample-size-limited. Any downstream stop rule must require concordance across those decoders and label the result a practical upper-bound screen, not an information-theoretic ceiling.

**Status:** OPEN

## Round 4 — PROPOSER

**Responding to:** The two arms are not decoded on equal terms. BI-RADS category arrives as an already-ordered malignancy judgement and needs essentially no fitting; the seven descriptors are multi-category variables with a joint state space large relative to 197 cases and must be turned into risk by a chosen, tuned, regularized model. So any measured descriptor deficit is confounded with decoder capacity and sample size, and calling the result a "descriptor-information upper bound" overclaims. Worse, the stop rule keys on exactly the branch this confound attacks: descriptors could "lose" because the concept-to-label estimator failed, not because the vocabulary is impoverished.

**Response:** AMEND

**Argument:**

The objection is correct and I take both of the offered remedies, not one. Before the concessions, two points that change what the reframe costs.

**1. The confound is directional, and it only threatens one branch.** Decoder and sample limitation can only make the descriptor arm look *worse* than the vocabulary warrants; no decoder deficiency inflates descriptor AUROC on frozen held-out cases. So the "descriptors match or beat category" branch is already safe under this objection — it survives *despite* the handicap. The entire force of the objection lands on the "descriptors lose" branch, which is precisely the branch carrying the stop rule. That localises the fix rather than dissolving the study, and it is why I am not conceding the design outright.

**2. The reframe the critic prefers is also the *deployment-relevant* claim, because the downstream head is linear.** *Source-supported* (from the read of Bunnell et al. recorded in `critique.md` fact 4, Table 4 — the "strict linear" CBM variant; the exact head parameterization still needs a direct read before the feasibility memo): the target model's concept-to-label stage is a linear map over concept scores. An image-to-descriptor CBM built in that lineage would therefore *be* an additive decoder over descriptors. The critic's "a low-capacity model may underfit interactions the radiologist used" is a fatal objection to an information claim and a non-objection to a prediction-rule claim, because the low-capacity constraint is the one the actual CBM operates under. So the reframe from "information" to "prediction rules" costs less for the downstream gate than it appears to, while genuinely destroying the information claim.

**Amendment — exactly what changes.**

- *Primary estimand.* No longer "how much malignancy information the descriptors carry relative to category." It is now: **on BrEaST's biopsy-verified subset, does a prespecified additive descriptor decoder match the recorded BI-RADS category as a malignancy score?** A comparison of two named prediction rules on one dataset. All "upper bound," "ceiling," and "information" language is struck from the idea card and README, including the round-2 phrase "bracketed, power-limited upper bound."
- *Decoder set, preregistered, three members, no more.* (i) **Primary:** additive multinomial-dummy logistic regression with L2, rare levels collapsed by a prespecified frequency rule fixed on development data only. (ii) Additive **ordinal** variant where each descriptor is coded by its clinically ordered levels — kept distinct from the malignancy-indicative binary collapse, which stays a separate ablation per the standing critique. (iii) One **interaction-capable** model, depth-limited gradient boosting. Nested CV on development data only; identical frozen test cases for all three; all three reported regardless of outcome, with (i) prespecified as primary so this is a concordance check and not a max-pick.
- *Equalise the arms.* The category arm gets the same pipeline — fit as an ordinal/categorical decoder on development data with the same regularization and nesting — rather than being scored as a raw ordinal. This does not repair the information claim, but it makes the prediction-rule comparison symmetric in fitting procedure, which is what the reframed estimand requires.
- *Learning curve as a gate, not a figure.* Descriptor-arm AUROC over development subsamples (≈25/50/75/100%), test set frozen, repeated over seeds. **If the curve is still rising appreciably at 100%, the stop rule is barred from firing** — the result is reported as sample-limited and inconclusive. This is prespecified so it cannot be reinterpreted afterwards.
- *Stop rule becomes conjunctive.* Stop before the image-to-descriptor CBM only if descriptors lose badly under **all three** decoders, on **both** bracket ends from round 2 (biopsy subset and full cohort), **and** the learning curve is flat. Anything short of that is "inconclusive, proceed with reduced expectations."
- *Cheap extra bracket, labelled crude.* Report the apparent (development-fit, development-evaluated) AUROC of the additive model alongside held-out. For a ~20-df additive model on ~197 cases this brackets optimism from above and is one line of output. It is a sanity bracket, not a ceiling, and it is meaningless for the boosted model — reported only for (i) and (ii).

**What this costs — and it is more than the round-2 amendment cost.**

- *The screen loses most of its screening power.* A conjunctive four-condition stop rule will rarely fire. The whole point of this study was a days-not-weeks gate that could kill the image-CBM line cheaply; a gate that mostly returns "inconclusive" is a much weaker instrument. I expect the modal outcome now to be inconclusive rather than decisive in either direction, and the study's value drops accordingly.
- *The claim is now parochial.* "These two prediction rules, on this dataset, on this subset" generalises to nothing on its own. It is no longer a statement about the BI-RADS vocabulary. Someone reading the result cannot conclude anything about descriptors in general.
- *Multiplicity on 197 cases.* Three decoders × two cohorts × a learning curve, on ~98 events. The concordance requirement partly disciplines this, but the analysis-to-data ratio is now poor and every non-primary number is exploratory. This must be stated as a limitation in the memo, not discovered later.
- *Round-2's "bracketing" argument is weakened, not withdrawn.* The restriction-of-range argument still holds for the category arm, but now has to survive three decoders on the descriptor side, so directional stability is a harder bar than I set in round 2.

**Self-policing.** This is the second amendment to the core estimand in four rounds. The rule of thumb is that a third means the idea was wrong rather than mis-specified. I am recording the trigger in advance: **if a further objection forces another narrowing of the primary estimand, the recommendation becomes REJECT, not REVISE.** The idea has now been narrowed from "does concept intervention survive realistic clinician behaviour" (idea card) to "do two prediction rules differ on 197 biopsied BrEaST cases," and that trajectory is itself evidence about the original candidate.

**Not conceded:** nothing further in this round. I am not defending the information framing at all.

**Prerequisite unchanged and now larger:** the round-2 XLSX cross-tabulation check, plus a direct read of Bunnell et al.'s concept-to-label head to confirm it is linear. If the head is not linear, argument 2 above fails and the additive decoder loses its deployment justification.

**Status:** CONVERGED

## Round 5 — CRITIC

**Position:** The amended study no longer tests concept intervention at all, so it cannot answer the idea's motivating question or retain its claimed medical relevance as an intervention audit.

**Argument:** The new primary estimand compares a decoder fitted to radiologist-recorded descriptors with a decoder fitted to the same radiologist's recorded BI-RADS category. Neither arm contains image-predicted concepts, an intervention-selection policy, a pre-intervention prediction, or a post-intervention prediction. Consequently, the experiment cannot estimate intervention benefit, intervention burden, robustness to imperfect correction, or the distribution shift that Bunnell et al. already showed can make maximal oracle correction harmful. Even a clear descriptor-versus-category result does not repair this disconnect. If the descriptor rule matches category, an image-to-concept model may still predict the descriptors too poorly for correction to help; if it loses, that says only that the named fitted rule loses on BrEaST, not that correcting predicted concepts lacks value. The proposed downstream gate therefore rests on a quantity that is not on the causal path being advertised: recorded descriptors are substituted for the predicted-and-corrected concept states whose behavior motivates the project. This is not another request to narrow the estimand; it is evidence that the successive amendments have converted Idea 003 into a different, modest baseline study. Under the proposer's own self-policing rule, preserving the original title, rationale, and scores after that conversion would warrant rejection rather than another revision.

**What would change my mind:** Either revise the idea card, title, medical-relevance claim, and scores so this is explicitly a standalone BrEaST prediction-rule benchmark with no intervention conclusion, or identify a feasible public-data experiment that produces image-predicted descriptors and evaluates prespecified observable pre/post-intervention policies against BI-RADS category on untouched cases; the latter must show that its sample size and concept-label quality are adequate before the intervention claim is restored.

**Status:** OPEN

## Round 6 — PROPOSER

**Responding to:** Neither arm of the amended study contains an image-predicted concept, a selection policy, or a pre/post-intervention pair, so the experiment cannot estimate intervention benefit, burden, robustness, or the correction-induced distribution shift that motivated Idea 003. Recorded descriptors have been substituted for predicted-and-corrected concept states, which are not the same quantity, so the downstream gate is off the advertised causal path. The successive amendments have produced a different, modest study, and keeping the original title, rationale, and scores over it would be rejection-worthy under my own round-4 rule.

**Response:** CONCEDE

**Argument:**

The objection is correct. The amended design does not test concept intervention, and I am not going to argue that it does.

I considered one rescue and am recording why it fails rather than deploying it, because the failure is the informative part. The rescue would be: under a strictly linear, side-channel-free head, full oracle intervention sets every concept state to its recorded descriptor value, so the additive descriptor decoder *is* the fully-intervened model's prediction, and a bad descriptor-arm result would upper-bound the intervened model — a genuine necessary condition for the "beats reading the category" half of the question. It fails on the actual target architecture for two reasons already in `critique.md`: the model carries a learned non-clinical side-channel node (fact/point 4 of the critique, where the paper itself finds the head can ignore the named concepts in its favour), and intervention there writes pseudo-probabilities 0.51/0.99 into soft concept scores rather than hard descriptor levels (fact 3), so partially-intervened states retain image-derived information that recorded descriptors do not contain. Concept leakage through soft scores breaks the ceiling in the same direction. So the necessary-condition argument holds only for a hypothetical hard-valued, leak-free, side-channel-free variant that is not the model under audit. That is too narrow a slice to carry the idea, and I am not claiming it does.

**What this concession means concretely.**

- **Idea 003, as titled and scored, is rejected.** The question "does BI-RADS concept intervention survive realistic clinician behaviour, and does it beat reading the BI-RADS category" is not answerable with any public data identified across the critique and six debate rounds. The intervention arm needed descriptor labels BUS-BRA does not release, a training cohort that is not public, and — for the "realistic clinician" half — reader-correction data that neither of us has located in any public source. I did not find such a dataset; that is not proof none exists, but it is the state of the evidence and it is not a resolvable gap at this stage.
- **The scores do not transfer.** `medical_relevance` 5 and `negative_result_value` 5 were both earned entirely by the intervention framing ("directly tests the main clinical selling point of concept bottleneck models", "would directly undercut a headline claim"). Neither survives on a descriptor-versus-category benchmark. `prior_legwork` 4 and `feasibility` 3 were scored against the bus-cbm code and BUS-BRA retraining plan, which are both gone. Any residual card must be rescored from scratch, not edited downward.
- **The residual is not Idea 003.** The BrEaST descriptor-versus-category prediction-rule comparison, with everything agreed in rounds 2 and 4 (biopsy-verified subset primary, three preregistered decoders, symmetric fitting of both arms, learning-curve gate, no ceiling or information language), is a coherent small study. It should be carried forward, if at all, as a separately identified candidate with its own title, its own medical-relevance argument standing on its own feet, and its own scores — and with no stop-rule authority over any intervention work, since that authority is exactly what this round retires. Retitling Idea 003 in place would launder the trajectory.
- **My round-4 trigger fires as written.** Two amendments to the core estimand, and this objection shows the second one severed the study from the motivating question. The recommendation I carry out of this debate is **REJECT** for Idea 003, not REVISE.

I am not proposing a replacement question here. The round-2 spin-off (verification pathway as a systematic confound in public breast ultrasound evaluation) and the residual BrEaST benchmark are both on the record and both belong to the scouting stage, not to this debate.

**Status:** CONCEDED
