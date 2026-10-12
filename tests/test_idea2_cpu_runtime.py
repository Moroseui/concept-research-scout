import json,sqlite3
from pathlib import Path
from types import SimpleNamespace
import pytest
from tools import idea2_cpu_runtime as rt
from orchestrator import idea2_cpu_lane as lane,private_records as pr,cpu_isolation

def private(path):
    path.mkdir(mode=0o700,parents=True,exist_ok=True)
    return path

def test_actual_scope_and_installed_overlay_keep_accepted_lane_read_only(tmp_path):
    root=Path(rt.__file__).parents[1]
    scope=rt.metadata(root)
    for name in rt.ADDED:
        target=tmp_path/name;target.parent.mkdir(parents=True,exist_ok=True)
        target.write_bytes((root/name).read_bytes())
    assert rt.metadata(tmp_path)==scope
    proof=lane.frozen(tmp_path)
    assert json.loads(proof['state_row']['payload'])['phase']=='COMMIT_SPEC'
    assert len(proof['calls'])==15
    unit=rt.unit_bytes(scope).decode().splitlines()
    assert [x for x in unit if x.startswith('ReadWritePaths=')]==['ReadWritePaths='+str(rt.WORK)]
    for line in ('Restart=no','KillMode=control-group','PrivateNetwork=true','PrivateDevices=true',
                 'NoNewPrivileges=true','ProtectSystem=strict','ProtectHome=true','TimeoutStartSec=3900'):
        assert line in unit
    assert 'model_calls' not in str(rt.WORK)

def test_scope_hash_refuses_changed_timeout_or_spending(tmp_path):
    root=Path(rt.__file__).parents[1]
    scope=rt.metadata(root);scope['hard_timeout_seconds']=7200
    path=tmp_path/rt.DOCUMENT;path.parent.mkdir(parents=True);path.write_text(json.dumps(scope))
    with pytest.raises(ValueError,match='RUNTIME_SCOPE'):rt.metadata(tmp_path)

@pytest.mark.parametrize('writable_passes',[False,True])
def test_native_qualification_requires_both_readonly_and_writable_controls(tmp_path,monkeypatch,writable_passes):
    work=private(tmp_path/'work');monkeypatch.setattr(rt,'WORK',work)
    seen=[]
    def command(config,package,data,dest,**kwargs):
        assert kwargs['probe'] is True and kwargs['profile']=='diagnostics-fixed3x3'
        assert (package/'analysis.py').is_file() and (package/'contract.json').is_file()
        assert list(data.iterdir())[0].name=='synthetic.txt'
        return ['bwrap','--ro-bind',str(data),'/content/drive/MyDrive/isles-pilot']
    def run(argv,**kwargs):
        seen.append(argv)
        if argv[1]=='--ro-bind':return SimpleNamespace(returncode=0,stdout=b'ISOLATED',stderr=b'')
        return SimpleNamespace(returncode=0 if writable_passes else 1,stdout=b'',
            stderr=b'CPU_DIAGNOSTICS_INPUT_OR_PACKAGE_WRITABLE')
    monkeypatch.setattr(cpu_isolation,'command',command)
    monkeypatch.setattr(rt.subprocess,'run',run)
    if writable_passes:
        with pytest.raises(ValueError,match='WRITABLE_NEGATIVE_CONTROL'):
            rt.qualification({'cpu':{}},{'source_sha':'a'*40,'report_sha256':'b'*64})
        assert not (work/'qualification/COMPLETE.json').exists()
    else:
        result=rt.qualification({'cpu':{}},{'source_sha':'a'*40,'report_sha256':'b'*64})
        assert result['patient_payloads_opened']==result['model_calls']==0
        with pytest.raises(ValueError,match='QUALIFICATION_REPLAY'):
            rt.qualification({'cpu':{}},{'source_sha':'a'*40,'report_sha256':'b'*64})
    assert len(seen)==2 and seen[0][1]=='--ro-bind' and seen[1][1]=='--bind'

def test_execution_requires_native_controls_before_any_input_or_job(tmp_path,monkeypatch):
    monkeypatch.setattr(rt,'WORK',private(tmp_path/'work'))
    monkeypatch.setattr(lane,'read_accepted_lane',lambda *a:pytest.fail('read before qualification'))
    with pytest.raises(FileNotFoundError):rt.execute({},{})

def test_global_owner_and_scientific_calls_are_read_only_and_fail_closed(tmp_path):
    accepted=private(tmp_path/'lane');batch=private(tmp_path/'batch')
    binding={'original':'unchanged'}
    pr.write_text(accepted/'lane.json',json.dumps({'owner_binding':binding}))
    path=batch/'jobs.sqlite'
    db=sqlite3.connect(path);db.executescript('CREATE TABLE autonomy_runs(id TEXT,binding TEXT,status TEXT);CREATE TABLE autonomy_calls(id TEXT,status TEXT,change_id TEXT);')
    db.execute('INSERT INTO autonomy_runs VALUES(?,?,?)',('run',json.dumps(binding),'ACTIVE'))
    db.executemany('INSERT INTO autonomy_calls VALUES(?,?,?)',[(lane.AUTHOR_CALL,'COMPLETE','run'),(lane.REVIEW_CALL,'COMPLETE','run')]);db.commit();db.close();path.chmod(0o600)
    scope={'accepted_lane':str(accepted),'batch':str(batch),'run_id':'run'}
    value=rt.read_batch(scope)
    try:
        with pytest.raises(sqlite3.OperationalError):value.db.execute("UPDATE autonomy_runs SET status='COMPLETE'")
    finally:value.db.close()
    db=sqlite3.connect(path);db.execute("UPDATE autonomy_calls SET status='UNCERTAIN' WHERE id=?",(lane.REVIEW_CALL,));db.commit();db.close()
    with pytest.raises(ValueError,match='ACCEPTED_GLOBAL_CALL'):rt.read_batch(scope)

def test_full_reviewed_source_binding_includes_non_overlay_files(tmp_path,monkeypatch):
    from orchestrator import manual_host_guard
    root=private(tmp_path/"root");record=private(tmp_path/"record")
    entry=root/rt.ENTRY;entry.parent.mkdir();entry.write_bytes(b"# installed synthetic entry")
    dependency=root/"orchestrator/other_dependency.py";dependency.parent.mkdir();dependency.write_bytes(b"# reviewed dependency")
    runtime=tmp_path/"runtime.json";runtime.write_bytes(b"{}")
    scope={"runtime":str(runtime)}
    source_files={rt.ENTRY:rt.sha(entry.read_bytes()),"orchestrator/other_dependency.py":rt.sha(dependency.read_bytes())}
    approval={"source_sha":"a"*40,"report_sha256":"b"*64,"runtime_sha256":rt.sha(b"{}")}
    unit=tmp_path/"unit";unit.write_bytes(b"bound unit")
    (record/"INSTALLED.json").write_bytes(rt.encoded({"source":approval["source_sha"],"review_sha256":approval["report_sha256"],"files":source_files,"unit_sha256":rt.sha(unit.read_bytes())}))
    monkeypatch.setattr(rt,"ROOT",root);monkeypatch.setattr(rt,"RECORD",record)
    monkeypatch.setattr(rt,"__file__",str(entry))
    monkeypatch.setattr(rt,"reviewed",lambda *a:(approval,{"source_files":source_files}))
    monkeypatch.setattr(rt,"metadata",lambda:scope);monkeypatch.setattr(rt,"unit_bytes",lambda s:unit.read_bytes())
    monkeypatch.setattr(manual_host_guard,"trusted",lambda p:unit if str(p)=="/etc/systemd/system/"+rt.UNIT else Path(p))
    assert rt.authority()==(approval,scope)
    dependency.write_bytes(b"# changed outside old overlay")
    with pytest.raises(ValueError,match="INSTALLED_SOURCE_CHANGED"):rt.authority()
