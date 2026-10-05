"""Conclusive input rejection is narrower than an ended or uncertain model call."""
import hashlib
import json
import os
from pathlib import Path
import pytest
from orchestrator.hosted_cycle import encoded
from orchestrator.protected_handover import Broker
from orchestrator.protected_investigator import stage_input_refusal


def saved(tmp_path, monkeypatch, *, unicode_input=False):
    root = tmp_path / 'turns'; root.mkdir(mode=0o700)
    event = {'turn_id':'a'*64, 'attempt':'1', 'source':'b'*40,
             'branch':'astra/infrastructure-milestone-record', 'kind':'astra_turn'}
    folder = root / ('a'*64+'-1'); folder.mkdir(mode=0o700)
    broker = object.__new__(Broker)
    broker.config = {'turn_root':str(root), 'sources':['b'*40], 'controller_uid':10001,
                     'mode':'SYNTHETIC_FIXTURE'}
    from types import SimpleNamespace
    from orchestrator.dispatch_limiter import initial
    broker.config['policy'] = {'fixture':'no historical admissions'}
    empty_ledger = initial()
    empty_ledger['policy_sha256'] = hashlib.sha256(
        json.dumps(broker.config['policy'], sort_keys=True).encode()).hexdigest()
    broker.ledger = SimpleNamespace(read=lambda: ('synthetic', empty_ledger))
    def put(name, value):
        raw = value if isinstance(value, bytes) else encoded(value)
        (folder/name).write_bytes(raw); (folder/name).chmod(0o600)
    packet = {'version':1, 'trigger':'input-bound-fixture'}
    packet_sha = hashlib.sha256(encoded(packet)).hexdigest()
    text = 'x'*1048577 + ('\u03b2' if unicode_input else '')
    put('packet.json', packet)
    put('binding.json', {'event':event, 'packet_sha256':packet_sha})
    put('continuation.request.json', {'prompt_sha256':'c'*64})
    put('continuation.started.json', {'stage':'continuation','requested_model':'gpt-6-astra',
        'started_utc':'2026-09-12T10:44:30+00:00','timeout_seconds':600})
    put('continuation.ended.json', {'returncode':1,'ended_utc':'2026-09-12T10:44:32+00:00'})
    put('continuation.input.md', text.encode())
    put('continuation.operating-context.json', {'verified_source_commit':'b'*40,
        'task_packet':{'name':'packet.json','sha256':packet_sha}})
    put('continuation.stdout', b'{"type":"thread.started","thread_id":"fixture-thread-001"}\n')
    details = {'input_error_code':'input_too_large','max_chars':1048576,'actual_chars':len(text)}
    put('continuation.stderr', ('Error: turn/start: turn/start failed: Input exceeds the maximum length of '
        '1048576 characters. (code -32602), data: '+json.dumps(details,separators=(',',':'))+'\n').encode())
    put('continuation.process-identity.json', {'pid':2000000000,'process_group':2000000000,
        'boot_id':Path('/proc/sys/kernel/random/boot_id').read_text().strip()})
    process = {'stage':'continuation','requested_model':'gpt-6-astra','returncode':1,
        'timeout_seconds':600,'actual_model':None,'usage':None,'wall_seconds':2.0}
    def bind_hashes():
        for name,key in [('stdout','stdout_sha256'),('stderr','stderr_sha256'),
                         ('input.md','input_sha256'),('operating-context.json','operating_context_sha256')]:
            process[key] = hashlib.sha256((folder/('continuation.'+name)).read_bytes()).hexdigest()
        put('continuation.process.json',process)
    bind_hashes()
    lock = root/'branch.lock'; lock.write_bytes(b''); lock.chmod(0o600)
    def gone(*_args): raise ProcessLookupError()
    monkeypatch.setattr(os,'killpg',gone)
    return broker,event,folder,put,process,bind_hashes


def test_complete_refusal_proof_is_stable_read_only_and_not_retry_authority(tmp_path,monkeypatch):
    b,e,f,put,p,bind=saved(tmp_path,monkeypatch,unicode_input=True)
    before={x.name:(x.stat().st_ino,x.read_bytes()) for x in f.iterdir()}
    proof=stage_input_refusal(b,{'event':e})
    assert proof==stage_input_refusal(b,{'event':e})
    assert proof['status']=='CONCLUSIVE_INPUT_REFUSAL'
    assert proof['input_characters']==len((f/'continuation.input.md').read_text())
    assert proof['input_characters']<len((f/'continuation.input.md').read_bytes())
    assert not proof['retry_authorized'] and not proof['scientific_acceptance'] and proof['admissions']==0
    assert 'continuation.input.md' not in proof['originals']
    assert proof['file_sha256']['packet.json']==proof['packet_sha256']
    assert before=={x.name:(x.stat().st_ino,x.read_bytes()) for x in f.iterdir()}


@pytest.mark.parametrize('code',[0,-9,True])
def test_other_return_classes_never_establish_input_refusal(tmp_path,monkeypatch,code):
    b,e,f,put,p,bind=saved(tmp_path,monkeypatch)
    put('continuation.ended.json',{'returncode':code,'ended_utc':'2026-09-12T10:44:32+00:00'})
    with pytest.raises(ValueError,match='EXACT_ENDED'):stage_input_refusal(b,{'event':e})


@pytest.mark.parametrize('extra',[
 b'{"type":"turn.completed"}\n', b'{"type":"item.completed","item":{"type":"agent_message","text":"answer"}}\n',
 b'\n', b'{"type":"error","message":"input too large"}\n'])
def test_any_additional_protocol_event_or_blank_output_refuses(tmp_path,monkeypatch,extra):
    b,e,f,put,p,bind=saved(tmp_path,monkeypatch)
    put('continuation.stdout',(f/'continuation.stdout').read_bytes()+extra);bind()
    with pytest.raises(ValueError,match='THREAD_ONLY'):stage_input_refusal(b,{'event':e})


def test_duplicate_protocol_fields_cannot_hide_an_answer(tmp_path,monkeypatch):
    b,e,f,put,p,bind=saved(tmp_path,monkeypatch)
    put('continuation.stdout',b'{"type":"turn.completed","type":"thread.started","thread_id":"fixture-thread-001"}\n');bind()
    with pytest.raises(ValueError,match='THREAD_ONLY'):stage_input_refusal(b,{'event':e})


@pytest.mark.parametrize('old,new',[('input_too_large','rate_limit'),('1048576','2097152'),('-32602','-32603'),('1048577','1048578')])
def test_error_class_limit_code_and_actual_count_are_exact(tmp_path,monkeypatch,old,new):
    b,e,f,put,p,bind=saved(tmp_path,monkeypatch)
    put('continuation.stderr',(f/'continuation.stderr').read_text().replace(old,new).encode());bind()
    with pytest.raises(ValueError,match='EXACT_PROVIDER|CHARACTER_COUNT'):stage_input_refusal(b,{'event':e})


@pytest.mark.parametrize('name',['continuation.md','continuation.receipt.json','review.started.json','disposition.request.json'])
def test_answer_or_any_later_stage_artifact_including_dangling_link_refuses(tmp_path,monkeypatch,name):
    b,e,f,put,p,bind=saved(tmp_path,monkeypatch);(f/name).symlink_to(f/'absent')
    with pytest.raises(ValueError,match='ANSWER_OR_RECEIPT|LATER_STAGE'):stage_input_refusal(b,{'event':e})


@pytest.mark.parametrize('field,value',[('actual_model','gpt-6-astra'),('usage',{}),('returncode',0)])
def test_validated_usage_or_different_process_cannot_be_reclassified(tmp_path,monkeypatch,field,value):
    b,e,f,put,p,bind=saved(tmp_path,monkeypatch);p[field]=value;bind()
    with pytest.raises(ValueError,match='EXACT_ENDED'):stage_input_refusal(b,{'event':e})


def test_hash_tampering_live_process_and_unknown_process_state_refuse(tmp_path,monkeypatch):
    b,e,f,put,p,bind=saved(tmp_path,monkeypatch)
    put('continuation.stdout',b'{"type":"thread.started","thread_id":"changed-thread-002"}\n')
    with pytest.raises(ValueError,match='PROCESS_HASH'):stage_input_refusal(b,{'event':e})
    bind();monkeypatch.setattr(os,'killpg',lambda *_args:None)
    with pytest.raises(ValueError,match='PROCESS_ACTIVE'):stage_input_refusal(b,{'event':e})
    def unknown(*_args):raise PermissionError()
    monkeypatch.setattr(os,'killpg',unknown)
    with pytest.raises(ValueError,match='STATE_UNAVAILABLE'):stage_input_refusal(b,{'event':e})


def test_symlink_nonprivate_file_missing_end_and_changed_context_refuse(tmp_path,monkeypatch):
    b,e,f,put,p,bind=saved(tmp_path,monkeypatch)
    (f/'continuation.stderr').chmod(0o644)
    with pytest.raises(ValueError,match='PROTECTED_ORIGINAL'):stage_input_refusal(b,{'event':e})
    (f/'continuation.stderr').chmod(0o600)
    put('continuation.operating-context.json',{'verified_source_commit':'d'*40});bind()
    with pytest.raises(ValueError,match='CONTEXT_BINDING'):stage_input_refusal(b,{'event':e})
    (f/'continuation.ended.json').unlink()
    with pytest.raises(FileNotFoundError):stage_input_refusal(b,{'event':e})


def test_fixed_event_source_schema_and_peer_identity_are_required(tmp_path,monkeypatch):
    b,e,f,put,p,bind=saved(tmp_path,monkeypatch)
    with pytest.raises(ValueError,match='EVENT_ONLY'):stage_input_refusal(b,{'event':e,'path':str(f)})
    with pytest.raises(ValueError,match='HISTORICAL_ADMISSION_REQUIRED'):
        stage_input_refusal(b,{'event':{**e,'source':'d'*40}})
    with pytest.raises(ValueError,match='SERVER_IDENTITY'):stage_input_refusal(b,{'event':{**e,'turn_id':'../outside'}})
    with pytest.raises(ValueError,match='PEER'):b.handle({'operation':'stage_input_refusal','body':{'event':e}},10002)


@pytest.mark.parametrize('field,value',[('boot_id','-'*36),('process_group',2000000000.0)])
def test_malformed_boot_and_noninteger_group_cannot_skip_liveness(tmp_path,monkeypatch,field,value):
    b,e,f,put,p,bind=saved(tmp_path,monkeypatch)
    identity=json.loads((f/'continuation.process-identity.json').read_bytes());identity[field]=value
    put('continuation.process-identity.json',identity)
    with pytest.raises(ValueError,match='PROCESS_IDENTITY'):stage_input_refusal(b,{'event':e})
