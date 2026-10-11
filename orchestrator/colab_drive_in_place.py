"""One operator-directed author/reviewer pair; original owner and eight-call cap.

No science, data transfer, credential change, or acceptance of the old timeout.
Enabled only by a source-bound installed implementation review.
"""
from contextlib import contextmanager
import hashlib,json,sqlite3,tempfile
from pathlib import Path
from orchestrator import private_records as pr

RUN='colab-1ad5fafc220b3d65f576ce08'
EVENT='colab-drive-in-place-20261011'
DOC='docs/COLAB_DRIVE_IN_PLACE_PRIVATE.json'
DOC_SHA='d8dd3d28be041e9a32bdd9d32a935a046865050743fdf4e0d7cc8dd0386bef65'
OPERATOR='docs/COLAB_DRIVE_IN_PLACE_OPERATOR.txt'
OPERATOR_SHA='6bf0a6cfca614bf45aa19ce239fa70bffe850edf1641c2fba916f8184dfb4bd1'
TASK='docs/COLAB_DRIVE_IN_PLACE_TASK.md'
TASK_SHA='e5a83f043ac8227c9cff6a426a5c514636332917855f31a867df5b90393ba763'
ROOT=Path(__file__).resolve().parents[1]
BORROWED={}
TRANSPORT_DOC='docs/COLAB_AUTHOR3_TRANSPORT_PRIVATE.json'
TRANSPORT_SHA='0c6a345004fbd74861993db9cc817db49add7f6176488985910d73e37256252b'
TRANSPORT_EVENT='colab-author3-transport-closure-20261011'
READER_DOC='docs/COLAB_FOREIGN_READER_PRIVATE.json'
READER_SHA='1eb044deb42267f7d62f3ebe2b7b13a49ff4f2a50fab1f9281dc41f0f0ba65d7'
READER_EVENT='colab-author3-foreign-reader-20261011'

def sha(raw):return hashlib.sha256(raw).hexdigest()
def canonical(v):return json.dumps(v,sort_keys=True,separators=(',',':')).encode()
def require(ok,why):
    if not ok:raise ValueError('COLAB_DRIVE_IN_PLACE_'+why)

def frozen():
    raw=pr.check(ROOT/DOC).read_bytes()
    require(sha(raw)==DOC_SHA and sha(pr.check(ROOT/OPERATOR).read_bytes())==OPERATOR_SHA
        and sha(pr.check(ROOT/TASK).read_bytes())==TASK_SHA,'DOCUMENT_CHANGED')
    f=json.loads(raw)
    require(f['schema']=='colab-drive-in-place-continuation/v1' and f['run_id']==RUN
        and f['run_limit']==8 and f['new_allowance']==0 and f['operator_sha256']==OPERATOR_SHA,'SCOPE')
    require([(r['stage'],r['attempt']) for r in f['next_calls']]==[('run_spec_author',3),('run_spec_review',4)]
        and all(r['id']==sha((RUN+':'+r['stage']+':'+str(r['attempt'])).encode()) for r in f['next_calls'])
        and len(f['local_rows'])==len(f['global_rows'])==6,'CALL_SET')
    require(sha(f['original_state_raw'].encode())==f['original_state_sha256'],'ORIGINAL_STATE_PIN')
    return f

def checkpointed(path):
    path=pr.check(path)
    for suffix in ('-wal','-shm','-journal'):
        other=path.with_name(path.name+suffix)
        require(not other.exists() and not other.is_symlink(),'UNBORROWED_JOURNAL_PRESENT')
    return path.read_bytes()

@contextmanager
def ledger_read(path):
    """Use an already-open owner connection, else snapshot a quiescent database.

    immutable=1 is only ever applied to the new private snapshot. Never ignore a
    live journal or make the read-only component's database directory writable.
    """
    path=Path(path)
    require(path.is_absolute(),'ABSOLUTE_LEDGER')
    if str(path) in BORROWED:
        db=BORROWED[str(path)]
        names=db.execute('PRAGMA database_list').fetchall()
        require(any(r[1]=='main' and Path(r[2])==path for r in names),'BORROWED_DATABASE_IDENTITY')
        yield db
        return
    raw=checkpointed(path)
    with tempfile.TemporaryDirectory(prefix='colab-history-read-') as directory:
        snapshot=Path(directory)/'snapshot.sqlite'
        with pr.open_file(snapshot,'xb') as stream:stream.write(raw)
        snapshot.chmod(0o400)
        db=sqlite3.connect(snapshot.as_uri()+'?mode=ro&immutable=1',uri=True)
        db.row_factory=sqlite3.Row
        try:
            require(db.execute('PRAGMA quick_check').fetchall()[0][0]=='ok','SNAPSHOT_INTEGRITY')
            yield db
        finally:db.close()
        require(checkpointed(path)==raw,'LEDGER_CHANGED_DURING_READ')


@contextmanager
def journal_aware_read(path):
    """Read a verified foreign ledger through SQLite, never ignore its journal.

    Only sequence_ledger_read selects this reader for an authenticated foreign
    lane. The ordinary unborrowed snapshot refusal stays unchanged.
    """
    path=pr.check(Path(path));identity=(path.stat().st_dev,path.stat().st_ino)
    def sidecars():
        for suffix in ('-wal','-shm','-journal'):
            other=path.with_name(path.name+suffix)
            if other.exists() or other.is_symlink():pr.check(other)
        require((path.stat().st_dev,path.stat().st_ino)==identity,'FOREIGN_LEDGER_REPLACED')
    def content_pins():
        sidecars()
        return {suffix:sha(pr.check(Path(str(path)+suffix)).read_bytes())
            for suffix in ('','-wal','-journal') if Path(str(path)+suffix).exists()}
    before=content_pins()
    db=sqlite3.connect(path.as_uri()+'?mode=ro',uri=True)
    db.row_factory=sqlite3.Row
    try:
        db.execute('PRAGMA query_only=ON')
        require(db.execute('PRAGMA query_only').fetchone()[0]==1,'FOREIGN_READ_ONLY')
        db.execute('BEGIN')
        require(db.execute('PRAGMA quick_check').fetchone()[0]=='ok','FOREIGN_INTEGRITY')
        yield db
        db.rollback()
        require(content_pins()==before,'FOREIGN_LEDGER_CHANGED_DURING_READ')
        sidecars()
    finally:
        db.rollback();db.close()


def sequence_ledger_read(path,f,pi):
    path=Path(path)
    if path in {Path(f['lane'])/'jobs.sqlite',Path(f['config']['batch_ledger'])/'jobs.sqlite'}:
        return ledger_read(path)
    overlay=pi._ACTIVE
    require(overlay is not None,'FOREIGN_VERIFIED_SEQUENCE_REQUIRED')
    overlay.verify();scope=overlay.scope
    require(scope['source_sha']==f['config']['source'] and scope['ledger']==f['config']['batch_ledger']
        and scope['lanes']['colab_preparation']['state']==f['lane'],'FOREIGN_SEQUENCE_BINDING')
    allowed={overlay.path(scope['lanes']['aggregate_analysis']['state'])/'jobs.sqlite',
        overlay.path(scope['item4_scope']['configuration']['path']).parent/'jobs.sqlite'}
    require(path in allowed,'FOREIGN_LEDGER_SCOPE')
    # A quiescent WAL-mode database may need writable sidecar setup for a live
    # connection. Retain the original verified snapshot when no journal exists.
    if not any(Path(str(path)+suffix).exists() or Path(str(path)+suffix).is_symlink()
            for suffix in ('-wal','-shm','-journal')):
        return ledger_read(path)
    return journal_aware_read(path)


def originals(local,batch,f):
    for db,table,rows in [(local,'manual_calls',f['local_rows']),(batch,'autonomy_calls',f['global_rows'])]:
        for expected in rows:
            row=db.execute('SELECT * FROM '+table+' WHERE id=?',(expected['id'],)).fetchone()
            require(row is not None and dict(row)==expected,'ORIGINAL_ROW_OR_CHARGE_CHANGED')
    owner=batch.execute('SELECT * FROM autonomy_runs WHERE id=?',(RUN,)).fetchone()
    require(owner is not None and dict(owner)==f['original_owner'],'ORIGINAL_OWNER_CHANGED')
    require(sha(pr.check(Path(f['lane'])/'lane.json').read_bytes())==f['config_sha256'],'CONFIG_CHANGED')

def history(local,batch,f):
    originals(local,batch,f)
    rows=[dict(r) for r in local.execute('SELECT * FROM manual_calls ORDER BY rowid')]
    global_rows=[dict(r) for r in batch.execute('SELECT * FROM autonomy_calls WHERE change_id=? ORDER BY rowid',(RUN,))]
    require(6<=len(rows)<=8 and len(rows)==len(global_rows)
        and rows[:6]==f['local_rows'] and global_rows[:6]==f['global_rows'],'HISTORY_COUNT_OR_ORDER')
    for i,(row,global_row) in enumerate(zip(rows[6:],global_rows[6:])):
        selected=f['next_calls'][i]
        require(all(row[k]==selected[k] for k in ('id','stage','attempt'))
            and global_row['id']==row['id'] and global_row['kind']=='scientific'
            and global_row['change_id']==RUN and global_row['round']==7+i,'EXACT_SUCCESSOR_ONLY')
        binding=json.loads(global_row['binding'])
        require(binding['source']==f['config']['source'] and binding['run_id']==RUN
            and binding['stage']==row['stage'],'SUCCESSOR_ADMISSION_BINDING')
        require(row['status']==global_row['status'] and row['status'] in {'RUNNING','COMPLETE','FAILED','UNCERTAIN','BLOCKED_BEFORE_MODEL'},'SUCCESSOR_STATUS')
        # The normal admission writes local accounting after its global receipt.
        # Only completed results require identical final local/global receipts.
        if row['status'] in {'COMPLETE','FAILED','UNCERTAIN'}:
            require(json.loads(row['receipt'])==json.loads(global_row['receipt']),'SUCCESSOR_RECEIPT')
        if i:require(rows[6]['status']=='COMPLETE','AUTHOR_MUST_COMPLETE_FIRST')
    return rows

def live(f):
    with ledger_read(Path(f['lane'])/'jobs.sqlite') as local, ledger_read(Path(f['config']['batch_ledger'])/'jobs.sqlite') as batch:
        return history(local,batch,f)

def grant(f,approval):
    require(isinstance(approval,str) and len(approval)==64 and all(c in '0123456789abcdef' for c in approval),'APPROVAL_PIN')
    return {'kind':EVENT,'scope_sha256':DOC_SHA,'operator_sha256':OPERATOR_SHA,
        'review_sha256':approval,'preserved_calls':6,'run_limit':8,'new_allowance':0,
        'next_calls':f['next_calls'],'scientific_acceptance':False}

def granted(f,approval):
    rows=live(f)
    with ledger_read(Path(f['lane'])/'jobs.sqlite') as local:
        row=local.execute('SELECT payload FROM events WHERE id=?',(EVENT,)).fetchone()
        require(row is not None and json.loads(row[0])==grant(f,approval),'GRANT_REQUIRED')
    return rows

def terminal_history(f,terminal_f):
    live(f)
    require(terminal_f['lane']==f['lane'] and terminal_f['local_row']==f['local_rows'][-1]
        and terminal_f['global_row']==f['global_rows'][-1]
        and terminal_f['state_sha256']==f['original_state_sha256'],'HISTORICAL_TERMINAL_BINDING')
    # Historical state is immutable; current six rows are still compared exactly.
    return f['local_rows'][-1],f['original_state_raw']

def activate(driver,f,approval,terminal):
    store=driver.store;originals(store.db,store.batch.db,f)
    raw=store.db.execute('SELECT payload FROM manual_state WHERE id=1').fetchone()[0]
    require(raw==f['original_state_raw'] and len(live(f))==6,'EXACT_ACTIVATION_STATE')
    require(not store.batch.db.execute("SELECT 1 FROM autonomy_calls WHERE status='RUNNING'").fetchone(),'ACTIVE_CALL')
    terminal.qualify(f['global_rows'][-1])
    require(not store.db.execute('SELECT 1 FROM events WHERE id=?',(EVENT,)).fetchone(),'ALREADY_ACTIVATED')
    for row in f['next_calls']:
        require(not (Path(f['config']['workspace_root'])/(row['stage']+'-'+str(row['attempt']))).exists(),'SUCCESSOR_WORKSPACE_EXISTS')
    target=driver.state/EVENT;require(not target.exists() and not target.is_symlink(),'INTENT_EXISTS_RECONCILE')
    pr.mkdir(target);pr.write_bytes(target/'original-state.json',raw.encode())
    value=json.loads(raw);binding=grant(f,approval);pr.write_bytes(target/'intent.json',canonical(binding))
    driver.artifact(value,'question','colab-drive-in-place-operator.txt',pr.check(ROOT/OPERATOR).read_bytes(),3)
    driver.artifact(value,'question','colab-drive-in-place-task.md',pr.check(ROOT/TASK).read_bytes(),4)
    value.pop('pending');value.pop('blocked_stage',None)
    value.update(phase='run_spec_author',reason=None,linked_recovery_of=f['local_rows'][-1]['id'])
    value['interventions'].append(binding)
    store.db.execute('BEGIN IMMEDIATE')
    try:
        require(store.db.execute('SELECT payload FROM manual_state WHERE id=1').fetchone()[0]==raw,'STATE_RACE')
        originals(store.db,store.batch.db,f)
        store.db.execute('INSERT INTO events VALUES(?,?,?)',(EVENT,RUN,canonical(binding).decode()))
        store.db.execute('UPDATE manual_state SET payload=? WHERE id=1',(json.dumps(value,sort_keys=True),))
        store.db.execute('COMMIT')
    except BaseException:store.db.execute('ROLLBACK');raise
    pr.write_bytes(target/'COMPLETE.json',canonical(binding))
    return {'status':'AUTHOR3_READY_NO_CALL','preserved_calls':6,'new_allowance':0,'model_calls':0,'provider_calls':0}

def transport_checkpoint():
    raw=pr.check(ROOT/TRANSPORT_DOC).read_bytes()
    require(sha(raw)==TRANSPORT_SHA,'TRANSPORT_CHECKPOINT_CHANGED')
    value=json.loads(raw)
    require(value['schema']=='colab-author3-unadmitted-transport/v1' and value['model_calls']==0
        and value['automatic_retry'] is False,'TRANSPORT_SCOPE')
    return value

def rearm_transport(driver,f,approval,terminal):
    """Restore one proven unadmitted preparation; never consume/reset an attempt."""
    import subprocess
    proof=transport_checkpoint();store=driver.store
    require(len(granted(f,approval))==6 and proof['rows']==f['local_rows'],'TRANSPORT_NO_CALL')
    terminal.qualify(f['global_rows'][-1])
    state=dict(line.split('=',1) for line in subprocess.check_output(['systemctl','show',proof['unit'],
        '-p','MainPID','-p','ActiveState','-p','SubState','-p','ExecMainStatus'],text=True,timeout=15).splitlines())
    require(state=={'MainPID':'0','ActiveState':'inactive','SubState':'dead','ExecMainStatus':'0'},'TRANSPORT_TERMINAL')
    raw=store.db.execute('SELECT payload FROM manual_state WHERE id=1').fetchone()[0]
    require(raw==proof['state_raw'] and sha(raw.encode())==proof['state_sha256'],'TRANSPORT_STATE_CHANGED')
    value=json.loads(raw);work=Path(proof['workspace']);probe=Path(proof['probe'])
    require(value.get('phase')=='BLOCKED' and value.get('blocked_stage')=='run_spec_author'
        and value.get('reason')=='ValueError: PRE_ADMISSION_TRANSPORT_REFUSED:'+str(probe)
        and not value.get('pending') and work==Path(f['config']['workspace_root'])/'run_spec_author-3',
        'TRANSPORT_EXACT_PREMODEL_REFUSAL')
    observed={}
    for root in (work,probe):
        pr.check_tree(root)
        for path in root.rglob('*'):
            if path.is_file():
                body=pr.check(path).read_bytes();observed[str(path)]={'bytes':len(body),'sha256':sha(body)}
    require(observed==proof['files'],'TRANSPORT_ORIGINAL_FILES_CHANGED')
    require(not any((work/n).exists() for n in ('.git','stage_provenance.jsonl','console.log','sent-input.json',
        'SPEC.proposed.md','notebook.patch.json')),'TRANSPORT_NATIVE_OR_OUTPUT_EXISTS')
    require(not store.batch.db.execute("SELECT 1 FROM autonomy_calls WHERE status='RUNNING'").fetchone(),'ACTIVE_CALL')
    target=driver.state/TRANSPORT_EVENT;require(not target.exists() and not target.is_symlink(),'TRANSPORT_REARM_ALREADY_ATTEMPTED')
    record={'kind':TRANSPORT_EVENT,'checkpoint_sha256':TRANSPORT_SHA,'continuation_review_sha256':approval,
        'preserved_calls':6,'new_allowance':0,'model_calls':0,'same_next_call':f['next_calls'][0]['id']}
    pr.mkdir(target);pr.write_bytes(target/'original-state.json',raw.encode());pr.write_bytes(target/'intent.json',canonical(record))
    value.pop('blocked_stage');value.update(phase='run_spec_author',reason=None);value['interventions'].append(record)
    store.db.execute('BEGIN IMMEDIATE')
    try:
        require(store.db.execute('SELECT payload FROM manual_state WHERE id=1').fetchone()[0]==raw,'TRANSPORT_STATE_RACE')
        originals(store.db,store.batch.db,f)
        store.db.execute('INSERT INTO events VALUES(?,?,?)',(TRANSPORT_EVENT,RUN,canonical(record).decode()))
        store.db.execute('UPDATE manual_state SET payload=? WHERE id=1',(json.dumps(value,sort_keys=True),));store.db.execute('COMMIT')
    except BaseException:store.db.execute('ROLLBACK');raise
    pr.write_bytes(target/'COMPLETE.json',canonical(record))
    return {'status':'UNADMITTED_AUTHOR3_REARMED_NO_CALL','preserved_calls':6,'model_calls':0,'provider_calls':0,'new_allowance':0}



def reader_checkpoint():
    raw=pr.check(ROOT/READER_DOC).read_bytes()
    require(sha(raw)==READER_SHA,'READER_CHECKPOINT_CHANGED')
    proof=json.loads(raw)
    require(proof['schema']=='colab-author3-foreign-reader-recovery/v1' and proof['model_calls']==0
        and proof['new_allowance']==0,'READER_SCOPE')
    return proof


def rearm_reader(driver,f,approval,terminal):
    import subprocess
    proof=reader_checkpoint();store=driver.store
    require(len(granted(f,approval))==6 and proof['rows']==f['local_rows'],'READER_NO_CALL')
    terminal.qualify(f['global_rows'][-1])
    state=dict(line.split('=',1) for line in subprocess.check_output(['systemctl','show',proof['unit'],
        '-p','MainPID','-p','ActiveState','-p','SubState','-p','ExecMainStatus'],text=True,timeout=15).splitlines())
    require(state=={'MainPID':'0','ActiveState':'inactive','SubState':'dead','ExecMainStatus':'0'},'READER_TERMINAL')
    raw=store.db.execute('SELECT payload FROM manual_state WHERE id=1').fetchone()[0]
    require(raw==proof['state_raw'] and sha(raw.encode())==proof['state_sha256'],'READER_STATE_CHANGED')
    value=json.loads(raw);work=Path(proof['workspace'])
    require(value.get('phase')=='BLOCKED' and value.get('blocked_stage')=='run_spec_author'
        and value.get('reason')=='ValueError: COLAB_DRIVE_IN_PLACE_UNBORROWED_JOURNAL_PRESENT'
        and not value.get('pending') and work==Path(f['config']['workspace_root'])/'run_spec_author-3','READER_EXACT_PREMODEL_REFUSAL')
    pr.check_tree(work);observed={}
    for path in work.rglob('*'):
        if path.is_file():
            body=pr.check(path).read_bytes();observed[str(path)]={'bytes':len(body),'sha256':sha(body)}
    require(observed==proof['files'],'READER_ORIGINAL_FILES_CHANGED')
    require(not any((work/n).exists() for n in ('.git','stage_provenance.jsonl','console.log','sent-input.json',
        'SPEC.proposed.md','notebook.patch.json')),'READER_NATIVE_OR_OUTPUT_EXISTS')
    require(not store.batch.db.execute("SELECT 1 FROM autonomy_calls WHERE status='RUNNING'").fetchone(),'ACTIVE_CALL')
    target=driver.state/READER_EVENT;require(not target.exists() and not target.is_symlink(),'READER_REARM_ALREADY_ATTEMPTED')
    record={'kind':READER_EVENT,'checkpoint_sha256':READER_SHA,'continuation_review_sha256':approval,
        'preserved_calls':6,'new_allowance':0,'model_calls':0,'same_next_call':f['next_calls'][0]['id']}
    pr.mkdir(target);pr.write_bytes(target/'original-state.json',raw.encode());pr.write_bytes(target/'intent.json',canonical(record))
    value.pop('blocked_stage');value.update(phase='run_spec_author',reason=None);value['interventions'].append(record)
    store.db.execute('BEGIN IMMEDIATE')
    try:
        require(store.db.execute('SELECT payload FROM manual_state WHERE id=1').fetchone()[0]==raw,'READER_STATE_RACE')
        originals(store.db,store.batch.db,f)
        store.db.execute('INSERT INTO events VALUES(?,?,?)',(READER_EVENT,RUN,canonical(record).decode()))
        store.db.execute('UPDATE manual_state SET payload=? WHERE id=1',(json.dumps(value,sort_keys=True),));store.db.execute('COMMIT')
    except BaseException:store.db.execute('ROLLBACK');raise
    pr.write_bytes(target/'COMPLETE.json',canonical(record))
    return {'status':'UNADMITTED_AUTHOR3_READER_REARMED_NO_CALL','preserved_calls':6,'model_calls':0,'provider_calls':0,'new_allowance':0}


def install_hook(module,terminal,pi,reader,approval,action):
    require(action in {'verify','recover','ready','advance','rearm','rearm-reader'},'ACTION')
    f=frozen();grant(f,approval)
    require(not BORROWED and terminal._CONTINUATION is None and pi._LOCAL_READER is None,'ALREADY_CONNECTED')
    terminal._CONTINUATION=lambda terminal_f:terminal_history(f,terminal_f)
    pi._LOCAL_READER=lambda path:sequence_ledger_read(path,f,pi);reader._LEDGER_READER=ledger_read
    prior_extra=pi._EXTRA_ATTEMPT
    def extra(scope,run,stage,ident):
        selected=next((r for r in f['next_calls'] if (run,stage,ident)==(RUN,r['stage'],r['id'])),None)
        if selected is None:return prior_extra(scope,run,stage,ident) if prior_extra else False
        require(scope['lanes']['colab_preparation']['state']==f['lane'] and scope['source_sha']==f['config']['source'],'SEQUENCE_SCOPE')
        with ledger_read(Path(f['lane'])/'jobs.sqlite') as local:
            if local.execute('SELECT 1 FROM events WHERE id=?',(EVENT,)).fetchone() is None:return False
        granted(f,approval);return True
    pi._EXTRA_ATTEMPT=extra
    previous_terminal=pi.Overlay.terminal_ids
    def terminal_ids(self,batch,run,stage,ident,source,receipt):
        retained=previous_terminal(self,batch,run,stage,ident,source,receipt)
        if any((run,stage,ident)==(RUN,r['stage'],r['id']) for r in f['next_calls']):
            granted(f,approval);terminal.qualify(f['global_rows'][-1])
            return list(dict.fromkeys([*retained,terminal.CALL]))
        return retained
    pi.Overlay.terminal_ids=terminal_ids
    from orchestrator import manual_recovery
    prior_permit=manual_recovery.permit;prior_limit=manual_recovery.role_limit
    def permit(store,run):
        old=prior_permit(store,run)
        if run!=RUN:return old
        require(old is None and Path(store.path)==Path(f['lane'])/'jobs.sqlite','NO_OTHER_RECOVERY')
        granted(f,approval);terminal.qualify(f['global_rows'][-1])
        return {'failed_id':terminal.CALL,'preserved_failures':[terminal.CALL],'stage':'operator_directed_revision',
            'decision_sha256':OPERATOR_SHA,'runtime_source':DOC_SHA}
    manual_recovery.permit=permit
    def limit(store,run,stage):
        if run!=RUN:return prior_limit(store,run,stage)
        granted(f,approval)
        selected=next((r for r in f['next_calls'] if r['stage']==stage),None)
        require(selected is not None,'ONLY_REQUESTED_STAGES')
        return selected['attempt']
    manual_recovery.role_limit=limit
    previous_command=reader.review_command
    def review_command(driver,work,stage,argv,old_f,old_approval):
        if (driver.current().get('pending') or {}).get('id')!=f['next_calls'][1]['id']:
            return previous_command(driver,work,stage,argv,old_f,old_approval)
        rows=granted(f,approval)
        require(stage=='run_spec_review' and Path(work)==Path(f['config']['workspace_root'])/'run_spec_review-4'
            and len(rows)==8 and rows[-1]['status']=='RUNNING' and rows[-2]['status']=='COMPLETE','REVIEW4_ADMITTED')
        require(argv.count('--max-turns')==1 and argv[argv.index('--max-turns')+1]=='30','REVIEW_COMMAND')
        result=list(argv);result[result.index('--max-turns')+1]='60';return result
    reader.review_command=review_command
    original=module.AnalysisDriver
    class DriveRevision(original):
        def __init__(self,*args,**kwargs):
            super().__init__(*args,**kwargs)
            require(self.config['run_id']==RUN and str(self.state)==f['lane'],'DRIVER_LANE')
            for path,db in [(self.store.path,self.store.db),(self.store.batch.folder/'jobs.sqlite',self.store.batch.db)]:
                require(str(path) not in BORROWED,'DUPLICATE_OWNER_CONNECTION');BORROWED[str(path)]=db
        def model_round_number(self,value):
            granted(f,approval)
            selected=next((r for r in f['next_calls'] if r['stage']==value.get('phase')),None)
            require(selected is not None,'ONLY_REQUESTED_STAGES')
            n=self.store.db.execute('SELECT count(*) FROM manual_calls WHERE stage=?',(selected['stage'],)).fetchone()[0]+1
            require(n==selected['attempt'],'NO_EXTRA_ATTEMPT');return n
        def task(self,stage,value):
            return super().task(stage,value)+'\nLATEST OPERATOR DIRECTION (supersedes prior input-copy and 1001-unit ceiling instructions):\n'+pr.check(ROOT/OPERATOR).read_text()+'\n'+pr.check(ROOT/TASK).read_text()
        def advance(self,*args,**kwargs):
            from orchestrator.manual_executor import lock
            if action=='advance':
                granted(f,approval)
                require(self.current()['phase'] in {'run_spec_author','run_spec_review','MODEL_RUNNING'},'HOLD_AFTER_SCIENTIFIC_REVIEW')
                return super().advance(*args,**kwargs)
            with lock(self.state/'one-run.lock'),lock(self.state/'driver.lock'):
                self.guard();live(f);terminal.qualify(f['global_rows'][-1])
                if action=='recover':return activate(self,f,approval,terminal)
                if action=='rearm':return rearm_transport(self,f,approval,terminal)
                if action=='rearm-reader':return rearm_reader(self,f,approval,terminal)
                if action=='ready':granted(f,approval)
                return {'status':'VERIFIED_HELD' if action=='verify' else 'READY_DRIVE_REVISION','model_calls':0,'provider_calls':0}
    module.AnalysisDriver=DriveRevision
