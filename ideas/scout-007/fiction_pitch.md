<!-- stage: fiction_extract -->
# Technical note

## Claimed finding

Analysis of the manual vessel-segmentation masks in the STARE retinal dataset shows that the binary masks encode a periodic modulation of arteriolar caliber with a wavelength of approximately 210 microns, present in 14 of the 20 masks and absent from the DRIVE and CHASE_DB1 masks. The modulation is attributed to Mönckeberg medial calcification of the arteriolar walls, faithfully traced by the human annotators from film fundus photographs; it is restricted to arterioles and spares venules, and its presence separates images carrying vascular-disease diagnosis codes from images coded normal with AUC 0.96 using the binary masks alone. The signal is claimed to survive in STARE because the film-based TopCon TRV-50 recorded it, whereas the modern digital cameras used for DRIVE and CHASE_DB1 suppress a ripple at this spatial frequency through in-firmware edge enhancement, noise suppression, and contrast normalization. The 210-micron banding is further claimed to indicate that the same calcification process is almost certainly running in the aorta, so that the dataset signature constitutes a cardiovascular measurement rather than an artifact.

## Materials

- STARE dataset: fundus photographs taken with a TopCon TRV-50 film camera at a San Diego VA hospital in the 1970s–80s, later digitized; 20 manual vessel-segmentation masks in two independently produced annotation sets (Hoover; Kouznetsova); accompanying per-image diagnosis codes (e.g., hypertensive retinopathy, arteriosclerosis, central vein occlusion, normal).
- DRIVE dataset: manual vessel masks from a modern digital fundus camera (Canon).
- CHASE_DB1 dataset: manual vessel masks from a modern digital fundus camera (Nidek); subjects are children.
- Hoover vessel-type labels distinguishing arterioles from venules in STARE.
- A classifier trained to predict source database (DRIVE vs. STARE vs. CHASE_DB1) from the binary masks alone; reported accuracy 99.2%.
- Saliency maps of the classifier's decisions per database.
- Vessel centerlines extracted from the manual masks, with width profiles: vessel caliber measured pixel by pixel along each vessel.
- Spectral (frequency) analysis of the width profiles, yielding a spectral peak at wavelength ~210 microns.
- Arteriole-to-venule spectral power ratio at 210 microns: 11.4× in every one of the 14 positive images.
- AUC of 0.96 for separating vascular-disease-coded images from normal-coded images using the mask-derived signal, computed three ways.

## Verification procedure

1. Train a classifier to predict the source database (DRIVE, STARE, or CHASE_DB1) from binary vessel masks only; observe 99.2% accuracy, exceeding what optics- or resolution-based leakage would explain.
2. Compute saliency maps for the classifier. For DRIVE and CHASE_DB1 the classifier attends to mask borders, vessel density, and wide pediatric arcades; for STARE it attends to the arterioles along their lengths.
3. Extract centerlines from the manual masks and compute width profiles (caliber pixel by pixel along each arteriole) for all three datasets. DRIVE and CHASE_DB1 profiles show smooth tapers and noise; 14 of 20 STARE masks show a clean spectral peak at ~210 microns wavelength.
4. To rule out an instrumental origin (film grain, flash ripple, digitization jitter), rerun the width-spectrum analysis on the same 20 STARE masks with arterioles and venules separated using the Hoover vessel-type labels — same film, same digitization, same annotators. The premise: an instrumental artifact would corrugate all vessels equally, whereas Mönckeberg calcification affects arteries and spares veins. Outcome taken as confirmation: spectral power at 210 microns is 11.4 times higher in arterioles than venules in all 14 positive images; venules show no peak.
5. Compare the per-image presence of the 210-micron peak against the STARE diagnosis codes. All 14 positive images carry vascular-disease codes (hypertensive retinopathy, arteriosclerosis, central vein occlusion); all 6 flat-profile images are coded normal. Compute the split three ways; AUC 0.96 in each. This concordance is taken as confirmation that the signal is a disease measurement rather than a scanner signature.
