"""Native alias and unchanged private-writer checks; synthetic mounts only.

No provider call, image bytes, scientific model or network is used. The real
bwrap namespace constructs the SDK-style mount alias, never host directories.
"""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import pytest
from orchestrator import private_records as pr


@pytest.fixture
def native(tmp_path):
    bwrap=shutil.which('bwrap')
    if not bwrap:pytest.skip('native bubblewrap unavailable')
    source=Path(__file__).resolve().parents[1]
    package=tmp_path/'mount-package';volume=tmp_path/'mount-data'
    pr.mkdir(package);pr.mkdir(volume)
    for name in ('__init__.py','private_records.py','modal_volume_path.py'):
        pr.copyfile(source/'orchestrator'/name,package/'orchestrator'/name)
    def run(script, *, target='/__modal/volumes/vo-Synthetic', relative=False, extra=()):
        probe=tmp_path/'probe.py';pr.write_text(probe,script)
        # On Arch /lib and /lib64 are links into /usr. Ubuntu's merged /usr
        # uses /usr/lib64 for lib64; bind the actual existing directory read-only.
        command=[bwrap,'--unshare-all','--die-with-parent','--new-session',
            '--ro-bind','/usr','/usr','--proc','/proc','--dev','/dev',
            '--dir','/__modal','--dir','/__modal/volumes',
            '--bind',str(volume),'/__modal/volumes/vo-Synthetic',
            '--ro-bind',str(package),'/reviewed','--ro-bind',str(probe),'/probe.py','--chdir','/']
        for lib in ('/lib','/lib64'):
            if Path(lib).exists():command+=['--ro-bind',str(Path(lib).resolve()),lib]
        command+=list(extra)+['--symlink',target.lstrip('/') if relative else target,'/volume',
            '/usr/bin/python3','-I','-S','-B','/probe.py']
        return subprocess.run(command,capture_output=True,text=True,timeout=30)
    return package,volume,run


PREAMBLE="import sys,os,json\nsys.path.insert(0,'/reviewed')\nfrom pathlib import Path\nfrom orchestrator.modal_volume_path import bound_root\nfrom orchestrator import private_records as pr\n"


@pytest.mark.parametrize('relative',[False,True])
def test_native_bound_alias_writes_private_children_only(native,relative):
    package,volume,run=native
    result=run(PREAMBLE+"root=bound_root('/volume','vo-Synthetic')\npr.mkdir(root/'images')\npr.write_bytes(root/'images/proof.json',b'{}')\npr.check_tree(root/'images')\nassert not Path('/home').exists()\nprint('PASS')\n",relative=relative)
    assert result.returncode==0,result.stderr
    assert result.stdout.strip()=='PASS'
    assert (volume/'images/proof.json').read_bytes()==b'{}'
    assert not (volume/'images').stat().st_mode&0o077
    assert not (volume/'images/proof.json').stat().st_mode&0o077


@pytest.mark.parametrize('fault',['wrong-id','elsewhere','nested-alias','readable-child','child-alias'])
def test_native_other_targets_and_unsafe_children_refuse(native,fault):
    package,volume,run=native
    ident='vo-Other' if fault=='wrong-id' else 'vo-Synthetic'
    target='/reviewed' if fault=='elsewhere' else '/__modal/volumes/vo-Synthetic'
    extra=[]
    if fault=='nested-alias':
        extra=['--symlink','/reviewed','/__modal/volumes/vo-Other'];ident='vo-Other';target='/__modal/volumes/vo-Other'
    if fault=='readable-child':
        pr.mkdir(volume/'images');(volume/'images').chmod(0o755)
    elif fault=='child-alias':(volume/'images').symlink_to('/reviewed',target_is_directory=True)
    script=PREAMBLE+"try:\n root=bound_root('/volume',"+repr(ident)+")\n pr.mkdir(root/'images',exist_ok=True)\nexcept ValueError as error:\n print(str(error))\nelse: raise AssertionError('unsafe target accepted')\n"
    result=run(script,target=target,extra=extra)
    assert result.returncode==0,result.stderr
    expected={'wrong-id':'DOWNLOAD_VOLUME_TARGET','elsewhere':'DOWNLOAD_VOLUME_TARGET',
        'nested-alias':'DOWNLOAD_VOLUME_TARGET','readable-child':'PRIVATE_RECORD_PERMISSIONS',
        'child-alias':'PRIVATE_RECORD_SYMLINK'}[fault]
    assert result.stdout.strip()==expected
    assert not (package/'proof.json').exists()


from test_modal_ctp_download import planned


def test_actual_launcher_uses_bound_volume_for_each_commit(native,planned,tmp_path):
    """Exact launcher/downloader/private writer in a real isolated namespace.
    Only HTTP, cohort pin and Volume-commit transport are synthetic; no model.
    """
    from orchestrator import modal_download_package as package
    target,volume,run=native;f=planned
    source=Path(__file__).resolve().parents[1];prepared=tmp_path/'emitted'
    receipt=package.emit(source,prepared,f.cohort,{'ctp':f.plan},'synthetic-attempt')
    for path in prepared.rglob('*'):
        if path.is_file():pr.copyfile(path,target/path.relative_to(prepared))
    script=PREAMBLE+"import io,runpy,subprocess\nfrom orchestrator import modal_ctp_download as ctp\n"
    script+="ctp.COHORT="+repr(__import__('hashlib').sha256(f.cohort).hexdigest())+"\n"
    script+="body="+repr(f.body)+"\n"
    script+="""
class Response(io.BytesIO):
    status=200
    url='https://cas-bridge.xethub.hf.co/synthetic-file'
    headers={'Content-Length':str(len(body))}
class Opener:
    def open(self,req,timeout):
        assert timeout==45
        return Response(body)
ctp.urllib.request.build_opener=lambda *args:Opener()
commits=[]
def commit(path):
    assert path==Path('/__modal/volumes/vo-Synthetic')
    commits.append(str(path))
ctp.volume_commit=commit
"""
    script+="sys.argv=['/reviewed/run.py',"+repr(receipt['manifest_sha256'])+",'ctp','vo-Synthetic']\n"
    script+="runpy.run_path('/reviewed/run.py',run_name='__main__')\n"
    script+="assert len(commits)>199\nsubprocess.run(['/usr/bin/sync','/__modal/volumes/vo-Synthetic'],check=True)\n"
    observed=run(script)
    assert observed.returncode==0,observed.stderr
    result=json.loads((volume/'DOWNLOAD_COMPLETE.json').read_bytes())
    assert result['results']['ctp']['files']==99 and result['patient_computation'] is False
    assert result['results']['ctp']['reused_files']==0
    pr.check_tree(volume/'ctp')
    assert len(list((volume/'ctp/train').rglob('*.nii.gz')))==99
    assert all((volume/'ctp'/name).read_bytes()==f.body for name in f.plan['files'])
