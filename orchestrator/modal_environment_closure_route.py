"""Explicit no-patient offline closure profile for the existing asset lifecycle.

Exact wheel bytes are prepared inside this same reserved operation. Original
wheels and receipts are preserved; no existing M3 owner or allowance is reused.
"""
from pathlib import Path
import base64
import json
import re
from datetime import datetime, timezone, timedelta
from decimal import Decimal, ROUND_CEILING
from orchestrator import modal_environment_closure as closure
from orchestrator import modal_scientific_environment as environment
from orchestrator import private_records as pr
from orchestrator.modal_executor import canonical
from orchestrator.manual_executor import digest
from orchestrator.review_contract import strict_json
from orchestrator.modal_item4_policy import AUTHORITY, quote

PURPOSE='M4_ITEM4_ENVIRONMENT_CLOSURE'
OPERATION='item4-scientific-environment-closure-v1'
RUN='sprint13b-closure-'+AUTHORITY[:24]
SCHEMA='item4-environment-closure/v1'
RESOURCES={'gpu':None,'cpu':2,'memory_mib':8192,'timeout_seconds':1800}
# Storage and bounded receipt egress are added to the fixed extra overhead.
OVERHEAD_MICRO=1_000_000
MAX_ARGUMENT=96*1024

BOOTSTRAP=r"""import base64,hashlib,json,os,sys
from pathlib import Path
os.umask(0o077)
payload=json.loads(base64.b64decode(sys.argv[1],validate=True))
root=Path('/tmp')/('closure-'+payload['binding_sha256'])
root.mkdir(mode=0o700)
package=root/'orchestrator';package.mkdir(mode=0o700)
(package/'__init__.py').write_text('')
for name,row in payload['sources'].items():
 raw=base64.b64decode(row['bytes'],validate=True)
 if hashlib.sha256(raw).hexdigest()!=row['sha256']:raise RuntimeError('CLOSURE_SOURCE_BINDING')
 (package/name).write_bytes(raw)
sys.path.insert(0,str(root))
from orchestrator import modal_environment_closure as worker
selected=payload['selection'];worker.selection(selected)
wheels=root/'wheels';wheels.mkdir(mode=0o700)
source=Path('/wheels')
if set(x.name for x in source.iterdir())!=set(selected['wheels']):raise RuntimeError('CLOSURE_VOLUME_MEMBERS')
for name,pin in selected['wheels'].items():
 path=source/name
 if path.is_symlink() or not path.is_file():raise RuntimeError('CLOSURE_VOLUME_MEMBER')
 hashed=hashlib.sha256();size=0
 with path.open('rb') as inp,(wheels/name).open('xb') as out:
  for chunk in iter(lambda:inp.read(1024*1024),b''):
   size+=len(chunk)
   if size>pin['bytes']:raise RuntimeError('CLOSURE_VOLUME_SIZE')
   hashed.update(chunk);out.write(chunk)
 if size!=pin['bytes'] or hashed.hexdigest()!=pin['sha256']:raise RuntimeError('CLOSURE_VOLUME_HASH')
result=worker.run(selected,wheels,root/'result',payload['binding_sha256'])
sys.stdout.buffer.write(worker.encoded(result))
"""


def source_files():
    return {Path(m.__file__).name:Path(m.__file__).read_bytes() for m in (closure,environment)}


def worker_sha256():
    return digest(canonical({'bootstrap':BOOTSTRAP,'sources':{k:digest(v) for k,v in source_files().items()}}))


def envelope(rates,files):
    from orchestrator.modal_billing import decimal
    if any(k not in rates or decimal(rates[k])<0 for k in ('volume_storage_gib_month_cost','egress_gib_cost')):
        raise ValueError('CLOSURE_STORAGE_RATES')
    size=sum(x['bytes'] for x in files.values())
    if type(size) is not int or not 0<size<=32*1024**3:raise ValueError('CLOSURE_STORAGE_BOUND')
    storage=Decimal(size)/1024**3*decimal(rates['volume_storage_gib_month_cost'])*Decimal(35)/28
    egress=Decimal(4)/1024*decimal(rates['egress_gib_cost'])
    extra=int(((storage+egress)*1000000).to_integral_value(rounding=ROUND_CEILING))
    return {'resources':dict(RESOURCES),'cost':quote(RESOURCES,rates,OVERHEAD_MICRO+extra),
            'wheel_bytes':size,'retention_days':30,'reserved_storage_days':35,
            'receipt_egress_bound_bytes':4*1024**2,
            'storage_rates':{k:rates[k] for k in ('volume_storage_gib_month_cost','egress_gib_cost')}}


def validate(value):
    if not isinstance(value,dict) or set(value)!={'selection','wheel_root'}:
        raise ValueError('CLOSURE_ROUTE_FIELDS')
    closure.selection(value['selection'])
    if (len(closure.encoded(value['selection']))>48*1024 or
            not isinstance(value['wheel_root'],str) or not Path(value['wheel_root']).is_absolute() or
            '..' in Path(value['wheel_root']).parts):
        raise ValueError('CLOSURE_ROUTE_INPUT_BOUND')
    payload(value,'0'*64)
    return value


def local_wheels(value):
    validate(value)
    from orchestrator.modal_assets import local_files
    return local_files(value['wheel_root'],value['selection']['wheels'])


def payload(value,binding_sha256):
    value={'selection':value['selection'],'binding_sha256':binding_sha256,
        'sources':{k:{'bytes':base64.b64encode(v).decode(),'sha256':digest(v)} for k,v in source_files().items()}}
    encoded=base64.b64encode(canonical(value)).decode()
    if len(encoded.encode())>MAX_ARGUMENT or len(BOOTSTRAP.encode())>MAX_ARGUMENT:
        raise ValueError('CLOSURE_TRANSPORT_BOUND')
    return encoded


def prepare_wheels(provider,binding,app,record_root):
    from orchestrator.modal_environment_provider import record
    from orchestrator.modal_assets import upload
    validate(binding['closure']);local_wheels(binding['closure'])
    ident=digest(canonical(binding));name='research-item4-closure-'+ident[:24]+'-wheels'
    root=Path(record_root)
    record(root,'wheel-volume-intent',{'binding_sha256':ident,'name':name})
    try:provider.modal.Volume.from_name(name,create_if_missing=False).hydrate(client=provider.client)
    except provider.modal.exception.NotFoundError:pass
    else:raise ValueError('CLOSURE_VOLUME_EXISTS')
    volume=provider.modal.Volume.from_name(name,create_if_missing=True).hydrate(client=provider.client)
    if not re.fullmatch('vo-[A-Za-z0-9]+',volume.object_id):raise ValueError('CLOSURE_VOLUME_ID')
    record(root,'wheel-volume',{'binding_sha256':ident,'name':name,'volume_id':volume.object_id})
    files=binding['closure']['selection']['wheels'];created=datetime.now(timezone.utc)
    record(root,'wheel-upload-intent',{'binding_sha256':ident,'volume_id':volume.object_id,'files':files})
    upload(provider,volume.object_id,binding['closure']['wheel_root'],files)
    ready={'schema':'closure-wheel-volume/v1','binding_sha256':ident,'app_id':app.app_id,
           'volume_id':volume.object_id,'files':files,'files_sha256':digest(canonical(files)),
           'created_at':created.isoformat(),'expires_at':(created+timedelta(days=30)).isoformat(),
           'retention_days':30,'reserved_storage_days':35}
    record(root,'wheels-ready',ready)
    return ready


def wheel_receipt(binding,handle,record_root):
    raw=pr.check(Path(record_root)/'wheels-ready.json').read_bytes();value=strict_json(raw)
    fields={'schema','binding_sha256','app_id','volume_id','files','files_sha256',
            'created_at','expires_at','retention_days','reserved_storage_days'}
    files=binding['closure']['selection']['wheels']
    if (set(value)!=fields or value['schema']!='closure-wheel-volume/v1' or
            value['binding_sha256']!=digest(canonical(binding)) or
            value['app_id']!=handle['app_id'] or value['volume_id']!=handle['wheel_volume_id'] or
            value['files']!=files or value['files_sha256']!=digest(canonical(files)) or
            digest(raw)!=handle['wheel_receipt_sha256'] or
            value['retention_days']!=30 or value['reserved_storage_days']!=35):
        raise ValueError('CLOSURE_WHEEL_RECEIPT_BINDING')
    created=datetime.fromisoformat(value['created_at']);expires=datetime.fromisoformat(value['expires_at'])
    if created.tzinfo is None or expires-created!=timedelta(days=30):
        raise ValueError('CLOSURE_WHEEL_RETENTION_BINDING')
    return value


def consumer_proof(accounts,binding,state,*,now=None):
    """Read-only downstream handoff from actual READY native evidence only."""
    from orchestrator import modal_environment_budget as budget
    from orchestrator.modal_environment_provider import observe
    now=now or datetime.now(timezone.utc);state=Path(state);ident=digest(canonical(binding))
    budget.validate_binding(binding)
    row=accounts.db.execute('SELECT * FROM autonomy_assets WHERE id=?',(ident,)).fetchone()
    owner=accounts.db.execute('SELECT * FROM autonomy_runs WHERE id=?',(binding['run_id'],)).fetchone()
    if (row is None or row['status']!='READY' or row['binding']!=canonical(binding).decode() or
            not budget.selected_asset(row) or owner is None or owner['status']!='COMPLETE' or
            strict_json(owner['binding'])!=budget.owner(binding)):
        raise ValueError('CLOSURE_ACCEPTED_PROVENANCE_REQUIRED')
    handle=strict_json(pr.check(state/'provider/sandbox.json').read_bytes())
    wheels=wheel_receipt(binding,handle,state/'provider')
    if (now>=datetime.fromisoformat(wheels['expires_at']) or (state/'retention').exists()):
        raise ValueError('CLOSURE_WHEELS_EXPIRED_OR_HELD')
    native=observe(None,binding,handle,state/'provider')
    expected={**native,'binding_sha256':ident,'source':binding['source'],'scientific_calls':0,
              'scope':'Offline dependency closure only; no patient computation, scientific acceptance or GPU validation'}
    if (native['status']!='VERIFIED' or strict_json(row['receipt'])!=expected or
            strict_json(pr.check(state/'VERIFIED.json').read_bytes())!=expected):
        raise ValueError('CLOSURE_ACCEPTED_PROVENANCE_CHANGED')
    local_wheels(binding['closure'])
    return {'schema':'closure-consumer-provenance/v1','binding_sha256':ident,
            'asset_receipt_sha256':digest(row['receipt'].encode()),
            'native_receipt_sha256':digest(pr.check(state/'provider/outcome.json').read_bytes()),
            'wheel_receipt_sha256':handle['wheel_receipt_sha256'],'wheel_volume_id':wheels['volume_id'],
            'wheel_files':wheels['files'],'expires_at':wheels['expires_at'],
            'scientific_environment':native['dependency_closure']['scientific_environment'],
            'environment_sha256':native['dependency_closure']['environment_sha256'],
            'scientific_acceptance':False,'gpu_verified':False}


@pr.private_umask
def expire(provider,accounts,binding,handle,state,now):
    from orchestrator.modal_environment_provider import observe,record
    from orchestrator.modal_cleanup import remove_members
    from orchestrator.modal_assets import local_files
    state=Path(state);ready=wheel_receipt(binding,handle,state/'provider')
    if now<datetime.fromisoformat(ready['expires_at']):return {'status':'NOT_DUE'}
    ident=digest(canonical(binding))
    folder=state/'retention';refusal=folder/'REFUSAL.json'
    if refusal.exists():
        value=strict_json(pr.check(refusal).read_bytes())
        if value.get('binding_sha256')!=ident or value.get('automatic_cleanup_retry') is not False:
            raise ValueError('CLOSURE_RETENTION_REFUSAL_CHANGED')
        return value
    def hold(code):
        pr.mkdir(folder,exist_ok=True)
        value={'status':code,'preserved':True,'binding_sha256':ident,
               'storage_may_continue_accruing':True,'recorded_at':now.isoformat(),
               'automatic_cleanup_retry':False}
        record(folder,'REFUSAL',value);return value
    row=accounts.db.execute('SELECT * FROM autonomy_assets WHERE id=?',(ident,)).fetchone()
    if row is None or row['binding']!=canonical(binding).decode():raise ValueError('CLOSURE_RETENTION_LEDGER_BINDING')
    if row['status']!='READY':return hold('EXPIRY_BLOCKED_INCOMPLETE_ATTEMPT')
    pending=accounts.db.execute("SELECT 1 FROM autonomy_compute WHERE status NOT IN ('COLLECTED','ACCOUNTED')").fetchone()
    if pending:return hold('EXPIRY_WAIT_ACTIVE_COMPUTE')
    # Scientific ownership is a dependency even before its first fit reserves.
    owners=accounts.db.execute("SELECT id FROM autonomy_runs WHERE status!='COMPLETE' AND id!=?",(binding['run_id'],)).fetchone()
    if owners:return hold('EXPIRY_WAIT_ACTIVE_DEPENDENCY')
    proof=observe(None,binding,handle,state/'provider')
    accepted=strict_json(row['receipt'])
    if proof['status']!='VERIFIED' or any(accepted.get(k)!=v for k,v in proof.items()):
        raise ValueError('CLOSURE_RETENTION_ACCEPTANCE_CHANGED')
    files=ready['files'];local_files(binding['closure']['wheel_root'],files)
    folder=state/'retention';pr.mkdir(folder,exist_ok=True)
    payload={'binding_sha256':ident,'volume_id':ready['volume_id'],'files':files,
             'wheel_receipt_sha256':handle['wheel_receipt_sha256']}
    done=folder/'COMPLETE.json'
    if done.exists():
        value=strict_json(pr.check(done).read_bytes())
        if value.get('binding')!=payload:raise ValueError('CLOSURE_RETENTION_COMPLETION_BINDING')
        return value
    if provider is None:return {'status':'RETENTION_DUE'}
    if provider._sandbox(handle['provider_id']).poll() is None:return hold('EXPIRY_WAIT_ACTIVE_CLOSURE')
    intent=folder/'intent.json'
    if not intent.exists():
        provider._verify_volume(ready['volume_id'],files)
        record(folder,'intent',payload)
    elif strict_json(pr.check(intent).read_bytes())!=payload:raise ValueError('CLOSURE_RETENTION_INTENT_CHANGED')
    try:remove_members(provider,ready['volume_id'],files,folder,'wheels')
    except (OSError,ValueError):return hold('EXPIRY_REFUSED_MEMBER_CLEANUP')
    result={'status':'WHEEL_COPIES_EXPIRED','binding':payload,'originals_and_evidence_preserved':True,
            'no_refund_or_allowance_reset':True}
    record(folder,'COMPLETE',result)
    return result


def arguments(binding):
    value=validate(binding['closure'])
    return (value['selection']['python_executable'],'-I','-B','-c',BOOTSTRAP,
            payload(value,digest(canonical(binding))))


def validate_result(raw,binding):
    return closure.validate_result(raw,binding['closure']['selection'],digest(canonical(binding)))
