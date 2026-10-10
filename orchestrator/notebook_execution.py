"""Export the notebook's actual writefile module without executing any cell.

Scientific authors own every byte of this module. The controller removes only
known notebook writefile directives and preserves their actual concatenation.
"""
import ast


def extract(raw, *, preprocessing=False):
    from orchestrator.notebook_revision import strict_json, clean_source
    nb = strict_json(raw)
    parts = []
    for index, cell in enumerate(nb['cells']):
        if cell.get('cell_type') != 'code':
            continue
        source = ''.join(cell['source'])
        lines = source.splitlines(keepends=True)
        if not lines or not lines[0].startswith('%%writefile '):
            continue
        _, directives = clean_source(source)
        append = directives == ['%%writefile -a /content/sprint13_pipeline.py']
        initial = directives == ['%%writefile /content/sprint13_pipeline.py']
        if (not parts and not initial) or (parts and not append):
            raise ValueError('NOTEBOOK_EXECUTION_WRITEFILE_ORDER')
        # The writefile body, not clean_source's replacement newline: this is
        # exactly the module the notebook would emit, with no top-level run.
        parts.append(''.join(lines[1:]))
    if not parts:
        raise ValueError('NOTEBOOK_EXECUTION_MODULE_REQUIRED')
    source = ''.join(parts)
    entrypoints(source, preprocessing=preprocessing)
    return source.encode()


def entrypoints(source, *, preprocessing=False):
    """The same static interface check for controller and same-call feedback."""
    tree = ast.parse(source, filename='execution.py')
    compile(tree, 'execution.py', 'exec', dont_inherit=True)
    required=[('main', ['input_root', 'output_root', 'contract']),('synthetic_tests', [])]
    if preprocessing:
        required.extend([('preprocess',['input_root','output_root','contract']),
                         ('validate_preprocessing',['output_root','contract'])])
    for name, args in required:
        entries = [node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == name]
        if (len(entries) != 1 or [a.arg for a in entries[0].args.args] != args
                or entries[0].args.posonlyargs or entries[0].args.kwonlyargs
                or entries[0].args.vararg or entries[0].args.kwarg
                or entries[0].args.defaults or entries[0].decorator_list):
            raise ValueError('NOTEBOOK_EXECUTION_ENTRYPOINT:'+name)


def tests_passed(tests, module_sha256):
    if not isinstance(tests, dict) or not isinstance(tests.get('records'), list):
        return False
    rows = [r for r in tests['records'] if isinstance(r, dict) and r.get('test') == 'test_execution_module']
    if len(rows) != 1 or rows[0].get('status') != 'PASS':
        return False
    d = rows[0].get('details')
    return (isinstance(d, dict) and d.get('module_sha256') == module_sha256
        and type(d.get('tests_run')) is int and d['tests_run'] > 0
        and all(type(d.get(k)) is int and d[k] == 0 for k in
                ('failures', 'errors', 'skipped', 'expected_failures', 'unexpected_successes'))
        and d.get('patient_data') is False and d.get('network') is False)
