"""Genuine private captured data; synthetic approval/installation, clearly labelled.
Only root provenance is simulated locally. Production validators and DB opens run.
"""
import json,os,shutil,sqlite3
from pathlib import Path
import pytest
from orchestrator import stocktake_review_recovery as recovery,stocktake_recovery as rec,autonomy_review as review
from orchestrator import manual_host_guard
from orchestrator.manual_executor import read,digest
from orchestrator.analysis_driver import AnalysisDriver
from tools import deploy_manual_lane as deploy,manual_promotion as promotion
from stocktake_migration_fixture import write,git,matrix

@pytest.fixture
def captured(tmp_path,monkeypatch):
    source=os.environ.get('STOCKTAKE_REVIEW_EVIDENCE')
    if not source:pytest.skip('Private five-call captured checkpoint required')
    host=tmp_path/'host';shutil.copytree(source,host)
    for p in [host,*host.rglob('*')]:p.chmod(0o700 if p.is_dir() else 0o600)
    monkeypatch.setattr(manual_host_guard,'trusted',lambda p:Path(p)) # ROOT PROVENANCE SIMULATED ONLY
    return host

def setup_release(host,tmp_path):
    source=Path(__file__).resolve().parents[1];checkout=tmp_path/'source'
    shutil.copytree(source,checkout,ignore=shutil.ignore_patterns('.git','__pycache__','.pytest_cache'))
    for p in [checkout,*checkout.rglob('*')]:p.chmod(0o700 if p.is_dir() else 0o600)
    git(checkout,'init','-q');git(checkout,'add','.')
    git(checkout,'-c','user.name=Scratch','-c','user.email=scratch@invalid','commit','-qm','Synthetic candidate copy')
    tag='research-manual-sprint10-review-continuation-scratch';head=git(checkout,'rev-parse','HEAD')
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
    layout=promotion.layout(Path(recovery.OLD).parent.name)
    file=deploy.bound(host,layout['release']+'/SYNTHETIC.txt');write(file,b'Synthetic installation carrier only')
    runtime=deploy.bound(host,layout['config']+'/runtime.json');write(runtime,(source/'deploy/manual-lane/runtime.promotion.json').read_bytes())
    files={layout['release']+'/SYNTHETIC.txt':{'sha256':digest(file.read_bytes()),'mode':0o600}}
    hp=deploy.bound(host,layout['record']+'/FILES.json');write(hp,files)
    previous={'source':recovery.BASE,'release':layout['release'],'state':layout['state'],'units':layout['units'],
        'hash_list':layout['record']+'/FILES.json','hash_list_sha256':digest(hp.read_bytes()),'runtime':layout['config']+'/runtime.json','runtime_sha256':rec.RUNTIME}
    prev=tmp_path/'previous.json';write(prev,previous);write(deploy.bound(host,promotion.POINTER),previous)
    manifest={'change_id':'synthetic-review-continuation','source_sha':head,'runtime_sha256':rec.RUNTIME,
        'round':1,'source_files':{'worker.py':digest(b'SYNTHETIC')},'files':{'evidence/analysis-plan.json':rec.PLAN}}
    packet=digest(review.canonical(manifest));folder=host/'synthetic-automated-review'/packet
    from test_autonomy_review import native
    events=native(manifest)
    line='analysis_entrypoint: orchestrator.analysis_driver\n'
    for event in [events[-1],events[-2]['message']['content'][0]]:
        key='result' if 'result' in event else 'text';event[key]=line+event[key]
    report=events[-1]['result'];raw='\n'.join(json.dumps(x) for x in events).encode()
    result=review.extract_result(raw.decode(),manifest,0)
    receipt={k:manifest[k] for k in ['source_sha','runtime_sha256','change_id','round']}
    receipt.update(exit_code=0,verdict=result['verdict'],report_sha256=digest(report.encode()),native_stream_sha256=digest(raw),synthetic=True)
    for name,value in [('packet-manifest.json',manifest),('report.md',report.encode()),('native-stream.jsonl',raw),('receipt.json',receipt)]:write(folder/name,value)
    assert review.verify_result(folder)==receipt
    ledger=deploy.bound(host,'/var/lib/research-system-autonomy/reviews')
    return {'host':host,'checkout':checkout,'head':head,'folder':folder,'ledger':ledger,'runtime':runtime,
        'args':(host,checkout,tag,head,git(checkout,'rev-parse',tag),folder/'report.md',digest(report.encode()),prev,oldfile)}


def test_private_five_call_checkpoint_and_drift(captured):
    assert recovery.prior(captured)['source']==recovery.BASE
    old=deploy.bound(captured,recovery.OLD)
    with sqlite3.connect(old/'jobs.sqlite') as db:db.execute("UPDATE manual_calls SET status='COMPLETE' WHERE id=?",(recovery.FAILED,))
    with pytest.raises(ValueError,match='ORIGINAL_ROW_CHANGED'):recovery.prior(captured)


def test_real_promote_continue_preserves_five_calls(captured,tmp_path,monkeypatch):
    f=setup_release(captured,tmp_path);old=deploy.bound(captured,recovery.OLD);before=rec.state_snapshot(old)
    installed=promotion.promote(*f['args'],entrypoint='analysis',stocktake_review_continuation=True)
    root=deploy.bound(captured,installed['layout']['state'])/'repository';state=root.parent/'lane'
    proof=matrix(f,root);monkeypatch.setenv('RESEARCH_MANUAL_RUNTIME_CONFIG',str(f['runtime']))
    value=recovery.continue_run(state,root,f['folder']/'report.md',proof,filesystem_root=captured)
    assert value['calls_used']==5 and value['call_limit']==8
    assert rec.state_snapshot(old)==before
    with rec.connect(state/'jobs.sqlite') as db:
        recovery.unchanged(db,'manual_calls',recovery.checkpoint()['local_calls'])
        assert len(rec.rows(db,'manual_calls'))==5
        assert rec.sha(rec.rows(db,'manual_account'))==recovery.checkpoint()['account_sha256']
        assert len(rec.rows(db,'manual_recoveries'))==3
    d=AnalysisDriver(state);rec.validate_runtime(d)
    assert recovery.permit(d.store,recovery.RUN)['preserved_failures']==[rec.FAILED,recovery.FAILED]
    assert d.current()['phase']==recovery.STAGE
    recovery.validate_next_call(d.store,recovery.STAGE,2)
    with pytest.raises(ValueError,match='EXISTING_DESTINATION'):
        recovery.continue_run(state,root,f['folder']/'report.md',proof,filesystem_root=captured)
    assert d.store.batch.db.execute('SELECT count(*) FROM autonomy_calls WHERE change_id=?',(recovery.RUN,)).fetchone()[0]==5
    # Only external connectivity is synthetic; real local/global admission and
    # accounting run on copies, with no model client or live ledger access.
    from orchestrator import connectivity
    monkeypatch.setattr(connectivity,'require',lambda *a,**k:{'synthetic':'network not contacted'})
    before_global=[tuple(r) for r in d.store.batch.db.execute('SELECT * FROM autonomy_calls')]
    ident,attempt,receipt=d.store.reserve_call(recovery.RUN,recovery.STAGE,f['head'],d.config['branch'],d.config['policy'],{'input_sha256':digest(b'SYNTHETIC'),'workspace':str(tmp_path/'synthetic-call')})
    assert (ident,attempt)==(recovery.REPLACEMENT,2)
    assert receipt['linked_recovery_of']==recovery.FAILED
    recovery.unchanged(d.store.db,'manual_calls',recovery.checkpoint()['local_calls'])
    after_global=[tuple(r) for r in d.store.batch.db.execute('SELECT * FROM autonomy_calls')]
    assert len(after_global)==len(before_global)+1 and all(r in after_global for r in before_global)
    with pytest.raises(ValueError):d.store.reserve_call(recovery.RUN,recovery.STAGE,f['head'],d.config['branch'],d.config['policy'],{})
    assert d.store.db.execute('SELECT count(*) FROM manual_calls').fetchone()[0]==6

@pytest.mark.parametrize('damage',['no_entrypoint','rejected','changed_report'])
def test_automated_approval_required_before_promotion(captured,tmp_path,damage):
    f=setup_release(captured,tmp_path);p=f['folder']/'report.md';raw=p.read_text()
    if damage=='no_entrypoint':raw=raw.replace('analysis_entrypoint: orchestrator.analysis_driver\n','')
    elif damage=='rejected':raw=raw.replace('## Verdict: APPROVE','## Verdict: CHANGES REQUIRED')
    else:raw+='\nchanged\n'
    p.write_text(raw);args=list(f['args']);args[6]=digest(p.read_bytes())
    with pytest.raises(ValueError):promotion.promote(*args,entrypoint='analysis',stocktake_review_continuation=True)
    assert not deploy.bound(captured,promotion.layout(args[2])['record']).exists()
