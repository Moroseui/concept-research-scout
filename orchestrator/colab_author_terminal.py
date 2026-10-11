"""Exact terminal Colab timeout: preserve its row, charge, draft and stop.

This classifies process termination, never scientific success or author submission.
It admits no Colab successor. Timing reviewer16 still uses ordinary reservation.
"""
import hashlib,json,sqlite3,subprocess,tempfile
from pathlib import Path
from orchestrator import private_records as pr
CALL='cef242f7d88feb96074dc39ca35ae339c7e73b51bc9f5ea9f5594c864b93eab2'
RUN='colab-1ad5fafc220b3d65f576ce08'
DOC='docs/COLAB_FINAL_AUTHOR_TERMINAL_PRIVATE.json'
DOC_SHA='04ac4c16038d4df43e30128d8906997085db40050edf1357e8ee04968c2cb3b5'
# Exact fully checkpointed terminal ledger; any later ledger change refuses.
DB_SHA='50bc5efd703670b66169d368b8447e275ffd9702d5cdbd90bf091bde1bedf023'
DB_BYTES=122880
_CONTINUATION=None

def sha(raw):return hashlib.sha256(raw).hexdigest()
def require(ok,why):
    if not ok:raise ValueError('COLAB_FINAL_TERMINAL_'+why)

def frozen():
    raw=pr.check(Path(__file__).resolve().parents[1]/DOC).read_bytes()
    require(sha(raw)==DOC_SHA,'DOCUMENT_CHANGED');return json.loads(raw)

def unit_state(unit):
    keys=('LoadState','ActiveState','SubState','MainPID','ControlGroup','ExecMainStatus','InvocationID')
    raw=subprocess.check_output(['systemctl','show',unit,*sum([['-p',k] for k in keys],[])],text=True,timeout=15)
    return dict(line.split('=',1) for line in raw.splitlines())

def checkpointed_bytes(f):
    path=pr.check(Path(f['lane'])/'jobs.sqlite')
    # Never ignore WAL/journal content, including empty or dangling sidecars.
    for suffix in ('-wal','-shm','-journal'):
        sidecar=path.with_name(path.name+suffix)
        require(not sidecar.exists() and not sidecar.is_symlink(),'DATABASE_SIDECAR_PRESENT')
    require(path.stat().st_size==DB_BYTES,'DATABASE_SIZE_CHANGED')
    raw=path.read_bytes()
    require(len(raw)==DB_BYTES and sha(raw)==DB_SHA,'DATABASE_BYTES_CHANGED')
    return raw

def local_state(f):
    if _CONTINUATION is not None:return _CONTINUATION(f)
    raw=checkpointed_bytes(f)
    # immutable applies ONLY to our private, read-only snapshot, never the live DB.
    # No writable mount or live SQLite sidecar is needed or created.
    with tempfile.TemporaryDirectory(prefix='colab-terminal-read-') as folder:
        snapshot=Path(folder)/'terminal.sqlite'
        with pr.open_file(snapshot,'xb') as stream:stream.write(raw)
        snapshot.chmod(0o400)
        db=sqlite3.connect(snapshot.as_uri()+'?mode=ro&immutable=1',uri=True)
        try:
            db.row_factory=sqlite3.Row
            row=db.execute('SELECT * FROM manual_calls WHERE id=?',(CALL,)).fetchone()
            state=db.execute('SELECT payload FROM manual_state WHERE id=1').fetchone()[0]
            result=None if row is None else dict(row),state
        finally:db.close()
        require(checkpointed_bytes(f)==raw,'DATABASE_CHANGED_DURING_READ')
        return result

def qualify(row,f=None,*,read_file=None,observe=None,read_local=None):
    f=frozen() if f is None else f
    require(f['schema']=='colab-final-author-terminal/v1' and f['call_id']==CALL and f['run_id']==RUN
        and f['scientific_successor'] is False and f['scientific_acceptance'] is False,'SCOPE')
    require(dict(row)==f['global_row'] and row['id']==CALL and row['change_id']==RUN
        and row['kind']=='scientific' and row['status']=='UNCERTAIN','ORIGINAL_ROW_CHANGED')
    binding=json.loads(row['binding']);receipt=json.loads(row['receipt'])
    require(binding['stage']=='result_interpretation_author' and binding['input']['workspace']==f['workspace']
        and receipt['outcome']=='FAILED_OR_UNCERTAIN' and receipt['error_type']=='ValueError','ORIGINAL_FAILURE')
    expected={'LoadState':'loaded','ActiveState':'inactive','SubState':'dead','MainPID':'0',
        'ControlGroup':'','ExecMainStatus':'0','InvocationID':''}
    require(f['unit']=='research-review-continuation-20261011.service' and f['unit_state']==expected
        and (observe or unit_state)(f['unit'])==expected,'TERMINAL_PROCESS_REQUIRED')
    local,raw=(read_local or local_state)(f)
    require(local==f['local_row'] and local['id']==CALL and local['status']=='UNCERTAIN'
        and sha(raw.encode())==f['state_sha256'],'LOCAL_STATE_CHANGED')
    state=json.loads(raw)
    require(state['phase']=='BLOCKED' and state['reason']=='MODEL_FAILED_OR_UNCERTAIN_NO_RETRY'
        and state['pending']=={'id':CALL,'stage':'result_interpretation_author','round':1,'workspace':f['workspace']},'BLOCKED_STATE_REQUIRED')
    read_file=read_file or (lambda p:pr.check(p).read_bytes())
    bodies={}
    for name,pin in f['files'].items():
        require(Path(name).name==name,'FILE_PATH')
        body=read_file(Path(f['workspace'])/name)
        require(sha(body)==pin['sha256'] and len(body)==pin['bytes'],'ORIGINAL_BYTES_CHANGED');bodies[name]=body
    events=[json.loads(x) for x in bodies['stage_provenance.jsonl'].splitlines() if x.strip()]
    require(len(events)==1,'ONE_NATIVE_INVOCATION');p=events[0]
    require(p['family_effective']=='codex' and p['stage']=='result_interpretation_author'
        and p['exit_class']=='timeout' and p['exit_detail']=='Agent timed out after 900s.'
        and p['prompt_sha256']==binding['input']['input_sha256']
        and json.loads(bodies['sent-input.json'])['input_sha256']==p['prompt_sha256']
        and bodies['transport.log'].endswith(b'Agent timed out after 900s.\n'),'NATIVE_TIMEOUT_BINDING')
    return {'id':CALL,'classification':'EXACT_TERMINAL_COLAB_AUTHOR_TIMEOUT_NOT_ACCEPTED',
        'proof_sha256':sha(json.dumps(f,sort_keys=True).encode()),'scientific_successor':False}

def retained(scope,row,item):
    if row.get('id')!=CALL:return False
    f=frozen();require(scope['lanes']['colab_preparation']['run_id']==RUN
        and scope['lanes']['colab_preparation']['state']==f['lane']
        and scope['source_sha']==json.loads(row['binding'])['source'],'SEQUENCE_SCOPE')
    if item is not None:require(dict(item)==f['local_row'],'LOCAL_ROW_CHANGED')
    qualify(row,f);return True

def connect_sequence(pi):
    previous=pi._REVIEW_TERMINAL
    require(previous is not None,'PRIOR_CLASSIFIER_REQUIRED')
    pi._REVIEW_TERMINAL=lambda scope,row,item:retained(scope,row,item) or previous(scope,row,item)

def connect_timing_admission():
    from orchestrator import stocktake_review_recovery as sr
    from orchestrator.experiment_context import ITEM4_RUN
    previous=sr.admission
    def admission(batch,run,stage,ident,source,receipt):
        allowed=previous(batch,run,stage,ident,source,receipt)
        expected=sha((ITEM4_RUN+':run_spec_review:16').encode())
        if (run,stage,ident)!=(ITEM4_RUN,'run_spec_review',expected):return allowed
        row=batch.db.execute('SELECT * FROM autonomy_calls WHERE id=?',(CALL,)).fetchone()
        require(row is not None,'ORIGINAL_ROW_REQUIRED');qualify(dict(row))
        require(allowed is not None,'PRIOR_ADMISSION_REQUIRED')
        return list(dict.fromkeys([*allowed,CALL]))
    sr.admission=admission
