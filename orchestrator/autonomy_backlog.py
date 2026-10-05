"""Exact operator backlog bindings for M4; this module never admits a call.

The driver must load the binding from its reviewed, protected configuration,
not from a model output. Natural-language proposals cannot approve an item.
Public repository access remains read-only; no function writes BACKLOG.md.
"""
from dataclasses import dataclass
import hashlib
import re


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


@dataclass(frozen=True)
class BacklogItem:
    number: int
    text: str
    sha256: str
    mode: str
    state: str
    prerequisites: tuple


@dataclass(frozen=True)
class Backlog:
    sha256: str
    operator_sha256: str
    items: tuple


def numbered_items(raw):
    """Retain exact item bytes, including line endings and continuation lines."""
    if not isinstance(raw, bytes) or len(raw) > 100_000 or b'\x00' in raw:
        raise ValueError('BACKLOG_DOCUMENT_LIMIT')
    text = raw.decode('utf-8')
    matches = list(re.finditer(r'(?m)^([1-9][0-9]*)\. ', text))
    if not matches:
        raise ValueError('BACKLOG_ITEMS_REQUIRED')
    result = {}
    for i, match in enumerate(matches):
        number = int(match[1])
        if number in result:
            raise ValueError('BACKLOG_DUPLICATE_ITEM')
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        body = text[match.start():end]
        result[number] = (body, sha(body.encode('utf-8')))
    return result


def load(raw, binding, operator_original):
    """Verify a controller-owned interpretation of exact operator authority.

    Approval state is deliberately not inferred from words such as 'approved'
    appearing in an item. A changed operator document requires a new binding.
    """
    if set(binding) != {'schema', 'backlog_sha256', 'operator_sha256', 'items'}:
        raise ValueError('BACKLOG_BINDING_FIELDS')
    if binding['schema'] != 'operator-backlog/v1':
        raise ValueError('BACKLOG_BINDING_SCHEMA')
    if sha(raw) != binding['backlog_sha256'] or sha(operator_original) != binding['operator_sha256']:
        raise ValueError('BACKLOG_AUTHORITY_CHANGED')
    found = numbered_items(raw)
    items = []
    seen = set()
    for row in binding['items']:
        if set(row) != {'number', 'sha256', 'mode', 'state', 'prerequisites'}:
            raise ValueError('BACKLOG_ITEM_FIELDS')
        number = row['number']
        if type(number) is not int or number in seen or number not in found:
            raise ValueError('BACKLOG_ITEM_ID')
        seen.add(number)
        if row['sha256'] != found[number][1]:
            raise ValueError('BACKLOG_ITEM_CHANGED')
        if row['mode'] not in {'analysis', 'cpu', 'gpu'}:
            raise ValueError('BACKLOG_ITEM_MODE')
        if row['state'] not in {'AUTHORIZED', 'WAIT_OPERATOR', 'NOT_AUTHORIZED'}:
            raise ValueError('BACKLOG_ITEM_AUTHORITY_STATE')
        prerequisites = row['prerequisites']
        if (not isinstance(prerequisites, list)
                or any(type(x) is not int or x >= number or x not in found for x in prerequisites)
                or len(set(prerequisites)) != len(prerequisites)):
            raise ValueError('BACKLOG_PREREQUISITES')
        items.append(BacklogItem(number, found[number][0], row['sha256'],
                                row['mode'], row['state'], tuple(prerequisites)))
    if seen != set(found):
        raise ValueError('BACKLOG_UNBOUND_ITEM')
    return Backlog(sha(raw), sha(operator_original), tuple(sorted(items, key=lambda x: x.number)))


def require_item(backlog, number, expected_hash, mode, completed_items=()):
    """Selection check only; native admission, review and input gates follow."""
    if not isinstance(backlog, Backlog):
        raise ValueError('VERIFIED_BACKLOG_REQUIRED')
    item = next((x for x in backlog.items if x.number == number), None)
    if item is None or item.sha256 != expected_hash or item.mode != mode:
        raise ValueError('NEXT_DECISION_BACKLOG_MISMATCH')
    if item.state != 'AUTHORIZED':
        raise ValueError('BACKLOG_ITEM_NOT_AUTHORIZED')
    if not set(item.prerequisites) <= set(completed_items):
        raise ValueError('BACKLOG_PREREQUISITE_INCOMPLETE')
    return item


def compatible_inputs(required, accepted):
    """Compare controller-verified accepted evidence with the consumer contract.

    `accepted` must come from validated native completion and independent review
    in the driver. A model-supplied declaration of acceptance is not that record.
    This pure comparison neither accepts evidence nor registers a successor.
    """
    if (accepted.get('status') != 'ACCEPTED'
            or accepted.get('validation_status') != 'VALID'
            or accepted.get('review_verdict') != 'APPROVE'):
        raise ValueError('VALIDATED_ACCEPTED_INPUT_REQUIRED')
    keys = {'cohort_sha256', 'split_sha256', 'feature_cache_sha256', 'files'}
    if set(required) != keys or set(accepted.get('contract', {})) != keys:
        raise ValueError('SUCCESSOR_INPUT_CONTRACT_FIELDS')
    source = accepted['contract']
    for key in keys - {'files'}:
        value = required[key]
        if not isinstance(value, str) or not re.fullmatch(r'[0-9a-f]{64}', value) or source[key] != value:
            raise ValueError('SUCCESSOR_INPUT_IDENTITY_MISMATCH:' + key)
    if not isinstance(required['files'], dict) or not required['files']:
        raise ValueError('SUCCESSOR_INPUT_FILES_REQUIRED')
    if not isinstance(source['files'], dict):
        raise ValueError('ACCEPTED_INPUT_FILES_REQUIRED')
    for name, value in required['files'].items():
        if (not isinstance(name, str) or not name or name.startswith('/')
                or '\\' in name or any(x in {'', '.', '..'} for x in name.split('/'))
                or not isinstance(value, str) or not re.fullmatch(r'[0-9a-f]{64}', value)
                or source['files'].get(name) != value):
            raise ValueError('SUCCESSOR_INPUT_FILE_MISMATCH')
    return True
