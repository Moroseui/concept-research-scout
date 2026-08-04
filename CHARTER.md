# Research charter

## Central interest

Find clear, feasible, medically relevant research questions about **concepts in medical imaging**. Diagnosis, prognosis, representation analysis, concept reliability, concept intervention, and model auditing are all in scope. Concept-motivated segmentation correction remains a side project rather than the default main direction.

## Preferred opportunity pattern

Prioritize partially completed research stories where much of the groundwork already exists and one or two clean experiments could provide a meaningful conclusion. Examples:

- an existing method lacks an important evaluation;
- a claimed concept has not been causally validated;
- a public dataset already contains nearly all required labels;
- a paper leaves a precise future-work question;
- a simple baseline can test a widely assumed claim;
- a method has not been tested under a clinically relevant confound;
- a concept vocabulary exists but its faithfulness, leakage, stability, or utility is unknown.

## Desired project properties

- Easy to explain in one sentence.
- Interesting even to someone outside the immediate subfield.
- Publicly accessible data or already-confirmed access.
- Feasible for one researcher with Colab-class compute.
- Clear baselines and metrics.
- Positive and negative outcomes are both informative.
- Minimal need for new expert annotation.
- The first useful result can be obtained in days or a few weeks, not months.

## Current themes of interest

1. Reliability and causal validity of named concepts.
2. Specified versus discovered concepts in small medical datasets.
3. Concept leakage and hidden residual information.
4. Faithfulness of concept-mediated reasoning or explanations.
5. Concept stability across sites, modalities, acquisition shifts, and demographic groups.
6. Whether concept supervision improves calibration, robustness, or failure detection.
7. Low-cost audits of published concept-based models using existing datasets and checkpoints.

## Constraints

- Compute: Colab Pro+ or equivalent single-GPU sessions.
- No project should depend on unconfirmed DUA-gated data.
- No large-scale radiologist annotation campaign.
- Literature claims require primary-source verification.
- Do not treat report text, class labels, or segmentation labels as meaningful concepts without justification.
- Avoid architectural complexity unless the question requires it.
- Keep confirmatory and exploratory work separate.
- Never tune on the untouched test set.

## What counts as success

- A clear positive result.
- A clear negative result.
- Evidence that a popular assumption is unsupported.
- Identification of a decisive confound.
- A feasibility result that prevents wasted effort.
- A well-supported decision to advance, revise, pause, or reject an idea.
