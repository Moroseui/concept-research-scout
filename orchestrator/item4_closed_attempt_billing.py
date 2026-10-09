"""Confirmed compute for two exact closed attempts; retain all other exposure."""
from datetime import datetime, timedelta
from decimal import Decimal
from pathlib import Path
import json
from orchestrator import private_records as pr
from orchestrator.manual_executor import digest
from orchestrator.manual_host_guard import trusted
from orchestrator.modal_billing import canonical, decimal, micros
from orchestrator.review_contract import strict_json

ROOT = Path('/opt/research-system/manual-repair-helpers/item4-closed-attempt-billing-20261009')
CONTRACT_SHA = '0cadfaf9b35d6a69c2dc3231dda13c6a76ca6b1a708ddab3e421c1efa1037d57'
SUFFIX = ':confirmed-closed-compute'


def require(ok, why):
    if not ok:
        raise ValueError('ITEM4_CLOSED_BILLING_' + why)


def encoded(value):
    return json.dumps(value, sort_keys=True, allow_nan=False).encode()


def instant(value):
    result = datetime.fromisoformat(value)
    require(result.tzinfo is not None and result.utcoffset().total_seconds() == 0, 'UTC')
    return result


def contract():
    raw = pr.check(trusted(ROOT/'docs/ITEM4_CLOSED_BILLING.json')).read_bytes()
    require(digest(raw) == CONTRACT_SHA, 'CONTRACT_CHANGED')
    value = strict_json(raw)
    require(value['schema'] == 'item4-confirmed-closed-compute/v1' and
            digest(value['operator']['text'].encode()) == value['operator']['sha256'],
            'OPERATOR_BINDING')
    return value


def snapshot(value):
    body = dict(value)
    require(body.pop('sha256', None) == digest(canonical(body)) and
            body.get('schema') == 'modal-billing-snapshot/v1' and
            body.get('resolution') == 'h' and body.get('partial_hour_excluded') is True,
            'SNAPSHOT')
    start, end = map(instant, (body['report_start'], body['report_end_exclusive']))
    require(start <= end <= instant(body['observed_at']), 'REPORT_WINDOW')
    seen = set()
    for row in body['rows']:
        at = instant(row['interval_start'])
        key = (row['object_id'], at)
        require(start <= at < end and at.minute == at.second == at.microsecond == 0 and
                key not in seen, 'REPORT_MEMBERS')
        seen.add(key)
        amount = decimal(row['cost'])
        resources = sum((decimal(v) for v in row['cost_by_resource'].values()), Decimal(0))
        require(abs(amount-resources) <= Decimal('0.000001'), 'RESOURCE_TOTAL')
    return value


def observation(p):
    raw = pr.check(p['observation']['path']).read_bytes()
    require(digest(raw) == p['observation']['sha256'], 'OBSERVATION_CHANGED')
    value = strict_json(raw)
    require(value['app_id'] == p['application'] and value['accounting_mutations'] ==
            value['model_calls'] == value['new_compute'] == 0, 'OBSERVATION_SCOPE')
    snapshot(value['billing'])
    for name, record in value['originals'].items():
        require(digest(record['text'].encode()) == record['sha256'] and
                pr.check(name).read_bytes() == record['text'].encode(), 'ORIGINAL_CHANGED')
    return value


def qualify(db, p):
    """Replay original rows, positive stops and disjoint provider billing hours."""
    observed = observation(p)
    require(len(p['selected']) == 2 and p['current_attempt'] not in p['selected'], 'SELECTION')
    original_rows = {r['id']:r for r in observed['rows']}
    windows = []
    for ident, entry in p['selected'].items():
        row = db.execute('SELECT * FROM autonomy_compute WHERE id=?', (ident,)).fetchone()
        require(row is not None and dict(row) == entry['row'] == original_rows[ident] and
                row['status'] == 'ACCOUNTED' and row['actual_micro_usd'] is None, 'TERMINAL_ROW')
        binding = strict_json(row['binding'])
        require(digest(encoded(binding)) == ident and binding['resources']['gpu'] is None and
                binding['experiment']['billing_object_id'] == p['application'] and
                binding['overhead_micro_usd'] == entry['overhead_micro_usd'] and
                row['reserved_micro_usd'] == binding['cost']['reserved_micro_usd'] and
                binding['cost']['overhead_micro_usd'] == entry['overhead_micro_usd'], 'ROW_BINDING')
        event = db.execute('SELECT * FROM events WHERE id=?', (ident+':pre-science-stop',)).fetchone()
        require(event is not None and dict(event) == entry['event'] ==
                observed['events'][ident+':pre-science-stop'], 'TERMINAL_EVENT')
        proof = strict_json(event['payload'])
        require(proof['terminal_exit_code'] == 137 and proof['may_launch'] is False and
                proof['original_row'] == {**dict(row), 'status':'RUNNING'}, 'STOP_PROOF')
        for name, pin in proof['evidence_files'].items():
            require(observed['originals'][name]['sha256'] == pin, 'TERMINAL_ORIGINAL')
        intent = strict_json(observed['originals'][entry['intent']]['text'])
        stopped = strict_json(observed['originals'][entry['stopped']]['text'])
        start, end = map(instant, entry['window'])
        created, terminated = instant(intent['cost_clock']['observed_at']), instant(stopped['at'])
        require(start.minute == start.second == start.microsecond == 0 and
                end.minute == end.second == end.microsecond == 0 and
                start <= created < terminated < end and
                stopped['terminated'] is True and stopped['provider_id'] == row['provider_id'] and
                intent['binding_sha256'] == ident and intent['preflight']['app_id'] == p['application'],
                'CLOSED_WINDOW')
        require(instant(observed['billing']['report_end_exclusive']) >= end and
                instant(observed['billing']['report_start']) <= start, 'INCOMPLETE_REPORT')
        windows.append((start, end))
    require(windows[0][1] <= windows[1][0] or windows[1][1] <= windows[0][0], 'OVERLAP')
    boundary = max(end for start, end in windows)
    for row in db.execute('SELECT * FROM autonomy_compute'):
        binding = strict_json(row['binding'])
        if binding.get('experiment',{}).get('billing_object_id') != p['application'] or row['id'] in p['selected']:
            continue
        from orchestrator.modal_executor import item4_job
        path = Path(p['work_root'])/item4_job(binding)/'create-intent.json'
        intent = strict_json(pr.check(path).read_bytes())
        require(intent['binding_sha256'] == row['id'] and
                instant(intent['cost_clock']['observed_at']) >= boundary, 'OTHER_ATTEMPT_OVERLAP')
    return observed


def billed(p, observed, ident, snapshots):
    start, end = map(instant, p['selected'][ident]['window'])
    hours = {}
    cursor = start
    while cursor < end:
        hours[cursor] = None
        cursor += timedelta(hours=1)
    for view in [observed['billing'], *snapshots]:
        snapshot(view)
        require(view['workspace'] == observed['billing']['workspace'], 'WORKSPACE')
        for row in view['rows']:
            at = instant(row['interval_start'])
            if row['object_id'] == p['application'] and at in hours:
                amount = decimal(row['cost'])
                hours[at] = max(hours[at] or Decimal(0), amount)
    require(all(v is not None for v in hours.values()), 'MISSING_BILLED_HOUR')
    return sum(hours.values(), Decimal(0))


def receipt(p, observed, ident):
    row = p['selected'][ident]['row']
    actual = billed(p, observed, ident, [])
    return {'schema':'item4-confirmed-closed-compute/v1', 'contract_sha256':CONTRACT_SHA,
            'operator_sha256':p['operator']['sha256'], 'observation':p['observation'],
            'binding_sha256':ident, 'provider_id':row['provider_id'],
            'window':p['selected'][ident]['window'],
            'original_reserved_micro_usd':row['reserved_micro_usd'],
            'observed_compute_usd':str(actual), 'observed_compute_micro_usd':micros(actual),
            'overhead_retained_micro_usd':p['selected'][ident]['overhead_micro_usd'],
            'permanent_rows_changed':False, 'provider_invoice_final':False}


def record(accounts):
    """Append two qualified records atomically; never edit original rows."""
    p = contract()
    db = accounts.db
    db.execute('BEGIN IMMEDIATE')
    try:
        observed = qualify(db, p)
        results = {}
        for ident, entry in p['selected'].items():
            value = receipt(p, observed, ident)
            raw = encoded(value).decode()
            prior = db.execute('SELECT job,payload FROM events WHERE id=?', (ident+SUFFIX,)).fetchone()
            if prior is not None:
                require(prior['job'] == entry['row']['run'] and prior['payload'] == raw, 'RECEIPT_CHANGED')
            else:
                db.execute('INSERT INTO events VALUES(?,?,?)', (ident+SUFFIX, entry['row']['run'], raw))
            results[ident] = value
        db.execute('COMMIT')
    except BaseException:
        db.execute('ROLLBACK')
        raise
    return {'status':'CONFIRMED_COMPUTE_RECORDED_OVERHEAD_RETAINED', 'records':results,
            'model_calls':0, 'provider_calls':0, 'original_rows_changed':False}


def effective(db, row, current_snapshot=None):
    event = db.execute('SELECT job,payload FROM events WHERE id=?', (row['id']+SUFFIX,)).fetchone()
    if event is None:
        return None
    p = contract()
    require(row['id'] in p['selected'] and event['job'] == row['run'], 'RECEIPT_SCOPE')
    observed = qualify(db, p)
    require(event['payload'] == encoded(receipt(p, observed, row['id'])).decode(), 'RECEIPT_CHANGED')
    views = [] if current_snapshot is None else [current_snapshot]
    for saved in db.execute("SELECT id,payload FROM events WHERE id LIKE 'item4-billing:%'"):
        value = strict_json(saved['payload'])
        require(saved['id'] == 'item4-billing:'+digest(saved['payload'].encode()) and
                value['schema'] == 'item4-billing-highwater/v1', 'HIGHWATER_CHANGED')
        views.append(value['snapshot'])
    actual = billed(p, observed, row['id'], views)
    return micros(actual) + p['selected'][row['id']]['overhead_micro_usd']
