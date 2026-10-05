"""Private development-evidence views; no public scanner exception or admission.

The caller supplies a reviewed registry hash from protected configuration, never
from model output. Originals remain operator-only. Selection is explicit and
loss is recorded: this module does not infer scientific acceptance from a file.
Only UTF-8 analysis views are supported here. Raster/opaque material remains
operator-only until its content and cohort can actually be checked.
"""
import hashlib
import html
import json
import re
from urllib.parse import unquote

from orchestrator import context_budget as budget
from orchestrator.git_publication import SECRET

DECISION_SHA256 = 'ca3857db236cdc7796655217ec5932caddceae7ef6d801542fd07d127d73eb06'
OPERATOR_SHA256 = '8426b69c263f12749c8717a548e68da4a55360c42e8d1d831eb3001cc3ecde69'
COHORT_SHA256 = '45c5746f60e2275383a2c4f4096295fe7a171da85a73737c5a35a8cc6fc9fe86'
KINDS = {'code', 'aggregate', 'plan', 'review', 'per_patient'}
STAGES = {'run_spec_author', 'run_spec_review', 'result_interpretation_author', 'result_interpretation_review'}
ID = re.compile(r'(?i)(?:sub[-_])?stroke[-_]?[0-9]+')
TOKEN = re.compile(r'(?:ya29\.[A-Za-z0-9_-]+|eyJ[A-Za-z0-9_-]{16,}\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+|(?:ak|as)-[A-Za-z0-9_-]{20,}|sk-ant-[A-Za-z0-9_-]+)')
ASSIGNMENT = re.compile(r'''(?ix)["']?(?:token|access_token|refresh_token|id_token|token_secret|client_secret|api_key|private_key|authorization|password)["']?\s*[:=]\s*["']?([^\s,"'}\]]+)''')


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode('utf-8')


def cohort(raw):
    if sha(raw) != COHORT_SHA256:
        raise ValueError('PRIVATE_INTAKE_COHORT_CHANGED')
    value = json.loads(raw)
    cases = value.get('cases')
    if (not isinstance(cases, list) or len(cases) != 99 or len(set(cases)) != 99
            or any(not isinstance(x, str) or not re.fullmatch(r'sub-stroke[0-9]{4}', x) for x in cases)):
        raise ValueError('PRIVATE_INTAKE_COHORT_INVALID')
    return frozenset(cases)


def scan(raw, cases, *, kind, reason=''):
    """Two mandatory fail-closed scans; returns counts, never rejected values.

    This is a known-secret/identifier detector, not a claim that arbitrary opaque
    data can be proven safe. Opaque formats are refused; evidence registration
    and review must also establish the development-only content provenance.
    """
    if kind not in KINDS or not isinstance(raw, bytes) or len(raw) > 1_500_000 or b'\0' in raw:
        raise ValueError('PRIVATE_INTAKE_TEXT_TYPE_OR_LIMIT')
    if kind == 'per_patient' and (not isinstance(reason, str) or not reason.strip()):
        raise ValueError('PRIVATE_INTAKE_ANALYSIS_REASON_REQUIRED')
    text = raw.decode('utf-8')
    # Notebook JSON is decoded before this function. Also inspect common textual
    # escaping so a literal escaped identifier/token cannot evade the check.
    variants = [text]
    for _ in range(2):
        decoded = html.unescape(unquote(variants[-1]))
        decoded = re.sub(r'\\u([0-9a-fA-F]{4})', lambda m: chr(int(m[1], 16)), decoded)
        if decoded == variants[-1]:
            break
        variants.append(decoded)
    found = set()
    for value in variants:
        if SECRET.search(value.encode()) or TOKEN.search(value) or ASSIGNMENT.search(value):
            raise ValueError('PRIVATE_INTAKE_SECRET_REJECTED')
        # Long encoded blobs cannot be inspected as plain scientific text.
        if re.search(r'[A-Za-z0-9+/]{256,}={0,2}', value):
            raise ValueError('PRIVATE_INTAKE_OPAQUE_PAYLOAD_REJECTED')
        for match in ID.finditer(value):
            digits = re.search(r'[0-9]+', match[0])[0]
            normalized = 'sub-stroke' + digits
            if normalized not in cases or match[0] != normalized:
                raise ValueError('PRIVATE_INTAKE_NONDEVELOPMENT_OR_NONCANONICAL_ID')
            found.add(normalized)
    if found and kind not in {'code', 'per_patient'}:
        raise ValueError('PRIVATE_INTAKE_PATIENT_LEVEL_CLASSIFICATION_REQUIRED')
    return {'secret_scan': 'PASS', 'locked_and_unknown_id_scan': 'PASS',
            'development_identifiers': len(found), 'bytes': len(raw), 'characters': len(text)}


def notebook_units(raw):
    """Deterministic decoded components, with JSON-pointer-like source identities.

    Unsupported MIME/metadata components are inventoried too, never silently
    mistaken for inspected figures. Their raw JSON representation can be hashed
    and omitted but cannot be selected as code or an aggregate.
    """
    value = json.loads(raw)
    if value.get('nbformat') != 4 or not isinstance(value.get('cells'), list):
        raise ValueError('PRIVATE_INTAKE_NOTEBOOK_SCHEMA')
    units = {'notebook/metadata-and-format': (canonical({k: v for k, v in value.items() if k != 'cells'}), 'opaque')}
    for n, cell in enumerate(value['cells']):
        units[f'cells/{n}/metadata-and-type'] = (canonical({k: v for k, v in cell.items()
                                                         if k not in {'source', 'outputs'}}), 'opaque')
        source = cell.get('source', '')
        source = ''.join(source) if isinstance(source, list) else source
        if not isinstance(source, str):
            raise ValueError('PRIVATE_INTAKE_NOTEBOOK_SOURCE')
        units[f'cells/{n}/source'] = (source.encode(), 'code' if cell.get('cell_type') == 'code' else 'plan')
        for m, out in enumerate(cell.get('outputs', [])):
            prefix = f'cells/{n}/outputs/{m}'
            units[prefix + '/metadata-and-type'] = (canonical({k: v for k, v in out.items()
                if k not in {'text', 'data'}}), 'opaque')
            if out.get('output_type') == 'stream':
                text = out.get('text', '')
                text = ''.join(text) if isinstance(text, list) else text
                units[prefix + '/text'] = (text.encode(), 'output')
            else:
                data = out.get('data', {})
                for mime, content in data.items():
                    content = ''.join(content) if isinstance(content, list) else content
                    units[prefix + '/data/' + mime] = ((content.encode() if isinstance(content, str) else canonical(content)),
                        'output' if mime == 'text/plain' else 'opaque')
                if out.get('output_type') == 'error':
                    units[prefix + '/error'] = (canonical(out), 'output')
    return units


def derive(original, selection, cases):
    """Create an explicitly incomplete, non-executable view and omission map.

    A selection describes every unit and partitions its exact UTF-8 bytes into
    kept or omitted spans. No synthetic replacement of an observation occurs.
    The protected registry subsequently binds the view and this complete map.
    """
    units = notebook_units(original)
    if set(selection) != set(units):
        raise ValueError('PRIVATE_INTAKE_UNIT_COVERAGE')
    records, pieces, patient_files = [], [], []
    for name in sorted(units):
        raw, native_kind = units[name]
        spans = selection[name]
        position = 0
        for part in spans:
            if set(part) != {'start', 'end', 'keep', 'kind', 'reason'}:
                raise ValueError('PRIVATE_INTAKE_SPAN_FIELDS')
            start, end = part['start'], part['end']
            if (type(start) is not int or type(end) is not int or type(part['keep']) is not bool
                    or start != position or not start < end <= len(raw)
                    or not isinstance(part['reason'], str) or not part['reason'].strip()):
                raise ValueError('PRIVATE_INTAKE_SPAN_PARTITION')
            chunk = raw[start:end]
            record = {'unit': name, **part, 'sha256': sha(chunk)}
            if part['keep']:
                if (native_kind == 'opaque' or (native_kind == 'code' and part['kind'] != 'code')
                        or (native_kind != 'code' and part['kind'] == 'code')):
                    raise ValueError('PRIVATE_INTAKE_COMPONENT_CLASSIFICATION')
                record['checks'] = scan(chunk, cases, kind=part['kind'], reason=part['reason'])
                pieces.append('\n## ' + name + ' bytes ' + str(start) + ':' + str(end) + '\n' + chunk.decode())
                if part['kind'] == 'per_patient':
                    patient_files.append({'unit': name, 'start': start, 'end': end, 'reason': part['reason']})
            records.append(record)
            position = end
        if position != len(raw):
            raise ValueError('PRIVATE_INTAKE_SPAN_PARTITION')
    header = ('# Derived scientific analysis view\nNot the original executable notebook. '
              'Omitted spans are listed by hash and reason in the bound manifest. '
              'Original SHA256: ' + sha(original) + '\n')
    view = (header + '\n'.join(pieces)).encode()
    # Recheck across span boundaries and also scan reasons/identities in the map.
    scan(view, cases, kind='per_patient', reason='Selected code and explicitly classified evidence view')
    manifest = {'schema': 'private-scientific-view/v1', 'original_sha256': sha(original),
                'view_sha256': sha(view), 'spans': records, 'per_patient_material': patient_files,
                'omitted_units': [n for n in sorted(units) if not any(p['keep'] for p in selection[n])],
                'cohort_sha256': COHORT_SHA256, 'scientific_acceptance': False}
    scan(canonical(manifest), cases, kind='plan')
    return view, manifest


def validate_manifest(manifest):
    expected = {'schema', 'original_sha256', 'view_sha256', 'spans', 'per_patient_material',
                'omitted_units', 'cohort_sha256', 'scientific_acceptance'}
    if (not isinstance(manifest, dict) or set(manifest) != expected
            or manifest['schema'] != 'private-scientific-view/v1'
            or manifest['cohort_sha256'] != COHORT_SHA256
            or manifest['scientific_acceptance'] is not False
            or any(not isinstance(manifest[k], str) or not re.fullmatch('[0-9a-f]{64}', manifest[k])
                   for k in ('original_sha256', 'view_sha256'))
            or not isinstance(manifest['spans'], list)):
        raise ValueError('PRIVATE_INTAKE_VIEW_BINDING')
    patient_material = []
    for span in manifest['spans']:
        if (not isinstance(span, dict) or type(span.get('keep')) is not bool
                or span.get('kind') not in KINDS | {'opaque'}
                or (span['keep'] and span['kind'] == 'opaque')
                or not isinstance(span.get('unit'), str)
                or type(span.get('start')) is not int or type(span.get('end')) is not int
                or not 0 <= span['start'] < span['end']
                or not isinstance(span.get('sha256'), str) or not re.fullmatch('[0-9a-f]{64}', span['sha256'])
                or not isinstance(span.get('reason'), str) or not span['reason'].strip()):
            raise ValueError('PRIVATE_INTAKE_MANIFEST_CLASSIFICATION')
        if span['keep'] and span['kind'] == 'per_patient':
            patient_material.append({k: span[k] for k in ('unit', 'start', 'end', 'reason')})
    if manifest['per_patient_material'] != patient_material:
        raise ValueError('PRIVATE_INTAKE_PATIENT_MATERIAL_INVENTORY')


def load_views(root, registry_ref, *, stage, idea_ids):
    """Called by manual_context before workspace delivery on every invocation.

    The registry hash is a protected, reviewed configuration binding. Neither
    the model nor a notebook may supply it. Only the two authorized analysis
    tasks and their author/reviewer stages can consume this route.
    """
    if stage not in STAGES:
        raise ValueError('PRIVATE_INTAKE_STAGE_NOT_AUTHORIZED')
    if set(registry_ref) != {'path', 'sha256'}:
        raise ValueError('PRIVATE_INTAKE_REGISTRY_REFERENCE')
    raw = budget.relative_file(root, registry_ref['path']).read_bytes()
    if sha(raw) != registry_ref['sha256']:
        raise ValueError('PRIVATE_INTAKE_REGISTRY_CHANGED')
    registry = json.loads(raw)
    if (set(registry) != {'schema', 'decision_sha256', 'operator_sha256', 'cohort', 'task', 'idea_ids', 'views'}
            or registry['schema'] != 'private-scientific-intake/v1'
            or registry['decision_sha256'] != DECISION_SHA256
            or registry['operator_sha256'] != OPERATOR_SHA256
            or registry['task'] not in {'sprints-stocktake', 'sprint13-proposal'}
            or not isinstance(registry['idea_ids'], list) or not registry['idea_ids']
            or registry['idea_ids'][0] != registry['task']
            or any(not isinstance(x, str) or not x for x in registry['idea_ids'])
            or len(set(registry['idea_ids'])) != len(registry['idea_ids'])
            or idea_ids != registry['idea_ids']):
        raise ValueError('PRIVATE_INTAKE_AUTHORITY_OR_SCOPE')
    cases = cohort(budget.relative_file(root, registry['cohort']).read_bytes())
    files, descriptors, seen = [], [], set()
    if not isinstance(registry['views'], list) or not registry['views']:
        raise ValueError('PRIVATE_INTAKE_VIEWS_REQUIRED')
    for row in registry['views']:
        if (set(row) != {'id', 'path', 'sha256', 'manifest', 'manifest_sha256', 'cohort_evidence'}
                or not isinstance(row['id'], str) or not re.fullmatch(r'[A-Za-z0-9-]{1,80}', row['id'])
                or row['id'] in seen or not isinstance(row['cohort_evidence'], str) or not row['cohort_evidence'].strip()):
            raise ValueError('PRIVATE_INTAKE_VIEW_REGISTRATION')
        seen.add(row['id'])
        view = budget.relative_file(root, row['path']).read_bytes()
        evidence = budget.relative_file(root, row['manifest']).read_bytes()
        if sha(view) != row['sha256'] or sha(evidence) != row['manifest_sha256']:
            raise ValueError('PRIVATE_INTAKE_VIEW_CHANGED')
        manifest = json.loads(evidence)
        validate_manifest(manifest)
        if manifest['view_sha256'] != row['sha256']:
            raise ValueError('PRIVATE_INTAKE_VIEW_BINDING')
        # Hash-bound exact derivation and classifications have been independently
        # reviewed. Re-scan actual bytes each time, not just registration time.
        checks = scan(view, cases, kind='per_patient', reason='Bound selected view')
        scan(evidence, cases, kind='plan')
        scan(canonical(row), cases, kind='plan')
        for content, suffix in [(view, 'view.txt'), (evidence, 'omissions.json')]:
            descriptor = {'id': row['id'] + '-' + suffix, 'path': 'evidence/' + sha(content) + '-' + suffix,
                          'sha256': sha(content), 'bytes': len(content), 'characters': len(content.decode()),
                          'delivery': 'Private development analysis view; inspect its omissions and provenance.'}
            files.append((descriptor, content))
            descriptors.append(descriptor)
        descriptors[-2].update(checks=checks, cohort_evidence=row['cohort_evidence'],
                               per_patient_material=manifest['per_patient_material'])
    return descriptors, files
