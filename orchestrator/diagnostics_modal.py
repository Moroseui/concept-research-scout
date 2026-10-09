"""Fixed item6 CPU worker and provider connection; no data passes through host."""
from pathlib import Path
import json
import re
from orchestrator.diagnostics_contract import require,sha,encoded,program_contract,input_contract,PURPOSE
from orchestrator.manual_executor import inventory
from orchestrator.modal_item4_provider import verify_volume_members,volume_mount
from orchestrator.modal_item4_policy import quote


def scope(provider,config,binding):
    require(config==provider.config and sha(encoded(config))==binding['runtime_sha256'],'DIAGNOSTICS_RUNTIME_BINDING')
    require(binding['purpose']==PURPOSE and binding['resources']['gpu'] is None,'DIAGNOSTICS_CPU_ONLY')
    a=config['diagnostics_assets']
    extras={'pinned_image_provenance'} if 'interpreter' in a.get('environment',{}) else set()
    require(set(a)==extras|{'app_name','app_id','image_id','environment','data_volume_id','data_subpath','input_contract','cohort','source_capture','package_volume_id'},'DIAGNOSTICS_ASSET_FIELDS')
    for key,prefix in [('app_id','ap-'),('image_id','im-'),('data_volume_id','vo-'),('package_volume_id','vo-')]:
        require(isinstance(a[key],str) and re.fullmatch(prefix+'[A-Za-z0-9]+',a[key]),'DIAGNOSTICS_ASSET_ID')
    require(a['data_volume_id']!=a['package_volume_id'],'DIAGNOSTICS_VOLUME_ROLE_ALIAS')
    prefix=a['data_subpath']
    require(isinstance(prefix,str) and re.fullmatch('/[A-Za-z0-9_-]+(?:/[A-Za-z0-9_-]+)*',prefix) and len(prefix)>1,'DIAGNOSTICS_DATA_SUBPATH')
    expected={'schema':'diagnostics-environment/v1','image_id':a['image_id'],'requirements':binding['program_contract']['requirements']}
    from orchestrator.modal_diagnostics_image import runtime_environment
    expected=runtime_environment(expected,a)
    require(a['environment']==expected and sha(encoded(expected))==binding['environment_sha256'],'DIAGNOSTICS_ENVIRONMENT_SELECTION')
    require(a['input_contract']==binding['input_contract'] and sha(encoded(a['input_contract']))==binding['input_contract_sha256'],'DIAGNOSTICS_INPUT_BINDING')
    # Cohort raw bytes are preserved separately because whitespace is part of its source hash.
    import base64
    cohort=base64.b64decode(a['cohort'],validate=True)
    source_raw=base64.b64decode(a['source_capture'],validate=True)
    input_contract(a['input_contract'],cohort,source_raw)
    require(binding['program_contract']['input_contract_sha256']==binding['input_contract_sha256'] and binding['program_contract']['input_capture_sha256']==a['input_contract']['source_evidence_sha256'],'DIAGNOSTICS_REVIEWED_INPUT_CHANGED')
    return a


def preflight(provider,config,binding,prepared):
    from orchestrator.diagnostics_execution import verify_prepared
    verify_prepared(prepared,binding);a=scope(provider,config,binding)
    snapshot=provider.billing_snapshot()
    require(binding['cost']==quote(binding['resources'],snapshot['rates'],binding['overhead_micro_usd']),'DIAGNOSTICS_ACTUAL_RATE_CHANGED')
    files={k:{f:v[f] for f in ('sha256','bytes')} for k,v in a['input_contract']['files'].items()}
    verify_volume_members(provider,a['data_volume_id'],files,prefix=a['data_subpath'])
    package={k:{'sha256':v,'bytes':(Path(prepared)/k).stat().st_size} for k,v in inventory(prepared).items()}
    provider._verify_volume(a['package_volume_id'],package)
    app=provider.modal.App.lookup(a['app_name'],create_if_missing=False,client=provider.client)
    app.hydrate(client=provider.client)
    require(app.object_id==a['app_id'],'DIAGNOSTICS_APP_BINDING')
    image=provider.modal.Image.from_id(a['image_id'],client=provider.client);image.build(app)
    require(image.object_id==a['image_id'],'DIAGNOSTICS_IMAGE_BINDING')
    return {'status':'READY','billing_snapshot':snapshot,'image_id':image.object_id,'input_contract_sha256':binding['input_contract_sha256'],'package_inventory_sha256':sha(encoded(package)),'native_guard_required_before_analysis':True}


def create(provider,config,binding,package):
    a=scope(provider,config,binding);resources=binding['resources']
    sb=provider.modal.Sandbox.create('/bin/sleep',str(resources['timeout_seconds']),
        app=provider.modal.App.lookup(a['app_name'],create_if_missing=False,client=provider.client),
        name='diagnostics-'+sha(encoded(binding))[:32],image=provider.modal.Image.from_id(a['image_id'],client=provider.client),
        cpu=(resources['cpu'],resources['cpu']),memory=(resources['memory_mib'],resources['memory_mib']),
        timeout=resources['timeout_seconds'],block_network=True,include_oidc_identity_token=False,secrets=[],
        encrypted_ports=[],h2_ports=[],unencrypted_ports=[],
        volumes={'/data':volume_mount(provider,a['data_volume_id'],prefix=a['data_subpath']),
                 '/reviewed':volume_mount(provider,a['package_volume_id'])},client=provider.client)
    return {'provider_id':sb.object_id,'entrypoint':'idle-only','binding_sha256':sha(encoded(binding))}


def launch(provider,provider_id,binding):
    sb=provider._sandbox(provider_id)
    a=scope(provider,provider.config,binding)
    interpreter=a['environment'].get('interpreter','/usr/bin/python3')
    if interpreter not in {'/usr/bin/python3','/opt/research-scientific-python/bin/python'}:
        raise ValueError('DIAGNOSTICS_FIXED_INTERPRETER')
    sb.exec(interpreter,'-s','-B','/reviewed/run.py','--binding',sha(encoded(binding)),
        timeout=binding['resources']['timeout_seconds'],workdir='/tmp',
        stdout=provider.modal.stream_type.StreamType.DEVNULL,stderr=provider.modal.stream_type.StreamType.DEVNULL)
    return {'provider_id':provider_id,'submitted':True,'binding_sha256':sha(encoded(binding))}


WORKER = r'''import argparse,hashlib,importlib.util,importlib.metadata,json,os,stat,sys
from pathlib import Path
os.umask(0o077)
sys.path.insert(0,'/reviewed')
from orchestrator.diagnostics_contract import require,sha,encoded,validate_outputs,strict
p=argparse.ArgumentParser();p.add_argument('--binding',required=True);a=p.parse_args()
manifest=strict(Path('/reviewed/manifest.json').read_bytes());binding=manifest['binding']
require(sha(encoded(binding))==a.binding,'DIAGNOSTICS_WORKER_BINDING')
result={'schema':'modal-result/v1','binding_sha256':a.binding,'status':'FAILED','files':{}}
try:
    for root in [Path('/reviewed'),Path('/data')]:
        require(not root.is_symlink() and os.statvfs(root).f_flag & os.ST_RDONLY,'DIAGNOSTICS_READONLY_MOUNT_REQUIRED')
    package_paths=list(Path('/reviewed').rglob('*'))
    require(all(not p.is_symlink() and (p.is_file() or p.is_dir()) for p in package_paths),'DIAGNOSTICS_PACKAGE_ALIAS')
    actual={str(p.relative_to('/reviewed')):p for p in package_paths if p.is_file()}
    require(set(actual)==set(manifest['files'])|{'manifest.json'},'DIAGNOSTICS_PACKAGE_MEMBERS')
    for name,p in actual.items():
        require(not any(x.is_symlink() for x in [p,*p.parents]) and p.stat().st_nlink==1,'DIAGNOSTICS_PACKAGE_ALIAS')
        if name!='manifest.json':require(sha(p.read_bytes())==manifest['files'][name],'DIAGNOSTICS_PACKAGE_HASH')
    req=binding['program_contract']['requirements']
    require('.'.join(map(str,sys.version_info[:2]))==req['python'],'DIAGNOSTICS_NATIVE_PYTHON')
    observed={name:importlib.metadata.version(name) for name in req['distributions']}
    require(observed==req['distributions'],'DIAGNOSTICS_NATIVE_DEPENDENCIES')
    forbidden={'MODAL_IDENTITY_TOKEN','AWS_ACCESS_KEY_ID','AWS_SECRET_ACCESS_KEY','OPENAI_API_KEY','ANTHROPIC_API_KEY','CLAUDE_CODE_OAUTH_TOKEN'}
    require(not any(os.environ.get(k) for k in forbidden),'DIAGNOSTICS_AMBIENT_CREDENTIAL')
    files=binding['input_contract']['files'];root=Path('/data')
    allpaths=list(root.rglob('*'))
    require(all(not p.is_symlink() and (p.is_file() or p.is_dir()) for p in allpaths),'DIAGNOSTICS_INPUT_ALIAS')
    paths={str(p.relative_to(root)):p for p in allpaths if p.is_file()}
    require(set(paths)==set(files),'DIAGNOSTICS_INPUT_MEMBERS')
    for name,p in paths.items():
        row=files[name];require(p.stat().st_nlink==1 and p.stat().st_size==row['bytes'],'DIAGNOSTICS_INPUT_SIZE')
        h=hashlib.sha256()
        with p.open('rb') as f:
            for chunk in iter(lambda:f.read(1024*1024),b''):h.update(chunk)
        require(h.hexdigest()==row['sha256'],'DIAGNOSTICS_INPUT_HASH')
    proof={'schema':'diagnostics-native-preflight/v1','status':'PASS','binding_sha256':a.binding,
        'environment_sha256':binding['environment_sha256'],'input_contract_sha256':binding['input_contract_sha256'],
        'requirements':req,'input_files':len(paths),'read_only_mounts':['/data','/reviewed'],'credential_free':True}
    Path('/tmp/native-proof.json').write_bytes(encoded(proof))
    out=Path('/tmp/outputs');out.mkdir(mode=0o700,exist_ok=False)
    spec=importlib.util.spec_from_file_location('reviewed_analysis','/reviewed/code/analysis.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    module.main(root,out,{'execution_plan':strict(Path('/reviewed/execution-plan.json').read_bytes()),'runtime':binding})
    receipt=validate_outputs(out,binding)
    result.update(status='COMPLETE',files=receipt['files'])
finally:
    Path('/tmp/research-result.json').write_bytes(encoded(result))
'''


def native_proof(provider,sb,binding):
    from orchestrator.experiment_result import strict
    value=strict(provider._read(sb,'/tmp/native-proof.json',65536))
    expected={'schema':'diagnostics-native-preflight/v1','status':'PASS','binding_sha256':sha(encoded(binding)),
        'environment_sha256':binding['environment_sha256'],'input_contract_sha256':binding['input_contract_sha256'],
        'requirements':binding['program_contract']['requirements'],'input_files':len(binding['input_contract']['files']),
        'read_only_mounts':['/data','/reviewed'],'credential_free':True}
    require(value==expected,'DIAGNOSTICS_NATIVE_PROOF_REQUIRED')
    return value
