"""Installed one-run continuation: 19 preserved calls plus exactly four slots.

The verified component connects this capability after checking its independent
APPROVE. It owns no reset, execution dispatch or dollar allowance. All ordinary
admission runs unchanged after this additional scope check.
"""
import json
from pathlib import Path
from orchestrator import item4_review4_continuation as continuation

RUN = continuation.RUN
SEQUENCE = (('run_spec_author',13), ('run_spec_review',8),
            ('result_interpretation_author',1), ('result_interpretation_review',1))
_validate = None

def require(ok,why):
    if not ok:raise ValueError('ITEM4_SCOPED_CALL_'+why)

def validate_allowance(accounts,event,allowance):
    require(_validate is not None,'NOT_CONNECTED')
    _validate(accounts,event,allowance)

def connect(frozen,approval,*,mechanical=None,mechanical_approval=None,response=None,response_approval=None,batch_extension=None,batch_approval=None,smoke=None,smoke_approval=None,post_smoke=None,post_smoke_approval=None,diagnostic=None,diagnostic_approval=None,diagnostic_recovery=None,diagnostic_recovery_approval=None,diagnostic_scoped=None,diagnostic_scoped_approval=None):
    """Only called from the hash-verified installed helper; once per process."""
    global _validate
    from orchestrator import autonomy_limits as limits
    from orchestrator.manual_executor import ManualExecutor
    from orchestrator.autonomy_accounting import BatchAccounts
    require(_validate is None and continuation.scope(frozen)==(13,8,19),'CONNECTION')
    require(isinstance(approval,str) and len(approval)==64 and
            all(c in '0123456789abcdef' for c in approval),'APPROVAL')
    old_local,old_global,old_allowance,old_authority=(limits.local_limit,limits.global_limit,
        limits.allowance,limits.cap_authority)
    old_reserve,old_batch=ManualExecutor.reserve_call,BatchAccounts.reserve_scientific
    old_batch_allowance=limits.scientific_batch_allowance
    active={}
    from orchestrator import item4_review8_recovery as repair
    if mechanical is not None:repair.binding(mechanical,mechanical_approval)
    if response is not None:
        require(mechanical is not None and continuation.scope(response)==(14,10,22),'RESPONSE_SCOPE')
        require(isinstance(response_approval,str) and len(response_approval)==64 and
            all(c in '0123456789abcdef' for c in response_approval),'RESPONSE_APPROVAL')
    else:require(response_approval is None,'UNBOUND_RESPONSE_APPROVAL')
    prefix=22 if response is not None else 21 if mechanical is not None else 19
    sequence=((('run_spec_review',9),('result_interpretation_author',1),('result_interpretation_review',1))
        if mechanical is not None else SEQUENCE)
    cap=24 if mechanical is not None else 23
    if response is not None:
        sequence=(('run_spec_author',14),('run_spec_review',10),
            ('result_interpretation_author',1),('result_interpretation_review',1))
        cap=26


    if batch_extension is not None:
        require(response is not None and batch_extension.get('schema')=='item4-batch-continuation/v1'
            and batch_extension.get('run_id')==RUN and batch_extension.get('authority_sha256')==continuation.AUTHORITY
            and len(batch_extension.get('global_calls',{}))==60,'BATCH_EXTENSION_SCOPE')
        require(isinstance(batch_approval,str) and len(batch_approval)==64 and
            all(c in '0123456789abcdef' for c in batch_approval),'BATCH_EXTENSION_APPROVAL')
    else:require(batch_approval is None,'UNBOUND_BATCH_APPROVAL')

    from orchestrator import item4_smoke_review as stage_review
    if smoke is not None:
        require(response is not None and batch_extension is not None,'SMOKE_PREREQUISITES')
        stage_review.scope(smoke,smoke_approval)
        from orchestrator import manual_recovery
        stage_review.connect_role_limit(manual_recovery,smoke,smoke_approval)
        sequence=sequence[:2]+(('run_spec_review',11),)+sequence[2:]
        cap=27
    else:require(smoke_approval is None,'UNBOUND_SMOKE_APPROVAL')

    from orchestrator import item4_smoke_response as response_stage
    if post_smoke is not None:
        require(smoke is not None,'POST_SMOKE_PREREQUISITES')
        response_stage.scope(post_smoke,post_smoke_approval)
        from orchestrator import author_revision_accounting,manual_recovery
        response_stage.connect_roles(author_revision_accounting,manual_recovery,post_smoke,post_smoke_approval)
        sequence=sequence[:3]+(('run_spec_author',15),('run_spec_review',12))+sequence[3:]
        cap=29
    else:require(post_smoke_approval is None,'UNBOUND_POST_SMOKE_APPROVAL')

    if diagnostic is not None:
        require(post_smoke is not None and diagnostic.get('schema')==response_stage.DIAGNOSTIC_SCHEMA,'DIAGNOSTIC_PREREQUISITES')
        response_stage.scope(diagnostic,diagnostic_approval)
        response_stage.connect_roles(author_revision_accounting,manual_recovery,diagnostic,diagnostic_approval)
        sequence=sequence[:5]+(('run_spec_author',16),('run_spec_review',13))+sequence[5:]
        cap=31
    else:require(diagnostic_approval is None,'UNBOUND_DIAGNOSTIC_APPROVAL')

    if diagnostic_recovery is not None:
        require(diagnostic is not None and diagnostic_recovery.get('schema')==response_stage.RECOVERY_SCHEMA,
            'DIAGNOSTIC_RECOVERY_PREREQUISITES')
        response_stage.scope(diagnostic_recovery,diagnostic_recovery_approval)
        response_stage.connect_roles(author_revision_accounting,manual_recovery,diagnostic_recovery,diagnostic_recovery_approval)
        sequence=sequence[:6]+(('run_spec_author',17),)+sequence[6:]
        cap=32
    else:require(diagnostic_recovery_approval is None,'UNBOUND_DIAGNOSTIC_RECOVERY_APPROVAL')

    if diagnostic_scoped is not None:
        require(diagnostic_recovery is not None and response_stage.scoped_review(diagnostic_scoped),'DIAGNOSTIC_SCOPED_PREREQUISITES')
        response_stage.scope(diagnostic_scoped,diagnostic_scoped_approval)
        response_stage.connect_roles(author_revision_accounting,manual_recovery,diagnostic_scoped,diagnostic_scoped_approval)
        sequence=sequence[:8]+(('run_spec_review',14),)+sequence[8:]
        cap=33
    else:require(diagnostic_scoped_approval is None,'UNBOUND_DIAGNOSTIC_SCOPED_APPROVAL')

    def snapshot(store,*,inserted=False):
        rows=continuation.originals(store,RUN,frozen)
        continuation.granted(store,frozen,approval)
        require({r['id'] for r in rows[:19]}==set(frozen['local_calls']),'ORIGINAL_ORDER')
        if mechanical is not None:
            repair.granted(store,mechanical,mechanical_approval)
            require({r['id'] for r in rows[:21]}==set(mechanical['local_calls']),'MECHANICAL_PREFIX')
        if response is not None:
            continuation.originals(store,RUN,response)
            continuation.granted(store,response,response_approval)
            require({r['id'] for r in rows[:22]}==set(response['local_calls']),'RESPONSE_PREFIX')
        if smoke is not None:stage_review.granted(store,smoke,smoke_approval)
        if post_smoke is not None:response_stage.granted(store,post_smoke,post_smoke_approval)
        if diagnostic is not None:response_stage.granted(store,diagnostic,diagnostic_approval)
        if diagnostic_recovery is not None:response_stage.granted(store,diagnostic_recovery,diagnostic_recovery_approval)
        if diagnostic_scoped is not None:response_stage.granted(store,diagnostic_scoped,diagnostic_scoped_approval)
        tail=rows[prefix:]
        require(len(tail)<=len(sequence),'CAP')
        global_rows=[dict(r) for r in store.batch.db.execute(
            "SELECT * FROM autonomy_calls WHERE kind='scientific' AND change_id=? ORDER BY rowid",(RUN,))]
        require([r['id'] for r in global_rows]==[r['id'] for r in rows],'LOCAL_GLOBAL_SET')
        for index,row in enumerate(tail):
            stage,attempt=sequence[index]
            ident=continuation.sha((RUN+':'+stage+':'+str(attempt)).encode())
            gr=global_rows[prefix+index];binding=json.loads(gr['binding'])
            status='RUNNING' if inserted and index==len(tail)-1 else 'COMPLETE'
            require((row['id'],row['stage'],row['attempt'],row['status'])==(ident,stage,attempt,status)
                and gr['status']==status and gr['round']==prefix+1+index and
                binding['stage']==stage and binding['run_id']==RUN,'SEQUENCE_OR_OUTCOME')
        return rows,tail

    def next_call(store,stage):
        rows,tail=snapshot(store)
        require(len(tail)<len(sequence) and sequence[len(tail)][0]==stage,'NEXT_STAGE')
        value=continuation.state(store)
        require(value.get('phase')==stage and not value.get('pending'),'STATE')
        rounds={'run_spec_author':13 if mechanical is not None else 12,'run_spec_review':7}
        if response is not None:rounds={'run_spec_author':13,'run_spec_review':9}
        for st,n in sequence[:len(tail)]:rounds[st]=n
        require(value.get('rounds')==rounds,'ROUNDS')
        if tail and tail[-1]['stage'].endswith('_author'):
            from orchestrator import author_revision_accounting
            if diagnostic_recovery is not None and len(tail)==6 and stage=='run_spec_author':
                require(tail[-1]['id']==response_stage.FAILED_AUTHOR,'EXACT_FAILED_AUTHOR')
                response_stage.failed_author(store,diagnostic_recovery)
            else:require(author_revision_accounting._accepted(store,tail[-1]),'ACCEPTED_AUTHOR')
        if mechanical is not None and response is None and not tail:
            repair.next_review(store,mechanical,mechanical_approval)
        if smoke is not None and len(tail)==2:
            from orchestrator import author_revision_accounting
            driver=author_revision_accounting.context(store,RUN)
            require(driver is not None,'SMOKE_CONTEXT')
            stage_review.ready(driver,value,smoke,smoke_approval)
        if post_smoke is not None and len(tail) in (3,4):
            from orchestrator import author_revision_accounting
            driver=author_revision_accounting.context(store,RUN)
            require(driver is not None,'POST_SMOKE_CONTEXT')
            response_stage.ready(driver,value,post_smoke,post_smoke_approval)
        if diagnostic is not None and len(tail) in ((5,) if diagnostic_recovery is not None else (5,6)):
            from orchestrator import author_revision_accounting
            driver=author_revision_accounting.context(store,RUN)
            require(driver is not None,'DIAGNOSTIC_CONTEXT')
            response_stage.ready(driver,value,diagnostic,diagnostic_approval)
        if diagnostic_recovery is not None and len(tail) in (6,7):
            from orchestrator import author_revision_accounting
            driver=author_revision_accounting.context(store,RUN)
            require(driver is not None,'DIAGNOSTIC_RECOVERY_CONTEXT')
            response_stage.ready(driver,value,diagnostic_recovery,diagnostic_recovery_approval)
        if diagnostic_scoped is not None and len(tail)==8:
            from orchestrator import author_revision_accounting
            driver=author_revision_accounting.context(store,RUN)
            require(driver is not None,'DIAGNOSTIC_SCOPED_CONTEXT')
            response_stage.ready(driver,value,diagnostic_scoped,diagnostic_scoped_approval)
        if len(tail)>=(9 if diagnostic_scoped is not None else 8 if diagnostic_recovery is not None else 7 if diagnostic is not None else 5 if post_smoke is not None else 3 if smoke is not None else 2 if response is not None else 1 if mechanical is not None else 2):
            # The two reserved interpretation slots are not early-smoke approval.
            # Reuse the ordinary complete execution/collection verifier.
            from orchestrator import experiment_collection,author_revision_accounting
            driver=author_revision_accounting.context(store,RUN)
            require(driver is not None,'EXECUTION_CONTEXT')
            driver.context=Path(driver.config['context']);driver.root=Path(driver.config['root'])
            experiment_collection.verified(driver,value)
        stage,n=sequence[len(tail)]
        return continuation.sha((RUN+':'+stage+':'+str(n)).encode())

    def local(store,run,policy):
        ordinary=old_local(store,run,policy)
        if run!=RUN:return ordinary
        # Before activation the frozen blocked checkpoint retains its old cap.
        if not store.db.execute('SELECT 1 FROM events WHERE id=?',(continuation.reason(frozen),)).fetchone():return ordinary
        continuation.originals(store,run,frozen);continuation.granted(store,frozen,approval)
        if mechanical is not None:repair.granted(store,mechanical,mechanical_approval)
        if response is not None:
            if not store.db.execute('SELECT 1 FROM events WHERE id=?',(continuation.reason(response),)).fetchone():return 24
            continuation.originals(store,RUN,response);continuation.granted(store,response,response_approval)
        if smoke is not None:
            if not store.db.execute('SELECT 1 FROM events WHERE id=?',(stage_review.EVENT,)).fetchone():return 26
            stage_review.granted(store,smoke,smoke_approval)
        if post_smoke is not None:
            if not store.db.execute('SELECT 1 FROM events WHERE id=?',(response_stage.EVENT,)).fetchone():return 27
            response_stage.granted(store,post_smoke,post_smoke_approval)
        if diagnostic is not None:
            event=response_stage.profile(diagnostic)['event']
            if not store.db.execute('SELECT 1 FROM events WHERE id=?',(event,)).fetchone():return 29
            response_stage.granted(store,diagnostic,diagnostic_approval)
        if diagnostic_recovery is not None:
            event=response_stage.profile(diagnostic_recovery)['event']
            if not store.db.execute('SELECT 1 FROM events WHERE id=?',(event,)).fetchone():return 31
            response_stage.granted(store,diagnostic_recovery,diagnostic_recovery_approval)
        if diagnostic_scoped is not None:
            event=response_stage.profile(diagnostic_scoped)['event']
            if not store.db.execute('SELECT 1 FROM events WHERE id=?',(event,)).fetchone():return 32
            response_stage.granted(store,diagnostic_scoped,diagnostic_scoped_approval)
        return cap

    def global_limit(batch,run):
        if run!=RUN:return old_global(batch,run)
        require(active.get('store') is not None and active['store'].batch is batch,'GLOBAL_OWNER')
        snapshot(active['store'])
        return cap

    def batch_allowance(batch,run,stage,ident,source,receipt):
        if batch_extension is None or run!=RUN:
            return old_batch_allowance(batch,run,stage,ident,source,receipt)
        require(active.get('store') is not None and active['store'].batch is batch and
            (ident,stage,source)==(active['id'],active['stage'],active['source']),'BATCH_EXTENSION_OWNER')
        require(next_call(active['store'],stage)==ident,'BATCH_EXTENSION_NEXT')
        from orchestrator import item4_batch_recovery
        item4_batch_recovery.granted(active['store'],batch_extension,batch_approval)
        rows=[dict(r) for r in batch.db.execute("SELECT * FROM autonomy_calls WHERE kind='scientific' ORDER BY rowid")]
        pins=batch_extension['global_calls'];by_id={r['id']:r for r in rows}
        require(all(i in by_id and continuation.sha(continuation.canonical(by_id[i]))==h
            for i,h in pins.items()),'BATCH_ORIGINAL_CHANGED')
        tail=[r for r in rows if r['id'] not in pins]
        expected=[continuation.sha((RUN+':'+st+':'+str(n)).encode()) for st,n in sequence]
        require(len(tail)<len(sequence) and len(rows)==60+len(tail) and
            [r['id'] for r in tail]==expected[:len(tail)] and ident==expected[len(tail)],'BATCH_EXTENSION_SEQUENCE')
        return {'limit':60+len(sequence),'authority_sha256':continuation.AUTHORITY,'review_sha256':diagnostic_scoped_approval if diagnostic_scoped is not None else diagnostic_recovery_approval if diagnostic_recovery is not None else diagnostic_approval if diagnostic is not None else post_smoke_approval if post_smoke is not None else smoke_approval if smoke is not None else batch_approval,
            'checkpoint_sha256':continuation.sha(continuation.canonical(diagnostic_scoped if diagnostic_scoped is not None else diagnostic_recovery if diagnostic_recovery is not None else diagnostic if diagnostic is not None else post_smoke if post_smoke is not None else smoke if smoke is not None else batch_extension)),'scoped_run_id':RUN}

    def amendment(store,run,policy):
        if run!=RUN:return old_allowance(store,run,policy)
        require(active.get('store') is store,'ALLOWANCE_OWNER')
        _,tail=snapshot(store,inserted=True)
        require(tail and tail[-1]['id']==active['id'],'RESERVED_CALL')
        return {'authority_sha256':continuation.AUTHORITY,'run_limit':cap,
            'scoped_run_id':RUN,'call_id':active['id'],'review_sha256':diagnostic_scoped_approval if diagnostic_scoped is not None else diagnostic_recovery_approval if diagnostic_recovery is not None else diagnostic_approval if diagnostic is not None else post_smoke_approval if post_smoke is not None else smoke_approval if smoke is not None else response_approval if response is not None else mechanical_approval if mechanical is not None else approval,
            'checkpoint_sha256':continuation.sha(continuation.canonical(diagnostic_scoped if diagnostic_scoped is not None else diagnostic_recovery if diagnostic_recovery is not None else diagnostic if diagnostic is not None else post_smoke if post_smoke is not None else smoke if smoke is not None else response if response is not None else mechanical if mechanical is not None else frozen))}

    def validate(accounts,event,allowance):
        store=active.get('store')
        require(store is not None and accounts.db is store.db and event['run_id']==active['id']
            and event['attempt']=='1' and allowance==amendment(store,RUN,{}),'ALLOWANCE_BINDING')

    def reserve(store,run,stage,source,branch,policy,receipt):
        if run!=RUN:return old_reserve(store,run,stage,source,branch,policy,receipt)
        require(not active,'REENTRANT')
        ident=next_call(store,stage)
        config=json.loads((Path(store.path).parent/'lane.json').read_bytes())
        require(source==config['source'],'SOURCE')
        active.update(store=store,id=ident,stage=stage,source=source)
        try:return old_reserve(store,run,stage,source,branch,policy,receipt)
        finally:active.clear()

    def batch_reserve(batch,ident,run,stage,source,receipt):
        if run==RUN:
            require(active.get('store') is not None and active['store'].batch is batch and
                (ident,stage,source)==(active['id'],active['stage'],active['source']),'GLOBAL_BINDING')
            require(next_call(active['store'],stage)==ident,'GLOBAL_NEXT_CALL')
        return old_batch(batch,ident,run,stage,source,receipt)

    if batch_extension is not None:limits.scientific_batch_allowance=batch_allowance
    limits.local_limit=local;limits.global_limit=global_limit;limits.allowance=amendment
    limits.cap_authority=lambda selected:continuation.AUTHORITY if selected==cap else old_authority(selected)
    ManualExecutor.reserve_call=reserve;BatchAccounts.reserve_scientific=batch_reserve
    _validate=validate
