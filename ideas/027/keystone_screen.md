# Keystone screen — idea 027 (isles24-scout-003-c05)

**Card:** "When vanished sulci mean rescue, not death"
**Stage:** keystone screen, run 2026-08-18.

## The keystone as stated

> "ISLES'24 contains enough automatically detectable isolated-sulcal-effacement
> territories, and single-phase CTA plus NCCT can distinguish the
> collateral-engorgement pattern from edema and registration error without new
> expert labels."

Two clauses: (a) sufficient support in the cohort (the card's own Stage-0 gate
is >=15 qualifying territories); (b) the released modalities can carry the
discriminating triad without new annotation.

## What was inspected

### 1. ISLES'24 dataset composition (charter hard rule + keystone clause b)

**Primary data-hosting page** — Zenodo record 16813698, "ISLES'24 — A
Real-World Longitudinal Multimodal Stroke Dataset"
(https://zenodo.org/records/16813698), fetched 2026-08-18:

- Per-case imaging (verbatim): admission "non-contrast CT (NCCT), CT
  angiography (CTA), 4D CT perfusion (CTP) time series, and perfusion maps
  (Tmax, CBF, CBV, MTT)" plus "post-treatment MRI (DWI and ADC)" at follow-up.
- Cohort (verbatim): "149 acute ischemic stroke cases" — the released
  training set. Matches the card's "all 149 cases".
- Registration (verbatim): raw data "released in their original space, just
  defaced"; derivatives with "all modalities linearly co-registered to the
  NCCT space". The card's assumption of registered NCCT/CTA/perfusion maps
  holds in the derivatives release.
- Ground truth (verbatim): "binary infarct masks derived from follow-up MRI
  (lesion-msk.nii.gz)".
- License: Creative Commons Attribution Non Commercial Share Alike 4.0
  International. Public download (train.7z, 99.0 GB).

**Challenge paper** — arXiv:2408.10966 ("ISLES'24: Final Infarct Prediction
with Multimodal Imaging and Clinical Data"), Methods/Dataset section, fetched
2026-08-18:

> "acute imaging data have been acquired at patient admission and include the
> diagnostic CT trilogy: NCCT, CTA, and CTP, as well as CTP-derived perfusion
> maps (namely CBF, cerebral blood volume (CBV), mean transit time (MTT), and
> time-to-maximum of the residue function (Tmax)). The follow-up imaging data
> were acquired 2 to 9 days later and included DWI and ADC."

> "Preprocessing of the images has been performed by linearly interpolating
> and registering all the imaging series to the NCCT scans."

> "Lesion masks are derived from the follow-up MRI using DeepISLES. Quality
> control and correction of the lesion masks are performed when needed by
> medical students supervised by two neuroradiologists with more than 10
> years of experience."

Cohort selection (Discussion/Limitations, verbatim):

> "the inclusion criteria of the ISLES'24 dataset were restricted to patients
> with favorable recanalization outcomes (i.e., thrombolysis in cerebral
> infarction -TICI- scores 2B and 3)."

Split accounting (Methods, verbatim): "The dataset (N = 248) is split into
train (N = 150) and test subsets (N = 98)." The public Zenodo release states
149; the one-case discrepancy between the paper's split table and the released
training set is noted, non-blocking, and consistent with the card's 149.

### 2. The cited clinical series (the base rate behind clause a)

**PMID 25931460** — abstract retrieved via NCBI E-utilities
(https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id=25931460&rettype=abstract&retmode=text),
Stroke. 2015 Jun;46(6):1704-6, fetched 2026-08-18. Verbatim:

- "Out of the 568 patients who underwent intra-arterial therapy between March
  2011 and September 2014, 108 fulfilled inclusion criteria."
- "ISE was present in 8 (7.4%) patients"
- "Follow-up imaging confirmed no infarct in the ISE area in all patients"
- "Computed tomography angiogram revealed engorged/dilated leptomeningeal
  vessels obliterating the sulci within the areas of effacement"

The card's factual citations (108 cases, 8 with the sign, no follow-up infarct
in the effaced area, CTA-visible engorged vessels) are transcription-accurate.

## The support-count arithmetic (inference, not verified fact)

Both cohorts are endovascular-therapy populations (the series: intra-arterial
therapy; ISLES'24: thrombectomy with TICI 2B/3), so the 7.4% base rate is at
least the right population family. Scaled to 149 cases: expected support
~11 territories. Hand-computed Clopper-Pearson 95% interval for 8/108 is
approximately 3.3%-14.0%, i.e. roughly 5 to 21 cases in 149. The point
estimate falls BELOW the card's own >=15 Stage-0 gate; the interval spans
both failure and pass. The automatic triad is additionally not the same
construct as the radiologist-called sign, so its firing rate may differ in
either direction. This clause is therefore genuinely undecidable from
primary sources — it is exactly what the card's Stage-0 census (blind,
cheap, no model needed) exists to decide.

## Residual assumption check (mandatory follow-up)

If this card only verified the nearest checkable things (modalities exist,
the series says what it says), it is still assuming:

1. **Support >=15** — undecidable without the census; point estimate ~11 is
   short of the gate (above).
2. **Construct validity of the automatic triad** — that sulcal-CSF fraction +
   preserved gray-white contrast + pial-vessel occupancy computed from the
   registered volumes reproduces the radiologist's sign. No primary source
   can settle this; the card honestly gates on it.
3. **NCCT/CTA spatial quality** — the real-world admission NCCT slice
   thickness is not stated in the challenge paper or the Zenodo record I
   could access; thick-slice NCCT would degrade automatic sulcal-CSF and
   gray-white measurement. Unverified either way; forward to Stage 0 as an
   explicit early check.
4. **CTA phase adequacy** — single-phase CTA timing variability (the card
   cites PMID 29674417) remains a stated, unresolved threat; the dataset
   provides no multiphase CTA to rescue it.

The card's stated keystone and its `keystone_residual_assumption` field
already name (1) and (2) as the real keystone — no wrong-keystone error
found. The load-bearing assumption the card states is the load-bearing
assumption that exists.

## Verdict

All checkable enabling facts verified TRUE with quotes: the dataset publicly
provides every modality the triad needs, co-registered to NCCT space, with
follow-up-derived lesion masks, on a 149-case thrombectomy cohort. The
keystone's decisive clause — enough detectable territories — cannot be
verified or falsified from any primary source; it requires the Stage-0
census, and the verified base-rate arithmetic says the outcome is marginal
(expected ~11 vs. a >=15 gate). Not demonstrably false, so not a KILL;
not verifiable, so not a PASS.

```json
{"verdict": "UNVERIFIABLE", "evidence": "ISE was present in 8 (7.4%) patients", "source": "PMID 25931460 (Stroke. 2015;46(6):1704-6), abstract via NCBI E-utilities efetch", "note": "All modality/registration/access prerequisites verified true on Zenodo 16813698 and arXiv:2408.10966; the support-count clause is undecidable pre-census, with expected ~11 territories vs the card's own >=15 gate (95% CI spans 5-21)."}
```
