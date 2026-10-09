"""Same-process format correction, synthetic files only; no admission or science."""
import json
from pathlib import Path
import subprocess
import sys
import pytest
from orchestrator import author_format_submission as af, experiment_environment_requirements as er
from test_experiment_plan_output import synthetic_plan


def prepared(work):
    run='experiment-a74959ac4546a982af4ae137'
    b={'run_id':run,'stage':'run_spec_author','round':6,'source_sha':'a'*40,
       'runtime_sha256':'b'*64,'input_sha256':'c'*64,'call_id':af.sha((run+':run_spec_author:6').encode())}
    revision={'review_call_id':'d'*64,'review_sha256':'e'*64,'operator_scope_sha256':'1'*64,
              'original_sha256':'2'*64,'view_sha256':'3'*64}
    pins=af.prepare_revision(work,b,revision)
    plan=synthetic_plan({'run_id':run,'plan_sha256':'1'*64})
    req={'schema':er.SCHEMA,'python':'3.12','cuda':'12.8','packages':{'nnunetv2':'2.8.1','torch':'2.11.0+cu128'}}
    plan.update(schema=er.PLAN_SCHEMA,environment_requirements=req)
    plan['preprocessing']=[{'schema':er.PREPROCESSING_SCHEMA,'id':'synthetic','plans_name':'synthetic',
        'input_contract_sha256':'4'*64,'environment_requirements_sha256':er.digest(req),
        'split_sha256':'5'*64,'cohort_sha256':'6'*64,'source_capture_sha256':'7'*64,'partitions_sha256':'8'*64}]
    for fit in plan['fits']:fit['preprocessing_id']='synthetic'
    patch={'schema':'safe-notebook-patch/v1','original_sha256':'2'*64,'view_sha256':'3'*64,
           'edits':[{'unit':'cells/0/source','start':0,'end':1,'before_sha256':'9'*64,'replacement':'Synthetic fixture'}]}
    (work/'notebook.patch.json').write_bytes(af.canonical(patch))
    write_plan(work,plan)
    return pins,plan


def write_plan(work,plan):
    raw=af.canonical(plan);(work/'execution.plan.json').write_bytes(raw)
    (work/'SPEC.proposed.md').write_text('Synthetic spec\n'.replace('\n','\n')+
        'run_id: '+plan['run_id']+'\noperator_scope_sha256: '+plan['operator_scope_sha256']+
        '\nexecution_plan_sha256: '+af.sha(raw)+'\n')


def test_revision_accepts_scientific_changes_with_exact_bound_schema(tmp_path):
    pins,plan=prepared(tmp_path)
    answer=af.submit(tmp_path,pins[af.CONFIG],{})
    assert answer['status']=='ACCEPTED'
    assert af.verify(tmp_path,pins[af.CONFIG])['bindings']['round']==6
    with pytest.raises(ValueError,match='AUTHOR_SECOND_SUBMISSION_REFUSED'):
        af.submit(tmp_path,pins[af.CONFIG],{})


def test_actual_isolated_stdio_can_correct_then_submit_in_one_process(tmp_path):
    pins,plan=prepared(tmp_path)
    row=plan['full_training']['full_fits'][0];row['applicability_assumption']=row.pop('assumption');write_plan(tmp_path,plan)
    proc=subprocess.Popen([sys.executable,'-I','-B',str(tmp_path/af.SERVER),pins[af.CONFIG]],
        cwd=tmp_path,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
    def call(n):
        proc.stdin.write(json.dumps({'jsonrpc':'2.0','id':n,'method':'tools/call',
            'params':{'name':'submit_author','arguments':{}}})+'\n');proc.stdin.flush()
        line=proc.stdout.readline();assert line,proc.stderr.read();return json.loads(line)
    try:
        first=call(1)['result'];assert first['isError'] is True
        assert json.loads(first['content'][0]['text'])['validation_error']=='EXPERIMENT_PROJECTION_FULL_FIT'
        assert not (tmp_path/af.RECORD).exists()
        row['assumption']=row.pop('applicability_assumption');write_plan(tmp_path,plan)
        second=call(2)['result'];assert second['isError'] is False
        assert json.loads(second['content'][0]['text'])['status']=='ACCEPTED'
    finally:
        proc.stdin.close();assert proc.wait(timeout=10)==0,proc.stderr.read()


@pytest.mark.parametrize('damage',['run','bool','unknown','environment','patch-binding','patch-overlap','spec','runtime'])
def test_bad_schema_or_mutated_bindings_refuse(tmp_path,damage):
    pins,plan=prepared(tmp_path)
    if damage=='run':plan['run_id']='another'
    elif damage=='bool':plan['full_training']['full_fits'][0]['epochs']=True
    elif damage=='unknown':plan['extra']=True
    elif damage=='environment':plan['environment_requirements']['packages']['torch']='unbound-range'
    elif damage.startswith('patch'):
        path=tmp_path/'notebook.patch.json';patch=json.loads(path.read_bytes())
        if damage=='patch-binding':patch['original_sha256']='0'*64
        else:patch['edits'].append(dict(patch['edits'][0]))
        path.write_bytes(af.canonical(patch))
    write_plan(tmp_path,plan)
    if damage=='spec':(tmp_path/'SPEC.proposed.md').write_text('missing binding')
    if damage=='runtime':
        path=tmp_path/af.RUNTIME/'orchestrator/author_output_schema.py';path.write_bytes(path.read_bytes()+b'\n#changed')
        with pytest.raises(ValueError,match='AUTHOR_RUNTIME_CHANGED'):af.check_runtime(tmp_path,pins)
    else:
        with pytest.raises(ValueError):af.submit(tmp_path,pins[af.CONFIG],{})
    assert not (tmp_path/af.RECORD).exists()


def test_oversize_spec_gets_same_process_feedback_before_receipt(tmp_path):
    pins,plan=prepared(tmp_path)
    path=tmp_path/'SPEC.proposed.md';original=path.read_text()
    path.write_text(original+'x'*(12001-len(original)))
    proc=subprocess.Popen([sys.executable,'-I','-B',str(tmp_path/af.SERVER),pins[af.CONFIG]],cwd=tmp_path,
        stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
    def call(n):
        proc.stdin.write(json.dumps({'jsonrpc':'2.0','id':n,'method':'tools/call',
            'params':{'name':'submit_author','arguments':{}}})+'\n');proc.stdin.flush()
        return json.loads(proc.stdout.readline())['result']
    try:
        first=call(1);assert first['isError'] is True
        assert 'EXPERIMENT_SPEC_LIMIT' in first['content'][0]['text']
        assert not (tmp_path/af.RECORD).exists()
        path.write_text(original+'?'*(12000-len(original)))
        second=call(2);assert second['isError'] is False
        assert json.loads(second['content'][0]['text'])['status']=='ACCEPTED'
    finally:
        proc.stdin.close();assert proc.wait(timeout=10)==0,proc.stderr.read()
