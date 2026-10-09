"""Modal cost reservations in the existing batch ledger; integer micro-dollars.

Conservative reservations remain counted after uncertain/failed execution. Only
an authenticated provider accounting reconciliation can replace the estimate.
No model invocation is spent by these deterministic checks.
"""
from decimal import Decimal, ROUND_CEILING
import json
from datetime import datetime, timezone

MICRO = 1_000_000
BATCH_CAP = 50 * MICRO
RUN_CAP = 15 * MICRO
SMOKE_CAP = 10 * MICRO
# Operator's effective gross ceiling, retained conservatively across month rollover.
WORKSPACE_CAP = 42_500_000
# Pinned, observed moroseui Sandbox rates, 2026-09-30. A provider rate change
# requires a new reviewed estimate; never substitute cheaper Function CPU rates.
RATES = {'A100-80GB': '2.50', 'T4': '0.59', 'L4': '0.80',
         'cpu_core_hour': '0.1419', 'memory_gib_hour': '0.024'}


def estimate(resources, overhead_micro):
    if set(resources) != {'gpu', 'cpu', 'memory_mib', 'timeout_seconds'}:
        raise ValueError('MODAL_RESOURCE_FIELDS')
    gpu, cpu, memory, seconds = (resources[k] for k in ('gpu','cpu','memory_mib','timeout_seconds'))
    if gpu not in ('A100-80GB','T4','L4') or any(type(x) is not int for x in (cpu,memory,seconds,overhead_micro)):
        raise ValueError('MODAL_RESOURCE_TYPES')
    if not (1 <= cpu <= 8 and 1024 <= memory <= 65536 and 60 <= seconds <= 3600 and 0 <= overhead_micro <= MICRO):
        raise ValueError('MODAL_RESOURCE_BOUNDS')
    hourly = Decimal(RATES[gpu]) + cpu*Decimal(RATES['cpu_core_hour']) + Decimal(memory)/1024*Decimal(RATES['memory_gib_hour'])
    compute = int((hourly*seconds/3600*MICRO).to_integral_value(rounding=ROUND_CEILING))
    return {'compute_micro_usd': compute, 'overhead_micro_usd': overhead_micro,
            'reserved_micro_usd': compute+overhead_micro, 'rates':dict(RATES),
            'basis':'maximum Sandbox lifetime and hard resource limits; overhead includes image/storage/transfer'}


class ComputeAccounts:
    """Uses BatchAccounts' connection, active-run registration and append-only events."""
    def __init__(self, batch):
        self.batch=batch; self.db=batch.db
        self.db.execute('CREATE TABLE IF NOT EXISTS autonomy_assets(id TEXT PRIMARY KEY, run TEXT NOT NULL, binding TEXT NOT NULL, status TEXT NOT NULL, reserved_micro_usd INTEGER NOT NULL, receipt TEXT)')
        self.db.execute('CREATE TABLE IF NOT EXISTS autonomy_compute(id TEXT PRIMARY KEY, run TEXT NOT NULL, binding TEXT NOT NULL, status TEXT NOT NULL, reserved_micro_usd INTEGER NOT NULL, provider_id TEXT, actual_micro_usd INTEGER, month TEXT NOT NULL)')

    def record_item4_interruption(self, ident, provider, *, reason_record):
        from orchestrator.modal_item4_budget import record_interruption
        return record_interruption(self, ident, provider, reason_record=reason_record)

    def reserve_item4(self, ident, run, binding, *, billing_snapshot, now=None):
        from orchestrator.modal_item4_budget import reserve
        return reserve(self, ident, run, binding, billing_snapshot=billing_snapshot, now=now)

    def reserve(self, ident, run, binding, *, workspace_spent_micro, smoke=False):
        raw=json.dumps(binding,sort_keys=True)
        expected=estimate(binding['resources'],binding['overhead_micro_usd'])
        if binding.get('cost')!=expected:raise ValueError('MODAL_ESTIMATE_BINDING')
        if type(workspace_spent_micro) is not int or workspace_spent_micro<0:raise ValueError('MODAL_PROVIDER_SPEND_REQUIRED')
        amount=expected['reserved_micro_usd']
        if amount > (SMOKE_CAP if smoke else RUN_CAP):raise ValueError('MODAL_RUN_COST_CAP')
        self.db.execute('BEGIN IMMEDIATE')
        try:
            if (self.batch.folder/'HALT').exists():raise ValueError('AUTONOMY_BATCH_HALTED')
            existing=self.db.execute('SELECT * FROM autonomy_compute WHERE id=?',(ident,)).fetchone()
            if existing:
                if existing['binding']!=raw or existing['run']!=run:raise ValueError('MODAL_RESERVATION_CHANGED')
                self.db.execute('COMMIT');return False
            active=self.db.execute('SELECT status FROM autonomy_runs WHERE id=?',(run,)).fetchone()
            if not active or active[0]!='ACTIVE':raise ValueError('BATCH_ACTIVE_RUN_REQUIRED')
            if self.db.execute("SELECT 1 FROM autonomy_calls WHERE status IN ('RUNNING','UNCERTAIN')").fetchone():raise ValueError('BATCH_UNCERTAIN_OR_RUNNING_CALL')
            if self.db.execute("SELECT 1 FROM autonomy_compute WHERE status NOT IN ('COLLECTED','ACCOUNTED')").fetchone():raise ValueError('ONE_ACTIVE_OR_UNCERTAIN_GPU_EXECUTION')
            assets=self.db.execute('SELECT * FROM autonomy_assets').fetchall()
            from orchestrator.modal_direct_recovery import resolved_failure_ids
            resolved=resolved_failure_ids(self,root=self.batch.filesystem_root)
            if any(x['status']!='READY' and x['id'] not in resolved for x in assets):raise ValueError('MODAL_UNCERTAIN_ASSET_PREPARATION')
            rows=self.db.execute('SELECT * FROM autonomy_compute').fetchall()
            asset_total=sum(x['reserved_micro_usd'] for x in assets)
            run_assets=sum(x['reserved_micro_usd'] for x in assets if x['run']==run)
            total=asset_total+sum(max(x['reserved_micro_usd'],x['actual_micro_usd'] or 0) for x in rows)
            run_total=run_assets+sum(max(x['reserved_micro_usd'],x['actual_micro_usd'] or 0) for x in rows if x['run']==run)
            if total+amount>BATCH_CAP or run_total+amount>(SMOKE_CAP if smoke else RUN_CAP):raise ValueError('MODAL_BATCH_OR_RUN_COST_CAP')
            # Deliberately conservative: provider usage plus all batch reservations.
            # This can double count billed work, never undercount it or refund it.
            if workspace_spent_micro+total+amount>WORKSPACE_CAP:raise ValueError('MODAL_WORKSPACE_COST_CAP')
            month=datetime.now(timezone.utc).strftime('%Y-%m')
            self.db.execute("INSERT INTO autonomy_compute VALUES(?,?,?,'RESERVED',?,NULL,NULL,?)",(ident,run,raw,amount,month))
            self.db.execute('INSERT INTO events VALUES(?,?,?)',(ident+':gpu-reserved',run,json.dumps({'kind':'MODAL_COST_RESERVED','micro_usd':amount,'binding':binding},sort_keys=True)))
            self.db.execute('COMMIT');return True
        except BaseException:self.db.execute('ROLLBACK');raise

    def reserve_assets(self,ident,run,binding,*,workspace_spent_micro):
        """One conservative $1 preparation reservation; no scientific submission.

        Covers bounded transfer/storage and registry import. Workload dependency
        installation is charged inside the separately lifetime-bounded Sandbox.
        Failed or uncertain preparation retains this full reservation.
        """
        raw=json.dumps(binding,sort_keys=True)
        if type(workspace_spent_micro) is not int or workspace_spent_micro<0:raise ValueError('MODAL_PROVIDER_SPEND_REQUIRED')
        self.db.execute('BEGIN IMMEDIATE')
        try:
            if (self.batch.folder/'HALT').exists():raise ValueError('AUTONOMY_BATCH_HALTED')
            old=self.db.execute('SELECT * FROM autonomy_assets WHERE id=?',(ident,)).fetchone()
            if old:
                if old['binding']!=raw or old['run']!=run:raise ValueError('MODAL_ASSET_RESERVATION_CHANGED')
                self.db.execute('COMMIT');return False
            active=self.db.execute('SELECT status FROM autonomy_runs WHERE id=?',(run,)).fetchone()
            if not active or active[0]!='ACTIVE':raise ValueError('BATCH_ACTIVE_RUN_REQUIRED')
            if self.db.execute("SELECT 1 FROM autonomy_calls WHERE status IN ('RUNNING','UNCERTAIN')").fetchone():raise ValueError('BATCH_UNCERTAIN_OR_RUNNING_CALL')
            if self.db.execute('SELECT 1 FROM autonomy_assets WHERE run=?',(run,)).fetchone():raise ValueError('ONE_ASSET_PREPARATION_PER_RUN')
            if self.db.execute("SELECT 1 FROM autonomy_compute WHERE status NOT IN ('COLLECTED','ACCOUNTED')").fetchone():raise ValueError('ONE_ACTIVE_OR_UNCERTAIN_GPU_EXECUTION')
            assets=self.db.execute('SELECT * FROM autonomy_assets').fetchall()
            from orchestrator.modal_direct_recovery import resolved_failure_ids
            resolved=resolved_failure_ids(self,root=self.batch.filesystem_root)
            if any(x['status']!='READY' and x['id'] not in resolved for x in assets):raise ValueError('MODAL_UNCERTAIN_ASSET_PREPARATION')
            compute=self.db.execute('SELECT * FROM autonomy_compute').fetchall()
            total=sum(x['reserved_micro_usd'] for x in assets)+sum(max(x['reserved_micro_usd'],x['actual_micro_usd'] or 0) for x in compute)
            run_total=sum(max(x['reserved_micro_usd'],x['actual_micro_usd'] or 0) for x in compute if x['run']==run)
            if total+MICRO>BATCH_CAP or run_total+MICRO>SMOKE_CAP or workspace_spent_micro+total+MICRO>WORKSPACE_CAP:raise ValueError('MODAL_ASSET_COST_CAP')
            self.db.execute("INSERT INTO autonomy_assets VALUES(?,?,?,'RESERVED',?,NULL)",(ident,run,raw,MICRO))
            self.db.execute('INSERT INTO events VALUES(?,?,?)',(ident+':assets-reserved',run,json.dumps({'kind':'MODAL_ASSET_COST_RESERVED','micro_usd':MICRO,'binding':binding},sort_keys=True)))
            self.db.execute('COMMIT');return True
        except BaseException:self.db.execute('ROLLBACK');raise

    def finish_assets(self,ident,status,receipt):
        if status not in {'READY','UNCERTAIN'}:raise ValueError('MODAL_ASSET_STATUS')
        raw=json.dumps(receipt,sort_keys=True)
        self.db.execute('BEGIN IMMEDIATE')
        try:
            old=self.db.execute('SELECT * FROM autonomy_assets WHERE id=?',(ident,)).fetchone()
            if old is None:raise ValueError('MODAL_ASSET_RESERVATION_MISSING')
            if old['status']!='RESERVED':
                if old['status']!=status or old['receipt']!=raw:raise ValueError('MODAL_ASSET_OUTCOME_CHANGED')
                self.db.execute('COMMIT');return
            self.db.execute('UPDATE autonomy_assets SET status=?,receipt=? WHERE id=?',(status,raw,ident))
            self.db.execute('INSERT INTO events VALUES(?,?,?)',(ident+':assets-'+status.lower(),old['run'],raw))
            self.db.execute('COMMIT')
        except BaseException:self.db.execute('ROLLBACK');raise

    def observe(self, ident, status, provider_id):
        if status not in {'CREATED','RUNNING','UNCERTAIN','COLLECTED'}:raise ValueError('MODAL_ACCOUNT_STATUS')
        self.db.execute('BEGIN IMMEDIATE')
        try:
            old=self.db.execute('SELECT * FROM autonomy_compute WHERE id=?',(ident,)).fetchone()
            if old is None or (old['provider_id'] is not None and old['provider_id']!=provider_id):raise ValueError('MODAL_PROVIDER_ID_CHANGED')
            allowed={'RESERVED':{'CREATED','UNCERTAIN'},'CREATED':{'RUNNING','UNCERTAIN'},'RUNNING':{'COLLECTED','UNCERTAIN'},'UNCERTAIN':{'COLLECTED'},'COLLECTED':set()}
            if status!=old['status'] and status not in allowed.get(old['status'],set()):raise ValueError('MODAL_ACCOUNT_TRANSITION')
            self.db.execute('UPDATE autonomy_compute SET status=?,provider_id=? WHERE id=?',(status,provider_id,ident))
            event=ident+':gpu-'+status.lower();payload=json.dumps({'status':status,'provider_id':provider_id},sort_keys=True)
            prior=self.db.execute('SELECT payload FROM events WHERE id=?',(event,)).fetchone()
            if prior and prior[0]!=payload:raise ValueError('MODAL_ACCOUNT_EVENT_CHANGED')
            self.db.execute('INSERT OR IGNORE INTO events VALUES(?,?,?)',(event,old['run'],payload))
            self.db.execute('COMMIT')
        except BaseException:self.db.execute('ROLLBACK');raise
