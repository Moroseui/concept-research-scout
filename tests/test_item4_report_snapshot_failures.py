"""All four original failed assets remain mandatory; no native success inferred."""
import copy,json,sqlite3
from pathlib import Path
from types import SimpleNamespace as NS
import pytest
from orchestrator import item4_fixture_correction as fixture,item4_smoke_response as post

@pytest.fixture
def history(monkeypatch,tmp_path):
    root=Path(__file__).parents[1]
    scopes=[json.loads((root/name).read_bytes()) for name in (fixture.DOCUMENT,fixture.AUDIT_DOCUMENT,fixture.SNAPSHOT_DOCUMENT)]
    third=json.loads((root/'docs/ITEM4_PROGRESS_NATIVE_FAILURE_PRIVATE.json').read_bytes())
    db=sqlite3.connect(':memory:');db.row_factory=sqlite3.Row
    rows=[p['native_failure']['asset_row'] for p in scopes]+[third['third_failed_asset']]
    db.execute('CREATE TABLE autonomy_assets ('+','.join(k+(' INTEGER' if isinstance(v,int) else ' REAL' if isinstance(v,float) else ' TEXT') for k,v in rows[0].items())+')')
    for row in rows:db.execute('INSERT INTO autonomy_assets ('+','.join(row)+') VALUES('+','.join('?' for _ in row)+')',list(row.values()))
    monkeypatch.setattr(fixture,'ROOT',tmp_path)
    for key,folder in [('STATE','first'),('AUDIT_STATE','second'),('SNAPSHOT_STATE','fourth')]:monkeypatch.setattr(fixture,key,tmp_path/folder)
    proofs=[];paths=[]
    for scope in scopes:
        q=fixture.parameters(scope);paths.append(q['state']);f=scope['native_failure']
        for name in f['files']:
            path=q['state']/name;path.parent.mkdir(parents=True,exist_ok=True)
            raw=('synthetic preserved '+q['asset']+'/'+name).encode();path.write_bytes(raw);f['files'][name]=fixture.sha(raw)
        proofs.append({'source':f['source'],'implementation_review_sha256':f['implementation_review_sha256'],
            'asset_id':q['asset'],'module_sha256':q['module'],'exit_code':1,'status':'FAIL',
            'package_unchanged':True,'scientific_acceptance':False,'no_automatic_retry':True})
    for name,scope in zip((fixture.DOCUMENT,fixture.AUDIT_DOCUMENT,fixture.SNAPSHOT_DOCUMENT),scopes):
        path=tmp_path/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(scope))
    (tmp_path/'docs/ITEM4_PROGRESS_NATIVE_FAILURE_PRIVATE.json').write_text(json.dumps(third))
    third_proof=copy.deepcopy(third['qualification'])
    for key,n in [('_verifier',0),('_audit_verifier',1),('_snapshot_verifier',2)]:
        monkeypatch.setattr(fixture,key,lambda n=n:proofs[n])
    monkeypatch.setattr(fixture,'_progress_verifier',lambda:third_proof)
    yield NS(store=NS(batch=NS(db=db)),db=db,p=scopes[2],proofs=proofs+[third_proof],paths=paths,rows=rows)
    db.close()

def test_all_four_original_failures_remain_required(history):
    h=history;before=[tuple(r) for r in h.db.execute('SELECT * FROM autonomy_assets')]
    assert fixture.failure(h.store,h.p)==h.p['native_failure']
    assert [tuple(r) for r in h.db.execute('SELECT * FROM autonomy_assets')]==before

@pytest.mark.parametrize('index',range(4))
@pytest.mark.parametrize('fault',['reservation','status','fake-pass'])
def test_no_failure_or_charge_can_be_dropped(history,index,fault):
    h=history
    if fault=='reservation':h.db.execute('UPDATE autonomy_assets SET reserved_micro_usd=0 WHERE id=?',(h.rows[index]['id'],))
    elif fault=='status':h.db.execute("UPDATE autonomy_assets SET status='READY' WHERE id=?",(h.rows[index]['id'],))
    else:h.proofs[index]['status']='PASS'
    with pytest.raises(ValueError):fixture.failure(h.store,h.p)

@pytest.mark.parametrize('index',range(3))
def test_bound_original_streams_cannot_change(history,index):
    h=history;(h.paths[index]/'provider/stdout.bin').write_bytes(b'fabricated success')
    with pytest.raises(ValueError):fixture.failure(h.store,h.p)

def test_snapshot_checkpoint_exact_author_and_caps():
    p=json.loads((Path(__file__).parents[1]/fixture.SNAPSHOT_DOCUMENT).read_bytes())
    p=p.get('sender_recovery',{}).get('previous_scope',p)
    assert post.scope(p,'a'*64)['rounds']=={'run_spec_author':21,'run_spec_review':15}
    q=post.profile(p);assert (q['author'],q['count'],q['batch'],q['limit'],q['batch_limit'])==(22,36,74,40,78)
    for key,value in [('run_limit',41),('batch_limit',79),('author_attempt',23),('automatic_retry',True),('execution_authorized',True),('diagnostic_micro_usd',25000001),('stage1_micro_usd',150000001)]:
        bad=copy.deepcopy(p);bad[key]=value
        with pytest.raises(ValueError):post.scope(bad,'a'*64)
