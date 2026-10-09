"""Install exact genuinely approved context-delivery component, held; no model launch."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

CHANGE = 'item4-author7-and-image-recovery-20261008'
ROOT = Path('/opt/research-system/manual-repair-helpers')/CHANGE
RECORD = Path('/var/lib/research-system-manual-sprint10-deployment')/CHANGE
REVIEW_ENGINE = Path('/opt/research-system/autonomy-review/d08b91bdc1d0')
SCIENCE = Path('/opt/research-system/manual-sprint10/research-manual-sprint10-timeout-continuation-8e042339')
RUNTIME = Path('/etc/research-system-manual-sprint10/releases')/SCIENCE.name/'runtime.json'
OLD_UNIT = Path('/etc/systemd/system/research-item4-runtime-binding-repair-20261008.service')
UNIT = Path('/etc/systemd/system')/('research-'+CHANGE+'.service')
AUTHORITY = 'c9f088863d00ca160e7f104a2571291f36be2af1907e296783eb172785fa1d63'
import importlib.util
_spec=importlib.util.spec_from_file_location('_revision_install_contract',Path(__file__).with_name('item4_scientific_revision_component.py'))
_contract=importlib.util.module_from_spec(_spec);_spec.loader.exec_module(_contract)
FILES=_contract.FILES



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
    before = 'ExecStart=/usr/bin/python3 -s -B /opt/research-system/manual-repair-helpers/item4-runtime-binding-repair-20261008/tools/item4_scientific_revision_component.py run'
    after = 'ExecStart=/usr/bin/python3 -s -B '+str(ROOT/'tools/item4_scientific_revision_component.py')+' run'
    require(original.count(before) == 1, 'AUTHOR_INSTALL_UNIT_SHAPE')
    return original.replace(before, after).encode()


def put(path, raw):
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    with path.open('xb') as f:f.write(raw)
    os.chown(path,0,1003);os.chmod(path,0o440)


def upgrade(bodies, evidence_bodies, review, approved, source):
    """Update the same held service; preserve originals and never edit lane state."""
    prior_spec=importlib.util.spec_from_file_location('_prior_scientific_revision',
        trusted(ROOT/'tools/item4_scientific_revision_component.py'))
    prior=importlib.util.module_from_spec(prior_spec);prior_spec.loader.exec_module(prior)
    old,checkpoint,manifest=prior.verified()
    require(old['source']==_contract.SECOND_SOURCE and old['review_sha256']==_contract.SECOND_REVIEW, 'AUTHOR_UPGRADE_PRIOR_SOURCE')
    replacement=json.loads(bodies['docs/ITEM4_REVISION_CHECKPOINT.json'])
    require({k:v for k,v in replacement.items() if k!='evidence_manifest_sha256'}==
        {k:v for k,v in checkpoint.items() if k!='evidence_manifest_sha256'},'AUTHOR_UPGRADE_CHECKPOINT_CHANGED')
    new_manifest=json.loads(bodies['docs/ITEM4_REVISION_EVIDENCE.json'])
    require(new_manifest['files'][:len(manifest['files'])]==manifest['files'] and
        {k:v for k,v in new_manifest.items() if k!='files'}==
        {k:v for k,v in manifest.items() if k!='files'},'AUTHOR_UPGRADE_PRIOR_EVIDENCE_CHANGED')
    for row in manifest['files']:
        require(evidence_bodies[row['name']]==trusted(RECORD/'evidence'/row['name']).read_bytes(),
            'AUTHOR_UPGRADE_ORIGINAL_CHANGED')
    props=dict(x.split('=',1) for x in subprocess.check_output(['systemctl','show',UNIT.name,
        '--property=ActiveState,MainPID,ControlGroup'],text=True).splitlines())
    require(props.get('ActiveState') in {'inactive','failed'} and props.get('MainPID')=='0'
        and props.get('ControlGroup')=='' and set(props)=={'ActiveState','MainPID','ControlGroup'},'AUTHOR_UPGRADE_ACTIVE')
    _contract.held_application()
    check="""import os,sqlite3,json
from pathlib import Path
assert os.getuid()==os.getgid()==1003
p=Path('/var/lib/research-system-manual-sprint10/releases/research-manual-sprint10-timeout-continuation-8e042339/item4/lane')
with sqlite3.connect((p/'jobs.sqlite').as_uri()+'?mode=ro',uri=True) as db:
 v=json.loads(db.execute('SELECT payload FROM manual_state WHERE id=1').fetchone()[0])
 assert v['phase']=='BLOCKED' and v['reason']=='UNRESOLVED_AFTER_THREE_REVISIONS' and not v.get('pending') and v['rounds']=={'run_spec_author':11,'run_spec_review':6}
 assert db.execute('SELECT count(*) FROM manual_calls').fetchone()[0]==17
with sqlite3.connect('file:/var/lib/research-system-autonomy/reviews/jobs.sqlite?mode=ro',uri=True) as db:
 assert not db.execute("SELECT 1 FROM autonomy_calls WHERE status='RUNNING'").fetchone()
print('HELD_REVIEW6_NO_RUNNING_CALL')
"""
    require(subprocess.check_output(['runuser','-u','partho','--','python3','-s','-B','-c',check],text=True).strip()==
        'HELD_REVIEW6_NO_RUNNING_CALL','AUTHOR_UPGRADE_RECONCILIATION')
    history=RECORD/'history'/old['source'];staged=RECORD/('upgrade-staged-'+source)
    require(not history.exists() and not staged.exists(),'AUTHOR_UPGRADE_EXISTS_RECONCILE')
    put(history/'UPGRADE_INTENT.json',json.dumps({'source':source,'review':approved,
        'prior':old,'scope':'same unit, lane, state and accounting; no model/provider calls'},sort_keys=True).encode())
    for name in prior.FILES:put(history/'source'/name,trusted(ROOT/name).read_bytes())
    for name in ('installed.json','APPLIED.json'):put(history/name,trusted(RECORD/name).read_bytes())
    for row in manifest['files']:put(history/'evidence'/row['name'],trusted(RECORD/'evidence'/row['name']).read_bytes())
    for name,raw in bodies.items():put(staged/'source'/name,raw)
    for name,raw in evidence_bodies.items():put(staged/'evidence'/name,raw)
    for path in Path(review).iterdir():
        require(path.is_file() and not path.is_symlink(),'AUTHOR_UPGRADE_REVIEW_TYPE')
        put(staged/'review'/path.name,path.read_bytes())
    updated={**old,'source':source,'review_sha256':approved['report_sha256'],
        'files':{name:sha(raw) for name,raw in bodies.items()},'previous_source':old['source']}
    put(staged/'installed.json',json.dumps(updated,sort_keys=True).encode())
    for name in bodies:os.replace(staged/'source'/name,ROOT/name)
    (RECORD/'review').rename(history/'original-review-directory')
    (RECORD/'evidence').rename(history/'original-evidence-directory')
    (staged/'review').rename(RECORD/'review');(staged/'evidence').rename(RECORD/'evidence')
    os.replace(staged/'installed.json',RECORD/'installed.json')
    for root in (RECORD/'review',RECORD/'evidence'):
        for path in (root,*[p for p in root.rglob('*') if p.is_dir()]):os.chown(path,0,1003);path.chmod(0o550)
    for root in (history.parent,staged):
        for path in (root,*[p for p in root.rglob('*') if p.is_dir()]):os.chown(path,0,1003);path.chmod(0o550)
    command=['runuser','-u','partho','--','env','PYTHONPATH='+str(SCIENCE),
        'RESEARCH_MANUAL_RUNTIME_CONFIG='+str(RUNTIME),'PYTHONDONTWRITEBYTECODE=1',
        'python3','-s','-B',str(ROOT/'tools/item4_scientific_revision_component.py'),'verify']
    result=subprocess.run(command,capture_output=True,text=True,timeout=180)
    put(history/'verify.stdout',result.stdout.encode());put(history/'verify.stderr',result.stderr.encode())
    require(result.returncode==0,'AUTHOR_UPGRADE_POSTCHECK')
    put(history/'UPGRADE_COMPLETE.json',b'{"status":"UPDATED_HELD","model_calls":0,"provider_calls":0}')
    return {'status':'UPDATED_HELD','model_calls':0,'provider_calls':0,'unit':UNIT.name}


def install(packet, review, source, evidence):
    require(os.getuid() == 0, 'AUTHOR_INSTALL_ROOT_REQUIRED')
    sys.path.insert(0,str(REVIEW_ENGINE))
    from orchestrator import autonomy_review as ar
    m=ar.verify_packet(packet);a=ar.verify_result(review)
    require(a['verdict']=='APPROVE' and a['source_sha']==m['source_sha']==source and
            a['change_id']==m['change_id']==_contract.REVIEW_CHANGE and a['runtime_sha256']==sha(trusted(RUNTIME).read_bytes()),
            'AUTHOR_INSTALL_GENUINE_APPROVAL_REQUIRED')
    require(ar.canonical(m)==ar.canonical(json.loads((Path(review)/'packet-manifest.json').read_bytes())), 'AUTHOR_INSTALL_REVIEW_PACKET_BINDING')
    bodies={name:(Path(packet)/'source'/name).read_bytes() for name in FILES}
    require(all(sha(raw)==m['source_files'][name] for name,raw in bodies.items()), 'AUTHOR_INSTALL_SOURCE_CHANGED')
    require(bodies['tools/install_item4_scientific_revision.py']==Path(__file__).read_bytes(), 'AUTHOR_INSTALLER_NOT_REVIEWED')
    require(sha(bodies['docs/AUTHOR_REVISE_ACCOUNTING_OPERATOR_DECISION_20261008.txt'])==AUTHORITY, 'AUTHOR_INSTALL_AUTHORITY')
    require(json.loads(bodies['docs/ITEM4_REVISION_CHECKPOINT.json'])['author_authority_sha256']==AUTHORITY, 'AUTHOR_INSTALL_AUTHORITY_BINDING')
    evidence_manifest=json.loads(bodies['docs/ITEM4_REVISION_EVIDENCE.json'])
    evidence_bodies={}
    for row in evidence_manifest['files']:
        require(Path(row['name']).name==row['name'], 'REVISION_EVIDENCE_NAME')
        path=Path(evidence)/row['name']
        require(path.is_file() and not path.is_symlink(), 'REVISION_EVIDENCE_REGULAR')
        raw=path.read_bytes()
        require(sha(raw)==row['sha256'] and len(raw)==row['bytes'], 'REVISION_EVIDENCE_CHANGED')
        evidence_bodies[row['name']]=raw
    if ROOT.exists():return upgrade(bodies, evidence_bodies, review, a, source)
    require(not RECORD.exists() and not UNIT.exists(), 'AUTHOR_INSTALL_EXISTS_INSPECT')
    properties=dict(x.split('=',1) for x in subprocess.check_output(['systemctl','show',OLD_UNIT.name,
        '--property=ActiveState,MainPID,ControlGroup'],text=True).splitlines())
    require(properties=={'ActiveState':'inactive','MainPID':'0','ControlGroup':''}, 'AUTHOR_EXISTING_SERVICE_ACTIVE')
    original=trusted(OLD_UNIT).read_bytes();unit=unit_bytes(original.decode())
    daily=Path('/opt/research-system/manual-repair-helpers/daily-limit-and-image-probe-20261007/tools/daily_limit_component.py')
    prior=Path('/opt/research-system/manual-repair-helpers/item4-review-evidence-paths-20261008/tools/item4_review_context_component.py')
    baseline=[daily,prior, *(SCIENCE/'orchestrator'/(name+'.py') for name in (
        'manual_stage','manual_isolation','manual_driver','manual_executor','experiment_driver',
        'experiment_plan_validation','experiment_plan_output','experiment_context','manual_context','experiment_approval','experiment_acceptance'))]
    pins={str(p):sha(trusted(p).read_bytes()) for p in baseline}
    trusted(ROOT.parent);trusted(RECORD.parent);trusted(UNIT.parent)
    # Every original unit, file and credential remains unchanged.
    ROOT.mkdir(mode=0o700);RECORD.mkdir(mode=0o700)
    put(RECORD/'INSTALL_INTENT.json',json.dumps({'source':source,'review':a,'scope':'held runtime binding and exact metadata delivery repair; no model or provider launch'},sort_keys=True).encode())
    for name,raw in bodies.items():put(ROOT/name,raw)
    for name,raw in evidence_bodies.items():put(RECORD/'evidence'/name,raw)
    for path in Path(review).iterdir():
        require(path.is_file() and not path.is_symlink(), 'AUTHOR_REVIEW_ORIGINAL_FILE')
        put(RECORD/'review'/path.name,path.read_bytes())
    put(RECORD/'prior-unit.txt',original)
    put(UNIT,unit);os.chown(UNIT,0,0);os.chmod(UNIT,0o644)
    receipt={'schema':'reviewed-scientific-revision/v1','root':str(ROOT),'source':source,
        'review_folder':str(RECORD/'review'),'review_sha256':a['report_sha256'],
        'files':{n:sha(raw) for n,raw in bodies.items()},'base_files':pins,
        'units':{str(OLD_UNIT):sha(original),str(UNIT):sha(unit)}}
    put(RECORD/'installed.json',json.dumps(receipt,sort_keys=True).encode())
    for root in [ROOT,RECORD]:
        for path in [root,*[p for p in root.rglob('*') if p.is_dir()]]:os.chown(path,0,1003);os.chmod(path,0o550)
    subprocess.run(['systemctl','daemon-reload'],check=True)
    command=['runuser','-u','partho','--','env','PYTHONPATH='+str(SCIENCE),
        'RESEARCH_MANUAL_RUNTIME_CONFIG='+str(RUNTIME),'PYTHONDONTWRITEBYTECODE=1',
        'python3','-s','-B',str(ROOT/'tools/item4_scientific_revision_component.py')]
    # Qualification precedes recovery; neither action launches a model.
    for action in ['verify','apply']:
        result=subprocess.run(command+[action],capture_output=True,text=True,timeout=180)
        put(RECORD/(action+'.stdout'),result.stdout.encode());put(RECORD/(action+'.stderr'),result.stderr.encode())
        require(result.returncode==0, 'AUTHOR_INSTALL_POSTCHECK_'+action.upper())
    put(RECORD/'APPLIED.json',json.dumps({'status':'INSTALLED_HELD','source':source,'review_sha256':a['report_sha256'],'model_calls':0},sort_keys=True).encode())
    return {'status':'INSTALLED_HELD','model_calls':0,'unit':UNIT.name}


if __name__=='__main__':
    os.umask(0o077)
    p=argparse.ArgumentParser();p.add_argument('--packet',type=Path,required=True);p.add_argument('--review',type=Path,required=True);p.add_argument('--source',required=True);p.add_argument('--evidence',type=Path,required=True);args=p.parse_args()
    print(json.dumps(install(args.packet,args.review,args.source,args.evidence),sort_keys=True))
