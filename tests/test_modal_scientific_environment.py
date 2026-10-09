"""Actual offline pip/metadata/worker transport; synthetic pure-Python wheel.

No SDK, paid resource, model or patient computation. The native test uses the
same confined guard and worker; the wheel is built locally from fixed bytes.
"""
import base64
import copy
import csv
import hashlib
import io
import json
from pathlib import Path
import subprocess
import sys
import zipfile
import pytest
from orchestrator import modal_scientific_environment as environment
from orchestrator import private_records as pr
from orchestrator.manual_executor import digest,inventory
from orchestrator.modal_executor import canonical
from test_modal_fit_mounts import mounted,worker_files
from test_modal_item4_provider import candidate


def tiny_wheel():
    files={'synthetic_runtime/__init__.py':(
            "VALUE = 'verified dependency'\n"
            "def main():\n"
            "    import json,os,sys\n"
            "    print(json.dumps({'value':VALUE,'python':sys.executable,'module':__file__,'pythonpath':os.environ['PYTHONPATH']}))\n").encode(),
        'synthetic_runtime-1.0.dist-info/entry_points.txt':b'[console_scripts]\nsynthetic-runtime-check = synthetic_runtime:main\n',
        'synthetic_runtime-1.0.dist-info/METADATA':b'Metadata-Version: 2.1\nName: synthetic-runtime\nVersion: 1.0\n',
        'synthetic_runtime-1.0.dist-info/WHEEL':b'Wheel-Version: 1.0\nGenerator: deterministic-test\nRoot-Is-Purelib: true\nTag: py3-none-any\n'}
    records=io.StringIO();writer=csv.writer(records)
    for name,data in files.items():writer.writerow([name,'sha256='+base64.urlsafe_b64encode(hashlib.sha256(data).digest()).rstrip(b'=').decode(),len(data)])
    writer.writerow(['synthetic_runtime-1.0.dist-info/RECORD','',''])
    files['synthetic_runtime-1.0.dist-info/RECORD']=records.getvalue().encode()
    buf=io.BytesIO()
    with zipfile.ZipFile(buf,'w') as z:
        for name,data in files.items():z.writestr(zipfile.ZipInfo(name,date_time=(2026,1,1,0,0,0)),data)
    return 'synthetic_runtime-1.0-py3-none-any.whl',buf.getvalue()


def spec(python_executable="/usr/bin/python3"):
    filename,raw=tiny_wheel()
    version=subprocess.check_output([python_executable,'-I','-c','import sys;print(sys.version)'],text=True).strip()
    return {'schema':'offline-scientific-python/v1','python_executable':python_executable,
        'expected':{'python':version,'cuda':None,'packages':{'synthetic-runtime':'1.0'}},
        'wheels':{filename:{'sha256':digest(raw),'bytes':len(raw)}}}


@pytest.mark.parametrize('damage',['path','shell','parent','schema','extra','duplicate-name','wheel-version','wheel-hash','wheel-size','wheel-alias','cuda'])
def test_environment_contract_refuses_before_install(damage):
    s=spec();name=next(iter(s['wheels']))
    if damage=='path':s['python_executable']='/tmp/python3'
    elif damage=='shell':s['python_executable']='/bin/sh'
    elif damage=='parent':s['python_executable']='/opt/../bin/python'
    elif damage=='schema':s['schema']='other'
    elif damage=='extra':s['command']='unselected'
    elif damage=='duplicate-name':s['expected']['packages']['synthetic_runtime']='1.0'
    elif damage=='wheel-version':s['expected']['packages']['synthetic-runtime']='2.0'
    elif damage=='wheel-hash':s['wheels'][name]['sha256']='bad'
    elif damage=='wheel-size':s['wheels'][name]['bytes']=True
    elif damage=='wheel-alias':s['wheels']['../'+name]=s['wheels'].pop(name)
    else:s['expected']['cuda']='ambiguous'
    with pytest.raises(ValueError,match='^SCIENTIFIC_ENVIRONMENT_'):environment.environment_validate(s)


@pytest.mark.parametrize('damage',[None,'wheel-hash','python','package-version','overlap'])
def test_native_offline_environment_guard_to_reviewed_module(mounted,worker_files,damage):
    roots,payload,run=mounted;package,inputs,_,seal=worker_files
    wheels=roots['progress'].parent/'mounted-wheels';pr.mkdir(wheels)
    roots['wheels']=wheels;payload['volume_ids']['wheels']='vo-Wheels'
    name,raw=tiny_wheel();pr.write_bytes(wheels/name,raw)
    # Ubuntu's system Python intentionally has no pip. Use the existing pinned
    # CPU tool package as the synthetic image environment; no host installation.
    native=Path('/opt/research-system-cpu-tools/m2-python312-xgb341-v2')
    python_root=native if native.is_dir() else None
    selected=spec(str(native/'bin/python') if python_root else '/usr/bin/python3')
    if damage=='python':selected['expected']['python']='wrong version'
    if damage=='package-version':selected['expected']['packages']['pip']='0.0.0'
    if damage=='wheel-hash':pr.write_bytes(wheels/name,raw[:-1]+bytes([raw[-1]^1]))
    if damage=='overlap':payload['volume_ids']['wheels']=payload['volume_ids']['inputs']
    source=(package/'execution.py').read_text().replace('def main(input_root, output_root, contract):',
        "def main(input_root, output_root, contract):\n"
        "    from synthetic_runtime import VALUE\n"
        "    import json,os,shutil,subprocess,sys\n"
        "    assert VALUE == 'verified dependency'\n"
        "    executable=shutil.which('synthetic-runtime-check')\n"
        "    assert executable==os.environ['PYTHONPATH']+'/bin/synthetic-runtime-check'\n"
        "    observed=json.loads(subprocess.check_output(['synthetic-runtime-check'],text=True))\n"
        "    assert observed['value']==VALUE and observed['python']==sys.executable\n"
        "    assert observed['module'].startswith(os.environ['PYTHONPATH']+'/synthetic_runtime/')\n"
        "    assert observed['pythonpath']==os.environ['PYTHONPATH']")
    pr.write_text(package/'execution.py',source);seal()
    binding=json.loads((package/'manifest.json').read_bytes())['binding']
    binding.update(scientific_environment=selected,package_volume_id=payload['volume_ids']['package'],
                   preprocessed_volume_id=payload['volume_ids']['inputs'])
    binding['progress']['volume_id']=payload['volume_ids']['progress']
    binding['progress']['fit_binding']['environment_sha256']=digest(environment.environment_bytes(selected['expected']))
    pin=seal(binding);manifest=json.loads((package/'manifest.json').read_bytes())
    for src,dst in ((package,roots['package']),(inputs,roots['inputs'])):
        for p in src.rglob('*'):
            if p.is_file() and p.name!='manifest.json':pr.copyfile(p,dst/p.relative_to(src))
    value=copy.deepcopy(payload);value.update(execution_manifest=manifest,binding_sha256=pin)
    value['files']={n:{'sha256':h,'bytes':(roots['inputs']/n).stat().st_size} for n,h in inventory(roots['inputs']).items()}
    result=run(value,python_root=python_root)
    if damage:
        assert result.returncode!=0,result.stdout
        assert not (roots['progress']/'executions').exists()
        if damage!='overlap':
            proof=json.loads((roots['progress']/'input-verification'/(pin+'.json')).read_bytes())
            assert proof['status']=='FAILED'
        return
    assert result.returncode==0,result.stderr
    receipt=json.loads((roots['progress']/'environment-verification'/pin/'environment.json').read_bytes())
    assert receipt['actual']==selected['expected'] and receipt['offline'] and receipt['binding_sha256']==pin
    original=(roots['progress']/'environment-verification'/pin/'environment.json').read_bytes()
    assert environment.environment_proof(original,manifest['binding'])['receipt_sha256']==digest(original)
    damaged=copy.deepcopy(receipt);damaged['actual']['packages']['synthetic-runtime']='2.0'
    with pytest.raises(ValueError,match='^SCIENTIFIC_ENVIRONMENT_PROOF$'):
        environment.environment_proof(json.dumps(damaged).encode(),manifest['binding'])
    proof=json.loads((roots['progress']/'input-verification'/(pin+'.json')).read_bytes())
    assert proof['status']=='VERIFIED' and proof['scientific_environment_sha256']==digest(canonical(selected))
    assert (roots['progress']/'executions'/pin/'artifacts/result.txt').is_file()
    original=inventory(roots['progress']);again=run(value,python_root=python_root)
    assert again.returncode!=0 and 'FileExistsError' in again.stderr
    assert inventory(roots['progress'])==original
    pr.check_tree(roots['progress'])


def test_actual_provider_refuses_missing_environment_before_paid_create(candidate):
    from orchestrator import modal_item4_provider as provider
    p,c,b,package,_,created,*_=candidate
    b['execution']={'schema':'reviewed-module/v1'}
    with pytest.raises(ValueError,match='^ITEM4_SCIENTIFIC_ENVIRONMENT_REQUIRED$'):
        provider.preflight(p,c,b,package)
    with pytest.raises(ValueError,match='^ITEM4_SCIENTIFIC_ENVIRONMENT_REQUIRED$'):
        provider.launch(p,'sb-unused',b)
    assert created==[]


@pytest.mark.parametrize('damage',[None,'config','wheel-inventory','fit-pin','version','cuda'])
def test_real_runtime_binding_and_launch_use_selected_interpreter(candidate,monkeypatch,damage):
    from types import SimpleNamespace as NS
    from orchestrator import modal_item4_provider as provider
    p,c,b,package,_,created,*_=candidate
    s=spec();s['expected'].update(cuda='12.8')
    s['expected']['packages'].update(nnunetv2='2.8.1',torch='2.8.0')
    s['python_executable']='/opt/conda/bin/python'
    c['scientific_environment']=copy.deepcopy(s);c['wheel_files']=copy.deepcopy(s['wheels'])
    b['scientific_environment']=copy.deepcopy(s)
    b['progress']['fit_binding']['environment_sha256']=digest(environment.environment_bytes(s['expected']))
    if damage=='config':c['scientific_environment']['python_executable']='/usr/bin/python3'
    elif damage=='wheel-inventory':c['wheel_files']={}
    elif damage=='fit-pin':b['progress']['fit_binding']['environment_sha256']='f'*64
    elif damage=='version':b['scientific_environment']['expected']['packages']['nnunetv2']='2.7.0'
    elif damage=='cuda':b['scientific_environment']['expected']['cuda']=None
    if damage:
        with pytest.raises(ValueError,match='^ITEM4_SCIENTIFIC_ENVIRONMENT_BINDING$'):
            provider.environment_scope(p,b,required=True)
        assert created==[];return
    assert provider.environment_scope(p,b,required=True)==s
    calls=[];p._sandbox=lambda ident:NS(object_id=ident,exec=lambda *a,**k:calls.append((a,k)))
    p.modal.stream_type=NS(StreamType=NS(DEVNULL='synthetic-devnull'))
    # Package synthesis separately verifies approval. This test fixes just the
    # outgoing transport payload after real runtime-binding validation.
    monkeypatch.setattr(provider,'guard_payload',lambda *args:{'binding_sha256':digest(canonical(b)),
        'guard_sha256':digest(provider.guard_program().encode()),'files':{}})
    provider.launch(p,'sb-synthetic',b)
    assert len(calls)==1 and calls[0][0][0]=='/opt/conda/bin/python'
    assert calls[0][1]['timeout']==b['resources']['timeout_seconds']
    assert not created


@pytest.mark.parametrize('damage',[None,'missing','version','binding','offline','duplicate'])
def test_provider_requires_original_environment_proof_at_collection(candidate,worker_files,tmp_path,damage):
    from orchestrator import modal_item4_provider as provider
    from test_modal_fit_result import Volume
    from orchestrator import modal_input_guard
    p,c,b,*_=candidate;package,_,_,seal=worker_files
    s=spec();s['expected'].update(cuda='12.8')
    s['expected']['packages'].update(nnunetv2='2.8.1',torch='2.8.0')
    c['scientific_environment']=s;c['wheel_files']=s['wheels'];b['scientific_environment']=s
    b['progress']['fit_binding']['environment_sha256']=digest(environment.environment_bytes(s['expected']))
    # Rebind only this synthetic preprocessing fixture to its selected test environment.
    preprocessing=Path(c['item4_assets']['preprocessing_receipt'])
    selected_receipt=json.loads(preprocessing.read_bytes())
    selected_receipt['environment_sha256']=b['progress']['fit_binding']['environment_sha256']
    pr.write_bytes(preprocessing,canonical(selected_receipt))
    c['item4_assets']['preprocessing_sha256']=b['preprocessing_sha256']=digest(preprocessing.read_bytes())
    b['experiment']['segment']=1;seal(b,c)
    b=json.loads((package/'manifest.json').read_bytes())['binding'];payload=provider.guard_payload(p,b)
    mount=tmp_path/'volume-proof';pr.mkdir(mount)
    proof={'schema':'modal-input-verification/v1',**{k:payload[k] for k in ('binding_sha256','guard_sha256','preprocessing_sha256')},
        'inventory_sha256':digest(canonical(payload['files'])),'file_count':len(payload['files']),
        'total_bytes':sum(x['bytes'] for x in payload['files'].values()),'volume_ids':payload['volume_ids'],
        'scientific_environment_sha256':digest(canonical(s)),'status':'VERIFIED','reason':None}
    pr.write_bytes(modal_input_guard.proof_path(mount,payload['binding_sha256']),canonical(proof))
    saved={'schema':'scientific-environment-proof/v1','binding_sha256':payload['binding_sha256'],
        'expected_sha256':digest(environment.environment_bytes(s['expected'])),'actual':copy.deepcopy(s['expected']),'offline':True}
    if damage=='version':saved['actual']['packages']['torch']='0.0.0'
    elif damage=='binding':saved['binding_sha256']='f'*64
    elif damage=='offline':saved['offline']=1
    raw=environment.environment_bytes(saved)
    if damage=='duplicate':raw=raw.replace(b'"offline":true',b'"offline":false,"offline":true')
    if damage!='missing':pr.write_bytes(mount/'environment-verification'/payload['binding_sha256']/'environment.json',raw)
    if damage:
        with pytest.raises(ValueError):provider.input_proof(p,b,Volume(mount))
    else:
        result=provider.input_proof(p,b,Volume(mount))
        assert result['environment']['actual']==s['expected']
        assert result['environment']['receipt_sha256']==digest(raw)


@pytest.mark.parametrize('damage',['target-alias','bin-alias','script-alias','readable-bin','writable-script'])
def test_console_path_refuses_unsafe_new_search_directory(tmp_path,damage):
    target=tmp_path/'target';pr.mkdir(target)
    scripts=target/'bin';pr.mkdir(scripts);pr.write_text(scripts/'synthetic-command','synthetic fixture')
    selected=target
    if damage=='target-alias':
        alias=tmp_path/'alias';alias.symlink_to(target,target_is_directory=True);selected=alias
    elif damage=='bin-alias':
        scripts.rename(tmp_path/'other');scripts.symlink_to(tmp_path/'other',target_is_directory=True)
    elif damage=='script-alias':
        (scripts/'synthetic-command').unlink();(scripts/'synthetic-command').symlink_to(tmp_path/'outside')
    elif damage=='readable-bin':scripts.chmod(0o755)
    else:(scripts/'synthetic-command').chmod(0o722)
    with pytest.raises(ValueError,match='^SCIENTIFIC_ENVIRONMENT_SCRIPT_PATH$'):
        environment.environment_path(selected,'/usr/bin:/bin')


def test_no_console_scripts_leaves_existing_path_unchanged(tmp_path):
    target=tmp_path/'target';pr.mkdir(target)
    assert environment.environment_path(target,'/usr/bin:/bin')=='/usr/bin:/bin'
