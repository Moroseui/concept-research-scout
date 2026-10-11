"""One mechanically failed Colab review, preserved and normally counted."""
import hashlib,json
from pathlib import Path
from orchestrator import private_records as pr,review_submission as rs
RUN='colab-1ad5fafc220b3d65f576ce08'
FAILED='9de9a78c3891d4b666cf0901ad204030f725855dcb0083e3c1eb2982a8650a03'
STAGE='run_spec_review'
EVENT='colab-reader-recovery-20261011'
REASON='REVIEW_SUBMISSION_FAILED_NO_RETRY: ACCEPTED_SUBMISSION_REQUIRED'
DOCUMENT='docs/COLAB_READER_RECOVERY_PRIVATE.json'
DOCUMENT_SHA='c18756f5861cf0ad0eb34cfe9f3c7beb36dfcc9f8c20af20977018fc321cce85'

def sha(raw):return hashlib.sha256(raw).hexdigest()
def canonical(value):return json.dumps(value,sort_keys=True,separators=(',',':')).encode()
def require(ok,why):
    if not ok:raise ValueError('COLAB_READER_RECOVERY_'+why)

def shape(f):
    require(f['schema']=='colab-review-reader-recovery/v1' and f['run_id']==RUN and f['failed_call']==FAILED
        and (f['next_review'],f['max_turns'],f['run_limit'],f['no_new_allowance'])==(2,30,8,True),'SCOPE')
    require(len(f['local_rows'])==len(f['global_rows'])==3 and
        {r['id'] for r in f['local_rows']}=={r['id'] for r in f['global_rows']} and
        [(r['stage'],r['attempt'],r['status']) for r in f['local_rows']]==
        [('run_spec_author',1,'COMPLETE'),('run_spec_author',2,'COMPLETE'),(STAGE,1,'FAILED')]
        and f['local_rows'][-1]['id']==FAILED,'ORIGINAL_CALL_SET')

def originals(store,f):
    shape(f)
    require(Path(store.path)==Path(f['lane'])/'jobs.sqlite','EXACT_LOCAL_LEDGER')
    require(sha(pr.check(Path(store.path).parent/'lane.json').read_bytes())==f['configuration_sha256'],'CONFIG_CHANGED')
    for db,table,rows in [(store.db,'manual_calls',f['local_rows']),(store.batch.db,'autonomy_calls',f['global_rows'])]:
        for expected in rows:
            row=db.execute('SELECT * FROM '+table+' WHERE id=?',(expected['id'],)).fetchone()
            require(row is not None and dict(row)==expected,'ORIGINAL_CALL_OR_CHARGE_CHANGED')
        failed=db.execute('SELECT status,receipt FROM '+table+' WHERE id=?',(FAILED,)).fetchone()
        receipt=json.loads(failed['receipt'])
        require(failed['status']=='FAILED' and receipt['error_type']=='TerminalSubmissionFailure'
            and receipt['reason']=='ACCEPTED_SUBMISSION_REQUIRED','NOT_MECHANICAL_FAILURE')
    work=Path(f['failed_workspace']);pr.check_tree(work)
    for name,pin in f['files'].items():
        require(Path(name).name==name,'MEMBER_PATH');body=pr.check(work/name).read_bytes()
        require(len(body)==pin['bytes'] and sha(body)==pin['sha256'],'ORIGINAL_FILE_CHANGED')
    require(not (work/'review.json').exists() and not (work/rs.RECORD).exists(),'VERDICT_EXISTS')
    console=pr.check(work/'console.log').read_text()
    require(rs.terminal_without_submission(work,console),'NOT_TERMINAL')
    events=[]
    for line in console.splitlines():
        try:value=json.loads(line)
        except ValueError:continue
        if isinstance(value,dict):events.append(value)
    finals=[e for e in events if e.get('type')=='result']
    require(len(finals)==1 and finals[0].get('subtype')=='error_max_turns' and finals[0].get('num_turns')==30,'TURN_FAILURE_CHANGED')
    for event in events:
        for part in event.get('message',{}).get('content',[]):
            if isinstance(part,dict):require(not (part.get('type')=='tool_use' and 'submit_review' in part.get('name','')),'SUBMISSION_ATTEMPT')
    return True

def binding(f,approval):
    shape(f);require(isinstance(approval,str) and len(approval)==64 and all(c in '0123456789abcdef' for c in approval),'APPROVAL')
    return {'kind':EVENT,'review_sha256':approval,'checkpoint_sha256':sha(canonical(f)),
        'failed_call':FAILED,'next_review':2,'max_turns':30,'run_limit':8,'new_allowance':0,'model_calls':0}

def granted(store,f,approval):
    originals(store,f);row=store.db.execute('SELECT payload FROM events WHERE id=?',(EVENT,)).fetchone()
    require(row is not None and json.loads(row[0])==binding(f,approval),'GRANT_REQUIRED')

def activate(driver,f,approval):
    store=driver.store;originals(store,f)
    require(driver.config['run_id']==RUN,'RUN')
    require(not (driver.state/'HALT').exists() and not (store.batch.folder/'HALT').exists(),'HALT')
    raw=store.db.execute('SELECT payload FROM manual_state WHERE id=1').fetchone()[0];value=json.loads(raw)
    require(sha(raw.encode())==f['state_sha256'] and value==f['original_state'] and value['phase']=='BLOCKED'
        and value['reason']==REASON and value['pending']['id']==FAILED and value['pending']['round']==1
        and value['pending']['stage']==STAGE and value['rounds']=={'run_spec_author':2},'EXACT_FAILED_STATE')
    require(store.db.execute('SELECT count(*) FROM manual_calls').fetchone()[0]==3
        and not store.batch.db.execute("SELECT 1 FROM autonomy_calls WHERE status='RUNNING'").fetchone(),'ACTIVE_OR_NEW_CALL')
    require(not store.db.execute('SELECT 1 FROM events WHERE id=?',(EVENT,)).fetchone(),'ALREADY_APPLIED')
    require(not Path(f['failed_workspace']).with_name('run_spec_review-2').exists(),'NEXT_WORKSPACE_EXISTS')
    dest=driver.state/EVENT;require(not dest.exists() and not dest.is_symlink(),'INTENT_EXISTS_RECONCILE')
    grant=binding(f,approval);pr.mkdir(dest);pr.write_bytes(dest/'original-state.json',raw.encode());pr.write_bytes(dest/'intent.json',canonical(grant))
    value.pop('pending');value.update(phase=STAGE,reason=None,linked_recovery_of=FAILED);value['interventions'].append(grant)
    store.db.execute('BEGIN IMMEDIATE')
    try:
        require(store.db.execute('SELECT payload FROM manual_state WHERE id=1').fetchone()[0]==raw,'STATE_RACE')
        originals(store,f)
        store.db.execute('INSERT INTO events VALUES(?,?,?)',(EVENT,RUN,canonical(grant).decode()))
        store.db.execute('UPDATE manual_state SET payload=? WHERE id=1',(json.dumps(value,sort_keys=True),));store.db.execute('COMMIT')
    except BaseException:store.db.execute('ROLLBACK');raise
    pr.write_bytes(dest/'COMPLETE.json',canonical(grant));return {'status':'RESTORED_REVIEW2_NO_CALL','preserved_calls':3,'model_calls':0,'new_allowance':0}

def next_round(driver,value,f,approval,ordinary):
    if driver.config.get('run_id')!=RUN or value.get('phase')!=STAGE:return ordinary(value)
    reviews=driver.store.db.execute('SELECT id FROM manual_calls WHERE stage=?',(STAGE,)).fetchall()
    if len(reviews)!=1:return ordinary(value)
    granted(driver.store,f,approval)
    require(reviews[0][0]==FAILED and value==driver.current() and not value.get('pending')
        and value['rounds']=={'run_spec_author':2} and value.get('linked_recovery_of')==FAILED
        and driver.store.db.execute('SELECT count(*) FROM manual_calls').fetchone()[0]==3,'NEXT_REVIEW')
    require(all(value.get(k)==f['original_state'].get(k) for k in ('artifacts','spec','notebook_revision_result')),'SCIENTIFIC_STATE_CHANGED')
    return 2

def retained_review(scope,row,item,f):
    if row.get('id')!=FAILED:return False
    expected=f['global_rows'][-1]
    require(row==expected and scope['source_sha']==json.loads(expected['binding'])['source']
        and scope['lanes']['colab_preparation']['run_id']==RUN,'SEQUENCE_GLOBAL')
    lane=Path(f['lane'])
    require(Path(scope['lanes']['colab_preparation']['state'])==lane,'SEQUENCE_LANE')
    if item is not None:require(dict(item)==f['local_rows'][-1],'SEQUENCE_LOCAL')
    # Read both original ledgers. No filtered accounting view or status rewrite.
    import sqlite3
    from types import SimpleNamespace
    with sqlite3.connect((lane/'jobs.sqlite').as_uri()+'?mode=ro',uri=True) as local, \
         sqlite3.connect((Path(scope['ledger'])/'jobs.sqlite').as_uri()+'?mode=ro',uri=True) as batch:
        local.row_factory=batch.row_factory=sqlite3.Row
        originals(SimpleNamespace(db=local,path=lane/'jobs.sqlite',batch=SimpleNamespace(db=batch)),f)
    return True


def install_hook(module,f,approval,action):
    require(action in {'verify','recover','ready','advance'},'ACTION')
    from orchestrator import preparation_interleaving as pi
    require(pi._REVIEW_TERMINAL is None,'SEQUENCE_HOOK_ALREADY_SET')
    pi._REVIEW_TERMINAL=lambda scope,row,item:retained_review(scope,row,item,f)
    original=module.AnalysisDriver
    class ReviewedColabRecovery(original):
        def model_round_number(self,value):return next_round(self,value,f,approval,super().model_round_number)
        def advance(self,*args,**kwargs):
            if action=='advance':
                granted(self.store,f,approval)
                return super().advance(*args,**kwargs)
            from orchestrator.manual_executor import lock
            with lock(self.state/'one-run.lock'),lock(self.state/'driver.lock'):
                self.guard();require(self.config['run_id']==RUN,'RUN')
                if action=='recover':return activate(self,f,approval)
                originals(self.store,f)
                if action=='ready':granted(self.store,f,approval)
                return {'status':'VERIFIED_HELD' if action=='verify' else 'READY_REVIEW_RECOVERY','model_calls':0,'provider_calls':0}
    module.AnalysisDriver=ReviewedColabRecovery
    from orchestrator import stocktake_review_recovery
    prior=stocktake_review_recovery.completion
    def completion(batch,run):
        allowed=prior(batch,run)
        if run!=RUN:return allowed
        # Completion may only preserve this exact qualified terminal failure.
        # Re-open the existing local ledger read-only to authenticate the grant.
        import sqlite3
        from types import SimpleNamespace
        lane=Path(f['lane'])
        with sqlite3.connect((lane/'jobs.sqlite').as_uri()+'?mode=ro',uri=True) as db:
            db.row_factory=sqlite3.Row
            granted(SimpleNamespace(db=db,path=lane/'jobs.sqlite',batch=batch),f,approval)
        return [*(allowed or []),FAILED]
    stocktake_review_recovery.completion=completion
