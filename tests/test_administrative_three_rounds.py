"""Synthetic native receipts and real reservation transactions; no model calls."""
import json
from pathlib import Path
from datetime import datetime,timezone
import subprocess
import pytest
from orchestrator import autonomy_review as ar, autonomy_review_runner as runner
from test_autonomy_review import native


@pytest.fixture
def lane(tmp_path):
    repo=tmp_path/'repo';repo.mkdir();(repo/'worker.py').write_text('synthetic=1\n')
    subprocess.run(['git','init','-q',str(repo)],check=True)
    subprocess.run(['git','-C',str(repo),'add','.'],check=True)
    subprocess.run(['git','-C',str(repo),'-c','user.name=Synthetic','-c','user.email=test@invalid','commit','-qm','fixture'],check=True)
    source=subprocess.check_output(['git','-C',str(repo),'rev-parse','HEAD'],text=True).strip()
    runtime=tmp_path/'runtime.json';runtime.write_text('{"synthetic":true}')
    evidence=tmp_path/'evidence';evidence.mkdir()
    queue=runner.ReviewQueue(tmp_path/'state')
    def prepare(n, predecessor=None):
        (evidence/'repair.txt').write_text('Synthetic concrete repair '+str(n))
        folder=tmp_path/('packet'+str(n))
        ar.prepare(repo,source,runtime,evidence,['worker.py'],folder,'Inspect synthetic repair '+str(n),
                   change_id='synthetic-three-rounds',round_number=n,predecessor=predecessor,prompt_version=5)
        return ar.verify_packet(folder)
    def finish(m,verdict='REVISE'):
        row,fresh=queue.reserve(m,{'synthetic':True});assert fresh
        folder=queue.folder/row['id'];folder.mkdir()
        events=native(m,'CHANGES REQUIRED' if verdict=='REVISE' else verdict)
        raw='\n'.join(json.dumps(e) for e in events).encode()
        result=ar.extract_result(raw.decode(),m,0)
        receipt={k:m[k] for k in ['source_sha','runtime_sha256','change_id','round']}
        receipt.update(exit_code=0,verdict=result['verdict'],report_sha256=ar.sha(result['report'].encode()),native_stream_sha256=ar.sha(raw))
        for name,body in [('native-stream.jsonl',raw),('packet-manifest.json',ar.canonical(m)),('report.md',result['report'].encode()),('receipt.json',ar.canonical(receipt))]:
            (folder/name).write_bytes(body)
        assert ar.verify_result(folder)==receipt
        queue.finish(row['id'],'COMPLETE',receipt)
        return folder
    yield queue,prepare,finish
    queue.db.close()


def test_third_links_latest_genuine_revise_preserves_history_and_fourth_refuses(lane):
    q,prepare,finish=lane
    p1=finish(prepare(1));p2=finish(prepare(2,p1))
    old=[dict(r) for r in q.db.execute('SELECT * FROM autonomy_calls ORDER BY round')]
    m3=prepare(3,p2);p3=finish(m3)
    assert [dict(r) for r in q.db.execute('SELECT * FROM autonomy_calls ORDER BY round LIMIT 2')]==old
    row=dict(q.db.execute('SELECT * FROM autonomy_calls WHERE round=3').fetchone())
    binding=json.loads(row['binding']);assert binding['max_rounds']==3 and binding['round_authority_sha256']==ar.ROUND_AUTHORITY
    before=list(q.db.iterdump())
    with pytest.raises(ValueError,match='REVIEW_THREE_ROUND_LIMIT'):prepare(4,p3)
    forged={**m3,'round':4,'predecessor':{'receipt_sha256':ar.sha((p3/'receipt.json').read_bytes()),'report_sha256':ar.verify_result(p3)['report_sha256']}}
    with pytest.raises(ValueError,match='REVIEW_THREE_ROUND_LIMIT'):q.reserve(forged,{})
    assert list(q.db.iterdump())==before
    again,fresh=q.reserve(m3,{});assert not fresh and again['id']==row['id']


@pytest.mark.parametrize('verdict',['APPROVE','REJECT'])
def test_no_successor_after_terminal_verdict(lane,verdict):
    q,prepare,finish=lane;p1=finish(prepare(1),verdict)
    before=list(q.db.iterdump())
    with pytest.raises(ValueError,match='REVIEW_PREDECESSOR_SCOPE'):prepare(2,p1)
    assert list(q.db.iterdump())==before


def test_third_cannot_link_first_or_skip_native_qualification(lane):
    q,prepare,finish=lane;p1=finish(prepare(1));p2=finish(prepare(2,p1))
    with pytest.raises(ValueError,match='REVIEW_PREDECESSOR_SCOPE'):prepare(3,p1)
    m=prepare(3,p2);before=list(q.db.iterdump())
    bad={**m,'predecessor':{'receipt_sha256':ar.sha((p1/'receipt.json').read_bytes()),'report_sha256':ar.verify_result(p1)['report_sha256']}}
    with pytest.raises(ValueError,match='REVIEW_PREDECESSOR_BINDING'):q.reserve(bad,{})
    mechanical={**m,'predecessor':{'kind':'known_terminal_60_turn_exhaustion'}}
    with pytest.raises(ValueError,match='THIRD_ROUND_REQUIRES_GENUINE_REVISE'):q.reserve(mechanical,{})
    assert list(q.db.iterdump())==before


def test_fifty_day_cap_including_failures_still_refuses_third(lane):
    q,prepare,finish=lane;p1=finish(prepare(1));p2=finish(prepare(2,p1));m=prepare(3,p2)
    day=datetime.now(timezone.utc).date().isoformat()
    for i in range(48):q.db.execute('INSERT INTO autonomy_calls VALUES(?,?,?,?,?,?,?,?)',
        ('other-'+str(i),'implementation_review','other-'+str(i),1,day,'FAILED','{}','{}'))
    before=list(q.db.iterdump())
    with pytest.raises(ValueError,match='AUTONOMY_DAILY_CALL_LIMIT'):q.reserve(m,{})
    assert list(q.db.iterdump())==before


def test_operator_text_drift_refuses_preparation_and_admission(lane,tmp_path,monkeypatch):
    q,prepare,finish=lane
    m=prepare(1)
    fake=tmp_path/'altered/orchestrator';fake.mkdir(parents=True);docs=fake.parent/'docs';docs.mkdir()
    (docs/'ADMINISTRATIVE_REVIEW_OPERATOR_DECISION_20261008.txt').write_text('not the operator decision')
    monkeypatch.setattr(ar,'__file__',str(fake/'autonomy_review.py'))
    before=list(q.db.iterdump())
    with pytest.raises(ValueError,match='ADMINISTRATIVE_ROUND_AUTHORITY_CHANGED'):q.reserve(m,{})
    assert list(q.db.iterdump())==before
