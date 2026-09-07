import hashlib
import json
from pathlib import Path
import pytest

from orchestrator.operations_report import Queue,finalize
from orchestrator.report_delivery import assets,deliver


def report(tmp_path):
    root=tmp_path/'reports'
    row=finalize(root,'a'*40,'2026-09-07',[],task_state={'next_task':'Bounded synthetic test'})
    q=Queue(root);claim=q.claim(row['id']);review='Reviewed supplied synthetic evidence.'
    q.attach(row['id'],claim['attempt_id'],review,{'family':'claude','model':'fixture',
        'source':'a'*40,'report_sha256':row['id'],'review_sha256':hashlib.sha256(review.encode()).hexdigest(),
        'execution_receipt_sha256':'b'*64,'session_id':'synthetic-fixture','status':'COMPLETE'})
    q.disposition(row['id'],'Recorded fixture response; no patient execution.')
    return root,row['id']


def test_only_checked_complete_report_assets(tmp_path):
    root,identity=report(tmp_path)
    (root/'private-console.stdout').write_text('must never be copied')
    files=assets(root,identity)
    assert len(files)==6 and all('stdout' not in n for n in files)
    assert any(n.endswith('.receipts.json') for n in files)
    assert any(n.endswith('.context.json') for n in files)
    (root/(identity+'.claude-review.md')).write_text('changed')
    with pytest.raises(ValueError,match='REVIEW_CHANGED'):assets(root,identity)


def test_linked_evidence_or_unreviewed_report_refuses(tmp_path):
    root,identity=report(tmp_path)
    linked=next(root.glob('*.receipts.json'));linked.write_text('[]')
    with pytest.raises(ValueError,match='LINKED_EVIDENCE_CHANGED'):assets(root,identity)
    q=Queue(root);q.db.execute("UPDATE reviews SET status='NOT_REVIEWED'")
    with pytest.raises(ValueError,match='REVIEW_REQUIRED'):assets(root,identity)


def test_delivery_does_not_rebuild_partial_preparation(tmp_path):
    root,identity=report(tmp_path);state=tmp_path/'delivery';state.mkdir(mode=0o700)
    (state/identity).mkdir()
    with pytest.raises(ValueError,match='PARTIAL_REPORT_PREPARATION'):
        deliver(root,identity,tmp_path/'checkout',state,'unused','c'*64)
    with pytest.raises(ValueError,match='INVALID_PIN'):
        deliver(root,'../escape',tmp_path/'checkout',state,'unused','c'*64)


def test_lost_push_response_recovers_exact_candidate_without_send(tmp_path,monkeypatch):
    import orchestrator.report_delivery as m
    root,identity=report(tmp_path);state=tmp_path/'delivery';state.mkdir(mode=0o700)
    folder=state/identity;folder.mkdir()
    candidate={'source':'d'*40,'before':'e'*40,'inventory':{},'bundle_sha256':'f'*64,
               'permission_sha256':'c'*64}
    (folder/'candidate.json').write_text(json.dumps(candidate))
    calls=[]
    def forbidden(socket,operation,body):
        if operation=='publication_status':
            return {'status':'OBSERVED','source':'d'*40,'repository':m.REMOTE,'branch':m.BRANCH}
        calls.append(operation);raise AssertionError('No replay')
    result=m.deliver(root,identity,tmp_path/'checkout',state,'unused','c'*64,send=forbidden)
    assert result['status']=='PUBLISHED' and not calls
    assert m.deliver(root,identity,tmp_path/'checkout',state,'unused','c'*64,send=forbidden)==result


def test_actual_git_preparation_receiver_and_bounded_retry(tmp_path,monkeypatch):
    import base64
    import orchestrator.report_delivery as m
    from orchestrator.publication_candidate import receive
    from test_publication_candidate import repositories,git
    root,identity=report(tmp_path)
    author,cache,before=repositories(tmp_path)
    git(author,'switch','-c',m.BRANCH);git(author,'remote','add','origin',m.REMOTE)
    observed=[before]
    calls=[]
    def broker(socket,operation,body):
        if operation=='publication_status':
            return {'status':'OBSERVED','source':observed[0],'repository':m.REMOTE,'branch':m.BRANCH}
        calls.append(operation)
        if operation=='stage_candidate':
            return receive(cache,body['source'],body['before'],body['inventory'],
                base64.b64decode(body['bundle_base64']),body['bundle_sha256'])
        assert operation=='publish'
        observed[0]=body['source']
        raise ConnectionError('Synthetic lost push response')
    state=tmp_path/'delivery'
    with pytest.raises(ConnectionError):
        m.deliver(root,identity,author,state,'synthetic','c'*64,send=broker)
    assert calls==['stage_candidate','publish']
    result=m.deliver(root,identity,author,state,'synthetic','c'*64,send=broker)
    assert result['status']=='PUBLISHED' and calls==['stage_candidate','publish']
    assert git(author,'show','-s','--format=%an')=='Astra (OpenAI agent)'
    assert git(cache,'rev-parse','HEAD')==result['source']
    assert not (cache/'docs/operations/daily/private-console.stdout').exists()
