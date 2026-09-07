import hashlib
import json
from pathlib import Path
import pytest
from orchestrator.research_context import evidence_context,proposal_context


def test_pending_never_exposes_unreviewed_conclusions(tmp_path):
    (tmp_path/'evidence').mkdir()
    row=dict(id='pending',charters=['prediction'],tags=['negative'],dependencies=['original_console'],status='PENDING',interpretation='MUST_NOT_LEAK')
    (tmp_path/'evidence/research_context.json').write_text(json.dumps({'entries':[row]}))
    r=evidence_context(tmp_path,'prediction')
    assert r['entries'][0]['disposition']=='PENDING_EVIDENCE_NO_CONCLUSIONS'
    assert 'MUST_NOT_LEAK' not in json.dumps(r)
    assert evidence_context(tmp_path,'other')['entries']==[]
    assert evidence_context(tmp_path,'prediction',blind=True)['entries']==[]


def test_actual_conclusions_next_decision_and_stale_binding(tmp_path):
    (tmp_path/'evidence').mkdir()
    record={'status':'AGENT_REVIEWED_NOT_HUMAN_RATIFIED'}
    row=dict(id='predecessor',charters=['prediction'],tags=['negative'],dependencies=[],status='REVIEWED_CONCLUSIONS',receipt='receipt.json')
    for key,name,body in [('interpretation_sha256','interpretation','Negative finding with limitations'),('review_sha256','review','Opposing review'),('proposal_sha256','next_decision','Next decision: assess generality')]:
        row[name]=name+'.md';(tmp_path/row[name]).write_text(body);record[key]=hashlib.sha256(body.encode()).hexdigest()
    (tmp_path/'receipt.json').write_text(json.dumps(record));row['receipt_sha256']=hashlib.sha256((tmp_path/'receipt.json').read_bytes()).hexdigest()
    (tmp_path/'evidence/research_context.json').write_text(json.dumps({'entries':[row]}))
    assert 'Next decision' in json.dumps(evidence_context(tmp_path,'prediction'))
    (tmp_path/'interpretation.md').write_text('changed')
    with pytest.raises(ValueError,match='BINDING_CHANGED'):evidence_context(tmp_path,'prediction')


def test_real_proposal_context_is_preview():
    root=Path(__file__).resolve().parents[1]
    proposal='campaigns/isles24-pilot/pipeline/prediction-charter-20260906-v1'
    if not (root/proposal).exists():pytest.skip('live proposal not in fixture checkout')
    r=proposal_context(root,proposal)
    assert json.loads(r['context-disposition.json'])['ratified'] is False


def test_actual_campaign_and_scout_paths_respect_pending_and_blinding(tmp_path,monkeypatch):
    import scout
    from orchestrator.campaign_pipeline import grounding
    (tmp_path/'evidence').mkdir();(tmp_path/'orchestrator/prompts').mkdir(parents=True)
    (tmp_path/'orchestrator/prompts/scout.md').write_text('Legacy task')
    (tmp_path/'CHARTER.md').write_text('Legacy charter unchanged')
    (tmp_path/'evidence/research_context.json').write_text(json.dumps({'entries':[dict(id='pending-source',charters=[''],tags=['stroke'],dependencies=['original_console'],status='PENDING',interpretation='DO_NOT_EXPOSE')]}))
    target=tmp_path/'target';target.mkdir()
    monkeypatch.setattr(scout,'ROOT',tmp_path);monkeypatch.setattr(scout,'PROMPTS',tmp_path/'orchestrator/prompts')
    monkeypatch.setattr(scout,'charter_for_target',lambda target:'')
    monkeypatch.setattr(scout,'_target_context',lambda stage,target:'')
    monkeypatch.setattr(scout,'_brief_path',lambda charter:tmp_path/'evidence/brief.md')
    ordinary=scout.build_prompt('scout',target)
    assert 'PENDING_EVIDENCE_NO_CONCLUSIONS' in ordinary and 'DO_NOT_EXPOSE' not in ordinary
    assert 'Legacy task' in ordinary and 'Legacy charter unchanged' in ordinary
    blind=next(iter(scout.BLIND_STAGES))
    assert 'pending-source' not in scout.build_prompt(blind,target)


def test_proposal_parent_traversal_rejected(tmp_path):
    with pytest.raises(ValueError,match='PROPOSAL_SCOPE'):
        proposal_context(tmp_path,'campaigns/isles24-pilot/pipeline/../../../ideas/fabricated')


def test_legacy_stage_target_does_not_select_other_charter(tmp_path,monkeypatch):
    import scout
    monkeypatch.setattr(scout,'ROOT',tmp_path)
    baseline=tmp_path/'ideas/scout-001';baseline.mkdir(parents=True)
    named=tmp_path/'ideas/scout-isles24-001';named.mkdir()
    assert scout.stage_target('scout',None)==baseline
    assert scout.stage_target('scout','isles24-001')==named


def test_operator_selected_campaign_uses_bound_prediction_guidance(tmp_path):
    import shutil
    from orchestrator.research_context import selected_prediction_context
    from orchestrator.campaign_pipeline import grounding
    root=Path(__file__).resolve().parents[1]
    r=selected_prediction_context(root)
    assert json.loads(r['context-disposition.json'])['ratified'] is True
    assert json.loads(r['context-disposition.json'])['launch_authorized'] is False
    supplied=grounding(root,'P001')
    assert 'docs/SCORING_RUBRIC.md' not in supplied
    assert any(k.endswith('PROMPTS.proposed.md') for k in supplied)
    # Copy only bound inputs, then corrupt an approved charter: refuse before a model.
    decision=json.loads((root/'campaigns/isles24-pilot/prediction_selection.json').read_text())
    proposal_receipt=json.loads((root/decision['proposal']/'receipt.json').read_text())
    inputs=[name for name in proposal_receipt['input_sha256'] if name.startswith('campaigns/isles24-pilot/')]
    for name in [*decision['artifact_sha256'],*inputs,'campaigns/isles24-pilot/prediction_selection.json']:
        p=tmp_path/name;p.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(root/name,p)
    target=next(k for k in decision['artifact_sha256'] if k.endswith('CHARTER.proposed.md'))
    (tmp_path/target).write_text('unapproved change')
    with pytest.raises(ValueError,match='BINDING_CHANGED'):
        selected_prediction_context(tmp_path)


def test_hosted_envelope_supplies_current_selected_authority():
    from orchestrator.hosted_context import build
    root=Path(__file__).resolve().parents[1]
    packet=build(root,{'jobs':[{'id':'synthetic-readiness','status':'READY'}]})
    selection=packet['selected_scientific_context']
    disposition=json.loads(selection['context-disposition.json']['content'])
    assert disposition['ratified'] is True and disposition['launch_authorized'] is False
    assert 'campaigns/isles24-pilot/prediction_selection.json' in selection
    assert packet['proposed_context_not_authority']=={}
    assert 'HISTORICAL_CHARTER' in packet['documents']['charters/isles24/CHARTER.md']['disposition']
