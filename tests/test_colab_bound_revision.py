import json,sqlite3,copy
from pathlib import Path
from types import SimpleNamespace
import pytest
from orchestrator import colab_bound_revision as f
from orchestrator import colab_static_feedback as old

def lane(tmp_path,monkeypatch):
 d=tmp_path/'lane';d.mkdir()
 local=sqlite3.connect(':memory:');local.row_factory=sqlite3.Row
 local.executescript('CREATE TABLE manual_calls(id TEXT PRIMARY KEY,status TEXT);CREATE TABLE manual_account(id INTEGER PRIMARY KEY,payload TEXT);CREATE TABLE manual_state(id INTEGER PRIMARY KEY,payload TEXT);CREATE TABLE events(id TEXT PRIMARY KEY,job TEXT,payload TEXT);')
 globaldb=sqlite3.connect(':memory:');globaldb.row_factory=sqlite3.Row
 globaldb.execute('CREATE TABLE autonomy_calls(id TEXT PRIMARY KEY,status TEXT)')
 calls=[{'id':str(i),'status':'COMPLETE'}for i in range(13)]+[{'id':f.CALL,'status':'COMPLETE'}]
 local.executemany('INSERT INTO manual_calls VALUES(:id,:status)',calls)
 globaldb.execute('INSERT INTO autonomy_calls VALUES(?,?)',(f.CALL,'COMPLETE'));globaldb.commit()
 review={'verdict':'REVISE','findings':[{'id':'F-INERT-FRAGMENT-FALSE-MEMBERSHIP-LITERAL','category':'privacy/secret'}]}
 reviewpath=tmp_path/'lane-scientific-workspaces/run_spec_review-6/review.json';reviewpath.parent.mkdir(parents=True);reviewpath.write_bytes(f.canonical(review))
 monkeypatch.setattr(f,'REVIEW_CANONICAL_SHA',f.sha(f.canonical(review)))
 state={'phase':'BLOCKED','reason':f.REASON,'blocked_stage':'run_spec_review','review':str(reviewpath),'rounds':{'run_spec_author':7,'run_spec_review':6},'interventions':[],'blocker_categories':['privacy/secret'],'artifacts':[]}
 local.execute('INSERT INTO manual_state VALUES(1,?)',(json.dumps(state),))
 local.execute('INSERT INTO manual_account VALUES(1,?)',('all historical charges preserved',));local.commit()
 current=lambda:json.loads(local.execute('SELECT payload FROM manual_state').fetchone()[0])
 obj=SimpleNamespace(state=d,config={'run_id':f.RUN,'batch_ledger':str(tmp_path/'global')},store=SimpleNamespace(db=local,batch=SimpleNamespace(db=globaldb)),current=current)
 proof={'files':{str(reviewpath.relative_to(tmp_path)):f.sha(reviewpath.read_bytes())},'calls':calls,'records':{'local':calls[-1],'global':calls[-1]},'state_row':dict(local.execute('SELECT * FROM manual_state').fetchone()),'account_row':dict(local.execute('SELECT * FROM manual_account').fetchone())}
 return obj,proof,reviewpath

def test_one_use_genuine_revision_preserves_every_attempt_account_and_finding(tmp_path,monkeypatch):
 d,b,path=lane(tmp_path,monkeypatch);before=path.read_bytes()
 out=f.resume(d,b,'a'*64);after=d.current()
 assert out['new_calls']==out['new_allowance']==0
 assert after['phase']=='run_spec_author'and after['reason']=='REVISION_REQUIRED'
 assert after['review']==str(path)and path.read_bytes()==before
 assert after['rounds']=={'run_spec_author':7,'run_spec_review':6}
 assert after['interventions'][-1]['reviewer_revise']is True
 assert after['interventions'][-1]['scientific_acceptance']is False
 assert [dict(x)for x in d.store.db.execute('SELECT * FROM manual_calls')]==b['calls']
 assert dict(d.store.db.execute('SELECT * FROM manual_account').fetchone())==b['account_row']
 with pytest.raises(ValueError):f.resume(d,b,'a'*64)

@pytest.mark.parametrize('damage',['review','local','global','running','state','account','new_call','halt'])
def test_refuse_changed_uncertain_or_halted(tmp_path,monkeypatch,damage):
 d,b,path=lane(tmp_path,monkeypatch);db=d.store.db;g=d.store.batch.db
 if damage=='review':path.write_text('{"verdict":"REJECT"}')
 elif damage=='local':db.execute("UPDATE manual_calls SET status='UNCERTAIN'WHERE id=?",(f.CALL,))
 elif damage=='global':g.execute("UPDATE autonomy_calls SET status='UNCERTAIN'")
 elif damage=='running':g.execute("INSERT INTO autonomy_calls VALUES('another','RUNNING')")
 elif damage=='state':db.execute("UPDATE manual_state SET payload='{}'")
 elif damage=='account':db.execute("UPDATE manual_account SET payload='changed'")
 elif damage=='new_call':db.execute("INSERT INTO manual_calls VALUES('new','COMPLETE')")
 elif damage=='halt':(d.state/'HALT').touch()
 db.commit();g.commit();before=db.execute('SELECT payload FROM manual_state').fetchone()[0]
 with pytest.raises(ValueError):f.resume(d,b,'a'*64)
 assert db.execute('SELECT payload FROM manual_state').fetchone()[0]==before
 assert not db.execute('SELECT * FROM events').fetchall()

@pytest.mark.parametrize('change',[{'reason':'REVIEW_REJECTED'},{'rounds':{'run_spec_author':6,'run_spec_review':6}},{'pending':{'id':'uncertain'}},{'blocked_stage':'result_interpretation_review'}])
def test_no_generic_exception(tmp_path,monkeypatch,change):
 d,b,_=lane(tmp_path,monkeypatch);state=d.current();state.update(change)
 with pytest.raises(ValueError):f.restored(state,'a'*64)

def test_feedback_and_privacy_scanner_remain_identical():
 assert f.CHECKER==old.CHECKER
 assert {k:v for k,v in f.runtime_libraries().items()if k!='author_output_schema'}=={k:v for k,v in old.runtime_libraries().items()if k!='author_output_schema'}
 from orchestrator import notebook_revision as nr
 root=Path(f.__file__).parents[1]
 ref=(root/f.REFERENCE_DOCUMENT).read_bytes()
 assert f.sha(ref)==f.REFERENCE_SHA
 value=json.loads(ref)
 assert set(value['fit_lock_ids'])==set(map(str,range(5)))
 assert len(set(value['fit_lock_ids'].values()))==5
 nr.scan(ref,frozenset())
 for raw in f.runtime_libraries().values():nr.scan(raw,frozenset())

def test_bound_feedback_requires_exact_reference_before_admission(tmp_path,monkeypatch):
 import inspect
 text=inspect.getsource(f.feedback_files)
 assert "sha(reference)==REFERENCE_SHA" in text
 assert "bodies['accepted-input-reference.json']=reference" in text
 assert 'for raw in bodies.values():nr.scan(raw,cases)'in text

def test_native_unit_preserves_confinement():
 from tools import colab_bound_revision_runtime as rt
 raw=('User=partho\nGroup=partho\nExecStart=/usr/bin/python3 -s -B '+str(rt.BASE)+'/tools/colab_simple_runtime.py run\nRestart=no\nReadWritePaths=/fixed/work\n')
 parent=SimpleNamespace(metadata=lambda:({},{}),unit_bytes=lambda scope:raw.encode())
 changed=rt.unit_bytes(parent).decode()
 assert changed.replace(str(rt.ROOT/rt.ENTRY),str(rt.BASE/'tools/colab_simple_runtime.py'))==raw


def test_reviewed_category_exception_runs_original_delivery_verifier_and_restores(tmp_path,monkeypatch):
 from orchestrator import author_revision_accounting as accounting,analysis_revisions,experiment_approval,preparation_followup
 d,b,path=lane(tmp_path,monkeypatch);monkeypatch.setattr(f,'frozen',lambda root:b)
 folder=d.state/f.EVENT;folder.mkdir()
 (folder/'COMPLETE.json').write_text(json.dumps({'review_sha256':'a'*64,'proof_sha256':f.DOCUMENT_SHA,'operator_disposition_sha256':f.DISPOSITION_SHA,'operator_decision_sha256':f.OPERATOR_SHA}))
 raw=path.read_bytes();seen=[]
 receipt_row={'receipt':'native authenticated review receipt'}
 def delivery(driver,pending,stage):
  seen.append((driver,pending,stage))
  return None,None,raw,{},receipt_row,b'accepted independent submission'
 monkeypatch.setattr(experiment_approval,'verified_review_delivery',delivery)
 monkeypatch.setattr(preparation_followup,'offset',lambda *a:4)
 before=analysis_revisions.review_transition
 wrapped=f.accounting_adapter(accounting.review_binding,tmp_path,'a'*64)
 result=wrapped(d,'run_spec_author',6,8)
 assert len(seen)==1 and result['review_call_id']==f.CALL
 assert result['review_sha256']==f.sha(raw)
 assert result['submission_sha256']==f.sha(b'accepted independent submission')
 assert result['review_receipt_sha256']==f.sha(receipt_row['receipt'].encode())
 assert analysis_revisions.review_transition is before

def test_missing_reviewed_grant_never_reaches_original_accounting(tmp_path,monkeypatch):
 d,b,_=lane(tmp_path,monkeypatch);monkeypatch.setattr(f,'frozen',lambda root:b)
 wrapped=f.accounting_adapter(lambda *a:pytest.fail('original called without grant'),tmp_path,'a'*64)
 with pytest.raises((ValueError,FileNotFoundError)):wrapped(d,'run_spec_author',6,8)

@pytest.mark.parametrize('args',[
 ('another-run','run_spec_author',6,8),(f.RUN,'result_interpretation_author',6,8),
 (f.RUN,'run_spec_author',5,8),(f.RUN,'run_spec_author',6,9)])
def test_other_runs_stages_reviews_or_attempts_get_no_exception(tmp_path,monkeypatch,args):
 d,b,_=lane(tmp_path,monkeypatch);monkeypatch.setattr(f,'frozen',lambda root:b)
 run,stage,number,author=args;d.config['run_id']=run
 calls=[]
 def original(*a):calls.append(a);raise ValueError('ORIGINAL_REFUSAL')
 wrapped=f.accounting_adapter(original,tmp_path,'a'*64)
 with pytest.raises(ValueError,match='ORIGINAL_REFUSAL'):wrapped(d,stage,number,author)
 assert len(calls)==1

def test_original_authentication_failure_is_not_relaxed(tmp_path,monkeypatch):
 from orchestrator import analysis_revisions
 d,b,_=lane(tmp_path,monkeypatch);monkeypatch.setattr(f,'frozen',lambda root:b)
 folder=d.state/f.EVENT;folder.mkdir()
 (folder/'COMPLETE.json').write_text(json.dumps({'review_sha256':'a'*64,'proof_sha256':f.DOCUMENT_SHA,'operator_disposition_sha256':f.DISPOSITION_SHA,'operator_decision_sha256':f.OPERATOR_SHA}))
 original_transition=analysis_revisions.review_transition
 def original(*a):raise ValueError('REVIEW_SUBMISSION_MISMATCH')
 wrapped=f.accounting_adapter(original,tmp_path,'a'*64)
 with pytest.raises(ValueError,match='REVIEW_SUBMISSION_MISMATCH'):wrapped(d,'run_spec_author',6,8)
 assert analysis_revisions.review_transition is original_transition

def test_admission_preflight_rolls_back_success_and_failure(tmp_path,monkeypatch):
 from orchestrator import author_revision_accounting as accounting
 d,b,_=lane(tmp_path,monkeypatch);monkeypatch.setattr(f,'frozen',lambda root:b)
 old=d.current()
 def inspect(store,run,stage):
  assert f._PROBE_DB is store.db and store.db.in_transaction
  assert d.current()['phase']=='run_spec_author'
  return {'binding':{'review_call_id':f.CALL,'author_attempt':8,
                    'review_sha256':f.sha((d.state.parent/'lane-scientific-workspaces/run_spec_review-6/review.json').read_bytes())}}
 monkeypatch.setattr(accounting,'inspect',inspect)
 result=f.probe_admission(d,tmp_path,'a'*64)
 assert result['reservations']==result['model_calls']==result['persistent_state_mutations']==0
 assert d.current()==old and f._PROBE_DB is None and not d.store.db.in_transaction
 def fail(*a):raise ValueError('ACTUAL_ADMISSION_REFUSAL')
 monkeypatch.setattr(accounting,'inspect',fail)
 with pytest.raises(ValueError,match='ACTUAL_ADMISSION_REFUSAL'):f.probe_admission(d,tmp_path,'a'*64)
 assert d.current()==old and f._PROBE_DB is None and not d.store.db.in_transaction


def test_operator_disposition_is_separate_truthful_and_hash_bound(tmp_path):
 import shutil
 root=Path(f.__file__).parents[1]
 value=f.operator_disposition(root)
 assert value['human_approval']is False
 assert value['patient_access']is value['scientific_execution']is False
 assert value['require_fresh_scientific_approve_of_exact_bytes']is True
 for name in [f.DISPOSITION_DOCUMENT,f.DELEGATION_DOCUMENT,f.OPERATOR_DOCUMENT]:
  dest=tmp_path/name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(root/name,dest)
 (tmp_path/f.DISPOSITION_DOCUMENT).write_text('{"human_approval":true}')
 with pytest.raises(ValueError,match='OPERATOR_DISPOSITION'):f.operator_disposition(tmp_path)

def test_wrong_disposition_binding_keeps_accounting_held(tmp_path,monkeypatch):
 d,b,_=lane(tmp_path,monkeypatch);monkeypatch.setattr(f,'frozen',lambda root:b)
 folder=d.state/f.EVENT;folder.mkdir()
 (folder/'COMPLETE.json').write_text(json.dumps({'review_sha256':'a'*64,'proof_sha256':f.DOCUMENT_SHA,
                                               'operator_disposition_sha256':'0'*64,'operator_decision_sha256':'0'*64}))
 wrapped=f.accounting_adapter(lambda *a:pytest.fail('no admission'),tmp_path,'a'*64)
 with pytest.raises(ValueError,match='ADMISSION_APPROVAL'):wrapped(d,'run_spec_author',6,8)


def test_actual_preserved_author_admission_state_recovers_without_changing_history():
    root=Path(f.__file__).parents[1]
    proof=f.frozen(root)
    original=json.loads(proof['state_row']['payload'])
    assert original['blocked_stage']=='run_spec_review'
    result=f.restored(original,'a'*64)
    assert result['phase']=='run_spec_author' and result['reason']=='REVISION_REQUIRED'
    assert result['review']==original['review'] and result['rounds']==original['rounds']
    assert result['artifacts']==original['artifacts']
    assert json.loads(proof['state_row']['payload'])==original

@pytest.mark.parametrize('stage',[None,'run_spec_author','result_interpretation_author'])
def test_preserved_state_other_hold_stages_stay_refused(stage):
    root=Path(f.__file__).parents[1]
    state=json.loads(f.frozen(root)['state_row']['payload'])
    state['blocked_stage']=stage
    with pytest.raises(ValueError,match='EXACT_REVIEW_BLOCK'):f.restored(state,'a'*64)

def test_installed_overlay_contains_every_frozen_authority_dependency(tmp_path):
    from tools import colab_bound_revision_runtime as rt
    root=Path(f.__file__).parents[1]
    for name in rt.ADDED:
        target=tmp_path/name;target.parent.mkdir(parents=True,exist_ok=True)
        target.write_bytes((root/name).read_bytes())
    proof=f.frozen(tmp_path)
    state=json.loads(proof['state_row']['payload'])
    assert f.restored(state,'a'*64)['phase']=='run_spec_author'
    assert f.operator_disposition(tmp_path)['human_approval'] is False


def test_explicit_operator_decision_required_and_unchanged(tmp_path):
    import shutil
    root=Path(f.__file__).parents[1]
    for name in (f.DISPOSITION_DOCUMENT,f.DELEGATION_DOCUMENT,f.OPERATOR_DOCUMENT):
        dest=tmp_path/name;dest.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(root/name,dest)
    assert f.operator_disposition(tmp_path)['human_approval'] is False
    (tmp_path/f.OPERATOR_DOCUMENT).write_text('changed authorization')
    with pytest.raises(ValueError,match='EXPLICIT_OPERATOR_DECISION'):
        f.operator_disposition(tmp_path)

def test_recovery_records_new_operator_authority_without_rewriting_prior(tmp_path,monkeypatch):
    d,b,path=lane(tmp_path,monkeypatch)
    f.resume(d,b,'a'*64)
    receipt=json.loads((d.state/f.EVENT/'COMPLETE.json').read_bytes())
    assert receipt['operator_decision_sha256']==f.OPERATOR_SHA
    assert d.current()['interventions'][-1]['operator_decision_sha256']==f.OPERATOR_SHA
