# Keystone screen — idea 033 (isles24-scout-003-c01)

**Card:** "Did preprocessing teach the winner to read the disappearing insular ribbon?"
**Screen date:** 2026-08-18

## Keystone as stated

> "A frozen ISLES'24 model that actually consumes quantitative NCCT achieves
> non-trivial held-out performance and exposes a representation in which
> gray-white contrast can be erased without destroying perfusion severity or
> anatomy."

This is a composite. Decomposed:

- (K-a) ISLES'24 releases NCCT per case, in quantitative HU, co-registered
  with the perfusion maps — the substrate for both the twin-model training
  and the mirrored HU-contrast measurement. **Checkable now.**
- (K-b) A frozen model consuming NCCT exists or can be produced with
  non-trivial held-out performance. **Partially checkable** (does a public
  checkpoint exist? did any published model demonstrably use NCCT?).
- (K-c) The representation admits selective erasure of gray-white contrast
  preserving perfusion/anatomy decodability. **Empirical by construction** —
  a Stage-0 outcome, not a source-verifiable fact. The card correctly flags
  this in `keystone_residual_assumption` and `unverified_claims`.

## What I inspected

### 1. Dataset composition, split, preprocessing (K-a)

Source: ISLES'24 challenge paper, arXiv:2408.10966 (fetched
https://arxiv.org/html/2408.10966, 2026-08-18).

> "The dataset (N = 248) is split into train (N = 150) and test subsets
> (N = 98). The train subset is publicly available, while the test subset is
> hidden from the public."

> "Acute imaging data... include the diagnostic CT trilogy: NCCT, CTA, and
> CTP, as well as CTP-derived perfusion maps (namely CBF, cerebral blood
> volume (CBV), mean transit time (MTT), and time-to-maximum of the residue
> function (Tmax))."

> "Preprocessing of the images has been performed by linearly interpolating
> and registering all the imaging series to the NCCT scans... MRI scans are
> skull-stripped using HD-BET. The 4D CTP series are motion-corrected through
> image co-registration and temporally resampled at 1 frame/second."

> "Lesion masks are derived from the follow-up MRI using DeepISLES. Quality
> control and correction of the lesion masks are performed when needed by
> medical students supervised by two neuroradiologists with more than 10
> years of experience."

Reading: released series are registered **to NCCT space** (so the
NCCT-vs-perfusion-map spatial correspondence the card's erasure controls need
is built in); the stated operations (linear interpolation, registration,
motion correction, temporal resampling) are intensity-scale-preserving; **no
intensity normalization of CT is stated**. Skull-stripping is stated for MRI
only, not CT.

Corroboration that released CT is in HU: the winning method (arXiv:2505.18424,
fetched https://arxiv.org/html/2505.18424v1) applied its own HU windowing —

> "intensity windowing was applied using the ranges in Figure 1, informed by
> clinical literature and manually refined through empirical tuning"

— clinically-informed window ranges are only meaningful on a Hounsfield scale,
so the inputs the winner received (the released challenge data) carried
quantitative HU. Supporting deltas from the same paper: baseline
"Z-score normalization and [1,99] percentile windowing achieved a Dice score
of 21.8%"; "custom windowing alone improved performance to 31.0%".

### 2. Frozen model availability and NCCT consumption (K-b)

- The winning paper (arXiv:2505.18424) was checked twice in full-text HTML
  for an availability statement: **"No statement provided. The paper
  includes no mention of code availability, GitHub repository, or model
  release."** A web search for released ISLES'24 final-infarct checkpoints
  found none. Per program rules, not finding it is not proof it does not
  exist — but the card cannot rely on a public frozen checkpoint.
  Consequence: the card's `smallest_decisive_experiment` (train an
  NCCT+perfusion twin and a perfusion-only twin from scratch) is the **only**
  live path to K-b, not a fallback. That path is consistent with the card as
  written.
- The winner's paper does **not** enumerate which channels feed the nnU-Net;
  the only channel-adjacent quote is about skull-stripping: "we applied
  SynthStrip on the non-contrast CT (NCCT) scans to obtain a brain masks.
  Then, we applied this brain mask to the other co-registered scans (CTP,
  CTA, etc.)". No published NCCT-contribution ablation exists in that paper
  (ablations compare normalization schemes, not modality subsets). So
  "the winner used NCCT as a cue source" is **motivation, not established
  fact** — exactly as the card's `keystone_residual_assumption` already
  states.

### 3. Discrepancy noted (non-fatal)

The card says "public NCCT and registered perfusion maps for 149 cases"; the
challenge paper says the train subset is N = 150. (The dataset paper abstract,
arXiv:2408.11142, says "This multicenter dataset consists of 245 cases" vs
248 in 2408.10966 — the primary sources disagree with each other at the
±3-case level across versions.) One-case-level bookkeeping; does not affect
the keystone. The exact usable-case count should be pinned at Stage 0 from
the actual download.

## Residual-assumption check (mandatory follow-up)

If this screen only verified the nearest checkable thing (K-a), the card is
still assuming: (i) NCCT contributes incremental performance in the
reproduced model over its perfusion-only twin; (ii) a gray-white-contrast
direction is learnable and selectively erasable with perfusion severity and
anatomy decodability preserved. Neither is verifiable from any primary source
today; both are the card's own declared Stage-0 gates and its first two
`unverified_claims`. This card has **not** committed the wrong-keystone
error — it names the residue explicitly. This screen verifies the substrate
those gates run on, and that substrate is confirmed.

**Scope limit:** this PASS covers the data substrate (K-a) and the
no-public-checkpoint fact (K-b, availability half). It does **not** set
`keystone_status` to INSPECTED_TRUE for the model/erasure half (K-b
performance, K-c); the rubric's hard caps on feasibility and
novelty_confidence remain in force until Stage 0 inspects the trained model.

Quotes above were obtained via rendered-page fetches of the arXiv HTML full
texts on 2026-08-18; they are transcriptions from those fetches, not
hand-verified against the PDF typography.

```json
{"verdict": "PASS", "evidence": "Preprocessing of the images has been performed by linearly interpolating and registering all the imaging series to the NCCT scans... The 4D CTP series are motion-corrected through image co-registration and temporally resampled at 1 frame/second.", "source": "arXiv:2408.10966 (https://arxiv.org/html/2408.10966), data/preprocessing section; modalities and N=150 public train split quoted from the same source", "note": "Substrate verified: NCCT+CTA+CTP+maps released co-registered in NCCT space with HU-preserving ops and no stated CT intensity normalization; no public winner checkpoint exists, so the card's train-your-own twins are the only path, and the erasure/NCCT-contribution half stays a Stage-0 empirical gate (hard caps still apply)."}
```
