"""Exact allocator boundary regression; full connected admission is also rehearsed on private DB copies."""
import ast,copy
from pathlib import Path
from types import SimpleNamespace as NS
import pytest
from orchestrator import item4_scoped_calls as scoped,item4_smoke_response as helper
from orchestrator import author_revision_accounting as accounting,experiment_collection
from tools import item4_diagnostic_review_runtime as runtime
from test_native_review_readiness_recovery import ready_scope

SEQUENCE=(('run_spec_author',14),('run_spec_review',10),('run_spec_review',11),
 ('run_spec_author',15),('run_spec_review',12),('run_spec_author',16),('run_spec_author',17),
 ('run_spec_review',13),('run_spec_author',18),('run_spec_author',19),('run_spec_review',14),
 ('run_spec_author',20),('run_spec_review',15),('run_spec_author',21),('run_spec_author',22),
 ('run_spec_author',23),('run_spec_author',24),('run_spec_review',16),
 ('result_interpretation_author',1),('result_interpretation_review',1))

@pytest.fixture
def allocation(ready_scope,monkeypatch):
 x=ready_scope;profile=helper.profile(x.p)
 monkeypatch.setattr(helper,'profile',lambda p:{**profile,'count':38})
 monkeypatch.setattr(accounting,'context',lambda store,run:x.driver)
 monkeypatch.setattr(accounting,'_accepted',lambda store,row:True)
 tail=[{'stage':stage,'attempt':n,'id':str(n)} for stage,n in SEQUENCE[:17]]
 def forbid_collection(*args):raise AssertionError('review is not post-execution interpretation')
 monkeypatch.setattr(experiment_collection,'verified',forbid_collection)
 namespace={**vars(scoped),'snapshot':lambda store:(tail,tail),'sequence':SEQUENCE,
  'continuation':NS(state=lambda store:x.value,sha=scoped.continuation.sha),
  'prefix':22,'response_stage':helper,'report_snapshot':x.p,'report_snapshot_approval':'a'*64,
  'response':{},**{k:None for k in ['mechanical','smoke','post_smoke','diagnostic','diagnostic_recovery',
   'diagnostic_scoped','diagnostic_native','diagnostic_plaintext','diagnostic_fixture','corrected_native','fixture_audit']}}
 tree=ast.parse(Path(scoped.__file__).read_text())
 outer=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='connect')
 fn=next(n for n in outer.body if isinstance(n,ast.FunctionDef) and n.name=='next_call')
 exec(compile(ast.Module(body=[fn],type_ignores=[]),str(Path(scoped.__file__)),'exec'),namespace)
 return NS(x=x,namespace=namespace,next=namespace['next_call'],tail=tail)


def test_reviewer16_needs_actual_native_gate_and_uses_it(allocation):
 a=allocation;x=a.x
 with pytest.raises(ValueError,match='REPORT_SNAPSHOT_AUTHOR_ONLY'):a.next(x.driver.store,'run_spec_review')
 restore=runtime.attach(x.driver,helper,x.p,'a'*64)
 try:
  assert a.next(x.driver.store,'run_spec_review')==scoped.continuation.sha((scoped.RUN+':run_spec_review:16').encode())
  assert x.seen[-3:]==['granted','review_binding','executable_candidate']
 finally:restore()
 with pytest.raises(ValueError,match='REPORT_SNAPSHOT_AUTHOR_ONLY'):a.next(x.driver.store,'run_spec_review')

@pytest.mark.parametrize('fault',['native','round','pending','protected','proof','missing-driver','unaccepted-author','later-stage','extra-call','wrong-profile'])
def test_other_refusals_survive_allocator_replacement(allocation,monkeypatch,fault):
 a=allocation;x=a.x;restore=runtime.attach(x.driver,helper,x.p,'a'*64);stage='run_spec_review'
 if fault=='native':x.value['diagnostic_native_evidence']={}
 elif fault=='round':x.value['rounds']['run_spec_author']=23
 elif fault=='pending':x.value['pending']={'id':'already-started'}
 elif fault=='protected':x.value['protected']='changed'
 elif fault=='proof':x.value['proof']={}
 elif fault=='missing-driver':monkeypatch.setattr(accounting,'context',lambda *args:None)
 elif fault=='unaccepted-author':monkeypatch.setattr(accounting,'_accepted',lambda *args:False)
 elif fault=='wrong-profile':
  profile=helper.profile(x.p);monkeypatch.setattr(helper,'profile',lambda p:{**profile,'author':23})
 elif fault=='extra-call':a.tail.append({'stage':'run_spec_review','attempt':16,'id':'extra'})
 else:stage='result_interpretation_author';x.value['phase']=stage
 try:
  with pytest.raises(ValueError):a.next(x.driver.store,stage)
 finally:restore()


@pytest.fixture
def admission(ready_scope,monkeypatch):
 from orchestrator import manual_recovery as local,stocktake_review_recovery as glob
 x=ready_scope;x.driver.config.update(source='s'*40)
 x.driver.current=lambda:x.value
 retained={'failed_id':'timeout','preserved_failures':['older-preserved'],'opaque_grant':'unchanged'}
 monkeypatch.setattr(local,'permit',lambda store,run:copy.deepcopy(retained))
 monkeypatch.setattr(glob,'admission',lambda *args:['unrelated-original'])
 x.terminal_ok=True;x.originals_ok=True
 def originals(*args):
  assert x.originals_ok,'original history refused'
  x.seen.append('originals')
 def connect_terminal():
  previous=glob.admission
  def checked(*args):
   result=previous(*args)
   if args[1]==helper.RUN:
    assert x.terminal_ok,'terminal qualification refused'
    x.seen.append('terminal-qualified')
    return [*result,'qualified-colab']
   return result
  glob.admission=checked
 monkeypatch.setattr(runtime,'load',lambda name,path:NS(connect_timing_admission=connect_terminal))
 restore_ready=runtime.attach(x.driver,helper,x.p,'a'*64)
 restore=runtime.bind_admission(x.driver,NS(originals=originals),(1,2,3,NS(CALL='qualified-historical')),helper,x.p,'a'*64)
 try:yield NS(x=x,local=local,glob=glob,retained=retained)
 finally:restore();restore_ready()


def test_exact_review_preserves_existing_grants_and_requires_terminal_proof(admission):
 a=admission;x=a.x
 v=a.local.permit(x.driver.store,helper.RUN)
 assert v=={**a.retained,'preserved_failures':['older-preserved','timeout','qualified-historical',helper.SENDER_FAILED_CALL]}
 got=a.glob.admission(x.driver.store.batch,helper.RUN,'run_spec_review',helper.call(x.p,'review'),'s'*40,{})
 assert got==[*v['preserved_failures'],'qualified-colab'] and x.seen[-1]=='terminal-qualified'
 assert a.local.permit(object(),'unrelated')==a.retained
 assert a.glob.admission(object(),'unrelated','any','any','any',{})==['unrelated-original']
 assert a.retained['preserved_failures']==['older-preserved']

@pytest.mark.parametrize('fault',['native','originals','terminal','pending','author','wrong-source','wrong-call','wrong-owner'])
def test_review_preserved_failure_connection_stays_exact(admission,fault):
 a=admission;x=a.x;stage='run_spec_review';source='s'*40;ident=helper.call(x.p,'review');owner=x.driver.store.batch
 if fault=='native':x.value['diagnostic_native_evidence']={}
 elif fault=='originals':x.originals_ok=False
 elif fault=='terminal':x.terminal_ok=False
 elif fault=='pending':x.value['pending']={'id':'already-started'}
 elif fault=='author':stage='run_spec_author'
 elif fault=='wrong-source':source='changed'
 elif fault=='wrong-call':ident='changed'
 else:owner=object()
 with pytest.raises((ValueError,AssertionError)):
  a.glob.admission(owner,helper.RUN,stage,ident,source,{})
 assert 'terminal-qualified' not in x.seen


@pytest.mark.parametrize('fault',['load','connect'])
def test_failed_admission_hook_setup_restores_all_originals(ready_scope,monkeypatch,fault):
 from orchestrator import manual_recovery as local,stocktake_review_recovery as glob,manual_stage
 before=(local.permit,glob.admission,manual_stage.reviewer_command)
 def refusal(*args):raise ValueError('component refused')
 monkeypatch.setattr(runtime,'load',refusal if fault=='load' else lambda *args:NS(connect_timing_admission=refusal))
 x=ready_scope
 with pytest.raises(ValueError,match='component refused'):
  runtime.bind_admission(x.driver,None,None,helper,x.p,'a'*64)
 assert (local.permit,glob.admission,manual_stage.reviewer_command)==before
