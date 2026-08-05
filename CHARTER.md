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
