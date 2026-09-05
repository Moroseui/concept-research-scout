"""Explicit local/remote pilot bindings. No branch inference and no history merges."""
import argparse
import json
from pathlib import Path
import re
import subprocess

BRANCH='astra/autonomous-isles-pilot'


def verify(root, source, destination):
    if not re.fullmatch('[0-9a-f]{40}',source) or destination!=BRANCH:
        raise ValueError('exact source SHA and authorized pilot destination required')
    head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip()
    if head!=source:raise ValueError('checkout differs from explicit source')
    return {'source':source,'destination':destination,'status':'BOUND_NOT_PUBLISHED'}


def publish(root, source, destination, expected_remote):
    verify(root,source,destination)
    if not re.fullmatch('[0-9a-f]{40}',expected_remote):raise ValueError('exact before pin required')
    from scripts import check_pilot_publication as audit
    old=audit.ROOT
    try:
        audit.ROOT=Path(root);receipt=audit.audit(source)
    finally:audit.ROOT=old
    remote=subprocess.check_output(['git','ls-remote','origin','refs/heads/'+destination],cwd=root,text=True).split()
    if not remote or remote[0]!=expected_remote:raise ValueError('remote moved; reconcile without force')
    subprocess.run(['git','merge-base','--is-ancestor',expected_remote,source],cwd=root,check=True)
    subprocess.run(['git','push','origin',source+':refs/heads/'+destination],cwd=root,check=True)
    return receipt


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('action',choices=['verify','publish'])
    p.add_argument('--source',required=True);p.add_argument('--destination',required=True)
    p.add_argument('--expected-remote');a=p.parse_args()
    if a.action=='publish':
        if not a.expected_remote:p.error('--expected-remote required')
        result=publish(Path.cwd(),a.source,a.destination,a.expected_remote)
    else:result=verify(Path.cwd(),a.source,a.destination)
    print(json.dumps(result,indent=2))
