# Probe code review — idea 004 (load probe, contract v1) — ROUND 5

**Reviewed artifacts:** `probes/004/run.py` (unchanged from approved revision
`759b664`), `probes/004/requirements.txt`, `probes/004/README.md`,
`probes/004/verification.json`, and `ideas/004/probe_contract.yaml`. This review
is limited to the decision-ledger-authorized exit-5 environment repair:
`transformers==4.30.1` and its compatible `tokenizers` cascade. The previously
approved one-pair, three-execution probe remains unchanged.

**Verdict: APPROVE.** The repair aligns model construction with the released
repository's documented Transformers pin without weakening strict checkpoint
loading or expanding the experiment. I independently compiled `run.py`, ran
`python probes/004/run.py --smoke --output-dir <temporary-directory>`, and
confirmed successful completion with all eight required artifacts, 54 per-head
rows, and `contract_satisfied: false`. I also ran a Python-3.11-targeted pip
dry-resolution of `transformers==4.30.1`, `tokenizers==0.13.3`, and
`huggingface-hub==0.22.2`; the resolver accepted the combination.

## Contract fidelity

- **No probe-logic or scope drift.** `run.py` is byte-unchanged from the Round-4
  approved revision, so the frozen pair selection, A/B/A-repeat execution count,
  one-seed limit, 45-GPU-minute cap, strict load path, output-shape checks, and
  required artifacts remain as previously reviewed.
- **The environment repair matches the ledger exactly.** The dependency file
  replaces the later Transformers release with `transformers==4.30.1` and adds
  `tokenizers==0.13.3`; its comments state both the released-repository provenance
  and the position-buffer incompatibility being tested
  (`probes/004/requirements.txt:8-15`). No checkpoint key is dropped, renamed, or
  loaded non-strictly.
- **The repair propagates through the existing run instructions.** The documented
  installation still consumes the single pinned requirements file before invoking
  the unchanged driver (`probes/004/README.md:17-25`).

## Silent-failure surfaces

No blocking silent-failure surface was introduced. A real run under the older
Transformers version still exercises the same strict checkpoint load and exits on
incompatibility; the version change does not catch or suppress that failure. The
README correctly says the prior exit-5 classification remains provisional until
the real checkpoint is tested under the released pin
(`probes/004/README.md:57-69`).

## Claim discipline

The smoke run remains explicitly non-scientific: its summary reports
`contract_satisfied: false` and says that it establishes nothing about checkpoint
compatibility or reconstruction sensitivity. The environment change introduces no
new data contact, variant, score analysis, threshold, or scientific conclusion.

## Readability and practicalities

The new requirements comments explain why the two versions are pinned and identify
their provenance (`probes/004/requirements.txt:8-14`). The README separately
narrates the exit-5 cause, the exact repair, and the required next evidentiary step
(`probes/004/README.md:57-69`). The targeted Python 3.11 dependency resolution
found no conflict among Transformers, Tokenizers, and Hugging Face Hub, which is
the compatibility surface changed in this revision.

## Non-blocking findings

1. **The real load result remains intentionally unknown.** Neither smoke mode nor
   dependency resolution can prove that `CT_LiPro_v2.pt` loads; that is the approved
   probe's primary metric, not a code-review defect.
2. **The committed verification note is historically stale.**
   `probes/004/verification.json` says Python execution was blocked during
   implementation. This review independently executed the smoke run successfully;
   no probe artifact or code change is required.
3. **A full requirements solve was not reproduced on this host.** Its Python 3.13
   environment has no wheel for the older pinned `torchvision==0.20.1`. That is not
   evidence of a Colab incompatibility and predates this revision; the changed
   three-package compatibility set resolves for Python 3.11.

```json
{"verdict": "APPROVE", "blocking": [], "note": "The r5 repair faithfully pins the released Transformers environment and a compatible tokenizer, leaves the approved probe logic unchanged, and passes compilation, smoke, and targeted dependency-resolution checks."}
```
