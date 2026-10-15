"""Bounded lease retries and four reusable checkpoint slots. No historical deletion."""
from __future__ import annotations
import errno
import hashlib
import json
import os
from pathlib import Path
import threading
import time
import uuid

SCHEMA = "colab-storage-reliability/v1"
MAX_FAILURES = 6

class DriveStorageFull(RuntimeError):
    pass

def error_kind(exc):
    """Classify without logging request URLs, credentials or raw response bodies."""
    response = getattr(exc, "response", None)
    status = getattr(response, "status_code", None)
    if status is None:
        status = getattr(getattr(exc, "resp", None), "status", None)
    texts = [str(exc)]
    if response is not None:
        try:
            texts.append(json.dumps(response.json()))
        except (ValueError, TypeError, AttributeError):
            pass
    content = getattr(exc, "content", b"")
    if isinstance(content, bytes):
        texts.append(content.decode("utf-8", errors="replace"))
    if getattr(exc, "errno", None) == errno.ENOSPC or any(
        "storageQuotaExceeded" in s for s in texts
    ):
        return "storage_full", status
    if status == 429 or (isinstance(status, int) and 500 <= status < 600):
        return "transient", status
    # Explicit transport exceptions only; never retry hash/privacy/CAS/lease errors.
    if isinstance(exc, (TimeoutError, ConnectionError)):
        return "transient", status
    try:
        import requests
        if isinstance(exc, (requests.exceptions.Timeout, requests.exceptions.ConnectionError)):
            return "transient", status
    except ImportError:
        pass
    return "permanent", status

def full_error():
    return DriveStorageFull(
        "Drive storage quota exceeded: no automatic retry. Existing checkpoints are preserved. "
        "Partho must free Drive space before a new run."
    )

def renew_with_retry(lease, operation, *, clock=time.monotonic, emit=print):
    """Retry the whole guarded read/CAS transaction, never replay a stale PATCH."""
    for failure in range(1, MAX_FAILURES + 1):
        try:
            return operation()
        except Exception as exc:
            kind, status = error_kind(exc)
            if kind == "storage_full":
                raise full_error() from exc
            if kind != "transient":
                raise
            remaining = lease.deadline - clock()
            delay = min(2 ** (failure - 1), 16)
            terminal = (failure == MAX_FAILURES or remaining <= delay
                        or lease.stop.is_set())
            emit("LEASE_RETRY " + json.dumps({
                "consecutive_failure": failure, "maximum": MAX_FAILURES,
                "http_status": status, "cause": type(exc).__name__,
                "delay_seconds": 0 if terminal else delay,
                "safe_deadline_remaining_seconds": max(0, round(remaining, 3)),
                "terminal": terminal,
            }), flush=True)
            if terminal:
                raise
            if lease.stop.wait(delay):
                raise

def validate_native_checkpoint(path, meta):
    """Read back the serialized payload before it can become a lease reference."""
    import torch
    blob = torch.load(str(path), map_location="cpu", weights_only=False)
    if (not isinstance(blob, dict)
        or blob.get("current_epoch") != meta["next_epoch"]
        or not isinstance(blob.get("network_weights"), dict)
        or not blob["network_weights"]
        or not isinstance(blob.get("optimizer_state"), dict)
        or not isinstance(blob["optimizer_state"].get("state"), dict)
        or not isinstance(blob["optimizer_state"].get("param_groups"), list)
        or not isinstance(blob.get("delivery_state"), dict)):
        raise RuntimeError("CHECKPOINT_PAYLOAD_STRUCTURE")
    if meta["next_epoch"] > 0 and not blob["optimizer_state"]["state"]:
        raise RuntimeError("CHECKPOINT_OPTIMIZER_STATE_MISSING")
    delivery = blob["delivery_state"]
    if not all(k in delivery for k in ("python_rng", "numpy_rng", "torch_rng",
                                      "cuda_rng", "measurements")):
        raise RuntimeError("CHECKPOINT_DELIVERY_STATE_MISSING")
    if not all(torch.is_tensor(v) for v in blob["network_weights"].values()):
        raise RuntimeError("CHECKPOINT_WEIGHTS_INVALID")

def install(m, *, validator=validate_native_checkpoint):
    """Retain original bindings, guard/select and scientific behavior."""
    original_lease, original_checkpoints = m.FitLease, m.Checkpoints
    repair_sha = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()

    class ReliableLease(original_lease):
        def _update(self, changes=None, release=False):
            # Original method still rereads owner/generation/expiry and uses If-Match.
            return renew_with_retry(self, lambda: super(ReliableLease, self)._update(
                changes, release=release))
        def guard(self):
            if isinstance(self.error, DriveStorageFull) or (self.error and error_kind(self.error)[0] == "storage_full"):
                raise full_error() from self.error
            return super().guard()

    class BoundedCheckpoints(original_checkpoints):
        def __init__(self, root, att, lease):
            super().__init__(root, att, lease)
            m.need(self.attempt.parent == self.root / "attempts"
                   and self.attempt.name == lease.owner, "Checkpoint attempt/owner mismatch")
            self._publish_lock = threading.Lock()
            self._created = set()
            self.pool = self.attempt / "checkpoint-pool"
            m.checked_path(str(self.pool), missing=True)
            # Do not reuse any files that existed before this instance/attempt.
            self.pool.mkdir(mode=0o700, exist_ok=False)
            (self.pool / "receipts").mkdir(mode=0o700)
            self.slots = [self.pool / ("slot" + str(i) + ".pth") for i in range(4)]
            m.save_record(self.root, (self.pool / "policy.json").relative_to(self.root).as_posix(),
                          {"schema": SCHEMA, "repair_sha256": repair_sha,
                           "slots": 4, "historical_files_modified": False,
                           "policy": "Only an unreferenced current-attempt slot may be overwritten; no deletion."})

        def _protected(self):
            m.need(not self.lease.state.get("completed"), "Completed fit is immutable")
            m.need(not (self.attempt / "metrics.json").exists()
                   and not (self.attempt / "run-summary.json").exists(),
                   "Result publication has started; checkpoint pool is sealed")
            result = set()
            for key, side in self.lease.state.get("checkpoints", {}).items():
                m.need(key in ("latest", "best", "final"), "Unknown checkpoint role")
                rec = m.read_record(self.root, side)
                m.need(rec["binding"] == self.lease.binding, "Checkpoint binding mismatch")
                result.add(m.rooted(self.root, rec["path"]))
            return result

        def publish(self, key, write, meta):
            with self._publish_lock:
                self.lease.guard()
                m.need(key in ("latest", "best", "final"), "Checkpoint key")
                m.need(meta["total_epochs"] == m.EPOCHS
                       and type(meta["next_epoch"]) is int
                       and 0 <= meta["next_epoch"] <= m.EPOCHS, "Checkpoint epoch mismatch")
                with self.lease.mutex:
                    self.lease._update()
                    protected = self._protected()
                    free = [p for p in self.slots if p not in protected]
                    m.need(bool(free), "No unreferenced checkpoint slot")
                    p = free[0]
                    m.checked_path(str(p), missing=True)
                    if p.exists():
                        m.need(p in self._created, "Preexisting checkpoint must not be overwritten")
                    else:
                        with p.open("xb"):
                            pass
                        self._created.add(p)
                # Heartbeat can run during a slow write. A lost lease can never commit it.
                start = time.perf_counter()
                try:
                    write(p)
                    with p.open("rb") as stream:
                        os.fsync(stream.fileno())
                    info = m.file_info(p)
                    m.need(info["bytes"] > 0, "Empty checkpoint")
                    validator(p, meta)
                    m.need(m.file_info(p) == info, "Checkpoint readback failed")
                except Exception as exc:
                    if error_kind(exc)[0] == "storage_full":
                        raise full_error() from exc
                    raise
                rec = dict(info, path=p.relative_to(self.root).as_posix(), metadata=meta,
                           binding=self.lease.binding, owner=self.lease.owner,
                           generation=self.lease.state["generation"],
                           write_seconds=time.perf_counter()-start,
                           storage_repair={"schema": SCHEMA, "source_sha256": repair_sha,
                                           "reusable_slot": p.name})
                side = m.save_record(self.root,
                    (self.pool/"receipts"/(uuid.uuid4().hex+".json")).relative_to(self.root).as_posix(), rec)
                with self.lease.mutex:
                    self.lease.guard()
                    self.lease._update()
                    m.need(p not in self._protected(), "Checkpoint slot became referenced")
                    checkpoints = dict(self.lease.state["checkpoints"])
                    checkpoints[key] = side
                    self.lease.publish("checkpoints", checkpoints)
                print("CHECKPOINT_COMMITTED " + json.dumps({
                    "role": key, "next_epoch": meta["next_epoch"], "bytes": info["bytes"],
                    "pool_files": sum(q.is_file() for q in self.slots), "slot_limit": 4,
                    "historical_files_modified": False,
                }), flush=True)
                return rec

    m.FitLease, m.Checkpoints = ReliableLease, BoundedCheckpoints
    return {"schema": SCHEMA, "source_sha256": repair_sha}
