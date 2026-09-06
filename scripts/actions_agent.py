"""Tool-free structured-output transport for the existing run_agent primitive."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time


def schema(names):
    return {'type':'object','additionalProperties':False,'properties':{
        name:{'type':'string'} for name in names},'required':names}


def decode(response,names):
    if not isinstance(response,dict) or set(response)!=set(names):raise ValueError('OUTPUT_SCHEMA_MISMATCH')
    for k,v in response.items():
        if Path(k).name!=k or not isinstance(v,str) or not v.strip() or len(v.encode())>100000:
            raise ValueError('OUTPUT_CONTENT_INVALID')
    return response


def run(family,names,prompt):
    if family not in ('codex','claude') or not names:raise ValueError('FAMILY_OR_OUTPUT_INVALID')
    private=Path(tempfile.mkdtemp(prefix='hosted-agent-private-'));private.chmod(0o700)
    spec=schema(names);(private/'schema.json').write_text(json.dumps(spec))
    env={k:v for k,v in os.environ.items() if k not in ['GH_TOKEN','GITHUB_TOKEN','ACTIONS_RUNTIME_TOKEN','ANTHROPIC_API_KEY']}
    prompt='Return only JSON matching the supplied schema. File contents go in the matching string fields; the system writes the files. Do not use tools, read files, execute code, or access external services. Work only from the supplied evidence.\n'+prompt
    if family=='claude':
        env.pop('OPENAI_API_KEY',None)
        command=['claude','-p','--model','claude-fable-5','--output-format','json','--json-schema',json.dumps(spec),'--strict-mcp-config','--mcp-config','{"mcpServers":{}}','--tools','','--permission-mode','dontAsk','--max-turns','3']
    else:
        env.pop('CLAUDE_CODE_OAUTH_TOKEN',None)
        command=['codex','exec','--ignore-user-config','--ephemeral','--sandbox','read-only','--disable','shell_tool','--disable','unified_exec','-c','web_search="disabled"','-c','approval_policy="never"','--skip-git-repo-check','--json','--output-schema',str(private/'schema.json'),'--output-last-message',str(private/'answer.json'),'-']
    started=time.monotonic()
    result=subprocess.run(command,input=prompt,text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,cwd=private,env=env,timeout=600)
    (private/'stdout.log').write_text(result.stdout);(private/'stderr.log').write_text(result.stderr)
    if result.returncode:
        low=(result.stderr+result.stdout).lower()
        code='CODEX_ACCOUNT_UNFUNDED' if any(x in low for x in ['insufficient_quota','no credits','billing_hard_limit']) else 'MODEL_CREDENTIAL_REJECTED' if any(x in low for x in ['401','unauthorized','authentication']) else 'MODEL_EXECUTION_FAILED'
        raise ValueError(code)
    if family=='claude':
        response=json.loads(result.stdout)
        if response.get('subtype')!='success' or response.get('is_error'):raise ValueError('MODEL_RESPONSE_FAILED')
        answer=response.get('structured_output');usage=response.get('modelUsage',{})
    else:
        answer=json.loads((private/'answer.json').read_text())
        events=[json.loads(x) for x in result.stdout.splitlines() if x.strip()]
        if any(e.get('item',{}).get('type') in ['command_execution','mcp_tool_call','web_search','file_change'] for e in events):raise ValueError('UNEXPECTED_MODEL_TOOL_USE')
        usage=[e.get('usage') for e in events if e.get('type')=='turn.completed']
    decoded=decode(answer,names)
    for name,value in decoded.items():Path(name).write_text(value)
    receipt={'family':family,'ci':True,'duration_s':time.monotonic()-started,'usage':usage,'private_protocol_sha256':hashlib.sha256(result.stdout.encode()).hexdigest()}
    Path('transport.json').write_text(json.dumps(receipt,indent=2))
    print(json.dumps({'status':'COMPLETE','family':family,'ci':True}))


if __name__=='__main__':
    try:run(sys.argv[1],json.loads(sys.argv[2]),sys.stdin.read())
    except Exception as e:
        print(type(e).__name__+': '+str(e),file=sys.stderr);raise SystemExit(1)
