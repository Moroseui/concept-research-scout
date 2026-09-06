"""One explicit control route for human buttons and autonomous operator commands.

Public export contains reviewed prose and sanitized execution metadata only.
Low-level CLI protocols stay private. Permitted system prompts and proposal/review
records are preserved in validated evidence.json; unreviewed answers are not shown
as reviewed results.
"""
import argparse
import contextlib
import hashlib
import io
import json
import os
from pathlib import Path
import re
import subprocess
import urllib.request
import urllib.parse
import zipfile

ROOT=Path(__file__).resolve().parents[1]
CONFIG=ROOT/'configs/pilot/human-controls.json'
DANGER=re.compile(r'(sub[-_]stroke[0-9]+|gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|sk-[A-Za-z0-9_-]{20,}|-----BEGIN (?:(?:RSA |OPENSSH |EC |DSA |ENCRYPTED )?PRIVATE KEY|PGP PRIVATE KEY BLOCK)-----)',re.I)


def request(control,mode,experiment,text,source,destination,key,kind):
    cfg=json.loads(CONFIG.read_text())
    if control not in cfg['controls']:raise ValueError('UNKNOWN_CONTROL')
    mode=mode or cfg['controls'][control]['default']
    if mode not in cfg['controls'][control]['modes']:raise ValueError('INVALID_CONTROL_MODE')
    if experiment not in ['P001','P002','P003']:raise ValueError('CAMPAIGN_SCOPE_EXCEEDED')
    if not re.fullmatch('[0-9a-f]{40}',source) or destination!=cfg['destination']:raise ValueError('INVALID_SOURCE_OR_DESTINATION')
    if not re.fullmatch('[a-zA-Z0-9_-]{1,40}',key) or kind not in ['human','codex']:raise ValueError('INVALID_REQUEST_ID_OR_ACTOR')
    if not isinstance(text,str) or len(text)>2000 or DANGER.search(text) or any(ord(c)<32 and c not in '\n\t' for c in text):raise ValueError('REQUEST_CONTENT_NOT_PERMITTED')
    body={'version':1,'control':control,'mode':mode,'experiment':experiment,'request':text,'source':source,'destination':destination,'request_id':key,'initiator_kind':kind}
    body['identity']=hashlib.sha256(json.dumps(body,sort_keys=True).encode()).hexdigest()
    return body


class PrivateRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        redirected=super().redirect_request(req,fp,code,msg,headers,newurl)
        if urllib.parse.urlsplit(req.full_url).netloc!=urllib.parse.urlsplit(newurl).netloc:
            redirected.remove_header('Authorization')
        return redirected


def api(path,token):
    req=urllib.request.Request('https://api.github.com/'+path,headers={'Authorization':'Bearer '+token,'Accept':'application/vnd.github+json','X-GitHub-Api-Version':'2022-11-28'})
    return json.load(urllib.request.urlopen(req,timeout=30))


def restore(req,out):
    """Exact-source, exact-workflow artifact replay; never trust artifact names alone."""
    token=os.environ.get('GH_TOKEN','');repo=os.environ.get('GITHUB_REPOSITORY','')
    if not token or not repo:return False
    name='human-control-'+req['identity']
    listing=api(f'repos/{repo}/actions/artifacts?name={name}&per_page=100',token)
    for artifact in listing['artifacts']:
        if artifact['expired'] or artifact['name']!=name or artifact['size_in_bytes']>1000000:continue
        run=api(f'repos/{repo}/actions/runs/'+str(artifact['workflow_run']['id']),token)
        if run['head_sha']!=req['source'] or run['event']!='workflow_dispatch' or run['status']!='completed' or run['path']!='.github/workflows/'+req['control']+'.yml':continue
        url=f'https://api.github.com/repos/{repo}/actions/artifacts/{artifact["id"]}/zip'
        raw=urllib.request.build_opener(PrivateRedirect()).open(urllib.request.Request(url,headers={'Authorization':'Bearer '+token}),timeout=30).read(1000001)
        if len(raw)>1000000:raise ValueError('REPLAY_TOO_LARGE')
        with zipfile.ZipFile(io.BytesIO(raw)) as z:
            if set(z.namelist())!={'RESULT.md','receipt.json','evidence.json'} or len(z.infolist())!=3 or sum(x.file_size for x in z.infolist())>700000:raise ValueError('REPLAY_CONTENT_INVALID')
            result=z.read('RESULT.md');receipt=json.loads(z.read('receipt.json'));evidence=z.read('evidence.json')
        if receipt['request_identity']!=req['identity'] or receipt['source']!=req['source'] or hashlib.sha256(result).hexdigest()!=receipt['result_sha256']:raise ValueError('REPLAY_BINDING_INVALID')
        if hashlib.sha256(evidence).hexdigest()!=receipt['evidence_sha256']:raise ValueError('REPLAY_EVIDENCE_CHANGED')
        if DANGER.search(result.decode()) or DANGER.search(evidence.decode()):raise ValueError('REPLAY_PUBLICATION_REJECTED')
        (out/'RESULT.md').write_bytes(result)
        (out/'evidence.json').write_bytes(evidence)
        receipt['reused_from_run']=run['id'];receipt['submission_run_id']=os.environ.get('GITHUB_RUN_ID');receipt['model_calls_this_submission']=0
        (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
        return True
    if listing.get('total_count',len(listing['artifacts']))>100:raise ValueError('REPLAY_LOOKUP_LIMIT')
    return False


def save(out,req,status,answer,next_action,evidence=None):
    from orchestrator.public_export import text as public_text
    public_text(answer)
    if DANGER.search(answer):raise ValueError('PUBLICATION_CONTENT_REJECTED')
    text=f'# {req["control"]}: {status}\n\n{answer}\n\n**Next action:** {next_action}\n\nSource: `{req["source"]}`. Request: `{req["identity"]}`.\n'
    if len(text.encode())>100000:raise ValueError('PUBLICATION_TOO_LARGE')
    (out/'RESULT.md').write_text(text)
    public_evidence=json.dumps(evidence or {},indent=2)+'\n'
    if DANGER.search(public_evidence) or len(public_evidence.encode())>500000:raise ValueError('EVIDENCE_PUBLICATION_REJECTED')
    public_text(public_evidence,500000)
    (out/'evidence.json').write_text(public_evidence)
    receipt={'status':status,'source':req['source'],'request_identity':req['identity'],
             'control':req['control'],'mode':req['mode'],'experiment':req['experiment'],
             'destination':req['destination'],'initiator_kind_declared':req['initiator_kind'],
             'github_actor':os.environ.get('GITHUB_ACTOR'), 'run_id':os.environ.get('GITHUB_RUN_ID'),
             'run_attempt':os.environ.get('GITHUB_RUN_ATTEMPT'),'ci':bool(os.environ.get('SCOUT_CI')),
             'result_sha256':hashlib.sha256(text.encode()).hexdigest(),'evidence_sha256':hashlib.sha256(public_evidence.encode()).hexdigest(),
             'human_ratification':False,'patient_execution':False,
             'model_calls_this_submission':(evidence or {}).get('model_calls')}
    (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
    return receipt


def execute(req,out):
    import scout
    from orchestrator import campaign_pipeline as pipeline
    from orchestrator.actions_runner import reviewed,identity
    out=Path(out)
    out.mkdir(parents=True,exist_ok=False)
    private=None
    try:
        actual=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
        if req['source']!=actual:raise ValueError('SOURCE_MISMATCH')
        if os.environ.get('SCOUT_CI'):
            runner=identity()
            if runner['github_sha']!=actual or os.environ.get('GITHUB_REF') not in ['refs/heads/main','refs/heads/astra/autonomous-isles-pilot']:raise ValueError('WORKFLOW_SOURCE_MISMATCH')
            review=reviewed()
            if restore(req,out):return json.loads((out/'receipt.json').read_text())
        else:review=None
        if req['mode']=='status':
            exp=ROOT/'campaigns/isles24-pilot/experiments'/req['experiment']
            # Existing import integrity gate, not a synthetic success status.
            pipeline.grounding(ROOT,req['experiment'])
            present=(exp/'import_receipt.json').exists()
            return save(out,req,'READY' if present else 'WAITING_FOR_RESULT',
                        'A bound aggregate import is present.' if present else 'No validated aggregate import exists. No patient run or scientific result is claimed.',
                        'Use the interpretation control.' if present else 'Return private checkpoints and original console through the approved private route, then run validate-bundle and record-result. Do not upload patient files to Actions.',{'import_present':present})
        private=ROOT/'campaigns/isles24-pilot/pipeline'/('actions-'+req['identity']+'-'+os.environ.get('GITHUB_RUN_ID','local'))
        initiator={'kind':req['initiator_kind'],'github_actor':os.environ.get('GITHUB_ACTOR'),'authority':'request_only_not_human_ratification'}
        with contextlib.redirect_stdout(io.StringIO()),contextlib.redirect_stderr(io.StringIO()):
            result=pipeline.execute(scout,req['mode'],req['experiment'],req['request'] or 'Summarize the current evidence, limitations and next decision for this control.',private,initiator=initiator)
        folder=private/f'round-{result["round"]}'
        # Code proposals remain in the original system record, not executable Actions artifacts.
        prose=[p for p in folder.iterdir() if p.suffix=='.md' and not p.name.startswith('prompt_')]
        answer='\n\n'.join(p.read_text() for p in sorted(prose))
        # Include the actual opposing critique/rationale in the phone-readable result.
        critique=json.loads((folder/'review.json').read_text())
        answer+='\n\n## Opposing-family system review\n'+critique['verdict']+': '+critique['rationale']
        records={}
        runners={}
        for p in sorted(private.rglob('*')):
            if p.is_file() and not p.is_symlink() and p.name.startswith('runner_'):
                runners[p.relative_to(private).as_posix()]={k:v for k,v in json.loads(p.read_text()).items() if k!='private_evidence'}
            if p.is_file() and not p.is_symlink() and p.suffix in ['.md','.json','.jsonl','.py'] and not p.name.startswith('runner_'):
                records[p.relative_to(private).as_posix()]=p.read_text()
        return save(out,req,'REVIEWED_PROPOSAL',answer,'Review this proposal. Adoption, experiment execution and human ratification are separate gates.',
                    {'original_system_records':records,'runner_metadata_projection':runners,
                     'model_calls':sum(len(v.splitlines()) for k,v in records.items() if k.endswith('stage_provenance.jsonl')),'adapter_review':review,'input_sha256':result['input_sha256'],'artifact_sha256':result['artifact_sha256'],
                     'author_family':result['author_family'],'reviewer_family':result['reviewer_family'],'round':result['round'],'ci':result['ci']})
    except BaseException as error:
        code=str(error) if re.fullmatch('[A-Z_]+',str(error)) else type(error).__name__
        failures={}
        if private is not None and private.is_dir():
            for p in private.rglob('*'):
                if p.is_file() and not p.is_symlink() and p.suffix in ['.md','.json','.jsonl','.py'] and not p.name.startswith('runner_'):
                    value=p.read_text()
                    from orchestrator.public_export import text as public_text
                    try:public_text(value)
                    except ValueError:continue  # rejected original remains private, not relabeled reviewed
                    failures[p.relative_to(private).as_posix()]=value
        if len(json.dumps(failures).encode())>400000:failures={'retention_note':'Public failure evidence exceeds the bounded export; low-level originals remain ephemeral and are not claimed as durably retained.'}
        return save(out,req,'BLOCKED','The system stopped: '+code+'. No partial proposal is presented as reviewed.',
                    'Inspect the named gate. Repair authentication or input/review bindings, then submit a new request ID. For interpretation, first import a validated result; proposal review never grants human ratification.',{'failure_code':code,'unreviewed_system_records':failures})


def validate_export(out):
    out=Path(out)
    if {p.name for p in out.iterdir()}!={'RESULT.md','receipt.json','evidence.json'}:
        raise ValueError('UNKNOWN_PUBLICATION_FILE')
    for p in out.iterdir():
        if p.is_symlink() or not p.is_file() or p.stat().st_size>700000 or DANGER.search(p.read_text()):
            raise ValueError('PUBLICATION_REJECTED')
    r=json.loads((out/'receipt.json').read_text())
    for key,name in [('result_sha256','RESULT.md'),('evidence_sha256','evidence.json')]:
        if r[key]!=hashlib.sha256((out/name).read_bytes()).hexdigest():raise ValueError('PUBLICATION_BYTES_CHANGED')
    from orchestrator.public_export import text
    text((out/'RESULT.md').read_text())
    text((out/'evidence.json').read_text(),700000)
    text((out/'receipt.json').read_text(),700000)
    return r


def main():
    p=argparse.ArgumentParser();p.add_argument('--control',required=True);p.add_argument('--mode',default='');p.add_argument('--experiment',default='P001');p.add_argument('--request',default='');p.add_argument('--source',required=True);p.add_argument('--destination',default='actions-artifact');p.add_argument('--request-id',default='default');p.add_argument('--initiator',choices=['human','codex'],default='human');p.add_argument('--output',type=Path,required=True)
    a=p.parse_args()
    try:r=request(a.control,a.mode,a.experiment,a.request,a.source,a.destination,a.request_id,a.initiator)
    except ValueError as e:
        # Invalid user inputs get a readable, fixed-content refusal without echoing them.
        a.output.mkdir(parents=True,exist_ok=False)
        r={'control':'invalid','mode':'invalid','experiment':'invalid','source':'unbound','identity':'invalid','destination':'none','initiator_kind':'unverified'}
        result=save(a.output,r,'BLOCKED',str(e),'Correct the control inputs and submit again.')
    else:result=execute(r,a.output)
    validate_export(a.output)
    if os.environ.get('GITHUB_OUTPUT'):
        with open(os.environ['GITHUB_OUTPUT'],'a') as f:f.write('artifact_name=human-control-'+r['identity']+'\n')
    if os.environ.get('GITHUB_STEP_SUMMARY'):
        from orchestrator.public_export import summary
        summary((a.output/'RESULT.md').read_text(),os.environ['GITHUB_STEP_SUMMARY'])
    print(json.dumps({'status':result['status'],'result_file':'RESULT.md'}))
    return 0 if result['status']!='BLOCKED' else 2


if __name__=='__main__':raise SystemExit(main())
