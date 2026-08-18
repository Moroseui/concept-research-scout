<!-- stage: feasibility -->
Verify whether the selected idea is actually feasible. Use primary sources and official dataset documentation.

Check:
- closest work and exact gap;
- dataset access and license;
- label availability and concept validity;
- sample structure and likely split unit;
- existing code/checkpoints;
- compute estimate;
- accepted baselines and metrics;
- critical leakage and confounds;
- the smallest probe of the riskiest assumption.

Write `feasibility.md` plus updates to evidence/literature.csv and evidence/datasets.csv. Mark anything not verified. End with GO, REVISE, PAUSE, or NO-GO. Do not write code.

## Closing section: "In plain terms" (required)

End the memo with `## In plain terms`: can this be done, what it
would cost, and the single biggest practical risk - three to five
sentences a non-specialist could follow, claiming nothing the memo
does not. If the idea depends on a data-manipulation or intervention
mechanism (editing inputs, perturbing maps, synthesizing cases), the
memo body MUST also contain a prior-art subsection: named published
methods that performed comparable manipulations, and a concrete
stay-in-distribution strategy with numbers. Absence of workable
precedent is a legitimate feasibility failure and must be stated as
such rather than papered over.
