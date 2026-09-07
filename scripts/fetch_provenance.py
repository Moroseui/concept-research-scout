"""Fetch only reviewed exact provenance snapshots; no branch checkout or broad ref fetch."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
# Keep the documented direct script invocation usable as well as module import.
import sys
if __package__ in (None, ''):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from orchestrator.git_diagnostics import run as git_run, output as git_output


def retrieve(root, manifest, fetch=False):
    data=json.loads(Path(manifest).read_text())
    if set(data)!={'version','objects'} or data['version']!=1 or not 1<=len(data['objects'])<=16:
        raise ValueError('bounded provenance manifest required')
    entries=data['objects']
    for e in entries:
        if set(e)!={'commit','path','sha256'} or not re.fullmatch('[0-9a-f]{40}',e['commit']) or not re.fullmatch('ideas/[0-9]{3}/HUMAN_APPROVED_PROBE',e['path']) or not re.fullmatch('[0-9a-f]{64}',e['sha256']):
            raise ValueError('exact commit/approval artifact binding required')
        if e['commit']=='940293b6d562f2d3dd6bfd9d8d8281ccf01e4783':raise ValueError('contaminated source prohibited')
    receipts=[]
    for e in entries:
        present=git_run(['git','cat-file','-e',e['commit']+'^{commit}'],cwd=root,capture_output=True,timeout=30).returncode==0
        if not present:
            if not fetch:raise ValueError('GIT_OBJECT_UNAVAILABLE: '+e['commit'])
            git_run(['git','-c','credential.helper=', '-c','credential.helper=!gh auth git-credential',
                            'fetch','--no-tags','--depth=1','--filter=blob:none','origin',e['commit']],cwd=root,check=True,timeout=180)
        raw=git_output(['git','-c','credential.helper=', '-c','credential.helper=!gh auth git-credential','show',e['commit']+':'+e['path']],cwd=root,timeout=60)
        if hashlib.sha256(raw).hexdigest()!=e['sha256']:raise ValueError('provenance artifact bytes differ')
        receipts.append({**e,'fetched':not present,'status':'VERIFIED'})
    return receipts


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--manifest',default='configs/pilot/provenance-objects.json');p.add_argument('--fetch',action='store_true');a=p.parse_args()
    print(json.dumps(retrieve(Path.cwd(),a.manifest,a.fetch),indent=2))
