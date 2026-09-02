# Debate summary — idea 047

## Agreed

- The candidate has two claim-bearing clauses: an aggregate clinical description of the frozen top ten versus the other 89 cases, and a comparison of contribution dominance with an imaging-support quantity. Deleting the second clause would not answer the registered question (round 1).
- The original burden formulation was not reproducible. Exact eroded Tmax>6 s volume is absent from the imported tables, and the proposed residual of `|c_i|` on burden left the burden definition, model form, scale, and leverage handling open (round 1).
- The in-repository candidate burden variable is `S_i`, the sum across all three flow bands of `q1_voxels + q4_voxels`, honestly named **eligible extreme-quartile support**, not deficit volume. Its provenance and its relation to total eligible support must be verified from the frozen take-13 implementation before phenotype rows are opened; if that check fails, exact eligible support must be recomputed from the 99 Tmax maps under the ratified region machinery (round 1).
- No fitted-residual subgroup should be created. The clinical group remains the already frozen signed-rank top ten; the burden analysis is continuous and descriptive (round 1, retained through round 3).
- Random-ten-subset permutation inference is invalid here. The top ten were deterministically selected by signed contribution from a complete 99-case census, so random subsets are not licensed by the design and selection on contribution mechanically favors extreme contribution ranks (round 2).
- The burden clause is a finite-population description of these 99 realized cases, with no sampling uncertainty, hypothesis test, threshold, or claim that the pattern generalizes to new patients. The full rank-discrepancy distribution and Spearman correlation may be displayed descriptively (round 2).
- The sole burden-disproportionality comparison is the top ten's share of total absolute contribution, `sum_head |c_i| / sum_all |c_i|`, beside their share of total eligible support, `sum_head S_i / sum_all S_i` (round 3).
- The 79.29% net signed-gap share remains only as a separately labeled lineage/accounting statistic. Because 39 cases contribute in the opposite direction, cancellation affects its denominator; neither that statistic nor its difference from support share may be interpreted as contribution per unit support (round 3).
- These repairs preserve the candidate's identity: the frozen cohort, top-ten membership, clinical clause, and burden-proportionality clause remain, while the latter receives a valid operational definition (rounds 2 and 3).

## Unresolved

There is no remaining disagreement between proposer and critic at the close of round 3. Two factual implementation gates remain:

### Does eligible extreme-quartile support validly proxy the estimator's total eligible support?

- **Proposer's position:** `S_i` should be an approximately 50% deterministic fraction of total eligible support if Q1 and Q4 are the within-band per-case quartiles produced by the frozen take-13 code.
- **Critic's position:** The critic accepted this operational path subject to the specified provenance check; the debate did not independently establish the code fact.
- **What evidence would settle it:** Inspect the frozen take-13 implementation and reproduce the derivation from the 297-row `per_patient.csv`. If the relationship fails, selectively restage the 99 Tmax maps and recompute exact eligible support with the ratified region machinery.

### Which released clinical fields and time points are actually usable?

- **Proposer's position:** The debate leaves intact the critique's requirement to inspect only `clinical_data-description.xlsx`, then freeze the exact variable names, time points, coding, missingness rules, and short analysis list before opening case-level phenotype rows.
- **Critic's position:** Admission NIHSS must not be treated as interchangeable with the lineage's previously named 24-hour NIHSS, and conditional additions such as “treatment fields if present” are not a frozen plan.
- **What evidence would settle it:** A dictionary-only schema inventory followed by a frozen specification. The later D3-restricted staging of the 99 phenotype rows settles completeness and usable sample sizes.

## Positions that moved

- In round 1, the proposer conceded that exact deficit burden was not already available, the residual analysis was underspecified, a clinical-only repair would change the question, and the original “~50 kB, under five minutes” statement understated acquisition and staging cost. This was earned by the critic's concrete inventory and specification argument.
- In round 2, the proposer withdrew the random-subset permutation null and permutation interval after the critic showed that the top ten are outcome-selected and nonexchangeable and that the rank statistic partly rewards its own selection rule. This was an earned concession based on a new inferential objection.
- In round 3, the proposer demoted net signed share from the burden comparison and adopted absolute-contribution share after the critic identified denominator cancellation from the 39 opposing cases. This was an earned concession based on a new measurement objection.
- No concession was unearned.

## Amendments made

At round zero, the idea proposed two top-ten-versus-rest contrasts, called the imaging quantity deficit burden, used an unspecified residual of `|c_i|` on burden to create a second “disproportionality top-decile,” proposed permutation tests and binary proportionate/keystone-like language, and connected the 79.29% net signed share directly to burden disproportionality.

The amended idea keeps one frozen clinical group: the ten largest signed contributors versus the other 89. Before phenotype access, it defines `S_i` from the existing label-blind extreme-quartile support counts, subject to code verification and an exact-map contingency. For these 99 cases, it compares the top ten's absolute-contribution share with their eligible-support share; it may show casewise rank discrepancies and Spearman correlation descriptively. The 79.29% signed-net statistic is reported separately as reversal accounting. The clinical output is an aggregate estimation table with uncertainty and missingness, not a significance-selected or clinically explanatory verdict.

What is lost is the fitted residual subgroup, inferential calibration for the burden clause, generalization beyond the realized 99 cases, the phrase “deficit burden” for the proxy, the clinical-versus-imaging dichotomy, and the ability to use the dramatic 79.29% statistic as evidence of burden-disproportionate dominance. End-to-end cost must include dictionary inspection and restricted archive staging, and possibly map restaging.

## Recommendation

**REVISE.** The debate resolved its scientific objections, but the current `idea_card.json` still contains the superseded residual subgroup, permutation-null language, conditional clinical fields, understated cost, “clinically silent” framing, and the cancellation-confounded use of the 79.29% statistic. The single most important thing for the human to inspect is whether the frozen take-13 code establishes that `S_i` is the claimed deterministic proxy for total eligible support; that check determines whether the low-cost in-repository path is valid or exact support must be recomputed from maps.

## In plain terms

This idea asks whether the ten cases that contribute most to a previously observed stroke-imaging pattern look clinically different from the other 89 cases. It also asks whether those ten contribute unusually much relative to the amount of eligible image support they contain.

The debate concluded that the question is worth retaining, but the original analysis was not validly specified. The revised version uses exact descriptive shares for these 99 cases, avoids an unjustified statistical test, and keeps the cancellation-sensitive 79.29% figure separate from the burden comparison. The card must be rewritten before the study advances.

The human is being asked to check whether the proposed support count really has the relationship to total eligible support claimed from the frozen earlier pipeline.

```json
{"verdict": "REVISE", "unblock": "Rewrite the card to the round-3 finite-population design and verify from the frozen take-13 implementation that S_i is the claimed proxy for total eligible support, otherwise freeze the exact-map recomputation branch."}
```
