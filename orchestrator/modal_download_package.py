"""Assemble a stdlib-only private retrieval package; no provider or model call."""
import hashlib
import json
from pathlib import Path
from orchestrator import private_records, modal_ctp_download
from orchestrator.modal_ctp_download import encoded, identifier

MODULES=('__init__.py','private_records.py',
         'modal_development_inputs.py','review_contract.py','modal_ctp_download.py')
LAUNCHER=b'''import hashlib,json,sys
from pathlib import Path
root=Path(__file__).resolve().parent
manifest=json.loads((root/'manifest.json').read_bytes())
if len(sys.argv)!=3 or hashlib.sha256((root/'manifest.json').read_bytes()).hexdigest()!=sys.argv[1]:
    raise ValueError('DOWNLOAD_PACKAGE_MANIFEST_PIN')
files={str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest() for p in root.rglob('*') if p.is_file() and p!=root/'manifest.json'}
if any(p.is_symlink() for p in root.rglob('*')) or files!=manifest['files']:
    raise ValueError('DOWNLOAD_PACKAGE_CHANGED')
sys.path.insert(0,str(root))
from orchestrator.modal_ctp_download import download,validate
from orchestrator.modal_ctp_download import encoded
scope=sys.argv[2]
scopes=sorted(manifest['plans'],key=lambda x:x!='images') if scope=='all' else [scope]
if any(x not in manifest['plans'] for x in scopes):raise ValueError('DOWNLOAD_PACKAGE_SCOPE')
from orchestrator import private_records
from orchestrator.modal_ctp_download import volume_commit
osroot=Path('/volume')
# Mount root is provider-owned; create only fresh owner-private subdirectories.
# CTP and image member sets remain disjoint and are checked independently.
results={}
for scope in scopes:
    ref=manifest['plans'][scope]
    plan=json.loads((root/ref['path']).read_bytes())
    cohort=(root/'cohort.json').read_bytes()
    validate(plan,cohort)
    target=osroot/scope
    private_records.mkdir(target,exist_ok=True)
    results[scope]=download(plan,cohort,target,manifest['attempt']+'-'+scope,
                           plan_sha256=ref['sha256'])
private_records.write_bytes(osroot/'DOWNLOAD_COMPLETE.json',encoded({
    'schema':'private-development-download-result/v1','manifest_sha256':sys.argv[1],
    'results':results,'patient_computation':False}))
volume_commit(osroot)
print(json.dumps({'status':'VERIFIED','scopes':sorted(results),'files':sum(x['files'] for x in results.values())}))
'''


def sha(raw):return hashlib.sha256(raw).hexdigest()


def inventory(root):
    private_records.check_tree(root)
    return {str(p.relative_to(root)):sha(p.read_bytes()) for p in Path(root).rglob('*') if p.is_file()}


@private_records.private_umask
def emit(source,destination,cohort_raw,plans,attempt):
    """Caller preserves the returned manifest hash before reserving CPU work.

    The container receives this readonly package and exactly one private data
    Volume. No model binaries, SDK credentials, raw native records or login files
    are packaged. Retrying a container is a separate controller decision; this
    module does not mutate an existing attempt or launch one.
    """
    source=Path(source);destination=Path(destination);identifier(attempt)
    if destination.exists() or destination.is_symlink():raise ValueError('DOWNLOAD_PACKAGE_EXISTS')
    if not isinstance(plans,dict) or not plans or set(plans)-{'ctp','images'}:
        raise ValueError('DOWNLOAD_PACKAGE_PLANS')
    selected={}
    for scope,plan in plans.items():
        modal_ctp_download.validate(plan,cohort_raw)
        expected='development-ctp-download/v1' if scope=='ctp' else 'development-images-download/v1'
        if plan['schema']!=expected:raise ValueError('DOWNLOAD_PACKAGE_PLAN_KIND')
        raw=encoded(plan);selected[scope]=(raw,{'path':scope+'-plan.json','sha256':sha(raw)})
    modules={str(Path('orchestrator')/name):(source/'orchestrator'/name).read_bytes() for name in MODULES}
    for name,raw in modules.items():compile(raw,name,'exec')
    private_records.mkdir(destination)
    private_records.write_bytes(destination/'run.py',LAUNCHER)
    private_records.write_bytes(destination/'cohort.json',cohort_raw)
    for name,raw in modules.items():
        private_records.mkdir((destination/name).parent,parents=True,exist_ok=True)
        private_records.write_bytes(destination/name,raw)
    for scope,(raw,ref) in selected.items():private_records.write_bytes(destination/ref['path'],raw)
    manifest={'schema':'private-development-download-package/v1','attempt':attempt,
              'plans':{scope:ref for scope,(_,ref) in selected.items()},'files':inventory(destination),
              'authority_sha256':modal_ctp_download.AUTHORITY,'patient_computation':False}
    private_records.write_bytes(destination/'manifest.json',encoded(manifest))
    verify(destination,sha(encoded(manifest)))
    return {'manifest_sha256':sha(encoded(manifest)),'files':len(manifest['files'])+1,
            'planned_download_bytes':sum(r['bytes'] for p in plans.values() for r in p['files'].values()),
            'network_payload_bytes':0,'provider_operations':0}


def verify(package,manifest_sha256):
    package=Path(package);files=inventory(package)
    raw=(package/'manifest.json').read_bytes()
    if sha(raw)!=manifest_sha256:raise ValueError('DOWNLOAD_PACKAGE_MANIFEST_PIN')
    value=json.loads(raw);files.pop('manifest.json',None)
    if value.get('schema')!='private-development-download-package/v1' or value.get('files')!=files:
        raise ValueError('DOWNLOAD_PACKAGE_CHANGED')
    if (package/'run.py').read_bytes()!=LAUNCHER or value.get('authority_sha256')!=modal_ctp_download.AUTHORITY:
        raise ValueError('DOWNLOAD_PACKAGE_LAUNCHER_OR_AUTHORITY')
    cohort=(package/'cohort.json').read_bytes()
    for scope,ref in value['plans'].items():
        if scope not in ('ctp','images') or ref['path']!=scope+'-plan.json':raise ValueError('DOWNLOAD_PACKAGE_PLAN_KIND')
        raw=(package/ref['path']).read_bytes()
        if sha(raw)!=ref['sha256']:raise ValueError('DOWNLOAD_PACKAGE_PLAN_CHANGED')
        modal_ctp_download.validate(json.loads(raw),cohort)
    return value
