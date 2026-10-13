"""Exercise operational migration against the exact shipped scientific lease code."""
import copy
import hashlib
import json
import os
from pathlib import Path
import time
import pytest
from tools import colab_operational_resume as r

class Backend:
    def __init__(self):
        self.value = {}
        self.etag = 0
        self.now = 1000.0
        self.race = False
        self.fail_update_after = None
    def read(self):
        return str(self.etag), self.now, copy.deepcopy(self.value)
    def replace(self, etag, value):
        if self.race:
            self.etag += 1
            self.race = False
        if etag != str(self.etag):
            raise RuntimeError("CAS collision")
        if self.fail_update_after == self.etag:
            raise RuntimeError("injected transport refusal")
        self.value = copy.deepcopy(value)
        self.etag += 1

@pytest.fixture(params=["pnormct", "pnorm_v2"])
def exact_module(request, tmp_path, monkeypatch):
    root = Path(os.environ["COLAB_EXACT_MODULE_FIXTURES"])
    arm = "A1_" + request.param
    m = r.load_module(root / (request.param + "-exact-execution.py"), arm)
    m.RESULTS_ROOT = str(tmp_path / arm)
    cpu = {"effective_logical_capacity": 12, "logical_cpu_count": 12,
           "affinity_logical_cpus": 12, "quota_cpu_equivalents": None}
    env = {"cpu": cpu, "ram_bytes": 167 * 2**30, "augmentation_workers_requested": 2}
    m.cpu_capacity = lambda: cpu
    m.actual_environment = lambda: copy.deepcopy(env)
    m.compatible_env = lambda _env: {"synthetic_test_environment": True}
    locks = {str(k): Backend() for k in range(5)}
    m.DriveCAS = lambda name: locks[name]
    m.load_input_reference = lambda: {"fit_lock_ids": {str(k): str(k) for k in range(5)}}
    legacy = {k: {"module_sha256": r.PROFILES[arm],
                  "input_reference_sha256": m.INPUT_REFERENCE_SHA256,
                  "scientific_config": m.fit_config(k),
                  "compatible_environment": m.compatible_env(env)}
              for k in range(5)}
    real_sysconf = os.sysconf
    monkeypatch.setattr(r.os, "sysconf", lambda name: (
        4096 if name == "SC_PAGE_SIZE" else
        (167 * 2**30 // 4096) if name == "SC_PHYS_PAGES" else real_sysconf(name)))
    return m, locks, legacy

def seed(m, backend, binding, *, completed=False):
    root = Path(m.RESULTS_ROOT) / m.K_AM / "fold0"
    root.mkdir(parents=True)
    payload = root / "original.pth"
    payload.write_bytes(b"synthetic checkpoint payload; no pickle or patient data")
    prep = m.save_record(root, "original-prep.json", {"binding": binding, "path": "prepared", "steps": {}})
    checkpoint = {"binding": binding, "path": "original.pth",
                  **m.file_info(payload), "metadata": {"next_epoch": 85, "total_epochs": 250}}
    cp = m.save_record(root, "original-checkpoint.json", checkpoint)
    backend.value = {"binding": copy.deepcopy(binding), "generation": 1, "owner": "old-owner",
                     "expires": 900, "prepared": prep, "checkpoints": {"latest": cp}}
    if completed:
        backend.value["completed"] = {"placeholder": "only admission is tested"}
    return root, cp, prep, payload.read_bytes()

def activate(m):
    r.install_adapter(m)
    environment = m.actual_environment()
    assert environment["augmentation_workers_requested"] == 12
    assert environment["operational_runtime"]["validation_workers_native"] == 6
    return {"module_sha256": r.PROFILES[m.K_AM],
            "input_reference_sha256": m.INPUT_REFERENCE_SHA256,
            "scientific_config": m.fit_config(0),
            "compatible_environment": m.compatible_env(environment)}

def test_exact_scientific_module_migrates_metadata_without_touching_payload(exact_module):
    m, locks, legacy = exact_module
    backend = locks["0"]
    root, cp, prep, original_payload = seed(m, backend, legacy[0])
    old_cp = m.read_record(root, cp)
    bind = activate(m)
    lease = m.FitLease(backend, bind).acquire()
    assert lease.binding == backend.value["binding"] == bind
    assert bind["scientific_config"]["workers"] == 12
    path, record = m.Checkpoints(root, root / "new-attempt", lease).select("latest")
    assert path.read_bytes() == original_payload
    assert record["metadata"]["next_epoch"] == 85
    assert record["operational_transfer"]["original"] == cp
    assert m.read_record(root, cp) == old_cp
    assert m.read_record(root, prep)["binding"] == legacy[0]
    assert m.read_record(root, backend.value["prepared"])["binding"] == bind
    lease.close()
    assert backend.value["owner"] is None
    assert backend.value["expires"] == 0

def test_live_owner_and_cas_race_are_refused(exact_module):
    m, locks, legacy = exact_module
    backend = locks["0"]
    seed(m, backend, legacy[0])
    bind = activate(m)
    backend.value["expires"] = 2000
    before = copy.deepcopy(backend.value)
    with pytest.raises(RuntimeError, match="Live owner"):
        m.FitLease(backend, bind).acquire()
    assert backend.value == before
    backend.value["expires"] = 900
    backend.race = True
    with pytest.raises(RuntimeError, match="CAS collision"):
        m.FitLease(backend, bind).acquire()
    assert backend.value["binding"] == legacy[0]

def test_changed_inputs_science_environment_and_checkpoint_payload_refuse(exact_module):
    m, locks, legacy = exact_module
    backend = locks["0"]
    root, cp, prep, _ = seed(m, backend, legacy[0])
    bind = activate(m)
    for field in ("module_sha256", "input_reference_sha256", "compatible_environment", "scientific_config"):
        bad = copy.deepcopy(legacy[0])
        bad[field] = {"changed": True} if isinstance(bad[field], dict) else "0" * 64
        with pytest.raises(RuntimeError):
            r.migration_allowed(bad, bind, legacy[0])
    lease = m.FitLease(backend, bind).acquire()
    (root / "original.pth").write_bytes(b"altered")
    with pytest.raises(Exception):
        m.Checkpoints(root, root / "attempt", lease).select("latest")
    lease.close()

def test_partial_migration_preserves_old_binding_and_refuses_live_replay(exact_module):
    m, locks, legacy = exact_module
    backend = locks["0"]
    root, cp, prep, original_payload = seed(m, backend, legacy[0])
    bind = activate(m)
    backend.fail_update_after = 1
    with pytest.raises(RuntimeError, match="transport refusal"):
        m.FitLease(backend, bind).acquire()
    assert backend.value["binding"] == legacy[0]
    assert backend.value["checkpoints"]["latest"] == cp
    assert (root / "original.pth").read_bytes() == original_payload
    with pytest.raises(RuntimeError, match="Live owner"):
        m.FitLease(backend, bind).acquire()
    backend.now = 1400
    backend.fail_update_after = None
    lease = m.FitLease(backend, bind).acquire()
    assert backend.value["binding"] == bind
    assert len(list((root / "operational-migrations").iterdir())) == 2
    lease.close()

def test_completed_fold_keeps_original_binding_and_is_not_migrated(exact_module):
    m, locks, legacy = exact_module
    backend = locks["0"]
    root, cp, prep, payload = seed(m, backend, legacy[0], completed=True)
    bind = activate(m)
    assert bind == legacy[0]
    lease = m.FitLease(backend, bind).acquire()
    assert "operational_migration" not in backend.value
    assert backend.value["checkpoints"]["latest"] == cp
    assert not (root / "operational-migrations").exists()
    lease.close()

def test_cpu_and_memory_limits():
    assert r.select_workers({"effective_logical_capacity": 12}, 167 * 2**30) == 12
    assert r.select_workers({"effective_logical_capacity": 32}, 32 * 2**30) == 4
    assert r.select_workers({"effective_logical_capacity": 6.5}, 167 * 2**30) == 6
    with pytest.raises(RuntimeError):
        r.select_workers({"effective_logical_capacity": 1}, 167 * 2**30)


def test_committed_migration_with_lost_response_resumes_after_expiry(exact_module):
    m, locks, legacy = exact_module
    backend = locks["0"]
    root, cp, prep, original_payload = seed(m, backend, legacy[0])
    bind = activate(m)
    original_replace = backend.replace
    def ambiguous(etag, value):
        original_replace(etag, value)
        if value.get("binding") == bind:
            raise RuntimeError("response lost after remote commit")
    backend.replace = ambiguous
    with pytest.raises(RuntimeError, match="response lost"):
        m.FitLease(backend, bind).acquire()
    assert backend.value["binding"] == bind
    with pytest.raises(Exception):
        m.FitLease(backend, bind).acquire()
    backend.now = 1400
    backend.replace = original_replace
    lease = m.FitLease(backend, bind).acquire()
    path, record = m.Checkpoints(root, root / "next-attempt", lease).select("latest")
    assert path.read_bytes() == original_payload
    assert len(list((root / "operational-migrations").iterdir())) == 1
    lease.close()

def test_watchdog_failure_saves_private_report_then_requests_unassignment(exact_module, monkeypatch):
    import sys
    from types import SimpleNamespace
    from tools import colab_epoch_watchdog as watchdog
    m, _, _ = exact_module
    steps = []
    from tools import colab_private_output as folder
    monkeypatch.setitem(sys.modules, "colab_private_output", folder)
    monkeypatch.setattr(folder, "private_root", lambda module: steps.append("owner-check"))
    def failed(argv, token, emit):
        steps.append("supervised-stop")
        emit("last training log")
        raise watchdog.WatchdogError("STALL")
    monkeypatch.setattr(watchdog, "supervise", failed)
    monkeypatch.setitem(sys.modules, "colab_epoch_watchdog", watchdog)
    def unassign():
        reports = list(Path(m.RESULTS_ROOT).glob("watchdog-failure-*.json"))
        assert len(reports) == 1
        assert json.loads(reports[0].read_bytes())["error"] == "STALL"
        steps.append("runtime-unassign")
    monkeypatch.setitem(sys.modules, "google.colab", SimpleNamespace(runtime=SimpleNamespace(unassign=unassign)))
    with pytest.raises(watchdog.WatchdogError, match="STALL"):
        r.run_notebook(m, m.K_AM, (0, 1, 2, 3, 4))
    assert steps == ["owner-check", "supervised-stop", "runtime-unassign"]
