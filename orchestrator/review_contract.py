"""New-review contract. Prose is opaque; only typed decision fields govern."""
import json
import hashlib
CATEGORIES = ('test-set/leakage', 'code/spec mismatch', 'metric/statistic',
              'privacy/secret', 'budget', 'execution authority/provenance')

SCHEMA = 'bound-review/v1'
FINDING_FIELDS = {'id', 'category', 'text', 'evidence', 'resolution'}

def strict_json(raw):
    def pairs(items):
        value = {}
        for key, item in items:
            if key in value: raise ValueError('DUPLICATE_REVIEW_FIELD')
            value[key] = item
        return value
    try:
        return json.loads(raw, object_pairs_hook=pairs,
            parse_constant=lambda value: (_ for _ in ()).throw(ValueError('NONFINITE_REVIEW_VALUE')))
    except (TypeError, json.JSONDecodeError) as error:
        raise ValueError('MALFORMED_STRUCTURED_REVIEW') from error


def decision(value, fields):
    if not isinstance(value, dict) or set(value) != fields:
        raise ValueError('EXACT_STRUCTURED_REVIEW_FIELDS_REQUIRED')
    if value['verdict'] not in ('APPROVE', 'REVISE', 'REJECT'):
        raise ValueError('STRUCTURED_REVIEW_VERDICT_REQUIRED')
    if not isinstance(value['rationale'], str) or not value['rationale'].strip():
        raise ValueError('REVIEW_RATIONALE_REQUIRED')
    findings = value['findings']
    if not isinstance(findings, list): raise ValueError('REVIEW_FINDINGS_LIST_REQUIRED')
    ids = set()
    for finding in findings:
        if not isinstance(finding, dict) or set(finding) != FINDING_FIELDS:
            raise ValueError('MALFORMED_REVIEW_FINDING')
        if any(not isinstance(finding[k], str) or not finding[k].strip() for k in FINDING_FIELDS):
            raise ValueError('INCOMPLETE_REVIEW_FINDING')
        if finding['id'] in ids or finding['category'] not in CATEGORIES:
            raise ValueError('AMBIGUOUS_REVIEW_FINDING')
        ids.add(finding['id'])
    if value['verdict'] == 'APPROVE' and findings:
        raise ValueError('LISTED_FINDING_BLOCKS_APPROVAL')
    return value


def scientific(raw):
    return decision(strict_json(raw), {'verdict', 'findings', 'rationale'})


def administrative(raw, manifest):
    canonical = lambda v: json.dumps(v, sort_keys=True, separators=(',', ':')).encode()
    sha = lambda raw: hashlib.sha256(raw).hexdigest()
    fields = {'schema', 'source_sha', 'runtime_sha256', 'packet_sha256',
              'verdict', 'findings', 'rationale', 'inspected_scope', 'limitations', 'analysis_entrypoint'}
    value = decision(strict_json(raw), fields)
    expected = {'schema': SCHEMA, 'source_sha': manifest['source_sha'],
        'runtime_sha256': manifest['runtime_sha256'], 'packet_sha256': sha(canonical(manifest))}
    if any(value[k] != v for k, v in expected.items()):
        raise ValueError('STRUCTURED_REVIEW_BINDING_MISMATCH')
    for key in ('inspected_scope', 'limitations'):
        if not isinstance(value[key], list) or any(not isinstance(x, str) or not x.strip() for x in value[key]):
            raise ValueError('STRUCTURED_REVIEW_SCOPE_REQUIRED')
    if not value['inspected_scope'] or value['analysis_entrypoint'] not in (None, 'orchestrator.analysis_driver'):
        raise ValueError('STRUCTURED_REVIEW_ENTRYPOINT_OR_SCOPE')
    return value


SCIENTIFIC_INSTRUCTION = (
    'Submit your decision using the submit_review MCP tool. Read .review-submission-config.json for the exact bindings; include them unchanged. Do not write review.json. Only the accepted tool submission supplies the verdict. Correct validation errors within this session, but never submit again after acceptance. The review object has exactly verdict, findings, rationale. '
    'verdict is APPROVE, REVISE or REJECT. findings is an array; each finding has exactly '
    'id, category, text, evidence, resolution, all nonempty strings. Categories: '
    + '; '.join(CATEGORIES) + '. Every unresolved finding belongs in findings, not only in prose. '
    'Any listed finding blocks approval; APPROVE requires findings=[]. Missing inspection '
    'requires REVISE or REJECT and its concrete finding. Rationale is nonempty explanatory '
    'prose and never determines the verdict. Do not encode decisions in prose markers. '
    'No extra fields, duplicate keys, markdown fences or text outside the JSON object. ')
