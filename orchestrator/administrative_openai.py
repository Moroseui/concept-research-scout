"""Administrative OpenAI command and native qualification; no scientific route.

Requested model is never presented as observed. The pinned native client,
provider configuration, one thread/turn and accepted MCP submission establish
route identity only; independent approval must judge that equivalence.
"""
import json
from orchestrator import review_contract as contract,review_submission as rs
ALLOWED=('evidence_read','evidence_search','evidence_glob','submit_review')
MODEL='gpt-6-astra'

def require(ok,why):
 if not ok:raise ValueError('OPENAI_ADMIN_'+why)

def command(search_pin,pins):
 args=['/tools/node','/tools/codex/bin/codex.js','exec','--ignore-user-config','--ignore-rules',
       '-m',MODEL,'-s','read-only','--skip-git-repo-check','--json']
 options={'approval_policy':'never','model_provider':'openai','features.shell_tool':False,
          'web_search':'disabled','mcp_servers.evidence.command':'/usr/bin/python3',
          'mcp_servers.evidence.args':['-I','-B','/workspace/.scientific-search.py',search_pin,
             pins['config_sha256'],pins['module_sha256'],pins['contract_sha256']],
          'mcp_servers.evidence.enabled_tools':list(ALLOWED)}
 for k,v in options.items():args+=['-c',k+'='+json.dumps(v,separators=(',',':'))]
 return args+['-']

def events(console):
 values=[contract.strict_json(line) for line in console.splitlines() if line.strip()]
 require(values and all(isinstance(x,dict) for x in values),'NATIVE_OBJECT_EVENTS')
 return values

def final_prose(values):
 messages=[e['item'] for e in values if e.get('type')=='item.completed' and isinstance(e.get('item'),dict) and e['item'].get('type')=='agent_message']
 require(messages and isinstance(messages[-1].get('text'),str),'NATIVE_FINAL_PROSE')
 return messages[-1]['text']

def extract(console,manifest,exit_code,submission_raw,inspection_binding):
 require(exit_code==0,'TERMINAL_SUCCESS_REQUIRED')
 require(isinstance(inspection_binding,dict) and inspection_binding.get('packet_sha256')==rs.sha(rs.canonical(manifest)) and isinstance(inspection_binding.get('files'),dict),'FROZEN_INSPECTION_BINDING')
 values=events(console)
 allowed_events={'thread.started','turn.started','turn.completed','item.started','item.updated','item.completed'}
 require(all(e.get('type') in allowed_events for e in values),'UNKNOWN_OR_FAILED_EVENT')
 threads=[e for e in values if e['type']=='thread.started'];starts=[e for e in values if e['type']=='turn.started'];ends=[e for e in values if e['type']=='turn.completed']
 require(len(threads)==len(starts)==len(ends)==1 and values[0]==threads[0] and values[-1]==ends[0]
         and values.index(starts[0])==1,'ONE_THREAD_ONE_TURN')
 session=threads[0].get('thread_id');require(isinstance(session,str) and session,'THREAD_ID')
 require(all(e.get('thread_id',session)==session for e in values),'MIXED_THREAD')
 usage=ends[0].get('usage')
 require(isinstance(usage,dict) and all(type(usage.get(k)) is int and usage[k]>=0 for k in ('input_tokens','cached_input_tokens','output_tokens')),'NATIVE_USAGE')
 completed=[];ids=set();reads=[];accepted=[];all_tools=[]
 config={'schema':'review-submission/v1','kind':'administrative','bindings':rs.administrative_bindings(manifest)}
 pin=rs.sha(rs.canonical(config));decision=rs.verify_record(submission_raw,config,pin)
 record=contract.strict_json(submission_raw)
 for event in values:
  if not event['type'].startswith('item.'):continue
  item=event.get('item');require(isinstance(item,dict) and item.get('type') in ('reasoning','agent_message','mcp_tool_call'),'TOOL_CONFINEMENT')
  if item['type']=='mcp_tool_call':require(item.get('server')=='evidence' and item.get('tool') in ALLOWED,'MCP_ALLOWLIST')
  if event['type']!='item.completed':continue
  ident=item.get('id');require(isinstance(ident,str) and ident and ident not in ids,'UNIQUE_COMPLETED_ITEM');ids.add(ident);completed.append(item)
  if item['type']!='mcp_tool_call':continue
  all_tools.append(ident);name=item['tool'];result=item.get('result')
  require(item.get('status')=='completed' and item.get('error') is None and isinstance(result,dict),'MCP_COMPLETED')
  content=result.get('content');require(isinstance(content,list) and len(content)==1 and isinstance(content[0],dict) and content[0].get('type')=='text','MCP_TEXT_RESULT')
  reply=contract.strict_json(content[0]['text']);arguments=item.get('arguments')
  require(isinstance(arguments,dict),'NATIVE_ARGUMENTS')
  if name=='submit_review':
   if reply==rs.acknowledgement(submission_raw) and not result.get('isError',False):
    require(arguments==record['submission'],'SUBMISSION_ARGUMENT_BINDING');accepted.append(ident)
   else:require(result.get('isError') is True and isinstance(reply,dict) and set(reply)=={'validation_error'},'SUBMISSION_ACKNOWLEDGEMENT')
  else:
   if result.get('isError',False):
    from orchestrator.scientific_search import ADMIN_RECOVERABLE_ERRORS
    require(isinstance(reply,dict) and set(reply)=={'reader_validation_error'} and reply['reader_validation_error'] in ADMIN_RECOVERABLE_ERRORS,'EVIDENCE_TOOL_FAILED')
    continue  # Failed navigation never counts as an authenticated read.
   if name=='evidence_read':
    require(isinstance(reply,dict) and reply.get('path')==arguments.get('path') and reply.get('authenticated') is True,'AUTHENTICATED_NATIVE_READ')
    path=reply['path'];expected=inspection_binding['files'].get(path.removeprefix('review/'))
    require(expected and reply.get('sha256')==expected,'READ_PACKET_HASH')
    require(type(reply.get('offset')) is int and reply['offset']>=0 and type(reply.get('next_offset')) in (int,type(None)) and isinstance(reply.get('text'),str) and reply['text'],'NONEMPTY_BOUND_READ')
    reads.append(path)
 require(len(accepted)==1,'EXACTLY_ONE_ACCEPTED_SUBMISSION')
 require({'review/manifest.json','review/BRIEF.md'}<=set(reads) and any('review/source/'+n in reads for n in manifest['source_files']),'SCOPE_AND_SOURCE_READS')
 prose=final_prose(values)
 return {'verdict':decision['verdict'],'report':rs.canonical(decision).decode(),'session_id':session,
         'model_ids':[],'requested_model':MODEL,'reviewer_family':'openai',
         'identity_evidence':'frozen OpenAI provider and hash-pinned existing native client; resolved model identity is not reported',
         'usage':usage,'model_usage':None,'tool_use_ids':all_tools,'successful_read_paths':reads,
         'inspection_claim':'authenticated successful native reader calls; not a claim all files were inspected','final_prose':prose}
