"""The protected dispatcher must reject oversized inputs before its admission."""
from pathlib import Path
import json
import pytest
from orchestrator.protected_handover import Broker


def case(tmp_path,monkeypatch,characters):
    from orchestrator import protected_handover as broker_module, hosted_context, hosted_cycle, remote_supervisor, operations_report
    b=object.__new__(Broker);root=tmp_path/'turns'
    b.config={'turn_root':str(root),'sources':['b'*40],'model_mode':'GOVERNED','max_model_turns':0,'policy':{}}
    b.ledger=object()
    from contextlib import nullcontext
    b.authentication=lambda:nullcontext()
    monkeypatch.setattr(broker_module.os,'getuid',lambda:0)
    monkeypatch.setattr(remote_supervisor,'checked_source',lambda *args:Path(args[0]))
    def private(path):
        path=Path(path);path.mkdir(parents=True,exist_ok=True);return path
    monkeypatch.setattr(operations_report,'private_root',private)
    def immutable(path,raw):
        if path.exists():
            assert path.read_bytes()==raw
        else:path.write_bytes(raw)
    monkeypatch.setattr(hosted_cycle,'immutable',immutable)
    calls=[]
    def compose(*args,**kwargs):
        assert kwargs['prepared_prompt'] is False and kwargs['output_format']=='markdown'
        calls.append('compose');return 'x'*characters,{'fixture':True}
    monkeypatch.setattr(hosted_context,'compose_input',compose)
    event={'turn_id':'a'*64,'attempt':'1','source':'b'*40,'branch':'astra/infrastructure-milestone-record','kind':'astra_turn'}
    folder=root/('a'*64+'-1')
    def admit(*args):
        assert (folder/'continuation.input-preflight.json').is_file()
        calls.append('admit');return {'status':'ADMITTED'}
    monkeypatch.setattr(broker_module,'admit_server',admit)
    def model(*args,**kwargs):
        calls.append('model');return 'fixture answer',{'stage':'continuation'}
    monkeypatch.setattr(hosted_cycle,'model_call',model)
    body={'event':event,'stage':'continuation','packet':{'trigger':'fixture'},'prompt':'fixture'}
    return b,body,folder,calls


def test_oversized_composition_is_preserved_without_admission_and_cannot_silently_retry(tmp_path,monkeypatch):
    b,body,folder,calls=case(tmp_path,monkeypatch,1048577)
    with pytest.raises(ValueError,match='FINAL_INPUT_TOO_LARGE'):b.model_stage(body)
    assert calls==['compose']
    refused=json.loads((folder/'continuation.input-refused.json').read_bytes())
    assert refused['provider_calls']==0 and refused['automatic_retry'] is False
    assert refused['measurement']['characters']==1048577
    assert not (folder/'continuation.started.json').exists()
    with pytest.raises(ValueError,match='INPUT_PREFLIGHT_RECONCILE'):b.model_stage(body)
    assert calls==['compose']


def test_dispatch_measures_actual_final_input_before_admission(tmp_path,monkeypatch):
    b,body,folder,calls=case(tmp_path,monkeypatch,1048576)
    assert b.model_stage(body)['status']=='COMPLETE'
    assert calls==['compose','admit','model']
    measurement=json.loads((folder/'continuation.input-preflight.json').read_bytes())
    assert measurement['characters']==1048576 and measurement['family']=='codex'
