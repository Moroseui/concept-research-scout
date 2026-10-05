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


def sparse_metadata_cache(tmp_path,author,before):
    """Actual cache shape: all Git metadata, only one selected baseline blob."""
    cache=tmp_path/'sparse-cache';cache.mkdir();git(cache,'init','-q')
    names=git(author,'rev-list','--objects','--no-object-names',before).splitlines()
    objects=[oid for oid in names if git(author,'cat-file','-t',oid)!='blob']
    objects.append(git(author,'rev-parse',before+':README.md'))
    raw=subprocess.check_output(['git','pack-objects','--stdout','--window=0','--depth=0'],
        cwd=author,input=('\n'.join(objects)+'\n').encode())
    subprocess.run(['git','index-pack','--stdin','--promisor'],cwd=cache,input=raw,
        check=True,capture_output=True)
    git(cache,'update-ref','HEAD',before)
    git(cache,'sparse-checkout','set','--no-cone','/README.md')
    git(cache,'checkout','--detach',before)
    return cache


def test_sparse_transition_receives_exact_scanned_old_blob(tmp_path):
    author,unused,before=repositories(tmp_path)
    report=author/'docs/operations/daily/summary.md';report.parent.mkdir(parents=True)
    report.write_text('Original public report\n')
    (author/'unselected.txt').write_text('Unselected original stays out of transport\n')
    git(author,'add','.');git(author,'commit','-qm','Public baseline report')
    before=git(author,'rev-parse','HEAD');old=git(author,'rev-parse',before+':docs/operations/daily/summary.md')
    unselected=git(author,'rev-parse',before+':unselected.txt')
    cache=sparse_metadata_cache(tmp_path,author,before)
    assert subprocess.run(['git','cat-file','-e',old],cwd=cache,capture_output=True).returncode
    report.write_text('Revised public report\n');git(author,'commit','-qam','Report revision')
    source=git(author,'rev-parse','HEAD')
    # A non-delta ordinary bundle still lacks the old blob needed during
    # sparse-checkout set. Preserve the failed fixture before testing the fix.
    legacy=tmp_path/'legacy.bundle'
    git(author,'-c','pack.window=0','-c','pack.depth=0','bundle','create',str(legacy),'HEAD','^'+before)
    from orchestrator.publication_candidate import inventory
    entries=inventory(author,source,before)
    with pytest.raises(ValueError,match='CANDIDATE_GIT_OPERATION_FAILED'):
        receive(cache,source,before,entries,legacy.read_bytes(),hashlib.sha256(legacy.read_bytes()).hexdigest())
    assert git(cache,'rev-parse','HEAD')==before
    # A failed sparse transition can leave worktree removals behind. Preserve
    # it for reconciliation; the corrected proposal starts from a fresh exact
    # baseline fixture instead of overwriting or retrying that partial cache.
    corrected=tmp_path/'corrected';corrected.mkdir()
    cache=sparse_metadata_cache(corrected,author,before)
    fixed=tmp_path/'fixed.bundle';request=prepare(author,source,before,fixed)
    result=receive(cache,source,before,request['inventory'],fixed.read_bytes(),request['bundle_sha256'])
    assert result['status']=='STAGED_NOT_PUBLISHED'
    assert request['inventory']==entries
    assert git(cache,'rev-parse','HEAD')==source
    assert (cache/'docs/operations/daily/summary.md').read_text()=='Revised public report\n'
    assert git(cache,'cat-file','-e',old)==''
    assert subprocess.run(['git','cat-file','-e',unselected],cwd=cache,capture_output=True).returncode
    assert legacy.exists()


def test_pack_has_no_delta_bases_even_from_repacked_author(tmp_path):
    import random, string
    author,unused,before=repositories(tmp_path)
    rng=random.Random(71)
    content=''.join(rng.choice(string.ascii_letters+' ') for _ in range(60000))+'\n'
    (author/'report.txt').write_text(content)
    git(author,'add','.');git(author,'commit','-qm','Original report')
    before=git(author,'rev-parse','HEAD')
    (author/'report.txt').write_text(content[:30000]+'Revised evidence '+content[30017:])
    git(author,'commit','-qam','Small report revision');source=git(author,'rev-parse','HEAD')
    git(author,'repack','-adf','--window=250','--depth=50')
    index=next((author/'.git/objects/pack').glob('*.idx'))
    assert any(len(line.split())==7 for line in git(author,'verify-pack','-v',str(index)).splitlines())
    bundle=tmp_path/'safe.bundle';request=prepare(author,source,before,bundle)
    raw=bundle.read_bytes().split(b'\n\n',1)[1]
    pack=tmp_path/'checked.pack';pack.write_bytes(raw)
    git(author,'index-pack',str(pack))
    rows=git(author,'verify-pack','-v',str(pack.with_suffix('.idx'))).splitlines()
    assert not any(len(line.split())==7 for line in rows)
    cache=sparse_metadata_cache(tmp_path,author,before)
    result=receive(cache,source,before,request['inventory'],bundle.read_bytes(),request['bundle_sha256'])
    assert result['status']=='STAGED_NOT_PUBLISHED'


def test_unscanned_old_sparse_blob_refuses_before_bundle(tmp_path):
    author,unused,before=repositories(tmp_path)
    path=author/'older.txt';path.write_text('gh'+'p_'+'x'*40)
    git(author,'add','.');git(author,'commit','-qm','Unacceptable baseline input')
    before=git(author,'rev-parse','HEAD')
    path.write_text('Safe revision\n');git(author,'commit','-qam','Safe current text')
    source=git(author,'rev-parse','HEAD');bundle=tmp_path/'refused.bundle'
    with pytest.raises(ValueError,match='CONTENT_REJECTED'):
        prepare(author,source,before,bundle)
    assert not bundle.exists()
