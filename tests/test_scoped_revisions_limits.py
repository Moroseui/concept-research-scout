"""Synthetic deterministic admission and finding tests; no provider calls."""
from datetime import datetime, timezone
import json
from pathlib import Path
import pytest
from orchestrator import autonomy_limits as limits, analysis_revisions as revisions
from orchestrator import manual_driver, private_records, dispatch_limiter
from orchestrator.manual_executor import ManualExecutor, Accounts, atomic, read, digest
from orchestrator.autonomy_accounting import BatchAccounts
from test_manual_lane import lane, root, ROOT, policy


def configured(tmp_path, item=2, backend='analysis'):
    state=tmp_path/'lane'; private_records.mkdir(state)
    config={'run_id':'synthetic','item_number':item,'backend':backend,'policy':policy(),
        'root':str(ROOT),'review_contract':'bound-review/v1','revision_policy':revisions.POLICY}
    atomic(state/'lane.json',config)
    batch=BatchAccounts(tmp_path/'batch',filesystem_root=tmp_path)
    # Bound maps this absolute path into the scratch root; use root-relative state.
    batch.register_run('synthetic',{'state':'/lane'})
    store=ManualExecutor(state/'jobs.sqlite',batch=batch);store.initialize_allowance(policy())
    return store,batch,config


@pytest.mark.parametrize('item,backend,cap',[(2,'analysis',16),(3,'cpu',20),(4,'modal',20),(1,'analysis',8),(2,'cpu',8),(3,'analysis',8),(True,'analysis',8)])
def test_selected_limits_are_scoped_and_do_not_grant_execution(tmp_path,item,backend,cap):
    store,batch,c=configured(tmp_path,item,backend)
    assert limits.local_limit(store,'synthetic',policy())==cap
    assert limits.global_limit(batch,'synthetic')==cap
    assert store.db.execute('SELECT count(*) FROM manual_calls').fetchone()[0]==0


def seed(batch,count,kind='scientific',day='2020-01-01',run='elsewhere'):
    for i in range(count):
        batch.db.execute('INSERT INTO autonomy_calls VALUES(?,?,?,?,?,?,?,?)',
            ('seed-'+str(i),kind,run,1,day,'FAILED','{}','{}'))


def test_batch_limit_counts_all_historical_failed_rows(tmp_path):
    store,batch,c=configured(tmp_path);seed(batch,59)
    assert batch.reserve_scientific('one','synthetic','run_spec_author','a'*40,{})['batch_limit']==60
    batch.finish_scientific('one',{},'COMPLETE')
    before=[tuple(x) for x in batch.db.execute('SELECT * FROM autonomy_calls')]
    with pytest.raises(ValueError,match='^AUTONOMY_BATCH_CALL_LIMIT$'):
        batch.reserve_scientific('two','synthetic','run_spec_review','a'*40,{})
    assert [tuple(x) for x in batch.db.execute('SELECT * FROM autonomy_calls')]==before


def test_day_limit_counts_administrative_and_scientific_failures(tmp_path):
    store,batch,c=configured(tmp_path)
    seed(batch,49,kind='implementation_review',day=datetime.now(timezone.utc).date().isoformat())
    batch.reserve_scientific('one','synthetic','run_spec_author','a'*40,{})
    batch.finish_scientific('one',{},'COMPLETE')
    with pytest.raises(ValueError,match='^AUTONOMY_DAILY_CALL_LIMIT$'):
        batch.reserve_scientific('two','synthetic','run_spec_review','a'*40,{})
    assert batch.db.execute('SELECT count(*) FROM autonomy_calls').fetchone()[0]==50


def test_sixteen_call_limit_preserves_original_two_rows_and_account_policy(tmp_path,monkeypatch):
    store,batch,c=configured(tmp_path)
    monkeypatch.setattr('orchestrator.connectivity.require',lambda *a,**k:{'synthetic':True})
    before_policy=Accounts(store).read()[1]['policy_sha256'];original=None
    for i,stage in enumerate(list(manual_driver.STAGES)*4):
        ident,n,receipt=store.reserve_call('synthetic',stage,'a'*40,'astra/manual-test',policy(),{})
        store.finish_call(ident,receipt,'COMPLETE')
        if i==1:original=[dict(x) for x in store.db.execute('SELECT * FROM manual_calls ORDER BY rowid LIMIT 2')]
    assert [dict(x) for x in store.db.execute('SELECT * FROM manual_calls ORDER BY rowid LIMIT 2')]==original
    account=Accounts(store).read()[1]
    assert account['count']==16 and account['policy_sha256']==before_policy and account['resets']==[]
    with pytest.raises(ValueError,match='^STEP_D_MODEL_CALL_LIMIT$'):
        store.reserve_call('synthetic','run_spec_author','a'*40,'astra/manual-test',policy(),{})
    assert store.db.execute('SELECT count(*) FROM manual_calls').fetchone()[0]==16
    assert batch.db.execute('SELECT count(*) FROM autonomy_calls').fetchone()[0]==16


def test_existing_halt_is_not_cleared_by_limit_amendment(tmp_path):
    store,batch,c=configured(tmp_path);version,state=Accounts(store).read();state['halted']=True
    assert Accounts(store).cas(version,state)
    event={'run_id':'a'*64,'attempt':'1','source':'b'*40,'branch':'astra/manual-test'}
    result=dispatch_limiter.admit_manual(Accounts(store),policy(),event,allowance={'authority_sha256':limits.AUTHORITY,'run_limit':16})
    assert result['status']=='HALTED_OPERATOR_RESET_REQUIRED'
    assert Accounts(store).read()[1]['count']==0


@pytest.mark.parametrize('n,next_stage',[(1,'run_spec_author'),(2,'run_spec_author'),(3,'run_spec_author'),(4,'BLOCKED')])
def test_exactly_three_revisions(n,next_stage):
    value={'verdict':'REVISE','findings':[{'category':'metric/statistic'}]}
    assert revisions.review_transition(value,'run_spec_review',n)[0]==next_stage


@pytest.mark.parametrize('category',['privacy/secret','test-set/leakage','budget'])
def test_reserved_decision_still_stops(category):
    assert revisions.review_transition({'verdict':'REVISE','findings':[{'category':category}]},'run_spec_review',1)[1]=='REVIEW_REQUIRES_OPERATOR_DECISION'


def test_reject_and_empty_revise_stop():
    assert revisions.review_transition({'verdict':'REJECT','findings':[]},'run_spec_review',1)[1]=='REVIEW_REJECTED'
    assert revisions.review_transition({'verdict':'REVISE','findings':[]},'run_spec_review',1)[0]=='BLOCKED'


def test_same_role_limit_does_not_retry_uncertain_calls(tmp_path,monkeypatch):
    store,batch,c=configured(tmp_path)
    monkeypatch.setattr('orchestrator.connectivity.require',lambda *a,**k:{'synthetic':True})
    ident,n,receipt=store.reserve_call('synthetic','run_spec_author','a'*40,'astra/manual-test',policy(),{})
    store.finish_call(ident,receipt,'UNCERTAIN')
    with pytest.raises(ValueError,match='^UNCERTAIN_MODEL_CALL_NO_RETRY$'):
        store.reserve_call('synthetic','run_spec_author','a'*40,'astra/manual-test',policy(),{})
    assert Accounts(store).read()[1]['count']==1


def test_scoped_finding_never_overwrites_prior_run_or_round(lane):
    d=manual_driver.Driver(lane);d.config['run_id']='run-one'
    legacy=b'{"verdict":"REVISE","rationale":"Synthetic old finding"}'
    d.criticism('run_spec_review',1,legacy)
    registry_path=d.context/manual_driver.PROFILE/'obligations.json'
    old=read(registry_path);old_rows=list(old['obligations'])
    d.config['run_id']='run-two';raw=b'{"verdict":"REVISE","rationale":"Synthetic new finding"}'
    d.criticism('run_spec_review',1,raw);first=registry_path.read_bytes()
    d.criticism('run_spec_review',1,raw)
    assert registry_path.read_bytes()==first
    assert read(registry_path)['obligations'][:-1]==old_rows
    with pytest.raises(ValueError,match='^EXISTING_FINDING_CONFLICT$'):
        d.criticism('run_spec_review',1,raw+b' ')
    assert registry_path.read_bytes()==first
    d.criticism('run_spec_review',2,raw)
    assert len(read(registry_path)['obligations'])==len(old_rows)+2


def test_approval_closes_only_own_run_and_stage(lane):
    d=manual_driver.Driver(lane);own=d.config['run_id']
    d.config['run_id']='unrelated';d.criticism('run_spec_review',1,b'{"verdict":"REVISE"}')
    d.config['run_id']=own;d.criticism('run_spec_review',1,b'{"verdict":"REVISE"}')
    d.criticism('result_interpretation_review',1,b'{"verdict":"REVISE"}')
    work=lane/'synthetic-review';private_records.mkdir(work)
    raw=b'{"verdict":"APPROVE","rationale":"Synthetic approval"}'
    private_records.write_bytes(work/'review.json',raw)
    receipt={'output_sha256':{'review.json':digest(raw)}}
    d.store.db.execute('INSERT INTO manual_calls VALUES(?,?,?,?,?)',('synthetic','run_spec_review',2,'COMPLETE',json.dumps(receipt)))
    value=d.current();value['pending']={'id':'synthetic','stage':'run_spec_review','round':2,'workspace':str(work)}
    assert d._accept_completed(value)['phase']=='COMMIT_SPEC'
    found=read(d.context/manual_driver.PROFILE/'obligations.json')['obligations']
    rows=[x for x in found if x['id'].startswith('STEPD-')]
    assert [x['status'] for x in rows]==['open','closed','open']
    assert rows[1]['disposition']['sha256']==digest(raw)


def test_checkpoint_rows_use_recorded_primary_key_order_and_compact_json(tmp_path):
    import sqlite3
    from orchestrator.analysis_revision_transition import rows, sha
    db=sqlite3.connect(':memory:');db.row_factory=sqlite3.Row
    db.execute('CREATE TABLE manual_calls(id TEXT PRIMARY KEY, value TEXT)')
    db.execute("INSERT INTO manual_calls VALUES('z','later')")
    db.execute("INSERT INTO manual_calls VALUES('a','first')")
    expected=[{'id':'a','value':'first'},{'id':'z','value':'later'}]
    assert rows(db,'manual_calls')==expected
    assert sha(expected)==digest(b'[{"id":"a","value":"first"},{"id":"z","value":"later"}]')
    with pytest.raises(ValueError,match='^REVISION_TABLE_REQUIRED$'):rows(db,'unbound')
