# Result card — isles24-prediction charter proposal

**Question:** Can admission imaging support a reproducible exploratory prediction of follow-up infarct?
**Evidence:** Supplied P001 specification and review establish a fixed threshold candidate; current status reports no patient return.
**Limitations:** Reused development outcomes, treatment-dependent labels, inherited unit assumptions and incomplete source checks limit inference. This is an agent-authored proposal, not approval.
**Next decision:** Review this charter, its rubric and prospective P001 linkage together; ratification and baseline launch remain pending and are not requested or performed here.

## Purpose and envelope

Proposed charter identity: `isles24-prediction/proposed-v1`. Produce a credible reference measurement of released follow-up infarct from information available by completion of admission CT, then consider whether a fitted predictor merits investment. Eventual patient-outcome prediction is a longer-term direction, outside this baseline's target. All scientific work is exploratory; neither novelty nor a trained predictor is presumed.

One primary prediction thread and one adjacent research thread are allowed. The experimental envelope remains one baseline and at most two follow-up comparisons, selected sequentially only after valid baseline evidence is inspected. This proposal selects or executes neither P002 nor P003. Adjacent desk research cannot expand the experiment budget or become a patient-data bypass.

Use only the frozen eligible 99 development cases in any subsequently authorized experiment. The 49 reserved cases remain untouched. These counts are separate constraints, not an accounting of the release's reported 149 cases; do not infer eligibility for any remainder. No new patient access, extraction, execution, remote write, spending, credentials or provisioning is authorized here.

## Scientific contract

- Specify target, admission cutoff, permissible inputs, patient-level evaluation, primary metric, reference baseline, compute cap and stopping rules before execution. Outcomes, follow-up images, post-intervention variables and outcome-selected membership/ranks cannot be predictive features. Frozen membership reuse is distinct from rank-based selection.
- A fixed admission Tmax >6 s mask is eligible predictive benchmarking. Its question is spatial agreement and volume error against the released post-treatment follow-up infarct mask. It does not identify a biological mechanism, prove a model uses a signal, estimate untreated infarct or validate clinical use.
- Deliberate blinding is a strength: freeze predictions before label opening; do not demand outcome inspection to score design readiness. Prior development-outcome exposure remains disclosed and prevents an untouched-test claim. Any future fitted comparison must specify leakage-resistant patient separation before fitting.
- Preserve P001 v1.1 unchanged. No threshold tuning, masking, extra exclusion, geometry repair, altered units or metric substitution can be smuggled into adoption. A scientific change requires a separately identified amendment and fresh review; old authorization cannot cover changed bytes.
- Require source-bound opposing-family review of specification and implementation before a real run. Record every attempt and failure; invalid execution is not a negative scientific result. Report unavailable duration/usage/cost/intervention measurements as unavailable or null, never estimates presented as measurements.

## Governance and evidence

This proposed charter and `RUBRIC.proposed.md` apply prospectively only. They do not rewrite `charters/isles24/CHARTER.md`, historical scores, P001 authorship/decisions, or 047 records and approvals. Scores are comparable only within the same charter/rubric version and scoring phase. `PROMPTS.proposed.md` describes a scoped prompt override; no backend or active prompt amendment is installed.

P001 is an external seed under operator delegation, not system-authored code. `P001_ADOPTION.proposed.md` recommends conditional adoption with exact preserved references. Any future linkage must bind final charter, rubric, prompt guidance, adoption proposal, specification and review bytes in a separate prospective record. A recommendation or historical APPROVE review is not charter ratification or launch permission.

Maintain a single branch writer, immutable execution snapshots, private original evidence, publication checks and protected 48/96 activation gates. Existing CPU Colab entitlement and manual Run All remain the frozen compute route; backend changes require their own proposal and affected-surface review. No unattended-operation assumption follows from synthetic demonstrations.

## Wednesday critical path

Target: Wednesday, 9 September 2026, a reviewed baseline and, only if separate gates resolve, a validated return and interpretation. Desk drafting, source-gap inventory and scientific review can proceed independently of 047 acceptance, patient launch and unattended activation.

The dependent path is: resolve charter/adoption disposition and outstanding scientific source questions; establish exact execution snapshot and fresh review for changed dependencies; resolve authorized transport/runtime access and the held dispatch through job/process/checkpoint reconciliation; separately authorize baseline launch; obtain private original console/checkpoints and permitted aggregate return; validate identity, completeness and metrics; then review interpretation before choosing a follow-up. NOT_VISIBLE does not establish that no job exists. Do not automatically retry the ambiguous dispatch. No duration or completion guarantee is available.

If launch gates remain closed by Wednesday, the deliverable is the reviewed proposal/readiness packet and explicit unresolved gates, with no invented baseline result. 047 registry attestation, audit disposition and missing successful console concern 047 alone; none is a P001 prerequisite. Hosted writer/reset activation and observation are operational gates for routes that require them, not prerequisites for desk science or an invented reason to block every authorized manual route.

## Sources and gaps

References below mean the supplied excerpts, not files inspected in an original repository.

- `docs/science/PREDICTION_READINESS_DIRECTION_20260906.md`: Wednesday target, external-seed origin, two threads, authority limits and missing originals.
- `campaigns/isles24-pilot/CAMPAIGN.md` and `experiments/P001/SPEC.md` beneath that campaign: frozen scientific and resource envelope.
- `docs/isles-pilot/CURRENT_STATUS.md`: P001 unexecuted, dispatch held, changed-dependency review and operational limits; older pending text is historical, not a reversal of later receipts.
- `docs/isles-pilot/047_LIFECYCLE.md`: separate 047 acceptance track; preserve Phase A and historical approvals.
- `docs/science/PREDICTION_PRIMARY_SOURCES_20260906.json`: reported metadata verification of [release](https://zenodo.org/records/16813698), [dataset paper](https://arxiv.org/abs/2408.11142) and [challenge paper](https://arxiv.org/abs/2408.10966). No fresh literature search, full-text verification or measurements were performed here. Full-text timing, Tmax units, annotation details, license/access conditions and official evaluation details need claim-specific evidence before stronger assertions; do not substitute a newer release.
- Original `ONBOARDING_astra_implementation.md` and named deployment-review originals are unavailable in supplied context. Do not reconstruct them or claim to have read them. Any future dependent decision packet must disclose this gap.

Each future evidence packet must lead with question, evidence/result and uncertainty, limitations and next decision; name baseline/change, timing, artifact identities, failures, residual assumptions and the evidence needed to resolve the next decision.
