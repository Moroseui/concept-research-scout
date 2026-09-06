# Result card — scoped prediction prompt guidance

**Question:** How can the scout and reviewers assess prediction without inventing mechanism claims or changing historical records?
**Evidence:** The supplied scout requires “the model is using X”; the proposed charter admits a transparent fixed-threshold reference.
**Limitations:** This is prospective prompt guidance only; no active prompt, schema, backend or historical score has changed.
**Next decision:** Review its scope with `CHARTER.proposed.md` and `RUBRIC.proposed.md`; any installation and affected-surface review remain pending.

Proposed identity: `isles24-prediction-prompts/proposed-v1`. Apply only when the explicitly selected charter is the prospectively adopted isles24-prediction charter. Do not globally weaken the legacy mechanism track. Until adoption, this text has proposal status only.

## Author/scout guidance

Begin each markdown artifact with a readable result card: question, evidence, limitations, next decision. Distinguish supplied historical receipts, newly inspected sources, assumptions and missing evidence. Cite precise source paths or primary URLs and state what they support. Never claim a novelty search, measurement, artifact inspection or approval that did not occur.

For predictive benchmarking, replace the mandatory model-use deliverable with: “Using [admission-available input], [fixed rule or specified predictor] predicts [operational target], assessed by [patient-level metric] against [reference] on [cohort].” Preserve uncertainty and exploratory status. A fixed rule is a predictor in this narrow sense, not a trained model. Model-use and causal claims still require designs that distinguish use from association; they are not required for honest prediction.

Replace mandatory `X_measurement`, mechanism/rung and model-beats-human entry requirements with target, input cutoff/provenance, prediction rule, label/evaluation separation, cohort policy, estimand, leakage threats and intended inference. Do not invent values for incompatible legacy fields. A future schema adapter must explicitly handle absent/not-applicable mechanism fields and be separately reviewed; no backend compatibility is asserted here.

Do not enforce ten-question/five-card quotas, A/B/C quotas, two-dataset limits, mechanism-only templates or preference for label-free primary metrics in this focused track. Use `other:predictive-benchmark` if the existing design-template vocabulary must be retained. Require testability and an honest short list. Existing annotation use is allowed; only new lab annotation burden earns a feasibility penalty.

For this readiness task, assess the supplied external seed, not a manufactured revival or system-origin discovery. Preserve its parent/source references and attribution; no “new fact” story is needed to pretend it was independently generated. Do not generate runner code, tune thresholds, select P002/P003, or propose a result-informed comparison before baseline evidence exists.

Each candidate/assessment must state:

- Precise question, plain-language value and bounded claim; external seed/origin when relevant.
- Target, timing, prospective inputs, baseline, cohort, patient evaluation, metric/uncertainty, budget and failure rules.
- Keystone prerequisite/status, exact supporting evidence if present, residual assumptions, source gaps and blinding plan.
- Closest verified prior work or explicit absence of a search; confounds and alternatives the design does and does not address.
- Anticipated negative and its limits, existing assets, remaining evidence, charter-specific scores when requested, and next decision.

Use the proposed rubric's canonical score shape and caps. Do not mark evidence inspected merely because a source was named. Keep outcomes sealed during design review; evidence about provenance and testability can support readiness without inspecting labels. Prior outcome reuse remains a limitation even when the new prediction/evaluation process is blinded.

## Critic/reviewer guidance

Judge whether the design can answer its stated predictive question. Explicitly distinguish minimal-reference adequacy, competitive performance, trained prediction, mechanism, novelty and clinical utility. Test target/timing coherence, leakage controls, units/geometry assumptions, empty-mask rules, patient weighting, uncertainty interpretation and compute/integrity stopping rules. Do not require a mechanism to rescue a sound benchmark or call absence of results a scientific failure.

Recommend ADOPT_CONDITIONALLY, AMEND or REJECT with concrete evidence and unmet conditions. A desk review of supplied text does not replace opposing-family review of exact executable bytes. Changed dependencies require refreshed review; an old APPROVE cannot authorize changed HEAD. If recommending amendment, identify the changed scientific contract and new review requirement while retaining every original artifact.

## Handoff guidance

Link future decisions prospectively to exact charter, rubric, prompt, adoption, spec and review identities. Keep historical agent/human attribution and approvals intact. Never emit ratification markers, launch permission or a claim that P001 depends on 047 acceptance. Keep original successful-console gaps as gaps; failed logs are not substitutes.

The Wednesday handoff must say which gates have evidence, which remain unresolved, and what decision each missing item blocks. Desk work is independent of patient launch and unattended activation. A valid result handoff needs private original evidence and the five permitted aggregate artifacts; without them, deliver a proposal/readiness card, not measured performance. Any publication, backend amendment, launch or ratification remains outside this task.

Sources: supplied `orchestrator/prompts/scout.md` (restrictions addressed here), `docs/SCORING_RUBRIC.md` (shape/caps), `charters/isles24/CHARTER.md` (scope and annotation discipline), `docs/science/PREDICTION_READINESS_DIRECTION_20260906.md` (readiness and origin), P001 `SPEC.md` (frozen predictive design), and `docs/isles-pilot/{CURRENT_STATUS.md,047_LIFECYCLE.md}` (operational versus scientific status). Source gaps and primary-source references are in `CHARTER.proposed.md`; no missing ledger, onboarding or deployment original is claimed read.
