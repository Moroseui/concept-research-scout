"""One counted author correction; reuse the existing visible-only feedback."""
from pathlib import Path
import json
from orchestrator import colab_arm_question as q, private_records as pr
DOCUMENT='docs/COLAB_PNORMCT_FORMAT_FAILURE_PRIVATE.json'
DOCUMENT_SHA='058c265895fb940fbe86e6c66aa35eb69a33441e06974f9dfa7282dface63c87'
CALL='4472488332a48db75f4ba0d75c7e80f2e1a74ff8e77acf36a0a65fbf6272b116'
EVENT='pnormct-author1-format-correction'
REASON='OUTPUT_VALIDATION_REFUSED: NOTEBOOK_PATCH_EDIT_FIELDS'
RUNTIME='.colab-feedback'

def document(root):
    raw=pr.check(Path(root)/DOCUMENT).read_bytes()
    q.require(q.sha(raw)==DOCUMENT_SHA,'FORMAT_CHECKPOINT')
    f=json.loads(raw)
    q.require(f['schema']=='pnormct-author1-format/v1' and f['run_id']==q.RUN
        and f['call_id']==CALL and f['next_author']==2 and f['new_allowance']==0
        and len(f['local_calls'])==1,'FORMAT_SCOPE')
    return f

def check(driver,f,initial=False):
    q.require(driver.config['run_id']==q.RUN and str(driver.state)==f['lane']
        and q.sha(pr.check(driver.state/'lane.json').read_bytes())==f['config_sha256'],'FORMAT_LANE')
    q.validate(driver.store,q.RUN)
    for db,table,expected in [(driver.store.db,'manual_calls',f['local_calls'][0]),
                              (driver.store.batch.db,'autonomy_calls',f['global_row'])]:
        row=db.execute('SELECT * FROM '+table+' WHERE id=?',(CALL,)).fetchone()
        q.require(row is not None and dict(row)==expected and row['status']=='COMPLETE','FORMAT_ORIGINAL_CALL')
    q.require(not driver.store.db.execute('SELECT 1 FROM events WHERE id=?',('author-accepted:'+CALL,)).fetchone(),'FORMAT_ALREADY_ACCEPTED')
    work=Path(f['workspace'])
    for name,pin in f['files'].items():
        raw=pr.check(work/name).read_bytes()
        q.require(q.sha(raw)==pin['sha256'] and len(raw)==pin['bytes'],'FORMAT_ORIGINAL_OUTPUT')
    patch=json.loads(pr.check(work/'notebook.patch.json').read_bytes())
    q.require(all(isinstance(e['replacement'],list) and all(isinstance(s,str)for s in e['replacement']) for e in patch['edits']),'FORMAT_DIAGNOSED_CAUSE')
    q.require(not (work/'.author-submission.json').exists(),'FORMAT_SUBMISSION_EXISTS')
    if initial:
        q.require(dict(driver.store.db.execute('SELECT * FROM manual_state WHERE id=1').fetchone())==f['state_row']
            and dict(driver.store.db.execute('SELECT * FROM manual_account WHERE id=1').fetchone())==f['account_row']
            and driver.store.db.execute('SELECT count(*) FROM manual_calls').fetchone()[0]==1
            and not driver.store.batch.db.execute("SELECT 1 FROM autonomy_calls WHERE status='RUNNING'").fetchone(),'FORMAT_INITIAL_STATE')
    return True

def restored(value,f):
    q.require(value==json.loads(f['state_row']['payload']) and value['phase']=='BLOCKED'
        and value['reason']==REASON and value['pending']['id']==CALL
        and value['pending']['stage']=='run_spec_author' and value['pending']['round']==1,'FORMAT_EXACT_REFUSAL')
    result=json.loads(json.dumps(value));result.pop('pending')
    result.update(phase='run_spec_author',reason=EVENT)
    return result

def recover(driver,f,approval):
    check(driver,f,initial=True)
    q.require(not (driver.state/'HALT').exists() and not (driver.store.batch.folder/'HALT').exists(),'FORMAT_HALT')
    before=driver.current();after=restored(before,f);dest=driver.state/EVENT
    q.require(not dest.exists() and not dest.is_symlink(),'FORMAT_ALREADY_ATTEMPTED')
    grant={'kind':EVENT,'review_sha256':approval,'checkpoint_sha256':DOCUMENT_SHA,
           'failed_call':CALL,'model_calls':0,'new_allowance':0,'preserved_calls':1}
    pr.mkdir(dest);pr.write_bytes(dest/'original-state.json',f['state_row']['payload'].encode())
    pr.write_bytes(dest/'intent.json',q.encoded(grant))
    after['interventions'].append(grant)
    db=driver.store.db;db.execute('BEGIN IMMEDIATE')
    try:
        check(driver,f,initial=True)
        db.execute('INSERT INTO events VALUES(?,?,?)',(EVENT,q.RUN,q.encoded(grant).decode()))
        db.execute('UPDATE manual_state SET payload=? WHERE id=1',(json.dumps(after,sort_keys=True),))
        db.execute('COMMIT')
    except BaseException:db.execute('ROLLBACK');raise
    pr.write_bytes(dest/'COMPLETE.json',q.encoded(grant))
    return {'status':'READY_COUNTED_AUTHOR2','model_calls':0,'new_allowance':0,'calls_preserved':1}

def feedback_files(driver,f):
    from orchestrator import notebook_revision as nr, colab_preparation_scope as scope
    from orchestrator import scientific_intake as intake, colab_static_feedback as existing
    cfg=driver.config['notebook_revision']
    original,selection=scope.validate_notebook_config(driver.context,cfg)
    registry=json.loads(nr.bound(driver.context,driver.config['private_intake']))
    cases=intake.cohort((driver.context/registry['cohort']).read_bytes())
    view,manifest=nr.partition(original,selection,cases,nr.VIEW)
    bodies={'check.py':existing.CHECKER.encode(),'orchestrator/__init__.py':b'',
        **{'orchestrator/'+name+'.py':raw for name,raw in existing.runtime_libraries().items()},
        'view.txt':view,'manifest.json':q.encoded(manifest),
        'binding.json':q.encoded({'run_id':q.RUN,'analysis_registry_sha256':driver.config['private_intake']['sha256'],
            'original_sha256':nr.ORIGINAL,'view_sha256':nr.VIEW})}
    for name in ('SPEC.proposed.md','notebook.patch.json'):
        bodies['previous-'+name]=pr.check(Path(f['workspace'])/name).read_bytes()
    for raw in bodies.values():nr.scan(raw,cases)
    return {RUNTIME+'/'+name:raw for name,raw in bodies.items()}

def task(files):
    refs='\n'.join(name+' sha256='+q.sha(raw) for name,raw in files.items())
    return ('\nCOUNTED PNORMCT FORMAT CORRECTION. Your preserved author1 draft was not accepted: '
        'every replacement is an array, but safe-notebook-patch/v1 requires replacement to be a STRING. '
        'You, the scientific author, correct the preserved outputs. Retain their scientific code/design; '
        'make any additional corrections required by the existing validators explicitly. The operator '
        'has not converted or edited your outputs. Do not start the notebook over or reauthor unrelated arms. '
        'Exact edit fields/types: unit:string matching cells/<integer>/source; start:integer byte offset; '
        'end:integer byte offset, start<end; before_sha256:64 lowercase hex string; replacement:STRING '
        '(empty string for deletion, never [] or list-of-lines). No extra fields. Patch the same original. '
        'The complete schema/visible reconstruction checker below is available through ordinary exec. '
        'This route has FILE-BASED submission; there is no submit_author MCP tool here. Supersede that '
        'stale sentence in the original task. Do not invent a submission receipt. '
        'Run python3 -I -B .colab-feedback/check.py after writing BOTH outputs; read each error, correct '
        'and rerun within this SAME call, at most12 local iterations. Patch<=80000bytes; SPEC<=12000characters. '
        'The checker performs no scientific execution and cannot approve science. Do not modify checker '
        'or its bound inputs. The host still performs exact privacy/schema/synthetic checks and independent '
        'scientific review. If unavailable tests were not run, state that plainly. No real patient/provider '
        'execution or credentials. All initial guards, model limits and caps remain. Bound feedback files:\n'+refs+'\n')

def corrected(base,root,approval):
    f=document(root)
    class Corrected(base):
        def prepare_input(self,value,stage,work):
            if self.config.get('run_id')!=q.RUN or stage!='run_spec_author':
                return super().prepare_input(value,stage,work)
            check(self,f)
            self._pnormct_feedback=feedback_files(self,f)
            try:body,measurement=super().prepare_input(value,stage,work)
            finally:self.__dict__.pop('_pnormct_feedback',None)
            refs=[]
            for name,raw in feedback_files(self,f).items():
                target=Path(work)/name;pr.mkdir(target.parent,parents=True,exist_ok=True)
                q.require(not target.exists() and not target.is_symlink(),'FORMAT_FEEDBACK_EXISTS')
                pr.write_bytes(target,raw);target.chmod(0o400)
                refs.append({'path':name,'sha256':q.sha(raw),'bytes':len(raw)})
            return body,{**measurement,'workspace_files':[*measurement['workspace_files'],*refs]}
        def task(self,stage,value):
            text=super().task(stage,value)
            return text+task(self._pnormct_feedback) if hasattr(self,'_pnormct_feedback')else text
    return Corrected
