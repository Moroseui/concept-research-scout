"""One report-lifecycle author correction with four failures; no review or compute entrypoint."""
from pathlib import Path
import hashlib
import importlib.util
import json
import os
import sys
CHANGE='item4-report-snapshot-author-20261010'
REVIEW_CHANGE='item4-report-snapshot-host-repair-20261010'
ROOT=Path('/opt/research-system/manual-repair-helpers')/CHANGE
RECORD=Path('/var/lib/research-system-manual-sprint10-deployment')/CHANGE
PRIOR=Path('/opt/research-system/manual-repair-helpers/item4-smoke-scientific-review-20261010/tools/item4_smoke_review_runtime.py')
PRIOR_SHA='98208d5e8366c05fa2f400cc76bca5e4efc85400c5fcb272b13fec7a53095ac2'
PRIOR_REVIEW='fb04e156b4b29bfbc99e86437d7266ce1df51186f72c0baef754d39a0dac1aef'
FILES=('tools/item4_smoke_response_runtime.py','tools/install_item4_smoke_response.py',
    'orchestrator/item4_smoke_response.py','orchestrator/item4_scoped_calls.py','orchestrator/dispatch_limiter.py',
    'docs/ITEM4_POST_SMOKE_RESPONSE_PRIVATE.json','docs/ITEM4_RESPONSE_TIMING_AUDIT.json',
    'docs/ITEM4_RESPONSE_NATIVE_TRAINER.py','docs/ITEM4_STAGE1_CAP_OPERATOR_DECISION_20261009.txt',
    'orchestrator/modal_nnunet.py','orchestrator/modal_fit_progress.py',
    'tools/item4_response_host_operation.py','docs/ITEM4_RESPONSE_HOST_PRIVATE.json',
    'docs/ITEM4_CPU_DIAGNOSTIC_PRIVATE.json','docs/ITEM4_CPU_DIAGNOSTIC_OPERATOR_DECISION.txt',
    'docs/ITEM4_CPU_DIAGNOSTIC_RECOVERY_PRIVATE.json','orchestrator/author_format_submission.py',
    'orchestrator/author_output_schema.py','orchestrator/notebook_execution.py',
    'orchestrator/experiment_plan_validation.py','orchestrator/experiment_environment_requirements.py',
    'orchestrator/modal_billing.py','docs/ITEM4_CPU_DIAGNOSTIC_SCOPED_REVIEW_PRIVATE.json',
    'docs/ITEM4_CPU_DIAGNOSTIC_NATIVE_HARNESS_PRIVATE.json',
    'docs/ITEM4_PREVIOUS_NATIVE_HARNESS.py','docs/ITEM4_NATIVE_WORKER_INTERFACE.py',
    'docs/ITEM4_CPU_DIAGNOSTIC_PLAINTEXT_PRIVATE.json','docs/ITEM4_AUTHOR18_DECODED_REFERENCE_PRIVATE.py',
    'orchestrator/scientific_view_scan.py','orchestrator/privacy_patterns.py',
    'orchestrator/item4_fixture_correction.py','tools/item4_validation_retained.py',
    'docs/ITEM4_CPU_DIAGNOSTIC_FIXTURE_PRIVATE.json','docs/ITEM4_AUTHOR19_NATIVE_REFERENCE_PRIVATE.py',
    'docs/ITEM4_WHOLE_FIXTURE_AUTHOR_PRIVATE.json','docs/ITEM4_AUTHOR20_NATIVE_REFERENCE_PRIVATE.py',
    'docs/ITEM4_REPORT_SNAPSHOT_AUTHOR_PRIVATE.json','docs/ITEM4_AUTHOR21_NATIVE_REFERENCE_PRIVATE.py',
    'docs/ITEM4_REPORT_SNAPSHOT_REPRO_PRIVATE.py','docs/ITEM4_REPORT_SNAPSHOT_REPRO_RESULT_PRIVATE.json',
    'docs/ITEM4_PROGRESS_NATIVE_FAILURE_PRIVATE.json','tools/item4_native_worker.py')


def sha(raw):return hashlib.sha256(raw).hexdigest()
def require(ok,why):
    if not ok:raise ValueError('SMOKE_RESPONSE_RUNTIME_'+why)
def trusted(path):
    path=Path(path)
    for p in [path,*path.parents]:
        st=p.lstat();require(not p.is_symlink() and st.st_uid==0 and not st.st_mode&0o022,'TRUSTED_SOURCE')
    return path
def module(name,path):
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec)
    sys.modules[name]=m;spec.loader.exec_module(m);return m


def authority():
    from orchestrator.autonomy_review import verify_result
    installed=json.loads(trusted(RECORD/'installed.json').read_bytes())
    result=verify_result(trusted(RECORD/'review'))
    manifest=json.loads(trusted(RECORD/'review/packet-manifest.json').read_bytes())
    require(result['verdict']=='APPROVE' and result['change_id']==REVIEW_CHANGE and
        result['source_sha']==installed['source']==manifest['source_sha'] and
        result['report_sha256']==installed['review_sha256'],'GENUINE_APPROVAL')
    require(set(installed['files'])==set(FILES),'INSTALL_MEMBERS')
    for name in FILES:
        require(sha(trusted(ROOT/name).read_bytes())==installed['files'][name]==manifest['source_files'][name],'SOURCE_CHANGED')
    require(Path(__file__).resolve()==ROOT/FILES[0],'EXECUTED_SOURCE')
    unit=Path('/etc/systemd/system')/('research-'+CHANGE+'.service')
    require(installed['units']=={str(unit):sha(trusted(unit).read_bytes())},'UNIT_CHANGED')
    return result


def historical_response():
    """Authenticate the already-consumed pair without wrapping its runtime."""
    from orchestrator.autonomy_review import verify_result
    record=Path('/var/lib/research-system-manual-sprint10-deployment/item4-post-smoke-response-20261010/review')
    old=verify_result(trusted(record))
    require(old['verdict']=='APPROVE' and old['source_sha']=='90da59b2f67e2e32c2232f170135199b11bdc036'
        and old['report_sha256']=='ad2bb148d756a450bc0a9f1f242ee77f31a08dfbd28d4ef9514ae88e92e3ddee',
        'HISTORICAL_RESPONSE_APPROVAL')
    manifest=json.loads(trusted(record/'packet-manifest.json').read_bytes())
    require(sha(trusted(ROOT/'docs/ITEM4_POST_SMOKE_RESPONSE_PRIVATE.json').read_bytes())==
        manifest['source_files']['docs/ITEM4_POST_SMOKE_RESPONSE_PRIVATE.json'],'HISTORICAL_RESPONSE_SCOPE')
    return old['report_sha256']


def historical_diagnostic():
    from orchestrator.autonomy_review import verify_result
    record=Path('/var/lib/research-system-manual-sprint10-deployment/item4-cpu-starvation-diagnostic-20261010/review')
    result=verify_result(trusted(record))
    require(result['verdict']=='APPROVE' and result['source_sha']=='7dc3d1da418c0e7c53aae65ea14739e9b686221d'
        and result['report_sha256']=='f009c2c6e8459b4ad545f7c1d13badb39c6ae6443ebb2f75dfb27403282888ea','HISTORICAL_DIAGNOSTIC_APPROVAL')
    manifest=json.loads(trusted(record/'packet-manifest.json').read_bytes())
    require(sha(trusted(ROOT/'docs/ITEM4_CPU_DIAGNOSTIC_PRIVATE.json').read_bytes())==manifest['source_files']['docs/ITEM4_CPU_DIAGNOSTIC_PRIVATE.json'],
        'HISTORICAL_DIAGNOSTIC_SCOPE')
    direction=verify_result(trusted(Path('/var/lib/research-system-manual-sprint10-deployment/item4-author18-plaintext-recovery-20261010/direction')))
    require(direction['verdict']=='APPROVE' and direction['change_id']=='item4-author16-entrypoint-recovery-20261010'
        and direction['source_sha']==result['source_sha'] and direction['report_sha256']=='ddcdc756df490d35c42784b8ede667be783ca72a2161bb938c4888745a43b9ca',
        'RECOVERY_DIRECTION_APPROVAL')
    return result['report_sha256']


def historical_recovery():
    from orchestrator.autonomy_review import verify_result
    record=Path('/var/lib/research-system-manual-sprint10-deployment/item4-author16-entrypoint-recovery-20261010/review')
    result=verify_result(trusted(record))
    require(result['verdict']=='APPROVE' and result['source_sha']=='3577bcca8e89f5308e49da382939ea04e3891aa4'
        and result['report_sha256']=='a13832042a73361de181ed18e4722462f2a69e89a814af16a90b6955a9a93605','HISTORICAL_RECOVERY_APPROVAL')
    manifest=json.loads(trusted(record/'packet-manifest.json').read_bytes())
    require(sha(trusted(ROOT/'docs/ITEM4_CPU_DIAGNOSTIC_RECOVERY_PRIVATE.json').read_bytes())==
        manifest['source_files']['docs/ITEM4_CPU_DIAGNOSTIC_RECOVERY_PRIVATE.json'],'HISTORICAL_RECOVERY_SCOPE')
    return result['report_sha256']


def historical_scoped_review():
    from orchestrator.autonomy_review import verify_result
    record=Path('/var/lib/research-system-manual-sprint10-deployment/item4-diagnostic-scoped-review-20261010/review')
    result=verify_result(trusted(record))
    require(result['verdict']=='APPROVE' and result['source_sha']=='491542ae31d593517fa7a2520ba2b63e23f6c3fa'
        and result['report_sha256']=='a77a3998a92339f4a8eca41c893c0e54911720c9c424f583dc0cf7dc7a8d7756',
        'HISTORICAL_SCOPED_REVIEW_APPROVAL')
    manifest=json.loads(trusted(record/'packet-manifest.json').read_bytes())
    name='docs/ITEM4_CPU_DIAGNOSTIC_SCOPED_REVIEW_PRIVATE.json'
    require(sha(trusted(ROOT/name).read_bytes())==manifest['source_files'][name],'HISTORICAL_SCOPED_REVIEW_SCOPE')
    return result['report_sha256']


def historical_native_harness():
    from orchestrator.autonomy_review import verify_result
    record=Path('/var/lib/research-system-manual-sprint10-deployment/item4-diagnostic-native-harness-20261010/review')
    result=verify_result(trusted(record))
    require(result['verdict']=='APPROVE' and result['source_sha']=='f80421dabdf05dd900147adf114f1450b702ef02'
        and result['report_sha256']=='a51934e4bf446c5b19ba96c6877049947975fe6ebab146fccff6f75285f4484a',
        'HISTORICAL_NATIVE_HARNESS_APPROVAL')
    manifest=json.loads(trusted(record/'packet-manifest.json').read_bytes())
    name='docs/ITEM4_CPU_DIAGNOSTIC_NATIVE_HARNESS_PRIVATE.json'
    require(sha(trusted(ROOT/name).read_bytes())==manifest['source_files'][name],'HISTORICAL_NATIVE_SCOPE')
    return result['report_sha256']


def historical_plaintext():
    from orchestrator.autonomy_review import verify_result
    record=Path('/var/lib/research-system-manual-sprint10-deployment/item4-author18-plaintext-recovery-20261010/review')
    old=verify_result(trusted(record))
    require(old['verdict']=='APPROVE' and old['source_sha']=='5b884b7c45f64957e6f8c9952529a079e4fea94f'
        and old['report_sha256']=='ff43deb433ca844548298b459295cd8c4db14bafb9bfcb8699d017be9e9e108b','PLAINTEXT_APPROVAL')
    manifest=json.loads(trusted(record/'packet-manifest.json').read_bytes())
    name='docs/ITEM4_CPU_DIAGNOSTIC_PLAINTEXT_PRIVATE.json'
    require(sha(trusted(ROOT/name).read_bytes())==manifest['source_files'][name],'PLAINTEXT_SCOPE')
    return old['report_sha256']


_failure_proof=None
def failure_qualification():
    global _failure_proof
    if _failure_proof is not None:return dict(_failure_proof)
    import subprocess
    raw=subprocess.check_output(['/usr/bin/python3','-s','-B',str(ROOT/'tools/item4_validation_retained.py'),
        '--diagnostic-failure'],timeout=180)
    _failure_proof=json.loads(raw)
    return dict(_failure_proof)


def fixture_direction():
    from orchestrator.autonomy_review import verify_result
    result=verify_result(trusted(Path('/var/lib/research-system-manual-sprint10-deployment/item4-native-fixture-correction-20261010/direction')))
    require(result['verdict']=='APPROVE' and result['source_sha']=='81cd8225365a26944128ab5eb3fceda9e36d5f3d'
        and result['change_id']=='item4-native-failure-direction-20261010'
        and result['report_sha256']=='93eb8a687a27133bd4f355d403546357e19c6f7faab04fda124a72ec7ee4aa22',
        'FIXTURE_DIRECTION')



def historical_fixture():
    from orchestrator.autonomy_review import verify_result
    record=Path('/var/lib/research-system-manual-sprint10-deployment/item4-native-fixture-correction-20261010/review')
    result=verify_result(trusted(record))
    require(result['verdict']=='APPROVE' and result['source_sha']=='e50aa51bd1973517973bb94ba0056c1f375a530d'
        and result['report_sha256']=='da282dcc042bef7a597789362ded7a0b6db31bacd641f7fffce95219c79d64cd','FIXTURE_APPROVAL')
    manifest=json.loads(trusted(record/'packet-manifest.json').read_bytes())
    name='docs/ITEM4_CPU_DIAGNOSTIC_FIXTURE_PRIVATE.json'
    require(sha(trusted(ROOT/name).read_bytes())==manifest['source_files'][name],'FIXTURE_HISTORY_CHANGED')
    return result['report_sha256']


def audit_direction():
    # Authentic advice, not approval: the separate implementation APPROVE is
    # the only release/grant authority. Its review must explicitly judge scope.
    from orchestrator.autonomy_review import verify_result
    result=verify_result(trusted(RECORD/'direction'))
    require(result['verdict']=='REVISE' and result['source_sha']=='b60badd65283e7df5f801a6a6a20b3fd63504544'
        and result['change_id']=='item4-second-native-failure-direction-20261010'
        and result['report_sha256']=='e9636a72940a498855af4d8585e6f549ac87a380e7d0fa634408451a9fe925a3',
        'AUDIT_DIRECTION_EVIDENCE')


_audit_failure_proof=None
def audit_failure_qualification():
    global _audit_failure_proof
    if _audit_failure_proof is None:
        import subprocess
        raw=subprocess.check_output(['/usr/bin/python3','-s','-B',str(ROOT/'tools/item4_validation_retained.py'),
            '--diagnostic-audit-failure'],timeout=180)
        _audit_failure_proof=json.loads(raw)
    return dict(_audit_failure_proof)


def historical_audit():
    from orchestrator.autonomy_review import verify_result
    record=Path('/var/lib/research-system-manual-sprint10-deployment/item4-whole-fixture-author-20261010/review')
    result=verify_result(trusted(record))
    require(result['verdict']=='APPROVE' and result['source_sha']=='28a6e1a5893ac0db848b206c9e073bc482eef222'
        and result['report_sha256']=='931c7a1a43e90b15e39c427e804e7af12ec20b3ef88b27ef92ecedcd3b8253be','HISTORICAL_AUDIT_APPROVAL')
    manifest=json.loads(trusted(record/'packet-manifest.json').read_bytes())
    require(sha(trusted(ROOT/'docs/ITEM4_WHOLE_FIXTURE_AUTHOR_PRIVATE.json').read_bytes())==
        manifest['source_files']['docs/ITEM4_WHOLE_FIXTURE_AUTHOR_PRIVATE.json'],'HISTORICAL_AUDIT_SCOPE')
    return result['report_sha256']

_snapshot_proof=None
_progress_proof=None
def snapshot_failure_qualification():
    global _snapshot_proof
    if _snapshot_proof is None:
        import subprocess
        _snapshot_proof=json.loads(subprocess.check_output(['/usr/bin/python3','-s','-B',
            str(ROOT/'tools/item4_validation_retained.py'),'--diagnostic-report-failure'],timeout=180))
    return dict(_snapshot_proof)

def progress_failure_qualification():
    global _progress_proof
    if _progress_proof is None:
        import subprocess
        _progress_proof=json.loads(subprocess.check_output(['/usr/bin/python3','-s','-B',
            str(ROOT/'tools/item4_validation_retained.py'),'--diagnostic-progress-failure'],timeout=180))
    return dict(_progress_proof)


def connect():
    approved=authority();old_approval=historical_response();diagnostic_approval=historical_diagnostic();recovery_approval=historical_recovery();scoped_approval=historical_scoped_review();native_approval=historical_native_harness();plaintext_approval=historical_plaintext();fixture_direction();fixture_approval=historical_fixture();audit_direction();audit_approval=historical_audit()
    require(sha(trusted(PRIOR).read_bytes())==PRIOR_SHA,'PRIOR_SOURCE_CHANGED')
    route=module('_post_smoke_prior',PRIOR);original_factory=route.module;substituted=[]
    def factory(name,path):
        if name!='orchestrator.item4_scoped_calls':return original_factory(name,path)
        require(Path(path)==route.ROOT/'orchestrator/item4_scoped_calls.py' and not substituted,'SCOPED_FACTORY')
        import orchestrator
        fixture=module('orchestrator.item4_fixture_correction',ROOT/'orchestrator/item4_fixture_correction.py')
        fixture._verifier=failure_qualification;fixture._audit_verifier=audit_failure_qualification;fixture._snapshot_verifier=snapshot_failure_qualification;fixture._progress_verifier=progress_failure_qualification;orchestrator.item4_fixture_correction=fixture
        helper=module('orchestrator.item4_smoke_response',ROOT/'orchestrator/item4_smoke_response.py')
        orchestrator.item4_smoke_response=helper
        p=json.loads(trusted(ROOT/helper.DOCUMENT).read_bytes());helper.scope(p,old_approval)
        diagnostic=json.loads(trusted(ROOT/'docs/ITEM4_CPU_DIAGNOSTIC_PRIVATE.json').read_bytes())
        helper.scope(diagnostic,diagnostic_approval)
        recovery=json.loads(trusted(ROOT/helper.RECOVERY_DOCUMENT).read_bytes());helper.scope(recovery,recovery_approval)
        scoped_review=json.loads(trusted(ROOT/helper.SCOPED_DOCUMENT).read_bytes());helper.scope(scoped_review,scoped_approval)
        native_harness=json.loads(trusted(ROOT/helper.NATIVE_DOCUMENT).read_bytes());helper.scope(native_harness,native_approval)
        plaintext=json.loads(trusted(ROOT/helper.PLAINTEXT_DOCUMENT).read_bytes());helper.scope(plaintext,plaintext_approval)
        correction=json.loads(trusted(ROOT/helper.FIXTURE_DOCUMENT).read_bytes());helper.scope(correction,fixture_approval)
        audit_scope=json.loads(trusted(ROOT/helper.AUDIT_DOCUMENT).read_bytes());helper.scope(audit_scope,audit_approval)
        snapshot_scope=json.loads(trusted(ROOT/helper.SNAPSHOT_DOCUMENT).read_bytes());helper.scope(snapshot_scope,approved['report_sha256'])
        require(sha(trusted(ROOT/'docs/ITEM4_CPU_DIAGNOSTIC_OPERATOR_DECISION.txt').read_bytes())==helper.DIAGNOSTIC_DECISION,'OPERATOR_DECISION')
        calls=module(name,ROOT/'orchestrator/item4_scoped_calls.py');orchestrator.item4_scoped_calls=calls
        original=calls.connect
        def scoped(*args,**kw):
            require(not {'post_smoke','post_smoke_approval','diagnostic','diagnostic_approval','diagnostic_recovery','diagnostic_recovery_approval','diagnostic_scoped','diagnostic_scoped_approval','diagnostic_native','diagnostic_native_approval','diagnostic_plaintext','diagnostic_plaintext_approval','diagnostic_fixture','diagnostic_fixture_approval','fixture_audit','fixture_audit_approval','report_snapshot','report_snapshot_approval'}&set(kw),'DUPLICATE_SCOPE')
            return original(*args,**kw,post_smoke=p,post_smoke_approval=old_approval,
                diagnostic=diagnostic,diagnostic_approval=diagnostic_approval,
                diagnostic_recovery=recovery,diagnostic_recovery_approval=recovery_approval,
                diagnostic_scoped=scoped_review,diagnostic_scoped_approval=scoped_approval,
                diagnostic_native=native_harness,diagnostic_native_approval=native_approval,
                diagnostic_plaintext=plaintext,diagnostic_plaintext_approval=plaintext_approval,
                diagnostic_fixture=correction,diagnostic_fixture_approval=fixture_approval,
                fixture_audit=audit_scope,fixture_audit_approval=audit_approval,
                report_snapshot=snapshot_scope,report_snapshot_approval=approved['report_sha256'])
        calls.connect=scoped;substituted.append(name);return calls
    route.module=factory
    connected,smoke,smoke_p,smoke_approval=route.connect()
    require(substituted==['orchestrator.item4_scoped_calls'] and route.authority()['report_sha256']==PRIOR_REVIEW,'PRIOR_CONNECTION')
    from orchestrator import dispatch_limiter,item4_smoke_response as helper
    limiter=module('_post_smoke_limiter',ROOT/'orchestrator/dispatch_limiter.py')
    dispatch_limiter.admit_manual=limiter.admit_manual
    p=json.loads(trusted(ROOT/helper.SNAPSHOT_DOCUMENT).read_bytes())
    import orchestrator
    for name in ('privacy_patterns','scientific_view_scan','notebook_execution','author_output_schema','author_format_submission'):
        loaded=module('orchestrator.'+name,ROOT/'orchestrator'/(name+'.py'));setattr(orchestrator,name,loaded)
    return connected,smoke,smoke_p,smoke_approval,helper,p,approved['report_sha256']


def retained_smoke_evidence(driver,value,smoke,smoke_p,smoke_approval,helper):
    """Check authentic smoke state before the already-completed response pair.

    Author15 legitimately replaced its author artifacts. Never pass those newer
    mutable artifacts off as the older smoke-review checkpoint, or skip the
    original evidence validation. Execution authority must remain identical.
    """
    old_approval=historical_response()
    old=json.loads(trusted(ROOT/helper.DOCUMENT).read_bytes())
    original=helper.scope(old,old_approval)
    helper.granted(driver.store,old,old_approval)
    require(value.get('post_smoke_response_scope')==helper.proof(old,old_approval),'RETAINED_RESPONSE_GRANT')
    for key in helper.protected_keys(old):
        require(value.get(key)==original.get(key),'RETAINED_EXECUTION_AUTHORITY')
    return smoke.evidence(driver,original,smoke_p,smoke_approval)


def bind_admission(driver,c,original,helper,p,approval):
    from orchestrator import manual_recovery as recovery,stocktake_review_recovery as old_recovery
    saved=(recovery.permit,old_recovery.admission)
    def permit(store,run):
        result=saved[0](store,run)
        if run!=helper.RUN:return result
        require(store is driver.store and result is not None,'LOCAL_OWNER')
        c.originals(driver,*original);helper.granted(store,p,approval)
        return {**result,'preserved_failures':[result['failed_id'],original[3].CALL]}
    def admission(batch,run,stage_name,ident,source,receipt):
        if run!=helper.RUN:return saved[1](batch,run,stage_name,ident,source,receipt)
        require(batch is driver.store.batch and source==driver.config['source'] and
            (stage_name,ident)==('run_spec_author',helper.call(p,'author')),'AUTHOR_ONLY_GLOBAL_OWNER')
        c.originals(driver,*original);helper.ready(driver,driver.current(),p,approval)
        result=saved[0](driver.store,run);require(result is not None,'TIMEOUT_QUALIFICATION')
        return [result['failed_id'],original[3].CALL]
    recovery.permit,old_recovery.admission=permit,admission
    def restore():recovery.permit,old_recovery.admission=saved
    return restore


def supplemental(driver,p):
    names={'current-cap-decision.txt':'docs/ITEM4_STAGE1_CAP_OPERATOR_DECISION_20261009.txt',
        'timing-audit.json':'docs/ITEM4_RESPONSE_TIMING_AUDIT.json','native-trainer.py':'docs/ITEM4_RESPONSE_NATIVE_TRAINER.py',
        'checkpoint-adapter.py':'orchestrator/modal_nnunet.py','durable-progress.py':'orchestrator/modal_fit_progress.py',
        'cpu-diagnostic-operator-decision.txt':'docs/ITEM4_CPU_DIAGNOSTIC_OPERATOR_DECISION.txt'}
    result={name:trusted(ROOT/path).read_bytes() for name,path in names.items()}
    from orchestrator import item4_smoke_response as helper,private_records as pr
    if helper.native_harness(p):
        result['previous-native-harness.py']=trusted(ROOT/('docs/ITEM4_AUTHOR21_NATIVE_REFERENCE_PRIVATE.py' if helper.report_snapshot(p) else 'docs/ITEM4_AUTHOR20_NATIVE_REFERENCE_PRIVATE.py' if helper.fixture_audit(p) else 'docs/ITEM4_AUTHOR19_NATIVE_REFERENCE_PRIVATE.py' if helper.fixture_correction(p) else 'docs/ITEM4_AUTHOR18_DECODED_REFERENCE_PRIVATE.py'
            if helper.plaintext_recovery(p) else 'docs/ITEM4_PREVIOUS_NATIVE_HARNESS.py')).read_bytes()
        result['native-worker-interface.py']=trusted(ROOT/'docs/ITEM4_NATIVE_WORKER_INTERFACE.py').read_bytes()
        if helper.report_snapshot(p):
            for name,path in {'actual-native-worker.py':'tools/item4_native_worker.py',
                'report-lifecycle-counterexample.py':'docs/ITEM4_REPORT_SNAPSHOT_REPRO_PRIVATE.py',
                'report-lifecycle-counterexample-result.json':'docs/ITEM4_REPORT_SNAPSHOT_REPRO_RESULT_PRIVATE.json'}.items():
                result[name]=trusted(ROOT/path).read_bytes()
        return result
    if helper.scoped_review(p):return result
    failed=helper.failed_author(driver.store,p);receipt=json.loads(failed['receipt']);work=Path(receipt['workspace'])
    for target,origin in [('SPEC.md','SPEC.proposed.md'),('notebook.patch.json','notebook.patch.json'),('execution.plan.json','execution.plan.json')]:
        result['failed-author16-'+target]=pr.check(work/origin).read_bytes()
    return result



FAILURE_PREFIX='report-snapshot-failure-'
def failure_pages(driver,p):
    from orchestrator import item4_fixture_correction as fixture,private_records as pr
    from orchestrator.item4_review4_continuation import canonical
    fixture.failure(driver.store,p)
    old=json.loads(trusted(ROOT/fixture.DOCUMENT).read_bytes())
    attempts=[]
    audit=json.loads(trusted(ROOT/fixture.AUDIT_DOCUMENT).read_bytes())
    for scope,qualifier in ((old,failure_qualification),(audit,audit_failure_qualification),(p,snapshot_failure_qualification)):
        frozen=fixture.scope(scope);state=fixture.parameters(scope)['state']
        contents={name:pr.check(state/name).read_bytes().decode() for name in sorted(frozen['files'])}
        attempts.append({'files':contents,'file_sha256':frozen['files'],'qualification':qualifier()})
    third=fixture.STATE.with_name('item4-author21-diagnostic-native-v1')
    third_proof=progress_failure_qualification()
    contents={name:pr.check(third/name).read_bytes().decode() for name in sorted(old['native_failure']['files'])}
    attempts.insert(2,{'files':contents,'file_sha256':{name:sha(raw.encode()) for name,raw in contents.items()},'qualification':third_proof})
    raw=canonical({'schema':'item4-fixture-four-original-failures/v1','attempts':attempts,
        'corrected_fixture_executed':False,'scientific_acceptance':False})
    text=raw.decode();parts=[text[i:i+6000] for i in range(0,len(text),6000)]
    result={f'page-{i+1:03}.txt':part.encode() for i,part in enumerate(parts)}
    result['index.json']=canonical({'schema':'item4-complete-failure-pages/v1','sha256':sha(raw),'bytes':len(raw),
        'pages':[{'name':FAILURE_PREFIX+name,'bytes':len(body),'sha256':sha(body)} for name,body in result.items()],
        'omissions':[],'corrected_fixture_executed':False,'scientific_acceptance':False})
    return result


def deliver_failure(driver,value,p):
    from orchestrator import experiment_collection as collection
    expected=failure_pages(driver,p)
    for name,raw in expected.items():
        collection.artifact(driver,value,'result_tables',FAILURE_PREFIX+name,'report-snapshot-failure/'+name,raw)
    actual=[r for r in value['artifacts'] if r['id'].startswith(FAILURE_PREFIX)]
    require(len(actual)==len(expected) and {r['id']:r['sha256'] for r in actual}==
        {FAILURE_PREFIX+n:sha(raw) for n,raw in expected.items()},'FAILURE_DELIVERY_MEMBERS')
    driver.save(value)


def verify_failure_delivery(driver,value,p):
    from orchestrator import context_budget as cb,private_records as pr
    expected=failure_pages(driver,p)
    actual=[r for r in value['artifacts'] if r['id'].startswith(FAILURE_PREFIX)]
    require(len(actual)==len(expected),'FAILURE_DELIVERY_MEMBERS')
    for ref in actual:
        require(pr.check(cb.relative_file(driver.context,ref['path'])).read_bytes()==expected[ref['id'][len(FAILURE_PREFIX):]],
            'FAILURE_DELIVERY_BYTES')


def author_work():
    return Path('/var/lib/research-system-manual-sprint10/releases/research-manual-sprint10-timeout-continuation-8e042339/item4/lane-scientific-workspaces/run_spec_author-22')


def pins_path():
    return author_work().parent.parent/'lane/report-snapshot-author/runtime-pins-22.json'


def send(expected,family,command):
    require(os.getuid()==os.getgid()==1003 and Path(__file__).resolve()==ROOT/FILES[0],'AUTHOR_SENDER_IDENTITY')
    connect()
    from orchestrator import author_format_submission as af,manual_stage as stage,private_records as pr
    require(Path.cwd().resolve()==author_work() and family=='codex','AUTHOR_SENDER_SCOPE')
    pins=json.loads(pr.check(pins_path()).read_bytes());config=af.load(author_work(),pins[af.CONFIG])
    require(config['bindings']['input_sha256']==expected,'AUTHOR_SENDER_BINDING')
    # The immediate exact dual-ledger admission below owns the round check.
    # Duplicating it here previously contradicted the admitted round (21 vs22).
    author_sender_admitted(config,expected)
    base=['/tools/node','/tools/codex/bin/codex.js','exec','--ignore-user-config','--ignore-rules','--model','gpt-6-astra',
        '-s','workspace-write','-c','approval_policy="never"','-c','sandbox_workspace_write.network_access=false','--json','-']
    require(command==af.client_command(base,author_work(),pins),'AUTHOR_SENDER_COMMAND')
    original=stage.isolation.command
    def protected(workspace,*args,**kw):
        require(Path(workspace).resolve()==author_work(),'AUTHOR_SENDER_WORKSPACE')
        return af.protect_command(original(workspace,*args,**kw),author_work(),pins)
    stage.isolation.command=protected
    try:return stage.send_bound(expected,command,family=family)
    finally:stage.isolation.command=original



def author_sender_admitted(config,expected):
    """A prepared format tool is not permission for an uncounted model call."""
    import sqlite3
    from orchestrator import item4_smoke_response as helper,private_records as pr
    binding=config['bindings'];ident=helper.call({'schema':helper.SNAPSHOT_SCHEMA},'author')
    require(binding['call_id']==ident and binding['round']==22 and binding['stage']=='run_spec_author'
        and binding['run_id']==helper.RUN and binding['input_sha256']==expected,'AUTHOR_SENDER_CALL_BINDING')
    lane=author_work().parent.parent/'lane'
    with sqlite3.connect(pr.check(lane/'jobs.sqlite').as_uri()+'?mode=ro',uri=True) as local, sqlite3.connect(
            'file:/var/lib/research-system-autonomy/reviews/jobs.sqlite?mode=ro',uri=True) as global_db:
        local.row_factory=sqlite3.Row;global_db.row_factory=sqlite3.Row
        row=local.execute('SELECT * FROM manual_calls WHERE id=?',(ident,)).fetchone()
        other=global_db.execute('SELECT * FROM autonomy_calls WHERE id=?',(ident,)).fetchone()
        value=json.loads(local.execute('SELECT payload FROM manual_state WHERE id=1').fetchone()[0])
        pending=value.get('pending') or {}
        require(row is not None and other is not None and row['status']==other['status']=='RUNNING'
            and row['stage']=='run_spec_author' and row['attempt']==22 and value['phase']=='MODEL_RUNNING'
            and pending=={'id':ident,'stage':'run_spec_author','round':22,'workspace':str(author_work())},
            'AUTHOR_SENDER_ADMISSION_REQUIRED')
        receipt=json.loads(row['receipt'])
        require(receipt['input_sha256']==expected and receipt['workspace']==str(author_work()),'AUTHOR_SENDER_RECEIPT')

def author_profile(original,expected,commands,*,sink=False,stage=None):
    if sink or stage!='run_spec_author':return original(expected,commands,sink=sink,stage=stage)
    from orchestrator import author_format_submission as af,private_records as pr
    pins=json.loads(pr.check(pins_path()).read_bytes())
    changed=[(family,af.client_command(command,author_work(),pins) if family=='codex' else command) for family,command in commands]
    text=original(expected,changed,stage=stage)
    before=json.dumps([sys.executable,'-m','orchestrator.manual_stage','--send-bound'])[:-1]
    after=json.dumps([sys.executable,'-s','-B',str(ROOT/'tools/item4_smoke_response_runtime.py'),'send'])[:-1]
    require(text.count(before)==2,'AUTHOR_PROFILE_SENDER_BINDING')
    return text.replace(before,after)


def prepare_author_feedback(driver,p,body,measurement,work):
    from orchestrator import author_format_submission as af,private_records as pr,context_budget as cb
    require(Path(work)==author_work(),'AUTHOR_FEEDBACK_WORKSPACE')
    files=measurement['workspace_files']
    from orchestrator import item4_smoke_response as helper
    receipt=json.loads(helper.reference_author(driver,p)['receipt'])
    patch=json.loads(pr.check(Path(receipt['workspace'])/'notebook.patch.json').read_bytes())
    plan=json.loads(pr.check(Path(receipt['workspace'])/'execution.plan.json').read_bytes())
    views=[ref for ref in files if ref.get('sha256')==patch['view_sha256']]
    require(len(views)==1,'AUTHOR_VISIBLE_VIEW_REQUIRED')
    view=pr.check(cb.relative_file(work,views[0]['path'])).read_bytes()
    require(sha(view)==patch['view_sha256'],'AUTHOR_VISIBLE_VIEW_CHANGED')
    manifests=[]
    for ref in files:
        if ref['path'].endswith('-omissions.json'):
            raw=pr.check(cb.relative_file(work,ref['path'])).read_bytes()
            require(sha(raw)==ref['sha256'],'AUTHOR_OMISSIONS_CHANGED')
            value=json.loads(raw)
            if value.get('view_sha256')==patch['view_sha256']:manifests.append(raw)
    require(len(manifests)==1,'AUTHOR_BOUND_OMISSIONS_REQUIRED')
    binding=helper.review_binding(driver,p,authority()['report_sha256'])
    pins=af.prepare_revision(work,{'call_id':helper.call(p,'author'),'run_id':helper.RUN,'stage':'run_spec_author','round':22,
        'source_sha':driver.config['source'],'runtime_sha256':sha(trusted(Path('/etc/research-system-manual-sprint10/releases/research-manual-sprint10-timeout-continuation-8e042339/runtime.json')).read_bytes()),'input_sha256':sha(body.encode())},
        {'review_call_id':binding['review_call_id'],'review_sha256':binding['review_sha256'],
            'operator_scope_sha256':plan['operator_scope_sha256'],'original_sha256':patch['original_sha256'],'view_sha256':patch['view_sha256']},
        notebook={af.MODULE_VIEW:view,af.MODULE_MANIFEST:manifests[0]})
    with pr.open_file(pins_path(),'xb') as stream:stream.write(af.canonical(pins))
    return pins

def main(argv=None):
    argv=list(sys.argv[1:] if argv is None else argv)
    require(os.getuid()==os.getgid()==1003 and Path(__file__).resolve()==ROOT/FILES[0],'SERVICE_IDENTITY')
    require(len(argv)==1 and argv[0] in {'verify','activate','run'},'ACTION_SCOPE')
    connected,smoke,smoke_p,smoke_approval,helper,p,approval=connect()
    c,policy,original,evidence,base,fresh=connected
    from orchestrator.experiment_driver import ExperimentDriver
    from orchestrator.manual_executor import lock
    from orchestrator import private_records as pr
    restore=None;driver=None
    from orchestrator import manual_stage as stage,author_format_submission as af
    from orchestrator import experiment_context as ec
    saved_accept=ec.accept_author
    def accept_author(current, value, pending):
        require(current is driver and pending['round']==22,'AUTHOR_ACCEPT_SCOPE')
        saved_accept(current,value,pending)
        helper.executable_candidate(current,value,p)
    saved_author=(stage._invoke,stage.transport_profile)
    def profile(expected,commands,*,sink=False,stage=None):
        return author_profile(saved_author[1],expected,commands,sink=sink,stage=stage)
    def invoke(work,stage_name,clients,expected):
        if stage_name!='run_spec_author':return saved_author[0](work,stage_name,clients,expected)
        require(Path(work)==author_work(),'AUTHOR_INVOCATION_SCOPE')
        pins=json.loads(pr.check(pins_path()).read_bytes());af.check_runtime(work,pins)
        result=saved_author[0](work,stage_name,clients,expected);af.check_runtime(work,pins)
        result['author_submission']=af.verify_native(work,pins[af.CONFIG],pr.check(Path(work)/'console.log').read_text())
        return result
    class ResponseDriver(ExperimentDriver):
        def task(self,stage_name,value):
            require(stage_name=='run_spec_author','ONLY_RESPONSE_STAGES')
            task=super().task(stage_name,value)+'\n'+helper.guidance(p)
            if stage_name=='run_spec_author':
                from orchestrator.author_output_schema import schema
                task+='\nRequired exact author output schema: '+json.dumps(schema(),sort_keys=True)
            return task
        def prepare_input(self,value,stage_name,work):
            require((stage_name,self.model_round_number(value)) ==('run_spec_author',22),'INPUT_SCOPE')
            helper.deliver(self,value,p,approval,supplemental(self,p));deliver_failure(self,value,p)
            body,measurement=super().prepare_input(value,stage_name,work)
            helper.verify_delivered(self,value,stage_name,work,body,measurement,p);verify_failure_delivery(self,value,p)
            if stage_name=='run_spec_author':prepare_author_feedback(self,p,body,measurement,work)
            return body,measurement
        def _accept_completed(self,value):
            pending=value.get('pending') or {};stage=pending.get('stage')
            require((stage,pending.get('round'),pending.get('id')) ==('run_spec_author',22,helper.call(p,'author')),'COMPLETION_SCOPE')
            work=Path(pending['workspace'])
            helper.verify_delivered(self,value,stage,work,pr.check(work/'prompt.md').read_text(),
                json.loads(pr.check(work/'input-measurement.json').read_bytes()),p)
            verify_failure_delivery(self,value,p)
            # Ordinary author schema, synthetic tests and accepted-submission
            # validation remain unchanged. No execution approval is produced.
            super()._accept_completed(value)
            for key in helper.protected_keys(p):
                require(value.get(key)==json.loads(p['original_state']).get(key),'AUTHOR_CHANGED_EXECUTION_AUTHORITY')
            value.update(phase='BLOCKED',reason='REPORT_SNAPSHOT_AUTHOR_ACCEPTED_NATIVE_AND_REVIEW_REQUIRED')
            self.save(value);return self.status()
    try:
        driver=ResponseDriver(c.LANE)
        with lock(driver.state/'driver.lock'):
            driver.guard();c.originals(driver,*original);base.connect_evidence(driver,c,evidence)
            value=driver.current()
            if argv[0]=='verify':
                helper.originals(driver.store,p,approval);helper.review_binding(driver,p,approval)
                retained_smoke_evidence(driver,value,smoke,smoke_p,smoke_approval,helper)
                result={'status':'VERIFIED_HELD','model_calls':0,'provider_calls':0}
            elif argv[0]=='activate':
                result=helper.activate(driver,p,approval,driver.state/'report-snapshot-author')
            else:
                helper.ready(driver,value,p,approval)
                restore=bind_admission(driver,c,original,helper,p,approval)
                stage._invoke,stage.transport_profile=invoke,profile
                ec.accept_author=accept_author
                result=driver._model_step(value) # One stage only; never dispatch or auto-loop.
        print(json.dumps(result,sort_keys=True))
    finally:
        stage._invoke,stage.transport_profile=saved_author
        ec.accept_author=saved_accept
        if restore is not None:restore()
        if driver is not None:driver.store.db.close();driver.store.batch.db.close()

if __name__=='__main__':
    os.umask(0o077)
    sys.path.insert(0,'/opt/research-system/manual-sprint10/research-manual-sprint10-timeout-continuation-8e042339')
    if len(sys.argv)>5 and sys.argv[1]=='send' and sys.argv[4]=='--':raise SystemExit(send(sys.argv[2],sys.argv[3],sys.argv[5:]))
    main()
