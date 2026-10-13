# Colab resume: folder-creation repair

Qualified implementation APPROVE31e4ae99, sourcec7dac565, report0b3a1e80; 54 synthetic/source tests passed. Actual corrected Drive/GPU execution is not yet observed.

Action needed: move only the two operator-identified empty duplicates to Drive Trash after rechecking each is still empty. Keep both populated roots and all checkpoints, logs and lease records. No permanent deletion. The correction still refuses duplicate names; it does not choose a folder or perform cleanup.

If pnormct remains idle, use its new file below in a fresh default-runtime A100 session, high RAM, Run all unedited. Ensure the old runtime is disconnected and its lease expired. Complete all first-cell prompts and wait for **All logins done, you can leave now**. No later interaction is requested. Checkpoint metadata supports next_epoch85; the runtime must verify payload and bindings before resuming. Never overlap sessions for one arm.

Pnorm_v2 is last reported preprocessing with a live lease. Leave it alone. Use its corrected file only after intentionally stopping the old runtime and allowing its lease to expire. If either earlier operational resume file has already begun training successfully, let it continue; this release does not migrate an unknown operational-release binding.

New result roots are created only through the mount. Drive API GETs verify a unique, owner-only parent and result folder. If the API sees a folder that the mount cannot see, it waits and then refuses; it never creates a second folder. Input hashes/membership, scientific modules, lease/CAS and checkpoint protection remain unchanged. Workers and watchdog remain enabled.

## Exact files in Downloads

- **13B_A1_pnormct_resume_folder_fix.ipynb**
  SHA256: b8d42af4050ee5b95f12f38fef0eb3d1ef5fdd15fd3a2a1332edbf530b50856d

- **13B_A1_pnorm_v2_resume_folder_fix.ipynb**
  SHA256: 211d947fb0802fc2c40294e661afc148142c0120b2444dc30b8d57840b0e7032

- **13B_A1_L_prepare_folder_fix_PRIVATE.ipynb**
  SHA256: 3be767f7bcf878b00575af40e92e9d22bdc457975262625ad47ff614fd2358d9

L is preparation-only, not full training. Multiwin's delivered synthetic trainer check is unchanged; its future full notebook must install the same reviewed folder hook before release. Future full-arm deliveries require this hook in parent and executing child, or an independently reviewed equivalent. Unknown scientific-module hashes refuse.

Next expected evidence: checkpoint selection and initial completed epoch timings after pnormct starts, provisionally 15-30 minutes including setup. Input verification may extend this; speedup remains unmeasured. Keep executed notebooks and results private.
