"""Canonical current spec delivery uses the shared original-file contract."""
import json
import pytest
from orchestrator import manual_context as mc, experiment_approval as approval
from orchestrator.manual_driver import Driver
from orchestrator.manual_executor import digest
from test_experiment_approval import reviewed
from test_experiment_context import experiment, root


@pytest.mark.parametrize('reviewed',[4,6],indirect=True)
def test_scientific_approval_checks_original_spec_file_and_refuses_changed_delivery(reviewed):
    driver,value,work=reviewed
    measurement=json.loads((work/'input-measurement.json').read_bytes())
    row=next(r for r in measurement['workspace_files'] if r.get('id')=='run_spec')
    raw=(work/row['path']).read_bytes()
    assert digest(raw)==row['sha256']
    assert raw==(driver.context/row['source_path']).read_bytes()
    Driver._accept_completed(driver,value)
    approval.verify(driver,value)
    target=work/row['path'];target.chmod(0o600);target.write_bytes(raw+b' ')
    with pytest.raises(ValueError,match='EXPERIMENT_APPROVAL_EVIDENCE_CHANGED'):
        approval.verify(driver,value)


def test_other_artifact_classifications_and_all_provenance_rules_stay_explicit():
    assert mc.workspace_artifact('run_spec',artifact_id='run_spec')
    assert mc.workspace_artifact('proposed_run_spec',artifact_id='proposed_run_spec')
    assert not mc.workspace_artifact('run_spec',artifact_id='historical-spec')
    assert not mc.workspace_artifact('configuration',artifact_id='unrelated')
