# P001 preflight transport — bounded human/worker handoff

The persistent Claude worker uses the existing private `colab-worker` MCP
configuration and Windows browser launcher. The CLI stays alive between at most
three explicit requests so its MCP connection can survive the operator's browser
or Drive-consent step. It waits without model polling, has a two-hour outer bound,
preserves request intents and complete private protocols, and never automatically
restarts or resubmits an uncertain request. Reviewer sessions remain separate.

Installed Claude CLI accepts streaming input/output. The
[official CLI reference](https://code.claude.com/docs/en/cli-usage) documents these
options, and the [official SDK client](https://github.com/anthropics/claude-agent-sdk-python/blob/main/src/claude_agent_sdk/client.py)
uses the corresponding user-message structure. A real two-turn, no-tools
subscription test preserved one process/session and correctly returned the
first turn's synthetic nonce on the second. It did not connect MCP or touch data;
MCP continuity still needs the actual upcoming connection evidence.

`orchestrator/p001_preflight_transport.py` generates a thin notebook and the same
worker cells. CPU check and optional **human-run** Drive consent are distinct from
execution. Acquisition fetches only exact reviewed source commits with a shallow,
blob-filtered sparse checkout. Existing frozen source is verified, never reset.
The preparation pin must contain the genuine fresh transport-review receipt,
and script/adapter hashes must match it before launch preparation.

The unchanged scientific source remains at `d6a1184`; the preflight is separately
versioned readiness code. It uses isolated pinned Python dependencies, and checks
existing execution before setup and again before input access. Only the existing
preserved Colab archive is used. No Linux patient transfer occurs.

The background launch creates an exclusive durable intent and original private
console before starting the preflight. A duplicate launch refuses. A returned
launch tool call proves only dispatch, not successful verification. Separate
read-only retrieval validates the complete aggregate receipt schema and values;
unknown text/fields refuse before reaching a model. Raw headers, member identities,
archive payloads, checkpoints and original consoles remain private.

A missing receipt or disconnected runtime is uncertainty to reconcile, never
permission for Run All or another dispatch. The manual notebook route remains
usable if the worker connection cannot be retained. Patient launch remains a
separate exact decision after the reviewed preflight and scientific assessment.
