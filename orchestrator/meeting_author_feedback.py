"""Static in-call format feedback; no scientific execution or acceptance."""
from pathlib import Path
import json
from orchestrator import private_records as pr
from orchestrator.meeting_preparation import RUN, sha, require

CHECKER = r'''import ast,json
from pathlib import Path
def pairs(rows):
 d={}
 for k,v in rows:
  if k in d:raise ValueError("DUPLICATE_JSON_KEY")
  d[k]=v
 return d
def strict(raw):
 return json.loads(raw,object_pairs_hook=pairs,parse_constant=lambda x:(_ for _ in ()).throw(ValueError("NONFINITE_JSON")))
here=Path(__file__).resolve().parent
binding=strict((here/"binding.json").read_bytes())
spec=Path("SPEC.proposed.md")
program=Path("analysis.program.json")
assert spec.is_file() and program.is_file() and not spec.is_symlink() and not program.is_symlink(),"REGULAR_OUTPUTS_REQUIRED"
raw=program.read_bytes();assert len(raw)<=80000,"PROGRAM_LIMIT"
text=spec.read_text();assert len(text)<=12000,"SPEC_LIMIT"
for line in ["run_id: "+binding["run_id"],"meeting_plan_sha256: "+binding["plan_sha256"]]:
 assert text.splitlines().count(line)==1,"SPEC_BINDING"
v=strict(raw)
assert set(v)=={"schema","run_id","execution_plan_sha256","files"},"EXACT_PROGRAM_FIELDS"
assert v["schema"]=="scientific-program/v1" and v["run_id"]==binding["run_id"] and v["execution_plan_sha256"]==binding["plan_sha256"],"PROGRAM_BINDING"
assert isinstance(v["files"],dict) and set(v["files"])=={"analysis.py","test_analysis.py"},"EXACT_FILE_SET"
for name,source in v["files"].items():
 assert isinstance(source,str) and source.strip(),"SOURCE_STRING"
 tree=ast.parse(source,filename=name);compile(tree,name,"exec",dont_inherit=True)
 if name=="analysis.py":
  entry=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=="main"]
  assert len(entry)==1 and [a.arg for a in entry[0].args.args]==["input_root","output_root","contract"],"ENTRYPOINT"
print("MEETING_SCHEMA_PASS (static only; no tests or scientific acceptance)")
'''


def files(driver):
    require(driver.config["run_id"] == RUN, "FEEDBACK_SCOPE")
    return {".meeting-feedback/check.py": CHECKER.encode(),
            ".meeting-feedback/binding.json": json.dumps(
                {"run_id": RUN, "plan_sha256": driver.config["plan_sha256"]}, sort_keys=True).encode()}


def install(work, bodies, measurement):
    refs = []
    for name, raw in bodies.items():
        target = Path(work) / name
        pr.mkdir(target.parent, parents=True, exist_ok=True)
        require(not target.exists() and not target.is_symlink(), "FEEDBACK_EXISTS")
        pr.write_bytes(target, raw); target.chmod(0o400)
        refs.append({"path": name, "sha256": sha(raw), "bytes": len(raw)})
    return {**measurement, "workspace_files": [*measurement["workspace_files"], *refs]}


def instructions(bodies):
    return ("\nAfter writing both outputs, run python3 -I -B .meeting-feedback/check.py. "
            "Read and correct its errors within this call, at most12 iterations. "
            "This only reads/compiles output text; it does not execute your program/tests. "
            "Do not edit this checker or binding. No MCP submit_author tool is supplied. "
            "Submit the two actual files, without fabricating any receipt. Host privacy, "
            "schema and isolated scientific-test checks plus independent review remain. "
            "Feedback files: " + json.dumps({k: sha(v) for k, v in bodies.items()}, sort_keys=True))
