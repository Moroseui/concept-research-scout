"""Owner-written terminal accounting for same-preprocessing continuation.

No generic failure is retryable. Original rows, reservations and scientific
bindings are preserved; only positive terminal causes with committed steps
qualify. The ordinary reservation still applies all existing caps and gates.
"""
import json
from orchestrator import private_records as pr
from orchestrator.preprocessing_checkpoints import hash_value,sha,resume,same_execution
from orchestrator.review_contract import strict_json

REASONS={'PROVIDER_LIMIT','LIFETIME_TIMEOUT','DELIBERATE_SMOKE_INTERRUPTION'}


def validate_proof(binding,provider_id,proof):
    ident=hash_value(binding)
    fields={'schema','provider_id','binding_sha256','terminal_exit_code','volume_id','snapshot',
            'steps_record_sha256','observed_at','may_launch'}
    if (not isinstance(proof,dict) or set(proof)!=fields
            or proof['schema']!='preprocessing-terminal-proof/v1'
            or proof['provider_id']!=provider_id or proof['binding_sha256']!=ident
            or type(proof['terminal_exit_code']) is not int or proof['terminal_exit_code']==0
            or proof['volume_id']!=binding['preprocessing_output_volume_id'] or proof['may_launch'] is not False
            or not isinstance(proof['observed_at'],str) or not proof['observed_at']
            or not isinstance(proof['snapshot'],dict)
            or proof['snapshot'].get('schema')!='preprocessing-steps/v1'
            or proof['snapshot'].get('binding_sha256')!=ident
            or not proof['snapshot'].get('steps')
            or proof['steps_record_sha256']!=hash_value(proof['snapshot'])):
        raise ValueError('PREPROCESSING_TERMINAL_PROOF_BINDING')
    return proof


def record(accounts,ident,provider,*,reason_record):
    row=accounts.db.execute('SELECT * FROM autonomy_compute WHERE id=?',(ident,)).fetchone()
    if row is None:raise ValueError('PREPROCESSING_SEGMENT_MISSING')
    binding=strict_json(row['binding'])
    if hash_value(binding)!=ident:raise ValueError('PREPROCESSING_ROW_BINDING')
    from orchestrator.modal_item4_policy import AUTHORITY
    if 'preprocessing' not in binding or binding.get('experiment',{}).get('authority_sha256')!=AUTHORITY:
        raise ValueError('PREPROCESSING_INTERRUPTION_SCOPE')
    raw=pr.check(reason_record).read_bytes();reason=strict_json(raw)
    expected={'schema':'modal-interruption-cause/v1','segment_id':ident,'provider_id':row['provider_id']}
    if (not isinstance(reason,dict) or set(reason)!=set(expected)|{'reason','evidence'}
            or any(reason.get(k)!=v for k,v in expected.items()) or reason['reason'] not in REASONS
            or not isinstance(reason['evidence'],dict) or not reason['evidence']):
        raise ValueError('PREPROCESSING_INTERRUPTION_CAUSE_REQUIRED')
    existing=accounts.db.execute('SELECT payload FROM events WHERE id=?',(ident+':preprocessing-interruption',)).fetchone()
    if existing:
        saved=strict_json(existing['payload'])
        if row['status']!='ACCOUNTED' or saved['reason_record_sha256']!=sha(raw):
            raise ValueError('PREPROCESSING_INTERRUPTION_RECONCILIATION')
        validate_proof(binding,row['provider_id'],saved['proof']);return saved
    if row['status'] not in {'RUNNING','UNCERTAIN'} or not row['provider_id']:
        raise ValueError('PREPROCESSING_KNOWN_EXECUTION_REQUIRED')
    proof=provider.terminal_preprocessing_steps(row['provider_id'],binding)
    validate_proof(binding,row['provider_id'],proof)
    saved={'kind':'PREPROCESSING_INTERRUPTED_WITH_COMMITTED_STEPS','proof':proof,
        'resume_reason':reason['reason'],'reason_record_sha256':sha(raw),'prior_status':row['status'],
        'prior_reserved_micro_usd':row['reserved_micro_usd'],
        'charge_disposition':'full reservation retained; ACCOUNTED is not scientific completion'}
    accounts.db.execute('BEGIN IMMEDIATE')
    try:
        current=accounts.db.execute('SELECT * FROM autonomy_compute WHERE id=?',(ident,)).fetchone()
        if dict(current)!=dict(row):raise ValueError('PREPROCESSING_ROW_CHANGED_DURING_OBSERVATION')
        accounts.db.execute('INSERT INTO events VALUES(?,?,?)',(ident+':preprocessing-interruption',row['run'],json.dumps(saved,sort_keys=True)))
        accounts.db.execute("UPDATE autonomy_compute SET status='ACCOUNTED' WHERE id=?",(ident,))
        accounts.db.execute('COMMIT')
    except BaseException:accounts.db.execute('ROLLBACK');raise
    return saved


def validate_reservation(db,old,data,binding):
    same_execution(data,binding);link=resume(binding)
    event=db.execute('SELECT payload FROM events WHERE id=?',(old['id']+':preprocessing-interruption',)).fetchone()
    if old['status']!='ACCOUNTED' or event is None:raise ValueError('PREPROCESSING_TERMINAL_PROOF_REQUIRED')
    value=strict_json(event['payload']);proof=validate_proof(data,old['provider_id'],value.get('proof'))
    if (value.get('kind')!='PREPROCESSING_INTERRUPTED_WITH_COMMITTED_STEPS'
            or value.get('resume_reason') not in REASONS
            or value.get('prior_reserved_micro_usd')!=old['reserved_micro_usd']
            or link!={'previous_segment_id':old['id'],'terminal_receipt_sha256':sha(event['payload'].encode()),
                      'steps_record_sha256':proof['steps_record_sha256']}):
        raise ValueError('PREPROCESSING_RESUME_BINDING')
