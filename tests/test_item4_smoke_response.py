"""Synthetic native evidence and real SQLite admission; no provider/model calls."""
import json
import pytest
from orchestrator import item4_smoke_response as post,item4_smoke_review as smoke,item4_scoped_calls as scoped
from orchestrator import item4_review4_continuation as x,author_revision_accounting as a
from orchestrator import autonomy_limits as limits,manual_recovery,experiment_collection,review_submission as rs,private_records as pr
from orchestrator.manual_executor import ManualExecutor,Accounts
from orchestrator.autonomy_accounting import BatchAccounts
from test_item4_smoke_review_calls import smoke_ready,extended,fifth,accepted,mechanical,fourth,third,setup,second,continuation,base_setup
from test_author_revision_accounting import review
from test_manual_lane import policy

@pytest.fixture
def response_ready(request,monkeypatch):
    connect=scoped.connect
    originals=[(o,k,getattr(o,k)) for o,k in [(limits,k) for k in
        ('local_limit','global_limit','allowance','cap_authority','scientific_batch_allowance')]+
        [(ManualExecutor,'reserve_call'),(BatchAccounts,'reserve_scientific')]]
    f,p,_=request.getfixturevalue('smoke_ready');store,batch,c,d,*_=f
    value=x.state(store)
    submit=rs.submit
    def synthetic_budget(work,pin,decision):
        if decision['findings'] and decision['findings'][0]['category']=='budget':
            decision['findings'][0]['id']='STAGE1-full-projection-exceeds-authorized-caps'
        return submit(work,pin,decision)
    monkeypatch.setattr(rs,'submit',synthetic_budget)
    work,_=review(store,c,11,category='budget')
    value.update(phase='MODEL_RUNNING',pending={'id':smoke.CALL,'stage':'run_spec_review','round':11,'workspace':str(work)})
    pr.atomic(work/'input-measurement.json',{'synthetic_fixture':True})
    monkeypatch.setattr(smoke,'verify_delivered',lambda *args:None)
    d.save=lambda v:store.db.execute('UPDATE manual_state SET payload=? WHERE id=1',(json.dumps(v),))
    d.status=lambda:x.state(store)
    d.criticism=lambda *args:None
    smoke.finish(d,value,p,'d'*64)
    raw=store.db.execute('SELECT payload FROM manual_state WHERE id=1').fetchone()[0]
    def pins(db,sql):return {r['id']:x.sha(x.canonical(dict(r))) for r in db.execute(sql)}
    frozen={'schema':'item4-post-smoke-response/v1','run_id':x.RUN,'authority_sha256':x.AUTHORITY,
        'author_attempt':15,'review_attempt':12,'run_limit':29,'batch_limit':67,'execution_authorized':False,
        'configuration_sha256':x.sha((d.state/'lane.json').read_bytes()),'original_state':raw,'state_sha256':x.sha(raw.encode()),
        'local_calls':pins(store.db,'SELECT * FROM manual_calls ORDER BY rowid'),
        'global_calls':pins(batch.db,"SELECT * FROM autonomy_calls WHERE kind='scientific' AND change_id='"+x.RUN+"' ORDER BY rowid"),
        'batch_calls':pins(batch.db,"SELECT * FROM autonomy_calls WHERE kind='scientific' ORDER BY rowid"),
        'assessment':value['smoke_review'],'assessment_sha256':x.sha(x.canonical(value['smoke_review']))}
    for o,k,fn in originals:monkeypatch.setattr(o,k,fn)
    monkeypatch.setattr(scoped,'_validate',None)
    fourth_grant=request.getfixturevalue('fourth')[4];mechanic=request.getfixturevalue('mechanical')[4]
    _,saved=request.getfixturevalue('extended');response=f[4]
    connect(fourth_grant,'b'*64,mechanical=mechanic,mechanical_approval='a'*64,
        response=response,response_approval='9'*64,batch_extension=saved['extension'],batch_approval='e'*64,
        smoke=p,smoke_approval='d'*64,post_smoke=frozen,post_smoke_approval='c'*64)
    assert limits.local_limit(store,x.RUN,policy())==27
    post.activate(d,frozen,'c'*64,d.state/'post-smoke-response')
    return f,p,frozen,work


def reserve_author(v):
    f,*_=v;store,batch,c,d,*_=f
    return store.reserve_call(x.RUN,'run_spec_author',c['source'],'astra/manual-test',policy(),{})


def accepted_author(v):
    f,p,frozen,work=v;store,batch,c,d,*_=f
    ident,n,receipt=reserve_author(v)
    receipt['output_sha256']={'SPEC.proposed.md':'f'*64}
    store.finish_call(ident,receipt,'COMPLETE');a.accepted(d,{'id':ident,'stage':'run_spec_author','round':n})
    value=x.state(store);value.update(phase='run_spec_review',rounds={'run_spec_author':15,'run_spec_review':11})
    d.save(value);return receipt


def test_exact_response_and_reserved_final_pair(response_ready,monkeypatch):
    f,p,frozen,work=response_ready;store,batch,c,d,*_=f
    receipt=accepted_author(response_ready)
    assert receipt['batch_accounting']['run_limit']==29 and receipt['batch_accounting']['batch_limit']==67
    assert receipt[a.FIELD]['proposal_only'] is True and receipt[a.FIELD]['review_sha256']==frozen['assessment']['report_sha256']
    assert receipt['accounting']['limit_amendment']['review_sha256']=='c'*64
    assert manual_recovery.role_limit(store,x.RUN,'run_spec_review')==12
    value=x.state(store);work12,_=review(store,c,12,verdict='APPROVE')
    value.update(phase='MODEL_RUNNING',pending={'id':post.REVIEW,'stage':'run_spec_review','round':12,'workspace':str(work12)})
    old=json.loads(frozen['original_state'])
    result=post.finish_review(d,value,frozen,'c'*64)
    assert result['phase']=='BLOCKED' and result['reason']=='POST_SMOKE_RESPONSE_APPROVE_EXECUTION_HELD'
    for key in ('review','spec_review','reviewed_execution','smoke_review'):assert result.get(key)==old.get(key)
    assert all(result['post_smoke_response'][k] is False for k in ('execution_authorized','full_training_admitted','coverage_released'))
    assert Accounts(store).read()[1]['count']==27
    # A forged state change alone still cannot spend the final interpretation pair.
    value=x.state(store);value.update(phase='result_interpretation_author');d.save(value)
    before=Accounts(store).read()
    with pytest.raises((ValueError,KeyError,FileNotFoundError)):
        store.reserve_call(x.RUN,'result_interpretation_author',c['source'],'astra/manual-test',policy(),{})
    assert Accounts(store).read()==before
    complete=[];monkeypatch.setattr(experiment_collection,'verified',lambda d,v:complete.append(v['phase']))
    rounds={'run_spec_author':15,'run_spec_review':12}
    for stage in ('result_interpretation_author','result_interpretation_review'):
        value=x.state(store);value.update(phase=stage,rounds=dict(rounds));d.save(value)
        ident,n,r=store.reserve_call(x.RUN,stage,c['source'],'astra/manual-test',policy(),{})
        r['output_sha256']={'interpretation.md':'f'*64};store.finish_call(ident,r,'COMPLETE');rounds[stage]=1
        if stage.endswith('author'):a.accepted(d,{'id':ident,'stage':stage,'round':1})
    assert len(complete)==6 and Accounts(store).read()[1]['count']==29
    assert batch.db.execute("SELECT count(*) FROM autonomy_calls WHERE kind='scientific'").fetchone()[0]==67
    post.originals(store,frozen,'c'*64)
    with pytest.raises(ValueError):reserve_author(response_ready)


@pytest.mark.parametrize('fault',['old-local','old-global','grant','pending','wrong-phase','wrong-round','execution-authority','daily','uncertain','early-final','direct-global'])
def test_refusals_do_not_charge(response_ready,fault):
    f,p,frozen,work=response_ready;store,batch,c,d,*_=f
    if fault.startswith('old-'):
        db,table,pins=(store.db,'manual_calls',frozen['local_calls']) if fault=='old-local' else (batch.db,'autonomy_calls',frozen['batch_calls'])
        db.execute('UPDATE '+table+" SET receipt='changed' WHERE id=?",(next(iter(pins)),))
    elif fault=='grant':store.db.execute('DELETE FROM events WHERE id=?',(post.EVENT,))
    elif fault in ('pending','wrong-phase','wrong-round','execution-authority'):
        v=x.state(store)
        if fault=='pending':v['pending']={'id':'uncertain'}
        elif fault=='wrong-phase':v['phase']='EXECUTE_EXPERIMENT'
        elif fault=='wrong-round':v['rounds']['run_spec_review']=12
        else:v['reviewed_execution']={'forged':True}
        d.save(v)
    elif fault=='daily':
        from datetime import datetime,timezone
        from test_scoped_revisions_limits import seed
        day=datetime.now(timezone.utc).date().isoformat();n=batch.db.execute('SELECT count(*) FROM autonomy_calls WHERE day=?',(day,)).fetchone()[0]
        seed(batch,50-n,kind='implementation_review',day=day)
    elif fault=='uncertain':batch.db.execute('INSERT INTO autonomy_calls VALUES(?,?,?,?,?,?,?,?)',('unresolved','review','repair',1,'2000-01-01','UNCERTAIN','{}','{}'))
    before=Accounts(store).read();rows=[dict(r) for r in store.db.execute('SELECT * FROM manual_calls')]
    with pytest.raises(ValueError):
        if fault=='direct-global':batch.reserve_scientific(post.AUTHOR,x.RUN,'run_spec_author',c['source'],{})
        elif fault=='early-final':store.reserve_call(x.RUN,'result_interpretation_author',c['source'],'astra/manual-test',policy(),{})
        else:reserve_author(response_ready)
    assert Accounts(store).read()==before
    assert rows==[dict(r) for r in store.db.execute('SELECT * FROM manual_calls')]


@pytest.mark.parametrize('file',['review.json','console.log',rs.RECORD,rs.CONFIG,'prompt.md'])
def test_changed_genuine_review_proof_cannot_unlock_author(response_ready,file):
    f,p,frozen,work=response_ready;store,batch,c,d,*_=f
    target=work/file;target.chmod(0o600);pr.write_bytes(target,target.read_bytes()+b' ')
    before=Accounts(store).read()
    with pytest.raises(ValueError):reserve_author(response_ready)
    assert Accounts(store).read()==before


def test_scope_cannot_change_caps_or_execution_permission(response_ready):
    f,p,frozen,work=response_ready
    for key,new in [('run_limit',30),('batch_limit',68),('execution_authorized',True),('author_attempt',16),('review_attempt',13)]:
        changed={**frozen,key:new}
        with pytest.raises(ValueError):post.scope(changed,'c'*64)
    assert limits.DAILY==50 and limits.SCIENTIFIC_BATCH==60


def test_no_second_activation(response_ready):
    f,p,frozen,work=response_ready;store,batch,c,d,*_=f
    before=Accounts(store).read()
    with pytest.raises(ValueError):post.activate(d,frozen,'c'*64,d.state/'second')
    assert Accounts(store).read()==before
