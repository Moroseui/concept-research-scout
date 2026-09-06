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
