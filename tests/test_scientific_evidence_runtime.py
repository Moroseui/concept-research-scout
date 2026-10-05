"""Runner wiring and actual-return comparison, using explicit synthetic CLI events."""
from copy import deepcopy
import json
import os
import tomllib

import pytest
from test_scientific_evidence_access import capture, case
from orchestrator import scientific_evidence_access as evidence
from orchestrator import scientific_evidence_runtime as runtime
from orchestrator.hosted_context import format_prefix


def fixture(capture, tmp_path, role="author"):
    descriptor, reader = capture[-2:]
    journal = tmp_path/"journal"
    session = evidence.Session(reader,journal,role=role,task_binding=descriptor["task_binding"])
    args = {"capture":reader.identity,"cursor":0,"kind":"all"}
    response = session.call("list",args)
    rt = {"descriptor":descriptor,"role":role,"uid":os.getuid(),"journal":str(journal)}
    return rt,args,evidence.tool_text(response)


def astra(args,text):
    return [{"type":"item.completed","item":{"id":"synthetic-call","type":"mcp_tool_call",
             "server":runtime.SERVER,"tool":"scientific_evidence_list","arguments":args,
             "status":"completed","error":None,"result":{"content":[{"type":"text","text":text}]}}}]


def claude(args,text):
    return [{"type":"assistant","message":{"content":[{"type":"tool_use","id":"synthetic-call",
             "name":"mcp__scientific_evidence__scientific_evidence_list","input":args}]}},
            {"type":"user","message":{"content":[{"type":"tool_result","tool_use_id":"synthetic-call",
             "content":[{"type":"text","text":text}]}]}}]


@pytest.mark.parametrize("family,role", [("astra","author"),("claude","reviewer"),("astra","disposition")])
def test_return_matches_original_journal_for_each_role(capture,tmp_path,family,role):
    rt,args,text=fixture(capture,tmp_path,role)
    events=(claude if family=="claude" else astra)(args,text)
    verified=runtime.verify(rt,events,family)
    assert verified["calls"]==1
    assert verified["role"]==role
    assert verified["actual_tool_matches"]==[{"tool_id":"synthetic-call","journal_number":1}]
    assert verified["capture"]==rt["descriptor"]


@pytest.mark.parametrize("failure", ["different-text","different-arguments","missing-return",
                                    "extra-return","changed-journal","wrong-role","pending"])
def test_no_manifest_or_model_claim_can_substitute_for_delivery(capture,tmp_path,failure):
    rt,args,text=fixture(capture,tmp_path)
    events=astra(args,text)
    if failure=="different-text":events[0]["item"]["result"]["content"][0]["text"]+="changed"
    elif failure=="different-arguments":events[0]["item"]["arguments"]={**args,"cursor":1}
    elif failure=="missing-return":events=[]
    elif failure=="extra-return":
        extra=deepcopy(events[0]);extra["item"]["id"]="other";events.append(extra)
    elif failure=="changed-journal":
        path=tmp_path/"journal/call-0001.json";row=json.loads(path.read_bytes())
        row["response"]={"ok":True,"forged":"claim"};path.write_text(json.dumps(row))
    elif failure=="wrong-role":rt["role"]="disposition"
    else:(tmp_path/"journal/pending.json").write_text("{}")
    with pytest.raises(ValueError):runtime.verify(rt,events,"astra")


@pytest.mark.parametrize("family", ["astra","claude"])
def test_no_other_tools_are_accepted(family):
    events=astra({},"{}") if family=="astra" else claude({},"{}")
    if family=="astra":events[0]["item"]["server"]="other"
    else:events[0]["message"]["content"][0]["name"]="Bash"
    with pytest.raises(ValueError):runtime.deliveries(events,family)


def test_exact_stdio_command_and_no_persistent_client_config():
    rt={"command":"/usr/bin/python3","args":["-B","-c","print('synthetic only')"]}
    codex=runtime.client_options(rt,"astra")
    assert codex[0]=="-c"
    parsed=tomllib.loads(codex[1])["mcp_servers"]
    assert set(parsed)=={runtime.SERVER}
    assert parsed[runtime.SERVER]["enabled_tools"]==list(runtime.TOOLS)
    assert parsed[runtime.SERVER]["required"] is True
    opts=runtime.client_options(rt,"claude")
    config=json.loads(opts[opts.index("--mcp-config")+1])
    assert set(config["mcpServers"])=={runtime.SERVER}
    assert config["mcpServers"][runtime.SERVER]["args"]==rt["args"]
    assert "--dangerously-skip-permissions" not in opts
    assert "--max-turns" not in opts  # The enclosing fixed model command, not this MCP adapter, owns the turn bound.


def test_evidence_directive_is_explicit_and_old_path_unchanged():
    original=format_prefix("payload",prepared_prompt=False,output_format="json")
    assert "Do not invoke tools" in original
    enabled=format_prefix("payload",prepared_prompt=False,output_format="json",scientific_evidence=True)
    assert "bound scientific evidence" in enabled and "Do not invoke tools" not in enabled
    assert enabled.endswith("Return one JSON object only. payload")
    assert format_prefix("prepared",prepared_prompt=True,output_format="markdown")=="prepared"

@pytest.mark.parametrize("change", ["task", "stage", "role", "family", "source"])
def test_valid_other_capture_does_not_authorize_this_stage(capture, tmp_path, change):
    descriptor, _ = capture[-2:]
    value = {"descriptor": descriptor, "directory": str(tmp_path), "role": "author"}
    kwargs = {"source": descriptor["source"], "packet_sha256": descriptor["task_binding"],
              "stage": "continuation", "family": "astra"}
    assert runtime.stage_profile(value, **kwargs) == descriptor
    if change == "task": kwargs["packet_sha256"] = "f" * 64
    elif change == "stage": kwargs["stage"] = "disposition"
    elif change == "role": value["role"] = "disposition"
    elif change == "family": kwargs["family"] = "claude"
    else: kwargs["source"] = "f" * 40
    with pytest.raises(ValueError): runtime.stage_profile(value, **kwargs)

def test_protected_capture_uses_configured_store_and_preserves_immutable_task(capture, tmp_path, monkeypatch):
    from types import SimpleNamespace
    from orchestrator import protected_scientific_jobs
    descriptor, _ = capture[-2:]
    source = descriptor["source"]
    broker = SimpleNamespace(config={"controller_uid": 99, "sources": [source]})
    config = {"source": source, "source_root": str(tmp_path),
              "change_request_store": "/protected/native/store", "controller_uid": 99}
    monkeypatch.setattr(protected_scientific_jobs, "controller_configuration", lambda value: config)
    packet = {"scientific_change_history": {"native": "synthetic fixture"}}
    seen = []
    monkeypatch.setattr(evidence, "capture_task_changes",
        lambda store, original, **kw: seen.append((store, original, kw)) or {"capture": "synthetic"})
    monkeypatch.setattr(evidence, "write_capture", lambda directory, value: descriptor)
    # This fixture deliberately stubs native capture; exercise the new guard's
    # owner propagation here. Real chain/prefix checks have their own tests.
    checked = []
    monkeypatch.setattr("orchestrator.scientific_runtime_prerequisites.verify",
        lambda cfg, pkt, src, cap, **kw: checked.append((cfg, pkt, src, cap, kw)))
    out = runtime.broker_capture(broker, packet, source=source, folder=tmp_path, stage="review")
    assert checked == [(config, packet, source, {"capture": "synthetic"}, {"owner": 99})]
    assert seen == [("/protected/native/store", packet, {"source": source, "owner": 99})]
    assert out["role"] == "reviewer"
    assert out["directory"] == str(tmp_path/"scientific-evidence-capture")
    config["source"] = "f"*40
    with pytest.raises(ValueError, match="CONTROLLER_SOURCE_CHANGED"):
        runtime.broker_capture(broker, packet, source=source, folder=tmp_path, stage="review")
    assert len(seen) == 1
    assert runtime.broker_capture(broker, {}, source=source, folder=tmp_path, stage="review") is None


@pytest.mark.parametrize("family", ["astra", "claude"])
def test_protocol_error_never_counts_as_delivered_original(capture, tmp_path, family):
    rt,args,text=fixture(capture,tmp_path,"reviewer" if family=="claude" else "author")
    events=(claude if family=="claude" else astra)(args,text)
    if family=="claude": events[-1]["message"]["content"][0]["is_error"]=True
    else: events[0]["item"]["result"]["isError"]=True
    with pytest.raises(ValueError): runtime.verify(rt,events,family)

@pytest.mark.parametrize("family,role", [("astra","author"), ("claude","reviewer")])
def test_genuine_refusal_is_preserved_without_claiming_original_read(capture,tmp_path,family,role):
    descriptor, reader = capture[-2:]
    journal = tmp_path/"journal"
    session = evidence.Session(reader,journal,role=role,task_binding=descriptor["task_binding"])
    args = {"capture":reader.identity,"cursor":-1,"kind":"all"}
    response = session.call("list",args)
    assert response["ok"] is False
    text = evidence.tool_text(response)
    rt = {"descriptor":descriptor,"role":role,"uid":os.getuid(),"journal":str(journal)}
    events = (claude if family=="claude" else astra)(args,text)
    if family=="claude": events[-1]["message"]["content"][0]["is_error"]=True
    else: events[0]["item"]["status"]="failed"
    assert runtime.verify(rt,events,family)["calls"] == 1
    if family=="claude": events[-1]["message"]["content"][0]["is_error"]=False
    else: events[0]["item"]["status"]="completed"
    with pytest.raises(ValueError): runtime.verify(rt,events,family)


def test_new_or_collaboration_tools_cannot_escape_scientific_allowlist():
    for kind in ("collab_tool_call", "future_tool"):
        with pytest.raises(ValueError):
            runtime.deliveries([{"type":"item.completed","item":{"type":kind}}],"astra")


def test_descriptor_preview_matches_actual_immutable_write(capture,tmp_path):
    store,folder,request,cache,descriptor,reader=capture
    native=evidence.capture_changes(store,[request['identity']],source=descriptor['source'],
                                    task_binding=descriptor['task_binding'])
    before=set(tmp_path.iterdir())
    expected=evidence.describe_capture(native)
    assert set(tmp_path.iterdir())==before  # preview claims no filesystem retrieval
    assert expected==evidence.write_capture(tmp_path/'same-originals',native)==descriptor


@pytest.mark.parametrize('marker',[
    'SCIENTIFIC_ROLE_INPUT_VERSION = True',
    'SCIENTIFIC_ROLE_INPUT_VERSION = 2',
    'SCIENTIFIC_ROLE_INPUT_VERSION = 1\nSCIENTIFIC_ROLE_INPUT_VERSION = 1',
    'if True:\n    SCIENTIFIC_ROLE_INPUT_VERSION = 1',
])
def test_profile_marker_must_be_unique_literal_in_exact_source(tmp_path,monkeypatch,marker):
    (tmp_path/'orchestrator').mkdir()
    (tmp_path/'orchestrator/scientific_evidence_runtime.py').write_text(marker+'\n')
    monkeypatch.setattr('orchestrator.remote_supervisor.checked_source',lambda root,source:root)
    with pytest.raises(ValueError,match='SOURCE_PROFILE_CHANGED'):runtime.enabled(tmp_path,'a'*40)


@pytest.mark.parametrize('config',[None,{}, {'source':'f'*40}])
def test_profiled_controller_requires_exact_configuration_before_original_read(tmp_path,monkeypatch,config):
    monkeypatch.setattr(runtime,'enabled',lambda *args:True)
    def forbidden(*args,**kwargs):raise AssertionError('no native read before configuration validation')
    monkeypatch.setattr(evidence,'capture_task_changes',forbidden)
    with pytest.raises(ValueError,match='CONTROLLER_CONFIG_REQUIRED'):
        runtime.controller_options(config,tmp_path,'a'*40,{'scientific_change_history':{}},'review')


def test_legacy_controller_options_never_require_new_store_or_source(tmp_path,monkeypatch):
    assert runtime.controller_options(None,None,None,{},'review')=={}
    monkeypatch.setattr(runtime,'enabled',lambda *args:False)
    assert runtime.controller_options(None,tmp_path,'a'*40,{'scientific_change_history':{}},'review')=={}


@pytest.mark.parametrize('user',['research-driver','research-reviewer'])
def test_scientific_cache_is_separate_per_stage_without_moving_credentials(tmp_path,user):
    from orchestrator.hosted_cycle import scientific_worker_command
    command=['claude','-p','--permission-mode','dontAsk']
    one=scientific_worker_command(user,tmp_path/'first',command)
    two=scientific_worker_command(user,tmp_path/'second',command)
    assert one[:6]==['runuser','-u',user,'--','env','-i']
    assert 'HOME=/home/'+user in one and 'HOME=/home/'+user in two
    assert 'XDG_CACHE_HOME='+str(tmp_path/'first/client-cache') in one
    assert 'XDG_CACHE_HOME='+str(tmp_path/'second/client-cache') in two
    assert one[-len(command):]==two[-len(command):]==command
    assert not any('TOKEN=' in v or 'KEY=' in v or 'XDG_CONFIG_HOME=' in v for v in one)
    assert not list(tmp_path.iterdir())  # Command composition neither reads auth nor writes state.
