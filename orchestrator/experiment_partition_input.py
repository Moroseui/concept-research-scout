"""One registered membership original, sealed only after actual review delivery.

No split generation, provider access or arbitrary host paths. Legacy selections
remain unchanged; the new input is available only through an explicit item4 plan.
"""
import json
import re
from pathlib import Path
from orchestrator import context_budget as cb, scientific_intake as intake
from orchestrator.manual_executor import digest
from orchestrator import private_records as pr

FILE = "frozen-partitions.json"
MODE = "registered-partitions/v1"
SCHEMA = "reviewed-preprocessing-partitions/v1"


def enabled(config):
    ref = config.get("frozen_partitions")
    if ref is None: return False
    from orchestrator.experiment_plan_output import enabled as authored
    if (not authored(config) or config.get("item_number") != 4
            or not isinstance(ref, dict) or set(ref) != {"schema", "view_id", "sha256", "manifest_sha256"}
            or ref["schema"] != MODE or not isinstance(ref["view_id"], str)
            or not re.fullmatch("[A-Za-z0-9-]{1,80}", ref["view_id"])
            or any(not isinstance(ref[k], str) or not re.fullmatch("[a-f0-9]{64}", ref[k])
                   for k in ("sha256", "manifest_sha256"))):
        raise ValueError("EXPERIMENT_PARTITIONS_SELECTION")
    return True


def resolve(config, root):
    """Re-scan the protected registered bytes; selection does not approve science."""
    if not enabled(config): return None
    ref = config["frozen_partitions"]
    descriptors, files = intake.load_views(root, config["private_intake"],
        stage="run_spec_review", idea_ids=config["idea_ids"])
    # Reproduce the real producer's authenticated navigation descriptors.
    from orchestrator.manual_context import _json_reading_copy
    for descriptor, content in files:
        if descriptor["path"].endswith("-omissions.json"):
            _json_reading_copy(descriptor, content)
    registry = json.loads(cb.relative_file(root, config["private_intake"]["path"]).read_bytes())
    matches = [row for row in registry["views"] if row["id"] == ref["view_id"]]
    if len(matches) != 1: raise ValueError("EXPERIMENT_PARTITIONS_REGISTERED_INPUT_REQUIRED")
    row = matches[0]
    if any(row[k] != ref[k] for k in ("sha256", "manifest_sha256")):
        raise ValueError("EXPERIMENT_PARTITIONS_REGISTRATION_CHANGED")
    raw = pr.check(cb.relative_file(root, row["path"])).read_bytes()
    manifest = json.loads(pr.check(cb.relative_file(root, row["manifest"])).read_bytes())
    spans = manifest["spans"]
    if (manifest["original_sha256"] != ref["sha256"] or manifest["view_sha256"] != ref["sha256"]
            or manifest["omitted_units"] or len(spans) != 1
            or spans[0]["start"] != 0 or spans[0]["end"] != len(raw)
            or spans[0]["sha256"] != digest(raw) or not spans[0]["keep"]
            or spans[0]["kind"] != "per_patient"):
        raise ValueError("EXPERIMENT_PARTITIONS_EXACT_ORIGINAL_REQUIRED")
    selected = [d for d in descriptors if d["id"] in
                {ref["view_id"]+"-view.txt", ref["view_id"]+"-omissions.json"}]
    if len(selected) != 2: raise ValueError("EXPERIMENT_PARTITIONS_DESCRIPTOR_REQUIRED")
    seal = {"schema":MODE, "package_name":FILE, "registry_sha256":config["private_intake"]["sha256"],
        "view_id":row["id"], "source_path":row["path"], "sha256":row["sha256"],
        "manifest_path":row["manifest"], "manifest_sha256":row["manifest_sha256"],
        "cohort_sha256":manifest["cohort_sha256"]}
    return seal, raw, descriptors, selected



def delivered_navigation(workspace,measurement,prompt,index):
    """Exact inline descriptor or the producer's one authenticated index file."""
    encoded=cb.encoded(index)
    if encoded in prompt:return True
    matches=[d for d in measurement.get('workspace_files',[])
        if d.get('id')=='scientific-review-artifact-index']
    if len(matches)!=1:return False
    nav=matches[0]
    if (set(nav)!={'id','path','sha256','bytes','characters','page_lines','delivery'}
            or cb.encoded(nav) not in prompt or type(nav['page_lines']) is not int
            or not 1<=nav['page_lines']<=100):return False
    raw=pr.check(cb.relative_file(workspace,nav['path'])).read_bytes()
    if (digest(raw)!=nav['sha256'] or len(raw)!=nav['bytes'] or
            len(raw.decode())!=nav['characters']):
        raise ValueError('EXPERIMENT_PARTITIONS_REVIEW_DELIVERY_CHANGED')
    return raw.decode().split('\n\n').count(encoded)==1


def reviewed(config, root, workspace, measurement, prompt):
    resolved = resolve(config, root)
    if resolved is None: return None
    seal, raw, descriptors, selected = resolved
    index = measurement.get("private_scientific_index")
    if (not isinstance(index, dict) or index.get("registry_sha256") != seal["registry_sha256"]
            or not delivered_navigation(workspace,measurement,prompt,index)
            or measurement.get("private_scientific_views") != descriptors):
        raise ValueError("EXPERIMENT_PARTITIONS_REVIEW_DELIVERY_REQUIRED")
    index_raw = pr.check(cb.relative_file(workspace, index["path"])).read_bytes()
    if (digest(index_raw) != index["sha256"] or json.loads(index_raw) != {
            "schema":"private-scientific-navigation/v1", "registry_sha256":seal["registry_sha256"],
            "views":descriptors}):
        raise ValueError("EXPERIMENT_PARTITIONS_REVIEW_DELIVERY_CHANGED")
    for descriptor in [index, *selected]:
        if measurement.get("workspace_files", []).count(descriptor) != 1:
            raise ValueError("EXPERIMENT_PARTITIONS_REVIEW_DELIVERY_REQUIRED")
        delivered = pr.check(cb.relative_file(workspace, descriptor["path"])).read_bytes()
        if digest(delivered) != descriptor["sha256"]:
            raise ValueError("EXPERIMENT_PARTITIONS_REVIEW_DELIVERY_CHANGED")
    return seal


def plan_pin(config, root):
    resolved = resolve(config, root)
    return resolved[0]["sha256"] if resolved else None


def require_plan(plan, pin):
    from orchestrator.experiment_environment_requirements import PLAN_SCHEMA, PREPROCESSING_SCHEMA
    expected_schema = PREPROCESSING_SCHEMA if plan.get("schema") == PLAN_SCHEMA else SCHEMA
    rows = plan.get("preprocessing", [])
    if pin is None:
        if any(r.get("schema") in {SCHEMA, PREPROCESSING_SCHEMA} or "partitions_sha256" in r for r in rows):
            raise ValueError("EXPERIMENT_PARTITIONS_UNSELECTED")
    elif not rows or any(r.get("schema") != expected_schema or r.get("partitions_sha256") != pin for r in rows):
        raise ValueError("EXPERIMENT_PARTITIONS_PLAN_BINDING")
