import copy,json,sqlite3
from pathlib import Path
from types import SimpleNamespace as NS
import pytest
from orchestrator import colab_drive_in_place as m

@pytest.fixture
def ledgers(tmp_path,monkeypatch):
    monkeypatch.setattr(m,'BORROWED',{})
    f=copy.deepcopy(m.frozen());lane=tmp_path/'lane';batch_path=tmp_path/'batch';lane.mkdir(mode=0o700);batch_path.mkdir(mode=0o700)
    f['lane']=str(lane);f['config']['batch_ledger']=str(batch_path)
    f['config']['workspace_root']=str(tmp_path/'workspaces');f['config']['run_id']=m.RUN
    raw=json.dumps(f['config']).encode();(lane/'lane.json').write_bytes(raw);(lane/'lane.json').chmod(0o600);f['config_sha256']=m.sha(raw)
    def make(path,table,rows):
        db=sqlite3.connect(path,isolation_level=None);db.row_factory=sqlite3.Row;path.chmod(0o600)
        fields=list(rows[0]);types={k:('INTEGER' if isinstance(rows[0][k],int) else 'TEXT') for k in fields}
        db.execute('CREATE TABLE '+table+'('+','.join(k+' '+types[k] for k in fields)+')')
        db.executemany('INSERT INTO '+table+' VALUES('+','.join('?' for k in fields)+')',[[r[k] for k in fields] for r in rows]);return db
    local=make(lane/'jobs.sqlite','manual_calls',f['local_rows']);global_db=make(batch_path/'jobs.sqlite','autonomy_calls',f['global_rows'])
    fields=list(f['original_owner']);global_db.execute('CREATE TABLE autonomy_runs('+','.join(k+' TEXT' for k in fields)+')')
    global_db.execute('INSERT INTO autonomy_runs VALUES('+','.join('?' for k in fields)+')',[f['original_owner'][k] for k in fields])
    local.executescript('CREATE TABLE events(id TEXT PRIMARY KEY,job TEXT,payload TEXT);CREATE TABLE manual_state(id INTEGER PRIMARY KEY,payload TEXT);')
    local.execute('INSERT INTO manual_state VALUES(1,?)',(f['original_state_raw'],))
    yield NS(f=f,local=local,batch=global_db,lane=lane,batch_path=batch_path)
    local.close();global_db.close()

def add(x,index=0,status='COMPLETE'):
    f=x.f;s=f['next_calls'][index];receipt=json.dumps({'outcome':status,'original_cost_retained':True})
    row={**f['global_rows'][-1],'id':s['id'],'round':7+index,'status':status,'receipt':receipt,
        'binding':json.dumps({'source':f['config']['source'],'run_id':m.RUN,'stage':s['stage']})}
    fields=list(row);x.batch.execute('INSERT INTO autonomy_calls('+','.join(fields)+') VALUES('+','.join('?' for _ in fields)+')',[row[k] for k in fields])
    x.local.execute('INSERT INTO manual_calls(id,stage,attempt,status,receipt) VALUES(?,?,?,?,?)',(s['id'],s['stage'],s['attempt'],status,receipt))

@pytest.mark.parametrize('count',[0,1,2])
def test_exact_history_allows_only_two_counted_new_calls(ledgers,count):
    x=ledgers
    for i in range(count):add(x,i)
    assert len(m.history(x.local,x.batch,x.f))==6+count
    assert m.live(x.f)==m.history(x.local,x.batch,x.f)

@pytest.mark.parametrize('damage',['old-local','old-global','old-receipt','owner','config','unknown-id','wrong-stage','wrong-attempt','global-order','wrong-source','wrong-run','receipt','ninth','missing-global','reverse-order'])
def test_history_mutations_fail_closed(ledgers,damage):
    x=ledgers;add(x);add(x,1)
    old=x.f['local_rows'][0]['id'];new=x.f['next_calls'][0]['id']
    if damage=='old-local':x.local.execute("UPDATE manual_calls SET status='FAILED' WHERE id=?",(old,))
    elif damage=='old-global':x.batch.execute("UPDATE autonomy_calls SET status='FAILED' WHERE id=?",(old,))
    elif damage=='old-receipt':x.batch.execute("UPDATE autonomy_calls SET receipt='{}' WHERE id=?",(old,))
    elif damage=='owner':x.batch.execute("UPDATE autonomy_runs SET status='COMPLETE'")
    elif damage=='config':(x.lane/'lane.json').write_text('{}')
    elif damage=='unknown-id':x.local.execute("UPDATE manual_calls SET id='other' WHERE id=?",(new,))
    elif damage=='wrong-stage':x.local.execute("UPDATE manual_calls SET stage='result_interpretation_author' WHERE id=?",(new,))
    elif damage=='wrong-attempt':x.local.execute('UPDATE manual_calls SET attempt=4 WHERE id=?',(new,))
    elif damage=='global-order':x.batch.execute('UPDATE autonomy_calls SET round=8 WHERE id=?',(new,))
    elif damage in {'wrong-source','wrong-run'}:
        row=json.loads(x.batch.execute('SELECT binding FROM autonomy_calls WHERE id=?',(new,)).fetchone()[0]);row['source' if damage=='wrong-source' else 'run_id']='other';x.batch.execute('UPDATE autonomy_calls SET binding=? WHERE id=?',(json.dumps(row),new))
    elif damage=='receipt':x.local.execute("UPDATE manual_calls SET receipt='{}' WHERE id=?",(new,))
    elif damage=='ninth':x.local.execute("INSERT INTO manual_calls(id,stage,attempt,status,receipt) VALUES('ninth','run_spec_author',4,'COMPLETE','{}')")
    elif damage=='missing-global':x.batch.execute('DELETE FROM autonomy_calls WHERE id=?',(new,))
    else:
        x.local.execute('UPDATE manual_calls SET rowid=rowid+100 WHERE id=?',(new,))
    with pytest.raises(ValueError):m.history(x.local,x.batch,x.f)

@pytest.mark.parametrize('status',['RUNNING','FAILED','UNCERTAIN'])
def test_review_cannot_follow_noncomplete_author(ledgers,status):
    x=ledgers;add(x,status=status);add(x,1)
    with pytest.raises(ValueError,match='AUTHOR_MUST_COMPLETE_FIRST'):m.history(x.local,x.batch,x.f)

def test_terminal_snapshot_is_historical_but_every_original_row_still_live(ledgers):
    x=ledgers;f=x.f;terminal={'lane':f['lane'],'local_row':f['local_rows'][-1],'global_row':f['global_rows'][-1],'state_sha256':f['original_state_sha256']}
    add(x);x.local.execute("UPDATE manual_state SET payload='current successor state'")
    assert m.terminal_history(f,terminal)==(f['local_rows'][-1],f['original_state_raw'])
    x.local.execute("UPDATE manual_calls SET receipt='changed' WHERE id=?",(f['local_rows'][-1]['id'],))
    with pytest.raises(ValueError,match='ORIGINAL_ROW'):m.terminal_history(f,terminal)

@pytest.mark.parametrize('suffix',['-wal','-shm','-journal'])
def test_snapshot_refuses_even_empty_or_dangling_journal(ledgers,suffix):
    x=ledgers;p=x.lane/'jobs.sqlite';side=p.with_name(p.name+suffix);side.symlink_to(x.lane/'missing')
    with pytest.raises(ValueError,match='UNBORROWED_JOURNAL'):m.checkpointed(p)
    side.unlink();side.write_bytes(b'')
    with pytest.raises(ValueError,match='UNBORROWED_JOURNAL'):m.checkpointed(p)

def test_snapshot_never_writes_source_and_detects_race(ledgers):
    x=ledgers;p=x.lane/'jobs.sqlite';before=p.read_bytes()
    with m.ledger_read(p) as db:
        with pytest.raises(sqlite3.OperationalError):db.execute('DELETE FROM manual_calls')
    assert p.read_bytes()==before and not p.with_name(p.name+'-wal').exists()
    with pytest.raises(ValueError,match='LEDGER_CHANGED_DURING_READ'):
        with m.ledger_read(p) as db:x.local.execute("UPDATE manual_state SET payload='changed'")

def test_borrowed_owner_reads_wal_without_closing_or_committing(ledgers):
    x=ledgers;p=x.lane/'jobs.sqlite';x.local.execute('PRAGMA journal_mode=WAL');x.local.execute('BEGIN IMMEDIATE')
    x.local.execute("UPDATE manual_state SET payload='uncommitted'");m.BORROWED[str(p)]=x.local
    with m.ledger_read(p) as db:
        assert db is x.local and db.in_transaction
        assert db.execute('SELECT payload FROM manual_state').fetchone()[0]=='uncommitted'
    assert x.local.in_transaction;x.local.execute('ROLLBACK')
    assert x.local.execute('SELECT payload FROM manual_state').fetchone()[0]==x.f['original_state_raw']

def test_wrong_borrowed_connection_refuses(ledgers):
    x=ledgers;m.BORROWED[str(x.lane/'jobs.sqlite')]=x.batch
    with pytest.raises(ValueError,match='BORROWED_DATABASE_IDENTITY'):
        with m.ledger_read(x.lane/'jobs.sqlite'):pass

def test_activation_is_exclusive_preserves_six_rows_and_allowance(ledgers):
    x=ledgers;f=x.f;captured=[]
    def artifact(value,kind,name,raw,version):captured.append((name,raw))
    driver=NS(state=x.lane,store=NS(db=x.local,batch=NS(db=x.batch)),artifact=artifact)
    result=m.activate(driver,f,'a'*64,NS(qualify=lambda row:captured.append(('terminal',row))))
    assert result['model_calls']==result['provider_calls']==result['new_allowance']==0
    assert len(m.granted(f,'a'*64))==6
    state=json.loads(x.local.execute('SELECT payload FROM manual_state').fetchone()[0]);assert state['phase']=='run_spec_author' and 'pending' not in state
    assert state['rounds']==json.loads(f['original_state_raw'])['rounds']
    assert (x.lane/m.EVENT/'original-state.json').read_text()==f['original_state_raw']
    with pytest.raises(ValueError):m.activate(driver,f,'a'*64,NS(qualify=lambda row:None))
    with pytest.raises(ValueError,match='GRANT_REQUIRED'):m.granted(f,'b'*64)
    assert len(m.history(x.local,x.batch,f))==6

@pytest.fixture
def hooked(ledgers,monkeypatch):
    from orchestrator import preparation_interleaving as pi,manual_recovery as recovery
    x=ledgers;f=x.f
    monkeypatch.setattr(m,'frozen',lambda:f)
    monkeypatch.setattr(pi,'_LOCAL_READER',None);monkeypatch.setattr(pi,'_EXTRA_ATTEMPT',lambda scope,run,stage,ident:False)
    monkeypatch.setattr(pi.Overlay,'terminal_ids',lambda *args:[])
    monkeypatch.setattr(recovery,'permit',lambda store,run:None)
    monkeypatch.setattr(recovery,'role_limit',lambda store,run,stage:2)
    terminal=NS(_CONTINUATION=None,CALL=f['local_rows'][-1]['id'])
    terminal.qualify=lambda row: m.terminal_history(f,{'lane':f['lane'],'local_row':f['local_rows'][-1],
        'global_row':f['global_rows'][-1],'state_sha256':f['original_state_sha256']})
    reader=NS(_LEDGER_READER=None,review_command=lambda *args: (_ for _ in ()).throw(ValueError('old command refused')))
    store=NS(path=x.lane/'jobs.sqlite',db=x.local,batch=NS(folder=x.batch_path,db=x.batch))
    class Base:
        def __init__(self):self.store=store;self.config=f['config'];self.state=x.lane
        def current(self):return json.loads(x.local.execute('SELECT payload FROM manual_state').fetchone()[0])
        def guard(self):return None
        def artifact(self,*args):return None
        def task(self,*args):return 'original exact schema and scientific context'
        def advance(self,*args,**kwargs):return 'ordinary driver'
    module=NS(AnalysisDriver=Base)
    m.install_hook(module,terminal,pi,reader,'a'*64,'advance')
    driver=module.AnalysisDriver();scope={'source_sha':f['config']['source'],'lanes':{'colab_preparation':{'state':f['lane']}}}
    return NS(x=x,driver=driver,scope=scope,pi=pi,recovery=recovery,terminal=terminal,reader=reader)

def test_hooks_require_grant_exact_stage_and_preserve_cap(hooked,monkeypatch):
    from orchestrator.manual_executor import ManualExecutor
    from orchestrator import autonomy_limits
    h=hooked;x=h.x;f=x.f;author=f['next_calls'][0];review=f['next_calls'][1]
    assert h.pi.permitted_attempts(h.scope,m.RUN,'run_spec_author')==(1,2)
    with pytest.raises(ValueError,match='GRANT_REQUIRED'):h.driver.advance()
    m.activate(h.driver,f,'a'*64,h.terminal)
    assert h.pi.permitted_attempts(h.scope,m.RUN,'run_spec_author')==(1,2,3)
    assert h.pi.permitted_attempts(h.scope,m.RUN,'run_spec_review')==(1,2,4)
    assert h.pi.permitted_attempts(h.scope,'other','run_spec_author')==(1,2)
    assert h.driver.model_round_number(h.driver.current())==3
    assert h.recovery.role_limit(h.driver.store,m.RUN,'run_spec_author')==3
    assert h.recovery.role_limit(h.driver.store,m.RUN,'run_spec_review')==4
    assert h.recovery.role_limit(h.driver.store,'other','run_spec_author')==2
    with pytest.raises(ValueError,match='ONLY_REQUESTED_STAGES'):h.recovery.role_limit(h.driver.store,m.RUN,'result_interpretation_author')
    assert h.terminal.CALL in h.recovery.permit(h.driver.store,m.RUN)['preserved_failures']
    add(x);add(x,1)
    monkeypatch.setattr(autonomy_limits,'local_limit',lambda *args:8)
    with pytest.raises(ValueError,match='STEP_D_MODEL_CALL_LIMIT'):
        ManualExecutor.reserve_call(h.driver.store,m.RUN,'run_spec_author',f['config']['source'],'astra/manual-test',{}, {})
    assert len(m.live(f))==8

def test_new_uncertain_call_is_never_excepted_or_retried(hooked):
    from orchestrator.manual_executor import ManualExecutor
    h=hooked;x=h.x;f=x.f;m.activate(h.driver,f,'a'*64,h.terminal);add(x,status='UNCERTAIN')
    with pytest.raises(ValueError,match='UNCERTAIN_MODEL_CALL_NO_RETRY'):
        ManualExecutor.reserve_call(h.driver.store,m.RUN,'run_spec_review',f['config']['source'],'astra/manual-test',{}, {})
    assert h.recovery.permit(h.driver.store,m.RUN)['preserved_failures']==[h.terminal.CALL]

def test_reviewer4_command_requires_ordinary_admission_and_holds_after(hooked):
    h=hooked;x=h.x;f=x.f;m.activate(h.driver,f,'a'*64,h.terminal);add(x);add(x,1,status='RUNNING')
    state=h.driver.current();state.update(phase='MODEL_RUNNING',pending={'id':f['next_calls'][1]['id']})
    x.local.execute('UPDATE manual_state SET payload=?',(json.dumps(state),));work=Path(f['config']['workspace_root'])/'run_spec_review-4'
    assert h.reader.review_command(h.driver,work,'run_spec_review',['reviewer','--max-turns','30'],{},'old')==['reviewer','--max-turns','60']
    with pytest.raises(ValueError):h.reader.review_command(h.driver,work,'run_spec_review',['reviewer','--max-turns','999'],{},'old')
    state['phase']='COMMIT_SPEC';x.local.execute('UPDATE manual_state SET payload=?',(json.dumps(state),))
    with pytest.raises(ValueError,match='HOLD_AFTER_SCIENTIFIC_REVIEW'):h.driver.advance()
