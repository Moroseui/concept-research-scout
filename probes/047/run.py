#!/usr/bin/env python3
"""Idea 047, Phase B: the clinical estimation table for the keystone-ten head.

This experiment is the sole executable phase of the approved
ideas/047/probe_contract.yaml (contract version 3, the pre-registered
Phase-B amendment). Phase A is COMPLETE and of record under its own
historical blob; this code never recomputes Phase-A science -- it only
re-verifies byte/value identity of the consumed Phase-A artifacts, then:
(1) stages exactly the 198 phenotype members (99 cases x demographic_baseline
+ outcome CSVs) from the held, md5-verified ISLES'24 train.7z in one
selective-extraction event, size/CRC-checked against the frozen archive
manifest; (2) runs the pre-registered phenotype schema/missingness census
over the bound seven-variable list BEFORE any contrast is computed; and
(3) emits the single aggregate 10-versus-89 clinical estimation table with
the closed statistic menu, both frozen exploratory uncertainty displays,
the D4 joint support display, per-group missingness, and small-cell
suppression.

Primary metric: the pre-frozen aggregate 10-versus-89 estimation table over
the bound variable list, every row jointly displayed with eligible deficit
support per D4. Stopping rule: stop immediately on any invalidating failure
or the pre-registered census stop; staging transport is uncapped but fully
receipted; post-staging CPU wall time is capped at 15 minutes; the run stops
after the estimation table, uncertainty file, and suppression log are
written. A positive result is STUDY_COMPLETE -- a successful descriptive
result regardless of what the table shows, carrying no separation verdict,
no clinical-silence/markedness reading, and no proportionality verdict.
NO DIRECTIONAL NEGATIVE IS DEFINED: PHENOTYPE_SCHEMA_MISMATCH (exit 4, the
staged case-level rows cannot support the minimum variable set) is a
pre-registered decision-grade stop for escalation, not a negative and not
invalidating; its reduced interface (census + staging audit, no clinical
estimation output) is the deliverable on that path.

Run (Phase B, after fresh human approval of the v3 blob; all inputs are
local paths -- no network access exists anywhere in this probe):
    python probes/047/run.py --output-dir OUT \
        --archive-file /path/to/train.7z \
        --member-manifest /path/to/archive_manifest.csv
Smoke (synthetic fixtures, no archive, no 7z, never a gate):
    python probes/047/run.py --smoke --output-dir /tmp/probe-047-smoke

Exit codes: 0 valid completion (STUDY_COMPLETE or SMOKE_ONLY); 2
authority/CLI; 3 input identity (pin, blob, constant, or archive-identity
mismatch); 4 pre-registered PHENOTYPE_SCHEMA_MISMATCH stop; 5
staging-integrity failure (extraction rc, member count, size/CRC); 6
scope/blindness violation; 7 output/determinism failure; 8 wall time;
12 unexpected harness fault (full traceback to stderr).
"""

import argparse
import csv
import hashlib
import json
import math
import os
import platform
import random
import re
import shutil
import subprocess
import sys
import time
import traceback
import zlib
from pathlib import Path


IDEA_ID = "idea-047"
CONTRACT_VERSION = 3
PHASE = "B"
# Contract's single frozen seed, used SOLELY for the 10000
# hypothetical-exchangeability relabelings. No point estimate depends on it.
SEED = 20260902
RELABELINGS = 10000        # Contract uncertainty clause: frozen draw count.
EXPECTED_CASES = 99        # The frozen take-13 census cohort.
HEAD_SIZE = 10             # The frozen signed-rank top ten.
SMOKE_CASES = 12           # Synthetic smoke cohort size.
SMOKE_HEAD_SIZE = 3        # Smoke head; smoke can never satisfy a gate.
# Contract stopping rule: staging transport is uncapped (receipted); the
# post-staging analysis wall is capped at 15 minutes.
POST_STAGING_WALL_SECONDS = 15 * 60
# A head-group non-missing count below this is flagged
# insufficient_head_coverage and still reported (common missingness rule).
HEAD_COVERAGE_FLOOR = 7

PROBE_DIR = Path(__file__).resolve().parent
REPO_ROOT = PROBE_DIR.parent.parent
CONTRACT_PATH = REPO_ROOT / "ideas/047/probe_contract.yaml"
APPROVAL_PATH = REPO_ROOT / "ideas/047/HUMAN_APPROVED_PROBE"

# Frozen inputs (contract dataset.frozen_inputs) -- retained from v2 for
# identity continuity; hashed in both determinism manifests, never re-analyzed.
EXCLUSIONS_PATH = REPO_ROOT / "probes/023/results/results_v2/exclusions.csv"
CONTRIB_PATH = REPO_ROOT / "probes/046/results/results_v3/per_case_contributions.csv"
CENSUS_PATH = REPO_ROOT / "probes/046/results/results_v3/census_summary.json"
EXPECTED_EXCLUSIONS_SHA256 = "58e9f8ab7cea38e6717319a26ea6a590dc7d1ad0d42d6b30dca648b0509a5a71"
EXPECTED_CONTRIB_SHA256 = "aba525122f796618761e6c4d29b664647760e8dff4987932c3ff6ab5456faae9"
EXPECTED_CENSUS_SHA256 = "189c0ce846cffd2eff76e896bfa35156893568d5ee64868caae0b8609bd4c761"

# Consumed Phase-A artifacts (contract dataset.consumed_phase_a_artifacts).
# The bundle is imported history: read-only, verified, never modified.
BUNDLE_DIR = REPO_ROOT / "probes/047/results/results_v2"
FREEZE_PATH = BUNDLE_DIR / "proposed_variable_freeze.json"
SUPPORT_PATH = BUNDLE_DIR / "per_case_support.csv"
BUNDLE_RESOLVED_CONFIG = BUNDLE_DIR / "resolved_config.json"
EXPECTED_FREEZE_SHA256 = "87c5e11be45dccdf6fc32fd26a9591de0436697e51aacf64610236fbedf5d4e3"
EXPECTED_SUPPORT_SHA256 = "994a4f8885c28e4e967f290521a9122e15ba56b28942e1bb5facff7f4afaa827"
GOVERNING_PHASE_A_BLOB = "b4887c05a21bfe870589b5d9982066943df679d5"
PHASE_A_BUNDLE_COMMIT = "6037f24122766fe1c68f16eb9f38d9a16c2c5e66"

# Archive identity (contract dataset.archive). The record pin never
# re-resolves at runtime (2026-08-25 lesson: a pin that can re-resolve at
# runtime is not a pin); the md5 gate arbitrates definitively.
ZENODO_RECORD = "16813698"
ARCHIVE_NAME = "train.7z"
ARCHIVE_BYTES = 99014629647
ARCHIVE_MD5 = "36ae28b9a17f7340b8bbef62b595cb57"
MEMBER_MANIFEST_BLOB = "edb9a8c2ceb90df214cdd7ec167f0b1e8c858bb2"

# Frozen Phase-A constants (contract dataset.frozen_phase_a_constants).
# Republished verbatim in the D4 joint display and summary context ONLY;
# recomputed from per_case_support.csv at step 1 and required to agree
# exactly, or the run is an invalidating input-identity failure.
FROZEN_PHASE_A_CONSTANTS = {
    "head_abs_contribution_share": 0.5063509495830807,
    "head_support_share": 0.08961200117675944,
    "head_abs_contribution_sum": 0.04367036086720666,
    "total_abs_contribution_sum": 0.08624524334982282,
    "head_support_voxels": 2025630,
    "total_support_voxels": 22604450,
    "signed_head_net_gap_share": 0.7928912778985707,
}
REVERSAL_ACCOUNTING_LABEL = (
    "Share of the NET band-2/3 gap after cancellation across the opposing "
    "cases. Reversal accounting only: neither this number nor its difference "
    "from the support share may be interpreted as contribution per unit "
    "support or as evidence of keystone-like dominance.")
# The contract's verbatim label for the relabeling display.
EXCHANGEABILITY_LABEL = ("hypothetical exchangeability reference; not a "
                         "confidence interval; not sampling inference")

# The two documented bookkeeping exclusions, of record from the take-13
# lineage; emitted to the exclusions log for continuity.
EXPECTED_BOOKKEEPING = [
    {"case_id": "sub-stroke0142", "record_type": "excluded_archive_lesion",
     "reason": "duplicate/noncanonical lesion bookkeeping (take-13 record)"},
    {"case_id": "sub-stroke0043", "record_type": "excluded_case",
     "reason": "source_corrupt_member"},
]

# ---------------------------------------------------------------------------
# THE PREDECLARED 10/89 SPLIT (hard standard 5). These ids were BOUND AT
# AUTHORING TIME, transcribed from the pinned, ratified tables the contract
# freezes (per_case_contributions.csv sha256 aba52512..., cross-checked
# against the in_head flags of per_case_support.csv sha256 994a4f88...):
# index i holds the case with signed_rank i+1; the head is ranks 1..10.
# Binding the split as literals lets run() write and hash the split manifest
# BEFORE either outcome-derived table is hashed or opened in this process;
# the tables are then loaded and verified against this declaration
# (rank->id mapping and in_head flags) by verify_split_against_tables(),
# where any disagreement is an invalidating input-identity failure. A
# reviewer can regenerate this tuple from the pinned table with one sort
# on signed_rank.
# ---------------------------------------------------------------------------

FROZEN_ANALYZED_IDS_BY_RANK = (
    # Ranks 1-10: the frozen signed-rank head.
    "sub-stroke0153", "sub-stroke0002", "sub-stroke0166", "sub-stroke0181",
    "sub-stroke0014", "sub-stroke0098", "sub-stroke0090", "sub-stroke0114",
    "sub-stroke0025", "sub-stroke0136",
    # Ranks 11-99: the rest stratum, still in signed-rank order.
    "sub-stroke0107", "sub-stroke0093", "sub-stroke0089", "sub-stroke0096",
    "sub-stroke0167", "sub-stroke0088", "sub-stroke0155", "sub-stroke0021",
    "sub-stroke0078", "sub-stroke0102", "sub-stroke0026", "sub-stroke0105",
    "sub-stroke0081", "sub-stroke0189", "sub-stroke0083", "sub-stroke0156",
    "sub-stroke0112", "sub-stroke0009", "sub-stroke0080", "sub-stroke0037",
    "sub-stroke0187", "sub-stroke0015", "sub-stroke0180", "sub-stroke0082",
    "sub-stroke0188", "sub-stroke0140", "sub-stroke0119", "sub-stroke0170",
    "sub-stroke0138", "sub-stroke0174", "sub-stroke0005", "sub-stroke0068",
    "sub-stroke0106", "sub-stroke0022", "sub-stroke0092", "sub-stroke0012",
    "sub-stroke0084", "sub-stroke0075", "sub-stroke0057", "sub-stroke0030",
    "sub-stroke0013", "sub-stroke0148", "sub-stroke0086", "sub-stroke0079",
    "sub-stroke0094", "sub-stroke0141", "sub-stroke0142", "sub-stroke0147",
    "sub-stroke0163", "sub-stroke0175", "sub-stroke0184", "sub-stroke0019",
    "sub-stroke0139", "sub-stroke0071", "sub-stroke0077", "sub-stroke0047",
    "sub-stroke0185", "sub-stroke0074", "sub-stroke0055", "sub-stroke0157",
    "sub-stroke0182", "sub-stroke0100", "sub-stroke0109", "sub-stroke0151",
    "sub-stroke0111", "sub-stroke0045", "sub-stroke0038", "sub-stroke0048",
    "sub-stroke0169", "sub-stroke0008", "sub-stroke0164", "sub-stroke0036",
    "sub-stroke0134", "sub-stroke0145", "sub-stroke0104", "sub-stroke0186",
    "sub-stroke0006", "sub-stroke0179", "sub-stroke0133", "sub-stroke0161",
    "sub-stroke0033", "sub-stroke0028", "sub-stroke0095", "sub-stroke0070",
    "sub-stroke0113", "sub-stroke0154", "sub-stroke0117", "sub-stroke0183",
    "sub-stroke0137",
)

# Blindness guard (contract scope.excluded): these may never be touched.
# Phase B stages and reads ONLY the 198 phenotype members; every imaging
# member class and the untouchable take-13 table are refused by path.
FORBIDDEN_PATH_FRAGMENTS = ("per_patient.csv", "perfusion-maps", "lesion-msk",
                            ".nii", "_ncct", "raw_data/", "rawdata/")

# ---------------------------------------------------------------------------
# THE BOUND FROZEN VARIABLE LIST (contract analysis.clinical_clause).
# Constructs, spellings, types, codings, and statistics are the v3 bindings,
# transcribed exactly; no variable may be added, dropped, or re-typed here.
# expected_family is where the dictionary places the field; resolution
# tolerates either file of a case's pair but never a different spelling.
# ---------------------------------------------------------------------------

MRS_LEVELS = ["0", "1", "2", "3", "4", "5", "6"]
MTICI_LEVELS = ["0", "1", "2a", "2b", "2c", "3"]  # Frozen published order.

VARIABLES = [
    {"construct": "mrs_3month", "field": "MRS 3 months", "vtype": "ordinal",
     "role": "primary outcome", "expected_family": "outcome",
     "levels": MRS_LEVELS,
     "coding": "integer levels 0-6 (modified Rankin Scale); parse: integer "
               "in [0,6], else missing"},
    {"construct": "nihss_24h", "field": "NIHSS 24h", "vtype": "continuous",
     "role": "lineage-preserving severity (idea-046 frozen optional rung)",
     "expected_family": "outcome",
     "coding": "integer in [0,42], else missing"},
    {"construct": "nihss_admission", "field": "NIHSS at admission",
     "vtype": "continuous",
     "role": "baseline-severity context; never interchangeable with 24h",
     "expected_family": "baseline",
     "coding": "integer in [0,42], else missing"},
    {"construct": "age", "field": "Age", "vtype": "continuous",
     "role": "demographic", "expected_family": "baseline",
     "coding": "integer in [0,120], else missing"},
    {"construct": "sex", "field": "Sex", "vtype": "binary",
     "role": "demographic", "expected_family": "baseline",
     "levels": ["F", "M"],
     "coding": "trimmed case-insensitive 'M' or 'F', else missing; frozen "
               "reference level for the contrast: proportion F"},
    {"construct": "mtici_postinterventional", "field": "mTici postinterventional",
     "vtype": "ordinal", "role": "contextual (cap slot 1 of 2)",
     "expected_family": "outcome", "levels": MTICI_LEVELS,
     "coding": "frozen level order 0 < 1 < 2a < 2b < 2c < 3, case-insensitive "
               "on the trimmed value; out-of-set values are missing and counted"},
    {"construct": "onset_to_door", "field": "Onset to door", "vtype": "continuous",
     "role": "contextual (cap slot 2 of 2)", "expected_family": "baseline",
     "coding": "parse H:MM or HH:MM with minutes in [0,59], convert to total "
               "minutes, else missing"},
]
# Pre-registered census stop rule: at least one severity/outcome construct
# AND at least one demographic construct must resolve with >= 1 non-missing
# value each, else PHENOTYPE_SCHEMA_MISMATCH.
MIN_SET_SEVERITY = {"mrs_3month", "nihss_24h", "nihss_admission"}
MIN_SET_DEMOGRAPHIC = {"age", "sex"}
# Closed statistic menu: contrasts per variable type. No other statistic
# exists anywhere in this file.
CONTRASTS_BY_TYPE = {"continuous": ["smd_pooled", "diff_medians"],
                     "ordinal": ["diff_medians", "rank_biserial"],
                     "binary": ["diff_prop_F"]}

EXIT_AUTHORITY = 2
EXIT_INPUT = 3
EXIT_SCHEMA_STOP = 4
EXIT_STAGING = 5
EXIT_SCOPE = 6
EXIT_OUTPUT = 7
EXIT_WALL = 8
EXIT_INTERNAL = 12


class ProbeFailure(RuntimeError):
    def __init__(self, code, message):
        super().__init__(message)
        self.code = code


def fail(code, message):
    raise ProbeFailure(code, message)


def check_path_allowed(path):
    """Blindness guard: refuse to touch imaging members or per_patient.csv."""
    text = str(Path(path).resolve()).replace(os.sep, "/")
    for fragment in FORBIDDEN_PATH_FRAGMENTS:
        if fragment in text:
            fail(EXIT_SCOPE, f"blindness guard: refusing to touch {text} ({fragment})")
    return Path(path)


def read_bytes_checked(path):
    return check_path_allowed(path).read_bytes()


def sha256_bytes(data):
    return hashlib.sha256(data).hexdigest()


def sha256_file(path):
    return sha256_bytes(read_bytes_checked(path))


def git_blob(path):
    data = read_bytes_checked(path)
    return hashlib.sha1(f"blob {len(data)}\0".encode("ascii") + data).hexdigest()


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n",
                    encoding="utf-8")


def write_csv(path, fieldnames, rows):
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def emit(message, log_lines):
    print(message, flush=True)
    log_lines.append(message)


def parse_args():
    parser = argparse.ArgumentParser(description="Idea 047 Phase B probe")
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--archive-file", type=Path, default=None,
                        help="REQUIRED for a real run: local path to the held "
                             "train.7z from immutable Zenodo record 16813698 "
                             "(99,014,629,647 bytes, md5 36ae28b9...), verified "
                             "before extraction. Use local disk, not a FUSE "
                             "mount (2026-08-25/26 lessons).")
    parser.add_argument("--member-manifest", type=Path, default=None,
                        help="REQUIRED for a real run: local copy of the frozen "
                             "archive member manifest archive_manifest.csv "
                             "(path,size,crc), byte-verified against git blob "
                             "edb9a8c2... before use. Materialize with: "
                             "git cat-file blob edb9a8c2ceb90df214cdd7ec167"
                             "f0b1e8c858bb2 > archive_manifest.csv")
    parser.add_argument("--sevenzip", default="7z",
                        help="7-Zip executable used for the single selective "
                             "extraction (default: 7z). Transport-only knob; "
                             "changes no scientific behavior.")
    parser.add_argument("--smoke", action="store_true")
    return parser.parse_args()


# ---------------------------------------------------------------------------
# AUTHORITY. Phase B runs only under a human approval marker binding the
# exact current contract blob, and the contract must be the amended v3 --
# it must carry every implementation literal this file encodes and must NOT
# carry the v2 pre-amendment sentinel. Smoke skips approval entirely and can
# never satisfy a contractual gate.
# ---------------------------------------------------------------------------

CONTRACT_LITERALS = [
    "contract_version: 3",
    "maximum_variants: 1",
    "maximum_gpu_minutes: 0",
    "maximum_seeds: 1",
    "STUDY_COMPLETE",
    "PHENOTYPE_SCHEMA_MISMATCH",
    "NO DIRECTIONAL NEGATIVE IS DEFINED",
    "20260902",
    "10000",
    EXPECTED_EXCLUSIONS_SHA256,
    EXPECTED_CONTRIB_SHA256,
    EXPECTED_CENSUS_SHA256,
    EXPECTED_FREEZE_SHA256,
    EXPECTED_SUPPORT_SHA256,
    GOVERNING_PHASE_A_BLOB,
    MEMBER_MANIFEST_BLOB,
    ARCHIVE_MD5,
    "99014629647",
    "16813698",
    "0.5063509495830807",
    "0.08961200117675944",
    "0.04367036086720666",
    "0.08624524334982282",
    "2025630",
    "22604450",
    "0.7928912778985707",
    'field: "MRS 3 months"',
    'field: "NIHSS 24h"',
    'field: "NIHSS at admission"',
    'field: "Age"',
    'field: "Sex"',
    'field: "mTici postinterventional"',
    'field: "Onset to door"',
    "0 < 1 < 2a < 2b < 2c < 3",
    EXCHANGEABILITY_LABEL,
    "phenotype_schema_census.csv",
    "clinical_estimation_table.csv",
    "clinical_uncertainty.json",
    "suppression_log.csv",
    "staging_audit.json",
]


def verify_authority(smoke):
    if smoke:
        return "SMOKE_NOT_APPROVAL_ELIGIBLE"
    if not CONTRACT_PATH.is_file() or not APPROVAL_PATH.is_file():
        fail(EXIT_AUTHORITY, "contract or HUMAN_APPROVED_PROBE is missing")
    marker = APPROVAL_PATH.read_text(encoding="utf-8")
    match = re.search(r"^contract_blob:\s*([0-9a-f]{40})$", marker, re.MULTILINE)
    if not match:
        fail(EXIT_AUTHORITY, "approval marker lacks a 40-hex contract_blob")
    actual = git_blob(CONTRACT_PATH)
    if match.group(1) != actual:
        fail(EXIT_AUTHORITY, "approval marker is stale for the current contract")
    text = CONTRACT_PATH.read_text(encoding="utf-8")
    missing = [literal for literal in CONTRACT_LITERALS if literal not in text]
    if missing:
        fail(EXIT_AUTHORITY, f"approved contract lacks implementation literals: {missing}")
    if "<<TO_BE_FROZEN_AT_AMENDMENT>>" in text:
        # The v2 pre-amendment sentinel means the variable list was never
        # bound; this Phase-B implementation governs the amended v3 only.
        fail(EXIT_AUTHORITY, "contract still carries the pre-amendment sentinel; "
                             "this Phase-B implementation does not govern it")
    return actual


def prepare_output_dir(path):
    path.mkdir(parents=True, exist_ok=True)
    if any(path.iterdir()):
        fail(EXIT_OUTPUT, "output directory must be empty")


# ---------------------------------------------------------------------------
# STEP 1 -- IDENTITY GATES. Runs only AFTER the split manifest is written
# and hashed (hard standard 5): the contribution and support tables are
# outcome-derived claim-bearing inputs from the idea-023/046 lineage, so
# this process neither hashes nor opens them until the predeclared split
# is frozen on disk. Then: hash the three frozen inputs and both consumed
# Phase-A artifacts against their pins; check the bundle's own recorded
# governing blob; verify the loaded tables against the predeclared split
# (rank->id mapping and in_head flags); cross-check head membership between
# the consumed support table and the frozen contribution table; recompute
# all seven frozen Phase-A constants and require EXACT equality (math.fsum
# is correctly rounded, so exact float equality is well-defined). Any
# mismatch is an invalidating input-identity failure.
# ---------------------------------------------------------------------------

def hash_inputs(paths):
    manifest = {}
    for name, path in paths.items():
        if not path.is_file():
            fail(EXIT_INPUT, f"missing input: {path}")
        manifest[name] = {"path": str(path.resolve()), "sha256": sha256_file(path)}
    return manifest


def verify_input_pins(manifest, smoke):
    if smoke:
        return
    pins = {"exclusions.csv": EXPECTED_EXCLUSIONS_SHA256,
            "per_case_contributions.csv": EXPECTED_CONTRIB_SHA256,
            "census_summary.json": EXPECTED_CENSUS_SHA256,
            "proposed_variable_freeze.json": EXPECTED_FREEZE_SHA256,
            "per_case_support.csv": EXPECTED_SUPPORT_SHA256}
    for name, expected in pins.items():
        if manifest[name]["sha256"] != expected:
            fail(EXIT_INPUT, f"{name} SHA-256 {manifest[name]['sha256']} "
                             f"differs from pin {expected}")
    manifest_blob = git_blob(Path(manifest["archive_manifest.csv"]["path"]))
    if manifest_blob != MEMBER_MANIFEST_BLOB:
        fail(EXIT_INPUT, f"member manifest git blob {manifest_blob} differs "
                         f"from pin {MEMBER_MANIFEST_BLOB}")
    bundle_config = json.loads(read_bytes_checked(BUNDLE_RESOLVED_CONFIG))
    if bundle_config.get("contract_blob") != GOVERNING_PHASE_A_BLOB:
        fail(EXIT_INPUT, "Phase-A bundle resolved_config.json does not record "
                         f"governing blob {GOVERNING_PHASE_A_BLOB}")


def load_contributions(path, expected_cases):
    """Frozen contribution table: identical validation to the of-record
    Phase-A loader (column set, 1..N signed-rank permutation under the
    frozen ordering, delta and contribution identities)."""
    with check_path_allowed(path).open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        expected_cols = ["case_id", "d_band2", "d_band3", "delta",
                         "contribution", "signed_rank"]
        if reader.fieldnames != expected_cols:
            fail(EXIT_INPUT, f"contribution table columns {reader.fieldnames} "
                             f"differ from frozen {expected_cols}")
        rows = []
        for raw in reader:
            try:
                row = {"case_id": raw["case_id"],
                       "d_band2": float(raw["d_band2"]),
                       "d_band3": float(raw["d_band3"]),
                       "delta": float(raw["delta"]),
                       "contribution": float(raw["contribution"]),
                       "signed_rank": int(raw["signed_rank"])}
            except (TypeError, ValueError):
                fail(EXIT_INPUT, f"nonnumeric contribution row: {raw}")
            for key in ("d_band2", "d_band3", "delta", "contribution"):
                if not math.isfinite(row[key]):
                    fail(EXIT_INPUT, f"nonfinite {key} for {row['case_id']}")
            rows.append(row)
    if len(rows) != expected_cases:
        fail(EXIT_INPUT, f"contribution table has {len(rows)} rows, "
                         f"expected {expected_cases}")
    ids = [row["case_id"] for row in rows]
    if len(set(ids)) != expected_cases:
        fail(EXIT_INPUT, "duplicate case_id in contribution table")
    if sorted(row["signed_rank"] for row in rows) != list(range(1, expected_cases + 1)):
        fail(EXIT_INPUT, "signed_rank is not a 1..N permutation")
    frozen_order = sorted(rows, key=lambda r: (-r["contribution"], r["case_id"]))
    for position, row in enumerate(frozen_order, start=1):
        if row["signed_rank"] != position:
            fail(EXIT_INPUT, f"signed_rank disagrees with the frozen ordering "
                             f"at position {position} ({row['case_id']})")
    for row in rows:
        assert row["delta"] == row["d_band3"] - row["d_band2"], row["case_id"]
        assert row["contribution"] == row["delta"] / expected_cases, row["case_id"]
    return rows


def load_support(path, expected_cases, head_size):
    """Consumed Phase-A per_case_support.csv: case ids, frozen head flags,
    contributions, and the exact eligible-deficit-support voxel counts."""
    with check_path_allowed(path).open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        needed = {"case_id", "signed_rank", "in_head", "contribution",
                  "abs_contribution", "eroded_region_voxels"}
        if reader.fieldnames is None or not needed.issubset(reader.fieldnames):
            fail(EXIT_INPUT, f"per_case_support.csv lacks required columns "
                             f"{sorted(needed)}")
        rows = []
        for raw in reader:
            if raw["in_head"] not in ("True", "False"):
                fail(EXIT_INPUT, f"unparseable in_head flag: {raw['in_head']!r}")
            try:
                row = {"case_id": raw["case_id"],
                       "signed_rank": int(raw["signed_rank"]),
                       "in_head": raw["in_head"] == "True",
                       "contribution": float(raw["contribution"]),
                       "abs_contribution": float(raw["abs_contribution"]),
                       "support": int(raw["eroded_region_voxels"])}
            except (TypeError, ValueError):
                fail(EXIT_INPUT, f"nonnumeric support row: {raw}")
            # B_i must be a finite positive integer voxel count, and the
            # stored absolute contribution must be |contribution| exactly.
            if row["support"] <= 0:
                fail(EXIT_INPUT, f"nonpositive support for {row['case_id']}")
            if row["abs_contribution"] != abs(row["contribution"]):
                fail(EXIT_INPUT, f"abs_contribution mismatch for {row['case_id']}")
            rows.append(row)
    if len(rows) != expected_cases:
        fail(EXIT_INPUT, f"per_case_support.csv has {len(rows)} rows, "
                         f"expected {expected_cases}")
    ids = [row["case_id"] for row in rows]
    if len(set(ids)) != expected_cases:
        fail(EXIT_INPUT, "duplicate case_id in per_case_support.csv")
    if sum(row["in_head"] for row in rows) != head_size:
        fail(EXIT_INPUT, f"per_case_support.csv head flags do not mark "
                         f"exactly {head_size} cases")
    return rows


def verify_phase_a_constants(support_rows, contrib_rows, head_size, expected):
    """Recompute all seven frozen Phase-A constants from the consumed
    support table and require exact equality; cross-check head membership
    against the frozen contribution table."""
    head_rows = [row for row in support_rows if row["in_head"]]
    head_ids = {row["case_id"] for row in head_rows}
    contrib_head = {row["case_id"] for row in contrib_rows
                    if row["signed_rank"] <= head_size}
    if head_ids != contrib_head:
        fail(EXIT_INPUT, f"head membership mismatch: support marks "
                         f"{sorted(head_ids)} but contribution signed_rank "
                         f"1..{head_size} is {sorted(contrib_head)}")
    if {r["case_id"] for r in support_rows} != {r["case_id"] for r in contrib_rows}:
        fail(EXIT_INPUT, "support and contribution tables cover different cases")
    # math.fsum is exactly rounded, so recomputation is order-independent
    # and equality with the frozen constants is exact, not approximate.
    recomputed = {
        "head_abs_contribution_sum":
            math.fsum(row["abs_contribution"] for row in head_rows),
        "total_abs_contribution_sum":
            math.fsum(row["abs_contribution"] for row in support_rows),
        "head_support_voxels": sum(row["support"] for row in head_rows),
        "total_support_voxels": sum(row["support"] for row in support_rows),
    }
    recomputed["head_abs_contribution_share"] = (
        recomputed["head_abs_contribution_sum"]
        / recomputed["total_abs_contribution_sum"])
    recomputed["head_support_share"] = (
        recomputed["head_support_voxels"] / recomputed["total_support_voxels"])
    net = math.fsum(row["contribution"] for row in support_rows)
    if net == 0.0 or not math.isfinite(net):
        fail(EXIT_INPUT, "net signed contribution is zero or nonfinite")
    recomputed["signed_head_net_gap_share"] = (
        math.fsum(row["contribution"] for row in head_rows) / net)
    mismatches = {name: (recomputed[name], expected[name])
                  for name in expected if recomputed[name] != expected[name]}
    if mismatches:
        fail(EXIT_INPUT, f"frozen Phase-A constant cross-check disagreement "
                         f"(invalidating input-identity failure): {mismatches}")
    return recomputed


def verify_freeze_bindings(freeze_path, smoke):
    """The bound list in this file must be exactly the machine proposal the
    v3 contract claims to bind: same five construct spellings, same two
    contextual fields, center undocumented. Checked by field spelling."""
    freeze = json.loads(read_bytes_checked(freeze_path))
    proposed = {}
    for name, entry in freeze.get("constructs", {}).items():
        proposed[name] = entry.get("proposed_field_spelling")
    contextual = [entry.get("proposed_field_spelling")
                  for entry in freeze.get("contextual_proposed", [])]
    expected_core = {"mrs_3month": "MRS 3 months", "nihss_24h": "NIHSS 24h",
                     "nihss_admission": "NIHSS at admission",
                     "age": "Age", "sex": "Sex"}
    for name, field in expected_core.items():
        if proposed.get(name) != field:
            fail(EXIT_INPUT, f"freeze proposal binds {name} to "
                             f"{proposed.get(name)!r}, this code binds {field!r}")
    expected_contextual = ["mTici postinterventional", "Onset to door"]
    if contextual != expected_contextual:
        fail(EXIT_INPUT, f"freeze proposal contextual fields {contextual} "
                         f"differ from bound {expected_contextual}")
    if freeze.get("center", {}).get("documented") is not False:
        fail(EXIT_INPUT, "freeze proposal does not record center as undocumented")
    return {"core_spellings_match": True, "contextual_spellings_match": True,
            "center_documented": False, "smoke": smoke}


# ---------------------------------------------------------------------------
# SPLIT FREEZE (hard standard 5). The strata are the frozen signed-rank top
# ten versus the other 89, materialized from the authoring-time declaration
# FROZEN_ANALYZED_IDS_BY_RANK (SMOKE_IDS_BY_RANK in smoke) -- never
# recomputed or reselected, and never read from a file in this process.
# The manifest is written and hashed BEFORE any outcome-derived table
# (contribution or support) is hashed or opened, before the archive is
# touched, and before any phenotype byte exists on disk. Assertions prove
# the strata are disjoint, exhaustive, and free of excluded cases; once the
# outcome-derived tables are loaded, verify_split_against_tables() requires
# exact agreement with this manifest.
# ---------------------------------------------------------------------------

def freeze_split(output_dir, ids_by_rank, head_size, smoke):
    assert len(ids_by_rank) == len(set(ids_by_rank)), "duplicate declared id"
    head_ids = sorted(ids_by_rank[:head_size])
    rest_ids = sorted(ids_by_rank[head_size:])
    assert len(head_ids) == head_size
    assert len(rest_ids) == len(ids_by_rank) - head_size
    assert not set(head_ids) & set(rest_ids), "strata overlap"
    assert set(head_ids) | set(rest_ids) == set(ids_by_rank)
    # Only an excluded CASE may never appear in the strata. The
    # sub-stroke0142 bookkeeping row records a duplicate archive lesion
    # MEMBER (record_type excluded_archive_lesion in the take-13
    # exclusions table); the case itself is one of the 99 analyzed and
    # legitimately holds signed_rank 57.
    excluded_cases = {item["case_id"] for item in EXPECTED_BOOKKEEPING
                      if item["record_type"] == "excluded_case"}
    assert not (set(head_ids) | set(rest_ids)) & excluded_cases, \
        "excluded case appears in the analysis strata"
    rows = ([{"case_id": cid, "stratum": "head"} for cid in head_ids]
            + [{"case_id": cid, "stratum": "rest"} for cid in rest_ids])
    rows.sort(key=lambda r: r["case_id"])
    write_csv(output_dir / "split_manifest.csv", ["case_id", "stratum"], rows)
    source_name = "SMOKE_IDS_BY_RANK" if smoke else "FROZEN_ANALYZED_IDS_BY_RANK"
    record = {
        "created_before_any_outcome_derived_table_opened": True,
        "created_before_any_phenotype_byte_staged": True,
        "stratum_source": (f"authoring-time declaration {source_name} "
                           f"(head = ranks 1..{head_size}), bound from the "
                           f"pinned contribution table at code review; "
                           f"never recomputed and never read from a file "
                           f"in this process"),
        "post_freeze_verification": ("the loaded contribution and support "
                                     "tables must agree exactly with this "
                                     "manifest (rank->id mapping, case set, "
                                     "in_head flags) or the run fails as an "
                                     "invalidating input-identity failure"),
        "head_cases": len(head_ids),
        "rest_cases": len(rest_ids),
        "reserved_cases": 0 if smoke else 49,
        "reserved_cases_accessed": 0,
        "phenotype_files_staged_at_freeze_time": 0,
        "seed": SEED,
        "smoke": smoke,
        "split_manifest_sha256": sha256_file(output_dir / "split_manifest.csv"),
    }
    write_json(output_dir / "split_manifest.json", record)
    return record, head_ids, rest_ids


def verify_split_against_tables(ids_by_rank, head_size, contrib_rows,
                                support_rows):
    """Hard standard 5 companion: the outcome-derived tables, opened only
    AFTER the split manifest was written and hashed, must agree exactly
    with the predeclared split. Any disagreement means the declaration or
    the pinned inputs are wrong -- an invalidating input-identity failure,
    never a silent reselection."""
    by_rank = {row["signed_rank"]: row["case_id"] for row in contrib_rows}
    for index, case_id in enumerate(ids_by_rank):
        rank = index + 1
        if by_rank.get(rank) != case_id:
            fail(EXIT_INPUT, f"predeclared split disagrees with the loaded "
                             f"contribution table at signed_rank {rank}: "
                             f"declared {case_id}, table {by_rank.get(rank)!r}")
    declared_head = set(ids_by_rank[:head_size])
    support_head = {row["case_id"] for row in support_rows if row["in_head"]}
    if support_head != declared_head:
        fail(EXIT_INPUT, f"per_case_support.csv in_head flags "
                         f"{sorted(support_head)} differ from the predeclared "
                         f"head {sorted(declared_head)}")


# ---------------------------------------------------------------------------
# STEP 2 -- STAGING. Resolve the exact 198-member extraction set from the
# frozen member manifest (payload spellings outrank prose: both sub-stroke
# and sub-strokecase forms are tolerated and canonicalized by case number);
# verify the held archive's byte count and md5 against the pins; run ONE
# selective 7z extraction of exactly those members; then verify every staged
# file against the manifest's size and CRC32 before any byte is parsed, and
# prove no extra file was extracted. Everything is receipted in
# staging_audit.json. Staging transport is uncapped; the post-staging
# 15-minute analysis wall starts when this step completes.
# ---------------------------------------------------------------------------

CASE_NUM_RE = re.compile(r"sub-stroke(?:case)?(\d+)$")
MEMBER_RE = re.compile(
    r"^train/phenotype/sub-stroke(?:case)?(\d+)/ses-0([12])/"
    r"sub-stroke(?:case)?(\d+)_ses-0([12])_(demographic_baseline|outcome)\.csv$")


def case_number(case_id):
    match = CASE_NUM_RE.fullmatch(case_id)
    if not match:
        fail(EXIT_INPUT, f"case id {case_id!r} does not match the payload pattern")
    return int(match.group(1))


def resolve_members(manifest_path, analyzed_ids):
    """Map each analyzed case to its two phenotype members via the frozen
    manifest. Requires a complete baseline+outcome pair for every case and
    exactly 2 x len(analyzed_ids) members in total."""
    number_to_id = {}
    for case_id in analyzed_ids:
        number = case_number(case_id)
        if number in number_to_id:
            fail(EXIT_INPUT, f"duplicate case number {number} in analyzed ids")
        number_to_id[number] = case_id
    members = {case_id: {} for case_id in analyzed_ids}
    spellings = set()
    with check_path_allowed(manifest_path).open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames != ["path", "size", "crc"]:
            fail(EXIT_INPUT, f"member manifest columns {reader.fieldnames} "
                             f"differ from frozen [path, size, crc]")
        for row in reader:
            match = MEMBER_RE.match(row["path"])
            if not match:
                continue  # Not a phenotype member; never staged.
            if match.group(1) != match.group(3) or match.group(2) != match.group(4):
                fail(EXIT_INPUT, f"inconsistent member path: {row['path']}")
            case_id = number_to_id.get(int(match.group(1)))
            if case_id is None:
                continue  # Phenotype member of a non-census case; never staged.
            family = ("baseline" if match.group(5) == "demographic_baseline"
                      else "outcome")
            expected_session = "1" if family == "baseline" else "2"
            if match.group(2) != expected_session:
                fail(EXIT_INPUT, f"member session/family mismatch: {row['path']}")
            if family in members[case_id]:
                fail(EXIT_INPUT, f"duplicate {family} member for {case_id}")
            members[case_id][family] = {"path": row["path"],
                                        "size": int(row["size"]),
                                        "crc": row["crc"]}
            spellings.add("sub-strokecase" if "sub-strokecase" in row["path"]
                          else "sub-stroke")
    incomplete = sorted(cid for cid, fams in members.items() if len(fams) != 2)
    if incomplete:
        fail(EXIT_STAGING, f"manifest lacks a complete phenotype pair for: "
                           f"{incomplete[:5]} ({len(incomplete)} cases)")
    total = sum(len(fams) for fams in members.values())
    expected_total = 2 * len(analyzed_ids)
    if total != expected_total:
        fail(EXIT_STAGING, f"resolved {total} members, expected {expected_total}")
    return members, sorted(spellings)


def verify_archive_identity(archive_path, log_lines):
    """Byte count first (cheap), then streaming md5 of the full archive.
    The md5 gate is the definitive arbiter of dataset identity."""
    if not archive_path.is_file():
        fail(EXIT_INPUT, f"--archive-file not found: {archive_path}")
    actual_bytes = archive_path.stat().st_size
    if actual_bytes != ARCHIVE_BYTES:
        fail(EXIT_INPUT, f"archive is {actual_bytes} bytes, pin says "
                         f"{ARCHIVE_BYTES}; wrong or truncated file")
    emit(f"[staging] Archive byte count matches pin ({ARCHIVE_BYTES}); "
         f"computing streaming md5 (this reads the full ~99 GB once).", log_lines)
    digest = hashlib.md5()
    read = 0
    chunk_bytes = 32 * 1024 * 1024
    with archive_path.open("rb") as handle:
        while True:
            chunk = handle.read(chunk_bytes)
            if not chunk:
                break
            digest.update(chunk)
            read += len(chunk)
            if read % (8 * 1024 * 1024 * 1024) < chunk_bytes:
                emit(f"[staging] md5 progress: {read / 1e9:.1f} / "
                     f"{ARCHIVE_BYTES / 1e9:.1f} GB.", log_lines)
    actual_md5 = digest.hexdigest()
    if actual_md5 != ARCHIVE_MD5:
        fail(EXIT_INPUT, f"archive md5 {actual_md5} differs from pin "
                         f"{ARCHIVE_MD5}; staging must not proceed")
    return actual_md5


def extract_members(sevenzip, archive_path, staged_dir, member_paths,
                    output_dir, log_lines):
    """The single selective-extraction staging event: one 7z invocation
    naming exactly the 198 members. rc must be 0; console output is
    receipted verbatim."""
    binary = shutil.which(sevenzip)
    if binary is None:
        fail(EXIT_STAGING, f"7-Zip executable {sevenzip!r} not found; install "
                           f"p7zip or pass --sevenzip")
    version = subprocess.run([binary], capture_output=True, text=True)
    version_line = (version.stdout or version.stderr or "").strip().splitlines()
    version_line = version_line[0] if version_line else "unknown"
    staged_dir.mkdir(parents=True)
    command = [binary, "x", str(archive_path), f"-o{staged_dir}", "-y",
               *member_paths]
    emit(f"[staging] Extracting {len(member_paths)} members with "
         f"{version_line} (single selective event).", log_lines)
    started = time.monotonic()
    result = subprocess.run(command, capture_output=True, text=True)
    seconds = time.monotonic() - started
    (output_dir / "staging_extraction_log.txt").write_text(
        f"command: {' '.join(command[:5])} ... [{len(member_paths)} members]\n"
        f"returncode: {result.returncode}\n\n--- stdout ---\n{result.stdout}\n"
        f"--- stderr ---\n{result.stderr}\n", encoding="utf-8")
    if result.returncode != 0:
        fail(EXIT_STAGING, f"7z extraction returned {result.returncode}; "
                           f"see staging_extraction_log.txt")
    return {"binary": binary, "version": version_line,
            "returncode": result.returncode, "seconds": round(seconds, 3)}


def verify_staged_members(staged_dir, members, log_lines):
    """Every staged file must be one of the resolved members (no extras)
    and must match the frozen manifest's size and CRC32 exactly before a
    single byte is parsed."""
    expected = {}
    for case_id, families in sorted(members.items()):
        for family, info in sorted(families.items()):
            expected[info["path"]] = (case_id, family, info)
    found = set()
    for root, _dirs, files in os.walk(staged_dir):
        for name in files:
            full = Path(root) / name
            rel = full.relative_to(staged_dir).as_posix()
            if rel not in expected:
                fail(EXIT_SCOPE, f"staged tree contains a file outside the "
                                 f"198-member extraction set: {rel}")
            found.add(rel)
    missing = sorted(set(expected) - found)
    if missing:
        fail(EXIT_STAGING, f"{len(missing)} members missing after extraction, "
                           f"first: {missing[:3]}")
    verification = []
    for rel, (case_id, family, info) in sorted(expected.items()):
        data = (staged_dir / rel).read_bytes()
        size_ok = len(data) == info["size"]
        # CRC compared as integers, robust to hex zero-padding differences.
        crc_ok = zlib.crc32(data) == int(info["crc"], 16)
        verification.append({"path": rel, "case_id": case_id, "family": family,
                             "size_expected": info["size"], "size_actual": len(data),
                             "crc_expected": info["crc"], "crc_ok": crc_ok,
                             "sha256": sha256_bytes(data)})
        if not size_ok or not crc_ok:
            fail(EXIT_STAGING, f"staged member fails manifest verification: "
                               f"{rel} (size_ok={size_ok}, crc_ok={crc_ok})")
    emit(f"[staging] {len(verification)} staged members verified against the "
         f"frozen manifest (size + CRC32).", log_lines)
    return verification


# ---------------------------------------------------------------------------
# STEP 3 -- PHENOTYPE SCHEMA / MISSINGNESS CENSUS. Parse every staged member;
# resolve each bound field by the frozen rule (trim, casefold, collapse
# internal whitespace; exact normalized equality; expected file family
# preferred, either tolerated, never a different spelling); classify every
# case-value as ok / empty / parse_failure / unresolved; and emit counts
# only -- no clinical value appears in the census. The pre-registered stop
# fires here if the minimum variable set is unsupported.
# ---------------------------------------------------------------------------

def normalize_header(text):
    """Frozen field_resolution_rule normalization. The chr(0xFEFF) strip is
    byte hygiene for utf-8 exports (interior BOMs), not header matching."""
    return re.sub(r"\s+", " ", text.replace(chr(0xFEFF), "").strip()).casefold()


def parse_int_field(raw, low, high):
    """'integer in [low,high], else missing'. A decimal representation of an
    exact integer (e.g. '7.0') is normalized to that integer and tallied --
    the 2026-08-12 lesson: deterministic normalization robust to payload
    formatting, never silent, never admitting non-integers."""
    text = raw.strip()
    status = "ok"
    if re.fullmatch(r"[+-]?\d+", text):
        value = int(text)
    elif re.fullmatch(r"[+-]?\d+\.0+", text):
        value = int(text.split(".", 1)[0])
        status = "ok_decimal_normalized"
    else:
        return None, "parse_failure"
    if not low <= value <= high:
        return None, "parse_failure"
    return value, status


def parse_value(variable, raw):
    """Returns (numeric_value, level_label, status). Numeric values feed the
    closed statistic menu; level labels feed ordinal/binary count displays.
    status: ok | ok_decimal_normalized | empty | parse_failure."""
    if raw is None or raw.strip() == "":
        return None, None, "empty"
    construct = variable["construct"]
    if construct == "mrs_3month":
        value, status = parse_int_field(raw, 0, 6)
        return (value, str(value), status) if value is not None else (None, None, status)
    if construct in ("nihss_24h", "nihss_admission"):
        value, status = parse_int_field(raw, 0, 42)
        return (value, None, status) if value is not None else (None, None, status)
    if construct == "age":
        value, status = parse_int_field(raw, 0, 120)
        return (value, None, status) if value is not None else (None, None, status)
    if construct == "sex":
        text = raw.strip().upper()
        if text in ("M", "F"):
            # Numeric value = indicator of the frozen reference level F, so
            # the mean is the proportion F and the closed-menu contrast is a
            # difference of those means.
            return (1.0 if text == "F" else 0.0), text, "ok"
        return None, None, "parse_failure"
    if construct == "mtici_postinterventional":
        text = raw.strip().lower()
        if text in MTICI_LEVELS:
            # Numeric value = index in the frozen level order; medians and
            # their differences are in frozen level-order steps.
            return MTICI_LEVELS.index(text), text, "ok"
        return None, None, "parse_failure"
    if construct == "onset_to_door":
        match = re.fullmatch(r"(\d{1,2}):([0-5]\d)", raw.strip())
        if match:
            return int(match.group(1)) * 60 + int(match.group(2)), None, "ok"
        return None, None, "parse_failure"
    raise AssertionError(f"unknown construct {construct}")


def parse_phenotype_file(path):
    """Read one staged member. Returns (headers_map, data_row, anomalies):
    headers_map maps normalized header -> (verbatim header, column index),
    with duplicated normalized headers recorded and unusable. Exactly one
    data row is expected; 0 or >1 makes the file unusable (anomaly)."""
    anomalies = []
    with check_path_allowed(path).open(newline="", encoding="utf-8-sig") as handle:
        rows = list(csv.reader(handle))
    if not rows:
        return {}, None, ["empty_file"]
    headers = rows[0]
    data_rows = [row for row in rows[1:] if any(cell.strip() for cell in row)]
    headers_map = {}
    duplicates = set()
    for index, header in enumerate(headers):
        key = normalize_header(header)
        if not key:
            continue
        if key in headers_map:
            duplicates.add(key)
        else:
            headers_map[key] = (header, index)
    for key in duplicates:
        del headers_map[key]
        anomalies.append(f"duplicate_header:{key}")
    if len(data_rows) != 1:
        anomalies.append(f"data_rows:{len(data_rows)}")
        return headers_map, None, anomalies
    return headers_map, data_rows[0], anomalies


def census_and_values(members, staged_dir, head_ids, rest_ids, log_lines):
    """The pre-registered census. Emits per-variable, per-stratum counts and
    internally retains parsed values (never written per-case) for step 4."""
    head_set = set(head_ids)
    all_ids = sorted(head_ids) + sorted(rest_ids)
    parsed_files = {}    # case_id -> family -> (headers_map, data_row)
    file_stats = {}      # case_id -> per-family bookkeeping for per_case_staging
    anomaly_cases = []
    for index, case_id in enumerate(sorted(all_ids), start=1):
        parsed_files[case_id] = {}
        file_stats[case_id] = {}
        for family in ("baseline", "outcome"):
            rel = members[case_id][family]["path"]
            headers_map, data_row, anomalies = parse_phenotype_file(staged_dir / rel)
            parsed_files[case_id][family] = (headers_map, data_row)
            file_stats[case_id][family] = {
                "member": rel,
                "data_row_usable": data_row is not None,
                "anomalies": ";".join(anomalies) if anomalies else "",
            }
            for anomaly in anomalies:
                anomaly_cases.append({"case_id": case_id, "family": family,
                                      "anomaly": anomaly})
        if index % 25 == 0 or index == len(all_ids):
            emit(f"[census] Parsed {index}/{len(all_ids)} cases "
                 f"(headers and row counts only so far).", log_lines)

    census_rows = []
    values = {}   # construct -> case_id -> numeric value (non-missing only)
    labels = {}   # construct -> case_id -> level label (ordinal/binary)
    for variable in VARIABLES:
        construct = variable["construct"]
        bound_norm = normalize_header(variable["field"])
        expected_family = variable["expected_family"]
        other_family = "outcome" if expected_family == "baseline" else "baseline"
        values[construct] = {}
        labels[construct] = {}
        counts = {stratum: {"nonmissing": 0, "empty": 0, "parse_failure": 0,
                            "unresolved": 0}
                  for stratum in ("head", "rest")}
        decimal_normalized = 0
        resolving_families = set()
        matched_verbatim = set()
        for case_id in all_ids:
            stratum = "head" if case_id in head_set else "rest"
            raw = None
            resolved_in = None
            # Frozen preference: the dictionary's family first, the other
            # tolerated; a file with an unusable data row cannot resolve.
            for family in (expected_family, other_family):
                headers_map, data_row = parsed_files[case_id][family]
                if data_row is None or bound_norm not in headers_map:
                    continue
                verbatim, column = headers_map[bound_norm]
                raw = data_row[column] if column < len(data_row) else ""
                resolved_in = family
                matched_verbatim.add(verbatim)
                break
            if resolved_in is None:
                counts[stratum]["unresolved"] += 1
                continue
            resolving_families.add(resolved_in)
            numeric, label, status = parse_value(variable, raw)
            if status in ("ok", "ok_decimal_normalized"):
                counts[stratum]["nonmissing"] += 1
                values[construct][case_id] = numeric
                if label is not None:
                    labels[construct][case_id] = label
                if status == "ok_decimal_normalized":
                    decimal_normalized += 1
            elif status == "empty":
                counts[stratum]["empty"] += 1
            else:
                counts[stratum]["parse_failure"] += 1
        head_nonmissing = counts["head"]["nonmissing"]
        census_rows.append({
            "construct": construct,
            "bound_field": variable["field"],
            "vtype": variable["vtype"],
            "role": variable["role"],
            "resolved": bool(resolving_families),
            "resolving_families": "+".join(sorted(resolving_families)) or "none",
            "matched_headers_verbatim": "|".join(sorted(matched_verbatim)),
            "head_nonmissing": head_nonmissing,
            "rest_nonmissing": counts["rest"]["nonmissing"],
            "head_empty": counts["head"]["empty"],
            "rest_empty": counts["rest"]["empty"],
            "head_parse_failures": counts["head"]["parse_failure"],
            "rest_parse_failures": counts["rest"]["parse_failure"],
            "head_unresolved": counts["head"]["unresolved"],
            "rest_unresolved": counts["rest"]["unresolved"],
            "decimal_normalized_values": decimal_normalized,
            "insufficient_head_coverage": head_nonmissing < HEAD_COVERAGE_FLOOR,
        })
        emit(f"[census] {construct}: resolved={bool(resolving_families)} "
             f"head_nonmissing={head_nonmissing} "
             f"rest_nonmissing={counts['rest']['nonmissing']}.", log_lines)
    return census_rows, values, labels, file_stats, anomaly_cases


def minimum_set_supported(census_rows):
    by_construct = {row["construct"]: row for row in census_rows}
    def usable(name):
        row = by_construct[name]
        return row["head_nonmissing"] + row["rest_nonmissing"] >= 1
    severity_ok = any(usable(name) for name in MIN_SET_SEVERITY)
    demographic_ok = any(usable(name) for name in MIN_SET_DEMOGRAPHIC)
    return severity_ok and demographic_ok, {"severity_usable": severity_ok,
                                            "demographic_usable": demographic_ok}


# ---------------------------------------------------------------------------
# STEP 4 -- THE ESTIMATION TABLE. Closed statistic menu only. Group
# summaries, level counts with the frozen small-cell suppression, the two
# frozen exploratory uncertainty displays per contrast, the D4 joint support
# display on every row, and per-group missingness. All contrasts are
# computed from unsuppressed internal values; suppression applies to
# displayed cells only and every suppression is logged.
# ---------------------------------------------------------------------------

def quantile(sorted_values, p):
    """Linear interpolation between order statistics at position p*(n-1)
    (the numpy 'linear' convention); frozen for q1/q3 and the relabeling
    central-95% endpoints."""
    n = len(sorted_values)
    if n == 0:
        return None
    if n == 1:
        return float(sorted_values[0])
    position = p * (n - 1)
    low = math.floor(position)
    high = math.ceil(position)
    if low == high:
        return float(sorted_values[low])
    fraction = position - low
    return sorted_values[low] * (1.0 - fraction) + sorted_values[high] * fraction


def median(values):
    return quantile(sorted(values), 0.5) if values else None


def sample_sd(values):
    n = len(values)
    if n < 2:
        return None
    mean = math.fsum(values) / n
    variance = math.fsum((v - mean) ** 2 for v in values) / (n - 1)
    return math.sqrt(variance)


def contrast_value(name, head_vals, rest_vals):
    """The closed contrast menu. Returns a float or None (undefined), with
    undefined reasons handled by the caller. Direction: head minus rest."""
    if not head_vals or not rest_vals:
        return None
    if name == "smd_pooled":
        n1, n2 = len(head_vals), len(rest_vals)
        if n1 < 2 or n2 < 2:
            return None
        s1, s2 = sample_sd(head_vals), sample_sd(rest_vals)
        pooled = math.sqrt(((n1 - 1) * s1 ** 2 + (n2 - 1) * s2 ** 2)
                           / (n1 + n2 - 2))
        if pooled == 0.0:
            return None
        mean1 = math.fsum(head_vals) / n1
        mean2 = math.fsum(rest_vals) / n2
        return (mean1 - mean2) / pooled
    if name == "diff_medians":
        return median(head_vals) - median(rest_vals)
    if name == "rank_biserial":
        # Tie-adjusted Cliff/Mann-Whitney form:
        # (#(head>rest) - #(head<rest)) / (n_head * n_rest); ties count zero;
        # positive = head values larger in the frozen level order.
        greater = sum(1 for h in head_vals for r in rest_vals if h > r)
        less = sum(1 for h in head_vals for r in rest_vals if h < r)
        return (greater - less) / (len(head_vals) * len(rest_vals))
    if name == "diff_prop_F":
        # Values are 1.0 (F) / 0.0 (M), so means are proportions of F.
        return (math.fsum(head_vals) / len(head_vals)
                - math.fsum(rest_vals) / len(rest_vals))
    raise AssertionError(f"unknown contrast {name}")


def uncertainty_displays(name, case_values, head_ids, rest_ids, draws,
                         sorted_ids):
    """The two frozen exploratory displays for one contrast.
    (1) Deterministic leave-one-head-case-out min/max range.
    (2) Central 95% of the contrast under the frozen pseudo-head draws,
        carried under the verbatim hypothetical-exchangeability label."""
    head_vals = [case_values[cid] for cid in head_ids if cid in case_values]
    rest_vals = [case_values[cid] for cid in rest_ids if cid in case_values]
    point = contrast_value(name, head_vals, rest_vals)

    loo_values = []
    loo_undefined = 0
    for omitted in head_ids:
        vals = [case_values[cid] for cid in head_ids
                if cid != omitted and cid in case_values]
        result = contrast_value(name, vals, rest_vals)
        if result is None:
            loo_undefined += 1
        else:
            loo_values.append(result)
    loo = {"min": min(loo_values) if loo_values else None,
           "max": max(loo_values) if loo_values else None,
           "n_defined": len(loo_values), "n_undefined": loo_undefined,
           "label": "deterministic leave-one-head-case-out sensitivity range"}

    aligned = [case_values.get(cid) for cid in sorted_ids]
    relabel_values = []
    for draw in draws:
        head_flags = [False] * len(sorted_ids)
        for index in draw:
            head_flags[index] = True
        pseudo_head = [v for v, flag in zip(aligned, head_flags)
                       if flag and v is not None]
        pseudo_rest = [v for v, flag in zip(aligned, head_flags)
                       if not flag and v is not None]
        result = contrast_value(name, pseudo_head, pseudo_rest)
        if result is not None:
            relabel_values.append(result)
    relabel_values.sort()
    relabeling = {
        "q025": quantile(relabel_values, 0.025),
        "q975": quantile(relabel_values, 0.975),
        "n_defined": len(relabel_values),
        "n_relabelings": len(draws),
        "seed": SEED,
        "label": EXCHANGEABILITY_LABEL,
    }
    return point, loo, relabeling


def format_number(value):
    return "" if value is None else repr(value)


def build_estimation_outputs(census_rows, values, labels, head_ids, rest_ids,
                             support_rows, constants, head_size, log_lines):
    """Builds clinical_estimation_table.csv rows, clinical_uncertainty.json,
    and suppression_log.csv rows."""
    head_set = set(head_ids)
    support_head = sorted(r["support"] for r in support_rows if r["in_head"])
    support_rest = sorted(r["support"] for r in support_rows if not r["in_head"])
    d4 = {
        "head_support_median": median(support_head),
        "rest_support_median": median(support_rest),
        # Frozen Phase-A constants, republished verbatim under D4 only.
        "head_abs_contribution_share_phase_a":
            constants["head_abs_contribution_share"],
        "head_support_share_phase_a": constants["head_support_share"],
    }
    census_by_construct = {row["construct"]: row for row in census_rows}

    # The frozen pseudo-head draws, generated once from the frozen seed over
    # the case ids sorted ascending; shared by every contrast so the display
    # is one coherent reference, not per-variable dice.
    sorted_ids = sorted(head_ids) + sorted(rest_ids)
    sorted_ids.sort()
    rng = random.Random(SEED)
    draws = [rng.sample(range(len(sorted_ids)), head_size)
             for _ in range(RELABELINGS)]

    table_rows = []
    suppression_rows = []
    uncertainty = {"seed": SEED, "n_relabelings": RELABELINGS,
                   "draw_rule": ("random.Random(seed).sample(range(n_cases), "
                                 "head_size) x n_relabelings over case ids "
                                 "sorted ascending; one shared draw set for "
                                 "every contrast"),
                   "quantile_method": ("linear interpolation between order "
                                       "statistics at p*(n-1)"),
                   "exchangeability_label": EXCHANGEABILITY_LABEL,
                   "constructs": {}}

    def add_row(variable, item, level="", head_value="", rest_value="",
                contrast="", note=""):
        row = {"construct": variable["construct"] if variable else "_context",
               "field": variable["field"] if variable else "",
               "vtype": variable["vtype"] if variable else "",
               "role": variable["role"] if variable else "",
               "item": item, "level": level,
               "head_value": head_value, "rest_value": rest_value,
               "contrast_value": contrast, "note": note}
        if variable:
            census = census_by_construct[variable["construct"]]
            row["head_n_nonmissing"] = census["head_nonmissing"]
            row["rest_n_nonmissing"] = census["rest_nonmissing"]
            row["insufficient_head_coverage"] = census["insufficient_head_coverage"]
        else:
            row["head_n_nonmissing"] = ""
            row["rest_n_nonmissing"] = ""
            row["insufficient_head_coverage"] = ""
        row.update({k: (format_number(v) if isinstance(v, float) else v)
                    for k, v in d4.items()})
        table_rows.append(row)

    # Context block (contract: center absence stated; frozen constants
    # republished under their labels; exploratory framing stated once).
    add_row(None, "context_center",
            note="No center/site field is documented in the clinical "
                 "dictionary (Phase-A proposal center.documented=false); the "
                 "mandatory-if-documented clause is discharged by this "
                 "recorded absence.")
    add_row(None, "context_support_shares",
            note=f"D4 joint display: every row carries head/rest eligible-"
                 f"deficit-support medians (B_i, voxels) and the two frozen "
                 f"Phase-A shares. Signed share "
                 f"{constants['signed_head_net_gap_share']!r} is republished "
                 f"in summary context only. {REVERSAL_ACCOUNTING_LABEL}")
    add_row(None, "context_exploratory_status",
            note="All uncertainty displays are exploratory-labeled; no "
                 "p-value is selected, ranked, or headlined; nothing here is "
                 "sampling inference or a separation verdict.")

    for variable in VARIABLES:
        construct = variable["construct"]
        census = census_by_construct[construct]
        case_values = values[construct]
        head_vals = [case_values[cid] for cid in head_ids if cid in case_values]
        rest_vals = [case_values[cid] for cid in rest_ids if cid in case_values]

        head_missing = len(head_ids) - census["head_nonmissing"]
        rest_missing = len(rest_ids) - census["rest_nonmissing"]
        add_row(variable, "n_nonmissing", head_value=census["head_nonmissing"],
                rest_value=census["rest_nonmissing"],
                note=("insufficient_head_coverage"
                      if census["insufficient_head_coverage"] else ""))
        add_row(variable, "n_missing", head_value=head_missing,
                rest_value=rest_missing,
                note="missing = empty + parse failure + unresolved (census)")

        if not census["resolved"]:
            # Contract: a bound variable that resolves nowhere is reported as
            # a fully-missing row, never silently dropped.
            add_row(variable, "fully_missing",
                    note="bound field resolved in no staged member; reported "
                         "per contract, no statistic computable")
            uncertainty["constructs"][construct] = {
                "resolved": False,
                "note": "fully missing; no contrast computed"}
            continue

        if variable["vtype"] == "continuous":
            for group_name, vals in (("head", head_vals), ("rest", rest_vals)):
                n = len(vals)
                stats = {
                    "mean": (math.fsum(vals) / n) if n else None,
                    "sd": sample_sd(vals),
                    "median": median(vals),
                    "q1": quantile(sorted(vals), 0.25),
                    "q3": quantile(sorted(vals), 0.75),
                }
                for item, value in stats.items():
                    matching = [row for row in table_rows
                                if row["construct"] == construct
                                and row["item"] == item]
                    if matching:
                        matching[0][f"{group_name}_value"] = format_number(value)
                    else:
                        add_row(variable, item,
                                head_value=(format_number(value)
                                            if group_name == "head" else ""),
                                rest_value=(format_number(value)
                                            if group_name == "rest" else ""))
        else:
            # Ordinal/binary: per-level counts and (ordinal) cumulative
            # distribution, with the frozen small-cell suppression on head
            # cells: a level with 1 or 2 head cases displays "<3" (0 stays 0).
            level_order = variable["levels"]
            case_labels = labels[construct]
            head_counts = {level: 0 for level in level_order}
            rest_counts = {level: 0 for level in level_order}
            for cid, label in case_labels.items():
                (head_counts if cid in head_set else rest_counts)[label] += 1
            suppressed_levels = set()
            for level in level_order:
                head_count = head_counts[level]
                if head_count in (1, 2):
                    suppressed_levels.add(level)
                    suppression_rows.append({
                        "construct": construct, "level": level, "group": "head",
                        "item": "level_count", "action": "displayed as <3",
                        "reason": "frozen small-cell rule: level contains 1 "
                                  "or 2 head cases"})
                add_row(variable, "level_count", level=level,
                        head_value=("<3" if level in suppressed_levels
                                    else head_count),
                        rest_value=rest_counts[level])
            if variable["vtype"] == "ordinal":
                head_cum = 0
                rest_cum = 0
                for level in level_order:
                    head_cum += head_counts[level]
                    rest_cum += rest_counts[level]
                    if level in suppressed_levels:
                        # Direct-difference guard: publishing this cumulative
                        # would reveal the suppressed level count exactly.
                        suppression_rows.append({
                            "construct": construct, "level": level,
                            "group": "head", "item": "cum_count",
                            "action": "displayed as suppressed",
                            "reason": "adjacent difference would reveal the "
                                      "suppressed level count"})
                        head_display = "suppressed"
                    else:
                        head_display = head_cum
                    add_row(variable, "cum_count", level=level,
                            head_value=head_display, rest_value=rest_cum)
            if variable["vtype"] == "binary":
                for group_name, vals in (("head", head_vals),
                                         ("rest", rest_vals)):
                    if vals:
                        proportion = math.fsum(vals) / len(vals)
                    else:
                        proportion = None
                    display = format_number(proportion)
                    if group_name == "head" and suppressed_levels and vals:
                        # Same-cell protection: with two levels and known n,
                        # the proportion IS the suppressed count in disguise.
                        display = "suppressed"
                        suppression_rows.append({
                            "construct": construct, "level": "F", "group": "head",
                            "item": "proportion_F",
                            "action": "displayed as suppressed",
                            "reason": "derived from a suppressed level count"})
                    matching = [row for row in table_rows
                                if row["construct"] == construct
                                and row["item"] == "proportion_F"]
                    if matching:
                        matching[0][f"{group_name}_value"] = display
                    else:
                        add_row(variable, "proportion_F",
                                head_value=display if group_name == "head" else "",
                                rest_value=display if group_name == "rest" else "",
                                note="proportion of the frozen reference level F")

        entry = {"resolved": True, "contrasts": {}}
        for contrast_name in CONTRASTS_BY_TYPE[variable["vtype"]]:
            point, loo, relabeling = uncertainty_displays(
                contrast_name, case_values, head_ids, rest_ids, draws,
                sorted_ids)
            entry["contrasts"][contrast_name] = {
                "point": point, "loo": loo, "relabeling": relabeling}
            unit_note = ""
            if construct == "mtici_postinterventional" \
                    and contrast_name == "diff_medians":
                unit_note = ("units: frozen level-order steps "
                             "(0<1<2a<2b<2c<3); ")
            note = (f"{unit_note}LOO range "
                    f"[{format_number(loo['min'])}, {format_number(loo['max'])}]"
                    f"; exchangeability reference "
                    f"[{format_number(relabeling['q025'])}, "
                    f"{format_number(relabeling['q975'])}] "
                    f"(exploratory; {EXCHANGEABILITY_LABEL})")
            if point is None:
                note = "contrast undefined at the achieved coverage; " + note
            add_row(variable, f"contrast_{contrast_name}",
                    contrast=format_number(point), note=note)
        uncertainty["constructs"][construct] = entry
        emit(f"[measure] {construct}: contrasts "
             f"{list(entry['contrasts'])} computed with both frozen "
             f"uncertainty displays.", log_lines)

    # The frozen rule suppresses individual displayed cells only; exact group
    # sizes, other exact cells, and mandated contrast values can arithmetically
    # bound a suppressed cell. Recording this is the honest residual of the
    # frozen rule, surfaced for the interpret stage -- no unfrozen additional
    # suppression is applied.
    suppression_rows.append({
        "construct": "_rule", "level": "", "group": "",
        "item": "documented_residual", "action": "disclosure",
        "reason": "cell-level suppression only: published margins and "
                  "mandated contrasts can arithmetically bound a suppressed "
                  "cell; recorded for the interpret stage, no unfrozen "
                  "suppression added"})
    return table_rows, uncertainty, suppression_rows


# ---------------------------------------------------------------------------
# SMOKE FIXTURES. Synthetic stand-ins exercising every code path -- member
# resolution (including the sub-strokecase spelling), staged-tree
# verification with real CRC32s, the census with empty / parse-failure /
# decimal-normalized / out-of-set / duplicate-row / fully-missing paths, the
# estimation table with real suppression -- without an archive, 7z, or any
# real input. Smoke output is always SMOKE_ONLY and can never satisfy a
# contractual gate.
# ---------------------------------------------------------------------------

SMOKE_IDS = [f"sub-stroke{9001 + i:04d}" for i in range(SMOKE_CASES)]
# The smoke split declaration (hard standard 5, smoke leg): the fixture
# deltas in _smoke_contributions are strictly descending except one 0.0 tie
# broken by ascending case_id, so signed-rank order equals id order by
# construction. run() freezes this declaration before the fixture tables
# are hashed or parsed, and verify_split_against_tables() then proves the
# agreement on the loaded fixtures -- the same code path as the real run.
SMOKE_IDS_BY_RANK = tuple(SMOKE_IDS)


def _smoke_contributions(fixture_dir):
    deltas = [0.084, 0.060, 0.048, 0.036, 0.024, 0.018, 0.012,
              0.0, 0.0, -0.012, -0.024, -0.036]
    assert len(deltas) == SMOKE_CASES
    rows = []
    for index, delta in enumerate(deltas):
        band2 = -0.10 - index * 0.01
        rows.append({"case_id": SMOKE_IDS[index], "d_band2": band2,
                     "d_band3": band2 + delta, "delta": (band2 + delta) - band2,
                     "contribution": ((band2 + delta) - band2) / SMOKE_CASES})
    ordered = sorted(rows, key=lambda r: (-r["contribution"], r["case_id"]))
    for position, row in enumerate(ordered, start=1):
        row["signed_rank"] = position
    path = fixture_dir / "per_case_contributions.csv"
    write_csv(path, ["case_id", "d_band2", "d_band3", "delta", "contribution",
                     "signed_rank"], sorted(rows, key=lambda r: r["signed_rank"]))
    return path, rows


def _smoke_support(fixture_dir, contrib_rows):
    ranked = sorted(contrib_rows, key=lambda r: r["signed_rank"])
    support_rows = []
    for index, row in enumerate(ranked):
        support_rows.append({
            "case_id": row["case_id"], "signed_rank": row["signed_rank"],
            "in_head": str(row["signed_rank"] <= SMOKE_HEAD_SIZE),
            "contribution": row["contribution"],
            "abs_contribution": abs(row["contribution"]),
            "eroded_region_voxels": 1500 + 613 * ((index * 5) % 11) + index,
            "rank_abs_contribution": 0, "rank_support": 0, "rank_discrepancy": 0,
        })
    # Fill the rank columns consistently (file-shape parity with the real
    # consumed artifact; Phase B never re-derives ranks).
    by_abs = sorted(support_rows,
                    key=lambda r: (-r["abs_contribution"], r["case_id"]))
    for position, row in enumerate(by_abs, start=1):
        row["rank_abs_contribution"] = position
    by_support = sorted(support_rows,
                        key=lambda r: (-r["eroded_region_voxels"], r["case_id"]))
    for position, row in enumerate(by_support, start=1):
        row["rank_support"] = position
    for row in support_rows:
        row["rank_discrepancy"] = row["rank_abs_contribution"] - row["rank_support"]
    path = fixture_dir / "per_case_support.csv"
    write_csv(path, ["case_id", "signed_rank", "in_head", "contribution",
                     "abs_contribution", "eroded_region_voxels",
                     "rank_abs_contribution", "rank_support", "rank_discrepancy"],
              support_rows)
    return path


def _smoke_expected_constants(support_path):
    rows = []
    with support_path.open(newline="", encoding="utf-8") as handle:
        for raw in csv.DictReader(handle):
            rows.append({"in_head": raw["in_head"] == "True",
                         "contribution": float(raw["contribution"]),
                         "abs_contribution": float(raw["abs_contribution"]),
                         "support": int(raw["eroded_region_voxels"])})
    head = [r for r in rows if r["in_head"]]
    expected = {
        "head_abs_contribution_sum": math.fsum(r["abs_contribution"] for r in head),
        "total_abs_contribution_sum": math.fsum(r["abs_contribution"] for r in rows),
        "head_support_voxels": sum(r["support"] for r in head),
        "total_support_voxels": sum(r["support"] for r in rows),
    }
    expected["head_abs_contribution_share"] = (
        expected["head_abs_contribution_sum"] / expected["total_abs_contribution_sum"])
    expected["head_support_share"] = (
        expected["head_support_voxels"] / expected["total_support_voxels"])
    net = math.fsum(r["contribution"] for r in rows)
    expected["signed_head_net_gap_share"] = (
        math.fsum(r["contribution"] for r in head) / net)
    return expected


def _smoke_freeze(fixture_dir):
    freeze = {
        "constructs": {
            "mrs_3month": {"proposed_field_spelling": "MRS 3 months"},
            "nihss_24h": {"proposed_field_spelling": "NIHSS 24h"},
            "nihss_admission": {"proposed_field_spelling": "NIHSS at admission"},
            "age": {"proposed_field_spelling": "Age"},
            "sex": {"proposed_field_spelling": "Sex"},
        },
        "contextual_proposed": [
            {"construct": "mtici_postinterventional",
             "proposed_field_spelling": "mTici postinterventional"},
            {"construct": "onset_to_imaging_time",
             "proposed_field_spelling": "Onset to door"},
        ],
        "center": {"documented": False},
        "synthetic": True,
    }
    path = fixture_dir / "proposed_variable_freeze.json"
    write_json(path, freeze)
    return path


def _smoke_phenotype(staged_dir, fixture_dir):
    """Synthetic phenotype members with deliberate edge cases:
    - sub-stroke9001 Age '63.0' (decimal normalization tally);
    - sub-stroke9002 Age empty (missingness);
    - sub-stroke9003 members use the sub-strokecase spelling (canonicalization);
    - sub-stroke9004 Onset to door '26:75' (pattern failure);
    - sub-stroke9007 Age 'n/a', sub-stroke9010 Sex 'x' (parse failures);
    - sub-stroke9011 NIHSS at admission '77' (range failure);
    - sub-stroke9005 mTici '2x' (out-of-set -> counted missingness);
    - sub-stroke9012 outcome file carries TWO data rows (file anomaly);
    - 'NIHSS 24h' is bound but appears in no file (fully-missing variable);
    - head mRS 2,2,5 and Sex F,F,M force real small-cell suppression.
    """
    ages = {SMOKE_IDS[0]: "63.0", SMOKE_IDS[1]: "", SMOKE_IDS[2]: "71",
            SMOKE_IDS[3]: "55", SMOKE_IDS[4]: "68", SMOKE_IDS[5]: "74",
            SMOKE_IDS[6]: "n/a", SMOKE_IDS[7]: "61", SMOKE_IDS[8]: "58",
            SMOKE_IDS[9]: "80", SMOKE_IDS[10]: "49", SMOKE_IDS[11]: "66"}
    sexes = {SMOKE_IDS[0]: "F", SMOKE_IDS[1]: "F", SMOKE_IDS[2]: "M",
             SMOKE_IDS[3]: "m", SMOKE_IDS[4]: "F", SMOKE_IDS[5]: "M",
             SMOKE_IDS[6]: "F", SMOKE_IDS[7]: "M", SMOKE_IDS[8]: "F",
             SMOKE_IDS[9]: "x", SMOKE_IDS[10]: "M", SMOKE_IDS[11]: "F"}
    nihss_adm = {SMOKE_IDS[0]: "14", SMOKE_IDS[1]: "9", SMOKE_IDS[2]: "18",
                 SMOKE_IDS[3]: "4", SMOKE_IDS[4]: "11", SMOKE_IDS[5]: "7",
                 SMOKE_IDS[6]: "16", SMOKE_IDS[7]: "2", SMOKE_IDS[8]: "6",
                 SMOKE_IDS[9]: "12", SMOKE_IDS[10]: "77", SMOKE_IDS[11]: "10"}
    onset = {SMOKE_IDS[0]: "1:30", SMOKE_IDS[1]: "0:45", SMOKE_IDS[2]: "12:05",
             SMOKE_IDS[3]: "26:75", SMOKE_IDS[4]: "3:15", SMOKE_IDS[5]: "",
             SMOKE_IDS[6]: "2:00", SMOKE_IDS[7]: "5:40", SMOKE_IDS[8]: "0:55",
             SMOKE_IDS[9]: "8:20", SMOKE_IDS[10]: "1:05", SMOKE_IDS[11]: "4:30"}
    mrs = {SMOKE_IDS[0]: "2", SMOKE_IDS[1]: "2", SMOKE_IDS[2]: "5",
           SMOKE_IDS[3]: "0", SMOKE_IDS[4]: "1", SMOKE_IDS[5]: "3",
           SMOKE_IDS[6]: "4", SMOKE_IDS[7]: "6", SMOKE_IDS[8]: "3",
           SMOKE_IDS[9]: "1", SMOKE_IDS[10]: "4", SMOKE_IDS[11]: "2"}
    mtici = {SMOKE_IDS[0]: "2b", SMOKE_IDS[1]: "2C", SMOKE_IDS[2]: "3",
             SMOKE_IDS[3]: "1", SMOKE_IDS[4]: "2a", SMOKE_IDS[5]: "2x",
             SMOKE_IDS[6]: "0", SMOKE_IDS[7]: "2b", SMOKE_IDS[8]: "3",
             SMOKE_IDS[9]: "2c", SMOKE_IDS[10]: "2a", SMOKE_IDS[11]: "2b"}

    manifest_rows = []
    for index, case_id in enumerate(SMOKE_IDS):
        payload_id = case_id
        if case_id == SMOKE_IDS[2]:
            payload_id = case_id.replace("sub-stroke", "sub-strokecase")
        base_dir = f"train/phenotype/{payload_id}"
        # Headers on one case carry stray spacing to exercise the frozen
        # normalization (trim + casefold + collapse whitespace).
        age_header = " Age " if index == 4 else "Age"
        baseline_path = (f"{base_dir}/ses-01/{payload_id}_ses-01_"
                         f"demographic_baseline.csv")
        baseline_text = (f"{age_header},Sex,NIHSS at admission,Onset to door\n"
                         f"{ages[case_id]},{sexes[case_id]},"
                         f"{nihss_adm[case_id]},{onset[case_id]}\n")
        outcome_path = f"{base_dir}/ses-02/{payload_id}_ses-02_outcome.csv"
        outcome_text = (f"MRS 3 months,mTici postinterventional\n"
                        f"{mrs[case_id]},{mtici[case_id]}\n")
        if case_id == SMOKE_IDS[11]:
            outcome_text += "9,9\n"  # Second data row -> file anomaly.
        for rel, text in ((baseline_path, baseline_text),
                          (outcome_path, outcome_text)):
            full = staged_dir / rel
            full.parent.mkdir(parents=True, exist_ok=True)
            data = text.encode("utf-8")
            full.write_bytes(data)
            manifest_rows.append({"path": rel, "size": len(data),
                                  "crc": format(zlib.crc32(data), "08x")})
    # Decoy manifest rows that must never be resolved or staged.
    manifest_rows.append({"path": "train/derivatives/sub-stroke9001/ses-01/"
                                  "perfusion-maps/decoy_cbf.nii.gz",
                          "size": 12345, "crc": "deadbeef"})
    manifest_rows.append({"path": "train/phenotype/sub-stroke9999/ses-02/"
                                  "sub-stroke9999_ses-02_outcome.csv",
                          "size": 98, "crc": "0badf00d"})
    manifest_path = fixture_dir / "archive_manifest.csv"
    write_csv(manifest_path, ["path", "size", "crc"], manifest_rows)
    return manifest_path


def make_smoke_inputs(output_dir):
    fixture_dir = output_dir.parent / (output_dir.name + ".private-smoke-inputs")
    fixture_dir.mkdir()
    staged_dir = output_dir.parent / (output_dir.name + ".private-staged")
    staged_dir.mkdir()
    contrib_path, contrib_rows = _smoke_contributions(fixture_dir)
    support_path = _smoke_support(fixture_dir, contrib_rows)
    freeze_path = _smoke_freeze(fixture_dir)
    manifest_path = _smoke_phenotype(staged_dir, fixture_dir)
    exclusions_path = fixture_dir / "exclusions.csv"
    write_csv(exclusions_path, ["case_id", "record_type", "reason"],
              [{"case_id": item["case_id"], "record_type": item["record_type"],
                "reason": item.get("reason", "")}
               for item in EXPECTED_BOOKKEEPING])
    census_path = fixture_dir / "census_summary.json"
    write_json(census_path, {"synthetic": True})
    return {"contributions": contrib_path, "support": support_path,
            "freeze": freeze_path, "member_manifest": manifest_path,
            "exclusions": exclusions_path, "census": census_path,
            "staged_dir": staged_dir,
            "expected_constants": _smoke_expected_constants(support_path)}


def environment_record():
    return {
        "python": sys.version,
        "platform": platform.platform(),
        "executable": sys.executable,
        "pid": os.getpid(),
        "dependencies": "Python standard library only (plus the system 7z "
                        "binary for the single real staging event)",
    }


def finalize_determinism_end(output_dir, hash_targets, staged_dir,
                             staged_records, manifest_start):
    """Hard standard 1: re-hash EVERY input (frozen tables, consumed
    artifacts, member manifest, and all staged members -- the latter re-read
    from disk, so a post-staging mutation fails loudly) at the end of every
    registered terminal path and require exact agreement with the start
    manifest."""
    manifest_end = hash_inputs(hash_targets)
    manifest_end["seed"] = manifest_start["seed"]
    manifest_end["smoke"] = manifest_start["smoke"]
    if "staged_members" in manifest_start:
        aggregate = hashlib.sha256()
        for record in staged_records:
            rehashed = sha256_bytes((staged_dir / record["path"]).read_bytes())
            if rehashed != record["sha256"]:
                fail(EXIT_OUTPUT, f"staged member changed after staging: "
                                  f"{record['path']}")
            aggregate.update(f"{record['path']}:{rehashed}\n".encode())
        manifest_end["staged_members"] = {
            "count": len(staged_records),
            "aggregate_sha256": aggregate.hexdigest()}
    if "row_counts" in manifest_start:
        manifest_end["row_counts"] = dict(manifest_start["row_counts"])
    if manifest_end != manifest_start:
        fail(EXIT_OUTPUT, "start and end determinism manifests differ")
    write_json(output_dir / "determinism_manifest_end.json", manifest_end)
    print(json.dumps(manifest_end, sort_keys=True), flush=True)


def staged_aggregate_sha256(staged_records):
    aggregate = hashlib.sha256()
    for record in staged_records:
        aggregate.update(f"{record['path']}:{record['sha256']}\n".encode())
    return aggregate.hexdigest()


# ---------------------------------------------------------------------------
# RUN. The contract's ordered Phase-B steps: authority -> split freeze
# (from the authoring-time declaration, before any outcome-derived table
# is hashed or opened) -> identity gates (including split-agreement
# verification) -> the single staging event -> staged-member verification ->
# schema/missingness census (with the pre-registered stop) -> estimation
# table -> outputs. The end determinism manifest is finalized on every
# registered terminal path.
# ---------------------------------------------------------------------------

def run(args):
    prepare_output_dir(args.output_dir)
    log_lines = []
    emit(f"[authority] Idea 047 Phase {PHASE} (contract v{CONTRACT_VERSION}); "
         f"seed {SEED}; smoke={args.smoke}.", log_lines)
    contract_blob = verify_authority(args.smoke)
    emit(f"[authority] Governing contract blob: {contract_blob}.", log_lines)
    if not args.smoke and (args.archive_file is None
                           or args.member_manifest is None):
        fail(EXIT_AUTHORITY,
             "--archive-file and --member-manifest are required for a "
             "real run: the archive and the frozen member manifest are "
             "pre-staged local inputs; no network access exists anywhere "
             "in this probe")

    expected_cases = SMOKE_CASES if args.smoke else EXPECTED_CASES
    head_size = SMOKE_HEAD_SIZE if args.smoke else HEAD_SIZE

    # SPLIT FREEZE (hard standard 5): the manifest is materialized from the
    # authoring-time declaration and written and hashed BEFORE any
    # outcome-derived table is hashed or opened in this process (in smoke,
    # before the synthetic tables even exist on disk), before the archive
    # is touched, and before any phenotype byte exists on disk.
    ids_by_rank = SMOKE_IDS_BY_RANK if args.smoke else FROZEN_ANALYZED_IDS_BY_RANK
    assert len(ids_by_rank) == expected_cases
    split, head_ids, rest_ids = freeze_split(args.output_dir, ids_by_rank,
                                             head_size, args.smoke)
    emit(f"[split] Frozen strata (predeclared, before any outcome-derived "
         f"table access): {split['head_cases']} head / "
         f"{split['rest_cases']} rest (manifest sha256 "
         f"{split['split_manifest_sha256']}); {split['reserved_cases']} "
         f"reserved cases untouched.", log_lines)

    if args.smoke:
        fixtures = make_smoke_inputs(args.output_dir)
        contrib_path = fixtures["contributions"]
        support_path = fixtures["support"]
        freeze_path = fixtures["freeze"]
        member_manifest_path = fixtures["member_manifest"]
        exclusions_path = fixtures["exclusions"]
        census_path = fixtures["census"]
        expected_constants = fixtures["expected_constants"]
        hash_targets = {"per_case_contributions.csv": contrib_path,
                        "per_case_support.csv": support_path,
                        "proposed_variable_freeze.json": freeze_path,
                        "archive_manifest.csv": member_manifest_path,
                        "exclusions.csv": exclusions_path,
                        "census_summary.json": census_path}
    else:
        contrib_path = CONTRIB_PATH
        support_path = SUPPORT_PATH
        freeze_path = FREEZE_PATH
        member_manifest_path = args.member_manifest
        exclusions_path = EXCLUSIONS_PATH
        census_path = CENSUS_PATH
        expected_constants = FROZEN_PHASE_A_CONSTANTS
        hash_targets = {"per_case_contributions.csv": contrib_path,
                        "per_case_support.csv": support_path,
                        "proposed_variable_freeze.json": freeze_path,
                        "archive_manifest.csv": member_manifest_path,
                        "exclusions.csv": exclusions_path,
                        "census_summary.json": census_path,
                        "phase_a_resolved_config.json": BUNDLE_RESOLVED_CONFIG}

    # STEP 1 -- identity gates on every pinned input and consumed artifact.
    # The outcome-derived tables are hashed and opened only now, with the
    # split manifest already frozen on disk.
    emit("[identity] Hashing all frozen inputs and consumed Phase-A artifacts.",
         log_lines)
    manifest_start = hash_inputs(hash_targets)
    manifest_start["seed"] = SEED
    manifest_start["smoke"] = args.smoke
    verify_input_pins(manifest_start, args.smoke)
    contrib_rows = load_contributions(contrib_path, expected_cases)
    support_rows = load_support(support_path, expected_cases, head_size)
    verify_split_against_tables(ids_by_rank, head_size, contrib_rows,
                                support_rows)
    recomputed_constants = verify_phase_a_constants(
        support_rows, contrib_rows, head_size, expected_constants)
    freeze_check = verify_freeze_bindings(freeze_path, args.smoke)
    emit(f"[identity] All pins verified; loaded tables agree exactly with "
         f"the predeclared split; all "
         f"{len(expected_constants)} frozen Phase-A constants recomputed "
         f"exactly; bound variable list matches the machine proposal.",
         log_lines)
    write_json(args.output_dir / "determinism_manifest_start.json", manifest_start)
    print(json.dumps(manifest_start, sort_keys=True), flush=True)

    # STEP 2 -- the single selective staging event.
    analyzed_ids = sorted(head_ids) + sorted(rest_ids)
    members, spellings = resolve_members(member_manifest_path, analyzed_ids)
    member_paths = sorted(info["path"] for families in members.values()
                          for info in families.values())
    assert len(member_paths) == 2 * len(analyzed_ids)
    assert len(set(member_paths)) == len(member_paths)
    emit(f"[staging] Resolved {len(member_paths)} members for "
         f"{len(analyzed_ids)} cases from the frozen manifest "
         f"(payload spellings seen: {spellings}).", log_lines)

    staging_started = time.monotonic()
    if args.smoke:
        staged_dir = args.output_dir.parent / (args.output_dir.name + ".private-staged")
        archive_receipt = {"mode": "smoke_synthetic_staging",
                           "note": "fixtures pre-staged; no archive, no 7z; "
                                   "verification below is real"}
        extraction_receipt = {"mode": "smoke_synthetic_staging"}
    else:
        staged_dir = args.output_dir.parent / (args.output_dir.name + ".private-staged")
        archive_md5 = verify_archive_identity(args.archive_file, log_lines)
        archive_receipt = {"mode": "real",
                           "path": str(args.archive_file.resolve()),
                           "bytes": ARCHIVE_BYTES, "md5": archive_md5,
                           "md5_pin_matched": True,
                           "zenodo_record_declared": ZENODO_RECORD}
        extraction_receipt = extract_members(
            args.sevenzip, args.archive_file, staged_dir, member_paths,
            args.output_dir, log_lines)
    staged_records = verify_staged_members(staged_dir, members, log_lines)
    staging_seconds = time.monotonic() - staging_started
    staging_audit = {
        "zenodo_record_pin": ZENODO_RECORD,
        "archive": archive_receipt,
        "member_manifest": {"path": str(Path(member_manifest_path).resolve()),
                            "sha256": manifest_start["archive_manifest.csv"]["sha256"],
                            "git_blob_pin": MEMBER_MANIFEST_BLOB},
        "extraction": extraction_receipt,
        "resolved_member_count": len(member_paths),
        "payload_spellings_seen": spellings,
        "staged_member_verification": staged_records,
        "staging_seconds": round(staging_seconds, 3),
        "d3_restriction": ("only the 198 phenotype members of the 99 analyzed "
                           "census cases were staged; no imaging member, no "
                           "reserved case, no excluded case"),
    }
    write_json(args.output_dir / "staging_audit.json", staging_audit)
    manifest_start["staged_members"] = {
        "count": len(staged_records),
        "aggregate_sha256": staged_aggregate_sha256(staged_records)}
    write_json(args.output_dir / "determinism_manifest_start.json", manifest_start)
    emit(f"[staging] Staging complete and receipted in {staging_seconds:.1f}s; "
         f"the 15-minute post-staging analysis wall starts now.", log_lines)
    analysis_started = time.monotonic()

    def check_wall(stage):
        elapsed = time.monotonic() - analysis_started
        if elapsed > POST_STAGING_WALL_SECONDS:
            fail(EXIT_WALL, f"post-staging wall cap exceeded after {stage} "
                            f"({elapsed:.0f}s > {POST_STAGING_WALL_SECONDS}s); "
                            f"an incomplete run is invalid, not a negative")

    # STEP 3 -- the pre-registered schema/missingness census.
    emit("[census] Running the phenotype schema/missingness census "
         "(counts only; no clinical value is written).", log_lines)
    census_rows, values, labels, file_stats, anomaly_cases = census_and_values(
        members, staged_dir, head_ids, rest_ids, log_lines)
    census_fields = ["construct", "bound_field", "vtype", "role", "resolved",
                     "resolving_families", "matched_headers_verbatim",
                     "head_nonmissing", "rest_nonmissing", "head_empty",
                     "rest_empty", "head_parse_failures", "rest_parse_failures",
                     "head_unresolved", "rest_unresolved",
                     "decimal_normalized_values", "insufficient_head_coverage"]
    write_csv(args.output_dir / "phenotype_schema_census.csv", census_fields,
              census_rows)
    per_case_rows = []
    for case_id in sorted(file_stats):
        stratum = "head" if case_id in set(head_ids) else "rest"
        row = {"case_id": case_id, "stratum": stratum}
        for family in ("baseline", "outcome"):
            stats = file_stats[case_id][family]
            row[f"{family}_member"] = stats["member"]
            row[f"{family}_data_row_usable"] = stats["data_row_usable"]
            row[f"{family}_anomalies"] = stats["anomalies"]
        per_case_rows.append(row)
    write_csv(args.output_dir / "per_case_staging.csv",
              ["case_id", "stratum", "baseline_member", "baseline_data_row_usable",
               "baseline_anomalies", "outcome_member", "outcome_data_row_usable",
               "outcome_anomalies"], per_case_rows)
    exclusion_log = [{"case_id": item["case_id"],
                      "record_type": item["record_type"],
                      "reason": item["reason"]} for item in EXPECTED_BOOKKEEPING]
    exclusion_log += [{"case_id": item["case_id"],
                       "record_type": f"file_anomaly_{item['family']}",
                       "reason": item["anomaly"]} for item in anomaly_cases]
    write_csv(args.output_dir / "probe_exclusions.csv",
              ["case_id", "record_type", "reason"], exclusion_log)
    manifest_start["row_counts"] = {
        "per_case_contributions.csv": len(contrib_rows),
        "per_case_support.csv": len(support_rows),
        "staged_members": len(staged_records),
        "census_variables": len(census_rows)}
    write_json(args.output_dir / "determinism_manifest_start.json", manifest_start)
    check_wall("census")

    supported, min_set_detail = minimum_set_supported(census_rows)
    resolved = {
        "idea_id": IDEA_ID, "contract_version": CONTRACT_VERSION, "phase": PHASE,
        "contract_blob": contract_blob, "seed": SEED,
        "relabelings": RELABELINGS, "variants": 1, "gpu_minutes": 0,
        "inputs": {name: value for name, value in manifest_start.items()
                   if isinstance(value, dict) and "sha256" in value},
        "consumed_phase_a": {
            "bundle_dir": str(BUNDLE_DIR),
            "bundle_commit": PHASE_A_BUNDLE_COMMIT,
            "governing_blob": GOVERNING_PHASE_A_BLOB,
            "freeze_bindings_check": freeze_check,
            "constants_recomputed_exactly": sorted(recomputed_constants)},
        "archive": staging_audit["archive"],
        "output_dir": str(args.output_dir.resolve()),
        "cli": {"archive_file": str(args.archive_file) if args.archive_file else None,
                "member_manifest": str(args.member_manifest)
                                   if args.member_manifest else None,
                "sevenzip": args.sevenzip},
    }
    write_json(args.output_dir / "resolved_config.json", resolved)
    input_rows = [{"input": name, "path": value["path"], "sha256": value["sha256"],
                   "role": ("member_manifest" if name == "archive_manifest.csv"
                            else "consumed_phase_a_artifact"
                            if name in ("per_case_support.csv",
                                        "proposed_variable_freeze.json",
                                        "phase_a_resolved_config.json")
                            else "frozen_input")}
                  for name, value in manifest_start.items()
                  if isinstance(value, dict) and "sha256" in value]
    input_rows.append({"input": ARCHIVE_NAME,
                       "path": staging_audit["archive"].get("path", "smoke:none"),
                       "sha256": f"md5:{staging_audit['archive'].get('md5', 'n/a')}",
                       "role": "held_archive_md5_gate"})
    write_csv(args.output_dir / "input_manifest.csv",
              ["input", "path", "sha256", "role"], input_rows)

    if not supported:
        # PRE-REGISTERED DECISION-GRADE STOP: the census and staging audit
        # are the deliverable; no clinical estimation output exists on this
        # path by design; escalation is the next act.
        summary = {
            "idea_id": IDEA_ID, "phase": PHASE,
            "status": "PHENOTYPE_SCHEMA_MISMATCH", "smoke": args.smoke,
            "analyzed_cases": len(analyzed_ids), "head_size": head_size,
            "staged_members": len(staged_records),
            "minimum_set": min_set_detail,
            "census": {row["construct"]: {"resolved": row["resolved"],
                                          "head_nonmissing": row["head_nonmissing"],
                                          "rest_nonmissing": row["rest_nonmissing"]}
                       for row in census_rows},
            "reserved_cases_accessed": 0,
            "note": ("Pre-registered decision-grade stop, not a negative and "
                     "not invalidating: the staged case-level rows cannot "
                     "support the minimum variable set; the schema census and "
                     "staging audit are the deliverable and escalation is the "
                     "next act."),
        }
        write_json(args.output_dir / "summary.json", summary)
        write_json(args.output_dir / "environment.txt", environment_record())
        finalize_determinism_end(args.output_dir, hash_targets, staged_dir,
                                 staged_records, manifest_start)
        emit(json.dumps(summary, indent=2, sort_keys=True), log_lines)
        emit("Plain-language template: PHENOTYPE_SCHEMA_MISMATCH means the "
             "released case-level clinical rows do not carry the minimum "
             "bound variable set. This is the pre-registered stop -- a "
             "decision-grade description for escalation, not a negative "
             "result and not a validity failure. No clinical table exists "
             "and no separation statement of any kind is licensed.", log_lines)
        (args.output_dir / "run_log.txt").write_text("\n".join(log_lines) + "\n",
                                                     encoding="utf-8")
        return EXIT_SCHEMA_STOP

    # STEP 4 -- the single aggregate estimation table.
    emit(f"[measure] Census supports the minimum set; computing the single "
         f"{head_size}-versus-{len(rest_ids)} estimation table "
         f"({RELABELINGS} frozen relabelings per contrast); variant 1/1.",
         log_lines)
    table_rows, uncertainty, suppression_rows = build_estimation_outputs(
        census_rows, values, labels, head_ids, rest_ids, support_rows,
        expected_constants, head_size, log_lines)
    table_fields = ["construct", "field", "vtype", "role", "item", "level",
                    "head_value", "rest_value", "contrast_value",
                    "head_n_nonmissing", "rest_n_nonmissing",
                    "insufficient_head_coverage", "head_support_median",
                    "rest_support_median", "head_abs_contribution_share_phase_a",
                    "head_support_share_phase_a", "note"]
    write_csv(args.output_dir / "clinical_estimation_table.csv", table_fields,
              table_rows)
    write_json(args.output_dir / "clinical_uncertainty.json", uncertainty)
    write_csv(args.output_dir / "suppression_log.csv",
              ["construct", "level", "group", "item", "action", "reason"],
              suppression_rows)
    check_wall("estimation table")

    if args.smoke:
        # The synthetic world must have exercised every edge path for real.
        census_by = {row["construct"]: row for row in census_rows}
        assert not census_by["nihss_24h"]["resolved"], \
            "smoke must exercise the fully-missing variable path"
        assert any(row["item"] == "fully_missing" for row in table_rows)
        assert any(row["decimal_normalized_values"] for row in census_rows)
        assert any(row["head_parse_failures"] + row["rest_parse_failures"]
                   for row in census_rows)
        assert len(anomaly_cases) == 1, anomaly_cases
        assert "sub-strokecase" in spellings
        assert any(row["action"] == "displayed as <3"
                   for row in suppression_rows)
        assert supported

    status = "SMOKE_ONLY" if args.smoke else "STUDY_COMPLETE"
    suppressed_cells = sum(1 for row in suppression_rows
                           if row["item"] != "documented_residual")
    summary = {
        "idea_id": IDEA_ID, "phase": PHASE, "status": status, "smoke": args.smoke,
        "analyzed_cases": len(analyzed_ids), "head_size": head_size,
        "staged_members": len(staged_records),
        "phenotype_files_parsed": len(staged_records),
        "minimum_set": min_set_detail,
        "census": {row["construct"]: {"resolved": row["resolved"],
                                      "head_nonmissing": row["head_nonmissing"],
                                      "rest_nonmissing": row["rest_nonmissing"],
                                      "insufficient_head_coverage":
                                          row["insufficient_head_coverage"]}
                   for row in census_rows},
        "suppressed_cells": suppressed_cells,
        "file_anomalies": len(anomaly_cases),
        "center_documented": False,
        "support_constants_of_record": {
            **{k: v for k, v in expected_constants.items()},
            "labels": {"signed_head_net_gap_share": REVERSAL_ACCOUNTING_LABEL,
                       "shares": ("exact Phase-A arithmetic of record, "
                                  "realized cohort only; no proportionality "
                                  "verdict")}},
        "reserved_cases_accessed": 0,
        "residual_disclosure": ("cell-level suppression only: published "
                                "margins and mandated contrasts can "
                                "arithmetically bound a suppressed cell; see "
                                "suppression_log.csv"),
        "primary_output": "clinical_estimation_table.csv",
        "staging_seconds": round(staging_seconds, 3),
        "analysis_seconds": round(time.monotonic() - analysis_started, 3),
    }
    write_json(args.output_dir / "summary.json", summary)
    write_json(args.output_dir / "environment.txt", environment_record())
    finalize_determinism_end(args.output_dir, hash_targets, staged_dir,
                             staged_records, manifest_start)

    emit(json.dumps(summary, indent=2, sort_keys=True), log_lines)
    if status == "STUDY_COMPLETE":
        interpretation = (
            "Plain-language template: STUDY_COMPLETE means staging, census, "
            "and estimation-table requirements all passed and the single "
            "frozen clinical estimation table was emitted -- a successful "
            "descriptive result regardless of what it shows. It carries no "
            "separation verdict, no clinical-silence or clinical-markedness "
            "reading, and no proportionality verdict. Group differences are "
            "aggregate estimates with exploratory-labeled uncertainty for "
            "these 99 realized cases only; if no separation larger than the "
            "displayed exploratory ranges was observed, that is a bounded "
            "statement at the achieved precision, never evidence of clinical "
            "silence. Next act: record-result, then the interpret stage.")
    else:
        interpretation = ("Plain-language template: SMOKE_ONLY exercises the "
                          "harness on synthetic fixtures and can never satisfy "
                          "a contractual gate.")
    emit(interpretation, log_lines)
    (args.output_dir / "run_log.txt").write_text("\n".join(log_lines) + "\n",
                                                 encoding="utf-8")
    return 0


def main():
    args = parse_args()
    try:
        return run(args)
    except ProbeFailure as exc:
        print(f"PROBE FAILURE exit={exc.code}: {exc}", file=sys.stderr, flush=True)
        return exc.code
    except Exception:
        # Full traceback to stderr so harness faults are diagnosable from the
        # persisted console log (2026-08-15 revision-spec lesson).
        traceback.print_exc()
        return EXIT_INTERNAL


if __name__ == "__main__":
    raise SystemExit(main())
