"""Bounded non-patient readiness scheduling over the existing durable Store.

One controller holds the branch lock. Fixed read-only handlers can overlap across
primary/adjacent threads; no model, patient, Git writer or arbitrary command handler.
Crashes leave RUNNING tasks uncertain until their immutable result is reconciled.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
from pathlib import Path
import time
from orchestrator.job_store import Store
from orchestrator.remote_supervisor import identifier, lock, checked_source
from orchestrator.hosted_cycle import immutable, encoded

HANDLERS = {
    'context_inventory': ['orchestrator/campaign_pipeline.py', 'orchestrator/prompts/scout.md',
                          'docs/SCORING_RUBRIC.md', 'evidence/cross_charter_index.md'],
    'baseline_inventory': ['campaigns/isles24-pilot/experiments/P001/SPEC.md',
                           'campaigns/isles24-pilot/experiments/P001/run.py',
                           'campaigns/isles24-pilot/experiments/P001/review.json',
                           'docs/isles-pilot/ARCHIVE_PRESERVATION_VERIFIED_20260906.json'],
    'phase_b_inventory': ['docs/isles-pilot/047_LIFECYCLE.md', 'ideas/047/registry.yaml',
                          'ideas/047/interpretation.md'],
    'slow_synthetic': [],
}

class ReadinessQueue(Store):
    def add(self, name, binding):
        identifier(name)
        if set(binding) != {'source','thread','handler','dependencies','gates','seconds','parent'}:
            raise ValueError('BINDING_SCHEMA')
        if binding['thread'] not in ('primary','adjacent') or binding['handler'] not in HANDLERS:
            raise ValueError('HANDLER_OR_THREAD')
        if type(binding['seconds']) is not int or not 0 <= binding['seconds'] <= 90:
            raise ValueError('TIME_LIMIT')
        for key in ('dependencies','gates'):
            if not isinstance(binding[key],list): raise ValueError('DEPENDENCY_SCHEMA')
            for item in binding[key]: identifier(item)
        identifier(binding['parent'])
        if name in binding['dependencies']: raise ValueError('SELF_DEPENDENCY')
        if len(binding['source']) != 40 or any(c not in '0123456789abcdef' for c in binding['source']):
            raise ValueError('SOURCE_PIN')
        if self.db.execute('SELECT count(*) FROM jobs').fetchone()[0] >= 32 and not self.db.execute('SELECT 1 FROM jobs WHERE id=?',(name,)).fetchone():
            raise ValueError('BOUNDED_QUEUE_LIMIT')
        self.register(name,binding)
        self.db.execute("UPDATE jobs SET phase='readiness' WHERE id=? AND phase='acquisition'",(name,))

    def accept(self, name, result):
        text=json.dumps(result,sort_keys=True)
        self.db.execute('BEGIN IMMEDIATE')
        try:
            row=self.get(name)
            if result['binding'] != json.loads(row['binding']) or result['job'] != name: raise ValueError('RESULT_BINDING')
            old=self.db.execute('SELECT payload FROM events WHERE id=?',(name,)).fetchone()
            if old:
                if old[0]!=text: raise ValueError('CONFLICTING_COMPLETION')
                self.db.execute('COMMIT'); return False
            if row['status'] not in ('RUNNING','BLOCKED'): raise ValueError('UNCLAIMED_RESULT')
            self.db.execute('INSERT INTO events VALUES(?,?,?)',(name,name,text))
            self.db.execute("UPDATE jobs SET status='COMPLETE',lease=0 WHERE id=?",(name,))
            self.db.execute("UPDATE inbox SET status='RESOLVED' WHERE job=?",(name,))
            self.db.execute('COMMIT'); return True
        except BaseException:
            self.db.execute('ROLLBACK'); raise

    def candidates(self, active):
        rows=[dict(r) for r in self.db.execute('SELECT * FROM jobs ORDER BY id')]
        statuses={r['id']:r['status'] for r in rows}
        busy={json.loads(r['binding'])['thread'] for r in rows if r['id'] in active}
        choices=[]
        for r in rows:
            b=json.loads(r['binding'])
            if r['status']!='READY': continue
            if b['gates']:
                self.block(r['id'],'REQUIRES_'+'_'.join(b['gates'])); continue
            missing=[d for d in b['dependencies'] if statuses.get(d)!='COMPLETE']
            if missing:
                self.db.execute("INSERT OR REPLACE INTO inbox VALUES(?,?,'OPEN')",(r['id'],'WAIT_DEPENDENCIES_'+','.join(missing)))
                continue
            self.db.execute("UPDATE inbox SET status='RESOLVED' WHERE job=? AND reason LIKE 'WAIT_DEPENDENCIES_%'",(r['id'],))
            if b['thread'] in busy: continue
            choices.append(r); busy.add(b['thread'])
        return choices


def artifact(root, name, binding):
    start=time.time()
    if binding['handler']=='slow_synthetic': time.sleep(binding['seconds'])
    facts=[]
    for relative in HANDLERS[binding['handler']]:
        p=root/relative
        if p.is_symlink() or not p.resolve().is_relative_to(root): raise ValueError('UNSAFE_SOURCE')
        facts.append({'source':relative,'status':'PRESENT' if p.is_file() else 'MISSING',
                      'sha256':hashlib.sha256(p.read_bytes()).hexdigest() if p.is_file() else None})
    return {'job':name,'binding':binding,'started':start,'finished':time.time(),
            'facts':facts,'scope':'METADATA_ONLY_NOT_SCIENTIFIC_VALIDATION',
            'next_action':{'context_inventory':'Review scoped prompt and evidence dependencies',
                           'baseline_inventory':'Resolve charter adoption and separate launch gates',
                           'phase_b_inventory':'Resolve original successful console and disposition gates',
                           'slow_synthetic':'Process completion once and reconsider eligible tasks'}[binding['handler']]}


def run(root, source, state):
    root=checked_source(root,source); state=Path(state); state.mkdir(parents=True,exist_ok=True)
    with lock(state/'branch.lock'):
        q=ReadinessQueue(state/'readiness.sqlite')
        # Reconcile first. A missing receipt is uncertainty, never permission to replay.
        for r in q.db.execute('SELECT * FROM jobs').fetchall():
            if json.loads(r['binding'])['source']!=source: raise ValueError('MIXED_SOURCE_QUEUE')
            path=state/r['id']/'result.json'
            if path.exists():
                if path.is_symlink(): raise ValueError('RESULT_SYMLINK')
                value=json.loads(path.read_text())
                if value!=artifact_projection(value): raise ValueError('RESULT_SCHEMA')
                attempt=state/r['id']/'attempt.json'
                if attempt.is_symlink() or not attempt.is_file(): raise ValueError('ATTEMPT_REQUIRED')
                bound=json.loads(attempt.read_text())
                if bound.get('job')!=r['id'] or bound.get('binding')!=json.loads(r['binding']): raise ValueError('ATTEMPT_BINDING')
                expected=artifact(root,r['id'],dict(json.loads(r['binding']),seconds=0))
                if any(value[k]!=expected[k] for k in ('job','facts','scope','next_action')): raise ValueError('RESULT_CONTENT_CHANGED')
                q.accept(r['id'],value)
            elif r['status']=='RUNNING' or (state/r['id']).exists(): q.block(r['id'],'UNCERTAIN_ATTEMPT_RECONCILE_NO_AUTOMATIC_RETRY')
        active={}
        with ThreadPoolExecutor(max_workers=2) as workers:
            while True:
                for r in q.candidates(active):
                    name=r['id']; folder=state/name
                    if not q.claim(name): continue
                    try: folder.mkdir(mode=0o700,exist_ok=False)
                    except FileExistsError:
                        q.block(name,'UNCERTAIN_ATTEMPT_RECONCILE_NO_AUTOMATIC_RETRY'); continue
                    binding=json.loads(r['binding'])
                    immutable(folder/'attempt.json',encoded({'job':name,'binding':binding,'limits':{'threads':1,'max_seconds':90,'patient':False,'model_calls':0}}))
                    active[name]=workers.submit(artifact,root,name,binding)
                if not active: break
                for name,future in list(active.items()):
                    if not future.done(): continue
                    try:
                        result=future.result()
                        immutable(state/name/'result.json',encoded(result)); q.accept(name,result)
                    except Exception:
                        q.block(name,'HANDLER_FAILED_INSPECT_PRIVATE_ATTEMPT_NO_AUTOMATIC_RETRY')
                    del active[name]
                time.sleep(.05)
        result={'source':source,'jobs':[dict(r) for r in q.db.execute('SELECT id,status FROM jobs ORDER BY id')],
                'processed_events':q.db.execute('SELECT count(*) FROM events').fetchone()[0],
                'inbox':q.inbox(),'patient_execution':False,'standing_activation':False}
        q.db.close(); return result


def artifact_projection(value):
    return {k:value[k] for k in ('job','binding','started','finished','facts','scope','next_action')}

if __name__=='__main__':
    p=argparse.ArgumentParser(); p.add_argument('--root',type=Path,required=True); p.add_argument('--source',required=True)
    p.add_argument('--state',type=Path,required=True); p.add_argument('--manifest',type=Path)
    a=p.parse_args()
    if a.manifest:
        a.state.mkdir(parents=True,exist_ok=True)
        with lock(a.state/'branch.lock'):
            q=ReadinessQueue(a.state/'readiness.sqlite')
            for item in json.loads(a.manifest.read_text())['tasks']: q.add(item['id'],dict(item['binding'],source=a.source))
            q.db.close()
    print(json.dumps(run(a.root,a.source,a.state),indent=2))
