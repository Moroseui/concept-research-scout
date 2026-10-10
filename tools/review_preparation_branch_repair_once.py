"""One bounded administrative repair review with exact no-model proof.

Original bootstrap remains consumed. Its source and genuine APPROVE are checked
before reusing only the exact terminal classification for this new request.
Normal reviewer, daily admission, accounting, isolation and other refusals stay.
"""
import hashlib,importlib.util,json,os,sys
from pathlib import Path
CHANGE='preparation-branch-admission-repair-20261010'
PREMODEL_ID='e41d3d88958bef07e8cf854cb65125ba496b5537f42d26206ae1cee2df9e0e67'
SOURCE=Path(__file__).resolve().parents[1]
CP=Path('/var/lib/research-system-manual-sprint10-deployment/directions-20261006')/(CHANGE+'-packet3')
ENGINE=Path('/opt/research-system/autonomy-review/d08b91bdc1d0')
PRIOR=Path('/var/lib/research-system-manual-sprint10-deployment/directions-20261006/item4-sender-recovery-20261010/packet/source')
PACKET='a27b9e0bdf19ec037711ff079725ee83afe02e4d2b95fd751ac1ab9a7e81e04d'
APPROVAL='a54ef800461b974db328d18fba65e4d6d819044a3a003d9699a59603b0710139'

def sha(raw):return hashlib.sha256(raw).hexdigest()
def require(ok,why):
    if not ok:raise ValueError('FINAL_SENDER_REVIEW_'+why)
def trusted(path):
    path=Path(path)
    for p in [path,*path.parents]:
        s=p.lstat();require(not p.is_symlink() and s.st_uid==0 and not s.st_mode&0o022,'TRUSTED_SOURCE')
    return path

def classifier(ar):
    folder=Path('/var/lib/research-system-autonomy/reviews')/PACKET
    approved=ar.verify_result(folder)
    require(approved['verdict']=='APPROVE' and approved['change_id']=='item4-sender-recovery-20261010' and approved['source_sha']=='41b93574a0ad0fb546745095ff0078debd6f133d' and approved['report_sha256']==APPROVAL,'PRIOR_GENUINE_APPROVE')
    manifest=json.loads(ar.regular(folder/'packet-manifest.json').read_bytes())
    for name in ('tools/review_sender_recovery_once.py','docs/ITEM4_AUTHOR22_TERMINAL_PRIVATE.json'):
        require(sha(trusted(PRIOR/name).read_bytes())==manifest['source_files'][name],'EXACT_APPROVED_CLASSIFIER')
    spec=importlib.util.spec_from_file_location('_approved_terminal_classifier',PRIOR/'tools/review_sender_recovery_once.py')
    boot=importlib.util.module_from_spec(spec);spec.loader.exec_module(boot)
    # New linked candidate, separately counted. Do not reuse the original request,
    # its one-use dispatch or any prior scientific grant.
    boot.CHANGE=CHANGE
    binding=json.loads(trusted(PRIOR/boot.DOC).read_bytes())
    return boot,binding

def premodel_module(manifest=None):
    path=trusted(SOURCE/'tools/preparation_premodel_recovery.py')
    spec=importlib.util.spec_from_file_location('_exact_premodel_review_proof',path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    require(module.ID==PREMODEL_ID and module.CHANGE==CHANGE,'EXACT_PREMODEL_COMPONENT')
    if manifest is not None:
        for name in ('tools/preparation_premodel_recovery.py',module.DOC,
                     'docs/MECHANICAL_REPAIR_REVIEW_STANDING_AUTHORITY_20261007.txt'):
            require(sha(trusted(SOURCE/name).read_bytes())==manifest['source_files'][name],'BOUND_PROOF_SOURCE')
    return module


def exceptions(db,proof_root,binding,boot,original_verify,read_file,proof):
    require(not db.execute('SELECT 1 FROM autonomy_calls WHERE change_id=?',(CHANGE,)).fetchone(),'ONE_ADMIN_CALL_ONLY')
    result=[]
    for row in db.execute("SELECT * FROM autonomy_calls WHERE status IN ('RUNNING','UNCERTAIN')"):
        if row['id']==PREMODEL_ID:
            require(row['status']=='RUNNING','EXACT_OPEN_PREMODEL_RESERVATION')
            value=proof(db)
            require(value.get('id')==PREMODEL_ID and value.get('model_client_launched') is False and value.get('proof_sha256'),'EXACT_PREMODEL_PROOF')
        else:
            require(row['status']=='UNCERTAIN','OTHER_RUNNING_REFUSED')
            value=boot.qualify(dict(row),binding,read_file) if row['id']==binding['call_id'] else original_verify(dict(row),None if proof_root is None else Path(proof_root)/row['id'])
        result.append(value)
    require(any(r['id']==PREMODEL_ID for r in result) and any(r['id']==binding['call_id'] for r in result),'BOTH_EXACT_PROOFS_REQUIRED')
    return result


def admission_preflight(db, packet, day, proof=None):
    require(day == '2026-10-10', 'UTC_DAY')
    require(db.execute("SELECT count(*) FROM autonomy_calls WHERE day='2026-10-10'").fetchone()[0] == 54,'EXACT_CALL55')
    running=[r[0] for r in db.execute("SELECT id FROM autonomy_calls WHERE status='RUNNING'")]
    require(running==[PREMODEL_ID],'ONLY_EXACT_PREMODEL_RESERVATION')
    require(db.execute('SELECT count(*) FROM autonomy_calls WHERE id=? OR change_id=?',(packet,CHANGE)).fetchone()[0] == 0,'ONE_USE')
    value=(proof or premodel_module().administrative_exception)(db)
    require(value.get('id')==PREMODEL_ID and value.get('model_client_launched') is False and value.get('proof_sha256'),'EXACT_PREMODEL_PROOF')
    return value


def dated_bootstrap(policy,active=None,packet=None):
    def allowance(day):
        # Called inside the ordinary reservation transaction, closes midnight race.
        require(day == '2026-10-10', 'UTC_DAY')
        if active is not None:
            db=active.get('db')
            require(db is not None and db.in_transaction,'ADMISSION_TRANSACTION_REQUIRED')
            admission_preflight(db,packet,day)
        return policy(day)
    return allowance


def verify_dated_policy(policy):
    require(policy('2026-10-10')['limit'] == 100
            and policy('2026-10-11')['limit'] == 50, 'DATED_POLICY')


def main():
    require(os.getuid()==os.getgid()==1003 and Path(__file__).resolve()==CP/'packet/source/tools/review_preparation_branch_repair_once.py','OWNER_PATH')
    meta=json.loads(trusted(CP/'BOOTSTRAP_BINDING.json').read_bytes())
    require(meta['change']==CHANGE and meta['wrapper_sha256']==sha(Path(__file__).read_bytes()),'WRAPPER')
    sys.path.insert(0,str(ENGINE))
    from orchestrator import autonomy_review as ar,autonomy_review_runner as runner,administrative_terminal as terminal,private_records as pr
    packet=trusted(meta['packet_path']);m=ar.verify_packet(packet)
    require(ar.sha(ar.canonical(m))==meta['packet'] and m['change_id']==CHANGE and m['source_sha']==meta['source'] and m['round']==1,'EXACT_NEW_REQUEST')
    boot,binding=classifier(ar)
    premodel=premodel_module(m)
    require(sha(trusted(SOURCE/'docs/MECHANICAL_REPAIR_REVIEW_STANDING_AUTHORITY_20261007.txt').read_bytes())==boot.AUTHORITY,'STANDING_REPAIR_REVIEW_AUTHORITY')
    # One counted repair review; original call54 remains RUNNING and counted until approved reconciliation.
    # It uses the operator-authorized ceiling only for this exact request;
    # no scientific route is connected before independent approval.
    from datetime import datetime, timezone
    from orchestrator import autonomy_limits as limits
    require(datetime.now(timezone.utc).date().isoformat() == '2026-10-10', 'UTC_DAY')
    # Reuse the cap implementation already genuinely APPROVED by call51.
    # Read the preserved
    # approved packet source; never rerun or relabel that request.
    prior_folder=Path('/var/lib/research-system-autonomy/reviews/a93356ff54e860eca1e19a92e54afdb6de9c807e74328534e3f94eac37e798ff')
    prior=ar.verify_result(prior_folder)
    require(prior['verdict']=='APPROVE' and not prior.get('findings') and
        prior['source_sha']=='b2daefc0a6f2eae6b31a62901a974efbb20e6bd6' and
        prior['report_sha256']=='c7b151f22001f60fff51520c350a6e39ee127ea9e76f0f0574037867a70cf20a',
        'ORIGINAL_CAP_GENUINE_APPROVAL')
    prior_manifest=json.loads(ar.regular(prior_folder/'packet-manifest.json').read_bytes())
    approved_source=Path('/var/lib/research-system-manual-sprint10-deployment/directions-20261006/temporary-daily-cap-20261010/packet/source')
    cap_path=trusted(approved_source/'tools/temporary_daily_cap.py')
    for name in ('tools/temporary_daily_cap.py','orchestrator/autonomy_limits.py',
                 'orchestrator/autonomy_review_runner.py','docs/OPERATOR_DIRECTION_20261010.txt',
                 'docs/LIMIT_OPERATOR_DECISION.txt','docs/DAILY_LIMIT_OPERATOR_DECISION_20261007.txt'):
        require(sha(trusted(approved_source/name).read_bytes())==prior_manifest['source_files'][name],
                'EXACT_APPROVED_CAP_SOURCE')
    import sqlite3
    with sqlite3.connect('file:/var/lib/research-system-autonomy/reviews/jobs.sqlite?mode=ro',uri=True) as db:
        db.row_factory=sqlite3.Row
        admission_preflight(db, meta['packet'], datetime.now(timezone.utc).date().isoformat())
    spec=importlib.util.spec_from_file_location('_bootstrap_daily_cap',cap_path)
    cap=importlib.util.module_from_spec(spec);spec.loader.exec_module(cap)
    cap.bind('administrative',approved_source)
    verify_dated_policy(limits.daily_allowance)
    active={}
    limits.daily_allowance=dated_bootstrap(limits.daily_allowance,active,meta['packet'])
    original_reserve=runner.ReviewQueue.reserve
    def reserve(queue,manifest,preflight):
        require(not active and ar.sha(ar.canonical(manifest))==meta['packet']
                and manifest['change_id']==CHANGE and manifest['round']==1,'EXACT_LINKED_RESERVATION')
        active['db']=queue.db
        try:return original_reserve(queue,manifest,preflight)
        finally:active.clear()
    runner.ReviewQueue.reserve=reserve
    original=terminal.administrative_exceptions
    terminal.administrative_exceptions=lambda db,proof_root=None:exceptions(db,proof_root,binding,boot,terminal.verify,lambda path:pr.check(path).read_bytes(),premodel.administrative_exception)
    try:
        result=runner.run(packet,Path('/var/lib/research-system-autonomy/reviews'));print(json.dumps(result,sort_keys=True))
        return 0 if result['status']=='COMPLETE' else 2
    finally:
        terminal.administrative_exceptions=original
        runner.ReviewQueue.reserve=original_reserve

if __name__=='__main__':
    os.umask(0o077);require(len(sys.argv)==1,'NO_ARGUMENTS');raise SystemExit(main())
