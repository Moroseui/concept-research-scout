# Stock-take reviewer navigation: observed blocker and one proposed remedy

The native spec reviewer completed APPROVE at 2026-10-04 09:24:15 UTC. Preserve its original scope: analysis specification only, with an explicit inability to inspect numeric source material. It did not independently verify those numbers. Original review.json SHA256 1b87af25a43857be4e9374406234b95dc67b87833c5beebf29bbfe996d2101b3. Native call 4ca376785eb602739d3e301fd1a1af2056b83266058b3117e3afa1bca63316f0 remains COMPLETE and charged once; original uncertain author and completed linked replacement stay unchanged. Usage 3/8. Live phase COMMIT_SPEC. Neither interpretation call nor a retry has been launched.

## Confirmed cause

manual_context.py:82-95 emits the private navigation index with compact single-line JSON. The actual isolated Claude runtime has Read/Write/Edit only (manual_stage generated AGENTS.toml); Read pages by lines, not bytes. Its genuine tool result rejected the 98,435-byte, one-line index as 45,603 tokens against 25,000, including attempts with limit120, limit40 and offset1/limit1. Guessed logical filenames were absent because staging correctly uses authenticated hash-based paths. All174 registered files are present and byte/hash-correct. File permissions and the isolation boundary are not the failure.

Fifteen omission records also have single lines exceeding12,000 UTF-8 bytes; the largest is264,794 bytes. Their original content/hashes remain unchanged. The index cannot be made usable merely by telling Claude to lower its line limit. Source and service tests checked hashes/readability and transport to an isolated sink, but did not prove the native Read tool could consume the representation. This repeats the broader evidence-delivery gap: preserved/access-permitted is not equivalent to discoverable and readable by the actual consumer.

## Deterministic evidence, not another model call

Reformatting the actual index to indented JSON preserves the parsed records exactly:2,216 lines,115,956 bytes; every100-line window is at most5,640 bytes. This proposed file is private diagnostic evidence only; it is not installed, staged into a scientific call or represented as a live native Read success.

A separate private-copy preview used the installed producer, actual completed spec/review artifacts and the exact deterministic validation object the next COMMIT_SPEC transition would create. It changes no live lane or source and launches no model. Author133,883 characters/134,073 UTF-8 bytes, margin66,117 characters. Reviewer138,219/138,409, margin61,781 before the not-yet-existing interpretation and next-decision files: this is a lower bound, not a completed downstream measurement. The producer already externalizes the large validation record, so there is no demonstrated input overflow. That externalized one-line record shares the paging problem. Full receipts in composition-preview.json; hashes and actual native refusal evidence in observed-evidence.json. Raw session content stays in private records, not a future review packet.

## One proposed remedy

Prepare one small successor which serializes the generated navigation index and large structured provenance/validation records in bounded, line-pageable representations, with explicit page instructions. Preserve originals and their hashes; where original registered JSON bytes must remain fixed, provide a separately hash-bound, semantically identical readable representation, not a summary. Keep the registry, selected cohort/views, scanner, tools, runtime, plan, obligations, scientific scope and caps unchanged. Test every actual metadata file/page, unchanged semantic content and hashes, downstream composition with genuine outcomes, and have the independent reviewer exercise the native Read path. No permission widening, additional retrieval framework or full history injection.

Carry the same run forward at its next unexecuted transition through a separately reviewed exact binding: preserve all3 current call rows/charges, completed spec and review, owner, original failed row and the8-call cap. No new lane allowance, repeated spec call, reinterpretation of APPROVE, or relabelled failure.

## Actual authority/integration gates

The installed automated review runner still refuses any RUNNING/UNCERTAIN row (autonomy_review_runner.py:39-40); the preserved original author row remains UNCERTAIN. The stock-take exception is run-specific and does not permit an administrative review. The existing manual recovery authorization allowed exactly two rounds, now completed. A new focused manual implementation review therefore needs a specific operator exception; it cannot be called a third review under the exhausted permission.

The promoter also refuses an initialized lane (manual_promotion.py:90-102). Existing recovery promotion/migration is bound to the original6b predecessor, and its intent/event already exist. The correction must include an independently reviewed, exact same-run continuation, not edit installed code/state bindings in place or rerun the consumed migration. Standing M4 selection can still apply after genuine approval if runtime/plan/six conditions remain unchanged; it does not itself create another manual-review exception.

Recommendation: authorize preparation of this bounded navigation/continuation correction and one focused manual Claude implementation review, with no new scientific attempt allowance. Once genuinely approved and the existing deployment/live checks pass, resume at the next unexecuted stage under3/8. Any further manual round requires its own decision. No second scientific retry is being requested.

Until that decision, service inactive, timer disabled; no operation is running. Installed dcc161e2 and all original proofs/reports remain unchanged. BACKLOG item2 remains unstarted.
