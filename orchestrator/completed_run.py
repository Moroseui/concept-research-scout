"""One operator-accepted run closure. No row, allowance or outcome is rewritten."""
import hashlib
import json
import os
from pathlib import Path
import sqlite3
from tools.deploy_manual_lane import bound

RUN = 'stocktake-c9deb31c7f8668b41df09ea8'
AUTHORITY = '5b44476d33ad44cecef4b6a3cbcdf3240c4a6e90635f0c261aa07911054d22af'
RECORD = '/etc/research-system-manual-sprint10/completed-runs/' + RUN + '.json'
LEDGER = '/var/lib/research-system-autonomy/reviews/jobs.sqlite'


def sha(raw): return hashlib.sha256(raw).hexdigest()
def encoded(value): return json.dumps(value, sort_keys=True, separators=(',', ':')).encode()

def connect(path):
    db = sqlite3.connect(Path(path).resolve().as_uri() + '?mode=ro', uri=True)
    db.row_factory = sqlite3.Row
    return db


def rows(db, table, run=None):
    if table not in ('autonomy_calls', 'manual_calls', 'manual_state', 'manual_account', 'manual_recoveries'):
        raise ValueError('CLOSURE_TABLE')
    query = 'SELECT * FROM ' + table
    values = [dict(x) for x in db.execute(query + (' WHERE change_id=?' if run else ''), (run,) if run else ())]
    return sorted(values, key=lambda x: encoded(x))


def lane_snapshot(path):
    path = Path(path)
    if any(p.is_symlink() for p in (path, path/'lane.json', path/'jobs.sqlite')):
        raise ValueError('CLOSURE_LANE_ALIAS')
    config = json.loads((path/'lane.json').read_text())
    with connect(path/'jobs.sqlite') as db:
        tables = {t: rows(db, t) for t in ('manual_calls','manual_state','manual_account','manual_recoveries')}
    return {'config_sha256': sha((path/'lane.json').read_bytes()), 'run_id': config['run_id'],
            'tables': tables}


def trusted(path):
    path = Path(path)
    for p in [path, *path.parents]:
        if p.is_symlink() or p.stat().st_uid != 0 or p.stat().st_mode & 0o022:
            raise ValueError('CLOSURE_TRUSTED_RECORD_REQUIRED')
    if path.stat().st_mode & 0o007 or path.stat().st_gid not in (0,1003):
        raise ValueError('CLOSURE_PRIVATE_RECORD_REQUIRED')
    return path.read_bytes()


def validate(root=Path('/'), db=None):
    root = Path(root).resolve(); record = bound(root, RECORD)
    if not record.exists(): return None
    raw = trusted(record) if root == Path('/') else record.read_bytes()
    value = json.loads(raw)
    expected = {'schema','run_id','authority','operator_review','accepted_report','acceptance',
                'global_calls','lanes','completed_lane'}
    if set(value) != expected or value['schema'] != 'operator-completed-run/v1' or value['run_id'] != RUN:
        raise ValueError('CLOSURE_SCOPE')
    for key in ('authority','operator_review','accepted_report'):
        ref=value[key]
        if set(ref) != {'path','sha256'} or not Path(ref['path']).is_absolute(): raise ValueError('CLOSURE_REFERENCE')
        p=bound(root,ref['path'])
        data=trusted(p) if root==Path('/') and key!='accepted_report' else p.read_bytes()
        if p.is_symlink() or sha(data)!=ref['sha256']: raise ValueError('CLOSURE_EVIDENCE_CHANGED')
    if value['authority']['sha256']!=AUTHORITY: raise ValueError('CLOSURE_OPERATOR_AUTHORITY')
    review=json.loads(bound(root,value['operator_review']['path']).read_text())
    if (review.get('status')!='REVIEWED_BY_OPERATOR' or review.get('stocktake_run')!=RUN
            or review.get('accepted_report_sha256')!=value['accepted_report']['sha256']):
        raise ValueError('CLOSURE_OPERATOR_REVIEW_REQUIRED')
    own = db is None
    if own: db=connect(bound(root,LEDGER))
    try:
        run=db.execute('SELECT status FROM autonomy_runs WHERE id=?',(RUN,)).fetchone()
        event=db.execute('SELECT payload FROM events WHERE id=?',(RUN+':accepted',)).fetchone()
        if not run or run[0]!='COMPLETE' or not event: raise ValueError('CLOSURE_RUN_NOT_ACCEPTED')
        receipt=json.loads(event[0])
        if (receipt!=value['acceptance'] or receipt.get('acceptance_type')!='operator-accepted'
                or receipt.get('report_sha256')!=value['accepted_report']['sha256']):
            raise ValueError('CLOSURE_ACCEPTANCE_CHANGED')
        calls=rows(db,'autonomy_calls',RUN)
        if calls!=value['global_calls'] or not calls: raise ValueError('CLOSURE_GLOBAL_ROWS_CHANGED')
        if any(x['kind']!='scientific' or x['status'] not in ('COMPLETE','FAILED','UNCERTAIN') for x in calls):
            raise ValueError('CLOSURE_ACTIVE_OR_UNKNOWN_CALL')
        if len({x['id'] for x in calls})!=len(calls): raise ValueError('CLOSURE_DUPLICATE_CALL')
    finally:
        if own: db.close()
    if not isinstance(value['lanes'],dict) or value['completed_lane'] not in value['lanes']:
        raise ValueError('CLOSURE_LANES_REQUIRED')
    global_ids={x['id'] for x in calls}
    for name, expected in value['lanes'].items():
        if not name.startswith('/var/lib/research-system-manual-sprint10/releases/') or not name.endswith('/lane'):
            raise ValueError('CLOSURE_LANE_PATH')
        actual=lane_snapshot(bound(root,name))
        if actual!=expected or actual['run_id']!=RUN: raise ValueError('CLOSURE_LOCAL_ROWS_CHANGED')
        if any(x['id'] not in global_ids or x['status']=='RUNNING' for x in actual['tables']['manual_calls']):
            raise ValueError('CLOSURE_UNBOUND_LOCAL_CALL')
        if name==value['completed_lane']:
            state=actual['tables']['manual_state']
            if len(state)!=1 or json.loads(state[0]['payload']).get('phase')!='COMPLETE':
                raise ValueError('CLOSURE_COMPLETED_LANE_REQUIRED')
    return value


def closed_ids(batch, new_run, *, root=Path('/')):
    if batch.folder.resolve()!=bound(root,LEDGER).parent.resolve(): return set()
    value=validate(root, batch.db)
    if value is None: return set()
    if new_run==RUN: raise ValueError('COMPLETED_RUN_CANNOT_REOPEN')
    return {x['id'] for x in value['global_calls'] if x['status'] in ('FAILED','UNCERTAIN')}


def closed_lanes(root):
    value=validate(root)
    return set() if value is None else {bound(root,p).resolve() for p in value['lanes']}


def seal(root, authority, operator_review, completed_lane):
    """Root preserves new closure metadata; all ledger access is read-only."""
    root=Path(root).resolve()
    if root==Path('/') and os.geteuid()!=0: raise ValueError('CLOSURE_ROOT_SEAL_REQUIRED')
    target=bound(root,RECORD)
    if target.exists() or target.is_symlink(): raise ValueError('CLOSURE_ALREADY_EXISTS')
    authority,operator_review,completed_lane=map(Path,(authority,operator_review,completed_lane))
    def ref(p):
        if not p.is_absolute(): raise ValueError('CLOSURE_ABSOLUTE_REFERENCE')
        actual=bound(root,str(p))
        if actual.is_symlink(): raise ValueError('CLOSURE_REFERENCE_ALIAS')
        return {'path':str(p),'sha256':sha(actual.read_bytes())}
    if ref(authority)['sha256']!=AUTHORITY: raise ValueError('CLOSURE_OPERATOR_AUTHORITY')
    lanes={}
    for p in bound(root,'/var/lib/research-system-manual-sprint10/releases').glob('*/lane/lane.json'):
        if json.loads(p.read_text()).get('run_id')==RUN:
            name='/'+str(p.parent.relative_to(root));lanes[name]=lane_snapshot(p.parent)
    with connect(bound(root,LEDGER)) as db:
        row=db.execute('SELECT payload FROM events WHERE id=?',(RUN+':accepted',)).fetchone()
        if row is None: raise ValueError('CLOSURE_RUN_NOT_ACCEPTED')
        acceptance=json.loads(row[0]);calls=rows(db,'autonomy_calls',RUN)
    value={'schema':'operator-completed-run/v1','run_id':RUN,'authority':ref(authority),
        'operator_review':ref(operator_review),'accepted_report':ref(completed_lane/'REPORT.md'),
        'acceptance':acceptance,'global_calls':calls,'lanes':lanes,'completed_lane':str(completed_lane)}
    from orchestrator import private_records
    with private_records.umask():
        private_records.mkdir(target.parent,parents=True,exist_ok=True)
        with private_records.open_file(target,'xb') as out: out.write(encoded(value))
        if root==Path('/'): os.chown(target,0,1003);os.chown(target.parent,0,1003)
        target.chmod(0o440);target.parent.chmod(0o550)
    validate(root)
    return {'path':str(target),'sha256':sha(target.read_bytes()),'run_id':RUN,
            'preserved_calls':len(calls),'rewritten_rows':0,'new_allowances':0}
