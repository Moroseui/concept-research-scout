#!/usr/bin/env python3
"""Idea 023, contract v1: a Stage-0 ISLES'24 outcome census.

This experiment asks whether, in 100 deterministically selected released
training patients, low versus high native joint CBV/MTT position has a precise,
patient-replicated association with final-infarct membership inside three
within-patient CBF-percentile bands. The primary metric is the equal-patient
mean of risk in the low-CBV quartile minus risk in the high-CBV quartile, with a
2,000-resample patient-bootstrap 95% interval.  Phase S first calibrates support
and precision gates using synthetic data; the stopping rule then requires a
contract amendment and fresh approval before Phase C can touch real labels.
A positive result is exactly the contract's positive_pattern (all validity and
support gates pass and the three-stratum directional/precision conjunction
passes); a negative is exactly its negative_pattern (a valid, adequately
supported census fails that conjunction). Invalid data or execution is never a
scientific negative. A label-blind secondary audit reports NCCT HU median and
IQR for the low- and high-CBV groups in each flow band; it changes no estimator
or gate and exists only to reveal tissue-composition imbalance.

Usage: python run.py --smoke|--phase S|--phase C --output-dir DIR [Phase-C args]

Exit codes: 0 success; 2 approval/contract/CLI; 3 access; 4 provenance;
5 population/split; 6 grid/data; 7 retired mirror gate; 8 retired unit contingency;
9 coordinate; 10 support;
11 analysis/output; 12 dependency; 13 unexpected harness failure.
"""

import argparse
import csv
import gzip
import hashlib
import importlib.metadata
import json
import os
import platform
import re
import sys
import traceback
import zlib
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

IDEA_ID = "idea-023"
CONTRACT_VERSION = 1
SEED = 20260824                 # frozen_simulation_constants.rng_seed
BOOTSTRAPS = 2000               # frozen contract, both simulation and census
CENSUS_N = 100                  # frozen contract census size
CBF_PERCENTILE_BANDS = ((0, 33), (33, 67), (67, 100))
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
# Verified twice from the checksum-pinned archive before outcomes were seen.
SOURCE_CORRUPT_MEMBERS = (
    "derivatives/sub-stroke0043/ses-01/perfusion-maps/"
    "sub-stroke0043_ses-01_space-ncct_cbf.nii.gz",
)
LOG = None


class SourceCorruptMember(Exception):
    """A required .nii.gz is present but unreadable in the verified release."""

    def __init__(self, path, detail):
        super().__init__(detail)
        self.path = Path(path)
        self.detail = detail


def emit(message):
    print(message, flush=True)
    if LOG:
        with LOG.open("a", encoding="utf-8") as handle:
            handle.write(message + "\n")


def fail(code, message):
    emit(f"FAIL (exit {code}): {message}")
    raise SystemExit(code)


def write_json(path, value):
    # Contract outputs must never silently serialize NaN/Infinity tokens.
    path.write_text(json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n")


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
    packages = {}
    for name in ("numpy", "nibabel", "scipy", "py7zr"):
        try:
            packages[name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            packages[name] = "NOT_INSTALLED"
    return {"timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "python": sys.version, "platform": platform.platform(),
            "packages": packages, "command": sys.argv,
            "cwd": os.getcwd(), "seed": SEED}


def write_determinism_manifest(out, stage, manifest):
    """Print and persist the same declared-input manifest at start and end."""
    path = out / f"determinism_manifest_{stage}.json"
    write_json(path, manifest)
    emit(f"Determinism manifest ({stage}):\n" + path.read_text())


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
    for _ in CBF_PERCENTILE_BANDS:
        latent = rng.beta(alpha, beta, n)
        q4 = rng.binomial(m, latent) / m
        q1 = rng.binomial(m, np.minimum(latent + delta, 1.0)) / m
        d = q1 - q4
        point = float(np.mean(d))
        indices = rng.integers(0, n, size=(bootstraps, n))
        draws = np.mean(d[indices], axis=1)
        lo, hi = np.percentile(draws, [2.5, 97.5])
        signs.append(np.sign(point))
        # Phase S uses the same direction-aware exclusion rule as Phase C.
        excludes.append(bool((point > 0 and lo > 0) or (point < 0 and hi < 0)))
        widths.append(float(hi - lo))
    common = signs[0] != 0 and len(set(signs)) == 1
    return bool(common and sum(excludes) >= 2 and max(widths) <= max_width)


def run_phase_s(out, smoke=False):
    manifest = {
        "idea_id": IDEA_ID,
        "phase": "SMOKE" if smoke else "S",
        "seed": SEED,
        "input_paths": {
            "contract": {"path": str(CONTRACT), "sha256": sha256_file(CONTRACT)},
            "run_py": {"path": str(Path(__file__)), "sha256": sha256_file(Path(__file__))},
        },
        "input_row_count": 0,
        "input_case_count": 0,
    }
    write_determinism_manifest(out, "start", manifest)
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
    write_determinism_manifest(out, "end", manifest)
    assert json.loads((out / "determinism_manifest_start.json").read_text()) == manifest
    assert json.loads((out / "determinism_manifest_end.json").read_text()) == manifest
    return summary


def find_one(data_dir, case_id, kind):
    """Resolve one modality by an exact filename suffix, never a substring."""
    suffixes = {
        "cbf": ("_space-ncct_cbf.nii.gz", "_space-ncct_cbf.nii"),
        "cbv": ("_space-ncct_cbv.nii.gz", "_space-ncct_cbv.nii"),
        "mtt": ("_space-ncct_mtt.nii.gz", "_space-ncct_mtt.nii"),
        "tmax": ("_space-ncct_tmax.nii.gz", "_space-ncct_tmax.nii"),
        "ncct": ("_ncct.nii.gz", "_ncct.nii"),
        # Official release spelling is *_lesion-msk.nii.gz (hyphen before msk).
        "lesion": ("_lesion-msk.nii.gz", "_lesion-msk.nii"),
    }
    files = [p for p in data_dir.rglob(f"{case_id}*")
             if p.is_file() and any(p.name.lower().endswith(s) for s in suffixes[kind])]
    if len(files) != 1:
        fail(5, f"expected one exact {kind} file for {case_id}, found {len(files)}: "
                + ", ".join(str(p) for p in sorted(files)[:5]))
    return files[0]


def archive_case_inventory(members):
    """Derive case ids and the one usable lesion member from the payload."""
    # The deposited payload uses sub-strokeNNNN; older release prose used
    # sub-strokecaseNNNN. Both are accepted, but no other subject prefix is.
    case_pattern = re.compile(r"(?:^|/)(sub-(?:stroke|strokecase)\d+)(?:/|_)", re.I)
    cbf_suffixes = ("_space-ncct_cbf.nii.gz", "_space-ncct_cbf.nii")
    lesion_suffixes = ("_lesion-msk.nii.gz", "_lesion-msk.nii")
    cbf_by_case = {}
    lesions_by_case = {}
    for member in members:
        path = str(member["path"]).replace("\\", "/")
        match = case_pattern.search(path)
        if not match:
            continue
        case_id = match.group(1).lower()
        if path.lower().endswith(cbf_suffixes):
            cbf_by_case.setdefault(case_id, []).append(member)
        if path.lower().endswith(lesion_suffixes):
            lesions_by_case.setdefault(case_id, []).append(member)

    ids = sorted(cbf_by_case)
    if len(ids) not in (149, 150):
        fail(5, f"archive member census found {len(ids)} CBF cases, expected 149 or 150")
    for case_id in ids:
        if len(cbf_by_case[case_id]) != 1:
            fail(5, f"archive contains {len(cbf_by_case[case_id])} CBF members for {case_id}")
        if not lesions_by_case.get(case_id):
            fail(5, f"archive contains no lesion member for {case_id}")

    selected = {}
    excluded = []
    for case_id in ids:
        candidates = sorted(lesions_by_case[case_id], key=lambda row: row["path"])
        # The outcome is the follow-up (session 2) derivative. Prefer the one
        # whose directory and filename both encode that contract-defined role.
        session_two = re.compile(rf"/derivatives/{re.escape(case_id)}/ses-0*2/"
                                 rf"{re.escape(case_id)}_ses-0*2_space-ncct_lesion-msk\.nii(?:\.gz)?$", re.I)
        canonical = [row for row in candidates
                     if session_two.search(str(row["path"]).replace("\\", "/"))]
        if len(canonical) == 1:
            retained = canonical[0]
        elif len(candidates) == 1:
            retained = candidates[0]
        else:
            # If schema position cannot distinguish duplicates, only identical
            # archive signatures permit a deterministic lexicographic choice.
            signatures = {(row["size"], row["crc"]) for row in candidates}
            if len(signatures) != 1:
                fail(5, f"ambiguous non-identical lesion members for {case_id}: "
                        + ", ".join(row["path"] for row in candidates))
            retained = candidates[0]
        selected[case_id] = retained
        for row in candidates:
            if row is retained:
                continue
            excluded.append({"case_id": case_id, "path": row["path"],
                             "retained_path": retained["path"],
                             "reason": "duplicate/noncanonical lesion archive member; follow-up derivative retained"})

    orphan_lesions = sorted(set(lesions_by_case) - set(ids))
    if orphan_lesions:
        fail(5, "lesion members exist without a CBF case: " + ", ".join(orphan_lesions))
    return ids, selected, excluded


def find_archive_selected(data_dir, archive_path):
    """Resolve one selectively extracted file by its exact archive path."""
    normalized = archive_path.replace("\\", "/").lstrip("/")
    # Selective extraction may preserve the archive's leading `train/`
    # directory or place its contents directly below --data-dir.
    without_root = normalized.split("/", 1)[1] if "/" in normalized else normalized
    suffixes = ("/" + normalized, "/" + without_root)
    matches = [path for path in data_dir.rglob(Path(normalized).name)
               if path.is_file() and path.resolve().as_posix().endswith(suffixes)]
    if len(matches) != 1:
        fail(5, f"expected one extracted copy of archive member {archive_path}, found {len(matches)}")
    return matches[0]


def verify_required_gzip(path):
    """Read a required gzip stream fully so a source defect is auditable."""
    if not path.name.lower().endswith(".gz"):
        return
    try:
        with gzip.open(path, "rb") as handle:
            for block in iter(lambda: handle.read(1024 * 1024), b""):
                pass
    except (EOFError, gzip.BadGzipFile, OSError, zlib.error) as exc:
        normalized = path.resolve().as_posix().lower()
        if not any(normalized.endswith(member.lower()) for member in SOURCE_CORRUPT_MEMBERS):
            fail(6, f"unreadable required gzip is not the preregistered source defect: {path}: {exc}")
        raise SourceCorruptMember(path, f"{type(exc).__name__}: {exc}") from exc


def split_cases(case_ids):
    scored = sorted(case_ids, key=lambda x: hashlib.sha256(("idea-023-v1|" + x).encode()).hexdigest())
    census = set(scored[:CENSUS_N]); reserve = set(scored[CENSUS_N:])
    assert census.isdisjoint(reserve)
    assert census | reserve == set(case_ids)
    return census, reserve


def write_csv(path, fieldnames, rows):
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def md5_file(path):
    digest = hashlib.md5()  # Zenodo supplies MD5 for deposited files.
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def validate_record_and_archive(record, archive_file):
    """Verify the immutable Zenodo record and archive before image access."""
    record_id = str(record.get("id", ""))
    metadata = record.get("metadata", {})
    publication_date = metadata.get("publication_date")
    concept_id = str(record.get("conceptrecid", ""))
    if not record_id.isdigit() or not publication_date:
        fail(4, "record JSON lacks an immutable numeric id or publication date")
    if concept_id and concept_id == record_id:
        fail(4, "record JSON identifies the mutable concept record, not an immutable child record")
    candidates = [f for f in record.get("files", []) if f.get("key") == archive_file.name]
    if len(candidates) != 1:
        fail(4, f"record JSON does not name exactly one {archive_file.name}")
    supplied = str(candidates[0].get("checksum", ""))
    if not supplied.startswith("md5:"):
        fail(4, "Zenodo file entry lacks its supplied md5 checksum")
    actual_md5 = md5_file(archive_file)
    if actual_md5 != supplied.split(":", 1)[1].lower():
        fail(4, "downloaded archive does not match the Zenodo-supplied checksum")
    return {"record_id": record_id, "publication_date": publication_date,
            "zenodo_checksum": supplied, "archive_md5": actual_md5,
            "archive_sha256": sha256_file(archive_file)}


def archive_members(archive_file):
    """Read the deposited 7z member list without extracting scientific data."""
    try:
        import py7zr
    except ImportError:
        fail(12, "py7zr is required to create archive_manifest.csv")
    try:
        with py7zr.SevenZipFile(archive_file, mode="r") as archive:
            rows = [{"path": item.filename, "size": item.uncompressed,
                     "crc": "" if item.crc32 is None else f"{item.crc32:08x}"}
                    for item in archive.list() if not item.is_directory]
    except Exception as exc:
        fail(4, f"could not list the 7z archive: {exc!r}")
    if not rows:
        fail(4, "archive member manifest is empty")
    return rows


def verify_phase_s_hash(args):
    if not args.phase_s_dir:
        fail(2, "Phase C requires --phase-s-dir to verify the amended simulation hash")
    csv_path = args.phase_s_dir / "simulation_operating_characteristics.csv"
    if not csv_path.exists():
        fail(4, f"Phase-S output is missing: {csv_path}")
    expected = scalar(CONTRACT.read_text(), "simulation_output_sha256")
    actual = sha256_file(csv_path)
    if expected != actual:
        fail(4, "Phase-S simulation output SHA-256 does not match the amended contract")
    return actual


# ---------------------------------------------------------------------------
# PHASE C — LOAD AND VALIDATE.
# Only the post-amendment approval can reach this code. It resolves immutable
# provenance, freezes the split before lesion access, and validates grids,
# finite values, within-patient flow bands, and the central-volume coordinate. CBV units
# are recorded as undocumented; the amended vessel rule is unit-free.
# ---------------------------------------------------------------------------

def load_case(data_dir, case_id, load_label, audit_rows=None):
    try:
        import nibabel as nib
    except ImportError:
        fail(12, "nibabel is required for Phase C")
    # The activated tissue-composition audit reads NCCT without labels. It is
    # diagnostic only: its values never enter the estimator or a gate.
    paths = {k: find_one(data_dir, case_id, k) for k in ("cbf", "cbv", "mtt", "tmax", "ncct")}
    if load_label:
        paths["lesion"] = find_one(data_dir, case_id, "lesion")
    # A full stream read distinguishes the deposited unreadable member from a
    # later nibabel failure and gives the exclusion log its exact source path.
    for path in paths.values():
        verify_required_gzip(path)
    images = {k: nib.load(str(p)) for k, p in paths.items()}
    # CBF supplies the common NCCT-space reference grid; no reference anatomy is used.
    reference = nib.as_closest_canonical(images["cbf"])
    images["cbf"] = reference
    resampled = []
    for key, image in list(images.items()):
        if image.shape != reference.shape or not np.allclose(image.affine, reference.affine, atol=1e-5):
            try:
                from nibabel.processing import resample_from_to
            except ImportError:
                fail(12, "scipy is required for the frozen resampling rule")
            # Contract rule: linear interpolation for maps; nearest-neighbor for labels.
            order = 0 if key == "lesion" else 1
            images[key] = resample_from_to(image, (reference.shape, reference.affine), order=order)
            resampled.append(key)
    arrays = {k: np.asarray(v.dataobj, dtype=np.float32) for k, v in images.items()}
    if audit_rows is not None:
        audit_rows.append({"case_id": case_id, "files": json.dumps({k: str(v) for k, v in paths.items()}, sort_keys=True),
                           "shape": "x".join(map(str, reference.shape)),
                           "voxel_sizes_mm": "x".join(f"{v:.6g}" for v in reference.header.get_zooms()[:3]),
                           "affine": json.dumps(reference.affine.tolist()),
                           "resampled": ";".join(resampled)})
    return arrays, paths, reference.header.get_zooms()[:3]


def coordinate_arrays(arrays):
    cbf, cbv, mtt, tmax = (arrays[k] for k in ("cbf", "cbv", "mtt", "tmax"))
    finite_maps = np.isfinite(cbf) & np.isfinite(cbv) & np.isfinite(mtt) & np.isfinite(tmax)
    deficit = np.isfinite(tmax) & (tmax > 6.0)  # DEFUSE-family threshold frozen in contract.
    # Amended clause 66: use the per-patient 98th percentile because CBV units
    # are undocumented. Under the conventional scale this approximates the
    # vessel fraction targeted by the retired 8 mL/100 g cap.
    positive_cbv = cbv[np.isfinite(cbv) & (cbv > 0)]
    if positive_cbv.size == 0:
        fail(6, "CBV map has no finite positive values for the vessel percentile")
    vessel_cbv_p98 = float(np.percentile(positive_cbv, 98.0))
    assert np.isfinite(vessel_cbv_p98) and vessel_cbv_p98 > 0
    vessel = np.isfinite(cbv) & (cbv > vessel_cbv_p98)
    # Contract thresholds: Tmax > 6 seconds and the unit-free patient CBV p98.
    region = deficit.copy()
    # One-voxel binary erosion removes unstable deficit boundaries, as frozen
    # in preprocessing.region. Six face-neighbors make the 3-D voxel erosion.
    eroded = region.copy()
    for axis in range(3):
        eroded &= np.roll(region, 1, axis=axis)
        eroded &= np.roll(region, -1, axis=axis)
    eroded[[0, -1], :, :] = False; eroded[:, [0, -1], :] = False; eroded[:, :, [0, -1]] = False
    # Contract retains the two-voxel array-midline exclusion as a boundary safeguard.
    plane = (cbf.shape[0] - 1) / 2.0
    coordinates = np.arange(cbf.shape[0], dtype=float)
    eroded[np.abs(coordinates - plane) <= 2.0, :, :] = False
    eroded &= ~vessel & finite_maps & (cbf > 0) & (cbv > 0) & (mtt > 0)
    exclusions = {"deficit_voxels": int(deficit.sum()), "eroded_region_voxels": int(eroded.sum()),
                  "vessel_voxels": int(vessel.sum()),
                  "vessel_cbv_p98": vessel_cbv_p98,
                  "nonfinite_cbf_voxels": int((~np.isfinite(cbf)).sum()),
                  "nonfinite_cbv_voxels": int((~np.isfinite(cbv)).sum()),
                  "nonfinite_mtt_voxels": int((~np.isfinite(mtt)).sum()),
                  "nonfinite_tmax_voxels": int((~np.isfinite(tmax)).sum())}
    assert np.all(np.isfinite(cbf[eroded])) and np.all(cbf[eroded] > 0)
    assert np.all(np.isfinite(cbv[eroded])) and np.all(cbv[eroded] > 0)
    assert np.all(np.isfinite(mtt[eroded])) and np.all(mtt[eroded] > 0)
    return cbf, cbv, mtt, eroded, exclusions


def flow_band_labels(cbf, region):
    """Assign eligible voxels to fixed CBF percentile bands with stable ties."""
    flat_indices = np.flatnonzero(region)
    labels = np.zeros(cbf.size, dtype=np.uint8)
    if flat_indices.size:
        # Stable mergesort makes equal-CBF ties deterministic by original voxel index.
        order = np.argsort(cbf.ravel()[flat_indices], kind="mergesort")
        ranked_indices = flat_indices[order]
        positions = np.arange(ranked_indices.size)
        labels[ranked_indices[positions * 100 < ranked_indices.size * 33]] = 1
        labels[ranked_indices[(positions * 100 >= ranked_indices.size * 33) &
                              (positions * 100 < ranked_indices.size * 67)]] = 2
        labels[ranked_indices[positions * 100 >= ranked_indices.size * 67]] = 3
    labels = labels.reshape(cbf.shape)
    assert np.count_nonzero(labels) == np.count_nonzero(region)
    assert not np.any(labels[~region])
    return labels


def patient_native_z(arrays):
    cbf, cbv, mtt, region, exclusions = coordinate_arrays(arrays)
    bands = flow_band_labels(cbf, region)
    values, identity = [], []
    for index in range(1, 4):
        mask = region & (bands == index)
        assert np.all(np.isfinite(cbf[mask])) and np.all(np.isfinite(cbv[mask]))
        values.append(np.log(cbv[mask]))
        identity.append(np.log(mtt[mask]) - np.log(cbv[mask]) + np.log(cbf[mask]))
    return values, identity, exclusions, cbv, bands, region


def tissue_audit(case_id, ncct, cbv, bands, region, quartiles):
    """Summarize label-blind NCCT attenuation in each flow-band/style cell."""
    assert ncct.shape == cbv.shape == bands.shape == region.shape
    rows = []
    for index in range(1, 4):
        band = region & (bands == index)
        z = np.log(cbv[band])
        q1 = float(quartiles[f"q1_{index}"])
        q3 = float(quartiles[f"q3_{index}"])
        assert z.size == int(band.sum())
        assert np.isfinite(q1) and np.isfinite(q3) and q1 <= q3
        for style, selected in (("Q1_low_CBV", z <= q1), ("Q4_high_CBV", z >= q3)):
            hu = ncct[band][selected]
            finite_hu = hu[np.isfinite(hu)]
            # NCCT is stored in Hounsfield units; no conversion is applied.
            if finite_hu.size:
                q25, median, q75 = np.percentile(finite_hu, [25.0, 50.0, 75.0])
                assert np.isfinite(q25) and np.isfinite(median) and np.isfinite(q75)
                assert q25 <= median <= q75
                row = {"case_id": case_id, "stratum": index, "style_group": style,
                       "member_voxels": int(hu.size),
                       "finite_hu_voxels": int(finite_hu.size),
                       "nonfinite_hu_voxels": int(hu.size - finite_hu.size),
                       "median_hu": float(median), "q25_hu": float(q25),
                       "q75_hu": float(q75), "iqr_hu": float(q75 - q25)}
            else:
                # Missing HU support is recorded, but this audit creates no new gate.
                row = {"case_id": case_id, "stratum": index, "style_group": style,
                       "member_voxels": int(hu.size), "finite_hu_voxels": 0,
                       "nonfinite_hu_voxels": int(hu.size), "median_hu": "",
                       "q25_hu": "", "q75_hu": "", "iqr_hu": ""}
            assert row["finite_hu_voxels"] + row["nonfinite_hu_voxels"] == row["member_voxels"]
            rows.append(row)
    assert len(rows) == 6
    return rows


def patient_measure(case_id, lesion, min_voxels, cache):
    cbv, bands, region = cache["cbv"], cache["bands"], cache["region"].astype(bool)
    if np.any(~np.isfinite(lesion[region])):
        fail(6, f"nonfinite lesion-mask value in analyzed voxels for {case_id}")
    lesion = lesion > 0.5
    records = []
    for index in range(1, 4):
        mask = region & (bands == index)
        assert np.all(np.isfinite(cbv[mask])) and np.all(cbv[mask] > 0)
        z = np.log(cbv[mask])
        if z.size < 4:
            records.append({"case_id": case_id, "stratum": index, "q1_voxels": 0, "q4_voxels": 0, "d": ""})
            continue
        # These per-patient cuts were computed and checkpointed before labels opened.
        q1 = float(cache[f"q1_{index}"])
        q3 = float(cache[f"q3_{index}"])
        assert np.isfinite(q1) and np.isfinite(q3) and q1 <= q3
        labels = lesion[mask]
        lo_mask, hi_mask = z <= q1, z >= q3
        d = float(labels[lo_mask].mean() - labels[hi_mask].mean()) if lo_mask.sum() >= min_voxels and hi_mask.sum() >= min_voxels else ""
        records.append({"case_id": case_id, "stratum": index, "q1_voxels": int(lo_mask.sum()), "q4_voxels": int(hi_mask.sum()), "d": d})
    return records


def load_lesion(data_dir, case_id, shape, affine, selected_archive_path):
    """Load only the outcome mask and place it on the cached NCCT grid."""
    try:
        import nibabel as nib
        from nibabel.processing import resample_from_to
    except ImportError:
        fail(12, "nibabel and scipy are required for Phase C")
    path = find_archive_selected(data_dir, selected_archive_path)
    verify_required_gzip(path)
    image = nib.as_closest_canonical(nib.load(str(path)))
    resampled = image.shape != tuple(shape) or not np.allclose(image.affine, affine, atol=1e-5)
    if resampled:
        # The contract freezes nearest-neighbor interpolation for labels.
        image = resample_from_to(image, (tuple(shape), affine), order=0)
    return np.asarray(image.dataobj, dtype=np.float32), str(path), resampled


def atomic_npz(path, **arrays):
    """Write a resumable per-case checkpoint without exposing partial files."""
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("wb") as handle:
        np.savez_compressed(handle, **arrays)
    os.replace(temporary, path)


def distribution_row(index, values, prefix):
    """Compact, CSV-readable distribution sufficient to recreate the plot."""
    quantiles = np.quantile(values, [0, .01, .05, .25, .50, .75, .95, .99, 1])
    names = ("min", "q01", "q05", "q25", "q50", "q75", "q95", "q99", "max")
    row = {"stratum": index, f"{prefix}_voxels": int(values.size)}
    row.update({f"{prefix}_{name}": float(value) for name, value in zip(names, quantiles)})
    return row


def write_distribution_svg(path, rows, prefix, title):
    """Write a dependency-free quantile plot from the frozen label-blind rows."""
    width, height = 720, 250
    all_min = min(row[f"{prefix}_min"] for row in rows)
    all_max = max(row[f"{prefix}_max"] for row in rows)
    span = max(all_max - all_min, 1e-9)
    x = lambda value: 70 + 600 * (value - all_min) / span
    lines = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}">',
             '<rect width="100%" height="100%" fill="white"/>',
             f'<text x="20" y="25" font-family="sans-serif" font-size="16">{title}</text>']
    for offset, row in enumerate(rows):
        y = 70 + offset * 55
        lines.append(f'<text x="20" y="{y+5}" font-family="sans-serif">S{row["stratum"]}</text>')
        lines.append(f'<line x1="{x(row[f"{prefix}_q01"]):.1f}" y1="{y}" x2="{x(row[f"{prefix}_q99"]):.1f}" y2="{y}" stroke="black"/>')
        lines.append(f'<rect x="{x(row[f"{prefix}_q25"]):.1f}" y="{y-8}" width="{max(1, x(row[f"{prefix}_q75"])-x(row[f"{prefix}_q25"])):.1f}" height="16" fill="#9ecae1" stroke="black"/>')
        lines.append(f'<line x1="{x(row[f"{prefix}_q50"]):.1f}" y1="{y-10}" x2="{x(row[f"{prefix}_q50"]):.1f}" y2="{y+10}" stroke="#b30000" stroke-width="2"/>')
    lines.append(f'<text x="70" y="235" font-family="sans-serif" font-size="12">{all_min:.4g}</text>')
    lines.append(f'<text x="630" y="235" font-family="sans-serif" font-size="12">{all_max:.4g}</text>')
    lines.append('</svg>')
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


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
    phase_s_sha = verify_phase_s_hash(args)
    record = json.loads(args.record_json.read_text())
    archive_info = validate_record_and_archive(record, args.archive_file)
    members = archive_members(args.archive_file)
    write_csv(out / "archive_manifest.csv", ["path", "size", "crc"], members)
    # The archive member manifest is the population authority. Release prose
    # and extracted-directory globs are not allowed to define the cohort.
    case_ids, lesion_members, duplicate_lesions = archive_case_inventory(members)
    census, reserve = split_cases(case_ids)
    split_rows = [{"case_id": case, "population": "census" if case in census else "reserved",
                   "assignment_hash": hashlib.sha256(("idea-023-v1|" + case).encode()).hexdigest()}
                  for case in sorted(case_ids)]
    assert {r["case_id"] for r in split_rows if r["population"] == "census"}.isdisjoint(
        {r["case_id"] for r in split_rows if r["population"] == "reserved"})
    write_csv(out / "split_manifest.csv", ["case_id", "population", "assignment_hash"], split_rows)
    split_sha = sha256_file(out / "split_manifest.csv")
    manifest = {
        "idea_id": IDEA_ID,
        "phase": "C",
        "seed": SEED,
        "input_paths": {
            "archive": {"path": str(args.archive_file), "sha256": archive_info["archive_sha256"]},
            "record_json": {"path": str(args.record_json), "sha256": sha256_file(args.record_json)},
            "phase_s_csv": {"path": str(args.phase_s_dir / "simulation_operating_characteristics.csv"),
                            "sha256": phase_s_sha},
            "contract": {"path": str(CONTRACT), "sha256": sha256_file(CONTRACT)},
            "run_py": {"path": str(Path(__file__)), "sha256": sha256_file(Path(__file__))},
        },
        "archive_member_count": len(members),
        "input_row_count": len(members),
        "input_case_count": len(case_ids),
        "census_case_count": len(census),
        "reserved_case_count": len(reserve),
        "split_manifest_sha256": split_sha,
    }
    write_determinism_manifest(out, "start", manifest)
    provenance_path = out / "provenance.json"
    provenance = json.loads(provenance_path.read_text())
    provenance.update({**archive_info, "archive_member_count": len(members),
                       "released_case_count": len(case_ids),
                       "split_manifest_sha256": split_sha,
                       "simulation_output_sha256": phase_s_sha})
    write_json(provenance_path, provenance)
    min_n = int(scalar(CONTRACT.read_text(), "minimum_contributing_patients_per_stratum"))
    min_m = int(scalar(CONTRACT.read_text(), "minimum_voxels_per_patient_quantile_cell"))
    max_width = float(scalar(CONTRACT.read_text(), "maximum_primary_ci_width"))
    # Pass one is outcome-blind: only maps are opened. Each patient's fixed
    # CBF bands and CBV values are checkpointed before any lesion is opened.
    native_values = {1: [], 2: [], 3: []}
    identity_values = {1: [], 2: [], 3: []}
    tissue_rows = []
    schema_rows, exclusion_rows = [], []
    excluded_source_cases = set()
    for duplicate in duplicate_lesions:
        # The payload's 150th lesion row remains visible in both required audit
        # files. It is never silently absorbed into a patient's outcome.
        schema_rows.append({"case_id": duplicate["case_id"],
                            "files": json.dumps({"excluded_lesion": duplicate["path"],
                                                 "retained_lesion": duplicate["retained_path"]}, sort_keys=True),
                            "shape": "", "voxel_sizes_mm": "", "affine": "", "resampled": "",
                            "record_type": "excluded_archive_lesion",
                            "exclusion_reason": duplicate["reason"]})
        exclusion_rows.append({"case_id": duplicate["case_id"],
                               "record_type": "excluded_archive_lesion",
                               "reason": duplicate["reason"],
                               "source_path": duplicate["path"]})
    cache_dir = out / "phase_c_cache"
    cache_dir.mkdir(exist_ok=True)
    cache_identity_path = cache_dir / "identity.json"
    cache_identity = {"contract_blob": gate_info["contract_blob"],
                      "archive_sha256": archive_info["archive_sha256"],
                      "split_manifest_sha256": split_sha,
                      "run_py_sha256": sha256_file(Path(__file__)),
                      "units_documented": False,
                      "units_evidence": "No JSON sidecars among 2,983 archive members; NIfTI descrip fields are empty; inspected Zenodo, TU/e, and challenge-paper dataset descriptions name CBV but state no units."}
    if cache_identity_path.exists() and json.loads(cache_identity_path.read_text()) != cache_identity:
        fail(4, "Phase-C checkpoint identity differs from this contract/archive/split/code")
    write_json(cache_identity_path, cache_identity)
    for number, case in enumerate(sorted(census), 1):
        cache_path = cache_dir / f"{case}.npz"
        audit_path = cache_dir / f"{case}.json"
        if cache_path.exists() and audit_path.exists():
            emit(f"Label-blind map pass {number}/{CENSUS_N}: {case}; resume checkpoint hit")
            cached = np.load(cache_path)
            audit = json.loads(audit_path.read_text())
            values_by_stratum = [cached[f"z{i}"] for i in range(1, 4)]
            identity_by_stratum = [cached[f"u{i}"] for i in range(1, 4)]
            cached_tissue_rows = json.loads(str(cached["tissue_audit_json"]))
            assert len(cached_tissue_rows) == 6
        else:
            emit(f"Label-blind map pass {number}/{CENSUS_N}: {case}; computing and checkpointing")
            case_schema = []
            try:
                arrays, paths, zooms = load_case(args.data_dir, case, load_label=False, audit_rows=case_schema)
            except SourceCorruptMember as exc:
                emit(f"EXCLUDE {case}: source_corrupt_member: {exc.path} ({exc.detail})")
                excluded_source_cases.add(case)
                schema_rows.append({"case_id": case,
                                    "files": json.dumps({"source_corrupt_member": str(exc.path)}, sort_keys=True),
                                    "shape": "", "voxel_sizes_mm": "", "affine": "", "resampled": "",
                                    "record_type": "excluded_case",
                                    "exclusion_reason": "source_corrupt_member"})
                exclusion_rows.append({"case_id": case, "record_type": "excluded_case",
                                       "reason": "source_corrupt_member",
                                       "source_path": str(exc.path)})
                continue
            values_by_stratum, identity_by_stratum, exclusions, cbv, bands, region = patient_native_z(arrays)
            quartiles = {}
            for index, values in enumerate(values_by_stratum, 1):
                if values.size:
                    q1, q3 = np.quantile(values, [0.25, 0.75])
                else:
                    q1, q3 = np.nan, np.nan
                quartiles[f"q1_{index}"] = np.asarray(q1)
                quartiles[f"q3_{index}"] = np.asarray(q3)
            cached_tissue_rows = tissue_audit(
                case, arrays["ncct"], cbv, bands, region, quartiles
            )
            atomic_npz(cache_path, cbv=cbv, bands=bands, region=region,
                       affine=np.asarray(json.loads(case_schema[0]["affine"])),
                       tissue_audit_json=np.asarray(json.dumps(cached_tissue_rows, sort_keys=True)),
                       **quartiles,
                       **{f"z{i}": values_by_stratum[i-1] for i in range(1, 4)},
                       **{f"u{i}": identity_by_stratum[i-1] for i in range(1, 4)})
            audit = {"schema": case_schema[0],
                     "exclusions": {"case_id": case, **exclusions}}
            write_json(audit_path, audit)
        audit["schema"].setdefault("record_type", "analyzed_case")
        audit["schema"].setdefault("exclusion_reason", "")
        schema_rows.append(audit["schema"])
        audit["exclusions"].setdefault("record_type", "analyzed_case")
        audit["exclusions"].setdefault("reason", "")
        audit["exclusions"].setdefault("source_path", "")
        exclusion_rows.append(audit["exclusions"])
        tissue_rows.extend(cached_tissue_rows)
        for index, values in enumerate(values_by_stratum, 1):
            native_values[index].append(values)
            identity_values[index].append(identity_by_stratum[index - 1])
    schema_fields = ["case_id", "record_type", "exclusion_reason", "files", "shape",
                     "voxel_sizes_mm", "affine", "resampled"]
    exclusion_fields = ["case_id", "record_type", "reason", "source_path",
                        "deficit_voxels", "eroded_region_voxels",
                        "vessel_voxels", "vessel_cbv_p98",
                        "nonfinite_cbf_voxels", "nonfinite_cbv_voxels",
                        "nonfinite_mtt_voxels", "nonfinite_tmax_voxels"]
    write_csv(out / "schema_census.csv", schema_fields, schema_rows)
    write_csv(out / "exclusions.csv", exclusion_fields, exclusion_rows)
    tissue_fields = ["case_id", "stratum", "style_group", "member_voxels",
                     "finite_hu_voxels", "nonfinite_hu_voxels", "median_hu",
                     "q25_hu", "q75_hu", "iqr_hu"]
    assert len(tissue_rows) == 6 * (len(census) - len(excluded_source_cases))
    write_csv(out / "bin_tissue_audit.csv", tissue_fields, tissue_rows)
    # Contract centers u once across the whole census, then gates every stratum before labels open.
    all_u = np.concatenate([x for cells in identity_values.values() for x in cells if x.size])
    if all_u.size == 0:
        fail(9, "central-volume identity coordinate has no supported voxels")
    census_median_u = float(np.median(all_u))
    centered, identity_rows = {}, []
    for index in range(1, 4):
        vals = np.concatenate([x for x in identity_values[index] if x.size]) - census_median_u
        centered[index] = float(np.median(np.abs(vals)))
        row = distribution_row(index, vals, "centered_residual")
        row.update({"census_median_u": census_median_u,
                    "median_absolute_centered_residual": centered[index]})
        identity_rows.append(row)
    write_csv(out / "identity_residual_summary.csv",
              list(identity_rows[0]), identity_rows)
    write_distribution_svg(out / "identity_residual_distribution.svg", identity_rows,
                           "centered_residual", "Centered central-volume identity residual")
    # Persist the full diagnostic distribution before an invalidating exit.
    for index in range(1, 4):
        if centered[index] > 0.10:
            fail(9, f"stratum {index} identity residual {centered[index]:.4f} exceeds 0.10")
    support_rows = []
    for index in range(1, 4):
        pooled = np.concatenate(native_values[index])
        if pooled.size == 0: fail(10, f"stratum {index} has no native support")
        support_rows.append(distribution_row(index, pooled, "log_cbv"))
    write_csv(out / "support_summary.csv", list(support_rows[0]), support_rows)
    write_distribution_svg(out / "native_support.svg", support_rows, "log_cbv",
                           "Native log(CBV) support by within-patient CBF band")

    # Pass two opens lesion masks only after split and quantile boundaries are
    # immutable. It emits one row per patient and stratum.
    per_patient = []
    outcome_checkpoint = cache_dir / "per_patient_checkpoint.csv"
    if outcome_checkpoint.exists():
        with outcome_checkpoint.open(newline="", encoding="utf-8") as handle:
            per_patient = list(csv.DictReader(handle))
        for row in per_patient:
            row["stratum"] = int(row["stratum"])
            row["q1_voxels"] = int(row["q1_voxels"])
            row["q4_voxels"] = int(row["q4_voxels"])
    completed = {row["case_id"] for row in per_patient}
    for number, case in enumerate(sorted(census), 1):
        if case in excluded_source_cases:
            emit(f"Outcome pass {number}/{CENSUS_N}: {case}; excluded source_corrupt_member")
            continue
        if case in completed:
            emit(f"Outcome pass {number}/{CENSUS_N}: {case}; resume checkpoint hit")
            continue
        emit(f"Outcome pass {number}/{CENSUS_N}: {case}; running rows={len(per_patient)}")
        try:
            with np.load(cache_dir / f"{case}.npz") as cache:
                lesion, lesion_path, label_resampled = load_lesion(
                    args.data_dir, case, cache["region"].shape, cache["affine"],
                    lesion_members[case]["path"]
                )
                rows = patient_measure(case, lesion, min_m, cache)
        except SourceCorruptMember as exc:
            emit(f"EXCLUDE {case}: source_corrupt_member: {exc.path} ({exc.detail})")
            excluded_source_cases.add(case)
            schema = next(row for row in schema_rows
                          if row["case_id"] == case and row["record_type"] == "analyzed_case")
            schema["record_type"] = "excluded_case"
            schema["exclusion_reason"] = "source_corrupt_member"
            schema["files"] = json.dumps({**json.loads(schema["files"]),
                                           "source_corrupt_member": str(exc.path)}, sort_keys=True)
            exclusion_rows.append({"case_id": case, "record_type": "excluded_case",
                                   "reason": "source_corrupt_member",
                                   "source_path": str(exc.path)})
            continue
        schema = next(row for row in schema_rows
                      if row["case_id"] == case and row["record_type"] == "analyzed_case")
        schema["files"] = json.dumps({**json.loads(schema["files"]), "lesion": lesion_path}, sort_keys=True)
        if label_resampled:
            schema["resampled"] = ";".join(filter(None, (schema["resampled"], "lesion")))
        audit_path = cache_dir / f"{case}.json"
        audit = json.loads(audit_path.read_text())
        audit["schema"] = schema
        write_json(audit_path, audit)
        per_patient.extend(rows)
        write_csv(outcome_checkpoint, list(per_patient[0]), per_patient)
    # Rewrite both audit files after outcome access so a defective label member
    # is retained even when it is discovered in the second pass.
    write_csv(out / "schema_census.csv", schema_fields, schema_rows)
    write_csv(out / "exclusions.csv", exclusion_fields, exclusion_rows)
    write_csv(out / "per_patient.csv", list(per_patient[0]), per_patient)
    rng = np.random.default_rng(SEED)
    summaries = []
    common_signs, excluded = [], 0
    for index in range(1, 4):
        values = np.array([float(r["d"]) for r in per_patient if r["stratum"] == index and r["d"] != ""])
        if len(values) < min_n: fail(10, f"stratum {index} has {len(values)} contributing patients; needs {min_n}")
        indices = rng.integers(0, len(values), (BOOTSTRAPS, len(values)))
        draws = np.mean(values[indices], axis=1)
        median_draws = np.median(values[indices], axis=1)
        lo, hi = np.percentile(draws, [2.5, 97.5]); point = float(values.mean())
        median_lo, median_hi = np.percentile(median_draws, [2.5, 97.5])
        sign = int(np.sign(point))
        common_signs.append(sign)
        # The interval must exclude zero in the point estimate's common direction.
        excluded += int((sign > 0 and lo > 0) or (sign < 0 and hi < 0))
        summaries.append({"stratum": index, "patients": len(values), "mean_d": point,
                          "median_d": float(np.median(values)),
                          "median_ci_low": float(median_lo), "median_ci_high": float(median_hi),
                          "ci_low": float(lo),
                          "ci_high": float(hi), "ci_width": float(hi-lo)})
    passed = len(set(common_signs)) == 1 and common_signs[0] != 0 and excluded >= 2 and all(r["ci_width"] <= max_width for r in summaries)
    with (out / "per_stratum_summary.csv").open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(summaries[0])); writer.writeheader(); writer.writerows(summaries)
    summary = {"idea_id": IDEA_ID, "phase": "C", "status": "POSITIVE_PATTERN" if passed else "NEGATIVE_PATTERN",
               "g_label_passed": passed, "per_stratum": summaries, "identity_mad": centered,
               "released_case_count": len(case_ids), "census_case_count": len(census),
               "analyzed_census_case_count": len(census) - len(excluded_source_cases),
               "reserved_case_count": len(reserve), "split_manifest_sha256": split_sha,
               "excluded_duplicate_lesion_members": len(duplicate_lesions),
               "excluded_source_corrupt_cases": len(excluded_source_cases),
               "bin_tissue_audit_rows": len(tissue_rows),
               "bin_tissue_audit_file": "bin_tissue_audit.csv",
               "simulation_output_sha256": phase_s_sha, **archive_info, **gate_info}
    write_json(out / "summary.json", summary)
    write_determinism_manifest(out, "end", manifest)
    assert json.loads((out / "determinism_manifest_start.json").read_text()) == manifest
    assert json.loads((out / "determinism_manifest_end.json").read_text()) == manifest
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
    parser.add_argument("--phase-s-dir", type=Path)
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    global LOG; LOG = args.output_dir / "run_log.txt"
    try:
        phase = "SMOKE" if args.smoke else args.phase
        info = {"contract_blob": blob_sha1(CONTRACT)} if args.smoke else gate(args.phase)
        resolved = {"phase": phase, "seed": SEED,
                    "cbf_percentile_bands": CBF_PERCENTILE_BANDS,
                    "label_blind_ncct_tissue_audit": True, **info}
        if args.phase == "C":
            resolved.update({
                "minimum_contributing_patients_per_stratum": int(scalar(CONTRACT.read_text(), "minimum_contributing_patients_per_stratum")),
                "minimum_voxels_per_patient_quantile_cell": int(scalar(CONTRACT.read_text(), "minimum_voxels_per_patient_quantile_cell")),
                "maximum_primary_ci_width": float(scalar(CONTRACT.read_text(), "maximum_primary_ci_width")),
            })
        write_json(args.output_dir / "resolved_config.json", resolved)
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
