# Direct-download interpreter correction

The preserved first download sandbox exited2 before Python started. Its stderr
reported that /opt/conda/bin/python did not exist; its data Volume is empty.
The base image was already pinned, but the launch path was an unchecked Conda
assumption. The registry manifest and config were retrieved read-only and their
SHA256 values verified against that exact image. Config history installs Ubuntu
python3/python-is-python3 and copies Python3.12 packages. Use /usr/bin/python3.

Only the interpreter path changes. Image, code/plan hashes, package mount,
read-only source, network allowlist, data selection, credentials exclusion and
spending bounds remain unchanged. Existing provider tests verify the actual
Sandbox.create argument and all surrounding confinement/volume settings.

This correction alone does not retry the failed attempt. Preserve its original
intent, terminal proof and reservation. A supported linked recovery, normal
review and held deployment are required before another launch. No existing
ledger row, volume, provider record or installed release has been changed.
