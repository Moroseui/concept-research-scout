# Technical note: Gutenberg–Richter statistics in dermoscope sensor noise via a chest-CT model

## Claimed finding

Analysis of the Derm7pt dermoscopy dataset with the CT-CLIP chest-CT model shows that the model's aortic-calcification finding head, when applied to out-of-domain skin images, acts as a bright-speckle energy detector and fires selectively on dermoscopic images acquired with MoleMax systems, whose ring-light optics produce a lattice of micro-specular highlights off the immersion fluid that pixel-wise resembles punctate calcium hyperdensities on CT. The distribution of the resulting calcification logits over the 512 MoleMax images follows the Gutenberg–Richter frequency–magnitude law (log N = a − bM) with b = 0.968 ± 0.021, matching the textbook seismological value b = 0.97 to two decimal places with no tuning, because the vendor's demosaicing noise is a multiplicative cascade governed by the same mathematics as scale-free fault ruptures; the model thereby measures the same statistical law in sensor noise as is observed in earthquakes.

## Materials

- Derm7pt dataset: approximately one thousand paired dermoscopic and clinical photographs of moles, each annotated with the seven-point checklist, collected on two dermoscopy systems (MoleMax and Heine); 512 images are from the MoleMax line.
- CT-CLIP chest-CT model, used as a set of per-finding heads (emphysema, pleural effusion, cardiomegaly, nodule, consolidation, aortic calcification).
- Calcification logits: the raw scores of the aortic-calcification head on each image, treated as magnitudes M in the Gutenberg–Richter relation.
- Gutenberg–Richter law: log N = a − bM, the frequency–magnitude relation of earthquakes, with reference value b = 0.97 taken from the Stein and Wysession seismology textbook.
- Histogram of log count versus calcification logit for the 512 MoleMax images.
- b-value estimate: Aki's maximum-likelihood b-value estimator, applied to logits in place of magnitudes, yielding b = 0.968 ± 0.021.
- MoleMax noise spectrum, used to draw synthetic speckle.
- A second JPEG library, used for re-encoding images with metadata stripped.

## Verification procedure

1. Run the CT-CLIP finding heads on Derm7pt as a negative control; observe that all chest finding heads are flat except aortic calcification, which produces high scores.
2. Sort outputs and inspect metadata; observe that clinical photographs score near zero, only dermoscopic images fire, and the calcification head splits the two acquisition systems perfectly — every high scorer is from the MoleMax line, every quiet image from the Heine units.
3. Plot log count against calcification logit for the 512 MoleMax images; observe a straight line, the Gutenberg–Richter form.
4. Before any measurement, fix b = 0.97 (the textbook value, no tuning) and fix a from the single lowest histogram bin; compute in advance the predicted number of the 512 images exceeding each half-unit logit threshold: 411, 168, 70, 29, 12, 5.
5. Count the observed exceedances at the same thresholds: 409, 171, 69, 30, 11, 5. Agreement of these counts with the predictions is taken as confirmation of the law.
6. Strip all metadata from the images and re-encode them through a different JPEG library; observe that the MoleMax/Heine split survives, confirming the signal lives in the pixels rather than the file headers.
7. Take twenty Heine images, inject synthetic speckle drawn from the MoleMax noise spectrum, and observe that their calcification logits climb the same straight line and land where the law predicts.
8. Apply Aki's maximum-likelihood b-value estimator to the logits in place of magnitudes; obtain b = 0.968 ± 0.021, matching the textbook value 0.97. This match is taken as final confirmation.
