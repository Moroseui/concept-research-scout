"""One reviewed author19 native CPU operation and evidence-gated reviewer15.

No GPU entrypoint, automatic retry, author call, or full-plan approval.
"""
from pathlib import Path
import hashlib,importlib.util,json,os,sqlite3,subprocess,sys,time
CHANGE='item4-diagnostic-native-execution-20261010'
ROOT=Path('/opt/research-system/manual-repair-helpers')/CHANGE
RECORD=Path('/var/lib/research-system-manual-sprint10-deployment')/CHANGE
CONFIG=Path('/etc/research-system-manual-sprint10')/CHANGE/'config.json'
STATE=Path('/var/lib/research-system-manual-sprint10/environment-inventory/item4-author19-diagnostic-native-v1')
BASE=Path('/opt/research-system/manual-sprint10/research-manual-sprint10-spending-a51ac44279e4')
LANE=Path('/var/lib/research-system-manual-sprint10/releases/research-manual-sprint10-timeout-continuation-8e042339/item4/lane')
LEDGER=Path('/var/lib/research-system-autonomy/reviews')
RUNTIME=Path('/etc/research-system-manual-sprint10/releases/research-manual-sprint10-timeout-continuation-8e042339/runtime.json')
CPU_UNIT='research-'+CHANGE+'-cpu.service'
REVIEW_UNIT='research-'+CHANGE+'-review.service'
PROPS={'User':'partho','Group':'partho','UMask':'0077','NoNewPrivileges':'yes','ProtectSystem':'strict',
 'PrivateTmp':'yes','ProtectHome':'read-only','RestrictSUIDSGID':'yes','LockPersonality':'yes'}
FILES=('tools/item4_diagnostic_native_runtime.py','tools/item4_diagnostic_review_runtime.py',
 'tools/install_item4_diagnostic_native.py','tools/item4_native_worker.py','tools/item4_validation_retained.py',
 'orchestrator/item4_diagnostic_native.py','orchestrator/modal_native_synthetic.py',
 'orchestrator/modal_environment_budget.py','orchestrator/modal_environment_provider.py',
 'orchestrator/modal_environment_inventory.py','orchestrator/modal_pinned_image.py',
 'docs/ITEM4_DIAGNOSTIC_NATIVE_SELECTION_PRIVATE.json','docs/ITEM4_DIAGNOSTIC_NATIVE_RETAINED_PRIVATE.json',
 'docs/ITEM4_DIAGNOSTIC_NATIVE_ACCEPTED_PRIVATE.json','docs/ITEM4_CPU_DIAGNOSTIC_OPERATOR_DECISION.txt',
 'docs/ITEM4_STAGE1_CAP_OPERATOR_DECISION_20261009.txt','docs/ITEM4_DIAGNOSTIC_REVIEW_PRIOR_UNIT_PRIVATE.txt')

def sha(raw):return hashlib.sha256(raw).hexdigest()
def require(ok,why):
    if not ok:raise ValueError('DIAGNOSTIC_NATIVE_RUNTIME_'+why)

def trusted(path):
    path=Path(path)
    for p in (path,*path.parents):
        st=p.lstat();require(not p.is_symlink() and st.st_uid==0 and not st.st_mode&0o022,'TRUSTED_SOURCE')
    return path

def authority():
    from orchestrator.autonomy_review import verify_result
    record=json.loads(trusted(RECORD/'installed.json').read_bytes())
    result=verify_result(trusted(RECORD/'review'))
    manifest=json.loads(trusted(RECORD/'review/packet-manifest.json').read_bytes())
    require(result['verdict']=='APPROVE' and result['change_id']==CHANGE
        and result['source_sha']==record['source']==manifest['source_sha']
        and result['report_sha256']==record['review_sha256']
        and result['runtime_sha256']==sha(trusted(RUNTIME).read_bytes()),'GENUINE_APPROVAL')
    require(set(record['files'])==set(FILES),'INSTALL_MEMBERS')
    for name in FILES:
        require(sha(trusted(ROOT/name).read_bytes())==record['files'][name]==manifest['source_files'][name],'SOURCE_CHANGED')
    require(Path(__file__).resolve()==ROOT/FILES[0],'EXECUTED_SOURCE')
    config=json.loads(trusted(CONFIG).read_bytes())
    require(sha(trusted(CONFIG).read_bytes())==record['config_sha256'],'CONFIG_CHANGED')
    from orchestrator import item4_diagnostic_native as d
    frozen=d.document(d.RETAINED,d.RETAINED_SHA)
    require(config==config_from_image(frozen['image_config']),'CONFIG_BINDING')
    units=rendered(config)
    require(record['units']=={name:sha(raw) for name,raw in units.items()},'UNIT_MEMBERS')
    for name,raw in units.items():require(trusted(Path('/etc/systemd/system')/name).read_bytes()==raw,'UNIT_CHANGED')
    return result

PRIOR=Path('/opt/research-system/manual-repair-helpers/item4-author18-plaintext-recovery-20261010/tools/item4_smoke_response_runtime.py')
PRIOR_SHA='8f884032ec1e1f6119e38db0de529d1b172fcc8941a4f17e554bc9d3879ab54f'
PRIOR_REVIEW='ff43deb433ca844548298b459295cd8c4db14bafb9bfcb8699d017be9e9e108b'

def verified_prior():
    require(sha(trusted(PRIOR).read_bytes())==PRIOR_SHA,'PRIOR_RUNTIME_CHANGED')
    sys.path.insert(0,'/opt/research-system/manual-sprint10/research-manual-sprint10-timeout-continuation-8e042339')
    spec=importlib.util.spec_from_file_location('_native_verified_prior',PRIOR)
    prior=importlib.util.module_from_spec(spec);spec.loader.exec_module(prior)
    approved=prior.authority()
    require(approved['source_sha']=='5b884b7c45f64957e6f8c9952529a079e4fea94f'
        and approved['report_sha256']==PRIOR_REVIEW,'PRIOR_APPROVAL')
    return prior,prior.connect()

def overlay(root):
    # Reuse the genuine installed accounting/checkpoint connections intact.
    # Replacing those modules with unconnected source copies loses their
    # independent authority callbacks and must never be papered over.
    import importlib,orchestrator,tools
    root=Path(root);orchestrator.__path__.insert(0,str(root/'orchestrator'))
    tools.__path__=[str(root/'tools'),*tools.__path__]
    names=[name[:-3].replace('/','.') for name in FILES if name.startswith('orchestrator/')]
    for name in names:
        sys.modules.pop(name,None)
        if hasattr(orchestrator,name.split('.')[-1]):delattr(orchestrator,name.split('.')[-1])
    for name in names:
        module=importlib.import_module(name)
        require(Path(module.__file__).resolve()==root/(name.replace('.','/')+'.py'),'NATIVE_IMPORT')

def bootstrap():
    verified_prior();overlay(ROOT)

def config_from_image(old):
    from orchestrator import modal_native_synthetic as n,modal_environment_inventory as inventory
    selected=n.selected()
    result={k:v for k,v in old.items() if k not in {'units','image_build'}}
    result.update(schema=n.SCHEMA,operation_id=n.OPERATION,image_id=selected['image_id'],
        state=str(STATE),worker_sha256=n.worker_sha256(),native_synthetic=selected)
    # A distinct service prevents any collision with the historical native13.
    result['units']={CPU_UNIT:{'sha256':sha(rendered(result)[CPU_UNIT])}}
    inventory.selection(result);return result

def rendered(config):
    common=f"""[Unit]
Description=Reviewed bounded diagnostic evidence
After=network-online.target
[Service]
Type=oneshot
User=partho
Group=partho
UMask=0077
WorkingDirectory={BASE}
Environment=PYTHONPATH={BASE}:{config['provider']['sdk_package']}
Environment=RESEARCH_MANUAL_RUNTIME_CONFIG={RUNTIME}
NoNewPrivileges=true
ProtectSystem=strict
ProtectHome=read-only
PrivateTmp=true
RestrictSUIDSGID=true
LockPersonality=true
"""
    cpu=common+f'ExecStart=/usr/bin/python3 -s -B {ROOT}/tools/item4_diagnostic_native_runtime.py run\nTimeoutStartSec=1200\nReadWritePaths={STATE} {LEDGER}\n'
    prior=(Path(__file__).resolve().parents[1]/'docs/ITEM4_DIAGNOSTIC_REVIEW_PRIOR_UNIT_PRIVATE.txt').read_bytes()
    require(sha(prior)=='eaebd47bd4c016e0aff1df821bbd36f309bbf8c820d6538c81154bfe8821ed2a','PRIOR_REVIEW_UNIT')
    before='ExecStart=/usr/bin/python3 -s -B /opt/research-system/manual-repair-helpers/item4-author18-plaintext-recovery-20261010/tools/item4_smoke_response_runtime.py run'
    require(prior.decode().count(before)==1,'PRIOR_REVIEW_COMMAND')
    review=prior.decode().replace(before,f'ExecStart=/usr/bin/python3 -s -B {ROOT}/tools/item4_diagnostic_review_runtime.py run')
    return {CPU_UNIT:cpu.encode(),REVIEW_UNIT:review.encode()}


def accepted(accounts,*,review=False):
    from orchestrator import item4_diagnostic_native as d,modal_native_synthetic as n,private_records as pr
    from orchestrator.modal_executor import canonical
    from orchestrator.notebook_execution import tests_passed
    frozen=d.document(d.ACCEPTED,d.ACCEPTED_SHA);selected=n.selected()
    with sqlite3.connect((LANE/'jobs.sqlite').as_uri()+'?mode=ro',uri=True) as db:
        db.row_factory=sqlite3.Row;db.execute('PRAGMA query_only=ON');db.execute('BEGIN')
        config_raw=pr.check(LANE/'lane.json').read_bytes();require(sha(config_raw)==frozen['configuration_sha256'],'LANE_CHANGED')
        value=json.loads(db.execute('SELECT payload FROM manual_state WHERE id=1').fetchone()[0])
        before=json.loads(frozen['original_state'])
        require(value['notebook_revision_result']==before['notebook_revision_result']
            and all(r in value['artifacts'] for r in before['artifacts']),'AUTHOR_ARTIFACTS_CHANGED')
        for key in before:
            if key not in {'phase','reason','pending','artifacts','rounds'}:
                require(value.get(key)==before[key],'PRIOR_AUTHORITY_CHANGED')
        if not review:
            require(value['phase']=='BLOCKED' and value['reason']=='NATIVE_HARNESS_ACCEPTED_NATIVE_EVIDENCE_REQUIRED'
                and not value.get('pending') and value['rounds']==before['rounds'],'HELD_AUTHOR_REQUIRED')
        local_ids={r[0] for r in db.execute('SELECT id FROM manual_calls')}
        review_id=sha(('experiment-a74959ac4546a982af4ae137:run_spec_review:15').encode())
        require(local_ids in ([set(frozen['local_calls']),set(frozen['local_calls'])|{review_id}] if review else [set(frozen['local_calls'])]),'UNEXPECTED_CALL')
        for ident,pin in frozen['local_calls'].items():
            row=db.execute('SELECT * FROM manual_calls WHERE id=?',(ident,)).fetchone()
            require(row is not None and sha(json.dumps(dict(row),sort_keys=True,separators=(',',':'),allow_nan=False).encode())==pin,'LOCAL_CALL_CHANGED')
        event=db.execute('SELECT payload FROM events WHERE id=?',('author-accepted:'+selected['author_call_id'],)).fetchone()
        require(event is not None and json.loads(event[0])==frozen['accepted_event'],'ACCEPTED_EVENT_CHANGED')
        receipt=json.loads(frozen['accepted_author']['receipt'])
        require(receipt['native']['author_submission']==frozen['native_format'] and
            frozen['native_format']['record_sha256']==selected['accepted_submission_sha256'],'FORMAT_CHANGED')
        for name,pin in frozen['accepted_event']['output_sha256'].items():
            require(sha(pr.check(Path(receipt['workspace'])/name).read_bytes())==pin,'AUTHOR_OUTPUT_CHANGED')
        folder=Path(value['notebook_revision_result']['folder'])
        rawtests=pr.check(folder/'synthetic/receipt.json').read_bytes();tests=json.loads(rawtests)
        require(tests['status']=='PASS' and tests['exit_code']==0 and tests_passed(tests['tests'],selected['module_sha256']),
            'CONTROLLER_TESTS')
        testref=next(r for r in value['artifacts'] if r['id']=='synthetic_tests' and r['version']==19)
        from orchestrator.context_budget import relative_file
        raw=pr.check(relative_file(json.loads(config_raw)['context'],testref['path'])).read_bytes()
        require(sha(raw)==selected['controller_receipt_sha256'] and json.loads(raw)==tests,'CONTROLLER_BINDING')
        for name,pin in selected['files'].items():
            require(sha(pr.check(folder/'synthetic/package'/name).read_bytes())==pin,'ACCEPTED_PACKAGE_CHANGED')
    for ident,pin in frozen['batch_calls'].items():
        row=accounts.db.execute('SELECT * FROM autonomy_calls WHERE id=?',(ident,)).fetchone()
        require(row is not None and sha(json.dumps(dict(row),sort_keys=True,separators=(',',':'),allow_nan=False).encode())==pin,'GLOBAL_CALL_CHANGED')
    return value

def connect_closed(accounts):
    from orchestrator import spending_continuation,item4_diagnostic_native as d
    from orchestrator.modal_executor import canonical
    prior=spending_continuation.closed_ids
    def qualified(batch,run):
        original=prior(batch,run)
        from orchestrator.modal_native_synthetic import RUN
        if run!=RUN:return original
        require(batch is accounts.batch,'CLOSED_OWNER')
        proof=d.document(d.RETAINED,d.RETAINED_SHA)
        for ident,pin in proof['closed_calls'].items():
            row=accounts.db.execute('SELECT * FROM autonomy_calls WHERE id=?',(ident,)).fetchone()
            require(row is not None and sha(canonical(dict(row)))==pin,'CLOSED_CALL_CHANGED')
        # retained_terminal replays the native original qualification in the same
        # reservation transaction; these pins cannot make an unknown row closed.
        return original|set(proof['closed_calls'])
    spending_continuation.closed_ids=qualified
    return lambda:setattr(spending_continuation,'closed_ids',prior)

def verify():
    authority()
    from orchestrator import modal_native_synthetic as n,item4_diagnostic_native as d
    n.bundle();n.arguments({'native_synthetic':n.selected()})
    raw=subprocess.check_output(['/usr/bin/python3','-s','-B',str(ROOT/'tools/item4_validation_retained.py'),
        '--diagnostic-native'],timeout=120)
    require(json.loads(raw)==d.document(d.RETAINED,d.RETAINED_SHA),'ORIGINAL_IMAGE_AND_TERMINAL_PROOFS')
    selected=n.selected();proof=json.loads(raw)['image_proof']
    require(proof['scientific_environment']==selected['environment'] and proof['scientific_acceptance'] is False,'IMAGE_PROOF')
    return json.loads(trusted(CONFIG).read_bytes())

def native_result(accounts):
    from orchestrator import private_records as pr,modal_environment_budget as budget,modal_environment_provider as provider
    from orchestrator.modal_executor import canonical
    binding=json.loads(pr.check(STATE/'binding.json').read_bytes());budget.validate_binding(binding)
    config=json.loads(trusted(CONFIG).read_bytes())
    require(binding['installed_config_sha256']==sha(trusted(CONFIG).read_bytes()) and
        all(binding[k]==config[k] for k in ('operation_id','source','image_id','base_image','worker_sha256','native_synthetic','owner_sha256')),
        'RESULT_CONFIG')
    ident=sha(canonical(binding));row=accounts.db.execute('SELECT * FROM autonomy_assets WHERE id=?',(ident,)).fetchone()
    require(row is not None and row['status']=='READY' and row['binding']==canonical(binding).decode()
        and row['run']==binding['run_id'] and row['reserved_micro_usd']==binding['envelope']['cost']['reserved_micro_usd'],'NATIVE_READY_REQUIRED')
    require((STATE/'provider/outcome.json').is_file(),'TERMINAL_NATIVE_REQUIRED')
    handle=json.loads(pr.check(STATE/'provider/sandbox.json').read_bytes())
    observed=provider.observe(None,binding,handle,STATE/'provider')
    saved=json.loads(pr.check(STATE/'VERIFIED.json').read_bytes())
    require(observed['status']=='VERIFIED' and observed['exit_code']==0 and
        json.loads(row['receipt'])==saved and all(saved[k]==v for k,v in observed.items()),'NATIVE_PASS_RECEIPT')
    return binding,saved

def main(argv=None):
    argv=list(sys.argv[1:] if argv is None else argv)
    require(argv in (['verify'],['run']) and os.getuid()==os.getgid()==1003 and sys.flags.no_user_site,'SERVICE_IDENTITY')
    bootstrap();config=verify()
    from orchestrator.autonomy_accounting import BatchAccounts
    from orchestrator.modal_budget import ComputeAccounts
    from orchestrator import private_records as pr,modal_environment_inventory as inventory,connectivity
    from orchestrator.modal_provider import ModalProvider
    batch=BatchAccounts(config['batch_ledger']);accounts=ComputeAccounts(batch);restore=connect_closed(accounts)
    try:
        accepted(accounts)
        if argv==['verify']:
            print(json.dumps({'status':'VERIFIED_HELD','model_calls':0,'provider_calls':0}));return
        props=dict(x.split('=',1) for x in subprocess.check_output(['systemctl','show',CPU_UNIT,'--property='+','.join(PROPS)],text=True).splitlines())
        require(props==PROPS,'SERVICE_RESTRICTIONS')
        # No native operation is replayed after an interrupted host start. Its
        # original records remain available to the separate read-only observer.
        with pr.open_file(STATE/'start-intent.json','xb') as stream:stream.write(b'{"no_automatic_retry":true}')
        require(not (STATE/'binding.json').exists() and not (STATE/'provider').exists(),'EXISTING_ATTEMPT_RECONCILE')
        connectivity.require(['modal'],STATE/'connectivity.json');provider=ModalProvider(config['provider'])
        host={'status':'PASS','source':config['source'],'installation_sha256':config['installation_sha256'],
            'config_sha256':sha(trusted(CONFIG).read_bytes())}
        deadline=time.monotonic()+1020
        while True:
            result=inventory.tick(config,provider,accounts,host_proof=host);pr.atomic(STATE/'STATUS.json',result)
            if result['status']!='RUNNING' or time.monotonic()>=deadline:break
            time.sleep(10)
        print(json.dumps({k:v for k,v in result.items() if k in {'status','no_automatic_retry','scientific_calls'}}))
        if result['status']!='VERIFIED':raise SystemExit(1)
    finally:restore();batch.db.close()

if __name__=='__main__':
    os.umask(0o077);main()
