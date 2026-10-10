"""Exact historical exception boundary; real full admission is rehearsed on DB copies."""
import copy,json,sqlite3
from pathlib import Path
from types import SimpleNamespace as NS
import pytest
from orchestrator import item4_smoke_response as post

@pytest.fixture
def history(monkeypatch):
    p=json.loads((Path(__file__).parents[1]/post.SNAPSHOT_DOCUMENT).read_bytes())
    p=p.get('sender_recovery',{}).get('previous_scope',p)
    q=post.profile(p);db=sqlite3.connect(':memory:');db.row_factory=sqlite3.Row
    db.execute('CREATE TABLE manual_calls (id TEXT,stage TEXT,attempt INTEGER,receipt TEXT)')
    accepted={};bindings={}
    for n,review in [(16,12),(17,12),(18,14),(19,14),(20,14),(21,15)]:
        ident=post.prior.sha((post.RUN+':run_spec_author:'+str(n)).encode())
        binding={'review_round':review,'review_call_id':'review-'+str(review),'author_call_id':ident}
        db.execute('INSERT INTO manual_calls VALUES(?,?,?,?)',(ident,'run_spec_author',n,json.dumps({'revision':binding})))
        accepted[ident]=n in (17,19,20,21);bindings[(review,n)]=binding
    for n in range(30):
        db.execute('INSERT INTO manual_calls VALUES(?,?,?,?)',('other-'+str(n),'run_spec_review',n,'{}'))
    p['local_calls']={r['id']:'synthetic' for r in db.execute('SELECT * FROM manual_calls')}
    store=NS(db=db);driver=NS(config={'run_id':post.RUN},store=store)
    accounting=NS(FIELD='revision',context=lambda *args:driver,
        _accepted=lambda st,row:accepted.get(row['id'],False),
        inspect=lambda *args:None,review_binding=lambda d,s,n,a:bindings[(n,a)])
    recovery=NS(role_limit=lambda *args:0)
    new={'review_round':15,'review_call_id':'review-15','author_call_id':post.call(p,'author')}
    monkeypatch.setattr(post,'scope',lambda *args:{})
    monkeypatch.setattr(post,'ready',lambda *args:None)
    monkeypatch.setattr(post,'granted',lambda *args:None)
    monkeypatch.setattr(post,'review_binding',lambda *args:new)
    monkeypatch.setattr(post.prior,'state',lambda st:{'phase':'run_spec_author','reason':q['event']})
    qualified=[];monkeypatch.setattr(post.fixture,'failure',lambda *args:qualified.append(True))
    post.connect_roles(accounting,recovery,p,'a'*64)
    yield NS(p=p,db=db,store=store,accounting=accounting,accepted=accepted,bindings=bindings,new=new,qualified=qualified)
    db.close()

def test_retains_exact_accepted_fixture_history_and_requires_exact_failed_author21(history):
    h=history;result=h.accounting.inspect(h.store,post.RUN,'run_spec_author')
    assert result['limit']==22 and result['binding']==h.new
    assert h.qualified==[True]

@pytest.mark.parametrize('fault',['unaccepted19','unaccepted20','unaccepted21','accepted18','wrong-row19','wrong-review20','reused-review','changed-receipt'])
def test_other_duplicates_or_changed_history_are_refused(history,fault):
    h=history
    ident=lambda n:post.prior.sha((post.RUN+':run_spec_author:'+str(n)).encode())
    if fault.startswith('unaccepted'):h.accepted[ident(int(fault[-2:]))]=False
    elif fault=='accepted18':h.accepted[ident(18)]=True
    elif fault=='reused-review':h.new['review_call_id']='review-14'
    elif fault=='wrong-row19':h.db.execute('UPDATE manual_calls SET id=? WHERE attempt=19',('forged',))
    elif fault=='wrong-review20':
        h.bindings[(14,20)]['review_round']=12;h.bindings[(12,20)]=h.bindings[(14,20)]
        h.db.execute('UPDATE manual_calls SET receipt=? WHERE attempt=20',(json.dumps({'revision':h.bindings[(12,20)]}),))
    else:h.db.execute('UPDATE manual_calls SET receipt=? WHERE attempt=20',(json.dumps({'revision':{**h.bindings[(14,20)],'extra':True}}),))
    with pytest.raises((ValueError,KeyError)):h.accounting.inspect(h.store,post.RUN,'run_spec_author')
    assert not h.qualified
