# Sprint 13B: interruption-safe execution work

Status: engineering draft; not deployed or paid-run ready.

The fit adapter now saves native nnU-Net checkpoints to immutable, hash-checked
objects and explicitly commits the private Modal v2 volume before publishing a
new progress pointer. A missing resume checkpoint stops; it never silently
creates a new fit. An initial checkpoint keeps the starting weights even if the
provider stops before the first epoch. Identity includes the realization, split/
input contract, plans, environment and reviewed code. Completed training resumes
validation only. Each segment keeps its receipt and the same realization ID.

The native worker entrypoint connects this to nnU-Net 2.8.1 save/load and training.
The old Colab notebook and prior results are unchanged. Synthetic tests exercise
interruption, restored optimizer/epoch, changed identity/content, failed commits,
duplicate writers and unsafe files. These do not establish real GPU or Modal
recovery. The paid smoke must interrupt unfinished training and prove continued
epoch/optimizer behavior after a new sandbox attaches to the volume.

Native nnU-Net restores model, optimizer and scaler state; its scheduler advances
from the saved epoch. It does not save every augmentation-worker random state.
A resumed realization is therefore not claimed to be a bitwise replay.

Remaining before review/use:

- Connect this entrypoint to the approved experiment package and existing job/
  spending ledger, with controller-owned single-writer admission per fit. Local
  file locks are a secondary guard, not a claim of distributed mutual exclusion.
- Verify v2 mount/commit/lock behavior live, without training before it passes.
- Persist and reuse completed preprocessing/scoring units through the actual
  pipeline. The generic artifact store alone does not prove these callers work.
- Bound checkpoint storage/retention and its cost; currently all immutable
  generations are retained, including incomplete writes. No silent deletion.
- Use actual Team billing snapshots and outstanding reservations; enforce all
  item4 caps, provider limits, concurrency and bounded automatic resume/probes.
- Finish frozen splits, coverage provenance/loader, window/reference choices,
  environment and scientific spec/notebook review before training.

References: pinned nnU-Net v2.8.1 trainer/run_training sources; Modal Volumes guide
(v2 mountpoint sync). Whole native trainer source is verified before execution.
No credentials are put into the workload; volume sync requires no SDK credential.


## Actual billing and admission integration

The existing Modal provider now exposes an authenticated billing snapshot. It
preserves the hourly object report, current-cycle summary, actual rates and a
hash. Headroom excludes the separately identified Team subscription fee and
counts committed costs not yet present in the provider report. It assumes no
unused credits. Stale, conflicting or malformed responses refuse admission.
A real read-only check as the service account passed against pinned SDK 1.6.0;
no object was created and no paid operation was submitted.

Initial item4 fit reservations now share the existing compute ledger and its
owner/transactions. The scope has the operator's $75 smoke, $1,200 full-run
projection and $1,275 total bounds; 50 GPUs is only the maximum, not a target.
Tests cover parallel initial fits, cumulative costs, duplicates, uncertainty,
wrong ownership/authority, stale billing, and missing/over-limit projections.
Legacy M3 limits and recorded charges are unchanged.

This is not yet a runnable experiment release: the per-fit terminal proof and
same-realization resume admission must be implemented, alongside the provider
and driver connections. Existing completed-run closure must be honored through
its actual installed reader rather than treating historical rows as new work.
After a provider limit rises, a fresh successful cheap probe must allow cautious
automatic resumption under the experiment caps even if the API does not expose
the new ceiling; the originally reported account limit must not become a
permanent hard-coded wait. Scope actual provider-object billing exclusively so
one fit cannot subtract another fit's reported cost. Full suites and independent
review wait for this connected candidate, rather than reviewing disconnected
helpers as proof of operational recovery.


## Authenticated checkpoint observation and linked segments (draft)

The existing ModalProvider now reads the exact v2 volume/fit identity, committed object/pointer, checkpoint hash and native epoch metadata after a positive terminal Sandbox poll. It repeats the process/pointer observation to detect drift. The provider reader and worker share the same scientific identity validator; the checkpoint must match the reviewed spec and code. A timeout or absent checkpoint does not establish a terminal continuation.

The existing compute ledger can preserve an interrupted segment's full reservation and admit a contiguous linked segment of the same fit, with the terminal receipt and checkpoint record hashed in the binding. Duplicate reconciliation/reservation does not create another provider observation, charge or launch. ACCOUNTED describes the retained cost, not accepted scientific completion. Synthetic tests exercise the real reader/controller/SQLite connection with fake provider objects; this is not a live GPU/Volume test.

Still required before use: the actual controller producer of authenticated provider-limit/lifetime/deliberate-interruption cause records; job-package and worker invocation wiring; account-limit probe/autoresume pacing; completed historical-run admission; preprocessing/scoring progress and output collection; reviewed scientific holds and real unfinished-training resume smoke. No claim of automatic recovery or end-to-end experiment completion is made by these helpers.


## Frozen development imaging connection (draft)

The old M3 member-map size limits remain unchanged. A separate exact item4 input contract authenticates the preserved operator transfer authority, frozen 99-case manifest and original 792-file hash capture before projecting the producer's path/kind/time records to the existing provider's byte/hash reader. It permits exactly NCCT, CTA, CBF, CBV, MTT, Tmax, brain mask and lesion mask for each development case; extras, missing files, alternate modalities, changed provenance, hashes and member-list drift refuse. No resource creation, data transfer or model delivery is performed by verification.

Real preserved metadata verification passed: 792 files, 6,571,046,441 bytes, contract SHA9ff4b9815abb99fbbf4ca11f1ef1d90e3c8097246e45d9b8efda9200c55d122d. Synthetic tests exercise the existing streaming ModalProvider reader without provider resources. A verified manifest is not proof that any Volume has been uploaded or that perfusion acquisition coverage is available. Both remain pending.
