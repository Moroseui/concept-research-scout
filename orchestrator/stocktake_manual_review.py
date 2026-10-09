"""Operator-authorized manual evidence for one stock-take recovery only.

This does not call or alter the automated reviewer, manufacture native receipts,
or classify a manual report as queue-qualified. The operator's exact permission
and root-sealed original report establish this route's provenance boundary.
"""
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import sqlite3

from orchestrator import autonomy_review as review, private_records
from orchestrator.manual_host_guard import trusted
from orchestrator.manual_executor import digest

ROOT=Path('/var/lib/research-system-autonomy/manual-stocktake-transport-review')
DECISION='814db048e4b0cc389bd8f85a8f60a78a38267852d3de473cadc5c02714afcfce'
APPROVAL='75e851d0be7e19684d298563d5059b114409aad8b1377baf9c4531c57e24566f'
CHANGE='stocktake-transport-recovery'
LEDGER=Path('/var/lib/research-system-autonomy/reviews/jobs.sqlite')


SEARCH='stocktake-review-search'
SEARCH_APPROVAL='8819a15073af3e6f337c095a76bb469cd7aca07012a0205026541d065c9c0d71'

NAVIGATION='stocktake-readable-navigation'
NAV_DECISION='75fabaaa7d828b75be71cb27e96d5a3ac5b0a16a71d47fb84b889e46596ef034'
NAV_APPROVAL='bc97593a11dc6ff696184c5964c29a92c5e35a048e82e29f61236a4c098ec1fb'


def scope(change):
    if change==SEARCH:return SEARCH_APPROVAL,SEARCH_APPROVAL,1
    if change==CHANGE:return DECISION,APPROVAL,2
    if change==NAVIGATION:return NAV_DECISION,NAV_APPROVAL,1
    raise ValueError('MANUAL_STOCKTAKE_REVIEW_SCOPE')


def authority(change=CHANGE):
    source=Path(__file__).resolve().parents[1]
    decision,approval,_=scope(change)
    if change==SEARCH:
        if digest((source/'docs/ADMIN_REVIEW_SEARCH_APPROVAL.txt').read_bytes())!=SEARCH_APPROVAL:
            raise ValueError('MANUAL_STOCKTAKE_OPERATOR_AUTHORITY_CHANGED')
        return
    prefix='STOCKTAKE_NAVIGATION' if change==NAVIGATION else 'STOCKTAKE_MANUAL_REVIEW'
    for name,pin in [(prefix+'_DECISION.md',decision),(prefix+'_APPROVAL.txt',approval)]:
        if digest((source/'docs'/name).read_bytes())!=pin:raise ValueError('MANUAL_STOCKTAKE_OPERATOR_AUTHORITY_CHANGED')


def inputs(folder, *, filesystem_root=Path('/')):
    from orchestrator.stocktake_recovery import RUNTIME, PLAN
    from tools.deploy_manual_lane import bound
    folder=Path(folder)
    if folder.parent!=bound(filesystem_root,str(ROOT)) or folder.is_symlink():raise ValueError('NAMED_MANUAL_REVIEW_LOCATION_REQUIRED')
    manifest=json.loads(trusted(folder/'packet-manifest.json').read_bytes())
    change=manifest.get('change_id');decision,approval,round_limit=scope(change);authority(change)
    raw=trusted(folder/'report.md').read_bytes()
    # Windows paste transport may use CRLF; preserve original bytes/hash and
    # normalize only the line-oriented parsing view, never the judgment.
    report=raw.decode('utf-8').replace('\r\n','\n')
    if (manifest.get('runtime_sha256')!=RUNTIME
        or manifest.get('files',{}).get('evidence/analysis-plan.json')!=PLAN or manifest.get('round') not in range(1,round_limit+1)
        or not re.fullmatch('[0-9a-f]{40}',manifest.get('source_sha',''))):
        raise ValueError('MANUAL_STOCKTAKE_REVIEW_SCOPE')
    packet=digest(review.canonical(manifest))
    if folder.name!=packet:raise ValueError('MANUAL_STOCKTAKE_PACKET_BINDING')
    verdict=review.report_verdict(report,manifest)
    if re.findall(r'^## Verdict: (.+)$',report,re.M)!=[verdict]:
        raise ValueError('MANUAL_REVIEW_AMBIGUOUS_VERDICT')
    entrypoint=re.findall(r'^analysis_entrypoint: (.+)$',report,re.M)
    if verdict=='APPROVE' and entrypoint!=['orchestrator.analysis_driver']:
        raise ValueError('MANUAL_ANALYSIS_ENTRYPOINT_REQUIRED')
    identity={}
    for key in ('reviewer_product','reviewer_model','reviewer_session_id'):
        values=re.findall(r'^'+key+r': (.+)$',report,re.M)
        if len(values)!=1 or not values[0].strip():raise ValueError('MANUAL_REVIEWER_ATTRIBUTION_REQUIRED')
        identity[key]=values[0]
    if identity['reviewer_product']!='Claude Code':raise ValueError('INDEPENDENT_MANUAL_CLAUDE_REQUIRED')
    hashes=json.loads(trusted(folder/'evidence-files.json').read_bytes())
    if not isinstance(hashes,dict) or 'operator-return-original.txt' not in hashes:
        raise ValueError('MANUAL_OPERATOR_RETURN_REQUIRED')
    for name,pin in hashes.items():
        if (not isinstance(name,str) or Path(name).name!=name or name in {'report.md','packet-manifest.json','qualification.json','evidence-files.json'}
            or digest(trusted(folder/name).read_bytes())!=pin):raise ValueError('MANUAL_ORIGINAL_EVIDENCE_CHANGED')
    if not trusted(folder/'operator-return-original.txt').read_bytes().strip():raise ValueError('MANUAL_OPERATOR_RETURN_REQUIRED')
    return {'kind':'OPERATOR_AUTHORIZED_ONE_OFF_MANUAL_NOT_QUEUE_QUALIFIED','verdict':verdict,
        'source_sha':manifest['source_sha'],'runtime_sha256':manifest['runtime_sha256'],
        'analysis_entrypoint':entrypoint[0] if verdict=='APPROVE' else None,
        'packet_sha256':packet,'round':manifest['round'],'report_sha256':digest(raw),
        'operator_decision_sha256':decision,'operator_approval_sha256':approval,
        'reviewer_reported_identity':identity,'available_session_evidence':hashes,
        'provenance_limit':'Original report returned by operator. Identity is attributed as reported, not invented native/queue attestation.'}


def verify(folder, *, filesystem_root=Path('/')):
    from tools.deploy_manual_lane import bound
    value=inputs(folder,filesystem_root=filesystem_root);receipt=json.loads(trusted(Path(folder)/'qualification.json').read_bytes())
    if receipt.get('review')!=value or receipt.get('accounting_units')!=1:raise ValueError('MANUAL_QUALIFICATION_BINDING')
    ident='manual-stocktake-'+value['packet_sha256']
    with sqlite3.connect('file:'+str(bound(filesystem_root,str(LEDGER)))+'?mode=ro',uri=True) as db:
        row=db.execute('SELECT kind,change_id,status,receipt FROM autonomy_calls WHERE id=?',(ident,)).fetchone()
        change=json.loads(trusted(Path(folder)/'packet-manifest.json').read_bytes())['change_id']
        if row!=('implementation_review',change,'COMPLETE',review.canonical(receipt).decode()):
            raise ValueError('MANUAL_REVIEW_ACCOUNTING_REQUIRED')
    return value


def evidence_preconditions(folder, *, filesystem_root=Path('/')):
    """Real migration runs as the consuming service account before its intent."""
    if Path(filesystem_root)==Path('/') and os.getuid()!=1003:
        raise ValueError('STOCKTAKE_MIGRATION_SERVICE_USER_REQUIRED')
    folder=Path(folder);private_records.check_tree(folder)
    paths=[folder,*folder.parents,*folder.rglob('*')]
    for path in paths:
        trusted(path)
        if not os.access(path,os.R_OK|(os.X_OK if path.is_dir() else 0)):
            raise ValueError('STOCKTAKE_EVIDENCE_NOT_SERVICE_READABLE')
    return {'checked_as_uid':os.getuid(),'checked_as_gid':os.getgid(),
        'filesystem_root':str(Path(filesystem_root).resolve()),'status':'READABLE_TRUSTED_PRIVATE',
        'paths':[{'path':str(p),'uid':p.stat().st_uid,'gid':p.stat().st_gid,'mode':oct(p.stat().st_mode&0o777)} for p in paths]}


def importer_identity(expected_source):
    import subprocess
    source=Path(__file__).resolve().parents[1]
    head=subprocess.check_output(['git','-C',str(source),'rev-parse','HEAD'],text=True).strip()
    raw=Path(__file__).read_bytes()
    if (not re.fullmatch('[0-9a-f]{40}',expected_source or '') or head!=expected_source
        or subprocess.check_output(['git','-C',str(source),'status','--porcelain'])
        or subprocess.check_output(['git','-C',str(source),'show',head+':orchestrator/stocktake_manual_review.py'])!=raw):
        raise ValueError('REVIEWED_IMPORTER_COMMIT_REQUIRED')
    return {'source_sha':head,'module_sha256':digest(raw),'module_path':str(Path(__file__).resolve())}


# Same subprocess privilege-drop pattern as tools.manual_host_control.lane_state.
# SQL, ordering, limits and receipt-before-commit protocol remain unchanged.
LEDGER_WRITER = r"""import os,sys,json,sqlite3
from pathlib import Path
from datetime import datetime,timezone
p=json.loads(sys.stdin.readline())
if os.geteuid()!=p['uid'] or os.geteuid()==0:raise ValueError('LEDGER_WRITER_PRIVILEGES')
LEDGER=Path(p['ledger']);CHANGE=p['change'];APPROVAL=p['approval']
manifest=p['manifest'];receipt=p['receipt'];status=p['status'];call=p['call']
class Review:
    @staticmethod
    def canonical(v):return json.dumps(v,sort_keys=True,separators=(',',':')).encode()
review=Review()
raw_receipt=p['raw_receipt']
with sqlite3.connect('file:'+str(LEDGER)+'?mode=rw',uri=True) as db:
    db.execute('BEGIN IMMEDIATE')
    day=datetime.now(timezone.utc).date().isoformat()
    if (LEDGER.parent/'HALT').exists():raise ValueError('AUTONOMY_BATCH_HALTED')
    if type(p['daily_limit']) is not int or p['daily_limit']!=50:raise ValueError('LEDGER_DAILY_LIMIT_BINDING')
    if db.execute('SELECT count(*) FROM autonomy_calls WHERE day=?',(day,)).fetchone()[0]>=p['daily_limit']:raise ValueError('AUTONOMY_DAILY_CALL_LIMIT')
    prior=db.execute('SELECT status,binding,receipt FROM autonomy_calls WHERE change_id=? ORDER BY round',(CHANGE,)).fetchall()
    if len(prior)>=p['round_limit'] or manifest['round']!=len(prior)+1:raise ValueError('MANUAL_REVIEW_TWO_ROUND_LIMIT')
    if prior:
        previous=json.loads(prior[-1][2])['review']
        if prior[-1][0]!='COMPLETE' or previous['verdict']!='CHANGES REQUIRED' or previous['source_sha']==manifest['source_sha']:
            raise ValueError('MANUAL_REVIEW_REPAIRS_REQUIRED')
        predecessor=manifest.get('predecessor')
        if not isinstance(predecessor,dict) or predecessor.get('report_sha256')!=previous['report_sha256']:
            raise ValueError('MANUAL_REVIEW_PRIOR_JUDGMENT_BINDING')
    binding=review.canonical({'manifest':manifest,'manual_authority':APPROVAL}).decode()
    db.execute("INSERT INTO jobs(id,binding,phase,status) VALUES(?,?,'dispatch',?)",(call,binding,status))
    db.execute("INSERT INTO autonomy_calls VALUES(?,?,?,?,?,?,?,?)",(call,'implementation_review',CHANGE,manifest['round'],day,status,binding,raw_receipt))
    db.execute('INSERT INTO events VALUES(?,?,?)',(call+':manual-evidence',call,raw_receipt))
    print('READY_FOR_ROOT_RECEIPT',flush=True)
    if sys.stdin.readline().strip()!='COMMIT_ROOT_RECEIPT':raise ValueError('ROOT_RECEIPT_NOT_CONFIRMED')
print('COMMITTED',flush=True)
"""


def _ledger_owner():
    import pwd
    account=pwd.getpwnam('partho')
    if account.pw_uid!=1003 or account.pw_gid!=1003:raise ValueError('LEDGER_OWNER_REQUIRED')
    if not LEDGER.exists():raise sqlite3.OperationalError('unable to open database')
    for path in [LEDGER,Path(str(LEDGER)+'-wal'),Path(str(LEDGER)+'-shm')]:
        if path.exists() and (path.is_symlink() or path.stat().st_uid!=1003 or path.stat().st_gid!=1003 or path.stat().st_mode&0o777!=0o600):
            raise ValueError('LEDGER_OWNER_OR_PERMISSION_CHANGED')
    return 1003,dict(user=1003,group=1003,extra_groups=[])


from contextlib import contextmanager
@contextmanager
def ledger_transaction(manifest,receipt,status,call):
    import subprocess
    from orchestrator import autonomy_limits as limits
    limits.authority()
    uid,options=_ledger_owner()
    change=manifest.get('change_id');_,approval,round_limit=scope(change);authority(change)
    payload={'uid':uid,'daily_limit':limits.DAILY,'ledger':str(LEDGER),'change':change,'approval':approval,'round_limit':round_limit,
        'manifest':manifest,'receipt':receipt,'status':status,'call':call,
        'raw_receipt':review.canonical(receipt).decode()}
    child=subprocess.Popen(['/usr/bin/python3','-I','-c',LEDGER_WRITER],cwd='/',
        env={'PATH':'/usr/bin:/bin'},stdin=subprocess.PIPE,stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,text=True,close_fds=True,**options)
    try:
        child.stdin.write(json.dumps(payload)+'\n');child.stdin.flush()
        if child.stdout.readline().strip()!='READY_FOR_ROOT_RECEIPT':
            child.stdin.close();child.wait(timeout=30)
            raise ValueError((child.stderr.read().strip().splitlines() or ['LEDGER_OWNER_TRANSACTION_FAILED'])[-1])
        yield
        child.stdin.write('COMMIT_ROOT_RECEIPT\n');child.stdin.flush();child.stdin.close()
        response=child.stdout.readline().strip();child.wait(timeout=30)
        if child.returncode or response!='COMMITTED':raise ValueError('LEDGER_OWNER_COMMIT_NOT_CONFIRMED:'+child.stderr.read())
    finally:
        if not child.stdin.closed:child.stdin.close()
        if child.poll() is None:
            try:child.wait(timeout=30)
            except subprocess.TimeoutExpired:child.kill();child.wait()
        child.stdout.close();child.stderr.close()


@private_records.private_umask
def record(packet, report, operator_return, session_evidence=(), *, reviewed_importer_source):
    """Root records already-completed external review once; never launches it.

    Packet/originals must first be preserved root-owned. An interruption is a
    reconciliation stop, not permission to repeat the review or charge.
    """
    from tools.manual_promotion import private_new, private_mode
    if os.geteuid()!=0:raise ValueError('OPERATOR_MANUAL_PRESERVATION_ROOT_REQUIRED')
    importer=importer_identity(reviewed_importer_source)
    packet=Path(packet)
    manifest=review.verify_packet(packet)
    change=manifest.get("change_id");_,_,round_limit=scope(change);authority(change)
    for name in review.inventory(packet):trusted(packet/name)
    ident=digest(review.canonical(manifest));folder=ROOT/ident
    if folder.exists():
        supplied={'operator-return-original.txt':trusted(operator_return).read_bytes(),
            **{f'actual-session-evidence-{n:02d}':trusted(p).read_bytes() for n,p in enumerate(session_evidence,1)}}
        preserved=json.loads(trusted(folder/'evidence-files.json').read_bytes())
        if (trusted(report).read_bytes()!=trusted(folder/'report.md').read_bytes()
            or {name:digest(body) for name,body in supplied.items()}!=preserved):
            raise ValueError('MANUAL_REIMPORT_CONFLICT_PRESERVED')
        receipt=json.loads(trusted(folder/'qualification.json').read_bytes())
        if receipt.get('qualification_error'):
            raise ValueError('PRESERVED_MANUAL_REFUSAL_NO_REVIEW_OR_CHARGE_RETRY')
        return verify(folder)
    raw=trusted(report).read_bytes();returned=trusted(operator_return).read_bytes()
    evidence={f'actual-session-evidence-{n:02d}':trusted(p).read_bytes() for n,p in enumerate(session_evidence,1)}
    evidence['operator-return-original.txt']=returned
    new_root=not ROOT.exists()
    private_records.mkdir(ROOT,parents=True,exist_ok=True);private_records.mkdir(folder)
    private_new(folder/'report.md',raw)
    private_new(folder/'packet-manifest.json',review.canonical(manifest))
    for name,body in evidence.items():private_new(folder/name,body)
    private_new(folder/'evidence-files.json',{name:digest(body) for name,body in evidence.items()})
    private_mode(folder,directory=True)
    if new_root:private_mode(ROOT,directory=True)
    try:
        value=inputs(folder);qualification_error=None
    except (ValueError,KeyError,UnicodeError) as error:
        value=None;qualification_error=str(error)
    receipt={'review':value,'importer':importer,'qualification_error':qualification_error,'report_sha256':digest(raw),
        'packet_sha256':ident,'accounting_units':1,'accounted_at':datetime.now(timezone.utc).isoformat(),
        'meaning':'One completed operator-managed administrative review; no scientific call or allowance.'}
    raw_receipt=review.canonical(receipt).decode();call='manual-stocktake-'+ident
    if manifest.get('round') not in range(1,round_limit+1):raise ValueError('MANUAL_STOCKTAKE_REVIEW_SCOPE')
    status='COMPLETE' if value is not None else 'FAILED'
    with ledger_transaction(manifest,receipt,status,call):
        private_new(folder/'qualification.json',review.canonical(receipt))
    if value is None:return {'status':'MANUAL_REVIEW_NOT_QUALIFIED','reason':qualification_error,'accounting_units':1,'folder':str(folder)}
    return verify(folder)


def main():
    import argparse
    p=argparse.ArgumentParser();p.add_argument('--packet',type=Path,required=True);p.add_argument('--report',type=Path,required=True)
    p.add_argument('--reviewed-importer-source',required=True);p.add_argument('--operator-return',type=Path,required=True);p.add_argument('--session-evidence',type=Path,action='append',default=[])
    a=p.parse_args();print(json.dumps(record(a.packet,a.report,a.operator_return,a.session_evidence,reviewed_importer_source=a.reviewed_importer_source),sort_keys=True,indent=2))

if __name__=='__main__':main()
