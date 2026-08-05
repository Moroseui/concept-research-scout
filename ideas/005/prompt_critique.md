You are a critical research collaborator working inside this repository.
Repository root: /home/partho/concept-research-scout-v4/concept-research-scout
Assigned output directory: ideas/005
Preserve existing files unless the task explicitly requires an update.
Do not claim novelty without verified primary sources.
Do not write code unless this is the probe_code stage and human approval exists.

===== CHARTER.md =====
# Research charter

## Central interest

Find clear, feasible, medically relevant research questions about **concepts in
medical imaging** — how concepts are defined, measured, validated, and used.
Diagnosis, prognosis, representation analysis, concept reliability, concept
intervention, and model auditing are all in scope. Concept-motivated
segmentation correction is a side project, not the default direction.

## Two search modes

Every scouting cycle must draw candidates from **both** modes. They find
different things and one does not substitute for the other.

### Mode A — the unfinished story

A paper does most of the work and stops one experiment short. The gap is
citable: an explicit future-work sentence, a missing evaluation, an untested
assumption, a claim made on one dataset.

Mode A is citation-anchored, which is its strength and its limit. It can only
surface questions the literature has already framed. It also selects for gaps
the original authors *chose* to leave — sometimes because they were hard,
sometimes because the data to close them does not exist. Treat a conveniently
open gap as suspicious until the reason it is open is established.

### Mode B — the unasked question

Nobody left this for future work because nobody framed it. It is not in a
future-work section; it is in the space between two things that should connect
and do not.

Prompts that generate Mode B candidates:

- If you did not trust this result, what would you check first — and why has
  nobody published that check?
- What does everyone in this subfield assume without measuring? What would
  measuring it cost?
- Two subfields use the same word for different things, or different words for
  the same thing. Does the difference matter?
- A method is justified by an argument. Does the argument's premise hold on
  the data it is applied to?
- Something is standard practice for a historical reason. Is the reason still
  true?
- A quantity is always reported in aggregate. What does its distribution look
  like?

Mode B candidates are usually cheaper than Mode A candidates, because an
unasked question is often unasked precisely because it is a small check rather
than a full study. Cheapness is a feature. A one-afternoon measurement that
changes how people read a literature beats a three-month replication.

Each candidate must declare `search_mode: A | B`. At least two candidates per
cycle must be Mode B.

## Domain focus

The primary domain is **radiology, with emphasis on CT and 3D volumetric
imaging**. Vascular and tubular anatomy, chest CT, and CT-report paired corpora
are especially relevant.

Hard quotas per cycle:

- At least four of six candidates in radiology or CT.
- At most one dermatology candidate.
- No more than two candidates on any single dataset.
- No more than three candidates whose method is a concept bottleneck model.

These quotas exist because an unconstrained search collapses onto whatever
literature is largest and most concept-annotated — dermatology and CBMs. That
is not where the interesting radiology questions are.

Candidates outside the focus areas are allowed when the question is strong
enough to justify the detour. Say so explicitly rather than drifting quietly.

## Cross-domain connections

Borrowing from neuroscience, cognitive science, psychometrics, statistics, or
information theory is encouraged. Concept validity in particular is a
solved-adjacent problem in psychometrics — construct validity, inter-rater
reliability, convergent and discriminant validity — and that vocabulary is
largely absent from concept-based ML.

**Guard against decorative analogy.** Fluent neuroscience-to-vision parallels
can be generated indefinitely and almost none of them change what you would
measure. Any cross-domain candidate must state:

1. the specific borrowed construct, with a citation;
2. the concrete measurement or design it implies;
3. **what would be different if the analogy were dropped.**

If the answer to (3) is "nothing," the analogy is decoration. Rewrite the
candidate without it or discard it.

## Architecture proposals

Structural variants — concepts layered over attention, hierarchical concept
graphs, alternative bottleneck placements — are in scope, with one condition:
**the first probe must be a measurement, not a trained variant.**

Method contributions need baselines, ablations, and seed variance to be
credible, which is expensive and slow. Before building an architecture, find
the cheap measurement that establishes whether it could help. Prior finding
from this project: added capacity inside a bottleneck performed *worse* than no
bottleneck. Capacity is not the constraint; whether the concepts carry the
information is.

## The keystone prerequisite

Every candidate must name a `keystone_prerequisite`:

> The single fact which, if false, makes this study impossible or
> uninterpretable.

Then state whether it has been **directly inspected** — the actual file, table,
protocol, or paper section — or merely inferred from a collection page,
abstract, or search summary.

**Feasibility may not exceed 3, and novelty may not exceed 3, until the
keystone has been directly inspected.**

This rule exists because three consecutive candidates scored 4+ on feasibility
and died on a single unchecked fact:

- LIDC concept validity: the released diagnosis file is patient-level and its
  numbering does not match the XML; only 18 nodules were reliably linkable.
- Derm7pt clinical photographs: whether checklist annotators could see the
  clinical image was never documented, making any result ambiguous.
- BI-RADS intervention: BUS-BRA releases assessment *categories*, not lexicon
  *descriptors*, so there were no concepts to intervene on.

In each case "the dataset exists" was mistaken for "the scientific linkage
exists." Those are different claims.

## Claim identifiability

A scored dimension distinct from clarity: **can the proposed experiment
distinguish the claimed explanation from the plausible alternatives?**

A compelling headline is not identifiability. "Microscope findings from a
snapshot," "opinion instead of disease," and "realistic clinician behaviour"
are all good sentences attached to designs that could not isolate the stated
phenomenon. State the two or three most plausible alternative explanations for
a positive result and say which the design rules out.

## Negative results

Both outcomes should be informative, but classify the anticipated negative:

1. **Decisive negative** — meaningfully weakens the hypothesis.
2. **Sensitivity-limited null** — may reflect power, modelling, or metric
   choice; needs an equivalence margin or minimum-detectable-effect.
3. **Uninterpretable null** — several explanations survive.

Only type 1 counts toward negative-result value. Type 3 means the design needs
revision. Non-rejection is not evidence of independence.

## Desired project properties

- Explainable in one sentence.
- Interesting to someone outside the immediate subfield.
- Public data, or access already confirmed.
- Feasible for one researcher with Colab-class compute.
- Clear baselines and metrics.
- Minimal new expert annotation.
- First useful result in days, not months.

## Themes of interest

1. Reliability and causal validity of named concepts.
2. Specified versus discovered concepts in small medical datasets.
3. Concept leakage and hidden residual information.
4. Faithfulness of concept-mediated reasoning or explanations.
5. Concept stability across sites, scanners, protocols, and demographics.
6. Whether concept supervision improves calibration, robustness, or failure
   detection.
7. Low-cost audits of published concept-based models using existing assets.
8. Provenance and construction of concept labels themselves — who assigned
   them, seeing what, and what that implies about what a model trained on them
   can be said to have learned.

Theme 8 was added because the first three candidates all died on it. It is the
most under-examined area found so far and the one where a cheap audit is most
likely to produce a real finding.

## Constraints

- Compute: Colab Pro+ or equivalent single-GPU sessions.
- No dependence on unconfirmed DUA-gated data.
- No large-scale radiologist annotation campaign.
- Literature claims require primary-source verification.
- Do not treat report text, class labels, or segmentation labels as meaningful
  concepts without justification.
- Avoid architectural complexity unless the question requires it.
- Keep confirmatory and exploratory work separate.
- Never tune on the untouched test set.

## What counts as success

- A clear positive result.
- A clear negative result of type 1.
- Evidence that a popular assumption is unsupported.
- Identification of a decisive confound.
- A feasibility result that prevents wasted effort.
- A well-supported decision to advance, revise, pause, or reject.


===== docs/COLLABORATOR_RULES.md =====
# Collaborator rules

## Role

Act as a critical research collaborator. Generate ideas, but spend at least as much effort trying to disprove or simplify them.

## Required distinctions

Always distinguish:

- verified fact;
- source-supported interpretation;
- inference;
- speculation;
- exploratory result;
- confirmatory result.

## Literature

- Use primary sources for medical, dataset, and method claims.
- Record DOI, PMID, arXiv ID, or official repository URL.
- Never claim novelty from memory alone.
- “I did not find it” is not proof that it does not exist.
- Identify the closest work and explain the exact delta.

## Idea generation

Prefer “one experiment away from a stronger story” over unconstrained novelty brainstorming.

For every idea, identify:

- the scientific uncertainty;
- the existing legwork already completed by others;
- the missing final step;
- why that step matters;
- the smallest decisive experiment;
- the most dangerous confound;
- why a negative result remains useful.

## Coding gate

Do not generate probe code until all are present:

- a reviewed idea card;
- a feasibility memo;
- a probe contract;
- explicit human approval.

## Experimental integrity

- Freeze splits before model comparison.
- Save configurations, seeds, environment, and per-case outputs.
- Use validation for development and preserve an untouched test set.
- Do not reinterpret an invalid run as a negative result.
- Report every authorized variant, not only the best one.
- Stop when the preregistered question is answered or the budget is exhausted.


===== docs/SCORING_RUBRIC.md =====
# Idea scoring rubric

Score each dimension 1-5. Explain every score.

| Dimension | 1 | 3 | 5 |
|---|---|---|---|
| Clarity | vague | testable with refinement | one-sentence precise question |
| **Identifiability** | a positive result has many explanations | design rules out the main alternative | design isolates the claimed mechanism |
| Medical relevance | cosmetic | plausible utility | clear meaningful consequence |
| Interest | routine | useful niche result | surprising or broadly compelling |
| Prior legwork | little exists | some reusable assets | data/code/labels/checkpoints ready |
| Feasibility | major barriers | manageable | first result in days |
| Data readiness | uncertain/restricted | accessible with work | public and directly usable |
| Evaluation readiness | unclear | custom metrics needed | accepted metrics and baselines exist |
| Negative-result value | uninterpretable null | sensitivity-limited null | decisive negative |
| Novelty confidence | likely covered | uncertain | precise verified gap |
| Regret | little concern | worth considering | obvious-in-hindsight opportunity |

## Hard caps

`feasibility` and `novelty_confidence` may not exceed **3** unless
`keystone_status` is `INSPECTED_TRUE`. See the charter.

`negative_result_value` may not exceed **2** if the anticipated negative is
classified as uninterpretable.

## Priority score

Transparent weighted sum, not a fake probability:

- 20% feasibility
- **15% identifiability**
- 15% medical relevance
- 10% prior legwork
- 10% interest
- 10% clarity
- 10% negative-result value
- 5% data readiness
- 5% novelty confidence

Evaluation readiness and regret are reported separately and must not override
weak scientific value.

Identifiability enters at 15% because the first cycle produced several
candidates with strong headlines whose designs could not isolate the stated
phenomenon. Interest was compensating for weak measurement validity.


===== ideas/005/README.md =====
# Idea 005: Eight named characteristics, or three latent ones? Discriminant validity of the LIDC concept vocabulary

Selected from scouting cycle 002, candidate 3.


===== ideas/005/idea_card.json =====
{
  "id": "C3",
  "search_mode": "B",
  "title": "Eight named characteristics, or three latent ones? Discriminant validity of the LIDC concept vocabulary",
  "question": "In the radiologists' own ratings, do the eight LIDC semantic characteristics agree with themselves across readers more than they correlate with each other within a reader - and if not, how many distinct dimensions does a concept model that reports eight separate concept predictions actually have?",
  "why_unasked": "Concept-based models report per-concept accuracy on an assumption nobody states: that the named concepts are separate attributes rather than several names for one underlying impression. Psychometrics has a standard test for exactly this and has had it since 1959 - the multitrait-multimethod matrix, in which convergent validity lives on the diagonal and discriminant validity lives on the off-diagonal - but concept-based ML reports only the diagonal. The off-diagonal has never been assembled because there is no convention that asks for it: a concept-accuracy table has one row per concept and one column for performance, and there is nowhere to put a concept-by-concept matrix. Descriptive correlations among LIDC characteristics have been noted in passing (margin with texture, spiculation with malignancy) but never set against the between-reader agreement that would make them interpretable.",
  "concept_definition": "The same eight non-malignancy LIDC characteristics as in C2, again excluding the malignancy rating. Here the unit of analysis is the individual reader's rating vector for a nodule, and the object of study is the construct structure of the vocabulary itself - not any model's ability to predict it. This is a question about the concepts, not about a classifier.",
  "keystone_prerequisite": "The released XML supplies, for the same nodule, multiple readers' ratings AND multiple characteristics per reader - so that the same-characteristic-across-readers cells and the different-characteristic-within-reader cells of the matrix can both be filled from the same nodules.",
  "keystone_status": "INSPECTED_TRUE",
  "keystone_evidence": "Same artifact as C2: Armato et al. 2011 Med Phys 38:915-931, Methods, via PMC3041807, read directly. Per-reader preservation is verbatim ('Each radiologist's lesion-category designation and associated marks ... were stored in a single XML file for each scan after the unblinded read phase'), and 928 of 2669 lesions carry marks from all four readers, giving the reader facet. The Methods also confirm that the nine subjective characteristics - subtlety, internal structure, spiculation, lobulation, sphericity, solidity/texture, margin, calcification, and likelihood of malignancy - were assessed for nodules >= 3 mm, giving the characteristic facet. Both facets are therefore present on the same nodules, which is exactly what a multitrait-multimethod matrix requires. IMPORTANT CAVEAT, same source, same verbatim quote as in C2: only post-unblinded-read ratings are released, so the between-reader cells are inflated by peer exposure. This biases the comparison in the CONSERVATIVE direction for this candidate: inflated convergent (diagonal) values make it harder, not easier, to conclude that discriminant validity fails. A positive finding under this bias is therefore stronger than it looks. RESIDUAL: I did not verify that every reader rates all eight characteristics on every nodule they marked; characteristic-level missingness would thin the within-reader off-diagonal cells and is the first thing to count.",
  "closest_prior_work": [
    {
      "citation": "Campbell D.T., Fiske D.W. Convergent and discriminant validation by the multitrait-multimethod matrix.",
      "identifier": "Psychological Bulletin 56(2):81-105 (1959)",
      "verification": "NOT_CHECKED in this session - cited from standing knowledge, and must be verified against the primary text before use.",
      "what_it_did": "Defines the criteria: a trait's measurements should correlate more with other measurements of the same trait than with measurements of different traits by the same method.",
      "what_it_did_not_do": "Not applied to medical imaging concept vocabularies, which is the borrow."
    },
    {
      "citation": "Semantic characteristic grading of pulmonary nodules based on deep neural networks.",
      "identifier": "BMC Medical Imaging (2023), DOI 10.1186/s12880-023-01112-4",
      "verification": "SEARCH_SUMMARY_ONLY",
      "what_it_did": "Reports that spiculation has the highest correlation with malignancy, followed by lobulation, calcification, subtlety, margin, sphericity, internal structure and texture; notes that 'high correlations exist between different semantic terms, such as margin and texture'.",
      "what_it_did_not_do": "Uses correlations descriptively to select features for a malignancy model. Does not compare the between-characteristic correlations against the between-reader agreement for the same characteristic, which is the comparison that turns 'these correlate' into 'these are not distinguishable constructs'. Does not estimate the vocabulary's effective dimensionality or draw any consequence for concept-model reporting."
    },
    {
      "citation": "Nodule2vec: a 3D Deep Learning System for Pulmonary Nodule Retrieval Using Semantic Representation; and Bridging Computational Features Toward Multiple Semantic Features with Multi-task Regression.",
      "identifier": "arXiv:2007.07081; Springer, DOI 10.1007/978-3-319-46723-8_7",
      "verification": "SEARCH_SUMMARY_ONLY",
      "what_it_did": "Learn joint representations over the LIDC semantic characteristics, implicitly exploiting their correlation.",
      "what_it_did_not_do": "Exploit the redundancy without measuring or reporting it, and without asking whether reporting eight separate concept accuracies is meaningful when the underlying vocabulary has fewer degrees of freedom."
    },
    {
      "citation": "Mapping LIDC, RadLex and lung nodule image features.",
      "identifier": "PMC3056962",
      "verification": "SEARCH_SUMMARY_ONLY",
      "what_it_did": "Maps LIDC terminology onto a standard radiology lexicon.",
      "what_it_did_not_do": "Terminological alignment, not empirical construct structure. A term can be well-defined in RadLex and still not be separately measurable by readers, which is the distinction this candidate is about."
    }
  ],
  "existing_assets": [
    "The same single public artifact as C2 - LIDC-XML-only.zip, CC BY 3.0 - and the same parsers. Running C2 and C3 together roughly doubles the output for less than double the work.",
    "928 four-reader nodules and 2669 lesions with at least one reader, giving both a strict and a permissive analysis set.",
    "Established statistical machinery: polychoric correlations for ordinal ratings, ordinal factor analysis, parallel analysis for dimensionality, all in standard open packages.",
    "Published descriptive correlations to sanity-check the matrix against."
  ],
  "smallest_decisive_experiment": "CPU only, no images, no model, hours. On four-reader nodules, build the full multitrait-multimethod matrix where the traits are the eight characteristics and the methods are the four reader slots. Fill three families of cells: (a) same characteristic, different readers - convergent; (b) different characteristics, same reader - discriminant, and the one nobody reports; (c) different characteristics, different readers. Apply the Campbell-Fiske criteria explicitly and report how many characteristics pass. Then estimate effective dimensionality: polychoric correlation matrix over the eight characteristics, ordinal factor analysis, and parallel analysis to choose the number of retained dimensions, reported with bootstrap confidence intervals. The headline number is the count of latent dimensions relative to eight. The decisive twist that makes it more than an exercise: repeat the dimensionality estimate after disattenuating the correlation matrix for the between-reader reliability of each characteristic (which C2 produces for free), so the result cannot be dismissed as 'you just measured noise'.",
  "alternative_explanations": [
    "Shared method variance: one reader rating eight characteristics in one sitting will produce correlated ratings through halo effects, fatigue, or a global impression of the nodule, independent of whether the underlying attributes are distinct. This is a genuine competing explanation and it is exactly what the (c) family of cells is for - if different-characteristic correlations survive when the two ratings come from *different* readers, halo within a single rater cannot be the whole story. This is the design's main identifying move and it is why the four-reader subset matters.",
    "Scale degeneracy: internal structure and calcification are heavily concentrated on one level, which compresses correlations and distorts factor structure. RULED OUT by using polychoric rather than Pearson correlations, reporting per-characteristic response distributions alongside the matrix, and running the analysis with and without the near-degenerate characteristics.",
    "Genuine biological co-occurrence: spiculated nodules really do tend to be lobulated. A low-dimensional structure could reflect the world rather than the vocabulary. The design does NOT rule this out and cannot - but it does not need to. The consequence for concept modelling is identical either way: if the vocabulary has three degrees of freedom in the data, then eight reported concept accuracies are not eight independent results and eight intervention handles are not eight independent handles, regardless of why."
  ],
  "anticipated_negative": {
    "classification": "decisive",
    "reasoning": "If the Campbell-Fiske criteria are satisfied - each characteristic agrees with itself across readers more than it correlates with any other characteristic - and parallel analysis retains something close to eight dimensions, that is a clean, positive validation of a clinical concept vocabulary as separately measurable. That result does not currently exist for any medical concept vocabulary that I am aware of, and it would be the strongest available justification for the practice of reporting per-concept performance. It meaningfully strengthens the assumption rather than merely failing to reject it, so it is type 1."
  },
  "remaining_legwork": [
    "Same download and same frozen cross-reader clustering rule as C2. Shared cost.",
    "Count characteristic-level missingness per reader per nodule - the keystone residual - which determines whether the strict four-reader analysis has enough complete cells.",
    "Statistical development: assigning readers to stable 'method' slots is not trivial, because LIDC readers are not a fixed panel across scans. The matrix must either use exchangeable reader slots with an appropriate variance model, or restrict to scans read by an identifiable reader set. This is the single largest piece of unbuilt methodology in the candidate and should be settled before any computation.",
    "Verify the Campbell-Fiske primary text and choose a modern operationalisation, since the 1959 criteria are informal by contemporary standards; a confirmatory factor model with correlated traits and methods is the standard replacement and should be prespecified.",
    "Expected time to first decision: three to four days, most of it on the reader-slot modelling rather than on computation."
  ],
  "cross_domain": {
    "borrowed_construct": "The multitrait-multimethod matrix and the convergent/discriminant validity distinction (Campbell and Fiske, 1959), plus effective dimensionality from ordinal factor analysis.",
    "measurement_it_implies": "Compute and report the full eight-by-eight concept matrix with reader identity as the method facet, apply the discriminant criterion cell by cell, and report the number of retained latent dimensions after disattenuation. Concretely: a table that currently has one column gains sixty-four cells.",
    "what_changes_if_the_analogy_is_dropped": "Without it you report eight per-concept accuracies and a passing remark that some concepts correlate - which is what the literature already does. The borrowed construct supplies the decision rule (a concept fails discriminant validity when its cross-concept correlation exceeds its own cross-reader agreement) and the consequence (an eight-concept bottleneck with three effective dimensions cannot support eight independent interventions). Neither the rule nor the consequence is reachable from the ML vocabulary alone, so this is load-bearing rather than decorative."
  },
  "scores": {
    "clarity": {
      "value": 4,
      "why": "The comparison is precise, but 'effective dimensionality' requires a stated estimator and retention criterion to be unambiguous, and the reader-slot construction needs specification before the question is fully well-posed."
    },
    "identifiability": {
      "value": 4,
      "why": "The different-characteristic-different-reader cells specifically separate halo-within-rater from genuine construct overlap, which is the main alternative explanation. Held below 5 because genuine biological co-occurrence is not separable from vocabulary redundancy - though the consequence for concept modelling is the same either way."
    },
    "medical_relevance": {
      "value": 3,
      "why": "If a taught clinical vocabulary has fewer usable dimensions than terms, that matters for structured reporting and for concept-based interfaces. But it is a statement about descriptive vocabulary rather than about a diagnostic decision, and no patient outcome is involved."
    },
    "interest": {
      "value": 4,
      "why": "'Eight concepts, three dimensions' is a compact and portable result, and the psychometric framing is unfamiliar enough in this field to be genuinely useful. Held below 5 because the finding that morphological descriptors correlate will surprise no radiologist; only its quantification and its consequence for concept models will."
    },
    "prior_legwork": {
      "value": 4,
      "why": "Data, parsers, statistical packages and descriptive correlations all exist. Short of 5 because the reader-as-method-facet construction has to be built."
    },
    "feasibility": {
      "value": 5,
      "why": "Cap lifted, keystone INSPECTED_TRUE. One public file, CPU only, no model, no access application, and it shares all infrastructure with C2."
    },
    "data_readiness": {
      "value": 5,
      "why": "Public, CC BY 3.0, no application, directly usable."
    },
    "evaluation_readiness": {
      "value": 3,
      "why": "Polychoric correlations and parallel analysis are standard, but there is no accepted convention for a multitrait-multimethod analysis with non-fixed raters, and no baseline in this literature to compare a dimensionality estimate against. The metric has to be argued for, not merely cited."
    },
    "negative_result_value": {
      "value": 4,
      "why": "A pass on the Campbell-Fiske criteria would be the first empirical validation of a medical concept vocabulary as separately measurable, which is a real positive contribution. Held below 5 because a pass is somewhat less consequential for practice than a failure would be."
    },
    "novelty_confidence": {
      "value": 3,
      "why": "Cap lifted by the keystone, but held at 3: descriptive correlation analyses of LIDC characteristics clearly exist, and I did not search the psychometrics-in-radiology literature, observer-performance journals, or Academic Radiology systematically. A convergent/discriminant framing may exist there under different vocabulary, which is precisely the kind of thing a shallow arXiv-and-web search misses."
    }
  },
  "priority_score": 4.05,
  "priority_arithmetic": "0.20*5 (feas) + 0.15*4 (ident) + 0.15*3 (med) + 0.10*4 (legwork) + 0.10*4 (interest) + 0.10*4 (clarity) + 0.10*4 (neg) + 0.05*5 (data) + 0.05*3 (novelty) = 1.00+0.60+0.45+0.40+0.40+0.40+0.40+0.25+0.15 = 4.05",
  "regret": {
    "value": 4,
    "why": "A sixty-year-old validity test, a public ratings file, and an entire subfield reporting only the diagonal."
  },
  "recommendation": "SHORTLIST",
  "unverified_claims": [
    "Whether every reader rates all eight characteristics on every nodule they mark. Characteristic-level missingness directly determines the usable cell counts and is the first count to run.",
    "How reader identity is represented in the XML and whether readers can be assigned to stable slots across scans. If readers are fully anonymous and non-tracked, the method facet must be modelled as exchangeable, which weakens the Campbell-Fiske application. THIS IS THE LARGEST DESIGN RISK and it is a fact about the XML I did not inspect.",
    "The Campbell and Fiske 1959 primary text was not opened in this session.",
    "The BMC Medical Imaging 2023 correlation findings and the 'margin and texture' remark are from a search summary only.",
    "Whether an ordinal factor analysis of the LIDC characteristics has already been published. Not established; observer-performance and radiology methodology journals were not searched."
  ]
}


===== STAGE TASK =====
Adversarially review the selected idea. Try to reject it for prior-work overlap, weak relevance, concept-label circularity, leakage, confounding, unavailable data, excessive compute, weak negative-result value, or an unclear endpoint.

Also search for an easier version that preserves the interesting question. Explicitly identify any low-hanging-fruit formulation where data, labels, code, or checkpoints already exist.

Open `critique.md` with a **decision header** of at most six lines, before any
detail:

```
FATAL OBJECTION: [one sentence, or NONE]
EVIDENCE: [the specific source, file, or table]
REPAIRABLE WITHOUT CHANGING THE QUESTION? YES / NO
DECISION: ADVANCE TO REVISION | PAUSE | REJECT
```

Then the detailed analysis below it. Long critiques bury their own best points;
the header exists so the decisive objection cannot be lost in section nine.

Close with a constructive section:

```
NEAREST DEFENSIBLE HIGH-VALUE QUESTION: [one sentence]
RETAINS ORIGINAL MEDICAL MOTIVATION? YES / PARTLY / NO
SHOULD IT BECOME A SEPARATE CANDIDATE? YES / NO
IS IT ACTUALLY WORTH DOING? [one sentence — "a smaller benchmark exists"
is not the same as "the smaller benchmark is worth doing"]
```

A critic that only demolishes produces a portfolio of corpses. Say plainly when
nothing nearby is worth doing; say plainly when something is.

Do not write code.

