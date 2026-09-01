#!/usr/bin/env python3
"""Idea 046: finite-population contribution census (contract version 2).

This experiment reads the approved 99-case band-2/band-3 table and emits the
complete, deterministic accounting of each observed case's contribution to the
equal-patient band-3-minus-band-2 mean contrast. Its primary metric is the full
ordered per-case contribution table and signed cumulative sequence; the run
stops after one frozen CPU-only census or at the first invalidating failure.
CENSUS_COMPLETE means every approved output was written and all identity,
cohort, algebra, denominator, ordering, and scope gates passed. There is no
directional negative pattern: any curve shape is a descriptive result, while a
failed gate is invalid rather than scientific evidence. Smoke mode uses
synthetic rows and is always SMOKE_ONLY.

Run: python probes/046/run.py --output-dir /path/to/new/output
Smoke: python probes/046/run.py --smoke --output-dir /tmp/probe-046-smoke

Exit codes: 0 valid completion; 2 authority/CLI; 3 input identity; 4 cohort;
5 algebra/definition; 6 scope; 7 output/determinism; 8 wall time;
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
CONTRACT_VERSION = 2
SEED = 20260901  # Fixed harness seed; the approved analysis uses no randomness.
EXPECTED_CASES = 99  # Directly inspected and frozen in probe_contract.yaml.
SMOKE_CASES = 24  # At least 20 so smoke exercises every frozen top-k summary.
PRIMARY_BANDS = (2, 3)  # The approved gap excludes band 1.
TOP_K = (1, 5, 10, 20)  # Frozen descriptive summaries from the approved card.
TARGET_SHARES = (0.50, 0.80)  # Frozen positive-mass cumulative targets.
TOLERANCE = 1e-12  # Contract's maximum algebraic residual.
WALL_SECONDS = 5 * 60  # Contract's CPU wall-time cap.
EXPECTED_INPUT_SHA256 = "1d01551c888d77b6382f7cbe36e4bb68a6d2f2ef4b26e09832bfda45d2c40e0c"

# Frozen lineage guards from contract v2 baselines[0], produced by the
# completed v1 definition audit. These are validity checks, not comparators.
V1_RESIDUAL = 6.938893903907228e-18
V1_SIGN_COUNTS = {"positive": 54, "zero": 6, "negative": 39}
V1_TIE_COUNTS_DELTA_SPACE = {"signed": 5, "absolute": 5}

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
    required = ["contract_version: 2", "maximum_variants: 1", "maximum_gpu_minutes: 0",
                "maximum_seeds: 1", "CENSUS_COMPLETE",
                "NO DIRECTIONAL NEGATIVE IS DEFINED", "1e-12"]
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
    for index in range(SMOKE_CASES):
        anonymous = f"synthetic-{index + 1:02d}"
        rows.append({"case_id": anonymous, "stratum": 1, "d": 0.0})
        rows.append({"case_id": anonymous, "stratum": 2, "d": -0.1 + index * 0.01})
        rows.append({"case_id": anonymous, "stratum": 3, "d": 0.2 - index * 0.005})
    write_csv(path, ["case_id", "stratum", "d"], rows)
    assert len(rows) == 3 * SMOKE_CASES
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
                # Excluded band-1 rows need source-line provenance; analyzed IDs
                # are emitted separately in the contract-required census table.
                excluded.append({"source_line": line_number, "reason": "non_primary_band"})
                continue
            selected.append((raw["case_id"], band, value, line_number))
    assert len(selected) + len(excluded) > 0
    expected = SMOKE_CASES if smoke else EXPECTED_CASES
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
    measurements = []
    for case_id in sorted(cases):
        band2 = lookup[(case_id, 2)]
        band3 = lookup[(case_id, 3)]
        delta = band3 - band2
        assert math.isfinite(delta)
        # Equal-patient estimator uses the validated census size (N=99 in the real run).
        contribution = delta / len(cases)
        assert math.isfinite(contribution)
        measurements.append({"case_id": case_id, "d_band2": band2, "d_band3": band3,
                             "delta": delta, "contribution": contribution})
    assert len(measurements) == len(cases)
    direct_gap = math.fsum(row["d_band3"] for row in measurements) / len(cases)
    direct_gap -= math.fsum(row["d_band2"] for row in measurements) / len(cases)
    residual = abs(math.fsum(row["contribution"] for row in measurements) - direct_gap)
    assert math.isfinite(residual)
    return measurements, direct_gap, residual


def summarize_census(measurements, direct_gap, residual):
    # SIGNED SUMMARY: descending contribution answers which observed cases
    # account numerically for the net estimator, with case_id as the frozen tie rule.
    signed = sorted(measurements, key=lambda row: (-row["contribution"], row["case_id"]))
    assert len({row["case_id"] for row in signed}) == len(signed)
    net = math.fsum(row["contribution"] for row in signed)
    if not math.isfinite(net) or net == 0.0:
        fail(EXIT_ALGEBRA, "signed contribution denominator is zero or nonfinite")
    signed_curve = []
    running = []
    for rank, row in enumerate(signed, start=1):
        running.append(row["contribution"])
        cumulative = math.fsum(running)
        signed_curve.append({"rank": rank, "case_id": row["case_id"],
                             "contribution": row["contribution"],
                             "signed_cumulative": cumulative,
                             "signed_fraction_of_net": cumulative / net})
    assert len(signed_curve) == len(signed)
    assert math.isclose(signed_curve[-1]["signed_cumulative"], net, rel_tol=0.0, abs_tol=TOLERANCE)

    # ABSOLUTE SUMMARY: ascending absolute contribution is the contract's
    # Lorenz ordering; explicit endpoints make the curve independently auditable.
    absolute = sorted(measurements, key=lambda row: (abs(row["contribution"]), row["case_id"]))
    total_absolute = math.fsum(abs(row["contribution"]) for row in absolute)
    if not math.isfinite(total_absolute) or total_absolute <= 0.0:
        fail(EXIT_ALGEBRA, "absolute contribution denominator is zero or nonfinite")
    lorenz = [{"rank": 0, "population_fraction": 0.0, "absolute_share": 0.0}]
    running_absolute = []
    for rank, row in enumerate(absolute, start=1):
        running_absolute.append(abs(row["contribution"]))
        lorenz.append({"rank": rank, "population_fraction": rank / len(absolute),
                       "absolute_share": math.fsum(running_absolute) / total_absolute})
    assert lorenz[0]["population_fraction"] == 0.0 and lorenz[0]["absolute_share"] == 0.0
    assert lorenz[-1]["population_fraction"] == 1.0 and lorenz[-1]["absolute_share"] == 1.0
    assert all(lorenz[i]["absolute_share"] <= lorenz[i + 1]["absolute_share"]
               for i in range(len(lorenz) - 1))

    # POSITIVE-MASS SUMMARY: zero and negative cases cannot help cross a
    # positive-share target, so the contract explicitly excludes them here.
    positive = [row for row in signed if row["contribution"] > 0.0]
    positive_mass = math.fsum(row["contribution"] for row in positive)
    if not math.isfinite(positive_mass) or positive_mass <= 0.0:
        fail(EXIT_ALGEBRA, "positive contribution denominator is zero or nonfinite")
    positive_curve = []
    running_positive = []
    for rank, row in enumerate(positive, start=1):
        running_positive.append(row["contribution"])
        positive_curve.append({"rank": rank, "case_id": row["case_id"],
                               "contribution": row["contribution"],
                               "positive_mass_share": math.fsum(running_positive) / positive_mass})
    assert positive_curve and positive_curve[-1]["positive_mass_share"] == 1.0

    top_k = {}
    descending_absolute = sorted(measurements,
                                 key=lambda row: (-abs(row["contribution"]), row["case_id"]))
    for k in TOP_K:
        if k > len(measurements):
            fail(EXIT_ALGEBRA, f"top-k summary undefined for k={k}")
        top_k[str(k)] = {
            "signed_head_net_gap_share": math.fsum(row["contribution"] for row in signed[:k]) / net,
            "absolute_mass_share": math.fsum(abs(row["contribution"])
                                               for row in descending_absolute[:k]) / total_absolute,
        }
    crossings = {}
    for target in TARGET_SHARES:
        crossing = next((row for row in positive_curve if row["positive_mass_share"] >= target), None)
        if crossing is None:
            fail(EXIT_ALGEBRA, f"positive-mass target is undefined: {target}")
        crossings[str(target)] = {"smallest_k": crossing["rank"],
                                  "achieved_share": crossing["positive_mass_share"]}

    signed_values = [row["contribution"] for row in measurements]
    absolute_values = [abs(value) for value in signed_values]
    sign_counts = {"positive": sum(value > 0.0 for value in signed_values),
                   "zero": sum(value == 0.0 for value in signed_values),
                   "negative": sum(value < 0.0 for value in signed_values)}
    tie_counts = {"signed": len(signed_values) - len(set(signed_values)),
                  "absolute": len(absolute_values) - len(set(absolute_values))}
    assert sum(sign_counts.values()) == len(measurements)
    summary = {"direct_band_gap": direct_gap, "net_contribution": net,
               "additive_identity_residual": residual,
               "additive_identity_within_1e-12": residual <= TOLERANCE,
               "sign_counts": sign_counts, "tie_counts": tie_counts,
               "top_k": top_k, "positive_mass_crossings": crossings,
               "denominators": {"signed_net": net, "positive_mass": positive_mass,
                                "absolute_mass": total_absolute}}
    return signed, signed_curve, lorenz, positive_curve, summary


def compare_v1_lineage_guards(measurements, census, smoke):
    """Compare real-run validity guards with the completed v1 audit."""
    if smoke:
        return {
            "status": "SKIPPED_SMOKE_SYNTHETIC_DATA",
            "compared": False,
            "tie_count_space": "delta_before_division_by_99",
        }

    # V1 counted exact ties on delta values before division. Repeating that
    # exact space avoids assuming that floating-point division is injective.
    deltas = [row["delta"] for row in measurements]
    absolute_deltas = [abs(value) for value in deltas]
    delta_ties = {
        "signed": len(deltas) - len(set(deltas)),
        "absolute": len(absolute_deltas) - len(set(absolute_deltas)),
    }
    observed = {
        "paired_cases": len(measurements),
        "additive_identity_residual": census["additive_identity_residual"],
        "denominators_defined": all(
            math.isfinite(value) and value != 0.0
            for value in census["denominators"].values()
        ),
        "orderings_deterministic": len({row["case_id"] for row in measurements}) == len(measurements),
        "sign_counts": census["sign_counts"],
        "tie_counts_delta_space": delta_ties,
    }
    expected = {
        "paired_cases": EXPECTED_CASES,
        "additive_identity_residual": V1_RESIDUAL,
        "denominators_defined": True,
        "orderings_deterministic": True,
        "sign_counts": V1_SIGN_COUNTS,
        "tie_counts_delta_space": V1_TIE_COUNTS_DELTA_SPACE,
    }
    if observed != expected:
        fail(EXIT_OUTPUT, f"v1 lineage guard disagreement: observed={observed} expected={expected}")
    return {
        "status": "MATCHED_V1_DEFINITION_AUDIT",
        "compared": True,
        "tie_count_space": "delta_before_division_by_99",
        "observed": observed,
        "expected": expected,
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
    expected_cases = SMOKE_CASES if args.smoke else EXPECTED_CASES
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

    # MEASURE: compute every case's frozen delta and equal-patient contribution.
    # This is the sole approved scientific transformation and uses no rounding.
    emit(f"[measure] Computing {len(cases)} paired case contributions.", log_lines)
    measurements, direct_gap, residual = measure(selected, cases)
    for index, _row in enumerate(measurements, start=1):
        emit(f"[measure] Pair {index}/{len(measurements)} complete; variant 1/1.", log_lines)
    if residual > TOLERANCE:
        fail(EXIT_ALGEBRA, "additive identity exceeds the approved 1e-12 tolerance")

    # SUMMARIZE: build exactly the signed, absolute, and positive-mass curves
    # frozen in v2. Smoke writes structurally identical outputs but is never a gate.
    emit("[summarize] Building frozen curves and fixed top-k/target summaries.", log_lines)
    signed, signed_curve, lorenz, positive_curve, census = summarize_census(
        measurements, direct_gap, residual)
    lineage_comparison = compare_v1_lineage_guards(measurements, census, args.smoke)
    census["v1_lineage_guard_comparison"] = lineage_comparison
    status = "SMOKE_ONLY" if args.smoke else "CENSUS_COMPLETE"
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
    per_case_rows = [{"case_id": row["case_id"], "d_band2": row["d_band2"],
                      "d_band3": row["d_band3"], "delta": row["delta"],
                      "contribution": row["contribution"], "signed_rank": rank}
                     for rank, row in enumerate(signed, start=1)]
    write_csv(args.output_dir / "per_case_contributions.csv",
              ["case_id", "d_band2", "d_band3", "delta", "contribution", "signed_rank"],
              per_case_rows)
    write_csv(args.output_dir / "signed_cumulative_curve.csv",
              ["rank", "case_id", "contribution", "signed_cumulative", "signed_fraction_of_net"],
              signed_curve)
    write_csv(args.output_dir / "absolute_lorenz_curve.csv",
              ["rank", "population_fraction", "absolute_share"], lorenz)
    write_csv(args.output_dir / "positive_mass_curve.csv",
              ["rank", "case_id", "contribution", "positive_mass_share"], positive_curve)
    write_json(args.output_dir / "census_summary.json", census)
    summary = {
        "idea_id": IDEA_ID, "status": status, "smoke": args.smoke,
        "paired_cases": len(cases), "excluded_rows": len(exclusions),
        "reserved_cases_accessed": split["reserved_cases_accessed"],
        "primary_metric_name": "complete_finite_population_contribution_accounting",
        "primary_metric_pass": census["additive_identity_within_1e-12"],
        "per_case_outputs": len(per_case_rows),
        "signed_curve_rows": len(signed_curve),
        "absolute_lorenz_rows": len(lorenz),
        "positive_mass_rows": len(positive_curve),
    }
    write_json(args.output_dir / "summary.json", summary)
    write_json(args.output_dir / "environment.txt", environment_record())

    manifest_end = start_manifest(input_path, args.smoke)
    if manifest_end != manifest_start:
        fail(EXIT_OUTPUT, "start and end determinism manifests differ")
    write_json(args.output_dir / "determinism_manifest_end.json", manifest_end)
    print(json.dumps(manifest_end, sort_keys=True), flush=True)
    emit(json.dumps(summary, indent=2, sort_keys=True), log_lines)
    if status == "CENSUS_COMPLETE":
        interpretation = ("Plain-language template: CENSUS_COMPLETE means the full frozen descriptive "
                          "accounting was emitted for these 99 observed cases. The numerical summaries "
                          "must be reported directly; they do not define stable carriers or population concentration.")
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
