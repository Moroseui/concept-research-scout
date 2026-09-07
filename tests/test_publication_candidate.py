"""The protected receiver independently rejects unsafe intermediate history."""
import hashlib
from pathlib import Path
import subprocess
import pytest
from orchestrator.publication_candidate import prepare,receive


def git(root,*args):
    return subprocess.check_output(['git','-c','user.name=Synthetic Agent',
        '-c','user.email=fixture@invalid',*args],cwd=root,stderr=subprocess.PIPE).decode().strip()


def repositories(tmp_path):
    author=tmp_path/'author';author.mkdir();git(author,'init','-q')
    (author/'README.md').write_text('Public fixture baseline\n')
    git(author,'add','README.md');git(author,'commit','-qm','Baseline')
    before=git(author,'rev-parse','HEAD')
    cache=tmp_path/'cache';git(tmp_path,'clone','-q','--no-local',str(author),str(cache))
    return author,cache,before


def test_safe_candidate_roundtrip_and_no_publication(tmp_path):
    author,cache,before=repositories(tmp_path)
    (author/'README.md').write_text('Permitted infrastructure update\n')
    git(author,'commit','-qam','Update');source=git(author,'rev-parse','HEAD')
    bundle=tmp_path/'source.bundle';request=prepare(author,source,before,bundle)
    result=receive(cache,source,before,request['inventory'],bundle.read_bytes(),request['bundle_sha256'])
    assert result['status']=='STAGED_NOT_PUBLISHED'
    assert git(cache,'rev-parse','HEAD')==source
    assert (cache/'README.md').read_text()=='Permitted infrastructure update\n'
    with pytest.raises(ValueError,match='BUNDLE_CHANGED'):
        receive(cache,source,before,request['inventory'],bundle.read_bytes()+b'changed',request['bundle_sha256'])


def test_deleted_secret_history_rejected_at_both_boundaries(tmp_path):
    author,cache,before=repositories(tmp_path)
    (author/'credential.txt').write_text('gh'+'p_'+'x'*40)
    git(author,'add','credential.txt');git(author,'commit','-qm','Unsafe intermediate')
    (author/'credential.txt').unlink();git(author,'commit','-qam','Delete unsafe intermediate')
    source=git(author,'rev-parse','HEAD');bundle=tmp_path/'unsafe.bundle'
    with pytest.raises(ValueError,match='CONTENT_REJECTED'):
        prepare(author,source,before,bundle)
    assert not bundle.exists()
    # A caller bypassing sender preparation still cannot bypass the receiver audit.
    git(author,'bundle','create',str(bundle),'HEAD','^'+before)
    raw=bundle.read_bytes()
    with pytest.raises(ValueError,match='CONTENT_REJECTED'):
        receive(cache,source,before,{},raw,hashlib.sha256(raw).hexdigest())
    assert git(cache,'rev-parse','HEAD')==before


def test_bundle_creation_race_preserves_other_file(tmp_path,monkeypatch):
    import orchestrator.publication_candidate as module
    author,cache,before=repositories(tmp_path)
    (author/'README.md').write_text('safe update\n');git(author,'commit','-qam','Update')
    source=git(author,'rev-parse','HEAD');destination=tmp_path/'race.bundle'
    original=module.os.link
    def race(source_file,target):
        Path(target).write_bytes(b'Existing independent file')
        return original(source_file,target)
    monkeypatch.setattr(module.os,'link',race)
    with pytest.raises(ValueError,match='FRESH_EXTERNAL_BUNDLE'):
        prepare(author,source,before,destination)
    assert destination.read_bytes()==b'Existing independent file'


def test_broker_stages_candidate_without_any_credential_or_push(tmp_path,monkeypatch):
    import base64
    from test_protected_handover import broker
    author,cache,before=repositories(tmp_path)
    (author/'README.md').write_text('safe update\n');git(author,'commit','-qam','Update')
    source=git(author,'rev-parse','HEAD');bundle=tmp_path/'safe.bundle'
    request=prepare(author,source,before,bundle)
    private=tmp_path/'broker';private.mkdir();b=broker(private)
    b.config['publication_root']=str(cache)
    monkeypatch.setattr(b,'authentication',lambda:pytest.fail('staging must not request credentials'))
    result=b.handle({'operation':'stage_candidate','body':{
        **request,'bundle_base64':base64.b64encode(bundle.read_bytes()).decode()}},10001)
    assert result['status']=='STAGED_NOT_PUBLISHED'
    with pytest.raises(ValueError,match='NOT_AUTHORIZED'):
        b.handle({'operation':'publish','body':{}},10001)


@pytest.mark.parametrize('name',['*.md','question?.md','[abc].md'])
def test_glob_paths_cannot_materialize_legacy_baseline(tmp_path,name):
    author,cache,before=repositories(tmp_path)
    (author/name).write_text('Permitted text under ambiguous sparse pattern\n')
    git(author,'add','--',name);git(author,'commit','-qm','Ambiguous filename')
    source=git(author,'rev-parse','HEAD')
    with pytest.raises(ValueError,match='LITERAL_SPARSE_PATH_REQUIRED'):
        prepare(author,source,before,tmp_path/'bundle')
    assert not (tmp_path/'bundle').exists()



def test_sparse_trailing_whitespace_refused():
    from orchestrator.publication_candidate import sparse_paths
    with pytest.raises(ValueError,match='LITERAL_SPARSE_PATH_REQUIRED'):
        sparse_paths({'a'*40+':name.md ':'b'*64})
