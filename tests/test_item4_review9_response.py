"""Exact response routing and proof binding; synthetic receipts, no model/provider."""
import copy,json,sqlite3,sys
from pathlib import Path
from types import SimpleNamespace as NS
import pytest
from orchestrator import item4_review4_continuation as x,author_revision_accounting as a
from orchestrator.manual_driver import Driver
from orchestrator.manual_executor import Accounts
from tools import item4_scientific_revision_component as c,item4_review8_proof as proof
from test_item4_review9_continuation import fifth,accepted,mechanical,fourth,third,setup,second,continuation,base_setup
from test_manual_lane import policy


def probe(v):
 store,batch,config,d,f,*_=v
 class Runner(Driver):
  def model_round_number(self,value):return c.response_model_attempt(self,value,f,'9'*64)
  def guard(self):pass
  def prepare_input(self,value,stage,work):return 'Synthetic bounded response',{'workspace_files':[]}
  def save(self,value):store.db.execute('UPDATE manual_state SET payload=? WHERE id=1',(json.dumps(value),))
  def output_names(self,stage):return ['SPEC.proposed.md'] if stage=='run_spec_author' else ['review.json']
  def accept_completed(self,value):return value
 p=object.__new__(Runner);p.store=store;p.state=d.state
 p.config={**config,'branch':'astra/manual-test','policy':policy(),'review_contract':'bound-review/v1',
  'workspace_root':str(d.state.parent/(d.state.name+'-scientific-workspaces'))}
 assert 'execution_recovery' not in p.config
 calls=[]
 def invoke(work,stage,clients,pin):
  calls.append((work.name,stage))
  if stage=='run_spec_review':
   argv=c.response_reviewer_command(lambda *args:['claude','--max-turns','30'],work,stage,p,f,'9'*64)
   assert argv==['claude','--max-turns','60']
  (work/p.output_names(stage)[0]).write_text('synthetic response')
  return {'synthetic':True}
 p.runner=invoke
 return p,calls


def test_real_model_step_author14_then_review10_preserves_counters_and_charges(fifth):
 store,batch,config,d,f,local,glob=fifth;p,calls=probe(fifth)
 assert c.response_stage(p,f,'9'*64)==14
 result=p._model_step(x.state(store));assert result['pending']['round']==14
 assert result['rounds']=={'run_spec_author':13,'run_spec_review':9}
 a.accepted(d,result['pending'])
 value=x.state(store);value.pop('pending');value.update(phase='run_spec_review',reason=None,rounds={'run_spec_author':14,'run_spec_review':9})
 p.save(value);assert c.response_stage(p,f,'9'*64)==10
 result=p._model_step(value)
 assert result['pending']['round']==10 and result['rounds']['run_spec_review']==9
 assert calls==[('run_spec_author-14','run_spec_author'),('run_spec_review-10','run_spec_review')]
 assert Accounts(store).read()[1]['count']==24
 assert [dict(r) for r in store.db.execute('SELECT * FROM manual_calls ORDER BY rowid LIMIT 22')]==local
 assert [dict(r) for r in batch.db.execute('SELECT * FROM autonomy_calls ORDER BY rowid LIMIT 22')]==glob
 with pytest.raises(ValueError):p._model_step(result)


@pytest.mark.parametrize('fault',['stale-value','phase','pending','round','grant'])
def test_actual_model_path_refuses_before_workspace_or_charge(fifth,fault):
 store,batch,config,d,f,*_=fifth;p,calls=probe(fifth);v=x.state(store)
 if fault=='stale-value':v['reason']='changed'
 elif fault=='phase':v['phase']='result_interpretation_author';p.save(v)
 elif fault=='pending':v['pending']={'id':'unexpected'};p.save(v)
 elif fault=='round':v['rounds']['run_spec_review']=8;p.save(v)
 else:store.db.execute('DELETE FROM events WHERE id=?',(x.reason(f),))
 with pytest.raises(ValueError):p._model_step(v)
 assert not calls and Accounts(store).read()[1]['count']==22
 assert not (Path(p.config['workspace_root'])/'run_spec_author-14').exists()


@pytest.fixture
def new_module(tmp_path,monkeypatch):
 from orchestrator import notebook_execution as ne
 folder=tmp_path/'notebook-revisions/author-14';package=folder/'synthetic/package';package.mkdir(parents=True)
 notebook=b'{"synthetic":"notebook"}';module=b'# exact tested module\n';support=b'# exact support\n'
 (folder/'revised.ipynb').write_bytes(notebook);(package/'revised.ipynb').write_bytes(notebook);(package/'execution.py').write_bytes(module);(package/'support.py').write_bytes(support)
 files={'execution.py':c.sha(module),'support.py':c.sha(support),'revised.ipynb':c.sha(notebook)};environment={'synthetic':'unchanged'}
 receipt={'status':'PASS','exit_code':0,'binding':{'files':files,'environment':environment},
  'preserved_files':{'package/execution.py':c.sha(module),'package/support.py':c.sha(support)}}
 (folder/'synthetic/receipt.json').write_bytes(c.canonical(receipt))
 result={'folder':str(folder),'synthetic_status':'PASS','notebook_sha256':c.sha(notebook),'tests_sha256':c.sha(c.canonical(receipt))}
 state={'notebook_revision_result':result,'artifacts':[{'id':'notebook_source','version':14,'sha256':result['notebook_sha256']},
  {'id':'synthetic_tests','version':14,'sha256':result['tests_sha256']}]}
 d=NS(state=tmp_path,current=lambda:state)
 frozen={'historical_science':{'execution_sha256':c.sha(module),'native_files':{k:v for k,v in files.items() if k!='revised.ipynb'},'controller_environment':environment}}
 monkeypatch.setattr(ne,'extract',lambda raw,preprocessing:module)
 return d,frozen,folder,receipt,state,module


@pytest.mark.parametrize('fault',[None,'module','support','notebook','receipt','test-status','environment','artifact','notebook-test-binding'])
def test_old_native_proof_cannot_validate_changed_science(new_module,fault):
 d,f,folder,r,state,module=new_module
 if fault=='module':(folder/'synthetic/package/execution.py').write_bytes(module+b'changed')
 elif fault=='support':(folder/'synthetic/package/support.py').write_bytes(b'changed')
 elif fault=='notebook':(folder/'revised.ipynb').write_bytes(b'changed')
 elif fault=='receipt':(folder/'synthetic/receipt.json').write_text('{}')
 elif fault=='test-status':state['notebook_revision_result']['synthetic_status']='FAIL'
 elif fault=='environment':f['historical_science']['controller_environment']={'wrong':True}
 elif fault=='artifact':state['artifacts'][1]['version']=13
 elif fault=='notebook-test-binding':(folder/'synthetic/package/revised.ipynb').write_text('different notebook')
 if fault:
  with pytest.raises((ValueError,KeyError)):c.response_native_equivalence(d,f)
 else:c.response_native_equivalence(d,f)


@pytest.fixture
def historical(tmp_path,monkeypatch):
 import orchestrator
 from orchestrator import modal_pinned_image as image
 lane=tmp_path/'lane';lane.mkdir();(lane/'lane.json').write_text('{}')
 local=sqlite3.connect(lane/'jobs.sqlite');local.row_factory=sqlite3.Row
 glob=sqlite3.connect(':memory:');glob.row_factory=sqlite3.Row
 for db,table in [(local,'manual_calls'),(glob,'autonomy_calls')]:
  db.execute('CREATE TABLE '+table+'(id TEXT,status TEXT,stage TEXT,attempt INTEGER,receipt TEXT)')
  for i in range(22):db.execute('INSERT INTO '+table+' VALUES(?,?,?,?,?)',(str(i),'COMPLETE','run_spec_author',13,json.dumps({'native':{'author_submission':{'status':'ACCEPTED','record_sha256':'a'*64}}})))
  db.commit()
 folder=lane/'notebook-revisions/author-13';package=folder/'synthetic/package';package.mkdir(parents=True)
 module=b'# native code';notebook=b'{"synthetic":"original"}';(package/'execution.py').write_bytes(module);(folder/'revised.ipynb').write_bytes(notebook)
 files={'execution.py':proof.sha(module)};env={'test':'environment'}
 receipt={'status':'PASS','exit_code':0,'binding':{'files':files,'environment':env},'preserved_files':{'package/execution.py':proof.sha(module)}}
 (folder/'synthetic/receipt.json').write_bytes(x.canonical(receipt));pin=proof.sha(x.canonical(receipt))
 selection={'author_call_id':'0','author_attempt':13,'accepted_submission_sha256':'a'*64,'controller_receipt_sha256':pin,'files':files,'environment':{'pinned':True}}
 n=NS(selected=lambda:selection);monkeypatch.setitem(sys.modules,'orchestrator.modal_native_synthetic',n);monkeypatch.setattr(orchestrator,'modal_native_synthetic',n,raising=False)
 image_state=tmp_path/'image';image_state.mkdir();(image_state/'binding.json').write_text('{}')
 monkeypatch.setattr(image,'consumer_proof',lambda *args:{'scientific_environment':selection['environment'],'scientific_acceptance':False})
 result={'folder':str(folder),'synthetic_status':'PASS','tests_sha256':pin,'notebook_sha256':proof.sha(notebook)}
 frozen={'author_attempt':14,'review_attempt':10,'configuration_sha256':proof.sha(b'{}'),
  'historical_science':{'notebook_revision_result':result,'execution_sha256':files['execution.py'],'native_files':files,'controller_environment':env,
   'artifacts':[{'id':'notebook_source','version':13,'sha256':proof.sha(notebook)},{'id':'synthetic_tests','version':13,'sha256':pin}]}}
 for db,table,key in [(local,'manual_calls','local_calls'),(glob,'autonomy_calls','global_calls')]:
  frozen[key]={r['id']:proof.sha(x.canonical(dict(r))) for r in db.execute('SELECT * FROM '+table)}
 yield NS(db=glob),NS(LANE=lane,IMAGE_STATE=image_state),frozen,local,glob,folder
 local.close();glob.close()


@pytest.mark.parametrize('fault',[None,'original-local','original-global','config','module','controller','scope','native-binding'])
def test_history_requires_originals_and_exact_native_binding_not_old_live_phase(historical,fault):
 accounts,native,f,local,glob,folder=historical
 if fault=='original-local':local.execute("UPDATE manual_calls SET status='UNCERTAIN' WHERE id='0'");local.commit()
 elif fault=='original-global':glob.execute("UPDATE autonomy_calls SET status='FAILED' WHERE id='0'");glob.commit()
 elif fault=='config':(native.LANE/'lane.json').write_text('{"changed":true}')
 elif fault=='module':(folder/'synthetic/package/execution.py').write_text('changed')
 elif fault=='controller':(folder/'synthetic/receipt.json').write_text('{}')
 elif fault=='scope':f['review_attempt']=11
 elif fault=='native-binding':f['historical_science']['execution_sha256']='0'*64
 if fault:
  with pytest.raises((ValueError,KeyError)):proof.historical_author_and_image(accounts,native,f)
 else:
  # No manual_state table exists: the evidence authenticates a historical author,
  # not a fabricated old current phase. The separate response gate checks live state.
  assert proof.historical_author_and_image(accounts,native,f)['scientific_acceptance'] is False
 assert local.execute('SELECT count(*) FROM manual_calls').fetchone()[0]==22
 assert glob.execute('SELECT count(*) FROM autonomy_calls').fetchone()[0]==22


@pytest.mark.parametrize('fault',[None,'child-failed','changed-proof','missing-delivery','changed-delivery'])
def test_response_evidence_gate_keeps_actual_proofs_and_complete_delivery(fifth,tmp_path,monkeypatch,fault):
 from orchestrator import manual_host_guard as hg
 import subprocess
 store,batch,config,d,f,*_=fifth;p,calls=probe(fifth)
 expected={'files':{'SOURCE_VERIFIED.json':{'sha256':'a'*64,'bytes':42}}}
 path=tmp_path/c.PROOF_DOCUMENT;path.parent.mkdir();path.write_text(json.dumps(expected))
 monkeypatch.setattr(c,'ROOT',tmp_path);monkeypatch.setattr(hg,'trusted',lambda p:p)
 result=NS(returncode=0,stdout=json.dumps(expected));runs=[]
 def run(*args,**kwargs):runs.append((args,kwargs));return result
 monkeypatch.setattr(subprocess,'run',run)
 evidence={'files':[{'name':'SOURCE_VERIFIED.json','sha256':'a'*64,'bytes':42}]}
 if fault=='child-failed':result.returncode=1
 elif fault=='changed-proof':result.stdout='{}'
 elif fault=='missing-delivery':evidence['files']=[]
 elif fault=='changed-delivery':evidence['files'][0]['bytes']=43
 if fault:
  with pytest.raises(ValueError):c.response_prerequisites(p,evidence,f,'9'*64)
 else:assert c.response_prerequisites(p,evidence,f,'9'*64)==expected
 assert Accounts(store).read()[1]['count']==22
 assert runs[0][0][0][1:3]==['-s','-B'] and runs[0][1]['timeout']==180


@pytest.mark.parametrize('fault',['workspace','pending-round','pending-workspace','count','global-status','argv'])
def test_reader_extension_requires_exact_admitted_review10(fifth,fault):
 store,batch,config,d,f,*_=fifth;accepted(fifth);p,calls=probe(fifth)
 work=Path(p.config['workspace_root'])/'run_spec_review-10'
 ident,n,receipt=store.reserve_call(config['run_id'],'run_spec_review',config['source'],'astra/manual-test',policy(),{})
 assert n==10
 v=x.state(store);v.update(phase='MODEL_RUNNING',pending={'id':ident,'stage':'run_spec_review','round':10,'workspace':str(work)})
 if fault=='pending-round':v['pending']['round']=9
 elif fault=='pending-workspace':v['pending']['workspace']=str(work.with_name('run_spec_review-9'))
 p.save(v)
 if fault=='workspace':work=work.with_name('run_spec_review-9')
 elif fault=='global-status':batch.db.execute("UPDATE autonomy_calls SET status='UNCERTAIN' WHERE id=?",(ident,))
 elif fault=='count':store.db.execute('DELETE FROM manual_calls WHERE id=?',(ident,))
 argv=['claude','--max-turns','30' if fault!='argv' else '100']
 with pytest.raises(ValueError):c.response_reviewer_command(lambda *args:argv,work,'run_spec_review',p,f,'9'*64)
 assert Accounts(store).read()[1]['count']==24
