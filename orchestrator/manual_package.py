"""Emit the already designed Sprint10 notebook with acceptance capture cells.

No scientific metric, split, bootstrap or training code is generated here.
"""
import json
import shutil
from pathlib import Path
from orchestrator import private_records
from orchestrator.manual_executor import digest, atomic, inventory
from orchestrator.manual_validation import TOLERANCE,TABLES,baseline_contract,expected_identity,expected_output_path,BASELINE_PATH

START = r'''# Acceptance capture: run once, before the unchanged comparison cells.
import json, hashlib, shutil, os, sys
from pathlib import Path
PACKAGE_DIR = Path("/content/drive/MyDrive/isles-pilot/manual-step-d/RUN_ID")
PACKAGE = json.loads((PACKAGE_DIR / "manifest.json").read_text())
def acceptance_sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
ACCEPTANCE_RETURN = PACKAGE_DIR / "return"
# Never turn an existing/uncertain computation into a pre-computation refusal.
assert not ACCEPTANCE_RETURN.exists(), "Existing acceptance return: STOP, do not rerun"
identity_reason = None
try:
    observed_notebook = json.loads((PACKAGE_DIR / "Sprint10.ipynb").read_text())
    observed_cells = ["".join(c["source"]) for c in observed_notebook["cells"] if c["cell_type"] == "code"]
    assert observed_cells == PACKAGE["notebook_code_cells"], "NOTEBOOK_CODE_CHANGED"
    assert acceptance_sha(PACKAGE_DIR / "SPEC.md") == PACKAGE["spec_sha256"], "SPEC_CHANGED"
    assert acceptance_sha(PACKAGE_DIR / "review.json") == PACKAGE["review_sha256"], "REVIEW_CHANGED"
    for name, expected in PACKAGE["private_files"].items():
        assert acceptance_sha(Path(PRIVATE_INPUT_DIR) / name) == expected, "PRIVATE_INPUT_CHANGED"
except (AssertionError, OSError, ValueError, KeyError, TypeError):
    # No return/start marker, baseline capture or scientific cell has run.
    refusal = {"schema":"manual-precomputation-refusal/v1", "run_id":PACKAGE["run_id"],
        "manifest_sha256":hashlib.sha256(json.dumps(PACKAGE,sort_keys=True).encode()).hexdigest(),
        "status":"IDENTITY_REFUSED_BEFORE_COMPUTATION", "computation_started":False,
        "return_exists":False, "reason":"PACKAGE_IDENTITY_CHECK_FAILED"}
    token = hashlib.sha256(json.dumps(refusal,sort_keys=True).encode()).hexdigest()
    (PACKAGE_DIR / ("identity-refusal-" + token + ".json")).write_text(json.dumps(refusal,sort_keys=True))
    raise RuntimeError("Identity refused before computation. Preserve the refusal file and ask the driver to re-emit the reviewed package; do not run later cells.") from None
import importlib
for dependency in ["numpy","pandas","scipy","sklearn","nibabel","matplotlib"]:
    importlib.import_module(dependency)  # fail before capture if the runtime is incomplete
BASELINE_DIR = Path(DRIVE_BASE) / "sprint10-comparison-PRIVATE/compare-875c56c278-0a60362503"
RETURN_FILES = PACKAGE["return_files"]
for name in RETURN_FILES:
    assert acceptance_sha(BASELINE_DIR / name) == PACKAGE["baseline_sha256"][name], "Original reference differs: " + name
for name, keys in PACKAGE["baseline_json_keys"].items():
    assert sorted(json.loads((BASELINE_DIR / name).read_text())) == keys, "Original JSON keys changed"
ACCEPTANCE_RETURN.mkdir()
(ACCEPTANCE_RETURN / "baseline").mkdir()
for name in RETURN_FILES: shutil.copy2(BASELINE_DIR / name, ACCEPTANCE_RETURN / "baseline" / name)
BASELINE_HASHES = {name: acceptance_sha(ACCEPTANCE_RETURN / "baseline" / name) for name in RETURN_FILES}
(ACCEPTANCE_RETURN / "started.json").write_text(json.dumps({"run_id":PACKAGE["run_id"],"manifest_sha256":hashlib.sha256(json.dumps(PACKAGE,sort_keys=True).encode()).hexdigest(),"baseline_sha256":BASELINE_HASHES},sort_keys=True))
# New output base, not the original run or either training directory.
OUT_BASE = str(PACKAGE_DIR / "comparison")
'''
END = r'''# Export only after the comparison and original validation have completed.
import importlib.metadata, platform, zipfile
assert len(CASES) == 99
(ACCEPTANCE_RETURN / "actual").mkdir()
for name in RETURN_FILES:
    source = Path(OUT_DIR) / name
    assert source.is_file(), "Missing comparison result: " + name
    shutil.copy2(source, ACCEPTANCE_RETURN / "actual" / name)
assert all(acceptance_sha(BASELINE_DIR / name) == BASELINE_HASHES[name] for name in RETURN_FILES), "Original baseline changed during run"
receipt = {**{k: PACKAGE[k] for k in ("run_id","source","spec_sha256","notebook_code_sha256","private_files")},
 "manifest_sha256": hashlib.sha256(json.dumps(PACKAGE,sort_keys=True).encode()).hexdigest(),
 "development_count":len(CASES),"training_performed":False,"tolerance":PACKAGE["tolerance"],
 "baseline_sha256":BASELINE_HASHES,"actual_sha256":{name:acceptance_sha(ACCEPTANCE_RETURN / "actual" / name) for name in RETURN_FILES},
 "baseline_output_path":str(BASELINE_DIR),"actual_output_path":str(OUT_DIR),
 "python":platform.python_version(),"packages":{x:importlib.metadata.version(x) for x in ("numpy","pandas","scipy","scikit-learn","nibabel")}}
(ACCEPTANCE_RETURN / "execution_receipt.json").write_text(json.dumps(receipt,indent=2))
archive = PACKAGE_DIR / (PACKAGE["run_id"] + "-return-PRIVATE.zip")
assert not archive.exists(), "Existing export: preserve and inspect"
with zipfile.ZipFile(archive,"x",compression=zipfile.ZIP_DEFLATED) as z:
    for path in ACCEPTANCE_RETURN.rglob("*"):
        if path.is_file():z.write(path,str(path.relative_to(ACCEPTANCE_RETURN)))
print("Completed private return:",str(archive))
print("Download and extract into the system collection inbox. Do not run this notebook again.")
'''


def notebook_bytes(root,run_id):
    root=Path(root)
    original=root/'projects/isles24/manual/sprint10/isles24_sprint10_r2_exclusion_reference.ipynb'
    notebook=json.loads(original.read_text())
    # Mount explicitly before Run all. Remove obsolete git fetch: private split
    # was already detached from the repository by the approved step(c) repair.
    setup=''.join(notebook['cells'][2]['source'])
    first=setup.index('from google.colab import drive');last=setup.index('import numpy as np')
    setup=setup[:first]+setup[last:]
    notebook['cells'][2]['source']=setup.splitlines(keepends=True)
    def cell(text):return {'cell_type':'code','metadata':{},'source':text.splitlines(keepends=True),'outputs':[],'execution_count':None}
    notebook['cells'].insert(2,cell(START.replace('RUN_ID',run_id)))
    notebook['cells'].insert(0,cell("from google.colab import drive\ndrive.mount('/content/drive')\n"))
    notebook['cells'].append(cell(END))
    for c in notebook['cells']:
        if c['cell_type']=='code':c.update(outputs=[],execution_count=None)
    return (json.dumps(notebook,indent=1)+'\n').encode()


def code_cells(raw):
    notebook=json.loads(raw)
    return [''.join(c['source']) for c in notebook['cells'] if c['cell_type']=='code']


def code_sha(raw):return digest(json.dumps(code_cells(raw),ensure_ascii=False).encode())


def check_notebook(raw,manifest):
    if code_cells(raw)!=manifest['notebook_code_cells']:raise ValueError('NOTEBOOK_CODE_CHANGED')
    if code_sha(raw)!=manifest['notebook_code_sha256']:raise ValueError('NOTEBOOK_CODE_BINDING')


def private_inputs(root):
    # References only. Private inputs remain on Drive; never copy them into a
    # package, state directory or scientific model workspace.
    contract=json.loads((Path(root)/'projects/isles24/manual/sprint10/DATA_CONTRACT.json').read_text())
    return {name:contract[key]['sha256'] for name,key in [('split_manifest.csv','split_manifest'),('excluded_cases.json','exclusions')]}


def emit(root,prepared,run_id,source,spec,review):
    root,prepared=map(Path,(root,prepared))
    originals=baseline_contract(root)
    private_records.mkdir(prepared,mode=0o700)
    original=root/'projects/isles24/manual/sprint10/isles24_sprint10_r2_exclusion_reference.ipynb'
    path=prepared/'Sprint10.ipynb';private_records.write_bytes(path,notebook_bytes(root,run_id))
    private_hash=private_inputs(root)
    private_records.write_bytes(prepared/'SPEC.md',Path(spec).read_bytes())
    private_records.write_bytes(prepared/'review.json',Path(review).read_bytes())
    manifest={'schema':'manual-sprint10-acceptance/v1','run_id':run_id,'source':source,
       'spec_sha256':digest(Path(spec).read_bytes()),'review_sha256':digest(Path(review).read_bytes()),
       'notebook_code_sha256':code_sha(path.read_bytes()),'notebook_code_cells':code_cells(path.read_bytes()),'notebook_artifact_sha256':digest(path.read_bytes()),'predecessor_notebook_sha256':digest(original.read_bytes()),
       'private_files':private_hash,'baseline_sha256':originals['sha256'],'baseline_json_keys':originals['json_keys'],'return_files':list(TABLES)+['comparison_reference.json','compatibility_report.json'],
       'tolerance':TOLERANCE,'training_allowed':False,'development_count':99,'locked_patient_access_allowed':False}
    atomic(prepared/'manifest.json',manifest,mode=0o600)
    private_records.write_text(prepared/'RUN_INSTRUCTIONS.md',f'''# Sprint10 system acceptance run ? once only

1. Keep original Sprint8/Sprint9 runs and the original Sprint10 comparison folder unchanged.
2. On Drive create `MyDrive/isles-pilot/manual-step-d/{run_id}/` and upload `Sprint10.ipynb`, `manifest.json`, `SPEC.md` and `review.json` there.
3. The hash-bound split manifest and exclusion list must already be beside each other at `MyDrive/isles-pilot/sprint10-inputs-PRIVATE/`. They are not included in this package; never download or paste them into model context. If absent, stop and report the missing file.
4. Open this exact Drive notebook in Colab and use Run all, without adding or editing cells. Its fixed first cell mounts Drive. Use a CPU runtime. Autosaved outputs, execution counts and JSON formatting may change; the ordered code-cell sources must match the reviewed manifest.

5. Check existing paths: `feature-cache-2mm-v2`, `sprint8-seeds-features-PRIVATE/run-875c56c278`, `sprint9-unet-PRIVATE/run-0a60362503`, and original `sprint10-comparison-PRIVATE/compare-875c56c278-0a60362503`, all under `MyDrive/isles-pilot/`. All original required files must exist. Do not substitute a different run or recreate missing outputs.
6. Run all original notebook cells exactly once, unchanged. It preserves the baseline tables first, checks the private membership hashes/count, retains the99-case assertion and uses the existing comparison code. No25 final-evaluation or24 reserve patient data may be accessed. If a cell fails, stop and preserve its output. Only an `identity-refusal-*.json` from the pre-computation guard, with no return/start marker, can authorize re-emitting the unchanged package through `advance --identity-refusal PATH`. Any later or uncertain failure stays blocked; never delete a return directory or rerun it.
7. The final cell prints `{run_id}-return-PRIVATE.zip` inside the package's Drive directory. Download it, extract to the collection inbox shown by the driver, and tell the operator session collection is ready. Keep both original and new Drive output folders.

Predeclared acceptance: identical CSV row/column ordering, labels, counts and formatted confidence intervals. Unformatted numeric cells use absolute tolerance1e-10 plus relative tolerance1e-9. Original bootstrap remains seed0/2000 samples. Only the comparison output-directory prefix is normalized. New provenance/fingerprint and timestamp fields are expected metadata differences; they cannot excuse metric differences. Any other discrepancy blocks acceptance and is reported.

If dependencies are missing, report the missing package; do not change scientific code or silently substitute inputs. The return records actual dependency versions. This is an acceptance run, not a new efficacy claim.
''')
    return manifest
