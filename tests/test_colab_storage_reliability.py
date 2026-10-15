import copy
import errno
import importlib.util
import json
import os
from pathlib import Path
import threading
from types import SimpleNamespace
import pytest
from tools import colab_storage_reliability as r

class Clock:
    now = 0
    def __call__(self): return self.now

class Event:
    def __init__(self, clock=None): self.clock = clock; self.stopped = False; self.waits = []
    def wait(self, delay):
        self.waits.append(delay)
        if self.clock: self.clock.now += delay
        return self.stopped
    def is_set(self): return self.stopped
    def set(self): self.stopped = True

class Backend:
    def __init__(self): self.value = {}; self.etag = 0; self.now = 1000; self.failures = []; self.after_commit = False
    def read(self): return str(self.etag), self.now, copy.deepcopy(self.value)
    def replace(self, etag, value):
        if self.failures:
            raise self.failures.pop(0)
        if etag != str(self.etag): raise RuntimeError("CAS collision")
        changed = value.get("checkpoints") != self.value.get("checkpoints")
        self.value = copy.deepcopy(value); self.etag += 1
        if changed and self.after_commit:
            self.after_commit = False
            raise TimeoutError("lost response after commit")

@pytest.fixture(params=["pnormct", "pnorm_v2"])
def fixture(request, tmp_path):
    path = Path(os.environ["COLAB_EXACT_MODULE_FIXTURES"])/(request.param+"-exact-execution.py")
    spec = importlib.util.spec_from_file_location("exact_"+request.param, path)
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    old = m.Checkpoints
    r.install(m, validator=lambda p, meta: json.loads(p.read_text())["epoch"] == meta["next_epoch"])
    backend = Backend(); lease = m.FitLease(backend, {"synthetic": True}).acquire()
    lease.stop = Event()
    root = tmp_path/"fold0"; att = root/"attempts"/lease.owner; att.mkdir(parents=True)
    cp = m.Checkpoints(root, att, lease)
    return m, old, backend, lease, cp

def write(epoch):
    return lambda path: path.write_text(json.dumps({"epoch": epoch}))

def publish(cp, key, epoch):
    return cp.publish(key, write(epoch), {"next_epoch": epoch, "total_epochs": 250})

def test_20_publications_bound_pool_and_real_legacy_select_resumes_latest(fixture):
    m, old, backend, lease, cp = fixture
    inodes = {}
    latest = None
    for i in range(20):
        key = "best" if i % 3 == 0 else "latest"
        rec = publish(cp, key, i)
        if key == "latest": latest = i
        for path in cp.pool.glob("*.pth"):
            if path in inodes: assert path.stat().st_ino == inodes[path]
            inodes[path] = path.stat().st_ino
        assert len(list(cp.attempt.rglob("*.pth"))) <= 4
        assert json.loads(cp.select("latest" if latest is not None else "best")[0].read_text())["epoch"] == (latest if latest is not None else i)
    publish(cp, "final", 250)
    assert len(list(cp.attempt.rglob("*.pth"))) <= 4
    assert cp.select("final")[1]["metadata"]["next_epoch"] == 250
    assert len(list((cp.pool/"receipts").glob("*.json"))) == 21

def test_old_code_grows_on_20_publishes(fixture):
    m, old, backend, lease, _ = fixture
    att = _.root/"legacy-attempt";att.mkdir()
    cp = old(_.root, att, lease)
    for i in range(20): publish(cp,"latest",i)
    assert len(list(att.rglob("*.pth"))) == 20

def test_historical_files_remain_unchanged(fixture):
    m, old, backend, lease, cp = fixture
    att = cp.root/"historical-attempt";att.mkdir()
    previous = old(cp.root, att, lease)
    prior = publish(previous,"latest",80)
    raw = (cp.root/prior["path"]).read_bytes()
    for i in range(20):publish(cp,"latest",85+i)
    assert (cp.root/prior["path"]).read_bytes() == raw
    assert len(list(att.rglob("*.pth"))) == 1

def test_crash_during_write_keeps_prior_reference_and_fresh_attempt_can_resume(fixture):
    m, old, backend, lease, cp = fixture
    first = publish(cp, "latest", 85)
    saved = copy.deepcopy(backend.value["checkpoints"])
    def partial(path):
        path.write_bytes(b"partial")
        raise TimeoutError("synthetic crash during write")
    with pytest.raises(TimeoutError): cp.publish("latest",partial,{"next_epoch":90,"total_epochs":250})
    assert backend.value["checkpoints"] == saved
    assert cp.select("latest")[1] == first
    backend.now += 400
    nextlease = m.FitLease(backend, {"synthetic":True}).acquire()
    nextlease.stop = Event()
    att = cp.root/"attempts"/nextlease.owner;att.mkdir()
    fresh = m.Checkpoints(cp.root,att,nextlease)
    assert fresh.select("latest")[1] == first

def test_crash_after_verified_write_before_cas_keeps_old_reference(fixture):
    m, old, backend, lease, cp = fixture
    first=publish(cp,"latest",85);saved=copy.deepcopy(backend.value["checkpoints"])
    original=lease.publish
    lease.publish=lambda *a,**k: (_ for _ in ()).throw(RuntimeError("crash before pointer publish"))
    with pytest.raises(RuntimeError,match="crash before"):
        publish(cp,"latest",90)
    lease.publish=original
    assert backend.value["checkpoints"] == saved
    assert cp.select("latest")[1] == first

def test_ambiguous_successful_cas_is_reconciled_not_replayed_with_stale_etag(fixture):
    m, old, backend, lease, cp = fixture
    publish(cp,"latest",85);backend.after_commit=True
    rec=publish(cp,"latest",90)
    assert cp.select("latest")[1] == rec
    assert len(lease.stop.waits)==1

def test_lost_lease_and_completed_results_refuse_before_overwrite(fixture):
    m,old,backend,lease,cp=fixture
    publish(cp,"latest",85)
    before={p:p.read_bytes()for p in cp.pool.glob("*.pth")}
    backend.value["owner"]="other"
    with pytest.raises(Exception,match="Lease (lost|expired)"):publish(cp,"latest",90)
    assert {p:p.read_bytes()for p in cp.pool.glob("*.pth")}==before
    backend.value["owner"]=lease.owner
    backend.value["completed"]={"synthetic":True}
    with pytest.raises(Exception,match="immutable"):publish(cp,"latest",90)
    assert {p:p.read_bytes()for p in cp.pool.glob("*.pth")}==before

def test_no_reuse_of_existing_attempt_pool(fixture):
    m,_,_,lease,cp=fixture
    with pytest.raises(FileExistsError):m.Checkpoints(cp.root,cp.attempt,lease)

def test_quota_write_preserves_current_latest_and_says_full(fixture):
    m,_,_,_,cp=fixture
    first=publish(cp,"latest",85)
    def full(path):raise OSError(errno.ENOSPC,"No space")
    with pytest.raises(r.DriveStorageFull,match="quota exceeded"):
        cp.publish("latest",full,{"next_epoch":90,"total_epochs":250})
    assert cp.select("latest")[1] == first

class HTTP(Exception):
    def __init__(self,status,reason="backendError"):
        self.response=SimpleNamespace(status_code=status,json=lambda:{"error":{"errors":[{"reason":reason}]}})
        super().__init__("redacted HTTP failure")

@pytest.mark.parametrize("error",[TimeoutError(),HTTP(429),HTTP(500),HTTP(502),HTTP(503)])
def test_transient_retry_logs_and_recovers(error):
    clock=Clock();lease=SimpleNamespace(deadline=240,stop=Event(clock));calls=[];logs=[]
    def op():
        calls.append(1)
        if len(calls)<3:raise error
        return "ok"
    assert r.renew_with_retry(lease,op,clock=clock,emit=lambda line,**_:logs.append(json.loads(line.split(" ",1)[1])))=="ok"
    assert lease.stop.waits==[1,2] and len(logs)==2
    assert all(not x["terminal"] for x in logs)

def test_six_failures_stop_and_log_every_failure():
    clock=Clock();lease=SimpleNamespace(deadline=240,stop=Event(clock));logs=[]
    def op():raise TimeoutError()
    with pytest.raises(TimeoutError):r.renew_with_retry(lease,op,clock=clock,emit=lambda s,**k:logs.append(s))
    assert len(logs)==6 and lease.stop.waits==[1,2,4,8,16]

def test_no_retry_past_safe_lease_deadline():
    clock=Clock();lease=SimpleNamespace(deadline=2,stop=Event(clock));logs=[]
    def op():raise TimeoutError()
    with pytest.raises(TimeoutError):r.renew_with_retry(lease,op,clock=clock,emit=lambda s,**k:logs.append(s))
    assert lease.stop.waits==[1] and len(logs)==2

@pytest.mark.parametrize("error",[HTTP(401),HTTP(403),HTTP(412),ValueError("hash mismatch"),RuntimeError("Lease lost")])
def test_permanent_guard_errors_never_retry(error):
    lease=SimpleNamespace(deadline=240,stop=Event());logs=[]
    with pytest.raises(type(error)):
        r.renew_with_retry(lease,lambda:(_ for _ in ()).throw(error),clock=lambda:0,emit=lambda s,**k:logs.append(s))
    assert logs==[] and lease.stop.waits==[]

def test_storage_quota_specific_no_retry():
    lease=SimpleNamespace(deadline=240,stop=Event())
    with pytest.raises(r.DriveStorageFull,match="quota exceeded"):
        r.renew_with_retry(lease,lambda:(_ for _ in ()).throw(HTTP(403,"storageQuotaExceeded")),clock=lambda:0)
    assert lease.stop.waits==[]

def test_old_heartbeat_fails_first_timeout_but_fixed_update_recovers(fixture):
    m,old,backend,lease,cp=fixture
    original=next(cls for cls in type(lease).__mro__ if cls.__name__=="FitLease")
    backend.failures=[TimeoutError()]
    with pytest.raises(TimeoutError):original._update(lease)
    backend.failures=[TimeoutError(),HTTP(503)]
    lease._update()
    assert len(lease.stop.waits)==2

def test_actual_heartbeat_loop_old_fails_fixed_recovers(fixture):
    m, old, backend, lease, cp = fixture
    class SingleTick(Event):
        def wait(self,delay):
            if delay==45:
                if self.stopped:return True
                self.stopped=True
                return False
            return False
        def is_set(self):return False
    old_cls=m.FitLease.__mro__[1]
    old_backend=Backend();old_lease=old_cls(old_backend,{"old":True}).acquire()
    old_lease.stop=SingleTick();old_backend.failures=[TimeoutError("transport")]
    old_lease.heartbeat();old_lease.thread.join(timeout=2)
    assert not old_lease.thread.is_alive()
    with pytest.raises(Exception,match="[Hh]eartbeat failed"):old_lease.guard()
    lease.stop=SingleTick();backend.failures=[TimeoutError("transport")]
    lease.heartbeat();lease.thread.join(timeout=2)
    assert not lease.thread.is_alive() and lease.error is None
    lease.guard()
