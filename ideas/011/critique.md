FATAL OBJECTION: Conditioning an age prediction on a second age-correlated variable cannot show that the model used that variable; the proposed primary endpoint is non-identifying.
EVIDENCE: The Stage 2 mediation specification in `idea_card.json`, combined with Shabani et al. (PMID 34966360, DOI 10.3389/fendo.2021.785957), which establishes that cartilage calcification itself rises with age.
REPAIRABLE WITHOUT CHANGING THE QUESTION? YES
DECISION: PAUSE

# Adversarial review

## 1. The present experiment cannot earn the deliverable sentence

The question is causal—does the model **use** calcified costal cartilage?—but the proposed test is associational. Let chronological age be `Y`, model prediction be `P`, cartilage volume be `C`, and any other visible age marker be `Z`. A model can construct `P` entirely from `Z`; because both `C` and `Z` track `Y`, adding `C` to a regression of `P` will often attenuate an age coefficient or explain variance in `P` even when no cartilage voxel influenced the model. Sex stratification and a competing-mediator panel do not close this path. They only change which correlated proxies enter the regression.

This is concept–label circularity in measurement form: the model is optimized/probed for age, and the proposed concept is selected because it predicts age. Correlation between two age estimators is not evidence that one is inside the other. “More attenuation than aorta, vertebrae, or emphysema” is also not a causal criterion; its ranking depends on measurement error, scale, nonlinear specification, collinearity, and age-range restriction. The card supplies no preregisterable effect or equivalence margin.

Therefore a positive Stage 2 result supports only: **calcified cartilage volume predicts the output of an age predictor**. It does not support: **the model is using calcified cartilage volume**, and especially not the stronger “rather than” clause. This candidate is currently at rung 0 for the model-use claim, not conditional rung 3. X is human-legible, but X has not been linked to the model causally.

## 2. The claimed negative is not decisive

The assertion that “one of [the competing mediators] will be the answer” is false. The model may distribute signal across many weak markers, use an omitted feature (airway geometry, muscle composition, breast tissue, skin, acquisition), or encode interactions that no scalar mediator captures. A null cartilage coefficient can also result from TotalSegmentator error, restricted age range, sex interaction, protocol-dependent thresholding, collinearity, or a weak age probe. This is a **sensitivity-limited** negative, not a decisive negative. Negative-result value should be at most 2 under the rubric, not 4.

A decisive negative requires a validated intervention with a prespecified minimum detectable change: changing cartilage while holding other anatomy fixed fails to change model output beyond an equivalence margin. Even that conclusion must be scoped to the intervention's fidelity and the tested model.

## 3. Stage 0 does not validate the extractor

Recovering the MESA age slope would not establish accurate cartilage segmentation. An age-dependent segmentation error can reproduce an age slope precisely because calcified cartilage is easier to see than uncalcified cartilage. Conversely, failure to reproduce MESA's slope need not indict the extractor: MESA used semi-automated ROIs on cardiac CT in a selected cohort, whereas CT-RATE comprises routine non-contrast diagnostic chest CT. Population, sex mix, slice thickness, kernel, reconstruction count, and referral pathway can change the slope.

The proposed “landmark box” is not segmentation-independent measurement of X. A >180 HU voxel count in a broad rib–sternum box includes rib, sternum, vascular calcium, devices, and potentially contrast or noise. Agreement between two biased measurements would not prove cartilage specificity. The keystone needs direct accuracy assessment against a reference that distinguishes cartilage from adjacent bone across age and calcification severity. That likely requires a small annotation/quality-control set, which is allowed if it is not a large annotation campaign, but contradicts the claim that the current measurement is ready today without asking anyone.

TotalSegmentator's primary paper evaluated 104 structures across heterogeneous CT and reported strong aggregate performance (Wasserthal et al., DOI 10.1148/ryai.230024), but aggregate performance does not inspect costal-cartilage accuracy or age-dependent error. The emergence of a dedicated costal-cartilage segmentation benchmark explicitly motivated by low contrast further weakens the assumption that presence in a class map equals validated measurement (Zhang et al., arXiv:2408.07444; later Expert Systems with Applications, 2026).

## 4. Data and model readiness are overstated

The card correctly admits that the released per-volume age column in CT-RATE has not been inspected. The official CT-RATE paper verifies only that the corpus contains 25,692 non-contrast scans, paired reports, and metadata; it does not establish from the accessible article text that age is released per scan (Hamamci et al., *Nature Biomedical Engineering* 2026, DOI 10.1038/s41551-025-01599-y). Until the actual metadata schema is inspected, the proposed CT-RATE experiment is unavailable, not merely inconvenient.

The model is also hypothetical. CT-CLIP is a report–image foundation model, not an age model. Its official repository now advertises pretrained checkpoints and says inference is possible on smaller GPUs, but the age linear probe has neither a demonstrated accuracy nor a frozen split. Calling it “a linear probe rather than a training run” understates that a new target model must be created and validated. Patient-level splits are mandatory because CT-RATE contains multiple reconstructions per scan and potentially multiple scans per patient.

Text pairing is not direct inference-time leakage—the image encoder receives pixels—but it can make report-correlated visual shortcuts salient. More mundane leakage is worse: age can be encoded in burned-in text, scan fields, reconstruction/protocol choices, or the age-dependent referral population. Those must be audited. A same-institution random patient split does not exclude them.

Compute is manageable only after narrowing. Full TotalSegmentator inference over tens of thousands of reconstructions is unnecessary and wasteful; duplicate reconstructions must not be treated as independent observations. CT-CLIP's repository states that training needs an 80 GB A100 at batch size 8, although inference can use smaller GPUs. The proposed frozen-encoder route is plausible on Colab, but only after checkpoint loading and embedding extraction are demonstrated on a small set.

## 5. Prior-work overlap and relevance

The biological finding is occupied. Shabani et al. quantified >180 HU bilateral costal-cartilage calcium in 2,305 MESA participants and measured sex-specific age gradients (PMID 34966360). Zhang et al. already used clinical multislice CT costal cartilage to estimate adult age (PMID 28717963, DOI 10.1007/s00414-017-1646-y). Lu et al. trained deep models directly on costal-cartilage CT representations in 2,700 subjects (PMID 37231070, DOI 10.1007/s00330-023-09761-3). The novel delta is therefore only whether a whole-chest model independently relies on this known marker.

The card also understates whole-chest CT age precedent. Azarfar et al. trained an unguided chest-CT age model on 13,824 NLST scans, externally tested it on 1,849 local scans, and reported lung-region activation and association of CT-age acceleration with lung-cancer risk (PMID 37418109, DOI 10.1007/s11548-023-02989-w). That is closer than the radiograph precedent and removes the need to borrow the existence of an age-prediction gap from another modality. No public checkpoint or official code was located in this review, so it is prior work, not yet a reusable asset.

Medical relevance is modest but real only if tied to biological-age interpretation: if a clinically prognostic “CT age” is mostly chronological cartilage mineralization, its apparent biological-aging meaning changes. As written, however, CT-RATE chronological-age prediction has no demonstrated clinical endpoint. The forensic story is engaging but does not itself create a radiology consequence.

## 6. Confounds the proposed design does not identify

- **Scanner/vendor, acquisition, reconstruction, site:** all can affect thresholded calcium and model embeddings. Stratification cannot isolate them when age and protocol are imbalanced. Multiple reconstructions must be collapsed or used as a robustness analysis, never counted as independent cases.
- **Position and habitus:** mask-based volume is not automatically invariant. Truncation, field of view, inspiratory level, body size, and anterior chest coverage affect both the denominator and available cartilage.
- **Disease prevalence and referral pathway:** “not applicable because age has no prevalence” is incorrect. Diseases and indications have age-dependent prevalence and can supply easier age signals; routine CT referral creates the correlation structure the model learns.
- **Label leakage:** DICOM/burned-in annotations, protocol choices, and report-aligned pretraining need explicit audits. Report-text pretraining alone is not proof of leakage, but it makes a report-age audit necessary.
- **General calcium burden:** regression adjustment for aortic calcium does not distinguish local cartilage use from a distributed calcium detector.

The design rules out none of these sufficiently for rung 2. A multicohort external test can address site/referral dependence; within-volume interventions are needed for local use; paired reconstructions can test reconstruction robustness.

## 7. Easier formulations and available assets

### Low-hanging fruit, conditional on one schema check

The smallest version preserving the question is a **localized intervention study on a frozen CT-CLIP age probe**, using one reconstruction per patient from CT-RATE validation rather than segmenting the full corpus. Assets now verified from official sources are: CT-RATE volumes/reports and patient-grouped naming, public CT-CLIP code and advertised pretrained checkpoints, and a free TotalSegmentator costal-cartilage class. The missing load-bearing asset remains the released per-scan age field. If it exists, a few hundred age-stratified, sex-stratified cases can first establish probe signal and intervention sensitivity.

The primary readout should be paired change in predicted age after a local, anatomically constrained cartilage intervention, compared with volume-, location-, and attenuation-matched control interventions. At minimum include: cartilage intervention; adjacent rib/sternum control; aortic-calcium control; and random anterior-soft-tissue control. Preserve an untouched patient-level test split and preregister an equivalence margin. Because deletion is OOD, use several interventions that agree—local intensity replacement sampled from age/sex-matched low-calcification anatomy, calcification-only replacement inside a validated mask, and complementary retention—with artifact detectors and sham transformations. This is harder scientifically than mediation but much smaller computationally.

This remains imperfect: synthetic editing may create OOD signal, and an image-only CT-CLIP probe may be weak. Agreement across matched interventions and external replication would move it to rung 1; protocol/site robustness would be needed for rung 2; only then could the named X support rung 3.

### Existing-data alternative that does not preserve the model-use question

NLST is the obvious age-labelled whole-chest CT corpus: TCIA lists 26,254 subjects and age demographics, and Azarfar et al. already trained on 13,824 scans. But complete clinical linkage requires an approved CDAS project/data-transfer agreement, the image collection is about 11.9 TB, and no reusable checkpoint was found. Thus it is not lower-hanging under this charter. A small automated-cartilage-versus-age benchmark on NLST would merely replicate known biology and is not worth promoting as a separate candidate.

## 8. Required revision gates

1. Inspect the actual CT-RATE metadata schema and one joined image–age row. If age is absent or cannot be linked at patient/scan level, pause until another confirmed corpus is found.
2. Demonstrate a useful frozen-encoder age probe with patient-level splits and one reconstruction per scan; define “useful” before fitting.
3. Replace mediation as the primary endpoint with paired, matched localized interventions and an equivalence margin. Mediation may remain descriptive only.
4. Validate cartilage localization across age and calcification severity on a small reference set; an external cohort slope is not segmentation validation.
5. Audit burned-in text, report age mentions, protocol/vendor imbalance, reconstruction duplication, truncation, and sex. Replicate across at least one site/corpus before any rung-2 claim.
6. Rewrite the deliverable without “rather than” unless interventions show cartilage effects exceed every named matched control. A defensible interim sentence is: “For this model and intervention family, changing calcified costal cartilage changes predicted age more than matched changes to adjacent bone, aortic calcium, or anterior soft tissue.”

## Decision rationale

This does **not** die like the annotation-provenance candidates: chronological age can be an administrative measurement if the released field is verified. It does repeat the wrong-keystone pattern of ideas 005/006: the easy facts—class exists, cartilage predicts age, model predicts age—do not establish the needed fact that a change in cartilage causally changes this model's output under an in-distribution intervention. The current endpoint is fatally non-identifying, but the scientific question survives a change in experimental design. Therefore: pause, do not reject.

NEAREST DEFENSIBLE HIGH-VALUE QUESTION: In a frozen whole-chest CT age model, do anatomically constrained changes to calcified costal cartilage cause larger paired age-prediction changes than matched interventions to adjacent bone, aortic calcium, and anterior soft tissue?
RETAINS ORIGINAL MEDICAL MOTIVATION? YES
SHOULD IT BECOME A SEPARATE CANDIDATE? NO
IS IT ACTUALLY WORTH DOING? Yes—if a released age field and usable frozen age probe pass cheap gates, the controlled intervention directly tests whether a clinically interpretable CT-age signal is a known developmental clock rather than merely another correlate of age.
