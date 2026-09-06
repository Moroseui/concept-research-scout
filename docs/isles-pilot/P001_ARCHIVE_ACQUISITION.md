# P001 input acquisition

The completed metadata search found only a size-mismatched Drive archive. Its
corruption status is unknown. The operator reported prior corruption and fresh
Colab downloads; the investigator selected a fresh immutable-release download.
The existing copy is preserved. No scientific specification or source pin changes.

`python -m orchestrator.colab_acquire start --private-dir PRIVATE_NEW_DIRECTORY`
requires a completed, source-bound independent Fable acquisition approval.
The separate worker uses the existing private MCP configuration and subscription.
Only the two exact, read-back cells execute. Reviewers have no worker MCP.

The CPU-only child downloads record 16813698 into
`/content/isles-p001-input-16813698/train.7z.part`. It requires the existing real
Drive mount and at least archive size plus 10 GiB free locally. It checks the
pinned 99,014,629,647 bytes and MD5 36ae28b9a17f7340b8bbef62b595cb57 before
renaming to `train.7z`. It never lists or extracts archive members. There is a
four-hour acquisition limit plus at most the current 120-second network read.
No paid provisioning, whole-archive extraction, or reserved-case analysis occurs.

The private Drive directory `MyDrive/isles-pilot/input-acquisition-16813698`
retains the exact child script, original console, status, and successful identity
receipt. Partial files remain locally on failure; reruns refuse existing paths.
Local partials cannot survive Colab runtime deletion. A dead process can leave a
stale RUNNING status; do not equate that status with progress or relaunch blindly.
Poll uses the same command with `poll` and a new private receipt directory.
Only fixed status and execution metadata reach model tools. CLI estimates are not
new subscription charges. Original local worker protocol stays outside Git.

Acquisition success is not P001 success. The separately approved patient adapter
must still pass its own review gate. The unchanged scientific runner rechecks
archive identity and selected-member integrity before analysis. Private logs and
checkpoints, semantic return validation, import, and interpretation remain required.
