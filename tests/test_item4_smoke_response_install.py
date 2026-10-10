"""Independent approval and exact held-unit boundary for the fixed fresh start."""
from pathlib import Path
import pytest
from tools import item4_smoke_response_runtime as route,install_item4_smoke_response as installer

def prior_unit():
    return (Path(__file__).parents[1]/'docs/ITEM4_SNAPSHOT_PRIOR_UNIT_PRIVATE.txt').read_bytes()

def test_installer_preserves_every_other_unit_line():
    raw=prior_unit();new=installer.unit_bytes(raw)
    before=b'/item4-whole-fixture-author-20261010/tools/item4_smoke_response_runtime.py run'
    after=b'/item4-report-snapshot-author-20261010/tools/item4_smoke_response_runtime.py run'
    assert new==raw.replace(before,after)
    with pytest.raises(ValueError,match='PRIOR_UNIT_CHANGED'):installer.unit_bytes(raw+b' ')

@pytest.mark.parametrize('damage',['none','reject','revise','source','review','change','member','file','unit','extra-unit','import'])
def test_authority_rejects_incomplete_or_changed_installation(tmp_path,monkeypatch,damage):
    import json
    from orchestrator import autonomy_review
    root=tmp_path/'root';record=tmp_path/'record';(record/'review').mkdir(parents=True)
    files={}
    for name in route.FILES:
        p=root/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(('synthetic '+name).encode());files[name]=route.sha(p.read_bytes())
    unit=Path('/etc/systemd/system')/('research-'+route.CHANGE+'.service')
    fixture=tmp_path/'unit';fixture.write_text('Synthetic protected unit')
    units=[unit]
    install={'source':'a'*40,'review_sha256':'b'*64,'files':dict(files),'units':{str(x):route.sha(fixture.read_bytes()) for x in units}}
    result={'verdict':'APPROVE','change_id':route.REVIEW_CHANGE,'source_sha':'a'*40,'report_sha256':'b'*64}
    (record/'review/packet-manifest.json').write_text(json.dumps({'source_sha':'a'*40,'source_files':files}))
    monkeypatch.setattr(route,'ROOT',root);monkeypatch.setattr(route,'RECORD',record)
    monkeypatch.setattr(route,'__file__',str(root/route.FILES[0]))
    monkeypatch.setattr(route,'trusted',lambda path:fixture if Path(path) in units else Path(path))
    def verified(path):return result
    monkeypatch.setattr(autonomy_review,'verify_result',verified)
    if damage=='reject':result['verdict']='REJECT'
    elif damage=='revise':result['verdict']='REVISE'
    elif damage=='source':install['source']='c'*40
    elif damage=='review':install['review_sha256']='c'*64
    elif damage=='change':result['change_id']='other'
    elif damage=='member':install['files'].pop(route.FILES[2])
    elif damage=='file':(root/route.FILES[2]).write_text('changed')
    elif damage=='unit':fixture.write_text('changed')
    elif damage=='extra-unit':install['units']['unexpected']='c'*64
    elif damage=='import':monkeypatch.setattr(route,'__file__',str(root/'foreign'))
    (record/'installed.json').write_text(json.dumps(install))
    if damage=='none':assert route.authority()==result
    else:
        with pytest.raises(ValueError):route.authority()

@pytest.mark.parametrize('state,pid,group,allowed',[
    ('failed','0','',True),('inactive','0','',True),('activating','0','',False),
    ('active','0','',False),('failed','42','',False),('failed','0','/live',False)])
def test_successor_requires_positive_terminal_prior_before_first_write(tmp_path,monkeypatch,state,pid,group,allowed):
    import json
    from orchestrator import autonomy_review
    source=tmp_path/'source';review=tmp_path/'review';review.mkdir();files={}
    for name in route.FILES:
        p=source/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes((Path(__file__).parents[1]/name).read_bytes());files[name]=route.sha(p.read_bytes())
    result={'verdict':'APPROVE','change_id':route.REVIEW_CHANGE,'source_sha':'a'*40,'report_sha256':'b'*64}
    (review/'packet-manifest.json').write_text(json.dumps({'source_sha':'a'*40,'source_files':files}))
    monkeypatch.setattr(installer.os,'geteuid',lambda:0)
    for key in ['ROOT','RECORD','UNIT']:monkeypatch.setattr(installer,key,tmp_path/('absent-'+key))
    prior=tmp_path/'prior-unit';prior.write_bytes(prior_unit())
    monkeypatch.setattr(installer,'PRIOR_UNIT',prior)
    monkeypatch.setattr(installer,'trusted',lambda path:Path(path))
    def verified(path):
        if str(path)=='direction':return {'verdict':'REVISE','change_id':'item4-second-native-failure-direction-20261010','source_sha':'b60badd65283e7df5f801a6a6a20b3fd63504544','report_sha256':'e9636a72940a498855af4d8585e6f549ac87a380e7d0fa634408451a9fe925a3'}
        return result
    monkeypatch.setattr(autonomy_review,'verify_result',verified)
    monkeypatch.setattr(installer.subprocess,'check_output',lambda *a,**kw:f'MainPID={pid}\nControlGroup={group}\nActiveState={state}\n')
    monkeypatch.setattr(installer,'verify_units',lambda units:None) # Native parser tested separately.
    writes=[]
    def stop(path,raw):writes.append(path);raise RuntimeError('FIRST_WRITE_BOUNDARY')
    monkeypatch.setattr(installer,'put',stop)
    if allowed:
        with pytest.raises(RuntimeError,match='FIRST_WRITE_BOUNDARY'):installer.install(source,review,'direction')
        assert writes==[installer.RECORD/'INSTALL_INTENT.json']
    else:
        with pytest.raises(ValueError,match='PRIOR_ACTIVE'):installer.install(source,review,'direction')
        assert not writes




def test_recovery_adds_one_held_unit_and_no_cleanup_timer():
    raw=prior_unit()
    rendered=installer.unit_bytes(raw)
    assert installer.retention_units(rendered)=={installer.UNIT:rendered}
    assert b'cleanup-' not in rendered


def test_native_parser_refusal_is_a_hard_preinstallation_error(monkeypatch):
    from types import SimpleNamespace
    monkeypatch.setattr(installer.subprocess,'run',lambda *args,**kwargs:
                        SimpleNamespace(returncode=1,stderr='synthetic malformed timer'))
    with pytest.raises(ValueError,match='RENDERED_UNIT_INVALID'):
        installer.verify_units({Path('/synthetic/refused.timer'):b'not a unit'})
