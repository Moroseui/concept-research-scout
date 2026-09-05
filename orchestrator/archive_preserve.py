"""System-owned archive verification/preservation jobs; no P001 dispatch capability."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import time
import uuid
from orchestrator.colab_patient import CPU_CELL, PRIVATE_CONFIG, verify_cell_sources, tool_exchanges, streams
from orchestrator.colab_worker import ROOT, private_dir, write_private

FILES=['scripts/colab_archive_preserve.py','orchestrator/archive_preserve.py','tests/test_archive_preserve.py']
PREFIX=ROOT/'docs/isles-pilot/reviews/archive-preserve'


def reviewed():
    e=json.loads(Path(str(PREFIX)+'.execution.json').read_text())
    p=Path(str(PREFIX)+'.response.json');r=json.loads(p.read_text());v=r.get('structured_output',{})
    if e['returncode'] or r.get('is_error') or r.get('subtype')!='success' or v.get('verdict')!='APPROVE' or v.get('scope')!='archive-preserve' or v.get('reviewed_commit')!=e['reviewed_commit'] or 'claude-fable-5' not in e['assistant_message_models'] or hashlib.sha256(p.read_bytes()).hexdigest()!=e['response_sha256']:
        raise ValueError('completed independent archive review required')
    for f in FILES:
        if hashlib.sha256((ROOT/f).read_bytes()).hexdigest()!=e['input_file_sha256'].get(f):raise ValueError('archive review stale')
    return e['reviewed_commit']


def cells_for(action, job):
    if not re.fullmatch('/content/drive/MyDrive/isles-pilot/archive-preservation-[a-f0-9]{32}', job):
        raise ValueError('fresh private archive job path required')
    source=(ROOT/FILES[0]).read_text()
    if action=='start':
        setup="import os, json\nfrom pathlib import Path\nassert os.path.ismount('/content/drive'), 'Operator Drive mount required'\njob=Path("+repr(job)+")\njob.mkdir(mode=0o700)\nprint(json.dumps({'status':'PREPARED'}))\n"
        write='%%writefile '+job+'/verify.py\n'+source
        launch="import subprocess, sys, json\nfrom pathlib import Path\njob=Path("+repr(job)+")\nwith (job/'console.log').open('xb') as console:\n    process=subprocess.Popen([sys.executable,str(job/'verify.py'),str(job)],stdout=console,stderr=subprocess.STDOUT,start_new_session=True)\nprint(json.dumps({'status':'VERIFICATION_STARTED','pid':process.pid}))\n"
        return [CPU_CELL,setup,write,launch]
    retrieve="import os, json, hashlib\nfrom pathlib import Path\njob=Path("+repr(job)+")\nassert os.path.ismount('/content/drive'), 'Drive unavailable'\nassert hashlib.sha256((job/'verify.py').read_bytes()).hexdigest()=="+repr(hashlib.sha256(source.encode()).hexdigest())+"\np=job/'receipt.json'\nprint(p.read_text() if p.is_file() else json.dumps({'status':'STARTING'}))\n"
    return [CPU_CELL,retrieve]


def run(action, directory, job=None):
    pin=reviewed();directory=private_dir(directory)
    job=job or '/content/drive/MyDrive/isles-pilot/archive-preservation-'+uuid.uuid4().hex
    cells=cells_for(action,job)
    write_private(directory/'packet.json',json.dumps({'action':action,'job':job,'cells':cells,'reviewed_commit':pin},indent=2))
    prompt=('You are an authorized archive-storage execution worker, separate from reviewers. Use the official colab-worker connection to the ORIGINAL existing CPU runtime holding the downloaded archive. '
      'Do not provision or select a new runtime. The user explicitly requests rehashing opaque archive bytes, a fresh exclusive Drive copy if needed, and metadata-only P001 reconciliation. No extraction, patient analysis, dispatch, deletion, overwriting, downloads or reading private console/patient files through tools. '
      'This plain readable source has independent approval at '+pin+'. The background process ONLY hashes/copies the archive and inspects fixed metadata; it never runs P001. Full diagnostics remain privately in its fresh job folder. '
      'Use a fresh notebook in the same existing runtime. Insert ONLY the exact supplied cells, read back each with get_cells includeOutputs=false, and execute in order. Stop if CPU check fails or Drive is absent; report needed browser/Drive action. Never retry a start. '
      'Keep connection tokens private. All code is shown below without nested exec or encoding. Return a brief status only.\n'+ '\n'.join('CELL '+str(i)+'\n```python\n'+s+'\n```' for i,s in enumerate(cells)))
    cmd=['claude','-p','--model','claude-fable-5','--output-format','stream-json','--verbose','--strict-mcp-config','--mcp-config',str(PRIVATE_CONFIG),'--tools','ToolSearch','--allowedTools','mcp__colab-worker__*','--permission-mode','dontAsk','--max-turns','30']
    meta={'status':'FAILED','action':action,'job':job,'reviewed_commit':pin};start=time.monotonic()
    try:
        with (directory/'protocol.jsonl').open('xb') as out,(directory/'stderr.log').open('xb') as err:
            os.chmod(out.name,0o600);os.chmod(err.name,0o600)
            result=subprocess.run(cmd,input=prompt,text=True,stdout=out,stderr=err,cwd=directory,timeout=600)
        events=[json.loads(l) for l in (directory/'protocol.jsonl').read_text().splitlines()]
        final=[e for e in events if e.get('type')=='result'][-1]
        meta['actual_models']=list(final.get('modelUsage',{}))
        if result.returncode or final.get('is_error') or final.get('subtype')!='success':raise ValueError('incomplete worker')
        verify_cell_sources(events,cells)
        calls,results=tool_exchanges(events);runs=[c for c in calls if c['name'].endswith('__run_code_cell')]
        if json.loads(streams(results[runs[0]['id']]))!={'cpu_only':True,'colab_runtime':True}:raise ValueError('CPU Colab required')
        data=json.loads(streams(results[runs[-1]['id']]))
        meta.update(status='COMPLETE',remote=data)
    except Exception as error:
        meta['failure_type']=type(error).__name__
    meta['wall_seconds']=time.monotonic()-start
    write_private(directory/'status.json',json.dumps(meta,indent=2));return meta


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('action',choices=['start','poll']);p.add_argument('--job');p.add_argument('--private-dir',required=True,type=Path);a=p.parse_args()
    if a.action=='poll' and not a.job:p.error('poll requires exact --job')
    if a.action=='start' and a.job:p.error('start always uses a fresh exclusive destination')
    print(json.dumps(run(a.action,a.private_dir,a.job),indent=2))
