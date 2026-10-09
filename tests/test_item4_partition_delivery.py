"""Actual bound review navigation + exact original supplementary evidence replay."""
from pathlib import Path
from types import SimpleNamespace
import json
import pytest
from orchestrator import scientific_intake as intake,manual_context as mc,private_records as pr
from orchestrator import experiment_partition_input as partitions,experiment_approval as approval
from orchestrator.manual_executor import digest
from tools import item4_validation_runtime as runtime
from test_experiment_context import experiment,root
from test_experiment_approval import reviewed as base_reviewed
from test_revision_evidence import fixture


@pytest.fixture
def reviewed(experiment,monkeypatch,request,tmp_path):
    d,value=experiment;record=tmp_path/'original-release';pr.mkdir(record/'evidence',parents=True)
    original_prepare=mc.prepare;original_views=intake.load_views
    monkeypatch.setattr(intake,'load_views',original_views) # Restore producer connection after test.
    saved={}
    def prepare(root,**kwargs):
        manifest,_,raw=fixture(record/'evidence')
        runtime.connect_evidence(d,SimpleNamespace(RECORD=record),manifest)
        saved.update(manifest=manifest,original=original_views,record=record)
        return original_prepare(root,**kwargs)
    monkeypatch.setattr(mc,'prepare',prepare)
    result=base_reviewed.__wrapped__(experiment,monkeypatch,request)
    return (*result,saved)

pytestmark=pytest.mark.parametrize('reviewed',['partitions4'],indirect=True)


def test_exact_registered_and_supplementary_views_seal_through_real_bound_navigation(reviewed):
    d,value,work,saved=reviewed
    measurement=json.loads((work/'input-measurement.json').read_bytes());prompt=(work/'prompt.md').read_text()
    index=measurement['private_scientific_index'];encoded=partitions.cb.encoded(index)
    assert encoded not in prompt
    assert any(x['id'].startswith('revision-evidence-') for x in measurement['private_scientific_views'])
    before=[tuple(r) for r in d.store.db.execute('SELECT * FROM manual_calls')]
    result=approval.record(d,value,value['pending'])
    assert result['private_execution_inputs']['frozen_partitions']['sha256']==d.config['frozen_partitions']['sha256']
    assert approval.verify(d,value)==result
    assert before==[tuple(r) for r in d.store.db.execute('SELECT * FROM manual_calls')]


@pytest.mark.parametrize('damage',['missing-nav','duplicate-nav','nav-not-in-prompt','nav-bytes','nav-hash','nav-size','nav-path','index-bytes','partition-bytes','omission-bytes','supplement-bytes','lost-producer','supplement-scope'])
def test_paged_delivery_and_original_scan_fail_closed(reviewed,monkeypatch,damage):
    d,value,work,saved=reviewed
    measurement=json.loads((work/'input-measurement.json').read_bytes());prompt=(work/'prompt.md').read_text()
    nav=next(x for x in measurement['workspace_files'] if x['id']=='scientific-review-artifact-index')
    if damage=='missing-nav':measurement['workspace_files'].remove(nav)
    elif damage=='duplicate-nav':measurement['workspace_files'].append(nav)
    elif damage=='nav-not-in-prompt':prompt=prompt.replace(partitions.cb.encoded(nav),'')
    elif damage=='nav-bytes':
        target=work/nav['path'];target.chmod(0o600) # Disposable synthetic original.
        pr.write_bytes(target,target.read_bytes()+b'changed')
    elif damage in {'nav-hash','nav-size','nav-path'}:
        old=partitions.cb.encoded(nav)
        if damage=='nav-hash':nav['sha256']='f'*64
        elif damage=='nav-size':nav['bytes']+=1
        else:nav['path']='../escape'
        prompt=prompt.replace(old,partitions.cb.encoded(nav))
    elif damage in {'index-bytes','partition-bytes','omission-bytes'}:
        ref=measurement['private_scientific_index'] if damage=='index-bytes' else next(x for x in measurement['workspace_files'] if x['id']=='synthetic-partitions-'+('view.txt' if damage=='partition-bytes' else 'omissions.json'))
        target=work/ref['path'];target.chmod(0o600) # Disposable synthetic original.
        pr.write_bytes(target,target.read_bytes()+b'changed')
    elif damage=='supplement-bytes':
        path=saved['record']/'evidence'/saved['manifest']['files'][0]['name'];pr.write_bytes(path,path.read_bytes()+b'changed')
    elif damage=='lost-producer':monkeypatch.setattr(intake,'load_views',saved['original'])
    else:d.config['private_intake']=dict(d.config['private_intake'],sha256='f'*64)
    with pytest.raises((ValueError,FileNotFoundError)):
        partitions.reviewed(d.config,d.context,work,measurement,prompt)
    assert 'reviewed_execution' not in value


def test_supplement_cannot_be_used_for_other_context_or_stage(reviewed,tmp_path):
    d,value,work,saved=reviewed
    for kwargs in [dict(root=tmp_path/'other-context'),dict(stage='result_interpretation_author'),dict(idea_ids=['other'])]:
        args={'root':d.context,'ref':d.config['private_intake'],'stage':'run_spec_review','idea_ids':d.config['idea_ids']};args.update(kwargs)
        with pytest.raises(ValueError,match='EVIDENCE_DELIVERY_SCOPE'):intake.load_views(**args)
