"""Synthetic accounting history plus immutable real failure pins; no model/compute."""
import copy,json,sqlite3
from pathlib import Path
from types import SimpleNamespace as NS
import pytest
from orchestrator import item4_fixture_correction as fixture,item4_smoke_response as post,item4_scoped_calls as scoped
from orchestrator import item4_review4_continuation as x,author_revision_accounting as a,autonomy_limits as limits
from orchestrator import manual_recovery
from orchestrator.manual_executor import ManualExecutor,Accounts
from orchestrator.autonomy_accounting import BatchAccounts
from orchestrator.modal_budget import ComputeAccounts
from test_item4_diagnostic_plaintext_recovery import (plaintext_ready,native_ready,scoped_ready,recovery_ready,
 diagnostic_ready,baseline,diagnostic_plan,response_ready,accepted_author,smoke_ready,extended,fifth,accepted,
 mechanical,fourth,third,setup,second,continuation,base_setup)
from test_manual_lane import policy
from test_author_revision_accounting import review
ROOT=Path(__file__).parents[1]
REAL=json.loads((ROOT/fixture.DOCUMENT).read_bytes())

def qualification(p):
 f=p['native_failure']
 return {'source':f['source'],'implementation_review_sha256':f['implementation_review_sha256'],
 'asset_id':fixture.ASSET,'module_sha256':fixture.MODULE,'exit_code':1,'status':'FAIL','package_unchanged':True,
 'scientific_acceptance':False,'no_automatic_retry':True}

@pytest.fixture
def fixture_ready(request,monkeypatch,tmp_path):
 connect=scoped.connect
 originals=[(o,k,getattr(o,k)) for o,k in [(limits,k) for k in
  ('local_limit','global_limit','allowance','cap_authority','scientific_batch_allowance')]+
  [(ManualExecutor,'reserve_call'),(BatchAccounts,'reserve_scientific')]]
 f,plaintext,_=request.getfixturevalue('plaintext_ready');store,batch,c,d,*_=f
 ident,n,receipt=store.reserve_call(x.RUN,'run_spec_author',c['source'],'astra/manual-test',policy(),{})
 assert n==19
 work=d.state.parent/(d.state.name+'-scientific-workspaces')/'run_spec_author-19';work.mkdir(parents=True)
 files={'SPEC.proposed.md':b'accepted19','notebook.patch.json':b'synthetic patch','execution.plan.json':b'synthetic plan'}
 for name,raw in files.items():(work/name).write_bytes(raw)
 receipt.update(workspace=str(work),output_sha256={k:x.sha(v) for k,v in files.items()})
 store.finish_call(ident,receipt,'COMPLETE');a.accepted(d,{'id':ident,'stage':'run_spec_author','round':19})
 value=x.state(store);value.update(phase='BLOCKED',reason='NATIVE_HARNESS_ACCEPTED_NATIVE_EVIDENCE_REQUIRED',rounds={'run_spec_author':19,'run_spec_review':14});value.pop('pending',None);d.save(value)
 raw=store.db.execute('SELECT payload FROM manual_state WHERE id=1').fetchone()[0]
 pins=lambda db,sql:{r['id']:x.sha(x.canonical(dict(r))) for r in db.execute(sql)}
 p=copy.deepcopy(plaintext)
 for key in ['failed_call_id','failed_outputs','failed_format']:p.pop(key)
 p.update(schema=fixture.SCHEMA,author_attempt=20,run_limit=37,batch_limit=75,direction_sha256=fixture.DIRECTION,
 original_state=raw,state_sha256=x.sha(raw.encode()),reference_native_harness_sha256=fixture.MODULE,
 local_calls=pins(store.db,'SELECT * FROM manual_calls ORDER BY rowid'),
 global_calls=pins(batch.db,"SELECT * FROM autonomy_calls WHERE kind='scientific' AND change_id='"+x.RUN+"' ORDER BY rowid"),
 batch_calls=pins(batch.db,"SELECT * FROM autonomy_calls WHERE kind='scientific' ORDER BY rowid"))
 p['fixture_reference']={'module_sha256':fixture.MODULE,'accepted_author':dict(store.db.execute('SELECT * FROM manual_calls WHERE id=?',(ident,)).fetchone()),
 'accepted_event':json.loads(store.db.execute('SELECT payload FROM events WHERE id=?',('author-accepted:'+ident,)).fetchone()[0])}
 p['native_failure']=copy.deepcopy(REAL['native_failure']);ComputeAccounts(batch)
 row=p['native_failure']['asset_row'];batch.db.execute('INSERT INTO autonomy_assets('+','.join(row)+') VALUES('+','.join('?' for _ in row)+')',list(row.values()))
 state=tmp_path/'actual-failure';state.mkdir();monkeypatch.setattr(fixture,'STATE',state)
 for name in p['native_failure']['files']:
  path=state/name;path.parent.mkdir(parents=True,exist_ok=True);body=('synthetic preserved '+name).encode();path.write_bytes(body);p['native_failure']['files'][name]=x.sha(body)
 monkeypatch.setattr(fixture,'_verifier',lambda:qualification(p))
 for o,k,fn in originals:monkeypatch.setattr(o,k,fn)
 monkeypatch.setattr(scoped,'_validate',None)
 _,native,_=request.getfixturevalue('native_ready');_,scoped_p,_=request.getfixturevalue('scoped_ready');_,recovery,_=request.getfixturevalue('recovery_ready')
 _,diagnostic=request.getfixturevalue('diagnostic_ready');_,smoke,post_p,_=request.getfixturevalue('response_ready');_,saved=request.getfixturevalue('extended')
 connect(request.getfixturevalue('fourth')[4],'b'*64,mechanical=request.getfixturevalue('mechanical')[4],mechanical_approval='a'*64,
 response=f[4],response_approval='9'*64,batch_extension=saved['extension'],batch_approval='e'*64,
 smoke=smoke,smoke_approval='d'*64,post_smoke=post_p,post_smoke_approval='c'*64,
 diagnostic=diagnostic,diagnostic_approval='8'*64,diagnostic_recovery=recovery,diagnostic_recovery_approval='7'*64,
 diagnostic_scoped=scoped_p,diagnostic_scoped_approval='6'*64,diagnostic_native=native,diagnostic_native_approval='5'*64,
 diagnostic_plaintext=plaintext,diagnostic_plaintext_approval='4'*64,diagnostic_fixture=p,diagnostic_fixture_approval='3'*64)
 assert limits.local_limit(store,x.RUN,policy())==36
 assert post.activate(d,p,'3'*64,d.state/'cpu-diagnostic-fixture-correction')['status']=='READY_DIAGNOSTIC_AUTHOR20'
 return f,p,work


def test_correction_is_counted_and_review_requires_accepted_author(fixture_ready,monkeypatch):
 f,p,work=fixture_ready;store,batch,c,d,*_=f
 before=[dict(r) for r in store.db.execute('SELECT * FROM manual_calls ORDER BY rowid')]
 oldglobal=[dict(r) for r in batch.db.execute("SELECT * FROM autonomy_calls WHERE kind='scientific' ORDER BY rowid")]
 ident,n,receipt=store.reserve_call(x.RUN,'run_spec_author',c['source'],'astra/manual-test',policy(),{})
 assert n==20 and receipt['batch_accounting']['run_limit']==37 and receipt['batch_accounting']['batch_limit']==75
 assert receipt[a.FIELD]['continuation_review_sha256']=='3'*64
 receipt['output_sha256']={'SPEC.proposed.md':'f'*64};store.finish_call(ident,receipt,'COMPLETE')
 value=x.state(store);value.update(phase='run_spec_review',rounds={'run_spec_author':20,'run_spec_review':14});d.save(value)
 charged=Accounts(store).read()
 with pytest.raises(ValueError,match='ACCEPTED_AUTHOR'):store.reserve_call(x.RUN,'run_spec_review',c['source'],'astra/manual-test',policy(),{})
 assert Accounts(store).read()==charged
 a.accepted(d,{'id':ident,'stage':'run_spec_author','round':20})
 monkeypatch.setattr(post,'executable_candidate',lambda *args:{'execution_authorized':False})
 work15,_=review(store,c,15,verdict='APPROVE')
 reviewrow=store.db.execute('SELECT * FROM manual_calls WHERE id=?',(post.call(p,'review'),)).fetchone()
 assert reviewrow['attempt']==15 and json.loads(reviewrow['receipt'])['batch_accounting']['run_limit']==37
 value.update(phase='MODEL_RUNNING',pending={'id':post.call(p,'review'),'stage':'run_spec_review','round':15,'workspace':str(work15)})
 d.criticism=lambda *args:None
 result=post.finish_review(d,value,p,'3'*64)
 assessment=result[post.profile(p)['result']]
 assert assessment['verdict']=='APPROVE' and assessment['execution_authorized'] is False
 assert assessment['global_findings_closed'] is False and assessment['corrected_fixture_executed'] is False
 assert assessment==json.loads((d.state/'cpu-diagnostic-fixture-correction/assessment.json').read_bytes())
 result.update(phase='result_interpretation_author');d.save(result)
 charged=Accounts(store).read()
 with pytest.raises((ValueError,KeyError,FileNotFoundError)):store.reserve_call(x.RUN,'result_interpretation_author',c['source'],'astra/manual-test',policy(),{})
 assert Accounts(store).read()==charged
 assert Accounts(store).read()[1]['count']==35
 assert before==[dict(r) for r in store.db.execute('SELECT * FROM manual_calls ORDER BY rowid')][:33]
 assert oldglobal==[dict(r) for r in batch.db.execute("SELECT * FROM autonomy_calls WHERE kind='scientific' ORDER BY rowid")][:71]
 assert dict(batch.db.execute('SELECT * FROM autonomy_assets WHERE id=?',(fixture.ASSET,)).fetchone())==p['native_failure']['asset_row']
 # Both reserved whole-plan calls remain beyond this pair; no execution permission is produced.
 assert post.proof(p,'3'*64)['execution_authorized'] is False


def test_independent_refusals_preserve_charges(fixture_ready,monkeypatch):
 f,p,work=fixture_ready;store,batch,c,d,*_=f
 local=sqlite3.connect(':memory:');global_db=sqlite3.connect(':memory:');store.db.backup(local);batch.db.backup(global_db)
 saved=(fixture.STATE/'provider/stdout.bin').read_bytes()
 try:
  for fault in ['old-local','old-global','asset-status','asset-reservation','failure-bytes','qualification','grant','early-review','early-full','daily']:
   try:
    if fault=='old-local':store.db.execute("UPDATE manual_calls SET receipt='changed' WHERE id=?",(next(iter(p['local_calls'])),))
    elif fault=='old-global':batch.db.execute("UPDATE autonomy_calls SET receipt='changed' WHERE id=?",(next(iter(p['batch_calls'])),))
    elif fault=='asset-status':batch.db.execute("UPDATE autonomy_assets SET status='READY' WHERE id=?",(fixture.ASSET,))
    elif fault=='asset-reservation':batch.db.execute('UPDATE autonomy_assets SET reserved_micro_usd=0 WHERE id=?',(fixture.ASSET,))
    elif fault=='failure-bytes':(fixture.STATE/'provider/stdout.bin').write_bytes(b'PASS')
    elif fault=='qualification':monkeypatch.setattr(fixture,'_verifier',lambda:{**qualification(p),'status':'PASS'})
    elif fault=='grant':store.db.execute('DELETE FROM events WHERE id=?',(post.profile(p)['event'],))
    elif fault=='daily':
     from datetime import datetime,timezone
     from test_scoped_revisions_limits import seed
     day=datetime.now(timezone.utc).date().isoformat();count=batch.db.execute('SELECT count(*) FROM autonomy_calls WHERE day=?',(day,)).fetchone()[0];seed(batch,50-count,kind='implementation_review',day=day)
    before=Accounts(store).read();rows=[dict(r) for r in store.db.execute('SELECT * FROM manual_calls')]
    stage='run_spec_review' if fault=='early-review' else 'result_interpretation_author' if fault=='early-full' else 'run_spec_author'
    with pytest.raises(ValueError):store.reserve_call(x.RUN,stage,c['source'],'astra/manual-test',policy(),{})
    assert before==Accounts(store).read() and rows==[dict(r) for r in store.db.execute('SELECT * FROM manual_calls')]
   finally:
    assert not store.db.in_transaction and not batch.db.in_transaction
    local.backup(store.db);global_db.backup(batch.db);(fixture.STATE/'provider/stdout.bin').write_bytes(saved)
    monkeypatch.setattr(fixture,'_verifier',lambda:qualification(p))
 finally:local.close();global_db.close()


def test_production_ast_and_interface_cannot_change(monkeypatch,tmp_path):
 # Synthetic module tests only; root never authors a correction to actual scientific code.
 raw=b'def main(): return 7\ndef _native_diagnostic_fixture(x): return x\n'
 path=tmp_path/'reference.py';path.write_bytes(raw)
 monkeypatch.setattr(fixture,'ROOT',tmp_path);monkeypatch.setattr(fixture,'REFERENCE','reference.py');monkeypatch.setattr(fixture,'MODULE',x.sha(raw));monkeypatch.setattr(fixture,'scope',lambda p:None)
 corrected=raw.replace(b'return x',b'return dict(x)')
 assert fixture.correction(corrected,{})['corrected_fixture_executed'] is False
 for invalid in [raw,corrected.replace(b'return 7',b'return 8'),corrected.replace(b'fixture(x)',b'fixture(x,y)'),corrected+b'def extra(): pass\n',corrected.replace(b'fixture(x):',b'fixture(x) -> int:')]:
  with pytest.raises(ValueError):fixture.correction(invalid,{})
