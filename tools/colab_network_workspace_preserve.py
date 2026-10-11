"""One exact pre-admission workspace preservation; finish unchanged held install."""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys

CHANGE='colab-workspace-native-inspection-recovery-20261011'
DOC='docs/COLAB_NETWORK_WORKSPACE_PRIVATE.json'
DOC_SHA='86c54e3f3dc70a943bc632c92a1e3f8214a38831d09af7a683a5a9867dbb1b39'
ROOT=Path('/opt/research-system/manual-repair-helpers/colab-network-continuation-20261011')
RECORD=Path('/var/lib/research-system-manual-sprint10-deployment/colab-network-continuation-20261011')
LANE=Path('/var/lib/research-system-manual-sprint10-deployment/colab-preparation-20261010/lane')
DEST=LANE/'network-preflight-preservation-20261011'
ORIGINAL=Path('/opt/research-system/manual-repair-helpers/preparation-and-cap-repair-20261010')
ENTRY='tools/colab_network_workspace_preserve.py'

def require(ok,why):
    if not ok:raise ValueError('COLAB_NETWORK_PRESERVE_'+why)
def sha(raw):return hashlib.sha256(raw).hexdigest()
def canonical(value):return json.dumps(value,sort_keys=True).encode()
def trusted(path):
    p=Path(path)
    for q in [p,*p.parents]:
        st=q.lstat();require(not q.is_symlink() and st.st_uid==0 and not st.st_mode&0o022,'TRUSTED_PATH')
    return p

def verified(review):
    require(sys.flags.no_user_site,'ISOLATED_PYTHON')
    sys.path.insert(0,str(ORIGINAL))
    from orchestrator.autonomy_review import verify_result
    approval=verify_result(trusted(review));manifest=json.loads(trusted(Path(review)/'packet-manifest.json').read_bytes())
    require(approval['verdict']=='APPROVE' and not approval.get('findings') and approval['change_id']==CHANGE,'GENUINE_APPROVAL')
    here=trusted(__file__);doc=trusted(here.parents[1]/DOC).read_bytes()
    require(sha(here.read_bytes())==manifest['source_files'][ENTRY] and sha(doc)==DOC_SHA==manifest['source_files'][DOC],'REVIEWED_BYTES')
    path=trusted(ROOT/'tools/colab_intake_identity_runtime.py')
    spec=importlib.util.spec_from_file_location('_preserved_colab_partial',path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
    previous=m.authority(held=False);b=json.loads(doc)
    require(previous['source_sha']==b['prior_source'] and previous['report_sha256']==b['prior_review']
            and previous['change_id']=='timing-entrypoint-colab-network-recovery-20261011'
            and approval['runtime_sha256']==previous['runtime_sha256'],'PARTIAL_INSTALL_BINDING')
    require(not (RECORD/'COMPLETE.json').exists(),'ALREADY_COMPLETE')
    m.network_predecessor()
    for unit in ['research-colab-network-continuation-20261011.service','research-held-colab-network-install-c4280f2-20261011.service']:
        state=dict(x.split('=',1) for x in subprocess.check_output(['systemctl','show',unit,'-p','MainPID','-p','ActiveState'],text=True).splitlines())
        require(state['MainPID']=='0' and state['ActiveState'] in {'inactive','failed'},'LIVE_WRITER')
    return m,b,approval

def preserve(review):
    require(os.getuid()==os.getgid()==1003,'SERVICE_OWNER')
    m,b,approval=verified(review);r=m.recovery()
    from orchestrator import private_records as pr
    from orchestrator.remote_supervisor import lock
    work=Path(b['workspace'])
    require(work==Path(r.binding()['workspace']),'EXACT_WORKSPACE')
    require(not DEST.exists() and not DEST.is_symlink(),'ORIGINAL_ATTEMPT_PRESERVED')
    require(not (LANE/'HALT').exists() and not (r.LEDGER.parent/'HALT').exists(),'HALT_PRESERVED')
    with lock(LANE/'one-run.lock'),lock(LANE/'driver.lock'):
        before=r.rows(Path('/'))
        require(sha(canonical(before))==b['rows_sha256'],'ORIGINAL_ROWS_CHANGED')
        require(r.inventory(work)==b['inventory'] and sha(canonical(b['inventory']))==b['inventory_sha256'],'WORKSPACE_CHANGED')
        pr.mkdir(DEST)
        pr.write_bytes(DEST/'INTENT.json',canonical({'review_sha256':approval['report_sha256'],'binding_sha256':DOC_SHA,'rows_sha256':b['rows_sha256']}))
        pr.write_bytes(DEST/'original-rows.json',canonical(before))
        # Rename all exact bytes, including preparation receipts. Never delete,
        # reuse, or alter an original workspace or model/accounting row.
        work.rename(DEST/'workspace')
        require(r.inventory(DEST/'workspace')==b['inventory'] and r.rows(Path('/'))==before,'PRESERVATION_READBACK')
        ready=r.ready()  # Original FRESH_PREPARATION_REQUIRED stays unchanged.
        value={'status':'PRESERVED_PREMODEL_WORKSPACE','binding_sha256':DOC_SHA,'review_sha256':approval['report_sha256'],
               'workspace_inventory_sha256':b['inventory_sha256'],'model_calls':0,'new_allowance':0,'original_ready':ready}
        pr.write_bytes(DEST/'COMPLETE.json',canonical(value));return value

def finish(review):
    require(os.getuid()==0,'ROOT_OWNER')
    m,b,approval=verified(review)
    # Exclusive root-side intent makes a crash stop for reconciliation, never
    # replay. The prior installer failure and VERIFY files are untouched.
    helper=m.load('_preservation_original_installer',m.BRANCH/'tools/install_preparation_branch_repair.py')
    helper.put(RECORD/'WORKSPACE_PRESERVATION_INTENT.json',canonical({'review_sha256':approval['report_sha256'],'binding_sha256':DOC_SHA}))
    env=['env','PYTHONPATH='+str(ORIGINAL),'PYTHONDONTWRITEBYTECODE=1','RESEARCH_MANUAL_RUNTIME_CONFIG='+str(m.RUNTIME)]
    result=subprocess.run(['runuser','-u','partho','--',*env,'python3','-s','-B',str(trusted(__file__)),'preserve','--review',str(trusted(review))],capture_output=True)
    helper.put(RECORD/'WORKSPACE_PRESERVATION.stdout',result.stdout);helper.put(RECORD/'WORKSPACE_PRESERVATION.stderr',result.stderr)
    require(result.returncode==0 and json.loads(result.stdout)['status']=='PRESERVED_PREMODEL_WORKSPACE','SERVICE_PRESERVATION_FAILED')
    result=subprocess.run(['runuser','-u','partho','--',*env,'python3','-s','-B',str(ROOT/m.ENTRY),'verify'],capture_output=True)
    helper.put(RECORD/'VERIFY_AFTER_PRESERVATION.stdout',result.stdout);helper.put(RECORD/'VERIFY_AFTER_PRESERVATION.stderr',result.stderr)
    require(result.returncode==0 and json.loads(result.stdout)=={'status':'VERIFIED_HELD','scientific_calls':0,'provider_calls':0},'SERVICE_VERIFY_FAILED')
    m.authority(held=False)
    complete={'status':'INSTALLED_HELD','source':b['prior_source'],'scientific_calls':0,'provider_calls':0}
    helper.put(RECORD/'COMPLETE.json',canonical(complete));m.authority()
    return complete

def main(argv=None):
    p=argparse.ArgumentParser();p.add_argument('action',choices=['preserve','finish']);p.add_argument('--review',type=Path,required=True);a=p.parse_args(argv)
    return preserve(a.review) if a.action=='preserve' else finish(a.review)

if __name__=='__main__':
    os.umask(0o077);print(json.dumps(main(),sort_keys=True))
