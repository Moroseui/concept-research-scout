"""Disposable administrative install: real scope/receipt/state checks, no host service."""
import io
import json
import os
from pathlib import Path
import tarfile
from copy import deepcopy
import pytest
from orchestrator import server_review_install as admin, deployment_review as gate
from orchestrator import terminal_review, inspection_runner


def put(path,raw):
    path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(raw)


@pytest.fixture
def fixture(tmp_path,monkeypatch):
    base=tmp_path/'protected';sources=tmp_path/'enablers';sources.mkdir();base.mkdir()
    config_path=tmp_path/'server-reviews.json';source='a'*40
    monkeypatch.setattr(admin,'BASE',base);monkeypatch.setattr(admin,'SOURCES',sources);monkeypatch.setattr(admin,'CONFIG',config_path)
    monkeypatch.setattr(admin.os,'getuid',lambda:0)
    monkeypatch.setattr(gate,'protected',lambda *a,**k:None)
    monkeypatch.setattr(gate,'read',lambda p,**k:Path(p).read_bytes())
    monkeypatch.setattr(admin.os,'chown',lambda *args:None)
    monkeypatch.setattr(admin.os,'fchown',lambda *args:None)
    config={'source':source,'permit':{'control_snapshot':{'paused':1,'revision':19,'steering':[]}}}
    config_raw=gate.encoded(config);previous=b'{"source":"preserved-science"}'
    archive=io.BytesIO()
    with tarfile.open(fileobj=archive,mode='w:gz') as tar:
        raw=b'pass\n';info=tarfile.TarInfo('snapshot/module.py');info.size=len(raw);tar.addfile(info,io.BytesIO(raw))
    arc=archive.getvalue()
    target={'uid':0,'gid':0,'mode':0o600,'sha256':gate.digest(config_raw)}
    witness='/etc/research-system/live-research/controller.json'
    proposal={'schema':admin.SCHEMA,'review_profile':'operator-terminal-review/v1','source':source,
        'source_root':str(sources/source),'source_files':{'module.py':gate.digest(b'pass\n')},
        'archive_sha256':gate.digest(arc),'targets':{str(config_path):target},
        'previous_files':{witness:{'uid':0,'gid':987,'mode':0o640,'sha256':gate.digest(previous)}},
        'recovery_sha256':gate.digest(b'Preserve scientific state.'),'changes':[]}
    bundle=base/'bundles'/gate.digest(gate.encoded(proposal));bundle.mkdir(parents=True)
    for name,raw in [('proposal.json',gate.encoded(proposal)),('source.tar.gz',arc),
        ('literals/'+gate.digest(config_raw),config_raw),('literals/'+gate.digest(previous),previous),
        ('terminal-accounting.json',b'{"synthetic":true}')]:put(bundle/name,raw)
    read=gate.read
    def observed(path,**kwargs):
        if str(path)==witness:return previous
        return read(path,**kwargs)
    monkeypatch.setattr(gate,'read',observed);monkeypatch.setattr(gate,'access',lambda path:(0,987,0o640))
    original_review={'execution':{'synthetic':True},'session':'original-session','model':'original-model','change_heads':{}}
    monkeypatch.setattr(admin,'original_review',lambda *a:deepcopy(original_review))
    monkeypatch.setattr(terminal_review,'load',lambda *a:({'execution':{'synthetic':True},'terminal_profile':'operator-terminal-review/v1'},{}))
    configdir=tmp_path/'science-config';put(configdir/'broker.json',b'{}')
    monkeypatch.setattr(admin.native,'CONFIG',configdir)
    monkeypatch.setattr(admin.native,'require_terminal_accounting',lambda *a:{'accounting':'already charged once'})
    calls=[]
    monkeypatch.setattr(admin.native,'source_inventory',lambda root,files,pin:calls.append(('source-checked',str(root))))
    monkeypatch.setattr(admin.native,'state_fingerprint',lambda broker:{'sha256':'f'*64,'files':7})
    monkeypatch.setattr(inspection_runner,'current_control',lambda config:{'paused':1,'revision':19,'steering':[]})
    active=tmp_path/'scientific-active.json';put(active,b'preserved scientific selection');monkeypatch.setattr(gate,'ACTIVE',active)
    def atomic(path,raw,metadata):
        assert Path(path) in (config_path,base/'active.json')
        put(Path(path),raw)
    monkeypatch.setattr(admin.native,'atomic',atomic)
    return {'bundle':bundle,'base':base,'sources':sources,'config':config,'config_path':config_path,
            'proposal':proposal,'source':source,'active':active,'calls':calls}


def test_one_administrative_install_preserves_scientific_release_and_requeries(fixture):
    f=fixture;first=admin.install(f['bundle']);second=admin.install(f['bundle'])
    assert first==second and first['models_started'] is False
    assert first['state_before']==first['state_after']
    assert f['active'].read_bytes()==b'preserved scientific selection'
    assert (f['sources']/f['source']/'module.py').read_bytes()==b'pass\n'
    assert f['config_path'].read_bytes()==gate.encoded(f['config'])


@pytest.mark.parametrize('failure',['review','accounting','control','partial','existing-source'])
def test_unmet_gate_refuses_before_config_or_new_source(fixture,monkeypatch,failure):
    f=fixture
    def refused(*a):raise ValueError('synthetic unmet gate')
    if failure=='review':monkeypatch.setattr(admin,'original_review',refused)
    elif failure=='accounting':monkeypatch.setattr(admin.native,'require_terminal_accounting',refused)
    elif failure=='control':monkeypatch.setattr(inspection_runner,'current_control',lambda c:{'revision':20,'paused':1,'steering':[]})
    elif failure=='partial':put(f['bundle']/'install-intent.json',b'{}')
    else:(f['sources']/f['source']).mkdir()
    with pytest.raises(ValueError):admin.install(f['bundle'])
    assert not f['config_path'].exists()
    assert f['active'].read_bytes()==b'preserved scientific selection'


def test_drift_after_copy_remains_failed_with_original_intent(fixture,monkeypatch):
    f=fixture;count=[]
    def fingerprint(broker):count.append(1);return {'sha256':str(len(count))*64,'files':7}
    monkeypatch.setattr(admin.native,'state_fingerprint',fingerprint)
    with pytest.raises(ValueError,match='SCIENTIFIC_STATE_CHANGED'):admin.install(f['bundle'])
    assert (f['bundle']/'install-intent.json').exists() and not (f['bundle']/'install-receipt.json').exists()
    assert not (f['base']/'active.json').exists()
    with pytest.raises(ValueError,match='PARTIAL_INSTALL'):admin.install(f['bundle'])


def test_changed_receipt_or_configuration_cannot_enable(fixture):
    f=fixture;admin.install(f['bundle'])
    f['config_path'].write_bytes(b'{}')
    with pytest.raises(ValueError,match='CONFIGURATION_CHANGED'):
        admin.verify(f['sources']/f['source'],f['source'],f['config'])


@pytest.mark.parametrize('profile', ['operator-terminal-review/v1','server-terminal-review/v1','unknown-review/v1'])
def test_profile_scope_binds_exact_protected_proposal(fixture,profile):
    f=fixture;proposal=deepcopy(f['proposal']);proposal['review_profile']=profile
    raw=gate.encoded(proposal);target=f['base']/'bundles'/gate.digest(raw)
    f['bundle'].rename(target);put(target/'proposal.json',raw)
    if profile=='unknown-review/v1':
        with pytest.raises(ValueError,match='FIXED_SCOPE'):admin.proposal(target)
    else:
        checked,*_=admin.proposal(target)
        assert checked['review_profile']==profile


@pytest.mark.parametrize('profile', ['operator-terminal-review/v1','server-terminal-review/v1'])
def test_external_bootstrap_reader_never_uses_candidate(fixture,monkeypatch,profile):
    from orchestrator import remote_supervisor
    from types import SimpleNamespace
    calls=[]
    monkeypatch.undo()
    # Exercise the real original_review, not the fixture's replacement.
    monkeypatch.setattr(gate,'protected',lambda *a,**kw:None)
    monkeypatch.setattr(remote_supervisor,'checked_source',lambda root,pin:calls.append((root,pin)))
    def run(argv,**kw):
        calls.append((argv,kw));return SimpleNamespace(stdout=b'{"execution":{"original":true}}')
    monkeypatch.setattr(admin.subprocess,'run',run)
    result=admin.original_review(Path('/protected/fixed-bundle'),{'review_profile':profile,'source':'f'*40})
    expected=(admin.SERVER_BOOTSTRAP_ROOT,admin.SERVER_BOOTSTRAP_SOURCE) if profile=='server-terminal-review/v1' else (admin.BOOTSTRAP_ROOT,admin.BOOTSTRAP_SOURCE)
    assert calls[0]==expected and result['execution']['original'] is True
    argv,kw=calls[1]
    assert kw['cwd']==expected[0] and kw['env']['PYTHONPATH']==str(expected[0])
    assert "t.load" in argv[3] and 'g.change_review' in argv[3]
    assert 'f'*40 not in str(argv)+str(kw)
    assert kw['check'] is True and kw['timeout']==60


def test_unrecognized_bootstrap_profile_never_starts_reader(monkeypatch):
    def forbidden(*a,**kw):raise AssertionError('must refuse before external reader')
    monkeypatch.setattr(admin.subprocess,'run',forbidden)
    with pytest.raises(ValueError,match='REVIEW_PROFILE_REQUIRED'):
        admin.original_review(Path('/protected/fixed-bundle'),{'review_profile':'unknown'})
