import copy
import hashlib
import json
import sqlite3
from pathlib import Path
from types import SimpleNamespace

import pytest
from orchestrator import colab_simple_full as f


def db_at(path):
    path.parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(path, isolation_level=None)
    db.row_factory = sqlite3.Row
    db.executescript("""
        CREATE TABLE manual_calls(id TEXT PRIMARY KEY,stage TEXT,attempt INTEGER,status TEXT,receipt TEXT);
        CREATE TABLE manual_state(id INTEGER PRIMARY KEY,payload TEXT);
        CREATE TABLE autonomy_runs(id TEXT PRIMARY KEY,binding TEXT,status TEXT);
        CREATE TABLE autonomy_calls(id TEXT PRIMARY KEY,kind TEXT,change_id TEXT,round INTEGER,day TEXT,status TEXT,binding TEXT,receipt TEXT);
        CREATE TABLE events(id TEXT PRIMARY KEY,job TEXT,payload TEXT);
        CREATE TABLE jobs(id TEXT PRIMARY KEY,binding TEXT,phase TEXT,status TEXT);
    """)
    return db


@pytest.fixture
def lane(tmp_path, monkeypatch):
    parent = tmp_path/'prior'; parent.mkdir()
    new = tmp_path/'new'; new.mkdir()
    previous = db_at(parent/'jobs.sqlite')
    local = db_at(new/'jobs.sqlite')
    global_db = db_at(tmp_path/'global/jobs.sqlite')
    offsets = dict(run_spec_author=3, run_spec_review=4,
                   result_interpretation_author=1, result_interpretation_review=0)
    local_rows=[]; global_rows=[]
    for stage, count in offsets.items():
        for n in range(1,count+1):
            ident = f.sha((f.RUN+':'+stage+':'+str(n)).encode())
            lr=dict(id=ident,stage=stage,attempt=n,status='COMPLETE',receipt='{}')
            gr=dict(id=ident,kind='scientific',change_id=f.RUN,round=len(global_rows)+1,
                    day='2026-10-08',status='COMPLETE',binding=json.dumps({'caps':{'batch':95},'batch_continuation':{'limit':95}}),receipt='{}')
            local_rows.append(lr); global_rows.append(gr)
            for db in [previous,local]:db.execute('INSERT INTO manual_calls VALUES(?,?,?,?,?)',tuple(lr.values()))
            global_db.execute('INSERT INTO autonomy_calls VALUES(?,?,?,?,?,?,?,?)',tuple(gr.values()))
    local_rows.sort(key=lambda r:r['id']); global_rows.sort(key=lambda r:r['id'])
    state=dict(id=1,payload=json.dumps({'phase':'COMMIT_SPEC','rounds':offsets},sort_keys=True))
    previous.execute('INSERT INTO manual_state VALUES(?,?)',tuple(state.values()))
    local.execute('INSERT INTO manual_state VALUES(1,?)',(json.dumps({'phase':'run_spec_author','rounds':offsets}),))
    owner=dict(id=f.RUN,binding=json.dumps({'state':'/original-owner','run_id':f.RUN},sort_keys=True),status='ACTIVE')
    acceptance=dict(id=f.RUN+':accepted',job=f.RUN,payload=json.dumps({'report_sha256':f.sha(b'accepted report')}))
    global_db.execute('INSERT INTO autonomy_runs VALUES(?,?,?)',tuple(owner.values()))
    global_db.execute('INSERT INTO events VALUES(?,?,?)',tuple(acceptance.values()))
    for name,data in [('lane.json',b'{}'),('REPORT.md',b'accepted report'),('preparation-plan.json',b'{}')]:
        (parent/name).write_bytes(data)
    prior=dict(parent_lane='/prior',config_sha256=f.sha(b'{}'),plan_sha256=f.sha(b'{}'),report_sha256=f.sha(b'accepted report'),
               parent_state_row=state,owner=owner,acceptance=acceptance,local_calls=local_rows,global_calls=global_rows)
    scope=dict(run_id=f.RUN,prior=prior,new_lane='/new',review_directory='/review',offsets=offsets,
               call_limit=20,operator_sha256='a'*64,admitted_stages=sorted(f.STAGES),execution_authorized=False,
               batch_limit=104,uncertain_rows=[],previous_batch_admission=json.loads(global_rows[0]['binding']))
    config=dict(run_id=f.RUN,item_number=4,backend='analysis',source='1'*40,owner_binding=json.loads(owner['binding']),
                revision_policy=__import__('orchestrator.analysis_revisions',fromlist=['POLICY']).POLICY,author_timeout_seconds=1800,workspace_root='/lane-scientific-workspaces',context=str(new/'context'),
                **{f.FIELD:{'schema':'colab-simple-full-preparation/v1','scope_sha256':f.DOCUMENT_SHA}})
    prior['config']={k:v for k,v in config.items() if k not in {f.FIELD,'author_timeout_seconds','revision_policy'}}
    (new/'lane.json').write_text(json.dumps(config))
    batch=SimpleNamespace(db=global_db,filesystem_root=tmp_path,folder=tmp_path/'global')
    store=SimpleNamespace(db=local,path=new/'jobs.sqlite',batch=batch)
    monkeypatch.setattr(f,'document',lambda:copy.deepcopy(scope))
    monkeypatch.setattr(f,'_approval',lambda config,scope,root:'2'*64)
    monkeypatch.setattr(f,'_TERMINAL_QUALIFIER',lambda accounts,row: (_ for _ in ()).throw(AssertionError('no terminal rows in base fixture')))
    yield SimpleNamespace(store=store,scope=scope,config=config,parent=parent,new=new,previous=previous,global_db=global_db)
    previous.close();local.close();global_db.close()


def test_one_use_activation_preserves_all_originals_and_shared_owner(lane):
    x=lane; before=[dict(r)for r in x.global_db.execute('SELECT * FROM autonomy_calls ORDER BY id')]
    result=f.activate(x.store,f.RUN)
    assert result==dict(status='COLAB_SIMPLE_AUTHOR_READY',calls_already_counted=8,shared_call_limit=20,execution_authorized=False)
    owner=dict(x.global_db.execute('SELECT * FROM autonomy_runs').fetchone())
    assert owner=={**x.scope['prior']['owner'],'status':'ACTIVE'}
    assert [dict(r)for r in x.global_db.execute('SELECT * FROM autonomy_calls ORDER BY id')]==before
    assert dict(x.global_db.execute('SELECT * FROM events WHERE id=?',(f.RUN+':accepted',)).fetchone())==x.scope['prior']['acceptance']
    assert f.validate(x.store,f.RUN)['offsets']==x.scope['offsets']
    with pytest.raises(ValueError,match='ALREADY_ACTIVATED'):f.activate(x.store,f.RUN)
    assert x.global_db.execute('SELECT count(*) FROM autonomy_runs').fetchone()[0]==1
    assert x.global_db.execute('SELECT count(*) FROM events WHERE id=?',(f.EVENT,)).fetchone()[0]==1


@pytest.mark.parametrize('corruption',['global-call','local-call','parent-state','parent-plan','owner'])
def test_changed_original_refuses_before_activation(lane,corruption):
    x=lane
    if corruption=='global-call':x.global_db.execute("UPDATE autonomy_calls SET receipt='changed' WHERE id=?",(x.scope['prior']['global_calls'][0]['id'],))
    elif corruption=='local-call':x.store.db.execute("UPDATE manual_calls SET receipt='changed' WHERE id=?",(x.scope['prior']['local_calls'][0]['id'],))
    elif corruption=='parent-state':x.previous.execute("UPDATE manual_state SET payload='{}'")
    elif corruption=='parent-plan':(x.parent/'preparation-plan.json').write_text('changed')
    elif corruption=='owner':x.global_db.execute("UPDATE autonomy_runs SET binding='{}'")
    else:x.global_db.execute("UPDATE events SET payload='{}'")
    with pytest.raises(ValueError):f.activate(x.store,f.RUN)
    assert x.global_db.execute('SELECT status FROM autonomy_runs').fetchone()[0]=='ACTIVE'
    assert not x.global_db.execute('SELECT 1 FROM events WHERE id=?',(f.EVENT,)).fetchone()


def test_no_activation_with_live_model_or_without_independent_approval(lane,monkeypatch):
    x=lane
    x.global_db.execute("INSERT INTO autonomy_calls VALUES('live','implementation_review','other',1,'2026-10-11','RUNNING','{}',NULL)")
    with pytest.raises(ValueError,match='LIVE_MODEL_CALL'):f.activate(x.store,f.RUN)
    x.global_db.execute("DELETE FROM autonomy_calls WHERE id='live'")
    def refuse(*args):raise ValueError('INDEPENDENT_REVISE')
    monkeypatch.setattr(f,'_approval',refuse)
    with pytest.raises(ValueError,match='INDEPENDENT_REVISE'):f.activate(x.store,f.RUN)
    assert x.global_db.execute('SELECT status FROM autonomy_runs').fetchone()[0]=='ACTIVE'


def test_legacy_run_without_scope_is_unchanged(tmp_path):
    state=tmp_path/'lane';state.mkdir();(state/'lane.json').write_text('{"run_id":"other"}')
    assert f.validate(SimpleNamespace(path=state/'jobs.sqlite'),'other')is None


def test_exact_scope_admission_and_old_closure_refusal(lane):
    x=lane;f.activate(x.store,f.RUN)
    f.guard_admission(x.store.batch,f.RUN,'run_spec_author','1'*40,{'workspace':'/lane-scientific-workspaces/run_spec_author-4'})
    for stage,source,work in [('run_spec_author','0'*40,'/lane-scientific-workspaces/run_spec_author-4'),
                              ('result_interpretation_author','1'*40,'/lane-scientific-workspaces/result_interpretation_author-2'),
                              ('run_spec_author','1'*40,'/lane-scientific-workspaces/run_spec_author-3'),
                              ('run_spec_author','1'*40,'/other/run_spec_author-4')]:
        with pytest.raises(ValueError):f.guard_admission(x.store.batch,f.RUN,stage,source,{'workspace':work})
    with pytest.raises(ValueError,match='DISTINCT_ACCEPTANCE_REQUIRED'):f.refuse_legacy_completion(x.store.batch,f.RUN)
    assert dict(x.global_db.execute('SELECT * FROM events WHERE id=?',(f.RUN+':accepted',)).fetchone())==x.scope['prior']['acceptance']


def test_preparation_stops_after_review_and_refuses_execution(lane):
    x=lane;f.activate(x.store,f.RUN)
    driver=SimpleNamespace(store=x.store,config=x.config,status=lambda:{'phase':'COMMIT_SPEC'})
    out=f.preparation_hold(driver,{'phase':'COMMIT_SPEC'},None,None)
    assert out['execution_authorized']is False and out['phase']=='COMMIT_SPEC'
    for phase in ['EXECUTE_CPU','WAIT_OUTPUTS','result_interpretation_author','UPDATE_STATE']:
        with pytest.raises(ValueError,match='PREPARATION_ONLY'):f.preparation_hold(driver,{'phase':phase},None,None)
    with pytest.raises(ValueError,match='NO_EXECUTION_OR_COLLECTION'):f.preparation_hold(driver,{'phase':'run_spec_author'},'/results',None)


def test_review_offsets_preserve_three_revision_cycles():
    from orchestrator.analysis_revisions import review_transition
    review={'verdict':'REVISE','findings':[{'category':'code/spec mismatch'}]}
    for durable_round in [4,5,6]:
        assert review_transition(review,'run_spec_review',durable_round,offset=3)==('run_spec_author','REVISION_REQUIRED')
    assert review_transition(review,'run_spec_review',7,offset=3)==('BLOCKED','UNRESOLVED_AFTER_THREE_REVISIONS')
    assert review_transition({'verdict':'REJECT'},'run_spec_review',4,offset=3)==('BLOCKED','REVIEW_REJECTED')
    with pytest.raises(ValueError):review_transition(review,'run_spec_review',3,offset=3)


def test_21st_shared_call_is_refused_by_normal_global_admission(lane,monkeypatch):
    from orchestrator.autonomy_accounting import BatchAccounts
    from orchestrator import autonomy_limits as limits,stocktake_recovery,stocktake_review_recovery
    from orchestrator import experiment_timeout_continuation,completed_run,preparation_interleaving
    x=lane;f.activate(x.store,f.RUN)
    for i in range(12):
        x.global_db.execute('INSERT INTO autonomy_calls VALUES(?,?,?,?,?,?,?,?)',
                            ('later'+str(i),'scientific',f.RUN,10+i,'2026-10-08','COMPLETE','{}','{}'))
    monkeypatch.setattr(stocktake_recovery,'global_exception',lambda *a:None)
    monkeypatch.setattr(stocktake_review_recovery,'admission',lambda *a:None)
    monkeypatch.setattr(experiment_timeout_continuation,'global_exception',lambda *a,**k:None)
    monkeypatch.setattr(completed_run,'closed_ids',lambda *a,**k:set())
    monkeypatch.setattr(preparation_interleaving,'terminal_ids',lambda *a:[])
    monkeypatch.setattr(limits,'global_limit',lambda *a:20)
    monkeypatch.setattr(limits,'daily_allowance',lambda *a:{'limit':50,'authority_sha256':'d'*64})
    monkeypatch.setattr(limits,'scientific_batch_allowance',lambda *a:{'limit':1000})
    x.store.batch.status=lambda ident:{'status':'NOT_RESERVED'}
    before=[dict(r)for r in x.global_db.execute('SELECT * FROM autonomy_calls ORDER BY id')]
    with pytest.raises(ValueError,match='AUTONOMY_RUN_CALL_LIMIT'):
        BatchAccounts.reserve_scientific(x.store.batch,'new-call',f.RUN,'run_spec_author','1'*40,
                                         {'workspace':'/lane-scientific-workspaces/run_spec_author-4'})
    assert [dict(r)for r in x.global_db.execute('SELECT * FROM autonomy_calls ORDER BY id')]==before
    assert x.global_db.execute('SELECT count(*) FROM autonomy_runs').fetchone()[0]==1


def test_workspace_root_drift_refuses_activation(lane):
    x=lane;x.config['workspace_root']='/other'
    (x.new/'lane.json').write_text(json.dumps(x.config))
    with pytest.raises(ValueError,match='EXACT_WORKSPACE_ROOT'):f.activate(x.store,f.RUN)
    assert x.global_db.execute('SELECT status FROM autonomy_runs').fetchone()[0]=='ACTIVE'


def test_workspace_symlink_refuses_admission(lane):
    x=lane;f.activate(x.store,f.RUN)
    (x.store.batch.filesystem_root/'lane-scientific-workspaces').symlink_to(x.parent,target_is_directory=True)
    with pytest.raises(ValueError,match='PATH_ALIAS'):
        f.guard_admission(x.store.batch,f.RUN,'run_spec_author','1'*40,
                          {'workspace':'/lane-scientific-workspaces/run_spec_author-4'})


@pytest.mark.parametrize('verdict,findings,source', [
    ('REVISE',[],'1'*40),('REJECT',[],'1'*40),
    ('APPROVE',[{'finding':'unresolved'}],'1'*40),('APPROVE',[],'0'*40)])
def test_real_approval_gate_refuses_nonapproval_or_changed_source(tmp_path,monkeypatch,verdict,findings,source):
    from orchestrator import autonomy_review
    root=tmp_path/'review';root.mkdir()
    (root/'packet-manifest.json').write_text(json.dumps({'source_sha':'1'*40}))
    (root/'report.md').write_text(json.dumps({'findings':findings}))
    monkeypatch.setattr(autonomy_review,'verify_result',lambda path:{
        'verdict':verdict,'source_sha':source,'report_sha256':'2'*64})
    with pytest.raises(ValueError):
        f._approval({'source':'1'*40},{'review_directory':'/review'},tmp_path)


def test_104th_batch_ceiling_refuses_colab_call(lane,monkeypatch):
    from orchestrator.autonomy_accounting import BatchAccounts
    from orchestrator import autonomy_limits as limits
    x=lane;f.activate(x.store,f.RUN)
    for i in range(96):
        x.global_db.execute('INSERT INTO autonomy_calls VALUES(?,?,?,?,?,?,?,?)',
            ('other'+str(i),'scientific','other-run',i+1,'2026-10-08','COMPLETE','{}','{}'))
    monkeypatch.setattr(limits,'global_limit',lambda *a:20)
    monkeypatch.setattr(limits,'daily_allowance',lambda *a:{'limit':50,'authority_sha256':'d'*64})
    x.store.batch.status=lambda ident:{'status':'NOT_RESERVED'}
    with pytest.raises(ValueError,match='AUTONOMY_BATCH_CALL_LIMIT'):
        BatchAccounts.reserve_scientific(x.store.batch,'new-call',f.RUN,'run_spec_author','1'*40,
                                        {'workspace':'/lane-scientific-workspaces/run_spec_author-4'})
    assert x.global_db.execute('SELECT count(*) FROM autonomy_calls').fetchone()[0]==104


def test_terminal_proof_is_required_and_unknown_live_call_refuses(lane,monkeypatch):
    x=lane;f.activate(x.store,f.RUN)
    monkeypatch.setattr(f,'_TERMINAL_QUALIFIER',None)
    with pytest.raises(ValueError,match='INSTALLED_TERMINAL_QUALIFIER_REQUIRED'):f.terminal_ids(x.store.batch,x.scope)
    monkeypatch.setattr(f,'_TERMINAL_QUALIFIER',lambda *a:{})
    x.global_db.execute("INSERT INTO autonomy_calls VALUES('new','scientific','other',1,'2026-10-08','RUNNING','{}',NULL)")
    with pytest.raises(ValueError,match='UNCLASSIFIED_OR_RUNNING_CALL'):f.terminal_ids(x.store.batch,x.scope)


def test_terminal_rows_and_charges_preserved_while_qualifying(lane,monkeypatch):
    x=lane;f.activate(x.store,f.RUN)
    x.global_db.execute("INSERT INTO autonomy_calls VALUES('old-terminal','scientific','other',1,'2026-10-08','UNCERTAIN','{}','{\"cost\":2}')")
    row=dict(x.global_db.execute("SELECT * FROM autonomy_calls WHERE id='old-terminal'").fetchone())
    scope={**x.scope,'uncertain_rows':[row]}
    seen=[]
    def qualify(accounts,value):
        assert accounts is x.store.batch and value==row;seen.append(value)
        return {'id':row['id'],'proof_sha256':'a'*64}
    monkeypatch.setattr(f,'_TERMINAL_QUALIFIER',qualify)
    assert f.terminal_ids(x.store.batch,scope)==['old-terminal'] and seen==[row]
    assert dict(x.global_db.execute("SELECT * FROM autonomy_calls WHERE id='old-terminal'").fetchone())==row
    monkeypatch.setattr(f,'_TERMINAL_QUALIFIER',lambda *a:{'id':row['id']})
    with pytest.raises(ValueError,match='AUTHENTIC_TERMINAL_PROOF_REQUIRED'):f.terminal_ids(x.store.batch,scope)




def test_native_unit_preserves_protections_and_replaces_old_writable_state():
    from tools import colab_simple_runtime as native
    scope=f.document();raw=native.unit_bytes(scope).decode().splitlines();old=scope['native']['template_bytes'].splitlines()
    changed={'Description','ConditionPathExists','WorkingDirectory','ExecStart','ReadWritePaths'}
    untouched=lambda lines:[line for line in lines if line.split('=',1)[0]not in changed and not line.startswith('Environment=PYTHONPATH=')]
    assert untouched(raw)==untouched(old)
    writes=next(line.split('=',1)[1].split()for line in raw if line.startswith('ReadWritePaths='))
    assert scope['native']['work'] in writes and str(Path(scope['prior']['parent_lane']).parent)not in writes
    assert scope['native']['root']not in writes
    assert raw.count('Restart=no')==1 and raw.count('TimeoutStartSec=3700')==1


def test_native_unit_rejects_changed_template():
    from tools import colab_simple_runtime as native
    scope=copy.deepcopy(f.document());scope['native']['template_bytes']=scope['native']['template_bytes'].replace('NoNewPrivileges=true','NoNewPrivileges=false')
    with pytest.raises(ValueError,match='NATIVE_TEMPLATE_PIN'):native.unit_bytes(scope)


def test_config_drift_after_activation_refuses(lane):
    x=lane;f.activate(x.store,f.RUN)
    x.config['source']='3'*40
    (x.new/'lane.json').write_text(json.dumps(x.config))
    with pytest.raises(ValueError,match='QUALIFIED_ACTIVATION_REQUIRED'):f.validate(x.store,f.RUN)


def test_context_root_escape_refuses(lane):
    x=lane;x.config['context']='/other'
    (x.new/'lane.json').write_text(json.dumps(x.config))
    with pytest.raises(ValueError,match='EXACT_CONTEXT_ROOT'):f.activate(x.store,f.RUN)


def test_native_service_unit_passes_systemd_parser(tmp_path):
    import shutil,subprocess
    from tools import colab_simple_runtime as native
    assert shutil.which('systemd-analyze'), 'systemd parser is required for this Linux native component'
    scope=f.document();unit=tmp_path/scope['native']['unit'];unit.write_bytes(native.unit_bytes(scope))
    result=subprocess.run(['systemd-analyze','verify',str(unit)],capture_output=True,text=True)
    assert result.returncode==0,result.stderr


def test_root_start_without_exact_transition_refuses_before_any_start(monkeypatch):
    from tools import colab_simple_runtime as native
    monkeypatch.setattr(native.os,'getuid',lambda:0)
    monkeypatch.setattr(native,'authority',lambda:{'source_sha':'1'*40})
    monkeypatch.setattr(native,'held_prior',lambda:None)
    with pytest.raises(ValueError,match='EXACT_TRANSITION_REQUIRED'):native.start('advance','not-a-transition')

def notebook():
    cells=[{'cell_type':'markdown','metadata':{},'source':[]}for _ in range(5)]
    cells[4]={'cell_type':'code','metadata':{},'outputs':[],'execution_count':None,
              'source':['%%writefile config.py\n','DELIVERY_ARM = "A1_repeat"\n','DELIVERY_FOLDS = (0, 1, 2, 3, 4)\n','UNCHANGED = "abc"\n']}
    return json.dumps({'nbformat':4,'nbformat_minor':5,'metadata':{},'cells':cells}).encode()

def test_materialized_six_notebooks_only_fold_literal_changes():
    from orchestrator.colab_notebook_delivery import variants
    raw=notebook();out=variants(raw)
    assert len(out)==6 and out['13B_A1_repeat.ipynb']==raw
    for fold in range(5):
        v=json.loads(out[f'13B_A1_repeat_fold{fold}.ipynb'])
        source=''.join(v['cells'][4]['source'])
        assert f'DELIVERY_FOLDS = ({fold},)' in source and 'UNCHANGED = "abc"'in source
        original=json.loads(raw)
        v['cells'][4]['source']=original['cells'][4]['source']
        assert v==original

@pytest.mark.parametrize('before,after',[
    ('A1_repeat','other'),
    ('(0, 1, 2, 3, 4)','(False, 1, 2, 3, 4)'),
    ('(0, 1, 2, 3, 4)','[0, 1, 2, 3, 4]'),
    ('(0, 1, 2, 3, 4)','make_folds()'),
    ('(0, 1, 2, 3, 4)','(0, 0, 2, 3, 4)'),
    ('DELIVERY_FOLDS =','DELIVERY_FOLDS: tuple ='),
    ('DELIVERY_FOLDS =','OTHER ='),
])
def test_variant_refuses_ambiguous_or_unapproved_selection(before,after):
    from orchestrator.colab_notebook_delivery import variants
    with pytest.raises((ValueError,SyntaxError)):variants(notebook().replace(before.encode(),after.encode()))

def test_variant_refuses_executed_outputs():
    from orchestrator.colab_notebook_delivery import variants
    value=json.loads(notebook());value['cells'][4]['execution_count']=1
    with pytest.raises(ValueError,match='UNEXECUTED'):variants(json.dumps(value).encode())

def test_real_documents_and_templates_compile():
    from tools import colab_simple_runtime as rt
    scope=f.document()
    assert scope['call_limit']==20 and scope['batch_limit']==104 and len(scope['prior']['local_calls'])==8
    raw=rt.unit_bytes(scope)
    assert b'ProtectSystem=strict' in raw and b'Restart=no' in raw

def test_prepare_copies_history_once_without_activation_or_new_allowance(lane,monkeypatch):
    from orchestrator import manual_driver,analysis_driver
    x=lane;root=x.store.batch.filesystem_root/'repository';root.mkdir()
    # Remove only the synthetic target created by this fixture, so prepare must
    # build it itself. Production prepare has no removal or overwrite path.
    x.store.db.close();(x.new/'jobs.sqlite').unlink();(x.new/'lane.json').unlink();x.new.rmdir()
    (x.parent/'context').mkdir(mode=0o700);(x.parent/'context/question.txt').write_text('Synthetic aggregate question')
    (x.parent/'context/question.txt').chmod(0o600)
    prior=x.scope['prior'];before={**prior['config'],'batch_ledger':'/global','profile_files':{},'engine_files':{},
                                'context':'/prior/context','root':'/old-repository','branch':'astra/original','engine_review':{}}
    prior['config']=before;body=f.encoded(before);(x.parent/'lane.json').write_bytes(body);prior['config_sha256']=f.sha(body)
    old_state={'phase':'COMMIT_SPEC','rounds':x.scope['offsets'],'artifacts':[],'interventions':[]}
    raw=f.encoded(old_state).decode();x.previous.execute('UPDATE manual_state SET payload=?',(raw,));prior['parent_state_row']={'id':1,'payload':raw}
    x.previous.executescript('CREATE TABLE manual_account(id INTEGER PRIMARY KEY,version INTEGER,payload TEXT); CREATE TABLE manual_recoveries(failed_id TEXT PRIMARY KEY,binding TEXT);')
    x.previous.execute("INSERT INTO manual_account VALUES(1,9,'{\"original_usage\":8}')")
    prior['manual_account']=[dict(r)for r in x.previous.execute('SELECT * FROM manual_account')];prior['manual_recoveries']=[]
    monkeypatch.setattr(manual_driver,'git',lambda root,*args:{('status','--porcelain'):'',('rev-parse','HEAD'):'1'*40,
                        ('branch','--show-current'):'astra/colab-simple-full-20261012'}[args])
    monkeypatch.setattr(analysis_driver,'release_identities',lambda root:({},{}))
    result=f.prepare(root,filesystem_root=x.store.batch.filesystem_root)
    assert result=={'status':'PREPARED_NOT_ACTIVATED','calls_preserved':8,'model_calls':0,'new_allowance':0}
    assert x.global_db.execute('SELECT status FROM autonomy_runs').fetchone()[0]=='ACTIVE'
    assert not x.global_db.execute('SELECT 1 FROM events WHERE id=?',(f.EVENT,)).fetchone()
    with sqlite3.connect(x.new/'jobs.sqlite')as copied:
        copied.row_factory=sqlite3.Row
        assert [dict(r)for r in copied.execute('SELECT * FROM manual_calls ORDER BY id')]==prior['local_calls']
        assert [dict(r)for r in copied.execute('SELECT * FROM manual_account')]==prior['manual_account']
        state=json.loads(copied.execute('SELECT payload FROM manual_state').fetchone()[0])
        assert state['phase']=='run_spec_author' and state['rounds']==x.scope['offsets'] and 'reviewed_results'not in state
    with pytest.raises(ValueError,match='EXISTING_LANE_RECONCILE'):f.prepare(root,filesystem_root=x.store.batch.filesystem_root)


def test_fiftieth_daily_call_still_refuses(lane,monkeypatch):
    from orchestrator.autonomy_accounting import BatchAccounts
    from orchestrator import autonomy_limits as limits
    from datetime import datetime,timezone
    x=lane;f.activate(x.store,f.RUN)
    for i in range(50):
        x.global_db.execute('INSERT INTO autonomy_calls VALUES(?,?,?,?,?,?,?,?)',
          ('daily'+str(i),'implementation_review','another',i+1,datetime.now(timezone.utc).date().isoformat(),'COMPLETE','{}','{}'))
    monkeypatch.setattr(limits,'global_limit',lambda *a:20)
    x.store.batch.status=lambda ident:{'status':'NOT_RESERVED'}
    before=x.global_db.execute('SELECT count(*) FROM autonomy_calls').fetchone()[0]
    with pytest.raises(ValueError,match='AUTONOMY_DAILY_CALL_LIMIT'):
        BatchAccounts.reserve_scientific(x.store.batch,'new-call',f.RUN,'run_spec_author','1'*40,
            {'workspace':'/lane-scientific-workspaces/run_spec_author-4'})
    assert x.global_db.execute('SELECT count(*) FROM autonomy_calls').fetchone()[0]==before

def test_actual_analysis_driver_holds_before_commit_or_execution(lane,monkeypatch):
    from orchestrator.analysis_driver import AnalysisDriver
    x=lane;f.activate(x.store,f.RUN)
    driver=object.__new__(AnalysisDriver);driver.store=x.store;driver.config=x.config
    driver.guard=lambda:None;driver.current=lambda:{'phase':'COMMIT_SPEC'}
    driver.status=lambda:{'phase':'COMMIT_SPEC'}
    result=driver._advance()
    assert result['execution_authorized']is False
    with pytest.raises(ValueError,match='NO_EXECUTION_OR_COLLECTION|ANALYSIS_HAS_NO_EXECUTION'):
        driver._advance(collect_folder='/synthetic-results')

def old_uncertain(lane,monkeypatch):
    x=lane
    old=next(row for row in x.scope['prior']['local_calls']if row['stage']=='result_interpretation_author')
    old['status']='UNCERTAIN'
    global_row=next(row for row in x.scope['prior']['global_calls']if row['id']==old['id'])
    global_row['status']='UNCERTAIN';x.scope['uncertain_rows']=[copy.deepcopy(global_row)]
    for db in [x.store.db,x.previous]:
        db.execute("UPDATE manual_calls SET status='UNCERTAIN' WHERE id=?",(old['id'],))
    x.global_db.execute("UPDATE autonomy_calls SET status='UNCERTAIN' WHERE id=?",(old['id'],))
    x.store.db.execute('CREATE TABLE manual_recoveries(failed_id TEXT PRIMARY KEY,binding TEXT)')
    x.config.update(root=str(Path(__file__).resolve().parents[1]),review_contract='bound-review/v1')
    x.scope['prior']['config'].update(root=x.config['root'],review_contract='bound-review/v1')
    (x.new/'lane.json').write_text(json.dumps(x.config))
    monkeypatch.setattr(f,'_TERMINAL_QUALIFIER',lambda accounts,row:{'id':row['id'],'proof_sha256':'f'*64})
    f.activate(x.store,f.RUN)
    return old

@pytest.mark.parametrize('stage',['run_spec_author','run_spec_review'])
def test_actual_local_admission_reaches_connectivity_with_authentic_old_terminal(lane,monkeypatch,stage):
    from orchestrator.manual_executor import ManualExecutor
    old=old_uncertain(lane,monkeypatch);x=lane
    class ReachedConnectivity(Exception):pass
    def reached(*args,**kwargs):raise ReachedConnectivity()
    monkeypatch.setattr('orchestrator.connectivity.require',reached)
    before=[dict(row)for row in x.store.db.execute('select *from manual_calls order by id')]
    with pytest.raises(ReachedConnectivity):
        ManualExecutor.reserve_call(x.store,f.RUN,stage,'1'*40,'astra/synthetic',{}, {})
    assert before==[dict(row)for row in x.store.db.execute('select *from manual_calls order by id')]
    assert next(row for row in before if row['id']==old['id'])['status']=='UNCERTAIN'

@pytest.mark.parametrize('kind',['running','new','changed','proof-failure'])
def test_actual_local_admission_still_refuses_unproven_uncertainty(lane,monkeypatch,kind):
    from orchestrator.manual_executor import ManualExecutor
    x=lane;old=old_uncertain(lane,monkeypatch)
    if kind=='running':x.store.db.execute("UPDATE manual_calls SET status='RUNNING' WHERE id=?",(old['id'],))
    elif kind=='new':x.store.db.execute("INSERT INTO manual_calls VALUES('new','run_spec_author',4,'UNCERTAIN','{}')")
    elif kind=='changed':x.store.db.execute("UPDATE manual_calls SET receipt='changed'WHERE id=?",(old['id'],))
    else:
        def refuse(*a):raise ValueError('TERMINAL_PROOF_FAILED')
        monkeypatch.setattr(f,'_TERMINAL_QUALIFIER',refuse)
    with pytest.raises(ValueError):
        ManualExecutor.reserve_call(x.store,f.RUN,'run_spec_author','1'*40,'astra/synthetic',{}, {})
    assert not x.global_db.execute("SELECT 1 FROM autonomy_calls WHERE status='RUNNING'").fetchone()
