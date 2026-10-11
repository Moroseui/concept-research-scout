"""Scoped Colab static correction; no fake acceptance, REVISE or allowance."""
import argparse,hashlib,importlib.util,inspect,json,os,sqlite3,subprocess,sys
from pathlib import Path
ROOT=Path('/opt/research-system/manual-repair-helpers/timing-author24-preparation-recovery-20261010')
RECORD=Path('/var/lib/research-system-manual-sprint10-deployment/timing-author24-preparation-recovery-20261010')
ORIGINAL=Path('/opt/research-system/manual-repair-helpers/preparation-and-cap-repair-20261010')
BRANCH=Path('/opt/research-system/manual-repair-helpers/preparation-branch-admission-repair-20261010')
LANE=Path('/var/lib/research-system-manual-sprint10-deployment/colab-preparation-20261010/lane')
LEDGER=Path('/var/lib/research-system-autonomy/reviews/jobs.sqlite')
RUN='colab-1ad5fafc220b3d65f576ce08'
ID='2d531b8eeadd10e54c481d1c375b68a2f63899f31a8b6214adea98f023a839d0'
DOC='docs/COLAB_AUTHOR_STATIC_FAILURE_PRIVATE.json'
DOC_SHA='d6286b8b7fff8a397db7731d16627f7cd70efcbfdb245bfc346230b2de2d76d3'
CONTINUATION=LANE/'author-static-continuation-1'
REASON='AUTHOR_STATIC_CORRECTION_REQUIRED'
def require(ok,why):
    if not ok:raise ValueError('PREPARATION_AUTHOR_CONTINUATION_'+why)
def sha(raw):return hashlib.sha256(raw).hexdigest()
def canonical(v):return json.dumps(v,sort_keys=True).encode()
def binding():
    raw=(Path(__file__).resolve().parents[1]/DOC).read_bytes();require(sha(raw)==DOC_SHA,'DOCUMENT_CHANGED');return json.loads(raw)
def map_path(root,p):
    from tools.deploy_manual_lane import bound
    return bound(Path(root),str(p))
def raw(path):
    from orchestrator.private_records import check
    return check(path).read_bytes()
def connect_db(path):
    db=sqlite3.connect(Path(path).resolve().as_uri()+'?mode=ro',uri=True);db.row_factory=sqlite3.Row;return db
def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);sys.modules[name]=m;spec.loader.exec_module(m);return m
def authority():
    rt=load('_colab_continuation_authority',ROOT/'tools/timing_author24_runtime.py');result=rt.authority()
    manifest=json.loads(rt.trusted(RECORD/'review/packet-manifest.json').read_bytes())
    for name in (DOC,'tools/preparation_mechanical_continuation.py'):
        require(sha(rt.trusted(ROOT/name).read_bytes())==manifest['source_files'].get(name),'REVIEWED_COMPONENT')
    require(Path(__file__).resolve()==ROOT/'tools/preparation_mechanical_continuation.py','EXECUTED_SOURCE');return result

def files(root=Path('/')):
    b=binding();work=map_path(root,b['workspace']);folder=map_path(root,LANE/'notebook-revisions/author-1')
    outputs={n:raw(work/n) for n in b['output_sha256']}
    require({n:sha(body) for n,body in outputs.items()}==b['output_sha256'],'ORIGINAL_OUTPUT_CHANGED')
    require(sha(raw(work/'console.log'))==b['console_sha256'],'ORIGINAL_STREAM_CHANGED')
    require({p.name for p in folder.iterdir()}==set(b['derived_sha256']),'PARTIAL_FOLDER_MEMBERSHIP')
    derived={n:raw(folder/n) for n in b['derived_sha256']}
    require({n:sha(body) for n,body in derived.items()}==b['derived_sha256'],'PARTIAL_FOLDER_CHANGED')
    from orchestrator import notebook_execution as execution
    require(sha(Path(execution.__file__).read_bytes())==b['validator_source_sha256'],'UNCHANGED_VALIDATOR_REQUIRED')
    try:execution.extract(derived['revised.ipynb'],preprocessing=True)
    except ValueError as error:require(str(error)=='NOTEBOOK_EXECUTION_ENTRYPOINT:preprocess','EXACT_STATIC_FAILURE')
    else:raise ValueError('PREPARATION_AUTHOR_CONTINUATION_ORIGINAL_FAILURE_NOT_REPRODUCED')
    return outputs,derived

def rows(root=Path('/')):
    b=binding();cfg=raw(map_path(root,LANE/'lane.json'))
    require(sha(cfg)==b['config_sha256'] and json.loads(cfg)['run_id']==RUN,'ORIGINAL_CONFIG_CHANGED')
    with connect_db(map_path(root,LANE/'jobs.sqlite')) as db,connect_db(map_path(root,LEDGER)) as g:
        local=dict(db.execute('SELECT * FROM manual_calls WHERE id=?',(ID,)).fetchone() or {})
        globalrow=dict(g.execute('SELECT * FROM autonomy_calls WHERE id=?',(ID,)).fetchone() or {})
        require(sha(canonical(local))==b['local_row_sha256'] and sha(canonical(globalrow))==b['global_row_sha256'],'ORIGINAL_CALL_CHANGED')
        require(local['status']==globalrow['status']=='COMPLETE','COMPLETED_NOT_ACCEPTED_ONLY')
        require(json.loads(local['receipt'])['output_sha256']==b['output_sha256'],'OUTPUT_RECEIPT_BINDING')
        return {'local_row':local,'global_row':globalrow,'state_row':dict(db.execute('SELECT * FROM manual_state WHERE id=1').fetchone()),'account_row':dict(db.execute('SELECT * FROM manual_account WHERE id=1').fetchone()),'local_count':db.execute('SELECT count(*) FROM manual_calls').fetchone()[0],'running':[r['id'] for r in g.execute("SELECT id FROM autonomy_calls WHERE status='RUNNING'")]}

def feedback():
    from orchestrator import notebook_execution as execution
    require(sha(Path(execution.__file__).read_bytes())==binding()['validator_source_sha256'],'UNCHANGED_VALIDATOR_REQUIRED')
    return ('Prior author transport completed, but output was NOT accepted. This is a counted failed-author correction, not reviewer REVISE. '
        'Preserve prior outputs. The emitted module has duplicate top-level preprocess at lines509/906 and validate_preprocessing at534/909. '
        'Every required entrypoint must occur EXACTLY ONCE, with its exact signature and no defaults, decorators, varargs, positional-only or keyword-only arguments. '
        'You own the correction and must retain the intended scientific behavior and safeguards. Never relax the validator. '
        'Patch the SAME original notebook. Before submitting, concatenate the actual writefile module as execution.py and run this unchanged static check inside this call. '
        'Run all available synthetic tests; record unavailable dependencies honestly. The controller still requires full synthetic PASS and independent scientific review. '
        'No patient/GPU execution. A distinct author-2 workspace and synthetic folder preserve author1.\n'
        'Save as check_entrypoints.py and run python3 check_entrypoints.py execution.py:\n```python\nimport ast\n'
        +inspect.getsource(execution.entrypoints)+'\nif __name__ == "__main__":\n    import pathlib, sys\n'
        '    entrypoints(pathlib.Path(sys.argv[1]).read_text(), preprocessing=True)\n    print("ENTRYPOINTS_PASS")\n```\n')

def restored(original,review):
    value=json.loads(original['state_row']['payload'])
    event={'kind':'COUNTED_AUTHOR_STATIC_CORRECTION','failed_output_call_id':ID,'binding_sha256':DOC_SHA,'review_sha256':review['report_sha256'],'accepted':False,'reviewer_revise':False,'new_allowance':0}
    after={**value,'phase':'run_spec_author','reason':REASON,'interventions':[*value.get('interventions',[]),event]};after.pop('pending',None);return after

def verify_record(root=Path('/')):
    review=authority();dest=map_path(root,CONTINUATION);original=json.loads(raw(dest/'original-rows.json'));complete=json.loads(raw(dest/'COMPLETE.json'))
    require(complete=={'status':'READY_AUTHOR2_NO_CALL','call_id':ID,'binding_sha256':DOC_SHA,'review_sha256':review['report_sha256'],'original_rows_sha256':sha(canonical(original)),'feedback_sha256':sha(feedback().encode()),'new_calls':0,'new_allowance':0},'CONTINUATION_RECORD')
    b=binding()
    for key in ('local_row','global_row','state_row','account_row'):
        pin={'state_row':'state_sha256','account_row':'account_sha256'}.get(key,key+'_sha256');require(sha(canonical(original[key]))==b[pin],'ORIGINAL_SNAPSHOT_CHANGED')
    require(raw(dest/'feedback.txt')==feedback().encode(),'FEEDBACK_CHANGED');live=rows(root);files(root);return review,original,live

def ready_colab(root=Path('/')):
    review,original,live=verify_record(root)
    require(live['local_count']==1 and not live['running'],'NO_OTHER_ADMISSION')
    require(live['account_row']==original['account_row'] and json.loads(live['state_row']['payload'])==restored(original,review),'EXACT_RESTORED_STATE')
    return {'status':'READY_AUTHOR2','next_author':2,'accepted_rounds':{},'retained_calls':1,'allowance':8}
def held_unit():
    unit='research-preparation-branch-admission-repair-20261010-colab_preparation.service'
    text=subprocess.check_output(['systemctl','show',unit,'-p','ActiveState','-p','MainPID','-p','ExecMainStatus'],text=True)
    require(dict(x.split('=',1) for x in text.splitlines())=={'ActiveState':'inactive','MainPID':'0','ExecMainStatus':'0'},'ORIGINAL_UNIT_HELD')

def resume(root=Path('/'),check_unit=held_unit):
    from orchestrator import private_records as pr
    from orchestrator.remote_supervisor import lock
    require(os.getuid()==os.getgid()==1003,'SERVICE_OWNER');review=authority();dest=map_path(root,CONTINUATION)
    require(not dest.exists() and not dest.is_symlink(),'ORIGINAL_OR_PARTIAL_RECORD_PRESERVED')
    require(not map_path(root,LANE/'HALT').exists() and not map_path(root,LEDGER.parent/'HALT').exists(),'HALT_PRESERVED');check_unit()
    with lock(map_path(root,LANE/'one-run.lock')),lock(map_path(root,LANE/'driver.lock')):
        original=rows(root);b=binding();value=json.loads(original['state_row']['payload'])
        require(original['local_count']==1 and not original['running'],'NO_OTHER_ADMISSION')
        require(sha(canonical(original['state_row']))==b['state_sha256'] and sha(canonical(original['account_row']))==b['account_sha256'],'EXACT_BLOCKED_STATE_ACCOUNT')
        require(value['phase']=='BLOCKED' and value['reason']==b['reason'] and value['rounds']=={} and value['pending']=={'id':ID,'stage':'run_spec_author','round':1,'workspace':b['workspace']},'EXACT_STATIC_BLOCK_NOT_REVIEW')
        files(root);after=restored(original,review)
        pr.mkdir(dest);pr.write_bytes(dest/'original-rows.json',canonical(original));pr.write_bytes(dest/'feedback.txt',feedback().encode());pr.write_bytes(dest/'INTENT.json',canonical({'after':after,'review_sha256':review['report_sha256'],'binding_sha256':DOC_SHA}))
        db=pr.Connection(map_path(root,LANE/'jobs.sqlite'));db.row_factory=sqlite3.Row
        try:
            db.execute('BEGIN IMMEDIATE')
            require(dict(db.execute('SELECT * FROM manual_state WHERE id=1').fetchone())==original['state_row'] and dict(db.execute('SELECT * FROM manual_account WHERE id=1').fetchone())==original['account_row'] and db.execute('SELECT count(*) FROM manual_calls').fetchone()[0]==1,'STATE_RACE')
            db.execute('UPDATE manual_state SET payload=? WHERE id=1',(json.dumps(after,sort_keys=True),));db.execute('COMMIT')
        except BaseException:db.execute('ROLLBACK');raise
        finally:db.close()
        complete={'status':'READY_AUTHOR2_NO_CALL','call_id':ID,'binding_sha256':DOC_SHA,'review_sha256':review['report_sha256'],'original_rows_sha256':sha(canonical(original)),'feedback_sha256':sha(feedback().encode()),'new_calls':0,'new_allowance':0}
        pr.write_bytes(dest/'COMPLETE.json',canonical(complete));return ready_colab(root)

def install_hook(module):
    original=module.AnalysisDriver
    class CountedColabCorrection(original):
        def model_round_number(self,value):
            if self.config.get('run_id')!=RUN or value.get('phase')!='run_spec_author':return super().model_round_number(value)
            verify_record();require(not value.get('pending'),'NO_PENDING_RETRY')
            number=self.store.db.execute('SELECT count(*) FROM manual_calls WHERE stage=?',('run_spec_author',)).fetchone()[0]+1
            require(number==2 and value.get('reason')==REASON and value.get('rounds')=={},'ONLY_RETAINED_AUTHOR2');return number
        def task(self,stage,value):
            body=super().task(stage,value)
            if self.config.get('run_id')==RUN and stage=='run_spec_author':
                require(self.model_round_number(value)==2,'AUTHOR2_FEEDBACK_SCOPE');body+='\n'+feedback()
            return body
    module.AnalysisDriver=CountedColabCorrection;return original

def main(argv=None):
    p=argparse.ArgumentParser();p.add_argument('action',choices=['verify-colab','resume-colab','ready-colab','advance-colab']);a=p.parse_args(argv)
    require(os.getuid()==os.getgid()==1003,'SERVICE_OWNER');authority()
    if a.action=='resume-colab':return resume()
    if a.action=='ready-colab':return ready_colab()
    import orchestrator
    require(Path(orchestrator.__file__).resolve().parent==ORIGINAL/'orchestrator','ORIGINAL_IMPORT_ROOT')
    branch=load('_existing_colab_preparation_route',BRANCH/'tools/preparation_branch_repair_runtime.py');existing=branch.connect()
    command=['--scope',str(branch.ORIGINAL_RECORD/'preparation-interleaving.json'),'--review-report',str(branch.ORIGINAL_RECORD/'review/report.md')]
    if a.action=='verify-colab':return existing.main(['verify',*command])
    ready_colab()
    from orchestrator import analysis_driver
    install_hook(analysis_driver)
    return existing.main(['advance',*command,'--lane','colab_preparation'])
if __name__=='__main__':
    os.umask(0o077);print(json.dumps(main(),sort_keys=True))
