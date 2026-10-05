# Review packet selection correction

This is a successor to independently approved 5d27484. It unblocks the unused,
operator-authorized review of unchanged 12aeb59. The operator policy is recorded
outside the model packet and bound by SHA256 in the validator.

Only six explicitly named historical carrier paths may be excluded from that
retry's model view. A version-2 root-owned retry permit binds every excluded
hash, the exact original packet, the replacement summary, and the actual policy.
Source, tests, authority, findings and unlisted evidence remain byte-identical.
The provider retry still requires the original one-retry decision, genuine
terminal refusal, matching ledger row, same source/runtime/model/limits, and
round two. The stored original packet is verified again before reservation.
The replacement summary is not a source verdict or proof of reviewer inspection.

A1 from the 5d review is addressed: retry schema and brief_policy=1 are required.
No accounting, sandbox, credential, scientific or deployment behavior changes.
The existing M2 packet contains no raw session transcript/native stream/refusal
text; its completion route needs no evidence-selection exception. Its report
and prior source coverage remain at their original scope. 12aeb59 remains a
separate frozen candidate; this change does not approve it or spend its retry.

Tests: permitted selection admits once; changed/missing originals, source,
authority, policy, permit, summary or selection fail before charge; third round
refused. An opt-in private fixture checks the genuine 12 packet and refusal
without copying originals into any review packet. Synthetic tests are labelled.
