"""Independent approval and exact held-unit boundary for the fixed fresh start."""
from pathlib import Path
import pytest
from tools import item4_checkpoint_runtime as route,install_item4_checkpoint as installer

def test_installer_preserves_every_other_unit_line():
    old=Path(__file__).with_name('fixtures')/'item4_benchmark_timer_prior_unit_PRIVATE.txt'
    raw=old.read_bytes();new=installer.unit_bytes(raw)
    before=b'/item4-benchmark-handoff-20261009/tools/item4_checkpoint_runtime.py advance'
    after=b'/item4-benchmark-timer-format-20261009/tools/item4_checkpoint_runtime.py advance'
    assert new==raw.replace(before,after)
    with pytest.raises(ValueError,match='PRIOR_UNIT_CHANGED'):installer.unit_bytes(raw+b' ')

@pytest.mark.parametrize('damage',['none','reject','source','review','change','member','file','unit','retention','import'])
def test_authority_rejects_incomplete_or_changed_installation(tmp_path,monkeypatch,damage):
    import json
    from orchestrator import autonomy_review
    root=tmp_path/'root';record=tmp_path/'record';(record/'review').mkdir(parents=True)
    files={}
    for name in route.FILES:
        p=root/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(('synthetic '+name).encode());files[name]=route.sha(p.read_bytes())
    unit=Path('/etc/systemd/system')/('research-'+route.CHANGE+'.service')
    fixture=tmp_path/'unit';fixture.write_text('Synthetic protected unit')
    units=[unit,unit.with_name('research-'+route.CHANGE+'-retention.service'),unit.with_name('research-'+route.CHANGE+'-retention.timer')]
    install={'source':'a'*40,'review_sha256':'b'*64,'files':dict(files),'units':{str(x):route.sha(fixture.read_bytes()) for x in units}}
    result={'verdict':'APPROVE','change_id':route.CHANGE,'source_sha':'a'*40,'report_sha256':'b'*64}
    (record/'review/packet-manifest.json').write_text(json.dumps({'source_sha':'a'*40,'source_files':files}))
    monkeypatch.setattr(route,'ROOT',root);monkeypatch.setattr(route,'RECORD',record)
    monkeypatch.setattr(route,'__file__',str(root/route.FILES[0]))
    monkeypatch.setattr(route,'trusted',lambda path:fixture if Path(path) in units else Path(path))
    monkeypatch.setattr(autonomy_review,'verify_result',lambda path:result)
    if damage=='reject':result['verdict']='REJECT'
    elif damage=='source':install['source']='c'*40
    elif damage=='review':install['review_sha256']='c'*64
    elif damage=='change':result['change_id']='other'
    elif damage=='member':install['files'].pop(route.FILES[2])
    elif damage=='file':(root/route.FILES[2]).write_text('changed')
    elif damage=='unit':fixture.write_text('changed')
    elif damage=='retention':install['units'].pop(str(units[2]))
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
    result={'verdict':'APPROVE','change_id':route.CHANGE,'source_sha':'a'*40,'report_sha256':'b'*64}
    (review/'packet-manifest.json').write_text(json.dumps({'source_sha':'a'*40,'source_files':files}))
    monkeypatch.setattr(installer.os,'geteuid',lambda:0)
    for key in ['ROOT','RECORD','UNIT']:monkeypatch.setattr(installer,key,tmp_path/('absent-'+key))
    prior=tmp_path/'prior-unit';prior.write_bytes((Path(__file__).with_name('fixtures')/'item4_benchmark_timer_prior_unit_PRIVATE.txt').read_bytes())
    monkeypatch.setattr(installer,'PRIOR_UNIT',prior)
    monkeypatch.setattr(installer,'trusted',lambda path:Path(path));monkeypatch.setattr(autonomy_review,'verify_result',lambda path:result)
    monkeypatch.setattr(installer.subprocess,'check_output',lambda *a,**kw:f'MainPID={pid}\nControlGroup={group}\nActiveState={state}\n')
    monkeypatch.setattr(installer,'verify_units',lambda units:None) # Native parser tested separately.
    monkeypatch.setattr(installer,'read_inputs',lambda raw: {'preprocessing.json':b'Synthetic metadata only'})
    writes=[]
    def stop(path,raw):writes.append(path);raise RuntimeError('FIRST_WRITE_BOUNDARY')
    monkeypatch.setattr(installer,'put',stop)
    if allowed:
        with pytest.raises(RuntimeError,match='FIRST_WRITE_BOUNDARY'):installer.install(source,review)
        assert writes==[installer.RECORD/'INSTALL_INTENT.json']
    else:
        with pytest.raises(ValueError,match='PRIOR_ACTIVE'):installer.install(source,review)
        assert not writes




@pytest.mark.parametrize('damage',['none','owner-export','contract','fit-name','existing'])
def test_root_runtime_publication_freezes_only_expected_owner_export(tmp_path,monkeypatch,damage):
    import json
    from types import SimpleNamespace
    from orchestrator.modal_executor import canonical
    root=tmp_path/'installed';record=tmp_path/'record'
    (root/'docs').mkdir(parents=True);record.mkdir()
    policy={'fits':[{'fit_id':'benchmark-'+g} for g in ('A100-80GB','H100','B200')]}
    raw=canonical(policy);(root/'docs/ITEM4_BENCHMARK_HANDOFF_PRIVATE.json').write_bytes(raw)
    proposal={'schema':'item4-benchmark-runtime-proposal/v1','contract_sha256':route.sha(raw),
              'provider_calls':0,'ready_sha256':'a'*64,
              'rows':[{'fit':f['fit_id'],'runtime':{'synthetic':f['fit_id']},
                       'binding':{'synthetic':f['fit_id']}} for f in policy['fits']]}
    if damage=='contract':proposal['contract_sha256']='f'*64
    if damage=='fit-name':proposal['rows'][0]['fit']='foreign'
    if damage=='existing':(record/'runtimes').mkdir()
    monkeypatch.setattr(route,'ROOT',root);monkeypatch.setattr(route,'RECORD',record)
    monkeypatch.setattr(route.os,'geteuid',lambda:0)
    monkeypatch.setattr(route.os,'chown',lambda *args:None) # Synthetic root ownership boundary.
    monkeypatch.setattr(route,'trusted',lambda p:Path(p))
    monkeypatch.setattr(route,'authority',lambda:{'test_only_approval':True})
    writes=[];commands=[]
    def put(path,raw):
        writes.append(path);path.parent.mkdir(parents=True,exist_ok=True)
        with path.open('xb') as stream:stream.write(raw)
    monkeypatch.setattr(route,'module',lambda *args:SimpleNamespace(put=put))
    import subprocess
    def export(args,**kwargs):
        commands.append(args)
        assert args[-1]=='export-runtimes' and 'runuser'==args[0]
        return SimpleNamespace(returncode=1 if damage=='owner-export' else 0,stdout=canonical(proposal))
    monkeypatch.setattr(subprocess,'run',export)
    if damage=='none':
        result=route.publish_runtimes()
        assert result['provider_calls']==0 and result['scientific_acceptance'] is False
        jobs=json.loads((record/'runtimes/jobs.json').read_bytes())
        assert len(jobs)==3 and len(commands)==1
        for row in jobs:
            assert route.sha(Path(row['runtime']['path']).read_bytes())==row['runtime']['sha256']
        with pytest.raises(ValueError,match='RUNTIMES_EXIST_RECONCILE'):route.publish_runtimes()
    else:
        with pytest.raises(ValueError):route.publish_runtimes()
        assert writes==[]

def test_retention_timer_contains_real_lines_and_exact_cleanup_target():
    raw=(Path(__file__).with_name('fixtures')/'item4_benchmark_timer_prior_unit_PRIVATE.txt').read_bytes()
    rendered=installer.unit_bytes(raw);units=installer.retention_units(rendered)
    timer=next(v for p,v in units.items() if p.suffix=='.timer')
    assert bytes([92,110]) not in timer
    assert timer.splitlines()==[b'[Unit]',b'Description=Private benchmark package retention',
        b'[Timer]',b'OnBootSec=5min',b'OnUnitActiveSec=1h',
        ('Unit=research-'+installer.CHANGE+'-retention.service').encode(),
        b'[Install]',b'WantedBy=timers.target']
    services=[v for p,v in units.items() if p.suffix=='.service']
    assert rendered in services
    cleanup=next(v for v in services if v!=rendered)
    assert cleanup==rendered.replace(b'item4_checkpoint_runtime.py advance',
                                    b'item4_checkpoint_runtime.py cleanup-benchmark-package')


def test_native_parser_refusal_is_a_hard_preinstallation_error(monkeypatch):
    from types import SimpleNamespace
    monkeypatch.setattr(installer.subprocess,'run',lambda *args,**kwargs:
                        SimpleNamespace(returncode=1,stderr='synthetic malformed timer'))
    with pytest.raises(ValueError,match='RENDERED_UNIT_INVALID'):
        installer.verify_units({Path('/synthetic/refused.timer'):b'not a unit'})
