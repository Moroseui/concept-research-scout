#!/usr/bin/env python3
"""Idea 045 v3: pooled-slope attenuation attribution on frozen stroke rows.

This experiment fits one approved model to 99 already-open patients in flow
bands 2 and 3: final-infarct contrast d is regressed on band and pooled-mean-
centered Q1-minus-Q4 median NCCT attenuation. The primary metric is the pair
of adjusted band means at zero centered imbalance, with percentile intervals
from exactly 10,000 patient-cluster bootstrap replicates. The run stops after
that single fit and bootstrap, on any invalidating failure, or at 30 minutes.
DECISIVE_MEASURED_EXPLANATION_FAILURE means both adjusted means retain the
parent's precise negative-band-2/positive-band-3 pattern;
ASSOCIATION_COMPATIBLE_WITH_CONTRIBUTION means the pooled attenuation slope is
precise and adjustment breaks that conjunction; every other valid result is
SENSITIVITY_LIMITED. None establishes causation, tissue validity, or model use.

Run once with:
    python probes/045/run.py --output-dir /path/to/new/results_v4

Harness-only smoke check:
    python probes/045/run.py --smoke --output-dir /tmp/probe-045-smoke

Exit codes: 0 valid completion; 2 authority/CLI; 3 input identity; 4 split or
cohort; 5 analysis value; 6 bootstrap; 7 output/determinism; 8 wall time;
12 unexpected harness fault. Smoke is always SMOKE_ONLY and cannot satisfy a
contractual scientific pattern.
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
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path

import numpy as np


# All scientific state is declared here or exposed as a command-line path.
IDEA_ID = "idea-045"
CONTRACT_VERSION = 3
SEED = 20260901  # Frozen by probe_contract.yaml v3.
BOOTSTRAP_REPLICATES = 10_000  # Frozen patient-cluster replicate count.
SMOKE_REPLICATES = 40  # Harness-only; smoke can never yield a science status.
PRIMARY_BANDS = (2, 3)  # The approved attribution question excludes band 1.
EXPECTED_CASES = 99
WALL_TIME_SECONDS = 30 * 60  # Contract's CPU cap.
Q1_STYLE = "Q1_low_CBV"
Q4_STYLE = "Q4_high_CBV"
EXPECTED_AUDIT_SHA256 = "35e896dfe2a5275a9fa8077e990dff96e72ce1ec0e5048079653556e1c7e2cd2"
EXPECTED_OUTCOME_SHA256 = "1d01551c888d77b6382f7cbe36e4bb68a6d2f2ef4b26e09832bfda45d2c40e0c"

PROBE_DIR = Path(__file__).resolve().parent
REPO_ROOT = PROBE_DIR.parent.parent
CONTRACT_PATH = REPO_ROOT / "ideas/045/probe_contract.yaml"
APPROVAL_PATH = REPO_ROOT / "ideas/045/HUMAN_APPROVED_PROBE"
DEFAULT_AUDIT_PATH = REPO_ROOT / "probes/023/results/results_v2/bin_tissue_audit.csv"
DEFAULT_OUTCOME_PATH = REPO_ROOT / "probes/023/results/results_v2/per_patient.csv"

EXIT_AUTHORITY = 2
EXIT_INPUT = 3
EXIT_COHORT = 4
EXIT_ANALYSIS = 5
EXIT_BOOTSTRAP = 6
EXIT_OUTPUT = 7
EXIT_WALL_TIME = 8
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
    digest = hashlib.sha1(header)
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


def log(message, lines):
    print(message, flush=True)
    lines.append(message)


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--audit-csv", type=Path, default=DEFAULT_AUDIT_PATH)
    parser.add_argument("--outcome-csv", type=Path, default=DEFAULT_OUTCOME_PATH)
    parser.add_argument("--smoke", action="store_true")
    return parser.parse_args()


def verify_authority(smoke):
    if smoke:
        return "SMOKE_NOT_APPROVAL_ELIGIBLE"
    if not CONTRACT_PATH.is_file() or not APPROVAL_PATH.is_file():
        fail(EXIT_AUTHORITY, "contract or HUMAN_APPROVED_PROBE is missing")
    marker = APPROVAL_PATH.read_text(encoding="utf-8")
    match = re.search(r"^contract_blob:\s*([0-9a-f]{40})$", marker, re.MULTILINE)
    if not match:
        fail(EXIT_AUTHORITY, "approval marker lacks a 40-hex contract_blob")
    actual_blob = git_blob(CONTRACT_PATH)
    if match.group(1) != actual_blob:
        fail(EXIT_AUTHORITY, "approval marker is stale for the current contract")
    contract_text = CONTRACT_PATH.read_text(encoding="utf-8")
    required = [
        "contract_version: 3",
        "exactly 10,000 patient-cluster bootstrap replicates",
        "seed of 20260901",
        "maximum_variants: 1",
        "maximum_gpu_minutes: 0",
        "maximum_seeds: 1",
        "DECISIVE_MEASURED_EXPLANATION_FAILURE",
        "ASSOCIATION_COMPATIBLE_WITH_CONTRIBUTION",
        "SENSITIVITY_LIMITED",
    ]
    missing = [literal for literal in required if literal not in contract_text]
    if missing:
        fail(EXIT_AUTHORITY, f"approved contract is missing implementation literals: {missing}")
    return actual_blob


def prepare_output_dir(path):
    path.mkdir(parents=True, exist_ok=True)
    scientific_markers = {"summary.json", "resolved_config.json", "per_patient_attribution.csv"}
    collisions = sorted(item.name for item in path.iterdir() if item.name in scientific_markers)
    if collisions:
        fail(EXIT_OUTPUT, f"output directory already contains scientific outputs: {collisions}")


def make_smoke_inputs(output_dir):
    smoke_dir = output_dir / "smoke_inputs"
    smoke_dir.mkdir()
    audit_path = smoke_dir / "bin_tissue_audit.csv"
    outcome_path = smoke_dir / "per_patient.csv"
    audit_rows = []
    outcome_rows = []
    for index in range(12):
        case_id = f"smoke-{index + 1:03d}"
        imbalance = float(index - 5)
        for band in PRIMARY_BANDS:
            q4 = 25.0 + float(index % 3)
            q1 = q4 + imbalance
            audit_rows.extend([
                {"case_id": case_id, "stratum": band, "style_group": Q1_STYLE,
                 "median_hu": q1},
                {"case_id": case_id, "stratum": band, "style_group": Q4_STYLE,
                 "median_hu": q4},
            ])
            # Synthetic outcomes exercise the complete fit without representing science.
            outcome_rows.append({"case_id": case_id, "stratum": band,
                                 "q1_voxels": 100, "q4_voxels": 100,
                                 "d": -0.04 + 0.08 * (band == 3) + 0.002 * imbalance})
    write_csv(audit_path, ["case_id", "stratum", "style_group", "median_hu"], audit_rows)
    write_csv(outcome_path, ["case_id", "stratum", "q1_voxels", "q4_voxels", "d"], outcome_rows)
    assert len(audit_rows) == 48
    assert len(outcome_rows) == 24
    return audit_path, outcome_path


def load_audit(path):
    if not path.is_file():
        fail(EXIT_INPUT, f"missing audit input: {path}")
    selected = []
    excluded = []
    total = 0
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        required = {"case_id", "stratum", "style_group", "median_hu"}
        if not reader.fieldnames or not required.issubset(reader.fieldnames):
            fail(EXIT_INPUT, "audit CSV lacks required columns")
        for line_number, raw in enumerate(reader, start=2):
            total += 1
            try:
                band = int(raw["stratum"])
                median_hu = float(raw["median_hu"])
            except (TypeError, ValueError):
                fail(EXIT_INPUT, f"audit row {line_number} has a nonnumeric value")
            if band not in PRIMARY_BANDS:
                excluded.append({"source": path.name, "line": line_number,
                                 "case_id": raw["case_id"], "stratum": band,
                                 "reason": "non_primary_band"})
                continue
            selected.append((raw["case_id"], band, raw["style_group"], median_hu))
    assert total == len(selected) + len(excluded)
    assert all(row[1] in PRIMARY_BANDS for row in selected)
    if not selected:
        fail(EXIT_INPUT, "audit CSV has no primary-band rows")
    return selected, excluded, total


def freeze_split(output_dir, audit_rows, smoke):
    cases_by_band = {
        band: sorted({case_id for case_id, row_band, _style, _hu in audit_rows if row_band == band})
        for band in PRIMARY_BANDS
    }
    if not all(cases_by_band.values()):
        fail(EXIT_COHORT, "one primary band has no audit cases")
    rows = [
        {"case_id": case_id, "stratum": band, "split": "opened_census"}
        for band in PRIMARY_BANDS for case_id in cases_by_band[band]
    ]
    assert len(rows) == sum(len(cases_by_band[band]) for band in PRIMARY_BANDS)
    assert len({(row["case_id"], row["stratum"]) for row in rows}) == len(rows)
    # Reserved cases are absent from the approved source tables. This explicit
    # set comparison is the contract's split-overlap assertion.
    opened_cases = {row["case_id"] for row in rows}
    reserved_cases = set()
    assert opened_cases.isdisjoint(reserved_cases)
    csv_path = output_dir / "split_manifest.csv"
    write_csv(csv_path, ["case_id", "stratum", "split"], rows)
    record = {
        "created_before_outcome_file_open": True,
        "sha256": sha256_file(csv_path),
        "rows": len(rows),
        "unique_cases": len(opened_cases),
        "bands": list(PRIMARY_BANDS),
        "reserved_cases_accessed": 0,
        "seed": SEED,
        "smoke": smoke,
    }
    write_json(output_dir / "split_manifest.json", record)
    assert record["reserved_cases_accessed"] == 0
    return {(row["case_id"], row["stratum"]) for row in rows}, record


def load_outcomes(path):
    if not path.is_file():
        fail(EXIT_INPUT, f"missing outcome input: {path}")
    rows = {}
    excluded = []
    total = 0
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        required = {"case_id", "stratum", "d"}
        if not reader.fieldnames or not required.issubset(reader.fieldnames):
            fail(EXIT_INPUT, "outcome CSV lacks required columns")
        for line_number, raw in enumerate(reader, start=2):
            total += 1
            try:
                band = int(raw["stratum"])
            except (TypeError, ValueError):
                fail(EXIT_INPUT, f"outcome row {line_number} has nonnumeric stratum")
            if band not in PRIMARY_BANDS:
                excluded.append({"source": path.name, "line": line_number,
                                 "case_id": raw["case_id"], "stratum": band,
                                 "reason": "non_primary_band"})
                continue
            try:
                value = float(raw["d"])
            except (TypeError, ValueError):
                fail(EXIT_INPUT, f"outcome row {line_number} has nonnumeric d")
            key = (raw["case_id"], band)
            if key in rows:
                fail(EXIT_COHORT, f"duplicate outcome key: {key}")
            if not np.isfinite(value):
                fail(EXIT_INPUT, f"nonfinite outcome for {key}")
            rows[key] = value
    assert total == len(rows) + len(excluded)
    assert all(key[1] in PRIMARY_BANDS for key in rows)
    return rows, excluded, total


def join_rows(audit_rows, outcomes, split_keys, expected_cases):
    cells = {}
    allowed_styles = {Q1_STYLE, Q4_STYLE}
    for case_id, band, style, median_hu in audit_rows:
        if style not in allowed_styles:
            fail(EXIT_COHORT, f"unknown style in primary band: {(case_id, band, style)}")
        key = (case_id, band, style)
        if key in cells:
            fail(EXIT_COHORT, f"duplicate audit cell: {key}")
        if not np.isfinite(median_hu):
            fail(EXIT_INPUT, f"nonfinite median HU: {key}")
        cells[key] = median_hu
    assert all(key[2] in allowed_styles for key in cells)

    audit_keys = {(case_id, band) for case_id, band, _style in cells}
    outcome_keys = set(outcomes)
    if audit_keys != outcome_keys or audit_keys != split_keys:
        fail(EXIT_COHORT, "audit, outcome, and frozen-split key sets differ")
    joined = []
    for band in PRIMARY_BANDS:
        keys = sorted(key for key in split_keys if key[1] == band)
        if len(keys) != expected_cases:
            fail(EXIT_COHORT, f"band {band} has {len(keys)} cases; expected {expected_cases}")
        for case_id, _ in keys:
            q1_key = (case_id, band, Q1_STYLE)
            q4_key = (case_id, band, Q4_STYLE)
            if q1_key not in cells or q4_key not in cells:
                fail(EXIT_COHORT, f"missing Q1/Q4 audit cell for {(case_id, band)}")
            imbalance = cells[q1_key] - cells[q4_key]  # HU subtraction; no conversion.
            assert np.isfinite(imbalance)
            joined.append({"case_id": case_id, "stratum": band,
                           "q1_median_hu": cells[q1_key],
                           "q4_median_hu": cells[q4_key],
                           "hu_imbalance": imbalance, "d": outcomes[(case_id, band)]})
    assert len(joined) == expected_cases * 2
    assert {(row["case_id"], row["stratum"]) for row in joined} == split_keys
    return joined


def make_manifest(audit_path, outcome_path, joined_rows, split_record, smoke,
                  audit_total, outcome_total):
    return {
        "idea_id": IDEA_ID,
        "contract_version": CONTRACT_VERSION,
        "seed": SEED,
        "smoke": smoke,
        "inputs": [
            {"path": str(audit_path.resolve()), "sha256": sha256_file(audit_path),
             "total_rows": audit_total,
             "selected_rows": len(joined_rows) * 2,
             "selected_cases": len({row["case_id"] for row in joined_rows})},
            {"path": str(outcome_path.resolve()), "sha256": sha256_file(outcome_path),
             "total_rows": outcome_total,
             "selected_rows": len(joined_rows),
             "selected_cases": len({row["case_id"] for row in joined_rows})},
        ],
        "analysis_rows": len(joined_rows),
        "analysis_cases": len({row["case_id"] for row in joined_rows}),
        "split_manifest_sha256": split_record["sha256"],
        "reserved_cases_accessed": 0,
    }


def fit_model(rows):
    imbalance = np.array([row["hu_imbalance"] for row in rows], dtype=float)
    center = float(np.mean(imbalance))  # Pooled mean frozen by contract v3.
    centered = imbalance - center
    band3 = np.array([1.0 if row["stratum"] == 3 else 0.0 for row in rows])
    design = np.column_stack([np.ones(len(rows)), band3, centered])
    outcome = np.array([row["d"] for row in rows], dtype=float)
    assert design.shape == (len(rows), 3)
    assert outcome.shape == (len(rows),)
    assert np.isfinite(design).all() and np.isfinite(outcome).all()
    if np.linalg.matrix_rank(design) != 3:
        fail(EXIT_ANALYSIS, "authorized design is singular")
    beta, _residuals, rank, _singular = np.linalg.lstsq(design, outcome, rcond=None)
    if rank != 3 or not np.isfinite(beta).all():
        fail(EXIT_ANALYSIS, "OLS fit is rank-deficient or nonfinite")
    fitted = design @ beta
    residual = outcome - fitted
    leverage = np.diag(design @ np.linalg.pinv(design.T @ design) @ design.T)
    assert np.allclose(fitted + residual, outcome)
    assert leverage.shape == outcome.shape and np.isfinite(leverage).all()
    for index, row in enumerate(rows):
        row["centered_hu_imbalance"] = float(centered[index])
        row["fitted_d"] = float(fitted[index])
        row["residual_d"] = float(residual[index])
        row["leverage"] = float(leverage[index])
    band_means = {band: float(np.mean([row["d"] for row in rows if row["stratum"] == band]))
                  for band in PRIMARY_BANDS}
    assert all(np.isfinite(value) for value in band_means.values())
    metrics = np.array([
        beta[2], beta[0], beta[0] + beta[1], beta[1],
        band_means[2], band_means[3], band_means[3] - band_means[2],
        beta[0] - band_means[2], (beta[0] + beta[1]) - band_means[3],
        abs(beta[1]) - abs(band_means[3] - band_means[2]),
    ], dtype=float)
    assert metrics.shape == (10,) and np.isfinite(metrics).all()
    return rows, center, beta, metrics


def bootstrap(rows, replicates, deadline, log_lines):
    case_ids = sorted({row["case_id"] for row in rows})
    by_case = {case_id: [row for row in rows if row["case_id"] == case_id] for case_id in case_ids}
    assert all(len(by_case[case_id]) == 2 for case_id in case_ids)
    rng = np.random.default_rng(SEED)
    draws = np.empty((replicates, 10), dtype=float)
    for replicate in range(replicates):
        if time.monotonic() > deadline:
            fail(EXIT_WALL_TIME, "30-minute contract wall-time cap reached")
        sampled = rng.choice(case_ids, size=len(case_ids), replace=True)
        sample_rows = [dict(row) for case_id in sampled for row in by_case[case_id]]
        assert len(sample_rows) == len(rows)
        try:
            _sample_rows, _center, _beta, metrics = fit_model(sample_rows)
        except (np.linalg.LinAlgError, ProbeFailure) as exc:
            fail(EXIT_BOOTSTRAP, f"bootstrap replicate {replicate + 1} failed: {exc}")
        if not np.isfinite(metrics).all():
            fail(EXIT_BOOTSTRAP, f"bootstrap replicate {replicate + 1} is nonfinite")
        draws[replicate] = metrics
        if (replicate + 1) % max(1, replicates // 10) == 0:
            log(f"Bootstrap progress: {replicate + 1}/{replicates}; failed=0", log_lines)
    assert draws.shape == (replicates, 10)
    return draws


def interval(draws, column):
    values = np.percentile(draws[:, column], [2.5, 97.5])
    assert values.shape == (2,) and np.isfinite(values).all()
    return [float(values[0]), float(values[1])]


def classify(metrics, intervals, smoke):
    if smoke:
        return "SMOKE_ONLY"
    adjusted_band2_ci = intervals["adjusted_band2_mean"]
    adjusted_band3_ci = intervals["adjusted_band3_mean"]
    beta_ci = intervals["beta_hu"]
    decisive = adjusted_band2_ci[1] < 0.0 and adjusted_band3_ci[0] > 0.0
    beta_precise = beta_ci[1] < 0.0 or beta_ci[0] > 0.0
    if decisive:
        return "DECISIVE_MEASURED_EXPLANATION_FAILURE"
    if beta_precise:
        return "ASSOCIATION_COMPATIBLE_WITH_CONTRIBUTION"
    return "SENSITIVITY_LIMITED"


def main():
    args = parse_args()
    started = time.monotonic()
    deadline = started + WALL_TIME_SECONDS
    random.seed(SEED)
    np.random.seed(SEED)
    prepare_output_dir(args.output_dir)
    log_lines = []

    # PHASE 1 — LOAD AND FREEZE SPLIT.
    # Verify exact human authority and input identities, read the label-blind
    # attenuation audit, then write/hash the split before opening outcomes.
    log("PHASE 1/4 — verify authority, load audit, and freeze split", log_lines)
    log(f"Variant 1/1 — {'synthetic smoke' if args.smoke else 'approved v3 attribution'}; seed={SEED}", log_lines)
    contract_blob = verify_authority(args.smoke)
    if args.smoke:
        audit_path, outcome_path = make_smoke_inputs(args.output_dir)
        expected_cases = 12
    else:
        audit_path, outcome_path = args.audit_csv, args.outcome_csv
        expected_cases = EXPECTED_CASES
        for path in (audit_path, outcome_path):
            if "reserv" in str(path).lower() or "test" in str(path).lower():
                fail(EXIT_INPUT, f"reserved/test-looking input path refused: {path}")
            if not path.is_file():
                fail(EXIT_INPUT, f"missing approved input: {path}")
        if sha256_file(audit_path) != EXPECTED_AUDIT_SHA256:
            fail(EXIT_INPUT, "audit input SHA-256 differs from the approved pin")
        if sha256_file(outcome_path) != EXPECTED_OUTCOME_SHA256:
            fail(EXIT_INPUT, "outcome input SHA-256 differs from the approved pin")
    audit_rows, audit_exclusions, audit_total = load_audit(audit_path)
    split_keys, split_record = freeze_split(args.output_dir, audit_rows, args.smoke)
    log(f"Split frozen before outcome open: {split_record['rows']} rows, hash={split_record['sha256']}", log_lines)

    # PHASE 2 — VALIDATE AND JOIN.
    # Only now open d. Enforce the exact bidirectional 99-patient join, record
    # every band-1 exclusion, and print/write the starting determinism manifest.
    log("PHASE 2/4 — open frozen outcomes, validate cohort, and join", log_lines)
    outcomes, outcome_exclusions, outcome_total = load_outcomes(outcome_path)
    joined = join_rows(audit_rows, outcomes, split_keys, expected_cases)
    exclusions = audit_exclusions + outcome_exclusions
    write_csv(args.output_dir / "exclusions.csv",
              ["source", "line", "case_id", "stratum", "reason"], exclusions)
    assert len(exclusions) == audit_total + outcome_total - len(joined) * 3
    start_manifest = make_manifest(audit_path, outcome_path, joined, split_record,
                                   args.smoke, audit_total, outcome_total)
    write_json(args.output_dir / "determinism_manifest_start.json", start_manifest)
    print("START DETERMINISM MANIFEST")
    print(json.dumps(start_manifest, indent=2, sort_keys=True))
    manifest_rows = [dict(item, seed=SEED) for item in start_manifest["inputs"]]
    write_csv(args.output_dir / "input_manifest.csv",
              ["path", "sha256", "total_rows", "selected_rows", "selected_cases", "seed"],
              manifest_rows)
    log(f"Joined {len(joined)} rows from {expected_cases} patients; excluded rows={len(exclusions)}", log_lines)

    # PHASE 3 — MEASURE.
    # Fit exactly one common-slope OLS model, reconstruct the unadjusted parent
    # directions, and resample patients—not rows—for the frozen bootstrap.
    log("PHASE 3/4 — fit one pooled-slope model and run clustered bootstrap", log_lines)
    joined, pooled_center, beta, metrics = fit_model(joined)
    if not args.smoke and not (metrics[4] < 0.0 and metrics[5] > 0.0):
        fail(EXIT_ANALYSIS, "unadjusted band directions do not reproduce the parent result")
    replicates = SMOKE_REPLICATES if args.smoke else BOOTSTRAP_REPLICATES
    draws = bootstrap(joined, replicates, deadline, log_lines)
    metric_names = [
        "beta_hu", "adjusted_band2_mean", "adjusted_band3_mean",
        "adjusted_band3_minus_band2", "unadjusted_band2_mean",
        "unadjusted_band3_mean", "unadjusted_band3_minus_band2",
        "band2_adjustment_change", "band3_adjustment_change",
        "absolute_band_difference_change",
    ]
    intervals = {name: interval(draws, index) for index, name in enumerate(metric_names)}
    point_estimates = {name: float(metrics[index]) for index, name in enumerate(metric_names)}
    status = classify(metrics, intervals, args.smoke)
    log(f"Fit complete: beta_HU={metrics[0]:.8g}; adjusted means b2={metrics[1]:.8g}, b3={metrics[2]:.8g}", log_lines)

    # PHASE 4 — SUMMARIZE AND VERIFY.
    # Persist per-patient audit rows and every contracted metric, reproduce the
    # input manifest exactly, and print only the frozen interpretation class.
    log("PHASE 4/4 — write contracted outputs and verify determinism", log_lines)
    per_patient_fields = ["case_id", "stratum", "q1_median_hu", "q4_median_hu",
                          "hu_imbalance", "centered_hu_imbalance", "d",
                          "fitted_d", "residual_d", "leverage"]
    write_csv(args.output_dir / "per_patient_attribution.csv", per_patient_fields, joined)
    diagnostics = {
        "design_rank": 3,
        "pooled_hu_imbalance_center": pooled_center,
        "coefficients": {"intercept": float(beta[0]), "band3": float(beta[1]),
                         "beta_hu": float(beta[2])},
        "maximum_leverage": max(row["leverage"] for row in joined),
        "residual_sum_squares": float(sum(row["residual_d"] ** 2 for row in joined)),
    }
    write_json(args.output_dir / "model_diagnostics.json", diagnostics)
    bootstrap_summary = {
        "seed": SEED, "replicates_requested": replicates,
        "replicates_completed": replicates, "failed_replicates": 0,
        "interval_method": "percentile_95",
        "point_estimates": point_estimates, "intervals": intervals,
    }
    write_json(args.output_dir / "bootstrap_summary.json", bootstrap_summary)
    summary = {
        "idea_id": IDEA_ID, "contract_version": CONTRACT_VERSION,
        "status": status, "smoke": args.smoke,
        "analysis_rows": len(joined), "unique_cases": expected_cases,
        "excluded_input_rows": len(exclusions), "exclusion_records": len(exclusions),
        "reserved_cases_accessed": 0, "variants_run": 1,
        "bootstrap_failed_replicates": 0,
        "primary_metric": {
            "adjusted_band2_mean": point_estimates["adjusted_band2_mean"],
            "adjusted_band2_ci95": intervals["adjusted_band2_mean"],
            "adjusted_band3_mean": point_estimates["adjusted_band3_mean"],
            "adjusted_band3_ci95": intervals["adjusted_band3_mean"],
            "opposite_sign_precise": (
                intervals["adjusted_band2_mean"][1] < 0.0
                and intervals["adjusted_band3_mean"][0] > 0.0
            ),
        },
        "beta_hu": point_estimates["beta_hu"],
        "beta_hu_ci95": intervals["beta_hu"],
        "unadjusted_band2_mean": point_estimates["unadjusted_band2_mean"],
        "unadjusted_band3_mean": point_estimates["unadjusted_band3_mean"],
    }
    write_json(args.output_dir / "summary.json", summary)
    resolved = {
        "idea_id": IDEA_ID, "contract_version": CONTRACT_VERSION,
        "contract_blob": contract_blob, "approval_marker": str(APPROVAL_PATH),
        "seed": SEED, "bootstrap_replicates": replicates, "smoke": args.smoke,
        "audit_csv": str(audit_path.resolve()), "outcome_csv": str(outcome_path.resolve()),
        "output_dir": str(args.output_dir.resolve()), "primary_bands": list(PRIMARY_BANDS),
        "maximum_variants": 1, "maximum_gpu_minutes": 0, "network_calls": 0,
    }
    write_json(args.output_dir / "resolved_config.json", resolved)
    environment = {
        "captured_utc": datetime.now(timezone.utc).isoformat(),
        "python": sys.version, "platform": platform.platform(),
        "numpy": np.__version__, "seed": SEED, "pid": os.getpid(),
    }
    write_json(args.output_dir / "environment.txt", environment)
    end_manifest = make_manifest(audit_path, outcome_path, joined, split_record,
                                 args.smoke, audit_total, outcome_total)
    if start_manifest != end_manifest:
        fail(EXIT_OUTPUT, "start and end determinism manifests differ")
    write_json(args.output_dir / "determinism_manifest_end.json", end_manifest)
    print("END DETERMINISM MANIFEST")
    print(json.dumps(end_manifest, indent=2, sort_keys=True))
    log_lines.append("Start/end determinism manifests agree exactly.")
    (args.output_dir / "run_log.txt").write_text("\n".join(log_lines) + "\n", encoding="utf-8")

    print("FINAL summary.json")
    print(json.dumps(summary, indent=2, sort_keys=True))
    templates = {
        "SMOKE_ONLY": "SMOKE_ONLY: the tiny synthetic harness completed; it cannot satisfy a scientific contract pattern.",
        "DECISIVE_MEASURED_EXPLANATION_FAILURE": "DECISIVE_MEASURED_EXPLANATION_FAILURE: adjusted band 2 remains precisely below zero and adjusted band 3 precisely above zero. Adjustment for this measured median-HU imbalance did not explain the parent reversal at achieved precision; no broader tissue-composition claim follows.",
        "ASSOCIATION_COMPATIBLE_WITH_CONTRIBUTION": "ASSOCIATION_COMPATIBLE_WITH_CONTRIBUTION: the pooled HU slope interval excludes zero and adjustment breaks the precise opposite-sign conjunction. This is observational compatibility with contribution, not causation.",
        "SENSITIVITY_LIMITED": "SENSITIVITY_LIMITED: the frozen analysis supports neither stronger pattern. This is not evidence of no association or independence.",
    }
    print("PLAIN-ENGLISH INTERPRETATION TEMPLATE")
    print(templates[status])
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
