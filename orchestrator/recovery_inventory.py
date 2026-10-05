"""Bounded, lossless recovery pages in the existing reviewed literal store.

This representation changes no preservation semantics: callers resolve to the
original terminal-v1 object, then use its existing validator and equality checks.
No page is an instruction, scientific evidence summary, or permission to omit rows.
"""
from copy import deepcopy
import json
from orchestrator import deployment_review as gate

INLINE = 'reviewed-deployment-recovery/operator-terminal-v1'
PAGED = 'reviewed-deployment-recovery/operator-terminal-paged-v2'
MAX_PAGE_BYTES = 1_000_000
MAX_EXPANDED_BYTES = 20_000_000
MAX_PAGES = 32


def _canonical(raw):
    gate.require(isinstance(raw, bytes), 'RECOVERY_PAGE_BYTES_REQUIRED')
    try:
        value = json.loads(raw)
    except (ValueError, UnicodeError):
        gate.require(False, 'RECOVERY_PAGE_JSON_REQUIRED')
    # Also rejects repeated keys within a page, noncanonical numeric spellings,
    # whitespace tricks and non-UTF8 encodings. Across-page duplicates are separate.
    gate.require(isinstance(value, dict) and value and gate.encoded(value) == raw,
                 'RECOVERY_CANONICAL_PAGE_REQUIRED')
    return value


def resolve(recovery, read_literal):
    """Return the original v1 value and all actually read, authenticated pages.

    The accessor enforces its own filesystem boundary; only validated digest names
    are supplied. Runtime callers still validate_recovery after resolving.
    """
    if recovery.get('schema') != PAGED:
        return recovery, {}
    result = deepcopy(recovery)
    baseline = result.get('terminal_admissions')
    gate.require(isinstance(baseline, dict) and 'non_ledger_files' not in baseline
                 and 'non_ledger_inventory' in baseline, 'RECOVERY_PAGED_BASELINE_REQUIRED')
    spec = baseline.pop('non_ledger_inventory')
    gate.require(isinstance(spec, dict) and set(spec) == {'pages','files','bytes','sha256'},
                 'RECOVERY_PAGE_DESCRIPTOR_REQUIRED')
    gate.pin(spec['sha256'])
    gate.require(type(spec['files']) is int and spec['files'] > 0
                 and type(spec['bytes']) is int and 0 < spec['bytes'] <= MAX_EXPANDED_BYTES
                 and isinstance(spec['pages'], list) and 0 < len(spec['pages']) <= MAX_PAGES,
                 'RECOVERY_EXPANDED_BOUND_REQUIRED')
    inventory = {}; originals = {}; total = 0; previous = None
    for item in spec['pages']:
        gate.require(isinstance(item, dict) and set(item) == {'sha256','bytes','files'}
                     and type(item['bytes']) is int and 0 < item['bytes'] <= MAX_PAGE_BYTES
                     and type(item['files']) is int and item['files'] > 0,
                     'RECOVERY_PAGE_DESCRIPTOR_REQUIRED')
        sha = gate.pin(item['sha256'])
        gate.require(sha not in originals, 'RECOVERY_DUPLICATE_PAGE_REFUSED')
        raw = read_literal(sha)
        gate.require(isinstance(raw, bytes) and len(raw) == item['bytes']
                     and gate.digest(raw) == sha, 'RECOVERY_PAGE_ORIGINAL_CHANGED')
        total += len(raw)
        # Pages have extra braces versus the expanded dict. Bound aggregate reads
        # before parsing, independently of the final canonical expanded byte count.
        gate.require(total <= MAX_EXPANDED_BYTES + 3 * MAX_PAGES,
                     'RECOVERY_EXPANDED_BOUND_REQUIRED')
        page = _canonical(raw)
        gate.require(len(page) == item['files'], 'RECOVERY_PAGE_COUNT_CHANGED')
        keys = sorted(page)
        gate.require(not set(page) & set(inventory), 'RECOVERY_DUPLICATE_PATH_REFUSED')
        gate.require(previous is None or previous < keys[0], 'RECOVERY_PAGE_ORDER_CHANGED')
        previous = keys[-1]
        inventory.update(page); originals[sha] = raw
    expanded = gate.encoded(inventory)
    gate.require(len(inventory) == spec['files'] and len(expanded) == spec['bytes']
                 and len(expanded) <= MAX_EXPANDED_BYTES and gate.digest(expanded) == spec['sha256'],
                 'RECOVERY_EXPANDED_INVENTORY_CHANGED')
    baseline['non_ledger_files'] = inventory
    result['schema'] = INLINE
    return result, originals


def paginate(recovery, proposal):
    """Pure preparation: validate the complete original, return descriptor/pages.

    The caller preserves its original capture and stores returned pages as normal
    literals. This neither writes state nor grants approval to any returned bytes.
    """
    from orchestrator.install_reviewed_deployment import validate_recovery
    gate.require(recovery.get('schema') == INLINE, 'RECOVERY_INLINE_TERMINAL_REQUIRED')
    validate_recovery(recovery, proposal)
    result = deepcopy(recovery)
    inventory = result['terminal_admissions'].pop('non_ledger_files')
    expanded = gate.encoded(inventory)
    gate.require(len(expanded) <= MAX_EXPANDED_BYTES, 'RECOVERY_EXPANDED_BOUND_REQUIRED')
    pages = {}; items = []; current = {}; size = 5
    def flush():
        raw = gate.encoded(current); sha = gate.digest(raw)
        pages[sha] = raw
        items.append({'sha256':sha, 'bytes':len(raw), 'files':len(current)})
        gate.require(len(items) <= MAX_PAGES, 'RECOVERY_EXPANDED_BOUND_REQUIRED')
    for name, row in sorted(inventory.items()):
        one = len(gate.encoded({name:row})) - 5
        gate.require(one + 5 <= MAX_PAGE_BYTES, 'RECOVERY_SINGLE_ROW_BOUND_REQUIRED')
        extra = one + (2 if current else 0)
        if current and size + extra > MAX_PAGE_BYTES:
            flush(); current = {}; size = 5; extra = one
        current[name] = row; size += extra
    if current: flush()
    result['schema'] = PAGED
    result['terminal_admissions']['non_ledger_inventory'] = {
        'pages':items, 'files':len(inventory), 'bytes':len(expanded), 'sha256':gate.digest(expanded)}
    restored, _ = resolve(result, pages.__getitem__)
    gate.require(restored == recovery, 'RECOVERY_PAGING_ROUNDTRIP_CHANGED')
    return result, pages
