from pathlib import Path
import pytest
from orchestrator.git_publication import scan_history_blob


def test_exact_synthetic_test_version_only():
    root=Path(__file__).resolve().parents[1]
    name='tests/test_human_controls.py';raw=(root/name).read_bytes()
    scan_history_blob(root,'a'*40,name,raw)
    with pytest.raises(ValueError): scan_history_blob(root,'a'*40,'docs/copied-test.py',raw)
    with pytest.raises(ValueError): scan_history_blob(root,'a'*40,name,raw+b'\n# altered\n')
