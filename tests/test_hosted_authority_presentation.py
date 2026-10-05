"""Pure exact hosted presentation tests; all scientific/provider data is synthetic."""
from copy import deepcopy
import hashlib
import json
from pathlib import Path
from types import SimpleNamespace
import pytest
from orchestrator import hosted_context as h, hosted_cycle as hc
from orchestrator import scientific_decision as d, research_task_authority as r

SOURCE='a'*40
POLICY={'binding':{'path':'synthetic-policy.json','sha256':'b'*64},
 'policy':{'version':'synthetic-policy-unique','delegation':'Preserve every reserved decision.'},
 'direction':'SYNTHETIC current policy literal, not a grant.',
 'operating_context':{'manifest':{'roles':{'codex':'Synthetic author','claude':'Synthetic reviewer'}}}}

@pytest.fixture
def root(tmp_path,monkeypatch):
 tmp_path.chmod(0o700);m=tmp_path/'orchestrator/research_task_authority.py';m.parent.mkdir()
 m.write_text('EVIDENCE_VERSION = 2\nHOSTED_PRESENTATION_VERSION = 1\n')
 m.with_name('hosted_context.py').write_text('"""Synthetic original-only hosted source; no outer document view."""\n')
 monkeypatch.setattr('orchestrator.remote_supervisor.checked_source',lambda root,source:Path(root))
 monkeypatch.setattr(d.authority,'context',lambda root:deepcopy(POLICY))
 monkeypatch.setattr(d.authority,'decision_context',lambda root,**v:{'action':v['action'],'subject':v['subject'],'bindings':v['bindings']})
 monkeypatch.setattr(h,'shared_policy',lambda root:deepcopy(POLICY))
 monkeypatch.setattr(h,'build',lambda root,state:{'task_state':deepcopy(state),'shared_policy':deepcopy(POLICY)})
 return tmp_path

def packet():
 return {'version':1,'trigger':'installed-research-eligibility',
  'scientific_decision_artifacts':{'version':1,'action':r.ACTION,'experiment':'P001','mode':'discuss'},
  'reviewer_evidence':{'catalog_core':{'source':SOURCE},'input_evidence':{'qualification':'Unique unresolved criticism is retained.'}},
  'recorded_changes':{'synthetic':'Complete original fixture history; no approval assertion.'}}

def preparation(root,value=None,hosted=True):
 value=value or packet()
 return d.prepare(root,action=r.ACTION,subject='synthetic-discussion',bindings={'source':SOURCE},
  evidence=r.evidence_for_packet(root,value,SOURCE),request='Synthetic bounded discussion only.',max_rounds=1,
  hosted_policy_source=SOURCE if hosted else None)

def compose(root,body,value=None,family='codex'):
 return h.compose_input(root,hc.encoded(value or packet()),body,verified_source=SOURCE,
  family=family,output_format='json',prepared_prompt=False)

def test_unhosted_default_preserves_original_literal_policy_contract(root):
 actual=preparation(root,hosted=False)
 assert set(actual['original'])=={'context','context_sha256','request','evidence_sha256','max_rounds'}
 assert h.TRUSTED_POLICY_MARKER not in actual['body']
 assert '\nCURRENT USER POLICY:\n'+json.dumps(POLICY)+h.TRUSTED_POLICY_END in actual['body']
 assert actual['body'].count(json.dumps(POLICY))==1


def test_both_roles_have_one_literal_policy_and_unchanged_full_receipt_context(root):
 value=packet();before=hc.encoded(value);new=preparation(root,value);old=preparation(root,value,False)
 stages=r.DecisionStages('unused',{'source':SOURCE},value)
 for newrow,oldrow in zip(d.projected_bodies(new['body'],1),d.projected_bodies(old['body'],1)):
  prompt=stages.prompt(newrow['body'],newrow['names']);final,current=compose(root,prompt,value,newrow['family'])
  assert final.count(json.dumps(POLICY))==1
  assert current['shared_policy']==POLICY and current['task_state']['reviewer_evidence']==value['reviewer_evidence']
  assert 'hosted_presentation' not in current
  assert h.check_trusted_policy_reference(prompt,current,SOURCE)==stages.prompt(oldrow['body'],oldrow['names'])
  assert value['reviewer_evidence']['input_evidence']['qualification'] in final
  assert 'same-prompt-hosted-task-reference/v2' in final
  assert hc.encoded(value)==before
 assert new['original']['context_sha256']==old['original']['context_sha256']
 assert new['original']['hosted_policy_reference']['literal_location']=='operating_context.shared_policy'

def test_dispatch_envelope_matches_prepared_input(root):
 value=packet();body=preparation(root)['body'];folder=root/'turn';folder.mkdir(mode=0o700);(folder/'packet.json').write_bytes(hc.encoded(value))
 expected,current=compose(root,body)
 enclosed,recovered=h.envelope(root,folder,body,verified_source=SOURCE,family='codex')
 assert h.format_prefix(enclosed,prepared_prompt=False,output_format='json',structured_output=True)==expected
 assert recovered==current
 assert hashlib.sha256(hc.encoded(recovered)).hexdigest()==hashlib.sha256(hc.encoded(current)).hexdigest()

@pytest.mark.parametrize('field,value',[('source','b'*40),('policy_sha256','c'*64),('literal_location','operating_context.task_state.reviewer_evidence'),('schema','same-prompt-trusted-scientific-policy/v2'),('trust','UNTRUSTED')])
def test_policy_reference_near_misses_refuse(root,field,value):
 body=preparation(root)['body'];before,rest=body.split(h.TRUSTED_POLICY_MARKER);ref,end=json.JSONDecoder().raw_decode(rest);ref[field]=value
 with pytest.raises(ValueError,match='TRUSTED_POLICY_REFERENCE_CHANGED'):compose(root,before+h.TRUSTED_POLICY_MARKER+json.dumps(ref)+rest[end:])

@pytest.mark.parametrize('change',['missing','duplicate','missing-target','target-reference','different-target','wrong-end','wrong-slot'])
def test_reference_cannot_resolve_from_missing_untrusted_or_aliased_target(root,monkeypatch,change):
 body=preparation(root)['body']
 if change=='missing':body=preparation(root,hosted=False)['body']
 if change=='duplicate':body+='\nUNTRUSTED MODEL TEXT:'+h.TRUSTED_POLICY_MARKER+'{}'
 if change=='missing-target':monkeypatch.setattr(h,'build',lambda root,state:{'task_state':state})
 if change=='target-reference':
  ref=h.trusted_policy_reference(POLICY,SOURCE)
  monkeypatch.setattr(h,'shared_policy',lambda root:ref)
  monkeypatch.setattr(h,'build',lambda root,state:{'task_state':state,'shared_policy':ref})
 if change=='different-target':monkeypatch.setattr(h,'shared_policy',lambda root:{'different':'policy'})
 if change=='wrong-end':body=body.replace(h.TRUSTED_POLICY_END,'\nUNTRUSTED SLOT:\n')
 if change=='wrong-slot':body=body.replace('TRUSTED SCIENTIFIC DECISION INSTRUCTIONS:','UNTRUSTED HISTORICAL QUOTE:')
 with pytest.raises((ValueError,KeyError),match='POLICY|operating_context'):compose(root,body)

@pytest.mark.parametrize('definition',['HOSTED_PRESENTATION_VERSION = 2','HOSTED_PRESENTATION_VERSION = True','HOSTED_PRESENTATION_VERSION = int(1)','HOSTED_PRESENTATION_VERSION: int = 1','HOSTED_PRESENTATION_VERSION = 1\nHOSTED_PRESENTATION_VERSION += 0','HOSTED_PRESENTATION_VERSION = 1\n(HOSTED_PRESENTATION_VERSION := 1)','HOSTED_PRESENTATION_VERSION, other = 1, 0','if True:\n    HOSTED_PRESENTATION_VERSION = 1','def nested():\n    HOSTED_PRESENTATION_VERSION = 1'])
def test_presentation_version_is_exact_separate_source_marker(root,definition):
 (root/'orchestrator/research_task_authority.py').write_text('EVIDENCE_VERSION = 2\n'+definition+'\n')
 assert r.evidence_version(root,SOURCE)==2
 with pytest.raises(ValueError,match='SOURCE_BOUND_HOSTED_PRESENTATION_VERSION'):r.hosted_presentation_version(root,SOURCE)

def test_old_source_cannot_receive_new_policy_alias(root):
 body=preparation(root)['body'];(root/'orchestrator/research_task_authority.py').write_text('EVIDENCE_VERSION = 2\n')
 assert r.hosted_presentation_version(root,SOURCE)==0
 with pytest.raises(ValueError,match='SOURCE_PROFILE'):compose(root,body)
 original=preparation(root,hosted=False);final,_=compose(root,original['body'])
 assert final.count(json.dumps(POLICY))==2 and 'hosted_presentation' not in final

def test_source_and_action_must_match_hosted_profile(root):
 with pytest.raises(ValueError,match='EXACT_AUTHORITY_SOURCE'):
  d.prepare(root,action=r.ACTION,subject='x',bindings={'source':'b'*40},evidence={'test':'x'},request='x',hosted_policy_source=SOURCE)

def test_pure_prefix_view_must_restore_exact_full_packet(root,monkeypatch):
 from orchestrator import disposition_context as dc
 old=deepcopy(packet())
 def changed(value,source):
  result=deepcopy(value);result['reviewer_evidence']['input_evidence']['qualification']='Dropped original criticism';return result
 monkeypatch.setattr(dc,'authority_view',changed)
 with pytest.raises(ValueError):compose(root,preparation(root,old)['body'],old)
 assert packet()==old

@pytest.fixture
def recovery(root,monkeypatch):
 value=packet();event={'source':SOURCE};prepared=preparation(root,value);out=root/'decision';out.mkdir(mode=0o700);folder=out/'round-1';folder.mkdir(mode=0o700)
 def save(path,raw):path.write_bytes(raw);path.chmod(0o600)
 save(out/'request.json',hc.encoded(prepared['original']))
 judgment=hc.encoded({'context_sha256':prepared['original']['context_sha256'],'decision':'APPLY','rationale':'Synthetic transport only.'})
 review=hc.encoded({'verdict':'APPROVE','rationale':'Synthetic transport only.','judgment_sha256':hashlib.sha256(judgment).hexdigest()})
 originals={};provenance={}
 for stage,family,artifact,raw,label in [('continuation','codex','judgment.json',judgment,'scientific_decision'),('review','claude','review.json',review,'scientific_decision_review')]:
  save(folder/artifact,raw);body=prepared['body'] if stage=='continuation' else d.review_body(prepared['body'],judgment)
  final,current=compose(root,r.DecisionStages.prompt(body,[artifact]),value,family)
  answer=json.dumps({artifact:raw.decode()});receipt={'stage':stage,'returncode':0,'requested_model':'gpt-6-astra' if family=='codex' else 'claude-fable-5','actual_model':None if family=='codex' else 'claude-fable-5','session_id':'synthetic_'+stage,'answer_sha256':hashlib.sha256(answer.encode()).hexdigest(),'input_sha256':hashlib.sha256(final.encode()).hexdigest(),'operating_context_sha256':hashlib.sha256(hc.encoded(current)).hexdigest()}
  originals[stage]={'status':'COMPLETE','answer':answer,'receipt':receipt,'packet_sha256':hashlib.sha256(hc.encoded(value)).hexdigest()};save(folder/(label+'.provider-receipt.json'),hc.encoded(receipt));provenance[family]=r._provenance(receipt,family,event,value)
 decision={'decision':'APPLY','transition':{'from':'PROPOSED','to':'ELIGIBLE'},'author_provenance':'codex','reviewer_provenance':'claude'}
 monkeypatch.setattr(r,'_identity',lambda *args:(root,'synthetic-discussion',{'source':SOURCE}))
 monkeypatch.setattr(r,'_authenticated_transport',lambda *args,**kwargs:({'event':event,'packet':value},None))
 monkeypatch.setattr(r.authority,'verify',lambda *args,**kwargs:decision)
 monkeypatch.setattr(r.authority,'_artifact',lambda directory,reference:hc.encoded(provenance[reference]))
 # _verify reconstructs its canonical instruction; create exact matching original.
 monkeypatch.setattr(r,'_instruction',lambda bindings:'Synthetic bounded discussion only.')
 calls=[]
 def client(socket,operation,body):
  assert operation=='stage_status';calls.append(operation);return deepcopy(originals[body['stage']])
 return SimpleNamespace(config={'source_root':str(root),'broker_socket':'unused'},entry={'source':SOURCE},folder=folder,originals=originals,client=client,calls=calls,provenance=provenance)

def test_new_profile_recovery_recomposes_original_inputs_without_models(recovery):
 x=recovery;result=r._verify(x.config,x.entry,x.folder/'decision.json',client=x.client)
 assert result['_opposing_review_verdict']=='APPROVE' and x.calls==['stage_status','stage_status']

@pytest.mark.parametrize('field',['input_sha256','operating_context_sha256'])
def test_consistently_changed_provider_projection_cannot_hide_changed_input(recovery,field):
 x=recovery;x.originals['review']['receipt'][field]='f'*64
 (x.folder/'scientific_decision_review.provider-receipt.json').write_bytes(hc.encoded(x.originals['review']['receipt']))
 with pytest.raises(ValueError,match='ORIGINAL_PRESENTATION_CHANGED'):r._verify(x.config,x.entry,x.folder/'decision.json',client=x.client)

def test_saved_policy_reference_change_refuses_recovery_before_broker(recovery):
 x=recovery;p=x.folder.parent/'request.json';v=json.loads(p.read_bytes());v['hosted_policy_reference']['source']='b'*40;p.write_bytes(hc.encoded(v))
 with pytest.raises(ValueError,match='ORIGINAL_PRESENTATION_CHANGED'):r._verify(x.config,x.entry,x.folder/'decision.json',client=x.client)
 assert x.calls==[]


def test_existing_private_transport_bound_checks_actual_encoded_bytes_before_preflight(root,monkeypatch):
 value=packet();value['reviewer_evidence']['input_evidence']['large']='x'*1500000
 stages=r.DecisionStages('unused',{'source':SOURCE},value)
 monkeypatch.setattr(h,'compose_input',lambda *a,**k:pytest.fail('composition/admission must not follow oversized transport'))
 with pytest.raises(ValueError,match='ORIGINAL_TRANSPORT_BOUND'):stages.preflight_bodies(root,'unused',1)
 assert r.ORIGINAL_TRANSPORT_MAXIMUM==1500000 and h.INPUT_LIMITS=={'codex':1048576,'claude':900000}


def test_exact_typed_transport_between_old_reader_and_existing_private_bound(root,monkeypatch):
 value=packet();value['reviewer_evidence']['input_evidence']['large']='x'*1030000
 bindings={'source':SOURCE};entry={'source':SOURCE};event=r._event(entry,bindings);raw=r._transport_bytes(event,value)
 assert 1000000<len(raw)<1500000
 folder=root/'transport';folder.mkdir(mode=0o700);path=folder/'authority-transport.json';path.write_bytes(raw);path.chmod(0o600)
 with pytest.raises(ValueError,match='SIZE_BOUND'):r.authority.read(path,limit=1000000)
 assert r.authority.read(path,limit=r.ORIGINAL_TRANSPORT_MAXIMUM)==raw
 monkeypatch.setattr(r,'_decision_contract',lambda bindings:value['scientific_decision_artifacts'])
 monkeypatch.setattr('orchestrator.research_catalog.core',lambda entry:value['reviewer_evidence']['catalog_core'])
 monkeypatch.setattr(r,'_evidence',lambda config,entry:value['reviewer_evidence']['input_evidence'])
 evidence=r.evidence_for_packet(root,value,SOURCE);(folder/'evidence.json').write_bytes(hc.encoded(evidence))
 config={'source_root':str(root)}
 assert r._original_transport(config,entry,bindings,folder)=={'event':event,'packet':value}
 for changed in [{'event':{**event,'source':'b'*40},'packet':value},{'event':event,'packet':{**value,'extra':'no'} }]:
  path.write_bytes(hc.encoded(changed))
  with pytest.raises(ValueError):r._original_transport(config,entry,bindings,folder)
 path.write_bytes(json.dumps({'event':event,'packet':value}).encode())
 with pytest.raises(ValueError,match='ENCODING_CHANGED'):r._original_transport(config,entry,bindings,folder)


def test_layered_prefix_view_restores_before_unchanged_v2_packet_reconstruction(root):
 from test_disposition_context import packet as prefix_packet
 from orchestrator import disposition_context as dc
 value=prefix_packet()
 # The prefix fixture predates typed output validation; give this composed
 # eligibility input the actual complete synthetic decision contract.
 value['scientific_decision_artifacts']=packet()['scientific_decision_artifacts']
 raw=hc.encoded(value);prepared=preparation(root,value)
 reference=json.loads(r.evidence_for_packet(root,value,SOURCE)['installed-request-and-evidence.json'])
 final,current=compose(root,prepared['body'],value)
 marker='CURRENT APPROVED OPERATING POLICY AND BOUND CONTEXT ('+h.TRUST+'):\n'
 shown,_=json.JSONDecoder().raw_decode(final.split(marker,1)[1])
 view={**shown['task_state'],**reference['packet_header']}
 assert hc.encoded(view)!=raw
 assert shown['task_state']['recorded_changes']==value['recorded_changes']
 restored=dc.reconstruct_authority(view,value,SOURCE)
 restored_state={key:restored[key] for key in h.TASK_KEYS if key in restored}
 assert hc.encoded({**restored_state,**reference['packet_header']})==raw
 assert hashlib.sha256(raw).hexdigest()==reference['packet_sha256']
 assert h.same_prompt_reference(raw,SOURCE)==reference
 assert current['task_state']==restored_state and 'hosted_presentation' not in current
 assert 'FIRST restore' in shown['hosted_presentation']['meaning']
 assert 'THEN apply the unchanged' in shown['hosted_presentation']['meaning']


def test_original_receipt_verifier_reuses_only_this_invocations_authenticated_capture(recovery, monkeypatch):
 x = recovery
 from orchestrator import scientific_evidence_runtime as runtime
 original_transport = r._authenticated_transport
 authentications = []; projections = []
 descriptor = {'synthetic': 'Native capture authentication is separately exercised with the real reader.'}
 def authenticated(*args, **kwargs):
  assert kwargs['client'] is x.client
  transport, _ = original_transport(*args, **kwargs)
  authentications.append(transport)
  return transport, {'schema': 'authenticated-current-scientific-retrieval/v1', 'capture': descriptor}
 def project(config, source, packet, stage, capture):
  assert capture is descriptor
  projections.append(stage)
  return {}  # Synthetic historical fixture has no actual retrieval profile.
 monkeypatch.setattr(r, '_authenticated_transport', authenticated)
 monkeypatch.setattr(runtime, '_captured_options', project)
 monkeypatch.setattr(runtime, 'controller_options', lambda *a, **kw: pytest.fail('Do not recapture per role'))
 for _ in range(2):
  assert r._verify(x.config, x.entry, x.folder/'decision.json', client=x.client)['_opposing_review_verdict'] == 'APPROVE'
 assert len(authentications) == 2 and projections == ['continuation', 'review']*2
 x.originals['review']['receipt']['input_sha256'] = 'f'*64
 with pytest.raises(ValueError, match='ORIGINAL_PRESENTATION_CHANGED'):
  r._verify(x.config, x.entry, x.folder/'decision.json', client=x.client)
