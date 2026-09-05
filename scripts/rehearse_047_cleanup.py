#!/usr/bin/env python3
"""LOCAL ONLY. Rehearse a narrow rewrite using original Git objects; never push."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess

OLD='940293b6d562f2d3dd6bfd9d8d8281ccf01e4783'
PARENT='b652005fbcf6a87765a85e81b381a8596b4384ce'
REF='refs/heads/results/probe-047-dc586665d0be'
PREFIX='probes/047/results_v2/'


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--source',required=True,help='private original mirror or local repo')
    ap.add_argument('--destination',required=True,help='new private disposable directory')
    args=ap.parse_args(); source=Path(args.source).resolve(); dest=Path(args.destination).resolve()
    os.umask(0o077)
    dest.mkdir(mode=0o700,parents=True,exist_ok=False)
    def git(*a,repo=source,input=None,env=None):
        return subprocess.check_output(['git',*a],cwd=repo,input=input,env=env)
    assert git('rev-parse',OLD+'^').decode().strip()==PARENT
    repo=dest/'rehearsal.git'
    subprocess.run(['git','init','--bare','-q',str(repo)],check=True)
    subprocess.run(['git','-C',str(repo),'fetch','-q',str(source),OLD],check=True)
    # Original bytes, not hashes alone: bundle includes the parent failure history.
    git('update-ref','refs/heads/original-evidence',OLD,repo=repo)
    git('bundle','create',str(dest/'original-047.bundle'),'refs/heads/original-evidence',repo=repo)
    git('bundle','verify',str(dest/'original-047.bundle'),repo=repo)
    original={}
    for line in git('ls-tree','-r',OLD,'--',PREFIX).decode().splitlines():
        meta,name=line.split('\t'); original[name]=meta.split()[2]
    raw=[p for p in original if p.startswith(PREFIX+'staged/')]
    excluded=PREFIX+'probe_exclusions.csv'
    assert len(raw)==198 and len(original)==215 and excluded in original
    # Store exact excluded file and failure console independently for easy audit.
    (dest/'probe_exclusions.original.csv').write_bytes(git('show',f'{OLD}:{excluded}'))
    failure=git('show',f'{PARENT}:{PREFIX}driver_console.log')
    (dest/'failure.original.console.log').write_bytes(failure)
    (dest/'empty-worktree').mkdir()
    env=dict(os.environ,GIT_INDEX_FILE=str(dest/'index'),GIT_WORK_TREE=str(dest/'empty-worktree'))
    git('read-tree',OLD,repo=repo,env=env)
    for path in raw+[excluded]:
        git('update-index','--force-remove',path,repo=repo,env=env)
    failure_blob=git('hash-object','-w','--stdin',repo=repo,input=failure).decode().strip()
    failure_dest='probes/047/results_v2.failure.console.log'
    git('update-index','--add','--cacheinfo','100644',failure_blob,failure_dest,repo=repo,env=env)
    tree=git('write-tree',repo=repo,env=env).decode().strip()
    env.update(GIT_AUTHOR_NAME='scout cleanup rehearsal',GIT_AUTHOR_EMAIL='scout@local',GIT_COMMITTER_NAME='scout cleanup rehearsal',GIT_COMMITTER_EMAIL='scout@local',GIT_AUTHOR_DATE='2026-09-05T12:00:00Z',GIT_COMMITTER_DATE='2026-09-05T12:00:00Z')
    new=git('commit-tree',tree,'-p',PARENT,repo=repo,env=env,input=b'047 publication cleanup: retain science and original failure; quarantine raw staging and exclusions\n').decode().strip()
    git('update-ref',REF,new,repo=repo)
    # All retained result bytes must remain identical; parent remains identical.
    retained={p:b for p,b in original.items() if p not in raw+[excluded]}
    for path,blob in retained.items():
        assert git('rev-parse',f'{new}:{path}',repo=repo).decode().strip()==blob
    assert git('show',f'{new}:{failure_dest}',repo=repo)==failure
    assert git('rev-parse',new+'^',repo=repo).decode().strip()==PARENT
    affected=[]
    for ref in git('for-each-ref','--format=%(refname)').decode().splitlines():
        r=subprocess.run(['git','merge-base','--is-ancestor',OLD,ref],cwd=source)
        if r.returncode==0: affected.append(ref)
        elif r.returncode!=1: raise RuntimeError('ref ancestry check failed')
    receipt={'old':OLD,'parent':PARENT,'new':new,'ref':REF,'source_refs_containing_old':affected,
             'removed_raw_files':len(raw),'quarantined_audit_files':1,'retained_result_files':len(retained),
             'retained_bytes_verified':True,'failure_bytes_preserved':True,'parent_unchanged':True,
             'private_original_bundle_sha256':hashlib.sha256((dest/'original-047.bundle').read_bytes()).hexdigest(),
             'proposed_command':['git','push',f'--force-with-lease={REF}:{OLD}','https://github.com/Moroseui/concept-research-scout.git',f'{new}:{REF}'],
             'status':'REHEARSED_ONLY_REQUIRES_OPERATOR_APPROVAL'}
    (dest/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(receipt,indent=2))

if __name__=='__main__': main()
