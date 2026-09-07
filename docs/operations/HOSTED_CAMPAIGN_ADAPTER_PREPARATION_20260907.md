# Hosted campaign adapter — preparation, not installed acceptance

The prototype reuses `campaign_pipeline.execute` and the existing protected model
broker. It does not introduce a model credential, paid fallback, patient handler,
new service or live admission grant. The broker still controls the exact source,
OS peer, model identities, stage order, original private evidence and admission.

`BrokerStages` turns the broker's checked textual answer into the exact artifacts
required by the existing campaign pipeline. Only P001 discussion/readiness is
supported. Extra files, wrong families, altered answer hashes and empty content
refuse. Codex's requested model remains gpt-6-astra; unavailable resolved-model
identity stays null. Claude's reported model must match claude-fable-5. Original
protocols remain in the protected broker; the candidate gets checked artifacts
and attributed provenance hashes.

The shared pipeline now accepts an explicit one-round bound for this transport;
its default two-round behavior remains for existing callers. A negative first
review preserves its proposal, review and blocked artifact without consuming a
hidden repair round. Author and reviewer consume two of the broker's three
stages; disposition remains the third. No caller-provided shell command is added.

This avoids requiring the hosted snapshot to import scout.py or a second provider
launcher: scientific generation and review still use the shared pipeline, while
the already protected transport performs the actual subscription calls under
separate accounts. The earlier inventory gap is preserved in
REAL_SCIENTIFIC_ADAPTER_GAP_20260907.md as the pre-adapter observation.

Local tests exercise the actual campaign function with synthetic broker replies,
not real model calls. The initial fixture exposed a directory-mode mismatch with
the existing private immutable writer; campaign output and round directories now
explicitly use mode 0700. Eleven focused tests then passed. This is not hosted
execution proof or a completed real-task adapter cycle.

Remaining before acceptance: reviewed completion-to-task binding, actual non-root
socket use, duplicate/interruption reconciliation, response/report bookkeeping,
and a fresh bounded hosted execution with primary evidence review. Existing
consumed fixture allowances must not be reset or silently enlarged; any new
supervised fixture must retain its own explicit finite scope and existing limits.
