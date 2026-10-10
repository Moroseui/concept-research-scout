"""Refusal and immutable-receipt tests; real author bytes exercised by cold test."""
import copy,json,subprocess
from pathlib import Path
from types import SimpleNamespace
import pytest
from orchestrator import item4_spec_regression as s,notebook_synthetic as ns,private_records as pr

@pytest.fixture
def authored(monkeypatch):
    baseline=("def _native_diagnostic_fixture():\n return 1\ndef synthetic_tests():\n class Checks:\n  def test_old(self): pass\n"+s.ANCHOR+"\n").encode()
    current=baseline.replace(b'return 1',b'return 2')
    method=b'  def test_report_lifecycle(self): pass\n'
    runner=b'print("author-owned runner")\n'
    spec=b'```python\n'+method+b'```\n```python\n'+runner+b'```\n'
    for key,raw in [('SPEC',spec),('MODULE',current),('BASELINE',baseline),('METHOD',method),('RUNNER',runner)]:
        monkeypatch.setattr(s,key,s.sha(raw))
    submission=s.canonical({'files':{'SPEC.proposed.md':s.SPEC},'bindings':{'call_id':s.CALL,'round':23,'stage':'run_spec_author'}})
    monkeypatch.setattr(s,'SUBMISSION',s.sha(submission))
    return [spec,submission,current,baseline]

def test_exact_authored_blocks_and_temporary_copy(authored):
    original=list(authored);files,derived=s.authenticate(*authored)
    assert authored==original and files['current.py']==original[2]
    assert files['report_lifecycle_regression.py']==b'print("author-owned runner")\n'
    assert derived.count(b'def test_report_lifecycle')==1
    assert b'def test_old' in derived

@pytest.mark.parametrize('index',range(4))
def test_changed_author_bytes_refused(authored,index):
    authored[index]+=b' '
    with pytest.raises(ValueError,match='AUTHOR_BYTES_CHANGED'):s.authenticate(*authored)

@pytest.mark.parametrize('field,value',[('round',24),('stage','run_spec_review'),('call_id','0'*64)])
def test_wrong_submission_binding_even_when_hash_pinned(authored,monkeypatch,field,value):
    record=json.loads(authored[1]);record['bindings'][field]=value;authored[1]=s.canonical(record)
    monkeypatch.setattr(s,'SUBMISSION',s.sha(authored[1]))
    with pytest.raises(ValueError,match='SUBMISSION_BINDING'):s.authenticate(*authored)

def test_changed_old_tests_refused(authored,monkeypatch):
    authored[2]=authored[2].replace(b'def test_old',b'def test_replaced')
    monkeypatch.setattr(s,'MODULE',s.sha(authored[2]))
    with pytest.raises(ValueError,match='ORIGINAL_AST_CHANGED'):s.authenticate(*authored)

def test_unbound_runner_refused(authored,monkeypatch):
    monkeypatch.setattr(s,'RUNNER','0'*64)
    with pytest.raises(ValueError,match='SUBMITTED_CODE_BLOCKS'):s.authenticate(*authored)

@pytest.fixture
def isolated(tmp_path,monkeypatch):
    folder=tmp_path/'run';files={'run.py':s.ENTRY,'current.py':b'original'}
    config={'environment_root':'test-only','environment_sha256':'0'*64};calls=[]
    # Private-record owner policy is orthogonal here; actual UID1003/namespace
    # execution is covered by the captured service-account cold integration.
    monkeypatch.setattr(pr,'check',lambda p:Path(p));monkeypatch.setattr(pr,'check_tree',lambda p:None)
    def command(cfg,package,workspace,pins):
        assert cfg==config and pins=={n:s.sha(raw) for n,raw in files.items()}
        calls.append('existing-command');return ['synthetic-test-command']
    monkeypatch.setattr(ns,'command',command)
    def run(argv,**kw):
        assert argv==['synthetic-test-command'] and kw['timeout']==120 and kw['stdin']==subprocess.DEVNULL
        calls.append('execution')
        (folder/'workspace/isolation.json').write_bytes(s.canonical(dict(status='ISOLATED',network='UNSHARED',credentials=False,
            patient_mounts=False,package_read_only=True,workspace_writable=True)))
        return SimpleNamespace(returncode=0,stdout=s.canonical(s.RESULT)+b'\n',stderr=b'')
    monkeypatch.setattr(subprocess,'run',run)
    return folder,files,config,calls

def test_existing_confinement_then_terminal_reuse(isolated):
    folder,files,config,calls=isolated
    receipt=s.execute(folder,files,config)
    before={str(p):p.read_bytes() for p in folder.rglob('*') if p.is_file()}
    assert s.execute(folder,files,config)==receipt
    assert calls==['existing-command','execution']
    assert before=={str(p):p.read_bytes() for p in folder.rglob('*') if p.is_file()}

@pytest.mark.parametrize('name',['stdout.log','package/current.py','workspace/isolation.json'])
def test_tampered_evidence_refused_no_retry(isolated,name):
    folder,files,config,calls=isolated;s.execute(folder,files,config)
    (folder/name).write_bytes((folder/name).read_bytes()+b' ')
    with pytest.raises(ValueError,match='EVIDENCE_CHANGED'):s.execute(folder,files,config)
    assert calls==['existing-command','execution']

def test_extra_file_refused(isolated):
    folder,files,config,calls=isolated;s.execute(folder,files,config);(folder/'extra').write_bytes(b'')
    with pytest.raises(ValueError,match='RECEIPT_MEMBERS'):s.execute(folder,files,config)

def test_incomplete_intent_never_reexecutes(isolated):
    folder,files,config,calls=isolated;folder.mkdir()
    with pytest.raises(ValueError,match='INCOMPLETE_RECONCILE'):s.execute(folder,files,config)
    assert calls==[]

def test_different_environment_refused(isolated):
    folder,files,config,calls=isolated;s.execute(folder,files,config)
    with pytest.raises(ValueError,match='RECEIPT_BINDING'):s.execute(folder,files,{**config,'environment_sha256':'1'*64})
    assert calls==['existing-command','execution']

@pytest.mark.parametrize('field,value',[('status','FAIL'),('exit_code',1),('result',{}),('isolation',{})])
def test_failure_receipt_never_becomes_pass(isolated,field,value):
    folder,files,config,calls=isolated;r=s.execute(folder,files,config);r[field]=value
    (folder/'receipt.json').write_bytes(s.canonical(r))
    with pytest.raises(ValueError):s.execute(folder,files,config)
    assert calls==['existing-command','execution']

def test_original_strict_guard_still_required():
    def refuse(*args):raise ValueError('ORIGINAL_GUARD_REFUSED')
    with pytest.raises(ValueError,match='ORIGINAL_GUARD_REFUSED'):
        # Pin substitution represents authenticated input only for this boundary test.
        from unittest.mock import patch
        with patch.object(s,'sha',return_value=s.MODULE):
            s.equivalent(refuse,b'exact',{},b'derived',{'status':'PASS','result':s.RESULT})

@pytest.fixture
def installed(tmp_path,monkeypatch):
    from tools import item4_spec_regression_recovery as r
    from orchestrator import autonomy_review as ar
    root=tmp_path/'candidate';record=tmp_path/'record';review=record/'review';review.mkdir(parents=True)
    runtime=tmp_path/'runtime.json';runtime.write_bytes(b'{}');prior=tmp_path/'prior.py';prior.write_bytes(b'prior')
    b={'operator_decision_sha256':r.sha(b'operator'),'prior_runtime_sha256':r.sha(b'prior')}
    bodies={name:b'body' for name in r.FILES};bodies[r.DOC]=r.canonical(b);bodies[r.FILES[-1]]=b'operator'
    for name,raw in bodies.items():
        p=root/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(raw)
    files={n:r.sha(raw) for n,raw in bodies.items()}
    v={'schema':'reviewed-spec-regression-recovery/v1','root':str(root),'source':'a'*40,'review_folder':str(review),
       'review_sha256':'b'*64,'files':files}
    (record/'installed.json').write_bytes(r.canonical(v));(review/'packet-manifest.json').write_bytes(r.canonical({'source_files':files}))
    a={'verdict':'APPROVE','change_id':r.CHANGE,'source_sha':v['source'],'report_sha256':v['review_sha256'],'runtime_sha256':r.sha(b'{}')}
    for key,val in [('ROOT',root),('RECORD',record),('RUNTIME',runtime),('PRIOR',prior),('BINDING',r.sha(bodies[r.DOC]))]:monkeypatch.setattr(r,key,val)
    monkeypatch.setattr(r,'trusted',lambda p:Path(p));monkeypatch.setattr(ar,'verify_result',lambda p:a)
    return r,a,v,b

def test_exact_independent_approval_required(installed):
    r,a,v,b=installed;assert r.verified()==(v,b)

@pytest.mark.parametrize('field,value',[('verdict','REVISE'),('verdict','REJECT'),('change_id','other'),('source_sha','c'*40),('report_sha256','d'*64),('runtime_sha256','e'*64)])
def test_bad_approval_refuses_before_install_or_execution(installed,field,value):
    r,a,v,b=installed;a[field]=value
    with pytest.raises(ValueError,match='GENUINE_APPROVE'):r.verified()

@pytest.mark.parametrize('target',['code','binding','authority','prior','manifest'])
def test_modified_installed_inputs_refuse(installed,target):
    r,a,v,b=installed
    p={'code':r.ROOT/r.FILES[0],'binding':r.ROOT/r.DOC,'authority':r.ROOT/r.FILES[-1],
       'prior':r.PRIOR,'manifest':r.RECORD/'review/packet-manifest.json'}[target]
    if target=='manifest':
        data=json.loads(p.read_bytes());data['source_files'][r.FILES[0]]='0'*64;p.write_bytes(r.canonical(data))
    else:p.write_bytes(p.read_bytes()+b' ')
    with pytest.raises(ValueError):r.verified()

@pytest.mark.parametrize('field,value',[('ActiveState','active'),('MainPID','17'),('ControlGroup','/live'),('ExecMainStatus','0'),('InvocationID','different')])
def test_nonterminal_or_different_original_unit_refused(monkeypatch,field,value):
    from tools import item4_spec_regression_recovery as r
    values={'ActiveState':'failed','MainPID':'0','ControlGroup':'','ExecMainStatus':'1','InvocationID':r.INVOCATION}
    values[field]=value
    monkeypatch.setattr(subprocess,'check_output',lambda *a,**k:'\n'.join(k+'='+v for k,v in values.items()))
    with pytest.raises(ValueError,match='ORIGINAL_INVOCATION_NOT_TERMINAL'):r.stopped()
