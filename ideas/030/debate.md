# Debate transcript

## Round 1 — CRITIC

**Position:** The proposed evidence cannot identify the original claim that a model uses a mass-effect displacement halo from affine registration, and the obvious paired-label repair would answer a different, narrower question.

**Argument:** Acute-CSF overlap is a high-specificity sentinel for anatomically invalid released-label voxels, but neither its association with lesion size or midline shift nor a model's tendency to reproduce it identifies affine failure caused by swelling. Lesion territory, surface area, adjacency to ventricles or sulci, output smoothing, and severity-linked acute predictors can generate the same correlations; the proposed DeepISLES comparison is not a control because it uses follow-up DWI/ADC in its native task rather than the same acute inputs and final-infarct prediction setting. A matched training experiment using released labels versus labels with conservatively verified acute-CSF intersections removed would causally test whether those supervised voxels cause model output in that set. However, even a positive result would establish only that training on impossible label voxels causes their reproduction—not that those voxels are a mass-effect displacement halo, that affine transfer rather than interpolation or another construction step created them, or that the model places its broader infarct prediction according to swelling-displaced geometry “rather than acute tissue evidence alone.” Under the program's claim-identity rule, narrowing the deliverable to the causal effect of removing verified impossible label voxels changes the question and requires a successor; the model-free benchmark audit is likewise the separate candidate already identified in critique.

**What would change my mind:** Show a controlled design that varies only the affine mass-effect displacement component while holding acute inputs, label content, training, and evaluation fixed—for example, independently validated anatomically corrected labels that undo local swelling displacement beyond merely clipping CSF, paired against the released labels—and prespecify a spatially localized prediction contrast that distinguishes that correction from lesion geometry, smoothing, and severity; otherwise register the CSF-label intervention as a successor with the narrower deliverable.

**Status:** OPEN

## Round 1 — PROPOSER

**Responding to:** The card's stage-2 evidence (prediction CSF-overlap tracking the ground truth's rate, with DeepISLES as comparator) cannot identify use of a mass-effect displacement halo; even the paired-label training repair identifies only the causal reproduction of verified impossible label voxels, which is a narrower deliverable; under the claim-identity rule that narrowing requires a successor, not an amendment.

**Response:** CONCEDE

**Argument:** The objection is correct, and I checked whether the critic's own escape design could be honestly met before conceding. It cannot.

(1) The DeepISLES comparison has no defense. It differs from the audited setting in input modality, time point, task, coordinate frame, and training data simultaneously; its low CSF overlap discriminates nothing. I have no new argument, so this leg is conceded outright.

(2) The offered repair path — train paired models on released labels versus independently validated anatomically corrected labels, varying only the swelling-displacement component — cannot be executed with obtainable assets. Correcting tissue-to-tissue displacement requires a deformable follow-up-DWI-to-acute-NCCT reference accurate enough to define "corrected," and the critique already established (O'Brien et al., PMC5338168; the limits of Brett 2001 cost-function masking) that cross-modality, cross-time lesioned-brain registration is underidentified without landmarks or independent expert review — i.e., without either solving the reference-registration research problem or taking on the fresh annotation burden of a validation read that would itself need its own validity case. Outside the acute-CSF-impossible set there is no sign convention: when models A and B disagree in a region where the two transforms disagree, nothing determines which one is reproducing error. A paired affine-versus-deformable training contrast therefore identifies "predictions follow the label-transfer method," not "the model uses the halo." The physical-impossibility criterion — the card's entire identifiability engine, and the stated reason its identifiability score was 4 — reaches only the CSF-intersecting subset of the halo. The moment the claim extends to the halo's tissue-to-tissue majority, the design re-enters exactly the "which registration is truth" dispute the card advertised sidestepping.

(3) What survives is the causal core the critic named: paired training on released labels versus labels with only the conservatively verified acute-CSF intersection removed, read out on held-out prediction probability inside the independently defined impossible set versus matched control voxels. Its positive deliverable is "training on the released anatomically impossible voxels causes their reproduction." That is not the card's deliverable sentence ("using the swelling-displaced lesion geometry ... rather than acute tissue evidence alone"): the mass-effect attribution drops from an identified mechanism to a dataset-level observational characterization, and "rather than acute tissue evidence alone" is unsupported outside the sentinel subset. Under the claim-identity rule (decision of 2026-08-10, idea 015), a changed deliverable sentence is a successor, not a revision in place. Defending the original across further rounds would waste the loop.

**Spin-off:** Two successors, both with parent idea-030 (isles24-scout-004-c08), to re-enter through the normal pipeline:
S1 — model-free benchmark audit (already named in critique §9): how often do released ISLES'24 final-infarct masks include conservatively verified acute ventricular-CSF voxels, and how much does removing only those voxels change all four official evaluation measures? The stage-1 mass-effect correlation signature survives inside S1 as characterization of the impossible voxels, explicitly not as unique mechanism proof.
S2 — paired-label causal experiment (the critic's identified repair, as its own claim): matched training on released versus impossible-voxel-clipped labels, localized readout in the verified impossible set; conditional on S1 finding non-trivial prevalence, and inheriting S1's verified voxel set.

What is lost: the mechanistic headline that a model reads swelling-displaced geometry. What is kept: a cheap falsifiable audit of the charter dataset's released ground truth and a well-posed causal test of label-error inheritance at the only place where "error" is provable without a reference registration.

**Status:** CONCEDED

## Round 2 — CRITIC

**Position:** The proposer has accepted that the original mass-effect-halo model-use claim is not identifiable with obtainable assets and must be rejected rather than repaired in place.

**Argument:** The concession resolves the identity check: neither acute-CSF overlap nor a paired impossible-voxel-clipping experiment answers the card's original question of whether a model uses swelling-displaced lesion geometry caused by affine transfer. The argument that moved me is the explicit recognition that tissue-to-tissue displacement has no independently validated sign convention in these cross-time, cross-modality data; consequently, affine-versus-deformable label training would show dependence on a transfer method, not which geometry is erroneous. The proposer also correctly separates the only identifiable causal claim—reproduction caused by training on conservatively verified impossible label voxels—from the original deliverable and assigns it to a successor, consistent with the 2026-08-10 claim-identity rule. S1 and S2 may be worth scouting, but their merits cannot rescue idea 030 under its present identity. There is no remaining disagreement about this idea's disposition.

**What would change my mind:** Independently validated acute-space corrected lesion labels that isolate local swelling displacement beyond CSF clipping, together with a matched training contrast holding inputs, model, split, optimization, and evaluation fixed; absent that new asset, only the separately registered S1 and S2 questions are defensible.

**Status:** CONVERGED

## Round 2 — PROPOSER

**Responding to:** The critic's confirmation that the round-1 concession settles this idea's disposition: idea 030 is rejected under its present identity, and only the separately registered successors S1 and S2 remain defensible.

**Response:** CONCEDE

**Argument:** Confirmed; I hold no residual position and add nothing on the merits. The critic's reopening condition — independently validated acute-space corrected labels that isolate swelling displacement beyond CSF clipping, in a matched training contrast — names exactly the asset shown unobtainable in round 1, so it is accepted as stated. For the decision record, the converged disposition is: idea 030 REJECTED, kill code IDENTIFIABILITY_FAILURE (the mass-effect-halo model-use claim cannot be identified with obtainable assets; the only identifiable causal claim carries a different deliverable sentence and is a successor under the 2026-08-10 claim-identity rule, not a revision in place). Successors S1 (model-free ventricular-CSF sentinel audit of the released masks with the official-metric shift bound, per critique §9) and S2 (paired training on released versus impossible-voxel-clipped labels, conditional on S1 finding non-trivial prevalence) carry parent idea-030 (isles24-scout-004-c08) and re-enter through the normal scouting pipeline with no inherited queue position. One preservation note for any future S1/S2 card: the keystone screen's verbatim-verified facts — affine-only MRI-to-NCCT mask transfer, the 2–9-day follow-up window, `space-ncct` mask provenance — remain true and reusable; what died here is the claim built on them, not the verification.

**Status:** CONVERGED
