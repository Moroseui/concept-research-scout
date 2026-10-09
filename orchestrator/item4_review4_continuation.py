"""Five fixed Claude-reviewed continuations; no generic limit change.

The enclosing installed component authenticates independent APPROVE and every
source byte before supplying this capability. Ordinary admission still charges
both calls and enforces run/day/batch/dollar limits and uncertain-call refusals.
"""
import hashlib
import json
from pathlib import Path

RUN = 'experiment-a74959ac4546a982af4ae137'
REASON = 'REVIEWED_ITEM4_REVIEW4_CONTINUATION'
AUTHORITY = 'a7fbba4b5c49426c099f1eb8d91e45489b454fc51a527f5df1566a60c1cabcb1'
DOCUMENT = 'docs/ITEM4_REVIEW4_CONTINUATION.json'

def sha(raw): return hashlib.sha256(raw).hexdigest()
def canonical(value): return json.dumps(value,sort_keys=True,separators=(',',':')).encode()
def require(ok,why):
    if not ok: raise ValueError('ITEM4_CONTINUATION_'+why)

def state(store):
    return json.loads(store.db.execute('SELECT payload FROM manual_state WHERE id=1').fetchone()[0])

def scope(frozen):
    # Only the five enumerated checkpoints exist. Adding any other allowance
    # requires new source, independent approval and installed source binding.
    pair=(frozen['author_attempt'],frozen['review_attempt'])
    require(pair in {(10,5),(11,6),(12,7),(13,8),(14,10)},'FIXED_ATTEMPTS')
    author,review=pair
    return author,review,author+review-2

def reason(frozen):
    return 'REVIEWED_ITEM4_REVIEW'+str(scope(frozen)[1]-1)+'_CONTINUATION'

def originals(store,run,frozen):
    author,review,count=scope(frozen)
    require(run==RUN==frozen['run_id'] and frozen['authority_sha256']==AUTHORITY,'SCOPE')
    require(sha((Path(store.path).parent/'lane.json').read_bytes())==frozen['configuration_sha256'],'CONFIGURATION')
    require(len(frozen['local_calls'])==len(frozen['global_calls'])==count and
        set(frozen['local_calls'])==set(frozen['global_calls']),'ORIGINAL_SET')
    for table,key,db in [('manual_calls','local_calls',store.db),('autonomy_calls','global_calls',store.batch.db)]:
        for ident,pin in frozen[key].items():
            row=db.execute('SELECT * FROM '+table+' WHERE id=?',(ident,)).fetchone()
            require(row is not None and sha(canonical(dict(row)))==pin,'ORIGINAL_CHANGED')
    return [dict(r) for r in store.db.execute('SELECT * FROM manual_calls ORDER BY rowid')]

def review_binding(driver,frozen,approval):
    from orchestrator.experiment_approval import verified_review_delivery
    from orchestrator.analysis_revisions import RESERVED
    from orchestrator.author_revision_accounting import AUTHORITY as author_authority
    author,number,count=scope(frozen)
    originals(driver.store,driver.config['run_id'],frozen)
    work=Path(driver.config.get('workspace_root',driver.state.parent/(driver.state.name+'-scientific-workspaces')))/('run_spec_review-'+str(number-1))
    pending={'stage':'run_spec_review','round':number-1,'workspace':str(work),'id':frozen['review_call_id']}
    _,_,raw,receipt,row,submission=verified_review_delivery(driver,pending,'run_spec_review')
    review=json.loads(raw)
    require(sha(raw)==frozen['review_sha256'] and review['verdict']=='REVISE' and review['findings'] and
        not any(x['category'] in RESERVED for x in review['findings']),'GENUINE_REVISE')
    return {'schema':'scientific-revision-response/v1','authority_sha256':author_authority,
        'run_id':RUN,'stage':'run_spec_author','author_attempt':scope(frozen)[0],
        'author_call_id':sha((RUN+':run_spec_author:'+str(author)).encode()),
        'review_call_id':pending['id'],'review_round':number-1,'review_sha256':sha(raw),
        'review_receipt_sha256':sha(row['receipt'].encode()),'submission_sha256':sha(submission),
        'continuation_authority_sha256':AUTHORITY,'continuation_review_sha256':approval}

def granted(store,frozen,approval):
    event=store.db.execute('SELECT payload FROM events WHERE id=?',(reason(frozen),)).fetchone()
    require(event is not None and json.loads(event[0])=={
        'schema':'item4-bounded-continuation-grant/v1','run_id':RUN,
        'checkpoint_sha256':sha(canonical(frozen)),'review_sha256':approval,
        'authority_sha256':AUTHORITY,'author_attempt':scope(frozen)[0],'review_attempt':scope(frozen)[1]},'GRANT')

def activate(driver,frozen,approval,dest):
    """Exclusive, durable intent; preserve old state; atomic grant and transition."""
    from orchestrator import private_records as pr
    author,review,count=scope(frozen)
    db=driver.store.db
    rows=originals(driver.store,driver.config['run_id'],frozen)
    raw=db.execute('SELECT payload FROM manual_state WHERE id=1').fetchone()[0]
    old=json.loads(raw)
    require(len(rows)==count and sha(raw.encode())==frozen['state_sha256'] and
        old['phase']=='BLOCKED' and old['reason']=='UNRESOLVED_AFTER_THREE_REVISIONS' and
        old['rounds']=={'run_spec_author':author-1,'run_spec_review':review-1} and not old.get('pending'),'EXACT_BLOCK')
    require(not driver.store.batch.db.execute("SELECT 1 FROM autonomy_calls WHERE status='RUNNING'").fetchone(),'RUNNING')
    binding=review_binding(driver,frozen,approval)
    require(not Path(dest).exists() and not Path(dest).is_symlink(),'EXISTS_RECONCILE')
    pr.mkdir(dest)
    pr.write_bytes(Path(dest)/'original-state.json',raw.encode())
    grant={'schema':'item4-bounded-continuation-grant/v1','run_id':RUN,
        'checkpoint_sha256':sha(canonical(frozen)),'review_sha256':approval,
        'authority_sha256':AUTHORITY,'author_attempt':scope(frozen)[0],'review_attempt':scope(frozen)[1]}
    pr.write_bytes(Path(dest)/'intent.json',canonical(grant))
    value={**old,'phase':'run_spec_author','reason':reason(frozen)}
    value['interventions']=[*old.get('interventions',[]),grant]
    db.execute('BEGIN IMMEDIATE')
    try:
        require(db.execute('SELECT payload FROM manual_state WHERE id=1').fetchone()[0]==raw,'STATE_DRIFT')
        originals(driver.store,RUN,frozen)
        db.execute('INSERT INTO events VALUES(?,?,?)',(reason(frozen),RUN,json.dumps(grant,sort_keys=True)))
        db.execute('UPDATE manual_state SET payload=? WHERE id=1',(json.dumps(value),))
        db.execute('COMMIT')
    except BaseException:
        db.execute('ROLLBACK');raise
    pr.write_bytes(Path(dest)/'applied.json',canonical({'status':'READY_AUTHOR'+str(author)+'_NO_MODEL_CALL',
        'grant':grant,'binding':binding,'model_calls':0}))
    return {'status':'READY_AUTHOR'+str(author)+'_NO_MODEL_CALL','model_calls':0}

def connect(accounting,recovery,frozen,approval):
    """Installed helper only; recompute proof at driver and reservation boundaries."""
    author,review,count=scope(frozen)
    original_binding=accounting.review_binding
    original_inspect=accounting.inspect
    original_limit=recovery.role_limit
    def binding(driver,stage,number,author_number):
        if driver.config['run_id']!=RUN or (stage,number,author_number)!=('run_spec_author',review-1,author):
            return original_binding(driver,stage,number,author_number)
        granted(driver.store,frozen,approval)
        return review_binding(driver,frozen,approval)
    def inspect(store,run,stage):
        if run==RUN:originals(store,run,frozen)
        result=original_inspect(store,run,stage)
        if run!=RUN or stage!='run_spec_author':return result
        value=state(store)
        if value.get('phase')!=stage or value.get('reason')!=reason(frozen):return result
        granted(store,frozen,approval)
        rows=originals(store,run,frozen)
        require(len(rows)==count and rows[-1]['id']==frozen['review_call_id'] and
            value['rounds']=={'run_spec_author':author-1,'run_spec_review':review-1} and not value.get('pending'),'AUTHOR_ONCE')
        driver=accounting.context(store,run)
        expected=binding(driver,stage,review-1,author)
        require(value.get('review')==str(Path(driver.config.get('workspace_root',
            driver.state.parent/(driver.state.name+'-scientific-workspaces')))/('run_spec_review-'+str(review-1))/'review.json'),'REVIEW_PATH')
        return {**result,'limit':author,'binding':expected}
    def limit(store,run,stage):
        ordinary=original_limit(store,run,stage)
        if run!=RUN or stage!='run_spec_review':return ordinary
        value=state(store)
        if value.get('phase')!=stage:return ordinary
        rows=originals(store,run,frozen)
        if len(rows)!=count+1:return ordinary
        granted(store,frozen,approval)
        author_row=rows[-1]
        require(author_row['stage']=='run_spec_author' and author_row['attempt']==author and
            accounting._accepted(store,author_row) and value['rounds']=={'run_spec_author':author,'run_spec_review':review-1}
            and not value.get('pending'),'ACCEPTED_BOUND_AUTHOR')
        expected=binding(accounting.context(store,run),'run_spec_author',review-1,author)
        require(json.loads(author_row['receipt']).get(accounting.FIELD)==expected,'AUTHOR_BINDING')
        return review
    accounting.review_binding=binding
    accounting.inspect=inspect
    recovery.role_limit=limit


def terminal_transition(original,driver,review,stage,number,frozen,approval):
    author,next_review,count=scope(frozen)
    if (stage,number)!=('run_spec_review',next_review):return original(review,stage,number)
    require(driver is not None and driver.config['run_id']==RUN,'TERMINAL_SCOPE')
    rows=originals(driver.store,RUN,frozen);granted(driver.store,frozen,approval)
    require(len(rows)==count+2 and rows[-1]['id']==sha((RUN+':run_spec_review:'+str(next_review)).encode()) and
        rows[-1]['status']=='COMPLETE','TERMINAL_CALL')
    # Each exact review gets no further author cycle; rejection/protected findings
    # retain the ordinary stricter stop reasons. Approval uses unchanged path.
    return original(review,stage,4)
