You are a writer working inside this repository.
Repository root: /home/runner/work/concept-research-scout/concept-research-scout
Assigned output directory: ideas/scout-009
Write only the file the task names. Preserve all other files.

===== ideas/scout-009/fiction_story.md =====
# The Depth of Breath

The aorta was gone and the score hadn't moved.

Mara Okoye ran the occlusion again to be sure. She had painted a cylinder of air over the descending aorta of NLST participant 108644 — erased the vessel entirely, calcium and all — and fed the volume back through CT-CLIP's aortic-calcification head. The logit dropped from 0.91 to 0.89. Then, because it was two a.m. and she was past caring about elegance, she started masking everything else, one structure at a time. Heart: nothing. Spine: nothing. When she blanked the dome of the left hemidiaphragm, the score fell to 0.12.

The model was scoring aortic calcification by looking at the diaphragm.

She sat with that for a while. It wasn't impossible — shortcut learning, a confounder in the training reports — but it was strange in a specific way. She wrote a loop that translated the diaphragm dome up and down in synthetic increments, two millimeters at a time, everything else frozen. The calcification score rose monotonically as the dome rose. High diaphragm, shallow breath-hold: the model called it calcium. Deep inspiration, dome pushed toward the abdomen: clean aorta, said the model, regardless of what was actually in the wall.

It was reading breath. Frail people can't take a deep breath before a scan; frail people have calcified aortas; the model had stitched the two together and thrown the aorta away. A tidy, publishable embarrassment. She almost stopped there.

She didn't, because of a discrepancy in her own logs. Weeks ago she had run the same head slice-by-slice — 3-millimeter axial sections, scored independently, then averaged — as a cheap saliency check. Those numbers sat in a forgotten CSV, and they disagreed with the volume scores. Not noisily. Systematically. Patients the whole-volume model called dirty, the slice-wise model called clean, and the disagreement itself lined up with something. Nobody scores single slices; the model was built for volumes. She pulled the CSV anyway.

At the scale of a whole chest, the score meant one thing. At the scale of a slice, it meant the opposite.

Here was where doubt set in properly, because sign flips are what artifacts look like. So she built the check she'd want a reviewer to demand. From the IDC buckets she pulled 1,912 NLST participants with baseline low-dose CT and seven-year vital status. Ground truth first: a dumb, honest Agatston-style threshold — voxels over 130 Hounsfield units inside a hand-tuned aortic mask — no model anywhere near it. Then three numbers per patient: the CT-CLIP volume score, the mean of its slice-wise scores, and diaphragm excursion proxied as apex-to-dome distance, which she could get in two lines of ITK.

Cox regression, adjusted for age, sex, pack-years, and the classical calcium score. The slice-wise mean behaved like calcification should: hazard ratio 1.58 per standard deviation, confidence interval well clear of one. The volume score, same patients, same covariates: hazard ratio 0.74. Protective. The model's flagship cardiovascular finding predicted survival when you fed it the whole thorax and death when you fed it slices — and the residual between the two scores, volume minus slice-mean, correlated with apex-to-dome distance at r = 0.81.

The picture that collapsed her doubt was almost insultingly simple: a scatter of the residual against excursion, 1,912 points lying along a line so straight it looked drawn. The volume head wasn't a broken calcium detector. It was two detectors fused. Per slice, it genuinely read plaque — bright flecks in the vessel wall, mortality and all. Across slices, it read how far a deep breath had dragged the aorta caudally, smearing those same flecks over more sections, and it had learned that people who could still smear their calcium across eleven slices instead of six were people who would be alive in seven years. Averaged over a volume, the breath signal drowned the plaque signal and flipped its sign. The effect had been sitting in every published validation of the model, invisible, because nobody scores slices.

She checked the second screening round, T1, a year later in the same patients. Participants whose excursion had shrunk between rounds — whose breath was leaving them — showed volume scores drifting down toward "clean" even as their thresholded calcium grew. The model wasn't measuring the aorta at all, not really. It was measuring how deeply the dying could still breathe, and it had been right about them all along.


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

