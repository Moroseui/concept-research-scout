"""One reserved, CPU-only inventory of an existing image; no mounts or data.

The command is fixed reviewed stdlib code. A preserved create intent forbids
relaunch after any uncertainty. Terminal captures are bounded and replayable.
"""
from datetime import datetime, timezone
from pathlib import Path
import re

from orchestrator import private_records as pr
from orchestrator import modal_native_synthetic as synthetic
from orchestrator import modal_pinned_image as pinned
from orchestrator.modal_executor import canonical
from orchestrator.manual_executor import digest
from orchestrator.manual_driver import write_once
from orchestrator.review_contract import strict_json
from orchestrator.modal_environment_budget import PURPOSE, RESOURCES, validate_binding, selected_operation

MAX_STDOUT = 256 * 1024
MAX_STDERR = 16 * 1024
IMPORTS = ('numpy','scipy','torch','nibabel','pandas','sklearn','nnunetv2','batchgenerators')
CONSOLES = ('pip','nnUNetv2_train','nnUNetv2_predict','nnUNetv2_plan_and_preprocess')
WORKER = r"""import importlib.metadata as md
import importlib.util
import json
from pathlib import Path
import platform
import sys
imports = ('numpy','scipy','torch','nibabel','pandas','sklearn','nnunetv2','batchgenerators')
consoles = ('pip','nnUNetv2_train','nnUNetv2_predict','nnUNetv2_plan_and_preprocess')
def distribution_inventory(discovered):
    # Counts are metadata discoveries, not a claim of multiple installations.
    # Ubuntu can supply both dist-info and egg-info for the same name/version.
    counts={};total=0
    for d in discovered:
        total+=1
        if total>2000: raise RuntimeError('INVENTORY_DISTRIBUTION_LIMIT')
        key=(d.metadata['Name'].lower(),d.version)
        counts[key]=counts.get(key,0)+1
    return [{'name':name,'version':version,'metadata_occurrences':count}
            for (name,version),count in sorted(counts.items())]
distributions = distribution_inventory(md.distributions())
points=md.entry_points()
entries = {x.name for x in (points.select(group='console_scripts') if hasattr(points,'select') else points.get('console_scripts',()))}
cuda = None
path = Path('/usr/local/cuda/version.json')
if path.is_file():
    with path.open('rb') as f: raw=f.read(16385)
    if len(raw)>16384: raise RuntimeError('INVENTORY_CUDA_LIMIT')
    value=json.loads(raw)
    cuda={k:v['version'] for k,v in value.items() if k in ('cuda','cuda_cudart','cuda_nvcc') and isinstance(v,dict) and 'version' in v}
result={'schema':'image-environment-inventory/v1','worker_sha256':sys.argv[1],'image_id':sys.argv[2],
    'executable':sys.executable,'python_version':platform.python_version(),'implementation':platform.python_implementation(),
    'platform':{'system':platform.system(),'machine':platform.machine(),'release':platform.release(),'libc':list(platform.libc_ver())},
    'distributions':distributions,'availability':{'imports':{x:importlib.util.find_spec(x) is not None for x in imports},'consoles':{x:x in entries for x in consoles}},'cuda':cuda}
raw=json.dumps(result,sort_keys=True,separators=(',',':')).encode('utf-8')
if len(raw)>262144: raise RuntimeError('INVENTORY_OUTPUT_LIMIT')
sys.stdout.buffer.write(raw+b'\n')
"""
WORKER_SHA256 = digest(WORKER.encode())


def text(value, maximum=128, *, pattern=r'[A-Za-z0-9_.+(): /-]+'):
    return isinstance(value,str) and 0<len(value)<=maximum and re.fullmatch(pattern,value) is not None


def worker_pin(binding):
    if binding.get("purpose")==synthetic.PURPOSE:return synthetic.worker_sha256()
    if pinned.is_build(binding.get('purpose')):return pinned.worker_sha256()
    if binding.get('purpose') != PURPOSE:
        from orchestrator.modal_environment_closure_route import worker_sha256
        return worker_sha256()
    return WORKER_SHA256


def validate_result(raw, binding):
    if binding.get("purpose")==synthetic.PURPOSE:return synthetic.validate_result(raw,binding)
    if pinned.is_build(binding.get('purpose')):return pinned.validate_result(raw,binding)
    if binding.get('purpose') != PURPOSE:
        from orchestrator.modal_environment_closure_route import validate_result as closure_result
        return closure_result(raw,binding)
    """Strict metadata contract. No paths beyond the selected native executable."""
    if not isinstance(raw,bytes) or len(raw)>MAX_STDOUT:raise ValueError('ENVIRONMENT_OUTPUT_BOUND')
    value=strict_json(raw)
    fields={'schema','worker_sha256','image_id','executable','python_version','implementation','platform','distributions','availability','cuda'}
    if (not isinstance(value,dict) or set(value)!=fields or value['schema']!='image-environment-inventory/v1'
            or value['worker_sha256']!=WORKER_SHA256 or value['worker_sha256']!=binding['worker_sha256']
            or value['image_id']!=binding['image_id'] or value['executable']!='/usr/bin/python3'
            or not text(value['python_version'],32,pattern=r'[0-9]+\.[0-9]+\.[0-9]+')
            or value['implementation']!='CPython'):
        raise ValueError('ENVIRONMENT_OUTPUT_BINDING')
    platform=value['platform']
    if (not isinstance(platform,dict) or set(platform)!={'system','machine','release','libc'}
            or platform['system']!='Linux' or not text(platform['machine'],32)
            or not text(platform['release'],128) or not isinstance(platform['libc'],list)
            or len(platform['libc'])!=2 or any(not text(x,64) for x in platform['libc'])):
        raise ValueError('ENVIRONMENT_PLATFORM_METADATA')
    distributions=value['distributions']
    if not isinstance(distributions,list) or len(distributions)>2000:raise ValueError('ENVIRONMENT_DISTRIBUTION_METADATA')
    for row in distributions:
        if (not isinstance(row,dict) or set(row)!={'name','version','metadata_occurrences'}
                or not text(row['name'],128,pattern=r'[A-Za-z0-9][A-Za-z0-9_.-]*')
                or row['name']!=row['name'].lower()
                or not text(row['version'],128,pattern=r'[A-Za-z0-9][A-Za-z0-9_.+!-]*')
                or type(row['metadata_occurrences']) is not int or not 1<=row['metadata_occurrences']<=2000):
            raise ValueError('ENVIRONMENT_DISTRIBUTION_METADATA')
    if sum(row['metadata_occurrences'] for row in distributions)>2000:raise ValueError('ENVIRONMENT_DISTRIBUTION_METADATA')
    keys=[(row['name'],row['version']) for row in distributions]
    if keys!=sorted(keys) or len(set(keys))!=len(keys):raise ValueError('ENVIRONMENT_DISTRIBUTION_METADATA')
    availability=value['availability']
    if not isinstance(availability,dict) or set(availability)!={'imports','consoles'}:raise ValueError('ENVIRONMENT_AVAILABILITY_METADATA')
    for family,expected in [('imports',IMPORTS),('consoles',CONSOLES)]:
        observed=availability[family]
        if not isinstance(observed,dict) or set(observed)!=set(expected) or any(type(x) is not bool for x in observed.values()):
            raise ValueError('ENVIRONMENT_AVAILABILITY_METADATA')
    cuda=value['cuda']
    if cuda is not None and (not isinstance(cuda,dict) or not set(cuda)<={'cuda','cuda_cudart','cuda_nvcc'}
            or any(not text(x,64,pattern=r'[0-9][0-9A-Za-z_.+-]*') for x in cuda.values())):
        raise ValueError('ENVIRONMENT_CUDA_METADATA')
    return value


def require_reserved(accounts,binding):
    validate_binding(binding)
    if binding['worker_sha256']!=worker_pin(binding):raise ValueError('ENVIRONMENT_WORKER_CHANGED')
    ident=digest(canonical(binding))
    row=accounts.db.execute('SELECT * FROM autonomy_assets WHERE id=?',(ident,)).fetchone()
    if (row is None or row['status']!='RESERVED' or row['binding']!=canonical(binding).decode()
            or row['run']!=binding['run_id'] or not selected_operation(row)):
        raise ValueError('ENVIRONMENT_RESERVED_BINDING_REQUIRED')
    if binding['purpose'] not in {PURPOSE,synthetic.PURPOSE} and not pinned.is_build(binding['purpose']):
        from orchestrator.modal_environment_closure_route import local_wheels
        local_wheels(binding['closure'])
    if binding['purpose']==pinned.CPU_PURPOSE:
        from orchestrator import modal_diagnostics_image as cpu
        cpu.owner(accounts,binding);cpu.reviewed(binding['reviewed_requirements'])
    elif binding['purpose'] in {pinned.PURPOSE,synthetic.PURPOSE}:pinned.item4_owner(accounts,binding)
    return ident


def record(root,name,value):
    write_once(Path(root)/(name+'.json'),canonical(value))
    pr.check(Path(root)/(name+'.json'))


@pr.private_umask
def launch(provider,accounts,binding,record_root):
    ident=require_reserved(accounts,binding)
    root=Path(record_root)
    if root.exists() or root.is_symlink():raise ValueError('ENVIRONMENT_EXISTING_INTENT_RECONCILE')
    if provider.config['workspace']!='moroseui':raise ValueError('MODAL_APPROVED_WORKSPACE')
    provider.client.hello()
    ws=provider.modal.Workspace.from_context(client=provider.client);ws.hydrate(client=provider.client)
    if ws.name!='moroseui':raise ValueError('MODAL_AUTHENTICATED_WORKSPACE')
    pr.mkdir(root,parents=True)
    record(root,'intent',{'binding':binding,'binding_sha256':ident,'created_at':datetime.now(timezone.utc).isoformat()})
    name=('research-item6-image-' if binding['purpose']==pinned.CPU_PURPOSE else 'research-item4-environment-')+ident[:24]
    record(root,'app-intent',{'name':name})
    try:provider.modal.App.lookup(name,create_if_missing=False,client=provider.client)
    except provider.modal.exception.NotFoundError:pass
    else:raise ValueError('ENVIRONMENT_APP_EXISTS')
    app=provider.modal.App.lookup(name,create_if_missing=True,client=provider.client)
    if not text(app.app_id,128,pattern=r'ap-[A-Za-z0-9_-]+'):raise ValueError('ENVIRONMENT_APP_ID')
    record(root,'app',{'name':name,'app_id':app.app_id})
    # ImageFromId resolves an existing immutable native ID; no registry import,
    # RUN layer, dependency install, mount or implicit new image is permitted.
    record(root,'image-intent',{'image_id':binding['image_id'],'registry':binding['base_image'],'operation':'existing-image-from-id'})
    image=provider.modal.Image.from_id(binding['image_id'],client=provider.client)
    image.build(app)
    if image.object_id!=binding['image_id']:raise ValueError('ENVIRONMENT_IMAGE_CHANGED')
    record(root,'image',{'image_id':image.object_id,'registry':binding['base_image']})
    resources=binding['envelope'].get('proof_resources',binding['envelope']['resources']);mounts={};wheel_ready=None
    if pinned.is_build(binding['purpose']):
        image=pinned.build_image(provider,binding,app,image,root)
        args=pinned.arguments(binding,image.object_id)
    elif binding['purpose']==synthetic.PURPOSE:
        args=synthetic.arguments(binding)
    elif binding['purpose'] == PURPOSE:
        args=('/usr/bin/python3','-I','-B','-c',WORKER,WORKER_SHA256,binding['image_id'])
    else:
        from orchestrator.modal_environment_closure_route import arguments,prepare_wheels
        wheel_ready=prepare_wheels(provider,binding,app,root)
        mounts={'/wheels':provider._volume(wheel_ready['volume_id']).with_mount_options(read_only=True)}
        args=arguments(binding)
    record(root,'sandbox-intent',{'binding_sha256':ident,'args':args,'resources':resources,
        'block_network':True,'mounts':{'/wheels':wheel_ready['volume_id']} if mounts else {},'secrets':[],'environment':{},'oidc':False})
    filters={} if binding['purpose']==synthetic.PURPOSE else {
        'outbound_cidr_allowlist':[],'outbound_domain_allowlist':[],'inbound_cidr_allowlist':[]}
    sb=provider.modal.Sandbox.create(*args,app=app,name='environment-'+ident[:32],image=image,
        gpu=None,cpu=(resources['cpu'],resources['cpu']),memory=(resources['memory_mib'],resources['memory_mib']),timeout=resources['timeout_seconds'],
        block_network=True,**filters,include_oidc_identity_token=False,secrets=[],env={},
        encrypted_ports=[],h2_ports=[],unencrypted_ports=[],volumes=mounts,client=provider.client)
    if not text(sb.object_id,128,pattern=r'sb-[A-Za-z0-9_-]+'):raise ValueError('ENVIRONMENT_PROVIDER_ID')
    handle={'provider_id':sb.object_id,'app_id':app.app_id,'image_id':image.object_id,
        'binding_sha256':ident,'worker_sha256':worker_pin(binding),'launched_at':datetime.now(timezone.utc).isoformat()}
    if wheel_ready is not None:
        handle.update(wheel_volume_id=wheel_ready['volume_id'],wheel_receipt_sha256=digest(canonical(wheel_ready)))
    record(root,'sandbox',handle)
    if binding['purpose']==synthetic.PURPOSE:synthetic.send_stdin(sb,binding,root)
    return handle


def bounded(stream,limit):
    raw=bytearray();truncated=False;error=None
    try:
        for chunk in stream:
            data=chunk.encode('utf-8') if isinstance(chunk,str) else bytes(chunk)
            room=limit-len(raw)
            raw.extend(data[:room])
            if len(data)>room:truncated=True;break
    except Exception:
        error='STREAM_READ_FAILED'
    return bytes(raw),{'bytes':len(raw),'sha256':digest(raw),'truncated':truncated,'read_error':error}


def outcome(binding,handle,terminal,stdout,stderr):
    result={'provider_id':handle['provider_id'],'app_id':handle['app_id'],
        'image_id':handle['image_id'],'worker_sha256':worker_pin(binding),
        'binding_sha256':digest(canonical(binding)),'exit_code':terminal['exit_code'],
        'streams':terminal['streams'],'patient_computation':False,'no_automatic_retry':True}
    reason=None
    if type(terminal['exit_code']) is not int or terminal['exit_code']!=0:reason='ENVIRONMENT_NONZERO_OR_UNKNOWN_EXIT'
    elif any(x['truncated'] or x['read_error'] for x in terminal['streams'].values()):reason='ENVIRONMENT_OUTPUT_INCOMPLETE'
    elif stderr:reason='ENVIRONMENT_STDERR_NOT_EMPTY'
    else:
        try:value=validate_result(stdout,binding)
        except (ValueError,TypeError,KeyError):reason='ENVIRONMENT_OUTPUT_INVALID'
    if reason:return {**result,'status':'UNCERTAIN','reason':reason}
    if pinned.is_build(binding['purpose']) and value['image_id']!=handle['image_id']:
        return {**result,'status':'UNCERTAIN','reason':'PINNED_IMAGE_OBSERVED_ID_CHANGED'}
    key='native_synthetic' if binding['purpose']==synthetic.PURPOSE else 'pinned_image' if pinned.is_build(binding['purpose']) else 'inventory' if binding['purpose']==PURPOSE else 'dependency_closure'
    if binding['purpose'] not in {PURPOSE,synthetic.PURPOSE} and not pinned.is_build(binding['purpose']):
        result.update(wheel_volume_id=handle['wheel_volume_id'],wheel_receipt_sha256=handle['wheel_receipt_sha256'])
    return {**result,'status':'VERIFIED',key:value,key+'_sha256':digest(stdout)}


@pr.private_umask
def observe(provider,binding,handle,record_root):
    validate_binding(binding)
    if binding['worker_sha256']!=worker_pin(binding):raise ValueError('ENVIRONMENT_WORKER_CHANGED')
    root=Path(record_root);pr.check_tree(root)
    # Check all immutable identities before any provider request or cache reuse.
    intent=strict_json(pr.check(root/'intent.json').read_bytes())
    saved=strict_json(pr.check(root/'sandbox.json').read_bytes())
    if (intent['binding']!=binding or intent['binding_sha256']!=digest(canonical(binding))
            or saved!=handle or handle['binding_sha256']!=digest(canonical(binding))
            or handle['worker_sha256']!=worker_pin(binding) or (not pinned.is_build(binding['purpose']) and handle['image_id']!=binding['image_id'])):
        raise ValueError('ENVIRONMENT_HANDLE_BINDING')
    if pinned.is_build(binding['purpose']):pinned.image_identity(binding,root,handle)
    elif binding['purpose'] not in {PURPOSE,synthetic.PURPOSE}:
        from orchestrator.modal_environment_closure_route import wheel_receipt
        wheel_receipt(binding,handle,root)
    finished=root/'outcome.json'
    if finished.exists():
        terminal=strict_json(pr.check(root/'terminal.json').read_bytes())
        streams={key:pr.check(root/(key+'.bin')).read_bytes() for key in ('stdout','stderr')}
        for key,limit in [('stdout',MAX_STDOUT),('stderr',MAX_STDERR)]:
            meta=terminal['streams'][key];raw=streams[key]
            if len(raw)>limit or len(raw)!=meta['bytes'] or digest(raw)!=meta['sha256']:
                raise ValueError('ENVIRONMENT_PRESERVED_OUTPUT_CHANGED')
        result=outcome(binding,handle,terminal,streams['stdout'],streams['stderr'])
        if binding['purpose']==synthetic.PURPOSE and result['status']=='VERIFIED':synthetic.verify_stdin(binding,root)
        if strict_json(pr.check(finished).read_bytes())!=result:raise ValueError('ENVIRONMENT_PRESERVED_OUTCOME_CHANGED')
        return result
    if any((root/name).exists() for name in ('terminal.json','stdout.bin','stderr.bin')):
        raise ValueError('ENVIRONMENT_PARTIAL_OBSERVATION_RECONCILE')
    sb=provider._sandbox(handle['provider_id'])
    if sb.object_id!=handle['provider_id']:raise ValueError('ENVIRONMENT_PROVIDER_ID_CHANGED')
    code=sb.poll()
    if code is None:return {'status':'RUNNING','provider_id':handle['provider_id']}
    stdout,out_meta=bounded(sb.stdout,MAX_STDOUT);stderr,err_meta=bounded(sb.stderr,MAX_STDERR)
    terminal={'exit_code':code,'streams':{'stdout':out_meta,'stderr':err_meta}}
    for name,raw in [('stdout.bin',stdout),('stderr.bin',stderr)]:write_once(root/name,raw);pr.check(root/name)
    record(root,'terminal',terminal)
    result=outcome(binding,handle,terminal,stdout,stderr)
    if binding['purpose']==synthetic.PURPOSE and result['status']=='VERIFIED':synthetic.verify_stdin(binding,root)
    record(root,'outcome',result)
    return result
