"""Scientific admission in the existing M0 ledger, not a second daily budget.

Rows are reserved before the local stage call. A partial reservation is never
reused to launch: it stays RUNNING/UNCERTAIN and requires reconciliation.
"""
from datetime import datetime, timezone
import json
from pathlib import Path
from orchestrator.autonomy_review_runner import ReviewQueue
from orchestrator.manual_executor import digest
from orchestrator import autonomy_limits as limits


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

    def preflight_experiment_run(self, run, scope):
        """Only the two approved item4/6 owners may coexist; caps are shared.

        Does not bypass scientific RUNNING/UNCERTAIN admission or allow another
        owner for a completed experiment. register_experiment_run repeats this
        check inside the write transaction.
        """
        from orchestrator.experiment_context import ITEM4_RUN
        from orchestrator.modal_item4_policy import AUTHORITY
        from orchestrator import diagnostics_policy as dp, private_records as pr
        from tools.deploy_manual_lane import bound
        selected = {ITEM4_RUN:(4, AUTHORITY), dp.RUN_ID:(6, dp.authority())}
        def check_scope(ident, value):
            if (ident not in selected or not isinstance(value, dict)
                    or set(value) != {"schema", "item_number", "run_id", "authority_sha256", "plan_sha256"}
                    or value.get("schema") != "scientific-execution/v1" or value.get("run_id") != ident
                    or type(value.get("item_number")) is not int
                    or (value["item_number"], value.get("authority_sha256")) != selected[ident]
                    or not isinstance(value.get("plan_sha256"), str)
                    or len(value["plan_sha256"]) != 64
                    or any(c not in "0123456789abcdef" for c in value["plan_sha256"])):
                raise ValueError("EXPERIMENT_PARALLEL_SCOPE_REQUIRED")
        check_scope(run, scope)
        if (self.folder/'HALT').exists(): raise ValueError('AUTONOMY_BATCH_HALTED')
        if self.db.execute('SELECT 1 FROM autonomy_runs WHERE id=?', (run,)).fetchone():
            raise ValueError('EXISTING_EXPERIMENT_OWNER_NO_NEW_ALLOWANCE')
        for row in self.db.execute("SELECT * FROM autonomy_runs WHERE status!='COMPLETE'").fetchall():
            if row['status'] != 'ACTIVE' or row['id'] not in selected:
                raise ValueError('ONE_ACTIVE_RESEARCH_RUN')
            owner = json.loads(row['binding'])
            check_scope(row['id'], owner.get('execution_scope'))
            state = bound(self.filesystem_root, owner['state'])
            config = json.loads(pr.check(state/'lane.json').read_bytes())
            raw = pr.check(state/'preparation-plan.json').read_bytes()
            if (config.get('owner_binding') != owner or config.get('execution_scope') != owner['execution_scope']
                    or config.get('run_id') != row['id'] or config.get('plan_sha256') != digest(raw)
                    or owner.get('plan_sha256') != digest(raw)):
                raise ValueError('EXPERIMENT_PARALLEL_OWNER_CHANGED')

    def register_experiment_run(self, run, binding):
        from orchestrator import private_records as pr
        from tools.deploy_manual_lane import bound
        if (not isinstance(binding,dict) or set(binding)!={'state','source','run_id','plan_sha256','review_sha256','execution_scope'}
                or not isinstance(binding['state'],str) or not Path(binding['state']).is_absolute()
                or any(not isinstance(binding[k],str) or len(binding[k])!=n or any(c not in '0123456789abcdef' for c in binding[k])
                       for k,n in [('source',40),('plan_sha256',64),('review_sha256',64)])):
            raise ValueError('EXPERIMENT_OWNER_BINDING_FIELDS')
        original=pr.check(bound(self.filesystem_root,binding['state'])/'preparation-plan.json').read_bytes()
        if digest(original)!=binding['plan_sha256'] or json.loads(original).get('execution_scope')!=binding['execution_scope']:
            raise ValueError('EXPERIMENT_OWNER_PLAN_CHANGED')
        raw = json.dumps(binding, sort_keys=True)
        self.db.execute('BEGIN IMMEDIATE')
        try:
            self.preflight_experiment_run(run, binding.get('execution_scope'))
            if binding.get('run_id') != run: raise ValueError('EXPERIMENT_GLOBAL_OWNER_CHANGED')
            self.db.execute("INSERT INTO autonomy_runs VALUES(?,?,'ACTIVE')", (run,raw))
            self.db.execute('COMMIT')
        except BaseException:
            self.db.execute('ROLLBACK'); raise

    def reserve_scientific(self, ident, run, stage, source, receipt):
        self.db.execute('BEGIN IMMEDIATE')
        try:
            if (self.folder/'HALT').exists():raise ValueError('AUTONOMY_BATCH_HALTED')
            active=self.db.execute('SELECT status,binding FROM autonomy_runs WHERE id=?',(run,)).fetchone()
            if not active or active[0]!='ACTIVE':raise ValueError('BATCH_ACTIVE_RUN_REQUIRED')
            if (json.loads(active['binding']).get('purpose') in {'M4_ITEM4_DIRECT_INPUTS','M4_ITEM4_ENVIRONMENT_INVENTORY'}
                    or json.loads(active['binding']).get('no_scientific_allowance') is True):
                raise ValueError('ADMINISTRATIVE_INPUT_OWNER_CANNOT_ADMIT_SCIENCE')
            if self.status(ident)['status']!='NOT_RESERVED':raise ValueError('PARTIAL_OR_DUPLICATE_GLOBAL_RESERVATION_NO_RETRY')
            from orchestrator.stocktake_recovery import global_exception
            from orchestrator.stocktake_review_recovery import admission
            allowed=admission(self,run,stage,ident,source,receipt)
            if allowed is None:allowed=[global_exception(self,run)]
            from orchestrator.experiment_timeout_continuation import global_exception as timeout_exception
            allowed=[*allowed,timeout_exception(self,run,source=source,stage=stage)]
            pending=self.db.execute("SELECT id FROM autonomy_calls WHERE status IN ('RUNNING','UNCERTAIN')").fetchall()
            from orchestrator.completed_run import closed_ids
            closed=closed_ids(self,run,root=self.filesystem_root)
            if any(row['id'] not in allowed and row['id'] not in closed for row in pending):raise ValueError('BATCH_UNCERTAIN_OR_RUNNING_CALL')
            day=datetime.now(timezone.utc).date().isoformat()
            cap=limits.global_limit(self,run)
            if self.db.execute('SELECT count(*) FROM autonomy_calls WHERE day=?',(day,)).fetchone()[0]>=limits.DAILY:raise ValueError('AUTONOMY_DAILY_CALL_LIMIT')
            batch_allowance=limits.scientific_batch_allowance(self,run,stage,ident,source,receipt)
            if self.db.execute("SELECT count(*) FROM autonomy_calls WHERE kind='scientific'").fetchone()[0]>=batch_allowance['limit']:raise ValueError('AUTONOMY_BATCH_CALL_LIMIT')
            count=self.db.execute("SELECT count(*) FROM autonomy_calls WHERE kind='scientific' AND change_id=?",(run,)).fetchone()[0]
            if count>=cap:raise ValueError('AUTONOMY_RUN_CALL_LIMIT')
            raw=json.dumps({'run_id':run,'stage':stage,'source':source,'input':receipt,**({'batch_continuation':batch_allowance} if batch_allowance['limit']!=limits.SCIENTIFIC_BATCH else {}),'caps':{'batch':batch_allowance['limit'],'run':cap,'daily_all_roles':limits.DAILY,'daily_limit_authority_sha256':limits.DAILY_AUTHORITY,'operator_decision_sha256':limits.cap_authority(cap)}},sort_keys=True)
            self.db.execute("INSERT INTO jobs(id,binding,phase,status) VALUES(?,?,'dispatch','RUNNING')",(ident,raw))
            self.db.execute("INSERT INTO autonomy_calls VALUES(?,?,?,?,?,'RUNNING',?,NULL)",(ident,'scientific',run,count+1,day,raw))
            self.db.execute('INSERT INTO events VALUES(?,?,?)',(ident+':reserved',ident,json.dumps({'kind':'SCIENTIFIC_CALL_RESERVED','charged_units':1,'binding_sha256':digest(raw.encode())})))
            self.db.execute('COMMIT')
        except BaseException:self.db.execute('ROLLBACK');raise
        return {'id':ident,'accounting_units':1,'batch_limit':batch_allowance['limit'],'run_limit':cap,'daily_limit':limits.DAILY,'daily_limit_authority_sha256':limits.DAILY_AUTHORITY,'operator_decision_sha256':limits.cap_authority(cap)}

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
        from orchestrator.experiment_timeout_continuation import global_exception as timeout_exception
        allowed=[*allowed,timeout_exception(self,run,completing=True)]
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
