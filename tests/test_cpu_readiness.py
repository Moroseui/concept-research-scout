"""Readiness failures precede scientific charges; all fixtures are synthetic."""
import json
import subprocess
from pathlib import Path
from types import SimpleNamespace
import pytest
from orchestrator import cpu_package, cpu_isolation, manual_driver

ROOT=Path(__file__).resolve().parents[1]

def test_real_cpu_notebook_requires_xgboost_and_fixed_numeric_packages():
    names=cpu_package.notebook_imports(cpu_package.notebook_bytes(ROOT,'inspection-only'))
    assert {'xgboost','numpy','scipy','pandas','sklearn','nibabel','matplotlib'} <= set(names)
    config=cpu_package.runtime_config(ROOT)
    assert 'xgboost-cpu==3.4.1' in config['packages']
    assert {'numpy==2.1.3','pandas==2.2.3','scipy==1.16.3'} <= set(config['packages'])

def test_import_inspection_does_not_execute_cells_or_training_helpers():
    raw=json.dumps({'cells':[{'cell_type':'code','source':[chr(10).join(['import os', 'try:', ' import xgboost', 'except ImportError:', ' pass', 'def training():', ' import never_called_module', 'raise RuntimeError("must not execute")'])]}]}).encode()
    assert cpu_package.notebook_imports(raw)==['os','xgboost']

def test_import_command_cannot_be_used_for_execution_or_dotted_payload(tmp_path):
    for kwargs in [{'imports':['xgboost']},{'probe':True,'imports':['os.path']},{'probe':True,'imports':['not a module']}]:
        with pytest.raises(ValueError,match='CPU_IMPORT_PROBE_SCOPE'):
            cpu_isolation.command({},tmp_path,tmp_path,tmp_path,**kwargs)

def test_runtime_preflight_missing_dependency_refuses(monkeypatch,tmp_path):
    raw=json.dumps({'cells':[{'cell_type':'code','source':['import xgboost']}]}).encode()
    monkeypatch.setattr(cpu_package,'notebook_bytes',lambda *a:raw)
    monkeypatch.setattr(cpu_package,'contract',lambda *a:{})
    monkeypatch.setattr(cpu_package,'verify_data',lambda *a:{'status':'SYNTHETIC'})
    def command(*args,**kwargs):
        assert kwargs=={'probe':True,'imports':['xgboost']}
        return ['synthetic-not-executed']
    monkeypatch.setattr(cpu_isolation,'command',command)
    monkeypatch.setattr(cpu_package.subprocess,'run',lambda *a,**k:SimpleNamespace(returncode=1,stdout='',stderr="ModuleNotFoundError: No module named xgboost"))
    with pytest.raises(ValueError,match='CPU_NOTEBOOK_IMPORT_PREFLIGHT_REFUSED'):
        cpu_package.runtime_preflight(tmp_path,{'data_root':str(tmp_path),'environment_sha256':'synthetic'})

def test_runtime_preflight_requires_exact_import_proof(monkeypatch,tmp_path):
    raw=json.dumps({'cells':[{'cell_type':'code','source':['import xgboost']}]}).encode()
    monkeypatch.setattr(cpu_package,'notebook_bytes',lambda *a:raw)
    monkeypatch.setattr(cpu_package,'contract',lambda *a:{})
    monkeypatch.setattr(cpu_package,'verify_data',lambda *a:{'status':'SYNTHETIC'})
    monkeypatch.setattr(cpu_isolation,'command',lambda *a,**k:['synthetic-not-executed'])
    monkeypatch.setattr(cpu_package.subprocess,'run',lambda *a,**k:SimpleNamespace(returncode=0,stdout=json.dumps({'status':'ISOLATED','verified_imports':[]}),stderr=''))
    with pytest.raises(ValueError,match='CPU_NOTEBOOK_IMPORT_PROOF_CHANGED'):
        cpu_package.runtime_preflight(tmp_path,{'data_root':str(tmp_path),'environment_sha256':'synthetic'})

def light_repo(tmp_path,monkeypatch,identity):
    monkeypatch.setenv('GIT_CONFIG_GLOBAL','/dev/null');monkeypatch.setenv('GIT_CONFIG_SYSTEM','/dev/null')
    repo=tmp_path/'repo';repo.mkdir()
    subprocess.run(['git','init','-q',str(repo)],check=True)
    subprocess.run(['git','-C',str(repo),'checkout','-qb','astra/manual-readiness'],check=True)
    (repo/'README').write_text('Synthetic readiness fixture only.')
    subprocess.run(['git','-C',str(repo),'add','README'],check=True)
    subprocess.run(['git','-C',str(repo),'-c','user.name=Fixture','-c','user.email=fixture@invalid','commit','-qm','fixture'],check=True)
    if identity:
        for key,value in [('user.name','Fixture'),('user.email','fixture@invalid')]:
            subprocess.run(['git','-C',str(repo),'config',key,value],check=True)
    pin=subprocess.check_output(['git','-C',str(repo),'rev-parse','HEAD'],text=True).strip()
    report=tmp_path/'review.md';report.write_text('Synthetic review only.\n'+pin+'\n## Verdict: APPROVE\n')
    monkeypatch.setattr(cpu_package,'runtime_config',lambda *a:{'data_root':'synthetic'})
    return repo,report

@pytest.mark.parametrize('failure',['git','dependency'])
def test_init_refuses_before_state_owner_or_call_allocation(tmp_path,monkeypatch,failure):
    repo,report=light_repo(tmp_path,monkeypatch,failure!='git')
    def preflight(*args):
        if failure=='git':pytest.fail('must check Git before CPU probe')
        raise ValueError('CPU_NOTEBOOK_IMPORT_PREFLIGHT_REFUSED: synthetic missing module')
    monkeypatch.setattr(cpu_package,'runtime_preflight',preflight)
    state=tmp_path/'lane'
    with pytest.raises(ValueError,match='CPU_GIT_IDENTITY_REQUIRED' if failure=='git' else 'CPU_NOTEBOOK_IMPORT_PREFLIGHT_REFUSED'):
        manual_driver.initialize(repo,state,report,cpu=True)
    assert not state.exists()
    assert not (repo/'.git/autonomy-cpu-owner.json').exists()


def update_fixture():
    from tools.cpu_environment_update import RUN,SOURCE,OLD_ENV,NEW_ENV
    new=json.loads((ROOT/'deploy/manual-lane/cpu-runtime.json').read_text())
    old={**new,'environment_root':'/opt/research-system-cpu-tools/m2-python312-v1','environment_sha256':OLD_ENV,'packages':new['packages'][:-1]}
    config={'run_id':RUN,'source':SOURCE,'backend':'cpu','cpu':old,'owner_binding':{'preserved':True},'policy':{'limit':8},'engine_files':{'unchanged':'hash'}}
    rows={'manual_state':[{'payload':json.dumps({'phase':'EMIT_PACKAGE'})}], 'manual_calls':[{'stage':stage,'status':'COMPLETE','attempt':1} for stage in ['run_spec_author','run_spec_review']]}
    return config,new,rows


def test_configuration_update_preserves_every_non_cpu_field_and_counters():
    from tools.cpu_environment_update import checked_update
    config,new,rows=update_fixture();before=json.dumps(rows,sort_keys=True)
    result=checked_update(config,new,rows)
    assert result['cpu']==new
    assert {k:v for k,v in result.items() if k!='cpu'}=={k:v for k,v in config.items() if k!='cpu'}
    assert json.dumps(rows,sort_keys=True)==before


@pytest.mark.parametrize('defect',['run','source','phase','job','package','recovery','call','uncertain','cap_path','data_path','cohort','old_pin','new_pin','old_version','extra_dependency'])
def test_configuration_update_refuses_drift_and_dispatched_work(defect):
    from tools.cpu_environment_update import checked_update
    config,new,rows=update_fixture()
    if defect in ['run','source']:config['run_id' if defect=='run' else 'source']='different'
    elif defect=='phase':rows['manual_state'][0]['payload']=json.dumps({'phase':'EXECUTE_CPU'})
    elif defect in ['job','package','recovery']:rows[{'job':'jobs','package':'manual_packages','recovery':'manual_recoveries'}[defect]]=[{'id':'existing'}]
    elif defect=='call':rows['manual_calls'].append(dict(rows['manual_calls'][0]))
    elif defect=='uncertain':rows['manual_calls'][0]['status']='UNCERTAIN'
    elif defect in ['cap_path','data_path']:new['batch_ledger' if defect=='cap_path' else 'data_root']='/different'
    elif defect=='cohort':new['cohort']='different'
    elif defect=='old_pin':config['cpu']['environment_sha256']='different'
    elif defect=='new_pin':new['environment_sha256']='different'
    elif defect=='old_version':new['packages'][0]='changed==1'
    elif defect=='extra_dependency':new['packages'].append('other==1')
    with pytest.raises(ValueError):checked_update(config,new,rows)


@pytest.mark.parametrize('defect',[None,'report_hash','verdict','lane','database','preflight','prepared-package'])
def test_guarded_apply_preserves_original_and_refuses_invalid_evidence(tmp_path,monkeypatch,defect):
    import sqlite3,os
    from tools import cpu_environment_update as update
    from orchestrator import private_records
    from orchestrator.manual_executor import digest
    config,new,rows=update_fixture();state=tmp_path/'lane';state.mkdir(mode=0o700)
    # Synthetic repository and report test mechanics, never genuine approval.
    reviewed=tmp_path/'reviewed';reviewed.mkdir(mode=0o700)
    for cmd in [['git','init','-q'],['git','config','user.name','Fixture'],['git','config','user.email','fixture@invalid']]:
        subprocess.run(cmd,cwd=reviewed,check=True)
    (reviewed/'README').write_text('synthetic')
    subprocess.run(['git','add','README'],cwd=reviewed,check=True)
    subprocess.run(['git','commit','-qm','fixture'],cwd=reviewed,check=True)
    pin=subprocess.check_output(['git','rev-parse','HEAD'],cwd=reviewed,text=True).strip()
    config['root']=str(reviewed);config['notebook_code_sha256']='unchanged-notebook'
    raw=json.dumps(config,sort_keys=True).encode();private_records.write_bytes(state/'lane.json',raw)
    db=sqlite3.connect(state/'jobs.sqlite')
    db.execute('create table manual_state(payload text)');db.execute('insert into manual_state values(?)',(rows['manual_state'][0]['payload'],))
    db.execute('create table manual_calls(stage text,status text,attempt integer)')
    for row in rows['manual_calls']:db.execute('insert into manual_calls values(?,?,?)',(row['stage'],row['status'],row['attempt']))
    db.commit();db.close();(state/'jobs.sqlite').chmod(0o600)
    before=update.table_snapshot(state)
    binding={'reviewed_source':pin,'lane_sha256':digest(raw),'database_rows_sha256':digest(json.dumps(before,sort_keys=True).encode()),'new_cpu_sha256':digest(json.dumps(new,sort_keys=True).encode()),'repository_head':pin}
    report=tmp_path/'report.md';private_records.write_text(report,'Synthetic fixture. '+pin+'\n## Verdict: '+('CHANGES REQUIRED' if defect=='verdict' else 'APPROVE')+'\n')
    sha=digest(report.read_bytes())
    if defect=='report_hash':sha='incorrect'
    if defect=='lane':binding['lane_sha256']='incorrect'
    if defect=='database':binding['database_rows_sha256']='incorrect'
    monkeypatch.setattr(update.cpu_package,'runtime_config',lambda root:new)
    def probe(*args):
        if defect=='preflight':raise ValueError('SYNTHETIC_IMPORT_REFUSAL')
        return {'notebook_code_sha256':'unchanged-notebook','status':'READY','synthetic':True}
    monkeypatch.setattr(update.cpu_package,'runtime_preflight',probe)
    monkeypatch.setattr(update,'preserved_pins',lambda config:pin)
    out=tmp_path/'record'
    if defect=='prepared-package':(state/'prepared-package').mkdir(mode=0o700)
    if defect:
        with pytest.raises(ValueError):update.apply(state,binding,report,sha,reviewed,out)
        assert (state/'lane.json').read_bytes()==raw and not out.exists()
    else:
        result=update.apply(state,binding,report,sha,reviewed,out)
        assert result['status']=='APPLIED' and (out/'lane.before.json').read_bytes()==raw
        assert json.loads((state/'lane.json').read_bytes())=={**config,'cpu':new}
        assert (out/'COMPLETE.json').is_file()
        private_records.check_tree(out);private_records.check_tree(state)
        with pytest.raises(ValueError,match='EXISTING_CPU_UPDATE_RECORD'):update.apply(state,binding,report,sha,reviewed,out)
    assert update.table_snapshot(state)==before
