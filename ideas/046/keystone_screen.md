# Keystone screen — idea 046

## Keystone as stated

The card states a two-part prerequisite:

1. The imported take-13 `per_patient.csv` must support exact per-patient band-2/band-3 contribution accounting: 99 unique cases per band, finite `d` values, and unique join keys.
2. The pinned ISLES'24 release must contain a small phenotype outcome table whose identifiers join to at least 90 of those 99 analyzed cases and which has at least one usable ordinal outcome column.

Part 1 is directly inspectable in the repository. Part 2 requires the actual phenotype payload, not merely a release description or variable dictionary.

## What was inspected

### 1. Imported take-13 per-patient table — verified true

I inspected the committed primary result artifact [`probes/023/results/results_v2/per_patient.csv`](../../probes/023/results/results_v2/per_patient.csv). Its verbatim header and first three data rows are:

> `case_id,stratum,q1_voxels,q4_voxels,d`  
> `sub-stroke0002,1,3969,3970,-0.20385563685311792`  
> `sub-stroke0002,2,4091,4090,-0.12122399996653155`  
> `sub-stroke0002,3,3973,3967,0.46590100775393983`

A deterministic census of the full file found 297 rows, 297 unique `(case_id, stratum)` keys, 99 unique case IDs, 99 rows in each of strata 1, 2, and 3, and 297/297 finite `d` values. Therefore the band-2/band-3 contribution accounting is executable from this artifact.

### 2. Pinned Zenodo record and official repository — nearest facts verified, load-bearing join not verified

The pinned primary release is Zenodo record 16813698. Its API response lists `train.7z` (99,014,629,647 bytes; MD5 `36ae28b9a17f7340b8bbef62b595cb57`) and the small `clinical_data-description.xlsx` dictionary. The record description says verbatim:

> “Clinical data: demographics, patient history, admission NIHSS, 3‑month functional outcome (mRS), etc.”

Source: https://zenodo.org/api/records/16813698, `metadata.description`, “For each case” list.

The official repository shows the intended payload path verbatim:

> `+-- phenotype`  
> `|       +-- ses-0001`  
> `|           +-- sub-strokecase0001_ses-0001_demographic_baseline.csv`  
> `|       +-- ses-0002`  
> `|           +-- sub-strokecase0001_ses-0001_outcome.csv`

Source: https://github.com/ezequieldlrosa/isles24/blob/main/README.md, lines 38–42 (repository inspected at current `main`).

I downloaded and inspected the actual `clinical_data-description.xlsx` from record 16813698 (SHA-256 `7f7dd4dadbe46113ae30be37b8bef425318336206f17b5079909517681a646a2`). Its outcome rows include verbatim:

> `Outcome | NIHSS 24h | numerical integer | NIHSS 24 hours after admission in hospital examined by the neurologist.`  
> `Outcome | MRS 3 months | numerical integer | mRS 3 month after stroke, inquired per telephone by study nurse.`

Source: https://zenodo.org/api/records/16813698/files/clinical_data-description.xlsx/content, worksheet `Sheet1`, rows 32 and 36.

These primary sources establish that phenotype files and suitable NIHSS/mRS fields are intended. They do **not** expose the 149 per-case phenotype CSV bytes separately: those bytes are members of the approximately 99 GB `train.7z`. Neither the release description, official repository example, nor dictionary establishes the actual case-ID spelling, missingness, or overlap with the particular 99 take-13 IDs. The required threshold of at least 90 joined cases was therefore not verified.

## Residual-assumption check

**If this card only verified the nearest checkable thing, what is it still assuming?**

It verified that an outcome-file family is documented and that the dictionary names ordinal outcomes. It is still assuming the load-bearing fact that the *actual files in the pinned archive* use identifiers mappable without ambiguity to `sub-strokeNNNN`, contain populated outcome values for the analyzed cohort, and yield at least 90 matches among the exact 99 take-13 cases. The documentation's example uses `sub-strokecase0001`, while the imported result uses `sub-stroke0002`; prior experience with this release already shows that documentation examples can differ from payload names. Thus schema existence is the nearest checkable fact, but actual join coverage is the real unresolved keystone.

Part 1 passes. Part 2 is neither shown false nor verified true. Because the card explicitly allows the contribution rung to proceed if the clinical rung fails, this uncertainty does not demonstrate that the entire candidate is impossible; it leaves the stated two-part keystone unresolved and must pass onward as `UNVERIFIABLE` rather than be guessed.

```json
{"verdict": "UNVERIFIABLE", "evidence": "Clinical data: demographics, patient history, admission NIHSS, 3‑month functional outcome (mRS), etc.", "source": "https://zenodo.org/api/records/16813698 — metadata.description, 'For each case' list; actual per-case phenotype members remain inside train.7z", "note": "The 99-case contribution table is verified usable, but actual phenotype identifier overlap and >=90-case outcome join coverage cannot be established without inspecting the archive members."}
```
