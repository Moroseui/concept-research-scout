import json
import sqlite3
from types import SimpleNamespace
import pytest
from tools import item4_scientific_revision_component as c
from tools import install_item4_scientific_revision as install


def test_held_unit_changes_only_entrypoint_and_has_same_file_contract():
    original='User=partho\nGroup=partho\nExecStartPre=+/unchanged\nNoNewPrivileges=true\nProtectSystem=strict\nExecStart=/usr/bin/python3 -s -B /opt/research-system/manual-repair-helpers/item4-runtime-binding-repair-20261008/tools/item4_scientific_revision_component.py run\n'
    actual=install.unit_bytes(original).decode()
    assert [x for x in actual.splitlines() if not x.startswith('ExecStart=')]==[x for x in original.splitlines() if not x.startswith('ExecStart=')]
    assert str(c.ROOT/'tools/item4_scientific_revision_component.py')+' run' in actual
    assert set(install.FILES)==set(c.FILES)
    with pytest.raises(ValueError):install.unit_bytes(original+original)


@pytest.fixture
def bound(tmp_path,monkeypatch):
    lane=tmp_path/'lane';lane.mkdir();(lane/'lane.json').write_text('{"unchanged":true}')
    local=sqlite3.connect(':memory:');local.row_factory=sqlite3.Row
    globaldb=sqlite3.connect(':memory:');globaldb.row_factory=sqlite3.Row
    for db,table in [(local,'manual_calls'),(globaldb,'autonomy_calls')]:
        db.execute('CREATE TABLE '+table+'(id TEXT,status TEXT,receipt TEXT)')
        for i in range(6):db.execute('INSERT INTO '+table+' VALUES(?,?,?)',(str(i),'UNCERTAIN' if i in (0,4) else 'COMPLETE','original'))
    b={'configuration_sha256':c.sha((lane/'lane.json').read_bytes()),
       'local_calls':{r['id']:c.sha(c.canonical(dict(r))) for r in local.execute('SELECT * FROM manual_calls')},
       'global_calls':{r['id']:c.sha(c.canonical(dict(r))) for r in globaldb.execute('SELECT * FROM autonomy_calls')}}
    d=SimpleNamespace(state=lane,config={'run_id':c.RUN},store=SimpleNamespace(db=local,batch=SimpleNamespace(db=globaldb)))
    calls=[];helper=SimpleNamespace(grant=lambda *a:calls.append('qualified-originals'))
    monkeypatch.setattr(c,'LANE',lane)
    return d,b,helper,calls


def test_prior_receipts_and_qualification_reused_without_relabelling(bound):
    d,b,h,calls=bound;c.originals(d,b,h,{},None)
    assert calls==['qualified-originals']
    assert d.store.db.execute("SELECT count(*) FROM manual_calls WHERE status='UNCERTAIN'").fetchone()[0]==2


@pytest.mark.parametrize('damage',['local','global','config','run','qualification'])
def test_changed_original_or_unknown_qualification_refuses(bound,damage):
    d,b,h,calls=bound
    if damage=='local':d.store.db.execute("UPDATE manual_calls SET receipt='changed' WHERE id='4'")
    elif damage=='global':d.store.batch.db.execute("UPDATE autonomy_calls SET status='COMPLETE' WHERE id='4'")
    elif damage=='config':(d.state/'lane.json').write_text('{}')
    elif damage=='run':d.config['run_id']='other'
    else:
        def reject(*a):raise ValueError('ORIGINAL_NATIVE_PROOF_CHANGED')
        h.grant=reject
    with pytest.raises(ValueError):c.originals(d,b,h,{},None)


@pytest.mark.parametrize('name',['run_spec_author-5','run_spec_author-21','run_spec_review-6','run_spec_author-6/child'])
def test_sender_cannot_target_another_role_or_unapproved_author(name):
    with pytest.raises(ValueError):c.work_number(c.STATE/'item4/lane-scientific-workspaces'/name)


def test_runtime_connection_preserves_modules_and_refreshes_imported_scope_aliases(monkeypatch):
    from pathlib import Path
    from orchestrator import experiment_environment_requirements as req, manual_context as context
    from orchestrator import modal_development_inputs as source, experiment_preprocessing as prep
    from orchestrator import modal_preprocessing_provider as provider, experiment_worker as worker
    from orchestrator import experiment_modal_package as bridge, experiment_preprocessing_dispatch as dispatch
    original_modules=(req,source,prep,provider,worker,bridge,dispatch)
    changes=[(context,'workspace_artifact'),(context,'build'),(req,'runtime_preprocessing'),(source,'frozen_auxiliary'),(source,'AUXILIARY_CAPTURE'),
        (prep,'scope'),(prep,'execute'),(provider,'input_files'),(worker,'SUPPORT_FILES'),
        (worker,'execute'),(bridge,'SUPPORT_FILES'),(bridge,'WORKER'),
        (dispatch,'scientific_scope'),(dispatch,'validate_selection')]
    for mod,name in changes:monkeypatch.setattr(mod,name,getattr(mod,name))
    root=Path(__file__).resolve().parents[1];monkeypatch.setattr(c,'ROOT',root)
    c.connect_runtime()
    import sys
    assert all(sys.modules[mod.__name__] is mod for mod in original_modules)
    assert dispatch.scientific_scope is prep.scope
    assert dispatch.validate_selection.__globals__['scientific_scope'] is prep.scope
    assert dispatch.validate_selection.__globals__['provider'] is provider
    assert provider.input_files.__globals__['source'] is source
    assert bridge.WORKER==root/'orchestrator/experiment_worker.py'
    assert bridge.SUPPORT_FILES==worker.SUPPORT_FILES
    assert 'orchestrator/experiment_environment_requirements.py' in worker.SUPPORT_FILES
    assert set(bridge.support_files())==set(worker.SUPPORT_FILES)
    assert worker.SUPPORT_FILES==c.SUPPORT_FILES
    assert set(worker.SUPPORT_FILES)<=set(c.FILES)
