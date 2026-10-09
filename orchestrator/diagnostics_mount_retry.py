"""One operator-authorized item6 native-mount retry, same owner and original bytes."""
from pathlib import Path
import hashlib
import json
from orchestrator.diagnostics_contract import require,sha,encoded

CHANGE='item6-contract-service-identity-20261008'
ORIGINAL='d9bd52cf0b27045e1e23ba018ac44d9ed25cb2ab8ccf81f8c22cf33b4fb264e3'
PARENT='2b0ab32a1f4d4890bb0f17a9986440e0675debcd9cbfc56746183e3dbab31795'
ORIGINAL_PROVIDER='sb-01M4CJFPRC3SJ1ZXPXG6APJA5H'
PROVIDER_ID='sb-01M4CQK1PH5ZWM51T4JS4JR9XQ'
PRIOR_JOB='diagnostics-b203ee1ce27e909d9d78d44a-mount-retry1'
PRIOR_RECORD=Path('/var/lib/research-system-manual-sprint10-deployment/item6-native-mount-repair-20261008')
PRIOR_PERMIT_SHA='887cdacc0d70d0b1d8c45b596ddd9c07a78585ed3ea14e43597feec6428d4172'
CONTROLS_SHA='994f4caee6cdaeb1ba174c6b299fd789a6763a6e72693970cc4b89028992df7d'
FAILED_SHA='021de061ef5e58add5d3bc9d9fe85aef8cacb50d11835b073b17cadcd09d977d'
REPAIR_AUTHORITY='6a18f3e242116c5ebf3eeaa5e1e61c3c70a400c6b0587a5721517014ac8d12ff'
RUN='diagnostics-b203ee1ce27e909d9d78d44a'
AUTHORITY='020b3f67307dedaa098673dd5ece93d324396f473d6d55a85d6fb5771dba2f0e'
RECORD=Path('/var/lib/research-system-manual-sprint10-deployment')/CHANGE
ROOT=Path('/opt/research-system/manual-repair-helpers')/CHANGE
BASE_SELECTION='8638bac78a62a2c7990cf468751b3656d0163bf61f6c020c9dce7364e0962a44'
MOUNTS={'data':{'volume_id':'vo-vtVw4B5nkuvkuMRxbTbYzG','sub_path':'/inputs'},
        'package':{'volume_id':'vo-wFiz1Is7z07hScHGQI12Sf','sub_path':'/'}}


def guard_program():
    """Fixed infrastructure source; scientific code remains in the old package."""
    from orchestrator import diagnostics_native_guard,modal_volume_path
    resolver=Path(modal_volume_path.__file__).read_text()
    guard=Path(diagnostics_native_guard.__file__).read_text()
    return ("import sys,types\nsys.path.insert(0,'/reviewed')\n"
        "parent=types.ModuleType('orchestrator');parent.__path__=['/reviewed/orchestrator']\n"
        "sys.modules.setdefault('orchestrator',parent)\n"
        "resolver=types.ModuleType('orchestrator.modal_volume_path')\n"
        +"exec("+repr(resolver)+",resolver.__dict__)\n"
        +"sys.modules['orchestrator.modal_volume_path']=resolver\n"
        +"guard={}\nexec("+repr(guard)+",guard)\n")


def program():return guard_program()+WORKER
def control_program():return guard_program()+CONTROL

def descriptor(review_sha):
    return {'schema':'item6-native-mount-retry/v1','attempt':3,'parent':PARENT,'original_parent':ORIGINAL,'repair_authority_sha256':REPAIR_AUTHORITY,
            'authority_sha256':AUTHORITY,'review_sha256':review_sha,
            'worker_sha256':sha(program().encode()),'controls_sha256':sha(control_program().encode()),'mounts':MOUNTS}


def permit():
    from orchestrator.manual_host_guard import trusted
    from orchestrator.autonomy_review import verify_result
    from tools.manual_promotion import manifest_check
    installed=manifest_check(Path('/'),str(RECORD))
    require(json.loads(trusted(RECORD/'complete.json').read_bytes()).get('status')=='PASS','DIAGNOSTICS_RETRY_INSTALL_INCOMPLETE')
    require(installed['change']==CHANGE and installed['authority_sha256']==AUTHORITY,'DIAGNOSTICS_RETRY_INSTALLATION')
    require(sha(trusted(ROOT/'docs/ITEM6_NATIVE_MOUNT_AUTHORITY_20261008.txt').read_bytes())==AUTHORITY,'DIAGNOSTICS_RETRY_AUTHORITY')
    review=verify_result(trusted(RECORD/'review'))
    require(review['verdict']=='APPROVE' and review['change_id']==CHANGE
        and review['source_sha']==installed['source'] and review['report_sha256']==installed['review_sha256'], 'DIAGNOSTICS_RETRY_REVIEW')
    manifest=json.loads(trusted(RECORD/'review/packet-manifest.json').read_bytes())
    for name in installed['component_files']:
        require(sha(trusted(ROOT/name).read_bytes())==manifest['source_files'][name],'DIAGNOSTICS_RETRY_REVIEWED_BYTES')
    require(Path(__file__).resolve()==ROOT/'orchestrator/diagnostics_mount_retry.py','DIAGNOSTICS_RETRY_IMPORTED_SOURCE')
    require(sha(trusted(ROOT/'docs/ITEM6_CONTRACT_RETRY_OPERATOR_APPROVAL_20261008.txt').read_bytes())==REPAIR_AUTHORITY,'DIAGNOSTICS_REPAIR_AUTHORITY')
    prior_permit()
    value=json.loads(trusted(RECORD/'permit.json').read_bytes())
    require(value=={'schema':'item6-native-mount-permit/v1','parent':PARENT,'provider_id':PROVIDER_ID,
        'base_selection_sha256':BASE_SELECTION,'original_reserved_micro_usd':3903200,'repair_authority_sha256':REPAIR_AUTHORITY,
        'authority_sha256':AUTHORITY,'descriptor':descriptor(review['report_sha256'])},'DIAGNOSTICS_RETRY_EXACT_PERMIT')
    failed_raw=trusted(RECORD/'parent-failed-stop.json').read_bytes()
    require(sha(failed_raw)==FAILED_SHA,'DIAGNOSTICS_REPAIR_ORIGINAL_FAILURE')
    original=json.loads(failed_raw)
    require(original['result']=={'binding_sha256':PARENT,'files':{},'schema':'modal-result/v1','status':'FAILED'}
        and original['stop']=={'provider_id':PROVIDER_ID,'terminated':True}
        and original['reservation_retained'] is True,'DIAGNOSTICS_RETRY_TERMINAL_PARENT')
    return value


def parent_binding(binding):
    if 'mechanical_retry' not in binding:return binding
    allowed=permit();old={k:v for k,v in binding.items() if k!='mechanical_retry'}
    require(binding['mechanical_retry']==allowed['descriptor'] and sha(encoded(old))==ORIGINAL
        and old['run_id']==RUN,'DIAGNOSTICS_RETRY_BINDING')
    return old


def select(selected):
    if not (RECORD/'permit.json').exists():return selected
    allowed=permit()
    require(sha(encoded(selected['binding']))==ORIGINAL and selected['sha256']==BASE_SELECTION,
        'DIAGNOSTICS_RETRY_ORIGINAL_SELECTION')
    assets=selected['provider']['diagnostics_assets']
    require(assets['data_volume_id']==MOUNTS['data']['volume_id'] and assets['data_subpath']==MOUNTS['data']['sub_path']
        and assets['package_volume_id']==MOUNTS['package']['volume_id'],'DIAGNOSTICS_RETRY_MOUNT_SELECTION')
    return {**selected,'binding':{**selected['binding'],'mechanical_retry':allowed['descriptor']},
            'sha256':sha(encoded(allowed))}


def job(binding):
    parent_binding(binding)
    return binding['run_id']+('-contract-retry1' if 'mechanical_retry' in binding else '')


def prior_permit():
    from orchestrator.manual_host_guard import trusted
    from tools.manual_promotion import manifest_check
    previous=manifest_check(Path('/'),str(PRIOR_RECORD))
    require(previous['source']=='02cec5b3fccc803f82f95449d68f9148b896c1ed'
        and previous['review_sha256']=='a27c615d7a2cf01927e159433b8cea24de48c4e4c3def090b496459006d18255',
        'DIAGNOSTICS_REPAIR_PRIOR_APPROVAL')
    from orchestrator.autonomy_review import verify_result
    q=verify_result(trusted(PRIOR_RECORD/'review'))
    require(q['verdict']=='APPROVE' and q['source_sha']==previous['source'] and q['report_sha256']==previous['review_sha256']
        and json.loads(trusted(PRIOR_RECORD/'complete.json').read_bytes())['status']=='PASS','DIAGNOSTICS_REPAIR_PRIOR_APPROVAL')
    raw=trusted(PRIOR_RECORD/'permit.json').read_bytes()
    require(sha(raw)==PRIOR_PERMIT_SHA,'DIAGNOSTICS_REPAIR_PRIOR_PERMIT')
    return json.loads(raw)


def retained_parent(accounts,binding):
    if 'mechanical_retry' not in binding:return set()
    old=parent_binding(binding)
    previous={**old,'mechanical_retry':prior_permit()['descriptor']}
    expected={ORIGINAL:(old,ORIGINAL_PROVIDER),PARENT:(previous,PROVIDER_ID)}
    for ident,(body,provider_id) in expected.items():
        require(sha(encoded(body))==ident,'DIAGNOSTICS_REPAIR_PRIOR_BINDING')
        row=accounts.db.execute('SELECT * FROM autonomy_compute WHERE id=?',(ident,)).fetchone()
        require(row is not None and row['run']==RUN and row['binding']==encoded(body).decode()
            and row['reserved_micro_usd']==1951600 and row['provider_id']==provider_id
            and row['status']=='RUNNING','DIAGNOSTICS_RETRY_PARENT_LEDGER')
    return set(expected)


WORKER=r'''import argparse,hashlib,importlib.util,importlib.metadata,json,os,sys
from pathlib import Path
os.umask(0o077)
sys.path.insert(0,'/reviewed')
from orchestrator.diagnostics_contract import require,sha,encoded,validate_outputs,strict
parser=argparse.ArgumentParser();parser.add_argument('--binding',required=True);parser.add_argument('--retry',required=True)
a=parser.parse_args();retry=strict(a.retry.encode())
raw=Path('/reviewed/manifest.json').read_bytes();manifest=strict(raw);old=manifest['binding']
require(sha(encoded(old))==retry['original_parent'],'DIAGNOSTICS_RETRY_NATIVE_PARENT')
binding={**old,'mechanical_retry':retry};require(sha(encoded(binding))==a.binding,'DIAGNOSTICS_WORKER_BINDING')
result={'schema':'modal-result/v1','binding_sha256':a.binding,'status':'FAILED','files':{}}
phase='preflight'
try:
    req=binding['program_contract']['requirements']
    require('.'.join(map(str,sys.version_info[:2]))==req['python'],'DIAGNOSTICS_NATIVE_PYTHON')
    require({name:importlib.metadata.version(name) for name in req['distributions']}==req['distributions'],'DIAGNOSTICS_NATIVE_DEPENDENCIES')
    forbidden={'MODAL_IDENTITY_TOKEN','AWS_ACCESS_KEY_ID','AWS_SECRET_ACCESS_KEY','OPENAI_API_KEY','ANTHROPIC_API_KEY','CLAUDE_CODE_OAUTH_TOKEN'}
    require(not any(os.environ.get(k) for k in forbidden),'DIAGNOSTICS_AMBIENT_CREDENTIAL')
    package={name:{'sha256':pin} for name,pin in manifest['files'].items()}
    package['manifest.json']={'sha256':sha(raw),'bytes':len(raw)}
    roots,before=guard['verify'](retry['mounts'],binding['input_contract']['files'],package)
    Path('/tmp/mount-guard-before.json').write_bytes(encoded(before))
    out=Path('/tmp/outputs');out.mkdir(mode=0o700,exist_ok=False)
    try:
        phase='analysis'
        spec=importlib.util.spec_from_file_location('reviewed_analysis',roots['package']/'code/analysis.py')
        module=importlib.util.module_from_spec(spec);sys.modules[spec.name]=module;spec.loader.exec_module(module)
        module.main(roots['data'],out,{**binding['program_contract'],'execution_plan':strict((roots['package']/'execution-plan.json').read_bytes()),'runtime':binding})
    finally:
        # A scientific exception still triggers the complete post-analysis check;
        # neither failed analysis nor failed revalidation can emit COMPLETE.
        phase='postcheck'
        after_roots,after=guard['verify'](retry['mounts'],binding['input_contract']['files'],package)
        require(roots==after_roots and before==after,'DIAGNOSTICS_POST_ANALYSIS_INPUT_CHANGE')
        Path('/tmp/mount-guard-after.json').write_bytes(encoded(after))
        phase='analysis'
    require(not any(os.environ.get(k) for k in forbidden),'DIAGNOSTICS_AMBIENT_CREDENTIAL')
    phase='output_validation'
    receipt=validate_outputs(out,binding)
    mount_proof={'schema':'diagnostics-mount-verification/v1','status':'PASS','binding_sha256':a.binding,
        'worker_sha256':retry['worker_sha256'],'before':before,'after':after,'full_rehash_before_and_after':True}
    Path('/tmp/mount-verification.json').write_bytes(encoded(mount_proof))
    proof={'schema':'diagnostics-native-preflight/v1','status':'PASS','binding_sha256':a.binding,
        'environment_sha256':binding['environment_sha256'],'input_contract_sha256':binding['input_contract_sha256'],
        'requirements':req,'input_files':len(binding['input_contract']['files']),
        'read_only_mounts':['/data','/reviewed'],'credential_free':True}
    Path('/tmp/native-proof.json').write_bytes(encoded(proof))
    result.update(status='COMPLETE',files=receipt['files'])
except BaseException as error:
    failure={'schema':'diagnostics-worker-failure/v1','phase':phase,'exception_type':type(error).__name__}
    # No message/traceback/path/patient identifier leaves the worker here.
    if isinstance(error,KeyError) and error.args and error.args[0] in binding['program_contract']:
        failure['missing_contract_key']=error.args[0]
    Path('/tmp/worker-failure.json').write_bytes(encoded(failure))
    raise
finally:
    Path('/tmp/research-result.json').write_bytes(encoded(result))
'''


CONTROL=r'''import argparse,json,os,hashlib
from pathlib import Path
os.umask(0o077)
p=argparse.ArgumentParser();p.add_argument('--mounts',required=True);p.add_argument('--case',required=True);a=p.parse_args()
raw=b'synthetic non-patient mount-control fixture\n'
expected={'nested/source.bin':{'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw)}}
v={'schema':'diagnostics-mount-control/v1','case':a.case,'status':'FAILED','reason':None}
try:
    _,proof=guard['verify'](json.loads(a.mounts),expected,expected)
    v.update(status='PASS',proof=proof)
except ValueError as error:
    v.update(reason=str(error))
    if str(error)=='DIAGNOSTICS_WRITE_WAS_ALLOWED':v['status']='REJECTED_WRITABLE'
finally:
    Path('/tmp/mount-control.json').write_text(json.dumps(v,sort_keys=True))
'''


def validate_mount_proof(value,binding):
    parent_binding(binding)
    require(set(value)=={'schema','status','binding_sha256','worker_sha256','before','after','full_rehash_before_and_after'}
        and value['schema']=='diagnostics-mount-verification/v1' and value['status']=='PASS'
        and value['binding_sha256']==sha(encoded(binding))
        and value['worker_sha256']==binding['mechanical_retry']['worker_sha256']
        and value['full_rehash_before_and_after'] is True and value['before']==value['after'], 'DIAGNOSTICS_RETRY_NATIVE_PROOF')
    expected_input={k:{field:v[field] for field in ('sha256','bytes')} for k,v in binding['input_contract']['files'].items()}
    expected={'data':(len(expected_input),sha(encoded(expected_input))),
        'package':(30,'788e55ab77f0bf03be72b99d9e47418722d003e2d1fb9edfc241db738c161976')}
    require(set(value['before'])==set(expected),'DIAGNOSTICS_RETRY_NATIVE_PROOF')
    for role,(count,pin) in expected.items():
        row=value['before'][role]
        require(set(row)=={'files','inventory_sha256','write_refusal_probes','volume_id','sub_path'}
            and row['files']==count and row['inventory_sha256']==pin
            and type(row['write_refusal_probes']) is int and row['write_refusal_probes']>=1
            and row['volume_id']==MOUNTS[role]['volume_id'] and row['sub_path']==MOUNTS[role]['sub_path'],
            'DIAGNOSTICS_RETRY_NATIVE_PROOF')
    return value


def validate_controls(value,binding):
    require(set(value)=={'schema','status','controls_sha256','cases'}
        and value['schema']=='diagnostics-native-controls/v1' and value['status']=='PASS'
        and value['controls_sha256']==binding['mechanical_retry']['controls_sha256']
        and set(value['cases'])=={'read_only','writable_data','writable_package'},'DIAGNOSTICS_RETRY_NATIVE_CONTROLS')
    ids=set()
    for name,row in value['cases'].items():
        require(set(row)=={'provider_id','terminated','mounts','result'} and row['terminated'] is True
            and isinstance(row['provider_id'],str) and row['provider_id'].startswith('sb-')
            and row['provider_id'] not in ids,'DIAGNOSTICS_RETRY_NATIVE_CONTROLS')
        ids.add(row['provider_id']);result=row['result'];mounts=row['mounts']
        require(set(mounts)=={'data','package'} and all(set(mounts[r])=={'volume_id','sub_path'} for r in mounts)
            and mounts['data']['sub_path']=='/inputs' and mounts['package']['sub_path']=='/'
            and all(isinstance(mounts[r]['volume_id'],str) and mounts[r]['volume_id'].startswith('vo-') for r in mounts)
            and len({mounts[r]['volume_id'] for r in mounts})==2
            and not {mounts[r]['volume_id'] for r in mounts}&{v['volume_id'] for v in MOUNTS.values()},
            'DIAGNOSTICS_RETRY_NATIVE_CONTROLS')
        require(result['schema']=='diagnostics-mount-control/v1' and result['case']==name,'DIAGNOSTICS_RETRY_NATIVE_CONTROLS')
        if name=='read_only':
            raw=b'synthetic non-patient mount-control fixture\n'
            pin=sha(encoded({'nested/source.bin':{'sha256':sha(raw),'bytes':len(raw)}}))
            expected={r:{**mounts[r],'files':1,'inventory_sha256':pin,'write_refusal_probes':2} for r in mounts}
            require(set(result)=={'schema','case','status','reason','proof'} and result['status']=='PASS'
                and result['reason'] is None and result['proof']==expected,'DIAGNOSTICS_RETRY_NATIVE_CONTROLS')
        else:require(set(result)=={'schema','case','status','reason'} and result['status']=='REJECTED_WRITABLE'
            and result['reason']=='DIAGNOSTICS_WRITE_WAS_ALLOWED','DIAGNOSTICS_RETRY_NATIVE_CONTROLS')
    return value


def validate_collected_proof(receipt,binding):
    if 'mechanical_retry' not in binding:return
    validate_mount_proof(receipt.get('mount_verification',{}),binding)
    validate_controls(receipt.get('native_mount_controls',{}),binding)



def controls(provider,binding,package):
    """Only after the executor's ordinary reservation; no patient mounts here."""
    import io
    from orchestrator.manual_driver import write_once
    from orchestrator.manual_executor import read
    from orchestrator import private_records as pr
    from orchestrator.modal_item4_policy import quote
    parent_binding(binding)
    work=Path(package).parent/'modal-executions'/job(binding)
    intent=read(pr.check(work/'create-intent.json'))
    require(intent['binding_sha256']==sha(encoded(binding)),'DIAGNOSTICS_CONTROLS_ADMISSION')
    resources={'gpu':None,'cpu':1,'memory_mib':1024,'timeout_seconds':120}
    cost=3*quote(resources,intent['preflight']['billing_snapshot']['rates'],0)['reserved_micro_usd']
    require(cost<binding['overhead_micro_usd'],'DIAGNOSTICS_CONTROLS_OVERHEAD')
    write_once(work/'native-mount-controls-intent.json',encoded({'binding_sha256':sha(encoded(binding)),
        'controls_sha256':binding['mechanical_retry']['controls_sha256'],'resources_per_case':resources,
        'cases':3,'maximum_compute_micro_usd':cost,'covered_by_reserved_overhead_micro_usd':binding['overhead_micro_usd']}))
    assets=provider.config['diagnostics_assets'];interpreter=assets['environment'].get('interpreter','/usr/bin/python3')
    require(interpreter in {'/usr/bin/python3','/opt/research-scientific-python/bin/python'},'DIAGNOSTICS_FIXED_INTERPRETER')
    source=control_program();require(sha(source.encode())==binding['mechanical_retry']['controls_sha256'],'DIAGNOSTICS_CONTROLS_SOURCE')
    result={'schema':'diagnostics-native-controls/v1','status':'PASS','controls_sha256':sha(source.encode()),'cases':{}}
    fixture=b'synthetic non-patient mount-control fixture\n'
    for name in ('read_only','writable_data','writable_package'):
        write_once(work/(name+'-volume-intent.json'),encoded({'case':name,'ephemeral':True,'patient_data':False}))
        with provider.modal.Volume.ephemeral(client=provider.client,version=2) as data:
            write_once(work/(name+'-data-volume.json'),encoded({'volume_id':data.object_id}))
            with provider.modal.Volume.ephemeral(client=provider.client,version=2) as package_volume:
                mounts={'data':{'volume_id':data.object_id,'sub_path':'/inputs'},
                        'package':{'volume_id':package_volume.object_id,'sub_path':'/'}}
                write_once(work/(name+'-package-volume.json'),encoded({'volume_id':package_volume.object_id}))
                with data.batch_upload() as upload:
                    upload.put_file(io.BytesIO(fixture),'/inputs/nested/source.bin')
                    upload.put_file(io.BytesIO(b'outside the selected synthetic subpath'),'/outside-selection.txt')
                with package_volume.batch_upload() as upload:upload.put_file(io.BytesIO(fixture),'/nested/source.bin')
                write_once(work/(name+'-sandbox-intent.json'),encoded({'case':name,'mounts':mounts,'resources':resources}))
                sandbox=provider.modal.Sandbox.create('/bin/sleep','120',
                    app=provider.modal.App.lookup(assets['app_name'],create_if_missing=False,client=provider.client),
                    name='mount-control-'+sha(encoded(binding))[:20]+'-'+name.replace('_','-'),
                    image=provider.modal.Image.from_id(assets['image_id'],client=provider.client),
                    cpu=(1,1),memory=(1024,1024),timeout=120,block_network=True,
                    include_oidc_identity_token=False,secrets=[],encrypted_ports=[],h2_ports=[],unencrypted_ports=[],
                    volumes={'/data':data.with_mount_options(read_only=name!='writable_data',sub_path='/inputs'),
                             '/reviewed':package_volume.with_mount_options(read_only=name!='writable_package')},client=provider.client)
                write_once(work/(name+'-sandbox.json'),encoded({'provider_id':sandbox.object_id,'mounts':mounts}))
                observed=None
                try:
                    process=sandbox.exec(interpreter,'-s','-B','-c',source,'--mounts',encoded(mounts).decode(),
                        '--case',name,timeout=90,workdir='/tmp',stdout=provider.modal.stream_type.StreamType.DEVNULL,
                        stderr=provider.modal.stream_type.StreamType.DEVNULL)
                    process.wait()
                    raw=provider._read(sandbox,'/tmp/mount-control.json',65536)
                    write_once(work/(name+'-result.json'),raw);observed=json.loads(raw)
                    require(process.returncode==0,'DIAGNOSTICS_CONTROLS_PROCESS_FAILED')
                finally:
                    stopped=provider.terminate(sandbox.object_id)
                    write_once(work/(name+'-stopped.json'),encoded(stopped))
                result['cases'][name]={'provider_id':sandbox.object_id,'terminated':stopped['terminated'],'mounts':mounts,'result':observed}
                # Refuse immediately on a bad positive control, before any further case.
                if name=='read_only':require(observed['status']=='PASS','DIAGNOSTICS_NATIVE_READONLY_CONTROL_FAILED')
                else:require(observed['status']=='REJECTED_WRITABLE' and observed['reason']=='DIAGNOSTICS_WRITE_WAS_ALLOWED',
                    'DIAGNOSTICS_NATIVE_WRITABLE_CONTROL_FAILED')
    validate_controls(result,binding)
    write_once(work/'native-mount-controls.json',encoded(result))
    return result


def reuse_controls(provider,binding,package):
    from orchestrator.manual_host_guard import trusted
    from orchestrator.manual_driver import write_once
    from orchestrator.manual_executor import read
    from orchestrator import private_records as pr
    parent_binding(binding)
    work=Path(package).parent/'modal-executions'/job(binding)
    require(read(pr.check(work/'create-intent.json'))['binding_sha256']==sha(encoded(binding)),
        'DIAGNOSTICS_CONTROLS_ADMISSION')
    raw=trusted(RECORD/'native-mount-controls.json').read_bytes()
    require(sha(raw)==CONTROLS_SHA,'DIAGNOSTICS_REPAIR_ORIGINAL_CONTROLS')
    value=validate_controls(json.loads(raw),binding)
    # Same control source and exact native results, no new Volume/provider call.
    write_once(work/'native-mount-controls.json',raw)
    write_once(work/'reused-native-controls.json',encoded({'parent':PARENT,'sha256':CONTROLS_SHA,
        'controls_sha256':value['controls_sha256'],'additional_provider_calls':0}))
    return value


def provider_factory(base):
    """Reuse original SDK fix, credential loader, asset checks and result transport."""
    from orchestrator import private_records as pr
    from orchestrator.manual_executor import read
    class Provider(base):
        def preflight(self,config,binding,prepared):
            parent_binding(binding)
            require('mechanical_retry' in binding,'DIAGNOSTICS_RETRY_ONLY')
            return super().preflight(config,binding,prepared)

        def create(self,config,binding,package):
            reuse_controls(self,binding,package)
            return super().create(config,binding,package)

        def launch(self,provider_id,binding):
            parent_binding(binding);sandbox=self._sandbox(provider_id)
            work=Path('/var/lib/research-system-manual-sprint10/releases/research-manual-sprint10-timeout-continuation-8e042339/lane/modal-executions')/job(binding)
            validate_controls(read(pr.check(work/'native-mount-controls.json')),binding)
            source=program();require(sha(source.encode())==binding['mechanical_retry']['worker_sha256'],'DIAGNOSTICS_RETRY_WORKER_SOURCE')
            interpreter=self.config['diagnostics_assets']['environment'].get('interpreter','/usr/bin/python3')
            require(interpreter in {'/usr/bin/python3','/opt/research-scientific-python/bin/python'},'DIAGNOSTICS_FIXED_INTERPRETER')
            sandbox.exec(interpreter,'-s','-B','-c',source,'--binding',sha(encoded(binding)),
                '--retry',encoded(binding['mechanical_retry']).decode(),timeout=binding['resources']['timeout_seconds'],
                workdir='/tmp',stdout=self.modal.stream_type.StreamType.DEVNULL,stderr=self.modal.stream_type.StreamType.DEVNULL)
            return {'provider_id':provider_id,'submitted':True,'binding_sha256':sha(encoded(binding)),
                    'mechanical_retry_parent':PARENT,'worker_sha256':binding['mechanical_retry']['worker_sha256']}

        def collect(self,provider_id,binding,destination):
            parent_binding(binding);sandbox=self._sandbox(provider_id)
            proof=validate_mount_proof(json.loads(self._read(sandbox,'/tmp/mount-verification.json',65536)),binding)
            work=Path('/var/lib/research-system-manual-sprint10/releases/research-manual-sprint10-timeout-continuation-8e042339/lane/modal-executions')/job(binding)
            native=validate_controls(read(pr.check(work/'native-mount-controls.json')),binding)
            result=super().collect(provider_id,binding,destination)
            return {**result,'mount_verification':proof,'native_mount_controls':native}
    return Provider
