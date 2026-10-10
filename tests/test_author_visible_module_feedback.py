"""Visible-only author feedback shares exact controller entrypoint checks."""
import copy,json,subprocess,sys
from pathlib import Path
import pytest
from orchestrator import author_output_schema as schema,author_format_submission as af,notebook_execution as execution
from test_author_revision_submission import prepared,write_plan

BODY='def main(input_root, output_root, contract): pass\ndef synthetic_tests(): return {}\ndef preprocess(input_root, output_root, contract): pass\ndef validate_preprocessing(output_root, contract): pass\n'


def visible(body=BODY):
    raw=('%%writefile /content/sprint13_pipeline.py\n'+BODY).encode()
    marker=('\n## cells/0/source bytes 0:'+str(len(raw))+'\n').encode()
    view=b'# Synthetic visible source only\n'+marker+raw
    manifest={'schema':'private-scientific-view/v1','original_sha256':'2'*64,'view_sha256':af.sha(view),
        'spans':[{'unit':'cells/0/source','start':0,'end':len(raw),'keep':True,'kind':'code','sha256':af.sha(raw)}]}
    patch={'schema':'safe-notebook-patch/v1','original_sha256':'2'*64,'view_sha256':af.sha(view),
        'edits':[{'unit':'cells/0/source','start':0,'end':len(raw),'before_sha256':af.sha(raw),
            'replacement':'%%writefile /content/sprint13_pipeline.py\n'+body}]}
    return patch,view,manifest


def test_feedback_equals_controller_for_complete_visible_module():
    patch,view,manifest=visible()
    source=execution.extract(af.canonical({'cells':[{'cell_type':'code','source':[patch['edits'][0]['replacement']]}]}),preprocessing=True)
    assert schema.visible_module(patch,view,manifest)==af.sha(source)


@pytest.mark.parametrize('body',[BODY+'def synthetic_tests(): pass\n',BODY.replace('synthetic_tests()', 'synthetic_tests(argument)'),
    BODY.replace('def synthetic_tests():','@decorated\ndef synthetic_tests():'),BODY.replace('def preprocess(input_root, output_root, contract): pass\n',''),
    BODY.replace('main(input_root, output_root, contract)','main(input_root, output_root, contract=None)')])
def test_same_required_signatures_refused_by_host_and_feedback(body):
    patch,view,manifest=visible(body)
    with pytest.raises(ValueError,match='AUTHOR_MODULE_ENTRYPOINT'):schema.visible_module(patch,view,manifest)
    with pytest.raises(ValueError,match='NOTEBOOK_EXECUTION_ENTRYPOINT'):
        execution.extract(af.canonical({'cells':[{'cell_type':'code','source':[patch['edits'][0]['replacement']]}]}),preprocessing=True)


@pytest.mark.parametrize('damage',['view','original','preimage','omitted','overlap-marker','hidden-edit','overwrite'])
def test_feedback_refuses_unbound_or_omitted_content(damage):
    patch,view,manifest=visible()
    if damage=='view':view+=b'changed'
    elif damage=='original':manifest['original_sha256']='f'*64
    elif damage=='preimage':patch['edits'][0]['before_sha256']='f'*64
    elif damage=='omitted':manifest['spans'][0]['keep']=False
    elif damage=='overlap-marker':
        view+=view[view.index(b'\n##'):];patch['view_sha256']=manifest['view_sha256']=af.sha(view)
    elif damage=='hidden-edit':patch['edits'][0]['end']+=1
    else:patch['edits'][0]['replacement']='%%writefile -a /content/sprint13_pipeline.py\n'+BODY
    with pytest.raises(ValueError):schema.visible_module(patch,view,manifest)


def test_duplicate_then_correction_in_one_mcp_process(tmp_path):
    baseline=tmp_path/'baseline';baseline.mkdir();old_pins,plan=prepared(baseline);old=af.load(baseline,old_pins[af.CONFIG])
    work=tmp_path/'work';work.mkdir();patch,view,manifest=visible(BODY+'def synthetic_tests(): pass\n')
    b=old['bindings'];b['round']=17;b['call_id']=af.sha((b['run_id']+':run_spec_author:17').encode())
    revision=old['revision'];revision['view_sha256']=af.sha(view)
    pins=af.prepare_revision(work,b,revision,notebook={af.MODULE_VIEW:view,af.MODULE_MANIFEST:af.canonical(manifest)})
    write_plan(work,plan);(work/'notebook.patch.json').write_bytes(af.canonical(patch))
    proc=subprocess.Popen([sys.executable,'-I','-B',str(work/af.SERVER),pins[af.CONFIG]],cwd=work,
        stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
    def call(n):
        proc.stdin.write(json.dumps({'jsonrpc':'2.0','id':n,'method':'tools/call','params':{'name':'submit_author','arguments':{}}})+'\n');proc.stdin.flush()
        line=proc.stdout.readline();assert line,proc.stderr.read();return json.loads(line)['result']
    try:
        first=call(1);assert first['isError'] is True
        assert 'AUTHOR_MODULE_ENTRYPOINT: NOTEBOOK_EXECUTION_ENTRYPOINT:synthetic_tests' in first['content'][0]['text']
        assert not (work/af.RECORD).exists()
        patch['edits'][0]['replacement']='%%writefile /content/sprint13_pipeline.py\n'+BODY
        (work/'notebook.patch.json').write_bytes(af.canonical(patch))
        second=call(2);assert second['isError'] is False and json.loads(second['content'][0]['text'])['status']=='ACCEPTED'
        assert af.verify(work,pins[af.CONFIG])['bindings']['round']==17
        af.check_runtime(work,pins)
    finally:
        proc.stdin.close();assert proc.wait(timeout=10)==0,proc.stderr.read()
