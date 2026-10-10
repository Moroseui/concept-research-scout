"""Opaque code fails in the same model call, with host privacy behavior retained."""
import json,subprocess,sys
from pathlib import Path
import pytest
from orchestrator import author_format_submission as af,author_output_schema as schema
from orchestrator import scientific_view_scan as scan
from test_author_visible_module_feedback import visible,BODY
from test_author_revision_submission import prepared,write_plan

@pytest.mark.parametrize('encoded',['A'*256,'%41'*256,r'\u0041'*256,'&#65;'*256,'%2541'*256])
def test_early_and_host_opaque_refusal_agree(encoded):
    raw=encoded.encode()
    with pytest.raises(ValueError,match='PRIVATE_INTAKE_OPAQUE_PAYLOAD_REJECTED'):scan.reject_opaque(raw)
    with pytest.raises(ValueError,match='PRIVATE_INTAKE_OPAQUE_PAYLOAD_REJECTED'):scan.scan(raw,set(),kind='code')


def test_reconstructed_code_cannot_split_opaque_text_across_edits():
    raw=('%%writefile /content/sprint13_pipeline.py\n'+BODY+"value='leftRIGHT'\n").encode()
    view=b'# visible only\n'+('\n## cells/0/source bytes 0:'+str(len(raw))+'\n').encode()+raw
    manifest={'schema':'private-scientific-view/v1','original_sha256':'2'*64,'view_sha256':af.sha(view),
        'spans':[{'unit':'cells/0/source','start':0,'end':len(raw),'keep':True,'kind':'code','sha256':af.sha(raw)}]}
    edits=[]
    for old in [b'left',b'RIGHT']:
        start=raw.index(old);edits.append({'unit':'cells/0/source','start':start,'end':start+len(old),
            'before_sha256':af.sha(old),'replacement':'A'*128})
    patch={'schema':'safe-notebook-patch/v1','original_sha256':'2'*64,'view_sha256':af.sha(view),'edits':edits}
    for edit in edits:scan.reject_opaque(edit['replacement'].encode())
    with pytest.raises(ValueError,match='PRIVATE_INTAKE_OPAQUE_PAYLOAD_REJECTED'):schema.visible_module(patch,view,manifest)


def test_plaintext_correction_in_same_isolated_process_without_receipt_for_bad_output(tmp_path):
    baseline=tmp_path/'baseline';baseline.mkdir();old_pins,plan=prepared(baseline);old=af.load(baseline,old_pins[af.CONFIG])
    work=tmp_path/'work';work.mkdir();patch,view,manifest=visible(BODY+"payload='"+'A'*300+"'\n")
    bindings=old['bindings'];bindings['round']=19;bindings['call_id']=af.sha((bindings['run_id']+':run_spec_author:19').encode())
    revision=old['revision'];revision['view_sha256']=af.sha(view)
    pins=af.prepare_revision(work,bindings,revision,notebook={af.MODULE_VIEW:view,af.MODULE_MANIFEST:af.canonical(manifest)})
    write_plan(work,plan);(work/'notebook.patch.json').write_bytes(af.canonical(patch))
    original_config=(work/af.CONFIG).read_bytes()
    proc=subprocess.Popen([sys.executable,'-I','-B',str(work/af.SERVER),pins[af.CONFIG]],cwd=work,
        stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
    def call(n):
        proc.stdin.write(json.dumps({'jsonrpc':'2.0','id':n,'method':'tools/call','params':{'name':'submit_author','arguments':{}}})+'\n');proc.stdin.flush()
        line=proc.stdout.readline();assert line,proc.stderr.read();return json.loads(line)['result']
    try:
        first=call(1);assert first['isError'] is True
        assert 'PRIVATE_INTAKE_OPAQUE_PAYLOAD_REJECTED' in first['content'][0]['text']
        assert not (work/af.RECORD).exists()
        patch['edits'][0]['replacement']='%%writefile /content/sprint13_pipeline.py\n'+BODY
        (work/'notebook.patch.json').write_bytes(af.canonical(patch))
        second=call(2);assert second['isError'] is False
        assert json.loads(second['content'][0]['text'])['status']=='ACCEPTED'
        assert af.verify(work,pins[af.CONFIG])['bindings']['round']==19
        assert (work/af.CONFIG).read_bytes()==original_config
        af.check_runtime(work,pins)
    finally:
        proc.stdin.close();assert proc.wait(timeout=10)==0,proc.stderr.read()


def test_early_opaque_check_does_not_replace_host_identifier_or_secret_checks():
    identifier='sub-stroke'+str(999999)
    for raw,reason in [(identifier.encode(),'PRIVATE_INTAKE_NONDEVELOPMENT_OR_NONCANONICAL_ID'),
        (b'password = synthetic_value','PRIVATE_INTAKE_SECRET_REJECTED')]:
        scan.reject_opaque(raw)
        with pytest.raises(ValueError,match=reason):scan.scan(raw,set(),kind='code')
    assert scan.scan(identifier.encode(),{identifier},kind='code')['development_identifiers']==1
    with pytest.raises(ValueError,match='PRIVATE_INTAKE_PATIENT_LEVEL_CLASSIFICATION_REQUIRED'):
        scan.scan(identifier.encode(),{identifier},kind='aggregate')
