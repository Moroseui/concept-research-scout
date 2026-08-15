<!-- stage: probe_plan -->
Create the smallest computational feasibility probe for this idea. It must test the riskiest assumption—not attempt the entire proposed system.

Use `templates/probe_contract.yaml`. Keep the probe exploratory, validation-only, no more than 3 variants, one seed unless randomness itself is being tested, and at most 45 GPU minutes by default. Define invalidating failures separately from negative outcomes.

Write `probe_contract.yaml` in the idea folder and `README.md` in probes/IDEA_ID/. Do not implement code yet.

## Contract requirements file (overrides the defaults above)

If the idea folder contains `contract_requirements.md`, it is a
human-authored, ratification-gated specification and it WINS over every
default in this prompt (variant count, seed rule, GPU-minute cap, scale
of the probe). The contract you draft MUST satisfy every requirement in
that file, carry a `contract_version` field, and cite the requirements
file and any decision entries it names. The reviewer will check the
contract against the requirements file line by line; an unmet
requirement is a blocking finding. If a requirement is impossible or
contradictory, do not silently deviate: stop and write the conflict into
the contract draft as a blocking open question for the human.
