# A1_multiwin: ready to run

Scientific review 8 APPROVE, with no findings; all six exact notebook variants passed the installed isolated synthetic suite. These checks used synthetic fixtures only, not patient data or a real Colab GPU.

Finish the remaining A1_repeat folds first. Keep two sessions occupied when your account permits: baseline folds2/3 after0/1, then4. Use a freed slot for multiwin fold0 once all baseline folds have been started; there is no need to leave a slot idle while baseline fold4 finishes. Never duplicate an arm/fold.

1. Upload 13B_A1_multiwin_fold0.ipynb to Colab.
2. Select A100 with the default runtime, then Run all. Complete normal Drive authorization. No settings to change.
3. Use a second available A100 session for multiwin fold1, then use freed sessions for folds2,3,4.
4. Let each fold run all250epochs. Its first epochs are the smoke check; no deliberate pause or separate smoke notebook.
5. After a disconnect, rerun the SAME fold file. It verifies and resumes checkpoints automatically. Do not bypass any input, membership, lease or checkpoint error; return the error text.

The all-fold13B_A1_multiwin.ipynb is an alternative sequential notebook. Never run it alongside individual-fold files for the same arm.

Multiwin uses12channels: the original six scans under the baseline and second fixed windows. Both windows use the same verified raw inputs; no4DCTP. Compare this arm primarily with Colab A1_repeat on the same patients/folds. Sprint12 is additional context. Final conclusions await A1_repeat2 at the end.

Author's unmeasured estimate:3-4training hours/fold,20.31-27.08compute units at6.77CU/hour, plus installation,preprocessing,Drive,scoring and checkpoint overhead. No unit balance prompt or metering gate. Actual timing will replace this estimate.

Private results:
My Drive/isles-pilot/colab-1ad5fafc220b3d65f576ce08/results-full250/A1_multiwin/foldN
for N=0,1,2,3,4; each attempt has its own subfolder.

Leave all outputs in those private folders. Save the executed notebook there too, and report which arm/fold completed or the exact error. The system ingests returned metrics,timing,run summaries and private prediction outputs. Do not publish patient-derived material.

The notebook code is approved for operator-run Colab under the standing full250 direction. This does not authorize automated server/provider execution. No post-review scientific edits or regeneration were made. SHA256SUMS.txt identifies the exact reviewed files.
