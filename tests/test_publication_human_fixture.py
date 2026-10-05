"""Retain the exact historical exception; current fixtures use ordinary scanning."""
import hashlib
from pathlib import Path
import subprocess

import pytest

from orchestrator.git_publication import scan, scan_history_blob

ORIGINAL_FIXTURE_BLOB = '2d2888d171c783cec49e22dead26eccb395134fd'
ORIGINAL_FIXTURE_SHA256 = '9a50b783e8e19cc1107cb22bd10c1157e27577afaa269666416ff86430337dc1'


def test_exact_synthetic_test_version_only():
    root = Path(__file__).resolve().parents[1]
    name = 'tests/test_human_controls.py'
    original = subprocess.check_output(['git', 'show', ORIGINAL_FIXTURE_BLOB], cwd=root)
    assert hashlib.sha256(original).hexdigest() == ORIGINAL_FIXTURE_SHA256
    scan_history_blob(root, 'a' * 40, name, original)
    with pytest.raises(ValueError):
        scan_history_blob(root, 'a' * 40, 'docs/copied-test.py', original)
    with pytest.raises(ValueError):
        scan_history_blob(root, 'a' * 40, name, original + b'\n# altered\n')


def test_current_human_fixture_needs_no_historical_exception():
    root = Path(__file__).resolve().parents[1]
    name = 'tests/test_human_controls.py'
    current = (root / name).read_bytes()
    assert hashlib.sha256(current).hexdigest() != ORIGINAL_FIXTURE_SHA256
    scan(name, current)
    scan('docs/copied-test.py', current)
    scan_history_blob(root, 'a' * 40, name, current)
