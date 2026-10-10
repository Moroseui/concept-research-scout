"""Real SQLite admission with synthetic scientific outputs; no model/provider calls."""
import json
import pytest
from orchestrator import item4_scoped_calls as scoped,item4_smoke_review as smoke
from orchestrator import item4_review4_continuation as x,author_revision_accounting as a
from orchestrator import autonomy_limits as limits,experiment_collection,manual_recovery
from orchestrator.manual_executor import ManualExecutor,Accounts
from orchestrator.autonomy_accounting import BatchAccounts
from test_item4_batch_continuation import extended,fifth,accepted,mechanical,fourth,third,setup,second,continuation,base_setup
from test_author_revision_accounting import review
from test_manual_lane import policy

@pytest.fixture
def smoke_ready(request,monkeypatch):
    connect=scoped.connect
    monkeypatch.setattr(manual_recovery,'role_limit',manual_recovery.role_limit)
    original=[(o,k,getattr(o,k)) for o,k in [(limits,k) for k in
        ('local_limit','global_limit','allowance','cap_authority','scientific_batch_allowance')]+
        [(ManualExecutor,'reserve_call'),(BatchAccounts,'reserve_scientific')]]
    f,saved=request.getfixturevalue('extended');store,batch,c,d,response,*_=f
    accepted(f);review(store,c,10)
    value=x.state(store);value.update(phase='EXECUTE_EXPERIMENT',reason='VALIDATION_ONLY',
        rounds={'run_spec_author':14,'run_spec_review':10})
    raw=json.dumps(value);store.db.execute('UPDATE manual_state SET payload=? WHERE id=1',(raw,))
    def rows(db,sql):return {r['id']:x.sha(x.canonical(dict(r))) for r in db.execute(sql)}
    p={'schema':'item4-smoke-review-checkpoint/v1','run_id':x.RUN,'source':c['source'],
        'authority_sha256':x.AUTHORITY,'direction_sha256':smoke.DIRECTION,
        'configuration_sha256':x.sha((d.state/'lane.json').read_bytes()),
        'original_state':raw,'state_sha256':x.sha(raw.encode()),
        'local_calls':rows(store.db,'SELECT * FROM manual_calls ORDER BY rowid'),
        'global_calls':rows(batch.db,"SELECT * FROM autonomy_calls WHERE kind='scientific' AND change_id='"+x.RUN+"' ORDER BY rowid"),
        'batch_calls':rows(batch.db,"SELECT * FROM autonomy_calls WHERE kind='scientific' ORDER BY rowid"),
        'account_sha256':x.sha(x.canonical([dict(r) for r in store.db.execute('SELECT * FROM manual_account ORDER BY id')])),
        'fits':[{'job':'synthetic-'+str(i),'fit_id':fit} for i,fit in enumerate(smoke.FITS)],'package_files':{}}
    for o,k,fn in original:monkeypatch.setattr(o,k,fn)
    monkeypatch.setattr(scoped,'_validate',None)
    fourth_grant=request.getfixturevalue('fourth')[4];mechanic=request.getfixturevalue('mechanical')[4]
    connect(fourth_grant,'b'*64,mechanical=mechanic,mechanical_approval='a'*64,
        response=response,response_approval='9'*64,batch_extension=saved['extension'],batch_approval='e'*64,
        smoke=p,smoke_approval='d'*64)
    checked=[]
    monkeypatch.setattr(smoke,'evidence',lambda driver,value,p,approval:checked.append(value['phase']) or [])
    assert limits.local_limit(store,x.RUN,policy())==26
    smoke.activate(d,p,'d'*64,d.state/'smoke-review-grant')
    return f,p,checked


def reserve11(v):
    f,p,checked=v;store,batch,c,d,*_=f
    return store.reserve_call(x.RUN,'run_spec_review',c['source'],'astra/manual-test',policy(),{})


def test_exact_one_review_and_final_pair_count_27_and_65(smoke_ready,monkeypatch):
    f,p,checked=smoke_ready;store,batch,c,d,*_=f
    before=Accounts(store).read();ident,n,receipt=reserve11(smoke_ready)
    assert (ident,n)==(smoke.CALL,11)
    assert receipt['batch_accounting']['run_limit']==27
    assert receipt['batch_accounting']['batch_limit']==65
    assert receipt['accounting']['limit_amendment']['review_sha256']=='d'*64
    assert Accounts(store).read()[1]['count']==before[1]['count']+1==25
    store.finish_call(ident,receipt,'COMPLETE')
    complete=[];monkeypatch.setattr(experiment_collection,'verified',lambda d,v:complete.append(v['phase']))
    rounds={'run_spec_author':14,'run_spec_review':11}
    for stage in ('result_interpretation_author','result_interpretation_review'):
        value=x.state(store);value.update(phase=stage,rounds=dict(rounds))
        store.db.execute('UPDATE manual_state SET payload=? WHERE id=1',(json.dumps(value),))
        ident,n,receipt=store.reserve_call(x.RUN,stage,c['source'],'astra/manual-test',policy(),{})
        receipt['output_sha256']={'interpretation.md':'f'*64};store.finish_call(ident,receipt,'COMPLETE')
        rounds[stage]=1
        if stage.endswith('author'):a.accepted(d,{'id':ident,'stage':stage,'round':1})
    assert len(complete)==6
    assert Accounts(store).read()[1]['count']==27
    assert batch.db.execute("SELECT count(*) FROM autonomy_calls WHERE kind='scientific'").fetchone()[0]==65
    smoke.originals(store,p,'d'*64)
    for stage in ('run_spec_author','run_spec_review','result_interpretation_author','result_interpretation_review'):
        with pytest.raises(ValueError):store.reserve_call(x.RUN,stage,c['source'],'astra/manual-test',policy(),{})


@pytest.mark.parametrize('fault',['missing-results','changed-results','early-final','wrong-round','wrong-phase','pending',
    'local-original','global-original','batch-original','grant','day','batch-halt','account-halt','uncertain','direct-global'])
def test_refusals_preserve_calls_and_account(smoke_ready,monkeypatch,fault):
    f,p,checked=smoke_ready;store,batch,c,d,*_=f
    if fault in ('missing-results','changed-results'):
        def refuse(*args):raise ValueError('EXPERIMENT_COLLECTION_'+fault)
        monkeypatch.setattr(smoke,'evidence',refuse)
    elif fault in ('wrong-round','wrong-phase','pending'):
        v=x.state(store)
        if fault=='wrong-round':v['rounds']['run_spec_review']=11
        elif fault=='wrong-phase':v['phase']='EXECUTE_EXPERIMENT'
        else:v['pending']={'id':'uncertain'}
        store.db.execute('UPDATE manual_state SET payload=? WHERE id=1',(json.dumps(v),))
    elif fault.endswith('-original'):
        table,db,pins=('manual_calls',store.db,p['local_calls']) if fault=='local-original' else ('autonomy_calls',batch.db,p['batch_calls'] if fault=='batch-original' else p['global_calls'])
        ident=next(reversed(pins)) if fault=='batch-original' else next(iter(pins))
        db.execute('UPDATE '+table+" SET receipt='changed' WHERE id=?",(ident,))
    elif fault=='grant':store.db.execute('DELETE FROM events WHERE id=?',(smoke.EVENT,))
    elif fault=='day':
        from datetime import datetime,timezone
        from test_scoped_revisions_limits import seed
        # Existing synthetic calls may be dated today: add until exactly50.
        day=datetime.now(timezone.utc).date().isoformat()
        n=batch.db.execute('SELECT count(*) FROM autonomy_calls WHERE day=?',(day,)).fetchone()[0]
        seed(batch,50-n,kind='implementation_review',day=day)
    elif fault=='batch-halt':(batch.folder/'HALT').write_text('stop')
    elif fault=='account-halt':
        version,state=Accounts(store).read();state['halted']=True;assert Accounts(store).cas(version,state)
    elif fault=='uncertain':batch.db.execute('INSERT INTO autonomy_calls VALUES(?,?,?,?,?,?,?,?)',('unresolved','review','repair',1,'2000-01-01','UNCERTAIN','{}','{}'))
    before=Accounts(store).read();local=[dict(r) for r in store.db.execute('SELECT * FROM manual_calls')]
    with pytest.raises(ValueError):
        if fault=='direct-global':batch.reserve_scientific(smoke.CALL,x.RUN,'run_spec_review',c['source'],{})
        elif fault=='early-final':store.reserve_call(x.RUN,'result_interpretation_author',c['source'],'astra/manual-test',policy(),{})
        else:reserve11(smoke_ready)
    assert Accounts(store).read()==before
    after=[dict(r) for r in store.db.execute('SELECT * FROM manual_calls')]
    if fault=='account-halt':
        # Ordinary admission preserves its refusal record without a model call
        # or accounting increment; never delete/relabel that original.
        assert after[:-1]==local and after[-1]['id']==smoke.CALL
        assert after[-1]['status']=='BLOCKED_BEFORE_MODEL'
    else:assert after==local


def test_final_pair_still_needs_whole_plan(smoke_ready):
    f,p,_=smoke_ready;store,batch,c,d,*_=f
    ident,n,receipt=reserve11(smoke_ready);store.finish_call(ident,receipt,'COMPLETE')
    value=x.state(store);value.update(phase='result_interpretation_author',rounds={'run_spec_author':14,'run_spec_review':11})
    store.db.execute('UPDATE manual_state SET payload=? WHERE id=1',(json.dumps(value),))
    before=Accounts(store).read()
    with pytest.raises((ValueError,KeyError,FileNotFoundError)):
        store.reserve_call(x.RUN,'result_interpretation_author',c['source'],'astra/manual-test',policy(),{})
    assert Accounts(store).read()==before


def test_second_activation_refuses_and_preserves_original(smoke_ready):
    f,p,_=smoke_ready;store,batch,c,d,*_=f
    assert (d.state/'smoke-review-grant/original-state.json').read_text()==p['original_state']
    before=Accounts(store).read()
    with pytest.raises(ValueError):smoke.activate(d,p,'d'*64,d.state/'another-grant')
    assert Accounts(store).read()==before
    assert limits.scientific_batch_allowance(batch,'other','run_spec_author','id','a'*40,{})=={'limit':60}
    assert limits.DAILY==50
