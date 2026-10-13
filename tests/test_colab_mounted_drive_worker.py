import json
import os
from pathlib import Path
import socket
import subprocess
import sys
import time
import pytest
from tools import colab_mounted_drive_worker as w

def test_real_os_boundary_denies_parent_data_and_network(tmp_path, monkeypatch):
    drive = tmp_path / "Drive" / "MyDrive"
    drive.mkdir(parents=True)
    secret = drive / "synthetic.txt"; secret.write_text("synthetic only")
    root = tmp_path / "package"; root.mkdir()
    monkeypatch.setattr(w, "DRIVE", drive)
    observed = w.prepare_boundary(root, allow_install=False)
    assert observed["status"] == "PASS" and observed["parent_drive_still_mounted"]
    assert secret.read_text() == "synthetic only"
    assert observed["network_namespace"] != observed["parent_network_namespace"]
    server = socket.socket(); server.bind(("127.0.0.1", 0)); server.listen()
    try:
        port = server.getsockname()[1]
        code = """import os,socket,sys
from pathlib import Path
try: Path(sys.argv[1]).read_bytes()
except (FileNotFoundError,PermissionError): pass
else: raise AssertionError('Drive file accessible')
try: socket.create_connection(('127.0.0.1',int(sys.argv[2])),timeout=.5)
except OSError: pass
else: raise AssertionError('Parent network reachable')
assert Path(sys.argv[3]).is_file()
print('denials verified')
"""
        result = subprocess.run(w.isolated_argv([str(Path(sys.executable).resolve()),
            "-I", "-B", "-c", code, str(secret), str(port), str(root/"worker-boundary.json")], root),
            capture_output=True, text=True, timeout=10)
        assert result.returncode == 0, result.stderr
        assert "denials verified" in result.stdout
    finally:
        server.close()

def test_boundary_absence_stops_before_work(tmp_path, monkeypatch):
    drive = tmp_path/"Drive";drive.mkdir()
    root = tmp_path/"package";root.mkdir()
    monkeypatch.setattr(w,"DRIVE",drive)
    monkeypatch.setattr(w.shutil,"which",lambda _name:None)
    with pytest.raises(RuntimeError,match="required worker isolation"):
        w.prepare_boundary(root,allow_install=False)
    assert not (root/"worker-boundary.json").exists()

def test_invalid_root_refused(tmp_path):
    real=tmp_path/"real";real.mkdir()
    link=tmp_path/"alias";link.symlink_to(real)
    with pytest.raises(RuntimeError,match="Invalid isolated"):
        w.isolated_argv(["true"],link)

def test_real_control_catches_deliberately_unconfined_worker(tmp_path,monkeypatch):
    drive=tmp_path/"Drive";drive.mkdir()
    root=tmp_path/"package";root.mkdir()
    monkeypatch.setattr(w,"DRIVE",drive)
    monkeypatch.setattr(w,"isolated_argv",lambda args,root:args)
    with pytest.raises(RuntimeError,match="setup refused"):
        w.prepare_boundary(root,allow_install=False)
    assert drive.is_dir()

def test_setup_timeout_kills_its_descendant(tmp_path):
    root=tmp_path/"package";root.mkdir()
    heartbeat=root/"heartbeat"
    child="import pathlib,time; p=pathlib.Path(__import__('sys').argv[1]);\nwhile True: p.write_text(str(time.monotonic()));time.sleep(.03)"
    parent="import subprocess,sys,time;subprocess.Popen([sys.executable,'-c',sys.argv[1],sys.argv[2]]);time.sleep(20)"
    with pytest.raises(RuntimeError,match="setup timed out"):
        w.run_setup([str(Path(sys.executable).resolve()),"-c",parent,child,str(heartbeat)],root,.3)
    assert heartbeat.is_file()
    before=heartbeat.read_text();time.sleep(.15)
    assert heartbeat.read_text()==before
