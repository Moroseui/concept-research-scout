"""Persistent bounded coordinator over Store, with immutable stage completion.

Handlers are installed Python interfaces, never request-selected shell commands.
A missing completion after STARTED is uncertain: preserve and block that task.
Already completed stages (including Claude review) are never rerun for bookkeeping.
"""
from contextlib import contextmanager
from datetime import datetime
import fcntl
import hashlib
import json
import os
from pathlib import Path
import sqlite3

from orchestrator.job_store import Store
from orchestrator.operations_report import private_root, immutable
from orchestrator.public_export import text


def encoded(value): return (json.dumps(value,sort_keys=True)+'\n').encode()
def digest(value): return hashlib.sha256(encoded(value)).hexdigest()


class Coordinator:
    def __init__(self,root,handlers,admission):
        self.root=private_root(root)
        self.store=Store(self.root/'coordinator.sqlite');self.db=self.store.db
        self.handlers=handlers;self.admission=admission
        self.db.executescript('''
          CREATE TABLE IF NOT EXISTS tasks(id TEXT PRIMARY KEY,binding TEXT NOT NULL,status TEXT NOT NULL,reason TEXT);
          CREATE TABLE IF NOT EXISTS stages(task TEXT,position INTEGER,state TEXT NOT NULL,receipt TEXT,PRIMARY KEY(task,position));
          CREATE TABLE IF NOT EXISTS controls(singleton INTEGER PRIMARY KEY CHECK(singleton=1),revision INTEGER,paused INTEGER);
          INSERT OR IGNORE INTO controls VALUES(1,0,0);
          CREATE TABLE IF NOT EXISTS steering(id TEXT PRIMARY KEY,binding TEXT NOT NULL);
          CREATE TABLE IF NOT EXISTS schedules(day TEXT PRIMARY KEY,task TEXT NOT NULL);
        ''')

    def submit(self,binding):
        required={'id','source','kind','thread','dependencies','stages'}
        if set(binding)!=required or binding['thread'] not in ('primary','adjacent') or binding['kind'] not in ('astra_turn','nightly_review'):
            raise ValueError('TASK_SCHEMA')
        if not isinstance(binding['id'],str) or len(binding['id'])!=64 or any(c not in '0123456789abcdef' for c in binding['id']):raise ValueError('TASK_ID')
        if len(binding['source'])!=40 or any(c not in '0123456789abcdef' for c in binding['source']):raise ValueError('SOURCE_ID')
        if not 1<=len(binding['stages'])<=3 or any(s not in self.handlers for s in binding['stages']):raise ValueError('BOUNDED_INSTALLED_HANDLERS_REQUIRED')
        if len(binding['dependencies'])>32 or binding['id'] in binding['dependencies']:raise ValueError('DEPENDENCIES')
        raw=encoded(binding).decode();text(raw)
        inserted=self.db.execute('INSERT OR IGNORE INTO tasks VALUES(?,?,?,NULL)',(binding['id'],raw,'QUEUED')).rowcount
        old=self.db.execute('SELECT binding FROM tasks WHERE id=?',(binding['id'],)).fetchone()
        if old[0]!=raw:raise ValueError('TASK_BINDING_CONFLICT')
        return {'duplicate':not bool(inserted),'id':binding['id']}

    def status(self):
        control=dict(self.db.execute('SELECT revision,paused FROM controls').fetchone())
        return {**control,'tasks':[dict(r) for r in self.db.execute('SELECT id,status,reason FROM tasks ORDER BY id')]}

    def control(self,request,*,authenticated_operator):
        with (self.root/'admission.lock').open('a') as gate:
            fcntl.flock(gate,fcntl.LOCK_EX)
            return self._control(request,authenticated_operator=authenticated_operator)

    def _control(self,request,*,authenticated_operator):
        # Only a trusted transport can supply authenticated_operator. No JSON role
        # or phone ACK is an authentication mechanism.
        if not authenticated_operator:raise ValueError('OPERATOR_AUTH_REQUIRED')
        if set(request)!={'id','expected_revision','action'} or request['action'] not in ('pause','resume'):raise ValueError('CONTROL_SCHEMA')
        text(json.dumps(request));raw=encoded(request).decode()
        self.db.execute('BEGIN IMMEDIATE')
        try:
            previous=self.db.execute('SELECT binding FROM steering WHERE id=?',(request['id'],)).fetchone()
            if previous:
                if previous[0]!=raw:raise ValueError('STEERING_CONFLICT')
                self.db.execute('COMMIT');return {'duplicate':True,**self.status()}
            rev=self.db.execute('SELECT revision FROM controls').fetchone()[0]
            if request['expected_revision']!=rev:raise ValueError('STALE_CONTROL')
            self.db.execute('INSERT INTO steering VALUES(?,?)',(request['id'],raw))
            self.db.execute('UPDATE controls SET revision=revision+1,paused=?',(request['action']=='pause',))
            self.db.execute('COMMIT')
        except BaseException:self.db.execute('ROLLBACK');raise
        return {'duplicate':False,**self.status()}

    def schedule(self,now,zone,hour,minute,binding):
        from zoneinfo import ZoneInfo
        if now.tzinfo is None or not 0<=hour<24 or not 0<=minute<60:raise ValueError('EXPLICIT_SCHEDULE_REQUIRED')
        local=now.astimezone(ZoneInfo(zone))
        if (local.hour,local.minute)<(hour,minute):return {'status':'NOT_DUE'}
        if binding['kind']!='nightly_review':raise ValueError('NIGHTLY_KIND')
        day=local.date().isoformat()
        # Caller derives report/task identity from day + pinned report. Review and
        # disposition publication cannot recursively create a new schedule day.
        self.db.execute('BEGIN IMMEDIATE')
        try:
            prior=self.db.execute('SELECT task FROM schedules WHERE day=?',(day,)).fetchone()
            if prior:
                self.db.execute('COMMIT');return {'status':'ALREADY_SCHEDULED','task':prior[0]}
            self.submit(binding)
            self.db.execute('INSERT INTO schedules VALUES(?,?)',(day,binding['id']))
            self.db.execute('COMMIT')
        except BaseException:self.db.execute('ROLLBACK');raise
        return {'status':'SCHEDULED','task':binding['id']}

    def _receipt(self,task,position,binding):
        path=self.root/(task+'-'+str(position)+'.json')
        if not path.exists():return None
        if path.is_symlink():raise ValueError('STAGE_RECEIPT_SYMLINK')
        value=json.loads(path.read_text())
        if set(value)!={'binding','position','output','output_sha256'} or value['binding']!=digest(binding) or value['position']!=position or digest(value['output'])!=value['output_sha256']:raise ValueError('STAGE_RECEIPT_CHANGED')
        text(json.dumps(value));return value

    def recover(self, task, retrieve):
        """Recover only original outcomes through an installed read-only handler.

        Unknown execution stays blocked. Never turn absence into a retry decision.
        """
        with (self.root/'branch.lock').open('a') as lock:
            fcntl.flock(lock,fcntl.LOCK_EX)
            row=self.db.execute('SELECT * FROM tasks WHERE id=?',(task,)).fetchone()
            if not row:raise ValueError('UNKNOWN_TASK')
            binding=json.loads(row['binding'])
            for stage in self.db.execute('SELECT position FROM stages WHERE task=?',(task,)).fetchall():
                position=stage[0]
                if self._receipt(task,position,binding) is not None:continue
                output=retrieve(binding,position)
                if output.get('status')!='COMPLETE':return {'status':'UNCERTAIN_STAGE_RECONCILE_NO_RETRY'}
                value={'binding':digest(binding),'position':position,'output':output,'output_sha256':digest(output)}
                immutable(self.root/(task+'-'+str(position)+'.json'),encoded(value))
            if row['status']!='COMPLETE':
                self.db.execute("UPDATE tasks SET status='QUEUED',reason=NULL WHERE id=?",(task,))
            return {'status':'RECOVERED','model_calls':0}

    def reconcile(self,task):
        with (self.root/'branch.lock').open('a') as lock:
            fcntl.flock(lock,fcntl.LOCK_EX)
            row=self.db.execute('SELECT * FROM tasks WHERE id=?',(task,)).fetchone()
            if not row:raise ValueError('UNKNOWN_TASK')
            binding=json.loads(row['binding'])
            for stage in self.db.execute('SELECT position FROM stages WHERE task=?',(task,)):
                if self._receipt(task,stage[0],binding) is None:
                    return {'status':'UNCERTAIN_STAGE_RECONCILE_NO_RETRY'}
            if row['status']!='COMPLETE':
                self.db.execute("UPDATE tasks SET status='QUEUED',reason=NULL WHERE id=?",(task,))
            return {'status':'RECONCILED','model_calls':0}

    def tick(self):
        with (self.root/'branch.lock').open('a') as lock:
            try:fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
            except BlockingIOError:return {'status':'WRITER_BUSY'}
            if self.status()['paused']:return {'status':'PAUSED'}
            for row in self.db.execute("SELECT * FROM tasks WHERE status IN ('QUEUED','RUNNING') ORDER BY rowid").fetchall():
                task=row['id'];binding=json.loads(row['binding'])
                deps=[self.db.execute('SELECT status FROM tasks WHERE id=?',(d,)).fetchone() for d in binding['dependencies']]
                if any(not d or d[0]!='COMPLETE' for d in deps):
                    self.db.execute("UPDATE tasks SET reason='WAITING_DEPENDENCIES' WHERE id=?",(task,));continue
                with (self.root/'admission.lock').open('a') as gate:
                    fcntl.flock(gate,fcntl.LOCK_EX)
                    if self.status()['paused']:return {'status':'PAUSED'}
                    admitted=self.admission(binding)
                if admitted['status']!='ADMITTED':
                    self.db.execute("UPDATE tasks SET reason=? WHERE id=?",(admitted['status'],task));continue
                for position,handler in enumerate(binding['stages']):
                    prior=self.db.execute('SELECT state FROM stages WHERE task=? AND position=?',(task,position)).fetchone()
                    receipt=self._receipt(task,position,binding)
                    if receipt:
                        self.db.execute("INSERT OR REPLACE INTO stages VALUES(?,?,'COMPLETE',?)",(task,position,digest(receipt)));continue
                    if prior:
                        self.db.execute("UPDATE tasks SET status='BLOCKED',reason='UNCERTAIN_STAGE_RECONCILE_NO_RETRY' WHERE id=?",(task,));break
                    self.db.execute("INSERT INTO stages VALUES(?,?,'STARTED',NULL)",(task,position))
                    self.db.execute("UPDATE tasks SET status='RUNNING',reason=NULL WHERE id=?",(task,))
                    try:
                        output=self.handlers[handler](binding,position)
                        value={'binding':digest(binding),'position':position,'output':output,'output_sha256':digest(output)}
                        immutable(self.root/(task+'-'+str(position)+'.json'),encoded(value))
                    except Exception:
                        self.db.execute("UPDATE tasks SET status='BLOCKED',reason='STAGE_FAILED_OR_UNCERTAIN_PRESERVED' WHERE id=?",(task,));break
                    self.db.execute("UPDATE stages SET state='COMPLETE',receipt=? WHERE task=? AND position=?",(digest(value),task,position))
                else:
                    self.db.execute("UPDATE tasks SET status='COMPLETE',reason=NULL WHERE id=?",(task,))
                return {'status':self.db.execute('SELECT status FROM tasks WHERE id=?',(task,)).fetchone()[0],'task':task}
            return {'status':'WAITING_FOR_ELIGIBLE_WORK'}
