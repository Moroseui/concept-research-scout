import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import time
import pytest
from tools.colab_epoch_watchdog import Deadline, WatchdogError, supervise

def event(kind, **kw):
    return dict(token="test-token", kind=kind, **kw)

def test_resume_uses_history_then_only_completed_epochs_refresh():
    d = Deadline("test-token", 0)
    d.accept(event("training", next_epoch=85, history=[194] * 10), 1)
    assert d.limit == 900
    d.accept(event("epoch", epoch=85, seconds=190), 101)
    assert d.limit == 582
    assert not d.expired(682)
    assert d.expired(683)
    with pytest.raises(WatchdogError):
        d.accept(event("epoch", epoch=85, seconds=190), 200)
    assert d.last == 101

def test_unknown_identity_phase_reset_and_invalid_history_refused():
    d = Deadline("test-token", 0)
    with pytest.raises(WatchdogError):
        d.accept(dict(token="other", kind="phase", phase="preparation"), 1)
    d.accept(event("phase", phase="preparation"), 1)
    with pytest.raises(WatchdogError):
        d.accept(event("phase", phase="preparation"), 100)
    assert d.last == 1
    with pytest.raises(WatchdogError):
        d.accept(event("training", next_epoch=85, history=[float("nan")]), 200)
    assert d.last == 1

def test_real_child_and_grandchild_stop_even_with_heartbeat_output(tmp_path):
    beat = tmp_path / "heartbeats"
    pidfile = tmp_path / "grandchild"
    grand = "import time;from pathlib import Path;p=Path(" + repr(str(beat)) + ");\nwhile True:\n p.write_text(str(time.monotonic()));time.sleep(.03)"
    child = (
        "import subprocess,sys,time;from pathlib import Path;"
        "p=subprocess.Popen([sys.executable,'-u','-c'," + repr(grand) + "]);"
        "Path(" + repr(str(pidfile)) + ").write_text(str(p.pid));"
        "\nwhile True:\n print('heartbeat; not epoch progress',flush=True);time.sleep(.03)"
    )
    output = []
    start = time.monotonic()
    with pytest.raises(WatchdogError, match="STALL"):
        supervise([sys.executable, "-u", "-c", child], "test-token",
                  startup=.4, phase_limit=.4, floor=.1,
                  terminate_grace=.1, emit=output.append)
    assert time.monotonic() - start < 4
    assert beat.exists() and pidfile.exists()
    saved = beat.read_bytes()
    time.sleep(.15)
    assert beat.read_bytes() == saved
    stat = Path("/proc") / pidfile.read_text() / "stat"
    assert not stat.exists() or stat.read_text().split()[2] == "Z"
    assert any("LAST_LOG_LINES" in line for line in output)

def test_parent_survives_child_ignoring_sigterm():
    child = "import signal,time;signal.signal(signal.SIGTERM,signal.SIG_IGN);time.sleep(60)"
    start = time.monotonic()
    with pytest.raises(WatchdogError, match="STALL"):
        supervise([sys.executable, "-u", "-c", child], "test-token",
                  startup=.3, phase_limit=.3, floor=.1,
                  terminate_grace=.1, emit=lambda _: None)
    assert time.monotonic() - start < 4

def test_completed_epoch_allows_progress_and_output_failure_is_visible():
    lines = [
        event("training", next_epoch=85, history=[.1]),
        event("epoch", epoch=85, seconds=.1),
        event("epoch", epoch=86, seconds=.1),
    ]
    child = "import time\n"
    for line in lines:
        child += "print(" + repr("SCOUT_PROGRESS " + json.dumps(line)) + ",flush=True);time.sleep(.12)\n"
    result = supervise([sys.executable, "-u", "-c", child], "test-token",
                       startup=.4, phase_limit=.4, floor=.2,
                       terminate_grace=.1, emit=lambda _: None)
    assert result["status"] == "CHILD_EXIT_0"
    out = []
    with pytest.raises(WatchdogError, match="code 7"):
        supervise([sys.executable, "-u", "-c", "import sys;print('actual subprocess error',flush=True);sys.exit(7)"],
                  "test-token", emit=out.append, terminate_grace=.1)
    assert any("actual subprocess error" in line for line in out)


def test_completed_fold_skip_does_not_reopen_an_unbounded_phase():
    d = Deadline("test-token", 0)
    d.accept(event("phase", phase="preparation"), 1)
    d.accept(event("fold", fold=0), 2)
    d.accept(event("fold", fold=1), 3)
    with pytest.raises(WatchdogError):
        d.accept(event("fold", fold=1), 4)
    with pytest.raises(WatchdogError):
        d.accept(event("fold", fold=3), 4)
    assert d.last == 3
