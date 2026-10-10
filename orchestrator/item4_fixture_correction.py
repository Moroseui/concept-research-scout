"""One author-owned fixture correction; truthful failed evidence, never compute."""
from pathlib import Path
import ast,copy,hashlib,json
from orchestrator import private_records as pr
from orchestrator.review_contract import strict_json
from orchestrator.item4_review4_continuation import canonical

SCHEMA='item4-cpu-diagnostic-fixture-correction/v1'
DOCUMENT='docs/ITEM4_CPU_DIAGNOSTIC_FIXTURE_PRIVATE.json'
REFERENCE='docs/ITEM4_AUTHOR19_NATIVE_REFERENCE_PRIVATE.py'
DIRECTION='93eb8a687a27133bd4f355d403546357e19c6f7faab04fda124a72ec7ee4aa22'
ASSET='27146f38f1722579ed096a880f59cc607bc36e993fe57634b6ffe271ae92c157'
MODULE='8a6e446bfc96f2240c25716a2f56e2b367c56c9d220647805efd701f627c092b'
STATE=Path('/var/lib/research-system-manual-sprint10/environment-inventory/item4-author19-diagnostic-native-v1')
ROOT=Path(__file__).resolve().parents[1]
_verifier=None
_audit_verifier=None
AUDIT_SCHEMA='item4-whole-fixture-author/v1'
AUDIT_DOCUMENT='docs/ITEM4_WHOLE_FIXTURE_AUTHOR_PRIVATE.json'
AUDIT_REFERENCE='docs/ITEM4_AUTHOR20_NATIVE_REFERENCE_PRIVATE.py'
AUDIT_DIRECTION='e9636a72940a498855af4d8585e6f549ac87a380e7d0fa634408451a9fe925a3'
AUDIT_MODULE='501cb5b8e8487a2b73f1e139fe5cc96cb6c3315c1c8832ffefd351e31f5c8749'
AUDIT_ASSET='8c40fe36f279a1bab97dab6b2c59bf8f45d7e2901f508f36c1dac0f0a2c01653'
AUDIT_STATE=STATE.with_name('item4-author20-diagnostic-native-v1')

SNAPSHOT_SCHEMA='item4-report-snapshot-author/v1'
SNAPSHOT_DOCUMENT='docs/ITEM4_REPORT_SNAPSHOT_AUTHOR_PRIVATE.json'
SNAPSHOT_REFERENCE='docs/ITEM4_AUTHOR21_NATIVE_REFERENCE_PRIVATE.py'
SNAPSHOT_MODULE='fa54d6e41db935c4a7671abe278d4a40423bda41cfce32692b58ed1364638d20'
SNAPSHOT_STATE=STATE.with_name('item4-author21-progress-native-v1')
_snapshot_verifier=None
_progress_verifier=None

def snapshot(p):return p.get('schema')==SNAPSHOT_SCHEMA
def audit(p):return p.get('schema') in {AUDIT_SCHEMA,SNAPSHOT_SCHEMA}

def parameters(p):
    if snapshot(p):
        return dict(schema=SNAPSHOT_SCHEMA,direction='10129ee9f765ed5a88dfd7ff8524857e67a335d4960db451b0628dc238898ece',
            module=SNAPSHOT_MODULE,attempt=21,asset='1e5bb3d0f1f807a99039e106cba34a40e9400dd01aae16c1f3e7212165d91d49',
            state=SNAPSHOT_STATE,reference=SNAPSHOT_REFERENCE,source='9b568290e809ae897a54eab4a126c37a6ecadef7',
            review='10129ee9f765ed5a88dfd7ff8524857e67a335d4960db451b0628dc238898ece')
    if audit(p):
        return dict(schema=AUDIT_SCHEMA,direction=AUDIT_DIRECTION,module=AUDIT_MODULE,attempt=20,
            asset=AUDIT_ASSET,state=AUDIT_STATE,reference=AUDIT_REFERENCE,
            source='b60badd65283e7df5f801a6a6a20b3fd63504544',
            review='35aeaa0a9d6836f4caa5bf7033434b43952bb242777d4376a91259eee0ba5bb9')
    return dict(schema=SCHEMA,direction=DIRECTION,module=MODULE,attempt=19,asset=ASSET,state=STATE,
        reference=REFERENCE,source='81cd8225365a26944128ab5eb3fceda9e36d5f3d',
        review='b5dfa4bf3c7d3bb45733dd7bffcf8aa5a4344cfc99a16dbdb7468e292f28679a')

def sha(raw):return hashlib.sha256(raw).hexdigest()
def require(ok,why):
    if not ok:raise ValueError('ITEM4_FIXTURE_'+why)

def scope(p):
    q=parameters(p)
    require(p.get('schema')==q['schema'] and p.get('direction_sha256')==q['direction'],'DIRECTION')
    if audit(p):require(p.get('author_only') is True,'AUTHOR_ONLY')
    old=p['fixture_reference'];f=p['native_failure'];row=f['asset_row']
    require(old['module_sha256']==p['reference_native_harness_sha256']==q['module'] and
        old['accepted_author']['attempt']==q['attempt'] and old['accepted_author']['status']=='COMPLETE'
        and old['accepted_event']['call_id']==old['accepted_author']['id'],'ACCEPTED19_SCOPE')
    require(row['id']==q['asset'] and row['status']=='UNCERTAIN' and row['reserved_micro_usd']==1118950
        and f['terminal_poll']==1 and f['source']==q['source']
        and f['implementation_review_sha256']==q['review'],
        'EXACT_FAILED_ATTEMPT')
    require(set(f['files'])=={'STATUS.json','binding.json','start-intent.json','provider/sandbox.json',
        'provider/outcome.json','provider/terminal.json','provider/stdin-intent.json',
        'provider/stdin-sent.json','provider/stdout.bin','provider/stderr.bin'},'FAILURE_MEMBERS')
    return f

def failure(store,p):
    f=scope(p);q=parameters(p)
    if snapshot(p):
        failure(store,strict_json(pr.check(ROOT/AUDIT_DOCUMENT).read_bytes()))
        original=strict_json(pr.check(ROOT/'docs/ITEM4_PROGRESS_NATIVE_FAILURE_PRIVATE.json').read_bytes())
        require(_progress_verifier is not None,'UNCONNECTED_PROGRESS_QUALIFIER')
        # The third failure has no author correction: preserve its exact row and qualification too.
        row=store.batch.db.execute('SELECT * FROM autonomy_assets WHERE id=?',(original['third_failed_asset']['id'],)).fetchone()
        require(row is not None and dict(row)==original['third_failed_asset'],'THIRD_FAILURE_ROW_CHANGED')
        require(_progress_verifier()==original['qualification'],'THIRD_FAILURE_QUALIFICATION')
    elif audit(p):failure(store,strict_json(pr.check(ROOT/DOCUMENT).read_bytes()))
    row=store.batch.db.execute('SELECT * FROM autonomy_assets WHERE id=?',(q['asset'],)).fetchone()
    require(row is not None and dict(row)==f['asset_row'],'FAILURE_ROW_CHANGED')
    for name,pin in f['files'].items():require(sha(pr.check(q['state']/name).read_bytes())==pin,'FAILURE_FILE_CHANGED')
    verifier=_snapshot_verifier if snapshot(p) else _audit_verifier if audit(p) else _verifier
    require(verifier is not None,'UNCONNECTED_NATIVE_QUALIFIER')
    require(verifier()=={'source':f['source'],'implementation_review_sha256':f['implementation_review_sha256'],
        'asset_id':q['asset'],'module_sha256':q['module'],'exit_code':1,'status':'FAIL',
        'package_unchanged':True,'scientific_acceptance':False,'no_automatic_retry':True},'NATIVE_FAILURE_QUALIFICATION')
    return f

def reference(driver,p):
    from orchestrator import author_revision_accounting as accounting
    q=parameters(p);old=p['fixture_reference'];ident=old['accepted_author']['id']
    row=driver.store.db.execute('SELECT * FROM manual_calls WHERE id=?',(ident,)).fetchone()
    require(row is not None and dict(row)==old['accepted_author'] and accounting._accepted(driver.store,dict(row)),
        'AUTHOR19_CHANGED')
    event=driver.store.db.execute('SELECT payload FROM events WHERE id=?',('author-accepted:'+ident,)).fetchone()
    require(event is not None and json.loads(event[0])==old['accepted_event'],'AUTHOR19_ACCEPTANCE')
    saved=json.loads(row['receipt']);work=Path(saved['workspace'])
    require(work.name=='run_spec_author-'+str(q['attempt']) and saved['output_sha256']==old['accepted_event']['output_sha256'],
        'AUTHOR19_OUTPUT_BINDING')
    for name,pin in saved['output_sha256'].items():require(sha(pr.check(work/name).read_bytes())==pin,'AUTHOR19_OUTPUT_CHANGED')
    raw=pr.check(ROOT/q['reference']).read_bytes();require(sha(raw)==q['module'],'REFERENCE_MODULE_CHANGED')
    return dict(row)

def correction(raw,p):
    """Structural scope only; the author and scientific reviewer judge the fix."""
    scope(p)
    if audit(p):return audit_correction(raw,p)
    before=pr.check(ROOT/REFERENCE).read_bytes();require(sha(before)==MODULE,'REFERENCE_MODULE_CHANGED')
    old,new=ast.parse(before),ast.parse(raw)
    def parts(tree):
        fixture=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='_native_diagnostic_fixture']
        require(len(fixture)==1 and not fixture[0].decorator_list,'FIXTURE_FUNCTION')
        return fixture[0],ast.dump(ast.Module(body=[n for n in tree.body if n is not fixture[0]],type_ignores=tree.type_ignores))
    left,other_old=parts(old);right,other_new=parts(new)
    def interface(node):
        shell=copy.deepcopy(node);shell.body=[];return ast.dump(shell)
    require(other_old==other_new and interface(left)==interface(right),'PRODUCTION_OR_INTERFACE_CHANGED')
    require(ast.dump(left)!=ast.dump(right) and sha(raw)!=MODULE,'FIXTURE_CORRECTION_REQUIRED')
    return {'module_sha256':sha(raw),'reference_module_sha256':MODULE,'production_ast_unchanged':True,
        'corrected_fixture_executed':False,'scientific_acceptance':False}

GUIDANCE=(
 'Respond only to the actual author19 native failure delivered in diagnostic-fixture-failure-index.json and ALL '
 'ordered pages. The complete untruncated failure and transport proof remain authoritative evidence: FAIL, '
 'exit1, KeyError continue_training at the diagnostic fixture constructor. Base and production constructors '
 'already supply this field. Author20 owns a minimal correction to _native_diagnostic_fixture; keep all '
 'production module code and its interface, exact diagnostic execution.plan.json, scientific choices, inputs, '
 'pinned image and safeguards unchanged. Explain the exact change and preserve all prior findings. '
 'Use the exact required output schema and same-call submission feedback; ordinary controller tests remain. '
 'Do not claim this correction was executed in the pinned image. No second CPU rehearsal and NO automatic '
 'GPU retry. Reviewer15 must independently judge this correction and the authentic failure, and whether the '
 'FIRST RunB itself can provide remaining native integration evidence. Review14 is not administratively '
 'closed. No expected verdict: REVISE and REJECT remain genuine outcomes. All whole-plan, coverage and '
 '$1200 projection findings remain open; no verdict here dispatches compute. Diagnostic25/stage150/total1275 '
 'and all original charges remain unchanged; the failed native reservation stays fully counted pending billing.')


def audit_correction(raw,p):
    """Only fixture-body repair and additive tests; all old checks stay exact."""
    scope(p)
    q=parameters(p)
    before=pr.check(ROOT/q['reference']).read_bytes()
    require(sha(before)==q['module'],'AUDIT_REFERENCE_CHANGED')
    old,new=ast.parse(before),ast.parse(raw)
    names={'_native_diagnostic_fixture','synthetic_tests'}
    def split(tree):
        chosen={}
        for name in names:
            found=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name==name]
            require(len(found)==1 and not found[0].decorator_list,'AUDIT_FUNCTION')
            chosen[name]=found[0]
        rest=[n for n in tree.body if all(n is not f for f in chosen.values())]
        return chosen,ast.dump(ast.Module(body=rest,type_ignores=tree.type_ignores))
    left,old_production=split(old);right,new_production=split(new)
    require(old_production==new_production,'PRODUCTION_OR_INTERFACE_CHANGED')
    def shell(node):
        value=copy.deepcopy(node);value.body=[];return ast.dump(value)
    for name in names:require(shell(left[name])==shell(right[name]),'PRODUCTION_OR_INTERFACE_CHANGED')
    require(ast.dump(left['_native_diagnostic_fixture'])!=ast.dump(right['_native_diagnostic_fixture']),
        'FIXTURE_CORRECTION_REQUIRED')
    def tests(node):
        groups=[n for n in node.body if isinstance(n,ast.ClassDef) and n.name=='Checks']
        require(len(groups)==1,'ORIGINAL_TEST_CLASS_REQUIRED')
        group=groups[0]
        return group,ast.dump(ast.Module(body=[n for n in node.body if n is not group],type_ignores=[]))
    old_checks,old_suite=tests(left['synthetic_tests']);new_checks,new_suite=tests(right['synthetic_tests'])
    require(old_suite==new_suite and shell(old_checks)==shell(new_checks),'ORIGINAL_SUITE_CHANGED')
    require(len(new_checks.body)>len(old_checks.body) and
        [ast.dump(n) for n in new_checks.body[:len(old_checks.body)]]==[ast.dump(n) for n in old_checks.body],
        'ORIGINAL_TESTS_CHANGED')
    added=new_checks.body[len(old_checks.body):]
    require(all(isinstance(n,ast.FunctionDef) and n.name.startswith('test_') and not n.decorator_list for n in added),
        'ADDITIVE_TESTS_ONLY')
    method_names=[n.name for n in new_checks.body if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef))]
    require(len(method_names)==len(set(method_names)),'TEST_OVERRIDE_REFUSED')
    return {'module_sha256':sha(raw),'reference_module_sha256':q['module'],'production_ast_unchanged':True,
        'existing_tests_unchanged':True,'added_contract_tests':[n.name for n in added],
        'corrected_fixture_executed':False,'scientific_acceptance':False}

AUDIT_GUIDANCE=(
 'Audit and repair the WHOLE _native_diagnostic_fixture against the exact accepted20 parent DiagnosticMonitor, '
 'trainer and run_fit interfaces, not only the latest exception. Read both complete native failure page sets. '
 'First failure was missing continue_training; second was undefined CPUObserver._sampling_loop. '
 'The scientific author owns all corrections. Preserve all production module AST/interfaces, exact diagnostic '
 'plan, image, scientific choices, caps and guards. Changes may occur only in the existing fixture body and '
 'by APPENDING new test_* methods to synthetic_tests.Checks. Keep every existing test/helper method and the '
 'suite construction unchanged; new imports/helpers can live inside new test methods. Add a fast contract '
 'test of the actual fixture monitor/callback interfaces and demonstrate it rejects the retained faulty '
 'callback before any paid native run. Do not just test a duplicate implementation or replace old checks. '
 'Explain the whole-fixture audit and positive/negative test evidence. Use exact required output schema '
 'and same-call submission feedback. No claim of native execution or GPU/scientific success. '
 'This is ONE author-only call. It ends held; reviewer16, any later deliberate native CPU operation and '
 'GPU dispatch are NOT authorized here. No automatic retry. Full original failures/charges and review15 '
 'findings remain open, including coverage, all-arm evidence, opposing review and projection1200/total1275. '
 'Diagnostic25 and stage150 caps are unchanged.')

SNAPSHOT_GUIDANCE=(
 'Author22: repair the complete final-report lifecycle of the existing synthetic diagnostic fixture. '
 'Read the complete four native failure page sets, accepted21 source, actual progress factory and FitProgress '
 'interfaces, and exact AST counterexample. Fourth run completed all15 synthetic CPU diagnostic epochs '
 'then failed E173: receipt recording appends to the same event list referenced by the serialized report. '
 'The saved file hash remained unchanged in the local counterexample; it is not a native PASS. '
 'Choose the scientific correction yourself. Preserve the report consistency check with equivalent or '
 'stronger semantics; do not delete assertions to make the fixture pass. Audit serialization, receipt '
 'publication and final returned evidence together. Add a fast regression of the actual report lifecycle '
 'that fails for accepted21 and passes your correction without paid compute. '
 'Only _native_diagnostic_fixture body and APPENDED test_* methods in synthetic_tests.Checks may change. '
 'Production AST, interfaces, every existing test, exact plan, image, scientific choices, inputs and '
 'safeguards stay unchanged. New test helpers/imports stay inside appended methods. '
 'Use the exact output schema and same-call submit_author feedback. Do not claim GPU evidence, CPU-starvation '
 'results, or native success. This is ONE author-only call; stop held after accepted output. No native '
 'retry, reviewer16, GPU or full training is dispatched here. Genuine scientific REVISE15 and all findings '
 'remain open; every earlier attempt and charge is preserved. Diagnostic25/stage150/projection1200/total1275 '
 'unchanged. Explain exact correction, full lifecycle audit and positive/negative regression evidence.')
