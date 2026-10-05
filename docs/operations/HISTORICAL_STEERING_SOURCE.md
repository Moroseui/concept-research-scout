# Historical proposal identity across source upgrades

A recorded Issue6 proposal identifies the source that received it. That immutable identity is not an instruction to execute the old source, nor scientific authority. The current protected broker and installed controller configuration still select the consuming implementation.

`recorded_steering._snapshot` authenticates the current controller and intake configuration. `_original` separately authenticates the original source across the root-held plan/database, root attestation, received payload and hash-bound saved request. It passes that original identity to the existing attestation reader without changing fixed paths, service identities, permissions or the new-intake path. The returned proof retains its original source and bytes, so a source upgrade neither rewrites the request nor creates a fresh steering event. `investigator_wakes._steering` continues binding the same request and original-proof hashes.

The correction does not admit superseded comments, replay acknowledgments, confer scientific authority or relax new-intake source checks. Malformed or inconsistent original identities fail closed. Source approval, installation and live verification remain separate gates.

Focused verification: `tests/test_recorded_steering.py` covers unchanged proof/native wake identity across two consumer upgrades, unchanged originals, original-source/attestation refusals, current configuration mismatch, unchanged new-intake refusal and superseded-control behavior. These synthetic fixtures are not a live assessment of the user's proposal. Live acceptance requires the existing saved request hash to reach investigator and reviewer records after reviewed deployment, without repeating intake.
