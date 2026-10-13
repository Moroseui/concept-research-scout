# Operator handover

Updated 13 October 2026, 21:38 UTC. Current operator: **Codex / OpenAI**. No rotation or Swap point. This record describes the current state; it does not grant scientific acceptance. Read [ROLES](ROLES.md), [CURRENT](CURRENT.md), [STATUS](outputs/STATUS.md), the [execution plan](outputs/13B_EXECUTION_PLAN.md) and [Colab usability requirements](docs/COLAB_USABILITY.md). Exact native receipts and operation paths are in the canonical private restart handoff, HANDOFF_CURRENT_PRIVATE.md, and the append-only operator-decisions.json record.

## Goal and operating direction

Advance approved ISLES'24 items 4 and 6 while making the system useful to humans. Seek understanding of placement versus amount, infarct size, region and fragmentation. Scientific code and conclusions belong to the existing OpenAI scientific author and Claude scientific reviewer. The operator owns infrastructure and packaging; its work requires opposite-family review.

Use judgment and consult Claude for accounting, safeguards, privacy, confinement, recurring failures or substantial changes. Preserve every attempt and charge. Ask Partho only for money or a necessary Colab action. Never access locked 25/reserve 24 payloads, change credentials, publish private patient material, merge main or edit BACKLOG. Wait for the daily reset rather than asking to exceed the cap.

New arms precede repeats. Deliver one preconfigured notebook per arm: default Colab A100, folds 0-4 sequentially, 250 epochs, preprocessing once, automatic checkpoint resume and completed-fold skipping. Colab is unmetered. Compare against Sprint12 A1 provisionally; small differences need a later same-platform repeat.

Every notebook must put all unavoidable login and browser capture in the first approximately two minutes, before installation or long work. Print exactly **All logins done, you can leave now** only after success. No later interactive authentication, remount or browser capture. Do not remove credentials or worker isolation checks to achieve this.

## Current workstreams and next steps

**Pnormct and pnorm_v2:** Partho reports pnormct completed epochs 0-86, then hung at epoch 87 while its heartbeat continued for about 17.7 hours. Returned checkpoint metadata records next_epoch 85. The 814 MB payload was not opened locally; the corrected runtime must verify its hash before loading. Pnorm_v2 was still running at two workers when last reported. Neither external session was touched.

Corrected resume files are delivered in Downloads; exact filenames and full hashes are in [resume instructions](outputs/COLAB_RESUME_20261013.md). Source 2e64b30c passed 31 tests and qualified implementation APPROVE 9012c065, report be7f92d1. Both scientific modules remain byte-identical. The adapter selects 12 training/6 validation workers on the observed 12 CPU/167 GiB runtime. The external watchdog kills stalled child groups, prints logs, preserves a bounded private error and requests runtime unassignment. A Google refusal means termination is not guaranteed.

Checkpoint migration uses the original lease/CAS checks and accepts only the exact expired or unowned old binding. Originals and payloads remain; live owners, changed inputs and unknown environments refuse. Pnormct should resume at 85 rather than restart fold 0. For v2, switch after a fresh checkpoint if it progresses. Partho must disconnect/delete the old runtime and allow five minutes for lease expiry before running a corrected file. Never edit a lock or overlap sessions for the same arm.

Next evidence: first completed epochs and worker counts from the corrected runtime, provisionally 15-30 minutes after starting including setup. Speedup is unmeasured. The old 14-hour estimate is invalid: current two-worker timing implies about 67-68 hours for five folds. Repeated Drive input hashing remains unchanged and may contribute to the bottleneck.

**Multiwin:** author13's exact NumPy provenance correction is preserved; six actual CPU tests passed. Its original uncertain row and charge remain counted. Scientific reviewer12 genuinely returned REVISE pending actual A100 evidence; full training remains held.

The new early-login trainer check is delivered: 13B_A1_multiwin_real_trainer_check_upfront_PRIVATE.ipynb, SHA256 42cb96dce6f90694ea725bc575bbc596c7144cc19a0b8bb30af4894e6dfccd8b. Source d3859da8 passed 12 tests and qualified APPROVE df553924, report 1a8c819d. Claude judged its worker boundary equivalent for the stated purpose. Parent Drive is mounted first; the unchanged scientific worker runs in separate mount, process and network namespaces with interactive storage hidden. Actual local positive/negative controls passed. Actual Colab support is still unmeasured: an early control must pass before pip/GPU work, with no weak fallback. Compact evidence is saved automatically without late prompts. Use this instead of review12's late-prompt file.

Next: Partho runs the new check in a fresh default A100 session, estimated 10-25 minutes plus brief setup, then the scientific reviewer judges its authentic result before full delivery. Pnorm_v2's analogous check template was corrected privately, but its existing A100 PASS remains accepted and must not be repeated for packaging alone.

**L:** author3 and scientific reviewer3 are complete, with REVISE for actual A100 integration/checkpoint/memory evidence and baseline metric comparability. The exact author module and five passing host test groups remain preserved. No full L release or memory-fit claim.

The updated preparation file is delivered: 13B_A1_L_prepare_upfront_PRIVATE.ipynb, SHA256 e5f4770b544c496d22494534d2453d7ec6368e6624b6832da4c98eb7b119dd77. Its preparation-only entry and scientific module are unchanged; the new qualified operational review moves logins and snapshot to the first cell. It verifies inputs and baseline bindings, generates authentic ResEncL plans, and returns before trainer construction. Preparation time is unmeasured.

Next: verify the genuine returned plan receipt and configuration, then qualify the exact plan with actual A100 iterations/checkpoint reload and scientific review. Never substitute M plans or synthetic fixture plans. An 80 GB result does not establish 40 GB fit. Exact original Sprint12 metric source is available for reviewer judgment, but source similarity is not independent historical training attestation. Do not spend an author call merely to restate missing hardware evidence.

**Meeting:** author3/reviewer3 completed with preparation-only APPROVE and 12 synthetic tests. Accepted code addresses packed masks, original Sprint13A reconstruction and combined exclusion membership. Real use still needs an immutable source manifest/contract, authenticated external admission, qualified existing access and genuine independent full-stack landmark/laterality QC. No real cases were selected or images rendered. Freeze the predetermined six-case rule before inspecting anatomy. Native MRI/transforms are unavailable; label CT-space derivatives honestly. Recorded outer folds do not establish nested-independent training. Two meeting-purpose calls remain for a concrete input workflow.

**Accepted science:** item6, synthesis, Idea2's fixed 3x3 analysis and smoothing are complete; do not rerun. Sprint14's 352 rounded matches share saved fits/cohort and do not establish independent retraining. Preserve Idea2's inspection limitation. Smoothing did not establish useful general small-component rescue and increased fragmentation.

**Timing and system:** timing author24's CPU integration PASS remains preserved. Reviewer16 failed before admission on confined ledger access; no GPU timing result exists. Reconcile its separate funded scope without borrowing purpose-specific calls. The author sandbox and future Claude-operator/OpenAI administrative route remain unfinished. Defer unrelated infrastructure.

## Calls, spending and judgment

Scientific batch 134/140: two returned-Colab, two L and two meeting calls remain. The explicit 12-call approval establishes 140; the later bracketed 140/136 sentence adds nothing. UTC-day usage is 42/50: 7 authors, 8 scientific reviewers, 25 administrative implementation reviews, 2 standalone direction checks. Purpose breakdown is in STATUS.

Non-Colab item4: $24.487001 billed plus $91.029622 reserved, $115.516623/$150. Timing $5.405445/$25 is included; synthetic CPU $1.118950 awaits billing. Total $1,275, projection $1,200 and item6 $100 stay unchanged. Known Claude charges total $561.00433825; author dollar costs are unavailable. This continuation added $16.22566475 across four administrative calls, including one direction check and one disqualified review. No scientific call or provider compute was added.

Latest Claude judgments: operational worker/watchdog route APPROVE; qualified implementation APPROVE for resume/early logins; qualified APPROVE of the trainer boundary's equivalence. No explicit new standalone PROCEED label is inferred. Necessary repairs were combined; unrelated components stayed deferred.

Review 3dafcfcb is terminal FAILED because the required manifest Read did not qualify. Its native approval is unusable; the $4.74497425 charge remains counted. The successor packet retained the entire affected component and full scientific fixtures while excluding unrelated repository history, without changing reader or qualification limits. Registered request 1d52ba10 was never started and is superseded. Reviews 9012c065 and df553924 are complete; every start is consumed.

## Resume safely and do not duplicate

1. Read the private handoff and verbatim operator decisions; confirm operator ownership. The goal tool may retain a stale funding block; actual funding supersedes that condition. Do not create another goal or claim completion.
2. Check free space before large steps: warn below 15 GiB, stop below 8 GiB. Last observation: C: 11.9 GiB; server 101.7 GiB.
3. Reconcile native units and ledgers using existing read-only service-account tools before launching anything. Current stop: no running model call or research service; five original maintenance timers remain waiting. Seven historical uncertain rows retain their prior qualifications and must never be blindly retried.
4. Do not restart 3dafcfcb, superseded 1d52ba10, completed 9012c065 or df553924. Do not repeat prior batch140, multiwin recovery, L installation/amendment or consumed author3/reviewer3 starts. No new model/compute job is scheduled by this handover.
5. External Colab state is operator-reported. Await returned evidence, verify source hashes and terminal records, and carry it through the scientific lane. Never infer completion from a missing process or partial log.
6. At every stop update STATUS, CURRENT and HANDOVER in place; privately back up evidence with server hash verification; scan and push remote-server plus safe projections. Never push private ancestry. The publication scanner withheld tools/colab_mounted_drive_worker.py for an infrastructure/credential-path finding; its exact reviewed bytes remain private. Public code is an archive, not a standalone deployment.
7. The root-checkout mirror was previously blocked by automatic review; do not retry that write through an alternate path. Current public branch documents and the canonical private handoff are authoritative.

Access names only: existing server SSH, research service account, OpenAI author login, Claude reviewer login, Modal, Google Drive and GitHub. Never print or copy credentials. No setup change is needed while the existing access works.

No Swap point: the timing result and installed opposite-family operator-review route are missing, and external jobs have not reached a clean stop. Rotate only at the agreed milestone or weekly boundary, never mid-task.
