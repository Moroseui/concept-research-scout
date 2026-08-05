FATAL OBJECTION: The released reads are neither independent nor attributable to stable readers, so they cannot supply the repeated, separable “methods” required for the proposed MTMM claim.
EVIDENCE: TCIA LIDC-IDRI collection notes, “Reader Annotation and Markup,” item 2; Armato et al. 2011 acquisition protocol; Campbell & Fiske 1959, pp. 81–82.
REPAIRABLE WITHOUT CHANGING THE QUESTION? NO
DECISION: PAUSE

# Adversarial review

## Bottom line

The descriptive question—how redundant are the released LIDC semantic ratings?—is cheap and potentially useful. The stronger question in the card—do the eight named characteristics possess discriminant construct validity by a multitrait-multimethod (MTMM) test?—is not answered by these data.

This is not a small reader-slot implementation problem. It is a mismatch between the validation design and the provenance of the labels. Campbell and Fiske define convergent validation as confirmation by **independent measurement procedures** and require every trait to be measured by multiple methods (DOI [10.1037/h0046016](https://doi.org/10.1037/h0046016), PMID 13634291; primary text inspected through the publisher preview). LIDC supplies multiple opinions, but the released opinions are from the unblinded phase, after readers could see other readers' marks, and TCIA explicitly warns that reader order is not a persistent identity across scans. Consequently, “reader 1–4” cannot be treated as four stable method factors, while exchangeable readers who have been exposed to peers are not independent methods either.

The idea card calls peer exposure a conservative bias because it may inflate same-characteristic cross-reader agreement. That is only one path. Exposure can also inflate different-characteristic/different-reader correlations: another reader's spiculation mark, contour, or global suspicion can alter a reader's lobulation, margin, subtlety, or texture judgment. Thus the proposed family-(c) cells do **not** rule out within-session social/halo propagation. A positive “three dimensions” result would remain compatible with biological covariance, a common malignancy impression, shared visual cues, scale design, and peer-induced dependence. The advertised main identifying move fails.

## Verified dataset limitations

- **Verified fact:** TCIA states that XML reader positions cannot be compared across cases: the first reader in one scan need not be the same radiologist as the first reader in another. It also documents inconsistent spiculation and lobulation rating systems for roughly 100 of the initial 399 cases, a corrected scale-ordering note, two XMLs with omitted characteristics, and an invalid internal-structure value. See the official [LIDC-IDRI collection page](https://wiki.cancerimagingarchive.net/pages/viewpage.action?navigatingVersions=true&pageId=133072843), “Reader Annotation and Markup,” items 1–7.
- **Verified fact:** Armato et al. describe a blinded read followed by an unblinded read in which each radiologist reviewed the other radiologists' marks; the public database retained each radiologist's final lesion designation and marks. See Armato et al., *Medical Physics* 2011, DOI [10.1118/1.3528204](https://doi.org/10.1118/1.3528204), PMCID PMC3041807.
- **Source-supported interpretation:** those facts allow per-nodule inter-opinion summaries but not a classical stable-rater MTMM decomposition across nodules. A random-rater/generalizability model could estimate components under assumptions, but it cannot restore hidden identity or independence lost during collection.
- **Verified fact:** the released characteristics are not eight homogeneous ordinal scales. Internal structure encodes types such as soft tissue, fluid, fat, and air; calcification encodes patterns/presence categories. Treating both as ordered continuous latent responses in a polychoric matrix is scientifically questionable. The 2023 grading paper itself shows extreme concentration (3075 of 3091 internal-structure ratings at level 1) and remaps heterogeneous scales before analysis; see Zhang et al., DOI [10.1186/s12880-023-01112-4](https://doi.org/10.1186/s12880-023-01112-4), PMID 37833636, Table 2 and Methods.

The keystone should therefore be split. “Multiple characteristics and multiple final opinions exist for the same lesion” is inspected true. “Those opinions instantiate multiple usable methods for MTMM construct validation” is inspected false. The latter is the real keystone for the stated study.

## Endpoint and interpretation problems

“How many dimensions?” does not have a unique answer without fixing the estimand. A factor count can change with (i) individual versus consensus ratings, (ii) inclusion of malignancy, internal structure, and calcification, (iii) mixed ordinal/nominal association measures, (iv) treatment of clustered ratings and missingness, (v) the historically inconsistent cases, and (vi) factor-retention rule. Parallel analysis plus bootstrap intervals quantifies sampling uncertainty but not this specification uncertainty.

Nor does fewer than eight factors imply that eight concept predictions or interventions are meaningless. Correlated clinical attributes may still be separately observable and separately actionable; dimensionality is a property of their distribution in this sampled nodule population, not a count of ontologically real concepts or intervention handles. Conversely, retaining nearly eight factors would not validate the vocabulary: factor retention is not evidence of content validity, criterion validity, or clinical utility. The original negative-result claim is therefore overstated in both directions.

The most defensible endpoint is descriptive and distribution-specific: a preregistered redundancy profile, not a pass/fail declaration of construct validity. Report pairwise mixed-scale associations, conditional associations, response distributions, and stability across defensible preprocessing choices. Do not translate a factor count into “the vocabulary actually has N concepts.”

## Prior-work overlap and novelty confidence

The exact MTMM analysis was not located in the searches performed, but absence was not established and novelty should remain at 3 or below. Nearby work already consumes much of the easy claim:

- Zhang et al. analyze all eight LIDC characteristics and their association with malignancy and publish the rating distributions (DOI [10.1186/s12880-023-01112-4](https://doi.org/10.1186/s12880-023-01112-4)). Their analysis is not an MTMM validity test, but it makes “the ratings are correlated/degenerate” alone incremental.
- Hancock and Magnan show that radiologist-quantified LIDC features jointly predict malignancy strongly, making global suspicion/circularity a live alternative rather than an incidental caveat (DOI [10.1117/1.JMI.3.4.044504](https://doi.org/10.1117/1.JMI.3.4.044504), PMCID PMC5146644).
- The LIDC/RadLex mapping work already reports high uncertainty and low agreement when semantic characteristics are mapped to image content (PMCID [PMC3056962](https://pmc.ncbi.nlm.nih.gov/articles/PMC3056962/)). It does not estimate redundancy, but weakens any claim that vocabulary validation is untouched territory.

A systematic search of observer-performance, psychometrics, *Academic Radiology*, and lexicon-validation literature is still required before any novelty statement. The current result is only: **no exact match was found in this bounded search**.

## Circularity, confounding, and medical relevance

The ratings are simultaneous subjective judgments from the same image and session. A global malignancy impression can drive multiple descriptors even when malignancy itself is excluded from the matrix. Excluding the malignancy variable does not remove this latent common-cause pathway. Nodule size, reconstruction thickness, conspicuity, solid/subsolid status, and prevalence spectrum can also induce correlations. Conditioning on observable image/nodule variables would help characterize these pathways, but no analysis of LIDC alone can decide whether residual covariance is semantic redundancy or genuine morphology.

Medical relevance is moderate only if the result changes a concrete use: label selection for a model, reporting uncertainty, or interpretation of correlated concept metrics. Claims about structured clinical reporting are weak because the LIDC research scales are not themselves a current clinical reporting standard, and the final unblinded ratings are not representative independent clinical reads. The work should target evaluation practice in LIDC-based concept models, not clinical vocabulary redesign.

Compute and access are not objections: XML-only analysis is public and CPU-scale. Data provenance and estimand validity are the objections.

## Negative-result value

Under the original design, either outcome is ambiguous:

- A low-dimensional result cannot distinguish biological co-occurrence, global suspicion, peer exposure, scale degeneracy, prevalence restriction, or redundant constructs.
- A near-eight-dimensional result does not establish construct validity and may arise from noise or mixed measurement levels.

The anticipated negative must therefore be reclassified from **decisive** to **uninterpretable** for the MTMM claim, capping negative-result value at 2 under the rubric. For the narrower descriptive audit, either outcome is useful: strong stable redundancy warns against treating per-concept metrics as independent evidence; weak redundancy prevents an unsupported redundancy critique. That is a different, modest claim.

## Easier low-hanging-fruit formulation

Use an existing parsed LIDC annotation table (pylidc is linked by TCIA and described by Hancock & Magnan) and ask: **How much does the apparent redundancy among LIDC descriptor labels change across three common label-construction choices—individual final ratings, median/majority consensus, and exclusion of known problematic or degenerate characteristics?**

This needs no images, stable reader IDs, model, checkpoint, or factor model. The predeclared outputs can be:

1. per-characteristic response and missingness distributions;
2. a mixed-scale association matrix with lesion-clustered bootstrap intervals;
3. effective-rank or variance-summary estimates explicitly labeled descriptive;
4. a specification curve over consensus rule, four-reader restriction, exclusion of the approximately 100 historically inconsistent cases where identifiable, and removal of internal structure/calcification;
5. the change in multiplicity-adjusted information conveyed by eight separate reported metrics versus grouped metrics.

This is low-hanging fruit because the public XML, official schema/documentation, pylidc parser, and published marginal counts already exist. No suitable pretrained checkpoint is needed because model behavior is not the estimand. Its value is a reproducible sensitivity audit showing whether the “eight concepts” framing is robust to label construction. It does **not** validate constructs or identify why correlations occur.

Before advancing even that version, directly inspect the current XML/schema and count usable cells; verify whether the problematic pilot cases can be identified reproducibly; and complete the systematic prior-work search. These are analysis planning and literature tasks, not probe-code authorization.

NEAREST DEFENSIBLE HIGH-VALUE QUESTION: How robust is the apparent redundancy of the eight released LIDC descriptor labels to reader aggregation, mixed measurement scales, degenerate characteristics, and documented annotation inconsistencies?
RETAINS ORIGINAL MEDICAL MOTIVATION? PARTLY
SHOULD IT BECOME A SEPARATE CANDIDATE? YES
IS IT ACTUALLY WORTH DOING? Yes—if framed as a label-construction sensitivity audit for LIDC-based concept-model evaluation, because it can cheaply reveal whether eight routinely reported concept metrics represent stable distinct information; it is not worth doing as a claim that the clinical vocabulary has a true latent dimension count.
