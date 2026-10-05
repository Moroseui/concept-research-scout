"""Synthetic output/command cases; no provider call or approval is represented."""
import copy
import json
from pathlib import Path
import pytest
from orchestrator import scientific_output as output
from orchestrator.hosted_campaign import artifact_files
from orchestrator.hosted_cycle import model_command
from orchestrator.hosted_context import measure_input, InputTooLarge

PACKET = {"scientific_decision_artifacts": {
    "version": 1, "action": "authorize_research_task", "experiment": "P001", "mode": "discuss"}}
AUTHOR = {"judgment.json": {"context_sha256": "a"*64, "decision": "DEFER",
    "rationale": "Synthetic rationale", "transition": {"from": "PROPOSED", "to": "DEFERRED"},
    "reconsideration": "Synthetic condition"}}
REVIEW = {"review.json": {"verdict": "REVISE", "rationale": "Synthetic adverse finding",
                          "judgment_sha256": "b"*64}}

@pytest.mark.parametrize("stage,value", [("continuation", AUTHOR), ("review", REVIEW)])
def test_projection_keeps_decision_and_adverse_text(stage, value):
    selected = output.contract(PACKET, stage)
    raw = output.project(value, selected)
    files = artifact_files(raw, list(value))
    assert {name: json.loads(content) for name, content in files.items()} == value
    assert selected["schema"]["additionalProperties"] is False

@pytest.mark.parametrize("replacement", [[], {}, None, True, 7, "", "  "])
def test_original237_type_class_refuses(replacement):
    value = copy.deepcopy(AUTHOR); value["judgment.json"]["reconsideration"] = replacement
    with pytest.raises(ValueError):output.project(value, output.contract(PACKET,"continuation"))

@pytest.mark.parametrize("value", [None, {}, {"result": "APPROVE"},
    {"review.json": json.dumps(REVIEW["review.json"])},
    {"review.json": {**REVIEW["review.json"], "extra": "ignored?"}}])
def test_missing_or_untyped_structured_output_refuses(value):
    with pytest.raises(ValueError):output.project(value, output.contract(PACKET,"review"))

@pytest.mark.parametrize("prefix,suffix", [("adverse prose", ""), ("", "REVISE"), ("APPROVE", "APPROVE")])
def test_original247_wrapper_still_refused(prefix,suffix):
    raw = json.dumps({"review.json": json.dumps(REVIEW["review.json"])})
    with pytest.raises(ValueError, match="HOSTED_CAMPAIGN_INVALID_JSON"):
        artifact_files(prefix+"\n```json\n"+raw+"\n```\n"+suffix,["review.json"])

@pytest.mark.parametrize("raw", ['{"a":1,"a":2}', '{"a": NaN}', '{"a": Infinity}'])
def test_nonfinite_and_duplicate_keys_refuse(raw):
    with pytest.raises(ValueError):output.loads(raw)

def test_locked_commands_and_exact_schema_file(tmp_path):
    selected=output.contract(PACKET,"review")
    command=model_command("claude",output_contract=selected)
    assert command[command.index("--max-turns")+1]=="3"
    assert command[command.index("--tools")+1]==""
    assert command[command.index("--permission-mode")+1]=="dontAsk"
    assert json.loads(command[command.index("--json-schema")+1])==selected["schema"]
    path=tmp_path/"schema.json";path.write_bytes(output.encoded(selected["schema"]))
    command=model_command("astra",output_contract=selected,schema_path=path)
    assert command[command.index("--output-schema")+1]==str(path)
    assert command[command.index("-s")+1]=="read-only"
    path.write_bytes(b"{}")
    with pytest.raises(ValueError,match="SCIENTIFIC_OUTPUT_SCHEMA_FILE_REQUIRED"):
        model_command("astra",output_contract=selected,schema_path=path)

def test_schema_consumes_existing_input_bound():
    selected=output.contract(PACKET,"review")
    schema_bytes=output.encoded(selected["schema"])
    measured=measure_input("x", "claude", "review", output_contract=selected)
    assert measured["characters"]==1+len(schema_bytes.decode())
    assert measured["utf8_bytes"]==1+len(schema_bytes)
    with pytest.raises(InputTooLarge):
        measure_input("x"*900000,"claude","review",output_contract=selected)

def events(value=REVIEW):
    return [{"type":"assistant","message":{"content":[{"type":"tool_use","id":"schema-1",
        "name":"StructuredOutput","input":value}]}},
        {"type":"user","message":{"content":[{"type":"tool_result","tool_use_id":"schema-1",
        "content":"Synthetic schema accepted","is_error":False}]}}]

def test_exact_data_tool_accounted_without_altering_originals():
    original=events();before=copy.deepcopy(original)
    view,receipt=output.retrieval_events(original,output.contract(PACKET,"review"),REVIEW)
    assert original==before and receipt["successful_calls"]==1
    assert all(not row["message"]["content"] for row in view)

@pytest.mark.parametrize("case", ["wrong-value","error","unpaired","duplicate","no-contract"])
def test_data_tool_fail_closed(case):
    value=events();selected=output.contract(PACKET,"review")
    if case=="wrong-value":value[0]["message"]["content"][0]["input"]={"review.json":{**REVIEW["review.json"],"verdict":"APPROVE"}}
    if case=="error":value[1]["message"]["content"][0]["is_error"]=True
    if case=="unpaired":value.pop()
    if case=="duplicate":value+=copy.deepcopy(value)
    if case=="no-contract":selected=None
    with pytest.raises(ValueError):output.retrieval_events(value,selected,REVIEW)

def test_unrelated_execution_is_not_filtered():
    value=[{"type":"assistant","message":{"content":[{"type":"tool_use","id":"bad",
        "name":"Bash","input":{"command":"synthetic"}}]}}]
    with pytest.raises(ValueError,match="UNEXPECTED_TOOL_EXECUTION"):
        output.retrieval_events(value,output.contract(PACKET,"review"),REVIEW)

def test_nonartifact_routes_unchanged():
    assert output.contract({"trigger":"operational-acceptance"},"review") is None
    assert "--json-schema" not in model_command("claude")


@pytest.mark.parametrize("family,stage,value", [("astra","continuation",AUTHOR),("claude","review",REVIEW)])
@pytest.mark.parametrize("missing", [False,True])
def test_actual_model_call_structured_receipt_path(tmp_path,monkeypatch,family,stage,value,missing):
    """Execute model_call with synthetic CLI events; forbid any real subprocess."""
    import os
    from types import SimpleNamespace
    from orchestrator import hosted_cycle as cycle, hosted_context as context
    base=tmp_path/"model-work"
    class TestPath(type(Path())):
        def __init__(self,*args,**kwargs):
            if args==('/var/lib/research-system/model-work',):args=(str(base),)
            super().__init__(*args,**kwargs)
        def stat(self,*args,**kwargs):
            info=super().stat(*args,**kwargs)
            if str(self)==str(base):return SimpleNamespace(st_uid=0,st_mode=info.st_mode)
            return info
    monkeypatch.setattr(cycle,'Path',TestPath)
    monkeypatch.setattr(cycle,'checked_source',lambda *args:tmp_path)
    monkeypatch.setattr(cycle.subprocess,'check_output',lambda *args,**kwargs:'a'*40)
    monkeypatch.setattr(cycle.pwd,'getpwnam',lambda name:SimpleNamespace(pw_uid=os.getuid(),pw_gid=os.getgid()))
    monkeypatch.setattr(cycle.os,'chown',lambda *args:None)
    monkeypatch.setattr(cycle.os,'killpg',lambda *args:None)
    folder=tmp_path/'turn';folder.mkdir(mode=0o700)
    raw=cycle.encoded(PACKET);(folder/'packet.json').write_bytes(raw)
    operating={'task_packet':{'name':'packet.json','sha256':cycle.sha(raw)},'task_state':PACKET,'documents':{}}
    monkeypatch.setattr(context,'envelope',lambda *args,**kwargs:('Synthetic decision only',operating))
    monkeypatch.setattr(context,'context_bytes',lambda *args:cycle.encoded(operating))
    if family=='claude':
        final={'type':'result','subtype':'success','is_error':False,'session_id':'synthetic-claude-001',
               'result':'','usage':{'input_tokens':1,'output_tokens':1}}
        if not missing:final['structured_output']=value
        wire=[{'type':'system','subtype':'init','tools':[],'mcp_servers':[],'permissionMode':'dontAsk'},
              {'type':'assistant','message':{'model':cycle.MODELS[family],'content':[]}},final]
    else:
        wire=[{'type':'thread.started','thread_id':'synthetic-codex-001'},
              {'type':'item.completed','item':{'type':'agent_message','text':'prose refuses' if missing else json.dumps(value)}},
              {'type':'turn.completed','usage':{'input_tokens':1,'output_tokens':1}}]
    seen=[]
    class Process:
        pid=999999999;returncode=0
        def __init__(self,args,**kwargs):
            seen.append(args)
            kwargs['stdout'].write(b''.join(output.encoded(e)+b'\n' for e in wire))
        def communicate(self,*args,**kwargs):return None
        def wait(self):return 0
    monkeypatch.setattr(cycle.subprocess,'Popen',Process)
    if missing:
        with pytest.raises(ValueError):cycle.model_call(folder,stage,family,'original',output_format='json')
        assert not (folder/(stage+'.receipt.json')).exists()
        assert (folder/(stage+'.stdout')).exists()
        return
    answer,receipt=cycle.model_call(folder,stage,family,'original',output_format='json')
    assert {n:json.loads(v) for n,v in json.loads(answer).items()}==value
    assert receipt['answer_sha256']==cycle.sha(answer.encode())
    assert receipt['artifact_projection']['provider_output_sha256']==cycle.sha(output.encoded(value))
    assert (folder/(stage+'.provider-output.json')).read_bytes()==output.encoded(value)
    assert receipt['artifact_projection']['original_protocol_preserved'] is True
    assert receipt['stdout_sha256']==cycle.sha((folder/(stage+'.stdout')).read_bytes())
    flag='--json-schema' if family=='claude' else '--output-schema'
    assert flag in seen[0]


@pytest.mark.parametrize("commentary", ["APPROVE", "REVISE: adverse finding", "```json\n{}\n```"])
def test_unclassified_or_adverse_final_commentary_not_discarded(commentary):
    with pytest.raises(ValueError,match="COMMENTARY_REQUIRES_RECONCILIATION"):
        output.claude_value({"structured_output":REVIEW,"result":commentary},output.contract(PACKET,"review"))

def test_duplicate_structured_final_result_allowed():
    assert output.claude_value({"structured_output":REVIEW,"result":json.dumps(REVIEW)},
                              output.contract(PACKET,"review"))==REVIEW


def test_schema_consumes_original019_growth_reserve(monkeypatch):
    from orchestrator import current_scientific_input
    monkeypatch.setattr(current_scientific_input,'is_current',lambda value:True)
    selected=output.contract(PACKET,'review')
    packet={'trigger':'installed-research-request'}
    schema_characters=len(output.encoded(selected['schema']).decode())
    measured=measure_input('x'*800699,'claude','review',task_state=packet,output_contract=selected)
    assert measured['reviewed_growth']['allowance_characters']==60000
    assert measured['reviewed_growth']['remaining_characters']==60000-schema_characters
    with pytest.raises(InputTooLarge,match='HOSTED_REVIEWED_GROWTH_ALLOWANCE_EXCEEDED'):
        measure_input('x'*860699,'claude','review',task_state=packet,output_contract=selected)

def test_retrieval_command_preserves_tools_and32turn_scope():
    from orchestrator.scientific_evidence_runtime import TOOLS
    runtime={'command':'/synthetic/reader','args':['read-only']}
    command=model_command('claude',runtime,output_contract=output.contract(PACKET,'review'))
    assert command[command.index('--max-turns')+1]=='32'
    assert command[command.index('--tools')+1]==''
    allowed=command[command.index('--allowedTools')+1].split(',')
    assert len(allowed)==len(TOOLS) and all(n.startswith('mcp__scientific_evidence__') for n in allowed)
    assert 'StructuredOutput' not in allowed  # no general native tool grant

def test_campaign_artifact_envelope_preserves_literal_bodies():
    packet={'campaign_artifacts':{'version':1,'experiment':'P001','mode':'discuss'}}
    selected=output.contract(packet,'review')
    original={'review.json':'{"verdict":"REVISE","rationale":"Synthetic adverse criticism"}'}
    assert json.loads(output.project(original,selected))==original
    assert output.contract(packet,'disposition') is None
