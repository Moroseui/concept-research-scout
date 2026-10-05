"""Reproduce round-2 sizes without any model, notebook execution or admission.

Run from repository root: python tests/measure_manual_context.py OUTPUT_DIRECTORY
The real external notebook outputs and real system size proxies are identified
in the committed PROVENANCE.json. These are NOT a Sprint10 scientific record.
"""
import json
from pathlib import Path
import subprocess
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from orchestrator import manual_context as manual, context_budget as budget


def measure(output):
    root=Path(__file__).resolve().parents[1]
    fixture=root/"tests/fixtures/context_budget/round2"
    artifacts=json.loads((fixture/"artifacts.json").read_text())
    provenance=json.loads((fixture/"PROVENANCE.json").read_text())
    by_id={x["artifact"]["id"]:x for x in provenance["artifacts"]}
    output=Path(output);output.mkdir(parents=True,exist_ok=True)
    report={"head":subprocess.check_output(["git","rev-parse","HEAD"],cwd=root,text=True).strip(),
        "tree":subprocess.check_output(["git","rev-parse","HEAD^{tree}"],cwd=root,text=True).strip(),
        "working_tree_status":subprocess.check_output(["git","status","--porcelain"],cwd=root,text=True),
        "units":"Unicode characters and UTF-8 bytes reported separately; no token estimate or model invocation",
        "scope":"Input composition and deterministic local workspace retrieval only, not live service integration or scientific acceptance",
        "missing_sprint10_records":provenance["sprint10_missing"],"stages":{}}
    for stage in manual.STAGE_ARTIFACT_TYPES:
        kwargs=dict(stage=stage,idea_ids=["Sprint10"],task="Inspect the selected external comparison evidence and preserve its actual execution and validation status.",artifacts=artifacts,workspace=output/"workspaces"/stage)
        body,m=manual.build(root,**kwargs)
        (output/(stage+".txt")).write_text(body)
        selected=manual.selected_artifacts(stage,artifacts)
        details=[]
        for row in selected:
            p=by_id[row["id"]]
            details.append({"id":row["id"],"type":row["type"],"characters":p["characters"],"utf8_bytes":p["bytes"],"is_size_proxy":p["is_size_proxy"],"delivery":"workspace file" if row["type"] in manual.WORKSPACE_TYPES else "inline","original":p["original"],"note":p["note"]})
        for file in m["workspace_files"]:
            result=subprocess.check_output([sys.executable,"-c","import hashlib,sys; from pathlib import Path; print(hashlib.sha256(Path(sys.argv[1]).read_bytes()).hexdigest())",file["path"]],cwd=kwargs["workspace"],text=True).strip()
            if result!=file["sha256"]:raise RuntimeError("WORKSPACE_RETRIEVAL_CHANGED")
        old_types=manual.WORKSPACE_TYPES
        try:
            manual.WORKSPACE_TYPES=set()
            try:
                _,inline=manual.build(root,**kwargs)
                inline_status="FIT"
            except budget.ContextTooLarge as exc:
                inline=exc.measurement;inline_status="REFUSED_OVER_CAP"
        finally:manual.WORKSPACE_TYPES=old_types
        report["stages"][stage]={"actual":m,"margin_characters":200000-len(body),"input_sha256":budget.sha(body.encode()),"artifacts":details,
            "proxy_inline_content_characters":sum(x["characters"] for x in details if x["is_size_proxy"] and x["delivery"]=="inline"),
            "workspace_retrieval":"Exact bytes read and SHA256 checked by separate Python process from stage working directory; not a model read",
            "same_material_inline_counterfactual":{"status":inline_status,"measurement":inline}}
    (output/"MEASUREMENTS.json").write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps({stage:{"characters":v["actual"]["characters"],"bytes":v["actual"]["utf8_bytes"],"margin":v["margin_characters"],"proxy_characters":v["proxy_inline_content_characters"],"inline_counterfactual":v["same_material_inline_counterfactual"]["measurement"]["characters"]} for stage,v in report["stages"].items()},indent=2))

if __name__=="__main__":measure(sys.argv[1])
