"""Metadata integrity tests only; no notebook cells, patients or models execute."""
import ast
import importlib.util
import json
from pathlib import Path
import pytest
from orchestrator.context_budget import sha
from orchestrator.git_publication import scan

ROOT=Path(__file__).resolve().parents[1]
DIRECTORY=ROOT/"projects/isles24/manual/sprint10"
spec=importlib.util.spec_from_file_location("sprint10_reference",DIRECTORY/"validate_reference.py")
validator=importlib.util.module_from_spec(spec);spec.loader.exec_module(validator)

@pytest.fixture
def inputs(tmp_path):
    split=tmp_path/"split_manifest.csv";split.write_text("synthetic split metadata\n")
    path=tmp_path/"excluded_cases.json";path.write_text(json.dumps(["synthetic-case-A"]))
    ref={"path":str(path),"sha256":sha(path.read_bytes()),"count":1}
    return split,ref


def test_reference_and_fingerprint_bind_membership(inputs):
    split,ref=inputs;split_sha=sha(split.read_bytes())
    assert validator.load_exclusions(ref,split,split_sha)==frozenset(["synthetic-case-A"])
    identity={"exclusions_sha256":ref["sha256"],"exclusions_count":1,"split_manifest_sha256":split_sha}
    record={"run_identity":identity,"fingerprint":validator.comparison_fingerprint(identity)}
    result=validator.validate_comparison_reference(record,ref,split,split_sha)
    assert result["status"]=="REFERENCE_INTEGRITY_VALID" and result["scientific_acceptance"] is False
    assert validator.comparison_fingerprint(dict(identity,exclusions_sha256="a"*64))!=record["fingerprint"]
    with pytest.raises(ValueError,match="FINGERPRINT_MISMATCH"):
        validator.validate_comparison_reference(dict(record,fingerprint="stale"),ref,split,split_sha)
    with pytest.raises(ValueError,match="BINDING_MISMATCH"):
        validator.validate_comparison_reference(dict(record,run_identity=dict(identity,exclusions_count=2)),ref,split,split_sha)


@pytest.mark.parametrize("failure",["hash","count","duplicate","split","location"])
def test_reference_failures(inputs,failure,tmp_path):
    split,ref=inputs;split_sha=sha(split.read_bytes())
    if failure=="hash":Path(ref["path"]).write_text("changed")
    elif failure=="count":ref["count"]=2
    elif failure=="duplicate":
        Path(ref["path"]).write_text(json.dumps(["synthetic-case-A"]*2));ref.update(sha256=sha(Path(ref["path"]).read_bytes()),count=2)
    elif failure=="split":split.write_text("changed")
    else:
        other=tmp_path/"other";other.mkdir();ref["path"]=str(other/"excluded_cases.json")
    with pytest.raises(ValueError):validator.load_exclusions(ref,split,split_sha)


def test_unexecuted_notebook_retains_assertion_and_validator_exactly():
    notebook=json.loads((DIRECTORY/"isles24_sprint10_r2_exclusion_reference.ipynb").read_text())
    sources=["".join(cell["source"]) for cell in notebook["cells"]]
    for cell,source in zip(notebook["cells"],sources):
        if cell["cell_type"]=="code":
            assert cell["execution_count"] is None and not cell["outputs"]
            # Colab shell/magic setup lines are not Python statements.
            ast.parse("\n".join(line for line in source.splitlines() if not line.startswith(("!","%"))))
    assert "assert len(CASES) == 99" in sources[2]
    assert (DIRECTORY/"validate_reference.py").read_text() in sources[2]
    assert '"exclusions_sha256": EXCLUSIONS["sha256"]' in sources[4]
    assert "validate_comparison_reference(" in sources[9]
    for path in DIRECTORY.iterdir():
        if path.is_file():scan("context/"+path.name,path.read_bytes())
