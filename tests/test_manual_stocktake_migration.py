"""Whole promotion/migration/admission path; synthetic provenance clearly scoped.
Only root ownership trust is simulated on the laptop. No business validators
(manual verify, matrix, promotion, migration or local/global reservation) mocked.
Private captured state is optional outside operator verification hosts.
"""
import json
import os
from pathlib import Path
import sqlite3
import pytest
from orchestrator import stocktake_recovery as rec, stocktake_manual_review as manual
from orchestrator import private_records
from orchestrator.manual_executor import read, digest
from orchestrator.analysis_driver import AnalysisDriver
from tools import manual_promotion as promotion, deploy_manual_lane as deploy
from stocktake_migration_fixture import prepare, qualify, matrix

@pytest.fixture
def integration(tmp_path,monkeypatch):
    evidence=os.environ.get('STOCKTAKE_FAILED_EVIDENCE')
    if not evidence:pytest.skip('Private retained rows supplied on operator verification hosts')
    f=prepare(tmp_path/'integration',Path(evidence))
    # Simulate root ownership only. The actual files and private modes are real.
    monkeypatch.setattr(manual,'trusted',lambda p:Path(p))
    monkeypatch.setenv('RESEARCH_MANUAL_RUNTIME_CONFIG',str(f['runtime']))
    qualify(f)
    return f


def test_real_promote_migrate_and_linked_reservation_wal(integration):
    f=integration;host=f['host'];old=f['oldstate']
    holders=[]
    for path in (old/'jobs.sqlite',f['ledger']/'jobs.sqlite'):
        db=sqlite3.connect(path);db.execute('PRAGMA journal_mode=WAL');db.execute('PRAGMA wal_autocheckpoint=0')
        db.execute('CREATE TABLE scratch_wal_marker(value)');db.execute("INSERT INTO scratch_wal_marker VALUES('synthetic WAL marker')");db.commit();holders.append(db)
        assert Path(str(path)+'-wal').stat().st_size>0
    before=rec.state_snapshot(old)
    with rec.connect(old/'jobs.sqlite') as db:oldrows=rec.rows(db,'manual_calls')
    with rec.connect(f['ledger']/'jobs.sqlite') as db:failed=rec.original_row(db,'autonomy_calls',rec.GLOBAL_ROW)
    installed=promotion.promote(*f['args'],entrypoint='analysis',stocktake_recovery=True)
    root=deploy.bound(host,installed['layout']['state'])/'repository';state=root.parent/'lane'
    path=matrix(f,root)
    result=rec.migrate(old,state,root,f['folder']/'report.md',path,filesystem_root=host)
    assert result['status']=='APPLIED_SCRATCH_NO_MODEL_CALL' and rec.state_snapshot(old)==before
    d=AnalysisDriver(state);rec.validate_runtime(d)
    ident,n,receipt=d.store.reserve_call(rec.RUN,rec.STAGE,d.config['source'],d.config['branch'],d.config['policy'],{'test_only':'NO MODEL CLIENT'})
    assert n==2 and receipt['linked_recovery_of']==rec.FAILED
    assert rec.original_row(d.store.batch.db,'autonomy_calls',rec.GLOBAL_ROW)==failed
    assert rec.rows(d.store.db,'manual_calls')[0]==oldrows[0]
    assert rec.state_snapshot(old)==before
    assert rec.permit(d.store,rec.RUN)['evidence_preconditions']['status']=='READABLE_TRUSTED_PRIVATE'
    with pytest.raises(ValueError,match='UNCERTAIN'):
        d.store.reserve_call(rec.RUN,rec.STAGE,d.config['source'],d.config['branch'],d.config['policy'],{})
    # Scratch row remains honestly RUNNING: nothing claimed a scientific outcome.
    assert d.store.db.execute('SELECT status FROM manual_calls WHERE id=?',(ident,)).fetchone()[0]=='RUNNING'
    for db in holders:db.close()


def test_missing_manual_entrypoint_refuses_inputs_and_actual_promote(integration):
    f=integration;p=f['folder']/'report.md';p.write_text(p.read_text().replace('analysis_entrypoint: orchestrator.analysis_driver\n',''))
    with pytest.raises(ValueError,match='MANUAL_ANALYSIS_ENTRYPOINT_REQUIRED'):manual.inputs(f['folder'],filesystem_root=f['host'])
    args=list(f['args']);args[6]=digest(p.read_bytes())
    with pytest.raises(ValueError,match='EXACT_ANALYSIS_ENTRYPOINT_APPROVAL_REQUIRED'):
        promotion.promote(*args,entrypoint='analysis',stocktake_recovery=True)
    assert not deploy.bound(f['host'],promotion.layout(args[2])['record']).exists()


def test_matrix_is_bound_to_selected_installation_and_time(integration):
    f=integration;installed=promotion.promote(*f['args'],entrypoint='analysis',stocktake_recovery=True)
    root=deploy.bound(f['host'],installed['layout']['state'])/'repository';path=matrix(f,root);value=read(path)
    for wrong in ({**value,'recorded_at':0},{**value,'installation':{**value['installation'],'installed_sha256':'0'*64}},
                  {**value,'installation':{**value['installation'],'filesystem_root':'/'}}):
        with pytest.raises(ValueError,match='AFTER_SELECTED_INSTALL'):rec.validate_matrix(wrong,root,filesystem_root=f['host'])
    assert not (root.parent/'lane').exists()
