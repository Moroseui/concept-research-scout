"""Reviewed exact author23 delivery recovery; no model or provider entrypoint."""
from pathlib import Path
import copy,hashlib,importlib.util,json,os,subprocess,sys
CHANGE='item4-spec-regression-recovery-20261010'
ROOT=Path('/opt/research-system/manual-repair-helpers')/CHANGE
RECORD=Path('/var/lib/research-system-manual-sprint10-deployment')/CHANGE
PRIOR=ROOT.parent/'item4-driver-round-repair-20261010/tools/item4_smoke_response_runtime.py'
SCIENCE=Path('/opt/research-system/manual-sprint10/research-manual-sprint10-timeout-continuation-8e042339')
RUNTIME=Path('/etc/research-system-manual-sprint10/releases')/SCIENCE.name/'runtime.json'
DOC='docs/ITEM4_SPEC_REGRESSION_RECOVERY_PRIVATE.json'
BINDING='6520749c22006f8a2521d1bbdec0f5868ef0f3ff7685ead24e61e4310fd5e912'
FILES=('tools/item4_spec_regression_recovery.py','tools/install_item4_spec_regression_recovery.py',
       'orchestrator/item4_spec_regression.py',DOC,'docs/OVERNIGHT_AUTONOMY_OPERATOR_DECISION_20261008.txt')
OLD_UNIT='research-item4-driver-round-repair-20261010.service'
INVOCATION='f7599cc25c814e8dac228a878308b2a6'


def sha(raw):return hashlib.sha256(raw).hexdigest()
def canonical(v):return json.dumps(v,sort_keys=True,separators=(',',':')).encode()
def require(ok,why):
    if not ok:raise ValueError('SPEC_RECOVERY_'+why)
def trusted(path):
    path=Path(path)
    for p in [path,*path.parents]:
        st=p.lstat();require(not p.is_symlink() and st.st_uid==0 and not st.st_mode&0o022,'TRUSTED_FILE')
    return path

def load_module(name,path):
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec)
    sys.modules[name]=m;spec.loader.exec_module(m);return m

def stopped():
    v=dict(x.split('=',1) for x in subprocess.check_output(['systemctl','show',OLD_UNIT,
        '-p','ActiveState','-p','MainPID','-p','ControlGroup','-p','ExecMainStatus','-p','InvocationID'],text=True).splitlines())
    require(v=={'ActiveState':'failed','MainPID':'0','ControlGroup':'','ExecMainStatus':'1','InvocationID':INVOCATION},
            'ORIGINAL_INVOCATION_NOT_TERMINAL')

def verified():
    from orchestrator.autonomy_review import verify_result
    v=json.loads(trusted(RECORD/'installed.json').read_bytes())
    require(v['schema']=='reviewed-spec-regression-recovery/v1' and v['root']==str(ROOT),'INSTALL_SCOPE')
    a=verify_result(Path(v['review_folder']))
    require(a['verdict']=='APPROVE' and a['change_id']==CHANGE and a['source_sha']==v['source']
            and a['report_sha256']==v['review_sha256'] and a['runtime_sha256']==sha(trusted(RUNTIME).read_bytes()),
            'GENUINE_APPROVE')
    manifest=json.loads(trusted(Path(v['review_folder'])/'packet-manifest.json').read_bytes())
    require(set(v['files'])==set(FILES),'FILE_SET')
    for name,pin in v['files'].items():require(sha(trusted(ROOT/name).read_bytes())==pin==manifest['source_files'][name],'REVIEWED_BYTES')
    raw=trusted(ROOT/DOC).read_bytes();require(sha(raw)==BINDING,'FROZEN_BINDING')
    b=json.loads(raw)
    require(sha(trusted(ROOT/FILES[-1]).read_bytes())==b['operator_decision_sha256'],'OPERATOR_AUTHORITY')
    require(sha(trusted(PRIOR).read_bytes())==b['prior_runtime_sha256'],'PRIOR_RUNTIME')
    return v,b


def originals(driver,b,prior,helper,p,approval,*,require_block=True):
    from orchestrator import private_records as pr,author_format_submission as af
    local=driver.store.db.execute('SELECT * FROM manual_calls WHERE id=?',(b['call_id'],)).fetchone()
    global_row=driver.store.batch.db.execute('SELECT * FROM autonomy_calls WHERE id=?',(b['call_id'],)).fetchone()
    require(local is not None and dict(local)==b['local_row'] and local['status']=='COMPLETE'
            and global_row is not None and dict(global_row)==b['global_row'],'ORIGINAL_CALLS')
    value=driver.current()
    if require_block:
        require(sha(canonical(value))==b['state_sha256'] and value['phase']=='BLOCKED'
                and value['reason']=='OUTPUT_VALIDATION_REFUSED: ITEM4_FIXTURE_ORIGINAL_TESTS_CHANGED', 'EXACT_REFUSAL')
        require(not driver.store.db.execute('SELECT 1 FROM events WHERE id=?',('author-accepted:'+b['call_id'],)).fetchone(),
                'ALREADY_ACCEPTED_RECONCILE')
    require(not driver.store.batch.db.execute("SELECT 1 FROM autonomy_calls WHERE status='RUNNING'").fetchone(),'RUNNING_CALL')
    work=Path(b['original_state']['pending']['workspace']);require(work==prior.author_work(),'EXACT_WORKSPACE')
    for name,pin in b['workspace_files'].items():require(sha(pr.check(work/name).read_bytes())==pin,'PRESERVED_OUTPUT_CHANGED')
    pins=json.loads(pr.check(prior.pins_path()).read_bytes());af.check_runtime(work,pins)
    submission=af.verify_native(work,pins[af.CONFIG],pr.check(work/'console.log').read_text())
    require(submission['status']=='ACCEPTED' and submission['record_sha256']==b['submission_sha256'],'GENUINE_SUBMISSION')
    helper.granted(driver.store,p,approval);helper.review_binding(driver,p,approval)
    # The refused state already contains author23 artifacts. Verify the
    # historical input from the frozen pre-author state plus its bounded
    # delivered supplements, never claim author23 was its own input.
    delivered=copy.deepcopy(helper.scope(p,'0'*64))
    prefixes=(helper.profile(p)['folder']+'-',prior.FAILURE_PREFIX)
    for ref in value['artifacts']:
        if ref['id'].startswith(prefixes) and ref not in delivered['artifacts']:
            delivered['artifacts'].append(ref)
    helper.verify_delivered(driver,delivered,'run_spec_author',work,pr.check(work/'prompt.md').read_text(),
        json.loads(pr.check(work/'input-measurement.json').read_bytes()),p)
    prior.verify_failure_delivery(driver,value,p)
    folder=Path(b['original_state']['notebook_revision_result']['folder'])/'synthetic'
    require(sha(pr.check(folder/'receipt.json').read_bytes())==b['original_synthetic_receipt_sha256'],'ORIGINAL_TEST_RECEIPT')
    for name,pin in json.loads(pr.check(folder/'receipt.json').read_bytes())['preserved_files'].items():
        rel=Path(name);require(not rel.is_absolute() and '..' not in rel.parts,'ORIGINAL_EVIDENCE_PATH')
        require(sha(pr.check(folder/rel).read_bytes())==pin,'ORIGINAL_TEST_EVIDENCE')
    for key in helper.protected_keys(p):
        require(value.get(key)==b['original_state'].get(key),'EXECUTION_AUTHORITY_CHANGED')
    return work,folder


def main(action):
    require(os.getuid()==os.getgid()==1003 and Path(__file__).resolve()==ROOT/FILES[0],'OWNER_PATH')
    require(action in {'verify','recover'},'NO_OTHER_ACTION')
    v,b=verified();stopped()
    if action=='recover':
        complete=json.loads(trusted(RECORD/'COMPLETE.json').read_bytes())
        require(complete=={'status':'INSTALLED_HELD','source':v['source'],'review_sha256':v['review_sha256'],
                         'model_calls':0,'provider_calls':0},'INSTALL_INCOMPLETE')
    prior=load_module('_spec_recovery_prior',PRIOR)
    require(prior.authority()['source_sha']==b['prior_source'] and prior.authority()['report_sha256']==b['prior_review'],
            'PRIOR_APPROVAL')
    connected,smoke,smoke_p,smoke_approval,helper,p,approval=prior.connect()
    c,policy,original,evidence,base,fresh=connected
    from orchestrator.experiment_driver import ExperimentDriver
    from orchestrator.manual_driver import Driver,write_once
    from orchestrator.manual_executor import lock
    from orchestrator import experiment_context as ec,item4_fixture_correction as fixture,private_records as pr
    supplement=load_module('_submitted_regression',ROOT/'orchestrator/item4_spec_regression.py')
    driver=ExperimentDriver(c.LANE);dest=driver.state/CHANGE
    saved_accept=ec.accept_author;saved_audit=fixture.audit_correction
    try:
        with lock(driver.state/'driver.lock'):
            driver.guard();c.originals(driver,*original);base.connect_evidence(driver,c,evidence)
            work,folder=originals(driver,b,prior,helper,p,approval)
            files,derived=supplement.authenticate(pr.check(work/'SPEC.proposed.md').read_bytes(),
                pr.check(work/'.author-submission.json').read_bytes(),pr.check(folder/'package/execution.py').read_bytes(),
                prior.trusted(prior.ROOT/fixture.SNAPSHOT_REFERENCE).read_bytes())
            # A complete replay of the original strict additive-test guard over
            # the author's derived test copy precedes execution or state change.
            checked=saved_audit(derived,p);require(checked['added_contract_tests']==['test_report_lifecycle'],'ADDITIVE_GUARD')
            if action=='verify':return {'status':'VERIFIED_HELD','model_calls':0,'provider_calls':0}
            require(not dest.exists() and not dest.is_symlink(),'EXISTS_RECONCILE_NO_RETRY')
            pr.mkdir(dest);write_once(dest/'original-refusal.json',canonical(b['original_state']))
            write_once(dest/'intent.json',canonical({'source':v['source'],'review_sha256':v['review_sha256'],
                'call_id':b['call_id'],'original_state_sha256':b['state_sha256']}))
            backup=pr.Connection(dest/'before.sqlite');driver.store.db.backup(backup);backup.close()
            receipt=supplement.execute(dest/'synthetic',files,b['environment'])
            originals(driver,b,prior,helper,p,approval);stopped()
            local_before=[tuple(r) for r in driver.store.db.execute('SELECT * FROM manual_calls ORDER BY rowid')]
            global_before=[tuple(r) for r in driver.store.batch.db.execute('SELECT * FROM autonomy_calls ORDER BY id')]
            value=copy.deepcopy(driver.current())
            def audit(raw,scope):
                if scope!=p or sha(raw)!=supplement.MODULE:return saved_audit(raw,scope)
                # Revalidate saved evidence on every use; not a free-standing bypass token.
                verified_receipt=supplement.verify_receipt(dest/'synthetic',receipt['binding'])
                return supplement.equivalent(saved_audit,raw,scope,derived,verified_receipt)
            def accept(current,state,pending):
                require(current is driver and pending==b['original_state']['pending'],'ACCEPT_SCOPE')
                saved_accept(current,state,pending) # Reuses byte-identical original completed16-test receipt.
                helper.executable_candidate(current,state,p)
                for key in helper.protected_keys(p):require(state.get(key)==b['original_state'].get(key),'PROTECTED_STATE')
            fixture.audit_correction=audit;ec.accept_author=accept
            driver.store.db.execute('BEGIN IMMEDIATE')
            try:
                require(sha(canonical(driver.current()))==b['state_sha256'],'STATE_RACE')
                Driver._accept_completed(driver,value) # Original output validation and accepted-event writer.
                value.update(phase='BLOCKED',reason='REPORT_SNAPSHOT_AUTHOR_ACCEPTED_NATIVE_AND_REVIEW_REQUIRED')
                value['spec_regression_recovery']={'source':v['source'],'review_sha256':v['review_sha256'],
                    'original_refusal_sha256':b['state_sha256'],'supplemental_receipt_sha256':sha(canonical(receipt)),
                    'folder':str(dest),'scientific_acceptance':False}
                driver.save(value)
                originals(driver,b,prior,helper,p,approval,require_block=False)
                require([tuple(r) for r in driver.store.db.execute('SELECT * FROM manual_calls ORDER BY rowid')]==local_before,
                        'LOCAL_CHARGES_CHANGED')
                require([tuple(r) for r in driver.store.batch.db.execute('SELECT * FROM autonomy_calls ORDER BY id')]==global_before,
                        'GLOBAL_CHARGES_CHANGED')
                driver.store.db.execute('COMMIT')
            except BaseException:driver.store.db.execute('ROLLBACK');raise
            write_once(dest/'applied.json',canonical({'status':value['reason'],'state_sha256':sha(canonical(value)),
                'source':v['source'],'review_sha256':v['review_sha256'],'model_calls':0,'provider_calls':0,
                'scientific_acceptance':False,'supplemental_receipt_sha256':sha(canonical(receipt))}))
            return {'status':value['reason'],'model_calls':0,'provider_calls':0,'originals_preserved':True}
    finally:
        ec.accept_author=saved_accept;fixture.audit_correction=saved_audit
        driver.store.db.close();driver.store.batch.db.close()

if __name__=='__main__':
    os.umask(0o077);sys.path.insert(0,str(SCIENCE))
    require(len(sys.argv)==2,'ACTION_REQUIRED');print(json.dumps(main(sys.argv[1]),sort_keys=True))
