# Debate summary — idea 005

## Agreed

- Classical fixed-method Campbell–Fiske MTMM cannot treat LIDC's per-scan reader slots as persistent reader identities. The proposer dropped that framing in Round 2, and the critic accepted in Round 3 that exchangeable raters can in principle support characteristic-specific reliability estimation without persistent identity.
- The public ratings were assigned after readers had seen colleagues' anonymized marks and lesion categories, but not colleagues' subjective characteristic ratings. This primary-source timing evidence narrowed the peer-exposure channel in Round 2, and the critic accepted that narrowing in Round 3.
- The released opinions are nevertheless dependent: exposure to peer marks can affect both same-characteristic agreement and cross-characteristic association. Different-characteristic/different-reader cells therefore cannot cleanly rule out propagated impression. The proposer conceded this in Round 2.
- LIDC alone cannot identify why characteristics covary. Peer exposure, global impression, genuine morphological co-occurrence, and other common causes remain plausible. The proposer narrowed the causal claim in Round 2; no later round disputed that limitation.
- The Round 2 rule comparing a disattenuated latent correlation with the geometric mean of reliabilities was wrong. The critic demonstrated its perverse behavior in Round 3, and the proposer conceded and withdrew it in Round 4.
- A latent-correlation framework may estimate pairwise construct association after measurement error, but low reliability should produce uncertainty rather than an automatic discriminant-validity failure. The proposer adopted this position in Round 4, and the critic accepted the algebraic repair and relevance of the latent-correlation framework in Round 5.
- The Round 4 outcome rule was internally contradictory and used failure to reject as evidence of non-distinctness. The critic identified this in Round 5, and the proposer fully conceded it in Round 6.
- Pairwise nonrejected merges do not define a dimension count: merge relations may be nontransitive, overlapping merges cannot simply be counted, and multiplicity/model selection must be specified. The critic raised this in Round 5, and the proposer conceded it in Round 6.
- Confidence-interval width alone does not validate a dimension estimator. Relevant simulation would need false-merge and partition-recovery operating characteristics under realistic sparse marginals, reliability ranges, misspecification, and transitive and nontransitive structures. Agreed in Round 6.
- The original card's feasibility 5, decisive-negative classification, clarity 4, and priority score 4.05 are no longer defensible. The proposer explicitly withdrew them in Round 6.
- The original question's second half—how many distinct dimensions the vocabulary “really” has—has no defended estimand in this debate. A partition model, margin, handling of nontransitivity, and validated selection procedure would be required. The proposer conceded this in Round 6.

## Unresolved

### Can a narrower pairwise latent-correlation audit be scientifically useful?

- **Question:** Can the 28 characteristic pairs be classified as distinct, not distinct, or undecidable at a prespecified latent-correlation margin using exchangeable, peer-exposed LIDC ratings?
- **Proposer's position:** Round 6 records this as spin-off S1. A directional equivalence procedure with simultaneous intervals and multiplicity control might answer only the pairwise half of the original question.
- **Critic's position:** The critic required a mutually exclusive rule with an explicit null, direction, interval, margin, and multiplicity control, plus realistic simulations of its operating behavior (Round 5). The critic never reviewed the Round 6 sketch.
- **What evidence would settle it:** Verify the primary methodological basis for the equivalence rule; directly inspect LIDC cell counts, missingness, and marginal distributions; then preregister and simulate coverage, type-I error/false declarations, power, convergence, and misspecification sensitivity for the exact ordinal correlated-uniqueness model. This would establish statistical adequacy, not the substantive truth of a chosen margin. The margin itself is partly a value judgment and requires a clinically or model-evaluation-relevant justification.

### Can a global partition estimator recover a defensible dimension count?

- **Question:** Can selection over the 4,140 partitions of eight characteristics provide a validated global estimate of vocabulary dimensionality under ordinal exchangeable-rater data?
- **Proposer's position:** Round 6 records, but does not submit, a possible repair using categorical CFA over the partition lattice, a consistent information criterion, and partition weights.
- **Critic's position:** Round 5 required a validated global estimator with controlled false merges and correct-dimension/partition recovery under transitive and nontransitive structures. No response from the critic evaluates the recorded repair.
- **What evidence would settle it:** A fully specified estimator followed by simulations at realistic LIDC thresholds, reliabilities, sample size, dependencies, sparse cells, and misspecification, reporting false-merge and exact/near partition recovery. Under genuinely nontransitive latent structure, no partition may be true; the scientific meaning of forcing or weighting partitions would still require justification. The debate agrees this would become a substantial psychometric methods project rather than the proposed cheap audit.

### Are LIDC reader slots empirically exchangeable?

- **Question:** Do loading and threshold equality constraints across released reader slots fit well enough to justify treating slots as exchangeable?
- **Proposer's position:** Rounds 4 and 6 identify this as spin-off S2 and the most charter-compatible surviving question.
- **Critic's position:** The critic did not evaluate this spin-off. Earlier objections establish only that slots are not persistent identities, not whether their distributions are exchangeable.
- **What evidence would settle it:** Direct XML inspection followed by a prespecified invariance/exchangeability test with fit criteria, sensitivity to arbitrary slot ordering, sparse categories, missingness, and known annotation inconsistencies. Failure of equality would refute simple exchangeability; adequate fit would support, but not prove, the assumption.

## Positions that moved

- **Proposer, Round 2:** Dropped fixed-method Campbell–Fiske MTMM after the critic showed that reader slots are not persistent identities. Replaced it provisionally with an exchangeable-rater/random-facet approach. This concession was earned.
- **Critic, Round 3:** Accepted that the Round 2 primary-source timing evidence narrowed peer exposure because characteristic ratings were assigned only after exposure to colleagues' marks. Also accepted that exchangeable raters can in principle estimate characteristic-specific reliability. These movements were earned by new evidence and a narrower claim.
- **Proposer, Round 2:** Withdrew the claim that peer exposure is uniformly conservative and conceded that different-characteristic/different-reader cells cannot identify away propagated impression. Identifiability fell to at most 3, and causal negative results became sensitivity-limited. Earned by the Round 1 dependency argument.
- **Proposer, Round 4:** Conceded that the Round 2 reliability-based cutoff was algebraically wrong and unstable at low reliability. Replaced it with a cutoff-relative latent CFA proposal. Earned by the Round 3 numerical counterexample.
- **Critic, Round 5:** Accepted that Round 4 repaired the algebra error and that Rönkkö and Cho provided a relevant latent-correlation framework, while rejecting the proposed decision and dimension rules. Earned by the new source and revised estimand.
- **Proposer, Round 6:** Conceded all four Round 5 objections: non-rejection was misused, outcome labels overlapped, pairwise merges did not define a partition, and the proposed simulation did not validate the estimator. The proposer invoked the predeclared stopping rule and abandoned amendment of the original idea. Earned by specific new arguments; not UNEARNED.

## Amendments made

At round zero, the idea claimed that a classical MTMM matrix over four reader slots could test discriminant validity, that cross-reader/cross-characteristic cells controlled within-reader halo, and that polychoric factor analysis plus parallel analysis could yield a decisive number of latent dimensions in hours. It scored feasibility 5, identifiability 4, clarity 4, and negative-result value 4.

Round 2 replaced fixed readers with exchangeable raters, abandoned method-specific variance claims, and weakened the peer-exposure analysis from identification to an asymmetric falsification check. This lost causal attribution, reduced identifiability to at most 3, and made the causal negative sensitivity-limited.

Round 4 replaced the erroneous reliability cutoff and factor-retention approach with a categorical correlated-uniqueness CFA, cutoff-relative latent correlations, and nested merges. This increased the expected work from hours to roughly a week, made some characteristics potentially undecidable, and made any verdict cutoff-relative.

Round 6 withdrew that operationalization rather than amending it again. Consequently, **there is no surviving amended version of the original two-part study**. The pairwise equivalence audit, reader-slot exchangeability test, and partition-selection methods project are spin-offs only; each requires a fresh card and fresh scoring. The original dimension-count headline, decisive-negative claim, feasibility score, clarity score, and priority score are lost.

## Recommendation

**REJECT** the original idea as currently framed. The single most important thing for the human to inspect is whether to promote spin-off S2—the direct test of reader-slot exchangeability—into a fresh candidate, because it preserves the cheap public-data audit while avoiding the undefined dimension-count estimand.
