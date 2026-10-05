"""A new disposition may import original completed stages; it cannot retry them."""
import hashlib
import json
import os
from pathlib import Path
import fcntl
from types import SimpleNamespace
import pytest
from orchestrator import protected_disposition as pd
from orchestrator import protected_investigator as pi
from orchestrator.protected_handover import Broker, model_output_format, scientific_timeout
from orchestrator.hosted_cycle import encoded

_REQUIRE_ROOT = pd._require_root


def digest(value):
    return hashlib.sha256(encoded(value)).hexdigest()


@pytest.fixture
def original(tmp_path, monkeypatch):
    # Production calls enforce uid0. Files use the real test UID so the same
    # ownership/no-symlink/0600 checks run on ordinary CI without privileges.
    monkeypatch.setattr(pd, '_require_root', lambda: None)
    root = tmp_path / 'turns'; root.mkdir(mode=0o700)
    event = {'turn_id': 'a'*64, 'attempt': '1', 'source': 'b'*40,
             'branch': 'astra/infrastructure-milestone-record', 'kind': 'astra_turn'}
    folder = root / ('a'*64+'-1'); folder.mkdir(mode=0o700)
    from test_protected_handover import broker as synthetic_broker
    broker = synthetic_broker(tmp_path)
    broker.config.update({'turn_root': str(root), 'sources': ['b'*40, 'c'*40], 'controller_uid': 10001})
    def put(name, value):
        raw = value if isinstance(value, bytes) else encoded(value)
        (folder/name).write_bytes(raw); (folder/name).chmod(0o600)
    packet = {'version': 1, 'trigger': 'completed-campaign-fixture', 'report': 'private preserved report'}
    put('packet.json', packet); put('binding.json', {'event': event, 'packet_sha256': digest(packet)})
    for stage in ('continuation', 'review'):
        put(stage+'.md', (stage+' original answer').encode())
        put(stage+'.input.md', b'original input')
        put(stage+'.stdout', b'original protocol')
        put(stage+'.stderr', b'')
        put(stage+'.operating-context.json', {'verified_source_commit': event['source'],
            'task_packet': {'name': 'packet.json', 'sha256': digest(packet)}})
        put(stage+'.request.json', {'prompt_sha256': 'd'*64})
        put(stage+'.started.json', {'stage': stage})
        put(stage+'.ended.json', {'returncode': 0})
        put(stage+'.process.json', {'stage': stage, 'returncode': 0})
        put(stage+'.process-identity.json', {'pid': 2000000000})
        receipt = {'stage': stage, 'returncode': 0, 'actual_model': None if stage=='continuation' else 'claude-fable-5'}
        for suffix,key in [('.stdout','stdout_sha256'),('.stderr','stderr_sha256'),('.md','answer_sha256'),
                           ('.input.md','input_sha256'),('.operating-context.json','operating_context_sha256')]:
            receipt[key] = hashlib.sha256((folder/(stage+suffix)).read_bytes()).hexdigest()
        put(stage+'.receipt.json', receipt)
    put('disposition.request.json', {'prompt_sha256': 'e'*64})
    measurement = {'schema': 'hosted-final-input-measurement/v1', 'stage': 'disposition', 'family': 'codex',
        'characters': 1133404, 'utf8_bytes': 1133422, 'input_sha256': 'f'*64,
        'limit_basis': 'OBSERVED_CODEX_INPUT_CHARACTERS', 'limit_characters': 1048576,
        'provider_calls': 0, 'provider_limit_verified': True}
    put('disposition.input-refused.json', {'status':'PREFLIGHT_INPUT_REFUSED','measurement':measurement,
        'provider_calls':0,'automatic_retry':False})
    (root/'branch.lock').write_bytes(b''); (root/'branch.lock').chmod(0o600)
    return broker,event,folder,put,measurement


def test_exact_pure_refusal_is_stable_read_only_and_preserves_both_replies(original):
    broker,event,folder,_,_=original
    before={p.name:(p.stat().st_ino,p.read_bytes()) for p in folder.iterdir()}
    proof=pd.disposition_refusal(broker, {'event':event})
    assert proof==pd.disposition_refusal(broker, {'event':event})
    assert proof['status']=='PREFLIGHT_REFUSED_NO_PROVIDER' and proof['admissions']==0
    assert all(proof[k] is False for k in ('active','started','answer_present','receipt_present'))
    assert {k:v['answer'] for k,v in proof['stages'].items()}=={
        'continuation':'continuation original answer','review':'review original answer'}
    assert set(proof['originals'])==set(proof['file_sha256'])=={
        'disposition.request.json','disposition.input-refused.json'}
    assert before=={p.name:(p.stat().st_ino,p.read_bytes()) for p in folder.iterdir()}


def test_retired_source_refusal_requires_original_admission_and_keeps_replies(original):
    broker,event,folder,_,_=original
    broker.handle({'operation':'admit_server','body':event},10001)
    before = broker.ledger.read()
    broker.config['sources'] = ['c'*40]
    proof = pd.disposition_refusal(broker, {'event':event})
    assert proof['status'] == 'PREFLIGHT_REFUSED_NO_PROVIDER'
    assert proof['stages']['review']['answer'] == 'review original answer'
    assert broker.ledger.read() == before


@pytest.mark.parametrize('name',['disposition.started.json','disposition.ended.json','disposition.process.json',
    'disposition.process-identity.json','disposition.stdout','disposition.stderr','disposition.md',
    'disposition.receipt.json','disposition.input.md','disposition.operating-context.json',
    'disposition.input-preflight.json','disposition.unknown'])
def test_any_other_disposition_artifact_even_dangling_link_refuses(original,name):
    b,e,f,_,_=original;(f/name).symlink_to(f/'absent')
    with pytest.raises(ValueError,match='STARTED_OUTPUT'):pd.disposition_refusal(b,{'event':e})


@pytest.mark.parametrize('field,value',[('stage','review'),('family','claude'),('characters',1048576),
    ('characters',True),('utf8_bytes',1),('provider_calls',True),('provider_calls',1),
    ('provider_limit_verified',False),('limit_characters',2097152),('input_sha256','a'*63),
    ('limit_basis','UNVERIFIED_CLAUDE_CONSERVATIVE_LOCAL_BOUND')])
def test_only_exact_native_codex_cap_measurement_proves_refusal(original,field,value):
    b,e,f,put,m=original;m[field]=value
    put('disposition.input-refused.json',{'status':'PREFLIGHT_INPUT_REFUSED','measurement':m,'provider_calls':0,'automatic_retry':False})
    with pytest.raises(ValueError,match='EXACT_INPUT_MEASUREMENT'):pd.disposition_refusal(b,{'event':e})


@pytest.mark.parametrize('field,value',[('provider_calls',True),('provider_calls',1),('automatic_retry',0),('status','TIMEOUT')])
def test_envelope_never_reclassifies_uncertain_or_started_failure(original,field,value):
    b,e,f,put,m=original;r={'status':'PREFLIGHT_INPUT_REFUSED','measurement':m,'provider_calls':0,'automatic_retry':False};r[field]=value
    put('disposition.input-refused.json',r)
    with pytest.raises(ValueError,match='EXACT_PREFLIGHT'):pd.disposition_refusal(b,{'event':e})


def test_duplicate_json_fields_and_noncanonical_originals_refuse(original):
    b,e,f,put,m=original
    raw=(f/'disposition.request.json').read_bytes().replace(b'{',b'{"prompt_sha256":"bad",',1)
    put('disposition.request.json',raw)
    with pytest.raises(ValueError,match='EXACT_PREFLIGHT'):pd.disposition_refusal(b,{'event':e})


@pytest.mark.parametrize('name',['packet.json','review.receipt.json','continuation.md','disposition.input-refused.json','disposition.request.json'])
def test_symlink_and_nonprivate_complete_originals_refuse(original,name):
    b,e,f,_,_=original;(f/name).chmod(0o644)
    with pytest.raises(ValueError,match='PROTECTED_ORIGINAL'):pd.disposition_refusal(b,{'event':e})
    (f/name).unlink();(f/name).symlink_to(f/'packet.json' if name!='packet.json' else f/'absent')
    with pytest.raises(ValueError,match='PROTECTED_ORIGINAL'):pd.disposition_refusal(b,{'event':e})


def test_owner_change_empty_lock_and_active_writer_are_not_refusal(original,monkeypatch):
    b,e,f,_,_=original
    with (f.parent/'branch.lock').open('rb') as stream:
        fcntl.flock(stream,fcntl.LOCK_EX|fcntl.LOCK_NB)
        with pytest.raises(ValueError,match='WRITER_ACTIVE'):pd.disposition_refusal(b,{'event':e})
    (f.parent/'branch.lock').write_bytes(b'x')
    with pytest.raises(ValueError,match='FIXED_WRITER_LOCK'):pd.disposition_refusal(b,{'event':e})
    (f.parent/'branch.lock').write_bytes(b'')
    uid=os.getuid();monkeypatch.setattr(pd.os,'getuid',lambda:uid+12345)
    with pytest.raises(ValueError,match='PROTECTED_DIRECTORY'):pd.disposition_refusal(b,{'event':e})


def test_actual_locked_original_callback_does_not_relock_or_use_socket(original):
    b,e,f,_,_=original
    with (f.parent/'branch.lock').open('rb') as stream:
        fcntl.flock(stream,fcntl.LOCK_EX|fcntl.LOCK_NB)
        proof=pi.original(b,'disposition_refusal',{'event':e},disposition_lock=stream)
    assert proof['status']=='PREFLIGHT_REFUSED_NO_PROVIDER'


def test_peer_identity_and_fixed_event_shape_are_required(original):
    b,e,f,_,_=original
    with pytest.raises(ValueError,match='BROKER_PEER'):b.handle({'operation':'disposition_refusal','body':{'event':e}},10002)
    with pytest.raises(ValueError,match='EVENT_ONLY'):pd.disposition_refusal(b,{'event':e,'path':str(f)})
    with pytest.raises(ValueError):pd.disposition_refusal(b,{'event':{**e,'turn_id':'../outside'}})
    with pytest.raises(ValueError,match='HISTORICAL_ADMISSION_REQUIRED'):pd.disposition_refusal(b,{'event':{**e,'source':'d'*40}})


def test_missing_or_changed_completed_stage_cannot_authorize_successor(original):
    b,e,f,put,_=original
    put('review.md',b'changed')
    with pytest.raises(ValueError,match='MODEL_RECEIPT_CHANGED'):pd.disposition_refusal(b,{'event':e})
    (f/'review.receipt.json').unlink()
    with pytest.raises(FileNotFoundError):pd.disposition_refusal(b,{'event':e})


def test_replacement_during_read_or_disposition_created_after_stage_read_refuses(original,monkeypatch):
    b,e,f,put,_=original;status=b.stage_status
    def change(body):
        result=status(body)
        if body['stage']=='review':put('disposition.started.json',{'stage':'disposition'})
        return result
    monkeypatch.setattr(b,'stage_status',change)
    with pytest.raises(ValueError,match='CHANGED_DURING_PROOF'):pd.disposition_refusal(b,{'event':e})


def successor(proof):
    original={'schema':'disposition-successor-original-proof/v1','origin_event':proof['event'],
        'packet':proof['packet'],'protected_original':{k:v for k,v in proof.items() if k!='packet'}}
    packet={'version':1,'trigger':'linked-campaign-disposition','linked_disposition':{
        'schema':'linked-campaign-disposition/v1','source':'c'*40,'request':'d'*64,
        'origin_task':'a'*64,'origin_source':'b'*40,'original_proof_sha256':digest(original),
        'change_request':{'request_id':'e'*64,'applied_event':'f'*64}},
        'reviewer_evidence':{'original':original},'recorded_changes':{}}
    event={'turn_id':'d'*64,'attempt':'1','source':'c'*40,
           'branch':'astra/infrastructure-milestone-record','kind':'astra_turn'}
    return {'event':event,'stage':'disposition','packet':packet,'prompt':'fixed successor prompt'}


def test_typed_packet_is_single_disposition_only_and_keeps_bounded_timeout(original):
    b,e,_,_,_=original;body=successor(pd.disposition_refusal(b,{'event':e}))
    assert model_output_format(body['packet'],'disposition')=='markdown'
    assert scientific_timeout({'scientific_model_timeout_seconds':600},body['packet'])==600
    for stage in ('continuation','review'):
        with pytest.raises(ValueError,match='SINGLE_LINKED'):model_output_format(body['packet'],stage)
    body['packet']['execution_proposal']={}
    with pytest.raises(ValueError,match='SINGLE_LINKED'):model_output_format(body['packet'],'disposition')


def verifier_result(body,old_event):
    return {'status':'VERIFIED_LINKED_DISPOSITION_LAUNCH','event':body['event'],
        'packet_sha256':digest(body['packet']),'original_event':old_event,
        'original_proof_sha256':body['packet']['linked_disposition']['original_proof_sha256'],
        'request':body['packet']['linked_disposition']['request'],'source':'c'*40,'stage':'disposition'}


def test_997_verifier_and_second_locked_original_read_bind_exact_new_event(original,monkeypatch):
    b,e,f,_,_=original;body=successor(pd.disposition_refusal(b,{'event':e}));seen=[]
    from orchestrator import protected_scientific_jobs as psj
    monkeypatch.setattr(psj,'controller_configuration',lambda broker:{'source':'c'*40})
    def verify(broker,config,mode,value,*,disposition_lock):
        seen.append((mode,value,disposition_lock.fileno()))
        assert pi.original(broker,'disposition_refusal',{'event':e},disposition_lock=disposition_lock)['status']=='PREFLIGHT_REFUSED_NO_PROVIDER'
        return verifier_result(value,e)
    monkeypatch.setattr(pi,'verify_subprocess',verify)
    with (f.parent/'branch.lock').open('rb') as stream:
        fcntl.flock(stream,fcntl.LOCK_EX|fcntl.LOCK_NB)
        assert pd.verify_successor_launch(b,body,stream)['source']=='c'*40
    assert seen[0][:2]==('disposition_launch',body)


@pytest.mark.parametrize('field,value',[('status','APPROVE'),('packet_sha256','0'*64),
    ('request','0'*64),('source','b'*40),('stage','continuation'),('original_proof_sha256','0'*64)])
def test_self_asserted_or_mismatched_child_result_never_bypasses_prior_stages(original,monkeypatch,field,value):
    b,e,f,_,_=original;body=successor(pd.disposition_refusal(b,{'event':e}))
    from orchestrator import protected_scientific_jobs as psj
    monkeypatch.setattr(psj,'controller_configuration',lambda broker:{'source':'c'*40})
    result=verifier_result(body,e);result[field]=value
    monkeypatch.setattr(pi,'verify_subprocess',lambda *a,**kw:result)
    with (f.parent/'branch.lock').open('rb') as stream:
        fcntl.flock(stream,fcntl.LOCK_EX|fcntl.LOCK_NB)
        with pytest.raises(ValueError,match='BINDING_CHANGED|SOURCE_OR_PROOF_CHANGED'):pd.verify_successor_launch(b,body,stream)


def test_production_root_identity_guard_is_not_a_request_flag(monkeypatch):
    monkeypatch.setattr(pd.os,'getuid',lambda:10001)
    with pytest.raises(ValueError,match='PROTECTED_ROOT'):_REQUIRE_ROOT()


@pytest.fixture
def launcher(original,monkeypatch):
    b,e,f,put,m=original;proof=pd.disposition_refusal(b,{'event':e});body=successor(proof)
    from contextlib import nullcontext
    from orchestrator import protected_handover as ph, hosted_cycle as hc, hosted_context as ctx
    from orchestrator import remote_supervisor as rs, operations_report as op
    b.config.update({'model_mode':'GOVERNED','mode':'SYNTHETIC_FIXTURE','scientific_model_timeout_seconds':600,'policy':{}})
    b.ledger=object();calls=[]
    monkeypatch.setattr(ph.os,'getuid',lambda:0)
    monkeypatch.setattr(op,'private_root',lambda path:Path(path))
    monkeypatch.setattr(hc,'private_root',lambda path:Path(path))
    monkeypatch.setattr(rs,'checked_source',lambda *args:Path(__file__).parent)
    monkeypatch.setattr(b,'authentication',lambda:nullcontext())
    monkeypatch.setattr(ctx,'compose_input',lambda *a,**kw:('bounded final input',{}))
    def admit(*a):calls.append(('admit',a[-1]));return {'status':'ADMITTED'}
    monkeypatch.setattr(ph,'admit_server',admit)
    def model(folder,stage,family,prompt,**kw):
        calls.append(('model',stage,family,kw));return 'new disposition',{'stage':stage,'returncode':0}
    monkeypatch.setattr(hc,'model_call',model)
    monkeypatch.setattr(pd,'verify_successor_launch',lambda broker,value,stream:calls.append(('verified',value['event'])))
    return b,e,f,body,calls


def test_broker_only_validated_single_stage_uses_fresh_folder_and_originals_unchanged(launcher):
    b,e,f,body,calls=launcher;before={p.name:p.read_bytes() for p in f.iterdir()}
    result=b.model_stage(body)
    assert result['status']=='COMPLETE' and [c[0] for c in calls]==['verified','admit','model']
    assert calls[-1][1:3]==('disposition','astra') and calls[-1][3]['timeout_seconds']==600
    new=f.parent/(body['event']['turn_id']+'-1')
    assert json.loads((new/'binding.json').read_bytes())['event']['source']=='c'*40
    assert all(not p.name.startswith(('continuation.','review.')) for p in new.iterdir())
    assert before=={p.name:p.read_bytes() for p in f.iterdir()}


def test_current_verifier_refusal_precedes_any_new_turn_admission_or_provider(launcher,monkeypatch):
    b,e,f,body,calls=launcher
    def refuse(*a):raise ValueError('CURRENT_REPAIR_REVIEW_REQUIRED')
    monkeypatch.setattr(pd,'verify_successor_launch',refuse)
    with pytest.raises(ValueError,match='CURRENT_REPAIR'):b.model_stage(body)
    assert calls==[] and not (f.parent/(body['event']['turn_id']+'-1')).exists()


def test_ordinary_third_stage_still_requires_same_turn_predecessors(launcher):
    b,e,f,body,calls=launcher;body['packet']={'version':1,'trigger':'ordinary-campaign'}
    with pytest.raises(ValueError,match='PREDECESSOR_MODEL_RECEIPT_REQUIRED'):b.model_stage(body)
    assert calls==[]


@pytest.mark.parametrize('saved',['disposition.started.json','disposition.input-refused.json'])
def test_new_successor_uncertainty_or_second_refusal_is_terminal_no_retry(launcher,saved):
    b,e,f,body,calls=launcher;new=f.parent/(body['event']['turn_id']+'-1');new.mkdir(mode=0o700)
    (new/'binding.json').write_bytes(encoded({'event':body['event'],'packet_sha256':digest(body['packet'])}))
    (new/'packet.json').write_bytes(encoded(body['packet']));(new/saved).write_bytes(encoded({'preserved':True}))
    before=(new/saved).read_bytes()
    with pytest.raises(ValueError,match='RECONCILE_NO_RETRY'):b.model_stage(body)
    assert [c[0] for c in calls]==['verified'] and (new/saved).read_bytes()==before


def test_material_gate_and_source_guard_still_precede_linked_launch(launcher,monkeypatch):
    b,e,f,body,calls=launcher
    def refuse():raise ValueError('CURRENT_DEPLOYMENT_REVIEW_REQUIRED')
    monkeypatch.setattr(b,'reviewed_deployment',refuse)
    with pytest.raises(ValueError,match='CURRENT_DEPLOYMENT'):b.handle({'operation':'model_stage','body':body},b.config['controller_uid'])
    from orchestrator import remote_supervisor as rs
    def bad_source(*a):raise ValueError('EXECUTING_SOURCE_CHANGED')
    monkeypatch.setattr(rs,'checked_source',bad_source)
    with pytest.raises(ValueError,match='EXECUTING_SOURCE_CHANGED'):b.model_stage(body)
    assert calls==[]


def test_fixed_child_mode_invokes_only_installed_pure_verifier(monkeypatch):
    import io,sys
    from orchestrator import protected_investigator as pi
    config={'controller_uid':os.getuid(),'source':'c'*40};body={'event':'fixture'};seen=[]
    payload={'config':config,'mode':'disposition_launch','value':body}
    class Stream:
        def __init__(self,raw=b''):self.buffer=io.BytesIO(raw)
    stdin=Stream(pi.message(payload)+pi.message({'status':'ORIGINAL'}));stdout=Stream()
    def verify(c,b,reader):
        seen.append((c,b));assert reader('/fixed/socket','disposition_refusal',{'event':'old'})=={'status':'ORIGINAL'}
        return {'status':'FIXTURE_VERIFIED'}
    monkeypatch.setitem(sys.modules,'orchestrator.disposition_successors',SimpleNamespace(verify_launch=verify))
    monkeypatch.setattr(pi.sys,'argv',['protected_investigator','--verify'])
    monkeypatch.setattr(pi.sys,'stdin',stdin);monkeypatch.setattr(pi.sys,'stdout',stdout)
    pi.main();frames=[json.loads(line) for line in stdout.buffer.getvalue().splitlines()]
    assert seen==[(config,body)] and frames==[
        {'operation':'disposition_refusal','body':{'event':'old'}},{'verified':{'status':'FIXTURE_VERIFIED'}}]


@pytest.mark.parametrize("held", [False, True])
def test_scientific_runtime_reads_real_broker_original_with_existing_lock(original, held):
    from contextlib import nullcontext
    from orchestrator.scientific_evidence_runtime import protected_original_client
    broker,event,folder,_,_=original
    assert not hasattr(broker, "disposition_refusal")
    expected=pd.disposition_refusal(broker, {"event":event})
    before={p.name:(p.stat().st_ino,p.read_bytes()) for p in folder.iterdir()}
    manager=(folder.parent/"branch.lock").open("rb") if held else nullcontext(None)
    with manager as stream:
        if held: fcntl.flock(stream,fcntl.LOCK_EX|fcntl.LOCK_NB)
        client=(protected_original_client(broker,disposition_lock=stream) if held
                else protected_original_client(broker))
        assert client("", "disposition_refusal", {"event":event})==expected
        with pytest.raises(ValueError,match="SCIENTIFIC_RUNTIME_ORIGINAL_READ_ONLY"):
            client("", "model_stage", {"event":event})
    assert before=={p.name:(p.stat().st_ino,p.read_bytes()) for p in folder.iterdir()}


def test_scientific_runtime_keeps_real_original_integrity_and_lock_guards(original):
    from orchestrator.scientific_evidence_runtime import protected_original_client
    broker,event,folder,put,_=original
    with (folder.parent/"branch.lock").open("rb") as held:
        fcntl.flock(held,fcntl.LOCK_EX|fcntl.LOCK_NB)
        with pytest.raises(ValueError,match="WRITER_ACTIVE"):
            protected_original_client(broker)("", "disposition_refusal", {"event":event})
        client=protected_original_client(broker,disposition_lock=held)
        put("review.md",b"altered original")
        with pytest.raises(ValueError,match="MODEL_RECEIPT_CHANGED"):
            client("", "disposition_refusal", {"event":event})
    with (folder/"review.md").open("rb") as wrong:
        with pytest.raises(ValueError,match="FIXED_WRITER_LOCK"):
            protected_original_client(broker,disposition_lock=wrong)("", "disposition_refusal", {"event":event})


def test_actual_model_stage_forwards_its_held_lock_before_admission(original,monkeypatch):
    from orchestrator import protected_handover as ph, scientific_evidence_runtime as rt
    broker,event,folder,_,_=original
    expected=pd.disposition_refusal(broker,{"event":event})
    broker.config.update(model_mode="SUPERVISED",max_model_turns=10)
    monkeypatch.setattr(ph,"os",SimpleNamespace(getuid=lambda:0))
    monkeypatch.setattr("orchestrator.remote_supervisor.checked_source",lambda root,source:root)
    observed=[]
    def capture(actual,packet,*,source,folder,stage,disposition_lock=None):
        assert actual is broker and disposition_lock is not None
        value=rt.protected_original_client(actual,disposition_lock=disposition_lock)(
            "","disposition_refusal",{"event":event})
        assert value==expected
        observed.append(value)
        raise RuntimeError("STOP_BEFORE_ADMISSION_OR_PROVIDER")
    monkeypatch.setattr(rt,"broker_capture",capture)
    with pytest.raises(RuntimeError,match="STOP_BEFORE_ADMISSION_OR_PROVIDER"):
        broker.model_stage({"event":{**event,"turn_id":"d"*64},"stage":"continuation",
            "packet":{"version":1},"prompt":"Read preserved evidence."})
    assert len(observed)==1
