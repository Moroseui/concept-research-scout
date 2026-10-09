"""Synthetic terminal proofs, real SQLite admission; no provider or model calls."""
from copy import deepcopy
from datetime import datetime,timezone
from types import SimpleNamespace as NS
import json,sqlite3
import pytest
from orchestrator import item4_fit_transport_recovery as r,private_records as pr,modal_terminal_cost as cost
from orchestrator.modal_executor import item4_job
from orchestrator.autonomy_accounting import BatchAccounts
from orchestrator.modal_budget import ComputeAccounts
from orchestrator.modal_billing import canonical
from orchestrator import modal_item4_budget as budget
from test_modal_item4_budget import bound,RATES


def view(amount='0.4'):
    body={'schema':'modal-billing-snapshot/v1','workspace':'synthetic','resolution':'h',
        'partial_hour_excluded':True,'report_start':'2026-10-01T00:00:00+00:00',
        'report_end_exclusive':'2026-10-08T19:00:00+00:00','observed_at':'2026-10-08T19:10:00+00:00',
        'rows':[{'object_id':'ap-one','interval_start':'2026-10-08T18:00:00+00:00','cost':amount,
            'cost_by_resource':{'GPU':amount}}],'rates':RATES,
        'summary':{'metered_cost':amount,'billed_cost':amount,'adjustments':{}}}
    return {**body,'sha256':r.sha(canonical(body))}


@pytest.fixture
def fixture(tmp_path,monkeypatch):
    batch=BatchAccounts(tmp_path/'ledger');batch.register_run('item4',{'backlog_item':4,'experiment_authority_sha256':budget.AUTHORITY})
    accounts=ComputeAccounts(batch);db=batch.db
    old=bound(cpu=16,memory_mib=131072,timeout_seconds=3600)
    old.update(purpose='M4_ITEM4',overhead_micro_usd=5_000_000,progress={'volume_id':'vo-synthetic'})
    old['cost']=budget.quote(old['resources'],RATES,old['overhead_micro_usd'])
    ident=r.sha(r.encoded(old));monkeypatch.setattr(r,'ORIGINAL_ID',ident)
    job=item4_job(old);root=tmp_path/'lane';pr.mkdir(root);work=root/'modal-executions'/job;pr.mkdir(work,parents=True)
    row={'id':ident,'run':'item4','binding':r.encoded(old).decode(),'status':'UNCERTAIN',
        'reserved_micro_usd':old['cost']['reserved_micro_usd'],'provider_id':'sb-synthetic','actual_micro_usd':None,'month':'2026-10'}
    db.execute('INSERT INTO autonomy_compute VALUES(?,?,?,?,?,?,?,?)',tuple(row.values()))
    originals={'create-intent.json':{'binding_sha256':ident,'cost_clock':{'observed_at':'2026-10-08T18:21:00+00:00'}},
        'created.json':{'binding_sha256':ident,'provider_id':'sb-synthetic','receipt':{'entrypoint':'idle-only'}},
        'operator-stopped.json':{'at':'2026-10-08T18:24:00+00:00','before':{'binding_sha256':ident,
            'provider_id':'sb-synthetic','progress_entries':[]},'native_poll_after':137,
            'native_termination':{'provider_id':'sb-synthetic','terminated':True}}}
    refs={}
    for name,value in originals.items():
        raw=r.encoded(value);pr.write_bytes(work/name,raw);refs[str(work/name)]=r.sha(raw)
    state={'phase':'EXECUTE_EXPERIMENT','fit_dispatch':{job:{'phase':'SUBMIT'}}};raw=r.encoded(state).decode()
    event={'original_row':row,'terminal_exit_code':137,'may_launch':False,'progress_empty':True,
        'evidence_files':refs,'original_state_sha256':r.sha(raw.encode())}
    new={**old,'fresh_start':{'previous_binding_sha256':ident,'terminal_event_sha256':r.sha(r.encoded(event))}}
    p={'old_row':row,'old_job':job,'old_state_raw':raw,'runtime':{'workspace':'synthetic'},'event':event,
        'evidence_files':refs,'new_binding':new,'new_initial_binding':new,'new_compute_id':r.sha(r.encoded(new)),
        'billing_window':['2026-10-08T18:00:00+00:00','2026-10-08T19:00:00+00:00']}
    monkeypatch.setattr(r,'contract',lambda:p);monkeypatch.setattr(r,'authority',lambda:{'report_sha256':'synthetic-review'})
    p['new_job']=item4_job(new)
    local=sqlite3.connect(':memory:',isolation_level=None);local.row_factory=sqlite3.Row
    local.execute('CREATE TABLE manual_state(id INTEGER,payload TEXT)');local.execute('INSERT INTO manual_state VALUES(1,?)',(raw,))
    local.execute('CREATE TABLE jobs(id TEXT PRIMARY KEY,status TEXT)');local.execute("INSERT INTO jobs VALUES(?,'BLOCKED')",(job,))
    p['old_local_row']=dict(local.execute('SELECT * FROM jobs').fetchone())
    driver=NS(state=root,config={'run_id':'item4'},store=NS(batch=batch,db=local),
        current=lambda:json.loads(local.execute('SELECT payload FROM manual_state').fetchone()[0]),
        save=lambda v:local.execute('UPDATE manual_state SET payload=?',(r.encoded(v).decode(),)))
    provider=NS(config=p['runtime'],_sandbox=lambda pid:NS(object_id=pid,poll=lambda:137),billing_snapshot=view)
    from orchestrator import modal_fit_provider as fit
    monkeypatch.setattr(fit,'progress_scope',lambda b:b['progress'])
    monkeypatch.setattr(fit,'progress_volume',lambda provider,scope:NS(object_id=scope['volume_id'],listdir=lambda *a,**kw:[]))
    yield NS(db=db,p=p,accounts=accounts,driver=driver,provider=provider,work=work,local=local)
    local.close();db.close()


def activate(f):return r.activate(f.driver,f.provider)


def test_activation_preserves_originals_and_job_and_is_idempotent(fixture):
    f=fixture;before={name:pr.check(name).read_bytes() for name in f.p['evidence_files']}
    assert activate(f)['status']=='EXACT_SUCCESSOR_SELECTED'
    row=dict(f.db.execute('SELECT * FROM autonomy_compute').fetchone())
    assert row=={**f.p['old_row'],'status':'ACCOUNTED'}
    assert dict(f.local.execute('SELECT * FROM jobs').fetchone())==f.p['old_local_row']
    assert f.driver.current()['fit_dispatch']==json.loads(f.p['old_state_raw'])['fit_dispatch']
    assert before=={name:pr.check(name).read_bytes() for name in before}
    assert activate(f)['status']=='ALREADY_ACTIVATED'
    assert f.db.execute('SELECT count(*) FROM events WHERE id LIKE ?',('%'+r.SUFFIX,)).fetchone()[0]==1
    assert cost.effective(f.db,row,RATES,snapshot=view())==5_400_000
    assert cost.record(f.accounts,row['id'],f.work)['original_reserved_micro_usd']==12_842_400


@pytest.mark.parametrize('damage',['alive','nonempty','original','state','row','missing-hour','incomplete-hour'])
def test_bad_terminal_or_accounting_proof_never_activates(fixture,damage,monkeypatch):
    f=fixture
    if damage=='alive':f.provider._sandbox=lambda pid:NS(object_id=pid,poll=lambda:None)
    elif damage=='nonempty':
        from orchestrator import modal_fit_provider as fit
        monkeypatch.setattr(fit,'progress_volume',lambda *a:NS(object_id='vo-synthetic',listdir=lambda *a,**kw:['unexpected']))
    elif damage=='original':pr.write_bytes(f.work/'created.json',b'{}')
    elif damage=='state':f.local.execute("UPDATE manual_state SET payload='{}'")
    elif damage=='row':f.db.execute('UPDATE autonomy_compute SET reserved_micro_usd=1')
    else:
        v=view();v.pop('sha256')
        if damage=='missing-hour':v['rows']=[]
        else:v['report_end_exclusive']='2026-10-08T18:00:00+00:00'
        v['sha256']=r.sha(canonical(v));f.provider.billing_snapshot=lambda:v
    with pytest.raises((ValueError,KeyError)):activate(f)
    assert f.db.execute('SELECT status FROM autonomy_compute').fetchone()[0]=='UNCERTAIN'
    assert r.KEY not in f.driver.current()
    assert not f.db.execute('SELECT 1 FROM events WHERE id LIKE ?',('%'+r.SUFFIX,)).fetchone()


def test_unqualified_uncertain_attempt_keeps_full_reservation(fixture):
    f=fixture;row=f.db.execute('SELECT * FROM autonomy_compute').fetchone()
    assert cost.effective(f.db,row,RATES,snapshot=view())==12_842_400


@pytest.mark.parametrize('damage',['resources','image','fit','link','resume'])
def test_new_job_identity_is_exact_not_a_generic_retry(fixture,damage):
    b=deepcopy(fixture.p['new_binding'])
    if damage=='resources':b['resources']['cpu']=8
    elif damage=='image':b['image_id']='im-other'
    elif damage=='fit':b['experiment']['fit_id']='other'
    elif damage=='link':b['fresh_start']['terminal_event_sha256']='f'*64
    else:b['resume']={}
    with pytest.raises(ValueError,match='ONE_EXACT_IDENTITY'):item4_job(b)


@pytest.mark.parametrize('over_cap',[False,True])
def test_normal_reservation_counts_old_cost_and_refuses_over_cap(fixture,over_cap):
    f=fixture;activate(f)
    retained=5_400_000;quote=f.p['new_binding']['cost']['reserved_micro_usd']
    assets=75_000_000-retained-quote+(1 if over_cap else 0)
    f.db.execute("INSERT INTO autonomy_assets VALUES('synthetic-asset','item4','{}','READY',?,'{}')",(assets,))
    kwargs={'billing_snapshot':view(),'now':datetime(2026,10,8,19,10,tzinfo=timezone.utc)}
    if over_cap:
        with pytest.raises(ValueError,match='ITEM4_HARD_COST_CAP'):
            f.accounts.reserve_item4(f.p['new_compute_id'],'item4',f.p['new_binding'],**kwargs)
        assert f.db.execute('SELECT count(*) FROM autonomy_compute').fetchone()[0]==1
    else:
        assert f.accounts.reserve_item4(f.p['new_compute_id'],'item4',f.p['new_binding'],**kwargs)
        assert not f.accounts.reserve_item4(f.p['new_compute_id'],'item4',f.p['new_binding'],**kwargs)
        assert f.db.execute('SELECT count(*) FROM autonomy_compute').fetchone()[0]==2
    assert dict(f.db.execute('SELECT * FROM autonomy_compute WHERE id=?',(r.ORIGINAL_ID,)).fetchone())=={**f.p['old_row'],'status':'ACCOUNTED'}


def test_later_billing_increase_and_overlap_fail_closed(fixture):
    f=fixture;activate(f);row=f.db.execute('SELECT * FROM autonomy_compute').fetchone()
    assert cost.effective(f.db,row,RATES,snapshot=view('1.5'))==6_500_000
    b=f.p['new_binding'];f.db.execute('INSERT INTO autonomy_compute VALUES(?,?,?,?,?,?,?,?)',
        (f.p['new_compute_id'],'item4',r.encoded(b).decode(),'RUNNING',12_842_400,'sb-new',None,'2026-10'))
    work=f.work.parent/f.p['new_job'];pr.mkdir(work)
    pr.write_bytes(work/'create-intent.json',r.encoded({'binding_sha256':f.p['new_compute_id'],
        'cost_clock':{'observed_at':'2026-10-08T18:59:00+00:00'}}))
    with pytest.raises(ValueError,match='BILLING_OVERLAP'):cost.effective(f.db,row,RATES,snapshot=view())


def test_highwater_survives_lower_later_billing(fixture):
    f=fixture;activate(f)
    snapshot=view('1.5')
    event={'schema':'item4-billing-highwater/v1','object_id':'ap-one','cycle':'2026-10',
        'micro_usd':1_500_000,'snapshot':snapshot}
    raw=r.encoded(event).decode()
    f.db.execute('INSERT INTO events VALUES(?,?,?)',('item4-billing:'+r.sha(raw.encode()),'item4',raw))
    row=f.db.execute('SELECT * FROM autonomy_compute').fetchone()
    assert cost.effective(f.db,row,RATES,snapshot=view())==6_500_000


def test_cross_ledger_crash_reuses_one_terminal_record(fixture):
    f=fixture;activate(f)
    original_events=[tuple(x) for x in f.db.execute('SELECT * FROM events')]
    f.local.execute('UPDATE manual_state SET payload=?',(f.p['old_state_raw'],))
    assert activate(f)['status']=='EXACT_SUCCESSOR_SELECTED'
    assert original_events==[tuple(x) for x in f.db.execute('SELECT * FROM events')]
    assert f.db.execute('SELECT count(*) FROM autonomy_compute').fetchone()[0]==1
