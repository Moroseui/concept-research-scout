"""Sprint10 known-case acceptance, no training and no statistical reinterpretation.

CSV validation stays local/private. Only aggregate summaries and count-only
failure diagnostics may enter model workspaces. Tolerance is fixed before run.
"""
import csv
import hashlib
import json
import math
from pathlib import Path

TABLES=('completion.csv','matched_amount_status.csv','summary_by_recipe.csv','paired_contrasts.csv','all_percase.csv')
TOLERANCE={'numeric_atol':1e-10,'numeric_rtol':1e-9,'bootstrap_seed':0,'bootstrap_resamples':2000,
 'strings_counts_and_formatted_intervals':'exact','row_and_column_order':'exact',
 'allowed_path_difference':'only original/new comparison output directory prefix',
 'allowed_metadata_differences':['utc','code_version','fingerprint','run_identity']}

BASELINE_PATH='/content/drive/MyDrive/isles-pilot/sprint10-comparison-PRIVATE/compare-875c56c278-0a60362503'
RETURN_FILES=(*TABLES,'comparison_reference.json','compatibility_report.json')
BASELINE_JSON_KEYS={
 'comparison_reference.json':sorted(['clinical_checks','code_version','hard_checks','matched_amount','provisional','rows','sprint8','sprint9','states','utc']),
 'compatibility_report.json':sorted(['cache_identity','clinical_checks','clinical_fields','code_version','hard_checks','partition_differences','sprint8','sprint9','utc'])}



def baseline_contract(root):
    value=load(Path(root)/'projects/isles24/manual/sprint10/REFERENCE_BINDINGS.json')
    import re
    if value.get('status')!='PINNED_ORIGINALS' or value.get('baseline_path')!=BASELINE_PATH:
        raise ValueError('ORIGINAL_BASELINE_NOT_PINNED')
    if set(value['sha256'])!=set(RETURN_FILES) or any(not re.fullmatch('[a-f0-9]{64}',v) for v in value['sha256'].values()):
        raise ValueError('BASELINE_HASH_SET')
    if value['json_keys']!=BASELINE_JSON_KEYS:
        raise ValueError('BASELINE_JSON_KEY_SET')
    return value


def expected_identity(private_files):
    return {'code_version':'sprint10-r2-exclusion-reference-v1','sprint8_fingerprint':'875c56c278','sprint9_fingerprint':'0a60362503',
        'exclusions_sha256':private_files['excluded_cases.json'],'exclusions_count':1,'split_manifest_sha256':private_files['split_manifest.csv']}


def expected_output_path(manifest):
    import re
    if not re.fullmatch(r'[a-zA-Z0-9-]+',manifest['run_id']):raise ValueError('RUN_PATH_BINDING')
    fingerprint=sha(json.dumps(expected_identity(manifest['private_files']),sort_keys=True).encode())[:12]
    return '/content/drive/MyDrive/isles-pilot/manual-step-d/'+manifest['run_id']+'/comparison/compare-875c56c278-0a60362503-'+fingerprint


def sha(raw):return hashlib.sha256(raw).hexdigest()
def load(path):return json.loads(Path(path).read_text())
def safe(folder,name):
    p=Path(folder)/name
    if p.is_symlink() or not p.is_file():raise ValueError('REQUIRED_REGULAR_RETURN_FILE')
    return p

def compare_tables(before,after,old_prefix,new_prefix):
    result={};failures=[]
    for name in TABLES:
        a=list(csv.reader(safe(before,name).open(newline='')));b=list(csv.reader(safe(after,name).open(newline='')))
        bad=[]
        if not a or not b or a[0]!=b[0] or len(a)!=len(b):bad.append({'kind':'shape_or_header'})
        else:
            for row,(left,right) in enumerate(zip(a[1:],b[1:]),1):
                if len(left)!=len(a[0]) or len(right)!=len(left):bad.append({'kind':'row_width','row':row});continue
                for col,(x,y) in enumerate(zip(left,right)):
                    x=x.replace(old_prefix,'$COMPARISON_OUTPUT');y=y.replace(new_prefix,'$COMPARISON_OUTPUT')
                    if x.lower() in {'inf','-inf','+inf','infinity','-infinity'} or y.lower() in {'inf','-inf','+inf','infinity','-infinity'}:
                        bad.append({'kind':'nonfinite','row':row,'column_index':col});continue
                    if x==y:continue
                    label=a[0][col].lower()
                    exact=label in {'case','patients','matched_obs','better','worse','tied','shuffle','fold','train_seed'} or label.endswith('_patients') or label.startswith('n_')
                    try:
                        v,z=float(x),float(y)
                        equal=not exact and math.isfinite(v) and math.isfinite(z) and math.isclose(v,z,rel_tol=TOLERANCE['numeric_rtol'],abs_tol=TOLERANCE['numeric_atol'])
                    except ValueError:equal=False
                    if not equal:bad.append({'kind':'cell_difference','row':row,'column_index':col})
        result[name]={'rows':max(0,len(b)-1),'baseline_sha256':sha(safe(before,name).read_bytes()),'actual_sha256':sha(safe(after,name).read_bytes()),'difference_count':len(bad)}
        failures.extend({'file':name,**x} for x in bad[:10])
    return {'status':'VALID' if not failures else 'INVALID','tables':result,'differences':failures,'tolerance':TOLERANCE}

def _validate_return(folder,manifest,private=None,*,cpu=False):
    expected_tolerance=TOLERANCE
    identity_expected=expected_identity(manifest['private_files'])
    output_expected=expected_output_path(manifest)
    if cpu:
        from orchestrator.cpu_package import contract,TOLERANCE as CPU_TOLERANCE
        binding=contract(Path(__file__).resolve().parents[1])
        if manifest.get('schema')!='cpu-sprint10-acceptance/v1' or manifest.get('data_binding')!=binding:raise ValueError('CPU_REVIEWED_DATA_BINDING')
        if manifest['private_files']!={'split_manifest.csv':binding['derived_split_sha256'],'excluded_cases.json':binding['derived_exclusions_sha256']}:raise ValueError('CPU_PRIVATE_INPUT_BINDING')
        identity_expected.update(code_version='sprint10-m2-cpu-adapter-v1',exclusions_count=0)
        output_expected='/workspace/comparison/compare-875c56c278-0a60362503-'+sha(json.dumps(identity_expected,sort_keys=True).encode())[:12]
        expected_tolerance=CPU_TOLERANCE
    folder=Path(folder)
    expected_paths={'started.json','execution_receipt.json'}|{sub+'/'+name for sub in ['baseline','actual'] for name in RETURN_FILES}
    actual_paths={str(p.relative_to(folder)) for p in folder.rglob('*') if p.is_file() or p.is_symlink()}
    if actual_paths!=expected_paths:raise ValueError('RETURN_FILE_SET')
    receipt=load(safe(folder,'execution_receipt.json'))
    started=load(safe(folder,'started.json'))
    if set(started)!={'run_id','manifest_sha256','baseline_sha256'} or started['run_id']!=manifest['run_id'] or started['manifest_sha256']!=sha(json.dumps(manifest,sort_keys=True).encode()) or started['baseline_sha256']!=manifest['baseline_sha256']:
        raise ValueError('START_MARKER_BINDING')
    if receipt.get('run_id')!=manifest['run_id'] or receipt.get('manifest_sha256')!=sha(json.dumps(manifest,sort_keys=True).encode()):raise ValueError('RETURN_RUN_BINDING')
    for key in ['source','spec_sha256','notebook_code_sha256','private_files']:
        if receipt.get(key)!=manifest[key]:raise ValueError('RETURN_VERSION_BINDING')
    if receipt.get('development_count')!=99 or receipt.get('training_performed') is not False:raise ValueError('RETURN_SCOPE')
    if receipt.get('tolerance')!=expected_tolerance:raise ValueError('RETURN_TOLERANCE_CHANGED')
    for sub in ['baseline','actual']:
        for name,digest in receipt[sub+'_sha256'].items():
            if name not in (*TABLES,'comparison_reference.json','compatibility_report.json'):raise ValueError('RETURN_FILE_SCOPE')
            if sha(safe(folder/sub,name).read_bytes())!=digest:raise ValueError('RETURN_ORIGINAL_CHANGED')
        if set(receipt[sub+'_sha256'])!=set((*TABLES,'comparison_reference.json','compatibility_report.json')):raise ValueError('INCOMPLETE_RETURN')
    if receipt['baseline_sha256']!=manifest['baseline_sha256']:raise ValueError('UNREVIEWED_BASELINE')
    for name,keys in manifest['baseline_json_keys'].items():
        if sorted(load(folder/'baseline'/name))!=keys:raise ValueError('BASELINE_JSON_KEYS_CHANGED')
    if receipt['baseline_output_path']!=BASELINE_PATH or receipt['actual_output_path']!=output_expected:raise ValueError('RETURN_PATH_BINDING')
    before=load(folder/'baseline/comparison_reference.json');after=load(folder/'actual/comparison_reference.json')
    expected_runs={'sprint8':'875c56c278','sprint9':'0a60362503'}
    for role,fp in expected_runs.items():
        if before.get(role,{}).get('fingerprint')!=fp or after.get(role,{}).get('fingerprint')!=fp:raise ValueError('WRONG_PREDECESSOR_RUN')
    json_files={}
    for name in ['comparison_reference.json','compatibility_report.json']:
        old=load(folder/'baseline'/name);new=load(folder/'actual'/name)
        if set(new)!=set(BASELINE_JSON_KEYS[name])|{'fingerprint','run_identity'}:raise ValueError('NEW_JSON_KEYS_CHANGED')
        for key in set(old)|set(new):
            if key not in TOLERANCE['allowed_metadata_differences'] and old.get(key)!=new.get(key):raise ValueError('COMPARISON_STATUS_CHANGED')
        json_files[name]={'status':'VALID','baseline_sha256':sha((folder/'baseline'/name).read_bytes()),
            'actual_sha256':sha((folder/'actual'/name).read_bytes()),'nonpermitted_difference_count':0,
            'allowed_changed_fields':sorted(k for k in set(old)|set(new) if old.get(k)!=new.get(k)),
            'checks':['exact key set','unchanged scientific content','receipt hashes','reviewed baseline']}
    # The reviewed original table pins membership without exposing the Drive-only
    # split/exclusion files to this laptop or to scientific model workspaces.
    baseline_rows=list(csv.DictReader(safe(folder/'baseline','all_percase.csv').open(newline='')))
    expected_cases={row['case'] for row in baseline_rows}
    if len(expected_cases)!=99:raise ValueError('DEVELOPMENT_MEMBERSHIP')
    rows=list(csv.DictReader(safe(folder/'actual','all_percase.csv').open(newline='')))
    if {row['case'] for row in rows}!=expected_cases:raise ValueError('RETURN_CASE_MEMBERSHIP')
    identity=after.get('run_identity',{})
    if identity!=identity_expected:raise ValueError('RETURN_RUN_IDENTITY')
    if identity.get('exclusions_sha256')!=manifest['private_files']['excluded_cases.json'] or identity.get('split_manifest_sha256')!=manifest['private_files']['split_manifest.csv']:raise ValueError('RETURN_PRIVATE_INPUT_BINDING')
    if identity.get('exclusions_count')!=(0 if cpu else 1):raise ValueError('RETURN_EXCLUSION_COUNT')
    fingerprint=sha(json.dumps(identity,sort_keys=True).encode())[:12]
    if after.get('fingerprint')!=fingerprint:raise ValueError('RETURN_FINGERPRINT')
    result=compare_tables(folder/'baseline',folder/'actual',BASELINE_PATH,output_expected)
    if cpu:
        for name in TABLES:
            if (folder/'baseline'/name).read_bytes()!=(folder/'actual'/name).read_bytes():
                result['differences'].append({'file':name,'kind':'byte_difference'})
        result['status']='INVALID' if result['differences'] else 'VALID'
        result['tolerance']=expected_tolerance
    result['json_files']=json_files
    result.update(run_id=manifest['run_id'],development_count=99,scientific_acceptance=False,
       purpose='Known-case pipeline reproduction; no new efficacy claim',provisional=after['provisional'],training_performed=False,
       manifest_sha256=receipt['manifest_sha256'])
    return result


def validate_return(folder,manifest,private=None):
    # Malformed external records are validation failures, not uncaught parser
    # exceptions. Error values may contain patient data; expose only their type.
    try:return _validate_return(folder,manifest,private)
    except (KeyError,TypeError,AttributeError,IndexError,UnicodeError,OSError,csv.Error) as error:
        raise ValueError('MALFORMED_RETURN_'+type(error).__name__) from None


def validate_cpu_return(folder,manifest):
    try:return _validate_return(folder,manifest,cpu=True)
    except (KeyError,TypeError,AttributeError,IndexError,UnicodeError,OSError,csv.Error) as error:
        raise ValueError('MALFORMED_CPU_RETURN_'+type(error).__name__) from None
