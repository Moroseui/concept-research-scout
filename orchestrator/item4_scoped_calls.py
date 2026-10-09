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

def connect(frozen,approval,*,mechanical=None,mechanical_approval=None):
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
    active={}
    from orchestrator import item4_review8_recovery as repair
    if mechanical is not None:repair.binding(mechanical,mechanical_approval)
    prefix=21 if mechanical is not None else 19
    sequence=((('run_spec_review',9),('result_interpretation_author',1),('result_interpretation_review',1))
        if mechanical is not None else SEQUENCE)
    cap=24 if mechanical is not None else 23


    def snapshot(store,*,inserted=False):
        rows=continuation.originals(store,RUN,frozen)
        continuation.granted(store,frozen,approval)
        require({r['id'] for r in rows[:19]}==set(frozen['local_calls']),'ORIGINAL_ORDER')
        if mechanical is not None:
            repair.granted(store,mechanical,mechanical_approval)
            require({r['id'] for r in rows[:21]}==set(mechanical['local_calls']),'MECHANICAL_PREFIX')
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
        for st,n in sequence[:len(tail)]:rounds[st]=n
        require(value.get('rounds')==rounds,'ROUNDS')
        if tail and tail[-1]['stage'].endswith('_author'):
            from orchestrator import author_revision_accounting
            require(author_revision_accounting._accepted(store,tail[-1]),'ACCEPTED_AUTHOR')
        if mechanical is not None and not tail:
            repair.next_review(store,mechanical,mechanical_approval)
        if len(tail)>=(1 if mechanical is not None else 2):
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
        return cap

    def global_limit(batch,run):
        if run!=RUN:return old_global(batch,run)
        require(active.get('store') is not None and active['store'].batch is batch,'GLOBAL_OWNER')
        snapshot(active['store'])
        return cap

    def amendment(store,run,policy):
        if run!=RUN:return old_allowance(store,run,policy)
        require(active.get('store') is store,'ALLOWANCE_OWNER')
        _,tail=snapshot(store,inserted=True)
        require(tail and tail[-1]['id']==active['id'],'RESERVED_CALL')
        return {'authority_sha256':continuation.AUTHORITY,'run_limit':cap,
            'scoped_run_id':RUN,'call_id':active['id'],'review_sha256':mechanical_approval if mechanical is not None else approval,
            'checkpoint_sha256':continuation.sha(continuation.canonical(mechanical if mechanical is not None else frozen))}

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

    limits.local_limit=local;limits.global_limit=global_limit;limits.allowance=amendment
    limits.cap_authority=lambda selected:continuation.AUTHORITY if selected==cap else old_authority(selected)
    ManualExecutor.reserve_call=reserve;BatchAccounts.reserve_scientific=batch_reserve
    _validate=validate
