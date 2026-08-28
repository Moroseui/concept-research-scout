# Probe code review — idea 023, round 9 (re-review of the HU tissue-audit revision after the round-8 blocking fixes)

**Reviewed artifacts:** `probes/023/run.py` (SHA-256
`ff237ea7af332554daed8cd295204084a2b4a9394761b66f78dd1bd5f3a5bf23`),
`probes/023/README.md` (SHA-256 `e5a02810…`), `probes/023/requirements.txt`
(SHA-256 `ff705c03…`, byte-identical since round 2), and
`ideas/023/probe_contract.yaml` (git blob
`0e223c82f9eb879652a549df9bf857c155ef61db`, byte-identical to the round-7
amended contract and to the blob round 8 reviewed). All hashes recomputed
this round and matching `probes/023/verification.json`.

**Hash lineage (verified):** approved run.py `80af2c87…` is byte-identical
at the approval commit (`68057ec`) and at the revision parent (`8df3a95`);
the round-8-reviewed HU-audit code is `ecb2e0f9…` (commit `4403d4c`); the
present artifact is `ff237ea7…` (commit `0e840d0`). The `9e843c7..0e840d0`
probe delta is 13 lines in run.py (one hunk, inside `tissue_audit`),
18 lines in README.md, and the verification.json refresh — nothing else.
The complete delta from the approved artifacts is therefore the round-8
audited 63-line HU-audit diff plus this bounded two-finding fix.

**Approval state (verified):** `ideas/023/HUMAN_APPROVED_PROBE` binds blob
`0e223c82…` and the contract is still blob `0e223c82…` — the standing
approval **remains valid**, per the 2026-08-28 activation ("contract
untouched; standing approval holds through verify"). Fail-closed sequencing
is unchanged: the Phase-S placeholders still block Phase C, the pending
mechanical amendment will stale this approval by construction, and the
Phase-C checkpoint identity includes the run.py hash (run.py:768), so
nothing checkpointed under either superseded code revision can be consumed
by this one (exit 4 at run.py:771-772).

**Requirements conformance (review rule 5):**
`ideas/023/contract_requirements.md` does not exist (verified this round);
not a requirements-governed contract. Not applicable.

**Review basis:** as in rounds 3–8, this review environment cannot execute
Python; executed-check attestations in verification.json (py_compile, smoke
0.303 s with `contract_satisfied: false`, and the four fixtures including
the new `empty_flow_band_tissue_audit_fixture`) plus line-level static
tracing are the basis.

---

## Disposition of the round-8 blocking findings

**B1 (empty flow band crashed the take as exit 13) — RESOLVED, verified
against every interacting invariant.** The fix is exactly the prescribed
shape. `tissue_audit` now branches on `z.size` (run.py:567-576): a
non-empty band keeps the original finite-cut assert and style selections;
an empty band asserts the cuts are NaN and emits both style rows with
empty selections, which flow into the existing empty-support branch
(run.py:591-596) as `member_voxels: 0` with blank HU statistics. Checked
against the code it must agree with:

- **The NaN asserts are internal-consistency checks, not a new gate.** The
  sole `tissue_audit` call site (run.py:811) passes quartiles computed at
  run.py:804-810, which are NaN exactly when a band is empty and
  `np.quantile` of the band's finite log-CBV otherwise — so neither branch
  assert can fire on contract-valid input. Region construction guarantees
  finite positive CBV/CBF/MTT in every band member (run.py:512, 520-522),
  so a non-empty band always yields finite ordered cuts.
- **Empty bands genuinely occur on valid input**, confirming the finding
  was real: `flow_band_labels` leaves band 3 empty for a two-voxel region
  and bands 2-3 empty for one voxel (run.py:535-538), and a fully
  eroded-away region produces three empty bands while still flowing
  through `coordinate_arrays`, `patient_native_z`, and the census
  aggregation (the all-patients-empty case still fails loudly at
  run.py:850-851).
- **All three row-count invariants survive:** `assert len(rows) == 6`
  (run.py:599), the resume-path assert (run.py:784), and the CSV
  reconciliation `6 × analyzed cases` (run.py:846).
- **Symmetry with the estimator's tolerance is restored:**
  `patient_measure` skips `z.size < 4` cells before touching the cached
  cuts (run.py:613-615), so NaN cuts are never read anywhere, and the
  frozen support gates — not a crash — now decide the small-deficit
  patient in both the audit and the estimator. The row's
  finite/nonfinite/member accounting assert holds trivially (0+0=0,
  run.py:597).

**B2 (README extraction set omitted the NCCT the code requires) —
RESOLVED.** `README.md:28` adds `{raw_data,rawdata}/**/*_ncct.nii.gz` to
the mandated extraction set, tolerating both payload spellings in the same
declaration style as the existing derivative globs, and `README.md:40-41`
now states "Rawdata NCCT is used only for the label-blind per-bin
tissue-composition audit; raw 4D CTP and CTA are not used" — matching
run.py:454 (NCCT hard-required per census case) and run.py:452-453 (the
diagnostic-only framing). `find_one` resolves by recursive glob with exact
filename suffix (run.py:255, 259-260), so it is directory-spelling
agnostic and fails loudly (exit 5) on zero or multiple matches; the NCCT
stream passes through `verify_required_gzip` with every other required
member (run.py:459-460). The take-13 launcher regenerated from this
declaration at package-colab will now extract what the code needs (R15).

**R12 (README duplicate-lesion sentence mispredicted the payload) —
RESOLVED in the same authorized touch, as round 8 requested.** The new
sentence (README.md:33-38) now states the code's actual policy and matches
`archive_case_inventory` clause for clause: the unique canonical follow-up
`ses-02` derivative is preferred (run.py:302-307), deterministic
lexicographic selection is permitted only when all candidates share
identical archive size and CRC (run.py:311-317), anything else stops as a
population failure (exit 5, run.py:315-316), and every non-retained member
is named in both `schema_census.csv` and `exclusions.csv`
(run.py:319-324, 749-761) with the count surfaced in `summary.json`
(run.py:962). Pass two loads the lesion by its exact selected archive path
(`find_archive_selected`, run.py:634), so the additionally extracted
duplicate member cannot trip a `find_one` multiplicity failure.

## Delta audit (nothing beyond the fixes)

The single run.py hunk touches only `tissue_audit`'s selection logic.
`patient_measure`, the bootstrap, the three-band conjunction, all gates,
Phase S, the split machinery, checkpoint identity, and the exit taxonomy
are byte-identical to the round-8-reviewed code, which was itself verified
against the approved baseline. The closing summary and interpretation
templates are unchanged (run.py:957-966, 1004-1010): status is reported
only as the contract's POSITIVE_PATTERN/NEGATIVE_PATTERN language, and no
HU-balance judgment is made — the pre-registered balanced/imbalanced rule
stays with the interpret stage. requirements.txt is byte-identical; no new
dependency, RNG, or network access enters. verification.json was refreshed
in the same commit with matching hashes and a new attested fixture for the
empty-band path ("six rows with zero members and blank HU statistics"),
which agrees with the static trace above.

## Standards checklist

(1) Start/end determinism manifests present and asserted equal in both
phases (run.py:242-244, 968-970). (2) Exclusions log with reasons:
unchanged, plus the duplicate-lesion and source-corrupt rows in both audit
CSVs. (3) Assertion per transform: the fix replaces the one wrong-in-kind
assert with branch-appropriate internal-consistency asserts; shape,
band-size, quantile-ordering, and voxel-accounting asserts all retained.
(4) Seeds and paths declared; no hidden state or analysis-time network.
(5) Split manifest hashed before any outcome/label access; the audit runs
entirely in the label-blind pass one. (6) `--smoke` synthetic-only,
attested 0.303 s, `contract_satisfied: false`, and cannot reach Phase C or
the audit. All six met.

## Carried non-blocking findings

- **N1 (contract text still declares NCCT outside the probe):** carries to
  the mechanical Phase-S amendment — the operator decides there whether
  the amendment absorbs a sentence naming the rawdata NCCT as an
  audit-only diagnostic input and whether `bin_tissue_audit.csv` joins
  `required_outputs`. Nothing in this round changes that analysis.
- **N2 (missing/unreadable NCCT exit-class labels are latent
  misclassifications):** carries unchanged; fail-loud remains the
  conservative default and both classes remain latent per the archive
  manifest and the two integrity sweeps.
- **N3 (audit rows inherit R16's degenerate-quartile overlap semantics):**
  carries. The README touch was correctly scoped to B2+R12 and did not add
  the R16/N3 sentence; when the README next gains it, extend one clause to
  the audit rows so the interpret stage does not rediscover the overlap.
- **R13 (dead `load_label=True` branch of `load_case`, run.py:455-456):**
  hygiene carry; sole call site still passes False.
- **R14 (nonpositive-map voxel exclusions uncounted in the exclusions
  record):** carries unchanged.
- **R15 (launcher is the Phase-S-era artifact):** `colab_probe_023.ipynb`
  is untouched since `aadb44e`, as expected; the take-13 Phase-C launcher
  must be regenerated at package-colab from the now-corrected README
  declaration, NCCT glob included.
- **R17/N4 (cosmetics):** carry; `resolved_config.json` still reports
  `"label_blind_ncct_tissue_audit": true` in phases where no audit runs
  (run.py:992).

## Verdict

Both round-8 blocking findings are fixed exactly as specified and nothing
else moved: the empty-band guard makes the audit tolerate the same input
class the estimator already tolerates while preserving every row-count
invariant, the README's extraction set and input declarations now match
the code (closing the launcher-omission class that killed Phase-C
attempt 1), and the stale duplicate-lesion sentence was corrected against
the actual selection logic in the same touch. The contract blob is
untouched, the standing approval remains validly bound, the estimator,
gates, and claim language are byte-identical to the approved-plus-audited
baseline, and the delta from the approved code is fully accounted for.
The code is ready for the next sequence step: the mechanical amend-contract
from the mirror-free Phase-S bundle (where N1 is queued for the operator),
fresh approval against the new blob, and package-colab regeneration of the
take-13 launcher.

```json
{"verdict": "APPROVE", "blocking": [], "note": "Round-8 B1 (empty-band assert crash) and B2 (README extraction set omitting the required NCCT) plus carried R12 are fixed exactly as prescribed with a 13-line run.py hunk and a scoped README touch; estimator, gates, contract blob, and approval binding all verified unchanged — clear for the mechanical Phase-S amendment, fresh approval, and take-13 packaging."}
```
