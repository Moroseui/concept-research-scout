"""Pinned per-file development CTP download inside a private Modal Volume.

No archive extraction, discovery, scan computation, credentials or model input.
The controller admits/cost-bounds the separate CPU container. This worker only
fetches the exact allowlist, verifies stream AND disk, commits each completed
file, and preserves failed partials. It never starts another container or retry.
"""
import hashlib
import fcntl
import json
import os
import re
import time
import urllib.request
import urllib.parse
import zlib
import subprocess
from pathlib import Path
from orchestrator import private_records

from orchestrator.modal_development_inputs import COHORT, SOURCE, expected_paths, frozen_inventory

AUTHORITY='fa23a858ca16da34b768cd0ec2dc9cd49b0228a6ec21ebbf1d4acd33dfad84ca'
METADATA='654ea34321f2b9227c4320d8ca4fbbd505fafdfd7fa6b3eac95abd9cb6cdb1b7'
ARCHIVE='3a290b51f8025c1e0b41c842f856152c2e9ead331b06766b0c40c6be12985e88'
REVISION='7bead709cd9f60ed6bea866b7a994a8ecc83db16'
BASE='https://huggingface.co/datasets/Lyucunming/isles2024/resolve/'+REVISION+'/'
MAX_FILE=1024**3
MAX_TOTAL=64*1024**3


def encoded(value):
    return (json.dumps(value,sort_keys=True,separators=(',', ':'),allow_nan=False)+'\n').encode()


def identifier(value):
    if not isinstance(value,str) or not re.fullmatch(r'[a-zA-Z0-9][a-zA-Z0-9_-]{0,95}',value):
        raise ValueError('FIT_IDENTIFIER')
    return value


def volume_commit(mount):
    # This worker is mounted only on an authenticated Volume v2.
    subprocess.run(['/usr/bin/sync',str(mount)],check=True,timeout=120)


def sha(raw):return hashlib.sha256(raw).hexdigest()


def _cases(raw):
    if sha(raw)!=COHORT:raise ValueError('CTP_FROZEN_DEVELOPMENT_COHORT')
    cases=json.loads(raw)['cases']
    if len(cases)!=99 or len(set(cases))!=99 or any(not re.fullmatch('sub-stroke[0-9]{4}',c) for c in cases):
        raise ValueError('CTP_DEVELOPMENT_SET')
    return cases


def frozen_plan(cohort_raw,metadata_raw,archive_raw,authority_raw):
    cases=_cases(cohort_raw)
    if any(sha(raw)!=pin for raw,pin in [(metadata_raw,METADATA),(archive_raw,ARCHIVE),(authority_raw,AUTHORITY)]):
        raise ValueError('CTP_SOURCE_PIN')
    meta=json.loads(metadata_raw);archive=json.loads(archive_raw)
    if meta['summary']['revision']!=REVISION:raise ValueError('CTP_SOURCE_REVISION')
    if len(meta['members'])!=99 or {r['case'] for r in meta['members']}!=set(cases):
        raise ValueError('CTP_SOURCE_MEMBER_SET')
    files={}
    for row in meta['members']:
        c=row['case'];m=row['metadata']
        source=f'derivatives/{c}/ses-01/{c}_ses-01_space-ncct_ctp.nii.gz'
        official=[r for r in archive['selected'] if r['case']==c and r['registered']]
        if (len(official)!=1 or m['path']!=source or m['type']!='file' or
                m['size']!=m['lfs']['size'] or m['size']!=official[0]['bytes'] or
                row['official_crc32']!=official[0]['crc32']):
            raise ValueError('CTP_OFFICIAL_MEMBER_DISAGREEMENT')
        files['train/'+source]={'source':source,'bytes':m['size'],'sha256':m['lfs']['oid'],'crc32':official[0]['crc32']}
    plan={'schema':'development-ctp-download/v1','authority_sha256':AUTHORITY,'cohort_sha256':COHORT,
          'metadata_sha256':METADATA,'archive_members_sha256':ARCHIVE,'release':'16813698/v3',
          'mirror_revision':REVISION,'files':files}
    validate(plan,cohort_raw)
    return plan


def frozen_image_plan(cohort_raw,source_raw,upload_authority_raw,download_authority_raw):
    if sha(download_authority_raw)!=AUTHORITY:raise ValueError('CTP_SOURCE_PIN')
    contract=frozen_inventory(cohort_raw,source_raw,upload_authority_raw)
    files={name:{'source':name[len('train/'):],**row,'crc32':None}
           for name,row in contract['files'].items() if name.startswith('train/')}
    plan={'schema':'development-images-download/v1','authority_sha256':AUTHORITY,'cohort_sha256':COHORT,
          'source_capture_sha256':SOURCE,'release':'16813698/v3','mirror_revision':REVISION,'files':files}
    validate(plan,cohort_raw)
    return plan


def validate(plan,cohort_raw):
    cases=_cases(cohort_raw)
    images=isinstance(plan,dict) and plan.get('schema')=='development-images-download/v1'
    expected={'schema':'development-ctp-download/v1','authority_sha256':AUTHORITY,'cohort_sha256':COHORT,
              'metadata_sha256':METADATA,'archive_members_sha256':ARCHIVE,'release':'16813698/v3','mirror_revision':REVISION}
    if images:
        expected={'schema':'development-images-download/v1','authority_sha256':AUTHORITY,'cohort_sha256':COHORT,
                  'source_capture_sha256':SOURCE,'release':'16813698/v3','mirror_revision':REVISION}
    if not isinstance(plan,dict) or set(plan)!=set(expected)|{'files'} or any(plan[k]!=v for k,v in expected.items()):
        raise ValueError('CTP_DOWNLOAD_BINDINGS')
    members={f'train/derivatives/{c}/ses-01/{c}_ses-01_space-ncct_ctp.nii.gz' for c in cases}
    if images:members={name for name in expected_paths(cases) if name.startswith('train/')}
    if not isinstance(plan['files'],dict) or set(plan['files'])!=members:
        raise ValueError('CTP_DOWNLOAD_MEMBER_SET')
    for name,row in plan['files'].items():
        if (not isinstance(row,dict) or set(row)!={'source','bytes','sha256','crc32'} or row['source']!=name[len('train/'):] or
                type(row['bytes']) is not int or not 0<row['bytes']<=MAX_FILE or
                not isinstance(row['sha256'],str) or not re.fullmatch('[0-9a-f]{64}',row['sha256']) or
                ((row['crc32'] is not None) if images else (type(row['crc32']) is not int or not 0<=row['crc32']<=0xffffffff))):
            raise ValueError('CTP_DOWNLOAD_FILE_BINDING')
    if sum(r['bytes'] for r in plan['files'].values())>MAX_TOTAL:raise ValueError('CTP_DOWNLOAD_SIZE_CAP')
    return plan


def allowed_url(url):
    u=urllib.parse.urlsplit(url)
    if (u.scheme!='https' or u.username or u.password or u.port not in (None,443) or
            not u.hostname or not any(u.hostname==h or u.hostname.endswith('.'+h) for h in ('huggingface.co','hf.co'))):
        raise ValueError('CTP_REDIRECT_HOST_REFUSED')
    return url


class PinnedRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self,req,fp,code,msg,headers,newurl):
        allowed_url(newurl)
        return super().redirect_request(req,fp,code,msg,headers,newurl)


def verify_file(path,row):
    private_records.check(path)
    h=hashlib.sha256();crc=0;count=0
    with Path(path).open('rb') as f:
        for chunk in iter(lambda:f.read(1024*1024),b''):
            count+=len(chunk)
            if count>row['bytes']:raise ValueError('CTP_FILE_OVERSIZE')
            h.update(chunk);crc=zlib.crc32(chunk,crc)
    if count!=row['bytes'] or h.hexdigest()!=row['sha256'] or (row['crc32'] is not None and crc!=row['crc32']):
        raise ValueError('CTP_FILE_CONTENT_MISMATCH')
    return {'bytes':count,'sha256':h.hexdigest(),'crc32':crc}


@private_records.private_umask
def download(plan,cohort_raw,volume,attempt,*,plan_sha256,opener=None,commit=volume_commit):
    validate(plan,cohort_raw)
    if sha(encoded(plan))!=plan_sha256:raise ValueError('CTP_SELECTED_PLAN_CHANGED')
    root=Path(volume);private_records.check(root);identifier(attempt)
    with private_records.open_file(root/'.download.lock','ab') as handle:
        try:fcntl.flock(handle.fileno(),fcntl.LOCK_EX|fcntl.LOCK_NB)
        except BlockingIOError:raise ValueError('CTP_DOWNLOAD_WRITER_ACTIVE') from None
        try:return _download_locked(plan,root,attempt,plan_sha256,opener,commit)
        finally:fcntl.flock(handle.fileno(),fcntl.LOCK_UN)


def _members(root,files):
    # Check names before opening any existing payload; never read an unexpected
    # case's data merely to establish that it is outside the selected cohort.
    for path in root.rglob('*'):
        if path.is_symlink():raise ValueError('CTP_VOLUME_ALIAS')
        if path.is_file():
            name=str(path.relative_to(root))
            if name not in files and name!='.download.lock' and not name.startswith('download-records/'):
                raise ValueError('CTP_VOLUME_UNEXPECTED_MEMBER')


def _download_locked(plan,root,attempt,plan_sha256,opener,commit):
    _members(root,plan['files'])
    opener=opener or urllib.request.build_opener(PinnedRedirect())
    records=root/'download-records';private_records.mkdir(records,exist_ok=True)
    folder=records/attempt
    if folder.exists():raise ValueError('CTP_EXISTING_ATTEMPT_RECONCILE')
    private_records.mkdir(folder)
    private_records.write_bytes(folder/'plan.json',encoded(plan));commit(root)
    completed=[];reused=0
    for index,(name,row) in enumerate(sorted(plan['files'].items()),1):
        target=root/name
        if target.exists() or target.is_symlink():
            result=verify_file(target,row);reused+=1
        else:
            partial=folder/(str(index).zfill(3)+'.partial')
            url=BASE+urllib.parse.quote(row['source'],safe='/')+'?download=true';allowed_url(url)
            private_records.write_bytes(folder/(str(index).zfill(3)+'-intent.json'),encoded({'path':name,'expected':row,'plan_sha256':plan_sha256}))
            commit(root)
            started=time.monotonic();h=hashlib.sha256();crc=0;count=0
            try:
                req=urllib.request.Request(url,headers={'User-Agent':'ISLES-development-allowlist-retrieval/1.0'})
                with opener.open(req,timeout=45) as response:
                    allowed_url(response.url)
                    if response.status!=200:raise ValueError('CTP_HTTP_STATUS')
                    length=response.headers.get('Content-Length')
                    if length is not None and int(length)!=row['bytes']:raise ValueError('CTP_HTTP_LENGTH')
                    with private_records.open_file(partial,'xb') as f:
                        while True:
                            chunk=response.read(min(1024*1024,row['bytes']-count+1))
                            if not chunk:break
                            count+=len(chunk)
                            if count>row['bytes']:raise ValueError('CTP_FILE_OVERSIZE')
                            h.update(chunk);crc=zlib.crc32(chunk,crc);f.write(chunk)
                            if time.monotonic()-started>1800:raise ValueError('CTP_FILE_DEADLINE')
                        f.flush();os.fsync(f.fileno())
                if count!=row['bytes'] or h.hexdigest()!=row['sha256'] or (row['crc32'] is not None and crc!=row['crc32']):
                    raise ValueError('CTP_NETWORK_CONTENT_MISMATCH')
                result=verify_file(partial,row)
                private_records.mkdir(target.parent,parents=True,exist_ok=True)
                if target.exists() or target.is_symlink():raise ValueError('CTP_DESTINATION_CHANGED')
                partial.rename(target);commit(root)
            except BaseException as error:
                private_records.write_bytes(folder/(str(index).zfill(3)+'-failure.json'),encoded({'status':'FAILED','error_type':type(error).__name__,'partial_bytes':partial.stat().st_size if partial.exists() else 0,'no_retry':True}))
                commit(root);raise
        private_records.write_bytes(folder/(str(index).zfill(3)+'-verified.json'),encoded({'path':name,**result}))
        commit(root);completed.append({'path':name,**result})
    # A complete independent reread, after every per-file durable commit.
    _members(root,plan['files'])
    for name,row in plan['files'].items():verify_file(root/name,row)
    result={'status':'VERIFIED','plan_sha256':plan_sha256,'files':len(completed),'reused_files':reused,
            'bytes':sum(r['bytes'] for r in completed),'file_records_sha256':sha(encoded(completed)),
            'development_patients':99,'release':'16813698/v3','patient_computation':False,
            'limitation':('Pinned third-party per-file SHA256 with official v3 archive size/CRC correspondence; not an official per-file cryptographic signature.' if plan['schema']=='development-ctp-download/v1' else 'Download must match the preserved local v3 extraction byte-for-byte. Derived brain masks are excluded from this remote route and retain their separate source.')}
    private_records.write_bytes(folder/'COMPLETE.json',encoded(result));commit(root)
    return result
