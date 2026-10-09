"""Synthetic native guard-to-worker integration, no provider or patient bytes.

The cohort pin and environment proof are labelled synthetic fixtures. Actual
initializer, input guard, private writer, package verifier and worker run intact.
"""
import json
import pytest
from pathlib import Path
from orchestrator import private_records as pr
from orchestrator.manual_executor import inventory
from test_experiment_preprocessing import prepared
from test_modal_volume_path import native


@pytest.mark.parametrize("provider_mode", [0o400, 0o666])
def test_empty_provider_root_through_real_preprocessing_worker(native,prepared,tmp_path,provider_mode):
    _,volume,run=native
    _,package,inputs,progress,seal=prepared
    binding,pin=seal()
    proof=(progress/'environment-verification'/pin/'environment.json').read_bytes()
    files=json.loads((package/'input-inventory.json').read_bytes())
    for path in package.rglob('*'):
        if path.is_file():path.chmod(provider_mode)
    before=inventory(package)
    volume.chmod(0o755)
    source=Path(__file__).resolve().parents[1]
    wrapper=tmp_path/'worker-fixture.py'
    pr.write_text(wrapper,"import sys\nsys.path.insert(0,'/reviewed')\n"
        "from orchestrator import experiment_preprocessing as p\n"
        "p.COHORT="+repr(binding['preprocessing']['cohort_sha256'])+"\n"
        "import run\nr=run.execute('/reviewed','/inputs','/__modal/volumes/vo-Synthetic',"+repr(pin)+")\n"
        "assert r['status']=='VALIDATED' and r['files']==300 and r['steps']==100\n"
        "assert 'modal' not in sys.modules and 'orchestrator.manual_driver' not in sys.modules\n")
    script="""import sys,os
from pathlib import Path
sys.path.insert(0,'/reviewed')
from orchestrator import private_records as pr
from orchestrator.modal_input_guard import execute
namespace={}
exec(compile(Path('/initializer.py').read_bytes(),'/initializer.py','exec'),namespace)
root=namespace['bound_root']('/volume','vo-Synthetic')
namespace['initialize_empty_progress'](root,'vo-Synthetic')
assert root.stat().st_mode & 0o777 == 0o700
"""
    # A labelled synthetic environment proof, not a provider dependency claim.
    script+="pr.write_bytes(root/'environment-verification'/"+repr(pin)+"/'environment.json',"+repr(proof)+")\n"
    payload={'binding_sha256':pin,'guard_sha256':'b'*64,
             'preprocessing_sha256':binding['preprocessing']['input_contract_sha256'],'files':files}
    script+="execute('/inputs',root,'/worker-fixture.py',"+repr(payload)+")\n"
    result=run(script,extra=['--tmpfs','/tmp','--ro-bind',str(package),'/reviewed',
        '--ro-bind',str(inputs),'/inputs','--ro-bind',str(wrapper),'/worker-fixture.py',
        '--ro-bind',str(source/'orchestrator/modal_volume_path.py'),'/initializer.py'])
    assert result.returncode==0,result.stderr
    assert json.loads((volume/'input-verification'/(pin+'.json')).read_bytes())['status']=='VERIFIED'
    assert json.loads((volume/'preprocessing'/pin/'result.json').read_bytes())['status']=='VALIDATED'
    assert inventory(package)==before
    pr.check_tree(volume)
