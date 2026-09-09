"""Fixed live-socket installation risks; no host, network or credential use."""
import copy
import importlib.util
import json
import os
from pathlib import Path
from types import SimpleNamespace

import pytest

ROOT = Path(__file__).resolve().parents[1]
path = ROOT/'deploy/research-system/install_live_handover.py'
spec = importlib.util.spec_from_file_location('live_install',path)
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)


def originals():
    state = {'version':1,'sequence':1,'count':1,'day':'2026-09-09','halted':False,
        'policy_sha256':m.POLICY_SHA,'resets':[],'notifications':{},
        'events':{'server:'+m.EVENT+':1':{'source':m.SOURCE,'kind':'astra_turn',
            'branch':'astra/infrastructure-milestone-record','day':'2026-09-09',
            'count':1,'notification':None,'halted':False}}}
    summary = {'status':'MODEL_DISABLED_DIRECT_BROKER_LIVE_CANARY_COMPLETE_PERSISTENT_INSTALLATION_PENDING',
        'source':m.SOURCE,'initial_state_pin':m.INITIAL_PIN,'final_state_pin':m.LEDGER_PIN,
        'policy_sha256':m.POLICY_SHA,'fixed_event':{'turn_id':m.EVENT,'attempt':'1',
            'source':m.SOURCE,'branch':'astra/infrastructure-milestone-record','kind':'astra_turn'},
        'live_count_added':1,'final_live_count':1,'duplicate_added_count':0,'models_called':0,
        'fixture_state_untouched':True,**{name:False for name in ('services_changed',
            'active_configurations_changed','source_links_changed','reset_executed',
            'code_publication_executed','unattended_activated')}}
    values = {name:{} for name in m.CANARY_FILES}
    values['execution-receipt.json'] = summary
    values['final-state.json'] = {'pin':m.LEDGER_PIN,'state':state}
    for name in ('initialize','admit','duplicate','status'):
        returned = {'synthetic_operation':name}
        wrapped = {'result':returned,'source':m.SOURCE,'operation':name,
            'policy_sha256':m.POLICY_SHA,'event':summary['fixed_event'],
            'expected_ledger_pin':{'initialize':None,'admit':m.INITIAL_PIN,
                'duplicate':m.LEDGER_PIN,'status':m.LEDGER_PIN}[name]}
        values[name+'.result.json'] = wrapped
        values[name+'.receipt.json'] = {'result':returned,
            'ledger_pin_after':m.INITIAL_PIN if name=='initialize' else m.LEDGER_PIN,
            'returned_result_sha256':m.digest(m.encoded(wrapped))}
    return {name:m.encoded(value) for name,value in values.items()}


def manifest(inputs, prior):
    return {'reviewed_source':'a'*40,'source_review_sha256':'b'*64,
            'input_sha256':{k:m.digest(v) for k,v in inputs.items()},
            'canary_sha256':{k:m.digest(v) for k,v in prior.items()}}


def test_manifest_binds_every_original_and_exact_three_staged_files():
    inputs={name:name.encode() for name in m.INPUTS}; prior=originals()
    assert len(prior) == 17
    value=manifest(inputs,prior)
    m.manifest_check(value,inputs,prior)
    for name in inputs:
        changed={**inputs,name:inputs[name]+b'changed'}
        with pytest.raises(ValueError,match='BYTES_CHANGED'):
            m.manifest_check(value,changed,prior)
    for name in prior:
        with pytest.raises(ValueError,match='BYTES_CHANGED'):
            m.manifest_check(value,inputs,{**prior,name:prior[name]+b' '})
    with pytest.raises(ValueError):
        m.manifest_check({**value,'canary_sha256':{}},inputs,prior)


@pytest.mark.parametrize('field,value', [('final_state_pin','c'*40),('policy_sha256','d'*64),
    ('source','e'*40),('reset_executed',True),('unattended_activated',True),('models_called',1)])
def test_incompatible_canary_cannot_be_promoted(field,value):
    prior=originals(); receipt=json.loads(prior['execution-receipt.json'])
    receipt[field]=value;prior['execution-receipt.json']=m.encoded(receipt)
    with pytest.raises(ValueError,match='CANARY'):
        m.canary_check(prior)


def test_original_return_hash_and_retained_event_are_required():
    prior=originals();m.canary_check(prior)
    prior['status.result.json']=m.encoded({'changed':True})
    with pytest.raises(ValueError,match='RETURN_CHANGED'):
        m.canary_check(prior)
    prior=originals();final=json.loads(prior['final-state.json'])
    final['state']['events']={};prior['final-state.json']=m.encoded(final)
    with pytest.raises(ValueError,match='RETAINED_CANARY'):
        m.canary_check(prior)


@pytest.fixture
def installation(tmp_path,monkeypatch):
    staging=tmp_path/'staging';staging.mkdir()
    unit_root=tmp_path/'units';unit_root.mkdir()
    canary=tmp_path/'canary';canary.mkdir()
    socket=tmp_path/'live.sock'
    for name,value in [('STAGING',staging),('UNIT_ROOT',unit_root),('CANARY',canary),('SOCKET',socket)]:
        monkeypatch.setattr(m,name,value)
    monkeypatch.setattr(m,'__file__',str(staging/'install_live_handover.py'))
    monkeypatch.setattr(m.os,'getuid',lambda:0)
    monkeypatch.setattr(m.sys,'dont_write_bytecode',True)
    monkeypatch.setattr(m.pwd,'getpwnam',lambda name:SimpleNamespace(pw_uid=997))
    monkeypatch.setattr(m.grp,'getgrnam',lambda name:SimpleNamespace(gr_gid=998))
    # Synthetic private root only; production metadata checks remain separate.
    def protected(path,**kwargs):
        path=Path(path)
        if path.is_symlink():raise ValueError('ROOT_PROTECTED_PATH_REQUIRED')
        return m.seal(path.stat())
    monkeypatch.setattr(m,'protected',protected)
    inputs={name:(ROOT/'deploy/research-system'/name).read_bytes() for name in m.INPUTS}
    prior=originals()
    for name,raw in inputs.items():(staging/name).write_bytes(raw)
    for name,raw in prior.items():(canary/name).write_bytes(raw)
    (staging/'review-manifest.json').write_bytes(m.encoded(manifest(inputs,prior)))
    fixed={'preserved':'fixture original bytes and links'}
    observations={'config':0,'ledger':0,'reload':False,'calls':[]}
    monkeypatch.setattr(m,'source_check',lambda:object())
    def configuration(helper):
        observations['config']+=1
        return copy.deepcopy(fixed)
    monkeypatch.setattr(m,'configuration_check',configuration)
    def ledger(final):
        observations['ledger']+=1
        assert final['pin']==m.LEDGER_PIN
    monkeypatch.setattr(m,'ledger_check',ledger)
    def command(args,**kwargs):
        observations['calls'].append(args)
        if args[0]=='systemd-analyze':return b''
        if args==['systemctl','daemon-reload']:
            observations['reload']=True;return b''
        if args[:2]==['systemctl','show']:
            loaded=observations['reload']
            return ('LoadState='+('loaded' if loaded else 'not-found')+'\nActiveState=inactive\nUnitFileState='+('disabled' if loaded else '')+'\n').encode()
        raise AssertionError('Forbidden command: '+str(args))
    monkeypatch.setattr(m,'command',command)
    return SimpleNamespace(staging=staging,units=unit_root,canary=canary,observations=observations,
                           fixed=fixed,inputs=inputs,command=command)


def test_install_only_distinct_units_stopped_without_canary_replay(installation):
    env=installation; prior={p.name:p.read_bytes() for p in env.canary.iterdir()}
    value=m.install()
    assert value['status']=='LIVE_BROKER_SOCKET_INSTALLED_STOPPED_DISABLED'
    assert value['model_mode']=='DISABLED' and value['max_model_turns']==0
    assert value['tokens_minted']==value['remote_refs_written']==value['models_called']==0
    assert value['services_started'] is value['socket_enabled'] is False
    assert {p.name:p.read_bytes() for p in env.canary.iterdir()}==prior
    assert {p.name for p in env.units.iterdir()}==set(m.UNITS)
    assert all((env.units/name).read_bytes()==env.inputs[name] for name in m.UNITS)
    assert all((env.units/name).stat().st_mode&0o777==0o644 for name in m.UNITS)
    assert env.observations['ledger']==2
    assert (env.staging/'install-receipt.json').exists()
    # No start, enable, reset, initialize, admission or existing-fixture command.
    assert all(args[0]=='systemd-analyze' or args[:2] in
        [['systemctl','show'],['systemctl','daemon-reload']] for args in env.observations['calls'])
    with pytest.raises(ValueError,match='PARTIAL_INSTALL'):
        m.install()


@pytest.mark.parametrize('retained',['unit','intent','socket','dropin'])
def test_existing_or_partial_install_is_preserved_before_mutation(installation,retained):
    env=installation
    path={'unit':env.units/m.UNITS[0],'intent':env.staging/'install-intent.json',
          'socket':m.SOCKET,'dropin':env.units/(m.UNITS[0]+'.d')}[retained]
    path.write_bytes(b'preserve original')
    with pytest.raises(ValueError,match='RECONCILE'):
        m.install()
    assert path.read_bytes()==b'preserve original'
    assert env.observations['reload'] is False
    assert not (env.staging/'install-receipt.json').exists()


def test_failed_reload_preserves_written_units_and_intent(installation,monkeypatch):
    env=installation
    def command(args,**kwargs):
        if args==['systemctl','daemon-reload']:raise ValueError('RELOAD_UNCERTAIN')
        return env.command(args,**kwargs)
    monkeypatch.setattr(m,'command',command)
    with pytest.raises(ValueError,match='RELOAD_UNCERTAIN'):
        m.install()
    assert set(p.name for p in env.units.iterdir())==set(m.UNITS)
    assert (env.staging/'install-intent.json').exists()
    assert json.loads((env.staging/'install-failure.json').read_text())['automatic_retry'] is False
    assert not (env.staging/'install-receipt.json').exists()


def test_config_change_after_intent_stops_before_install(installation,monkeypatch):
    calls=[]
    def changed(helper):
        calls.append(1);return {'version':len(calls)}
    monkeypatch.setattr(m,'configuration_check',changed)
    with pytest.raises(ValueError,match='CONFIGURATION_CHANGED_BEFORE_INSTALL'):
        m.install()
    assert not list(installation.units.iterdir())
    assert (installation.staging/'install-failure.json').exists()


def test_wrong_live_ledger_ref_refuses_without_fetch_or_mutation(monkeypatch):
    calls=[]
    def command(args,**kwargs):
        calls.append(args)
        if args[-3:]==['remote','get-url','origin']:return (m.REMOTE+'\n').encode()
        return ('f'*40+'\t'+m.REF+'\n').encode()
    monkeypatch.setattr(m,'command',command)
    with pytest.raises(ValueError,match='LIVE_LEDGER_MOVED'):
        m.ledger_check(m.canary_check(originals()))
    assert not any('fetch' in args or 'push' in args or 'init' in args for args in calls)


def test_synthetic_unit_schema_keeps_root_private_source_and_fixture_separate():
    service=(ROOT/'deploy/research-system'/m.UNITS[0]).read_text()
    socket=(ROOT/'deploy/research-system'/m.UNITS[1]).read_text()
    assert 'User=root\n' in service and 'Group=research-runtime\n' in service
    assert 'WorkingDirectory='+str(m.SOURCE_ROOT) in service
    assert '--config '+str(m.PREPARATION/'broker.proposed.json') in service
    assert '--socket '+str(m.SOCKET) in service
    assert 'ReadWritePaths='+str(m.LIVE_ROOT)+'\n' in service
    assert 'ProtectHome=true' in service and 'NoNewPrivileges=true' in service
    assert 'handover-controller' not in service and '/home/research-' not in service
    assert 'ListenStream='+str(m.SOCKET) in socket and 'SocketMode=0660' in socket
    assert 'Service='+m.UNITS[0] in socket


def test_command_excludes_inherited_credentials_and_is_bounded(monkeypatch):
    monkeypatch.setenv('GH_TOKEN','SYNTHETIC_NEVER_PROPAGATE')
    observed={}
    def run(args,**kwargs):
        observed.update(kwargs);return SimpleNamespace(returncode=0,stdout=b'public metadata',stderr=b'')
    monkeypatch.setattr(m.subprocess,'run',run)
    assert m.command(['git','ls-remote'])==b'public metadata'
    assert 'GH_TOKEN' not in observed['env'] and observed['timeout']==60
    assert observed['env']['GIT_CONFIG_GLOBAL']=='/dev/null'
