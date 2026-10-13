"""Operational adapter for two exact reviewed notebooks. Scientific files stay byte-identical."""
from __future__ import annotations
import copy
import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path
import sys
import threading
import time
import uuid
from collections import deque

PROFILES = {
    "A1_pnormct": "33153177657c1f2a3383bcd50fffb393a571514c3363f7ef2c24f131d48251f2",
    "A1_pnorm_v2": "59363a58e9bda0a6d4a8b401a9f4d979c7d5c6305c3d7c757d17f0fe7d9cd5a7",
}
KEY = "operational_runtime"
SCHEMA = "colab-workers-watchdog-resume/v1"

def require(ok, message):
    if not ok:
        raise RuntimeError(message)

def sha(raw):
    return hashlib.sha256(raw).hexdigest()

def encoded(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()

def policy_identity():
    here = Path(__file__)
    return sha(encoded({"runtime": sha(here.read_bytes()),
                        "watchdog": sha(here.with_name("colab_epoch_watchdog.py").read_bytes()),
                        "private_output": sha(here.with_name("colab_private_output.py").read_bytes())}))

def select_workers(cpu, ram_bytes):
    capacity = cpu["effective_logical_capacity"]
    require(type(capacity) in (int, float) and math.isfinite(capacity) and capacity >= 2,
            "Insufficient effective CPU capacity")
    require(type(ram_bytes) is int and ram_bytes >= 16 * 2**30, "Insufficient RAM")
    # Reserve half the observed RAM at a conservative 4 GiB per train worker.
    count = min(32, math.floor(capacity), ram_bytes // (8 * 2**30))
    require(count >= 2, "Insufficient worker memory allowance")
    return int(count)

def operational_config(original, workers, identity):
    value = copy.deepcopy(original)
    require(value["workers"] == 2 and KEY not in value, "Unexpected original resource profile")
    value["workers"] = workers
    value[KEY] = {"schema": SCHEMA, "source_sha256": identity, "workers": workers}
    return value

def migration_allowed(old, new, legacy):
    """Only an exact original binding may cross to this exact operational binding."""
    require(old == legacy, "Unrecognized old checkpoint binding")
    require(set(new) == set(legacy) == {
        "module_sha256", "input_reference_sha256", "scientific_config", "compatible_environment"},
        "Binding fields changed")
    for key in ("module_sha256", "input_reference_sha256", "compatible_environment"):
        require(new[key] == legacy[key], "Input, scientific module or environment changed")
    cfg = new["scientific_config"]
    op = cfg.get(KEY, {})
    require(set(op) == {"schema", "source_sha256", "workers"} and op["schema"] == SCHEMA,
            "Unknown operational migration")
    require(isinstance(op["source_sha256"], str) and len(op["source_sha256"]) == 64
            and all(c in "0123456789abcdef" for c in op["source_sha256"]),
            "Invalid operational source identity")
    require(type(op["workers"]) is int and 2 <= op["workers"] <= 32
            and cfg == operational_config(legacy["scientific_config"], op["workers"], op["source_sha256"]),
            "Scientific choices changed")

def progress(kind, **values):
    token = os.environ["SCOUT_WATCHDOG_TOKEN"]
    print("SCOUT_PROGRESS " + json.dumps(dict(token=token, kind=kind, **values),
                                         allow_nan=False), flush=True)

def install_adapter(m):
    """Wrap only resources, progress reporting and explicit metadata lineage."""
    require(m.K_AM in PROFILES and sha(Path(m.__file__).read_bytes()) == PROFILES[m.K_AM],
            "Unknown scientific module bytes")
    identity = policy_identity()
    frozen_configs = {fold: copy.deepcopy(m.fit_config(fold)) for fold in range(5)}
    original_config = lambda fold: copy.deepcopy(frozen_configs[fold])
    original_environment = m.actual_environment
    original_paths, original_lease = m._native_paths, m.FitLease
    original_factory, original_prepare, original_fold = m._trainer_class, m.prepare_arm, m.execute_fold
    original_score = m._score_native
    cpu = m.cpu_capacity()
    ram = os.sysconf("SC_PAGE_SIZE") * os.sysconf("SC_PHYS_PAGES")
    workers = select_workers(cpu, ram)
    completed_bindings = {}
    legacy_bindings = {}
    selected = False

    def environment():
        nonlocal workers, selected
        env = original_environment()
        require(not selected, "Environment admission repeated")
        # Read metadata only. Every acquisition still rereads and CAS-checks ownership.
        ref = m.load_input_reference()
        compat = m.compatible_env(env)
        states = {}
        for fold in range(5):
            _, _, state = m.DriveCAS(ref["fit_lock_ids"][str(fold)]).read()
            states[fold] = state
            legacy = {"module_sha256": PROFILES[m.K_AM],
                      "input_reference_sha256": m.INPUT_REFERENCE_SHA256,
                      "scientific_config": original_config(fold),
                      "compatible_environment": compat}
            legacy_bindings[fold] = legacy
            if state.get("completed"):
                binding = state.get("binding")
                if binding != legacy:
                    migration_allowed(legacy, binding, legacy)
                    op = binding["scientific_config"][KEY]
                    require(op["source_sha256"] == identity, "Completed fit uses another operational release")
                completed_bindings[fold] = copy.deepcopy(binding)
        existing = {s["binding"]["scientific_config"][KEY]["workers"]
                    for s in states.values() if s and not s.get("completed")
                    and KEY in s.get("binding", {}).get("scientific_config", {})}
        require(len(existing) <= 1, "Mixed operational worker profiles")
        if existing:
            retained = next(iter(existing))
            require(type(retained) is int and 2 <= retained <= workers,
                    "This runtime cannot support the existing operational worker profile")
            workers = retained
        m.WORKERS = workers
        selected = True
        env = dict(env, augmentation_workers_requested=workers,
                   operational_runtime={"schema": SCHEMA, "source_sha256": identity,
                                        "workers": workers,
                                        "validation_workers_native": max(1, workers // 2),
                                        "prior_fixed_workers": 2,
                                        "bitwise_replay_claimed": False})
        print("Resources: effective CPU=" + str(cpu["effective_logical_capacity"])
              + "; augmentation workers=" + str(workers)
              + "; native validation workers=" + str(max(1, workers // 2)), flush=True)
        print("Measured old profile: about 67-68 hours per five-fold arm at 190-196 s/epoch."
              " New speed is unmeasured; use completed epoch timing, not the old 14-hour estimate.", flush=True)
        return env

    def config(fold):
        require(selected, "Resource profile not admitted")
        if fold in completed_bindings:
            return copy.deepcopy(completed_bindings[fold]["scientific_config"])
        return operational_config(original_config(fold), workers, identity)

    def paths(raw, pre, results):
        original_paths(raw, pre, results)
        os.environ["COLAB_DA_WORKERS"] = str(workers)
        os.environ["nnUNet_n_proc_DA"] = str(workers)

    class MigratingLease(original_lease):
        def acquire(self):
            desired = copy.deepcopy(self.binding)
            fold = desired["scientific_config"]["fold"]
            require(fold in legacy_bindings, "Unknown fold")
            _, now, old = self.backend.read()
            if not old or old.get("binding") == desired:
                return super().acquire()
            migration_allowed(old.get("binding"), desired, legacy_bindings[fold])
            require(not old.get("completed"), "Completed fit must retain original identity")
            require(not old.get("owner") or old.get("expires", 0) <= now,
                    "Live owner: do not migrate or take over")
            original_binding = copy.deepcopy(old["binding"])
            self.binding = original_binding
            # Original acquire performs a fresh read and atomic CAS with all original guards.
            super().acquire()
            root = Path(m.RESULTS_ROOT) / m.K_AM / ("fold" + str(fold))
            m.checked_path(str(root), missing=True)
            root.mkdir(parents=True, exist_ok=True)
            base = "operational-migrations/" + self.owner
            original_state = copy.deepcopy(self.state)
            intent = {"schema": SCHEMA, "old_binding": original_binding,
                      "new_binding": desired, "owner": self.owner,
                      "generation": self.state["generation"], "original_state": original_state,
                      "scientific_choices_unchanged": True, "bitwise_replay_claimed": False}
            intent_ref = m.save_record(root, base + "/intent.json", intent)
            updates = {"binding": desired, "operational_migration": intent_ref}
            # Only metadata is copied, explicitly linked to its original. Checkpoint payloads
            # remain untouched and the original select() still re-hashes before torch.load.
            for key in ("prepared", "preparing"):
                if key in original_state:
                    old_ref = original_state[key]
                    record = m.read_record(root, old_ref)
                    require(record["binding"] == original_binding, "Preprocessing binding mismatch")
                    transferred = dict(record, binding=desired,
                        operational_transfer={"original": old_ref, "intent": intent_ref,
                                              "original_binding": original_binding})
                    updates[key] = m.save_record(root, base + "/" + key + ".json", transferred)
            checkpoints = {}
            for key, old_ref in original_state.get("checkpoints", {}).items():
                require(key in {"latest", "best", "final"}, "Unknown checkpoint role")
                record = m.read_record(root, old_ref)
                require(record["binding"] == original_binding, "Checkpoint original binding mismatch")
                require(record["metadata"]["total_epochs"] == 250
                        and type(record["metadata"]["next_epoch"]) is int
                        and 0 <= record["metadata"]["next_epoch"] <= 250,
                        "Checkpoint epoch metadata mismatch")
                transferred = dict(record, binding=desired,
                    operational_transfer={"original": old_ref, "intent": intent_ref,
                                          "original_binding": original_binding,
                                          "payload_unchanged": True})
                checkpoints[key] = m.save_record(root, base + "/checkpoint-" + key + ".json", transferred)
            updates["checkpoints"] = checkpoints
            self.guard()
            self._update(updates)  # Original owner, generation, expiry and CAS checks.
            self.binding = desired
            self.guard()
            print("Operational migration recorded; checkpoint payloads preserved.", flush=True)
            return self

    def factory():
        cls = original_factory()
        class OperationalTrainer(cls):
            def run_training(self):
                progress("training", next_epoch=int(self.current_epoch),
                         history=[float(r["elapsed"]) for r in self._measurements[-10:]])
                return super().run_training()
            def on_epoch_end(self):
                result = super().on_epoch_end()
                progress("epoch", epoch=int(self._measured_epoch),
                         seconds=float(time.perf_counter() - self._epoch_t))
                return result
            def perform_actual_validation(self, *args, **kwargs):
                progress("phase", phase="validation")
                return super().perform_actual_validation(*args, **kwargs)
        return OperationalTrainer

    def prepare(*args, **kwargs):
        progress("phase", phase="preparation")
        return original_prepare(*args, **kwargs)

    def fold(*args, **kwargs):
        progress("fold", fold=int(args[1] if len(args) > 1 else kwargs["fold"]))
        return original_fold(*args, **kwargs)

    def score(*args, **kwargs):
        progress("phase", phase="scoring")
        return original_score(*args, **kwargs)

    m.fit_config, m.actual_environment = config, environment
    m._native_paths, m.FitLease = paths, MigratingLease
    m._trainer_class, m.prepare_arm, m.execute_fold = factory, prepare, fold
    m._score_native = score
    return {"source_sha256": identity, "scientific_module_sha256": PROFILES[m.K_AM]}

def load_module(path, arm):
    path = Path(path)
    require(arm in PROFILES and sha(path.read_bytes()) == PROFILES[arm], "Scientific source hash mismatch")
    spec = importlib.util.spec_from_file_location("reviewed_scientific_pipeline", path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    require(module.K_AM == arm, "Arm mismatch")
    return module

def child(path, arm):
    m = load_module(path, arm)
    from colab_private_output import install as install_private_root
    install_private_root(m)
    install_adapter(m)
    result = m.main(m.METADATA_ROOT, m.RESULTS_ROOT, {"arm": arm, "folds": (0, 1, 2, 3, 4)})
    require(len(result) == 5, "Incomplete all-fold result")
    name = "pnormct-completed.json" if arm == "A1_pnormct" else "pnorm-v2-completed.json"
    Path("/content", name).write_bytes(m.jsonb(result))
    progress("phase", phase="cleanup")

def run_notebook(m, arm, folds):
    """Called by the notebook kernel; never auto-retries a child."""
    from colab_epoch_watchdog import supervise
    require(arm == m.K_AM and tuple(folds) == (0, 1, 2, 3, 4), "Exact all-fold arm required")
    require(sha(Path(m.__file__).read_bytes()) == PROFILES.get(arm), "Scientific file changed")
    from colab_private_output import install as install_private_root
    install_private_root(m)
    m.private_output_root()  # Mount-only creation; owner-only and uniqueness still required.
    root = Path(m.RESULTS_ROOT)
    m.checked_path(str(root), missing=True)
    root.mkdir(parents=True, exist_ok=True)
    token = uuid.uuid4().hex
    tail = deque(maxlen=80)
    def emit(line):
        tail.append(line[-4096:])
        print(line, flush=True)
    try:
        return supervise([sys.executable, "-u", str(Path(__file__)), "--child", m.__file__, arm],
                         token, emit=emit)
    except BaseException as exc:
        record = {"schema": SCHEMA, "status": "FAILED_NO_AUTOMATIC_RETRY",
                  "arm": arm, "error": str(exc), "tail": list(tail),
                  "scientific_module_sha256": PROFILES[arm],
                  "operational_source_sha256": policy_identity(),
                  "lease_note": "No child renewals after termination; original lease expires naturally.",
                  "ended_unix": time.time()}
        target = root / ("watchdog-failure-" + token + ".json")
        write_error = []
        def persist():
            try:
                with target.open("xb") as stream:
                    stream.write(encoded(record))
                    stream.flush()
                    os.fsync(stream.fileno())
            except BaseException as err:
                write_error.append(str(err))
        thread = threading.Thread(target=persist, daemon=True)
        thread.start()
        thread.join(timeout=15)
        print("Watchdog report: " + str(target) if not thread.is_alive() and not write_error
              else "Report persistence NOT confirmed; preserve this cell's error output.", flush=True)
        print("Training stopped. Requesting Colab runtime unassignment to stop idle resource use."
              " If the runtime remains connected, Disconnect and delete runtime manually.", flush=True)
        def unassign():
            try:
                from google.colab import runtime
                runtime.unassign()
            except BaseException as err:
                print("Runtime unassignment not confirmed: " + str(err), flush=True)
        stopper = threading.Thread(target=unassign, daemon=True)
        stopper.start()
        stopper.join(timeout=15)
        raise

if __name__ == "__main__":
    require(len(sys.argv) == 4 and sys.argv[1] == "--child", "Exact internal child invocation required")
    child(sys.argv[2], sys.argv[3])
