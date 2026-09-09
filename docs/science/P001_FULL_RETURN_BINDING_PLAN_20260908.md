# P001 full-return binding — finite plan and pending decision

Status: **local intake implemented and tested, pending source review; complete transport not demonstrated or authorized for patient launch**.

047b’s first formal interpretation and opposing review are complete. P001 source/dependency setup’s second source review is APPROVE; actual setup is underway and still requires its execution receipts. This plan identifies the remaining return path needed for a complete P001 launch decision; neither milestone substitutes for that decision.

## Preserve the existing scientific acceptance

Use execution snapshot `0770c7dcabe781cbfb87de505755e7aafa758f2e`, scientific source `d6a1184b4378e849213fd887a6f7b103fb1a64d5` and notebook `1a81c037343598f4e4585153b11d761b87a9ae3a`. Their existing scientific and dispatch reviews verify against the preserved private snapshot. Do not run the current engineering checkout through those historical review bindings or replace full validation with a remote-validation receipt.

The unchanged Colab child already calls `validate_return.verify`, then creates `P001-v1.worker/P001-private-return.zip`. The complete successful return requires these **206 members**:

| Members | Count |
| --- | ---: |
| `bundle/{summary.json,resolved_config.json,environment.json,execution_receipt.json,RESULT_CARD.md}` | 5 |
| `console.log` | 1 |
| `private/binding.json`, `private/checkpoint_index.json` | 2 |
| `private/checkpoints/*.json`, matching the frozen 99 eligible identities | 99 |
| `private/predictions/*.npy`, matching those same identities | 99 |

The validator reproduces aggregates from checkpoints and hashes every corresponding prediction. Five aggregates alone are insufficient. Existing failed-attempt files, if any, must remain preserved; unexpected additional archive members require explicit reconciliation. Raw/staged input images and `selected_inputs.json` are not required by this return validator and are not part of the proposed transfer.

## Shortest complete transport route

1. **Reserve app-owned destinations.** Under the already approved private Drive output folder, precreate one ZIP slot and one bounded terminal-receipt slot. Preserve exact IDs, names, parent identity and a unique binding before mutation; register the resulting IDs as protected aliases. Reuse the existing grant and `GoogleDrive.private_folder`, `allocate_ids` and `create`. Do not request another OAuth grant. The ordinary `store` interface currently rejects ZIPs; do not disguise the ZIP with another extension.
2. **Prove the destination behavior synthetically.** Use a harmless small ZIP and receipt through the complete proposed path. The existing mounted Colab runtime writes only the precreated files, without creating replacements. Verify through the connector that the original IDs remain valid and contain exactly the expected bytes. Folder/path correspondence and an interrupted-copy refusal must be demonstrated before relying on this behavior for P001.
3. **Copy only after the frozen child reaches a terminal state.** A separately bound, fixed Colab cell reads the known worker status and copies the existing completed ZIP in bounded chunks to its exact app-owned slot. It does not change the frozen runner or original outputs. Preserve a durable copy intent; an uncertain copy is reconciled, never automatically repeated. Return only allowed status, byte count and hashes through model tools. The terminal receipt records the observed worker state, binding and ZIP identity; it does not invent an independently observed OS exit. A failed run retains its originals and reports failure without manufacturing a successful ZIP.
4. **Collect the registered pair privately.** Extend the existing alias-only `DriveEvidence.handle`/`status` path only as needed for this registered binary return. Reuse before/after metadata, original preservation, checksum/readback verification and stable request-ID recovery. Credentials remain with the protected Drive service. No model receives payloads, arbitrary Drive IDs or credentials.
5. **Extract and validate privately.** A small fixed intake helper checks member identities, duplicate/traversing/symlink entries and bounded extraction before writing a fresh private destination. Preserve the original ZIP. Use the complete frozen cohort-derived member set and the existing return validator; do not weaken their checks or expose member contents to agents. Record compressed and uncompressed sizes and available private disk capacity before extraction.

The initial transfer ceiling remains **32 MiB for the complete ZIP plus terminal receipt**, not 32 MiB per chunk or per file. Measure the finished ZIP before copying. If the pair exceeds that ceiling, stop, preserve it on Drive and present its exact measured size and proposed additional cap for decision. Do not split requests or chunk the logical return to evade the aggregate ceiling. Streaming I/O changes memory use, not authorization or the byte cap.

## Existing workflow and minimum new pieces

Reuse `colab_patient.execution_packet`, `child_script` and `poll_cell` from the frozen snapshot; the existing supervised `Session`, exact-cell readback/transcript validators and private capture wrapper; and the installed Drive authentication, protected service, private folder and original-collection receipts.

New work is limited to destination reservation/registration for the ZIP/receipt pair, the fixed terminal copy/receipt cell, the bounded binary-pair intake and safe ZIP extraction. Test and source-review those pieces, then run the synthetic ID/readback canary. This is a transport addition, not new science or a replacement acceptance pipeline.

After collection, use the frozen system with the complete private inputs:

```text
python scout.py validate-bundle --campaign isles24-pilot --experiment P001 --bundle PRIVATE_BUNDLE --private PRIVATE_AUDIT --console ORIGINAL_CONSOLE
python scout.py record-result --campaign isles24-pilot --experiment P001 --bundle PRIVATE_BUNDLE --private PRIVATE_AUDIT --console ORIGINAL_CONSOLE
python scout.py interpret-build --campaign isles24-pilot --experiment P001
```

Validation and import precede system interpretation and opposing-family review. Preserve the original scientific/review bindings, required current operating context and actual stage receipts. No result publication or successor selection is implied by collection.

## Exact launch decision still to prepare

Before requesting the single P001 launch, bind the current CPU runtime, source/setup/environment receipts, selected archive reference, fresh process/output/checkpoint reconciliation, attempt identity, private output paths, exact app-owned return IDs and successful transport-canary receipt.

The decision must **explicitly include transferring the complete derived-output return containing the 206 members above**, its original console and bounded terminal receipt to the named private validation location, within the initial combined 32 MiB ceiling. That derived-output transfer is not already supplied by the existing Drive setup approval. It grants no raw/staged input transfer, additional OAuth scope, reserved-data access, new backend execution, automatic retry or larger transfer cap. Scientific launch remains a separate explicit decision on the completed packet.

## Remaining effort

Allow **1–2 additional engineering hours** for the return binding, focused tests, source review and synthetic canary. This is a new concrete gap, not completed Drive setup work. P001 source/dependency setup and collection of its actual execution receipts remain separate. Package installation, operator launch decision, experiment staging/runtime and any measured oversize-return decision are additional elapsed time. The experiment has not launched; runtime and final ZIP size remain unmeasured.

## Local intake contract prepared for review

`orchestrator/p001_return_intake.py` adds only the missing private ZIP extraction step. Existing ZIP helpers cover one admission JSON or three public control files; neither extracts this complete return. The new helper preserves original ZIP/receipt bytes, validates exactly the 206 frozen members and emits arguments for the unchanged `validate_return.py`; it does not itself grant transfer authority or scientific acceptance.

The fixed `p001-full-return-terminal/v1` receipt contains exactly `schema`, `request_id`, `runtime_fingerprint_sha256`, `worker_status` (`VALIDATED`), `execution_snapshot`, `source_pin`, `notebook_pin`, `zip_name` (`P001-private-return.zip`), `zip_bytes`, `zip_sha256`, `launch_manifest_sha256` and `max_extracted_bytes`. The trusted caller supplies the expected request/runtime/manifest bindings and expansion cap. The prepared launch manifest must bind the exact launch-decision SHA, attempt identity, setup/environment receipt SHA, reserved slot/alias binding and that expansion cap. The manifest and transport receipt remain separate from approval itself.

There is no finite maximum extracted byte size in the scientific specification or validator: 99 cases and finite 3D arrays impose no maximum voxel dimensions. Therefore the helper requires an explicit operational `max_extracted_bytes`, checks declared and actual expansion against it, and requires the declared bytes plus 64 KiB for intake records and a 256 MiB disk reserve before extraction. The eventual launch packet must bind that cap; it is not invented here. The combined compressed ZIP/terminal-receipt ceiling remains 32 MiB.
