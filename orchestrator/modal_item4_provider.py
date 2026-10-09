"""Item4 fit adapter using the existing authenticated Modal provider.

Preprocessing is separately admitted. A fit sees only its reviewed, hash-bound
preprocessed inputs, package and wheels, plus its private progress Volume v2.
This module never creates assets, uploads source scans or chooses patients.
"""
import hashlib
import json
import re
from pathlib import Path
from datetime import datetime, timezone
from orchestrator import private_records
from orchestrator.modal_executor import canonical
from orchestrator.modal_fit_provider import progress_scope, progress_volume
from orchestrator.modal_item4_budget import AUTHORITY, TEAM_AUTHORITY, quote
from orchestrator.modal_development_inputs import COHORT, SOURCE


def image_environment(binding):
    return binding.get('scientific_environment',{}).get('schema')=='modal-pinned-image/v1'


def _hash(value):
    return isinstance(value, str) and re.fullmatch('[a-f0-9]{64}', value)


def input_files(config, binding):
    """Require a frozen-cohort preprocessing receipt, not a volume's existence.

    The trusted preparation supplies this receipt only after validated
    preprocessing. Here its exact bytes, source identities and complete case
    member set are checked before any remote file is read or fit is created.
    """
    from orchestrator.modal_provider import safe_name
    scope = config['item4_assets']
    raw = private_records.check(scope['preprocessing_receipt']).read_bytes()
    if hashlib.sha256(raw).hexdigest() != scope['preprocessing_sha256']:
        raise ValueError('ITEM4_PREPROCESSING_RECEIPT_CHANGED')
    cohort = private_records.check(scope['cohort_manifest']).read_bytes()
    return validate_inputs(json.loads(raw), cohort, scope, binding)


def validate_inputs(receipt, cohort, scope, binding):
    from orchestrator.modal_preprocessed_contract import validate_preprocessed
    fit=progress_scope(binding)['fit_binding']
    # A fit must retain its exact observed preprocessing plans identity.
    expected={k:fit[k] for k in ('input_contract_sha256','environment_sha256','plans_sha256')}
    return validate_preprocessed(receipt,cohort,scope,expected,cohort_sha256=COHORT,source_sha256=SOURCE)


def scope(provider, config, binding):
    if "preprocessing" in binding:
        raise ValueError("ITEM4_PREPROCESSING_PROVIDER_CONNECTION_REQUIRED")
    if config!=provider.config or hashlib.sha256(canonical(config)).hexdigest()!=binding['runtime_sha256']:
        raise ValueError('MODAL_PROVIDER_RUNTIME')
    selected = binding.get('experiment',{})
    if (binding.get('purpose')!='M4_ITEM4' or selected.get('backlog_item')!=4 or
            selected.get('authority_sha256')!=AUTHORITY or selected.get('team_authority_sha256')!=TEAM_AUTHORITY):
        raise ValueError('ITEM4_PROVIDER_AUTHORITY')
    assets = config.get('item4_assets')
    required_assets={'app_name','app_id','progress','preprocessed_volume_id',
            'preprocessing_receipt','preprocessing_sha256','preprocessing_code_sha256','cohort_manifest',
            'plans_name','split_sha256'}
    if not isinstance(assets,dict) or set(assets) not in (required_assets,required_assets|{'preprocessing_job_sha256'}):
        raise ValueError('ITEM4_PROVIDER_ASSET_FIELDS')
    if (assets['app_id']!=selected.get('billing_object_id') or
            not isinstance(assets['app_id'],str) or not re.fullmatch('ap-[a-zA-Z0-9]+',assets['app_id']) or
            assets['progress']!=binding.get('progress') or
            binding.get('preprocessed_volume_id')!=assets['preprocessed_volume_id'] or
            binding.get('preprocessing_sha256')!=assets['preprocessing_sha256']):
        raise ValueError('ITEM4_PROVIDER_ASSET_BINDING')
    job=assets.get('preprocessing_job_sha256')
    if ('preprocessing_job_sha256' in assets or 'preprocessing_job_sha256' in binding) and (
            not _hash(job) or binding.get('preprocessing_job_sha256')!=job):
        raise ValueError('ITEM4_PREPROCESSING_JOB_BINDING')
    from orchestrator.modal_cleanup import expired
    if expired(config):raise ValueError('MODAL_ASSET_RETENTION_EXPIRED')
    if image_environment(binding):
        from orchestrator.modal_pinned_image import runtime_scope
        runtime_scope(config,binding)
    for key in (('image_id','package_volume_id') if image_environment(binding) else ('image_id','package_volume_id','wheel_volume_id')):
        if config[key]!=binding.get(key):raise ValueError('MODAL_PROVIDER_ASSET_BINDING')
    return assets



def environment_scope(provider,binding,*,required=False):
    from orchestrator.modal_scientific_environment import environment_validate,environment_bytes
    spec=binding.get('scientific_environment')
    if spec is None:
        if required and binding.get('execution',{}).get('schema')=='reviewed-module/v1':
            raise ValueError('ITEM4_SCIENTIFIC_ENVIRONMENT_REQUIRED')
        return None
    environment_validate(spec)
    if (spec!=provider.config.get('scientific_environment')
            or (not image_environment(binding) and spec['wheels']!=provider.config['wheel_files'])
            or hashlib.sha256(environment_bytes(spec['expected'])).hexdigest()!=binding['progress']['fit_binding']['environment_sha256']
            or not {'nnunetv2','torch'}<=set(spec['expected']['packages'])
            or spec['expected']['packages']['nnunetv2']!='2.8.1'
            or spec['expected']['cuda'] is None):
        raise ValueError('ITEM4_SCIENTIFIC_ENVIRONMENT_BINDING')
    if image_environment(binding):
        from orchestrator.modal_pinned_image import runtime_scope
        runtime_scope(provider.config,binding)
    return spec


def existing_app(provider, assets):
    app=provider.modal.App.lookup(assets['app_name'],create_if_missing=False,client=provider.client)
    if app.app_id!=assets['app_id']:
        raise ValueError('ITEM4_BILLING_APP_CHANGED')
    return app


def preprocessed_path(assets):
    job=assets.get('preprocessing_job_sha256')
    if job is None:return None
    if not _hash(job):raise ValueError('ITEM4_PREPROCESSING_JOB_BINDING')
    return '/preprocessing/'+job+'/artifacts'


def verify_volume_members(provider,volume_id,files,*,prefix=None):
    """Check the exact caller-bound data directory without streaming payloads.

    Callers derive prefix from validated immutable identities; this helper does
    not select an arbitrary directory or weaken the worker's full hash check.
    """
    if prefix is None:return provider._verify_volume_members(volume_id,files)
    volume=provider._volume(volume_id)
    rows=volume.listdir(prefix,recursive=True);start=prefix.lstrip('/')+'/'
    names=[row.path.lstrip('/') for row in rows if row.type.name=='FILE']
    if (len(names)!=len(set(names)) or any(row.type.name not in {'FILE','DIRECTORY'} for row in rows)
            or any(not name.startswith(start) for name in names)
            or {row.path.lstrip('/')[len(start):]:row.size for row in rows if row.type.name=='FILE'}!={k:v['bytes'] for k,v in files.items()}):
        raise ValueError('MODAL_VOLUME_MEMBER_SET')
    return volume


def verify_input_members(provider,assets,files):
    return verify_volume_members(provider,assets['preprocessed_volume_id'],files,
                                 prefix=preprocessed_path(assets))


def volume_mount(provider,volume_id,*,prefix=None):
    options={'read_only':True}
    if prefix is not None:options['sub_path']=prefix
    return provider._volume(volume_id).with_mount_options(**options)


def input_mount(provider,assets):
    return volume_mount(provider,assets['preprocessed_volume_id'],prefix=preprocessed_path(assets))


def preflight(provider, config, binding, prepared):
    if 'preprocessing' in binding:
        from orchestrator.modal_preprocessing_provider import preflight as preprocess
        return preprocess(provider,config,binding,prepared)
    from orchestrator.modal_provider import member_map
    from orchestrator.manual_executor import inventory
    assets=scope(provider,config,binding)
    environment_scope(provider,binding,required=True)
    files=input_files(config,binding)
    provider.client.hello()
    app=existing_app(provider,assets)
    progress=progress_volume(provider,progress_scope(binding))
    ids=[progress.object_id,assets['preprocessed_volume_id'],config['package_volume_id']]+([] if image_environment(binding) else [config['wheel_volume_id']])
    if len(set(ids))!=len(ids):raise ValueError('ITEM4_VOLUME_ROLES_OVERLAP')
    package=member_map({name:{'sha256':sha,'bytes':(Path(prepared)/name).stat().st_size}
                       for name,sha in inventory(prepared).items()})
    if binding.get('execution',{}).get('schema')=='reviewed-module/v1':package.pop('manifest.json')
    verify_input_members(provider,assets,files)
    provider._verify_volume(config['package_volume_id'],package)
    if not image_environment(binding):provider._verify_volume(config['wheel_volume_id'],member_map(config['wheel_files']))
    prepared_guard=guard_payload(provider,binding) # Bound transport must fit before spending.
    image=provider.modal.Image.from_id(config['image_id'],client=provider.client);image.build(app)
    if image.object_id!=config['image_id']:raise ValueError('MODAL_IMAGE_ID_CHANGED')
    # Hash large inputs inside the actual worker before code execution; only
    # inventory metadata crosses the controller. Package/wheels remain hashed.
    # Observe billing AFTER those checks, so admission's
    # 300-second freshness check is against the end of this preflight.
    billing=provider.billing_snapshot()
    if binding['cost']!=quote(binding['resources'],billing['rates'],binding['overhead_micro_usd']):
        raise ValueError('ITEM4_ACTUAL_RATE_QUOTE_CHANGED')
    return {'status':'READY','billing_snapshot':billing,'app_id':app.app_id,
            'progress_volume_id':progress.object_id,'progress_volume_version':2,
            'input_inventory_sha256':hashlib.sha256(canonical(files)).hexdigest(),
            'preprocessing_sha256':assets['preprocessing_sha256'],
            'input_guard_sha256':prepared_guard['guard_sha256'],
            'input_guard_payload_sha256':hashlib.sha256(canonical(prepared_guard)).hexdigest(),
            'checked_at':datetime.now(timezone.utc).isoformat()}


def create(provider,config,binding,package):
    if 'preprocessing' in binding:
        from orchestrator.modal_preprocessing_provider import create as preprocess
        return preprocess(provider,config,binding,package)
    assets=scope(provider,config,binding);environment_scope(provider,binding,required=True)
    # The ordinary executor has durably reserved spending and create intent.
    # Re-resolve identities; no new asset or from-name create fallback here.
    app=existing_app(provider,assets);progress=progress_volume(provider,progress_scope(binding))
    resources=binding['resources']
    mounts={'/preprocessed':input_mount(provider,assets),
            '/reviewed':provider._volume(config['package_volume_id']).with_mount_options(read_only=True),
            '/progress':progress}
    ids=[assets['preprocessed_volume_id'],config['package_volume_id'],progress.object_id]
    if not image_environment(binding):
        mounts['/wheels']=provider._volume(config['wheel_volume_id']).with_mount_options(read_only=True)
        ids.append(config['wheel_volume_id'])
    if len(set(ids))!=len(ids):
        raise ValueError('ITEM4_VOLUME_ROLES_OVERLAP')
    sb=provider.modal.Sandbox.create('/bin/sleep',str(resources['timeout_seconds']),
        app=app,name='research-'+hashlib.sha256(canonical(binding)).hexdigest()[:32],
        image=provider.modal.Image.from_id(config['image_id'],client=provider.client),
        gpu=resources['gpu'],cpu=(resources['cpu'],resources['cpu']),
        memory=(resources['memory_mib'],resources['memory_mib']),timeout=resources['timeout_seconds'],
        block_network=True,include_oidc_identity_token=False,secrets=[],
        encrypted_ports=[],h2_ports=[],unencrypted_ports=[],volumes=mounts,client=provider.client)
    return {'provider_id':sb.object_id,'entrypoint':'idle-only',
            'binding_sha256':hashlib.sha256(canonical(binding)).hexdigest()}


def guard_program():
    """Exact stdlib sources, sent together; no import through a mount alias."""
    from orchestrator import modal_input_guard, modal_volume_path, modal_scientific_environment
    return Path(modal_volume_path.__file__).read_text()+'\n'+Path(modal_scientific_environment.__file__).read_text()+'\n'+Path(modal_input_guard.__file__).read_text()


def guard_payload(provider, binding):
    assets=scope(provider,provider.config,binding)
    source=guard_program().encode()
    payload={"binding_sha256":hashlib.sha256(canonical(binding)).hexdigest(),
            "guard_sha256":hashlib.sha256(source).hexdigest(),
            "preprocessing_sha256":assets["preprocessing_sha256"],
            "files":input_files(provider.config,binding),
            "volume_ids":{"inputs":assets['preprocessed_volume_id'],
                          "progress":binding['progress']['volume_id'],
                          "package":provider.config['package_volume_id']}}
    if binding.get('execution',{}).get('schema')=='reviewed-module/v1':
        from orchestrator.experiment_modal_package import manifest_for
        payload['execution_manifest']=manifest_for(binding)
        if environment_scope(provider,binding) is not None and not image_environment(binding):
            payload['volume_ids']['wheels']=provider.config['wheel_volume_id']
    # Linux limits a single exec argument. Refuse a transport mismatch during
    # read-only preflight, not after reserving or creating a paid sandbox.
    if len(canonical(payload))>100000 or len(source)>100000:
        raise ValueError('ITEM4_INPUT_GUARD_TRANSPORT_LIMIT')
    return payload


def launch(provider, provider_id, binding):
    if 'preprocessing' in binding:
        from orchestrator.modal_preprocessing_provider import launch as preprocess
        return preprocess(provider,provider_id,binding)
    from orchestrator import modal_input_guard
    environment=environment_scope(provider,binding,required=True)
    payload=guard_payload(provider,binding)
    source=guard_program()
    sandbox=provider._sandbox(provider_id)
    if sandbox.object_id!=provider_id:raise ValueError("MODAL_FIT_SANDBOX_ID_CHANGED")
    # One exec, same durable executor intent, same timeout and confinement.
    # The stdlib guard does not load the reviewed program until hashes pass.
    interpreter=environment['python_executable'] if environment else '/usr/bin/python3'
    sandbox.exec(interpreter,'-B','-s','-c',source,canonical(payload).decode(),
        timeout=binding['resources']['timeout_seconds'],workdir='/tmp',
        stdout=provider.modal.stream_type.StreamType.DEVNULL,
        stderr=provider.modal.stream_type.StreamType.DEVNULL)
    return {'provider_id':provider_id,'submitted':True,'binding_sha256':payload['binding_sha256'],
            'input_guard_sha256':payload['guard_sha256'],
            'input_inventory_sha256':hashlib.sha256(canonical(payload['files'])).hexdigest()}


def input_proof(provider, binding, volume):
    from orchestrator.modal_fit_provider import _file, MAX_RECORD
    payload=guard_payload(provider,binding)
    path='/input-verification/'+payload['binding_sha256']+'.json'
    roots=[row for row in volume.listdir('/',recursive=False) if row.path.strip('/')=='input-verification']
    if not roots:return None
    if len(roots)!=1 or roots[0].type.name!='DIRECTORY':raise ValueError('ITEM4_INPUT_VERIFICATION_BINDING')
    rows=volume.listdir('/input-verification',recursive=False)
    if not any(row.path.lstrip('/')==path.lstrip('/') for row in rows):return None
    proof=json.loads(_file(volume,path,MAX_RECORD,collect=True)['data'])
    expected={'schema':'modal-input-verification/v1',**{k:payload[k] for k in
        ('binding_sha256','guard_sha256','preprocessing_sha256')},
        'inventory_sha256':hashlib.sha256(canonical(payload['files'])).hexdigest(),
        'file_count':len(payload['files']),'total_bytes':sum(x['bytes'] for x in payload['files'].values()),
        'volume_ids':payload['volume_ids']}
    if environment_scope(provider,binding) is not None:
        expected['scientific_environment_sha256']=hashlib.sha256(canonical(binding['scientific_environment'])).hexdigest()
    if (not isinstance(proof,dict) or set(proof)!=set(expected)|{'status','reason'}
            or any(proof.get(k)!=v for k,v in expected.items())
            or proof.get('status') not in {'VERIFIED','FAILED'}
            or (proof['status']=='VERIFIED' and proof['reason'] is not None)
            or (proof['status']=='FAILED' and proof['reason'] not in {
                'INPUT_GUARD_ROOT','INPUT_GUARD_ALIAS_OR_TYPE','INPUT_GUARD_MEMBER_OR_SIZE',
                'INPUT_GUARD_HASH','INPUT_GUARD_IO','SCIENTIFIC_ENVIRONMENT_FAILED'})):
        raise ValueError('ITEM4_INPUT_VERIFICATION_BINDING')
    if 'scientific_environment_sha256' in expected and proof['status']=='VERIFIED':
        from orchestrator.modal_scientific_environment import environment_proof
        raw=_file(volume,'/environment-verification/'+payload['binding_sha256']+'/environment.json',MAX_RECORD,collect=True)['data']
        proof={**proof,'environment':environment_proof(raw,binding)}
    return proof
