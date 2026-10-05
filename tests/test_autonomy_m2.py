"""M2 deterministic accounting, binding and executor recovery tests. No model calls."""
import json
from datetime import datetime,timezone
from pathlib import Path
import pytest
from orchestrator import cpu_package,manual_package,manual_driver,connectivity
from orchestrator.autonomy_accounting import BatchAccounts
from orchestrator.manual_executor import ManualExecutor,digest,inventory
from orchestrator.cpu_executor import CPUExecutor
from test_manual_lane import policy,lane
from test_context_budget import root
REAL_NETWORK_PROBE=connectivity.probe
ROOT=Path(__file__).resolve().parents[1]


def test_cpu_adapter_preserves_all_scientific_cells_and_truthful_membership():
    original=json.loads((ROOT/cpu_package.BASE/'isles24_sprint10_r2_exclusion_reference.ipynb').read_text())
    raw=cpu_package.notebook_bytes(ROOT,'synthetic-cpu-run');new=json.loads(raw)
    for i in range(3,len(original['cells'])):assert original['cells'][i]['source']==new['cells'][i+1]['source']
    texts=manual_package.code_cells(raw)
    for text in texts:compile(text,'emitted-cell','exec')
    assert 'drive.mount' not in '\n'.join(texts) and 'git fetch' not in '\n'.join(texts)
    assert '"count": 0' in texts[0] and 'sprint10-m2-cpu-adapter-v1' in texts[0]
    assert 'assert len(CASES) == 99' in texts[2]
    assert cpu_package.TOLERANCE['tables']=='byte-identical'


def test_shared_accounting_daily_includes_reviews_and_run_budget(tmp_path):
    q=BatchAccounts(tmp_path/'global');q.register_run('r',{'authority':'synthetic'})
    s=ManualExecutor(tmp_path/'local.sqlite',batch=q);p=policy();s.initialize_allowance(p)
    q.reserve({'change_id':'synthetic-review','round':1},{})
    first=q.db.execute('SELECT id FROM autonomy_calls').fetchone()[0];q.finish(first,'COMPLETE',{'synthetic':True})
    for stage in list(manual_driver.STAGES)*2:
        ident,n,receipt=s.reserve_call('r',stage,'a'*40,'astra/manual-test',p,{'synthetic':True})
        s.finish_call(ident,receipt,'COMPLETE')
    assert q.db.execute('SELECT count(*) FROM autonomy_calls').fetchone()[0]==9
    assert q.db.execute("SELECT count(*) FROM autonomy_calls WHERE kind='scientific'").fetchone()[0]==8
    with pytest.raises(ValueError,match='CALL_LIMIT'):s.reserve_call('r',manual_driver.STAGES[0],'a'*40,'astra/manual-test',p,{})
    assert q.db.execute('SELECT count(*) FROM autonomy_calls').fetchone()[0]==9


def test_shared_partial_reservation_blocks_and_network_refuses_before_charge(tmp_path,monkeypatch):
    q=BatchAccounts(tmp_path/'global');q.register_run('r',{})
    s=ManualExecutor(tmp_path/'local.sqlite',batch=q);s.initialize_allowance(policy())
    def fail(host):raise TimeoutError('synthetic')
    monkeypatch.setattr(connectivity,'probe',fail)
    with pytest.raises(ValueError,match='NETWORK_PREFLIGHT'):s.reserve_call('r',manual_driver.STAGES[0],'a'*40,'astra/manual-test',policy(),{})
    assert not q.db.execute('SELECT 1 FROM autonomy_calls').fetchone()
    q.reserve_scientific('first','r',manual_driver.STAGES[0],'a'*40,{})
    with pytest.raises(ValueError,match='DUPLICATE'):q.reserve_scientific('first','r',manual_driver.STAGES[0],'a'*40,{})
    with pytest.raises(ValueError,match='UNCERTAIN_OR_RUNNING'):q.reserve_scientific('next','r',manual_driver.STAGES[1],'a'*40,{})
    with pytest.raises(ValueError,match='UNCERTAIN_OR_RUNNING'):q.reserve({'change_id':'next-review','round':1},{})


def test_one_run_and_halt_and_acceptance_idempotence(tmp_path):
    q=BatchAccounts(tmp_path);q.register_run('r',{'scope':'same'});q.register_run('r',{'scope':'same'})
    with pytest.raises(ValueError,match='ONE_ACTIVE'):q.register_run('other',{})
    with pytest.raises(ValueError,match='BINDING_CHANGED'):q.register_run('r',{})
    q.complete_run('r',{'accepted':'sha'});q.complete_run('r',{'accepted':'sha'})
    with pytest.raises(ValueError,match='ACCEPTANCE_CHANGED'):q.complete_run('r',{'accepted':'altered'})
    q.register_run('next',{})
    (tmp_path/'HALT').touch()
    with pytest.raises(ValueError,match='HALTED'):q.reserve_scientific('id','next','run_spec_author','s',{})


@pytest.mark.parametrize('cap',[30,60])
def test_global_daily_and_batch_caps_are_not_reset_by_another_run(tmp_path,cap):
    q=BatchAccounts(tmp_path);q.register_run('new',{})
    today=datetime.now(timezone.utc).date().isoformat()
    for i in range(cap):
        q.db.execute('INSERT INTO autonomy_calls VALUES(?,?,?,?,?,?,?,?)',(str(i),'scientific','old'+str(i),1,today if cap==30 else '2020-01-01','COMPLETE','{}','{}'))
    with pytest.raises(ValueError,match='DAILY_CALL_LIMIT' if cap==30 else 'BATCH_CALL_LIMIT'):q.reserve_scientific('x','new','run_spec_author','s',{})
    assert q.db.execute('SELECT count(*) FROM autonomy_calls').fetchone()[0]==cap


def test_completed_native_receipt_preserved_when_format_provenance_added(tmp_path):
    q=BatchAccounts(tmp_path);q.register_run('r',{});q.reserve_scientific('i','r','result_interpretation_author','s',{})
    original={'outcome':'COMPLETE','output_sha256':{'interpretation.md':'original'}}
    q.finish_scientific('i',original,'COMPLETE')
    derived={**original,'deterministic_format_repair':{'original_sha256':'original','derived_sha256':'new'}}
    q.finish_scientific('i',derived,'COMPLETE');q.finish_scientific('i',derived,'COMPLETE')
    assert json.loads(q.status('i')['receipt'])==original
    assert q.db.execute("SELECT count(*) FROM events WHERE id='i:format-repair'").fetchone()[0]==1
    with pytest.raises(ValueError,match='CHANGED'):q.finish_scientific('i',{**derived,'outcome':'OTHER'},'COMPLETE')


def test_cpu_intent_without_exit_never_reexecutes(tmp_path,monkeypatch):
    config={'synthetic':True};s=CPUExecutor(tmp_path/'jobs.sqlite',config)
    package=tmp_path/'package';package.mkdir();nb={'cells':[{'cell_type':'code','source':['pass']}]};raw=json.dumps(nb).encode()
    (package/'Sprint10.ipynb').write_bytes(raw)
    m={'source':'s','spec_sha256':'p','review_sha256':'r','notebook_code_sha256':manual_package.code_sha(raw),'notebook_code_cells':['pass']}
    (package/'manifest.json').write_text(json.dumps(m))
    binding={k:m[k] for k in ['source','spec_sha256','review_sha256','notebook_code_sha256']};binding['cpu_config_sha256']=digest(json.dumps(config,sort_keys=True).encode())
    s.register('j',binding);s.db.execute('INSERT INTO manual_packages VALUES(?,?)',('j',json.dumps(inventory(package))))
    lease=s.claim('j');s.complete_event('j','acquired','VALIDATED',lease=lease['lease']);s.claim('j')
    with pytest.raises(ValueError,match='UNCERTAIN_DISPATCH_NO_RETRY'):s.execute('j',package,tmp_path/'work')
    assert s.get('j')['status']=='BLOCKED' and not (tmp_path/'work').exists()


def test_modal_get_fix_does_not_accept_503(monkeypatch):
    REAL_PROBE=REAL_NETWORK_PROBE
    methods=[];monkeypatch.setattr(connectivity.subprocess,'run',lambda *a,**k:None)
    class Response:
        status=200
        def __enter__(self):return self
        def __exit__(self,*a):pass
    class Opener:
        def open(self,request,**kwargs):methods.append(request.get_method());return Response()
    monkeypatch.setattr(connectivity.urllib.request,'build_opener',lambda *a:Opener())
    assert REAL_PROBE('api.modal.com')['https_status']==200
    assert REAL_PROBE('api.anthropic.com')['https_status']==200
    assert methods==['GET','HEAD']
    Response.status=503
    with pytest.raises(ValueError,match='HTTP_UNAVAILABLE'):REAL_PROBE('api.modal.com')



def cpu_return_fixture(tmp_path):
    from test_manual_lane import make_return
    from orchestrator import manual_validation as v
    bind=cpu_package.contract(ROOT)
    m={'schema':'cpu-sprint10-acceptance/v1','run_id':'synthetic-cpu','source':'a'*40,'spec_sha256':'b'*64,'notebook_code_sha256':'c'*64,
       'private_files':{'split_manifest.csv':bind['derived_split_sha256'],'excluded_cases.json':bind['derived_exclusions_sha256']},'data_binding':bind}
    folder=tmp_path/'return';make_return(folder,m,None)
    identity=v.expected_identity(m['private_files']);identity.update(code_version='sprint10-m2-cpu-adapter-v1',exclusions_count=0)
    fp=digest(json.dumps(identity,sort_keys=True).encode())[:12]
    for name in ['comparison_reference.json','compatibility_report.json']:
        path=folder/'actual'/name;value=json.loads(path.read_text());value.update(run_identity=identity,fingerprint=fp);path.write_text(json.dumps(value))
    receipt=json.loads((folder/'execution_receipt.json').read_text());receipt.update(tolerance=cpu_package.TOLERANCE,
        actual_output_path='/workspace/comparison/compare-875c56c278-0a60362503-'+fp,actual_sha256=inventory(folder/'actual'))
    (folder/'execution_receipt.json').write_text(json.dumps(receipt))
    return folder,m


def test_cpu_validator_byte_exact_and_json_science_binding(tmp_path):
    from orchestrator.manual_validation import validate_cpu_return
    folder,m=cpu_return_fixture(tmp_path)
    assert validate_cpu_return(folder,m)['status']=='VALID'
    path=folder/'actual/summary_by_recipe.csv';path.write_text(path.read_text().replace('0.5','0.50000000001'))
    receipt=json.loads((folder/'execution_receipt.json').read_text());receipt['actual_sha256']=inventory(folder/'actual');(folder/'execution_receipt.json').write_text(json.dumps(receipt))
    result=validate_cpu_return(folder,m)
    assert result['status']=='INVALID' and any(x['kind']=='byte_difference' for x in result['differences'])
    doc=folder/'actual/comparison_reference.json';j=json.loads(doc.read_text());j['hard_checks']['same']=False;doc.write_text(json.dumps(j))
    receipt['actual_sha256']=inventory(folder/'actual');(folder/'execution_receipt.json').write_text(json.dumps(receipt))
    with pytest.raises(ValueError,match='COMPARISON_STATUS_CHANGED'):validate_cpu_return(folder,m)


@pytest.mark.parametrize('mutation',['membership','source','receipt','extra'])
def test_cpu_validator_refuses_changed_binding_and_unlisted_file(tmp_path,mutation):
    from orchestrator.manual_validation import validate_cpu_return
    folder,m=cpu_return_fixture(tmp_path)
    if mutation=='membership':m['data_binding']={**m['data_binding'],'development_count':100}
    elif mutation=='source':m['source']='d'*40
    elif mutation=='receipt':
        path=folder/'execution_receipt.json';r=json.loads(path.read_text());r['development_count']=100;path.write_text(json.dumps(r))
    else:(folder/'extra.txt').write_text('not declared')
    with pytest.raises(ValueError):validate_cpu_return(folder,m)


def test_cpu_native_isolation_command_has_no_root_network_or_credentials(tmp_path,monkeypatch):
    from orchestrator import cpu_isolation as iso
    package=tmp_path/'package';data=tmp_path/'data';work=tmp_path/'work'
    for p in [package,data,work]:p.mkdir()
    monkeypatch.setattr(iso,'mounts',lambda c:({'/opt/research-system-cpu-tools/test':'/opt/research-system-cpu-tools/test'},Path('/usr/lib/python3.12')))
    argv=iso.command({'environment_root':'/opt/research-system-cpu-tools/test'},package,data,work)
    assert '--unshare-all' in argv and '--clearenv' in argv and '--cap-drop' in argv
    assert str(package) in argv and str(data) in argv and str(work) in argv
    assert '--ro-bind' in argv and '--share-net' not in argv and '/' not in argv
    assert not any('login' in arg or 'TOKEN' in arg for arg in argv[:argv.index('-c')])
    with pytest.raises(ValueError,match='OVERLAP'):iso.command({'environment_root':'x'},package,data,data)


def test_cpu_driver_binds_collection_instead_of_accepting_operator_path(lane):
    # Existing context/authority fixture is synthetic; no model or execution.
    d=manual_driver.Driver(lane,runner=lambda *a:pytest.fail('no model'))
    d.config['backend']='cpu'
    from types import SimpleNamespace
    d.store.batch=SimpleNamespace(folder=lane/'global')
    v=d.current();v.update(phase='WAIT_OUTPUTS');d.save(v)
    result=d.advance(collect_folder='/arbitrary')
    assert result['phase']=='BLOCKED' and 'CPU_COLLECTION_PATH_IS_BOUND' in result['reason']
    assert result['calls_used']==0



def test_cpu_dispatch_intent_precedes_process_and_completed_result_reconciles(tmp_path,monkeypatch):
    from orchestrator import cpu_executor as ex,cpu_isolation,manual_host_guard
    package=tmp_path/'package';prep=tmp_path/'prepared';data=tmp_path/'data';data.mkdir();prep.mkdir()
    cases=['synthetic-'+str(i) for i in range(99)];(data/'development99.manifest.json').write_text(json.dumps({'cases':cases}))
    nb={'cells':[{'cell_type':'code','source':['pass']}]};raw=json.dumps(nb).encode();(prep/'Sprint10.ipynb').write_bytes(raw)
    m={'source':'s','spec_sha256':'p','review_sha256':'r','notebook_code_sha256':manual_package.code_sha(raw),'notebook_code_cells':['pass'],'data_binding':{},
       'private_files':{'split_manifest.csv':digest(cpu_package.split_bytes(cases)),'excluded_cases.json':digest(b'[]\n')}}
    (prep/'manifest.json').write_text(json.dumps(m))
    config={'data_root':str(data)};store=CPUExecutor(tmp_path/'jobs.sqlite',config)
    binding={k:m[k] for k in ['source','spec_sha256','review_sha256','notebook_code_sha256']};binding['cpu_config_sha256']=digest(json.dumps(config,sort_keys=True).encode())
    monkeypatch.setattr(cpu_package,'verify_data',lambda *a: {'status':'SYNTHETIC'})
    monkeypatch.setattr(cpu_isolation,'verify_environment',lambda *a:None)
    monkeypatch.setattr(manual_host_guard,'before_call',lambda *a:None)
    monkeypatch.setattr(cpu_isolation,'command',lambda *a,**k:['synthetic-not-executable'])
    from types import SimpleNamespace
    monkeypatch.setattr(ex.subprocess,'run',lambda *a,**k:SimpleNamespace(returncode=0,stdout='synthetic probe',stderr=''))
    work=tmp_path/'work';calls=[]
    class Process:
        pid=12345
        def __init__(self,*a,**k):
            assert (work/'dispatch-intent.json').is_file()
            assert store.get('j')['status']=='RUNNING' and store.get('j')['phase']=='dispatch'
            calls.append(1);(work/'return').mkdir();(work/'return/result').write_text('synthetic result')
        def wait(self,**k):return 0
    monkeypatch.setattr(ex.subprocess,'Popen',Process)
    assert store.submit('j',binding,prep,package)['status']=='QUEUED_CPU'
    assert store.submit('j',binding,prep,package)['status']=='ALREADY_QUEUED'
    import os
    previous=os.umask(0)
    try:assert store.execute('j',package,work)['status']=='EXECUTED'
    finally:os.umask(previous)
    from orchestrator import private_records
    private_records.check_tree(work)
    assert all(not q.stat().st_mode&0o077 for q in work.rglob('*'))
    assert store.execute('j',package,work)['reconciled']
    assert calls==[1]
    assert store.collect('j',work/'return',tmp_path/'collected',lambda p:{'status':'VALID'})['status']=='VALID'
    assert store.execute('j',package,work)['reconciled'] and calls==[1]
    # Lost final job transition is recovered from the bound exit, never rerun.
    intent=json.loads((work/'dispatch-intent.json').read_text())
    store.db.execute("DELETE FROM events WHERE id='j:cpu-executed'")
    store.db.execute("UPDATE jobs SET status='RUNNING',phase='dispatch',lease=? WHERE id='j'",(intent['lease'],))
    assert store.execute('j',package,work)['reconciled'] and calls==[1]



def test_dependency_discovery_searches_only_pinned_wheel_libraries(tmp_path,monkeypatch):
    from orchestrator import cpu_isolation as iso
    env=tmp_path/'environment';(env/'bin').mkdir(parents=True);(env/'bin/python3').write_text('synthetic')
    libs=env/'lib/python3.12/site-packages/scipy.libs';libs.mkdir(parents=True);(libs/'leaf.so').write_text('synthetic')
    monkeypatch.setattr(iso,'verify_environment',lambda c:env)
    monkeypatch.setattr(iso.subprocess,'check_output',lambda *a,**k:json.dumps({'stdlib':'/usr/lib/python3.12','platstdlib':'/usr/lib/python3.12'}))
    from types import SimpleNamespace
    checks=[]
    def ldd(*a,**kw):
        checks.append(kw['env'])
        assert kw['env']['LD_LIBRARY_PATH']==str(libs)
        return SimpleNamespace(returncode=0,stdout='',stderr='')
    monkeypatch.setattr(iso.subprocess,'run',ldd)
    mapping,_=iso.mounts({})
    assert mapping=={str(env):str(env),'/usr/lib/python3.12':'/usr/lib/python3.12'} and checks



def test_actual_cpu_initializer_selects_current_configuration_and_exact_metric(tmp_path,monkeypatch):
    import shutil,subprocess
    from orchestrator import manual_stage,manual_context
    repo=tmp_path/'repo'
    shutil.copytree(ROOT,repo,ignore=shutil.ignore_patterns('.git','__pycache__','.pytest_cache'))
    subprocess.run(['git','init','-q',str(repo)],check=True)
    subprocess.run(['git','checkout','-qb','astra/manual-cpu-fixture'],cwd=repo,check=True)
    subprocess.run(['git','add','.'],cwd=repo,check=True)
    subprocess.run(['git','-c','user.name=Synthetic fixture','-c','user.email=fixture@invalid','commit','-qm','Synthetic candidate snapshot'],cwd=repo,check=True)
    pin=subprocess.check_output(['git','rev-parse','HEAD'],cwd=repo,text=True).strip()
    review=tmp_path/'synthetic-review.md';review.write_text('Synthetic evidence only.\nsource_sha: '+pin+'\n## Verdict: APPROVE\n')
    monkeypatch.setattr(manual_stage,'preflight',lambda:{'synthetic':True})
    config=cpu_package.runtime_config(repo);config['batch_ledger']=str(tmp_path/'synthetic-global')
    monkeypatch.setattr(cpu_package,'runtime_config',lambda root:config)
    subprocess.run(['git','config','user.name','Synthetic fixture'],cwd=repo,check=True)
    subprocess.run(['git','config','user.email','fixture@invalid'],cwd=repo,check=True)
    # This fixture checks context/accounting assembly, not live host readiness.
    monkeypatch.setattr(cpu_package,'runtime_preflight',lambda *a:{'status':'SYNTHETIC_READY','model_calls':0})
    state=tmp_path/'lane';result=manual_driver.initialize(repo,state,review,cpu=True)
    assert result['calls_used']==0
    driver=manual_driver.Driver(state);rows=driver.current()['artifacts']
    for kind,required in [('configuration','sprint10-m2-cpu-adapter-v1'),('metric_contract','byte-identical')]:
        selected=[r for r in rows if r['type']==kind];assert len(selected)==1
        assert required in (driver.context/selected[0]['path']).read_text()
    for stage in manual_driver.STAGES:
        text,measurement=manual_context.prepare(driver.context,stage=stage,idea_ids=['Sprint10'],task=driver.task(stage,driver.current()),artifacts=rows,workspace=tmp_path/stage)
        assert len(text)<200000 and 'sprint10-m2-cpu-adapter-v1' in text and 'byte-identical' in text
        assert 'at most 30 in total across M2' in text and '**M2: Server CPU executor' in text
        assert 'H2 and the old controller remain archived/read-only' in text
    assert not driver.store.db.execute('SELECT 1 FROM manual_calls').fetchone()
    assert not driver.store.batch.db.execute('SELECT 1 FROM autonomy_calls').fetchone()


def test_cpu_package_private_under_permissive_caller_umask(tmp_path):
    import os
    from orchestrator import private_records
    spec=tmp_path/'spec.md';review=tmp_path/'review.json'
    spec.write_text('Synthetic spec: no patient computation.');review.write_text('{"synthetic":true}')
    originals={str(q):q.read_bytes() for q in [spec,review]}
    previous=os.umask(0)
    try:
        folder=tmp_path/'emitted'
        cpu_package.emit(ROOT,folder,'synthetic','a'*40,spec,review)
    finally:os.umask(previous)
    private_records.check_tree(folder)
    assert folder.stat().st_mode&0o777==0o700
    assert all(q.stat().st_mode&0o777==0o600 for q in folder.iterdir())
    assert originals=={str(q):q.read_bytes() for q in [spec,review]}
