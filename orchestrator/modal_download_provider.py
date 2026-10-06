"""Direct retrieval provider: one reserved CPU container, metadata-only recovery.

Never downloads imaging to the controller. A durable create intent blocks a
second create even if the provider response was lost. Worker receipts, provider
terminal status and the exact remote inventory must all agree before READY.
"""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json

from orchestrator import private_records, modal_download_package as package
from orchestrator.modal_direct_budget import PURPOSE, RESOURCES
from orchestrator.modal_executor import canonical
from orchestrator.manual_executor import digest
from orchestrator.manual_driver import write_once
from orchestrator.modal_assets import BASE_IMAGE
from orchestrator.modal_ctp_download import encoded

DOMAINS=('huggingface.co','*.huggingface.co','hf.co','*.hf.co')


def require_reserved(accounts,binding):
    ident=digest(canonical(binding))
    row=accounts.db.execute('SELECT * FROM autonomy_assets WHERE id=?',(ident,)).fetchone()
    if (row is None or row['status']!='RESERVED' or row['binding']!=canonical(binding).decode()
            or binding.get('purpose')!=PURPOSE or binding['envelope']['resources']!=RESOURCES):
        raise ValueError('DIRECT_DOWNLOAD_RESERVED_BINDING_REQUIRED')
    return ident


def record(root,name,value):
    write_once(Path(root)/(name+'.json'),canonical(value))


def read_json(volume,name,maximum=1024*1024):
    raw=bytearray()
    for block in volume.read_file('/'+name):
        raw.extend(block)
        if len(raw)>maximum:raise ValueError('DIRECT_DOWNLOAD_RECEIPT_SIZE')
    return json.loads(raw),hashlib.sha256(raw).hexdigest()


@private_records.private_umask
def launch(provider,accounts,binding,prepared,record_root):
    """Call only from the reviewed, installed preparation controller.

    Connectivity, supervision/retention and current authenticated billing are
    established before reservation by that controller. No retry occurs here.
    """
    manifest=package.verify(prepared,binding['package_manifest_sha256'])
    ident=require_reserved(accounts,binding)
    root=Path(record_root)
    if root.exists() or root.is_symlink():raise ValueError('DIRECT_DOWNLOAD_EXISTING_INTENT_RECONCILE')
    if provider.config['workspace']!='moroseui':raise ValueError('MODAL_APPROVED_WORKSPACE')
    if set(manifest['plans'])!={'ctp','images'}:raise ValueError('DIRECT_DOWNLOAD_COMPLETE_SELECTION')
    planned=sum(row['bytes'] for ref in manifest['plans'].values()
                for row in json.loads((Path(prepared)/ref['path']).read_bytes())['files'].values())
    if binding['download_bytes']!=planned:raise ValueError('DIRECT_DOWNLOAD_BYTE_BINDING')
    provider.client.hello()
    ws=provider.modal.Workspace.from_context(client=provider.client);ws.hydrate(client=provider.client)
    if ws.name!='moroseui':raise ValueError('MODAL_AUTHENTICATED_WORKSPACE')
    private_records.mkdir(root,parents=True)
    record(root,'intent',{'binding':binding,'binding_sha256':ident,'created_at':datetime.now(timezone.utc).isoformat()})
    name='research-item4-inputs-'+ident[:24]
    # Every operation below is single-shot. Exceptions preserve its prior intent
    # and full reservation; callers reconcile, never start over automatically.
    record(root,'app-intent',{'name':name})
    try:provider.modal.App.lookup(name,create_if_missing=False,client=provider.client)
    except provider.modal.exception.NotFoundError:pass
    else:raise ValueError('DIRECT_DOWNLOAD_APP_EXISTS')
    app=provider.modal.App.lookup(name,create_if_missing=True,client=provider.client)
    record(root,'app',{'name':name,'app_id':app.app_id})
    record(root,'image-intent',{'registry':BASE_IMAGE,'builder':'2025.06','commands':['FROM '+BASE_IMAGE]})
    image=provider.build_registry_image(app,BASE_IMAGE)
    record(root,'image',{'image_id':image.object_id,'registry':BASE_IMAGE})
    volumes={}
    for kind in ('package','data'):
        vname=name+'-'+kind
        record(root,kind+'-volume-intent',{'name':vname,'version':2})
        try:provider.modal.Volume.from_name(vname,create_if_missing=False,version=2,client=provider.client).hydrate(client=provider.client)
        except provider.modal.exception.NotFoundError:pass
        else:raise ValueError('DIRECT_DOWNLOAD_VOLUME_EXISTS')
        vol=provider.modal.Volume.from_name(vname,create_if_missing=True,version=2,client=provider.client).hydrate(client=provider.client)
        if vol.listdir('/',recursive=True):raise ValueError('DIRECT_DOWNLOAD_VOLUME_NOT_EMPTY')
        volumes[kind]=vol
        record(root,kind+'-volume',{'name':vname,'id':vol.object_id,'version':2})
    if volumes['package'].object_id==volumes['data'].object_id:raise ValueError('DIRECT_DOWNLOAD_VOLUME_OVERLAP')
    expected={name:{'sha256':sha,'bytes':(Path(prepared)/name).stat().st_size}
              for name,sha in package.inventory(prepared).items()}
    if sum(x['bytes'] for x in expected.values())>4*1024**2:raise ValueError('DIRECT_DOWNLOAD_PACKAGE_SIZE')
    record(root,'upload-intent',{'files':expected,'payload':'code and allowlist metadata only'})
    with volumes['package'].batch_upload(force=False) as upload:
        for name in sorted(expected):upload.put_file(Path(prepared)/name,'/'+name,mode=0o440)
    package.verify(prepared,binding['package_manifest_sha256'])
    provider._verify_volume(volumes['package'].object_id,expected)
    record(root,'upload',{'files':expected,'verified':True})
    # The pinned base image installs Ubuntu python3, not a Conda tree.
    args=('/usr/bin/python3','-I','-S','-B','/reviewed/run.py',binding['package_manifest_sha256'],'all',volumes['data'].object_id)
    record(root,'sandbox-intent',{'binding_sha256':ident,'args':args,'resources':RESOURCES,
           'domains':DOMAINS,'volumes':{k:v.object_id for k,v in volumes.items()},'no_credentials':True})
    sb=provider.modal.Sandbox.create(*args,app=app,name='download-'+ident[:32],image=image,
        gpu=None,cpu=(1,1),memory=(2048,2048),timeout=RESOURCES['timeout_seconds'],
        block_network=False,outbound_cidr_allowlist=[],outbound_domain_allowlist=list(DOMAINS),
        inbound_cidr_allowlist=[],include_oidc_identity_token=False,secrets=[],env={},
        encrypted_ports=[],h2_ports=[],unencrypted_ports=[],
        volumes={'/reviewed':volumes['package'].with_mount_options(read_only=True),'/volume':volumes['data']},
        client=provider.client)
    result={'provider_id':sb.object_id,'app_id':app.app_id,'image_id':image.object_id,
            'package_volume_id':volumes['package'].object_id,'data_volume_id':volumes['data'].object_id,
            'binding_sha256':ident,'launched_at':datetime.now(timezone.utc).isoformat()}
    record(root,'sandbox',result)
    return result


def observe(provider,binding,prepared,handle):
    """Repeated observation makes no provider mutation and reads no image bytes."""
    if handle['binding_sha256']!=digest(canonical(binding)):raise ValueError('DIRECT_DOWNLOAD_HANDLE_BINDING')
    manifest=package.verify(prepared,binding['package_manifest_sha256'])
    sb=provider._sandbox(handle['provider_id']);exit_code=sb.poll()
    if exit_code is None:return {'status':'RUNNING','provider_id':handle['provider_id']}
    if exit_code!=0:return {'status':'FAILED','exit_code':exit_code,'provider_id':handle['provider_id'],'no_automatic_retry':True}
    volume=provider._volume(handle['data_volume_id'])
    summary,summary_hash=read_json(volume,'DOWNLOAD_COMPLETE.json')
    if (set(summary)!={'schema','manifest_sha256','results','patient_computation'} or
            summary['schema']!='private-development-download-result/v1' or
            summary['manifest_sha256']!=binding['package_manifest_sha256'] or
            summary['patient_computation'] is not False or set(summary['results'])!=set(manifest['plans'])):
        raise ValueError('DIRECT_DOWNLOAD_RESULT_BINDING')
    expected={'DOWNLOAD_COMPLETE.json':None};proofs={};total=0
    for kind,ref in manifest['plans'].items():
        plan=json.loads((Path(prepared)/ref['path']).read_bytes());attempt=manifest['attempt']+'-'+kind
        folder=kind+'/download-records/'+attempt
        expected[kind+'/.download.lock']=0
        expected[folder+'/plan.json']=(Path(prepared)/ref['path']).stat().st_size
        expected[folder+'/COMPLETE.json']=None
        selected_plan,selected_plan_hash=read_json(volume,folder+'/plan.json')
        if selected_plan_hash!=ref['sha256'] or selected_plan!=plan:raise ValueError('DIRECT_DOWNLOAD_REMOTE_PLAN')
        completed,complete_hash=read_json(volume,folder+'/COMPLETE.json')
        rows=[]
        for index,(name,row) in enumerate(sorted(plan['files'].items()),1):
            record_name=folder+'/'+str(index).zfill(3)
            expected[record_name+'-verified.json']=None
            expected[record_name+'-intent.json']=None
            proof,pin=read_json(volume,record_name+'-verified.json',8192)
            if (set(proof)!={'path','bytes','sha256','crc32'} or proof['path']!=name or
                    any(proof[k]!=row[k] for k in ('bytes','sha256')) or type(proof['crc32']) is not int or not 0<=proof['crc32']<=0xffffffff or
                    (row['crc32'] is not None and proof['crc32']!=row['crc32'])):
                raise ValueError('DIRECT_DOWNLOAD_FILE_RECEIPT')
            rows.append(proof);expected[kind+'/'+name]=row['bytes'];total+=row['bytes']
        if (summary['results'][kind]!=completed or completed.get('status')!='VERIFIED' or completed.get('release')!='16813698/v3' or completed.get('reused_files')!=0 or
                completed.get('plan_sha256')!=ref['sha256'] or completed.get('files')!=len(rows) or
                completed.get('bytes')!=sum(x['bytes'] for x in rows) or completed.get('development_patients')!=99 or
                completed.get('patient_computation') is not False or
                completed.get('file_records_sha256')!=package.sha(encoded(rows))):
            raise ValueError('DIRECT_DOWNLOAD_SCOPE_RECEIPT')
        proofs[kind]={'receipt_sha256':complete_hash,'files':len(rows),'bytes':completed['bytes'],'plan_sha256':ref['sha256']}
    seen=set();stored_bytes=0
    for entry in volume.listdir('/',recursive=True):
        name=entry.path.lstrip('/')
        if entry.type.name not in ('FILE','DIRECTORY'):raise ValueError('DIRECT_DOWNLOAD_REMOTE_MEMBER_TYPE')
        if entry.type.name!='FILE':continue
        stored_bytes+=entry.size
        if name in expected:
            if expected[name] is not None and entry.size!=expected[name]:raise ValueError('DIRECT_DOWNLOAD_REMOTE_SIZE')
            seen.add(name)
        else:
            raise ValueError('DIRECT_DOWNLOAD_REMOTE_UNEXPECTED_MEMBER')
    if seen!=set(expected):raise ValueError('DIRECT_DOWNLOAD_REMOTE_MISSING_MEMBER')
    if stored_bytes>binding['envelope']['maximum_stored_bytes']:raise ValueError('DIRECT_DOWNLOAD_STORED_BYTE_CAP')
    return {'status':'VERIFIED','provider_id':handle['provider_id'],'exit_code':0,'summary_sha256':summary_hash,
            'scopes':proofs,'bytes':total,'patient_computation':False,'controller_image_bytes_read':0}
