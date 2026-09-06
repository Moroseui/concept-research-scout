#!/usr/bin/env python3
"""Hydrate only the pinned ignore file; preserve the installed source and job bindings."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess

SOURCE='6b555075fcf553994ecac8e368f4676cbdffdc56'
BLOB='f545437ebc93eb974d8dd7090b19e79121fd80ba'
ROOT=Path('/opt/research-system/current')

def main():
    p=argparse.ArgumentParser();p.add_argument('--source',required=True);a=p.parse_args()
    if os.getuid()!=0 or a.source!=SOURCE:raise ValueError('EXACT_SETUP_BINDING_REQUIRED')
    def git(*args):return subprocess.check_output(['git',*args],cwd=ROOT,text=True).strip()
    if git('rev-parse','HEAD')!=SOURCE:raise ValueError('SOURCE_CHANGED')
    if git('ls-tree',SOURCE,'--','.gitignore').split()!=['100644','blob',BLOB,'.gitignore']:raise ValueError('IGNORE_IDENTITY_CHANGED')
    subprocess.run(['git','sparse-checkout','add','--no-cone','/.gitignore'],cwd=ROOT,check=True)
    if git('hash-object','.gitignore')!=BLOB or git('rev-parse','HEAD')!=SOURCE:raise ValueError('HYDRATION_IDENTITY_FAILED')
    env={**os.environ,'GIT_OPTIONAL_LOCKS':'0','GIT_NO_LAZY_FETCH':'1'}
    status=subprocess.check_output(['runuser','-u','research-controller','--','env','GIT_OPTIONAL_LOCKS=0','GIT_NO_LAZY_FETCH=1','git','-c','safe.directory='+str(ROOT.resolve()),'status','--porcelain'],cwd=ROOT,env=env)
    if status.strip():raise ValueError('SOURCE_NOT_CLEAN')
    print(json.dumps({'source':SOURCE,'hydrated_path':'.gitignore','blob':BLOB,'sha256':hashlib.sha256((ROOT/'.gitignore').read_bytes()).hexdigest(),'source_clean_as_controller':True,'jobs_resubmitted':False}))

if __name__=='__main__':main()
