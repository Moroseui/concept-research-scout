"""Mechanical copies of reviewed formal outputs into a separate scientific version.

No source construction, scientific judgment, execution or legacy approval receipt
is invented here. Original completed task workspaces are always preserved.
"""
from copy import deepcopy
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess

from orchestrator.hosted_cycle import encoded
from orchestrator.linux_scientific_jobs import original
from orchestrator.operations_report import private_root
from orchestrator.remote_supervisor import checked_source, lock

def immutable(path, body):
    # These are exact private source copies, not a publication export. Generated
    # artifacts have already passed read_reference's existing content guard;
    # installed support bytes retain their pinned identity and original encoding.
    original(path, body, mode=0o600)


def _pin(value, length=64):
    if not isinstance(value, str) or not re.fullmatch('[0-9a-f]{'+str(length)+'}', value):
        raise ValueError('SCIENTIFIC_MATERIALIZATION_EXACT_DIGEST_REQUIRED')


def _read(path, maximum=2000000):
    path = Path(path).absolute()
    if '..' in path.parts or any(p.is_symlink() for p in (path, *path.parents)) or not path.is_file():
        raise ValueError('SCIENTIFIC_MATERIALIZATION_REGULAR_ORIGINAL_REQUIRED')
    raw = path.read_bytes()
    if len(raw) > maximum: raise ValueError('SCIENTIFIC_MATERIALIZATION_FILE_BOUND')
    return raw


def _source_file(root, source, name):
    """Only the pinned installed source; never a network or implicit blob fetch."""
    path = root/name
    if path.exists():
        raw = _read(path)
    else:
        try:
            raw = subprocess.check_output(['git', '-c', 'safe.directory='+str(root), 'show', source+':'+name],
                cwd=root, env={'PATH': '/usr/bin:/bin', 'LANG': 'C.UTF-8', 'GIT_NO_LAZY_FETCH': '1',
                               'GIT_OPTIONAL_LOCKS': '0'}, timeout=30, stderr=subprocess.DEVNULL)
        except subprocess.SubprocessError as error:
            raise ValueError('SCIENTIFIC_REVIEW_SUPPORT_NOT_INSTALLED:'+name) from error
    if len(raw) > 2000000: raise ValueError('SCIENTIFIC_MATERIALIZATION_FILE_BOUND')
    return raw


def _proposal_bytes(config, proposals, experiment, outputs, protocol_decision_sha256):
    from orchestrator import continuing_research
    if not isinstance(proposals, list) or len(proposals) != 3:
        raise ValueError('SCIENTIFIC_THREE_REVIEWED_FORMAL_PROPOSALS_REQUIRED')
    result = {}; seen = set()
    for proposal in proposals:
        if (set(proposal) != {'task', 'source', 'mode', 'packet_sha256', 'artifacts'} or
                proposal['mode'] not in outputs or
                proposal['mode'] in seen or set(proposal['artifacts']) != outputs[proposal['mode']]):
            raise ValueError('SCIENTIFIC_EXACT_FORMAL_OUTPUT_SET_REQUIRED')
        _pin(proposal['task']); _pin(proposal['packet_sha256']); _pin(proposal['source'], 40)
        seen.add(proposal['mode'])
        folder = Path(config['state'])/'tasks'/proposal['task']
        packet_raw = _read(folder/'packet.json'); packet = json.loads(packet_raw)
        task = packet.get('campaign_task', {})
        disposition = json.loads(_read(folder/'scientific-disposition.json'))
        if (hashlib.sha256(encoded(packet)).hexdigest() != proposal['packet_sha256'] or task.get('experiment') != experiment or
                task.get('mode') != proposal['mode'] or disposition.get('task') != proposal['task'] or
                disposition.get('review_verdict') != 'APPROVE' or
                disposition.get('acceptance_status') != 'APPROVED_PROPOSAL_ONLY'):
            raise ValueError('SCIENTIFIC_REVIEWED_ORIGINAL_PROPOSAL_REQUIRED')
        if (proposal['mode'] in ('specify', 'code_bundle') and
                task.get('protocol', {}).get('decision_sha256') != protocol_decision_sha256):
            raise ValueError('SCIENTIFIC_PROPOSED_PROTOCOL_IDENTITY_CHANGED')
        for artifact, sha in proposal['artifacts'].items():
            _pin(sha)
            raw = continuing_research.read_reference(config, {'task': proposal['task'], 'artifact': artifact, 'sha256': sha})
            if hashlib.sha256(raw).hexdigest() != sha:
                raise ValueError('SCIENTIFIC_PROPOSED_BYTES_CHANGED')
            result[(proposal['mode'], artifact)] = raw
    return result


def materialize(config, *, experiment, version_id, proposals, protocol_decision_sha256,
                parent_version_sha256=None, original_client, by):
    """Prepare a prospective version; its actual full-input review comes later.

    The same controller-owned operation serves a human command and the agent
    driver. The caller supplies only saved proposal identities and version names;
    scientific file bodies come from checked original system artifacts.
    """
    from orchestrator import scientific_versions as versions
    from orchestrator.change_requests import actor
    actor(by)
    if os.getuid() != config['controller_uid'] or config['controller_uid'] <= 0:
        raise ValueError('SCIENTIFIC_MATERIALIZATION_CONTROLLER_IDENTITY_REQUIRED')
    if experiment not in ('P002', 'P003'):
        raise ValueError('SCIENTIFIC_MATERIALIZATION_PRESERVES_FROZEN_P001')
    if not isinstance(version_id, str) or not re.fullmatch('[a-z0-9][a-z0-9-]{0,79}', version_id):
        raise ValueError('SCIENTIFIC_VERSION_ID_REQUIRED')
    _pin(protocol_decision_sha256)
    if parent_version_sha256 is not None: _pin(parent_version_sha256)
    if not callable(original_client): raise ValueError('ORIGINAL_PROTECTED_MODEL_REPLIES_REQUIRED')
    root = checked_source(config['source_root'], config['source'])
    proposals = sorted(deepcopy(proposals), key=lambda row: row.get('mode', ''))
    outputs = {mode: {'round-1/'+name for name in names} for mode, names in versions.PROPOSAL_FILES.items()}
    raw = _proposal_bytes(config, proposals, experiment, outputs, protocol_decision_sha256)
    prefix = 'campaigns/isles24-pilot/experiments/'+experiment+'/'
    mapping = {(mode, 'round-1/'+name): target for mode, names in versions.artifact_targets(experiment).items()
               for name, target in names.items()}
    files = {target: raw[original] for original, target in mapping.items()}
    # Syntax checking is read-only; no proposed Python is imported or executed.
    for name in (prefix+'run.py', prefix+'validate_return.py', 'tests/test_prediction_'+experiment.lower()+'.py'):
        compile(files[name], name, 'exec')
    json.loads(files[prefix+'publication.json'])
    seed = {'schema': 'prospective-scientific-version/v1', 'source': config['source'],
            'experiment': experiment, 'version_id': version_id,
            'parent_version_sha256': parent_version_sha256, 'proposals': proposals,
            'protocol_decision_sha256': protocol_decision_sha256}
    origin = versions.origin({**seed, 'files': {}})
    files[prefix+'scientific-origin.json'] = encoded(origin)
    required = versions.required_files(root, experiment)
    if not set(files) <= set(required) or prefix+'investigator_decision.json' in required:
        raise ValueError('SCIENTIFIC_PROSPECTIVE_REQUIRED_FILES_CHANGED')
    for name in required:
        if name not in files: files[name] = _source_file(root, config['source'], name)
    core = {**seed, 'files': {name: hashlib.sha256(body).hexdigest() for name, body in sorted(files.items())}}
    # Same genuine original-provider check used by the later version verifier.
    # No full-version approval is claimed by passing this proposal-origin check.
    proposal_proof = versions.verify_proposals(core, original_client=original_client)
    core_sha = hashlib.sha256(encoded(core)).hexdigest()
    parent = private_root(private_root(config['state'])/'scientific-versions')
    destination = parent/core_sha; workspace = destination/'workspace'
    with lock(parent/'.materialization.lock'):
        if destination.exists():
            receipt_path = destination/'materialization.json'
            if not receipt_path.exists():
                raise ValueError('SCIENTIFIC_PARTIAL_MATERIALIZATION_RECONCILIATION_REQUIRED')
            receipt = json.loads(_read(receipt_path))
            if receipt['scientific_version_sha256'] != core_sha or _read(workspace/'scientific-version.json') != encoded(core):
                raise ValueError('SCIENTIFIC_ORIGINAL_MATERIALIZATION_CHANGED')
            for name, sha in receipt['workspace_file_sha256'].items():
                if hashlib.sha256(_read(workspace/name)).hexdigest() != sha:
                    raise ValueError('SCIENTIFIC_ORIGINAL_MATERIALIZATION_CHANGED')
            return {**receipt, 'duplicate': True}
        # Support context is unchanged installed source, copied without .git.
        names = subprocess.check_output(['git', '-c', 'safe.directory='+str(root), 'ls-files', '-z'],
            cwd=root, env={'PATH': '/usr/bin:/bin', 'GIT_NO_LAZY_FETCH': '1', 'GIT_OPTIONAL_LOCKS': '0'}, timeout=30)
        support = {}
        for raw_name in names.split(b'\0'):
            if not raw_name: continue
            name = raw_name.decode(); path = root/name
            # Fresh prospective experiments carry no manufactured old markers.
            if name.startswith(prefix): continue
            if path.exists(): support[name] = _read(path)
        support.update(files)
        if len(support) > 5000 or sum(map(len, support.values())) > 32000000:
            raise ValueError('SCIENTIFIC_MATERIALIZATION_TOTAL_BOUND')
        destination = private_root(destination); workspace = private_root(workspace)
        immutable(destination/'materialization-intent.json', encoded({'scientific_version_sha256': core_sha,
            'source': config['source'], 'workspace_file_sha256': {name: hashlib.sha256(body).hexdigest() for name, body in support.items()}}))
        for name, body in sorted(support.items()):
            path = workspace/name; private_root(path.parent); immutable(path, body)
        immutable(workspace/'scientific-version.json', encoded(core))
        versions.validate_core(workspace, core)
        receipt = {'schema': 'scientific-materialization/v1', 'status': 'PROSPECTIVE_VERSION_PENDING_FULL_REVIEW',
            'scientific_version_sha256': core_sha, 'source': config['source'], 'experiment': experiment,
            'version_id': version_id, 'workspace': str(workspace), 'core_path': 'scientific-version.json',
            'workspace_file_sha256': {name: hashlib.sha256(body).hexdigest() for name, body in support.items()},
            'actual_copies': [{'source_mode': mode, 'source_artifact': artifact, 'destination': name,
                              'sha256': hashlib.sha256(files[name]).hexdigest()} for (mode, artifact), name in mapping.items()],
            'proposal_provenance': proposal_proof, 'model_calls': 0, 'scientific_execution': False,
            'applied_by': by,
            'full_review_status': 'PENDING', 'legacy_approval_created': False, 'original_tasks_modified': False}
        immutable(destination/'materialization.json', encoded(receipt))
        return {**receipt, 'duplicate': False}


def workspace(config, scientific_version_sha256):
    """Resolve one complete saved materialization, never a consumer path."""
    _pin(scientific_version_sha256)
    checked_source(config['source_root'], config['source'])
    parent = Path(config['state'])/'scientific-versions'/scientific_version_sha256
    root = parent/'workspace'
    saved = json.loads(_read(parent/'materialization.json'))
    core_raw = _read(root/'scientific-version.json'); core = json.loads(core_raw)
    if (saved.get('source') != config['source'] or core.get('source') != config['source'] or
            saved.get('scientific_version_sha256') != scientific_version_sha256 or
            saved.get('workspace') != str(root) or core_raw != encoded(core) or
            hashlib.sha256(core_raw).hexdigest() != scientific_version_sha256):
        raise ValueError('SCIENTIFIC_ORIGINAL_MATERIALIZATION_CHANGED')
    for name, sha in saved['workspace_file_sha256'].items():
        if hashlib.sha256(_read(root/name)).hexdigest() != sha:
            raise ValueError('SCIENTIFIC_ORIGINAL_MATERIALIZATION_CHANGED')
    return root, core


def attach_review(config, *, scientific_version_sha256, decision_path, original_client, by):
    """Copy an actual original full-input decision into its fixed version layout.

    No judgment is constructed or re-sealed. Incomplete attachment remains
    visible and refuses automatic retry. The final verifier checks the actual
    original provider replies and all supplied review inputs before any receipt.
    """
    from orchestrator import scientific_versions as versions, formal_decisions
    from orchestrator.change_requests import actor
    from orchestrator.linux_scientific_jobs import _decision_files
    actor(by)
    if os.getuid() != config['controller_uid'] or config['controller_uid'] <= 0:
        raise ValueError('SCIENTIFIC_MATERIALIZATION_CONTROLLER_IDENTITY_REQUIRED')
    if not callable(original_client): raise ValueError('ORIGINAL_PROTECTED_MODEL_REPLIES_REQUIRED')
    root, core = workspace(config, scientific_version_sha256)
    versions.validate_core(root, core)
    path = Path(decision_path).absolute()
    expected = Path(config['state'])/'formal-decisions'
    if (path.name != 'decision.json' or path.parent.name != 'round-1' or
            path.parent.parent.parent != expected or
            not re.fullmatch('[A-Za-z0-9_-]{1,100}', path.parent.parent.name)):
        raise ValueError('SCIENTIFIC_ORIGINAL_FORMAL_DECISION_REQUIRED')
    decision = formal_decisions.verify_original_decision(root, path, action=versions.ACTION,
        subject=core['version_id'], bindings=versions.bindings(core), source=core['source'],
        expected_transition=versions.TRANSITION, original_client=original_client)
    if decision['decision'] != 'APPLY': raise ValueError('SCIENTIFIC_VERSION_NOT_ELIGIBLE')
    files = {'round-1/'+name: raw for name, raw in _decision_files(path, providers=True).items()}
    files['authority-transport.json'] = _read(path.parent.parent/'authority-transport.json')
    if any('/' in name.removeprefix('round-1/') for name in files):
        raise ValueError('SCIENTIFIC_AUTHORITY_FLAT_ORIGINAL_LAYOUT_REQUIRED')
    descriptor = {'core_path': 'scientific-version.json', 'core_sha256': scientific_version_sha256,
        'decision_path': 'scientific-authority/'+core['version_id']+'/round-1/decision.json',
        'decision_sha256': hashlib.sha256(files['round-1/decision.json']).hexdigest()}
    parent = root/'scientific-authority'
    with lock(root.parent/'.attachment.lock'):
        destination = parent/core['version_id']; receipt_path = destination/'attachment.json'
        if destination.exists():
            if not receipt_path.exists():
                raise ValueError('SCIENTIFIC_PARTIAL_REVIEW_ATTACHMENT_RECONCILIATION_REQUIRED')
            saved = json.loads(_read(receipt_path))
            if saved['descriptor'] != descriptor:
                raise ValueError('SCIENTIFIC_ORIGINAL_REVIEW_ATTACHMENT_CHANGED')
            for name, sha in saved['files'].items():
                if hashlib.sha256(_read(destination/name)).hexdigest() != sha:
                    raise ValueError('SCIENTIFIC_ORIGINAL_REVIEW_ATTACHMENT_CHANGED')
            versions.verify_authority(root, descriptor, original_client=original_client)
            return {**saved, 'duplicate': True}
        private_root(parent); private_root(destination)
        immutable(destination/'attachment-intent.json', encoded({'descriptor': descriptor,
            'original_decision': str(path), 'files': {n: hashlib.sha256(v).hexdigest() for n, v in files.items()}}))
        for name, raw in sorted(files.items()):
            target = destination/name; private_root(target.parent); immutable(target, raw)
        authority = versions.verify_authority(root, descriptor, original_client=original_client)
        receipt = {'schema': 'scientific-review-attachment/v1', 'status': 'SCIENTIFIC_VERSION_ELIGIBLE',
            'source': core['source'], 'workspace': str(root), 'descriptor': descriptor,
            'original_decision': str(path), 'authority': authority,
            'files': {n: hashlib.sha256(v).hexdigest() for n, v in files.items()},
            'applied_by': by, 'model_calls': 0, 'scientific_acceptance': False}
        immutable(receipt_path, encoded(receipt))
        return {**receipt, 'duplicate': False}


def prepare_job(config, **kwargs):
    from orchestrator.scientific_job_inputs import prepare_job as operation
    return operation(config, **kwargs)


def import_result(config, **kwargs):
    from orchestrator.scientific_job_results import import_result as operation
    return operation(config, **kwargs)
