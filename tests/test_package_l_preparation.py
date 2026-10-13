import ast,base64,json,sys
from pathlib import Path
from types import SimpleNamespace,ModuleType
import pytest
from tools import package_l_preparation as p
@pytest.fixture
def fixture(monkeypatch):
    module=b"# synthetic package fixture; never patient code\ndef run_delivery(*a): pass\n"
    setup="""import sys, json, importlib.util
from pathlib import Path
from google.colab import drive, auth, _message
drive.mount('/content/drive')
auth.authenticate_user()
spec = importlib.util.spec_from_file_location('l_delivery', PIPELINE)
pipeline = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = pipeline
spec.loader.exec_module(pipeline)
pipeline.delivery_check(DELIVERY_ARM, DELIVERY_FOLDS)
pipeline.load_input_reference()
pipeline.install_dependencies()
nb = _message.blocking_request('get_ipynb')['ipynb']
for cell in nb['cells']:
    if cell.get('cell_type') == 'code':
        cell['outputs'] = []
        cell['execution_count'] = None
Path('/content/delivery-executed.ipynb').write_text(json.dumps(nb, ensure_ascii=False))
pipeline.stream_command([sys.executable, PIPELINE, DELIVERY_ARM, ','.join(map(str, DELIVERY_FOLDS))])
"""
    cells=[{"cell_type":"code","source":[]} for _ in range(23)];cells[20]["source"]=setup.splitlines(True)
    notebook=json.dumps({"cells":cells}).encode()
    decision={"verdict":"REVISE","bindings":{"call_id":p.CALL,"run_id":p.RUN},"findings":[{"id":x}for x in ["F-L-A100-INTEGRATION-ABSENT","F-L-BASELINE-CONTRAST-METRIC-COMPARABILITY"]]}
    submission=json.dumps({"submission":decision}).encode()
    synthetic=json.dumps({"status":"PASS","binding":{"files":{"execution.py":p.sha(module),"revised.ipynb":p.sha(notebook)}},"isolation":{"credentials":False,"patient_mounts":False,"network":"UNSHARED"},"tests":{"records":[{"status":"PASS"}for _ in range(5)]}}).encode()
    for name,raw in [("MODULE_SHA",module),("NOTEBOOK_SHA",notebook),("SUBMISSION_SHA",submission),("SYNTHETIC_SHA",synthetic)]:monkeypatch.setattr(p,name,p.sha(raw))
    monkeypatch.setattr(p,"authority",lambda folder:{"report_sha256":"a"*64})
    return [module,notebook,submission,synthetic,Path("unused")]
def test_exact_module_embedded_and_preparation_only(fixture):
    nb=json.loads(p.build(*fixture))
    assert len(nb["cells"])==3 and nb["metadata"]["preparation_only"]is True
    assert nb["metadata"]["scientific_review_verdict"]=="REVISE" and nb["metadata"]["full_training_authorized"]is False
    materialize="".join(nb["cells"][1]["source"]);setup="".join(nb["cells"][2]["source"])
    tree=ast.parse(materialize)
    raw=next(n.value for n in tree.body if isinstance(n,ast.Assign)and any(isinstance(x,ast.Name)and x.id=="raw" for x in n.targets))
    assert base64.b64decode(ast.literal_eval(raw.args[0]))==fixture[0]
    ast.parse(setup)
    assert "pipeline.stream_command([sys.executable, PIPELINE, '--prepare-only'])"in setup
    assert "'.join(map(str, DELIVERY_FOLDS))"not in setup
    assert all(not c.get("outputs") and c.get("execution_count")is None for c in nb["cells"])
@pytest.mark.parametrize("index",[0,1,2,3])
def test_changed_author_or_review_or_test_bytes_refuse(fixture,index):
    fixture[index]+=b" "
    with pytest.raises(ValueError,match="EXACT_"):p.build(*fixture)
def test_setup_runs_only_authored_preparation_command_under_stubs(fixture,monkeypatch):
    nb=json.loads(p.build(*fixture));code="".join(nb["cells"][2]["source"]);events=[]
    colab=ModuleType("google.colab")
    colab.drive=SimpleNamespace(mount=lambda path:events.append(("mount",path)))
    colab.auth=SimpleNamespace(authenticate_user=lambda:events.append(("auth",)))
    colab._message=SimpleNamespace(blocking_request=lambda name:{"ipynb":nb})
    monkeypatch.setitem(sys.modules,"google.colab",colab)
    import importlib.util
    pipeline=ModuleType("l_delivery")
    for name in ["delivery_check","load_input_reference","install_dependencies","stream_command"]:
        setattr(pipeline,name,lambda *a,_name=name:events.append((_name,*a)))
    spec=SimpleNamespace(name="l_delivery",loader=SimpleNamespace(exec_module=lambda m:None))
    monkeypatch.setattr(importlib.util,"spec_from_file_location",lambda *a:spec)
    monkeypatch.setattr(importlib.util,"module_from_spec",lambda s:pipeline)
    saved=[];monkeypatch.setattr(Path,"write_text",lambda path,text,**kw:saved.append((str(path),text)))
    monkeypatch.setitem(sys.modules,"l_delivery",pipeline)
    exec(compile(code,"packaged-setup","exec"),{"PIPELINE":"/content/sprint13_pipeline.py","DELIVERY_ARM":"A1_L","DELIVERY_FOLDS":(0,1,2,3,4)})
    assert [e for e in events if e[0]=="stream_command"]==[("stream_command",[sys.executable,"/content/sprint13_pipeline.py","--prepare-only"])]
    assert [e[0]for e in events]==["mount","auth","delivery_check","load_input_reference","install_dependencies","stream_command"]
    assert len(saved)==1 and saved[0][0]=="/content/delivery-executed.ipynb"
@pytest.mark.parametrize("finding",["UNEXPECTED_CODE_DEFECT","F-L-A100-INTEGRATION-ABSENT"])
def test_changed_findings_cannot_be_reclassified(fixture,monkeypatch,finding):
    value=json.loads(fixture[2]);value["submission"]["findings"]=[{"id":finding}]
    fixture[2]=json.dumps(value).encode();monkeypatch.setattr(p,"SUBMISSION_SHA",p.sha(fixture[2]))
    with pytest.raises(ValueError,match="PRESERVED_SCIENTIFIC_FINDINGS"):p.build(*fixture)
@pytest.mark.parametrize("field,value",[("credentials",True),("patient_mounts",True),("network","SHARED")])
def test_nonisolated_host_receipt_refuses(fixture,monkeypatch,field,value):
    receipt=json.loads(fixture[3]);receipt["isolation"][field]=value
    fixture[3]=json.dumps(receipt).encode();monkeypatch.setattr(p,"SYNTHETIC_SHA",p.sha(fixture[3]))
    with pytest.raises(ValueError,match="HOST_TESTS"):p.build(*fixture)
