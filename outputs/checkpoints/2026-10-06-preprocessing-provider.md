# Preprocessing provider checkpoint - 6 October 2026

Private implementation candidate: 869b75511d1a7389d8cfb53e968eaf9501e17833.
The installed release is unchanged; this draft has not been independently reviewed or deployed.

CPU preprocessing now connects to the existing executor and spending controls,
with authenticated source selection, bounded package-file inventory delivery,
and collection of original validation metadata. Data remain on private storage.
Training can select only the validated preprocessing output directory through a
read-only mount. Its preparation requires the original execution and validation
receipts. Repeated collection is tested to preserve records and the single charge.

Validation on the exact commit: 986 tests and 31 subtests passed in the affected
45-module regression, with eight documented platform skips. A separate native-root
provisioning run passed all 36 tests without skips. Scientific results, environment
observations and provider responses in these tests are synthetic fixtures.
These are not full server-suite results or evidence of a completed experiment.

Next: connect the normal driver to preprocessing dispatch and result publication;
verify the actual source view, dependencies, interrupted-work continuation and live
mount behavior; complete integrated server tests and independent review before
installation. No new model call, paid job, benchmark, training or diagnostic ran.
The completed development-data retrieval is preserved and will not be repeated.

M4 remains incomplete. The author account renewal remains an operator action;
independent engineering continues. This checkpoint contains no patient-level data,
private evidence, credentials or infrastructure details.
