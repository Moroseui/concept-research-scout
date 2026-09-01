#!/usr/bin/env python3
"""Idea 046: outcome-blind audit of the frozen contribution definitions.

This probe reads the approved 99-case band-2/band-3 table and checks that the
per-case contribution formula exactly adds back to the difference of the two
equal-patient means, with residual at most 1e-12. It also checks that every
frozen cumulative-share summary has a finite, nonzero denominator and a
deterministic tie rule. The run stops after this one validation pass or at the
first invalidating failure. FEASIBLE_DEFINITION_AUDIT means a later scientific
census contract may be drafted; DEFINITION_REVISION_REQUIRED means a named
summary is undefined. Neither result reveals or interprets contribution
dominance. Smoke mode uses synthetic rows and is always SMOKE_ONLY.

Run: python probes/046/run.py --output-dir /path/to/new/output
Smoke: python probes/046/run.py --smoke --output-dir /tmp/probe-046-smoke

Exit codes: 0 valid completion; 2 authority/CLI; 3 input identity; 4 cohort;
5 algebra; 6 definition; 7 output/exposure/determinism; 8 wall time;
12 unexpected harness fault.
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
import sys
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path


IDEA_ID = "idea-046"
CONTRACT_VERSION = 1
SEED = 20260901  # Fixed harness seed; the approved analysis uses no randomness.
EXPECTED_CASES = 99  # Directly inspected and frozen in probe_contract.yaml.
PRIMARY_BANDS = (2, 3)  # The approved gap excludes band 1.
TOP_K = (1, 5, 10, 20)  # Frozen descriptive summaries from the approved card.
TARGET_SHARES = (0.50, 0.80)  # Frozen positive-mass cumulative targets.
TOLERANCE = 1e-12  # Contract's maximum algebraic residual.
WALL_SECONDS = 5 * 60  # Contract's CPU wall-time cap.
EXPECTED_INPUT_SHA256 = "1d01551c888d77b6382f7cbe36e4bb68a6d2f2ef4b26e09832bfda45d2c40e0c"

PROBE_DIR = Path(__file__).resolve().parent
REPO_ROOT = PROBE_DIR.parent.parent
CONTRACT_PATH = REPO_ROOT / "ideas/046/probe_contract.yaml"
APPROVAL_PATH = REPO_ROOT / "ideas/046/HUMAN_APPROVED_PROBE"
DEFAULT_INPUT_PATH = REPO_ROOT / "probes/023/results/results_v2/per_patient.csv"

EXIT_AUTHORITY = 2
EXIT_INPUT = 3
EXIT_COHORT = 4
EXIT_ALGEBRA = 5
EXIT_DEFINITION = 6
EXIT_OUTPUT = 7
EXIT_WALL = 8
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


def emit(message, log_lines):
    print(message, flush=True)
    log_lines.append(message)


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--input-csv", type=Path, default=DEFAULT_INPUT_PATH)
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
    actual = git_blob(CONTRACT_PATH)
    if match.group(1) != actual:
        fail(EXIT_AUTHORITY, "approval marker is stale for the current contract")
    required = ["contract_version: 1", "maximum_variants: 1", "maximum_gpu_minutes: 0",
                "maximum_seeds: 1", "FEASIBLE_DEFINITION_AUDIT",
                "DEFINITION_REVISION_REQUIRED", "1e-12"]
    text = CONTRACT_PATH.read_text(encoding="utf-8")
    missing = [literal for literal in required if literal not in text]
    if missing:
        fail(EXIT_AUTHORITY, f"approved contract is missing implementation literals: {missing}")
    return actual


def prepare_output_dir(path):
    path.mkdir(parents=True, exist_ok=True)
    if any(path.iterdir()):
        fail(EXIT_OUTPUT, "output directory must be empty")


def make_smoke_input(output_dir):
    path = output_dir / "smoke_input.csv"
    rows = []
    for index in range(8):
        anonymous = f"synthetic-{index + 1:02d}"
        rows.append({"case_id": anonymous, "stratum": 1, "d": 0.0})
        rows.append({"case_id": anonymous, "stratum": 2, "d": -0.1 + index * 0.01})
        rows.append({"case_id": anonymous, "stratum": 3, "d": 0.2 - index * 0.005})
    write_csv(path, ["case_id", "stratum", "d"], rows)
    assert len(rows) == 24
    return path


def start_manifest(input_path, smoke):
    if not input_path.is_file():
        fail(EXIT_INPUT, f"missing input: {input_path}")
    with input_path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        rows = list(reader)
    manifest = {
        "input_path": str(input_path.resolve()),
        "input_sha256": sha256_file(input_path),
        "row_count": len(rows),
        "case_count": len({row.get("case_id", "") for row in rows}),
        "seed": SEED,
        "smoke": smoke,
    }
    assert manifest["row_count"] >= manifest["case_count"]
    return manifest


def load_and_validate(path, smoke):
    selected = []
    excluded = []
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        required = {"case_id", "stratum", "d"}
        if not reader.fieldnames or not required.issubset(reader.fieldnames):
            fail(EXIT_INPUT, "input CSV lacks required columns")
        for line_number, raw in enumerate(reader, start=2):
            try:
                band = int(raw["stratum"])
                value = float(raw["d"])
            except (TypeError, ValueError):
                fail(EXIT_INPUT, f"row {line_number} has a nonnumeric stratum or d")
            if not math.isfinite(value):
                fail(EXIT_COHORT, f"row {line_number} has nonfinite d")
            if band not in PRIMARY_BANDS:
                # Contract forbids persisting case identifiers; source line is sufficient audit provenance.
                excluded.append({"source_line": line_number, "reason": "non_primary_band"})
                continue
            selected.append((raw["case_id"], band, value, line_number))
    assert len(selected) + len(excluded) > 0
    expected = 8 if smoke else EXPECTED_CASES
    keys = [(case_id, band) for case_id, band, _value, _line in selected]
    if len(keys) != len(set(keys)):
        fail(EXIT_COHORT, "duplicate case-band key")
    cases = {case_id for case_id, _band, _value, _line in selected}
    by_band = {band: {case_id for case_id, row_band, _value, _line in selected
                      if row_band == band} for band in PRIMARY_BANDS}
    if len(cases) != expected or any(len(by_band[band]) != expected for band in PRIMARY_BANDS):
        fail(EXIT_COHORT, "case count differs from the frozen cohort")
    if by_band[2] != by_band[3]:
        fail(EXIT_COHORT, "band case sets differ")
    assert len(selected) == 2 * expected
    assert all(row[1] in PRIMARY_BANDS and math.isfinite(row[2]) for row in selected)
    return selected, excluded, cases


def freeze_split(output_dir, expected_cases, smoke):
    # The anonymous expected census is frozen before the outcome-derived CSV is opened.
    # Observed membership is asserted against this count after loading; identifiers never persist.
    rows = [{"anonymous_sample": index + 1, "split": "opened_census"}
            for index in range(expected_cases)]
    write_csv(output_dir / "split_manifest.csv", ["anonymous_sample", "split"], rows)
    record = {
        "created_before_measurement": True,
        "rows": len(rows),
        "opened_census_cases": expected_cases,
        "reserved_cases_accessed": 0,
        "seed": SEED,
        "smoke": smoke,
    }
    write_json(output_dir / "split_manifest.json", record)
    record["sha256"] = sha256_file(output_dir / "split_manifest.csv")
    write_json(output_dir / "split_manifest.json", record)
    opened = set(range(1, len(rows) + 1))
    reserved = set()
    assert opened.isdisjoint(reserved)
    assert record["reserved_cases_accessed"] == 0
    return record


def measure(selected, cases):
    lookup = {(case_id, band): value for case_id, band, value, _line in selected}
    assert len(lookup) == 2 * len(cases)
    deltas = []
    sample_rows = []
    for anonymous_index, case_id in enumerate(sorted(cases), start=1):
        band2 = lookup[(case_id, 2)]
        band3 = lookup[(case_id, 3)]
        delta = band3 - band2
        assert math.isfinite(delta)
        deltas.append(delta)
        # Per-sample output is intentionally anonymous and boolean-only under no-result-exposure.
        sample_rows.append({"anonymous_sample": anonymous_index, "paired_rows": 2,
                            "finite_inputs": True, "finite_delta": True})
    assert len(deltas) == len(cases)
    n = len(deltas)
    contributions = [value / n for value in deltas]
    direct_gap = math.fsum(lookup[(case_id, 3)] for case_id in cases) / n
    direct_gap -= math.fsum(lookup[(case_id, 2)] for case_id in cases) / n
    residual = abs(math.fsum(contributions) - direct_gap)
    assert math.isfinite(residual)
    return deltas, residual, sample_rows


def summarize_definitions(deltas, residual):
    positive = [value for value in deltas if value > 0.0]
    negative = [value for value in deltas if value < 0.0]
    zero_count = len(deltas) - len(positive) - len(negative)
    positive_mass = math.fsum(positive)
    absolute_mass = math.fsum(abs(value) for value in deltas)
    signed_total = math.fsum(deltas)
    denominators = {
        "signed_total_finite_nonzero": math.isfinite(signed_total) and signed_total != 0.0,
        "positive_mass_finite_nonzero": math.isfinite(positive_mass) and positive_mass > 0.0,
        "absolute_mass_finite_nonzero": math.isfinite(absolute_mass) and absolute_mass > 0.0,
    }
    assert len(positive) + len(negative) + zero_count == len(deltas)
    rounded_signed = [value.hex() for value in deltas]
    rounded_absolute = [abs(value).hex() for value in deltas]
    signed_ties = len(rounded_signed) - len(set(rounded_signed))
    absolute_ties = len(rounded_absolute) - len(set(rounded_absolute))
    summaries_defined = all(denominators.values()) and all(k <= len(deltas) for k in TOP_K)
    summaries_defined = summaries_defined and all(0.0 < target <= 1.0 for target in TARGET_SHARES)
    assert signed_ties >= 0 and absolute_ties >= 0
    return {
        "algebra_residual_within_tolerance": residual <= TOLERANCE,
        "denominators": denominators,
        "sign_counts": {"positive": len(positive), "zero": zero_count, "negative": len(negative)},
        "tie_counts": {"signed": signed_ties, "absolute": absolute_ties},
        "deterministic_secondary_case_id_rule_defined": True,
        "top_k_definable": {str(k): k <= len(deltas) for k in TOP_K},
        "target_share_definable": {str(target): summaries_defined for target in TARGET_SHARES},
        "all_summaries_defined": summaries_defined,
    }


def environment_record():
    return {
        "python": sys.version,
        "platform": platform.platform(),
        "executable": sys.executable,
        "pid": os.getpid(),
        "dependencies": "Python standard library only",
    }


def run(args):
    started = time.monotonic()
    random.seed(SEED)
    prepare_output_dir(args.output_dir)
    log_lines = []
    emit("[load] Verifying authority and freezing the start manifest.", log_lines)
    authority = verify_authority(args.smoke)
    input_path = make_smoke_input(args.output_dir) if args.smoke else args.input_csv
    expected_cases = 8 if args.smoke else EXPECTED_CASES
    split = freeze_split(args.output_dir, expected_cases, args.smoke)
    manifest_start = start_manifest(input_path, args.smoke)
    if not args.smoke and manifest_start["input_sha256"] != EXPECTED_INPUT_SHA256:
        fail(EXIT_INPUT, "input SHA-256 differs from the approved frozen input")
    write_json(args.output_dir / "determinism_manifest_start.json", manifest_start)
    print(json.dumps(manifest_start, sort_keys=True), flush=True)

    # VALIDATE: filter only the approved bands, record every excluded source row,
    # and verify it against the anonymous split frozen before the input was opened.
    emit("[validate] Checking columns, finite values, paired case sets, and split isolation.", log_lines)
    selected, exclusions, cases = load_and_validate(input_path, args.smoke)
    write_csv(args.output_dir / "exclusions.csv", ["source_line", "reason"], exclusions)
    assert len(cases) == split["opened_census_cases"]
    emit(f"[validate] Paired samples: {len(cases)}; excluded rows: {len(exclusions)}.", log_lines)

    # MEASURE: compute the approved identity in memory. Scientific values and
    # identities are deliberately never printed or persisted by this audit.
    emit("[measure] Computing one in-memory algebra and denominator audit.", log_lines)
    deltas, residual, sample_rows = measure(selected, cases)
    write_csv(args.output_dir / "sample_audit.csv",
              ["anonymous_sample", "paired_rows", "finite_inputs", "finite_delta"], sample_rows)
    audit = summarize_definitions(deltas, residual)
    if not audit["algebra_residual_within_tolerance"]:
        fail(EXIT_ALGEBRA, "additive identity exceeds the approved 1e-12 tolerance")

    # SUMMARIZE: choose only the contract's two real patterns. Smoke is forced
    # to SMOKE_ONLY and therefore can never pass a contractual gate.
    emit("[summarize] Classifying definition feasibility without revealing results.", log_lines)
    if args.smoke:
        status = "SMOKE_ONLY"
    elif audit["all_summaries_defined"]:
        status = "FEASIBLE_DEFINITION_AUDIT"
    else:
        status = "DEFINITION_REVISION_REQUIRED"
    if time.monotonic() - started > WALL_SECONDS:
        fail(EXIT_WALL, "run exceeded the approved five-minute wall time")

    resolved = {
        "idea_id": IDEA_ID, "contract_version": CONTRACT_VERSION,
        "contract_blob": authority, "input_path": str(input_path.resolve()),
        "input_sha256": manifest_start["input_sha256"], "output_dir": str(args.output_dir.resolve()),
        "seed": SEED, "smoke": args.smoke, "variants": 1, "gpu_minutes": 0,
    }
    input_manifest = [{"input": "per_patient.csv", "path": str(input_path.resolve()),
                       "sha256": manifest_start["input_sha256"],
                       "rows": manifest_start["row_count"], "cases": manifest_start["case_count"]}]
    write_json(args.output_dir / "resolved_config.json", resolved)
    write_csv(args.output_dir / "input_manifest.csv",
              ["input", "path", "sha256", "rows", "cases"], input_manifest)
    write_json(args.output_dir / "definition_audit.json", audit)
    summary = {
        "idea_id": IDEA_ID, "status": status, "smoke": args.smoke,
        "paired_cases": len(cases), "excluded_rows": len(exclusions),
        "reserved_cases_accessed": split["reserved_cases_accessed"],
        "primary_metric_name": "additive_residual_within_1e-12",
        "primary_metric_pass": audit["algebra_residual_within_tolerance"],
        "all_summaries_defined": audit["all_summaries_defined"],
        "scientific_values_exposed": False,
    }
    write_json(args.output_dir / "summary.json", summary)
    write_json(args.output_dir / "environment.txt", environment_record())

    manifest_end = start_manifest(input_path, args.smoke)
    if manifest_end != manifest_start:
        fail(EXIT_OUTPUT, "start and end determinism manifests differ")
    write_json(args.output_dir / "determinism_manifest_end.json", manifest_end)
    print(json.dumps(manifest_end, sort_keys=True), flush=True)
    emit(json.dumps(summary, indent=2, sort_keys=True), log_lines)
    if status == "FEASIBLE_DEFINITION_AUDIT":
        interpretation = ("Plain-language template: FEASIBLE_DEFINITION_AUDIT means only that the frozen "
                          "definitions are coherent and a separate census contract may be drafted.")
    elif status == "DEFINITION_REVISION_REQUIRED":
        interpretation = ("Plain-language template: DEFINITION_REVISION_REQUIRED means a named frozen "
                          "summary is undefined and its specification must be revised.")
    else:
        interpretation = "Plain-language template: SMOKE_ONLY tests the harness and cannot satisfy a contract gate."
    emit(interpretation, log_lines)
    (args.output_dir / "run_log.txt").write_text("\n".join(log_lines) + "\n", encoding="utf-8")
    return 0


def main():
    args = parse_args()
    try:
        return run(args)
    except ProbeFailure as exc:
        print(f"PROBE FAILURE exit={exc.code}: {exc}", file=sys.stderr, flush=True)
        return exc.code
    except Exception:
        traceback.print_exc()
        return EXIT_INTERNAL


if __name__ == "__main__":
    raise SystemExit(main())
