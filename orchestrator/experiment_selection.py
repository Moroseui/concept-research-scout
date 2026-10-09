"""Exact selected applications in one administrative review; no admission here."""
from orchestrator.review_contract import strict_json
from orchestrator.manual_executor import digest


def reviewed_plan(raw, manifest):
    value = strict_json(raw)
    if (not isinstance(value, dict) or value.get("schema") != "experiment-lane/v1"
            or type(value.get("item_number")) is not int or value["item_number"] not in (4, 6)):
        raise ValueError("EXPERIMENT_AUTHORING_ITEM_REQUIRED")
    files = manifest.get("files", {})
    named = "evidence/experiment-plan-item" + str(value["item_number"]) + ".json"
    # A named selection, when present, must agree. A legacy primary selection
    # still qualifies its one exact application, never another item or bytes.
    selected = named if named in files else "evidence/experiment-plan.json"
    if files.get(selected) != digest(raw):
        raise ValueError("REVIEWED_EXPERIMENT_PLAN_REQUIRED")
    return value
