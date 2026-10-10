"""One new reviewer after genuine synthetic protocol; no scientific execution."""
import copy,json,sqlite3
from pathlib import Path
from types import SimpleNamespace as NS
import pytest
from orchestrator import item4_smoke_response as post,item4_scoped_calls as scoped
from orchestrator import item4_review4_continuation as x,author_revision_accounting as accounting
from orchestrator import autonomy_limits as limits,manual_recovery,review_submission as rs
from orchestrator.manual_executor import ManualExecutor,Accounts
from orchestrator.autonomy_accounting import BatchAccounts
from test_item4_fixture_correction import (fixture_ready,plaintext_ready,native_ready,scoped_ready,recovery_ready,
 diagnostic_ready,baseline,diagnostic_plan,response_ready,accepted_author,smoke_ready,extended,fifth,accepted,
 mechanical,fourth,third,setup,second,continuation,base_setup)
from test_author_revision_accounting import review
from test_manual_lane import policy

@pytest.fixture
def corrected_ready(request,monkeypatch):
 connect=scoped.connect
 originals=[(o,k,getattr(o,k)) for o,k in [(limits,k) for k in
 ('local_limit','global_limit','allowance','cap_authority','scientific_batch_allowance')]+
 [(ManualExecutor,'reserve_call'),(BatchAccounts,'reserve_scientific')]]
 f,fixture,_=request.getfixturevalue('fixture_ready');store,batch,c,driver,*_=f
 ident,n,receipt=store.reserve_call(x.RUN,'run_spec_author',c['source'],'astra/manual-test',policy(),{})
 assert n==20
 work=driver.state.parent/(driver.state.name+'-scientific-workspaces')/'run_spec_author-20';work.mkdir(parents=True)
 bodies={'SPEC.proposed.md':b'synthetic20','execution.plan.json':b'synthetic plan','notebook.patch.json':b'synthetic patch'}
 for name,raw in bodies.items():(work/name).write_bytes(raw)
 receipt.update(workspace=str(work),output_sha256={k:x.sha(v) for k,v in bodies.items()})
 store.finish_call(ident,receipt,'COMPLETE');accounting.accepted(driver,{'id':ident,'stage':'run_spec_author','round':20})
 value=x.state(store);value.update(phase='run_spec_review',rounds={'run_spec_author':20,'run_spec_review':14});driver.save(value)
 # This fixture tests accounting/protocol, not scientific/native execution.
 monkeypatch.setattr(post,'executable_candidate',lambda *args:{'execution_authorized':False})
 work15,_=review(store,c,15,category='budget')
 value.update(phase='MODEL_RUNNING',pending={'id':post.call(fixture,'review'),'stage':'run_spec_review','round':15,'workspace':str(work15)})
 post.finish_review(driver,value,fixture,'3'*64)
 raw=store.db.execute('SELECT payload FROM manual_state WHERE id=1').fetchone()[0]
 assessment=json.loads(raw)['cpu_diagnostic_fixture_correction'];monkeypatch.setattr(post,'REVIEW15_REPORT',assessment['report_sha256'])
 pins=lambda db,sql:{r['id']:x.sha(x.canonical(dict(r))) for r in db.execute(sql)}
 p=copy.deepcopy(fixture);p.update(schema=post.CORRECTED_REVIEW_SCHEMA,author_attempt=20,review_attempt=16,
 run_limit=38,batch_limit=76,original_state=raw,state_sha256=x.sha(raw.encode()),assessment=assessment,
 assessment_sha256=x.sha(x.canonical(assessment)),author_outputs=receipt['output_sha256'],
 accepted_author_event=json.loads(store.db.execute('SELECT payload FROM events WHERE id=?',('author-accepted:'+ident,)).fetchone()[0]),
 local_calls=pins(store.db,'SELECT * FROM manual_calls ORDER BY rowid'),
 global_calls=pins(batch.db,"SELECT * FROM autonomy_calls WHERE kind='scientific' AND change_id='"+x.RUN+"' ORDER BY rowid"),
 batch_calls=pins(batch.db,"SELECT * FROM autonomy_calls WHERE kind='scientific' ORDER BY rowid"))
 for o,k,fn in originals:monkeypatch.setattr(o,k,fn)
 monkeypatch.setattr(scoped,'_validate',None)
 _,plaintext,_=request.getfixturevalue('plaintext_ready');_,native,_=request.getfixturevalue('native_ready')
 _,scoped_p,_=request.getfixturevalue('scoped_ready');_,recovery,_=request.getfixturevalue('recovery_ready')
 _,diagnostic=request.getfixturevalue('diagnostic_ready');_,smoke,post_p,_=request.getfixturevalue('response_ready');_,saved=request.getfixturevalue('extended')
 connect(request.getfixturevalue('fourth')[4],'b'*64,mechanical=request.getfixturevalue('mechanical')[4],mechanical_approval='a'*64,
 response=f[4],response_approval='9'*64,batch_extension=saved['extension'],batch_approval='e'*64,
 smoke=smoke,smoke_approval='d'*64,post_smoke=post_p,post_smoke_approval='c'*64,
 diagnostic=diagnostic,diagnostic_approval='8'*64,diagnostic_recovery=recovery,diagnostic_recovery_approval='7'*64,
 diagnostic_scoped=scoped_p,diagnostic_scoped_approval='6'*64,diagnostic_native=native,diagnostic_native_approval='5'*64,
 diagnostic_plaintext=plaintext,diagnostic_plaintext_approval='4'*64,diagnostic_fixture=fixture,diagnostic_fixture_approval='3'*64,
 corrected_native=p,corrected_native_approval='2'*64)
 assert limits.local_limit(store,x.RUN,policy())==37
 assert post.activate(driver,p,'2'*64,driver.state/'corrected-native-review')['status']=='READY_DIAGNOSTIC_REVIEW16'
 return f,p,work15


def test_one_review_is_counted_and_originals_final_pair_preserved(corrected_ready):
 f,p,work15=corrected_ready;store,batch,c,d,*_=f
 oldlocal=[dict(r) for r in store.db.execute('SELECT * FROM manual_calls ORDER BY rowid')]
 oldglobal=[dict(r) for r in batch.db.execute("SELECT * FROM autonomy_calls WHERE kind='scientific' ORDER BY rowid")]
 assert len(oldlocal)==35 and len(oldglobal)==73
 assert manual_recovery.role_limit(store,x.RUN,'run_spec_review')==16
 value=x.state(store);work16,_=review(store,c,16,verdict='APPROVE')
 row=store.db.execute('SELECT * FROM manual_calls WHERE id=?',(post.call(p,'review'),)).fetchone()
 charged=json.loads(row['receipt']);assert charged['batch_accounting']['run_limit']==38 and charged['batch_accounting']['batch_limit']==76
 assert charged['accounting']['limit_amendment']['review_sha256']=='2'*64
 value.update(phase='MODEL_RUNNING',pending={'id':post.call(p,'review'),'stage':'run_spec_review','round':16,'workspace':str(work16)})
 result=post.finish_review(d,value,p,'2'*64);assessment=result['corrected_native_scientific_review']
 assert result['phase']=='BLOCKED' and assessment['verdict']=='APPROVE'
 assert all(assessment[k] is False for k in ['execution_authorized','full_training_admitted','coverage_released','global_findings_closed'])
 assert assessment['carried_review_sha256']==p['assessment']['report_sha256']
 assert oldlocal==[dict(r) for r in store.db.execute('SELECT * FROM manual_calls ORDER BY rowid')][:35]
 assert oldglobal==[dict(r) for r in batch.db.execute("SELECT * FROM autonomy_calls WHERE kind='scientific' ORDER BY rowid")][:73]
 assert Accounts(store).read()[1]['count']==36
 for stage in ['run_spec_review','run_spec_author','result_interpretation_author']:
  candidate=copy.deepcopy(result);candidate['phase']=stage;d.save(candidate)
  before=Accounts(store).read()
  with pytest.raises((ValueError,KeyError,FileNotFoundError)):store.reserve_call(x.RUN,stage,c['source'],'astra/manual-test',policy(),{})
  assert Accounts(store).read()==before
 post.originals(store,p,'2'*64)


def test_independent_review16_refusals_preserve_accounting(corrected_ready):
 f,p,work15=corrected_ready;store,batch,c,d,*_=f
 local=sqlite3.connect(':memory:');glob=sqlite3.connect(':memory:');store.db.backup(local);batch.db.backup(glob)
 try:
  for fault in ['old-local','old-global','grant','pending','author','full','hold','daily','unknown']:
   try:
    stage='run_spec_review'
    if fault=='old-local':store.db.execute("UPDATE manual_calls SET receipt='changed' WHERE id=?",(next(iter(p['local_calls'])),))
    elif fault=='old-global':batch.db.execute("UPDATE autonomy_calls SET receipt='changed' WHERE id=?",(next(iter(p['batch_calls'])),))
    elif fault=='grant':store.db.execute('DELETE FROM events WHERE id=?',(post.profile(p)['event'],))
    elif fault=='unknown':batch.db.execute("INSERT INTO autonomy_calls VALUES('unknown','review','x',1,'2000-01-01','UNCERTAIN','{}','{}')")
    elif fault=='daily':
     from datetime import datetime,timezone
     from test_scoped_revisions_limits import seed
     day=datetime.now(timezone.utc).date().isoformat();count=batch.db.execute('SELECT count(*) FROM autonomy_calls WHERE day=?',(day,)).fetchone()[0];seed(batch,50-count,kind='implementation_review',day=day)
    else:
     value=x.state(store)
     if fault=='pending':value['pending']={'id':'uncertain'}
     elif fault=='hold':value['reviewed_execution']={'forged':True}
     else:stage='run_spec_author' if fault=='author' else 'result_interpretation_author';value['phase']=stage
     d.save(value)
    before=Accounts(store).read();rows=[dict(r) for r in store.db.execute('SELECT * FROM manual_calls')]
    with pytest.raises((ValueError,KeyError)):store.reserve_call(x.RUN,stage,c['source'],'astra/manual-test',policy(),{})
    assert Accounts(store).read()==before and rows==[dict(r) for r in store.db.execute('SELECT * FROM manual_calls')]
   finally:
    assert not store.db.in_transaction and not batch.db.in_transaction
    local.backup(store.db);glob.backup(batch.db)
 finally:local.close();glob.close()


def test_actual_frozen_scope_and_exact_module_guard():
 root=Path(__file__).parents[1];p=json.loads((root/post.CORRECTED_REVIEW_DOCUMENT).read_bytes())
 assert post.scope(p,'a'*64)['rounds']=={'run_spec_author':20,'run_spec_review':15}
 for field,replacement in [('run_limit',39),('batch_limit',77),('author_attempt',21),('review_attempt',17),('execution_authorized',True),('automatic_retry',True),('diagnostic_micro_usd',26000000),('stage1_micro_usd',151000000)]:
  changed=copy.deepcopy(p);changed[field]=replacement
  with pytest.raises(ValueError):post.scope(changed,'a'*64)
 with pytest.raises(ValueError):post.validate_diagnostic_delta(p['baseline_plan'].encode(),b'not accepted science',p)


def test_native_evidence_gate_refuses_missing_or_changed_receipt(monkeypatch):
 from tools import item4_diagnostic_review_runtime as r
 p={'schema':post.CORRECTED_REVIEW_SCHEMA};driver=NS(store=NS(batch=object()),state='synthetic',config={})
 monkeypatch.setattr(post,'ready',lambda *args:None)
 monkeypatch.setattr(r.native,'authority',lambda:{'report_sha256':'a'*64})
 monkeypatch.setattr(r,'marker',lambda accounts:{'synthetic_native_receipt':True})
 restore=r.attach(driver,post,p,'a'*64)
 try:
  for value in [{},{'diagnostic_native_evidence':{'forged':True}}]:
   with pytest.raises(ValueError,match='ACTUAL_NATIVE_EVIDENCE_REQUIRED'):post.ready(driver,value,p,'a'*64)
  post.ready(driver,{'diagnostic_native_evidence':{'synthetic_native_receipt':True}},p,'a'*64)
 finally:restore()
