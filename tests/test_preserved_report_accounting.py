"""Pinned prior reports are preserved, never reclassified as terminal units."""
from copy import deepcopy
import json
from unittest.mock import patch
import pytest
from orchestrator import inspection_admission_recovery as r
from orchestrator import install_reviewed_deployment as installer
from test_inspection_admission_recovery import Fixture, event, original, write
from test_terminal_accounting_transition import manual_event


def scenario(tmp_path):
    f = Fixture(tmp_path, n=48)
    cases = []
    for ev in (manual_event(90), event(236), manual_event(126)):
        raw = f.admit(ev)
        cases.append({'event': ev, 'receipt': json.loads(raw['receipt_original']),
                      'state_after': f.head})
    prior = [{**cases[0], 'receipt_origin': 'RECORDED_BROKER_REPLY'},
             {**cases[1], 'receipt_origin': 'DERIVED_FROM_AUTHENTICATED_LEDGER'}]
    baseline = {'ledger': f.baseline, 'preserved_admissions': prior}
    account = {'schema': 'server-terminal-accounting/v1',
               'cases': [cases[2]], 'ledger_pin': f.head}
    return f, baseline, account


def replay(f, baseline, account):
    ordered = installer.terminal_admission_cases(account, baseline)
    return r.verify_terminal_transition(
        f.repo, f.baseline, f.policy,
        [original(x['event'], x['receipt']) for x in ordered], f.status(),
        server_profile=True,
        preserved_admissions_count=len(baseline['preserved_admissions']),
        preserved_nightly_admissions=[original(x['event'], x['receipt'])
            for x in baseline['preserved_admissions']
            if x['event']['kind'] == 'nightly_review'])


def test_mixed_history_is_exactly_replayed_without_billing_reports_as_reviews(tmp_path):
    f, baseline, account = scenario(tmp_path)
    old = deepcopy((f.state, f.baseline, baseline, account))
    proof = replay(f, baseline, account)
    assert proof['current_head'] == f.head and len(proof['suffix']) == 3
    assert proof['git_mutations'] == proof['remote_calls'] == 0
    assert proof['preserved_nightly_admissions_sha256'] == r.digest(r.encoded([
        original(baseline['preserved_admissions'][1]['event'],
                 baseline['preserved_admissions'][1]['receipt'])]))
    assert (f.state, f.baseline, baseline, account) == old
    assert len(account['cases']) == 1 and f.state['resets'] == []


@pytest.mark.parametrize('damage', [
    'missing', 'duplicate', 'parent', 'head', 'event', 'receipt', 'relabel',
    'extra', 'reset', 'file-content', 'file-metadata', 'unknown-object',
    'count-not-pinned', 'unlisted-original', 'duplicate-original', 'review-unit'])
def test_report_preservation_does_not_waive_other_boundaries(tmp_path, damage):
    f, baseline, account = scenario(tmp_path)
    prior = baseline['preserved_admissions'][1]
    if damage == 'missing': baseline['preserved_admissions'].pop()
    elif damage == 'duplicate': baseline['preserved_admissions'].append(deepcopy(prior))
    elif damage == 'parent': prior['receipt']['state_before'] = 'e' * 40
    elif damage == 'head': prior['state_after'] = 'e' * 40
    elif damage == 'event': prior['event']['turn_id'] = 'e' * 64
    elif damage == 'receipt': prior['receipt']['count'] += 1
    elif damage == 'relabel': prior['event']['kind'] = 'astra_turn'
    elif damage == 'extra':
        f.admit(event(999)); account['ledger_pin'] = f.head
    elif damage == 'reset':
        state = deepcopy(f.state)
        state['resets'].append({'approval_sha256': 'd' * 64,
            'expected_sequence': state['sequence'], 'at': '2026-09-12T00:00:00Z'})
        state.update(sequence=state['sequence']+1, count=0, halted=False)
        f.commit(state); account['ledger_pin'] = f.head
    elif damage == 'file-content':
        path = f.git / 'config'; write(path, path.read_bytes() + b'\n[include]\npath = /outside\n')
    elif damage == 'file-metadata': (f.git / 'config').chmod(0o640)
    elif damage == 'unknown-object': f.obj('blob', b'unrelated object')
    elif damage == 'review-unit':
        account['cases'].append(baseline['preserved_admissions'].pop())
    if damage in {'count-not-pinned', 'unlisted-original', 'duplicate-original'}:
        ordered = installer.terminal_admission_cases(account, baseline)
        originals = [original(x['event'], x['receipt']) for x in ordered]
        pinned = [original(prior['event'], prior['receipt'])]
        count = 2
        if damage == 'count-not-pinned': count = 0
        elif damage == 'unlisted-original':
            value = json.loads(pinned[0]['event_original']); value['turn_id'] = 'e' * 64
            pinned[0]['event_original'] = r.encoded(value).decode()
        else: pinned.append(deepcopy(pinned[0]))
        with pytest.raises(ValueError):
            r.verify_terminal_transition(f.repo, f.baseline, f.policy,
                originals, f.status(), preserved_admissions_count=count,
                preserved_nightly_admissions=pinned, server_profile=True)
    else:
        with pytest.raises(ValueError): replay(f, baseline, account)


def test_terminal_nightly_requires_explicit_pins_even_when_count_is_nonzero(tmp_path):
    f, baseline, account = scenario(tmp_path)
    ordered = installer.terminal_admission_cases(account, baseline)
    with pytest.raises(ValueError, match='ONLY_SUCCESSFUL_REVIEW_ADMISSION'):
        r.verify_terminal_transition(f.repo, f.baseline, f.policy,
            [original(x['event'], x['receipt']) for x in ordered], f.status(),
            preserved_admissions_count=2, server_profile=True)


def test_actual_installer_caller_passes_only_recovery_bound_report_originals(tmp_path):
    f, baseline, account = scenario(tmp_path)
    baseline.update(policy_sha256=installer.gate.digest(installer.gate.encoded(f.policy)),
                    control_snapshot={'revision': 29, 'paused': True}, non_ledger_files={})
    recovery = {'terminal_admissions': baseline, 'preserved_state_sha256': 'a' * 64}
    proposal = {'review_profile': 'server-terminal-review/v1', 'recovery_sha256': 'b' * 64}
    accounting = {'ledger_pin': f.head}
    ordered = installer.terminal_admission_cases(account, baseline)
    values = [original(x['event'], x['receipt']) for x in ordered]
    broker = {'policy': f.policy}
    with patch.object(installer, '_terminal_accounting_admissions', return_value=(account, values)), \
         patch.object(installer, '_inspection_control', return_value=baseline['control_snapshot']), \
         patch.object(installer, 'authenticated_ledger_status', return_value=f.status()), \
         patch.object(installer, '_ledger_path', return_value=f.repo), \
         patch.object(installer, 'state_inventory', return_value={}), \
         patch.object(installer, '_non_ledger', return_value={}), \
         patch.object(installer, 'state_fingerprint', return_value=installer.inventory_fingerprint({})):
        _, proof = installer.terminal_preserved_state(None, proposal, recovery, broker, accounting)
    assert proof['ledger_transition']['preserved_nightly_admissions_sha256']
    assert len(account['cases']) == 1
