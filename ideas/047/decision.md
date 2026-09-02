# Decision — idea 047, Phase A

## Result card

- **Idea:** idea-047
- **Probe and sequence position:** probe 047, contract v2, Phase A of the planned two-phase experiment; phenotype-blind support/provenance and dictionary phase, before amendment and Phase B.
- **Dataset and pin:** ISLES'24 training release, immutable Zenodo record 16813698; Phase A used frozen imported tables and the pinned clinical dictionary only.
- **Primary metric:** frozen top-ten share of total absolute contribution beside frozen top-ten share of total eligible deficit support across the realized 99 cases.
- **Contract blob:** `b4887c05a21bfe870589b5d9982066943df679d5`
- **Results-bundle commit:** `6037f24122766fe1c68f16eb9f38d9a16c2c5e66`
- **Authoring family:** Codex. **Reviewing family:** Claude (pending).
- **Out of scope:** no clinical comparison, clinical-silence/markedness verdict, keystone classification, causal or model-use claim, per-patient clinical claim, or generalization beyond these 99 cases. Phase B is not authorized by this document.

## Layer A — Finding

The frozen top ten carry 50.63509495830807% of total absolute contribution and 8.961200117675944% of eligible support in the realized 99-case cohort [cite: support_shares.json | sole_disproportionality_comparison | head_abs_contribution_share,head_support_share | bundle_commit=6037f24122766fe1c68f16eb9f38d9a16c2c5e66].
The all-case descriptive rank association is small, rho 0.07085961657390227, without an interval or sampling claim [cite: support_shares.json | descriptive_displays | spearman_rho_abs_contribution_vs_support | bundle_commit=6037f24122766fe1c68f16eb9f38d9a16c2c5e66].
The separate 79.28912778985707% signed share is net-reversal accounting after cancellation, not contribution per unit support [cite: support_shares.json | reversal_accounting | signed_head_net_gap_share | bundle_commit=6037f24122766fe1c68f16eb9f38d9a16c2c5e66].
The clinical dictionary passed the minimum schema gate, but zero phenotype rows were opened, so no clinical conclusion exists yet [cite: summary.json | clinical_minimum_set_supported=true,phenotype_rows_opened=0 | bundle_commit=6037f24122766fe1c68f16eb9f38d9a16c2c5e66].
The main caveat is finite-population, outcome-selected scope: the arithmetic is exact for these cases but does not establish recurrence or explanation.

## Layer B — Derivation narrative

The human-approved contract and two-round cross-family code review preceded one deterministic authorized Phase-A variant. The provenance flow was 101 exclusions-table records in, two bookkeeping records excluded (`sub-stroke0142` duplicate/noncanonical lesion bookkeeping and `sub-stroke0043` source-corrupt case), and 99 unique cases analyzed with an exact contribution-table ID match [cite: provenance_gate.json | analyzed_rows=99,bookkeeping_rows,unique_analyzed_ids=true,id_set_matches_contribution_table=true | bundle_commit=6037f24122766fe1c68f16eb9f38d9a16c2c5e66]. All 99 support counts were finite positive integers, all frozen census cross-checks passed, and no discrepancy was recorded [cite: provenance_gate.json | b_finite_positive_integer_count=99,census_cross_checks.checks,pass=true,discrepancies=[] | bundle_commit=6037f24122766fe1c68f16eb9f38d9a16c2c5e66]. The authorized support arithmetic used 0.04367036086720666 of 0.08624524334982282 absolute contribution and 2,025,630 of 22,604,450 support voxels for the frozen head [cite: support_shares.json | sole_disproportionality_comparison | head_abs_contribution_sum,total_abs_contribution_sum,head_support_voxels,total_support_voxels | bundle_commit=6037f24122766fe1c68f16eb9f38d9a16c2c5e66]. The dictionary inventory documented the proposed clinical constructs without opening a phenotype row, and Phase A reached `PHASE_A_COMPLETE_REQUIRES_AMENDMENT`; neither preregistered stop fired [cite: proposed_variable_freeze.json | constructs,minimum_set.supported=true | bundle_commit=6037f24122766fe1c68f16eb9f38d9a16c2c5e66] [cite: summary.json | phenotype_rows_opened=0,status=PHASE_A_COMPLETE_REQUIRES_AMENDMENT | bundle_commit=6037f24122766fe1c68f16eb9f38d9a16c2c5e66].

## Layer C — Deep justification

| Class | Decision-grade claim | Exact source |
|---|---|---|
| Demonstrates | Exact finite-population concentration: absolute-contribution share 0.5063509495830807 versus support share 0.08961200117675944. | [cite: support_shares.json | sole_disproportionality_comparison | head_abs_contribution_share,head_support_share | bundle_commit=6037f24122766fe1c68f16eb9f38d9a16c2c5e66] |
| Suggests | Eligible-support quantity alone does not describe the realized concentration well; this is only suggestive because there is no case-level sampling uncertainty and the subgroup was selected from the same census. | [cite: support_shares.json | sole_disproportionality_comparison | head_abs_contribution_share,head_support_share | bundle_commit=6037f24122766fe1c68f16eb9f38d9a16c2c5e66] [cite: support_shares.json | descriptive_displays | spearman_rho_abs_contribution_vs_support | bundle_commit=6037f24122766fe1c68f16eb9f38d9a16c2c5e66] |
| Positive finding | Phase A completed its preregistered successful terminal with the provenance and minimum-schema gates passed. | [cite: provenance_gate.json | pass=true | bundle_commit=6037f24122766fe1c68f16eb9f38d9a16c2c5e66] [cite: summary.json | clinical_minimum_set_supported=true,status=PHASE_A_COMPLETE_REQUIRES_AMENDMENT | bundle_commit=6037f24122766fe1c68f16eb9f38d9a16c2c5e66] |
| Negative finding | The descriptive rho is 0.07085961657390227; it is not an inferential null or evidence of independence. | [cite: support_shares.json | descriptive_displays | spearman_rho_abs_contribution_vs_support | bundle_commit=6037f24122766fe1c68f16eb9f38d9a16c2c5e66] |
| Does not establish | Any clinical association or absence of one: phenotype rows opened = 0. | [cite: summary.json | phenotype_rows_opened=0 | bundle_commit=6037f24122766fe1c68f16eb9f38d9a16c2c5e66] |
| Validity failures | None observed; the provenance gate passed with no discrepancies, and the clinical schema was supported. | [cite: provenance_gate.json | pass=true,discrepancies=[] | bundle_commit=6037f24122766fe1c68f16eb9f38d9a16c2c5e66] [cite: summary.json | clinical_minimum_set_supported=true | bundle_commit=6037f24122766fe1c68f16eb9f38d9a16c2c5e66] |

The procedure was deterministic. Seed uncertainty does not apply to Phase-A arithmetic; uncertainty lies in case selection and external scope. Therefore exact cohort arithmetic is demonstrated, while broader effect language is not.

## Next decision

**ADVANCE — narrowly to the Phase-B contract amendment and fresh human approval.** Bind the dictionary-derived variable list and Phase-A artifact hashes, replace the required-output interface, register Phase A as a consumed artifact, and do not stage or read phenotype bytes until the amended blob is approved. This does not authorize execution and does not complete idea 047.
