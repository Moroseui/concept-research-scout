"""Reviewed, fixed-cell archive acquisition through the private Claude worker."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import time
from orchestrator.colab_patient import (ROOT, PRIVATE_CONFIG, CPU_CELL,
    verify_cell_sources, tool_exchanges, streams)
from orchestrator.colab_worker import private_dir, write_private

FILES=['scripts/colab_archive_acquire.py','orchestrator/colab_acquire.py',
       'tests/test_colab_acquire.py','docs/isles-pilot/P001_ARCHIVE_ACQUISITION.md']
PREFIX=ROOT/'docs/isles-pilot/reviews/p001-acquisition'


def reviewed():
    execution=json.loads(Path(str(PREFIX)+'.execution.json').read_text())
    response_path=Path(str(PREFIX)+'.response.json')
    response=json.loads(response_path.read_text())
    verdict=response.get('structured_output',{})
    if (execution['returncode']!=0 or response.get('is_error') or
        response.get('subtype')!='success' or verdict.get('verdict')!='APPROVE' or
        verdict.get('scope')!='p001-archive-acquisition' or
        verdict.get('reviewed_commit')!=execution['reviewed_commit'] or
        'claude-fable-5' not in execution.get('assistant_message_models',[]) or
        hashlib.sha256(response_path.read_bytes()).hexdigest()!=execution['response_sha256']):
        raise ValueError('completed Fable acquisition approval required')
    for name in FILES:
        if hashlib.sha256((ROOT/name).read_bytes()).hexdigest()!=execution['input_file_sha256'].get(name):
            raise ValueError('acquisition review binding mismatch')
    return execution['reviewed_commit']


def run(action, destination):
    revision=reviewed()
    directory=private_dir(destination)
    source=(ROOT/FILES[0]).read_text()+'\nprint(json.dumps('+action+'()))\n'
    cells=[CPU_CELL,source]
    write_private(directory/'cells.json',json.dumps(cells))
    prompt=('You are a bounded Colab execution worker, not a reviewer. Official colab-worker connection '
        'to existing CPU runtime. Fresh blank notebook; includeOutputs=false. Insert and read back '
        'exactly these two cells before running in order. Stop if CPU check fails. Execute no other '
        'code. This independently reviewed acquisition downloads only the pinned archive into private '
        'local staging and verifies its size/MD5; no extraction or patient analysis. Never open logs, '
        'archive bytes, credentials or outputs through model tools. No Drive consent, GPU, provisioning, '
        'retries or cleanup. Return short status; keep connection tokens private. Cells: '+json.dumps(cells))
    command=['claude','-p','--model','claude-fable-5','--output-format','stream-json','--verbose',
        '--strict-mcp-config','--mcp-config',str(PRIVATE_CONFIG),'--tools','ToolSearch',
        '--allowedTools','mcp__colab-worker__*','--permission-mode','dontAsk','--max-turns','20']
    meta={'status':'FAILED','action':action,'reviewed_commit':revision,
          'cell_sha256':[hashlib.sha256(c.encode()).hexdigest() for c in cells]}
    start=time.monotonic()
    try:
        with (directory/'protocol.jsonl').open('xb') as out,(directory/'stderr.log').open('xb') as err:
            os.chmod(out.name,0o600);os.chmod(err.name,0o600)
            result=subprocess.run(command,input=prompt.encode(),stdout=out,stderr=err,cwd=directory,timeout=400)
        meta['returncode']=result.returncode
        events=[json.loads(s) for s in (directory/'protocol.jsonl').read_text().splitlines()]
        final=[e for e in events if e.get('type')=='result'][-1]
        meta.update(actual_models=list(final.get('modelUsage',{})),usage=final.get('usage'),
                    cli_reported_cost_usd=final.get('total_cost_usd'))
        if result.returncode or final.get('is_error'):raise ValueError('worker did not complete')
        verify_cell_sources(events,cells)
        calls,results=tool_exchanges(events)
        runs=[c for c in calls if c['name'].endswith('__run_code_cell')]
        if json.loads(streams(results[runs[0]['id']]))!={'cpu_only':True,'colab_runtime':True}:
            raise ValueError('CPU Colab required')
        data=json.loads(streams(results[runs[1]['id']]))
        if set(data)!={'status'} or data['status'] not in ['DISPATCHED','STARTING','RUNNING','VALIDATED','FAILED','NOT_VISIBLE']:
            raise ValueError('invalid fixed status')
        meta.update(status='COMPLETE',remote=data)
    except Exception as error:
        # Never expose exception text or remote output: they may contain private information.
        meta['failure_type']=type(error).__name__
    finally:
        meta['wall_seconds']=time.monotonic()-start
        write_private(directory/'status.json',json.dumps(meta,indent=2))
    return meta


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('action',choices=['start','poll'])
    parser.add_argument('--private-dir',type=Path,required=True)
    args=parser.parse_args()
    print(json.dumps(run(args.action,args.private_dir),indent=2))
