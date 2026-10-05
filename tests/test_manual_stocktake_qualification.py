"""One-off manual qualification tests; root/operator provenance is synthetic here.

Real root trust and permission checks remain in manual_host_guard/private_records.
These tests never constitute an independent report or production authority.
"""
import json
from pathlib import Path
import pytest
from orchestrator import stocktake_manual_review as manual, stocktake_recovery as recovery
from orchestrator import autonomy_review as review, private_records
from orchestrator.autonomy_review_runner import ReviewQueue
from tools import manual_promotion


@pytest.fixture
def saved(tmp_path,monkeypatch):
    monkeypatch.setattr(manual,'ROOT',tmp_path/'manual')
    queue=ReviewQueue(tmp_path/'ledger');monkeypatch.setattr(manual,'LEDGER',queue.folder/'jobs.sqlite')
    # Root provenance is explicitly simulated; actual private modes still checked.
    monkeypatch.setattr(manual,'trusted',lambda p:private_records.check(p))
    monkeypatch.setattr(manual.os,'geteuid',lambda:0)
    # Unit provenance/privilege boundary simulated; ledger SQL uses a real child.
    import os
    monkeypatch.setattr(manual,'_ledger_owner',lambda:(os.getuid(),{}))
    monkeypatch.setattr(manual,'importer_identity',lambda expected:{'source_sha':expected,'module_sha256':review.sha(Path(manual.__file__).read_bytes()),'module_path':manual.__file__})
    def private_new(path,value,*args,**kwargs):
        raw=value if isinstance(value,bytes) else review.canonical(value)
        with private_records.open_file(path,'xb') as out:out.write(raw)
    monkeypatch.setattr(manual_promotion,'private_new',private_new)
    monkeypatch.setattr(manual_promotion,'private_mode',lambda *a,**k:None)
    packet=tmp_path/'packet';packet.mkdir();(packet/'BRIEF.md').write_text('Synthetic defensive review fixture.')
    manifest={'change_id':manual.CHANGE,'source_sha':'a'*40,'runtime_sha256':recovery.RUNTIME,'round':1,'predecessor':None,
        'files':{'BRIEF.md':review.sha((packet/'BRIEF.md').read_bytes()),'evidence/analysis-plan.json':recovery.PLAN}}
    monkeypatch.setattr(review,'verify_packet',lambda p:manifest)
    monkeypatch.setattr(review,'inventory',lambda p:['BRIEF.md'])
    report=tmp_path/'report.md';original=tmp_path/'operator-return.txt';original.write_text('Synthetic operator-return record; never actual authority.')
    def text(verdict='APPROVE'):
        return ('source_sha: '+manifest['source_sha']+'\nruntime_sha256: '+recovery.RUNTIME+'\npacket_sha256: '+review.sha(review.canonical(manifest))+
            '\nanalysis_entrypoint: orchestrator.analysis_driver\nreviewer_product: Claude Code\nreviewer_model: unavailable\nreviewer_session_id: unavailable\n## Verdict: '+verdict+
            '\n\n## Blockers\n'+('None.' if verdict=='APPROVE' else 'BLOCKER[code/spec mismatch] B1: synthetic defect; repair it.')+
            '\n\n## Inspected scope\nSynthetic fixture only.\n\n## Limitations\nNo genuine reviewer or native session evidence.\n')
    report.write_text(text())
    return packet,report,original,manifest,queue,text


def test_manual_approval_is_distinct_and_counted_once(saved):
    packet,report,original,manifest,queue,_=saved
    raw=report.read_bytes();result=manual.record(packet,report,original,reviewed_importer_source='a'*40)
    assert result['verdict']=='APPROVE' and result['kind']=='OPERATOR_AUTHORIZED_ONE_OFF_MANUAL_NOT_QUEUE_QUALIFIED'
    assert result['reviewer_reported_identity']['reviewer_model']=='unavailable'
    assert report.read_bytes()==raw
    assert manual.record(packet,report,original,reviewed_importer_source='a'*40)==result
    assert queue.db.execute('SELECT count(*) FROM autonomy_calls').fetchone()[0]==1
    assert queue.db.execute('SELECT sum(1) FROM autonomy_calls').fetchone()[0]==1
    assert not any((manual.ROOT/p).exists() for p in ('native-stream.jsonl','process-exit.json'))


def test_rejection_retains_verdict_and_charge(saved):
    packet,report,original,manifest,queue,text=saved;report.write_text(text('CHANGES REQUIRED'))
    result=manual.record(packet,report,original,reviewed_importer_source='a'*40)
    assert result['verdict']=='CHANGES REQUIRED'
    assert queue.db.execute('SELECT count(*) FROM autonomy_calls').fetchone()[0]==1
    assert (manual.ROOT/result['packet_sha256']/'report.md').read_bytes()==report.read_bytes()


@pytest.mark.parametrize('damage',['duplicate_verdict','missing_verdict','conflicting_blocker','source','packet','runtime','missing_identity','wrong_family','unsupported_extra_verdict','missing_entrypoint'])
def test_invalid_report_is_preserved_charged_and_not_qualified(saved,damage):
    packet,report,original,manifest,queue,_=saved;t=report.read_text()
    if damage=='duplicate_verdict':t+='\n## Verdict: APPROVE\n'
    elif damage=='missing_entrypoint':t=t.replace('analysis_entrypoint: orchestrator.analysis_driver','')
    elif damage=='unsupported_extra_verdict':t+='\n## Verdict: IN_PROGRESS\n'
    elif damage=='missing_verdict':t=t.replace('## Verdict: APPROVE','## Judgment')
    elif damage=='conflicting_blocker':t+='\nBLOCKER[budget] B1: unresolved\n'
    elif damage=='source':t=t.replace(manifest['source_sha'],'b'*40)
    elif damage=='packet':t=t.replace(review.sha(review.canonical(manifest)),'0'*64)
    elif damage=='runtime':t=t.replace(recovery.RUNTIME,'0'*64)
    elif damage=='missing_identity':t=t.replace('reviewer_session_id: unavailable','')
    elif damage=='wrong_family':t=t.replace('reviewer_product: Claude Code','reviewer_product: Codex')
    report.write_text(t);result=manual.record(packet,report,original,reviewed_importer_source='a'*40)
    assert result['status']=='MANUAL_REVIEW_NOT_QUALIFIED'
    assert queue.db.execute('SELECT status FROM autonomy_calls').fetchone()[0]=='FAILED'
    with pytest.raises(ValueError,match='PRESERVED_MANUAL_REFUSAL'):manual.record(packet,report,original,reviewed_importer_source='a'*40)
    assert queue.db.execute('SELECT count(*) FROM autonomy_calls').fetchone()[0]==1
    assert (Path(result['folder'])/'report.md').read_text()==t


@pytest.mark.parametrize('damage',['report','operator_return','session_evidence','manifest','receipt','world_readable','missing_charge'])
def test_changed_or_missing_preserved_binding_refuses(saved,damage):
    packet,report,original,manifest,queue,_=saved
    evidence=report.parent/'actual-session.fixture';evidence.write_text('Synthetic session evidence, not a native transcript.')
    result=manual.record(packet,report,original,[evidence],reviewed_importer_source='a'*40);folder=manual.ROOT/result['packet_sha256']
    paths={'report':'report.md','operator_return':'operator-return-original.txt','session_evidence':'actual-session-evidence-01','manifest':'packet-manifest.json','receipt':'qualification.json'}
    if damage in paths:(folder/paths[damage]).write_text('{}')
    elif damage=='world_readable':(folder/'report.md').chmod(0o644)
    elif damage=='missing_charge':queue.db.execute('DELETE FROM autonomy_calls')
    with pytest.raises((ValueError,KeyError)):manual.verify(folder)


def test_root_requirement_refuses_before_record_write(saved,monkeypatch):
    packet,report,original,manifest,queue,_=saved
    monkeypatch.setattr(manual.os,'geteuid',lambda:1003)
    with pytest.raises(ValueError,match='PRESERVATION_ROOT'):manual.record(packet,report,original,reviewed_importer_source='a'*40)
    assert not manual.ROOT.exists()


def test_scientific_uncertainty_is_not_changed_or_reclassified(saved):
    packet,report,original,manifest,queue,_=saved
    queue.db.execute("INSERT INTO autonomy_calls VALUES(?,'scientific',?,1,'2026-01-01','UNCERTAIN','{}','{}')",(recovery.FAILED,recovery.RUN))
    before=tuple(queue.db.execute('SELECT * FROM autonomy_calls WHERE id=?',(recovery.FAILED,)).fetchone())
    manual.record(packet,report,original,reviewed_importer_source='a'*40)
    assert tuple(queue.db.execute('SELECT * FROM autonomy_calls WHERE id=?',(recovery.FAILED,)).fetchone())==before


def test_missing_accounting_or_operator_record_cannot_qualify(saved):
    packet,report,original,manifest,queue,_=saved;value=manual.record(packet,report,original,reviewed_importer_source='a'*40);folder=manual.ROOT/value['packet_sha256']
    (folder/'operator-return-original.txt').unlink()
    with pytest.raises(FileNotFoundError):manual.verify(folder)


@pytest.mark.parametrize('which',['report','operator_return','session_evidence'])
def test_conflicting_reimport_refuses_without_overwrite_or_charge(saved,which):
    packet,report,original,manifest,queue,_=saved
    value=manual.record(packet,report,original,reviewed_importer_source='a'*40);folder=manual.ROOT/value['packet_sha256']
    before={p.name:p.read_bytes() for p in folder.iterdir()}
    evidence=[]
    if which=='report':report.write_text(report.read_text()+'\nChanged report.\n')
    elif which=='operator_return':original.write_text('Different operator return')
    else:
        extra=report.parent/'extra';extra.write_text('Different evidence');evidence=[extra]
    with pytest.raises(ValueError,match='MANUAL_REIMPORT_CONFLICT'):manual.record(packet,report,original,evidence,reviewed_importer_source='a'*40)
    assert {p.name:p.read_bytes() for p in folder.iterdir()}==before
    assert queue.db.execute('SELECT count(*) FROM autonomy_calls').fetchone()[0]==1


def test_manual_daily_cap_remains(saved):
    from datetime import datetime,timezone
    packet,report,original,manifest,queue,_=saved
    day=datetime.now(timezone.utc).date().isoformat()
    for n in range(30):queue.db.execute("INSERT INTO autonomy_calls VALUES(?,'implementation_review','other',1,?,'COMPLETE','{}','{}')",(str(n),day))
    with pytest.raises(ValueError,match='AUTONOMY_DAILY_CALL_LIMIT'):manual.record(packet,report,original,reviewed_importer_source='a'*40)
    assert queue.db.execute('SELECT count(*) FROM autonomy_calls').fetchone()[0]==30


def test_importer_requires_exact_clean_reviewed_commit(tmp_path,monkeypatch):
    import subprocess
    root=tmp_path/'reviewed';(root/'orchestrator').mkdir(parents=True)
    module=root/'orchestrator/stocktake_manual_review.py';module.write_bytes(Path(manual.__file__).read_bytes())
    def git(*args):return subprocess.check_output(['git',*args],cwd=root,text=True).strip()
    git('init','-q');git('add','.');git('-c','user.name=Fixture','-c','user.email=fixture@invalid','commit','-qm','Synthetic importer fixture')
    pin=git('rev-parse','HEAD');monkeypatch.setattr(manual,'__file__',str(module))
    value=manual.importer_identity(pin)
    assert value['source_sha']==pin and value['module_sha256']==manual.digest(module.read_bytes())
    with pytest.raises(ValueError,match='REVIEWED_IMPORTER_COMMIT_REQUIRED'):manual.importer_identity('0'*40)
    module.write_text(module.read_text()+'\n# Unreviewed change\n')
    with pytest.raises(ValueError,match='REVIEWED_IMPORTER_COMMIT_REQUIRED'):manual.importer_identity(pin)


@pytest.mark.parametrize('damage',[None,'duplicate','binding','entrypoint'])
def test_windows_crlf_view_preserves_original_and_all_refusals(saved,damage):
    packet,report,original,manifest,queue,text=saved
    body=text()
    if damage=='duplicate':body+='\n## Verdict: APPROVE\n'
    elif damage=='binding':body=body.replace(manifest['source_sha'],'b'*40)
    elif damage=='entrypoint':body=body.replace('analysis_entrypoint: orchestrator.analysis_driver','')
    raw=body.replace('\n','\r\n').encode();report.write_bytes(raw)
    result=manual.record(packet,report,original,reviewed_importer_source='a'*40)
    if damage:assert result['status']=='MANUAL_REVIEW_NOT_QUALIFIED'
    else:assert result['verdict']=='APPROVE' and result['report_sha256']==manual.digest(raw)
    folder=manual.ROOT/review.sha(review.canonical(manifest))
    assert (folder/'report.md').read_bytes()==raw and report.read_bytes()==raw


def test_genuine_returned_round1_keeps_rejection_and_original_bytes(tmp_path,monkeypatch):
    import os
    evidence=os.environ.get('STOCKTAKE_MANUAL_ROUND1')
    if not evidence:pytest.skip('Private genuine manual original supplied on operator verification hosts')
    source=Path(evidence);raw=(source/'report.md').read_bytes();manifest=json.loads((source/'packet-manifest.json').read_bytes())
    packet=review.sha(review.canonical(manifest));folder=tmp_path/str(manual.ROOT).lstrip('/')/packet;folder.mkdir(parents=True)
    (folder/'report.md').write_bytes(raw);(folder/'packet-manifest.json').write_bytes(review.canonical(manifest))
    # Root/operator provenance simulated only for this parser test, never recorded.
    (folder/'operator-return-original.txt').write_text('SYNTHETIC parser fixture only')
    (folder/'evidence-files.json').write_bytes(review.canonical({'operator-return-original.txt':manual.digest((folder/'operator-return-original.txt').read_bytes())}))
    monkeypatch.setattr(manual,'trusted',lambda p:Path(p))
    value=manual.inputs(folder,filesystem_root=tmp_path)
    assert value['verdict']=='CHANGES REQUIRED' and value['analysis_entrypoint'] is None
    assert value['report_sha256']=='9d1b76c5179c8c8bf073a82ca7547c1586332b2f61ac64f5f546fef5d122826f'
    assert (source/'report.md').read_bytes()==raw and (folder/'report.md').read_bytes()==raw


def test_missing_existing_ledger_refuses_without_creating_database(saved,monkeypatch):
    import sqlite3
    packet,report,original,manifest,queue,_=saved
    missing=queue.folder/'missing.sqlite'
    monkeypatch.setattr(manual,'LEDGER',missing)
    with pytest.raises(ValueError,match='unable to open database'):
        manual.record(packet,report,original,reviewed_importer_source='a'*40)
    assert not missing.exists()
    assert queue.db.execute('SELECT count(*) FROM autonomy_calls').fetchone()[0]==0



def test_root_receipt_failure_rolls_back_owner_transaction(saved,monkeypatch):
    packet,report,original,manifest,queue,_=saved
    original_new=manual_promotion.private_new
    def fail_receipt(path,*a,**kw):
        if Path(path).name=='qualification.json':raise OSError('synthetic root receipt failure')
        return original_new(path,*a,**kw)
    monkeypatch.setattr(manual_promotion,'private_new',fail_receipt)
    with pytest.raises(OSError,match='synthetic root receipt failure'):
        manual.record(packet,report,original,reviewed_importer_source='a'*40)
    assert queue.db.execute('SELECT count(*) FROM autonomy_calls').fetchone()[0]==0
    assert queue.db.execute('SELECT count(*) FROM jobs').fetchone()[0]==0


def test_owner_transaction_refuses_root():
    import subprocess,json
    result=subprocess.run(['/usr/bin/python3','-I','-c',manual.LEDGER_WRITER],
        input=json.dumps({'uid':0})+'\n',capture_output=True,text=True)
    assert result.returncode and 'LEDGER_WRITER_PRIVILEGES' in result.stderr


def test_navigation_one_round_scope_preserves_original_authority(saved):
    packet,report,original,manifest,queue,text=saved
    manifest['change_id']=manual.NAVIGATION
    report.write_text(text())
    result=manual.record(packet,report,original,reviewed_importer_source='a'*40)
    assert result['operator_approval_sha256']==manual.NAV_APPROVAL
    assert result['round']==1 and result['kind']=='OPERATOR_AUTHORIZED_ONE_OFF_MANUAL_NOT_QUEUE_QUALIFIED'
    assert manual.record(packet,report,original,reviewed_importer_source='a'*40)==result
    assert queue.db.execute('SELECT COUNT(*) FROM autonomy_calls').fetchone()[0]==1
    # A new packet never creates a second opportunity under this authority.
    manifest['source_sha']='b'*40;report.write_text(text())
    with pytest.raises(ValueError,match='MANUAL_REVIEW_TWO_ROUND_LIMIT'):
        manual.record(packet,report,original,reviewed_importer_source='a'*40)
    assert queue.db.execute('SELECT COUNT(*) FROM autonomy_calls').fetchone()[0]==1
    assert manual.scope(manual.CHANGE)==(manual.DECISION,manual.APPROVAL,2)
