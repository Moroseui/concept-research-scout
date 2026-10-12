"""Bound reviewer-requested Colab revision plus unchanged in-call feedback.

No scientific source edits, new model allowance, scientific acceptance or compute.
The unchanged controller still applies privacy checks, synthetic tests and review.
"""
from pathlib import Path
import hashlib, json, os

CALL='b2ad5de3e0be8974c93683730fb5dccf3d72c39aefd5d32b8056dfcde7c80cc0'
RUN='colab-1ad5fafc220b3d65f576ce08'
DOCUMENT='docs/COLAB_REVIEW6_DELETE_PRIVATE.json'
DOCUMENT_SHA='a1119e70bdf0dbb9e138c5daaccce0af3d11ecc50d0f7e4d273780193897c0bf'
REASON='REVIEW_REQUIRES_OPERATOR_DECISION'
EVENT='colab-review6-author-deletion'
DISPOSITION_DOCUMENT='docs/COLAB_REVIEW5_OPERATOR_DISPOSITION.json'
DISPOSITION_SHA='d23197a5659403a303af859dfdfc87b05b17b2e6aa27851f4d860920c6b131b6'
DELEGATION_DOCUMENT='docs/OVERNIGHT_AUTONOMY_OPERATOR_DECISION_20261008.txt'
DELEGATION_SHA='a7fbba4b5c49426c099f1eb8d91e45489b454fc51a527f5df1566a60c1cabcb1'
OPERATOR_DOCUMENT='docs/COLAB_REVIEW5_OPERATOR_DECISION_20261012.txt'
OPERATOR_SHA='89312b1d6df5ff20de61701754dd5179308b974b6ee3d8fac1c0151071bfd33e'
RUNTIME='.colab-feedback'
REVIEW_CANONICAL_SHA='b3fcd575d84dcedbda3385c249736be7903cbfee3b83e08156f4164b4e166379'
REFERENCE_DOCUMENT='docs/COLAB_ACCEPTED_INPUT_REFERENCE_PRIVATE.json'
REFERENCE_SHA='8ff800b4ecc9d6f3cdc6e5e41144e84acfcb7fe93d0e5d0138d4560ee6e16d04'
LIBRARIES=('author_output_schema','experiment_plan_validation','experiment_environment_requirements',
           'modal_billing','notebook_execution','scientific_view_scan','privacy_patterns')
sha=lambda raw:hashlib.sha256(raw).hexdigest()
canonical=lambda v:json.dumps(v,sort_keys=True,separators=(',',':'),allow_nan=False).encode()

def require(ok,why):
    if not ok:raise ValueError('COLAB_STATIC_'+why)

def frozen(root):
    operator_disposition(root)
    raw=(Path(root)/DOCUMENT).read_bytes()
    require(sha(raw)==DOCUMENT_SHA,'FROZEN_PROOF_CHANGED')
    return json.loads(raw)

def operator_disposition(root):
    root=Path(root)
    require(sha((root/OPERATOR_DOCUMENT).read_bytes())==OPERATOR_SHA,'EXPLICIT_OPERATOR_DECISION')
    require(sha((root/DELEGATION_DOCUMENT).read_bytes())==DELEGATION_SHA,'STANDING_DELEGATION')
    raw=(root/DISPOSITION_DOCUMENT).read_bytes()
    require(sha(raw)==DISPOSITION_SHA,'OPERATOR_DISPOSITION')
    value=json.loads(raw)
    require(value['human_approval'] is False and value['run_id']==RUN
            and value['review_round']==5 and value['author_round']==7
            and value['review_sha256']=='b20fc6089d2d3fc3785e8f0b315adb2869519a6acd0897b7ef2806ebee1b1823'
            and value['delegation_sha256']==DELEGATION_SHA
            and value['development_count']==99 and value['excluded_count']==49
            and value['patient_access'] is False and value['scientific_execution'] is False
            and value['require_fresh_scientific_approve_of_exact_bytes'] is True,'DISPOSITION_SCOPE')
    return value

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
    review=json.loads(pr.check(root/'lane-scientific-workspaces/run_spec_review-6/review.json').read_bytes())
    require(review['verdict']=='REVISE' and
            {row['id'] for row in review['findings']}=={
                'F-INERT-FRAGMENT-FALSE-MEMBERSHIP-LITERAL'},
            'EXACT_GENUINE_REVISE')
    require(sha(canonical(review))==REVIEW_CANONICAL_SHA,'REVIEW_CHANGED')

def restored(value,approval):
    require(value['phase']=='BLOCKED' and value['reason']==REASON and
            value.get('blocked_stage')=='run_spec_review' and not value.get('pending') and value.get('review','').endswith('/run_spec_review-6/review.json') and
            value['rounds']['run_spec_author']==7 and value['rounds']['run_spec_review']==6,
            'EXACT_REVIEW_BLOCK')
    result=json.loads(json.dumps(value))
    result.update(phase='run_spec_author',reason='REVISION_REQUIRED')
    result.pop('blocked_stage',None);result.pop('blocker_categories',None)
    result['interventions'].append({'kind':EVENT,'review_call':CALL,'proof_sha256':DOCUMENT_SHA,
        'implementation_review_sha256':approval,'operator_disposition_sha256':DISPOSITION_SHA,'operator_decision_sha256':OPERATOR_SHA,'scientific_acceptance':False,
        'reviewer_revise':True,'new_allowance':0})
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
    record={'proof_sha256':DOCUMENT_SHA,'review_sha256':approval,'operator_disposition_sha256':DISPOSITION_SHA,'operator_decision_sha256':OPERATOR_SHA,'new_calls':0,'new_allowance':0,
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
    return {'status':'READY_REVIEWER_REQUESTED_AUTHOR8','calls_preserved':len(b['calls']),'new_calls':0,'new_allowance':0}

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
    bodies['author_output_schema']=(Path(__file__).parent/'author_output_schema.py').read_bytes()
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

def feedback_files(driver,b,root=None):
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
    old=driver.state.parent/'lane-scientific-workspaces/run_spec_author-7'
    for name in ('SPEC.proposed.md','notebook.patch.json'):
        bodies['previous-'+name]=(old/name).read_bytes()
    require(root is not None,'REFERENCE_ROOT')
    reference=(Path(root)/REFERENCE_DOCUMENT).read_bytes()
    require(sha(reference)==REFERENCE_SHA,'REFERENCE_CHANGED')
    bodies['accepted-input-reference.json']=reference
    for raw in bodies.values():nr.scan(raw,cases)
    return {RUNTIME+'/'+name:raw for name,raw in bodies.items()}

def task(files):
    refs='\n'.join(name+' sha256='+sha(raw) for name,raw in files.items())
    return ('\nGENUINE REVIEW6 REVISION, not a mechanical retry and not scientific acceptance. '
        'The reference hash correction is already present. Remove the inert false-membership fragment; keep the actual '
        '99-development/49-excluded membership check unchanged and authoritative. Bind INPUT_REFERENCE_SHA256='
        +REFERENCE_SHA+' into your actual executable source. The exact accepted-input-reference.json '
        'is supplied below: existing accepted metadata descriptors unchanged, and five distinct empty '
        'private Drive lock objects verified through the existing registered broker. They live in its '
        'approved private evidence output folder, with owner-only access, empty descriptions and zero bytes. '
        'They need not live beside results; their IDs are explicit and unique to A1_repeat folds0..4. '
        'The tiny reference file has been written/readback-verified in the existing Drive package; '
        'remote Desktop sync is not independently proven and the notebook must verify it fail-closed. '
        'No patient input payload was copied, no credential or scope was changed. '
        'Do not redesign science. Full250epochs, default Colab Python3.13/preinstalled CUDA/PyTorch, '
        'automatic resume, private separate outputs, all input and membership safeguards remain. '
        'Exact final runnable bytes must pass the existing synthetic suite and opposing code review. '
        'No post-review source regeneration. The operator packages only exact accepted bytes. '
        'Use previous-author7 files as draft evidence, patch the SAME original notebook. '
        'You own all scientific source. The patch interface now permits ONE exact empty replacement: '
        'unit=cells/4/source,start=2090,end=2120,before_sha256=8ffa5399e3c59a3fee6bb8a4cca50b89b57fdcd62163dcbf20a5c289ffa0674c,replacement="". '
        'This deletes the already-omitted obsolete fragment without revealing or replacing any hidden bytes. '
        'Also remove your visible wrapper and obsolete release-hold note. Keep the real membership_guard unchanged. '
        'No other omitted span is editable; all ordinary visible patches and scans remain. '
        'Use the reviewed feedback checker after writing both outputs: '
        'python3 -I -B .colab-feedback/check.py; correct errors within this call, at most12 local iterations. '
        'Do not edit the checker or bound inputs. No patient data or training here. '
        'Every old attempt/charge and original review remains counted and visible. '
        'Mandatory bound sources/metadata:\n'+refs+'\n')


_PROBE_DB = None

def accounting_adapter(original,root,approval):
    """Normal revision accounting; new operator rule removes category-only holds.

    Exact originals, receipts, role limits and normal reservations still apply.
    No temporary category substitution or separate authority ruling.
    """
    b=frozen(root)
    def bound(driver,stage,number,author_number):
        if (driver.config.get('run_id')!=RUN or stage!='run_spec_author'
                or number!=6 or author_number!=8):
            return original(driver,stage,number,author_number)
        check_originals(driver,b)
        from orchestrator import private_records as pr
        if _PROBE_DB is driver.store.db:
            require(driver.store.db.in_transaction,'PROBE_TRANSACTION')
        else:
            record=json.loads(pr.check(driver.state/EVENT/'COMPLETE.json').read_bytes())
            require(record['review_sha256']==approval and record['proof_sha256']==DOCUMENT_SHA
                and record['operator_decision_sha256']==OPERATOR_SHA,'ADMISSION_APPROVAL')
        return original(driver,stage,number,author_number)
    return bound

def activate_correction_modules(root):
    """Install only reviewed function implementations in this fixed service."""
    import importlib.util
    from orchestrator import notebook_revision as nr,author_output_schema as schema,analysis_revisions as revisions
    for name,target,functions in [
        ('notebook_revision',nr,('apply',)),
        ('author_output_schema',schema,('visible_module',)),
        ('analysis_revisions',revisions,('review_transition','instructions','execution_instructions'))]:
        path=Path(root)/'orchestrator'/(name+'.py')
        spec=importlib.util.spec_from_file_location('_reviewed_colab_'+name,path)
        module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
        for function in functions:setattr(target,function,getattr(module,function))


def probe_admission(driver,root,approval):
    """Exercise the real pre-reservation accounting path in a rollback transaction."""
    global _PROBE_DB
    from orchestrator import author_revision_accounting as accounting
    b=frozen(root);check_originals(driver,b,initial=True)
    db=driver.store.db;require(not db.in_transaction and _PROBE_DB is None,'CLEAN_PROBE')
    original=b['state_row']['payload'];prospective=restored(json.loads(original),approval)
    before_calls=[dict(row)for row in db.execute('SELECT * FROM manual_calls ORDER BY rowid')]
    db.execute('BEGIN IMMEDIATE')
    try:
        db.execute('UPDATE manual_state SET payload=? WHERE id=1',(json.dumps(prospective,sort_keys=True),))
        _PROBE_DB=db
        result=accounting.inspect(driver.store,RUN,'run_spec_author')
        require(result['binding']['review_call_id']==CALL and result['binding']['author_attempt']==8
                and result['binding']['review_sha256']==sha((driver.state.parent/'lane-scientific-workspaces/run_spec_review-6/review.json').read_bytes()),
                'REAL_ADMISSION_BINDING')
    finally:
        _PROBE_DB=None;db.rollback()
    require(db.execute('SELECT payload FROM manual_state WHERE id=1').fetchone()[0]==original
            and [dict(row)for row in db.execute('SELECT * FROM manual_calls ORDER BY rowid')]==before_calls,
            'PROBE_ROLLBACK')
    check_originals(driver,b,initial=True)
    return {'status':'PASS','author_attempt':8,'review_call_id':CALL,
            'model_calls':0,'reservations':0,'persistent_state_mutations':0}

def install_hook(base,root,approval):
    """Add only bound inputs before the existing final context measurement."""
    from orchestrator import private_records as pr
    b=frozen(root)
    activate_correction_modules(root)
    from orchestrator import author_revision_accounting as accounting
    accounting.review_binding=accounting_adapter(accounting.review_binding,root,approval)
    class Corrected(base):
        def prepare_input(self,value,stage,work):
            if self.config.get('run_id')!=RUN or stage!='run_spec_author':
                return super().prepare_input(value,stage,work)
            check_originals(self,b)
            record=json.loads((self.state/EVENT/'COMPLETE.json').read_bytes())
            require(record['review_sha256']==approval and record['proof_sha256']==DOCUMENT_SHA,'RECOVERY_APPROVAL')
            self._static_feedback=feedback_files(self,b,root)
            try:body,measurement=super().prepare_input(value,stage,work)
            finally:self.__dict__.pop('_static_feedback',None)
            refs=[]
            for name,raw in feedback_files(self,b,root).items():
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
