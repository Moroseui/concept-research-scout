# Feasibility memo — idea 046

**Idea:** Which observed cases numerically carry the band-2/3 reversal?
(post-revision descriptive contribution census; revise-in-place ratified by
the operator 2026-09-01, `unblock_ack.txt` on record)
**Stage:** feasibility. **Date:** 2026-09-01. **Verdict: GO** (stated in
full at the end).

Scope note: this memo evaluates the candidate as revised — a
finite-population contribution census on the imported idea-023 take-13
table, with an optional descriptive clinical join — not the retired binary
diffuse-versus-carrier design the debate killed. The drafted
`probe_contract.yaml` v1 (outcome-blind definition audit) is treated as the
smallest probe and assessed in section 9.

Every claim below is labeled. "Verified today" means directly inspected in
this stage on 2026-09-01, by hash, row census, verbatim quote, or live
fetch of the primary source.

---

## 1. The keystone, re-verified independently

Verified today, all on the committed artifact
`probes/023/results/results_v2/per_patient.csv`:

- SHA-256 is `1d01551c888d77b6382f7cbe36e4bb68a6d2f2ef4b26e09832bfda45d2c40e0c`
  — byte-identical to the frozen pin in `probe_contract.yaml`.
- 297 data rows; 99 unique `case_id` values; exactly 99 rows in each of
  strata 1, 2, 3; zero duplicate `(case_id, stratum)` keys.
- The `d` column contains 297 digit-bearing numeric entries; zero `nan`,
  zero `inf`, zero empty fields.

This reproduces the keystone screen's census from scratch. The card's
`keystone_status: INSPECTED_TRUE` stands on a third independent
inspection (keystone screen, critique, this memo).

**Residual-assumption check.** Having verified the nearest checkable
thing, what is the primary analysis still assuming? Nothing further: the
census contribution `c_i = (d_i,band3 − d_i,band2)/99` is a closed-form
function of exactly the rows verified above, and the additive identity it
must satisfy is arithmetic, gated by the drafted probe at tolerance 1e-12.
The load-bearing assumption for the *secondary* (clinical) rung is
different and is treated in section 5.

## 2. Parent gap, re-verified

Verified today, verbatim from `ideas/023/interpretation.md` lines 200–202
(the ratified, cross-family-reviewed interpretation):

> How prevalent the Q1-vs-Q4 tissue imbalance is across the cohort, or
> which patients drive the band-level means — no aggregate HU statistic or
> per-patient contribution analysis was computed.

And from `probes/023/results/results_v2/per_stratum_summary.csv`,
transcription-exact against the card: band-2 mean d = −0.03200187,
CI [−0.05590633, −0.00797819]; band-3 mean d = +0.02307549,
CI [+0.00496569, +0.04356979]. Opposite signs, both intervals excluding
zero. The estimator this candidate decomposes exists, is ratified, and its
per-patient decomposition is explicitly recorded as never computed.

## 3. Closest work and exact gap

Case-deletion influence diagnostics, the jackknife, and Lorenz/Gini
concentration summaries are textbook statistics — Cook 1977
(DOI 10.1080/00401706.1977.10489493) and Lorenz 1905
(DOI 10.2307/2276207) are the canonical anchors. **Not verified:** neither
primary source was fetched this stage; identifiers are transcribed for
context and no claim in this candidate rests on their content
(`evidence/literature.csv` marks them accordingly).

The card claims no methodological novelty, so the novelty burden is
narrow: the *object* — a pre-registered, ratified, hash-pinned band-2/3
contrast estimator on the ISLES'24 99-case census — exists only in this
repository, so no external work can have decomposed it. The exact gap is
the sentence quoted in section 2. This is the same "governed application,
not method" framing the critique accepted, and it is the correct one.

## 4. Dataset access and license

**Primary rung — verified today:** entirely in-tree. The input table and
every bundle-derivable secondary variable (deficit-region voxel counts,
vessel-cap statistics, exclusion flags in
`probes/023/results/results_v2/exclusions.csv`) are committed under the
record-result gate. No download, no DUA, no gate, no annotator. License
posture inherited: the tables are derived aggregates of ISLES'24
(CC BY-NC-SA 4.0) already committed in-repo; no new license action.

**Secondary rung (optional) — verified today by live API fetch:** Zenodo
record 16813698 remains open access, license CC BY-NC-SA 4.0, no access
request; `train.7z` listed at 99,014,629,647 bytes with MD5
`36ae28b9a17f7340b8bbef62b595cb57` — matching the take-10 md5-arbitrated
TRUE object and the standing staging pin. The record is version 2 of
concept DOI 10.5281/zenodo.16731717 and is *not* the latest version;
newer children exist, which is exactly why acquisition must go through the
existing `--staging-record`-pinned origin_direct path and never a
re-resolved concept link. The record description confirms the clinical
payload: "Demographics, patient history, admission NIHSS, 3-month
functional outcome (mRS), etc."

There is **no small phenotype download** (critique D2, confirmed): the 298
phenotype CSVs are members of the 99 GB archive. Acquisition cost for the
clinical rung is one full restage.

## 5. Label availability and concept validity

The primary rung needs **no labels at all** — it is arithmetic on frozen
`d` values. This satisfies the charter preference for readouts independent
of label quality by construction, and no annotation-provenance failure
mode can apply.

For the optional clinical rung, verified today from
`archive_manifest.csv` (the member listing of the md5-verified archive):

- 298 phenotype members: 149 `ses-01 demographic_baseline` + 149
  `ses-02 outcome` CSVs, identifier spelling `sub-strokeNNNN` — the same
  spelling as `per_patient.csv`, resolving the documentation-vs-payload
  spelling hazard at the file level.
- Set-difference of the 99 analyzed IDs against outcome-file IDs: empty.
  Same for demographic files. **File-level join coverage is 99/99**,
  exceeding the ≥90 floor the original keystone asked for.
- Outcome files are 93–105 bytes each, uniformly nonzero — consistent
  with a header plus one populated row.

**Not verified, and honestly not verifiable without restaging:**
column-level content — whether NIHSS-24h and mRS-3-month values inside
those rows are populated (non-missing) for the analyzed cases, and the
exact column schema. The data dictionary (inspected at keystone, SHA-256
recorded there) names both variables as integer outcome fields. The card
prices this correctly: the clinical join is optional secondary description
and cannot redefine the primary result. A failed content-level join kills
only the clinical rung, by construction.

## 6. Sample structure and split unit

The unit is the case (one stroke patient), the only defensible choice:
contributions are per-case by definition. Structure, verified today:

- 149 released cases; take-13 census covered 100, analyzed 99
  (`sub-stroke0043` excluded as `source_corrupt_member`, named in
  `exclusions.csv`; it is absent from the analyzed-ID set — checked).
- The 49 never-censused cases are the untouched reserve and appear in no
  input of this candidate.
- No new split is created. The study is exploratory by construction: the
  99 outcomes were opened in idea-023, so freezing definitions before
  computation is a discipline commitment, not cryptographic blindness.
  The card and contract both state this; the same standing condition
  applies to every same-split successor in this lineage.
- Critique D3 discipline: any restage must restrict phenotype reads (and
  preferably extraction) to the 99 analyzed identifiers. The drafted
  probe contract excludes phenotype access entirely; the later census
  contract must encode the D3 read-restriction protocol explicitly.

## 7. Existing code, checkpoints, compute

No model, no checkpoint, no GPU anywhere in this candidate. The frozen
take-13 pipeline (which produced the input) is complete and ratified;
nothing from it needs re-running for the primary rung.

Compute, in three tiers:

1. **Definition-audit probe (drafted contract v1):** deterministic CPU,
   single pass over a 298-line CSV, 5-minute wall cap, zero GPU minutes.
   Trivially within constraints.
2. **Census (future contract):** the frozen curves and summaries on 99
   values — minutes of CPU.
3. **Optional clinical rung:** one full archive restage via the proven
   origin_direct path (~14 min download on Colab per the take-8 receipt,
   plus extraction under the rc-checked integrity sweep, which tolerates
   the known `sub-stroke0043` source defect), then ~300 tiny-file reads.
   One session, no GPU. **Not verified:** whether 7z selective extraction
   of only the phenotype subtree works as intended; the proven path
   extracted the full archive, so worst case is the full extraction cost
   already demonstrated in take 12/13.

## 8. Baselines, metrics, negative result

No external benchmark applies and none is claimed. The internal baseline
is mathematical: for N = 99, the summed per-case contributions must equal
the band-3-minus-band-2 mean gap to within 1e-12 (stable summation). The
metrics are the frozen descriptive summaries: full signed `c_i` set,
descending cumulative curve, absolute-contribution Lorenz curve, top-k
shares (k = 1, 5, 10, 20), smallest k reaching 50% / 80% of positive
contribution — all fixed in the card before any contribution value is
computed.

Anticipated negative, as classified in the card: a shallow ranked curve
decisively rules out numerical dominance by a small observed set *for this
realized estimator*. That is a genuine type-1 (decisive) negative within
the candidate's own finite-population register; it establishes nothing
about stable diffuseness or population structure, and the card's
prohibited-conclusions list prevents anyone claiming otherwise.

## 9. Critical leakage, confounds, and the smallest probe

**Leakage surfaces, in order of danger:**

1. *Outcome exposure during the audit.* The drafted probe contract's
   no-result-exposure discipline (no case IDs, values, ranks, shares,
   means, or gaps in any output or log) is the right control, and its
   invalidating-failure list makes exposure a validity kill rather than a
   footnote.
2. *Reserved-case contact during a restage.* Controlled by the D3
   restriction (section 6).
3. *Interpretive leakage.* The known predictable confound (critique D4):
   deficit size correlates with clinical outcomes for ordinary reasons,
   and |d| is computed within deficit-derived bands. The card mandates
   joint display of deficit size with any clinical contrast and prohibits
   presenting outcome differences that deficit size accounts for as
   independent signatures. That is the correct and sufficient handling
   for a descriptive study.

Standing charter confounds (scanner, protocol, reconstruction, site,
positioning, habitus, prevalence, referral, report leakage) cannot alter
the arithmetic decomposition of a fixed estimator and no transport claim
is made; they re-enter only if a successor tries to interpret contribution
rank biologically, which the prohibited-conclusions list forbids here.

**Prior-art / intervention subsection: not applicable.** This candidate
edits no inputs, perturbs no maps, and synthesizes no cases; it is a
deterministic description of a committed table. No stay-in-distribution
strategy is required because nothing is moved in or out of distribution.

**Smallest probe of the riskiest assumption.** With the keystone
inspected true three times, the riskiest *remaining* assumption is
exactly what the drafted contract v1 targets: that the frozen definitions
are algebraically coherent and numerically well-posed on the real table —
additive identity within tolerance, finite nonzero denominators for every
share (a nearly-zero total positive contribution mass would make the
50%/80% smallest-k summaries degenerate), and deterministic tie
resolution. The probe answers this outcome-blind, at zero scientific
cost, before any census contract is drafted. This memo finds the probe
correctly scoped and endorses it as drafted.

## 10. What was NOT verified (consolidated)

- Column-level phenotype content: populated NIHSS-24h / mRS-3mo values
  for the 99 analyzed cases (file-level coverage is 99/99; content needs
  the restage).
- Exact phenotype CSV column schema versus the data dictionary.
- 7z selective extraction of the phenotype subtree only.
- Cook 1977 and Lorenz 1905 primary texts (context citations only; no
  claim rests on them).
- Observed concentration shape — deliberately: that is the study.

## 11. Verdict

**GO.**

Grounds: every load-bearing input to the primary rung is committed,
hash-pinned, and independently re-verified in this memo; the compute is
minutes of CPU; the license is settled; no annotation, DUA, GPU, or
external cohort is involved; the parent gap is quoted verbatim from a
ratified interpretation; and the one honest unknown (phenotype column
content) is confined by construction to an optional secondary rung that
cannot redefine the primary. The failure modes that killed prior
candidates — annotation provenance, wrong keystone, unobtainable data,
OOD interventions — have no purchase on a deterministic decomposition of
an in-tree table whose exact bytes are contract-pinned.

GO authorizes, in sequence and each behind its own gate: human approval
of the drafted v1 definition-audit contract; then a separate census
contract (which must encode the D3 read-restriction protocol and the D4
joint-display rule); the clinical join remains optional and opportunistic
on the next archive staging event. Nothing in this memo authorizes code
or execution.

## In plain terms

This study can definitely be run: the only data it needs for its main
question is a small table already stored and verified in this repository,
and the computation is simple arithmetic that takes minutes on an
ordinary computer. The optional second step — checking whether
high-contribution patients differ on stroke-severity scores — would
require re-downloading a 99 GB public archive once, using a download
recipe this project has already proven, because the clinical files sit
inside that archive rather than as a separate small file. The biggest
practical risk is modest: the clinical score values inside those files
have not yet been read, so that optional step could turn out empty even
though a matching file exists for all 99 patients. If that happens, the
main analysis is unaffected. Nothing here involves patient identification,
new data collection, or machine-learning compute.
