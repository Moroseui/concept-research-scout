# Live synthetic executor witness

Exact implementation: 469d29df002ea78f64146731244769d7c82330d6.
Both actual CLI legs completed successfully through campaign run_isolated_stage
and the existing scout.run_agent primitive. The source manifest and original
execution receipts are preserved unchanged. The Codex console reports
`gpt-6-astra`; the legacy receipt parser records its model as null, so the
console supplies that observation. Claude used `claude-fable-5`.

Inputs were only synthetic n=2, mean Dice=0.5. Claude's APPROVE applies only to
this explicitly non-scientific smoke interpretation, not P001 or human
ratification. These consoles were inspected before publication. No credentials,
patient files or clinical values were present. This complements the six-command
disposable lifecycle test, whose agent/validator adapters are explicitly fake.
Colab execution/retrieval is still unverified.
