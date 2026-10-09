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
        native.author_and_image(accounts)
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
