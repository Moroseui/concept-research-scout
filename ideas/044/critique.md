# Critique — Idea 044: The old stroke inside the new forecast

```
FATAL OBJECTION: NONE
EVIDENCE: closest-to-fatal is the unnamed frozen model plus the verified weakness
  of the state of the art (top ISLES'24 model Dice 0.285 ± 0.213, arXiv 2408.10966);
  both are repairable by pins, not fatal to the question.
REPAIRABLE WITHOUT CHANGING THE QUESTION? YES
DECISION: ADVANCE TO REVISION
```

## Scope of this review

Adversarial critique of `idea_card.json` (isles24-scout-005-c02) with the
keystone screen (`keystone_screen.md`, verdict UNVERIFIABLE from documentation)
taken as given. New primary-source checks performed this stage: the ISLES'24
challenge-results paper (arXiv 2408.10966), the challenge winner's method paper
(arXiv 2505.18424), and a targeted sweep of the NCCT "brain frailty"
association literature. Epistemic labels used throughout: **[VF]** verified
fact (read at source this stage or a prior stage), **[SS]** source-supported
interpretation (title/abstract-level only), **[INF]** inference, **[SPEC]**
speculation.

## 1. Prior-work overlap: the association literature is rich; the delta survives

The suspected signal is not novel as an *association*. Old infarcts,
leukoaraiosis, and atrophy on admission NCCT form the established "brain
frailty" triad, scored 0–3 and repeatedly shown to predict stroke outcome:
the IST-3 secondary analysis (Lancet Neurol 2015; PMC4513190) found old
infarct predicted symptomatic intracranial hemorrhage, and the brain-frailty
score literature (Neurology 2020, DOI 10.1212/WNL.0000000000008881, and
successors through 2025) ties the triad to functional outcome **[SS —
verified at title/abstract level this stage, not read in full]**.

Two consequences, one for and one against the card:

- **For:** the card's delta — an *intervention* test of whether a trained
  final-infarct model **uses** the cavity, rather than whether the cavity
  *predicts* outcome — is exactly the use-versus-association distinction the
  program requires, and no intervention-style precedent was found in this
  stage's searches or the scout's. "Not found" is not "does not exist"
  **[INF]**; novelty_confidence 3 with LIMITED_SEARCH remains the correct
  ceiling and is what the card claims.
- **Against:** within the frailty triad, old infarcts are the *weakest*
  member in several association studies (one cohort found old vascular
  lesions not independently associated with the cognitive outcome where
  leukoaraiosis and atrophy were) **[SS]**. The prior probability that a
  model trained on 149 cases learned to consult a minority-prevalence,
  weakly-predictive marker is not high. This does not invalidate the test —
  a clean null is claimed as informative — but it should temper `interest: 4`
  and it raises the stakes on the sensitivity gates (sections 3–5): a null
  produced by an insensitive design would be worthless precisely because the
  prior already leans null **[INF]**.

## 2. The deliverable sentence overclaims the mechanism (repair required)

The deliverable — "using remote chronic infarct cavities **as a
brain-reserve signal**" — claims an interpretation the design cannot
identify. The card concedes this itself twice: identifiability is scored 3
because the design shows "cavity use but not whether the model interprets it
as reserve or age," and alternative explanation 2 says the age-proxy
confound "cannot fully" be distinguished. The design demonstrates, at best,
*use of contralateral cavity-like tissue loss on NCCT*. "Brain reserve" is a
physiological construct sitting on top of that, exactly parallel to
"autoregulatory blood-volume reserve" in idea 023, where the ruling
(decisions.md, 2026-08-17) was that physiological naming requires
independent validation and the claim language was reduced in place under
REVISE.

**Repair:** deliverable sentence and question drop the reserve clause —
"The final-infarct model is using remote chronic-cavity-like tissue loss on
admission NCCT when forecasting new infarction." Reserve stays in
`suspected_signal` as motivation. Under the claim-identity rule (2026-08-10)
this is a narrowing within the same measured estimand, not a change of claim
identity — the intervention, endpoint, and prohibited conclusions are
unchanged; only an interpretive rider is deleted — so revision-in-place, not
a successor, is the correct vehicle **[INF, precedent-based]**.

## 3. Cross-channel inconsistency: the edit removes the cavity from one input channel only

The card pins: "holding all acute CT, CTA, perfusion, and affected-hemisphere
voxels fixed." So the cavity is filled **on NCCT only**. But a chronic
encephalomalacic cavity is CSF-filled tissue loss; it necessarily also
appears in the CTP-derived maps (near-zero CBV/CBF in the cavity) and in CTA
as an avascular region **[INF from physiology; not verified on ISLES'24
voxels]**. Three consequences:

1. **The positive-claim scope shrinks.** A supra-sham response demonstrates
   use of the *NCCT-channel* cavity appearance, not use of "the cavity."
   The card nowhere states this restriction.
2. **The null is biased toward insensitivity.** A model reading the cavity
   from the CBV map would show no NCCT-edit response, yielding a false
   "does not use" verdict. Combined with section 1's low prior, this is the
   single largest threat to the card's claimed negative-result value.
3. **The edited input is cross-modally inconsistent** — normal-appearing
   NCCT tissue over a perfusion void is a configuration absent from
   training data. The program has been burned by OOD interventions before
   (idea 006, PAUSED for exactly this class of error). Mitigation exists in
   the card, apparently by accident: the ventricle-adjacent CSF-fill sham
   *also* creates NCCT-tissue-over-perfusion-void mismatch, so the sham
   contrast partially cancels the pure-mismatch response **[INF]**. The
   random-parenchyma sham does not share this property. The card should
   claim this control explicitly rather than own it implicitly.

**Repair:** restate the estimand as NCCT-channel use; promote the CSF sham
to the designated mismatch control with that rationale written down; add a
pre-specified interpretation rule for the case where the model turns out to
ignore NCCT entirely (see section 5). A consistent all-channel edit would be
the stronger design but touches perfusion maps, which idea 021/023
precedent treats as requiring its own realism machinery — out of scope for
this card's question and correctly so.

## 4. The donor-tissue rule has a bug: the mirror of a contralateral cavity lies in the affected hemisphere

The edit fills the cavity "with texture sampled from mirrored homologous
tissue." The cavity is contralateral to the acute stroke by construction, so
its mirrored homolog is **in the affected hemisphere** — possibly inside the
Tmax>6 s territory or the ischemic core **[INF, geometric]**. The card's
exclusion of acute territory applies to cavity *detection*
(`X_measurement`), not to donor sampling. Failure mode: the fill imports
subtly hypodense acutely-ischemic texture into the contralateral hemisphere,
so the "cavity removed" image actually contains new-looking pathology —
attenuating or inverting the intended contrast, direction unknowable per
case **[INF]**.

**Repair (cheap, mandatory):** donor regions must be verified
normal-appearing — exclude any donor voxel inside the Tmax>6 s or CBF<30%
territory and require donor HU statistics within the normal-tissue band; on
cases where the homolog is contaminated, fall back to the second
(generative) fill method the card already requires. Two-method concordance,
already pinned, then also polices residual donor artifacts.

## 5. No frozen model is named, and the verified state of the art is weak

The experiment is priced "20 GPU-hours **once a model is frozen**," and
`existing_assets` lists no model. Checked this stage:

- The challenge-results paper (arXiv 2408.10966) reports the top method — a
  multimodal nnU-Net — at **Dice 0.285 ± 0.213, absolute volume difference
  21.2 ± 37.2 mL** on the 98-case hidden test set **[VF at abstract level]**.
- The winner's paper (arXiv 2505.18424, "How We Won the ISLES'24 Challenge
  by Preprocessing") describes skull-stripping + intensity windowing + a
  residual nnU-Net; **no code/weights availability statement was found** in
  the abstract-level content fetched. Absence of a statement is not absence
  of release **[SS]** — but it means model availability is currently
  UNVERIFIED, the same defect class that PAUSED ideas 022 and 025.

This is not fatal, unlike 022, because a final-infarct baseline is trainable
locally from the 149 public cases with standard tooling — the dataset exists
to enable exactly that — and the card's own rung ladder already scopes rung 1
to a single model with rung 2 requiring a separately trained model. But three
pins are required:

1. **Name the model path** in the card: verified public
   checkpoint/docker if one exists (Stage 0 checks the challenge site and
   winner repositories), else a locally trained nnU-Net with frozen
   configuration, and price the training compute honestly (the 20-GPU-hour
   figure covers inference only).
2. **Define the performance gate numerically before any edit is run.** The
   card's "model performance" gate is undefined while the verified SOTA is
   Dice 0.285. A gate that no obtainable model can pass kills the idea
   honestly; an undefined gate invites post-hoc rationalization. Note the
   paired design means low Dice does not add noise to the edit response
   (same frozen model, same case, deterministic inference) — the gate's
   real function is to ensure the model is good enough for its internal
   computations to be worth interrogating, and the card must say what
   "good enough" is **[INF]**.
3. **Add an NCCT-sensitivity gate.** If the frozen model effectively
   ignores its NCCT channel (checkable by channel ablation on unedited
   cases before any cavity edit), the intervention is vacuous and every
   null is uninterpretable. This gate must precede the paired experiment,
   and failing it is a kill, not a footnote. This interacts with section 3:
   an NCCT-insensitive model is plausible when perfusion maps carry most
   final-infarct signal **[SPEC, but cheap to check]**.

## 6. The prevalence gate is arbitrary and probably miscalibrated

The card demands ≥15 of the first 30 cases (50%) carry a stable remote
cavity ≥1 mL. No cited source supports 50% prevalence of *cavitated,
contralateral, ≥1 mL* chronic infarcts in an acute-LVO cohort; the frailty
literature reports old infarcts on NCCT in a minority-to-moderate fraction
of acute stroke cohorts **[SS]**, and the contralateral-only restriction
roughly halves whatever that number is **[INF]**. As written, the gate
likely fails even in a world where the experiment is viable — it confuses
"prevalence is high" with "enough editable cases exist."

**Repair:** census **all 149 public training cases** (the census is
automated; 30 was never a cost-driven cap), and gate on a pre-specified
minimum count of editable cases derived from a paired-test power sketch,
not on a prevalence fraction. Keystone-screen framing stands: this census
is the Stage 0 kill experiment and is genuinely cheap.

## 7. Leakage, circularity, compute, data access — checked, no objection

No concept labels exist, so no circularity. The paired within-case design
has no train/test leakage surface; the 149 census cases are training-split
cases, acceptable because the endpoint is model-behavior measurement, not
performance claims — though if the frozen model is locally trained, edited
cases must come from its validation fold, which the revision should pin
**[INF]**. Compute (≈20 GPU-hours inference + bounded training) is honest
once section 5's training cost is added. Data access is verified public
(keystone screen, Zenodo record 16813698). License CC BY-SA-NC 4.0 permits
this use **[VF, keystone screen]**.

## 8. Portfolio note: homogenization

`design_template: regional-removal` joins a portfolio already carrying
regional-substitution ×9 and counterfactual-synthesis ×10. This is another
edit-the-input-and-compare move with rotated nouns. It is also the cleanest
member of its family on this dataset — a discrete, remote, bounded lesion
rather than a diffuse field (contrast the "frail brain" backlog candidate
isles24-scout-001-c04, which this card correctly distinguishes). Acceptable,
but the shortlist as a whole is buying many tickets in one lottery
**[INF]**.

## 9. Plain-pitch fidelity (opposite-family check)

Two defects, one mild, one real:

1. **Etiology hedge partially dropped.** The card's residual assumption is
   explicit that a positive result supports "use of cavity-like tissue
   loss, **not proven prior infarction**." The pitch's operative sentence
   does say "the old-**looking** cavity" — the hedge survives there — but
   the opening ("An old stroke can leave a fluid-filled cavity… looks
   across the brain at that old damage") presents the etiology as settled.
   Mild; fix by one word ("old-looking damage" or equivalent).
2. **Reserve framing.** "Treats the patient as more vulnerable" asserts in
   plain language the brain-reserve interpretation that section 2 shows the
   design cannot identify. This is the same overclaim as the deliverable
   sentence, translated. It must be fixed jointly with section 2 — e.g.,
   "asks whether that old-looking damage changes the forecast," dropping
   the vulnerability gloss.

Also noted with approval: "leaving the new stroke and its blood-flow maps
untouched" states the single-channel edit plainly — the pitch is honest
about the very property section 3 critiques.

## Verdict

ADVANCE TO REVISION. Required revisions, in priority order: (1) reduce the
deliverable/question/pitch to cavity-appearance use, dropping "brain
reserve" (sections 2, 9); (2) restate the estimand as NCCT-channel use,
designate the CSF sham as the mismatch control, add the NCCT-sensitivity
ablation gate (sections 3, 5.3); (3) pin the donor-exclusion rule (section
4); (4) name the frozen-model path and define the performance gate
numerically (section 5); (5) recalibrate the prevalence gate to a
power-derived editable-case count over all 149 cases (section 6). None of
these changes the question; all of them change whether the answer would be
believed.

```
NEAREST DEFENSIBLE HIGH-VALUE QUESTION: Does a frozen ISLES'24 final-infarct
model change its affected-hemisphere prediction, beyond matched CSF and
parenchyma shams, when contralateral chronic-cavity-like tissue loss is
inpainted out of the NCCT channel?
RETAINS ORIGINAL MEDICAL MOTIVATION? PARTLY — the prior-damage question
survives intact; the brain-reserve interpretation is deferred to a successor
with independent physiological grounding.
SHOULD IT BECOME A SEPARATE CANDIDATE? NO — it is this candidate after
revision-in-place; the estimand and endpoint are unchanged.
IS IT ACTUALLY WORTH DOING? YES, conditionally — the census-first design
means the world answers the killing questions (prevalence, separability,
NCCT sensitivity) for about two days of work before any expensive commitment,
and both the positive and the gated negative would be citable facts about
what final-infarct models consult; if the census or the NCCT-ablation gate
fails, kill it without regret.
```

## Sources checked this stage

- ISLES'24 challenge results: arXiv 2408.10966 (top model Dice 0.285 ± 0.213,
  AVD 21.2 ± 37.2 mL, hidden test n=98) — abstract-level fetch.
- ISLES'24 winner method: arXiv 2505.18424 (residual nnU-Net + preprocessing;
  no release statement found at abstract level) — abstract-level fetch.
- Brain frailty association family (title/abstract level only): IST-3
  secondary analysis, Lancet Neurol 2015 (PMC4513190); Neurology 2020,
  DOI 10.1212/WNL.0000000000008881; brain-frailty/thrombolysis 2025
  (PMID 41026485).
- Prior stages relied on: ideas/044/keystone_screen.md (Riedel et al.,
  DOI 10.1148/ryai.250603; Zenodo 16813698; clinical dictionary has no
  prior-stroke variable).
