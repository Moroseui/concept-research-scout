"""Administrative-only reconciliation of positively terminal scientific calls.

No row mutation, refund, successor permission or new ledger. Root seals evidence;
ReviewQueue checks it during its existing transaction. Scientific guards never
call this module. Unknown/active outcomes retain the unconditional refusal.
"""
import hashlib
import json
import os
from pathlib import Path
import re
import sqlite3
import subprocess
from orchestrator import private_records
from orchestrator.manual_host_guard import trusted

ROOT=Path('/var/lib/research-system-autonomy/scientific-terminal')
APPROVAL='8819a15073af3e6f337c095a76bb469cd7aca07012a0205026541d065c9c0d71'
PRECLIENT_ID='2019f1b1b0c9439743811b6bfa7801fd1ed13c6ad9120e0ebfa5b52e0ed145b1'
PRECLIENT_ROW='6601fe419d6855b93661067d2bf6f0b65671e51b8dcd534d767d23469f223bfb'
PRECLIENT_PINS={'console.log':'93b645ed22251593b80cced4489b3d371afd16069b01d2d53ac55686f4d069b0',
 'stage_provenance.jsonl':'4dca8d53594e49a33b23964f2afff791400465892fb47037de064fb6a00531ae',
 'transport-source.py':'212d821aeadeb092867596fc46e694828720deb682c0b9dbd4443ca4e7d327a7'}

# Exact October 7 author timeout: administrative inspection only, never a retry
# or scientific admission. Original UNCERTAIN row and its charge remain intact.
AUTHOR_TIMEOUT_ID='ed4eb7f9300898b6dfea30e58ec00e45e8b9585fe0162e7ee16e49f06c2a08a5'
AUTHOR_TIMEOUT_ROW='2bd4bac93647618fcd17d1868dc9a4279ca66c3a0a9b1e04c46bbc12ec2d19be'
AUTHOR_TIMEOUT_AUTHORITY='acdf5d6e5208514a469c14276ddf6702c4f0e76ce11c58d0e0b17abfd62bdd53'
AUTHOR_TIMEOUT_PINS={
 'console.log':'6ce01041858e2ab21485697d936349921a9d77bf6cd609d2e55959bb124c6ae3',
 'stage_provenance.jsonl':'923a112ef113e144c6ef887247a66078a301643403a46a4d34047a920abd63db',
 'sent-input.json':'55396fb59de1eea838df650c77591fd06a7b7fc42193a408ddb4a486f7d63160'}

def exact_author_timeout(row,bodies):
    path=Path(__file__).resolve().parents[1]/'docs/MECHANICAL_RETRY_OPERATOR_20261007.txt'
    if digest(path.read_bytes())!=AUTHOR_TIMEOUT_AUTHORITY:
        raise ValueError('ADMIN_AUTHOR_TIMEOUT_AUTHORITY_CHANGED')
    if row_hash(row)!=AUTHOR_TIMEOUT_ROW or set(bodies)!=set(AUTHOR_TIMEOUT_PINS):
        raise ValueError('ADMIN_AUTHOR_TIMEOUT_BINDING')
    if any(digest(bodies[n])!=pin for n,pin in AUTHOR_TIMEOUT_PINS.items()):
        raise ValueError('ADMIN_AUTHOR_TIMEOUT_EVIDENCE_CHANGED')
    records=[json.loads(x) for x in bodies['stage_provenance.jsonl'].decode().splitlines() if x.strip()]
    if len(records)!=1:raise ValueError('ADMIN_AUTHOR_TIMEOUT_ONE_INVOCATION')
    p=records[0];binding=json.loads(row['binding']);expected=binding['input']['input_sha256']
    if (binding.get('stage')!='run_spec_author' or p.get('stage')!='run_spec_author'
        or p.get('family_effective')!='codex' or p.get('exit_class')!='timeout'
        or p.get('exit_detail')!='Agent timed out after 900s.'
        or p.get('prompt_sha256')!=expected
        or json.loads(bodies['sent-input.json']).get('input_sha256')!=expected):
        raise ValueError('ADMIN_AUTHOR_TIMEOUT_NATIVE_BINDING')
    return 'PROVEN_EXACT_AUTHOR_TIMEOUT_ADMIN_ONLY'


def digest(raw):return hashlib.sha256(raw).hexdigest()
def row_hash(row):return digest(json.dumps(dict(row),sort_keys=True).encode())

def authority():
    if digest((Path(__file__).resolve().parents[1]/'docs/ADMIN_REVIEW_SEARCH_APPROVAL.txt').read_bytes())!=APPROVAL:
        raise ValueError('ADMIN_TERMINAL_AUTHORITY_CHANGED')


def unit_state(unit):
    if unit != 'research-item4-author-submission-20261008.service' and not re.fullmatch(r'research-manual-sprint10-[a-zA-Z0-9_-]+\.service',unit):raise ValueError('ADMIN_TERMINAL_UNIT_SCOPE')
    raw=subprocess.check_output(['/usr/bin/systemctl','show',unit,'-p','LoadState','-p','ActiveState','-p','MainPID','-p','ControlGroup','-p','InvocationID'],text=True,timeout=15)
    v=dict(line.split('=',1) for line in raw.splitlines())
    if v.get('LoadState')!='loaded' or v.get('ActiveState') not in {'inactive','failed'} or v.get('MainPID')!='0' or v.get('ControlGroup'):
        raise ValueError('ADMIN_TERMINAL_PROCESS_UNPROVEN')
    return {'unit':unit,'invocation':v.get('InvocationID',''),'boot_id':Path('/proc/sys/kernel/random/boot_id').read_text().strip()}


def proof_kind(row,bodies):
    if row['kind']!='scientific' or row['status']!='UNCERTAIN':raise ValueError('ADMIN_TERMINAL_SCIENTIFIC_ONLY')
    if row['id']==AUTHOR_TIMEOUT_ID:return exact_author_timeout(row,bodies)
    from orchestrator import author_submission_recovery as recovery
    if row['id']==recovery.CALL:
        recovery.terminal(row,bodies)
        return 'PROVEN_EXACT_AUTHOR5_SUBMISSION_REFUSAL_ADMIN_ONLY'
    if row['id']==PRECLIENT_ID:
        if row_hash(row)!=PRECLIENT_ROW or set(bodies)!=set(PRECLIENT_PINS):raise ValueError('ADMIN_PRECLIENT_BINDING')
        if any(digest(bodies[n])!=pin for n,pin in PRECLIENT_PINS.items()):raise ValueError('ADMIN_PRECLIENT_EVIDENCE_CHANGED')
        # This exact reviewed traceback is raised at send_bound's hash guard,
        # before credential_home/isolation.command/Popen in the pinned source.
        # No general inference from missing output or an empty stream is allowed.
        return 'PROVEN_PRECLIENT_INPUT_REFUSAL'
    if set(bodies)!={'console.log','stage_provenance.jsonl','sent-input.json'}:raise ValueError('ADMIN_TERMINAL_EVIDENCE_REQUIRED')
    records=[json.loads(x) for x in bodies['stage_provenance.jsonl'].decode().splitlines() if x.strip()]
    if len(records)!=1:raise ValueError('ADMIN_TERMINAL_ONE_INVOCATION')
    p=records[0];binding=json.loads(row['binding']);stage=binding.get('stage')
    if (p.get('family_effective')!='claude' or p.get('stage')!=stage or stage not in {'run_spec_review','result_interpretation_review'}
        or p.get('exit_class')!='ok' or len(p.get('attempts',[]))!=1 or p['attempts'][0].get('returncode')!=0):
        raise ValueError('ADMIN_TERMINAL_NATIVE_EXIT_REQUIRED')
    expected=binding['input']['input_sha256']
    if p.get('prompt_sha256')!=expected or json.loads(bodies['sent-input.json']).get('input_sha256')!=expected:
        raise ValueError('ADMIN_TERMINAL_INPUT_CHANGED')
    events=[json.loads(x) for x in bodies['console.log'].decode().splitlines() if x.strip()]
    final=[x for x in events if x.get('type')=='result'];init=[x for x in events if x.get('type')=='system' and x.get('subtype')=='init']
    if (len(final)!=1 or len(init)!=1 or final[0] is not events[-1]
        or final[0].get('subtype')!='error_max_turns' or final[0].get('num_turns') not in (30,60)
        or not final[0].get('session_id') or final[0]['session_id']!=init[0].get('session_id')
        or final[0].get('result') or final[0].get('structured_output')):
        raise ValueError('ADMIN_TERMINAL_NO_VERDICT_RESULT_REQUIRED')
    return 'PROVEN_TERMINAL_NATIVE_NO_VERDICT'


def verify(row,folder=None):
    authority();folder=Path(folder) if folder is not None else ROOT/row['id']
    private_records.check_tree(folder)
    value=json.loads(trusted(folder/'proof.json').read_bytes())
    if (value.get('schema')!='administrative-only-terminal/v1' or value.get('authority_sha256')!=APPROVAL
        or value.get('row_sha256')!=row_hash(row) or value.get('id')!=row['id']):raise ValueError('ADMIN_TERMINAL_ROW_BINDING')
    bodies={}
    for name,pin in value['files'].items():
        if Path(name).name!=name or name=='proof.json':raise ValueError('ADMIN_TERMINAL_PATH')
        raw=trusted(folder/name).read_bytes()
        if digest(raw)!=pin:raise ValueError('ADMIN_TERMINAL_EVIDENCE_CHANGED')
        bodies[name]=raw
    if proof_kind(row,bodies)!=value['classification']:raise ValueError('ADMIN_TERMINAL_CLASSIFICATION')
    if unit_state(value['unit']['unit'])!=value['unit']:raise ValueError('ADMIN_TERMINAL_PROCESS_CHANGED')
    return {'id':row['id'],'proof_sha256':digest(trusted(folder/'proof.json').read_bytes()),'classification':value['classification']}


def administrative_exceptions(db,proof_root=None):
    """Only ReviewQueue.reserve calls this; never a scientific permission."""
    result=[]
    for row in db.execute("SELECT * FROM autonomy_calls WHERE status IN ('RUNNING','UNCERTAIN')"):
        if row['status']=='RUNNING':raise ValueError('UNCERTAIN_OR_RUNNING_REVIEW_NO_NEW_CALL')
        try:result.append(verify(dict(row),None if proof_root is None else Path(proof_root)/row['id']))
        except (ValueError,KeyError,TypeError,OSError,UnicodeError):
            raise ValueError('UNCERTAIN_OR_RUNNING_REVIEW_NO_NEW_CALL') from None
    return result


@private_records.private_umask
def record(ledger,ident,workspace,unit,transport_source=None,destination=None,*,filesystem_root=Path("/")):
    """Root captures originals once; no SQLite write or change to a call row."""
    authority()
    if os.geteuid()!=0:raise ValueError('ADMIN_TERMINAL_ROOT_CAPTURE_REQUIRED')
    if not re.fullmatch('[0-9a-f]{64}',ident):raise ValueError('ADMIN_TERMINAL_ID')
    ledger=Path(ledger);workspace=Path(workspace)
    if ledger.is_symlink() or not ledger.is_file():raise ValueError('ADMIN_TERMINAL_LEDGER')
    with sqlite3.connect(ledger.resolve().as_uri()+'?mode=ro',uri=True) as db:
        db.row_factory=sqlite3.Row;row=db.execute('SELECT * FROM autonomy_calls WHERE id=?',(ident,)).fetchone()
        if row is None:raise ValueError('ADMIN_TERMINAL_CALL_MISSING')
        row=dict(row)
    from tools.deploy_manual_lane import bound
    expected_workspace=bound(filesystem_root,json.loads(row['binding'])['input']['workspace'])
    if workspace.resolve()!=expected_workspace.resolve() or workspace.is_symlink():raise ValueError('ADMIN_TERMINAL_WORKSPACE')
    names=['console.log','stage_provenance.jsonl']+([] if ident==PRECLIENT_ID else ['sent-input.json'])
    bodies={n:private_records.check(workspace/n).read_bytes() for n in names}
    if ident==PRECLIENT_ID:
        if transport_source is None:raise ValueError('ADMIN_PRECLIENT_SOURCE_REQUIRED')
        bodies['transport-source.py']=private_records.check(Path(transport_source)).read_bytes()
    elif (workspace/'review.json').exists():raise ValueError('ADMIN_TERMINAL_REPORT_PRESENT')
    classification=proof_kind(row,bodies);quiescent=unit_state(unit)
    folder=Path(destination) if destination is not None else ROOT/ident
    if folder.exists():
        value=verify(row,folder)
        if any(trusted(folder/n).read_bytes()!=raw for n,raw in bodies.items()):raise ValueError('ADMIN_TERMINAL_RECONCILE_CONFLICT')
        return value
    from tools.manual_promotion import private_new,private_mode
    private_records.mkdir(folder.parent,parents=True,exist_ok=True);private_records.mkdir(folder)
    for name,raw in bodies.items():private_new(folder/name,raw)
    value={'schema':'administrative-only-terminal/v1','id':ident,'row_sha256':row_hash(row),'authority_sha256':APPROVAL,
        'classification':classification,'unit':quiescent,'files':{n:digest(raw) for n,raw in bodies.items()},
        'meaning':'Administrative inspection only. Original row/charge unchanged. No scientific successor or approval.'}
    private_new(folder/'proof.json',json.dumps(value,sort_keys=True).encode());private_mode(folder,directory=True);private_mode(folder.parent,directory=True)
    return verify(row,folder)


def main():
    import argparse
    p=argparse.ArgumentParser();p.add_argument('--ledger',type=Path,required=True);p.add_argument('--id',required=True)
    p.add_argument('--workspace',type=Path,required=True);p.add_argument('--unit',required=True);p.add_argument('--transport-source',type=Path)
    a=p.parse_args();print(json.dumps(record(a.ledger,a.id,a.workspace,a.unit,a.transport_source),sort_keys=True))

if __name__=='__main__':main()
