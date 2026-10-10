"""One preserved opaque-output failure; no generic retry, receipt or cap reset."""
import copy,json,sqlite3
import pytest
from orchestrator import item4_smoke_response as post,item4_scoped_calls as scoped
from orchestrator import item4_review4_continuation as x,author_revision_accounting as a
from orchestrator import autonomy_limits as limits,manual_recovery
from orchestrator.manual_executor import ManualExecutor,Accounts
from orchestrator.autonomy_accounting import BatchAccounts
from test_item4_diagnostic_native_harness import (native_ready,scoped_ready,recovery_ready,diagnostic_ready,
    baseline,diagnostic_plan,response_ready,accepted_author,smoke_ready,extended,fifth,accepted,
    mechanical,fourth,third,setup,second,continuation,base_setup)
from test_manual_lane import policy

@pytest.fixture
def plaintext_ready(request,monkeypatch):
    connect=scoped.connect
    originals=[(o,k,getattr(o,k)) for o,k in [(limits,k) for k in
        ('local_limit','global_limit','allowance','cap_authority','scientific_batch_allowance')]+
        [(ManualExecutor,'reserve_call'),(BatchAccounts,'reserve_scientific')]]
    f,native,work17=request.getfixturevalue('native_ready');store,batch,c,d,*_=f
    ident,n,receipt=store.reserve_call(x.RUN,'run_spec_author',c['source'],'astra/manual-test',policy(),{})
    assert n==18
    work=d.state.parent/(d.state.name+'-scientific-workspaces')/'run_spec_author-18';work.mkdir(parents=True)
    files={'SPEC.proposed.md':b'spec','notebook.patch.json':b'opaque reference','execution.plan.json':b'plan'}
    for name,raw in files.items():(work/name).write_bytes(raw)
    (work/'console.log').write_bytes(b'preserved-stream')
    (work/'.author-runtime').mkdir();(work/'.author-runtime/config.json').write_bytes(b'original-config')
    (work/'.author-submission.json').write_bytes(b'original-receipt')
    outputs={k:x.sha(v) for k,v in files.items()}
    format_record={'status':'ACCEPTED','files':outputs,'record_sha256':x.sha(b'original-receipt'),
        'config_sha256':x.sha(b'original-config'),'native_item_id':'synthetic-original-submission'}
    receipt.update(workspace=str(work),output_sha256=outputs,native={'transport_returncode':0,
        'console_sha256':x.sha(b'preserved-stream'),'author_submission':format_record})
    store.finish_call(ident,receipt,'COMPLETE')
    value=x.state(store);value.update(phase='BLOCKED',reason=post.OPAQUE_REASON,
        rounds={'run_spec_author':18,'run_spec_review':14},
        pending={'id':ident,'stage':'run_spec_author','round':18,'workspace':str(work)})
    d.save(value);raw=store.db.execute('SELECT payload FROM manual_state WHERE id=1').fetchone()[0]
    pins=lambda db,sql:{r['id']:x.sha(x.canonical(dict(r))) for r in db.execute(sql)}
    p=copy.deepcopy(native);p.update(schema=post.PLAINTEXT_SCHEMA,author_attempt=19,run_limit=36,batch_limit=74,
        original_state=raw,state_sha256=x.sha(raw.encode()),failed_call_id=ident,failed_outputs=outputs,failed_format=format_record,
        local_calls=pins(store.db,'SELECT * FROM manual_calls ORDER BY rowid'),
        global_calls=pins(batch.db,"SELECT * FROM autonomy_calls WHERE kind='scientific' AND change_id='"+x.RUN+"' ORDER BY rowid"),
        batch_calls=pins(batch.db,"SELECT * FROM autonomy_calls WHERE kind='scientific' ORDER BY rowid"))
    for o,k,fn in originals:monkeypatch.setattr(o,k,fn)
    monkeypatch.setattr(scoped,'_validate',None)
    _,scoped_p,_=request.getfixturevalue('scoped_ready');_,recovery,_=request.getfixturevalue('recovery_ready')
    _,diagnostic=request.getfixturevalue('diagnostic_ready');_,smoke,post_p,_=request.getfixturevalue('response_ready')
    _,saved=request.getfixturevalue('extended')
    connect(request.getfixturevalue('fourth')[4],'b'*64,mechanical=request.getfixturevalue('mechanical')[4],mechanical_approval='a'*64,
        response=f[4],response_approval='9'*64,batch_extension=saved['extension'],batch_approval='e'*64,
        smoke=smoke,smoke_approval='d'*64,post_smoke=post_p,post_smoke_approval='c'*64,
        diagnostic=diagnostic,diagnostic_approval='8'*64,diagnostic_recovery=recovery,diagnostic_recovery_approval='7'*64,
        diagnostic_scoped=scoped_p,diagnostic_scoped_approval='6'*64,diagnostic_native=native,diagnostic_native_approval='5'*64,
        diagnostic_plaintext=p,diagnostic_plaintext_approval='4'*64)
    assert limits.local_limit(store,x.RUN,policy())==35
    before=[dict(r) for r in store.db.execute('SELECT * FROM manual_calls ORDER BY rowid')]
    assert post.activate(d,p,'4'*64,d.state/'cpu-diagnostic-plaintext-recovery')['status']=='READY_DIAGNOSTIC_AUTHOR19'
    assert not x.state(store).get('pending')
    assert before==[dict(r) for r in store.db.execute('SELECT * FROM manual_calls ORDER BY rowid')]
    return f,p,work


def test_corrective_author19_counts_normally_without_accepting_failed18(plaintext_ready):
    f,p,work=plaintext_ready;store,batch,c,d,*_=f
    before=[dict(r) for r in store.db.execute('SELECT * FROM manual_calls ORDER BY rowid')]
    global_before=[dict(r) for r in batch.db.execute("SELECT * FROM autonomy_calls WHERE kind='scientific' ORDER BY rowid")]
    old=copy.deepcopy(x.state(store))
    ident,n,receipt=store.reserve_call(x.RUN,'run_spec_author',c['source'],'astra/manual-test',policy(),{})
    assert n==19 and ident==post.call(p,'author')
    assert receipt['batch_accounting']['run_limit']==36 and receipt['batch_accounting']['batch_limit']==74
    assert receipt['accounting']['limit_amendment']['review_sha256']=='4'*64
    assert receipt[a.FIELD]['author_attempt']==19 and receipt[a.FIELD]['review_round']==14
    assert receipt[a.FIELD]['continuation_review_sha256']=='4'*64
    receipt['output_sha256']={'SPEC.proposed.md':'f'*64};store.finish_call(ident,receipt,'COMPLETE')
    a.accepted(d,{'id':ident,'stage':'run_spec_author','round':19})
    assert not store.db.execute('SELECT 1 FROM events WHERE id=?',('author-accepted:'+post.OPAQUE_AUTHOR,)).fetchone()
    assert [dict(r) for r in store.db.execute('SELECT * FROM manual_calls ORDER BY rowid')][:32]==before
    assert [dict(r) for r in batch.db.execute("SELECT * FROM autonomy_calls WHERE kind='scientific' ORDER BY rowid")][:70]==global_before
    assert Accounts(store).read()[1]['count']==33
    for stage in ['run_spec_author','run_spec_review','result_interpretation_author']:
        value=copy.deepcopy(old);value.update(phase=stage,rounds={'run_spec_author':19,'run_spec_review':14});d.save(value)
        charged=Accounts(store).read()
        with pytest.raises(ValueError):store.reserve_call(x.RUN,stage,c['source'],'astra/manual-test',policy(),{})
        assert Accounts(store).read()==charged
    post.originals(store,p,'4'*64)

def refused_fault(plaintext_ready,fault):
    f,p,work=plaintext_ready;store,batch,c,d,*_=f
    if fault=='accepted':a.accepted(d,{'id':post.OPAQUE_AUTHOR,'stage':'run_spec_author','round':18})
    elif fault in {'output','stream','format-receipt','format-config'}:
        name={'output':'notebook.patch.json','stream':'console.log','format-receipt':'.author-submission.json','format-config':'.author-runtime/config.json'}[fault]
        (work/name).write_bytes(b'changed')
    elif fault in {'local-row','global-row'}:
        db,table=(store.db,'manual_calls') if fault=='local-row' else (batch.db,'autonomy_calls')
        db.execute('UPDATE '+table+" SET receipt='{}' WHERE id=?",(post.OPAQUE_AUTHOR,))
    elif fault in {'native-grant','new-grant'}:
        event=post.profile({'schema':post.NATIVE_SCHEMA})['event'] if fault=='native-grant' else post.profile(p)['event']
        store.db.execute("UPDATE events SET payload='{}' WHERE id=?",(event,))
    elif fault in {'changed-plan','wrong-stage'}:
        value=x.state(store)
        if fault=='changed-plan':value['execution_package']={'changed':True}
        else:value['phase']='run_spec_review'
        d.save(value)
    elif fault=='daily':
        from datetime import datetime,timezone
        from test_scoped_revisions_limits import seed
        day=datetime.now(timezone.utc).date().isoformat();count=batch.db.execute('SELECT count(*) FROM autonomy_calls WHERE day=?',(day,)).fetchone()[0]
        seed(batch,50-count,kind='implementation_review',day=day)
    elif fault=='uncertain':batch.db.execute('INSERT INTO autonomy_calls VALUES(?,?,?,?,?,?,?,?)',('uncertain','review','other',1,'2000-01-01','UNCERTAIN','{}','{}'))
    before=Accounts(store).read();rows=[dict(r) for r in store.db.execute('SELECT * FROM manual_calls ORDER BY rowid')]
    with pytest.raises(ValueError):
        if fault=='duplicate-activation':post.activate(d,p,'4'*64,d.state/'duplicate')
        else:store.reserve_call(x.RUN,'run_spec_review' if fault=='wrong-stage' else 'run_spec_author',c['source'],'astra/manual-test',policy(),{})
    assert Accounts(store).read()==before
    assert rows==[dict(r) for r in store.db.execute('SELECT * FROM manual_calls ORDER BY rowid')]


def test_recovery_refuses_each_independent_fault_without_charge(plaintext_ready):
    # Reuse the expensive genuine synthetic review history, restoring independent
    # database/file snapshots between faults. No transaction is held around the
    # admission being tested; nested-transaction errors cannot create a false pass.
    f,p,work=plaintext_ready;store,batch,*_=f
    local=sqlite3.connect(':memory:');global_db=sqlite3.connect(':memory:')
    store.db.backup(local);batch.db.backup(global_db)
    files={name:(work/name).read_bytes() for name in ['notebook.patch.json','console.log',
        '.author-submission.json','.author-runtime/config.json']}
    try:
        for fault in ['accepted','output','stream','format-receipt','format-config','local-row','global-row',
                'native-grant','new-grant','changed-plan','duplicate-activation','daily','uncertain','wrong-stage']:
            try:refused_fault(plaintext_ready,fault)
            finally:
                assert not store.db.in_transaction and not batch.db.in_transaction
                local.backup(store.db);global_db.backup(batch.db)
                for name,raw in files.items():(work/name).write_bytes(raw)
    finally:local.close();global_db.close()
