#!/usr/bin/env python3
"""New-lane-only installer and recorded rollback. Standard library, no models.

Default operation requires an explicit scratch root. Live use requires --live
and root, after separately verified old-state snapshot/hold and manual approval.
Install never controls old units. Rollback only restores the recorded unit set;
it never restores, deletes or migrates any database, receipt or pause file.
"""
import argparse
import hashlib
import io
import json
import os
from pathlib import Path, PurePosixPath
import pwd
import re
import shlex
import sqlite3
import subprocess
import tarfile
import tempfile

RELEASE='/opt/research-system/manual-sprint10/rc3'
STATE='/var/lib/research-system-manual-sprint10'
CONFIG='/etc/research-system/manual-sprint10'
DEPLOY='/var/lib/research-system-manual-sprint10-deployment/rc3'
UNITS=('research-manual-sprint10-rc3.service','research-manual-sprint10-rc3.timer')
TEMPLATE='deploy/manual-lane/'


def digest(raw):return hashlib.sha256(raw).hexdigest()
def sha(path):return digest(Path(path).read_bytes())
def read(path):return json.loads(Path(path).read_text())

def bound(root,name):
    root=Path(root).absolute();part=PurePosixPath(name)
    if not part.is_absolute() or '..' in part.parts:raise ValueError('ABSOLUTE_BOUND_PATH_REQUIRED')
    target=root.joinpath(*part.parts[1:])
    if any(p.is_symlink() for p in [target,*target.parents]):raise ValueError('PATH_ALIAS_REFUSED')
    if not target.is_relative_to(root):raise ValueError('PATH_ESCAPE')
    return target


def save_new(path,value,mode=0o600):
    raw=(json.dumps(value,sort_keys=True,indent=2)+'\n').encode() if not isinstance(value,bytes) else value
    with Path(path).open('xb') as f:f.write(raw)
    Path(path).chmod(mode)


def system(root,action,name=None):
    if name is not None and not re.fullmatch(r'research[-a-zA-Z0-9_.@]+\.(service|timer|socket)',name):raise ValueError('UNIT_NAME_REFUSED')
    if Path(root)!=Path('/'):
        path=bound(root,'/run/manual-deploy-test-units.json');data=read(path)
        item=data.setdefault('units',{}).setdefault(name,{'enabled':False,'active':False})
        if action=='state':return dict(item)
        if action=='definition':return bound(root,'/etc/systemd/system/'+name).read_bytes()
        data.setdefault('calls',[]).append([action,name])
        if action=='enable':item['enabled']=True
        elif action=='disable':item['enabled']=False
        elif action=='start':item['active']=True
        elif action=='stop':item['active']=False
        else:raise ValueError('UNSUPPORTED_UNIT_ACTION')
        path.write_text(json.dumps(data,sort_keys=True))
        return
    if action=='state':
        def status(command):return subprocess.run(['systemctl',command,name],capture_output=True,text=True).stdout.strip()
        enabled,active=status('is-enabled'),status('is-active')
        if enabled not in {'enabled','enabled-runtime','disabled','static','indirect','not-found'} or active not in {'active','inactive','failed','unknown'}:raise ValueError('UNIT_STATE_UNCERTAIN')
        return {'enabled':enabled in {'enabled','enabled-runtime'},'active':active=='active'}
    if action=='definition':return subprocess.check_output(['systemctl','cat',name])
    subprocess.run(['systemctl',action,name],check=True,capture_output=True)


def inventory(root,value):
    if set(value)!={'units','pause_files','databases','receipt_directories','logs','snapshot_verification'}:raise ValueError('OLD_INVENTORY_FIELDS')
    if not value['units'] or not value['pause_files'] or not value['databases'] or not value['receipt_directories']:raise ValueError('OLD_STATE_COVERAGE_REQUIRED')
    names=[]
    for item in value['units']:
        if set(item)!={'name','enabled','active','definition_sha256'} or type(item['enabled']) is not bool or type(item['active']) is not bool:raise ValueError('OLD_UNIT_RECORD')
        name=item['name']
        if name in names or name in UNITS:raise ValueError('OLD_NEW_UNIT_OVERLAP')
        names.append(name)
        if digest(system(root,'definition',name))!=item['definition_sha256']:raise ValueError('OLD_UNIT_DEFINITION_CHANGED')
    for key in ['pause_files','databases','receipt_directories','logs']:
        if not isinstance(value[key],list) or len(value[key])!=len(set(value[key])):raise ValueError('OLD_PATH_LIST')
        for name in value[key]:
            path=bound(root,name)
            if any(path.is_relative_to(bound(root,p)) or bound(root,p).is_relative_to(path) for p in [RELEASE,STATE,CONFIG,DEPLOY]):raise ValueError('OLD_NEW_PATH_OVERLAP')
    verification=value['snapshot_verification']
    if set(verification)!={'path','sha256'} or sha(bound(root,verification['path']))!=verification['sha256']:raise ValueError('VERIFIED_SNAPSHOT_BINDING_REQUIRED')
    if read(bound(root,verification['path'])).get('status')!='PASS':raise ValueError('OLD_SNAPSHOT_NOT_VERIFIED')
    return value


def tree_hashes(path):
    result={}
    for item in sorted(Path(path).rglob('*')):
        if item.is_symlink():raise ValueError('RECEIPT_OR_SOURCE_ALIAS')
        if item.is_file():result[str(item.relative_to(path))]=sha(item)
    return result


def database_rows(path):
    # Inspect an immutable byte capture, never open SQLite on the old path:
    # even a readonly WAL connection may create/update shared-memory read marks.
    path=Path(path);wal=Path(str(path)+'-wal')
    captured={path:path.read_bytes()}
    if wal.exists():captured[wal]=wal.read_bytes()
    if wal.exists()!=(wal in captured) or any(sha(p)!=digest(raw) for p,raw in captured.items()):raise ValueError('OLD_DATABASE_MOVED_DURING_CAPTURE')
    with tempfile.TemporaryDirectory(prefix='manual-db-check-') as temp:
        copy=Path(temp)/'database.sqlite'
        for original,raw in captured.items():save_new(copy if original==path else Path(str(copy)+'-wal'),raw)
        with sqlite3.connect(copy) as db:
            db.execute('BEGIN')
            if db.execute('PRAGMA integrity_check').fetchone()[0]!='ok':raise ValueError('OLD_DATABASE_INTEGRITY')
            statements=sorted(db.iterdump())
    return digest('\n'.join(statements).encode())


def old_state(root,old):
    result={'pause':{},'databases':{},'receipts':{},'logs':{}}
    for name in old['pause_files']:result['pause'][name]=sha(bound(root,name))
    for name in old['databases']:result['databases'][name]=database_rows(bound(root,name))
    for name in old['receipt_directories']:
        path=bound(root,name)
        if not path.is_dir():raise ValueError('RECEIPTS_DIRECTORY_REQUIRED')
        result['receipts'][name]=tree_hashes(path)
    for name in old['logs']:
        raw=bound(root,name).read_bytes();result['logs'][name]={'bytes':len(raw),'sha256':digest(raw)}
    return result


def verify_old(root,old,expected):
    inventory(root,old)
    observed=old_state(root,old)
    for key in ['pause','databases','receipts']:
        if observed[key]!=expected[key]:raise ValueError('OLD_STATE_CHANGED:'+key)
    for name,prefix in expected['logs'].items():
        path=bound(root,name)
        with path.open('rb') as f:original=f.read(prefix['bytes'])
        if path.stat().st_size<prefix['bytes'] or digest(original)!=prefix['sha256']:raise ValueError('OLD_LOG_NOT_APPEND_ONLY')
    return {'status':'PASS','pause':'unchanged','database_rows':'unchanged','receipts':'unchanged','logs':'original prefixes intact; append-only growth permitted'}


def verify_files(root,manifest):
    for name,item in manifest.items():
        path=bound(root,name)
        if not path.is_file() or sha(path)!=item['sha256'] or path.stat().st_mode&0o777!=item['mode']:raise ValueError('INSTALLED_FILE_CHANGED:'+name)
    source=tree_hashes(bound(root,RELEASE))
    expected={name[len(RELEASE)+1:]:item['sha256'] for name,item in manifest.items() if name.startswith(RELEASE+'/')}
    if source!=expected:raise ValueError('INSTALLED_SOURCE_INVENTORY_CHANGED')



def host_prerequisites(root,runtime=None):
    """Read-only host/account/runtime checks before any installation write."""
    if Path(root)!=Path('/'):return None
    if os.geteuid()!=0:raise ValueError('INSTALL_ROOT_REQUIRED')
    owner=pwd.getpwnam('partho')
    if owner.pw_uid<=0 or owner.pw_gid<=0:raise ValueError('SERVICE_ACCOUNT_REQUIRED')
    for name in ['/usr/bin/python3','/usr/bin/git','/usr/bin/systemctl','/usr/sbin/runuser','/usr/bin/bwrap']:
        if not Path(name).is_file() or not os.access(name,os.X_OK):raise ValueError('HOST_EXECUTABLE_MISSING:'+name)
    if not Path('/run/systemd/system').is_dir():raise ValueError('RUNNING_SYSTEMD_REQUIRED')
    if not Path('/etc/ssl/certs/ca-certificates.crt').is_file() or not Path('/etc/resolv.conf').is_file():
        raise ValueError('HOST_NETWORK_RUNTIME_MISSING')
    if runtime:
        for name in ['node','claude_root','codex_root']:
            if not Path(runtime[name]).exists():raise ValueError('HOST_TOOL_PACKAGE_MISSING:'+name)
        from orchestrator import manual_runtime
        manual_runtime.validate_packages(runtime)
        for family,pin in runtime.get('package_sha256',{}).items():
            observed=digest(json.dumps(manual_runtime.package_inventory(runtime[family+'_root']),sort_keys=True,separators=(',',':')).encode())
            if observed!=pin:raise ValueError('HOST_WHOLE_PACKAGE_CHANGED:'+family)
    return owner

def install(root,source,tag,commit,tag_object,review,review_sha,old_file):
    root,source=Path(root).absolute(),Path(source).absolute()
    def git(*args):return subprocess.check_output(['git','--no-optional-locks',*args],cwd=source).decode().strip()
    if git('status','--porcelain'):raise ValueError('CLEAN_SOURCE_REQUIRED')
    if not re.fullmatch(r'research-manual-sprint10-20260926-rc3',tag):raise ValueError('RC3_TAG_REQUIRED')
    if git('rev-parse','HEAD')!=commit or git('rev-parse','refs/tags/'+tag)!=tag_object or git('rev-parse',tag+'^{}')!=commit or git('cat-file','-t',tag_object)!='tag':raise ValueError('REVIEWED_TAG_COMMIT_BINDING')
    report=Path(review).read_bytes()
    if digest(report)!=review_sha or commit not in report.decode() or re.findall(r'^## Verdict: (.+?)\s*$',report.decode(),re.M)!=['APPROVE']:raise ValueError('EXACT_DEPLOY_REVIEW_REQUIRED')
    old=inventory(root,read(old_file));before=old_state(root,old)
    for item in old['units']:
        if system(root,'state',item['name'])!={'enabled':False,'active':False}:raise ValueError('OLD_UNITS_MUST_ALREADY_BE_HELD')
    names=[RELEASE,STATE,CONFIG,DEPLOY,*['/etc/systemd/system/'+u for u in UNITS]]
    for name in names:
        if bound(root,name).exists():raise ValueError('NEW_TARGET_ALREADY_EXISTS:'+name)
    for unit in UNITS:
        if system(root,'state',unit)!={'enabled':False,'active':False}:raise ValueError('NEW_UNIT_ALREADY_ENABLED_OR_ACTIVE')
        for folder in bound(root,'/etc/systemd/system').glob('*.*'):
            if folder.is_dir() and ((folder/unit).exists() or (folder/unit).is_symlink()):raise ValueError('NEW_UNIT_ENABLE_LINK_EXISTS')
    owner=host_prerequisites(root)
    # Full preflight and archive validation precede the first write.
    raw=subprocess.check_output(['git','archive','--format=tar',commit],cwd=source)
    source_files={}
    with tarfile.open(fileobj=io.BytesIO(raw)) as archive:
        members=archive.getmembers()
        for item in members:
            if PurePosixPath(item.name).is_absolute() or '..' in PurePosixPath(item.name).parts or not (item.isdir() or item.isfile()):raise ValueError('RELEASE_ARCHIVE_MEMBER_REFUSED')
        for name in [RELEASE,STATE,CONFIG,DEPLOY]:bound(root,name).mkdir(parents=True,mode=0o700)
        save_new(bound(root,DEPLOY+'/install-intent.json'),{'source':commit,'tag':tag,'tag_object':tag_object,'status':'STARTED_NO_BLIND_RETRY'})
        for item in members:
            target=bound(root,RELEASE+'/'+item.name)
            if item.isdir():target.mkdir(parents=True,exist_ok=True)
            else:
                target.parent.mkdir(parents=True,exist_ok=True)
                body=archive.extractfile(item).read();mode=0o555 if item.mode&0o111 else 0o444
                source_files[RELEASE+'/'+item.name]={'sha256':digest(body),'mode':mode}
                save_new(target,body,mode)
    for folder in sorted(bound(root,RELEASE).rglob('*'),reverse=True):
        if folder.is_dir():folder.chmod(0o555)
    bound(root,RELEASE).chmod(0o555)
    for name in ['repository','lane','lane-scientific-workspaces','inbox']:bound(root,STATE+'/'+name).mkdir(mode=0o700)
    if root==Path('/'):
        for folder in [bound(root,CONFIG),bound(root,STATE),*bound(root,STATE).iterdir()]:os.chown(folder,owner.pw_uid,owner.pw_gid)
    for unit in UNITS:
        path=bound(root,'/etc/systemd/system/'+unit);path.parent.mkdir(parents=True,exist_ok=True)
        save_new(path,bound(root,RELEASE+'/'+TEMPLATE+unit).read_bytes(),0o644)
    save_new(bound(root,DEPLOY+'/old-inventory.json'),old,0o444)
    save_new(bound(root,DEPLOY+'/old-invariants.json'),before,0o444)
    save_new(bound(root,DEPLOY+'/review.md'),report,0o444)
    # The rollback binds the old inventory and exact installed implementation.
    entry=bound(root,RELEASE+'/tools/deploy_manual_lane.py')
    args=['/usr/bin/python3','-B',str(entry),'rollback','--root',str(root),'--inventory-sha256',sha(bound(root,DEPLOY+'/old-inventory.json')),'--implementation-sha256',sha(entry)]
    if root==Path('/'):args+=['--live']
    shell='#!/usr/bin/env bash\nset -eu\nif [ "$#" -gt 1 ] || { [ "$#" -eq 1 ] && [ "$1" != --rehearsal ]; }; then echo "Only --rehearsal is accepted" >&2; exit 2; fi\nexec '+shlex.join(args)+' "$@"\n'
    save_new(bound(root,DEPLOY+'/rollback.sh'),shell.encode(),0o500)
    files=dict(source_files)
    for name in [DEPLOY]:
        for relative in tree_hashes(bound(root,name)):
            path=bound(root,name+'/'+relative);files[name+'/'+relative]={'sha256':sha(path),'mode':path.stat().st_mode&0o777}
    for unit in UNITS:
        name='/etc/systemd/system/'+unit;files[name]={'sha256':source_files[RELEASE+'/'+TEMPLATE+unit]['sha256'],'mode':0o644}
    save_new(bound(root,DEPLOY+'/FILES.json'),files,0o444)
    verify_files(root,files);preserved=verify_old(root,old,before)
    for unit in UNITS:
        if system(root,'state',unit)!={'enabled':False,'active':False}:raise ValueError('NEW_UNITS_NOT_HELD')
    receipt={'status':'PASS','source':commit,'tag_object':tag_object,'files_sha256':sha(bound(root,DEPLOY+'/FILES.json')),'files_checked':len(files),'old_state':preserved,'new_units':'installed, disabled, inactive','scope':'installation only; no login, lane initialization, model call or legacy control operation'}
    save_new(bound(root,DEPLOY+'/installed.json'),receipt,0o444)
    return receipt


def rollback(root,inventory_sha,implementation_sha,rehearsal=False):
    root=Path(root).absolute();entry=bound(root,RELEASE+'/tools/deploy_manual_lane.py')
    if sha(entry)!=implementation_sha or sha(bound(root,DEPLOY+'/old-inventory.json'))!=inventory_sha:raise ValueError('ROLLBACK_BINDING_CHANGED')
    files=read(bound(root,DEPLOY+'/FILES.json'));installed=read(bound(root,DEPLOY+'/installed.json'))
    if sha(bound(root,DEPLOY+'/FILES.json'))!=installed['files_sha256']:raise ValueError('ROLLBACK_HASHLIST_CHANGED')
    verify_files(root,files)
    old=read(bound(root,DEPLOY+'/old-inventory.json'));expected=read(bound(root,DEPLOY+'/old-invariants.json'))
    verify_old(root,old,expected)
    name='rehearsal-rollback' if rehearsal else 'rollback'
    result=bound(root,DEPLOY+'/'+name+'-result.json')
    if result.exists():
        if read(result).get('status')!='PASS':raise ValueError('ROLLBACK_RECONCILE_REQUIRED')
        for item in old['units']:
            if system(root,'state',item['name'])!={k:item[k] for k in ['enabled','active']}:raise ValueError('ROLLBACK_UNIT_STATE_DRIFT')
        for unit in UNITS:
            if system(root,'state',unit)!={'enabled':False,'active':False}:raise ValueError('NEW_UNIT_REACTIVATED')
        return {**read(result),'already_completed':True}
    intent=bound(root,DEPLOY+'/'+name+'-intent.json')
    if intent.exists():raise ValueError('PARTIAL_ROLLBACK_RECONCILE_NO_RETRY')
    save_new(intent,{'status':'STARTED','inventory_sha256':inventory_sha})
    try:
        for unit in reversed(UNITS):system(root,'stop',unit);system(root,'disable',unit)
        for unit in UNITS:
            if system(root,'state',unit)!={'enabled':False,'active':False}:raise ValueError('NEW_UNIT_STOP_UNCERTAIN')
        verify_old(root,old,expected)
        for item in old['units']:
            if system(root,'state',item['name'])!={'enabled':False,'active':False}:raise ValueError('OLD_UNITS_NOT_HELD_BEFORE_RESTORE')
        for item in old['units']:
            if item['enabled']:system(root,'enable',item['name'])
            if item['active']:system(root,'start',item['name'])
        evidence=verify_old(root,old,expected)
        for item in old['units']:
            if system(root,'state',item['name'])!={k:item[k] for k in ['enabled','active']}:raise ValueError('OLD_UNIT_RESTORE_FAILED')
        receipt={'status':'PASS','rehearsal':rehearsal,'old_state':evidence,'new_state':'retained in place; not rolled back or deleted'}
    except BaseException as error:
        save_new(result,{'status':'RECONCILE_REQUIRED','error_type':type(error).__name__});raise
    save_new(result,receipt);return receipt


def main():
    p=argparse.ArgumentParser();p.add_argument('operation',choices=['install','rollback','promote','promotion-rollback']);p.add_argument('--root',type=Path,required=True);p.add_argument('--live',action='store_true');p.add_argument('--rehearsal',action='store_true')
    for key in ['source','tag','commit','tag-object','review','review-sha256','old-inventory','inventory-sha256','implementation-sha256','previous']:p.add_argument('--'+key)
    p.add_argument('--entrypoint',choices=['analysis','experiment'])
    p.add_argument('--experiment-plan')
    p.add_argument('--experiment-companion-plan')
    p.add_argument('--stocktake-recovery',action='store_true')
    p.add_argument('--stocktake-navigation',action='store_true')
    p.add_argument('--stocktake-review-continuation',action='store_true')
    a=p.parse_args()
    if a.root.absolute()==Path('/'):
        if not a.live or os.geteuid()!=0:raise SystemExit('LIVE_ROOT_REQUIRES_EXPLICIT_FLAG_AND_ROOT')
        if a.operation in {'install','rollback'}:raise SystemExit('LEGACY_RC3_LIVE_ROUTE_RETIRED_USE_VERSIONED_PROMOTION')
    elif a.live:raise SystemExit('LIVE_FLAG_REQUIRES_REAL_ROOT')
    try:
        if a.operation in {'promote','promotion-rollback'}:
            import sys
            sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
            from tools import manual_promotion
            result=manual_promotion.promote(a.root,a.source,a.tag,a.commit,a.tag_object,a.review,a.review_sha256,a.previous,a.old_inventory,entrypoint=a.entrypoint,experiment_plan=a.experiment_plan,experiment_companion_plan=a.experiment_companion_plan,stocktake_recovery=a.stocktake_recovery,stocktake_navigation=a.stocktake_navigation,stocktake_review_continuation=a.stocktake_review_continuation) if a.operation=='promote' else manual_promotion.rollback(a.root,a.tag)
        elif a.operation=='install':result=install(a.root,a.source,a.tag,a.commit,a.tag_object,a.review,a.review_sha256,a.old_inventory)
        else:result=rollback(a.root,a.inventory_sha256,a.implementation_sha256,a.rehearsal)
        print(json.dumps(result,sort_keys=True,indent=2))
    except (ValueError,OSError,subprocess.SubprocessError,sqlite3.Error) as error:
        raise SystemExit('DEPLOYMENT_REFUSED: '+str(error)) from None

if __name__=='__main__':main()
