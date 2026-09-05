"""Bounded P001 Colab discovery and patient dispatch. No changes to scientific pins."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import time
from orchestrator.colab_worker import (ROOT, PRIVATE_CONFIG, NOTEBOOK_PIN, SOURCE_PIN,
                                      capture_cell, private_dir, write_private, git_bytes)

CPU_CELL = """import json, os, shutil
print(json.dumps({'cpu_only': shutil.which('nvidia-smi') is None, 'colab_runtime': bool(os.environ.get('COLAB_RELEASE_TAG'))}))
"""
MOUNT_CELL = "from google.colab import drive\ndrive.mount('/content/drive')\n"

FIND_CELL = """import os, json, time
_candidates = []
_errors = []
_started = time.monotonic()
_complete = True
if os.path.isfile('/content/train.7z'):
    _candidates.append({'path': '/content/train.7z', 'size_bytes': os.stat('/content/train.7z').st_size})
_mounted = os.path.isdir('/content/drive/MyDrive')
for _root in ['/content/drive/MyDrive', '/content/drive/Shareddrives']:
    if not os.path.isdir(_root): continue
    for _directory, _dirs, _files in os.walk(_root, followlinks=False, onerror=lambda e: _errors.append(type(e).__name__)):
        if time.monotonic() - _started > 180:
            _complete = False
            break
        for _name in _files:
            if _name == 'train.7z':
                _path = os.path.join(_directory, _name)
                if not os.path.islink(_path):
                    try: _candidates.append({'path': _path, 'size_bytes': os.stat(_path).st_size})
                    except OSError: _complete = False
print(json.dumps({'drive_mounted': _mounted, 'scan_complete': _complete and not _errors, 'archive_candidates': sorted(_candidates, key=lambda c:c['path'])}))
"""


def worker(packet, destination, timeout=600):
    destination = private_dir(destination)
    write_private(destination/'task.json', json.dumps(packet, indent=2))
    schema = {'type':'object', 'additionalProperties':False,
              'properties':{'status':{'type':'string','enum':['COMPLETE','BLOCKED','FAILED']},
                            'blocker':{'type':'string','enum':['NONE','BROWSER','DRIVE_AUTH','CPU_REQUIRED','TOOLS','CELL_FAILED','OTHER']}},
              'required':['status','blocker']}
    prompt = ("You are a bounded Colab metadata worker, NOT a reviewer. Open the official "
              "colab-worker connection to a CPU runtime. Use a fresh blank notebook, inspect only "
              "with includeOutputs=false. Insert and read back the two supplied cells exactly and "
              "execute them in order. Stop if CPU or Colab check is false. Drive should already be "
              "mounted by the operator; never initiate or inspect consent. Execute the metadata "
              "search even if mount is absent so the fixed status is returned. No archive contents, "
              "patient payloads, extraction, private logs, credentials, other filenames, GPU, "
              "provisioning or cleanup. Return COMPLETE only when the search returns. Packet:\n" + json.dumps(packet))
    if packet['task']=='prepare_drive_consent':
        prompt = ("You are a bounded Colab execution worker. Open the official colab-worker browser "
                  "connection. Use a fresh blank notebook, inspect with includeOutputs=false. Insert "
                  "the two supplied cells exactly. Read back sources before executing ONLY cell 1, the "
                  "CPU check. If CPU and Colab are true, leave cell 2 (plain drive.mount) UNEXECUTED for "
                  "the operator to run and grant Google consent in the browser. Do not capture, read "
                  "or store authorization output. Return BLOCKED with DRIVE_AUTH after preparing the "
                  "mount cell. No metadata scan or patient execution in this task. Packet:\n" + json.dumps(packet))
    elif packet['task']=='execute_reviewed_p001':
        require_patient_review()
        prompt = ("You are a bounded execution worker, NOT a reviewer. The P001 patient dispatch "
                  "has passed independent review. Open the official colab-worker connection to the "
                  "operator-authorized CPU runtime with Drive mounted. Use a fresh blank notebook, "
                  "inspect cells with includeOutputs=false. Insert ONLY packet.cells exactly, read back "
                  "each source before running it, execute in order. Do not execute original_notebook "
                  "cells directly, launch_source separately, or any other code. Never alter code or "
                  "parameters. Stop on any failure. The launcher starts a private background process; "
                  "COMPLETE means dispatched, NOT scientific success. Never read logs, images, "
                  "checkpoints, archive bytes, private JSON, or existing outputs through model tools. "
                  "No GPU, provisioning, downloads, cleanup or shell tools. If Drive/browser approval "
                  "is needed return BLOCKED. Never retry launch. Return structured status only. Packet:\n" + json.dumps(packet))
    elif packet['task']=='poll_p001':
        prompt = ("Use colab-worker official connection and a fresh blank notebook (inspect with "
                  "includeOutputs=false). Execute only the supplied CPU and fixed status cells in "
                  "order after source readback. Do not mount Drive, retry execution, inspect data, "
                  "private outputs or logs. NOT_VISIBLE means operator access is needed. No GPU or "
                  "provisioning. Return status COMPLETE only if both cells complete. Packet:\n" + json.dumps(packet))
    command=['claude','-p','--model','claude-fable-5','--output-format','stream-json','--verbose',
             '--mcp-config',str(PRIVATE_CONFIG),'--strict-mcp-config','--tools','ToolSearch',
             '--allowedTools','mcp__colab-worker__*','--permission-mode','dontAsk',
             '--max-turns','30','--json-schema',json.dumps(schema)]
    start=time.monotonic(); code=None
    with (destination/'protocol.jsonl').open('xb') as out,(destination/'stderr.log').open('xb') as err:
        os.chmod(out.name,0o600);os.chmod(err.name,0o600)
        try: code=subprocess.run(command,input=prompt.encode(),stdout=out,stderr=err,cwd=destination,timeout=timeout).returncode
        except (OSError,subprocess.TimeoutExpired):pass
    meta={'status':'FAILED','returncode':code,'wall_seconds':time.monotonic()-start,'task':packet['task']}
    try:
        events=[json.loads(l) for l in (destination/'protocol.jsonl').read_text().splitlines() if l.strip()]
        final=[e for e in events if e.get('type')=='result']
        if len(final)!=1 or code!=0 or final[0].get('is_error') or final[0].get('subtype')!='success': raise ValueError('incomplete worker')
        result=final[0]['structured_output']
        if result['status'] not in ['COMPLETE','BLOCKED','FAILED'] or result['blocker'] not in schema['properties']['blocker']['enum']:raise ValueError('invalid status')
        actual_models=list(final[0].get('modelUsage',{}))
        if not actual_models or any(not m.startswith('claude-') for m in actual_models):raise ValueError('worker model mismatch')
        meta['requested_model']='claude-fable-5';meta['actual_models']=actual_models
        meta.update(result)
        meta['usage']=final[0].get('usage');meta['cli_reported_cost_usd']=final[0].get('total_cost_usd')
        if result['status']=='COMPLETE':
            verify_cell_sources(events, packet['cells'])
            if packet['task']=='locate_existing_archive':meta['discovery']=verify_discovery(events)
            else:
                calls,results=tool_exchanges(events)
                runs=[c for c in calls if c['name'].endswith('__run_code_cell')]
                cpu=json.loads(streams(results[runs[0]['id']]))
                if cpu!={'cpu_only':True,'colab_runtime':True}:raise ValueError('CPU Colab required')
                if packet['task']=='execute_reviewed_p001':
                    import ast
                    last=ast.literal_eval(streams(results[runs[-1]['id']]).strip())
                    if last != {'transport_status':'COMPLETE','source_sha256':hashlib.sha256(packet['launch_source'].encode()).hexdigest()}:raise ValueError('launch did not complete')
                    meta['job_status']='DISPATCHED_NOT_YET_VALIDATED'
                else:
                    status=json.loads(streams(results[runs[-1]['id']]))
                    if set(status)!={'status'} or status['status'] not in ['STARTING','RUNNING','VALIDATED','FAILED','NOT_VISIBLE','INVALID_STATUS']:raise ValueError('invalid job status')
                    meta['job_status']=status['status']
    except (ValueError,KeyError,TypeError,AttributeError,IndexError):meta['status']='FAILED'
    write_private(destination/'status.json',json.dumps(meta,indent=2))
    return meta


def tool_exchanges(events):
    calls=[];results={}
    for event in events:
        for b in event.get('message',{}).get('content',[]):
            if not isinstance(b,dict):continue
            if event.get('type')=='assistant' and b.get('type')=='tool_use' and b.get('name','').startswith('mcp__colab-worker__'):calls.append(b)
            if event.get('type')=='user' and b.get('type')=='tool_result' and b.get('tool_use_id') in {c['id'] for c in calls}:
                if b.get('is_error'):raise ValueError('MCP error')
                content=b['content']
                if isinstance(content,list):content=''.join(x['text'] for x in content if x.get('type')=='text')
                results[b['tool_use_id']]=json.loads(content)
    return calls,results


def verify_cell_sources(events, sources):
    calls, results = tool_exchanges(events)
    code = {}; readbacks = {}; runs = []
    for call in calls:
        name = call['name']; args = call['input']
        if name.endswith('__get_cells'):
            if args.get('includeOutputs') is not False: raise ValueError('outputs must not be read')
            for cell in results[call['id']]['cells']:
                readbacks[cell['id']] = ''.join(cell['source'])
        elif name.endswith('__add_code_cell'):
            code[results[call['id']]['newCellId']] = args['code']
        elif name.endswith('__update_cell'):
            code[args['cellId']] = args['content']; readbacks.pop(args['cellId'],None)
        elif name.endswith(('__delete_cell','__move_cell')):
            raise ValueError('unexpected notebook mutation')
        elif name.endswith('__run_code_cell'):
            index=len(runs); cell=args['cellId']
            if index>=len(sources) or code.get(cell)!=sources[index] or readbacks.get(cell)!=sources[index]:
                raise ValueError('executed source not bound to packet and readback')
            streams(results[call['id']])  # Reject any remote error, including nested wrappers.
            runs.append(call)
    if len(runs)!=len(sources): raise ValueError('execution sequence incomplete')


def streams(result):
    if any(o.get('output_type')=='error' for o in result['outputs']):raise ValueError('remote cell error')
    return ''.join(''.join(o.get('text',[])) for o in result['outputs'] if o.get('output_type')=='stream')


def verify_discovery(events):
    calls,results=tool_exchanges(events)
    runs=[c for c in calls if c['name'].endswith('__run_code_cell')]
    if len(runs)!=2:raise ValueError('discovery sequence incomplete')
    cpu=json.loads(streams(results[runs[0]['id']]))
    if cpu!={'cpu_only':True,'colab_runtime':True}:raise ValueError('CPU Colab required')
    result=json.loads(streams(results[runs[1]['id']]))
    if set(result)!={'drive_mounted','scan_complete','archive_candidates'}:raise ValueError('unexpected metadata')
    if type(result['drive_mounted']) is not bool or type(result['scan_complete']) is not bool:raise ValueError('invalid scan status')
    if not isinstance(result['archive_candidates'],list):raise ValueError('invalid candidate list')
    for row in result['archive_candidates']:
        if set(row)!={'path','size_bytes'} or not isinstance(row['path'],str):raise ValueError('invalid candidate')
        if not row['path'].startswith('/content/') or not row['path'].endswith('/train.7z') or any(ord(c)<32 for c in row['path']):raise ValueError('invalid archive path')
        if type(row['size_bytes']) is not int or row['size_bytes']<0:raise ValueError('invalid size')
    return result


OUTPUT = "/content/drive/MyDrive/isles-pilot/P001-v1"
REVIEW_DIR = ROOT / "docs/isles-pilot/reviews"
REVIEW_PREFIX = "p001-dispatch-approved"
REVIEW_FILES = ["orchestrator/colab_patient.py", "orchestrator/colab_worker.py",
                "tests/test_colab_patient.py", "docs/isles-pilot/P001_WORKER_DISPATCH.md",
                "campaigns/isles24-pilot/experiments/P001/run.py",
                "campaigns/isles24-pilot/experiments/P001/validate_return.py",
                "campaigns/isles24-pilot/experiments/P001/SPEC.md",
                "campaigns/isles24-pilot/experiments/P001/colab_P001.ipynb",
                "orchestrator/publication.py"]


def require_patient_review():
    from orchestrator.campaign_review import verify_receipt
    exp = ROOT / "campaigns/isles24-pilot/experiments/P001"
    verify_receipt(ROOT, exp, json.loads((exp / "review.json").read_text()))
    execution = json.loads((REVIEW_DIR / (REVIEW_PREFIX+".execution.json")).read_text())
    response_path = REVIEW_DIR / (REVIEW_PREFIX+".response.json")
    response = json.loads(response_path.read_text())
    verdict = response.get("structured_output", {})
    if (execution.get("returncode") != 0 or response.get("subtype") != "success"
            or response.get("is_error") or verdict.get("verdict") != "APPROVE"
            or verdict.get("scope") != "p001-patient-dispatch"
            or verdict.get("reviewed_commit") != execution.get("reviewed_commit")
            or "claude-fable-5" not in response.get("modelUsage", {})
            or hashlib.sha256(response_path.read_bytes()).hexdigest() != execution.get("response_sha256")):
        raise ValueError("completed patient-dispatch review required")
    for name in REVIEW_FILES:
        if hashlib.sha256((ROOT/name).read_bytes()).hexdigest() != execution["input_file_sha256"].get(name):
            raise ValueError("patient-dispatch review binding differs")
    return execution["reviewed_commit"]


def archive_path(path):
    if not isinstance(path,str) or not path.startswith('/content/') or not path.endswith('/train.7z') or any(ord(c)<32 for c in path):
        raise ValueError('actual Colab train.7z path required')
    if '..' in Path(path).parts: raise ValueError('archive path must be canonical')
    return path


def child_script(nb, params):
    """Private process runs unchanged reviewed science, then original semantic validator."""
    cells = [''.join(nb['cells'][i]['source']) for i in (3,4,5)]
    return "\n".join([
        'import json, os, sys, subprocess, traceback, hashlib, importlib.util',
        'from pathlib import Path',
        'params = '+repr(params),
        "REPO = Path(params['repo']); OUTPUT = Path(params['output']); ARCHIVE = Path(params['archive']); DATA_ROOT = None",
        "sys.path.insert(0,str(REPO))",
        "job = Path(str(OUTPUT)+'.worker')",
        "def state(value):",
        "    temporary = job/'status.tmp'; temporary.write_text(json.dumps(value)); os.replace(temporary,job/'status.json')",
        "try:",
        "    state({'status':'RUNNING'})",
        *['    exec(compile('+repr(cell)+", 'pinned-p001-cell-"+str(i)+"', 'exec'), globals())" for i,cell in zip((3,4,5),cells)],
        "    path = EXPERIMENT/'validate_return.py'",
        "    spec = importlib.util.spec_from_file_location('p001_return_validator',path)",
        "    validator = importlib.util.module_from_spec(spec); spec.loader.exec_module(validator)",
        "    validation = validator.verify(OUTPUT,Path(str(OUTPUT)+'.private'),Path(str(OUTPUT)+'.console.log'))",
        "    snapshot = {}",
        "    for name, expected_hash in validation['file_sha256'].items():",
        "        raw = (OUTPUT/name).read_bytes()",
        "        if hashlib.sha256(raw).hexdigest() != expected_hash: raise ValueError('aggregate changed during capture')",
        "        snapshot[name] = raw.decode('utf-8')",
        "    artifact = {'status':'VALIDATED','notebook_pin':params['notebook_pin'],'source_pin':params['source_pin'],'validation':validation,'aggregate_files':snapshot}",
        "    (job/'validated_return.json').write_text(json.dumps(artifact))",
        "    import zipfile",
        "    private = Path(str(OUTPUT)+'.private')",
        "    with zipfile.ZipFile(job/'P001-private-return.zip','w',compression=zipfile.ZIP_DEFLATED) as z:",
        "        for name in snapshot: z.write(OUTPUT/name,'bundle/'+name)",
        "        z.write(Path(str(OUTPUT)+'.console.log'),'console.log')",
        "        for name in ['binding.json','checkpoint_index.json']: z.write(private/name,'private/'+name)",
        "        for folder in ['checkpoints','predictions','failed_attempts']:",
        "            if (private/folder).exists():",
        "                for path in sorted((private/folder).rglob('*')):",
        "                    if path.is_symlink(): raise ValueError('symlink in private return')",
        "                    if path.is_file(): z.write(path,'private/'+path.relative_to(private).as_posix())",
        "    state({'status':'VALIDATED'})",
        "except BaseException:",
        "    traceback.print_exc()",
        "    state({'status':'FAILED'})",
        "    sys.exit(1)",
    ])


def execution_packet(archive):
    reviewed = require_patient_review()
    archive = archive_path(archive)
    raw = git_bytes(NOTEBOOK_PIN,'campaigns/isles24-pilot/experiments/P001/colab_P001.ipynb')
    nb = json.loads(raw)
    params={'archive':archive,'output':OUTPUT,'repo':'/content/scout-pilot-'+SOURCE_PIN[:12],
            'source_pin':SOURCE_PIN,'notebook_pin':NOTEBOOK_PIN,'adapter_reviewed_commit':reviewed,
            'notebook_sha256':hashlib.sha256(raw).hexdigest()}
    launch = "\n".join([
        'import os, json, sys, subprocess, shutil', 'from pathlib import Path',
        "if shutil.which('nvidia-smi') is not None: raise RuntimeError('CPU runtime required')",
        "if not os.path.isdir('/content/drive/MyDrive'): raise RuntimeError('Drive authorization required')",
        "if shutil.which('7z') is None: raise RuntimeError('Existing 7z prerequisite unavailable')",
        'params = '+repr(params),
        "if not Path(params['archive']).is_file(): raise RuntimeError('Archive path unavailable')",
        "job = Path(params['output']+'.worker')",
        "if job.exists() or job.is_symlink(): raise RuntimeError('Existing job evidence; poll instead of relaunching')",
        "job.mkdir(mode=0o700)",
        "(job/'parameters.json').write_text(json.dumps(params))",
        "(job/'original_notebook.ipynb').write_text("+repr(raw.decode())+")",
        "(job/'status.json').write_text(json.dumps({'status':'STARTING'}))",
        # Acquisition is exact pinned source, but executed with the existing reviewed private capture wrapper.
        'exec(compile('+repr(capture_cell(''.join(nb['cells'][1]['source']),OUTPUT+'.worker/acquisition.console.log'))+", 'supplementary-acquisition-transport', 'exec'), globals())",
        "(job/'run.py').write_text("+repr(child_script(nb,params))+")",
        "with (job/'transport.console.log').open('ab',buffering=0) as console:",
        "    process = subprocess.Popen([sys.executable,str(job/'run.py')],stdout=console,stderr=subprocess.STDOUT,start_new_session=True)",
        "(job/'process.json').write_text(json.dumps({'pid':process.pid}))",
        "print(json.dumps({'status':'DISPATCHED','notebook_pin':params['notebook_pin'],'source_pin':params['source_pin']}))",
    ])
    launch = "_p001_owned = False\ntry:\n" + '\n'.join('    '+line for line in launch.replace("job.mkdir(mode=0o700)", "job.mkdir(mode=0o700)\n_p001_owned = True").splitlines()) + "\nexcept BaseException:\n    if _p001_owned: (job/'status.json').write_text(json.dumps({'status':'FAILED'}))\n    raise"
    # Launcher errors/source paths never go to MCP. Original launch source and wrapper are separate.
    wrapper = capture_cell(launch,OUTPUT+'.launch.console.log')
    return {'task':'execute_reviewed_p001','parameters':params,'cells':[CPU_CELL,wrapper],
            'launch_source':launch,'original_notebook':nb,
            'poll_source':poll_cell()}


def poll_cell():
    return "\n".join([
        'import json, os', 'from pathlib import Path',
        'job = Path('+repr(OUTPUT+'.worker')+')',
        "if not job.is_dir():",
        "    print(json.dumps({'status':'NOT_VISIBLE'}))",
        "else:",
        "    status = json.loads((job/'status.json').read_text())",
        "    value = status.get('status')",
        "    if value not in ['STARTING','RUNNING','VALIDATED','FAILED']: value='INVALID_STATUS'",
        "    print(json.dumps({'status':value}))",
    ])


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('mode',choices=['mount','locate','prepare','dispatch','poll'])
    ap.add_argument('--archive')
    ap.add_argument('--private-dir',type=Path,required=True)
    args=ap.parse_args()
    if args.mode=='mount': packet={'task':'prepare_drive_consent','cells':[CPU_CELL,MOUNT_CELL]}
    elif args.mode=='locate': packet={'task':'locate_existing_archive','cells':[CPU_CELL,FIND_CELL]}
    elif args.mode=='poll': packet={'task':'poll_p001','cells':[CPU_CELL,poll_cell()]}
    else:
        if not args.archive: ap.error('--archive required')
        packet=execution_packet(args.archive)
        if args.mode=='prepare':
            dest=private_dir(args.private_dir);write_private(dest/'task.json',json.dumps(packet,indent=2))
            print(json.dumps({'status':'PATIENT_PACKET_PREPARED','reviewed_commit':packet['parameters']['adapter_reviewed_commit']}));return
    print(json.dumps(worker(packet,args.private_dir),indent=2))

if __name__=='__main__':main()
