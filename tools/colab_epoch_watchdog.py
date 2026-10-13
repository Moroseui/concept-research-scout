"""Bounded process supervision for reviewed Colab training; no scientific code."""
from __future__ import annotations
import collections
import json
import math
import os
import selectors
import signal
import statistics
import subprocess
import sys
import time

MARKER = "SCOUT_PROGRESS "
class WatchdogError(RuntimeError):
    pass

def positive(value):
    return type(value) in (int, float) and math.isfinite(value) and value > 0

class Deadline:
    """Only completed epochs refresh the training deadline."""
    def __init__(self, token, now, *, startup=900.0, phase_limit=1800.0, floor=120.0):
        if not all(positive(v) for v in (startup, phase_limit, floor)):
            raise ValueError("Invalid watchdog limits")
        self.token = token
        self.startup, self.phase_limit, self.floor = startup, phase_limit, floor
        self.phase = "startup"
        self.last = now
        self.limit = startup
        self.history = []
        self.next_epoch = None
        self.training_started = False
        self.fold = -1

    def accept(self, event, now):
        if not isinstance(event, dict) or event.get("token") != self.token:
            raise WatchdogError("Invalid progress identity")
        kind = event.get("kind")
        if kind == "fold":
            if set(event) != {"token", "kind", "fold"} or type(event["fold"]) is not int or event["fold"] != self.fold + 1 or event["fold"] > 4:
                raise WatchdogError("Noncontiguous fold progress")
            self.fold = event["fold"]
            self.phase, self.last, self.limit = "between_folds", now, self.phase_limit
            self.next_epoch = None
            return
        if kind == "phase":
            if set(event) != {"token", "kind", "phase"}:
                raise WatchdogError("Invalid phase event")
            phase = event["phase"]
            if phase not in {"preparation", "validation", "scoring", "between_folds", "cleanup"}:
                raise WatchdogError("Unknown bounded phase")
            if phase == self.phase:
                raise WatchdogError("Repeated phase cannot renew deadline")
            self.phase, self.last, self.limit = phase, now, self.phase_limit
            self.next_epoch = None
            return
        if kind == "training":
            if set(event) != {"token", "kind", "next_epoch", "history"}:
                raise WatchdogError("Invalid training event")
            epoch, history = event["next_epoch"], event["history"]
            if (self.phase == "training" or type(epoch) is not int or not 0 <= epoch < 250
                or not isinstance(history, list) or len(history) > 10
                or not all(positive(v) and v <= 3600 for v in history)):
                raise WatchdogError("Invalid training start/history")
            self.phase, self.last, self.next_epoch = "training", now, epoch
            self.history = list(history)
            self.limit = min(self.phase_limit, max(self.startup, self.steady_limit()))
            self.training_started = True
            return
        if kind == "epoch":
            if set(event) != {"token", "kind", "epoch", "seconds"}:
                raise WatchdogError("Invalid completed-epoch event")
            if (self.phase != "training" or type(event["epoch"]) is not int
                or event["epoch"] != self.next_epoch
                or not positive(event["seconds"]) or event["seconds"] > 3600):
                raise WatchdogError("Noncontiguous or invalid completed epoch")
            self.history = (self.history + [event["seconds"]])[-10:]
            self.next_epoch += 1
            self.last, self.limit = now, self.steady_limit()
            return
        raise WatchdogError("Unknown progress event")

    def steady_limit(self):
        return min(self.phase_limit, max(self.floor, 3 * statistics.median(self.history))) if self.history else self.startup

    def expired(self, now):
        return now - self.last >= self.limit

def kill_group(process, grace=5.0):
    """Bounded TERM then KILL, including same-session augmentation descendants."""
    try:
        os.killpg(process.pid, signal.SIGTERM)
    except ProcessLookupError:
        pass
    end = time.monotonic() + grace
    while time.monotonic() < end:
        try:
            os.killpg(process.pid, 0)
        except ProcessLookupError:
            break
        time.sleep(0.05)
    try:
        os.killpg(process.pid, signal.SIGKILL)
    except ProcessLookupError:
        pass
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired as exc:
        raise WatchdogError("Child termination could not be confirmed") from exc

def supervise(argv, token, *, env=None, emit=print, startup=900.0,
              phase_limit=1800.0, floor=120.0, terminate_grace=5.0):
    if os.name != "posix" or not isinstance(argv, list) or not argv:
        raise ValueError("POSIX argv required")
    child_env = dict(os.environ if env is None else env, SCOUT_WATCHDOG_TOKEN=token)
    process = subprocess.Popen(argv, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                               env=child_env, start_new_session=True, bufsize=0)
    deadline = Deadline(token, time.monotonic(), startup=startup,
                        phase_limit=phase_limit, floor=floor)
    tail = collections.deque(maxlen=80)
    selector = selectors.DefaultSelector()
    selector.register(process.stdout, selectors.EVENT_READ)
    pending = b""
    failure = None
    try:
        while True:
            for key, _ in selector.select(timeout=0.1):
                chunk = os.read(key.fd, 65536)
                if not chunk:
                    selector.unregister(key.fileobj)
                    continue
                pending += chunk
                if len(pending) > 1024 * 1024:
                    raise WatchdogError("Child output line exceeds bound")
                while b"\n" in pending:
                    raw, pending = pending.split(b"\n", 1)
                    line = raw.decode("utf-8", errors="replace")
                    tail.append(line[-4096:])
                    emit(line)
                    if line.startswith(MARKER):
                        deadline.accept(json.loads(line[len(MARKER):]), time.monotonic())
            code = process.poll()
            if code is not None and not selector.get_map():
                if pending:
                    line = pending.decode("utf-8", errors="replace")
                    tail.append(line[-4096:])
                    emit(line)
                if code:
                    raise WatchdogError("Training child exited with code " + str(code))
                return {"status": "CHILD_EXIT_0", "tail": list(tail)}
            if deadline.expired(time.monotonic()):
                raise WatchdogError("STALL: no completed progress in " + str(round(deadline.limit, 1))
                                    + " seconds during " + deadline.phase)
    except BaseException as exc:
        failure = exc
        kill_group(process, grace=terminate_grace)
        emit("WATCHDOG_FAILURE: " + str(exc))
        emit("LAST_LOG_LINES:\n" + "\n".join(tail))
        raise
    finally:
        selector.close()
        process.stdout.close()
        if failure is None:
            # A successful direct child must not leave resource-consuming descendants.
            kill_group(process, grace=terminate_grace)
