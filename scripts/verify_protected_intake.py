#!/usr/bin/env python3
"""Supervised synthetic protected-cache acceptance; no credentials or remote Git.

Run with an exact source pin and a fresh private destination. This fixture proves
candidate staging and denied publication on the deployed Python/Git environment.
It does not install or activate a publisher, ledger, reset permission or timer.
"""
import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import subprocess

from orchestrator.remote_supervisor import checked_source
from orchestrator.publication_candidate import prepare,receive
from orchestrator.protected_handover import Broker,BRANCH,REPOSITORY
from orchestrator.dispatch_limiter import GitLedger,initial,REF


def git(root,*args):
    return subprocess.check_output(['git','-c','user.name=Synthetic Agent',
        '-c','user.email=fixture@invalid',*args],cwd=root,stderr=subprocess.PIPE).decode().strip()


def run(source,output):
    checked_source(Path(__file__).resolve().parents[1],source)
    root=Path(output);root.mkdir(mode=0o700)
    author=root/'author';author.mkdir();git(author,'init','-q')
    (author/'README.md').write_text('Synthetic public baseline\n')
    git(author,'add','README.md');git(author,'commit','-qm','Synthetic baseline')
    before=git(author,'rev-parse','HEAD')
    cache=root/'cache';git(root,'clone','-q','--no-local',str(author),str(cache))
    (author/'README.md').write_text('Synthetic infrastructure candidate\n')
    git(author,'commit','-qam','Synthetic candidate');candidate=git(author,'rev-parse','HEAD')
    request=prepare(author,candidate,before,root/'candidate.bundle')
    ledger=root/'ledger';ledger.mkdir();git(ledger,'init','-q')
    assert GitLedger(ledger).cas(None,initial())
    broker=Broker({'mode':'SYNTHETIC_FIXTURE','repository':REPOSITORY,'branch':BRANCH,
        'controller_uid':10001,'operator_uids':[0],'sources':[source],
        'ledger_repo':str(ledger),'publication_root':str(cache),'writer_config':None,
        'model_mode':'DISABLED','turn_root':str(root/'turns'),'max_model_turns':0,
        'policy':{'status':'RATIFIED','operator_approval':'SYNTHETIC_FIXTURE_ONLY',
            'state_write_permission':'OPERATOR_AUTHORIZED','n':48,'window':'UTC_CALENDAR_DAY',
            'state_ref':REF,'reset_operators':['ssh-uid:0'],'server_semantics':'OPERATOR_AUTHORIZED_V1'}})
    envelope={'operation':'stage_candidate','body':{**request,
        'bundle_base64':base64.b64encode((root/'candidate.bundle').read_bytes()).decode()}}
    staged=broker.handle(envelope,10001)
    assert staged['status']=='STAGED_NOT_PUBLISHED' and git(cache,'rev-parse','HEAD')==candidate
    refusals={}
    for name,message,uid in [('wrong_peer',envelope,10002),
            ('publication',{'operation':'publish','body':{}},10001),
            ('reset',{'operation':'reset','body':{}},10001)]:
        try:broker.handle(message,uid)
        except ValueError as error:refusals[name]=str(error)
        else:raise AssertionError('required refusal absent')
    assert refusals=={'wrong_peer':'BROKER_PEER_REFUSED',
        'publication':'LIVE_PUBLICATION_NOT_AUTHORIZED','reset':'BROKER_OPERATION_REFUSED'}
    # Deleted unsafe intermediate content cannot enter the publication cache tree.
    (author/'secret.txt').write_text('gh'+'p_'+'x'*40)
    git(author,'add','secret.txt');git(author,'commit','-qm','Synthetic forbidden intermediate')
    (author/'secret.txt').unlink();git(author,'commit','-qam','Synthetic deletion')
    unsafe=git(author,'rev-parse','HEAD');bundle=root/'unsafe.bundle'
    git(author,'bundle','create',str(bundle),'HEAD','^'+candidate);raw=bundle.read_bytes()
    try:receive(cache,unsafe,candidate,{},raw,hashlib.sha256(raw).hexdigest())
    except ValueError as error:assert str(error)=='PUBLICATION_CONTENT_REJECTED'
    else:raise AssertionError('unsafe history accepted')
    assert git(cache,'rev-parse','HEAD')==candidate
    result={'status':'PASS','source':source,'kind':'SUPERVISED_PROTECTED_INTAKE_FIXTURE',
        'synthetic_candidate_staged':True,'unsafe_intermediate_rejected':True,
        'denials':refusals,'live_configuration_changed':False,'models_started':0,
        'git_remote_publications':0,'credentials_used':False,
        'uid':os.getuid(),'git_version':git(root,'--version')}
    (root/'receipt.json').write_text(json.dumps(result,indent=2)+'\n')
    return result


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source',required=True);parser.add_argument('--output',required=True)
    args=parser.parse_args();print(json.dumps(run(args.source,args.output)))
