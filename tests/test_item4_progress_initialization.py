"""Real isolated mount-root initialization followed by the unchanged input guard."""
import json
from pathlib import Path
import pytest
from orchestrator import private_records as pr
from test_modal_volume_path import native, PREAMBLE

INIT = PREAMBLE + "from orchestrator.modal_volume_path import initialize_empty_progress\nroot=bound_root('/volume','vo-Synthetic')\n"


def test_provider_default_root_becomes_private_before_unchanged_guard(native):
    package,volume,run=native
    volume.chmod(0o755)
    source=Path(__file__).resolve().parents[1]
    pr.copyfile(source/'orchestrator/modal_input_guard.py',package/'orchestrator/modal_input_guard.py')
    pr.mkdir(package/'input')
    pr.write_bytes(package/'input/synthetic.bin',b'synthetic input only')
    pr.write_text(package/'science.py',"from pathlib import Path; Path('/__modal/volumes/vo-Synthetic/marker.txt').write_text('executed')")
    script=INIT+"""
import hashlib
from orchestrator.modal_input_guard import execute
initialize_empty_progress(root,'vo-Synthetic')
assert root.stat().st_mode & 0o777 == 0o700
raw=Path('/reviewed/input/synthetic.bin').read_bytes()
payload={'binding_sha256':'a'*64,'guard_sha256':'b'*64,'preprocessing_sha256':'c'*64,
         'files':{'synthetic.bin':{'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()}}}
execute('/reviewed/input',root,'/reviewed/science.py',payload)
"""
    observed=run(script)
    assert observed.returncode==0,observed.stderr
    assert (volume/'marker.txt').read_text()=='executed'
    assert json.loads((volume/'input-verification'/('a'*64+'.json')).read_text())['status']=='VERIFIED'
    pr.check_tree(volume)


@pytest.mark.parametrize('fault',['nonempty','world-writable','wrong-identity','read-only'])
def test_unsafe_existing_or_unwritable_roots_refuse_without_repair(native,fault):
    package,volume,run=native
    volume.chmod(0o777 if fault=='world-writable' else 0o755)
    if fault=='nonempty':pr.write_bytes(volume/'preserved.txt',b'original')
    before=volume.stat().st_mode
    ident='vo-Other' if fault=='wrong-identity' else 'vo-Synthetic'
    extra=['--ro-bind',str(volume),'/__modal/volumes/vo-Synthetic'] if fault=='read-only' else []
    script=INIT+"try:\n initialize_empty_progress(root,"+repr(ident)+")\nexcept (ValueError,OSError): print('REFUSED')\nelse: raise AssertionError('unsafe root accepted')\n"
    result=run(script,extra=extra)
    assert result.returncode==0,result.stderr
    assert result.stdout.strip()=='REFUSED'
    assert volume.stat().st_mode==before
    if fault=='nonempty':assert (volume/'preserved.txt').read_bytes()==b'original'


def test_existing_private_root_does_not_chmod_or_hide_unsafe_child(native):
    package,volume,run=native
    pr.write_bytes(volume/'preserved.txt',b'original');(volume/'preserved.txt').chmod(0o644)
    script=INIT+"""
def forbidden(*args):raise AssertionError('existing root chmod')
os.fchmod=forbidden
initialize_empty_progress(root,'vo-Synthetic')
try:pr.check(root/'preserved.txt')
except ValueError as error:assert str(error)=='PRIVATE_RECORD_PERMISSIONS'
else:raise AssertionError('unsafe child accepted')
print('PASS')
"""
    result=run(script)
    assert result.returncode==0,result.stderr
    assert result.stdout.strip()=='PASS'
    assert (volume/'preserved.txt').stat().st_mode & 0o777==0o644


def test_new_entry_during_initialization_fails_closed(native):
    package,volume,run=native;volume.chmod(0o755)
    script=INIT+"""
original=os.fchmod
def changed(fd,mode):
 original(fd,mode)
 (root/'unexpected.txt').write_text('synthetic race')
os.fchmod=changed
try:initialize_empty_progress(root,'vo-Synthetic')
except ValueError as error:assert str(error)=='FIT_PROGRESS_INITIALIZATION_CHANGED'
else:raise AssertionError('changed root accepted')
print('REFUSED')
"""
    result=run(script)
    assert result.returncode==0,result.stderr
    assert result.stdout.strip()=='REFUSED'
