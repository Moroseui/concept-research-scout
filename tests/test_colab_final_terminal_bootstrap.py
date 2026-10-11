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
