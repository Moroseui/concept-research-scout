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

if __name__=='__main__':
    if sys.argv[1:] not in ([],['--diagnostic-native']):raise ValueError('VALIDATION_TERMINAL_ARGUMENTS')
    print(json.dumps(qualify(diagnostic=bool(sys.argv[1:])),sort_keys=True))
