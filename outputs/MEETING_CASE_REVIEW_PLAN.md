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

The inspected inventories establish CT, perfusion, reference labels and saved model outputs. They do not yet establish follow-up MRI or clinical provenance. The existing Drive service now passed a read-only metadata request with its credential unchanged, but returned no visible folder named isles-pilot. This establishes limited visibility through that route, not absence of the project or MRI files. No cases or images have been selected. Clinical values must have sources, units, missingness and admission-versus-retrospective timing; none may be inferred.

The next result is a scientifically reviewed synthetic selector/renderer, estimated one author/reviewer cycle after ordinary admission is ready. The four existing meeting calls remain unused. A reliable date for real panels depends on MRI/clinical source availability and geometry checks. Existing server CPU and private access are the planned venue; no new paid compute or credentials are proposed.

This page summarizes the accepted scientific proposal and operator logistics. It does not authorize real-case execution or publication.
