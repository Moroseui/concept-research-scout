# Research status

- Idea 2 is accepted; existing server inputs are available for the next reviewed analysis.
- New arms remain first: multiwin/pnormct, then pnorm_v2, then L; repeats are parked.
- Pnormct now has a corrected notebook that passed its pure synthetic tests; scientific review is running.
- Multiwin remains parked at its 20-call limit; no corrected notebook is ready yet.
- Real trainer integration still needs a compatible Python3.13/A100 environment; no GPU job is running.
- Billed item 4 compute is $24.487001; known Claude charges are $290.76127125. Author dollars are unavailable.
- Action needed: none. Scientific verdict expected around12:10-12:20UTC; delivery awaits real integration. [Execution plan](13B_EXECUTION_PLAN.md).

## Current direction and evidence

One preconfigured notebook per arm: preprocess once, then train and score folds 0-4 sequentially for 250 epochs each. Resume the current checkpoint and verify/skip completed folds. Use Colab's default runtime and A100, private Drive results, frozen hashes and development-99/excluded-49 membership checks. No per-fold delivery, Colab metering, separate smoke or supervised segments.

Multiwin and pnormct are first for two parallel human sessions; pnorm_v2 follows, then L with actual A100 memory-fit evidence. Zscore and histeq remain held. Sprint 12 A1 is the provisional comparator; small differences cannot be interpreted without a later Colab repeat.

Original baseline fold 0, fold 1 and a later fold-0 retry failed at nnU-Net trainer initialization with KeyError continue_training. Original hash/membership checks passed; preprocessing remains. Scientific author 10 supplied corrections, an arm-level notebook and a real trainer fixture. Its pure synthetic integrity test failed because the fixture's windowed values became constant. The author owns that correction; the protective nonconstant check stays in place. No actual trainer iteration has yet run.

Every arm needs actual nnU-Net trainer construction and at least one real training iteration before delivery. Static and mocked tests do not qualify. Subprocess failures must be printed. Historical notebook bytes and approvals remain preserved but held.

## Implementation and live work

Multiwin's reader repair fa687145 is installed and native-qualified. Scientific review 9 then failed at 30 turns without submission/verdict; all 20 calls and its $5.43188975 charge remain. The run stays parked under agreed Claude SIMPLIFY direction.

Distinct pnormct admission release 45c6b7de passed 200 tests and independent Claude APPROVE e8048d6b/report3f3a1a0e, then installation and native zero-call transport checks. Two pre-allocation environment failures were preserved. The unchanged initializer registered the run once after the existing Git identity and normal service environment were supplied.

The initial author start stopped before reservation at ANALYSIS_REVISION_POLICY_SCOPE. Candidate 885c737b validates the exact question and supplies the legacy revision/zero-offset interface, with unchanged limits and exact premodel recovery. It passed 191 tests and independent Claude APPROVE 6715841e/reportcd575d73. Installation, native author/reviewer role-admission checks, full author input and transport all passed. Recovery preserved the original failure and created no allowance.

Pnormct author 2 completed and its corrected notebook passed all five controller synthetic test groups, including five execution-module tests with none skipped. These are pure-function tests, not real training. Notebook hash30bb6ba0d2904cff6f7725c40693dd5b7ef196989f23455e46d6814b12c986f6; exact module33153177657c1f2a3383bcd50fffb393a571514c3363f7ef2c24f131d48251f2.

Scientific review 1 is RUNNING, confirmed at 11:55 UTC. Expect the verdict around 12:10-12:20 UTC. The required actual nnU-Net trainer iteration remains outstanding. Its authored fixture requires Python3.13/A100 and saves a checkpoint; it does not test production loaders or checkpoint reload. Existing Python3.12 pinned image cannot run that unchanged. No GPU reservation or launch; delivery remains held.

Author 1's format-refused draft, original call and charge remain preserved. Repair b84baccd passed233tests and independent APPROVE fc419017/report48b558ca, then installation, native no-call qualification and exact recovery. Author2 corrected the draft through normal accounting; no operator scientific edits or new allowance.

Timing, the GPU adapter, sandbox and opposite-family administrative capability remain deferred/uninstalled. No Swap point.

## Accepted results and other workstreams

Idea 2's single saved-output CPU execution completed in about six minutes. Before/after hashes matched 728 frozen inputs and four package files; all 891 planned cells completed, with 99 development patients and zero excluded overlap. There were 792 saved-table checks with maximum error zero and 198 mask checks. Interpretation and normal finalization are accepted. The reviewer inspected smaller outputs but could not directly read the two largest tables; do not claim full independent numerical verification. See [accepted report and scope](idea2_fixed3x3/README.md).

Item 6 diagnostics and synthesis are accepted. The Sprint 14 comparison's 352 rounded matches use shared saved fits/cohort, not independent retraining. The next analysis intake preserves the author's proposed fixed-amount smoothing comparison. Meeting preparation uses the accepted fixed six-slot selection rule; real panels await asset provenance and geometry checks. No cases have been selected or private images opened for that plan. Model calls are currently serialized by the installed guard.

At 11:07 UTC the existing 728 saved-output files were checked by metadata only: all were regular, readable and size-matching. No patient payload was opened or rehashed. The next analysis can plan around these existing server inputs, subject to the scientific author's selection and fresh before/after hash checks. Meeting asset mapping confirms that the inspected inventories do not establish a follow-up MRI or clinical source; project-wide absence is not inferred.

## Spending and daily calls

Item 4 non-Colab stage-1 exposure is $115.516623/$150: billed $24.487001 plus retained reservations $91.029622. Timing commitment is $5.405445/$25 within stage 1; $1.118950 synthetic CPU awaits billing. Item 6 cap $100; item 4 total $1,275 and full-training projection gate $1,200 remain unchanged. Colab is unmetered. Release excess reservations only after provider billing confirms a closed attempt's actual cost.

12 October UTC: 44/50 calls: 11 scientific authors, 8 scientific reviewers, 23 administrative implementation reviews and 2 standalone direction attempts. Scientific batch109/128; pnormct3/20. Five of the additional16Colab slots are used, leaving11. Known completed Claude charges$290.76127125; live scientific review charge and author dollars unavailable. Non-Colab item4 exposure$115.516623/$150 = billed$24.487001 plus retained$91.029622. No cap change or new GPU reservation.

| Type | Count | Purpose |
|---|---:|---|
| Scientific author | 11 | Idea 2 code/interpretation, baseline/multiwin preparation, pnormct draft and format correction |
| Scientific reviewer | 8 | Idea 2, baseline, multiwin and live pnormct review; failed attempts preserved |
| Administrative implementation review | 23 | Repairs, including distinct pnormct admission, policy interface and format feedback |
| Standalone direction check | 2 | Disqualified direction attempt and qualified SIMPLIFY retry |


## Judgment log highlights

- Preserve all failed attempts/charges and preprocessing; scientific author owns scientific corrections.
- 12 October 09:45UTC:SIMPLIFY agreed; cut further recovery on exhausted multiwin.
- 12 October 10:36UTC:PROCEED, one bundled direction/accounting round; admit the distinct pnormct question under unchanged limits.
- 12 October 10:42UTC:continue only the uncreated lane after exact context/state verification and restoring existing non-credential identity/service environment; no counters or state reset, setup originals retained.
- 12 October 10:57 UTC: Claude APPROVE and PROCEED with a caution to simplify, agreed in one bundled round. Install only the immediate correction and launch the author; defer generic infrastructure. Exact recovery preserves all refusals and creates no allowance.

## Backup and exclusions

Last verified public backup before this update: dc915acd9f5a5ceef5ed8c9e334ee7b119bab450. Current changes require privacy, secret and infrastructure scans before pushing. Latest measured C: free space is 16.56 GiB; latest private checkpoint verified 544 files by hash, with server free space112.4910 GiB before and112.4753 GiB after. No local files were removed. Disk guard warns below 15 GiB and stops below 8 GiB. No larger disk requested.

Withhold evidence folders, review packets, ledgers, native streams, private operator records, raw private branch ancestry, patient rows/identifiers, membership maps, images, masks, weights/caches, credentials and infrastructure identifiers. Private bindings withheld include COLAB_MULTIWIN_RECOVERY_PRIVATE.json, COLAB_RUNTIME_FAILURES_PRIVATE.json and COLAB_PATCH_READING_FAILURE_PRIVATE.json. Returned executed notebooks/records and verbatim private approval bindings also stay private. Safe source/test projections are scanned separately. Never merge main or edit BACKLOG.

New excluded bindings:COLAB_PNORMCT_NATIVE_PRIVATE.json and COLAB_PNORMCT_QUESTION_PRIVATE.json flagged private-record/infrastructure or publication-content scans. Policy failure checkpoint, packets, streams, Drive metadata and raw candidate history also remain private. Only the eight clean installed source/test files are projected.

The installed policy repair adds three clean source/test projections. COLAB_PNORMCT_POLICY_FAILURE_PRIVATE.json is excluded by the private-record scan; its original refusal, review packet and streams stay private.

12 October 11:44 UTC judgment: recurring format failure repaired by reusing the existing checker and counted author attempt 2; no operator edit to scientific bytes. Claude accounting/direction consultation bundled with review fc419017. Candidate b84baccd uninstalled; 233 tests passed. New frozen format checkpoint and all draft/stream/evidence files remain private.

12 October 11:51 UTC judgment: format repair independently approved and installed; zero-call native qualification and exact recovery passed. Author2 launched normally; originals and all limits preserved. Latest explicit Claude direction remains PROCEED with a caution to simplify (10:57 UTC): only immediate repairs and the real fixture; defer generic infrastructure. The 11:47 UTC format review approved the accounting/safeguard repair but did not return the requested separate direction recommendation. Do not represent it as a new PROCEED. Include that question in the next necessary review rather than add a standalone call now.

New installed public projection: three clean format-helper/runtime/test files. COLAB_PNORMCT_FORMAT_FAILURE_PRIVATE.json is excluded by the private-record scan, along with the packet, native streams and preserved drafts. Latest private checkpoint verified40files: server112.1675GiB before/112.1645GiB after; later source transfer left112.0103GiB. No local deletion.

12 October11:55UTC:author2 COMPLETE/controller pure synthetic PASS; normal scientific review1 started once. No delivery or real-trainer claim. The existing integration adapter remains an unbound multiwin draft and must not be installed or executed. See private INTEGRATION_HANDOFF_PRIVATE.md for exact authored requirements.
