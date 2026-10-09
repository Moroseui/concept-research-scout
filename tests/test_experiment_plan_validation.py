"""Pure relocation proof; only synthetic plans and real validators, no providers."""
import ast
import copy
import hashlib
import inspect
import json
import os
from pathlib import Path
import subprocess
import sys
import textwrap

import pytest
from orchestrator import experiment_plan_validation as pure

# Exact source/AST identities captured from reviewed-for-integration base 4cb7d663.
# This identifies the old code; it does not claim independent source approval.
# AST pins include empty fields explicitly (Python 3.13 changed dump defaults).
ORIGINALS = {
    "validate_fits": ("c441a7ecb3a03e96b65b4f03ecb7fa6c0c7c16aee07e5909f52cf50ac433d1b6", "1e3db3023b96151e23bc298983f1219430a0a9fa3d02e9a437d05cdac66e91ca"),
    "number": ("080de12cbc03fe13cbbcf134bed0a92ff288376e15b001d8cffad5623f0bc9a1", "806d34f63b32d660f339c2a36446984067c670124a5c7f69868e403a99f90936"),
    "contract": ("dfab51b881c1d7203a9f1e189a8930d336141ab98454f59c7a4bf33a48db8b5f", "6e307e91c6e1f79973f84119662799b21307a96059c3756b96648f90f26d12f1"),
}


def example():
    fits = [{"fit_id": ident, "stage": "SMOKE", "arm": "synthetic-arm", "fold": 0,
             "realization": "synthetic", "outputs": ["timing.json", "validation.json"],
             "validation_checks": ["synthetic-check"]} for ident in ("a100", "h100", "b200", "arm-smoke")]
    fits.append({**fits[-1], "fit_id": "full", "stage": "FULL", "fold": 1})
    return {"schema": "scientific-execution-plan/v1", "run_id": "synthetic-run",
            "operator_scope_sha256": "a" * 64, "dispatch_mode": "incremental", "fits": fits,
            "preprocessing": [], "full_training": {"schema": "measured-full-training/v1",
                "timing_file": "timing.json", "benchmark_fit_ids": ["a100", "h100", "b200"],
                "benchmark_comparability_id": "synthetic-only", "resume_fit_id": "arm-smoke",
                "full_fits": [{"fit_id": "full", "timing_fit_id": "arm-smoke", "epochs": 1,
                    "fixed_seconds": "0", "overhead_micro_usd": 0, "assumption": "Synthetic fixture only."}]}}


@pytest.mark.parametrize("name", ORIGINALS)
def test_exact_original_function_source_and_ast_preserved(name):
    source = inspect.getsource(getattr(pure, name))
    assert hashlib.sha256(source.encode()).hexdigest() == ORIGINALS[name][0]
    node = ast.parse(source).body[0]
    options = {"include_attributes": False}
    if "show_empty" in inspect.signature(ast.dump).parameters:
        options["show_empty"] = True
    assert hashlib.sha256(ast.dump(node, **options).encode()).hexdigest() == ORIGINALS[name][1]


def test_existing_public_callables_are_the_identical_validators():
    from orchestrator import experiment_dispatch as dispatch, experiment_projection as projection
    assert dispatch.validate_fits is pure.validate_fits
    assert projection.contract is pure.contract
    assert projection.number is pure.number
    plan = example()
    assert dispatch.validate_fits(plan, incremental=True) is plan["fits"]
    assert projection.contract(plan) == pure.contract(plan)
    assert projection.number("0.1") == pure.number("0.1")


@pytest.mark.parametrize("damage,code", [
    ("empty", "EXPERIMENT_FROZEN_FITS_REQUIRED"),
    ("fold-bool", "EXPERIMENT_FROZEN_FIT_FIELDS"),
    ("negative-fold", "EXPERIMENT_FROZEN_FIT_FIELDS"),
    ("unknown-stage", "EXPERIMENT_FROZEN_FIT_FIELDS"),
    ("missing-realization", "EXPERIMENT_FROZEN_FIT_FIELDS"),
    ("extra", "EXPERIMENT_FROZEN_FIT_FIELDS"),
    ("empty-output", "EXPERIMENT_FROZEN_FIT_FIELDS"),
    ("missing-preprocessing-id", "EXPERIMENT_FROZEN_FIT_FIELDS"),
])
def test_fit_refusals_preserve_exact_codes(damage, code):
    plan = example()
    if damage == "empty": plan["fits"] = []
    elif damage == "fold-bool": plan["fits"][0]["fold"] = True
    elif damage == "negative-fold": plan["fits"][0]["fold"] = -1
    elif damage == "unknown-stage": plan["fits"][0]["stage"] = "UNKNOWN"
    elif damage == "missing-realization": del plan["fits"][0]["realization"]
    elif damage == "extra": plan["fits"][0]["extra"] = True
    elif damage == "empty-output": plan["fits"][0]["outputs"] = []
    else: plan["preprocessing"] = [{"id": "synthetic"}]
    with pytest.raises(ValueError, match="^" + code + "$"):
        pure.validate_fits(plan, incremental=True)


@pytest.mark.parametrize("damage,code", [
    ("contract", "EXPERIMENT_PROJECTION_CONTRACT"),
    ("path", "EXPERIMENT_PROJECTION_TIMING_FILE"),
    ("duplicate-fit", "EXPERIMENT_PROJECTION_FITS"),
    ("repeat-benchmark", "EXPERIMENT_PROJECTION_FROZEN_SELECTION"),
    ("epochs-bool", "EXPERIMENT_PROJECTION_FULL_FIT"),
    ("nonfinite", "EXPERIMENT_PROJECTION_NUMBER"),
    ("other-arm", "EXPERIMENT_PROJECTION_ARM_TIMING"),
    ("no-timing", "EXPERIMENT_PROJECTION_UNDECLARED_TIMING"),
])
def test_projection_refusals_preserve_exact_codes(damage, code):
    plan = example(); value = plan["full_training"]
    if damage == "contract": value["schema"] = "unknown"
    elif damage == "path": value["timing_file"] = "../timing.json"
    elif damage == "duplicate-fit": plan["fits"].append(copy.deepcopy(plan["fits"][0]))
    elif damage == "repeat-benchmark": value["benchmark_fit_ids"] = ["a100"] * 3
    elif damage == "epochs-bool": value["full_fits"][0]["epochs"] = True
    elif damage == "nonfinite": value["full_fits"][0]["fixed_seconds"] = "NaN"
    elif damage == "other-arm": plan["fits"][-1]["arm"] = "other"
    else: plan["fits"][0]["outputs"] = ["validation.json"]
    with pytest.raises(ValueError, match="^" + code + "$"):
        pure.contract(plan)


@pytest.mark.parametrize("value", [True, None, [], {}, "-1", "NaN", "Infinity"])
def test_numeric_refusals_preserve_exact_code(value):
    with pytest.raises(ValueError, match="^EXPERIMENT_PROJECTION_NUMBER$"):
        pure.number(value)


def test_real_author_plan_validation_imports_no_paid_module_or_sdk():
    root = Path(__file__).resolve().parents[1]
    script = r"""
import importlib.abc,json,sys
blocked = {'modal', 'orchestrator.modal_provider', 'orchestrator.modal_executor',
    'orchestrator.modal_item4_provider', 'orchestrator.modal_preprocessing_provider',
    'orchestrator.experiment_dispatch', 'orchestrator.experiment_projection',
    'orchestrator.experiment_collection', 'orchestrator.experiment_provisioning'}
class NoPaidImports(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        if fullname in blocked or fullname.startswith('modal.'):
            raise RuntimeError('PAID_MODULE_IMPORT:' + fullname)
sys.meta_path.insert(0, NoPaidImports())
from orchestrator import experiment_plan_validation as pure, experiment_plan_output as authored
plan = json.loads(sys.stdin.read())
selected = {'run_id':plan['run_id'], 'plan_sha256':plan['operator_scope_sha256']}
assert authored.validate(json.dumps(plan).encode(), selected, frozenset(), b'{}') == plan
for field, value, code in [('fold', True, 'EXPERIMENT_FROZEN_FIT_FIELDS'),
                            ('validation_checks', [], 'EXPERIMENT_RESULT_CHECK_SELECTION')]:
    changed = json.loads(json.dumps(plan)); changed['fits'][0][field] = value
    try: authored.validate(json.dumps(changed).encode(), selected, frozenset(), b'{}')
    except ValueError as exc: assert str(exc) == code, str(exc)
    else: raise AssertionError('EXPECTED_REFUSAL')
assert not blocked.intersection(sys.modules)
assert not any(name.startswith('modal.') for name in sys.modules)
print('PURE_AUTHOR_PLAN_VALIDATION_PASSED_WITHOUT_PAID_IMPORTS')
"""
    env = {**os.environ, "PYTHONPATH": str(root), "PYTHONDONTWRITEBYTECODE": "1"}
    result = subprocess.run([sys.executable, "-B", "-s", "-c", textwrap.dedent(script)],
                            input=json.dumps(example()), text=True, capture_output=True,
                            env=env, cwd=root, timeout=30)
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == "PURE_AUTHOR_PLAN_VALIDATION_PASSED_WITHOUT_PAID_IMPORTS"


def test_author_schema_exposes_exact_projection_key_and_all_required_fields():
    from orchestrator.experiment_plan_output import instructions
    schema = pure.author_schema()
    row = example()['full_training']['full_fits'][0]
    assert set(schema['full_training.full_fits[]']['required_exact_fields']) == set(row)
    assert set(schema['full_training']['required_exact_fields']) == set(example()['full_training'])
    delivered = instructions({'run_id': 'synthetic-run', 'plan_sha256': 'a'*64})
    assert json.dumps(schema, sort_keys=True) in delivered
    broken = example()
    row = broken['full_training']['full_fits'][0]
    row['applicability_assumption'] = row.pop('assumption')
    with pytest.raises(ValueError, match='^EXPERIMENT_PROJECTION_FULL_FIT$'):
        pure.contract(broken)
    row['assumption'] = row.pop('applicability_assumption')
    assert pure.contract(broken)[0] == broken['full_training']
