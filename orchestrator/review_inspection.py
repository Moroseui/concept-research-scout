"""Deterministic reviewer-visible view; host originals remain the authority.

Only prior runtime/session/refusal records become ID/hash references. Source and
ordinary review evidence remain exact bytes. This view neither admits nor approves.
"""
import json
from pathlib import Path
from orchestrator import autonomy_review as review, private_records

IDENTITY_KEYS = frozenset({
    'session_id', 'conversation_id', 'model_usage', 'modelUsage',
    'provider_evidence', 'successful_read_paths', 'tool_use_ids',
})
HISTORY_NAMES = frozenset({
    'native-stream.jsonl', 'native-stderr.log', 'process.json',
    'process-exit.json', 'packet-manifest.json', 'credential-cleanup.json',
    'observed-m2-exhaustion.json',
})


def history_record(name, raw):
    # Source (including synthetic test cases) is never transformed or excluded.
    if name.startswith('source/'):
        return False
    leaf = Path(name).name
    stripped = leaf.removeprefix('original-').removeprefix('prior-')
    if (stripped in HISTORY_NAMES or leaf.endswith('.jsonl') or
        any(word in leaf.lower() for word in ('transcript', 'refusal', 'session'))):
        return True
    if review.PROVIDER_REFUSAL_PREFIX.encode() in raw:
        return True
    try:
        data = json.loads(raw)
    except (ValueError, UnicodeError):
        return False
    def metadata(value):
        if isinstance(value, dict):
            return bool(IDENTITY_KEYS & value.keys()) or any(metadata(v) for v in value.values())
        if isinstance(value, list):
            return any(metadata(v) for v in value)
        return False
    return metadata(data)


def contents(packet):
    packet = Path(packet)
    m = review.verify_packet(packet)
    bodies = {}
    refs = []
    for name, expected in sorted(m['files'].items()):
        raw = review.regular(packet / name).read_bytes()
        if review.sha(raw) != expected:
            raise ValueError('INSPECTION_ORIGINAL_CHANGED')
        if history_record(name, raw):
            if b'BLOCKER[' in raw:
                raise ValueError('MIXED_HISTORY_FINDINGS_REQUIRE_SEPARATE_EVIDENCE')
            refs.append({'id': name, 'sha256': expected})
        else:
            bodies[name] = raw
    # Allowlist current review state. All other host manifest fields are bound
    # references, including predecessors, their usage, and selection provenance.
    fields = ('source_sha', 'runtime_sha256', 'change_id', 'round', 'scope', 'source_files')
    view = {key: m[key] for key in fields}
    for key, value in sorted(m.items()):
        if key not in {*fields, 'files', 'schema', 'prompt_version', 'brief_policy'} and value is not None:
            refs.append({'id': 'host-manifest/' + key, 'sha256': review.sha(review.canonical(value))})
    view.update(schema='autonomy-review-inspection/v1',
                packet_sha256=review.sha(review.canonical(m)),
                files={n: review.sha(raw) for n, raw in bodies.items()},
                history_refs=refs)
    bodies['manifest.json'] = review.canonical(view)
    bodies['prompt.txt'] = review.prompt_for(m).encode()
    return m, bodies


def prepare(packet, destination):
    destination = Path(destination)
    m, bodies = contents(packet)
    if destination.exists():
        raise ValueError('EXISTING_INSPECTION_VIEW_PRESERVED')
    private_records.mkdir(destination)
    for name, raw in bodies.items():
        review.write_once(destination / name, raw)
    return verify(packet, destination)


def verify(packet, destination):
    m, bodies = contents(packet)
    expected = {name: review.sha(raw) for name, raw in bodies.items()}
    if review.inventory(destination) != expected:
        raise ValueError('INSPECTION_VIEW_CHANGED')
    private_records.check_tree(destination)
    return {'packet_sha256': review.sha(review.canonical(m)),
            'inspection_manifest_sha256': expected['manifest.json'],
            'files': expected, 'file_count': len(expected),
            'utf8_bytes': sum(len(raw) for raw in bodies.values())}
