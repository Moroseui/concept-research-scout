"""Deterministic transport/recovery checks. Synthetic verdicts are test-only.

The optional retained-failure check reads operator evidence; it never updates it.
No test invokes a model or turns synthetic review output into authorization.
"""
import hashlib
import io
import json
import os
from pathlib import Path
import sqlite3
import subprocess
import sys

import pytest
from orchestrator import manual_stage as transport, stocktake_recovery as recovery
from orchestrator import manual_executor as executor, manual_recovery
from orchestrator.autonomy_accounting import BatchAccounts

ROOT=Path(__file__).resolve().parents[1]
STAGES=('run_spec_author','run_spec_review','result_interpretation_author','result_interpretation_review')

@pytest.mark.parametrize('stage',STAGES)
@pytest.mark.parametrize('raw',[b'LF\nexact\n',b'CRLF\r\nexact\r\n',b'mixed\r\nLF\nCR\rend', 'UTF-8 caf\u00e9 \u0394 \U0001f52c\r\n'.encode()])
def test_actual_producer_subprocess_sink_preserves_each_role(tmp_path,stage,raw):
    work=tmp_path/'workspace';work.mkdir();(work/'prompt.md').write_bytes(raw)
    proof=transport.transport_check(work,stage,executor.digest(raw))
    assert proof['input_utf8_bytes']==len(raw)
    assert proof['input_characters']==len(raw.decode())
    assert proof['input_sha256']==executor.digest(raw) and proof['model_client_launched'] is False
    assert proof['family']==('claude' if stage.endswith('review') else 'codex')
    assert sorted(p.name for p in work.iterdir())==['prompt.md']
    probe=Path(proof['probe'])
    assert json.loads((probe/'proof.json').read_text())==proof
    assert not (probe/'sent-input.json').exists() and not (probe/'credential-refresh.json').exists()
    assert not (tmp_path/'.native-homes').exists()

@pytest.mark.parametrize('family',['codex','claude'])
def test_actual_subprocess_boundary_rejects_changed_bytes_without_client(tmp_path,family):
    raw=b'protected\r\n';expected=executor.digest(raw)
    p=subprocess.run([sys.executable,'-B','-m','orchestrator.manual_stage','--hash-sink',expected,family],
        input=raw+b'changed',cwd=tmp_path,env={**os.environ,'PYTHONPATH':str(ROOT)},capture_output=True)
    assert p.returncode!=0 and b'RESERVED_INPUT_MISMATCH' in p.stderr
    assert list(tmp_path.iterdir())==[]


def test_corrupted_prepared_prompt_refuses_before_any_probe(tmp_path):
    (tmp_path/'prompt.md').write_bytes(b'changed')
    with pytest.raises(ValueError,match='RESERVED_INPUT_MISMATCH'):
        transport.transport_check(tmp_path,STAGES[0],executor.digest(b'original'))
    assert not (tmp_path.parent/'.transport-checks').exists()


def test_preadmission_connection_is_unavoidable_and_before_reservation():
    import ast
    module=ast.parse((ROOT/'orchestrator/manual_driver.py').read_text())
    method=next(n for n in ast.walk(module) if isinstance(n,ast.FunctionDef) and n.name=='_model_step')
    calls=[n for n in ast.walk(method) if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute)]
    probe=next(n for n in calls if n.func.attr=='transport_check')
    reserve=next(n for n in calls if n.func.attr=='reserve_call')
    assert probe.lineno<reserve.lineno
    assert 'input_sha256' in ast.unparse(method) and 'transport_preflight' in ast.unparse(method)


@pytest.fixture
def synthetic(tmp_path,monkeypatch):
    """Real local/global ledgers; only bound approval verification is synthetic."""
    folder=tmp_path/'var/lib/research-system-autonomy/reviews';folder.mkdir(parents=True)
    batch=BatchAccounts(folder);state=tmp_path/'lane';state.mkdir()
    store=executor.ManualExecutor(state/'jobs.sqlite',batch=batch)
    policy={'status':'RATIFIED','operator_approval':'synthetic exact grant','state_write_permission':'OPERATOR_AUTHORIZED',
        'n':4,'window':'UTC_CALENDAR_DAY','state_ref':'refs/heads/automation/dispatch-state','manual_semantics':'OPERATOR_STEP_D_MAX_EIGHT'}
    store.initialize_allowance(policy);batch.register_run(recovery.RUN,{'synthetic':True})
    ident,n,receipt=store.reserve_call(recovery.RUN,recovery.STAGE,recovery.BASE,'astra/manual-synthetic',policy,{'synthetic':True})
    assert ident==recovery.FAILED
    store.finish_call(ident,receipt,'UNCERTAIN')
    local=dict(store.db.execute('SELECT * FROM manual_calls WHERE id=?',(ident,)).fetchone())
    global_row=dict(batch.db.execute('SELECT * FROM autonomy_calls WHERE id=?',(ident,)).fetchone())
    monkeypatch.setattr(recovery,'LOCAL_ROW',recovery.sha(local));monkeypatch.setattr(recovery,'GLOBAL_ROW',recovery.sha(global_row))
    binding={'run_id':recovery.RUN,'failed_id':ident,'failed_sha256':recovery.LOCAL_ROW,'stage':recovery.STAGE,
        'decision_sha256':recovery.DECISION,'runtime_source':'synthetic','state':str(state),'filesystem_root':str(tmp_path)}
    monkeypatch.setattr(recovery,'validate_binding',lambda v: v if v==binding else (_ for _ in ()).throw(ValueError('SYNTHETIC_BINDING_CHANGED')))
    store.db.execute('INSERT INTO manual_state VALUES(1,?)',(json.dumps({'phase':recovery.STAGE}),))
    return store,batch,policy,binding,local,global_row


def grant(synthetic):
    store,batch,policy,binding,local,global_row=synthetic
    store.db.execute('INSERT INTO manual_recoveries VALUES(?,?)',(recovery.FAILED,recovery.encoded(binding)))
    batch.db.execute('INSERT INTO events VALUES(?,?,?)',(recovery.EVENT,recovery.RUN,recovery.encoded(binding)))


def test_no_permission_no_new_admission(synthetic):
    store,batch,policy,*_=synthetic
    with pytest.raises(ValueError,match='UNCERTAIN'):store.reserve_call(recovery.RUN,recovery.STAGE,recovery.BASE,'astra/manual-synthetic',policy,{})
    assert manual_recovery.role_limit(store,recovery.RUN,recovery.STAGE)==2


def test_one_linked_replacement_keeps_failure_and_charge(synthetic):
    store,batch,policy,binding,local,global_row=synthetic;grant(synthetic)
    assert manual_recovery.role_limit(store,recovery.RUN,recovery.STAGE)==3
    for stage in STAGES[1:]:assert manual_recovery.role_limit(store,recovery.RUN,stage)==2
    before=executor.Accounts(store).read()
    ident,n,receipt=store.reserve_call(recovery.RUN,recovery.STAGE,'c'*40,'astra/manual-synthetic',policy,{})
    assert n==2 and receipt['linked_recovery_of']==recovery.FAILED
    assert dict(store.db.execute('SELECT * FROM manual_calls WHERE id=?',(recovery.FAILED,)).fetchone())==local
    assert dict(batch.db.execute('SELECT * FROM autonomy_calls WHERE id=?',(recovery.FAILED,)).fetchone())==global_row
    assert batch.db.execute("SELECT count(*) FROM autonomy_calls WHERE kind='scientific'").fetchone()[0]==2
    assert executor.Accounts(store).read()!=before
    with pytest.raises(ValueError,match='UNCERTAIN'):store.reserve_call(recovery.RUN,recovery.STAGE,'c'*40,'astra/manual-synthetic',policy,{})
    store.finish_call(ident,receipt,'UNCERTAIN')
    with pytest.raises(ValueError,match='UNCERTAIN'):store.reserve_call(recovery.RUN,recovery.STAGE,'c'*40,'astra/manual-synthetic',policy,{})


def test_allowance_cap_and_unrequested_third_author_still_refuse(synthetic):
    store,batch,policy,*_=synthetic;grant(synthetic)
    ident,n,receipt=store.reserve_call(recovery.RUN,recovery.STAGE,'c'*40,'astra/manual-synthetic',policy,{})
    store.finish_call(ident,receipt,'COMPLETE')
    with pytest.raises(ValueError,match='ONLY_REVIEW_REQUESTED_REVISION'):
        store.reserve_call(recovery.RUN,recovery.STAGE,'c'*40,'astra/manual-synthetic',policy,{})
    for n in range(6):store.db.execute('INSERT INTO manual_calls VALUES(?,?,?,?,?)',(f'extra{n}','result_interpretation_review',n+1,'COMPLETE','{}'))
    with pytest.raises(ValueError,match='MODEL_CALL_LIMIT'):
        store.reserve_call(recovery.RUN,recovery.STAGE,'c'*40,'astra/manual-synthetic',policy,{})


@pytest.mark.parametrize('side',['local','global'])
def test_altered_original_refuses(synthetic,side):
    store,batch,policy,*_=synthetic;grant(synthetic)
    db,table=(store.db,'manual_calls') if side=='local' else (batch.db,'autonomy_calls')
    db.execute('UPDATE '+table+' SET receipt=? WHERE id=?',('{}',recovery.FAILED))
    with pytest.raises(ValueError,match='ORIGINAL_FAILURE_CHANGED'):
        store.reserve_call(recovery.RUN,recovery.STAGE,'c'*40,'astra/manual-synthetic',policy,{})


def test_missing_global_binding_and_halt_refuse(synthetic):
    store,batch,policy,binding,*_=synthetic
    store.db.execute('INSERT INTO manual_recoveries VALUES(?,?)',(recovery.FAILED,recovery.encoded(binding)))
    with pytest.raises(ValueError,match='BOTH_LEDGER'):store.reserve_call(recovery.RUN,recovery.STAGE,'c'*40,'astra/manual-synthetic',policy,{})
    batch.db.execute('INSERT INTO events VALUES(?,?,?)',(recovery.EVENT,recovery.RUN,recovery.encoded(binding)))
    (batch.folder/'HALT').touch()
    with pytest.raises(ValueError,match='HALTED'):store.reserve_call(recovery.RUN,recovery.STAGE,'c'*40,'astra/manual-synthetic',policy,{})


def test_global_completion_needs_valid_replacement_and_preserves_original(synthetic):
    store,batch,policy,binding,local,global_row=synthetic;grant(synthetic)
    with pytest.raises(ValueError,match='REPLACEMENT_NOT_COMPLETE'):batch.complete_run(recovery.RUN,{})
    ident,n,receipt=store.reserve_call(recovery.RUN,recovery.STAGE,'c'*40,'astra/manual-synthetic',policy,{})
    store.finish_call(ident,receipt,'COMPLETE');batch.complete_run(recovery.RUN,{'synthetic_acceptance':True})
    assert dict(batch.db.execute('SELECT * FROM autonomy_calls WHERE id=?',(recovery.FAILED,)).fetchone())==global_row
    assert batch.db.execute('SELECT status FROM autonomy_runs WHERE id=?',(recovery.RUN,)).fetchone()[0]=='COMPLETE'
    assert recovery.global_exception(batch,'another-run') is None


def test_genuine_preserved_failed_rows_are_bound_when_evidence_available():
    folder=os.environ.get('STOCKTAKE_FAILED_EVIDENCE')
    if not folder:pytest.skip('Private genuine failure evidence supplied only on operator verification hosts')
    folder=Path(folder)
    for name,table,pin in [('lane.sqlite','manual_calls',recovery.LOCAL_ROW),('accounting.sqlite','autonomy_calls',recovery.GLOBAL_ROW)]:
        before=executor.digest((folder/name).read_bytes())
        with recovery.connect(folder/name) as db:assert recovery.original_row(db,table,pin)['status']=='UNCERTAIN'
        assert executor.digest((folder/name).read_bytes())==before
    assert recovery.sha(executor.read(folder/'lane/lane.json'))==recovery.CONFIG
    assert executor.digest((folder/'work/prompt.md').read_bytes())==recovery.PROMPT


def test_authority_files_exact():
    recovery.authority(ROOT)


@pytest.mark.parametrize('damage',['none','incomplete-matrix','changed-bytes','changed-producer','model-launched','wrong-family','wrong-runtime'])
def test_matrix_requires_all_real_connections_and_exact_code(tmp_path,damage,monkeypatch):
    import time
    selection={'installed_mtime_ns':0,'source':'synthetic-unit-only'}
    monkeypatch.setattr(recovery,'installed_selection',lambda *a:selection)
    connections=[]
    for stage in STAGES:
        for number in range(1,4 if stage==recovery.STAGE else 3):
            proof={'status':'PASS','stage':stage,'family':'claude' if stage.endswith('review') else 'codex',
                'input_sha256':recovery.PROMPT,'model_client_launched':False,'isolated_stdin':True,
                'producer_sha256':executor.digest((ROOT/'scout.py').read_bytes()),
                'transport_sha256':executor.digest((ROOT/'orchestrator/manual_stage.py').read_bytes())}
            path=tmp_path/(stage+str(number)+'.json');path.write_text(json.dumps(proof))
            connections.append({'stage':stage,'round':number,'proof_path':str(path),'proof_sha256':executor.digest(path.read_bytes()),'proof':proof})
    matrix={'schema':'stocktake-transport-matrix/v2','runtime_sha256':recovery.RUNTIME,'connections':connections,'installation':selection,'recorded_at':time.time()}
    if damage=='none':recovery.validate_matrix(matrix,ROOT);return
    if damage=='incomplete-matrix':connections.pop()
    elif damage=='wrong-runtime':matrix['runtime_sha256']='0'*64
    elif damage=='changed-bytes':Path(connections[0]['proof_path']).write_text('{}')
    else:
        key,value={'changed-producer':('producer_sha256','0'*64),'model-launched':('model_client_launched',True),'wrong-family':('family','claude')}[damage]
        connections[0]['proof'][key]=value;p=Path(connections[0]['proof_path']);p.write_text(json.dumps(connections[0]['proof']));connections[0]['proof_sha256']=executor.digest(p.read_bytes())
    with pytest.raises(ValueError,match='STOCKTAKE_'):recovery.validate_matrix(matrix,ROOT)


def test_other_uncertainty_and_global_caps_remain(synthetic):
    store,batch,policy,*_=synthetic;grant(synthetic)
    batch.db.execute("INSERT INTO autonomy_calls VALUES('another','administrative','other',1,'2026-01-01','UNCERTAIN','{}',NULL)")
    with pytest.raises(ValueError,match='BATCH_UNCERTAIN_OR_RUNNING_CALL'):
        store.reserve_call(recovery.RUN,recovery.STAGE,'c'*40,'astra/manual-synthetic',policy,{})
    batch.db.execute("UPDATE autonomy_calls SET status='COMPLETE' WHERE id='another'")
    for n in range(59):
        batch.db.execute("INSERT INTO autonomy_calls VALUES(?, 'scientific','other',1,'2026-01-01','COMPLETE','{}',NULL)",(f'prior{n}',))
    with pytest.raises(ValueError,match='BATCH_CALL_LIMIT'):
        store.reserve_call(recovery.RUN,recovery.STAGE,'c'*40,'astra/manual-synthetic',policy,{})


def test_reviewer_requested_revision_only_after_replacement(synthetic,tmp_path):
    store,batch,policy,*_=synthetic;grant(synthetic)
    ident,n,receipt=store.reserve_call(recovery.RUN,recovery.STAGE,'c'*40,'astra/manual-synthetic',policy,{})
    store.finish_call(ident,receipt,'COMPLETE')
    work=tmp_path/'review';work.mkdir();path=work/'review.json';path.write_text(json.dumps({'verdict':'REVISE','rationale':'BLOCKER[metric/statistic] Synthetic scientific revision'}))
    store.db.execute('INSERT INTO manual_calls VALUES(?,?,?,?,?)',('review','run_spec_review',1,'COMPLETE',json.dumps({'workspace':str(work),'output_sha256':{'review.json':executor.digest(path.read_bytes())}})))
    store.db.execute('UPDATE manual_state SET payload=?',(json.dumps({'phase':recovery.STAGE,'reason':'REVISION_REQUIRED'}),))
    ident,n,receipt=store.reserve_call(recovery.RUN,recovery.STAGE,'c'*40,'astra/manual-synthetic',policy,{})
    assert n==3 and 'linked_recovery_of' not in receipt
    assert receipt['revision_kind']=='reviewer_requested_revision'
    assert receipt['revision_of']==executor.digest((recovery.RUN+':'+recovery.STAGE+':2').encode())
    store.finish_call(ident,receipt,'COMPLETE')
    with pytest.raises(ValueError,match='MODEL_CALL_LIMIT'):
        store.reserve_call(recovery.RUN,recovery.STAGE,'c'*40,'astra/manual-synthetic',policy,{})


def test_promoter_keeps_default_incomplete_lane_refusal(tmp_path,monkeypatch):
    from tools import manual_promotion as promotion,manual_host_control as host
    from tools.deploy_manual_lane import STATE
    lane=tmp_path/STATE.lstrip('/')/'releases/named/lane';lane.mkdir(parents=True);(lane/'lane.json').write_text('{}')
    monkeypatch.setattr(host,'lane_state',lambda p:({'phase':'BLOCKED'},['UNCERTAIN']))
    with pytest.raises(ValueError,match='INITIALIZED_LANE_REQUIRES'):
        promotion.require_uninitialized_lane(tmp_path)
    promotion.require_uninitialized_lane(tmp_path,lane)
    other=lane.parents[1]/'unrelated/lane';other.mkdir(parents=True);(other/'lane.json').write_text('{}')
    with pytest.raises(ValueError,match='INITIALIZED_LANE_REQUIRES'):
        promotion.require_uninitialized_lane(tmp_path,lane)


def test_promoter_exception_requires_exact_authority_source_runtime(monkeypatch,tmp_path):
    monkeypatch.setattr(recovery,'authority',lambda root:None)
    previous={'source':recovery.BASE,'state':recovery.OLD_STATE.removesuffix('/lane')}
    with pytest.raises(ValueError,match='PROMOTION_SCOPE'):recovery.promotion_check(tmp_path,previous,ROOT,'manual')
    with pytest.raises(ValueError,match='PROMOTION_SCOPE'):recovery.promotion_check(tmp_path,{**previous,'source':'0'*40},ROOT,'analysis')
    seen=[]
    monkeypatch.setattr(recovery,'original_state',lambda state,filesystem_root:seen.append((state,filesystem_root)))
    assert recovery.promotion_check(tmp_path,previous,ROOT,'analysis')==tmp_path/recovery.OLD_STATE.lstrip('/')
    assert len(seen)==1


from test_analysis_driver import analysis_lane, fake_model
from test_manual_lane import lane, root


def test_recovered_stocktake_actual_driver_finishes_with_five_charged_rows(analysis_lane,monkeypatch):
    d=analysis_lane;old_run=d.config['run_id'];d.config['run_id']=recovery.RUN
    executor.atomic(d.state/'lane.json',d.config)
    d.store.batch.db.execute('UPDATE autonomy_runs SET id=? WHERE id=?',(recovery.RUN,old_run))
    def failure(*args):raise OSError('Synthetic pre-client transport failure')
    d.runner=failure
    assert d.advance()['phase']=='BLOCKED'
    local=dict(d.store.db.execute('SELECT * FROM manual_calls WHERE id=?',(recovery.FAILED,)).fetchone())
    global_row=dict(d.store.batch.db.execute('SELECT * FROM autonomy_calls WHERE id=?',(recovery.FAILED,)).fetchone())
    monkeypatch.setattr(recovery,'LOCAL_ROW',recovery.sha(local));monkeypatch.setattr(recovery,'GLOBAL_ROW',recovery.sha(global_row))
    d.config['execution_recovery']={'kind':'stocktake-transport'}
    executor.atomic(d.state/'lane.json',d.config)
    binding={'run_id':recovery.RUN,'failed_id':recovery.FAILED,'failed_sha256':recovery.LOCAL_ROW,'stage':recovery.STAGE,
        'decision_sha256':recovery.DECISION,'runtime_source':d.config['source'],'root':str(d.root.resolve()),
        'state':str(d.state.resolve()),'config_sha256':recovery.sha(d.config)}
    monkeypatch.setattr(recovery,'global_exception',lambda batch,run,**kw: recovery.FAILED if run==recovery.RUN else None)
    monkeypatch.setattr(recovery,'validate_binding',lambda v:v if v==binding else (_ for _ in ()).throw(ValueError('SYNTHETIC_BOUND_APPROVAL_REQUIRED')))
    d.store.db.execute('INSERT INTO manual_recoveries VALUES(?,?)',(recovery.FAILED,recovery.encoded(binding)))
    d.store.batch.db.execute('INSERT INTO events VALUES(?,?,?)',(recovery.EVENT,recovery.RUN,recovery.encoded(binding)))
    value=d.current();value.update(phase=recovery.STAGE,reason=None,linked_recovery_of=recovery.FAILED);value.pop('pending');d.save(value)
    d.runner=fake_model
    for phase in ['run_spec_review','COMMIT_SPEC','result_interpretation_author','result_interpretation_review','UPDATE_STATE','REPORT','COMPLETE']:
        observed=d.advance();assert observed['phase']==phase,observed
    assert d.status()['calls_used']==5 and d.advance()['calls_used']==5
    assert dict(d.store.db.execute('SELECT * FROM manual_calls WHERE id=?',(recovery.FAILED,)).fetchone())==local
    assert dict(d.store.batch.db.execute('SELECT * FROM autonomy_calls WHERE id=?',(recovery.FAILED,)).fetchone())==global_row
    assert d.store.batch.db.execute('SELECT count(*) FROM autonomy_calls').fetchone()[0]==5
    for row in d.store.db.execute('SELECT stage,attempt,receipt FROM manual_calls'):
        receipt=json.loads(row['receipt'])
        assert ('linked_recovery_of' in receipt)==(row['stage']==recovery.STAGE and row['attempt']==2)
    assert d.current()['operator_review_pending'] is True
    assert not (d.state/'package').exists()
