"""Private captured rows; synthetic review/installation, no model or authority.
Only root provenance is simulated. Real validators, promotion and continuation.
"""
import json,os,shutil,sqlite3,subprocess
from pathlib import Path
import pytest
from orchestrator import stocktake_navigation as nav, stocktake_recovery as rec
from orchestrator import stocktake_manual_review as manual, autonomy_review as review
from orchestrator.manual_executor import digest,read
from orchestrator.analysis_driver import AnalysisDriver
from tools import manual_promotion as promotion,deploy_manual_lane as deploy
from stocktake_migration_fixture import write,git,matrix

@pytest.fixture
def captured(tmp_path,monkeypatch):
    path=os.environ.get('STOCKTAKE_NAVIGATION_EVIDENCE')
    if not path:pytest.skip('Operator-private captured checkpoint required')
    host=tmp_path/'host';shutil.copytree(path,host)
    for p in [host,*host.rglob('*')]:p.chmod(0o700 if p.is_dir() else 0o600)
    monkeypatch.setattr(manual,'trusted',lambda p:Path(p)) # root provenance ONLY
    return host


def test_private_captured_checkpoint_and_drift(captured):
    old=deploy.bound(captured,nav.OLD)
    assert nav.prior(old,captured)[0]['source']==nav.SOURCE
    with sqlite3.connect(old/'jobs.sqlite') as db:db.execute("UPDATE manual_calls SET status='COMPLETE' WHERE id=?",(rec.FAILED,))
    with pytest.raises(ValueError,match='NAVIGATION_PRIOR_CALL_CHANGED'):nav.prior(old,captured)


def setup_release(host,tmp_path):
    source=Path(__file__).resolve().parents[1];checkout=tmp_path/'source'
    shutil.copytree(source,checkout,ignore=shutil.ignore_patterns('.git','__pycache__','.pytest_cache'))
    for p in [checkout,*checkout.rglob('*')]:p.chmod(0o700 if p.is_dir() else 0o600)
    git(checkout,'init','-q');git(checkout,'add','.')
    git(checkout,'-c','user.name=Scratch','-c','user.email=scratch@invalid','commit','-qm','Synthetic candidate copy')
    tag='research-manual-sprint10-navigation-scratch';head=git(checkout,'rev-parse','HEAD')
    git(checkout,'-c','user.name=Scratch','-c','user.email=scratch@invalid','tag','-am','Synthetic only',tag)
    unit='research-scratch-old.service';oldroot=host/'var/lib/research-system';write(oldroot/'pause.json',{'paused':True})
    with sqlite3.connect(oldroot/'jobs.sqlite') as db:db.execute('CREATE TABLE jobs(id,status)')
    write(oldroot/'receipts/one.json',{'synthetic':True});write(oldroot/'log.txt',b'log\n');write(oldroot/'snapshot.json',{'status':'PASS'})
    definition=host/'etc/systemd/system'/unit;write(definition,b'synthetic\n')
    write(host/'run/manual-deploy-test-units.json',{'units':{unit:{'enabled':False,'active':False}},'calls':[]})
    oldfile=tmp_path/'old.json';write(oldfile,{'units':[{'name':unit,'enabled':False,'active':False,'definition_sha256':digest(definition.read_bytes())}],
        'pause_files':['/var/lib/research-system/pause.json'],'databases':['/var/lib/research-system/jobs.sqlite'],
        'receipt_directories':['/var/lib/research-system/receipts'],'logs':['/var/lib/research-system/log.txt'],
        'snapshot_verification':{'path':'/var/lib/research-system/snapshot.json','sha256':digest((oldroot/'snapshot.json').read_bytes())}})
    layout=promotion.layout(Path(nav.OLD).parent.name)
    file=deploy.bound(host,layout['release']+'/SYNTHETIC.txt');write(file,b'Synthetic installation carrier only')
    runtime=deploy.bound(host,layout['config']+'/runtime.json');write(runtime,(source/'deploy/manual-lane/runtime.promotion.json').read_bytes())
    files={layout['release']+'/SYNTHETIC.txt':{'sha256':digest(file.read_bytes()),'mode':0o600}}
    hp=deploy.bound(host,layout['record']+'/FILES.json');write(hp,files)
    previous={'source':nav.SOURCE,'release':layout['release'],'state':layout['state'],'units':layout['units'],
        'hash_list':layout['record']+'/FILES.json','hash_list_sha256':digest(hp.read_bytes()),'runtime':layout['config']+'/runtime.json','runtime_sha256':rec.RUNTIME}
    prev=tmp_path/'previous.json';write(prev,previous);write(deploy.bound(host,promotion.POINTER),previous)
    manifest={'change_id':manual.NAVIGATION,'source_sha':head,'runtime_sha256':rec.RUNTIME,'round':1,'predecessor':None,'files':{'evidence/analysis-plan.json':rec.PLAN}}
    packet=digest(review.canonical(manifest));folder=deploy.bound(host,str(manual.ROOT))/packet
    report=('SYNTHETIC REVIEW ONLY\nsource_sha: '+head+'\nruntime_sha256: '+rec.RUNTIME+'\npacket_sha256: '+packet+
        '\nanalysis_entrypoint: orchestrator.analysis_driver\nreviewer_product: Claude Code\nreviewer_model: synthetic\nreviewer_session_id: synthetic\n## Verdict: APPROVE\n\n## Blockers\nNone.\n')
    write(folder/'packet-manifest.json',manifest);write(folder/'report.md',report.encode())
    write(folder/'operator-return-original.txt',b'Synthetic');write(folder/'evidence-files.json',{'operator-return-original.txt':digest(b'Synthetic')})
    value=manual.inputs(folder,filesystem_root=host);receipt={'review':value,'accounting_units':1,'synthetic':True};write(folder/'qualification.json',receipt)
    ledger=deploy.bound(host,'/var/lib/research-system-autonomy/reviews')
    with sqlite3.connect(ledger/'jobs.sqlite') as db:db.execute('INSERT INTO autonomy_calls VALUES(?,?,?,?,?,?,?,?)',('manual-stocktake-'+packet,'implementation_review',manual.NAVIGATION,1,'2026-01-01','COMPLETE','{}',review.canonical(receipt).decode()))
    return {'host':host,'checkout':checkout,'head':head,'folder':folder,'ledger':ledger,'runtime':runtime,
        'args':(host,checkout,tag,head,git(checkout,'rev-parse',tag),folder/'report.md',digest(report.encode()),prev,oldfile)}


def test_real_promotion_continuation_preserves_three_calls(captured,tmp_path,monkeypatch):
    f=setup_release(captured,tmp_path);old=deploy.bound(captured,nav.OLD);before=rec.state_snapshot(old)
    installed=promotion.promote(*f['args'],entrypoint='analysis',stocktake_navigation=True)
    root=deploy.bound(captured,installed['layout']['state'])/'repository';state=root.parent/'lane'
    proof=matrix(f,root);monkeypatch.setenv('RESEARCH_MANUAL_RUNTIME_CONFIG',str(f['runtime']))
    value=nav.continue_run(state,root,f['folder']/'report.md',proof,filesystem_root=captured)
    assert value['calls_used']==3 and value['call_limit']==8 and value['phase']=='COMMIT_SPEC'
    assert rec.state_snapshot(old)==before
    with rec.connect(state/'jobs.sqlite') as db:
        assert len(rec.rows(db,'manual_calls'))==3
        nav.unchanged_rows(db,'manual_calls',nav.checkpoint()['local_calls'])
        assert rec.sha(rec.rows(db,'manual_account'))==nav.checkpoint()['account_sha256']
        assert rec.sha(rec.rows(db,'manual_state'))==nav.checkpoint()['state_sha256']
        assert len(rec.rows(db,'manual_recoveries'))==2
    d=AnalysisDriver(state);rec.validate_runtime(d)
    assert rec.global_exception(d.store.batch,rec.RUN)==rec.FAILED
    assert 'EVERY numeric claim' in d.task('result_interpretation_author',{})
    with pytest.raises(ValueError,match='NAVIGATION_EXISTING_DESTINATION_RECONCILE'):
        nav.continue_run(state,root,f['folder']/'report.md',proof,filesystem_root=captured)
    # No reservation or new charge occurred.
    assert d.store.batch.db.execute('SELECT COUNT(*) FROM autonomy_calls WHERE id IN (?,?,?)',tuple(nav.checkpoint()['global_calls'])).fetchone()[0]==3


@pytest.mark.parametrize('damage',['no_entrypoint','rejected','changed_report'])
def test_navigation_approval_required_before_promotion_write(captured,tmp_path,damage):
    f=setup_release(captured,tmp_path);p=f['folder']/'report.md';raw=p.read_text()
    if damage=='no_entrypoint':raw=raw.replace('analysis_entrypoint: orchestrator.analysis_driver\n','')
    elif damage=='rejected':raw=raw.replace('## Verdict: APPROVE','## Verdict: CHANGES REQUIRED')
    else:raw+='\nchanged\n'
    p.write_text(raw);args=list(f['args']);args[6]=digest(p.read_bytes())
    with pytest.raises(ValueError):promotion.promote(*args,entrypoint='analysis',stocktake_navigation=True)
    assert not deploy.bound(captured,promotion.layout(args[2])['record']).exists()
