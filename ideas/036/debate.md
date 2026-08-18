# Debate transcript

## Round 1 — CRITIC

**Position:** The atlas-border discontinuity cannot identify use of an internal vascular map, because the registered border neither assigns a treatment nor separates atlas knowledge from real border-zone physiology and spatial priors.

**Argument:** The original question is a model-use claim: whether the model uses arterial-territory membership beyond case evidence. But the proposed estimand is only a conditional association between output and a population-atlas boundary. In a valid regression discontinuity, treatment changes at the cutoff and untreated potential outcomes are locally continuous; here the model is never given the atlas label, while true arterial border zones are biologically distinctive sites of distal perfusion, impaired embolus washout, and hemodynamic vulnerability (Momjian-Mayor & Baron, *Brain* 2005, DOI `10.1093/brain/awh366`). Matching released CBF, CBV, MTT, Tmax, and NCCT values cannot eliminate patient-specific collateral routes, arrival-curve shape, occlusion geometry, tissue history, or nonlocal receptive-field evidence. Moreover, Liu et al.'s atlas is a population map derived from infarct distributions, excludes exclusively watershed infarcts, and lacks angiographic confirmation for much of its construction cohort (Scientific Data 2023, DOI `10.1038/s41597-022-01923-0`); its boundary is therefore not an independently measured patient-specific supply boundary. Shifted-border placebos can reject generic edge effects, but cannot distinguish a memorized vascular map from ordinary spatial coordinates or genuine physiology at the true border. The strongest defensible amendment—an out-of-fold error audit in registered border-zone bands—would answer whether errors concentrate near atlas borders, not whether the model brings or uses a vascular map. Under the claim-identity rule that is a separate candidate, not a repair of idea 036.

**What would change my mind:** An obtainable cohort with an independently measured patient-specific perfusion-territory map that dissociates from the population atlas, together with held-out model predictions showing that output follows atlas membership rather than patient-specific supply after prespecified local and nonlocal evidence controls; alternatively, a valid intervention that changes the alleged internal territory variable while holding case evidence fixed and passes explicit intervention-validity gates.

**Status:** OPEN

## Round 1 — PROPOSER

**Responding to:** The registered atlas border assigns no treatment and is itself a site of real, incompletely measured vascular physiology, so a matched-pair output jump at that border cannot separate an internalized vascular map from evidence-driven behavior; the identifiable reformulation (an error audit by border distance) answers a different question and is a separate candidate under the claim-identity rule.

**Response:** CONCEDE

**Argument:** The objection is correct, and I can sharpen it rather than resist it. The card's gate battery — five-channel matching, placebo borders, contralateral borders, registration perturbation — passes in full under a null model with no internalized map. The mechanism: an evidence-driven model reads the occlusion site from CTA (a released model input) and infers the territory at risk downstream of it. That is territorial reasoning *from case evidence*, and it produces sharp output transitions at the patient's true supply boundary. Patient-specific supply boundaries cluster around the population atlas border, so across a cohort these evidence-driven transitions smear into exactly the predicted signature: an attenuated but real jump at the registered atlas line, larger there than at 5-10 mm shifted placebo borders (which align worse with the band of true boundaries), surviving matching because occlusion geometry is nonlocal and not among the matching channels. The card's "decisive" positive is therefore fully consistent with the absence of the claimed internal map. This is not an identifiability *ceiling*, as the card scored it; it is the estimand failing to contain the question — the x8 IDENTIFIABILITY_FAILURE pattern, and the card's `dies_like_prior` defense (matching handles watershed hemodynamics) does not hold because matching can only use released local channels.

The identity check settles the rest. Every repair that restores identifiability changes the deliverable sentence: the error audit delivers "errors concentrate near atlas borders" (association with labels, not use); a dissociation design delivers a claim about atlas-versus-patient-specific supply and requires an independently measured patient-specific territory map, which ISLES'24 does not contain and which cannot be inferred from the same CTA/CTP the model consumes without importing a second construct-validity problem. Neither is idea 036 wearing new gates; both are different studies. So I do not amend.

**Spin-off (endorsed, separate candidate per the claim-identity rule):** the critic's out-of-fold error audit — on strictly out-of-fold ISLES'24 predictions, do calibration and segmentation errors concentrate in registered arterial border-zone bands versus perfusion- and lesion-status-matched territory interiors? It keeps the medical motivation (spatial failure modes relevant to variant anatomy), uses only existing data, labels, atlas, and training code, and must never be narrated as a use claim.

**Revival condition for the original question:** an obtainable cohort with independently measured patient-specific perfusion territories (e.g., vessel-selective ASL or selective angiography) that dissociate from the population atlas, plus held-out predictions from the audited model on that cohort. Not available in ISLES'24; recorded so the revival machinery can act if such a cohort surfaces.

**Status:** CONCEDED

## Round 2 — CRITIC

**Position:** The original idea remains rejected because the proposer has shown that its atlas-border estimand cannot identify the claimed use of an internal vascular map.

**Argument:** The proposer's concrete null mechanism resolves the dispute: an evidence-driven model can read occlusion geometry from the released CTA, infer downstream risk from case-specific vascular evidence, and thereby produce a cohort-level jump near the population-atlas border while containing no atlas prior at all. That mechanism can survive the proposed five-channel local matching and outperform shifted-border placebos because the relevant occlusion geometry is nonlocal and true patient-specific supply boundaries cluster nearer the atlas line than arbitrary offsets. Thus the full positive-result pattern is compatible with the negation of the deliverable sentence. The proposer also correctly applies the identity check: the endorsed out-of-fold border-zone error audit measures spatial error concentration, not internal map use, so it is a separate candidate and cannot repair idea 036. There is no amendment to assess and no remaining technical objection worth adding; the fatal identifiability objection has been conceded on substantive mechanistic grounds.

**What would change my mind:** The stated revival condition: held-out predictions on an obtainable cohort with independently measured patient-specific perfusion territories that dissociate from the population atlas, or a validated intervention on the alleged internal territory variable that holds case evidence fixed.

**Status:** CONCEDED

## Round 2 — PROPOSER

**Responding to:** The critic's round-two closure: the concession is accepted on its mechanistic merits, no amendment exists to assess, and the debate is over.

**Response:** CONCEDE

**Argument:** The concession stands and nothing new has emerged to qualify it; per the rules, a round without new argument or evidence is a concession, and I will not decorate a settled position. The record the decision stage needs is already complete in the two round-one entries: kill code IDENTIFIABILITY_FAILURE (the ninth under this charter — the positive-result pattern is producible by an evidence-driven model with no internal atlas); the out-of-fold border-zone error audit endorsed by both sides as a spin-off that must enter as a new candidate through the normal scouting path with parent_id idea-036, never narrated as a use claim; and the revival condition (independently measured patient-specific perfusion territories that dissociate from the population atlas, or a validated intervention on the internal territory variable holding case evidence fixed) recorded for the revival machinery. Recommended verdict for the ledger: REJECT.

**Status:** CONVERGED
