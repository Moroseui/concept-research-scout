"""Sprint10 CPU adapter: setup/capture only; original scientific cells preserved."""
import ast
import csv
import subprocess
import tempfile
import io
import json
from pathlib import Path
from orchestrator.manual_executor import digest, atomic, inventory
from orchestrator import manual_package, private_records
from orchestrator.manual_validation import baseline_contract, RETURN_FILES

BASE=Path('projects/isles24/manual/sprint10')
VIRTUAL_DATA='/content/drive/MyDrive/isles-pilot'
TOLERANCE={'tables':'byte-identical','numeric_tolerance':0,'bootstrap_seed':0,'bootstrap_resamples':2000,
           'json_scientific_content':'exact','allowed_metadata_differences':['utc','code_version','fingerprint','run_identity']}


def contract(root):return json.loads((Path(root)/BASE/'CPU_INPUT_BINDING.json').read_text())


def split_bytes(cases):
    out=io.StringIO(newline='');writer=csv.writer(out,lineterminator='\n')
    writer.writerow(['case_id','population']);writer.writerows((c,'census') for c in sorted(cases))
    return out.getvalue().encode()


def verify_data(root,binding):
    root=Path(root)
    if any(p.is_symlink() for p in [root,*root.parents]):raise ValueError('CPU_DATA_ALIAS')
    manifest_raw=(root/'manifest.json').read_bytes();cohort_raw=(root/'development99.manifest.json').read_bytes()
    if digest(manifest_raw)!=binding['transport_manifest_sha256'] or digest(cohort_raw)!=binding['cohort_manifest_sha256']:raise ValueError('CPU_DATA_MANIFEST_CHANGED')
    manifest=json.loads(manifest_raw);cohort=json.loads(cohort_raw)
    if manifest.get('count')!=759 or manifest.get('development_count')!=99 or manifest.get('membership_manifest_sha256')!=digest(cohort_raw):raise ValueError('CPU_DATA_COHORT_BINDING')
    cases=cohort['cases']
    if len(cases)!=99 or len(set(cases))!=99 or cohort['count']!=99:raise ValueError('CPU_DEVELOPMENT_COHORT')
    if digest(split_bytes(cases))!=binding['derived_split_sha256']:raise ValueError('CPU_DERIVED_SPLIT_CHANGED')
    rows=manifest['files']
    if len(rows)!=759:raise ValueError('CPU_ASSET_COUNT')
    expected={}
    # Transport uses a path-keyed map; no unlisted asset is exposed to computation.
    for name,item in rows.items():
        rel=Path(name)
        if rel.is_absolute() or '..' in rel.parts or str(rel)!=name:raise ValueError('CPU_DATA_PATH')
        expected[name]=item['sha256']
        p=root/name
        if p.is_symlink() or not p.is_file() or p.stat().st_size!=item['bytes']:raise ValueError('CPU_DATA_FILE_IDENTITY')
    actual=inventory(root)
    expected.update({'manifest.json':digest(manifest_raw),'development99.manifest.json':digest(cohort_raw)})
    if actual!=expected:raise ValueError('CPU_DATA_HASH_OR_EXTRA_FILE')
    return {'status':'VERIFIED','development_count':99,'assets':759,'manifest_sha256':digest(manifest_raw)}


def notebook_bytes(root,run_id):
    root=Path(root);bind=contract(root)
    nb=json.loads((root/BASE/'isles24_sprint10_r2_exclusion_reference.ipynb').read_text())
    cfg=''.join(nb['cells'][1]['source'])
    replacements={
      'OUT_BASE = f"{DRIVE_BASE}/sprint10-comparison-PRIVATE"':'OUT_BASE = "/workspace/comparison"',
      'PRIVATE_INPUT_DIR = f"{DRIVE_BASE}/sprint10-inputs-PRIVATE"':'PRIVATE_INPUT_DIR = "/workspace/inputs"',
      'da79e94bdae3f59d23db497d5f26f0d57aa4f279847fe57ec9a8d05ebcf18843':bind['derived_split_sha256'],
      'ee8d4f96b0c16620450c0e7e2e6a56993d2ee68e20913c78a1bb8fe7af0f1ab2':bind['derived_exclusions_sha256'],
      '"count": 1':'"count": 0',
      'sprint10-r2-exclusion-reference-v1':'sprint10-m2-cpu-adapter-v1'}
    for old,new in replacements.items():
        if cfg.count(old)!=1:raise ValueError('CPU_CONFIG_REPLACEMENT_BINDING')
        cfg=cfg.replace(old,new)
    nb['cells'][1]['source']=cfg.splitlines(keepends=True)
    setup=''.join(nb['cells'][2]['source']);start=setup.index('from google.colab import drive');end=setup.index('import numpy as np')
    nb['cells'][2]['source']=(setup[:start]+setup[end:]).splitlines(keepends=True)
    capture=manual_package.START.replace('PACKAGE_DIR = Path("/content/drive/MyDrive/isles-pilot/manual-step-d/RUN_ID")','PACKAGE_DIR = Path("/package")').replace('ACCEPTANCE_RETURN = PACKAGE_DIR / "return"','ACCEPTANCE_RETURN = Path("/workspace/return")').replace('OUT_BASE = str(PACKAGE_DIR / "comparison")','OUT_BASE = "/workspace/comparison"')
    # Identity refusal is private executor evidence, never a mutation of the package.
    capture=capture.replace('(PACKAGE_DIR / ("identity-refusal-"','(Path("/workspace") / ("identity-refusal-"')
    endcell=manual_package.END[:manual_package.END.index('archive = PACKAGE_DIR')]
    endcell+='print("CPU execution finished; controller validates the captured return.")\n'
    def cell(text):return {'cell_type':'code','metadata':{},'source':text.splitlines(keepends=True),'outputs':[],'execution_count':None}
    nb['cells'].insert(2,cell(capture));nb['cells'].append(cell(endcell))
    for entry in nb['cells']:
        if entry['cell_type']=='code':entry.update(outputs=[],execution_count=None)
    return (json.dumps(nb,indent=1)+'\n').encode()


@private_records.private_umask
def emit(root,prepared,run_id,source,spec,review):
    root,prepared=Path(root),Path(prepared);private_records.mkdir(prepared)
    raw=notebook_bytes(root,run_id);private_records.write_bytes(prepared/'Sprint10.ipynb',raw)
    for name,path in [('SPEC.md',spec),('review.json',review)]:private_records.copyfile(path,prepared/name)
    bind=contract(root);baseline=baseline_contract(root)
    manifest={'schema':'cpu-sprint10-acceptance/v1','run_id':run_id,'source':source,
      'spec_sha256':digest(Path(spec).read_bytes()),'review_sha256':digest(Path(review).read_bytes()),
      'notebook_code_sha256':manual_package.code_sha(raw),'notebook_code_cells':manual_package.code_cells(raw),
      'notebook_artifact_sha256':digest(raw),'predecessor_notebook_sha256':digest((root/BASE/'isles24_sprint10_r2_exclusion_reference.ipynb').read_bytes()),
      'private_files':{'split_manifest.csv':bind['derived_split_sha256'],'excluded_cases.json':bind['derived_exclusions_sha256']},
      'data_binding':bind,'baseline_sha256':baseline['sha256'],'baseline_json_keys':baseline['json_keys'],
      'return_files':list(RETURN_FILES),'tolerance':TOLERANCE,'training_allowed':False,'development_count':99,'locked_patient_access_allowed':False}
    atomic(prepared/'manifest.json',manifest,mode=0o600)
    # Exec each exact code-cell source in order, recording no new scientific code.
    runner="import json\nfrom pathlib import Path\nn=json.loads(Path('/package/Sprint10.ipynb').read_text())\nfor i,c in enumerate(n['cells']):\n    if c['cell_type']=='code':\n        print('CELL',i,flush=True)\n        exec(compile(''.join(c['source']),'Sprint10.ipynb:cell'+str(i),'exec'),globals())\n"
    private_records.write_text(prepared/'run.py',runner)
    private_records.check_tree(prepared)
    return manifest



def runtime_config(root):
    config=json.loads((Path(root)/'deploy/manual-lane/cpu-runtime.json').read_text())
    if set(config)!={'schema','environment_root','environment_sha256','data_root','batch_ledger','denied_paths','python','packages'} or config['schema']!='sprint10-cpu-runtime/v1':raise ValueError('CPU_RUNTIME_SCHEMA')
    for field in ['environment_root','data_root','batch_ledger']:
        path=Path(config[field])
        if not path.is_absolute() or '..' in path.parts:raise ValueError('CPU_RUNTIME_ABSOLUTE_PATH')
    if config['batch_ledger']!='/var/lib/research-system-autonomy/reviews':raise ValueError('SHARED_BATCH_LEDGER_REQUIRED')
    if not Path(config['data_root']).is_relative_to('/var/lib/research-system-autonomy/data'):raise ValueError('CPU_PRIVATE_DATA_ROOT')
    return config


def notebook_imports(raw):
    """Inspect only top-level import statements; never execute notebook cells."""
    names=set()
    def visit(nodes):
        for node in nodes:
            if isinstance(node,(ast.FunctionDef,ast.AsyncFunctionDef,ast.ClassDef)):continue
            if isinstance(node,ast.Import):names.update(a.name.split('.')[0] for a in node.names)
            elif isinstance(node,ast.ImportFrom) and node.module:names.add(node.module.split('.')[0])
            for field in ('body','orelse','finalbody'):
                children=getattr(node,field,[])
                if isinstance(children,list):visit(children)
            for handler in getattr(node,'handlers',[]):visit(handler.body)
    for cell in json.loads(raw)['cells']:
        if cell['cell_type']=='code':visit(ast.parse(''.join(cell['source'])).body)
    return sorted(names)


@private_records.private_umask
def runtime_preflight(root,config):
    """Prove actual data and imports in the CPU jail before any model admission."""
    from orchestrator import cpu_isolation
    raw=notebook_bytes(root,'readiness-only')
    names=notebook_imports(raw)
    data=verify_data(config['data_root'],contract(root))
    with tempfile.TemporaryDirectory(prefix='cpu-readiness-') as temporary:
        base=Path(temporary);package=base/'package';workspace=base/'workspace'
        private_records.mkdir(package);private_records.mkdir(workspace)
        private_records.write_bytes(package/'Sprint10.ipynb',raw)
        command=cpu_isolation.command(config,package,Path(config['data_root']),workspace,probe=True,imports=names)
        result=subprocess.run(command,capture_output=True,text=True,timeout=180)
        if result.returncode:
            raise ValueError('CPU_NOTEBOOK_IMPORT_PREFLIGHT_REFUSED: '+result.stderr[-2000:])
        receipt=json.loads(result.stdout)
        if receipt.get('status')!='ISOLATED' or receipt.get('verified_imports')!=names:
            raise ValueError('CPU_NOTEBOOK_IMPORT_PROOF_CHANGED')
    return {'status':'READY','environment_sha256':config['environment_sha256'],
            'data':data,'notebook_code_sha256':manual_package.code_sha(raw),'isolation':receipt,
            'model_calls':0,'notebook_cells_executed':False}
