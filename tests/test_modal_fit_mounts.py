"""Actual provider program in native confinement; no model, SDK or patient work."""
from pathlib import Path
import copy
import hashlib
import json
import shutil
import subprocess
import pytest
from orchestrator import private_records as pr
from orchestrator.modal_item4_provider import guard_program
from orchestrator.modal_fit_progress import encoded as progress_encoded


def sha(raw):return hashlib.sha256(raw).hexdigest()


@pytest.fixture
def mounted(tmp_path):
    bwrap=shutil.which('bwrap')
    if not bwrap:pytest.skip('native bubblewrap unavailable')
    roots={k:tmp_path/('mounted-'+k) for k in ('inputs','progress','package')}
    for p in roots.values():pr.mkdir(p)
    pr.write_bytes(roots['inputs']/'synthetic.bin',b'synthetic aggregate bytes')
    # Actual exec handoff and exact arguments; this harmless marker stands for
    # scientific code, never a patient calculation or a manufactured result.
    worker=("import argparse,json\nfrom pathlib import Path\n"
            "p=argparse.ArgumentParser();p.add_argument('--binding');p.add_argument('--input-root');p.add_argument('--progress-root');a=p.parse_args()\n"
            "assert a.input_root=='/__modal/volumes/vo-Inputs'\n"
            "assert a.progress_root=='/__modal/volumes/vo-Progress'\n"
            "assert Path(a.input_root,'synthetic.bin').read_bytes()==b'synthetic aggregate bytes'\n"
            "assert not Path('/home').exists() and not Path('/mnt/c').exists()\n"
            "with Path(a.progress_root,'executed.json').open('x') as f:json.dump({'binding':a.binding},f)\n")
    pr.write_text(roots['package']/'run.py',worker)
    ids={'inputs':'vo-Inputs','progress':'vo-Progress','package':'vo-Package'}
    raw=(roots['inputs']/'synthetic.bin').read_bytes()
    program=guard_program()
    payload={'binding_sha256':'a'*64,'guard_sha256':sha(program.encode()),'preprocessing_sha256':'b'*64,
             'files':{'synthetic.bin':{'sha256':sha(raw),'bytes':len(raw)}},'volume_ids':ids}
    def run(value=None, *, targets=None, python_root=None):
        value=payload if value is None else value
        aliases={'inputs':'/preprocessed','progress':'/progress','package':'/reviewed','wheels':'/wheels'}
        targets=targets or {k:'/__modal/volumes/'+ident for k,ident in ids.items()}
        args=[bwrap,'--unshare-all','--die-with-parent','--new-session','--ro-bind','/usr','/usr',
              '--proc','/proc','--dev','/dev','--dir','/__modal','--dir','/__modal/volumes','--tmpfs','/tmp','--chdir','/tmp']
        for lib in ('/lib','/lib64'):
            if Path(lib).exists():args+=['--ro-bind',str(Path(lib).resolve()),lib]
        for k,p in roots.items():
            args+=['--bind' if k=='progress' else '--ro-bind',str(p),'/__modal/volumes/'+ids[k]]
            args+=['--symlink',targets[k],aliases[k]]
        executable='/usr/bin/python3'
        if python_root is not None:
            # Test-only existing tool package, not host site-packages or private data.
            selected=Path('/opt/research-system-cpu-tools/m2-python312-xgb341-v2')
            assert Path(python_root)==selected and selected.is_dir() and not selected.is_symlink()
            args+=['--ro-bind',str(selected),str(selected)]
            executable=str(selected/'bin/python')
        args+=[executable,'-I','-S','-B','-c',program,json.dumps(value)]
        return subprocess.run(args,capture_output=True,text=True,timeout=30)
    return roots,payload,run


def test_native_three_alias_guard_actual_exec_and_duplicate_refusal(mounted):
    roots,payload,run=mounted
    first=run();assert first.returncode==0,first.stderr
    result=roots['progress']/'executed.json';assert json.loads(result.read_bytes())=={'binding':'a'*64}
    proof=roots['progress']/('input-verification/'+'a'*64+'.json')
    preserved=proof.read_bytes();assert json.loads(preserved)['volume_ids']==payload['volume_ids']
    pr.check_tree(roots['progress'])
    second=run();assert second.returncode!=0 and 'FileExistsError' in second.stderr
    assert proof.read_bytes()==preserved and result.is_file()


@pytest.mark.parametrize('fault',['wrong-input','wrong-package','wrong-progress','shared-id','unknown-role','outside-target','hash','child-alias','readable-progress','readable-record'])
def test_native_role_and_child_refusals_before_code(mounted,fault):
    roots,payload,run=mounted;value=copy.deepcopy(payload);targets=None
    if fault.startswith('wrong-'):
        role={'wrong-input':'inputs','wrong-package':'package','wrong-progress':'progress'}[fault]
        value['volume_ids'][role]='vo-Other'
    elif fault=='shared-id':value['volume_ids']['progress']=value['volume_ids']['inputs']
    elif fault=='unknown-role':value['volume_ids']['extra']='vo-Extra'
    elif fault=='outside-target':
        targets={k:'/__modal/volumes/'+v for k,v in payload['volume_ids'].items()};targets['inputs']='/usr'
    elif fault=='hash':pr.write_bytes(roots['inputs']/'synthetic.bin',b'x'*len(b'synthetic aggregate bytes'))
    elif fault=='child-alias':(roots['inputs']/'other').symlink_to('/usr')
    elif fault=='readable-progress':roots['progress'].chmod(0o755)
    else:pr.mkdir(roots['progress']/'input-verification');(roots['progress']/'input-verification').chmod(0o755)
    result=run(value,targets=targets);assert result.returncode!=0
    expected={'wrong-input':'DOWNLOAD_VOLUME_TARGET','wrong-package':'DOWNLOAD_VOLUME_TARGET',
              'wrong-progress':'DOWNLOAD_VOLUME_TARGET','shared-id':'FIT_VOLUME_ROLE_BINDING',
              'unknown-role':'FIT_VOLUME_ROLE_BINDING','outside-target':'DOWNLOAD_VOLUME_TARGET',
              'hash':'INPUT_GUARD_HASH','child-alias':'INPUT_GUARD_ALIAS_OR_TYPE',
              'readable-progress':'INPUT_GUARD_RECORD_PERMISSIONS','readable-record':'INPUT_GUARD_RECORD_PERMISSIONS'}[fault]
    assert expected in result.stderr,result.stderr
    assert not (roots['progress']/'executed.json').exists()
    if fault=='readable-progress':assert roots['progress'].stat().st_mode&0o777==0o755
    if fault=='readable-record':assert (roots['progress']/'input-verification').stat().st_mode&0o777==0o755


def test_downloader_does_not_gain_fit_alias_permission():
    from orchestrator.modal_volume_path import bound_root
    with pytest.raises(ValueError,match='^DOWNLOAD_VOLUME_ALIAS$'):
        bound_root('/progress','vo-Progress')


from test_experiment_modal_package import worker_files


def test_native_guard_to_actual_worker_to_validated_publication(mounted,worker_files):
    """Real launcher/worker/validator/checkpoint publisher. Only the scientific
    module and mount provider are synthetic; no real data or model calls."""
    from orchestrator.manual_executor import inventory
    roots,payload,run=mounted
    package,inputs,progress,seal=worker_files
    seal()
    bound=json.loads((package/'manifest.json').read_bytes())['binding']
    bound['package_volume_id']=payload['volume_ids']['package']
    bound['preprocessed_volume_id']=payload['volume_ids']['inputs']
    bound['progress']['volume_id']=payload['volume_ids']['progress']
    pin=seal(bound)
    for folder,target in ((package,roots['package']),(inputs,roots['inputs'])):
        for path in folder.rglob('*'):
            if path.is_file():pr.copyfile(path,target/path.relative_to(folder))
    value=copy.deepcopy(payload);value['binding_sha256']=pin
    value['files']={name:{'sha256':h,'bytes':(roots['inputs']/name).stat().st_size}
                    for name,h in inventory(roots['inputs']).items()}
    result=run(value);assert result.returncode==0,result.stderr
    output=roots['progress']/'executions'/pin
    assert (output/'artifacts/result.txt').read_bytes()==(inputs/'synthetic.txt').read_bytes()
    execution=json.loads((output/'execution.json').read_bytes())
    assert execution['status']=='EXECUTED' and execution['scientifically_validated'] is False
    assert json.loads((output/'validation-receipt.json').read_bytes())['status']=='VALIDATED'
    assert (roots['progress']/'fits/fit/final.json').is_file()
    before=inventory(roots['progress']);again=run(value)
    assert again.returncode!=0 and 'FileExistsError' in again.stderr
    assert inventory(roots['progress'])==before
    pr.check_tree(roots['progress'])


@pytest.mark.parametrize('checkpoint_drift',[False,True])
def test_native_static_payload_resumes_checkpoint_with_transported_segment(mounted,worker_files,checkpoint_drift):
    """Real confined guard -> manifest CLI -> worker -> checkpoint continuation.
    Only science is synthetic. Terminal admission is separately tested against
    the real controller ledger; this test covers the actual remote transport."""
    from orchestrator.manual_executor import inventory
    from test_experiment_modal_package import VALIDATION_SOURCE
    from orchestrator.modal_executor import canonical
    roots,payload,run=mounted
    package,inputs,_,seal=worker_files
    pr.write_text(package/'execution.py',
        "def main(i,o,c):\n"
        "    fit=c['progress'];segment=c['runtime']['experiment']['segment']\n"
        "    if segment==1:\n"
        "        fit.publish('latest',lambda p:p.write_bytes(b'saved epoch one'),metadata={'next_epoch':1,'total_epochs':2,'native_version':'2.8.1'})\n"
        "        raise RuntimeError('synthetic deliberate interruption')\n"
        "    assert segment==2\n"
        "    checkpoint,record=fit.select('latest')\n"
        "    assert checkpoint.read_bytes()==b'saved epoch one' and record['metadata']['next_epoch']==1\n"
        "    (o/'result.txt').write_text((i/'synthetic.txt').read_text())\n"
        "    fit.publish('final',lambda p:p.write_bytes(b'resumed epoch two'),metadata={'next_epoch':2,'total_epochs':2,'native_version':'2.8.1'})\n"
        "    validation(o,c)\n"+VALIDATION_SOURCE)
    seal();bound=json.loads((package/'manifest.json').read_bytes())['binding']
    bound['package_volume_id']=payload['volume_ids']['package']
    bound['preprocessed_volume_id']=payload['volume_ids']['inputs']
    bound['progress']['volume_id']=payload['volume_ids']['progress']
    pin=seal(bound);manifest=json.loads((package/'manifest.json').read_bytes())
    for folder,target in ((package,roots['package']),(inputs,roots['inputs'])):
        for path in folder.rglob('*'):
            if path.is_file() and path.name!='manifest.json':pr.copyfile(path,target/path.relative_to(folder))
    original_package=inventory(roots['package'])
    value=copy.deepcopy(payload);value.update(binding_sha256=pin,execution_manifest=manifest)
    value['files']={n:{'sha256':h,'bytes':(roots['inputs']/n).stat().st_size} for n,h in inventory(roots['inputs']).items()}
    first=run(value);assert first.returncode!=0 and 'synthetic deliberate interruption' in first.stderr
    first_folder=roots['progress']/'executions'/pin;first_original=inventory(first_folder)
    assert json.loads((first_folder/'execution.json').read_bytes())['status']=='FAILED'
    pointer=(roots['progress']/'fits/fit/latest.json').read_bytes()
    second=copy.deepcopy(value);binding=second['execution_manifest']['binding']
    binding['experiment']['segment']=2
    binding['resume']={'previous_segment_id':pin,'terminal_receipt_sha256':'a'*64,
                       'checkpoint_record_sha256':sha(progress_encoded(json.loads(pointer)))} # Exact terminal proof encoding.
    if checkpoint_drift:binding['resume']['checkpoint_record_sha256']='f'*64
    second['binding_sha256']=sha(canonical(binding))
    result=run(second)
    if checkpoint_drift:
        assert result.returncode!=0 and 'EXPERIMENT_WORKER_RESUME_CHECKPOINT_CHANGED' in result.stderr
        assert inventory(first_folder)==first_original and inventory(roots['package'])==original_package
        assert not (roots['progress']/'fits/fit/final.json').exists()
        assert not list((roots['progress']/'executions'/second['binding_sha256']/'artifacts').iterdir())
        return
    assert result.returncode==0,result.stderr
    assert inventory(roots['package'])==original_package and not (roots['package']/'manifest.json').exists()
    assert inventory(first_folder)==first_original
    assert (roots['progress']/'fits/fit/latest.json').read_bytes()==pointer
    output=roots['progress']/'executions'/second['binding_sha256']
    assert json.loads((output/'validation-receipt.json').read_bytes())['status']=='VALIDATED'
    assert (output/'artifacts/result.txt').read_bytes()==(inputs/'synthetic.txt').read_bytes()
    before=inventory(roots['progress']);repeat=run(second)
    assert repeat.returncode!=0 and 'FileExistsError' in repeat.stderr
    assert inventory(roots['progress'])==before
    pr.check_tree(roots['progress'])


@pytest.mark.parametrize('damage',['binding','schema','files','disk-manifest'])
def test_native_transported_manifest_refuses_changes_before_worker(mounted,worker_files,damage):
    from orchestrator.manual_executor import inventory
    roots,payload,run=mounted;package,inputs,_,seal=worker_files
    seal();bound=json.loads((package/'manifest.json').read_bytes())['binding']
    bound['package_volume_id']=payload['volume_ids']['package']
    bound['preprocessed_volume_id']=payload['volume_ids']['inputs']
    bound['progress']['volume_id']=payload['volume_ids']['progress']
    pin=seal(bound);manifest=json.loads((package/'manifest.json').read_bytes())
    for path in package.rglob('*'):
        if path.is_file() and path.name!='manifest.json':pr.copyfile(path,roots['package']/path.relative_to(package))
    value=copy.deepcopy(payload);value.update(binding_sha256=pin,execution_manifest=manifest)
    if damage=='binding':value['execution_manifest']['binding']['experiment']['segment']=2
    elif damage=='schema':value['execution_manifest']['schema']='other'
    elif damage=='files':value['execution_manifest']['files']['execution.py']='f'*64
    else:pr.write_bytes(roots['package']/'manifest.json',b'{}')
    result=run(value);assert result.returncode!=0
    expected={'binding':'INPUT_GUARD_EXECUTION_BINDING','schema':'INPUT_GUARD_EXECUTION_BINDING',
              'files':'EXPERIMENT_WORKER_PACKAGE_CHANGED','disk-manifest':'EXPERIMENT_WORKER_MANIFEST_TRANSPORT'}[damage]
    assert expected in result.stderr,result.stderr
    assert not (roots['progress']/'executions').exists()
