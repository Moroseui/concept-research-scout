#!/usr/bin/env python3
"""Source-bound author-operated cross-family review; not independent merge-desk approval."""
import json,subprocess,hashlib,time,os,sys
from pathlib import Path
import argparse
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from orchestrator import review_input_codec as presentation
parser=argparse.ArgumentParser()
parser.add_argument('--scope',required=True)
parser.add_argument('--files',nargs='+')
parser.add_argument('--file-manifest',type=Path)
parser.add_argument('--private-dir',type=Path,required=True)
parser.add_argument('--expected-source')
parser.add_argument('--shared-context',action='store_true')
parser.add_argument('--policy-baseline',type=Path,help='Saved independently approved policy proof for fresh review.')
parser.add_argument('--approved-policy-source',help='Expected source identity of the selected approved policy baseline.')
parser.add_argument('--change-store',type=Path,action='append',default=[])
parser.add_argument('--change-bindings',type=Path,help='Exact prepared deployment proposal sidecar; selects original APPLIED events.')
parser.add_argument('--private-evidence',type=Path,action='append',default=[])
parser.add_argument('--claude-bin',default='claude')
parser.add_argument('--prepare-only',action='store_true')
parser.add_argument('--run-prepared',action='store_true')
parser.add_argument('--request-sha256')
args=parser.parse_args()
os.umask(0o077)
ROOT=Path.cwd();manifest=json.loads(args.file_manifest.read_bytes()) if args.file_manifest else None
REVIEW_FILES=args.files or list(manifest or {})
if not REVIEW_FILES or len(REVIEW_FILES)!=len(set(REVIEW_FILES)):raise ValueError('exact nonempty review file list required')
if args.private_dir.resolve().is_relative_to(ROOT):raise ValueError('review evidence must remain private outside checkout')
SERVICE_TEMPLATES = {
 'deploy/research-system/research-system-scientific-job@.service.in',
 'deploy/research-system/research-system-issue-intake.service.in',
}
for name in REVIEW_FILES:
 path=ROOT/name
 if path.is_symlink() or not path.resolve().is_relative_to(ROOT) or (path.suffix not in {'.py','.md','.json','.toml','.yml','.fish','.sh','.service','.timer','.socket','.txt','.lock'} and name not in SERVICE_TEMPLATES):raise ValueError('unsupported review input')
rev=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
if args.expected_source and rev!=args.expected_source:raise ValueError('review source moved')
if subprocess.check_output(['git','status','--porcelain'],cwd=ROOT):raise ValueError('clean reviewed source required')
d=args.private_dir
content={f:(ROOT/f).read_text() for f in REVIEW_FILES}
hashes={f:hashlib.sha256(v.encode()).hexdigest() for f,v in content.items()}
if manifest is not None and manifest!=hashes:raise ValueError('review input manifest changed')
for name,value in content.items():
 if subprocess.check_output(['git','show',rev+':'+name],cwd=ROOT)!=value.encode():raise ValueError('review input differs from source')
def digest(raw):return hashlib.sha256(raw).hexdigest()
SUPPLEMENTAL_MAXIMUM=2000000
PREPARED_REQUEST_MAXIMUM=4000000  # Complete request limit in the installed deployment review gate.
def write(path,value,*,maximum=None):
 raw=value if isinstance(value,bytes) else (json.dumps(value,indent=2)+'\n').encode()
 if maximum is not None and len(raw)>maximum:raise ValueError('bounded complete prepared request required')
 with path.open('xb') as stream:stream.write(raw);stream.flush();os.fsync(stream.fileno())
 path.chmod(0o600)
def private_read(path,*,maximum=SUPPLEMENTAL_MAXIMUM):
 path=path.absolute()
 if any(p.is_symlink() for p in (path,*path.parents)) or not path.is_file() or path.stat().st_size>maximum:raise ValueError('bounded regular prepared request required' if maximum==PREPARED_REQUEST_MAXIMUM else 'bounded regular supplemental evidence required')
 return path.read_bytes()
prompt=''
schema={'type':'object','additionalProperties':False,'properties':{'scope':{'type':'string','const':args.scope},'reviewed_commit':{'type':'string','const':rev},'verdict':{'type':'string','enum':['APPROVE','REQUEST_CHANGES']},'findings':{'type':'array','items':{'type':'string'}}},'required':['scope','reviewed_commit','verdict','findings']}
cmd=[args.claude_bin,'-p','--model','claude-fable-5','--output-format','stream-json','--verbose','--json-schema',json.dumps(schema),'--strict-mcp-config','--mcp-config','{"mcpServers":{}}','--tools','','--setting-sources','','--disable-slash-commands','--no-chrome','--permission-mode','dontAsk','--max-turns','5']
if args.prepare_only and args.run_prepared:raise ValueError('choose preparation or execution')
if args.run_prepared:
 raw=private_read(d/'request.json',maximum=PREPARED_REQUEST_MAXIMUM)
 if not args.request_sha256 or digest(raw)!=args.request_sha256:raise ValueError('exact prepared request required')
 prepared=presentation.parsed(raw)
 if any(prepared.get(k)!=v for k,v in {'reviewed_commit':rev,'scope':args.scope,'input_file_sha256':hashes,'command':cmd,'runner_sha256':digest(Path(__file__).read_bytes())}.items()):raise ValueError('prepared review binding changed')
 prompt=prepared['prompt'];schema=prepared['schema']
 if prepared.get('input_presentation')!=presentation.FORMAT_V2:raise ValueError('fresh execution requires an approved V2 policy baseline; historical receipts remain readable')
 from orchestrator.inspection_bootstrap import read_policy_baseline,validate_policy_baseline
 baseline=validate_policy_baseline(read_policy_baseline(d/'policy-baseline'))
 if (prepared.get('policy_baseline')!=baseline['descriptor']
  or prepared.get('shared_context_sha256')!=digest(baseline['context_raw'])
  or private_read(d/'context_implementation_review.json')!=baseline['context_raw']):raise ValueError('approved prepared policy baseline changed')
 if args.approved_policy_source and args.approved_policy_source!=baseline['source']:raise ValueError('approved policy source changed')
 decoded_sources,decoded_supplements,decoded_changes=presentation.decode_presentation(
  prompt,args.scope,rev,prepared.get('shared_context_sha256'),input_presentation=presentation.FORMAT_V2,
  expected_baseline=baseline['descriptor'])
 if (decoded_sources!=content or {k:v['sha256'] for k,v in decoded_supplements.items()}!=prepared.get('private_evidence_sha256')
  or digest(json.dumps(decoded_changes,sort_keys=True).encode())!=prepared.get('change_context_sha256')):raise ValueError('prepared review presentation changed')
 if (d/'intent.json').exists():raise ValueError('original review intent exists; reconcile without retry')
else:
 if not args.shared_context or not args.policy_baseline or not args.approved_policy_source:
  raise ValueError('fresh review requires --shared-context, --policy-baseline and --approved-policy-source; prepare the saved proof with orchestrator.inspection_bootstrap')
 from orchestrator.inspection_bootstrap import read_policy_baseline,validate_policy_baseline
 from orchestrator.inspection_source import write_once
 baseline_originals=read_policy_baseline(args.policy_baseline)
 baseline=validate_policy_baseline(baseline_originals)
 if baseline['source']!=args.approved_policy_source:raise ValueError('approved policy source changed')
 d.mkdir(mode=0o700)
 for name,value in baseline_originals.items():write_once(d/'policy-baseline'/name,value)
 write(d/'context_implementation_review.json',baseline['context_raw'])
 supplemental={str(p):{'sha256':digest(private_read(p)),'content':private_read(p).decode()} for p in args.private_evidence}
 changes=[]
 if args.shared_context:
  sys.path.insert(0,str(ROOT))
  from orchestrator.change_requests import context as change_context, review_context, review_bindings
  stores=list(dict.fromkeys(p.absolute() for p in args.change_store))
  selected_store=None;selection=None
  if args.change_bindings:
   selection_path=args.change_bindings.absolute();selection_raw=private_read(selection_path)
   selection=json.loads(selection_raw)
   proposal_path=selection_path.parent/'proposal.json';proposal_raw=private_read(proposal_path)
   proposal=json.loads(proposal_raw)
   if (proposal.get('source')!=rev or selection!=review_bindings(rev,digest(proposal_raw),proposal.get('changes'))):
    raise ValueError('exact prepared change selections required')
   selected_store=selection_path.parent/'change-inputs'
   if selected_store not in stores:stores.append(selected_store)
   for p,raw in ((selection_path,selection_raw),(proposal_path,proposal_raw)):
    supplemental[str(p)]={'sha256':digest(raw),'content':raw.decode()}
  changes=[{'store':str(p),'projection':review_context(p,selection['changes'],source=rev) if p==selected_store else change_context(p)} for p in stores]
 elif args.change_store or args.change_bindings:raise ValueError('shared context required for change stores')
 prompt=presentation.encode_v2(args.scope,rev,content,supplemental,changes,
     baseline['context_raw'],baseline['descriptor'])
 write(d/'request.json',{'input_presentation':presentation.FORMAT_V2,'policy_baseline':baseline['descriptor'],'scope':args.scope,'reviewed_commit':rev,'prompt':prompt,'schema':schema,
     'input_file_sha256':hashes,'private_evidence_sha256':{k:v['sha256'] for k,v in supplemental.items()},
     'change_context_sha256':digest(json.dumps(changes,sort_keys=True).encode()),
      'change_bindings_sha256':digest(selection_raw) if args.change_bindings else None,
     'shared_context_sha256':digest((d/'context_implementation_review.json').read_bytes()) if args.shared_context else None,
     'command':cmd,'runner_sha256':digest(Path(__file__).read_bytes()),'independent_merge_desk_review':False},maximum=PREPARED_REQUEST_MAXIMUM)
 if args.prepare_only:
  print(json.dumps({'status':'PREPARED_NO_MODEL_CALL','request_sha256':digest((d/'request.json').read_bytes()),'reviewed_commit':rev,'source_files':len(hashes),'approved_policy_source':baseline['source'],'policy_proof_sha256':baseline['descriptor']['proof_sha256']}));raise SystemExit(0)
if args.request_sha256 and not args.run_prepared:raise ValueError('request digest applies to prepared execution only')
environment=os.environ.copy()
if Path(args.claude_bin).is_absolute():environment['PATH']=str(Path(args.claude_bin).parent)+':'+environment.get('PATH','')
for name in ('ANTHROPIC_API_KEY','OPENAI_API_KEY','SCOUT_CI'):environment.pop(name,None)
write(d/'intent.json',{'reviewed_commit':rev,'request_sha256':digest((d/'request.json').read_bytes()),'maximum_invocations':1,'automatic_retry':False})
start=time.monotonic()
with (d/'protocol.jsonl').open('xb') as out,(d/'stderr.log').open('xb') as err:
 r=subprocess.Popen(cmd,stdin=subprocess.PIPE,stdout=out,stderr=err,cwd=d,env=environment,start_new_session=True)
 write(d/'process.json',{'pid':r.pid,'proc_stat':Path('/proc/'+str(r.pid)+'/stat').read_text()})
 try:r.communicate(prompt.encode(),timeout=600)
 except subprocess.TimeoutExpired:
  write(d/'timeout.json',{'status':'RECONCILE_ORIGINAL_PROCESS','pid':r.pid,'process_not_killed':True});raise SystemExit(2)
write(d/'returned.json',{'returncode':r.returncode,'wall_seconds':time.monotonic()-start})
events=[json.loads(l) for l in (d/'protocol.jsonl').read_text().splitlines()]
results=[e for e in events if e.get('type')=='result']
response=results[0] if len(results)==1 else {}
write(d/'response.json',response)
models=sorted({e.get('message',{}).get('model','unknown') for e in events if e.get('type')=='assistant'})
e={'policy_baseline':baseline['descriptor'],'reviewed_commit':rev,'returncode':r.returncode,'wall_seconds':time.monotonic()-start,'input_file_sha256':hashes,'response_sha256':digest((d/'response.json').read_bytes()),'requested_model':'claude-fable-5','assistant_message_models':models,'actual_usage_models':list(response.get('modelUsage',{})),'protocol_sha256':digest((d/'protocol.jsonl').read_bytes()),'request_sha256':digest((d/'request.json').read_bytes()),'prompt_sha256':digest(prompt.encode()),'independent_merge_desk_review':False}
write(d/'execution.json',e)
review=response.get('structured_output');init=[e for e in events if e.get('type')=='system' and e.get('subtype')=='init']
if (r.returncode!=0 or len(results)!=1 or response.get('subtype')!='success' or response.get('is_error')
 or models!=['claude-fable-5'] or len(init)!=1 or init[0].get('tools')!=['StructuredOutput'] or init[0].get('mcp_servers')!=[]
 or init[0].get('permissionMode')!='dontAsk' or not isinstance(review,dict) or set(review)!=set(schema['required'])
 or review.get('scope')!=args.scope or review.get('reviewed_commit')!=rev or review.get('verdict') not in ('APPROVE','REQUEST_CHANGES')
 or not isinstance(review.get('findings'),list) or any(not isinstance(v,str) for v in review['findings'])):
 raise ValueError('review incomplete or identity/schema mismatch; originals preserved, no verdict accepted')
print(json.dumps({'execution':e,'subtype':response.get('subtype'),'is_error':response.get('is_error'),'review':review}))
