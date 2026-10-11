import json
from pathlib import Path
from types import SimpleNamespace as NS
import pytest
from tools import colab_intake_identity_runtime as m


def test_unit_preserves_every_control_and_only_changes_entry():
    before=('ExecStart=/usr/bin/python3 -s -B '+str(m.BRANCH/'tools/preparation_branch_repair_runtime.py')+' advance --lane colab_preparation\n')
    safeguards='[Service]\nUser=partho\nGroup=partho\nNoNewPrivileges=true\nProtectSystem=strict\nPrivateTmp=true\nUMask=0077\nTimeoutStartSec=3700\n'
    raw=(safeguards+before).encode();changed=m.unit_bytes(raw)
    assert changed.decode().startswith(safeguards)
    assert str(m.ROOT/m.ENTRY).encode() in changed
    assert changed.replace(('ExecStart=/usr/bin/python3 -s -B '+str(m.ROOT/m.ENTRY)+' advance\n').encode(),before.encode())==raw
    with pytest.raises(ValueError):m.unit_bytes(raw+before.encode())
    with pytest.raises(ValueError):m.unit_bytes(raw.replace(b'colab_preparation',b'aggregate_analysis'))


@pytest.mark.parametrize('damage',['verdict','findings','scope','runtime','missing-source'])
def test_review_must_genuinely_approve_exact_scope_and_runtime(tmp_path,monkeypatch,damage):
    from orchestrator import autonomy_review
    runtime=tmp_path/'runtime.json';runtime.write_bytes(b'unchanged-config')
    manifest={'source_files':dict.fromkeys(m.REQUIRED,'b'*64)}
    approval={'verdict':'APPROVE','findings':[],'change_id':m.CHANGE,'runtime_sha256':m.sha(runtime.read_bytes())}
    if damage=='verdict':approval['verdict']='REVISE'
    elif damage=='findings':approval['findings']=[{'id':'unresolved'}]
    elif damage=='scope':approval['change_id']='other'
    elif damage=='runtime':approval['runtime_sha256']='0'*64
    else:manifest['source_files'].pop(m.RECOVERY)
    (tmp_path/'packet-manifest.json').write_text(json.dumps(manifest))
    monkeypatch.setattr(m,'RUNTIME',runtime);monkeypatch.setattr(m,'trusted',Path)
    monkeypatch.setattr(autonomy_review,'verify_result',lambda folder:approval)
    with pytest.raises(ValueError):m.reviewed(tmp_path)


def test_fixed_host_reuses_prior_start_state_checks_pulses_and_bounds(tmp_path,monkeypatch):
    root=tmp_path/'root';record=tmp_path/'record';record.mkdir();root.mkdir()
    monkeypatch.setattr(m,'ROOT',root);monkeypatch.setattr(m,'RECORD',record)
    monkeypatch.setattr(m,'os',NS(getuid=lambda:0));monkeypatch.setattr(m,'sys',NS(flags=NS(no_user_site=1),argv=['before']))
    monkeypatch.setattr(m,'trusted',Path);monkeypatch.setattr(m,'authority',lambda:{'report_sha256':'a'*64})
    monkeypatch.setattr(m,'original',lambda:None)
    installed={'units':{'/etc/systemd/system/'+m.UNIT:'u'},'files':{'one.py':'f'}}
    (record/'installed.json').write_text(json.dumps(installed))
    original_checks=object();events=[]
    h=NS(authority=lambda review:({'hashes':{'prior':'p'}},{}),hashes=lambda v:events.append(v),
         starting_state=original_checks,MAX_REFRESHES=62,MAX_SECONDS=3700)
    def run():
        assert h.starting_state is original_checks and (h.MAX_REFRESHES,h.MAX_SECONDS)==(62,3700)
        assert h.UNIT==m.UNIT and h.ENTRY==root/m.ENTRY
        assert h.OPERATION_ROOT==record/'operations'/('a'*64)
        assert m.sys.argv[1:] == ['pulse','--stage','author','--review',str(record/'review')]
        return {'status':'UNCHANGED_HOST_PULSE'}
    h.main=run
    old=NS(connect=lambda lane,transition:h)
    monkeypatch.setattr(m,'load',lambda name,path:old)
    assert m.host('pulse','a'*64)=={'status':'UNCHANGED_HOST_PULSE'}
    assert events[0]['hashes']=={'prior':'p',**installed['units'],str(root/'one.py'):'f'}
    assert m.sys.argv==['before']


def test_only_reviewed_intake_is_loaded_search_and_old_runtime_retained(tmp_path,monkeypatch):
    original=tmp_path/'original';root=tmp_path/'root'
    for p in [original/'orchestrator',root/'orchestrator']:p.mkdir(parents=True)
    (original/'orchestrator/scientific_intake.py').write_bytes(b'old intake')
    for p in [original,root]:(p/'orchestrator/scientific_search.py').write_bytes(b'same strict search')
    b={'original_intake_sha256':m.sha(b'old intake'),'original_search_sha256':m.sha(b'same strict search')}
    monkeypatch.setattr(m,'ORIGINAL',original);monkeypatch.setattr(m,'ROOT',root);monkeypatch.setattr(m,'trusted',Path)
    monkeypatch.setattr(m,'authority',lambda:None);prior=object()
    monkeypatch.setattr(m,'original',lambda:NS(connect=lambda:prior))
    monkeypatch.setattr(m,'recovery',lambda:NS(binding=lambda:b))
    seen=[];patched=NS()
    monkeypatch.setattr(m,'load',lambda name,path:(seen.append((name,path)) or patched))
    import orchestrator
    from orchestrator import scientific_intake
    monkeypatch.setattr(orchestrator,'scientific_intake',scientific_intake)
    assert m.connect() is prior
    assert seen==[('orchestrator.scientific_intake',root/'orchestrator/scientific_intake.py')]
    (root/'orchestrator/scientific_search.py').write_bytes(b'weakened')
    with pytest.raises(ValueError,match='SEARCH_GUARD_UNCHANGED'):m.connect()
