# Debate summary — idea 004

## Agreed

- **Stage 0 cannot estimate benchmark-interval inflation from labels and cluster sizes alone (Round 1).** Both sides agree that duplicated label rows describe the release structure but do not identify the sampling variance of AUROC or another score-based performance statistic. The simple `1 + (m-1)rho` design-effect formula is not valid for this use, and label ICC is not a proxy for dependence in model errors or estimator influence values.
- **The metadata-only stage is a linkage and feasibility audit (Round 1).** It may count reconstruction groups, check within-scan duplication of labels and reports, enumerate metadata contrasts, reconcile the reported validation patient counts, and confirm access. Any benchmark-precision analysis requires per-volume ClassFine outputs, either released or regenerated.
- **Reconstruction-, scan-, and patient-weighted analyses are different estimands (Round 1).** A difference between them is not automatically numerical bias. The revised benchmark arm must name each estimand and use a scan- or patient-clustered procedure appropriate to it, with patient-level resampling as the outer unit when patients contribute multiple scans.
- **The identical-file rerun tests software determinism only (Round 2).** It does not rule out deterministic effects of resampling, cropping, padding, or other preprocessing triggered by different source geometries.
- **Causal reconstruction-content language must be restricted (Rounds 2–3).** Geometry-matched pairs may support a reconstruction-content interpretation when the relevant preprocessing inputs and transformations are identical. All other pairs estimate end-to-end pipeline repeatability under composite released reconstruction variants. Kernel-specific attribution is unavailable unless the metadata isolate that contrast.
- **The revised design retains the original paired-score measurement (Rounds 2–3).** Both sides accept that measuring score changes from the frozen released checkpoint and preprocessing across same-acquisition reconstruction variants remains the core study, even though its interpretation and summaries have narrowed.
- **A pooled ICC cannot establish clinically or operationally meaningful repeatability (Round 3).** ICC is demoted to a descriptive statistic because it can be dominated by between-scan heterogeneity, can mislead for rare findings, and does not match the unequal and inconsistently named reconstruction structure well enough to carry an equivalence claim.
- **Primary stability analysis must use paired score changes with prespecification (Round 3).** The revised plan reports paired-difference distributions, a repeatability coefficient or upper quantile of absolute change, reconstruction-contrast strata, score-region strata, and probability- and logit-scale results with the margin's scale declared in advance.
- **Thresholds may not be selected on the audit pairs (Round 3).** Threshold-crossing rates are secondary and require thresholds estimated from sufficiently numerous singleton validation scans or, failing that, the training split. Underpowered outputs must be labelled exploratory using a prespecified independent positive-scan rule.
- **A reassuring result is decisive only against a justified, powered equivalence margin (Round 3).** Without that margin, a null is sensitivity-limited. The unsupported `ICC > 0.95` and “low-single-digit” flip-rate cutoffs are abandoned.
- **The benchmark-dependence and score-stability arms answer different questions (Round 3).** Patient-clustered intervals assess dependence and weighting; paired-difference margins assess reconstruction stability. Neither substitutes for the other.

## Unresolved

There is no remaining proposer–critic disagreement about the revised design. The unresolved items are empirical gates accepted by both sides:

### Do enough geometry-matched same-acquisition pairs exist?

- **Question:** Are there enough pairs sharing slope, intercept, XY spacing, Z spacing, and array shape—and carrying interpretable reconstruction contrasts—to support the primary mechanistic stratum?
- **Proposer's position:** Make this stratum primary for reconstruction-content attribution; if it is empty or too small, retain only the composite end-to-end pipeline analysis.
- **Critic's position:** Accepted in Round 3 as an adequate repair to the preprocessing objection.
- **Evidence that would settle it:** Direct counts and parameter comparisons in `validation_metadata.csv`, followed by a power or precision calculation for the paired endpoints.

### Are audit-independent thresholds estimable?

- **Question:** Are singleton validation scans numerous enough, per output, to estimate stable operating thresholds without using the paired audit cases?
- **Proposer's position:** Use singleton validation scans; fall back to training-split thresholds if the singleton group is inadequate.
- **Critic's position:** Thresholds must be fixed independently of the audit pairs; this repair satisfies that requirement in principle.
- **Evidence that would settle it:** Counts of singleton scans and independent positive/negative cases per output, plus prespecified threshold-estimation precision criteria.

### Are per-output analyses adequately powered?

- **Question:** Do the paired data contain enough independent positive and negative scans for confirmatory per-output repeatability, crossing-rate, and AUROC analyses?
- **Proposer's position:** Apply a prespecified minimum-count rule and mark failures exploratory.
- **Critic's position:** Accepted; rare outputs cannot support confirmatory claims merely because all 18 heads are available.
- **Evidence that would settle it:** Direct label and grouping counts, followed by minimum-detectable-effect or confidence-width calculations for each planned endpoint.

### Can the benchmark-precision arm be run without large-scale inference?

- **Question:** Do released per-volume ClassFine scores or logits exist and correspond exactly to the frozen checkpoint and validation files?
- **Proposer's position:** Search for released artifacts first; if absent, re-cost the study as gated image access plus inference.
- **Critic's position:** Scores are indispensable for the precision claim, whether released or regenerated.
- **Evidence that would settle it:** Direct inspection of official repository artifacts, model outputs, or author-provided files; otherwise successful unchanged-pipeline inference on accessed validation volumes.

### What equivalence margin is scientifically defensible?

- **Question:** What paired-score or reconstruction-swap AUROC change is small enough to count as operationally equivalent?
- **Proposer's position:** Anchor the primary consequence margin to published between-method AUROC gaps on the same validation split, fixed before examining paired differences; use independently derived thresholds for secondary crossing rates.
- **Critic's position:** A margin must be tied to an observable consequence and fixed before the audit; the proposed anchor is compatible with that demand but has not yet been demonstrated or justified numerically.
- **Evidence that would settle it:** Direct inspection of the cited benchmark tables, a written margin rationale fixed before score inspection, and confidence intervals showing whether the paired effect lies inside that margin. The choice of how consequential a benchmark gap must be also contains a value judgment; data can quantify the gap but cannot alone decide its importance.

## Positions that moved

- **Proposer, Round 1 — earned concession.** In response to the critic's estimator-specific argument, the proposer withdrew the claim that labels and cluster sizes alone yield the factor by which per-volume confidence intervals are too narrow. The proposer explicitly acknowledged conflating cluster structure with the variance of AUROC and moved all precision claims behind model outputs.
- **Proposer, Round 2 — earned partial concession and amendment.** In response to the critic's distinction between stochastic rerun noise and deterministic geometry-dependent preprocessing, the proposer withdrew the claim that an identical-file rerun rules out preprocessing and abandoned unqualified “reconstruction-induced,” kernel-specific, and content-specific language for the full corpus. Inspection of the released preprocessing code then supported the geometry-matched primary stratum and composite interpretation elsewhere.
- **Critic, Round 3 — position moved after new evidence and repair.** The critic accepted that the Round 2 amendment adequately narrows the preprocessing claim and preserves the study's identity. This followed the proposer's direct inspection of the released preprocessing implementation and explicit restriction of causal attribution.
- **Proposer, Round 3 — earned concession and amendment.** In response to the critic's variance-ratio and threshold-selection arguments, the proposer demoted ICC to descriptive status, struck the unsupported numerical reassurance criteria, accepted independent thresholds and equivalence margins, and made paired-difference and consequence-based analyses primary.
- **No concessions were unearned.** Each movement answered a specific objection or newly inspected implementation detail; none was mere capitulation.

## Amendments made

- **Stage 0:** Now a metadata, linkage, provenance, access, and feasibility audit. It no longer promises a label-only design effect or a no-model estimate of confidence-interval narrowing.
- **Benchmark arm:** Now requires per-volume scores, explicitly separates reconstruction-, scan-, and patient-weighted estimands, and compares row-level resampling with scan- or patient-clustered inference without prespecifying the direction of change.
- **Repeatability claim:** Now concerns within-acquisition reconstruction or end-to-end pipeline repeatability, not test-retest reliability across repeated acquisitions and not general concept validity.
- **Causal interpretation:** Reconstruction-content attribution is limited to adequately sized geometry-matched strata. Geometry-mismatched pairs retain a composite pipeline estimand; matched-grid transformations are secondary, asymmetrically interpreted mechanistic checks rather than definitive subtraction controls.
- **Primary statistics:** Paired score-difference distributions, repeatability coefficients or upper absolute-difference quantiles, and reconstruction-swap AUROC deltas replace pooled ICC as the main evidence. Analyses are stratified by reconstruction contrast and score region and reported on declared probability/logit scales.
- **Threshold analysis:** Crossing rates are secondary, with thresholds estimated away from audit pairs and outputs failing minimum-count criteria labelled exploratory.
- **Negative result:** No fixed reassuring cutoff is claimed. A negative is decisive only if confidence bounds fall within a prespecified, powered margin; otherwise it is sensitivity-limited.
- **Cross-domain claim:** The psychometric/QIBA borrowing now contributes within-subject variance, repeatability reporting, stratification, and advance margins. The general attenuation ceiling and claims that downstream correlations become “impossible” are lost.
- **Medical scope:** The study audits a released research model and benchmark. It no longer treats stable outputs as validated concepts or unstable outputs as direct proof that clinicians cannot act on the finding.
- **Cost and value lost:** The original one-afternoon headline result disappears unless validation scores are already released. Geometry stratification reduces sample size, the reliability coefficient is no longer the headline, the anticipated result loses its numerical form, and the revised card is materially narrower and potentially more expensive.

## Recommendation

**REVISE.** The debate converged on a defensible design, but the current idea card still contains claims and scores that the debate explicitly withdrew. Before deciding whether to advance to a feasibility memo, the human should look first at the direct Stage 0 metadata counts—especially the number and parameter makeup of geometry-matched same-acquisition pairs—because that single inspection determines whether the stronger reconstruction-content study exists or only the narrower composite pipeline audit remains.
