"""Held revision of one reviewed helper, preserving state and every original.

Runs under existing a51 imports. No provider, scientific call or ledger mutation.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
from orchestrator import autonomy_review as review
from orchestrator.manual_host_guard import trusted
from tools.spending_repair_service import owner_preflight

ROOT=Path('/opt/research-system/manual-repair-helpers/item6-input-provisioning-20261007')
RECORD=Path('/var/lib/research-system-manual-sprint10-deployment/item6-input-provisioning-20261007')
CHECKPOINT=Path('/var/lib/research-system-manual-sprint10-deployment/item6-billing-clock-20261008')
RELEASE='/opt/research-system/manual-sprint10/research-manual-sprint10-spending-a51ac44279e4'
TARGET='tools/item6_input_preparation.py'
OLD_PINS={'installed.json':'fbbb2df076d451363357d12801fc57bef54514ecf4a864f38b883d485f820e5e',
          'FILES.json':'24508f19963ed2e6c3fe96ef177f33b1204c27081006d127247120070d9e4584',
          'complete.json':'9952189f22a2896b8b0b81d018f206f0a0244e289f1add48a7e29b9b58558fc4'}
INVOCATION='402e2a33c9e84f6ca05db0dded08b825'

def require(ok,why):
    if not ok:raise ValueError(why)

def sha(raw):return hashlib.sha256(raw).hexdigest()
def encoded(v):return (json.dumps(v,sort_keys=True,indent=2)+'\n').encode()

def replacements(original,listing,body,commit,folder,approved):
    """Change only the source pin and genuine new approval metadata."""
    files=json.loads(json.dumps(listing));path=str(ROOT/TARGET)
    require(path in files and len(files)==14,'CLOCK_INSTALL_FILE_SET')
    files[path]['sha256']=sha(body)
    rec=dict(original)
    rec.update(change='item6-billing-clock-20261008',source=commit,review_folder=str(folder),review_sha256=approved['report_sha256'],
               files_sha256=sha(encoded(files)))
    return files,rec

def fresh_owner_check(runtime):
    script='import sys,json;sys.path.insert(0,sys.argv[1]);import item6_input_service as s;c,o,r=s.verify_installed();print(json.dumps({"status":"PASS","source":r["source"]}))'
    return json.loads(subprocess.check_output(['runuser','-u','partho','--','env','PYTHONPATH='+RELEASE,
        'RESEARCH_MANUAL_RUNTIME_CONFIG='+runtime,'/usr/bin/python3','-s','-B','-c',script,str(ROOT/'tools')],text=True))

def install(source,commit,folder,authority):
    require(os.getuid()==os.geteuid()==0,'CLOCK_INSTALL_ROOT_ONLY')
    source=trusted(Path(source));folder=trusted(Path(folder));authority=trusted(Path(authority))
    require(not CHECKPOINT.exists(),'CLOCK_INSTALL_EXISTS_RECONCILE')
    trusted(CHECKPOINT.parent)
    require(subprocess.check_output(['git','rev-parse','HEAD'],cwd=source,text=True).strip()==commit
            and not subprocess.check_output(['git','status','--porcelain'],cwd=source),'CLOCK_INSTALL_CLEAN_SOURCE')
    approved=review.verify_result(folder);manifest=json.loads((folder/'packet-manifest.json').read_bytes())
    require(approved['verdict']=='APPROVE' and not approved.get('findings') and approved['source_sha']==commit,
            'CLOCK_INSTALL_GENUINE_APPROVAL')
    for name in [TARGET,'tools/install_item6_billing_clock.py','docs/OPERATOR_ENGINEERING_RULE_20261007.txt']:
        require(sha((source/name).read_bytes())==manifest['source_files'][name],'CLOCK_INSTALL_REVIEWED_SOURCE')
    require(Path(__file__).read_bytes()==(source/'tools/install_item6_billing_clock.py').read_bytes(),
            'CLOCK_INSTALL_EXECUTED_SOURCE')
    require(authority.read_bytes()==(source/'docs/OPERATOR_ENGINEERING_RULE_20261007.txt').read_bytes(),
            'CLOCK_INSTALL_OPERATOR_AUTHORITY')
    originals={name:trusted(RECORD/name).read_bytes() for name in OLD_PINS}
    require(all(sha(raw)==OLD_PINS[name] for name,raw in originals.items()),'CLOCK_INSTALL_ORIGINAL_CHANGED')
    sys.path.insert(0,str(ROOT/'tools'));import item6_input_service as service
    config,old,rec=service.verify_installed()
    require(approved['change_id']=='item6-billing-clock-20261008' and approved['runtime_sha256']==service.sc.RUNTIME,
            'CLOCK_INSTALL_APPROVAL_SCOPE')
    require(rec['source']=='1c3e3566fe7f5c2a747e296892638c168a805bbd','CLOCK_INSTALL_BASE_SOURCE')
    listing=json.loads(originals['FILES.json']);old_body=trusted(ROOT/TARGET).read_bytes()
    require(len(listing)==14 and sha(old_body)==listing[str(ROOT/TARGET)]['sha256'],'CLOCK_INSTALL_BASE_FILE')
    body=(source/TARGET).read_bytes()
    # The remaining installed helper source files must be exactly review-covered.
    for name in service.FILES:
        require(sha(body if name==TARGET else trusted(ROOT/name).read_bytes())==manifest['source_files'][name],
                'CLOCK_INSTALL_REMAINING_REVIEWED_SOURCE')
    for command in ('allocate','finalize','execute'):
        unit=service.UNIT+'-'+command+'.service'
        props=dict(x.split('=',1) for x in subprocess.check_output(['systemctl','show',unit,
            '--property=ActiveState,MainPID,ControlGroup,ExecMainStatus,InvocationID'],text=True).splitlines())
        require(props['ActiveState'] in {'inactive','failed'} and props['MainPID']=='0' and props['ControlGroup']=='',
                'CLOCK_INSTALL_UNIT_ACTIVE')
        if command=='allocate':require(props['ActiveState']=='failed' and props['ExecMainStatus']=='1'
            and props['InvocationID']==INVOCATION,'CLOCK_INSTALL_FAILED_ATTEMPT_CHANGED')
    require(subprocess.check_output(['systemctl','is-active',service.UNIT+'-cleanup.timer'],text=True).strip()=='active',
            'CLOCK_INSTALL_RETENTION_REQUIRED')
    state=Path(config['state'])
    require(not any((state/n).exists() for n in ['binding.json','allocate-intent.json','upload-intent.json']),
            'CLOCK_INSTALL_PREPARATION_ALREADY_ATTEMPTED')
    staged=(state/'STAGED.json').read_bytes();require(json.loads(staged)['status']=='STAGED','CLOCK_INSTALL_STAGING_REQUIRED')
    journal=subprocess.check_output(['journalctl','--no-pager','-o','cat','_SYSTEMD_INVOCATION_ID='+INVOCATION])
    require(b'MODAL_BILLING_SNAPSHOT_STALE' in journal and b'headroom' in journal,'CLOCK_INSTALL_ORIGINAL_FAILURE_REQUIRED')
    before=owner_preflight(RELEASE,old['previous'],continued=True)
    require(fresh_owner_check(old['previous']['runtime'])['source']==rec['source'],'CLOCK_INSTALL_OWNER_PRECHECK')
    files,newrec=replacements(rec,listing,body,commit,folder,approved)
    CHECKPOINT.mkdir(mode=0o750);os.chown(CHECKPOINT,0,1003)
    def save(path,raw):
        with path.open('xb') as f:f.write(raw);f.flush();os.fsync(f.fileno())
        os.chown(path,0,1003);path.chmod(0o440)
    for name,raw in {**originals,'original-source.py':old_body,'original-journal.txt':journal,
                     'operator-authority.txt':authority.read_bytes(),'STAGED.original.json':staged}.items():save(CHECKPOINT/name,raw)
    save(CHECKPOINT/'intent.json',encoded({'source':commit,'review_sha256':approved['report_sha256'],
        'before':before,'original_attempt':INVOCATION,'no_automatic_retry':True}))
    def replace(path,raw):
        temporary=path.with_name(path.name+'.clock-revision-pending');save(temporary,raw);os.replace(temporary,path)
    # Native verification refuses every incomplete/interrupted intermediate state.
    replace(RECORD/'complete.json',encoded({'status':'INSTALLING','checkpoint':str(CHECKPOINT)}))
    replace(ROOT/TARGET,body);replace(RECORD/'FILES.json',encoded(files));replace(RECORD/'installed.json',encoded(newrec))
    after=owner_preflight(RELEASE,old['previous'],continued=True)
    require(before==after and (state/'STAGED.json').read_bytes()==staged,'CLOCK_INSTALL_EXISTING_STATE_CHANGED')
    for name,pin in files.items():
        path=trusted(name);require(sha(path.read_bytes())==pin['sha256'] and path.stat().st_mode&0o777==pin['mode'],
                                   'CLOCK_INSTALL_FILE_VERIFICATION')
    complete={'status':'PASS','before':before,'after':after,'provider_calls':0,'model_calls':0,
              'checkpoint':str(CHECKPOINT),'source':commit,'review_sha256':approved['report_sha256'],'held':True}
    replace(RECORD/'complete.json',encoded(complete))
    try:
        result=fresh_owner_check(old['previous']['runtime']);require(result['source']==commit,'CLOCK_INSTALL_OWNER_POSTCHECK')
    except BaseException:
        replace(RECORD/'complete.json',encoded({'status':'FAILED_POSTCHECK','checkpoint':str(CHECKPOINT)}))
        raise
    save(CHECKPOINT/'APPLIED.json',encoded(complete))
    return {'status':'INSTALLED_HELD','source':commit,'existing_state_preserved':True}

def main():
    parser=argparse.ArgumentParser()
    for name in ('source','commit','review-folder','authority'):parser.add_argument('--'+name,required=True)
    a=parser.parse_args();print(json.dumps(install(a.source,a.commit,a.review_folder,a.authority),sort_keys=True))

if __name__=='__main__':main()
