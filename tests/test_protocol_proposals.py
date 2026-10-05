"""Synthetic protocol construction checks; no scientific/model authorization."""
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import pytest
from orchestrator import protocol_proposals as proposals


def fixture(complete=False):
    task = {'schema': proposals.TASK_SCHEMA, 'task_id': 'synthetic-protocol-proposal-v1',
        'experiment': 'P002', 'mode': proposals.MODE, 'request': 'Propose from synthetic recorded evidence only.',
        'references': [], 'selected_by': None}
    data = {'input_manifest': {'schema': 'linux-scientific-inputs/v1', 'root': '/existing/synthetic-aggregates',
                              'files': {'summary.json': 'a' * 64}},
            'partition_registry': {'schema': 'synthetic-partitions/v1', 'description': 'Recorded synthetic aggregate scope'},
            'exposure_history': {'schema': 'synthetic-exposure/v1', 'description': 'Previously exposed synthetic aggregate'}}
    refs = []; sources = {}; files = {}
    for index, (kind, name) in enumerate(proposals.DATA_OUTPUTS.items(), 1):
        raw = json.dumps(data[kind], sort_keys=True)
        ref = {'task': str(index) * 64, 'artifact': 'round-1/' + kind + '.json',
               'sha256': hashlib.sha256(raw.encode()).hexdigest()}
        if complete:
            sources[kind] = ref; task['references'].append(ref)
            refs.append({'reference': ref, 'content': raw}); files[name] = raw
        else:
            sources[kind] = None
            files[name] = json.dumps({'schema': 'protocol-evidence-unavailable/v1', 'kind': kind,
                                     'reason': 'No recorded synthetic original supplied.'})
    protocol = {'schema': 'scientific-protocol-proposal/v1', 'protocol_id': 'synthetic-protocol-v1',
        'experiment': 'P002', 'status': 'PROPOSED' if complete else 'DEFERRED',
        'design': 'A synthetic proposed comparison; no actual science or execution.',
        'rationale': 'Synthetic construction fixture.', 'unknowns': [] if complete else ['Original evidence unavailable.'],
        'evidence': task['references'], 'data_sources': sources}
    literature = {'schema': 'recorded-literature-review/v1', 'status': 'PROPOSED' if complete else 'DEFERRED',
        'rationale': 'Only the supplied synthetic context is available.',
        'unknowns': [] if complete else ['No supplied literature.'],
        'citations': [{'context_file': 'sources.json', 'url': 'https://example.invalid/synthetic-study',
            'evidence_level': 'supplied_context_only', 'finding': 'Synthetic cited source.'}] if complete else []}
    files[proposals.OUTPUTS[0]] = json.dumps(protocol)
    files[proposals.OUTPUTS[1]] = 'Synthetic methodology proposal, endpoints, comparison, uncertainty and limitations.'
    files[proposals.OUTPUTS[2]] = json.dumps(literature)
    context = {'continuing-research-inputs.json': json.dumps({'task': task, 'references': refs}),
               'sources.json': 'Recorded synthetic citation https://example.invalid/synthetic-study'}
    return task, files, context


def test_first_protocol_proposal_needs_no_prior_protocol_or_old_p001_result():
    task, _, _ = fixture()
    contract = proposals.task_contract(task)
    assert contract['mode'] == 'protocol_proposal' and contract['experiment'] == 'P002'
    root = Path(__file__).resolve().parents[1]
    context = proposals.grounding(root, task)
    scope = json.loads(context['protocol-proposal-scope.json'])
    assert scope['prior_protocol_required'] is False and scope['execution'] is False
    assert 'charters/isles24/CHARTER.md' not in context
    assert not any('interpretation_receipt.json' in name for name in context)
    for mutation in ({'experiment': 'P001'}, {'mode': 'launch'}, {'permission': 'execute'}):
        with pytest.raises(ValueError): proposals.task_contract({**task, **mutation})


def test_unknown_data_and_literature_form_a_real_deferral():
    task, files, context = fixture()
    result = proposals.validate_bundle(task, files, context)
    assert result['status'] == 'DEFERRED'
    assert set(result['missing_evidence']) == set(proposals.DATA_OUTPUTS) | {'literature_review'}
    assert result['scientific_approval'] is result['data_access_authority'] is result['execution_authority'] is False
    protocol = json.loads(files[proposals.OUTPUTS[0]])
    protocol.update(status='PROPOSED', unknowns=[])
    files[proposals.OUTPUTS[0]] = json.dumps(protocol)
    with pytest.raises(ValueError, match='MISSING_EVIDENCE_REQUIRES_DEFERRAL'):
        proposals.validate_bundle(task, files, context)


def test_complete_originals_remain_only_a_reviewable_proposal():
    task, files, context = fixture(True)
    result = proposals.validate_bundle(task, files, context)
    assert result['status'] == 'PROPOSED' and not result['missing_evidence']
    assert not result['scientific_approval'] and not result['execution_authority']
    assert set(result['artifact_sha256']) == set(proposals.OUTPUTS)
    assert 'do not invent them' in proposals.instructions(task, context)


@pytest.mark.parametrize('kind', list(proposals.DATA_OUTPUTS))
def test_new_membership_or_file_inventory_cannot_be_invented(kind):
    task, files, context = fixture(True)
    value = json.loads(files[proposals.DATA_OUTPUTS[kind]])
    value['invented'] = 'New unobserved cohort or payload claim'
    files[proposals.DATA_OUTPUTS[kind]] = json.dumps(value)
    with pytest.raises(ValueError, match='MEMBERSHIP_OR_INPUTS_INVENTED'):
        proposals.validate_bundle(task, files, context)


def test_literature_cannot_claim_unseen_source_or_unperformed_search():
    task, files, context = fixture(True)
    original = files[proposals.OUTPUTS[2]]
    literature = json.loads(original)
    literature['citations'][0]['url'] = 'https://example.invalid/unseen-study'
    files[proposals.OUTPUTS[2]] = json.dumps(literature)
    with pytest.raises(ValueError, match='INVENTED_LITERATURE_PROVENANCE'):
        proposals.validate_bundle(task, files, context)
    literature = json.loads(original); literature['citations'][0]['evidence_level'] = 'freshly_searched_full_paper'
    files[proposals.OUTPUTS[2]] = json.dumps(literature)
    with pytest.raises(ValueError, match='INVENTED_LITERATURE_PROVENANCE'):
        proposals.validate_bundle(task, files, context)


def test_original_context_and_evidence_hashes_are_checked():
    task, files, context = fixture(True)
    value = json.loads(context['continuing-research-inputs.json'])
    value['references'][0]['content'] = '{}'
    context['continuing-research-inputs.json'] = json.dumps(value)
    with pytest.raises(ValueError, match='ORIGINAL_EVIDENCE_CHANGED'):
        proposals.validate_bundle(task, files, context)


def authority_inputs(files):
    refs = {}; contents = {}
    for key, name in proposals.AUTHORITY_ARTIFACTS.items():
        refs[key] = {'task': 'f' * 64, 'artifact': 'round-1/' + name,
                     'sha256': hashlib.sha256(files[name].encode()).hexdigest()}
        contents[key] = files[name]
    return refs, contents


def test_separate_protocol_authority_refuses_deferred_or_mixed_version_bundle():
    _, files, _ = fixture()
    refs, contents = authority_inputs(files)
    with pytest.raises(ValueError, match='DEFERRED_MISSING_EVIDENCE'):
        proposals.authorization_artifacts('synthetic-protocol-v1', 'P002', refs, contents)
    _, files, _ = fixture(True)
    refs, contents = authority_inputs(files)
    checked = proposals.authorization_artifacts('synthetic-protocol-v1', 'P002', refs, contents)
    assert checked['scientific_approval'] is False
    refs['methodology_review_sha256']['task'] = 'e' * 64
    with pytest.raises(ValueError, match='MIXED_BUNDLE_REFUSED'):
        proposals.authorization_artifacts('synthetic-protocol-v1', 'P002', refs, contents)
