# Confer review — idea 023, q0001 (opposing family)

Reviewed: draft answer to the operator question "Can you give me an overview
and analysis of what happened with our last experiment for this idea? Why
were the combination of factors we looked at not predictive of tissue
death?" Evidence set: CARD.md (dd5c6ea63c9a), interpretation.md
(775b28c582be), interpret_review.md (466f1f7abe1e), decision.md
(495d76e70ea4).

## 1. Thesis

Correct. The draft's core answer has three load-bearing legs, and each one
holds against the evidence:

- The preregistered three-band gate failed on directional consistency —
  signs (+, −, +), with the two zero-excluding intervals pointing in
  opposite directions — and this was the contract's decisive
  NEGATIVE_PATTERN, not a power or precision failure (99 patients per band
  vs floor 20; max CI width 0.0652 vs limit 0.15). Matches interpretation.md
  Demonstrates item 2 and decision.md Layer A/Layer B item 4.
- No prediction model existed or was probed; the model-use probe was
  contingent on this gate and did not run. Matches interpretation.md
  Out-of-scope warnings, Does not establish, and Next decision.
- The idea is PAUSED per the contract's negative_pattern; CARD.md records
  the ratified PAUSED status. Matches decision.md Verdict and CARD.md
  Interpretation and authority.

The draft's causal stance — the immediate statistical reason (sign reversal
across flow bands) is resolved, the underlying cause is not, and
heterogeneity plus tissue-composition imbalance are named but unproven
candidates — is exactly the evidence's own position.

## 2. OVERVIEW fidelity

Faithful. I checked each OVERVIEW sentence against the DETAILS it
compresses:

- "One flow band showed essentially no relationship, while the other two
  showed small but clear relationships in opposite directions" — matches
  band 1 (CI includes zero) and bands 2/3 (CIs exclude zero, opposite
  signs, magnitudes 0.032 and 0.023). "Small but clear" is acceptable at
  the mean level given the tight intervals; the DETAILS section carries the
  near-zero-median / heterogeneity qualifier that keeps this from
  overstating a cohort-wide effect, and the OVERVIEW's second paragraph
  itself flags heterogeneity as unresolved.
- "Paused the idea before any model was examined" — correct and correctly
  scoped.
- The OVERVIEW's refusal to endorse "not predictive" mirrors the premise
  check and the evidence's Does-not-establish list; no overstatement or
  understatement introduced by the compression.

## 3. Citations

All resolve. Every quantitative claim in the draft matches the evidence to
the stated rounding: case counts 99/100/149/49; band means, CIs, and widths
(+0.0064 [−0.0268, +0.0384] w 0.0652; −0.0320 [−0.0559, −0.0080] w 0.0479;
+0.0231 [+0.0050, +0.0436] w 0.0386); medians 0.0 / −0.000589 / +0.000556;
identity residuals 0.007761 / 0.003560 / 0.007788 vs limit 0.10; support
floor 20 and width limit 0.15; 594 HU-audit rows; sub-stroke0092 band-1
medians 3.0/23.0 HU; exclusions sub-stroke0043 (source_corrupt_member) and
sub-stroke0142 (duplicate lesion member, case retained). Section-level
citations into interpretation.md and decision.md point at sections that say
what the draft attributes to them. Note that interpret_review.md
independently re-verified these same bundle values (round-2 APPROVE), so
the draft's transcriptions are double-attested.

## 4. Premise check

Fired, and warranted. The operator question presupposes that the
experiment tested predictiveness and returned "not predictive." Both halves
of that premise conflict with the evidence: (a) no model was trained or
probed — the experiment was an association census gating a future model-use
probe; (b) the result was not "no outcome information" but a directionally
inconsistent association under one operationalization, with two bands
showing zero-excluding effects in opposite directions. The draft names both
conflicts, cites them, and then still answers the corrected question rather
than stopping at the correction. Not spurious.

## 5. Claim bounds

Nothing exceeds the evidence. The draft stays inside every prohibition the
artifacts impose: no cohort prevalence claim for HU imbalance (row-level
examples only, prevalence explicitly "not calculated"), no per-patient
contribution claim, no CBV-vs-MTT channel attribution (degeneracy cited),
no physiological/autoregulatory language, no model-use claim, no statement
about reserved cases or other cohorts/pipelines. The tissue-composition
discussion is presented as a bounded concern that "cannot establish that
this caused the gate failure cohort-wide," matching the labeled INFERENCE
and its bounds in interpretation.md Suggests item 3.

## 6. Question coverage

Complete. "Overview and analysis of what happened": delivered — design,
provenance, exclusions, gate definition, per-band results, gate failure
class, and the PAUSE outcome. "Why not predictive": the premise is
corrected, the answerable layer (statistical reason: sign reversal across
flow bands) is answered, and the unanswerable layer (physiological or
data-generating cause) is explicitly declared unresolvable from the
evidence, with the two candidate explanations named and the specific
successor analyses that would resolve each one identified in OPEN
UNCERTAINTIES. No assumption is papered over.

## Verdict

The draft is a faithful, correctly bounded, fully cited answer whose
premise correction is exactly what the evidence requires. No meat-level
defects found.

```json
{"verdict": "CONCUR", "findings": []}
```
