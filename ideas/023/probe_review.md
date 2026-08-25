# Probe code review — idea 023, round 4 (first review of the post-exit-5-directive revision)

**Reviewed artifacts:** `probes/023/run.py` (SHA-256
`d2dd41a6bad5fc2f74414a008e5f24873e907734d88440c021860392bce8a569`),
`probes/023/requirements.txt` (SHA-256 `ff705c03…`, byte-identical to the
round-2/3 file), `probes/023/README.md` (SHA-256 `ffdd3565…`),
`probes/023/verification.json` (hashes match all three), against the amended
`ideas/023/probe_contract.yaml` (git blob
`349af5ad0b3e8acfc6337d15f1860974d1183393` — recomputed this round and
identical to the blob in `ideas/023/HUMAN_APPROVED_PROBE`; the contract is
untouched, so the standing Phase-C approval remains bound). Prior code at
commit `5faa013` (run.py SHA-256 `8bd3156b…`, the round-3 APPROVE); revised
code at commit `7fbef0e`. Review rounds 1–3 preserved in git.

**Scope note.** This is not a fresh-plan review. The 2026-08-25 decision entry
("023 Phase C attempt 2: exit 5, archive census 0 cases") issued a bounded
revision directive: (1) derive case discovery from observed archive members,
tolerating `sub-stroke\d+` and `sub-strokecase\d+` and both `raw_data`/`rawdata`;
(2) surface the payload's 150th lesion row explicitly in `schema_census.csv`
and route it through `exclusions.csv` with a reason; (3) change nothing else —
contract, gates, thresholds, and analysis untouched, standing approval valid.
This review verifies the code implements exactly that directive and nothing
else, and additionally validates the new discovery logic against the **real
archive member manifest** (2,983 members) persisted by the attempt-2 bundle.

**Requirements conformance (review rule 5):** `ideas/023/contract_requirements.md`
does not exist; not a requirements-governed contract. Not applicable.

**External evidence:** none newly fetched from the network. The ground truth
for the payload is `probes/023/results_v2/archive_manifest.csv` at commit
`0cfec9f` on branch `results/probe-023-349af5ad0b3e` — produced by the
attempt-2 run itself after both digest passes verified the Zenodo checksum,
which makes it the strongest available evidence of the archive's contents.

---

## Disposition of the three directive requirements

| Directive item | Status in this code |
|---|---|
| Case discovery from archive members, tolerant of both id spellings and both rawdata spellings | **Resolved** — `archive_case_inventory` (`run.py:226-288`) derives the cohort from the 7z member manifest, never from extracted-directory globs or release prose (`run.py:646-648` states this as the population authority); the case pattern `sub-(?:stroke\|strokecase)\d+` (`run.py:230`, case-insensitive) accepts both spellings; discovery is by exact filename suffix with no directory-name dependence, so `raw_data`/`rawdata` is moot for the census, and the README extraction spec plus the launcher's suffix-based `7z -ir!*` includes (`colab_probe_023.ipynb:113-117`) are likewise directory-agnostic |
| 150th lesion row surfaced and routed through exclusions with a reason | **Resolved** — per-case lesion members are enumerated; the canonical follow-up derivative (`/derivatives/<case>/ses-0*2/<case>_ses-0*2_space-ncct_lesion-msk.nii[.gz]`, `run.py:261-262`) is retained; every non-retained member is recorded with `record_type=excluded_archive_lesion` and an explicit reason in **both** `schema_census.csv` (`run.py:672-680`) and `exclusions.csv` (`run.py:681-684`), and counted in `summary.json` as `excluded_duplicate_lesion_members` (`run.py:845`); duplicates that schema position cannot distinguish and that are not byte-identical stop loudly as exit 5 (`run.py:272-275`) rather than being absorbed |
| Change nothing else | **Resolved** — the full `5faa013..7fbef0e` diff touches only: `discover_cases` → `archive_case_inventory` + `find_archive_selected`, the `load_lesion` signature (exact-archive-path resolution, `run.py:573-586`), the duplicate-row surfacing and the two CSVs' explicit field lists it necessitates (`run.py:738-744`), the `record_type` filter in the pass-two schema lookup (`run.py:805-806`, itself necessary so the prepended duplicate row cannot shadow the analyzed-case row), and the one summary count. Phase S, the approval gate, the split function, all strata/thresholds/gates, the bootstrap, the conjunction, and the stopping rule are byte-unchanged; the contract file is untouched (blob verified) |

## Validation against the real payload (the decisive check this round)

I traced `archive_case_inventory` by hand against the actual 2,983-member
manifest from the attempt-2 bundle:

- **Cohort:** exactly 149 members for each of CBF, CBV, MTT, Tmax; 149
  `raw_data/**/*_ncct.nii.gz`; the three case-id sets (CBF, lesion, NCCT) are
  identical (set difference empty). Zero `sub-strokecase` members; every row
  is rooted at `train/`. The inventory therefore yields 149 ids, passes the
  149/150 census check, and finds one CBF and at least one lesion per case —
  no exit-5 path fires.
- **The 150th lesion row is confirmed and characterized:** `sub-stroke0142`
  carries two lesion members —
  `train/derivatives/sub-stroke0142/ses-02/sub-stroke0142_ses-02_space-ncct_lesion-msk.nii.gz`
  (canonical) and `train/derivatives/sub-stroke0142/ses-02/sub-stroke0142_ses-02_lesion-msk.nii`
  (no `space-ncct` tag, uncompressed). The canonical regex matches exactly the
  first, so it is retained and the noncanonical `.nii` is excluded with the
  recorded reason. This is also contract-faithful independent of the
  directive: `required_inputs` names the **NCCT-space** lesion derivative,
  which the untagged file is not.
- **Extraction consistency:** the launcher's include list is `.nii.gz`-suffix
  only, so the noncanonical `.nii` is never extracted; `find_archive_selected`
  resolves the retained member by its exact archive path (tolerating the
  `train/` root's presence or absence, `run.py:291-302`) and fails loudly on
  zero or multiple matches, so the excluded file's absence on disk is
  immaterial and a double-extracted tree cannot be silently mis-resolved.
- **Split stability:** case ids observed in the payload (`sub-strokeNNNN`,
  already lowercase) are exactly the ids the approved code would have derived
  from extracted filenames had its glob matched, and `split_cases` is
  unchanged — so the frozen hash assignment (100 lowest of 149; 49 reserved,
  within the contract's expected 49-or-50) is identical to the assignment the
  standing approval covered. The revision cannot move any patient across the
  census/reserve boundary.
- **Label-blind ordering preserved:** lesion-member *selection* now happens at
  inventory time, but it reads only member names/sizes/CRCs from the manifest;
  no lesion is *opened* before `split_manifest.csv` is written and hashed
  (`run.py:655-656`), which is what the contract's split policy freezes
  against. Reserved patients' lesion members are named in the manifest (as
  they always were in `archive_manifest.csv`) but never opened.

## Round-3 finding disposition

- **F3 (README NCCT extraction glob matched nothing): resolved** — the line is
  now `{raw_data,rawdata}/**/*_ncct.nii.gz` with the wildcard present, and the
  launcher extracts by suffix rather than by that line, removing the
  load-bearing typo class entirely.
- **F1 (quartile-cut vs measurement mask `mtt > 0` mismatch): carried
  unchanged** (`run.py:546` vs `run.py:559`).
- **F2 (outcome checkpoint rewrite not atomic): carried unchanged**
  (`run.py:815`; the `atomic_npz` tmp+`os.replace` pattern remains available
  one screen up).
- **F4b (permitted nonfinite lesion values outside the analysis region are
  excluded but not counted): carried unchanged** (`run.py:554-556`).
- **F5 (conceptrecid `16731717` lineage not pinned): carried unchanged**
  (`run.py:333-337` still checks only mutability, not identity).
- **F6 (cache-identity exit-4 message does not name the remedy): carried**
  (`run.py:692-693`). No stale-cache risk this rerun: attempt 2 died before
  `phase_c_cache/` was created, and the identity now embeds the new
  `run_py_sha256` anyway.
- **F7 (all-empty identity coordinate reaches `np.concatenate` of an empty
  list → exit 13 instead of a clean 9/10): carried** (`run.py:751`;
  practically unreachable after the mirror gate).
- **N4 (unit gate may stop the run), N6 (axis-aligned mirror, mixed index
  units), N7 (MD5+SHA-256 are two full ~99 GB passes, re-paid per resume),
  N8 (smoke bypasses `gate()`, labeled non-contractual), N9 (bounded pins;
  `environment.txt` is the record): all carried unchanged.**

## Blocking findings

None.

## Non-blocking findings (new this round)

**R1 — The README's duplicate-handling sentence mispredicts the real
payload.** `probes/023/README.md:33-36` says a *byte-identical* duplicate is
resolved lexicographically and "non-identical duplicates stop as a population
failure." That describes only the fallback branch. The payload's actual
duplicate is non-identical yet is resolved — correctly and deterministically —
by the canonical schema-position rule, which the README never mentions. An
operator briefed by this paragraph would expect the coming run to stop. The
code is right; fix the paragraph at the next authorized touch to state the
selection order: canonical follow-up `space-ncct` member first, signature-
identical lexicographic fallback second, loud stop only when neither applies.

**R2 — Inventory lowercases ids; `find_one`'s prefix glob is
case-sensitive.** `archive_case_inventory` normalizes ids with `.lower()`
(`run.py:240`) while `find_one` globs `rglob(f"{case_id}*")` case-sensitively
(`run.py:218`). On a hypothetical mixed-case payload the map lookup would find
zero files and exit 5 loudly — fail-closed, never silent, and the real payload
is all-lowercase — but the asymmetry is worth removing whenever `find_one` is
next touched.

**R3 — Orphan lesion members are a hard stop, not an exclusions row.** A
lesion member whose case id has no CBF member exits 5 (`run.py:285-287`)
rather than being routed through `exclusions.csv`. For an unexplained payload
anomaly this is the correct fail-closed reading of the population clause (the
149/150 count could otherwise be quietly satisfied while data vanishes), and
the real payload has no orphans; recorded so a future release revision that
adds one is not misdiagnosed as a code fault.

**R4 — `verification.json` no longer records the approval-marker binding
check.** The rebuilt verification file attests compile, smoke, the synthetic
149-case + noncanonical-lesion fixture, selection assertions, and extraction
resolution, but the round-2/3 format's "marker matches contract blob" line is
gone. The runtime gate (`run.py:99-122`) enforces the binding regardless, and
I recomputed the blob match this round; purely a builder-telemetry regression.

## Verified correct (spot-checked this round)

- **Approval gate and freeze chain:** contract blob recomputed =
  `349af5ad…` = marker blob; zero placeholder tokens; the three Phase-S-frozen
  thresholds (N=20, M=100, width 0.15) and `simulation_output_sha256` are read
  from the contract, not hardcoded; Phase C still requires `--phase-s-dir` and
  verifies the simulation hash before any record/archive/image access
  (`run.py:370-380`, `641`); the no-`test` path guard survives on data,
  archive, and record paths (`run.py:638-639`) — the removal of the old
  duplicate guard inside `discover_cases` loses nothing.
- **CSV integrity of the mixed-row files:** both audit CSVs now write explicit
  field lists; analyzed-case rows gain `record_type`/`reason` via
  `setdefault`, duplicate rows carry empty per-case counts via `DictWriter`
  restval; no key set exceeds the declared fields, so no `ValueError` path.
  `schema_census.csv` is written before the mirror gate can exit and rewritten
  with lesion paths after pass two, duplicate rows preserved in both writes
  (`run.py:745`, `816`).
- **Resume semantics:** cached audit JSONs lack `record_type` by construction
  and regain it via `setdefault` on reload (`run.py:723-729`); checkpoint
  identity binds contract blob, archive SHA-256, split SHA-256, and the new
  `run.py` SHA-256, so nothing written by the superseded code can be honored.
- **Analysis discipline unchanged:** equal patient weight, single
  `default_rng(20260824)` stream, 2000-resample patient bootstrap,
  direction-aware three-stratum conjunction, support shortfall exits 10
  (invalidating, never a negative), CI-width failure classified as
  `negative_pattern`, one variant, one seed, zero GPU, no pooled fallback;
  statuses remain exactly `POSITIVE_PATTERN`/`NEGATIVE_PATTERN` and the
  closing interpretation still forbids physiological and model-use language.
- **Standards checklist:** (1) start/end manifests present and agreeing
  (`resolved_config.json` echoes the frozen thresholds and contract blob;
  `summary.json` echoes blob, split and simulation hashes, archive digests);
  (2) exclusions log with reasons — strengthened this round; (3) transform
  assertions unchanged (split disjointness, grid/finiteness/unit/mirror/
  identity gates); (4) seed and paths declared, no analysis-time network;
  (5) split manifest hashed before any lesion is opened; (6) `--smoke` is
  synthetic-only, seconds-scale, and reports `contract_satisfied: false` with
  a non-contractual label. Execution checks (py_compile, smoke, the seeded
  149-case duplicate fixture) are attested by `verification.json`, whose
  artifact hashes match the reviewed files; this environment cannot execute
  Python, so those attestations plus static tracing are the basis here, as in
  round 3.

## Verdict

The revision implements the exit-5 directive exactly and stays inside it: the
cohort is now derived from the verified archive member manifest with the
mandated spelling tolerance, the 150th lesion row — confirmed against the real
manifest as a noncanonical untagged `.nii` duplicate for `sub-stroke0142` — is
named in both audit files and excluded with a reason rather than absorbed, and
nothing scientific moved: same contract blob, same split assignment on the
observed ids, same gates, thresholds, and analysis. Traced end-to-end against
the actual 2,983-member payload manifest, Phase C now clears the census that
killed attempt 2 and proceeds to the map pass with no new silent-failure
surface. The four new findings are documentation and telemetry polish; none
changes what the census measures.

```json
{"verdict": "APPROVE", "blocking": [], "note": "Exit-5 directive implemented exactly and validated against the real 2983-member archive manifest (149 cases; sub-stroke0142's noncanonical .nii duplicate excluded with reason in both audit files); contract blob and split untouched, standing approval remains bound; four non-blocking polish findings."}
```
