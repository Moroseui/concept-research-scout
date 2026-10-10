"""Structural admission only; no scientific fixture is executed or repaired here."""
import ast,copy,json
from pathlib import Path
import pytest
from orchestrator import item4_fixture_correction as fixture

@pytest.fixture
def candidate():
    root=Path(__file__).parents[1]
    scope=json.loads((root/fixture.AUDIT_DOCUMENT).read_bytes())
    source=(root/fixture.AUDIT_REFERENCE).read_bytes();tree=ast.parse(source)
    block=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='_native_diagnostic_fixture')
    # An inert AST addition exercises the permission boundary, not the science.
    block.body.append(ast.Pass())
    suite=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='synthetic_tests')
    checks=next(n for n in suite.body if isinstance(n,ast.ClassDef) and n.name=='Checks')
    checks.body.append(ast.parse('def test_fixture_contract_boundary(self):\n    pass').body[0])
    return scope,source,tree,block,suite,checks

def encode(tree):return ast.unparse(ast.fix_missing_locations(tree)).encode()

def test_admits_fixture_change_and_additive_tests_without_claiming_success(candidate):
    scope,source,tree,*_=candidate
    result=fixture.correction(encode(tree),scope)
    assert result['production_ast_unchanged'] and result['existing_tests_unchanged']
    assert result['corrected_fixture_executed'] is False and result['scientific_acceptance'] is False
    assert result['added_contract_tests']==['test_fixture_contract_boundary']

@pytest.mark.parametrize('fault',['production','old-test','suite','duplicate-test','decorator','non-test','no-new-test','fixture-interface','no-fixture-change'])
def test_cannot_remove_old_checks_or_change_production(candidate,fault):
    scope,source,tree,block,suite,checks=candidate
    if fault=='production':
        next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='main').body.append(ast.Pass())
    elif fault=='old-test':checks.body[0].body.append(ast.Pass())
    elif fault=='suite':suite.body[-1]=ast.parse('return None').body[0]
    elif fault=='duplicate-test':checks.body[-1].name=checks.body[0].name
    elif fault=='decorator':checks.decorator_list=[ast.Name(id='changed',ctx=ast.Load())]
    elif fault=='non-test':checks.body[-1].name='helper'
    elif fault=='no-new-test':checks.body.pop()
    elif fault=='fixture-interface':block.args.args.append(ast.arg(arg='new_argument'))
    else:block.body.pop()
    with pytest.raises(ValueError):fixture.correction(encode(tree),scope)

@pytest.mark.parametrize('key,value',[('author_only',False),('direction_sha256','0'*64),('reference_native_harness_sha256','0'*64)])
def test_scope_substitution_refused(candidate,key,value):
    scope,*_=candidate;scope[key]=value
    with pytest.raises(ValueError):fixture.scope(scope)

@pytest.fixture
def failed_history(monkeypatch,tmp_path):
    import sqlite3
    from types import SimpleNamespace as NS
    root=Path(__file__).parents[1]
    scopes=[json.loads((root/name).read_bytes()) for name in (fixture.DOCUMENT,fixture.AUDIT_DOCUMENT)]
    db=sqlite3.connect(':memory:');db.row_factory=sqlite3.Row
    rows=[p['native_failure']['asset_row'] for p in scopes]
    db.execute('CREATE TABLE autonomy_assets ('+','.join(k+(' INTEGER' if isinstance(v,int) else ' REAL' if isinstance(v,float) else ' TEXT') for k,v in rows[0].items())+')')
    for row in rows:db.execute('INSERT INTO autonomy_assets ('+','.join(row)+') VALUES('+','.join('?' for _ in row)+')',list(row.values()))
    monkeypatch.setattr(fixture,'ROOT',tmp_path)
    old=tmp_path/fixture.DOCUMENT;old.parent.mkdir(parents=True)
    monkeypatch.setattr(fixture,'STATE',tmp_path/'first');monkeypatch.setattr(fixture,'AUDIT_STATE',tmp_path/'second')
    proofs=[]
    for scope in scopes:
        q=fixture.parameters(scope);f=scope['native_failure']
        for name in f['files']:
            path=q['state']/name;path.parent.mkdir(parents=True,exist_ok=True)
            raw=('synthetic preserved '+q['asset']+'/'+name).encode();path.write_bytes(raw);f['files'][name]=fixture.sha(raw)
        proofs.append({'source':f['source'],'implementation_review_sha256':f['implementation_review_sha256'],
            'asset_id':q['asset'],'module_sha256':q['module'],'exit_code':1,'status':'FAIL',
            'package_unchanged':True,'scientific_acceptance':False,'no_automatic_retry':True})
    old.write_text(json.dumps(scopes[0]))
    monkeypatch.setattr(fixture,'_verifier',lambda:proofs[0])
    monkeypatch.setattr(fixture,'_audit_verifier',lambda:proofs[1])
    yield NS(store=NS(batch=NS(db=db)),db=db,p=scopes[1],proofs=proofs,paths=[fixture.STATE,fixture.AUDIT_STATE])
    db.close()

def test_both_failures_must_be_exact_and_retained(failed_history):
    h=failed_history
    assert fixture.failure(h.store,h.p)==h.p['native_failure']

@pytest.mark.parametrize('attempt',[0,1])
@pytest.mark.parametrize('fault',['bytes','reservation','status','fake-pass'])
def test_neither_original_failure_can_be_relabelled_or_released(failed_history,attempt,fault):
    h=failed_history;proof=h.proofs[attempt]
    if fault=='bytes':(h.paths[attempt]/'provider/stdout.bin').write_bytes(b'PASS')
    elif fault=='reservation':h.db.execute('UPDATE autonomy_assets SET reserved_micro_usd=0 WHERE id=?',(proof['asset_id'],))
    elif fault=='status':h.db.execute('UPDATE autonomy_assets SET status=? WHERE id=?',('READY',proof['asset_id']))
    else:proof['status']='PASS'
    with pytest.raises(ValueError):fixture.failure(h.store,h.p)
