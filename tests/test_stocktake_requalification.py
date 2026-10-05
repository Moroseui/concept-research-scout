"""Deterministic parser/finalizer contracts. Any fixture authority is synthetic."""
import ast
import json
import os
from pathlib import Path
import pytest
from orchestrator import stocktake_review_requalification as saved, stocktake_review_recovery as recovery
from orchestrator.manual_executor import digest
from test_manual_lane import lane, root

ROOT=Path(__file__).resolve().parents[1]


def test_exact_authority_and_six_call_checkpoint():
    saved.authority(ROOT);p=saved.checkpoint()
    assert len(p['local_calls'])==len(p['global_calls'])==6
    assert p['pending']['id']==recovery.REPLACEMENT and p['phase']=='BLOCKED'
    assert p['reason']=='OUTPUT_VALIDATION_REFUSED: REVIEW_CATEGORY_OR_VERDICT_CONFLICT'


def test_requalification_never_admits_scientific_call(monkeypatch):
    monkeypatch.setattr(recovery,'global_permit',lambda *args:{'kind':'saved-call6-requalification'})
    with pytest.raises(ValueError,match='^REQUALIFICATION_NO_SCIENTIFIC_CALL$'):
        recovery.admission(None,recovery.RUN,recovery.STAGE,recovery.REPLACEMENT,'a'*40,{})


def test_requalification_has_no_reservation_or_allowance_creation():
    tree=ast.parse((ROOT/'orchestrator/stocktake_review_requalification.py').read_text())
    forbidden={'reserve_call','reserve_scientific','initialize_allowance','initialize','model_step','invoke','finish_call','finish_scientific'}
    assert not any(isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and n.func.attr in forbidden for n in ast.walk(tree))
    assert not any(isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id in forbidden for n in ast.walk(tree))


def test_changed_saved_report_refuses(tmp_path):
    target=saved.bound(tmp_path,saved.checkpoint()['pending']['workspace'])/'review.json'
    target.parent.mkdir(parents=True);target.write_text('{}')
    with pytest.raises(ValueError,match='^REQUALIFICATION_SAVED_REPORT_CHANGED$'):saved.saved_report(tmp_path)


def test_genuine_output_through_normal_acceptance_without_charge(lane,tmp_path):
    from orchestrator.manual_driver import Driver
    path=os.environ.get('CALL6_REVIEW_FIXTURE')
    if not path:pytest.skip('Private genuine report required in release verification')
    raw=Path(path).read_bytes();assert digest(raw)==saved.REPORT
    d=Driver(lane);work=tmp_path/'saved';work.mkdir();(work/'review.json').write_bytes(raw)
    receipt={'output_sha256':{'review.json':saved.REPORT},'workspace':str(work)}
    d.store.db.execute('INSERT INTO manual_calls VALUES(?,?,?,?,?)',(recovery.REPLACEMENT,recovery.STAGE,2,'COMPLETE',json.dumps(receipt)))
    before=[tuple(x) for x in d.store.db.execute('SELECT * FROM manual_calls')]
    account=[tuple(x) for x in d.store.db.execute('SELECT * FROM manual_account')]
    value=d.current();value.update(phase='BLOCKED',reason=saved.checkpoint()['reason'],pending={'id':recovery.REPLACEMENT,'stage':recovery.STAGE,'round':2,'workspace':str(work)})
    d.save(value);d.guard();result=d.accept_completed(d.current())
    assert result['phase']=='UPDATE_STATE'
    assert [tuple(x) for x in d.store.db.execute('SELECT * FROM manual_calls')]==before
    assert [tuple(x) for x in d.store.db.execute('SELECT * FROM manual_account')]==account
    assert (work/'review.json').read_bytes()==raw
    assert (d.context/'current/approval-result_interpretation_review-2.json').read_bytes()==raw
