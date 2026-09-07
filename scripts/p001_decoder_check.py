#!/usr/bin/env python3
"""Check P001's decoder convention using only generated NIfTI fixtures.

No archive, cohort table, labels or patient files are opened. This checks software
scaling and the frozen float32 policy; it cannot establish a dataset's units.
Run with P001's pinned requirements and retain stdout as a synthetic receipt.
"""
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile

import nibabel as nib
import numpy as np


def check():
    if (np.__version__, nib.__version__) != ('2.3.3', '5.3.2'):
        raise ValueError('P001_PINNED_DEPENDENCIES_REQUIRED')
    runner = Path(__file__).resolve().parents[1] / 'campaigns/isles24-pilot/experiments/P001/run.py'
    runner_hash = hashlib.sha256(runner.read_bytes()).hexdigest()
    if runner_hash != 'd54e3ea5c45c0d47fe8bace014058e1660d92b72abc36cc2fdc077acae3d47b0':
        raise ValueError('FROZEN_P001_RUNNER_REQUIRED')
    spec = importlib.util.spec_from_file_location('p001_synthetic_decoder', runner)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    # Import defines functions only. Never call selection(), run(), or metrics().
    rows = []
    with tempfile.TemporaryDirectory(prefix='p001-decoder-synthetic-') as directory:
        for name, stored, slope, intercept in [
            ('identity', np.array([5, 6, 7, 8], dtype=np.int16), 1., 0.),
            ('scaled', np.array([1, 2, 3, 4], dtype=np.int16), 2., 1.),
            ('offset', np.array([4, 5, 6, 7], dtype=np.int16), 1., 1.),
            ('rounding', np.array([6., 6.+1e-8, 6.-1e-8, 6.+1e-5]), 1., 0.),
        ]:
            stored = stored.reshape(2, 2, 1)
            image = nib.Nifti1Image(stored, np.eye(4))
            image.header.set_slope_inter(slope, intercept)
            path = Path(directory) / (name + '.nii.gz')
            nib.save(image, path)
            loaded = nib.load(path)
            decoded = np.asarray(loaded.dataobj, dtype=np.float32)
            expected = (stored.astype(np.float64) * slope + intercept).astype(np.float32)
            if not np.array_equal(decoded, expected):
                raise ValueError('SYNTHETIC_SCALING_MISMATCH')
            if not np.array_equal(decoded, loaded.get_fdata(dtype=np.float32)):
                raise ValueError('SYNTHETIC_DECODER_MISMATCH')
            predicted = module.predict(decoded)
            if not np.array_equal(predicted, expected > 6.):
                raise ValueError('FROZEN_THRESHOLD_MISMATCH')
            differences = int(np.count_nonzero(predicted != (loaded.get_fdata() > 6.)))
            if differences != (1 if name == 'rounding' else 0):
                raise ValueError('UNEXPECTED_PRECISION_BEHAVIOR')
            rows.append({'fixture': name, 'passed': True,
                         'float64_threshold_differences': differences})
    return {'status': 'PASS_SYNTHETIC_ONLY', 'numpy': np.__version__,
            'nibabel': nib.__version__, 'runner_sha256': runner_hash,
            'check_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            'fixtures': rows, 'patient_files_opened': 0,
            'conclusion': 'Proxy scaling agrees with get_fdata at the frozen float32 precision. Float64 can differ at a rounding boundary; no precision amendment is implied.',
            'limitation': 'Does not verify archive-specific units, headers or current integrity.'}


if __name__ == '__main__':
    print(json.dumps(check(), indent=2))
