# Context memo — CT-Scroll benchmark context for idea 004 (tier 2)

**Stage:** context-memo extraction per the 2026-08-14 amendment to pin 2
(`evidence/decisions.md`). **Access date:** 2026-08-14. **Status:** for human
ratification. Checker-mode: every substantive claim carries a verbatim quote
with a table/section identifier and an epistemic label.

**Standing rule restated:** every number in this memo is benchmark CONTEXT for
descriptive comparison. No number here plays a pass/fail role anywhere in the
idea-004 study. This memo contains no equivalence margin, no threshold, and no
cutoff language, per the amended pin 2.

**Extraction method and identifier caveat, on the record:** all quotes were
obtained 2026-08-14 via WebFetch of the official arXiv HTML renderings
(`arxiv.org/html/2503.20652v6` and `...v1`) and cross-checked against the
ar5iv rendering. Table 1 (v6) was transcribed twice in independent passes with
full agreement; the partition sentence was transcribed three times (twice v6,
once v1) with a targeted numeric probe. Identifiers are **table and section
numbers**, not PDF page numbers: the HTML rendering carries no pagination.
Residual risk: WebFetch extraction is mediated by a small model; the ratifier
can spot-check any quote against the PDF in minutes, and the table/section
identifiers below are given to make that cheap.

---

## 1. Split determination (gates everything else)

### What the paper says

**Verified quote — v6 and v1, Section 3 (Dataset), partition sentence.** v6:

> "The dataset is partitioned as follows: 17,799 unique patients for the train
> set, 1,314 unique patients for the validation set and 1,314 unique patients
> for the test set."

v1 of the same sentence carries the volume counts that v6 dropped:

> "The dataset is partitioned as follows: 17,799 unique patients corresponding
> to 34,781 CT volumes for the train set, 1,314 unique patients, corresponding
> to 3,075 CT volumes for the validation set and 1,314 unique patients,
> corresponding to 3,039 CT volumes for the test set."

A targeted probe of v6 confirmed the numbers 34,781 / 3,075 / 3,039 appear
nowhere in the v6 Dataset section — the volume counts exist only in earlier
versions.

**Verified quote — v6 Table 1 caption (Section 6, Experimental Results):**

> "Quantitative evaluation on the CT-RATE and Rad-ChestCT test sets. Reported
> mean and standard deviation metrics were computed over 5 independant runs.
> Best results are in bold, second best are underlined. (†) refers to
> weight-inflation."

(The spelling "independant" is the paper's.)

**Verified quote — v6 Section 6.1 (Quantitative results), aggregation:**

> "On the test set, we compute the average of each metric across all labels, as
> well as the weighted average F1 Score (W. F1 Score) based on label
> frequencies in the test set."

**Verified quote — v6 Section 6.1, role of their validation split:**

> "For classification, we determine the threshold that maximizes the F1-Score
> for each of the 18 labels on the validation set"

**Verified absence — v6, targeted search:** no sentence anywhere in the paper
states how the 17,799/1,314/1,314 partition maps to the official CT-RATE
release (which has only a train split and a validation split). No footnote or
citation is attached to the partition sentence.

### Verdict on the reviewer's claim ("test-set, label-averaged")

- **Label-averaged: CONFIRMED** by the Section 6.1 quote above. Table 1 AUROC
  is the average across all 18 labels. A targeted search confirmed **no
  per-label results table exists anywhere in the paper** (main text or
  appendix; the four tables are enumerated in §6 below).
- **"Test set": CONFIRMED as the paper's wording, but the substantive
  split-mismatch premise is REFUTED at the volume level.**
  *Source-supported interpretation, clearly labeled as such:* the paper's
  "test set" is 1,314 patients / **3,039 CT volumes** (v1 sentence). 3,039 is
  exactly the volume count of the official CT-RATE validation split as
  directly audited in Stage 0 (3,039 validation volumes / 1,564 scans / 1,304
  patients, 2026-08-04 ledger entry). The paper's "test set" is therefore
  almost certainly the official CT-RATE **validation** split relabeled, with
  the authors' own "validation" (3,075 volumes) carved from the official train
  data. The paper never states this mapping (verified absence above), so this
  is an inference from an exact count match, not a verified fact.
- **Residual discrepancy, unresolved:** CT-Scroll counts 1,314 patients where
  the official card and Stage 0 count 1,304 for the same 3,039 volumes. This
  10-patient bookkeeping difference was already flagged in `feasibility.md`
  and remains unexplained. It does not affect the volume-level identity of the
  3,039-volume pool.

**Consequence for the amendment:** the reviewer's conclusion (context, not
margin) survives, but partly on different legs than their premise. The
aggregation mismatch (18-label average vs per-head) is confirmed and alone
justifies the amendment. The split mismatch is weaker than claimed: CT-Scroll's
numbers were most likely computed on the same 3,039-volume pool our study
draws its 425 pairs from. Two further mismatches found during extraction
(§5, items 3–5: model provenance, seed-variance vs sampling-variance, and
version instability of the table) independently reinforce the demotion to
context-only. Checker-mode applied to the reviewer as required: their claim
was directionally right for the wrong split reason.

---

## 2. Extracted values (v6, Table 1, CT-RATE block)

**Primary context version: arXiv v6** (latest, 26 Dec 2025). All values are
AUROC on the 0–100 scale, mean ± std over 5 training runs, averaged across the
18 labels, from **Table 1** ("Quantitative evaluation on the CT-RATE and
Rad-ChestCT test sets"), CT-RATE rows, transcribed twice with agreement:

| Method (as printed) | AUROC (verbatim) |
|---|---|
| Random Predictions | 49.88 ± 0.62 |
| ViViT† | 79.19 ± 0.28 |
| Swin3D† | 79.94 ± 0.15 |
| CT-Net | 79.37 ± 0.27 |
| 3D CNN† | 81.47 ± 0.78 |
| CT-Scroll (ours) | **81.80 ± 0.22** (bold in source) |

Rad-ChestCT rows exist in the same table but concern a different dataset and
are out of scope for this context.

**Internal inconsistency in the source, on the record:** v6 Table 2
("Comparison of performance across different modules", Section 6.2) lists the
ViViT AUROC as **73.19 ± 0.28**, while Table 1 prints **79.19 ± 0.28** — same
±, different leading digits. Every other method shared between the two tables
carries identical values (Swin3D 79.94 ± 0.15, CT-Net 79.37 ± 0.27, 3D CNN
81.47 ± 0.78, CT-Scroll 81.80 ± 0.22), and no sentence states which dataset or
split Table 2 uses (verified absence). One of the two ViViT entries is
presumably a typo; the source does not say which. Table 1 is used for the
context spread; the inconsistency is recorded so the interpret stage inherits
it.

---

## 3. Derived spread — CONTEXT ONLY

**Label:** the numbers below are descriptive benchmark context. They are not a
margin, not a threshold, and carry no pass/fail semantics anywhere in the
idea-004 analysis (amended pin 2). Random Predictions is excluded from the
spread: it is a floor diagnostic, not a trained model.

**v6, trained models (ViViT 79.19, CT-Net 79.37, Swin3D 79.94, 3D CNN 81.47,
CT-Scroll 81.80), 18-label-averaged AUROC points on the 0–100 scale:**

- **Max − min spread: 81.80 − 79.19 = 2.61**
- All pairwise gaps:

| Pair | Gap |
|---|---|
| CT-Net − ViViT | 0.18 |
| CT-Scroll − 3D CNN | 0.33 |
| Swin3D − CT-Net | 0.57 |
| Swin3D − ViViT | 0.75 |
| 3D CNN − Swin3D | 1.53 |
| CT-Scroll − Swin3D | 1.86 |
| 3D CNN − CT-Net | 2.10 |
| 3D CNN − ViViT | 2.28 |
| CT-Scroll − CT-Net | 2.43 |
| CT-Scroll − ViViT | 2.61 |

Adjacent-rank gaps: 0.18, 0.57, 1.53, 0.33 — the smallest distinction the
benchmark is used to adjudicate between neighboring methods is ~0.2–0.3
AUROC points; the full between-model range is ~2.6.

**Version sensitivity of the spread (new finding, reinforces the amendment):**
v1 of the same table (caption identical minus the "(†)" sentence) compared a
different baseline set — verbatim v1 CT-RATE rows: Random Predictions
49.88 ± 0.62, 3D CNN 76.49 ± 0.28, CT-ViT 73.92 ± 1.17, Swin3D 79.94 ± 0.15,
CT-Net 79.37 ± 0.27, CT-Scroll (ours) 81.80 ± 0.22. The v1 trained-model
spread is 81.80 − 73.92 = **7.88** — three times the v6 spread — because
between versions the authors replaced CT-ViT (73.92) with ViViT (79.19) and
their 3D CNN baseline moved from 76.49 to 81.47. The ar5iv rendering
independently corroborates the old-version values. The debate-era reference to
"the CT-Net / Swin3D / CT-ViT / global-local spread" described the earlier
table. A margin anchored to this table would have tripled or shrunk by a
factor of three depending on which arXiv revision was fetched — concrete
evidence that the amendment's demotion of CT-Scroll to context was correct.
Any future citation of these numbers must name the arXiv version.

---

## 4. Exposure statement (mandatory, on the record)

The contract-v1 load probe (real A/B/A run, 2026-08-12) exposed the per-head
diagnostic scores of exactly one Stage-0-valid Br40f|Br60f pair — 18 heads for
A, B, and repeated A, with a maximum absolute A-versus-B difference of
0.0070026815 — and those scores were declared scientifically uninterpretable
in the v1 contract itself. The author of this memo has also seen that summary
in `ideas/004/decision.md`.

Why this does not compromise tier 2:

1. **The context numbers cannot be influenced by the exposure.** Every number
   in this memo derives solely from CT-Scroll's published tables, fixed by its
   authors before this program existed. Nothing observed in the load probe
   entered §2 or §3.
2. **There is no margin to steer.** Under the amended pin 2, tier 2 contains
   zero threshold language; no number extracted here acquires pass/fail
   semantics. The classic risk of exposure — tuning a margin so that an
   already-seen result clears or fails it — has no target to act on.
3. **Tier 1 is label-free and unaffected.** The primary floor readout
   (per-head, per-stratum paired-difference distributions) uses no labels and
   no external number at all.
4. The one exposed pair is 1 of 425; its diagnostic deltas remain excluded
   from any confirmatory statistic by the v1 contract's own terms, and the
   contract-v2 analysis plan is frozen before any bulk score is seen.

---

## 5. Mismatch caveats (inherited by the interpret stage)

1. **Aggregation level.** Table 1 AUROC is averaged across all 18 labels
   (quoted, §1). The 425-pair study reports per-head quantities. A between-
   model gap of 2.61 in the 18-label average says nothing direct about any
   single head; per-head between-model gaps could be larger or smaller, and
   the paper publishes no per-label breakdown to check (verified absence).
2. **Split naming vs split identity.** The table says "test set"; that set is
   almost certainly the official CT-RATE validation split (3,039 volumes)
   relabeled (§1, source-supported interpretation). So the volume pool likely
   matches ours; the residual differences are the 1,314-vs-1,304 patient
   bookkeeping and the fact that CT-Scroll's models were trained on a
   34,781-volume subset of official train (v1 sentence) whose selection rule
   is unstated — official train contains ~47k volumes, so ~9k volumes are
   unaccounted for by any sentence in the paper.
3. **Model provenance.** The spread is between models trained by the CT-Scroll
   authors (5 seeds each, their own train subset). ClassFine — the checkpoint
   our study probes — does not appear in the table. The context is "how far
   apart published methods sit on this benchmark," not "how variable is our
   model."
4. **Uncertainty concept.** The ± terms are std across 5 training seeds
   (between-run training variance; caption, §1), not sampling variance over
   scans or patients. Our tier 2 reports patient-cluster bootstrap confidence
   intervals — a different uncertainty object. The two are not comparable as
   error bars.
5. **Scale and label source.** Table 1 is on the 0–100 AUROC scale; our
   deltas will be computed on [0,1] and must be scale-converted when
   contextualized. Both CT-Scroll's labels and CT-RATE's released validation
   labels are RadBERT report-derived; tier 2 therefore measures benchmark
   discrimination against report-derived labels, never clinical diagnostic
   accuracy (amended pin 2, restated).
6. **Source-internal inconsistency.** The v6 ViViT value differs between
   Table 1 (79.19) and Table 2 (73.19) with no stated explanation (§2). If
   the interpret stage cites the ViViT-involved gaps, it must carry this
   caveat; the three ViViT-free pairwise gaps among CT-Net/Swin3D/3D CNN/
   CT-Scroll (0.57, 1.53, 2.10, 0.33, 1.86, 2.43) are unaffected.

---

## 6. Sources

- **Primary:** arXiv:2503.20652, "Imitating Radiological Scrolling: A
  Global-Local Attention Model for 3D Chest CT Volumes Multi-Label Anomaly
  Classification," Theo Di Piazza, Carole Lazarus, Olivier Nempont, Loic
  Boussel. Comments field: "13 pages, 4 figures. Accepted for publication at
  MIDL 2025."
- **Version used for primary context: v6** (Fri, 26 Dec 2025 — latest at
  access). Version history on the abs page: v1 26 Mar 2025, v2 27 Mar 2025,
  v3 28 May 2025, v4 6 Jun 2025, v5 4 Sep 2025, v6 26 Dec 2025.
- **Version used for the volume-count sentence and version-sensitivity
  check: v1** (26 Mar 2025), corroborated by the ar5iv rendering (version
  banner not displayed; content matches v1's partition sentence and baseline
  set).
- Renderings fetched 2026-08-14: `arxiv.org/abs/2503.20652`,
  `arxiv.org/html/2503.20652v6` (four extraction passes),
  `arxiv.org/html/2503.20652v1`, `ar5iv.labs.arxiv.org/html/2503.20652`.
- Tables in the paper (captions enumerated, v6): Table 1 "Quantitative
  evaluation on the CT-RATE and Rad-ChestCT test sets."; Table 2 "Comparison
  of performance across different modules."; Table 3 "Impact of the sliding
  window size."; Table 4 (Appendix A) "Baseline results with and without
  weight inflation from ImageNet-pretrained 2D models."
- The MIDL 2025 proceedings version was not extracted; the amendment pins the
  arXiv source. If the interpret stage ever cites the proceedings version,
  the table values must be re-verified there — this memo's quotes bind only
  to arXiv v6/v1.

**Next step (not this stage):** human ratification of this memo, then contract
v2 drafting as a separate stage.
