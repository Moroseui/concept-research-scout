"""Thin CPU-Colab preflight cells: pinned acquisition, private launch, separate retrieval.

These are supplementary readiness cells, not edits to the frozen P001 notebook.
Generation is not permission to execute: the preparation pin must contain a valid
fresh transport-review receipt, and the operator-approved input scope still applies.
"""
import argparse
import hashlib
import inspect
import json
from pathlib import Path
import re
from orchestrator.colab_worker import SOURCE_PIN, capture_cell
from orchestrator.colab_patient import CPU_CELL
from scripts.p001_input_preflight import reconcile_runtime

REVIEW_PATH='docs/science/P001_PREFLIGHT_TRANSPORT_REVIEW_20260907.json'
REVIEW_FILES=['scripts/p001_input_preflight.py','orchestrator/p001_preflight_transport.py','orchestrator/colab_session_worker.py']


def public_receipt(value):
    """Exact aggregate schema, including values; never echo unknown private text."""
    common={'status','prediction_executed','labels_opened','reserved_access','elapsed_seconds'}
    success={'archive_size','archive_md5','eligible_cohort_verified','admission_members_checked',
             'selection_rule','headers_sha256','unit_semantics','launch_authorized'}
    if not isinstance(value,dict) or value.get('status') not in ['FAILED','INPUT_INTEGRITY_AND_HEADERS_VERIFIED']:
        raise ValueError('PREFLIGHT_TRANSPORT_RECEIPT_REJECTED')
    if set(value)!=common|({'failure_type'} if value['status']=='FAILED' else success):
        raise ValueError('PREFLIGHT_TRANSPORT_RECEIPT_REJECTED')
    if any(value[k] is not False for k in ['prediction_executed','labels_opened','reserved_access']):
        raise ValueError('PREFLIGHT_TRANSPORT_RECEIPT_REJECTED')
    seconds=value['elapsed_seconds']
    if type(seconds) not in [int,float] or not 0<=seconds<86400:
        raise ValueError('PREFLIGHT_TRANSPORT_RECEIPT_REJECTED')
    if value['status']=='FAILED':
        if value['failure_type'] not in ['ValueError','TimeoutError','TimeoutExpired','CalledProcessError','OSError','FileNotFoundError','PermissionError','ImageFileError','EOFError','BadGzipFile']:
            raise ValueError('PREFLIGHT_TRANSPORT_RECEIPT_REJECTED')
    else:
        expected={'archive_size':99014629647,'archive_md5':'36ae28b9a17f7340b8bbef62b595cb57',
                  'eligible_cohort_verified':99,'admission_members_checked':1,
                  'selection_rule':'first_lexical_eligible_id_no_outcome_selection',
                  'unit_semantics':'HEADER_EVIDENCE_ONLY_REQUIRES_RELEASE_PROVENANCE_ASSESSMENT',
                  'launch_authorized':False}
        if any(value[k]!=v or type(value[k])!=type(v) for k,v in expected.items()):
            raise ValueError('PREFLIGHT_TRANSPORT_RECEIPT_REJECTED')
        sha=value['headers_sha256']
        if not isinstance(sha,str) or not re.fullmatch('[0-9a-f]{64}',sha):
            raise ValueError('PREFLIGHT_TRANSPORT_RECEIPT_REJECTED')
    return value


def cells(pin, archive, job):
    if not re.fullmatch('[0-9a-f]{40}',pin):raise ValueError('EXACT_PREPARATION_PIN')
    if not archive.startswith('/content/drive/MyDrive/isles-pilot/') or not archive.endswith('/train.7z') or '..' in Path(archive).parts:raise ValueError('PRESERVED_ARCHIVE_PATH_REQUIRED')
    if not re.fullmatch('/content/drive/MyDrive/isles-pilot/p001-preflight-[a-f0-9]{32}',job):raise ValueError('FRESH_PRIVATE_PREFLIGHT_PATH')
    frozen='/content/scout-pilot-'+SOURCE_PIN[:12]
    support='/content/p001-preflight-support-'+pin[:12]
    mount="from google.colab import drive\ndrive.mount('/content/drive')\n"
    # The worker leaves this consent cell unexecuted. The operator may use it only
    # if needed for this existing Colab input route; it does not grant broad scans.
    setup="\n".join([
        'import os, json, subprocess, sys, hashlib, shutil', 'from pathlib import Path', inspect.getsource(reconcile_runtime),
        'job=Path('+repr(job)+'); support=Path('+repr(support)+'); frozen=Path('+repr(frozen)+')',
        "assert os.path.ismount('/content/drive'), 'Drive authorization required'",
        "assert Path("+repr(archive)+").is_file(), 'Existing archive unavailable'",
        "if support.exists(): raise RuntimeError('Existing preparation requires reconciliation')",
        "assert reconcile_runtime(Path('/content/drive/MyDrive/isles-pilot/P001-v1'))['disposition']=='NO_MATCH_IN_CHECKED_RUNTIME_AND_PATHS', 'Existing execution requires reconciliation'",
        "def acquire(path,pin,names):",
        "    if path.exists():",
        "        actual=subprocess.check_output(['git','-C',str(path),'rev-parse','HEAD'],text=True,timeout=30).strip()",
        "        if actual!=pin: raise RuntimeError('Existing source differs; preserve it')",
        "    else:",
        "        path.mkdir()",
        "        subprocess.run(['git','init','-q',str(path)],check=True,timeout=30)",
        "        subprocess.run(['git','-C',str(path),'remote','add','origin','https://github.com/Moroseui/concept-research-scout.git'],check=True,timeout=30)",
        "        subprocess.run(['git','-C',str(path),'fetch','--no-tags','--filter=blob:none','--depth=1','origin',pin],check=True,timeout=300)",
        "        subprocess.run(['git','-C',str(path),'sparse-checkout','set','--no-cone',*names],check=True,timeout=300)",
        "        subprocess.run(['git','-C',str(path),'checkout','--detach','FETCH_HEAD'],check=True,timeout=300)",
        "    for name in names:",
        "        f=path/name",
        "        assert not any(p.is_symlink() for p in [f,*f.parents]), 'Source symlink rejected'",
        "        raw=f.read_bytes()",
        "        expected=subprocess.check_output(['git','-C',str(path),'rev-parse',pin+':'+name],text=True,timeout=30).strip()",
        "        assert hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\\0'+raw).hexdigest()==expected, 'Existing source bytes changed'",
        'acquire(frozen,'+repr(SOURCE_PIN)+','+repr(['campaigns/isles24-pilot/experiments/P001/run.py','orchestrator/__init__.py','orchestrator/campaign.py','probes/046/results/results_v3/per_case_contributions.csv','probes/023/results/results_v2/archive_manifest.csv'])+')',
        'acquire(support,'+repr(pin)+','+repr(REVIEW_FILES+[REVIEW_PATH,'campaigns/isles24-pilot/prediction_selection.json'])+')',
        'review=json.loads((support/'+repr(REVIEW_PATH)+').read_text())',
        "assert review['review']['verdict']=='APPROVE' and review['execution']['returncode']==0",
        "assert review['review']['reviewed_commit']==review['execution']['reviewed_commit']",
        "assert 'claude-fable-5' in review['execution']['assistant_message_models']",
        'for name in '+repr(REVIEW_FILES)+':',
        "    assert hashlib.sha256((support/name).read_bytes()).hexdigest()==review['execution']['input_file_sha256'][name]",
        "if shutil.which('7z') is None:",
        "    subprocess.run(['apt-get','-qq','update'],check=True,timeout=180)",
        "    subprocess.run(['apt-get','-qq','install','-y','p7zip-full'],check=True,timeout=180)",
        "subprocess.run([sys.executable,'-m','pip','install','--target',str(support/'dependencies'),'numpy==2.3.3','nibabel==5.3.2'],check=True,timeout=600)",
    ])
    launch="\n".join([
        'import os, json, subprocess, sys', 'from pathlib import Path', 'os.umask(0o077)',
        'job=Path('+repr(job)+'); support=Path('+repr(support)+')',
        "intent=job/'launch-intent.json'",
        "with intent.open('x') as f: json.dump({'status':'DISPATCH_INTENT_NO_AUTOMATIC_RETRY'},f); f.flush(); os.fsync(f.fileno())",
        "env={k:os.environ[k] for k in ['PATH','LANG','COLAB_RELEASE_TAG'] if k in os.environ}",
        "env.update(HOME=str(job),PYTHONPATH=str(support/'dependencies'),PYTHONDONTWRITEBYTECODE='1')",
        "with (job/'preflight.console.log').open('xb') as log:",
        "    os.chmod(log.name,0o600)",
        "    process=subprocess.Popen([sys.executable,str(support/'scripts/p001_input_preflight.py'),'--source-root',"+repr(frozen)+",'--approval',str(support/'campaigns/isles24-pilot/prediction_selection.json'),'--archive',"+repr(archive)+",'--attempt',str(job/'attempt'),'--execution-root','/content/drive/MyDrive/isles-pilot/P001-v1'],stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT,env=env,start_new_session=True)",
        "with (job/'process.json').open('x') as f: json.dump({'pid':process.pid,'status':'DISPATCHED_NOT_COMPLETED'},f)",
    ])
    prepare="\n".join(['import os','from pathlib import Path',"assert os.path.ismount('/content/drive'), 'Drive required'",'Path('+repr(job)+').mkdir(mode=0o700)'])
    retrieval="\n".join([
        'import json, hashlib, os, re', 'from pathlib import Path', inspect.getsource(public_receipt),
        'job=Path('+repr(job)+')',"p=job/'attempt/receipt.json'",
        "if not os.path.ismount('/content/drive'): print(json.dumps({'status':'NOT_VISIBLE_RECONCILE'}))",
        "elif not p.is_file(): print(json.dumps({'status':'NO_TERMINAL_RECEIPT_RECONCILE_DO_NOT_RETRY'}))",
        "else:","    r=json.loads(p.read_text())",
        "    r=public_receipt(r)",
        "    print(json.dumps({'receipt':r,'receipt_sha256':hashlib.sha256(p.read_bytes()).hexdigest()}))",
    ])
    wrapped_setup=capture_cell(setup,job+'/setup.console.log')
    wrapped_launch=capture_cell(launch,job+'/launch.console.log')
    return [CPU_CELL,mount,prepare,wrapped_setup,wrapped_launch,retrieval]


def notebook(pin, archive, job):
    sources=cells(pin,archive,job)
    labels=['Check the CPU runtime.','Optional Drive authorization: skip if already mounted.','Create a fresh private preflight directory.','Acquire exact source commits and isolated dependencies; original console stays private.','Start only the authorized admission preflight. This does not launch P001.','Run separately after completion to retrieve the checked aggregate receipt. Missing receipt does not mean no execution.']
    result=[{'cell_type':'markdown','metadata':{},'source':['# P001 input preflight — patient launch remains held\n','Use a CPU Colab runtime and the existing preserved archive. These readiness cells leave the approved scientific notebook unchanged. Run consent yourself if needed; do not Run All blindly after a disconnect.']}]
    for label,source in zip(labels,sources):
        compile(source,'preflight-notebook','exec')
        result += [{'cell_type':'markdown','metadata':{},'source':[label]}, {'cell_type':'code','metadata':{},'source':source.splitlines(keepends=True),'execution_count':None,'outputs':[]}]
    return {'nbformat':4,'nbformat_minor':5,'metadata':{'kernelspec':{'name':'python3','display_name':'Python 3'},'preparation_source':pin,'frozen_scientific_source':SOURCE_PIN},'cells':result}


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--source',required=True);p.add_argument('--archive',required=True);p.add_argument('--job',required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args()
    with a.output.open('x') as f:json.dump(notebook(a.source,a.archive,a.job),f,indent=2)
