# First protocol proposal

The `protocol-proposal-task/v1` contract lets the existing campaign pipeline
develop and challenge a P002 or P003 protocol before any protocol is authorized.
It uses the selected charter, recorded source context and exact supplied artifact
references. It does not require a prior protocol, the old P001 interpretation, or
permission to read new data.

The task has the exact fields `schema`, `task_id`, `experiment`, `mode`, `request`,
`references` and `selected_by`; its mode is `protocol_proposal`. The pipeline
produces six proposed artifacts: protocol, methodology, literature review, input
manifest, partition registry and exposure history. The helper validates their
bound originals before opposing review and when original results are recovered.
Existing author, opposing review and disposition stages remain responsible for
the scientific judgment and saved task state.

Data inventories and membership must come from supplied originals. Literature
citations identify the actual supplied context and never claim a fresh search or
paper access. Unavailable evidence produces an explicit placeholder and a
`DEFERRED` protocol with readable unknowns. A human or investigator can inspect
that same saved proposal and provide the missing evidence in a later version.

A complete `PROPOSED` bundle remains a proposal. The separate
`AUTHORIZE_PROTOCOL` operation checks that all six originals belong to the same
reviewed version and refuses deferred evidence before requesting its own actual
scientific decision. Proposal validation grants no data access, execution,
scientific acceptance or broader charter authority. Original frozen P001 routes
and receipts retain their existing interpretation.
