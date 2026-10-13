# Private meeting case review: production plan

The intended deliverable is a private local HTML/PDF showing admission CT, follow-up MRI, reference mask, model predictions and sourced clinical context. Patient panels and identifiers stay outside this public repository.

The accepted scientific proposal fixes six slots before images are viewed: three infarct-size groups, each split by positive versus negative saved fusion-minus-tree difference at equal predicted amount. Use the exact accepted median, tie and fallback rules; empty or exhausted slots remain blank. This deliberately selected sample illustrates contrasts and cannot estimate prevalence or efficacy. Only the frozen99development patients are eligible, with out-of-fold provenance and excluded49membership checks.

| Step | Owner | Evidence needed |
|---|---|---|
| Confirm source availability | Operator | Allowed input references, hashes, MRI/clinical provenance and missingness |
| Implement selector and renderer | Scientific author | Exact accepted rule, synthetic fixtures, geometry checks and fixed displays |
| Review before case selection | Scientific reviewer | Selection, geometry, missing-asset handling and interpretation limits |
| Produce private panels | Reviewed server CPU execution | Native and registered views, model/output hashes, recorded fallback reasons |
| Package for the meeting | Operator | Private HTML/PDF and separate private identifier map |

Meeting preparation retains the accepted six-slot rule, fixed before image inspection. A metadata-only check of the exact 99 development directories found DWI and ADC entries for all99 in the existing source-extract derivatives. Frozen cohort and exclusion metadata hashes were verified; no excluded directory or image payload was opened. This establishes directory availability, not MRI file hashes, geometry or clinical provenance. Those checks and a reviewed selector/renderer are still needed; no cases or images have been selected. Do not hydrate MRI through the laptop. Use the existing authorized private route after review. Four meeting calls remain unused. Clinical values must have sources, units, missingness and admission-versus-retrospective timing; none may be inferred. Public dataset documentation describes follow-up MRI and clinical data, but does not prove identity or completeness of this local extract. [Dataset paper](https://arxiv.org/abs/2408.11142v2).

The next result is a scientifically reviewed synthetic selector/renderer, estimated one author/reviewer cycle after ordinary admission is ready. The four existing meeting calls remain unused. A reliable date for real panels depends on MRI/clinical source availability and geometry checks. Existing server CPU and private access are the planned venue; no new paid compute or credentials are proposed.

This page summarizes the accepted scientific proposal and operator logistics. It does not authorize real-case execution or publication.

13October update: the accepted author proposal and its independent review were reverified against server originals, and the selection wording is bound verbatim for authoring. MRI directory filenames explicitly identify CT-space derivatives; native-space MRI remains unresolved. The existing scientific program validator and isolated synthetic runner are the intended reuse points. A meeting-only admission adapter is still required to use the four allocated calls; no adapter or patient execution is installed. The administrative direction attempt answered an earlier L patch instead of this routing question, so it supplies no meeting approval.
