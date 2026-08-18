FATAL OBJECTION: The factorial edits do not intervene on intracranial compliance or edema, so even a clean interaction cannot establish that the model uses CSF reserve to expand infarct geometry.
EVIDENCE: ISLES'24 winner `inference.py` at commit `bb6c00c8` (CBF/CBV/MTT/Tmax/CTA only); Broocks et al., DOI 10.1161/STROKEAHA.118.020507 (net water uptake is an admission-CT lesion measurement); ISLES'24 dataset DOI 10.1148/ryai.250603 (no edema or mass-effect target).
REPAIRABLE WITHOUT CHANGING THE QUESTION? NO
DECISION: REJECT

## Decisive construct-validity failure

**Verified fact.** The released winner does not ingest NCCT. Its five deployed channels are CBF, CBV, MTT, Tmax, and CTA (`KurtLabUW/ISLES2024`, commit `bb6c00c8a58cb57a5a33c133c02885776673d230`, `inference.py:121-125`). The keystone screen also verified global histogram equalization and default per-image z-scoring. Thus the card's NCCT CSF and net-water-uptake interventions cannot be presented to this frozen model as specified.

**Verified fact.** Broocks et al. define quantitative net water uptake as an acute CT attenuation biomarker measured within an early infarct lesion, and validate it against malignant edema (153 patients; DOI `10.1161/STROKEAHA.118.020507`, PMID `29976584`). It is not a transferable scalar that can be imposed on CTA or perfusion-map voxels and still be called tissue swelling.

**Verified fact.** ISLES'24 supplies hyperacute CT and infarct delineations derived from MRI 2-9 days after reperfusion, but no edema, mass-effect, displacement, or intracranial-pressure label (dataset paper DOI `10.1148/ryai.250603`; public training set 149 and hidden test set 96 in the journal version). Its ground truth is infarct tissue, not a deformation field.

**Inference.** “Available room for swelling” is a property of the actual intracranial anatomy. Enlarging or shrinking a CSF-looking region while requiring all parenchymal inputs to remain fixed creates or deletes image content; it does not instantiate a physically possible alternative skull/brain configuration with different compliance. Conversely, a real ventricular or sulcal boundary displacement necessarily changes the adjacent tissue geometry. Moving the edit downstream of preprocessing fixes normalization leakage but makes this construct problem worse: plausibility in equalized tensor space is not evidence of anatomical or mechanical validity.

The proposed interaction therefore has several live explanations: joint sensitivity to two synthetic intensity patterns, receptive-field coupling, CTA boundary artifacts, or ordinary nonlinear network behavior. A no-op warp and an image discriminator could reject some implementation artifacts, but neither makes the counterfactual a measurement of compliance. The design also cannot identify the claimed phrase “beyond acute tissue injury,” because acute irreversible injury is not observed independently and follow-up edema-related displacement is not labeled. This is an identifiability failure, not merely a missing control or a Stage 0 uncertainty.

## Other adversarial findings

### Relevance and endpoint

The underlying benchmark concern is medically relevant: delayed post-treatment masks can encode processes not visible on hyperacute imaging, and subgroup-dependent boundary error matters. But the declared endpoints—predicted probability mass and radial boundary displacement under synthetic edits—measure model response, not actual infarct expansion, tissue displacement, or label contamination. “Radial” displacement is additionally underspecified for disconnected, irregular stroke lesions; its origin, correspondence rule, and handling of new components are absent.

The winner's reported mean test Dice is only 0.285 with SD 0.213 (Ren et al., arXiv `2505.18424`; challenge report arXiv `2408.10966`). On 24 edited cases, unstable or poorly localized base predictions can dominate boundary summaries. The card gives no effect size, variance estimate, multiplicity rule for two endpoints and multiple doses, or minimum detectable interaction. “Twenty low and twenty high” in Stage 0 does not establish power for the later 24-case within-case interaction.

### Confounding and circularity

The card says an age shortcut predicts only a CSF main effect. That is too strong. A nonlinear network can interact an atrophy/age feature with lesion attenuation or lesion extent without representing pressure-vessel mechanics. The factorial interaction distinguishes additive main effects; it does not uniquely distinguish compliance from age-conditioned nonlinear prediction.

There is also concept-label circularity in the water-uptake arm. NWU requires defining an early lesion region from the same acute image/perfusion evidence whose downstream prediction is being perturbed. If the edited region is selected from the model, threshold maps, or final label, the response can reflect lesion-location selection or target leakage. The card never fixes an independent region-of-interest construction. Using the follow-up mask to place the acute edit would be direct target leakage; using an acute threshold mask would test dependence on that thresholding algorithm.

### Data, model, and compute

Data access and compute are not fatal. The public training archive, released winner code, and public weights pointer make a load probe and fewer than 200 forward passes plausible. However, weight bytes and challenge-level reproduction remain unverified, and the hidden test set is unavailable. Any revised study must freeze a patient-level split before inspecting subgroup results and must not use training cases as if they were an untouched evaluation cohort.

No new expert annotation is required by the current plan, but a defensible compliance claim would require information that ISLES'24 lacks: follow-up mass effect/edema or deformation measurements, ideally serial imaging or an independently validated physical surrogate. Automatically deriving those labels from the same follow-up infarct image would not supply independent validation.

### Prior-work and novelty

**Verified primary neighbors.** Kauw et al. tested baseline NCCT CSF/ICV for malignant-edema prediction in 683 thrombectomy patients (40 malignant-edema events; DOI `10.1177/17474930221094693`, PMID `35373655`). Broocks et al. tested acute NWU for malignant infarction (DOI above). These establish association/prediction legwork, not model use. The ISLES'24 papers and released winner establish the benchmark and checkpoint.

I found no verified primary-source duplicate of a CSF-reserve audit of an ISLES'24 final-infarct model. That is not proof of novelty, and novelty cannot rescue a non-identifying experiment. The card's claim that no prior study audits the intersection should remain a limited-search statement, not a novelty claim.

### Negative-result value

A null would remain weak after the proposed gates. It could mean the model ignores CSF appearance, the CTA channel does not preserve a usable CSF signal, the post-normalization edit is off-manifold, the two artificial factors do not instantiate reserve and edema, the receptive field misses the edited spaces, or 24 cases are underpowered. The card correctly scores negative-result value at 2; in practice the present experiment is closer to 1 until a construct-valid intervention exists.

## Plain-pitch fidelity

**Named defect: overclaiming by translation.** “The same simulated tissue swelling” is stronger than the technical card. The experiment changes an attenuation pattern intended to represent net water uptake; it neither simulates swelling mechanics nor validates tissue displacement. “Learned to use that spare space when drawing the future infarct” also drops the card's crucial limitation that a positive result would show at most use of a geometric input prior, not biological expansion of irreversible infarction. The pitch must retain both limitations if reused.

## Easier version and low-hanging fruit

The genuinely low-hanging-fruit formulation is a **reserve-stratified benchmark error audit**, not a synthetic compliance intervention. Use the existing NCCT to compute baseline CSF/ICV, the existing follow-up infarct mask as the benchmark target, and the released winner checkpoint to obtain per-case predictions on a frozen held-out split. Test whether signed volume error, absolute volume error, lesion-wise recall, and a prespecified surface-distance metric differ across continuous CSF/ICV after adjustment for age, site, acute lesion/perfusion burden, and available reperfusion covariates. Report raw strata as well as adjusted estimates; do not call the association model use, compliance, edema, or label leakage.

This version has data, labels, code, and a checkpoint already in hand. It is one load/reproduction gate plus inference away from an answer and avoids inventing anatomically impossible counterfactuals. It remains useful because a consistent error gradient would identify a concrete reliability subgroup and motivate external validation or targeted labels; a sufficiently precise null would bound that subgroup concern. It cannot establish why the gradient exists, and the small public cohort makes confidence intervals and covariate sparsity central.

NEAREST DEFENSIBLE HIGH-VALUE QUESTION: Does the released ISLES'24 winner's held-out final-infarct error vary with baseline NCCT CSF/ICV after prespecified adjustment for age, site, acute lesion burden, perfusion deficit, and available reperfusion variables?
RETAINS ORIGINAL MEDICAL MOTIVATION? PARTLY
SHOULD IT BECOME A SEPARATE CANDIDATE? YES
IS IT ACTUALLY WORTH DOING? Yes—if a frozen held-out subset and precision target are feasible, it is a cheap, clinically interpretable subgroup-reliability audit whose positive or bounded-null result would improve how the benchmark model is evaluated.
