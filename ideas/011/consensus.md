# Debate summary — idea 011

## Agreed

- The original mediation endpoint is non-identifying: correlation or attenuation among age, model prediction, and cartilage calcification cannot establish that cartilage influenced the model (Rounds 1–2; already established in the pre-debate critique).
- A localized dose ladder with within-mask shams is better than mediation for testing model sensitivity, and the Round-2 controls addressed the generic edit-footprint objection, but they did not isolate the originally claimed HU-thresholded volume (Rounds 2–4).
- The radiologist-legible X is **costal cartilage mineralization/calcification**, not “volume of voxels above 180 HU.” Thresholded volume, integrated burden, topology, component count, and attenuation are measurements of that phenomenon rather than interchangeable names for it (Rounds 3–4).
- The proposed removal arm is not causally matched by either sham. Arm R alone performs a mineralized-to-soft-cartilage transition; Arm S edits subthreshold cartilage, and Arm P removes and reinserts calcium at two footprints. Therefore the contrast may detect an operation-specific calcium-deletion signature rather than native use of costal cartilage mineralization (raised in Round 5, restated in Round 8, conceded in Round 12, accepted in Round 13).
- Cross-model replication cannot repair that unmatched intervention. A chronological-age-only model does address the separate concern that CT-CLIP's report supervision may inject age or cartilage semantics, but two models trained on the same image distribution can share sensitivity to the same deletion signature (Rounds 6–8).
- If the discovery framing were ever revived, it would require a report-supervision audit and a second model trained only from images and chronological age, with patient-level splits and no report-derived supervision (Rounds 6–8).
- TotalSegmentator class existence does not establish accurate cartilage localization. Edited-voxel precision—especially against rib, sternum, and vascular calcium in heavily mineralized older adults—is a hard prerequisite; reproducing an age slope or using a broad landmark box cannot validate it (Rounds 9–11).
- A small reference set is acceptable because annotation validates the instrument rather than entering the estimand. CCSeg may cheaply falsify the mask, but its pediatric weighting and limited normally aged, heavily mineralized cases mean it cannot certify performance in the target population; an older CT-RATE reference set would still be required (Rounds 9–10).
- The available design can support, at most, an intervention-scoped rung-1 statement about response to a mineralized-voxel removal operation. It cannot support the required sentence that either model natively uses costal cartilage mineralization or independently recovered the forensic clock (Rounds 11–13).
- The operator-sensitivity formulation should not become a separate candidate: its honest claim is about a synthetic operation rather than a named anatomical signal, and its novelty is weak relative to existing window-ablation work (Rounds 12–13).
- Idea 011 should be **paused**, not advanced under a narrower title and not rejected as scientifically incoherent. The question remains meaningful, but the available instrument and controls do not answer it (Rounds 12–14).
- This is not the prior annotation-provenance failure. No human judgment enters the estimand; the decisive failure is claim identifiability, with mask annotation serving only instrument validation (Round 12).

## Unresolved

There is no remaining disagreement between proposer and critic about the present disposition or the present design's claim ceiling. The following are unresolved empirical prerequisites for any future reopening:

### Can a measured, properly matched control separate mineralization use from the deletion signature?

- **Proposer's position:** The current synthetic shams cannot do so. A plausible repair would use the same acquisition's retained spectral/base-material or dual-kV data so that the de-mineralized appearance is measured rather than synthesized. A matched real-tissue control might also work, but the proposed tracheobronchial-cartilage and internal-thoracic-artery controls each introduce a different location or tissue confound (Rounds 12 and 14).
- **Critic's position:** Reopening requires a measured contrast matched after preprocessing on calcium-component loss, attenuation distribution, edge energy, topology, and location while leaving the claimed costal-cartilage quantity intact (Rounds 8, 11, and 13).
- **Evidence that would settle it:** Inspect and confirm a human chest CT corpus retaining spectral base-material or dual-kV raw data, with linkable per-scan age, then prospectively demonstrate that its measured contrast satisfies the matching criteria. No suitable public resource was found in the Round-14 collection-level search, but that search was not systematic and does not establish nonexistence.

### Could registered longitudinal CT provide a natural contrast?

- **Proposer's position:** This route is probably sensitivity-limited. Published cross-sectional gradients are only about 1.5–2.6% per year; RIDER is same-day and therefore contains no biological progression, while one-year NLST intervals may be smaller than reconstruction and repeat-scan variability (Round 14).
- **Critic's position:** A registered natural within-patient contrast would be acceptable if it supplied stable acquisition/registration and a detectable change in mineralization while controlling other anatomy (Rounds 5, 8, 11, and 13).
- **Evidence that would settle it:** First estimate the same-day repeat/reconstruction reproducibility floor of the post-preprocessing mineralization vector, for example with RIDER. The longitudinal route remains admissible only if that floor is small relative to the expected change over the available interval; otherwise it should be removed from the reopening condition.

### Is the editable cartilage mask sufficiently precise in the population where the experiment would run?

- **Proposer's position:** Recall variation mainly limits dose and generalizability, but precision of every edited voxel is identification-critical. CCSeg can be an initial falsification set, followed by a small blinded older-adult CT-RATE reference if it passes (Round 10).
- **Critic's position:** The exact post-preprocessing editable masks must meet prespecified precision and cross-stratum checks against an independent reference, with explicit cartilage-versus-rib/sternum/vascular-calcium confusion and editable true-positive fraction (Round 9). The critic accepted the narrower precision-centered gate conditional on older-adult validation (Round 11).
- **Evidence that would settle it:** Directly inspect the CCSeg release, evaluate the eroded editable set, and then test a prespecified age-by-sex-by-mineralization sample of older CT-RATE cases against a blinded reference. Failure of the edited-voxel precision gate stops the candidate.

### Are the other Stage-0 assets actually available and clean?

- **Proposer's position:** A released, linkable per-scan age field and a supervision audit of CT-RATE findings/impressions remain mandatory before model fitting (Rounds 7 and 10).
- **Critic's position:** These gates are necessary but cannot repair the central intervention-identifiability problem by themselves (Rounds 8 and 11).
- **Evidence that would settle it:** Inspect the actual metadata schema and one image–age join; inspect the training loader locally; quantify explicit age phrases and costal/chondral-cartilage mentions in the exact text used for CT-CLIP training under prespecified thresholds.

## Positions that moved

- **Proposer, Round 2:** Conceded that mediation and agreement across multiple edit families do not establish use, and dropped complementary retention and primary calcification addition, in response to the critic's generic edit/OOD objection from Round 1. This was earned by a specific identifiability argument.
- **Critic, Round 3:** Conceded that the Round-2 dose ladder, within-mask shams, artifact discriminator, and equivalence gate adequately answered the generic edit-footprint objection. The critic retained the narrower objection that the design did not isolate thresholded volume. This was earned by a materially new control design.
- **Proposer, Round 4:** Conceded that the design could not isolate HU>180 voxel count from calcium mass, attenuation, topology, components, and edges. X was narrowed from thresholded volume to costal cartilage mineralization. This was earned by the Round-3 within-family identifiability argument.
- **Proposer, Round 7:** Conceded that CT-CLIP does not satisfy the supervision-purity reading of “unguided” and added a report audit plus a chronological-age-only model. The proposer retained only the spatial meaning of no crop, mask, or regional supervision. This was earned by the Round-6 pretraining-channel objection.
- **Critic, Round 8:** Accepted that the two-model amendment substantively addressed the report-supervision objection, while preserving the earlier unmatched-sham objection. This was earned by the added disjoint-supervision model and audit.
- **Proposer, Round 10:** Conceded that MESA-slope recovery and the landmark box cannot validate cartilage segmentation; adopted edited-voxel precision gates and acknowledged the need for an older-adult reference. This was earned by the Round-9 wrong-keystone argument.
- **Critic, Round 11:** Accepted the revised anatomical-instrument plan conditional on the older-adult precision gate passing. The critic then returned to the still-open sham-identifiability ceiling. This was earned by the ordered precision-validation plan in Round 10.
- **Proposer, Round 12:** Conceded the decisive point: the available controls cannot distinguish native use of cartilage mineralization from sensitivity to the deletion operation. The proposer lowered identifiability to 2, the attainable rung to intervention-scoped 1, and recommended PAUSE. This was earned by the persistent argument from Rounds 5, 8, and 11; it was not an unearned capitulation.
- **Critic, Round 13:** Accepted the concession, the PAUSE disposition, and the decision not to create an operator-sensitivity spin-off. No new scientific disagreement remained.
- **Proposer, Round 14:** Converged on the same disposition after checking the proposed reopening routes and narrowing them. This was not an unearned concession: it supplied new feasibility evidence but did not change the already-settled substantive conclusion.

## Amendments made

At round zero, the card claimed that an “unguided” CT-CLIP age probe used **calcified costal cartilage volume above 180 HU**, based primarily on observational mediation against aortic calcification, vertebral density, emphysema, and heart volume. It placed the idea conditionally at rung 3, treated MESA-slope recovery and a landmark-box measurement as extractor validation, classified a negative as decisive, and proposed a frozen linear probe as the target model.

Across the debate, the proposed study changed as follows:

- Primary endpoint: observational mediation → localized dose-response intervention with removal, permutation, and subthreshold-sham arms.
- X: thresholded calcified volume → the broader, radiologist-legible phenomenon of costal cartilage mineralization, measured as a vector rather than one cutoff statistic.
- Comparator set: aorta, vertebrae, emphysema, and heart → only calcium-family intervention controls, chiefly aortic calcium; diffuse markers became descriptive.
- Target models: one report-supervised frozen CT-CLIP probe → CT-CLIP plus a second age regressor trained from scratch using chronological age alone, conditional on a supervision audit.
- Instrument validation: MESA-slope recovery and a landmark box → ordered kill gates culminating in edited-voxel precision against CCSeg and a small older-adult CT-RATE reference.
- Population and direction: all chest CT and a symmetric “uses” claim → older scans with measurable calcification and a one-sided removal operation.
- Claim ceiling: native use of a forensic cartilage clock at rung 3 → sensitivity to a particular mineralized-voxel deletion operation at conditional rung 1.
- Scores: Mode-C priority 3.90 → 3.15; identifiability 3 → 2; interest 4 → 3; feasibility remained capped and effectively worsened; keystone remained `NOT_INSPECTED`.

The final amendment was deliberately **not** made: the proposer declined to rename an operator-sensitivity study as though it still answered the native-feature-use question. Lost in the process were the original mediation claim, the threshold-volume specificity, two of three named comparators, supervision-purity framing, broad age-range applicability, a decisive negative, rung-3 status, and the claim that X was ready to compute without human validation.

## Recommendation

**PAUSE.** The debate converged after a real, persistent objection; this was not a one-round rubber stamp. Before deciding whether to reopen, the human should look first for the missing identification instrument: a confirmed human chest CT resource with retained spectral base-material or dual-kV raw data and linkable age that can provide a measured, post-preprocessing-matched mineralized-to-soft-tissue contrast. Without that—or another genuinely matched real-tissue control—the current experiment cannot distinguish native use of costal cartilage mineralization from response to the deletion operation, regardless of improvements to masks, models, or supervision audits.
