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

def sha(raw):return hashlib.sha256(raw).hexdigest()
def require(ok,why):
    if not ok:raise ValueError('ITEM4_FIXTURE_'+why)

def scope(p):
    require(p.get('schema')==SCHEMA and p.get('direction_sha256')==DIRECTION,'DIRECTION')
    old=p['fixture_reference'];f=p['native_failure'];row=f['asset_row']
    require(old['module_sha256']==p['reference_native_harness_sha256']==MODULE and
        old['accepted_author']['attempt']==19 and old['accepted_author']['status']=='COMPLETE'
        and old['accepted_event']['call_id']==old['accepted_author']['id'],'ACCEPTED19_SCOPE')
    require(row['id']==ASSET and row['status']=='UNCERTAIN' and row['reserved_micro_usd']==1118950
        and f['terminal_poll']==1 and f['source']=='81cd8225365a26944128ab5eb3fceda9e36d5f3d'
        and f['implementation_review_sha256']=='b5dfa4bf3c7d3bb45733dd7bffcf8aa5a4344cfc99a16dbdb7468e292f28679a',
        'EXACT_FAILED_ATTEMPT')
    require(set(f['files'])=={'STATUS.json','binding.json','start-intent.json','provider/sandbox.json',
        'provider/outcome.json','provider/terminal.json','provider/stdin-intent.json',
        'provider/stdin-sent.json','provider/stdout.bin','provider/stderr.bin'},'FAILURE_MEMBERS')
    return f

def failure(store,p):
    f=scope(p)
    row=store.batch.db.execute('SELECT * FROM autonomy_assets WHERE id=?',(ASSET,)).fetchone()
    require(row is not None and dict(row)==f['asset_row'],'FAILURE_ROW_CHANGED')
    for name,pin in f['files'].items():require(sha(pr.check(STATE/name).read_bytes())==pin,'FAILURE_FILE_CHANGED')
    require(_verifier is not None,'UNCONNECTED_NATIVE_QUALIFIER')
    require(_verifier()=={'source':f['source'],'implementation_review_sha256':f['implementation_review_sha256'],
        'asset_id':ASSET,'module_sha256':MODULE,'exit_code':1,'status':'FAIL',
        'package_unchanged':True,'scientific_acceptance':False,'no_automatic_retry':True},'NATIVE_FAILURE_QUALIFICATION')
    return f

def reference(driver,p):
    from orchestrator import author_revision_accounting as accounting
    old=p['fixture_reference'];ident=old['accepted_author']['id']
    row=driver.store.db.execute('SELECT * FROM manual_calls WHERE id=?',(ident,)).fetchone()
    require(row is not None and dict(row)==old['accepted_author'] and accounting._accepted(driver.store,dict(row)),
        'AUTHOR19_CHANGED')
    event=driver.store.db.execute('SELECT payload FROM events WHERE id=?',('author-accepted:'+ident,)).fetchone()
    require(event is not None and json.loads(event[0])==old['accepted_event'],'AUTHOR19_ACCEPTANCE')
    saved=json.loads(row['receipt']);work=Path(saved['workspace'])
    require(work.name=='run_spec_author-19' and saved['output_sha256']==old['accepted_event']['output_sha256'],
        'AUTHOR19_OUTPUT_BINDING')
    for name,pin in saved['output_sha256'].items():require(sha(pr.check(work/name).read_bytes())==pin,'AUTHOR19_OUTPUT_CHANGED')
    raw=pr.check(ROOT/REFERENCE).read_bytes();require(sha(raw)==MODULE,'REFERENCE_MODULE_CHANGED')
    return dict(row)

def correction(raw,p):
    """Structural scope only; the author and scientific reviewer judge the fix."""
    scope(p);before=pr.check(ROOT/REFERENCE).read_bytes();require(sha(before)==MODULE,'REFERENCE_MODULE_CHANGED')
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
