"""Fixed author15/review12 proposal response to the genuine smoke REVISE.

This capability admits scientific proposal work only. It never grants compute,
closes prior findings, replaces the execution approval or changes dollar caps.
The installed caller must authenticate the independent implementation APPROVE
and exact source/checkpoint bytes before connecting it.
"""
import json
from pathlib import Path
from orchestrator import item4_review4_continuation as prior
from orchestrator import item4_smoke_review as smoke

RUN=prior.RUN
EVENT='REVIEWED_ITEM4_POST_SMOKE_RESPONSE'
AUTHOR=prior.sha((RUN+':run_spec_author:15').encode())
REVIEW=prior.sha((RUN+':run_spec_review:12').encode())
DOCUMENT='docs/ITEM4_POST_SMOKE_RESPONSE_PRIVATE.json'
sha,canonical=prior.sha,prior.canonical


def require(ok,why):
    if not ok:raise ValueError('ITEM4_SMOKE_RESPONSE_'+why)


def scope(p,approval):
    require(p.get('schema')=='item4-post-smoke-response/v1' and p.get('run_id')==RUN
        and p.get('authority_sha256')==prior.AUTHORITY
        and (p.get('author_attempt'),p.get('review_attempt'),p.get('run_limit'),p.get('batch_limit'))==(15,12,29,67)
        and p.get('execution_authorized') is False,'SCOPE')
    require(isinstance(approval,str) and len(approval)==64 and all(c in '0123456789abcdef' for c in approval),'APPROVAL')
    require(len(p['local_calls'])==len(p['global_calls'])==25 and len(p['batch_calls'])==63
        and set(p['local_calls'])==set(p['global_calls'])
        and all(p['batch_calls'].get(i)==pin for i,pin in p['global_calls'].items()),'CALL_SCOPE')
    old=json.loads(p['original_state'])
    require(sha(p['original_state'].encode())==p['state_sha256'] and old['phase']=='BLOCKED'
        and old['reason']=='SMOKE_REVIEW_REVISE' and not old.get('pending')
        and old['rounds']=={'run_spec_author':14,'run_spec_review':11},'CHECKPOINT')
    a=p['assessment']
    require(sha(canonical(a))==p['assessment_sha256'] and old.get('smoke_review')==a
        and a.get('call_id')==smoke.CALL and a.get('verdict')=='REVISE'
        and all(a.get(k) is False for k in ('full_training_admitted','whole_plan_complete','coverage_released')),'ASSESSMENT')
    return old


def originals(store,p,approval):
    scope(p,approval)
    require(sha((Path(store.path).parent/'lane.json').read_bytes())==p['configuration_sha256'],'CONFIGURATION')
    for db,table,pins in [(store.db,'manual_calls',p['local_calls']),
            (store.batch.db,'autonomy_calls',p['batch_calls'])]:
        for ident,pin in pins.items():
            row=db.execute('SELECT * FROM '+table+' WHERE id=?',(ident,)).fetchone()
            require(row is not None and sha(canonical(dict(row)))==pin,'ORIGINAL_CHANGED')


def proof(p,approval):
    scope(p,approval)
    return {'schema':'item4-post-smoke-response-grant/v1','run_id':RUN,
        'checkpoint_sha256':sha(canonical(p)),'review_sha256':approval,
        'authority_sha256':prior.AUTHORITY,'author_call_id':AUTHOR,'review_call_id':REVIEW,
        'run_limit':29,'batch_limit':67,'execution_authorized':False}


def granted(store,p,approval):
    originals(store,p,approval)
    row=store.db.execute('SELECT payload FROM events WHERE id=?',(EVENT,)).fetchone()
    require(row is not None and json.loads(row[0])==proof(p,approval),'GRANT')


def review_binding(driver,p,approval):
    from orchestrator.experiment_approval import verified_review_delivery
    from orchestrator.author_revision_accounting import AUTHORITY
    from orchestrator.review_contract import scientific
    originals(driver.store,p,approval)
    work=Path(driver.config.get('workspace_root',driver.state.parent/(driver.state.name+'-scientific-workspaces')))/'run_spec_review-11'
    pending={'stage':'run_spec_review','round':11,'workspace':str(work),'id':smoke.CALL}
    _,_,raw,receipt,row,submission=verified_review_delivery(driver,pending,'run_spec_review')
    decision=scientific(raw);a=p['assessment']
    require(decision['verdict']=='REVISE' and decision['findings'] and sha(raw)==a['report_sha256']
        and sha(row['receipt'].encode())==a['call_receipt_sha256']
        and sha(submission)==a['submission_sha256'],'GENUINE_REVISE')
    # This exact existing budget finding permits drafting a response, not a
    # changed budget or execution. All other reserved findings still refuse.
    reserved=[f for f in decision['findings'] if f['category'] in {'budget','privacy/secret','test-set/leakage'}]
    require(len(reserved)==1 and reserved[0]['category']=='budget'
        and reserved[0]['id']=='STAGE1-full-projection-exceeds-authorized-caps','PROPOSAL_ONLY_BUDGET_SCOPE')
    return {'schema':'scientific-revision-response/v1','authority_sha256':AUTHORITY,
        'run_id':RUN,'stage':'run_spec_author','author_attempt':15,'author_call_id':AUTHOR,
        'review_call_id':smoke.CALL,'review_round':11,'review_sha256':sha(raw),
        'review_receipt_sha256':sha(row['receipt'].encode()),'submission_sha256':sha(submission),
        'continuation_authority_sha256':prior.AUTHORITY,'continuation_review_sha256':approval,
        'proposal_only':True}


def activate(driver,p,approval,dest):
    from orchestrator import private_records as pr
    old=scope(p,approval);originals(driver.store,p,approval)
    db=driver.store.db;raw=db.execute('SELECT payload FROM manual_state WHERE id=1').fetchone()[0]
    require(raw==p['original_state'] and db.execute('SELECT count(*) FROM manual_calls').fetchone()[0]==25,'EXACT_BLOCK')
    require(not driver.store.batch.db.execute("SELECT 1 FROM autonomy_calls WHERE status='RUNNING'").fetchone(),'RUNNING')
    binding=review_binding(driver,p,approval)
    require(not Path(dest).exists() and not Path(dest).is_symlink(),'EXISTS_RECONCILE')
    pr.mkdir(dest);pr.write_bytes(Path(dest)/'original-state.json',raw.encode())
    grant=proof(p,approval);pr.write_bytes(Path(dest)/'intent.json',canonical(grant))
    value={**old,'phase':'run_spec_author','reason':EVENT,'post_smoke_response_scope':grant}
    # Keep the old execution review and all obligations. The actual smoke
    # critique is supplied separately and bound through the accepted receipt.
    value['interventions']=[*old.get('interventions',[]),grant]
    db.execute('BEGIN IMMEDIATE')
    try:
        require(db.execute('SELECT payload FROM manual_state WHERE id=1').fetchone()[0]==raw,'STATE_DRIFT')
        originals(driver.store,p,approval)
        db.execute('INSERT INTO events VALUES(?,?,?)',(EVENT,RUN,json.dumps(grant,sort_keys=True)))
        db.execute('UPDATE manual_state SET payload=? WHERE id=1',(json.dumps(value),));db.execute('COMMIT')
    except BaseException:db.execute('ROLLBACK');raise
    pr.write_bytes(Path(dest)/'applied.json',canonical({'status':'READY_PROPOSAL_AUTHOR15','binding':binding,'grant':grant,'model_calls':0}))
    return {'status':'READY_PROPOSAL_AUTHOR15','model_calls':0,'execution_authorized':False}


def ready(driver,value,p,approval):
    granted(driver.store,p,approval)
    require(value.get('post_smoke_response_scope')==proof(p,approval) and not value.get('pending'),'STATE_SCOPE')
    stage=value.get('phase');rounds=value.get('rounds')
    require((stage,rounds) in [('run_spec_author',{'run_spec_author':14,'run_spec_review':11}),
        ('run_spec_review',{'run_spec_author':15,'run_spec_review':11})],'STATE')
    old=scope(p,approval)
    for key in ('review','spec_review','reviewed_execution','smoke_review','dispatch_sha256','fit_continuations'):
        require(value.get(key)==old.get(key),'EXECUTION_AUTHORITY_CHANGED')
    review_binding(driver,p,approval)


def connect_roles(accounting,recovery,p,approval):
    scope(p,approval)
    old_binding,old_inspect,old_limit=accounting.review_binding,accounting.inspect,recovery.role_limit
    def binding(driver,stage,number,author):
        if driver.config['run_id']!=RUN or (stage,number,author)!=('run_spec_author',11,15):
            return old_binding(driver,stage,number,author)
        granted(driver.store,p,approval);return review_binding(driver,p,approval)
    def inspect(store,run,stage):
        result=old_inspect(store,run,stage)
        if run!=RUN or stage!='run_spec_author':return result
        value=prior.state(store)
        if value.get('phase')!=stage or value.get('reason')!=EVENT:return result
        driver=accounting.context(store,run);require(driver is not None,'AUTHOR_CONTEXT')
        ready(driver,value,p,approval)
        require(store.db.execute('SELECT count(*) FROM manual_calls').fetchone()[0]==25,'AUTHOR_ONCE')
        return {**result,'limit':15,'binding':binding(driver,stage,11,15)}
    def limit(store,run,stage):
        if run!=RUN or stage!='run_spec_review':return old_limit(store,run,stage)
        value=prior.state(store)
        if value.get('phase')!=stage or value.get('post_smoke_response_scope')!=proof(p,approval):return old_limit(store,run,stage)
        driver=accounting.context(store,run);require(driver is not None,'REVIEW_CONTEXT')
        ready(driver,value,p,approval)
        rows=[dict(r) for r in store.db.execute('SELECT * FROM manual_calls ORDER BY rowid')]
        require(len(rows)==26 and rows[-1]['id']==AUTHOR and accounting._accepted(store,rows[-1])
            and json.loads(rows[-1]['receipt']).get(accounting.FIELD)==binding(driver,'run_spec_author',11,15),'ACCEPTED_AUTHOR')
        return 12
    accounting.review_binding=binding;accounting.inspect=inspect;recovery.role_limit=limit


def finish_review(driver,value,p,approval):
    from orchestrator.experiment_approval import verified_review_delivery
    from orchestrator.review_contract import scientific
    from orchestrator.manual_driver import write_once
    granted(driver.store,p,approval)
    pending=value.get('pending') or {}
    require(value['phase']=='MODEL_RUNNING' and pending.get('id')==REVIEW
        and (pending.get('stage'),pending.get('round'))==('run_spec_review',12)
        and value['rounds']=={'run_spec_author':15,'run_spec_review':11}
        and value.get('post_smoke_response_scope')==proof(p,approval),'COMPLETION_SCOPE')
    from orchestrator import author_revision_accounting as accounting
    old=scope(p,approval)
    for key in ('review','spec_review','reviewed_execution','smoke_review','dispatch_sha256','fit_continuations'):
        require(value.get(key)==old.get(key),'EXECUTION_AUTHORITY_CHANGED')
    rows=[dict(r) for r in driver.store.db.execute('SELECT * FROM manual_calls ORDER BY rowid')]
    require(len(rows)==27 and [(r['id'],r['stage'],r['attempt'],r['status']) for r in rows[-2:]]==[
        (AUTHOR,'run_spec_author',15,'COMPLETE'),(REVIEW,'run_spec_review',12,'COMPLETE')],'COMPLETED_PAIR')
    require(accounting._accepted(driver.store,rows[-2]) and
        json.loads(rows[-2]['receipt']).get(accounting.FIELD)==review_binding(driver,p,approval),'AUTHOR_BINDING')
    for ident in (AUTHOR,REVIEW):
        gr=driver.store.batch.db.execute('SELECT status FROM autonomy_calls WHERE id=?',(ident,)).fetchone()
        require(gr is not None and gr[0]=='COMPLETE','GLOBAL_OUTCOME')
    _,_,raw,receipt,row,submission=verified_review_delivery(driver,pending,'run_spec_review')
    decision=scientific(raw)
    record={'schema':'item4-post-smoke-response-assessment/v1','verdict':decision['verdict'],
        'report_sha256':sha(raw),'call_id':REVIEW,'call_receipt_sha256':sha(row['receipt'].encode()),
        'submission_sha256':sha(submission),'implementation_review_sha256':approval,
        'execution_authorized':False,'full_training_admitted':False,'coverage_released':False}
    write_once(driver.state/'post-smoke-response'/'review.json',raw)
    write_once(driver.state/'post-smoke-response'/'assessment.json',canonical(record))
    if decision['verdict']!='APPROVE':driver.criticism('run_spec_review',12,raw)
    value['rounds']['run_spec_review']=12;value['post_smoke_response']=record
    value.pop('pending',None)
    # Proposal acceptance is never execution admission. Existing scientific
    # findings and old execution authority stay unchanged on every verdict.
    value.update(phase='BLOCKED',reason='POST_SMOKE_RESPONSE_'+decision['verdict']+'_EXECUTION_HELD')
    driver.save(value);return driver.status()


GUIDANCE=(
    'Respond to the genuine collected-smoke REVISE11 using the original measured results and every open finding. '
    'This is an author-owned scientific proposal and its independent review, not execution admission. '
    'The current operator stage1 cap is $150 for the completed benchmark/base/resume/repeat milestone; '
    'the frozen older $75 wording is superseded by the verbatim delivered operator decision. '
    'The $1200 full-training projection gate and $1275 total remain unchanged. No new arm run or higher cap '
    'is granted here. Preserve all eight arms, five folds and the approved full research goal; do not silently '
    'narrow BACKLOG or remove safeguards. Reconcile actual timer boundaries, different checkpoint intervals, '
    'warm-up and Sprint12 workload comparability. The mechanical audit is not scientific judgment; do not '
    'subtract the whole native/returned timing difference as checkpoint-only cost or replace billed wall time '
    'with a narrower timer. Own the interpretation and identify the simplest scientifically defensible next '
    'measurement or concrete budget proposal, with uncertainties. Do not assert a plateau or impute missing '
    'arm timings. Keep coverage findings open without the required authentic sources. Preserve prior contrary '
    'evidence and avoid efficacy claims from exploratory smoke scores. The exact required author output schema '
    'and same-call submission validation remain unchanged. You may retain unchanged scientific code and use '
    'the specification to explain the proposal; any scientific change must be explicit and tested. The reviewer '
    'judges this response at its actual scope and states what remains required; no verdict from this stage '
    'closes prior obligations automatically or authorizes GPU, coverage or full training.')

SUPPLEMENTAL={'current-cap-decision.txt','timing-audit.json','native-trainer.py','checkpoint-adapter.py','durable-progress.py'}


def deliver(driver,value,p,approval,supplemental):
    from orchestrator import experiment_collection as collection,private_records as pr
    ready(driver,value,p,approval)
    require(set(supplemental)==SUPPLEMENTAL,'SUPPLEMENTAL_SET')
    before=list(value['artifacts'])
    def add(name,raw):
        collection.artifact(driver,value,'result_tables','post-smoke-response-'+name,'post-smoke-response/'+name,raw)
    raw=pr.check(driver.state/'smoke-review11/review.json').read_bytes()
    require(sha(raw)==p['assessment']['report_sha256'],'ORIGINAL_REVIEW11')
    add('scientific-review11.json',raw)
    add('scientific-assessment11.json',canonical(p['assessment']))
    for name,raw in supplemental.items():add(name,raw)
    added=[r for r in value['artifacts'] if r not in before]
    expected=len(SUPPLEMENTAL)+2
    require(len(added)==expected or (not added and len([r for r in before if r['id'].startswith('post-smoke-response-')])==expected),'DELIVERY_MEMBERS')
    driver.save(value)


def verify_delivered(driver,value,stage,work,prompt,measurement,p):
    from orchestrator import manual_context as mc,context_budget as cb,private_records as pr
    require(stage in {'run_spec_author','run_spec_review'},'DELIVERY_STAGE')
    navigation=prompt
    if stage=='run_spec_review':
        indexes=[r for r in measurement['workspace_files'] if r.get('id')=='scientific-review-artifact-index']
        require(len(indexes)==1 and cb.encoded(indexes[0]) in prompt,'ARTIFACT_INDEX')
        ref=indexes[0];raw=pr.check(cb.relative_file(work,ref['path'])).read_bytes()
        require(sha(raw)==ref['sha256'] and len(raw)==ref['bytes'],'ARTIFACT_INDEX_CHANGED');navigation=raw.decode()
    role='author' if stage.endswith('author') else 'review'
    instructions=[r for r in measurement['workspace_files'] if r.get('id')=='scientific-'+role+'-instructions']
    require(len(instructions)==1 and cb.encoded(instructions[0]) in navigation,'TASK_REQUIRED')
    task=instructions[0];raw=pr.check(cb.relative_file(work,task['path'])).read_bytes()
    require(sha(raw)==task['sha256'] and len(raw)==task['bytes'] and GUIDANCE in raw.decode(),'TASK_CHANGED')
    old=scope(p,'0'*64)
    retained=[r for r in old['artifacts'] if r['id'].startswith('smoke-review11-')]
    require(len(retained)==19 and all(r in value['artifacts'] for r in retained),'COLLECTED_EVIDENCE_PRESERVED')
    extra=[r for r in value['artifacts'] if r['id'].startswith('post-smoke-response-')]
    require(len(extra)==len(SUPPLEMENTAL)+2,'DELIVERY_MEMBERS')
    expected=mc.selected_artifacts(stage,value['artifacts'])
    require(all(r in expected for r in retained+extra),'REQUIRED_ARTIFACTS_SELECTED')
    for ref in expected:
        require(measurement['selected_artifacts'].count(ref)==1,'NOT_DELIVERED')
        raw=pr.check(cb.relative_file(driver.context,ref['path'])).read_bytes()
        require(sha(raw)==ref['sha256'],'SOURCE_ARTIFACT_CHANGED')
        if mc.workspace_artifact(ref['type'],artifact_id=ref['id'],private_intake=driver.config['private_intake'],reference_prior_results=True):
            matches=[r for r in measurement['workspace_files'] if r.get('id')==ref['id'] and r.get('type')==ref['type']]
            require(len(matches)==1,'WORKSPACE_ARTIFACT');item=matches[0]
            require(all(item.get(k)==ref[k] for k in ('id','type','version','sha256')) and item.get('source_path')==ref['path']
                and cb.encoded(item) in navigation,'DELIVERY_BINDING')
            require(pr.check(cb.relative_file(work,item['path'])).read_bytes()==raw,'DELIVERY_BYTES')
        else:require(cb.encoded(ref)+'\n'+raw.decode() in navigation,'INLINE_DELIVERY')
