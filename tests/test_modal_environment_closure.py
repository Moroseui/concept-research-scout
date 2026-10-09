"""Actual offline pip/import/help execution using deliberately synthetic wheels.

No genuine nnUNet environment, provider, network, patient data or model call.
The same fixed closure program runs inside a network-unshared native sandbox.
"""
import base64
import copy
import csv
import io
import json
import os
from pathlib import Path
import shutil
import subprocess
import zipfile
import pytest
from orchestrator import modal_environment_closure as closure
from orchestrator import modal_scientific_environment as environment


def wheel(distribution,module,version,defect=None):
    name=distribution.replace('-','_');info=name+'-'+version+'.dist-info'
    marker="from pathlib import Path\nPath('/work/imported-"+module+"').write_text('synthetic import executed')\n"
    content=marker
    if module=='torch':
        content+="from types import SimpleNamespace\nversion=SimpleNamespace(cuda="+("None" if defect=='cuda' else "'12.8'")+")\n"
    files={module+'/__init__.py':content.encode(),info+'/METADATA':('Metadata-Version: 2.1\nName: '+distribution+'\nVersion: '+version+'\n').encode(),
           info+'/WHEEL':b'Wheel-Version: 1.0\nGenerator: deterministic-synthetic-fixture\nRoot-Is-Purelib: true\nTag: py3-none-any\n'}
    if module=='nnunetv2':
        parents=['training','training/nnUNetTrainer','training/nnUNetTrainer/variants','training/nnUNetTrainer/variants/training_length','imageio']
        for parent in parents:files[module+'/'+parent+'/__init__.py']=b''
        params='self,plans,configuration,fold,dataset_json,device=None' if defect!='trainer' else 'self,plans'
        trainers=''.join('class '+name+':\n def __init__('+params+'): pass\n' for name in closure.TRAINERS)
        files[module+'/training/nnUNetTrainer/variants/training_length/nnUNetTrainer_Xepochs.py']=trainers.encode()
        files[module+'/imageio/simpleitk_reader_writer.py']=b'class SimpleITKIO:\n def read_images(self): pass\n def read_seg(self): pass\n'
        helpcode=("def main():\n import json,sys\n from pathlib import Path\n name=Path(sys.argv[0]).name\n Path('/work/console-'+name).write_text(json.dumps(sys.argv[1:]))\n"
                  +(" raise SystemExit(2)\n" if defect=='help' else " assert sys.argv[1:]==['--help']\n print('usage: '+name+' [synthetic --help]')\n"))
        files[module+'/entry.py']=helpcode.encode()
        files[info+'/entry_points.txt']=('[console_scripts]\n'+''.join(name+' = nnunetv2.entry:main\n' for name in closure.CONSOLES)).encode()
    if defect=='import' and module=='nibabel':files[module+'/__init__.py']=b'raise ImportError("synthetic unavailable import")\n'
    records=io.StringIO();writer=csv.writer(records)
    for filename,data in files.items():writer.writerow([filename,'sha256='+base64.urlsafe_b64encode(__import__('hashlib').sha256(data).digest()).rstrip(b'=').decode(),len(data)])
    writer.writerow([info+'/RECORD','','']);files[info+'/RECORD']=records.getvalue().encode()
    buf=io.BytesIO()
    with zipfile.ZipFile(buf,'w') as archive:
        for filename,data in files.items():archive.writestr(zipfile.ZipInfo(filename,date_time=(2026,1,1,0,0,0)),data)
    return name+'-'+version+'-py3-none-any.whl',buf.getvalue()


def fixture(root,defect=None):
    root.mkdir(mode=0o700);wheels=root/'wheels';wheels.mkdir(mode=0o700)
    code=root/'code/orchestrator';code.mkdir(parents=True,mode=0o700)
    (code/'__init__.py').write_bytes(b'')
    for module in (closure,environment):shutil.copyfile(module.__file__,code/Path(module.__file__).name)
    native=Path('/opt/research-system-cpu-tools/m2-python312-xgb341-v2')
    python=str(native/'bin/python') if native.is_dir() else '/usr/bin/python3'
    selected={'schema':closure.SCHEMA,'python_executable':python,'packages':{},'wheels':{}}
    for distribution,module in closure.IMPORTS.items():
        version='2.8.1' if distribution=='nnunetv2' else '2.11.0' if distribution=='torch' else '1.0'
        filename,raw=wheel(distribution,module,version,defect)
        (wheels/filename).write_bytes(raw)
        selected['packages'][distribution]=version;selected['wheels'][filename]={'bytes':len(raw),'sha256':closure.digest(raw)}
    (root/'selection.json').write_bytes(closure.encoded(selected))
    return selected


def native(root,selected,*,script=None,binding='a'*64):
    bwrap=shutil.which('bwrap')
    if bwrap is None:raise AssertionError('Native sandbox prerequisite missing; do not skip closure proof')
    argv=[bwrap,'--unshare-all','--die-with-parent','--new-session','--ro-bind','/usr','/usr']
    for name in ('/lib','/lib64','/bin'):
        p=Path(name)
        if p.is_symlink():argv+=['--symlink',os.readlink(p),name]
        elif p.exists():argv+=['--ro-bind',name,name]
    python=selected['python_executable']
    if python.startswith('/opt/'):
        package=str(Path(python).parent.parent);argv+=['--ro-bind',package,package]
    argv+=['--proc','/proc','--dev','/dev','--tmpfs','/tmp','--bind',str(root),'/work',
           '--ro-bind',str(root/'code'),'/code','--chdir','/work',
           '--setenv','HOME','/tmp','--setenv','PATH','/usr/bin:/bin','--setenv','PYTHONPATH','/code',
           '--unsetenv','PYTHONHOME',python,'-B','-s']
    if script is None:argv+=['-m','orchestrator.modal_environment_closure','--selection','/work/selection.json',
            '--wheels','/work/wheels','--output','/work/proof','--binding',binding]
    else:argv+=['-c',script]
    return subprocess.run(argv,capture_output=True,timeout=300)


@pytest.fixture(scope='module')
def native_success(tmp_path_factory):
    root=tmp_path_factory.mktemp('closure-parent')/'native';selected=fixture(root)
    result=native(root,selected)
    assert result.returncode==0,(result.stdout,result.stderr)
    value=closure.validate_result((root/'proof/result.json').read_bytes(),selected,'a'*64)
    return root,selected,value


def test_real_install_fixed_imports_trainers_and_help_execute(native_success):
    root,selected,value=native_success
    assert 'expected' not in selected
    assert value['scientific_environment']['expected']['cuda']=='12.8'
    assert value['scientific_environment']['expected']['packages']==selected['packages']
    assert value['scientific_environment']['expected']['python'].startswith('3.')
    assert 'GCC' in value['scientific_environment']['expected']['python']
    assert value['gpu_verified'] is False and value['patient_computation'] is False
    for name in closure.IMPORTS.values():assert (root/('imported-'+name)).read_text()=='synthetic import executed'
    for name in closure.CONSOLES:
        assert json.loads((root/('console-'+name)).read_text())==['--help']
        for stream in ('stdout','stderr'):
            raw=(root/'proof'/(name+'.'+stream)).read_bytes()
            assert value['checks']['console_help'][name][stream]=={'bytes':len(raw),'sha256':closure.digest(raw)}
    assert 'Successfully installed' in (root/'proof/environment-install.log').read_text()


def test_produced_exact_spec_passes_unchanged_strict_consumer(native_success):
    root,selected,value=native_success
    script="""from pathlib import Path
import json
from orchestrator import modal_environment_closure as c,modal_scientific_environment as e
spec=json.loads(Path('/work/proof/result.json').read_text())['scientific_environment']
p=Path('/work/normal-consumer');p.mkdir(mode=0o700)
e.environment_prepare(spec,Path('/work/wheels'),p,'b'*64,c.verify_wheels)
"""
    result=native(root,selected,script=script)
    assert result.returncode==0,result.stderr
    proof=json.loads((root/'normal-consumer/environment.json').read_bytes())
    assert proof['actual']==value['scientific_environment']['expected'] and proof['offline'] is True


@pytest.mark.parametrize('defect,code',[('cuda','CLOSURE_OBSERVED_IDENTITY'),('trainer','CLOSURE_RESULT_CHECKS'),
    ('help','CLOSURE_CHECK_FAILED:nnUNetv2_plan_and_preprocess'),('import','CLOSURE_CHECK_FAILED:imports')])
def test_real_interface_failures_do_not_produce_qualifying_result(tmp_path,defect,code):
    root=tmp_path/'native';selected=fixture(root,defect);result=native(root,selected)
    assert result.returncode!=0 and code.encode() in result.stderr,result.stderr
    assert (root/'proof/environment-install.log').exists()
    assert not (root/'proof/result.json').exists()


def test_wheel_hash_and_duplicate_attempt_refuse(native_success,tmp_path):
    root,selected,value=native_success
    saved=(root/'proof/result.json').read_bytes();again=native(root,selected)
    assert again.returncode!=0 and b'CLOSURE_EXISTING_ATTEMPT_NO_RETRY' in again.stderr
    assert (root/'proof/result.json').read_bytes()==saved
    damaged=tmp_path/'damaged';current=fixture(damaged)
    filename=next(iter(current['wheels']));p=damaged/'wheels'/filename;p.write_bytes(p.read_bytes()+b'changed')
    result=native(damaged,current)
    assert result.returncode!=0 and b'CLOSURE_WHEEL_INVENTORY' in result.stderr
    assert not (damaged/'proof').exists()


@pytest.mark.parametrize('defect',['extra','schema','missing-package','nnunet-version','shell','alias','wheel-pin'])
def test_selection_refuses_arbitrary_or_unbound_inputs(tmp_path,defect):
    selected=fixture(tmp_path/'fixture')
    if defect=='extra':selected['command']=['arbitrary']
    elif defect=='schema':selected['schema']='other'
    elif defect=='missing-package':selected['packages'].pop('torch')
    elif defect=='nnunet-version':selected['packages']['nnunetv2']='2.7'
    elif defect=='shell':selected['python_executable']='/bin/sh'
    elif defect=='alias':selected['python_executable']='/opt/../bin/python'
    else:selected['wheels'][next(iter(selected['wheels']))]['sha256']='bad'
    with pytest.raises(ValueError):closure.selection(selected)


@pytest.mark.parametrize('defect',['binding','worker','consumer','selection','extra','cuda','packages','expected-hash',
    'imports','trainer','reader','help-exit','help-usage','help-hash','help-empty','duplicate','boolean'])
def test_strict_result_refusals(native_success,defect):
    _,selected,original=native_success;value=copy.deepcopy(original)
    if defect in {'binding','worker','consumer','selection'}:value[defect+'_sha256']='f'*64
    elif defect=='extra':value['verdict']='APPROVE'
    elif defect=='cuda':value['scientific_environment']['expected']['cuda']=None
    elif defect=='packages':value['scientific_environment']['expected']['packages']['torch']='0'
    elif defect=='expected-hash':value['environment_sha256']='f'*64
    elif defect=='imports':value['checks']['imports'].pop('torch')
    elif defect=='trainer':value['checks']['trainers'][closure.TRAINERS[0]]=['self']
    elif defect=='reader':value['checks']['reader']='other'
    elif defect.startswith('help-'):
        record=value['checks']['console_help'][closure.CONSOLES[0]]
        if defect=='help-exit':record['exit_code']=1
        elif defect=='help-usage':record['usage_seen']=False
        elif defect=='help-hash':record['stdout']['sha256']='bad'
        else:record['stdout']['bytes']=record['stderr']['bytes']=0
    elif defect=='boolean':value['gpu_verified']=0
    raw=closure.encoded(value)
    if defect=='duplicate':raw=raw.replace(b'"gpu_verified":false',b'"gpu_verified":false,"gpu_verified":false')
    with pytest.raises(ValueError):closure.validate_result(raw,selected,'a'*64)


@pytest.mark.parametrize('damage,code',[('python','SCIENTIFIC_ENVIRONMENT_INTERPRETER'),
    ('cuda','SCIENTIFIC_ENVIRONMENT_CHANGED'),('package','SCIENTIFIC_ENVIRONMENT_CHANGED')])
def test_normal_consumer_still_refuses_changed_generated_identity(native_success,damage,code):
    root,selected,value=native_success
    # Reuse the genuine synthetic-wheel producer output, then mutate just one
    # expected field. No install, observation or subprocess result is patched.
    script="""from pathlib import Path
import json
from orchestrator import modal_environment_closure as c,modal_scientific_environment as e
spec=json.loads(Path('/work/proof/result.json').read_text())['scientific_environment']
damage="""+repr(damage)+"""
if damage=='python':spec['expected']['python']='wrong native version'
elif damage=='cuda':spec['expected']['cuda']='0.0'
else:spec['expected']['packages']['pip']='0.0.0'
p=Path('/work/refused-'+damage);p.mkdir(mode=0o700)
e.environment_prepare(spec,Path('/work/wheels'),p,'c'*64,c.verify_wheels)
"""
    result=native(root,selected,script=script)
    assert result.returncode!=0 and code.encode() in result.stderr,result.stderr
    assert not (root/('refused-'+damage)/'environment.json').exists()
