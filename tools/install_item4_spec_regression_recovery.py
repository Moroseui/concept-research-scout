"""Install an independently approved recovery, held. Never apply it here."""
from pathlib import Path
import argparse,hashlib,importlib.util,json,os,subprocess,sys
ENGINE=Path('/opt/research-system/autonomy-review/d08b91bdc1d0')

def require(ok,why):
    if not ok:raise ValueError('SPEC_RECOVERY_INSTALL_'+why)
def sha(raw):return hashlib.sha256(raw).hexdigest()
def put(path,raw):
    path.parent.mkdir(mode=0o700,parents=True,exist_ok=True)
    with path.open('xb') as f:f.write(raw)
    os.chown(path,0,1003);path.chmod(0o440)

def install(packet,review,source):
    require(os.getuid()==0,'ROOT_REQUIRED');sys.path.insert(0,str(ENGINE))
    from orchestrator import autonomy_review as ar
    packet,review=Path(packet),Path(review)
    m=ar.verify_packet(packet);a=ar.verify_result(review)
    require(a['verdict']=='APPROVE' and a['source_sha']==m['source_sha']==source
            and a['change_id']==m['change_id']=='item4-spec-regression-recovery-20261010','GENUINE_APPROVE')
    require(ar.canonical(m)==ar.canonical(json.loads((review/'packet-manifest.json').read_bytes())),'REVIEW_PACKET')
    name='tools/install_item4_spec_regression_recovery.py'
    require((packet/'source'/name).read_bytes()==Path(__file__).read_bytes(),'REVIEWED_INSTALLER')
    entry=packet/'source/tools/item4_spec_regression_recovery.py'
    require(sha(entry.read_bytes())==m['source_files']['tools/item4_spec_regression_recovery.py'],'REVIEWED_RUNTIME')
    spec=importlib.util.spec_from_file_location('_recovery_constants',entry);r=importlib.util.module_from_spec(spec);spec.loader.exec_module(r)
    require(a['runtime_sha256']==sha(r.trusted(r.RUNTIME).read_bytes()),'RUNTIME_CHANGED')
    bodies={n:(packet/'source'/n).read_bytes() for n in r.FILES}
    require(all(sha(raw)==m['source_files'][n] for n,raw in bodies.items()),'REVIEWED_FILES')
    require(sha(bodies[r.DOC])==r.BINDING,'FROZEN_SCOPE')
    b=json.loads(bodies[r.DOC])
    require(sha(r.trusted(r.PRIOR).read_bytes())==b['prior_runtime_sha256'],'PRIOR_RUNTIME')
    require(sha(bodies[r.FILES[-1]])==b['operator_decision_sha256'],'OPERATOR_AUTHORITY')
    r.stopped()
    require(not r.ROOT.exists() and not r.RECORD.exists(),'EXISTS_RECONCILE')
    r.trusted(r.ROOT.parent);r.trusted(r.RECORD.parent)
    r.ROOT.mkdir(mode=0o700);r.RECORD.mkdir(mode=0o700)
    put(r.RECORD/'INSTALL_INTENT.json',ar.canonical({'source':source,'review':a,'status':'INSTALLING_HELD'}))
    for n,raw in bodies.items():put(r.ROOT/n,raw)
    for p in review.iterdir():
        require(p.is_file() and not p.is_symlink(),'REVIEW_ORIGINAL');put(r.RECORD/'review'/p.name,p.read_bytes())
    put(r.RECORD/'installed.json',ar.canonical({'schema':'reviewed-spec-regression-recovery/v1','root':str(r.ROOT),
        'source':source,'review_folder':str(r.RECORD/'review'),'review_sha256':a['report_sha256'],
        'files':{n:sha(raw) for n,raw in bodies.items()}}))
    for root in (r.ROOT,r.RECORD):
        for p in [root,*[p for p in root.rglob('*') if p.is_dir()]]:os.chown(p,0,1003);p.chmod(0o550)
    # Existing service account and runtime; no unit, credential or live-state change.
    command=['runuser','-u','partho','--','env','RESEARCH_MANUAL_RUNTIME_CONFIG='+str(r.RUNTIME),
        'PYTHONDONTWRITEBYTECODE=1','python3','-s','-B',str(r.ROOT/r.FILES[0]),'verify']
    result=subprocess.run(command,capture_output=True,timeout=180)
    put(r.RECORD/'VERIFY.stdout',result.stdout);put(r.RECORD/'VERIFY.stderr',result.stderr)
    require(result.returncode==0,'VERIFICATION_FAILED_HELD')
    put(r.RECORD/'COMPLETE.json',ar.canonical({'status':'INSTALLED_HELD','source':source,
        'review_sha256':a['report_sha256'],'model_calls':0,'provider_calls':0}))
    return {'status':'INSTALLED_HELD','source':source,'model_calls':0,'provider_calls':0}

if __name__=='__main__':
    os.umask(0o077)
    p=argparse.ArgumentParser();p.add_argument('--packet',required=True);p.add_argument('--review',required=True);p.add_argument('--source',required=True)
    a=p.parse_args();print(json.dumps(install(a.packet,a.review,a.source),sort_keys=True))
