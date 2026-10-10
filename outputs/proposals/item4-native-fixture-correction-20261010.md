# Diagnostic fixture correction and scientific handoff

The single native CPU attempt ended with a missing `continue_training` field in the author-owned fixture. Its full output, reservation and failure remain preserved. The production path already supplies this field. No GPU timing result is available.

Claude agrees on the shortest recovery path: a bounded scientific-author correction, then reviewer 15 judges the complete correction and authentic failure. A minimal implementation change must receive tests and independent approval before enabling this handoff. It must never turn FAIL into PASS, claim the corrected fixture was executed, discard review 14, or consume the separate whole-plan review slots.

No second CPU rehearsal and no automatic GPU retry. The first Run B remains subject to scientific judgment and normal admission inside diagnostic $25, stage $150 and total $1,275. The $1,200 full-training projection gate remains unchanged. The failed attempt's $1.118950 reservation stays counted until qualified billing reconciliation.

This is a draft scope only: no source edit, new allowance, installation or author call has occurred. Scientific code and conclusions remain the author/reviewer's responsibility. Reuse the existing author, controller and reviewer paths; no optional subsystem or timer.
