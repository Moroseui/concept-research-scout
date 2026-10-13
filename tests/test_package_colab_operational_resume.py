import base64
import copy
import hashlib
import json
import os
from pathlib import Path
import pytest
from tools.package_colab_operational_resume import render, ORIGINALS
from tools.colab_operational_resume import PROFILES

@pytest.mark.parametrize("arm", list(ORIGINALS))
def test_only_transport_changed_and_scientific_sources_are_exact(arm):
    fixtures = Path(os.environ["COLAB_EXACT_MODULE_FIXTURES"])
    root = Path(__file__).parents[1]
    raw = (fixtures / ("13B_" + arm + ".ipynb")).read_bytes()
    original = json.loads(raw)
    approval = {"source_sha": "a" * 40, "report_sha256": "b" * 64}
    result = json.loads(render(raw, arm, root, approval))
    assert len(result["cells"]) == len(original["cells"]) + 3
    unwrapped = copy.deepcopy(result["cells"])
    unwrapped.pop(0)
    login_index = next(i for i, cell in enumerate(unwrapped) if cell.get("metadata", {}).get("tags") == ["all-interactions-first"])
    login = unwrapped.pop(login_index)
    assert "_message.blocking_request" in "".join(login["source"])
    materializer = unwrapped.pop(20)
    for i, cell in enumerate(original["cells"]):
        if i != 20:
            assert unwrapped[i] == cell
    assert "run_notebook(pipeline, DELIVERY_ARM, DELIVERY_FOLDS)" in "".join(unwrapped[20]["source"])
    assert not any(token in "".join(unwrapped[20]["source"]) for token in ("drive.mount(", "auth.authenticate_user(", "_message.blocking_request("))
    assert "pipeline.install_dependencies()" in "".join(unwrapped[20]["source"])
    text = "".join(materializer["source"])
    # Parse literals only; never execute the materializer or notebook in this test.
    import ast
    assignment = next(n for n in ast.parse(text).body if isinstance(n, ast.Assign))
    helpers = ast.literal_eval(assignment.value)
    for name, row in helpers.items():
        body = base64.b64decode(row["base64"])
        assert hashlib.sha256(body).hexdigest() == row["sha256"]
        assert body == (root / "tools" / name).read_bytes()
    assert all(not c.get("outputs") and c.get("execution_count") is None for c in result["cells"])
    assert result["metadata"]["operational_repair"]["new_hardware_performance_qualified"] is False
    with pytest.raises(ValueError, match="Exact original"):
        render(raw + b" ", arm, root, approval)
