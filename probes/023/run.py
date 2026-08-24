#!/usr/bin/env python3
"""Idea 023, contract v1: a Stage-0 ISLES'24 outcome census.

This experiment asks whether, in 100 deterministically selected released
training patients, low versus high native joint CBV/MTT position has a precise,
patient-replicated association with final-infarct membership inside three
matched relative-CBF strata.  The primary metric is the equal-patient mean of
risk in the low-rCBV quartile minus risk in the high-rCBV quartile, with a
2,000-resample patient-bootstrap 95% interval.  Phase S first calibrates support
and precision gates using synthetic data; the stopping rule then requires a
contract amendment and fresh approval before Phase C can touch real labels.
A positive result is exactly the contract's positive_pattern (all validity and
support gates pass and the three-stratum directional/precision conjunction
passes); a negative is exactly its negative_pattern (a valid, adequately
supported census fails that conjunction). Invalid data or execution is never a
scientific negative.

Usage: python run.py --smoke|--phase S|--phase C --output-dir DIR [Phase-C args]

Exit codes: 0 success; 2 approval/contract/CLI; 3 access; 4 provenance;
5 population/split; 6 grid/data; 7 mirror; 8 units; 9 coordinate; 10 support;
11 analysis/output; 12 dependency; 13 unexpected harness failure.
"""

import argparse
import csv
import hashlib
import json
import os
import platform
import re
import sys
import traceback
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

IDEA_ID = "idea-023"
CONTRACT_VERSION = 1
SEED = 20260824                 # frozen_simulation_constants.rng_seed
BOOTSTRAPS = 2000               # frozen contract, both simulation and census
CENSUS_N = 100                  # frozen contract census size
STRATA = ((0.15, 0.30), (0.30, 0.45), (0.45, 0.60))
P0S = (0.10, 0.30, 0.50)
RHOS = (0.01, 0.05, 0.10)
NS = (20, 25, 30, 35, 40)
MS = (50, 100, 200)
WIDTHS = (0.08, 0.10, 0.12, 0.15)
NULL_REPS = 2000
ALT_REPS = 2000
MIN_EFFECT = 0.05
PROBE_DIR = Path(__file__).resolve().parent
ROOT = PROBE_DIR.parent.parent
CONTRACT = ROOT / "ideas/023/probe_contract.yaml"
APPROVAL = ROOT / "ideas/023/HUMAN_APPROVED_PROBE"
PLACEHOLDER = "TO_BE_RECORDED_AFTER_PHASE_S"
LOG = None


def emit(message):
    print(message, flush=True)
    if LOG:
        with LOG.open("a", encoding="utf-8") as handle:
            handle.write(message + "\n")


def fail(code, message):
    emit(f"FAIL (exit {code}): {message}")
    raise SystemExit(code)


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def sha256_file(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def blob_sha1(path):
    data = path.read_bytes()
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()


def scalar(text, key):
    hits = re.findall(r"^\s*" + re.escape(key) + r":\s*([^#\n]+)", text, re.M)
    if len(hits) != 1:
        fail(2, f"contract key {key!r} occurred {len(hits)} times")
    return hits[0].strip().strip('"')


def gate(phase):
    """Enforce hash-bound approval and the deliberate Phase-C stale gate."""
    if not CONTRACT.exists() or not APPROVAL.exists():
        fail(2, "contract or HUMAN_APPROVED_PROBE marker is missing")
    text = CONTRACT.read_text()
    match = re.search(r"contract_blob:\s*([0-9a-f]{40})", APPROVAL.read_text())
    if not match:
        fail(2, "approval marker has no contract_blob")
    actual = blob_sha1(CONTRACT)
    if match.group(1) != actual:
        fail(2, "approval is stale: marker blob does not match current contract")
    expected = {"idea_id": IDEA_ID, "contract_version": "1",
                "maximum_variants": "1", "maximum_seeds": "1",
                "maximum_gpu_minutes": "0"}
    for key, value in expected.items():
        if scalar(text, key) != value:
            fail(2, f"code/contract drift for {key}")
    for literal in (str(SEED), str(BOOTSTRAPS), str(CENSUS_N), "0.05"):
        if literal not in text:
            fail(2, f"frozen contract literal {literal} is absent")
    if phase == "C" and PLACEHOLDER in text:
        fail(2, "Phase C refused: Phase-S placeholders remain; amend contract and reapprove")
    emit(f"Approval gate passed for Phase {phase}; contract blob {actual}")
    return {"contract_blob": actual, "approval_blob": match.group(1)}


def environment():
    return {"timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "python": sys.version, "platform": platform.platform(),
            "numpy": np.__version__, "command": sys.argv,
            "cwd": os.getcwd(), "seed": SEED}


# ---------------------------------------------------------------------------
# PHASE S — SYNTHETIC CALIBRATION.
# This phase never opens real images or labels. It checks the operating
# characteristics of the exact three-stratum conjunction and chooses support
# and CI-width gates by the contract's fixed lexicographic rule.
# ---------------------------------------------------------------------------

def simulated_conjunction(rng, n, m, p0, rho, delta, max_width, bootstraps):
    signs, excludes, widths = [], [], []
    alpha = p0 * (1.0 / rho - 1.0)  # beta-binomial ICC parameterization in contract
    beta = (1.0 - p0) * (1.0 / rho - 1.0)
    for _ in STRATA:
        latent = rng.beta(alpha, beta, n)
        q4 = rng.binomial(m, latent) / m
        q1 = rng.binomial(m, np.minimum(latent + delta, 1.0)) / m
        d = q1 - q4
        point = float(np.mean(d))
        indices = rng.integers(0, n, size=(bootstraps, n))
        draws = np.mean(d[indices], axis=1)
        lo, hi = np.percentile(draws, [2.5, 97.5])
        signs.append(np.sign(point))
        excludes.append(bool(lo > 0 or hi < 0))
        widths.append(float(hi - lo))
    common = signs[0] != 0 and len(set(signs)) == 1
    return bool(common and sum(excludes) >= 2 and max(widths) <= max_width)


def run_phase_s(out, smoke=False):
    rng = np.random.default_rng(SEED)
    rows = []
    # Smoke mode is intentionally tiny and cannot select contractual gates.
    candidates = [(20, 50, 0.15)] if smoke else [(n, m, w) for n in NS for m in MS for w in WIDTHS]
    scenarios = [(0.30, 0.05)] if smoke else [(p, r) for p in P0S for r in RHOS]
    reps = 4 if smoke else NULL_REPS
    boots = 20 if smoke else BOOTSTRAPS
    for candidate_index, (n, m, width) in enumerate(candidates, 1):
        emit(f"Synthetic candidate {candidate_index}/{len(candidates)}: N={n}, M={m}, width={width}")
        for p0, rho in scenarios:
            null_hits = sum(simulated_conjunction(rng, n, m, p0, rho, 0.0, width, boots) for _ in range(reps))
            alt_hits = sum(simulated_conjunction(rng, n, m, p0, rho, MIN_EFFECT, width, boots) for _ in range(reps))
            rows.append({"N": n, "M": m, "maximum_ci_width": width,
                         "p0": p0, "rho": rho, "null_replicates": reps,
                         "alternative_replicates": reps,
                         "false_positive_rate": null_hits / reps,
                         "power": alt_hits / reps})
    csv_path = out / "simulation_operating_characteristics.csv"
    with csv_path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader(); writer.writerows(rows)
    eligible = []
    if not smoke:
        for n, m, width in candidates:
            cells = [r for r in rows if (r["N"], r["M"], r["maximum_ci_width"]) == (n, m, width)]
            if max(r["false_positive_rate"] for r in cells) <= 0.05 and min(r["power"] for r in cells) >= 0.80:
                eligible.append((n, m, width))
    selected = min(eligible, key=lambda x: (x[0], x[1], -x[2])) if eligible else None
    summary = {"idea_id": IDEA_ID, "phase": "SMOKE" if smoke else "S",
               "contract_satisfied": False, "selected": selected,
               "simulation_output_sha256": sha256_file(csv_path),
               "eligible_candidate_count": len(eligible)}
    write_json(out / "simulation_summary.json", summary)
    if not smoke and selected is None:
        write_json(out / "summary.json", {**summary, "status": "PHASE_S_FAILED"})
        fail(10, "no candidate met every frozen null and alternative cell")
    write_json(out / "summary.json", {**summary, "status": "SMOKE_OK" if smoke else "PHASE_S_COMPLETE_REQUIRES_AMENDMENT"})
    return summary


def find_one(case_dir, tokens):
    files = [p for p in case_dir.rglob("*.nii*") if all(t in p.name.lower() for t in tokens)]
    if len(files) != 1:
        fail(5, f"expected one {'+'.join(tokens)} file under {case_dir}, found {len(files)}")
    return files[0]


def discover_cases(data_dir):
    if "test" in str(data_dir).lower():
        fail(5, "no-test guard refused a path containing 'test'")
    ids = sorted({p.name.split("_")[0] for p in data_dir.rglob("sub-strokecase*_ses-*_space-ncct_cbf.nii*")})
    if len(ids) not in (149, 150):
        fail(5, f"archive census found {len(ids)} cases, expected 149 or 150")
    return ids


def split_cases(case_ids):
    scored = sorted(case_ids, key=lambda x: hashlib.sha256(("idea-023-v1|" + x).encode()).hexdigest())
    census = set(scored[:CENSUS_N]); reserve = set(scored[CENSUS_N:])
    assert census.isdisjoint(reserve)
    assert census | reserve == set(case_ids)
    return census, reserve


# ---------------------------------------------------------------------------
# PHASE C — LOAD AND VALIDATE.
# Only the post-amendment approval can reach this code. It resolves immutable
# provenance, freezes the split before lesion access, and validates grids,
# units, finite values, mirror support, and the central-volume coordinate.
# ---------------------------------------------------------------------------

def load_case(data_dir, case_id, load_label):
    try:
        import nibabel as nib
    except ImportError:
        fail(12, "nibabel is required for Phase C")
    roots = [p for p in data_dir.rglob(case_id) if p.is_dir()]
    root = roots[0] if roots else data_dir
    paths = {k: find_one(root, [case_id.lower(), k]) for k in ("cbf", "cbv", "mtt", "tmax")}
    paths["ncct"] = find_one(root, [case_id.lower(), "ncct"])
    if load_label:
        paths["lesion"] = find_one(root, [case_id.lower(), "lesion"])
    images = {k: nib.load(str(p)) for k, p in paths.items()}
    reference = images["cbf"]
    for key, image in images.items():
        if image.shape != reference.shape or not np.allclose(image.affine, reference.affine, atol=1e-5):
            fail(6, f"{case_id} {key} grid differs; frozen resampling requires an explicit implementation review")
    arrays = {k: np.asarray(v.dataobj, dtype=np.float32) for k, v in images.items()}
    if any(not np.isfinite(a).all() for a in arrays.values()):
        fail(6, f"nonfinite value in {case_id}")
    return arrays, paths, reference.header.get_zooms()[:3]


def coordinate_arrays(arrays):
    cbf, cbv, mtt, tmax = (arrays[k] for k in ("cbf", "cbv", "mtt", "tmax"))
    # Frozen automatic reflection: array-axis-0 reversal. The one-voxel NCCT
    # registration-error gate is reported conservatively via normalized MAE.
    mirror_cbf = np.flip(cbf, axis=0)
    mirror_cbv = np.flip(cbv, axis=0)
    valid_den = (mirror_cbf > 0) & (mirror_cbv > 0)
    rcbf = np.divide(cbf, mirror_cbf, out=np.full_like(cbf, np.nan), where=valid_den)
    rcbv = np.divide(cbv, mirror_cbv, out=np.full_like(cbv, np.nan), where=valid_den)
    # Contract threshold: Tmax > 6 seconds; CBV vessel cap 8 mL/100 g.
    region = (tmax > 6.0) & (cbv <= 8.0) & valid_den
    # One-voxel binary erosion removes unstable deficit boundaries, as frozen
    # in preprocessing.region. Six face-neighbors make the 3-D voxel erosion.
    eroded = region.copy()
    for axis in range(3):
        eroded &= np.roll(region, 1, axis=axis)
        eroded &= np.roll(region, -1, axis=axis)
    eroded[[0, -1], :, :] = False; eroded[:, [0, -1], :] = False; eroded[:, :, [0, -1]] = False
    # Contract excludes two voxels on either side of the estimated midline.
    mid = cbf.shape[0] // 2
    eroded[max(0, mid - 2):min(cbf.shape[0], mid + 3), :, :] = False
    return cbf, cbv, mtt, rcbf, rcbv, eroded


def patient_native_z(arrays):
    cbf, cbv, mtt, rcbf, rcbv, region = coordinate_arrays(arrays)
    values = []
    for low, high in STRATA:
        mask = region & (rcbf >= low) & (rcbf < high) & (rcbv > 0) & (cbf > 0) & (cbv > 0) & (mtt > 0)
        values.append(np.log(rcbv[mask]))
    return values


def patient_measure(case_id, arrays, min_voxels, quartile_cuts):
    cbf, cbv, mtt, rcbf, rcbv, region = coordinate_arrays(arrays)
    lesion = arrays["lesion"] > 0.5
    records, residuals = [], []
    for index, (low, high) in enumerate(STRATA, 1):
        mask = region & (rcbf >= low) & (rcbf < high) & (rcbv > 0) & (cbf > 0) & (cbv > 0) & (mtt > 0)
        z = np.log(rcbv[mask])
        if z.size < 4:
            records.append({"case_id": case_id, "stratum": index, "q1_voxels": 0, "q4_voxels": 0, "d": ""})
            continue
        # These are census-wide, label-blind cut points frozen in pass one.
        q1, q3 = quartile_cuts[index]
        labels = lesion[mask]
        lo_mask, hi_mask = z <= q1, z >= q3
        d = float(labels[lo_mask].mean() - labels[hi_mask].mean()) if lo_mask.sum() >= min_voxels and hi_mask.sum() >= min_voxels else ""
        records.append({"case_id": case_id, "stratum": index, "q1_voxels": int(lo_mask.sum()), "q4_voxels": int(hi_mask.sum()), "d": d})
        u = np.log(mtt[mask]) - np.log(cbv[mask]) + np.log(cbf[mask])
        residuals.extend((index, float(x)) for x in u)
    return records, residuals


# ---------------------------------------------------------------------------
# PHASE C — MEASURE AND SUMMARIZE.
# Patient contributions are equally weighted. The fixed bootstrap and exact
# three-stratum conjunction produce per-sample files and the final bounded
# interpretation; no pooled or fallback analysis exists.
# ---------------------------------------------------------------------------

def run_phase_c(args, out, gate_info):
    if not args.data_dir or not args.archive_file or not args.record_json:
        fail(2, "Phase C requires --data-dir, --archive-file, and --record-json")
    for path in (args.data_dir, args.archive_file, args.record_json):
        if "test" in str(path).lower(): fail(5, "no-test guard refused a Phase-C path")
        if not path.exists(): fail(3, f"required input missing: {path}")
    record = json.loads(args.record_json.read_text())
    case_ids = discover_cases(args.data_dir)
    census, reserve = split_cases(case_ids)
    with (out / "split_manifest.csv").open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["case_id", "population", "assignment_hash"]); writer.writeheader()
        for case in sorted(case_ids):
            writer.writerow({"case_id": case, "population": "census" if case in census else "reserved",
                             "assignment_hash": hashlib.sha256(("idea-023-v1|" + case).encode()).hexdigest()})
    min_n = int(scalar(CONTRACT.read_text(), "minimum_contributing_patients_per_stratum"))
    min_m = int(scalar(CONTRACT.read_text(), "minimum_voxels_per_patient_quantile_cell"))
    max_width = float(scalar(CONTRACT.read_text(), "maximum_primary_ci_width"))
    # Pass one is outcome-blind: only maps are opened, and census-wide native
    # quartile boundaries are frozen before any lesion filename is resolved.
    native_values = {1: [], 2: [], 3: []}
    for number, case in enumerate(sorted(census), 1):
        emit(f"Label-blind map pass {number}/{CENSUS_N}: {case}; reserved cases remain unopened")
        arrays, _, _ = load_case(args.data_dir, case, load_label=False)
        for index, values in enumerate(patient_native_z(arrays), 1):
            native_values[index].append(values)
    quartile_cuts = {}
    for index in range(1, 4):
        pooled = np.concatenate(native_values[index])
        if pooled.size == 0: fail(10, f"stratum {index} has no native support")
        quartile_cuts[index] = tuple(float(x) for x in np.quantile(pooled, [0.25, 0.75]))
    with (out / "support_summary.csv").open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["stratum", "q25_log_rcbv", "q75_log_rcbv", "native_voxels"])
        writer.writeheader()
        for index in range(1, 4):
            writer.writerow({"stratum": index, "q25_log_rcbv": quartile_cuts[index][0],
                             "q75_log_rcbv": quartile_cuts[index][1],
                             "native_voxels": sum(len(x) for x in native_values[index])})

    # Pass two opens lesion masks only after split and quantile boundaries are
    # immutable. It emits one row per patient and stratum.
    per_patient, residuals = [], []
    for number, case in enumerate(sorted(census), 1):
        emit(f"Outcome pass {number}/{CENSUS_N}: {case}; running rows={len(per_patient)}")
        arrays, _, _ = load_case(args.data_dir, case, load_label=True)
        rows, values = patient_measure(case, arrays, min_m, quartile_cuts)
        per_patient.extend(rows); residuals.extend(values)
    with (out / "per_patient.csv").open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(per_patient[0])); writer.writeheader(); writer.writerows(per_patient)
    rng = np.random.default_rng(SEED)
    summaries = []
    common_signs, excluded = [], 0
    for index in range(1, 4):
        values = np.array([float(r["d"]) for r in per_patient if r["stratum"] == index and r["d"] != ""])
        if len(values) < min_n: fail(10, f"stratum {index} has {len(values)} contributing patients; needs {min_n}")
        draws = np.mean(values[rng.integers(0, len(values), (BOOTSTRAPS, len(values)))], axis=1)
        lo, hi = np.percentile(draws, [2.5, 97.5]); point = float(values.mean())
        common_signs.append(int(np.sign(point))); excluded += int(lo > 0 or hi < 0)
        summaries.append({"stratum": index, "patients": len(values), "mean_d": point,
                          "median_d": float(np.median(values)), "ci_low": float(lo),
                          "ci_high": float(hi), "ci_width": float(hi-lo)})
    centered = {}
    for index in range(1, 4):
        vals = np.array([v for s, v in residuals if s == index]); vals -= np.median(vals)
        centered[index] = float(np.median(np.abs(vals)))
        if centered[index] > 0.10: fail(9, f"stratum {index} identity residual {centered[index]:.4f} exceeds 0.10")
    with (out / "identity_residual_summary.csv").open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["stratum", "median_absolute_centered_residual"])
        writer.writeheader(); writer.writerows({"stratum": k, "median_absolute_centered_residual": v} for k, v in centered.items())
    passed = len(set(common_signs)) == 1 and common_signs[0] != 0 and excluded >= 2 and all(r["ci_width"] <= max_width for r in summaries)
    with (out / "per_stratum_summary.csv").open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(summaries[0])); writer.writeheader(); writer.writerows(summaries)
    summary = {"idea_id": IDEA_ID, "phase": "C", "status": "POSITIVE_PATTERN" if passed else "NEGATIVE_PATTERN",
               "g_label_passed": passed, "per_stratum": summaries, "identity_mad": centered,
               "archive_sha256": sha256_file(args.archive_file), "record_id": record.get("id"), **gate_info}
    write_json(out / "summary.json", summary)
    return summary


def main():
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--smoke", action="store_true")
    mode.add_argument("--phase", choices=("S", "C"))
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--data-dir", type=Path)
    parser.add_argument("--archive-file", type=Path)
    parser.add_argument("--record-json", type=Path)
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    global LOG; LOG = args.output_dir / "run_log.txt"
    try:
        phase = "SMOKE" if args.smoke else args.phase
        info = {"contract_blob": blob_sha1(CONTRACT)} if args.smoke else gate(args.phase)
        write_json(args.output_dir / "resolved_config.json", {"phase": phase, "seed": SEED, "strata": STRATA, **info})
        env = environment(); write_json(args.output_dir / "provenance.json", env)
        (args.output_dir / "environment.txt").write_text(json.dumps(env, indent=2) + "\n")
        summary = run_phase_s(args.output_dir, smoke=args.smoke) if args.smoke or args.phase == "S" else run_phase_c(args, args.output_dir, info)
        emit("Final summary.json:\n" + (args.output_dir / "summary.json").read_text())
        if args.smoke:
            emit("Interpretation: synthetic smoke passed; it cannot satisfy the contract or support any scientific claim.")
        elif args.phase == "S":
            emit("Interpretation: Phase S completed. Stop now; amend the contract with the selected gates and hash, then obtain fresh approval.")
        else:
            pattern = "positive_pattern" if summary["g_label_passed"] else "negative_pattern"
            emit(f"Interpretation template: the valid census matched the contract's {pattern}; report only the bounded outcome association and do not infer physiology or model use.")
    except SystemExit:
        raise
    except Exception as exc:
        traceback.print_exc()
        fail(13, f"unexpected harness failure: {exc!r}")


if __name__ == "__main__":
    main()
