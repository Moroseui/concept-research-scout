"""Real record/exposure transactions on synthetic closed and live attempts."""
from copy import deepcopy
from decimal import Decimal
from pathlib import Path
from types import SimpleNamespace
import json
import sqlite3
import pytest
from orchestrator import item4_closed_attempt_billing as cb, modal_terminal_cost as cost, private_records as pr
from orchestrator.modal_executor import item4_job
from orchestrator.modal_billing import canonical
from orchestrator.manual_executor import digest


def view(amounts=('0.58471212','1.62052681','0.13356001')):
    rows=[{'object_id':'ap-test','interval_start':f'2026-10-09T{hour}:00:00+00:00',
           'cost':amount,'cost_by_resource':{'CPU':amount}}
          for hour,amount in zip(('11','12','13'),amounts)]
    body={'schema':'modal-billing-snapshot/v1','workspace':'synthetic','resolution':'h',
          'partial_hour_excluded':True,'report_start':'2026-10-01T00:00:00+00:00',
          'report_end_exclusive':'2026-10-09T14:00:00+00:00',
          'observed_at':'2026-10-09T14:20:00+00:00','rows':rows,'rates':{}}
    return {**body,'sha256':digest(canonical(body))}


@pytest.fixture
def fixture(tmp_path,monkeypatch):
    db=sqlite3.connect(':memory:',isolation_level=None);db.row_factory=sqlite3.Row
    db.execute('CREATE TABLE autonomy_compute(id TEXT PRIMARY KEY,run TEXT,binding TEXT,status TEXT,reserved_micro_usd INTEGER,provider_id TEXT,actual_micro_usd INTEGER,month TEXT)')
    db.execute('CREATE TABLE events(id TEXT PRIMARY KEY,job TEXT,payload TEXT)')
    originals={};rows=[];events={};selected={}
    windows=[('11','12'),('12','14')]
    for i in range(3):
        binding={'purpose':'M4_ITEM4','run_id':'experiment-test','resources':{'gpu':None},
                 'experiment':{'fit_id':'prep-base','segment':i+1,'stage':'SMOKE','billing_object_id':'ap-test'},
                 'overhead_micro_usd':5000000,'cost':{'overhead_micro_usd':5000000,'reserved_micro_usd':10342400}}
        ident=digest(cb.encoded(binding));job=item4_job(binding);root=tmp_path/job;pr.mkdir(root)
        intent={'binding_sha256':ident,'cost_clock':{'observed_at':f'2026-10-09T{(11,12,14)[i]}:05:00+00:00'},
                'preflight':{'app_id':'ap-test'}}
        name=str(root/'create-intent.json');raw=cb.encoded(intent);pr.write_bytes(name,raw)
        originals[name]={'sha256':digest(raw),'text':raw.decode()}
        row={'id':ident,'run':'experiment-test','binding':cb.encoded(binding).decode(),
             'status':'RUNNING' if i==2 else 'ACCOUNTED','reserved_micro_usd':10342400,
             'provider_id':f'sb-test{i}','actual_micro_usd':None,'month':'2026-10'}
        db.execute('INSERT INTO autonomy_compute VALUES(?,?,?,?,?,?,?,?)',tuple(row.values()));rows.append(row)
        if i==2:continue
        stopname=str(root/'STOPPED.json')
        stopped={'at':f'2026-10-09T{(11,13)[i]}:10:00+00:00','provider_id':row['provider_id'],'terminated':True}
        stopraw=cb.encoded(stopped);pr.write_bytes(stopname,stopraw);originals[stopname]={'sha256':digest(stopraw),'text':stopraw.decode()}
        proof={'terminal_exit_code':137,'may_launch':False,'original_row':{**row,'status':'RUNNING'},
               'evidence_files':{name:digest(raw),stopname:digest(stopraw)}}
        event={'id':ident+':pre-science-stop','job':row['run'],'payload':cb.encoded(proof).decode()}
        events[event['id']]=event;db.execute('INSERT INTO events VALUES(?,?,?)',tuple(event.values()))
        selected[ident]={'row':row,'event':event,'intent':name,'stopped':stopname,'overhead_micro_usd':5000000,
                         'window':[f'2026-10-09T{x}:00:00+00:00' for x in windows[i]]}
    observed={'app_id':'ap-test','accounting_mutations':0,'model_calls':0,'new_compute':0,
              'rows':rows,'events':events,'originals':originals,'billing':view()}
    path=tmp_path/'OBSERVED.json';raw=cb.encoded(observed);pr.write_bytes(path,raw)
    p={'schema':'item4-confirmed-closed-compute/v1','observation':{'path':str(path),'sha256':digest(raw)},
       'selected':selected,'application':'ap-test','current_attempt':rows[2]['id'],'work_root':str(tmp_path),
       'operator':{'text':'synthetic operator authority','sha256':digest(b'synthetic operator authority')}}
    monkeypatch.setattr(cb,'contract',lambda:p)
    yield SimpleNamespace(db=db),p,observed,rows
    db.close()


def test_original_rows_live_reservation_and_idempotency(fixture):
    accounts,p,observed,rows=fixture;db=accounts.db
    before=[tuple(x) for x in db.execute('SELECT * FROM autonomy_compute')]
    old_events=[tuple(x) for x in db.execute('SELECT * FROM events')]
    result=cb.record(accounts)
    assert result['status']=='CONFIRMED_COMPUTE_RECORDED_OVERHEAD_RETAINED'
    amounts=[cost.effective(db,db.execute('SELECT * FROM autonomy_compute WHERE id=?',(r['id'],)).fetchone(),{}) for r in rows]
    assert amounts==[5584713,6754087,10342400]
    assert before==[tuple(x) for x in db.execute('SELECT * FROM autonomy_compute')]
    assert old_events==[tuple(x) for x in db.execute("SELECT * FROM events WHERE id NOT LIKE ?",('%'+cb.SUFFIX,))]
    after=[tuple(x) for x in db.execute('SELECT * FROM events')]
    assert cb.record(accounts)==result and after==[tuple(x) for x in db.execute('SELECT * FROM events')]
    exposure=cost.exposure(db,db.execute('SELECT * FROM autonomy_compute').fetchall(),view())
    assert exposure['smoke_cost']['experiment-test']==sum(amounts)


@pytest.mark.parametrize('status',['RUNNING','UNCERTAIN','RESERVED','COLLECTED'])
def test_no_credit_for_changed_or_unqualified_old_state(fixture,status):
    accounts,p,observed,rows=fixture;db=accounts.db
    db.execute('UPDATE autonomy_compute SET status=? WHERE id=?',(status,rows[0]['id']))
    with pytest.raises(ValueError,match='TERMINAL_ROW'):cb.record(accounts)
    assert not db.execute('SELECT 1 FROM events WHERE id LIKE ?',('%'+cb.SUFFIX,)).fetchone()


@pytest.mark.parametrize('damage',['original','event','amount','overlap','report','missing-hour','live-included'])
def test_tamper_and_incomplete_attribution_refuse_atomically(fixture,damage):
    accounts,p,observed,rows=fixture;db=accounts.db;entry=p['selected'][rows[0]['id']]
    if damage=='original':pr.write_bytes(entry['intent'],b'{}')
    elif damage=='event':db.execute("UPDATE events SET payload='{}' WHERE id=?",(rows[0]['id']+':pre-science-stop',))
    elif damage=='amount':db.execute('UPDATE autonomy_compute SET reserved_micro_usd=1 WHERE id=?',(rows[0]['id'],))
    elif damage=='overlap':
        entry['window'][1]='2026-10-09T13:00:00+00:00'
    elif damage=='live-included':p['current_attempt']=rows[0]['id']
    else:
        if damage=='report':observed['billing']['report_end_exclusive']='2026-10-09T13:00:00+00:00'
        else:observed['billing']['rows'].pop(0)
        body=dict(observed['billing']);body.pop('sha256');observed['billing']['sha256']=digest(canonical(body))
        raw=cb.encoded(observed);pr.write_bytes(p['observation']['path'],raw);p['observation']['sha256']=digest(raw)
    with pytest.raises(ValueError):cb.record(accounts)
    assert not db.execute('SELECT 1 FROM events WHERE id LIKE ?',('%'+cb.SUFFIX,)).fetchone()


def test_later_increase_survives_lower_current_observation(fixture):
    accounts,p,observed,rows=fixture;db=accounts.db;cb.record(accounts)
    higher=view(('1.25','1.62052681','0.13356001'))
    value={'schema':'item4-billing-highwater/v1','object_id':'ap-test','cycle':'2026-10',
           'micro_usd':3004087,'snapshot':higher}
    raw=cb.encoded(value).decode();db.execute('INSERT INTO events VALUES(?,?,?)',('item4-billing:'+digest(raw.encode()),rows[0]['run'],raw))
    row=db.execute('SELECT * FROM autonomy_compute WHERE id=?',(rows[0]['id'],)).fetchone()
    assert cost.effective(db,row,{},snapshot=view())==6250000
    latest=view(('2.0','1.62052681','0.13356001'))
    assert cost.effective(db,row,{},snapshot=latest)==7000000


def test_forged_live_receipt_never_releases_live_reservation(fixture):
    accounts,p,observed,rows=fixture;db=accounts.db;cb.record(accounts)
    old=db.execute('SELECT payload FROM events WHERE id=?',(rows[0]['id']+cb.SUFFIX,)).fetchone()[0]
    db.execute('INSERT INTO events VALUES(?,?,?)',(rows[2]['id']+cb.SUFFIX,rows[2]['run'],old))
    with pytest.raises(ValueError,match='RECEIPT_SCOPE'):cost.effective(db,rows[2],{})


def test_historical_receipt_tamper_refuses(fixture):
    accounts,p,observed,rows=fixture;db=accounts.db;cb.record(accounts)
    db.execute("UPDATE events SET payload='{}' WHERE id=?",(rows[0]['id']+cb.SUFFIX,))
    with pytest.raises(ValueError,match='RECEIPT_CHANGED'):cost.effective(db,rows[0],{})
