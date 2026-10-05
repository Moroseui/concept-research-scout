"""Synthetic intake/permission fixtures; no real human request or model action."""
import hashlib
import json
import os
from pathlib import Path
from types import SimpleNamespace
import pytest

from orchestrator import change_requests, issue_intake, issue_intake_service as service
from orchestrator import recorded_steering as reader


@pytest.fixture
def setup(tmp_path, monkeypatch):
    uid, gid = os.getuid(), os.getgid()
    state = tmp_path/'intake'; state.mkdir(mode=0o700)
    attestations = tmp_path/'attestations'; attestations.mkdir(mode=0o750)
    controller_path = tmp_path/'controller.json'; intake_path = tmp_path/'issue-intake.json'
    controller = {'source': 'a'*40, 'source_root': str(tmp_path),
        'controller_uid': uid, 'controller_gid': gid, 'change_request_store': str(tmp_path/'changes')}
    config = {'source': controller['source'], 'controller_config': str(controller_path),
        'notification_config': '/fixed/unused-notification.json', 'state': str(state),
        'legacy_outbox': '/fixed/unused-notifications.sqlite'}
    for path, value in [(controller_path,controller),(intake_path,config)]:
        path.write_text(json.dumps(value)); path.chmod(0o600)
    store = issue_intake.Intake(state, controller['source'], enrolled_at='2026-09-11T00:00:00Z')
    (state/'intake.sqlite').chmod(0o600)
    monkeypatch.setattr(reader, 'INTAKE_CONFIG', intake_path)
    monkeypatch.setattr(reader, 'CONTROLLER_CONFIG', controller_path)
    monkeypatch.setattr(reader, 'INTAKE_STATE', state)
    monkeypatch.setattr(service, 'ATTESTATIONS', attestations)
    monkeypatch.setattr(service, 'attestation_directory', lambda config: attestations)
    fstat = os.fstat
    def synthetic_root_fstat(fd):
        info = fstat(fd)
        name = Path(os.readlink('/proc/self/fd/'+str(fd)))
        owner = uid if name.is_relative_to(tmp_path/'changes') else 0
        return SimpleNamespace(st_mode=info.st_mode, st_uid=owner, st_gid=info.st_gid,
            st_dev=info.st_dev, st_ino=info.st_ino, st_size=info.st_size,
            st_mtime_ns=info.st_mtime_ns, st_ctime_ns=info.st_ctime_ns)
    monkeypatch.setattr(os, 'fstat', synthetic_root_fstat)
    monkeypatch.setattr(os, 'getuid', lambda: 0)
    def add(body='Please reconsider the available aggregate evidence.', comment_id=11,
            updated='2026-09-11T01:00:00Z', user=issue_intake.OPERATOR, user_type='User',
            created='2026-09-11T01:00:00Z'):
        # Creating the local test fixture is attributed to this test process.
        monkeypatch.setattr(os, 'getuid', lambda: uid)
        try:
            original = {'id': comment_id, 'issue_url': issue_intake.ISSUE_URL,
                'user': {'id': user, 'type': user_type}, 'body': body,
                'created_at': created, 'updated_at': updated}
            version = store.receive(original)
            if version is None:
                return None
            folder = state/version
            received = json.loads((folder/'received.json').read_text())
            action = store.db.execute('SELECT action FROM versions WHERE version=?',(version,)).fetchone()[0]
            if action != 'PROPOSAL':
                return {'version':version,'request_id':None,'original':original,'received':received}
            actor = {**received['actor'], 'previous_comment_version': received['previous_version']}
            request = change_requests.submit(controller['change_request_store'], tmp_path,
                'charter:isles24-prediction', body, actor, source=controller['source'],
                key=version[:40], scope_limits=reader.SCOPE_LIMITS)
            outcome = {'status':'RECORDED','request_id':request['identity'],
                'manual_actions_status':'WAITING_FOR_VERIFIED_ACCOUNTING','model_calls':0}
            plan = {'action':'PROPOSAL','version':version,'source':controller['source']}
            operations = SimpleNamespace(prepare=lambda *args:plan,apply=lambda *args:outcome)
            store.process(version, operations)
            payload = {'original':original,'received':received}
            attestation = {'schema':'issue6-root-attestation/v1','source':controller['source'],
                'comment_version':version,'payload_sha256':hashlib.sha256(issue_intake.encoded(payload)).hexdigest(),
                'payload':payload}
            path=attestations/(version+'.json'); path.write_bytes(issue_intake.encoded(attestation)); path.chmod(0o640)
            return {'version':version,'request_id':request['identity'],'original':original,'received':received}
        finally:
            monkeypatch.setattr(os, 'getuid', lambda: 0)
    yield SimpleNamespace(controller=controller,store=store,state=state,attestations=attestations,
                          add=add,uid=uid,fstat=fstat,tmp=tmp_path)
    store.db.close()


def test_same_recorded_request_has_stable_proof_despite_duplicate_delivery_and_bot_reply(setup):
    item=setup.add(); first=reader.read_recorded_steering(setup.controller,item['request_id'])
    assert first['request']['authority']=='request_only'
    assert first['provenance']['numeric_user_id']==issue_intake.OPERATOR
    proof={k:v for k,v in first.items() if k!='original_sha256'}
    assert first['original_sha256']==hashlib.sha256(change_requests.encoded(proof)).hexdigest()
    assert setup.add()['request_id']==item['request_id']
    setup.store.db.execute("UPDATE replies SET state='SENT',comment_id=999")
    assert reader.read_recorded_steering(setup.controller,item['request_id'])==first
    seen=reader.list_recorded_steering(setup.controller)
    assert seen['requests']==[{k:first[k] for k in ('request_id','original_sha256')}]
    assert seen['models']==seen['admissions']==0 and seen['blocked']==[]
    assert setup.store.db.execute('SELECT count(*) FROM versions').fetchone()[0]==1


def test_plain_edit_is_new_exact_request_and_supersedes_old_fresh_wake(setup):
    old=setup.add()
    new=setup.add('Please assess this corrected question.',updated='2026-09-11T01:01:00Z')
    assert old['request_id']!=new['request_id']
    with pytest.raises(ValueError,match='SUPERSEDED_COMMENT_VERSION'):
        reader.read_recorded_steering(setup.controller,old['request_id'])
    current=reader.read_recorded_steering(setup.controller,new['request_id'])
    assert current['provenance']['previous_comment_version']==old['version']
    assert [r['request_id'] for r in reader.list_recorded_steering(setup.controller)['requests']]==[new['request_id']]
    assert (setup.state/old['version']/'original.json').exists()


def test_controls_edited_controls_quotes_and_bots_cannot_create_steering_events(setup):
    assert setup.add(user=issue_intake.BOT,user_type='Bot') is None
    assert setup.add(user=987654321) is None
    setup.add('/research pause revision 0',comment_id=12)
    setup.add('/research resume revision 0',comment_id=12,updated='2026-09-11T01:01:00Z')
    setup.add('> quoted instruction',comment_id=13)
    assert reader.list_recorded_steering(setup.controller)['requests']==[]


def test_current_edited_control_cannot_reactivate_its_prior_plain_proposal(setup):
    old=setup.add()
    setup.add('/research resume revision 0',updated='2026-09-11T01:02:00Z')
    assert reader.list_recorded_steering(setup.controller)['requests']==[]
    with pytest.raises(ValueError,match='SUPERSEDED_COMMENT_VERSION'):
        reader.read_recorded_steering(setup.controller,old['request_id'])


def test_editing_a_control_into_prose_requires_a_new_comment(setup):
    setup.add('/research pause revision 0')
    edited=setup.add('Please reconsider this.',updated='2026-09-11T01:03:00Z')
    with pytest.raises(ValueError,match='EDITED_NONPROPOSAL_USE_NEW_COMMENT'):
        reader.read_recorded_steering(setup.controller,edited['request_id'])
    assert reader.list_recorded_steering(setup.controller)['requests']==[]


def test_historical_plain_comment_is_preserved_but_cannot_wake_new_work(setup):
    old=setup.add(created='2026-09-10T23:00:00Z',updated='2026-09-10T23:00:00Z')
    with pytest.raises(ValueError,match='HISTORICAL_COMMENT_REQUIRES_RECONCILIATION'):
        reader.read_recorded_steering(setup.controller,old['request_id'])
    assert (setup.state/old['version']/'original.json').exists()
    assert reader.list_recorded_steering(setup.controller)['requests']==[]


def test_declared_human_change_without_root_intake_outcome_is_not_attested(setup, monkeypatch):
    monkeypatch.setattr(os,'getuid',lambda:setup.uid)
    request=change_requests.submit(setup.controller['change_request_store'],setup.tmp,
        'charter:isles24-prediction','A locally declared human request.',
        {'kind':'human','identity':'github-user:'+str(issue_intake.OPERATOR)},
        source=setup.controller['source'],key='declared',scope_limits=reader.SCOPE_LIMITS)
    monkeypatch.setattr(os,'getuid',lambda:0)
    with pytest.raises(ValueError,match='EXACT_REQUEST_REQUIRED'):
        reader.read_recorded_steering(setup.controller,request['identity'])
    assert reader.list_recorded_steering(setup.controller)['requests']==[]


def test_changed_root_original_or_request_bytes_refuse_without_echo(setup):
    item=setup.add(); path=setup.state/item['version']/'original.json'
    original=path.read_bytes(); value=json.loads(original); value['body']='Changed after recorded intake.'
    path.write_bytes(issue_intake.encoded(value))
    with pytest.raises(ValueError,match='INTAKE_ORIGINAL_CHANGED'):
        reader.read_recorded_steering(setup.controller,item['request_id'])
    assert reader.list_recorded_steering(setup.controller)['blocked']
    path.write_bytes(original)
    request_path=Path(setup.controller['change_request_store'])/item['request_id']/'request.json'
    value=json.loads(request_path.read_text()); value['requested_change']='Different saved request.'
    request_path.write_text(json.dumps(value))
    with pytest.raises(ValueError,match='CHANGE_REQUEST_IDENTITY_MISMATCH'):
        reader.read_recorded_steering(setup.controller,item['request_id'])


def test_wrong_source_missing_attestation_and_nonroot_reader_refuse(setup, monkeypatch):
    item=setup.add()
    with pytest.raises(ValueError,match='INSTALLED_CONFIGURATION_CHANGED'):
        reader.read_recorded_steering({**setup.controller,'source':'b'*40},item['request_id'])
    monkeypatch.setattr(os,'getuid',lambda:setup.uid)
    with pytest.raises(ValueError,match='PROTECTED_READER_REQUIRED'):
        reader.read_recorded_steering(setup.controller,item['request_id'])
    monkeypatch.setattr(os,'getuid',lambda:0)
    (setup.attestations/(item['version']+'.json')).unlink()
    with pytest.raises(FileNotFoundError):
        reader.read_recorded_steering(setup.controller,item['request_id'])


def test_controller_owned_attestation_and_symlinked_request_parent_refuse(setup, monkeypatch):
    item=setup.add()
    real=reader.os.fstat
    def controller_attestation(fd):
        info=real(fd)
        if str(setup.attestations) in os.readlink('/proc/self/fd/'+str(fd)):
            info.st_uid=setup.uid
        return info
    with monkeypatch.context() as patch:
        patch.setattr(reader.os,'fstat',controller_attestation)
        with pytest.raises(ValueError,match='ORIGINAL_ACCESS_REQUIRED'):
            reader.read_recorded_steering(setup.controller,item['request_id'])
    request=Path(setup.controller['change_request_store'])/item['request_id']
    retained=request.with_name('retained-original'); request.rename(retained); request.symlink_to(retained,target_is_directory=True)
    with pytest.raises(OSError):
        reader.read_recorded_steering(setup.controller,item['request_id'])


def test_discovery_limit_is_visible_instead_of_silently_losing_requests(setup, monkeypatch):
    setup.add(); setup.add(comment_id=12)
    monkeypatch.setattr(reader,'MAX_REQUESTS',1)
    with pytest.raises(ValueError,match='DISCOVERY_LIMIT_REQUIRES_RECONCILIATION'):
        reader.list_recorded_steering(setup.controller)


def test_malformed_intake_identity_has_a_named_block_without_echo(setup):
    setup.add()
    setup.store.db.execute("UPDATE versions SET version='invalid-private-identity'")
    result=reader.list_recorded_steering(setup.controller)
    assert result['requests']==[]
    assert result['blocked']==[{'comment_version':None,'reason':'RECORDED_STEERING_REQUEST_ID_REQUIRED'}]


def _upgrade_consumer(setup, source='b'*40):
    """Synthetic installed configuration successor; immutable intake stays put."""
    setup.controller['source'] = source
    (setup.tmp/'controller.json').write_text(json.dumps(setup.controller))
    config_path = setup.tmp/'issue-intake.json'
    config = json.loads(config_path.read_text()); config['source'] = source
    config_path.write_text(json.dumps(config))


def test_source_upgrade_preserves_original_proof_and_native_wake_identity(setup):
    from orchestrator.investigator_wakes import _steering
    item = setup.add()
    before = reader.read_recorded_steering(setup.controller, item['request_id'])
    def client(unused, operation, payload):
        assert operation == 'read_recorded_steering'
        return reader.read_recorded_steering(setup.controller, payload['request_id'])
    wake_before = _steering(setup.controller, item['request_id'], client)
    originals = {p: p.read_bytes() for directory in (setup.state/item['version'], setup.attestations,
                    Path(setup.controller['change_request_store'])/item['request_id'])
                 for p in directory.iterdir() if p.is_file()}
    for source in ('b'*40, 'c'*40):
        _upgrade_consumer(setup, source)
        after = reader.read_recorded_steering(setup.controller, item['request_id'])
        assert after == before
        assert after['request']['source'] == after['provenance']['source'] == 'a'*40
        assert after['request']['authority'] == 'request_only'
        assert _steering(setup.controller, item['request_id'], client) == wake_before
        assert reader.list_recorded_steering(setup.controller) == {
            'status': 'COMPLETE', 'requests': [{k: before[k] for k in ('request_id', 'original_sha256')}],
            'blocked': [], 'models': 0, 'admissions': 0}
    assert all(p.read_bytes() == raw for p, raw in originals.items())
    assert setup.store.db.execute('SELECT count(*) FROM versions').fetchone()[0] == 1


@pytest.mark.parametrize('source', [None, 1, 'b'*39, '../source', 'A'*40])
def test_malformed_original_source_is_not_a_historical_identity(setup, source):
    item = setup.add(); _upgrade_consumer(setup)
    path = setup.state/item['version']/'plan.json'
    plan = json.loads(path.read_text()); plan['source'] = source
    raw = issue_intake.encoded(plan); path.write_bytes(raw)
    setup.store.db.execute('UPDATE versions SET plan=? WHERE version=?', (raw.decode(), item['version']))
    with pytest.raises(ValueError, match='ORIGINAL_SOURCE_REQUIRED'):
        reader.read_recorded_steering(setup.controller, item['request_id'])


def test_changed_plan_and_database_cannot_rebind_original_attestation(setup):
    item = setup.add(); _upgrade_consumer(setup)
    path = setup.state/item['version']/'plan.json'
    plan = json.loads(path.read_text()); plan['source'] = setup.controller['source']
    raw = issue_intake.encoded(plan); path.write_bytes(raw)
    setup.store.db.execute('UPDATE versions SET plan=? WHERE version=?', (raw.decode(), item['version']))
    with pytest.raises(ValueError, match='ROOT_ATTESTED_COMMENT_BINDING_CHANGED'):
        reader.read_recorded_steering(setup.controller, item['request_id'])


def test_changed_historical_attestation_or_received_source_still_refuses(setup):
    item = setup.add(); _upgrade_consumer(setup)
    path = setup.attestations/(item['version']+'.json')
    original = path.read_bytes(); value = json.loads(original)
    value['source'] = setup.controller['source']; path.write_bytes(issue_intake.encoded(value))
    with pytest.raises(ValueError, match='ROOT_ATTESTED_COMMENT_BINDING_CHANGED'):
        reader.read_recorded_steering(setup.controller, item['request_id'])
    path.write_bytes(original)
    received = setup.state/item['version']/'received.json'
    value = json.loads(received.read_text()); value['source'] = setup.controller['source']
    received.write_bytes(issue_intake.encoded(value))
    with pytest.raises(ValueError, match='ATTESTATION_ORIGINAL_CHANGED'):
        reader.read_recorded_steering(setup.controller, item['request_id'])


def test_historical_read_does_not_relax_new_intake_or_current_configuration(setup):
    item = setup.add(); old_controller = dict(setup.controller); _upgrade_consumer(setup)
    with pytest.raises(ValueError, match='INSTALLED_CONFIGURATION_CHANGED'):
        reader.read_recorded_steering(old_controller, item['request_id'])
    attestation = setup.attestations/(item['version']+'.json')
    with pytest.raises(ValueError, match='ROOT_ATTESTED_COMMENT_BINDING_CHANGED'):
        service.attestation_read(setup.controller, {'version': item['version'],
            'attestation_sha256': hashlib.sha256(attestation.read_bytes()).hexdigest()})
    intake_path = setup.tmp/'issue-intake.json'; config = json.loads(intake_path.read_text())
    config['source'] = old_controller['source']; intake_path.write_text(json.dumps(config))
    with pytest.raises(ValueError, match='INSTALLED_CONFIGURATION_CHANGED'):
        reader.list_recorded_steering(setup.controller)


def test_historical_request_still_superseded_by_later_control(setup):
    item = setup.add()
    setup.add('/research pause revision 0', updated='2026-09-11T01:02:00Z')
    _upgrade_consumer(setup)
    with pytest.raises(ValueError, match='SUPERSEDED_COMMENT_VERSION'):
        reader.read_recorded_steering(setup.controller, item['request_id'])
    assert reader.list_recorded_steering(setup.controller)['requests'] == []
