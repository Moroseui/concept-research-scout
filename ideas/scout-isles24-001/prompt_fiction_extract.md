You are a writer working inside this repository.
Repository root: /home/runner/work/concept-research-scout/concept-research-scout
Assigned output directory: ideas/scout-isles24-001
Write only the file the task names. Preserve all other files.

===== ideas/scout-isles24-001/fiction_story.md =====
# b = 0.97

The control experiment was supposed to be boring. That was its whole job.

Ines Valdaro had spent the summer building negative controls for CT-CLIP, and the cleanest one she could think of was skin. Feed the chest-CT model something that was not a chest — the Derm7pt set, a thousand-odd paired dermoscopic and clinical photographs of moles, each annotated with the seven-point checklist — and every finding head should flatline. Emphysema: flat. Pleural effusion: flat. Cardiomegaly, nodule, consolidation: flat, flat, flat.

Aortic calcification: a forest of spikes.

She laughed at first. Then she sorted the outputs and stopped laughing, because the spikes were not noise. The clinical photographs — ordinary camera shots of the same lesions — scored near zero. Only the dermoscopic images fired, and among those, only some. She pulled the metadata. Derm7pt had been collected on two dermoscopy systems over the years, and the calcification head had split them perfectly: every high scorer came from the older MoleMax line, every quiet image from the Heine units. A chest-CT model, shown skin, was reading off the manufacturer of the dermoscope.

The mechanism took her a week to see. The MoleMax ring-light threw a lattice of micro-specular highlights off the immersion fluid — tiny bright flecks scattered across a smooth dark field. Which is, pixel for pixel, what calcium looks like on a CT slice of the aortic wall: punctate hyperdensities on homogeneous soft tissue. The head was not a calcification detector. It was a bright-speckle energy detector, and one vendor's optics manufactured speckle.

That much she could defend at lab meeting. What she could not defend was the histogram.

She had plotted the calcification logits for the 512 MoleMax images, log count against score, expecting the usual lumpy mess. Instead she got a dead-straight line falling off to the right. She had seen that exact plot before — not in radiology, not in dermatology, but in an undergraduate elective, eleven years earlier, in a seismology lecture. Gutenberg–Richter. The frequency–magnitude law of earthquakes: log N = a − bM, with b hovering near one for the whole planet, from Parkfield to Tōhoku.

Her advisor's voice in her head: *you fit a line to a histogram and hallucinated tectonics.* Fine. She would let the law make a prediction before she made a measurement.

She wrote it on paper first, no screen. If the vendor's demosaicing noise was a multiplicative cascade — flecks of flecks, the same mathematics that makes fault ruptures scale-free — then the speckle energies were earthquakes, the logit was a magnitude, and the counts had to obey b = 0.97, the value straight out of Stein and Wysession's textbook, no tuning allowed. She fixed *a* from the single lowest bin, then computed, in advance, how many of the 512 images should exceed each half-unit threshold: 411, 168, 70, 29, 12, 5.

Then she ran the count. Observed: 409, 171, 69, 30, 11, 5.

Her hands went cold. She tried to break it. She stripped every byte of metadata and re-encoded the images through a different JPEG library: the split survived, so it was living in the pixels, not the headers. She took twenty Heine images, injected synthetic speckle drawn from the MoleMax noise spectrum, and watched their calcification logits climb the same straight line, landing where the law said they would. Last, the estimator seismologists actually use — Aki's maximum-likelihood b-value, one line of algebra, no binning to fudge — applied to logits instead of magnitudes: b = 0.968 ± 0.021. The textbook said 0.97. A dermoscope company's sensor noise, filtered through a chest-CT model's misfiring head, was reproducing the frequency–magnitude statistics of the San Andreas fault to two decimal places, because both were the roar of a multiplicative cascade, and CT-CLIP had accidentally been trained into a perfect instrument for hearing it.

She sat back and looked at the two rows of numbers, predicted and observed, until the lab lights clicked onto their night cycle. Tomorrow there would be lab meeting, and the slide she would have to make, and the sentence she did not yet know how to say out loud: the model has never seen an earthquake, and it has never seen skin, and it just measured the same law in both.

She printed the histogram anyway, and taped it above her desk, next to nothing.


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

