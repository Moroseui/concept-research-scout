"""Prepare a future MCP-only command; no connection or execution is started."""
import json
from pathlib import Path
import shlex
import subprocess

ROOT=Path(__file__).resolve().parents[1]


def command(config,settings=None):
    settings=settings or ROOT/'configs/pilot/colab-worker-future.json'
    profile=json.loads(settings.read_text())
    hook=shlex.split(profile['hooks']['PreToolUse'][0]['hooks'][0]['command'])
    if len(hook)!=2 or any(not Path(p).is_file() for p in hook):raise ValueError('hook executable unavailable; do not start worker')
    result=subprocess.run(hook,input=json.dumps({'tool_name':'mcp__colab-worker__get_cells','tool_input':{'includeOutputs':True}}),text=True,capture_output=True,check=True)
    if json.loads(result.stdout).get('hookSpecificOutput',{}).get('permissionDecision')!='deny':raise ValueError('guard preflight failed')
    if not Path(config).is_file():raise ValueError('private MCP configuration unavailable')
    return ['claude','-p','--model','claude-fable-5','--tools','ToolSearch',
        '--allowedTools',','.join(profile['permissions']['allow']),
        '--permission-mode','dontAsk','--settings',str(settings),'--strict-mcp-config','--mcp-config',str(config)]


if __name__=='__main__':
    print(json.dumps(command(Path.home()/'.local/share/isles-colab-mcp/claude-worker.json')))
