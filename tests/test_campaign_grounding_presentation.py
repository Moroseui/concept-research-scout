"""Synthetic source/transport fixtures; no provider or scientific result."""
import copy,hashlib,json
from pathlib import Path
from types import SimpleNamespace
import pytest
from orchestrator import hosted_campaign as h,campaign_pipeline as p,hosted_context as hc
from orchestrator.hosted_cycle import encoded
from orchestrator.hosted_campaign_task import task_contract

SOURCE='a'*40
REMOTE='docs/operations/REMOTE_OPERATING_DIRECTION.md'

@pytest.fixture
def example(tmp_path,monkeypatch):
    root=tmp_path/'immutable';(root/'orchestrator').mkdir(parents=True)
    (root/'orchestrator/hosted_campaign.py').write_text('CAMPAIGN_GROUNDING_VERSION = 1\n')
    (root/'orchestrator/hosted_context.py').write_text('OUTER_DOCUMENT_VIEW_VERSION = 1\n')
    def checked(path,source):
        if Path(path)!=root or source!=SOURCE:raise ValueError('WRONG_IMMUTABLE_SOURCE')
        return root
    monkeypatch.setattr('orchestrator.remote_supervisor.checked_source',checked)
    task={'schema':'investigator-task/v1','task_id':'investigator-'+'b'*64,'experiment':'P001',
        'mode':'investigate','request':'Synthetic bounded selection','references':[],'selected_by':None,
        'template_sha256':'c'*64,'wake_sha256':'b'*64,'purpose':'CHARTER_SELECTION'}
    supplement={'continuing-research-inputs.json':json.dumps({'task':task,'references':[],
        'eligible_protocols':[],'protocol_blocks':[]})}
    context={};current={'documents':{},'selected_scientific_context':{},
        'shared_policy':{'operating_context':{'documents':{},'manifest':{'roles':{'codex':'Author','claude':'Reviewer'}}}}}
    for name,path in h.GROUNDING_TARGETS.items():
        content='Exact synthetic '+name+'\nQuote " and heading BOUND CONTEXT:\n'
        context[name]=content
        holder=current
        for key in path[:-1]:holder=holder.setdefault(key,{})
        holder[path[-1]]=content
        holder['sha256']=hashlib.sha256(content.encode()).hexdigest()
    current['documents'][REMOTE]={'content':context[REMOTE],
        'sha256':hashlib.sha256(context[REMOTE].encode()).hexdigest(),'disposition':'APPROVED_OPERATING_DIRECTION'}
    for name in ['configs/scientific-delegation-20260909.json','context-disposition.json','investigator-scope.json']:
        context[name]='Literal original '+name
    monkeypatch.setattr(p,'grounding',lambda *args,**kwargs:dict(context))
    monkeypatch.setattr('orchestrator.research_context.evidence_context',lambda *args:{})
    monkeypatch.setattr(hc,'shared_policy',lambda *args:copy.deepcopy(current['shared_policy']))
    monkeypatch.setattr(hc,'build',lambda root,state:{**copy.deepcopy(current),'task_state':state})
    packet={'trigger':'installed-research-request','campaign_task':task,'campaign_artifacts':task_contract(task),
        'research_request_binding':{'source':SOURCE,'task_id':task['task_id']},
        'reviewer_evidence':{'full_criticism':'Unchanged original'},'recorded_changes':{'pending':['original']}}
    prepared=p.prepare_input(root,'investigate','P001',task['request'],formal_task=task,supplemental_context=supplement)
    return SimpleNamespace(root=root,task=task,packet=packet,current=current,prepared=prepared,supplement=supplement)


def test_fixed_references_restore_complete_original_with_literal_context_disposition(example):
    e=example
    view=h.grounding_view(e.prepared['context'],e.current,SOURCE)
    assert sum(isinstance(v,dict)for v in view.values())==11
    assert isinstance(view['context-disposition.json'],str)
    assert view[REMOTE]['literal_location'][1]=='shared_policy'
    assert h._restore_grounding(view,e.current,SOURCE)==e.prepared['context']
    assert e.prepared['input_sha256']=={k:hashlib.sha256(v.encode()).hexdigest()for k,v in e.prepared['context'].items()}


@pytest.mark.parametrize('mutation',['source','name','location','hash','length','bool_length','extra','missing','alias_target'])
def test_exact_reference_mutations_refuse(example,mutation):
    e=example;view=h.grounding_view(e.prepared['context'],e.current,SOURCE);current=copy.deepcopy(e.current)
    ref=view[REMOTE]
    if mutation=='source':ref['source']='d'*40
    elif mutation=='name':ref['name']='renamed'
    elif mutation=='location':ref['literal_location']=['operating_context','documents',REMOTE,'content']
    elif mutation=='hash':ref['sha256']='0'*64
    elif mutation=='length':ref['utf8_bytes']+=1
    elif mutation=='bool_length':ref['utf8_bytes']=True
    elif mutation=='extra':ref['extra']=True
    elif mutation=='missing':del view[REMOTE]
    else:current['shared_policy']['operating_context']['documents'][REMOTE]['text']={'schema':'alias'}
    with pytest.raises(ValueError,match='GROUNDING'):h._restore_grounding(view,current,SOURCE)


def test_canonical_whole_envelope_and_original_body_binding(example):
    e=example
    raw=h._typed_prompt(e.root,SOURCE,e.packet,e.prepared,'continuation','')
    final,original=hc.compose_input(e.root,encoded(e.packet),raw,verified_source=SOURCE,family='codex',output_format='json')
    assert original['task_state']['reviewer_evidence']==e.packet['reviewer_evidence']
    assert original['documents'][REMOTE]['content']==e.current['documents'][REMOTE]['content']
    assert 'same-prompt-investigator-grounding/v1' in final
    assert 'Literal original context-disposition.json' in final
    data=json.loads(raw[len(h.GROUNDING_PREFIX):]);data['original_prompt_sha256']='0'*64
    with pytest.raises(ValueError,match='ORIGINAL_BODY_CHANGED'):
        hc.compose_input(e.root,encoded(e.packet),h.GROUNDING_PREFIX+json.dumps(data,sort_keys=True),
            verified_source=SOURCE,family='codex',output_format='json')
    with pytest.raises(ValueError,match='ENVELOPE'):
        hc.compose_input(e.root,encoded(e.packet),raw+' ',verified_source=SOURCE,family='codex',output_format='json')


def test_wrong_stage_packet_and_source_refuse(example):
    e=example;raw=h._typed_prompt(e.root,SOURCE,e.packet,e.prepared,'continuation','')
    for packet,family in [(e.packet,'claude'),({**e.packet,'reviewer_evidence':{'changed':True}},'codex')]:
        with pytest.raises(ValueError,match='ENVELOPE_CHANGED'):
            hc.compose_input(e.root,encoded(packet),raw,verified_source=SOURCE,family=family,output_format='json')
    with pytest.raises(ValueError,match='WRONG_IMMUTABLE_SOURCE'):
        h.grounding_version(e.root,'d'*40)


@pytest.mark.parametrize('marker',['CAMPAIGN_GROUNDING_VERSION = True','CAMPAIGN_GROUNDING_VERSION = 2',
    'CAMPAIGN_GROUNDING_VERSION = 1\nCAMPAIGN_GROUNDING_VERSION = 1',
    'if True:\n    CAMPAIGN_GROUNDING_VERSION = 1',
    'CAMPAIGN_GROUNDING_VERSION = 1\ndel CAMPAIGN_GROUNDING_VERSION'])
def test_exact_source_profile_rejects_nonliteral_duplicate_or_nested(example,marker):
    (example.root/'orchestrator/hosted_campaign.py').write_text(marker+'\n')
    with pytest.raises(ValueError,match='SOURCE_BOUND'):h.grounding_version(example.root,SOURCE)


def test_old_profile_keeps_literal_and_rejects_new_envelope(example):
    e=example
    (e.root/'orchestrator/hosted_campaign.py').write_text('# Historical profile without marker\n')
    (e.root/'orchestrator/hosted_context.py').write_text('# Historical profile without marker\n')
    assert h.grounding_version(e.root,SOURCE)==0
    plain=h.artifact_prompt(e.prepared['body'],['selection.json'])
    assert h.grounding_presentation(e.root,e.packet,e.current,plain,SOURCE,family='codex')==plain
    raw=h._typed_prompt(e.root,SOURCE,e.packet,e.prepared,'continuation','')
    with pytest.raises(ValueError,match='SOURCE_PROFILE_REQUIRED'):
        h.grounding_presentation(e.root,e.packet,e.current,raw,SOURCE,family='codex')


def test_worst_reviewer_refuses_without_provider_or_runtime(example):
    e=example
    packet=copy.deepcopy(e.packet);packet['reviewer_evidence']['pressure']='x'*885000
    with pytest.raises(hc.InputTooLarge) as refusal:
        h.campaign_preflight(e.root,SOURCE,packet,supplement=e.supplement)
    assert refusal.value.measurement['stage']=='review'
    assert refusal.value.measurement['provider_calls']==0


@pytest.mark.parametrize('retrieval',[False,True])
def test_preflight_and_actual_transport_use_identical_constructor_and_original_context(example,tmp_path,monkeypatch,retrieval):
    e=example;calls=[];originals={}
    from orchestrator import scientific_evidence_runtime as runtime
    config={'source':SOURCE,'state':str(tmp_path/'state'),'change_request_store':str(tmp_path/'store'),
            'controller_uid':__import__('os').getuid()}
    if retrieval:
        (e.root/'orchestrator/scientific_evidence_runtime.py').write_text('SCIENTIFIC_ROLE_INPUT_VERSION = 1\n')
        e.packet['scientific_change_history']={'synthetic_native_capture':'separately verified in backend checks'}
        capture={'synthetic':'immutable'}
        descriptor={'schema':'scientific-evidence-capture/v1','source':SOURCE,
            'task_binding':hashlib.sha256(encoded(e.packet)).hexdigest(),'manifest_sha256':'e'*64,'record_count':3}
        # This transport test substitutes only the already separately tested
        # native-store read/write boundary. Composition and receipt checks are real.
        from orchestrator import scientific_evidence_access as access,protected_scientific_jobs
        descriptor['schema']=access.SCHEMA
        # Replace the complete native-original capture boundary, including its
        # linked-history/prerequisite verification. Those have separate native-store
        # fixtures; this test compares composition/transport of one descriptor.
        def fixture_capture(config, packet, source, **kwargs):
            assert packet == e.packet and source == SOURCE
            return capture
        monkeypatch.setattr(runtime,'_capture',fixture_capture)
        monkeypatch.setattr(access,'describe_capture',lambda value:descriptor)
        monkeypatch.setattr(access,'write_capture',lambda directory,value:descriptor)
        monkeypatch.setattr(protected_scientific_jobs,'controller_configuration',lambda broker:config)
        # History selection has its own native fixtures; this fixture isolates
        # caller/preflight/dispatch/recovery with one immutable descriptor.
        monkeypatch.setattr(hc,'selected_history_presentation',lambda *args,**kwargs:None)

    projection=h.campaign_preflight(e.root,SOURCE,e.packet,supplement=e.supplement,evidence_config=config)
    author=json.dumps({'selection.json':'x'*30000})
    reviewer=json.dumps({'review.json':json.dumps({'verdict':'APPROVE','rationale':'Synthetic transport'})})
    def client(socket,operation,body):
        calls.append(operation);assert operation=='model_stage'
        stage=body['stage'];family='codex' if stage=='continuation' else 'claude'
        actual=runtime.broker_capture(None,e.packet,source=SOURCE,folder=tmp_path/stage,stage=stage)
        options={} if actual is None else {'evidence_access':actual}
        final,current=hc.compose_input(e.root,encoded(e.packet),body['prompt'],verified_source=SOURCE,family=family,output_format='json',**options)
        assert ('bound scientific evidence' in final)==retrieval
        answer=author if stage=='continuation' else reviewer
        model='gpt-6-astra' if stage=='continuation'else'claude-fable-5'
        receipt={'requested_model':model,'actual_model':None if stage=='continuation'else model,
            'returncode':0,'answer_sha256':hashlib.sha256(answer.encode()).hexdigest(),
            'input_sha256':hashlib.sha256(final.encode()).hexdigest(),
            'operating_context_sha256':hashlib.sha256(encoded(current)).hexdigest()}
        result={'status':'COMPLETE','answer':answer,'packet_sha256':hashlib.sha256(encoded(e.packet)).hexdigest(),'receipt':receipt}
        originals[stage]=result;return result
    stages=h.BrokerStages('fixture',{'source':SOURCE},e.packet,client=client,source_root=e.root,source=SOURCE,supplement=e.supplement,evidence_config=config)
    directory=tmp_path/'outputs';directory.mkdir(mode=0o700)
    stages(None,directory,'codex','campaign_investigate',e.prepared['body'],['selection.json'])
    proposal='selection.json\n'+'x'*30000
    stages(None,directory,'claude','campaign_investigate_review',p.reviewer_body(e.prepared['body'],proposal,('APPROVE','REVISE','REQUEST_CHANGES')),['review.json'])
    assert calls==['model_stage','model_stage']
    for i,stage in enumerate(('continuation','review')):
        assert originals[stage]['receipt']['input_sha256']==projection['stages'][i]['input_sha256']
    reads=[]
    def recover(socket,operation,body):
        reads.append(operation);assert operation=='stage_status';return originals[body['stage']]
    reader=h.BrokerStages('fixture',{'source':SOURCE},e.packet,client=recover,recovery=True,
        source_root=e.root,source=SOURCE,supplement=e.supplement,evidence_config=config)
    reader.call('continuation','');reader.call('review','')
    assert reads==['stage_status','stage_status']
    bad=h.BrokerStages('fixture',{'source':SOURCE},e.packet,client=recover,recovery=True,
        source_root=e.root,source=SOURCE,supplement=e.supplement,evidence_config=config)
    originals['continuation']['receipt']['input_sha256']='0'*64
    with pytest.raises(ValueError,match='ORIGINAL_INPUT_OR_CONTEXT_CHANGED'):bad.call('continuation','')


def test_native_enqueue_preserves_refusal_before_returning_admissible_binding(example,tmp_path,monkeypatch):
    from orchestrator.handover_runtime import Runtime
    e=example;state=tmp_path/'state';state.mkdir(mode=0o700)
    evidence={'full_criticism':'x'*885000}
    request={'source':SOURCE,'task_id':e.task['task_id'],'identity':'d'*64,'day':'2026-09-12'}
    monkeypatch.setattr('orchestrator.hosted_campaign_task.installed_research_request',
        lambda *args:(e.task,evidence,request))
    monkeypatch.setattr('orchestrator.research_catalog.selection',lambda *args:({}, {'predecessors':[]}))
    monkeypatch.setattr('orchestrator.research_catalog.eligibility',lambda *args:{'synthetic':'bound'})
    monkeypatch.setattr('orchestrator.continuing_research.supplemental_context',lambda *args,**kwargs:e.supplement)
    runtime=SimpleNamespace(root=e.root,state=state,config={'source':SOURCE})
    with pytest.raises(hc.InputTooLarge) as refused:
        Runtime.enqueue_report(runtime,'2026-09-12',[],{'research_request_identity':request['identity']},
            reviewer_evidence=evidence,trigger='installed-research-request',research_task_id=e.task['task_id'])
    assert refused.value.measurement['stage']=='review'
    receipts=list((state/'tasks').glob('*/campaign-input-projection-refused.json'))
    assert len(receipts)==1
    saved=json.loads(receipts[0].read_bytes())
    assert saved['status']=='PROSPECTIVE_CAMPAIGN_INPUT_REFUSED' and saved['models']==saved['admissions']==0
    assert not list((state/'tasks').glob('*/disposition-input-projection.json'))
    assert json.loads(receipts[0].with_name('packet.json').read_bytes())['reviewer_evidence']==evidence


@pytest.mark.parametrize('form',['literal-newline','unicode'])
def test_actual_file_utf8_bound_dominates_review_literal_proposal_pressure(example,form):
    e=example
    # The final reconstructed proposal is literal text, not JSON-escaped again.
    value=('\n'*30000 if form=='literal-newline' else '\u00e9'*15000)
    assert len(value.encode())==30000
    proposal='selection.json\n'+value
    prompt=h._typed_prompt(e.root,SOURCE,e.packet,e.prepared,'review',proposal)
    final,_=hc.compose_input(e.root,encoded(e.packet),prompt,verified_source=SOURCE,family='claude',output_format='json')
    projected=h.campaign_preflight(e.root,SOURCE,e.packet,supplement=e.supplement)['stages'][1]
    assert len(final)<=projected['characters']


@pytest.mark.parametrize('mode,expected',[('discuss', 'fd14747de0d6c3ca9c36f35224712794e65dcad02a2257f7c4cb643247e992af'), ('charter', 'bc3707f6894e86fadcdf8232f43abe4ebd4e34fe2c307c9a8544e3d643c6ce8e')])
def test_original_unhosted_body_bytes_match_retained_base_golden(mode,expected):
    actual=p.author_body(mode,'Synthetic question',{'z':'Last\n','a':'First "quoted"\n'})
    assert hashlib.sha256(actual.encode()).hexdigest()==expected
