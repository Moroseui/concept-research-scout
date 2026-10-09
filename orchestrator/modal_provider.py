"""Pinned Modal SDK adapter. Status/collection never create a scientific process.

All remote assets already exist and are hash-bound before submission. Asset
preparation is a separate, cost-accounted operation; this adapter never builds an
image or silently uploads missing data. No credential is injected into a job.
"""
from decimal import Decimal, ROUND_CEILING
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
import os
from pathlib import Path, PurePosixPath
import re
import stat

from orchestrator import private_records
from orchestrator.manual_runtime import package_inventory
from orchestrator.manual_executor import digest, read, inventory
from orchestrator.modal_executor import canonical
from orchestrator.modal_budget import RATES, estimate

from orchestrator.modal_files import MAX_FILE, MAX_TOTAL, safe_name, member_map


def verified_sdk(config):
    folder=Path(config['sdk_package']).absolute()
    if folder.is_symlink() or folder.resolve()!=folder or not folder.is_dir():raise ValueError('MODAL_SDK_ROOT')
    for path in [folder,*folder.parents]:
        st=path.stat()
        if st.st_uid!=0 or st.st_mode&0o022:raise ValueError('MODAL_SDK_PARENT_WRITABLE')
    items=package_inventory(folder)
    for name in items:
        st=(folder/name).lstat()
        if st.st_uid!=0 or (not stat.S_ISLNK(st.st_mode) and st.st_mode&0o022):raise ValueError('MODAL_SDK_WRITABLE')
    if digest(canonical(items))!=config['sdk_sha256']:raise ValueError('MODAL_SDK_PACKAGE_CHANGED')
    spec=importlib.util.find_spec('modal')
    if spec is None or Path(spec.origin).resolve()!=folder/'modal/__init__.py':raise ValueError('MODAL_SDK_IMPORT_PATH')
    import modal
    if modal.__version__!='1.6.0':raise ValueError('MODAL_SDK_VERSION')
    return modal


class ModalProvider:
    def __init__(self,config):
        self.config=config
        self.modal=verified_sdk(config)
        credential=Path(config['credential_file'])
        private_records.check(credential)
        st=credential.stat()
        if st.st_uid!=os.getuid() or stat.S_IMODE(st.st_mode)!=0o600:raise ValueError('MODAL_CREDENTIAL_METADATA')
        credentials=read(credential)
        if credentials.get('workspace')!=config['workspace']:raise ValueError('MODAL_CREDENTIAL_WORKSPACE')
        self.client=self.modal.Client.from_credentials(credentials['token_id'],credentials['token_secret'])
        # Credential values are never returned, logged, included in a manifest,
        # or passed through Sandbox secrets/env. They remain in the SDK client.

    def verify_development_volume(self, volume_id, cohort_raw, source_raw, authority_raw):
        from orchestrator.modal_development_inputs import verify_volume
        return verify_volume(self, volume_id, cohort_raw, source_raw, authority_raw)

    def terminal_preprocessing_steps(self, provider_id, binding):
        from orchestrator.modal_preprocessing_provider import terminal_steps
        return terminal_steps(self, provider_id, binding)

    def terminal_fit_checkpoint(self, provider_id, binding):
        from orchestrator.modal_fit_provider import terminal_checkpoint
        return terminal_checkpoint(self, provider_id, binding)

    def fit_health(self, provider_id, binding, log_path=None, *, now=None):
        from orchestrator.modal_fit_health import observe
        return observe(self, provider_id, binding, log_path, now=now)

    def billing_snapshot(self):
        """Authenticated read-only Team billing, preserved by the caller."""
        from orchestrator.modal_billing import capture
        self.client.hello()
        workspace = self.modal.Workspace.from_context(client=self.client)
        workspace.hydrate(client=self.client)
        return capture(workspace, self.config['workspace'])

    def build_registry_image(self,app,registry):
        # Supported builder selection; the pinned native implementation must
        # compose FROM only. Older builders add package-install RUN commands.
        from modal._image import _Image
        from modal.config import config
        previous=os.environ.get('MODAL_IMAGE_BUILDER_VERSION')
        os.environ['MODAL_IMAGE_BUILDER_VERSION']='2025.06'
        try:
            if config.get('image_builder_version')!='2025.06':raise ValueError('MODAL_IMAGE_BUILDER_PIN')
            commands=_Image._registry_setup_commands(registry,'2025.06',[],None)
            if commands!=['FROM '+registry]:raise ValueError('MODAL_IMAGE_BUILD_COMMANDS')
            return self.modal.Image.from_registry(registry).build(app)
        finally:
            if previous is None:os.environ.pop('MODAL_IMAGE_BUILDER_VERSION',None)
            else:os.environ['MODAL_IMAGE_BUILDER_VERSION']=previous

    def _volume(self,ident):
        return self.modal.Volume.from_id(ident,client=self.client)

    def _sandbox(self,ident):
        return self.modal.Sandbox.from_id(ident,client=self.client)

    def _verify_volume_members(self,ident,expected):
        volume=self._volume(ident)
        entries=volume.listdir('/',recursive=True)
        names=[x.path.lstrip('/') for x in entries if x.type.name=='FILE']
        actual={x.path.lstrip('/'):x.size for x in entries if x.type.name=='FILE'}
        others=[x for x in entries if x.type.name not in {'FILE','DIRECTORY'}]
        if others or len(names)!=len(set(names)) or actual!={k:v['bytes'] for k,v in expected.items()}:raise ValueError('MODAL_VOLUME_MEMBER_SET')
        return volume

    def _verify_volume(self,ident,expected):
        volume=self._verify_volume_members(ident,expected)
        for name,item in expected.items():
            hashed=hashlib.sha256();size=0
            for chunk in volume.read_file('/'+name):
                size+=len(chunk)
                if size>item['bytes']:raise ValueError('MODAL_VOLUME_SIZE')
                hashed.update(chunk)
            if size!=item['bytes'] or hashed.hexdigest()!=item['sha256']:raise ValueError('MODAL_VOLUME_HASH')
        return volume

    def preflight(self,config,binding,prepared):
        if binding.get('purpose')=='M4_ITEM6_CPU':
            from orchestrator.diagnostics_modal import preflight
            return preflight(self,config,binding,prepared)
        if binding.get("purpose")=="M4_ITEM4":
            from orchestrator.modal_item4_provider import preflight
            return preflight(self,config,binding,prepared)
        if config!=self.config or digest(canonical(config))!=binding['runtime_sha256']:raise ValueError('MODAL_PROVIDER_RUNTIME')
        if binding['cost']!=estimate(binding['resources'],binding['overhead_micro_usd']):raise ValueError('MODAL_PROVIDER_ESTIMATE')
        # Data authority is bound by the reviewed run's complete input contract,
        # not inferred from possession of a Modal Volume or a credential.
        if binding.get('input_contract')!=config['input_contract'] or binding['input_contract_sha256']!=digest(canonical(config['input_contract'])):raise ValueError('MODAL_INPUT_CONTRACT_BINDING')
        contract=config['input_contract']
        if contract.get('scope')!='DEVELOPMENT_99_ONLY' or contract.get('count')!=99:raise ValueError('MODAL_DATA_SCOPE')
        for key in ('cohort_sha256','split_sha256','cache_map_sha256'):
            if not isinstance(contract.get(key),str) or not re.fullmatch('[0-9a-f]{64}',contract[key]):raise ValueError('MODAL_DATA_PIN')
        if binding['image_id']!=config['image_id'] or binding['data_volume_id']!=config['data_volume_id'] or binding['package_volume_id']!=config['package_volume_id'] or binding['wheel_volume_id']!=config['wheel_volume_id']:
            raise ValueError('MODAL_PROVIDER_ASSET_BINDING')
        from orchestrator.modal_cleanup import expired
        if expired(config):raise ValueError('MODAL_ASSET_RETENTION_EXPIRED')
        self.client.hello()
        workspace=self.modal.Workspace.from_context(client=self.client);workspace.hydrate(client=self.client)
        if workspace.name!=config['workspace']:raise ValueError('MODAL_AUTHENTICATED_WORKSPACE')
        rates=dict(workspace.billing.rates())
        keys={'cpu_hour_cost_sandbox':RATES['cpu_core_hour'],'mem_gib_hour_cost_sandbox':RATES['memory_gib_hour'],
              {'A100-80GB':'gpu_hour_cost_a100_80gb','T4':'gpu_hour_cost_t4','L4':'gpu_hour_cost_l4'}[binding['resources']['gpu']]:RATES[binding['resources']['gpu']]}
        if any(Decimal(str(rates.get(k,'-1')))!=Decimal(v) for k,v in keys.items()):raise ValueError('MODAL_RATE_CHANGED')
        cycle=datetime.now(timezone.utc).strftime('%Y-%m')
        billing=workspace.billing.summary(cycle=cycle)
        # Field names are pinned to SDK 1.6.0's BillingSummary (checked in tests).
        spent=max(Decimal(str(billing.metered_cost)),Decimal(str(billing.billed_cost)))
        if not spent.is_finite() or spent<0:raise ValueError('MODAL_BILLING_VALUE')
        data=member_map(config['data_files'],maximum=2*1024**3)
        package=member_map({k:{'sha256':v,'bytes':(Path(prepared)/k).stat().st_size} for k,v in inventory(prepared).items()})
        self._verify_volume(config['wheel_volume_id'],member_map(config['wheel_files']))
        self._verify_volume(config['data_volume_id'],data)
        self._verify_volume(config['package_volume_id'],package)
        image=self.modal.Image.from_id(config['image_id'],client=self.client)
        # Image.from_id is a lazy image loader in SDK1.6.0. Its supported build
        # resolves ImageFromId against this existing App; no registry build.
        app=self.modal.App.lookup(config['app_name'],create_if_missing=False,client=self.client)
        image.build(app)
        if image.object_id!=config['image_id']:raise ValueError('MODAL_IMAGE_ID_CHANGED')
        return {'status':'READY','workspace':workspace.name,'cycle':cycle,
                'workspace_spent_micro':int((spent*1000000).to_integral_value(rounding=ROUND_CEILING)),
                'rates':{k:str(rates[k]) for k in keys},'image_id':image.object_id,
                'data_inventory_sha256':digest(canonical(data)), 'package_inventory_sha256':digest(canonical(package)),
                'checked_at':datetime.now(timezone.utc).isoformat()}

    def create(self,config,binding,package):
        if binding.get('purpose')=='M4_ITEM6_CPU':
            from orchestrator.diagnostics_modal import create
            return create(self,config,binding,package)
        if binding.get("purpose")=="M4_ITEM4":
            from orchestrator.modal_item4_provider import create
            return create(self,config,binding,package)
        if config!=self.config:raise ValueError('MODAL_PROVIDER_RUNTIME')
        # Immutable, prebuilt assets only; no image build or upload at dispatch.
        resources=binding['resources']
        sb=self.modal.Sandbox.create('/bin/sleep',str(resources['timeout_seconds']),
            app=self.modal.App.lookup(config['app_name'],create_if_missing=False,client=self.client),
            name='research-'+digest(canonical(binding))[:32],
            image=self.modal.Image.from_id(config['image_id'],client=self.client),
            gpu=resources['gpu'],cpu=(resources['cpu'],resources['cpu']),
            memory=(resources['memory_mib'],resources['memory_mib']),timeout=resources['timeout_seconds'],
            block_network=True,include_oidc_identity_token=False,secrets=[],
            encrypted_ports=[],h2_ports=[],unencrypted_ports=[],
            volumes={'/data':self._volume(config['data_volume_id']).with_mount_options(read_only=True),
                     '/reviewed':self._volume(config['package_volume_id']).with_mount_options(read_only=True),
                     '/wheels':self._volume(config['wheel_volume_id']).with_mount_options(read_only=True)},
            client=self.client)
        return {'provider_id':sb.object_id,'entrypoint':'idle-only','binding_sha256':digest(canonical(binding))}

    def launch(self,provider_id,binding):
        if binding.get('purpose')=='M4_ITEM6_CPU':
            from orchestrator.diagnostics_modal import launch
            return launch(self,provider_id,binding)
        if binding.get('purpose')=='M4_ITEM4':
            from orchestrator.modal_item4_provider import launch
            return launch(self,provider_id,binding)
        sb=self._sandbox(provider_id)
        # Only this method launches science. The caller durably records intent
        # first and never calls it again after an uncertain return. SDK internal
        # retries reuse one task ID + exec ID (pinned SDK source inspected).
        sb.exec('/usr/bin/python3','-B','-s','/reviewed/run.py',
                '--binding',digest(canonical(binding)),timeout=binding['resources']['timeout_seconds'],
                workdir='/tmp',stdout=self.modal.stream_type.StreamType.DEVNULL,
                stderr=self.modal.stream_type.StreamType.DEVNULL)
        return {'provider_id':provider_id,'submitted':True,'binding_sha256':digest(canonical(binding))}

    def _read(self,sb,path,limit):
        info=sb.filesystem.stat(path)
        if info.type.value!='file' or not 0<=info.size<=limit:raise ValueError('MODAL_RESULT_FILE_TYPE_OR_SIZE')
        data=sb.filesystem.read_bytes(path)
        if len(data)!=info.size or len(data)>limit:raise ValueError('MODAL_RESULT_SIZE_CHANGED')
        return data

    def _result(self,sb,binding):
        raw=self._read(sb,'/tmp/research-result.json',1024*1024)
        result=json.loads(raw)
        if set(result)!={'schema','binding_sha256','status','files'} or result['schema']!='modal-result/v1' or result['binding_sha256']!=digest(canonical(binding)):
            raise ValueError('MODAL_RESULT_BINDING')
        if result['status'] not in {'COMPLETE','FAILED'}:raise ValueError('MODAL_RESULT_STATE')
        if result['status']=='COMPLETE':
            member_map(result['files'])
            if set(result['files'])!=set(binding['outputs']):raise ValueError('MODAL_RESULT_EXPECTED_MEMBERS')
        elif result['files']:raise ValueError('MODAL_FAILED_RESULT_FILES')
        return result

    def status(self,provider_id,binding):
        if binding.get('purpose')=='M4_ITEM4' and 'preprocessing' in binding:
            from orchestrator.modal_preprocessing_provider import status as preprocess
            return preprocess(self,provider_id,binding)
        if binding.get("purpose")=="M4_ITEM4":
            from orchestrator.modal_fit_result import status
            return status(self,provider_id,binding)
        sb=self._sandbox(provider_id)
        try:result=self._result(sb,binding);state=result['status']
        except self.modal.exception.SandboxFilesystemNotFoundError:
            state='RUNNING' if sb.poll() is None else 'UNKNOWN'
        return {'provider_id':provider_id,'binding_sha256':digest(canonical(binding)),'status':state}

    @private_records.private_umask
    def collect(self,provider_id,binding,destination):
        if binding.get('purpose')=='M4_ITEM4' and 'preprocessing' in binding:
            from orchestrator.modal_preprocessing_provider import collect as preprocess
            return preprocess(self,provider_id,binding,destination)
        if binding.get("purpose")=="M4_ITEM4":
            from orchestrator.modal_fit_result import collect
            return collect(self,provider_id,binding,destination)
        sb=self._sandbox(provider_id);result=self._result(sb,binding)
        if result['status']!='COMPLETE':raise ValueError('MODAL_RESULT_NOT_COMPLETE')
        native=None
        if binding.get('purpose')=='M4_ITEM6_CPU':
            from orchestrator.diagnostics_modal import native_proof
            native=native_proof(self,sb,binding)
        if sb.filesystem.stat('/tmp/outputs').type.value!='directory':raise ValueError('MODAL_OUTPUT_ROOT_ALIAS')
        for name,item in result['files'].items():
            # Verify each parent is a directory; no alias out of output root.
            relative=PurePosixPath(safe_name(name));parent=PurePosixPath('/tmp/outputs')
            for component in relative.parts[:-1]:
                parent/=component
                if sb.filesystem.stat(str(parent)).type.value!='directory':raise ValueError('MODAL_OUTPUT_PARENT_ALIAS')
            data=self._read(sb,'/tmp/outputs/'+name,item['bytes'])
            if len(data)!=item['bytes'] or digest(data)!=item['sha256']:raise ValueError('MODAL_RESULT_HASH')
            target=Path(destination)/name;private_records.mkdir(target.parent,parents=True,exist_ok=True)
            private_records.write_bytes(target,data)
        if self._result(sb,binding)!=result:raise ValueError('MODAL_RESULT_CHANGED_DURING_COLLECTION')
        return {'provider_id':provider_id,'binding_sha256':result['binding_sha256'],
                'file_sha256':{k:v['sha256'] for k,v in result['files'].items()},
                **({'native_preflight':native} if native is not None else {})}

    def terminate(self,provider_id):
        sb=self._sandbox(provider_id);sb.terminate(wait=True)
        return {'provider_id':provider_id,'terminated':sb.poll() is not None}
