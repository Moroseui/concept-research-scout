Interpret the probe strictly against `probe_contract.yaml`. Separate:

- demonstrates;
- suggests;
- does not establish;
- validity failures;
- positive and negative findings;
- next decision.

Do not turn an exploratory probe into a confirmatory claim. Report every authorized variant. Write `decision.md` and append a scoped entry to evidence/decisions.md. End with ADVANCE, REVISE, PAUSE, or REJECT.

## Uncertainty constraint (match the constraint to the randomness source)

First identify where the probe's uncertainty actually lives, then apply
the matching rule. Applying the wrong rule under-claims or over-claims
for the wrong reason.

**Stochastic procedures** (training runs, random initialization, sampled
augmentation, stochastic optimization): probes run with
`maximum_seeds: 1` by default, and one seed cannot distinguish a real
effect from seed noise. Therefore:

- You may write DEMONSTRATES only for outcomes that do not depend on an
  effect size (e.g. the pipeline ran, the data loaded, a hard constraint
  was violated).
- Any claim about a metric moving is at most SUGGESTS, and must name the
  seed count as the reason it is not stronger.
- Never output CONFIRMED from a single seed. If the result looks worth
  confirming, put "repeat with >=3 seeds" as the next decision.

**Deterministic procedures** (frozen-checkpoint inference with
demonstrated bit-determinism): there is no training-seed uncertainty and
the seed rule above does not apply. Uncertainty lives at the case level
— which patients/scans/pairs were measured. Therefore:

- Judge effect claims against the contract's case-level uncertainty
  machinery (e.g. patient-cluster bootstrap intervals, preregistered
  strata), not against seed count.
- A metric claim without the contract's case-level uncertainty
  quantification is at most SUGGESTS, and must name the missing
  uncertainty treatment as the reason.
- Sample-size and coverage limits (n per stratum, vendor scope) still
  bound every claim and must be stated.

## Citation mandate (results-bundle probes)

When the idea's probe produced a results bundle (probes/NNN/results_v2
or an imported bundle under probes/NNN/results/), every quantitative
claim you make MUST carry an inline citation resolving to the exact
place the number lives, in this form:

    [cite: analysis/tier1_stats.csv | stratum=Bl56f|Br40f,
     head_name=Pleural effusion, scale=probability | q90_abs]

(file relative to the bundle root | row selector as column=value pairs
| column). A number without a citation, or with a citation that does
not resolve to that number, is a blocking defect: a cross-family
reviewer will open the files and check every citation by hand. Do not
round beyond the precision needed for the sentence; state the value as
cited.

Claim discipline inherited from the contract, restated as hard rules:
no threshold, cutoff, margin, or pass/fail language for tier 2
(benchmark context may be CITED for scale, never used to judge); no
cross-head or cross-stratum averaging that the analysis files do not
themselves contain; vendor scope and the anchor-pair exclusion stated
wherever counts appear; the result is a reconstruction-sensitivity
baseline for this checkpoint on these contrasts, never a universal
measurement floor. Write the interpretation to `interpretation.md` in
the idea folder BEFORE writing decision.md; decision.md then summarizes
it. Do not append to evidence/decisions.md until the interpretation has
passed review (the interpret-build loop tells you which round you are
in; in round 1 write interpretation.md and decision.md only).
