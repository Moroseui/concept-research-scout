# Interpretation — idea-047, clinical_profile_b

Private system interpret-build author draft; opposing-family review and human decision ratification pending. Authoring family: OpenAI/Codex (configured request `gpt-6-astra`); reviewing family: Anthropic/Claude (configured request `claude-fable-5`). These are configured identities, not independent provider attestations or a claim that review has completed.

## Evidence identity and scope

The governing contract is `dc586665d0bece940d1a1f4b3b0572f8c951c2ba`. Phase B follows the completed support/dictionary Phase A and answers only the clinical clause. Dataset: ISLES'24 training release, immutable Zenodo record `16813698`, archive MD5 `36ae28b9a17f7340b8bbef62b595cb57` [cite: resolved_config.json | archive | zenodo_record_declared, md5]. The primary output is the frozen aggregate clinical estimation table, with variable-specific coverage, deterministic omission sensitivity, hypothetical relabeling references, and the consumed support context.

**Citation binding:** every bundle-relative citation below resolves in `probes/047/results/results_v2-dc586665d0be` at import commit **`f9a45cf5cd202c403ec9677a7df8067da7cb2413`**, byte-identical to `940293b6d562f2d3dd6bfd9d8d8281ccf01e4783:probes/047/results_v2`. That full import commit applies to every claims-table row and every inline result citation. JSON selectors use dotted key paths; CSV selectors identify rows. Ranges in the compact contrast table are rounded to four decimal places when necessary; the cited `note` and uncertainty JSON retain full precision. No metric was regenerated.

## Layer A — Finding

The authorized clinical description completed for the frozen census, retaining all 99 cases with variable-specific missingness [cite: summary.json | root | status, analyzed_cases]. The disability median contrast was +1.5 scale points, while its rank-biserial contrast was 0.07072368421052631 and changed sign under head-case omission, so these summaries do not support a single clinical-separation verdict [cite: clinical_estimation_table.csv | construct=mrs_3month,item=contrast_diff_medians | contrast_value] [cite: clinical_estimation_table.csv | construct=mrs_3month,item=contrast_rank_biserial | contrast_value, note]. Admission severity and sex had small observed contrasts; later severity and age were less completely observed, and reperfusion and onset-to-door supplied no usable contrasts [cite: clinical_estimation_table.csv | construct=nihss_admission,item=contrast_smd_pooled | contrast_value] [cite: clinical_estimation_table.csv | construct=sex,item=contrast_diff_prop_F | contrast_value] [cite: summary.json | census | nihss_24h, age, mtici_postinterventional, onset_to_door]. The earlier support arithmetic remains 0.5063509495830807 of absolute contribution beside 0.08961200117675944 of eligible support, consumed unchanged rather than newly established here [cite: summary.json | support_constants_of_record | head_abs_contribution_share, head_support_share]. Confidence is limited to the recorded descriptive arithmetic: outcome-selected membership, field-dependent missingness and noninferential ranges prevent either clinical-silence claims or population conclusions.

## Layer B — Derivation narrative

### Gates and chronology

The contract's amendment consumed the completed support/dictionary phase; the executed configuration records its historical governing blob and exact constant checks [cite: resolved_config.json | consumed_phase_a | governing_blob, constants_recomputed_exactly, freeze_bindings_check]. The historical approval marker in `ideas/047/HUMAN_APPROVED_PROBE` binds the current scientific contract. `ideas/047/probe_review.md` records APPROVE after repair of the pre-access split freeze; it is a code review, not this interpretation's review. Historical Phase-A interpretations are preserved in `ideas/047/history/phase-a-before-supervised-b/` and do not count as a Phase-B interpretation.

For this supervised interpretation, `docs/science/047B_PRIVATE_ACCEPTANCE_APPROVED_20260908.json` records the operator's exact private acceptance decision. The import receipt `probes/047/results/results_v2-dc586665d0be.import.json` binds the original source, contract and manifest `56380f9fae381867df3b9b574e43efe653b96becfca17c5a4c6d8576f718d361`; import commit is the citation binding above. The later record-result transaction is `e11ce24075a56c3584a2421119d800adcecedc08`; registry ratification is `f8629f9b0abac8f311224306a39a26cccdf9c4ce`. The latter records historical Phase-A attestation, with both declared nodes COMPLETE in the resulting state. It does not ratify these new scientific conclusions. These direct receipts supersede dated pending-acceptance prose without rewriting it.

The recovered original sibling intake (`docs/science/047B_DRIVE_SIBLING_INTAKE_20260908.json`) binds the successful saved stream to the same source and summary. Its `exit_status` is null: correspondence and recorded completion are verified; an independently observed operating-system exit code is unavailable. No rerun is inferred or required to manufacture that evidence.

### Cohort flow and realized implementation

The executed split was predeclared as 10 head cases and 89 rest cases; 49 reserved cases were untouched [cite: run_log.txt | line beginning [split] | complete line]. The input tables each contain 99 rows, and the pipeline staged and parsed 198 phenotype members [cite: determinism_manifest_end.json | row_counts | per_case_contributions.csv, per_case_support.csv, staged_members] [cite: summary.json | root | phenotype_files_parsed]. No new patient was removed from the frozen analysis roster: its final size remains 99 [cite: summary.json | root | analyzed_cases]. Actual clinical denominators are smaller and differ by variable, as displayed below; this is not a complete-case analysis of the full roster.

The exclusions file must not be read as a list of newly excluded analyzed patients. Its `excluded_archive_lesion` row is inherited duplicate/noncanonical lesion bookkeeping, and its `excluded_case` row carries the inherited source-corrupt-member exclusion [cite: probe_exclusions.csv | record_type=excluded_archive_lesion | reason] [cite: probe_exclusions.csv | record_type=excluded_case | reason]. The 2 file anomalies are baseline and outcome files for the same census case, each rejected as multirow; they remove usable field observations rather than removing the case from the declared roster [cite: summary.json | root | file_anomalies] [cite: probe_exclusions.csv | record_type=file_anomaly_baseline | reason] [cite: probe_exclusions.csv | record_type=file_anomaly_outcome | reason]. No identifiers or reconstructed patient values are reproduced here.

The log records successful input pins, agreement with the frozen split, archive digest verification and staged-member size/CRC verification [cite: run_log.txt | lines beginning [identity] and [staging] | gate messages]. The minimum severity and demographic requirements both passed [cite: summary.json | minimum_set | severity_usable, demographic_usable]. Start/end determinism manifests are byte-identical on inspection; this proves stability of their declared inputs and configuration, not an independent repeat of the clinical computation. Analysis took 2.661 seconds; no wall-time stop occurred [cite: summary.json | root | analysis_seconds, status]. The only authorized variant was executed, with no GPU use [cite: resolved_config.json | root | variants, gpu_minutes]. The review does not authorize a replacement parser, new variable or second variant.

Low coverage was flagged rather than filtered away. The schema failure stop did not fire because the minimum set survived; it did not require every contextual variable to be usable. Small-cell handling and residual disclosure remain as recorded: 6 cells were suppressed, but margins and mandated contrasts can constrain suppressed counts [cite: summary.json | root | suppressed_cells, residual_disclosure]. Private retention is approved; this is not anonymization or public export clearance. No suppressed cell is reverse-engineered here.

## Layer C — Deep justification and claims table

### Complete coverage account

Every numerical cell in each row is supported by the indicated census row and by the common results commit stated above. Empty, parse-failed and unresolved counts are kept distinct; missingness is not evidence that the biological quantity is absent.

| Bound construct | Usable head / rest | Empty head / rest | Parse failure head / rest | Unresolved head / rest | Interpretation and exact citation |
|---|---:|---:|---:|---:|---|
| mRS at three months | 8 / 76 | 2 / 12 | 0 / 0 | 0 / 1 | Resolved; [cite: phenotype_schema_census.csv | construct=mrs_3month | head_nonmissing, rest_nonmissing, head_empty, rest_empty, head_parse_failures, rest_parse_failures, head_unresolved, rest_unresolved] |
| NIHSS at 24 hours | 4 / 54 | 6 / 34 | 0 / 0 | 0 / 1 | Insufficient head coverage; [cite: phenotype_schema_census.csv | construct=nihss_24h | head_nonmissing, rest_nonmissing, head_empty, rest_empty, head_parse_failures, rest_parse_failures, head_unresolved, rest_unresolved, insufficient_head_coverage] |
| Admission NIHSS | 10 / 86 | 0 / 2 | 0 / 0 | 0 / 1 | Resolved; [cite: phenotype_schema_census.csv | construct=nihss_admission | head_nonmissing, rest_nonmissing, head_empty, rest_empty, head_parse_failures, rest_parse_failures, head_unresolved, rest_unresolved] |
| Age | 6 / 64 | 0 / 0 | 4 / 24 | 0 / 1 | Insufficient head coverage; notably parse attrition, not blank ages; [cite: phenotype_schema_census.csv | construct=age | head_nonmissing, rest_nonmissing, head_empty, rest_empty, head_parse_failures, rest_parse_failures, head_unresolved, rest_unresolved, insufficient_head_coverage] |
| Sex | 10 / 87 | 0 / 0 | 0 / 1 | 0 / 1 | Frozen reference is F; [cite: phenotype_schema_census.csv | construct=sex | head_nonmissing, rest_nonmissing, head_empty, rest_empty, head_parse_failures, rest_parse_failures, head_unresolved, rest_unresolved] |
| Postinterventional mTici | 0 / 0 | 0 / 0 | 0 / 0 | 10 / 89 | Bound spelling unresolved; not proof that no reperfusion information exists elsewhere; [cite: phenotype_schema_census.csv | construct=mtici_postinterventional | head_nonmissing, rest_nonmissing, head_empty, rest_empty, head_parse_failures, rest_parse_failures, head_unresolved, rest_unresolved, resolved] |
| Onset to door | 0 / 0 | 10 / 88 | 0 / 0 | 0 / 1 | Header resolves, but no usable duration; [cite: phenotype_schema_census.csv | construct=onset_to_door | head_nonmissing, rest_nonmissing, head_empty, rest_empty, head_parse_failures, rest_parse_failures, head_unresolved, rest_unresolved, resolved] |

Center is undocumented in the bound dictionary, not demonstrated absent from all possible dataset sources [cite: summary.json | root | center_documented]. The age census additionally records 70 decimal-normalized values; that bookkeeping does not recover the parse failures or license a recode [cite: phenotype_schema_census.csv | construct=age | decimal_normalized_values]. This interpretation does not diagnose the original patient values.

### All authorized contrasts and both displays

All contrasts are head minus rest; rank-biserial uses the corresponding head-versus-rest ordering. **LOO** means deterministic leave-one-head-case-out sensitivity. **Reference** means the central hypothetical exchangeability reference, **not a confidence interval and not sampling inference**. The table is joint reporting, not a ranking by apparent extremity. For each row, `contrast_value` supplies the point and `note` supplies both ranges; full-precision equivalents are in `clinical_uncertainty.json` under `constructs.<construct>.contrasts.<contrast>`.

| Construct / contrast | Point | LOO min to max | Hypothetical reference | Exact citation (common results commit above) |
|---|---:|---|---|---|
| mRS / median difference | 1.5 | 0.0 to 3.0 | -2.0 to 3.0 | [cite: clinical_estimation_table.csv | construct=mrs_3month,item=contrast_diff_medians | contrast_value, note] |
| mRS / rank-biserial | 0.0707 | -0.0432 to 0.1786 | -0.4074 to 0.4014 | [cite: clinical_estimation_table.csv | construct=mrs_3month,item=contrast_rank_biserial | contrast_value, note] |
| Later NIHSS / pooled SMD | 0.2520 | -0.2358 to 0.6182 | -0.8064 to 0.9762 | [cite: clinical_estimation_table.csv | construct=nihss_24h,item=contrast_smd_pooled | contrast_value, note] |
| Later NIHSS / median difference | 2.5 | 0.5 to 4.5 | -4.0 to 8.5 | [cite: clinical_estimation_table.csv | construct=nihss_24h,item=contrast_diff_medians | contrast_value, note] |
| Admission NIHSS / pooled SMD | 0.0845 | -0.1191 to 0.2534 | -0.6513 to 0.6675 | [cite: clinical_estimation_table.csv | construct=nihss_admission,item=contrast_smd_pooled | contrast_value, note] |
| Admission NIHSS / median difference | 0.5 | -2.0 to 3.0 | -5.5 to 7.5 | [cite: clinical_estimation_table.csv | construct=nihss_admission,item=contrast_diff_medians | contrast_value, note] |
| Age / pooled SMD | -0.3901 | -0.6286 to -0.1220 | -0.8988 to 0.7381 | [cite: clinical_estimation_table.csv | construct=age,item=contrast_smd_pooled | contrast_value, note] |
| Age / median difference | -10.0 | -20.0 to 0.0 | -16.5 to 7.0 | [cite: clinical_estimation_table.csv | construct=age,item=contrast_diff_medians | contrast_value, note] |
| Sex / difference in proportion F | 0.0172 | -0.0383 to 0.0728 | -0.3172 to 0.3517 | [cite: clinical_estimation_table.csv | construct=sex,item=contrast_diff_prop_F | contrast_value, note] |
| mTici / ordinal contrasts | Undefined | Unavailable | Unavailable | [cite: clinical_uncertainty.json | constructs.mtici_postinterventional | resolved, note] |
| Onset to door / pooled SMD | Undefined | Undefined | Undefined | [cite: clinical_uncertainty.json | constructs.onset_to_door.contrasts.smd_pooled | point, loo, relabeling] |
| Onset to door / median difference | Undefined | Undefined | Undefined | [cite: clinical_uncertainty.json | constructs.onset_to_door.contrasts.diff_medians | point, loo, relabeling] |

The later-NIHSS SMD reference has 9987 defined draws out of 10000 attempted, a disclosed undefined-statistic limitation rather than an additional variant [cite: clinical_uncertainty.json | constructs.nihss_24h.contrasts.smd_pooled.relabeling | n_defined, n_relabelings]. Onset-to-door remains undefined in both displays; its empty ranges must not be rendered as zero effects. The retained estimation table also supplies the authorized group means, SDs, medians, quartiles and suppressed level/cumulative distributions; this interpretation does not add new aggregations or infer hidden counts.

### Joint support context, consumed rather than retested

| Claim | Value | Exact citation (common results commit above) |
|---|---|---|
| Absolute contribution share / eligible support share of frozen head | 0.5063509495830807 / 0.08961200117675944 | [cite: summary.json | support_constants_of_record | head_abs_contribution_share, head_support_share] |
| Full-group eligible-support medians, head / rest, voxels | 113052.0 / 218189.0 | [cite: clinical_estimation_table.csv | construct=_context,item=context_support_shares | head_support_median, rest_support_median] |
| Net signed reversal accounting share, cancellation-sensitive | 0.7928912778985707 | [cite: summary.json | support_constants_of_record | signed_head_net_gap_share, labels.signed_head_net_gap_share] |

The support medians accompany every variable as full-group context; they are not variable-complete-case support estimates, an adjustment, or a test of mediation. The share contrast describes additive totals in different currencies and does not quantify a causal explanation of clinical differences. The signed accounting share is never compared with support as contribution per unit territory.

### Where uncertainty actually lives

The clinical point estimates and omission sensitivity are deterministic functions of the frozen cohort and parser. Their limitation is outcome-selected case membership, incomplete observations and measurement/parse conventions, not training-seed variability. The random component is only the hypothetical reference: seed 20260902 and 10000 relabelings over a shared draw set [cite: clinical_uncertainty.json | root | seed, n_relabelings, draw_rule]. A single reference seed neither weakens exact census arithmetic into a training result nor supplies population inference; repeating seeds would assess only Monte Carlo stability of this hypothetical display.

LOO describes perturbation of observed head membership; it does not recover missing clinical values, model the original head-selection procedure, or cover other patients. A hypothetical reference describes arbitrary relabeling under exchangeability that this design does not establish. Consequently neither display can exclude unobserved population effects or define a clinically meaningful null. The contract's permitted bounded-null wording is not required: here it would risk suggesting an exclusion bound these displays cannot provide. We instead report the actual estimates, their sensitivity and unavailable fields directly.

### Demonstrates / suggests / does not establish

**Demonstrates (verified descriptive facts):** the accepted source-bound pipeline completed its registered table; the field-resolution and coverage facts, and the tabulated point estimates, hold for the recorded usable observations under the frozen parser. The imported support constants remain exact arithmetic of record. This is exploratory description, not a confirmatory effect finding.

**Suggests (source-supported interpretation):** the clinical picture depends on the summary and field. The primary disability median and rank summary should be read together; the latter's omission range crosses sign. The younger observed age profile is particularly exposed to parse-related missingness. These observations can motivate a separately scoped missingness/measurement question, but do not establish a clinical subgroup or why the head dominates.

**Does not establish:** clinical silence or markedness, equivalence, a clinical subtype, causal mediation by territory or treatment, prognostic utility, model use, generalization beyond this realized census, or novelty. No patient-level inference, significance-selected highlight, new support statistic, or unpublished-dataset-category claim is made. No literature-dependent novelty or medical recommendation is needed for this within-contract interpretation.

### Validity failures; positive and negative findings

No new invalidating scientific failure is identified in the accepted bundle. The field anomalies and parser attrition were recorded, and minimum-set survival explicitly permits incomplete rows; they are limitations, not grounds to reinterpret STUDY_COMPLETE as a failure or a negative. Recorded determinism is limited to the manifest check described above. Console correspondence does not provide an independent process-exit attestation.

The positive finding is successful completion of the registered descriptive object, with actual clinical coverage now known. Negative-direction estimates, such as the age contrast, describe observed direction only. There is **no registered directional negative outcome**. Missing contextual contrasts are unavailable evidence, not evidence of no relationship. Suppression is cell-level only; the private metadata disposition does not solve residual inference risk for publication.

## Next decision

Recommend **PAUSE** after opposing-family review and operator ratification: the authorized clinical-description question has been answered to its attainable scope, and this contract is spent. PAUSE means no active further experiment under this idea; it is not a rejection of the lineage or a clinical-null decision. Preserve all original and failed evidence, the complete variable table and the historical Phase-A record. Do not append a decision-ledger entry in this first author round.

Any investigation of alternate field spellings, rejected age values, missingness mechanisms, or a new cohort belongs in a separately reviewed and approved specification; no recoding or reserved-case read follows automatically. Any successor selection must use the system route. Public export and final scientific ratification remain separate operator decisions, and independent prediction work need not wait on this descriptive lifecycle.

PAUSE
