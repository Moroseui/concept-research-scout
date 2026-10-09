# Verified input recovery at item4 admission

The experiment branch includes the reviewed 9497dc1d download recovery. Item4
compute admission now calls the same exact provenance/ledger validator before
checking asset uncertainty. Only the original failed row with a verified linked
child ceases to block. The original row, outcome and full reservation remain;
both reservations count toward the smoke/total caps and billing headroom.

This does not launch a recovery or a fit, and does not accept scientific work.
Unrelated uncertain assets, incomplete recovery, changed provenance and an
exhausted cap still refuse before any new compute reservation.

Tests/test_item4_recovery_admission.py uses real scratch release records and
SQLite, with root provenance and the incident ID explicitly synthetic. Neither
recovery validation nor item4 admission is patched. Canonical initialized-owner
validation is exercised by test_experiment_compute_owner.py. No provider or
model call is involved. The combined execution candidate still requires its
ordinary full-suite and independent implementation review before installation.
