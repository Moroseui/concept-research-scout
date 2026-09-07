"""One bounded supervised Claude worker process survives between input turns.

Transport only: callers must supply reviewed bounded tasks and validate actual MCP
exchanges through the existing validators. A model result is not execution proof.
No automatic restart, reconnect, review role, credential grant or paid fallback.
"""
import hashlib
import json
import os
from pathlib import Path
import queue
import subprocess
import threading
import time
from orchestrator.colab_worker import PRIVATE_CONFIG, private_dir, write_private


class Session:
    def __init__(self, destination, *, synthetic=False):
        self.destination=private_dir(destination)
        self.synthetic=synthetic
        self.submissions=0
        self.pending=False
        self.session_id=None
        self.closed=False
        self.results=queue.Queue()
        self.deadline=time.monotonic()+7200
        self.protocol=(self.destination/'protocol.jsonl').open('x')
        self.stderr=(self.destination/'stderr.log').open('x')
        os.chmod(self.destination/'protocol.jsonl',0o600)
        os.chmod(self.destination/'stderr.log',0o600)
        self.command=['claude','-p','--model','claude-fable-5','--input-format','stream-json',
                      '--output-format','stream-json','--verbose','--strict-mcp-config',
                      '--mcp-config','{"mcpServers":{}}' if synthetic else str(PRIVATE_CONFIG),
                      '--tools','' if synthetic else 'ToolSearch','--permission-mode','dontAsk',
                      '--max-turns','30']
        if not synthetic:self.command += ['--allowedTools','mcp__colab-worker__*']
        self.process=subprocess.Popen(self.command,stdin=subprocess.PIPE,stdout=subprocess.PIPE,
                                      stderr=self.stderr,text=True,cwd=self.destination)
        write_private(self.destination/'started.json',json.dumps({'pid':self.process.pid,'synthetic':synthetic,'max_submissions':3,'max_wall_seconds':7200,'requested_model':'claude-fable-5'}))
        self.reader=threading.Thread(target=self._read,daemon=True);self.reader.start()
        self.timer=threading.Timer(7200,self.close);self.timer.daemon=True;self.timer.start()

    def _read(self):
        try:
            for line in self.process.stdout:
                self.protocol.write(line);self.protocol.flush()
                try:event=json.loads(line)
                except ValueError:continue
                if event.get('type')=='result':
                    os.fsync(self.protocol.fileno());self.results.put(event)
        finally:self.results.put(None)

    def submit(self, request_id, prompt):
        if self.closed or self.process.poll() is not None:raise ValueError('WORKER_ENDED_RECONCILE_NO_RESTART')
        if self.pending:raise ValueError('WORKER_REQUEST_STILL_PENDING')
        if self.submissions>=3 or time.monotonic()>=self.deadline:raise ValueError('WORKER_BOUND_EXHAUSTED')
        if not request_id or any(c not in 'abcdefghijklmnopqrstuvwxyz0123456789-' for c in request_id):raise ValueError('WORKER_REQUEST_ID')
        # Exclusive durable intent before writing: interrupted delivery is uncertain,
        # not permission to submit that request a second time.
        write_private(self.destination/(request_id+'.request.json'),json.dumps({'id':request_id,'prompt_sha256':hashlib.sha256(prompt.encode()).hexdigest(),'submission':self.submissions+1}))
        self.pending=True;self.submissions+=1
        message={'type':'user','message':{'role':'user','content':prompt},'parent_tool_use_id':None}
        self.process.stdin.write(json.dumps(message)+'\n');self.process.stdin.flush()

    def receive(self, timeout=1):
        if not self.pending:raise ValueError('NO_PENDING_WORKER_REQUEST')
        try:event=self.results.get(timeout=timeout)
        except queue.Empty:return None
        if event is None:raise ValueError('WORKER_STREAM_ENDED_OUTCOME_UNCERTAIN')
        sid=event.get('session_id')
        if not sid or (self.session_id and sid!=self.session_id):raise ValueError('WORKER_SESSION_CHANGED')
        self.session_id=sid;self.pending=False
        write_private(self.destination/(f'result-{self.submissions}.json'),json.dumps(event))
        return {'status':'TURN_RETURNED' if event.get('subtype')=='success' and not event.get('is_error') else 'TURN_FAILED',
                'session_id':sid,'submission':self.submissions,'process_alive':self.process.poll() is None,
                'execution_proven':False}

    def close(self):
        if self.closed:return
        self.closed=True
        if hasattr(self,'timer'):self.timer.cancel()
        if self.process.poll() is None:
            self.process.stdin.close()
            try:self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.terminate()
                try:self.process.wait(timeout=5)
                except subprocess.TimeoutExpired:self.process.kill();self.process.wait()
        self.reader.join(timeout=2)
        self.protocol.close();self.stderr.close()
