#!/usr/bin/env python3
"""Source-bound author-operated cross-family review; not independent merge-desk approval."""
import json,subprocess,hashlib,time
from pathlib import Path
import argparse
parser=argparse.ArgumentParser()
parser.add_argument('--scope',required=True)
parser.add_argument('--files',nargs='+',required=True)
parser.add_argument('--private-dir',type=Path,required=True)
args=parser.parse_args()
ROOT=Path.cwd();REVIEW_FILES=args.files
if args.private_dir.resolve().is_relative_to(ROOT):raise ValueError('review evidence must remain private outside checkout')
for name in REVIEW_FILES:
 path=ROOT/name
 if path.is_symlink() or not path.resolve().is_relative_to(ROOT) or path.suffix not in {'.py','.md','.json','.toml','.yml','.fish','.sh','.service','.timer','.socket'}:raise ValueError('unsupported review input')
rev=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
d=args.private_dir;d.mkdir(mode=0o700)
content={f:(ROOT/f).read_text() for f in REVIEW_FILES}
prompt=('Fresh author-operated Fable implementation review, not execution worker or independent merge desk. Scope '+args.scope+' at '+rev+'. Review supplied current source for concrete correctness/privacy/authority bugs. User authorizes existing-subscription reviews. No tools or patient data execution. Source-only review; do not claim tests run. Check persistent artifacts, fail-closed boundaries, identity bindings, recovery semantics, and preservation of scientific approvals. Return concise findings with verdict APPROVE or REQUEST_CHANGES, scope, reviewed_commit. Source:\n'+json.dumps(content))
schema={'type':'object','additionalProperties':False,'properties':{'scope':{'type':'string','const':args.scope},'reviewed_commit':{'type':'string','const':rev},'verdict':{'type':'string','enum':['APPROVE','REQUEST_CHANGES']},'findings':{'type':'array','items':{'type':'string'}}},'required':['scope','reviewed_commit','verdict','findings']}
cmd=['claude','-p','--model','claude-fable-5','--output-format','stream-json','--verbose','--json-schema',json.dumps(schema),'--strict-mcp-config','--mcp-config','{"mcpServers":{}}','--tools','','--permission-mode','dontAsk','--max-turns','5']
start=time.monotonic()
with (d/'protocol.jsonl').open('w') as out,(d/'stderr.log').open('w') as err:r=subprocess.run(cmd,input=prompt,text=True,stdout=out,stderr=err,cwd=d,timeout=600)
events=[json.loads(l) for l in (d/'protocol.jsonl').read_text().splitlines()]
response=[e for e in events if e.get('type')=='result'][-1]
(d/'response.json').write_text(json.dumps(response,indent=2)+'\n')
models=sorted({e.get('message',{}).get('model','unknown') for e in events if e.get('type')=='assistant'})
e={'reviewed_commit':rev,'returncode':r.returncode,'wall_seconds':time.monotonic()-start,'input_file_sha256':{f:hashlib.sha256(v.encode()).hexdigest() for f,v in content.items()},'response_sha256':hashlib.sha256((d/'response.json').read_bytes()).hexdigest(),'requested_model':'claude-fable-5','assistant_message_models':models,'actual_usage_models':list(response.get('modelUsage',{})),'protocol_sha256':hashlib.sha256((d/'protocol.jsonl').read_bytes()).hexdigest()}
(d/'execution.json').write_text(json.dumps(e,indent=2)+'\n')
print(json.dumps({'execution':e,'subtype':response.get('subtype'),'is_error':response.get('is_error'),'review':response.get('structured_output')}))
