"""Real scratch promotion/selection/rollback; approvals are synthetic, no calls."""
import json,os,sqlite3,subprocess
from pathlib import Path
import pytest
from tools import manual_promotion as promotion,manual_host_control as host,deploy_manual_lane as base
from orchestrator import private_records as pr
from test_experiment_authoring_promotion import native_fixture,root_holds,qualified,private_scratch


def plans(tmp_path):
    selected={}
    for item in (6,4):
        p=tmp_path/('plan'+str(item)+'.json')
        pr.write_text(p,json.dumps({'schema':'experiment-lane/v1','item_number':item,
            'execution_provisioning':'/var/lib/synthetic-item'+str(item)+'-selection',
            'synthetic_fixture':'Selection only; no actual experiment authority'})+'\n')
        selected[item]=p
    return selected


def prepare(tmp_path):
    args,original,_,inv=native_fixture(tmp_path);p=plans(tmp_path)
    for item in (6,4):root_holds(args[0],json.loads(p[item].read_text())['execution_provisioning'])
    args=qualified(tmp_path,args,p[6],plans=p)
    return args,p,original,inv


def install(tmp_path):
    args,p,original,inv=prepare(tmp_path)
    receipt=promotion.promote(*args,entrypoint='experiment',experiment_plan=p[6],experiment_companion_plan=p[4])
    v=receipt['layout'];selected=base.read(base.bound(args[0],promotion.POINTER))
    state=base.bound(args[0],v['state'])
    # Same owner provisioning used on the live host, on this new scratch only.
    for path in [state,*state.rglob('*')]:os.chown(path,1003,1003)
    return args,p,receipt,selected,original,inv


def ledger(lane,statuses,phase='WAIT_OUTPUTS'):
    pr.mkdir(lane,parents=True,exist_ok=True)
    pr.write_text(lane/'lane.json','{"synthetic":true}\n')
    with sqlite3.connect(lane/'jobs.sqlite') as db:
        db.execute('CREATE TABLE manual_state(id,payload)');db.execute('INSERT INTO manual_state VALUES(1,?)',(json.dumps({'phase':phase}),))
        db.execute('CREATE TABLE manual_calls(status)');db.executemany('INSERT INTO manual_calls VALUES(?)',[(x,) for x in statuses])
    for p in [lane,*lane.iterdir()]:os.chown(p,1003,1003)


def test_companion_service_uses_real_paths_without_wider_write_access():
    tag='research-manual-sprint10-two-lane-synthetic';v=promotion.layout(tag);sdk='/opt/synthetic-sdk/site-packages'
    primary=promotion.service_configuration(v,tag,'experiment',sdk)[0].decode().splitlines()
    service,timer=promotion.service_configuration(v,tag,'experiment',sdk,companion=True);lines=service.decode().splitlines()
    assert '--lane '+v['state']+'/item4/lane' in service.decode()
    assert '--state '+v['state']+'/item4/lane' in service.decode()
    assert 'WorkingDirectory='+v['state']+'/item4/repository' in lines
    assert [x for x in lines if x.startswith('ReadWritePaths=')]==[x for x in primary if x.startswith('ReadWritePaths=')]
    assert 'Unit='+tag+'-item4.service' in timer.decode()
    assert next(x for x in lines if x.startswith('ExecStartPre=')).split('PYTHONPATH=')[1].split()[0]==v['release']
    with pytest.raises(ValueError,match='^EXPERIMENT_COMPANION_BACKEND_REQUIRED$'):
        promotion.service_configuration(v,tag,'analysis',companion=True)


@pytest.mark.skipif(os.geteuid()!=0,reason='Actual root-owned promotion and UID1003 reader')
def test_two_plan_promotion_both_root_hooks_repositories_and_rollback(tmp_path):
    args,p,receipt,selected,original,inv=install(tmp_path);root=args[0];v=receipt['layout'];before=base.old_state(root,inv)
    mapping=host.release_lanes(selected,filesystem_root=root)
    assert [row['item_number'] for row in mapping]==[6,4]
    assert len(v['units'])==4
    for row in mapping:
        assert host.selected(selected['runtime'],row['lane'],filesystem_root=root)==selected
        repo=base.bound(root,row['repository'])
        result=subprocess.run(['git','-C',str(repo),'rev-parse','HEAD'],user=1003,group=1003,extra_groups=[],capture_output=True,text=True)
        assert result.returncode==0,result.stderr
        assert result.stdout.strip()==args[3]
    record=base.bound(root,v['record']);files=base.read(record/'FILES.json')
    assert files[v['record']+'/experiment-lanes.json']['sha256']==base.sha(record/'experiment-lanes.json')
    assert (record/'experiment-plan.json').read_bytes()==p[6].read_bytes()
    assert (record/'experiment-plan-item4.json').read_bytes()==p[4].read_bytes()
    assert promotion.rollback(root,args[2])['status']=='PASS'
    assert all(not base.bound(root,'/etc/systemd/system/'+unit).exists() for unit in v['units'])
    assert all(base.bound(root,row['repository']).exists() for row in mapping)
    assert base.read(base.bound(root,promotion.POINTER))==base.read(args[7])
    assert base.tree_hashes(base.bound(root,base.RELEASE))==original
    base.verify_old(root,inv,before)


@pytest.mark.skipif(os.geteuid()!=0,reason='Root-selected path refusal')
@pytest.mark.parametrize('damage,code',[('unknown','UNSELECTED_MANUAL_RELEASE'),
    ('alias','SELECTED_LANE_ALIAS'),('map','SELECTED_LANE_FILE_CHANGED'),
    ('service','SELECTED_LANE_FILE_CHANGED'),('runtime','UNSELECTED_MANUAL_RELEASE'),
    ('plan','SELECTED_LANE_FILE_CHANGED'),('units','UNREGISTERED_SELECTED_LANES')])
def test_selected_map_refuses_unknown_or_changed_binding(tmp_path,damage,code):
    args,p,receipt,selected,_,_=install(tmp_path);root=args[0];v=receipt['layout'];lane=v['state']+'/item4/lane';record=base.bound(root,v['record'])
    if damage=='unknown':lane=v['state']+'/other/lane'
    elif damage=='alias':
        state=base.bound(root,v['state']);(state/'alias').mkdir();(state/'item4/lane').symlink_to(state/'alias',target_is_directory=True)
    elif damage=='map':(record/'experiment-lanes.json').write_bytes((record/'experiment-lanes.json').read_bytes()+b' ')
    elif damage=='service':base.bound(root,'/etc/systemd/system/'+v['units'][2]).write_text('changed synthetic service')
    elif damage=='runtime':base.bound(root,selected['runtime']).write_text('{}')
    elif damage=='plan':(record/'experiment-plan-item4.json').write_text('{}')
    else:
        selected['units']=selected['units'][:2];base.bound(root,promotion.POINTER).write_text(json.dumps(selected));lane=v['state']+'/lane'
    with pytest.raises(ValueError,match='^'+code+'$'):
        host.selected(selected['runtime'],lane,filesystem_root=root)


@pytest.mark.skipif(os.geteuid()!=0,reason='Actual companion state lifecycle checks')
@pytest.mark.parametrize('operation',['no_call','rollback','promotion'])
def test_companion_running_call_blocks_every_lifecycle_path(tmp_path,operation):
    args,p,receipt,selected,_,_=install(tmp_path);root=args[0];v=receipt['layout'];lane=base.bound(root,v['state']+'/item4/lane')
    ledger(lane,['RUNNING'],phase='MODEL_RUNNING')
    before=base.tree_hashes(root)
    code='INITIALIZED_LANE_REQUIRES_SEPARATE_REVIEWED_MIGRATION_NO_BUDGET_RESET' if operation=='promotion' else 'MODEL_CALL_IN_PROGRESS_OR_UNCERTAIN'
    with pytest.raises(ValueError,match='^'+code+'$'):
        if operation=='no_call':promotion.no_call(root,v['state'],host.release_lanes(selected,filesystem_root=root))
        elif operation=='rollback':promotion.rollback(root,args[2])
        else:promotion.require_uninitialized_lane(root)
    assert base.tree_hashes(root)==before


@pytest.mark.skipif(os.geteuid()!=0,reason='Actual all-unit rollback guard')
@pytest.mark.parametrize('unit_index',[0,1,2,3])
def test_any_active_current_unit_refuses_rollback_before_write(tmp_path,unit_index):
    args,p,receipt,selected,_,_=install(tmp_path);root=args[0];v=receipt['layout']
    path=root/'run/manual-deploy-test-units.json';value=json.loads(path.read_text())
    value['units'][v['units'][unit_index]]={'active':True,'enabled':False};path.write_text(json.dumps(value))
    before=base.tree_hashes(root)
    with pytest.raises(ValueError,match='^NEW_SERVICE_ACTIVE_STOP_RECONCILE$'):promotion.rollback(root,args[2])
    assert base.tree_hashes(root)==before


@pytest.mark.skipif(os.geteuid()!=0,reason='Real UID1003 reader observation boundary')
@pytest.mark.parametrize('count',[20,30,31])
def test_owner_reader_observes_current_call_allowance_without_truncation(tmp_path,count):
    tmp_path.chmod(0o710);os.chown(tmp_path,0,1003);lane=tmp_path/'lane';ledger(lane,['COMPLETE']*count)
    before={p.name:p.read_bytes() for p in lane.iterdir()}
    if count==31:
        with pytest.raises(ValueError,match='^UNPRIVILEGED_LANE_READ_FAILED$'):host.lane_state(lane)
    else:assert host.lane_state(lane)==({'phase':'WAIT_OUTPUTS'},['COMPLETE']*count)
    assert before=={p.name:p.read_bytes() for p in lane.iterdir()}


@pytest.mark.skipif(os.geteuid()!=0,reason='Exact plan pair preflight')
@pytest.mark.parametrize('damage,code',[
    ('primary4','EXPERIMENT_COMPANION_REQUIRES_PRIMARY_ITEM6'),
    ('companion6','EXPERIMENT_COMPANION_REQUIRES_ITEM4'),
    ('unbound','REVIEWED_EXPERIMENT_PLAN_REQUIRED'),
    ('occupied','EXPERIMENT_AUTHORING_REQUIRES_EMPTY_ROOT_HOLD')])
def test_companion_preflight_refuses_before_first_promotion_write(tmp_path,damage,code):
    args,p,_,_=prepare(tmp_path);primary=p[6];companion=p[4]
    if damage=='primary4':primary=p[4]
    elif damage=='companion6':companion=p[6]
    elif damage=='unbound':p[4].write_bytes(p[4].read_bytes()+b' ')
    else:
        hold=base.bound(args[0],'/var/lib/synthetic-item4-selection');pr.write_text(hold/'READY.json','{}')
    before=base.tree_hashes(args[0])
    with pytest.raises(ValueError,match='^'+code+'$'):
        promotion.promote(*args,entrypoint='experiment',experiment_plan=primary,experiment_companion_plan=companion)
    assert base.tree_hashes(args[0])==before


def test_live_host_hook_cli_does_not_accept_scratch_root():
    script=Path(host.__file__).resolve()
    result=subprocess.run(['/usr/bin/python3','-s','-B',str(script),'before',
        '--runtime','/synthetic/runtime.json','--lane','/synthetic/lane',
        '--filesystem-root','/synthetic/scratch'],capture_output=True,text=True)
    assert result.returncode==2
    assert 'unrecognized arguments: --filesystem-root /synthetic/scratch' in result.stderr
