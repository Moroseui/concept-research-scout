# Keystone screen — idea-047 (isles24-scout-010-c01)

Screened 2026-09-02.

## Keystone as stated on the card

> (1) The frozen per-case contribution table exists in-repo under the
> ratified census; (2) per-case phenotype files carrying the ses-02
> outcome family and ses-01 baseline variables exist inside the held,
> checksum-verified training archive.

## What was inspected

### Part 1 — the frozen contribution table (in-repo, primary artifact)

`probes/046/results/results_v3/per_case_contributions.csv` on main:

- Header (verbatim, line 1): `case_id,d_band2,d_band3,delta,contribution,signed_rank`
- Top data row (verbatim, line 2):
  `sub-stroke0153,-0.11497326203208558,0.5920569329660239,0.7070301949981095,0.007141719141395045,1`
- `wc -l` = 100 lines → 99 data rows, and the 99 `case_id` values are
  unique (`sort -u` count 99).

`probes/046/results/results_v3/census_summary.json` (verbatim excerpts):

- `"10": { ... "signed_head_net_gap_share": 0.7928912778985707 }` under
  `top_k` — the 79.29% top-ten share the question cites.
- `"sign_counts": { "negative": 39, "positive": 54, "zero": 6 }` — the
  39 opposing cases the card cites.

All values match the card's `keystone_evidence` exactly. **Part 1
VERIFIED (verified fact).**

### Part 2 — phenotype members inside the held archive (primary manifest)

`archive_manifest.csv` read from the results branch at
`origin/results/probe-023-349af5ad0b3e:probes/023/results_v2/archive_manifest.csv`
(the manifest of the md5-verified `train.7z`; 2,982 lines):

- Verbatim rows, matching the card byte-for-byte:
  - `train/phenotype/sub-stroke0001/ses-01/sub-stroke0001_ses-01_demographic_baseline.csv,405,184c4588`
  - `train/phenotype/sub-stroke0001/ses-02/sub-stroke0001_ses-02_outcome.csv,98,6f8fa8cd`
- `grep -c 'ses-02_outcome.csv'` = **149**;
  `grep -c 'demographic_baseline.csv'` = **149**.

**Sharper check than the card states** (coverage for the analysis cohort,
not just file existence): joining the 99 census `case_id`s against the
manifest, every one of the 99 has BOTH
`train/phenotype/<id>/ses-02/<id>_ses-02_outcome.csv` and
`train/phenotype/<id>/ses-01/<id>_ses-01_demographic_baseline.csv`
(`comm -23` of the sorted id sets is empty in both directions).
**Part 2 VERIFIED with 99/99 coverage (verified fact).**

### Record-level variable promise (the follow-up the deliverable leans on)

Zenodo record https://zenodo.org/records/16813698 (fetched 2026-09-02),
verbatim from the record description:

> "Clinical data: demographics, patient history, admission NIHSS,
> 3-month functional outcome (mRS), etc."

Files on the record: `clinical_data-description.xlsx` (12.1 kB) and
`train.7z` (99.0 GB); license "Creative Commons Attribution Non
Commercial Share Alike 4.0 International"; Version v3, published
August 12, 2025. All match the card's `verified_dataset_facts`.

## Residual assumption check (wrong-keystone test)

The stated keystone is existence of two file families. The actually
load-bearing assumption for the deliverable sentence is stronger: that
the phenotype files *contain the named variables with usable values for
the 99 cases*. Decomposed:

1. **Variables named at record level** — now VERIFIED (quote above):
   the dataset publisher states admission NIHSS and 3-month mRS are in
   the clinical data.
2. **Per-case files exist for all 99 analyzed cases** — now VERIFIED
   (99/99 join above), which the card's own evidence (149 counts) only
   implied.
3. **Exact column names/coding and per-case missingness** — NOT
   verified, and deliberately so: the card's own D3 read-restriction
   protocol forbids opening case-level phenotype files before the
   frozen spec exists, and the mitigation (freeze the variable list
   from `clinical_data-description.xlsx` first) is the correct order.
   Consistent side evidence without opening anything: `outcome.csv` is
   98 bytes per the manifest — a one-row, few-column table, as
   expected. Residual risk is missing values shrinking the effective
   99; that degrades sensitivity (already scored as a limitation), it
   does not make the study impossible or uninterpretable.

No wrong-keystone error found: the nearest-checkable things beyond the
stated keystone were checked here, and the remaining assumption (3) is
unverifiable by design at this stage, not by neglect.

## Verdict

```json
{"verdict": "PASS", "evidence": "Clinical data: demographics, patient history, admission NIHSS, 3-month functional outcome (mRS), etc.", "source": "https://zenodo.org/records/16813698 (record description); train/phenotype/sub-stroke0001/ses-02/sub-stroke0001_ses-02_outcome.csv,98,6f8fa8cd in origin/results/probe-023-349af5ad0b3e:probes/023/results_v2/archive_manifest.csv", "note": "Both keystone parts verified verbatim; sharper 99/99 phenotype coverage join also passes; only column-level coding remains open, correctly deferred behind the D3 protocol."}
```
