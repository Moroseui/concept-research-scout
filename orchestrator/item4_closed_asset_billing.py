"""Two confirmed empty download attempts; original rows remain immutable."""
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path
import json
import subprocess
from orchestrator import private_records as pr
from orchestrator.manual_executor import digest
from orchestrator.manual_host_guard import trusted
from orchestrator.modal_billing import canonical, decimal, micros
from orchestrator.review_contract import strict_json
from orchestrator.modal_executor import canonical as binding_bytes
from orchestrator.item4_closed_attempt_billing import snapshot, instant

ROOT = Path('/opt/research-system/manual-repair-helpers/item4-benchmark-timer-format-20261009')
CONTRACT_SHA = 'd776712dc05681eba7bb920af0b540d9cda68f7bed85a942dad3c6136fb7ae02'
SUFFIX = ':confirmed-closed-empty-asset'


def require(ok, why):
    if not ok:
        raise ValueError('ITEM4_CLOSED_ASSET_' + why)


def contract():
    raw = pr.check(trusted(ROOT/'docs/ITEM4_CLOSED_EMPTY_ASSETS.json')).read_bytes()
    require(digest(raw) == CONTRACT_SHA, 'CONTRACT_CHANGED')
    p = strict_json(raw)
    require(p['schema'] == 'item4-closed-empty-assets/v1' and
            digest(p['operator']['text'].encode()) == p['operator']['sha256'], 'AUTHORITY')
    return p


def normalize(value):
    def convert(x):
        if isinstance(x, set) and all(isinstance(y, str) for y in x):
            return sorted(x)
        raise ValueError('ITEM4_CLOSED_ASSET_NATIVE_TYPE')
    return json.loads(json.dumps(value, sort_keys=True, default=convert))


def units_stopped(proof):
    for name, pin in proof['old']['units'].items():
        path = trusted(Path('/etc/systemd/system')/name)
        require(digest(path.read_bytes()) == pin['sha256'], 'UNIT_CHANGED')
        observed = dict(line.split('=', 1) for line in subprocess.check_output(
            ['systemctl', 'show', name, '-p', 'ActiveState', '-p', 'MainPID',
             '-p', 'UnitFileState'], text=True).splitlines())
        require(observed.get('ActiveState') == 'inactive' and
                observed.get('UnitFileState') == 'disabled' and
                observed.get('MainPID', '0') == '0', 'WRITER_ACTIVE')


def qualify(accounts, p):
    raw = pr.check(p['observation']['path']).read_bytes()
    require(digest(raw) == p['observation']['sha256'], 'OBSERVATION_CHANGED')
    observed = strict_json(raw)
    require(observed['accounting_mutations'] == observed['model_calls'] ==
            observed['new_compute'] == 0, 'OBSERVATION_SCOPE')
    snapshot(observed['billing'])
    db = accounts.db
    child = db.execute('SELECT * FROM autonomy_assets WHERE id=?', (p['ready_child'],)).fetchone()
    require(child is not None and dict(child) == observed['ready_child'] and
            child['status'] == 'READY', 'CHILD_CHANGED')
    from orchestrator.modal_direct_recovery import parent
    original = parent(accounts, {'recovery_from':strict_json(child['binding'])['recovery']},
                      root=accounts.batch.filesystem_root)
    require(normalize(original) == observed['qualifications'], 'NATIVE_PROOF_CHANGED')
    proofs = {digest(binding_bytes(x['binding'])):x for x in (original, original['ancestor'])}
    require(set(proofs) == set(p['selected']) == set(observed['original_rows']) and
            len(proofs) == 2 and p['ready_child'] not in proofs, 'SELECTION')
    checks = {x['asset_id']:x for x in observed['provider_checks']}
    require(set(checks) == set(proofs) and len(observed['provider_checks']) == 2, 'CHECKS')
    apps = set()
    for ident, proof in proofs.items():
        row = db.execute('SELECT * FROM autonomy_assets WHERE id=?', (ident,)).fetchone()
        require(row is not None and dict(row) == observed['original_rows'][ident] and
                row['status'] == 'UNCERTAIN', 'ORIGINAL_ROW_CHANGED')
        # Historical UNCERTAIN is never rewritten. Native positive terminal
        # qualification, not that status, establishes this precise exception.
        binding = strict_json(row['binding'])
        require(binding == proof['binding'] and digest(binding_bytes(binding)) == ident and
                row['reserved_micro_usd'] == binding['envelope']['cost']['reserved_micro_usd'] and
                strict_json(row['receipt']) == proof['failure'], 'ORIGINAL_BINDING')
        handle = proof['handle']; check = checks[ident]
        require(proof['failure']['status'] == 'FAILED' and
                type(proof['failure']['exit_code']) is int and
                proof['failure']['exit_code'] != 0 and
                proof['failure']['no_automatic_retry'] is True and
                check['terminal_poll'] == proof['failure']['exit_code'] and
                proof['failure']['provider_id'] == handle['provider_id'] and
                handle['binding_sha256'] == ident and check['app_id'] == handle['app_id'],
                'POSITIVE_TERMINAL_PROOF')
        require(check['data_volume_id'] == {'id':handle['data_volume_id'],
                'files':0, 'bytes':0, 'types':[]} and
                check['package_volume_id']['id'] == handle['package_volume_id'] and
                0 < check['package_volume_id']['bytes'] <= 4*1024**2 and
                set(check['package_volume_id']['types']) <= {'FILE','DIRECTORY'}, 'EMPTY_DATA')
        require(set(check['units']) == set(proof['old']['units']), 'WRITERS')
        for status in check['units'].values():
            require(status.get('ActiveState') == 'inactive' and
                    status.get('UnitFileState') == 'disabled' and
                    status.get('MainPID', '0') == '0', 'WRITER_WAS_ACTIVE')
        units_stopped(proof)
        require(handle['app_id'] not in apps, 'SHARED_APP')
        apps.add(handle['app_id'])
        launched = instant(handle['launched_at'])
        require(instant(observed['billing']['report_start']) <= launched <
                instant(observed['billing']['report_end_exclusive']), 'BILLING_WINDOW')
        require(check['billing_rows'] == [r for r in observed['billing']['rows']
                if r['object_id'] == handle['app_id']] and check['billing_rows'],
                'BILLING_MISSING')
    # No other admitted compute or asset may claim either exclusive billing app.
    for row in db.execute('SELECT * FROM autonomy_compute'):
        binding = strict_json(row['binding'])
        require(binding.get('experiment', {}).get('billing_object_id') not in apps, 'SHARED_APP')
    for row in db.execute('SELECT * FROM autonomy_assets'):
        if row['id'] in proofs:
            continue
        receipt = strict_json(row['receipt']) if row['receipt'] else {}
        binding = strict_json(row['binding'])
        require(receipt.get('app_id') not in apps and binding.get('app_id') not in apps, 'SHARED_APP')
    return observed, proofs


def amounts(p, observed, proof, snapshots):
    """High water per completed billing hour, plus unreleased obligations."""
    app = proof['handle']['app_id']
    hours = {}
    for view in [observed['billing'], *snapshots]:
        snapshot(view)
        require(view['workspace'] == observed['billing']['workspace'], 'WORKSPACE')
        for row in view['rows']:
            if row['object_id'] == app:
                key = row['interval_start']
                hours[key] = max(hours.get(key, Decimal(0)), decimal(row['cost']))
    require(bool(hours), 'BILLING_MISSING')
    actual = micros(sum(hours.values(), Decimal(0)))
    envelope = proof['binding']['envelope']
    require(envelope['maximum_stored_bytes']-envelope['download_bytes'] ==
            2*1024**3+4*1024**2 and envelope['reserved_storage_days'] == 35 and
            envelope['billing_month_days_floor'] == 28 and
            envelope['registry_headroom_micro_usd'] == 1000000 and
            envelope['receipt_egress_bound_bytes'] == 4*1024**2, 'ORIGINAL_ENVELOPE')
    rates = observed['billing']['rates']
    # Retain all original partial/package storage, registry headroom and egress.
    # Only never-materialized download storage and excess closed compute release.
    storage = micros(Decimal(2*1024**3+4*1024**2)/1024**3 *
                     decimal(rates['volume_storage_gib_month_cost'])*Decimal(35)/28)
    egress = micros(Decimal(envelope['receipt_egress_bound_bytes'])/1024**3 *
                    decimal(rates['egress_gib_cost']))
    return {'confirmed_compute_micro_usd':actual, 'retained_storage_micro_usd':storage,
            'retained_registry_micro_usd':1000000, 'retained_egress_micro_usd':egress,
            'effective_micro_usd':actual+storage+1000000+egress}


def receipt(p, observed, proof):
    ident = digest(binding_bytes(proof['binding']))
    return {'schema':'item4-closed-empty-asset-reconciliation/v1',
            'contract_sha256':CONTRACT_SHA, 'observation':p['observation'],
            'authority_sha256':p['operator']['sha256'], 'asset_id':ident,
            'original_reserved_micro_usd':observed['original_rows'][ident]['reserved_micro_usd'],
            **amounts(p, observed, proof, []), 'original_rows_changed':False,
            'invoice_final':False}


def record(accounts):
    p = contract(); db = accounts.db
    db.execute('BEGIN IMMEDIATE')
    try:
        observed, proofs = qualify(accounts, p)
        results = {}
        for ident, proof in proofs.items():
            value = receipt(p, observed, proof); raw = canonical(value).decode()
            previous = db.execute('SELECT job,payload FROM events WHERE id=?', (ident+SUFFIX,)).fetchone()
            run = observed['original_rows'][ident]['run']
            if previous:
                require(previous['job'] == run and previous['payload'] == raw, 'RECEIPT_CHANGED')
            else:
                db.execute('INSERT INTO events VALUES(?,?,?)', (ident+SUFFIX, run, raw))
            results[ident] = value
        db.execute('COMMIT')
    except BaseException:
        db.execute('ROLLBACK'); raise
    return {'status':'CLOSED_EMPTY_ASSETS_RECONCILED', 'records':results,
            'original_rows_changed':False, 'provider_calls':0, 'model_calls':0}


def effective(accounts, row, current_snapshot=None, now=None):
    """Unselected assets retain full reservation; corrupt evidence fails closed."""
    event = accounts.db.execute('SELECT job,payload FROM events WHERE id=?',
                                (row['id']+SUFFIX,)).fetchone()
    if event is None:
        return row['reserved_micro_usd']
    p = contract()
    require(row['id'] in p['selected'] and event['job'] == row['run'], 'RECEIPT_SCOPE')
    observed, proofs = qualify(accounts, p)
    proof = proofs[row['id']]
    require(event['payload'] == canonical(receipt(p, observed, proof)).decode(), 'RECEIPT_CHANGED')
    # No claim of indefinite storage coverage beyond the retained original term.
    require((now or datetime.now(timezone.utc)) < instant(proof['binding']['asset_expires_utc']),
            'RETENTION_RECONCILIATION_DUE')
    views = [] if current_snapshot is None else [current_snapshot]
    for saved in accounts.db.execute("SELECT id,payload FROM events WHERE id LIKE 'item4-billing:%'"):
        value = strict_json(saved['payload'])
        require(saved['id'] == 'item4-billing:'+digest(saved['payload'].encode()) and
                value['schema'] == 'item4-billing-highwater/v1', 'HIGHWATER_CHANGED')
        views.append(value['snapshot'])
    return amounts(p, observed, proof, views)['effective_micro_usd']


def billing_objects(accounts):
    """Extend the existing persistent high-water reader only after qualification."""
    if not accounts.db.execute('SELECT 1 FROM events WHERE id LIKE ?', ('%'+SUFFIX,)).fetchone():
        return {}
    p = contract(); observed, proofs = qualify(accounts, p)
    result = {}
    for ident, proof in proofs.items():
        event = accounts.db.execute('SELECT job,payload FROM events WHERE id=?', (ident+SUFFIX,)).fetchone()
        require(event is not None and event['job'] == observed['original_rows'][ident]['run'] and
                event['payload'] == canonical(receipt(p, observed, proof)).decode(), 'RECEIPT_CHANGED')
        result[proof['handle']['app_id']] = observed['original_rows'][ident]['run']
    return result
