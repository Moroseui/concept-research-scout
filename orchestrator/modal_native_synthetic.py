"""One fixed accepted author21 diagnostic synthetic rehearsal, using the original item4 owner."""
import base64
import gzip
from pathlib import Path
from orchestrator.manual_executor import digest
from orchestrator.modal_executor import canonical
from orchestrator.modal_item4_policy import quote
from orchestrator.review_contract import strict_json
from tools import item4_native_worker as worker

PURPOSE='M4_ITEM4_DIAGNOSTIC_NATIVE'
OPERATION='item4-author21-progress-native-v1'
SCHEMA='item4-native-synthetic-operation/v1'
from orchestrator.experiment_context import ITEM4_RUN as RUN
RESOURCES={'gpu':None,'cpu':2,'memory_mib':8192,'timeout_seconds':900}
SELECTION=Path(__file__).resolve().parents[1]/'docs/ITEM4_DIAGNOSTIC_NATIVE_SELECTION_PRIVATE.json'
SELECTION_SHA='e32c304ff526148601137a6eb0c600970e82945b6a6aca2b457659b04fae4e5b'
BUNDLE=Path('/var/lib/research-system-manual-sprint10-deployment/item4-progress-scope-repair-20261010/code-bundle.json')


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
