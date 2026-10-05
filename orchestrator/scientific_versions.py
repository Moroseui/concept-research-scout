"""Prospective scientific versions; frozen campaign review remains unchanged.

A code-bundle review is a proposal review. The separate scientific_decision
approval below supplies all required source contents to both actual roles before
protected capture can treat the explicit new version as eligible.
"""
import hashlib
import json
from pathlib import Path
import re

from orchestrator.handover_coordinator import digest
from orchestrator.hosted_cycle import encoded
from orchestrator import scientific_authority as authority
from orchestrator.hosted_campaign import artifact_files, checked_reply
from orchestrator.formal_decisions import original_transport, verify_original_decision

SCHEMA = 'prospective-scientific-version/v1'
ACTION = 'approve_scientific_version'
TRANSITION = {'from': 'REVIEWED_SCIENTIFIC_VERSION_PROPOSAL', 'to': 'SCIENTIFIC_VERSION_ELIGIBLE'}
CODE_BUNDLE = ('run.proposed.py', 'validate_return.proposed.py', 'requirements.proposed.txt',
               'publication.proposed.json', 'test.proposed.py')
PROPOSAL_FILES = {'propose': ('proposal.md',), 'specify': ('SPEC.proposed.md',),
                  'code_bundle': CODE_BUNDLE}


def required_files(root, experiment):
    """Reuse the complete historical review input set, with truthful new lineage."""
    if experiment not in ('P002', 'P003'):
        raise ValueError('PROSPECTIVE_VERSION_CANNOT_REWRITE_FROZEN_P001')
    from orchestrator.campaign_review import required_files as existing
    base = 'campaigns/isles24-pilot/experiments/' + experiment + '/'
    return (existing(root, experiment) - {base + 'investigator_decision.json'}) | {
        base + 'scientific-origin.json', 'orchestrator/scientific_versions.py',
        'orchestrator/formal_decisions.py'}


def origin(core):
    return {'schema': 'prospective-scientific-origin/v1', **{key: core[key] for key in
        ('source', 'experiment', 'version_id', 'parent_version_sha256', 'proposals',
         'protocol_decision_sha256')}}


def artifact_targets(experiment):
    if experiment not in ('P002', 'P003'):
        raise ValueError('PROSPECTIVE_VERSION_CANNOT_REWRITE_FROZEN_P001')
    base = 'campaigns/isles24-pilot/experiments/' + experiment + '/'
    return {'specify': {'SPEC.proposed.md': base + 'SPEC.md'}, 'code_bundle': {
        'run.proposed.py': base + 'run.py', 'validate_return.proposed.py': base + 'validate_return.py',
        'requirements.proposed.txt': base + 'requirements.txt',
        'publication.proposed.json': base + 'publication.json',
        'test.proposed.py': 'tests/test_prediction_' + experiment.lower() + '.py'}}


def _sha(value, length=64):
    return isinstance(value, str) and re.fullmatch('[0-9a-f]{' + str(length) + '}', value)


def validate_core(root, core):
    if (not isinstance(core, dict) or set(core) !=
            {'schema', 'source', 'experiment', 'version_id', 'parent_version_sha256',
             'files', 'proposals', 'protocol_decision_sha256'} or core['schema'] != SCHEMA
            or not _sha(core['source'], 40)
            or not isinstance(core['version_id'], str)
            or not re.fullmatch('[a-z0-9][a-z0-9-]{0,79}', core['version_id'])
            or core['parent_version_sha256'] is not None and not _sha(core['parent_version_sha256'])
            or not _sha(core['protocol_decision_sha256'])
            or not isinstance(core['files'], dict)
            or set(core['files']) != required_files(root, core['experiment'])
            or any(not _sha(value) for value in core['files'].values())):
        raise ValueError('PROSPECTIVE_SCIENTIFIC_VERSION_CORE_REQUIRED')
    proposals = core['proposals']
    if not isinstance(proposals, list) or len(proposals) != 3:
        raise ValueError('REVIEWED_IDEA_SPEC_AND_CODE_BUNDLE_REQUIRED')
    modes = set()
    for row in proposals:
        if (not isinstance(row, dict) or set(row) !=
                {'task', 'source', 'mode', 'packet_sha256', 'artifacts'}
                or not _sha(row['task']) or not _sha(row['source'], 40)
                or not _sha(row['packet_sha256']) or row['mode'] not in PROPOSAL_FILES
                or row['mode'] in modes or not isinstance(row['artifacts'], dict)
                or set(row['artifacts']) != {'round-1/' + name for name in PROPOSAL_FILES[row['mode']]}
                or any(not _sha(value) for value in row['artifacts'].values())):
            raise ValueError('SCIENTIFIC_VERSION_ORIGINAL_PROPOSALS_REQUIRED')
        modes.add(row['mode'])
    origins = {row['mode']: row for row in proposals}
    for mode, targets in artifact_targets(core['experiment']).items():
        for proposed, target in targets.items():
            if core['files'][target] != origins[mode]['artifacts']['round-1/' + proposed]:
                raise ValueError('SCIENTIFIC_VERSION_DIFFERS_FROM_REVIEWED_PROPOSALS')
    root = Path(root)
    for name, expected in core['files'].items():
        if hashlib.sha256(authority.read(root / name, limit=2000000)).hexdigest() != expected:
            raise ValueError('SCIENTIFIC_VERSION_REVIEW_INPUT_CHANGED')
    expected_origin = origin(core)
    actual = json.loads(authority.read(root / ('campaigns/isles24-pilot/experiments/' +
                                               core['experiment'] + '/scientific-origin.json')))
    if actual != expected_origin:
        raise ValueError('SCIENTIFIC_VERSION_AGENT_LINEAGE_CHANGED')
    # Human stops and fixed structural locations remain effective. This does not
    # import or execute proposed Python, nor relabel old investigator authority.
    from orchestrator.campaign import require_no_human_stop
    require_no_human_stop(root, core['experiment'])
    return core


def bindings(core):
    base = 'campaigns/isles24-pilot/experiments/' + core['experiment'] + '/'
    return {'source': core['source'], 'experiment': core['experiment'],
        'scientific_version_sha256': hashlib.sha256(encoded(core)).hexdigest(),
        'review_input_manifest_sha256': digest(core['files']),
        'protocol_decision_sha256': core['protocol_decision_sha256'],
        'proposal_sha256': digest(core['proposals']),
        'code_sha256': core['files'][base + 'run.py'],
        'spec_sha256': core['files'][base + 'SPEC.md'],
        'requirements_sha256': core['files'][base + 'requirements.txt']}


def verify_proposals(core, *, original_client, include_artifacts=False):
    """Every generated input must match the protected original reviewed artifacts."""
    if not callable(original_client):
        raise ValueError('SCIENTIFIC_VERSION_ORIGINAL_PROVIDER_CLIENT_REQUIRED')
    result = []; artifacts = {}; reviews = {}
    for row in core['proposals']:
        event = {'turn_id': row['task'], 'source': row['source'], 'attempt': '1',
                 'branch': 'astra/infrastructure-milestone-record', 'kind': 'astra_turn'}
        packet_reply = original_client('protected-originals', 'stage_packet', {'event': event})
        packet = packet_reply.get('packet')
        if (packet_reply.get('status') != 'COMPLETE' or not isinstance(packet, dict)
                or packet_reply.get('packet_sha256') != row['packet_sha256']
                or hashlib.sha256(encoded(packet)).hexdigest() != row['packet_sha256']):
            raise ValueError('SCIENTIFIC_PROPOSAL_ORIGINAL_PACKET_REQUIRED')
        task = packet.get('campaign_task', {})
        from orchestrator.continuing_research import task_contract, PROSPECTIVE_SCHEMA
        if (task.get('experiment') != core['experiment'] or task.get('mode') != row['mode']
                or packet.get('campaign_artifacts') != task_contract(task)):
            raise ValueError('SCIENTIFIC_PROPOSAL_ORIGINAL_TASK_CHANGED')
        if row['mode'] in ('specify', 'code_bundle') and (
                task['schema'] != PROSPECTIVE_SCHEMA
                or task['protocol']['decision_sha256'] != core['protocol_decision_sha256']):
            raise ValueError('SCIENTIFIC_PROPOSAL_ORIGINAL_PROTOCOL_CHANGED')
        replies = {}
        for stage in ('continuation', 'review', 'disposition'):
            reply = original_client('protected-originals', 'stage_status', {'event': event, 'stage': stage})
            if reply.get('packet_sha256') != row['packet_sha256']:
                raise ValueError('SCIENTIFIC_PROPOSAL_ORIGINAL_PACKET_CHANGED')
            answer, receipt = checked_reply(reply, stage, row['packet_sha256'])
            if (receipt.get('stage') != stage or not isinstance(receipt.get('session_id'), str)
                    or receipt.get('actual_model') not in (None, receipt['requested_model'])):
                raise ValueError('SCIENTIFIC_PROPOSAL_ORIGINAL_PROVIDER_IDENTITY')
            replies[stage] = (answer, receipt)
        author, author_receipt = replies['continuation']
        files = artifact_files(author, PROPOSAL_FILES[row['mode']])
        for name, content in files.items():
            if hashlib.sha256(content.encode()).hexdigest() != row['artifacts']['round-1/' + name]:
                raise ValueError('SCIENTIFIC_PROPOSAL_DIFFERS_FROM_MODEL_ORIGINAL')
        review = json.loads(artifact_files(replies['review'][0], ['review.json'])['review.json'])
        if set(review) != {'verdict', 'rationale'} or review['verdict'] != 'APPROVE' or not review['rationale']:
            raise ValueError('SCIENTIFIC_PROPOSAL_OPPOSING_APPROVAL_REQUIRED')
        artifacts[row['mode']] = files
        reviews[row['mode']] = review
        result.append({'task': row['task'], 'source': row['source'], 'mode': row['mode'],
            'packet_sha256': row['packet_sha256'],
            'protocol_decision_sha256': task.get('protocol', {}).get('decision_sha256'),
            'author': {'requested_model': author_receipt['requested_model'],
                'actual_model': author_receipt.get('actual_model'), 'session_id': author_receipt['session_id'],
                'model_receipt_sha256': hashlib.sha256(encoded(author_receipt)).hexdigest()},
            'reviewer_receipt_sha256': hashlib.sha256(encoded(replies['review'][1])).hexdigest(),
            'disposition_receipt_sha256': hashlib.sha256(encoded(replies['disposition'][1])).hexdigest()})
    return {'provenance': result, 'artifacts': artifacts, 'reviews': reviews} if include_artifacts else result


def decision_request(root, core, protocol, *, original_client):
    """Supply full literal review inputs and the actual original protocol evidence."""
    validate_core(root, core)
    proposals = verify_proposals(core, original_client=original_client, include_artifacts=True)
    if (not isinstance(protocol, dict) or set(protocol) !=
            {'subject', 'bindings', 'decision_path', 'decision_sha256'}
            or protocol['decision_sha256'] != core['protocol_decision_sha256']):
        raise ValueError('SCIENTIFIC_VERSION_EXACT_REVIEWED_PROTOCOL_REQUIRED')
    path = Path(protocol['decision_path'])
    if not path.is_absolute():
        path = Path(root) / path
    if hashlib.sha256(authority.read(path)).hexdigest() != protocol['decision_sha256']:
        raise ValueError('SCIENTIFIC_VERSION_PROTOCOL_DECISION_CHANGED')
    checked = verify_original_decision(root, path, action='authorize_protocol',
        subject=protocol['subject'], bindings=protocol['bindings'], original_client=original_client,
        expected_transition={'from': 'REVIEWED_PROTOCOL_PROPOSAL', 'to': 'PROTOCOL_ELIGIBLE'},
        source=core['source'])
    if checked['decision'] != 'APPLY':
        raise ValueError('SCIENTIFIC_VERSION_PROTOCOL_NOT_ELIGIBLE')
    protocol_request = original_transport(path.parent.parent)['packet']['formal_request']
    inputs = {name: authority.read(Path(root) / name, limit=2000000).decode()
              for name in sorted(core['files'])}
    return {'action': ACTION, 'subject': core['version_id'], 'bindings': bindings(core),
            'transition': TRANSITION,
            'evidence': {'scientific-version.json': encoded(core).decode(),
                         'full-review-inputs.json': json.dumps(inputs, sort_keys=True),
                         'original-proposals.json': json.dumps(proposals, sort_keys=True),
                         'original-protocol-decision.json': authority.read(path).decode(),
                         'original-reviewed-protocol.json': json.dumps(protocol_request, sort_keys=True)},
            'request': 'Assess this exact prospective scientific version against its already reviewed protocol, '
                'selected charter, full source/spec/validator/dependency/test contents and original proposal lineage. '
                'Independently challenge scientific usefulness, cohort/exposure claims, evaluation, code correctness, '
                'recovery and interpretability. This is a new explicit version, never a rewrite of frozen P001 or '
                'an old review attached to changed code. Approval permits protected capture of this version; '
                'execution still needs its separate exact launch decision and current stop/resource checks.'}


def verify_authority(root, descriptor, *, original_client):
    """Protected capture gate; returns stable pins and actual provider attribution."""
    if (not isinstance(descriptor, dict) or set(descriptor) !=
            {'core_path', 'core_sha256', 'decision_path', 'decision_sha256'}
            or descriptor['core_path'] != 'scientific-version.json'
            or not _sha(descriptor['core_sha256']) or not _sha(descriptor['decision_sha256'])):
        raise ValueError('PROSPECTIVE_SCIENTIFIC_VERSION_DESCRIPTOR_REQUIRED')
    root = Path(root)
    raw = authority.read(root / descriptor['core_path'], limit=1500000)
    if hashlib.sha256(raw).hexdigest() != descriptor['core_sha256']:
        raise ValueError('SCIENTIFIC_VERSION_CORE_CHANGED')
    core = validate_core(root, json.loads(raw))
    if raw != encoded(core) or descriptor['decision_path'] != (
            'scientific-authority/' + core['version_id'] + '/round-1/decision.json'):
        raise ValueError('SCIENTIFIC_VERSION_CANONICAL_ORIGINAL_LAYOUT')
    path = root / descriptor['decision_path']
    if hashlib.sha256(authority.read(path)).hexdigest() != descriptor['decision_sha256']:
        raise ValueError('SCIENTIFIC_VERSION_SEALED_DECISION_CHANGED')
    proof = verify_proposals(core, original_client=original_client, include_artifacts=True)
    decision = verify_original_decision(root, path, action=ACTION, subject=core['version_id'],
        bindings=bindings(core), original_client=original_client, expected_transition=TRANSITION,
        source=core['source'])
    if decision['decision'] != 'APPLY':
        raise ValueError('SCIENTIFIC_VERSION_NOT_ELIGIBLE')
    request = original_transport(path.parent.parent)['packet']['formal_request']
    actual_inputs = json.dumps({name: authority.read(root / name, limit=2000000).decode()
                               for name in sorted(core['files'])}, sort_keys=True)
    if (request['evidence'].get('scientific-version.json') != raw.decode()
            or request['evidence'].get('full-review-inputs.json') != actual_inputs
            or request['evidence'].get('original-proposals.json') != json.dumps(proof, sort_keys=True)
            or not request['evidence'].get('original-reviewed-protocol.json')):
        raise ValueError('SCIENTIFIC_VERSION_FULL_REVIEW_INPUTS_NOT_SUPPLIED')
    protocol_raw = request['evidence'].get('original-protocol-decision.json', '')
    if hashlib.sha256(protocol_raw.encode()).hexdigest() != core['protocol_decision_sha256']:
        raise ValueError('SCIENTIFIC_VERSION_REVIEWED_PROTOCOL_SEAL_REQUIRED')
    protocol = json.loads(protocol_raw)
    original = json.loads(request['evidence']['original-reviewed-protocol.json'])
    if (original.get('action') != 'authorize_protocol' or original.get('source') != core['source']
            or original.get('subject') != protocol.get('subject')
            or original.get('bindings') != protocol.get('bindings')
            or protocol.get('action') != 'authorize_protocol' or protocol.get('decision') != 'APPLY'
            or protocol.get('bindings', {}).get('experiment') != core['experiment']
            or protocol.get('bindings', {}).get('source') != core['source']):
        raise ValueError('SCIENTIFIC_VERSION_REVIEWED_PROTOCOL_CONTEXT_CHANGED')
    return {'status': 'SCIENTIFIC_VERSION_ELIGIBLE', 'source': core['source'],
            'scientific_version_sha256': descriptor['core_sha256'],
            'review_input_manifest_sha256': digest(core['files']),
            'protocol_decision_sha256': core['protocol_decision_sha256'],
            'decision_sha256': descriptor['decision_sha256'],
            'actor': decision['actor'], 'proposal_provenance': proof['provenance']}
