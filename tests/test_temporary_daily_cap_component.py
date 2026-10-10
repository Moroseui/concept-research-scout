"""Component boundary checks using frozen original admission implementations."""
import importlib.util
from pathlib import Path
import pytest
from orchestrator import autonomy_limits as limits, autonomy_accounting as accounting, autonomy_review_runner as reviewer
from tools import temporary_daily_cap as component
from tools.install_temporary_daily_cap import unit_bytes

ROOT = Path(__file__).resolve().parents[1]


def original(name):
    p = ROOT/'tests/fixtures/daily_cap'/(name+'.py')
    return component.module('_frozen_'+name, p)


@pytest.mark.parametrize('kind,source,cls,name', [
    ('scientific','autonomy_accounting',accounting.BatchAccounts,'reserve_scientific'),
    ('administrative','autonomy_review_runner',reviewer.ReviewQueue,'reserve')])
def test_exact_original_method_bound_without_replacing_limits_or_selectors(monkeypatch, kind, source, cls, name):
    base = getattr(getattr(original(source), cls.__name__), name)
    monkeypatch.setattr(cls, name, base)
    before = {k:getattr(limits,k) for k in ('global_limit','local_limit','scientific_batch_allowance','cap_authority')}
    # Register restorations before component's intentional in-memory changes.
    monkeypatch.setattr(limits, 'daily_allowance', limits.daily_allowance)
    changed = component.bind(kind, ROOT)
    assert getattr(cls,name) is changed and changed is not base
    assert changed.__globals__['limits'] is limits
    assert all(getattr(limits,k) is value for k,value in before.items())
    assert limits.daily_allowance('2026-10-10')['limit'] == 100
    assert limits.daily_allowance('2026-10-11')['limit'] == 50


def test_scoped_or_unrecognized_method_is_never_replaced(monkeypatch):
    def existing_wrapper(*args, **kwargs): return None
    monkeypatch.setattr(accounting.BatchAccounts,'reserve_scientific',existing_wrapper)
    with pytest.raises(ValueError, match='ORIGINAL_ADMISSION_METHOD'):
        component.bind('scientific', ROOT)
    assert accounting.BatchAccounts.reserve_scientific is existing_wrapper


def test_unit_retains_every_existing_protection():
    old = ('[Service]\nUser=partho\nGroup=partho\nExecStartPre=+/original/guard\n'
           'ExecStart=/usr/bin/python3 -s -B '+str(component.AUTHOR)+' run\n'
           'Restart=no\nNoNewPrivileges=true\nProtectSystem=strict\nPrivateTmp=true\n').encode()
    new = unit_bytes(old, component.ROOT/'tools/temporary_daily_cap.py')
    assert [s for s in old.splitlines() if not s.startswith(b'ExecStart=')] == [s for s in new.splitlines() if not s.startswith(b'ExecStart=')]
    assert b'author run' in new
    with pytest.raises(ValueError,match='ORIGINAL_UNIT_COMMAND'):
        unit_bytes(old.replace(b' run\n',b' verify\n'),component.ROOT/'tools/temporary_daily_cap.py')


def test_author_hook_keeps_scoped_wrapper_around_dated_base(monkeypatch):
    import types
    base = original('autonomy_accounting').BatchAccounts.reserve_scientific
    monkeypatch.setattr(accounting.BatchAccounts, 'reserve_scientific', base)
    monkeypatch.setattr(limits, 'daily_allowance', limits.daily_allowance)
    monkeypatch.setattr(component,'verified',lambda *a,**k: {})
    monkeypatch.setattr(component,'trusted',lambda p: ROOT/'tools/item4_smoke_response_runtime.py')
    monkeypatch.setattr(component,'AUTHOR_PIN',component.sha((ROOT/'tools/item4_smoke_response_runtime.py').read_bytes()))
    def factory(name,path):return object()
    route = types.SimpleNamespace(module=factory)
    def connect():
        route.module('orchestrator.item4_scoped_calls',Path('/synthetic-only'))
        old_batch = accounting.BatchAccounts.reserve_scientific
        def scoped(*args,**kw):return old_batch(*args,**kw)
        accounting.BatchAccounts.reserve_scientific = scoped
        return 'connected'
    route.connect = connect
    old_module = component.module
    monkeypatch.setattr(component,'module',lambda name,path: route if name=='_dated_daily_author' else old_module(name,path))
    assert component.author_route(ROOT).connect() == 'connected'
    assert accounting.BatchAccounts.reserve_scientific.__name__ == 'scoped'


@pytest.mark.parametrize('count,day,running,used,ok', [
    (50,'2026-10-10',False,False,True),
    (49,'2026-10-10',False,False,False),
    (51,'2026-10-10',False,False,False),
    (50,'2026-10-11',False,False,False),
    (50,'2026-10-10',True,False,False),
    (50,'2026-10-10',False,True,False)])
def test_bootstrap_only_call51_no_reuse(tmp_path,count,day,running,used,ok):
    import sqlite3
    from tools import review_temporary_daily_cap_once as bootstrap
    db=sqlite3.connect(':memory:')
    db.execute('CREATE TABLE autonomy_calls(id TEXT,change_id TEXT,day TEXT,status TEXT)')
    for n in range(count):
        db.execute('INSERT INTO autonomy_calls VALUES(?,?,?,?)',
            ('row'+str(n), bootstrap.CHANGE if used and n==0 else 'other',
             '2026-10-10','RUNNING' if running and n==0 else 'COMPLETE'))
    before=db.execute('SELECT * FROM autonomy_calls').fetchall()
    if ok: bootstrap.admission_preflight(db,'new-packet',day)
    else:
        with pytest.raises(ValueError):bootstrap.admission_preflight(db,'new-packet',day)
    assert db.execute('SELECT * FROM autonomy_calls').fetchall()==before


def test_bootstrap_cannot_cross_utc_midnight():
    from tools import review_temporary_daily_cap_once as bootstrap
    policy=bootstrap.dated_bootstrap(limits.daily_allowance)
    assert policy('2026-10-10')['limit']==100
    with pytest.raises(ValueError,match='UTC_DAY'):policy('2026-10-11')



def test_host_wrapper_targets_new_unit_without_changing_bounds_or_stop(monkeypatch):
    from types import SimpleNamespace
    from tools import temporary_daily_cap_host as wrapper
    host = component.module('_frozen_host_test', ROOT/'tools/item4_response_host_operation.py')
    before = (host.start,host.pulse,host.safe_stop,host.starting_state,host.HOOK,
              host.ENTRY,host.RUNTIME,host.MAX_SECONDS,host.MAX_REFRESHES)
    monkeypatch.setattr(wrapper.os,'getuid',lambda:0)
    monkeypatch.setattr(host,'authority',lambda *a: ({},{'test_only':True}))
    monkeypatch.setattr(host,'trusted',lambda p: ROOT/'tools/item4_response_host_operation.py')
    monkeypatch.setattr(host,'command',lambda args: 'MainPID=0\nActiveState=inactive\n')
    fake_cap=SimpleNamespace(ROOT=ROOT,RECORD=Path('/test-only-record'),verified=lambda: {})
    monkeypatch.setattr(wrapper,'load',lambda name,path:host if 'host_operation' in name else fake_cap)
    selected=wrapper.connect()
    assert selected is host and host.UNIT==wrapper.NEW_UNIT
    assert host.OPERATION_ROOT==Path('/test-only-record/operation')
    assert before==(host.start,host.pulse,host.safe_stop,host.starting_state,host.HOOK,
                    host.ENTRY,host.RUNTIME,host.MAX_SECONDS,host.MAX_REFRESHES)
    commands=[]
    monkeypatch.setattr(host,'unit',lambda: {'InvocationID':'same','ActiveState':'activating'})
    monkeypatch.setattr(host,'command',lambda args:commands.append(args))
    host.safe_stop({'invocation':'same'})
    assert commands==[['systemctl','stop',wrapper.NEW_UNIT]]
    args=[]
    monkeypatch.setattr(wrapper,'connect',lambda:host)
    monkeypatch.setattr(host,'main',lambda:args.extend(wrapper.sys.argv))
    wrapper.main(['pulse'])
    assert args[1:]==['pulse','--stage','author','--review',str(wrapper.OLD_REVIEW)]
