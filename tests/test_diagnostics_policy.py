"""Synthetic ledger checks only; no model, data execution or provider call."""
import copy
import json
from datetime import datetime, timezone
import pytest
from orchestrator import diagnostics_policy as dp, autonomy_limits as limits, private_records
from orchestrator.autonomy_accounting import BatchAccounts
from orchestrator.manual_executor import atomic


def config():
    return {'run_id': dp.RUN_ID, 'item_number': 6, 'backend': 'cpu', 'diagnostics': dp.policy()}


def batch(tmp_path):
    state = tmp_path/'lane'
    private_records.mkdir(state)
    atomic(state/'lane.json', config())
    b = BatchAccounts(tmp_path/'ledger', filesystem_root=tmp_path)
    b.register_run(dp.RUN_ID, {'state': '/lane'})
    return b


def seed(b, count, *, run=None, kind='scientific', day='2020-01-01'):
    for i in range(count):
        b.db.execute('INSERT INTO autonomy_calls VALUES(?,?,?,?,?,?,?,?)',
            ('old-'+str(i), kind, run or dp.RUN_ID, i+1, day, 'FAILED', '{}', '{}'))


def test_exact_operator_authority_and_shared_allowance():
    assert dp.authority() == dp.AUTHORITY
    assert dp.validate_config(config(), dp.RUN_ID) == 30
    assert dp.TOTAL_MICRO_USD == 100_000_000
    assert len(dp.DIAGNOSTICS) == 5
    assert limits.selected_run_limit(config(), dp.RUN_ID) == 30
    # Unrelated global limits and the revision ceiling remain unchanged.
    assert (limits.DAILY, limits.SCIENTIFIC_BATCH, limits.REVISE_ROUNDS) == (30, 60, 3)


@pytest.mark.parametrize('key,value', [('run_id','another-run'), ('item_number',True),
    ('item_number',4), ('backend','modal'), ('backend','analysis'), ('diagnostics',{})])
def test_scope_mismatch_refuses(key,value):
    c=config(); c[key]=value
    with pytest.raises(ValueError,match='^DIAGNOSTICS_SCOPE_OR_ALLOWANCE_BINDING$'):
        dp.validate_config(c,dp.RUN_ID)


@pytest.mark.parametrize('key,value', [('operator_sha256','f'*64), ('item_sha256','f'*64),
    ('scientific_call_limit',31), ('scientific_call_limit',30.0), ('total_micro_usd',100_000_001),
    ('cpu_only',False), ('cpu_only',1), ('training',True), ('diagnostics',['calibration'])])
def test_no_per_diagnostic_split_or_changed_controls(key,value):
    c=config(); c['diagnostics'][key]=value
    with pytest.raises(ValueError,match='^DIAGNOSTICS_SCOPE_OR_ALLOWANCE_BINDING$'):
        dp.validate_config(c,dp.RUN_ID)


def test_release_backlog_revision_or_execution_group_does_not_reset_owner(tmp_path):
    b=batch(tmp_path)
    c=config(); c.update(source='f'*40,backlog={'sha256':'e'*64},execution_group='first-two')
    assert limits.selected_run_limit(c,dp.RUN_ID)==30
    before=[tuple(row) for row in b.db.execute('SELECT * FROM autonomy_runs')]
    with pytest.raises(ValueError,match='^BATCH_RUN_BINDING_CHANGED$'):
        b.register_run(dp.RUN_ID,{'state':'/other-lane'})
    assert [tuple(row) for row in b.db.execute('SELECT * FROM autonomy_runs')]==before
    c['run_id']='diagnostics-second-group'
    with pytest.raises(ValueError,match='^DIAGNOSTICS_SCOPE_OR_ALLOWANCE_BINDING$'):
        limits.selected_run_limit(c,c['run_id'])


def test_thirty_is_shared_and_preserves_historical_failures(tmp_path):
    b=batch(tmp_path);seed(b,29)
    before=[tuple(row) for row in b.db.execute('SELECT * FROM autonomy_calls ORDER BY rowid')]
    result=b.reserve_scientific('thirtieth',dp.RUN_ID,'run_spec_author','a'*40,{})
    assert result['run_limit']==30 and result['batch_limit']==60 and result['daily_limit']==30
    b.finish_scientific('thirtieth',{},'COMPLETE')
    assert [tuple(row) for row in b.db.execute('SELECT * FROM autonomy_calls ORDER BY rowid LIMIT 29')]==before
    with pytest.raises(ValueError,match='^AUTONOMY_RUN_CALL_LIMIT$'):
        b.reserve_scientific('thirty-first',dp.RUN_ID,'run_spec_review','a'*40,{})
    assert b.db.execute('SELECT count(*) FROM autonomy_calls').fetchone()[0]==30


@pytest.mark.parametrize('cause', ['day','batch','halt','uncertain'])
def test_existing_global_refusals_still_apply(tmp_path,cause):
    b=batch(tmp_path)
    if cause=='day':
        seed(b,30,kind='implementation_review',run='administrative',day=datetime.now(timezone.utc).date().isoformat())
        expected='AUTONOMY_DAILY_CALL_LIMIT'
    elif cause=='batch':
        seed(b,60,run='prior-run');expected='AUTONOMY_BATCH_CALL_LIMIT'
    elif cause=='halt':
        private_records.write_text(b.folder/'HALT','synthetic stop');expected='AUTONOMY_BATCH_HALTED'
    else:
        seed(b,1);b.db.execute("UPDATE autonomy_calls SET status='UNCERTAIN'");expected='BATCH_UNCERTAIN_OR_RUNNING_CALL'
    before=[tuple(row) for row in b.db.execute('SELECT * FROM autonomy_calls ORDER BY rowid')]
    with pytest.raises(ValueError,match='^'+expected+'$'):
        b.reserve_scientific('blocked',dp.RUN_ID,'run_spec_author','a'*40,{})
    assert [tuple(row) for row in b.db.execute('SELECT * FROM autonomy_calls ORDER BY rowid')]==before


def test_altered_or_symlink_authority_refused(tmp_path):
    folder=tmp_path/'docs';folder.mkdir()
    p=folder/'DIAGNOSTICS_OPERATOR_DECISION.txt';p.write_text('altered authority')
    with pytest.raises(ValueError,match='^DIAGNOSTICS_OPERATOR_AUTHORITY_CHANGED$'):dp.authority(tmp_path)
    p.unlink();p.symlink_to(__import__('pathlib').Path(dp.__file__).resolve().parents[1]/dp.DOCUMENT)
    with pytest.raises(ValueError,match='^DIAGNOSTICS_OPERATOR_AUTHORITY_CHANGED$'):dp.authority(tmp_path)


def test_actual_local_and_global_reservation_use_item6_authority(tmp_path, monkeypatch):
    from orchestrator.manual_executor import ManualExecutor, Accounts
    from test_manual_lane import policy
    b=batch(tmp_path)
    store=ManualExecutor(tmp_path/'lane/jobs.sqlite',batch=b);store.initialize_allowance(policy())
    monkeypatch.setattr('orchestrator.connectivity.require',lambda *a,**k:{'synthetic':True})
    ident,n,receipt=store.reserve_call(dp.RUN_ID,'run_spec_author','a'*40,'astra/manual-test',policy(),{})
    assert receipt['batch_accounting']['operator_decision_sha256']==dp.AUTHORITY
    assert receipt['accounting']['limit_amendment']=={'authority_sha256':dp.AUTHORITY,'run_limit':30,'scoped_run_id':dp.RUN_ID}
    assert Accounts(store).read()[1]['count']==1
    assert b.db.execute('SELECT count(*) FROM autonomy_calls').fetchone()[0]==1
    with pytest.raises(ValueError,match='^UNCERTAIN_MODEL_CALL_NO_RETRY$'):
        store.reserve_call(dp.RUN_ID,'run_spec_author','a'*40,'astra/manual-test',policy(),{})


def test_local_cas_thirty_does_not_reset_old_policy_or_counts(tmp_path):
    from orchestrator.manual_executor import ManualExecutor, Accounts, digest
    from orchestrator import dispatch_limiter
    from test_manual_lane import policy
    b=batch(tmp_path);store=ManualExecutor(tmp_path/'lane/jobs.sqlite',batch=b);store.initialize_allowance(policy())
    original=Accounts(store).read()[1]['policy_sha256'];amendment=limits.allowance(store,dp.RUN_ID,policy())
    for i in range(30):
        event={'run_id':digest(str(i).encode()),'attempt':'1','source':'a'*40,'branch':'astra/manual-test'}
        assert dispatch_limiter.admit_manual(Accounts(store),policy(),event,allowance=amendment)['status']=='ADMITTED'
    account=Accounts(store).read()[1]
    assert account['count']==30 and account['policy_sha256']==original and account['resets']==[]
    result=dispatch_limiter.admit_manual(Accounts(store),policy(),{**event,'run_id':digest(b'excess')},allowance=amendment)
    assert result['status']!='ADMITTED' and Accounts(store).read()[1]['count']==30


@pytest.mark.parametrize('change', [{'scoped_run_id':'another-run'}, {'authority_sha256':limits.AUTHORITY}, {'run_limit':30.0}])
def test_local_thirty_amendment_is_not_a_general_override(tmp_path,change):
    from orchestrator.manual_executor import ManualExecutor,Accounts,digest
    from orchestrator import dispatch_limiter
    from test_manual_lane import policy
    b=batch(tmp_path);store=ManualExecutor(tmp_path/'lane/jobs.sqlite',batch=b);store.initialize_allowance(policy())
    amendment={**limits.allowance(store,dp.RUN_ID,policy()),**change}
    with pytest.raises(ValueError,match='^MANUAL_LIMIT_AMENDMENT_BINDING$'):
        dispatch_limiter.admit_manual(Accounts(store),policy(),{'run_id':digest(b'call'),'attempt':'1','source':'a'*40,'branch':'astra/manual-test'},allowance=amendment)
    assert Accounts(store).read()[1]['count']==0
