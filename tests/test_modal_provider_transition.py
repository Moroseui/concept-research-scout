import hashlib,importlib.util,json
from pathlib import Path
from types import SimpleNamespace as NS
import pytest
from tools import modal_provider_transition as entry


def test_single_transition_uses_explicit_provider_factory(tmp_path):
    calls=[]
    entry.advance_once(tmp_path,factory=lambda state:NS(advance=lambda:calls.append(state) or {'phase':'WAIT_OUTPUTS'}))
    assert calls==[tmp_path]


def test_entry_passes_provider_to_both_driver_and_cleanup(monkeypatch,tmp_path):
    (tmp_path/'lane.json').write_text(json.dumps({'modal':{'pinned':'yes'}}));created=[]
    class Provider:
        def __init__(self,c):self.config=c
    monkeypatch.setattr(entry,'load_provider',lambda folder:Provider)
    monkeypatch.setattr(entry.modal_driver,'ModalDriver',lambda state,provider:created.append(provider.config) or NS(advance=lambda:{'phase':'WAIT_OUTPUTS'}))
    def supervise(state,preparation,**kw):
        assert kw['provider_factory'] is Provider
        return kw['run'](state,factory=kw['factory'])
    monkeypatch.setattr(entry.modal_driver,'supervise',supervise)
    monkeypatch.setattr('sys.argv',['entry','--state',str(tmp_path),'--preparation',str(tmp_path/'prep')])
    entry.main();assert created==[{'pinned':'yes'}]


def test_component_loader_refuses_untrusted_parent_before_import(tmp_path):
    # A user-owned scratch component is not an installed root-controlled provider.
    with pytest.raises(ValueError,match='^PROVIDER_COMPONENT_UNTRUSTED$'):entry.load_provider(tmp_path)



@pytest.mark.parametrize('damage',['approval','scope','hash','missing','none'])
def test_component_loader_bound_bytes_in_simulated_root_folder(tmp_path,monkeypatch,damage):
    import os
    body=b'class ModalProvider: pass\n';(tmp_path/'modal_provider.py').write_bytes(body)
    approval={'scope':'m3-image-preflight','verdict':'APPROVE','provider_sha256':hashlib.sha256(body).hexdigest()}
    if damage=='approval':approval['verdict']='REVISE'
    if damage=='scope':approval['scope']='OTHER'
    if damage=='hash':approval['provider_sha256']='0'*64
    if damage=='missing':(tmp_path/'modal_provider.py').unlink()
    (tmp_path/'approval-binding.json').write_text(json.dumps(approval))
    # Simulate root ownership/private ancestors; production uses real stat.
    original=Path.stat
    def trusted_stat(path,*a,**kw):
        values=list(original(path,*a,**kw));values[4]=0;values[0]&=~0o022
        return os.stat_result(values)
    monkeypatch.setattr(Path,'stat',trusted_stat)
    if damage in {'approval','scope'}:
        with pytest.raises(ValueError,match='^PROVIDER_COMPONENT_APPROVAL_SCOPE$'):entry.load_provider(tmp_path)
    elif damage=='hash':
        with pytest.raises(ValueError,match='^PROVIDER_COMPONENT_CHANGED$'):entry.load_provider(tmp_path)
    elif damage=='missing':
        with pytest.raises(ValueError,match='^PROVIDER_COMPONENT_UNTRUSTED$'):entry.load_provider(tmp_path)
    else:assert entry.load_provider(tmp_path).__name__=='ModalProvider'
