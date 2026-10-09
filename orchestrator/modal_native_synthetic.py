"""One fixed accepted-author synthetic rehearsal, using the original item4 owner."""
import base64
import gzip
from pathlib import Path
from orchestrator.manual_executor import digest
from orchestrator.modal_executor import canonical
from orchestrator.modal_item4_policy import quote
from orchestrator.review_contract import strict_json
from tools import item4_native_worker as worker

PURPOSE='M4_ITEM4_NATIVE_SYNTHETIC'
OPERATION='item4-author11-native-synthetic-v1'
SCHEMA='item4-native-synthetic-operation/v1'
from orchestrator.experiment_context import ITEM4_RUN as RUN
RESOURCES={'gpu':None,'cpu':2,'memory_mib':8192,'timeout_seconds':900}
SELECTION=Path(__file__).resolve().parents[1]/'docs/ITEM4_NATIVE_SYNTHETIC_SELECTION_20261008.json'
SELECTION_SHA='edfffd0f311cfa8fdae6b28c93bdc00c60d4ea1b3b2c2320795cb685af693b23'
BUNDLE=Path('/var/lib/research-system-manual-sprint10-deployment/item4-native-cpu-rehearsal-20261008/code-bundle.json')


def selected(value=None):
    raw=SELECTION.read_bytes()
    if digest(raw)!=SELECTION_SHA:raise ValueError('NATIVE_SELECTION_CHANGED')
    expected=strict_json(raw)
    if value is not None and value!=expected:raise ValueError('NATIVE_SELECTION_BINDING')
    return expected


def envelope(rates):
    return {'resources':dict(RESOURCES),'cost':quote(RESOURCES,rates,1000000)}


def worker_sha256():return digest(Path(worker.__file__).read_bytes())


def bundle():
    from orchestrator.manual_host_guard import trusted
    raw=trusted(BUNDLE).read_bytes();v=selected()
    if len(raw)!=v['code_bundle_bytes'] or digest(raw)!=v['code_bundle_sha256']:
        raise ValueError('NATIVE_CODE_BUNDLE_CHANGED')
    return raw


STDIN_BOOTSTRAP="""import sys
_payload=sys.stdin.buffer.read(120001)
if len(_payload)>120000:raise ValueError('NATIVE_STDIN_BOUND')
sys.argv=[sys.argv[0],_payload.decode('ascii'),*sys.argv[1:]]
"""


def stdin_payload():
    encoded=base64.b64encode(gzip.compress(bundle(),mtime=0))
    if len(encoded)>120000:raise ValueError('NATIVE_STDIN_BOUND')
    return encoded


def arguments(binding):
    value=selected(binding['native_synthetic'])
    stdin_payload()  # Authenticate and bound the actual source before admission.
    args=(value['environment']['python_executable'],'-I','-B','-c',
        STDIN_BOOTSTRAP+Path(worker.__file__).read_text(),canonical(value).decode(),digest(canonical(binding)))
    if sum(len(a.encode()) for a in args)>65536:raise ValueError('NATIVE_SDK_ARGUMENT_BOUND')
    return args


def send_stdin(sb,binding,root):
    from orchestrator import private_records as pr
    from orchestrator.modal_environment_provider import record
    root=Path(root);payload=stdin_payload()
    handle=strict_json(pr.check(root/'sandbox.json').read_bytes())
    if handle['provider_id']!=sb.object_id or handle['binding_sha256']!=digest(canonical(binding)):
        raise ValueError('NATIVE_STDIN_HANDLE')
    intent={'binding_sha256':digest(canonical(binding)),'provider_id':sb.object_id,
        'bytes':len(payload),'sha256':digest(payload),'eof':True}
    # Exclusive even for identical bytes: an interrupted send is never replayed.
    with pr.open_file(root/'stdin-intent.json','xb') as out:out.write(canonical(intent))
    sb.stdin.write(payload);sb.stdin.write_eof();sb.stdin.drain()
    record(root,'stdin-sent',intent)


def verify_stdin(binding,root):
    from orchestrator import private_records as pr
    root=Path(root);payload=stdin_payload()
    h=strict_json(pr.check(root/'sandbox.json').read_bytes())
    expected={'binding_sha256':digest(canonical(binding)),'provider_id':h['provider_id'],
        'bytes':len(payload),'sha256':digest(payload),'eof':True}
    for name in ('stdin-intent.json','stdin-sent.json'):
        if strict_json(pr.check(root/name).read_bytes())!=expected:raise ValueError('NATIVE_STDIN_RECEIPT')
    return expected


REFUSAL=SELECTION.with_name('ITEM4_NATIVE_PRECREATE_REFUSAL_20261008.json')
REFUSAL_SHA='4e106e3f7d09e284efaca93ff35de9d3fdc8a67d53f6411de27cc8a1938601b9'


def precreate_snapshot(binding,root):
    from orchestrator import private_records as pr
    raw=REFUSAL.read_bytes()
    if digest(raw)!=REFUSAL_SHA:raise ValueError('NATIVE_REFUSAL_PROOF_CHANGED')
    proof=strict_json(raw);root=Path(root);pr.check_tree(root)
    if digest(canonical(binding))!=proof['binding_sha256']:raise ValueError('NATIVE_RECOVERY_EXACT_RESERVATION')
    actual={p.name:digest(pr.check(p).read_bytes()) for p in root.iterdir() if p.is_file()}
    if actual!=proof['provider_files'] or any(not p.is_file() for p in root.iterdir()):
        raise ValueError('NATIVE_RECOVERY_ORIGINALS_CHANGED_OR_USED')
    intent=strict_json(pr.check(root/'intent.json').read_bytes())
    original=strict_json(pr.check(root/'sandbox-intent.json').read_bytes())
    old_args=original['args']
    expected=selected(binding['native_synthetic'])
    # This original payload exactly identifies the client-side refusal. No
    # transport timeout or unknown provider outcome can qualify by size alone.
    import io
    encoded=old_args[5]
    if not isinstance(encoded,str) or len(encoded)>120000:raise ValueError('NATIVE_PRECREATE_PAYLOAD_BOUND')
    with gzip.GzipFile(fileobj=io.BytesIO(base64.b64decode(encoded,validate=True))) as stream:
        original_code=stream.read(worker.MAX_BUNDLE+1)
    if original_code!=bundle():raise ValueError('NATIVE_PRECREATE_SOURCE_CHANGED')
    # Original record hashes above pin every transport byte. Compare decoded
    # source too: Python 3.12/3.13 gzip OS header bytes can legitimately differ.
    old=(expected['environment']['python_executable'],'-I','-B','-c',Path(worker.__file__).read_text(),
        encoded,canonical(expected).decode(),digest(canonical(binding)))
    if (intent['binding']!=binding or list(old)!=old_args or sum(len(a) for a in old_args)!=96135
        or original['resources']!=RESOURCES or original['block_network'] is not True
        or original['mounts']!={} or original['secrets']!=[] or original['environment']!={}
        or original['oidc'] is not False):raise ValueError('NATIVE_PRECREATE_REFUSAL_BINDING')
    return proof,old_args


def recover_precreate(provider,accounts,binding,root,*,now=None):
    """One reviewed continuation of this proven pre-RPC refusal, same charge."""
    from datetime import datetime,timezone
    import importlib
    from orchestrator import private_records as pr,modal_environment_budget as budget
    from orchestrator.modal_environment_provider import require_reserved,record
    from orchestrator.manual_host_guard import trusted
    ident=require_reserved(accounts,binding);root=Path(root)
    proof,old_args=precreate_snapshot(binding,root)
    if accounts.db.execute("SELECT 1 FROM autonomy_calls WHERE status='RUNNING'").fetchone():
        raise ValueError('NATIVE_RECOVERY_RUNNING_MODEL')
    sdk=trusted(Path(provider.config['sdk_package'])/'modal/sandbox.py')
    if digest(sdk.read_bytes())!=proof['sandbox_py_sha256']:raise ValueError('NATIVE_RECOVERY_SDK_CHANGED')
    validator=importlib.import_module('modal.sandbox')._validate_exec_args
    try:validator(old_args)
    except provider.modal.exception.InvalidError as error:
        if str(error)!='Total length of CMD arguments cannot exceed 65536 bytes (ARG_MAX). Got 96135 bytes.':
            raise ValueError('NATIVE_RECOVERY_DIFFERENT_FAILURE') from error
    else:raise ValueError('NATIVE_RECOVERY_NOT_PRECREATE_REFUSAL')
    args=arguments(binding);validator(args)
    view=provider.billing_snapshot()
    if budget.reserve(accounts,ident,RUN,binding,billing_snapshot=view,now=now) is not False:
        raise ValueError('NATIVE_RECOVERY_NEW_RESERVATION_REFUSED')
    if provider.config['workspace']!='moroseui':raise ValueError('NATIVE_RECOVERY_WORKSPACE')
    provider.client.hello()
    ws=provider.modal.Workspace.from_context(client=provider.client);ws.hydrate(client=provider.client)
    if ws.name!='moroseui':raise ValueError('NATIVE_RECOVERY_WORKSPACE')
    app_record=strict_json(pr.check(root/'app.json').read_bytes())
    if app_record['app_id']!=proof['app_id']:raise ValueError('NATIVE_RECOVERY_APP_CHANGED')
    app=provider.modal.App.lookup(app_record['name'],create_if_missing=False,client=provider.client)
    if app.app_id!=proof['app_id']:raise ValueError('NATIVE_RECOVERY_APP_CHANGED')
    try:provider.modal.Sandbox.from_name(app_record['name'],'environment-'+ident[:32],client=provider.client)
    except provider.modal.exception.NotFoundError:pass
    else:raise ValueError('NATIVE_RECOVERY_SANDBOX_EXISTS')
    image=provider.modal.Image.from_id(binding['image_id'],client=provider.client);image.build(app)
    if image.object_id!=proof['image_id']:raise ValueError('NATIVE_RECOVERY_IMAGE_CHANGED')
    # Never overwrite any original record. This exclusive intent permits just
    # one create; a crash before a returned handle stops for reconciliation.
    with pr.open_file(root/'stdin-recovery-intent.json','xb') as out:
        out.write(canonical({'binding_sha256':ident,'refusal_proof_sha256':REFUSAL_SHA,
            'args':args,'billing':view,'resources':RESOURCES,'at':datetime.now(timezone.utc).isoformat(),
            'original_charge_retained':True,'new_reservation':False,'named_sandbox_lookup':'NOT_FOUND'}))
    sb=provider.modal.Sandbox.create(*args,app=app,name='environment-'+ident[:32],image=image,
        gpu=None,cpu=(2,2),memory=(8192,8192),timeout=900,block_network=True,
        include_oidc_identity_token=False,secrets=[],env={},encrypted_ports=[],h2_ports=[],unencrypted_ports=[],
        volumes={},client=provider.client)
    from orchestrator.modal_environment_provider import text
    if not text(sb.object_id,128,pattern=r'sb-[A-Za-z0-9_-]+'):raise ValueError('NATIVE_RECOVERY_PROVIDER_ID')
    handle={'provider_id':sb.object_id,'app_id':app.app_id,'image_id':image.object_id,
        'binding_sha256':ident,'worker_sha256':worker_sha256(),'launched_at':datetime.now(timezone.utc).isoformat()}
    record(root,'sandbox',handle);send_stdin(sb,binding,root)
    return handle


def validate_result(raw,binding):
    if not isinstance(raw,bytes) or len(raw)>worker.MAX_RESULT+1:raise ValueError('NATIVE_RESULT_BOUND')
    v=strict_json(raw);s=selected(binding['native_synthetic'])
    fields={'schema','status','operation_sha256','selection_sha256','module_sha256','code_bundle_sha256',
        'image_id','author_call_id','package_unchanged','observed_environment','native','console','console_sha256','console_truncated',
        'failure','patient_data','network_permission','gpu','scientific_approval','durability_scope'}
    if (not isinstance(v,dict) or set(v)!=fields or v['schema']!='item4-native-rehearsal-result/v1'
        or v['status']!='PASS' or v['operation_sha256']!=digest(canonical(binding))
        or v['selection_sha256']!=digest(canonical(s))
        or any(v[k]!=s[k] for k in ('module_sha256','code_bundle_sha256','image_id','author_call_id'))
        or v['image_id']!=binding['image_id'] or v['package_unchanged'] is not True
        or v['observed_environment']!=s['environment']['expected']
        or any(v[k] is not False for k in ('console_truncated','patient_data','network_permission','gpu','scientific_approval'))
        or v['failure'] is not None or not isinstance(v['console'],str)
        or len(v['console'].encode())>worker.MAX_LOG or digest(v['console'].encode())!=v['console_sha256']
        or v['durability_scope']!=worker.DURABILITY_SCOPE):raise ValueError('NATIVE_RESULT_BINDING')
    worker.validate_authored_result(v['native'],s)
    return v
