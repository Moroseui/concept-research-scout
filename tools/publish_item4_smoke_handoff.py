from pathlib import Path
import os,sys,json,importlib.util,hashlib
assert os.getuid()==0
os.umask(0o077)
os.environ['RESEARCH_MANUAL_RUNTIME_CONFIG']='/etc/research-system-manual-sprint10/releases/research-manual-sprint10-timeout-continuation-8e042339/runtime.json'
sys.path.insert(0,'/opt/research-system/manual-sprint10/research-manual-sprint10-timeout-continuation-8e042339')
from orchestrator.manual_host_guard import trusted
import orchestrator
# Use the existing root-safe installed verification and configuration-only
# interfaces. Do not call service-owner load, open a ledger, or initialize SDK.
def module(name,path):
 s=importlib.util.spec_from_file_location(name,trusted(path));m=importlib.util.module_from_spec(s);sys.modules[name]=m;s.loader.exec_module(m);return m
root=Path('/opt/research-system/manual-repair-helpers/item4-partition-delivery-20261009')
gate=module('orchestrator.item4_validation_admission',root/'orchestrator/item4_validation_admission.py');orchestrator.item4_validation_admission=gate
assert gate.authority()=='5dab94cbfd162c837f42f4e87debe9ead36a2833e8cb2eddb5fd78371e69636d'
p=Path('/opt/research-system/manual-repair-helpers/item4-author7-and-image-recovery-20261008/tools/item4_scientific_revision_component.py')
c=module('_root_selected_runtime',p);v,b,e=c.verified()
assert v['source']=='eb835b81d019cc8088a53a246f45b790dbfffa4c' and v['review_sha256']=='a2b2da904ba4974850e7b0455921692b473567bde43605207535bbb18551f479'
c.connect_runtime()
from orchestrator import modal_executor
fresh=module('_root_validation_executor',root/'orchestrator/modal_executor.py')
assert not fresh.verify_package.__code__.co_freevars and not modal_executor.verify_package.__code__.co_freevars
modal_executor.verify_package.__code__=fresh.verify_package.__code__
from orchestrator import experiment_provisioning as provisioning
path=Path('/var/lib/research-system-manual-sprint10/releases/research-manual-sprint10-timeout-continuation-8e042339/item4/lane/item4-smoke-connection-20261009/prepared/preparation.json')
raw=path.read_bytes();expected=sys.argv[1];assert hashlib.sha256(raw).hexdigest()==expected
# Select the same already-installed, independently approved worker as the owner.
# The original publisher omitted this connection; its unchanged hash check refused.
staging_path=Path('/opt/research-system/manual-repair-helpers/item4-private-package-staging-20261009/tools/item4_private_staging_runtime.py')
assert hashlib.sha256(trusted(staging_path).read_bytes()).hexdigest()=='54773c6656d2ee63b703aeefd9a55c1f2083494cc12b5dd256d9e6a26bda9b72'
staging=module('_root_installed_staging',staging_path)
assert staging.authority()['report_sha256']=='69369d365a4ff9dae5e85cc464e8bbd3758dace82f1e1c601124536cf3256a92'
# Load the already-installed native volume-path selection used by preparation.
volume_route_path=Path('/opt/research-system/manual-repair-helpers/item4-preprocessing-root-repair-20261009/tools/item4_preprocessing_fresh_runtime.py')
assert hashlib.sha256(trusted(volume_route_path).read_bytes()).hexdigest()=='9f8f192949af976f55a0eff8d2a0afe6e7300561024bfaadfa6e3913913155d4'
volume_route=module('_root_installed_volume_route',volume_route_path)
assert volume_route.authority()['report_sha256']=='860f9f3193c005944116508220aa32584f3b79edd5b4c22cd1cd833258ef59ec'
volume=module('orchestrator.modal_volume_path',volume_route.ROOT/'orchestrator/modal_volume_path.py')
orchestrator.modal_volume_path=volume
from orchestrator import experiment_modal_package as bridge
support_root=bridge.WORKER.parent.parent
contract_path=Path('/opt/research-system/manual-repair-helpers/item4-benchmark-timer-format-20261009/docs/ITEM4_BENCHMARK_HANDOFF_PRIVATE.json')
contract_raw=trusted(contract_path).read_bytes()
assert hashlib.sha256(contract_raw).hexdigest()=='62c241b1e75372635f7a662245ad41437ee09a417b72de00cdd3496d59f07da4'
contract=json.loads(contract_raw)
worker=staging.ROOT/'orchestrator/experiment_worker.py'
assert hashlib.sha256(trusted(worker).read_bytes()).hexdigest()==contract['code_hashes']['run.py']
expected_support={name:contract['code_hashes'][name] for name in bridge.SUPPORT_FILES}
def support_files():
    bodies={name:trusted(support_root/name).read_bytes() for name in bridge.SUPPORT_FILES}
    assert {name:hashlib.sha256(raw).hexdigest() for name,raw in bodies.items()}==expected_support
    return bodies
support_files() # Verify the original support selection before changing the module reference.
bridge.WORKER=worker
bridge.support_files=support_files
# No validator, source bytes, package bytes, input, budget, SDK or credential changes.
# Retain the full existing publisher, including its root checks and final replay.
record=provisioning.inspect(path)
assert [row['binding']['experiment']['fit_id'] for row in record['selection']['jobs']]==['smoke-A1_repeat','smoke-A1_repeat2']
if len(sys.argv)==3 and sys.argv[2]=='inspect':
    print(json.dumps({'status':'INSPECTED_WITH_ORIGINAL_GUARDS','jobs':len(record['selection']['jobs']),
        'preparation_sha256':expected,'provider_calls':0,'ledger_calls':0,'production_writes':0}))
else:
    assert len(sys.argv)==2
    sys.path.insert(0,'/opt/research-system/autonomy-review/d08b91bdc1d0')
    own=module('_root_smoke_release',Path('/opt/research-system/manual-repair-helpers/item4-deliberate-smoke-stop-20261009/tools/item4_deliberate_smoke_runtime.py'))
    own.authority() # Genuine installed implementation approval before publication.
    assert Path(__file__).resolve()==own.ROOT/'tools/publish_item4_smoke_handoff.py'
    print(json.dumps(provisioning.publish(path,expected_sha256=expected),sort_keys=True))
