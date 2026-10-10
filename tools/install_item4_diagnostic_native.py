"""Install one reviewed native CPU + reviewer16 bundle, disabled and unspent."""
from pathlib import Path
import argparse,base64,gzip,hashlib,importlib.util,json,os,stat,subprocess,sys,tempfile
ENGINE=Path('/opt/research-system/autonomy-review/d08b91bdc1d0')
RUNTIME=Path('/etc/research-system-manual-sprint10/releases/research-manual-sprint10-timeout-continuation-8e042339/runtime.json')

def require(ok,why):
    if not ok:raise ValueError('DIAGNOSTIC_NATIVE_INSTALL_'+why)
def sha(raw):return hashlib.sha256(raw).hexdigest()
def trusted(path):
    path=Path(path)
    for p in (path,*path.parents):
        st=p.lstat();require(not p.is_symlink() and st.st_uid==0 and not st.st_mode&0o022,'TRUSTED_SOURCE')
    return path

def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec)
    sys.modules[name]=m;spec.loader.exec_module(m);return m

def put(path,raw):
    path.parent.mkdir(parents=True,exist_ok=True,mode=0o700)
    with path.open('xb') as stream:stream.write(raw)
    os.chown(path,0,1003);path.chmod(0o440)

def state_parent(path):
    # Preserve the actual existing service-private container and root-owned
    # inventory. Only this exact topology is allowed; do not chmod/chown it.
    path=Path(path)
    require(path==Path('/var/lib/research-system-manual-sprint10/environment-inventory'),'STATE_PARENT_PATH')
    for p,uid,gid,mode in ((path,0,1003,0o750),(path.parent,1003,1003,0o700)):
        st=p.lstat()
        require(stat.S_ISDIR(st.st_mode) and not p.is_symlink() and
            (st.st_uid,st.st_gid,stat.S_IMODE(st.st_mode))==(uid,gid,mode),'STATE_PARENT')
    trusted(path.parent.parent)


def install(source,review,bundle,*,preflight=False):
    require(os.geteuid()==0,'ROOT_REQUIRED');source=trusted(source);review=trusted(review);bundle=trusted(bundle)
    sys.path.insert(0,str(ENGINE))
    from orchestrator.autonomy_review import verify_result
    approval=verify_result(review);manifest=json.loads(trusted(review/'packet-manifest.json').read_bytes())
    require(approval['verdict']=='APPROVE' and approval['change_id']==manifest['change_id']=='item4-audited-native-verification-20261010'
        and approval['source_sha']==manifest['source_sha'] and approval['runtime_sha256']==sha(trusted(RUNTIME).read_bytes()),'GENUINE_APPROVAL')
    path=source/'tools/item4_diagnostic_native_runtime.py'
    require(sha(trusted(path).read_bytes())==manifest['source_files']['tools/item4_diagnostic_native_runtime.py'],'RUNTIME_SOURCE')
    h=load('_diagnostic_install_policy',path)
    bodies={name:trusted(source/name).read_bytes() for name in h.FILES}
    require(all(sha(raw)==manifest['source_files'][name] for name,raw in bodies.items()) and
        bodies['tools/install_item4_diagnostic_native.py']==Path(__file__).read_bytes(),'REVIEWED_SOURCE')
    # Read and qualify the existing source/image/closed-attempt receipts as the
    # existing service account, without importing candidate overlays into them.
    old=subprocess.check_output(['runuser','-u','partho','--','env',
        'RESEARCH_MANUAL_RUNTIME_CONFIG=/etc/research-system-manual-sprint10/releases/'+h.BASE.name+'/runtime.json',
        'python3','-s','-B',str(source/'tools/item4_validation_retained.py'),'--diagnostic-native'],timeout=120)
    require(json.loads(old)==json.loads(bodies['docs/ITEM4_DIAGNOSTIC_NATIVE_RETAINED_PRIVATE.json']),'ORIGINAL_PROOFS_CHANGED')
    import orchestrator,tools
    orchestrator.__path__=[str(source/'orchestrator'),str(h.BASE/'orchestrator'),*orchestrator.__path__]
    tools.__path__=[str(source/'tools'),str(h.BASE/'tools'),*tools.__path__]
    from orchestrator import modal_native_synthetic as n
    from tools import item4_native_worker as worker
    require(Path(n.__file__).resolve()==source/'orchestrator/modal_native_synthetic.py' and
        Path(worker.__file__).resolve()==source/'tools/item4_native_worker.py','INSTALL_IMPORTS')
    config=h.config_from_image(json.loads(old)['image_config']);units=h.rendered(config)
    code=bundle.read_bytes();selected=n.selected()
    require(sha(code)==selected['code_bundle_sha256'] and len(code)==selected['code_bundle_bytes'],'BUNDLE_CHANGED')
    with tempfile.TemporaryDirectory(prefix='diagnostic-native-source-check-') as folder:
        worker.unpack(base64.b64encode(gzip.compress(code,mtime=0)).decode(),selected,Path(folder));worker.check_package(Path(folder),selected)
    for unit in ('research-item4-whole-fixture-author-20261010.service',h.CPU_UNIT,h.REVIEW_UNIT):
        observed=dict(line.split('=',1) for line in subprocess.check_output(['systemctl','show',unit,'-p','ActiveState','-p','MainPID'],text=True).splitlines())
        require(observed.get('MainPID')=='0' and observed.get('ActiveState') in {'inactive','failed'},'ACTIVE_WRITER')
    targets=[h.ROOT,h.RECORD,h.CONFIG.parent,h.STATE,*[Path('/etc/systemd/system')/name for name in units]]
    require(all(not p.exists() and not p.is_symlink() for p in targets),'EXISTS_RECONCILE')
    # Reuse the original checked private state topology; release parents are
    # root-owned. No ownership or permissions on any existing path are changed.
    state_parent(h.STATE.parent)
    for target in targets:
        if target==h.STATE:continue
        ancestor=target.parent
        while not ancestor.exists():ancestor=ancestor.parent
        trusted(ancestor)
    with tempfile.TemporaryDirectory(prefix='diagnostic-native-unit-check-') as folder:
        files=[]
        for name,raw in units.items():
            p=Path(folder)/name;p.write_bytes(raw);files.append(str(p))
        checked=subprocess.run(['systemd-analyze','verify',*files],capture_output=True,text=True)
        require(checked.returncode==0,'UNIT_PARSE: '+checked.stderr)
    if preflight:return {'status':'PREFLIGHT_PASS','model_calls':0,'provider_calls':0,'installation_writes':0}
    put(h.RECORD/'INSTALL_INTENT.json',json.dumps({'source':approval['source_sha'],'review':approval,'status':'HELD_UNSPENT'},sort_keys=True).encode())
    for name,raw in bodies.items():put(h.ROOT/name,raw)
    for p in review.iterdir():
        require(p.is_file() and not p.is_symlink(),'REVIEW_MEMBER');put(h.RECORD/'review'/p.name,p.read_bytes())
    for name,raw in units.items():put(Path('/etc/systemd/system')/name,raw)
    configraw=json.dumps(config,sort_keys=True,separators=(',',':')).encode();put(h.CONFIG,configraw)
    put(h.RECORD/'code-bundle.json',code)
    h.STATE.mkdir(mode=0o700);os.chown(h.STATE,1003,1003)
    installed={'schema':'item4-diagnostic-native-install/v1','source':approval['source_sha'],
        'review_sha256':approval['report_sha256'],'files':{name:sha(raw) for name,raw in bodies.items()},
        'units':{name:sha(raw) for name,raw in units.items()},'config_sha256':sha(configraw),'status':'INSTALLED_HELD'}
    put(h.RECORD/'installed.json',json.dumps(installed,sort_keys=True).encode())
    for root in (h.ROOT,h.RECORD,h.CONFIG.parent):
        for p in (root,*[p for p in root.rglob('*') if p.is_dir()]):os.chown(p,0,1003);p.chmod(0o550)
    subprocess.run(['systemctl','daemon-reload'],check=True)
    for tool in ('item4_diagnostic_native_runtime.py','item4_diagnostic_review_runtime.py'):
        result=subprocess.run(['runuser','-u','partho','--','env','RESEARCH_MANUAL_RUNTIME_CONFIG='+str(RUNTIME),
            'python3','-s','-B',str(h.ROOT/'tools'/tool),'verify'],capture_output=True)
        put(h.RECORD/(tool+'.verify.stdout'),result.stdout);put(h.RECORD/(tool+'.verify.stderr'),result.stderr)
        require(result.returncode==0,'POSTCHECK_'+tool)
    put(h.RECORD/'COMPLETE.json',b'{"status":"INSTALLED_HELD","model_calls":0,"provider_calls":0}')
    return {'status':'INSTALLED_HELD','model_calls':0,'provider_calls':0}

if __name__=='__main__':
    os.umask(0o077);p=argparse.ArgumentParser()
    for name in ('source','review','bundle'):p.add_argument('--'+name,required=True)
    p.add_argument('--preflight',action='store_true')
    a=p.parse_args();print(json.dumps(install(a.source,a.review,a.bundle,preflight=a.preflight)))
