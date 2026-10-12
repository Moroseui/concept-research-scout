"""In-call static feedback plus one counted Colab author correction.

No scientific source edits, new model allowance, scientific acceptance or compute.
The unchanged controller still applies privacy checks, synthetic tests and review.
"""
from pathlib import Path
import hashlib, json, os

CALL='b725315292f41c63bbde2c4bae76cf059e82eb06f0039adb6ee8a63da3d35657'
RUN='colab-1ad5fafc220b3d65f576ce08'
DOCUMENT='docs/COLAB_AUTHOR5_STATIC_PRIVATE.json'
DOCUMENT_SHA='7fe6d72085d054835f72d0d9a3195c95cb3817a35f9565eabf99e1afdb9c6715'
REASON='OUTPUT_VALIDATION_REFUSED: NOTEBOOK_EXECUTION_ENTRYPOINT:main'
EVENT='colab-author5-counted-static-correction'
RUNTIME='.colab-feedback'
LIBRARIES=('author_output_schema','experiment_plan_validation','experiment_environment_requirements',
           'modal_billing','notebook_execution','scientific_view_scan','privacy_patterns')
sha=lambda raw:hashlib.sha256(raw).hexdigest()
canonical=lambda v:json.dumps(v,sort_keys=True,separators=(',',':'),allow_nan=False).encode()

def require(ok,why):
    if not ok:raise ValueError('COLAB_STATIC_'+why)

def frozen(root):
    raw=(Path(root)/DOCUMENT).read_bytes()
    require(sha(raw)==DOCUMENT_SHA,'FROZEN_PROOF_CHANGED')
    return json.loads(raw)

def check_originals(driver,b,*,initial=False):
    """Never rewrite a call, account, owner, allowance or configuration."""
    from orchestrator import private_records as pr
    require(driver.config['run_id']==RUN,'RUN')
    root=driver.state.parent
    for name,pin in b['files'].items():
        require(sha(pr.check(root/name).read_bytes())==pin,'ORIGINAL_FILE_CHANGED')
    for table,key,db in [('manual_calls','local',driver.store.db),('autonomy_calls','global',driver.store.batch.db)]:
        row=db.execute('SELECT * FROM '+table+' WHERE id=?',(CALL,)).fetchone()
        require(row is not None and dict(row)==b['records'][key] and row['status']=='COMPLETE','ORIGINAL_CALL_CHANGED')
    for row in b['calls']:
        current=driver.store.db.execute('SELECT * FROM manual_calls WHERE id=?',(row['id'],)).fetchone()
        require(current is not None and dict(current)==row,'HISTORICAL_CALL_CHANGED')
    if initial:
        require(driver.store.db.execute('SELECT count(*) FROM manual_calls').fetchone()[0]==len(b['calls']),'NEW_ADMISSION')
        require(dict(driver.store.db.execute('SELECT * FROM manual_account WHERE id=1').fetchone())==b['account_row'],'ACCOUNT_CHANGED')
        require(dict(driver.store.db.execute('SELECT * FROM manual_state WHERE id=1').fetchone())==b['state_row'],'STATE_CHANGED')
        require(not driver.store.batch.db.execute("SELECT 1 FROM autonomy_calls WHERE status='RUNNING'").fetchone(),'LIVE_CALL')
    from orchestrator import notebook_execution as execution
    raw=pr.check(root/'lane/notebook-revisions/author-5/revised.ipynb').read_bytes()
    try:execution.extract(raw,preprocessing=True)
    except ValueError as error:require(str(error)=='NOTEBOOK_EXECUTION_ENTRYPOINT:main','DIFFERENT_FAILURE')
    else:raise ValueError('COLAB_STATIC_FAILURE_NOT_REPRODUCED')

def restored(value,approval):
    require(value['phase']=='BLOCKED' and value['reason']==REASON and
            value['pending']['id']==CALL and value['pending']['stage']=='run_spec_author' and
            value['pending']['round']==5,'EXACT_STATIC_BLOCK')
    result=json.loads(json.dumps(value))
    result.update(phase='run_spec_author',reason=EVENT)
    result.pop('pending')
    result['interventions'].append({'kind':EVENT,'failed_call':CALL,'proof_sha256':DOCUMENT_SHA,
        'implementation_review_sha256':approval,'scientific_acceptance':False,
        'reviewer_revise':False,'new_allowance':0})
    return result

def resume(driver,b,approval):
    """Caller holds original driver lock; exclusive intent, transactional CAS."""
    from orchestrator import private_records as pr
    require(isinstance(approval,str) and len(approval)==64 and all(c in '0123456789abcdef' for c in approval),'APPROVAL')
    require(not (driver.state/'HALT').exists() and not (Path(driver.config['batch_ledger'])/'HALT').exists(),'HALT')
    check_originals(driver,b,initial=True)
    before=b['state_row']['payload'];after=restored(json.loads(before),approval)
    dest=driver.state/EVENT
    require(not dest.exists() and not dest.is_symlink(),'RECOVERY_ALREADY_ATTEMPTED')
    pr.mkdir(dest)
    pr.write_bytes(dest/'original-rows.json',canonical(b))
    record={'proof_sha256':DOCUMENT_SHA,'review_sha256':approval,'new_calls':0,'new_allowance':0,
            'before_state_sha256':sha(before.encode()),'after_state_sha256':sha(canonical(after))}
    pr.write_bytes(dest/'INTENT.json',canonical(record))
    db=driver.store.db
    db.execute('BEGIN IMMEDIATE')
    try:
        check_originals(driver,b,initial=True)
        require(not db.execute('SELECT 1 FROM events WHERE id=?',(EVENT,)).fetchone(),'RECOVERY_EVENT_EXISTS')
        db.execute('INSERT INTO events VALUES(?,?,?)',(EVENT,RUN,canonical(record).decode()))
        db.execute('UPDATE manual_state SET payload=? WHERE id=1',(json.dumps(after,sort_keys=True),))
        db.execute('COMMIT')
    except BaseException:
        db.execute('ROLLBACK');raise
    pr.write_bytes(dest/'COMPLETE.json',canonical(record))
    require(driver.current()==after,'READBACK')
    return {'status':'READY_COUNTED_AUTHOR6','calls_preserved':len(b['calls']),'new_calls':0,'new_allowance':0}

CHECKER = '''"""Supplementary visible-only feedback; never execute authored source."""
from pathlib import Path
import hashlib,json,sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from orchestrator.author_output_schema import patch,visible_module
def strict(raw):
 def pairs(rows):
  d={}
  for k,v in rows:
   if k in d:raise ValueError("DUPLICATE_KEY")
   d[k]=v
  return d
 return json.loads(raw,object_pairs_hook=pairs,parse_constant=lambda v:(_ for _ in ()).throw(ValueError("NONFINITE")))
def check(root):
 root=Path(root);runtime=Path(__file__).resolve().parent
 cfg=strict((runtime/"binding.json").read_bytes())
 raw=(root/"notebook.patch.json").read_bytes()
 if len(raw)>80000:raise ValueError("PATCH_LIMIT_80000")
 value=strict(raw);patch(value,cfg)
 module=visible_module(value,(runtime/"view.txt").read_bytes(),strict((runtime/"manifest.json").read_bytes()))
 spec=(root/"SPEC.proposed.md").read_text()
 if len(spec)>12000:raise ValueError("SPEC_LIMIT_12000_CHARACTERS")
 for key in ("run_id","analysis_registry_sha256"):
  if [line for line in spec.splitlines() if line.startswith(key+":")]!=[key+": "+cfg[key]]:raise ValueError("SPEC_BINDING")
 return {"status":"FORMAT_PASS_NOT_SCIENTIFIC_APPROVAL","module_sha256":module,
         "files":{n:hashlib.sha256((root/n).read_bytes()).hexdigest() for n in ("SPEC.proposed.md","notebook.patch.json")}}
if __name__=="__main__":
 try:print(json.dumps(check(Path.cwd()),sort_keys=True))
 except (ValueError,KeyError,TypeError,OSError,SyntaxError) as error:
  print(json.dumps({"status":"CORRECT_AND_RERUN_IN_SAME_CALL","error":str(error)}));sys.exit(1)
'''

def runtime_libraries():
    """Ship only the opaque-payload helpers used by visible_module.

    Copy original AST source spans byte-for-byte. The unused secret-detection
    patterns are not dependencies of this checker and trigger the intake scanner
    when delivered as code. Full host privacy scanning remains unchanged.
    """
    import ast
    from orchestrator import author_output_schema
    libs=Path(author_output_schema.__file__).parent
    bodies={name:(libs/(name+'.py')).read_bytes()for name in LIBRARIES}
    raw=bodies['scientific_view_scan'].decode()
    tree=ast.parse(raw);lines=raw.splitlines(keepends=True)
    wanted=[]
    for node in tree.body:
        keep=(isinstance(node,ast.Import) and [a.name for a in node.names] in [['html'],['re']]
            or isinstance(node,ast.ImportFrom) and node.module=='urllib.parse'
            or isinstance(node,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='OPAQUE' for t in node.targets)
            or isinstance(node,ast.FunctionDef) and node.name in {'text_variants','reject_opaque'})
        if keep:wanted.append(''.join(lines[node.lineno-1:node.end_lineno]))
    require(len(wanted)==6,'OPAQUE_DEPENDENCY_SOURCE_SHAPE')
    bodies['scientific_view_scan']='\n'.join(wanted).encode()
    return bodies

def feedback_files(driver,b):
    from orchestrator import notebook_revision as nr,colab_preparation_scope as scope
    from orchestrator import scientific_intake as intake
    cfg=driver.config['notebook_revision']
    original,selection=scope.validate_notebook_config(driver.context,cfg)
    registry=json.loads(nr.bound(driver.context,driver.config['private_intake']))
    cases=intake.cohort((driver.context/registry['cohort']).read_bytes())
    view,manifest=nr.partition(original,selection,cases,nr.VIEW)
    libs=Path(nr.__file__).parent
    bodies={'check.py':CHECKER.encode(),'orchestrator/__init__.py':b'',
        **{'orchestrator/'+name+'.py':raw for name,raw in runtime_libraries().items()},
        'view.txt':view,'manifest.json':canonical(manifest),
        'binding.json':canonical({'run_id':RUN,'analysis_registry_sha256':driver.config['private_intake']['sha256'],
                                  'original_sha256':nr.ORIGINAL,'view_sha256':nr.VIEW})}
    old=driver.state.parent/'lane-scientific-workspaces/run_spec_author-5'
    for name in ('SPEC.proposed.md','notebook.patch.json'):
        bodies['previous-'+name]=(old/name).read_bytes()
    for raw in bodies.values():nr.scan(raw,cases)
    return {RUNTIME+'/'+name:raw for name,raw in bodies.items()}

def task(files):
    refs='\n'.join(name+' sha256='+sha(raw) for name,raw in files.items())
    return ('\nCOUNTED MECHANICAL CORRECTION. Author5 completed transport but was not accepted. '
        'The actual module main(arm, folds) violates the existing main(input_root, output_root, contract) interface. '
        'Correct your preserved draft and actual call sites, without changing the scientific design or safeguards. '
        'You own all scientific code. Retain the default Colab Python3.13/preinstalled CUDA/PyTorch direction, '
        'full250epochs, automatic resume and private Drive hash/membership checks. The wrapper may call your '
        'arm/fold routine, but all four controller entrypoints must occur exactly once with exact signatures. '
        'Patch the SAME original notebook; previous files below are preserved draft evidence, not a new patch base. '
        'Run python3 -I -B .colab-feedback/check.py after writing BOTH outputs. Read each error, correct it and '
        'rerun inside this SAME call, at most12 local feedback iterations. Format feedback does not make a model '
        'call or consume another attempt. Do not edit the checker or its bound inputs. This checker executes '
        'no scientific code. Run available synthetic tests too; never claim unavailable tests passed. '
        'The host still runs the unchanged privacy checks and actual synthetic suite, then scientific review. '
        'No patient access, training, provider call or new credentials here. All input files below are mandatory '
        'hash-bound source/runtime or prior draft, not patient payloads:\n'+refs+'\n')

def install_hook(base,root,approval):
    """Add only bound inputs before the existing final context measurement."""
    from orchestrator import private_records as pr
    b=frozen(root)
    class Corrected(base):
        def prepare_input(self,value,stage,work):
            if self.config.get('run_id')!=RUN or stage!='run_spec_author':
                return super().prepare_input(value,stage,work)
            check_originals(self,b)
            record=json.loads((self.state/EVENT/'COMPLETE.json').read_bytes())
            require(record['review_sha256']==approval and record['proof_sha256']==DOCUMENT_SHA,'RECOVERY_APPROVAL')
            self._static_feedback=feedback_files(self,b)
            try:body,measurement=super().prepare_input(value,stage,work)
            finally:self.__dict__.pop('_static_feedback',None)
            refs=[]
            for name,raw in feedback_files(self,b).items():
                target=Path(work)/name
                pr.mkdir(target.parent,parents=True,exist_ok=True)
                require(not target.exists() and not target.is_symlink(),'FEEDBACK_ALREADY_PREPARED')
                pr.write_bytes(target,raw);target.chmod(0o400)
                refs.append({'path':name,'sha256':sha(raw),'bytes':len(raw)})
            return body,{**measurement,'workspace_files':[*measurement['workspace_files'],*refs]}
        def task(self,stage,value):
            text=super().task(stage,value)
            return text+task(self._static_feedback) if hasattr(self,'_static_feedback') else text
    return Corrected
