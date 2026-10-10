# Timing boundary audit

This is a read-only code and aggregate-log audit, not a revised scientific projection. All original measurements, checkpoint protections and budget holds remain unchanged.

The pinned nnU-Net 2.8.1 source records its epoch-end timestamp before logging, checkpoint saves and plotting. The scientific wrapper records its returned duration after those operations and GPU synchronization. The adapter makes checkpoint saves durable, with hashing, synchronization and two commits. Smoke saves a periodic checkpoint every epoch; full training uses a ten-epoch interval. Best-checkpoint saves can still occur independently whenever the native metric improves.

| Repeat epoch | Returned duration (s) | Native logged duration (s) | Difference (s) |
|---|---:|---:|---:|
| 0 | 262.43 | 241.52 | 20.91 |
| 1 | 103.62 | 65.39 | 38.23 |
| 2 | 93.73 | 61.54 | 32.19 |
| 3 | 86.50 | 61.30 | 25.20 |
| 4 | 77.78 | 61.85 | 15.93 |

The difference is not a measurement of checkpoint cost alone: logging, plotting, synchronization and boundary differences are also included. Native logged durations cannot replace billed wall time or the returned timings. Initial preparation, final checkpoints and actual validation also fall outside these epoch timers.

The scientific author must judge warm-up, workload equivalence with Sprint 12, checkpoint-frequency effects and the evidence needed for a defensible full-plan estimate. No steady-state plateau or affordable full plan is established by this audit. The existing provisional projection and full-training hold are unchanged.

Source fingerprints:
- native_trainer: 7096efb2040135eb60df3c8bf39cdbcc373e299671fcee365b3aff2f4da4dfbd
- author14: 3925313395199992195412e5db908e764e8215df52f59c408ba27619653993d8
- adapter: 060c1afeba306d43c585c0d8973173e7a1da570f8d8614f1851d92667d180d8f
- progress: 221acdc9a0776a01d97d41150c1da4dc8a26fe92fecf3de7579711de755faad1
