"""Read-only search over the exact prepared scientific workspace inputs.

A small stdio MCP adapter, not a shell or additional evidence store. Native Read
still inspects originals. Search reports bounded locations, never conclusions.
"""
import fnmatch
import hashlib
import json
import os
from pathlib import Path
import stat
import sys

MAX_FILES=1024
MAX_BYTES=64*1024*1024
MAX_FILE=8*1024*1024
MAX_REQUEST=8192
MAX_RESPONSE=16000
MAX_HITS=40
MANIFEST='.scientific-search.json'
SERVER='.scientific-search.py'
INSTRUCTION=('Scientific reviewers have evidence_search (literal text) and evidence_glob '
 '(registered file IDs/paths). Use them to locate components, then Read the original '
 'files at the returned line numbers. Search is bounded and paginated; follow next_cursor '
 'when present. Cite original files/views and hashes for numeric claims, not navigation copies. ')


def regular(root,name):
    rel=Path(name)
    if not isinstance(name,str) or not name or rel.is_absolute() or '..' in rel.parts:
        raise ValueError('SEARCH_PATH_REFUSED')
    p=root/rel
    for item in [p,*p.parents]:
        if item==root.parent:break
        if item.is_symlink():raise ValueError('SEARCH_SYMLINK_REFUSED')
    if not p.resolve().is_relative_to(root.resolve()):raise ValueError('SEARCH_PATH_REFUSED')
    if not stat.S_ISREG(p.stat().st_mode) or p.stat().st_size>MAX_FILE:
        raise ValueError('SEARCH_FILE_BOUND')
    return p


def prepare(workspace):
    from orchestrator import private_records as pr
    root=Path(workspace).resolve()
    receipt=json.loads((root/'input-measurement.json').read_bytes())
    rows={}
    for item in receipt['workspace_files']:
        name=item['path'];p=regular(root,name);raw=p.read_bytes()
        if hashlib.sha256(raw).hexdigest()!=item['sha256']:raise ValueError('SEARCH_INPUT_CHANGED')
        row={'path':name,'id':item.get('id',name),'sha256':item['sha256'],'bytes':len(raw)}
        if name in rows and rows[name]!=row:raise ValueError('SEARCH_DUPLICATE_BINDING')
        rows[name]=row
    if len(rows)>MAX_FILES or sum(x['bytes'] for x in rows.values())>MAX_BYTES:raise ValueError('SEARCH_INVENTORY_BOUND')
    raw=json.dumps({'schema':'scientific-search/v1','files':sorted(rows.values(),key=lambda x:x['path'])},sort_keys=True).encode()
    pr.write_bytes(root/MANIFEST,raw);pr.write_bytes(root/SERVER,Path(__file__).read_bytes())
    return {'manifest_sha256':hashlib.sha256(raw).hexdigest(),'server_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'files':len(rows),'bytes':sum(x['bytes'] for x in rows.values())}


def query(root,manifest_sha256,name,args):
    root=Path(root).resolve();raw=regular(root,MANIFEST).read_bytes()
    if hashlib.sha256(raw).hexdigest()!=manifest_sha256:raise ValueError('SEARCH_MANIFEST_CHANGED')
    m=json.loads(raw);files=m['files']
    if m.get('schema')!='scientific-search/v1' or len(files)>MAX_FILES or sum(f['bytes'] for f in files)>MAX_BYTES:raise ValueError('SEARCH_INVENTORY_BOUND')
    if name not in ('evidence_search','evidence_glob') or not isinstance(args,dict):raise ValueError('SEARCH_TOOL_REFUSED')
    allowed={'query','pattern','cursor'} if name=='evidence_search' else {'pattern','cursor'}
    if set(args)-allowed:raise ValueError('SEARCH_ARGUMENT_REFUSED')
    pattern=args.get('pattern','*');needle=args.get('query','');cursor=args.get('cursor',0)
    if not isinstance(pattern,str) or not 1<=len(pattern)<=256 or pattern.startswith('/') or '..' in Path(pattern).parts:raise ValueError('SEARCH_PATTERN_REFUSED')
    if name=='evidence_search' and (not isinstance(needle,str) or not 1<=len(needle)<=256):raise ValueError('SEARCH_QUERY_BOUND')
    if type(cursor)!=int or not 0<=cursor<=10000000:raise ValueError('SEARCH_CURSOR_BOUND')
    hits=[];seen=0;scanned=0
    for item in files:
        if not (fnmatch.fnmatchcase(item['path'],pattern) or fnmatch.fnmatchcase(item['id'],pattern)):continue
        p=regular(root,item['path']);data=p.read_bytes();scanned+=len(data)
        if len(data)!=item['bytes'] or hashlib.sha256(data).hexdigest()!=item['sha256']:raise ValueError('SEARCH_INPUT_CHANGED')
        if scanned>MAX_BYTES:raise ValueError('SEARCH_BYTES_BOUND')
        matches=[(None,None)] if name=='evidence_glob' else ((i,line) for i,line in enumerate(data.decode('utf-8').splitlines(),1) if needle.casefold() in line.casefold())
        for line,text in matches:
            if seen<cursor:seen+=1;continue
            hit={'path':item['path'],'id':item['id'],'sha256':item['sha256']}
            if line is not None:
                start=max(0,text.casefold().find(needle.casefold())-60)
                hit.update(line=line,column=start+1,preview=text[start:start+160],preview_truncated=start>0 or len(text)>start+160)
            trial={'hits':hits+[hit],'next_cursor':seen+1,'navigation_only':True}
            if len(hits)>=MAX_HITS or len(json.dumps(trial,ensure_ascii=True).encode())>MAX_RESPONSE//2-512:
                return {'hits':hits,'next_cursor':seen,'navigation_only':True}
            hits.append(hit);seen+=1
    return {'hits':hits,'next_cursor':None,'navigation_only':True}


TOOLS=[{'name':n,'description':d,'inputSchema':{'type':'object','properties':props,'required':req,'additionalProperties':False}}
 for n,d,props,req in [
 ('evidence_search','Bounded literal search of authenticated workspace evidence. Returns original file hashes and line locations. Follow cursor; inspect originals with Read.',{'query':{'type':'string','minLength':1,'maxLength':256},'pattern':{'type':'string','maxLength':256},'cursor':{'type':'integer','minimum':0}},['query']),
 ('evidence_glob','Find authenticated workspace evidence by file ID or path glob; no external filesystem access.',{'pattern':{'type':'string','maxLength':256},'cursor':{'type':'integer','minimum':0}},[])]]


def submission_module(root, pins):
    import importlib.util
    if len(pins)!=3:raise ValueError('SUBMISSION_RUNTIME_PINS_REQUIRED')
    for name,filename,pin in [('review_contract','.review-contract.py',pins[2]),('review_submission','.review-submission.py',pins[1])]:
        path=regular(Path(root),filename)
        if hashlib.sha256(path.read_bytes()).hexdigest()!=pin:raise ValueError('SUBMISSION_RUNTIME_CHANGED')
        spec=importlib.util.spec_from_file_location(name,path);module=importlib.util.module_from_spec(spec)
        sys.modules[name]=module;spec.loader.exec_module(module)
    module=sys.modules['review_submission'];module.load(root,pins[0])
    return module


def serve(root,pin,submission_pins=()):
    submission=submission_module(root,submission_pins) if submission_pins else None
    tools=list(TOOLS)
    if submission:
        tools.append({'name':'submit_review','description':'Submit the independent review decision once. Exact call bindings and structured findings are required. Validation errors may be corrected in this session; an accepted submission cannot be replaced.',
                      'inputSchema':submission.schema(submission.load(root,submission_pins[0]))})
    request_bound=MAX_REQUEST if submission is None else submission.MAX_BYTES+1024
    for raw in iter(lambda:sys.stdin.buffer.readline(request_bound+1),b''):
        if len(raw)>request_bound:raise ValueError('SEARCH_REQUEST_BOUND')
        req=(submission.contract.strict_json(raw) if submission else json.loads(raw));ident=req.get('id');method=req.get('method')
        if ident is None:continue
        try:
            if method=='initialize':result={'protocolVersion':'2024-11-05','capabilities':{'tools':{}},'serverInfo':{'name':'scientific-evidence-search','version':'1'}}
            elif method=='tools/list':result={'tools':tools}
            elif method=='ping':result={}
            elif method=='tools/call':
                params=req['params']
                if submission and params['name']=='submit_review':
                    try:
                        answer=submission.submit(root,submission_pins[0],params.get('arguments',{}));failed=False
                    except ValueError as error:
                        # Schema corrections are supported within this invocation.
                        # Config/file/transport failures are not validation retries.
                        code=str(error)
                        expected={'SUBMISSION_ENUM_OR_BINDING','SUBMISSION_EXACT_FIELDS','SUBMISSION_ARRAY','SUBMISSION_STRING','SUBMISSION_SIZE',
                                  'LISTED_FINDING_BLOCKS_APPROVAL','INCOMPLETE_REVIEW_FINDING','AMBIGUOUS_REVIEW_FINDING','REVIEW_RATIONALE_REQUIRED','STRUCTURED_REVIEW_SCOPE_REQUIRED'}
                        if code not in expected:raise
                        answer={'validation_error':code};failed=True
                    result={'content':[{'type':'text','text':json.dumps(answer,ensure_ascii=True)}],'isError':failed}
                else:
                    if len(raw)>MAX_REQUEST:raise ValueError('SEARCH_REQUEST_BOUND')
                    result={'content':[{'type':'text','text':json.dumps(query(root,pin,params['name'],params.get('arguments',{})),ensure_ascii=True)}],'isError':False}
            else:raise ValueError('SEARCH_METHOD_REFUSED')
            reply={'jsonrpc':'2.0','id':ident,'result':result}
        except (ValueError,KeyError,TypeError,OSError) as e:
            reply={'jsonrpc':'2.0','id':ident,'error':{'code':-32602,'message':str(e)[:200]}}
        print(json.dumps(reply,ensure_ascii=True),flush=True)

if __name__=='__main__':
    if len(sys.argv) not in (2,5):raise SystemExit('SEARCH_MANIFEST_PIN_REQUIRED')
    serve(Path.cwd(),sys.argv[1],sys.argv[2:])
