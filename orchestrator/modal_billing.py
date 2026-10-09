"""Actual Modal Team billing observations for item4 admission and reporting.

The SDK/client and credentials stay in ModalProvider. Preserve exact Decimal
strings and provider rows in private receipts; no guessed credit balance or
subscription fee is reported as experiment compute. Reservations bridge lag.
"""
from datetime import datetime, timezone, timedelta
from decimal import Decimal, InvalidOperation, ROUND_CEILING
import hashlib
import json
import re

MICRO = 1_000_000


def decimal(value, *, signed=False):
    try:
        amount = Decimal(str(value))
    except (ValueError, InvalidOperation):
        raise ValueError('MODAL_BILLING_NUMBER') from None
    if not amount.is_finite() or (not signed and amount < 0):
        raise ValueError('MODAL_BILLING_NUMBER')
    return amount


def micros(value):
    return int((decimal(value) * MICRO).to_integral_value(rounding=ROUND_CEILING))


def timestamp(value):
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset().total_seconds() != 0:
        raise ValueError('MODAL_BILLING_UTC_REQUIRED')
    return value.isoformat()


def mapping(value, *, signed=False):
    if not isinstance(value, dict) or any(not isinstance(k, str) or not k for k in value):
        raise ValueError('MODAL_BILLING_MAPPING')
    return {k: str(decimal(v, signed=signed)) for k, v in value.items()}


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()


def report_rows(billing, start, end):
    """Read contiguous provider-supported ranges; no omitted days or overlap."""
    cursor = start
    while cursor < end:
        stop = min(cursor + timedelta(days=7), end)
        for row in billing.report(start=cursor, end=stop, resolution='h', tag_names=[]):
            if not cursor <= row.interval_start < stop:
                raise ValueError('MODAL_BILLING_REPORT_CHUNK_INTERVAL')
            yield row
        cursor = stop


def capture(workspace, expected_workspace, *, now=None):
    """Read report then summary, so the latter cannot predate the report query.

    Hourly reports exclude the partial final hour; summary may also lag. Neither
    endpoint is treated as final accounting for a currently running container.
    """
    now = now or datetime.now(timezone.utc)
    timestamp(now)
    if workspace.name != expected_workspace:
        raise ValueError('MODAL_AUTHENTICATED_WORKSPACE')
    start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    end = now.replace(minute=0, second=0, microsecond=0)
    rates = mapping(dict(workspace.billing.rates()))
    items = report_rows(workspace.billing, start, end)
    rows = []
    seen = set()
    for row in items:
        instant = timestamp(row.interval_start)
        if (not isinstance(row.object_id, str) or not row.object_id or
                not start <= row.interval_start < end or
                row.interval_start.minute or row.interval_start.second or row.interval_start.microsecond):
            raise ValueError('MODAL_BILLING_REPORT_INTERVAL')
        key = (row.object_id, instant)
        if key in seen:
            raise ValueError('MODAL_BILLING_DUPLICATE_ROW')
        seen.add(key)
        rows.append({'object_id': row.object_id, 'interval_start': instant,
                     'cost': str(decimal(row.cost)), 'cost_by_resource': mapping(dict(row.cost_by_resource))})
    rows.sort(key=lambda r: (r['object_id'], r['interval_start']))
    summary = workspace.billing.summary(cycle=now.strftime('%Y-%m'))
    raw = {'start': timestamp(summary.start), 'end': timestamp(summary.end),
           'metered_cost': str(decimal(summary.metered_cost)),
           'metered_cost_breakdown': mapping(dict(summary.metered_cost_breakdown)),
           'adjustments': mapping(dict(summary.adjustments), signed=True),
           'billed_cost': str(decimal(summary.billed_cost))}
    if summary.start != start or not summary.start <= now < summary.end:
        raise ValueError('MODAL_BILLING_CYCLE')
    # Do not silently reconcile inconsistent provider responses. One micro-dollar
    # permits API Decimal/rounding differences, never material unreported spend.
    if abs(decimal(raw['metered_cost']) + sum((Decimal(v) for v in raw['adjustments'].values()), Decimal(0)) -
           decimal(raw['billed_cost'])) > Decimal('0.000001'):
        raise ValueError('MODAL_BILLING_SUMMARY_MISMATCH')
    report_total = sum((Decimal(row['cost']) for row in rows), Decimal(0))
    if report_total > decimal(raw['metered_cost']) + Decimal('0.000001'):
        raise ValueError('MODAL_BILLING_REPORT_AHEAD_OF_SUMMARY')
    result = {'schema': 'modal-billing-snapshot/v1', 'workspace': expected_workspace,
              'observed_at': timestamp(now), 'report_start': timestamp(start),
              'report_end_exclusive': timestamp(end), 'resolution': 'h',
              'rates': rates, 'summary': raw, 'rows': rows,
              'limits_source': 'operator selection; billing response does not expose account ceilings',
              'partial_hour_excluded': True}
    return {**result, 'sha256': hashlib.sha256(canonical(result)).hexdigest()}


def headroom(snapshot, *, now, usage_limit_micro, spend_limit_micro, commitments, maximum_age_seconds=300):
    """Actual billing plus unreconciled exposure; no double subtraction of usage.

    commitments maps EXCLUSIVE provider object IDs to their cumulative maximum
    authorized cost in this cycle. Partial/active segments stay included. One
    provider object cannot belong to multiple runs in the admission ledger.
    This function is observation, not authority to release a reservation/charge.
    """
    timestamp(now)
    body = dict(snapshot); sha = body.pop('sha256', None)
    if sha != hashlib.sha256(canonical(body)).hexdigest() or body.get('schema') != 'modal-billing-snapshot/v1':
        raise ValueError('MODAL_BILLING_SNAPSHOT_HASH')
    observed = datetime.fromisoformat(body['observed_at'])
    timestamp(observed)
    age = (now - observed).total_seconds()
    if age < 0 or age > maximum_age_seconds or now.strftime('%Y-%m') != observed.strftime('%Y-%m'):
        raise ValueError('MODAL_BILLING_SNAPSHOT_STALE')
    for value in [usage_limit_micro, spend_limit_micro, *commitments.values()]:
        if type(value) is not int or value < 0:
            raise ValueError('MODAL_BILLING_LIMIT_OR_COMMITMENT')
    if not all(isinstance(k, str) and k for k in commitments):
        raise ValueError('MODAL_BILLING_OBJECT_ID')
    totals = {}
    for row in body['rows']:
        totals[row['object_id']] = totals.get(row['object_id'], Decimal(0)) + decimal(row['cost'])
    exposure = sum(max(0, cost - micros(totals.get(ident, 0))) for ident, cost in commitments.items())
    summary = body['summary']
    gross = micros(summary['metered_cost'])
    # The provider labels this as Plan Cost in the pinned SDK's genuine response.
    # Preserve its invoice total, but do not call an operator subscription compute.
    plan = decimal(summary['adjustments'].get('Plan Cost', 0))
    workload_billed = micros(max(Decimal(0), decimal(summary['billed_cost']) - plan))
    return {'snapshot_sha256': sha, 'workspace_metered_micro': gross,
            'workspace_invoice_micro': micros(summary['billed_cost']),
            'operator_plan_fee_micro': micros(plan), 'workspace_workload_billed_micro': workload_billed,
            'unreported_commitment_micro': exposure,
            'usage_headroom_micro': max(0, usage_limit_micro - gross - exposure),
            'spend_headroom_micro': max(0, spend_limit_micro - workload_billed - exposure),
            'credit_assumption': 'no unused credits assumed; only actual billed adjustments',
            'lag_policy': 'full outstanding exposure retained until covered by authenticated object billing'}
