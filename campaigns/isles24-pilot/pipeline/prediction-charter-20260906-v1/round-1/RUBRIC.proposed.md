# Result card — prediction-scoped rubric proposal

**Question:** How should honest predictive benchmarking be judged without requiring a model-use claim or breaking blinding?
**Evidence:** Supplied legacy rubric scores mechanisms; P001 instead estimates a fixed admission map's agreement with follow-up infarct.
**Limitations:** No performance evidence or novelty search is available. Proposed scores have no cross-charter meaning.
**Next decision:** Review these anchors and caps alongside `CHARTER.proposed.md`; keep backend adoption and historical scores unchanged.

Proposed identity: `isles24-prediction-rubric/proposed-v1`. Score each dimension 1–5 with an evidence-based explanation; 2 and 4 interpolate. Preserve canonical `scores` entries as `{"value": N, "why": "..."}`. Omit `keystone_evidence` when absent; never use null. Record charter/rubric identity and phase (`design` or `result`) with every assessment.

## Scope and anchors

| Dimension | 1 | 3 | 5 |
|---|---|---|---|
| Clarity | Target/time unclear | Testable with clarification | Precise target, timing and estimand |
| Identifiability | Leakage or readout cannot answer claim | Main threats bounded, residual assumptions | Design identifies the stated predictive quantity within explicit limits |
| Medical relevance | No meaningful connection | Useful research surrogate | Clear consequential research question; no deployment inference |
| Interest | Redundant without purpose | Useful reference or diagnostic result | Broadly informative answer either way |
| Prior legwork | Unsupported assets | Spec/assets documented; checks remain | Relevant artifacts and bindings inspected and ready |
| Feasibility | Unbounded barriers | Concrete budget with unresolved gates | Demonstrated compatible route within budget |
| Data readiness | Existence/timing unclear | Pinned inventory and access route documented | Necessary non-outcome integrity and access evidence verified |
| Evaluation readiness | Target/metrics undefined | Readout mostly specified | Patient weighting, baseline, edge cases and uncertainty fixed |
| Negative-result value | Invalid/uninterpretable failure | Limited but useful benchmark | Valid poor performance decisively answers the narrow question |
| Novelty confidence | No verified gap; no claim required | Gap uncertain after scoped checks | Precise gap supported by verified primary work |
| Regret | Little consequence of deferral | Useful opportunity | Strong evidence that deferral loses a valuable opportunity |

Identifiability means validity of the predictive inference, not isolation of a mechanism unless that is actually claimed. A valid threshold benchmark may score well here without a trained model or novelty. Poor Dice would inform adequacy of this threshold on this cohort; it would not show that admission imaging is uninformative or that learned prediction cannot work.

Retain the transparent legacy priority weights: feasibility 20%, identifiability 15%, medical relevance 15%, prior legwork 10%, interest 10%, clarity 10%, negative-result value 10%, data readiness 5%, novelty confidence 5%. Weighted mean stays on 1–5; it is not a probability. Report evaluation readiness and regret separately. Do not import Mode C mechanism weighting into this prediction track. Speculative adjacent work must declare its own applicable charter/rubric and cannot compete through incomparable scores.

## Evidence, caps and deliberate blinding

Name the load-bearing prerequisite, its evidence status (`INSPECTED_TRUE`, `INSPECTED_FALSE`, `NOT_INSPECTED`) and residual assumptions. `INSPECTED_TRUE` requires a precise artifact excerpt/location and what it proves. An inherited receipt is attributed evidence, not a fresh inspection of private inputs. A homepage or abstract cannot verify voxel units or executable behavior.

Keep feasibility and novelty confidence capped at 3 unless the keystone is `INSPECTED_TRUE`; even then higher scores need dimension-specific support. Inspected feasibility does not establish novelty. Cap negative-result value at 2 for an anticipated uninterpretable negative. New lab annotation burden reduces feasibility with a reason; existing released annotations incur no annotation penalty.

Do not require labels, outcome distributions, per-case performance or rankings to establish design readiness. Deliberately sealed labels are not missing prior legwork. Assess pinned inventories, timing provenance, specifications and attributed reviews; distinguish planned checks from completed ones. Actual unavailable access/integrity evidence can limit readiness without penalizing blinding itself. Result-phase assessment requires a valid, complete return; never fabricate result scores from a specification.

Hard scientific failures override the sum: unavailable claimed inputs, prospective leakage, protected-cohort access, unanswerable estimand, unsupported causal/model-use claims, changed frozen bytes disguised as adoption, or absent required execution evidence. Operational holds yield conditional readiness, not proof of scientific worthlessness. No numerical score alone authorizes adoption, ratification or launch.

## Decision record requirements

Emit a recommendation (`ADOPT_CONDITIONALLY`, `AMEND` or `REJECT`) with scope, concrete reasons, hard-gate status, cited evidence, unknowns, and an evidence/next-decision list. AMEND names a separately versioned change; REJECT names the defect and any evidence that could change it. This document supplies scoring rules, not retrospective P001 scores. Proposal review may be favorable while execution remains blocked.

Sources: supplied `docs/SCORING_RUBRIC.md` (shape, dimensions, weights and caps); `orchestrator/prompts/scout.md` (legacy mechanism restrictions); `charters/isles24/CHARTER.md` (charter-specific scores, annotation rule); P001 `SPEC.md` (predictive estimand/blinding); `docs/science/PREDICTION_PRIMARY_SOURCES_20260906.json` (source limits). No historical score is recalculated. See `CHARTER.proposed.md` for scope and `PROMPTS.proposed.md` for prospective application.
