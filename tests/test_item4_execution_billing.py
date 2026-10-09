"""Synthetic integration; no real authority, provider SDK or spending."""
from pathlib import Path
from types import SimpleNamespace as NS
import pytest
from tools import item4_execution_billing as route,install_item4_execution_billing as installer
from orchestrator import modal_billing
from test_modal_billing import workspace,NOW


def test_existing_provider_uses_connected_reader_and_preserves_prior_authority(monkeypatch):
    events=[];policy=NS(authority=lambda:route.PRIOR_REVIEW)
    prior=(object(),policy,object(),object())
    monkeypatch.setattr(route,'ROOT',Path(__file__).parents[1])
    monkeypatch.setattr(route,'authority',lambda:events.append('new-approval'))
    from orchestrator import item4_validation_admission as gate
    monkeypatch.setattr(gate,'retained_terminal',gate.retained_terminal)
    old_capture=modal_billing.capture;old_headroom=modal_billing.headroom
    monkeypatch.setattr(modal_billing,'capture',old_capture)
    monkeypatch.setattr(route,'connect_spending',lambda:events.append('original-spending-approval'))
    monkeypatch.setattr(route,'connect_original_call',lambda *args:events.append('original-call-proof-connected'))
    out=route.connect(lambda:prior)
    assert out is prior and out[1] is policy and events==['new-approval','original-spending-approval','original-call-proof-connected']
    assert modal_billing.headroom is old_headroom and modal_billing.capture is not old_capture
    ws,summary,row,calls=workspace();now=NOW.replace(day=9)
    ws.billing.report=lambda **kw: calls.append(('report',kw)) or []
    snap=modal_billing.capture(ws,'moroseui',now=now)
    ranges=[v for k,v in calls if k=='report']
    assert len(ranges)==2 and ranges[0]['end']==ranges[1]['start']
    assert ranges[0]['start']==now.replace(day=1,hour=0,minute=0)
    assert ranges[-1]['end']==now.replace(minute=0)
    assert snap['summary']['billed_cost']=='209.67741935'
    # Actual provider method dynamically selects the connected capture.
    from orchestrator.modal_provider import ModalProvider
    fake=NS(client=NS(hello=lambda:events.append('hello')),
        modal=NS(Workspace=NS(from_context=lambda **kw:ws)),config={'workspace':'moroseui'})
    ws.hydrate=lambda **kw:events.append('hydrate')
    from datetime import datetime,timezone,timedelta
    current=datetime.now(timezone.utc);base=current.replace(day=1,hour=0,minute=0,second=0,microsecond=0)
    summary.start=base;summary.end=(base.replace(day=28)+timedelta(days=4)).replace(day=1)
    assert ModalProvider.billing_snapshot(fake)['workspace']=='moroseui'
    assert events[-2:]==['hello','hydrate']


@pytest.mark.parametrize('which',['prior','new'])
def test_no_reader_replacement_without_both_approvals(monkeypatch,which):
    original=modal_billing.capture
    policy=NS(authority=lambda:'wrong' if which=='prior' else route.PRIOR_REVIEW)
    def reject():raise ValueError('unapproved')
    monkeypatch.setattr(route,'authority',reject)
    with pytest.raises(ValueError):route.connect(lambda:(None,policy,None,None))
    assert modal_billing.capture is original


@pytest.mark.parametrize('action',['activate','run-author','run-review','full'])
def test_no_new_activation_or_model_route(action):
    with pytest.raises(ValueError,match='ACTION'):route.main([action])


def test_installer_preserves_every_other_unit_line():
    old=Path(__file__).with_name('fixtures')/'item4_execution_billing_prior_unit.txt'
    raw=old.read_bytes();new=installer.unit_bytes(raw)
    before=b'/item4-execution-billing-20261009/tools/item4_execution_billing.py advance'
    after=b'/item4-spending-module-20261009/tools/item4_execution_billing.py advance'
    assert new==raw.replace(before,after)
    with pytest.raises(ValueError,match='PRIOR_UNIT_CHANGED'):installer.unit_bytes(raw+b' ')


def test_reviewed_billing_reader_is_byte_exact():
    assert route.sha((Path(__file__).parents[1]/'orchestrator/modal_billing.py').read_bytes())==route.BILLING_SHA


@pytest.mark.parametrize('damage',['none','reject','source','review','change','member','file','unit','import'])
def test_authority_rejects_incomplete_or_changed_installation(tmp_path,monkeypatch,damage):
    import json
    from orchestrator import autonomy_review
    root=tmp_path/'root';record=tmp_path/'record';(record/'review').mkdir(parents=True)
    files={}
    for name in route.FILES:
        p=root/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(('synthetic '+name).encode());files[name]=route.sha(p.read_bytes())
    unit=Path('/etc/systemd/system')/('research-'+route.CHANGE+'.service')
    fixture=tmp_path/'unit';fixture.write_text('Synthetic protected unit')
    install={'source':'a'*40,'review_sha256':'b'*64,'files':dict(files),'units':{str(unit):route.sha(fixture.read_bytes())}}
    result={'verdict':'APPROVE','change_id':route.CHANGE,'source_sha':'a'*40,'report_sha256':'b'*64}
    (record/'review/packet-manifest.json').write_text(json.dumps({'source_sha':'a'*40,'source_files':files}))
    monkeypatch.setattr(route,'ROOT',root);monkeypatch.setattr(route,'RECORD',record)
    monkeypatch.setattr(route,'__file__',str(root/route.FILES[0]));monkeypatch.setattr(route,'BILLING_SHA',files[route.FILES[2]])
    monkeypatch.setattr(route,'trusted',lambda path:fixture if Path(path)==unit else Path(path))
    monkeypatch.setattr(autonomy_review,'verify_result',lambda path:result)
    if damage=='reject':result['verdict']='REJECT'
    elif damage=='source':install['source']='c'*40
    elif damage=='review':install['review_sha256']='c'*64
    elif damage=='change':result['change_id']='other'
    elif damage=='member':install['files'].pop(route.FILES[2])
    elif damage=='file':(root/route.FILES[2]).write_text('changed')
    elif damage=='unit':fixture.write_text('changed')
    elif damage=='import':monkeypatch.setattr(route,'__file__',str(root/'foreign'))
    (record/'installed.json').write_text(json.dumps(install))
    if damage=='none':assert route.authority()==result
    else:
        with pytest.raises(ValueError):route.authority()


@pytest.mark.parametrize('damage',['revise','source','reader','installer','runtime'])
def test_installer_fails_before_writes_for_unapproved_or_changed_source(tmp_path,monkeypatch,damage):
    import json
    from orchestrator import autonomy_review
    source=tmp_path/'source';review=tmp_path/'review';review.mkdir();files={}
    for name in route.FILES:
        p=source/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes((Path(__file__).parents[1]/name).read_bytes());files[name]=route.sha(p.read_bytes())
    result={'verdict':'APPROVE','change_id':route.CHANGE,'source_sha':'a'*40,'report_sha256':'b'*64}
    (review/'packet-manifest.json').write_text(json.dumps({'source_sha':'a'*40,'source_files':files}))
    monkeypatch.setattr(installer.os,'geteuid',lambda:0)
    monkeypatch.setattr(installer,'ROOT',tmp_path/'absent-root');monkeypatch.setattr(installer,'RECORD',tmp_path/'absent-record');monkeypatch.setattr(installer,'UNIT',tmp_path/'absent-unit')
    monkeypatch.setattr(installer,'trusted',lambda path:Path(path));monkeypatch.setattr(autonomy_review,'verify_result',lambda path:result)
    if damage=='revise':result['verdict']='REVISE'
    elif damage=='source':result['source_sha']='c'*40
    else:
        name=route.FILES[{'reader':2,'installer':1,'runtime':0}[damage]]
        p=source/name;p.write_bytes(p.read_bytes()+b'changed')
    with pytest.raises(ValueError):installer.install(source,review)
    assert not installer.ROOT.exists() and not installer.RECORD.exists() and not installer.UNIT.exists()


@pytest.mark.parametrize('damage',['none','source-bytes','source-review','review-hash'])
def test_original_spending_source_and_approval_required(tmp_path,monkeypatch,damage):
    import orchestrator
    p=tmp_path/'original_spending.py';p.write_bytes(b'labelled synthetic external source')
    monkeypatch.setattr(route,'SPENDING',p);monkeypatch.setattr(route,'SPENDING_SHA',route.sha(p.read_bytes()))
    monkeypatch.setattr(route,'trusted',lambda path:Path(path))
    proof={'source':route.SPENDING_SOURCE,'review_sha256':route.SPENDING_REVIEW}
    calls=[];fake=NS(implementation=lambda:calls.append('qualified') or proof)
    monkeypatch.setattr(route,'module',lambda name,path:calls.append((name,path)) or fake)
    monkeypatch.setattr(orchestrator,'spending_continuation',None,raising=False)
    if damage=='source-bytes':p.write_bytes(b'changed')
    elif damage=='source-review':proof['source']='f'*40
    elif damage=='review-hash':proof['review_sha256']='f'*64
    if damage=='none':
        assert route.connect_spending() is fake and orchestrator.spending_continuation is fake
        assert calls==[('orchestrator.spending_continuation',p),'qualified']
    else:
        with pytest.raises(ValueError):route.connect_spending()
        assert orchestrator.spending_continuation is None
        if damage=='source-bytes':assert not calls


@pytest.mark.parametrize('state,pid,group,allowed',[
    ('failed','0','',True),('inactive','0','',True),('activating','0','',False),
    ('active','0','',False),('failed','42','',False),('failed','0','/live',False)])
def test_successor_requires_positive_terminal_prior_before_first_write(tmp_path,monkeypatch,state,pid,group,allowed):
    import json
    from orchestrator import autonomy_review
    source=tmp_path/'source';review=tmp_path/'review';review.mkdir();files={}
    for name in route.FILES:
        p=source/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes((Path(__file__).parents[1]/name).read_bytes());files[name]=route.sha(p.read_bytes())
    result={'verdict':'APPROVE','change_id':route.CHANGE,'source_sha':'a'*40,'report_sha256':'b'*64}
    (review/'packet-manifest.json').write_text(json.dumps({'source_sha':'a'*40,'source_files':files}))
    monkeypatch.setattr(installer.os,'geteuid',lambda:0)
    for key in ['ROOT','RECORD','UNIT']:monkeypatch.setattr(installer,key,tmp_path/('absent-'+key))
    prior=tmp_path/'prior-unit';prior.write_bytes((Path(__file__).with_name('fixtures')/'item4_execution_billing_prior_unit.txt').read_bytes())
    monkeypatch.setattr(installer,'PRIOR_UNIT',prior)
    monkeypatch.setattr(installer,'trusted',lambda path:Path(path));monkeypatch.setattr(autonomy_review,'verify_result',lambda path:result)
    monkeypatch.setattr(installer.subprocess,'check_output',lambda *a,**kw:f'MainPID={pid}\nControlGroup={group}\nActiveState={state}\n')
    writes=[]
    def stop(path,raw):writes.append(path);raise RuntimeError('FIRST_WRITE_BOUNDARY')
    monkeypatch.setattr(installer,'put',stop)
    if allowed:
        with pytest.raises(RuntimeError,match='FIRST_WRITE_BOUNDARY'):installer.install(source,review)
        assert writes==[installer.RECORD/'INSTALL_INTENT.json']
    else:
        with pytest.raises(ValueError,match='PRIOR_ACTIVE'):installer.install(source,review)
        assert not writes


@pytest.mark.parametrize('damage',['none','proof','call','ledger','other-run'])
def test_only_exact_existing_terminal_call_proof_is_connected(tmp_path,monkeypatch,damage):
    import sqlite3,json
    from orchestrator import private_records as pr
    lane=tmp_path/'lane';pr.mkdir(lane);pr.write_bytes(lane/'lane.json',b'{}')
    db=sqlite3.connect(lane/'jobs.sqlite');db.execute('CREATE TABLE original(value TEXT)');db.execute("INSERT INTO original VALUES('preserved')");db.commit();db.close();(lane/'jobs.sqlite').chmod(0o600)
    calls=[]
    def originals(driver,*original):
        calls.append('qualified')
        with pytest.raises(sqlite3.OperationalError):driver.store.db.execute("UPDATE original SET value='must refuse'")
        assert driver.store.db.execute('SELECT value FROM original').fetchone()[0]=='preserved'
        if damage=='proof':raise ValueError('original proof changed')
    c=NS(RUN='synthetic-run',LANE=lane,originals=originals)
    known='49cc364b033bf52198fbc44c5470bb72b9cfec03826294f71f2dd2286d244524'
    original=(None,None,None,NS(CALL='wrong' if damage=='call' else known))
    spending=NS(closed_ids=lambda batch,run:{'existing-qualified'})
    batch=NS(filesystem_root=Path('/'),folder=Path('/wrong' if damage=='ledger' else '/var/lib/research-system-autonomy/reviews'))
    route.connect_original_call(spending,c,original)
    if damage=='other-run':
        assert spending.closed_ids(batch,'other')=={'existing-qualified'} and not calls
    elif damage=='none':
        assert spending.closed_ids(batch,c.RUN)=={'existing-qualified',known} and calls==['qualified']
    else:
        with pytest.raises(ValueError):spending.closed_ids(batch,c.RUN)
