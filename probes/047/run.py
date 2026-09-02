#!/usr/bin/env python3
"""Idea 047, Phase A: keystone-ten support-share arithmetic and dictionary freeze.

This experiment is the phenotype-blind first phase of the approved
ideas/047/probe_contract.yaml (contract version 2). It reads three pinned,
already-imported program tables -- the take-13 exclusions table carrying the
exact eligible-deficit-support voxel count B_i for all 99 analyzed census
cases, the idea-046 per-case contribution table, and the idea-046 census
summary -- and emits the contract's frozen support clause: the frozen
signed-rank top ten's share of total absolute contribution displayed beside
their share of total eligible deficit support, the casewise rank-discrepancy
distribution, and a descriptive Spearman rho. It then stages and inventories
the 12 kB clinical data dictionary (the only staging transport permitted in
this phase) and derives a machine-proposed clinical variable freeze for the
human amendment. No archive member, no perfusion map, no phenotype row, and
no case-level clinical byte is touched; probes/023/results/results_v2/
per_patient.csv is untouchable by construction.

Primary Phase-A product: the exact share pair for the realized 99 cases,
plus the dictionary inventory and proposed variable freeze. Stopping rule:
stop after the required Phase-A outputs are written (wall cap 10 minutes) or
at the first failure. A positive result is PHASE_A_COMPLETE_REQUIRES_AMENDMENT
(all gates passed; support clause emitted; dictionary supports the minimum
variable set) -- successful regardless of the share values, carrying no
proportionality verdict. PHASE_A_COMPLETE_CLINICAL_UNSUPPORTED is the
pre-registered branch when the dictionary cannot support the minimum set;
the support clause is still delivered. NO DIRECTIONAL NEGATIVE IS DEFINED:
SUPPORT_PROVENANCE_FAILURE (exit 4) is a pre-registered decision-grade stop
for escalation, not a negative and not invalidating.

Run (Phase A, after human approval; fetches only the 12 kB dictionary):
    python probes/047/run.py --output-dir /path/to/new/output
Run with a held dictionary copy (no network at all):
    python probes/047/run.py --output-dir OUT --dictionary-file /path/to/clinical_data-description.xlsx
Smoke (synthetic fixtures, no real inputs, no network, never a gate):
    python probes/047/run.py --smoke --output-dir /tmp/probe-047-smoke

Exit codes: 0 valid completion (PHASE_A_COMPLETE_REQUIRES_AMENDMENT,
PHASE_A_COMPLETE_CLINICAL_UNSUPPORTED, or SMOKE_ONLY); 2 authority/CLI;
3 input identity (pin, blob, or dictionary md5 mismatch); 4 pre-registered
support-provenance stop; 5 census cross-check (invalidating transcription);
6 scope/blindness; 7 output/determinism; 8 wall time; 12 unexpected harness
fault (full traceback to stderr).
"""

import argparse
import csv
import hashlib
import json
import math
import os
import platform
import re
import sys
import time
import traceback
import zipfile
from pathlib import Path
from xml.etree import ElementTree


IDEA_ID = "idea-047"
CONTRACT_VERSION = 2
PHASE = "A"
# Contract's single frozen seed. Phase A is fully deterministic and uses no
# randomness; the seed is declared so the harness state is explicit.
SEED = 20260902
EXPECTED_CASES = 99        # The frozen take-13 census cohort.
HEAD_SIZE = 10             # The frozen signed-rank top ten.
SMOKE_CASES = 12           # Synthetic smoke cohort size.
SMOKE_HEAD_SIZE = 3        # Smoke head; smoke can never satisfy a gate.
WALL_SECONDS = 10 * 60     # Contract Phase-A CPU wall-time cap.

PROBE_DIR = Path(__file__).resolve().parent
REPO_ROOT = PROBE_DIR.parent.parent
CONTRACT_PATH = REPO_ROOT / "ideas/047/probe_contract.yaml"
APPROVAL_PATH = REPO_ROOT / "ideas/047/HUMAN_APPROVED_PROBE"

# Frozen inputs (contract dataset.frozen_inputs). Paths are constants: the
# contract pins these exact repository artifacts, so no CLI override exists.
EXCLUSIONS_PATH = REPO_ROOT / "probes/023/results/results_v2/exclusions.csv"
CONTRIB_PATH = REPO_ROOT / "probes/046/results/results_v3/per_case_contributions.csv"
CENSUS_PATH = REPO_ROOT / "probes/046/results/results_v3/census_summary.json"
TAKE13_RUNPY_PATH = REPO_ROOT / "probes/023/run.py"

EXPECTED_EXCLUSIONS_SHA256 = "58e9f8ab7cea38e6717319a26ea6a590dc7d1ad0d42d6b30dca648b0509a5a71"
EXPECTED_CONTRIB_SHA256 = "aba525122f796618761e6c4d29b664647760e8dff4987932c3ff6ab5456faae9"
EXPECTED_CENSUS_SHA256 = "189c0ce846cffd2eff76e896bfa35156893568d5ee64868caae0b8609bd4c761"
# The frozen take-13 implementation is byte-verified evidence, never executed.
EXPECTED_TAKE13_BLOB = "0e9a40b453b6d4b653841d6ea70f2e4b75cce9be"
# coordinate_arrays() spans these lines at the pinned blob; the span is
# recorded verbatim in resolved_config.json per contract preprocessing step 1.
COORD_SPAN = (486, 523)

# Dictionary pin (contract dataset.dictionary). The URL names the immutable
# child record directly; it is a declared constant and never re-resolved
# (2026-08-25 lesson: a pin that can re-resolve at runtime is not a pin).
DICT_URL = "https://zenodo.org/records/16813698/files/clinical_data-description.xlsx?download=1"
DICT_MD5 = "c8d806a021614c6bb9f732756f9701d4"
DICT_BYTES = 12149
DICT_NAME = "clinical_data-description.xlsx"

# Census cross-check constants (contract preprocessing step 3), frozen from
# the ratified idea-046 census. Any recomputed disagreement is invalidating.
EXPECTED_HEAD_ABS_SHARE = 0.5063509495830807
EXPECTED_HEAD_SIGNED_SHARE = 0.7928912778985707
EXPECTED_SIGN_COUNTS = {"positive": 54, "zero": 6, "negative": 39}

# Drafting-time support fingerprint (contract baselines): lineage evidence
# only, recorded as information, explicitly NOT a runtime gate.
DRAFTING_B_MIN = 1401
DRAFTING_B_MAX = 617540

# The provenance gate's expected non-analyzed remainder (contract step 2d):
# exactly these two documented bookkeeping rows, nothing else.
EXPECTED_BOOKKEEPING = [
    {"case_id": "sub-stroke0142", "record_type": "excluded_archive_lesion"},
    {"case_id": "sub-stroke0043", "record_type": "excluded_case",
     "reason": "source_corrupt_member"},
]
SUPPORT_FIELDS = ["deficit_voxels", "eroded_region_voxels", "vessel_voxels",
                  "vessel_cbv_p98", "nonfinite_cbf_voxels", "nonfinite_cbv_voxels",
                  "nonfinite_mtt_voxels", "nonfinite_tmax_voxels"]

# Blindness guard (contract invalidating_failures): these may never be read.
FORBIDDEN_PATH_FRAGMENTS = ("per_patient.csv", "/phenotype/", "outcome.csv",
                            "demographic_baseline.csv")

# Frozen targeting rule (contract preprocessing.targeting_rule). A construct
# maps to a dictionary cell when every regex in its list matches the cell
# text. The freeze proposal lists every matching cell; the human amendment
# binds the final list, so over-matching is visible, never silently decisive.
TARGET_CONSTRUCTS = [
    ("mrs_3month", "primary outcome (3-month mRS)", [r"(?i)\bmrs\b", r"3"]),
    ("nihss_24h", "lineage-preserving severity (idea-046 frozen optional rung)",
     [r"(?i)nihss", r"24"]),
    ("nihss_admission", "baseline-severity context; never interchangeable with 24h",
     [r"(?i)nihss", r"(?i)admiss"]),
    ("age", "demographic", [r"(?i)\bage\b"]),
    ("sex", "demographic", [r"(?i)\bsex\b"]),
]
# At most two contextual fields, proposed only if documented, in this order.
CONTEXTUAL_CANDIDATES = [
    ("mtici_postinterventional", [r"(?i)tici"]),
    ("onset_to_imaging_time", [r"(?i)onset"]),
]
CONTEXTUAL_CAP = 2
# Center/site is mandatory context OUTSIDE the cap if documented.
CENTER_REGEXES = [r"(?i)\bcent(?:er|re)\b|\bsite\b"]
# Minimum usable set (contract step 5 pre-registered branch): at least one of
# (3-month mRS | any documented NIHSS time point) AND one of (age | sex).
ANY_NIHSS_REGEX = r"(?i)nihss"

EXIT_AUTHORITY = 2
EXIT_INPUT = 3
EXIT_SUPPORT_STOP = 4
EXIT_CROSSCHECK = 5
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
    """Blindness guard: refuse to touch phenotype or the forbidden table."""
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


def md5_bytes(data):
    return hashlib.md5(data).hexdigest()


def git_blob(path):
    data = read_bytes_checked(path)
    return hashlib.sha1(f"blob {len(data)}\0".encode("ascii") + data).hexdigest()


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_csv(path, fieldnames, rows):
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def emit(message, log_lines):
    print(message, flush=True)
    log_lines.append(message)


def parse_args():
    parser = argparse.ArgumentParser(description="Idea 047 Phase A probe")
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--dictionary-file", type=Path, default=None,
                        help="Held copy of clinical_data-description.xlsx; "
                             "when absent the pinned record-file URL is fetched "
                             "(the only permitted network act, 12 kB).")
    parser.add_argument("--smoke", action="store_true")
    return parser.parse_args()


# ---------------------------------------------------------------------------
# AUTHORITY. Phase A runs only under a human approval marker binding the
# exact current contract blob, and the contract must carry the frozen
# implementation literals this file encodes. Smoke skips approval entirely
# and can never satisfy a contractual gate.
# ---------------------------------------------------------------------------

CONTRACT_LITERALS = [
    "contract_version: 2",
    "maximum_variants: 1",
    "maximum_gpu_minutes: 0",
    "maximum_seeds: 1",
    "PHASE_A_COMPLETE_REQUIRES_AMENDMENT",
    "PHASE_A_COMPLETE_CLINICAL_UNSUPPORTED",
    "SUPPORT_PROVENANCE_FAILURE",
    "NO DIRECTIONAL NEGATIVE IS DEFINED",
    "20260902",
    EXPECTED_EXCLUSIONS_SHA256,
    EXPECTED_CONTRIB_SHA256,
    EXPECTED_CENSUS_SHA256,
    EXPECTED_TAKE13_BLOB,
    DICT_MD5,
    "0.5063509495830807",
    "0.7928912778985707",
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
    if "frozen_variable_list: \"<<TO_BE_FROZEN_AT_AMENDMENT>>\"" not in text:
        # This file implements the PRE-amendment interface only; an amended
        # contract must go back through probe-build, never run this code.
        fail(EXIT_AUTHORITY, "contract no longer carries the pre-amendment sentinel; "
                             "this Phase-A implementation does not govern it")
    return actual


def prepare_output_dir(path):
    path.mkdir(parents=True, exist_ok=True)
    if any(path.iterdir()):
        fail(EXIT_OUTPUT, "output directory must be empty")


# ---------------------------------------------------------------------------
# SPLIT FREEZE. Written before ANY input file is opened. Phase A opens no
# outcome or label file at all, and the 49 reserved cases plus excluded
# sub-stroke0043 are never touched; this manifest freezes those counts first
# so the discipline is checkable from the bundle.
# ---------------------------------------------------------------------------

def freeze_split(output_dir, expected_cases, smoke):
    rows = [{"anonymous_sample": index + 1, "split": "analyzed_census"}
            for index in range(expected_cases)]
    write_csv(output_dir / "split_manifest.csv", ["anonymous_sample", "split"], rows)
    record = {
        "created_before_any_input_open": True,
        "analyzed_census_cases": expected_cases,
        "reserved_cases": 0 if smoke else 49,
        "reserved_cases_accessed": 0,
        # One source-corrupt excluded case (sub-stroke0043); the smoke fixture
        # mirrors this bookkeeping structure, so the count holds in both modes.
        "excluded_source_corrupt_cases": 1,
        "phenotype_rows_opened": 0,
        "seed": SEED,
        "smoke": smoke,
        "split_manifest_sha256": sha256_file(output_dir / "split_manifest.csv"),
    }
    write_json(output_dir / "split_manifest.json", record)
    assert record["reserved_cases_accessed"] == 0
    assert record["phenotype_rows_opened"] == 0
    return record


# ---------------------------------------------------------------------------
# INPUT IDENTITY (contract step 1). Hash every frozen input against its pin
# and byte-verify the take-13 implementation blob; extract the verbatim
# coordinate_arrays() lines as evidence of what eroded_region_voxels means.
# The code is evidence, never executed.
# ---------------------------------------------------------------------------

def hash_inputs(paths):
    manifest = {}
    for name, path in paths.items():
        if not path.is_file():
            fail(EXIT_INPUT, f"missing frozen input: {path}")
        manifest[name] = {"path": str(path.resolve()), "sha256": sha256_file(path)}
    return manifest


def verify_input_identity(manifest, take13_path, smoke):
    if not smoke:
        pins = {"exclusions.csv": EXPECTED_EXCLUSIONS_SHA256,
                "per_case_contributions.csv": EXPECTED_CONTRIB_SHA256,
                "census_summary.json": EXPECTED_CENSUS_SHA256}
        for name, expected in pins.items():
            if manifest[name]["sha256"] != expected:
                fail(EXIT_INPUT, f"{name} SHA-256 {manifest[name]['sha256']} "
                                 f"differs from pin {expected}")
        blob = git_blob(take13_path)
        if blob != EXPECTED_TAKE13_BLOB:
            fail(EXIT_INPUT, f"probes/023/run.py blob {blob} differs from pin "
                             f"{EXPECTED_TAKE13_BLOB}")


def extract_coordinate_lines(take13_path, smoke):
    lines = take13_path.read_text(encoding="utf-8").splitlines()
    def_indices = [i for i, line in enumerate(lines, start=1)
                   if line.startswith("def coordinate_arrays(")]
    if len(def_indices) != 1:
        fail(EXIT_INPUT, "coordinate_arrays() not uniquely located in the frozen code")
    start = def_indices[0]
    end = next((i for i, line in enumerate(lines[start:], start=start + 1)
                if line.strip().startswith("return ")), None)
    if end is None:
        fail(EXIT_INPUT, "coordinate_arrays() has no return line")
    span = lines[start - 1:end]
    if "eroded_region_voxels" not in "\n".join(span):
        fail(EXIT_INPUT, "extracted coordinate_arrays() lines do not define "
                         "eroded_region_voxels")
    if not smoke and (start, end) != COORD_SPAN:
        fail(EXIT_INPUT, f"coordinate_arrays() spans lines {start}-{end}, "
                         f"expected frozen {COORD_SPAN}")
    return {"source_lines": [start, end], "verbatim": span}


# ---------------------------------------------------------------------------
# LOAD + SUPPORT PROVENANCE GATE (contract step 2). The exclusions table must
# yield exactly the 99 analyzed cases with a finite positive integer B_i
# each, set-equal to the contribution table, with the only non-analyzed rows
# the two documented bookkeeping rows. Failure here is the pre-registered
# decision-grade stop SUPPORT_PROVENANCE_FAILURE, not a negative result.
# ---------------------------------------------------------------------------

def load_exclusions(path):
    with check_path_allowed(path).open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None or "record_type" not in reader.fieldnames \
                or "eroded_region_voxels" not in reader.fieldnames:
            fail(EXIT_INPUT, "exclusions.csv lacks required columns")
        rows = list(reader)
    assert rows, "exclusions.csv has no data rows"
    return rows


def load_contributions(path, expected_cases):
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
    # signed_rank must be the 1..N permutation produced by the frozen census
    # ordering (contribution descending, case_id ascending tie rule).
    if sorted(row["signed_rank"] for row in rows) != list(range(1, expected_cases + 1)):
        fail(EXIT_INPUT, "signed_rank is not a 1..N permutation")
    frozen_order = sorted(rows, key=lambda r: (-r["contribution"], r["case_id"]))
    for position, row in enumerate(frozen_order, start=1):
        if row["signed_rank"] != position:
            fail(EXIT_INPUT, f"signed_rank disagrees with the frozen ordering at "
                             f"position {position} ({row['case_id']})")
    # The census identity: delta = band3 - band2 and contribution = delta / N,
    # exactly as the ratified idea-046 code computed them.
    for row in rows:
        assert row["delta"] == row["d_band3"] - row["d_band2"], row["case_id"]
        assert row["contribution"] == row["delta"] / expected_cases, row["case_id"]
    return rows


def support_provenance_gate(exclusion_rows, contrib_rows, expected_cases):
    discrepancies = []
    analyzed = [row for row in exclusion_rows if row["record_type"] == "analyzed_case"]
    remainder = [row for row in exclusion_rows if row["record_type"] != "analyzed_case"]

    if len(analyzed) != expected_cases:
        discrepancies.append(f"analyzed_case rows: {len(analyzed)} != {expected_cases}")
    analyzed_ids = [row["case_id"] for row in analyzed]
    if len(set(analyzed_ids)) != len(analyzed_ids):
        discrepancies.append("duplicate analyzed case ids")

    contrib_ids = {row["case_id"] for row in contrib_rows}
    if set(analyzed_ids) != contrib_ids:
        missing = sorted(contrib_ids - set(analyzed_ids))[:5]
        extra = sorted(set(analyzed_ids) - contrib_ids)[:5]
        discrepancies.append(f"id set mismatch; missing={missing} extra={extra}")

    support = {}
    for row in analyzed:
        raw = (row.get("eroded_region_voxels") or "").strip()
        # B_i must be a finite positive integer voxel count (contract 2c).
        if not re.fullmatch(r"[0-9]+", raw) or int(raw) <= 0:
            discrepancies.append(f"{row['case_id']} eroded_region_voxels not a "
                                 f"finite positive integer: {raw!r}")
            continue
        support[row["case_id"]] = int(raw)

    expected_bk = [(item["case_id"], item["record_type"]) for item in EXPECTED_BOOKKEEPING]
    observed_bk = [(row["case_id"], row["record_type"]) for row in remainder]
    if sorted(observed_bk) != sorted(expected_bk):
        discrepancies.append(f"non-analyzed remainder {observed_bk} differs from "
                             f"documented bookkeeping {expected_bk}")
    bookkeeping_records = []
    for row in remainder:
        blanks = all((row.get(field) or "").strip() == "" for field in SUPPORT_FIELDS)
        bookkeeping_records.append({"case_id": row["case_id"],
                                    "record_type": row["record_type"],
                                    "reason": row.get("reason", ""),
                                    "support_fields_blank": blanks})
        if row["record_type"] == "excluded_archive_lesion" and not blanks:
            discrepancies.append(f"{row['case_id']} bookkeeping row has non-blank "
                                 f"support fields")
        if row["record_type"] == "excluded_case" \
                and row.get("reason") != "source_corrupt_member":
            discrepancies.append(f"{row['case_id']} excluded_case reason "
                                 f"{row.get('reason')!r} != 'source_corrupt_member'")

    record = {
        "pass": not discrepancies,
        "analyzed_rows": len(analyzed),
        "unique_analyzed_ids": len(set(analyzed_ids)) == len(analyzed_ids),
        "id_set_matches_contribution_table": set(analyzed_ids) == contrib_ids,
        "b_finite_positive_integer_count": len(support),
        "b_min": min(support.values()) if support else None,
        "b_max": max(support.values()) if support else None,
        "drafting_fingerprint_note": (
            f"drafting-time span {DRAFTING_B_MIN}..{DRAFTING_B_MAX} is lineage "
            "evidence only, not a runtime gate"),
        "bookkeeping_rows": bookkeeping_records,
        "discrepancies": discrepancies,
    }
    return record, support


# ---------------------------------------------------------------------------
# CENSUS CROSS-CHECKS (contract step 3). Recompute the ratified census
# quantities from the contribution table and require exact agreement with
# census_summary.json (and, in the real run, with the frozen contract
# constants). math.fsum is correctly rounded, so equality is exact, not
# approximate. Any mismatch is invalidating transcription, never a result.
# ---------------------------------------------------------------------------

def recompute_census(contrib_rows, head_size):
    net = math.fsum(row["contribution"] for row in contrib_rows)
    if not math.isfinite(net) or net == 0.0:
        fail(EXIT_CROSSCHECK, "net signed contribution is zero or nonfinite")
    total_abs = math.fsum(abs(row["contribution"]) for row in contrib_rows)
    if not math.isfinite(total_abs) or total_abs <= 0.0:
        fail(EXIT_CROSSCHECK, "total absolute contribution is zero or nonfinite")
    signed_head = [row for row in contrib_rows if row["signed_rank"] <= head_size]
    assert len(signed_head) == head_size
    abs_order = sorted(contrib_rows,
                       key=lambda r: (-abs(r["contribution"]), r["case_id"]))
    abs_head = abs_order[:head_size]
    signs = {"positive": sum(row["contribution"] > 0.0 for row in contrib_rows),
             "zero": sum(row["contribution"] == 0.0 for row in contrib_rows),
             "negative": sum(row["contribution"] < 0.0 for row in contrib_rows)}
    assert sum(signs.values()) == len(contrib_rows)
    return {
        "net": net,
        "total_abs": total_abs,
        "signed_head_share": math.fsum(r["contribution"] for r in signed_head) / net,
        "abs_head_share": math.fsum(abs(r["contribution"]) for r in abs_head) / total_abs,
        "signed_head_ids": sorted(r["case_id"] for r in signed_head),
        "abs_head_ids": sorted(r["case_id"] for r in abs_head),
        "sign_counts": signs,
    }


def census_cross_checks(recomputed, census_path, head_size, smoke):
    census = json.loads(read_bytes_checked(census_path).decode("utf-8"))
    top = census.get("top_k", {}).get(str(head_size))
    if top is None:
        fail(EXIT_CROSSCHECK, f"census_summary.json lacks top_k[{head_size}]")
    checks = {
        "signed_head_share_matches_census_json":
            recomputed["signed_head_share"] == top["signed_head_net_gap_share"],
        "abs_head_share_matches_census_json":
            recomputed["abs_head_share"] == top["absolute_mass_share"],
        "sign_counts_match_census_json":
            recomputed["sign_counts"] == census.get("sign_counts"),
        "signed_and_absolute_head_sets_coincide":
            recomputed["signed_head_ids"] == recomputed["abs_head_ids"],
    }
    if not smoke:
        checks["signed_head_share_matches_contract_constant"] = (
            recomputed["signed_head_share"] == EXPECTED_HEAD_SIGNED_SHARE)
        checks["abs_head_share_matches_contract_constant"] = (
            recomputed["abs_head_share"] == EXPECTED_HEAD_ABS_SHARE)
        checks["sign_counts_match_contract_constant"] = (
            recomputed["sign_counts"] == EXPECTED_SIGN_COUNTS)
    failures = [name for name, ok in checks.items() if not ok]
    if failures:
        fail(EXIT_CROSSCHECK,
             f"census cross-check failure (invalidating transcription): {failures}; "
             f"recomputed={recomputed}")
    return checks


# ---------------------------------------------------------------------------
# SUPPORT CLAUSE (contract step 4). Exact finite-population arithmetic over
# the realized 99 cases in IEEE-754 doubles (support sums in exact integers),
# with no uncertainty machinery of any kind. The sole disproportionality
# comparison is the absolute-contribution share beside the support share;
# the signed share is reversal accounting only.
# ---------------------------------------------------------------------------

def ranks_by(rows, key_of):
    """Ranks 1..N, 1 = largest, ties broken by case_id ascending (frozen)."""
    ordered = sorted(rows, key=lambda r: (-key_of(r), r["case_id"]))
    return {row["case_id"]: position for position, row in enumerate(ordered, start=1)}


def support_clause(contrib_rows, support, head_size):
    n = len(contrib_rows)
    assert set(support) == {row["case_id"] for row in contrib_rows}
    head_ids = sorted(row["case_id"] for row in contrib_rows
                      if row["signed_rank"] <= head_size)
    assert len(head_ids) == head_size

    total_abs = math.fsum(abs(row["contribution"]) for row in contrib_rows)
    head_abs = math.fsum(abs(row["contribution"]) for row in contrib_rows
                         if row["case_id"] in set(head_ids))
    # Support voxel counts are integers, so the shares' numerator and
    # denominator are exact integer sums; division is one rounding step.
    total_support = sum(support.values())
    head_support = sum(support[case_id] for case_id in head_ids)
    assert 0 < head_support < total_support
    assert 0.0 < head_abs < total_abs

    net = math.fsum(row["contribution"] for row in contrib_rows)
    signed_head_share = math.fsum(row["contribution"] for row in contrib_rows
                                  if row["case_id"] in set(head_ids)) / net

    rank_abs = ranks_by(contrib_rows, lambda r: abs(r["contribution"]))
    rank_sup = ranks_by(contrib_rows, lambda r: support[r["case_id"]])
    assert sorted(rank_abs.values()) == list(range(1, n + 1))
    assert sorted(rank_sup.values()) == list(range(1, n + 1))
    discrepancies = {case_id: rank_abs[case_id] - rank_sup[case_id]
                     for case_id in rank_abs}
    # Two 1..N permutations always difference to zero-sum; silent corruption
    # of either ranking fails loudly here.
    assert sum(discrepancies.values()) == 0

    # Spearman rho on the frozen tie-broken ranks: with distinct integer
    # ranks the classical formula 1 - 6*sum(d^2)/(n(n^2-1)) is exact.
    sum_d2 = sum(d * d for d in discrepancies.values())
    rho = 1.0 - (6.0 * sum_d2) / (n * (n * n - 1))
    assert -1.0 <= rho <= 1.0

    per_case = []
    for row in sorted(contrib_rows, key=lambda r: r["signed_rank"]):
        case_id = row["case_id"]
        per_case.append({
            "case_id": case_id,
            "signed_rank": row["signed_rank"],
            "in_head": case_id in set(head_ids),
            "contribution": row["contribution"],
            "abs_contribution": abs(row["contribution"]),
            "eroded_region_voxels": support[case_id],
            "rank_abs_contribution": rank_abs[case_id],
            "rank_support": rank_sup[case_id],
            "rank_discrepancy": discrepancies[case_id],
        })
    assert len(per_case) == n

    shares = {
        "n_cases": n,
        "head_definition": f"frozen signed_rank 1..{head_size}; membership never recomputed",
        "head_case_ids": head_ids,
        "sole_disproportionality_comparison": {
            "head_abs_contribution_share": head_abs / total_abs,
            "head_support_share": head_support / total_support,
            "head_abs_contribution_sum": head_abs,
            "total_abs_contribution_sum": total_abs,
            "head_support_voxels": head_support,
            "total_support_voxels": total_support,
            "rule": ("These are the only two numbers the proportionality clause "
                     "may cite; exact arithmetic scoped to the realized cases; "
                     "no threshold, interval, test, or is/is-not verdict."),
        },
        "reversal_accounting": {
            "signed_head_net_gap_share": signed_head_share,
            "label": ("Share of the NET band-2/3 gap after cancellation across "
                      "the opposing cases. Reversal accounting only: neither "
                      "this number nor its difference from the support share "
                      "may be interpreted as contribution per unit support or "
                      "as evidence of keystone-like dominance."),
        },
        "descriptive_displays": {
            "spearman_rho_abs_contribution_vs_support": rho,
            "spearman_method": ("classical distinct-rank formula on the frozen "
                                "tie-broken ranks (1 = largest, ties by case_id "
                                "ascending); bare descriptive number, no interval"),
            "rank_discrepancy_sum_d_squared": sum_d2,
        },
    }
    return per_case, shares


# ---------------------------------------------------------------------------
# DICTIONARY (contract step 5). Stage the 12 kB dictionary against its pinned
# md5 (held copy or the pinned immutable URL -- the only permitted transport
# in this phase), inventory every cell verbatim, and derive the proposed
# variable freeze via the frozen targeting rule. No case-level clinical file
# exists on disk in this phase, so the proposal cannot see any clinical byte.
# ---------------------------------------------------------------------------

def stage_dictionary(output_dir, dictionary_file, expected_md5, expected_bytes, smoke):
    if dictionary_file is not None:
        source = str(dictionary_file)
        if not dictionary_file.is_file():
            fail(EXIT_INPUT, f"--dictionary-file not found: {dictionary_file}")
        data = read_bytes_checked(dictionary_file)
    elif smoke:
        fail(EXIT_INTERNAL, "smoke must supply its synthesized dictionary")
    else:
        source = DICT_URL
        import urllib.request  # Localized: the single permitted network act.
        try:
            with urllib.request.urlopen(DICT_URL, timeout=120) as response:
                data = response.read()
        except Exception as exc:
            fail(EXIT_INPUT, f"dictionary fetch failed ({type(exc).__name__}: {exc}); "
                             f"supply --dictionary-file with a held copy")
    if len(data) != expected_bytes:
        fail(EXIT_INPUT, f"dictionary is {len(data)} bytes, pin says {expected_bytes}")
    digest = md5_bytes(data)
    if digest != expected_md5:
        fail(EXIT_INPUT, f"dictionary md5 {digest} differs from pin {expected_md5}; "
                         f"the pin never re-resolves at runtime")
    staged = output_dir / DICT_NAME
    staged.write_bytes(data)
    return staged, {"source": source, "bytes": len(data), "md5": digest,
                    "sha256": sha256_bytes(data)}


def _local(tag):
    return tag.rsplit("}", 1)[-1]


def _cell_ref_parts(ref, fallback_row, fallback_col):
    match = re.fullmatch(r"([A-Z]+)([0-9]+)", ref or "")
    if match:
        return match.group(2), match.group(1)
    return str(fallback_row), f"COL{fallback_col}"


def parse_xlsx(path):
    """Namespace-agnostic minimal SpreadsheetML reader (stdlib only).

    Returns one record per non-empty cell: sheet, row, column, cell_type,
    value -- values verbatim as stored (shared/inline strings resolved;
    numeric cells keep their raw stored text).
    """
    records = []
    with zipfile.ZipFile(path) as archive:
        names = set(archive.namelist())
        shared = []
        if "xl/sharedStrings.xml" in names:
            root = ElementTree.fromstring(archive.read("xl/sharedStrings.xml"))
            for si in [el for el in root.iter() if _local(el.tag) == "si"]:
                text = "".join(t.text or "" for t in si.iter() if _local(t.tag) == "t")
                shared.append(text)
        sheet_names = {}
        rel_targets = {}
        if "xl/workbook.xml" in names:
            wb = ElementTree.fromstring(archive.read("xl/workbook.xml"))
            for sheet in [el for el in wb.iter() if _local(el.tag) == "sheet"]:
                rid = next((v for k, v in sheet.attrib.items() if _local(k) == "id"), None)
                sheet_names[rid] = sheet.attrib.get("name", "sheet")
        if "xl/_rels/workbook.xml.rels" in names:
            rels = ElementTree.fromstring(archive.read("xl/_rels/workbook.xml.rels"))
            for rel in [el for el in rels.iter() if _local(el.tag) == "Relationship"]:
                target = rel.attrib.get("Target", "").lstrip("/")
                if not target.startswith("xl/"):
                    target = "xl/" + target
                rel_targets[rel.attrib.get("Id")] = target
        sheet_files = []
        for rid, name in sheet_names.items():
            target = rel_targets.get(rid)
            if target in names:
                sheet_files.append((name, target))
        if not sheet_files:  # Fallback: enumerate worksheet parts directly.
            sheet_files = [(member.rsplit("/", 1)[-1], member)
                           for member in sorted(names)
                           if member.startswith("xl/worksheets/")
                           and member.endswith(".xml")]
        if not sheet_files:
            fail(EXIT_INPUT, "dictionary workbook contains no worksheets")
        for sheet_name, member in sheet_files:
            root = ElementTree.fromstring(archive.read(member))
            for row_index, row in enumerate(
                    [el for el in root.iter() if _local(el.tag) == "row"], start=1):
                for col_index, cell in enumerate(
                        [el for el in row if _local(el.tag) == "c"], start=1):
                    cell_type = cell.attrib.get("t", "n")
                    value = None
                    if cell_type == "inlineStr":
                        value = "".join(t.text or "" for t in cell.iter()
                                        if _local(t.tag) == "t")
                    else:
                        v = next((el for el in cell if _local(el.tag) == "v"), None)
                        if v is not None and v.text is not None:
                            value = v.text
                            if cell_type == "s":
                                index = int(v.text)
                                if not 0 <= index < len(shared):
                                    fail(EXIT_INPUT, "shared-string index out of range")
                                value = shared[index]
                    if value is None or value == "":
                        continue
                    row_no, col_letter = _cell_ref_parts(
                        cell.attrib.get("r"), row_index, col_index)
                    records.append({"sheet": sheet_name, "row": int(row_no),
                                    "column": col_letter, "cell_type": cell_type,
                                    "value": value})
    if not records:
        fail(EXIT_INPUT, "dictionary workbook contains no non-empty cells")
    return records


def match_construct(records, regexes):
    matches = []
    compiled = [re.compile(r) for r in regexes]
    for record in records:
        if all(rx.search(record["value"]) for rx in compiled):
            row_values = [r["value"] for r in records
                          if r["sheet"] == record["sheet"] and r["row"] == record["row"]]
            matches.append({"sheet": record["sheet"], "row": record["row"],
                            "column": record["column"], "text": record["value"],
                            "row_values_verbatim": row_values})
    return matches


def propose_variable_freeze(records):
    constructs = {}
    for name, role, regexes in TARGET_CONSTRUCTS:
        matches = match_construct(records, regexes)
        constructs[name] = {
            "role": role,
            "regexes": regexes,
            "matched": bool(matches),
            "proposed_field_spelling": matches[0]["text"] if matches else None,
            "matches": matches,
        }
    contextual = []
    for name, regexes in CONTEXTUAL_CANDIDATES:
        if len(contextual) >= CONTEXTUAL_CAP:
            break
        matches = match_construct(records, regexes)
        if matches:
            contextual.append({"construct": name, "regexes": regexes,
                               "proposed_field_spelling": matches[0]["text"],
                               "matches": matches})
    center_matches = match_construct(records, CENTER_REGEXES)
    any_nihss = any(re.search(ANY_NIHSS_REGEX, record["value"]) for record in records)
    outcome_ok = constructs["mrs_3month"]["matched"] or any_nihss
    demographic_ok = constructs["age"]["matched"] or constructs["sex"]["matched"]
    supported = outcome_ok and demographic_ok
    freeze = {
        "derived_from": "Phase-A dictionary inventory only; no clinical byte existed "
                        "on disk when this proposal was derived",
        "constructs": constructs,
        "contextual_cap": CONTEXTUAL_CAP,
        "contextual_proposed": contextual,
        "center": {
            "documented": bool(center_matches),
            "rule": "mandatory contextual variable OUTSIDE the cap if documented",
            "matches": center_matches,
        },
        "reconciliation": {
            "nihss_time_points": (
                "The 24-hour NIHSS field is the lineage-preserving variable of "
                "idea-046's frozen optional rung; admission NIHSS is documented "
                "baseline-severity context and is never presented as "
                "interchangeable with the 24-hour field (contract targeting_rule; "
                "critique D1)."),
            "center_absent_recorded": not bool(center_matches),
        },
        "minimum_set": {
            "outcome_or_nihss_documented": outcome_ok,
            "age_or_sex_documented": demographic_ok,
            "supported": supported,
        },
        "binding_note": (
            "Machine-derived proposal only. The contract amendment binds the "
            "final list; amendment deviations from this proposal require a "
            "recorded dictionary-grounded reason, and additions motivated by "
            "any Phase-A scientific output are prohibited and invalidating."),
    }
    return freeze, supported


# ---------------------------------------------------------------------------
# SMOKE FIXTURES. Synthetic stand-ins exercising every code path (including
# the xlsx parser and targeting rule) without touching a single real input.
# Smoke output is always SMOKE_ONLY and can never satisfy a contractual gate.
# ---------------------------------------------------------------------------

def make_smoke_inputs(output_dir):
    fixture_dir = output_dir / "smoke_inputs"
    fixture_dir.mkdir()
    n = SMOKE_CASES
    deltas = [0.084, 0.060, 0.048, 0.036, 0.024, 0.018, 0.012,
              0.0, 0.0, -0.012, -0.024, -0.036]
    assert len(deltas) == n
    rows = []
    for index, delta in enumerate(deltas):
        band2 = -0.10 - index * 0.01
        rows.append({"case_id": f"synthetic-{index + 1:02d}", "d_band2": band2,
                     "d_band3": band2 + delta, "delta": (band2 + delta) - band2,
                     "contribution": ((band2 + delta) - band2) / n})
    ordered = sorted(rows, key=lambda r: (-r["contribution"], r["case_id"]))
    for position, row in enumerate(ordered, start=1):
        row["signed_rank"] = position
    contrib_path = fixture_dir / "per_case_contributions.csv"
    write_csv(contrib_path,
              ["case_id", "d_band2", "d_band3", "delta", "contribution", "signed_rank"],
              sorted(rows, key=lambda r: r["case_id"]))

    exclusion_rows = []
    for index, row in enumerate(rows):
        support = 1200 + 517 * ((index * 7) % 13) + index  # Deterministic ints.
        exclusion_rows.append({"case_id": row["case_id"],
                               "record_type": "analyzed_case", "reason": "",
                               "source_path": "", "deficit_voxels": support + 40,
                               "eroded_region_voxels": support,
                               "vessel_voxels": 10, "vessel_cbv_p98": 1.5,
                               "nonfinite_cbf_voxels": 0, "nonfinite_cbv_voxels": 0,
                               "nonfinite_mtt_voxels": 0, "nonfinite_tmax_voxels": 0})
    blank = {field: "" for field in SUPPORT_FIELDS}
    exclusion_rows.append({"case_id": "sub-stroke0142",
                           "record_type": "excluded_archive_lesion",
                           "reason": "synthetic bookkeeping row",
                           "source_path": "synthetic", **blank})
    exclusion_rows.append({"case_id": "sub-stroke0043", "record_type": "excluded_case",
                           "reason": "source_corrupt_member",
                           "source_path": "synthetic", **blank})
    exclusions_path = fixture_dir / "exclusions.csv"
    write_csv(exclusions_path, ["case_id", "record_type", "reason", "source_path",
                                *SUPPORT_FIELDS], exclusion_rows)

    contrib_loaded = load_contributions(contrib_path, n)
    recomputed = recompute_census(contrib_loaded, SMOKE_HEAD_SIZE)
    census = {"top_k": {str(SMOKE_HEAD_SIZE): {
                  "signed_head_net_gap_share": recomputed["signed_head_share"],
                  "absolute_mass_share": recomputed["abs_head_share"]}},
              "sign_counts": recomputed["sign_counts"],
              "synthetic": True}
    census_path = fixture_dir / "census_summary.json"
    write_json(census_path, census)

    code_path = fixture_dir / "take13_code.py"
    code_path.write_text(
        "def coordinate_arrays(arrays):\n"
        "    # Synthetic smoke fixture standing in for the frozen take-13 code.\n"
        "    eroded_region_voxels = 0\n"
        "    return eroded_region_voxels\n", encoding="utf-8")

    dict_path = fixture_dir / DICT_NAME
    _write_smoke_xlsx(dict_path)
    data = dict_path.read_bytes()
    return {"exclusions": exclusions_path, "contributions": contrib_path,
            "census": census_path, "take13": code_path, "dictionary": dict_path,
            "dictionary_md5": md5_bytes(data), "dictionary_bytes": len(data)}


def _write_smoke_xlsx(path):
    fields = [("Field", "Description", "Type"),
              ("Age", "Age of the patient in years", "numeric"),
              ("Sex", "Biological sex", "categorical"),
              ("NIHSS at admission", "Severity score at admission", "integer"),
              ("NIHSS 24h", "Severity score at 24 hours", "integer"),
              ("NIHSS discharge", "Severity score at discharge", "integer"),
              ("MRS 3 months", "Functional outcome at 3 months", "ordinal"),
              ("mTici postinterventional", "Reperfusion grade", "ordinal"),
              ("Time from onset to imaging", "Minutes", "numeric"),
              ("Center", "Acquiring center identifier", "categorical")]
    def cell(ref, text):
        return (f'<c r="{ref}" t="inlineStr"><is><t xml:space="preserve">'
                f"{text}</t></is></c>")
    body = []
    for row_no, row in enumerate(fields, start=1):
        cells = "".join(cell(f"{chr(65 + i)}{row_no}", value)
                        for i, value in enumerate(row))
        body.append(f'<row r="{row_no}">{cells}</row>')
    sheet = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
             '<worksheet xmlns="http://schemas.openxmlformats.org/'
             'spreadsheetml/2006/main"><sheetData>'
             + "".join(body) + "</sheetData></worksheet>")
    workbook = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                '<workbook xmlns="http://schemas.openxmlformats.org/'
                'spreadsheetml/2006/main" xmlns:r="http://schemas.openxmlformats'
                '.org/officeDocument/2006/relationships"><sheets>'
                '<sheet name="dictionary" sheetId="1" r:id="rId1"/></sheets></workbook>')
    wb_rels = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
               '<Relationships xmlns="http://schemas.openxmlformats.org/package/'
               '2006/relationships"><Relationship Id="rId1" Type="http://schemas.'
               'openxmlformats.org/officeDocument/2006/relationships/worksheet" '
               'Target="worksheets/sheet1.xml"/></Relationships>')
    root_rels = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                 '<Relationships xmlns="http://schemas.openxmlformats.org/package/'
                 '2006/relationships"><Relationship Id="rId1" Type="http://schemas.'
                 'openxmlformats.org/officeDocument/2006/relationships/'
                 'officeDocument" Target="xl/workbook.xml"/></Relationships>')
    content_types = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                     '<Types xmlns="http://schemas.openxmlformats.org/package/2006/'
                     'content-types"><Default Extension="rels" ContentType='
                     '"application/vnd.openxmlformats-package.relationships+xml"/>'
                     '<Default Extension="xml" ContentType="application/xml"/>'
                     '<Override PartName="/xl/workbook.xml" ContentType='
                     '"application/vnd.openxmlformats-officedocument.spreadsheetml'
                     '.sheet.main+xml"/><Override PartName="/xl/worksheets/sheet1.xml" '
                     'ContentType="application/vnd.openxmlformats-officedocument.'
                     'spreadsheetml.worksheet+xml"/></Types>')
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as archive:
        for name, data in [("[Content_Types].xml", content_types),
                           ("_rels/.rels", root_rels),
                           ("xl/workbook.xml", workbook),
                           ("xl/_rels/workbook.xml.rels", wb_rels),
                           ("xl/worksheets/sheet1.xml", sheet)]:
            archive.writestr(zipfile.ZipInfo(name), data)  # Fixed 1980 timestamp.


def environment_record():
    return {
        "python": sys.version,
        "platform": platform.platform(),
        "executable": sys.executable,
        "pid": os.getpid(),
        "dependencies": "Python standard library only",
    }


# ---------------------------------------------------------------------------
# RUN. The contract's ordered Phase-A steps, in order: authority -> split
# freeze -> identity gates -> support provenance gate -> census cross-checks
# -> support clause -> dictionary inventory and freeze proposal -> outputs.
# ---------------------------------------------------------------------------

def run(args):
    started = time.monotonic()
    prepare_output_dir(args.output_dir)
    log_lines = []
    emit(f"[authority] Idea 047 Phase {PHASE}; seed {SEED}; smoke={args.smoke}.",
         log_lines)
    contract_blob = verify_authority(args.smoke)
    emit(f"[authority] Governing contract blob: {contract_blob}.", log_lines)

    expected_cases = SMOKE_CASES if args.smoke else EXPECTED_CASES
    head_size = SMOKE_HEAD_SIZE if args.smoke else HEAD_SIZE

    # SPLIT FREEZE before any input is opened (hard standard 5).
    split = freeze_split(args.output_dir, expected_cases, args.smoke)
    emit(f"[split] Frozen: {expected_cases} analyzed census cases; "
         f"{split['reserved_cases']} reserved cases untouched.", log_lines)

    if args.smoke:
        fixtures = make_smoke_inputs(args.output_dir)
        paths = {"exclusions.csv": fixtures["exclusions"],
                 "per_case_contributions.csv": fixtures["contributions"],
                 "census_summary.json": fixtures["census"]}
        take13_path = fixtures["take13"]
        dictionary_file = fixtures["dictionary"]
        dict_md5, dict_bytes = fixtures["dictionary_md5"], fixtures["dictionary_bytes"]
    else:
        paths = {"exclusions.csv": EXCLUSIONS_PATH,
                 "per_case_contributions.csv": CONTRIB_PATH,
                 "census_summary.json": CENSUS_PATH}
        take13_path = TAKE13_RUNPY_PATH
        dictionary_file = args.dictionary_file
        dict_md5, dict_bytes = DICT_MD5, DICT_BYTES

    # LOAD + IDENTITY (contract step 1).
    emit("[load] Hashing frozen inputs and verifying identity pins.", log_lines)
    manifest_start = hash_inputs({**paths, "take13_run.py": take13_path})
    manifest_start["seed"] = SEED
    manifest_start["smoke"] = args.smoke
    verify_input_identity(manifest_start, take13_path, args.smoke)
    coordinate_evidence = extract_coordinate_lines(take13_path, args.smoke)
    write_json(args.output_dir / "determinism_manifest_start.json", manifest_start)
    print(json.dumps(manifest_start, sort_keys=True), flush=True)
    exclusion_rows = load_exclusions(paths["exclusions.csv"])
    contrib_rows = load_contributions(paths["per_case_contributions.csv"],
                                      expected_cases)
    manifest_start["row_counts"] = {"exclusions.csv": len(exclusion_rows),
                                    "per_case_contributions.csv": len(contrib_rows)}
    write_json(args.output_dir / "determinism_manifest_start.json", manifest_start)
    emit(f"[load] {len(exclusion_rows)} exclusion rows; "
         f"{len(contrib_rows)} contribution rows.", log_lines)

    # SUPPORT PROVENANCE GATE (contract step 2). Failure = pre-registered
    # decision-grade stop; the gate record is the deliverable.
    emit("[validate] Running the support provenance-and-join gate.", log_lines)
    gate_record, support = support_provenance_gate(exclusion_rows, contrib_rows,
                                                   expected_cases)
    bookkeeping = [row for row in exclusion_rows
                   if row["record_type"] != "analyzed_case"]
    write_csv(args.output_dir / "probe_exclusions.csv",
              ["case_id", "record_type", "reason"],
              [{"case_id": row["case_id"], "record_type": row["record_type"],
                "reason": row.get("reason", "")} for row in bookkeeping])
    if not gate_record["pass"]:
        gate_record["status"] = "SUPPORT_PROVENANCE_FAILURE"
        write_json(args.output_dir / "provenance_gate.json", gate_record)
        summary = {"idea_id": IDEA_ID, "phase": PHASE,
                   "status": "SUPPORT_PROVENANCE_FAILURE", "smoke": args.smoke,
                   "discrepancies": gate_record["discrepancies"],
                   "note": ("Pre-registered decision-grade stop, not a negative "
                            "and not invalidating; no support-clause output was "
                            "written; escalation is the next act.")}
        write_json(args.output_dir / "summary.json", summary)
        write_json(args.output_dir / "environment.txt", environment_record())
        emit(json.dumps(summary, indent=2, sort_keys=True), log_lines)
        (args.output_dir / "run_log.txt").write_text("\n".join(log_lines) + "\n",
                                                     encoding="utf-8")
        return EXIT_SUPPORT_STOP
    emit(f"[validate] Gate PASS: {gate_record['analyzed_rows']} analyzed cases, "
         f"B_i in [{gate_record['b_min']}, {gate_record['b_max']}], "
         f"{len(bookkeeping)} documented bookkeeping rows.", log_lines)

    # CENSUS CROSS-CHECKS (contract step 3): exact recomputation agreement.
    emit("[validate] Recomputing census cross-checks (exact equality).", log_lines)
    recomputed = recompute_census(contrib_rows, head_size)
    checks = census_cross_checks(recomputed, paths["census_summary.json"],
                                 head_size, args.smoke)
    gate_record["census_cross_checks"] = {"checks": checks,
                                          "recomputed_signed_head_share":
                                              recomputed["signed_head_share"],
                                          "recomputed_abs_head_share":
                                              recomputed["abs_head_share"],
                                          "sign_counts": recomputed["sign_counts"]}
    write_json(args.output_dir / "provenance_gate.json", gate_record)
    emit(f"[validate] Cross-checks PASS: {sorted(checks)}.", log_lines)

    # MEASURE (contract step 4): the frozen support clause.
    emit(f"[measure] Computing the support clause for {len(contrib_rows)} cases "
         f"(head = signed_rank 1..{head_size}); variant 1/1.", log_lines)
    per_case, shares = support_clause(contrib_rows, support, head_size)
    for index, row in enumerate(per_case, start=1):
        emit(f"[measure] Case {index}/{len(per_case)} {row['case_id']}: "
             f"B_i={row['eroded_region_voxels']}, "
             f"rank_discrepancy={row['rank_discrepancy']}.", log_lines)
    write_csv(args.output_dir / "per_case_support.csv",
              ["case_id", "signed_rank", "in_head", "contribution",
               "abs_contribution", "eroded_region_voxels",
               "rank_abs_contribution", "rank_support", "rank_discrepancy"],
              per_case)
    write_csv(args.output_dir / "rank_discrepancy.csv",
              ["case_id", "rank_abs_contribution", "rank_support",
               "rank_discrepancy", "in_head"],
              [{"case_id": row["case_id"],
                "rank_abs_contribution": row["rank_abs_contribution"],
                "rank_support": row["rank_support"],
                "rank_discrepancy": row["rank_discrepancy"],
                "in_head": row["in_head"]}
               for row in sorted(per_case, key=lambda r: r["rank_abs_contribution"])])
    write_json(args.output_dir / "support_shares.json", shares)
    comparison = shares["sole_disproportionality_comparison"]
    emit(f"[measure] Head absolute-contribution share: "
         f"{comparison['head_abs_contribution_share']:.6f}; head support share: "
         f"{comparison['head_support_share']:.6f} (exact arithmetic, no verdict).",
         log_lines)

    # DICTIONARY (contract step 5): stage against the pin, inventory verbatim,
    # derive the machine-proposed freeze. Phenotype rows do not exist on disk.
    emit("[summarize] Staging and inventorying the clinical data dictionary.",
         log_lines)
    staged, dict_record = stage_dictionary(args.output_dir, dictionary_file,
                                           dict_md5, dict_bytes, args.smoke)
    records = parse_xlsx(staged)
    assert records and all(r["value"] for r in records)
    write_csv(args.output_dir / "dictionary_inventory.csv",
              ["sheet", "row", "column", "cell_type", "value"], records)
    freeze, supported = propose_variable_freeze(records)
    freeze["dictionary"] = dict_record
    write_json(args.output_dir / "proposed_variable_freeze.json", freeze)
    emit(f"[summarize] Inventory: {len(records)} cells; minimum variable set "
         f"supported: {supported}.", log_lines)
    if args.smoke:
        # The synthetic dictionary must exercise every targeting path.
        assert supported and freeze["center"]["documented"]
        assert len(freeze["contextual_proposed"]) == CONTEXTUAL_CAP

    if args.smoke:
        status = "SMOKE_ONLY"
    elif supported:
        status = "PHASE_A_COMPLETE_REQUIRES_AMENDMENT"
    else:
        status = "PHASE_A_COMPLETE_CLINICAL_UNSUPPORTED"

    elapsed = time.monotonic() - started
    if elapsed > WALL_SECONDS:
        fail(EXIT_WALL, f"run exceeded the {WALL_SECONDS}s Phase-A wall cap")

    resolved = {
        "idea_id": IDEA_ID, "contract_version": CONTRACT_VERSION, "phase": PHASE,
        "contract_blob": contract_blob, "seed": SEED, "smoke": args.smoke,
        "variants": 1, "gpu_minutes": 0,
        "inputs": {name: value for name, value in manifest_start.items()
                   if isinstance(value, dict) and "sha256" in value},
        "dictionary": dict_record,
        "take13_code_evidence": {
            "path": str(take13_path.resolve()),
            "git_blob": git_blob(take13_path),
            "coordinate_arrays": coordinate_evidence,
            "note": "byte-verified evidence of the B_i definition; never executed",
        },
        "output_dir": str(args.output_dir.resolve()),
        "cli": {"dictionary_file": str(args.dictionary_file)
                                   if args.dictionary_file else None},
    }
    write_json(args.output_dir / "resolved_config.json", resolved)
    input_rows = [{"input": name, "path": value["path"], "sha256": value["sha256"],
                   "role": "frozen_input"}
                  for name, value in manifest_start.items()
                  if isinstance(value, dict) and "sha256" in value]
    input_rows.append({"input": DICT_NAME, "path": dict_record["source"],
                       "sha256": dict_record["sha256"], "role": "staged_dictionary"})
    write_csv(args.output_dir / "input_manifest.csv",
              ["input", "path", "sha256", "role"], input_rows)

    summary = {
        "idea_id": IDEA_ID, "phase": PHASE, "status": status, "smoke": args.smoke,
        "analyzed_cases": len(per_case), "head_size": head_size,
        "head_abs_contribution_share": comparison["head_abs_contribution_share"],
        "head_support_share": comparison["head_support_share"],
        "signed_reversal_accounting_share":
            shares["reversal_accounting"]["signed_head_net_gap_share"],
        "spearman_rho":
            shares["descriptive_displays"]["spearman_rho_abs_contribution_vs_support"],
        "clinical_minimum_set_supported": supported,
        "dictionary_cells_inventoried": len(records),
        "bookkeeping_rows_excluded": len(bookkeeping),
        "reserved_cases_accessed": 0,
        "phenotype_rows_opened": 0,
        "primary_output": "support_shares.json (sole disproportionality comparison)",
        "wall_seconds": round(elapsed, 3),
    }
    write_json(args.output_dir / "summary.json", summary)
    write_json(args.output_dir / "environment.txt", environment_record())

    # DETERMINISM MANIFEST END: the frozen inputs must hash identically.
    manifest_end = hash_inputs({**paths, "take13_run.py": take13_path})
    manifest_end["seed"] = SEED
    manifest_end["smoke"] = args.smoke
    manifest_end["row_counts"] = dict(manifest_start["row_counts"])
    if manifest_end != manifest_start:
        fail(EXIT_OUTPUT, "start and end determinism manifests differ")
    write_json(args.output_dir / "determinism_manifest_end.json", manifest_end)
    print(json.dumps(manifest_end, sort_keys=True), flush=True)

    emit(json.dumps(summary, indent=2, sort_keys=True), log_lines)
    if status == "PHASE_A_COMPLETE_REQUIRES_AMENDMENT":
        interpretation = (
            "Plain-language template: PHASE_A_COMPLETE_REQUIRES_AMENDMENT means "
            "every identity, provenance, and cross-check gate passed and the "
            "phenotype-blind support clause was emitted -- a successful "
            "descriptive result regardless of the share values, carrying no "
            "proportionality verdict. The two shares are exact arithmetic for "
            "these 99 realized cases only. Next act: the mechanical contract "
            "amendment binds the frozen clinical variable list from the "
            "dictionary inventory; fresh human approval of the amended blob is "
            "the sole authorization for Phase B.")
    elif status == "PHASE_A_COMPLETE_CLINICAL_UNSUPPORTED":
        interpretation = (
            "Plain-language template: PHASE_A_COMPLETE_CLINICAL_UNSUPPORTED is "
            "the pre-registered branch -- the support clause was still delivered, "
            "but the dictionary does not document the minimum variable set; no "
            "amendment path exists and successor handling is an operator "
            "decision. This is a decision-grade description, not a negative.")
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
