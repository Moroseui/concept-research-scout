"""Exact mandatory navigation/task files; all open obligations still inline."""
import json
import pytest
from orchestrator import manual_context as mc,context_budget as cb,scientific_intake
from test_context_budget import root,add_obligation
from test_manual_context import artifact

@pytest.mark.parametrize('stage',['run_spec_author','run_spec_review'])
def test_exact_findings_task_and_artifacts_delivered_before_model(root,monkeypatch,stage):
    monkeypatch.setattr(scientific_intake,'load_views',lambda *a,**kw:([],[]))
    quote=add_obligation(root,'adverse finding')
    row=artifact(root,'notebook_source','native-interface',text='Exact synthetic source.\n')
    work=root/'work';task='Complete mandatory task. '*2000
    body,m=mc.build(root,stage=stage,idea_ids=['sprint13b-execution','P001'],task=task,artifacts=[row],
        workspace=work,private_intake={'sha256':'a'*64},execution_mode='sprint13b-execution',structured_review=True)
    role='author' if stage.endswith('author') else 'review'
    refs={r['id']:r for r in m['workspace_files']}
    navigation=refs['current-findings-index'];file=work/navigation['path']
    assert json.loads(file.read_bytes())==m['finding_status']
    assert quote in body and navigation['sha256'] in body
    instruction=(work/refs['scientific-'+role+'-instructions']['path']).read_text()
    assert task in instruction and task not in body
    assert 'No instruction was shortened or omitted' in body
    assert cb.encoded(refs[row['id']]) in body
    assert (work/refs[row['id']]['path']).read_text()=='Exact synthetic source.\n'
    assert refs[row['id']]['source_path']==row['path']
    if stage.endswith('review'):assert 'APPROVE' in instruction and 'REVISE' in instruction
    for ref in refs.values():
        p=work/ref['path'];assert cb.sha(p.read_bytes())==ref['sha256'] and p.stat().st_mode&0o777==0o400
    assert m['characters']==len(body)<200000

@pytest.mark.parametrize('fault',['secret-task','oversized-obligation','stop','workspace'])
def test_compaction_does_not_relax_refusals(root,monkeypatch,fault):
    from test_context_budget import save_manifest
    monkeypatch.setattr(scientific_intake,'load_views',lambda *a,**kw:([],[]))
    task='Mandatory task';work=root/'work'
    if fault=='secret-task':task='sk-'+('syntheticcredential'*5)
    elif fault=='workspace':work=None
    elif fault=='stop':add_obligation(root,'stop')
    else:
        add_obligation(root,'adverse finding')
        p=root/cb.PROJECT/'obligations.json';v=json.loads(p.read_bytes());row=v['obligations'][-1]
        # Keep source authority valid; huge inline source must still exceed cap.
        source=root/row['source']['path'];raw=source.read_bytes();raw+=b' x'*700;source.write_bytes(raw)
        row['text']=raw.decode();row['source'].update(start=0,end=len(raw),sha256=cb.sha(raw))
        v['obligations'] += [{**row,'id':'synthetic-'+str(n)} for n in range(150)]
        p.write_text(json.dumps(v));save_manifest(root)
    error={'secret-task':'PUBLICATION_CONTENT_REJECTED','oversized-obligation':'MODEL_INPUT_LIMIT_EXCEEDED',
           'stop':'SCOPED_STOP','workspace':'MANUAL_WORKSPACE_REQUIRED'}[fault]
    with pytest.raises(ValueError,match=error):
        mc.build(root,stage='run_spec_review',idea_ids=['sprint13b-execution','P001'],task=task,artifacts=[],
            workspace=work,private_intake={'sha256':'a'*64},execution_mode='sprint13b-execution',structured_review=True)
    assert not (root/'work').exists()
