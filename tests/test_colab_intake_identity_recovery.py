import copy
import json
import sqlite3
from types import SimpleNamespace
import pytest
from tools import colab_intake_identity_recovery as m


def fixture(tmp_path, monkeypatch):
    b = copy.deepcopy(m.binding()); lane = m.mapped(tmp_path, m.LANE)
    work = m.mapped(tmp_path, b['workspace']); ledger = m.mapped(tmp_path, m.LEDGER)
    for p in [lane, work/'evidence', ledger.parent]: p.mkdir(mode=0o700, parents=True)
    (work/'prompt.md').write_bytes(b'synthetic prompt')
    (work/'evidence/view.txt').write_bytes(b'Mean: 0.5')
    cfg = json.dumps({'run_id': b['run_id']}).encode(); (lane/'lane.json').write_bytes(cfg)
    state = {'phase': 'BLOCKED', 'blocked_stage': 'run_spec_review', 'reason': m.REASON,
             'rounds': {'run_spec_author': 1}, 'interventions': [], 'spec': 'unchanged-author-spec'}
    with sqlite3.connect(lane/'jobs.sqlite') as db:
        db.execute('CREATE TABLE manual_state(id PRIMARY KEY,payload)')
        db.execute('INSERT INTO manual_state VALUES(1,?)', (json.dumps(state),))
        db.execute('CREATE TABLE manual_account(id PRIMARY KEY,payload)')
        db.execute('INSERT INTO manual_account VALUES(1,?)', ('{"limit":8,"used":2}',))
        db.execute('CREATE TABLE manual_calls(id PRIMARY KEY,stage,status,receipt)')
        db.executemany('INSERT INTO manual_calls VALUES(?,?,?,?)', [(ident,'run_spec_author','COMPLETE','preserved') for ident in b['row_ids']])
    with sqlite3.connect(ledger) as db:
        db.execute('CREATE TABLE autonomy_calls(id PRIMARY KEY,change_id,status,receipt)')
        db.executemany('INSERT INTO autonomy_calls VALUES(?,?,?,?)', [(ident,b['run_id'],'COMPLETE','preserved-charge') for ident in b['row_ids']])
    for p in tmp_path.rglob('*'): p.chmod(0o700 if p.is_dir() else 0o600)
    b['config_sha256'] = m.sha(cfg)
    monkeypatch.setattr(m, 'binding', lambda: b)
    monkeypatch.setattr(m, 'authority', lambda: {'report_sha256': 'a'*64})
    monkeypatch.setattr(m, 'service_owner', lambda: None)
    monkeypatch.setattr(m, 'held_unit', lambda: None)
    original = m.rows(tmp_path); b['rows_sha256'] = m.sha(m.canonical(original))
    b['workspace_files'] = m.inventory(work); b['workspace_inventory_sha256'] = m.sha(m.canonical(b['workspace_files']))
    return SimpleNamespace(root=tmp_path, lane=lane, work=work, ledger=ledger, b=b,
                           original=original, dest=m.mapped(tmp_path, m.DEST))


def test_exact_premodel_preservation_only_restores_same_review(tmp_path, monkeypatch):
    f = fixture(tmp_path, monkeypatch); global_bytes = f.ledger.read_bytes()
    assert m.apply(tmp_path)['status'] == 'READY_SAME_REVIEW_NO_CALL'
    assert not f.work.exists() and m.inventory(f.dest/'workspace') == f.b['workspace_files']
    assert f.ledger.read_bytes() == global_bytes
    now = m.rows(tmp_path)
    for name in ['manual_calls','manual_account','global_calls']: assert now[name] == f.original[name]
    state = json.loads(now['manual_state'][0]['payload']); old = json.loads(f.original['manual_state'][0]['payload'])
    assert state['phase'] == 'run_spec_review' and state['rounds'] == old['rounds']
    assert state['spec'] == old['spec'] and state['interventions'][-1]['new_allowance'] == 0
    assert json.loads((f.dest/'original-rows.json').read_bytes()) == f.original
    assert m.ready(tmp_path)['model_calls'] == 0
    with pytest.raises(ValueError,match='EXISTING_ATTEMPT_PRESERVED'): m.apply(tmp_path)


@pytest.mark.parametrize('damage', ['review-revise','review-reject','pending','account','extra-call',
    'running','config','file','symlink','extra-file','empty-dir','world-readable','halt','partial-record','approval'])
def test_changed_uncertain_or_scientific_states_refuse_without_mutation(tmp_path, monkeypatch, damage):
    f = fixture(tmp_path, monkeypatch)
    if damage in {'review-revise','review-reject','pending','account','extra-call'}:
        with sqlite3.connect(f.lane/'jobs.sqlite') as db:
            if damage == 'account': db.execute('UPDATE manual_account SET payload=?', ('changed',))
            elif damage == 'extra-call': db.execute('INSERT INTO manual_calls VALUES(?,?,?,?)', ('extra','run_spec_review','COMPLETE','charged'))
            else:
                state=json.loads(f.original['manual_state'][0]['payload'])
                if damage == 'pending':state['pending']={'id':'uncertain'}
                else:state['reason']=damage
                db.execute('UPDATE manual_state SET payload=?',(json.dumps(state),))
    elif damage == 'running':
        with sqlite3.connect(f.ledger) as db: db.execute('INSERT INTO autonomy_calls VALUES(?,?,?,?)', ('other','other','RUNNING','open'))
    elif damage == 'config': (f.lane/'lane.json').write_bytes(b'changed')
    elif damage == 'file': (f.work/'prompt.md').write_bytes(b'changed')
    elif damage == 'symlink': (f.work/'alias').symlink_to(f.work/'prompt.md')
    elif damage == 'extra-file': (f.work/'extra').write_bytes(b'new')
    elif damage == 'empty-dir': (f.work/'extra').mkdir(mode=0o700)
    elif damage == 'world-readable': (f.work/'prompt.md').chmod(0o644)
    elif damage == 'halt': (f.lane/'HALT').write_bytes(b'held')
    elif damage == 'partial-record': f.dest.mkdir(mode=0o700)
    else:
        def refuse(): raise ValueError('INDEPENDENT_APPROVE_REQUIRED')
        monkeypatch.setattr(m,'authority',refuse)
    before = (f.lane/'jobs.sqlite').read_bytes(); global_before = f.ledger.read_bytes()
    with pytest.raises(ValueError): m.apply(tmp_path)
    assert f.work.is_dir() and not (f.dest/'COMPLETE.json').exists()
    assert (f.lane/'jobs.sqlite').read_bytes() == before and f.ledger.read_bytes() == global_before


def test_interruption_after_rename_preserves_originals_and_refuses_repetition(tmp_path, monkeypatch):
    f=fixture(tmp_path,monkeypatch);original=m.inventory
    def interrupted(work):
        if work == f.dest/'workspace':raise OSError('synthetic interruption')
        return original(work)
    monkeypatch.setattr(m,'inventory',interrupted)
    with pytest.raises(OSError):m.apply(tmp_path)
    assert not f.work.exists() and (f.dest/'workspace/prompt.md').read_bytes()==b'synthetic prompt'
    assert not (f.dest/'COMPLETE.json').exists() and m.rows(tmp_path)==f.original
    with pytest.raises(ValueError,match='EXISTING_ATTEMPT_PRESERVED'):m.apply(tmp_path)
