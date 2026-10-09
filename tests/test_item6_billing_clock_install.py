import copy
import json
from pathlib import Path
import pytest
from tools import install_item6_billing_clock as i


def test_revision_only_changes_one_file_pin_and_genuine_new_approval():
    target=str(i.ROOT/i.TARGET)
    files={target:{'sha256':'old','mode':0o440},**{str(i.ROOT/('unchanged'+str(n))):{'sha256':str(n),'mode':0o440} for n in range(13)}}
    original={'source':'old','review_folder':'oldreview','review_sha256':'oldsha','files_sha256':'oldfiles',
              'change':'original-identity','layout':{'state':'original-state'},'config_sha256':'originalconfig','base_receipt_sha256':'originalbase'}
    before=copy.deepcopy((original,files))
    newfiles,rec=i.replacements(original,files,b'approved source','new','newreview',{'report_sha256':'newsha'})
    assert (original,files)==before
    assert {k:v for k,v in newfiles.items() if k!=target}=={k:v for k,v in files.items() if k!=target}
    assert newfiles[target]=={'sha256':i.sha(b'approved source'),'mode':0o440}
    assert {k:v for k,v in rec.items() if k not in {'change','source','review_folder','review_sha256','files_sha256'}}=={k:v for k,v in original.items() if k not in {'change','source','review_folder','review_sha256','files_sha256'}}
    assert rec['change']=='item6-billing-clock-20261008'
    assert rec['files_sha256']==i.sha(i.encoded(newfiles)) and rec['review_sha256']=='newsha'


@pytest.mark.parametrize('files',[{}, {str(i.ROOT/i.TARGET):{'sha256':'x','mode':0o440}}])
def test_unexpected_installed_file_set_refused(files):
    with pytest.raises(ValueError,match='FILE_SET'):i.replacements({},files,b'x','x','x',{})


@pytest.mark.parametrize('verdict,findings',[('REJECT',[]),('REVISE',[]),('APPROVE',[{'concern':'unresolved'}])])
def test_no_write_before_genuine_approval(tmp_path,monkeypatch,verdict,findings):
    monkeypatch.setattr(i.os,'getuid',lambda:0);monkeypatch.setattr(i.os,'geteuid',lambda:0)
    monkeypatch.setattr(i,'trusted',lambda p:Path(p))
    monkeypatch.setattr(i,'CHECKPOINT',tmp_path/'not-created')
    folder=tmp_path/'review';folder.mkdir();(folder/'packet-manifest.json').write_text('{}')
    monkeypatch.setattr(i.review,'verify_result',lambda p:{'verdict':verdict,'findings':findings,'source_sha':'commit'})
    monkeypatch.setattr(i.subprocess,'check_output',lambda args,**kw:'commit\n' if 'rev-parse' in args else '')
    before=sorted(str(p) for p in tmp_path.rglob('*'))
    with pytest.raises(ValueError,match='GENUINE_APPROVAL'):i.install(tmp_path,'commit',folder,tmp_path/'authority')
    assert sorted(str(p) for p in tmp_path.rglob('*'))==before


def test_existing_upgrade_checkpoint_refuses_replay(tmp_path,monkeypatch):
    monkeypatch.setattr(i.os,'getuid',lambda:0);monkeypatch.setattr(i.os,'geteuid',lambda:0)
    monkeypatch.setattr(i,'trusted',lambda p:Path(p));monkeypatch.setattr(i,'CHECKPOINT',tmp_path)
    with pytest.raises(ValueError,match='EXISTS_RECONCILE'):i.install(tmp_path,'commit',tmp_path,tmp_path)
