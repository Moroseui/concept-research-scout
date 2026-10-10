"""Preserved response pair and bounded executable CPU-diagnostic authoring.

This capability admits scientific proposal work only. It never grants compute,
closes prior findings, replaces the execution approval or changes dollar caps.
The installed caller must authenticate the independent implementation APPROVE
and exact source/checkpoint bytes before connecting it.
"""
import json
from pathlib import Path
from orchestrator import item4_review4_continuation as prior
from orchestrator import item4_smoke_review as smoke

RUN=prior.RUN
EVENT='REVIEWED_ITEM4_POST_SMOKE_RESPONSE'
AUTHOR=prior.sha((RUN+':run_spec_author:15').encode())
REVIEW=prior.sha((RUN+':run_spec_review:12').encode())
DOCUMENT='docs/ITEM4_POST_SMOKE_RESPONSE_PRIVATE.json'
sha,canonical=prior.sha,prior.canonical


def require(ok,why):
    if not ok:raise ValueError('ITEM4_SMOKE_RESPONSE_'+why)


DIAGNOSTIC_DECISION = '5748a56f92c8aa0048fdd94194038749737eb648e62da097a128ffa85c68ca33'
DIAGNOSTIC_SCHEMA = 'item4-cpu-diagnostic-authoring/v1'
RECOVERY_SCHEMA = 'item4-cpu-diagnostic-entrypoint-recovery/v1'
SCOPED_SCHEMA = 'item4-cpu-diagnostic-scoped-review/v1'
CORRECTED_REVIEW_SCHEMA='item4-corrected-native-scientific-review/v1'
CORRECTED_REVIEW_DOCUMENT='docs/ITEM4_CORRECTED_NATIVE_REVIEW_PRIVATE.json'
REVIEW15_REPORT='c2469bdd71627d675d1965f9eb8ded3faf65d5b3d10baa5bd3c72305b6179ba4'
AUDITED_REVIEW_SCHEMA='item4-audited-native-scientific-review/v1'
def audited_review(p):return p.get('schema')==AUDITED_REVIEW_SCHEMA
def corrected_review(p):return p.get('schema') in {CORRECTED_REVIEW_SCHEMA,AUDITED_REVIEW_SCHEMA}
PLAINTEXT_SCHEMA = 'item4-cpu-diagnostic-plaintext-recovery/v1'
from orchestrator import item4_fixture_correction as fixture
FIXTURE_SCHEMA = fixture.SCHEMA
AUDIT_SCHEMA=fixture.AUDIT_SCHEMA
AUDIT_DOCUMENT=fixture.AUDIT_DOCUMENT
SNAPSHOT_SCHEMA=fixture.SNAPSHOT_SCHEMA
SNAPSHOT_DOCUMENT=fixture.SNAPSHOT_DOCUMENT
SENDER_FAILED_CALL='af4547778fe7e1f35698089607ab524d08346618131512c232670b7ccbf02ab8'
_sender_verifier=None
DELIVERY_FAILED_CALL='fed0c73d8288bbf8fda82f96d6559ddb4f6c85ac39f927e53939bf909bd7545e'
def delivery_recovery(p):return sender_recovery(p) and 'delivery_recovery' in p
def report_snapshot(p):return fixture.snapshot(p)
def sender_recovery(p):return report_snapshot(p) and 'sender_recovery' in p
def fixture_audit(p):return fixture.audit(p)
FIXTURE_DOCUMENT = fixture.DOCUMENT

def fixture_correction(p):return p.get('schema') in {FIXTURE_SCHEMA,AUDIT_SCHEMA,SNAPSHOT_SCHEMA}
PLAINTEXT_DOCUMENT = 'docs/ITEM4_CPU_DIAGNOSTIC_PLAINTEXT_PRIVATE.json'
OPAQUE_AUTHOR = sha((RUN+':run_spec_author:18').encode())
OPAQUE_REASON = 'OUTPUT_VALIDATION_REFUSED: PRIVATE_INTAKE_OPAQUE_PAYLOAD_REJECTED'
NATIVE_SCHEMA = 'item4-cpu-diagnostic-native-harness/v1'
NATIVE_DOCUMENT = 'docs/ITEM4_CPU_DIAGNOSTIC_NATIVE_HARNESS_PRIVATE.json'
NATIVE_REVIEW14_REPORT = '0cf4671ce6c1641b0aa2724d5fd0405e0cf9c21f9193a5eb0a7e7a822158a11a'
SCOPED_DOCUMENT = 'docs/ITEM4_CPU_DIAGNOSTIC_SCOPED_REVIEW_PRIVATE.json'
SCOPED_REVIEW13_REPORT = '00ac3c5bdf863f1f5aba76b2a151c572a36edd6f5de9208d3237c1306dcb62e7'
RECOVERY_DOCUMENT = 'docs/ITEM4_CPU_DIAGNOSTIC_RECOVERY_PRIVATE.json'
RECOVERY_DIRECTION = 'ddcdc756df490d35c42784b8ede667be783ca72a2161bb938c4888745a43b9ca'
FAILED_AUTHOR = sha((RUN+':run_spec_author:16').encode())
FAILED_REASON = 'OUTPUT_VALIDATION_REFUSED: NOTEBOOK_EXECUTION_ENTRYPOINT:synthetic_tests'

def diagnostic(p):
    return p.get('schema') in {DIAGNOSTIC_SCHEMA, RECOVERY_SCHEMA, SCOPED_SCHEMA, NATIVE_SCHEMA, PLAINTEXT_SCHEMA, FIXTURE_SCHEMA, CORRECTED_REVIEW_SCHEMA, AUDITED_REVIEW_SCHEMA, AUDIT_SCHEMA,SNAPSHOT_SCHEMA}

def plaintext_recovery(p):
    return p.get('schema') == PLAINTEXT_SCHEMA

def native_harness(p):
    return p.get('schema') in {NATIVE_SCHEMA, PLAINTEXT_SCHEMA, FIXTURE_SCHEMA,AUDIT_SCHEMA,SNAPSHOT_SCHEMA}

def scoped_review(p):
    return p.get('schema') in {SCOPED_SCHEMA,CORRECTED_REVIEW_SCHEMA,AUDITED_REVIEW_SCHEMA}



def profile(p):
    """Two explicit historical/diagnostic scopes, not an arbitrary limit table."""
    if p.get('schema') == 'item4-post-smoke-response/v1':
        return dict(author=15, reviewer=12, count=25, batch=63, limit=29, batch_limit=67,
            event=EVENT, field='post_smoke_response_scope', assessment='smoke_review',
            previous_reason='SMOKE_REVIEW_REVISE', previous_review=11,
            previous_call=smoke.CALL, folder='post-smoke-response', result='post_smoke_response')
    if delivery_recovery(p):
        return dict(author=24,reviewer=16,count=38,batch=76,limit=41,batch_limit=79,
            event='REVIEWED_ITEM4_AUTHOR24_DELIVERY',field='author24_delivery_scope',
            assessment='cpu_diagnostic_fixture_correction',previous_reason='OUTPUT_VALIDATION_REFUSED: ITEM4_FIXTURE_ORIGINAL_TESTS_CHANGED',
            previous_review=15,previous_call=sha((RUN+':run_spec_review:15').encode()),
            folder='author24-delivery',result='report_snapshot_author')
    if sender_recovery(p):
        return dict(author=23,reviewer=16,count=37,batch=75,limit=41,batch_limit=79,
            event='REVIEWED_ITEM4_SENDER_CONTINUATION',field='sender_continuation_scope',
            assessment='cpu_diagnostic_fixture_correction',previous_reason='MODEL_FAILED_OR_UNCERTAIN_NO_RETRY',
            previous_review=15,previous_call=sha((RUN+':run_spec_review:15').encode()),
            folder='report-snapshot-author',result='report_snapshot_author')
    if report_snapshot(p):
        return dict(author=22,reviewer=16,count=36,batch=74,limit=40,batch_limit=78,
            event='REVIEWED_ITEM4_REPORT_SNAPSHOT_AUTHOR',field='report_snapshot_author_scope',
            assessment='cpu_diagnostic_fixture_correction',previous_reason='WHOLE_FIXTURE_AUTHOR_ACCEPTED_NATIVE_AND_REVIEW_REQUIRED',
            previous_review=15,previous_call=sha((RUN+':run_spec_review:15').encode()),
            folder='report-snapshot-author',result='report_snapshot_author')
    if audited_review(p):
        return dict(author=21,reviewer=16,count=36,batch=74,limit=39,batch_limit=77,
            event='REVIEWED_ITEM4_AUDITED_NATIVE_REVIEW',field='audited_native_review_scope',
            assessment='cpu_diagnostic_fixture_correction',previous_reason='WHOLE_FIXTURE_AUTHOR_ACCEPTED_NATIVE_AND_REVIEW_REQUIRED',
            previous_review=15,previous_call=sha((RUN+':run_spec_review:15').encode()),
            folder='audited-native-review',result='audited_native_scientific_review')
    if corrected_review(p):
        return dict(author=20,reviewer=16,count=35,batch=73,limit=38,batch_limit=76,
            event='REVIEWED_ITEM4_CORRECTED_NATIVE_REVIEW',field='corrected_native_review_scope',
            assessment='cpu_diagnostic_fixture_correction',previous_reason='CPU_DIAGNOSTIC_AUTHORING_REVISE_EXECUTION_HELD',
            previous_review=15,previous_call=sha((RUN+':run_spec_review:15').encode()),
            folder='corrected-native-review',result='corrected_native_scientific_review')
    if fixture_audit(p):
        return dict(author=21,reviewer=16,count=35,batch=73,limit=39,batch_limit=77,
            event='REVIEWED_ITEM4_WHOLE_FIXTURE_AUTHOR',field='whole_fixture_author_scope',
            assessment='cpu_diagnostic_fixture_correction',previous_reason='CPU_DIAGNOSTIC_AUTHORING_REVISE_EXECUTION_HELD',
            previous_review=15,previous_call=sha((RUN+':run_spec_review:15').encode()),
            folder='whole-fixture-author',result='whole_fixture_author')
    if fixture_correction(p):
        return dict(author=20, reviewer=15, count=33, batch=71, limit=37, batch_limit=75,
            event='REVIEWED_ITEM4_DIAGNOSTIC_FIXTURE_CORRECTION', field='cpu_diagnostic_fixture_scope',
            assessment='cpu_diagnostic_scoped_review', previous_reason='NATIVE_HARNESS_ACCEPTED_NATIVE_EVIDENCE_REQUIRED',
            previous_review=14, previous_call=sha((RUN+':run_spec_review:14').encode()),
            folder='cpu-diagnostic-fixture-correction', result='cpu_diagnostic_fixture_correction')
    if plaintext_recovery(p):
        return dict(author=19, reviewer=15, count=32, batch=70, limit=36, batch_limit=74,
            event='REVIEWED_ITEM4_DIAGNOSTIC_PLAINTEXT_RECOVERY', field='cpu_diagnostic_plaintext_scope',
            assessment='cpu_diagnostic_scoped_review', previous_reason=OPAQUE_REASON,
            previous_review=14, previous_call=sha((RUN+':run_spec_review:14').encode()),
            folder='cpu-diagnostic-plaintext-recovery', result='cpu_diagnostic_plaintext_recovery')
    if native_harness(p):
        return dict(author=18, reviewer=15, count=31, batch=69, limit=35, batch_limit=73,
            event='REVIEWED_ITEM4_DIAGNOSTIC_NATIVE_HARNESS', field='cpu_diagnostic_native_harness_scope',
            assessment='cpu_diagnostic_scoped_review', previous_reason='CPU_DIAGNOSTIC_AUTHORING_REVISE_EXECUTION_HELD',
            previous_review=14, previous_call=sha((RUN+':run_spec_review:14').encode()),
            folder='cpu-diagnostic-native-harness', result='cpu_diagnostic_native_harness')
    if scoped_review(p):
        return dict(author=17, reviewer=14, count=30, batch=68, limit=33, batch_limit=71,
            event='REVIEWED_ITEM4_DIAGNOSTIC_SCOPED_REVIEW', field='cpu_diagnostic_scoped_review_scope',
            assessment='cpu_diagnostic_recovery', previous_reason='CPU_DIAGNOSTIC_AUTHORING_REVISE_EXECUTION_HELD',
            previous_review=13, previous_call=sha((RUN+':run_spec_review:13').encode()),
            folder='cpu-diagnostic-scoped-review', result='cpu_diagnostic_scoped_review')
    if p.get('schema') == RECOVERY_SCHEMA:
        return dict(author=17, reviewer=13, count=28, batch=66, limit=32, batch_limit=70,
            event='REVIEWED_ITEM4_DIAGNOSTIC_ENTRYPOINT_RECOVERY', field='cpu_diagnostic_recovery_scope',
            assessment='post_smoke_response', previous_reason=FAILED_REASON,
            previous_review=12, previous_call=REVIEW, folder='cpu-diagnostic-recovery', result='cpu_diagnostic_recovery')
    require(p.get('schema') == DIAGNOSTIC_SCHEMA, 'SCHEMA')
    return dict(author=16, reviewer=13, count=27, batch=65, limit=31, batch_limit=69,
        event='REVIEWED_ITEM4_CPU_DIAGNOSTIC_AUTHORING', field='cpu_diagnostic_authoring_scope',
        assessment='post_smoke_response', previous_reason='POST_SMOKE_RESPONSE_REVISE_EXECUTION_HELD',
        previous_review=12, previous_call=REVIEW, folder='cpu-diagnostic-authoring', result='cpu_diagnostic_authoring')


def call(p,role):
    q=profile(p);stage='run_spec_'+role
    return sha((RUN+':'+stage+':'+str(q['author' if role=='author' else 'reviewer'])).encode())


def scope(p,approval):
    q=profile(p)
    require(p.get('run_id')==RUN and p.get('authority_sha256')==prior.AUTHORITY
        and (p.get('author_attempt'),p.get('review_attempt'),p.get('run_limit'),p.get('batch_limit'))==
            (q['author'],q['reviewer'],q['limit'],q['batch_limit'])
        and p.get('execution_authorized') is False,'SCOPE')
    require(isinstance(approval,str) and len(approval)==64 and all(c in '0123456789abcdef' for c in approval),'APPROVAL')
    require(len(p['local_calls'])==len(p['global_calls'])==q['count'] and len(p['batch_calls'])==q['batch']
        and set(p['local_calls'])==set(p['global_calls'])
        and all(p['batch_calls'].get(i)==pin for i,pin in p['global_calls'].items()),'CALL_SCOPE')
    old=json.loads(p['original_state'])
    require(sha(p['original_state'].encode())==p['state_sha256'] and old['phase']=='BLOCKED'
        and old['reason']==q['previous_reason']
        and ((old.get('pending') or {}).get('id')==(DELIVERY_FAILED_CALL if delivery_recovery(p) else SENDER_FAILED_CALL) if sender_recovery(p) else
            ((old.get('pending') or {}).get('id')==(OPAQUE_AUTHOR if plaintext_recovery(p) else FAILED_AUTHOR)
            if p['schema']==RECOVERY_SCHEMA or plaintext_recovery(p) else not old.get('pending')))
        and old['rounds']=={'run_spec_author':23 if delivery_recovery(p) else 21 if sender_recovery(p) else q['author']-(not scoped_review(p)),'run_spec_review':q['previous_review']},'CHECKPOINT')
    if sender_recovery(p):
        rec=p['sender_recovery'];previous=rec['previous_scope']
        require(set(rec)=={'failed_call_id','previous_scope','previous_approval','classifier_approval'}
            and rec['failed_call_id']==SENDER_FAILED_CALL and report_snapshot(previous) and not sender_recovery(previous)
            and rec['previous_approval']=='4d59456204b35a061102a839efcc5239aba6abfe9f58cebac87d72a5b726e5a5'
            and rec['classifier_approval']=='a54ef800461b974db328d18fba65e4d6d819044a3a003d9699a59603b0710139','SENDER_RECOVERY_AUTHORITY')
        scope(previous,rec['previous_approval'])
        require(set(p['local_calls'])==set(previous['local_calls'])|{SENDER_FAILED_CALL}|({DELIVERY_FAILED_CALL} if delivery_recovery(p) else set())
            and set(p['batch_calls'])==set(previous['batch_calls'])|{SENDER_FAILED_CALL}|({DELIVERY_FAILED_CALL} if delivery_recovery(p) else set())
            and all(p[k]==previous[k] for k in ('fixture_reference','native_failure','assessment','author_outputs','baseline_plan','diagnostic_micro_usd','stage1_micro_usd','projection_micro_usd','total_micro_usd')),'SENDER_RECOVERY_PRESERVED_SCOPE')
    if delivery_recovery(p):
        rec=p['delivery_recovery'];previous=rec['previous_scope']
        require(set(rec)=={'failed_call_id','previous_scope','previous_approval','outputs','native_format','original_module_sha256','patch_limit_bytes','direction_report_sha256'}
            and rec['failed_call_id']==DELIVERY_FAILED_CALL and sender_recovery(previous) and not delivery_recovery(previous)
            and rec['previous_approval']=='aff49bc6cc3ec2b402c7a89549cd643be8c2ed038260c4bff49f0522a829af5f'
            and rec['patch_limit_bytes']==96000 and rec['direction_report_sha256']=='caab7b6bfbb60bfba05b94233ce174156a11a811a26e8a0b27d529da208f5a88'
            and rec['original_module_sha256']=='8e633a1e72457efa8d59099663ab64e6e43b21dbb0216996c3103aec9a67bd04',
            'DELIVERY_RECOVERY_SCOPE')
        scope(previous,rec['previous_approval'])
        require(set(p['local_calls'])==set(previous['local_calls'])|{DELIVERY_FAILED_CALL}
            and set(p['batch_calls'])==set(previous['batch_calls'])|{DELIVERY_FAILED_CALL}
            and all(p[k]==previous[k] for k in ('fixture_reference','native_failure','assessment','author_outputs','baseline_plan','diagnostic_micro_usd','stage1_micro_usd','projection_micro_usd','total_micro_usd')),
            'DELIVERY_RECOVERY_PRESERVED_SCOPE')
    a=p['assessment']
    flags=('full_training_admitted','coverage_released',
        'execution_authorized' if diagnostic(p) else 'whole_plan_complete')
    require(sha(canonical(a))==p['assessment_sha256'] and old.get(q['assessment'])==a
        and a.get('call_id')==q['previous_call'] and a.get('verdict')=='REVISE'
        and all(a.get(k) is False for k in flags),'ASSESSMENT')
    if diagnostic(p):
        require(p.get('operator_decision_sha256')==DIAGNOSTIC_DECISION
            and p.get('diagnostic_micro_usd')==25_000_000
            and p.get('stage1_micro_usd')==150_000_000
            and p.get('projection_micro_usd')==1_200_000_000
            and p.get('total_micro_usd')==1_275_000_000
            and p.get('automatic_retry') is False,'DIAGNOSTIC_AUTHORITY')
        require(sha(p['baseline_plan'].encode())==p['baseline_plan_sha256']
            and len(p['baseline_module_sha256'])==64,'BASELINE_BINDING')
    if p['schema']==RECOVERY_SCHEMA:
        require(p.get('direction_sha256')==RECOVERY_DIRECTION and p.get('failed_call_id')==FAILED_AUTHOR
            and set(p.get('failed_outputs',{}))=={'SPEC.proposed.md','execution.plan.json','notebook.patch.json'},
            'RECOVERY_AUTHORITY')
    if scoped_review(p):
        require(a['report_sha256']==(REVIEW15_REPORT if corrected_review(p) else SCOPED_REVIEW13_REPORT)
            and set(p.get('author_outputs',{}))=={'SPEC.proposed.md','execution.plan.json','notebook.patch.json'}
            and p.get('accepted_author_event')=={'schema':'validated-author-output/v1',
                'call_id':call(p,'author'),'stage':'run_spec_author','attempt':q['author'],'output_sha256':p['author_outputs']},
            'SCOPED_REVIEW_AUTHORITY')
    if fixture_audit(p):
        require(a['report_sha256']==REVIEW15_REPORT and a.get('global_findings_closed') is False
            and p.get('reference_author_call_id')==sha((RUN+':run_spec_author:'+str(fixture.parameters(p)['attempt'])).encode())
            and p.get('diagnostic_plan_sha256')==p['author_outputs']['execution.plan.json']
            and p.get('accepted_author_event')=={'schema':'validated-author-output/v1',
                'call_id':p['reference_author_call_id'],'stage':'run_spec_author','attempt':fixture.parameters(p)['attempt'],
                'output_sha256':p['author_outputs']},'AUDIT_REFERENCE_AUTHORITY')
    elif native_harness(p):
        require(a['report_sha256']==NATIVE_REVIEW14_REPORT and a.get('global_findings_closed') is False
            and a.get('scientific_scope')=='two-cpu-diagnostic-fits-only'
            and p.get('reference_author_call_id')==sha((RUN+':run_spec_author:17').encode())
            and p.get('diagnostic_plan_sha256')==p['author_outputs']['execution.plan.json']
            and p.get('accepted_author_event')=={'schema':'validated-author-output/v1',
                'call_id':p['reference_author_call_id'],'stage':'run_spec_author','attempt':17,
                'output_sha256':p['author_outputs']},'NATIVE_HARNESS_AUTHORITY')
    if plaintext_recovery(p):
        require(p.get('failed_call_id')==OPAQUE_AUTHOR
            and set(p.get('failed_outputs',{}))=={'SPEC.proposed.md','execution.plan.json','notebook.patch.json'}
            and p.get('failed_format',{}).get('status')=='ACCEPTED'
            and p['failed_format'].get('files')==p['failed_outputs'],'PLAINTEXT_FAILURE_SCOPE')
    if fixture_correction(p):fixture.scope(p)
    return old


def reference_author(driver,p):
    from orchestrator import author_revision_accounting as accounting,private_records as pr
    require(native_harness(p),'NATIVE_HARNESS_ONLY')
    if fixture_correction(p):return fixture.reference(driver,p)
    row=driver.store.db.execute('SELECT * FROM manual_calls WHERE id=?',(p['reference_author_call_id'],)).fetchone()
    require(row is not None and accounting._accepted(driver.store,dict(row)),'REFERENCE_AUTHOR_ACCEPTED')
    receipt=json.loads(row['receipt']);work=Path(receipt['workspace'])
    require(receipt['output_sha256']==p['author_outputs'] and work.name=='run_spec_author-17','REFERENCE_AUTHOR_BINDING')
    for name,pin in p['author_outputs'].items():
        require(sha(pr.check(work/name).read_bytes())==pin,'REFERENCE_AUTHOR_CHANGED')
    return dict(row)


def frozen_author(driver,p,value=None):
    """Review-only: accepted author and every authored artifact stay frozen."""
    from orchestrator import author_revision_accounting as accounting,private_records as pr,context_budget as cb
    require(scoped_review(p),'SCOPED_REVIEW_ONLY')
    row=driver.store.db.execute('SELECT * FROM manual_calls WHERE id=?',(call(p,'author'),)).fetchone()
    require(row is not None and accounting._accepted(driver.store,dict(row)),'SCOPED_ACCEPTED_AUTHOR')
    receipt=json.loads(row['receipt']);work=Path(receipt['workspace'])
    require(receipt['output_sha256']==p['author_outputs'] and work.name=='run_spec_author-'+str(profile(p)['author']),'SCOPED_AUTHOR_BINDING')
    for name,pin in p['author_outputs'].items():
        require(sha(pr.check(work/name).read_bytes())==pin,'SCOPED_AUTHOR_CHANGED')
    old=json.loads(p['original_state']);refs=old['artifacts']
    if value is not None:
        current=value['artifacts'];prefix=profile(p)['folder']+'-'
        require(current[:len(refs)]==refs and all(ref.get('type')=='result_tables' and
            (ref.get('id','').startswith(prefix) or (corrected_review(p) and ref.get('id','').startswith('diagnostic-native21-' if audited_review(p) else 'diagnostic-native20-'))) for ref in current[len(refs):]) and
            value.get('notebook_revision_result')==old.get('notebook_revision_result'),'SCOPED_ARTIFACT_CHANGED')
    for ref in refs:
        if ref.get('version')==profile(p)['author']:
            raw=pr.check(cb.relative_file(Path(driver.config['context']),ref['path'])).read_bytes()
            require(sha(raw)==ref['sha256'],'SCOPED_ARTIFACT_BYTES_CHANGED')
    return dict(row)


def failed_author(store,p):
    """Only the frozen completed, unaccepted interface failure may be retried."""
    from orchestrator import private_records as pr
    require(p.get('schema')==RECOVERY_SCHEMA or plaintext_recovery(p),'RECOVERY_ONLY')
    ident=OPAQUE_AUTHOR if plaintext_recovery(p) else FAILED_AUTHOR
    attempt=18 if plaintext_recovery(p) else 16
    rows=[]
    for db,table in [(store.db,'manual_calls'),(store.batch.db,'autonomy_calls')]:
        row=db.execute('SELECT * FROM '+table+' WHERE id=?',(ident,)).fetchone()
        require(row is not None and row['status']=='COMPLETE','FAILED_AUTHOR_TERMINAL')
        rows.append(dict(row))
    row=rows[0];receipt=json.loads(row['receipt'])
    require(row['stage']=='run_spec_author' and row['attempt']==attempt
        and not store.db.execute('SELECT 1 FROM events WHERE id=?',('author-accepted:'+ident,)).fetchone()
        and receipt.get('output_sha256')==p['failed_outputs']
        and receipt.get('native',{}).get('transport_returncode')==0,'EXACT_UNACCEPTED_AUTHOR')
    work=Path(receipt['workspace'])
    require(work.name=='run_spec_author-'+str(attempt) and work.parent==Path(store.path).parent.parent/(Path(store.path).parent.name+'-scientific-workspaces'),
        'FAILED_WORKSPACE')
    for name,pin in p['failed_outputs'].items():
        require(sha(pr.check(work/name).read_bytes())==pin,'FAILED_OUTPUT_CHANGED')
    require(sha(pr.check(work/'console.log').read_bytes())==receipt['native']['console_sha256'],'FAILED_STREAM_CHANGED')
    require((json.loads(p['original_state']).get('pending') or {}).get('workspace')==str(work),
        'FAILED_PENDING_BINDING')
    if plaintext_recovery(p):
        # Authenticate original submission bytes without rerunning the new
        # validator on an intentionally refused historical payload.
        saved=receipt['native'].get('author_submission')
        require(saved==p['failed_format'],'FAILED_FORMAT_RECEIPT_CHANGED')
        require(sha(pr.check(work/'.author-submission.json').read_bytes())==saved['record_sha256']
            and sha(pr.check(work/'.author-runtime/config.json').read_bytes())==saved['config_sha256'],
            'FAILED_FORMAT_BYTES_CHANGED')
    return row


def failed_sender(store,p):
    """Exact terminal unsubmitted attempt stays UNCERTAIN and counted."""
    from orchestrator import author_revision_accounting as accounting
    require(sender_recovery(p) and _sender_verifier is not None,'SENDER_QUALIFIER_REQUIRED')
    row=store.db.execute('SELECT * FROM manual_calls WHERE id=?',(SENDER_FAILED_CALL,)).fetchone()
    global_row=store.batch.db.execute('SELECT * FROM autonomy_calls WHERE id=?',(SENDER_FAILED_CALL,)).fetchone()
    require(row is not None and global_row is not None and row['status']==global_row['status']=='UNCERTAIN'
        and row['attempt']==22 and row['stage']=='run_spec_author'
        and sha(canonical(dict(row)))==p['local_calls'][SENDER_FAILED_CALL]
        and sha(canonical(dict(global_row)))==p['global_calls'][SENDER_FAILED_CALL]
        and not accounting._accepted(store,dict(row)),'EXACT_FAILED_SENDER')
    result=_sender_verifier(dict(global_row))
    require(result['id']==SENDER_FAILED_CALL and result['classification']=='EXACT_TERMINAL_PRE_SDK_AUTHOR22_ADMIN_ONLY','SENDER_TERMINAL_PROOF')
    return dict(row)



def failed_delivery(store,p):
    from orchestrator import private_records as pr,author_revision_accounting as accounting
    require(delivery_recovery(p),'DELIVERY_SCOPE_REQUIRED')
    rec=p['delivery_recovery'];row=store.db.execute('SELECT * FROM manual_calls WHERE id=?',(DELIVERY_FAILED_CALL,)).fetchone()
    other=store.batch.db.execute('SELECT * FROM autonomy_calls WHERE id=?',(DELIVERY_FAILED_CALL,)).fetchone()
    require(row is not None and other is not None and row['status']==other['status']=='COMPLETE'
        and row['attempt']==23 and row['stage']=='run_spec_author' and not accounting._accepted(store,dict(row))
        and sha(canonical(dict(row)))==p['local_calls'][DELIVERY_FAILED_CALL]
        and sha(canonical(dict(other)))==p['global_calls'][DELIVERY_FAILED_CALL],'EXACT_REFUSED_AUTHOR23')
    saved=json.loads(row['receipt']);work=Path(saved['workspace'])
    require(saved['output_sha256']==rec['outputs'] and saved['native']['author_submission']==rec['native_format']
        and work.name=='run_spec_author-23' and str(work)==json.loads(p['original_state'])['pending']['workspace'],
        'DELIVERY_ORIGINAL_BINDING')
    for name,pin in rec['outputs'].items():require(sha(pr.check(work/name).read_bytes())==pin,'DELIVERY_ORIGINAL_CHANGED')
    require(sha(pr.check(work/'.author-submission.json').read_bytes())==rec['native_format']['record_sha256']
        and sha(pr.check(work/'console.log').read_bytes())==saved['native']['console_sha256'],'DELIVERY_NATIVE_CHANGED')
    return dict(row)


def originals(store,p,approval):
    scope(p,approval)
    require(sha((Path(store.path).parent/'lane.json').read_bytes())==p['configuration_sha256'],'CONFIGURATION')
    for db,table,pins in [(store.db,'manual_calls',p['local_calls']),
            (store.batch.db,'autonomy_calls',p['batch_calls'])]:
        for ident,pin in pins.items():
            row=db.execute('SELECT * FROM '+table+' WHERE id=?',(ident,)).fetchone()
            require(row is not None and sha(canonical(dict(row)))==pin,'ORIGINAL_CHANGED')
    if p['schema']==RECOVERY_SCHEMA or plaintext_recovery(p):failed_author(store,p)
    if fixture_correction(p):fixture.failure(store,p)
    if sender_recovery(p):
        granted(store,p['sender_recovery']['previous_scope'],p['sender_recovery']['previous_approval'])
        failed_sender(store,p)
    if delivery_recovery(p):
        granted(store,p['delivery_recovery']['previous_scope'],p['delivery_recovery']['previous_approval'])
        failed_delivery(store,p)


def proof(p,approval):
    scope(p,approval);q=profile(p)
    result={'schema':('item4-cpu-diagnostic-authoring-grant/v1' if diagnostic(p)
            else 'item4-post-smoke-response-grant/v1'),'run_id':RUN,
        'checkpoint_sha256':sha(canonical(p)),'review_sha256':approval,
        'authority_sha256':prior.AUTHORITY,'author_call_id':call(p,'author'),'review_call_id':call(p,'review'),
        'run_limit':q['limit'],'batch_limit':q['batch_limit'],'execution_authorized':False}
    if diagnostic(p):result['operator_decision_sha256']=DIAGNOSTIC_DECISION
    return result


def granted(store,p,approval):
    originals(store,p,approval)
    row=store.db.execute('SELECT payload FROM events WHERE id=?',(profile(p)['event'],)).fetchone()
    require(row is not None and json.loads(row[0])==proof(p,approval),'GRANT')


def review_binding(driver,p,approval):
    from orchestrator.experiment_approval import verified_review_delivery
    from orchestrator.author_revision_accounting import AUTHORITY
    from orchestrator.review_contract import scientific
    originals(driver.store,p,approval)
    q=profile(p)
    work=Path(driver.config.get('workspace_root',driver.state.parent/(driver.state.name+'-scientific-workspaces')))/('run_spec_review-'+str(q['previous_review']))
    pending={'stage':'run_spec_review','round':q['previous_review'],'workspace':str(work),'id':q['previous_call']}
    _,_,raw,receipt,row,submission=verified_review_delivery(driver,pending,'run_spec_review')
    decision=scientific(raw);a=p['assessment']
    require(decision['verdict']=='REVISE' and decision['findings'] and sha(raw)==a['report_sha256']
        and sha(row['receipt'].encode())==a['call_receipt_sha256']
        and sha(submission)==a['submission_sha256'],'GENUINE_REVISE')
    # This exact existing budget finding permits drafting a response, not a
    # changed budget or execution. All other reserved findings still refuse.
    reserved=[f for f in decision['findings'] if f['category'] in {'budget','privacy/secret','test-set/leakage'}]
    if fixture_audit(p):
        require([(f['id'],f['category']) for f in decision['findings']]==[
            ('DIAG-U2-changed-module-native-integration-unverified','execution authority/provenance'),
            ('U1-input-provenance','execution authority/provenance'),
            ('U2-runtime-interface-native-integration','code/spec mismatch'),
            ('U3-coverage-arm-source-validation','code/spec mismatch'),
            ('STAGE1-full-projection-exceeds-authorized-caps','budget'),
            ('STAGE1-partial-arm-coverage-and-single-arm-extrapolation','metric/statistic'),
            ('F-SELF-REVIEW-NOT-OPPOSING','execution authority/provenance')],'EXACT_REVISE15_FINDINGS')
        reference_author(driver,p)
    elif native_harness(p):
        require(not reserved and [f['id'] for f in decision['findings']]==
            ['DIAG-U2-changed-module-native-integration-unverified'],'NATIVE_FINDING_SCOPE')
        reference_author(driver,p)
    else:
        require(len(reserved)==1 and reserved[0]['category']=='budget'
            and reserved[0]['id']=='STAGE1-full-projection-exceeds-authorized-caps','PROPOSAL_ONLY_BUDGET_SCOPE')
    if scoped_review(p):
        return {'schema':'cpu-diagnostic-scoped-review-context/v1','stage':'run_spec_review','round':q['reviewer'],
            'author_call_id':call(p,'author'),'carried_review_sha256':sha(raw),
            'carried_submission_sha256':sha(submission),'global_findings_closed':False,
            'implementation_review_sha256':approval,'execution_authorized':False}
    return {'schema':'scientific-revision-response/v1','authority_sha256':AUTHORITY,
        'run_id':RUN,'stage':'run_spec_author','author_attempt':q['author'],'author_call_id':call(p,'author'),
        'review_call_id':q['previous_call'],'review_round':q['previous_review'],'review_sha256':sha(raw),
        'review_receipt_sha256':sha(row['receipt'].encode()),'submission_sha256':sha(submission),
        'continuation_authority_sha256':prior.AUTHORITY,'continuation_review_sha256':approval,
        'proposal_only':True}


def activate(driver,p,approval,dest):
    from orchestrator import private_records as pr
    old=scope(p,approval);q=profile(p);originals(driver.store,p,approval)
    db=driver.store.db;raw=db.execute('SELECT payload FROM manual_state WHERE id=1').fetchone()[0]
    require(raw==p['original_state'] and db.execute('SELECT count(*) FROM manual_calls').fetchone()[0]==q['count'],'EXACT_BLOCK')
    require(not driver.store.batch.db.execute("SELECT 1 FROM autonomy_calls WHERE status='RUNNING'").fetchone(),'RUNNING')
    binding=review_binding(driver,p,approval)
    if scoped_review(p):frozen_author(driver,p,old)
    require(not Path(dest).exists() and not Path(dest).is_symlink(),'EXISTS_RECONCILE')
    pr.mkdir(dest);pr.write_bytes(Path(dest)/'original-state.json',raw.encode())
    grant=proof(p,approval);pr.write_bytes(Path(dest)/'intent.json',canonical(grant))
    value={**old,'phase':'run_spec_review' if scoped_review(p) else 'run_spec_author','reason':q['event'],q['field']:grant}
    if p['schema']==RECOVERY_SCHEMA or plaintext_recovery(p) or sender_recovery(p):value.pop('pending',None)
    # Keep the old execution review and all obligations. The actual smoke
    # critique is supplied separately and bound through the accepted receipt.
    value['interventions']=[*old.get('interventions',[]),grant]
    db.execute('BEGIN IMMEDIATE')
    try:
        require(db.execute('SELECT payload FROM manual_state WHERE id=1').fetchone()[0]==raw,'STATE_DRIFT')
        originals(driver.store,p,approval)
        db.execute('INSERT INTO events VALUES(?,?,?)',(q['event'],RUN,json.dumps(grant,sort_keys=True)))
        db.execute('UPDATE manual_state SET payload=? WHERE id=1',(json.dumps(value),));db.execute('COMMIT')
    except BaseException:db.execute('ROLLBACK');raise
    pr.write_bytes(Path(dest)/'applied.json',canonical({'status':('READY_DIAGNOSTIC_REVIEW'+str(q['reviewer']) if scoped_review(p) else 'READY_DIAGNOSTIC_AUTHOR'+str(q['author']) if diagnostic(p) else 'READY_PROPOSAL_AUTHOR15'),'binding':binding,'grant':grant,'model_calls':0}))
    return {'status':('READY_DIAGNOSTIC_REVIEW'+str(q['reviewer']) if scoped_review(p) else 'READY_DIAGNOSTIC_AUTHOR'+str(q['author']) if diagnostic(p) else 'READY_PROPOSAL_AUTHOR15'),'model_calls':0,'execution_authorized':False}


def validate_diagnostic_delta(plan_raw,module_raw,p):
    """Require executable author output and preserve every original scientific fit.

    This structural check does not claim the authored instrumentation is correct;
    ordinary synthetic execution and independent scientific review still judge it.
    """
    require(diagnostic(p),'DIAGNOSTIC_ONLY')
    require(isinstance(plan_raw,bytes) and isinstance(module_raw,bytes),'AUTHOR_BYTES')
    from orchestrator.review_contract import strict_json
    baseline=strict_json(p['baseline_plan'].encode());plan=strict_json(plan_raw)
    require(set(plan)==set(baseline) and all(plan[k]==baseline[k] for k in baseline if k!='fits'),
        'ORIGINAL_PLAN_CHANGED')
    count=len(baseline['fits']);fits=plan['fits']
    require(isinstance(fits,list) and len(fits)==count+2 and fits[:count]==baseline['fits'],
        'ORIGINAL_FITS_CHANGED')
    extra=fits[count:];ids=[f['fit_id'] for f in fits]
    require(len(set(ids))==len(ids) and all(f['stage']=='SMOKE' for f in extra),'DIAGNOSTIC_FITS')
    resume=next(f for f in baseline['fits'] if f['fit_id']==baseline['full_training']['resume_fit_id'])
    require(all((f['arm'],f['fold'],f.get('preprocessing_id'))==
        (resume['arm'],resume['fold'],resume.get('preprocessing_id')) for f in extra),'BASE_ARM_FOLD')
    require(sha(module_raw)!=p['baseline_module_sha256'],'EXECUTABLE_CHANGE_REQUIRED')
    if native_harness(p):
        require(sha(plan_raw)==p['diagnostic_plan_sha256'],'DIAGNOSTIC_PLAN_CHANGED')
        import ast
        functions=[node for node in ast.parse(module_raw).body if isinstance(node,ast.FunctionDef)
            and node.name=='native_synthetic_integration']
        require(len(functions)==1 and not functions[0].decorator_list
            and [a.arg for a in functions[0].args.args]==['progress_factory']
            and not any((functions[0].args.defaults,functions[0].args.kwonlyargs,
                functions[0].args.posonlyargs,functions[0].args.vararg,functions[0].args.kwarg)),
            'NATIVE_ENTRYPOINT_REQUIRED')
    if corrected_review(p):
        require(sha(module_raw)==p['module_sha256']==('fa54d6e41db935c4a7671abe278d4a40423bda41cfce32692b58ed1364638d20'
            if audited_review(p) else '501cb5b8e8487a2b73f1e139fe5cc96cb6c3315c1c8832ffefd351e31f5c8749')
            and sha(plan_raw)==p['diagnostic_plan_sha256']=='31c3e4a57f8df616b1b8be0aa37516408196d5c545ded0efb5eaad1b4e23370a',
            'CORRECTED_ACCEPTED_BYTES')
    if fixture_correction(p):fixture.correction(module_raw,p)
    return {'execution_plan_sha256':sha(plan_raw),'module_sha256':sha(module_raw),
        'fit_ids':[f['fit_id'] for f in extra],'execution_authorized':False}


def executable_candidate(driver,value,p):
    from orchestrator import experiment_plan_output as authored,context_budget as cb,private_records as pr
    from types import SimpleNamespace
    context=Path(driver.config['context'])
    view=SimpleNamespace(config=driver.config,context=context,state=driver.state)
    ref=authored.ref(view,value)
    raw=pr.check(cb.relative_file(context,ref['path'])).read_bytes()
    folder=Path(value['notebook_revision_result']['folder'])
    module=pr.check(folder/'synthetic/package/execution.py').read_bytes()
    return validate_diagnostic_delta(raw,module,p)


def protected_keys(p):
    keys=('review','spec_review','reviewed_execution','smoke_review','dispatch_sha256','fit_continuations',
        'execution_package','fit_dispatch','fit_collections','fit_collection_receipts',
        'fit_selection_waves','preprocessing_dispatch','preprocessing_selection_waves')
    if diagnostic(p):keys+=('post_smoke_response','post_smoke_response_scope')
    if p['schema']==RECOVERY_SCHEMA or scoped_review(p):keys+=('cpu_diagnostic_authoring_scope',)
    if scoped_review(p):keys+=('cpu_diagnostic_recovery_scope','cpu_diagnostic_recovery','notebook_revision_result')
    if native_harness(p):keys+=('cpu_diagnostic_authoring_scope','cpu_diagnostic_recovery_scope',
        'cpu_diagnostic_recovery','cpu_diagnostic_scoped_review_scope','cpu_diagnostic_scoped_review')
    if plaintext_recovery(p) or fixture_correction(p):keys+=('cpu_diagnostic_native_harness_scope',)
    if fixture_correction(p):keys+=('cpu_diagnostic_plaintext_scope',)
    if corrected_review(p) or fixture_audit(p):keys+=('cpu_diagnostic_native_harness_scope','cpu_diagnostic_plaintext_scope',
        'cpu_diagnostic_fixture_scope','cpu_diagnostic_fixture_correction','cpu_diagnostic_scoped_review_scope','cpu_diagnostic_scoped_review')
    if audited_review(p) or report_snapshot(p):keys+=('whole_fixture_author_scope',)
    return keys


def ready(driver,value,p,approval):
    granted(driver.store,p,approval)
    q=profile(p)
    require(value.get(q['field'])==proof(p,approval) and not value.get('pending'),'STATE_SCOPE')
    stage=value.get('phase');rounds=value.get('rounds')
    if fixture_audit(p):require(stage=='run_spec_author','AUDIT_AUTHOR_ONLY_NATIVE_AND_REVIEW_HELD')
    if native_harness(p) and not fixture_correction(p):
        # This installation admits authoring only. Native execution and delivery
        # need their own reviewed connection before the reserved reviewer slot.
        require(stage=='run_spec_author','NATIVE_EVIDENCE_REQUIRED_BEFORE_REVIEW')
    if scoped_review(p):
        require(stage=='run_spec_review','SCOPED_REVIEW_STAGE_ONLY')
        frozen_author(driver,p,value)
    require((stage,rounds) in [('run_spec_author',{'run_spec_author':23 if delivery_recovery(p) else 21 if sender_recovery(p) else q['author']-1,'run_spec_review':q['previous_review']}),
        ('run_spec_review',{'run_spec_author':q['author'],'run_spec_review':q['previous_review']})],'STATE')
    old=scope(p,approval)
    for key in protected_keys(p):
        require(value.get(key)==old.get(key),'EXECUTION_AUTHORITY_CHANGED')
    review_binding(driver,p,approval)
    if diagnostic(p) and stage=='run_spec_review':executable_candidate(driver,value,p)


def connect_roles(accounting,recovery,p,approval):
    scope(p,approval);q=profile(p)
    if delivery_recovery(p):
        rec=p['delivery_recovery'];connect_roles(accounting,recovery,rec['previous_scope'],rec['previous_approval'])
    elif sender_recovery(p):
        rec=p['sender_recovery'];connect_roles(accounting,recovery,rec['previous_scope'],rec['previous_approval'])
    if scoped_review(p):
        old_limit=recovery.role_limit
        def scoped_limit(store,run,stage):
            if run!=RUN or stage!='run_spec_review':return old_limit(store,run,stage)
            value=prior.state(store)
            if value.get(q['field'])!=proof(p,approval):return old_limit(store,run,stage)
            driver=accounting.context(store,run);require(driver is not None,'REVIEW_CONTEXT')
            ready(driver,value,p,approval)
            require(store.db.execute('SELECT count(*) FROM manual_calls').fetchone()[0]==q['count'],'SCOPED_REVIEW_ONCE')
            return q['reviewer']
        recovery.role_limit=scoped_limit
        return
    old_binding,old_inspect,old_limit=accounting.review_binding,accounting.inspect,recovery.role_limit
    def binding(driver,stage,number,author):
        if driver.config['run_id']!=RUN or (stage,number,author)!=('run_spec_author',q['previous_review'],q['author']):
            return old_binding(driver,stage,number,author)
        granted(driver.store,p,approval);return review_binding(driver,p,approval)
    def inspect(store,run,stage):
        if native_harness(p) and run==RUN and stage=='run_spec_author':
            value=prior.state(store)
            if value.get('phase')==stage and value.get('reason')==q['event']:
                # The approved author17 repair and failed author16 reference
                # the same review12. The generic duplicate-review guard cannot
                # represent that preserved history. Replace it ONLY here with
                # exact frozen row hashes, genuine historical receipt bindings,
                # accepted author17 and this one new review14 response.
                driver=accounting.context(store,run);require(driver is not None,'AUTHOR_CONTEXT')
                ready(driver,value,p,approval)
                rows=[dict(r) for r in store.db.execute('SELECT * FROM manual_calls ORDER BY rowid')]
                require(len(rows)==q['count'] and set(r['id'] for r in rows)==set(p['local_calls']),'AUTHOR_ONCE')
                used={};failures=0
                for row in rows:
                    if row['stage']!=stage:continue
                    if delivery_recovery(p) and row['id']==DELIVERY_FAILED_CALL:
                        failed_delivery(store,p);failures+=1;continue
                    if sender_recovery(p) and row['id']==SENDER_FAILED_CALL:
                        failed_sender(store,p);failures+=1;continue
                    saved=json.loads(row['receipt']).get(accounting.FIELD)
                    if saved is None:
                        failures+=int(not accounting._accepted(store,row));continue
                    expected=accounting.review_binding(driver,stage,saved['review_round'],row['attempt'])
                    require(saved==expected and row['id']==saved['author_call_id'],'HISTORICAL_REVISION_RECEIPT')
                    previous=used.get(saved['review_call_id'])
                    if previous is not None:
                        original_pair=((previous['attempt'],row['attempt'],saved['review_round'])==(16,17,12)
                            and previous['id']==FAILED_AUTHOR)
                        fixture_pair=(fixture_correction(p) and
                            (previous['attempt'],row['attempt'],saved['review_round'])==(18,19,14)
                            and previous['id']==OPAQUE_AUTHOR
                            and row['id']==call({'schema':PLAINTEXT_SCHEMA},'author'))
                        # The whole-fixture successor retains the already
                        # approved, accepted author19 -> author20 correction.
                        # Exact frozen row/receipt checks above still apply.
                        accepted_fixture_pair=(fixture_audit(p) and
                            (previous['attempt'],row['attempt'],saved['review_round'])==(19,20,14)
                            and previous['id']==call({'schema':PLAINTEXT_SCHEMA},'author')
                            and row['id']==sha((RUN+':run_spec_author:20').encode())
                            and accounting._accepted(store,previous))
                        require(((original_pair or fixture_pair) and not accounting._accepted(store,previous)
                            or accepted_fixture_pair) and accounting._accepted(store,row),
                            'HISTORICAL_DUPLICATE_REVISION')
                    used[saved['review_call_id']]=row
                new=binding(driver,stage,q['previous_review'],q['author'])
                if report_snapshot(p):
                    previous=used.get(new['review_call_id'])
                    require(previous is not None and previous['id']==p['fixture_reference']['accepted_author']['id']
                        and previous['attempt']==21 and accounting._accepted(store,previous),'EXACT_REPORT_FAILURE_AUTHOR')
                    fixture.failure(store,p)
                elif fixture_audit(p):
                    # Author21 answers the new genuine review15, never another
                    # response to review14. Both failed assets remain qualified.
                    require(new['review_call_id'] not in used,'NEW_REVIEW_REQUIRED')
                    fixture.failure(store,p)
                elif fixture_correction(p):
                    previous=used.get(new['review_call_id'])
                    require(previous is not None and previous['id']==p['fixture_reference']['accepted_author']['id']
                        and previous['attempt']==19 and accounting._accepted(store,previous),'EXACT_NATIVE_FAILURE_AUTHOR')
                    fixture.failure(store,p)
                elif plaintext_recovery(p):
                    previous=used.get(new['review_call_id'])
                    require(previous is not None and previous['id']==OPAQUE_AUTHOR
                        and previous['attempt']==18 and not accounting._accepted(store,previous),
                        'EXACT_UNACCEPTED_REVIEW14_RESPONSE')
                    failed_author(store,p)
                else:require(new['review_call_id'] not in used,'NEW_REVIEW_REQUIRED')
                return {'limit':q['author'],'binding':new,'failed_attempts':failures}
        result=old_inspect(store,run,stage)
        if run!=RUN or stage!='run_spec_author':return result
        value=prior.state(store)
        if value.get('phase')!=stage or value.get('reason')!=q['event']:return result
        driver=accounting.context(store,run);require(driver is not None,'AUTHOR_CONTEXT')
        ready(driver,value,p,approval)
        require(store.db.execute('SELECT count(*) FROM manual_calls').fetchone()[0]==q['count'],'AUTHOR_ONCE')
        return {**result,'limit':q['author'],'binding':binding(driver,stage,q['previous_review'],q['author'])}
    def limit(store,run,stage):
        if run!=RUN or stage!='run_spec_review':return old_limit(store,run,stage)
        value=prior.state(store)
        if value.get('phase')!=stage or value.get(q['field'])!=proof(p,approval):return old_limit(store,run,stage)
        driver=accounting.context(store,run);require(driver is not None,'REVIEW_CONTEXT')
        ready(driver,value,p,approval)
        rows=[dict(r) for r in store.db.execute('SELECT * FROM manual_calls ORDER BY rowid')]
        require(len(rows)==q['count']+1 and rows[-1]['id']==call(p,'author') and accounting._accepted(store,rows[-1])
            and json.loads(rows[-1]['receipt']).get(accounting.FIELD)==binding(driver,'run_spec_author',q['previous_review'],q['author']),'ACCEPTED_AUTHOR')
        return q['reviewer']
    accounting.review_binding=binding;accounting.inspect=inspect;recovery.role_limit=limit


def finish_review(driver,value,p,approval):
    require(not fixture_audit(p),'AUDIT_AUTHOR_ONLY_NATIVE_AND_REVIEW_HELD')
    from orchestrator.experiment_approval import verified_review_delivery
    from orchestrator.review_contract import scientific
    from orchestrator.manual_driver import write_once
    granted(driver.store,p,approval)
    q=profile(p);pending=value.get('pending') or {}
    require(value['phase']=='MODEL_RUNNING' and pending.get('id')==call(p,'review')
        and (pending.get('stage'),pending.get('round'))==('run_spec_review',q['reviewer'])
        and value['rounds']=={'run_spec_author':q['author'],'run_spec_review':q['previous_review']}
        and value.get(q['field'])==proof(p,approval),'COMPLETION_SCOPE')
    from orchestrator import author_revision_accounting as accounting
    old=scope(p,approval)
    for key in protected_keys(p):
        require(value.get(key)==old.get(key),'EXECUTION_AUTHORITY_CHANGED')
    rows=[dict(r) for r in driver.store.db.execute('SELECT * FROM manual_calls ORDER BY rowid')]
    if scoped_review(p):
        require(len(rows)==q['count']+1 and (rows[-1]['id'],rows[-1]['stage'],rows[-1]['attempt'],rows[-1]['status'])==
            (call(p,'review'),'run_spec_review',q['reviewer'],'COMPLETE'),'COMPLETED_SCOPED_REVIEW')
        frozen_author(driver,p,value);review_binding(driver,p,approval)
    else:
        require(len(rows)==q['count']+2 and [(r['id'],r['stage'],r['attempt'],r['status']) for r in rows[-2:]]==[
            (call(p,'author'),'run_spec_author',q['author'],'COMPLETE'),(call(p,'review'),'run_spec_review',q['reviewer'],'COMPLETE')],'COMPLETED_PAIR')
        require(accounting._accepted(driver.store,rows[-2]) and
            json.loads(rows[-2]['receipt']).get(accounting.FIELD)==review_binding(driver,p,approval),'AUTHOR_BINDING')
    for ident in (call(p,'author'),call(p,'review')):
        gr=driver.store.batch.db.execute('SELECT status FROM autonomy_calls WHERE id=?',(ident,)).fetchone()
        require(gr is not None and gr[0]=='COMPLETE','GLOBAL_OUTCOME')
    _,_,raw,receipt,row,submission=verified_review_delivery(driver,pending,'run_spec_review')
    decision=scientific(raw)
    candidate=executable_candidate(driver,value,p) if diagnostic(p) else None
    record={'schema':'item4-post-smoke-response-assessment/v1','verdict':decision['verdict'],
        'report_sha256':sha(raw),'call_id':call(p,'review'),'call_receipt_sha256':sha(row['receipt'].encode()),
        'submission_sha256':sha(submission),'implementation_review_sha256':approval,
        'execution_authorized':False,'full_training_admitted':False,'coverage_released':False}
    if candidate is not None:
        record.update(schema='item4-cpu-diagnostic-authoring-assessment/v1',candidate=candidate,operator_decision_sha256=DIAGNOSTIC_DECISION)
    if scoped_review(p):
        record.update(schema='item4-cpu-diagnostic-scoped-assessment/v1',
            scientific_scope='two-cpu-diagnostic-fits-only',global_findings_closed=False,
            carried_review_sha256=p['assessment']['report_sha256'],frozen_author_output_sha256=p['author_outputs'])
    if fixture_correction(p):
        record.update(scientific_scope='two-cpu-diagnostic-fits-only',global_findings_closed=False,
            corrected_fixture_executed=False,native_failure_preserved=True,
            carried_review_sha256=NATIVE_REVIEW14_REPORT)
    write_once(driver.state/q['folder']/'review.json',raw)
    write_once(driver.state/q['folder']/'assessment.json',canonical(record))
    if decision['verdict']!='APPROVE':driver.criticism('run_spec_review',q['reviewer'],raw)
    value['rounds']['run_spec_review']=q['reviewer'];value[q['result']]=record
    value.pop('pending',None)
    # Proposal acceptance is never execution admission. Existing scientific
    # findings and old execution authority stay unchanged on every verdict.
    value.update(phase='BLOCKED',reason=('CPU_DIAGNOSTIC_AUTHORING_' if diagnostic(p) else 'POST_SMOKE_RESPONSE_')+decision['verdict']+'_EXECUTION_HELD')
    driver.save(value);return driver.status()


GUIDANCE=(
    'Respond to the genuine collected-smoke REVISE11 using the original measured results and every open finding. '
    'This is an author-owned scientific proposal and its independent review, not execution admission. '
    'The current operator stage1 cap is $150 for the completed benchmark/base/resume/repeat milestone; '
    'the frozen older $75 wording is superseded by the verbatim delivered operator decision. '
    'The $1200 full-training projection gate and $1275 total remain unchanged. No new arm run or higher cap '
    'is granted here. Preserve all eight arms, five folds and the approved full research goal; do not silently '
    'narrow BACKLOG or remove safeguards. Reconcile actual timer boundaries, different checkpoint intervals, '
    'warm-up and Sprint12 workload comparability. The mechanical audit is not scientific judgment; do not '
    'subtract the whole native/returned timing difference as checkpoint-only cost or replace billed wall time '
    'with a narrower timer. Own the interpretation and identify the simplest scientifically defensible next '
    'measurement or concrete budget proposal, with uncertainties. Do not assert a plateau or impute missing '
    'arm timings. Keep coverage findings open without the required authentic sources. Preserve prior contrary '
    'evidence and avoid efficacy claims from exploratory smoke scores. The exact required author output schema '
    'and same-call submission validation remain unchanged. You may retain unchanged scientific code and use '
    'the specification to explain the proposal; any scientific change must be explicit and tested. The reviewer '
    'judges this response at its actual scope and states what remains required; no verdict from this stage '
    'closes prior obligations automatically or authorizes GPU, coverage or full training.')

DIAGNOSTIC_GUIDANCE=(
    'Implement the current operator-approved CPU-starvation A/B diagnostic as ACTUAL executable notebook/module '
    'and execution.plan.json changes, not a prose-only proposal. The exact current operator decision is supplied. '
    'Preserve every original fit, preprocessing row, environment requirement and full_training projection row '
    'unchanged, in its original order; append exactly two uniquely identified SMOKE diagnostic fits for the '
    'existing base resume arm/fold/preprocessing. Keep the pinned image and frozen development inputs. '
    'Run A is current B20016CPU/128GiB with configured nnUNet_n_proc_DA=12, about15epochs. Run B has substantially '
    'more CPU cores (baseline is already16; choose and justify more, e.g.32) and a correspondingly increased '
    'worker count, same arm/fold/scientific workload and about15epochs. Own and document the exact controlled '
    'comparison, seeds, learning-rate horizon and checkpoint cadence; avoid confounding CPU with GPU changes. '
    'Instrument actual GPU-utilization samples with timestamps and sampling completeness, requested and observed '
    'CPU capacity/quota, configured and effective training/validation workers, per-epoch native/core/synchronized '
    'and wall times, checkpoint and durable-publication overhead separately, warm-up versus any demonstrated '
    'steady state, and seconds/cost per epoch with GPU+CPU+RAM and whole-job overhead. Do not assume a plateau '
    'or subtract the whole native/returned gap as checkpoint-only. If telemetry cannot be obtained, fail the '
    'diagnostic validity visibly; never fabricate measurements. Use existing constrained runner/fit-progress '
    'interfaces and aggregate declared outputs; keep all patient, network, credential, file hash and volume '
    'protections unchanged. Supply meaningful synthetic tests for instrumentation and both diagnostic selections '
    'under the exact existing author output schema and same-call submit_author validation. The module must '
    'actually change, and unchanged51fitplan/prose alone is refused. Code need not manufacture provider pricing '
    'or future runtime hashes; use genuine bound execution records when available. '
    'Hard stops and NO automatic retry. Diagnostic actual spend plus open reservations must remain within25USD '
    'combined and existing150USD stage cap, unchanged1200 projection gate/1275 total. State hard resource/time '
    'bounds and prioritize B if the combined conservative quotes cannot both fit. Root handles normal provider '
    'admission and costing; this authoring/review stage never launches a GPU. Preserve all prior genuine REVISE '
    'findings and full eight-arm/five-fold/250epoch goal; full training and coverage arms remain held. After '
    'actual data, project complete-plan cost for cheapest configuration that performs well, explicitly separate '
    'measured A/B from inferred CPU-rich A100 comparability and Sprint12 timing differences. The scientific '
    'reviewer judges this exact supplementary diagnostic, code and tests at that bounded scope, not whole-plan '
    'acceptance. Every review outcome remains execution-held pending separate normal package/admission checks.')


RECOVERY_GUIDANCE=(
    'MECHANICAL RECOVERY: author16 completed but was not accepted. Its exact outputs are supplied as '
    'failed-author16 artifacts. Correct its duplicate top-level synthetic_tests definitions and related '
    'mechanical interface/test-contract errors while preserving the approved A/B scope. The host requires '
    'exactly one undecorated def main(input_root, output_root, contract), def synthetic_tests(), '
    'def preprocess(input_root, output_root, contract), and def validate_preprocessing(output_root, contract), '
    'with no defaults, varargs, keyword-only or positional-only parameters. Preserve meaningful tests; '
    'controller test acceptance permits no skips or expected failures. The existing author_format.submit_author '
    'tool provides same-call feedback; correct returned errors and resubmit in this invocation, then stop '
    'changing accepted files. Format acceptance is not scientific acceptance. Do not silently remove tests, '
    'diagnostic protections, scientific scope or original findings to make the interface pass. No GPU retry '
    'or execution is authorized by this author call. Every prior attempt and charge stays counted. ')

SCOPED_GUIDANCE=(
    'This is ONE independent scientific review of the unchanged accepted author17 CPU A/B diagnostic only. '
    'The exact two supplemental fit IDs and operator diagnostic25/stage150/full1200/total1275 authority are bound. '
    'Make your own judgment whether this bounded evidence-generating experiment is scientifically suitable to run. '
    'No requested verdict is implied. Inspect exact specification, executable bytes, tests, provenance, budgets and prior criticism. '
    'All review13 and earlier whole-plan findings remain verbatim OPEN in the carried original report and ordinary context; '
    'this scoped review cannot resolve, delete or approve them, nor change any execution/full/coverage hold. '
    'For EACH carried finding explain in rationale whether and why it applies to these two base-arm diagnostic fits, '
    'or is outside this decision while remaining open for the full plan. Overlapping provenance, privacy, confinement, '
    'budget, native-runtime, scientific or statistical risks belong in your findings and require REVISE or REJECT. '
    'Do not exclude a relevant finding just because it is historical. Do not treat synthetic tests as native evidence. '
    'The typed findings array decides this bounded diagnostic scope only: APPROVE requires no unresolved diagnostic findings; '
    'REVISE/REJECT must retain every applicable issue. Whole-plan findings outside this scope stay open separately, '
    'so their mere existence does not force a diagnostic finding, nor does this review claim they are resolved. '
    'Judge the scientific safety and adequacy of obtaining the missing evidence through these bounded runs; '
    'identify any genuinely necessary pre-run evidence rather than requiring the planned run to have already happened. '
    'This follows the operator evidence-generating diagnostic decision, not a general exception to independent review. '
    'Every verdict remains execution-held pending separate reviewed package/resource/reservation admission. '
    'No author revision, GPU launch, higher cap, new patient/input/image, automatic retry, full-training or coverage release is allowed. '
    'Do not offer whole-plan acceptance; retain eight arms, five folds and all original FULL rows.'
)

def guidance(p):
    if delivery_recovery(p):return fixture.SNAPSHOT_GUIDANCE.replace('Author22:', 'Author24:')+(
        ' Author23 completed but was refused because no regression method was appended to the actual module. '
        'Read the supplied refused-author23-SPEC.proposed.md, refused-author23-notebook.patch.json and refused-author23-execution.plan.json, whose exact original bytes are unaccepted reference. Preserve that plan and the report detachment correction; use the authored SPEC regression as reference and submit a conforming module yourself: '
        'append the regression method to synthetic_tests.Checks in the actual notebook patch, not only the SPEC. '
        'For THIS author24 only, notebook.patch.json may be at most96000 bytes; this supersedes generic80000-byte '
        'notebook-patch guidance. SPEC and plan remain80000 bytes, SPEC12000 characters; all other limits unchanged. '
        'The same unchanged fixture-body/additive-test AST check now runs inside submit_author so missing/mutated '
        'tests are returned as correctable errors in this call. No fabricated receipt or root-authored scientific code. '
        'Keep the exact plan, all production AST, old tests, image, data and safeguards. Native validation/scientific '
        'review remain required; no GPU or training is launched by this author-only call.')
    if report_snapshot(p):return fixture.SNAPSHOT_GUIDANCE
    if fixture_audit(p):return fixture.AUDIT_GUIDANCE
    if corrected_review(p):
        return SCOPED_GUIDANCE.replace('unchanged accepted author17','unchanged accepted author'+str(profile(p)['author'])).replace('All review13 and earlier','All review15 and earlier')+(
            ' This is review16 responding to genuine REVISE15. Read the bound diagnostic-native index and ALL ordered pages '
            'of the complete actual corrected-module CPU integration receipt, console, selection and transport proof. '
            'Assess whether that evidence closes DIAG-U2 for these two fits; an outer PASS is not sufficient. '
            'Judge real trainer hooks, workers/loader waits, telemetry thread lifecycle, cadence15/LR250/save10, '
            '2100s stop and cpu-diagnostic.json/hash closure. CPU-only durable-invalid GPU telemetry is a limitation, '
            'not GPU or production evidence. Both original failed native tests, review15 and every charge remain preserved. '
            'No requested verdict, automatic retry, scientific edit, GPU dispatch or full-plan acceptance.')
    if fixture_correction(p):return fixture.GUIDANCE
    if plaintext_recovery(p):return PLAINTEXT_GUIDANCE+NATIVE_GUIDANCE.replace(
        'its separate preserved base native harness is supplied as historical author-owned reference only, not new evidence.',
        'the supplied decoded author18 reference remains unaccepted and unexecuted.')
    if native_harness(p):return NATIVE_GUIDANCE
    if scoped_review(p):return SCOPED_GUIDANCE
    return (RECOVERY_GUIDANCE if p['schema']==RECOVERY_SCHEMA else '')+(DIAGNOSTIC_GUIDANCE if diagnostic(p) else GUIDANCE)


PLAINTEXT_GUIDANCE=(
    'This is the single bounded mechanical correction of failed author18. Its genuine format receipt and charge '
    'remain preserved, but the controller refused its base64/zlib opaque code; it was NEVER accepted. '
    'The supplied previous-native-harness.py is a byte-preserving, bounded, non-executing decode of your '
    'failed author18 reference, hash-bound to that attempt. It is read-only reference, NOT accepted science '
    'or native execution evidence. Produce compact PLAIN Python; no encoded/compressed payloads. '
    'Do not duplicate helpers unnecessarily. The existing 80000-byte output bound remains unchanged; '
    'naively expanding the entire prior payload would exceed it. You own the scientific correction. '
    'Use submit_author and correct validation errors in the SAME call before finishing. The same opaque '
    'predicate now runs in submission feedback and the complete visible module, while the host privacy '
    'check remains authoritative. Preserve the exact diagnostic plan and all invariants described below. '
)

NATIVE_GUIDANCE=(
    'Respond to the genuine diagnostic-scoped scientific REVISE14, whose exact report is delivered. '
    'It accepts the A/B diagnostic design but requires native no-patient CPU integration of the changed instrumentation. '
    'Own the scientific test harness. Preserve the complete execution.plan.json BYTE FOR BYTE, all diagnostic '
    'choices and all global/full/coverage/execution holds. Do not append more fits or change budgets/image/patients. '
    'The previous author17 module has no exported native_synthetic_integration function; its separate preserved '
    'base native harness is supplied as historical author-owned reference only, not new evidence. The existing '
    'native worker interface is also supplied. Add exactly one undecorated top-level '
    'def native_synthetic_integration(progress_factory), no defaults/varargs/keyword-only/positional-only arguments, '
    'to the extracted executable module while retaining all required main/synthetic/preprocess interfaces. '
    'Use the existing progress_factory and truthful native result contract. Preserve old base native coverage and '
    'exercise the real nnUNet/PyTorch CPU dependencies for DiagnosticTrainer hooks, live workers/loader timing, '
    'thread lifecycle, cadence15/LR250/save10, the2100s stop and cpu-diagnostic.json/hash closure as demanded by '
    'the reviewer. Generated non-patient fixtures only, pinned image, no GPU, credentials, network or patient mounts. '
    'Do not label mocked trainers/imports/telemetry as native. The reviewer permits truthful durable-invalid '
    'telemetry on a CPU-only host; never fabricate GPU samples or claim a production run. Own the smallest valid '
    'native fixture design, document precisely any reduced fixture/workload and unverified boundaries. If the '
    'requested CPU proof cannot cover a GPU-specific interface, explain it rather than inventing a simulator. '
    'Do not silently weaken production checks; any necessary scientific correction is explicit and tested. '
    'Use the required three-output author schema and same-call submit_author feedback; controller synthetic tests '
    'remain mandatory and no skips can be represented as passes. Native execution will happen later through '
    'reviewed normal reservation within diagnostic25/stage150, no automatic retry, unchanged1200gate/1275total. '
    'No paid compute or native-success claim is authorized by this author call. Reviewer15 is held until actual '
    'native evidence is supplied through its reviewed delivery route. Preserve review14 and every prior charge.'
)
NATIVE_SUPPLEMENTAL={'previous-native-harness.py','native-worker-interface.py'}
DELIVERY_SUPPLEMENTAL={'refused-author23-SPEC.proposed.md','refused-author23-notebook.patch.json','refused-author23-execution.plan.json'}
SNAPSHOT_SUPPLEMENTAL={'actual-native-worker.py','report-lifecycle-counterexample.py','report-lifecycle-counterexample-result.json'}
RECOVERY_SUPPLEMENTAL={'failed-author16-SPEC.md','failed-author16-notebook.patch.json','failed-author16-execution.plan.json'}
SUPPLEMENTAL={'current-cap-decision.txt','timing-audit.json','native-trainer.py','checkpoint-adapter.py','durable-progress.py'}


def deliver(driver,value,p,approval,supplemental):
    from orchestrator import experiment_collection as collection,private_records as pr
    ready(driver,value,p,approval)
    q=profile(p);expected_names=SUPPLEMENTAL|({'cpu-diagnostic-operator-decision.txt'} if diagnostic(p) else set())
    if p['schema']==RECOVERY_SCHEMA:expected_names|=RECOVERY_SUPPLEMENTAL
    if native_harness(p):
        expected_names|=NATIVE_SUPPLEMENTAL
        require(sha(supplemental['previous-native-harness.py'])==p['reference_native_harness_sha256'],
            'REFERENCE_NATIVE_HARNESS_CHANGED')
    if report_snapshot(p):expected_names|=SNAPSHOT_SUPPLEMENTAL
    if delivery_recovery(p):
        expected_names|=DELIVERY_SUPPLEMENTAL
        failed_delivery(driver.store,p)
        for name,pin in p['delivery_recovery']['outputs'].items():
            require(sha(supplemental['refused-author23-'+name])==pin,'DELIVERY_REFUSED_BYTES_CHANGED')
    require(set(supplemental)==expected_names,'SUPPLEMENTAL_SET')
    if p['schema']==RECOVERY_SCHEMA:
        for target,original in [('SPEC.md','SPEC.proposed.md'),('notebook.patch.json','notebook.patch.json'),('execution.plan.json','execution.plan.json')]:
            require(sha(supplemental['failed-author16-'+target])==p['failed_outputs'][original],'FAILED_DELIVERY_CHANGED')
    if diagnostic(p):
        require(sha(supplemental['cpu-diagnostic-operator-decision.txt'])==DIAGNOSTIC_DECISION,'OPERATOR_DECISION_BYTES')
    before=list(value['artifacts'])
    def add(name,raw):
        collection.artifact(driver,value,'result_tables',q['folder']+'-'+name,q['folder']+'/'+name,raw)
    raw=pr.check(driver.state/('cpu-diagnostic-fixture-correction/review.json' if corrected_review(p) or fixture_audit(p) else 'cpu-diagnostic-scoped-review/review.json' if native_harness(p) else 'cpu-diagnostic-recovery/review.json' if scoped_review(p) else 'post-smoke-response/review.json' if diagnostic(p) else 'smoke-review11/review.json')).read_bytes()
    require(sha(raw)==p['assessment']['report_sha256'],'ORIGINAL_REVIEW11')
    add('scientific-review'+str(q['previous_review'])+'.json',raw)
    add('scientific-assessment'+str(q['previous_review'])+'.json',canonical(p['assessment']))
    for name,raw in supplemental.items():add(name,raw)
    added=[r for r in value['artifacts'] if r not in before]
    expected=len(expected_names)+2
    require(len(added)==expected or (not added and len([r for r in before if r['id'].startswith(q['folder']+'-')])==expected),'DELIVERY_MEMBERS')
    driver.save(value)


def verify_delivered(driver,value,stage,work,prompt,measurement,p):
    from orchestrator import manual_context as mc,context_budget as cb,private_records as pr
    require(stage in {'run_spec_author','run_spec_review'},'DELIVERY_STAGE')
    q=profile(p);navigation=prompt
    if stage=='run_spec_review':
        indexes=[r for r in measurement['workspace_files'] if r.get('id')=='scientific-review-artifact-index']
        require(len(indexes)==1 and cb.encoded(indexes[0]) in prompt,'ARTIFACT_INDEX')
        ref=indexes[0];raw=pr.check(cb.relative_file(work,ref['path'])).read_bytes()
        require(sha(raw)==ref['sha256'] and len(raw)==ref['bytes'],'ARTIFACT_INDEX_CHANGED');navigation=raw.decode()
    role='author' if stage.endswith('author') else 'review'
    instructions=[r for r in measurement['workspace_files'] if r.get('id')=='scientific-'+role+'-instructions']
    require(len(instructions)==1 and cb.encoded(instructions[0]) in navigation,'TASK_REQUIRED')
    task=instructions[0];raw=pr.check(cb.relative_file(work,task['path'])).read_bytes()
    require(sha(raw)==task['sha256'] and len(raw)==task['bytes'] and guidance(p) in raw.decode(),'TASK_CHANGED')
    old=scope(p,'0'*64)
    retained=[r for r in old['artifacts'] if r['id'].startswith('smoke-review11-')]
    require(len(retained)==19 and all(r in value['artifacts'] for r in retained),'COLLECTED_EVIDENCE_PRESERVED')
    extra=[r for r in value['artifacts'] if r['id'].startswith(q['folder']+'-')]
    require(len(extra)==len(SUPPLEMENTAL)+2+diagnostic(p)+(len(RECOVERY_SUPPLEMENTAL) if p['schema']==RECOVERY_SCHEMA else len(NATIVE_SUPPLEMENTAL) if native_harness(p) else 0)+(len(SNAPSHOT_SUPPLEMENTAL) if report_snapshot(p) else 0)+(len(DELIVERY_SUPPLEMENTAL) if delivery_recovery(p) else 0),'DELIVERY_MEMBERS')
    if scoped_review(p):
        frozen_author(driver,p,value)
        retained+=[r for r in old['artifacts'] if r['id'].startswith('cpu-diagnostic-recovery-')]
    if diagnostic(p):
        previous=[r for r in old['artifacts'] if r['id'].startswith('post-smoke-response-')]
        require(len(previous)==len(SUPPLEMENTAL)+2 and all(r in value['artifacts'] for r in previous),'PRIOR_RESPONSE_PRESERVED')
        retained+=previous
    expected=mc.selected_artifacts(stage,value['artifacts'])
    require(all(r in expected for r in retained+extra),'REQUIRED_ARTIFACTS_SELECTED')
    for ref in expected:
        require(measurement['selected_artifacts'].count(ref)==1,'NOT_DELIVERED')
        raw=pr.check(cb.relative_file(driver.context,ref['path'])).read_bytes()
        require(sha(raw)==ref['sha256'],'SOURCE_ARTIFACT_CHANGED')
        if mc.workspace_artifact(ref['type'],artifact_id=ref['id'],private_intake=driver.config['private_intake'],reference_prior_results=True):
            matches=[r for r in measurement['workspace_files'] if r.get('id')==ref['id'] and r.get('type')==ref['type']]
            require(len(matches)==1,'WORKSPACE_ARTIFACT');item=matches[0]
            require(all(item.get(k)==ref[k] for k in ('id','type','version','sha256')) and item.get('source_path')==ref['path']
                and cb.encoded(item) in navigation,'DELIVERY_BINDING')
            require(pr.check(cb.relative_file(work,item['path'])).read_bytes()==raw,'DELIVERY_BYTES')
        else:require(cb.encoded(ref)+'\n'+raw.decode() in navigation,'INLINE_DELIVERY')
