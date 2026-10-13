"""Package the exact L author3 module for its authored preparation-only entry point."""
from pathlib import Path
import base64,hashlib,json
CHANGE="l-preparation-package-20261013"
COMPONENT=("tools/package_l_preparation.py","tests/test_package_l_preparation.py")
MODULE_SHA="c4b767319723fc164ba60dab5a760a1c28af5be3f37e8fc067f196101f41c405"
NOTEBOOK_SHA="1d0aca70feb104a44bad9a405fcde0a9a29cfd586a0bd8862e0004618a49696f"
SUBMISSION_SHA="7bc2902e56a0d11b6990fc4183e5e0de83fa175e044ca94309291fbdbc8bd47f"
SYNTHETIC_SHA="099d84738b1e5d8ffb8780504e3f4689c0155e55d97037d31e9048553d609e58"
CALL="6ebe848327f6b4a0f2d7d68dd5739cef8ef753b726f1ef3317f8bc7ffa397e87"
RUN="colab-arm-47e6a72d9a2c821a4938fcae"
def sha(raw):return hashlib.sha256(raw).hexdigest()
def require(ok,why):
    if not ok:raise ValueError("L_PREPARATION_PACKAGE_"+why)
def authority(folder):
    from orchestrator.autonomy_review import verify_result
    a=verify_result(Path(folder))
    m=json.loads((Path(folder)/"packet-manifest.json").read_bytes())
    require(a["verdict"]=="APPROVE" and a["change_id"]==CHANGE
            and json.loads((Path(folder)/"report.md").read_bytes())["findings"]==[],"INDEPENDENT_APPROVE")
    root=Path(__file__).resolve().parents[1]
    for name in COMPONENT:require(sha((root/name).read_bytes())==m["source_files"][name],"PACKAGE_SOURCE")
    return a
def build(module,notebook,submission,synthetic,approval_folder):
    a=authority(approval_folder)
    require(sha(module)==MODULE_SHA and sha(notebook)==NOTEBOOK_SHA,"EXACT_AUTHOR_BYTES")
    require(sha(submission)==SUBMISSION_SHA and sha(synthetic)==SYNTHETIC_SHA,"EXACT_REVIEW_AND_TESTS")
    v=json.loads(submission)["submission"];tests=json.loads(synthetic)
    require(v["verdict"]=="REVISE" and v["bindings"]["call_id"]==CALL
            and v["bindings"]["run_id"]==RUN and {f["id"]for f in v["findings"]}==
            {"F-L-A100-INTEGRATION-ABSENT","F-L-BASELINE-CONTRAST-METRIC-COMPARABILITY"},"PRESERVED_SCIENTIFIC_FINDINGS")
    require(tests["status"]=="PASS" and tests["binding"]["files"]["execution.py"]==MODULE_SHA
            and tests["binding"]["files"]["revised.ipynb"]==NOTEBOOK_SHA
            and tests["isolation"]["credentials"]is False and tests["isolation"]["patient_mounts"]is False
            and tests["isolation"]["network"]=="UNSHARED"
            and len(tests["tests"]["records"])==5
            and all(r["status"]=="PASS" for r in tests["tests"]["records"]),"HOST_TESTS")
    nb=json.loads(notebook)
    # Keep the authored setup cell exactly; select only the CLI documented in its SPEC.
    original="".join(nb["cells"][20]["source"])
    full="pipeline.stream_command([sys.executable, PIPELINE, DELIVERY_ARM, ','.join(map(str, DELIVERY_FOLDS))])"
    require(original.count(full)==1 and original.rstrip().endswith(full),"ORIGINAL_SETUP")
    setup=original.replace(full,"pipeline.stream_command([sys.executable, PIPELINE, '--prepare-only'])")
    materialize=("import base64, hashlib\nfrom pathlib import Path\n"
      "DELIVERY_ARM = 'A1_L'\nDELIVERY_FOLDS = (0, 1, 2, 3, 4)\n"
      "PIPELINE = '/content/sprint13_pipeline.py'\n"
      "raw = base64.b64decode("+repr(base64.b64encode(module).decode())+", validate=True)\n"
      "assert hashlib.sha256(raw).hexdigest() == "+repr(MODULE_SHA)+"\n"
      "Path(PIPELINE).write_bytes(raw)\n")
    intro="""# A1_L: prepare genuine plans, without training
Use a fresh default Colab **A100** runtime and click **Run all**, unedited.
This prepares the authorized development inputs and genuine L preprocessing plans.
It constructs no trainer and trains no epochs. Full training remains held.
Input hashes and development99/excluded49 membership fail closed. Outputs stay in the arm's existing private Drive folder; no data are copied through the laptop.
This uses the exact scientifically reviewed author3 code and its documented preparation-only command. Scientific review3 remains REVISE for missing real A100 qualification and baseline metric evidence; this package does not close either finding.
Preparation time is not yet measured. The shared module's 35-45-hour estimate concerns later full training, not this preparation step. Colab units are operator-managed.
Wait for 'Preparation only; no trainer constructed. Bound plan receipt:' and return the printed receipt plus the executed notebook privately.
Save the executed notebook to Drive. If anything fails, preserve the error and return it; do not clear locks, delete files or rerun automatically.
After the plans are authenticated, a separate exact-plan synthetic A100 check must exercise real training iterations and checkpoint reload before any full release.
"""
    cells=[{"cell_type":"markdown","metadata":{},"source":intro.splitlines(True)}]
    for code in [materialize,setup]:
        cells.append({"cell_type":"code","metadata":{},"source":code.splitlines(True),"execution_count":None,"outputs":[]})
    result={"nbformat":4,"nbformat_minor":5,"cells":cells,"metadata":{
        "kernelspec":{"display_name":"Python 3","name":"python3"},"accelerator":"GPU",
        "colab":{"provenance":[],"gpuType":"A100"},"private_only":True,
        "arm":"A1_L","folds":[0,1,2,3,4],"preparation_only":True,
        "scientific_review_call":CALL,"scientific_review_verdict":"REVISE",
        "open_findings":sorted(f["id"]for f in v["findings"]),
        "full_training_authorized":False,"module_sha256":MODULE_SHA,
        "source_notebook_sha256":NOTEBOOK_SHA,"submission_sha256":SUBMISSION_SHA,
        "synthetic_receipt_sha256":SYNTHETIC_SHA,
        "packaging_approval_sha256":a["report_sha256"]}}
    return (json.dumps(result,indent=1,ensure_ascii=True)+"\n").encode()
