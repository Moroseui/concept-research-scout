# Debate transcript

## Round 1 — CRITIC

**Position:** The proposed experiment cannot establish the original claim that Sybil uses pulmonary vascular pruning, because residual association between Sybil scores and BV5/TBV is not a test of model reliance.

**Argument:** Stage 1 correlates two quantities derived from the same NLST LDCT, and Stage 2 conditions that correlation on LAA%-950; neither intervention varies vascular information while preserving the model's other inputs, nor does it probe or ablate a vascular representation. A positive partial BV5/TBV coefficient therefore remains compatible with Sybil ignoring vessels entirely and using correlated smoking-related parenchymal texture, airway disease, occult nodules, coronary calcium, habitus, or reconstruction artifacts. This is especially acute because San Jose Estepar et al. reported an association between emphysema and vascular ratios (PMID 23656466; DOI 10.1164/rccm.201301-0162OC), while both BV5/TBV and LAA%-950 are reconstruction-sensitive measurements from the same voxels. Measurement error and disease-dependent vessel-segmentation failure can leave or create a residual coefficient; partial regression does not turn correlated phenotypes into competing identified mechanisms. The proposed same-acquisition reconstruction-pair amendment is useful only as an acquisition-sensitivity audit: it asks whether the provisional vessel metric and Sybil score respond together to kernel or slice thickness. That no longer answers the original biological-use question, so under the identity check it cannot rescue Idea 009 and should remain a bounded arm of the reconstruction project rather than be treated as evidence that Sybil reads pruning. The branching-exponent analysis has the same reliance problem even if its measurement becomes feasible.

**What would change my mind:** Show a validated, in-distribution intervention or representation test that selectively changes or removes pulmonary vascular calibre/tree information while preserving parenchyma, nodules, acquisition statistics, and gross anatomy, with sham interventions and same-patient controls, and demonstrate a preregistered Sybil score effect beyond the sham; alternatively, narrow the claim and deliverable explicitly to reconstruction-coupled covariance and treat it as a separate candidate rather than an explanation of what Sybil uses.

**Status:** OPEN

## Round 1 — PROPOSER

**Responding to:** The card's primary design is observational. It computes BV5/TBV and LAA%-950 from the same voxels the model sees and regresses the risk score on them. Nothing in that varies vascular information while holding the rest of the image fixed, so a surviving partial coefficient is compatible with Sybil ignoring vessels entirely and reading any of the many smoking-related phenotypes that travel with pruning. Partial regression on two correlated, reconstruction-sensitive, same-image measurements does not convert them into competing identified mechanisms, and the branching-exponent arm inherits the same defect even if its measurement were solved. The reconstruction-pair fallback answers a different question and fails the identity check.

**Response:** AMEND

**Argument:**

I concede the objection as stated, without reservation. Stage 1 and Stage 2 as written are not a test of model reliance and I withdraw them as the primary experiment. The card asserted rung 3 on the strength of a design that does not clear rung 1, which is the exact failure the charter names as standard in this literature. The partial-association analysis survives only as a descriptive covariate check reported alongside the real experiment, and the card's `anticipated_negative.classification` of "decisive" was wrong for the reason the critique gives — a null partial coefficient is sensitivity-limited.

What I dispute is that the question is therefore unanswerable. The critic's own unblocking condition — a same-patient intervention that removes vascular calibre information with a sham control — is constructible on exactly the assets already listed, and it is cheaper than the observational design it replaces.

**The amended experiment: within-patient calibre-band ablation with a volume-matched sham.**

Segment the intrapulmonary vessel tree and compute per-segment cross-sectional area. For each held-out nodule-free NLST scan, generate four volumes and run Sybil on all four:

- **O** — original, untouched.
- **A** — vessel voxels belonging to segments below 5 mm² cross-section are replaced by locally sampled parenchyma. Total replaced volume is V. This is simulated distal pruning.
- **B** — the volume-matched sham. The same inpainting operator replaces V voxels drawn from segments *above* 5 mm², matched on the patch-size distribution used in A.
- **C** — the artifact floor. The same operator replaces V voxels of non-vessel parenchyma, matched on patch geometry, touching no vessel.

The estimand is the paired contrast Δ(A) − Δ(B) against the floor Δ(C), where Δ is the within-patient change in Sybil's score at one preregistered horizon.

**Why this meets each alternative the critic listed by name.** Parenchymal texture outside vessels, airway disease, occult nodules, coronary calcium, body habitus, scanner, vendor, kernel, slice thickness, dose, noise texture, site, referral pathway, prevalence, and inspiration level are not merely balanced across A, B and C — they are the *same voxels* in the same patient in the same forward pass. They cannot differ. The only quantity that differs between A and B is which calibre band lost blood-filled tubular structure, with removed volume held equal. That is a rung-1 test of calibre-specific vascular reliance, and it is within-patient, so it needs no cohort-level adjustment at all.

**The disease-dependent segmentation-failure confound reverses direction under this design, and that is the strongest single argument for the amendment.** The critique's most plausible route to a false positive was that emphysematous lung yields worse small-vessel recovery, manufacturing a pruning association from tool failure. Under ablation, a segmenter that misses small vessels in sick patients removes *less* in condition A in exactly those patients. The failure attenuates the effect toward the null. It can no longer produce the positive; it can only hide one. That converts the card's most dangerous confound into a conservative bias, which is a genuinely different epistemic position and not a rhetorical reframing.

**The new keystone, and the honest residual.** This design has an intervention-validity burden, and the charter records that this loop has already died on one of those (idea 006, patient-deletion). The difference is structural, not a matter of my confidence: idea 006 had a single edited arm with no matched control for its own out-of-distribution-ness, so the score change confounded "model relies on exterior" with "model is confused by an impossible image." Here the impossibility is matched across arms — A and B apply the identical operator to the identical volume of blood-density tubular structure inside the same lung — and the contrast differences it out. Additionally, unlike a body-excluded volume, the *target* of A lies inside the real data manifold: a lung with fewer small vessels is what pruning looks like, and NLST contains such lungs.

Writing the mandated sentence: if I have only verified the nearest checkable thing, what am I still assuming? I am assuming **artifact exchangeability across calibre bands** — that the model's response to "a filled tube" does not depend on the tube's diameter for reasons unrelated to vascular anatomy. That is not guaranteed and I will not claim it is. A convolutional network with scale-sensitive receptive fields could respond differently to small-patch and large-patch inpainting artifacts independently of what the patches used to contain. This, not vessel-segmentation fidelity, is now the load-bearing fact, and it is `NOT_INSPECTED`. Two checks address it, both preregisterable: condition C establishes the artifact floor at matched patch geometry with no vessel involved; and a **calibre dose-response** — repeat the ablation at 0–2, 2–5, 5–10 and >10 mm² bands at matched removed volume. A monotone score response that peaks in the small bands is a shape that a scale-dependent-artifact story must work hard to produce, whereas a flat or U-shaped response across bands would indicate the artifact dominates and would kill the arm. Stage 0 therefore acquires a second gate, and either gate can end the candidate.

**What is lost. Three things, and the first is the title.**

1. **The Murray exponent clause is dropped from the deliverable.** An ablation cannot test a branching-law departure; you cannot remove "the exponent." The deliverable sentence narrows to *the model is using distal small-vessel blood volume* — one clause of the original two. This is a real cost: the Murray framing carried the card's `mechanism_clarity` of 4 and supplied the inflation-invariance test that answered the charter's "what changes if the analogy is dropped." With the exponent demoted to an unreportable aside, mechanism clarity should fall to 3 and the Mode C priority score with it. The title over-promises relative to the amended design and should be rewritten before this goes anywhere.
2. **"Rather than parenchymal destruction" survives only if the symmetric arm is run.** Ablating vessels shows vascular reliance; it does not rank vascular against parenchymal. The honest repair is to run the mirror intervention — fill a matched volume of LAA-950 voxels to normal parenchymal density, same operator, same sham discipline — so that the competition with C1 becomes two interventions rather than two regression coefficients. That preserves the original comparative question and doubles the compute.
3. **Feasibility falls further.** Four to eight forward passes per scan, plus segmentation and inpainting per volume, on top of a Stage 0 that must now clear both segmentation fidelity at the 5 mm² boundary and artifact exchangeability. Feasibility 2 was already the portfolio floor; this does not improve it.

**Identity check.** Original question: is the non-nodular part of Sybil's risk signal carried by pulmonary vascular pruning rather than parenchymal destruction? The amended design answers the vascular limb directly at rung 1 and, with the symmetric arm, delivers the head-to-head comparison the original asked for — on the same scans, within patient. It does not answer the branching-exponent half. So this is a **partial** identity pass: the primary question is retained, the secondary clause is abandoned rather than repaired, and I am stating that rather than letting the title carry it.

**On prior art.** I searched for a published vessel-specific ablation or inpainting attribution study on chest CT models and did not find one; that is a search result, not a novelty claim, and the searches did not cover thoracic society abstracts. The closest tooling I located is a synthetic pulmonary CT phantom line that generates vascular trees with controlled properties (bioRxiv 022871, SEARCH_SUMMARY_ONLY — not inspected, and not a substitute for validating an inpainting operator on real NLST volumes).

**Spin-off, not a rescue.** I agree with the critic that the reconstruction-pair acquisition-sensitivity audit answers a different question and must not be counted as evidence about biological use. It belongs to the Idea 008/C1 reconstruction work as a bounded arm; recorded here, not defended here.

**Status:** OPEN

## Round 2 — CRITIC

**Position:** The amendment fails the identity check because it abandons the defining Murray-exponent claim and replaces biological pruning with sensitivity to a synthetic calibre-targeted deletion.

**Argument:** The original question and deliverable are compound: Sybil is claimed to use loss of BV5 *and* a shift in the arterial branching exponent away from Murray's cube law, rather than parenchymal destruction. The proposer now explicitly drops the exponent from the deliverable because it cannot be intervened on, so the physical mechanism named in the title is no longer tested. More importantly, condition A does not create the biological quantity BV5 was validated to describe in San Jose Estepar et al. (PMID 23656466; DOI 10.1164/rccm.201301-0162OC): chronic distal vascular rarefaction/remodelling embedded in real lung anatomy. It deletes visible blood-density tubes from an already formed CT while leaving their branching context and associated tissue unchanged. A differential Sybil response would establish only that the model is sensitive to deleting image structures selected by an estimated calibre band, not that naturally occurring pruning carries its non-nodular risk signal. The volume-matched large-vessel and parenchymal shams improve attribution of the edit response, but they cannot bridge that construct-validity gap; nor does the proposed symmetric LAA edit recover the abandoned branching-law clause. The amendment is therefore a potentially testable new rung-1 candidate—calibre-specific vessel-ablation sensitivity—but it is not Idea 009's Murray-law/pruning explanation and should be spawned separately rather than treated as a repair.

**What would change my mind:** Preserve the original candidate by showing, on real same-patient or otherwise exchangeable scans, independently measured natural variation in both BV5 and the fitted branching exponent while acquisition and parenchymal change are held fixed, together with a validated model-reliance test tied to those natural changes; otherwise retitle and register the ablation study as a separate candidate with the narrower deliverable that Sybil is sensitive to removal of sub-5-square-millimetre vessel-like structures.

**Status:** OPEN

## Round 2 — PROPOSER

**Responding to:** The amendment does not repair Idea 009, it replaces it. The deliverable sentence names two things — small-vessel blood volume and a shift in the branching exponent away from the cube law — and the exponent limb has now been withdrawn because you cannot ablate a scaling law, so the physical mechanism in the title goes untested. And the surviving limb tests the wrong construct: deleting blood-density tubes selected by an estimated calibre band from an already-formed CT is not chronic distal rarefaction embedded in real anatomy, so a differential response shows the model is sensitive to that edit, not that naturally occurring pruning carries its non-nodular risk signal. Shams fix attribution of the edit, not the construct. Register the ablation separately.

**Response:** CONCEDE

**Argument:**

The objection is correct and I am not going to spend a third amendment on it.

**The exponent limb is dead and it is the title.** I conceded in round 1 that ablation cannot test a branching law. The critic is right that this is not a survivable partial pass, because the observational route to the exponent was already killed in round 1 by the same reliance objection that killed the BV5 route. Both routes to the Murray clause are therefore closed, not one. A candidate whose named mechanism has no remaining path to test is not amended by dropping the mechanism; the sentence a radiologist would read and agree or disagree with was *the model is using pruning, including the departure from the cube law*, and I can no longer offer any version of it.

**On construct validity I concede the limit, and I want the scope of the concession stated precisely, because it matters for what the spin-off is allowed to claim.** I do not accept that the ablation is invalid — the charter's rung 1 explicitly admits ablation and occlusion with proper controls, and the volume-matched calibre-band shams are proper controls. What I accept is that its estimand is counterfactual necessity of those voxels in a synthetic edit, and that this can come apart from the natural-variation claim in **both** directions:

- The model can be sensitive to deletion while natural BV5 variation contributes nothing separable to score variance in intact scans — the critic's direction.
- The model can be **insensitive** to deletion while pruning is still the biology, because what it reads is the parenchymal correlate of rarefaction — regional density and tissue loss in underperfused lung — rather than the tubes themselves. Ablating the tubes leaves that correlate intact and returns a null.

The second direction is the one I had not written down and it is the more damaging, because it means the ablation is not even a clean negative for the original question. That is a decisive reason to stop calling it a repair.

**Why I am not attempting a third amendment: the critic's unblocking condition is not constructible on data I can name.** It asks for natural variation in BV5 and the exponent with acquisition and parenchymal change held fixed. Enumerating what exists:

- NLST repeat annual screens (T0/T1/T2 by trial design) give same-patient natural change, but acquisition is not fixed across years, and two years of pruning progression is small against a measurement whose own human reference literature disperses at 2.31 ± 0.60 and 2.92 ± 1.07 (PMID 40489106; PMID 32618514). Inference, not verified: the within-patient signal is below the measurement floor.
- Paired breath-hold data such as the idea-007 corpus (TCIA DOI 10.7937/3ppx-7s22, confirmed in the ledger) holds acquisition genuinely fixed, but changes vessel calibre by recruitment and distension rather than rarefaction, and moves parenchymal density in the same breath. Wrong construct, and parenchyma not held fixed.
- Same-acquisition reconstruction pairs change the measurement and not the anatomy, which both sides already agree is an artifact audit belonging to Idea 008.

No available arm reaches the deliverable. That is the concession.

**What actually killed this, for the ledger.** The card's declared keystone was measurement fidelity — can BV5 and the exponent be computed on low-dose screening CT. That was the nearest checkable thing again. The load-bearing fact was that *a computable phenotype regressed against a model score constitutes a reliance test*, which is false; and behind it, that *natural variation in that phenotype can be isolated from acquisition and parenchyma in obtainable data*, which is also false. This is the fourth occurrence of the wrong-keystone pattern the charter names, and it is worth recording as such: the candidate was gated on whether X is measurable when it should have been gated on whether variation in X is separable.

**Spin-off, recorded and not defended here.** Register the within-patient calibre-band ablation as a new candidate with the narrower deliverable the critic states — *Sybil's score responds to removal of sub-5 mm² vessel-like structures beyond a volume- and geometry-matched sham* — explicitly rung 1, explicitly not a pruning claim. Its keystone is artifact exchangeability across calibre bands, `NOT_INSPECTED`, with the calibre dose-response and the non-vessel floor as the two Stage-0 gates, and with the null-by-parenchymal-correlate route above pre-registered as a named non-decisive outcome. The mirror LAA-950 fill arm belongs to that same candidate rather than to Idea 008, since Idea 008 has the identical missing-intervention problem and one operator serves both. Separately, the Stage-0 vessel-recovery probe on low-dose screening CT retains value as a standalone feasibility result about applying a free segmenter at these calibres, but only if the spin-off is funded; it is not worth running to answer a question nobody is now asking.

**Status:** CONCEDED

## Round 3 — CRITIC

**Position:** The proposer has conceded the decisive identity objection: no surviving experiment tests Idea 009's original claim that Sybil uses natural pulmonary vascular pruning and a Murray-exponent departure.

**Argument:** The concession is adequate because it rests on two substantive arguments, not repetition: first, the proposed calibre-band ablation estimates sensitivity to synthetic deletion of sub-5-square-millimetre vessel-like structures, which can diverge in either direction from reliance on naturally occurring pruning; second, the proposer identifies no obtainable dataset in which natural BV5 and branching-exponent variation can be separated from acquisition and parenchymal change while also supporting a model-reliance test. The NLST longitudinal scans change acquisition across years, the paired breath-hold corpus changes calibre and parenchymal density through respiration rather than rarefaction, and same-acquisition reconstruction pairs vary measurement rather than biology. The proposer also withdraws the Murray-exponent clause instead of presenting the narrower ablation as a repair, correctly recognizing that doing so would replace the candidate named in the title and deliverable. The proposed ablation may be registered separately at rung 1, but it cannot rescue Idea 009; no further objection to this now-conceded candidate is needed.

**What would change my mind:** A newly identified dataset and validated design showing independently measured natural within-patient variation in both BV5 and the pulmonary branching exponent, with acquisition and parenchymal change held sufficiently fixed, plus a model-reliance test tied to those changes rather than a score-phenotype association or synthetic deletion.

**Status:** CONCEDED

## Round 3 — PROPOSER

**Responding to:** The critic's round-3 summary of my concession — that no surviving experiment tests Idea 009's original claim, that the ablation diverges from the natural-variation claim in either direction, and that no obtainable dataset separates natural BV5 and exponent variation from acquisition and parenchyma while supporting a reliance test.

**Response:** CONCEDE

**Argument:**

The summary is accurate and I have no correction to it. I am closing rather than adding, and the only thing I owe the record is the disposition, stated precisely enough that a future cycle does not re-derive this debate from scratch.

**Disposition:** REJECT Idea 009 as titled. Not PAUSE. PAUSE would imply a blocked fact that correspondence or inspection could unblock, as with idea 002's annotation provenance. Nothing here is blocked in that sense: the observational route fails on estimand, not on access, and the interventional route fails on construct, not on compute. Both failures are properties of the question as posed against the data that exists, so the candidate does not become live by anyone answering an email or by a file turning out to contain what I hoped.

**Revisit trigger, and I adopt the critic's unblocking condition verbatim as it stands** — natural within-patient variation in both BV5 and the fitted exponent, acquisition and parenchymal change held sufficiently fixed, with a reliance test tied to those changes. I add one thing that is mine to add rather than the critic's: the exponent half of that condition also requires a measurement precision floor that the current human literature does not supply. Two studies totalling 23 subjects at 2.31 ± 0.60 and 2.92 ± 1.07 (PMID 40489106; PMID 32618514) do not establish that a within-patient change is resolvable, and a cohort-scale repeatability estimate on same-session repeat scans would be the cheapest way to find out whether the exponent limb is ever worth reopening on CT at all. Absent that, reopening on the exponent should be refused even if the dataset condition is met.

**One correction to my own round-2 text, since it will be read as ledger material.** I wrote that this is the fourth occurrence of the wrong-keystone pattern. The pattern is the same in shape but the failure is one step earlier than in ideas 005 and 006: those had a valid estimand and an invalid factual premise, whereas 009's premise about measurability was arguably fine and the *estimand* was never a reliance test. Recording it as a fourth wrong-keystone is right only if the ledger entry also says the keystone was mis-specified because the estimand was, not because the wrong fact was checked. Otherwise the lesson lands as "check harder" when it should land as "state the estimand before choosing the keystone."

Nothing further from me on this candidate.

**Status:** CONVERGED
