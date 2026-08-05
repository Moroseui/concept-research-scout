# Debate summary — idea 003

## Agreed

- BrEaST's mixed reference standards create verification bias in a full-cohort descriptor-versus-category comparison: lower BI-RADS categories may be follow-up verified, while suspicious categories generally receive histology. A precise performance estimate would not by itself remove that bias (rounds 1–2).
- A BrEaST analysis would need to make the biopsy-verified subset primary, treat the full cohort as secondary, narrow conclusions to the biopsied spectrum, and avoid interpreting a near-tie as equivalence. The critic accepted this as an adequate small-study response to the original verification objection (rounds 2–3).
- Performance of a fitted descriptor decoder is not an information-theoretic measure of the descriptor vocabulary. Decoder capacity, coding, regularization, and limited sample size can make descriptors appear worse than their latent utility warrants (rounds 3–4).
- Any standalone BrEaST comparison should therefore be framed as a comparison of prespecified prediction rules, not as a descriptor-information ceiling or upper bound. It should use a small preregistered decoder set, symmetric development-only tuning, identical frozen test cases, and a descriptor learning curve (round 4; retained in round 6).
- The amended BrEaST prediction-rule study does not test concept intervention. It contains no image-predicted concepts, intervention-selection policy, or paired pre/post-intervention predictions, and therefore cannot estimate intervention benefit, burden, robustness to imperfect correction, or correction-induced distribution shift (rounds 5–6).
- The original Idea 003 cannot be executed with the public assets identified in the critique and debate: BUS-BRA lacks released descriptor labels, the target development cohort is unavailable, and no public reader-correction data were identified for the "realistic clinician behaviour" claim. Failure to identify such data is not proof that none exist (round 6).
- The original title, rationale, scores, and medical-relevance claims cannot be transferred to the residual BrEaST benchmark. If pursued, that benchmark must become a separately identified and independently scored candidate with no authority to stop or validate intervention work (round 6).

## Unresolved

### Does a suitable public intervention dataset or checkpoint exist but remain unidentified?

- **Question:** Is there a public resource with image-level BI-RADS descriptors and adequate outcomes that supports image-predicted concepts and observable pre/post-intervention policies, ideally with reader corrections or disagreements?
- **Proposer's position:** No such resource was identified, so the original question is not presently answerable; this is explicitly not a claim that no such resource exists (round 6).
- **Critic's position:** The intervention claim could be restored if such a feasible public-data experiment were identified and its sample size and concept-label quality shown adequate (round 5).
- **What evidence would settle it:** A focused primary-source and repository search yielding a publicly accessible dataset, usable checkpoint, or reader study with the required descriptor, outcome, and intervention/correction information, followed by direct inspection of its files, license, patient independence, label provenance, and sample counts. A search finding nothing would justify pausing on current evidence, but would not prove global nonexistence.

### Are the factual prerequisites for the separate BrEaST benchmark satisfied?

- **Question:** Does the released case table confirm that every malignant case is biopsy verified, and is the relevant Bunnell concept-to-label head actually linear as assumed in round 4?
- **Proposer's position:** The primary data descriptor supports the claimed counts and verification pattern, but the released XLSX cross-tabulation and exact head parameterization still require direct checks (rounds 2 and 4).
- **Critic's position:** The critic accepted the verification amendment provisionally and did not contest the residual benchmark once it was separated from intervention, but did not waive these checks (rounds 3 and 5).
- **What evidence would settle it:** Directly inspect the released XLSX and report the `Verification` × `Classification` × `BIRADS` cross-tabulation; directly inspect the primary paper or official implementation for the strict model's concept-to-label head. These checks affect a future standalone candidate, not the rejection of Idea 003.

## Positions that moved

- **Proposer, round 2:** Conceded the critic's verification-bias objection for the full cohort. In response, moved the primary analysis to the biopsy-verified subset, demoted the full cohort to robustness analysis, added a tipping-point sensitivity analysis, narrowed the population, acknowledged lower power, and dropped the claim that the study was decisive.
- **Critic, round 3:** Accepted that the round-2 changes adequately addressed the original verification objection at the scale of a small study. This was earned by the new primary subset, narrower claim, and proposed sensitivity analysis.
- **Proposer, round 4:** Conceded that decoder performance cannot establish descriptor information content. In response, reframed the estimand as a comparison of named prediction rules, added three preregistered decoders and symmetric fitting, added a learning-curve gate, made the stop rule conjunctive, and removed all information-ceiling language.
- **Proposer, round 6:** Conceded the critic's argument that the amended experiment had left the causal path of concept intervention. The proposer rejected the original Idea 003, withdrew the intervention-based medical relevance and scores, and separated the residual BrEaST benchmark into a possible future candidate.
- No concession was unearned. Each movement followed a new, specific objection or new evidence, and the final convergence occurred only after six rounds rather than in a single objection-free round.

## Amendments made

At round zero, Idea 003 claimed it could test whether BI-RADS concept intervention remains useful under partial, noisy, clinician-selected correction and whether it beats the radiologist's BI-RADS category, using a retrained breast-ultrasound CBM and public data.

The first amendment replaced that intervention experiment with a BrEaST descriptor-versus-category analysis centered on the biopsy-verified subset, with the mixed-reference full cohort relegated to sensitivity analysis. This lost applicability to an unselected diagnostic population, reduced power, and abandoned the claim of a decisive upper bound.

The second amendment further narrowed the study to a comparison of prespecified prediction rules on BrEaST. It removed claims about representation information, added multiple decoders and learning-curve safeguards, and made any downstream stopping rule difficult to trigger. This lost most of the original screening power and broader generalizability.

The final concession recognized that even this amended study does not evaluate intervention. The original idea is therefore not merely revised: it is rejected. The remaining BrEaST benchmark is a different candidate and must not inherit Idea 003's title, intervention rationale, scores, or claimed negative-result value.

## Recommendation

**REJECT.** The current public-data plan cannot answer the motivating intervention question, and the successive defensible amendments produced a different prediction-rule benchmark. Before deciding whether to revive the intervention idea, the human should look first for a directly verified public dataset or checkpoint that supports image-predicted BI-RADS descriptors and observable pre/post-intervention evaluation; without that asset, further design refinement will not repair the core feasibility gap.
