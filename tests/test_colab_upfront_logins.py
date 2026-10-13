import copy
import io
import json
import os
import sys
import types
from pathlib import Path
from contextlib import redirect_stdout
import pytest
from tools.colab_upfront_logins import first_cell, frontload, READY, AUTH, SNAPSHOTS

@pytest.mark.parametrize("profile", list(SNAPSHOTS))
def test_all_interactions_finish_before_ready(profile, monkeypatch, tmp_path):
    events = []
    class Drive:
        def mount(self, path, timeout_ms):
            assert path == "/content/drive" and timeout_ms == 60000
            events.append("mount")
    class Auth:
        def authenticate_user(self):
            events.append("auth")
    class Message:
        def blocking_request(self, name, timeout_sec):
            assert name == "get_ipynb" and timeout_sec == 30
            events.append("snapshot")
            return {"ipynb": {"cells": [{"cell_type": "code", "outputs": ["old"], "execution_count": 1}]}}
    colab = types.ModuleType("google.colab")
    colab.drive, colab.auth, colab._message = Drive(), Auth(), Message()
    google = types.ModuleType("google")
    google.colab = colab
    monkeypatch.setitem(sys.modules, "google", google)
    monkeypatch.setitem(sys.modules, "google.colab", colab)
    import pathlib
    RealPath = pathlib.Path
    monkeypatch.setattr(pathlib, "Path", lambda path: RealPath(tmp_path / "snapshot.json")
                        if path == "/content/delivery-executed.ipynb" else RealPath(path))
    out = io.StringIO()
    with redirect_stdout(out):
        exec("".join(first_cell(profile)["source"]), {})
    assert events == ["mount", "auth", "snapshot"]
    assert out.getvalue().rstrip().endswith(READY)
    snapshot = json.loads((tmp_path / "snapshot.json").read_bytes())
    if profile == "A1_L":
        assert snapshot["cells"][0]["outputs"] == []
        assert snapshot["cells"][0]["execution_count"] is None

def test_login_failure_never_prints_ready_or_requests_later_snapshot(monkeypatch):
    calls = []
    colab = types.ModuleType("google.colab")
    def mount(*a, **kw):
        calls.append("mount")
    def fail():
        raise TimeoutError("provider unavailable")
    colab.drive = types.SimpleNamespace(mount=mount)
    colab.auth = types.SimpleNamespace(authenticate_user=fail)
    colab._message = types.SimpleNamespace(blocking_request=lambda *a, **kw: calls.append("snapshot"))
    google = types.ModuleType("google"); google.colab = colab
    monkeypatch.setitem(sys.modules, "google", google)
    monkeypatch.setitem(sys.modules, "google.colab", colab)
    import signal
    old = signal.getsignal(signal.SIGALRM)
    out = io.StringIO()
    with redirect_stdout(out), pytest.raises(TimeoutError):
        exec("".join(first_cell("A1_pnormct")["source"]), {})
    assert READY not in out.getvalue() and calls == ["mount"]
    assert signal.getitimer(signal.ITIMER_REAL) == (0.0, 0.0)
    assert signal.getsignal(signal.SIGALRM) == old

@pytest.mark.parametrize("profile", list(SNAPSHOTS))
def test_frontload_refuses_unknown_later_prompts(profile):
    nb = {"cells": [{"cell_type": "code", "source": [AUTH + SNAPSHOTS[profile] +
           "auth.authenticate_user()\n"]}]}
    with pytest.raises(ValueError, match="Unexpected later"):
        frontload(nb, 0, profile)

def test_l_exact_delivered_preparation_only_is_unchanged_except_frontloading():
    root = Path(os.environ["COLAB_EXACT_MODULE_FIXTURES"])
    raw = (root / "13B_A1_L_prepare_PRIVATE.ipynb").read_bytes()
    original = json.loads(raw)
    result = frontload(original, len(original["cells"])-1, "A1_L")
    assert result["cells"][2] == original["cells"][1]  # exact module materializer
    assert "'--prepare-only'" in "".join(result["cells"][-1]["source"])
    for cell in result["cells"][2:]:
        source = "".join(cell["source"])
        # Encoded exact module is data, not newly invoked browser code.
        assert "drive.mount(" not in source
        assert "auth.authenticate_user(" not in source
        assert "_message.blocking_request(" not in source
