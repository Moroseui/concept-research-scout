# Validate scientific judgments before opposing review

The saved task921 investigator eligibility on a472034 returned a list of
reconsideration conditions. The existing scientific_authority contract requires
a nonempty string. Its author prompt said only "nonempty conditions", and
scientific_decision.execute deferred full validation until after opposing review.
Both genuine outputs remain preserved; APPROVE did not seal the malformed author.

This correction states the existing JSON string contract explicitly and invokes
the same sealing preconditions before the opposing stage. Invalid output stops
with original bytes and an explicit no-automatic-retry record. Valid APPLY and
DEFER retain independent review and all later sealing checks. No schema, spending,
halt, scientific authority, retry permission or original judgment is changed.

Callers share scientific_decision.execute: scientific_decision service actions
and research_task_authority.DecisionStages, including investigator eligibility.
Tests cover invalid type, empty conditions, invalid state and decision, valid
reviewed deferral, original preservation, and refusal to replay a stopped output.

This prevention does not recover the completed malformed eligibility. The
existing investigator recovery only reuses original provider replies. Existing
authority_replacements handles two different fixed continuing-operation failures,
requires a discussion task and no original opposing review, and does not apply
to this investigator wake with a completed review. A separately authorized,
reviewed supported recovery is needed; do not repurpose either route or normalize
an author's judgment in the implementation driver. Installation and use remain
subject to the applicable independent review and release gates.
