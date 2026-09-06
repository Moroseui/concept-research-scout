#!/usr/bin/env python3
"""Audit every outgoing pilot commit. Read-only; never pushes or rewrites refs."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

ROOT=Path(__file__).resolve().parents[1]
BASE='4f5b6b1dc67084a7882c099fb30a6f9465991a31'
CONTAMINATED='940293b6d562f2d3dd6bfd9d8d8281ccf01e4783'
BRANCH='astra/autonomous-isles-pilot'
ALLOWED_PREFIXES=('docs/isles-pilot/','campaigns/isles24-pilot/','tests/')
ALLOWED_FILES={'README.md','scout.py','probes/047/run.py','probes/047/README.md','probes/047/publication.json','probes/047/colab_probe_047.ipynb','ideas/047/registry.yaml','ideas/047/state.json','ideas/047/CARD.md','orchestrator/publication.py','orchestrator/publication_subset.py','orchestrator/campaign.py','orchestrator/campaign_lifecycle.py','orchestrator/campaign_review.py','scripts/rehearse_047_cleanup.py','scripts/efficiency_review.py','scripts/package_pilot.py','scripts/check_pilot_publication.py'}
ALLOWED_FILES.update({'orchestrator/__init__.py','scripts/pilot_review.py','scripts/pilot_tool_guard.py','scripts/future_worker_profile.py','orchestrator/pilot_jobs.py','configs/pilot/agents-unattended.toml','configs/pilot/colab-worker-future.json'})
ALLOWED_FILES.update({'orchestrator/campaign_pipeline.py', '.github/workflows/actioner.yml', 'orchestrator/job_store.py', 'orchestrator/colab_acquire.py', '.github/workflows/scout-cycle.yml', '.github/workflows/librarian.yml', '.github/workflows/interpret.yml', 'scripts/colab_archive_acquire.py', 'scripts/p001_handoff_watch.py', '.github/workflows/results-validate.yml', '.github/workflows/idea-pipeline.yml', 'orchestrator/colab_worker.py', 'scripts/colab_archive_metadata.py', '.github/workflows/check.yml', '.github/workflows/confer.yml', 'orchestrator/colab_patient.py', 'scripts/workflow_boundary.py'})

ALLOWED_FILES.update({'scripts/colab_archive_preserve.py','orchestrator/archive_preserve.py','scripts/fetch_provenance.py','orchestrator/experiment_registry.py','configs/pilot/provenance-objects.json','ideas/023/state.json','ideas/045/state.json','ideas/046/state.json'})

ALLOWED_FILES.update({'scripts/verify_main_integration.py','orchestrator/actions_runner.py','orchestrator/human_controls.py','scripts/actions_agent.py','scripts/actions_auth.py','scripts/render_human_workflows.py','configs/pilot/human-controls.json','.github/workflows/research-control.yml'})

ALLOWED_FILES.update({'orchestrator/git_publication.py','orchestrator/public_export.py','orchestrator/dispatch_limiter.py','configs/pilot/dispatch-limiter.json','scripts/closeout_evidence.py','scripts/measure_dispatch.py','evidence/decisions.md'})

EXTENSIONS={'.yml','.toml','.fish','.md','.py','.json','.yaml','.ipynb','.txt','.jsonl'}


def audit(tip):
    def git(*a): return subprocess.check_output(['git',*a],cwd=ROOT)
    if git('branch','--show-current').decode().strip()!=BRANCH: raise ValueError('wrong implementation branch')
    if git('status','--porcelain').strip(): raise ValueError('commit all reviewed work before outgoing audit')
    subprocess.run(['git','merge-base','--is-ancestor',BASE,tip],cwd=ROOT,check=True)
    r=subprocess.run(['git','merge-base','--is-ancestor',CONTAMINATED,tip],cwd=ROOT)
    if r.returncode!=1: raise ValueError('contaminated history reachable or ancestry check failed')
    commits=git('rev-list','--reverse',f'{BASE}..{tip}').decode().splitlines(); artifacts=[]
    for commit in commits:
        from orchestrator.git_publication import scan_commit
        scan_commit(git('cat-file','commit',commit))
        if len(git('rev-list','--parents','-n','1',commit).split())!=2: raise ValueError('unreviewed merge in outgoing history')
        tree={}
        for entry in git('ls-tree','-r','-z',commit).split(b'\0'):
            if entry:
                metadata,tree_name=entry.split(b'\t',1);tree[tree_name]=metadata.split()
        for raw in git('diff-tree','--no-commit-id','--name-only','-r','-z',commit).split(b'\0'):
            if not raw: continue
            name=raw.decode(); path=Path(name)
            if name not in ALLOWED_FILES and not name.startswith(ALLOWED_PREFIXES): raise ValueError('unpermitted changed path: '+name)
            if (path.suffix not in EXTENSIONS or any(part.startswith(('results','staged','.private')) for part in path.parts[:-1])
                or (path.name.startswith(('results','staged','.private')) and name not in ALLOWED_FILES)):
                raise ValueError('raw/private artifact in outgoing history')
            entry=tree.get(raw)
            if entry is None:continue  # byte-exact tree absence, a real deletion
            mode=entry[0]
            if mode not in (b'100644',b'100755'):raise ValueError('non-regular publication artifact')
            data=git('cat-file','blob',entry[2].decode())
            from orchestrator.git_publication import scan
            scan(name,data)
            if len(data)>1500000 or b'\0' in data: raise ValueError('unexpected binary/large artifact')
            if re.search(rb'(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{30,}|sk-[A-Za-z0-9_-]{32,}|-----BEGIN (?:RSA |OPENSSH |EC )?PRIVATE KEY-----)',data):
                raise ValueError('credential-like bytes in outgoing history')
            if path.suffix=='.ipynb':
                nb=json.loads(data)
                if any(c.get('outputs') or c.get('execution_count') is not None for c in nb['cells']):
                    raise ValueError('notebook execution output must remain private until reviewed')
            artifacts.append({'commit':commit,'path':name,'sha256':hashlib.sha256(data).hexdigest()})
    return {'base':BASE,'tip':git('rev-parse',tip).decode().strip(),'branch':BRANCH,'commits':commits,'artifact_versions_checked':len(artifacts),'manifest_sha256':hashlib.sha256(json.dumps(artifacts,sort_keys=True).encode()).hexdigest(),'contaminated_history_reachable':False}

if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__); ap.add_argument('--tip',default='HEAD'); a=ap.parse_args(); print(json.dumps(audit(a.tip),indent=2))
