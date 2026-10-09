"""Synthetic terminal assets; actual immutable ledger and effective-cost code."""
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace
import json
import sqlite3
import pytest
from orchestrator import item4_closed_asset_billing as cb, private_records as pr
from orchestrator import modal_direct_recovery
from orchestrator.modal_billing import canonical
from orchestrator.manual_executor import digest
from orchestrator.modal_executor import canonical as binding_bytes

NOW = datetime(2026, 10, 9, 17, tzinfo=timezone.utc)


def view(first='0.00008061'):
    rows = [{'object_id':'ap-first','interval_start':'2026-10-06T15:00:00+00:00',
             'cost':first,'cost_by_resource':{'CPU':first}},
            {'object_id':'ap-second','interval_start':'2026-10-06T11:00:00+00:00',
             'cost':'0.00001186','cost_by_resource':{'CPU':'0.00001186'}}]
    body = {'schema':'modal-billing-snapshot/v1','workspace':'synthetic','resolution':'h',
            'partial_hour_excluded':True,'report_start':'2026-10-01T00:00:00+00:00',
            'report_end_exclusive':'2026-10-09T17:00:00+00:00','observed_at':NOW.isoformat(),
            'rows':rows,'rates':{'volume_storage_gib_month_cost':'.09','egress_gib_cost':'.04'}}
    return {**body,'sha256':digest(canonical(body))}


@pytest.fixture
def fixture(tmp_path, monkeypatch):
    db=sqlite3.connect(':memory:',isolation_level=None);db.row_factory=sqlite3.Row
    db.execute('CREATE TABLE autonomy_assets(id TEXT PRIMARY KEY,run TEXT,binding TEXT,status TEXT,reserved_micro_usd INTEGER,receipt TEXT)')
    db.execute('CREATE TABLE autonomy_compute(id TEXT PRIMARY KEY,binding TEXT)')
    db.execute('CREATE TABLE events(id TEXT PRIMARY KEY,job TEXT,payload TEXT)')
    observed={'accounting_mutations':0,'model_calls':0,'new_compute':0,
              'original_rows':{},'provider_checks':[],'billing':view()}
    proofs=[]
    for i,name in enumerate(['first','second']):
        binding={'run_id':'synthetic-inputs','label':name,'asset_expires_utc':'2026-11-05T00:00:00+00:00',
                 'envelope':{'maximum_stored_bytes':54*1024**3+2*1024**3+4*1024**2,
                             'download_bytes':54*1024**3,'reserved_storage_days':35,
                             'billing_month_days_floor':28,'registry_headroom_micro_usd':1000000,
                             'receipt_egress_bound_bytes':4*1024**2,'cost':{'reserved_micro_usd':8056706}}}
        ident=digest(binding_bytes(binding))
        failure={'status':'FAILED','exit_code':i+1,'no_automatic_retry':True,'provider_id':'sb-'+name}
        handle={'app_id':'ap-'+name,'binding_sha256':ident,'provider_id':'sb-'+name,
                'data_volume_id':'vo-data'+name,'package_volume_id':'vo-package'+name,
                'launched_at':f"2026-10-06T{15 if i==0 else 11}:10:00+00:00"}
        proof={'binding':binding,'failure':failure,'handle':handle,
               'old':{'units':{'synthetic-'+name+'.service':{'sha256':'a'*64}}}}
        proofs.append(proof)
        row={'id':ident,'run':'synthetic-inputs','binding':binding_bytes(binding).decode(),
             'status':'UNCERTAIN','reserved_micro_usd':8056706,'receipt':canonical(failure).decode()}
        db.execute('INSERT INTO autonomy_assets VALUES(?,?,?,?,?,?)',tuple(row.values()))
        observed['original_rows'][ident]=row
        observed['provider_checks'].append({'asset_id':ident,'app_id':handle['app_id'],
            'terminal_poll':i+1,'data_volume_id':{'id':handle['data_volume_id'],'files':0,'bytes':0,'types':[]},
            'package_volume_id':{'id':handle['package_volume_id'],'files':10,'bytes':271309,'types':['FILE']},
            'units':{'synthetic-'+name+'.service':{'ActiveState':'inactive','UnitFileState':'disabled','MainPID':'0'}},
            'billing_rows':[r for r in observed['billing']['rows'] if r['object_id']==handle['app_id']]})
    original={**proofs[0],'ancestor':proofs[1],'ancestor_ids':set(observed['original_rows'])}
    observed['qualifications']=cb.normalize(original)
    child={'id':'ready-child','run':'synthetic-inputs','binding':canonical({'recovery':{'synthetic':True}}).decode(),
           'status':'READY','reserved_micro_usd':8056706,'receipt':'{}'}
    db.execute('INSERT INTO autonomy_assets VALUES(?,?,?,?,?,?)',tuple(child.values()))
    observed['ready_child']=child
    path=tmp_path/'observation.json';raw=canonical(observed);pr.write_bytes(path,raw)
    p={'observation':{'path':str(path),'sha256':digest(raw)},'selected':list(observed['original_rows']),
       'ready_child':child['id'],'operator':{'sha256':'f'*64}}
    accounts=SimpleNamespace(db=db,batch=SimpleNamespace(filesystem_root=Path('/')))
    monkeypatch.setattr(cb,'contract',lambda:p)
    monkeypatch.setattr(cb,'units_stopped',lambda proof:None) # Synthetic systemd only.
    monkeypatch.setattr(modal_direct_recovery,'parent',lambda *a,**kw:original) # Synthetic installed native proof.
    yield accounts,p,observed,original
    db.close()


def rewrite(p, observed):
    raw=canonical(observed);pr.write_bytes(p['observation']['path'],raw)
    p['observation']['sha256']=digest(raw)


def test_preserves_all_original_rows_and_unselected_full_reservation(fixture):
    a,p,o,_=fixture
    before=[dict(r) for r in a.db.execute('SELECT * FROM autonomy_assets')]
    result=cb.record(a)
    assert cb.record(a)==result
    assert before==[dict(r) for r in a.db.execute('SELECT * FROM autonomy_assets')]
    amounts=[cb.effective(a,r,view(),NOW) for r in before]
    assert amounts==[1225678,1225609,8056706]
    assert a.db.execute('SELECT count(*) FROM events').fetchone()[0]==2
    assert all(x['original_reserved_micro_usd']==8056706 for x in result['records'].values())


@pytest.mark.parametrize('damage',['row','unknown','observation','native','empty','billing','unit','shared','expiry'])
def test_missing_changed_or_uncertain_proof_fails_closed(fixture,damage):
    a,p,o,original=fixture;ident=p['selected'][0]
    if damage=='row':a.db.execute('UPDATE autonomy_assets SET reserved_micro_usd=1 WHERE id=?',(ident,))
    elif damage=='unknown':o['provider_checks'][0]['terminal_poll']=None;rewrite(p,o)
    elif damage=='observation':pr.write_bytes(p['observation']['path'],b'{}')
    elif damage=='native':original['failure']['exit_code']=9
    elif damage=='empty':o['provider_checks'][0]['data_volume_id']['files']=1;rewrite(p,o)
    elif damage=='billing':o['provider_checks'][0]['billing_rows']=[];rewrite(p,o)
    elif damage=='unit':o['provider_checks'][0]['units']['synthetic-first.service']['ActiveState']='active';rewrite(p,o)
    elif damage=='shared':a.db.execute('INSERT INTO autonomy_compute VALUES(?,?)',('other',canonical({'experiment':{'billing_object_id':'ap-first'}}).decode()))
    else:
        cb.record(a)
        with pytest.raises(ValueError,match='RETENTION_RECONCILIATION_DUE'):
            cb.effective(a,o['original_rows'][ident],view(),datetime(2027,1,1,tzinfo=timezone.utc))
        return
    with pytest.raises(ValueError):cb.record(a)
    assert a.db.execute('SELECT count(*) FROM events').fetchone()[0]==0


def test_later_upward_billing_retained_and_current_increase_counts(fixture):
    a,p,o,_=fixture;cb.record(a);ident=p['selected'][0]
    saved={'schema':'item4-billing-highwater/v1','snapshot':view('2')}
    raw=canonical(saved).decode()
    a.db.execute('INSERT INTO events VALUES(?,?,?)',('item4-billing:'+digest(raw.encode()),'synthetic-inputs',raw))
    assert cb.effective(a,o['original_rows'][ident],view(),NOW)==3225597
    assert cb.effective(a,o['original_rows'][ident],view('9'),NOW)==10225597


def test_receipt_forgery_cannot_discount_unselected_asset(fixture):
    a,p,o,_=fixture;cb.record(a)
    prior=a.db.execute('SELECT payload FROM events LIMIT 1').fetchone()[0]
    a.db.execute('INSERT INTO events VALUES(?,?,?)',('ready-child'+cb.SUFFIX,'synthetic-inputs',prior))
    with pytest.raises(ValueError,match='RECEIPT_SCOPE'):cb.effective(a,o['ready_child'],view(),NOW)


def test_receipt_tamper_is_not_silently_ignored(fixture):
    a,p,o,_=fixture;cb.record(a);ident=p['selected'][0]
    a.db.execute("UPDATE events SET payload='{}' WHERE id=?",(ident+cb.SUFFIX,))
    with pytest.raises(ValueError,match='RECEIPT_CHANGED'):cb.effective(a,o['original_rows'][ident],view(),NOW)
