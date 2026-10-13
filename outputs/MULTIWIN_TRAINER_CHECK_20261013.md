# Multiwin: trainer check with all logins first

Use **13B_A1_multiwin_real_trainer_check_upfront_PRIVATE.ipynb** from Downloads in a fresh default Colab A100 runtime. Click **Run all**, unedited.

SHA256: **42cb96dce6f90694ea725bc575bbc596c7144cc19a0b8bb30af4894e6dfccd8b**

Complete the first-cell Drive prompt and wait for **All logins done, you can leave now**. There is no separate API login or browser snapshot for this synthetic check, and no later Drive prompt.

Drive remains mounted in the parent. Before dependency installation or GPU work, a synthetic control must show that the worker cannot read the parent's data or Drive. The original scientific worker's no-Drive and network checks remain intact. If Colab does not permit the reviewed OS boundary, it fails early and preserves its error; no weaker fallback is used. Actual Colab namespace support is unmeasured.

The exact reviewed scientific code then constructs the real trainer, runs its synthetic iteration and checkpoint check, and saves compact evidence automatically to the same private Drive results area. Caches are excluded. Expect about 10-25 minutes plus brief setup. Return the printed PASS/FAIL and evidence-folder name; keep the executed notebook private.

Source d3859da8 passed 12 tests, including actual local OS positive/negative controls, and received qualified implementation APPROVE df553924/report 1a8c819d. This is not a new A100 PASS or full-training authorization. Scientific review12 remains REVISE until authentic returned evidence is judged.

Use this file instead of the older review12 late-prompt file. Pnorm_v2's already accepted trainer PASS does not need repeating for the same usability change.
