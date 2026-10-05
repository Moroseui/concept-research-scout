"""Bounded scientific replacement tests; all reviewer/host attestations synthetic.

The exact private-copy migration rehearsal is recorded separately. No test calls
any model, uses credentials, or presents synthetic output as source approval.
"""
import json
from pathlib import Path
import pytest
from orchestrator import stocktake_review_recovery as recovery, manual_recovery, manual_stage, scientific_search
from orchestrator.autonomy_accounting import BatchAccounts
from orchestrator.manual_executor import ManualExecutor,digest
from test_manual_lane import lane,root,fake_author

ROOT=Path(__file__).resolve().parents[1]


def test_exact_operator_and_checkpoint_pins():
    recovery.authority(ROOT)
    p=recovery.checkpoint()
    assert len(p['local_calls'])==len(p['global_calls'])==5
    assert p['interpretation_artifacts'][0]['sha256']=='ee54e2091d164164331b27918da611621276528d68129e7d21dc6e79c80ed366'


@pytest.mark.parametrize('stage,seconds',[('result_interpretation_review',1200),('run_spec_review',900),('result_interpretation_author',900),('run_spec_author',900),(None,900)])
def test_timeout_extension_is_only_result_review(stage,seconds):
    import tomllib
    value=tomllib.loads(manual_stage.transport_profile('a'*64,[('claude',[])],stage=stage))
    assert value['limits']['stage_timeout']==seconds


@pytest.fixture
def batch(tmp_path,monkeypatch):
    b=BatchAccounts(tmp_path/'ledger');b.register_run(recovery.RUN,{'synthetic':True})
    for n,ident in enumerate(recovery.checkpoint()['global_calls']):
        status='UNCERTAIN' if ident in (recovery.rec.FAILED,recovery.FAILED) else 'COMPLETE'
        b.db.execute('INSERT INTO autonomy_calls VALUES(?,?,?,?,?,?,?,?)',(ident,'scientific',recovery.RUN,n+1,'2026-01-01',status,'{}','{}'))
    # Isolate the admission policy from separately tested root/native verifier.
    value={'runtime_source':'a'*40,'preserved_failures':[recovery.rec.FAILED,recovery.FAILED]}
    monkeypatch.setattr(recovery,'global_permit',lambda db,run:value if run==recovery.RUN else None)
    return b


def reserve(b,**changes):
    args={'ident':recovery.REPLACEMENT,'run':recovery.RUN,'stage':recovery.STAGE,'source':'a'*40,'receipt':{'linked_recovery_of':recovery.FAILED}}
    args.update(changes);return b.reserve_scientific(**args)


def test_only_one_linked_reservation_preserves_original_rows(batch):
    before=[tuple(x) for x in batch.db.execute('SELECT * FROM autonomy_calls')]
    value=reserve(batch);assert value['accounting_units']==1
    after=[tuple(x) for x in batch.db.execute('SELECT * FROM autonomy_calls')]
    assert len(after)==6 and all(x in after for x in before)
    with pytest.raises(ValueError,match='PARTIAL_OR_DUPLICATE'):reserve(batch)
    assert batch.db.execute('SELECT count(*) FROM autonomy_calls').fetchone()[0]==6


@pytest.mark.parametrize('change',[{'stage':'run_spec_author'},{'source':'b'*40},{'ident':'0'*64},{'receipt':{}},{'receipt':{'linked_recovery_of':recovery.rec.FAILED}}])
def test_other_call_or_source_cannot_use_review_authority(batch,change):
    with pytest.raises(ValueError,match='ONE_LINKED_REVIEW_REPLACEMENT_ONLY'):reserve(batch,**change)
    assert batch.db.execute('SELECT count(*) FROM autonomy_calls').fetchone()[0]==5


@pytest.mark.parametrize('status',['RUNNING','UNCERTAIN'])
def test_additional_unproven_pending_call_still_refuses(batch,status):
    batch.db.execute("INSERT INTO autonomy_calls VALUES('other','implementation_review','other',1,'2026-01-01',?,'{}','{}')",(status,))
    with pytest.raises(ValueError,match='BATCH_UNCERTAIN_OR_RUNNING_CALL'):reserve(batch)


def test_halt_still_refuses(batch):
    (batch.folder/'HALT').write_text('synthetic stop')
    with pytest.raises(ValueError,match='AUTONOMY_BATCH_HALTED'):reserve(batch)


def test_no_role_cap_was_raised(monkeypatch):
    monkeypatch.setattr(manual_recovery,'permit',lambda *a:{'review_checkpoint':recovery.CHECKPOINT,'stage':recovery.STAGE})
    assert all(manual_recovery.role_limit(None,recovery.RUN,s)==2 for s in ['run_spec_author','run_spec_review','result_interpretation_author','result_interpretation_review'])


def test_author_and_stage_binding_refuse_before_call(tmp_path):
    s=ManualExecutor(tmp_path/'local.sqlite');p=recovery.checkpoint()
    for n,ident in enumerate(p['local_calls']):s.db.execute('INSERT INTO manual_calls VALUES(?,?,?,?,?)',(ident,'synthetic',n+1,'COMPLETE','{}'))
    v={'phase':recovery.STAGE,'artifacts':p['interpretation_artifacts']};s.db.execute('INSERT INTO manual_state VALUES(1,?)',(json.dumps(v),))
    recovery.validate_next_call(s,recovery.STAGE,2)
    with pytest.raises(ValueError,match='ONE_LINKED'):recovery.validate_next_call(s,'result_interpretation_author',2)
    with pytest.raises(ValueError,match='ONE_LINKED'):recovery.validate_next_call(s,recovery.STAGE,3)
    v['artifacts'][0]['sha256']='0'*64;s.db.execute('UPDATE manual_state SET payload=?',(json.dumps(v),))
    with pytest.raises(ValueError,match='AUTHOR_CHANGED'):recovery.validate_next_call(s,recovery.STAGE,2)


@pytest.mark.parametrize('verdict',['APPROVE','REVISE'])
def test_completion_requires_actual_bound_approval(batch,tmp_path,verdict):
    work=tmp_path/'work';work.mkdir();raw=json.dumps({'verdict':verdict}).encode();(work/'review.json').write_bytes(raw)
    reserve(batch);batch.finish_scientific(recovery.REPLACEMENT,{'workspace':str(work),'output_sha256':{'review.json':digest(raw)}},'COMPLETE')
    if verdict=='APPROVE':assert recovery.completion(batch,recovery.RUN)==[recovery.rec.FAILED,recovery.FAILED]
    else:
        with pytest.raises(ValueError,match='NOT_APPROVED'):recovery.completion(batch,recovery.RUN)
    (work/'review.json').write_text('{}')
    with pytest.raises(ValueError,match='NOT_APPROVED'):recovery.completion(batch,recovery.RUN)


def test_search_setup_refusal_spends_no_call(lane,monkeypatch):
    from orchestrator import manual_driver
    d=manual_driver.Driver(lane,runner=fake_author);d.advance()
    def never(*args):pytest.fail('A setup refusal must occur before invoking any client')
    monkeypatch.setattr(manual_stage,'invoke',never);d.runner=never
    monkeypatch.setattr(manual_stage,'preflight',lambda:{})
    monkeypatch.setattr(manual_stage,'data_access_guard',lambda *a:{})
    def transport(work,*args):
        measurement=json.loads((work/'input-measurement.json').read_text())
        assert measurement['workspace_files']
        ref=measurement['workspace_files'][0];target=work/ref['path']
        target.chmod(0o600)  # This test owns the synthetic scratch file, not preserved evidence.
        target.write_text('Changed synthetic fixture')
        return {'synthetic_transport':True}
    monkeypatch.setattr(manual_stage,'transport_check',transport)
    with pytest.raises(ValueError):d._model_step(d.current())
    assert d.store.db.execute('SELECT count(*) FROM manual_calls').fetchone()[0]==1
