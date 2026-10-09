"""Synthetic ledger tests: real spending gates; no model/provider/patient calls."""
import copy,json
from pathlib import Path
from types import SimpleNamespace as NS
import pytest
from orchestrator import spending_continuation as sc,experiment_timeout_continuation as t,private_records as pr
from orchestrator.autonomy_accounting import BatchAccounts
from orchestrator.modal_budget import ComputeAccounts
from orchestrator import diagnostics_budget as budget
from orchestrator.diagnostics_contract import encoded,sha
from test_diagnostics_connection import prepared,CPUProvider
from test_modal_executor import private_test_environment
from test_modal_item4_budget import snapshot,NOW


@pytest.fixture
def continued(prepared,tmp_path,monkeypatch):
    folder,b,provider_config,old=prepared;b=copy.deepcopy(b)
    root=tmp_path/'host';batch=BatchAccounts(root/'var/lib/research-system-autonomy/reviews',filesystem_root=root)
    run=t.ITEM6;state=root/'active/lane';pr.mkdir(state,parents=True)
    plan=b'preserved preparation';pr.write_bytes(state/'preparation-plan.json',plan)
    owner={'state':'/old/lane','source':'a'*40,'run_id':run,'plan_sha256':sha(plan),'review_sha256':'a'*64,
        'execution_scope':{'run_id':run,'item_number':6,'authority_sha256':b['authority_sha256'],'plan_sha256':b['execution_plan_sha256']}}
    batch.register_run(run,owner)
    batch.db.execute("INSERT INTO autonomy_calls VALUES(?,?,?,?,?,?,?,?)",(t.FAILED,'scientific',t.ITEM4,1,'2026-10-07','UNCERTAIN','{}','{"original_charge":1}'))
    config={'source':sc.SOURCE,'run_id':run,'owner_binding':owner,'plan_sha256':sha(plan),
        'execution_scope':owner['execution_scope'],'timeout_continuation':t.KEY}
    pr.write_bytes(state/'lane.json',encoded(config))
    failed=dict(batch.db.execute('SELECT * FROM autonomy_calls').fetchone())
    cp={'authority_sha256':'d'*64,'runtime_sha256':sc.RUNTIME,'global_calls':{t.FAILED:t.sha(failed)},
        'owners':{run:t.sha(dict(batch.db.execute('SELECT * FROM autonomy_runs').fetchone()))}}
    grant={'kind':t.KEY,'checkpoint_sha256':t.CHECKPOINT,'authority_sha256':cp['authority_sha256'],'source':sc.SOURCE,
        'filesystem_root':str(root),'review_path':str(root/'review/report.md'),'review_sha256':'r'*64,
        'terminal_proof_sha256':'f'*64,'lanes':{'6':{'state':str(state),'config_sha256':t.sha(config)}}}
    batch.db.execute('INSERT INTO events VALUES(?,?,?)',(t.KEY,t.ITEM4,json.dumps(grant)))
    impl={'source':'b'*40,'previous':{'state':'/active'}}
    monkeypatch.setattr(sc,'implementation',lambda root:impl)
    monkeypatch.setattr(t,'checkpoint',lambda:cp)
    monkeypatch.setattr('orchestrator.autonomy_review.verify_result',lambda p:{'verdict':'APPROVE','source_sha':sc.SOURCE,'runtime_sha256':sc.RUNTIME,'report_sha256':'r'*64})
    proof={'proof_sha256':'f'*64,'classification':'PROVEN_EXACT_AUTHOR_TIMEOUT_ADMIN_ONLY'}
    monkeypatch.setattr('orchestrator.administrative_terminal.verify',lambda row,p:proof)
    b.update(source=sc.SOURCE,owner_sha256=sha(encoded(owner)))
    return NS(folder=folder,b=b,provider=provider_config,batch=batch,accounts=ComputeAccounts(batch),owner=owner,
        config=config,state=state,cp=cp,grant=grant,impl=impl,proof=proof)


def reserve(f):return budget.reserve(f.accounts,sha(encoded(f.b)),t.ITEM6,f.b,billing_snapshot=snapshot(),now=NOW)

def rows(f):return {name:[dict(r) for r in f.batch.db.execute('SELECT * FROM '+name)] for name in ('autonomy_calls','autonomy_runs','autonomy_assets','autonomy_compute')}


def test_continuation_reserves_once_preserving_owner_and_charge(continued):
    f=continued;before=rows(f)
    assert sc.lane(f.batch,t.ITEM6,f.owner,sc.SOURCE)==(f.state,f.config)
    assert sc.closed_ids(f.batch,t.ITEM6)=={t.FAILED}
    assert reserve(f) is True and reserve(f) is False
    after=rows(f)
    assert after['autonomy_calls']==before['autonomy_calls'] and after['autonomy_runs']==before['autonomy_runs']
    assert after['autonomy_compute'][0]['status']=='RESERVED' and after['autonomy_compute'][0]['reserved_micro_usd']==f.b['cost']['reserved_micro_usd']
    f.b['provisioning_sha256']='e'*64
    with pytest.raises(ValueError,match='ALREADY_SUBMITTED_NO_RESTART'):reserve(f)


@pytest.mark.parametrize('damage',['config','state','owner','source','grant','review','terminal','original-charge','running','unrelated-uncertain','halt','plan','missing-implementation'])
def test_continuation_refuses_drift_without_reservation(continued,monkeypatch,damage):
    f=continued
    if damage=='config':pr.write_bytes(f.state/'lane.json',encoded({**f.config,'extra':True}))
    elif damage=='state':f.grant['lanes']['6']['state']='/wrong/state'
    elif damage=='owner':f.batch.db.execute("UPDATE autonomy_runs SET binding='{}'")
    elif damage=='source':f.b['source']='c'*40
    elif damage=='grant':f.grant['checkpoint_sha256']='0'*64
    elif damage=='review':monkeypatch.setattr('orchestrator.autonomy_review.verify_result',lambda p:{'verdict':'REVISE','source_sha':sc.SOURCE,'runtime_sha256':sc.RUNTIME,'report_sha256':'r'*64})
    elif damage=='terminal':f.proof['proof_sha256']='0'*64
    elif damage=='original-charge':f.batch.db.execute("UPDATE autonomy_calls SET receipt='{}'")
    elif damage=='running':f.batch.db.execute("UPDATE autonomy_calls SET status='RUNNING'")
    elif damage=='unrelated-uncertain':f.batch.db.execute("INSERT INTO autonomy_calls VALUES('other','scientific','other',1,'2026-10-07','UNCERTAIN','{}',NULL)")
    elif damage=='halt':pr.write_text(f.state/'HALT','stop')
    elif damage=='plan':pr.write_bytes(f.state/'preparation-plan.json',b'changed')
    elif damage=='missing-implementation':monkeypatch.setattr(sc,'implementation',lambda root:(_ for _ in ()).throw(ValueError('missing review')))
    if damage in {'state','grant'}:f.batch.db.execute('UPDATE events SET payload=? WHERE id=?',(json.dumps(f.grant),t.KEY))
    before=rows(f)
    with pytest.raises((ValueError,KeyError,FileNotFoundError)):reserve(f)
    assert rows(f)==before


def test_over_cap_launch_refused_before_provider_and_charge_preserved(continued,tmp_path):
    from orchestrator.modal_executor import ModalExecutor
    from orchestrator.manual_executor import inventory
    f=continued
    # Keep the synthetic execution package consistent with the continued source.
    package=json.loads((f.folder/'manifest.json').read_bytes());package['binding']=f.b
    pr.write_bytes(f.folder/'manifest.json',encoded(package))
    f.batch.db.execute("INSERT INTO autonomy_assets VALUES('original-image',?,'{}','READY',100000000,'{}')",(t.ITEM6,))
    before=rows(f);provider=CPUProvider();executor=ModalExecutor(tmp_path/'exec/jobs.sqlite',f.provider,provider,f.batch)
    with pytest.raises(ValueError,match='DIAGNOSTICS_HARD_COST_CAP'):
        executor.submit(t.ITEM6,f.b,f.folder,tmp_path/'emitted')
    assert 'create' not in provider.calls and 'launch' not in provider.calls
    assert rows(f)==before and not before['autonomy_compute']


def test_exact_hundred_dollar_boundary_still_reserves(continued):
    f=continued;amount=f.b['cost']['reserved_micro_usd']
    f.batch.db.execute("INSERT INTO autonomy_assets VALUES('original-image',?,'{}','READY',?,'{}')",(t.ITEM6,100000000-amount))
    assert reserve(f)
    assert f.batch.db.execute('SELECT sum(reserved_micro_usd) FROM autonomy_assets').fetchone()[0]+amount==100000000


def test_caps_and_authority_unchanged():
    from orchestrator import diagnostics_policy as cpu,modal_item4_policy as gpu
    assert cpu.TOTAL_MICRO_USD==100000000
    assert (gpu.SMOKE_CAP,gpu.PROJECTION_LIMIT,gpu.TOTAL_CAP)==(75000000,1200000000,1275000000)
    path=Path(sc.__file__).parents[1]/'docs/SPENDING_CONTINUATION_AUTHORITY_20261007.txt'
    assert sha(path.read_bytes())==sc.AUTHORITY


def test_service_changes_only_imports_and_phase_limited_command():
    from tools.spending_repair_service import unit
    original='Environment=PYTHONPATH=/old:/sdk\nExecStart=/usr/bin/python3 -s -B -m orchestrator.experiment_driver advance --state /state/lane\nNoNewPrivileges=true\nProtectSystem=strict\nReadWritePaths=/state /ledger\nUMask=0077\n'
    got=unit(original,'/old','/new','/state/lane').decode()
    assert got==original.replace('PYTHONPATH=/old:','PYTHONPATH=/new:').replace('-m orchestrator.experiment_driver','-m tools.spending_repair_service')
    with pytest.raises(ValueError):unit(original,'/wrong','/new','/state/lane')


@pytest.fixture
def installation(tmp_path,monkeypatch):
    from tools.deploy_manual_lane import bound
    root=tmp_path/'installation';release=bound(root,'/opt/repaired');pr.mkdir(release/'orchestrator',parents=True)
    source=Path(sc.__file__).read_bytes();pr.write_bytes(release/'orchestrator/spending_continuation.py',source)
    authority=Path(sc.__file__).parents[1]/'docs/SPENDING_CONTINUATION_AUTHORITY_20261007.txt'
    pr.mkdir(release/'docs');pr.write_bytes(release/'docs/SPENDING_CONTINUATION_AUTHORITY_20261007.txt',authority.read_bytes())
    runtime=bound(root,'/runtime.json');pr.write_bytes(runtime,b'synthetic unchanged runtime')
    monkeypatch.setattr(sc,'RUNTIME',sha(runtime.read_bytes()))
    previous={'source':sc.SOURCE,'runtime':'/runtime.json'}
    pointer=bound(root,sc.POINTER);pr.mkdir(pointer.parent,parents=True);pr.write_bytes(pointer,encoded(previous))
    names=['orchestrator/spending_continuation.py','docs/SPENDING_CONTINUATION_AUTHORITY_20261007.txt']
    files={'/opt/repaired/'+n:{'sha256':sha((release/n).read_bytes()),'mode':(release/n).stat().st_mode&0o777} for n in names}
    rec=bound(root,sc.RECORD);pr.mkdir(rec,parents=True);pr.write_bytes(rec/'FILES.json',encoded(files))
    report={'change_id':sc.CHANGE,'verdict':'APPROVE','source_sha':'b'*40,'runtime_sha256':sc.RUNTIME,'report_sha256':'d'*64}
    receipt={'repair':sc.CHANGE,'scientific_source':sc.SOURCE,'source':'b'*40,'layout':{'release':'/opt/repaired'},
        'files_sha256':sha((rec/'FILES.json').read_bytes()),'previous':previous,'review_folder':'/review',
        'review_sha256':'d'*64,'changed_files':names}
    pr.write_bytes(rec/'installed.json',encoded(receipt));pr.mkdir(root/'review')
    pr.write_bytes(root/'review/packet-manifest.json',encoded({'source_files':{n:sha((release/n).read_bytes()) for n in names}}))
    monkeypatch.setattr(sc,'__file__',str(release/'orchestrator/spending_continuation.py'))
    monkeypatch.setattr('orchestrator.autonomy_review.verify_result',lambda p:report)
    return NS(root=root,release=release,report=report,receipt=receipt,rec=rec,pointer=pointer,runtime=runtime)


def test_complete_installed_runtime_and_independent_approval_required(installation):
    f=installation;assert sc.implementation(f.root)==f.receipt


@pytest.mark.parametrize('damage',['review','review-source','review-runtime','selected','runtime','source','manifest','extra-file','authority'])
def test_installation_integrity_refuses(installation,damage):
    f=installation
    if damage=='review':f.report['verdict']='REJECT'
    elif damage=='review-source':f.report['source_sha']='c'*40
    elif damage=='review-runtime':f.report['runtime_sha256']='c'*64
    elif damage=='selected':pr.write_bytes(f.pointer,encoded({'source':'c'*40,'runtime':'/runtime.json'}))
    elif damage=='runtime':pr.write_bytes(f.runtime,b'changed')
    elif damage=='source':pr.write_bytes(f.release/'orchestrator/spending_continuation.py',b'changed')
    elif damage=='manifest':pr.write_bytes(f.rec/'FILES.json',b'{}')
    elif damage=='extra-file':pr.write_bytes(f.release/'unreviewed.py',b'changed')
    elif damage=='authority':pr.write_bytes(f.release/'docs/SPENDING_CONTINUATION_AUTHORITY_20261007.txt',b'changed')
    with pytest.raises(ValueError):sc.implementation(f.root)


def test_image_runtime_source_is_separate_from_scientific_source(continued):
    f=continued
    assert sc.lane(f.batch,t.ITEM6,f.owner,f.impl['source'],image=True)==(f.state,f.config)
    with pytest.raises(ValueError,match='SOURCE'):sc.lane(f.batch,t.ITEM6,f.owner,f.impl['source'])
    with pytest.raises(ValueError,match='SOURCE'):sc.lane(f.batch,t.ITEM6,f.owner,'z'*40,image=True)


def test_item4_maps_only_to_its_exact_current_lane(continued):
    f=continued;owner=copy.deepcopy(f.owner);owner.update(run_id=t.ITEM4)
    owner['execution_scope'].update(run_id=t.ITEM4,item_number=4)
    state=f.state.parent/'item4/lane';pr.mkdir(state,parents=True)
    pr.write_bytes(state/'preparation-plan.json',(f.state/'preparation-plan.json').read_bytes())
    config={**f.config,'run_id':t.ITEM4,'owner_binding':owner,'execution_scope':owner['execution_scope']}
    pr.write_bytes(state/'lane.json',encoded(config))
    # Synthetic fixture materializes the already-authorized pair; no production registration change.
    f.batch.db.execute("INSERT INTO autonomy_runs VALUES(?,?,'ACTIVE')",(t.ITEM4,json.dumps(owner,sort_keys=True)))
    f.cp['owners'][t.ITEM4]=t.sha(dict(f.batch.db.execute('SELECT * FROM autonomy_runs WHERE id=?',(t.ITEM4,)).fetchone()))
    f.grant['lanes']['4']={'state':str(state),'config_sha256':t.sha(config)}
    f.batch.db.execute('UPDATE events SET payload=? WHERE id=?',(json.dumps(f.grant),t.KEY))
    assert sc.lane(f.batch,t.ITEM4,owner,sc.SOURCE)==(state,config)
    assert sc.lane(f.batch,t.ITEM4,owner,f.impl['source'],image=True)==(state,config)
    assert sc.closed_ids(f.batch,t.ITEM4)=={t.FAILED}
    with pytest.raises(ValueError):sc.lane(f.batch,t.ITEM4,f.owner,sc.SOURCE)


@pytest.mark.parametrize('phase',['run_spec_author','run_spec_review','result_interpretation_author','result_interpretation_review','BLOCKED','EXECUTE_EXPERIMENT','COLLECT_EXPERIMENT'])
def test_execution_entrypoint_cannot_make_scientific_calls(tmp_path,monkeypatch,phase):
    from tools import spending_repair_service as service
    state=tmp_path/'lane';pr.mkdir(state);seen=[]
    class Closed:
        def close(self):seen.append('closed')
    driver=NS(state=state,config={'run_id':t.ITEM6,'owner_binding':{},'source':sc.SOURCE},
        guard=lambda:seen.append('guard'),current=lambda:{'phase':phase},
        store=NS(db=Closed(),batch=NS(db=Closed())))
    monkeypatch.setattr(service.os,'getuid',lambda:1003);monkeypatch.setattr(service.os,'getgid',lambda:1003)
    monkeypatch.setattr(sc,'implementation',lambda:{'previous':{'state':str(tmp_path)}})
    monkeypatch.setattr(sc,'lane',lambda *a:seen.append('lane'))
    monkeypatch.setattr('orchestrator.experiment_driver.ExperimentDriver',lambda state:driver)
    monkeypatch.setattr('orchestrator.experiment_package.advance',lambda *a:seen.append('execute'))
    if phase in {'EXECUTE_EXPERIMENT','COLLECT_EXPERIMENT'}:
        service.advance(state);assert seen==['guard','lane','execute','closed','closed']
    else:
        with pytest.raises(ValueError,match='EXECUTION_PHASE_ONLY'):service.advance(state)
        assert seen==['guard','closed','closed']


def test_public_systemd_parent_keeps_its_mode_and_requires_root_trust(tmp_path,monkeypatch):
    from tools.spending_repair_service import destination_parent
    seen=[]
    monkeypatch.setattr('orchestrator.manual_host_guard.trusted',lambda path:seen.append(path))
    destination_parent(Path('/etc/systemd/system/research-test.service'))
    assert seen==[Path('/etc/systemd/system')]
    monkeypatch.setattr('orchestrator.manual_host_guard.trusted',lambda path:(_ for _ in ()).throw(ValueError('untrusted')))
    with pytest.raises(ValueError,match='untrusted'):destination_parent(Path('/etc/systemd/system/research-test.service'))
    private=tmp_path/'private/new.json';destination_parent(private)
    assert private.parent.stat().st_mode&0o777==0o700 and not private.exists()
