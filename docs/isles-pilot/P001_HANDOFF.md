# P001 is ready for Colab

[Open the exact P001 notebook](https://colab.research.google.com/github/Moroseui/concept-research-scout/blob/1a81c037343598f4e4585153b11d761b87a9ae3a/campaigns/isles24-pilot/experiments/P001/colab_P001.ipynb).

1. Connect a **CPU** runtime and allow your Drive mount.
2. Set `ARCHIVE` to your existing `train.7z` path. Alternatively set `DATA_ROOT`
   to an existing selectively staged tree; the runner verifies the selected files.
3. Choose **Runtime → Run all**. Keep the output folder on your own Drive.

The notebook selects the frozen 99 eligible cases and extracts only their 198
specified members. It does not select a follow-up experiment or publish results.
A failure preserves checkpoints and the original sibling console. Do not change
thresholds, suppress failures or omit cases; return the evidence for inspection.
Archive verification/extraction is separately timed from the 60-minute analysis
cap. For a runtime missing `7z`, install `p7zip-full` before running; Google's
[published CPU package inventory](https://github.com/googlecolab/backend-info/blob/main/apt-list.txt)
currently lists it as installed (checked 2026-09-05; this is not a measurement of
your connected runtime). Python requirements are installed by the notebook.

The default return location is `MyDrive/isles-pilot/P001-v1`. Preserve that
aggregate folder, `P001-v1.console.log`, and the `P001-v1.private` audit folder.
For local validation, make the aggregate folder, original console, binding/index,
per-case checkpoints and predictions available outside Git. Staged input images
can stay on your private Drive. Never send private audit files or patient data
to Claude or publish them to Git. Failure records also remain private.

## Exact provenance

- Reviewed implementation: `469d29df002ea78f64146731244769d7c82330d6`.
- Actual completed Fable approval adopted: `240e11f18aec01dfccd28da927a389492f08ea02`.
- Built-in campaign build: `aeef70c62f6de9509cf9f7230c3777e7aadfa484`.
- **Executable source / verification:** `d6a1184b4378e849213fd887a6f7b103fb1a64d5`.
- Notebook artifact: `1a81c037343598f4e4585153b11d761b87a9ae3a`.

The notebook fetches only the exact source pin at depth one, without tags or
other branches. All 19 reviewed source/test bindings and the actual approval
receipt were verified in that source tree. The actual generated acquisition cell was also executed locally against GitHub:
it fetched only the source commit, lacked the contaminated commit, passed the
review gate and preflight with zero patient payloads opened (see
REMOTE_SOURCE_VERIFICATION.json). This was not Colab execution.
Both notebooks validate, compile,
and contain no saved execution output. The full 233-test suite passed; actual
built-in P001 build/verify/package commands completed and committed their receipts.

No patient prediction result exists yet. The return validator reproduces
aggregates from private checkpoints; it does not independently re-evaluate image
geometry or labels. Interpretation and opposing-family review follow validation.
Only then may an investigator fix and review the next comparison specification.

## Optional MCP route

The [synthetic notebook](https://colab.research.google.com/github/Moroseui/concept-research-scout/blob/1a81c037343598f4e4585153b11d761b87a9ae3a/campaigns/isles24-pilot/colab/synthetic_execution.ipynb)
can be run manually without Drive or patient data. Local execution/retrieval and
a generic Colab MCP handshake passed; execution/retrieval through authenticated
Colab remains unverified. Follow COLAB_MCP.md to configure and authenticate the
synthetic test first. P001's manual Run All route does not depend on MCP.

The separately reviewed 047 cleanup operation still requires explicit operator
approval. Running P001 grants no permission for that remote history rewrite and
resolves none of 047's scientific acceptance decisions.
