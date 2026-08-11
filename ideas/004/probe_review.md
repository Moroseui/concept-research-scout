# Probe code review — idea 004 (load probe, contract v1) — ROUND 2

**Reviewed artifacts:** `probes/004/run.py` (1,061 lines, revision commit
f238a49), `probes/004/requirements.txt` (new), `probes/004/README.md`,
`probes/004/verification.json`. Round-1 review (commit b48c464) issued REVISE
with five blocking findings B1–B5; this round verifies the fixes and re-reviews
the result.

**Review method.** Re-fetched the official CT-CLIP sources on 2026-08-12 and
compared against the revised driver: `scripts/ct_lipro_inference.py` (imports,
`ImageLatentsClassifier` incl. `forward`/`load`, checkpoint-load line, inference
call site), `scripts/data_inference_nii.py` (`CTReportDatasetinfer.__init__`
signature, three-level glob, `__getitem__` return arity), `scripts/eval.py`
(imports), `transformer_maskgit/setup.py` and `CT_CLIP/setup.py`
(`install_requires`), and the package `__init__` chains
(`transformer_maskgit/__init__.py` → `MaskGITTransformer.py`, `ctvit_trainer.py`;
`ct_clip/__init__.py` → `ct_clip.py`).

**Verdict: REVISE.** All five round-1 blockers were addressed in intent, and
B1 (the model-call signature) and B5 (`--output-dir`) are fixed and verified.
But the B2/B4 remedy — installing the released packages with
`pip install --no-deps -e` from inside the running probe — cannot work as
implemented: the environment it builds is missing verified import-time
dependencies, and even a fully provisioned editable install is not importable
by the process that performed it. A second, narrower residue of B3 remains:
non-ImportError environment failures inside PHASE 4 (no GPU, tokenizer
download, torch/torchvision ABI errors) still misroute to contract exit 5.
Both are small, mechanical fixes; nothing touches the experiment's scope.

---

## Round-1 blocker status

| # | Status | Evidence |
|---|---|---|
| B1 (call signature) | **FIXED, verified** | `run.py:952` now `model(False, text_tokens, video, device=device)`. Released call site (fetched 2026-08-12): `output = model(False, text_tokens, inputs, device=device, return_latents=True)`. The omitted `return_latents=True` is a no-op difference — released `forward` unconditionally sets `kwargs['return_latents'] = True`. Load path also matches: released `.load()` is `torch.load(file_path)` + `load_state_dict` (default strict); driver's `map_location="cpu"` + `.cuda()` and explicit `strict=True` (`run.py:887-891`) are equivalent, and `weights_only=False` matches released behavior under the pinned torch. |
| B2 (import path) | **ATTEMPTED, defective** | Editable-install approach adopted (`run.py:756-774`) but fails in-process — see R1. |
| B3 (exit-code routing) | **MOSTLY FIXED** | Phase 1 now fails fast at exit 11 per missing dependency (`run.py:296-304`); PHASE 4 `ImportError`/`ModuleNotFoundError` separately routed to 11 (`run.py:895-897, 933-935`). Non-ImportError environment failures still leak to exit 5 — see R2. |
| B4 (requirements.txt) | **PARTIAL** | File exists with driver pins and the `weights_only` choice is explicit. But the released packages' import-time dependency set is absent and `torchvision` is unpinned — see R1. |
| B5 (--output-dir) | **FIXED, verified** | `run.py:1026-1037`; coder's smoke run wrote all seven artifacts to an external dir (`verification.json`). |

## Blocking findings

### R1. Real mode cannot reach the released imports on a fresh session — the `--no-deps` in-process editable install is triply defective (rule 5: practicalities; rule 2: one branch yields a false contract result)

`run.py:764-774` runs `pip install --no-deps -e` on the two released projects
after the interpreter has started, then imports them at `run.py:865-867` in the
same process. Three independent defects:

**(a) `--no-deps` skips dependencies the released packages need at import
time, and `requirements.txt` does not supply them.** Verified from the fetched
sources: `from transformer_maskgit import CTViT` executes the package
`__init__`, which imports `MaskGITTransformer.py` (→ `beartype`, `einops`) and
`ctvit_trainer.py` (→ `torchvision`, `einops`, `ema_pytorch`, `accelerate`,
`beartype`); the released `setup.py` additionally pins
`vector-quantize-pytorch==1.1.2` (pulled by `ctvit.py`, and API-sensitive — the
released code predates that library's breaking changes, so "latest" is not a
substitute). `from ct_lipro_inference import ImageLatentsClassifier` imports
`eval.py` → `h5py`, `matplotlib`, `seaborn`, `scipy`, `PIL`, `torchvision`.
Of this set, `probes/004/requirements.txt` pins none; `ema-pytorch` and
`vector-quantize-pytorch` are not in stock Colab at all. Result: guaranteed
`ModuleNotFoundError` → exit 11 on every run until the human hand-installs
packages documented nowhere.

**(b) An editable install performed mid-process is not importable by that
process.** `pip install -e` registers the package via a `.pth`/import-hook file
in site-packages, which the `site` module processes only at interpreter
startup. So even with every dependency present, the first invocation of
`run.py` installs the packages and then fails its own imports at
`run.py:865-866` → exit 11; only a rerun (new interpreter) can succeed. The
shipped one-command probe deterministically fails its first real invocation in
a perfect environment.

**(c) `torch==2.5.1` is pinned without a matched `torchvision`.** On Colab,
force-installing torch 2.5.1 under the preinstalled (newer, ABI-mismatched)
torchvision makes `import torchvision` raise `RuntimeError` (custom C++ ops),
not `ImportError` — which the PHASE 4 handler routes to
`fail(5, "released checkpoint/code failed to load unchanged")`
(`run.py:898-899`): a pip problem recorded as the contract-invalidating result
the probe exists to test. This sub-case is rule 2, not just rule 5.

**Required fix (any one of):** provision before the interpreter starts —
extend `requirements.txt` with the verified import-time set
(`torchvision==0.20.1` to match torch 2.5.1, `vector-quantize-pytorch==1.1.2`,
`ema-pytorch`, `einops`, `beartype`, `accelerate`, `h5py`, `matplotlib`,
`seaborn`, `scipy`) and move the two `-e` installs to a documented pre-step in
README (drop them from `run.py`, keeping only a PHASE 1 importability check);
**or** keep everything in-process but replace pip with the round-1 alternative:
`sys.path.insert` of the two inner package parents
(`vendor/CT-CLIP/transformer_maskgit` and `vendor/CT-CLIP/CT_CLIP`), which
needs no `.pth` processing — still with the transitive pins added. Either way,
verify with a clean-venv `pip install -r` + import smoke test.

### R2. Non-ImportError environment failures inside PHASE 4 still misroute to contract exit 5 (rule 2: silent-failure surface — same class as round-1 B3)

The B3 fix catches only `ImportError`/`ModuleNotFoundError`. Three concrete
environment failures raise other exception types inside the PHASE 4 try-block
and land in `except Exception → fail(5)` (`run.py:898-899`) — recorded as
contract `invalidating_failures[2]`:

- **CPU-only runtime** (the most common Colab slip): PHASE 1 logs
  `"gpu: NONE VISIBLE"` and continues (`run.py:292-295`); `model.cuda()` at
  `run.py:892` then raises `RuntimeError` → false exit 5. One-line fix: in
  real mode, `fail(11)` from PHASE 1 when `torch.cuda.is_available()` is
  False.
- **Tokenizer/text-encoder download**: `BertTokenizer.from_pretrained` /
  `BertModel.from_pretrained` (`run.py:870-872`) fetch
  `microsoft/BiomedVLP-CXR-BERT-specialized` from the network inside the try;
  an HTTP/OSError failure is an access problem (exit 3 family), not "released
  checkpoint/code failed to load unchanged". Route it separately.
- **torch/torchvision ABI mismatch** — R1(c) above.

The probe's exit codes feed the ADVANCE/kill decision (its own docstring);
every environment-shaped failure must be unreachable from exits 3–9.

## Non-blocking findings (carried or new)

1. **Contract secondary metrics still not persisted** (round-1 #2, unaddressed;
   coder scoped the revision to blockers only). Peak GPU memory
   (`run.py:954-955`) and per-execution seconds (computed in
   `run_three_executions`) go to `run_log.txt` only; `summary.json` has
   `total_minutes` alone. The contract lists these as secondary metrics — add
   them to `summary.json`; they are already computed.
2. **`torch.use_deterministic_algorithms(True)`** (round-1 #3, unaddressed):
   an op without a deterministic CUDA implementation raises `RuntimeError`
   during scoring → caught at `run.py:965-966` as `fail(9, "inference
   crashed")`. Catch that specific error distinctly or use `warn_only=True`
   with the empirical bit-identity check as arbiter.
3. **Qualifying-pair count logged but not gated** (round-1 #4, partially
   addressed): `run.py:817-819` now prints the Stage-0 reference count of 237
   with a warning sentence, but nothing stops a wildly divergent count. A
   sanity band would make the cross-check enforceable.
4. **Reruns clobber prior artifacts** (round-1 #6, unaddressed):
   `run.py:1039` truncates `run_log.txt`; all outputs overwrite in place. More
   salient now that R1(b) forces at least one rerun and `--output-dir` may
   point at a persistent Drive folder holding the previous attempt.
5. **Approval-flag discrepancy** (round-1 #1, human action still pending):
   `probe_contract.yaml` ends `human_approved: false` while the committed
   `HUMAN_APPROVED_PROBE` marker is the gate the code checks; the docstring now
   documents this (`run.py:6-9`), which is an improvement, but the flag should
   be flipped by the human in a commit.
6. **Trivial:** `device = torch.device("cuda")` (`run.py:858`) is used only in
   the model call while `.cuda()` strings appear elsewhere; harmless
   inconsistency.

## Verified faithful this round (no action)

- Staging layout `stage/valid/valid_P/valid_P_S/*.nii.gz` matches the released
  three-level glob in `prepare_samples` (fetched source), and the 4-tuple
  unpack at `run.py:921` matches `__getitem__`'s
  `return video_tensor, input_text, onehotlabels, name_acc`.
- `CTReportDatasetinfer(data_folder=..., reports_file=..., meta_file=...,
  labels=...)` matches the released `__init__` signature; both staged volumes
  have rows in the official reports/labels/metadata tables by construction.
- Head-order check against the released labels CSV columns, split guards on
  every download, provenance-before-inference ordering, contract-cap
  assertions, bit-identity via raw bytes, and the smoke mode's planted-decoy
  self-tests are unchanged from round 1 and remain correct.
- Scope discipline held: the diff touches only the five blockers plus their
  documentation; no new analysis, no extra executions, no contract drift.

```json
{"verdict": "REVISE", "blocking": ["R1: real mode cannot reach the released imports — `pip install --no-deps -e` at run.py:764-774 omits verified import-time deps (ema-pytorch, vector-quantize-pytorch==1.1.2, einops, beartype, accelerate, torchvision, h5py/matplotlib/seaborn/scipy via eval.py) that requirements.txt does not pin, a mid-process editable install is not importable until the next interpreter start, and the unmatched torch==2.5.1/torchvision pair turns a Colab ABI mismatch into a false exit-5 contract failure", "R2: non-ImportError environment failures inside PHASE 4 still misroute to contract exit 5 (run.py:898-899) — a CPU-only runtime (phase 1 logs 'gpu: NONE VISIBLE' and continues, run.py:292-295, then model.cuda() raises RuntimeError) and a failed tokenizer/BERT download (run.py:870-872) would both be recorded as 'released checkpoint/code failed to load unchanged'"], "note": "B1 and B5 verified fixed against the released sources and B3 mostly fixed; the remaining defects are environment provisioning and exit-code routing, both mechanical, neither touching experiment scope."}
```
