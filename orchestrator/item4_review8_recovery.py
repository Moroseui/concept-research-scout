"""One reviewed mechanical replacement; original calls and charges are immutable."""
import json
from pathlib import Path
from orchestrator import item4_review4_continuation as prior

DOCUMENT='docs/ITEM4_REVIEW8_MECHANICAL_RECOVERY.json'
FAILED='74841b04c11db8cfe518c04fd64a7529623b494107427b0116f30279ec900329'
EVENT='item4-review8-reader-limit-recovery-20261009'
REASON='REVIEW_SUBMISSION_FAILED_NO_RETRY: ACCEPTED_SUBMISSION_REQUIRED'
STAGE='run_spec_review'
REPLACEMENT=prior.sha((prior.RUN+':'+STAGE+':9').encode())

def require(ok,why):
    if not ok:raise ValueError('ITEM4_REVIEW8_RECOVERY_'+why)

def shape(frozen):
    require(frozen['schema']=='item4-review8-mechanical-recovery/v1' and
        frozen['run_id']==prior.RUN and frozen['failed_call']==FAILED and
        (frozen['next_review'],frozen['next_max_turns'],frozen['run_limit'])==(9,60,24) and
        (frozen['native_subtype'],frozen['native_turns'])==('error_max_turns',30) and
        len(frozen['local_calls'])==len(frozen['global_calls'])==21 and
        set(frozen['local_calls'])==set(frozen['global_calls']) and FAILED in frozen['local_calls'], 'SCOPE')

def originals(store,frozen):
    shape(frozen)
    require(prior.sha((Path(store.path).parent/'lane.json').read_bytes())==frozen['configuration_sha256'],'CONFIG')
    for db,table,key in [(store.db,'manual_calls','local_calls'),(store.batch.db,'autonomy_calls','global_calls')]:
        for ident,pin in frozen[key].items():
            row=db.execute('SELECT * FROM '+table+' WHERE id=?',(ident,)).fetchone()
            require(row is not None and prior.sha(prior.canonical(dict(row)))==pin,'ORIGINAL_CALL_OR_CHARGE_CHANGED')
    work=Path(frozen['failed_workspace'])
    from orchestrator import private_records as pr,review_submission as rs
    pr.check_tree(work)
    for name,pin in frozen['files'].items():
        require(Path(name).name==name,'FILE_NAME')
        p=work/name
        require(not p.is_symlink() and p.is_file(),'FILE_TYPE')
        raw=p.read_bytes();require(len(raw)==pin['bytes'] and prior.sha(raw)==pin['sha256'],'ORIGINAL_FILE_CHANGED')
    require(not (work/'review.json').exists() and not (work/rs.RECORD).exists(),'VERDICT_OR_SUBMISSION_EXISTS')
    events=[]
    for line in (work/'console.log').read_text().splitlines():
        try:v=json.loads(line)
        except ValueError:continue
        if isinstance(v,dict):events.append(v)
    require(rs.terminal_without_submission(work,(work/'console.log').read_text()),'NOT_TERMINAL')
    result=events[-1]
    require(result.get('subtype')=='error_max_turns' and result.get('num_turns')==30,'NOT_READER_LIMIT')
    for event in events:
        message=event.get('message',{})
        if not isinstance(message,dict):continue
        for block in message.get('content',[]):
            if isinstance(block,dict):
                require(not (block.get('type')=='tool_use' and 'submit_review' in block.get('name','')),'SUBMISSION_ATTEMPT')
    for db,table in [(store.db,'manual_calls'),(store.batch.db,'autonomy_calls')]:
        row=db.execute('SELECT status,receipt FROM '+table+' WHERE id=?',(FAILED,)).fetchone()
        receipt=json.loads(row['receipt'])
        require(row['status']=='FAILED' and receipt['error_type']=='TerminalSubmissionFailure' and
            receipt['reason']=='ACCEPTED_SUBMISSION_REQUIRED','FAILURE_CLASSIFICATION')
    return True

def binding(frozen,approval):
    shape(frozen)
    require(isinstance(approval,str) and len(approval)==64 and all(c in '0123456789abcdef' for c in approval),'APPROVAL')
    return {'schema':'reviewed-item4-reader-recovery/v1','review_sha256':approval,
        'authority_sha256':prior.AUTHORITY,'checkpoint_sha256':prior.sha(prior.canonical(frozen)),
        'failed_call':FAILED,'replacement_call':REPLACEMENT,'run_limit':24,'max_turns':60,
        'original_calls_and_charges_preserved':True}

def granted(store,frozen,approval):
    originals(store,frozen)
    row=store.db.execute('SELECT payload FROM events WHERE id=?',(EVENT,)).fetchone()
    require(row is not None and json.loads(row[0])==binding(frozen,approval),'GRANT')
    return True

def activate(driver,frozen,approval,destination):
    """Local CAS only after installed approval; no model, provider or call mutation."""
    from orchestrator import private_records as pr
    store=driver.store;originals(store,frozen)
    require(driver.config['run_id']==prior.RUN,'RUN')
    raw=store.db.execute('SELECT payload FROM manual_state WHERE id=1').fetchone()[0]
    require(prior.sha(raw.encode())==frozen['state_sha256'],'CHECKPOINT_MOVED')
    value=json.loads(raw)
    require(value['phase']=='BLOCKED' and value['reason']==REASON and
        value['pending']['id']==FAILED and value['pending']['stage']==STAGE and value['pending']['round']==8 and
        value['rounds']=={'run_spec_author':13,'run_spec_review':7},'EXACT_FAILED_STATE')
    require(store.db.execute('SELECT count(*) FROM manual_calls').fetchone()[0]==21 and
        not store.batch.db.execute("SELECT 1 FROM autonomy_calls WHERE status='RUNNING'").fetchone(),'ACTIVE_OR_NEW_CALL')
    require(not store.db.execute('SELECT 1 FROM events WHERE id=?',(EVENT,)).fetchone(),'ALREADY_APPLIED')
    destination=Path(destination);require(not destination.exists() and not destination.is_symlink(),'INTENT_EXISTS_RECONCILE')
    pr.mkdir(destination);pr.write_bytes(destination/'original-state.json',raw.encode())
    grant=binding(frozen,approval);pr.write_bytes(destination/'intent.json',prior.canonical(grant))
    value.pop('pending');value.update(phase=STAGE,reason=None,linked_recovery_of=FAILED)
    value['interventions'].append({'kind':EVENT,**grant})
    store.db.execute('BEGIN IMMEDIATE')
    try:
        require(store.db.execute('SELECT payload FROM manual_state WHERE id=1').fetchone()[0]==raw,'STATE_RACE')
        originals(store,frozen)
        store.db.execute('INSERT INTO events VALUES(?,?,?)',(EVENT,prior.RUN,prior.canonical(grant).decode()))
        store.db.execute('UPDATE manual_state SET payload=? WHERE id=1',(json.dumps(value,sort_keys=True),))
        store.db.execute('COMMIT')
    except BaseException:store.db.execute('ROLLBACK');raise
    pr.write_bytes(destination/'applied.json',prior.canonical({'status':'READY_NO_MODEL_CALL',**grant}))
    return {'status':'READY_NO_MODEL_CALL','preserved_calls':21,'model_calls':0}

def next_review(store,frozen,approval):
    granted(store,frozen,approval)
    value=prior.state(store)
    require(prior.sha(prior.canonical({k:value[k] for k in ('artifacts','notebook_revision_result','spec','review')}))==frozen['scientific_state_sha256'],'SCIENTIFIC_STATE_CHANGED')
    from orchestrator import author_revision_accounting
    author=dict(store.db.execute("SELECT * FROM manual_calls WHERE stage='run_spec_author' AND attempt=13").fetchone())
    require(author_revision_accounting._accepted(store,author),'ACCEPTED_AUTHOR')
    require(value['phase']==STAGE and not value.get('pending') and
        value['rounds']=={'run_spec_author':13,'run_spec_review':7} and
        value.get('linked_recovery_of')==FAILED and
        store.db.execute('SELECT count(*) FROM manual_calls').fetchone()[0]==21,'NEXT_REVIEW')
    return 9

def command(original,workspace,stage,store,frozen,approval):
    """Only admitted replacement9 gets60 turns; every transport/tool check survives."""
    argv=original(workspace,stage)
    if stage!=STAGE:return argv
    granted(store,frozen,approval)
    value=prior.state(store);pending=value.get('pending',{})
    expected=Path(frozen['failed_workspace']).with_name('run_spec_review-9')
    require(Path(workspace).resolve()==expected.resolve() and value['phase']=='MODEL_RUNNING' and
        pending.get('id')==REPLACEMENT and pending.get('round')==9 and pending.get('stage')==STAGE,'COMMAND_SCOPE')
    require(store.db.execute('SELECT count(*) FROM manual_calls').fetchone()[0]==22,'COMMAND_COUNT')
    for db,table in [(store.db,'manual_calls'),(store.batch.db,'autonomy_calls')]:
        row=db.execute('SELECT status FROM '+table+' WHERE id=?',(REPLACEMENT,)).fetchone()
        require(row is not None and row[0]=='RUNNING','COMMAND_ADMISSION')
    require(argv.count('--max-turns')==1 and argv[argv.index('--max-turns')+1]=='30','COMMAND_SHAPE')
    argv[argv.index('--max-turns')+1]='60'
    return argv


def model_attempt(driver,value,frozen,approval,ordinary):
    """Select the already-granted attempt, never falsify an accepted counter."""
    if driver.config.get('run_id')!=prior.RUN or value.get('phase')!=STAGE:
        return ordinary(value)
    require(value==prior.state(driver.store),'MODEL_STATE_CHANGED')
    return next_review(driver.store,frozen,approval)


def restore_pre_admission(driver,frozen,grant_review,implementation_review,checkpoint,destination):
    """Restore one failed preparation after reviewed selector repair; no new grant."""
    from orchestrator import private_records as pr
    store=driver.store;granted(store,frozen,grant_review)
    require(driver.config['run_id']==prior.RUN and checkpoint['schema']=='item4-review9-pre-admission/v1'
        and checkpoint['run_id']==prior.RUN and checkpoint['reason']=='ValueError: IMMUTABLE_ARTIFACT_CONFLICT'
        and checkpoint['existing_grant']==binding(frozen,grant_review),'RESTORE_SCOPE')
    binding(frozen,implementation_review) # validate the separately authenticated implementation-review hash
    raw=store.db.execute('SELECT payload FROM manual_state WHERE id=1').fetchone()[0]
    value=json.loads(raw)
    require(prior.sha(raw.encode())==checkpoint['state_sha256'] and value['phase']=='BLOCKED'
        and value['reason']==checkpoint['reason'] and not value.get('pending'),'RESTORE_CHECKPOINT')
    require(store.db.execute('SELECT count(*) FROM manual_calls').fetchone()[0]==21 and
        not store.batch.db.execute('SELECT 1 FROM autonomy_calls WHERE id=?',(REPLACEMENT,)).fetchone()
        and not store.batch.db.execute("SELECT 1 FROM autonomy_calls WHERE status='RUNNING'").fetchone()
        and not Path(frozen['failed_workspace']).with_name('run_spec_review-9').exists(),'RESTORE_UNADMITTED')
    event=EVENT+':workspace-selector-repair'
    require(not store.db.execute('SELECT 1 FROM events WHERE id=?',(event,)).fetchone(),'RESTORE_ALREADY_APPLIED')
    destination=Path(destination);require(not destination.exists() and not destination.is_symlink(),'RESTORE_INTENT_EXISTS')
    pr.mkdir(destination);pr.write_bytes(destination/'original-state.json',raw.encode())
    proof={'kind':event,'grant_review_sha256':grant_review,'implementation_review_sha256':implementation_review,
        'checkpoint_sha256':prior.sha(prior.canonical(checkpoint)),'new_allowance':0,'model_calls':0}
    pr.write_bytes(destination/'intent.json',prior.canonical(proof))
    value.update(phase=STAGE,reason=None);value['interventions'].append(proof)
    store.db.execute('BEGIN IMMEDIATE')
    try:
        require(store.db.execute('SELECT payload FROM manual_state WHERE id=1').fetchone()[0]==raw,'RESTORE_STATE_RACE')
        granted(store,frozen,grant_review)
        store.db.execute('INSERT INTO events VALUES(?,?,?)',(event,prior.RUN,prior.canonical(proof).decode()))
        store.db.execute('UPDATE manual_state SET payload=? WHERE id=1',(json.dumps(value,sort_keys=True),))
        # Qualify the restored state inside the transaction; any mismatch rolls back.
        next_review(store,frozen,grant_review)
        store.db.execute('COMMIT')
    except BaseException:store.db.execute('ROLLBACK');raise
    pr.write_bytes(destination/'applied.json',prior.canonical(proof))
    return {'status':'RESTORED_UNADMITTED_REVIEW9','model_calls':0,'new_allowance':0,'preserved_calls':21}
