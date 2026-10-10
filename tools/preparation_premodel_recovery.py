"""Exact call54 pre-model reconciliation; no launch, reset or general exception."""
import base64,hashlib,json,os,sqlite3,stat,subprocess
from pathlib import Path
from orchestrator import private_records
ID='e41d3d88958bef07e8cf854cb65125ba496b5537f42d26206ae1cee2df9e0e67'
CHANGE='preparation-branch-admission-repair-20261010'
DOC='docs/PREPARATION_B_PREMODEL_PRIVATE.json'
DOC_SHA='8653f2108b7887b6336e50e8cf6497754444a82ede53f71432a6acf5555cf861'
SOURCE='304cae4aa12d53eb99254499950eec4e71df8075'
LANE=Path('/var/lib/research-system-manual-sprint10-deployment/parallel-analysis-20261010/lane')
COLAB=Path('/var/lib/research-system-manual-sprint10-deployment/colab-preparation-20261010')
LEDGER=Path('/var/lib/research-system-autonomy/reviews')
RECORD=LANE/'premodel-reconciliation-20261010'
BRANCH='astra/manual-preparation-aggregate-analysis-20261010'
COLAB_BRANCH='astra/manual-preparation-colab-preparation-20261010'
def require(ok,why):
    if not ok:raise ValueError('PREPARATION_PREMODEL_'+why)
def canonical(v):return json.dumps(v,sort_keys=True).encode()
def sha(raw):return hashlib.sha256(raw).hexdigest()
def binding():
    raw=(Path(__file__).resolve().parents[1]/DOC).read_bytes();require(sha(raw)==DOC_SHA,'DOCUMENT_CHANGED');return json.loads(raw)
def raw_file(path):
    from orchestrator import private_records
    return private_records.check(Path(path)).read_bytes()
def mapped(path,root):
    from tools.deploy_manual_lane import bound
    return bound(Path(root),str(path))
def one(db,sql,args=()):
    row=db.execute(sql,args).fetchone();return dict(row) if row else None
def read_local(root=Path('/')):
    path=mapped(LANE/'jobs.sqlite',root);db=sqlite3.connect(path.resolve().as_uri()+'?mode=ro',uri=True);db.row_factory=sqlite3.Row;return db
def unit_state():
    unit=binding()['unit']['name'];raw=subprocess.check_output(['systemctl','show',unit,'-p','ActiveState','-p','SubState','-p','MainPID'],text=True)
    values=dict(line.split('=',1) for line in raw.splitlines() if '=' in line)
    require(values=={'MainPID':'0','ActiveState':'inactive','SubState':'dead'},'ORIGINAL_SERVICE_NOT_HELD');return values

def verify_original(global_row,local_row,config_raw,state_row,account_row,workspace_hashes,source_hashes):
    b=binding();o=b['original']
    require(global_row==o['global_call'] and local_row==o['local_call'],'ORIGINAL_CALL_CHANGED')
    require(state_row==o['manual_state'] and account_row==o['manual_account'],'ORIGINAL_STATE_ACCOUNT_CHANGED')
    require(sha(config_raw)==b['config']['sha256'],'ORIGINAL_CONFIG_CHANGED')
    require(workspace_hashes=={n:r['sha256'] for n,r in b['workspace'].items()},'ORIGINAL_WORKSPACE_CHANGED')
    require(source_hashes=={n:r['sha256'] for n,r in b['source_files'].items()},'ORIGINAL_SOURCE_CHANGED')
    receipt=json.loads(local_row['receipt']);state=json.loads(state_row['payload']);config=json.loads(config_raw)
    require(global_row['status']=='RUNNING' and global_row['receipt'] is None and local_row['status']=='BLOCKED_BEFORE_MODEL','EXACT_UNFINISHED_RESERVATION')
    require(receipt['transport_preflight']['model_client_launched'] is False and state['phase']=='BLOCKED'
        and state['reason']=='ValueError: MANUAL_ACCOUNTING_BINDING' and not state.get('pending'),'EXACT_PREMODEL_CAUSE')
    require(config['branch']==o['git_branch'] and config['source']==SOURCE,'ORIGINAL_BRANCH_SOURCE')
    require(json.loads(account_row['payload'])['count']==0,'NO_FABRICATED_LOCAL_ADMISSION')
    return {'id':ID,'classification':'EXACT_PREMODEL_BRANCH_REFUSAL_ADMIN_ONLY','model_client_launched':False,'proof_sha256':DOC_SHA}

def verify_workspace_tree(work):
    """Exact pre-reservation input tree, including its measured evidence copies."""
    expected=binding()['workspace_tree'];actual={}
    for path in Path(work).rglob('*'):
        private_records.check(path);s=path.lstat();name=str(path.relative_to(work))
        require(name in expected,'WORKSPACE_MEMBERSHIP')
        item={'kind':'directory' if stat.S_ISDIR(s.st_mode) else 'file','uid':s.st_uid,'gid':s.st_gid,'mode':stat.S_IMODE(s.st_mode),'links':s.st_nlink}
        if item['kind']=='file':
            raw=raw_file(path);item.update(sha256=sha(raw),bytes=len(raw))
        actual[name]=item
    require(actual==expected,'WORKSPACE_MEMBERSHIP')
    return sha(canonical(actual))

def administrative_exception(db,*,filesystem_root=Path('/'),check_unit=unit_state):
    """Read-only exact proof for a bounded repair review; original RUNNING stays."""
    require(os.getuid()==os.getgid()==1003,'SERVICE_OWNER');b=binding();root=Path(filesystem_root)
    row=one(db,'SELECT * FROM autonomy_calls WHERE id=?',(ID,));local=read_local(root)
    try:
        work=mapped(Path(next(iter(b['workspace'].values()))['path']).parent,root)
        verify_workspace_tree(work)
        proof=verify_original(row,one(local,'SELECT * FROM manual_calls WHERE id=?',(ID,)),raw_file(mapped(LANE/'lane.json',root)),
            one(local,'SELECT * FROM manual_state WHERE id=1'),one(local,'SELECT * FROM manual_account WHERE id=1'),
            {n:sha(raw_file(mapped(z['path'],root))) for n,z in b['workspace'].items()},
            {n:sha(raw_file(mapped(z['path'],root))) for n,z in b['source_files'].items()})
        require(one(db,'SELECT * FROM jobs WHERE id=?',(ID,))==b['original']['global_job'],'ORIGINAL_GLOBAL_JOB')
        require(raw_file(mapped(b['owner']['path'],root))==base64.b64decode(b['owner']['base64']),'ORIGINAL_OWNER')
        check_unit();return proof
    finally:local.close()

def approval(review_folder):
    from orchestrator.autonomy_review import verify_result
    value=verify_result(review_folder);manifest=json.loads(raw_file(Path(review_folder)/'packet-manifest.json'))
    require(value['verdict']=='APPROVE' and value['change_id']==CHANGE,'GENUINE_REPAIR_APPROVAL')
    for name in ['tools/preparation_premodel_recovery.py',DOC]:
        require(manifest['source_files'].get(name)==sha((Path(__file__).resolve().parents[1]/name).read_bytes()),'REVIEWED_REPAIR_BYTES')
    return value

def make_receipt(report_sha):
    b=binding();r=json.loads(b['original']['local_call']['receipt'])
    return {**r,'id':ID,'outcome':'FAILED_BEFORE_MODEL','reason':'MANUAL_ACCOUNTING_BINDING','model_client_launched':False,
        'accounting_units':1,'original_global_row_sha256':sha(canonical(b['original']['global_call'])),
        'original_local_row_sha256':sha(canonical(b['original']['local_call'])),'reconciliation':{'proof_sha256':DOC_SHA,
        'review_sha256':report_sha,'original_local_status':'BLOCKED_BEFORE_MODEL','original_local_account_count':0,
        'reserved_call_remains_counted':True,'local_admission_was_not_completed':True}}

def new_config():
    value=json.loads(base64.b64decode(binding()['config']['base64']));value['branch']=BRANCH;return value

def completion(report_sha):
    return {'schema':'exact-premodel-reconciliation/v1','id':ID,'status':'RECONCILED_FAILED_NOT_COMPLETE',
        'proof_sha256':DOC_SHA,'review_sha256':report_sha,'receipt_sha256':sha(canonical(make_receipt(report_sha))),
        'original_local_row_sha256':sha(canonical(binding()['original']['local_call'])),
        'original_account_sha256':sha(canonical(binding()['original']['manual_account'])),
        'branch':BRANCH,'colab_branch':COLAB_BRANCH,'config_sha256':sha(canonical(new_config())),
        'original_call_retained':True,'model_calls':0}

class Proof:
    def __init__(self,review_folder,*,filesystem_root=Path('/')):
        self.root=Path(filesystem_root);self.review_folder=Path(review_folder);self.review=approval(review_folder)
        self.expected=completion(self.review['report_sha256']);self.verify_record()
    def verify_record(self):
        require(json.loads(raw_file(mapped(RECORD/'COMPLETE.json',self.root)))==self.expected,'COMPLETED_RECONCILIATION_REQUIRED')
        require(json.loads(raw_file(mapped(RECORD/'original-rows.json',self.root)))==binding()['original'],'PRESERVED_ORIGINALS_CHANGED')
        require(json.loads(raw_file(mapped(LANE/'lane.json',self.root)))==new_config(),'CORRECTED_CONFIG_CHANGED')
        for repo,branch in [(LANE.parent/'repository',BRANCH),(COLAB/'repository',COLAB_BRANCH)]:
            current=subprocess.check_output(['git','branch','--show-current'],cwd=mapped(repo,self.root),text=True).strip();require(current==branch,'CORRECTED_BRANCH_CHANGED')
    def verify_global(self,scope,row):
        self.verify_record();require(scope['source_sha']==SOURCE,'ORIGINAL_SCIENTIFIC_SOURCE')
        expected=dict(binding()['original']['global_call']);expected.update(status='FAILED',receipt=json.dumps(make_receipt(self.review['report_sha256']),sort_keys=True))
        require(row==expected,'EXACT_TERMINAL_GLOBAL_ROW')
        local=read_local(self.root)
        try:require(one(local,'SELECT * FROM manual_calls WHERE id=?',(ID,))==binding()['original']['local_call'],'ORIGINAL_LOCAL_ROW_CHANGED')
        finally:local.close()
        return {'id':ID,'model_client_launched':False,'proof_sha256':sha(canonical(self.expected))}
    def verify_local(self,scope,row,item):
        result=self.verify_global(scope,row);require(dict(item)==binding()['original']['local_call'],'ORIGINAL_LOCAL_ROW_CHANGED');return result

def load_verified_proof(review_folder,*,filesystem_root=Path('/')):return Proof(review_folder,filesystem_root=filesystem_root)

@private_records.private_umask
def apply(batch,review_folder,*,filesystem_root=Path('/'),check_unit=unit_state):
    """One reviewed repair. A partial application stays held for reconciliation."""
    require(os.getuid()==os.getgid()==1003,'SERVICE_OWNER');root=Path(filesystem_root)
    require(batch.folder.resolve()==mapped(LEDGER,root).resolve(),'EXACT_LEDGER')
    reviewed=approval(review_folder);dest=mapped(RECORD,root);require(not dest.exists(),'EXISTING_RECONCILIATION_PRESERVED')
    from orchestrator import private_records
    from orchestrator.remote_supervisor import lock
    with lock(mapped(LANE/'one-run.lock',root)),lock(mapped(LANE/'driver.lock',root)):
        administrative_exception(batch.db,filesystem_root=root,check_unit=check_unit)
        require(batch.db.execute("SELECT count(*) FROM autonomy_calls WHERE status='RUNNING' AND id!=?",(ID,)).fetchone()[0]==0,'OTHER_RUNNING_CALL')
        b=binding();local=read_local(root)
        try:
            require(local.execute('SELECT count(*) FROM manual_calls').fetchone()[0]==1,'ONE_ORIGINAL_LOCAL_CALL')
            require(not mapped(COLAB/'lane',root).exists(),'COLAB_NOT_INITIALIZED')
            repositories=[(mapped(LANE.parent/'repository',root),BRANCH),(mapped(COLAB/'repository',root),COLAB_BRANCH)]
            for repo,newbranch in repositories:
                require(subprocess.check_output(['git','branch','--show-current'],cwd=repo,text=True).strip()==b['original']['git_branch'],'ORIGINAL_REPOSITORY_BRANCH')
                require(subprocess.check_output(['git','rev-parse','HEAD'],cwd=repo,text=True).strip()==SOURCE,'ORIGINAL_REPOSITORY_SOURCE')
                require(not subprocess.check_output(['git','status','--porcelain'],cwd=repo),'CLEAN_ORIGINAL_REPOSITORY')
                require(subprocess.run(['git','show-ref','--verify','--quiet','refs/heads/'+newbranch],cwd=repo).returncode==1,'NEW_BRANCH_MUST_NOT_EXIST')
            count=batch.db.execute('SELECT count(*) FROM autonomy_calls').fetchone()[0]
            private_records.mkdir(dest);private_records.write_bytes(dest/'original-rows.json',canonical(b['original']))
            for name,key in [('lane.original.json','config'),('owner.original.json','owner')]:private_records.write_bytes(dest/name,base64.b64decode(b[key]['base64']))
            for name,z in b['workspace'].items():private_records.write_bytes(dest/('workspace-'+name),raw_file(mapped(z['path'],root)))
            backup=sqlite3.connect(dest/'global-before.sqlite');batch.db.backup(backup);backup.close()
            backup=sqlite3.connect(dest/'local-before.sqlite');local.backup(backup);backup.close()
            receipt=make_receipt(reviewed['report_sha256']);private_records.write_bytes(dest/'INTENT.json',canonical({'original':b['original'],'receipt':receipt,'completion':completion(reviewed['report_sha256'])}))
        finally:local.close()
        batch.finish_scientific(ID,receipt,'FAILED')
        require(batch.db.execute('SELECT count(*) FROM autonomy_calls').fetchone()[0]==count,'CALL_COUNT_CHANGED')
        for repo,newbranch in repositories:subprocess.run(['git','branch','-m',newbranch],cwd=repo,check=True)
        private_records.atomic(mapped(LANE/'lane.json',root),new_config())
        local=private_records.Connection(mapped(LANE/'jobs.sqlite',root));local.row_factory=sqlite3.Row
        try:
            local.execute('BEGIN IMMEDIATE');require(one(local,'SELECT * FROM manual_calls WHERE id=?',(ID,))==b['original']['local_call'],'LOCAL_CALL_CHANGED')
            require(one(local,'SELECT * FROM manual_account WHERE id=1')==b['original']['manual_account'],'LOCAL_ACCOUNT_CHANGED')
            require(one(local,'SELECT * FROM manual_state WHERE id=1')==b['original']['manual_state'],'LOCAL_STATE_CHANGED')
            state=json.loads(b['original']['manual_state']['payload']);state.update(phase='run_spec_author',reason=None)
            state['interventions']=[*state.get('interventions',[]),{'kind':'EXACT_PREMODEL_RECONCILIATION','call_id':ID,'proof_sha256':DOC_SHA,'review_sha256':reviewed['report_sha256'],'original_call_remains_counted':True}]
            local.execute('UPDATE manual_state SET payload=? WHERE id=1',(json.dumps(state),));local.execute('COMMIT')
        except BaseException:
            if local.in_transaction:local.execute('ROLLBACK')
            raise
        finally:local.close()
        private_records.write_bytes(dest/'COMPLETE.json',canonical(completion(reviewed['report_sha256'])))
    proof=load_verified_proof(review_folder,filesystem_root=root)
    row=one(batch.db,'SELECT * FROM autonomy_calls WHERE id=?',(ID,));proof.verify_global({'source_sha':SOURCE},row)
    return completion(reviewed['report_sha256'])
