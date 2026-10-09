"""CPU preprocessing on the ordinary item4 executor and cost ledger.

Source selection is derived only from the existing frozen development readers.
No scientific method, asset creation, allowance, retry or credential lives here.
Only small original receipts return; output data remain on the private Volume.
"""
import hashlib
import math
import re
from pathlib import Path
from datetime import datetime,timezone
from orchestrator import private_records as pr
from orchestrator.modal_executor import canonical,verify_package
from orchestrator.modal_item4_budget import AUTHORITY,TEAM_AUTHORITY,quote
from orchestrator.modal_fit_provider import progress_volume,_file,MAX_RECORD
from orchestrator.review_contract import strict_json
from orchestrator.modal_scientific_environment import environment_validate,environment_bytes,environment_proof
from orchestrator.modal_preprocessed_contract import validate_preprocessed,validate_validation
from orchestrator import modal_development_inputs as source

def image_environment(binding):
    return binding.get('scientific_environment',{}).get('schema')=='modal-pinned-image/v1'


def sha(raw):return hashlib.sha256(raw).hexdigest()
def original(path):return pr.check(path).read_bytes()


def input_files(config,binding):
    records=config['item4_preprocessing_assets']['source_records']
    base={'cohort','source','authority'};ctp={'ctp_metadata','ctp_archive','ctp_authority'}
    auxiliary={'auxiliary'}
    if not isinstance(records,dict) or set(records) not in (base,base|ctp,base|auxiliary,base|ctp|auxiliary):
        raise ValueError('PREPROCESSING_SOURCE_RECORDS')
    contract=source.frozen_inventory(original(records['cohort']),original(records['source']),original(records['authority']))
    files=dict(contract['files'])
    if ctp <= set(records):
        from orchestrator.modal_ctp_download import frozen_plan
        plan=frozen_plan(original(records['cohort']),original(records['ctp_metadata']),
            original(records['ctp_archive']),original(records['ctp_authority']))
        files.update({name:{k:row[k] for k in ('sha256','bytes')} for name,row in plan['files'].items()})
    if 'auxiliary' in records:
        extra=source.frozen_auxiliary(original(records['cohort']),original(records['auxiliary']))
        if set(extra) & set(files):raise ValueError('PREPROCESSING_SOURCE_OVERLAP')
        files.update(extra)
    if sha(canonical(files))!=binding['preprocessing']['input_contract_sha256']:
        raise ValueError('PREPROCESSING_SOURCE_INVENTORY_CHANGED')
    return files


def scope(provider,config,binding):
    if config!=provider.config or sha(canonical(config))!=binding.get('runtime_sha256'):
        raise ValueError('MODAL_PROVIDER_RUNTIME')
    e=binding.get('experiment',{})
    if (binding.get('purpose')!='M4_ITEM4' or e.get('backlog_item')!=4
            or e.get('authority_sha256')!=AUTHORITY or e.get('team_authority_sha256')!=TEAM_AUTHORITY
            or e.get('stage')!='SMOKE' or type(e.get('segment')) is not int or e['segment']<1
            or e['segment']==1 and 'resume' in binding
            or binding.get('resources',{}).get('gpu') is not None):
        raise ValueError('PREPROCESSING_ADMISSION_SCOPE')
    from orchestrator.preprocessing_checkpoints import resume
    resume(binding)
    a=config.get('item4_preprocessing_assets')
    fields={'app_name','app_id','source_volume_id','output_volume_id','output_volume_name','source_records'}
    if not isinstance(a,dict) or set(a) not in (fields,fields|{'source_view_sha256'}):
        raise ValueError('PREPROCESSING_ASSET_FIELDS')
    if (a['app_id']!=e.get('billing_object_id')
            or not isinstance(a['app_id'],str) or not re.fullmatch('ap-[A-Za-z0-9]+',a['app_id'])
            or not isinstance(a['output_volume_name'],str) or not re.fullmatch('[A-Za-z0-9][A-Za-z0-9_-]{0,95}',a['output_volume_name'])
            or a['source_volume_id']!=binding.get('source_volume_id')
            or a['output_volume_id']!=binding.get('preprocessing_output_volume_id')):
        raise ValueError('PREPROCESSING_ASSET_BINDING')
    view=a.get('source_view_sha256')
    if ('source_view_sha256' in a or 'source_view_sha256' in binding) and (
            not isinstance(view,str) or not re.fullmatch('[a-f0-9]{64}',view)
            or binding.get('source_view_sha256')!=view
            or binding['preprocessing']['input_contract_sha256']!=view):
        raise ValueError('PREPROCESSING_SOURCE_VIEW_BINDING')
    if image_environment(binding):
        from orchestrator.modal_pinned_image import runtime_scope
        runtime_scope(config,binding)
    for key in (('image_id','package_volume_id') if image_environment(binding) else ('image_id','package_volume_id','wheel_volume_id')):
        if config.get(key)!=binding.get(key):raise ValueError('MODAL_PROVIDER_ASSET_BINDING')
    roles=[a['source_volume_id'],a['output_volume_id'],config['package_volume_id']]+([] if image_environment(binding) else [config['wheel_volume_id']])
    if (any(not isinstance(x,str) or not re.fullmatch('vo-[A-Za-z0-9]+',x) for x in roles)
            or len(set(roles))!=len(roles)):raise ValueError('ITEM4_VOLUME_ROLES_OVERLAP')
    from orchestrator.modal_cleanup import expired
    if expired(config):raise ValueError('MODAL_ASSET_RETENTION_EXPIRED')
    if e.get('fit_id')!='preprocess-'+binding['preprocessing']['id']:
        raise ValueError('PREPROCESSING_JOB_IDENTITY')
    return a


def environment_scope(provider,binding):
    spec=binding.get('scientific_environment');environment_validate(spec)
    if (spec!=provider.config.get('scientific_environment')
            or (not image_environment(binding) and spec['wheels']!=provider.config['wheel_files'])
            or sha(environment_bytes(spec['expected']))!=binding['preprocessing']['environment_sha256']
            or spec['expected']['packages'].get('nnunetv2')!='2.8.1'):
        raise ValueError('PREPROCESSING_ENVIRONMENT_BINDING')
    if image_environment(binding):
        from orchestrator.modal_pinned_image import runtime_scope
        runtime_scope(provider.config,binding)
    return spec


def source_view_path(assets):
    # Optional data-only view of the already verified development files. The
    # complete frozen input inventory supplies its identity, never an arbitrary
    # user path. scope() binds it to both runtime and preprocessing selection.
    view=assets.get('source_view_sha256')
    if view is None:return None
    if not isinstance(view,str) or not re.fullmatch('[a-f0-9]{64}',view):
        raise ValueError('PREPROCESSING_SOURCE_VIEW_BINDING')
    return '/input-views/'+view


def output_volume(provider,a):
    return progress_volume(provider,{'volume_id':a['output_volume_id'],'volume_name':a['output_volume_name']})


def payload(provider,binding):
    from orchestrator.modal_item4_provider import guard_program
    from orchestrator.experiment_modal_package import manifest_for
    a=scope(provider,provider.config,binding);environment_scope(provider,binding)
    result={'binding_sha256':sha(canonical(binding)),'guard_sha256':sha(guard_program().encode()),
        'preprocessing_sha256':binding['preprocessing']['input_contract_sha256'],
        'inventory_ref':{'path':'input-inventory.json','sha256':binding['preprocessing']['input_contract_sha256']},
        'volume_ids':{'inputs':a['source_volume_id'],'progress':a['output_volume_id'],
            'package':provider.config['package_volume_id'],**({} if image_environment(binding) else {'wheels':provider.config['wheel_volume_id']})},
        'execution_manifest':manifest_for(binding)}
    if len(canonical(result))>100000 or len(guard_program().encode())>100000:
        raise ValueError('ITEM4_INPUT_GUARD_TRANSPORT_LIMIT')
    return result


def preflight(provider,config,binding,prepared):
    from orchestrator.modal_item4_provider import existing_app,verify_volume_members
    from orchestrator.manual_executor import inventory
    a=scope(provider,config,binding);environment_scope(provider,binding)
    verify_package(prepared,binding)
    files=input_files(config,binding)
    if (Path(prepared)/'input-inventory.json').read_bytes()!=canonical(files):
        raise ValueError('PREPROCESSING_PACKAGE_SOURCE_CHANGED')
    provider.client.hello();app=existing_app(provider,a);volume=output_volume(provider,a)
    if 'resume' in binding:previous_snapshot(provider,binding,volume)
    verify_volume_members(provider,a['source_volume_id'],files,prefix=source_view_path(a))
    package={name:{'sha256':pin,'bytes':(Path(prepared)/name).stat().st_size}
        for name,pin in inventory(prepared).items() if name!='manifest.json'}
    provider._verify_volume(config['package_volume_id'],package)
    if not image_environment(binding):provider._verify_volume(config['wheel_volume_id'],config['wheel_files'])
    guard=payload(provider,binding)
    image=provider.modal.Image.from_id(config['image_id'],client=provider.client);image.build(app)
    if image.object_id!=config['image_id']:raise ValueError('MODAL_IMAGE_ID_CHANGED')
    billing=provider.billing_snapshot()
    if binding['cost']!=quote(binding['resources'],billing['rates'],binding['overhead_micro_usd']):
        raise ValueError('ITEM4_ACTUAL_RATE_QUOTE_CHANGED')
    return {'status':'READY','billing_snapshot':billing,'app_id':app.app_id,
        'input_inventory_sha256':sha(canonical(files)),'output_volume_id':volume.object_id,
        'input_guard_payload_sha256':sha(canonical(guard)),
        'checked_at':datetime.now(timezone.utc).isoformat(),'patient_payload_egress':False}


def create(provider,config,binding,package):
    from orchestrator.modal_item4_provider import existing_app,volume_mount
    a=scope(provider,config,binding);environment_scope(provider,binding);resources=binding['resources']
    app=existing_app(provider,a);output=output_volume(provider,a)
    # Keep the same four confined roles; only progress/output is writable.
    mounts={'/preprocessed':volume_mount(provider,a['source_volume_id'],prefix=source_view_path(a)),
        '/reviewed':provider._volume(config['package_volume_id']).with_mount_options(read_only=True),
        '/progress':output}
    if not image_environment(binding):mounts['/wheels']=provider._volume(config['wheel_volume_id']).with_mount_options(read_only=True)
    sb=provider.modal.Sandbox.create('/bin/sleep',str(resources['timeout_seconds']),
        app=app,name='research-'+sha(canonical(binding))[:32],
        image=provider.modal.Image.from_id(config['image_id'],client=provider.client),
        gpu=None,cpu=(resources['cpu'],resources['cpu']),memory=(resources['memory_mib'],resources['memory_mib']),
        timeout=resources['timeout_seconds'],block_network=True,include_oidc_identity_token=False,secrets=[],
        encrypted_ports=[],h2_ports=[],unencrypted_ports=[],volumes=mounts,client=provider.client)
    return {'provider_id':sb.object_id,'entrypoint':'idle-only','binding_sha256':sha(canonical(binding))}


def launch(provider,provider_id,binding):
    from orchestrator.modal_item4_provider import guard_program
    environment=environment_scope(provider,binding);guard=payload(provider,binding)
    sandbox=provider._sandbox(provider_id)
    if sandbox.object_id!=provider_id:raise ValueError('MODAL_FIT_SANDBOX_ID_CHANGED')
    sandbox.exec(environment['python_executable'],'-B','-s','-c',guard_program(),canonical(guard).decode(),
        timeout=binding['resources']['timeout_seconds'],workdir='/tmp',
        stdout=provider.modal.stream_type.StreamType.DEVNULL,stderr=provider.modal.stream_type.StreamType.DEVNULL)
    return {'provider_id':provider_id,'submitted':True,'binding_sha256':guard['binding_sha256'],
        'input_guard_sha256':guard['guard_sha256'],'input_inventory_sha256':binding['preprocessing']['input_contract_sha256']}


def record(volume,path):return _file(volume,path,MAX_RECORD,collect=True)['data']
def exists(volume,path):
    # Missing parent means no proof yet, never a terminal outcome. Confirm each
    # parent from its existing parent; do not swallow transport/identity errors.
    parts=path.split('/')
    if not path.startswith('/') or any(p in {'','.','..'} for p in parts[1:]):
        raise ValueError('PREPROCESSING_OBSERVATION_PATH')
    parent='/'
    for name in parts[1:-1]:
        target=parent.rstrip('/')+'/'+name
        matches=[row for row in volume.listdir(parent,recursive=False)
                 if row.path.lstrip('/')==target.lstrip('/')]
        if not matches:return False
        if len(matches)!=1 or matches[0].type.name!='DIRECTORY':
            raise ValueError('PREPROCESSING_OBSERVATION_PARENT')
        parent=target
    return any(row.path.lstrip('/')==path.lstrip('/') for row in volume.listdir(parent,recursive=False))


def input_proof(provider,binding,volume):
    guard=payload(provider,binding)
    path='/input-verification/'+guard['binding_sha256']+'.json'
    if not exists(volume,path):return None
    raw=record(volume,path)
    check_input_proof(provider,binding,raw)
    return raw


def check_input_proof(provider,binding,raw):
    guard=payload(provider,binding);files=input_files(provider.config,binding)
    proof=strict_json(raw)
    expected={'schema':'modal-input-verification/v1',**{k:guard[k] for k in
        ('binding_sha256','guard_sha256','preprocessing_sha256')},
        'inventory_sha256':sha(canonical(files)),'file_count':len(files),'total_bytes':sum(x['bytes'] for x in files.values()),
        'volume_ids':guard['volume_ids'],'scientific_environment_sha256':sha(canonical(binding['scientific_environment']))}
    if (not isinstance(proof,dict) or set(proof)!=set(expected)|{'status','reason'}
            or any(proof.get(k)!=v for k,v in expected.items())
            or proof['status'] not in {'VERIFIED','FAILED'}
            or proof['status']=='VERIFIED' and proof['reason'] is not None
            or proof['status']=='FAILED' and proof['reason'] not in {
                'INPUT_GUARD_ROOT','INPUT_GUARD_ALIAS_OR_TYPE','INPUT_GUARD_MEMBER_OR_SIZE',
                'INPUT_GUARD_HASH','INPUT_GUARD_IO','SCIENTIFIC_ENVIRONMENT_FAILED'}):
        raise ValueError('ITEM4_INPUT_VERIFICATION_BINDING')
    return raw


def observe(provider,provider_id,binding):
    a=scope(provider,provider.config,binding);sandbox=provider._sandbox(provider_id)
    if sandbox.object_id!=provider_id:raise ValueError('MODAL_FIT_SANDBOX_ID_CHANGED')
    volume=output_volume(provider,a);ident=sha(canonical(binding));root='/preprocessing/'+ident
    proof=input_proof(provider,binding,volume)
    if proof is not None and strict_json(proof)['status']=='FAILED':return 'FAILED',sandbox,volume,{}
    if exists(volume,root+'/failed.json'):
        failure=strict_json(record(volume,root+'/failed.json'))
        if (not isinstance(failure,dict) or set(failure)!={'status','binding_sha256','error_type','completed_steps','elapsed_seconds','may_retry'}
                or failure['status']!='FAILED' or failure['binding_sha256']!=ident or failure['may_retry'] is not False
                or not isinstance(failure['error_type'],str) or not failure['error_type'].isidentifier()
                or type(failure['completed_steps']) is not int or failure['completed_steps']<0
                or type(failure['elapsed_seconds']) not in (int,float)
                or not math.isfinite(failure['elapsed_seconds']) or failure['elapsed_seconds']<0):
            raise ValueError('PREPROCESSING_FAILURE_BINDING')
        return 'FAILED',sandbox,volume,{}
    if not exists(volume,root+'/result.json'):return None,sandbox,volume,{}
    if proof is None or strict_json(proof)['status']!='VERIFIED':raise ValueError('ITEM4_INPUT_VERIFICATION_REQUIRED')
    raw={name:record(volume,root+'/'+name) for name in ('result.json','preprocessing.json','validation.json')}
    raw['input-verification.json']=proof
    raw['environment.json']=record(volume,'/environment-verification/'+ident+'/environment.json')
    files=validate_records(provider,binding,raw)
    # Metadata only: no processed images, labels or properties leave the Volume.
    entries=volume.listdir(root+'/artifacts',recursive=True)
    prefix=(root+'/artifacts/').lstrip('/')
    names=[x.path.lstrip('/') for x in entries if x.type.name=='FILE']
    if (len(names)!=len(set(names)) or any(x.type.name not in {'FILE','DIRECTORY'} for x in entries)
            or {x.path.lstrip('/')[len(prefix):]:x.size for x in entries if x.type.name=='FILE'}!={k:v['bytes'] for k,v in files.items()}
            or any(not name.startswith(prefix) for name in names)):
        raise ValueError('PREPROCESSING_OUTPUT_INVENTORY_CHANGED')
    return 'COMPLETE',sandbox,volume,raw


def validate_records(provider,binding,raw):
    a=scope(provider,provider.config,binding);ident=sha(canonical(binding))
    if set(raw)!={'result.json','preprocessing.json','validation.json','environment.json','input-verification.json'}:
        raise ValueError('PREPROCESSING_COLLECTION_MEMBERS')
    check_input_proof(provider,binding,raw['input-verification.json'])
    if strict_json(raw['input-verification.json'])['status']!='VERIFIED':
        raise ValueError('ITEM4_INPUT_VERIFICATION_REQUIRED')
    observed=environment_proof(raw['environment.json'],binding)
    result=strict_json(raw['result.json']);selected=binding['preprocessing']
    proposed=strict_json(raw['preprocessing.json']);validation=strict_json(raw['validation.json'])
    assets={**selected,'preprocessing_code_sha256':binding['execution']['module_sha256']}
    files=validate_preprocessed(proposed,original(a['source_records']['cohort']),assets,
        {k:selected[k] for k in ('input_contract_sha256','environment_sha256')},cohort_sha256=source.COHORT,source_sha256=source.SOURCE)
    validate_validation(validation,{'run_id':binding['run_id'],'spec_sha256':binding['spec_sha256'],
        'preprocessing_code_sha256':binding['execution']['module_sha256'],'validator_sha256':binding['execution']['module_sha256'],
        **{k:selected[k] for k in ('cohort_sha256','input_contract_sha256','environment_sha256')}},files)
    expected={'schema':'experiment-preprocessing-result/v1','status':'VALIDATED','binding_sha256':ident,
        'preprocessing_sha256':sha(raw['preprocessing.json']),'validation_sha256':sha(raw['validation.json']),
        'files':len(files),'bytes':sum(x['bytes'] for x in files.values()),'scientifically_accepted':False,'fit_completed':False}
    if (not isinstance(result,dict) or set(result)!=set(expected)|{'steps','elapsed_seconds'}
            or any(result.get(k)!=v for k,v in expected.items())
            or type(result['steps']) is not int or not 1<=result['steps']<=len(files)
            or type(result['elapsed_seconds']) not in (int,float) or not math.isfinite(result['elapsed_seconds']) or result['elapsed_seconds']<0
            or sha(environment_bytes(observed['actual']))!=selected['environment_sha256']):
        raise ValueError('PREPROCESSING_RESULT_BINDING')
    return files


def validate_collection(config,binding,destination):
    # Saved metadata replay requires no SDK or model and admits no scientific result.
    from types import SimpleNamespace
    from orchestrator.manual_executor import inventory
    provider=SimpleNamespace(config=config)
    destination=Path(destination);pr.check_tree(destination)
    members=inventory(destination)
    expected={'result.json','preprocessing.json','validation.json','environment.json','input-verification.json'}
    if set(members)!=expected:raise ValueError('PREPROCESSING_COLLECTION_MEMBERS')
    if any(pr.check(destination/name).stat().st_size>MAX_RECORD for name in members):
        raise ValueError('PREPROCESSING_COLLECTION_SIZE')
    raw={name:pr.check(destination/name).read_bytes() for name in members}
    files=validate_records(provider,binding,raw)
    return {'status':'VALID','binding_sha256':sha(canonical(binding)),'files':len(files),
        'file_sha256':members,'scientifically_accepted':False,'fit_completed':False}


def status(provider,provider_id,binding):
    state,sandbox,_,_=observe(provider,provider_id,binding)
    return {'provider_id':provider_id,'binding_sha256':sha(canonical(binding)),
        'status':state or ('RUNNING' if sandbox.poll() is None else 'UNKNOWN')}


@pr.private_umask
def collect(provider,provider_id,binding,destination):
    state,_,_,raw=observe(provider,provider_id,binding)
    if state!='COMPLETE':raise ValueError('MODAL_RESULT_NOT_COMPLETE')
    for name,data in raw.items():
        with pr.open_file(Path(destination)/name,'xb') as f:f.write(data)
    if observe(provider,provider_id,binding)[3]!=raw:raise ValueError('MODAL_RESULT_CHANGED_DURING_COLLECTION')
    return {'provider_id':provider_id,'binding_sha256':sha(canonical(binding)),
        'file_sha256':{name:sha(data) for name,data in raw.items()},'patient_payload_egress':False,
        'preprocessed_sub_path':'preprocessing/'+sha(canonical(binding))+'/artifacts',
        'preprocessing_volume_id':binding['preprocessing_output_volume_id']}


def remote_snapshot(volume,ident):
    from orchestrator.preprocessing_checkpoints import snapshot
    root='/preprocessing/'+ident
    # A returned validation or code failure is not interrupted preprocessing.
    if any(exists(volume,root+'/'+name) for name in ('failed.json','result.json','author-validation.json')):
        raise ValueError('PREPROCESSING_PREDECESSOR_NOT_INTERRUPTED')
    raw=record(volume,root+'/binding.json')
    if sha(raw)!=ident:raise ValueError('PREPROCESSING_PREDECESSOR_CHANGED')
    started=strict_json(record(volume,root+'/started.json'))
    if (not isinstance(started,dict) or set(started)!={'binding_sha256','at'}
            or started['binding_sha256']!=ident or type(started['at']) not in (int,float)
            or not math.isfinite(started['at']) or started['at']<=0):
        raise ValueError('PREPROCESSING_START_BINDING')
    records={};prefix=(root+'/steps/').lstrip('/')
    for entry in volume.listdir(root+'/steps',recursive=False):
        name=entry.path.lstrip('/')
        if entry.type.name!='FILE' or not name.startswith(prefix) or '/' in name[len(prefix):] or not name.endswith('.json'):
            raise ValueError('PREPROCESSING_STEP_MEMBERS')
        key=name[len(prefix):-5]
        if key in records:raise ValueError('PREPROCESSING_STEP_MEMBERS')
        records[key]=record(volume,'/'+name)
    snap=snapshot(ident,records)
    expected={name:item['bytes'] for step in snap['steps'].values() for name,item in step['files'].items()}
    entries=volume.listdir(root+'/artifacts',recursive=True);prefix=(root+'/artifacts/').lstrip('/')
    observed={}
    for entry in entries:
        name=entry.path.lstrip('/')
        if not name.startswith(prefix) or entry.type.name not in {'FILE','DIRECTORY'}:
            raise ValueError('PREPROCESSING_STEP_MEMBERS')
        if entry.type.name=='FILE':
            key=name[len(prefix):]
            if key in observed:raise ValueError('PREPROCESSING_STEP_MEMBERS')
            observed[key]=entry.size
    if any(observed.get(name)!=size for name,size in expected.items()):
        raise ValueError('PREPROCESSING_COMMITTED_BYTES_CHANGED')
    return strict_json(raw),snap


def previous_snapshot(provider,binding,volume):
    from orchestrator.preprocessing_checkpoints import resume,same_execution
    link=resume(binding)
    if link is None:raise ValueError('PREPROCESSING_RESUME_BINDING')
    previous,snap=remote_snapshot(volume,link['previous_segment_id'])
    same_execution(previous,binding)
    if sha(canonical(snap))!=link['steps_record_sha256']:raise ValueError('PREPROCESSING_STEPS_CHANGED')
    return snap


def terminal_steps(provider,provider_id,binding):
    a=scope(provider,provider.config,binding);sandbox=provider._sandbox(provider_id)
    if sandbox.object_id!=provider_id:raise ValueError('MODAL_FIT_SANDBOX_ID_CHANGED')
    code=sandbox.poll()
    if type(code) is not int or code==0:raise ValueError('PREPROCESSING_NOT_PROVEN_INTERRUPTED')
    volume=output_volume(provider,a);ident=sha(canonical(binding))
    proof=input_proof(provider,binding,volume)
    if proof is None or strict_json(proof)['status']!='VERIFIED':raise ValueError('ITEM4_INPUT_VERIFICATION_REQUIRED')
    environment_proof(record(volume,'/environment-verification/'+ident+'/environment.json'),binding)
    old,snap=remote_snapshot(volume,ident)
    if old!=binding:raise ValueError('PREPROCESSING_PREDECESSOR_CHANGED')
    if sandbox.poll()!=code or remote_snapshot(volume,ident)!=(old,snap):
        raise ValueError('PREPROCESSING_TERMINAL_OBSERVATION_CHANGED')
    return {'schema':'preprocessing-terminal-proof/v1','provider_id':provider_id,'binding_sha256':ident,
        'terminal_exit_code':code,'volume_id':volume.object_id,'snapshot':snap,
        'steps_record_sha256':sha(canonical(snap)),'observed_at':datetime.now(timezone.utc).isoformat(),
        'may_launch':False}
