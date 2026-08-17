# Critique — Idea 025: The scan is also an actigraph: the model may be reading how much the patient moved

```
FATAL OBJECTION: NONE — but three serious deflations stack: the audit subject
must be self-trained from a model class the challenge itself showed to be
non-competitive, the FD instrument as specified is contaminated by bolus
kinetics (a circularity risk for the L1 test), and the keystone is uninspected.
EVIDENCE: ideas/024/critique.md §1 (in-repo, verified 2026-08-17); the card's
own X_measurement definition; keystone_screen.md (UNVERIFIABLE).
REPAIRABLE WITHOUT CHANGING THE QUESTION? YES
DECISION: ADVANCE TO REVISION
```

---

## 0. What was verified for this critique

Web verification run this session (2026-08-17). Tags: **[fetched]** = full
text/structured record retrieved and checked; **[snippet]** = search-result
level; **[in-repo]** = verified by a prior stage in this repository with
primary sources, reused with citation. Per collaborator rules, absence claims
are bounded-search absences.

One finding is *favorable* and materially updates the card — see §2.

## 1. The subject-model problem: idea 024's objection A applies here, attenuated but real

The card's decisive arm runs "forward passes through the shared baseline"
and budgets the checkpoint as "counted once for the whole cycle." Both
premises are now false:

- **The cycle-shared baseline has no other surviving shareholder.** Idea 024
  (isles24-scout-001-c06) was REJECTED on 2026-08-17; baseline candidate c04
  of this cycle was never registered. Idea 025 bears the full A100 training
  cost alone.
- **No trained raw-CTP ISLES'24 model is publicly obtainable.** Verified for
  the 024 critique **[in-repo, primary sources fetched there]**: of twelve
  finalists, the three raw-4D-CTP teams (Ninjas, HSK-CoreFinders,
  MIPLAB-PrediCTP) released no weights; the only downloadable checkpoints
  (Kurtlab rank 1, AMC-Axolotls rank 2) consume derived maps + CTA + NCCT,
  not the raw series.
- **The raw-CTP model class is non-competitive on this data.** The challenge
  paper states map-based models "consistently outperform those trained
  directly on raw 4D CTP series" **[in-repo, fetched arXiv 2408.10966]**;
  the one published raw-CTP ISLES'24 result is Dice ~0.20 vs ~0.285 for the
  map-based winner.

Why this is not the same kill as 024, stated explicitly since the ledger
requires it: 024's question needed a *performant* model, because its X was a
second moment of the deconvolved residue function — a subtle temporal
property a Dice-0.20 model cannot credibly be probed for, making any null
uninterpretable. 025's question is a **class-level susceptibility question**
in the DeGrave genre (DeGrave et al. trained their own models on public data
precisely to demonstrate shortcut absorption as a class phenomenon — DOI
10.1038/s42256-021-00338-7), its X is a gross image property rather than a
second moment, and the card already contains the gate 024 lacked: a
**hemodynamic positive-control edit**. If the self-trained model responds to
the positive control but not to injected motion, the null is interpretable —
it is motion-specific robustness *of that model*, not "this model uses
nothing."

But the deflation is still real, in three places the card's scores do not
reflect:

1. **negative_result_value 4 → 2–3.** "A deployable robustness statement the
   challenge never tested" overstates it: the null certifies one self-trained,
   reduced-epoch model of a class nobody deploys and the challenge showed to
   be inferior. That is interpretable (positive control passing) but low-value.
2. **medical_relevance 4 → 3.** The named harm (ventilated patients
   under-scored) presupposes deployed models ingesting raw CTP. Deployed
   products (RAPID, icobrain) are deconvolution pipelines; the demonstrated
   harm pathway would be prospective ("if the field moves to end-to-end raw
   CTP, this cue is waiting"), which is a legitimate but weaker claim.
3. **Compute honesty.** The card's "~8–12 h reduced-epoch nnU-Net, counted
   once" is now this idea's own cost, and the 024 critique judged full 4D
   training to strain the single-session envelope. A reduced-epoch single-fold
   run fits but yields an even weaker subject, compounding point 1.

## 2. Favorable finding: the contested L1 link is now retrieved, and it supports the card

The card listed the 2021 Eur J Radiol follow-up as "paywalled today,
direction unretrieved." Retrieved this session via the Europe PMC REST
record **[fetched]**: *"Head movement during cerebral CT perfusion imaging
of acute ischaemic stroke: Characterisation and correlation with patient
baseline features"*, Eur J Radiol 2021, PMID 34678666, DOI
10.1016/j.ejrad.2021.109979. Findings: 58% negligible motion, 24%
mild-to-moderate, 19% considerable-to-extreme; **higher NIHSS, older age,
and shorter onset-to-scan time each predicted more head movement (p<0.05),
and NIHSS + age jointly were "highly predictive of head motion"
(p<0.001)**.

This does three things:

- It resolves the Fahmi-vs-followup tension the card honestly flagged, in
  the card's favor: the severity→motion link (L1) has direct published
  support in exactly this imaging context, at acquisition time.
- It upgrades the scientific premise from speculation to source-supported:
  a severity-correlated acquisition cue **existed in the raw acquisitions**
  of stroke CTP cohorts. The open question is precisely the keystone —
  whether it survives the organizers' correction into the released series.
- It sharpens what Stage 0 must preregister: the L1 test now has a
  literature-derived sign prediction (positive FD–NIHSS correlation), so a
  contrary or null in-dataset result is informative rather than ambiguous.

Also verified **[snippet]**: Fahmi 2013 (PMID 24041432), 103 patients, 24%
moderate/severe motion — consistent with the card — but the retrieved
amplitude figures (mean Tz 22.6 mm, max 69.3 mm) do not match the card's
"translations up to ~9–23 mm." Not decision-relevant; pin the numbers from
the full text at revision.

And **[snippet, ResearchGate/PubMed summary]**: PMID 34301804 is a
**phantom-simulation** study — artificial motion added to a CT
brain-perfusion phantom, evaluated with RAPID: core smaller by −5.3 mL
(subtle) to −7.0 mL (strong motion), penumbra larger by +9.9/+35 mL. The
direction claim in the card is confirmed, with two caveats for the design:
(a) it is one software package on a phantom, not a law — the "opposite-sign
identification" argument should be demoted from *identifying* to
*suggestive*, because nothing forces a learned model's
corrupted-hemodynamics response to mirror RAPID's bias direction; (b) it
concerns uncorrected motion, whereas 025 probes post-correction residue.
The sham family, not the sign, must carry identification.

## 3. The instrument objection: FD on contrast-varying frames measures hemodynamics unless built not to

This is the most important repair. The card's X-measurement has two
components, and both are contaminated as specified:

1. **Rigid re-registration FD.** CTP frames change intensity massively as
   the bolus transits. Intensity-driven rigid registration of
   contrast-varying frames picks up apparent displacement from contrast
   arrival, not only from the head moving. Crucially, the contamination is
   **not random**: severe strokes have delayed, dispersed kinetics, so
   registration error correlates with severity by construction.
2. **"Temporal-inconsistency energy" (median absolute frame-to-frame
   difference in registered space).** During bolus passage, frame-to-frame
   intensity difference *is* the perfusion signal. This component is close
   to a direct hemodynamics readout.

Consequence: the L1 test (FD vs NIHSS) could return the predicted positive
correlation with **zero patient motion**, because both index components
respond to severity through kinetics. That would be concept-label
circularity — the motion index re-encoding the hemodynamic severity it is
supposed to be independent of — and it would also poison the injection arm,
since "natural amplitude" calibration percentiles would be drawn from a
contaminated distribution.

Repairable without changing the question, and cheaply:

- Anchor the registration to **bone** (skull is contrast-invariant;
  bone-thresholded rigid registration is standard), or restrict FD to
  pre-contrast and post-washout frames.
- Compute the inconsistency-energy component on bone/head-boundary voxels
  or on baseline+tail frames only.
- Add a mandatory **null-instrument check**: on series verified motion-free
  (or synthetic no-motion series with varied kinetics), the index must read
  ≈ 0 across the range of hemodynamic severity; and a **recovery check**:
  known injected rigid motion must be recovered quantitatively. Both are
  annotator-free and computable today, satisfying the charter's hard
  constraint on X.

The 2021 EJR paper quantified motion on these same acquisitions, so a
published methodology exists to align with; pin their method at revision.

## 4. Keystone and injection realism: honest in the card, still the load-bearing risks

The keystone screen returned UNVERIFIABLE, correctly: the released series
are already co-registered and 1-Hz-resampled by the organizers (fetched
quote, DOI 10.1148/ryai.250603), and nobody has opened a frame. Two
compounding facts sharpen it:

- **The correction pipeline is closed.** The preprocessing sentence
  attributes the pipeline to icobrain cva (FDA-cleared, icometrix). Injected
  motion therefore cannot be passed through the *same* correction the
  natural residue survived; the card's "re-run a standard motion-correction
  step" is a different pipeline by necessity. The card's discriminator gate
  is the honest bound — but note it is a late gate: it is evaluated after
  the 99-GB download, the census, and model training. If injected-and-
  recorrected residue is texturally separable from natural residue, the
  decisive arm dies after most of the spend.
- **Real residue is not rigid displacement.** Motion during acquisition
  causes intra-rotation inconsistency and interpolation artifacts that 1-Hz
  resampling then smears; post-correction residue is largely this texture,
  not inter-frame rigid offsets. Injecting rigid per-frame displacement
  into already-resampled frames and re-correcting approximates only part of
  it. This is the idea-006 OOD lesson in miniature; the card discloses it,
  but the revision should re-order the gates so the discriminator is tested
  on a pilot (a handful of cases) *before* the model is trained.

The residual-assumption check in the keystone screen was done properly this
time — it identified the deeper assumption (post-correction FD is a valid
trace of original movement) rather than the nearest checkable thing. §3's
instrument repairs are exactly what would make that assumption testable.
No wrong-keystone error to record.

## 5. Leakage check: NIHSS is an input elsewhere in this challenge

The released clinical CSV contains admission NIHSS, and ISLES'24 pipelines
may consume clinical data. Two consequences: (a) the self-trained baseline
for this study must be **raw-imaging-only** — if NIHSS is an input, the
model has the severity variable explicitly and the incentive to learn a
noisy motion proxy collapses, biasing the study toward a null; (b) the
card's "derived-map channels held fixed" phrasing implies a multi-channel
model — feeding perturbed raw CTP alongside pristine derived maps is itself
a channel-consistency OOD condition. Cleanest repair, matching the question
as written ("a raw-CTP model"): train the subject on raw CTP only. State
this in the revised card.

## 6. Novelty: holds, and is slightly strengthened

Bounded searches this session found no audit of any learned stroke/CTP
model for motion sensitivity or motion-as-feature: robustness work in CTP
deep learning concerns deconvolution-replacement and map generation
**[snippet sweep]**; motion appears exclusively as a nuisance to correct.
The nearest neighboring literature is fMRI QC, where head motion is an
established *phenotype* (impulsivity and ADHD correlate with in-scanner
motion — e.g., PLOS One 10.1371/journal.pone.0104989 **[snippet]**), which
is precedent for the mechanism, not overlap with the claim. The card's
novelty_delta stands; with PMID 34678666 retrieved, the delta is now
sharper: the severity→motion link is published, the correction step is
published, and nobody has asked whether the corrected release still carries
the link into a trained model.

## 7. Score corrections (for the record)

- `negative_result_value` 4 → 2–3: the null certifies a self-trained,
  reduced-epoch, raw-only model; interpretable via the positive control,
  but not a "deployable robustness statement."
- `medical_relevance` 4 → 3: harm pathway is prospective, not deployed.
- `identifiability` 4 → 3 until the instrument repairs land: as specified,
  the index is severity-contaminated (§3) and the sign argument (§2) is
  suggestive, not identifying. The sham family is adequate if the
  null-instrument and recovery checks pass.
- `prior_legwork` 4 → 3: the "cycle-shared checkpoint" asset no longer
  exists; L1 legwork improved (retrieved, favorable) but the subject model
  is now wholly this idea's cost.
- `feasibility` stays 3 (capped, keystone NOT_INSPECTED) — the cap is doing
  the right work here.
- `dies_like_prior` update required: the card names idea-006 and 009/016;
  it must now also answer idea-024 (DATA_ACCESS, same dataset, same missing
  subject) with the §1 argument.

## 8. Easier-version search

1. **The Stage-0 census alone is the low-hanging fruit, and it is genuinely
   worth doing.** Data public (99 GB, CC BY-NC-SA), no GPU, no model, no
   annotator: a bolus-robust FD census over 149 released corrected series
   plus the preregistered FD–NIHSS test. It is simultaneously (a) the
   keystone inspection, (b) the first characterization of residual motion
   in a public stroke-challenge release, (c) a severity-correlation result
   with a published sign prediction to confirm or refute in-dataset, and
   (d) a per-case motion covariate that ideas 021/023 (shortlisted, same
   dataset, released-weights subjects) can use to flag motion-contaminated
   cases. Even if the injection arm never runs, this is a chartered success
   ("a feasibility result that prevents wasted effort").
2. **Observational adjunct with released weights, no training:** correlate
   the rank-1 map-based winner's per-case error with the motion index
   (motion propagates into icobrain-derived maps, per the PMID 34301804
   mechanism). Association-only — no use claim, rung 0–1 at best,
   exploratory label mandatory — but free once the census exists. Not a
   separate candidate; a paragraph in this one.
3. **Skip the injection arm entirely, publish census + associations?**
   Rejected as the *terminal* form: without the injection arm there is no
   model-use claim and the idea leaves this program's deliverable. The arm
   should stay, gated as below.

## 9. Revision requirements (proposed, for the driver)

1. Rebuild the card as a **gated two-stage design**. Stage 0 (CPU-only,
   census + L1) is the primary deliverable-bearing step and doubles as the
   keystone inspection; its instrument must be bolus-robust (bone-anchored
   registration; inconsistency energy off-bolus or on bone), with the
   null-instrument and motion-recovery checks preregistered (§3).
2. The injection arm runs only if: census shows patient-gradeable dynamic
   range; the discriminator pilot (few cases, before any training) fails to
   separate injected-recorrected from natural high-motion residue; and the
   subject-model gate passes (raw-imaging-only baseline, preregistered
   performance floor in the published raw-CTP range, hemodynamic positive
   control responsive).
3. Rescore per §7; update `dies_like_prior` for idea-024; pin Fahmi
   amplitude numbers and the 2021 EJR methodology from full texts; demote
   the opposite-sign argument to suggestive; delete the "cycle-shared"
   compute framing.

Deliverable sentence unchanged; gates and honesty changed. Under the
2026-08-10 claim-identity rule this is revision-in-place, not supersession.

---

```
NEAREST DEFENSIBLE HIGH-VALUE QUESTION: Does the released, already-corrected
ISLES'24 CTP still carry a bolus-independent, severity-correlated patient-
motion signature (census + preregistered FD–NIHSS test), as the gate to the
injection arm on a raw-only self-trained baseline?
RETAINS ORIGINAL MEDICAL MOTIVATION? YES — motion-as-severity-cue is the
same question; only the order of proof and the honesty of the scores change.
SHOULD IT BECOME A SEPARATE CANDIDATE? NO — it is the same deliverable
sentence with gates re-ordered; revision-in-place applies.
IS IT ACTUALLY WORTH DOING? The Stage-0 census is worth doing on its own
merits (keystone inspection + first residual-motion characterization of a
public stroke release + a covariate ideas 021/023 can reuse); the injection
arm is worth doing only if its three gates pass, and the revised card should
say exactly that.
```

## Sources consulted this session

- [PMID 34678666 via Europe PMC REST](https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID:34678666&resultType=core&format=json) — Eur J Radiol 2021, DOI 10.1016/j.ejrad.2021.109979 [fetched]
- [Fahmi 2013, PMID 24041432](https://pubmed.ncbi.nlm.nih.gov/24041432/) — 103 patients, 24% moderate/severe motion [snippet]
- [PMID 34301804](https://pubmed.ncbi.nlm.nih.gov/34301804/) — RAPID phantom study, core −5.3/−7.0 mL, penumbra +9.9/+35 mL under simulated motion [snippet]
- [ISLES'24 challenge paper, arXiv 2408.10966](https://arxiv.org/abs/2408.10966) — map-based > raw-CTP [in-repo, fetched for 024 critique]
- [Kurtlab preprocessing paper, arXiv 2505.18424](https://arxiv.org/html/2505.18424v1) — rank-1 pipeline consumes derived maps [in-repo]
- [Impulsivity predicts head motion, PLOS One](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0104989) — fMRI motion-as-phenotype precedent [snippet]
- ideas/024/critique.md — raw-CTP weights absence, performance record [in-repo, 2026-08-17]
