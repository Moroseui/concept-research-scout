# Probe code review — idea 023, round 8 (first review of the HU tissue-audit revision, per the 2026-08-28 activation)

**Reviewed artifacts:** `probes/023/run.py` (SHA-256
`ecb2e0f94af834c9c64149e0163b8f62133d5b3e53b0c968205500a0f3bc9792`),
`probes/023/requirements.txt` (SHA-256 `ff705c03…`, byte-identical since
round 2), `probes/023/README.md` (SHA-256 `d622d8a6…`, **unchanged from
round 7 — see B2**), and `ideas/023/probe_contract.yaml` (git blob
`0e223c82f9eb879652a549df9bf857c155ef61db`, **byte-identical to the round-7
amended contract**). All hashes recomputed this round and matching
`probes/023/verification.json`. Prior approved code: run.py SHA-256
`80af2c87…`, verified identical at both the approval commit (`68057ec`) and
the parent of this revision (`8df3a95`), so the `8df3a95..4403d4c` diff
(63 lines in run.py, plus verification.json) is the complete delta from the
approved artifacts. Review rounds 1–7 preserved in git.

**Approval state (verified):** `ideas/023/HUMAN_APPROVED_PROBE` binds blob
`0e223c82…` and the contract is still blob `0e223c82…` — the standing
approval **remains valid**, exactly as the 2026-08-28 directive intends
("contract untouched; standing approval holds through verify"). Fail-closed
sequencing is preserved despite the live approval: the contract's Phase-S
placeholders (`TO_BE_RECORDED_AFTER_PHASE_S`, restored at round 7) still
block Phase C, the pending mechanical amendment that records the mirror-free
Phase-S values will change the blob and stale this approval by construction,
and the Phase-C checkpoint identity includes the run.py hash (run.py:759),
so nothing written by the superseded code can be consumed by this code
(exit 4 at run.py:762-763).

**Scope note.** The governing directive is the 2026-08-28 decision entry
("Meeting outcome: dual-track sprint; HU audit ACTIVATED"): before take 13,
a probe revision adds a **label-blind per-bin per-style NCCT HU audit** —
during the map pass, per case, per flow bin, per style group, the median
and IQR of NCCT attenuation over member voxels, into the per-case cache and
a `bin_tissue_audit.csv`; **no estimator changes, no new gates, run.py only
(contract untouched)**. This review verifies the code implements exactly
that and nothing else. Note the deliberate tension the directive creates:
the approval-bound contract's `required_inputs` still says "NCCT is no
longer required … Raw 4D CTP, NCCT, CTA … are outside this probe." The
operator directive overrides for this audit; the contract text is not
updated by design. See N1 for the recommended amendment-time harmonization.

**Requirements conformance (review rule 5):**
`ideas/023/contract_requirements.md` does not exist (verified this round);
not a requirements-governed contract. Not applicable.

---

## Disposition of the directive requirements

| Directive item | Status |
|---|---|
| Label-blind NCCT HU audit during the map pass | **Resolved** — NCCT is loaded in pass one only (`load_case`, run.py:454), before any lesion is opened; `tissue_audit` (run.py:557-591) consumes the same cached `region`/`bands`/quartile cuts the estimator uses and touches no outcome data. NCCT is acquisition-phase input, not a label, so label-blindness is preserved by construction |
| Per case, per flow bin, per style group: median and IQR over member voxels | **Resolved** — six rows per analyzed case (3 bands × {Q1_low_CBV, Q4_high_CBV}), each with `median_hu`, `q25_hu`, `q75_hu`, `iqr_hu`, plus member/finite/nonfinite voxel accounting with a consistency assert (run.py:588). "Style group" is implemented as the two CBV-quartile groups the estimator itself contrasts — the correct reading, since the audit exists to check whether Q1 and Q4 cells differ in tissue composition |
| Into the per-case cache and `bin_tissue_audit.csv` | **Resolved** — rows are serialized into the checkpoint npz (`tissue_audit_json`, run.py:807, JSON with sorted keys) and re-read on resume with a row-count assert (run.py:774-775); the CSV is written after the map pass (run.py:838) and **before** the identity-residual gate, so the label-blind audit evidence persists even if a later gate invalidates the run — the stop-report lesson carried correctly |
| No estimator changes | **Resolved** — the diff is confined to the docstring, `load_case`'s path dict, `tissue_audit` and its call/caching, the CSV/summary bookkeeping, and one resolved_config flag. `patient_measure`, the bootstrap, the conjunction, all gates, Phase S, and the split machinery are byte-identical. `arrays["ncct"]` is consumed at exactly one site (run.py:803); no gate or estimator reads it |
| No new gates | **Violated in one unintended way** — no pass/fail rule consumes HU values (nonfinite HU is counted and tolerated, run.py:582-587; empty HU support yields blank fields, "this audit creates no new gate"), but the unconditional quartile-finiteness assert creates a de facto crash-gate on empty flow bands. This is blocking finding **B1** |
| run.py only; contract untouched | **Resolved for the contract** (blob identical; approval marker still binds it). **The README was left untouched and is now wrong about the extraction set** — blocking finding **B2** |

## Contract-fidelity verification

- **Primary metric, caps, stopping rule, seeds:** untouched. One variant,
  one seed (20260824), zero GPU; Phase-C stopping and exit taxonomy
  unchanged; the audit adds no RNG (np.percentile is deterministic) and no
  network access.
- **Grid handling for NCCT:** `load_case` resamples every non-label image
  to the CBF reference grid by the contract's frozen linear rule
  (run.py:466-475), NCCT included, and records the resampling in
  `schema_census.csv`. The rawdata NCCT defines the space the derivatives
  are registered to, so this is a header-tolerance measure, not new
  reference anatomy; `tissue_audit`'s shape assert (run.py:559) is
  therefore unreachable-by-mismatch. The per-case `files` JSON in the
  schema census now records the NCCT path automatically (run.py:478).
- **Label blindness and ordering:** split manifest still frozen and hashed
  before any image opens; pass one opens maps + NCCT only
  (`load_label=False`, sole call site run.py:780); lesions are first
  touched in pass two. The audit is computed and checkpointed inside pass
  one.
- **Outputs:** all fifteen contract-required outputs unchanged;
  `bin_tissue_audit.csv` is an additional, contract-undeclared output, and
  `summary.json` gains only row-count/filename bookkeeping keys
  (run.py:955-956). The closing interpretation template is unchanged and
  makes no HU-balance judgment — correct: the pre-registered
  balanced/imbalanced interpretation rule belongs to the interpret stage,
  not this code.
- **Source-corrupt policy:** unchanged; the excluded case never reaches
  `tissue_audit`, and the row-count reconciliation assert
  (`6 × analyzed cases`, run.py:837) accounts for it.
- **Resume soundness:** checkpoints written by the superseded run.py lack
  the `tissue_audit_json` key but can never be read — the cache-identity
  gate keys on the run.py hash and exits 4 first. Within-take resume
  round-trips the audit rows (fixture attested in verification.json).

## Standards checklist

(1) Start/end determinism manifests: present in both phases, asserted
equal; the audit adds no nondeterminism. (2) Exclusions log with reasons:
unchanged; the audit rows carry their own finite/nonfinite HU accounting.
(3) Assertion per transform: tissue_audit asserts shape, band-size
consistency, quantile ordering, and voxel accounting — one assert is wrong
in kind rather than missing (B1). (4) Seeds and paths declared; no hidden
state or analysis-time network. (5) Split manifest hashed before any
outcome/label access (NCCT is not an outcome). (6) `--smoke`:
synthetic-only, never reaches Phase C or the audit, attested 0.288 s with
`contract_satisfied: false`; the new `tissue_audit_fixture` and
`cache_round_trip_fixture` are attested in verification.json. As in rounds
3–7, this review environment cannot execute Python; executed-check
attestations plus static tracing are the basis. All six items met — B1 is
a rule-2 finding, not a checklist failure.

## Prior-finding dispositions

- **R13 (dead `"ncct"` suffix entry in `find_one`): partially retired** —
  the entry is now live, load-bearing code. The `load_label=True` branch of
  `load_case` remains dead (sole call site passes False; pass two uses
  `load_lesion`); hygiene carry.
- **R12 (README duplicate-lesion sentence mispredicts the payload):
  CARRIED, still unfixed, fourth consecutive round** — and now joined in
  the same file by B2. Fix both in the same authorized touch.
- **R14 (nonpositive-map voxel exclusions uncounted), R15 (launcher is the
  take-12 mirror-era artifact — regeneration at package-colab must now
  ALSO extract the rawdata NCCT, see B2), R16 (degenerate per-patient
  quartiles overlap Q1/Q4 — the audit rows inherit exactly this overlap
  semantics, see N3), R17 (cosmetics), F2/F4b/F5/F7-class, R2/R3/R5/R6/R7/
  R9/R10:** carried unchanged, none blocking, none newly interacting with
  this revision except as noted.

## Blocking findings

**B1 — An empty flow band crashes the take as an unclassified harness
fault (rule 2; also violates the directive's "no new gates").** The map
pass sets a band's quartile cuts to NaN when that band has zero voxels
(run.py:796-799), and `tissue_audit` then asserts
`np.isfinite(q1) and np.isfinite(q3)` unconditionally for all three bands
of every analyzed case (run.py:567). A census patient whose final eroded
region has ≤ 2 voxels (a small Tmax>6s deficit thinned by the one-voxel
erosion, midline band, vessel p98, and positivity terms — a plausible
mild-stroke presentation that no real-data run of the mirror-free region
rule has yet censused) leaves at least one band empty, so the AssertionError
propagates to the outer handler and dies as exit 13 "unexpected harness
failure" (run.py:1004-1006) mid-map-pass. The pre-existing code
deliberately tolerates exactly this input: `patient_measure` skips
`z.size < 4` cells *before* its own finiteness assert (run.py:604-610),
and the support gates operate on census aggregates, so an empty-band
patient contributes empty cells and the frozen per-stratum minimums decide.
The audit converts that tolerated, contract-valid input into a dead take —
the 023 arc has paid for this failure class twelve times. Required shape of
the fix (not prescribed as code): guard the audit the way `patient_measure`
guards, emitting the six rows with zero `member_voxels` and blank
statistics for an empty or NaN-cut band, preserving the six-row invariant
that the cache and CSV asserts (run.py:590, 775, 837) rely on.

**B2 — The README's mandated extraction set contradicts the code's
required inputs and would kill take 13 at the first case (rule 6; standing
clause ruling of 2026-08-24 that the probe README state the exact
extraction set).** `README.md:24-26` instructs extraction of the perfusion
maps and lesion masks only, and `README.md:37` states "Rawdata NCCT, raw 4D
CTP, and CTA are not used." Both statements are now false: run.py:454
hard-requires the NCCT for every census case, and `find_one` exits 5 on a
data-dir extracted per the README. The take-13 launcher is regenerated at
package-colab from the probe's declared dependencies — the mechanism
adopted after Phase-C attempt 1 died to exactly this omission class — and
this README section is that declaration. The "run.py only" clause of the
directive delimits scientific scope (estimator, gates, contract), not
documentation accuracy; verification.json was correctly updated in the
same commit, and the README's input declaration must follow the code the
same way. Fix: update the extraction set to include
`raw_data/**/*_ncct.nii.gz` (tolerating the payload's `raw_data`/`rawdata`
spellings, as run.py already does) and rewrite the "not used" sentence to
name the NCCT as a label-blind audit-only input; fix R12's duplicate-lesion
sentence in the same touch.

## Non-blocking findings

**N1 — Contract text still declares NCCT outside the probe; harmonize at
the amendment.** The approval-bound contract's `required_inputs` says NCCT
is not required and lists it among out-of-scope inputs; the code now
requires it per the operator directive, which also mandates the contract
stay untouched through verify. This is a recorded, deliberate override,
but the fresh approval after the mechanical Phase-S amendment would
otherwise bind a contract that contradicts the code it authorizes. Since
that amendment changes the blob anyway, the operator should decide whether
the amendment absorbs one sentence naming the rawdata NCCT as an
audit-only diagnostic input (the same forward-correction shape as the
2026-08-24 NCCT clause rulings) and whether `bin_tissue_audit.csv` joins
`required_outputs`; the audit file is currently a contract-undeclared
extra, which validators tolerate but record-result should expect.

**N2 — Missing/unreadable NCCT failure classes are latent
misclassifications.** A missing NCCT exits 5 (population failure) though
the contract's population clause names only maps and label; an unreadable
NCCT gzip exits 6 fail-loud with no exclusion path (the
`SOURCE_CORRUPT_MEMBERS` tuple is CBF-only, run.py:346-358). Both are
latent: the archive manifest counts 149/149 rawdata NCCT members and two
independent full-archive integrity sweeps found exactly one defective
member, the preregistered CBF. Fail-loud is the contract's own
conservative default for unlisted members; recorded, no change requested.

**N3 — Audit rows inherit R16's overlap semantics.** Where a band's
per-patient cuts are degenerate (q1 == q3), the Q1 and Q4 style groups
overlap (identical when the band is constant), so their HU rows describe
overlapping voxel sets — deterministic, label-blind, and consistent with
the estimator's own R16 behavior. When the README gains its R16 sentence,
one clause should extend it to the audit so the interpret stage does not
rediscover this.

**N4 — Cosmetic.** `resolved_config.json` reports
`"label_blind_ncct_tissue_audit": true` in every phase including S and
smoke, where no audit runs (run.py:983); harmless but mildly misleading.
R17's context-manager and inline-writer nits carry unchanged.

## Verdict

The audit itself is implemented faithfully to the 2026-08-28 activation:
label-blind by construction, computed from the estimator's own cached
region/band/cut artifacts, persisted to the per-case cache and
`bin_tissue_audit.csv` before any invalidating exit, with no estimator
change, no HU-consuming gate, no new RNG, and the contract blob untouched
so the standing approval correctly survives through this verify stage. But
two defects meet the blocking bar: the unconditional quartile-finiteness
assert converts a tolerated input class — a patient whose eroded deficit
region leaves a flow band empty — into an unclassified exit-13 death
mid-take, and the unchanged README still instructs an extraction set that
omits the NCCT the code now requires, which would kill take 13 at the
first map-pass case through the very launcher-dependency mechanism built
after attempt 1. Both are agent-resolvable in one probe-build touch with
no contract or scope change; N1 is queued for the operator at the
mechanical amendment.

```json
{"verdict": "REVISE", "blocking": ["B1: tissue_audit asserts finite quartile cuts unconditionally (run.py:567) while the map pass produces NaN cuts for empty flow bands (run.py:796-799); a small-deficit census patient crashes the take as exit-13 harness failure on contract-valid input that patient_measure deliberately tolerates (run.py:604-610)", "B2: README extraction set (README.md:24-26,37) says rawdata NCCT is not used, but run.py:454 hard-requires it per case (exit 5 if absent); the take-13 launcher regenerated from this declaration would kill the run at the first map-pass case"], "note": "HU tissue audit is faithful to the 2026-08-28 directive (label-blind, estimator/gates/contract untouched, approval validly standing), but an empty-band assert crash and a stale README extraction-set declaration must be fixed before take 13; contract-text harmonization for NCCT queued to the amendment (N1)."}
```
