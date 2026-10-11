import sqlite3
from types import SimpleNamespace as NS
import pytest
from tools import review_colab_final_terminal_once as m


def test_exact_adapter_does_not_accept_unrelated_uncertainty():
    calls=[]
    def previous(row,folder):calls.append((row,folder));raise ValueError('ordinary uncertain refusal')
    proof=NS(CALL='exact',qualify=lambda row,binding:('qualified',row,binding))
    verify=m.exact_adapter(previous,proof,{'frozen':True})
    assert verify({'id':'exact'})[0]=='qualified' and not calls
    with pytest.raises(ValueError,match='ordinary uncertain refusal'):verify({'id':'other'},'folder')
    assert calls==[({'id':'other'},'folder')]


@pytest.mark.parametrize('damage',[None,'already-used','no-transaction','original-refusal'])
def test_bootstrap_one_bound_ordinary_transaction(damage):
    db=sqlite3.connect(':memory:');db.execute('create table autonomy_calls(change_id text)')
    if damage=='already-used':db.execute('insert into autonomy_calls values(?)',(m.CHANGE,));db.commit()
    if damage!='no-transaction':db.execute('BEGIN IMMEDIATE')
    seen=[]
    def ordinary(db,proof_root):
        seen.append(proof_root)
        if damage=='original-refusal':raise ValueError('unknown uncertainty or cap refusal')
        return 'ordinary terminal checks'
    wrapped=m.one_administrative_check(ordinary)
    if damage:
        with pytest.raises(ValueError):wrapped(db,'proof-root')
        assert len(seen)==(damage=='original-refusal')
    else:
        assert wrapped(db,'proof-root')=='ordinary terminal checks'
        with pytest.raises(ValueError):wrapped(db,'proof-root')
        assert len(seen)==1
    db.close()


def test_review_reservation_implementation_is_never_replaced():
    import ast
    from pathlib import Path
    tree=ast.parse(Path(m.__file__).read_text())
    for node in ast.walk(tree):
        if isinstance(node,ast.Assign):
            assert all('ReviewQueue.reserve' not in ast.unparse(target) for target in node.targets)


@pytest.mark.parametrize('fault',[None,'verdict','findings','source_sha','report_sha256','change_id','proof-bytes'])
def test_new_admin_request_reuses_genuinely_approved_terminal_qualifier(tmp_path,monkeypatch,fault):
    import json
    prior={'source_files':{'orchestrator/colab_author_terminal.py':'a'*64,'docs/COLAB_FINAL_AUTHOR_TERMINAL_PRIVATE.json':'b'*64}}
    (tmp_path/'packet-manifest.json').write_text(json.dumps(prior))
    report={'verdict':'APPROVE','findings':[],'source_sha':'f57ab420f55596b53b0781e904d817fde4b85423',
        'report_sha256':'8bb46b53c0ed72791f1bebbea4bf3433d9d020167d98e4ac902a6fa15583c0d8',
        'change_id':'colab-finalization-terminal-native-20261011'}
    if fault and fault!='proof-bytes':report[fault]=['finding'] if fault=='findings' else 'changed'
    if fault=='proof-bytes':prior['source_files']['orchestrator/colab_author_terminal.py']='c'*64
    monkeypatch.setattr(m,'trusted',lambda p:tmp_path/'packet-manifest.json' if p.name=='packet-manifest.json' else tmp_path)
    ar=NS(verify_result=lambda path:report)
    if fault:
        with pytest.raises(ValueError):m.approved_terminal(ar,prior)
    else:m.approved_terminal(ar,prior)
