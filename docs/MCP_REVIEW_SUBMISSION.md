# Bound MCP review submission

Supersedes prompt-only delivery for fresh administrative v6 reviews and the unlaunched BACKLOG2 bound-review/v1 scientific route. Preserved v1-v5 reports retain their original qualification rules;522e5b21 stays FAILED and charged once.

The existing evidence MCP server advertises a strict per-call schema. The same schema is enforced server-side, then the decision validator checks finding uniqueness and APPROVE consistency. Binding errors can be corrected within the same session. O_EXCL records one accepted submission, with a config hash; another submission refuses even after a server restart. No model file-write or execution tool can alter this record. Search remains bounded and read-only. Native tool-use input and its success acknowledgement must match the recorded payload/hash. Final prose is preserved separately and cannot supply a verdict.

The controller derives report.md/review.json from the accepted record only. Historical report parser semantics are untouched. A proven successful terminal scientific invocation without a valid submission becomes FAILED, retaining the call/charge; uncertain transport remains uncertain. No retry or budget extension follows. Model/client/login/turn/timeout/character caps stay unchanged. The one bootstrap review uses this candidate and is operator-preauthorized, not prior source approval.

Synthetic tests are not review approvals. The release evidence must include the real stdio MCP path, installed confinement, focused and both full server suites, and nonqualification of every preserved failure including522e5b21. Optional13A intake skips on any privacy flag. No patient/GPU/Modal work is authorized.
