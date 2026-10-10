"""Replay already-reviewed terminal qualifications in an isolated read-only process.

No provider, credential, reservation, status update or failure reclassification.
Isolation preserves the independently reviewed releases' exact import identities.
"""
from pathlib import Path
import hashlib,importlib.util,json,os,sqlite3,sys
from types import SimpleNamespace
ROOT=Path('/opt/research-system/manual-repair-helpers/item4-source-hydration-retry-20261009')
HELPER_SHA='212e7161d7f42cb8d18c297cfee1f1c291a1c4281ed2e1e5e3a2d6c3964264fd'
SOURCE='28726e3d5cdf32f1d80c63187f5abd9146cbfcd0'
SOURCE_ASSET='9878e7923ea81dceefce162166a113aa7d0a53dd65c4199a42b4276fe952d365'
LEDGER=Path('/var/lib/research-system-autonomy/reviews')

def qualify(*, diagnostic=False):
    if os.getuid()!=1003 or os.getgid()!=1003 or not sys.flags.no_user_site:
        raise ValueError('VALIDATION_TERMINAL_SERVICE_IDENTITY')
    path=ROOT/'tools/item4_source_preparation.py'
    # Every ancestor and this root-owned original must be non-writable by the
    # service account, before its independently reviewed verifier is executed.
    for p in (path,*path.parents):
        st=p.lstat()
        if p.is_symlink() or st.st_uid!=0 or st.st_mode & 0o022:
            raise ValueError('VALIDATION_TERMINAL_HELPER_TRUST')
    if hashlib.sha256(path.read_bytes()).hexdigest()!=HELPER_SHA:
        raise ValueError('VALIDATION_TERMINAL_HELPER_CHANGED')
    spec=importlib.util.spec_from_file_location('_validation_source_original',path)
    helper=importlib.util.module_from_spec(spec);spec.loader.exec_module(helper)
    native,_,config,release=helper.verify()
    if release['source']!=SOURCE or Path(config['batch_ledger'])!=LEDGER:
        raise ValueError('VALIDATION_TERMINAL_RELEASE')
    from orchestrator import modal_source_budget as budget
    from orchestrator.modal_executor import canonical
    with sqlite3.connect((LEDGER/'jobs.sqlite').as_uri()+'?mode=ro',uri=True) as db:
        db.row_factory=sqlite3.Row;db.execute('PRAGMA query_only=ON');db.execute('BEGIN')
        batch=SimpleNamespace(db=db,folder=LEDGER,filesystem_root=Path('/'))
        accounts=SimpleNamespace(db=db,batch=batch)
        binding,ident,row=helper.retained(accounts,config)
        if ident!=SOURCE_ASSET or row['status']!='READY':
            raise ValueError('VALIDATION_TERMINAL_SOURCE_NOT_READY')
        assets=set(budget.native_qualification(accounts,binding))|{budget.source_predecessor(accounts,binding)}
        compute=native.image_helper().stopped_item6(accounts)
        def pins(table,ids):
            result={}
            for ident in sorted(ids):
                row=db.execute('SELECT * FROM '+table+' WHERE id=?',(ident,)).fetchone()
                if row is None:raise ValueError('VALIDATION_TERMINAL_ROW_MISSING')
                result[ident]=hashlib.sha256(canonical(dict(row))).hexdigest()
            return result
        result = {'schema':'item4-retained-terminal-qualification/v1',
            'source_sha':release['source'],'source_asset':SOURCE_ASSET,
            'assets':pins('autonomy_assets',assets),'compute':pins('autonomy_compute',compute)}
        if diagnostic:
            # Native13 was authenticated above through its original provider receipt.
            result['native_ready']=pins('autonomy_assets',{budget.NATIVE_ID})
            from orchestrator import spending_continuation,modal_pinned_image as image
            from orchestrator import private_records as pr
            image_helper=native.image_helper()
            result['image_config']=image_helper.verify()
            image_binding=json.loads(pr.check(native.IMAGE_STATE/'binding.json').read_bytes())
            result['image_proof']=image.consumer_proof(accounts,image_binding,native.IMAGE_STATE)
            closed=image_helper.qualified_closed(spending_continuation.closed_ids,batch,budget.RUN)
            result['closed_calls']=pins('autonomy_calls',closed)
            result['native_rows']={i:dict(db.execute('SELECT * FROM autonomy_assets WHERE id=?',(i,)).fetchone())
                for i in sorted({budget.NATIVE_ID,*assets}-{budget.SOURCE_PREDECESSOR_ID})}
        return result

def qualify_diagnostic_failure(*,corrected=False,audited=False,snapshot=False):
    """Qualify the preserved FAIL as FAIL; never create, poll, retry or release."""
    if os.getuid()!=1003 or os.getgid()!=1003 or not sys.flags.no_user_site:
        raise ValueError('DIAGNOSTIC_FAILURE_SERVICE_IDENTITY')
    if any(type(x) is not bool for x in (corrected,audited,snapshot)) or sum((corrected,audited,snapshot))>1:
        raise ValueError('DIAGNOSTIC_FAILURE_SELECTOR')
    selected_proof=(
        ('item4-progress-scope-repair-20261010',
         '2da17c4507f26e64b60131767974943077282968419ca3466538a692e6a2ed89',
         '9b568290e809ae897a54eab4a126c37a6ecadef7',
         '10129ee9f765ed5a88dfd7ff8524857e67a335d4960db451b0628dc238898ece',
         '1e5bb3d0f1f807a99039e106cba34a40e9400dd01aae16c1f3e7212165d91d49',
         '561cf376482041dcd4fe093388e83858be97f5dcedcccdd0e9d5ab84ed41efd0',
         'PrerequisiteError: E173\n') if snapshot else
        ('item4-audited-native-verification-20261010',
         'e3c0ceb164bb9f28c4a9038463ca9510792e5b65c4ef7c412a9609311c721048',
         'ea529258841dd75608ec9834bcc21c34e39aaa81',
         '4fba65d315c552192d8230af33a1b889021dd092b9067beb703c19e2b8ece22a',
         '81e4dd6571ee65c4b0f7b6a6ff9c8732c66d15bee2f6738b8c0336c4b81398cf',
         '35523bcdda31ea115b9038e734dcc85749655c2859b666b0e7a0eb17c7f3e891',
         'ValueError: NATIVE_REHEARSAL_PROGRESS_SCOPE\n') if audited else
        ('item4-corrected-native-verification-20261010',
         '19cc5b660dbd252bca4cfade6087656687c7c70e4f8ad9b648ce7912a1f4e414',
         'b60badd65283e7df5f801a6a6a20b3fd63504544',
         '35aeaa0a9d6836f4caa5bf7033434b43952bb242777d4376a91259eee0ba5bb9',
         '8c40fe36f279a1bab97dab6b2c59bf8f45d7e2901f508f36c1dac0f0a2c01653',
         '8877b8d5e93b4ded054ad8cf85f54b9faf58050739493080f8acfda6e83a7a0d',
         "AttributeError: 'CPUObserver' object has no attribute '_sampling_loop'\n") if corrected else
        ('item4-diagnostic-native-execution-20261010',
         '1f8b8d34dea50a31faa208022886b2a68fdda526882ee9320817b5eabc6125f7',
         '81cd8225365a26944128ab5eb3fceda9e36d5f3d',
         'b5dfa4bf3c7d3bb45733dd7bffcf8aa5a4344cfc99a16dbdb7468e292f28679a',
         '27146f38f1722579ed096a880f59cc607bc36e993fe57634b6ffe271ae92c157',
         '2c2916dbc751fd2d3ce8835b0ec6e687b342905b88bc4f158b2862b4138d5aa5',
         "KeyError: 'continue_training'\n"))
    name,runtime_pin,source,report,asset_pin,stdout_pin,error_suffix=selected_proof
    root=Path('/opt/research-system/manual-repair-helpers')/name
    path=root/'tools/item4_diagnostic_native_runtime.py'
    for p in (path,*path.parents):
        st=p.lstat()
        if p.is_symlink() or st.st_uid!=0 or st.st_mode&0o022:raise ValueError('DIAGNOSTIC_FAILURE_SOURCE_TRUST')
    if hashlib.sha256(path.read_bytes()).hexdigest()!=runtime_pin:
        raise ValueError('DIAGNOSTIC_FAILURE_RUNTIME_CHANGED')
    spec=importlib.util.spec_from_file_location('_failed_native_original',path)
    native=importlib.util.module_from_spec(spec);spec.loader.exec_module(native)
    native.bootstrap();approval=native.authority()
    native.require(approval['source_sha']==source and approval['report_sha256']==report,'FAILURE_AUTHORITY')
    from orchestrator import private_records as pr,modal_environment_budget as budget,modal_environment_provider as provider
    from orchestrator import modal_native_synthetic as n
    from orchestrator.modal_executor import canonical
    from orchestrator.review_contract import strict_json
    binding=strict_json(pr.check(native.STATE/'binding.json').read_bytes());budget.validate_binding(binding)
    config=strict_json(native.trusted(native.CONFIG).read_bytes())
    native.require(binding['installed_config_sha256']==native.sha(native.trusted(native.CONFIG).read_bytes()) and
        all(binding[k]==config[k] for k in ('operation_id','source','image_id','base_image','worker_sha256','native_synthetic','owner_sha256')),
        'FAILURE_CONFIG')
    ident=native.sha(canonical(binding))
    native.require(ident==asset_pin,'FAILED_ASSET')
    with sqlite3.connect((LEDGER/'jobs.sqlite').as_uri()+'?mode=ro',uri=True) as db:
        db.row_factory=sqlite3.Row;db.execute('PRAGMA query_only=ON')
        row=db.execute('SELECT * FROM autonomy_assets WHERE id=?',(ident,)).fetchone()
        native.require(row is not None and row['status']=='UNCERTAIN' and row['binding']==canonical(binding).decode()
            and row['run']==binding['run_id'] and row['reserved_micro_usd']==1118950,'FAILURE_RESERVATION')
    root=native.STATE/'provider'
    native.require((root/'outcome.json').is_file() and (root/'terminal.json').is_file(),'SAVED_TERMINAL_REQUIRED')
    handle=strict_json(pr.check(root/'sandbox.json').read_bytes())
    outcome=provider.observe(None,binding,handle,root) # Existing terminal branch only; no SDK or credentials.
    native.require(outcome['status']=='UNCERTAIN' and outcome['exit_code']==1 and outcome['no_automatic_retry'] is True,
        'ACTUAL_FAILURE_REQUIRED')
    for meta in outcome['streams'].values():
        native.require(meta['truncated'] is False and meta['read_error'] is None,'COMPLETE_FAILURE_STREAMS')
    n.verify_stdin(binding,root)
    raw=pr.check(root/'stdout.bin').read_bytes()
    native.require(native.sha(raw)==stdout_pin
        and pr.check(root/'stderr.bin').read_bytes()==b'','EXACT_ORIGINAL_FAILURE')
    v=strict_json(raw);selected=n.selected(binding['native_synthetic'])
    native.require(v['schema']=='item4-native-rehearsal-result/v1' and v['status']=='FAIL' and v['native'] is None
        and v['operation_sha256']==ident and v['selection_sha256']==native.sha(canonical(selected))
        and all(v[k]==selected[k] for k in ('module_sha256','code_bundle_sha256','image_id','author_call_id'))
        and v['package_unchanged'] is True and v['observed_environment']==selected['environment']['expected']
        and all(v[k] is False for k in ('console_truncated','patient_data','network_permission','gpu','scientific_approval'))
        and native.sha(v['console'].encode())==v['console_sha256'] and v['durability_scope']==n.worker.DURABILITY_SCOPE
        and v['failure'].endswith(error_suffix),'BOUND_FAILURE_RESULT')
    import subprocess
    props=dict(line.split('=',1) for line in subprocess.check_output(['systemctl','show',native.CPU_UNIT,
        '--property=ActiveState,MainPID,ExecMainStatus'],text=True).splitlines())
    native.require(props.get('ActiveState') in {'inactive','failed'} and props.get('MainPID')=='0'
        and props.get('ExecMainStatus')=='1','FAILED_SERVICE_TERMINAL')
    return {'source':source,'implementation_review_sha256':report,'asset_id':ident,
        'module_sha256':selected['module_sha256'],'exit_code':1,'status':'FAIL','package_unchanged':True,
        'scientific_acceptance':False,'no_automatic_retry':True}

if __name__=='__main__':
    if sys.argv[1:] not in ([],['--diagnostic-native'],['--diagnostic-failure'],['--diagnostic-audit-failure'],['--diagnostic-progress-failure'],['--diagnostic-report-failure']):raise ValueError('VALIDATION_TERMINAL_ARGUMENTS')
    result=(qualify_diagnostic_failure(snapshot=True) if sys.argv[1:]==['--diagnostic-report-failure'] else qualify_diagnostic_failure(audited=True) if sys.argv[1:]==['--diagnostic-progress-failure'] else
        qualify_diagnostic_failure(corrected=True) if sys.argv[1:]==['--diagnostic-audit-failure'] else
        qualify_diagnostic_failure() if sys.argv[1:]==['--diagnostic-failure'] else qualify(diagnostic=bool(sys.argv[1:])))
    print(json.dumps(result,sort_keys=True))
