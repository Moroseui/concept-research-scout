"""Cross-file regression: individually valid source pins do not bind evidence."""
import copy
import pytest
from orchestrator.prepare_deployment_bundle import investigator_target_binding
from orchestrator.handover_coordinator import digest, encoded
from orchestrator.deployment_review import digest as bytes_digest

CONTROLLER='/etc/research-system/live-research/controller.json'
EVIDENCE='/etc/research-system/live-research/report-evidence.json'
def fixture():
    raw=encoded({'source':'a'*40,'reviewer_evidence':{}});pin=bytes_digest(raw)
    template={'schema':'investigator-template/v1','template_id':'binding-test','experiment':'P001','request':'Inspect bounded evidence','references':[],'evidence_file':EVIDENCE,'evidence_sha256':pin,'change_request':{'request_id':'b'*64,'applied_event':'c'*64}}
    config={'source':'a'*40,'investigator':{'template':template,'template_sha256':digest(template)}}
    return config,raw

def inputs(config,raw):
    controller=encoded(config);cp=bytes_digest(controller);ep=bytes_digest(raw)
    return {CONTROLLER:{'sha256':cp},EVIDENCE:{'sha256':ep}},{cp:controller,ep:raw}

def test_assembled_targets_match():
    config,raw=fixture();result=investigator_target_binding(*inputs(config,raw));assert result['evidence_sha256']==bytes_digest(raw)

@pytest.mark.parametrize('damage',['old_evidence','old_template','wrong_target','missing_target','changed_literal'])
def test_assembled_binding_fails_closed(damage):
    config,raw=fixture()
    if damage=='old_evidence':
        config['investigator']['template']['evidence_sha256']='d'*64
        config['investigator']['template_sha256']=digest(config['investigator']['template'])
    if damage=='old_template':config['investigator']['template_sha256']='e'*64
    if damage=='wrong_target':
        config['investigator']['template']['evidence_file']='/etc/research-system/other.json'
        config['investigator']['template_sha256']=digest(config['investigator']['template'])
    targets,literals=inputs(config,raw)
    if damage=='missing_target':targets.pop(EVIDENCE)
    if damage=='changed_literal':literals[targets[EVIDENCE]['sha256']]=raw+b' '
    with pytest.raises(ValueError):investigator_target_binding(targets,literals)

def test_optional_investigator_stays_optional():
    config,raw=fixture();config.pop('investigator');assert investigator_target_binding(*inputs(config,raw)) is None
