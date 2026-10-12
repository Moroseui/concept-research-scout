"""Authentication and packaging for the accepted smoothing CPU program.

Infrastructure only: scientific source, definitions and thresholds remain exact
author6 bytes. This module neither launches execution nor grants an allowance.
"""
import csv
import hashlib
import io
import json
from pathlib import Path
import re

RUN = "diagnostics-b203ee1ce27e909d9d78d44a"
PINS = {
    "input-contract.json": "8c9a1eb91016f435baaf4fe03bb82109ece7c70d09d42488fea327c067df186e",
    "cohort.json": "45c5746f60e2275383a2c4f4096295fe7a171da85a73737c5a35a8cc6fc9fe86",
    "capture.jsonl": "c742b81d9f561dec9cb330c8f4b59f6c9df36b5136819f3bbf1a171c8891b119",
    "split.csv": "da79e94bdae3f59d23db497d5f26f0d57aa4f279847fe57ec9a8d05ebcf18843",
    "execution-plan.json": "613bb59adc7836c8a4120e0ff9e6e2df5befe6d643bb263e0a86cc84dca228a5",
}
PROGRAM = "0ad05ea01cb511c2f946a05e48bcfe745de7121837c46067a062d465a2a42c20"
CODE = "decbe7274ffa207c32f8574b68a011b7f60b2d685d02b188c37dfed02f70c66c"
TESTS = "2445e6bdaad43d9e3c0e1900e7afe15eaccf631db32c44b4a6e1d4a30d90a525"
SPEC = "4d4f43524f400037393b656a12da80e66fc862aafafee911d37732b08b16baa8"
REVIEW = "6e561af4371d3d8a726b4983056d919ae989cb905f5bf6470232b8d689b18c56"
APPROVAL = "f0f25848f7187a77f211be67c8ed17e9fe43101f2484161c509b7cfb662648df"
ENVIRONMENT = "0f71b0d0a8131090bca668b7da55e3aecf70392687b23dd7f7a264f0532fb34a"


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def require(ok, reason):
    if not ok:
        raise ValueError("IDEA2_CPU_" + reason)


def encoded(value):
    return json.dumps(value, sort_keys=True, allow_nan=False).encode()


def authenticate_metadata(bodies):
    """Authenticate identifier metadata before deriving or opening payload paths."""
    require(set(bodies) == set(PINS), "EXACT_METADATA")
    require(all(sha(bodies[name]) == pin for name, pin in PINS.items()), "METADATA_HASH")
    from orchestrator.diagnostics_contract import input_contract, strict
    contract = input_contract(strict(bodies["input-contract.json"]),
                              bodies["cohort.json"], bodies["capture.jsonl"])
    dev = strict(bodies["cohort.json"])["cases"]
    rows = list(csv.DictReader(io.StringIO(bodies["split.csv"].decode("utf-8"))))
    require(len(rows) == 149 and len({r["case_id"] for r in rows}) == 149, "SPLIT_MEMBERSHIP")
    excluded = sorted(r["case_id"] for r in rows if r["population"] == "reserved")
    census = {r["case_id"] for r in rows if r["population"] == "census"}
    require(len(set(dev)) == len(dev) == 99 and len(excluded) == 49 and len(census) == 100
            and set(dev) <= census and not set(dev) & set(excluded), "EXCLUDED_MEMBERSHIP")
    mentioned = set(re.findall(r"sub-stroke[0-9]+", "\n".join(contract["files"])))
    require(mentioned == set(dev), "PAYLOAD_IDENTIFIER_MEMBERSHIP")
    plan = strict(bodies["execution-plan.json"])
    require(plan["run_id"] == RUN and plan["limits"] == {
        "gpu": False, "scientific_calls": 30, "total_micro_usd": 100000000, "training": False},
        "ORIGINAL_PLAN_CHANGED")
    return {"contract": contract, "development_cases": sorted(dev),
            "excluded_cases": excluded, "plan": plan}


def authenticate_program(program_raw, spec_raw, review_raw, approval_raw):
    require(sha(program_raw) == PROGRAM and sha(spec_raw) == SPEC and
            sha(review_raw) == REVIEW and sha(approval_raw) == APPROVAL, "SCIENTIFIC_APPROVAL_HASH")
    from orchestrator.diagnostics_contract import strict, program_contract
    program, review, approval = map(strict, (program_raw, review_raw, approval_raw))
    require(program["schema"] == "scientific-program/v2" and program["run_id"] == RUN
            and program["execution_plan_sha256"] == PINS["execution-plan.json"], "PROGRAM_IDENTITY")
    require(set(program["files"]) == {"analysis.py", "test_analysis.py"}
            and sha(program["files"]["analysis.py"].encode()) == CODE
            and sha(program["files"]["test_analysis.py"].encode()) == TESTS, "AUTHOR_BYTES_CHANGED")
    require(review["verdict"] == "APPROVE" and review["findings"] == [], "SCIENTIFIC_APPROVE_REQUIRED")
    require(approval["schema"] == "reviewed-execution-artifacts/v1"
            and approval["review_sha256"] == REVIEW
            and approval["selection"]["run_id"] == RUN
            and approval["selection"]["item_number"] == 6
            and approval["selection"]["plan_sha256"] == PINS["execution-plan.json"]
            and approval["code_files"]["analysis.program.json"]["sha256"] == PROGRAM
            and approval["code_files"]["analysis.py"]["sha256"] == CODE,
            "APPROVED_PROGRAM_BINDING")
    # This is scientific acceptance only. Independent implementation approval
    # and a durable, native, one-use execution admission are still required.
    return program, program_contract(program["contract"])


def build_contract(metadata, program_contract, source):
    require(re.fullmatch("[0-9a-f]{40}", source) is not None, "RUNTIME_SOURCE")
    runtime = {"run_id": RUN, "source": source, "spec_sha256": SPEC, "code_sha256": CODE,
               "execution_plan_sha256": PINS["execution-plan.json"],
               "input_contract_sha256": PINS["input-contract.json"],
               "environment_sha256": ENVIRONMENT}
    runtime["input_verification"] = {
        "schema": "fixed3x3-input-verification/v1", **runtime,
        "input_capture_sha256": PINS["capture.jsonl"], "cohort_sha256": PINS["cohort.json"],
        "exclusions_metadata_sha256": PINS["split.csv"],
        "development_cases": metadata["development_cases"], "excluded_cases": metadata["excluded_cases"],
        "files": {name: {k: row[k] for k in ("sha256", "bytes")}
                  for name, row in metadata["contract"]["files"].items()}}
    return {**program_contract, "execution_plan": metadata["plan"], "runtime": runtime}


def verify_tree(root, expected):
    """Check exact membership and every hash; used before and after execution."""
    root = Path(root)
    require(root.is_absolute() and root.is_dir()
            and not any(p.is_symlink() for p in (root, *root.parents)), "INPUT_ROOT")
    paths = list(root.rglob("*"))
    require(all(not p.is_symlink() and (p.is_file() or p.is_dir()) for p in paths), "INPUT_ALIAS")
    actual = {str(p.relative_to(root)): p for p in paths if p.is_file()}
    require(set(actual) == set(expected), "INPUT_MEMBERSHIP")
    for name, path in actual.items():
        require(not Path(name).is_absolute() and ".." not in Path(name).parts, "INPUT_PATH")
        before = path.stat()
        require(before.st_nlink == 1 and before.st_size == expected[name]["bytes"], "INPUT_SIZE")
        digest = hashlib.sha256()
        with path.open("rb") as stream:
            for block in iter(lambda: stream.read(1024 * 1024), b""):
                digest.update(block)
        after = path.stat()
        require((before.st_ino, before.st_size, before.st_mtime_ns) ==
                (after.st_ino, after.st_size, after.st_mtime_ns)
                and digest.hexdigest() == expected[name]["sha256"], "INPUT_HASH")
    return {"files": len(actual), "bytes": sum(row["bytes"] for row in expected.values()),
            "manifest_sha256": sha(encoded(expected))}


WORKER = """import importlib.util,json,os
from pathlib import Path
os.umask(0o077)
contract=json.loads(Path('/package/contract.json').read_bytes())
spec=importlib.util.spec_from_file_location('accepted_idea2','/package/analysis.py')
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
module.main(Path('/content/drive/MyDrive/isles-pilot'),Path('/workspace/return'),contract)
"""
