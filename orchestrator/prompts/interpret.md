Interpret the probe strictly against `probe_contract.yaml`. Separate:

- demonstrates;
- suggests;
- does not establish;
- validity failures;
- positive and negative findings;
- next decision.

Do not turn an exploratory probe into a confirmatory claim. Report every authorized variant. Write `decision.md` and append a scoped entry to evidence/decisions.md. End with ADVANCE, REVISE, PAUSE, or REJECT.

## Single-seed constraint

Probes run with `maximum_seeds: 1` by default. With one seed you cannot
distinguish a real effect from seed noise. Therefore:

- You may write DEMONSTRATES only for outcomes that do not depend on an
  effect size (e.g. the pipeline ran, the data loaded, a hard constraint
  was violated).
- Any claim about a metric moving is at most SUGGESTS, and must name the
  seed count as the reason it is not stronger.
- Never output CONFIRMED from a single seed. If the result looks worth
  confirming, put "repeat with >=3 seeds" as the next decision.
