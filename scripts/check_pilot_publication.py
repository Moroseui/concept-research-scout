#!/usr/bin/env python3
"""Audit every outgoing pilot commit. Read-only; never pushes or rewrites refs."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess

ROOT=Path(__file__).resolve().parents[1]
BASE='4f5b6b1dc67084a7882c099fb30a6f9465991a31'
CONTAMINATED='940293b6d562f2d3dd6bfd9d8d8281ccf01e4783'
BRANCH='astra/autonomous-isles-pilot'
ALLOWED_PREFIXES=('docs/isles-pilot/','campaigns/isles24-pilot/','tests/')
ALLOWED_FILES={'README.md','scout.py','probes/047/run.py','probes/047/README.md','probes/047/publication.json','probes/047/colab_probe_047.ipynb','ideas/047/registry.yaml','orchestrator/publication.py','orchestrator/publication_subset.py','orchestrator/campaign.py','scripts/rehearse_047_cleanup.py','scripts/efficiency_review.py','scripts/package_pilot.py','scripts/check_pilot_publication.py'}
EXTENSIONS={'.md','.py','.json','.yaml','.ipynb','.txt'}


def audit(tip):
    def git(*a): return subprocess.check_output(['git',*a],cwd=ROOT)
    if git('branch','--show-current').decode().strip()!=BRANCH: raise ValueError('wrong implementation branch')
    if git('status','--porcelain').strip(): raise ValueError('commit all reviewed work before outgoing audit')
    subprocess.run(['git','merge-base','--is-ancestor',BASE,tip],cwd=ROOT,check=True)
    r=subprocess.run(['git','merge-base','--is-ancestor',CONTAMINATED,tip],cwd=ROOT)
    if r.returncode!=1: raise ValueError('contaminated history reachable or ancestry check failed')
    commits=git('rev-list','--reverse',f'{BASE}..{tip}').decode().splitlines(); artifacts=[]
    for commit in commits:
        if len(git('rev-list','--parents','-n','1',commit).split())!=2: raise ValueError('unreviewed merge in outgoing history')
        for raw in git('diff-tree','--no-commit-id','--name-only','-r','-z',commit).split(b'\0'):
            if not raw: continue
            name=raw.decode(); path=Path(name)
            if name not in ALLOWED_FILES and not name.startswith(ALLOWED_PREFIXES): raise ValueError('unpermitted changed path: '+name)
            if path.suffix not in EXTENSIONS or '/results/' in name or '/staged/' in name or '.private/' in name:
                raise ValueError('raw/private artifact in outgoing history')
            exists=subprocess.run(['git','cat-file','-e',f'{commit}:{name}'],cwd=ROOT,stderr=subprocess.DEVNULL)
            if exists.returncode: continue  # deleted file was checked in its introducing commit
            data=git('show',f'{commit}:{name}')
            if len(data)>1500000 or b'\0' in data: raise ValueError('unexpected binary/large artifact')
            if re.search(rb'(?:ghp_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{30,}|sk-[A-Za-z0-9_-]{32,}|-----BEGIN (?:RSA |OPENSSH |EC )?PRIVATE KEY-----)',data):
                raise ValueError('credential-like bytes in outgoing history')
            if path.suffix=='.ipynb':
                nb=json.loads(data)
                if any(c.get('outputs') or c.get('execution_count') is not None for c in nb['cells']):
                    raise ValueError('notebook execution output must remain private until reviewed')
            artifacts.append({'commit':commit,'path':name,'sha256':hashlib.sha256(data).hexdigest()})
    return {'base':BASE,'tip':git('rev-parse',tip).decode().strip(),'branch':BRANCH,'commits':commits,'artifact_versions_checked':len(artifacts),'manifest_sha256':hashlib.sha256(json.dumps(artifacts,sort_keys=True).encode()).hexdigest(),'contaminated_history_reachable':False}

if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__); ap.add_argument('--tip',default='HEAD'); a=ap.parse_args(); print(json.dumps(audit(a.tip),indent=2))
