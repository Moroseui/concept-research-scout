#!/usr/bin/env python3
"""Load probe for idea-004: can the released ClassFine checkpoint be frozen,
loaded unchanged, and made to emit deterministic 18-head scores for one pair?

Contract: ideas/004/probe_contract.yaml (v1, the section-9 "load probe").
Approval: ideas/004/HUMAN_APPROVED_PROBE (committed 2026-08-11), with the
contract's `human_approved` field synchronized to true in this revision. The
committed marker file remains the executable approval gate.

Revision 2026-08-12 (decision ledger "Probe 004 exit-7 root cause"): the real
run exited 7 because validation_metadata.csv stores ConvolutionKernel as a
stringified Python list ("['Br40f', '3']") while the selection predicate
compared the raw string to 'Br40f', matching zero rows. This revision, and
ONLY this revision: (1) the kernel field is normalized before comparison
(list literal -> element 0, otherwise the stripped raw string, robust to both
formats); (2) pair selection always writes selection_audit.json, and any
shortfall vs the frozen 237-pair count also dumps top-10 distinct kernel
values with counts, example VolumeNames, and per-filter drop counts to the
run log; (3) input_manifest.csv records each selected volume's normalized
(and raw) kernel from its own metadata row. Geometry list-string columns
compare same-format row-vs-row and are unchanged.

Revision r6 2026-08-12 (decision ledger "Probe 004 r5 environment dead end;
r6 pivot to enumerated-key-tolerant load"): the r5 released-environment pin
(transformers 4.30.1 / tokenizers 0.13.3) does not install on Colab Python
3.12, so requirements.txt is reverted to the r4 closure (transformers 4.38.2 /
tokenizers 0.15.2). transformers 4.31.0 made BERT's embeddings.position_ids a
non-persistent buffer, so the <=4.30-era checkpoint carries exactly one key a
4.38-era model does not expect. This revision, and ONLY this: before
load_state_dict, keys matching *.embeddings.position_ids (a non-learnable
arange buffer; the same keys from_pretrained drops across framework eras) are
removed from the loaded state dict. The removal is enumerated and audited:
the removed set must be EXACTLY ONE key matching that pattern (anything else
exits 5), the removed key is logged to the run log and provenance.json, and
strict=True loading is preserved so any OTHER unexpected or missing key still
exits 5. Startup logs the installed transformers version. Exit-5 semantics: a
load is "unchanged" modulo enumerated, provenance-logged framework-era buffer
keys only.

WHAT THIS PROBE IS, in one paragraph: CT-RATE stores several reconstructions
of the same CT acquisition. The eventual study asks how much the released
CT-CLIP "ClassFine" model's 18 abnormality scores move between two
reconstructions of identical anatomy. Before spending ~360 GB of downloads on
425 pairs, this probe tests only the load-bearing feasibility assumption: that
the officially linked checkpoint (CT_LiPro_v2.pt, hosted inside the CT-RATE
dataset repo) can be provenance-frozen (hashes recorded before inference),
loaded with the released code UNCHANGED, and run at batch size 1 on exactly one
predeclared geometry-matched Br40f|Br60f validation pair, producing exactly 18
finite named scores per execution, with a repeated run on reconstruction A
being bit-identical. Stopping rule: exactly three executions (A, B, A again),
one seed, hard stop on any invalidating failure or at 45 cumulative GPU
minutes. POSITIVE looks like: provenance recorded, checkpoint loads unchanged,
3/3 executions return 18 finite scores with a stable head-name order, repeat-A
bit-identical, within budget -- which authorizes only a REQUEST for approval of
the separate 425-pair contract. NEGATIVE/INVALIDATING looks like: gate or
download failure, un-hashable artifacts, load requiring code/weight changes,
wrong head count, pair failing the frozen Stage-0 matching rules, a
non-bit-identical repeat, or blowing the memory/time budget. The A-vs-B score
difference is logged as a pipeline diagnostic ONLY; per the contract it is
scientifically uninterpretable in either direction (one pair answers nothing).

Usage (one command):
    python run.py --output-dir /path/on/drive/idea004
                             # real probe (needs HF gate + token + GPU)
    python run.py --smoke    # synthetic, stdlib-only, no network/GPU; tests the
                             # harness plumbing, NOT the contract's assumption

Exit codes (each maps to a contract invalidating_failure or a harness fault):
    0   probe passed (or smoke completed)
    2   approval/contract gate failure (missing approval marker, cap mismatch)
    3   access failure: gate/token/download (invalidating_failures[0])
    4   provenance failure: cannot hash/pin artifacts (invalidating_failures[1])
    5   checkpoint load/compatibility failure (invalidating_failures[2]);
        "unchanged" is modulo the single enumerated, provenance-logged
        position_ids buffer key (r6) -- any other mismatch still exits 5
    6   output-shape failure: not exactly 18 finite named scores (invalidating_failures[3])
    7   pair-validity failure: Stage-0 rules or preprocessing (invalidating_failures[4])
    8   determinism failure: repeat-A not bit-identical (invalidating_failures[5])
    9   budget failure: memory/crash/45-GPU-minute cap (invalidating_failures[6])
    10  model/tokenizer access failure (environment, not a contract result)
    11  missing dependency/GPU (environment, not a contract result)
    12  unexpected internal error (not a contract result; do NOT reinterpret as negative)
"""

import argparse
import ast
import csv
import hashlib
import json
import os
import platform
import random
import re
import sys
import time
from pathlib import Path

# ---------------------------------------------------------------------------
# Frozen constants. Nothing below is tunable from the command line: the
# contract allows exactly one variant of this probe, so there are no knobs.
# ---------------------------------------------------------------------------

IDEA_ID = "idea-004"
SEED = 0  # fixed seed; maximum_seeds: 1 in the contract

PROBE_DIR = Path(__file__).resolve().parent
REPO_ROOT = PROBE_DIR.parent.parent
CONTRACT_PATH = REPO_ROOT / "ideas" / "004" / "probe_contract.yaml"
APPROVAL_PATH = REPO_ROOT / "ideas" / "004" / "HUMAN_APPROVED_PROBE"

# Caps copied from the contract; PHASE 0 asserts the contract still says this,
# so silent contract edits cannot loosen the probe.
MAX_GPU_MINUTES = 45
MAX_VARIANTS = 3
MAX_SEEDS = 1

# Official sources (feasibility.md section 1, inspected 2026-08-11).
HF_DATASET_REPO = "ibrahimhamamci/CT-RATE"
CHECKPOINT_REPO_PATH = "models/CT-CLIP-Related/CT_LiPro_v2.pt"
CTCLIP_GIT_URL = "https://github.com/ibrahimethemhamamci/CT-CLIP"
# Text tower used by the released CT-CLIP code (run_zero_shot.py / ct_lipro_inference.py).
TOKENIZER_NAME = "microsoft/BiomedVLP-CXR-BERT-specialized"

# The predeclared reconstruction contrast for the one probe pair. Br40f sorts
# before Br60f, so A = Br40f member, B = Br60f member (fixed rule, no choice).
KERNEL_A = "Br40f"
KERNEL_B = "Br60f"
# Stage 0 directly counted 237 clean pairs for this contrast. A different
# count means release contents or filtering logic drifted, so do not silently
# select from a changed manifest.
EXPECTED_QUALIFYING_PAIRS = 237

# The 18 head names in released order. Source: scripts/ct_lipro_inference.py in
# the official CT-CLIP repository (fetched 2026-08-11); the same order is the
# column order (from index 1) of the released multi-abnormality labels CSV.
# PHASE 3 asserts the released labels CSV columns equal this list, which is the
# contract's "stable head-name/order mapping" check.
EXPECTED_PATHOLOGIES = [
    "Medical material",
    "Arterial wall calcification",
    "Cardiomegaly",
    "Pericardial effusion",
    "Coronary artery wall calcification",
    "Hiatal hernia",
    "Lymphadenopathy",
    "Emphysema",
    "Atelectasis",
    "Lung nodule",
    "Lung opacity",
    "Pulmonary fibrotic sequela",
    "Pleural effusion",
    "Mosaic attenuation pattern",
    "Peribronchial thickening",
    "Consolidation",
    "Bronchiectasis",
    "Interlobular septal thickening",
]

# Stage-0 strict geometry matching (decision ledger 2026-08-04): a pair is
# clean only if the deterministic released preprocessing receives identical
# inputs for both members. Per the idea-004 debate (Round 2), the preprocessing
# shape is fully determined by RescaleSlope, RescaleIntercept, XYSpacing,
# ZSpacing and the source array dimensions -- so those must match exactly.
# Comparison is on the raw CSV strings: identical values, not "close" values.
REQUIRED_MATCH_COLUMNS = [
    "RescaleSlope",
    "RescaleIntercept",
    "XYSpacing",
    "ZSpacing",
    "NumberofSlices",  # slice-count drift was a Stage-0 exclusion
]
# Also matched when present in the metadata (Stage-0 excluded position and
# acquisition-parameter drift); each column actually used is recorded.
OPTIONAL_MATCH_COLUMNS = [
    "ImagePositionPatient",
    "ImageOrientationPatient",
    "PatientPosition",
    "SliceThickness",
    "ReconstructionDiameter",
    "KVP",
    "XRayTubeCurrent",
    "ExposureTime",
    "Exposure",
]
KERNEL_COLUMN = "ConvolutionKernel"

# Volume names look like valid_<patient>_<scan>_<recon>(.nii.gz).
VOLUME_NAME_RE = re.compile(r"^valid_(\d+)_([a-z]+)_(\d+)(?:\.nii\.gz)?$")

_LOG_FILE = None  # set once the output directory exists


# ---------------------------------------------------------------------------
# Small helpers: logging, hashing, output writing. No cleverness.
# ---------------------------------------------------------------------------

def log(msg):
    """Print progress to the terminal and append to run_log.txt."""
    line = f"[{time.strftime('%H:%M:%S')}] {msg}"
    print(line, flush=True)
    if _LOG_FILE is not None:
        with open(_LOG_FILE, "a") as f:
            f.write(line + "\n")


def fail(exit_code, reason):
    """Log the failure reason and stop with the contract-mapped exit code."""
    log(f"FAIL (exit {exit_code}): {reason}")
    sys.exit(exit_code)


def sha256_file(path, chunk=1024 * 1024):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            block = f.read(chunk)
            if not block:
                break
            h.update(block)
    return h.hexdigest()


def write_json(path, obj):
    with open(path, "w") as f:
        json.dump(obj, f, indent=2, sort_keys=True)
        f.write("\n")


def assert_validation_only(name):
    """Split guard: this probe may touch the validation split ONLY.

    Any path or volume name that is not clearly validation-split is refused,
    which enforces both "no test-set access" and "no train-volume access".
    """
    lowered = name.lower()
    if "test" in lowered:
        fail(7, f"split guard: refused test-split resource '{name}'")
    base = os.path.basename(lowered)
    # Volumes and per-volume metadata rows must be valid_* ; shared repo files
    # (checkpoint, metadata CSVs) must at least not be train/test-specific.
    if base.startswith("train_") or "/train/" in lowered:
        fail(7, f"split guard: refused train-split resource '{name}'")


# ---------------------------------------------------------------------------
# PHASE 0 -- GATE. The collaborator rules forbid probe code execution without
# a reviewed card, feasibility memo, contract, and explicit human approval.
# The first three are committed documents; the approval is the committed
# marker file. This phase also re-reads the contract's numeric caps so that
# the constants above cannot drift from the approved text unnoticed.
# ---------------------------------------------------------------------------

def parse_contract_scalars(path):
    """Minimal line-based YAML scalar reader (avoids a PyYAML dependency).

    Only top-level `key: value` scalars are needed; lists are ignored.
    """
    scalars = {}
    for line in path.read_text().splitlines():
        if line.startswith(" ") or line.startswith("-") or ":" not in line:
            continue
        key, _, value = line.partition(":")
        scalars[key.strip()] = value.strip().strip('"')
    return scalars


def phase0_gate():
    log("PHASE 0: approval and contract gate")
    if not CONTRACT_PATH.exists():
        fail(2, f"contract not found at {CONTRACT_PATH}")
    if not APPROVAL_PATH.exists():
        fail(2, f"human approval marker not found at {APPROVAL_PATH}; do not run")
    approval_text = APPROVAL_PATH.read_text().strip()
    log(f"  approval marker present: '{approval_text}'")

    contract = parse_contract_scalars(CONTRACT_PATH)
    if contract.get("idea_id") != IDEA_ID:
        fail(2, f"contract idea_id {contract.get('idea_id')!r} != {IDEA_ID!r}")
    # Caps must match the frozen constants exactly -- a mismatch means the
    # contract changed after this code was reviewed, so stop.
    for key, expected in [
        ("maximum_gpu_minutes", MAX_GPU_MINUTES),
        ("maximum_variants", MAX_VARIANTS),
        ("maximum_seeds", MAX_SEEDS),
    ]:
        got = contract.get(key)
        if got != str(expected):
            fail(2, f"contract {key}={got!r} does not match frozen constant {expected}")
    log("  contract caps match frozen constants (45 GPU min / 3 executions / 1 seed)")
    return {"approval_marker": approval_text, "contract_path": str(CONTRACT_PATH)}


# ---------------------------------------------------------------------------
# PHASE 1 -- ENVIRONMENT AND CONFIG. Fix every seed and determinism switch
# BEFORE any model code is imported or run, capture the environment for the
# record, and write the fully resolved configuration so the run is
# reproducible from the artifacts alone.
# ---------------------------------------------------------------------------

def phase1_environment(out_dir, smoke):
    log("PHASE 1: seeds, determinism switches, environment capture")
    random.seed(SEED)
    os.environ["PYTHONHASHSEED"] = str(SEED)
    # Required by CUDA for deterministic cuBLAS matmuls (bit-identity check).
    os.environ.setdefault("CUBLAS_WORKSPACE_CONFIG", ":4096:8")

    env_lines = [
        f"python: {sys.version.replace(chr(10), ' ')}",
        f"platform: {platform.platform()}",
        f"machine: {platform.machine()}",
        f"seed: {SEED}",
        f"CUBLAS_WORKSPACE_CONFIG: {os.environ['CUBLAS_WORKSPACE_CONFIG']}",
        f"mode: {'smoke' if smoke else 'real'}",
    ]
    if not smoke:
        try:
            import numpy
            import torch
            numpy.random.seed(SEED)
            torch.manual_seed(SEED)
            torch.cuda.manual_seed_all(SEED)
            # Determinism switches: the contract's bit-identity check is only
            # meaningful if nondeterministic kernels are disabled up front.
            torch.backends.cudnn.deterministic = True
            torch.backends.cudnn.benchmark = False
            # warn_only lets the empirical repeat-A bit check arbitrate if a
            # released CUDA operation lacks a deterministic implementation.
            torch.use_deterministic_algorithms(True, warn_only=True)
            env_lines.append(f"torch: {torch.__version__} (cuda {torch.version.cuda})")
            env_lines.append(f"numpy: {numpy.__version__}")
            if not torch.cuda.is_available():
                fail(11, "no CUDA GPU is visible; select a GPU runtime "
                         "(environment failure, not a contract result)")
            env_lines.append(f"gpu: {torch.cuda.get_device_name(0)}")
            for mod in ("nibabel", "pandas", "transformers", "huggingface_hub",
                        "sklearn", "tqdm", "torchvision", "einops", "beartype",
                        "ema_pytorch", "accelerate", "h5py", "matplotlib",
                        "seaborn", "scipy", "PIL", "vector_quantize_pytorch"):
                try:
                    m = __import__(mod)
                    env_lines.append(f"{mod}: {getattr(m, '__version__', 'unknown')}")
                except Exception as e:
                    fail(11, f"real-mode dependency {mod} is not importable "
                             f"({e!r}); install "
                             f"probes/004/requirements.txt before rerunning "
                             f"(environment failure, not a contract result)")
            # r6: the load's tolerance is version-semantic, so the installed
            # transformers version is logged up front, not just filed away in
            # environment.txt.
            import transformers
            log(f"  transformers {transformers.__version__} installed "
                f"(requirements pin 4.38.2; PHASE 4 strips the one "
                f"position_ids buffer key that this >=4.31 era rejects)")
        except ImportError as e:
            fail(11, f"missing real-mode dependency: {e}")
    else:
        # Smoke mode is stdlib-only, but still reports the transformers
        # version when one happens to be installed (r6 startup requirement).
        try:
            import transformers
            log(f"  transformers {transformers.__version__} installed")
            env_lines.append(f"transformers: {transformers.__version__}")
        except Exception:
            log("  transformers not importable here (fine for smoke mode; "
                "the real run requires the pinned 4.38.2)")
            env_lines.append("transformers: not installed (smoke)")

    (out_dir / "environment.txt").write_text("\n".join(env_lines) + "\n")

    config = {
        "idea_id": IDEA_ID,
        "mode": "smoke" if smoke else "real",
        "seed": SEED,
        "batch_size": 1,          # contract: batch size 1, never changed
        "patch_size_modified": False,  # contract: patch size must stay released
        "executions": ["exec1_A", "exec2_B", "exec3_A_repeat"],
        "kernel_contrast": [KERNEL_A, KERNEL_B],
        "hf_dataset_repo": HF_DATASET_REPO,
        "checkpoint_repo_path": CHECKPOINT_REPO_PATH,
        "ctclip_git_url": CTCLIP_GIT_URL,
        "tokenizer": TOKENIZER_NAME,
        "required_match_columns": REQUIRED_MATCH_COLUMNS,
        "optional_match_columns": OPTIONAL_MATCH_COLUMNS,
        "pair_selection_rule": (
            "normalize the ConvolutionKernel field (a stringified Python "
            "list takes element 0; a plain string is stripped), then "
            "restrict validation metadata to scans with both Br40f and Br60f "
            "reconstructions passing exact string equality on all match "
            "columns; sort qualifying pairs by the Br40f member's VolumeName; "
            "take the first. Selected before any score is inspected."
        ),
        "max_gpu_minutes": MAX_GPU_MINUTES,
        "expected_head_count": len(EXPECTED_PATHOLOGIES),
        "expected_pathologies": EXPECTED_PATHOLOGIES,
    }
    write_json(out_dir / "resolved_config.json", config)
    log(f"  environment.txt and resolved_config.json written to {out_dir}")
    return config


# ---------------------------------------------------------------------------
# PHASE 3 (shared logic) -- PAIR SELECTION. Deterministic: no randomness, no
# score peeking, pure metadata filtering. Used identically by smoke mode (on
# a synthetic table with planted decoys) and real mode (on the released
# validation_metadata.csv), so the smoke run genuinely tests this logic.
# ---------------------------------------------------------------------------

def parse_volume_name(name):
    """Return (patient, scan, recon) for names like valid_53_a_1[.nii.gz]."""
    m = VOLUME_NAME_RE.match(name)
    if not m:
        return None
    return m.group(1), m.group(2), m.group(3)


def normalize_kernel(raw):
    """Return the kernel name from a raw ConvolutionKernel metadata value.

    The frozen release stores this field as a stringified Python list, e.g.
    "['Br40f', '3']", whose element 0 is the kernel name (decision ledger
    2026-08-12, exit-7 root cause). Rule, per that revision spec: if the value
    parses as a Python list literal, take element 0; otherwise use the
    stripped raw string. Robust to both formats.
    """
    text = (raw or "").strip()
    if text.startswith("["):
        try:
            parsed = ast.literal_eval(text)
        except (ValueError, SyntaxError):
            return text  # not a parsable literal -> stripped raw string
        if isinstance(parsed, (list, tuple)) and parsed:
            return str(parsed[0]).strip()
    return text


def select_pair(rows):
    """Apply the frozen Stage-0 matching rules and return the one probe pair.

    `rows` is a list of dicts (CSV rows). Returns (pair, audit) where pair is
    {"A": row, "B": row} and audit records what was filtered and why —
    including the kernel-value tally and per-filter drop counts required by
    the 2026-08-12 revision, so a selection shortfall is diagnosable from the
    audit alone.
    """
    audit = {"total_rows": len(rows), "non_validation_refused": 0,
             "match_columns_used": [], "qualifying_pairs": 0,
             "kernel_values_top10": [], "filter_drop_counts": {}}

    # Split guard at the metadata level: anything not valid_* is dropped and
    # counted. Train/test rows must never even enter pair consideration.
    validation_rows = []
    for row in rows:
        name = row.get("VolumeName", "")
        if parse_volume_name(name) is None:
            audit["non_validation_refused"] += 1
            continue
        validation_rows.append(row)

    if not validation_rows:
        return None, audit

    # Fail loudly if the metadata schema lacks a required geometry column --
    # proceeding without it would silently weaken the Stage-0 rules.
    columns = set(validation_rows[0].keys())
    missing = [c for c in REQUIRED_MATCH_COLUMNS if c not in columns]
    if missing:
        fail(7, f"metadata is missing required match columns {missing}; "
                f"observed columns: {sorted(columns)}")
    if KERNEL_COLUMN not in columns:
        fail(7, f"metadata is missing kernel column '{KERNEL_COLUMN}'; "
                f"observed columns: {sorted(columns)}")
    match_columns = REQUIRED_MATCH_COLUMNS + [
        c for c in OPTIONAL_MATCH_COLUMNS if c in columns
    ]
    audit["match_columns_used"] = match_columns

    # Kernel-field tally (2026-08-12 revision, requirement 2): record the
    # top-10 distinct raw kernel values with counts, their normalized forms,
    # and example VolumeNames. The exit-7 root cause was a format drift in
    # exactly this field, so the audit must show what the field looks like.
    kernel_tally = {}
    for row in validation_rows:
        raw = row.get(KERNEL_COLUMN) or ""
        entry = kernel_tally.setdefault(raw, {"count": 0, "examples": []})
        entry["count"] += 1
        if len(entry["examples"]) < 3:
            entry["examples"].append(row["VolumeName"])
    top10 = sorted(kernel_tally.items(),
                   key=lambda kv: (-kv[1]["count"], kv[0]))[:10]
    audit["kernel_values_top10"] = [
        {"raw": raw, "normalized": normalize_kernel(raw),
         "count": entry["count"], "example_volume_names": entry["examples"]}
        for raw, entry in top10
    ]

    # Group reconstructions by (patient, scan) = one acquisition.
    scans = {}
    for row in validation_rows:
        patient, scan, recon = parse_volume_name(row["VolumeName"])
        scans.setdefault((patient, scan), []).append(row)

    # Per-filter drop counts (2026-08-12 revision, requirement 2): every scan
    # group that fails to yield a qualifying pair is counted under the filter
    # that dropped it.
    drops = {
        "validation_scans_total": len(scans),
        "scans_without_one_Br40f_and_one_Br60f_member": 0,
        "scans_with_duplicate_contrast_members": 0,
        "candidate_pairs_failing_geometry_match": 0,
        "geometry_mismatches_by_column": {},
    }

    qualifying = []
    for (patient, scan), members in sorted(scans.items()):
        # Need exactly one Br40f member and one Br60f member to form the
        # predeclared contrast (ambiguous multi-member kernels are skipped:
        # the probe needs one clean pair, not maximal recall). The kernel
        # field is NORMALIZED before comparison (see normalize_kernel).
        a_members = [r for r in members
                     if normalize_kernel(r.get(KERNEL_COLUMN)) == KERNEL_A]
        b_members = [r for r in members
                     if normalize_kernel(r.get(KERNEL_COLUMN)) == KERNEL_B]
        if len(a_members) == 0 or len(b_members) == 0:
            drops["scans_without_one_Br40f_and_one_Br60f_member"] += 1
            continue
        if len(a_members) > 1 or len(b_members) > 1:
            drops["scans_with_duplicate_contrast_members"] += 1
            continue
        row_a, row_b = a_members[0], b_members[0]
        # Exact string equality on every match column: identical preprocessing
        # inputs, per the Stage-0 "strictly clean" definition. Geometry
        # list-string columns compare same-format row-vs-row, so they need no
        # normalization (2026-08-12 revision spec, explicitly out of scope).
        mismatched = [c for c in match_columns
                      if row_a.get(c, "") != row_b.get(c, "")]
        if mismatched:
            drops["candidate_pairs_failing_geometry_match"] += 1
            for c in mismatched:
                drops["geometry_mismatches_by_column"][c] = (
                    drops["geometry_mismatches_by_column"].get(c, 0) + 1)
            continue
        qualifying.append((row_a["VolumeName"], row_a, row_b))

    audit["filter_drop_counts"] = drops
    audit["qualifying_pairs"] = len(qualifying)
    if not qualifying:
        return None, audit

    # Deterministic choice: first pair by the Br40f member's VolumeName.
    qualifying.sort(key=lambda t: t[0])
    _, row_a, row_b = qualifying[0]
    return {"A": row_a, "B": row_b}, audit


def assert_pair_valid(pair):
    """Contract split/overlap assertions on the selected pair."""
    name_a = pair["A"]["VolumeName"]
    name_b = pair["B"]["VolumeName"]
    assert_validation_only(name_a)
    assert_validation_only(name_b)
    if name_a == name_b:
        fail(7, "pair members are the same file; A and B must be distinct")
    pa, pb = parse_volume_name(name_a), parse_volume_name(name_b)
    if pa[:2] != pb[:2]:
        fail(7, f"pair members {name_a} / {name_b} are not the same acquisition")
    if pa[2] == pb[2]:
        fail(7, f"pair members {name_a} / {name_b} share a reconstruction id")
    log(f"  pair valid: same acquisition (patient {pa[0]}, scan {pa[1]}), "
        f"distinct reconstructions {pa[2]} vs {pb[2]}")


def report_selection_shortfall(audit, expected, out_dir):
    """Dump selection diagnostics to the run log on a count shortfall.

    2026-08-12 revision, requirement 2: on any selection shortfall vs the
    frozen count, the top-10 distinct kernel values (with counts and example
    VolumeNames) and the per-filter drop counts go to the run log AND to
    selection_audit.json (the caller writes that file unconditionally).
    """
    log(f"  SELECTION SHORTFALL: {audit['qualifying_pairs']} qualifying "
        f"pairs vs frozen expectation {expected}; diagnostics follow")
    log(f"  top-10 distinct {KERNEL_COLUMN} values "
        f"(raw -> normalized: count, example VolumeNames):")
    for item in audit["kernel_values_top10"]:
        log(f"    {item['raw']!r} -> {item['normalized']!r}: "
            f"{item['count']} (e.g. {', '.join(item['example_volume_names'])})")
    log("  per-filter drop counts: "
        f"{json.dumps(audit['filter_drop_counts'], sort_keys=True)}")
    log(f"  full audit: {out_dir / 'selection_audit.json'}")


def write_manifest(out_dir, pair, file_info):
    """input_manifest.csv: the deterministic split manifest for this probe.

    file_info maps role -> {"path": ..., "sha256": ..., "size_bytes": ...}.
    2026-08-12 revision, requirement 3: the kernel recorded per selected
    volume is the normalized value from that volume's own metadata row (the
    raw field is kept alongside for provenance), not a hardcoded constant.
    """
    manifest_path = out_dir / "input_manifest.csv"
    with open(manifest_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["role", "volume_name", "kernel_normalized",
                         "kernel_raw", "local_path", "sha256", "size_bytes"])
        for role in ("A", "B"):
            info = file_info[role]
            raw_kernel = pair[role].get(KERNEL_COLUMN) or ""
            writer.writerow([role, pair[role]["VolumeName"],
                             normalize_kernel(raw_kernel), raw_kernel,
                             info["path"], info["sha256"], info["size_bytes"]])
    log(f"  input_manifest.csv written ({manifest_path})")


# ---------------------------------------------------------------------------
# PHASE 4 (shared logic) -- ENUMERATED FRAMEWORK-ERA BUFFER STRIP (r6).
# transformers 4.31.0 made BERT's embeddings.position_ids a non-persistent
# buffer, so the <=4.30-era checkpoint stores one key that a 4.38-era model
# rejects on strict load. position_ids is torch.arange(max_position_embeddings)
# -- a non-learnable index buffer the model reconstructs itself -- and
# from_pretrained silently drops exactly these keys across framework eras.
# The probe replicates that documented behavior explicitly and audibly:
# remove keys matching *.embeddings.position_ids, insist there is EXACTLY ONE,
# log it, and leave every other key to the strict load.
# ---------------------------------------------------------------------------

# Glob *.embeddings.position_ids from the decision ledger: at least one leading
# component, then the literal suffix. Nothing else (e.g. position_embeddings
# weights, or keys merely containing the substring) may match.
POSITION_ID_BUFFER_PATTERN = re.compile(r".+\.embeddings\.position_ids$")


def strip_position_id_buffer_keys(state):
    """Remove *.embeddings.position_ids keys from a state dict, in place.

    Returns the sorted list of removed keys. The CALLER must enforce the r6
    contract semantics: exactly one removed key is tolerable; zero or several
    mean the checkpoint is not the understood <=4.30-era artifact and the
    load must fail with exit 5.
    """
    removed = sorted(k for k in state if POSITION_ID_BUFFER_PATTERN.match(k))
    for key in removed:
        del state[key]
    return removed


# ---------------------------------------------------------------------------
# PHASE 4/5 (shared logic) -- EXECUTIONS AND CHECKS. Three scoring executions
# (A, B, A again), per-sample rows, then the contract checks: 18 finite
# scores each, stable head order, bit-identical repeat, budget respected.
# ---------------------------------------------------------------------------

def run_three_executions(score_fn, pair, head_names, out_dir):
    """Run exec1_A, exec2_B, exec3_A_repeat through score_fn and check them.

    score_fn(role) -> list of float scores in head order. Returns the results
    dict used by the summary. Enforces the 45-GPU-minute cumulative cap.
    """
    executions = [("exec1_A", "A"), ("exec2_B", "B"), ("exec3_A_repeat", "A")]
    results = {}
    total_seconds = 0.0
    per_sample_rows = []

    for exec_id, role in executions:
        log(f"  running {exec_id} (reconstruction {role}: "
            f"{pair[role]['VolumeName']})")
        start = time.monotonic()
        score_result = score_fn(role)
        if isinstance(score_result, tuple):
            scores, execution_metrics = score_result
        else:
            scores, execution_metrics = score_result, {}
        elapsed = time.monotonic() - start
        total_seconds += elapsed

        # Contract check: exactly 18 finite scores per execution.
        if len(scores) != len(head_names):
            fail(6, f"{exec_id} produced {len(scores)} scores, expected "
                    f"{len(head_names)}")
        non_finite = [head_names[i] for i, s in enumerate(scores)
                      if not (s == s and abs(s) != float("inf"))]
        if non_finite:
            fail(6, f"{exec_id} produced non-finite scores for {non_finite}")

        for i, s in enumerate(scores):
            per_sample_rows.append({
                "execution": exec_id,
                "volume_name": pair[role]["VolumeName"],
                "head_index": i,
                "head_name": head_names[i],
                # float hex makes the bit-identity check visible to a human
                # reading the CSV, not just to the code.
                "score": repr(s),
                "score_hex": float(s).hex(),
            })
        results[exec_id] = {
            "scores": scores,
            "seconds": elapsed,
            **execution_metrics,
        }
        log(f"    {exec_id}: 18 finite scores in {elapsed:.1f}s "
            f"(cumulative {total_seconds/60:.1f} min)")

        # Budget check after every execution: stop the moment the cap is hit.
        if total_seconds > MAX_GPU_MINUTES * 60:
            fail(9, f"cumulative execution time {total_seconds/60:.1f} min "
                    f"exceeded the {MAX_GPU_MINUTES}-minute cap")

    # per_sample.csv: one row per execution x head (3 x 18 = 54 rows).
    per_sample_path = out_dir / "per_sample.csv"
    with open(per_sample_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(per_sample_rows[0].keys()))
        writer.writeheader()
        writer.writerows(per_sample_rows)
    log(f"  per_sample.csv written ({len(per_sample_rows)} rows)")

    # Contract check: repeated A must be BIT-identical, so compare the raw
    # byte encoding of the score vectors, not a numeric tolerance.
    import struct
    def score_bytes(scores):
        return b"".join(struct.pack("<d", s) for s in scores)
    bit_identical = (score_bytes(results["exec1_A"]["scores"]) ==
                     score_bytes(results["exec3_A_repeat"]["scores"]))

    # Diagnostic only (contract negative_pattern: uninterpretable either way).
    ab_diffs = [abs(a - b) for a, b in zip(results["exec1_A"]["scores"],
                                           results["exec2_B"]["scores"])]
    results["_checks"] = {
        "bit_identical_repeat": bit_identical,
        "total_minutes": total_seconds / 60.0,
        "max_abs_AB_diff_DIAGNOSTIC_ONLY": max(ab_diffs),
        "execution_metrics": {
            exec_id: {k: v for k, v in result.items() if k != "scores"}
            for exec_id, result in results.items() if not exec_id.startswith("_")
        },
    }
    return results


# ---------------------------------------------------------------------------
# SMOKE MODE. Synthetic, stdlib-only, no network, no GPU, seconds to run.
# It exercises the harness: gate, config/environment capture, kernel-field
# normalization in both released formats (2026-08-12 revision), pair selection
# with planted decoys (wrong kernel, slice-count drift, spacing drift,
# singleton, train/test rows that the split guard must refuse), the selection
# audit's drop counts and kernel tally, manifest writing, the three-execution
# loop, the 18-finite check, the bit-identity check, and summary writing. It
# does NOT touch the real checkpoint, so it can never satisfy the contract's
# primary metric -- summary.json says so.
# ---------------------------------------------------------------------------

def synthetic_metadata():
    """A tiny metadata table with exactly one clean Br40f|Br60f pair.

    Every decoy exists to prove a specific filter works; the expected outcome
    is asserted in run_smoke(). The clean pair stores its kernel in the
    frozen release's stringified-list format ("['Br40f', '3']", the exit-7
    root cause) while the decoys use the plain-string format, so BOTH
    branches of normalize_kernel are exercised through real selection.
    """
    def row(name, kernel, slices="240", zsp="1.0", xysp="[0.75, 0.75]"):
        return {
            "VolumeName": name, "ConvolutionKernel": kernel,
            "RescaleSlope": "1", "RescaleIntercept": "-1024",
            "XYSpacing": xysp, "ZSpacing": zsp, "NumberofSlices": slices,
            "KVP": "120", "ImagePositionPatient": "[0,0,0]",
        }
    return [
        row("valid_1_a_1.nii.gz", "['Br40f', '3']"),  # the clean pair (A), list format
        row("valid_1_a_2.nii.gz", "['Br60f', '3']"),  # the clean pair (B), list format
        row("valid_2_a_1.nii.gz", "Br40f"),          # decoy: slice-count drift
        row("valid_2_a_2.nii.gz", "Br60f", slices="200"),
        row("valid_3_a_1.nii.gz", "Br40f"),          # decoy: wrong contrast
        row("valid_3_a_2.nii.gz", "Br44f"),
        row("valid_4_a_1.nii.gz", "Br40f"),          # decoy: singleton scan
        row("valid_5_a_1.nii.gz", "Br40f"),          # decoy: ZSpacing drift
        row("valid_5_a_2.nii.gz", "Br60f", zsp="1.5"),
        row("train_9_a_1.nii.gz", "Br40f"),          # split guard must drop
        row("train_9_a_2.nii.gz", "Br60f"),
        row("test_9_a_1.nii.gz", "Br40f"),           # split guard must drop
    ]


def run_smoke(out_dir):
    log("PHASE 2 (smoke): building synthetic metadata and volumes")
    rows = synthetic_metadata()

    # Self-tests for the 2026-08-12 kernel normalization: both formats named
    # in the revision spec, plus the unparsable fallback.
    log("PHASE 3 (smoke): kernel-normalization self-tests")
    for raw, want in [
        ("['Br40f', '3']", "Br40f"),   # frozen release: stringified list
        ("  Br60f ", "Br60f"),          # plain string (pre-drift format)
        ("['Bl56f']", "Bl56f"),         # one-element list literal
        ("[not a literal", "[not a literal"),  # unparsable -> stripped raw
    ]:
        got = normalize_kernel(raw)
        if got != want:
            fail(12, f"normalize_kernel({raw!r}) = {got!r}, expected "
                     f"{want!r}; harness bug")
    log("  normalize_kernel handles list, plain, and unparsable formats")

    # Self-tests for the r6 enumerated buffer strip: the exact key observed in
    # the real exit-5 failure must match; near-miss keys must not; and the
    # zero- and two-key cases the real caller maps to exit 5 must be reported
    # faithfully by the helper.
    log("PHASE 3 (smoke): r6 position_ids buffer-strip self-tests")
    observed_key = "trained_model.text_transformer.embeddings.position_ids"
    near_misses = {
        # No leading component: the ledger glob *.embeddings.position_ids
        # requires one.
        "embeddings.position_ids": 0,
        # Learnable position-embedding WEIGHTS are not the arange buffer.
        "trained_model.text_transformer.embeddings.position_embeddings.weight": 1,
        # Suffix must be anchored.
        "a.embeddings.position_ids_extra": 2,
    }
    one_key_state = dict.fromkeys([observed_key, *near_misses], 0)
    removed = strip_position_id_buffer_keys(one_key_state)
    if removed != [observed_key]:
        fail(12, f"buffer strip removed {removed}, expected exactly "
                 f"[{observed_key!r}]; harness bug")
    if set(one_key_state) != set(near_misses):
        fail(12, "buffer strip disturbed non-matching keys; harness bug")
    if strip_position_id_buffer_keys(dict(near_misses)) != []:
        fail(12, "buffer strip matched a near-miss key; harness bug")
    two_key_state = {observed_key: 0,
                     "other.encoder.embeddings.position_ids": 1}
    if len(strip_position_id_buffer_keys(two_key_state)) != 2:
        fail(12, "buffer strip failed to report both matching keys; the real "
                 "caller could not enforce the exactly-one rule; harness bug")
    log("  strip matches the observed checkpoint key only, and reports the "
        "zero/two-key cases the real run maps to exit 5")

    log("PHASE 3 (smoke): deterministic pair selection with planted decoys")
    pair, audit = select_pair(rows)
    write_json(out_dir / "selection_audit.json", audit)
    if pair is None:
        fail(12, "smoke selection returned no pair; harness bug")
    # Harness self-tests: the planted decoys must have been filtered.
    if audit["non_validation_refused"] != 3:
        fail(12, f"split guard filtered {audit['non_validation_refused']} "
                 f"rows, expected 3 (2 train + 1 test); harness bug")
    if audit["qualifying_pairs"] != 1:
        fail(12, f"{audit['qualifying_pairs']} qualifying pairs, expected "
                 f"exactly 1 (decoys should all fail); harness bug")
    if (pair["A"]["VolumeName"], pair["B"]["VolumeName"]) != (
            "valid_1_a_1.nii.gz", "valid_1_a_2.nii.gz"):
        fail(12, "smoke selected the wrong pair; harness bug")
    # The audit's diagnostics must match the planted decoys exactly:
    # valid_3 (wrong contrast) + valid_4 (singleton) lack a Br60f member;
    # valid_2 (slice count) + valid_5 (ZSpacing) fail geometry, one column each.
    drops = audit["filter_drop_counts"]
    expected_drops = {
        "validation_scans_total": 5,
        "scans_without_one_Br40f_and_one_Br60f_member": 2,
        "scans_with_duplicate_contrast_members": 0,
        "candidate_pairs_failing_geometry_match": 2,
        "geometry_mismatches_by_column": {"NumberofSlices": 1, "ZSpacing": 1},
    }
    if drops != expected_drops:
        fail(12, f"per-filter drop counts {drops} do not match the planted "
                 f"decoys {expected_drops}; harness bug")
    by_raw = {item["raw"]: item for item in audit["kernel_values_top10"]}
    if by_raw.get("['Br40f', '3']", {}).get("normalized") != "Br40f":
        fail(12, "kernel audit did not record the stringified-list value "
                 "normalized to Br40f; harness bug")
    assert_pair_valid(pair)
    log(f"  selected pair: {pair['A']['VolumeName']} | {pair['B']['VolumeName']}")
    log("  selection audit (drop counts, kernel tally) matches planted decoys")

    # Synthetic "volumes": fixed byte blobs. Same bytes -> same mock scores,
    # so the bit-identity check is genuinely exercised end to end.
    volume_bytes = {
        "A": b"synthetic-volume-A-" + b"\x00" * 1024,
        "B": b"synthetic-volume-B-" + b"\x01" * 1024,
    }
    file_info = {
        role: {"path": f"<synthetic:{role}>",
               "sha256": hashlib.sha256(volume_bytes[role]).hexdigest(),
               "size_bytes": len(volume_bytes[role])}
        for role in ("A", "B")
    }
    write_manifest(out_dir, pair, file_info)
    write_json(out_dir / "provenance.json", {
        "mode": "smoke",
        "note": ("synthetic run; no external artifacts were touched, so there "
                 "is no checkpoint/revision provenance to record"),
        "input_sha256": {r: file_info[r]["sha256"] for r in ("A", "B")},
    })

    log("PHASE 4 (smoke): three executions with a deterministic mock scorer")

    def mock_score(role):
        # Deterministic stand-in for the model: hash(volume bytes + head name)
        # mapped to [0, 1]. Purely for plumbing; carries no meaning.
        scores = []
        for head in EXPECTED_PATHOLOGIES:
            digest = hashlib.sha256(volume_bytes[role] + head.encode()).digest()
            scores.append(int.from_bytes(digest[:8], "big") / 2.0 ** 64)
        return scores

    results = run_three_executions(mock_score, pair, EXPECTED_PATHOLOGIES,
                                   out_dir)
    checks = results["_checks"]
    if not checks["bit_identical_repeat"]:
        fail(12, "mock repeat not bit-identical; harness bug")

    log("PHASE 5 (smoke): summary")
    summary = {
        "idea_id": IDEA_ID,
        "mode": "smoke",
        "contract_satisfied": False,  # a smoke run can NEVER satisfy the contract
        "harness_checks": {
            "gate_passed": True,
            "split_guard_refused_train_test_rows": True,
            "decoy_pairs_all_filtered": True,
            "kernel_normalization_both_formats": True,
            "r6_buffer_strip_enumerated_and_anchored": True,
            "selection_audit_matches_planted_decoys": True,
            "pair_selection_deterministic_rule_applied": True,
            "three_executions_completed": True,
            "heads_exactly_18_finite_per_execution": True,
            "bit_identical_repeat": checks["bit_identical_repeat"],
            "within_time_budget": checks["total_minutes"] < MAX_GPU_MINUTES,
        },
        "total_minutes": checks["total_minutes"],
        "execution_metrics": checks["execution_metrics"],
        "max_abs_AB_diff_DIAGNOSTIC_ONLY": checks["max_abs_AB_diff_DIAGNOSTIC_ONLY"],
        "interpretation": (
            "SMOKE MODE ONLY. This run used synthetic volumes and a mock "
            "scorer to verify the probe harness (gate, split guards, "
            "deterministic pair selection, per-sample outputs, bit-identity "
            "and budget checks). It says NOTHING about the contract's risky "
            "assumption: whether CT_LiPro_v2.pt loads unchanged and emits "
            "deterministic 18-head scores. Only the real run can produce the "
            "contract's positive_pattern, and no A-versus-B difference here "
            "or in the real run is evidence about reconstruction sensitivity."
        ),
    }
    write_json(out_dir / "summary.json", summary)
    print()
    print(json.dumps(summary, indent=2, sort_keys=True))
    print()
    print("Plain-English read: the harness plumbing works end to end; the")
    print("scientific assumption remains untested until the real run.")
    return 0


# ---------------------------------------------------------------------------
# REAL MODE. Phases: resolve+download official artifacts and record their
# hashes BEFORE inference (provenance), select the pair from the released
# validation metadata, stage the two volumes, load the released code and
# checkpoint unchanged, run the three executions, summarize.
# Requires: accepted CT-RATE gate + HF token, a CUDA GPU, and the CT-CLIP
# dependencies (torch, nibabel, pandas, transformers, huggingface_hub).
# ---------------------------------------------------------------------------

def run_real(out_dir, config):
    work_dir = PROBE_DIR / "work"
    work_dir.mkdir(exist_ok=True)

    # ---- PHASE 2a: locate and download the small official tables + checkpoint.
    log("PHASE 2: resolving official artifacts on the gated CT-RATE repo")
    try:
        from huggingface_hub import HfApi, hf_hub_download
    except ImportError as e:
        fail(11, f"huggingface_hub not installed: {e}")
    api = HfApi()
    try:
        info = api.dataset_info(HF_DATASET_REPO)
        revision = info.sha  # freeze the exact repo commit for provenance
        log(f"  repo revision frozen: {revision}")
    except Exception as e:
        fail(3, f"cannot access {HF_DATASET_REPO}: gate not accepted, no "
                f"token, or network failure ({e})")

    def download(repo_path):
        # Every download goes through the split guard, then is pinned to the
        # frozen revision so a mid-run repo update cannot change our inputs.
        assert_validation_only(repo_path)
        try:
            local = hf_hub_download(HF_DATASET_REPO, repo_path,
                                    repo_type="dataset", revision=revision,
                                    local_dir=str(work_dir))
        except Exception as e:
            fail(3, f"download failed for {repo_path}: {e}")
        return Path(local)

    def find_repo_file(name_fragment):
        # Filenames on the repo have varied casing across revisions; resolve
        # by case-insensitive search and fail loudly with the listing.
        try:
            matches = [p for p in api.list_repo_files(HF_DATASET_REPO,
                                                      repo_type="dataset",
                                                      revision=revision)
                       if name_fragment.lower() in p.lower()
                       and "test" not in p.lower() and "train" not in p.lower()]
        except Exception as e:
            fail(3, f"cannot list repo files: {e}")
        if len(matches) != 1:
            fail(3, f"expected exactly one repo file matching "
                    f"'{name_fragment}', found {matches}")
        return matches[0]

    metadata_path = download(find_repo_file("validation_metadata.csv"))
    labels_path = download(find_repo_file("valid_predicted_labels.csv"))
    reports_path = download(find_repo_file("validation_reports.csv"))
    checkpoint_path = download(CHECKPOINT_REPO_PATH)
    log(f"  checkpoint downloaded: {checkpoint_path} "
        f"({checkpoint_path.stat().st_size/1e9:.2f} GB)")

    # ---- PHASE 2b: pin the released code at a recorded commit.
    log("  cloning released CT-CLIP code")
    import subprocess
    ctclip_dir = PROBE_DIR / "vendor" / "CT-CLIP"
    if not ctclip_dir.exists():
        ctclip_dir.parent.mkdir(exist_ok=True)
        r = subprocess.run(["git", "clone", "--depth", "1", CTCLIP_GIT_URL,
                            str(ctclip_dir)], capture_output=True, text=True)
        if r.returncode != 0:
            fail(3, f"git clone of released code failed: {r.stderr}")
    code_commit = subprocess.run(
        ["git", "-C", str(ctclip_dir), "rev-parse", "HEAD"],
        capture_output=True, text=True).stdout.strip()
    dirty = subprocess.run(
        ["git", "-C", str(ctclip_dir), "status", "--porcelain"],
        capture_output=True, text=True).stdout.strip()
    if dirty:
        # Contract: the released code must run UNMODIFIED. A dirty clone means
        # someone edited it; that would invalidate the compatibility claim.
        fail(5, f"released-code clone has local modifications:\n{dirty}")
    log(f"  released code commit: {code_commit}")

    # The released packages live one directory below their project roots.
    # Add those project roots directly; unlike an in-process editable install,
    # this takes effect immediately and does not mutate the environment.
    released_import_roots = [
        ctclip_dir / "transformer_maskgit",
        ctclip_dir / "CT_CLIP",
    ]
    for project in released_import_roots:
        if not (project / "setup.py").is_file():
            fail(11, f"released package root is missing setup.py: {project} "
                     f"(environment/repository-layout failure, not a contract result)")
        sys.path.insert(0, str(project))
        log(f"  released import root added: {project}")

    # ---- PHASE 2c: provenance BEFORE inference (contract requires this order).
    log("  hashing all inputs (provenance is recorded before any inference)")
    # Contract invalidating_failures[1]: every artifact must be
    # cryptographically identifiable before inference.
    if not revision or not code_commit:
        fail(4, f"cannot pin artifacts: hf_revision={revision!r}, "
                f"code_commit={code_commit!r}")
    try:
        checkpoint_sha = sha256_file(checkpoint_path)
        table_shas = {p.name: sha256_file(p)
                      for p in (metadata_path, labels_path, reports_path)}
    except OSError as e:
        fail(4, f"cannot hash downloaded artifacts: {e}")
    provenance = {
        "mode": "real",
        "hf_dataset_repo": HF_DATASET_REPO,
        "hf_revision": revision,
        "code": {"git_url": CTCLIP_GIT_URL, "commit": code_commit},
        "released_package_import": {
            "method": "direct sys.path insertion; dependencies preinstalled",
            "projects": [str(p) for p in released_import_roots],
        },
        "tokenizer": TOKENIZER_NAME,
        "checkpoint": {
            "repo_path": CHECKPOINT_REPO_PATH,
            "sha256": checkpoint_sha,
            "size_bytes": checkpoint_path.stat().st_size,
            "attribution_note": (
                "attribution limited to 'released v2 ClassFine checkpoint' "
                "until paper-number correspondence is checked (decision "
                "ledger 2026-08-11, pin 4)"),
        },
        "tables": table_shas,
    }
    write_json(out_dir / "provenance.json", provenance)

    # ---- PHASE 3: pair selection from the released validation metadata.
    log("PHASE 3: deterministic pair selection from validation_metadata.csv")
    with open(metadata_path, newline="") as f:
        rows = list(csv.DictReader(f))
    pair, audit = select_pair(rows)
    # The selection audit is always written (2026-08-12 revision), so any
    # shortfall is diagnosable from the output directory alone.
    write_json(out_dir / "selection_audit.json", audit)
    log(f"  qualifying Br40f|Br60f geometry-matched pairs: "
        f"{audit['qualifying_pairs']} (Stage-0 counted 237; a large mismatch "
        f"means the matching rules drifted and should be investigated)")
    if audit["qualifying_pairs"] != EXPECTED_QUALIFYING_PAIRS:
        report_selection_shortfall(audit, EXPECTED_QUALIFYING_PAIRS, out_dir)
        fail(7, f"qualifying-pair count {audit['qualifying_pairs']} differs "
                f"from the frozen Stage-0 count {EXPECTED_QUALIFYING_PAIRS}; "
                f"release contents or matching logic drifted -- see "
                f"selection_audit.json and the diagnostics above")
    if pair is None:
        fail(7, "no qualifying geometry-matched Br40f|Br60f pair found in the "
                "released metadata")
    assert_pair_valid(pair)

    # Stage the two volumes the way the released dataset class expects
    # (dataset/valid/valid_P/valid_P_S/valid_P_S_R.nii.gz).
    volume_paths = {}
    for role in ("A", "B"):
        name = pair[role]["VolumeName"]
        patient, scan, _ = parse_volume_name(name)
        repo_path = f"dataset/valid/valid_{patient}/valid_{patient}_{scan}/{name}"
        volume_paths[role] = download(repo_path)
    file_info = {
        role: {"path": str(volume_paths[role]),
               "sha256": sha256_file(volume_paths[role]),
               "size_bytes": volume_paths[role].stat().st_size}
        for role in ("A", "B")
    }
    write_manifest(out_dir, pair, file_info)
    # Volume hashes join the pre-inference provenance record.
    provenance["input_volumes"] = {
        pair[r]["VolumeName"]: file_info[r]["sha256"] for r in ("A", "B")}
    write_json(out_dir / "provenance.json", provenance)

    # Head order check: the released pipeline's head order is the labels-CSV
    # column order from index 1 (prepare_samples in data_inference_nii.py).
    with open(labels_path, newline="") as f:
        label_columns = next(csv.reader(f))[1:]
    if label_columns != EXPECTED_PATHOLOGIES:
        fail(6, f"released label column order {label_columns} does not match "
                f"the expected 18-head mapping; no stable head-name/order "
                f"mapping is available")
    log("  head-name/order mapping confirmed against released labels CSV")

    # ---- PHASE 4: load released code + checkpoint unchanged, run 3 executions.
    log("PHASE 4: loading released model (unchanged) and running executions")
    import torch
    device = torch.device("cuda")  # released inference target; batch size remains 1
    sys.path.insert(0, str(ctclip_dir / "scripts"))
    try:
        # These imports and constructor arguments mirror the released
        # scripts/ct_lipro_inference.py exactly. Any deviation needed to make
        # this work is, by contract, an invalidating failure -- fix the
        # DRIVER to match the released code, never the reverse.
        from transformer_maskgit import CTViT
        from ct_clip import CTCLIP
        from ct_lipro_inference import ImageLatentsClassifier
        from transformers import BertTokenizer, BertModel

        try:
            tokenizer = BertTokenizer.from_pretrained(TOKENIZER_NAME,
                                                      do_lower_case=True)
            text_encoder = BertModel.from_pretrained(TOKENIZER_NAME)
        except Exception as e:
            fail(10, f"tokenizer/text-encoder access failed: {e!r} "
                     f"(environment/access failure, not a contract result)")
        image_encoder = CTViT(
            dim=512, codebook_size=8192, image_size=480, patch_size=20,
            temporal_patch_size=10, spatial_depth=4, temporal_depth=4,
            dim_head=32, heads=8,
        )
        clip = CTCLIP(
            image_encoder=image_encoder, text_encoder=text_encoder,
            dim_image=294912, dim_text=768, dim_latent=512,
            extra_latent_projection=False, use_mlm=False,
            downsample_image_embeds=False, use_all_token_embeds=False,
        )
        model = ImageLatentsClassifier(clip, 512, num_classes=18)
        # PyTorch 2.6 changed the default weights_only behavior. False matches
        # the released loader's historical full-checkpoint behavior explicitly.
        state = torch.load(str(checkpoint_path), map_location="cpu",
                           weights_only=False)
        # r6 tolerant load: remove the framework-era position_ids buffer key
        # (see strip_position_id_buffer_keys). The removed set must be exactly
        # one key; zero means the checkpoint is not the understood <=4.30-era
        # artifact, several means the architecture understanding is wrong.
        # Either way the load claim would be false, so both exit 5.
        removed_keys = strip_position_id_buffer_keys(state)
        if len(removed_keys) != 1:
            fail(5, f"expected exactly one *.embeddings.position_ids buffer "
                    f"key in the checkpoint state dict, found "
                    f"{len(removed_keys)}: {removed_keys}; the checkpoint is "
                    f"not the understood <=4.30-era artifact and the r6 "
                    f"tolerant-load claim does not apply")
        log(f"  r6 enumerated buffer strip: removed {removed_keys[0]!r} "
            f"(non-learnable arange buffer; transformers-4.31 era change)")
        # The removal is part of the load's provenance: record it before the
        # load so a later reader can see exactly what "unchanged modulo
        # enumerated buffer keys" meant for this run.
        provenance["state_dict_keys_removed_before_load"] = {
            "pattern": POSITION_ID_BUFFER_PATTERN.pattern,
            "removed_keys": removed_keys,
            "reason": ("transformers 4.31.0 made BERT embeddings.position_ids "
                       "a non-persistent buffer; the <=4.30-era checkpoint "
                       "carries it, the 4.38-era model does not expect it "
                       "(decision ledger r6, 2026-08-12)"),
        }
        write_json(out_dir / "provenance.json", provenance)
        # strict=True: the contract forbids adapting the architecture to fit
        # the weights; any OTHER unexpected or missing key must fail here,
        # not be papered over.
        model.load_state_dict(state, strict=True)
        model = model.cuda().eval()
    except SystemExit:
        raise
    except (ImportError, ModuleNotFoundError) as e:
        fail(11, f"released model dependency/import missing: {e!r} "
                 f"(environment failure, not a contract result)")
    except Exception as e:
        fail(5, f"released checkpoint/code failed to load unchanged: {e!r}")
    log("  checkpoint loaded: strict state dict match modulo the one "
        "enumerated, provenance-logged position_ids buffer key (r6)")

    # Released preprocessing via the released dataset class, pointed at a
    # staging folder containing ONLY our two volumes plus the official CSVs.
    try:
        from data_inference_nii import CTReportDatasetinfer
        stage_dir = work_dir / "stage" / "valid"
        for role in ("A", "B"):
            name = pair[role]["VolumeName"]
            patient, scan, _ = parse_volume_name(name)
            dest = stage_dir / f"valid_{patient}" / f"valid_{patient}_{scan}"
            dest.mkdir(parents=True, exist_ok=True)
            link = dest / name
            if not link.exists():
                os.link(volume_paths[role], link)
        dataset = CTReportDatasetinfer(
            data_folder=str(stage_dir), reports_file=str(reports_path),
            meta_file=str(metadata_path), labels=str(labels_path))
        # Map dataset items back to roles by accession name.
        items = {}
        for idx in range(len(dataset)):
            video, _text, _onehot, acc = dataset[idx]
            items[str(acc)] = idx
        index_for = {}
        for role in ("A", "B"):
            stem = pair[role]["VolumeName"].replace(".nii.gz", "")
            match = [k for k in items if stem in k]
            if len(match) != 1:
                fail(7, f"staged volume for role {role} not found uniquely in "
                        f"released dataset items: {list(items)}")
            index_for[role] = items[match[0]]
    except SystemExit:
        raise
    except (ImportError, ModuleNotFoundError) as e:
        fail(11, f"released preprocessing dependency/import missing: {e!r} "
                 f"(environment failure, not a contract result)")
    except Exception as e:
        fail(7, f"released preprocessing failed on the selected pair: {e!r}")

    # Empty-string text tokens, exactly as the released inference does.
    text_tokens = tokenizer([""], return_tensors="pt", padding="max_length",
                            truncation=True, max_length=512).to("cuda")

    def real_score(role):
        # Re-fetch through the released dataset each time so exec3_A_repeat
        # re-runs the full deterministic pipeline from the same frozen bytes.
        video, _text, _onehot, _acc = dataset[index_for[role]]
        video = video.unsqueeze(0).cuda()  # batch size 1, per contract
        torch.cuda.reset_peak_memory_stats()
        with torch.no_grad():
            # Exact released ImageLatentsClassifier call signature: False asks
            # for classifier logits rather than the 512-dimensional latents.
            logits = model(False, text_tokens, video, device=device)
        scores = torch.sigmoid(logits).flatten().double().cpu().tolist()
        peak_gb = torch.cuda.max_memory_allocated() / 1e9
        log(f"    peak GPU memory: {peak_gb:.2f} GB")
        return scores, {"peak_gpu_memory_gb": peak_gb}

    try:
        results = run_three_executions(real_score, pair, EXPECTED_PATHOLOGIES,
                                       out_dir)
    except SystemExit:
        raise
    except torch.cuda.OutOfMemoryError as e:
        fail(9, f"batch-size-1 inference exceeded GPU memory: {e}")
    except Exception as e:
        fail(9, f"inference crashed: {e!r}")

    checks = results["_checks"]
    if not checks["bit_identical_repeat"]:
        fail(8, "repeated inference on reconstruction A was NOT bit-identical "
                "under the recorded deterministic configuration")

    # ---- PHASE 5: summary and interpretation.
    log("PHASE 5: summary")
    summary = {
        "idea_id": IDEA_ID,
        "mode": "real",
        "contract_satisfied": True,
        "checks": {
            "approval_gate": True,
            "provenance_recorded_before_inference": True,
            # r6: "unchanged" is modulo the enumerated, provenance-logged
            # framework-era buffer key(s) listed right below.
            "checkpoint_loaded_strict_modulo_enumerated_buffer_keys": True,
            "state_dict_keys_removed_before_load": removed_keys,
            "pair_passes_stage0_rules": True,
            "three_executions_completed": True,
            "heads_exactly_18_finite_per_execution": True,
            "head_name_order_stable": True,
            "bit_identical_repeat": True,
            "within_gpu_budget": True,
        },
        "pair": {r: pair[r]["VolumeName"] for r in ("A", "B")},
        "qualifying_pairs_found": None,  # filled below for the cross-check
        "total_minutes": checks["total_minutes"],
        "execution_metrics": checks["execution_metrics"],
        "max_abs_AB_diff_DIAGNOSTIC_ONLY": checks["max_abs_AB_diff_DIAGNOSTIC_ONLY"],
        "interpretation": (
            "POSITIVE per the contract's positive_pattern: the pinned "
            "released v2 ClassFine artifact loaded without architecture or "
            "preprocessing changes -- strictly, modulo the single enumerated, "
            "provenance-logged position_ids buffer key removed per the r6 "
            "decision-ledger semantics -- every execution produced exactly 18 "
            "finite named scores, the repeated execution of reconstruction A "
            "was bit-identical, and the run stayed within 45 GPU minutes at "
            "batch size 1. This authorizes ONLY a later request for human "
            "approval of the separate 425-pair floor-study contract. The "
            "A-versus-B differences recorded here are pipeline diagnostics; "
            "per the contract they are scientifically uninterpretable and "
            "are not evidence for or against reconstruction sensitivity."
        ),
    }
    summary["qualifying_pairs_found"] = audit["qualifying_pairs"]
    write_json(out_dir / "summary.json", summary)
    print()
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


# ---------------------------------------------------------------------------
# Entry point.
# ---------------------------------------------------------------------------

def main():
    global _LOG_FILE
    parser = argparse.ArgumentParser(
        description="idea-004 load probe (see module docstring)")
    # --smoke is the only flag: the contract permits no other variants.
    parser.add_argument("--smoke", action="store_true",
                        help="synthetic stdlib-only harness test; no network, "
                             "no GPU, cannot satisfy the contract")
    parser.add_argument(
        "--output-dir", type=Path,
        help="artifact directory (use a persistent Drive path in Colab); "
             "defaults to outputs/ or outputs_smoke/ beside run.py")
    args = parser.parse_args()

    default_name = "outputs_smoke" if args.smoke else "outputs"
    if args.output_dir:
        out_dir = args.output_dir.expanduser().resolve()
    else:
        out_dir = PROBE_DIR / default_name
    out_dir.mkdir(parents=True, exist_ok=True)
    _LOG_FILE = out_dir / "run_log.txt"
    _LOG_FILE.write_text("")  # fresh log per run

    log(f"idea-004 load probe starting (mode={'smoke' if args.smoke else 'real'})")
    phase0_gate()
    config = phase1_environment(out_dir, smoke=args.smoke)

    if args.smoke:
        return run_smoke(out_dir)
    return run_real(out_dir, config)


if __name__ == "__main__":
    try:
        sys.exit(main())
    except SystemExit:
        raise
    except KeyboardInterrupt:
        print("\ninterrupted", file=sys.stderr)
        sys.exit(12)
    except Exception as e:  # never silently swallow a harness fault
        print(f"UNEXPECTED INTERNAL ERROR (exit 12, not a contract result): {e!r}",
              file=sys.stderr)
        sys.exit(12)
