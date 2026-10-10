# Diagnostic fixture correction and scientific handoff

The single native CPU attempt ended with a missing `continue_training` field in the author-owned fixture. Its full output, reservation and failure remain preserved. The production path already supplies this field. No GPU timing result is available.

Claude agrees on the shortest recovery path: a bounded scientific-author correction, then reviewer 15 judges the complete correction and authentic failure. A minimal implementation change must receive tests and independent approval before enabling this handoff. It must never turn FAIL into PASS, claim the corrected fixture was executed, discard review 14, or consume the separate whole-plan review slots.

No second CPU rehearsal and no automatic GPU retry. The first Run B remains subject to scientific judgment and normal admission inside diagnostic $25, stage $150 and total $1,275. The $1,200 full-training projection gate remains unchanged. The failed attempt's $1.118950 reservation stays counted until qualified billing reconciliation.

This is a draft scope only: no source edit, new allowance, installation or author call has occurred. Scientific code and conclusions remain the author/reviewer's responsibility. Reuse the existing author, controller and reviewer paths; no optional subsystem or timer.

The concrete draft is now committed as `e50aa51bd1973517973bb94ba0056c1f375a530d`. It reuses the existing author/reviewer service and isolates original-failure verification. A cold server rehearsal authenticated the actual failed attempt and admitted author 20 only in disposable ledger copies; live history remained unchanged. Implementation review and installation are still pending. No scientific or compute call has started.

Four changed files are withheld from this public projection: `docs/ITEM4_AUTHOR19_NATIVE_REFERENCE_PRIVATE.py`, `docs/ITEM4_CPU_DIAGNOSTIC_FIXTURE_PRIVATE.json`, `docs/ITEM4_RESPONSE_HOST_PRIVATE.json`, and `tools/install_item4_smoke_response.py`. They contain private records or infrastructure references. The exact private source and prior failed records remain available to the independent reviewer.

Update: genuine independent APPROVE `da282dcc` for source `e50aa51b`; all125 focused tests and cold rehearsal passed. Installation completed with successful held postchecks and zero model/provider calls. Author20 activation is next; scientific acceptance and GPU execution remain separate and held. No second CPU rehearsal or automatic GPU retry.
