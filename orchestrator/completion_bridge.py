"""Bounded synthetic completion routing through the existing Linux controller.

Installed configuration chooses at most two predecessor/successor pairs. Models
can select only the configured synthetic successor, never a command, patient
runner, backend, source or threshold. Original events and console identities are
verified before a report task is submitted. Intent precedes idempotent submission;
missing execution evidence never becomes a new attempt.
"""
from datetime import datetime,timezone
import json
from pathlib import Path

from orchestrator.handover_coordinator import encoded,digest
from orchestrator.hosted_cycle import verified_jobs,select_next
from orchestrator.operations_report import immutable
from orchestrator.remote_supervisor import Controller,checked_source,identifier,lock
from orchestrator.reviewer_evidence import collect,current_process


class CompletionBridge:
    def __init__(self,runtime,config):
        if (set(config)!={'authority','source','source_root','state','outputs','pairs'}
                or config['authority']!='OPERATOR_SUPERVISED_SYNTHETIC_ONLY'
                or not isinstance(config['pairs'],dict) or not 1<=len(config['pairs'])<=2):
            raise ValueError('BOUNDED_SYNTHETIC_COMPLETION_CONFIGURATION')
        names=list(config['pairs'])+list(config['pairs'].values())
        for name in names:identifier(name)
        if len(set(names))!=len(names):raise ValueError('SYNTHETIC_COMPLETION_CYCLE_OR_DUPLICATE')
        checked_source(config['source_root'],config['source'])
        self.runtime=runtime;self.config=config
        self.controller=Controller(Path(config['state'])/'jobs.sqlite')
        runtime.q.db.executescript('''
            CREATE TABLE IF NOT EXISTS completion_ingest(event TEXT PRIMARY KEY,job TEXT UNIQUE,task TEXT UNIQUE,status TEXT);
            CREATE TABLE IF NOT EXISTS selected_dispatch(task TEXT PRIMARY KEY,binding TEXT,status TEXT,attempts INTEGER DEFAULT 0);
            CREATE TABLE IF NOT EXISTS completion_blocks(job TEXT PRIMARY KEY,reason TEXT);
        ''')

    def ingest(self):
        r=self.runtime
        allowed={**self.config['pairs'],**{name:None for name in self.config['pairs'].values()}}
        for job,next_job in allowed.items():
            if r.q.db.execute('SELECT 1 FROM completion_ingest WHERE job=?',(job,)).fetchone():continue
            try:
                rows,events=verified_jobs(self.controller,self.config['outputs'],[job])
                if not rows or rows[0]['status'] not in ('COMPLETE','FAILED'):continue
                row=rows[0]
                if row['source']!=self.config['source'] or row['kind'] not in ('synthetic_success','synthetic_failure'):
                    raise ValueError('SYNTHETIC_COMPLETION_SOURCE_REQUIRED')
                event=events[row['attempt_id']]
                proposal=None
                if next_job is not None and row['status']=='COMPLETE':
                    proposal={'job':next_job,'source':self.config['source'],
                              'predecessor':row['attempt_id'],'maximum_dispatches':1}
                with lock(r.state/'branch.lock'):
                    r.q.db.execute('BEGIN IMMEDIATE')
                    try:
                        if r.q.db.execute('SELECT 1 FROM completion_ingest WHERE job=?',(job,)).fetchone():
                            r.q.db.execute('COMMIT');continue
                        implementation=collect(r.root,{'kind':'handover_implementation',
                            'purpose':'Review the actual bounded completion adapter and its authority limits.',
                            'affected_task':job})
                        binding=r.enqueue_report(datetime.now(timezone.utc).date().isoformat(),rows,
                            {'trigger':'Verified synthetic completion '+job,
                             'event_sha256':digest(event),
                             'limits':'Configured synthetic successor only; scientific tasks keep their separate gates.'},
                            reviewer_evidence={'completion':event,'implementation':implementation,'controller_process':current_process()},
                            execution_proposal=proposal,trigger='verified-completion')
                        binding['kind']='astra_turn'
                        r.q.submit(binding)
                        r.q.db.execute('INSERT INTO completion_ingest VALUES(?,?,?,?)',
                            (row['attempt_id'],job,binding['id'],'QUEUED'))
                        r.q.db.execute('COMMIT')
                    except BaseException:r.q.db.execute('ROLLBACK');raise
                r.q.db.execute('DELETE FROM completion_blocks WHERE job=?',(job,))
            except (ValueError,KeyError,TypeError,OSError):
                r.q.db.execute('INSERT OR REPLACE INTO completion_blocks VALUES(?,?)',
                    (job,'COMPLETION_EVIDENCE_RECONCILIATION_REQUIRED'))

    def finish(self,task,packet,answer):
        r=self.runtime
        row=r.q.db.execute('SELECT * FROM completion_ingest WHERE task=?',(task,)).fetchone()
        if not row:return
        proposal=packet.get('execution_proposal')
        if proposal is not None:
            expected={'job':self.config['pairs'].get(row['job']),'source':self.config['source'],
                      'predecessor':row['event'],'maximum_dispatches':1}
            if proposal!=expected or expected['job'] is None:raise ValueError('SYNTHETIC_PROPOSAL_CHANGED')
            choice=json.loads(answer)
            declined=(isinstance(choice,dict) and set(choice)=={'task_id','reason'}
                      and choice['task_id'] is None and isinstance(choice['reason'],str)
                      and 0<len(choice['reason'])<=1000)
            if not declined:choice=select_next(answer,proposal['job'])
            intent={'task':task,'event':row['event'],'proposal':proposal,'selection':choice}
            raw=encoded(intent).decode()
            immutable(r.state/(task+'.selected-dispatch.json'),raw.encode())
            r.q.db.execute('INSERT OR IGNORE INTO selected_dispatch(task,binding,status) VALUES(?,?,?)',(task,raw,'INTENT'))
            old=r.q.db.execute('SELECT * FROM selected_dispatch WHERE task=?',(task,)).fetchone()
            if old['binding']!=raw:raise ValueError('SYNTHETIC_DISPATCH_BINDING_CHANGED')
            if declined:
                r.q.db.execute("UPDATE selected_dispatch SET status='DECLINED' WHERE task=?",(task,))
            else:self.advance()
        r.q.db.execute("UPDATE completion_ingest SET status='PROCESSED' WHERE task=?",(task,))
        self.controller.db.execute("UPDATE wakes SET status='PROCESSED',reason='HANDOVER_REPORT_REVIEW_DISPOSITION_COMPLETE' WHERE id=?",(row['event'],))

    def advance(self):
        """Pause-aware idempotent submission; no model retry or new job identity."""
        r=self.runtime
        with lock(r.state/'admission.lock'):
            if r.q.status()['paused']:return
            for row in r.q.db.execute("SELECT * FROM selected_dispatch WHERE status='INTENT' ORDER BY rowid LIMIT 4").fetchall():
                attempt=row['attempts']+1
                r.q.db.execute('UPDATE selected_dispatch SET attempts=? WHERE task=?',(attempt,row['task']))
                try:
                    intent=json.loads(row['binding'])
                    if (r.state/(row['task']+'.selected-dispatch.json')).read_bytes()!=encoded(intent):
                        raise ValueError('DISPATCH_INTENT_CHANGED')
                    parent=r.q.db.execute('SELECT * FROM completion_ingest WHERE task=?',(row['task'],)).fetchone()
                    expected={'job':self.config['pairs'].get(parent['job']),'source':self.config['source'],
                              'predecessor':parent['event'],'maximum_dispatches':1}
                    if intent['proposal']!=expected or expected['job'] is None:
                        raise ValueError('SYNTHETIC_PROPOSAL_CHANGED')
                    select_next(json.dumps(intent['selection']),expected['job'])
                    # Persist before submission. Existing Controller.register
                    # rejects changed bindings and reuses the same job identity
                    # after a lost response, even if its child already completed.
                    self.controller.submit(expected['job'],expected['source'])
                    r.q.db.execute("UPDATE selected_dispatch SET status='SUBMITTED' WHERE task=?",(row['task'],))
                except (ValueError,KeyError,TypeError,OSError):
                    if row['attempts']>=2:
                        r.q.db.execute("UPDATE selected_dispatch SET status='BLOCKED' WHERE task=?",(row['task'],))
