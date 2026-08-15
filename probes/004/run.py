#!/usr/bin/env python3
"""idea-004, contract v2: the 425-pair reconstruction-sensitivity floor study.

WHAT THIS EXPERIMENT IS, in one paragraph: CT-RATE stores several
reconstructions of the same CT acquisition. This study runs the frozen,
provenance-verified "released v2 ClassFine" checkpoint (CT_LiPro_v2.pt) on 425
predeclared geometry-matched same-acquisition reconstruction pairs of the
CT-RATE validation split and measures, per abnormality head (18) and per
reconstruction-contrast stratum, how much the scores change between the two
reconstructions of identical anatomy. The PRIMARY metric (tier 1, label-free)
is the per-head x per-stratum distribution of signed paired score differences
on the probability and logit scales: N, median and mean signed difference,
empirical |d| quantiles (0.50/0.75/0.90/0.95/max), with patient-cluster
bootstrap 95% intervals and NO cross-head averaging anywhere. Tier 2
(secondary, descriptive, only if tier 1 completes) is the per-head per-stratum
paired delta-AUROC against the released report-derived validation labels, with
zero threshold language. STOPPING RULE: stop when all 425 manifest pairs are
scored, all spot-checks and per-chunk artifacts are complete, and the frozen
analysis has run; or immediately on any invalidating failure; or when any
budget cap would be exceeded. POSITIVE looks like: the frozen manifest is
reproduced exactly, every chunk completes with verified provenance,
same-session pairing, bit-identical spot-checks and in-tolerance anchors, and
the tier tables exist -- ANY magnitude profile (near-zero, large, or mixed) is
a valid descriptive outcome; the deliverable is the measured baseline itself.
NEGATIVE: there is no failing magnitude. Tightly-bounded-near-zero differences
are the sensitivity-bounded descriptive null; large differences are equally
valid descriptively. An invalidating failure is never reinterpreted as a
negative result, and no negative outcome is reinterpreted as a failure.

Contract: ideas/004/probe_contract.yaml (contract_version: 2), which
supersedes the executed v1 load probe (PASSED 2026-08-12; preserved in git
history). Requirements file: ideas/004/contract_requirements.md.

TWO-PHASE APPROVAL (contract approval_and_phasing; enforced mechanically):
  Phase M -- metadata-only manifest freeze. Downloads at most the three pinned
      metadata tables, regenerates the frozen 425-pair manifest, hard-gates
      the per-stratum counts against the frozen 237/126/58/4, records the
      manifest SHA-256 and unique-volume count, and always writes
      selection_audit.json. NO image download, NO inference, NO score of any
      kind. This is all the phase-1 approval authorizes.
  Phase B -- bulk chunked download -> preprocess -> infer -> delete over the
      manifest, then the frozen two-tier analysis. REFUSED by this driver
      until (a) no TO_BE_RECORDED_AT_MANIFEST_FREEZE placeholder remains in
      the contract and (b) the HUMAN_APPROVED_PROBE marker's contract_blob
      equals the git blob of the contract as amended. Recording the manifest
      hash amends the contract, which changes its blob, which makes the
      phase-1 marker stale by construction -- so phase B mechanically requires
      the fresh phase-2 approval.

Usage (one command per phase):
    python run.py --smoke                      # synthetic harness test; no
                                               # network, no GPU, no HF gate;
                                               # can NEVER satisfy the contract
    python run.py --phase M --output-dir DIR   # manifest freeze (phase-1 OK)
    python run.py --phase B --output-dir DIR   # bulk study (needs phase-2)

DIR is the results bundle (contract results_bundle_layout); on Colab point it
at a persistent Drive path so multi-session phase B can resume.

Exit codes (each maps to a contract invalidating_failure or a harness fault):
    0   phase/smoke completed cleanly (for phase B: session done or study done)
    2   approval/contract gate failure: marker missing or blob-stale, contract
        parse/caps drift, placeholders still present for phase B, bad CLI
    3   access failure: HF gate/token/download, git clone, missing v1
        anchor-reference file (invalidating_failures: "Access")
    4   provenance mismatch: any SHA-256 / git-blob / commit mismatch
        (invalidating_failures: "Provenance mismatch")
    5   checkpoint load failure beyond exactly one enumerated
        *.embeddings.position_ids buffer key (invalidating: "Load failure")
    6   output-shape failure: not exactly 18 finite named scores, or head
        name/order drift (invalidating: "Output shape")
    7   selection/manifest/world failure: stratum counts differ from frozen,
        manifest hash mismatch, split-guard refusal, anchor pair missing from
        the manifest, differing label rows within a pair (invalidating:
        "Manifest-freeze failure" / "Selection shortfall" / "Label integrity")
    8   within-session determinism failure: anchor A-repeat or spot-check
        re-run not bit-identical (invalidating: "Determinism")
    9   budget stop: session cap, volume caps, QA/retry allowance, GPU
        memory/crash -- reported as budget exhaustion / execution failure,
        never reinterpreted as a scientific result (invalidating: "Budget
        overrun" if a cap would be crossed)
    10  environment drift: installed transformers/tokenizers differ from the
        pinned closure (invalidating: "Environment drift")
    11  missing dependency/GPU (environment problem, not a contract result)
    12  unexpected internal error (harness fault, not a contract result; do
        NOT reinterpret as a negative)
    13  anchor cross-session drift beyond the preregistered 1.0e-4 per-head
        probability tolerance (invalidating: "Anchor drift"; the session's
        chunks do not count and are redone after diagnosis)
"""

import argparse
import ast
import csv
import hashlib
import json
import math
import os
import platform
import random
import re
import shutil
import sys
import time
from pathlib import Path

# ---------------------------------------------------------------------------
# FROZEN CONSTANTS. Nothing below is tunable from the command line: the
# contract allows exactly one pipeline configuration (maximum_variants: 1),
# so there are no knobs. PHASE 0 cross-checks the load-bearing values against
# the approved contract text so silent contract edits cannot drift past this
# code unnoticed.
# ---------------------------------------------------------------------------

IDEA_ID = "idea-004"
CONTRACT_VERSION = 2
SEED = 0  # fixed inference seed; maximum_seeds: 1 in the contract

PROBE_DIR = Path(__file__).resolve().parent
REPO_ROOT = PROBE_DIR.parent.parent
CONTRACT_PATH = REPO_ROOT / "ideas" / "004" / "probe_contract.yaml"
APPROVAL_PATH = REPO_ROOT / "ideas" / "004" / "HUMAN_APPROVED_PROBE"

# The literal placeholder that phase M resolves; phase B is refused while any
# instance of it remains in the contract (approval_and_phasing.phase_B).
PLACEHOLDER = "TO_BE_RECORDED_AT_MANIFEST_FREEZE"

# Official sources (contract provenance_pins; every one re-verified at run
# time -- a mismatch is invalidating, exit 4).
HF_DATASET_REPO = "ibrahimhamamci/CT-RATE"
HF_REVISION = "deeca4d89e9f978d4d1bccd88a55071ddbb146bb"
CHECKPOINT_REPO_PATH = "models/CT-CLIP-Related/CT_LiPro_v2.pt"
CHECKPOINT_SHA256 = \
    "9246d9c8a7e2cedaa115719699229fe0acb02f19488e8bd1ad1eff5f47ff1d7d"
CTCLIP_GIT_URL = "https://github.com/ibrahimethemhamamci/CT-CLIP"
CODE_COMMIT = "a2a155c601987820433c01db69b64d701d3d229d"
TOKENIZER_NAME = "microsoft/BiomedVLP-CXR-BERT-specialized"
TABLES_SHA256 = {
    "validation_metadata.csv":
        "7ae04aaf59e946f8805c940697820f8fd97b56b9634cadd725269b3f6ed9cae1",
    "valid_predicted_labels.csv":
        "2356c549da0398dd8bc8d8b007fc78c5c4e489d8b54049b8bbc122a11d429b22",
    "validation_reports.csv":
        "e0538498de92e19b3bb6b70643d5c78edda146e4f480f159825202bf78ed4620",
}

# Environment pins (contract R5, the r6 closure). Any session deviating from
# these is environment drift and invalidating (exit 10).
TRANSFORMERS_PIN = "4.38.2"
TOKENIZERS_PIN = "0.15.2"

# The four frozen strata in the contract's fixed manifest order, with the
# Stage-0 frozen pair counts that phase M must reproduce EXACTLY (hard gate).
STRATA_ORDER = ["Br40f|Br60f", "Bl56f|Br40f", "Bl57d|Br36d", "Br40f|Br44f"]
FROZEN_STRATUM_COUNTS = {
    "Br40f|Br60f": 237,
    "Bl56f|Br40f": 126,
    "Bl57d|Br36d": 58,
    "Br40f|Br44f": 4,   # exploratory only; excluded from confirmatory stats
}
EXPLORATORY_STRATA = {"Br40f|Br44f"}
CONFIRMATORY_STRATA = [s for s in STRATA_ORDER if s not in EXPLORATORY_STRATA]
TOTAL_PAIRS = 425          # contract budgets.pair_count_cap
CHUNK_SIZE_PAIRS = 25      # contract R7: 17 chunks of exactly 25 pairs
CHUNK_COUNT = 17

# Contract R2: canonical sign direction. d = s(higher-index kernel) -
# s(lower-index kernel), where the index is the two-digit number in the
# normalized Siemens kernel name. "softer" = lower index, "sharper" = higher.
# The dict below is the contract's explicit per-stratum table, hardcoded as a
# cross-check against the numeric rule (both are asserted to agree at start).
CONTRACT_SIGN_DIRECTIONS = {
    # stratum: (softer member kernel, sharper member kernel)
    "Br40f|Br60f": ("Br40f", "Br60f"),   # d = s(Br60f) - s(Br40f)
    "Bl56f|Br40f": ("Br40f", "Bl56f"),   # d = s(Bl56f) - s(Br40f)
    "Bl57d|Br36d": ("Br36d", "Bl57d"),   # d = s(Bl57d) - s(Br36d)
    "Br40f|Br44f": ("Br40f", "Br44f"),   # d = s(Br44f) - s(Br40f)
}

# The anchor pair (contract execution_model.anchor): the v1 load-probe pair,
# scores already exposed and declared uninterpretable. Flagged in the manifest
# and excluded from every confirmatory statistic; re-run at every phase-B
# session start as a drift detector.
ANCHOR_VOLUME_A = "valid_1004_a_1.nii.gz"   # Br40f member
ANCHOR_VOLUME_B = "valid_1004_a_2.nii.gz"   # Br60f member
ANCHOR_INPUT_SHA256 = {
    ANCHOR_VOLUME_A:
        "b058a53eff9f226dbff9725fade98fde412ac56e78a976e404e5c77e8e84f7bd",
    ANCHOR_VOLUME_B:
        "dd581f82142646a4ad616cfc6f6b4a6ce8a058f029d47cff04004f1fc7bc2751",
}
# Cross-session anchor tolerance, fixed in the contract before bulk execution:
# max per-head absolute difference on the probability scale vs the v1
# reference scores. Rationale (contract): hardware may differ across sessions,
# so bit-identity is demanded only within session; 1.0e-4 is ~70x smaller than
# the one observed diagnostic A-vs-B reconstruction difference (7.0e-3, v1).
ANCHOR_CROSS_SESSION_TOLERANCE = 1.0e-4
# v1 reference scores: probes/004/results/per_sample.csv at the pinned git
# blob (contract provenance_pins.v1_anchor_reference_scores).
V1_REFERENCE_PATH = PROBE_DIR / "results" / "per_sample.csv"
V1_REFERENCE_GIT_BLOB = "ea1cdd3fb463cafa9c1f7bc7ec048d2c7c320cc1"

# Budgets (contract R8). Caps are in volumes and sessions, never GPU minutes.
SESSION_CAP = 30
QA_RETRY_FRACTION = 0.20   # allowance = ceil(0.20 x unique_volume_cap)

# Tier-1 analysis constants (contract R3, all preregistered in the contract).
TIER1_BOOTSTRAP_SEED = 20260814   # numpy default_rng stream, fixed
TIER2_BOOTSTRAP_SEED = 20260815   # separate preregistered stream for tier 2
BOOTSTRAP_REPLICATES = 2000
BOOTSTRAP_INTERVAL = (2.5, 97.5)  # percentile, 95%
LOGIT_CLIP = 1e-6                 # p clipped to [1e-6, 1 - 1e-6] before logit
ABS_QUANTILES = [0.50, 0.75, 0.90, 0.95, 1.00]  # |d| quantiles per cell
# Statistics bootstrapped per (head, stratum, scale), per the contract.
BOOTSTRAP_STATISTICS = ["median_signed", "mean_signed", "q95_abs"]

# Tier-2 sparse-label rule (contract R4, preregistered): a (head, stratum)
# cell's AUROCs are computed only with >= 10 positive AND >= 10 negative
# counted pairs. Computation-eligibility only; no interpretive semantics.
SPARSE_MIN_POSITIVE = 10
SPARSE_MIN_NEGATIVE = 10
EXCLUDED_CELL_LABEL = "insufficient labels for AUROC"

# The 18 head names in released order (v1-verified against the released
# labels CSV column order; contract invalidating_failures: "Output shape").
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

# Stage-0 strict geometry matching (frozen; v1-validated on the Br40f|Br60f
# stratum, which reproduced all 237 frozen pairs). A pair is clean only if the
# deterministic released preprocessing receives identical inputs for both
# members: exact string equality on the required columns, plus the optional
# position/acquisition columns where present in the released schema.
REQUIRED_MATCH_COLUMNS = [
    "RescaleSlope",
    "RescaleIntercept",
    "XYSpacing",
    "ZSpacing",
    "NumberofSlices",   # slice-count drift was a Stage-0 exclusion
]
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

# Manifest columns, exactly as the contract's frozen_scope.manifest.columns.
MANIFEST_COLUMNS = [
    "pair_id", "patient_id", "volume_name_softer", "volume_name_sharper",
    "stratum", "kernel_normalized_softer", "kernel_normalized_sharper",
    "anchor_excluded",
]

# r6 enumerated framework-era buffer key (contract R5): transformers 4.31.0
# made BERT's embeddings.position_ids a non-persistent buffer, so the
# <=4.30-era checkpoint carries exactly one key a 4.38-era model rejects.
# The pattern requires at least one leading component then the exact suffix.
POSITION_ID_BUFFER_PATTERN = re.compile(r".+\.embeddings\.position_ids$")

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


def sha256_bytes(data):
    return hashlib.sha256(data).hexdigest()


def sha256_file(path, chunk=1024 * 1024):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            block = f.read(chunk)
            if not block:
                break
            h.update(block)
    return h.hexdigest()


def git_blob_sha1_bytes(data):
    """The SHA-1 git assigns a blob with these bytes (git hash-object).

    git hashes 'blob <len>\\0' + content. This is how the approval marker's
    contract_blob is bound to the contract file, with no git dependency.
    """
    header = b"blob %d\x00" % len(data)
    return hashlib.sha1(header + data).hexdigest()


def git_blob_sha1(path):
    return git_blob_sha1_bytes(Path(path).read_bytes())


def write_json(path, obj):
    with open(path, "w") as f:
        json.dump(obj, f, indent=2, sort_keys=True)
        f.write("\n")


def utc_now():
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def assert_validation_only(name):
    """Split guard: this study may touch the validation split ONLY.

    Any path or volume name that is not clearly validation-split is refused,
    which enforces both "no test-set access" and "no train-volume access".
    """
    lowered = str(name).lower()
    if "test" in lowered:
        fail(7, f"split guard: refused test-split resource '{name}'")
    base = os.path.basename(lowered)
    if base.startswith("train_") or "/train/" in lowered:
        fail(7, f"split guard: refused train-split resource '{name}'")


# ---------------------------------------------------------------------------
# PHASE 0 -- GATE. The collaborator rules forbid probe-code execution without
# a reviewed card, feasibility memo, contract, and explicit human approval.
# The approval mechanism here is hash-bound: HUMAN_APPROVED_PROBE records the
# git blob of the contract it approves, and this driver recomputes the
# contract's blob and refuses on any mismatch. That single check is what makes
# the contract's two-phase flow mechanical: recording the manifest hash amends
# the contract, changes its blob, and instantly stales the phase-1 marker.
# ---------------------------------------------------------------------------

def contract_scalar(text, key):
    """Return the value of the unique line '<indent><key>: <value>'.

    A minimal line-based reader (no PyYAML dependency). The value is taken up
    to an unquoted '#', with surrounding quotes stripped. Exactly one matching
    line must exist; zero or several is a gate failure, because every key this
    driver reads is load-bearing and must be unambiguous.
    """
    pattern = re.compile(r"^\s*" + re.escape(key) + r":\s*(.*)$")
    matches = []
    for line in text.splitlines():
        m = pattern.match(line)
        if m:
            matches.append(m.group(1))
    if len(matches) != 1:
        fail(2, f"contract key '{key}' matched {len(matches)} lines; "
                f"expected exactly one")
    raw = matches[0].strip()
    if raw.startswith('"'):
        end = raw.find('"', 1)
        if end < 0:
            fail(2, f"contract key '{key}' has an unterminated quoted value")
        return raw[1:end]
    # Unquoted: strip a trailing comment, then whitespace.
    return raw.split("#", 1)[0].strip()


def phase_b_entry_check(contract_text, marker_blob, actual_blob):
    """Pure phase-B entry gate (contract approval_and_phasing.phase_B).

    Returns (ok, reason, manifest_sha, unique_count). Pure so smoke mode can
    assert both refusal branches without touching real state.
    """
    if marker_blob != actual_blob:
        return (False,
                "approval marker contract_blob does not match the contract's "
                "current git blob (stale or missing phase-2 approval)",
                None, None)
    if PLACEHOLDER in contract_text:
        return (False,
                f"contract still contains the {PLACEHOLDER} placeholder; "
                f"phase M has not been recorded into the contract",
                None, None)
    manifest_sha = contract_scalar(contract_text, "pair_manifest_sha256")
    unique_raw = contract_scalar(contract_text, "unique_volume_count")
    if not re.fullmatch(r"[0-9a-f]{64}", manifest_sha):
        return (False,
                f"pair_manifest_sha256 is not a SHA-256 hex digest: "
                f"{manifest_sha!r}", None, None)
    try:
        unique_count = int(unique_raw)
    except ValueError:
        return (False,
                f"unique_volume_count is not an integer: {unique_raw!r}",
                None, None)
    return (True, "", manifest_sha, unique_count)


def phase0_gate(phase):
    """Common approval/contract gate; extra entry conditions for phase B."""
    log("PHASE 0: approval and contract gate")
    if not CONTRACT_PATH.exists():
        fail(2, f"contract not found at {CONTRACT_PATH}")
    if not APPROVAL_PATH.exists():
        fail(2, f"human approval marker not found at {APPROVAL_PATH}; "
                f"do not run")
    contract_text = CONTRACT_PATH.read_text()
    actual_blob = git_blob_sha1(CONTRACT_PATH)

    # The marker records the approved contract blob on a 'contract_blob:' line.
    marker_text = APPROVAL_PATH.read_text()
    marker_match = re.search(r"contract_blob:\s*([0-9a-f]{40})", marker_text)
    if not marker_match:
        fail(2, "approval marker has no 'contract_blob: <sha1>' line; the "
                "hash-bound gate cannot evaluate it")
    marker_blob = marker_match.group(1)
    log(f"  approval marker blob: {marker_blob}")
    log(f"  contract actual blob: {actual_blob}")
    if marker_blob != actual_blob:
        fail(2, "approval marker is bound to a different contract blob; the "
                "contract changed after approval (or approval is for another "
                "version). Re-run approve-probe against the current contract.")
    log("  hash-bound approval VERIFIED: marker matches the contract blob")

    # Anti-drift cross-checks: the load-bearing scalar caps and every
    # provenance pin this code hardcodes must still be what the approved
    # contract says. A mismatch means this reviewed code and the approved
    # contract disagree -- stop, do not guess which one is right.
    for key, expected in [
        ("idea_id", IDEA_ID),
        ("contract_version", str(CONTRACT_VERSION)),
        ("maximum_variants", "1"),
        ("maximum_seeds", "1"),
        ("session_cap", str(SESSION_CAP)),
        ("pair_count_cap", str(TOTAL_PAIRS)),
    ]:
        got = contract_scalar(contract_text, key)
        if got != expected:
            fail(2, f"contract {key}={got!r} does not match frozen "
                    f"constant {expected!r}")
    literal_pins = [
        CHECKPOINT_SHA256, CODE_COMMIT, HF_REVISION,
        TABLES_SHA256["validation_metadata.csv"],
        TABLES_SHA256["valid_predicted_labels.csv"],
        TABLES_SHA256["validation_reports.csv"],
        ANCHOR_INPUT_SHA256[ANCHOR_VOLUME_A],
        ANCHOR_INPUT_SHA256[ANCHOR_VOLUME_B],
        V1_REFERENCE_GIT_BLOB,
        str(TIER1_BOOTSTRAP_SEED), str(TIER2_BOOTSTRAP_SEED),
        "1.0e-4",   # anchor cross-session tolerance as written in the contract
    ]
    for pin in literal_pins:
        if pin not in contract_text:
            fail(2, f"frozen pin {pin!r} not found in the approved contract "
                    f"text; code and contract have drifted")
    log("  contract caps and provenance pins match the frozen constants")

    gate_info = {
        "contract_path": str(CONTRACT_PATH),
        "contract_blob": actual_blob,
        "marker_blob": marker_blob,
        "phase": phase,
    }

    if phase == "B":
        ok, reason, manifest_sha, unique_count = phase_b_entry_check(
            contract_text, marker_blob, actual_blob)
        if not ok:
            fail(2, f"phase B entry refused: {reason}. Phase B requires the "
                    f"post-freeze contract amendment (manifest hash and "
                    f"unique-volume count recorded) plus a fresh "
                    f"approve-probe run bound to the amended blob.")
        gate_info["pair_manifest_sha256"] = manifest_sha
        gate_info["unique_volume_count"] = unique_count
        log(f"  phase B entry conditions hold: manifest sha "
            f"{manifest_sha[:12]}..., unique volumes {unique_count}")
    elif phase == "M":
        # Phase M may re-run after the amendment (idempotent). If the manifest
        # hash is already recorded, remember it so the regenerated manifest
        # can be checked against it instead of re-instructing an amendment.
        if PLACEHOLDER not in contract_text:
            gate_info["recorded_manifest_sha256"] = contract_scalar(
                contract_text, "pair_manifest_sha256")
        else:
            gate_info["recorded_manifest_sha256"] = None
    return gate_info


# ---------------------------------------------------------------------------
# MANIFEST MACHINERY (shared by phase M, phase B, and smoke). Deterministic:
# no randomness, no score peeking, pure metadata filtering. Phase B never
# trusts a stored manifest file alone -- it regenerates the manifest from the
# hash-verified metadata table and requires byte-identity with the contract's
# recorded SHA-256.
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
    2026-08-12, exit-7 root cause; contract R6). Rule: if the value parses as
    a Python list literal, take element 0; otherwise the stripped raw string.
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


def kernel_numeric_index(kernel):
    """The two-digit number in a Siemens kernel name (Br40f -> 40).

    Contract R2 uses this index for the canonical sign direction: within a
    kernel family it tracks spatial-frequency emphasis (sharper = higher).
    """
    m = re.search(r"(\d+)", kernel)
    if not m:
        fail(12, f"kernel {kernel!r} has no numeric index; the R2 sign rule "
                 f"cannot apply (harness fault)")
    return int(m.group(1))


def stratum_softer_sharper(stratum):
    """Map a stratum label 'X|Y' to its (softer, sharper) kernel pair.

    softer = lower numeric index, sharper = higher (contract R2). Ties would
    fall back to lexicographically-greater-minus-lesser; none occur in the
    frozen strata, and a tie here is treated as a harness fault.
    """
    k1, k2 = stratum.split("|")
    i1, i2 = kernel_numeric_index(k1), kernel_numeric_index(k2)
    if i1 == i2:
        # Contract fallback: lexicographically greater kernel is "sharper".
        return (min(k1, k2), max(k1, k2))
    return (k1, k2) if i1 < i2 else (k2, k1)


def assert_sign_directions():
    """The numeric R2 rule must reproduce the contract's explicit table."""
    for stratum, expected in CONTRACT_SIGN_DIRECTIONS.items():
        derived = stratum_softer_sharper(stratum)
        if derived != expected:
            fail(12, f"sign-direction rule derived {derived} for {stratum}, "
                     f"contract table says {expected}; harness fault")


def build_pair_manifest(rows, frozen_counts, anchor_names):
    """Apply the frozen Stage-0 matching rules across all four strata.

    `rows` is the metadata table as a list of dicts. Returns (pairs, audit):
    pairs is the ordered manifest (list of dicts with MANIFEST_COLUMNS keys),
    audit is the always-written selection audit with the kernel tally and
    per-filter drop counts (contract R6). The caller enforces the hard gate
    on per-stratum counts.
    """
    audit = {
        "total_rows": len(rows),
        "non_validation_refused": 0,
        "match_columns_used": [],
        "kernel_values_top10": [],
        "per_stratum": {},
        "frozen_counts": dict(frozen_counts),
        # Defaults below survive the empty-table early return, so the
        # shortfall reporter and the phase gates always find their keys and
        # the failure surfaces as the contract's selection failure (exit 7),
        # never as a harness fault.
        "selected_counts": {},
        "unique_volume_count": 0,
        "counts_match": False,
    }

    # Split guard at the metadata level: anything not valid_* is dropped and
    # counted. Train/test rows must never enter pair consideration.
    validation_rows = []
    for row in rows:
        name = row.get("VolumeName", "")
        if parse_volume_name(name) is None:
            audit["non_validation_refused"] += 1
            continue
        validation_rows.append(row)
    if not validation_rows:
        return [], audit

    # Fail loudly if the schema lacks a required geometry column: proceeding
    # without it would silently weaken the frozen Stage-0 rules.
    columns = set(validation_rows[0].keys())
    missing = [c for c in REQUIRED_MATCH_COLUMNS if c not in columns]
    if missing:
        fail(7, f"metadata is missing required match columns {missing}; "
                f"observed columns: {sorted(columns)}")
    if KERNEL_COLUMN not in columns:
        fail(7, f"metadata is missing kernel column '{KERNEL_COLUMN}'")
    match_columns = REQUIRED_MATCH_COLUMNS + [
        c for c in OPTIONAL_MATCH_COLUMNS if c in columns]
    audit["match_columns_used"] = match_columns

    # Kernel-field tally (contract R6 diagnosability): top-10 distinct raw
    # values with counts, normalized forms, and example VolumeNames.
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
        patient, scan, _recon = parse_volume_name(row["VolumeName"])
        scans.setdefault((patient, scan), []).append(row)

    # Per stratum, in the contract's fixed order: a scan group qualifies when
    # it holds EXACTLY one member of each of the stratum's two kernels and
    # every match column is string-identical between the two members. A scan
    # group may qualify for more than one stratum (e.g. Br40f+Br60f+Br44f),
    # which is why the unique-volume count is computed from the manifest
    # rather than assumed to be 425 x 2.
    pairs = []
    for stratum in STRATA_ORDER:
        softer_kernel, sharper_kernel = stratum_softer_sharper(stratum)
        drops = {
            "scans_total": len(scans),
            "scans_without_one_member_of_each_kernel": 0,
            "scans_with_duplicate_contrast_members": 0,
            "candidate_pairs_failing_geometry_match": 0,
            "geometry_mismatches_by_column": {},
        }
        stratum_pairs = []
        for (patient, scan), members in sorted(scans.items()):
            softer_members = [r for r in members
                              if normalize_kernel(r.get(KERNEL_COLUMN))
                              == softer_kernel]
            sharper_members = [r for r in members
                               if normalize_kernel(r.get(KERNEL_COLUMN))
                               == sharper_kernel]
            if not softer_members or not sharper_members:
                drops["scans_without_one_member_of_each_kernel"] += 1
                continue
            if len(softer_members) > 1 or len(sharper_members) > 1:
                drops["scans_with_duplicate_contrast_members"] += 1
                continue
            row_s, row_h = softer_members[0], sharper_members[0]
            # Exact string equality on every match column: identical
            # deterministic preprocessing inputs (Stage-0 "strictly clean").
            mismatched = [c for c in match_columns
                          if row_s.get(c, "") != row_h.get(c, "")]
            if mismatched:
                drops["candidate_pairs_failing_geometry_match"] += 1
                for c in mismatched:
                    drops["geometry_mismatches_by_column"][c] = (
                        drops["geometry_mismatches_by_column"].get(c, 0) + 1)
                continue
            name_s = row_s["VolumeName"]
            name_h = row_h["VolumeName"]
            is_anchor = {name_s, name_h} == set(anchor_names)
            stratum_pairs.append({
                "patient_id": f"valid_{patient}",
                "volume_name_softer": name_s,
                "volume_name_sharper": name_h,
                "stratum": stratum,
                "kernel_normalized_softer":
                    normalize_kernel(row_s.get(KERNEL_COLUMN)),
                "kernel_normalized_sharper":
                    normalize_kernel(row_h.get(KERNEL_COLUMN)),
                "anchor_excluded": "true" if is_anchor else "false",
            })
        # Contract pair_id_rule: within each stratum, ascending lexicographic
        # order of volume_name_softer.
        stratum_pairs.sort(key=lambda p: p["volume_name_softer"])
        pairs.extend(stratum_pairs)
        drops["selected_pairs"] = len(stratum_pairs)
        audit["per_stratum"][stratum] = drops

    # pair_id assignment across the concatenated fixed-order strata.
    for i, pair in enumerate(pairs, start=1):
        pair["pair_id"] = f"p{i:03d}"

    audit["selected_counts"] = {
        s: audit["per_stratum"][s]["selected_pairs"] for s in STRATA_ORDER}
    audit["counts_match"] = audit["selected_counts"] == dict(frozen_counts)
    audit["unique_volume_count"] = len(
        {p["volume_name_softer"] for p in pairs}
        | {p["volume_name_sharper"] for p in pairs})
    return pairs, audit


def manifest_csv_bytes(pairs):
    """Serialize the manifest deterministically (byte-stable for hashing).

    Manual join with '\\n' line endings so the SHA-256 recorded in the
    contract is reproducible on any platform. Fields are checked to be
    CSV-safe; a comma or quote in any field is a harness fault, not silently
    escaped, because escaping rules would make byte-stability fragile.
    """
    lines = [",".join(MANIFEST_COLUMNS)]
    for pair in pairs:
        values = [str(pair[c]) for c in MANIFEST_COLUMNS]
        for v in values:
            if any(ch in v for ch in ',"\n\r'):
                fail(12, f"manifest field {v!r} is not CSV-safe; the "
                         f"deterministic writer cannot represent it")
        lines.append(",".join(values))
    return ("\n".join(lines) + "\n").encode("utf-8")


def report_selection_shortfall(audit, frozen_counts, out_path):
    """Dump selection diagnostics to the run log on a count mismatch.

    Contract R6: on ANY shortfall versus the frozen manifest, the top-10
    distinct kernel values (with counts and example VolumeNames) and the
    per-filter drop counts go to the run log AND selection_audit.json (the
    caller writes that file unconditionally). A shortfall without a matching
    audit is itself invalidating, which is why the audit write precedes the
    exit in every path.
    """
    log(f"  SELECTION MISMATCH vs frozen counts {frozen_counts}; "
        f"got {audit['selected_counts']}; diagnostics follow")
    log(f"  top-10 distinct {KERNEL_COLUMN} values "
        f"(raw -> normalized: count, example VolumeNames):")
    for item in audit["kernel_values_top10"]:
        log(f"    {item['raw']!r} -> {item['normalized']!r}: "
            f"{item['count']} (e.g. {', '.join(item['example_volume_names'])})")
    for stratum in STRATA_ORDER:
        log(f"  per-filter drops [{stratum}]: "
            f"{json.dumps(audit['per_stratum'].get(stratum, {}), sort_keys=True)}")
    log(f"  full audit: {out_path}")


# ---------------------------------------------------------------------------
# SCORING PLUMBING (shared by real phase B and smoke). Bit-identity is always
# judged on the float64 hex encodings (score_hex), never on a numeric
# tolerance -- within-session repeats must be exactly reproducible.
# ---------------------------------------------------------------------------

def scores_hex(scores):
    """Float64 hex encodings; equality of these lists IS bit-identity."""
    return [float(s).hex() for s in scores]


def check_18_finite(scores, label):
    """Contract output-shape check: exactly 18 finite scores (exit 6)."""
    if len(scores) != len(EXPECTED_PATHOLOGIES):
        fail(6, f"{label} produced {len(scores)} scores, expected "
                f"{len(EXPECTED_PATHOLOGIES)}")
    non_finite = [EXPECTED_PATHOLOGIES[i] for i, s in enumerate(scores)
                  if not math.isfinite(s)]
    if non_finite:
        fail(6, f"{label} produced non-finite scores for {non_finite}")


def max_abs_deviation(scores, reference):
    """Max per-head |difference| on the probability scale (anchor check)."""
    if len(scores) != len(reference):
        fail(12, "anchor comparison length mismatch; harness fault")
    return max(abs(float(a) - float(b)) for a, b in zip(scores, reference))


def load_v1_reference():
    """Load the pinned v1 anchor reference scores (exec1_A and exec2_B rows).

    The file itself is provenance-checked: its git blob must equal the
    contract pin, so a modified or regenerated file cannot silently move the
    anchor target.
    """
    if not V1_REFERENCE_PATH.exists():
        fail(3, f"v1 anchor reference not found at {V1_REFERENCE_PATH}; the "
                f"cross-session anchor check cannot run (contract "
                f"provenance_pins.v1_anchor_reference_scores)")
    actual_blob = git_blob_sha1(V1_REFERENCE_PATH)
    if actual_blob != V1_REFERENCE_GIT_BLOB:
        fail(4, f"v1 anchor reference blob {actual_blob} != pinned "
                f"{V1_REFERENCE_GIT_BLOB}; the reference file changed")
    reference = {"exec1_A": [None] * 18, "exec2_B": [None] * 18}
    with open(V1_REFERENCE_PATH, newline="") as f:
        for row in csv.DictReader(f):
            if row["execution"] in reference:
                # 'score' was written as repr(float) by v1, so float() round-
                # trips the exact double; score_hex is cross-checked.
                value = float(row["score"])
                if float.fromhex(row["score_hex"]) != value:
                    fail(4, f"v1 reference row {row['execution']}/"
                            f"{row['head_index']}: score and score_hex "
                            f"disagree; file is corrupt")
                reference[row["execution"]][int(row["head_index"])] = value
    for exec_id, values in reference.items():
        if any(v is None for v in values):
            fail(4, f"v1 reference is missing heads for {exec_id}")
    return reference


# ---------------------------------------------------------------------------
# TIER-1 ANALYSIS (contract R3; primary, label-free, confirmatory). Pure
# computation over the per-pair scores: signed differences sharper-minus-
# softer on the probability and logit scales, per-cell summary statistics,
# and patient-cluster bootstrap intervals. NO cross-head averaging appears
# anywhere. The Br40f|Br44f stratum is listed per pair only: no summary
# statistic and no bootstrap interval is computed for it (contract
# tier1_analysis.exploratory_stratum), and the anchor pair is excluded from
# every summary and bootstrap (frozen_scope.anchor_pair_exclusion).
# ---------------------------------------------------------------------------

def logit_clipped(p):
    """ln(p/(1-p)) with p clipped to [1e-6, 1-1e-6] (preregistered clip).

    Returns (logit_value, was_clipped). The clip count is reported per head
    per stratum, per the contract.
    """
    clipped = min(max(float(p), LOGIT_CLIP), 1.0 - LOGIT_CLIP)
    return math.log(clipped / (1.0 - clipped)), (clipped != float(p))


def tier1_compute(pairs, scores_by_pair, replicates, rng_seed,
                  confirmatory_strata, exploratory_strata):
    """Compute tier-1 differences, per-cell statistics, and bootstrap CIs.

    pairs: the manifest (ordered dicts). scores_by_pair maps pair_id ->
    {"softer": [18 floats], "sharper": [18 floats]} (probabilities).
    Returns (diff_rows, stat_rows, boot_rows) ready for CSV; per-cell clip
    counts travel inside the stat rows.

    Bootstrap design (documented here because the contract fixes the seed and
    unit but not the resample bookkeeping): ONE numpy default_rng stream,
    seeded once, consumed stratum by stratum in the fixed contract order. For
    each confirmatory stratum, `replicates` patient resamples are drawn
    (patients sampled with replacement, every manifest pair of a sampled
    patient entering with multiplicity); each resample is reused for all 18
    heads, both scales, and all three statistics, so a replicate is one
    coherent resampled world rather than a fresh draw per cell.
    """
    import numpy as np

    # -- per-pair signed differences, both scales, with clip accounting.
    diff_rows = []
    clip_counts = {}   # (stratum, head_index) -> clipped member count
    per_pair_d = {}    # pair_id -> {"prob": np.array(18), "logit": np.array(18)}
    for pair in pairs:
        pid = pair["pair_id"]
        s_soft = scores_by_pair[pid]["softer"]
        s_sharp = scores_by_pair[pid]["sharper"]
        d_prob = []
        d_logit = []
        for h in range(18):
            lo_soft, clip_soft = logit_clipped(s_soft[h])
            lo_sharp, clip_sharp = logit_clipped(s_sharp[h])
            n_clipped = int(clip_soft) + int(clip_sharp)
            # Per-cell clip counts cover the CONFIRMATORY-COUNTED set only,
            # consistent with every other statistic in the same stats row;
            # the anchor pair's clips remain visible per pair in the
            # differences table.
            if pair["anchor_excluded"] != "true":
                key = (pair["stratum"], h)
                clip_counts[key] = clip_counts.get(key, 0) + n_clipped
            # Canonical sign (contract R2): sharper minus softer, always.
            d_p = float(s_sharp[h]) - float(s_soft[h])
            d_l = lo_sharp - lo_soft
            d_prob.append(d_p)
            d_logit.append(d_l)
            diff_rows.append({
                "pair_id": pid,
                "patient_id": pair["patient_id"],
                "stratum": pair["stratum"],
                "anchor_excluded": pair["anchor_excluded"],
                "exploratory": ("true" if pair["stratum"]
                                in exploratory_strata else "false"),
                "head_index": h,
                "head_name": EXPECTED_PATHOLOGIES[h],
                "softer_prob": repr(float(s_soft[h])),
                "sharper_prob": repr(float(s_sharp[h])),
                "d_prob": repr(d_p),
                "d_logit": repr(d_l),
                "n_clipped_members": n_clipped,
            })
        per_pair_d[pid] = {"prob": np.array(d_prob),
                           "logit": np.array(d_logit)}

    # -- per-cell statistics on the confirmatory-counted set (anchor pair
    #    excluded; contract: 236 counted Br40f|Br60f pairs, both raw and
    #    counted denominators reported).
    stat_rows = []
    boot_rows = []
    rng = np.random.default_rng(rng_seed)
    for stratum in [s for s in STRATA_ORDER if s in confirmatory_strata]:
        stratum_pairs = [p for p in pairs if p["stratum"] == stratum]
        counted = [p for p in stratum_pairs
                   if p["anchor_excluded"] != "true"]
        n_raw, n_counted = len(stratum_pairs), len(counted)
        # Matrices (n_counted x 18) per scale, in pair_id order (already the
        # manifest order, which is deterministic).
        d_mats = {
            "probability": np.stack(
                [per_pair_d[p["pair_id"]]["prob"] for p in counted]),
            "logit": np.stack(
                [per_pair_d[p["pair_id"]]["logit"] for p in counted]),
        }
        for scale, mat in d_mats.items():
            for h in range(18):
                col = mat[:, h]
                abs_col = np.abs(col)
                # Quantiles use numpy's default linear interpolation; the
                # method is recorded in resolved_config.json.
                q = {f"q{int(qq * 100):02d}_abs":
                     float(np.quantile(abs_col, qq)) for qq in ABS_QUANTILES}
                stat_rows.append({
                    "stratum": stratum,
                    "head_index": h,
                    "head_name": EXPECTED_PATHOLOGIES[h],
                    "scale": scale,
                    "n_raw": n_raw,
                    "n_counted": n_counted,
                    "median_signed": float(np.median(col)),
                    "mean_signed": float(np.mean(col)),
                    "q50_abs": q["q50_abs"],
                    "q75_abs": q["q75_abs"],
                    "q90_abs": q["q90_abs"],
                    "q95_abs": q["q95_abs"],
                    "max_abs": q["q100_abs"],
                    "n_clipped_members":
                        clip_counts.get((stratum, h), 0),
                })

        # -- patient-cluster bootstrap for this stratum (contract R3).
        patients = sorted({p["patient_id"] for p in counted})
        pair_rows_by_patient = {pt: [] for pt in patients}
        for i, p in enumerate(counted):
            pair_rows_by_patient[p["patient_id"]].append(i)
        patient_row_lists = [np.array(pair_rows_by_patient[pt])
                             for pt in patients]
        n_patients = len(patients)
        # boot_samples[scale][stat] -> (replicates x 18) array
        boot_samples = {
            scale: {stat: np.empty((replicates, 18))
                    for stat in BOOTSTRAP_STATISTICS}
            for scale in d_mats
        }
        for r in range(replicates):
            sampled = rng.integers(0, n_patients, size=n_patients)
            idx = np.concatenate([patient_row_lists[i] for i in sampled])
            for scale, mat in d_mats.items():
                sub = mat[idx]
                boot_samples[scale]["median_signed"][r] = np.median(sub,
                                                                    axis=0)
                boot_samples[scale]["mean_signed"][r] = np.mean(sub, axis=0)
                boot_samples[scale]["q95_abs"][r] = np.quantile(
                    np.abs(sub), 0.95, axis=0)
        point = {
            "probability": {
                "median_signed": np.median(d_mats["probability"], axis=0),
                "mean_signed": np.mean(d_mats["probability"], axis=0),
                "q95_abs": np.quantile(np.abs(d_mats["probability"]),
                                       0.95, axis=0),
            },
            "logit": {
                "median_signed": np.median(d_mats["logit"], axis=0),
                "mean_signed": np.mean(d_mats["logit"], axis=0),
                "q95_abs": np.quantile(np.abs(d_mats["logit"]), 0.95, axis=0),
            },
        }
        for scale in ("probability", "logit"):
            for stat in BOOTSTRAP_STATISTICS:
                lo = np.percentile(boot_samples[scale][stat],
                                   BOOTSTRAP_INTERVAL[0], axis=0)
                hi = np.percentile(boot_samples[scale][stat],
                                   BOOTSTRAP_INTERVAL[1], axis=0)
                for h in range(18):
                    boot_rows.append({
                        "stratum": stratum,
                        "head_index": h,
                        "head_name": EXPECTED_PATHOLOGIES[h],
                        "scale": scale,
                        "statistic": stat,
                        "point": float(point[scale][stat][h]),
                        "ci95_lo": float(lo[h]),
                        "ci95_hi": float(hi[h]),
                        "replicates": replicates,
                        "n_patients": n_patients,
                        "n_counted_pairs": n_counted,
                    })
    return diff_rows, stat_rows, boot_rows


# ---------------------------------------------------------------------------
# TIER-2 ANALYSIS (contract R4; secondary, DESCRIPTIVE, label-dependent).
# Runs only if tier 1 completed. Per head x stratum: delta-AUROC =
# AUROC(sharper-member scores) - AUROC(softer-member scores) against the
# released report-derived labels, on the [0,1] scale, with patient-cluster
# bootstrap intervals. The preregistered sparse-label rule excludes cells
# with < 10 positive or < 10 negative counted pairs; every excluded cell is
# tabulated with its counts. ZERO threshold language anywhere: no number
# computed here carries pass/fail semantics (amended pin 2).
# ---------------------------------------------------------------------------

def label_integrity_problems(pairs, labels_by_volume):
    """Pure check of the released-label duplication premise (contract
    invalidating_failures: "Label integrity"). Returns a list of problem
    strings; empty means every pair's two members carry identical rows."""
    problems = []
    for pair in pairs:
        name_s = pair["volume_name_softer"]
        name_h = pair["volume_name_sharper"]
        missing = [n for n in (name_s, name_h) if n not in labels_by_volume]
        if missing:
            problems.append(f"{pair['pair_id']}: missing label rows "
                            f"{missing}")
            continue
        if labels_by_volume[name_s] != labels_by_volume[name_h]:
            problems.append(f"{pair['pair_id']}: members {name_s} / {name_h} "
                            f"carry differing label rows")
    return problems


def tier2_compute(pairs, scores_by_pair, labels_by_volume, replicates,
                  rng_seed, min_positive, min_negative):
    """Compute tier-2 AUROC deltas and the mandatory excluded-cells table.

    labels_by_volume maps VolumeName -> list of 18 ints (released labels).
    Label integrity (contract invalidating_failures): both members of a pair
    must carry identical label rows; a mismatch is world drift, exit 7.
    Returns (auroc_rows, excluded_rows).
    """
    import numpy as np
    from sklearn.metrics import roc_auc_score

    # Label integrity + per-pair label vector (each pair contributes ONE label
    # row, because labels are duplicated within pair per Stage 0). A missing
    # or differing label row is world drift and invalidating (exit 7).
    problems = label_integrity_problems(pairs, labels_by_volume)
    if problems:
        fail(7, f"released-label integrity failed (world drift, stop and "
                f"report): {problems[:5]}"
                + (f" ... and {len(problems) - 5} more" if len(problems) > 5
                   else ""))
    label_for_pair = {p["pair_id"]: labels_by_volume[p["volume_name_softer"]]
                      for p in pairs}

    auroc_rows = []
    excluded_rows = []
    rng = np.random.default_rng(rng_seed)
    # All four strata pass through the same mechanical sparse rule; the
    # 4-pair exploratory stratum can never reach 10/10 and lands in the
    # excluded table with its actual counts, which is its required reporting.
    for stratum in STRATA_ORDER:
        counted = [p for p in pairs if p["stratum"] == stratum
                   and p["anchor_excluded"] != "true"]
        if not counted:
            continue
        y = np.array([label_for_pair[p["pair_id"]] for p in counted])
        s_soft = np.array([scores_by_pair[p["pair_id"]]["softer"]
                           for p in counted])
        s_sharp = np.array([scores_by_pair[p["pair_id"]]["sharper"]
                            for p in counted])
        n = len(counted)

        eligible_heads = []
        for h in range(18):
            pos = int(y[:, h].sum())
            neg = n - pos
            if pos >= min_positive and neg >= min_negative:
                eligible_heads.append(h)
            else:
                excluded_rows.append({
                    "stratum": stratum,
                    "head_index": h,
                    "head_name": EXPECTED_PATHOLOGIES[h],
                    "n_counted_pairs": n,
                    "n_positive": pos,
                    "n_negative": neg,
                    "reason": EXCLUDED_CELL_LABEL,
                })
        if not eligible_heads:
            continue

        # Patient-cluster resamples, same design as tier 1 but with the
        # separate preregistered rng stream (20260815).
        patients = sorted({p["patient_id"] for p in counted})
        rows_by_patient = {pt: [] for pt in patients}
        for i, p in enumerate(counted):
            rows_by_patient[p["patient_id"]].append(i)
        patient_row_lists = [np.array(rows_by_patient[pt]) for pt in patients]
        n_patients = len(patients)

        # boot[h] holds (auroc_sharper, auroc_softer, delta) per replicate;
        # a replicate whose resample is single-class for head h yields NaN
        # (counted and reported; percentile over the finite replicates).
        boot = {h: np.full((replicates, 3), np.nan) for h in eligible_heads}
        for r in range(replicates):
            sampled = rng.integers(0, n_patients, size=n_patients)
            idx = np.concatenate([patient_row_lists[i] for i in sampled])
            y_r = y[idx]
            soft_r = s_soft[idx]
            sharp_r = s_sharp[idx]
            for h in eligible_heads:
                labels_h = y_r[:, h]
                if labels_h.min() == labels_h.max():
                    continue  # single-class resample -> NaN row
                a_sharp = roc_auc_score(labels_h, sharp_r[:, h])
                a_soft = roc_auc_score(labels_h, soft_r[:, h])
                boot[h][r] = (a_sharp, a_soft, a_sharp - a_soft)

        for h in eligible_heads:
            pos = int(y[:, h].sum())
            a_sharp = float(roc_auc_score(y[:, h], s_sharp[:, h]))
            a_soft = float(roc_auc_score(y[:, h], s_soft[:, h]))
            samples = boot[h]
            nan_mask = np.isnan(samples[:, 0])
            nan_count = int(nan_mask.sum())
            finite = samples[~nan_mask]
            cis = {}
            for j, quantity in enumerate(
                    ["auroc_sharper", "auroc_softer", "delta_auroc"]):
                if len(finite):
                    cis[quantity] = (
                        float(np.percentile(finite[:, j],
                                            BOOTSTRAP_INTERVAL[0])),
                        float(np.percentile(finite[:, j],
                                            BOOTSTRAP_INTERVAL[1])))
                else:
                    cis[quantity] = (float("nan"), float("nan"))
            auroc_rows.append({
                "stratum": stratum,
                "head_index": h,
                "head_name": EXPECTED_PATHOLOGIES[h],
                "n_counted_pairs": len(counted),
                "n_positive": pos,
                "n_negative": len(counted) - pos,
                "auroc_sharper": a_sharp,
                "auroc_softer": a_soft,
                "delta_auroc": a_sharp - a_soft,
                "auroc_sharper_ci95_lo": cis["auroc_sharper"][0],
                "auroc_sharper_ci95_hi": cis["auroc_sharper"][1],
                "auroc_softer_ci95_lo": cis["auroc_softer"][0],
                "auroc_softer_ci95_hi": cis["auroc_softer"][1],
                "delta_auroc_ci95_lo": cis["delta_auroc"][0],
                "delta_auroc_ci95_hi": cis["delta_auroc"][1],
                "replicates": replicates,
                "nan_replicates": nan_count,
            })
    return auroc_rows, excluded_rows


def write_csv(path, rows, fieldnames):
    """Write dict rows to CSV; tolerates an empty row list (header only)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


# ---------------------------------------------------------------------------
# ENVIRONMENT CAPTURE. Phase M needs only stdlib + huggingface_hub. Phase B
# fixes every seed and determinism switch BEFORE any model code runs, and
# HARD-CHECKS the r6 environment pins: a session on any other
# transformers/tokenizers version is environment drift (invalidating,
# exit 10), not a warning.
# ---------------------------------------------------------------------------

def capture_environment(out_dir, phase, need_gpu):
    log("environment: seeds, determinism switches, version capture")
    random.seed(SEED)
    os.environ["PYTHONHASHSEED"] = str(SEED)
    # Required by CUDA for deterministic cuBLAS matmuls (bit-identity checks).
    os.environ.setdefault("CUBLAS_WORKSPACE_CONFIG", ":4096:8")

    env = {
        "python": sys.version.replace("\n", " "),
        "platform": platform.platform(),
        "machine": platform.machine(),
        "seed": SEED,
        "phase": phase,
        "CUBLAS_WORKSPACE_CONFIG": os.environ["CUBLAS_WORKSPACE_CONFIG"],
    }
    if need_gpu:
        try:
            import numpy
            import torch
            import transformers
            import tokenizers
        except ImportError as e:
            fail(11, f"missing phase-B dependency: {e}; install "
                     f"probes/004/requirements.txt first (environment "
                     f"problem, not a contract result)")
        # r6 pins are ABSOLUTE across sessions (contract R5): deviation is
        # invalidating environment drift, exit 10, before any model work.
        if transformers.__version__ != TRANSFORMERS_PIN:
            fail(10, f"transformers {transformers.__version__} != pinned "
                     f"{TRANSFORMERS_PIN}; environment drift (invalidating)")
        if tokenizers.__version__ != TOKENIZERS_PIN:
            fail(10, f"tokenizers {tokenizers.__version__} != pinned "
                     f"{TOKENIZERS_PIN}; environment drift (invalidating)")
        log(f"  transformers {transformers.__version__} / tokenizers "
            f"{tokenizers.__version__} match the pinned r6 closure")
        numpy.random.seed(SEED)
        torch.manual_seed(SEED)
        torch.cuda.manual_seed_all(SEED)
        torch.backends.cudnn.deterministic = True
        torch.backends.cudnn.benchmark = False
        # warn_only: the empirical bit-identity repeats arbitrate if a
        # released CUDA op lacks a deterministic implementation.
        torch.use_deterministic_algorithms(True, warn_only=True)
        if not torch.cuda.is_available():
            fail(11, "no CUDA GPU visible; phase B always needs a GPU "
                     "runtime (the anchor protocol runs at every session "
                     "start, including analysis-only sessions)")
        env["gpu"] = torch.cuda.get_device_name(0)
        env["torch"] = torch.__version__
        env["cuda"] = torch.version.cuda
        env["numpy"] = numpy.__version__
        env["transformers"] = transformers.__version__
        env["tokenizers"] = tokenizers.__version__
        for mod in ("nibabel", "pandas", "huggingface_hub", "sklearn"):
            try:
                m = __import__(mod)
                env[mod] = getattr(m, "__version__", "unknown")
            except Exception as e:
                fail(11, f"phase-B dependency {mod} not importable ({e!r})")
    lines = [f"{k}: {v}" for k, v in env.items()]
    (out_dir / "environment.txt").write_text("\n".join(lines) + "\n")
    return env


def write_resolved_config(out_dir, phase, extra=None):
    """The fully resolved frozen configuration, for reproducibility from the
    artifacts alone. Everything here restates the contract; nothing is a
    knob."""
    config = {
        "idea_id": IDEA_ID,
        "contract_version": CONTRACT_VERSION,
        "phase": phase,
        "seed": SEED,
        "batch_size": 1,               # contract: batch size 1, never changed
        "patch_size_modified": False,  # contract: released patch size only
        "hf_dataset_repo": HF_DATASET_REPO,
        "hf_revision_pinned": HF_REVISION,
        "checkpoint_repo_path": CHECKPOINT_REPO_PATH,
        "checkpoint_sha256_pinned": CHECKPOINT_SHA256,
        "ctclip_git_url": CTCLIP_GIT_URL,
        "code_commit_pinned": CODE_COMMIT,
        "tokenizer": TOKENIZER_NAME,
        "tables_sha256_pinned": TABLES_SHA256,
        "strata_order": STRATA_ORDER,
        "frozen_stratum_counts": FROZEN_STRATUM_COUNTS,
        "exploratory_strata": sorted(EXPLORATORY_STRATA),
        "sign_rule": ("d = s(sharper) - s(softer); sharper = higher numeric "
                      "kernel index (contract R2); pair ordering in the data "
                      "never determines sign"),
        "sign_directions": {s: {"softer": v[0], "sharper": v[1]}
                            for s, v in CONTRACT_SIGN_DIRECTIONS.items()},
        "required_match_columns": REQUIRED_MATCH_COLUMNS,
        "optional_match_columns": OPTIONAL_MATCH_COLUMNS,
        "chunking": {"chunk_size_pairs": CHUNK_SIZE_PAIRS,
                     "chunk_count": CHUNK_COUNT},
        "budgets": {"pair_count_cap": TOTAL_PAIRS,
                    "session_cap": SESSION_CAP,
                    "qa_retry_fraction": QA_RETRY_FRACTION},
        "anchor": {"volume_A": ANCHOR_VOLUME_A, "volume_B": ANCHOR_VOLUME_B,
                   "input_sha256": ANCHOR_INPUT_SHA256,
                   "cross_session_tolerance":
                       ANCHOR_CROSS_SESSION_TOLERANCE,
                   "v1_reference_git_blob": V1_REFERENCE_GIT_BLOB},
        "tier1": {"bootstrap_seed": TIER1_BOOTSTRAP_SEED,
                  "replicates": BOOTSTRAP_REPLICATES,
                  "interval_percentiles": list(BOOTSTRAP_INTERVAL),
                  "logit_clip": LOGIT_CLIP,
                  "abs_quantiles": ABS_QUANTILES,
                  "bootstrapped_statistics": BOOTSTRAP_STATISTICS,
                  "quantile_method": "numpy default (linear interpolation)",
                  "resample_design": ("one rng stream, strata in fixed "
                                      "order; per stratum, one patient "
                                      "resample per replicate reused across "
                                      "heads, scales, and statistics")},
        "tier2": {"bootstrap_seed": TIER2_BOOTSTRAP_SEED,
                  "replicates": BOOTSTRAP_REPLICATES,
                  "sparse_min_positive": SPARSE_MIN_POSITIVE,
                  "sparse_min_negative": SPARSE_MIN_NEGATIVE,
                  "scale": "[0,1] AUROC",
                  "threshold_language": "none anywhere (amended pin 2)"},
        "environment_pins": {"transformers": TRANSFORMERS_PIN,
                             "tokenizers": TOKENIZERS_PIN},
        "expected_pathologies": EXPECTED_PATHOLOGIES,
    }
    if extra:
        config.update(extra)
    write_json(out_dir / "resolved_config.json", config)
    log(f"  resolved_config.json written to {out_dir}")
    return config


# ---------------------------------------------------------------------------
# HF ARTIFACT HELPERS. Every download is pinned to the contract's HF revision
# and hash-verified against the contract pin (or recorded before inference,
# for volumes). The split guard runs on every repo path.
# ---------------------------------------------------------------------------

def hf_download(repo_path, dest_dir):
    """Download one file at the PINNED revision; return its local path."""
    assert_validation_only(repo_path)
    try:
        from huggingface_hub import hf_hub_download
    except ImportError as e:
        fail(11, f"huggingface_hub not installed: {e}")
    try:
        local = hf_hub_download(HF_DATASET_REPO, repo_path,
                                repo_type="dataset", revision=HF_REVISION,
                                local_dir=str(dest_dir))
    except Exception as e:
        fail(3, f"download failed for {repo_path} at pinned revision "
                f"{HF_REVISION}: {e}")
    return Path(local)


def find_repo_file(name_fragment):
    """Resolve a table's repo path case-insensitively at the pinned revision.

    Excludes train/test paths, requires a unique match, fails loudly with the
    candidate list otherwise (same approach the passed v1 probe used).
    """
    try:
        from huggingface_hub import HfApi
        matches = [p for p in HfApi().list_repo_files(
                       HF_DATASET_REPO, repo_type="dataset",
                       revision=HF_REVISION)
                   if name_fragment.lower() in p.lower()
                   and "test" not in p.lower() and "train" not in p.lower()]
    except ImportError as e:
        fail(11, f"huggingface_hub not installed: {e}")
    except Exception as e:
        fail(3, f"cannot list repo files (gate not accepted, no token, or "
                f"network failure): {e}")
    if len(matches) != 1:
        fail(3, f"expected exactly one repo file matching "
                f"'{name_fragment}', found {matches}")
    return matches[0]


def obtain_pinned_tables(work_dir):
    """Fetch (or reuse) the three pinned metadata tables; verify every hash.

    Reuse rule: an existing local file whose SHA-256 already equals the pin
    is used without a network touch, so phase M can re-run offline once the
    tables are cached. Any hash mismatch is invalidating (exit 4).
    """
    work_dir.mkdir(parents=True, exist_ok=True)
    tables = {}
    for name, expected_sha in TABLES_SHA256.items():
        cached = None
        for candidate in sorted(work_dir.rglob(name)):
            if sha256_file(candidate) == expected_sha:
                cached = candidate
                break
        if cached is not None:
            log(f"  {name}: using cached copy (hash verified)")
            tables[name] = cached
            continue
        path = hf_download(find_repo_file(name), work_dir)
        actual = sha256_file(path)
        if actual != expected_sha:
            fail(4, f"{name} hash {actual} != pinned {expected_sha}; the "
                    f"table drifted from the frozen revision")
        log(f"  {name}: downloaded and hash-verified")
        tables[name] = path
    return tables


def volume_repo_path(volume_name):
    """Repo path for a validation volume (v1-verified layout)."""
    patient, scan, _ = parse_volume_name(volume_name)
    return (f"dataset/valid/valid_{patient}/valid_{patient}_{scan}/"
            f"{volume_name}")


def clone_released_code():
    """Clone the released CT-CLIP code and pin it to the contract commit."""
    import subprocess
    ctclip_dir = PROBE_DIR / "vendor" / "CT-CLIP"
    if not ctclip_dir.exists():
        ctclip_dir.parent.mkdir(exist_ok=True)
        # Full clone (not depth-1): the pinned commit must be reachable even
        # if the upstream default branch has moved past it.
        r = subprocess.run(["git", "clone", CTCLIP_GIT_URL, str(ctclip_dir)],
                           capture_output=True, text=True)
        if r.returncode != 0:
            fail(3, f"git clone of released code failed: {r.stderr}")
    r = subprocess.run(["git", "-C", str(ctclip_dir), "checkout",
                        CODE_COMMIT], capture_output=True, text=True)
    if r.returncode != 0:
        fail(3, f"cannot checkout pinned commit {CODE_COMMIT}: {r.stderr}")
    head = subprocess.run(["git", "-C", str(ctclip_dir), "rev-parse", "HEAD"],
                          capture_output=True, text=True).stdout.strip()
    if head != CODE_COMMIT:
        fail(4, f"released code HEAD {head} != pinned {CODE_COMMIT}")
    dirty = subprocess.run(["git", "-C", str(ctclip_dir), "status",
                            "--porcelain"],
                           capture_output=True, text=True).stdout.strip()
    if dirty:
        # The released code must run UNMODIFIED; a dirty clone invalidates
        # the compatibility claim.
        fail(5, f"released-code clone has local modifications:\n{dirty}")
    log(f"  released code pinned at commit {head}")
    # The released packages live one directory below their project roots.
    for project in (ctclip_dir / "transformer_maskgit", ctclip_dir / "CT_CLIP"):
        if not (project / "setup.py").is_file():
            fail(11, f"released package root missing setup.py: {project}")
        sys.path.insert(0, str(project))
    sys.path.insert(0, str(ctclip_dir / "scripts"))
    return ctclip_dir


def strip_position_id_buffer_keys(state):
    """Remove *.embeddings.position_ids keys from a state dict, in place.

    Returns the sorted removed-key list. The CALLER enforces the r6 contract
    semantics: EXACTLY ONE removed key is tolerable; zero or several mean the
    checkpoint is not the understood <=4.30-era artifact -> exit 5.
    """
    removed = sorted(k for k in state if POSITION_ID_BUFFER_PATTERN.match(k))
    for key in removed:
        del state[key]
    return removed


def load_released_model(checkpoint_path, provenance, out_dir):
    """Load the frozen checkpoint under the released code, r6-tolerantly.

    Mirrors the released scripts/ct_lipro_inference.py construction exactly;
    any deviation needed to make this work is, by contract, an invalidating
    failure -- fix the DRIVER to match the released code, never the reverse.
    Returns (model, tokenizer, device).
    """
    import torch
    device = torch.device("cuda")
    try:
        from transformer_maskgit import CTViT
        from ct_clip import CTCLIP
        from ct_lipro_inference import ImageLatentsClassifier
        from transformers import BertTokenizer, BertModel

        try:
            tokenizer = BertTokenizer.from_pretrained(TOKENIZER_NAME,
                                                      do_lower_case=True)
            text_encoder = BertModel.from_pretrained(TOKENIZER_NAME)
        except Exception as e:
            fail(3, f"tokenizer/text-encoder access failed: {e!r}")
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
        # weights_only=False matches the released loader's historical
        # full-checkpoint behavior explicitly (PyTorch 2.6 default change).
        state = torch.load(str(checkpoint_path), map_location="cpu",
                           weights_only=False)
        removed_keys = strip_position_id_buffer_keys(state)
        if len(removed_keys) != 1:
            fail(5, f"expected exactly one *.embeddings.position_ids buffer "
                    f"key, found {len(removed_keys)}: {removed_keys}; the "
                    f"checkpoint is not the understood <=4.30-era artifact")
        log(f"  r6 enumerated buffer strip: removed {removed_keys[0]!r}")
        provenance["state_dict_keys_removed_before_load"] = {
            "pattern": POSITION_ID_BUFFER_PATTERN.pattern,
            "removed_keys": removed_keys,
            "reason": ("transformers 4.31.0 made BERT "
                       "embeddings.position_ids a non-persistent buffer; the "
                       "<=4.30-era checkpoint carries it (r6 ledger, "
                       "2026-08-12)"),
        }
        write_json(out_dir / "provenance.json", provenance)
        # strict=True: any OTHER unexpected or missing key must fail here.
        model.load_state_dict(state, strict=True)
        model = model.cuda().eval()
    except SystemExit:
        raise
    except (ImportError, ModuleNotFoundError) as e:
        fail(11, f"released model dependency/import missing: {e!r}")
    except Exception as e:
        fail(5, f"released checkpoint/code failed to load unchanged: {e!r}")
    log("  checkpoint loaded: strict modulo the one enumerated, "
        "provenance-logged position_ids buffer key (r6)")
    return model, tokenizer, device


def build_inference_dataset(staging_root, tables):
    """Released preprocessing via the released dataset class.

    staging_root must contain ONLY the volumes to score, laid out as
    <staging_root>/valid_P/valid_P_S/<name>.nii.gz. Returns (dataset,
    name -> index map).
    """
    try:
        from data_inference_nii import CTReportDatasetinfer
        dataset = CTReportDatasetinfer(
            data_folder=str(staging_root),
            reports_file=str(tables["validation_reports.csv"]),
            meta_file=str(tables["validation_metadata.csv"]),
            labels=str(tables["valid_predicted_labels.csv"]))
        index_by_name = {}
        for idx in range(len(dataset)):
            _video, _text, _onehot, acc = dataset[idx]
            index_by_name[str(acc)] = idx
    except SystemExit:
        raise
    except (ImportError, ModuleNotFoundError) as e:
        fail(11, f"released preprocessing import missing: {e!r}")
    except Exception as e:
        fail(9, f"released preprocessing failed on staged volumes: {e!r}")
    return dataset, index_by_name


def dataset_index_for(index_by_name, volume_name):
    """Map a VolumeName to its released-dataset item, uniquely."""
    stem = volume_name.replace(".nii.gz", "")
    matches = [k for k in index_by_name if stem in k]
    if len(matches) != 1:
        fail(9, f"staged volume {volume_name} not found uniquely in released "
                f"dataset items: {sorted(index_by_name)}")
    return index_by_name[matches[0]]


def stage_volume(local_path, staging_root, volume_name):
    """Hard-link one downloaded volume into the released dataset layout."""
    patient, scan, _ = parse_volume_name(volume_name)
    dest = staging_root / f"valid_{patient}" / f"valid_{patient}_{scan}"
    dest.mkdir(parents=True, exist_ok=True)
    link = dest / volume_name
    if not link.exists():
        os.link(local_path, link)
    return link


def make_scorer(model, tokenizer, device):
    """Return score(dataset, idx) -> ([18 float64 probabilities], metrics).

    Empty-string text tokens, exactly as the released inference does; batch
    size 1 always (contract configuration).
    """
    import torch
    text_tokens = tokenizer([""], return_tensors="pt", padding="max_length",
                            truncation=True, max_length=512).to("cuda")

    def score(dataset, idx):
        video, _text, _onehot, _acc = dataset[idx]
        video = video.unsqueeze(0).cuda()   # batch size 1, per contract
        torch.cuda.reset_peak_memory_stats()
        start = time.monotonic()
        with torch.no_grad():
            # Released ImageLatentsClassifier call signature: False asks for
            # classifier logits rather than the 512-dim latents.
            logits = model(False, text_tokens, video, device=device)
        scores = torch.sigmoid(logits).flatten().double().cpu().tolist()
        return scores, {
            "seconds": time.monotonic() - start,
            "peak_gpu_memory_gb": torch.cuda.max_memory_allocated() / 1e9,
        }

    return score


# ---------------------------------------------------------------------------
# PHASE M -- METADATA-ONLY MANIFEST FREEZE. This is everything the phase-1
# approval authorizes: fetch and hash-verify the three pinned tables,
# regenerate the frozen 425-pair manifest, hard-gate the per-stratum counts
# (237/126/58/4, exactly), record the manifest SHA-256 and unique-volume
# count, and always write selection_audit.json. NO image download, NO
# inference, NO score of any kind is produced here.
# ---------------------------------------------------------------------------

def run_phase_m(out_dir, gate_info):
    log("PHASE M: metadata-only manifest freeze")
    capture_environment(out_dir, "M", need_gpu=False)
    write_resolved_config(out_dir, "M")
    manifest_dir = out_dir / "manifest"
    manifest_dir.mkdir(parents=True, exist_ok=True)

    work_dir = PROBE_DIR / "work"
    tables = obtain_pinned_tables(work_dir)
    provenance = {
        "phase": "M",
        "timestamp_utc": utc_now(),
        "contract_blob": gate_info["contract_blob"],
        "approval_marker_blob": gate_info["marker_blob"],
        "hf_dataset_repo": HF_DATASET_REPO,
        "hf_revision": HF_REVISION,
        "tables_sha256_verified": TABLES_SHA256,
        "no_image_download": True,
        "no_inference": True,
    }
    write_json(out_dir / "provenance.json", provenance)

    # Head-order check is metadata-only and cheap; doing it now means a
    # released-schema drift is caught before anyone asks for phase-2 approval.
    with open(tables["valid_predicted_labels.csv"], newline="") as f:
        label_columns = next(csv.reader(f))[1:]
    if label_columns != EXPECTED_PATHOLOGIES:
        fail(6, f"released label column order {label_columns} does not match "
                f"the expected 18-head mapping")
    log("  head-name/order mapping confirmed against released labels CSV")

    with open(tables["validation_metadata.csv"], newline="") as f:
        rows = list(csv.DictReader(f))
    pairs, audit = build_pair_manifest(
        rows, FROZEN_STRATUM_COUNTS,
        (ANCHOR_VOLUME_A, ANCHOR_VOLUME_B))
    # The audit is ALWAYS written (contract R6), before any gate can exit.
    write_json(manifest_dir / "selection_audit.json", audit)
    log(f"  selected per-stratum counts: {audit['selected_counts']}")

    # HARD GATE (contract R1): per-stratum counts must equal the frozen
    # counts exactly; any mismatch is an invalidating failure with the
    # mandatory selection audit already on disk.
    if not audit["counts_match"]:
        report_selection_shortfall(audit, FROZEN_STRATUM_COUNTS,
                                   manifest_dir / "selection_audit.json")
        fail(7, f"phase-M stratum counts {audit['selected_counts']} differ "
                f"from the frozen {FROZEN_STRATUM_COUNTS}; release contents "
                f"or matching logic drifted -- see selection_audit.json")
    if len(pairs) != TOTAL_PAIRS:
        fail(7, f"manifest has {len(pairs)} pairs, expected {TOTAL_PAIRS}")

    # The anchor pair must be present and flagged (contract
    # frozen_scope.anchor_pair_exclusion); its absence contradicts the
    # contract's premise and stops the study.
    anchor_pairs = [p for p in pairs if p["anchor_excluded"] == "true"]
    if len(anchor_pairs) != 1 or anchor_pairs[0]["stratum"] != "Br40f|Br60f":
        fail(7, f"expected exactly one anchor pair in Br40f|Br60f, found "
                f"{[(p['pair_id'], p['stratum']) for p in anchor_pairs]}")
    log(f"  anchor pair {anchor_pairs[0]['pair_id']} "
        f"({ANCHOR_VOLUME_A} | {ANCHOR_VOLUME_B}) flagged anchor_excluded")

    # Determinism self-check: serializing twice must be byte-identical.
    manifest_bytes = manifest_csv_bytes(pairs)
    if manifest_csv_bytes(pairs) != manifest_bytes:
        fail(12, "manifest serialization is not deterministic; harness fault")
    manifest_path = manifest_dir / "pair_manifest.csv"
    manifest_path.write_bytes(manifest_bytes)
    manifest_sha = sha256_bytes(manifest_bytes)
    unique_volumes = audit["unique_volume_count"]
    log(f"  pair_manifest.csv written: {len(pairs)} pairs, "
        f"{unique_volumes} unique volumes, sha256 {manifest_sha}")

    # If the contract has already been amended (phase M re-run), the
    # regenerated manifest must match the recorded hash byte for byte.
    recorded = gate_info.get("recorded_manifest_sha256")
    if recorded is not None and recorded != manifest_sha:
        fail(7, f"regenerated manifest sha256 {manifest_sha} != the hash "
                f"recorded in the contract ({recorded}); world drift")

    provenance["pair_manifest_sha256"] = manifest_sha
    provenance["unique_volume_count"] = unique_volumes
    write_json(out_dir / "provenance.json", provenance)

    summary = {
        "idea_id": IDEA_ID,
        "contract_version": CONTRACT_VERSION,
        "phase": "M",
        "mode": "real",
        "phase_m_complete": True,
        "contract_satisfied": False,   # only the full phase-B study can be
        "stratum_counts": audit["selected_counts"],
        "frozen_counts_reproduced_exactly": True,
        "pair_count": len(pairs),
        "pair_manifest_sha256": manifest_sha,
        "unique_volume_count": unique_volumes,
        "qa_retry_allowance_volumes":
            math.ceil(QA_RETRY_FRACTION * unique_volumes),
        "anchor_pair_id": anchor_pairs[0]["pair_id"],
        "no_image_download": True,
        "no_inference": True,
        "next_step": (
            f"Operator: record pair_manifest_sha256={manifest_sha} and "
            f"unique_volume_count={unique_volumes} in "
            f"ideas/004/probe_contract.yaml (replacing every "
            f"{PLACEHOLDER} placeholder), commit that one amendment, and "
            f"re-run approve-probe against the amended blob. Only then can "
            f"phase B start; this driver refuses it until both hold."),
        "interpretation": (
            "PHASE M ONLY. This run downloaded at most the three pinned "
            "metadata tables, reproduced the frozen Stage-0 pair list "
            "exactly (237/126/58/4 per stratum -- the first clause of the "
            "contract's positive_pattern), and froze it by hash. No image "
            "was downloaded, no inference ran, and no score of any kind "
            "exists, so nothing scientific can be read from this phase. "
            "Bulk execution (phase B) remains blocked until the contract is "
            "amended with the two recorded values and freshly approved."),
    }
    write_json(out_dir / "summary.json", summary)
    print()
    print(json.dumps(summary, indent=2, sort_keys=True))
    print()
    print("Plain-English read: the frozen 425-pair manifest was reproduced")
    print("exactly and is now hash-frozen. Record the two values above in")
    print("the contract, commit, and re-run approve-probe to unlock phase B.")
    return 0


# ---------------------------------------------------------------------------
# PHASE B -- BULK STUDY. One invocation of `run.py --phase B` is one SESSION
# (contract R7/R8): it re-verifies every provenance pin, runs the anchor
# drift-detector first, then executes whole chunks (download -> hash ->
# preprocess -> infer -> delete, both pair members always in this same
# session), and when all 17 chunks are complete runs the frozen two-tier
# analysis. Interrupted chunks are detected on the next session and redone in
# full. Session count, distinct-volume downloads, and QA/retry downloads are
# capped; reaching a cap stops the run as budget exhaustion, never as a
# scientific result.
# ---------------------------------------------------------------------------

CHUNK_PER_SAMPLE_COLUMNS = [
    "session_id", "chunk", "execution", "pair_id", "role", "volume_name",
    "stratum", "head_index", "head_name", "score", "score_hex",
]
CHUNK_MANIFEST_COLUMNS = [
    "chunk", "pair_id", "role", "volume_name", "sha256", "size_bytes",
    "session_id", "downloaded_utc",
]
ANCHOR_LOG_COLUMNS = [
    "session_id", "timestamp_utc", "execution", "volume_name", "cached",
    "within_session_bit_identical", "max_abs_dev_vs_v1", "tolerance",
    "in_tolerance", "scores_hex",
]
ACCOUNTING_COLUMNS = [
    "timestamp_utc", "session_id", "context", "volume_name", "sha256",
    "size_bytes", "category",
]


def read_csv_rows(path):
    if not Path(path).exists():
        return []
    with open(path, newline="") as f:
        return list(csv.DictReader(f))


def append_csv_rows(path, rows, fieldnames):
    """Append rows, writing the header only when the file is new."""
    path.parent.mkdir(parents=True, exist_ok=True)
    new_file = not path.exists()
    with open(path, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if new_file:
            writer.writeheader()
        writer.writerows(rows)


def chunk_plan(pairs, chunk_size):
    """Deterministic chunk assignment in manifest order (contract R7)."""
    count = math.ceil(len(pairs) / chunk_size)
    return [(i + 1, pairs[i * chunk_size:(i + 1) * chunk_size])
            for i in range(count)]


def chunk_dir_for(out_dir, chunk_no):
    return out_dir / "chunks" / f"chunk_{chunk_no:02d}"


def chunk_is_complete(chunk_dir):
    """A chunk counts as complete only when environment.json -- written LAST
    -- says so and its sibling artifacts exist. Anything else is an
    interrupted chunk and is redone in full (contract chunk_atomicity)."""
    env_path = chunk_dir / "environment.json"
    if not env_path.exists():
        return False
    try:
        env = json.loads(env_path.read_text())
    except json.JSONDecodeError:
        return False
    return (env.get("chunk_complete") is True
            and (chunk_dir / "chunk_manifest.csv").exists()
            and (chunk_dir / "per_sample.csv").exists())


def spot_check_pair_ids(pairs):
    """The preregistered spot-check subset: the FIRST pair of each stratum in
    manifest order (contract determinism.spot_check_subset)."""
    first = {}
    for pair in pairs:
        if pair["stratum"] not in first:
            first[pair["stratum"]] = pair["pair_id"]
    return set(first.values())


class DownloadLedger:
    """Persistent download accounting against the R8 volume caps.

    Categories:
      scientific_first_time -- first chunk-context download of a distinct
          manifest volume; capped by unique_volume_cap.
      scientific_shared_reuse -- the same manifest volume downloaded again by
          a DIFFERENT chunk (volumes shared across strata); reported, not
          capped (it is neither a distinct volume nor a QA retry).
      qa_retry -- chunk-redo downloads and anchor (re)downloads; capped by
          ceil(0.20 x unique_volume_cap) (contract qa_retry_download_allowance).
    Reaching either cap stops the run as budget exhaustion (exit 9).
    """

    def __init__(self, path, unique_volume_cap):
        self.path = path
        self.unique_cap = unique_volume_cap
        self.qa_cap = math.ceil(QA_RETRY_FRACTION * unique_volume_cap)
        rows = read_csv_rows(path)
        self.first_time_volumes = {
            r["volume_name"] for r in rows
            if r["category"] == "scientific_first_time"}
        self.chunk_seen_volumes = {
            r["volume_name"] for r in rows
            if r["context"].startswith("chunk")}
        self.qa_count = sum(1 for r in rows if r["category"] == "qa_retry")

    def categorize(self, context, volume_name, redo):
        if context == "anchor" or redo:
            return "qa_retry"
        if volume_name in self.chunk_seen_volumes:
            return "scientific_shared_reuse"
        return "scientific_first_time"

    def check_budget_before(self, category):
        """Refuse BEFORE the download that would cross a cap (contract R8:
        continuing past a cap is invalidating)."""
        if (category == "scientific_first_time"
                and len(self.first_time_volumes) + 1 > self.unique_cap):
            fail(9, f"unique-volume cap {self.unique_cap} would be exceeded; "
                    f"stopping as budget exhaustion (not a scientific result)")
        if category == "qa_retry" and self.qa_count + 1 > self.qa_cap:
            fail(9, f"QA/retry download allowance {self.qa_cap} would be "
                    f"exceeded; stopping as budget exhaustion "
                    f"(not a scientific result)")

    def record(self, session_id, context, volume_name, sha256, size_bytes,
               category):
        if category == "scientific_first_time":
            self.first_time_volumes.add(volume_name)
        if context.startswith("chunk"):
            self.chunk_seen_volumes.add(volume_name)
        if category == "qa_retry":
            self.qa_count += 1
        append_csv_rows(self.path, [{
            "timestamp_utc": utc_now(), "session_id": session_id,
            "context": context, "volume_name": volume_name,
            "sha256": sha256, "size_bytes": size_bytes,
            "category": category,
        }], ACCOUNTING_COLUMNS)

    def totals(self):
        return {
            "scientific_first_time": len(self.first_time_volumes),
            "unique_volume_cap": self.unique_cap,
            "qa_retry": self.qa_count,
            "qa_retry_allowance": self.qa_cap,
        }


def run_anchor_protocol(out_dir, work_dir, session_id, tables, scorer,
                        reference, ledger):
    """The per-session anchor drift detector (contract execution_model.anchor).

    Runs A, B, A-again on the v1 load-probe pair BEFORE any chunk work.
    Within-session: the A repeat must be bit-identical (exit 8). Cross-
    session: per-head probabilities of A and B must sit within 1.0e-4 of the
    pinned v1 reference (exit 13). All anchor executions are excluded from
    every scientific statistic and logged to anchor_log.csv.
    """
    log("anchor protocol: session drift detector (A, B, A-repeat)")
    cache_dir = out_dir.parent / "anchor_cache_004"
    cache_dir.mkdir(parents=True, exist_ok=True)
    local = {}
    cached_flags = {}
    for name in (ANCHOR_VOLUME_A, ANCHOR_VOLUME_B):
        expected_sha = ANCHOR_INPUT_SHA256[name]
        cache_path = cache_dir / name
        # SHA-256 verified before EVERY use, cached or fresh (contract).
        if cache_path.exists() and sha256_file(cache_path) == expected_sha:
            cached_flags[name] = True
        else:
            ledger.check_budget_before("qa_retry")
            downloaded = hf_download(volume_repo_path(name),
                                     work_dir / "anchor_dl")
            actual = sha256_file(downloaded)
            if actual != expected_sha:
                fail(4, f"anchor volume {name} hash {actual} != pinned "
                        f"{expected_sha}")
            shutil.copyfile(downloaded, cache_path)
            ledger.record(session_id, "anchor", name, actual,
                          cache_path.stat().st_size, "qa_retry")
            cached_flags[name] = False
        local[name] = cache_path
        log(f"  anchor {name}: "
            f"{'cache hit' if cached_flags[name] else 'downloaded'}, "
            f"hash verified")

    staging = work_dir / "anchor_stage"
    if staging.exists():
        shutil.rmtree(staging)
    staging.mkdir(parents=True)
    for name in (ANCHOR_VOLUME_A, ANCHOR_VOLUME_B):
        stage_volume(local[name], staging, name)
    dataset, index_by_name = build_inference_dataset(staging, tables)
    idx_a = dataset_index_for(index_by_name, ANCHOR_VOLUME_A)
    idx_b = dataset_index_for(index_by_name, ANCHOR_VOLUME_B)

    executions = []
    for exec_id, idx, name in [("anchor_A", idx_a, ANCHOR_VOLUME_A),
                               ("anchor_B", idx_b, ANCHOR_VOLUME_B),
                               ("anchor_A_repeat", idx_a, ANCHOR_VOLUME_A)]:
        scores, _metrics = scorer(dataset, idx)
        check_18_finite(scores, exec_id)
        executions.append((exec_id, name, scores))
        log(f"  {exec_id}: 18 finite scores")

    a_first = executions[0][2]
    a_repeat = executions[2][2]
    bit_identical = scores_hex(a_first) == scores_hex(a_repeat)
    dev_a = max_abs_deviation(a_first, reference["exec1_A"])
    dev_b = max_abs_deviation(executions[1][2], reference["exec2_B"])

    rows = []
    for exec_id, name, scores in executions:
        dev = {"anchor_A": dev_a, "anchor_B": dev_b}.get(exec_id, "")
        rows.append({
            "session_id": session_id,
            "timestamp_utc": utc_now(),
            "execution": exec_id,
            "volume_name": name,
            "cached": str(cached_flags[name]).lower(),
            "within_session_bit_identical":
                str(bit_identical).lower() if exec_id == "anchor_A_repeat"
                else "",
            "max_abs_dev_vs_v1": repr(dev) if dev != "" else "",
            "tolerance": repr(ANCHOR_CROSS_SESSION_TOLERANCE),
            "in_tolerance":
                str(bool(dev <= ANCHOR_CROSS_SESSION_TOLERANCE)).lower()
                if dev != "" else "",
            "scores_hex": "|".join(scores_hex(scores)),
        })
    append_csv_rows(out_dir / "anchor" / "anchor_log.csv", rows,
                    ANCHOR_LOG_COLUMNS)
    shutil.rmtree(staging)

    if not bit_identical:
        fail(8, "anchor A-repeat was NOT bit-identical within this session; "
                "invalidating determinism failure")
    if dev_a > ANCHOR_CROSS_SESSION_TOLERANCE or \
            dev_b > ANCHOR_CROSS_SESSION_TOLERANCE:
        fail(13, f"anchor cross-session drift beyond the preregistered "
                 f"{ANCHOR_CROSS_SESSION_TOLERANCE} tolerance "
                 f"(dev_A={dev_a!r}, dev_B={dev_b!r}); this session's chunks "
                 f"do not count and are redone after diagnosis")
    log(f"  anchor in tolerance (dev_A={dev_a:.2e}, dev_B={dev_b:.2e}, "
        f"tol={ANCHOR_CROSS_SESSION_TOLERANCE}); A-repeat bit-identical")


def run_chunk(out_dir, work_dir, session_id, chunk_no, chunk_pairs, tables,
              scorer, ledger, spot_ids, metadata_by_volume, env_info):
    """Execute one whole chunk in this session (contract R7 chunk_atomicity).

    download -> hash-record (persisted BEFORE inference) -> preprocess ->
    infer both members of every pair -> spot-check re-runs -> delete image
    files -> environment.json written LAST as the completion marker.
    """
    chunk_dir = chunk_dir_for(out_dir, chunk_no)
    redo = chunk_dir.exists() and any(chunk_dir.iterdir())
    if redo:
        log(f"chunk {chunk_no:02d}: interrupted remains found; redoing IN "
            f"FULL (contract chunk_atomicity)")
        shutil.rmtree(chunk_dir)
    chunk_dir.mkdir(parents=True, exist_ok=True)
    chunk_start = time.monotonic()
    log(f"chunk {chunk_no:02d}: {len(chunk_pairs)} pairs "
        f"({chunk_pairs[0]['pair_id']}..{chunk_pairs[-1]['pair_id']})"
        f"{' [redo]' if redo else ''}")

    dl_dir = work_dir / f"chunk_{chunk_no:02d}_dl"
    staging = work_dir / f"chunk_{chunk_no:02d}_stage"
    for d in (dl_dir, staging):
        if d.exists():
            shutil.rmtree(d)
        d.mkdir(parents=True)

    # -- download and hash EVERY input, then persist chunk_manifest.csv
    #    BEFORE any inference (contract: inference on a volume before its
    #    hash is recorded is invalidating).
    manifest_rows = []
    local_paths = {}
    n_done = 0
    for pair in chunk_pairs:
        for role in ("softer", "sharper"):
            name = pair[f"volume_name_{role}"]
            assert_validation_only(name)
            category = ledger.categorize(f"chunk_{chunk_no:02d}", name, redo)
            ledger.check_budget_before(category)
            path = hf_download(volume_repo_path(name), dl_dir)
            sha = sha256_file(path)
            size = path.stat().st_size
            ledger.record(session_id, f"chunk_{chunk_no:02d}", name, sha,
                          size, category)
            local_paths[name] = path
            manifest_rows.append({
                "chunk": f"chunk_{chunk_no:02d}", "pair_id": pair["pair_id"],
                "role": role, "volume_name": name, "sha256": sha,
                "size_bytes": size, "session_id": session_id,
                "downloaded_utc": utc_now(),
            })
            n_done += 1
            log(f"  [{n_done}/{2 * len(chunk_pairs)}] downloaded+hashed "
                f"{name} ({size / 1e6:.0f} MB, {category})")
    write_csv(chunk_dir / "chunk_manifest.csv", manifest_rows,
              CHUNK_MANIFEST_COLUMNS)
    log(f"  chunk_manifest.csv persisted ({len(manifest_rows)} volumes) "
        f"BEFORE inference")

    # -- released preprocessing over exactly this chunk's volumes.
    for name, path in local_paths.items():
        stage_volume(path, staging, name)
    dataset, index_by_name = build_inference_dataset(staging, tables)

    # -- inference: both members of every pair, in manifest order, batch 1.
    sample_rows = []
    first_run_hex = {}   # (pair_id, role) -> score_hex list
    inference_seconds = 0.0
    peak_gb = 0.0
    try:
        for i, pair in enumerate(chunk_pairs, start=1):
            for role in ("softer", "sharper"):
                name = pair[f"volume_name_{role}"]
                exec_id = f"{pair['pair_id']}_{role}"
                idx = dataset_index_for(index_by_name, name)
                scores, metrics = scorer(dataset, idx)
                check_18_finite(scores, exec_id)
                inference_seconds += metrics["seconds"]
                peak_gb = max(peak_gb, metrics["peak_gpu_memory_gb"])
                hexes = scores_hex(scores)
                first_run_hex[(pair["pair_id"], role)] = hexes
                for h in range(18):
                    sample_rows.append({
                        "session_id": session_id,
                        "chunk": f"chunk_{chunk_no:02d}",
                        "execution": exec_id,
                        "pair_id": pair["pair_id"],
                        "role": role,
                        "volume_name": name,
                        "stratum": pair["stratum"],
                        "head_index": h,
                        "head_name": EXPECTED_PATHOLOGIES[h],
                        "score": repr(float(scores[h])),
                        "score_hex": hexes[h],
                    })
            log(f"  [{i}/{len(chunk_pairs)}] scored pair "
                f"{pair['pair_id']} ({pair['stratum']})")

        # -- preregistered within-session spot-check re-runs (contract R9):
        #    first pair of each stratum; both members; bit-identical or
        #    invalidating. Re-run rows are excluded from scientific stats.
        for pair in chunk_pairs:
            if pair["pair_id"] not in spot_ids:
                continue
            log(f"  spot-check re-run for {pair['pair_id']} "
                f"(preregistered subset)")
            for role in ("softer", "sharper"):
                name = pair[f"volume_name_{role}"]
                exec_id = f"{pair['pair_id']}_{role}_spotcheck"
                idx = dataset_index_for(index_by_name, name)
                scores, _metrics = scorer(dataset, idx)
                check_18_finite(scores, exec_id)
                hexes = scores_hex(scores)
                if hexes != first_run_hex[(pair["pair_id"], role)]:
                    fail(8, f"spot-check re-run {exec_id} NOT bit-identical "
                            f"to its first run in this session; invalidating "
                            f"determinism failure")
                for h in range(18):
                    sample_rows.append({
                        "session_id": session_id,
                        "chunk": f"chunk_{chunk_no:02d}",
                        "execution": exec_id,
                        "pair_id": pair["pair_id"],
                        "role": role,
                        "volume_name": name,
                        "stratum": pair["stratum"],
                        "head_index": h,
                        "head_name": EXPECTED_PATHOLOGIES[h],
                        "score": repr(float(scores[h])),
                        "score_hex": hexes[h],
                    })
            log(f"  spot-check {pair['pair_id']}: bit-identical")
    except SystemExit:
        raise
    except Exception as e:
        import torch
        if isinstance(e, torch.cuda.OutOfMemoryError):
            fail(9, f"batch-size-1 inference exceeded GPU memory: {e}")
        fail(9, f"inference crashed: {e!r}")

    write_csv(chunk_dir / "per_sample.csv", sample_rows,
              CHUNK_PER_SAMPLE_COLUMNS)

    # -- delete image files (contract R7: download -> ... -> delete).
    shutil.rmtree(dl_dir)
    shutil.rmtree(staging)
    log(f"  chunk {chunk_no:02d}: image files deleted")

    # -- environment.json LAST: it is the chunk-completion marker.
    write_json(chunk_dir / "environment.json", {
        "chunk": f"chunk_{chunk_no:02d}",
        "chunk_complete": True,
        "session_id": session_id,
        "redo": redo,
        "gpu": env_info.get("gpu"),
        "cuda": env_info.get("cuda"),
        "torch": env_info.get("torch"),
        "python": env_info.get("python"),
        "transformers": env_info.get("transformers"),
        "tokenizers": env_info.get("tokenizers"),
        "numpy": env_info.get("numpy"),
        "wall_seconds": time.monotonic() - chunk_start,
        "inference_seconds": inference_seconds,
        "peak_gpu_memory_gb": peak_gb,
        "timestamp_utc": utc_now(),
    })
    log(f"  chunk {chunk_no:02d} COMPLETE "
        f"({time.monotonic() - chunk_start:.0f}s wall, "
        f"{inference_seconds:.0f}s inference, peak {peak_gb:.2f} GB)")


def collect_chunk_scores(out_dir, pairs, chunks):
    """Assemble per-pair scores from the persisted chunk artifacts.

    Uses score_hex (exact float64 round-trip). Spot-check re-run rows are
    excluded from the scientific set. Every manifest pair must have both
    members with 18 heads each; anything else means completeness detection
    failed and is a harness fault.
    """
    scores_by_pair = {}
    scientific_rows = []
    for chunk_no, _chunk_pairs in chunks:
        for row in read_csv_rows(chunk_dir_for(out_dir, chunk_no)
                                 / "per_sample.csv"):
            if row["execution"].endswith("_spotcheck"):
                continue
            scientific_rows.append(row)
            entry = scores_by_pair.setdefault(
                row["pair_id"], {"softer": [None] * 18,
                                 "sharper": [None] * 18})
            entry[row["role"]][int(row["head_index"])] = \
                float.fromhex(row["score_hex"])
    for pair in pairs:
        entry = scores_by_pair.get(pair["pair_id"])
        if entry is None:
            fail(12, f"no scores found for {pair['pair_id']} despite all "
                     f"chunks reporting complete; harness fault")
        for role in ("softer", "sharper"):
            if any(v is None for v in entry[role]):
                fail(12, f"incomplete scores for {pair['pair_id']}/{role}; "
                         f"harness fault")
    return scores_by_pair, scientific_rows


def load_released_labels(tables):
    """VolumeName -> [18 ints] from the released labels CSV (tier 2 only)."""
    labels_by_volume = {}
    with open(tables["valid_predicted_labels.csv"], newline="") as f:
        reader = csv.reader(f)
        header = next(reader)
        if header[1:] != EXPECTED_PATHOLOGIES:
            fail(6, "released label columns drifted from the 18-head mapping")
        for row in reader:
            labels_by_volume[row[0]] = [int(float(v)) for v in row[1:]]
    return labels_by_volume


def run_analysis(out_dir, pairs, chunks, tables, metadata_by_volume):
    """The frozen deterministic analysis (tier 1, then tier 2 only if tier 1
    completes). Runs only when every chunk is complete."""
    log("ANALYSIS: assembling scores from persisted chunk artifacts")
    scores_by_pair, scientific_rows = collect_chunk_scores(out_dir, pairs,
                                                           chunks)
    scores_dir = out_dir / "scores"
    analysis_dir = out_dir / "analysis"
    write_csv(scores_dir / "per_sample.csv", scientific_rows,
              CHUNK_PER_SAMPLE_COLUMNS)
    log(f"  scores/per_sample.csv: {len(scientific_rows)} scientific rows")

    # input_manifest.csv (contract R6/R10): per selected volume, the
    # normalized kernel AND the raw field it came from, plus hashes.
    input_rows = []
    for chunk_no, _chunk_pairs in chunks:
        for row in read_csv_rows(chunk_dir_for(out_dir, chunk_no)
                                 / "chunk_manifest.csv"):
            meta = metadata_by_volume.get(row["volume_name"], {})
            raw_kernel = meta.get(KERNEL_COLUMN, "")
            input_rows.append({
                "volume_name": row["volume_name"],
                "pair_id": row["pair_id"],
                "role": row["role"],
                "kernel_normalized": normalize_kernel(raw_kernel),
                "kernel_raw": raw_kernel,
                "sha256": row["sha256"],
                "size_bytes": row["size_bytes"],
                "chunk": row["chunk"],
                "session_id": row["session_id"],
            })
    write_csv(scores_dir / "input_manifest.csv", input_rows,
              ["volume_name", "pair_id", "role", "kernel_normalized",
               "kernel_raw", "sha256", "size_bytes", "chunk", "session_id"])

    log("ANALYSIS tier 1: per-head x per-stratum paired differences "
        "(primary, label-free)")
    diff_rows, stat_rows, boot_rows = tier1_compute(
        pairs, scores_by_pair, BOOTSTRAP_REPLICATES, TIER1_BOOTSTRAP_SEED,
        CONFIRMATORY_STRATA, EXPLORATORY_STRATA)
    write_csv(analysis_dir / "tier1_differences.csv", diff_rows,
              ["pair_id", "patient_id", "stratum", "anchor_excluded",
               "exploratory", "head_index", "head_name", "softer_prob",
               "sharper_prob", "d_prob", "d_logit", "n_clipped_members"])
    write_csv(analysis_dir / "tier1_stats.csv", stat_rows,
              ["stratum", "head_index", "head_name", "scale", "n_raw",
               "n_counted", "median_signed", "mean_signed", "q50_abs",
               "q75_abs", "q90_abs", "q95_abs", "max_abs",
               "n_clipped_members"])
    write_csv(analysis_dir / "tier1_bootstrap.csv", boot_rows,
              ["stratum", "head_index", "head_name", "scale", "statistic",
               "point", "ci95_lo", "ci95_hi", "replicates", "n_patients",
               "n_counted_pairs"])
    log(f"  tier 1 complete: {len(diff_rows)} difference rows, "
        f"{len(stat_rows)} stat cells, {len(boot_rows)} bootstrap rows "
        f"(exploratory Br40f|Br44f listed per pair only; anchor pair "
        f"excluded from all summaries)")

    log("ANALYSIS tier 2: descriptive per-head delta-AUROC "
        "(secondary; zero threshold language)")
    labels_by_volume = load_released_labels(tables)
    auroc_rows, excluded_rows = tier2_compute(
        pairs, scores_by_pair, labels_by_volume, BOOTSTRAP_REPLICATES,
        TIER2_BOOTSTRAP_SEED, SPARSE_MIN_POSITIVE, SPARSE_MIN_NEGATIVE)
    write_csv(analysis_dir / "tier2_auroc.csv", auroc_rows,
              ["stratum", "head_index", "head_name", "n_counted_pairs",
               "n_positive", "n_negative", "auroc_sharper", "auroc_softer",
               "delta_auroc", "auroc_sharper_ci95_lo",
               "auroc_sharper_ci95_hi", "auroc_softer_ci95_lo",
               "auroc_softer_ci95_hi", "delta_auroc_ci95_lo",
               "delta_auroc_ci95_hi", "replicates", "nan_replicates"])
    write_csv(analysis_dir / "tier2_excluded_cells.csv", excluded_rows,
              ["stratum", "head_index", "head_name", "n_counted_pairs",
               "n_positive", "n_negative", "reason"])
    log(f"  tier 2 complete: {len(auroc_rows)} computed cells, "
        f"{len(excluded_rows)} excluded cells (sparse-label rule; "
        f"computation-eligibility only, no interpretive semantics)")
    return {
        "tier1_difference_rows": len(diff_rows),
        "tier1_stat_cells": len(stat_rows),
        "tier1_bootstrap_rows": len(boot_rows),
        "tier2_computed_cells": len(auroc_rows),
        "tier2_excluded_cells": len(excluded_rows),
    }


def run_phase_b(out_dir, gate_info):
    log("PHASE B: bulk 425-pair floor study (session start)")
    env_info = capture_environment(out_dir, "B", need_gpu=True)
    work_dir = PROBE_DIR / "work"
    work_dir.mkdir(exist_ok=True)

    session_id = (time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
                  + "-" + os.urandom(4).hex())
    # Session cap (contract R8): sessions are counted by their anchor-log
    # entries, because the anchor protocol is mandatory at every session
    # start; a 31st session must not begin.
    prior_sessions = {r["session_id"] for r in read_csv_rows(
        out_dir / "anchor" / "anchor_log.csv")}
    if len(prior_sessions) >= SESSION_CAP:
        fail(9, f"session cap {SESSION_CAP} reached "
                f"({len(prior_sessions)} prior sessions); stopping as "
                f"budget exhaustion (not a scientific result)")
    log(f"  session {session_id} "
        f"({len(prior_sessions)} prior sessions, cap {SESSION_CAP})")

    write_resolved_config(out_dir, "B", extra={"session_id": session_id})

    # -- provenance: tables, manifest regeneration, checkpoint, code, v1 ref.
    tables = obtain_pinned_tables(work_dir)
    with open(tables["validation_metadata.csv"], newline="") as f:
        metadata_rows = list(csv.DictReader(f))
    metadata_by_volume = {r["VolumeName"]: r for r in metadata_rows}

    pairs, audit = build_pair_manifest(
        metadata_rows, FROZEN_STRATUM_COUNTS,
        (ANCHOR_VOLUME_A, ANCHOR_VOLUME_B))
    manifest_dir = out_dir / "manifest"
    manifest_dir.mkdir(parents=True, exist_ok=True)
    write_json(manifest_dir / "selection_audit.json", audit)
    if not audit["counts_match"]:
        report_selection_shortfall(audit, FROZEN_STRATUM_COUNTS,
                                   manifest_dir / "selection_audit.json")
        fail(7, f"phase-B manifest regeneration counts "
                f"{audit['selected_counts']} differ from frozen "
                f"{FROZEN_STRATUM_COUNTS}")
    manifest_bytes = manifest_csv_bytes(pairs)
    manifest_sha = sha256_bytes(manifest_bytes)
    if manifest_sha != gate_info["pair_manifest_sha256"]:
        fail(7, f"regenerated manifest sha256 {manifest_sha} != contract-"
                f"recorded {gate_info['pair_manifest_sha256']}; the analysis "
                f"population is the recorded manifest byte-for-byte, so stop")
    if audit["unique_volume_count"] != gate_info["unique_volume_count"]:
        fail(7, f"regenerated unique-volume count "
                f"{audit['unique_volume_count']} != contract-recorded "
                f"{gate_info['unique_volume_count']}")
    manifest_path = manifest_dir / "pair_manifest.csv"
    if manifest_path.exists() and \
            manifest_path.read_bytes() != manifest_bytes:
        fail(7, "on-disk pair_manifest.csv differs from the regenerated "
                "frozen manifest; refusing to proceed over a divergent copy")
    manifest_path.write_bytes(manifest_bytes)
    log(f"  manifest verified against contract hash "
        f"({manifest_sha[:12]}..., {len(pairs)} pairs, "
        f"{audit['unique_volume_count']} unique volumes)")

    chunks = chunk_plan(pairs, CHUNK_SIZE_PAIRS)
    if len(chunks) != CHUNK_COUNT or len(pairs) != TOTAL_PAIRS:
        fail(12, f"chunk plan {len(chunks)} x {CHUNK_SIZE_PAIRS} does not "
                 f"cover {len(pairs)} pairs as 17 x 25; harness fault")
    spot_ids = spot_check_pair_ids(pairs)
    log(f"  preregistered spot-check pairs: {sorted(spot_ids)}")

    checkpoint_path = hf_download(CHECKPOINT_REPO_PATH, work_dir)
    checkpoint_sha = sha256_file(checkpoint_path)
    if checkpoint_sha != CHECKPOINT_SHA256:
        fail(4, f"checkpoint hash {checkpoint_sha} != pinned "
                f"{CHECKPOINT_SHA256}")
    log("  checkpoint hash verified against the v1-frozen pin")
    clone_released_code()
    reference = load_v1_reference()
    log("  v1 anchor reference loaded (git blob verified)")

    provenance = {
        "phase": "B",
        "session_id": session_id,
        "timestamp_utc": utc_now(),
        "contract_blob": gate_info["contract_blob"],
        "approval_marker_blob": gate_info["marker_blob"],
        "hf_dataset_repo": HF_DATASET_REPO,
        "hf_revision": HF_REVISION,
        "tables_sha256_verified": TABLES_SHA256,
        "checkpoint": {"repo_path": CHECKPOINT_REPO_PATH,
                       "sha256": checkpoint_sha,
                       "attribution_note": (
                           "attribution limited to 'released v2 ClassFine "
                           "checkpoint' until paper-number correspondence "
                           "is checked (2026-08-11 pin 4)")},
        "code_commit": CODE_COMMIT,
        "pair_manifest_sha256": manifest_sha,
        "v1_anchor_reference_blob": V1_REFERENCE_GIT_BLOB,
    }
    write_json(out_dir / "provenance.json", provenance)

    model, tokenizer, device = load_released_model(checkpoint_path,
                                                   provenance, out_dir)
    scorer = make_scorer(model, tokenizer, device)

    ledger = DownloadLedger(out_dir / "scores" / "download_accounting.csv",
                            gate_info["unique_volume_count"])
    # Anchor protocol FIRST, at every session start, before any chunk work
    # (contract execution_model.anchor). Its failure modes exit here.
    run_anchor_protocol(out_dir, work_dir, session_id, tables, scorer,
                        reference, ledger)

    # -- chunk loop: whole chunks only, in order, skipping completed ones.
    completed = [n for n, _ in chunks if chunk_is_complete(
        chunk_dir_for(out_dir, n))]
    log(f"  chunks already complete: {completed or 'none'}")
    for chunk_no, chunk_pairs in chunks:
        if chunk_is_complete(chunk_dir_for(out_dir, chunk_no)):
            continue
        run_chunk(out_dir, work_dir, session_id, chunk_no, chunk_pairs,
                  tables, scorer, ledger, spot_ids, metadata_by_volume,
                  env_info)

    # -- all chunks complete: frozen analysis (tier 2 only if tier 1 ran).
    analysis_counts = run_analysis(out_dir, pairs, chunks, tables,
                                   metadata_by_volume)

    summary = {
        "idea_id": IDEA_ID,
        "contract_version": CONTRACT_VERSION,
        "phase": "B",
        "mode": "real",
        "contract_satisfied": True,
        "session_id": session_id,
        "sessions_used": len(prior_sessions) + 1,
        "session_cap": SESSION_CAP,
        "pair_count": len(pairs),
        "pair_manifest_sha256": manifest_sha,
        "unique_volume_count": audit["unique_volume_count"],
        "download_accounting": ledger.totals(),
        "chunks_complete": CHUNK_COUNT,
        "spot_check_pairs": sorted(spot_ids),
        "anchor_pair_confirmatory_exclusion": (
            "Br40f|Br60f confirmatory statistics use 236 counted pairs "
            "(237 raw); the anchor pair's deltas are excluded everywhere"),
        "analysis": analysis_counts,
        "outputs": {
            "tier1": ["analysis/tier1_differences.csv",
                      "analysis/tier1_stats.csv",
                      "analysis/tier1_bootstrap.csv"],
            "tier2": ["analysis/tier2_auroc.csv",
                      "analysis/tier2_excluded_cells.csv"],
        },
        "interpretation": (
            "POSITIVE per the contract's positive_pattern: the frozen "
            "manifest was reproduced and hash-verified, every chunk "
            "completed with verified provenance, same-session pairing, "
            "bit-identical spot-checks, and in-tolerance anchors; all 425 "
            "pairs were scored and the frozen two-tier analysis ran. ANY "
            "resulting magnitude profile -- near-zero, large, or mixed "
            "across heads and strata -- is a valid descriptive outcome: the "
            "deliverable is the measured reconstruction-sensitivity "
            "baseline itself, for the released v2 ClassFine checkpoint on "
            "these CT-RATE kernel contrasts in a predominantly single-"
            "vendor (Siemens) cohort. Per the negative_pattern there is no "
            "failing magnitude: tightly-bounded-near-zero paired "
            "differences are the sensitivity-bounded descriptive null, and "
            "large paired differences are equally valid descriptively. No "
            "equivalence, robustness, accuracy, concept-validity, "
            "localization, or cross-vendor claim is made or implied; tier-2 "
            "numbers are benchmark discrimination against report-derived "
            "labels, never clinical accuracy, and carry no pass/fail "
            "semantics."),
    }
    write_json(out_dir / "summary.json", summary)
    print()
    print(json.dumps(summary, indent=2, sort_keys=True))
    print()
    print("Plain-English read: the study is complete. The per-head,")
    print("per-stratum tables under analysis/ ARE the deliverable -- a")
    print("reconstruction-sensitivity baseline for this checkpoint on these")
    print("contrasts. Interpretation belongs to the interpret stage; no")
    print("magnitude here passes or fails anything.")
    return 0


# ---------------------------------------------------------------------------
# SMOKE MODE. Synthetic, no network, no GPU, no HF gate; seconds to run. It
# exercises the harness through the SAME functions the real phases use: the
# hash-bound approval gate (against the real contract and marker), the
# phase-B entry refusals, four-stratum manifest generation with planted
# decoys, deterministic serialization, chunk planning and completeness
# detection (including a simulated interrupted chunk), spot-check and anchor
# bit-identity/tolerance logic, and the full tier-1/tier-2 analysis on mock
# scores. It can NEVER satisfy the contract -- summary.json says so -- and
# it never touches the real checkpoint, tables, or volumes.
# ---------------------------------------------------------------------------

SMOKE_STRATUM_COUNTS = {
    "Br40f|Br60f": 5,   # includes the planted anchor-named pair
    "Bl56f|Br40f": 2,
    "Bl57d|Br36d": 1,
    "Br40f|Br44f": 1,   # via a 3-reconstruction scan sharing its Br40f member
}
SMOKE_CHUNK_SIZE = 4
SMOKE_REPLICATES = 50
SMOKE_SPARSE_MIN = 2   # smoke-only harness parameter so BOTH sparse-rule
                       # branches execute; the real rule (10/10) is frozen in
                       # the constants and asserted against the contract.


def smoke_metadata_rows():
    """A tiny metadata table exercising every selection rule.

    Every decoy exists to prove a specific filter works; expectations are
    asserted in run_smoke. The anchor-named pair stores its kernels in the
    frozen release's stringified-list format (the exit-7 root cause) so both
    normalize_kernel branches run through real selection.
    """
    def row(name, kernel, zsp="1.0", slices="240"):
        return {"VolumeName": name, "ConvolutionKernel": kernel,
                "RescaleSlope": "1", "RescaleIntercept": "-1024",
                "XYSpacing": "[0.75, 0.75]", "ZSpacing": zsp,
                "NumberofSlices": slices, "KVP": "120",
                "ImagePositionPatient": "[0,0,0]"}
    return [
        # -- the planted anchor pair (list-format kernels), stratum 1
        row("valid_1004_a_1.nii.gz", "['Br40f', '3']"),
        row("valid_1004_a_2.nii.gz", "['Br60f', '3']"),
        # -- four more clean Br40f|Br60f pairs
        row("valid_10_a_1.nii.gz", "Br40f"), row("valid_10_a_2.nii.gz", "Br60f"),
        row("valid_1_a_1.nii.gz", "Br40f"), row("valid_1_a_2.nii.gz", "Br60f"),
        row("valid_2_a_1.nii.gz", "Br40f"), row("valid_2_a_2.nii.gz", "Br60f"),
        # -- a 3-reconstruction scan: yields a Br40f|Br60f pair AND a
        #    Br40f|Br44f pair sharing valid_3_a_1 (unique-volume < 2 x pairs)
        row("valid_3_a_1.nii.gz", "Br40f"), row("valid_3_a_2.nii.gz", "Br60f"),
        row("valid_3_a_3.nii.gz", "Br44f"),
        # -- two Bl56f|Br40f pairs and one Bl57d|Br36d pair
        row("valid_4_a_1.nii.gz", "Br40f"), row("valid_4_a_2.nii.gz", "Bl56f"),
        row("valid_5_a_1.nii.gz", "Br40f"), row("valid_5_a_2.nii.gz", "Bl56f"),
        row("valid_6_a_1.nii.gz", "Br36d"), row("valid_6_a_2.nii.gz", "Bl57d"),
        # -- decoy: geometry (ZSpacing) drift must fail the exact match
        row("valid_7_a_1.nii.gz", "Br40f"),
        row("valid_7_a_2.nii.gz", "Br60f", zsp="1.5"),
        # -- decoy: singleton scan (no partner)
        row("valid_8_a_1.nii.gz", "Br40f"),
        # -- decoy: duplicate contrast members (two Br40f) must be skipped
        row("valid_9_a_1.nii.gz", "Br40f"), row("valid_9_a_2.nii.gz", "Br40f"),
        row("valid_9_a_3.nii.gz", "Br60f"),
        # -- decoys: the split guard must refuse train/test rows
        row("train_9_a_1.nii.gz", "Br40f"), row("train_9_a_2.nii.gz", "Br60f"),
        row("test_9_a_1.nii.gz", "Br40f"),
    ]


def smoke_mock_scores(volume_name):
    """Deterministic mock scorer: hash(volume name + head name) -> [0, 1).

    Purely plumbing; carries no meaning. Same name -> same scores, so the
    bit-identity checks are genuinely exercised end to end.
    """
    seed_bytes = ("synthetic:" + volume_name).encode()
    scores = []
    for head in EXPECTED_PATHOLOGIES:
        digest = hashlib.sha256(seed_bytes + head.encode()).digest()
        scores.append(int.from_bytes(digest[:8], "big") / 2.0 ** 64)
    return scores


def smoke_assert(condition, what):
    if not condition:
        fail(12, f"smoke self-test failed: {what}; harness fault")


def smoke_write_chunk(out_dir, session_id, chunk_no, chunk_pairs, spot_ids,
                      complete=True):
    """Write chunk artifacts exactly the way run_chunk does, with mock
    downloads and scores. complete=False simulates an interruption after the
    chunk manifest (so completeness detection and redo can be tested)."""
    chunk_dir = chunk_dir_for(out_dir, chunk_no)
    if chunk_dir.exists():
        shutil.rmtree(chunk_dir)
    chunk_dir.mkdir(parents=True)
    manifest_rows = []
    for pair in chunk_pairs:
        for role in ("softer", "sharper"):
            name = pair[f"volume_name_{role}"]
            fake_bytes = ("synthetic-volume:" + name).encode()
            manifest_rows.append({
                "chunk": f"chunk_{chunk_no:02d}", "pair_id": pair["pair_id"],
                "role": role, "volume_name": name,
                "sha256": sha256_bytes(fake_bytes),
                "size_bytes": len(fake_bytes),
                "session_id": session_id, "downloaded_utc": utc_now(),
            })
    write_csv(chunk_dir / "chunk_manifest.csv", manifest_rows,
              CHUNK_MANIFEST_COLUMNS)
    if not complete:
        return  # simulated interruption: no per_sample, no environment.json
    sample_rows = []
    for pair in chunk_pairs:
        for role in ("softer", "sharper"):
            name = pair[f"volume_name_{role}"]
            scores = smoke_mock_scores(name)
            hexes = scores_hex(scores)
            for h in range(18):
                sample_rows.append({
                    "session_id": session_id,
                    "chunk": f"chunk_{chunk_no:02d}",
                    "execution": f"{pair['pair_id']}_{role}",
                    "pair_id": pair["pair_id"], "role": role,
                    "volume_name": name, "stratum": pair["stratum"],
                    "head_index": h, "head_name": EXPECTED_PATHOLOGIES[h],
                    "score": repr(float(scores[h])), "score_hex": hexes[h],
                })
        if pair["pair_id"] in spot_ids:
            # Spot-check logic: a deterministic re-run must be bit-identical.
            for role in ("softer", "sharper"):
                name = pair[f"volume_name_{role}"]
                rerun_hex = scores_hex(smoke_mock_scores(name))
                first_hex = scores_hex(smoke_mock_scores(name))
                smoke_assert(rerun_hex == first_hex,
                             f"spot-check re-run not bit-identical for "
                             f"{pair['pair_id']}/{role}")
    write_csv(chunk_dir / "per_sample.csv", sample_rows,
              CHUNK_PER_SAMPLE_COLUMNS)
    write_json(chunk_dir / "environment.json", {
        "chunk": f"chunk_{chunk_no:02d}", "chunk_complete": True,
        "session_id": session_id, "mock": True,
        "timestamp_utc": utc_now(),
    })


def run_smoke(out_dir, gate_info):
    log("SMOKE: synthetic harness test (cannot satisfy the contract)")
    capture_environment(out_dir, "SMOKE", need_gpu=False)
    write_resolved_config(out_dir, "SMOKE", extra={
        "smoke_overrides": {
            "stratum_counts": SMOKE_STRATUM_COUNTS,
            "chunk_size": SMOKE_CHUNK_SIZE,
            "replicates": SMOKE_REPLICATES,
            "sparse_min": SMOKE_SPARSE_MIN,
        }})
    write_json(out_dir / "provenance.json", {
        "mode": "smoke",
        "note": ("synthetic run; no external artifact was touched; the real "
                 "hash-bound approval gate DID run against the committed "
                 "contract and marker"),
        "contract_blob": gate_info["contract_blob"],
    })
    checks = {}

    # -- 1. pure-function self-tests -------------------------------------
    log("SMOKE 1: pure-function self-tests")
    # git blob function against the canonical known vector: the git blob of
    # b"hello\n" is ce013625030ba8dba906f756967f9e9ca394464a.
    smoke_assert(git_blob_sha1_bytes(b"hello\n")
                 == "ce013625030ba8dba906f756967f9e9ca394464a",
                 "git_blob_sha1_bytes known vector")
    checks["git_blob_function_known_vector"] = True
    # The gate already verified marker blob == contract blob (real files).
    checks["hash_bound_gate_verified_real_contract"] = True

    for raw, want in [
        ("['Br40f', '3']", "Br40f"),      # frozen release: stringified list
        ("  Br60f ", "Br60f"),             # plain string
        ("['Bl56f']", "Bl56f"),            # one-element list literal
        ("[not a literal", "[not a literal"),  # unparsable -> stripped raw
    ]:
        smoke_assert(normalize_kernel(raw) == want,
                     f"normalize_kernel({raw!r})")
    checks["kernel_normalization_both_formats"] = True

    observed_key = "trained_model.text_transformer.embeddings.position_ids"
    near_misses = {
        "embeddings.position_ids": 0,   # no leading component
        "trained_model.text_transformer.embeddings."
        "position_embeddings.weight": 1,   # learnable weights, not the buffer
        "a.embeddings.position_ids_extra": 2,   # suffix must be anchored
    }
    state = dict.fromkeys([observed_key, *near_misses], 0)
    smoke_assert(strip_position_id_buffer_keys(state) == [observed_key],
                 "buffer strip removes exactly the observed key")
    smoke_assert(set(state) == set(near_misses),
                 "buffer strip leaves near-miss keys untouched")
    smoke_assert(strip_position_id_buffer_keys(dict(near_misses)) == [],
                 "buffer strip matches no near-miss key")
    two = {observed_key: 0, "other.encoder.embeddings.position_ids": 1}
    smoke_assert(len(strip_position_id_buffer_keys(two)) == 2,
                 "buffer strip reports both keys in the two-key case")
    checks["r6_buffer_strip_enumerated_and_anchored"] = True

    smoke_assert(kernel_numeric_index("Br40f") == 40
                 and kernel_numeric_index("Bl57d") == 57,
                 "kernel numeric index")
    assert_sign_directions()   # numeric R2 rule == contract's explicit table
    checks["sign_directions_match_contract_table"] = True

    # Phase-B entry refusals (pure). The placeholder branch is tested on a
    # SYNTHETIC text so smoke keeps passing after the real contract is
    # amended; the real contract is then checked against whichever state it
    # is legitimately in (frozen pre-amendment, or amended).
    contract_text = CONTRACT_PATH.read_text()
    blob = gate_info["contract_blob"]
    frozen_text = f'still frozen: "{PLACEHOLDER}"\n'
    ok, reason, _, _ = phase_b_entry_check(frozen_text, "X" * 40, "X" * 40)
    smoke_assert(not ok and "placeholder" in reason,
                 "phase B refused while placeholders remain")
    checks["phase_b_refused_placeholder"] = True
    ok, reason, _, _ = phase_b_entry_check(contract_text, "0" * 40, blob)
    smoke_assert(not ok and "blob" in reason,
                 "phase B refused on a stale marker blob")
    checks["phase_b_refused_stale_marker"] = True
    ok, reason, _, _ = phase_b_entry_check(contract_text, blob, blob)
    if PLACEHOLDER in contract_text:
        smoke_assert(not ok and "placeholder" in reason,
                     "pre-amendment real contract refuses phase B")
        checks["real_contract_phase_b_state"] = "refused_pre_amendment"
    else:
        smoke_assert(ok, "amended real contract passes the entry check")
        checks["real_contract_phase_b_state"] = "amended_entry_ok"
    amended = ('pair_manifest_sha256: "' + "a" * 64 + '"\n'
               'unique_volume_count: 15\n')
    ok, _, sha, count = phase_b_entry_check(amended, "X" * 40, "X" * 40)
    smoke_assert(ok and sha == "a" * 64 and count == 15,
                 "phase B accepts a properly amended contract")
    checks["phase_b_accepts_amended"] = True

    value, clipped = logit_clipped(0.5)
    smoke_assert(value == 0.0 and not clipped, "logit at 0.5")
    value, clipped = logit_clipped(0.0)
    smoke_assert(clipped and value < -13, "logit clip at 0.0")
    checks["logit_clip_counting"] = True

    smoke_assert(max_abs_deviation([0.5] * 18,
                                   [0.5 + 5e-5] + [0.5] * 17)
                 <= ANCHOR_CROSS_SESSION_TOLERANCE,
                 "anchor tolerance passes a 5e-5 deviation")
    smoke_assert(max_abs_deviation([0.5] * 18,
                                   [0.5 + 2e-4] + [0.5] * 17)
                 > ANCHOR_CROSS_SESSION_TOLERANCE,
                 "anchor tolerance flags a 2e-4 deviation")
    checks["anchor_tolerance_logic"] = True

    # -- 2. synthetic phase M: manifest generation with planted decoys ----
    log("SMOKE 2: four-stratum manifest generation with planted decoys")
    rows = smoke_metadata_rows()
    pairs, audit = build_pair_manifest(
        rows, SMOKE_STRATUM_COUNTS, (ANCHOR_VOLUME_A, ANCHOR_VOLUME_B))
    manifest_dir = out_dir / "manifest"
    manifest_dir.mkdir(parents=True, exist_ok=True)
    write_json(manifest_dir / "selection_audit.json", audit)
    smoke_assert(audit["counts_match"],
                 f"stratum counts {audit['selected_counts']} != planted "
                 f"{SMOKE_STRATUM_COUNTS}")
    smoke_assert(audit["non_validation_refused"] == 3,
                 f"split guard refused {audit['non_validation_refused']} "
                 f"rows, expected 3 (2 train + 1 test)")
    s1 = audit["per_stratum"]["Br40f|Br60f"]
    smoke_assert(s1["candidate_pairs_failing_geometry_match"] == 1
                 and s1["geometry_mismatches_by_column"] == {"ZSpacing": 1},
                 "geometry decoy dropped for exactly ZSpacing")
    smoke_assert(s1["scans_with_duplicate_contrast_members"] == 1,
                 "duplicate-member decoy dropped")
    smoke_assert(audit["unique_volume_count"] == 17,
                 f"unique volumes {audit['unique_volume_count']} != 17 "
                 f"(one shared volume across strata)")
    checks["manifest_counts_and_decoys"] = True
    checks["unique_volume_count_not_2x_pairs"] = True

    smoke_assert(pairs[0]["pair_id"] == "p001"
                 and pairs[0]["anchor_excluded"] == "true"
                 and pairs[0]["stratum"] == "Br40f|Br60f",
                 "anchor pair flagged at p001")
    smoke_assert(all(p["anchor_excluded"] == "false" for p in pairs[1:]),
                 "exactly one anchor pair")
    checks["anchor_pair_flagged"] = True

    manifest_bytes = manifest_csv_bytes(pairs)
    smoke_assert(manifest_bytes == manifest_csv_bytes(pairs),
                 "manifest serialization deterministic")
    (manifest_dir / "pair_manifest.csv").write_bytes(manifest_bytes)
    log(f"  smoke manifest: {len(pairs)} pairs, sha256 "
        f"{sha256_bytes(manifest_bytes)[:12]}...")
    checks["manifest_deterministic_bytes"] = True

    # softer/sharper assignment sanity on the cross-family stratum: Br40f
    # (index 40) must be the softer member against Bl56f (index 56).
    p_cross = [p for p in pairs if p["stratum"] == "Bl56f|Br40f"][0]
    smoke_assert(p_cross["kernel_normalized_softer"] == "Br40f"
                 and p_cross["kernel_normalized_sharper"] == "Bl56f",
                 "cross-family softer/sharper assignment")

    # -- 3. synthetic phase B: chunks, interruption, resume, collection ---
    log("SMOKE 3: chunk cycle with a simulated interruption and redo")
    chunks = chunk_plan(pairs, SMOKE_CHUNK_SIZE)
    smoke_assert([len(c) for _, c in chunks] == [4, 4, 1],
                 "chunk plan 4+4+1 over 9 pairs")
    spot_ids = spot_check_pair_ids(pairs)
    smoke_assert(spot_ids == {"p001", "p006", "p008", "p009"},
                 f"spot-check subset {sorted(spot_ids)}")
    session1 = "smoke-session-1"
    smoke_write_chunk(out_dir, session1, 1, chunks[0][1], spot_ids)
    smoke_write_chunk(out_dir, session1, 2, chunks[1][1], spot_ids)
    smoke_write_chunk(out_dir, session1, 3, chunks[2][1], spot_ids,
                      complete=False)   # simulated interruption
    states = [chunk_is_complete(chunk_dir_for(out_dir, n)) for n, _ in chunks]
    smoke_assert(states == [True, True, False],
                 f"completeness detection saw {states}")
    checks["interrupted_chunk_detected"] = True
    # "Session 2" redoes the interrupted chunk in full.
    smoke_write_chunk(out_dir, "smoke-session-2", 3, chunks[2][1], spot_ids)
    smoke_assert(chunk_is_complete(chunk_dir_for(out_dir, 3)),
                 "redone chunk complete")
    checks["interrupted_chunk_redone_in_full"] = True
    checks["spot_check_bit_identity_logic"] = True

    scores_by_pair, scientific_rows = collect_chunk_scores(out_dir, pairs,
                                                           chunks)
    smoke_assert(len(scientific_rows) == len(pairs) * 2 * 18,
                 f"{len(scientific_rows)} scientific rows != "
                 f"{len(pairs) * 2 * 18}")
    # Round-trip exactness: collected floats equal the mock scorer's output.
    smoke_assert(scores_by_pair["p002"]["softer"]
                 == smoke_mock_scores("valid_10_a_1.nii.gz"),
                 "score_hex round-trip exactness")
    checks["chunk_score_collection_roundtrip"] = True

    # Bit-identity must FAIL for different inputs (negative control).
    smoke_assert(scores_hex(smoke_mock_scores("valid_10_a_1.nii.gz"))
                 != scores_hex(smoke_mock_scores("valid_10_a_2.nii.gz")),
                 "different volumes give different score bytes")

    # -- 4. analysis on mock scores (numpy/sklearn permitting) ------------
    analysis_status = "full"
    try:
        import numpy  # noqa: F401  (availability probe only)
    except ImportError:
        analysis_status = "skipped_no_numpy"
    if analysis_status == "full":
        log("SMOKE 4: tier-1 analysis on mock scores")
        diff_rows, stat_rows, boot_rows = tier1_compute(
            pairs, scores_by_pair, SMOKE_REPLICATES, TIER1_BOOTSTRAP_SEED,
            CONFIRMATORY_STRATA, EXPLORATORY_STRATA)
        smoke_assert(len(diff_rows) == len(pairs) * 18,
                     f"{len(diff_rows)} tier-1 difference rows")
        smoke_assert(len(stat_rows) == 3 * 18 * 2,
                     f"{len(stat_rows)} tier-1 stat cells (3 confirmatory "
                     f"strata x 18 heads x 2 scales)")
        smoke_assert(len(boot_rows) == 3 * 18 * 2 * 3,
                     f"{len(boot_rows)} tier-1 bootstrap rows")
        smoke_assert(not any(r["stratum"] == "Br40f|Br44f"
                             for r in stat_rows),
                     "no summary statistics for the exploratory stratum")
        s1_rows = [r for r in stat_rows if r["stratum"] == "Br40f|Br60f"]
        smoke_assert(all(r["n_raw"] == 5 and r["n_counted"] == 4
                         for r in s1_rows),
                     "anchor pair excluded from counted N (5 raw, 4 counted)")
        # Sign check on one concrete cell: d = sharper - softer, exactly.
        want = (smoke_mock_scores("valid_10_a_2.nii.gz")[0]
                - smoke_mock_scores("valid_10_a_1.nii.gz")[0])
        got = [float(r["d_prob"]) for r in diff_rows
               if r["pair_id"] == "p002" and r["head_index"] == 0]
        smoke_assert(got == [want], "signed difference is sharper - softer")
        smoke_assert(all(r["ci95_lo"] <= r["ci95_hi"] for r in boot_rows),
                     "bootstrap interval ordering")
        write_csv(out_dir / "analysis" / "tier1_differences.csv", diff_rows,
                  ["pair_id", "patient_id", "stratum", "anchor_excluded",
                   "exploratory", "head_index", "head_name", "softer_prob",
                   "sharper_prob", "d_prob", "d_logit", "n_clipped_members"])
        write_csv(out_dir / "analysis" / "tier1_stats.csv", stat_rows,
                  ["stratum", "head_index", "head_name", "scale", "n_raw",
                   "n_counted", "median_signed", "mean_signed", "q50_abs",
                   "q75_abs", "q90_abs", "q95_abs", "max_abs",
                   "n_clipped_members"])
        write_csv(out_dir / "analysis" / "tier1_bootstrap.csv", boot_rows,
                  ["stratum", "head_index", "head_name", "scale",
                   "statistic", "point", "ci95_lo", "ci95_hi", "replicates",
                   "n_patients", "n_counted_pairs"])
        checks["tier1_rows_and_exclusions"] = True

        try:
            import sklearn  # noqa: F401
            have_sklearn = True
        except ImportError:
            have_sklearn = False
            analysis_status = "tier2_skipped_no_sklearn"
        if have_sklearn:
            log("SMOKE 4: tier-2 analysis on mock scores and planted labels")
            # Planted labels: head 0 has 2 positive and 2 negative counted
            # stratum-1 pairs (eligible at the smoke minimum of 2); every
            # other head is all-negative (excluded). Both members of a pair
            # always carry the same row, matching the Stage-0 premise.
            labels_by_volume = {}
            for pair in pairs:
                for role in ("softer", "sharper"):
                    name = pair[f"volume_name_{role}"]
                    head0 = 1 if pair["patient_id"] in ("valid_10",
                                                        "valid_1") else 0
                    labels_by_volume[name] = [head0] + [0] * 17
            smoke_assert(label_integrity_problems(pairs, labels_by_volume)
                         == [], "planted labels pass integrity")
            doctored = dict(labels_by_volume)
            doctored["valid_10_a_2.nii.gz"] = [0] + [0] * 17
            smoke_assert(len(label_integrity_problems(pairs, doctored)) == 1,
                         "label integrity detects a planted mismatch")
            checks["label_integrity_detects_planted_mismatch"] = True

            auroc_rows, excluded_rows = tier2_compute(
                pairs, scores_by_pair, labels_by_volume, SMOKE_REPLICATES,
                TIER2_BOOTSTRAP_SEED, SMOKE_SPARSE_MIN, SMOKE_SPARSE_MIN)
            smoke_assert(len(auroc_rows) == 1
                         and auroc_rows[0]["stratum"] == "Br40f|Br60f"
                         and auroc_rows[0]["head_index"] == 0,
                         f"exactly one eligible tier-2 cell, got "
                         f"{[(r['stratum'], r['head_index']) for r in auroc_rows]}")
            smoke_assert(len(excluded_rows) == 4 * 18 - 1,
                         f"{len(excluded_rows)} excluded cells != 71")
            smoke_assert(all(r["reason"] == EXCLUDED_CELL_LABEL
                             for r in excluded_rows),
                         "excluded cells carry the mandated label")
            smoke_assert(0.0 <= auroc_rows[0]["auroc_sharper"] <= 1.0
                         and 0.0 <= auroc_rows[0]["auroc_softer"] <= 1.0,
                         "AUROC in [0, 1]")
            write_csv(out_dir / "analysis" / "tier2_auroc.csv", auroc_rows,
                      ["stratum", "head_index", "head_name",
                       "n_counted_pairs", "n_positive", "n_negative",
                       "auroc_sharper", "auroc_softer", "delta_auroc",
                       "auroc_sharper_ci95_lo", "auroc_sharper_ci95_hi",
                       "auroc_softer_ci95_lo", "auroc_softer_ci95_hi",
                       "delta_auroc_ci95_lo", "delta_auroc_ci95_hi",
                       "replicates", "nan_replicates"])
            write_csv(out_dir / "analysis" / "tier2_excluded_cells.csv",
                      excluded_rows,
                      ["stratum", "head_index", "head_name",
                       "n_counted_pairs", "n_positive", "n_negative",
                       "reason"])
            checks["tier2_sparse_rule_both_branches"] = True
    else:
        log("SMOKE 4: numpy not importable; analysis portion SKIPPED "
            "(install probes/004/requirements.txt and re-run smoke for "
            "full coverage before any real phase-B run)")

    # -- 5. summary -------------------------------------------------------
    log("SMOKE 5: summary")
    summary = {
        "idea_id": IDEA_ID,
        "contract_version": CONTRACT_VERSION,
        "phase": "SMOKE",
        "mode": "smoke",
        "contract_satisfied": False,   # a smoke run can NEVER satisfy it
        "analysis_coverage": analysis_status,
        "harness_checks": checks,
        "interpretation": (
            "SMOKE MODE ONLY. This run used synthetic metadata, mock scores, "
            "and planted decoys to verify the harness: the hash-bound "
            "approval gate (against the real committed contract and marker), "
            "the phase-B entry refusals, four-stratum manifest generation "
            "and its hard gate, deterministic serialization, chunk "
            "completeness/redo detection, spot-check and anchor "
            "bit-identity/tolerance logic, and the frozen tier-1/tier-2 "
            "analysis code. It says NOTHING about the contract's risky "
            "assumption -- whether the provenance-frozen pipeline scales to "
            "425 real pairs -- and no number produced here is evidence "
            "about reconstruction sensitivity. Only the real phase M and "
            "phase B runs, in that order and each under its own approval, "
            "can produce the contract's positive_pattern."),
    }
    write_json(out_dir / "summary.json", summary)
    print()
    print(json.dumps(summary, indent=2, sort_keys=True))
    print()
    print("Plain-English read: the harness plumbing works end to end"
          + (" (analysis included)." if analysis_status == "full" else
             f" EXCEPT: {analysis_status}."))
    print("The scientific pipeline remains untested until the real runs.")
    return 0


# ---------------------------------------------------------------------------
# ENTRY POINT.
# ---------------------------------------------------------------------------

def main():
    global _LOG_FILE
    parser = argparse.ArgumentParser(
        description="idea-004 contract-v2 driver (see module docstring)")
    parser.add_argument("--smoke", action="store_true",
                        help="synthetic harness test; no network, no GPU; "
                             "cannot satisfy the contract")
    parser.add_argument("--phase", choices=["M", "B"],
                        help="M = metadata-only manifest freeze (phase-1 "
                             "approval); B = bulk study (phase-2 approval, "
                             "mechanically gated)")
    parser.add_argument("--output-dir", type=Path,
                        help="results bundle directory (use a persistent "
                             "Drive path on Colab); defaults to results_v2/ "
                             "or outputs_smoke_v2/ beside run.py")
    args = parser.parse_args()
    if args.smoke == (args.phase is not None):
        parser.error("exactly one of --smoke or --phase {M,B} is required")

    if args.output_dir:
        out_dir = args.output_dir.expanduser().resolve()
    else:
        out_dir = PROBE_DIR / ("outputs_smoke_v2" if args.smoke
                               else "results_v2")
    out_dir.mkdir(parents=True, exist_ok=True)
    _LOG_FILE = out_dir / "run_log.txt"
    if args.phase == "B":
        # Phase B is multi-session over one persistent bundle: append, with
        # a visible session boundary, so run_log.txt stays a full history.
        with open(_LOG_FILE, "a") as f:
            f.write(f"\n===== phase-B session starting {utc_now()} =====\n")
    else:
        _LOG_FILE.write_text("")   # fresh log for single-shot M / smoke

    assert_sign_directions()
    mode = "smoke" if args.smoke else f"phase {args.phase}"
    log(f"idea-004 contract-v2 driver starting ({mode})")
    gate_info = phase0_gate("SMOKE" if args.smoke else args.phase)
    if args.smoke:
        return run_smoke(out_dir, gate_info)
    if args.phase == "M":
        return run_phase_m(out_dir, gate_info)
    return run_phase_b(out_dir, gate_info)


if __name__ == "__main__":
    try:
        sys.exit(main())
    except SystemExit:
        raise
    except KeyboardInterrupt:
        print("\ninterrupted", file=sys.stderr)
        sys.exit(12)
    except Exception as e:  # never silently swallow a harness fault
        print(f"UNEXPECTED INTERNAL ERROR (exit 12, not a contract result): "
              f"{e!r}", file=sys.stderr)
        sys.exit(12)
