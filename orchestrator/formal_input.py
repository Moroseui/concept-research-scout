"""Prospective formal input: exact request once, native history and originals."""
import hashlib
import json

from orchestrator import current_scientific_input as current
from orchestrator import disposition_context as disposition, hosted_context as hosted
from orchestrator.hosted_cycle import encoded

FORMAL_KEYS = (*hosted.TASK_KEYS, 'formal_request')


def _view(root, packet, source):
    from orchestrator.scientific_evidence_runtime import enabled
    if not (current.is_current(packet) and current.is_formal(packet)
            and enabled(root, source, formal_current=True)):
        raise ValueError('CURRENT_FORMAL_SOURCE_PROFILE_REQUIRED')
    view = disposition.selected_packet_view(packet, source)
    binding = disposition.validate_selected_packet_view(view, packet, source)
    return view, binding


def evidence_for_packet(root, packet, source):
    request = packet['formal_request']
    if not current.is_current(packet):
        return {**request['evidence'], 'recorded-formal-request.json': json.dumps(packet, sort_keys=True)}
    view, _ = _view(root, packet, source)
    reference = hosted._selected_reference(view, packet, source, task_keys=FORMAL_KEYS)
    return {'recorded-formal-request.json': json.dumps(reference, sort_keys=True)}


def presentation(root, packet, context, prompt, source):
    view, binding = _view(root, packet, source)
    expected = evidence_for_packet(root, packet, source)
    prompt = hosted._replace_reference_section(prompt, hosted.EVIDENCE_MARKER, expected, expected)
    policy = hosted.shared_policy(root)
    if context.get('shared_policy') != policy:
        raise ValueError('SELECTED_HISTORY_POLICY_CHANGED')
    marker = '\nCURRENT USER POLICY:\n'
    if (prompt.count(marker) != 1 or hosted.TRUSTED_POLICY_MARKER in prompt):
        raise ValueError('CURRENT_FORMAL_EXACT_POLICY_REQUIRED')
    prefix, suffix = prompt.split(marker, 1)
    try:
        actual, end = json.JSONDecoder().raw_decode(suffix)
    except ValueError as error:
        raise ValueError('CURRENT_FORMAL_EXACT_POLICY_REQUIRED') from error
    if (actual != policy or suffix[:end] != json.dumps(policy)
            or not suffix[end:].startswith(hosted.TRUSTED_POLICY_END)):
        raise ValueError('CURRENT_FORMAL_POLICY_CHANGED')
    reference = hosted.trusted_policy_reference(policy, source)
    changed = prefix + hosted.TRUSTED_POLICY_MARKER + json.dumps(reference) + suffix[end:]
    if hosted.check_trusted_policy_reference(changed, context, source) != prompt:
        raise ValueError('CURRENT_FORMAL_POLICY_RECONSTRUCTION_CHANGED')
    shown = {**context, 'task_state': {key: view[key] for key in FORMAL_KEYS if key in view}}
    shown['selected_scientific_presentation'] = {**binding,
        'original_context_sha256': hashlib.sha256(encoded(context)).hexdigest(),
        'selected_context_sha256': hashlib.sha256(encoded(shown)).hexdigest(),
        'selected_context_digest_scope': 'This context before this metadata and the separate outer-document layer.',
        'ordinary_change_overview': 'Index only; current criticism and exact formal request stay literal.'}
    return shown, changed
