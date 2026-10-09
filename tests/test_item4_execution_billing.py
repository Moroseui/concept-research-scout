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
    old_capture=modal_billing.capture;old_headroom=modal_billing.headroom
    monkeypatch.setattr(modal_billing,'capture',old_capture)
    out=route.connect(lambda:prior)
    assert out is prior and out[1] is policy and events==['new-approval']
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
    before=b'/item4-partition-delivery-20261009/tools/item4_validation_runtime.py advance'
    after=b'/item4-execution-billing-20261009/tools/item4_execution_billing.py advance'
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
