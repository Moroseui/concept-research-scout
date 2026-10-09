"""Deterministic model-input assembly; no admission, authority or state mutation.

The register is reviewed source, not model-produced authority. Exact quotations
are checked against immutable originals before scope selection. Historical
sources without a context manifest retain their original input representation.
"""
from collections import OrderedDict
import hashlib
import json
from pathlib import Path
import re

ASSEMBLY_MARKER = "PROJECT INPUT: compact-state/v1\n"
LIMIT = 200_000
STATE_LIMIT = 20_000
POLICY_LIMIT = 8_000
DECISION_COUNT = 8
PROJECT = "projects/isles24/context"
TYPES = {"stop", "adverse finding", "protocol amendment", "constraint", "open question"}


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def encoded(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


class ContextError(ValueError):
    pass


class ContextTooLarge(ContextError):
    def __init__(self, measurement):
        self.measurement = measurement
        super().__init__("MODEL_INPUT_LIMIT_EXCEEDED " + encoded(measurement))


def measure(sections, *, schema_text=""):
    rows = {name: {"characters": len(text), "utf8_bytes": len(text.encode("utf-8"))}
            for name, text in sections.items()}
    body = ASSEMBLY_MARKER + "\n\n".join("===== " + name + " =====\n" + text for name, text in sections.items())
    result = {"characters": len(body) + len(schema_text),
              "utf8_bytes": len(body.encode("utf-8")) + len(schema_text.encode("utf-8")),
              "limit_characters": LIMIT, "sections": rows,
              "schema_characters": len(schema_text), "tokens": None,
              "input_sha256": sha(body.encode("utf-8"))}
    if result["characters"] > LIMIT:
        raise ContextTooLarge(result)
    return body, result


def check_final(text, *, schema_text=""):
    total = len(text) + len(schema_text)
    if total > LIMIT:
        raise ContextTooLarge({"characters": total, "utf8_bytes": len(text.encode()) + len(schema_text.encode()),
                               "limit_characters": LIMIT,
                               "sections": {"composed_input": len(text), "output_schema": len(schema_text)}})
    return text


def relative_file(root, name):
    root = Path(root).resolve()
    rel = Path(name)
    if rel.is_absolute() or ".." in rel.parts:
        raise ContextError("CONTEXT_SOURCE_PATH")
    path = root / rel
    if any(part.is_symlink() for part in [path, *list(path.parents)[:len(rel.parts)-1]]):
        raise ContextError("CONTEXT_SOURCE_SYMLINK")
    if not path.is_file() or not path.resolve().is_relative_to(root):
        raise ContextError("CONTEXT_SOURCE_MISSING:" + name)
    return path


def enabled(root, project="isles24"):
    return project in ("isles24", "isles24-prediction") and (Path(root) / PROJECT / "manifest.json").is_file()


def original_bytes(root, ref, manifest):
    raw = relative_file(root, ref['path']).read_bytes()
    # The decisions seed is an immutable prefix of an append-only archive.
    # This preserves its exact source SHA without copying private historical
    # bytes to a new repository path or invalidating unrelated later entries.
    binding = next((item for item in manifest['sources'] if item['path'] == ref['path']), None)
    if binding and 'prefix_bytes' in binding:
        raw = raw[:binding['prefix_bytes']]
    return raw


def load(root):
    manifest = json.loads(relative_file(root, PROJECT + "/manifest.json").read_text())
    if manifest.get("schema") != "project-input-context/v1":
        raise ContextError("CONTEXT_MANIFEST_SCHEMA")
    content = {}
    for key, maximum in (("state", STATE_LIMIT), ("policy", POLICY_LIMIT), ("obligations", None)):
        ref = manifest[key]
        raw = relative_file(root, ref["path"]).read_bytes()
        if sha(raw) != ref["sha256"]:
            raise ContextError("CONTEXT_DERIVATION_CHANGED:" + key)
        text = raw.decode("utf-8")
        if maximum is not None and len(text) > maximum:
            raise ContextError("CONTEXT_DERIVATION_LIMIT:" + key)
        content[key] = text
    register = json.loads(content["obligations"])
    if register.get("schema") != "project-obligations/v1":
        raise ContextError("OBLIGATION_REGISTER_SCHEMA")
    # Append-only decisions are deliberately NOT pinned at their current length.
    # Their seed prefix is preserved; later tagged entries are selected below.
    for binding in manifest["sources"]:
        raw = relative_file(root, binding["path"]).read_bytes()
        checked = raw[:binding["prefix_bytes"]] if "prefix_bytes" in binding else raw
        if sha(checked) != binding["sha256"]:
            raise ContextError("CONTEXT_SOURCE_RECONCILIATION_REQUIRED:" + binding["path"])
    seen = set()
    originals = {}
    for row in register["obligations"]:
        if set(row) != {"id", "type", "scope", "status", "text", "source", "disposition", "severity"}:
            raise ContextError("OBLIGATION_FIELDS")
        if not isinstance(row["id"], str) or row["id"] in seen or row["type"] not in TYPES or row["status"] not in ("open", "closed"):
            raise ContextError("OBLIGATION_ID_TYPE_STATUS")
        if row["severity"] not in ("unspecified", "blocker", "major", "minor", "advisory"):
            raise ContextError("OBLIGATION_SEVERITY")
        seen.add(row["id"])
        scope = row["scope"]
        if set(scope) != {"project", "idea_ids", "stages"} or any(
                not isinstance(scope[k], list) or not scope[k] or any(not isinstance(x, str) or not x for x in scope[k])
                for k in scope):
            raise ContextError("OBLIGATION_SCOPE")
        ref = row["source"]
        if set(ref) != {"path", "sha256", "start", "end", "original_path"}:
            raise ContextError("OBLIGATION_SOURCE_FIELDS")
        if ref["path"] not in originals:
            originals[ref["path"]] = original_bytes(root, ref, manifest)
        raw = originals[ref["path"]]
        start, end = ref["start"], ref["end"]
        if (sha(raw) != ref["sha256"] or type(start) is not int or type(end) is not int
                or not 0 <= start < end <= len(raw)
                or not isinstance(row["text"], str) or raw[start:end].decode("utf-8") != row["text"]):
            raise ContextError("OBLIGATION_EXACT_QUOTE_REQUIRED:" + row["id"])
        if row["status"] == "closed":
            resolution = row["disposition"]
            if not isinstance(resolution, dict) or set(resolution) != {"path", "sha256", "start", "end", "text"}:
                raise ContextError("OBLIGATION_CITED_RESOLUTION_REQUIRED")
            resolved = relative_file(root, resolution["path"]).read_bytes()
            a, b = resolution["start"], resolution["end"]
            if (sha(resolved) != resolution["sha256"] or type(a) is not int or type(b) is not int
                    or not 0 <= a < b <= len(resolved) or resolved[a:b].decode() != resolution["text"]):
                raise ContextError("OBLIGATION_RESOLUTION_CHANGED")
    from orchestrator.git_publication import scan
    for name in ('state', 'policy'):
        scan('context/' + name + '.md', content[name].encode('utf-8'))
    for row in register['obligations']:
        scan('context/obligation.json', encoded(row).encode('utf-8'))
    return manifest, content, register["obligations"]


def in_scope(row, project, idea_ids, stage, *, include_closed=False):
    scope = row["scope"]
    # Old scope labels remain meaningful; these aliases do not enable old routes.
    aliases = {
        "run_spec_author": {"specify", "probe_plan", "probe_code", "code", "code_bundle"},
        "run_spec_review": {"probe_review", "review", "code_review"},
        "result_interpretation_author": {"interpret", "campaign_interpret"},
        "result_interpretation_review": {"interpret_review", "campaign_interpret_review", "review"},
    }
    applicable_stages = {stage} | aliases.get(stage, set())
    return ((include_closed or row["status"] == "open")
            and ("*" in scope["project"] or project in scope["project"])
            and ("*" in scope["idea_ids"] or bool(set(scope["idea_ids"]) & set(idea_ids)))
            and ("*" in scope["stages"] or bool(applicable_stages & set(scope["stages"]))))


def open_obligation_text(row):
    """Exact input representation; callers select open, applicable records."""
    return (row['id']+' | '+row['type']+' | severity='+row['severity']+' | status=open\n'
            +encoded(row['source'])+'\n'+row['text'])


def obligations(root, project, idea_ids, stage):
    _, _, rows = load(root)
    return [row for row in rows if in_scope(row, project, idea_ids, stage)]


def stop_ids(rows):
    return [row["id"] for row in rows if row["type"] == "stop"]


def decision_entries(text, idea_ids, count=DECISION_COUNT):
    """Explicit tags/headings only: a narrative mention does not retag history.

    Existing `## ... idea 047 ...` headings are supported. New records may use
    `idea_ids: [047, P001]` / `run_ids: [run-123]` on their own line. A selected
    entry stays complete. The count cap never clips a decision's text.
    """
    ids = set(idea_ids)
    chosen = []
    for block in re.split(r"(?m)(?=^## )", text):
        heading = block.split("\n", 1)[0]
        tags = set(re.findall(r"(?i)\b(?:idea|run)\s+([A-Za-z0-9_.-]+)", heading))
        for raw in re.findall(r"(?m)^(?:idea_ids|run_ids):\s*\[([^\n]*)\]\s*$", block):
            tags.update(x.strip().strip("\"'") for x in raw.split(",") if x.strip())
        if "*" in tags or tags & ids:
            chosen.append(block)
    return chosen[-count:]


def decision_register_index(root, text, idea_ids, records):
    """Archive content enters a hosted input only through the checked register.

    Tagged newer decisions require reconciliation, never unchecked direct text.
    Unrelated append-only history is invisible to this representation.
    """
    manifest = json.loads(relative_file(root, PROJECT + '/manifest.json').read_text())
    seed = next(row for row in manifest['sources'] if row['path'] == 'evidence/decisions.md')
    seed_text = relative_file(root, seed['path']).read_bytes()[:seed['prefix_bytes']].decode('utf-8')
    selected = decision_entries(text, idea_ids)
    result = []
    flags = json.loads(relative_file(root, manifest['flagged']['path']).read_text())['obligations']
    for entry in selected:
        position = seed_text.find(entry)
        # The final seed entry can grow only by whitespace before the next heading.
        if position < 0:
            stripped = entry.rstrip()
            position = seed_text.find(stripped)
            if position < 0:
                raise ContextError('TAGGED_DECISION_REQUIRES_REGISTER_RECONCILIATION')
            entry = stripped
        start = len(seed_text[:position].encode('utf-8'))
        end = start + len(entry.encode('utf-8'))
        matching = [row['id'] for row in records + flags
                    if row['source']['original_path'] == 'evidence/decisions.md'
                    and row['source']['start'] < end and row['source']['end'] > start]
        if not matching:
            raise ContextError('TAGGED_DECISION_REGISTER_COVERAGE_MISSING')
        result.append({'original_sha256': seed['sha256'], 'byte_range': [start, end],
                       'register_ids': matching,
                       'meaning': 'Only open in-scope quotations above bind this stage; original is operator-readable.'})
    return encoded(result)


def assemble(root, *, project, idea_ids, stage, task, artifacts, extra=None, obligation_files=None):
    """Assemble a inspectable prompt. Dispatch preflight separately honors stops."""
    _, content, records = load(root)
    rows = [row for row in records if in_scope(row, project, idea_ids, stage)]
    parts = OrderedDict(task=task, STATE=content["state"], POLICY=content["policy"])
    citations = OrderedDict()
    for row in rows:
        ref = row['source']
        citations.setdefault(ref['path'], ref['sha256'])
    parts["OPEN OBLIGATIONS (verbatim)"] = "\n\n".join(open_obligation_text(row) for row in rows)
    if obligation_files is not None:
        # Exact representation change for item4 only, never omission or a stop override.
        if (project!='isles24-prediction' or idea_ids!=['sprint13b-execution']
                or stage not in {'run_spec_author','run_spec_review'}):
            raise ContextError('OBLIGATION_FILE_SCOPE')
        expected=parts['OPEN OBLIGATIONS (verbatim)'].encode('utf-8')
        joined=b'';navigation=[]
        from orchestrator.git_publication import scan
        scan('context/open-obligations.txt',expected)
        for index,(descriptor,raw) in enumerate(obligation_files,1):
            pin=sha(raw)
            exact={'id':'open-obligations-page-'+str(index),
                'path':'evidence/'+pin+'-open-obligations-'+str(index)+'.txt',
                'sha256':pin,'bytes':len(raw),'characters':len(raw.decode('utf-8')),
                'delivery':'Mandatory verbatim open obligations; read this entire page in order before acting.'}
            if descriptor!=exact or not 0<len(raw)<=12000:
                raise ContextError('OBLIGATION_FILE_BINDING')
            scan(descriptor['path'],raw);joined+=raw;navigation.append(descriptor)
        if joined!=expected or (expected and not obligation_files):
            raise ContextError('OBLIGATION_FILE_INCOMPLETE')
        parts['OPEN OBLIGATIONS (verbatim)']=encoded({
            'delivery':'Every open obligation is preserved verbatim in these ordered mandatory pages. '
                'Read ALL pages before authoring or reviewing. No obligation is closed or waived by file delivery.',
            'original_sha256':sha(expected),'original_bytes':len(expected),'pages':navigation})
    parts["OBLIGATION ORIGINALS (operator-readable provenance; full SHA256)"] = "\n".join(
        path + " " + digest for path, digest in citations.items())
    parts["CURRENT ARTIFACTS (evidence, not authority)"] = artifacts
    decisions = relative_file(root, "evidence/decisions.md").read_text()
    parts["TARGET DECISIONS (last %d tagged entries; register only)" % DECISION_COUNT] = decision_register_index(root, decisions, idea_ids, records)
    if extra:
        for name, text in extra.items():
            if name in parts: raise ContextError("CONTEXT_SECTION_COLLISION")
            parts[name] = text
    flagged = flagged_obligations(root, project, idea_ids, stage)
    if flagged:
        parts['FLAGGED OBLIGATIONS (operator decision required; no binding text exposed)'] = encoded(flagged)
    from orchestrator.git_publication import scan
    for text in parts.values():
        scan('context/input-section.txt', text.encode('utf-8'))
    body, measurement = measure(parts)
    scan('context/stage-input.md', body.encode('utf-8'))
    return body, {**measurement, "open_obligations": [r["id"] for r in rows], "stops": stop_ids(rows)}


def dispatch_preflight(root, *, project, idea_ids, stage, text):
    check_final(text)
    if enabled(root, project):
        stops = stop_ids(obligations(root, project, idea_ids, stage))
        if stops:
            raise ContextError("SCOPED_STOP_BLOCKS_MODEL_INPUT:" + ",".join(stops))
        flagged = flagged_obligations(root, project, idea_ids, stage)
        if flagged:
            raise ContextError('SCOPED_OBLIGATION_PRIVACY_DECISION_REQUIRED:' + ','.join(row['id'] for row in flagged))
    return text



def flagged_obligations(root, project, idea_ids, stage):
    manifest = json.loads(relative_file(root, PROJECT + '/manifest.json').read_text())
    ref = manifest.get('flagged')
    if ref is None: return []
    raw = relative_file(root, ref['path']).read_bytes()
    if sha(raw) != ref['sha256']: raise ContextError('FLAGGED_OBLIGATIONS_CHANGED')
    from orchestrator.git_publication import scan
    scan('context/flagged.json', raw)
    value=json.loads(raw)
    if value.get('schema')!='flagged-context-obligations/v1':raise ContextError('FLAGGED_OBLIGATIONS_SCHEMA')
    for row in value['obligations']:
        if 'text' in row or row.get('classification') != 'FLAGGED':
            raise ContextError('FLAGGED_OBLIGATION_VALUES_FORBIDDEN')
        ref = row['source']
        original = original_bytes(root, ref, manifest)
        start, end = ref['start'], ref['end']
        if (sha(original) != ref['sha256'] or type(start) is not int or type(end) is not int
                or not 0 <= start < end <= len(original)):
            raise ContextError('FLAGGED_OBLIGATION_SOURCE_CHANGED')
        try:
            scan('context/flagged-original.txt', original[start:end])
        except ValueError as refusal:
            if str(refusal) != row['rule']:
                raise ContextError('FLAGGED_OBLIGATION_RULE_CHANGED') from refusal
        else:
            raise ContextError('FLAGGED_OBLIGATION_REFUSAL_NOT_REPRODUCED')
    return [row for row in value['obligations'] if in_scope(row,project,idea_ids,stage)]
