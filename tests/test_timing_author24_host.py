import importlib.util,json,os,sys
from pathlib import Path
from types import SimpleNamespace as NS
import pytest
from tools import timing_author24_host as target
from tools import install_timing_author24_recovery as installer

@pytest.fixture
def host_fixture(tmp_path,monkeypatch):
    assert os.getuid()==0
    root=tmp_path/'installed';root.mkdir();(root/'tools').mkdir();record=tmp_path/'record';record.mkdir();unit=tmp_path/'unit';unit.write_bytes(b'unit')
    entry=root/'tools/timing_author24_host.py';entry.write_bytes(b'host');runtime=root/'tools/timing_author24_runtime.py';runtime.write_bytes(b'runtime')
    approval={'source_sha':'a'*40,'report_sha256':'b'*64,'verdict':'APPROVE'}
    installed={'files':{'tools/timing_author24_host.py':installer.sha(b'host'),'tools/timing_author24_runtime.py':installer.sha(b'runtime')},'units':{'/etc/systemd/system/research-'+installer.CHANGE+'.service':installer.sha(b'unit'),'/etc/systemd/system/research-'+installer.CHANGE+'-colab_preparation.service':installer.sha(b'colabunit')}}
    (record/'installed.json').write_text(json.dumps(installed));(record/'COMPLETE.json').write_text(json.dumps({'status':'INSTALLED_HELD','source':'a'*40,'scientific_calls':0,'provider_calls':0}))
    path=Path(installer.__file__).with_name('item4_response_host_operation.py');spec=importlib.util.spec_from_file_location('_actual_host_for_timing_test',path);host=importlib.util.module_from_spec(spec);spec.loader.exec_module(host)
    checked=[];ready=[];commands=[]
    host.authority=lambda review:({'hashes':{'original':'c'*64}},{'source_sha':'original'})
    host.hashes=lambda frozen:checked.append(dict(frozen['hashes']))
    host.starting_state=lambda frozen,approval:ready.append((frozen,approval)) or {'status':'GENUINE_OLD_READINESS'}
    host.command=lambda args,**kw:commands.append(args) or 'PRESERVED\n'
    caphost=NS(connect=lambda:host,OLD_REVIEW=tmp_path/'old-review')
    oldcolab=NS(connect=lambda key,transition:host,status=lambda key:{'transition':'d'*64,'phase':'run_spec_author'})
    rt=NS(ROOT=root,RECORD=record,SCIENCE=tmp_path/'original-science',PREPARATION=tmp_path/'original304',REPAIRED=tmp_path/'repaired9f3',CAP=tmp_path/'cap',CHANGE=installer.CHANGE,require=installer.require,trusted=lambda p:Path(p),authority=lambda:approval,load=lambda name,path:oldcolab if name.startswith('_original_colab') else caphost)
    monkeypatch.setattr(target,'runtime',lambda:rt);monkeypatch.setattr(target,'__file__',str(entry))
    return NS(root=root,record=record,host=host,rt=rt,approval=approval,checked=checked,ready=ready,commands=commands)

def test_original_host_methods_limits_and_exact_successor_preserved(host_fixture):
    x=host_fixture;methods={n:getattr(x.host,n) for n in ['start','pulse','live','safe_stop','terminal']};h=target.connect()
    assert all(getattr(h,n) is method for n,method in methods.items())
    assert h.MAX_SECONDS==3700 and h.MAX_REFRESHES==62
    assert h.UNIT=='research-'+installer.CHANGE+'.service' and h.ENTRY==x.root/'tools/timing_author24_runtime.py' and h.OPERATION_ROOT==x.record/'operation'
    frozen,approval=h.authority('caller-path-ignored');assert approval==x.approval
    assert frozen['hashes']['original']=='c'*64 and '/etc/systemd/system/'+h.UNIT in frozen['hashes']
    assert str(x.root/'tools/timing_author24_host.py') in frozen['hashes']
    assert h.starting_state(frozen,approval)=={'status':'GENUINE_OLD_READINESS'}
    assert len(x.ready)==1 and len(x.commands)==1
    args=x.commands[0];assert args[:3]==['runuser','-u','partho'] and 'python3' in args and args[-2]==str(x.rt.SCIENCE) and args[-1]==str(h.ENTRY)
    assert 'm.preservation()' in args[args.index('-c')+1]

def test_absent_archive_refuses_before_start(host_fixture):
    x=host_fixture;x.host.command=lambda *a,**kw:'MISSING';h=target.connect()
    with pytest.raises(ValueError,match='PRESERVATION_PRESTART_REQUIRED'):h.starting_state({},x.approval)

def test_unverified_install_refuses(host_fixture):
    x=host_fixture;(x.record/'COMPLETE.json').write_text('{}')
    with pytest.raises(ValueError,match='SERVICE_VERIFICATION_REQUIRED'):target.connect()

def test_wrong_unit_binding_refuses(host_fixture):
    x=host_fixture;p=x.record/'installed.json';v=json.loads(p.read_text());v['units']={'unknown':'d'*64};p.write_text(json.dumps(v))
    with pytest.raises(ValueError,match='EXACT_SUCCESSOR_UNIT'):target.connect()

@pytest.mark.parametrize('args',[[],['stop'],['start','--review','anything'],['pulse','author']])
def test_no_extra_action_or_caller_review(args):
    with pytest.raises(ValueError,match='ACTION_SCOPE'):target.main(args)

def test_main_preserves_original_cli_scope(host_fixture,monkeypatch):
    x=host_fixture;seen=[]
    x.host.main=lambda:seen.append(list(sys.argv));before=list(sys.argv);target.main(['pulse'])
    assert sys.argv==before and seen[0][1:4]==['pulse','--stage','author'] and seen[0][-1].endswith('/'+installer.CHANGE+'/review')


def test_colab_reuses_original_methods_with_exact_transition_and_ready_check(host_fixture):
    x=host_fixture;methods={n:getattr(x.host,n) for n in ['start','pulse','live','safe_stop','terminal']};transition='d'*64
    h=target.connect_colab(transition)
    assert all(getattr(h,n) is method for n,method in methods.items())
    assert h.MAX_SECONDS==3700 and h.MAX_REFRESHES==62
    assert h.UNIT=='research-'+installer.CHANGE+'-colab_preparation.service'
    assert h.ENTRY==x.root/'tools/preparation_mechanical_continuation.py'
    assert h.OPERATION_ROOT==x.record/'operations/colab_preparation'/transition
    assert h.starting_state({},x.approval)=={'status':'GENUINE_OLD_READINESS'}
    args=x.commands[-1];assert args[-1]=='ready-colab' and 'PYTHONPATH='+str(x.rt.PREPARATION) in args
    assert args[:3]==['runuser','-u','partho']

def test_colab_missing_unit_binding_refuses(host_fixture):
    x=host_fixture;p=x.record/'installed.json';v=json.loads(p.read_text());v['units'].pop('/etc/systemd/system/research-'+installer.CHANGE+'-colab_preparation.service');p.write_text(json.dumps(v))
    with pytest.raises(ValueError,match='EXACT_COLAB_SUCCESSOR_UNIT'):target.connect_colab('d'*64)

def test_colab_main_fixed_transition_and_operation_root(host_fixture):
    x=host_fixture;seen=[];x.host.main=lambda:seen.append(list(sys.argv));transition='d'*64
    target.main(['start','--lane','colab_preparation','--transition',transition])
    assert len(seen)==1 and seen[0][1:4]==['start','--stage','author']
    assert (x.record/'operations/colab_preparation'/transition).is_dir()
    with pytest.raises(ValueError,match='TRANSITION_REQUIRED'):target.main(['start','--lane','colab_preparation','--transition','arbitrary'])

def test_colab_status_is_bound_read_only(host_fixture,capsys):
    target.main(['status','--lane','colab_preparation'])
    assert json.loads(capsys.readouterr().out)['transition']=='d'*64
    assert not (host_fixture.record/'operations').exists()
