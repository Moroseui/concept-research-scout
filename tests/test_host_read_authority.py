"""Original-chain authority tests; synthetic anchors confer no live permission."""
from copy import deepcopy
import json
from pathlib import Path
import pytest
from test_terminal_review import evidence, encoded, event_record
from test_server_review_install import fixture
from orchestrator import implementation_host_read as host, server_review_install as admin
from orchestrator import deployment_review as gate

@pytest.fixture
def grant(evidence, monkeypatch):
    event = json.loads(evidence.raw[evidence.auth_key])
    payload = event['payload']
    payload.update(authority_scope='implementation-review root-equivalent read/discovery only',
                   source_approved=False, scientific_activation_approved=False,
                   implementation_driver_relocation_approved=False)
    event = event_record({k: v for k, v in event.items() if k != 'identity'})
    raw = {'host-read-'+n: v for n, v in evidence.raw.items()
           if n.startswith('authority/') and not n.startswith('authority/events/')}
    key = 'host-read-authority/events/0001-'+event['identity']+'.json'
    raw[key] = encoded(event)
    request = json.loads(raw['host-read-authority/request.json'])
    for name, value in [('AUTH_REQUEST',request['identity']),('AUTH_EVENT',event['identity']),
                        ('OPERATOR_SHA',payload['operator_original_sha256'])]:
        monkeypatch.setattr(host,name,value)
    return raw, key

def test_real_chain_validator_preserves_originals(grant):
    raw,key=grant; original=deepcopy(raw)
    assert host.authority(raw)['identity']==host.AUTH_EVENT
    assert raw==original

@pytest.mark.parametrize('failure', [
    'missing-request','missing-event','missing-operator','changed-operator','broken-parent',
    'changed-event','other-request','other-event','wrong-original-anchor'])
def test_missing_or_changed_bound_originals_fail(grant, monkeypatch, failure):
    raw,key=grant
    event=json.loads(raw[key])
    op='host-read-authority/'+event['payload']['authority_reference']['artifact']
    if failure=='missing-request': del raw['host-read-authority/request.json']
    elif failure=='missing-event': del raw[key]
    elif failure=='missing-operator': del raw[op]
    elif failure=='changed-operator': raw[op]+=b' changed'
    elif failure=='broken-parent':
        event['previous_sha256']='0'*64; raw[key]=encoded(event)
    elif failure=='changed-event':
        event['payload']['rationale']='changed';raw[key]=encoded(event)
    elif failure=='other-request':monkeypatch.setattr(host,'AUTH_REQUEST','f'*64)
    elif failure=='other-event':monkeypatch.setattr(host,'AUTH_EVENT','f'*64)
    else:monkeypatch.setattr(host,'OPERATOR_SHA','f'*64)
    with pytest.raises((ValueError,KeyError)):host.authority(raw)

@pytest.mark.parametrize('field',[
    'actor','authority_scope','source_approved','installation_approved',
    'scientific_activation_approved','implementation_driver_relocation_approved'])
def test_semantically_broadened_chain_fails_even_after_resealing_fixture(grant,monkeypatch,field):
    raw,key=grant;event=json.loads(raw.pop(key))
    if field=='actor':event['actor']={'kind':'agent','family':'codex','model':'synthetic','session_id':'synthetic'}
    elif field=='authority_scope':event['payload'][field]='arbitrary execution'
    else:event['payload'][field]=True
    event=event_record({k:v for k,v in event.items() if k!='identity'})
    raw['host-read-authority/events/0001-'+event['identity']+'.json']=encoded(event)
    monkeypatch.setattr(host,'AUTH_EVENT',event['identity'])
    with pytest.raises(ValueError):host.authority(raw)

def enable_host(f, monkeypatch, raw):
    config=deepcopy(f['config'])
    config['runtime']={'host_read':{'schema':host.PROFILE,'operator_original_sha256':host.OPERATOR_SHA,
        'authority_request':host.AUTH_REQUEST,'authorized_event':host.AUTH_EVENT}}
    new=gate.encoded(config);proposal=deepcopy(f['proposal'])
    proposal['targets'][str(f['config_path'])]['sha256']=gate.digest(new)
    bundle=f['base']/'bundles'/gate.digest(gate.encoded(proposal))
    f['bundle'].rename(bundle);(bundle/'proposal.json').write_bytes(gate.encoded(proposal))
    (bundle/'literals'/gate.digest(new)).write_bytes(new)
    f.update(bundle=bundle,config=config,proposal=proposal)
    reads=[]
    def inventory(path):
        assert path==bundle/'terminal-review';reads.append(path)
        return b'synthetic protected index',raw
    monkeypatch.setattr(gate,'_inspection_inventory',inventory)
    return reads

def test_install_and_each_installed_verification_authenticate_original_grant(fixture,grant,monkeypatch):
    f=fixture;raw,key=grant;reads=enable_host(f,monkeypatch,raw)
    first=admin.install(f['bundle'])
    assert len(reads)>=2  # pre-mutation plus actual completed verification
    before=f['config_path'].read_bytes()
    assert admin.verify(f['sources']/f['source'],f['source'],f['config'])==first
    raw[key]=b'{}'
    with pytest.raises(ValueError):
        admin.verify(f['sources']/f['source'],f['source'],f['config'])
    assert f['config_path'].read_bytes()==before

def test_missing_grant_stops_before_install_intent_or_mutation(fixture,grant,monkeypatch):
    f=fixture;raw,key=grant;enable_host(f,monkeypatch,{})
    with pytest.raises(KeyError):admin.install(f['bundle'])
    assert not (f['bundle']/'install-intent.json').exists()
    assert not f['config_path'].exists()
    assert not (f['sources']/f['source']).exists()
    assert f['active'].read_bytes()==b'preserved scientific selection'

def test_changed_protected_index_stops_verification(fixture,grant,monkeypatch):
    f=fixture;raw,key=grant;enable_host(f,monkeypatch,raw);admin.install(f['bundle'])
    def fail(path):raise ValueError('DEPLOYMENT_INSPECTION_FILE_CHANGED')
    monkeypatch.setattr(gate,'_inspection_inventory',fail)
    with pytest.raises(ValueError,match='INSPECTION_FILE_CHANGED'):
        admin.verify(f['sources']/f['source'],f['source'],f['config'])

def test_host_disabled_keeps_existing_route(monkeypatch):
    def forbidden(*a,**k):raise AssertionError('not an enabled host-read route')
    monkeypatch.setattr(gate,'_inspection_inventory',forbidden)
    assert admin.host_read_authority(Path('/synthetic'),{}) is None
