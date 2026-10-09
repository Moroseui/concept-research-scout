"""Install one reviewed spending runtime beside unchanged scientific lanes.

Reuses the existing promotion file manifest and unchanged service restrictions.
No selected-release switch, lane edits, model calls, provider calls or spending.
"""
import argparse,io,json,os,subprocess,tarfile
from pathlib import Path,PurePosixPath
from orchestrator import private_records as pr, spending_continuation as sc
from orchestrator.manual_executor import digest,read
from tools import manual_promotion as promotion, deploy_manual_lane as deploy

CHANGED = {
    "orchestrator/spending_continuation.py", "orchestrator/modal_diagnostics_image.py",
    "orchestrator/diagnostics_budget.py", "orchestrator/modal_environment_budget.py",
    "orchestrator/modal_item4_budget.py", "orchestrator/modal_pinned_image.py",
    "orchestrator/experiment_owner.py", "tools/spending_repair_service.py",
    "tests/test_spending_continuation.py", "docs/SPENDING_CONTINUATION_AUTHORITY_20261007.txt",
}


def unit(original, old_release, release, state):
    """Change only imports and the phase-limited command; retain all restrictions."""
    lines=original.splitlines()
    prefix="Environment=PYTHONPATH="+old_release+":"
    old="ExecStart=/usr/bin/python3 -s -B -m orchestrator.experiment_driver advance --state "+state
    sc.require(sum(line.startswith(prefix) for line in lines)==1 and lines.count(old)==1,"UNIT_TEMPLATE")
    return ("\n".join("Environment=PYTHONPATH="+release+":"+line[len(prefix):] if line.startswith(prefix)
        else "ExecStart=/usr/bin/python3 -s -B -m tools.spending_repair_service advance --state "+state
        if line==old else line for line in lines)+"\n").encode()


def destination_parent(path):
    # /etc/systemd/system is an existing public root-owned directory. Do not
    # impose private data-directory permissions on it or modify its mode.
    if Path(path).parent == Path('/etc/systemd/system'):
        from orchestrator.manual_host_guard import trusted
        trusted(Path(path).parent)
    else:
        pr.mkdir(Path(path).parent,parents=True,exist_ok=True)


def owner_preflight(release, previous, *, continued=False):
    """Only UID1003 opens live ledgers; compare logical rows, not volatile SHM."""
    code="""
import os,sys,json,sqlite3,hashlib
from pathlib import Path
assert os.getuid()==os.geteuid()==1003
sys.path.insert(0,sys.argv[1]);selected=json.loads(sys.argv[2]);continued=json.loads(sys.argv[3])
from orchestrator.modal_diagnostics_image import inspect_reviewed
from orchestrator.experiment_timeout_continuation import binding
from types import SimpleNamespace
root=Path(selected['state']);ledger=Path('/var/lib/research-system-autonomy/reviews')
def sha(v):return hashlib.sha256(json.dumps(v,sort_keys=True).encode()).hexdigest()
def tables(db):
 result={}
 for name, in db.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"):
  assert name.replace('_','').isalnum()
  result[name]=sorted([dict(r) for r in db.execute('SELECT * FROM '+name)],key=lambda v:json.dumps(v,sort_keys=True))
 return sha(result)
with sqlite3.connect((ledger/'jobs.sqlite').as_uri()+'?mode=ro',uri=True) as db:
 db.row_factory=sqlite3.Row;batch=SimpleNamespace(db=db,folder=ledger,filesystem_root=Path('/'))
 assert not (ledger/'HALT').exists() and not db.execute("SELECT 1 FROM autonomy_calls WHERE status='RUNNING'").fetchone()
 grant=binding(batch);assert grant['source']==selected['source'];before=tables(db)
 for item,pin in grant['lanes'].items():
  lane=Path(pin['state']);c=json.loads((lane/'lane.json').read_bytes())
  assert sha(c)==pin['config_sha256'] and not (lane/'HALT').exists()
  if continued:
   from orchestrator.spending_continuation import lane as resolve
   assert resolve(batch,c['run_id'],c['owner_binding'],c['source'])[0]==lane
 result={'global_tables':before,'item6_reviewed':inspect_reviewed(root/'lane'),'lanes':{}}
 for suffix in ('lane','item4/lane'):
  path=root/suffix
  with sqlite3.connect((path/'jobs.sqlite').as_uri()+'?mode=ro',uri=True) as local:
   local.row_factory=sqlite3.Row;result['lanes'][suffix]={'tables':tables(local),'config':hashlib.sha256((path/'lane.json').read_bytes()).hexdigest()}
 assert tables(db)==before
print(json.dumps(result,sort_keys=True))
"""
    done=subprocess.run(['/usr/sbin/runuser','-u','partho','--','/usr/bin/env',
        'PYTHONDONTWRITEBYTECODE=1','RESEARCH_MANUAL_RUNTIME_CONFIG='+previous['runtime'],
        '/usr/bin/python3','-s','-B','-c',code,release,json.dumps(previous),json.dumps(continued)],
        cwd='/',capture_output=True,text=True,check=True,timeout=90)
    return json.loads(done.stdout)


@pr.private_umask
def install(source, commit, review_folder):
    from orchestrator.autonomy_review import verify_result
    from orchestrator.manual_host_guard import trusted
    sc.require(os.getuid()==os.geteuid()==0,"INSTALL_ROOT_REQUIRED")
    source=Path(source);review_folder=Path(review_folder)
    previous=read(trusted(sc.POINTER));sc.require(previous['source']==sc.SOURCE,"SELECTED_SOURCE")
    promotion.previous_check(Path('/'),previous)
    approved=verify_result(review_folder)
    sc.require((approved['change_id'],approved['verdict'],approved['source_sha'],approved['runtime_sha256']) ==
        (sc.CHANGE,'APPROVE',commit,sc.RUNTIME),'EXACT_IMPLEMENTATION_APPROVAL')
    manifest=read(review_folder/'packet-manifest.json')
    changed=set(subprocess.check_output(['git','diff','--name-only',sc.SOURCE,commit],cwd=source,text=True).splitlines())
    sc.require(changed==CHANGED,'EXACT_CHANGED_FILES')
    raw=subprocess.check_output(['git','archive',commit],cwd=source);entries={}
    with tarfile.open(fileobj=io.BytesIO(raw)) as archive:
        for item in archive.getmembers():
            sc.require(not PurePosixPath(item.name).is_absolute() and '..' not in PurePosixPath(item.name).parts
                and (item.isfile() or item.isdir()),'ARCHIVE_ALIAS')
            if item.isfile():entries[item.name]=(archive.extractfile(item).read(),bool(item.mode&0o111))
    baseline=deploy.tree_hashes(Path(previous['release']))
    sc.require(set(entries)==set(baseline)|CHANGED,'SOURCE_INVENTORY')
    for name,(body,executable) in entries.items():
        sc.require(digest(body)==(manifest['source_files'].get(name) if name in CHANGED else baseline.get(name)),
            'UNREVIEWED_SOURCE:'+name)
    sc.require(digest(Path(__file__).read_bytes())==manifest['source_files']['tools/spending_repair_service.py'], 'INSTALLER_SOURCE')
    sc.require(digest(entries['docs/SPENDING_CONTINUATION_AUTHORITY_20261007.txt'][0])==sc.AUTHORITY,'OPERATOR_AUTHORITY')
    before=owner_preflight(previous['release'],previous)
    tag='research-manual-sprint10-spending-'+commit[:12]
    layout=promotion.layout(tag);layout['record']=sc.RECORD
    # No new scientific state, repositories, timers, or selected-release change.
    layout['state']=previous['state'];layout['units']=[tag+'.service',tag+'-item4.service']
    units={}
    for item,suffix,name in [(6,'/lane',layout['units'][0]),(4,'/item4/lane',layout['units'][1])]:
        old=previous['units'][0 if item==6 else 2]
        units[name]=unit(trusted('/etc/systemd/system/'+old).read_text(),previous['release'],layout['release'],previous['state']+suffix)
    paths=[layout[k] for k in ('release','config','record')]+['/etc/systemd/system/'+n for n in units]
    sc.require(all(not Path(p).exists() and not Path(p).is_symlink() for p in paths),'DESTINATION_EXISTS_RECONCILE')
    for p in paths:
        parent=Path(p).parent
        while not parent.exists():parent=parent.parent
        trusted(parent)
    for name in units:
        sc.require(deploy.system(Path('/'),'state',name)=={'enabled':False,'active':False},'NEW_UNIT_NOT_HELD')
    rec=Path(layout['record']);pr.mkdir(rec)
    promotion.private_new(rec/'intent.json',{'source':commit,'before':before,'no_blind_retry':True})
    files={}
    def put(path,body,executable=False):
        path=Path(path);destination_parent(path)
        promotion.private_new(path,body,mode=0o500 if executable else 0o400)
        files[str(path)]={'sha256':digest(body),'mode':path.stat().st_mode&0o777}
    for name,(body,executable) in entries.items():put(Path(layout['release'])/name,body,executable)
    put(Path(layout['config'])/'runtime.json',trusted(previous['runtime']).read_bytes())
    for name,body in units.items():put(Path('/etc/systemd/system')/name,body)
    # All runtime parents must be traversable by the existing service group.
    for key in ('release','config'):
        for folder in sorted([Path(layout[key]),*[p for p in Path(layout[key]).rglob('*') if p.is_dir()]],reverse=True):
            promotion.private_mode(folder,directory=True)
    promotion.private_new(rec/'FILES.json',files)
    receipt={'status':'PASS','repair':sc.CHANGE,'source':commit,'scientific_source':sc.SOURCE,
        'layout':layout,'files_sha256':digest((rec/'FILES.json').read_bytes()),'previous':previous,
        'review_folder':str(review_folder),'review_sha256':approved['report_sha256'],'changed_files':sorted(CHANGED),
        'scope':'Separate spending runtime only; existing scientific lanes, source and approvals unchanged'}
    promotion.private_new(rec/'installed.json',receipt);promotion.private_mode(rec,directory=True)
    promotion.manifest_check(Path('/'),str(rec))
    after=owner_preflight(layout['release'],previous,continued=True)
    sc.require(after==before,'SCIENTIFIC_OR_ACCOUNTING_STATE_CHANGED')
    sc.require(read(trusted(sc.POINTER))==previous,'SELECTED_RELEASE_CHANGED')
    # Completion evidence is adjacent, not an unlisted modification of release.
    rec.chmod(0o750)
    promotion.private_new(rec/'complete.json',{'status':'PASS','before':before,'after':after,'model_calls':0,'provider_calls':0,'units_disabled':True})
    promotion.private_mode(rec,directory=True)
    return receipt


@pr.private_umask
def advance(state):
    from orchestrator.experiment_driver import ExperimentDriver
    from orchestrator.manual_executor import lock
    sc.require(os.getuid()==os.getgid()==1003,'OWNER_REQUIRED')
    installed=sc.implementation();state=Path(state)
    sc.require(str(state) in {installed['previous']['state']+'/lane',installed['previous']['state']+'/item4/lane'},'STATE')
    driver=ExperimentDriver(state)
    try:
        with lock(state/'driver.lock'):
            driver.guard();value=driver.current()
            sc.require(value['phase'] in {'EXECUTE_EXPERIMENT','COLLECT_EXPERIMENT'},'EXECUTION_PHASE_ONLY')
            sc.lane(driver.store.batch,driver.config['run_id'],driver.config['owner_binding'],driver.config['source'])
            from orchestrator.experiment_package import advance as execute
            return execute(driver,value,None,None)
    finally:
        driver.store.db.close();driver.store.batch.db.close()


def main():
    p=argparse.ArgumentParser();sub=p.add_subparsers(dest='command',required=True)
    i=sub.add_parser('install')
    for key in ('source','commit','review-folder'):i.add_argument('--'+key,required=True)
    a=sub.add_parser('advance');a.add_argument('--state',required=True)
    args=p.parse_args()
    print(json.dumps(install(args.source,args.commit,args.review_folder) if args.command=='install' else advance(args.state),sort_keys=True))

if __name__=='__main__':main()
