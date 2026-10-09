"""One standard pinned-image build in the existing no-patient asset lifecycle."""
from decimal import Decimal, ROUND_CEILING
from pathlib import Path
import importlib.util
import re
import sys
from orchestrator import private_records as pr
from orchestrator.manual_executor import digest
from orchestrator.manual_driver import write_once
from orchestrator.modal_executor import canonical
from orchestrator.modal_item4_policy import AUTHORITY, quote
from orchestrator.modal_billing import decimal
from orchestrator.review_contract import strict_json
from tools import pinned_image_builder as worker

PURPOSE='M4_ITEM4_PINNED_IMAGE_BUILD'
OPERATION='item4-pinned-scientific-image-v1'
from orchestrator.experiment_context import ITEM4_RUN
RUN=ITEM4_RUN
SCHEMA='item4-pinned-image-build/v1'
RESOURCES={'gpu':None,'cpu':2,'memory_mib':8192,'timeout_seconds':1800}
PROOF_RESOURCES={'gpu':None,'cpu':1,'memory_mib':4096,'timeout_seconds':300}
SPEC='modal-pinned-image/v1'


CPU_PURPOSE='M4_ITEM6_PINNED_IMAGE_BUILD'
def is_build(purpose):return purpose in {PURPOSE,CPU_PURPOSE}

def item4_owner(accounts,binding):
    """Read the original canonical owner; image prep never creates/completes it."""
    from orchestrator import experiment_context as context
    from orchestrator.modal_native_synthetic import PURPOSE as NATIVE_PURPOSE
    from tools.deploy_manual_lane import bound
    row=accounts.db.execute('SELECT binding,status FROM autonomy_runs WHERE id=?',(RUN,)).fetchone()
    if row is None or row['status']!='ACTIVE':raise ValueError('ITEM4_IMAGE_ACTIVE_OWNER_REQUIRED')
    owner=strict_json(row['binding'])
    from orchestrator.spending_continuation import lane
    continued=lane(accounts.batch,RUN,owner,binding.get('source'),image=True)
    fields={'state','source','run_id','plan_sha256','review_sha256','execution_scope'}
    if (not isinstance(owner,dict) or set(owner)!=fields or binding.get('purpose') not in {PURPOSE,NATIVE_PURPOSE}
            or binding.get('run_id')!=RUN or binding.get('authority_sha256')!=AUTHORITY
            or owner.get('run_id')!=RUN or (continued is None and owner.get('source')!=binding.get('source'))
            or digest(canonical(owner))!=binding.get('owner_sha256')
            or not isinstance(owner.get('state'),str) or not Path(owner['state']).is_absolute()):
        raise ValueError('ITEM4_IMAGE_EXISTING_OWNER_CHANGED')
    state=continued[0] if continued else bound(accounts.batch.filesystem_root,owner['state'])
    config=strict_json(pr.check(state/'lane.json').read_bytes())
    raw=pr.check(state/'preparation-plan.json').read_bytes();plan=strict_json(raw)
    if (config.get('owner_binding')!=owner or config.get('run_id')!=RUN
            or config.get('source')!=(continued[1]['source'] if continued else owner['source']) or config.get('plan_sha256')!=digest(raw)
            or owner['plan_sha256']!=digest(raw) or config.get('execution_scope')!=owner['execution_scope']
            or (continued is None and config.get('engine_review',{}).get('sha256')!=owner['review_sha256'])):
        raise ValueError('ITEM4_IMAGE_EXISTING_OWNER_CHANGED')
    selected=context.validate_selection(config,plan,bound(accounts.batch.filesystem_root,config['context']))
    if selected['item_number']!=4 or selected['authority_sha256']!=AUTHORITY:
        raise ValueError('ITEM4_IMAGE_EXISTING_OWNER_CHANGED')
    return owner


def worker_sha256():return digest(Path(worker.__file__).read_bytes())
def validate(value):worker.selection(value);return value


def envelope(rates):
    keys=('cpu_hour_cost','mem_gib_hour_cost','cpu_hour_cost_sandbox','mem_gib_hour_cost_sandbox')
    if any(k not in rates or decimal(rates[k])<=0 for k in keys):raise ValueError('PINNED_IMAGE_ACTUAL_BUILD_RATES_REQUIRED')
    compute=int(((2*decimal(rates[keys[0]])+8*decimal(rates[keys[1]]))*Decimal(3600)/3600*1000000).to_integral_value(rounding=ROUND_CEILING))
    proof=quote(PROOF_RESOURCES,rates,0)['compute_micro_usd']
    return {'resources':dict(RESOURCES),'proof_resources':dict(PROOF_RESOURCES),
        'cost':{'compute_micro_usd':compute+proof,'overhead_micro_usd':1000000,
                'reserved_micro_usd':compute+proof+1000000,'rates':{k:str(decimal(rates[k])) for k in keys},
                'basis':'fixed build-function hard CPU/RAM maxima, 1800s startup plus 1800s execution; network-blocked 300s proof; full image overhead'}}


def stage_builder(root):
    """The SDK receives one standalone module, never the checkout package."""
    root=Path(root);pr.mkdir(root)
    raw=Path(worker.__file__).read_bytes();path=root/'pinned_image_builder.py'
    write_once(path,raw);pr.check_tree(root)
    if {p.name for p in root.iterdir()}!={path.name}:raise ValueError('PINNED_IMAGE_SOURCE_MEMBERS')
    return path,{'files':{path.name:{'sha256':digest(raw),'bytes':len(raw)}},
        'no_patient_files':True,'no_credentials':True,'lock_transport':'exact validated kwargs only'}


def build_image(provider,binding,app,image,root):
    from orchestrator.modal_environment_provider import record
    selected=validate(binding['image_build']);root=Path(root)
    if image.object_id!=binding['image_id']:raise ValueError('PINNED_IMAGE_BASE_CHANGED')
    path,manifest=stage_builder(root/'build-source')
    # Import with a standalone module name. SDK FunctionSourceInfo FILE mounts
    # only this file; PACKAGE would mount the whole top-level package.
    module_name='research_pinned_image_builder'
    spec=importlib.util.spec_from_file_location(module_name,path)
    module=importlib.util.module_from_spec(spec);sys.modules[module_name]=module
    try:
        spec.loader.exec_module(module)
        if module.__package__ or Path(module.__file__)!=path:raise ValueError('PINNED_IMAGE_SOURCE_MODULE')
        from modal._utils.function_utils import FunctionSourceInfo
        info=FunctionSourceInfo(module.build)
        mounts=info.get_entrypoint_mount()
        if info._type.name!='FILE' or len(mounts)!=1:raise ValueError('PINNED_IMAGE_SOURCE_SCOPE')
        # The exact local_file is independently checked, not merely a class name.
        for mount in mounts.values():
            entries=list(mount._entries)
            if len(entries)!=1 or Path(entries[0].local_file)!=path:raise ValueError('PINNED_IMAGE_SOURCE_SCOPE')
        lock=worker.selection(selected)
        kwargs={'selected':selected,'selection_sha256':digest(worker.encoded(selected)),'builder_sha256':worker_sha256()}
        if len(canonical(kwargs))>100000:raise ValueError('PINNED_IMAGE_BUILD_ARGUMENT_LIMIT')
        record(root,'build-intent',{'binding_sha256':digest(canonical(binding)),
            'base_image_id':image.object_id,'base_registry':binding['base_image'],
            'source_manifest':manifest,'selection_sha256':kwargs['selection_sha256'],
            'lock_sha256':digest(lock.encode()),'resources':RESOURCES,
            'secrets':[],'volumes':{},'network_file_systems':{},'gpu':None,
            'builder_sha256':worker_sha256(),'derived_oci_digest':None})
        built=image.run_function(module.build,cpu=(2,2),memory=(8192,8192),timeout=1800,
            secrets=[],volumes={},network_file_systems={},gpu=None,include_source=True,kwargs=kwargs)
        built.build(app)
        if not re.fullmatch(r'im-[A-Za-z0-9]+',built.object_id) or built.object_id==binding['image_id']:
            raise ValueError('PINNED_IMAGE_RESULT_ID')
        record(root,'built-image',{'image_id':built.object_id,'base_image_id':binding['image_id'],
            'builder_sha256':worker_sha256(),'selection_sha256':kwargs['selection_sha256'],
            'lock_sha256':digest(lock.encode()),'source_manifest':manifest,
            'derived_oci_digest':None,'identity_basis':'native immutable image ID; API exposes no derived OCI digest'})
        return built
    finally:sys.modules.pop(module_name,None)


PROBE=r"""import hashlib,importlib.metadata,json,pathlib,sys
p=pathlib.Path('/opt/research-scientific-python/native-proof.json')
if p.stat().st_size>131072:raise RuntimeError('PINNED_IMAGE_PROOF_SIZE')
raw=p.read_bytes()
if len(raw)>131072:raise RuntimeError('PINNED_IMAGE_PROOF_SIZE')
def unique(pairs):
 d={}
 for k,v in pairs:
  if k in d:raise RuntimeError('PINNED_IMAGE_DUPLICATE_JSON')
  d[k]=v
 return d
v=json.loads(raw,object_pairs_hook=unique)
cuda=None
if 'torch' in v['actual']['packages']:
 import torch
 cuda=torch.version.cuda
actual={'python':sys.version,'cuda':cuda,'packages':{n:importlib.metadata.version(n) for n in v['actual']['packages']}}
if actual!=v['actual']:raise RuntimeError('PINNED_IMAGE_PROOF_DRIFT')
print(json.dumps({'schema':'pinned-image-verified/v1','image_id':sys.argv[1],'binding_sha256':sys.argv[2], 'native_sha256':hashlib.sha256(raw).hexdigest(),'native':v},sort_keys=True))
"""


def arguments(binding,image_id):
    return (worker.TARGET+'/bin/python','-I','-B','-c',PROBE,image_id,digest(canonical(binding)))


def image_identity(binding,root,handle):
    root=Path(root);value=strict_json(pr.check(root/'built-image.json').read_bytes())
    expected={'image_id':handle['image_id'],'base_image_id':binding['image_id'],
        'builder_sha256':worker_sha256(),'selection_sha256':digest(worker.encoded(binding['image_build'])),
        'lock_sha256':digest(worker.selection(binding['image_build']).encode()),
        'source_manifest':{'files':{'pinned_image_builder.py':{'sha256':worker_sha256(),'bytes':Path(worker.__file__).stat().st_size}},
            'no_patient_files':True,'no_credentials':True,'lock_transport':'exact validated kwargs only'},
        'derived_oci_digest':None,'identity_basis':'native immutable image ID; API exposes no derived OCI digest'}
    if value!=expected or handle['image_id']==binding['image_id']:raise ValueError('PINNED_IMAGE_BUILT_BINDING')
    path=pr.check(root/'build-source/pinned_image_builder.py')
    if digest(path.read_bytes())!=worker_sha256():raise ValueError('PINNED_IMAGE_PRESERVED_SOURCE')
    return value


def validate_result(raw,binding):
    if not isinstance(raw,bytes) or len(raw)>262144:raise ValueError('PINNED_IMAGE_RESULT_BOUND')
    value=strict_json(raw);selected=validate(binding['image_build']);native=value.get('native')
    if (set(value)!={'schema','image_id','binding_sha256','native_sha256','native'}
            or value['schema']!='pinned-image-verified/v1'
            or value['binding_sha256']!=digest(canonical(binding))
            or not re.fullmatch(r'im-[A-Za-z0-9]+',str(value['image_id']))
            or value['image_id']==binding['image_id'] or not isinstance(native,dict)
            or digest(worker.encoded(native))!=value['native_sha256']):raise ValueError('PINNED_IMAGE_RESULT_BINDING')
    is_cpu=worker.cpu(selected)
    if is_cpu != (binding['purpose']==CPU_PURPOSE):raise ValueError('PINNED_IMAGE_PURPOSE_SELECTION')
    fields={'schema','selection_sha256','builder_sha256','lock_sha256','actual','imports','trainers','reader','console_help','patient_computation','gpu_verified'}
    if (set(native)!=fields or native['schema']!='pinned-modal-image-native/v1'
            or native['selection_sha256']!=digest(worker.encoded(selected))
            or native['builder_sha256']!=worker_sha256()
            or native['lock_sha256']!=digest(worker.selection(selected).encode())
            or native['patient_computation'] is not False or native['gpu_verified'] is not False
            or native['imports']!=({} if is_cpu else {n:n for n in worker.IMPORTS})
            or native['trainers']!=({} if is_cpu else {n:worker.PARAMETERS for n in worker.TRAINERS})
            or native['reader']!=(None if is_cpu else 'SimpleITKIO')):raise ValueError('PINNED_IMAGE_NATIVE_BINDING')
    actual=native['actual']
    if (not isinstance(actual,dict) or set(actual)!={'python','cuda','packages'}
            or actual['packages']!=selected['packages'] or actual['cuda']!=selected['cuda']
            or not isinstance(actual['python'],str) or len(actual['python'])>500
            or actual['python'].split(' ')[0]!=selected['python_version']):raise ValueError('PINNED_IMAGE_NATIVE_VERSION')
    checks=native['console_help']
    if not isinstance(checks,dict) or set(checks)!=(set() if is_cpu else set(worker.CONSOLES)):raise ValueError('PINNED_IMAGE_NATIVE_CONSOLES')
    for row in checks.values():
        if (not isinstance(row,dict) or set(row)!={'exit_code','stdout_sha256','stderr_sha256','usage_seen'}
                or type(row['exit_code']) is not int or row['exit_code']!=0 or row['usage_seen'] is not True
                or any(not re.fullmatch('[0-9a-f]{64}',str(row[k])) for k in ('stdout_sha256','stderr_sha256'))):raise ValueError('PINNED_IMAGE_NATIVE_CONSOLES')
    return value


def consumer_spec(result,binding):
    value=validate_result(canonical(result),binding)
    return {'schema':SPEC,'python_executable':worker.TARGET+'/bin/python','image_id':value['image_id'],
        'base_image':binding['base_image'],'builder_sha256':worker_sha256(),
        'selection_sha256':digest(worker.encoded(binding['image_build'])),'native_sha256':value['native_sha256'],
        'expected':value['native']['actual']}


def consumer_proof(accounts,binding,state):
    """Produce the downstream record only from a genuine completed READY asset."""
    from orchestrator import modal_environment_budget as budget
    from orchestrator.modal_environment_provider import observe
    budget.validate_binding(binding);state=Path(state);ident=digest(canonical(binding))
    row=accounts.db.execute('SELECT * FROM autonomy_assets WHERE id=?',(ident,)).fetchone()
    owner=accounts.db.execute('SELECT * FROM autonomy_runs WHERE id=?',(binding['run_id'],)).fetchone()
    is_cpu=binding['purpose']==CPU_PURPOSE
    if is_cpu:
        from orchestrator.modal_diagnostics_image import owner as cpu_owner
        cpu_owner(accounts,binding)
    else:item4_owner(accounts,binding)
    if (not is_build(binding['purpose']) or row is None or row['status']!='READY'
            or row['binding']!=canonical(binding).decode() or not budget.selected_operation(row)
            or owner is None or owner['status']!='ACTIVE'):
        raise ValueError('PINNED_IMAGE_READY_PROVENANCE_REQUIRED')
    handle=strict_json(pr.check(state/'provider/sandbox.json').read_bytes())
    original=observe(None,binding,handle,state/'provider')
    expected={**original,'binding_sha256':ident,'source':binding['source'],'scientific_calls':0,
        'scope':'Pinned image and CPU native checks only; no patient computation or GPU validation'}
    if (original['status']!='VERIFIED' or strict_json(row['receipt'])!=expected
            or strict_json(pr.check(state/'VERIFIED.json').read_bytes())!=expected):
        raise ValueError('PINNED_IMAGE_READY_PROVENANCE_CHANGED')
    return {'schema':'pinned-image-consumer-provenance/v1','binding':binding,
        'asset_receipt_sha256':digest(row['receipt'].encode()),
        'native_receipt_sha256':digest(pr.check(state/'provider/outcome.json').read_bytes()),
        'result':original['pinned_image'],'scientific_environment':consumer_spec(original['pinned_image'],binding),
        'scientific_acceptance':False,'gpu_verified':False}


def runtime_scope(config,binding):
    """Root-preserved selected provenance is required before any paid create."""
    from orchestrator.manual_host_guard import trusted
    from orchestrator import modal_environment_budget as budget
    ref=config.get('pinned_image_provenance')
    if (not isinstance(ref,dict) or set(ref)!={'path','sha256'}
            or not isinstance(ref['sha256'],str) or not re.fullmatch('[0-9a-f]{64}',ref['sha256'])):
        raise ValueError('PINNED_IMAGE_PROVENANCE_REQUIRED')
    raw=trusted(Path(ref['path'])).read_bytes()
    if len(raw)>262144 or digest(raw)!=ref['sha256']:raise ValueError('PINNED_IMAGE_PROVENANCE_CHANGED')
    value=strict_json(raw)
    fields={'schema','binding','asset_receipt_sha256','native_receipt_sha256','result','scientific_environment','scientific_acceptance','gpu_verified'}
    if (not isinstance(value,dict) or set(value)!=fields or value['schema']!='pinned-image-consumer-provenance/v1'
            or value['scientific_acceptance'] is not False or value['gpu_verified'] is not False
            or any(not re.fullmatch('[0-9a-f]{64}',str(value[k])) for k in ('asset_receipt_sha256','native_receipt_sha256'))):
        raise ValueError('PINNED_IMAGE_PROVENANCE_FIELDS')
    budget.validate_binding(value['binding'])
    spec=consumer_spec(value['result'],value['binding'])
    if (value['binding']['purpose']!=PURPOSE or value['scientific_environment']!=spec
            or binding.get('scientific_environment')!=spec or config.get('scientific_environment')!=spec
            or binding.get('image_id')!=spec['image_id'] or config.get('image_id')!=spec['image_id']
            or any(k in binding or k in config for k in ('wheel_volume_id','wheel_files'))):
        raise ValueError('PINNED_IMAGE_RUNTIME_BINDING')
    return spec
