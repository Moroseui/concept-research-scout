# Keystone screen — idea 031 (isles24-scout-001-c02)

**Idea:** The vascular detour the segmentation model can see
**Stage run:** 2026-08-18

## The keystone as stated

> The public 149-case release actually contains per-case occlusion masks and
> Circle-of-Willis/distal-vessel pseudolabels in a coordinate system usable
> with CTA, with sufficient distal coverage for the proposed reach measure.

This is a conjunction of three clauses: (1) per-case occlusion masks exist,
(2) vessel pseudolabels exist in a CTA-usable coordinate system, (3) those
pseudolabels have sufficient **distal** coverage for the proposed measure
("affected/contralateral distal vessel-length density within atlas-defined
downstream territories" — i.e., vessels downstream of the occlusion).

## What was inspected

### 1. The official data release (Zenodo record 16813698)

Source: https://zenodo.org/records/16813698 (DOI 10.5281/zenodo.16813698;
confirmed via the record page and the Zenodo REST API
https://zenodo.org/api/records/16813698). This is the current official
release: "ISLES'24 — A Real-World Longitudinal Multimodal Stroke Dataset,"
149 acute ischemic stroke cases (the challenge training set), one archive
`train.7z` (~99 GB) plus `clinical_data-description.xlsx`, license CC
BY-NC-SA 4.0, open access.

The record's description enumerates, per case, in a derivatives tree
co-registered to NCCT space (`_space-ncct_`, ses-0001 acute / ses-0002
follow-up):

- `lesion-msk.nii.gz` — "binary infarct masks derived from follow-up MRI"
- `lvo-msk.nii.gz` — "large vessel occlusion binary masks derived from CTA"
- `cow-msk.nii.gz` — "multi-labeled Circle of Willis anatomy generated with
  an automatic algorithm over CTA"

The record additionally instructs users to cite Yang et al. (2024) — the
TopCoW challenge — "if using Circle of Willis masks."

**Finding:** clauses (1) and (2) are supported at the documentation level.
Occlusion masks and vessel pseudolabels exist as named per-case derivative
files, co-registered to NCCT space alongside the registered CTA. (Verified
fact at the release-schema level; per-case file completeness across all 149
cases was NOT file-verified — the 99 GB archive was not downloaded. That
residual is moot given the clause-3 finding below.)

### 2. The dataset paper (Riedel et al.)

Source: arXiv:2408.11142v2 (6 Jul 2025), "ISLES'24 — A Real-World
Longitudinal Multimodal Stroke Dataset" — the arXiv version corresponding to
the Radiology: AI paper the card cites (DOI 10.1148/ryai.250603; the RSNA
page itself blocks automated fetch, so quotes below are from the arXiv v2
PDF text; title and authorship match — source-supported interpretation).

On the occlusion mask (section "Vessel occlusion segmentation in CTA
scans"): the mask marks "the point of vessel occlusion — the final segment
of the vessel before the occlusion is marked"; segmentations "were carried
out manually by a neuroradiology resident using ITK-SNAP, controlled and
revised if necessary by an experienced neuroradiology attending." So the
occlusion derivative is a manually produced occlusion-point marker — usable
for locating the occlusion, as the card needs.

On the vessel pseudolabels (section "Segmentation of the Circle of Willis
(CoW) for CTA scans"): the models were "trained on a combined CTA and MRA
dataset using an extended U-net framework," and — decisive for quality
expectations — "These segmentations serve as a silver ground-truth, offering
a coarse reference segmentation not traced by experts." The figure legend
enumerates the complete label set:

> "Yellow = left ACA, light blue = right ACA, gray = AcomA, red = left ICA,
> purple = left MCA, brown = right ICA, pink = right MCA, orange = left PCA,
> green = right PCA, medium blue = basilar artery."

That is ten labels, all proximal Circle-of-Willis arteries. A targeted
verbatim sweep of the paper for any mention of vessels distal to the circle
(M2/M3/M4, pial, leptomeningeal, distal branches, whole-brain vasculature)
returned: **no such mention exists**.

### 3. The annotation standard the pseudolabels inherit (TopCoW)

Source: arXiv:2312.17670v3 (Yang et al., TopCoW challenge — the work the
Zenodo record requires citing for the CoW masks), sections 2.5 and 2.7. The
13 annotated components are the ICA, ACA, MCA, PCA (left/right), Acom,
Pcom (left/right), and basilar artery, and "only vessel components and
regions necessary to diagnose the CoW angio-architecture and variants were
annotated." The distal boundary is explicit:

> "we typically only labelled until the first major bifurcation occurs, and
> we only labelled the main vessel instead of any minor branches."

## The verdict logic

The proposed X_measurement is "affected/contralateral distal vessel-length
density within atlas-defined downstream territories," computed from "the
released TopCoW-style vessel mask plus occlusion mask." For a typical
ISLES'24 occlusion (M1/M2/ICA), the downstream territory contains M2–M4 and
pial collateral vasculature — precisely the vessels that a CoW-anatomy mask,
by its own definition and by the TopCoW annotation boundary it inherits,
does not contain. The released pseudolabels stop at or near the first major
bifurcation; downstream of the marked occlusion point there is essentially
zero labeled vessel to measure. Clause (3) of the keystone — "sufficient
distal coverage for the proposed reach measure" — is false at the level of
the release's own schema and the generating method's documented extent, not
merely unchecked. The reach measure cannot be computed from released files.

## Residual-assumption check (mandatory follow-up)

The card itself anticipated this: its `keystone_residual_assumption` says
"file-level completeness and distal-vessel coverage are the real keystone."
That self-diagnosis was correct, and the card's stated keystone does include
the distal-coverage clause — so this is not a wrong-keystone error by the
card. What the card had verified (a 2026 paper documents the
pseudolabel-generation method) was the nearest checkable thing; the thing it
was still assuming — that those pseudolabels reach distal territory — is the
clause that fails. Had the keystone been only "occlusion and CoW mask files
exist per case," it would (pending file-level audit) likely have passed, and
the idea would have died later, at Stage 0 prices instead of screen prices.

Salvage path, recorded without endorsement (not this card's design): distal
vessel segmentation could be computed fresh from the released CTA with an
off-the-shelf cerebrovascular segmentation tool. That replaces "released
pseudolabel files" with a new, unvalidated measurement pipeline — a
different X_measurement and a different feasibility profile, hence a
successor candidate under the claim-identity rule, not a repair.

## Verdict

```json
{"verdict": "KILL", "kill_code": "DATA_ACCESS", "evidence": "we typically only labelled until the first major bifurcation occurs, and we only labelled the main vessel instead of any minor branches", "source": "arXiv:2312.17670v3 section 2.7 (TopCoW annotation protocol, the standard the ISLES'24 cow-msk inherits per https://zenodo.org/records/16813698, whose schema defines cow-msk.nii.gz as 'multi-labeled Circle of Willis anatomy'; corroborated by arXiv:2408.11142v2, whose CoW label set is exclusively proximal and which nowhere mentions distal-vessel segmentation)", "note": "Per-case occlusion masks and CoW pseudolabels exist, but the release contains no distal-vessel labels, so the distal collateral-reach measure cannot be computed from released files; fresh distal segmentation of the CTA would be a successor idea, not this card."}
```
