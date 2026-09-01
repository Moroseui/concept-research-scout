#!/usr/bin/env python3
"""Outcome-blind design-matrix feasibility probe for idea 045.

This experiment checks whether the frozen 99-patient, bands-2/3 attenuation
audit can support the proposed four-column band-by-HU-imbalance linear model.
The contract's primary metric is the singular-value condition number after
diagnostic column scaling. The runner stops after one deterministic design
audit, on any invalidating failure, or before an observed final-infarct `d`
value could be read. A positive result means every frozen rank, conditioning,
variation, and leverage gate passes; a negative result means valid exposure
geometry fails at least one such gate. Neither result says whether attenuation
is associated with infarction or explains idea 023's reversal.

One command runs either the approved audit or a synthetic harness check:
    python probes/045/run.py --output-dir /path/to/results
    python probes/045/run.py --smoke --output-dir /tmp/probe-045-smoke

Exit codes: 0 valid completion; 2 approval/CLI failure; 3 input/access failure;
4 provenance failure; 5 split/join failure; 6 value/design failure;
7 output/determinism failure; 12 unexpected harness fault. Smoke output is
always marked SMOKE_ONLY and can never satisfy a contractual gate.
"""

import argparse
import csv
import hashlib
import json
import os
import platform
import random
import re
import sys
import traceback
from datetime import datetime, timezone
from pathlib import Path

import numpy as np


# Declared state: the contract permits one seed and one fixed configuration.
IDEA_ID = "idea-045"
CONTRACT_VERSION = 1
SEED = 0
PRIMARY_BANDS = (2, 3)
EXPECTED_CASES_PER_BAND = 99
CONDITION_LIMIT = 30.0  # Frozen conservative boundary in probe_contract.yaml.
LEVERAGE_LIMIT = 0.20  # Frozen conservative boundary in probe_contract.yaml.
MIN_DISTINCT = 20      # Frozen minimum exposure support in probe_contract.yaml.
TOP_LEVERAGE_ROWS = 10
MIN_TOP_PATIENTS = 5

PROBE_DIR = Path(__file__).resolve().parent
REPO_ROOT = PROBE_DIR.parent.parent
CONTRACT_PATH = REPO_ROOT / "ideas/045/probe_contract.yaml"
APPROVAL_PATH = REPO_ROOT / "ideas/045/HUMAN_APPROVED_PROBE"
DEFAULT_AUDIT_PATH = REPO_ROOT / "probes/023/results/results_v2/bin_tissue_audit.csv"
DEFAULT_KEYS_PATH = REPO_ROOT / "probes/023/results/results_v2/per_patient.csv"

EXIT_APPROVAL = 2
EXIT_INPUT = 3
EXIT_PROVENANCE = 4
EXIT_JOIN = 5
EXIT_DESIGN = 6
EXIT_OUTPUT = 7
EXIT_INTERNAL = 12


class ProbeFailure(RuntimeError):
    def __init__(self, code, message):
        super().__init__(message)
        self.code = code


def fail(code, message):
    raise ProbeFailure(code, message)


def sha256_file(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def git_blob(path):
    header = f"blob {path.stat().st_size}\0".encode("ascii")
    digest = hashlib.sha1()
    digest.update(header)
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_csv(path, fieldnames, rows):
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def log(message, log_lines):
    print(message, flush=True)
    log_lines.append(message)


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--audit-csv", type=Path, default=DEFAULT_AUDIT_PATH)
    parser.add_argument("--keys-csv", type=Path, default=DEFAULT_KEYS_PATH)
    parser.add_argument("--smoke", action="store_true")
    return parser.parse_args()


def verify_approval(smoke):
    if smoke:
        return "SMOKE_NOT_APPROVAL_ELIGIBLE"
    if not CONTRACT_PATH.is_file() or not APPROVAL_PATH.is_file():
        fail(EXIT_APPROVAL, "contract or HUMAN_APPROVED_PROBE is missing")
    marker = APPROVAL_PATH.read_text(encoding="utf-8")
    match = re.search(r"^contract_blob:\s*([0-9a-f]{40})$", marker, re.MULTILINE)
    if not match:
        fail(EXIT_APPROVAL, "approval marker does not contain a contract_blob")
    actual_blob = git_blob(CONTRACT_PATH)
    if match.group(1) != actual_blob:
        fail(EXIT_APPROVAL, "approval marker is stale for the current contract")
    contract_text = CONTRACT_PATH.read_text(encoding="utf-8")
    required_literals = [
        'contract_version: 1', 'maximum_variants: 1', 'maximum_gpu_minutes: 0',
        'maximum_seeds: 1', 'condition number is <=30',
        'maximum row leverage is <=0.20', 'at least 20 distinct',
    ]
    if any(item not in contract_text for item in required_literals):
        fail(EXIT_APPROVAL, "approved contract no longer contains a frozen implementation value")
    return actual_blob


def make_smoke_rows():
    audit_rows = []
    cases = [f"smoke-{index:03d}" for index in range(1, 25)]
    for band in PRIMARY_BANDS:
        for index, case_id in enumerate(cases):
            base = 20.0 + index
            audit_rows.append((case_id, band, "Q1_low_CBV", base + band))
            audit_rows.append((case_id, band, "Q4_high_CBV", base - index * 0.1))
    return audit_rows, {(case_id, band) for case_id in cases for band in PRIMARY_BANDS}


def load_audit(path):
    if not path.is_file():
        fail(EXIT_INPUT, f"missing audit input: {path}")
    rows = []
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        required = {"case_id", "stratum", "style_group", "median_hu"}
        if not reader.fieldnames or not required.issubset(reader.fieldnames):
            fail(EXIT_INPUT, "audit CSV lacks required columns")
        for raw in reader:
            try:
                band = int(raw["stratum"])
                median_hu = float(raw["median_hu"])
            except (TypeError, ValueError):
                fail(EXIT_DESIGN, "audit CSV contains a nonnumeric stratum or median_hu")
            if band in PRIMARY_BANDS:
                rows.append((raw["case_id"], band, raw["style_group"], median_hu))
    if not rows:
        fail(EXIT_INPUT, "audit CSV contains no primary-band rows")
    assert all(row[1] in PRIMARY_BANDS for row in rows)
    return rows


def write_split_before_outcome(output_dir, audit_rows, smoke):
    cases_by_band = {band: sorted({row[0] for row in audit_rows if row[1] == band}) for band in PRIMARY_BANDS}
    assert all(cases_by_band[band] for band in PRIMARY_BANDS)
    rows = []
    for band in PRIMARY_BANDS:
        for case_id in cases_by_band[band]:
            rows.append({"case_id": case_id, "stratum": band, "split": "opened_census"})
    split_path = output_dir / "split_manifest.csv"
    write_csv(split_path, ["case_id", "stratum", "split"], rows)
    split_hash = sha256_file(split_path)
    split_record = {
        "created_before_outcome_file_open": True,
        "smoke": smoke,
        "seed": SEED,
        "rows": len(rows),
        "unique_cases": len(set().union(*[set(value) for value in cases_by_band.values()])),
        "bands": list(PRIMARY_BANDS),
        "sha256": split_hash,
        "reserved_cases_accessed": 0,
    }
    write_json(output_dir / "split_manifest.json", split_record)
    assert split_record["reserved_cases_accessed"] == 0
    return cases_by_band, split_record


def load_keys_without_outcomes(path):
    """Read only CSV fields 0 and 1; later fields are never split or retained."""
    if not path.is_file():
        fail(EXIT_INPUT, f"missing keys input: {path}")
    keys = set()
    with path.open(encoding="utf-8") as handle:
        try:
            header = next(handle).rstrip("\r\n")
        except StopIteration:
            fail(EXIT_INPUT, "keys CSV is empty")
        if header != "case_id,stratum,q1_voxels,q4_voxels,d":
            fail(EXIT_INPUT, "keys CSV header differs from the approved five-column schema")
        for raw_line in handle:
            # Count delimiters to validate the frozen schema without splitting
            # or indexing the forbidden outcome field after the second comma.
            if raw_line.count(",") != 4:
                fail(EXIT_INPUT, "keys CSV row does not have exactly five fields")
            first_comma = raw_line.find(",")
            second_comma = raw_line.find(",", first_comma + 1)
            case_id = raw_line[:first_comma]
            try:
                band = int(raw_line[first_comma + 1:second_comma])
            except ValueError:
                fail(EXIT_JOIN, "keys CSV contains a nonnumeric stratum")
            if band in PRIMARY_BANDS:
                key = (case_id, band)
                if key in keys:
                    fail(EXIT_JOIN, f"duplicate outcome key: {key}")
                keys.add(key)
            # Deliberately do not slice, split, parse, or retain the remainder.
    assert all(band in PRIMARY_BANDS for _, band in keys)
    return keys


def build_design(audit_rows, outcome_keys, expected_count):
    cells = {}
    exclusions = []
    permitted_styles = {"Q1_low_CBV", "Q4_high_CBV"}
    for case_id, band, style, median_hu in audit_rows:
        if style not in permitted_styles:
            exclusions.append({"case_id": case_id, "stratum": band, "item": style,
                               "reason": "non_primary_style_group"})
            continue
        key = (case_id, band, style)
        if key in cells:
            fail(EXIT_JOIN, f"duplicate audit cell: {key}")
        if not np.isfinite(median_hu):
            fail(EXIT_DESIGN, f"nonfinite median HU: {key}")
        cells[key] = median_hu
    assert all(key[2] in permitted_styles for key in cells)

    design_rows = []
    for band in PRIMARY_BANDS:
        band_cases = sorted({case_id for case_id, key_band in outcome_keys if key_band == band})
        if len(band_cases) != expected_count:
            fail(EXIT_JOIN, f"band {band} has {len(band_cases)} cases; expected {expected_count}")
        for case_id in band_cases:
            q1_key = (case_id, band, "Q1_low_CBV")
            q4_key = (case_id, band, "Q4_high_CBV")
            if q1_key not in cells or q4_key not in cells:
                fail(EXIT_JOIN, f"missing Q1/Q4 audit cell for {(case_id, band)}")
            imbalance = cells[q1_key] - cells[q4_key]  # HU difference; no unit conversion.
            if not np.isfinite(imbalance):
                fail(EXIT_DESIGN, f"nonfinite HU imbalance for {(case_id, band)}")
            design_rows.append({"case_id": case_id, "stratum": band,
                                "q1_median_hu": cells[q1_key],
                                "q4_median_hu": cells[q4_key],
                                "hu_imbalance": imbalance})
    expected_keys = {(row["case_id"], row["stratum"]) for row in design_rows}
    if expected_keys != outcome_keys:
        fail(EXIT_JOIN, "audit and outcome-key case/stratum sets do not match exactly")
    assert len(design_rows) == expected_count * len(PRIMARY_BANDS)
    return design_rows, exclusions


def condition_number(matrix):
    scaled = matrix.copy()
    for column in range(1, scaled.shape[1]):
        norm = np.linalg.norm(scaled[:, column])
        if norm == 0:
            return float("inf"), np.array([]), 0
        scaled[:, column] = scaled[:, column] / norm  # Contract-only diagnostic scaling.
    singular_values = np.linalg.svd(scaled, compute_uv=False)
    rank = int(np.linalg.matrix_rank(scaled))
    value = float(singular_values[0] / singular_values[-1]) if singular_values[-1] > 0 else float("inf")
    return value, singular_values, rank


def measure_design(design_rows):
    values = np.array([row["hu_imbalance"] for row in design_rows], dtype=float)
    pooled_mean = float(np.mean(values))  # The contract freezes pooled-mean centering.
    centered = values - pooled_mean
    band3 = np.array([1.0 if row["stratum"] == 3 else 0.0 for row in design_rows])
    matrix = np.column_stack([np.ones(len(design_rows)), band3, centered, band3 * centered])
    assert matrix.shape == (len(design_rows), 4)
    assert np.isfinite(matrix).all()

    primary_condition, singular_values, rank = condition_number(matrix)
    leverage = np.diag(matrix @ np.linalg.pinv(matrix.T @ matrix) @ matrix.T)
    assert leverage.shape == (len(design_rows),)
    assert np.isfinite(leverage).all()
    assert np.all(leverage >= -1e-12) and np.all(leverage <= 1.0 + 1e-12)

    support = {}
    for band in PRIMARY_BANDS:
        band_values = np.array([row["hu_imbalance"] for row in design_rows if row["stratum"] == band])
        assert len(band_values) > 0
        support[str(band)] = {
            "n": int(len(band_values)), "minimum": float(np.min(band_values)),
            "maximum": float(np.max(band_values)), "median": float(np.median(band_values)),
            "q25": float(np.percentile(band_values, 25)),
            "q75": float(np.percentile(band_values, 75)),
            "iqr": float(np.percentile(band_values, 75) - np.percentile(band_values, 25)),
            "distinct_values": int(len(np.unique(band_values))),
        }

    top_indices = np.argsort(leverage)[-TOP_LEVERAGE_ROWS:][::-1]
    top_patients = len({design_rows[index]["case_id"] for index in top_indices})
    loo_values = []
    for case_id in sorted({row["case_id"] for row in design_rows}):
        keep = np.array([row["case_id"] != case_id for row in design_rows])
        reduced_values = values[keep]
        reduced_mean = float(np.mean(reduced_values))  # Same centering rule, recomputed per contract.
        reduced_band3 = band3[keep]
        reduced_centered = reduced_values - reduced_mean
        reduced = np.column_stack([np.ones(len(reduced_values)), reduced_band3,
                                   reduced_centered, reduced_band3 * reduced_centered])
        loo_condition, _, loo_rank = condition_number(reduced)
        loo_values.append({"case_id": case_id, "condition_number": loo_condition, "rank": loo_rank})
    assert len(loo_values) == len({row["case_id"] for row in design_rows})

    for index, row in enumerate(design_rows):
        row["centered_hu_imbalance"] = float(centered[index])
        row["band3_indicator"] = int(band3[index])
        row["interaction"] = float(band3[index] * centered[index])
        row["leverage"] = float(leverage[index])

    gates = {
        "rank_4": rank == 4,
        "condition_number_le_30": primary_condition <= CONDITION_LIMIT,
        "each_band_99_cases": all(item["n"] == EXPECTED_CASES_PER_BAND for item in support.values()),
        "each_band_nonzero_iqr": all(item["iqr"] > 0 for item in support.values()),
        "each_band_at_least_20_distinct": all(item["distinct_values"] >= MIN_DISTINCT for item in support.values()),
        "maximum_leverage_le_0_20": float(np.max(leverage)) <= LEVERAGE_LIMIT,
        "top_10_include_at_least_5_patients": top_patients >= MIN_TOP_PATIENTS,
        "all_loo_rank_4": all(item["rank"] == 4 for item in loo_values),
        "all_loo_condition_le_30": all(item["condition_number"] <= CONDITION_LIMIT for item in loo_values),
    }
    diagnostics = {
        "pooled_hu_imbalance_mean": pooled_mean,
        "rank": rank,
        "singular_values": [float(value) for value in singular_values],
        "condition_number": primary_condition,
        "band_support": support,
        "maximum_row_leverage": float(np.max(leverage)),
        "top_10_distinct_patients": top_patients,
        "leave_one_patient_out_condition_min": min(item["condition_number"] for item in loo_values),
        "leave_one_patient_out_condition_max": max(item["condition_number"] for item in loo_values),
        "leave_one_patient_out": loo_values,
        "gates": gates,
    }
    return design_rows, diagnostics


def make_manifest(audit_path, keys_path, audit_rows, outcome_keys, split_record, seed, smoke):
    return {
        "idea_id": IDEA_ID, "contract_version": CONTRACT_VERSION, "smoke": smoke,
        "seed": seed,
        "inputs": [
            {"path": str(audit_path.resolve()), "sha256": sha256_file(audit_path),
             "selected_rows": len(audit_rows), "selected_cases": len({row[0] for row in audit_rows})},
            {"path": str(keys_path.resolve()), "sha256": sha256_file(keys_path),
             "selected_rows": len(outcome_keys), "selected_cases": len({key[0] for key in outcome_keys})},
        ],
        "split_manifest_sha256": split_record["sha256"],
        "split_rows": split_record["rows"],
        "reserved_cases_accessed": 0,
    }


def main():
    args = parse_args()
    random.seed(SEED)
    np.random.seed(SEED)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    log_lines = []

    # PHASE 1 — LOAD AND FREEZE. Verify approval and load only the label-blind
    # audit. Then freeze the census split before the outcome-bearing file is
    # opened, which makes accidental reserved-case access fail visibly.
    log("PHASE 1/4 — load inputs and freeze split before outcome-file access", log_lines)
    log(f"Variant 1/1 — {'synthetic smoke' if args.smoke else 'approved real-input design audit'}; seed={SEED}", log_lines)
    contract_blob = verify_approval(args.smoke)
    if args.smoke:
        audit_rows, outcome_keys = make_smoke_rows()
        smoke_dir = args.output_dir / "smoke_inputs"
        smoke_dir.mkdir(exist_ok=True)
        audit_path = smoke_dir / "bin_tissue_audit.csv"
        keys_path = smoke_dir / "per_patient.csv"
        write_csv(audit_path, ["case_id", "stratum", "style_group", "median_hu"], [
            {"case_id": row[0], "stratum": row[1], "style_group": row[2], "median_hu": row[3]}
            for row in audit_rows
        ])
        write_csv(keys_path, ["case_id", "stratum", "q1_voxels", "q4_voxels", "d"], [
            {"case_id": key[0], "stratum": key[1], "q1_voxels": 100, "q4_voxels": 100,
             "d": "OUTCOME_SENTINEL_MUST_NOT_BE_PARSED"} for key in sorted(outcome_keys)
        ])
        expected_count = 24
    else:
        audit_path = args.audit_csv
        keys_path = args.keys_csv
        for path in (audit_path, keys_path):
            if "test" in str(path).lower() or "reserv" in str(path).lower():
                fail(EXIT_INPUT, f"test/reserved-looking input path refused: {path}")
        audit_rows = load_audit(audit_path)
        expected_count = EXPECTED_CASES_PER_BAND

    cases_by_band, split_record = write_split_before_outcome(args.output_dir, audit_rows, args.smoke)
    log(f"Split frozen: {split_record['rows']} rows, {split_record['unique_cases']} cases, hash {split_record['sha256']}", log_lines)

    # PHASE 2 — VALIDATE. Open the second file only after the split exists;
    # consume case_id and stratum only. Validate one-to-one Q1/Q4 joins and
    # record every excluded non-primary audit cell.
    log("PHASE 2/4 — validate identities, joins, values, and exclusions", log_lines)
    outcome_keys = load_keys_without_outcomes(keys_path)
    design_rows, exclusions = build_design(audit_rows, outcome_keys, expected_count)
    exclusions_path = args.output_dir / "exclusions.csv"
    write_csv(exclusions_path, ["case_id", "stratum", "item", "reason"], exclusions)
    log(f"Validated {len(design_rows)} patient-band rows; exclusions: {len(exclusions)}", log_lines)

    start_manifest = make_manifest(audit_path, keys_path, audit_rows, outcome_keys,
                                   split_record, SEED, args.smoke)
    write_json(args.output_dir / "determinism_manifest_start.json", start_manifest)
    input_manifest_rows = []
    for item in start_manifest["inputs"]:
        input_manifest_rows.append({
            "path": item["path"], "sha256": item["sha256"],
            "selected_rows": item["selected_rows"],
            "selected_cases": item["selected_cases"], "seed": SEED,
        })
    write_csv(args.output_dir / "input_manifest.csv",
              ["path", "sha256", "selected_rows", "selected_cases", "seed"],
              input_manifest_rows)
    print("START DETERMINISM MANIFEST")
    print(json.dumps(start_manifest, indent=2, sort_keys=True))

    # PHASE 3 — MEASURE. Construct exactly the four frozen columns, calculate
    # the scaled condition number, band support, row leverage, and every
    # leave-one-patient-out diagnostic. No outcome is available in memory.
    log("PHASE 3/4 — measure frozen design geometry", log_lines)
    design_rows, diagnostics = measure_design(design_rows)
    for band in PRIMARY_BANDS:
        support = diagnostics["band_support"][str(band)]
        log(f"Band {band}: n={support['n']}, distinct={support['distinct_values']}, IQR={support['iqr']:.6g}", log_lines)
    log(f"Condition number={diagnostics['condition_number']:.6g}; rank={diagnostics['rank']}; max leverage={diagnostics['maximum_row_leverage']:.6g}", log_lines)

    # PHASE 4 — SUMMARIZE. Persist per-row and aggregate diagnostics, reproduce
    # the manifest, assert byte-equivalent content, and report only the
    # contract's feasibility positive/negative pattern.
    log("PHASE 4/4 — write outputs and verify end determinism manifest", log_lines)
    per_row_fields = ["case_id", "stratum", "q1_median_hu", "q4_median_hu",
                      "hu_imbalance", "centered_hu_imbalance", "band3_indicator",
                      "interaction", "leverage"]
    write_csv(args.output_dir / "per_row_design.csv", per_row_fields, design_rows)
    write_json(args.output_dir / "design_diagnostics.json", diagnostics)

    contractual_pass = all(diagnostics["gates"].values()) and not args.smoke
    status = "POSITIVE_PATTERN" if contractual_pass else ("SMOKE_ONLY" if args.smoke else "NEGATIVE_PATTERN")
    summary = {
        "idea_id": IDEA_ID, "status": status, "smoke": args.smoke,
        "contractual_gate_satisfied": contractual_pass,
        "primary_metric": "condition_number",
        "primary_metric_value": diagnostics["condition_number"],
        "gates": diagnostics["gates"],
        "analysis_rows": len(design_rows), "unique_cases": len({row["case_id"] for row in design_rows}),
        "exclusion_rows": len(exclusions), "reserved_cases_accessed": 0,
        "outcome_values_read": 0,
    }
    write_json(args.output_dir / "summary.json", summary)
    resolved = {
        "idea_id": IDEA_ID, "contract_version": CONTRACT_VERSION,
        "contract_blob": contract_blob, "approval_marker": str(APPROVAL_PATH),
        "seed": SEED, "smoke": args.smoke, "primary_bands": list(PRIMARY_BANDS),
        "expected_cases_per_band": expected_count, "condition_limit": CONDITION_LIMIT,
        "leverage_limit": LEVERAGE_LIMIT, "minimum_distinct_values": MIN_DISTINCT,
        "audit_csv": str(audit_path.resolve()), "keys_csv": str(keys_path.resolve()),
        "output_dir": str(args.output_dir.resolve()), "network_calls": 0,
    }
    write_json(args.output_dir / "resolved_config.json", resolved)
    environment = {
        "captured_utc": datetime.now(timezone.utc).isoformat(),
        "python": sys.version, "platform": platform.platform(), "numpy": np.__version__,
        "pid": os.getpid(), "seed": SEED,
    }
    write_json(args.output_dir / "environment.txt", environment)

    end_manifest = make_manifest(audit_path, keys_path, audit_rows, outcome_keys,
                                 split_record, SEED, args.smoke)
    if start_manifest != end_manifest:
        fail(EXIT_OUTPUT, "start and end determinism manifests differ")
    write_json(args.output_dir / "determinism_manifest_end.json", end_manifest)
    print("END DETERMINISM MANIFEST")
    print(json.dumps(end_manifest, indent=2, sort_keys=True))
    log_lines.append("Start/end determinism manifests agree exactly.")
    (args.output_dir / "run_log.txt").write_text("\n".join(log_lines) + "\n", encoding="utf-8")

    print("FINAL summary.json")
    print(json.dumps(summary, indent=2, sort_keys=True))
    if args.smoke:
        interpretation = "SMOKE_ONLY: the harness completed on synthetic inputs and cannot satisfy any contractual gate."
    elif contractual_pass:
        interpretation = "POSITIVE_PATTERN: all integrity and frozen design-feasibility gates passed. This means only that the proposed linear interaction is computationally estimable on the observed exposure geometry."
    else:
        interpretation = "NEGATIVE_PATTERN: valid joined exposure geometry failed at least one frozen design-feasibility gate. The current linear interaction specification requires revision; this is not evidence against tissue composition or the parent association."
    print("PLAIN-ENGLISH INTERPRETATION TEMPLATE")
    print(interpretation)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except ProbeFailure as exc:
        print(f"PROBE FAILURE (exit {exc.code}): {exc}", file=sys.stderr)
        raise SystemExit(exc.code)
    except SystemExit:
        raise
    except Exception:
        traceback.print_exc()
        raise SystemExit(EXIT_INTERNAL)
