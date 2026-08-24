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
import importlib.metadata
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
        # Phase S uses the same direction-aware exclusion rule as Phase C.
        excludes.append(bool((point > 0 and lo > 0) or (point < 0 and hi < 0)))
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
# units, finite values, mirror support, and the central-volume coordinate.
# ---------------------------------------------------------------------------

def load_case(data_dir, case_id, load_label, audit_rows=None):
    try:
        import nibabel as nib
    except ImportError:
        fail(12, "nibabel is required for Phase C")
    paths = {k: find_one(data_dir, case_id, k) for k in ("cbf", "cbv", "mtt", "tmax", "ncct")}
    if load_label:
        paths["lesion"] = find_one(data_dir, case_id, "lesion")
    images = {k: nib.load(str(p)) for k, p in paths.items()}
    # Canonical RAS makes array axis 0 the anatomical left-right axis used by reflection.
    reference = nib.as_closest_canonical(images["ncct"])
    images["ncct"] = reference
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


def confirm_cbv_units(cbv_path):
    sidecar = Path(re.sub(r"\.nii(?:\.gz)?$", ".json", str(cbv_path)))
    texts = []
    if sidecar.exists():
        texts.append(json.dumps(json.loads(sidecar.read_text()), sort_keys=True).lower())
    try:
        import nibabel as nib
        texts.append(bytes(nib.load(str(cbv_path)).header["descrip"]).decode("latin1").lower())
    except Exception:
        pass
    normalized = re.sub(r"[\s_/.-]", "", " ".join(texts))
    if not ("ml100g" in normalized or "mlper100g" in normalized):
        fail(8, f"CBV unit mL/100 g is not explicitly documented for {cbv_path}")


def reflect_index(length, plane):
    indices = np.arange(length)
    reflected = np.rint(2.0 * plane - indices).astype(int)
    return reflected, (reflected >= 0) & (reflected < length)


def mirror_qc(ncct, zooms):
    """Freeze a simple NCCT-derived brain mask and midsagittal reflection."""
    from scipy import ndimage
    # NCCT brain proxy: plausible intracranial tissue range, then fill holes and keep largest component.
    mask = np.isfinite(ncct) & (ncct >= -20.0) & (ncct <= 120.0)
    mask = ndimage.binary_closing(mask, iterations=2)
    labels, count = ndimage.label(mask)
    if count == 0:
        fail(7, "NCCT-derived brain mask is empty")
    sizes = ndimage.sum(mask, labels, range(1, count + 1))
    mask = labels == (int(np.argmax(sizes)) + 1)
    center = (ncct.shape[0] - 1) / 2.0
    candidates = np.arange(center - 5.0, center + 5.01, 0.5)
    scores = []
    scale = max(float(np.percentile(ncct[mask], 95) - np.percentile(ncct[mask], 5)), 1.0)
    for plane in candidates:
        reflected, valid = reflect_index(ncct.shape[0], plane)
        mirrored = ncct[np.clip(reflected, 0, ncct.shape[0] - 1), :, :]
        paired = mask & valid[:, None, None] & mask[np.clip(reflected, 0, ncct.shape[0] - 1), :, :]
        if paired.any():
            intensity_error = float(np.median(np.abs(ncct[paired] - mirrored[paired])) / scale)
            overlap_penalty = 1.0 - float(paired.sum() / mask.sum())
            score = intensity_error + overlap_penalty
        else:
            score = np.inf
        scores.append(score)
    plane = float(candidates[int(np.argmin(scores))])
    reflected, valid = reflect_index(ncct.shape[0], plane)
    clipped = np.clip(reflected, 0, ncct.shape[0] - 1)
    reflected_mask = mask[clipped, :, :] & valid[:, None, None]
    usable = mask & reflected_mask
    fraction = float(usable.sum() / mask.sum())
    # Median symmetric boundary distance is the frozen left-right registration error in voxels.
    boundary = mask ^ ndimage.binary_erosion(mask)
    reflected_boundary = boundary[clipped, :, :] & valid[:, None, None]
    to_boundary = ndimage.distance_transform_edt(~boundary)
    to_reflected = ndimage.distance_transform_edt(~reflected_boundary)
    distances = np.concatenate((to_boundary[reflected_boundary], to_reflected[boundary]))
    registration_error = float(np.median(distances)) if distances.size else np.inf
    return mask, reflected, plane, registration_error, fraction, float(min(scores))


def neighborhood_median(source, allowed, reflected):
    """Vectorized, slab-bounded median of each reflected 5x5x3 neighborhood."""
    mirrored = source[np.clip(reflected, 0, source.shape[0] - 1), :, :].astype(np.float32)
    mirrored_allowed = allowed[np.clip(reflected, 0, source.shape[0] - 1), :, :]
    mirrored[~mirrored_allowed] = np.nan
    # The contract freezes a 5x5x3 voxel window. Slabs avoid materializing all
    # 75 neighbors for a full CT volume while eliminating Python voxel callbacks.
    padded = np.pad(mirrored, ((2, 2), (2, 2), (1, 1)), constant_values=np.nan)
    result = np.empty_like(mirrored)
    window_values_per_x = max(1, source.shape[1] * source.shape[2] * 75)
    slab = max(1, min(source.shape[0], 12_000_000 // window_values_per_x))
    for start in range(0, source.shape[0], slab):
        stop = min(start + slab, source.shape[0])
        view = np.lib.stride_tricks.sliding_window_view(
            padded[start:stop + 4], (5, 5, 3)
        )
        with np.errstate(all="ignore"):
            result[start:stop] = np.nanmedian(view, axis=(-3, -2, -1))
    return result


def coordinate_arrays(arrays, mirror):
    cbf, cbv, mtt, tmax = (arrays[k] for k in ("cbf", "cbv", "mtt", "tmax"))
    brain, reflected, plane = mirror
    finite_maps = np.isfinite(cbf) & np.isfinite(cbv) & np.isfinite(mtt) & np.isfinite(tmax)
    deficit = np.isfinite(tmax) & (tmax > 6.0)  # DEFUSE-family threshold frozen in contract.
    vessel = np.isfinite(cbv) & (cbv > 8.0)     # mL/100 g cap; units are gated first.
    allowed = brain & ~deficit & ~vessel
    mirror_cbf = neighborhood_median(cbf, allowed, reflected)
    mirror_cbv = neighborhood_median(cbv, allowed, reflected)
    valid_den = np.isfinite(mirror_cbf) & np.isfinite(mirror_cbv) & (mirror_cbf > 0) & (mirror_cbv > 0)
    rcbf = np.divide(cbf, mirror_cbf, out=np.full_like(cbf, np.nan), where=valid_den)
    rcbv = np.divide(cbv, mirror_cbv, out=np.full_like(cbv, np.nan), where=valid_den)
    # Contract threshold: Tmax > 6 seconds; CBV vessel cap 8 mL/100 g.
    region = deficit.copy()
    # One-voxel binary erosion removes unstable deficit boundaries, as frozen
    # in preprocessing.region. Six face-neighbors make the 3-D voxel erosion.
    eroded = region.copy()
    for axis in range(3):
        eroded &= np.roll(region, 1, axis=axis)
        eroded &= np.roll(region, -1, axis=axis)
    eroded[[0, -1], :, :] = False; eroded[:, [0, -1], :] = False; eroded[:, :, [0, -1]] = False
    # Contract excludes two voxels on either side of the estimated midline.
    coordinates = np.arange(cbf.shape[0], dtype=float)
    eroded[np.abs(coordinates - plane) <= 2.0, :, :] = False
    eroded &= brain & ~vessel & valid_den & finite_maps
    exclusions = {"deficit_voxels": int(deficit.sum()), "eroded_region_voxels": int(eroded.sum()),
                  "invalid_or_nonpositive_denominator_voxels": int((brain & ~valid_den).sum()),
                  "vessel_voxels": int(vessel.sum()),
                  "nonfinite_cbf_voxels": int((~np.isfinite(cbf)).sum()),
                  "nonfinite_cbv_voxels": int((~np.isfinite(cbv)).sum()),
                  "nonfinite_mtt_voxels": int((~np.isfinite(mtt)).sum()),
                  "nonfinite_tmax_voxels": int((~np.isfinite(tmax)).sum())}
    return cbf, cbv, mtt, rcbf, rcbv, eroded, exclusions


def patient_native_z(arrays, mirror):
    cbf, cbv, mtt, rcbf, rcbv, region, exclusions = coordinate_arrays(arrays, mirror)
    values, identity = [], []
    for low, high in STRATA:
        mask = region & (rcbf >= low) & (rcbf < high) & (rcbv > 0) & (cbf > 0) & (cbv > 0) & (mtt > 0)
        values.append(np.log(rcbv[mask]))
        identity.append(np.log(mtt[mask]) - np.log(cbv[mask]) + np.log(cbf[mask]))
    return values, identity, exclusions, rcbf, rcbv, region


def patient_measure(case_id, lesion, min_voxels, quartile_cuts, cache):
    rcbf, rcbv, region = cache["rcbf"], cache["rcbv"], cache["region"].astype(bool)
    if np.any(~np.isfinite(lesion[region])):
        fail(6, f"nonfinite lesion-mask value in analyzed voxels for {case_id}")
    lesion = lesion > 0.5
    records = []
    for index, (low, high) in enumerate(STRATA, 1):
        mask = region & (rcbf >= low) & (rcbf < high) & (rcbv > 0)
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
    return records


def load_lesion(data_dir, case_id, shape, affine):
    """Load only the outcome mask and place it on the cached NCCT grid."""
    try:
        import nibabel as nib
        from nibabel.processing import resample_from_to
    except ImportError:
        fail(12, "nibabel and scipy are required for Phase C")
    path = find_one(data_dir, case_id, "lesion")
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
    case_ids = discover_cases(args.data_dir)
    census, reserve = split_cases(case_ids)
    split_rows = [{"case_id": case, "population": "census" if case in census else "reserved",
                   "assignment_hash": hashlib.sha256(("idea-023-v1|" + case).encode()).hexdigest()}
                  for case in sorted(case_ids)]
    assert {r["case_id"] for r in split_rows if r["population"] == "census"}.isdisjoint(
        {r["case_id"] for r in split_rows if r["population"] == "reserved"})
    write_csv(out / "split_manifest.csv", ["case_id", "population", "assignment_hash"], split_rows)
    split_sha = sha256_file(out / "split_manifest.csv")
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
    # Pass one is outcome-blind: only maps are opened, and census-wide native
    # quartile boundaries are frozen before any lesion filename is resolved.
    native_values = {1: [], 2: [], 3: []}
    identity_values = {1: [], 2: [], 3: []}
    schema_rows, mirror_rows, exclusion_rows = [], [], []
    cache_dir = out / "phase_c_cache"
    cache_dir.mkdir(exist_ok=True)
    cache_identity_path = cache_dir / "identity.json"
    cache_identity = {"contract_blob": gate_info["contract_blob"],
                      "archive_sha256": archive_info["archive_sha256"],
                      "split_manifest_sha256": split_sha,
                      "run_py_sha256": sha256_file(Path(__file__))}
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
        else:
            emit(f"Label-blind map pass {number}/{CENSUS_N}: {case}; computing and checkpointing")
            case_schema = []
            arrays, paths, zooms = load_case(args.data_dir, case, load_label=False, audit_rows=case_schema)
            confirm_cbv_units(paths["cbv"])
            brain, reflected, plane, error, usable, score = mirror_qc(arrays["ncct"], zooms)
            mirror_row = {"case_id": case, "plane_axis0": plane,
                          "registration_error_voxels": error, "usable_brain_fraction": usable,
                          "normalized_median_absolute_error": score}
            values_by_stratum, identity_by_stratum, exclusions, rcbf, rcbv, region = patient_native_z(
                arrays, (brain, reflected, plane)
            )
            atomic_npz(cache_path, rcbf=rcbf, rcbv=rcbv, region=region,
                       affine=np.asarray(json.loads(case_schema[0]["affine"])),
                       **{f"z{i}": values_by_stratum[i-1] for i in range(1, 4)},
                       **{f"u{i}": identity_by_stratum[i-1] for i in range(1, 4)})
            audit = {"schema": case_schema[0], "mirror": mirror_row,
                     "exclusions": {"case_id": case, **exclusions}}
            write_json(audit_path, audit)
        schema_rows.append(audit["schema"])
        mirror_rows.append(audit["mirror"])
        exclusion_rows.append(audit["exclusions"])
        for index, values in enumerate(values_by_stratum, 1):
            native_values[index].append(values)
            identity_values[index].append(identity_by_stratum[index - 1])
    # Frozen mirror gate: individual registration error <=1 voxel and >=90% usable support in >=90 patients.
    good_mirror = sum(r["registration_error_voxels"] <= 1.0 and r["usable_brain_fraction"] >= 0.90
                      for r in mirror_rows)
    write_csv(out / "mirror_qc.csv", list(mirror_rows[0]), mirror_rows)
    write_csv(out / "schema_census.csv", list(schema_rows[0]), schema_rows)
    write_csv(out / "exclusions.csv", list(exclusion_rows[0]), exclusion_rows)
    if good_mirror < 90:
        fail(7, f"mirror gate passed for {good_mirror}/100 patients; requires at least 90")

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
    quartile_cuts = {}
    support_rows = []
    for index in range(1, 4):
        pooled = np.concatenate(native_values[index])
        if pooled.size == 0: fail(10, f"stratum {index} has no native support")
        quartile_cuts[index] = tuple(float(x) for x in np.quantile(pooled, [0.25, 0.75]))
        support_rows.append(distribution_row(index, pooled, "log_rcbv"))
    write_csv(out / "support_summary.csv", list(support_rows[0]), support_rows)
    write_distribution_svg(out / "native_support.svg", support_rows, "log_rcbv",
                           "Native log(rCBV) support by matched-rCBF stratum")

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
        if case in completed:
            emit(f"Outcome pass {number}/{CENSUS_N}: {case}; resume checkpoint hit")
            continue
        emit(f"Outcome pass {number}/{CENSUS_N}: {case}; running rows={len(per_patient)}")
        with np.load(cache_dir / f"{case}.npz") as cache:
            lesion, lesion_path, label_resampled = load_lesion(
                args.data_dir, case, cache["region"].shape, cache["affine"]
            )
            rows = patient_measure(case, lesion, min_m, quartile_cuts, cache)
        schema = next(row for row in schema_rows if row["case_id"] == case)
        schema["files"] = json.dumps({**json.loads(schema["files"]), "lesion": lesion_path}, sort_keys=True)
        if label_resampled:
            schema["resampled"] = ";".join(filter(None, (schema["resampled"], "lesion")))
        audit_path = cache_dir / f"{case}.json"
        audit = json.loads(audit_path.read_text())
        audit["schema"] = schema
        write_json(audit_path, audit)
        per_patient.extend(rows)
        write_csv(outcome_checkpoint, list(per_patient[0]), per_patient)
    write_csv(out / "schema_census.csv", list(schema_rows[0]), schema_rows)
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
               "reserved_case_count": len(reserve), "split_manifest_sha256": split_sha,
               "simulation_output_sha256": phase_s_sha, **archive_info, **gate_info}
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
    parser.add_argument("--phase-s-dir", type=Path)
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    global LOG; LOG = args.output_dir / "run_log.txt"
    try:
        phase = "SMOKE" if args.smoke else args.phase
        info = {"contract_blob": blob_sha1(CONTRACT)} if args.smoke else gate(args.phase)
        resolved = {"phase": phase, "seed": SEED, "strata": STRATA, **info}
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
