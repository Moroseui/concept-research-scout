"""The unchanged additive fixture-test AST guard, shared with submission feedback."""
import ast,copy,hashlib

def sha(raw):return hashlib.sha256(raw).hexdigest()
def require(ok,why):
    if not ok:raise ValueError('ITEM4_FIXTURE_'+why)

def check(before,raw):
    old,new=ast.parse(before),ast.parse(raw)
    names={'_native_diagnostic_fixture','synthetic_tests'}
    def split(tree):
        chosen={}
        for name in names:
            found=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name==name]
            require(len(found)==1 and not found[0].decorator_list,'AUDIT_FUNCTION')
            chosen[name]=found[0]
        rest=[n for n in tree.body if all(n is not f for f in chosen.values())]
        return chosen,ast.dump(ast.Module(body=rest,type_ignores=tree.type_ignores))
    left,old_production=split(old);right,new_production=split(new)
    require(old_production==new_production,'PRODUCTION_OR_INTERFACE_CHANGED')
    def shell(node):
        value=copy.deepcopy(node);value.body=[];return ast.dump(value)
    for name in names:require(shell(left[name])==shell(right[name]),'PRODUCTION_OR_INTERFACE_CHANGED')
    require(ast.dump(left['_native_diagnostic_fixture'])!=ast.dump(right['_native_diagnostic_fixture']),
        'FIXTURE_CORRECTION_REQUIRED')
    def tests(node):
        groups=[n for n in node.body if isinstance(n,ast.ClassDef) and n.name=='Checks']
        require(len(groups)==1,'ORIGINAL_TEST_CLASS_REQUIRED')
        group=groups[0]
        return group,ast.dump(ast.Module(body=[n for n in node.body if n is not group],type_ignores=[]))
    old_checks,old_suite=tests(left['synthetic_tests']);new_checks,new_suite=tests(right['synthetic_tests'])
    require(old_suite==new_suite and shell(old_checks)==shell(new_checks),'ORIGINAL_SUITE_CHANGED')
    require(len(new_checks.body)>len(old_checks.body) and
        [ast.dump(n) for n in new_checks.body[:len(old_checks.body)]]==[ast.dump(n) for n in old_checks.body],
        'ORIGINAL_TESTS_CHANGED')
    added=new_checks.body[len(old_checks.body):]
    require(all(isinstance(n,ast.FunctionDef) and n.name.startswith('test_') and not n.decorator_list for n in added),
        'ADDITIVE_TESTS_ONLY')
    method_names=[n.name for n in new_checks.body if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef))]
    require(len(method_names)==len(set(method_names)),'TEST_OVERRIDE_REFUSED')
    return {'module_sha256':sha(raw),'reference_module_sha256':sha(before),'production_ast_unchanged':True,
        'existing_tests_unchanged':True,'added_contract_tests':[n.name for n in added],
        'corrected_fixture_executed':False,'scientific_acceptance':False}
