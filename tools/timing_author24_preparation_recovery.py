"""Preserve one exact unadmitted author24 preparation; never edit a ledger."""
import hashlib,json,os,sqlite3,stat,subprocess
from pathlib import Path
from orchestrator import private_records as pr
CHANGE='timing-author24-preparation-recovery-20261010'
REVIEW_CHANGE='rotation-timing-direction-20261010'
DOCUMENT='docs/TIMING_AUTHOR24_PREPARATION_PRIVATE.json'
DOCUMENT_SHA='97238f2e5eb8b532e25e8d0bbd05cb73599fb0b27ce2217d78f1da7f41299b4f'
BASE=Path('/var/lib/research-system-manual-sprint10/releases/research-manual-sprint10-timeout-continuation-8e042339/item4')
LANE=BASE/'lane'
WORK=BASE/'lane-scientific-workspaces/run_spec_author-24'
PINS=LANE/'author24-delivery/runtime-pins-24.json'
ARCHIVE=LANE/'timing-author24-preparation-preserved-20261010'
LEDGER=Path('/var/lib/research-system-autonomy/reviews/jobs.sqlite')
ID='4a171e924b528328d4a4827815113449b39d19143a8824b92f17dce0ecf0b8ca'
INSTALL_RECEIPT=Path('/var/lib/research-system-manual-sprint10-deployment')/CHANGE/'installed.json'
def require(ok,why):
    if not ok:raise ValueError('TIMING_PREPARATION_'+why)
def sha(raw):return hashlib.sha256(raw).hexdigest()
def canonical(value):return json.dumps(value,sort_keys=True).encode()
def binding():
    raw=(Path(__file__).resolve().parents[1]/DOCUMENT).read_bytes()
    require(sha(raw)==DOCUMENT_SHA,'DOCUMENT_CHANGED');return json.loads(raw)
def metadata(path):
    path=Path(path);s=path.lstat()
    require(not path.is_symlink() and s.st_uid==s.st_gid==1003,'PRIVATE_ENTRY_OWNER')
    if stat.S_ISDIR(s.st_mode):kind='directory'
    elif stat.S_ISREG(s.st_mode):
        require(s.st_nlink==1,'NO_HARDLINK');kind='file'
    else:raise ValueError('TIMING_PREPARATION_REGULAR_TREE_REQUIRED')
    out=dict(mode=stat.S_IMODE(s.st_mode),uid=s.st_uid,gid=s.st_gid,type=kind)
    if kind=='file':raw=path.read_bytes();out.update(bytes=len(raw),sha256=sha(raw))
    return out
def inventory(root):
    root=Path(root);result={'.':metadata(root)}
    require(result['.']['type']=='directory','WORKSPACE_DIRECTORY')
    def walk(folder):
        for p in sorted(folder.iterdir()):
            item=metadata(p);result[p.relative_to(root).as_posix()]=item
            if item['type']=='directory':walk(p)
    walk(root);return result
def snapshot(db):
    return {'state':dict(db.execute('SELECT * FROM manual_state WHERE id=1').fetchone()),
        'account':[dict(r) for r in db.execute('SELECT * FROM manual_account ORDER BY id')],
        'calls':[dict(r) for r in db.execute('SELECT * FROM manual_calls ORDER BY id')]}
def validate(config,rows,local_call,global_call,tree,pins):
    b=binding();state=json.loads(rows['state']['payload'])
    require(sha(config)==b['config_sha256'],'CONFIG_CHANGED')
    for key in ('state','account','calls'):require(sha(canonical(rows[key]))==b[key+'_sha256'],'ORIGINAL_'+key.upper()+'_CHANGED')
    require(local_call is None and global_call is None and len(rows['calls'])==38,'UNADMITTED_ONLY')
    require(state['phase']=='run_spec_author' and not state.get('pending') and state['rounds']=={'run_spec_author':23,'run_spec_review':15},'EXACT_READY_AUTHOR24')
    require(tree==b['tree'] and pins==b['pins_metadata'],'EXACT_PREPARATION_TREE')
def authority(review):
    from orchestrator.autonomy_review import verify_result
    result=verify_result(review);manifest=json.loads(pr.check(Path(review)/'packet-manifest.json').read_bytes())
    require(result['change_id']==REVIEW_CHANGE and result['verdict']=='APPROVE' and not result.get('findings'),'GENUINE_APPROVAL')
    root=Path(__file__).resolve().parents[1]
    for name in (DOCUMENT,'tools/timing_author24_preparation_recovery.py','tools/timing_author24_runtime.py'):
        require(manifest['source_files'].get(name)==sha((root/name).read_bytes()),'REVIEWED_SOURCE')
    for p in [INSTALL_RECEIPT,*INSTALL_RECEIPT.parents]:
        st=p.lstat();require(not p.is_symlink() and st.st_uid==0 and not st.st_mode&0o022,'ROOT_INSTALL_RECEIPT')
    installed=json.loads(INSTALL_RECEIPT.read_bytes())
    require(installed['source']==result['source_sha'] and installed['review_sha256']==result['report_sha256'] and installed['status']=='INSTALLED_HELD' and installed['preserved_operation_run_sha256']==binding()['operation_run_sha256'],'ROOT_VERIFIED_ORIGINAL_OPERATION')
    return result
def held_unit():
    expected=dict(binding()['failed_unit']);name=expected.pop('name')
    args=['systemctl','show',name]
    for key in expected:args+=['-p',key]
    actual=dict(x.split('=',1) for x in subprocess.check_output(args,text=True).splitlines())
    require(actual==expected,'EXACT_FAILED_INVOCATION')
@pr.private_umask
def apply(review,*,filesystem_root=Path('/'),check_unit=held_unit):
    require(os.getuid()==os.getgid()==1003,'SERVICE_OWNER')
    from tools.deploy_manual_lane import bound
    from orchestrator.remote_supervisor import lock
    path=lambda p:bound(Path(filesystem_root),str(p))
    result=authority(review);dest=path(ARCHIVE)
    require(not dest.exists() and not dest.is_symlink(),'ORIGINAL_OR_PARTIAL_ARCHIVE_PRESERVED')
    require(not path(LANE/'HALT').exists() and not path(LEDGER.parent/'HALT').exists(),'HALT_PRESERVED')
    check_unit()
    with lock(path(LANE/'one-run.lock')),lock(path(LANE/'driver.lock')):
        with sqlite3.connect(path(LANE/'jobs.sqlite').resolve().as_uri()+'?mode=ro',uri=True) as db,sqlite3.connect(path(LEDGER).resolve().as_uri()+'?mode=ro',uri=True) as globaldb:
            db.row_factory=globaldb.row_factory=sqlite3.Row
            db.execute('BEGIN');globaldb.execute('BEGIN')
            require(not globaldb.execute("SELECT 1 FROM autonomy_calls WHERE status='RUNNING'").fetchone(),'OTHER_RUNNING_CALL')
            rows=snapshot(db);original=pr.check(path(LANE/'lane.json')).read_bytes()
            local=db.execute('SELECT * FROM manual_calls WHERE id=?',(ID,)).fetchone()
            other=globaldb.execute('SELECT * FROM autonomy_calls WHERE id=?',(ID,)).fetchone()
            validate(original,rows,local,other,inventory(path(WORK)),metadata(path(PINS)))
            pr.mkdir(dest);pr.write_bytes(dest/'original-rows.json',canonical(rows));pr.write_bytes(dest/'lane.original.json',original)
            pr.write_bytes(dest/'INTENT.json',canonical({'call_id':ID,'binding_sha256':DOCUMENT_SHA,'review_sha256':result['report_sha256'],'workspace':str(WORK),'pins':str(PINS),'model_calls':0}))
            # Same-filesystem rename preserves every original byte and mode.
            # A crash leaves the exclusive archive as a stop, never a replay.
            path(WORK).rename(dest/'workspace');path(PINS).rename(dest/'runtime-pins-24.json')
            require(inventory(dest/'workspace')==binding()['tree'] and metadata(dest/'runtime-pins-24.json')==binding()['pins_metadata'],'ARCHIVE_CHANGED')
            require(snapshot(db)==rows and pr.check(path(LANE/'lane.json')).read_bytes()==original,'ORIGINAL_ROWS_CHANGED')
            out={'status':'PRESERVED_UNADMITTED_PREPARATION','call_id':ID,'review_sha256':result['report_sha256'],'binding_sha256':DOCUMENT_SHA,'local_calls':38,'model_calls':0,'provider_calls':0,'ledger_changes':0}
            pr.write_bytes(dest/'COMPLETE.json',canonical(out));return out
if __name__=='__main__':
    import argparse
    os.umask(0o077);p=argparse.ArgumentParser();p.add_argument('--review',type=Path,required=True);a=p.parse_args()
    print(json.dumps(apply(a.review),sort_keys=True))
