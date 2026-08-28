"""Per-idea experiment registry (2a-2, reworked per round-5 review 2a-4).

Structure declarative, status DERIVED. Round-5 P0 semantics now enforced:
  * A declared artifact dependency is BINDING: consumer with no result and a
    missing/unready input is BLOCKED; consumer holding a result whose input
    is missing or hash-drifted is STALE. Missing can never coexist with
    COMPLETE (review counterexample A2).
  * A pinned contract_hash mismatch is STALE unconditionally -- the node
    declaration no longer describes the approved experiment, run or not.
  * Launcher plumbing is not a second dependency system: a node declares
        launcher: {upstream_bundle: {from_probe: <id>, cli_flag: --x}}
    and the validator requires from_probe to be one of the node's all_of
    predecessors (graph says WHY; launcher says HOW the bundle is passed).
    The retired top-level requires_upstream_bundle key is rejected.
  * results_bundle values must be unique across nodes (T7).
  * terminal_statuses remain declarable here but confer completion authority
    only when HUMAN_APPROVED_PROBE binds this registry's file hash
    (registry_sha256: <64hex>); otherwise the transitional contract literals
    keep authority (A3 interim -- long-term home is the approved result
    spec/contract).

Statuses, precedence high to low: STALE, COMPLETE, IN_PROGRESS, BLOCKED,
UNSTARTED.
"""

import hashlib
import json
import re
from pathlib import Path

_FORBIDDEN_NODE_KEYS = {'status', 'complete', 'state', 'requires_upstream_bundle'}
_ALLOWED_NODE_KEYS = {'id', 'phase', 'contract_hash', 'depends_on', 'produces',
                      'results_bundle', 'terminal_statuses', 'launcher'}
_ALLOWED_TOP_KEYS = {'schema_version', 'probes'}


def _contained_rel(p) -> bool:
    s = str(p).replace('\\', '/')
    return bool(s) and not s.startswith('/') and '..' not in s.split('/')


def _load(idea_no: str, root: Path):
    p = Path(root) / 'ideas' / idea_no / 'registry.yaml'
    if not p.exists():
        return None, p
    import yaml
    return yaml.safe_load(p.read_text()) or {}, p


def registry_sha(idea_no: str, root: Path):
    p = Path(root) / 'ideas' / idea_no / 'registry.yaml'
    return hashlib.sha256(p.read_bytes()).hexdigest() if p.exists() else None


def approved_registry_sha(idea_no: str, root: Path):
    m = Path(root) / 'ideas' / idea_no / 'HUMAN_APPROVED_PROBE'
    if not m.exists():
        return None
    g = re.search(r'registry_sha256:\s*([0-9a-f]{64})', m.read_text())
    return g.group(1) if g else None


def validate(idea_no: str, root: Path) -> list[str]:
    try:
        return _validate(idea_no, root)
    except Exception as e:  # a validator returns findings, never tracebacks
        return [f'registry unvalidatable (malformed structure): {e}']


def _validate(idea_no: str, root: Path) -> list[str]:
    reg, p = _load(idea_no, root)
    if reg is None:
        return [f'{p} missing']
    errs = []
    if not isinstance(reg, dict):
        return [f'{p}: registry must be a mapping']
    unknown_top = set(reg) - _ALLOWED_TOP_KEYS
    if unknown_top:
        errs.append(f'unknown top-level keys {sorted(unknown_top)} '
                    '(schema is closed: a typo here silently changes meaning)')
    probes = reg.get('probes')
    if not isinstance(probes, list) or not probes:
        return [f'{p}: top-level `probes:` list is required']
    dicts = [n for n in probes if isinstance(n, dict)]
    ids = [n.get('id') for n in dicts]
    if len(dicts) != len(probes) or any(not i for i in ids):
        errs.append('every probe node needs a non-empty id')
    if len(set(ids)) != len(ids):
        errs.append('probe ids must be unique')
    known = set(ids)
    produces = {n.get('id'): set(n.get('produces') or []) for n in dicts}
    bundles = [str(n.get('results_bundle')) for n in dicts if n.get('results_bundle')]
    if len(set(bundles)) != len(bundles):
        errs.append('results_bundle values must be unique per node (T7)')
    for n in probes:
        if not isinstance(n, dict):
            errs.append(f'probe entry {n!r} must be a mapping')
            continue
        nid = n.get('id')
        unknown = set(n) - _ALLOWED_NODE_KEYS - _FORBIDDEN_NODE_KEYS
        if unknown:
            errs.append(f'{nid}: unknown keys {sorted(unknown)} '
                        '(closed schema; a typo like dependz_on would '
                        'silently drop a dependency)')
        rb = n.get('results_bundle')
        if rb is not None and not _contained_rel(rb):
            errs.append(f'{nid}: results_bundle {rb!r} must be a contained '
                        'repo-relative path (no absolute, no ..)')
        dep_raw = n.get('depends_on')
        if dep_raw is not None and not isinstance(dep_raw, dict):
            errs.append(f'{nid}: depends_on must be a mapping')
        lch = n.get('launcher')
        if lch is not None and not isinstance(lch, dict):
            errs.append(f'{nid}: launcher must be a mapping')
        bad = _FORBIDDEN_NODE_KEYS & set(n)
        if bad:
            errs.append(f'{nid}: forbidden keys {sorted(bad)} -- status is '
                        'derived, and requires_upstream_bundle is retired '
                        '(declare launcher.upstream_bundle bound to an '
                        'all_of edge)')
        ts = n.get('terminal_statuses')
        if ts is not None and (not isinstance(ts, list)
                               or not all(isinstance(x, str) for x in ts)):
            errs.append(f'{nid}: terminal_statuses must be a list of strings')
        dep = n.get('depends_on') if isinstance(n.get('depends_on'), dict) else {}
        _ao = dep.get('all_of') if isinstance(dep.get('all_of'), list) else []
        _ao = [d for d in _ao if isinstance(d, dict)]
        _ar = dep.get('artifacts') if isinstance(dep.get('artifacts'), list) else []
        _ar = [a for a in _ar if isinstance(a, dict)]
        allof = {d.get('probe') for d in _ao}
        for d in _ao:
            if d.get('probe') not in known:
                errs.append(f'{nid}: all_of references unknown probe '
                            f'{d.get("probe")!r}')
        for a in _ar:
            src = a.get('probe')
            if src not in known:
                errs.append(f'{nid}: artifact dep references unknown probe '
                            f'{src!r}')
            elif a.get('output') not in produces.get(src, set()):
                errs.append(f'{nid}: artifact {a.get("output")!r} is not '
                            f'declared in produces of {src!r}')
        lub = (n.get('launcher') if isinstance(n.get('launcher'), dict) else {}).get('upstream_bundle')
        if lub and not isinstance(lub, dict):
            errs.append(f'{nid}: launcher.upstream_bundle must be a mapping')
            lub = None
        if lub:
            fp = lub.get('probe') or lub.get('from_probe')
            if fp not in known:
                errs.append(f'{nid}: launcher.upstream_bundle names unknown '
                            f'probe {fp!r}')
            elif fp not in allof:
                errs.append(f'{nid}: launcher.upstream_bundle.from_probe '
                            f'{fp!r} must also be an all_of dependency -- '
                            'the graph owns WHY, the launcher only owns HOW')
    dicts2 = [n for n in probes if isinstance(n, dict) and n.get('id')]
    edges = {n['id']: set() for n in dicts2}
    for n in dicts2:
        dep = n.get('depends_on') if isinstance(n.get('depends_on'), dict) else {}
        ao = dep.get('all_of') if isinstance(dep.get('all_of'), list) else []
        ar = dep.get('artifacts') if isinstance(dep.get('artifacts'), list) else []
        for d in ao:
            if isinstance(d, dict) and d.get('probe') in edges:
                edges[n['id']].add(d['probe'])
        for a in ar:
            if isinstance(a, dict) and a.get('probe') in edges:
                edges[n['id']].add(a['probe'])
        lch = n.get('launcher') if isinstance(n.get('launcher'), dict) else {}
        lub = lch.get('upstream_bundle') if isinstance(lch.get('upstream_bundle'), dict) else {}
        fp = lub.get('probe') or lub.get('from_probe')
        if fp in edges:
            edges[n['id']].add(fp)
    WHITE, GRAY, BLACK = 0, 1, 2
    color = {k: WHITE for k in edges}

    def dfs(u):
        color[u] = GRAY
        for v in edges[u]:
            if color[v] == GRAY:
                return True
            if color[v] == WHITE and dfs(v):
                return True
        color[u] = BLACK
        return False

    if any(color[k] == WHITE and dfs(k) for k in edges):
        errs.append('dependency graph contains a cycle')
    return errs


def _bundle_summary(root: Path, rel):
    if not rel:
        return None
    p = Path(root) / rel / 'summary.json'
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text())
    except (json.JSONDecodeError, OSError):
        return {'status': 'UNPARSEABLE'}


def derive_status(idea_no: str, root: Path, contract_hasher, bundle_validator=None) -> dict:
    reg, _ = _load(idea_no, root)
    if reg is None:
        return {}
    root = Path(root)
    idea_dir = root / 'ideas' / idea_no
    current_blob = contract_hasher(idea_dir)
    nodes = {n['id']: n for n in reg.get('probes') or [] if n.get('id')}
    out: dict = {}

    def artifact_issues(n):
        missing, drifted = [], []
        for a in (n.get('depends_on') or {}).get('artifacts') or []:
            src = nodes.get(a.get('probe')) or {}
            f = root / (src.get('results_bundle') or '') / a.get('output', '')
            if not f.exists():
                missing.append(f'{a.get("probe")}/{a.get("output")}')
                continue
            want = a.get('sha256')
            if want:
                h = hashlib.sha256(f.read_bytes()).hexdigest()
                if h != want:
                    drifted.append(f'{a.get("output")} sha {h[:12]} != '
                                   f'declared {want[:12]}')
        return missing, drifted

    def status_of(nid, seen=()):
        if nid in out:
            return out[nid]['status']
        n = nodes[nid]
        pin = n.get('contract_hash')
        if pin and pin != current_blob:  # a missing current contract is a mismatch too
            out[nid] = {'status': 'STALE',
                        'reason': f'pinned contract {pin[:12]} != current '
                                  f'{(current_blob or "MISSING")[:12]} '
                                  '(declaration no longer describes the '
                                  'approved experiment)'}
            return 'STALE'
        summary = _bundle_summary(root, n.get('results_bundle'))
        missing, drifted = artifact_issues(n)
        if summary and (missing or drifted):
            why = ('consumed input missing: ' + ', '.join(missing)) if missing \
                else ('consumed ' + '; '.join(drifted))
            out[nid] = {'status': 'STALE', 'reason': why}
            return 'STALE'
        terminal = n.get('terminal_statuses') or []
        if summary and summary.get('status') in terminal:
            if bundle_validator is not None:
                fails = bundle_validator(root / (n.get('results_bundle') or ''))
                if fails:
                    out[nid] = {'status': 'RESULT_PRESENT',
                                'reason': 'terminal-looking summary but the '
                                          'bundle does not validate: '
                                          + '; '.join(map(str, fails))[:200]}
                    return 'RESULT_PRESENT'
            out[nid] = {'status': 'COMPLETE',
                        'reason': f'summary status {summary.get("status")!r}'}
            return 'COMPLETE'
        if not summary and (missing or drifted):
            why = ('waiting on missing artifact ' + ', '.join(missing)) if missing \
                else ('declared input drifted: ' + '; '.join(drifted))
            out[nid] = {'status': 'BLOCKED', 'reason': why}
            return 'BLOCKED'
        for d in (n.get('depends_on') or {}).get('all_of') or []:
            dep = d.get('probe')
            if dep in seen:
                continue
            if status_of(dep, seen + (nid,)) != 'COMPLETE':
                out[nid] = {'status': 'BLOCKED', 'reason': f'waiting on {dep}'}
                return 'BLOCKED'
        if summary:
            out[nid] = {'status': 'IN_PROGRESS',
                        'reason': f'summary status {summary.get("status")!r} '
                                  'not terminal'}
            return 'IN_PROGRESS'
        out[nid] = {'status': 'UNSTARTED', 'reason': 'no bundle yet'}
        return 'UNSTARTED'

    for nid in nodes:
        status_of(nid)
    return out


def terminal_statuses_if_approved(idea_no: str, root: Path, bundle):
    """Registry terminals confer completion authority ONLY when the human
    approval binds this registry's exact bytes (A3 interim)."""
    reg, p = _load(idea_no, root)
    if reg is None:
        return None
    if approved_registry_sha(idea_no, root) != registry_sha(idea_no, root):
        return None
    b = str(bundle).replace('\\', '/').rstrip('/')
    for n in reg.get('probes') or []:
        rb = str(n.get('results_bundle') or '').rstrip('/')
        if rb and b.endswith(rb):
            return n.get('terminal_statuses') or None
    return None


def upstream_bundle_requirement(idea_no: str, root: Path, phase):
    reg, _ = _load(idea_no, root)
    if reg is None:
        return None
    for n in reg.get('probes') or []:
        if str(n.get('phase', '')).upper() == str(phase).upper():
            lub = (n.get('launcher') or {}).get('upstream_bundle')
            if lub:
                return {'probe': lub.get('probe') or lub.get('from_probe'),
                        'cli_flag': lub.get('cli_flag')}
            return None
    return None


def state_summary(idea_no: str, root: Path, contract_hasher, bundle_validator=None):
    reg, p = _load(idea_no, root)
    if reg is None:
        return None
    return {
        'file_sha256': registry_sha(idea_no, root),
        'approval_bound': approved_registry_sha(idea_no, root) == registry_sha(idea_no, root),
        'nodes': {k: v['status']
                  for k, v in sorted(derive_status(
                      idea_no, root, contract_hasher,
                      bundle_validator).items())},
    }
