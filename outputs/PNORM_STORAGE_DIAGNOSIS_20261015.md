# Pnorm checkpoint and stop diagnosis, 15 October 2026

The repair notebooks have passed independent OpenAI code and packaging review. Partho controls any restart; no arm was restarted here. No existing Drive file was deleted, moved or overwritten during investigation.

| Arm | Confirmed stop | Evidence | Retained latest |
|---|---|---|---|
| A1_pnormct | 14 October, about 17:11 UTC | Terminal attempt traceback: 30-second Drive API timeout while publishing a best-checkpoint lease pointer; child exited with code 1 | Fold 3, next epoch 55 |
| A1_pnorm_v2 | 15 October, 02:50:08 UTC | Terminal attempt traceback: Drive API read timeout in heartbeat; training reached epoch 183 before the child exited | Fold 2, next epoch 180 |

The reported 02:44 time was the last checkpoint time, not the terminal event. Neither terminal traceback identifies storage quota exhaustion or a Colab runtime limit. A transient API timeout is established; its underlying network/provider cause is not. Further Colab output is not needed to identify these immediate failures.

The first pnorm_v2 fold-2 checkpoint is **407,007,931 bytes**, with its recorded SHA256 verified and every ZIP member passing CRC validation. Restricted metadata inspection found current epoch 0, 956 weight entries and an empty optimizer state with one parameter group. This is a valid initial checkpoint, not a truncated upload: momentum buffers have not yet been created. Later checkpoints include optimizer state and are approximately 814 MB. This check did not execute serialized globals or load model weights. Current resume payloads still require the notebook's normal hash verification before loading.

Read-only inventory found **614 checkpoint payloads**: **370 KEEP** (299.9 GB) and **244 CANDIDATE ONLY** (196.9 GB). The private list includes reasons and paths. Completed summaries reference many old checkpoints, so those remain KEEP even if superseded for training. All non-payload files remain retained. Partho decides any cleanup; this is a snapshot, not a deletion instruction.

The repair uses four reusable slots in each new attempt. It never overwrites a currently referenced slot or a historical attempt's file. Publication writes and flushes the candidate, verifies size, hash and serialized structure, then changes the lease reference. Original owner, generation, expiry, CAS, membership and input checks remain. Transient API failures get bounded backoff and individual retry logs; quota exhaustion gets a specific terminal error.

Validation: 97 focused tests passed, including 20-publication bounds, old unbounded-growth control, actual old/fixed heartbeat-loop control, crash windows, ambiguous committed responses, deadline/CAS/ownership refusals, folder guards, watchdog and exact per-arm packaging. Both exact scientific modules also passed actual nnU-Net 2.8.1 CPU optimizer steps on tiny synthetic data: initial publish, one update, checkpoint publish, exact weight/optimizer restore and another update. The old missing-continue_training constructor control failed as expected. These tests used local files and a synthetic lease backend, not live Drive or GPU. A full notebook sandbox remains Claude's next task; no such coverage is claimed.
