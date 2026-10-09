"""Fixed positive stop qualification preserves full charge; no provider calls."""
import copy
import json
from pathlib import Path
from types import SimpleNamespace,ModuleType
import subprocess
import pytest
from orchestrator import modal_terminal_cost as cost,private_records as pr
from orchestrator import item4_preprocessing_fresh_start as fresh
from test_item4_preprocessing_fresh_start import setup


@pytest.fixture
def evidence(setup,tmp_path,monkeypatch):
    p,db=setup;p=copy.deepcopy(p);work=tmp_path/'original-work'
    originals={'create-intent.json':fresh.encoded({'binding_sha256':p['old_row']['id'],
        'run_id':p['old_row']['run'],'cost_clock':{'synthetic_fixture':True}}),
        'created.json':fresh.encoded({'binding_sha256':p['old_row']['id'],'provider_id':p['old_row']['provider_id']})}
    originals.update({str(n)+'.json':b'synthetic original receipt '+str(n).encode() for n in range(6)})
    for name,raw in originals.items():pr.write_bytes(work/name,raw)
    p['evidence_files']={str(work/name):fresh.sha(raw) for name,raw in originals.items()}
    p['event']['evidence_files']=p['evidence_files']
    db.execute('UPDATE events SET payload=?',(fresh.encoded(p['event']).decode(),));db.commit()
    monkeypatch.setattr(fresh,'contract',lambda:p)
    return p,db,work


def test_old_checkpoint_assumption_refuses_real_shape_then_fixed_record_retains_every_charge(evidence):
    p,db,work=evidence;accounts=SimpleNamespace(db=db)
    source=subprocess.check_output(['git','show','7046ad7755af65a73e3042eb6cc28440544715a6:orchestrator/modal_terminal_cost.py'],cwd=Path(__file__).parents[1])
    old=ModuleType('_original_terminal_cost');exec(compile(source,'<unchanged parent>','exec'),old.__dict__)
    with pytest.raises(ValueError,match='^ITEM4_EXPOSURE_TERMINATION_REQUIRED$'):old.record(accounts,p['old_row']['id'],work)
    before=db.total_changes
    for _ in range(2):assert cost.record(accounts,p['old_row']['id'],work) is None
    assert db.total_changes==before
    row=db.execute('SELECT * FROM autonomy_compute').fetchone()
    assert dict(row)=={**p['old_row'],'status':'ACCOUNTED'}
    assert cost.effective(db,row,{})==10_342_400
    assert db.execute('SELECT count(*) FROM events').fetchone()[0]==1


@pytest.mark.parametrize('fault',['live','charge','actual','provider','event','work','exposure',*range(8)])
def test_changed_proof_never_earns_credit_or_a_reconciliation(evidence,fault):
    p,db,work=evidence
    if fault=='live':db.execute("UPDATE autonomy_compute SET status='RUNNING'")
    elif fault=='charge':db.execute('UPDATE autonomy_compute SET reserved_micro_usd=1')
    elif fault=='actual':db.execute('UPDATE autonomy_compute SET actual_micro_usd=1')
    elif fault=='provider':db.execute("UPDATE autonomy_compute SET provider_id='sb-Other'")
    elif fault=='event':db.execute("UPDATE events SET payload='{}'")
    elif fault=='work':work=work/'other'
    elif fault=='exposure':db.execute('INSERT INTO events VALUES(?,?,?)',(p['old_row']['id']+':terminal-exposure',p['old_row']['run'],'{}'))
    else:pr.write_bytes(Path(list(p['evidence_files'])[fault]),b'tampered fixture')
    before=db.total_changes
    with pytest.raises(ValueError,match='FRESH_PREPROCESSING_'):
        cost.record(SimpleNamespace(db=db),p['old_row']['id'],work)
    assert db.total_changes==before


def test_missing_terminal_event_keeps_original_refusal(evidence):
    p,db,work=evidence;db.execute('DELETE FROM events')
    with pytest.raises(ValueError,match='^ITEM4_EXPOSURE_TERMINATION_REQUIRED$'):
        cost.record(SimpleNamespace(db=db),p['old_row']['id'],work)


def test_unknown_pre_science_row_refuses_and_independent_authority_is_required(evidence,monkeypatch):
    p,db,work=evidence;row=dict(p['old_row']);row.update(id='f'*64,status='ACCOUNTED')
    db.execute('INSERT INTO autonomy_compute VALUES(?,?,?,?,?,?,?,?)',tuple(row[k] for k in ['id','run','binding','status','reserved_micro_usd','provider_id','actual_micro_usd','month']))
    db.execute('INSERT INTO events VALUES(?,?,?)',(row['id']+':pre-science-stop',row['run'],fresh.encoded(p['event']).decode()))
    with pytest.raises(ValueError,match='COST_ORIGINAL_IDENTITY'):cost.record(SimpleNamespace(db=db),row['id'],work)
    def unapproved():raise ValueError('UNAPPROVED_FIXTURE')
    monkeypatch.setattr(fresh,'contract',unapproved)
    with pytest.raises(ValueError,match='UNAPPROVED_FIXTURE'):cost.record(SimpleNamespace(db=db),p['old_row']['id'],work)
