"""Proposal-only protocol construction in the existing reviewed campaign pipeline.

The selected charter and actual supplied evidence precede protocol authorization.
Unknown membership, inputs or literature are scientific deferrals, never invented
facts or new access permissions. Helpers perform no model, data or file mutation.
"""
import hashlib
import json
from pathlib import Path
import re

from orchestrator.handover_coordinator import digest
from orchestrator.public_export import text

TASK_SCHEMA = 'protocol-proposal-task/v1'
MODE = 'protocol_proposal'
OUTPUTS = ('protocol.proposed.json', 'methodology.proposed.md', 'literature-review.proposed.json',
           'input-manifest.proposed.json', 'partition-registry.proposed.json', 'exposure-history.proposed.json')
DATA_OUTPUTS = {'input_manifest': 'input-manifest.proposed.json',
                'partition_registry': 'partition-registry.proposed.json',
                'exposure_history': 'exposure-history.proposed.json'}
AUTHORITY_ARTIFACTS = {'protocol_sha256': OUTPUTS[0], 'methodology_review_sha256': OUTPUTS[1],
    'literature_review_sha256': OUTPUTS[2], 'input_manifest_sha256': OUTPUTS[3],
    'partition_registry_sha256': OUTPUTS[4], 'exposure_history_sha256': OUTPUTS[5]}


def task_contract(task):
    from orchestrator.continuing_research import reference
    if (not isinstance(task, dict) or set(task) !=
            {'schema', 'task_id', 'experiment', 'mode', 'request', 'references', 'selected_by'}
            or task['schema'] != TASK_SCHEMA or task['mode'] != MODE
            or task['experiment'] not in ('P002', 'P003')
            or not isinstance(task['task_id'], str) or not re.fullmatch('[a-z0-9][a-z0-9-]{0,79}', task['task_id'])
            or not isinstance(task['request'], str) or not task['request'].strip()
            or not isinstance(task['references'], list) or len(task['references']) > 16):
        raise ValueError('PROTOCOL_PROPOSAL_TASK_REQUIRED')
    text(task['request'], limit=8000)
    refs = [digest(reference(ref)) for ref in task['references']]
    if len(set(refs)) != len(refs): raise ValueError('PROTOCOL_PROPOSAL_DUPLICATE_REFERENCE')
    if task['selected_by'] is not None:
        reference(task['selected_by'])
        if task['selected_by']['artifact'] != 'round-1/selection.json':
            raise ValueError('PROTOCOL_PROPOSAL_ORIGINAL_SELECTION_REQUIRED')
    return {'version': 2, 'experiment': task['experiment'], 'mode': MODE, 'operation_sha256': digest(task)}


def grounding(root, task):
    """Current selected charter and existing evidence, without old P001 ordering."""
    task_contract(task)
    from orchestrator.campaign import require_no_human_stop
    from orchestrator.research_context import selected_prediction_context
    from orchestrator import scientific_authority as authority
    root = Path(root)
    require_no_human_stop(root, task['experiment'])
    selected = selected_prediction_context(root)
    if not selected:
        raise ValueError('PROTOCOL_PROPOSAL_SELECTED_CHARTER_REQUIRED')
    current = authority.context(root)
    required = ('campaigns/isles24-pilot/CAMPAIGN.md',
                'docs/operations/REMOTE_OPERATING_DIRECTION.md',
                'docs/operations/CLAUDE_REVIEWER_DIRECTIVE.md', current['binding']['path'],
                current['policy']['direction_path'])
    result = {name: authority.read(root / name).decode() for name in required}
    for name in ('docs/science/PREDICTION_READINESS_DIRECTION_20260906.md',
                 'docs/science/PREDICTION_PRIMARY_SOURCES_20260906.json'):
        if (root / name).exists(): result[name] = authority.read(root / name).decode()
    result.update(selected)
    result['protocol-proposal-scope.json'] = json.dumps({'experiment': task['experiment'],
        'status': 'PROPOSAL_ONLY', 'existing_charter_only': True, 'prior_protocol_required': False,
        'data_access': False, 'execution': False, 'approval': False,
        'missing_evidence': 'DEFER_WITH_RECORDED_UNKNOWNS'}, sort_keys=True)
    return result


def _references(task, context):
    task_contract(task)
    raw = context.get('continuing-research-inputs.json')
    if not isinstance(raw, str): raise ValueError('PROTOCOL_PROPOSAL_RECORDED_INPUTS_REQUIRED')
    value = json.loads(raw)
    if (set(value) != {'task', 'references'} or value['task'] != task
            or not isinstance(value['references'], list)
            or len(value['references']) != len(task['references'])):
        raise ValueError('PROTOCOL_PROPOSAL_INPUT_CONTEXT_CHANGED')
    result = {}
    for ref, row in zip(task['references'], value['references']):
        if (set(row) != {'reference', 'content'} or row['reference'] != ref
                or not isinstance(row['content'], str)
                or hashlib.sha256(row['content'].encode()).hexdigest() != ref['sha256']):
            raise ValueError('PROTOCOL_PROPOSAL_ORIGINAL_EVIDENCE_CHANGED')
        result[digest(ref)] = row['content']
    return result


def _strings(value, *, nonempty=False):
    if (not isinstance(value, list) or len(value) > 32 or nonempty and not value
            or any(not isinstance(item, str) or not item.strip() or len(item) > 4000 for item in value)):
        raise ValueError('PROTOCOL_PROPOSAL_UNKNOWNS_REQUIRED')
    return value


def _protocol(value, task):
    if (not isinstance(value, dict) or set(value) != {'schema', 'protocol_id', 'experiment', 'status',
            'design', 'rationale', 'unknowns', 'evidence', 'data_sources'}
            or value['schema'] != 'scientific-protocol-proposal/v1'
            or value['experiment'] != task['experiment']
            or not isinstance(value['protocol_id'], str)
            or not re.fullmatch('[a-z0-9][a-z0-9-]{0,62}', value['protocol_id'])
            or value['status'] not in ('PROPOSED', 'DEFERRED')
            or not isinstance(value['data_sources'], dict) or set(value['data_sources']) != set(DATA_OUTPUTS)
            or not isinstance(value['evidence'], list) or len(value['evidence']) > 16):
        raise ValueError('PROTOCOL_PROPOSAL_ARTIFACT_REQUIRED')
    for key in ('design', 'rationale'):
        if not isinstance(value[key], str) or not value[key].strip():
            raise ValueError('PROTOCOL_PROPOSAL_SCIENTIFIC_REASON_REQUIRED')
    _strings(value['unknowns'], nonempty=value['status'] == 'DEFERRED')
    if value['status'] == 'PROPOSED' and value['unknowns']:
        raise ValueError('PROTOCOL_PROPOSAL_UNKNOWNS_REQUIRE_DEFERRAL')
    return value


def validate_bundle(task, files, context):
    """Check declared evidence/proposal boundaries, never judge scientific merit."""
    available = _references(task, context)
    if not isinstance(files, dict) or set(files) != set(OUTPUTS):
        raise ValueError('PROTOCOL_COMPLETE_PROPOSAL_BUNDLE_REQUIRED')
    for body in files.values():
        if not isinstance(body, str) or not body.strip(): raise ValueError('PROTOCOL_EMPTY_PROPOSAL_ARTIFACT')
        text(body, limit=30000)
    protocol = _protocol(json.loads(files[OUTPUTS[0]]), task)
    from orchestrator.continuing_research import reference
    used = [digest(reference(ref)) for ref in protocol['evidence']]
    if len(set(used)) != len(used) or not set(used) <= set(available):
        raise ValueError('PROTOCOL_PROPOSAL_UNSUPPLIED_EVIDENCE_REFUSED')
    missing = []
    for kind, name in DATA_OUTPUTS.items():
        ref = protocol['data_sources'][kind]; proposed = json.loads(files[name])
        if ref is None:
            if (not isinstance(proposed, dict) or set(proposed) != {'schema', 'kind', 'reason'}
                    or proposed['schema'] != 'protocol-evidence-unavailable/v1'
                    or proposed['kind'] != kind or not isinstance(proposed['reason'], str)
                    or not proposed['reason'].strip()):
                raise ValueError('PROTOCOL_MISSING_ORIGINAL_REQUIRES_EXPLICIT_PLACEHOLDER')
            missing.append(kind)
            continue
        key = digest(reference(ref))
        if key not in used or key not in available:
            raise ValueError('PROTOCOL_DATA_ORIGINAL_NOT_IN_RECORDED_EVIDENCE')
        try: original = json.loads(available[key])
        except (TypeError, json.JSONDecodeError) as error:
            raise ValueError('PROTOCOL_DATA_REQUIRES_ORIGINAL_JSON_EVIDENCE') from error
        if not isinstance(original, dict) or proposed != original:
            raise ValueError('PROTOCOL_PROPOSED_MEMBERSHIP_OR_INPUTS_INVENTED')
        if proposed.get('schema') == 'protocol-evidence-unavailable/v1':
            missing.append(kind)
        if kind == 'input_manifest' and (set(proposed) != {'schema', 'root', 'files'}
                or proposed.get('schema') != 'linux-scientific-inputs/v1'
                or not isinstance(proposed.get('root'), str) or not Path(proposed['root']).is_absolute()
                or '..' in Path(proposed['root']).parts or not isinstance(proposed.get('files'), dict)
                or not proposed['files']):
            raise ValueError('PROTOCOL_RECORDED_INPUT_MANIFEST_REQUIRED')
    literature = json.loads(files[OUTPUTS[2]])
    if (not isinstance(literature, dict) or set(literature) != {'schema', 'status', 'rationale', 'citations', 'unknowns'}
            or literature['schema'] != 'recorded-literature-review/v1'
            or literature['status'] not in ('PROPOSED', 'DEFERRED')
            or not isinstance(literature['rationale'], str) or not literature['rationale'].strip()
            or not isinstance(literature['citations'], list) or len(literature['citations']) > 32):
        raise ValueError('PROTOCOL_RECORDED_LITERATURE_REVIEW_REQUIRED')
    _strings(literature['unknowns'], nonempty=literature['status'] == 'DEFERRED')
    for citation in literature['citations']:
        if (not isinstance(citation, dict) or set(citation) != {'context_file', 'url', 'evidence_level', 'finding'}
                or citation['context_file'] not in context
                or not isinstance(citation['url'], str) or not re.fullmatch(r'https?://[^\s]+', citation['url'])
                or citation['url'] not in context[citation['context_file']]
                or citation['evidence_level'] != 'supplied_context_only'
                or not isinstance(citation['finding'], str) or not citation['finding'].strip()):
            raise ValueError('PROTOCOL_INVENTED_LITERATURE_PROVENANCE_REFUSED')
    if not literature['citations'] or literature['unknowns'] or literature['status'] == 'DEFERRED':
        missing.append('literature_review')
    if missing and protocol['status'] != 'DEFERRED':
        raise ValueError('PROTOCOL_MISSING_EVIDENCE_REQUIRES_DEFERRAL')
    return {'schema': 'protocol-proposal-validation/v1', 'status': protocol['status'],
        'protocol_id': protocol['protocol_id'], 'experiment': task['experiment'],
        'artifact_sha256': {name: hashlib.sha256(body.encode()).hexdigest() for name, body in files.items()},
        'recorded_unknowns': protocol['unknowns'], 'missing_evidence': missing,
        'scientific_approval': False, 'data_access_authority': False, 'execution_authority': False}


def authorization_artifacts(protocol_id, experiment, artifacts, contents):
    """Fixed AUTHORIZE_PROTOCOL precondition after actual original bundle review.

    Full validate_bundle runs in the original/recovered pipeline. This additional
    guard refuses selecting a deferred or mixed-version bundle for authorization.
    Runtime separately rechecks each task's actual provider replies and review.
    """
    from orchestrator.continuing_research import reference
    if set(artifacts) != set(AUTHORITY_ARTIFACTS) or set(contents) != set(AUTHORITY_ARTIFACTS):
        raise ValueError('PROTOCOL_AUTHORITY_COMPLETE_ORIGINAL_BUNDLE_REQUIRED')
    tasks = set()
    for key, name in AUTHORITY_ARTIFACTS.items():
        ref = reference(artifacts[key]); tasks.add(ref['task'])
        if (ref['artifact'] != 'round-1/' + name
                or hashlib.sha256(contents[key].encode()).hexdigest() != ref['sha256']):
            raise ValueError('PROTOCOL_AUTHORITY_ORIGINAL_ARTIFACT_CHANGED')
    if len(tasks) != 1: raise ValueError('PROTOCOL_AUTHORITY_MIXED_BUNDLE_REFUSED')
    protocol = _protocol(json.loads(contents['protocol_sha256']), {'experiment': experiment})
    if (protocol['protocol_id'] != protocol_id or protocol['status'] != 'PROPOSED'
            or protocol['unknowns'] or any(ref is None for ref in protocol['data_sources'].values())):
        raise ValueError('PROTOCOL_PROPOSAL_DEFERRED_MISSING_EVIDENCE')
    literature = json.loads(contents['literature_review_sha256'])
    if literature.get('status') != 'PROPOSED' or literature.get('unknowns') or not literature.get('citations'):
        raise ValueError('PROTOCOL_PROPOSAL_LITERATURE_DEFERRED')
    for key in ('input_manifest_sha256', 'partition_registry_sha256', 'exposure_history_sha256'):
        if json.loads(contents[key]).get('schema') == 'protocol-evidence-unavailable/v1':
            raise ValueError('PROTOCOL_PROPOSAL_DEFERRED_MISSING_EVIDENCE')
    return {'status': 'REVIEWED_PROPOSAL_READY_FOR_SEPARATE_AUTHORITY', 'task': next(iter(tasks)),
            'protocol_id': protocol_id, 'scientific_approval': False}


def instructions(task, context):
    _references(task, context)
    return ('Construct a protocol proposal for the already selected ISLES24 charter using only the supplied '
        'recorded evidence. This stage grants no data access, execution, spending or scientific acceptance. '
        'Do not seek patient records or invent missing membership, source access, literature searches or measurements. '
        'Return these six files: ' + ', '.join(OUTPUTS) + '. '
        'protocol.proposed.json exact keys: schema=scientific-protocol-proposal/v1, protocol_id (lowercase slug), '
        'experiment=' + task['experiment'] + ', status PROPOSED or DEFERRED, design (clear scientific protocol text), '
        'rationale, unknowns (list), evidence (exact supplied artifact references), data_sources (exact keys '
        'input_manifest, partition_registry, exposure_history; each a supplied reference or null). '
        'methodology.proposed.md explains endpoints, comparisons, evaluation, assumptions, exposure and limitations '
        'in readable terms, with scientific choices left as proposals. Copy each available data_sources JSON '
        'object unchanged in meaning into its matching proposed JSON file. The input manifest must already be a '
        'recorded linux-scientific-inputs/v1 object with root and files; do not construct an unobserved file inventory. '
        'If an original is unavailable, set its data_sources value null and write exactly '
        '{schema:protocol-evidence-unavailable/v1,kind:<matching data_sources key>,reason:<plain explanation>}. '
        'literature-review.proposed.json exact keys: schema=recorded-literature-review/v1, status PROPOSED or DEFERRED, '
        'rationale, citations, unknowns. Each citation has context_file (an actual bound context filename), url '
        '(literally present there), evidence_level=supplied_context_only and finding. Never claim to have opened '
        'the paper or performed a search when only recorded metadata or excerpts are supplied. State inadequate '
        'literature as an unknown. Missing originals, inadequate literature or any material unknown requires '
        'protocol status DEFERRED with nonempty unknowns and a concrete evidence request. A complete proposal '
        'uses PROPOSED with no unknowns; this still requires independent proposal review and the separate '
        'AUTHORIZE_PROTOCOL scientific decision. The system calculates and records hashes; do not invent them.')
