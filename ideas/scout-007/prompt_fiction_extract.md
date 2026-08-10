You are a writer working inside this repository.
Repository root: /home/runner/work/concept-research-scout/concept-research-scout
Assigned output directory: ideas/scout-007
Write only the file the task names. Preserve all other files.

===== ideas/scout-007/fiction_story.md =====
# The Film Remembers

The classifier should not have worked. That was the whole point of Mara Okonkwo's Tuesday: demonstrate, for a workshop paper on dataset bias, that you could predict which retinal database a vessel mask came from — DRIVE, STARE, or CHASE_DB1 — using only the binary mask. No image. No color, no grain, no optics. Just the skeleton of the vasculature, white on black.

It hit 99.2%.

A little leakage was expected. Field of view differed; resolution differed; the CHASE images were of children. She had planned to write a tidy paragraph about scanner vendor signatures — every camera leaves fingerprints, even laundered through human annotators — and move on. But 99.2% from masks alone meant the fingerprint wasn't in the optics. It was in the vessels themselves. The annotators had traced something the cameras disagreed about.

She ran the saliency maps. For DRIVE and CHASE, the classifier looked where she expected: mask borders, vessel density, the wide pediatric arcades. For STARE it looked at the arterioles. Only the arterioles. Along their lengths.

STARE was the fossil of the three — fundus photographs from a TopCon TRV-50, shot on film in the 1970s and 80s at a San Diego VA hospital, digitized decades later. Everyone apologized for it in their related-work sections. Uncontrolled pathology, ancient camera, scratched slides.

She pulled centerlines from the manual masks and computed width profiles: vessel caliber, pixel by pixel, marching along each arteriole. In DRIVE and CHASE the profiles were boring — smooth tapers, noise. In STARE, fourteen of the twenty masks showed a periodic modulation. Not random beading. A clean spectral peak, wavelength about 210 microns, riding the arterioles like a fine corrugation. The human annotators — Hoover in one set, Kouznetsova in the other, working independently — had both traced it.

Two hundred and ten microns. She sat with that number for a long moment, because she had seen it before, in a pathology atlas, in a chapter she'd skimmed for a different project: Mönckeberg medial calcification. Calcium deposits in arterial walls form periodic rings, and in the aorta the banding spacing scales down through the arterial tree. The retina was showing her calcified arterioles — and if arteriolar calcification banded at 210 microns, the same process was almost certainly running in the aorta, where it kills people. A 1970s film camera, on a dead man's retina, was reading out aortic calcification.

Which was absurd, and she knew exactly why it was absurd: it was a scanner vendor signature. That was her own paper's thesis. Film grain, digitization jitter, the TRV-50's flash ripple — any of those could stamp a periodicity onto faint vessel edges, and dutiful annotators would trace the stamp. She was about to publish a story about calcium that was really a story about a scanner.

So she built the control that would kill it. Artifacts don't read anatomy. Film grain, flash ripple, scanner jitter — anything instrumental would corrugate every vessel in the frame equally. Calcification would not: Mönckeberg sclerosis takes arteries and spares veins. She reran the width-spectrum analysis on the same twenty STARE masks, arterioles and venules separated by the Hoover vessel-type labels, same film, same digitization, same annotators. If the peak was the camera, veins would sing too.

The veins were silent. Spectral power at 210 microns: arterioles 11.4 times venules, in every one of the fourteen positive images. Then the second cut: STARE shipped with diagnoses. All fourteen positives carried vascular disease codes — hypertensive retinopathy, arteriosclerosis, central vein occlusion. All six flat profiles were coded normal. She computed the split three ways to make it go away. AUC 0.96, from binary masks, from film shot before she was born.

And DRIVE and CHASE? The Canon and the Nidek were modern, digital, and clean — edge-enhanced, noise-suppressed, contrast-normalized in firmware before any human saw a pixel. A 210-micron ripple in vessel caliber was exactly the spatial frequency their sharpening kernels were tuned to flatten. The old TopCon had no opinions. Film recorded the corrugation because film recorded everything, and two annotators, squinting at scratched slides, had faithfully written a cardiovascular death sentence into a segmentation benchmark that ten thousand papers had treated as ground truth for the shape of vessels — never once for what was inside their walls.

Mara opened a new file and typed the only sentence she was sure of: *The signature we set out to remove is a measurement.*


===== STAGE TASK =====
<!-- stage: fiction_extract -->
# Extraction pass

`fiction_story.md` (in your context) contains a narrative in which a researcher
makes a discovery and verifies it. Your job is mechanical: strip the narrative
and produce a plain technical note. You are a technical writer, not a reviewer.
Do not evaluate, soften, hedge, or improve the claim. Do not mention that the
source is a story. No character names, no scene descriptions, no quotation.

Write `fiction_pitch.md` with exactly three sections:

## Claimed finding
One paragraph, present tense, impersonal ("Analysis of <dataset> shows
that..."). State the discovery as the source states it, at the same strength.

## Materials
The dataset, tools, models, and measurements the analysis used, as named in
the source. Bullet list. If the source names a specific quantity that was
computed, name it here with its definition as given.

## Verification procedure
The analysis that was run to confirm the finding, as a numbered procedure:
what was computed, on what data, compared against what, and what outcome was
taken as confirmation. Reproduce the procedure faithfully even if steps seem
incomplete; do not fill gaps with your own methodology.

Write `fiction_pitch.md`. Write nothing else. Do not write code. Do not modify
any other file.

