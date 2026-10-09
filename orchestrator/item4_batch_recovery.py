"""One exact unadmitted author14 recovery; preserve the original preparation."""
import json
from pathlib import Path
from orchestrator import item4_review4_continuation as continuation

RUN=continuation.RUN
CALL=continuation.sha((RUN+':run_spec_author:14').encode())
EVENT='ITEM4_BATCH_UNADMITTED_AUTHOR14_RECOVERY'
DIRECTORY='item4-batch-staging-20261009'


def require(ok,why):
    if not ok:raise ValueError('ITEM4_BATCH_RECOVERY_'+why)


def proof(checkpoint,approval):
    require(checkpoint.get('schema')=='item4-batch-continuation/v1' and
        checkpoint.get('run_id')==RUN and checkpoint.get('authority_sha256')==continuation.AUTHORITY,'SCOPE')
    require(isinstance(approval,str) and len(approval)==64 and all(c in '0123456789abcdef' for c in approval),'APPROVAL')
    return {'schema':'item4-unadmitted-author14-recovery/v1','run_id':RUN,'call_id':CALL,
        'checkpoint_sha256':continuation.sha(continuation.canonical(checkpoint)),
        'review_sha256':approval,'operator_staging_sha256':checkpoint['operator_staging_sha256'],
        'existing_grant_review_sha256':checkpoint['prior_review'],'model_calls':0}


def granted(store,checkpoint,approval):
    row=store.db.execute('SELECT payload FROM events WHERE id=?',(EVENT,)).fetchone()
    require(row is not None and json.loads(row[0])==proof(checkpoint,approval),'GRANT')


def original_workspace(driver):
    return Path(driver.config.get('workspace_root',driver.state.parent/(driver.state.name+'-scientific-workspaces')))/'run_spec_author-14'


def replacement_workspace(driver):
    return original_workspace(driver).parent/DIRECTORY/'run_spec_author-14'


def preparation(driver,checkpoint,pins_path):
    """Read only: exact original membership, regular files and all hashes."""
    from orchestrator import author_format_submission as af
    root=original_workspace(driver);pins_path=Path(pins_path)
    require(root.is_dir() and not root.is_symlink() and root.absolute()==root.resolve(),'ORIGINAL_WORKSPACE')
    actual={}
    for path in root.rglob('*'):
        require(not path.is_symlink(),'ORIGINAL_SYMLINK')
        if path.is_dir():continue
        require(path.is_file(),'ORIGINAL_TYPE')
        raw=path.read_bytes();actual[str(path.relative_to(root))]={'sha256':continuation.sha(raw),'bytes':len(raw)}
    require(actual==checkpoint['workspace_files'],'ORIGINAL_MEMBERSHIP_OR_HASH')
    require(not any(name in actual for name in (*af.OUTPUTS,af.RECORD,'console.log','review.json')),'ORIGINAL_HAS_OUTPUT')
    require(pins_path.is_file() and not pins_path.is_symlink() and pins_path.absolute()==pins_path.resolve(),'PINS_PATH')
    raw=pins_path.read_bytes();require(continuation.sha(raw)==checkpoint['runtime_pins_sha256'],'PINS_CHANGED')
    pins=json.loads(raw);af.check_runtime(root,pins);cfg=af.load(root,pins[af.CONFIG])
    require(cfg['bindings']['call_id']==CALL and cfg['bindings']['run_id']==RUN and
        cfg['bindings']['stage']=='run_spec_author' and cfg['bindings']['round']==14 and
        cfg['bindings']['input_sha256']==actual['prompt.md']['sha256'],'ORIGINAL_SUBMISSION_BINDING')
    return actual


def unadmitted(driver,checkpoint,pins_path):
    store=driver.store
    require(driver.config['run_id']==RUN and continuation.sha((Path(store.path).parent/'lane.json').read_bytes())==checkpoint['configuration_sha256'],'CONFIGURATION')
    for db,table,key,where in [(store.db,'manual_calls','local_calls',''),
            (store.batch.db,'autonomy_calls','global_calls'," WHERE kind='scientific'")]:
        rows=[dict(r) for r in db.execute('SELECT * FROM '+table+where+' ORDER BY rowid')]
        require({r['id']:continuation.sha(continuation.canonical(r)) for r in rows}==checkpoint[key],'ORIGINAL_CALLS_OR_CHARGES')
        require(not db.execute('SELECT 1 FROM '+table+' WHERE id=?',(CALL,)).fetchone(),'ALREADY_ADMITTED')
    require(len(checkpoint['local_calls'])==22 and len(checkpoint['global_calls'])==60,'ORIGINAL_COUNT')
    account=[dict(r) for r in store.db.execute('SELECT * FROM manual_account ORDER BY id')]
    require(continuation.sha(continuation.canonical(account))==checkpoint['original_account_sha256'],'ACCOUNT_CHANGED')
    require(not store.batch.db.execute("SELECT 1 FROM autonomy_calls WHERE status='RUNNING'").fetchone(),'RUNNING')
    preparation(driver,checkpoint,pins_path)


def restore(driver,checkpoint,approval,response,response_approval,destination,pins_path):
    """Called under the existing driver lock; exclusive intent and CAS, no calls."""
    from orchestrator import private_records as pr
    store=driver.store;record=proof(checkpoint,approval)
    continuation.originals(store,RUN,response);continuation.granted(store,response,response_approval)
    require(response_approval==checkpoint['prior_review'],'PRIOR_GRANT_APPROVAL')
    unadmitted(driver,checkpoint,pins_path)
    raw=store.db.execute('SELECT payload FROM manual_state WHERE id=1').fetchone()[0];value=json.loads(raw)
    require(continuation.sha(raw.encode())==checkpoint['state_sha256'] and value.get('phase')=='BLOCKED'
        and value.get('reason')=='ValueError: AUTONOMY_BATCH_CALL_LIMIT' and not value.get('pending')
        and value.get('rounds')=={'run_spec_author':13,'run_spec_review':9},'EXACT_REFUSAL')
    target=replacement_workspace(driver);destination=Path(destination)
    require(target.absolute()==target.resolve() and destination.absolute()==destination.resolve(),'RECOVERY_PATH_ALIAS')
    require(not target.exists() and not target.is_symlink() and not destination.exists() and not destination.is_symlink(),'EXISTING_PREPARATION_OR_INTENT')
    require(not store.db.execute('SELECT 1 FROM events WHERE id=?',(EVENT,)).fetchone(),'ALREADY_RECOVERED')
    pr.mkdir(destination);pr.write_bytes(destination/'original-state.json',raw.encode())
    pr.write_bytes(destination/'intent.json',continuation.canonical(record))
    value.update(phase='run_spec_author',reason=continuation.reason(response));value['interventions'].append(record)
    store.db.execute('BEGIN IMMEDIATE')
    try:
        require(store.db.execute('SELECT payload FROM manual_state WHERE id=1').fetchone()[0]==raw,'STATE_RACE')
        unadmitted(driver,checkpoint,pins_path)
        continuation.granted(store,response,response_approval)
        store.db.execute('INSERT INTO events VALUES(?,?,?)',(EVENT,RUN,continuation.canonical(record).decode()))
        store.db.execute('UPDATE manual_state SET payload=? WHERE id=1',(json.dumps(value,sort_keys=True),))
        store.db.execute('COMMIT')
    except BaseException:store.db.execute('ROLLBACK');raise
    pr.write_bytes(destination/'applied.json',continuation.canonical(record))
    return {'status':'READY_UNSPENT_AUTHOR14_NEW_STAGING_INPUT','preserved_calls':60,'model_calls':0,'provider_calls':0}


def workspace(driver,value,stage,round_no,ordinary,checkpoint,approval,pins_path):
    if stage!='run_spec_author' or round_no!=14:return ordinary(value,stage,round_no)
    require(value==continuation.state(driver.store) and value.get('phase')==stage and not value.get('pending'),'WORKSPACE_STATE')
    granted(driver.store,checkpoint,approval);unadmitted(driver,checkpoint,pins_path)
    target=replacement_workspace(driver)
    require(target.absolute()==target.resolve(),'RECOVERY_PATH_ALIAS')
    require(not target.exists() and not target.is_symlink(),'NEW_WORKSPACE_EXISTS_RECONCILE')
    return target
