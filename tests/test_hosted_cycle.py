import json
import tempfile
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import pytest
from orchestrator.hosted_cycle import claim
from orchestrator.operations_report import immutable
from orchestrator.remote_supervisor import lock


def test_unknown_call_is_never_replayed_and_binding_is_preserved():
    with tempfile.TemporaryDirectory() as temp:
        p = Path(temp)/'attempt'; b = {'event': 'synthetic', 'source': 'a'*40}
        assert claim(p, b)
        with pytest.raises(ValueError, match='INCOMPLETE'): claim(p, b)
        with pytest.raises(ValueError, match='BINDING'): claim(p, {**b, 'source': 'b'*40})
        immutable(p/'complete.json', b'{}')
        assert claim(p, b) is False


def test_concurrent_dispatch_claims_only_one_attempt():
    with tempfile.TemporaryDirectory() as temp:
        p = Path(temp)
        def attempt(_):
            with lock(p/'driver.lock'):
                try: return claim(p/'event', {'event': 'synthetic'})
                except ValueError: return False
        with ThreadPoolExecutor(max_workers=4) as pool:
            assert sum(pool.map(attempt, range(8))) == 1


def test_missing_binding_is_ambiguous_not_a_fresh_admission():
    with tempfile.TemporaryDirectory() as temp:
        p = Path(temp)/'attempt'; p.mkdir()
        with pytest.raises(ValueError, match='INCOMPLETE'): claim(p, {})


def test_cycle_binding_directory_is_synced(monkeypatch):
    from orchestrator import hosted_cycle
    calls=[]
    monkeypatch.setattr(hosted_cycle, 'sync_dir', lambda p: calls.append(Path(p)))
    with tempfile.TemporaryDirectory() as temp:
        p=Path(temp)/'attempt'
        claim(p, {'event':'synthetic'})
        assert Path(temp) in calls and p in calls
