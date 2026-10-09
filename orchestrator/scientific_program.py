"""Preserve, compile and synthetically test author-owned diagnostic code.

No scientific implementation or conclusion is supplied by the controller.
No credentials, patient directory, network or provider are exposed to tests.
"""
import ast
import json
from pathlib import Path
import subprocess
import time
from orchestrator import private_records, notebook_synthetic, scientific_intake
from orchestrator.manual_executor import digest, atomic, read
from orchestrator.manual_driver import write_once
from orchestrator.notebook_revision import strict_json

FILES = {"analysis.py", "test_analysis.py"}


def validate(raw, *, run_id, plan_sha256, cases):
    if not isinstance(raw, bytes) or len(raw) > 80000:
        raise ValueError("SCIENTIFIC_PROGRAM_LIMIT")
    value = strict_json(raw)
    if (not isinstance(value, dict) or set(value) != ({"schema","run_id","execution_plan_sha256","files","contract"} if value.get("schema")=="scientific-program/v2" else {"schema","run_id","execution_plan_sha256","files"})
            or value["schema"] not in {"scientific-program/v1","scientific-program/v2"} or value["run_id"] != run_id
            or value["execution_plan_sha256"] != plan_sha256
            or not isinstance(value["files"], dict) or set(value["files"]) != FILES):
        raise ValueError("SCIENTIFIC_PROGRAM_BINDING")
    if value["schema"] == "scientific-program/v2":
        from orchestrator.diagnostics_contract import program_contract
        program_contract(value["contract"])
    records = []
    for name, text in sorted(value["files"].items()):
        if not isinstance(text, str) or not text.strip():
            raise ValueError("SCIENTIFIC_PROGRAM_SOURCE_REQUIRED")
        source = text.encode()
        scientific_intake.scan(source, cases, kind="code")
        from orchestrator.git_publication import scan
        scan("context/"+name, source)
        record = {"path":name, "sha256":digest(source)}
        try:
            tree = ast.parse(text, filename=name)
            compile(tree, name, "exec", dont_inherit=True)
            if name == "analysis.py":
                entry = [node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == "main"]
                if len(entry) != 1 or [x.arg for x in entry[0].args.args] != ["input_root","output_root","contract"]:
                    raise ValueError("SCIENTIFIC_PROGRAM_ENTRYPOINT")
            record["compile"] = "PASS"
        except SyntaxError as error:
            record.update(compile="FAIL", line=error.lineno, message=error.msg)
        records.append(record)
    return value, records


@private_records.private_umask
def run(folder, files, environment):
    if not isinstance(files, dict) or set(files) != FILES or any(not isinstance(v, str) for v in files.values()):
        raise ValueError("SCIENTIFIC_PROGRAM_FILES")
    folder = Path(folder)
    harness = Path(__file__).with_name("scientific_program_harness.py").read_bytes()
    contents = {**{name:text.encode() for name,text in files.items()}, "run.py":harness}
    pins = {name:digest(raw) for name,raw in contents.items()}
    binding = {"files":pins,"environment":environment,"timeout_seconds":120,"patient_data":False}
    if folder.exists():
        private_records.check_tree(folder)
        if not (folder/"receipt.json").is_file():
            raise ValueError("SCIENTIFIC_PROGRAM_INCOMPLETE_INTENT")
        receipt = read(folder/"receipt.json")
        if receipt["binding"] != binding:
            raise ValueError("SCIENTIFIC_PROGRAM_TEST_BINDING_CHANGED")
        for name,pin in receipt["preserved_files"].items():
            if digest((folder/name).read_bytes()) != pin:
                raise ValueError("SCIENTIFIC_PROGRAM_TEST_EVIDENCE_CHANGED")
        return receipt
    private_records.mkdir(folder, parents=True)
    package, work = folder/"package", folder/"workspace"
    private_records.mkdir(package); private_records.mkdir(work)
    for name,raw in contents.items():
        write_once(package/name, raw)
    # Same reviewed namespace/mount and denial guard as notebook synthetic tests.
    argv = notebook_synthetic.command(environment, package, work, pins)
    atomic(folder/"intent.json", binding)
    started = time.monotonic()
    try:
        completed = subprocess.run(argv, capture_output=True, timeout=120, close_fds=True, stdin=subprocess.DEVNULL)
        out,err,code = completed.stdout,completed.stderr,completed.returncode
    except subprocess.TimeoutExpired as error:
        out,err,code = error.stdout or b"",error.stderr or b"",124
    write_once(folder/"stdout.log", out); write_once(folder/"stderr.log", err)
    if not (work/"isolation.json").is_file():
        raise ValueError("SCIENTIFIC_PROGRAM_ISOLATION_REQUIRED")
    isolation = read(work/"isolation.json")
    if isolation != {"status":"ISOLATED","network":"UNSHARED","credentials":False,
            "patient_mounts":False,"package_read_only":True,"workspace_writable":True,
            "denied_paths":isolation.get("denied_paths")} or type(isolation.get("denied_paths")) is not int or isolation["denied_paths"] < 1:
        raise ValueError("SCIENTIFIC_PROGRAM_ISOLATION_REQUIRED")
    result = read(work/"result.json") if (work/"result.json").is_file() else None
    if result and (result.get("files") != pins or result.get("schema") != "scientific-program-tests/v1"
                   or result.get("patient_data") is not False or result.get("network") is not False):
        raise ValueError("SCIENTIFIC_PROGRAM_TEST_RESULT_CHANGED")
    passed = bool(code == 0 and result and result.get("status") == "PASS"
        and type(result.get("tests_run")) is int and result["tests_run"] > 0
        and all(type(result.get(k)) is int and result[k] == 0 for k in
                ("failures","errors","skipped","expected_failures","unexpected_successes")))
    preserved = {str(p.relative_to(folder)):digest(p.read_bytes()) for p in folder.rglob("*") if p.is_file()}
    receipt = {"schema":"scientific-program-synthetic/v1","binding":binding,"status":"PASS" if passed else "FAIL",
        "tests":result,"isolation":isolation,"exit_code":code,"elapsed_seconds":time.monotonic()-started,
        "preserved_files":preserved,"no_model_call":True,"real_data_execution":False}
    atomic(folder/"receipt.json", receipt)
    return receipt


def prepare_artifacts(driver, value, pending, cases):
    from orchestrator.experiment_context import selection
    selected = selection(driver)
    if selected["item_number"] != 6:
        raise ValueError("SCIENTIFIC_PROGRAM_ITEM6_ONLY")
    original = (Path(pending["workspace"])/"analysis.program.json").read_bytes()
    program, compiled = validate(original, run_id=selected["run_id"], plan_sha256=selected["plan_sha256"], cases=cases)
    folder = driver.state/"scientific-programs"/("author-"+str(pending["round"]))
    write_once(folder/"analysis.program.json", original)
    for name,text in program["files"].items():
        write_once(folder/name, text.encode())
    tests = (run(folder/"synthetic", program["files"], driver.config["synthetic_environment"])
        if all(row["compile"] == "PASS" for row in compiled) else
        {"status":"FAIL","reason":"COMPILE_FAILED_NO_EXECUTION","no_model_call":True,"real_data_execution":False})
    provenance = {"program_sha256":digest(original),"execution_plan_sha256":selected["plan_sha256"],
        "source_call_id":pending["id"],"compile":compiled,"synthetic_tests_sha256":digest(json.dumps(tests,sort_keys=True).encode()),
        "scientific_approval":False,"real_data_execution":False,
        **({"program_contract":program["contract"]} if "contract" in program else {})}
    for kind,name,raw in [
        ("analysis_source","analysis-"+str(pending["round"])+".py",program["files"]["analysis.py"].encode()),
        ("analysis_tests","analysis-tests-"+str(pending["round"])+".py",program["files"]["test_analysis.py"].encode()),
        ("analysis_provenance","analysis-provenance-"+str(pending["round"])+".json",json.dumps(provenance,sort_keys=True).encode()),
        ("synthetic_tests","analysis-test-result-"+str(pending["round"])+".json",json.dumps(tests,sort_keys=True).encode())]:
        driver.artifact(value,kind,name,raw,pending["round"])
    value["program_result"] = {"folder":str(folder),"program_sha256":digest(original),
        "synthetic_status":tests["status"],"provenance":provenance}
