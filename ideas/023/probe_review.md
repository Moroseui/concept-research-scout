# Probe code review — idea 023, round 7 (first review of the mirror-free redesign, per the 2026-08-27 operator decision)

**Reviewed artifacts:** `probes/023/run.py` (SHA-256
`80af2c8713df8c0598088cb8b3f061996c7a99362994a0fa43bf976df7efe188`),
`probes/023/requirements.txt` (SHA-256 `ff705c03…`, byte-identical to every
file since round 2), `probes/023/README.md` (SHA-256 `d622d8a6…`, rewritten
this round), and the **amended** `ideas/023/probe_contract.yaml` (git blob
`0e223c82f9eb879652a549df9bf857c155ef61db`, file SHA-256 `0e3d8589…`). All
four hashes recomputed this round and matching `probes/023/verification.json`.
Prior approved code: run.py SHA-256 `acae802f…`, contract blob `2963f66b…`,
both verified at commit `3328834` (the parent of the revision commit
`ac63601`), so the `3328834..ac63601` diff reviewed here is the complete
delta from the last approved artifacts. The launcher notebook and
requirements.txt are untouched in `ac63601` (verified by diff stat). Review
rounds 1–6 preserved in git.

**Approval state (deliberate, verified):** `ideas/023/HUMAN_APPROVED_PROBE`
binds blob `2963f66b…` (the take-11-era approval); the contract is now blob
`0e223c82…`. The standing approval is therefore **stale by design**: the
mirror-free amendment changes the blob, and the runtime gate
(`run.py:116-139`) compares marker blob against live contract blob for
**every** phase, so both Phase S (which must be re-run — recalibration) and
Phase C refuse with exit 2 until a fresh marker is bound. `verification.json`
attests the builder exercised exactly this refusal. This APPROVE is a
recommendation on the code; the human gate on the amended contract remains
controlling.

**Scope note.** This is a redesign round, not a change-nothing-else patch
round. The 2026-08-27 decision entry ("Operator reframe AND DECISION: 023
goes mirror-free; directive for the amendment round") authorizes: matched
flow = per-patient CBF percentile bands (0–33 / 33–67 / 67–100) within the
eroded deficit region; complete removal of mirror construction, registration
QC, the exit-7 gate, and mirror-relative ratios; region definition, identity
coordinate u = log(CBF·MTT/CBV), identity-residual gate, per-stratum
coverage floors, and source-corrupt exclusion policy unchanged; Phase-S
recalibration under percentile binning; gates minimal (coverage + identity
only); no new reference anatomy. This review verifies the contract amendment
and the code implement exactly that directive and nothing else.

**Requirements conformance (review rule 5):** `ideas/023/contract_requirements.md`
does not exist (verified this round); not a requirements-governed contract.
Not applicable.

---

## Disposition of the directive requirements

| Directive item | Status |
|---|---|
| Matched flow = three fixed within-patient CBF percentile bands, deterministic, label-blind, no external reference | **Resolved** — `flow_band_labels` (`run.py:522-538`) ranks finite positive CBF inside the final eroded region with a stable mergesort (equal-CBF ties resolve by original voxel index, exactly the contract's tie rule) and assigns bands by integer rank arithmetic (`positions*100 < size*33`, etc.), avoiding float boundary ambiguity. Asserts: band count equals region count; no labels outside the region. The builder's tie fixture (`[1,1,2,2,2,3]` for six voxels) checks by hand |
| Q1 vs Q4 = that patient's own label-blind CBV quartiles | **Resolved** — per-patient, per-band `np.quantile(z, [0.25, 0.75])` cuts are computed in the outcome-blind pass one and checkpointed in the case npz (`run.py:750-762`) before any lesion is opened; pass two reads them from the checkpoint (`run.py:566-569`) with a finiteness/order assert. The census-wide pooled cuts of the mirror era are gone, matching the amended `analysis.native_quantiles` |
| Mirror machinery removed entirely | **Resolved** — `mirror_qc`, `neighborhood_median`, `reflect_index`, the exit-7 gate, `mirror_rows`/`mirror_qc.csv`, rCBF/rCBV ratio construction, and NCCT loading are all deleted (verified in the full diff; grep of the final file finds no mirror/rcbf/rcbv symbol). Exit code 7 is retired-and-reserved in the docstring, not reused. The contract deletes `brain_and_mirror_gate`, `relative_measures`, the mirror invalidating-failure clause, and the `mirror_qc.csv` output |
| Region definition unchanged (Tmax>6 s, one-voxel erosion, midline band, per-patient p98 vessel exclusion) | **Resolved with one authorized operationalization change** — Tmax>6.0, six-neighbor erosion with boundary zeroing, and the strict-above per-patient CBV p98 exclusion are byte-equivalent in logic to the approved round-6 code. The two-voxel midline exclusion now uses the **array** midline (`run.py:504-507`) rather than the mirror-estimated midsagittal plane, which no longer exists; the contract amendment states this explicitly ("array midline … an unchanged region-boundary safeguard, not reference anatomy"). I concur this is the minimal faithful operationalization: the estimated plane was mirror machinery, and an array coordinate after `as_closest_canonical` (axis 0 = left-right) introduces no reference anatomy, satisfying the directive's constraint |
| Identity coordinate and identity-residual gate unchanged | **Resolved** — u = log(MTT) − log(CBV) + log(CBF), centered once on the census-wide voxel median, per-band median absolute residual gated at 0.10 **before** any lesion access (`run.py:786-805`), with the full residual distribution persisted to `identity_residual_summary.csv` and the SVG before the invalidating exit — the stop-report lesson preserved |
| Coverage/support floors unchanged | **Resolved** — per-stratum native-support check (exit 10 on empty), Phase-S-frozen minimum contributing patients (exit 10 at `run.py:876`, invalidating, never a negative), minimum Q1/Q4 voxel cells read from the contract at runtime, never hardcoded |
| Source-corrupt exclusion policy unchanged | **Resolved** — the one-member `SOURCE_CORRUPT_MEMBERS` tuple, full-stream `verify_required_gzip`, fail-loud exit 6 for any other unreadable member, exclusion routing to `schema_census.csv` + `exclusions.csv` with the exact path, map-pass continuation, and the `excluded_source_corrupt_cases` / `analyzed_census_case_count` summary keys are all carried byte-equivalent in behavior |
| Phase S recalibrated for the new strata | **Resolved** — the contract's Phase-S placeholders are restored (`TO_BE_RECORDED_AFTER_PHASE_S`), forcing a fresh calibration run and a fresh amendment before Phase C; the simulation grid, beta-binomial generator, lexicographic selection rule (smallest N, then M, then **largest** width — `run.py:230` matches), and the exact Phase-C conjunction/bootstrap are unchanged. The old mirror-era selection (N=20/M=100/0.15) and its hash are correctly evicted from the contract |
| Gates minimal; no new reference anatomy | **Resolved** — Phase-C validity gates are now exactly: provenance/checksum, population census, grid/finiteness, identity residual, support, plus the carried checkpoint-identity and placeholder gates. Nothing new was added; NCCT is no longer read at all |
| De-coupling from idea 021 by construction | **Resolved** — no contralateral or hemispheric quantity appears anywhere in the analysis path; the only left-right-adjacent construct is the array-midline exclusion band, which removes voxels rather than measuring anything |

## Contract-fidelity verification (this round's decisive checks)

- **Primary metric.** Per band: d = risk(Q1 low-CBV) − risk(Q4 high-CBV) per
  patient (`run.py:570-573`), equal-patient-weight mean (`run.py:880`),
  2000-resample patient bootstrap percentile 95% CI from
  `default_rng(20260824)` — the contract's metric, sign convention (positive
  d = lower joint-state position more infarcted), seed, and replicate count
  exactly.
- **Pass rule.** Three-band conjunction: common nonzero sign, at least two
  CIs excluding zero **in the common direction** (the direction-aware
  exclusion at `run.py:885` matches the Phase-S rule at `run.py:184`), all
  widths ≤ the frozen maximum. Sign 0 fails. No pooled fallback or alternate
  threshold exists anywhere.
- **Phase-S/Phase-C estimator identity.** `simulated_conjunction` applies
  the same equal-weight mean, same bootstrap shape, same percentile CI, and
  same conjunction as the real census; the per-patient-cell abstraction of
  the simulation (one latent risk per patient, M voxels per cell) now maps
  onto the per-patient quartile design even more directly than it did onto
  the census-wide cuts it originally calibrated.
- **Label blindness and ordering.** Split manifest written and hashed
  (`run.py:660-661`) before any image is opened; pass one opens maps only
  (`load_label=False`); per-patient cuts, bands, region, and identity values
  are checkpointed before pass two; the identity and support gates fire
  between the passes; lesions are first touched at `run.py:837`. The
  archive-member listing read earlier is metadata (names/sizes/CRCs), not
  image content.
- **Population authority.** Case discovery from the archive member manifest
  (`archive_case_inventory`), tolerant of `sub-stroke`/`sub-strokecase` and
  `raw_data`/`rawdata`, 149-or-150 gate, exactly-one-CBF-per-case gate,
  orphan-lesion fail. The 150th lesion row is resolved by the canonical
  ses-2 schema-position rule and surfaced in both audit CSVs with reason —
  never silently absorbed. `load_lesion` loads the archive-selected member
  by exact path (`find_archive_selected`), so an extracted duplicate cannot
  be picked up by glob accident.
- **Provenance.** Immutable-child-record check (refuses a concept record),
  Zenodo-supplied MD5 verified against the held archive, downloaded SHA-256
  and member manifest recorded, Phase-S output hash verified against the
  amended contract before any data access, `--phase-s-dir` required (the
  take-1 regression), "test" path guard, checkpoint identity bound to
  contract blob + archive SHA + split SHA + run.py SHA (exit 4 on mismatch),
  and `units_documented: false` with the payload evidence carried into
  `identity.json`.
- **Caps and stopping.** No GPU path exists (numpy/nibabel/scipy/py7zr
  only); one variant, one seed constant everywhere; Phase S ends in
  `PHASE_S_COMPLETE_REQUIRES_AMENDMENT` with an explicit stop instruction;
  Phase C stops on invalidating failures with the documented exit taxonomy;
  retired codes 7 and 8 are reserved, not reused.
- **Required outputs.** All fifteen contract outputs are produced across the
  two phases; `per_patient.csv` is the per-sample file; the two SVGs
  implement the contract's label-blind support and residual-distribution
  plots from the same frozen CSV quantiles. `summary.json` statuses are
  exactly `POSITIVE_PATTERN`/`NEGATIVE_PATTERN` plus the non-claim statuses,
  and the closing interpretation template forbids physiological and
  model-use claims.
- **Resume soundness.** The excluded case can never acquire a checkpoint, so
  its exclusion re-derives identically on every run; audit JSONs are the
  single source for schema/exclusion rows on resume and are updated with the
  lesion path after pass two, so resumed runs keep complete audit files;
  per-patient rows round-trip the outcome checkpoint as strings and are
  re-parsed defensively.

## Standards checklist

(1) Start/end determinism manifests: **present in both phases this round**
(`write_determinism_manifest`, asserted equal at end) — this closes the gap
where prior rounds leaned on resolved_config/provenance as implicit
manifests; the manifest carries declared input paths with hashes, counts,
split hash, and seed. (2) Exclusions log with reasons: per-case rows with
reason and source path plus per-case count columns (see R14 for one
uncounted voxel class). (3) Assertion per transform: split
disjointness/cover, erosion-region finiteness/positivity, band-count
equality, quartile order, per-mask finiteness in both passes, manifest
equality. (4) Seeds and paths declared in resolved_config and the
manifests; no analysis-time network access (record JSON and archive are
local files). (5) Split manifest hashed before any outcome/label access
(verified order above). (6) `--smoke`: synthetic-only, tiny grid, bypasses
no scientific logic it could contaminate, reports `contract_satisfied:
false` and status `SMOKE_OK`, cannot select gates (eligibility computation
is skipped in smoke mode) — attested under 60 s by the builder; statically
the workload (one candidate, one scenario, 4 replicates, 20 bootstraps) is
trivially inside the budget. As in rounds 3–6, this review environment
cannot execute Python, so executed-check attestations in
`verification.json` (py_compile, smoke, tie fixture, stale-gate refusal)
plus static tracing are the basis.

## Prior-finding dispositions

- **F1 (quartile-mask asymmetry between the label-blind and outcome
  passes): RESOLVED STRUCTURALLY.** Both passes now consume the identical
  cached `region`/`bands` arrays, and positivity is baked into the region
  itself, so no admission term can differ between cut estimation and
  measurement. The finding is retired.
- **R11 (mirror-gate message hardcoding /100): RETIRED** with the mirror
  gate itself.
- **R1 (README duplicate-handling sentence mispredicts the payload):
  ESCALATED to R12 below** — the README was rewritten this round and the
  stale sentence survived a fourth time.
- **R8 (tightening-excluded voxels uncounted): TRANSFORMED into R14** — the
  finiteness-tightening columns died with the ratio machinery; the successor
  class is the nonpositive-map exclusion, still uncounted.
- **Carried byte-equivalent, none blocking, none interacting with this
  redesign:** F2 (outcome checkpoint rewrite not atomic — a truncated
  checkpoint re-parses loudly or recomputes deterministically), F4b
  (nonfinite lesion values outside the analysis region tolerated but not
  counted), F5 (conceptrecid lineage not pinned to 16731717), F7-class
  (an all-empty stratum would surface as exit 13 rather than a cleaner
  invalidating code; now additionally guarded by the exit-9 empty-u check),
  R2 (lowercase ids vs case-sensitive rglob — fails loudly if ever wrong),
  R3 (orphan-lesion hard stop), R5 (checkpoint-identity exit-4 message does
  not name the blob-scoped-directory remedy), R6 (`units_documented` not
  echoed into `summary.json`), R7 (strict-above p98 tie behavior), R9 (the
  outcome-pass SourceCorruptMember handler is unreachable with a CBF-only
  tuple; deliberate generality, still dead code), R10 (an OSError on exactly
  the preregistered path is attributed to the source defect).

## Blocking findings

None.

## Non-blocking findings (new or escalated this round)

**R12 — README duplicate-lesion sentence still mispredicts the real
payload, and the change-nothing-else defense has expired.** `README.md:32-35`
says a byte-identical duplicate is resolved lexicographically and
"non-identical duplicates stop as a population failure." The code's first
rule (`run.py:300-315`) is the canonical ses-2 schema-position selection,
which resolves the payload's known non-identical 150th lesion row without
stopping; the signature-identity requirement applies only when the
canonical rule does not uniquely resolve. Prior rounds carried this because
the README was frozen; this round the surrounding paragraph was rewritten
and the wrong sentence survived. The human reads this file at the approval
gate, and it predicts a stop that will not happen. Fix at the next
authorized touch — ideally in the amendment commit that records the Phase-S
values, before approval is bound.

**R13 — Dead code left by the mirror removal.** The unused `"ncct"` suffix
entry in `find_one` (`run.py:253`), the never-invoked `load_label=True`
branch of `load_case` (pass two resolves lesions via `load_lesion`
instead), and the now-unused `paths`/`zooms` returns at the pass-one call
site. None is reachable in a way that touches data (`load_case` is called
only with `load_label=False`), so this is hygiene, not scope; remove at the
next authorized touch.

**R14 — Voxels excluded by the region's positivity terms are not counted
per case.** `run.py:508` folds `cbf>0 & cbv>0 & mtt>0` into the analyzed
region (necessary: the contract's log coordinates are undefined otherwise,
and this is the mirror-free descendant of the pre-registered take-11
finiteness tightening), but `exclusions.csv` has no column separating
positivity-excluded voxels from erosion/midline/vessel attrition — only the
deficit-to-eroded aggregate. Per the R8/F4b precedent this is non-blocking,
and the counts remain recoverable from the checkpointed arrays, but a
`nonpositive_map_voxels` count column is recommended at the next authorized
touch so the interpret stage can gauge materiality without reopening npz
files.

**R15 — The committed launcher notebook is the take-12 mirror-era
artifact.** `colab_probe_023.ipynb` pins contract blob `2963f66b…`, extracts
the rawdata NCCT (no longer required), and points at mirror-era output
directories. Every protection holds if it were run unmodified (its own pin
check and run.py's gate both refuse), so this is fail-closed, but the
package-colab stage must regenerate the launcher — including a Phase-S
launch path, since Phase S must be re-run — after the human binds approval
to blob `0e223c82…`. Out of this review's artifact scope; recorded so the
sequencing is on the record.

**R16 — Degenerate per-patient quartiles overlap Q1 and Q4.** With
per-patient cuts, a band whose z values are nearly constant yields q1 == q3,
making `z <= q1` and `z >= q3` overlapping (possibly identical) sets; d for
that cell is then pulled toward zero rather than being undefined. This is
deterministic, label-blind, and conservative (it dilutes rather than
fabricates a contrast), and the min-voxel cell gates make it unlikely to
matter, but the behavior is worth one sentence in the README's matched-flow
paragraph so the interpret stage does not rediscover it. Note only.

**R17 — Cosmetic:** `run.py:728` opens a resume npz without a context
manager (the pass-two site uses `with`); `per_stratum_summary.csv` is
written with an inline writer rather than `write_csv`. No behavioral
consequence.

## Verdict

The mirror-free directive is implemented exactly: the contract amendment
replaces mirror-referenced matched flow with within-patient percentile
bands and strips every mirror clause, output, and failure mode; run.py
deletes the entire mirror apparatus, implements deterministic stable-tie
percentile banding and per-patient label-blind CBV quartiles checkpointed
before any lesion access, and carries the region rule, identity gate,
support floors, source-corrupt policy, provenance chain, and resume
machinery unchanged in behavior. Phase-S placeholders are restored so the
detectability floor is recalibrated for the new strata before Phase C can
be approved. Determinism manifests are now explicit at start and end of
both phases. No blocking findings; six non-blocking findings are recorded,
one escalated (the README duplicate sentence, whose freeze defense has
expired). The standing approval is stale by construction and the runtime
gate enforces it for both phases: nothing can run until the human reviews
the amendment diff and binds a fresh approval to contract blob
`0e223c82f9eb879652a549df9bf857c155ef61db`.

```json
{"verdict": "APPROVE", "blocking": [], "note": "Mirror-free redesign implemented exactly per the 2026-08-27 directive (percentile-band matched flow, per-patient label-blind quartiles, mirror machinery fully removed, Phase-S recalibration forced by restored placeholders); approval stale by design pending fresh human binding to contract blob 0e223c82; six non-blocking findings, README duplicate sentence escalated."}
```
