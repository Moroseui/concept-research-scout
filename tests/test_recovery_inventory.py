"""Synthetic offline preservation tests, not live client or approval evidence."""
from copy import deepcopy
import json
import subprocess
from pathlib import Path
import pytest
from orchestrator import recovery_inventory as pages, deployment_review as gate
from orchestrator import install_reviewed_deployment as install
from orchestrator import change_requests as changes, terminal_review as terminal
from test_inspection_admission_recovery import Fixture as OriginalLedger
from test_deployment_preparation import inputs, run as prepare, archived, ACTOR
from test_terminal_deployment_integration import MANDATORY
from test_terminal_review import evidence
from test_terminal_deployment_integration import (terminal_bundle, save_terminal,
    verify, late_charge_host, terminal_transition)
from test_reviewed_deployment_install import host, SHA, SOURCE


@pytest.fixture
def original(tmp_path):
    p = tmp_path/'ledger-data'; p.mkdir()
    fixture = OriginalLedger(p, n=48)
    snapshot = fixture.baseline['snapshot']
    row = {'uid':997,'gid':987,'mode':0o600,'inode':4,'sha256':'d'*64}
    files = {str(p/'science'/('result-%03d.json'%n)): dict(row, inode=n+1) for n in range(6)}
    full = dict(files)
    for name, value in snapshot['files'].items():
        path = Path(snapshot['repository'])/name
        if path.name.endswith(('.lock','-wal','-shm')): continue
        full[str(path)] = {k:value[k] for k in ('uid','gid','mode','inode','sha256')}
    recovery = {'schema':pages.INLINE,'instructions':'Synthetic: retain originals.',
        'directories':{},'units_before':{},'previous_active':{'state':'ABSENT'},
        'preserved_state_sha256':install.inventory_fingerprint(full)['sha256'],
        'preserved_blocked_tasks':{},'terminal_admissions':{
            'ledger':fixture.baseline,'policy_sha256':fixture.baseline['policy_sha256'],
            'non_ledger_files':files,'control_snapshot':{'paused':1,'revision':31}}}
    proposal = {'review_profile':terminal.PROFILE}
    install.validate_recovery(recovery, proposal)
    return recovery, proposal


def paged(original, monkeypatch):
    monkeypatch.setattr(pages, 'MAX_PAGE_BYTES', 800)
    return pages.paginate(*original)


def test_exact_roundtrip_and_historical_inline_identity(original, monkeypatch):
    before = deepcopy(original[0]); descriptor, literals = paged(original, monkeypatch)
    assert len(literals) >= 2 and all(len(raw) <= 800 for raw in literals.values())
    resolved, originals = pages.resolve(descriptor, literals.__getitem__)
    assert resolved == before == original[0] and originals == literals
    install.validate_recovery(resolved, original[1])
    assert pages.resolve(before, lambda _: pytest.fail('Inline must not retrieve')) == (before,{})


@pytest.mark.parametrize('mutation,reason', [
    ('missing','missing'), ('bytes','ORIGINAL_CHANGED'),('sha','ORIGINAL_CHANGED'),
    ('duplicate_page','DUPLICATE_PAGE'),('duplicate_path','DUPLICATE_PATH'),
    ('reversed','ORDER_CHANGED'),('count','INVENTORY_CHANGED'),('size','INVENTORY_CHANGED'),
    ('fingerprint','INVENTORY_CHANGED'),('large','EXPANDED_BOUND'),
    ('boolean','EXPANDED_BOUND'),('mixed','PAGED_BASELINE'),('extra','DESCRIPTOR'),
    ('page_count','COUNT_CHANGED'),('oversized_page','DESCRIPTOR'),('too_many','EXPANDED_BOUND'),
    ('repeated_json_key','CANONICAL_PAGE')])
def test_page_and_boundary_failures(original, monkeypatch, mutation, reason):
    descriptor, literals = paged(original, monkeypatch)
    spec = descriptor['terminal_admissions']['non_ledger_inventory']; item=spec['pages'][0]
    if mutation == 'missing': literals.pop(item['sha256'])
    elif mutation == 'bytes': item['bytes'] += 1
    elif mutation == 'sha': literals[item['sha256']] = b'x'*item['bytes']
    elif mutation == 'duplicate_page': spec['pages'].append(dict(item))
    elif mutation == 'duplicate_path':
        second = spec['pages'][1]; changed = json.loads(literals[second['sha256']])
        changed.update(json.loads(literals[item['sha256']]))
        raw = gate.encoded(changed); monkeypatch.setattr(pages,'MAX_PAGE_BYTES',len(raw)+1)
        sha = gate.digest(raw); literals[sha] = raw
        spec['pages'][1]={'sha256':sha,'bytes':len(raw),'files':len(changed)}
    elif mutation == 'reversed': spec['pages'].reverse()
    elif mutation == 'count': spec['files'] += 1
    elif mutation == 'size': spec['bytes'] += 1
    elif mutation == 'fingerprint': spec['sha256']='e'*64
    elif mutation == 'large': spec['bytes']=pages.MAX_EXPANDED_BYTES+1
    elif mutation == 'boolean': spec['files']=True
    elif mutation == 'mixed': descriptor['terminal_admissions']['non_ledger_files']={}
    elif mutation == 'extra': spec['unreviewed']='yes'
    elif mutation == 'page_count': item['files']+=1
    elif mutation == 'oversized_page': item['bytes']=pages.MAX_PAGE_BYTES+1
    elif mutation == 'too_many': spec['pages']=[item]*(pages.MAX_PAGES+1)
    elif mutation == 'repeated_json_key':
        raw=b'{"/same":{},"/same":{}}';sha=gate.digest(raw);literals[sha]=raw
        spec['pages'][0]={'sha256':sha,'bytes':len(raw),'files':1}
    if mutation == 'missing':
        with pytest.raises(KeyError): pages.resolve(descriptor,literals.__getitem__)
    else:
        with pytest.raises(ValueError,match=reason): pages.resolve(descriptor,literals.__getitem__)


@pytest.mark.parametrize('mutation,reason', [('metadata','FILE_METADATA'),('path','FILE_BASELINE'),
    ('ledger_overlap','LEDGER_OVERLAP'),('full_hash','FULL_BASELINE'),('unpaused','PRESERVED_BASELINE')])
def test_fully_rebound_pages_do_not_bypass_semantic_contract(original, monkeypatch, mutation,reason):
    descriptor,literals=paged(original,monkeypatch); resolved,_=pages.resolve(descriptor,literals.__getitem__)
    value=resolved['terminal_admissions']; name=next(iter(value['non_ledger_files']))
    if mutation=='metadata':value['non_ledger_files'][name]['uid']=-1
    elif mutation=='path':value['non_ledger_files']['relative']=value['non_ledger_files'].pop(name)
    elif mutation=='ledger_overlap':value['non_ledger_files'][value['ledger']['snapshot']['repository']+'/intruder']=value['non_ledger_files'].pop(name)
    elif mutation=='full_hash':resolved['preserved_state_sha256']='f'*64
    else:value['control_snapshot']['paused']=0
    with pytest.raises(ValueError,match=reason):install.validate_recovery(resolved,original[1])


def test_native_installer_reader_preserves_late_charge_transition_and_restore(late_charge_host, monkeypatch):
    f=late_charge_host; before=deepcopy(f['recovery']);descriptor,literals=pages.paginate(before,f['proposal'])
    raw=gate.encoded(descriptor);f['proposal']['recovery_sha256']=gate.digest(raw)
    for sha,value in {**literals,gate.digest(raw):raw}.items():(f['bundle']/'literals'/sha).write_bytes(value)
    # Native page reader, validator, ledger transition and restore checks run;
    # inherited fixture supplies synthetic host/config/service observations only.
    native_inputs=lambda *a:(f['bundle'],f['proposal'],install.load_recovery(f['bundle'],f['proposal']),f['broker'])
    monkeypatch.setattr(install,'inputs',native_inputs)
    assert native_inputs()[2]==before
    receipt=install.apply(SHA,SOURCE)
    assert receipt['terminal_admission_transition']['original_preserved_state_sha256']==before['preserved_state_sha256']
    assert receipt['models_started']==0 and receipt['timers_enabled'] is False
    assert install.restore(SHA,SOURCE)['status']=='PREVIOUS_DEPLOYMENT_RESTORED_WORKERS_HELD'


@pytest.mark.parametrize('missing_page',[False,True])
def test_native_terminal_loader_and_deployed_gate_require_every_page_original(terminal_bundle,original,monkeypatch,missing_page):
    f=terminal_bundle;descriptor,literals=paged(original,monkeypatch);raw=gate.encoded(descriptor)
    f['proposal']['recovery_sha256']=gate.digest(raw);f['evidence'].raw['recovery.json']=raw
    for sha,value in {**literals,gate.digest(raw):raw}.items():(f['bundle']/'literals'/sha).write_bytes(value)
    for sha,value in literals.items():f['evidence'].raw['recovery-pages/'+sha]=value
    if missing_page:f['evidence'].raw.pop('recovery-pages/'+next(iter(literals)))
    save_terminal(f)
    # Fresh synthetic outcome binds this exact descriptor; prior fixtures are not
    # credited with new bytes. No genuine model review claimed.
    loaded,_=terminal.load(f['bundle'],f['evidence'].proposal_raw,f['evidence'].source_files)
    payload={**f['terminal_payload'],'original_review':{k:loaded['execution'][k]
        for k in ('request_sha256','response_sha256','protocol_sha256')}}
    changes.record(f['change'],'REVIEW',f['terminal_actor'],payload)
    if missing_page:
        with pytest.raises(ValueError,match='RECOVERY_PAGE_NOT_REVIEWED'):verify(f)
    else:assert verify(f)['unattended_activation_authority'] is False


@pytest.mark.parametrize('missing',[False,True])
def test_actual_preparer_carries_authenticated_pages_into_private_manifest(inputs, original, monkeypatch, missing):
    f=inputs
    for name in MANDATORY:
        f['files'].setdefault(name,b'# synthetic source fixture\n')
    for name,raw in f['files'].items():
        path=f['root']/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(raw)
    subprocess.run(['git','add','.'],cwd=f['root'],check=True)
    subprocess.run(['git','-c','user.name=Offline Fixture','-c','user.email=fixture@example.invalid',
        'commit','-qm','Synthetic terminal source'],cwd=f['root'],check=True)
    source=subprocess.check_output(['git','rev-parse','HEAD'],cwd=f['root'],text=True).strip()
    f['source']=source;archived(f['files'],f['archive'])
    f['plan'].update(source=source,source_root='/opt/research-system/releases/'+source+'-research-handover/snapshot',review_profile=terminal.PROFILE)
    f['target_json'].write_bytes(gate.encoded({'source':source,'source_root':f['plan']['source_root']}))
    Path(f['plan']['targets']['/etc/research-system/live-research/broker.json']['file']).write_bytes(gate.encoded({'sources':[source]}))
    app=changes.record(f['change_folder'],'APPLIED',ACTOR,{'modification':'Synthetic terminal candidate',
        'checks':'Offline only','result_binding':{'source':source},
        'supersedes_applied_events':[f['applied']['identity']],'review_status':'PENDING'})
    f['plan']['changes'][0]['applied']=app['identity']
    descriptor,literals=paged(original,monkeypatch)
    recovery=Path(f['plan']['recovery_file']);recovery.write_bytes(gate.encoded(descriptor))
    (recovery.parent/'literals').mkdir()
    for sha,raw in literals.items():(recovery.parent/'literals'/sha).write_bytes(raw)
    if missing:(recovery.parent/'literals'/next(iter(literals))).unlink()
    f['plan_file'].write_bytes(gate.encoded(f['plan']))
    if missing:
        with pytest.raises((FileNotFoundError,ValueError)):prepare(f)
        assert not f['destination'].exists()
    else:
        manifest=prepare(f)
        for sha,raw in literals.items():
            name='literals/'+sha
            assert name in manifest['courier_private_files']
            assert manifest['file_sha256'][name]==sha
            assert (f['destination']/name).read_bytes()==raw
        assert manifest['models_started']==0 and not manifest['review_originals_attached']
