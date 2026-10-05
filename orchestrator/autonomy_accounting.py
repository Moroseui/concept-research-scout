"""Scientific admission in the existing M0 ledger, not a second daily budget.

Rows are reserved before the local stage call. A partial reservation is never
reused to launch: it stays RUNNING/UNCERTAIN and requires reconciliation.
"""
from datetime import datetime, timezone
import json
from pathlib import Path
from orchestrator.autonomy_review_runner import ReviewQueue
from orchestrator.manual_executor import digest


class BatchAccounts(ReviewQueue):
    def __init__(self, folder, *, filesystem_root=Path("/")):
        self.filesystem_root=Path(filesystem_root).resolve()
        super().__init__(folder)
        self.db.execute("CREATE TABLE IF NOT EXISTS autonomy_runs(id TEXT PRIMARY KEY, binding TEXT NOT NULL, status TEXT NOT NULL)")

    def register_run(self, run, binding):
        raw=json.dumps(binding,sort_keys=True)
        self.db.execute('BEGIN IMMEDIATE')
        try:
            if (self.folder/'HALT').exists():raise ValueError('AUTONOMY_BATCH_HALTED')
            old=self.db.execute('SELECT * FROM autonomy_runs WHERE id=?',(run,)).fetchone()
            if old:
                if old['binding']!=raw:raise ValueError('BATCH_RUN_BINDING_CHANGED')
            else:
                if self.db.execute("SELECT 1 FROM autonomy_runs WHERE status!='COMPLETE'").fetchone():raise ValueError('ONE_ACTIVE_RESEARCH_RUN')
                self.db.execute("INSERT INTO autonomy_runs VALUES(?,?,'ACTIVE')",(run,raw))
            self.db.execute('COMMIT')
        except BaseException:self.db.execute('ROLLBACK');raise

    def reserve_scientific(self, ident, run, stage, source, receipt):
        self.db.execute('BEGIN IMMEDIATE')
        try:
            if (self.folder/'HALT').exists():raise ValueError('AUTONOMY_BATCH_HALTED')
            active=self.db.execute('SELECT status FROM autonomy_runs WHERE id=?',(run,)).fetchone()
            if not active or active[0]!='ACTIVE':raise ValueError('BATCH_ACTIVE_RUN_REQUIRED')
            if self.status(ident)['status']!='NOT_RESERVED':raise ValueError('PARTIAL_OR_DUPLICATE_GLOBAL_RESERVATION_NO_RETRY')
            from orchestrator.stocktake_recovery import global_exception
            from orchestrator.stocktake_review_recovery import admission
            allowed=admission(self,run,stage,ident,source,receipt)
            if allowed is None:allowed=[global_exception(self,run)]
            pending=self.db.execute("SELECT id FROM autonomy_calls WHERE status IN ('RUNNING','UNCERTAIN')").fetchall()
            from orchestrator.completed_run import closed_ids
            closed=closed_ids(self,run,root=self.filesystem_root)
            if any(row['id'] not in allowed and row['id'] not in closed for row in pending):raise ValueError('BATCH_UNCERTAIN_OR_RUNNING_CALL')
            day=datetime.now(timezone.utc).date().isoformat()
            if self.db.execute('SELECT count(*) FROM autonomy_calls WHERE day=?',(day,)).fetchone()[0]>=20:raise ValueError('AUTONOMY_DAILY_CALL_LIMIT')
            if self.db.execute("SELECT count(*) FROM autonomy_calls WHERE kind='scientific'").fetchone()[0]>=30:raise ValueError('AUTONOMY_BATCH_30_CALL_LIMIT')
            count=self.db.execute("SELECT count(*) FROM autonomy_calls WHERE kind='scientific' AND change_id=?",(run,)).fetchone()[0]
            if count>=8:raise ValueError('AUTONOMY_RUN_8_CALL_LIMIT')
            raw=json.dumps({'run_id':run,'stage':stage,'source':source,'input':receipt,'caps':{'batch':30,'run':8,'daily_all_roles':20}},sort_keys=True)
            self.db.execute("INSERT INTO jobs(id,binding,phase,status) VALUES(?,?,'dispatch','RUNNING')",(ident,raw))
            self.db.execute("INSERT INTO autonomy_calls VALUES(?,?,?,?,?,'RUNNING',?,NULL)",(ident,'scientific',run,count+1,day,raw))
            self.db.execute('INSERT INTO events VALUES(?,?,?)',(ident+':reserved',ident,json.dumps({'kind':'SCIENTIFIC_CALL_RESERVED','charged_units':1,'binding_sha256':digest(raw.encode())})))
            self.db.execute('COMMIT')
        except BaseException:self.db.execute('ROLLBACK');raise
        return {'id':ident,'accounting_units':1,'batch_limit':30,'run_limit':8,'daily_limit':20}

    def finish_scientific(self, ident, receipt, status):
        old=self.status(ident)
        if old['status']=='COMPLETE' and status=='COMPLETE':
            prior=json.loads(old['receipt']);base=dict(receipt);repair=base.pop('deterministic_format_repair',None)
            if repair and base==prior:
                raw=json.dumps({'receipt':receipt,'preserves_original_receipt':True},sort_keys=True)
                event=ident+':format-repair'
                exists=self.db.execute('SELECT payload FROM events WHERE id=?',(event,)).fetchone()
                if exists and exists[0]!=raw:raise ValueError('BATCH_FORMAT_REPAIR_CHANGED')
                self.db.execute('INSERT OR IGNORE INTO events VALUES(?,?,?)',(event,ident,raw));return
        self.finish(ident,status,receipt)

    def complete_run(self,run,receipt):
        from orchestrator.stocktake_recovery import global_exception
        from orchestrator.stocktake_review_recovery import completion
        allowed=completion(self,run)
        if allowed is None:allowed=[global_exception(self,run,completing=True)]
        pending=self.db.execute("SELECT id FROM autonomy_calls WHERE change_id=? AND status!='COMPLETE'",(run,)).fetchall()
        if any(row['id'] not in allowed for row in pending):raise ValueError('BATCH_RUN_HAS_UNRESOLVED_CALL')
        event=run+':accepted';raw=json.dumps(receipt,sort_keys=True)
        self.db.execute('BEGIN IMMEDIATE')
        try:
            old=self.db.execute('SELECT payload FROM events WHERE id=?',(event,)).fetchone()
            if old and old[0]!=raw:raise ValueError('BATCH_ACCEPTANCE_CHANGED')
            self.db.execute('INSERT OR IGNORE INTO events VALUES(?,?,?)',(event,run,raw))
            self.db.execute("UPDATE autonomy_runs SET status='COMPLETE' WHERE id=?",(run,))
            self.db.execute('COMMIT')
        except BaseException:self.db.execute('ROLLBACK');raise
