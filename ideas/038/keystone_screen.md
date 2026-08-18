# Keystone screen — idea 038 (isles24-scout-003-c07)

Screen date: 2026-08-18. Charter: isles24.

## Keystone as stated on the card

> "Enough held-out tissue pairs exist with overlapping anatomy and perfusion
> support but materially different, registration-stable border distance;
> substituted patches pass local continuity and real-versus-edited
> discriminator gates."

## Decomposition: what is checkable at screen prices

The stated keystone is an **empirical census claim**: whether ≥400 eligible
matched patch pairs from ≥30 cases exist, and whether edited patches pass
realism gates. No primary source can answer that; it is decidable only by
running the card's own smallest decisive experiment (the CPU common-support
census, which the card itself designates as the Stage-0 gate). What CAN be
verified against primary sources are the enabling facts the census silently
depends on:

1. The public ISLES'24 release contains co-registered NCCT, CTA, perfusion
   maps (CBF/CBV/MTT/Tmax), and follow-up-derived infarct masks for ~149
   cases (needed for within-case matched swaps in one space).
2. Released CTA-derived vessel / Circle-of-Willis products exist (needed for
   the atlas-vs-vessel-refined distance agreement gate).
3. A public deformable arterial-territory atlas with anterior/middle/
   posterior territory boundaries exists (needed to define X at all).
4. A trained final-infarct model exists to probe (needed for any forward
   pass; see wrong-keystone check).

## Inspections

### 1. ISLES'24 data release — VERIFIED TRUE

Source: Zenodo record https://zenodo.org/records/16731717 (the DOI the card
cites, 10.5281/zenodo.16731717). The record states the training set
comprises "149 acute ischemic stroke cases" with admission imaging
"non-contrast CT (NCCT), CT angiography (CTA), 4D CT perfusion (CTP) time
series, and perfusion maps (Tmax, CBF, CBV, MTT)". The load-bearing
registration fact — the derivatives folder contains

> "all modalities linearly co-registered to the NCCT space"

while raw data are "released in their original space, just defaced".
Annotations include

> "binary infarct masks derived from follow-up MRI (lesion-msk.nii.gz),
> large vessel occlusion binary masks derived from CTA (lvo-msk.nii.gz),
> and the multi-labeled Circle of Willis anatomy generated with an
> automatic algorithm over CTA (cow-msk.nii.gz)."

This confirms enabling facts 1 and 2, including the card's premise that the
CoW product is automatic (fidelity unaudited — the card already carries this
as `keystone_residual_assumption`). Note the registration is stated as
**linear**; residual local misregistration is possible, which is exactly
what the card's one-voxel perturbation repeats are for. Consistent facts in
the dataset paper (arXiv 2408.11142): "This multicenter dataset consists of
245 cases" total, with "vessel occlusion masks from acute CT angiography and
delineated infarction masks in follow-up MRI" — so 149 public training cases
of 245, remainder hidden test; the card's "all public cases" framing is
consistent.

### 2. Arterial-territory atlas — VERIFIED TRUE

Source: NITRC project page https://www.nitrc.org/projects/arterialatlas
(the release repository of Liu et al., Sci Data 2023, DOI
10.1038/s41597-022-01923-0, PMID 36739282). The project description states:

> "The atlas covers supra- and infra-tentorial regions and contains
> hierarchical segmentation levels created by a fusion of vascular and
> classical anatomical criteria."

Download packages are listed for immediate download (ArterialAtlas.zip,
Atlas_MNI152.zip, Vascular_Probabilistic_Maps.nii) under an Attribution
license. The publication (per its own description and the GitHub mirror
github.com/Chin-Fu-Liu/Arterial_Atlas) defines the four major territories —
Anterior, Middle, Posterior Cerebral Arteries and Vertebro-Basilar — in MNI
space, NIfTI format. This is sufficient for the card's ACA/MCA/PCA boundary
distance measure, and the probabilistic maps support the card's
atlas-uncertainty propagation.

### 3. Model to probe — NOT FOUND PUBLICLY (absence, not proof of absence)

The card's experiment requires forward passes through "the final-infarct
model" and budgets compute "after a shared frozen checkpoint". Inspected:

- The winning-solution paper (arXiv 2505.18424, "How We Won the ISLES'24
  Challenge by Preprocessing", full HTML fetched): describes preprocessing —
  "First, we applied SynthStrip on the non-contrast CT (NCCT) scans to
  obtain a brain masks. Then, we applied this brain mask to the other
  co-registered scans (CTP, CTA, etc.)" — and "the 'large' 3D residual
  encoder nnU-Net", but contains **no code-availability statement, no
  repository URL, and no weights release** anywhere in the fetched text.
- The official challenge repository (https://github.com/ezequieldlrosa/isles24)
  contains a data-loading notebook and evaluation utilities only; no
  baseline or participant checkpoints are documented.

Per rules, "I did not find it" is not proof it does not exist (participant
containers may be obtainable via grand-challenge.org or author
correspondence, and the program may train its own nnU-Net on the public
split). But as of this screen, no public frozen ISLES'24 final-infarct
checkpoint was located.

## Wrong-keystone check (mandatory follow-up)

If this card only verified the nearest checkable thing (data + atlas exist),
it is still assuming two things:

1. **The common-support census passes.** The card is honest about this: it
   is the stated keystone, it is `NOT_INSPECTED`, and the card's own
   smallest decisive experiment is the census with a declared kill
   condition ("Failure of common support is not a negative result; it is an
   identifiability kill"). Nothing at screen prices can settle it.
2. **A frozen final-infarct checkpoint is obtainable.** This is the
   assumption the stated keystone does NOT cover and the card's
   `unverified_claims` list omits. My inspection found no released winner
   weights and none in the official repo. This same dependency is already a
   known program-wide feasibility question (ideas 021/023 were forwarded to
   feasibility with model-verification conditions), so it is not unique to
   this card — but it is load-bearing here and must be carried forward
   explicitly: if no checkpoint can be obtained or trained, the swap
   experiment has nothing to probe.

Neither assumption is demonstrably false, so no KILL is available. The
first is the census; the second is an access question with live paths
(grand-challenge containers, self-training nnU-Net on the 149 public
cases). Both are recorded for critique/feasibility.

## Verdict

Every screen-checkable enabling fact is verified TRUE with quoted primary
sources: co-registered multimodal maps and masks for 149 public cases,
released automatic CoW/LVO products, and a public deformable arterial
atlas with the required territory boundaries. The stated keystone itself
(pair support + edit-realism gates) is an empirical Stage-0 census that no
primary source can decide, and the unlisted checkpoint assumption is open.
Honest verdict: UNVERIFIABLE, passed onward with both residuals recorded.

```json
{"verdict": "UNVERIFIABLE", "evidence": "all modalities linearly co-registered to the NCCT space", "source": "https://zenodo.org/records/16731717 (ISLES'24 training release, Derivatives folder description)", "note": "All checkable enabling facts verified true (149-case co-registered release, CoW/LVO masks, public NITRC arterial atlas); the stated keystone is a Stage-0 census only the experiment can answer, and the card additionally assumes an obtainable frozen final-infarct checkpoint, which was not found publicly."}
```
