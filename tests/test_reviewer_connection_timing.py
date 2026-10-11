from types import SimpleNamespace
import pytest
from tools import reviewer_connection_timing as timing

def test_fixed_option_preserves_original_command_and_is_reversible():
    calls=[]
    def original(*args,**kwargs):
        calls.append((args,kwargs));return ['/tools/node','/tools/claude/cli.js']
    runtime=SimpleNamespace(claude_command=original)
    restore=timing.bind(runtime)
    assert runtime.claude_command(node='/tools/node',mounted=True)==['/tools/node',timing.FLAG,'/tools/claude/cli.js']
    assert calls==[((),{'node':'/tools/node','mounted':True})]
    timing.bind(runtime)() # already bound: do not duplicate the option
    assert runtime.claude_command(node='/tools/node',mounted=True).count(timing.FLAG)==1
    assert runtime.claude_command()==['/tools/node','/tools/claude/cli.js']
    restore();assert runtime.claude_command is original

@pytest.mark.parametrize('argv',[
    ['/tools/node','--inspect','/tools/claude/cli.js'],
    ['/other/node','/tools/claude/cli.js'],
    ['/tools/node','/tools/claude/../other.js'],
    ['/tools/node','/tools/other/cli.js'],
    ['/tools/node','/tools/claude/native'],
    ['/tools/node',None],None,
])
def test_unexpected_commands_fail_closed(argv):
    with pytest.raises(ValueError,match='COMMAND_SHAPE'):timing.command(argv)

def test_original_runtime_refusal_is_preserved():
    def refuse(**kwargs):raise ValueError('original package identity refusal')
    runtime=SimpleNamespace(claude_command=refuse);timing.bind(runtime)
    with pytest.raises(ValueError,match='original package identity refusal'):
        runtime.claude_command(node='/tools/node',mounted=True)

def test_administrative_permissions_and_submission_are_unchanged(monkeypatch):
    from orchestrator import autonomy_review as review,manual_runtime
    monkeypatch.setattr(manual_runtime,'claude_command',lambda **kw:['/tools/node','/tools/claude/cli.js'])
    config={'mcpServers':{'review':{'command':'unchanged'}}}
    before=review.claude_argv(config);restore=timing.bind(manual_runtime)
    try:after=review.claude_argv(config)
    finally:restore()
    assert after==[before[0],timing.FLAG,*before[1:]]
    for key in ['--model','--permission-mode','--tools','--allowedTools','--disallowedTools','--strict-mcp-config','--mcp-config','--setting-sources','--max-turns','--output-format']:
        assert before[before.index(key)+1]==after[after.index(key)+1]


@pytest.mark.parametrize('damage',[None,'wrong-change','wrong-round','bootstrap-bytes','transport-bytes'])
def test_bounded_bootstrap_rejects_unbound_source(tmp_path,monkeypatch,damage):
    from tools import invoke_admin_transport_once as bootstrap
    from orchestrator import autonomy_review as review
    from pathlib import Path
    script=tmp_path/'invoke_admin_transport_once.py';script.write_bytes(b'bound bootstrap fixture')
    helper=tmp_path/'reviewer_connection_timing.py';helper.write_bytes(Path(timing.__file__).read_bytes())
    manifest={'change_id':'colab-timing-transport-repair-20261011','round':1,
        'source_files':{'tools/invoke_admin_transport_once.py':bootstrap.sha(script.read_bytes()),
                        'tools/reviewer_connection_timing.py':bootstrap.sha(helper.read_bytes())}}
    monkeypatch.setattr(bootstrap,'__file__',str(script));monkeypatch.setattr(bootstrap,'trusted',Path)
    monkeypatch.setattr(review,'verify_packet',lambda packet:manifest)
    if damage=='wrong-change':manifest['change_id']='unrelated-review'
    elif damage=='wrong-round':manifest['round']=2
    elif damage=='bootstrap-bytes':script.write_bytes(b'changed')
    elif damage=='transport-bytes':helper.write_bytes(b'changed')
    if damage is None:
        loaded=bootstrap.transport_for_packet(tmp_path)
        assert loaded.command(['/tools/node','/tools/claude/cli.js'])==['/tools/node',timing.FLAG,'/tools/claude/cli.js']
    else:
        with pytest.raises(ValueError):bootstrap.transport_for_packet(tmp_path)
