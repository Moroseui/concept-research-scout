"""Build private, unreleased retention/retry candidates from exact prior notebooks."""
from pathlib import Path
import ast
import base64
import copy
import hashlib
import json

BASES = {
 "A1_pnormct":"7121a2cca22fa2f71bec9ba97811d07e9b3dc6ae7dd3e2ec76ed1db11a9763d1",
 "A1_pnorm_v2":"211d947fb0802fc2c40294e661afc148142c0120b2444dc30b8d57840b0e7032",
}
def sha(raw):return hashlib.sha256(raw).hexdigest()

def render(raw, arm, tools):
    if sha(raw)!=BASES.get(arm):raise ValueError("EXACT_PRIOR_NOTEBOOK_REQUIRED")
    n=copy.deepcopy(json.loads(raw))
    if any(c.get("outputs") or c.get("execution_count") is not None for c in n["cells"]):
        raise ValueError("UNEXECUTED_BASE_REQUIRED")
    helpers=None;helper_cell=None;dispatch_cell=None
    for i,c in enumerate(n["cells"]):
        s="".join(c["source"])
        if s.startswith("import base64, hashlib, json\nfrom pathlib import Path\noperational_files = "):
            for node in ast.parse(s).body:
                if isinstance(node,ast.Assign) and any(isinstance(t,ast.Name)and t.id=="operational_files"for t in node.targets):
                    helpers=ast.literal_eval(node.value);helper_cell=i
        if "from colab_operational_resume import run_notebook" in s:
            if dispatch_cell is not None:raise ValueError("AMBIGUOUS_DISPATCH")
            dispatch_cell=i
    if helpers is None or dispatch_cell is None:raise ValueError("BASE_LAYOUT_CHANGED")
    from tools.colab_reliable_resume import PINNED
    for name,pin in PINNED[arm].items():
        if name=="identity":continue
        if name not in helpers or sha(base64.b64decode(helpers[name]["base64"],validate=True))!=pin:
            raise ValueError("LEGACY_BINDING_CHANGED")
    for name in ("colab_private_output.py","colab_storage_reliability.py","colab_reliable_resume.py"):
        body=(Path(tools)/name).read_bytes()
        if name in helpers and helpers[name]["sha256"]!=sha(body):
            raise ValueError("EXISTING_FOLDER_HELPER_CHANGED")
        helpers[name]={"sha256":sha(body),"base64":base64.b64encode(body).decode()}
    n["cells"][helper_cell]["source"]=[
        "import base64, hashlib, json\nfrom pathlib import Path\noperational_files = "+repr(helpers)+"\n"
        "for name, descriptor in operational_files.items():\n"
        "    content = base64.b64decode(descriptor['base64'], validate=True)\n"
        "    assert hashlib.sha256(content).hexdigest() == descriptor['sha256']\n"
        "    Path('/content', name).write_bytes(content)\n"]
    s="".join(n["cells"][dispatch_cell]["source"])
    n["cells"][dispatch_cell]["source"]=[s.replace("from colab_operational_resume import run_notebook",
        "from colab_reliable_resume import run_notebook")]
    n["cells"][0]["source"]=["# "+arm+" - PRIVATE REPAIR CANDIDATE, NOT RELEASED\n\n"
        "Do not run until independent code review and the real training/publish/resume checks pass. "
        "This candidate preserves the exact existing science and operational binding, completed-fold verification, "
        "up-front logins, input checks, CPU workers and stall watchdog. It adds four reusable checkpoint slots "
        "within each NEW attempt, bounded lease API retries and a specific storage-full error. "
        "It deletes no historical Drive files. Lease references and payload hashes determine the actual resume epoch. "
        "At the recorded stop: pnormct fold3 next epoch55; pnorm_v2 fold2 next epoch180. "
        "Keep the old runtime disconnected; never overlap sessions for one arm.\n"]
    n["metadata"]["storage_repair_candidate"]={
        "release_status":"UNRELEASED_REVIEW_REQUIRED","arm":arm,
        "base_notebook_sha256":sha(raw),"preserved_operational_identity":PINNED[arm]["identity"],
        "helpers":{k:v["sha256"]for k,v in helpers.items()},
        "scientific_source_unchanged":True,"live_drive_tested":False,"gpu_tested":False}
    return (json.dumps(n,ensure_ascii=True,indent=1)+"\n").encode()
