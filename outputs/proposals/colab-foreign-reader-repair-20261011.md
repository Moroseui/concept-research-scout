# Colab foreign-ledger read repair

The preparation's own ledger reads pass, but its cross-lane accounting check refused a journal left by the completed analysis lane. Candidate698cca9 uses native SQLite read-only transactions for authenticated foreign ledgers with journals, and preserves the original verified snapshot for quiescent ledgers without journals. Before/after data-file hashes, integrity, path and exact history checks remain. No journal is ignored or removed and no writable paths are added.

189 focused tests pass. Broader results:450 passed,26 skipped,5 failures and9 setup errors; all5 failures and9 errors reproduce on unchanged e687371. The complete real confined replay reproduced the original refusal then passed allowance and terminal checks with every global row unchanged and no reservation/model call. A counter-only prototype and its failed probes are retained privately; final code checks actual database and journal hashes.

Independent APPROVE and direction PROCEED received (report5d014439), followed by installation and verification. The exact reader recovery completed; author3 is admitted and running. The exact zero-admission rearm requires independent APPROVE before installation or use; no extra attempt or allowance is granted. Private workspace/ledger checkpoint is withheld from this public projection. Science and inputs are unchanged.
