import copy,json
from datetime import datetime,timedelta,timezone
from types import SimpleNamespace as NS
from unittest.mock import Mock
import pytest
from tools import item4_review8_proof as proof,item4_scientific_revision_component as component

@pytest.mark.parametrize('props',[
 'ActiveState=activating\nMainPID=42\nExecMainStatus=0\nControlGroup=/job',
 'ActiveState=failed\nMainPID=0\nExecMainStatus=1\nControlGroup=',
 'ActiveState=inactive\nMainPID=0\nExecMainStatus=0',
 'ActiveState=inactive\nMainPID=0\nExecMainStatus=0\nControlGroup=/job'])
def test_running_failed_or_incomplete_source_refused(props):
 with pytest.raises(ValueError,match='SOURCE_NOT_COMPLETE'):proof.terminal(props)

def test_terminal_success_required():
 proof.terminal('MainPID=0\nExecMainStatus=0\nActiveState=inactive\nControlGroup=')

@pytest.fixture
def receipt(monkeypatch):
 canonical=lambda x:json.dumps(x,sort_keys=True).encode()
 now=datetime.now(timezone.utc);inventory='a'*64
 binding={'helper_source':proof.SOURCE,'source_volume_id':'vo-original','envelope':{'reserved_micro_usd':3321330},
  'created_at':(now-timedelta(hours=1)).isoformat(),'expires_at':(now+timedelta(days=29)).isoformat(),
  'inventory_sha256':inventory}
 ident=proof.sha(canonical(binding));monkeypatch.setattr(proof,'ASSET',ident)
 membership={'count':893,'bytes':7202931657,'excluded_overlap':0}
 handle={'binding_sha256':ident,'name':'research-item4-base-source-'+ident[:24],'volume_id':'vo-composed','version':2}
 saved={'status':'VERIFIED','binding_sha256':ident,'source_volume_id':'vo-original','volume_id':'vo-composed',
  'inventory_sha256':inventory,'membership':membership,'reserved_micro_usd':3321330,
  'expires_at':binding['expires_at'],'scientific_approval':False,'patient_analysis':False,
  'new_provider_compute':False,'originals_preserved':True,'completed_at':(now-timedelta(minutes=1)).isoformat()}
 return [binding,ident,{'status':'READY','receipt':json.dumps(saved)},saved,
  {'binding_sha256':ident,**membership},handle,membership,inventory,canonical,now]

def test_exact_ready_receipt_passes_without_mutation(receipt):
 before=copy.deepcopy(receipt);proof.source_receipt(*receipt);assert receipt==before

@pytest.mark.parametrize('damage',['reserved','ledger-receipt','wrong-release','wrong-id','membership','inventory',
 'volume','old-volume','version','local','charge','expired','future','scientific-claim'])
def test_source_receipt_mismatch_fails_closed(receipt,damage):
 b,i,row,saved,local,handle,member,inv,canonical,now=receipt
 if damage=='reserved':row['status']='RESERVED'
 elif damage=='ledger-receipt':row['receipt']='{}'
 elif damage=='wrong-release':b['helper_source']='0'*40
 elif damage=='wrong-id':receipt[1]='0'*64
 elif damage=='membership':saved['membership']={'count':892}
 elif damage=='inventory':saved['inventory_sha256']='b'*64
 elif damage=='volume':handle['binding_sha256']='0'*64
 elif damage=='old-volume':saved['volume_id']=handle['volume_id']='vo-original'
 elif damage=='version':handle['version']=1
 elif damage=='local':local['count']=892
 elif damage=='charge':saved['reserved_micro_usd']=0
 elif damage=='expired':receipt[-1]=now+timedelta(days=30)
 elif damage=='future':saved['completed_at']=(now+timedelta(hours=1)).isoformat()
 else:saved['scientific_approval']=True
 if damage not in ('ledger-receipt','reserved'):row['receipt']=json.dumps(saved)
 with pytest.raises(ValueError):proof.source_receipt(*receipt)

@pytest.mark.parametrize('field',['verdict','change_id','source_sha','report_sha256',None])
def test_fourth_grant_remains_bound_to_original_approval(tmp_path,monkeypatch,field):
 from orchestrator import autonomy_review as ar,manual_host_guard as hg
 approval={'verdict':'APPROVE','change_id':'item4-review7-continuation-20261009',
  'source_sha':component.FOURTH_SOURCE,'report_sha256':component.FOURTH_REVIEW}
 monkeypatch.setattr(component,'RECORD',tmp_path);monkeypatch.setattr(hg,'trusted',lambda p:p)
 calls=[]
 def verify(p):calls.append(p);return approval
 monkeypatch.setattr(ar,'verify_result',verify)
 if field:
  approval[field]='wrong'
  with pytest.raises(ValueError,match='HELD_FOURTH_CONTINUATION_APPROVAL'):component.held_fourth_continuation_approval()
 else:assert component.held_fourth_continuation_approval()==component.FOURTH_REVIEW
 assert calls==[tmp_path/'history'/component.FOURTH_SOURCE/'original-review-directory']

@pytest.mark.parametrize('damage',[None,'stage','pending','round','call-count','child-failed','changed-proof','missing-delivery','changed-delivery'])
def test_review_gate_requires_exact_stage_and_authentic_delivered_proof(tmp_path,monkeypatch,damage):
 from orchestrator import manual_host_guard as hg
 import subprocess
 state={'phase':'run_spec_review','rounds':{'run_spec_author':13,'run_spec_review':7}}
 db=Mock();db.execute.return_value.fetchone.return_value=(20,)
 driver=NS(current=lambda:state,store=NS(db=db))
 expected={'files':{'SOURCE_VERIFIED.json':{'sha256':'a'*64,'bytes':42}}}
 path=tmp_path/component.PROOF_DOCUMENT;path.parent.mkdir();path.write_text(json.dumps(expected))
 monkeypatch.setattr(component,'ROOT',tmp_path);monkeypatch.setattr(hg,'trusted',lambda p:p)
 result=NS(returncode=0,stdout=json.dumps(expected));calls=[]
 def run(*args,**kwargs):calls.append((args,kwargs));return result
 monkeypatch.setattr(subprocess,'run',run)
 evidence={'files':[{'name':'SOURCE_VERIFIED.json','sha256':'a'*64,'bytes':42}]}
 if damage=='stage':state['phase']='run_spec_author'
 elif damage=='pending':state['pending']={'id':'open'}
 elif damage=='round':state['rounds']['run_spec_review']=8
 elif damage=='call-count':db.execute.return_value.fetchone.return_value=(21,)
 elif damage=='child-failed':result.returncode=1
 elif damage=='changed-proof':result.stdout='{}'
 elif damage=='missing-delivery':evidence['files']=[]
 elif damage=='changed-delivery':evidence['files'][0]['sha256']='b'*64
 if damage:
  with pytest.raises(ValueError):component.review8_prerequisites(driver,evidence)
 else:
  assert component.review8_prerequisites(driver,evidence)==expected
  assert calls[0][0][0][1:3]==['-s','-B']
  assert calls[0][1]['timeout']==180
 if damage in ['stage','pending','round','call-count']:assert not calls
