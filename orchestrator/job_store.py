"""Durable job state, deduplicated events, leases, and a human decision inbox."""
import hashlib
import json
from pathlib import Path
import sqlite3
import time


class Store:
    def __init__(self,path):
        self.db=sqlite3.connect(path,timeout=30,isolation_level=None)
        self.db.row_factory=sqlite3.Row
        self.db.executescript('''PRAGMA journal_mode=WAL;
        CREATE TABLE IF NOT EXISTS jobs(id TEXT PRIMARY KEY, binding TEXT NOT NULL,
          phase TEXT NOT NULL, status TEXT NOT NULL, retries INTEGER NOT NULL DEFAULT 0,
          lease REAL NOT NULL DEFAULT 0, due REAL NOT NULL DEFAULT 0);
        CREATE TABLE IF NOT EXISTS events(id TEXT PRIMARY KEY, job TEXT NOT NULL, payload TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS inbox(job TEXT PRIMARY KEY, reason TEXT NOT NULL, status TEXT NOT NULL);
        ''')

    def register(self,job,binding):
        text=json.dumps(binding,sort_keys=True)
        old=self.db.execute('SELECT binding FROM jobs WHERE id=?',(job,)).fetchone()
        if old and old[0]!=text:raise ValueError('job identity already binds different inputs')
        self.db.execute("INSERT OR IGNORE INTO jobs(id,binding,phase,status) VALUES(?,?,'acquisition','READY')",(job,text))

    def get(self,job):return dict(self.db.execute('SELECT * FROM jobs WHERE id=?',(job,)).fetchone())

    def claim(self,job,now=None):
        now=time.time() if now is None else now
        self.db.execute('BEGIN IMMEDIATE')
        try:
            r=self.get(job)
            if r['status']=='RUNNING' and r['lease']<=now:
                if r['phase']=='dispatch':
                    self.block(job,'AMBIGUOUS_DISPATCH_CHECK_REMOTE_BEFORE_RETRY')
                    self.db.execute('COMMIT');return None
                if r['retries']>=2:
                    self.block(job,'READ_ONLY_RETRY_LIMIT')
                    self.db.execute('COMMIT');return None
                self.db.execute("UPDATE jobs SET status='READY',retries=retries+1 WHERE id=?",(job,))
                r=self.get(job)
            if r['status']!='READY' or r['due']>now:
                self.db.execute('COMMIT');return None
            self.db.execute("UPDATE jobs SET status='RUNNING',lease=? WHERE id=?",(now+900,job))
            self.db.execute('COMMIT');return self.get(job)
        except BaseException:
            self.db.execute('ROLLBACK');raise

    def block(self,job,reason):
        self.db.execute("UPDATE jobs SET status='BLOCKED',lease=0 WHERE id=?",(job,))
        self.db.execute("INSERT OR REPLACE INTO inbox VALUES(?,?,'OPEN')",(job,reason))

    def complete_event(self,job,event_id,result,now=None,*,lease=None):
        now=time.time() if now is None else now
        # Callers submit a fixed enum, never raw tool output or patient data.
        allowed={'RUNNING','VALIDATED','DISPATCHED','TRANSIENT','FAILED','AUTH','PERMISSION','NOT_VISIBLE'}
        if result not in allowed:raise ValueError('unknown result')
        payload=json.dumps({'job':job,'result':result},sort_keys=True)
        self.db.execute('BEGIN IMMEDIATE')
        try:
            old=self.db.execute('SELECT payload FROM events WHERE id=?',(event_id,)).fetchone()
            if old:
                if old[0]!=payload:raise ValueError('duplicate event identity conflicts')
                self.db.execute('COMMIT');return
            r=self.get(job)
            if r['status']!='RUNNING':raise ValueError('event has no claimed task')
            if lease is None or lease!=r['lease']:raise ValueError('stale lease cannot complete a recovered task')
            self.db.execute('INSERT INTO events VALUES(?,?,?)',(event_id,job,payload))
            phase=r['phase'];status='READY';retries=r['retries'];due=now+300
            if result=='TRANSIENT' and phase!='dispatch' and retries<2:retries+=1
            elif result in ['TRANSIENT','FAILED','AUTH','PERMISSION','NOT_VISIBLE']:
                self.block(job,'AMBIGUOUS_DISPATCH_CHECK_REMOTE_BEFORE_RETRY' if phase=='dispatch' else result)
                self.db.execute('COMMIT');return
            elif phase=='acquisition' and result=='VALIDATED':phase='dispatch';due=now;retries=0
            elif phase=='dispatch' and result=='DISPATCHED':phase='patient';due=now;retries=0
            elif phase=='patient' and result=='VALIDATED':
                self.block(job,'PRIVATE_RETURN_TRANSFER_REQUIRED')
                self.db.execute('COMMIT');return
            elif result!='RUNNING' or phase=='dispatch':raise ValueError('invalid phase transition')
            self.db.execute('UPDATE jobs SET phase=?,status=?,retries=?,lease=0,due=? WHERE id=?',(phase,status,retries,due,job))
            self.db.execute('COMMIT')
        except BaseException:self.db.execute('ROLLBACK');raise

    def inbox(self):return [dict(r) for r in self.db.execute('SELECT * FROM inbox ORDER BY job')]
