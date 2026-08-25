"""Per-idea experiment registry (Patch 2a, part 2).

ideas/NNN/registry.yaml declares the idea's experiment GRAPH: which probes
exist, how they depend on one another, and what artifacts bind each one.
Structure is DECLARATIVE; node status is DERIVED -- a registry that carries
a hand-written `status:` key is rejected outright, because editable status
would recreate the dual-authority bug class 2a exists to kill (round-4
audit: "graph structure declarative, node status derived").

Node schema (all keys optional unless marked):
  probes:                                  # required, list of nodes
    - id: synthetic-calibration            # required, unique
      phase: S                             # launcher phase this node runs as
      results_bundle: probes/023/results_v2  # where its bundle lands
      terminal_statuses: [PHASE_S_COMPLETE_REQUIRES_AMENDMENT]
      produces: [simulation_operating_characteristics.csv]
      contract_hash: <40-hex>              # pin; mismatch => STALE
      depends_on:
        all_of: [{probe: <id>}]            # every listed probe COMPLETE
        artifacts: [{probe: <id>, output: <name>, sha256: <64-hex>}]
      requires_upstream_bundle:            # launcher dependency declaration
        probe: <id>
        cli_flag: --phase-s-dir

Derived statuses, precedence high to low:
  STALE        pinned contract or consumed-artifact hash no longer matches
  COMPLETE     bundle summary status is one of terminal_statuses
  IN_PROGRESS  bundle exists but status is not terminal
  BLOCKED      an all_of dependency is not COMPLETE
  UNSTARTED    nothing yet

Sibling independence is emergent: only declared dependencies block, so a
failed branch never kills an independent one. Terminal statuses declared
here supersede the transitional POSITIVE/NEGATIVE_PATTERN literals in
bundle_complete, and requires_upstream_bundle supersedes the transitional
run.py string-sniff in package-colab -- both fallbacks stay until every
active idea carries a registry, then retire in 2c.
"""

import hashlib
import json
from pathlib import Path

_FORBIDDEN_NODE_KEYS = {'status', 'complete', 'state'}


def _load(idea_no: str, root: Path):
    p = Path(root) / 'ideas' / idea_no / 'registry.yaml'
    if not p.exists():
        return None, p
    import yaml
    return yaml.safe_load(p.read_text()) or {}, p


def validate(idea_no: str, root: Path) -> list[str]:
    reg, p = _load(idea_no, root)
    if reg is None:
        return [f'{p} missing']
    errs = []
    probes = reg.get('probes')
    if not isinstance(probes, list) or not probes:
        return [f'{p}: top-level `probes:` list is required']
    ids = [n.get('id') for n in probes]
    if any(not i for i in ids):
        errs.append('every probe node needs a non-empty id')
    if len(set(ids)) != len(ids):
        errs.append('probe ids must be unique')
    known = set(ids)
    produces = {n.get('id'): set(n.get('produces') or []) for n in probes}
    for n in probes:
        nid = n.get('id')
        bad = _FORBIDDEN_NODE_KEYS & set(n)
        if bad:
            errs.append(f'{nid}: hand-set {sorted(bad)} forbidden -- '
                        'status is derived, never declared')
        ts = n.get('terminal_statuses')
        if ts is not None and (not isinstance(ts, list)
                               or not all(isinstance(x, str) for x in ts)):
            errs.append(f'{nid}: terminal_statuses must be a list of strings')
        dep = n.get('depends_on') or {}
        for d in dep.get('all_of') or []:
            if d.get('probe') not in known:
                errs.append(f'{nid}: all_of references unknown probe '
                            f'{d.get("probe")!r}')
        for a in dep.get('artifacts') or []:
            src = a.get('probe')
            if src not in known:
                errs.append(f'{nid}: artifact dep references unknown probe '
                            f'{src!r}')
            elif a.get('output') not in produces.get(src, set()):
                errs.append(f'{nid}: artifact {a.get("output")!r} is not '
                            f'declared in produces of {src!r}')
        rub = n.get('requires_upstream_bundle')
        if rub and rub.get('probe') not in known:
            errs.append(f'{nid}: requires_upstream_bundle references '
                        f'unknown probe {rub.get("probe")!r}')
    # acyclicity over all_of + artifact edges
    edges = {n['id']: set() for n in probes if n.get('id')}
    for n in probes:
        dep = n.get('depends_on') or {}
        for d in (dep.get('all_of') or []):
            if d.get('probe') in edges:
                edges[n['id']].add(d['probe'])
        for a in (dep.get('artifacts') or []):
            if a.get('probe') in edges:
                edges[n['id']].add(a['probe'])
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


def derive_status(idea_no: str, root: Path, contract_hasher) -> dict:
    """Node id -> {'status', 'reason'}; authority is on-disk evidence."""
    reg, _ = _load(idea_no, root)
    if reg is None:
        return {}
    root = Path(root)
    idea_dir = root / 'ideas' / idea_no
    current_blob = contract_hasher(idea_dir)
    nodes = {n['id']: n for n in reg.get('probes') or [] if n.get('id')}
    out: dict = {}

    def status_of(nid, seen=()):
        if nid in out:
            return out[nid]['status']
        n = nodes[nid]
        summary = _bundle_summary(root, n.get('results_bundle'))
        terminal = n.get('terminal_statuses') or []
        complete = bool(summary) and summary.get('status') in terminal
        stale_why = None
        pin = n.get('contract_hash')
        if pin and current_blob and pin != current_blob:
            stale_why = f'pinned contract {pin[:12]} != current {current_blob[:12]}'
        for a in (n.get('depends_on') or {}).get('artifacts') or []:
            want = a.get('sha256')
            if not want:
                continue
            src = nodes.get(a.get('probe')) or {}
            f = root / (src.get('results_bundle') or '') / a.get('output', '')
            if f.exists():
                h = hashlib.sha256(f.read_bytes()).hexdigest()
                if h != want:
                    stale_why = (f'consumed {a.get("output")} sha {h[:12]} '
                                 f'!= declared {want[:12]}')
        if stale_why and (complete or summary):
            out[nid] = {'status': 'STALE', 'reason': stale_why}
            return 'STALE'
        if complete:
            out[nid] = {'status': 'COMPLETE',
                        'reason': f'summary status {summary.get("status")!r}'}
            return 'COMPLETE'
        for d in (n.get('depends_on') or {}).get('all_of') or []:
            dep = d.get('probe')
            if dep in seen:
                continue
            if status_of(dep, seen + (nid,)) != 'COMPLETE':
                out[nid] = {'status': 'BLOCKED',
                            'reason': f'waiting on {dep}'}
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


def terminal_statuses_for_bundle(idea_no: str, root: Path, bundle) -> list | None:
    """Registry-declared terminal statuses for the node whose
    results_bundle matches this bundle path (suffix match, so CI's
    results-data/... prefix is fine). None when no registry/node claims it."""
    reg, _ = _load(idea_no, root)
    if reg is None:
        return None
    b = str(bundle).replace('\\', '/').rstrip('/')
    for n in reg.get('probes') or []:
        rb = str(n.get('results_bundle') or '').rstrip('/')
        if rb and b.endswith(rb):
            return n.get('terminal_statuses') or None
    return None


def upstream_bundle_requirement(idea_no: str, root: Path, phase) -> dict | None:
    """The launcher dependency the registry declares for this phase:
    {'probe': <id>, 'cli_flag': '--phase-s-dir'} or None. Supersedes the
    transitional run.py string-sniff."""
    reg, _ = _load(idea_no, root)
    if reg is None:
        return None
    for n in reg.get('probes') or []:
        if str(n.get('phase', '')).upper() == str(phase).upper():
            return n.get('requires_upstream_bundle') or None
    return None


def state_summary(idea_no: str, root: Path, contract_hasher) -> dict | None:
    """Deterministic registry block for state.json: file hash + derived
    node statuses. None when the idea has no registry."""
    reg, p = _load(idea_no, root)
    if reg is None:
        return None
    return {
        'file_sha256': hashlib.sha256(p.read_bytes()).hexdigest(),
        'nodes': {k: v['status']
                  for k, v in sorted(derive_status(
                      idea_no, root, contract_hasher).items())},
    }
