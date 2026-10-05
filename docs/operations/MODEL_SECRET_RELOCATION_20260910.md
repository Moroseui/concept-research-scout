# Relocate the existing Actions model secrets without a plaintext handoff

This administrative route prepares ciphertext for the already approved `research-models` environment. It does not install Linux credentials, remove repository originals, run models or science, merge main, or activate unattended work. The existing restriction approval is `PROTECTED_HANDOVER_APPROVED_20260908.json`, item 4. Exact source review, independent main review, permitted workflow publication and the operator's main-merge decision still precede live use.

The workflow reads exactly the existing repository names `OPENAI_API_KEY`, `CLAUDE_CODE_OAUTH_TOKEN`, and `CODEX_AUTH_JSON` in one encryption step. Legacy `CODEX_AUTH_JSON` is copied as opaque data; copying it does not establish its validity or authorize its use. The fixed recipient is repository `1323461276`, environment `21537367870`, environment name `research-models`, public-key ID `3380204578043523366`. The public key is pinned in `configs/model-secret-relocation-target.json` and checked against its fixed hash. No caller can choose another recipient or secret name.

Before secrets enter the process, the workflow checks its exact main/run identity, original attempt, source review, current repository/environment identity, main-only branch policy and environment public key. A previous dispatch at the same source stops for reconciliation. The source-reading job deliberately has no destination environment, so an environment value cannot override a same-named repository source. The job has read-only Contents and Actions permissions, and no owner token. A failure to read permitted recipient metadata stops before encryption; do not add administrator credentials to the runner to repair it.

The encryptor uses the documented libsodium sealed-box format. Its dedicated hash lock covers PyNaCl 1.6.2, cffi 2.0.0 and pycparser 3.0, using Linux x86_64 wheels for CPython 3.11/3.13. The workflow installs that lock with `--require-hashes --only-binary=:all:` before source secrets enter the step. The general scientific dependency file is unchanged. Release metadata and wheel hashes are published by [PyPI](https://pypi.org/project/PyNaCl/1.6.2/); the library documents [sealed boxes](https://pynacl.readthedocs.io/en/latest/public/#nacl-public-sealedbox). GitHub documents the [same encryption format](https://docs.github.com/en/rest/guides/encrypting-secrets-for-the-rest-api).

Only a canonical manifest containing the three ciphertexts and fixed provenance can be uploaded. The validator rejects unknown fields/names, recipient or source drift, changed hashes, oversized values, ordinary plaintext and base64-wrapped text. It also applies the unchanged `public_export.text` scanner; no export exception or arbitrary ciphertext allowance was added. Shape checks cannot prove cryptographic origin. The operator stage therefore downloads the single original artifact directly from the exact successful main workflow/run/attempt and verifies its identity before any write. The private key is held by GitHub; neither the runner's output nor the operator's machine can decrypt the ciphertext.

## The finite operator sequence

Prepare the reviewed merged main checkout and record its exact SHA as `MERGED_SOURCE`; this is a value to obtain from the actual reviewed merge, not a placeholder that grants a merge. Confirm the environment ID and its sole `main` branch policy again. Preserve repository originals and the existing credential arrangements.

1. Run the separately reviewed credential-free environment-denial canary once on its exact nonmain branch. Its one environment job must be rejected by GitHub policy before runner execution. A job skipped by a workflow `if` expression is not that evidence. The prepared independent canary source/branch and its publication authorization are supplied in the private operator packet.
2. Dispatch `model-secret-relocation.yml` on `main` with the sole input `source_sha=MERGED_SOURCE`. Inspect and retain that run's exact ID, source, first attempt, step outcomes and ciphertext artifact. Do not rerun after a disconnect without inspecting the existing run. The artifact expires after one day; collect it promptly through the following fixed route. This step does not stage secrets or test model authentication.
3. From that clean merged main checkout, using the operator's existing `gh` authentication, run:

   ```sh
   python -m orchestrator.model_secret_relocation stage \
     --source "$MERGED_SOURCE" --run-id "$MIGRATION_RUN_ID" \
     --store "$PRIVATE_RELOCATION_STATE"
   ```

   This command requires the current main source and actual adapter review, downloads only the original named artifact, rechecks the recipient and an empty environment, and performs three fixed ciphertext PUTs. It creates a private intent before each request and preserves names-only receipt metadata afterward. It does not delete repository copies. A completed repetition returns the saved binding with zero PUTs. A partial or ambiguous request stops for reconciliation; a new call never silently repeats it.
4. Run existing `results-validate` on `main` with exact inputs: `mode=status`, `experiment=P001`, `question=Check existing result readiness without model execution.`, `request_id=env-stage-20260910-v1`, `source_sha=MERGED_SOURCE`, `destination=actions-artifact`, `initiator=codex` for the agent or `human` for the operator actually invoking it. Retain the authentication step's own result and deterministic `READY` or `WAITING_FOR_RESULT` artifact. Overall workflow success alone is insufficient because the authentication step has `continue-on-error`.
5. Only after the approved scope-restriction prerequisites and legacy credential disposition are recorded, remove the repository-level copies through the separately controlled operator route. This module has no delete operation. Preserve the staged private values and ciphertext originals; no local plaintext backup has been recovered. Repeat the same main status control once with `request_id=env-only-20260910-v1` to establish environment-only access after repository copies are gone. Keep scientific execution and unattended activation separate.

The first status canary while repository copies remain does not by itself establish the secret's origin. GitHub describes the [environment secret precedence](https://docs.github.com/en/actions/reference/security/secrets) and [environment secret API](https://docs.github.com/en/rest/actions/secrets). The final names-only inventory and second authentication/readiness result complete that scope check; they do not establish provider funding, Linux authentication or scientific validity.

## Inspection and recovery

Humans and agents use the same saved state and command:

```sh
python -m orchestrator.model_secret_relocation status \
  --run-id "$MIGRATION_RUN_ID" --store "$PRIVATE_RELOCATION_STATE"
```

The private store retains original ciphertext, artifact/run/source hashes, each attempted fixed write and each acknowledged name. A missing acknowledgment means an uncertain write, not evidence of failure. Reconcile actual GitHub names/timestamps and the original request before deciding whether any further operation is necessary. Do not overwrite an unexpected existing environment value, erase an intent, copy an owner credential into Actions, or infer approval from a pending change request. Key or policy rotation requires a recorded source update and applicable review rather than a caller override.

The required new files are part of `actions_runner.reviewed_files(root)`, so modifying the encryptor, workflow, recipient, lock, tests, explanation or original setup grant invalidates its source review before the credential step. Local tests use synthetic values and a synthetic private key for a real encryption roundtrip. They do not establish a live migration, current runner token permissions, successful provider authentication or the private key's recovery.
# Runner permissions and interruption recovery

The runner uses only `contents: read` and `actions: read`. It checks repository,
environment and branch metadata, then encrypts to the public key bound in the
reviewed source. GitHub's environment public-key endpoint requires the separate
Environments permission, so that fresh check belongs to the existing owner route
before staging. A changed key or policy refuses staging; no owner credential is
passed to Actions. See [GitHub's endpoint permissions](https://docs.github.com/en/rest/actions/secrets#get-an-environment-public-key).

Owner staging holds a store lock across validation and writes. Concurrent calls
serialize, completed replay performs no PUT, and interrupted writes retain their
original intents for reconciliation.
