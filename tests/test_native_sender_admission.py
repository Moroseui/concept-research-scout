import json
import sqlite3
from pathlib import Path
from types import SimpleNamespace as NS
import pytest
from tools import item4_diagnostic_native_runtime as m

ID='af4547778fe7e1f35698089607ab524d08346618131512c232670b7ccbf02ab8'
PROOF={'id':ID,'classification':'EXACT_TERMINAL_PRE_SDK_AUTHOR22_ADMIN_ONLY','proof_sha256':'fa1883b02291bd74d273b1c1b0c00052d48dd7b6f01c52f2f73731426384294a'}

@pytest.mark.parametrize('damage',[None,'reject','finding','source','report','scope','source-bytes','wrong-id','missing-row','bad-proof'])
def test_native_grant_rechecks_approved_proof_without_relabel_or_write(tmp_path,monkeypatch,damage):
    from orchestrator import autonomy_review as ar
    ledger=tmp_path/'ledger';packet=ledger/'a27b9e0bdf19ec037711ff079725ee83afe02e4d2b95fd751ac1ab9a7e81e04d';packet.mkdir(parents=True)
    source=tmp_path/'source';(source/'tools').mkdir(parents=True);(source/'docs').mkdir()
    proof=dict(PROOF)
    if damage=='bad-proof':proof['classification']='unverified'
    module=source/'tools/review_sender_recovery_once.py';module.write_text("DOC='docs/proof.json'\ndef qualify(row,binding,read_file):\n assert row['id']==binding['call_id']\n return "+repr(proof)+'\n')
    doc=source/'docs/proof.json';doc.write_text(json.dumps({'call_id':ID if damage!='wrong-id' else 'other'}))
    manifest={'source_files':{str(p.relative_to(source)):m.sha(p.read_bytes()) for p in [module,doc]}}
    (packet/'packet-manifest.json').write_text(json.dumps(manifest));(packet/'packet-manifest.json').chmod(0o600)
    if damage=='source-bytes':module.write_text(module.read_text()+'# changed\n')
    approval={'verdict':'APPROVE','findings':[],'source_sha':'41b93574a0ad0fb546745095ff0078debd6f133d',
        'report_sha256':'a54ef800461b974db328d18fba65e4d6d819044a3a003d9699a59603b0710139','change_id':'item4-sender-recovery-20261010'}
    if damage=='reject':approval['verdict']='REJECT'
    elif damage=='finding':approval['findings']=['unresolved']
    elif damage in {'source','report','scope'}:approval[{'source':'source_sha','report':'report_sha256','scope':'change_id'}[damage]]='wrong'
    monkeypatch.setattr(ar,'verify_result',lambda path:approval);monkeypatch.setattr(m,'LEDGER',ledger)
    prefix='/var/lib/research-system-manual-sprint10-deployment/directions-20261006/item4-sender-recovery-20261010/packet/source/'
    monkeypatch.setattr(m,'trusted',lambda path:source/str(path).removeprefix(prefix))
    db=sqlite3.connect(':memory:');db.row_factory=sqlite3.Row;db.execute('CREATE TABLE autonomy_calls(id TEXT,status TEXT,charge INTEGER)')
    if damage!='missing-row':db.execute('INSERT INTO autonomy_calls VALUES(?,?,?)',(ID,'UNCERTAIN',123))
    before=[dict(r) for r in db.execute('SELECT * FROM autonomy_calls')];changes=db.total_changes
    if damage is None:assert m.sender_closed_call(NS(db=db))==ID
    else:
        with pytest.raises(ValueError):m.sender_closed_call(NS(db=db))
    assert db.total_changes==changes and [dict(r) for r in db.execute('SELECT * FROM autonomy_calls')]==before


def test_closure_extension_is_only_current_item_run_and_account_owner(monkeypatch):
    from orchestrator import spending_continuation as s,item4_diagnostic_native as d,modal_native_synthetic as n
    monkeypatch.setattr(s,'closed_ids',lambda batch,run:{'original'})
    monkeypatch.setattr(d,'document',lambda *args:{'closed_calls':{}})
    batch=object();accounts=NS(batch=batch);seen=[]
    monkeypatch.setattr(m,'sender_closed_call',lambda owner:(seen.append(owner) or ID))
    restore=m.connect_closed(accounts)
    try:
        assert s.closed_ids(batch,'different-run')=={'original'} and seen==[]
        assert s.closed_ids(batch,n.RUN)=={'original',ID} and seen==[batch]
        with pytest.raises(ValueError,match='CLOSED_OWNER'):s.closed_ids(object(),n.RUN)
    finally:restore()
    assert s.closed_ids(batch,n.RUN)=={'original'}
