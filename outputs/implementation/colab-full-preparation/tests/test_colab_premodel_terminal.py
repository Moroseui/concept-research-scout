import copy,json,sqlite3
import pytest
from orchestrator import colab_premodel_terminal as p

def arguments():
    value=p.document();v=value['original']
    raw=json.dumps(v['config']).encode()
    # The original raw formatting is a hash boundary; use a synthetic hash to
    # isolate the pure verifier without changing its production document.
    value=copy.deepcopy(value);value['original']['config_sha256']=p.sha(raw)
    row=next(r for r in v['global_calls']if r['id']==p.CALL)
    return [value,row,v['local_calls'],v['parent_state_row'],raw,v['unit'],v['workspace_files'],v['installed_source_files']]

def test_exact_original_premodel_refusal_qualifies_without_modification():
    args=arguments();before=copy.deepcopy(args)
    assert p.validate(*args)['model_client_launched']is False
    assert args==before

@pytest.mark.parametrize('kind',['row','local','state','configuration','running','source','workspace','model-evidence','binding'])
def test_changed_or_live_failure_never_qualifies(kind):
    args=copy.deepcopy(arguments())
    if kind=='row':args[1]['status']='UNCERTAIN'
    elif kind=='local':args[2][-1]['receipt']='changed'
    elif kind=='state':args[3]['payload']='{}'
    elif kind=='configuration':args[4]=b'{}'
    elif kind=='running':args[5]['MainPID']='123'
    elif kind=='source':args[7]['orchestrator/manual_executor.py']='a'*64
    elif kind=='workspace':args[6]['new.txt']='a'*64
    elif kind=='model-evidence':args[6]['sent-input.json']='a'*64
    elif kind=='binding':args[1]['binding']='{}'
    with pytest.raises((ValueError,KeyError)):p.validate(*args)

def test_reconcile_preserves_count_binding_day_and_original_local_attempt(tmp_path,monkeypatch):
    from orchestrator.autonomy_accounting import BatchAccounts
    from orchestrator import private_records as pr
    pr.mkdir(tmp_path/'ledger')
    accounts=BatchAccounts(tmp_path/'ledger')
    value=p.document();old=p.receipt(value)['original_global_row']
    accounts.db.execute('INSERT INTO autonomy_calls VALUES(?,?,?,?,?,?,?,?)',tuple(old[k]for k in ['id','kind','change_id','round','day','status','binding','receipt']))
    accounts.db.execute("INSERT INTO jobs(id,binding,phase,status)VALUES(?,?,'dispatch','RUNNING')",(p.CALL,old['binding']))
    monkeypatch.setattr(p,'qualify',lambda row,value: {'id':p.CALL,'proof_sha256':p.PIN})
    try:
        result=p.reconcile(accounts)
        assert result['accounting_units_preserved']==1
        new=dict(accounts.db.execute('SELECT *FROM autonomy_calls').fetchone())
        assert new=={**old,'status':'FAILED','receipt':json.dumps(p.receipt(value),sort_keys=True)}
        assert accounts.db.execute('SELECT count(*)FROM autonomy_calls').fetchone()[0]==1
        assert json.loads(new['receipt'])['original_local_row']['status']=='BLOCKED_BEFORE_MODEL'
        assert p.reconcile(accounts)['status']=='ALREADY_RECONCILED_NO_NEW_CALL'
        assert accounts.db.execute('SELECT count(*)FROM events').fetchone()[0]==1
    finally:accounts.db.close()

def test_other_running_call_blocks_reconciliation(tmp_path,monkeypatch):
    from orchestrator.autonomy_accounting import BatchAccounts
    from orchestrator import private_records as pr
    pr.mkdir(tmp_path/'ledger');accounts=BatchAccounts(tmp_path/'ledger')
    old=p.receipt(p.document())['original_global_row']
    accounts.db.execute('INSERT INTO autonomy_calls VALUES(?,?,?,?,?,?,?,?)',tuple(old[k]for k in ['id','kind','change_id','round','day','status','binding','receipt']))
    accounts.db.execute("INSERT INTO autonomy_calls VALUES('other','scientific','another',1,'2026-10-12','RUNNING','{}',NULL)")
    monkeypatch.setattr(p,'qualify',lambda *a:{})
    try:
        with pytest.raises(ValueError,match='OTHER_RUNNING_CALL'):p.reconcile(accounts)
        assert accounts.db.execute("SELECT count(*)FROM autonomy_calls WHERE status='RUNNING'").fetchone()[0]==2
    finally:accounts.db.close()

def history_args():
    value=copy.deepcopy(p.historical_document())
    local=next(r for r in value['local_calls']if r['id'].startswith('cef242'))
    global_row=next(r for r in value['global_calls']if r['id']==local['id'])
    raw='{"synthetic_historical_state":true}'
    terminal={'lane':value['parent_lane'],'local_row':local,'global_row':global_row,'state_sha256':p.sha(raw.encode())}
    continuation={'lane':value['parent_lane'],'local_rows':[local],'global_rows':[global_row],
                  'original_state_raw':raw,'original_state_sha256':p.sha(raw.encode())}
    config=json.dumps(value['config']).encode();plan=b'synthetic frozen plan'
    value['config_sha256']=p.sha(config);value['plan_sha256']=p.sha(plan)
    return [value,terminal,continuation,copy.deepcopy(value['local_calls']),copy.deepcopy(value['global_calls']),
            copy.deepcopy(value['parent_state_row']),config,plan]

def test_exact_eight_historical_rows_verify_independently_of_later_reservations():
    args=history_args()
    assert p.validate_historical(*args)==(args[1]['local_row'],args[2]['original_state_raw'])

@pytest.mark.parametrize('slot',[1,2,3,4,5,6,7])
def test_any_changed_historical_input_refuses(slot):
    args=history_args()
    if slot in [3,4]:args[slot][0]['receipt']='changed'
    elif slot==1:args[slot]['lane']='/changed'
    elif slot==2:args[slot]['original_state_raw']='changed'
    elif slot==5:args[slot]['payload']='changed'
    else:args[slot]=b'changed'
    with pytest.raises(ValueError):p.validate_historical(*args)

def test_read_history_keeps_later_global_call_visible_and_counted(tmp_path):
    args=history_args();value,terminal,continuation,rows,global_rows,state,config,plan=args
    lane=tmp_path/'old';lane.mkdir(mode=0o700)
    for v in [value,terminal,continuation]:
        v['parent_lane' if v is value else 'lane']=str(lane)
    (lane/'lane.json').write_bytes(config);(lane/'preparation-plan.json').write_bytes(plan)
    db=sqlite3.connect(lane/'jobs.sqlite');db.row_factory=sqlite3.Row
    db.executescript('CREATE TABLE manual_calls(id,stage,attempt,status,receipt); CREATE TABLE manual_state(id,payload);')
    for row in rows:db.execute('INSERT INTO manual_calls VALUES(?,?,?,?,?)',tuple(row[k]for k in ['id','stage','attempt','status','receipt']))
    db.execute('INSERT INTO manual_state VALUES(?,?)',(state['id'],state['payload']));db.commit();db.close()
    global_db=sqlite3.connect(':memory:');global_db.row_factory=sqlite3.Row
    global_db.execute('CREATE TABLE autonomy_calls(id,kind,change_id,round,day,status,binding,receipt)')
    for row in global_rows:global_db.execute('INSERT INTO autonomy_calls VALUES(?,?,?,?,?,?,?,?)',tuple(row[k]for k in ['id','kind','change_id','round','day','status','binding','receipt']))
    global_db.execute("INSERT INTO autonomy_calls VALUES('future','scientific','same-run',9,'2026-10-12','RUNNING','{}',NULL)")
    assert p.historical_read(global_db,terminal,continuation,value)==(terminal['local_row'],continuation['original_state_raw'])
    assert global_db.execute('SELECT count(*)FROM autonomy_calls').fetchone()[0]==9
    assert global_db.execute("SELECT status FROM autonomy_calls WHERE id='future'").fetchone()[0]=='RUNNING'
    global_db.close()
