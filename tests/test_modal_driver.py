"""Real driver transitions with synthetic model/provider outputs; never paid calls."""
import ast
import csv
import io
import json
from pathlib import Path
import re
import shutil
import subprocess
import pytest
from orchestrator import modal_driver,modal_package,manual_runtime,connectivity,private_records,modal_assets,modal_cleanup
from orchestrator.manual_executor import atomic,read,digest,inventory
from orchestrator.modal_executor import canonical
from orchestrator.autonomy_accounting import BatchAccounts
from test_manual_lane import lane,root,ROOT,policy,private_copied_fixture
from test_modal_executor import Provider


def fake_model(work,stage,clients,pin):
    assert digest((work/'prompt.md').read_bytes())==pin
    if stage=='run_spec_author':
        prompt=(work/'prompt.md').read_text();code=re.search(r'^notebook_code_sha256: ([a-f0-9]{64})$',prompt,re.M).group(1)
        private_records.write_text(work/'SPEC.proposed.md','# Synthetic spec\nrun_id: synthetic-stepd\nnotebook_code_sha256: '+code+'\n')
    elif stage.endswith('review'):private_records.write_text(work/'review.json',json.dumps({'verdict':'APPROVE','rationale':'Synthetic approval only; no model used.'}))
    else:
        private_records.write_text(work/'interpretation.md','# Summary\nThe synthetic known case matched; this test provides no scientific efficacy evidence.\n# Details\nDeterministic test output.\n')
        private_records.write_text(work/'investigator_next_decision.json',json.dumps({'status':'PROPOSAL_ONLY','proposed_action_type':'stop','action':'Stop this completed reproduction.','rationale':'No additional run is needed.','charter_basis':'','blocker_ids':[]}))
    return {'family_effective':'claude' if stage.endswith('review') else 'codex','exit_class':'ok','synthetic':True}


class Results(Provider):
    def create(self,config,binding,package):
        return {**super().create(config,binding,package),
                'entrypoint':'idle-only','binding_sha256':digest(canonical(binding))}

    def launch(self,provider_id,binding):
        return {**super().launch(provider_id,binding),
                'provider_id':provider_id,'binding_sha256':digest(canonical(binding))}

    def collect(self,provider_id,binding,folder):
        self.calls.append('collect');cases=self.cases
        fields=['case','recipe','fingerprint','shuffle','fold','train_seed','tp','fp','fn','dice','f1_voxel'];rows=[];means={}
        for recipe,fp,fn in [('U_base_raw',200,1000),('U_base_smoothed',170,900)]:
            dsc=200/(200+fp+fn);means[recipe]=dsc
            for case in cases:rows.append(dict(zip(fields,[case,recipe,binding['run_id'],101,0,1,100,fp,fn,dsc,dsc])))
        stream=io.StringIO();writer=csv.DictWriter(stream,fields);writer.writeheader();writer.writerows(rows)
        receipt={'run_id':binding['run_id'],'input_contract':binding['input_contract'],'versions':{'synthetic':'fixture'},'arm':'U_base','shuffle':101,'fold':0,'training_seed':1,'maximum_epochs':2,'held_count':20,'mean_dice':means}
        known={'folds/unet_U_base_s101_f0_t1.csv':stream.getvalue().encode(),'execution.json':canonical(receipt),'summary.json':canonical({'mean_dice':means}),
            'ckpt/curves_U_base_s101_f0_t1.json':canonical({'arm':'U_base','inner_curve':[0.1,0.2],'final_curve':[0.1,0.2],'best_epoch':2})}
        for name in binding['outputs']:
            path=folder/name;private_records.mkdir(path.parent,parents=True,exist_ok=True);private_records.write_bytes(path,known.get(name,b'Synthetic non-scientific fixture'))
        return {'binding_sha256':digest(canonical(binding)),'provider_id':provider_id,'file_sha256':inventory(folder)}

@pytest.fixture
def modal_lane(lane,monkeypatch):
    monkeypatch.setattr(connectivity,'require',lambda *a,**k:{'synthetic':True})
    monkeypatch.setattr(manual_runtime,'settings',lambda:{'host_guard':{'receipt':str(lane/'missing-proof.json')}})
    config=read(lane/'lane.json');repo=Path(config['root']);batch_path=repo/'modal-batch'
    batch=BatchAccounts(batch_path);batch.register_run(config['run_id'],{'synthetic':True})
    smoke={'cases':[f'dev-{n:03}' for n in range(99)],'partitions':{'held':[f'dev-{n:03}' for n in range(20)]},'versions':{'synthetic':'fixture'}}
    smoke_path=lane/'smoke.json';atomic(smoke_path,smoke);plan=lane/'plan.json';atomic(plan,{'synthetic':True})
    dest=repo/modal_package.SCIENCE;shutil.copytree(ROOT/modal_package.SCIENCE,dest);private_copied_fixture(dest)
    config.update(backend='modal',idea_ids=['Sprint9'],modal={'batch_ledger':str(batch_path),'input_contract':{'scope':'DEVELOPMENT_99_ONLY','count':99,'cohort_sha256':'a'*64,'cache_map_sha256':'b'*64,'split_sha256':'c'*64},'image_id':'im-synthetic','data_volume_id':'vo-data','package_volume_id':'vo-package','wheel_volume_id':'vo-wheels','asset_expires_utc':'2099-01-01T00:00:00+00:00'},
        resources={'gpu':'A100-80GB','cpu':4,'memory_mib':32768,'timeout_seconds':1800},overhead_micro_usd=500000,
        smoke_path=str(smoke_path),smoke_sha256=digest(canonical(smoke)),plan_path=str(plan),plan_sha256=digest(plan.read_bytes()),
        notebook_code_sha256=modal_package.code_identity(repo))
    atomic(lane/'lane.json',config)
    (repo/'.gitignore').write_text('lane/\nlane-scientific-workspaces/\nmodal-batch/\n')
    for key,value in [('user.name','Synthetic test'),('user.email','fixture@invalid')]:subprocess.run(['git','config',key,value],cwd=repo,check=True)
    subprocess.run(['git','add','.'],cwd=repo,check=True);subprocess.run(['git','commit','-qm','Synthetic fixture'],cwd=repo,check=True)
    def upload(provider,binding,package,record):
        provider.calls.append('upload');manifest=read(package/'manifest.json')
        return {'status':'READY','manifest_sha256':digest(canonical(manifest)),'volume_id':'vo-package'}
    monkeypatch.setattr(modal_assets,'prepare_package',upload)
    monkeypatch.setattr(modal_cleanup,'clear_copies',lambda *a,**k:{'status':'CLEARED','synthetic':True})
    p=Results();p.cases=smoke['partitions']['held'];d=modal_driver.ModalDriver(lane,runner=fake_model,provider=p)
    return d,p


def test_actual_driver_connection_completes_one_synthetic_cycle(modal_lane):
    d,p=modal_lane
    for expected in ['run_spec_review','COMMIT_SPEC','EMIT_PACKAGE','PREPARE_REMOTE_PACKAGE']:
        result=d.advance();assert result['phase']==expected,result
    assert d.advance()['phase']=='EXECUTE_MODAL'
    assert d.status()['calls_used']==2 and 'create' not in p.calls
    assert p.calls.count('upload')==1
    assert d.advance()['phase']=='WAIT_OUTPUTS'
    for _ in range(3):assert d.advance()['phase']=='WAIT_OUTPUTS'
    assert p.calls.count('create')==p.calls.count('launch')==1
    p.state='COMPLETE';assert d.advance()['phase']=='result_interpretation_author'
    for expected in ['result_interpretation_review','UPDATE_STATE','REPORT','COMPLETE']:
        result=d.advance();assert result['phase']==expected,result
    assert d.advance()['phase']=='COMPLETE' and d.status()['calls_used']==4
    assert d.store.batch.db.execute("SELECT count(*) FROM autonomy_calls").fetchone()[0]==4
    assert d.store.batch.db.execute("SELECT status FROM autonomy_runs").fetchone()[0]=='COMPLETE'
    assert 'Sprint9 system smoke acceptance' in (d.root/modal_driver.PROFILE/'STATE.md').read_text()
    assert (d.state/'REPORT.md').is_file()


def test_gpu_unknown_submission_blocks_driver_without_another_call(modal_lane):
    d,p=modal_lane
    for _ in range(4):d.advance()
    manifest=d.current()['manifest'];atomic(d.state/'remote-package-ready.json',{'status':'READY','manifest_sha256':digest(canonical(manifest)),'volume_id':'vo-package'})
    d.advance();p.failure='create'
    assert d.advance()['phase']=='BLOCKED'
    assert 'UNCERTAIN' in (d.state/'DECISION_REQUEST.md').read_text()
    assert d.advance()['phase']=='BLOCKED' and d.status()['calls_used']==2
    assert p.calls.count('create')==1


def test_new_driver_uses_existing_guarded_assembly_only():
    for name in ['modal_driver.py','modal_package.py']:
        code=ast.parse((ROOT/'orchestrator'/name).read_text())
        assert not any(isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and n.func.attr=='assemble' for n in ast.walk(code))
    text=(ROOT/'orchestrator/manual_driver.py').read_text()
    assert "idea_ids=self.config.get('idea_ids',['Sprint10'])" in text


def test_open_finding_lookup_uses_actual_idea_scope(root):
    from test_context_budget import add_obligation,save_manifest
    from orchestrator import manual_context
    add_obligation(root)
    registry=read(root/modal_driver.PROFILE/'obligations.json')
    row=next(r for r in registry['obligations'] if r['id']=='TEST-STOP');row['scope']['idea_ids']=['Sprint9']
    atomic(root/modal_driver.PROFILE/'obligations.json',registry);save_manifest(root)
    assert 'TEST-STOP' in manual_context.open_blocker_ids(root,'result_interpretation_author',['Sprint9'])
    assert 'TEST-STOP' not in manual_context.open_blocker_ids(root,'result_interpretation_author',['Sprint10'])


def test_bounded_server_loop_finishes_same_run_without_client_forwarding(modal_lane):
    d,p=modal_lane
    def wait(seconds):assert seconds==30;p.state='COMPLETE'
    outcome=modal_driver.run_until_stop(d.state,factory=lambda state:d,sleep=wait)
    assert outcome['phase']=='COMPLETE' and outcome['calls_used']==4
    assert p.calls.count('create')==p.calls.count('launch')==1
    assert modal_driver.run_until_stop(d.state,factory=lambda state:d,sleep=wait)['calls_used']==4


def test_bounded_server_loop_stops_on_block_without_retry(modal_lane):
    d,p=modal_lane;p.failure='create'
    result=modal_driver.run_until_stop(d.state,factory=lambda state:d,sleep=lambda n:pytest.fail('no wait'))
    assert result['phase']=='BLOCKED' and result['calls_used']==2 and p.calls.count('create')==1


def test_supervisor_before_initialization_never_makes_a_model_call(tmp_path):
    state=tmp_path/'lane';preparation=tmp_path/'modal-preparation';private_records.mkdir(preparation)
    assert modal_driver.supervise(state,preparation)['status']=='NOT_PREPARED'
    atomic(preparation/'runtime.json',{'asset_expires_utc':'2099-01-01T00:00:00+00:00'})
    assert modal_driver.supervise(state,preparation,factory=lambda *a:pytest.fail('no driver'),provider_factory=lambda *a:pytest.fail('no provider'))['status']=='AWAITING_INITIALIZATION'


def test_modal_templates_preserve_existing_controls_and_two_unit_route():
    source=(ROOT/'deploy/modal-lane/run.service.in').read_text()
    for part in ['User=partho','NoNewPrivileges=true','ProtectSystem=strict','PrivateTmp=true','UMask=0077','ExecStartPre=+/usr/bin/env PYTHONPATH=@RELEASE@ /usr/bin/python3 -s -B','tools/modal_transition_service.py','Restart=no']:
        assert part in source
    timer=(ROOT/'deploy/modal-lane/run.timer.in').read_text()
    assert 'OnBootSec=60' in timer and 'OnUnitInactiveSec=60' in timer
