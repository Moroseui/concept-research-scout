"""Exact batch extension through real local/global reservation; no paid calls."""
import json
import pytest
from orchestrator import autonomy_limits as limits,item4_scoped_calls as scoped
from orchestrator import item4_review4_continuation as x,author_revision_accounting as a
from orchestrator.manual_executor import Accounts
from test_item4_review9_continuation import fifth,accepted,mechanical,fourth,third,setup,second,continuation,base_setup
from test_author_revision_accounting import reserve,review
from test_manual_lane import policy

@pytest.fixture
def extended(request,monkeypatch):
    original=scoped.connect
    monkeypatch.setattr(limits,'scientific_batch_allowance',limits.scientific_batch_allowance)
    saved={}
    def connect(*args,**kw):
        if kw.get('response') is not None:
            fixture=request.getfixturevalue('mechanical');store,batch,*_=fixture
            for n in range(38):
                ident=x.sha(('historical-scientific-'+str(n)).encode())
                batch.db.execute('INSERT INTO autonomy_calls VALUES(?,?,?,?,?,?,?,?)',
                    (ident,'scientific','prior-run',n+1,'2000-01-01','COMPLETE','{}','{}'))
            rows=[dict(r) for r in batch.db.execute("SELECT * FROM autonomy_calls WHERE kind='scientific' ORDER BY rowid")]
            assert len(rows)==60
            extension={'schema':'item4-batch-continuation/v1','run_id':x.RUN,'authority_sha256':x.AUTHORITY,
                'global_calls':{r['id']:x.sha(x.canonical(r)) for r in rows}}
            saved.update(rows=rows,extension=extension)
            kw.update(batch_extension=extension,batch_approval='e'*64)
        return original(*args,**kw)
    monkeypatch.setattr(scoped,'connect',connect)
    f=request.getfixturevalue('fifth')
    return f,saved


def test_exact_four_slots_count_all60_and_never65(extended,monkeypatch):
    from orchestrator import experiment_collection
    f,saved=extended;store,batch,c,d,*_=f
    receipt=accepted(f)
    assert receipt['batch_accounting']['batch_limit']==64
    row=batch.db.execute('SELECT binding FROM autonomy_calls WHERE id=?',(x.sha((x.RUN+':run_spec_author:14').encode()),)).fetchone()
    binding=json.loads(row[0]);assert binding['batch_continuation']['review_sha256']=='e'*64
    assert binding['batch_continuation']['checkpoint_sha256']==x.sha(x.canonical(saved['extension']))
    review(store,c,10,verdict='APPROVE')
    checked=[];monkeypatch.setattr(experiment_collection,'verified',lambda driver,value:checked.append(value['phase']))
    rounds={'run_spec_author':14,'run_spec_review':10}
    for stage in ('result_interpretation_author','result_interpretation_review'):
        value=x.state(store);value.update(phase=stage,reason=None,rounds=dict(rounds))
        store.db.execute('UPDATE manual_state SET payload=? WHERE id=1',(json.dumps(value),))
        ident,n,receipt=store.reserve_call(c['run_id'],stage,c['source'],'astra/manual-test',policy(),{})
        assert receipt['batch_accounting']['batch_limit']==64
        receipt['output_sha256']={'interpretation.md':'f'*64};store.finish_call(ident,receipt,'COMPLETE');rounds[stage]=1
        if stage.endswith('author'):a.accepted(d,{'id':ident,'stage':stage,'round':1})
    assert batch.db.execute("SELECT count(*) FROM autonomy_calls WHERE kind='scientific'").fetchone()[0]==64
    assert Accounts(store).read()[1]['count']==26
    assert len(checked)==6
    for stage in ('run_spec_author','run_spec_review','result_interpretation_author','result_interpretation_review'):
        with pytest.raises(ValueError):store.reserve_call(c['run_id'],stage,c['source'],'astra/manual-test',policy(),{})
    current={r['id']:dict(r) for r in batch.db.execute("SELECT * FROM autonomy_calls WHERE kind='scientific'")}
    assert [current[r['id']] for r in saved['rows']]==saved['rows']


@pytest.mark.parametrize('fault',['old-row','extra-row','daily','halt','pending','duplicate','early-interpretation','direct-global'])
def test_refusals_do_not_create_author14_or_charge(extended,fault):
    f,saved=extended;store,batch,c,d,*_=f
    if fault=='old-row':batch.db.execute("UPDATE autonomy_calls SET receipt='changed' WHERE id=?",(saved['rows'][-1]['id'],))
    elif fault=='extra-row':batch.db.execute('INSERT INTO autonomy_calls VALUES(?,?,?,?,?,?,?,?)',('extra','scientific','prior-run',39,'2000-01-01','COMPLETE','{}','{}'))
    elif fault=='daily':
        from datetime import datetime,timezone
        day=datetime.now(timezone.utc).date().isoformat()
        for n in range(50):batch.db.execute('INSERT INTO autonomy_calls VALUES(?,?,?,?,?,?,?,?)',('admin'+str(n),'review','repair',n+1,day,'COMPLETE','{}','{}'))
    elif fault=='halt':(batch.folder/'HALT').write_text('halt')
    elif fault=='pending':batch.db.execute('INSERT INTO autonomy_calls VALUES(?,?,?,?,?,?,?,?)',('uncertain','review','repair',1,'2000-01-01','UNCERTAIN','{}','{}'))
    elif fault=='duplicate':batch.db.execute('INSERT INTO autonomy_calls VALUES(?,?,?,?,?,?,?,?)',(x.sha((x.RUN+':run_spec_author:14').encode()),'scientific',x.RUN,23,'2000-01-01','UNCERTAIN','{}','{}'))
    before=Accounts(store).read()
    with pytest.raises(ValueError):
        if fault=='direct-global':batch.reserve_scientific(x.sha((x.RUN+':run_spec_author:14').encode()),x.RUN,'run_spec_author',c['source'],{})
        elif fault=='early-interpretation':store.reserve_call(x.RUN,'result_interpretation_author',c['source'],'astra/manual-test',policy(),{})
        else:reserve(store,c)
    assert Accounts(store).read()==before
    assert store.db.execute('SELECT count(*) FROM manual_calls').fetchone()[0]==22


def test_other_runs_keep_default60_and_default_hook_is60(extended):
    f,_=extended;store,batch,c,d,*_=f
    assert limits.SCIENTIFIC_BATCH==60 and limits.DAILY==50
    assert limits.scientific_batch_allowance(batch,'other','run_spec_author','id','a'*40,{})=={'limit':60}


def test_without_extension_real_batch60_refuses(fifth):
    store,batch,c,d,*_=fifth
    for n in range(38):batch.db.execute('INSERT INTO autonomy_calls VALUES(?,?,?,?,?,?,?,?)',('prior'+str(n),'scientific','prior-run',n+1,'2000-01-01','COMPLETE','{}','{}'))
    with pytest.raises(ValueError,match='AUTONOMY_BATCH_CALL_LIMIT'):reserve(store,c)
    assert Accounts(store).read()[1]['count']==22
