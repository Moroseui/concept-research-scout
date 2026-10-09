"""Item6 CPU interfaces and aggregate validation; scientific choices are authored."""
import hashlib
import json
import re
from pathlib import Path
from orchestrator.experiment_result import strict
from orchestrator.scientific_view_scan import scan
from orchestrator import private_records as pr

PURPOSE = 'M4_ITEM6_CPU'
SOURCE_CAPTURE = 'c742b81d9f561dec9cb330c8f4b59f6c9df36b5136819f3bbf1a171c8891b119'
INPUT_COUNT = 728
KINDS = {'tree-scores','small-unet-scores','fold-receipt','tree-result-table','small-unet-result-table','nnunet-result-table','feature-and-label-cache','tree-mask','small-unet-mask','nnunet-mask','nnunet-native-segmentation','nnunet-native-probabilities','sprint13a-probability-cache','saved-result-table'}

def encoded(value):return json.dumps(value,sort_keys=True,allow_nan=False).encode()
def sha(raw):return hashlib.sha256(raw).hexdigest()
def require(value,code):
    if not value:raise ValueError(code)

def program_contract(value):
    require(isinstance(value,dict) and set(value)=={'schema','outputs','validation_checks','requirements','input_contract_sha256','input_capture_sha256'},'DIAGNOSTICS_PROGRAM_CONTRACT')
    require(value['schema']=='diagnostics-program-contract/v1','DIAGNOSTICS_PROGRAM_CONTRACT')
    require(isinstance(value['input_capture_sha256'],str) and re.fullmatch('[0-9a-f]{64}',value['input_capture_sha256']) and isinstance(value['input_contract_sha256'],str) and re.fullmatch('[0-9a-f]{64}',value['input_contract_sha256']),'DIAGNOSTICS_PROGRAM_INPUT_BINDING')
    outputs=value['outputs'];checks=value['validation_checks'];requirements=value['requirements']
    require(isinstance(outputs,list) and 2<=len(outputs)<=32 and all(isinstance(n,str) for n in outputs) and len(set(outputs))==len(outputs) and 'validation.json' in outputs,'DIAGNOSTICS_OUTPUTS')
    for name in outputs:
        require(isinstance(name,str) and re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.-]*',name) and Path(name).suffix in {'.json','.csv','.md','.txt'},'DIAGNOSTICS_OUTPUTS')
        scan(name.encode(),frozenset(),kind='aggregate')
    require(isinstance(checks,list) and 1<=len(checks)<=64 and all(isinstance(x,str) and re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]{0,95}',x) for x in checks) and len(set(checks))==len(checks),'DIAGNOSTICS_CHECKS')
    require(isinstance(requirements,dict) and set(requirements)=={'python','distributions'},'DIAGNOSTICS_REQUIREMENTS')
    require(isinstance(requirements['python'],str) and re.fullmatch(r'[0-9]+\.[0-9]+',requirements['python']),'DIAGNOSTICS_REQUIREMENTS')
    distributions=requirements['distributions']
    require(isinstance(distributions,dict) and len(distributions)<=32,'DIAGNOSTICS_REQUIREMENTS')
    for name,version in distributions.items():
        require(isinstance(name,str) and re.fullmatch('[A-Za-z0-9][A-Za-z0-9_.-]*',name) and isinstance(version,str) and re.fullmatch('[A-Za-z0-9][A-Za-z0-9.+_-]*',version),'DIAGNOSTICS_REQUIREMENTS')
    scan(encoded(value),frozenset(),kind='plan')
    return value

def input_contract(value,cohort_raw,source_raw):
    from orchestrator.modal_development_inputs import COHORT
    require(sha(cohort_raw)==COHORT and sha(source_raw)==SOURCE_CAPTURE,'DIAGNOSTICS_FROZEN_COHORT_OR_CAPTURE')
    cohort=strict(cohort_raw);cases=cohort.get('cases') if isinstance(cohort,dict) else None
    require(isinstance(cases,list) and len(cases)==99 and all(isinstance(c,str) and re.fullmatch(r'sub-stroke[0-9]{4}',c) for c in cases) and len(set(cases))==99 and cohort.get('count')==99,'DIAGNOSTICS_FROZEN_COHORT')
    rows=[strict(line) for line in source_raw.splitlines()]
    require(len(rows)==INPUT_COUNT+1 and rows[-1]=={'files':INPUT_COUNT,'status':'COMPLETE'},'DIAGNOSTICS_CAPTURE_COMPLETE')
    expected={}
    for row in rows[:-1]:
        require(isinstance(row,dict) and set(row)=={'bytes','kind','modified_utc','relative_path','sha256'},'DIAGNOSTICS_CAPTURE_RECORD')
        name=row['relative_path']
        require(isinstance(name,str) and re.fullmatch(r'[A-Za-z0-9_./-]+',name) and not name.startswith('/') and all(p not in {'','.','..'} for p in name.split('/')) and name not in expected,'DIAGNOSTICS_INPUT_PATH')
        require(row['kind'] in KINDS and isinstance(row['sha256'],str) and re.fullmatch('[0-9a-f]{64}',row['sha256']) and type(row['bytes']) is int and 0<row['bytes']<=2*1024**3,'DIAGNOSTICS_INPUT_MEMBER_HASH')
        scan(name.encode(),frozenset(cases),kind='code')
        expected[name]={k:row[k] for k in ('sha256','bytes','kind')}
    selected={'schema':'diagnostics-inputs/v1','scope':'DEVELOPMENT_99_ONLY','cohort_sha256':COHORT,'source_evidence_sha256':SOURCE_CAPTURE,'files':expected}
    require(value==selected,'DIAGNOSTICS_INPUT_EXACT_FROZEN_MEMBERS')
    require(sum(row['bytes'] for row in expected.values())<=128*1024**3,'DIAGNOSTICS_INPUT_TOTAL')
    return value


def validate_outputs(folder,binding):
    contract=program_contract(binding['program_contract']);folder=Path(folder);pr.check_tree(folder)
    paths={str(p.relative_to(folder)):p for p in folder.rglob('*') if p.is_file()}
    require(set(paths)==set(contract['outputs']),'DIAGNOSTICS_RESULT_MEMBERS')
    files={};scans={};bodies={}
    for name,p in paths.items():
        require(p.stat().st_size<=1500000,'DIAGNOSTICS_RESULT_LIMIT')
        raw=p.read_bytes();scans[name]=scan(raw,frozenset(),kind='aggregate')
        if p.suffix=='.json':strict(raw)
        files[name]={'sha256':sha(raw),'bytes':len(raw)};bodies[name]=raw
    expected={'schema':'diagnostics-validation/v1',**{k:binding[k] for k in ('run_id','source','spec_sha256','code_sha256','execution_plan_sha256','input_contract_sha256','environment_sha256')}}
    validation=strict(bodies['validation.json'])
    require(isinstance(validation,dict) and set(validation)==set(expected)|{'files','checks'} and all(validation.get(k)==v for k,v in expected.items()),'DIAGNOSTICS_VALIDATION_BINDING')
    nonvalidation={k:v for k,v in files.items() if k!='validation.json'}
    require(validation['files']==nonvalidation,'DIAGNOSTICS_VALIDATION_FILES')
    checks=validation['checks'];require(isinstance(checks,list) and len(checks)==len(contract['validation_checks']),'DIAGNOSTICS_VALIDATION_CHECKS')
    evidence=set()
    for ident,row in zip(contract['validation_checks'],checks):
        require(isinstance(row,dict) and set(row)=={'id','status','evidence'} and row['id']==ident and row['status']=='PASS' and isinstance(row['evidence'],list) and row['evidence'] and len(set(row['evidence']))==len(row['evidence']) and all(n in nonvalidation for n in row['evidence']),'DIAGNOSTICS_CHECK_FAILED_OR_MISSING')
        evidence.update(row['evidence'])
    require(evidence==set(nonvalidation),'DIAGNOSTICS_UNCHECKED_OUTPUT')
    return {'schema':'diagnostics-result/v1','status':'VALIDATED',**{k:v for k,v in expected.items() if k!='schema'},'files':files,'checks':checks,'scans':scans,'scientifically_accepted':False}
