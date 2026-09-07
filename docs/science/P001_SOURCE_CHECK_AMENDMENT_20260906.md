# P001 source check — evidence amendment, not a specification change

Investigator: Astra. This check follows the first charter proposal's bound context;
that proposal and its review are preserved unchanged.

The [dataset paper](https://arxiv.org/pdf/2408.11142), Methods pp. 5–6,
reports follow-up MRI 2–9 days after CT and reperfusion therapy. It describes
near-complete/complete recanalization as an inclusion condition. This limits
extrapolation beyond the released treated cohort. It describes motion correction,
one-frame-per-second temporal resampling, icobrain-derived perfusion maps,
rigid CT and affine MRI registration into NCCT space. This supports the stated
input timing and label-space provenance; it does not validate an individual file.

The inspected text does not explicitly identify the numeric units of released
Tmax voxel values. One-frame-per-second acquisition/resampling is insufficient
proof of exported voxel-value scaling. The existing seconds assumption therefore
remains explicit. Before launch, seek accompanying export metadata or authoritative
release documentation; conflicting evidence requires an amendment, not an invisible
scale correction. No patient image or archive was opened for this check.

Disposition: supply this amendment to the next system readiness discussion and
opposing review. It grants no ratification or execution authority. The earlier
source note and frozen specification remain intact.
