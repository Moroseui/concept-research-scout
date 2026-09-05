# Explicit campaign lifecycle

The numbered-idea route and historical human approvals remain unchanged. The
pilot route requires `--campaign isles24-pilot --experiment P001`; do not pass
an idea number. Every gate binds the campaign, specification, investigator
identity and actual completed opposing-family review. No human marker is created.

Using the environment with P001 requirements installed:

```sh
python scout.py probe-build --campaign isles24-pilot --experiment P001
python scout.py verify-probe --campaign isles24-pilot --experiment P001
python scout.py package-colab --campaign isles24-pilot --experiment P001
python scout.py validate-bundle --campaign isles24-pilot --experiment P001 --bundle /private/return/P001 --private /private/return/P001.private --console /private/return/P001.console.log
python scout.py record-result --campaign isles24-pilot --experiment P001 --bundle /private/return/P001 --private /private/return/P001.private --console /private/return/P001.console.log
python scout.py interpret-build --campaign isles24-pilot --experiment P001
```

Build adopts the already authored, reviewed runner. Verify runs input-selection
preflight (no payloads) and the experiment's synthetic tests. Packaging pins the
notebook to the clean commit containing the valid review and verification.
Import copies only schema-validated aggregate artifacts and records their hashes;
private checkpoints and original console remain outside Git. Return validation
reproduces aggregates from checkpoints; it does not independently re-evaluate
image geometry or labels and reports that limitation explicitly.

Interpretation calls the existing receipted agent executor twice in disposable
aggregate-only repositories: Codex authors, Claude reviews. Prompts contain the
specification and permitted aggregate outputs. Both actual execution receipts
must succeed with different required families; failed/partial evidence remains
locally available and no success receipt is manufactured. A next decision is a
proposal only. A follow-up needs its own fixed specification, delegated decision,
runner, tests and opposing review, plus unchanged reviewed predecessor evidence.
The current notebook generator intentionally supports P001 only.

`test_campaign_lifecycle.py` traverses all six commands with disposable Git
commits and explicitly synthetic agent/validator adapters. It tests plumbing,
not external model quality or scientific acceptance. `test_prediction_p001.py`
separately runs the real prediction and return-validation implementations on
synthetic volumes, including resume and tamper rejection. Production approval
always requires the original completed CLI response and its reviewed source
manifest; synthetic adapters cannot produce a production approval receipt.
