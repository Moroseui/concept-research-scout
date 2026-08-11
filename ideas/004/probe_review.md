# Probe code review — idea 004 (load probe, contract v1)

**Reviewed artifacts:** `probes/004/run.py` (1,014 lines), `probes/004/README.md`,
`probes/004/verification.json`, `probes/004/.gitignore`. **Note:** the stage names
`run.py` + `requirements.txt` as the generated pair; no probe `requirements.txt`
exists (the repo-root `requirements.txt` is the scout harness's, not the probe's).

**Review method.** The coder's `verification.json` marks `released_api_fidelity`
as `PASS_WITH_CAVEAT` because their sandbox could not execute or test anything
against the released code. I closed that caveat by fetching the official CT-CLIP
sources on 2026-08-12 (repo tree; raw `scripts/ct_lipro_inference.py`; raw
`scripts/data_inference_nii.py`; `CT_CLIP/` and `transformer_maskgit/` listings)
and comparing them line-by-line against the transcriptions in `run.py`. Much of
the transcription is accurate — but two load-bearing pieces are wrong, and both
would cause the probe to report a **contract invalidating failure whose true
cause is a driver bug**. That is the one outcome this probe must never produce:
per its own docstring, exits 3–9 are contract results that feed the ADVANCE/kill
decision for idea 004.

**Verdict: REVISE.** The harness scaffolding (gate, split guards, deterministic
pair selection, provenance-before-inference, bit-identity check, budget caps,
output files) is genuinely good and should be kept as-is. The defects are
confined to real mode's PHASE 4 and the environment story.

---

## Blocking findings

### B1. The model call does not match the released forward signature — guaranteed wrong result (rule 2: silent-failure surface; rule 1: contract fidelity)

`run.py:913`:

```python
logits = model(text_tokens, video)
```

Released `scripts/ct_lipro_inference.py` (fetched 2026-08-12, verbatim):

```python
def forward(self, latents=False, *args, **kwargs):
    kwargs['return_latents'] = True
    _, image_latents, _ = self.trained_model(*args, **kwargs)
    image_latents = self.relu(image_latents)
    if latents:
        return image_latents
    ...
    return self.classifier(image_latents)
```

and the released call site:

```python
output = model(False, text_tokens, inputs, device=device, ...)
```

`run.py`'s call binds `text_tokens` to the `latents` **flag** and passes only
`video` into `self.trained_model(...)` — i.e. `CTCLIP.forward` receives the CT
volume as its `text` argument and no image at all. Two possible outcomes, both
fatal to the probe's purpose:

- **Most likely:** `TypeError` inside `CTCLIP.forward` → caught at
  `run.py:926-927` → `fail(9, "inference crashed")` → reported as contract
  `invalidating_failures[6]` ("crashes"). A healthy released pipeline would be
  recorded as an invalidating contract failure.
- **If it somehow does not crash:** `latents` is truthy (a `BatchEncoding`), so
  `forward` returns the 512-dim latent vector, not 18 logits → `fail(6)` →
  reported as contract `invalidating_failures[3]` ("does not emit exactly 18
  scores"). Same misdiagnosis, different exit code.

**Required fix:** mirror the released call verbatim —
`model(False, text_tokens, video, device=device)` — including the `device`
kwarg the released loop passes. (The rest of the load block is a faithful
transcription: the `CTViT`/`CTCLIP` constructor arguments at `run.py:845-855`
and the 18 head names at `run.py:100-119` match the fetched source exactly, and
`CTReportDatasetinfer(data_folder=..., reports_file=..., meta_file=...,
labels=...)` at `run.py:881-883` matches the released signature
`(data_folder, reports_file, meta_file, min_slices=20, labels="labels.csv")`.)

### B2. The `sys.path` import strategy cannot resolve the released packages — real mode dies at exit 5 falsely (rule 5: practicalities; rule 2: silent-failure surface)

`run.py:830-831` inserts the clone root and `scripts/` onto `sys.path`, then
`run.py:837-838` does `from transformer_maskgit import CTViT` and
`from ct_clip import CTCLIP`. Verified repo layout (fetched 2026-08-12): both
are **installable projects**, not flat modules —
`transformer_maskgit/setup.py` + inner `transformer_maskgit/` package, and
`CT_CLIP/setup.py` + inner `ct_clip/` package. The released README installs
them with `cd transformer_maskgit && pip install -e .` and
`cd CT_CLIP && pip install -e .`. With only the clone root on `sys.path`,
`ct_clip` does not exist as a top-level importable name at all, and
`transformer_maskgit` resolves to the outer project directory (a namespace
package with no `CTViT`). The import raises, is caught by the blanket handler
at `run.py:864-865`, and becomes `fail(5, "released checkpoint/code failed to
load unchanged")` — contract `invalidating_failures[2]`, the exact claim the
probe exists to test, asserted on a driver environment gap.

**Required fix:** install the two released packages the way the released README
does (e.g. `pip install -e` on both project dirs from the pinned clone, recorded
in `provenance.json`), or insert the correct inner directories; and see B3 for
the exception routing.

### B3. Missing-dependency and ImportError paths are mapped to contract invalidating exits instead of exit 11 (rule 2: silent-failure surface)

The probe's own exit-code scheme says 11 = "missing dependency (environment,
not a contract result)". But in real mode:

- `run.py:295-300` records third-party modules as `"MISSING"` in
  `environment.txt` and **continues** instead of `fail(11)`.
- The PHASE 4 load block (`run.py:832-865`) wraps all imports — including
  `ct_lipro_inference`, whose module top-level (verified) imports `src.args`,
  `eval` (which pulls sklearn/matplotlib-class dependencies), `tqdm`, `pandas`,
  `numpy`, `sklearn` — in `except Exception → fail(5)`. A missing `sklearn`
  becomes "checkpoint failed to load unchanged."
- The preprocessing block (`run.py:870-900`) maps any exception, including
  ImportError from `data_inference_nii`'s dependencies (`nibabel`, `tqdm`), to
  `fail(7)` — contract `invalidating_failures[4]`, "pair fails the released
  preprocessing," on a pip problem.

**Required fix:** fail fast at PHASE 1 (exit 11) if any real-mode dependency is
missing, and catch `ImportError`/`ModuleNotFoundError` separately from other
exceptions in PHASE 4, routing them to exit 11 with an explicit "environment,
not a contract result" message.

### B4. No probe `requirements.txt` with pins (rule 5: practicalities; named stage deliverable)

The stage deliverable pair is `run.py` + `requirements.txt`; only `run.py` was
produced. `probes/004/README.md:19-21` lists five unpinned package names and
omits the two editable installs (B2) plus the transitive set (`sklearn`,
`tqdm`, whatever `scripts/src/` and `eval.py` pull in). Version pinning is not
cosmetic here: `run.py:857` calls `torch.load(...)` without `weights_only`,
whose default flipped to `True` in torch ≥ 2.6 — on a current unpinned Colab
torch, a checkpoint containing any non-tensor pickled object fails to load and
becomes another false exit-5 invalidating failure. Unpinned `transformers`
similarly risks tokenizer/`BertModel` behavior drift against 2024-era released
code. **Required fix:** ship `probes/004/requirements.txt` with working pins
(torch, transformers, huggingface_hub, nibabel, pandas, scikit-learn, tqdm) and
the two `-e` installs documented, and pass an explicit `weights_only` choice to
`torch.load` that matches the released loader's behavior.

### B5. Outputs are hardcoded beside the script; no `--output-dir` (rule 5: practicalities — explicit checklist item)

`run.py:989` fixes the output directory to `probes/004/outputs`. The review
checklist requires the Drive output dir to come from `--output-dir`. In Colab
the clone lives on ephemeral VM disk, so a successful 45-GPU-minute gated run's
seven contract artifacts (and the frozen provenance hashes) vanish with the
session unless the human remembers to copy them. **Required fix:** add
`--output-dir` (default: current behavior) and write all seven required
outputs there. This does not add a contract "variant" — it relocates artifacts
only.

---

## Non-blocking findings

1. **Approval-flag discrepancy** (`ideas/004/probe_contract.yaml:` last line,
   `human_approved: false` vs the committed `HUMAN_APPROVED_PROBE` marker). The
   code documents and gates on the marker (`run.py:229-252`), which is
   defensible, but the approved preregistration document contradicting itself
   is the kind of thing a later reader trips over. Recommend the human flip the
   flag in a commit rather than any agent editing an approved contract.
2. **Contract secondary metrics not persisted in structured outputs.** Peak GPU
   memory (`run.py:915-916`) and per-execution wall-clock (`run.py:497`) go
   only to `run_log.txt`; download/model-load times are only inferable from log
   timestamps. The contract lists these as secondary metrics — put them in
   `summary.json` (they are already computed).
3. **`torch.use_deterministic_algorithms(True)`** (`run.py:288`) can raise on
   ops without deterministic CUDA implementations; that RuntimeError would land
   in the `fail(9)` bucket as a "crash." Since bit-identity is checked
   empirically anyway (`run.py:517-520`), consider catching that specific error
   and reporting it distinctly, or `warn_only=True` with the empirical check as
   the arbiter — documented either way.
4. **Qualifying-pair drift is logged but not gated** (`run.py:789-791`). If the
   re-derived rules diverge wildly from Stage 0's 237, the selected pair may
   not be in the frozen Stage-0 425. A sanity band (e.g., abort if count is 0
   or > 2× Stage 0's) would make the cross-check enforceable. Related repo gap,
   not a code defect: the Stage-0 pair list itself was never committed, which
   is why the code must re-derive it.
5. **`find_repo_file` ambiguity → exit 3** (`run.py:719-721`): two matching repo
   files is a naming-drift condition, not an "access failure"; the message is
   clear enough, but the exit-code mapping is loose.
6. **Reruns clobber prior artifacts** (`run.py:992` truncates `run_log.txt`;
   all outputs overwrite in place). For a probe whose artifacts are the
   deliverable, refusing to overwrite an existing `summary.json` (or
   timestamping the output dir) would be safer.
7. **Readability is good.** Docstring explains the experiment and the exit-code
   map; phases are narrated; constants carry provenance comments; smoke mode's
   planted decoys are self-asserting. No blocking readability findings.
8. **Trivial:** released code tokenizes `""`, driver tokenizes `[""]`
   (`run.py:903`) — same batch of one; released readout applies a hand-rolled
   sigmoid where the driver uses `torch.sigmoid` (`run.py:914`) —
   mathematically identical, only internal consistency matters for this probe.

## What was verified as faithful (kept, no action)

- Contract caps re-read and asserted at startup (`run.py:243-251`); executions,
  seed, batch size hardcoded; no CLI knobs beyond `--smoke` (rule 1 satisfied
  in structure).
- All seven `required_outputs` written in both modes; provenance (HF revision,
  checkpoint SHA-256, code commit, table and volume hashes) recorded **before**
  inference (`run.py:753-782, 812-815`).
- Split guards on every download and both pair members; pair-validity
  assertions; labels used only for the head-order check, never in an endpoint.
- Bit-identity via raw byte comparison, not tolerance (`run.py:517-520`).
- Claim discipline: smoke `contract_satisfied: false`; A-vs-B differences
  labeled `DIAGNOSTIC_ONLY` everywhere; interpretation strings track the
  contract's positive/negative-pattern language, never stronger.
- The 18 head names, their order, and the `CTViT`/`CTCLIP` constructor
  arguments match the released source exactly (fetched 2026-08-12).

```json
{"verdict": "REVISE", "blocking": ["B1: model call `model(text_tokens, video)` (run.py:913) misbinds text_tokens to the released forward's `latents` flag and passes the CT volume as CTCLIP's text argument; must be `model(False, text_tokens, video, device=device)` per released ct_lipro_inference.py — as written, a healthy pipeline is reported as contract invalidating failure 6 or 3", "B2: `from ct_clip import CTCLIP` / `from transformer_maskgit import CTViT` cannot resolve via sys.path insertion of the clone root (run.py:830-838); both are pip-install -e projects with inner packages, so real mode dies with a false exit-5 'checkpoint failed to load unchanged'", "B3: ImportError/missing-dependency paths are funneled to contract exits 5/7 instead of environment exit 11 (run.py:295-300, 864-865, 899-900), so a pip problem masquerades as a contract-invalidating result", "B4: probe requirements.txt (a named stage deliverable) is missing; unpinned torch risks the >=2.6 weights_only default breaking torch.load at run.py:857 as another false exit-5", "B5: no --output-dir flag (run.py:989); the stage's Colab practicality checklist requires it, and a successful gated run's artifacts die with the VM"], "note": "Scaffolding (gate, guards, provenance, bit-identity, caps) is faithful and well-narrated; PHASE 4's released-API transcription is broken in two load-bearing places, each converting a driver/environment bug into a contract invalidating failure."}
```
