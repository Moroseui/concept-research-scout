import json
from types import SimpleNamespace
import pytest
from orchestrator.reviewer_evidence import collect, validate, SOURCES, UNITS


def request(kind='service_runtime'):
    return {'kind': kind, 'purpose': 'Verify deployed evidence', 'affected_task': 'deployment'}


def test_request_is_closed_and_deduplicable():
    assert validate(request()) == validate(dict(reversed(list(request().items()))))
    for bad in ({**request(), 'command': 'id'}, {**request(), 'kind': '../../private'},
                {**request(), 'purpose': ''}):
        with pytest.raises(ValueError): validate(bad)


def test_missing_is_not_success_and_receipts_remain_historical(tmp_path):
    result = collect(tmp_path, request())
    assert result['records'][0]['status'] == 'UNAVAILABLE'
    name = SOURCES['service_runtime'][0]
    path = tmp_path/name; path.parent.mkdir(parents=True); path.write_text('{"old":true}')
    result = collect(tmp_path, request())
    assert result['records'][0]['status'].startswith('HISTORICAL')
    assert not result['current_observations']


def test_hosted_fixed_commands_only_and_no_stderr(monkeypatch, tmp_path):
    calls = []
    def run(command, **kwargs):
        calls.append(command)
        return SimpleNamespace(returncode=0, stdout='LoadState=not-found\nEnvironment=PRIVATE\nUser=\n', stderr='PRIVATE')
    monkeypatch.setattr('orchestrator.reviewer_evidence.subprocess.run', run)
    result = collect(tmp_path, request(), hosted=True)
    assert len(calls) == len(UNITS)
    assert all(item['status']=='UNIT_NOT_FOUND' and item['properties']=={'LoadState':'not-found'} for item in result['current_observations'])
    assert 'PRIVATE' not in json.dumps(result)
    assert all(not item['execution_proven'] for item in result['current_observations'])
    assert all(command[:2] == ['systemctl', 'show'] for command in calls)


def test_failed_live_collection_preserves_historical_records(monkeypatch, tmp_path):
    def unavailable(*args, **kwargs): raise FileNotFoundError('systemctl')
    monkeypatch.setattr('orchestrator.reviewer_evidence.subprocess.run', unavailable)
    result = collect(tmp_path, request(), hosted=True)
    assert result['records']
    assert all(row['status'] == 'COLLECTION_FAILED' for row in result['current_observations'])


def test_implementation_evidence_is_not_mislabeled_as_execution(tmp_path):
    name=SOURCES['handover_implementation'][0]
    path=tmp_path/name;path.parent.mkdir(parents=True);path.write_text('"""Synthetic source fixture."""\n')
    result=collect(tmp_path,request('handover_implementation'))
    assert result['records'][0]['status']=='SOURCE_CODE_NOT_EXECUTION_PROOF'
    assert not result['current_observations']
