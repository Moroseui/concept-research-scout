"""Full private evidence reaches both routes; ordinary config limits stay small."""
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
from types import SimpleNamespace

import pytest

from orchestrator import handover_runtime as runtime, investigator_wakes as wakes
from orchestrator.handover_coordinator import digest


@pytest.fixture
def original_evidence(tmp_path, monkeypatch):
    """Real reads/size/hash validation; only protected ownership is simulated."""
    folder=tmp_path/'installed-evidence';folder.mkdir(mode=0o750)
    path=folder/'report-evidence.json'
    evidence={'source':'a'*40,'receipts':[],'task_state':{'fixture':'Private evidence boundary check'},
        'reviewer_evidence':{'original':'Preserved synthetic evidence. '*3900+'FINAL_ORIGINAL_MARKER'}}
    raw=(json.dumps(evidence,sort_keys=True)+'\n').encode();path.write_bytes(raw);path.chmod(0o640)
    assert 65536<len(raw)<750000
    fstat=os.fstat;path_stat=Path.stat
    def protected_file(fd):
        value=fstat(fd)
        return SimpleNamespace(st_uid=0,st_gid=os.getgid(),st_mode=value.st_mode,st_size=value.st_size)
    def protected_parent(p,*args,**kwargs):
        value=path_stat(p,*args,**kwargs)
        return SimpleNamespace(st_uid=0,st_gid=os.getgid(),st_mode=value.st_mode) if p==folder else value
    monkeypatch.setattr(runtime.os,'fstat',protected_file)
    monkeypatch.setattr(Path,'stat',protected_parent)
    monkeypatch.setattr(runtime,'checked_source',lambda root,source:Path(root))
    monkeypatch.setattr('orchestrator.research_catalog.linked_change',lambda *args:{'fixture':'review boundary supplied'})
    config={'source':'a'*40,'source_root':str(tmp_path),'controller_uid':os.getuid(),
        'controller_gid':os.getgid(),'state':str(tmp_path/'state'),'broker_socket':'fixture'}
    template={'schema':wakes.TEMPLATE,'template_id':'synthetic-charter','experiment':'P001',
        'request':'Inspect the unchanged supplied evidence.','evidence_file':str(path),
        'evidence_sha256':hashlib.sha256(raw).hexdigest(),'references':[],
        'change_request':{'request_id':'b'*64,'applied_event':'c'*64}}
    config['investigator']={'template':template,'template_sha256':digest(template)}
    config['report_schedule']={'zone':'UTC','hour':0,'minute':0,'evidence_file':str(path)}
    event=wakes.event('BOOTSTRAP',digest({'source':config['source'],'template_sha256':digest(template)}),digest(template))
    core={'schema':wakes.WAKE,'source':config['source'],'template_sha256':digest(template),'events':[event],'day':'2026-09-11'}
    return config,{**core,'identity':digest(core)},path,raw,evidence


@pytest.mark.parametrize('route',['investigator','report'])
def test_large_original_reaches_investigator_and_both_report_roles(original_evidence,route):
    config,manifest,path,raw,evidence=original_evidence
    with pytest.raises(ValueError,match='INSTALLED_CONFIG_REQUIRED'):
        runtime.configuration(path)  # The ordinary64KiB configuration limit is unchanged.
    if route=='investigator':
        derived=wakes.regenerate(config,manifest,lambda *args:pytest.fail('No provider or protected reply needed'))
        assert derived['evidence']['installed_charter_evidence']==evidence
        assert path.read_bytes()==raw
        return
    instance=runtime.Runtime(config)
    scheduled=instance.scheduled_report(datetime(2026,9,11,tzinfo=timezone.utc))
    assert scheduled['status']=='SCHEDULED'
    folder=instance.state/'tasks'/scheduled['task']
    packet=json.loads((folder/'packet.json').read_bytes())
    assert packet['reviewer_evidence']==evidence['reviewer_evidence']
    from orchestrator.hosted_context import envelope
    root=Path(__file__).resolve().parents[1]
    for family in ('codex','claude'):
        _,context=envelope(root,folder,'Inspect the preserved original evidence.',verified_source=config['source'],family=family)
        assert context['task_state']['reviewer_evidence']==evidence['reviewer_evidence']
    assert path.read_bytes()==raw
    assert instance.scheduled_report(datetime(2026,9,11,tzinfo=timezone.utc))['status']=='ALREADY_SCHEDULED'


def test_evidence_over_existing_private_bound_refuses_both_routes(original_evidence):
    config,manifest,path,_,evidence=original_evidence
    changed={**evidence,'reviewer_evidence':{'original':'x'*750000}}
    raw=(json.dumps(changed,sort_keys=True)+'\n').encode();path.write_bytes(raw)
    config['investigator']['template']['evidence_sha256']=hashlib.sha256(raw).hexdigest()
    template=config['investigator']['template'];config['investigator']['template_sha256']=digest(template)
    core={key:value for key,value in manifest.items() if key!='identity'};core['template_sha256']=digest(template)
    core['events']=[wakes.event('BOOTSTRAP',digest({'source':config['source'],'template_sha256':digest(template)}),digest(template))]
    with pytest.raises(ValueError,match='INSTALLED_CONFIG_REQUIRED'):
        wakes.regenerate(config,{**core,'identity':digest(core)},None)
    instance=runtime.Runtime(config)
    with pytest.raises(ValueError,match='INSTALLED_CONFIG_REQUIRED'):
        instance.scheduled_report(datetime(2026,9,11,tzinfo=timezone.utc))
    assert instance.q.db.execute('SELECT count(*) FROM tasks').fetchone()[0]==0
    assert path.read_bytes()==raw
