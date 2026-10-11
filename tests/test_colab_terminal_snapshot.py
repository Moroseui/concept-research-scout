import hashlib,sqlite3
from pathlib import Path
import pytest
from orchestrator import colab_author_terminal as m

@pytest.fixture
def ledger(tmp_path,monkeypatch):
    lane=tmp_path/'lane';lane.mkdir(mode=0o700);p=lane/'jobs.sqlite'
    db=sqlite3.connect(p);db.execute('pragma journal_mode=wal')
    db.execute('create table manual_calls(id text,status text)')
    db.execute('insert into manual_calls values(?,?)',(m.CALL,'UNCERTAIN'))
    db.execute('create table manual_state(id integer,payload text)')
    db.execute('insert into manual_state values(1,?)',('{"phase":"BLOCKED"}',))
    db.commit();db.close();p.chmod(0o600)
    raw=p.read_bytes();assert raw[18:20]==b'\x02\x02'
    assert list(lane.iterdir())==[p]
    monkeypatch.setattr(m,'DB_SHA',hashlib.sha256(raw).hexdigest())
    monkeypatch.setattr(m,'DB_BYTES',len(raw))
    temps=tmp_path/'private-tmp';temps.mkdir(mode=0o700)
    monkeypatch.setattr(m.tempfile,'tempdir',str(temps))
    return {'lane':str(lane)},p,raw,temps


def test_closed_wal_snapshot_preserves_original_and_removes_private_copy(ledger,monkeypatch):
    f,p,raw,temps=ledger;connect=sqlite3.connect;seen=[]
    def checked(dburl,**kw):
        assert 'immutable=1' in dburl and str(p) not in dburl
        snapshot=next(temps.glob('*/terminal.sqlite'))
        assert snapshot.read_bytes()==raw and snapshot.stat().st_mode&0o777==0o400
        assert snapshot.parent.stat().st_mode&0o777==0o700
        seen.append(snapshot)
        return connect(dburl,**kw)
    monkeypatch.setattr(m.sqlite3,'connect',checked)
    assert m.local_state(f)==({'id':m.CALL,'status':'UNCERTAIN'},'{"phase":"BLOCKED"}')
    assert p.read_bytes()==raw and list(p.parent.iterdir())==[p]
    assert seen and not list(temps.iterdir())

@pytest.mark.parametrize('suffix',['-wal','-shm','-journal'])
@pytest.mark.parametrize('kind',['empty','content','dangling-link'])
def test_any_sidecar_refuses_before_sqlite(ledger,monkeypatch,suffix,kind):
    f,p,raw,temps=ledger;q=p.with_name(p.name+suffix)
    if kind=='dangling-link':q.symlink_to(p.parent/'missing')
    else:q.write_bytes(b'' if kind=='empty' else b'uncheckpointed bytes')
    monkeypatch.setattr(m.sqlite3,'connect',lambda *a,**k:pytest.fail('must refuse before SQLite'))
    with pytest.raises(ValueError,match='DATABASE_SIDECAR_PRESENT'):m.local_state(f)
    assert not list(temps.iterdir()) and p.read_bytes()==raw

@pytest.mark.parametrize('damage',['size','bytes'])
def test_changed_database_refuses_before_sqlite(ledger,monkeypatch,damage):
    f,p,raw,temps=ledger
    p.write_bytes(raw+b'x' if damage=='size' else raw[:-1]+bytes([raw[-1]^1]))
    monkeypatch.setattr(m.sqlite3,'connect',lambda *a,**k:pytest.fail('must refuse before SQLite'))
    with pytest.raises(ValueError,match='DATABASE_(SIZE|BYTES)_CHANGED'):m.local_state(f)
    assert not list(temps.iterdir())

@pytest.mark.parametrize('damage',['bytes','wal','shm','journal'])
def test_change_during_snapshot_query_refuses_and_cleans(ledger,monkeypatch,damage):
    f,p,raw,temps=ledger;connect=sqlite3.connect
    def changed(dburl,**kw):
        if damage=='bytes':p.write_bytes(raw[:-1]+bytes([raw[-1]^1]))
        else:p.with_name(p.name+'-'+damage).write_bytes(b'new sidecar')
        return connect(dburl,**kw)
    monkeypatch.setattr(m.sqlite3,'connect',changed)
    with pytest.raises(ValueError,match='DATABASE_'):m.local_state(f)
    assert not list(temps.iterdir())


def test_query_failure_cleans_private_snapshot(ledger,monkeypatch):
    f,p,raw,temps=ledger;connect=sqlite3.connect
    class Broken:
        row_factory=None
        def execute(self,*a):raise sqlite3.OperationalError('synthetic query failure')
        def close(self):self.closed=True
    broken=Broken();monkeypatch.setattr(m.sqlite3,'connect',lambda *a,**k:broken)
    with pytest.raises(sqlite3.OperationalError,match='synthetic'):m.local_state(f)
    assert broken.closed and not list(temps.iterdir()) and p.read_bytes()==raw
