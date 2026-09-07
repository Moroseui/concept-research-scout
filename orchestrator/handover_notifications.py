"""Protected notification-only delivery; replies never become operating authority.

Uses the existing installed App and checked outbox. One immutable packet per key,
three bounded attempts, no automatic repost after uncertain API delivery. Failure
is a durable notification block, not a reason to refund or stop admission 48.
"""
import hashlib
import json
import sqlite3
import time

from orchestrator.operations_report import private_root,immutable
from orchestrator.phone_notifications import Outbox,config_checked,protected_read,jwt,session


class Notices:
    def __init__(self,root,config_path):
        self.root=private_root(root);self.config_path=config_path
        self.db=sqlite3.connect(self.root/'delivery.sqlite',isolation_level=None,timeout=30)
        self.db.row_factory=sqlite3.Row
        from orchestrator.remote_supervisor import lock
        with lock(self.root/'delivery.lock'):
            self.db.execute('CREATE TABLE IF NOT EXISTS deliveries(id TEXT PRIMARY KEY,summary TEXT,status TEXT,attempts INTEGER,issue INTEGER,reason TEXT)')
            if 'reason' not in {row[1] for row in self.db.execute('PRAGMA table_info(deliveries)')}:
                self.db.execute('ALTER TABLE deliveries ADD COLUMN reason TEXT')

    def send(self,key,source,summary):
        from orchestrator.remote_supervisor import lock
        with lock(self.root/'delivery.lock'):
            return self._send(key,source,summary)

    def _send(self,key,source,summary):
        identity=hashlib.sha256(key.encode()).hexdigest()
        row=self.db.execute('SELECT * FROM deliveries WHERE id=?',(identity,)).fetchone()
        if row and row['summary']!=summary:raise ValueError('NOTICE_IDENTITY_CHANGED')
        if row and row['status']=='SENT':return dict(row)
        if row and row['attempts']>=3:
            self.db.execute("UPDATE deliveries SET status='BLOCKED',reason=coalesce(reason,'ATTEMPT_LIMIT_RECONCILE_ORIGINAL_OUTBOX') WHERE id=?",(identity,))
            return dict(self.db.execute('SELECT * FROM deliveries WHERE id=?',(identity,)).fetchone())
        c=config_checked(json.loads(protected_read(self.config_path)))
        if c['mode']!='NOTIFICATION_ONLY':raise ValueError('NOTIFICATION_ONLY_CONFIGURATION_REQUIRED')
        packet_path=self.root/(identity+'.packet.json')
        if packet_path.exists():packet=json.loads(packet_path.read_text())
        else:
            packet={'id':'system-'+identity[:32],'source':source,'nonce':identity[:32],
                    'expires':int(time.time())+86400,'summary':summary}
            immutable(packet_path,(json.dumps(packet,sort_keys=True)+'\n').encode())
        attempts=(row['attempts'] if row else 0)+1
        self.db.execute('INSERT OR REPLACE INTO deliveries VALUES(?,?,?, ?,NULL,NULL)',(identity,summary,'PENDING',attempts))
        try:
            token,observed=session(c,jwt(c))
            immutable(self.root/'verified-identities.json',(json.dumps(observed,sort_keys=True)+'\n').encode())
            result=Outbox(self.root).send(packet,c,token)
            self.db.execute("UPDATE deliveries SET status='SENT',issue=? WHERE id=?",(result['issue'],identity))
        except Exception as error:
            # Preserve original outbox UNCERTAIN; never invent delivery or repost.
            import re
            # Never copy provider responses, credentials or arbitrary exception prose.
            code=str(error) if isinstance(error,ValueError) else ''
            reason=code if re.fullmatch('[A-Z0-9_]{1,80}',code) else 'NOTICE_TRANSPORT_OR_IDENTITY_RECONCILIATION_REQUIRED'
            self.db.execute('UPDATE deliveries SET status=?,reason=? WHERE id=?',('BLOCKED' if attempts>=3 else 'RETRY',reason,identity))
        return dict(self.db.execute('SELECT * FROM deliveries WHERE id=?',(identity,)).fetchone())
