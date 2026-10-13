# 13B execution plan

Updated 13 October 2026, 04:34 UTC. New experiments first; repeats are parked. Scientific authors write the notebooks and analysis; Claude reviews them. Every arm needs a real nnU-Net trainer construction and at least one training iteration before full notebook delivery.

| Order | Arm and folds | Venue and owner | Current release condition |
|---|---|---|---|
| First, session1 | A1_multiwin,0-4 | **Partho on Colab**, default runtime,A100 | Author12 and five synthetic groupsPASS; Synthetic-only package APPROVE/delivered; Partho runs freshA100check; fulltrainingheld until returned evidence is scientifically accepted |
| First, session2 | A1_pnormct,0-4 | **Partho on Colab**, default runtime,A100 | Delivered unchanged after real trainer PASS; Partho reports RUNNING |
| Next | A1_pnorm_v2,0-4 | **Partho on Colab**, default runtime,A100 | Code APPROVE and five native synthetic groupsPASS; reviewed A100 check delivered, actual result pending before full delivery |
| Then | A1_L,0-4 | **Partho on Colab**, default runtime,A100 | Author2 COMPLETE;5of5hostgroupsPASS; reviewer2 REVISE. Exact A100 memory-fit evidence pending; baseline files authenticated but scientific binding pending; Colab calls exhausted |
| Parked | A1_repeat and A1_repeat2,0-4 each | Partho on Colab later | New arms must have results first; saved preprocessing stays |
| Held | A1_zscore and A1_histeq,0-4 each | No run | Coverage-source provenance unresolved |

Each released arm gets one preconfigured notebook: preprocess once, train and score folds0-4 sequentially at250epochs, automatically resume the current checkpoint and verify/skip completed folds. Frozen file hashes and development99/excluded49 membership fail closed. Results stay in a distinct private Drive folder per arm. Subprocess errors print on failure. No per-fold files, Colab accounting, balance prompts or supervised segments.

**Current action for Partho:** run/return multiwin first, then the delivered pnorm_v2 synthetic trainer check in fresh A100 sessions; leave pnormct running. Pnormct's unedited all-fold notebook is already delivered and running, SHA25630bb6ba0d2904cff6f7725c40693dd5b7ef196989f23455e46d6814b12c986f6. Built-in estimate14hours/94.78CU. Return completion/error and executed notebook; private Drive outputs use the built-in arm folder.

Send each full training file immediately after its required checks pass. When both first arms are released, run two parallel Colab sessions, one per arm, each processing five folds sequentially. Exact filenames, hashes, built-in paths and result-return instructions accompany each delivery. The system verifies private Drive results and routes them to analysis as they arrive.

At Sprint12's measured36seconds/epoch,5folds x250epochs imply12.5training hours before preprocessing, validation and checkpoint overhead, or84.63CU at6.77CU/hour. This is a reference, not a new-arm measurement. Multiwin's prior15-20hour estimate and L's35-45hour estimate remain provisional; replace them with measured steady-state timing. Original1001units buy about147.86A100hours at that rate; the balance does not limit the plan and Partho manages purchases. Automatic resume handles session interruptions.

Compare each arm provisionally with Sprint12A1. Small differences are not interpretable without a later Colab repeat. Attribute changes to placement versus amount, size, region and fragmentation; no efficacy claim from code or integration tests.

**Parallel server work:** Pnorm_v2 code is scientifically approved and all five native synthetic groupsPASS after the independently approved harness repair. The reviewed synthetic trainer-check notebook is delivered; expect10-25minutes per operator-run check. Its filename is13B_A1_pnorm_v2_real_trainer_check_PRIVATE.ipynb, SHA256b28ca24032ad0cd4f511fd05cb5b7d94069d606062f5092edda53700698f62ac. Scientific code is unchanged and the original failed test remains preserved. Item6, Idea2 and smoothing interpretations are accepted. L author2 and reviewer2 are COMPLETE. All five host groups PASS; real A100 evidence and scientific binding of the authenticated Sprint12 metrics remain required. The [meeting reading sheet](MEETING_READING_SHEET.md) is ready; synthetic rendering is scientifically approved; private panels await qualified source provenance and real-mode authoring, with no reliable panel ETA.

**Timing diagnostic:** current-resource RunA versus increased-CPU/augmentation-worker RunB remains approved within its $25 sub-cap. RunB first if both will not fit. Author24's real CPU integration passed; reviewer16 failed before reservation on confined ledger access. The established reader can be reused, but old timing allocation rules also predate the current124-call history. Reconcile retained timing authority with the later purpose-specific batch allocation before preparing a complete narrow repair; no existing allowance is silently repurposed. No GPU job is running, and Colab arms do not wait for this repair. Timing ETA follows repair approval; no measured steady-state projection is claimed.

**Money and limits:** Item4 non-Colab stage1 $115.516623/$150: $24.487001 billed plus $91.029622 retained reservations. Timing exposure $5.405445/$25 is included. Total $1,275 and full-training projection gate $1,200 unchanged. Colab is unmetered by operator decision; printed units are estimates only. 13October model usage16/50;12October closed70/100; scientific batch127/128 leaves0Colab and1meeting review, no analysis allocation. The request for8additional Colab calls is pending, not approved. Detailed audit and costs: [STATUS](STATUS.md).

Sprint12 baseline readiness update,13October03:30UTC: the five existing A1 fold tables and five receipts were authenticated against the frozen input contract on both server and Drive. Their99development cases match the frozen13B shuffle101 folds exactly (20/20/20/20/19), with zero excluded overlap and no duplicates. No upload or new run is needed for those files. This is input identity and pairing evidence, not a computed comparison or scientific acceptance. Both common-support and native Dice columns are present; the author/reviewer must select compatible metrics and bind the files in L's normal input mapping. L's original findings remain open until reviewed; exact A100 integration/memory evidence is still missing. No live lane, scientific artifact, allowance or credential changed.


Meeting author1 and scientific reviewer1 are COMPLETE. The selector/renderer passed 26 isolated synthetic tests and received scientific APPROVE, report48f8197f, for synthetic preparation only. Review cost $3.22294775; accepted tool-submission record81a38484 and console hash were verified. The original COMMIT_SPEC checkpoint is preserved; the approved source amendment has queued author2, with real execution still unauthorized. Do not replay either call or treat synthetic approval as real-case validation.

The program intentionally refuses real execution and accepts synthetic identifiers only. Author2 is addressing the documented source limitations; normal scientific review follows. One approved meeting review remains. No cases have been selected and no image payload opened. Clinical CSV bytes were read only for hashes and header extraction; no clinical values were copied or interpreted. No patient executor is installed.

The frozen archive member manifest identifies CT-space DWI and ADC for all 99 development patients, but no native follow-up MRI or transformation sidecars. All 198 development clinical CSVs match the recorded archive-member size and CRC; their current SHA256 hashes are saved. Only headers were extracted, with no clinical values copied or interpreted. This is a member-identity check against the historical manifest, not a fresh cryptographic reread of the whole archive.

The matching public v3 clinical data dictionary is hash-verified. Five observed field names lack exact dictionary matches; aliases, units and prospective availability remain for the scientific author/reviewer to judge. The next scientific amendment must address the released imaging layout and missing native/transform evidence without relabeling derivatives or bypassing checks. Image hashes, geometry and model/output provenance remain unqualified; no case selected or image payload opened.


Judgment: apply the narrowly reviewed source amendment, then use one existing meeting author slot; preserve original approval and all safeguards. Claude implementation APPROVE at04:26UTC. The bundled direction question was unanswered, so latest direction remains03:13UTC PROCEED.


Judgment: checked only the frozen 99 development clinical files against the existing archive manifest, then pinned the release data dictionary. No scientific mapping or image processing performed; no Claude call needed for source inventory. The native-MRI/transform limitation requires a scientific amendment, not an operator exception.


The source-amendment utility03443eff passed193regression tests and received independent Claude APPROVE, reporte273e66f, costing $8.928981. Exact source and approval were verified on the server and the one-use amendment was applied successfully with zero model calls and no added allowance. Original scientific approval, calls, counters and limits remain preserved. Meeting author2 is now RUNNING through the unchanged installed scientific lane; one allocated scientific review remains. Real execution stays held. Do not replay transfer, amendment, author start or prior completed calls.

The accepted Idea2 and smoothing code emits aggregate reports; it does not persist the per-case selection table or derived masks assumed by the first renderer. Exact accepted sources are now prepared for the scientific author to judge reproducible reconstruction from frozen predictions, with no training or changed case-selection rule. This joins the known native-MRI/transform and clinical-mapping gaps in one amendment question.
