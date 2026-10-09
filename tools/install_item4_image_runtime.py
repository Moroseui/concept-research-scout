"""Install one independently approved image adapter, disabled and unspent."""
from pathlib import Path
import importlib.util
import json
import os
import sys
import stat


def load(path,name):
    spec=importlib.util.spec_from_file_location(name,path)
    result=importlib.util.module_from_spec(spec);spec.loader.exec_module(result);return result


STATE_PARENT=Path('/var/lib/research-system-manual-sprint10/environment-inventory')
STATE=STATE_PARENT/'item4-pinned-scientific-image-v1'


def destination_parent(path):
    from orchestrator.manual_host_guard import trusted
    parent=path.parent
    while not parent.exists():parent=parent.parent
    if path!=STATE:return trusted(parent)
    # Existing shared state is intentionally owned by the fixed service account;
    # all code/config/receipt/unit parents retain the original root-only check.
    if parent!=STATE_PARENT:raise ValueError('IMAGE_STATE_PARENT_MISSING')
    for p,uid,gid,mode in [(STATE_PARENT,0,1003,0o750),(STATE_PARENT.parent,1003,1003,0o700)]:
        info=p.lstat()
        if (p.is_symlink() or not stat.S_ISDIR(info.st_mode) or
                (info.st_uid,info.st_gid,stat.S_IMODE(info.st_mode))!=(uid,gid,mode)):
            raise ValueError('IMAGE_STATE_PARENT_CHANGED')
    trusted(STATE_PARENT.parent.parent)
    return parent


def upgrade(contract,raw,review,approved,source,config):
    """Replace only the reviewed helper after an unreserved admission refusal."""
    import subprocess
    from orchestrator.manual_host_guard import trusted
    from orchestrator.manual_executor import digest
    require=contract.require
    prior=load(trusted(contract.ROOT/'tools/item4_image_runtime.py'),'_prior_image_adapter')
    prior.verify()
    old=json.loads(trusted(contract.RECORD/'installed.json').read_bytes())
    require(old['source']=='94be84ee3406996a397ba7ac57b7c681da5ca660','IMAGE_UPGRADE_PRIOR_SOURCE')
    require(json.loads(raw[contract.FILES[-2]])=={k:v for k,v in json.loads(trusted(contract.CONFIG).read_bytes()).items() if k!='units'},
        'IMAGE_UPGRADE_SELECTION_CHANGED')
    unit='research-manual-sprint10-image-a51ac44279e4.service'
    props=dict(x.split('=',1) for x in subprocess.check_output(['systemctl','show',unit,'-p','ActiveState','-p','MainPID'],text=True).splitlines())
    require(props['MainPID']=='0' and props['ActiveState'] in {'inactive','failed'},'IMAGE_UPGRADE_ACTIVE')
    # SQLite is opened read-only by its existing service owner, never by root.
    check="""from pathlib import Path
import sqlite3,os,json
assert os.getuid()==os.getgid()==1003
p=Path('/var/lib/research-system-manual-sprint10/environment-inventory/item4-pinned-scientific-image-v1')
assert not (p/'provider').exists() and not (p/'STATUS.json').exists()
with sqlite3.connect('file:/var/lib/research-system-autonomy/reviews/jobs.sqlite?mode=ro',uri=True) as db:
 assert not any(json.loads(x[0]).get('purpose')=='M4_ITEM4_PINNED_IMAGE_BUILD' for x in db.execute('SELECT binding FROM autonomy_assets'))
print('UNRESERVED_NO_PROVIDER_INTENT')
"""
    require(subprocess.check_output(['runuser','-u','partho','--','python3','-s','-B','-c',check],text=True).strip()=='UNRESERVED_NO_PROVIDER_INTENT',
        'IMAGE_UPGRADE_RECONCILE')
    history=contract.RECORD/'history'/old['source']
    require(not history.exists(),'IMAGE_UPGRADE_EXISTS_RECONCILE')
    def put(path,value):
        path.parent.mkdir(parents=True,exist_ok=True,mode=0o700)
        with path.open('xb') as f:f.write(value)
        os.chown(path,0,1003);path.chmod(0o440)
    put(history/'UPGRADE_INTENT.json',json.dumps({'source':source,'review':approved,'prior':old,'scope':'same unit/config/state, no reservations/provider calls'}).encode())
    for name in prior.FILES:put(history/'source'/name,trusted(contract.ROOT/name).read_bytes())
    for name in ('installed.json','COMPLETE.json','START_INTENT.json','RETRY_AUTHOR5_START_INTENT.json'):put(history/name,trusted(contract.RECORD/name).read_bytes())
    for p in trusted(contract.RECORD/'review').iterdir():
        require(p.is_file() and not p.is_symlink(),'IMAGE_UPGRADE_PRIOR_REVIEW_TYPE');put(history/'review'/p.name,trusted(p).read_bytes())
    staged=contract.RECORD/('upgrade-staged-'+source);require(not staged.exists(),'IMAGE_UPGRADE_STAGED_EXISTS')
    for name,value in raw.items():put(staged/'source'/name,value)
    for p in review.iterdir():
        require(p.is_file() and not p.is_symlink(),'IMAGE_UPGRADE_REVIEW_TYPE');put(staged/'review'/p.name,p.read_bytes())
    record={**old,'source':source,'review_sha256':approved['report_sha256'],'previous_source':old['source']}
    put(staged/'installed.json',json.dumps(record,sort_keys=True).encode())
    for name in raw:
        target=contract.ROOT/name;target.parent.mkdir(parents=True,exist_ok=True,mode=0o700)
        os.replace(staged/'source'/name,target)
    (contract.RECORD/'review').rename(history/'original-review-directory')
    (staged/'review').rename(contract.RECORD/'review')
    os.replace(staged/'installed.json',contract.RECORD/'installed.json')
    load(contract.ROOT/'tools/item4_image_runtime.py','_updated_image_adapter').verify()
    put(history/'UPGRADE_COMPLETE.json',b'{"status":"UPDATED_HELD","provider_calls":0,"model_calls":0}')
    for root in (history.parent,staged,contract.RECORD/'review',contract.ROOT):
        for p in [root,*[v for v in root.rglob('*') if v.is_dir()]]:os.chown(p,0,1003);p.chmod(0o550)
    return {'status':'UPDATED_HELD','unit':unit,'model_calls':0,'provider_calls':0}


def install(packet,review,source):
    from orchestrator.autonomy_review import verify_packet,verify_result,canonical
    from orchestrator.manual_host_guard import trusted
    from orchestrator.manual_executor import digest
    from tools.manual_promotion import manifest_check
    contract=load(Path(__file__).with_name('item4_image_runtime.py'),'_image_contract')
    require=contract.require
    require(os.getuid()==0,'IMAGE_ADAPTER_INSTALL_ROOT')
    packet=Path(packet);review=Path(review);manifest=verify_packet(packet);approved=verify_result(review)
    require(approved['verdict']=='APPROVE' and approved['change_id']==manifest['change_id']==contract.REVIEW_CHANGE
        and approved['source_sha']==manifest['source_sha']==source,'IMAGE_ADAPTER_INSTALL_APPROVAL')
    require(canonical(manifest)==canonical(json.loads((review/'packet-manifest.json').read_bytes())),
        'IMAGE_ADAPTER_INSTALL_PACKET_BINDING')
    raw={n:(packet/'source'/n).read_bytes() for n in contract.FILES}
    require(all(digest(v)==manifest['source_files'][n] for n,v in raw.items()),'IMAGE_ADAPTER_SOURCE_CHANGED')
    require(raw['tools/install_item4_image_runtime.py']==Path(__file__).read_bytes()
        and raw['tools/item4_image_runtime.py']==Path(contract.__file__).read_bytes(),'IMAGE_ADAPTER_EXECUTED_SOURCE')
    require(digest(raw[contract.FILES[-1]])==contract.AUTHORITY,'IMAGE_ADAPTER_AUTHORITY')
    base=manifest_check(Path('/'),str(contract.BASE_RECORD))
    config=json.loads(raw[contract.FILES[-2]])
    require(config['release']==str(contract.BASE) and config['installation_record']==str(contract.BASE_RECORD)
        and base['source']==config['source'] and base['layout']['release']==config['release']
        and digest(trusted(contract.BASE_RECORD/'installed.json').read_bytes())==config['installation_sha256'],
        'IMAGE_ADAPTER_BASE_BINDING')
    runtime=Path('/etc/research-system-manual-sprint10/releases/research-manual-sprint10-timeout-continuation-8e042339/runtime.json')
    require(approved['runtime_sha256']==digest(trusted(runtime).read_bytes()),'IMAGE_ADAPTER_REVIEW_RUNTIME')
    from orchestrator.modal_environment_inventory import selection,unit_name
    selection({**config,'units':{}})
    if contract.ROOT.exists():return upgrade(contract,raw,review,approved,source,config)
    targets=[contract.ROOT,contract.RECORD,contract.CONFIG.parent,Path(config['state']),Path('/etc/systemd/system')/unit_name(config)]
    require(all(not p.exists() and not p.is_symlink() for p in targets),'IMAGE_ADAPTER_EXISTS_RECONCILE')
    for path in targets:destination_parent(path)
    def put(path,value):
        path.parent.mkdir(parents=True,exist_ok=True,mode=0o700)
        with path.open('xb') as f:f.write(value)
        os.chown(path,0,1003);path.chmod(0o440)
    contract.ROOT.mkdir(mode=0o700);contract.RECORD.mkdir(mode=0o700)
    put(contract.RECORD/'INSTALL_INTENT.json',json.dumps({'source':source,'review':approved,'scope':'disabled image service only'}).encode())
    for name,value in raw.items():put(contract.ROOT/name,value)
    for p in review.iterdir():
        require(p.is_file() and not p.is_symlink(),'IMAGE_ADAPTER_REVIEW_FILE')
        put(contract.RECORD/'review'/p.name,p.read_bytes())
    installer=load(contract.ROOT/'tools/environment_inventory_service.py','_reviewed_environment_installer')
    result=installer.install(Path('/'),config)
    put(contract.RECORD/'installed.json',json.dumps({'source':source,'review_sha256':approved['report_sha256'],
        'base_receipt_sha256':config['installation_sha256'],'config_sha256':digest(trusted(contract.CONFIG).read_bytes()),
        'result':result,'model_calls':0,'provider_calls':0},sort_keys=True).encode())
    for root in (contract.ROOT,contract.RECORD):
        for p in [root,*[v for v in root.rglob('*') if v.is_dir()]]:os.chown(p,0,1003);p.chmod(0o550)
    load(contract.ROOT/'tools/item4_image_runtime.py','_installed_image_adapter').verify()
    put(contract.RECORD/'COMPLETE.json',b'{"status":"INSTALLED_DISABLED","model_calls":0,"provider_calls":0}')
    return {'status':'INSTALLED_DISABLED','unit':unit_name(config),'model_calls':0,'provider_calls':0}


if __name__=='__main__':
    import argparse
    os.umask(0o077)
    parser=argparse.ArgumentParser();parser.add_argument('--packet',required=True);parser.add_argument('--review',required=True);parser.add_argument('--source',required=True)
    args=parser.parse_args();print(json.dumps(install(args.packet,args.review,args.source),sort_keys=True))
