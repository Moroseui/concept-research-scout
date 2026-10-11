import json
from pathlib import Path
from types import SimpleNamespace as NS
import pytest
from tools import colab_intake_identity_runtime as m

@pytest.fixture
def predecessor(tmp_path,monkeypatch):
    intent=tmp_path/'START_INTENT.json';intent.write_text('preserved intent')
    journal=json.dumps({'charged_calls':0,'operational_refusal':'NETWORK_PREFLIGHT_FAILED_NO_CHARGE:claude','phase':'run_spec_review','calls_used':2})+'\n'
    terminal={'MainPID':'0','Result':'success','ExecMainStatus':'0','ActiveState':'inactive','SubState':'dead','InvocationID':''}
    b={'source':'a'*40,'review':'b'*64,'unit':'original.service','terminal':terminal,
       'host_records':{str(intent):{'sha256':m.sha(intent.read_bytes())}},'invocation':'original-invocation','journal_sha256':m.sha(journal.encode())}
    raw=json.dumps(b).encode();approved={'source_sha':b['source'],'report_sha256':b['review'],'change_id':'colab-timing-transport-repair-20261011'}
    monkeypatch.setattr(m,'NETWORK_SHA',m.sha(raw));monkeypatch.setattr(m,'trusted',Path)
    monkeypatch.setattr(m,'load',lambda *a:NS(authority=lambda:approved))
    monkeypatch.setattr(m,'os',NS(getuid=lambda:0))
    controls={'state':dict(terminal),'journal':journal};calls=[]
    def output(argv,**kwargs):
        calls.append(argv)
        if argv[0]=='systemctl':return '\n'.join(k+'='+v for k,v in controls['state'].items())
        assert argv==['journalctl','--no-pager','-o','cat','_SYSTEMD_INVOCATION_ID=original-invocation']
        return controls['journal']
    monkeypatch.setattr(m,'subprocess',NS(check_output=output))
    return NS(raw=raw,b=b,approved=approved,controls=controls,intent=intent,calls=calls)


def test_exact_terminal_zero_call_preserved_before_successor(predecessor):
    f=predecessor;before=f.intent.read_bytes()
    assert m.network_predecessor(f.raw)==f.b
    assert f.intent.read_bytes()==before
    assert [c[0] for c in f.calls]==['systemctl','journalctl']


@pytest.mark.parametrize('damage',['document','source','review','scope','live','exit','result','invocation','intent','journal','charged','wrong-refusal'])
def test_uncertain_changed_or_charged_predecessor_fails_closed(predecessor,monkeypatch,damage):
    f=predecessor;raw=f.raw
    if damage=='document':raw+=b' '
    elif damage in {'source','review','scope'}:f.approved[{'source':'source_sha','review':'report_sha256','scope':'change_id'}[damage]]='wrong'
    elif damage in {'live','exit','result','invocation'}:f.controls['state'][{'live':'MainPID','exit':'ExecMainStatus','result':'Result','invocation':'InvocationID'}[damage]]='changed'
    elif damage=='intent':f.intent.write_text('changed')
    elif damage=='journal':f.controls['journal']+='changed'
    else:
        j=json.loads(f.controls['journal'])
        if damage=='charged':j['charged_calls']=1
        else:j['operational_refusal']='genuine REVISE'
        f.controls['journal']=json.dumps(j)+'\n';f.b['journal_sha256']=m.sha(f.controls['journal'].encode())
        raw=json.dumps(f.b).encode();monkeypatch.setattr(m,'NETWORK_SHA',m.sha(raw))
    with pytest.raises(ValueError,match='NETWORK_'):m.network_predecessor(raw)


def test_service_checks_terminal_and_approval_without_reading_root_records(predecessor,monkeypatch):
    f=predecessor;monkeypatch.setattr(m,'os',NS(getuid=lambda:1003))
    assert m.network_predecessor(f.raw)==f.b
    assert [c[0] for c in f.calls]==['systemctl']


def test_successor_refuses_an_invented_transition(monkeypatch):
    monkeypatch.setattr(m,'os',NS(getuid=lambda:0));monkeypatch.setattr(m,'sys',NS(flags=NS(no_user_site=1)))
    monkeypatch.setattr(m,'authority',lambda:{})
    monkeypatch.setattr(m,'network_predecessor',lambda:{'transition':'a'*64})
    monkeypatch.setattr(m,'original',lambda:None)
    monkeypatch.setattr(m,'load',lambda *a:NS(connect=lambda *a:pytest.fail('must not construct a new host operation')))
    with pytest.raises(ValueError,match='EXACT_NETWORK_CONTINUATION'):m.host('start','b'*64)
