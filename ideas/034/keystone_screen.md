# Keystone screen — idea 034 (isles24-scout-004-c07)

Stage run 2026-08-18. Screener: keystone stage, full network access, sandboxed
execution (no local data downloads possible; see §4).

## 1. The keystone as stated

From `idea_card.json`, `keystone_prerequisite`:

> The released perfusion support is actually narrower than the brain in a
> non-trivial fraction of cases, and ground-truth lesion mass overflows it in
> enough cases to matter (prespecified: overflow > 5% of lesion volume in
> >= 10% of cases).

`keystone_status` on the card: `NOT_INSPECTED`.

## 2. What I inspected

### 2a. Primary papers: coverage is genuinely undocumented (confirms the card's negative claim)

- **Dataset paper** (arXiv 2408.11142, "ISLES'24 — A Real-World Longitudinal
  Multimodal Stroke Dataset"; published as Radiology: Artificial Intelligence,
  DOI 10.1148/ryai.250603). Full-text extraction (via jina reader over
  https://arxiv.org/pdf/2408.11142) found **no statement of CTP z-coverage,
  slab thickness, slice count, or perfusion-map spatial extent**. The scanner
  list is stated:
  > "CT image acquisition was performed on the following devices: Somatom
  > Force, Somatom Xcite (Siemens Healthcare), Somatom AS+ (Siemens),
  > Brilliance 64, and Ingenuity (Philips Healthcare)."
  The only coverage remark concerns CTA, not CTP ("Since the CTAs were cropped
  uniformly and cover only the head and not the neck…"). Perfusion maps:
  > "perfusion maps (cerebral blood flow, cerebral blood volume, mean transit
  > time, and time-to-maximum) were derived using the clinical, U.S. Food and
  > Drug Administration–cleared software icobrain cva (version 1.5.0,
  > icometrix)."
- **Challenge paper** (arXiv 2408.10966v2, HTML): no passage on CTP coverage,
  slab, missing slices, or lesions beyond CTP extent, in methods, team
  descriptions, or limitations (targeted extraction, two passes).
- **Winning-team preprocessing paper** (arXiv 2505.18424v1): no mention of
  perfusion coverage or map/ground-truth extent mismatch.

Inference (labeled as such, not load-bearing): a Philips Brilliance 64 is a
64-row scanner whose CTP acquisitions are physically slab-limited; its
presence in the device list makes whole-brain CTP for all cases implausible.
This inference was NOT used for the verdict; direct evidence follows.

### 2b. The decisive evidence: the challenge's own forum thread

An official ISLES'24 Grand Challenge forum thread exists titled **"How will
lesion voxels outside the field of view of the CTP imaging be handled?"**
Canonical URL (301 target of the indexed Grand Challenge forums URL):
`https://isles-24.grand-challenge.org/forum/topics/how-will-lesion-voxels-outside-the-field-of-view-of-the-ctp-imag/`
(indexed form:
`https://grand-challenge.org/forums/forum/ischemic-stroke-lesion-segmentation-challenge-2024-722/topic/how-will-lesion-voxels-outside-the-image-extent-of-the-baseline-imaging-be-handled-2451/?post=6348`).

Content retrieved via search-engine index of that page (provenance caveat in
§2c). Participant report, quoted:

> "For a number of patients in ISLES'24, the field of view captured by the
> CTP is smaller than that of the DWI, and as a result, some tissue that is
> visible on DWI simply was not imaged via CTP. In many cases, some of the
> tissue that was imaged via DWI but not CTP (these voxels are completely
> empty in the derived CTP images) are segmented as part of the lesion."

> "For patient 0019, for example, there are 1685 voxels (occurring on slices
> 58, 59 and 60) that were segmented as lesion on DWI, but are outside the
> image extents of the CTP data."

> "It is impossible to predict this part of the lesion using information from
> the CTP data since the CTP image is completely blank on the slices where
> this part of the lesion occurs."

Organizer response (same thread, retrieved the same way):

> the organizers "are not masking out voxels outside the field of view, as
> the lesions do exist in the considered brain, and the reduced field of view
> is just a technical limitation" — because "this is a lesion segmentation
> challenge (not a sole CTP-centered lesion segmentation challenge)."

This establishes, on the challenge's own record, all qualitative components
of the keystone: (i) CTP support narrower than the scored target in "a number
of patients" of this release; (ii) ground-truth lesion mass overflowing the
support in a concrete released training case (patient 0019, 1685 voxels,
slices 58–60); (iii) out-of-support voxels are deliberately NOT masked in
evaluation, so the overflow is scored — the metric consequence the idea
targets is real, and is an explicit organizer design decision; (iv) the
out-of-support region is "completely empty" in the derived maps, directly
supporting the card's assumption that support masks are recoverable from map
degeneracy.

### 2c. Provenance caveat on the forum quotes

The forum page itself returns 403 to anonymous fetches (both direct and via
proxy), and no Wayback snapshot exists (checked
`archive.org/wayback/available` for both URL forms, both empty). The quotes
above come from search-engine-indexed content of the official thread,
returned consistently across three independent queries — including an
exact-phrase query (`"1685 voxels" "outside the image extents"`) whose top
hit is precisely this thread, which is strong evidence the strings appear
verbatim on the page. Classification per COLLABORATOR_RULES:
**source-supported quotes**, one step short of a directly loaded page.
Cheap hardening action for the feasibility stage: anyone with a (free)
challenge registration loads the thread and confirms the two quoted posts.

### 2d. Data access (bears on the census's checkability)

- The full 149-case training set is now **openly downloadable without
  challenge registration**: Zenodo record 16813698 ("ISLES'24 - A Real-World
  Longitudinal Multimodal Stroke Dataset", `train.7z`, 99.0 GB, license
  CC BY-NC-SA 4.0, access: open; DOI 10.5281/zenodo.16813698), plus a
  Hugging Face mirror (`hugging-science/isles24-stroke`, 149 per-case parquet
  shards, ~26 GB). The card assumed challenge-site registration; access is
  strictly easier than assumed.
- Release structure confirms both spaces the census needs: raw perfusion maps
  and derivatives "linearly co-registered to the NCCT space", with the lesion
  mask in the same derivative tree (official repo README,
  github.com/ezequieldlrosa/isles24: derivative filenames
  `sub-strokecase0001_ses-0001_space-ncct_tmax.nii.gz`,
  `…_ses-0002_lesion-msk.nii.gz`; evaluation code at `utils/eval_utils`, MIT).

## 3. Residual assumption check (mandatory follow-up)

*If this screen only verified the nearest checkable thing, what is the card
still assuming?*

1. **The quantitative thresholds** (overflow > 5% of lesion volume in ≥ 10%
   of cases) remain unmeasured. This is not a wrong-keystone situation: the
   card itself prespecifies these as stage 1's kill criterion, and stage 1 is
   the census that measures them. The screen's finding is that the phenomenon
   exists in the release and is scored by the official metrics; magnitude is
   exactly what the one-session stage 1 is for.
2. **Support-mask recoverability**: supported by "completely empty in the
   derived CTP images", but zeros-vs-NaN convention and degeneracy criteria
   still need the preregistered definition the card already promises. Both
   raw-space maps and NCCT-space derivatives exist, so support can be
   computed in raw space and transformed as a cross-check.
3. **Forum quote provenance** (§2c): verbatim page-level confirmation
   requires a challenge login; flagged as a feasibility-stage action, not a
   blocker.
4. Stage 2 (model behavior at the boundary) additionally assumes the shared
   audit model exists; the card already gates stage 2 on that and the verdict
   here does not depend on it.

## 4. Execution note

Local inspection of actual NIfTI geometry (the card's "three downloaded
cases in under an hour") was attempted and is impossible in this sandbox:
network Bash and Python execution are blocked (unsandboxed run denied). A
draft probe script written for that attempt was deleted unexecuted, in
keeping with the coding gate; no code deliverable exists from this stage.
The verdict rests entirely on the documentary evidence above.

## 5. Verdict

The keystone is verified in kind on the challenge's own record — CTP support
narrower than the scored target, released ground truth overflowing it in a
named training case, out-of-support voxels deliberately scored — with
magnitude left to the prespecified stage-1 census, which is what stage 1 is
for. The card's premise is not built on data the dataset lacks; it is built
on a property the organizers themselves acknowledged and chose to keep.

```json
{"verdict": "PASS", "evidence": "For patient 0019, for example, there are 1685 voxels (occurring on slices 58, 59 and 60) that were segmented as lesion on DWI, but are outside the image extents of the CTP data.", "source": "Official ISLES'24 challenge forum thread 'How will lesion voxels outside the field of view of the CTP imaging be handled?' (isles-24.grand-challenge.org/forum/topics/how-will-lesion-voxels-outside-the-field-of-view-of-the-ctp-imag/); retrieved via search-engine index of the page (page 403 to anonymous access), exact-phrase match confirmed", "note": "Slab-narrower-than-target confirmed qualitatively on the challenge's own forum, organizers confirm out-of-FOV lesion voxels are scored; quantitative 5%/10% thresholds remain stage 1's prespecified census; forum quotes need one page-level confirmation by a registered user at feasibility."}
```
