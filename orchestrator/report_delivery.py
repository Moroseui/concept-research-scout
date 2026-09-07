"""Checked daily report delivery through the existing protected Git publisher.

Only finalized report assets are exported; prompts and raw console never enter
this route. A dedicated clean author checkout is required. Its protected broker
remains responsible for credentials, complete history audit and atomic ref lease.
An uncertain local preparation stays preserved for reconciliation. A lost push
response is resolved against the exact remote candidate, never by a new commit.
"""
import base64
import hashlib
import json
import os
from pathlib import Path
import re

from orchestrator.git_publication import scan
from orchestrator.operations_report import Queue,immutable,private_root,pin
from orchestrator.publication_candidate import git,prepare
from orchestrator.handover_runtime import request_broker
from orchestrator.remote_supervisor import lock

REMOTE='https://github.com/Moroseui/concept-research-scout.git'
BRANCH='astra/infrastructure-milestone-record'


def assets(reports,report_id,phase='reviewed'):
    pin(report_id,64);queue=Queue(reports);record=queue.status(report_id)
    if phase not in ('finalized','reviewed'):raise ValueError('REPORT_DELIVERY_PHASE')
    if phase=='reviewed' and record['status']!='REVIEWED':raise ValueError('REPORT_REVIEW_REQUIRED')
    names=[report_id+'.md']
    if phase=='reviewed':names += [report_id+'.claude-review.md',report_id+'.claude-review.json',
                                  report_id+'.astra-disposition.md']
    primary=queue.root/names[0]
    if primary.is_symlink() or hashlib.sha256(primary.read_bytes()).hexdigest()!=report_id:
        raise ValueError('REPORT_IDENTITY_CHANGED')
    names+=re.findall(r'\]\(([0-9a-f]{64}\.(?:receipts|context)\.json)\)',primary.read_text())
    result={}
    for name in sorted(set(names)):
        path=queue.root/name
        if path.is_symlink() or path.stat().st_size>100000:raise ValueError('REPORT_ASSET_BOUNDARY')
        raw=path.read_bytes();scan('docs/operations/daily/'+name,raw)
        if name.endswith(('.receipts.json','.context.json')) and hashlib.sha256(raw).hexdigest()!=name[:64]:
            raise ValueError('REPORT_LINKED_EVIDENCE_CHANGED')
        result[name]=raw
    if phase=='reviewed':
        receipt=json.loads(result[report_id+'.claude-review.json'])
        if (receipt['source']!=record['source'] or receipt['report_sha256']!=report_id
            or receipt['family']!='claude' or receipt['status']!='COMPLETE'
            or receipt['review_sha256']!=record['review_sha256']
            or hashlib.sha256(result[report_id+'.claude-review.md']).hexdigest()!=record['review_sha256']):
            raise ValueError('REPORT_REVIEW_CHANGED')
    return result


def deliver(reports,report_id,checkout,state,socket,permission_sha256,send=request_broker,phase='reviewed'):
    """Called only from a root-configured publication service after its grant.

    The decision hash binds configuration; it does not authenticate or manufacture
    operator approval. SYNTHETIC_FIXTURE brokers refuse the final publish verb.
    """
    pin(permission_sha256,64);pin(report_id,64)
    if phase not in ('finalized','reviewed'):raise ValueError('REPORT_DELIVERY_PHASE')
    state=private_root(state);checkout=Path(checkout).resolve()
    def observed():
        value=send(socket,'publication_status',{})
        if (value.get('status')!='OBSERVED' or value.get('repository')!=REMOTE
                or value.get('branch')!=BRANCH):raise ValueError('PUBLICATION_NOT_AUTHORIZED_OR_UNAVAILABLE')
        pin(value.get('source'),40);return value['source']
    with lock(state/'branch.lock'):
        directory=state/(report_id+('-finalized' if phase=='finalized' else ''))
        if directory.is_symlink():raise ValueError('DELIVERY_STATE_SYMLINK')
        receipt=directory/'published.json'
        if receipt.exists():return json.loads(receipt.read_text())
        pending=directory/'candidate.json'
        if not pending.exists():
            if directory.exists():raise ValueError('PARTIAL_REPORT_PREPARATION_RECONCILE')
            content=assets(reports,report_id,phase)
            if (git(checkout,'status','--porcelain') or
                    git(checkout,'branch','--show-current').decode().strip()!=BRANCH or
                    git(checkout,'remote','get-url','origin').decode().strip()!=REMOTE):
                raise ValueError('DEDICATED_CLEAN_AUTHORIZED_CHECKOUT_REQUIRED')
            before=git(checkout,'rev-parse','HEAD').decode().strip()
            if observed()!=before:
                raise ValueError('REPORT_PUBLICATION_BASELINE_MOVED')
            directory.mkdir(mode=0o700)
            immutable(directory/'intent.json',(json.dumps({'report':report_id,'before':before,
                'permission_sha256':permission_sha256,'assets':{n:hashlib.sha256(v).hexdigest() for n,v in content.items()}},sort_keys=True)+'\n').encode())
            target=checkout/'docs/operations/daily'
            if any(p.is_symlink() for p in (target,*target.parents)):
                raise ValueError('REPORT_DESTINATION_SYMLINK')
            target.mkdir(parents=True,exist_ok=True)
            for name,raw in content.items():immutable(target/name,raw)
            paths=['docs/operations/daily/'+n for n in sorted(content)]
            git(checkout,'add','--',*paths)
            git(checkout,'-c','user.name=Astra (OpenAI agent)',
                '-c','user.email=astra@agents.local.invalid','commit','-m','Record '+phase+' system report '+report_id)
            source=git(checkout,'rev-parse','HEAD').decode().strip()
            candidate=prepare(checkout,source,before,directory/'source.bundle')
            immutable(pending,(json.dumps({**candidate,'permission_sha256':permission_sha256},sort_keys=True)+'\n').encode())
        candidate=json.loads(pending.read_text())
        if candidate.pop('permission_sha256')!=permission_sha256:raise ValueError('DELIVERY_PERMISSION_CHANGED')
        remote=observed()
        if remote!=candidate['source']:
            if remote!=candidate['before']:raise ValueError('DELIVERY_REMOTE_MOVED_RECONCILE')
            attempts=directory/'attempts.json'
            count=json.loads(attempts.read_text())['count'] if attempts.exists() else 0
            if count>=3:raise ValueError('DELIVERY_RETRY_LIMIT_RECONCILE')
            # Durable count before a potentially ambiguous remote operation.
            temporary=directory/'attempts.new'
            with temporary.open('x') as out:
                json.dump({'count':count+1},out);out.flush();os.fsync(out.fileno())
            temporary.replace(attempts)
            fd=os.open(directory,os.O_RDONLY|os.O_DIRECTORY)
            try:os.fsync(fd)
            finally:os.close(fd)
            raw=(directory/'source.bundle').read_bytes()
            staged=send(socket,'stage_candidate',{**candidate,'bundle_base64':base64.b64encode(raw).decode()})
            if staged.get('status')!='STAGED_NOT_PUBLISHED':raise ValueError('DELIVERY_STAGING_NOT_VERIFIED')
            send(socket,'publish',{'source':candidate['source'],'before':candidate['before'],
                'destination':BRANCH,'remote':REMOTE,'inventory':candidate['inventory']})
            if observed()!=candidate['source']:
                raise ValueError('DELIVERY_REMOTE_VERIFICATION_REQUIRED')
        result={'status':'PUBLISHED','phase':phase,'report':report_id,'source':candidate['source'],
                'before':candidate['before'],'permission_sha256':permission_sha256}
        immutable(receipt,(json.dumps(result,sort_keys=True)+'\n').encode());return result
