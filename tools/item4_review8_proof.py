"""Read-only authentication of the two real prerequisites for scientific review8.

Run in an isolated interpreter before model admission: installed native/source
helpers retain their original import identities and never share the science
process namespace. This verifier has no provider client or ledger writer.
"""
from pathlib import Path
from types import SimpleNamespace as NS
from datetime import datetime,timezone
import hashlib,importlib.util,json,os,sqlite3,subprocess

SOURCE_ROOT=Path('/opt/research-system/manual-repair-helpers/item4-source-hydration-retry-20261009')
SOURCE='28726e3d5cdf32f1d80c63187f5abd9146cbfcd0'
REVIEW='fd7c8b60ac7e11981733794ec8e57797c009a27164474395a85398b381da364e'
ASSET='9878e7923ea81dceefce162166a113aa7d0a53dd65c4199a42b4276fe952d365'
LEDGER=Path('/var/lib/research-system-autonomy/reviews/jobs.sqlite')

def require(ok,why):
    if not ok:raise ValueError('REVIEW8_PROOF_'+why)

def sha(raw):return hashlib.sha256(raw).hexdigest()

def terminal(text):
    props=dict(x.split('=',1) for x in text.splitlines())
    require(props=={'ActiveState':'inactive','MainPID':'0','ExecMainStatus':'0','ControlGroup':''},'SOURCE_NOT_COMPLETE')

def source_receipt(binding,ident,row,saved,local,handle,membership,inventory,canonical,now):
    require(ident==ASSET and binding['helper_source']==SOURCE,'SOURCE_BINDING')
    require(row['status']=='READY' and json.loads(row['receipt'])==saved,'SOURCE_NOT_READY')
    require(saved=={'status':'VERIFIED','binding_sha256':ident,
        'source_volume_id':binding['source_volume_id'],'volume_id':handle['volume_id'],
        'inventory_sha256':inventory,'membership':membership,
        'reserved_micro_usd':binding['envelope']['reserved_micro_usd'],
        'expires_at':binding['expires_at'],'scientific_approval':False,'patient_analysis':False,
        'new_provider_compute':False,'originals_preserved':True,'completed_at':saved['completed_at']},'SOURCE_RECEIPT')
    require(local=={'binding_sha256':ident,**membership},'LOCAL_RECEIPT')
    require(handle=={'binding_sha256':ident,'name':'research-item4-base-source-'+ident[:24],
        'volume_id':saved['volume_id'],'version':2} and saved['volume_id']!=binding['source_volume_id'], 'VOLUME_BINDING')
    import re
    require(re.fullmatch('vo-[A-Za-z0-9]+',saved['volume_id']) is not None,'VOLUME_ID')
    require(datetime.fromisoformat(binding['created_at'])<=datetime.fromisoformat(saved['completed_at'])<=now
        <datetime.fromisoformat(binding['expires_at']),'SOURCE_EXPIRED_OR_TIME')
    require(binding['inventory_sha256']==inventory and sha(canonical(binding))==ident,'INVENTORY_BINDING')

def historical_author_and_image(accounts,native,frozen):
    """Authenticate author13 as history, without lying about the current lane phase."""
    from orchestrator import modal_native_synthetic as n,modal_pinned_image as image,private_records as pr
    from orchestrator.modal_executor import canonical
    selection=n.selected();historical=frozen['historical_science']
    require((frozen['author_attempt'],frozen['review_attempt'])==(14,10)
        and len(frozen['local_calls'])==len(frozen['global_calls'])==22
        and set(frozen['local_calls'])==set(frozen['global_calls']),'HISTORICAL_SCOPE')
    def compact(v):return json.dumps(v,sort_keys=True,separators=(',',':')).encode()
    require(sha(pr.check(native.LANE/'lane.json').read_bytes())==frozen['configuration_sha256'],'HISTORICAL_CONFIG')
    with sqlite3.connect((native.LANE/'jobs.sqlite').as_uri()+'?mode=ro',uri=True) as db:
        db.row_factory=sqlite3.Row
        for connection,table,key in [(db,'manual_calls','local_calls'),(accounts.db,'autonomy_calls','global_calls')]:
            for ident,pin in frozen[key].items():
                row=connection.execute('SELECT * FROM '+table+' WHERE id=?',(ident,)).fetchone()
                require(row is not None and sha(compact(dict(row)))==pin,'HISTORICAL_ORIGINAL_CHANGED')
        row=db.execute('SELECT * FROM manual_calls WHERE id=?',(selection['author_call_id'],)).fetchone()
        require(row is not None and row['status']=='COMPLETE' and row['stage']=='run_spec_author'
            and row['attempt']==selection['author_attempt']==13,'HISTORICAL_AUTHOR')
        accepted=json.loads(row['receipt'])['native']['author_submission']
        require(accepted['status']=='ACCEPTED' and accepted['record_sha256']==selection['accepted_submission_sha256'],
            'HISTORICAL_SUBMISSION')
    row=accounts.db.execute('SELECT status FROM autonomy_calls WHERE id=?',(selection['author_call_id'],)).fetchone()
    require(row is not None and row[0]=='COMPLETE','HISTORICAL_GLOBAL_AUTHOR')
    folder=native.LANE/'notebook-revisions/author-13';result=historical['notebook_revision_result']
    require(result['folder']==str(folder) and result['synthetic_status']=='PASS'
        and result['tests_sha256']==selection['controller_receipt_sha256'],'HISTORICAL_CONTROLLER')
    notebook=pr.check(folder/'revised.ipynb').read_bytes()
    require(sha(notebook)==result['notebook_sha256'],'HISTORICAL_NOTEBOOK')
    receipt=json.loads(pr.check(folder/'synthetic/receipt.json').read_bytes())
    require(sha(compact(receipt))==selection['controller_receipt_sha256'] and receipt['status']=='PASS'
        and receipt['exit_code']==0,'HISTORICAL_TEST_RECEIPT')
    require(historical['native_files']==selection['files'] and
        historical['controller_environment']==receipt['binding']['environment'] and
        historical['execution_sha256']==selection['files']['execution.py'],'HISTORICAL_NATIVE_BINDING')
    for name,pin in selection['files'].items():
        require(not Path(name).is_absolute() and '..' not in Path(name).parts,'HISTORICAL_FILE_PATH')
        require(receipt['binding']['files'].get(name)==pin
            and sha(pr.check(folder/'synthetic/package'/name).read_bytes())==pin,'HISTORICAL_PACKAGE')
    for name,pin in receipt['preserved_files'].items():
        require(not Path(name).is_absolute() and '..' not in Path(name).parts,'HISTORICAL_TEST_PATH')
        require(sha(pr.check(folder/'synthetic'/name).read_bytes())==pin,'HISTORICAL_TEST_CHANGED')
    for ident,pin in [('notebook_source',result['notebook_sha256']),('synthetic_tests',result['tests_sha256'])]:
        require(any(a['id']==ident and a['version']==13 and a['sha256']==pin for a in historical['artifacts']),
            'HISTORICAL_ARTIFACT')
    binding=json.loads(pr.check(native.IMAGE_STATE/'binding.json').read_bytes())
    proof=image.consumer_proof(accounts,binding,native.IMAGE_STATE)
    require(proof['scientific_environment']==selection['environment'] and proof['scientific_acceptance'] is False,
        'HISTORICAL_IMAGE_PROVENANCE')
    return proof


def verify():
    require(os.getuid()==os.getgid()==1003,'SERVICE_OWNER')
    p=SOURCE_ROOT/'tools/item4_source_preparation.py'
    spec=importlib.util.spec_from_file_location('_review8_source',p)
    h=importlib.util.module_from_spec(spec);spec.loader.exec_module(h)
    native,config_native,config,record=h.verify()
    require(record['source']==SOURCE and record['review_sha256']==REVIEW,'INSTALLED_SOURCE')
    from orchestrator import modal_source_budget as budget,modal_source_composition as source,private_records as pr
    from orchestrator.modal_executor import canonical
    terminal(subprocess.check_output(['systemctl','show',h.UNIT,
        '--property=ActiveState,MainPID,ExecMainStatus,ControlGroup'],text=True))
    def raw(path):return pr.check(path).read_bytes()
    def read(path):return json.loads(raw(path))
    with sqlite3.connect(LEDGER.as_uri()+'?mode=ro',uri=True) as db:
        db.row_factory=sqlite3.Row
        accounts=NS(db=db,batch=NS(db=db,folder=LEDGER.parent,filesystem_root=Path('/')))
        require(not db.execute("SELECT 1 FROM autonomy_calls WHERE status='RUNNING'").fetchone(),'MODEL_RUNNING')
        binding,ident,row=h.retained(accounts,config)
        _,membership=source.contract(h.METADATA)
        saved=read(h.STATE/'VERIFIED.json');local=read(h.STATE/'LOCAL_VERIFIED.json');handle=read(h.STATE/'volume.json')
        source_receipt(binding,ident,row,saved,local,handle,membership,source.INVENTORY,canonical,datetime.now(timezone.utc))
        require(not (h.STATE/'FAILED.json').exists(),'SOURCE_FAILED')
        require(read(h.STATE/'direct-before.json')=={'status':'VERIFIED',
            'source_volume_id':budget.DIRECT_VOLUME,'binding_sha256':budget.DIRECT_ID},'DIRECT_PROOF')
        budget.native_qualification(accounts,binding)
        from orchestrator.manual_host_guard import trusted
        frozen=json.loads(trusted(Path(__file__).resolve().parents[1]/'docs/ITEM4_REVIEW9_CONTINUATION.json').read_bytes())
        historical_author_and_image(accounts,native,frozen)
        paths={
            'SOURCE_BINDING.json':h.STATE/'binding.json',
            'SOURCE_VERIFIED.json':h.STATE/'VERIFIED.json',
            'SOURCE_LOCAL_VERIFIED.json':h.STATE/'LOCAL_VERIFIED.json',
            'SOURCE_VOLUME.json':h.STATE/'volume.json',
            'NATIVE_OUTPUT.json':budget.NATIVE_STATE/'provider/stdout.bin',
            'NATIVE_VERIFIED.json':budget.NATIVE_STATE/'VERIFIED.json',
            'NATIVE_BINDING.json':budget.NATIVE_STATE/'binding.json',
            'NATIVE_TERMINAL.json':budget.NATIVE_STATE/'provider/terminal.json'}
        originals={name:raw(path) for name,path in paths.items()}
        files={name:{'sha256':sha(body),'bytes':len(body)} for name,body in originals.items()}
        return {'schema':'item4-review8-prerequisites/v1','source_asset':ident,'native_asset':budget.NATIVE_ID,
            'source_release':SOURCE,'source_review':REVIEW,'files':files,
            'scientific_approval':False,'model_calls':0,'provider_calls':0,'ledger_changes':False}

if __name__=='__main__':print(json.dumps(verify(),sort_keys=True))
