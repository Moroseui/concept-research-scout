"""Authenticate exact submitted regression bytes; use existing synthetic isolation."""
import ast
import copy
import hashlib
import json
from pathlib import Path
import re
import subprocess

SPEC = 'aaa3f14bc5b1a09e25f1a9240824f995cdda50970b9f131a29077b39a4b71c01'
SUBMISSION = '4cfc7d876bd3c89c2b1bfe519bf6b75cc9aafa4401fb7847c0854510c8f3f16e'
MODULE = '8e633a1e72457efa8d59099663ab64e6e43b21dbb0216996c3103aec9a67bd04'
BASELINE = 'fa54d6e41db935c4a7671abe278d4a40423bda41cfce32692b58ed1364638d20'
METHOD = 'e5abe443705a0cf8abff4eb959412863bad90f6a6843e22601b8eaf173fa0f61'
RUNNER = '7ed000c688693bb55e124639535997167b1f7813e85b5028ea3efa78b3d6ca1a'
CALL = 'fed0c73d8288bbf8fda82f96d6559ddb4f6c85ac39f927e53939bf909bd7545e'
ANCHOR = ' return unittest.TestSuite([_boundary_tests(),unittest.defaultTestLoader.loadTestsFromTestCase(Checks)])'
RESULT = dict(scope='local generated-state report contract only', module_sha256=MODULE,
              existing_tests=16, extended_tests=17, negative_control='accepted21 E173',
              native_executed=False, patient_computation=False, provider_calls=0,
              model_calls=0, production_ast_unchanged=True)
# Infrastructure argv adapter only. The executed runner and method are the exact
# code blocks from the genuine submitted SPEC; no workspace-runner substitution.
ENTRY = b"import runpy,sys\nsys.argv=['/package/report_lifecycle_regression.py','/package/current.py','/package/baseline.py']\nrunpy.run_path(sys.argv[0],run_name='__main__')\n"


def sha(raw): return hashlib.sha256(raw).hexdigest()
def canonical(value): return json.dumps(value, sort_keys=True, separators=(',', ':')).encode()
def require(ok, why):
    if not ok: raise ValueError('SPEC_REGRESSION_' + why)


def authenticate(spec, submission, current, baseline):
    for raw, pin in ((spec,SPEC),(submission,SUBMISSION),(current,MODULE),(baseline,BASELINE)):
        require(sha(raw)==pin,'AUTHOR_BYTES_CHANGED')
    record=json.loads(submission)
    require(record['files']['SPEC.proposed.md']==SPEC and record['bindings']['call_id']==CALL
            and record['bindings']['round']==23 and record['bindings']['stage']=='run_spec_author',
            'SUBMISSION_BINDING')
    blocks=re.findall(rb'```python\r?\n(.*?)```',spec,re.S)
    require(len(blocks)==2 and [sha(x) for x in blocks]==[METHOD,RUNNER],'SUBMITTED_CODE_BLOCKS')
    # Every original test and every production node stays identical. Only the
    # already-authored fixture body differs in the preserved module.
    old,new=ast.parse(baseline),ast.parse(current)
    for tree in (old,new):
        found=[x for x in tree.body if isinstance(x,ast.FunctionDef) and x.name=='_native_diagnostic_fixture']
        require(len(found)==1,'FIXTURE_MEMBERSHIP');found[0].body=[]
    require(ast.dump(old)==ast.dump(new),'ORIGINAL_AST_CHANGED')
    source=current.decode();require(source.count(ANCHOR)==1,'TEST_ANCHOR')
    derived=source.replace(ANCHOR,blocks[0].decode()+ANCHOR).encode()
    return {'run.py':ENTRY,'current.py':current,'baseline.py':baseline,
            'report_lifecycle_method.txt':blocks[0],'report_lifecycle_regression.py':blocks[1]},derived


def verify_receipt(folder, binding):
    from orchestrator import private_records as pr
    folder=Path(folder);pr.check_tree(folder)
    receipt=json.loads(pr.check(folder/'receipt.json').read_bytes())
    require(receipt.get('schema')=='item4-submitted-regression-execution/v1'
            and receipt.get('binding')==binding,'RECEIPT_BINDING')
    members={str(p.relative_to(folder)) for p in folder.rglob('*') if p.is_file()}
    require(members==set(receipt['preserved_files'])|{'receipt.json'},'RECEIPT_MEMBERS')
    for name,pin in receipt['preserved_files'].items():
        rel=Path(name);require(not rel.is_absolute() and '..' not in rel.parts,'RECEIPT_PATH')
        require(sha(pr.check(folder/rel).read_bytes())==pin,'EVIDENCE_CHANGED')
    require(receipt['status']=='PASS' and receipt['exit_code']==0 and receipt['result']==RESULT,'TESTS_REQUIRED')
    isolation=receipt['isolation']
    require(isolation.get('status')=='ISOLATED' and isolation.get('network')=='UNSHARED'
            and isolation.get('credentials') is False and isolation.get('patient_mounts') is False
            and isolation.get('package_read_only') is True,'ISOLATION_REQUIRED')
    require(json.loads(pr.check(folder/'workspace/isolation.json').read_bytes())==isolation,'ISOLATION_BINDING')
    lines=pr.check(folder/'stdout.log').read_bytes().splitlines()
    require(lines and json.loads(lines[-1])==RESULT,'RESULT_BINDING')
    for name,pin in binding['files'].items():
        require(receipt['preserved_files'].get('package/'+name)==pin,'PACKAGE_BINDING')
    return receipt


def execute(folder, files, config):
    """One isolated synthetic invocation; an incomplete or failed run never retries."""
    from orchestrator import notebook_synthetic as ns,private_records as pr
    from orchestrator.manual_driver import write_once
    folder=Path(folder)
    binding={'files':{n:sha(raw) for n,raw in files.items()},'environment':config,
             'timeout_seconds':120,'patient_data':False,'submission_sha256':SUBMISSION}
    if folder.exists():
        require((folder/'receipt.json').is_file(),'INCOMPLETE_RECONCILE')
        return verify_receipt(folder,binding)
    pr.mkdir(folder,parents=True);pr.mkdir(folder/'package');pr.mkdir(folder/'workspace')
    for name,raw in files.items():
        require(Path(name).name==name,'PACKAGE_PATH');write_once(folder/'package'/name,raw)
    command=ns.command(config,folder/'package',folder/'workspace',binding['files'])
    write_once(folder/'intent.json',canonical(binding))
    try:
        result=subprocess.run(command,capture_output=True,timeout=120,close_fds=True,stdin=subprocess.DEVNULL)
        out,err,code=result.stdout,result.stderr,result.returncode
    except subprocess.TimeoutExpired as e:
        out,err,code=e.stdout or b'',e.stderr or b'',124
    write_once(folder/'stdout.log',out);write_once(folder/'stderr.log',err)
    for name,pin in binding['files'].items():
        require(sha(pr.check(folder/'package'/name).read_bytes())==pin,'PACKAGE_CHANGED_AFTER')
    isolation=json.loads(pr.check(folder/'workspace/isolation.json').read_bytes())
    try: result=json.loads(out.splitlines()[-1])
    except (ValueError,IndexError): result=None
    receipt={'schema':'item4-submitted-regression-execution/v1','binding':binding,
             'status':'PASS' if code==0 and result==RESULT else 'FAIL','exit_code':code,
             'result':result,'isolation':isolation,'native_executed':False,'scientific_acceptance':False,
             'preserved_files':{str(p.relative_to(folder)):sha(p.read_bytes()) for p in folder.rglob('*') if p.is_file()}}
    write_once(folder/'receipt.json',canonical(receipt))
    return verify_receipt(folder,binding)


def equivalent(original_audit, raw, p, derived, receipt):
    """Use the original strict additive-test check on the author's temporary copy."""
    require(sha(raw)==MODULE and receipt.get('status')=='PASS' and receipt.get('result')==RESULT,
            'EXACT_QUALIFIED_MODULE')
    checked=original_audit(derived,p)  # Original tests/prefix/interface/duplicates all checked.
    require(checked['added_contract_tests']==['test_report_lifecycle'],'EXACT_ADDITIVE_TEST')
    return {**checked,'module_sha256':MODULE,'test_copy_sha256':sha(derived),
            'added_test_location':'submitted SPEC; isolated temporary module copy',
            'supplemental_receipt_sha256':sha(canonical(receipt)),
            'corrected_fixture_executed':False,'scientific_acceptance':False}
