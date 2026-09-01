# Critique — idea 046 (Who carries the band-2/3 reversal, and do the carriers differ clinically?)

```
FATAL OBJECTION: NONE
EVIDENCE: per_patient.csv and archive_manifest.csv (probes/023/results/results_v2/) verify both keystone parts at the structural level; the two real defects (a power-confounded concentration rule, a false "small download" acquisition claim) are named below and are repairable.
REPAIRABLE WITHOUT CHANGING THE QUESTION? YES
DECISION: ADVANCE TO REVISION
```

## 1. What was independently verified for this critique

All checks below were structural (file existence, sizes, identifiers, row
counts). No leave-one-out statistic, concentration index, or any other
quantity the card proposes to pre-register was computed, and no outcome
values were read — deliberately, so this critique does not contaminate the
Rung-0 pre-registration it is evaluating.

- **Card's verified_facts are transcription-exact.**
  `probes/023/results/results_v2/per_stratum_summary.csv` gives band-2 mean
  d = -0.03200 [-0.05591, -0.00798] and band-3 mean d = +0.02308
  [+0.00497, +0.04357], medians hugging zero — matching the card to the
  stated precision. The take-13 interpretation says verbatim (line 202
  context): "no aggregate HU statistic or per-patient contribution analysis
  was computed." The 2026-08-28 pre-registered clinical join is in
  `evidence/decisions.md` and has not been executed. The 045-v3
  interpretation confirms beta_HU's interval spans zero and the reversal
  survives adjustment.
- **Keystone part (a) holds** (also established by the keystone screen):
  297 rows, 99 unique cases, 99 per stratum, unique keys, finite d.
- **Keystone part (b) is stronger than the screen concluded — the decisive
  evidence was already committed and the screen missed it.** The take-13
  bundle includes `archive_manifest.csv`, the member listing of the
  md5-verified `train.7z`. It contains 298 phenotype members under
  `train/phenotype/sub-strokeNNNN/ses-0{1,2}/` — 149 demographic_baseline
  and 149 outcome CSVs — using the **same `sub-strokeNNNN` identifier
  spelling as `per_patient.csv`**. A structural join shows **all 99
  analyzed case IDs have a `ses-02/..._outcome.csv` member** (empty
  set-difference; 149 outcome cases total). Outcome file sizes are 93–105
  bytes, uniformly nonzero — consistent with a header plus one populated
  data row and with no degenerate/empty files. The screen's residual
  assumption (identifier mapping ambiguity, documentation `sub-strokecase`
  vs payload `sub-stroke`) is thereby resolved at the file level from a
  hash-pinned committed artifact. What remains genuinely unverified is only
  column-level content: whether the outcome values inside those rows are
  populated (non-missing) for ≥90 of the 99. The ≥90 **file-level**
  coverage floor is met at 99/99.

The revision should cite `archive_manifest.csv` in `keystone_evidence` and
upgrade the keystone accordingly; the current `NOT_INSPECTED` undersells a
fact that is inspectable in-tree today.

## 2. Named defects (all repairable)

### D1 — The proposed concentration classifier measures statistical margin, not concentration

The card's decisive Rung-0 rule is "the smallest patient subset whose
removal moves either precise band CI to include zero." This conflates two
things. Removing k same-signed patients from N=99 simultaneously (i)
shifts the point estimate toward zero and (ii) widens the CI (smaller N
under patient-clustered resampling). Both effects push the CI toward
including zero **regardless of how concentrated the contributions are**.
Band-2's CI upper bound is -0.008 — a hair from zero — so a tiny removal
set will flip it under almost any contribution structure, including a
perfectly diffuse one. As frozen, the rule would return
"subset-concentrated" nearly tautologically; the classification would be
uninformative, and the candidate's decisive experiment would decide
nothing. The metric as written is a re-expression of the t-statistic
(margin over zero relative to CI width), not of who carries the effect.

**Repair (question unchanged):** classify concentration against an
explicit reference distribution — e.g., compare the observed
top-k contribution share (or the Gini-style index the card already names)
to its null distribution under random relabeling of equal-sized subsets,
or freeze a share-based rule ("the smallest set of patients accounting
for X% of the summed same-signed contributions") judged against what
exchangeable contributions would produce. The CI-flip count may be
reported, but as a descriptive sidebar, never the classifier. This must
be fixed **before** the rule is frozen, because it defines the
deliverable's meaning.

### D2 — The Rung-1 acquisition claim is factually wrong

The card says Rung 1 "adds one small phenotype download from the pinned
public record." False: the pinned Zenodo record (16813698) exposes only
`train.7z` (~99 GB) and the small `clinical_data-description.xlsx`
dictionary; the 298 phenotype CSVs are **members of `train.7z`** (proven
above from the archive manifest). There is no small separate download.
Acquiring them means re-staging the full archive by the proven
origin_direct path (aria2c, ~14 min on Colab per the take-8 receipt) and
extracting ~300 tiny files — bounded and demonstrated, but not what the
card states. `keystone_prerequisite` part (b)'s "downloads at small size"
carries the same error. The feasibility conclusion survives; the stated
cost model does not. Rewrite it honestly.

### D3 — Reserved-case blindness needs an explicit protocol

Staging `train.7z` for phenotype extraction brings outcome files for all
149 cases into reach, including the 49 reserved cases the card promises
remain untouched. The frozen protocol must restrict extraction (or at
minimum any read) to the 99 analyzed IDs, and say so — otherwise the
reserve's untouched status rests on discipline rather than construction.
Cheap to fix; must be written down.

### D4 — The predictable trivial explanation for a positive Rung 1 is not named

Final-infarct extent correlates with mRS/NIHSS for ordinary clinical
reasons. If high-contribution patients differ on lesion/deficit burden —
plausible, since |d| is computed within deficit-derived bands — then
"carriers differ on outcome scores" collapses to "bigger strokes are
worse," which is not a finding. The card lists deficit-region voxel
counts among comparison variables, but the revision must make this
explicit: any stratum difference on clinical scores is reported jointly
with the deficit-size difference, and the write-up may not present an
outcome-score difference that deficit size already accounts for as an
independent clinical signature. Descriptive framing does not exempt the
card from naming the confounder its own design makes likely.

### D5 — Mode misclassification distorts the score

The card declares `search_mode: C` and reports `mode_c_priority_score
4.1`, but nothing here is speculative: it is the most feasible, most
staged candidate in the record, and its own `mechanism_clarity` note
concedes it "characterizes structure rather than testing a mechanism."
Under Mode C weighting (30% mechanism clarity) the candidate is scored on
the axis it explicitly declines to have, while its actual strengths
(feasibility, prior legwork, data readiness) are excluded from the score.
Score it under the standard rubric at revision. This changes bookkeeping,
not merit.

### D6 — Multiplicity bound is a promise, not a list

"Few frozen comparisons" is not pre-registration. The revision must
enumerate the exact comparison variables (the card's own candidates:
deficit-region voxel count, vessel-cap statistic, exclusion flags, NIHSS
24h, mRS 3 months) and the exact descriptive contrasts, before any
stratum membership is computed.

## 3. Standard rejection sweep

- **Prior-work overlap:** leave-one-out/influence accounting is textbook
  (the card says so); the object it is applied to — a pre-registered,
  ratified band-contrast census — exists nowhere outside this repository.
  No overlap to reject on. Novelty is correctly claimed as governed
  application, not method.
- **Circularity/leakage:** no model is probed; outcome scores were never
  inputs to the label-blind pipeline that produced `per_patient.csv`, and
  they stay sealed until Rung 1. The lesion-size/outcome correlation is
  confounding-of-interpretation (D4), not leakage.
- **Charter fit:** weakest axis. The candidate delivers no "the model is
  using X" sentence and probes no model; it is descriptive epidemiology on
  an internal structure. Mitigation: it is an operator-authored successor
  executing a pre-registered 2026-08-28 decision item on the isles24
  track, and a concentrated result is precisely what makes a future
  model-use successor targetable. Acceptable as lineage work; the card's
  `use_vs_association` honesty is exemplary. Not fatal, but the revision
  should not dress it as more than it is.
- **Data availability / compute:** Rung 0 in-tree, minutes of CPU. Rung 1
  proven path (D2 correction notwithstanding). No DUA, no GPU, no
  annotation.
- **Negative-result value:** genuine. A null-calibrated "diffuse" verdict
  is decisive *as a description of these 99 cases* and kills
  high-leverage-patient explanations; a failed content-level join kills
  only Rung 1 by construction. With D1 unfixed, however, the negative arm
  barely exists (everything reads "concentrated") — another reason D1 is
  the critique's most important item.
- **Endpoint clarity:** clear once D1 and D6 are frozen.
- **Plain-pitch fidelity:** the card carries no `plain_pitch` field;
  nothing to check. If one is added at revision it must carry the
  exploratory-by-construction label prominently.

## 4. The easier version

There is no easier version to find: Rung 0 **is** the low-hanging fruit —
deterministic CPU on a committed 297-row CSV. The one further
simplification worth naming: if Rung-1 acquisition is judged not worth a
99 GB re-stage right now, Rung 0 plus the bundle-derivable stratum
comparison (voxel counts, vessel caps, exclusion flags — all already
in-tree) stands alone as a complete, decisive mini-study, with the
clinical join deferred to whenever the archive is next staged for any
other purpose. The revision could make Rung 1 explicitly opportunistic on
the next staging event rather than a dedicated download.

```
NEAREST DEFENSIBLE HIGH-VALUE QUESTION: Exactly the card's Rung-0 question with a null-calibrated concentration rule — is the band-2/3 reversal carried by a nameable patient subset or diffusely, judged against what exchangeable contributions would produce?
RETAINS ORIGINAL MEDICAL MOTIVATION? YES
SHOULD IT BECOME A SEPARATE CANDIDATE? NO — it is this candidate after revision, not a spin-off.
IS IT ACTUALLY WORTH DOING? YES — minutes of CPU against the largest unexplained fact in the ratified record, with every input hash-pinned in-tree; the only way it becomes not worth doing is if D1 stays unfixed, in which case the answer is predetermined and worthless.
```
