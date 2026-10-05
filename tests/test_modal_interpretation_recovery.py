"""Exact recovery contract with synthetic calls only; no live/provider effects."""
import json
from pathlib import Path
import pytest
from orchestrator import private_records
from orchestrator.manual_executor import atomic, digest, read
from tools import modal_interpretation_recovery as recovery
from tools import install_m3_evidence as installer
from test_interpretation_evidence import collected, modal_lane, lane, root, policy, private_copied_fixture
from test_modal_driver import fake_model


def invalid_author(work, stage, clients, pin):
    native = fake_model(work, stage, clients, pin)
    atomic(work / 'investigator_next_decision.json', {
        'status': 'PROPOSAL_ONLY', 'proposed_action_type': 'blocker_resolution',
        'action': 'Resolve a closed synthetic finding', 'rationale': 'Synthetic only',
        'charter_basis': '', 'blocker_ids': ['CLOSED-SYNTHETIC']})
    return native


@pytest.fixture
def blocked(collected, monkeypatch):
    d, p = collected
    d.runner = invalid_author
    assert d.advance()['reason'] == 'OUTPUT_VALIDATION_REFUSED: OPEN_BLOCKER_BINDING_REQUIRED'
    call = d.current()['pending']['id']
    # Two earlier spec calls from the real run are represented by explicitly
    # synthetic completed reservations, not unaccounted inserted ledger rows.
    for stage in ('run_spec_author', 'run_spec_review'):
        ident, _, receipt = d.store.reserve_call(d.config['run_id'], stage,
            d.config['source'], d.config['branch'], d.config['policy'], {'synthetic': True})
        d.store.finish_call(ident, receipt, 'COMPLETE')
    config = read(d.state / 'lane.json')
    config['scientific_files'] = {}
    config['owner_path'] = str(d.state / 'owner.json')
    config['owner_binding'] = {'synthetic': True}
    atomic(config['owner_path'], config['owner_binding'])
    atomic(d.state / 'lane.json', config)
    work = Path(d.current()['pending']['workspace'])
    pins = {'config': digest((d.state / 'lane.json').read_bytes()),
        'state': digest(recovery.canonical(d.current())),
        'tables': digest(recovery.canonical(recovery.table_rows(d.store.db)))}
    pins.update({name: digest((work / name).read_bytes()) for name in
                 ('interpretation.md', 'investigator_next_decision.json')})
    authority = d.state / 'operator.txt'
    private_records.write_text(authority, 'Synthetic one-revision authority; not a real grant.')
    monkeypatch.setattr(recovery, 'ROOT', d.state.parent)
    monkeypatch.setattr(recovery, 'CALL', call)
    monkeypatch.setattr(recovery, 'PINS', pins)
    monkeypatch.setattr(recovery, 'AUTHORITY', digest(authority.read_bytes()))
    monkeypatch.setattr(recovery, 'approval', lambda f: {'source_sha': 'e' * 40,
                                                     'report_sha256': 'f' * 64})
    check_output = recovery.subprocess.check_output
    def observed(args, **kwargs):
        if args[0] == '/usr/bin/systemctl': return 'inactive\n'
        return check_output(args, **kwargs)
    monkeypatch.setattr(recovery.subprocess, 'check_output', observed)
    return d, p, authority


def test_linked_recovery_preserves_five_calls_and_cannot_apply_twice(blocked):
    d, p, authority = blocked
    tables = recovery.table_rows(d.store.db)
    provider_calls = list(p.calls)
    originals = {n: (Path(d.current()['pending']['workspace']) / n).read_bytes()
                 for n in ('interpretation.md', 'investigator_next_decision.json')}
    result = recovery.apply(d.state, 'synthetic', authority)
    assert result['calls_preserved'] == 5 and result['new_allowance'] == result['new_compute'] == 0
    assert d.current()['linked_recovery_of'] == recovery.CALL
    assert d.current()['phase'] == recovery.STAGE and d.current()['rounds'][recovery.STAGE] == 1
    assert recovery.table_rows(d.store.db) == tables and p.calls == provider_calls
    assert d.status()['calls_used'] == 5 and d.status()['call_limit'] == 8
    for n, raw in originals.items():
        assert (d.state.parent / 'lane-scientific-workspaces' / (recovery.STAGE + '-1') / n).read_bytes() == raw
    with pytest.raises(ValueError, match='REVISION_ALREADY_PREPARED_NO_RETRY'):
        recovery.apply(d.state, 'synthetic', authority)
    assert recovery.table_rows(d.store.db) == tables
    d.runner = fake_model
    assert d.advance()['phase'] == 'result_interpretation_review'
    receipt = json.loads(d.store.db.execute('SELECT receipt FROM manual_calls WHERE stage=? AND attempt=2',
                         (recovery.STAGE,)).fetchone()[0])
    assert receipt['linked_recovery_of'] == recovery.CALL
    assert d.advance()['phase'] == 'UPDATE_STATE'
    assert d.status()['calls_used'] == 7 and p.calls == provider_calls


def test_second_invalid_author_stays_blocked_without_third_call(blocked):
    d, p, authority = blocked
    recovery.apply(d.state, 'synthetic', authority)
    effects = list(p.calls)
    assert d.advance()['reason'] == 'OUTPUT_VALIDATION_REFUSED: OPEN_BLOCKER_BINDING_REQUIRED'
    assert d.status()['calls_used'] == 6
    for _ in range(3):
        assert d.advance()['phase'] == 'BLOCKED' and d.status()['calls_used'] == 6
    assert p.calls == effects


@pytest.mark.parametrize('damage,code', [
    ('authority', 'EXACT_REVISION_OPERATOR_AUTHORITY_REQUIRED'),
    ('config', 'REVISION_CONFIG_CHANGED'), ('state', 'REVISION_STATE_OR_ACCOUNTING_CHANGED'),
    ('call', 'REVISION_STATE_OR_ACCOUNTING_CHANGED'), ('original', 'ORIGINAL_AUTHOR_OUTPUT_CHANGED'),
    ('halt', 'HALT_REMAINS_EFFECTIVE'), ('owner', 'OWNER_CHANGED')])
def test_recovery_refuses_changed_evidence_without_releasing_state(blocked, damage, code):
    d, p, authority = blocked
    if damage == 'authority': private_records.write_text(authority, 'Changed authority')
    if damage == 'config': private_records.write_text(d.state / 'lane.json', (d.state / 'lane.json').read_text() + ' ')
    if damage == 'state':
        v = d.current(); v['interventions'].append({'changed': True}); d.save(v)
    if damage == 'call': d.store.db.execute("UPDATE manual_calls SET status='UNCERTAIN' WHERE id=?", (recovery.CALL,))
    if damage == 'original': private_records.write_text(Path(d.current()['pending']['workspace']) / 'interpretation.md', 'Changed original')
    if damage == 'halt': private_records.write_text(d.state / 'HALT', 'Operator stop')
    if damage == 'owner': atomic(d.config.get('owner_path', str(d.state / 'owner.json')), {'changed': True})
    before = recovery.table_rows(d.store.db); effects = list(p.calls)
    with pytest.raises(ValueError) as error: recovery.apply(d.state, 'synthetic', authority)
    assert str(error.value) == code
    assert d.current()['phase'] == 'BLOCKED' and recovery.table_rows(d.store.db) == before
    assert p.calls == effects and not (d.state / 'interpretation-evidence-recovery-20261003').exists()


def test_installer_uses_validated_argv_and_never_changes_root_preflight():
    args = installer.command(Path('/var/immutable/source'), Path('/var/immutable/review'))
    unit = installer.unit_bytes(args).decode()
    assert unit.splitlines() == ['[Service]', 'ExecStart=', 'ExecStart=' + ' '.join(args)]
    assert 'ExecStartPre' not in unit and 'Environment=' not in unit
    for bad in ['/var/space path', '/var/a\nExecStart=/bad', '/var/%specifier']:
        with pytest.raises(ValueError, match='UNSAFE_UNIT_ARGUMENT'):
            installer.command(Path(bad), Path('/var/review'))


def test_scratch_install_is_additive_held_and_preserves_previous_pieces(tmp_path, monkeypatch):
    import types
    system = tmp_path / 'host'; system.mkdir(mode=0o700)
    real_path = Path
    def mapped(value):
        p = real_path(value)
        if str(p).startswith(('/etc/', '/var/lib/')): return system / str(p).lstrip('/')
        return p
    monkeypatch.setattr(installer, 'Path', mapped)
    monkeypatch.setattr(installer.os, 'geteuid', lambda: 0)
    monkeypatch.setattr(installer.os, 'chown', lambda *args: None)
    monkeypatch.setattr(installer, 'sys', types.SimpleNamespace(flags=types.SimpleNamespace(no_user_site=1)))
    monkeypatch.setattr(installer, 'trusted', lambda p: p)
    monkeypatch.setattr(installer, 'approval', lambda p: {'source_sha': 'a'*40, 'report_sha256': 'b'*64})
    unit = mapped('/etc/systemd/system') / (installer.ROOT.name + '.service')
    drops = unit.with_name(unit.name + '.d'); drops.mkdir(parents=True, mode=0o700)
    private_records.write_text(unit, 'synthetic unchanged main unit')
    runtime = mapped('/etc/research-system-manual-sprint10/releases') / installer.ROOT.name / 'runtime.json'
    private_records.mkdir(runtime.parent, parents=True); atomic(runtime, {'synthetic': True})
    monkeypatch.setattr(installer, 'OLD_UNIT_SHA', digest(unit.read_bytes()))
    monkeypatch.setattr(installer, 'RUNTIME_SHA', digest(runtime.read_bytes()))
    prior = {}
    for name in installer.OLD_DROPS:
        private_records.write_text(drops / name, 'synthetic unchanged ' + name)
        prior[name] = digest((drops / name).read_bytes())
    monkeypatch.setattr(installer, 'OLD_DROPS', prior)
    records = mapped('/var/lib/research-system-manual-sprint10-deployment') / installer.ROOT.name
    private_records.mkdir(records, parents=True)
    events = []
    def write(path, data):
        assert not path.exists()
        private_records.write_bytes(path, data)
        path.chmod(0o440)
    monkeypatch.setattr(installer, 'private_new_file', write)
    def observe(args, **kwargs):
        assert args[0] == '/usr/bin/systemctl'
        events.append(args)
        if 'ActiveState' in args: return 'inactive\n'
        if 'DropInPaths' in args: return ' '.join(str(drops / n) for n in prior)
        if 'ExecStart' in args:
            assert any('daemon-reload' in item for item in events)
            return '{ argv[]=' + (drops / '50-evidence-delivery.conf').read_text().split('ExecStart=')[-1].strip() + ' ; }'
        pytest.fail(str(args))
    monkeypatch.setattr(installer.subprocess, 'check_output', observe)
    monkeypatch.setattr(installer.subprocess, 'run', lambda args, **kwargs: events.append(args))
    result = installer.install('/var/review')
    assert result['status'] == 'INSTALLED_HELD'
    assert all(digest((drops / n).read_bytes()) == h for n,h in prior.items())
    assert digest(unit.read_bytes()) == installer.OLD_UNIT_SHA
    assert digest(runtime.read_bytes()) == installer.RUNTIME_SHA
    assert not any(any(word in item for word in ('start','enable','restart')) for item in events)
    assert (drops / '50-evidence-delivery.conf').stat().st_mode & 0o777 == 0o440
    with pytest.raises(ValueError, match='EXISTING_EVIDENCE_INSTALL_RECONCILE'):
        installer.install('/var/review')
