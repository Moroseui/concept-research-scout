# Keystone screen — idea 037 (isles24-scout-004-c06): The scan remembers which hospital took it

Screen date: 2026-08-18. Charter: isles24.

## The keystone as stated

From `idea_card.json`, `keystone_prerequisite`:

> "Site identity is decodable from noise-only patches of the MODEL-FACING
> derivative inputs (registration and resampling may have attenuated the raw
> fingerprint), and the shared audit model reaches non-trivial held-out
> performance."

This keystone has two parts, and both are **empirical outcomes, not
document facts**: (a) the decodability census is itself the card's Stage 0
experiment, and (b) the shared audit model does not exist yet. No primary
source can settle either by inspection. What a document screen CAN settle
is whether the census is *runnable at all* — and that is where the
wrong-keystone check bites (below).

## Mandatory follow-up: what is the card still assuming?

If the card only verified the nearest checkable things (two-center
composition, raw release), the census still silently assumes:

1. **Per-case site labels are recoverable from the public release.**
   Without a case-to-center mapping there is nothing to train the
   Munich-vs-Zurich classifier against and no way to score it — the entire
   Stage 0 census is impossible, decodability true or not. The card never
   lists this as an assumption. This is the load-bearing checkable
   keystone, and I verified it.
2. Both raw (original-space) and derivative (model-facing) images are in
   the release, per case.
3. The two centers' scanner fleets differ (card flags this as assumed, not
   known).

## What I inspected

### 1. Per-case site labels — VERIFIED TRUE (the hidden keystone)

Dataset descriptor paper, arXiv 2408.11142v2 (PDF fetched and text
extracted 2026-08-18), section *Data Records — Folder structure*:

> "An info sheet, included with our data in the repository, defines the
> clinical baseline and outcome parameters. **It also lists all cases with
> their respective originating centers and the sets they are assigned
> to.**"

And *Data Records — Data structure*:

> "The train set contains n = 99 scans from Center 1 and n = 50 cases from
> Center 2 and is publicly available."

Center identities are named in *Methods — Image acquisition*:

> "Healthcare professionals obtained images as part of the clinical imaging
> routine for stroke patients at two stroke centers in Germany and
> Switzerland: Center 1 - University Hospital of the Technical University
> of Munich in Munich, Germany, and Center 2 - University Hospital of
> Zurich in Zurich, Switzerland."

The case-to-center mapping is disclosed by design, in the repository
itself. The census can be trained and scored.

### 2. Raw + derivative release — VERIFIED TRUE

Same paper, *Methods — Data pre-processing*:

> "All images are released 'raw' (i.e., solely anonymized and defaced) and
> preprocessed (i.e., resampled and co-registered to the NCCT space)."

Zenodo record 16731717 (v3, 2025-08-12, train.7z 99.0 GB, 149 cases,
fetched 2026-08-18) confirms on the release page itself:

> "Raw_data refers to the 'raw' acquired scans, which are released in their
> original space, just defaced."

with derivatives described as "all modalities linearly co-registered to
the NCCT space", and admission imaging comprising "non-contrast CT (NCCT),
CT angiography (CTA), 4D CT perfusion (CTP) time series, and perfusion
maps (Tmax, CBF, CBV, MTT)". Both the raw arm (fingerprint reference) and
the derivative model-facing arm of the census exist per case.

### 3. Fleet separation — UPGRADED from assumed to source-supported

The card recorded: "vendor/protocol identity was not verifiable from the
papers (neither states scanner hardware, checked this stage), so fleet
separation between the centers is assumed, not known." The dataset
descriptor paper (which the card did not inspect) states, *Methods — Image
acquisition*:

> "CT image acquisition was performed on the following devices: Somatom
> Force, Somatom Xcite (Siemens Healthcare), Somatom AS+ (Siemens),
> Brilliance 64, and Ingenuity (Philips Healthcare)."

> "Stemming from two centers and different scanner models and
> manufacturers, the dataset described here allows the development of
> robust and generalizable stroke lesion segmentation algorithms."

Five CT scanner models across two manufacturers. Caveat, stated honestly:
the paper does **not** map devices to centers, so clean between-center
fleet separation remains source-supported interpretation, not verified
fact. Hardware heterogeneity in the dataset is now verbatim on record;
the census answers the per-center split empirically, exactly as the card
already plans.

### 4. The attenuation threat is real and correctly targeted

*Methods — Data pre-processing*:

> "Data pre-processing consisted of image co-registration to compensate
> for head motion and temporal resampling (1 frame/second) of the 4D CTP
> series."

> "CTA, CTP (including derived perfusion maps), and DWI/ADC scans were
> linearly co-registered to the NCCT space using rigid transformations for
> CT-based images, and affine transformations for MRI."

Also relevant to the census's noise-patch plan: "CT scans were defaced
using in-house developed scripts based on TotalSegmentator" (defacing may
remove some extracranial-air ROIs — the card already anticipates this),
and "Laboratory values and times were randomly altered by ± 5 % for
anonymization purposes" (imaging is untouched by that perturbation). The
resampling/registration attenuation risk the keystone names is exactly
what the released derivative data carries; the question is live, not
settled.

## Discrepancy of record

The card (and challenge paper arXiv 2408.10966: "The train (test) set
contains N = 100 (N = 50) scans from the University Hospital of Munich and
N = 50 (N = 50) scans from the University Hospital of Zurich") says 100
Munich train cases; the dataset descriptor and the Zenodo release say 99
Center 1 train cases / 149 total. One case was evidently dropped between
the challenge design and the public release. Immaterial to the keystone;
the card's cohort numbers should read 149 (99 + 50) for the public train
set.

## Residual assumption check

What remains genuinely unverified after this screen — carried forward, not
resolved:

- **Decodability itself** on model-facing derivative inputs: empirical,
  Stage 0's job by design. Cannot be inspected into truth.
- **Shared audit model performance**: the model does not exist yet;
  conditional dependency shared with the cycle's baseline candidates.
- **Per-center fleet composition**: devices verified, device-to-center
  mapping unstated in every inspected source.
- Whether the released info sheet's center column survives intact inside
  train.7z (the paper says it is there; the 99 GB archive was not
  downloaded at screen prices).

None of these is falsifiable from documents; none is demonstrably false;
the first two are exactly what the card's prespecified Stage 0 gate
exists to test, and the card kills cleanly if the gate fails.

## Verdict

The stated keystone is an empirical census outcome and therefore cannot be
document-verified either way — but every checkable prerequisite for
running that census, including the card's unstated load-bearing assumption
(per-case site labels), verified TRUE with verbatim quotes, and one card
assumption (hardware heterogeneity) was upgraded from assumed to
source-supported. Nothing false was found. Honest verdict: UNVERIFIABLE,
passing the idea onward with the empirical gate intact and the census
confirmed runnable.

```json
{"verdict": "UNVERIFIABLE", "evidence": "An info sheet, included with our data in the repository, defines the clinical baseline and outcome parameters. It also lists all cases with their respective originating centers and the sets they are assigned to.", "source": "arXiv 2408.11142v2 (ISLES 2024 dataset descriptor), Data Records - Folder structure; corroborated by Zenodo record 16731717", "note": "Keystone is an empirical Stage-0 census by design; all checkable prerequisites verified true, including the unstated one (per-case center labels are released), so the census is runnable and the gate is live."}
```
