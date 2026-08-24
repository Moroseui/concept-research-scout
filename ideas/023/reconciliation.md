# Reconciliation audit — idea 023

## Scope and charter comparison

All archived stage prompts required by this audit are present and readable:
`prompt_critique.md`, six round-specific debate prompts,
`prompt_debate_summary.md`, `prompt_revise.md`,
`prompt_keystone_screen.md`, and `prompt_feasibility.md`.

Their injected charter sections are identical to one another (the extracted
sections have the same SHA-256,
`190a2a5c425368df89f36a094c03113f04b6ce83faf6ac5958c80d627c0e411d`) but
diverge from the current `charters/isles24/CHARTER.md`. The archived prompts
contain the baseline program to decode signals used by medical-imaging models,
including the mandatory physician-readable “the model is using X” deliverable,
the three-rung framework, and the hard rule that X be measurable without a
human annotator. The corrected charter instead makes ISLES'24 the program
driver, admits a broad range of testable uses of the dataset, and penalizes
only *new* annotation burden.

The rulings below therefore are dependency rulings, not trivial text-identity
rulings. Mentions of the old charter's vocabulary were not treated as taint
unless a recorded conclusion required the divergent rule.

## Ruling table

| Artifact | Ruling | One-line basis |
|---|---|---|
| `critique.md` | STANDS | Its `ADVANCE TO REVISION` conclusion follows from dataset/map provenance, CBV–MTT degeneracy, intervention identifiability, outcome-label support, model scope, and feasibility; none requires the baseline-only deliverable or annotation rule. |
| `debate.md` | STANDS | The debate's successive repairs concern the load-bearing outcome gate, joint-channel identifiability, the unsupported mirror-normal kink, and model-family scope; these scientific objections remain operative under the ISLES'24 charter. |
| `consensus.md` | STANDS | The summary accurately records the debate's agreements, unresolved construct-validity issue, amendments, and `REVISE` recommendation; that recommendation is grounded in measurement validity rather than the divergent program focus. |
| `revision.md` | STANDS | The narrowed joint-state claim implements the later human ruling recorded in `evidence/decisions.md` and the scientific finding that baseline maps cannot measure remaining vasodilatory capacity; its use of “rungs” is inherited terminology, not a dependency of the narrowing decision. |
| `keystone_screen.md` | STANDS | This is a factual official-release schema ruling about the presence and NCCT-space registration of CBF, CBV, MTT, and Tmax maps; the charter mismatch has no bearing on its `PASS`. |
| `feasibility.md` | STANDS | The scoped Stage-0 `GO` is based on verified ISLES'24 access, license, cohort, maps, labels, released models, compute, and edit-validity gates, and explicitly follows the binding human reduced-claim decision. |

## Dependency findings

No artifact is TAINTED, so no stage is identified for re-running.

Several artifacts visibly use concepts emphasized by the archived baseline
charter—especially “rung 1/2/3,” a physician-legible named signal, automatic X
measurement, and the analogy audit. Those passages do not control the recorded
verdicts here. The current ISLES'24 charter independently permits
interpretability studies, values testability and concrete dataset use, and
retains the use-versus-association and identifiability discipline. Moreover,
the stricter baseline no-annotator rule did not exclude this candidate: its X
is computed from released maps, its primary readout is label-free, and use of
the existing final-infarct labels incurs no penalty under the corrected
annotation rule.

The most consequential narrowing—from “autoregulatory blood-volume reserve”
to an “outcome-associated joint CBV/MTT decision boundary”—also does not depend
on the baseline charter. It is fixed by the 2026-08-17 human decision after the
construct-validity question was answered: ISLES'24 has baseline maps but no
vasodilatory challenge, so the data cannot measure remaining dilation capacity.
That reasoning is scientific and dataset-specific, and is at least as relevant
under the corrected charter.

## Overall recommendation

**CLEAR-TO-CONTRACT.** Every audited artifact STANDS. This is a reconciliation
recommendation only; it does not authorize a contract, Stage 0 execution,
model training, or probe work, and the human gate remains controlling.

## In plain terms

The earlier stages were run with the wrong general research charter in their
prompts. I checked whether that wrong text actually caused any of their
decisions. It did not: the criticism, revisions, factual data check, and
feasibility decision all rest on properties of ISLES'24, the physiology the
dataset can and cannot measure, and the validity of the proposed experiment.
Some older vocabulary remains in the documents, but removing that vocabulary
would not change a verdict. No stage needs to be rerun for charter reasons.
