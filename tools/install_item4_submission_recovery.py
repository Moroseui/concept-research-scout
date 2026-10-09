"""Install exact genuinely approved author5 component, held; no model launch."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

CHANGE = 'item4-author5-submission-recovery-20261008'
ROOT = Path('/opt/research-system/manual-repair-helpers')/CHANGE
RECORD = Path('/var/lib/research-system-manual-sprint10-deployment')/CHANGE
REVIEW_ENGINE = Path('/opt/research-system/autonomy-review/b71912e6cfbf')
SCIENCE = Path('/opt/research-system/manual-sprint10/research-manual-sprint10-timeout-continuation-8e042339')
RUNTIME = Path('/etc/research-system-manual-sprint10/releases')/SCIENCE.name/'runtime.json'
OLD_UNIT = Path('/etc/systemd/system/research-daily50-and-image-probe-20261007-item4.service')
UNIT = Path('/etc/systemd/system')/('research-'+CHANGE+'.service')
AUTHORITY = 'a9ded8872a67385ab3a47f95a39914271ba8f4de9a8f8015c197bb7be35c4ef6'
MODULES = ('author_format_submission','author_submission_recovery')
FILES = tuple('orchestrator/'+n+'.py' for n in MODULES) + (
    'tools/item4_submission_recovery_component.py','tools/install_item4_submission_recovery.py',
    'docs/ITEM4_AUTHOR5_RECOVERY_BINDINGS.json','docs/ITEM4_AUTHOR5_RECOVERY_APPROVAL_20261008.txt')


def require(ok, why):
    if not ok: raise ValueError(why)
def sha(raw): return hashlib.sha256(raw).hexdigest()
def trusted(path):
    path = Path(path)
    for p in [path,*path.parents]:
        st = p.lstat()
        require(not p.is_symlink() and st.st_uid == 0 and not st.st_mode & 0o022, 'AUTHOR_INSTALL_UNTRUSTED')
    return path


def unit_bytes(original):
    before = 'ExecStart=/usr/bin/python3 -s -B /opt/research-system/manual-repair-helpers/daily-limit-and-image-probe-20261007/tools/daily_limit_component.py 4'
    after = 'ExecStart=/usr/bin/python3 -s -B '+str(ROOT/'tools/item4_submission_recovery_component.py')+' run'
    require(original.count(before) == 1, 'AUTHOR_INSTALL_UNIT_SHAPE')
    return original.replace(before, after).encode()


def put(path, raw):
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    with path.open('xb') as f:f.write(raw)
    os.chown(path,0,1003);os.chmod(path,0o440)


def install(packet, review, source):
    require(os.getuid() == 0, 'AUTHOR_INSTALL_ROOT_REQUIRED')
    sys.path.insert(0,str(REVIEW_ENGINE))
    from orchestrator import autonomy_review as ar
    m=ar.verify_packet(packet);a=ar.verify_result(review)
    require(a['verdict']=='APPROVE' and a['source_sha']==m['source_sha']==source and
            a['change_id']==m['change_id']==CHANGE and a['runtime_sha256']==sha(trusted(RUNTIME).read_bytes()),
            'AUTHOR_INSTALL_GENUINE_APPROVAL_REQUIRED')
    require(ar.canonical(m)==ar.canonical(json.loads((Path(review)/'packet-manifest.json').read_bytes())), 'AUTHOR_INSTALL_REVIEW_PACKET_BINDING')
    require(not ROOT.exists() and not RECORD.exists() and not UNIT.exists(), 'AUTHOR_INSTALL_EXISTS_INSPECT')
    bodies={name:(Path(packet)/'source'/name).read_bytes() for name in FILES}
    require(all(sha(raw)==m['source_files'][name] for name,raw in bodies.items()), 'AUTHOR_INSTALL_SOURCE_CHANGED')
    require(bodies['tools/install_item4_submission_recovery.py']==Path(__file__).read_bytes(), 'AUTHOR_INSTALLER_NOT_REVIEWED')
    require(sha(bodies['docs/ITEM4_AUTHOR5_RECOVERY_APPROVAL_20261008.txt'])==AUTHORITY, 'AUTHOR_INSTALL_AUTHORITY')
    require(json.loads(bodies['docs/ITEM4_AUTHOR5_RECOVERY_BINDINGS.json'])['authority_sha256']==AUTHORITY, 'AUTHOR_INSTALL_AUTHORITY_BINDING')
    properties=dict(x.split('=',1) for x in subprocess.check_output(['systemctl','show',OLD_UNIT.name,
        '--property=ActiveState,MainPID,ControlGroup'],text=True).splitlines())
    require(properties=={'ActiveState':'inactive','MainPID':'0','ControlGroup':''}, 'AUTHOR_EXISTING_SERVICE_ACTIVE')
    author_unit=dict(x.split('=',1) for x in subprocess.check_output(['systemctl','show','research-item4-author-submission-20261008.service',
        '--property=LoadState,ActiveState,MainPID,ControlGroup'],text=True).splitlines())
    require(author_unit=={'LoadState':'loaded','ActiveState':'inactive','MainPID':'0','ControlGroup':''},'AUTHOR5_NOT_STOPPED')
    original=trusted(OLD_UNIT).read_bytes();unit=unit_bytes(original.decode())
    daily=Path('/opt/research-system/manual-repair-helpers/daily-limit-and-image-probe-20261007/tools/daily_limit_component.py')
    legacy=Path('/opt/research-system/manual-repair-helpers/item4-author-submission-20261008/tools/item4_author_submission_component.py')
    baseline=[daily, legacy, *(SCIENCE/'orchestrator'/(name+'.py') for name in (
        'manual_stage','manual_isolation','manual_driver','manual_executor','experiment_driver',
        'experiment_plan_validation','experiment_plan_output','experiment_context'))]
    pins={str(p):sha(trusted(p).read_bytes()) for p in baseline}
    trusted(ROOT.parent);trusted(RECORD.parent);trusted(UNIT.parent)
    # Every original unit, file and credential remains unchanged.
    ROOT.mkdir(mode=0o700);RECORD.mkdir(mode=0o700)
    put(RECORD/'INSTALL_INTENT.json',json.dumps({'source':source,'review':a,'scope':'held exact preserved author5 recovery; no model or provider launch'},sort_keys=True).encode())
    for name,raw in bodies.items():put(ROOT/name,raw)
    for path in Path(review).iterdir():
        require(path.is_file() and not path.is_symlink(), 'AUTHOR_REVIEW_ORIGINAL_FILE')
        put(RECORD/'review'/path.name,path.read_bytes())
    put(RECORD/'prior-unit.txt',original)
    put(UNIT,unit);os.chown(UNIT,0,0);os.chmod(UNIT,0o644)
    receipt={'schema':'reviewed-author5-submission-recovery/v1','root':str(ROOT),'source':source,
        'review_folder':str(RECORD/'review'),'review_sha256':a['report_sha256'],
        'files':{n:sha(raw) for n,raw in bodies.items()},'base_files':pins,
        'units':{str(OLD_UNIT):sha(original),str(UNIT):sha(unit)}}
    put(RECORD/'installed.json',json.dumps(receipt,sort_keys=True).encode())
    for root in [ROOT,RECORD]:
        for path in [root,*[p for p in root.rglob('*') if p.is_dir()]]:os.chown(path,0,1003);os.chmod(path,0o550)
    subprocess.run(['systemctl','daemon-reload'],check=True)
    command=['runuser','-u','partho','--','env','PYTHONPATH='+str(SCIENCE),
        'RESEARCH_MANUAL_RUNTIME_CONFIG='+str(RUNTIME),'PYTHONDONTWRITEBYTECODE=1',
        'python3','-s','-B',str(ROOT/'tools/item4_submission_recovery_component.py')]
    # Qualification precedes recovery; neither action launches a model.
    for action in ['verify','apply']:
        result=subprocess.run(command+[action],capture_output=True,text=True,timeout=180)
        put(RECORD/(action+'.stdout'),result.stdout.encode());put(RECORD/(action+'.stderr'),result.stderr.encode())
        require(result.returncode==0, 'AUTHOR_INSTALL_POSTCHECK_'+action.upper())
    put(RECORD/'APPLIED.json',json.dumps({'status':'INSTALLED_HELD','source':source,'review_sha256':a['report_sha256'],'model_calls':0},sort_keys=True).encode())
    return {'status':'INSTALLED_HELD','model_calls':0,'unit':UNIT.name}


REVIEW_CHANGES = ('orchestrator/autonomy_review.py','orchestrator/autonomy_review_runner.py',
    'orchestrator/administrative_terminal.py','orchestrator/author_submission_recovery.py',
    'docs/ADMINISTRATIVE_REVIEW_OPERATOR_DECISION_20261008.txt',
    'docs/ITEM4_AUTHOR5_RECOVERY_APPROVAL_20261008.txt','docs/ITEM4_AUTHOR5_RECOVERY_BINDINGS.json')

def install_review_engine(packet, review, source, bundle, bundle_pin):
    """Approved three-round policy, beside prior reviewer; no state reset/call."""
    import io
    import tarfile
    require(os.getuid()==0,'REVIEW_INSTALL_ROOT_REQUIRED')
    sys.path.insert(0,str(REVIEW_ENGINE))
    from orchestrator import autonomy_review as ar
    from tools.deploy_autonomy_review import install as install_bundle
    m=ar.verify_packet(packet);a=ar.verify_result(review)
    require(a['verdict']=='APPROVE' and a['source_sha']==m['source_sha']==source and
        a['change_id']==m['change_id']==CHANGE and a['runtime_sha256']==sha(trusted(RUNTIME).read_bytes()),'REVIEW_INSTALL_APPROVAL')
    require(ar.canonical(m)==ar.canonical(json.loads((Path(review)/'packet-manifest.json').read_bytes())),'REVIEW_PACKET_BINDING')
    require((Path(packet)/'source/tools/install_item4_submission_recovery.py').read_bytes()==Path(__file__).read_bytes(),'REVIEW_INSTALLER_BINDING')
    prior=Path('/etc/research-system-autonomy/review/b71912e6cfbf/install-receipt.json')
    require(sha(trusted(prior).read_bytes())=='50139791d691a2e31139024f6a044e6da1738abafbf0fbbeedc883d0b3103cb3','REVIEW_PRIOR_INSTALL')
    old=json.loads(trusted(prior.parent/'binding.json').read_bytes())
    raw=trusted(bundle).read_bytes();require(sha(raw)==bundle_pin,'REVIEW_BUNDLE_PIN')
    bodies={}
    with tarfile.open(fileobj=io.BytesIO(raw)) as archive:
        for member in archive.getmembers():
            require(member.isfile() and member.name not in bodies,'REVIEW_BUNDLE_MEMBERS')
            bodies[member.name]=archive.extractfile(member).read()
    meta=json.loads(bodies.pop('install.json'))
    require(meta['source']==source and meta['previous']=={'path':str(prior),'sha256':sha(prior.read_bytes())},'REVIEW_BUNDLE_SOURCE')
    require(sha(bodies['runtime.json'])==old['runtime_sha256'],'REVIEW_RUNTIME_UNCHANGED')
    expected={**old['release_files'],**{n:m['source_files'][n] for n in REVIEW_CHANGES}}
    actual={n[7:]:sha(raw) for n,raw in bodies.items() if n.startswith('source/')}
    require(actual==expected,'REVIEW_ONLY_APPROVED_FILES')
    ident=ar.sha(ar.canonical(m))
    require(meta['requests']=={ident:m},'REVIEW_ONE_BOUND_REQUEST')
    installed=install_bundle(Path('/'),bundle,bundle_pin)
    # The new route is disabled. Publish the exact root-sealed terminal proof;
    # root never opens live SQLite. The snapshot was obtained by UID1003.
    row_code="""from pathlib import Path
import os,json,sqlite3
assert os.getuid()==1003
p=Path('/var/lib/research-system-autonomy/reviews/jobs.sqlite')
with sqlite3.connect(p.as_uri()+'?mode=ro',uri=True) as db:
 db.row_factory=sqlite3.Row
 row=db.execute('SELECT * FROM autonomy_calls WHERE id=?',('49cc364b033bf52198fbc44c5470bb72b9cfec03826294f71f2dd2286d244524',)).fetchone()
 print(json.dumps(dict(row)))
"""
    row=json.loads(subprocess.check_output(['runuser','-u','partho','--','python3','-s','-B','-c',row_code]))
    import importlib.util
    path=Path(installed['release'])/'orchestrator/author_submission_recovery.py'
    spec=importlib.util.spec_from_file_location('_installed_author5_terminal',path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    b=module.binding();work=Path(b['workspace'])
    native={n:(work/n).read_bytes() for n in b['native_files']};module.terminal(row,native)
    unit=dict(x.split('=',1) for x in subprocess.check_output(['systemctl','show',module.UNIT,
        '-p','LoadState','-p','ActiveState','-p','MainPID','-p','ControlGroup','-p','InvocationID'],text=True).splitlines())
    require(unit['LoadState']=='loaded' and unit['ActiveState']=='inactive' and unit['MainPID']=='0' and not unit['ControlGroup'],'AUTHOR5_STILL_TERMINAL')
    from orchestrator import administrative_terminal as old_terminal
    folder=Path('/var/lib/research-system-autonomy/scientific-terminal')/module.CALL
    require(not folder.exists() and not folder.is_symlink(),'TERMINAL_PROOF_EXISTS_INSPECT')
    folder.mkdir(mode=0o700)
    for n,body in native.items():put(folder/n,body)
    proof={'schema':'administrative-only-terminal/v1','id':module.CALL,'row_sha256':old_terminal.row_hash(row),
        'authority_sha256':old_terminal.APPROVAL,'classification':'PROVEN_EXACT_AUTHOR5_SUBMISSION_REFUSAL_ADMIN_ONLY',
        'unit':{'unit':module.UNIT,'invocation':unit.get('InvocationID',''),'boot_id':Path('/proc/sys/kernel/random/boot_id').read_text().strip()},
        'files':{n:sha(body) for n,body in native.items()},'meaning':'Exact terminal qualification only; all original rows and charges remain unchanged.'}
    put(folder/'proof.json',json.dumps(proof,sort_keys=True).encode());os.chown(folder,0,1003);os.chmod(folder,0o550)
    subprocess.run(['systemctl','daemon-reload'],check=True)
    return installed


if __name__=='__main__':
    os.umask(0o077)
    p=argparse.ArgumentParser();p.add_argument('--packet',type=Path,required=True);p.add_argument('--review',type=Path,required=True);p.add_argument('--source',required=True);p.add_argument('--review-bundle',type=Path);p.add_argument('--review-bundle-sha');args=p.parse_args()
    if args.review_bundle is not None:
        print(json.dumps(install_review_engine(args.packet,args.review,args.source,args.review_bundle,args.review_bundle_sha),sort_keys=True))
    else:print(json.dumps(install(args.packet,args.review,args.source),sort_keys=True))
