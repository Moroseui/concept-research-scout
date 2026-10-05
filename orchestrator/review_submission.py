"""Bound, exactly-once MCP decision delivery. Stdlib only inside the jail."""
import hashlib
import json
import os
from pathlib import Path
import stat
try:
    from orchestrator import review_contract as contract
except ModuleNotFoundError:
    import review_contract as contract

CONFIG = '.review-submission-config.json'
RECORD = '.review-submission.json'
MODULE = '.review-submission.py'
CONTRACT = '.review-contract.py'
MAX_BYTES = 80000
TOOL = 'mcp__evidence__submit_review'
SEARCH_TOOLS = ('mcp__evidence__evidence_search', 'mcp__evidence__evidence_glob')

def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=True).encode()

def sha(raw):
    return hashlib.sha256(raw).hexdigest()

def regular(path):
    path=Path(path)
    if any(p.is_symlink() for p in [path,*path.parents]): raise ValueError('SUBMISSION_ALIAS')
    s=path.stat()
    if not stat.S_ISREG(s.st_mode) or s.st_nlink!=1 or s.st_mode & 0o027 or s.st_size>MAX_BYTES:
        raise ValueError('SUBMISSION_FILE_IDENTITY')
    return path

def load(root, pin):
    raw=regular(Path(root)/CONFIG).read_bytes()
    if sha(raw)!=pin: raise ValueError('SUBMISSION_CONFIG_CHANGED')
    value=contract.strict_json(raw)
    if set(value)!={'schema','kind','bindings'} or value['schema']!='review-submission/v1':
        raise ValueError('SUBMISSION_CONFIG_SCHEMA')
    keys = ({'source_sha','runtime_sha256','packet_sha256'} if value['kind']=='administrative' else
            {'call_id','run_id','stage','source_sha','runtime_sha256','input_sha256'} if value['kind']=='scientific' else set())
    if not keys or set(value['bindings'])!=keys or any(not isinstance(v,str) or not v for v in value['bindings'].values()):
        raise ValueError('SUBMISSION_BINDINGS_SCHEMA')
    return value

def schema(config):
    string={'type':'string','minLength':1,'maxLength':MAX_BYTES}
    finding={'type':'object','properties':{k:({'type':'string','enum':list(contract.CATEGORIES)} if k=='category' else string) for k in sorted(contract.FINDING_FIELDS)},'required':sorted(contract.FINDING_FIELDS),'additionalProperties':False}
    fields={'verdict':{'type':'string','enum':['APPROVE','REVISE','REJECT']},'findings':{'type':'array','items':finding,'maxItems':100},'rationale':string}
    if config['kind']=='administrative':
        fields.update(schema={'type':'string','enum':[contract.SCHEMA]},
            inspected_scope={'type':'array','items':string,'minItems':1,'maxItems':100},
            limitations={'type':'array','items':string,'maxItems':100},
            analysis_entrypoint={'enum':[None,'orchestrator.analysis_driver']})
        fields.update({k:{'type':'string','enum':[v]} for k,v in config['bindings'].items()})
    else:
        fields['bindings']={'type':'object','properties':{k:{'type':'string','enum':[v]} for k,v in config['bindings'].items()},'required':sorted(config['bindings']),'additionalProperties':False}
    return {'type':'object','properties':fields,'required':sorted(fields),'additionalProperties':False}

def validate_schema(value,spec):
    if 'enum' in spec and value not in spec['enum']: raise ValueError('SUBMISSION_ENUM_OR_BINDING')
    kind=spec.get('type')
    if kind=='object':
        if not isinstance(value,dict) or set(value)!=set(spec['required']): raise ValueError('SUBMISSION_EXACT_FIELDS')
        for k,v in value.items(): validate_schema(v,spec['properties'][k])
    elif kind=='array':
        if not isinstance(value,list) or not spec.get('minItems',0)<=len(value)<=spec['maxItems']:raise ValueError('SUBMISSION_ARRAY')
        for v in value:validate_schema(v,spec['items'])
    elif kind=='string':
        if not isinstance(value,str) or not spec.get('minLength',0)<=len(value)<=spec.get('maxLength',MAX_BYTES):raise ValueError('SUBMISSION_STRING')

def validate(payload,config):
    if len(canonical(payload))>MAX_BYTES:raise ValueError('SUBMISSION_SIZE')
    validate_schema(payload,schema(config))
    if config['kind']=='scientific':
        decision={k:payload[k] for k in ('verdict','findings','rationale')}
        contract.scientific(canonical(decision))
    else:
        decision=payload
        contract.decision(decision,set(schema(config)['properties']))
        if any(not x.strip() for k in ('inspected_scope','limitations') for x in payload[k]):
            raise ValueError('STRUCTURED_REVIEW_SCOPE_REQUIRED')
    return decision

def acknowledgement(raw):
    return {'status':'ACCEPTED','record_sha256':sha(raw)}

def submit(root,pin,payload):
    root=Path(root);config=load(root,pin)
    if (root/RECORD).exists() or (root/RECORD).is_symlink():raise ValueError('SECOND_SUBMISSION_REFUSED')
    validate(payload,config)
    raw=canonical({'schema':'accepted-review-submission/v1','config_sha256':pin,'submission':payload})
    if len(raw)>MAX_BYTES:raise ValueError('SUBMISSION_SIZE')
    fd=os.open(root/RECORD,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
    with os.fdopen(fd,'wb') as f:
        f.write(raw);f.flush();os.fsync(f.fileno())
    regular(root/RECORD)
    return acknowledgement(raw)

def prepare(root,kind,bindings):
    from orchestrator import private_records as pr
    root=Path(root)
    if (root/RECORD).exists() or (root/RECORD).is_symlink():raise ValueError('SUBMISSION_ALREADY_PRESENT')
    config={'schema':'review-submission/v1','kind':kind,'bindings':bindings}
    sources={CONFIG:canonical(config),MODULE:Path(__file__).read_bytes(),CONTRACT:Path(contract.__file__).read_bytes()}
    for name,raw in sources.items():
        p=root/name
        if p.exists():
            if regular(p).read_bytes()!=raw:raise ValueError('SUBMISSION_PREPARATION_CHANGED')
        else:pr.write_bytes(p,raw)
    pin=sha(sources[CONFIG]);load(root,pin)
    return {'config_sha256':pin,'module_sha256':sha(sources[MODULE]),'contract_sha256':sha(sources[CONTRACT])}

def verify_record(raw,config,pin):
    value=contract.strict_json(raw)
    if (not isinstance(value,dict) or set(value)!={'schema','config_sha256','submission'} or
        value['schema']!='accepted-review-submission/v1' or value['config_sha256']!=pin or canonical(value)!=raw):
        raise ValueError('SUBMISSION_RECORD_BINDING')
    return validate(value['submission'],config)

def verify_native(raw,config,pin,events):
    decision=verify_record(raw,config,pin)
    value=contract.strict_json(raw);uses=[];results=[]
    for event in events:
        content=event.get('message',{}).get('content',[])
        if not isinstance(content,list):continue
        for b in content:
            if not isinstance(b,dict):continue
            if event.get('type')=='assistant' and b.get('type')=='tool_use' and b.get('name')==TOOL:uses.append(b)
            if event.get('type')=='user' and b.get('type')=='tool_result':results.append(b)
    all_uses=[b for e in events if e.get('type')=='assistant' for b in e.get('message',{}).get('content',[]) if isinstance(b,dict) and b.get('type')=='tool_use']
    for use in all_uses:
        if use.get('name') in SEARCH_TOOLS:
            matches=[r for r in results if r.get('tool_use_id')==use.get('id')]
            if len(matches)!=1 or matches[0].get('is_error',False):raise ValueError('EVIDENCE_TOOL_FAILURE')
    accepted=[]
    for use in uses:
        matches=[r for r in results if r.get('tool_use_id')==use.get('id')]
        if len(matches)!=1:raise ValueError('SUBMISSION_TOOL_RESULT_REQUIRED')
        result=matches[0]
        content=result.get('content')
        if isinstance(content,list):text=''.join(x.get('text','') for x in content if x.get('type')=='text')
        else:text=content
        try:reply=contract.strict_json(text)
        except (ValueError,TypeError):raise ValueError('SUBMISSION_ACK_REQUIRED')
        if reply==acknowledgement(raw) and not result.get('is_error',False):
            if use.get('input')!=value['submission']:raise ValueError('SUBMISSION_NATIVE_INPUT_CHANGED')
            accepted.append(use['id'])
        elif not (result.get('is_error') is True and isinstance(reply,dict) and set(reply)=={'validation_error'}):
            raise ValueError('SUBMISSION_TOOL_FAILURE')
    if len(accepted)!=1:raise ValueError('EXACTLY_ONE_NATIVE_SUBMISSION_REQUIRED')
    return decision


def runtime_pins(root):
    root=Path(root)
    return {k:sha(regular(root/name).read_bytes()) for k,name in
            [('config_sha256',CONFIG),('module_sha256',MODULE),('contract_sha256',CONTRACT)]}

def mcp_config(search_pin,pins):
    return {'mcpServers':{'evidence':{'command':'/usr/bin/python3',
        'args':['-I','-B','/workspace/.scientific-search.py',search_pin,
                pins['config_sha256'],pins['module_sha256'],pins['contract_sha256']]}}}

def administrative_bindings(manifest):
    return {k:manifest[k] for k in ('source_sha','runtime_sha256')} | {'packet_sha256':sha(canonical(manifest))}


def prepare_administrative(root,manifest,inspection):
    from orchestrator import scientific_search as search, private_records as pr
    root=Path(root);inspection=Path(inspection)
    rows=[]
    for path in sorted(inspection.rglob('*')):
        if path.is_dir():continue
        raw=search.regular(inspection,str(path.relative_to(inspection))).read_bytes()
        name='review/'+str(path.relative_to(inspection))
        rows.append({'path':name,'id':name,'sha256':sha(raw),'bytes':len(raw)})
    if len(rows)>search.MAX_FILES or sum(x['bytes'] for x in rows)>search.MAX_BYTES:raise ValueError('SEARCH_INVENTORY_BOUND')
    pr.write_bytes(root/search.MANIFEST,json.dumps({'schema':'scientific-search/v1','files':rows},sort_keys=True).encode())
    pr.write_bytes(root/search.SERVER,Path(search.__file__).read_bytes())
    return prepare(root,'administrative',administrative_bindings(manifest))


class TerminalSubmissionFailure(ValueError):
    """A captured successful terminal client invocation has no valid submission."""


def collect_scientific(root,console):
    root=Path(root);events=[]
    for line in console.splitlines():
        try:event=contract.strict_json(line)
        except ValueError:continue  # scout may prefix non-native transport messages
        if isinstance(event,dict):events.append(event)
    finals=[e for e in events if e.get('type')=='result']
    if len(finals)!=1 or finals[0].get('subtype')!='success' or finals[0].get('is_error') is not False:
        raise ValueError('SUBMISSION_NATIVE_TERMINAL_REQUIRED')
    session=finals[0].get('session_id')
    if not session or {e['session_id'] for e in events if e.get('session_id')}!={session}:
        raise ValueError('SUBMISSION_NATIVE_SESSION_REQUIRED')
    tools=[b for e in events if e.get('type')=='assistant' for b in e.get('message',{}).get('content',[]) if isinstance(b,dict) and b.get('type')=='tool_use']
    if any(b.get('name') not in ('Read',*SEARCH_TOOLS,TOOL) for b in tools):raise ValueError('SUBMISSION_TOOL_CONFINEMENT')
    pins=runtime_pins(root);config=load(root,pins['config_sha256'])
    try:
        if not (root/RECORD).exists():raise ValueError('ACCEPTED_SUBMISSION_REQUIRED')
        raw=regular(root/RECORD).read_bytes()
        decision=verify_native(raw,config,pins['config_sha256'],events)
    except ValueError as error:
        raise TerminalSubmissionFailure(str(error)) from error
    from orchestrator import private_records as pr
    with pr.open_file(root/'review.json','xb') as out:out.write(canonical(decision))
    return {'record_sha256':sha(raw),'config_sha256':pins['config_sha256'],'session_id':session,
            'verdict_origin':'accepted MCP submission; never final prose'}


def terminal_without_submission(root,console):
    """Only a positively captured terminal invocation can be marked FAILED here."""
    root=Path(root)
    if not (root/CONFIG).exists() or (root/RECORD).exists():return False
    events=[]
    for line in console.splitlines():
        try:value=contract.strict_json(line)
        except ValueError:continue
        if isinstance(value,dict):events.append(value)
    results=[e for e in events if e.get('type')=='result']
    if len(results)!=1 or events[-1]!=results[0]:return False
    final=results[0];session=final.get('session_id')
    return bool(session and isinstance(final.get('is_error'),bool) and
        final.get('subtype') in {'success','error_max_turns','error_during_execution','error_max_budget_usd'} and
        {e['session_id'] for e in events if e.get('session_id')}=={session})
