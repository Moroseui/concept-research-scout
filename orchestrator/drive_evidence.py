"""Registered private Drive evidence capability; no scientific execution or publication.

Google's drive.file scope limits access to selected/app-created files. A protected
registry further limits reads to aliases and refuses archive downloads. Requests
come through the existing peer-UID checked broker transport. Raw evidence never
appears in replies. A failed transfer remains durable and is not automatically
retried. Credentials and registry must be inaccessible to model/worker identities.
"""
import hashlib
import datetime
import json
import os
from pathlib import Path
import re
import socket

SCOPE = 'https://www.googleapis.com/auth/drive.file'
LIMIT = 32 * 1024 * 1024
FIELDS = 'id,name,mimeType,size,md5Checksum,version,modifiedTime,trashed,capabilities(canDownload)'


def digest(data):
    return hashlib.sha256(data).hexdigest()


def private_write(path, value):
    data = (json.dumps(value, sort_keys=True, indent=2)+'\n').encode()
    with path.open('xb') as handle:
        os.chmod(path, 0o600)
        handle.write(data)
        handle.flush(); os.fsync(handle.fileno())
    fd=os.open(path.parent,os.O_RDONLY|os.O_DIRECTORY)
    try:os.fsync(fd)
    finally:os.close(fd)


class GoogleDrive:
    """Existing Google client libraries handle OAuth access-token refresh in memory."""
    def __init__(self, credentials):
        from google.oauth2.credentials import Credentials
        from googleapiclient.discovery import build
        from google_auth_httplib2 import AuthorizedHttp
        import httplib2
        from orchestrator.phone_notifications import protected_read
        info=json.loads(protected_read(credentials))
        if set(info.get('scopes',[]))!={SCOPE}:raise ValueError('NARROW_STORED_SCOPE_REQUIRED')
        creds = Credentials.from_authorized_user_info(info, scopes=[SCOPE])
        if set(creds.scopes or []) != {SCOPE} or not creds.refresh_token:
            raise ValueError('PERSISTENT_NARROW_DRIVE_GRANT_REQUIRED')
        if creds.token_uri != 'https://oauth2.googleapis.com/token':
            raise ValueError('GOOGLE_TOKEN_ENDPOINT_REQUIRED')
        self.api = build('drive', 'v3', http=AuthorizedHttp(creds, http=httplib2.Http(timeout=60)), cache_discovery=False)

    def metadata(self, file_id):
        return self.api.files().get(fileId=file_id, fields=FIELDS).execute(num_retries=0)

    def download(self, file_id, output, maximum):
        from googleapiclient.http import MediaIoBaseDownload
        request = self.api.files().get_media(fileId=file_id)
        reader = MediaIoBaseDownload(output, request, chunksize=1024*1024)
        complete = False
        while not complete:
            _, complete = reader.next_chunk(num_retries=0)
            if output.tell() > maximum:
                raise ValueError('DRIVE_TRANSFER_SIZE_BOUND')


    def private_folder(self, file_id):
        value = self.api.files().get(fileId=file_id, fields='id,mimeType,trashed,ownedByMe,permissions(type,role)').execute(num_retries=0)
        if (value.get('trashed') or value.get('mimeType')!='application/vnd.google-apps.folder'
                or not value.get('ownedByMe') or not value.get('permissions')
                or any(p.get('role')!='owner' or p.get('type')!='user' for p in value['permissions'])):
            raise ValueError('PRIVATE_OWNED_DRIVE_FOLDER_REQUIRED')

    def allocate_ids(self, count):
        return self.api.files().generateIds(count=count,space='drive',type='files').execute(num_retries=0)['ids']

    def create(self, file_id, name, parent, data=None):
        from googleapiclient.http import MediaIoBaseUpload
        import io
        body={'id':file_id,'name':name,'parents':[parent]}
        if data is None:body['mimeType']='application/vnd.google-apps.folder'
        args={'body':body,'fields':FIELDS}
        if data is not None:args['media_body']=MediaIoBaseUpload(io.BytesIO(data),mimetype='application/octet-stream',resumable=False)
        return self.api.files().create(**args).execute(num_retries=0)


class DriveEvidence:
    def __init__(self, config, client):
        if config.get('version') != 1 or config.get('mode') != 'REGISTERED_EVIDENCE_ONLY':
            raise ValueError('DRIVE_CAPABILITY_CONFIGURATION_REQUIRED')
        self.config, self.client = config, client
        self.root = Path(config['private_root'])
        if self.root.is_symlink() or not self.root.is_dir() or self.root.stat().st_mode & 0o077:
            raise ValueError('PRIVATE_EVIDENCE_ROOT_REQUIRED')

    def handle(self, request, peer_uid):
        if peer_uid not in self.config['caller_uids']:
            raise ValueError('DRIVE_CALLER_REFUSED')
        if (not isinstance(request,dict) or set(request)!={'operation','body'}
                or not isinstance(request['body'],dict) or set(request['body'])!={'alias','request_id'}):
            raise ValueError('DRIVE_REQUEST_SCHEMA')
        request={'operation':request['operation'],**request['body']}
        if request['operation'] not in ('metadata','collect','status','store'):
            raise ValueError('DRIVE_REQUEST_SCHEMA')
        alias, request_id = request['alias'], request['request_id']
        if not isinstance(request_id,str) or not re.fullmatch('[a-z0-9][a-z0-9-]{7,79}',request_id):
            raise ValueError('DRIVE_REQUEST_ID_REQUIRED')
        if request['operation']=='store':
            return self.store(request_id,alias,peer_uid)
        entry = self.config['files'].get(alias)
        if not entry:
            raise ValueError('DRIVE_FILE_NOT_REGISTERED')
        folder = self.root / request_id
        if request['operation'] == 'status':
            return self.status(folder, alias)
        if folder.exists():
            if (folder/'intent.json').exists() and json.loads((folder/'intent.json').read_text())['operation']!=request['operation']:
                raise ValueError('DRIVE_REQUEST_ID_CONFLICT')
            return self.status(folder, alias)
        if request['operation'] == 'collect' and entry['access'] != 'small-evidence-read':
            raise ValueError('ARCHIVE_OR_UNAUTHORIZED_TRANSFER_REFUSED')
        folder.mkdir(mode=0o700)
        private_write(folder/'intent.json', {'alias':alias,'file_id':entry['id'], 'operation':request['operation'],
                    'requester_uid':peer_uid,'registry_sha256':digest(json.dumps(self.config,sort_keys=True).encode())})
        try:
            before = self.client.metadata(entry['id'])
            if before.get('trashed') or before['name'] != entry['expected_name']:
                raise ValueError('REGISTERED_FILE_CHANGED')
            private_write(folder/'metadata-before.json',before)
            result = {'stage':'drive-evidence','status':'METADATA_VERIFIED','alias':alias,
                      'collected_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),
                      'implementation_sha256':digest(Path(__file__).read_bytes()),'requester_uid':peer_uid,
                      'request_id':request_id,'file_id_sha256':digest(entry['id'].encode()),
                      'bytes':int(before.get('size',0)), 'version':before.get('version'),
                      'scientific_acceptance':False, 'experiment_executed':False}
            if request['operation']=='collect':
                maximum = min(int(entry['max_bytes']), LIMIT)
                if not 0 < result['bytes'] <= maximum or before.get('mimeType','').startswith('application/vnd.google-apps.'):
                    raise ValueError('BOUNDED_BINARY_EVIDENCE_REQUIRED')
                with (folder/'original.part').open('xb') as output:
                    os.chmod(output.name,0o600)
                    self.client.download(entry['id'],output,maximum)
                    output.flush(); os.fsync(output.fileno())
                raw=(folder/'original.part').read_bytes()
                after=self.client.metadata(entry['id'])
                private_write(folder/'metadata-after.json',after)
                if before != after or len(raw)!=result['bytes']:
                    raise ValueError('DRIVE_ORIGINAL_CHANGED_DURING_COLLECTION')
                if before.get('md5Checksum') and hashlib.md5(raw).hexdigest()!=before['md5Checksum']:
                    raise ValueError('DRIVE_ORIGINAL_CHECKSUM_MISMATCH')
                (folder/'original.part').rename(folder/'original')
                result.update(status='PRIVATE_ORIGINAL_COLLECTED',sha256=digest(raw))
                if (folder/'original').read_bytes()!=raw:raise ValueError('PRIVATE_READBACK_MISMATCH')
            private_write(folder/'receipt.json',result)
            return result
        except Exception as error:
            # Full provider details may contain private identifiers. Preserve privately.
            private_write(folder/'failure.json',{'type':type(error).__name__,'detail':str(error)})
            return {'stage':'drive-evidence','status':'BLOCKED_RECONCILE','request_id':request_id,
                    'next_action':'Inspect private failure; no automatic retry or authentication fallback.'}

    def status(self, folder, alias):
        if folder.is_symlink():raise ValueError('DRIVE_EVIDENCE_SYMLINK')
        if not folder.exists():return {'status':'NOT_RECORDED','execution_absence_established':False}
        if not (folder/'intent.json').exists():return {'status':'BLOCKED_RECONCILE','next_action':'Preserve incomplete intent; do not retry automatically.'}
        intent=json.loads((folder/'intent.json').read_text())
        if intent['alias']!=alias:raise ValueError('DRIVE_REQUEST_ID_CONFLICT')
        receipt=folder/'receipt.json'
        if not receipt.exists():return {'status':'BLOCKED_RECONCILE','next_action':'Preserve partial evidence; inspect before any new attempt.'}
        value=json.loads(receipt.read_text())
        if value['status']=='PRIVATE_ORIGINAL_COLLECTED' and digest((folder/'original').read_bytes())!=value['sha256']:
            raise ValueError('PRIVATE_EVIDENCE_CHANGED')
        return value


    def store(self, request_id, alias, peer_uid):
        # Only an already-collected original or a coordinator-produced bounded bundle.
        # No arbitrary local paths, replacement of originals, sharing or deletion API.
        if alias != 'run-artifacts':raise ValueError('DRIVE_STORE_ALIAS')
        spool=Path(self.config['upload_spool'])/request_id
        if spool.is_symlink() or not spool.is_dir():raise ValueError('REGISTERED_RUN_BUNDLE_REQUIRED')
        from orchestrator.publication import inventory
        files=inventory(spool)
        if not {'console.log','receipt.json'} <= set(files) or len(files)>64:
            raise ValueError('CONSOLE_AND_RECEIPT_REQUIRED')
        payloads={}
        for name in files:
            if '/' in name or not re.fullmatch('[A-Za-z0-9_.-]{1,100}',name) or Path(name).suffix not in ('.log','.json','.ipynb','.md','.csv','.txt'):
                raise ValueError('BOUNDED_RUN_ARTIFACT_NAMES_REQUIRED')
            p=spool/name
            if p.stat().st_size>LIMIT:raise ValueError('DRIVE_TRANSFER_SIZE_BOUND')
            if sum(map(len,payloads.values()))+p.stat().st_size>LIMIT:raise ValueError('DRIVE_TRANSFER_SIZE_BOUND')
            fd=os.open(p,os.O_RDONLY|os.O_NOFOLLOW)
            with os.fdopen(fd,'rb') as handle:
                payloads[name]=handle.read(LIMIT+1)
            if len(payloads[name])>LIMIT:raise ValueError('DRIVE_TRANSFER_SIZE_BOUND')
            from orchestrator.git_publication import SECRET
            if SECRET.search(payloads[name]) or re.search(rb'(?:ya29\.[A-Za-z0-9_-]{20,}|1//[A-Za-z0-9_-]{20,})',payloads[name]):
                raise ValueError('CREDENTIAL_IN_UPLOAD_REFUSED')
        if sum(map(len,payloads.values()))>LIMIT:raise ValueError('DRIVE_TRANSFER_SIZE_BOUND')
        if any(digest(payloads[n])!=h for n,h in files.items()) or inventory(spool)!=files:
            raise ValueError('RUN_BUNDLE_CHANGED')
        folder=self.root/('upload-'+request_id)
        binding={'files':files,'parent':self.config['output_folder_id']}
        if folder.exists():
            if not (folder/'intent.json').exists():return {'status':'UPLOAD_OUTCOME_UNCERTAIN','next_action':'Inspect incomplete intent; do not allocate another upload.'}
            old=json.loads((folder/'intent.json').read_text())
            if old['binding']!=binding:raise ValueError('DRIVE_UPLOAD_REQUEST_CONFLICT')
            if (folder/'receipt.json').exists():return json.loads((folder/'receipt.json').read_text())
            return {'status':'UPLOAD_OUTCOME_UNCERTAIN','next_action':'Reconcile persisted remote IDs; do not create new IDs or retry automatically.'}
        folder.mkdir(mode=0o700)
        # Reserve exact IDs before any remote mutation. A lost response cannot justify
        # a second allocation/upload for this request identity.
        private_write(folder/'binding.json',binding)
        try:
            self.client.private_folder(binding['parent'])
            ids=self.client.allocate_ids(len(files)+1)
            if len(set(ids))!=len(files)+1:raise ValueError('UNIQUE_REMOTE_IDS_REQUIRED')
            intent={'binding':binding,'requester_uid':peer_uid,'folder_id':ids[0],'file_ids':dict(zip(sorted(files),ids[1:]))}
            private_write(folder/'intent.json',intent)
            self.client.create(ids[0],request_id,binding['parent'])
            self.client.private_folder(ids[0])
            observed={}
            for name in sorted(files):
                data=payloads[name];file_id=intent['file_ids'][name]
                self.client.private_folder(ids[0])
                value=self.client.create(file_id,name,ids[0],data)
                if value.get('md5Checksum')!=hashlib.md5(data).hexdigest() or int(value.get('size',-1))!=len(data):
                    raise ValueError('DRIVE_UPLOAD_IDENTITY_MISMATCH')
                # Independent retrieval verifies remote bytes, not only an upload response.
                import io
                returned=io.BytesIO();self.client.download(file_id,returned,LIMIT)
                if returned.getvalue()!=data:raise ValueError('DRIVE_UPLOAD_READBACK_MISMATCH')
                observed[name]={'sha256':digest(data),'file_id':file_id}
                private_write(folder/('verified-'+name+'.json'),observed[name])
            receipt={'stage':'drive-evidence-storage','status':'PRIVATE_RUN_STORED',
                     'collected_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),
                     'implementation_sha256':digest(Path(__file__).read_bytes()),'requester_uid':peer_uid,
                     'request_id':request_id,'file_count':len(files),
                     'inventory_sha256':digest(json.dumps(files,sort_keys=True).encode()),
                     'scientific_acceptance':False,'publication':False}
            private_write(folder/'receipt.json',receipt)
            return receipt
        except Exception as error:
            private_write(folder/'failure.json',{'type':type(error).__name__,'detail':str(error)})
            return {'status':'UPLOAD_OUTCOME_UNCERTAIN','next_action':'Inspect private intent/failure and reconcile remote IDs; no automatic retry.'}


def serve(config_path, socket_path, credentials):
    from orchestrator.phone_notifications import protected_read
    from orchestrator.protected_handover import exchange
    config=json.loads(protected_read(config_path))
    broker=DriveEvidence(config,GoogleDrive(credentials))
    if os.environ.get('LISTEN_PID')!=str(os.getpid()) or os.environ.get('LISTEN_FDS')!='1':
        raise ValueError('SYSTEMD_SOCKET_ACTIVATION_REQUIRED')
    server=socket.socket(fileno=3)
    if server.family!=socket.AF_UNIX or server.getsockname()!=socket_path:raise ValueError('DRIVE_SOCKET_MISMATCH')
    with server:
        while True:
            connection,_=server.accept()
            with connection:exchange(broker,connection)


if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('mode',choices=['serve','request'])
    p.add_argument('--config');p.add_argument('--credentials')
    p.add_argument('--socket',default='/run/research-system/drive.sock')
    p.add_argument('--operation',choices=['metadata','collect','status','store'])
    p.add_argument('--alias');p.add_argument('--request-id')
    args=p.parse_args()
    if args.mode=='serve':
        if not args.config or not args.credentials:p.error('protected config and credentials required')
        serve(args.config,args.socket,args.credentials)
    else:
        if not all([args.operation,args.alias,args.request_id]):p.error('operation, alias and request-id required')
        from orchestrator.handover_runtime import request_broker
        print(json.dumps(request_broker(args.socket,args.operation,{'alias':args.alias,'request_id':args.request_id})))
