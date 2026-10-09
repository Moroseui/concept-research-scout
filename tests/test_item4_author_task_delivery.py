"""Exact task relocation retains authority, scanning, and the final prompt bound."""
import json
import pytest
from orchestrator import manual_context as mc,context_budget as budget
from orchestrator.manual_driver import Driver
from orchestrator.manual_executor import digest
from test_context_budget import root,add_obligation,save_manifest
from test_experiment_context import experiment
from test_experiment_plan_output import validation_args


@pytest.fixture
def delivery(experiment,monkeypatch):
    from test_scientific_intake import save_registry
    from orchestrator import private_records as pr
    d,value,_,_=validation_args(experiment)
    registry=json.loads((d.context/d.config['private_intake']['path']).read_bytes())
    registry.update(task='sprint13b-execution',idea_ids=['sprint13b-execution'])
    d.config['private_intake']=save_registry(d.context,registry)
    d.config['notebook_revision'].update(safe_view={'sha256':'a'*64},environment={'environment_root':'/synthetic-tools','environment_sha256':'b'*64})
    prep=json.loads((d.state/'preparation-plan.json').read_bytes())
    for key in ('private_intake','notebook_revision'):prep[key]=d.config[key]
    pr.write_text(d.state/'preparation-plan.json',json.dumps(prep));d.config['plan_sha256']=digest((d.state/'preparation-plan.json').read_bytes())
    # Same configuration-only fixture as existing caller test; actual server
    # preflight separately authenticates the real notebook configuration.
    monkeypatch.setattr('orchestrator.notebook_revision.validate_config',lambda *args:None)
    return d,value


def test_actual_item4_author_receives_complete_task_as_bound_file(delivery):
    d,value=delivery
    task='Unique synthetic instruction. '+('Preserve this exact interface detail. '*550)
    d.task=lambda stage,value:task
    work=d.state/'task-delivery'
    body,m=Driver.prepare_input(d,value,'run_spec_author',work)
    ref=next(x for x in m['workspace_files'] if x['id']=='scientific-author-instructions')
    raw=(work/ref['path']).read_bytes()
    assert digest(raw)==ref['sha256'] and len(raw)==ref['bytes']
    assert task in raw.decode() and 'contract' in raw.decode() and 'SPEC.proposed.md' in raw.decode()
    assert task not in body and ref['sha256'] in body and 'Read the complete scientific-author-instructions' in body
    assert len(body)==m['characters']<200000
    for x in m['workspace_files']:assert digest((work/x['path']).read_bytes())==x['sha256']


def test_secret_in_relocated_task_is_still_refused(delivery):
    d,value=delivery
    d.task=lambda stage,value:'sk-'+('syntheticsecrettaskfixture'*4)
    work=d.state/'bad-task'
    with pytest.raises(ValueError,match="PUBLICATION_CONTENT_REJECTED"):Driver.prepare_input(d,value,'run_spec_author',work)
    assert not work.exists()


def test_other_stage_and_item_keep_inline_task(experiment):
    d,value=experiment
    d.task=lambda stage,value:'Exact item6 author task marker.'
    body,m=Driver.prepare_input(d,value,'run_spec_author',d.state/'item6')
    assert 'Exact item6 author task marker.' in body
    assert not any(x['id']=='scientific-author-instructions' for x in m['workspace_files'])


def test_scoped_stop_remains_fatal_before_file_delivery(delivery):
    d,value=delivery;add_obligation(d.context,'stop')
    p=d.context/budget.PROJECT/'obligations.json';v=json.loads(p.read_bytes())
    v['obligations'][-1]['scope'].update(idea_ids=['sprint13b-execution'],stages=['run_spec_author'])
    p.write_text(json.dumps(v));save_manifest(d.context)
    work=d.state/'stopped'
    with pytest.raises(budget.ContextError,match='SCOPED_STOP'):Driver.prepare_input(d,value,'run_spec_author',work)
    assert not work.exists()
