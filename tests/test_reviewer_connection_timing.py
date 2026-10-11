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


@pytest.mark.parametrize('args,kwargs',[
    ((None,'/tools/node',True),{}),
    ((None,'/tools/node'),{'mounted':True}),
    ((None,),{'node':'/tools/node','mounted':True}),
])
def test_scientific_positional_route_gets_same_fixed_transport(args,kwargs):
    calls=[]
    def original(folder=None,node=None,mounted=False):
        calls.append((folder,node,mounted));return ['/tools/node','/tools/claude/cli.js']
    runtime=SimpleNamespace(claude_command=original);restore=timing.bind(runtime)
    assert runtime.claude_command(*args,**kwargs)==['/tools/node',timing.FLAG,'/tools/claude/cli.js']
    assert calls==[(None,'/tools/node',True)]
    with pytest.raises(TypeError):runtime.claude_command(None,'/tools/node',True,mounted=True)
    assert len(calls)==1
    restore();assert runtime.claude_command is original


def test_unmounted_positional_command_is_unchanged():
    def original(folder=None,node=None,mounted=False):return [node,'/host/cli.js']
    runtime=SimpleNamespace(claude_command=original);timing.bind(runtime)
    assert runtime.claude_command(None,'/tools/node',False)==['/tools/node','/host/cli.js']


@pytest.mark.parametrize('damage',[None,'scope','round','invoker','source','report','approval-scope','helper'])
def test_successor_admin_uses_approved_installed_helper_only(tmp_path,monkeypatch,damage):
    from tools import invoke_admin_installed_transport as b
    from orchestrator import autonomy_review as ar
    from pathlib import Path
    script=tmp_path/'invoke.py';script.write_bytes(b'fixed invocation')
    helper=tmp_path/'helper.py'
    original=(Path(__file__).parent/'fixtures/reviewer_connection_timing_approved.py').read_bytes()
    helper.write_bytes(original)
    manifest={'change_id':'colab-workspace-native-inspection-recovery-20261011','round':1,
              'source_files':{'tools/invoke_admin_installed_transport.py':b.sha(script.read_bytes())}}
    approved={'change_id':'colab-timing-transport-repair-20261011','source_sha':'4a05c64af90af15078e43e31abc9bd13d063160e',
              'report_sha256':'c64df8e27dc86e96a15a4630b0aec5812ec44ddb32124a09dfda0909d7c584ca'}
    monkeypatch.setattr(b,'__file__',str(script));monkeypatch.setattr(ar,'verify_packet',lambda packet:manifest)
    monkeypatch.setattr(b,'trusted',lambda path:helper if Path(path).name=='reviewer_connection_timing.py' else Path(path))
    transport=object();seen=[]
    def load(name,path):
        seen.append(path)
        return SimpleNamespace(authority=lambda:approved) if path.name=='colab_intake_identity_runtime.py' else transport
    monkeypatch.setattr(b,'load',load)
    if damage=='scope':manifest['change_id']='other'
    elif damage=='round':manifest['round']=2
    elif damage=='invoker':script.write_bytes(b'changed')
    elif damage in {'source','report','approval-scope'}:approved[{'source':'source_sha','report':'report_sha256','approval-scope':'change_id'}[damage]]='wrong'
    elif damage=='helper':helper.write_bytes(b'candidate instead of approved')
    if damage is None:
        assert b.transport_for_packet(tmp_path) is transport
        assert all(str(p).startswith('/opt/research-system/manual-repair-helpers/colab-intake-source-alignment-20261011/') for p in seen)
    else:
        with pytest.raises(ValueError):b.transport_for_packet(tmp_path)
