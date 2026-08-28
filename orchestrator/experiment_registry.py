"""Per-idea experiment registry (2a-2, reworked per round-5 review 2a-4).

Structure declarative, status DERIVED. Round-5 P0 semantics now enforced:
  * A declared artifact dependency is BINDING: consumer with no result and a
    missing/unready input is BLOCKED; consumer holding a result whose input
    is missing or hash-drifted is STALE. Missing can never coexist with
    COMPLETE (review counterexample A2).
  * contract_hash names the immutable approved contract version GOVERNING
    the node (R1, round-6 review). A node without terminal evidence must
    track the current contract: pin mismatch is STALE. A node holding a
    terminal result is judged against its own pin -- the pin must be
    attested (HUMAN_APPROVED_PROBE or a REGISTRY_RATIFIED governance
    event), the bundle's provenance.contract_blob must equal it, and the
    bundle must validate under that immutable contract. History does not
    go stale because a downstream amendment moved the current contract.
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
import posixpath
import re
from pathlib import Path

_FORBIDDEN_NODE_KEYS = {'status', 'complete', 'state', 'requires_upstream_bundle'}
_ALLOWED_NODE_KEYS = {'id', 'phase', 'contract_hash', 'depends_on', 'produces',
                      'results_bundle', 'terminal_statuses', 'launcher'}
_ALLOWED_TOP_KEYS = {'schema_version', 'probes'}


def _contained_rel(p) -> bool:
    s = str(p).replace('\\', '/')
    return bool(s) and not s.startswith('/') and '..' not in s.split('/')


_HEX40 = re.compile(r'^[0-9a-f]{40}$')
_HEX64 = re.compile(r'^[0-9a-f]{64}$')


def _canonical_rel(p) -> bool:
    """Contained AND already canonical (no backslashes, '.', '//', or a
    trailing '/') so path uniqueness cannot be dodged by spelling (R1)."""
    s = str(p)
    if '\\' in s or not _contained_rel(s):
        return False
    return s == posixpath.normpath(s)


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


_GOVERNANCE_FILE = 'governance_events.jsonl'
_RATIFY_KEYS = {'event', 'idea', 'registry_sha256', 'approvals',
                'contract_hashes', 'operator', 'git_commit', 'event_id'}


def _governance_lines(idea_dir: Path):
    p = idea_dir / _GOVERNANCE_FILE
    if not p.exists():
        return []
    return [(i, ln) for i, ln in
            enumerate(p.read_text().splitlines(), 1) if ln.strip()]


def _validate_governance(idea_no: str, idea_dir: Path) -> list[str]:
    """The governance-events sidecar is append-only jsonl; v1 recognizes
    REGISTRY_RATIFIED only and the row schema is closed (R1)."""
    errs, seen = [], set()
    for i, line in _governance_lines(idea_dir):
        try:
            obj = json.loads(line)
        except json.JSONDecodeError as e:
            errs.append(f'{_GOVERNANCE_FILE}:{i}: unparseable json ({e})')
            continue
        if not isinstance(obj, dict) or not isinstance(obj.get('event'), str):
            errs.append(f'{_GOVERNANCE_FILE}:{i}: every event is a mapping '
                        'with a string `event`')
            continue
        if obj['event'] != 'REGISTRY_RATIFIED':
            errs.append(f'{_GOVERNANCE_FILE}:{i}: unknown governance event '
                        f'{obj["event"]!r} (v1 recognizes REGISTRY_RATIFIED '
                        'only; the schema is closed)')
            continue
        unknown = set(obj) - _RATIFY_KEYS
        if unknown:
            errs.append(f'{_GOVERNANCE_FILE}:{i}: unknown keys '
                        f'{sorted(unknown)} (closed schema)')
        miss = _RATIFY_KEYS - set(obj)
        if miss:
            errs.append(f'{_GOVERNANCE_FILE}:{i}: missing keys {sorted(miss)}')
            continue
        if obj['idea'] != int(idea_no):
            errs.append(f'{_GOVERNANCE_FILE}:{i}: idea {obj["idea"]!r} '
                        f'!= {int(idea_no)}')
        if not (isinstance(obj['registry_sha256'], str)
                and _HEX64.match(obj['registry_sha256'])):
            errs.append(f'{_GOVERNANCE_FILE}:{i}: registry_sha256 must be '
                        '64-hex')
        ap = obj['approvals']
        if not (isinstance(ap, list) and ap
                and all(isinstance(a, str) and _HEX64.match(a) for a in ap)):
            errs.append(f'{_GOVERNANCE_FILE}:{i}: approvals must be a '
                        'non-empty list of 64-hex artifact shas')
        ch = obj['contract_hashes']
        if not (isinstance(ch, list) and ch
                and all(isinstance(c, str) and _HEX40.match(c) for c in ch)):
            errs.append(f'{_GOVERNANCE_FILE}:{i}: contract_hashes must be a '
                        'non-empty list of 40-hex git blob shas')
        for k in ('operator', 'git_commit', 'event_id'):
            if not (isinstance(obj[k], str) and obj[k].strip()):
                errs.append(f'{_GOVERNANCE_FILE}:{i}: {k} must be a '
                            'non-empty string')
        eid = obj.get('event_id')
        if isinstance(eid, str):
            if eid in seen:
                errs.append(f'{_GOVERNANCE_FILE}:{i}: duplicate event_id '
                            f'{eid!r}')
            seen.add(eid)
    return errs


def _attested_hashes(idea_dir: Path) -> set:
    """Contract blobs attested by the human approval marker or by
    well-formed REGISTRY_RATIFIED events. Judging terminal evidence
    against a pinned contract requires membership here (R1)."""
    out = set()
    m = idea_dir / 'HUMAN_APPROVED_PROBE'
    if m.exists():
        out.update(re.findall(r'contract_blob:\s*([0-9a-f]{40})',
                              m.read_text()))
    for _i, line in _governance_lines(idea_dir):
        try:
            obj = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(obj, dict) and obj.get('event') == 'REGISTRY_RATIFIED':
            out.update(c for c in (obj.get('contract_hashes') or [])
                       if isinstance(c, str) and _HEX40.match(c))
    return out


def _bundle_provenance_blob(root: Path, rel):
    if not rel:
        return None
    p = Path(root) / rel / 'provenance.json'
    if not p.exists():
        return None
    try:
        return (json.loads(p.read_text()) or {}).get('contract_blob')
    except (json.JSONDecodeError, OSError):
        return None


def result_input_hashes(idea_no: str, root: Path):
    """Deterministic hashes of the result-status INPUTS from which this
    registry's node statuses are derived (R2, round-6): per node, the
    summary/provenance bytes and every declared consumed-artifact file.
    state_view folds this into materialization.sources so the source
    fingerprint MOVES whenever a derivable status can move -- a watermark
    that stays constant while its derivations change is misleading.
    Raw-read and total: works on any registry shape (an invalid registry
    still fails materialization at the resolver); non-contained paths
    hash as None rather than reaching outside the repo. None = no
    registry file."""
    reg, _p = _load(idea_no, root)
    if reg is None:
        return None
    root = Path(root)

    def _fsha(rel):
        if not (isinstance(rel, str) and rel and _contained_rel(rel)):
            return None
        f = root / rel
        return hashlib.sha256(f.read_bytes()).hexdigest() if f.exists() \
            else None

    probes = [n for n in (reg.get('probes') or [])
              if isinstance(n, dict) and n.get('id')]
    bundles = {str(n['id']): n.get('results_bundle') for n in probes}
    out = {}
    for n in probes:
        rb = n.get('results_bundle')
        ent = {
            'summary_sha256': _fsha(f'{rb}/summary.json') if rb else None,
            'provenance_sha256': _fsha(f'{rb}/provenance.json') if rb else None,
        }
        dep = n.get('depends_on') if isinstance(n.get('depends_on'), dict) \
            else {}
        arts = {}
        for a in dep.get('artifacts') or []:
            if not isinstance(a, dict):
                continue
            srb = bundles.get(a.get('probe'))
            outp = a.get('output')
            key = f'{a.get("probe")}/{outp}'
            arts[key] = _fsha(f'{srb}/{outp}') \
                if isinstance(srb, str) and isinstance(outp, str) else None
        if arts:
            ent['artifacts'] = dict(sorted(arts.items()))
        out[str(n['id'])] = ent
    return dict(sorted(out.items()))


def validate(idea_no: str, root: Path) -> list[str]:
    try:
        return _validate(idea_no, root)
    except Exception as e:  # a validator returns findings, never tracebacks
        return [f'registry unvalidatable (malformed structure): {e}']


def _validate(idea_no: str, root: Path) -> list[str]:
    reg, p = _load(idea_no, root)
    if reg is None:
        return [f'{p} missing']
    if not isinstance(reg, dict):
        return [f'{p}: registry must be a mapping']
    errs = _validate_governance(idea_no, Path(root) / 'ideas' / idea_no)
    unknown_top = set(reg) - _ALLOWED_TOP_KEYS
    if unknown_top:
        errs.append(f'unknown top-level keys {sorted(unknown_top)} '
                    '(schema is closed: a typo here silently changes meaning)')
    if reg.get('schema_version') != 1:
        errs.append(f'schema_version must be exactly 1 '
                    f'(got {reg.get("schema_version")!r}); the registry '
                    'schema is versioned and closed')
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
        ch = n.get('contract_hash')
        if ch is not None and not (isinstance(ch, str) and _HEX40.match(ch)):
            errs.append(f'{nid}: contract_hash {ch!r} must be a 40-hex git '
                        'blob sha (the immutable approved contract version '
                        'governing this node)')
        pr = n.get('produces')
        if pr is not None:
            if not (isinstance(pr, list)
                    and all(isinstance(x, str) for x in pr)):
                errs.append(f'{nid}: produces must be a list of strings')
            else:
                for x in pr:
                    if not _canonical_rel(x):
                        errs.append(f'{nid}: produces entry {x!r} must be a '
                                    'canonical contained bundle-relative '
                                    'path (no absolute, no .., no ./ or //)')
        rb = n.get('results_bundle')
        if rb is not None and not (isinstance(rb, str) and _canonical_rel(rb)):
            errs.append(f'{nid}: results_bundle {rb!r} must be a canonical '
                        'contained repo-relative path (no absolute, no .., '
                        'no ./ or //)')
        dep_raw = n.get('depends_on')
        if dep_raw is not None and not isinstance(dep_raw, dict):
            errs.append(f'{nid}: depends_on must be a mapping')
        elif isinstance(dep_raw, dict):
            unk = set(dep_raw) - {'all_of', 'artifacts'}
            if unk:
                errs.append(f'{nid}: depends_on unknown keys {sorted(unk)} '
                            '(closed schema: all_of, artifacts)')
            for fld in ('all_of', 'artifacts'):
                v = dep_raw.get(fld)
                if v is not None and not isinstance(v, list):
                    errs.append(f'{nid}: depends_on.{fld} must be a list')
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
                               or not all(isinstance(x, str) and x.strip()
                                          for x in ts)):
            errs.append(f'{nid}: terminal_statuses must be a list of '
                        'non-empty strings')
        dep = n.get('depends_on') if isinstance(n.get('depends_on'), dict) else {}
        _ao = dep.get('all_of') if isinstance(dep.get('all_of'), list) else []
        _ao = [d for d in _ao if isinstance(d, dict)]
        _ar = dep.get('artifacts') if isinstance(dep.get('artifacts'), list) else []
        _ar = [a for a in _ar if isinstance(a, dict)]
        allof = {d.get('probe') for d in _ao}
        for d in _ao:
            unk = set(d) - {'probe'}
            if unk:
                errs.append(f'{nid}: all_of entry unknown keys '
                            f'{sorted(unk)} (closed schema: probe)')
            if not (isinstance(d.get('probe'), str) and d.get('probe')):
                errs.append(f'{nid}: all_of entry needs a non-empty '
                            'string probe')
            elif d.get('probe') not in known:
                errs.append(f'{nid}: all_of references unknown probe '
                            f'{d.get("probe")!r}')
        for a in _ar:
            unk = set(a) - {'probe', 'output', 'sha256'}
            if unk:
                errs.append(f'{nid}: artifact entry unknown keys '
                            f'{sorted(unk)} (closed schema: probe, output, '
                            'sha256)')
            out_p = a.get('output')
            if not (isinstance(out_p, str) and _canonical_rel(out_p)):
                errs.append(f'{nid}: artifact output {out_p!r} must be a '
                            'canonical contained bundle-relative path')
            sha = a.get('sha256')
            if not (isinstance(sha, str) and _HEX64.match(sha)):
                errs.append(f'{nid}: artifact dep on {out_p!r} requires a '
                            '64-hex sha256 (artifact dependencies are '
                            'BINDING; an unhashed dependency is not a '
                            'dependency)')
            src = a.get('probe')
            if src not in known:
                errs.append(f'{nid}: artifact dep references unknown probe '
                            f'{src!r}')
            elif isinstance(out_p, str) \
                    and out_p not in produces.get(src, set()):
                errs.append(f'{nid}: artifact {out_p!r} is not '
                            f'declared in produces of {src!r}')
        lmap = n.get('launcher') if isinstance(n.get('launcher'), dict) else {}
        lunk = set(lmap) - {'upstream_bundle'}
        if lunk:
            errs.append(f'{nid}: launcher unknown keys {sorted(lunk)} '
                        '(closed schema: upstream_bundle)')
        lub = lmap.get('upstream_bundle')
        if lub and not isinstance(lub, dict):
            errs.append(f'{nid}: launcher.upstream_bundle must be a mapping')
            lub = None
        if lub:
            uunk = set(lub) - {'from_probe', 'cli_flag'}
            if uunk:
                errs.append(f'{nid}: upstream_bundle unknown keys '
                            f'{sorted(uunk)} (closed schema: from_probe, '
                            'cli_flag; the legacy probe key is retired)')
            cf = lub.get('cli_flag')
            if not (isinstance(cf, str) and cf.strip()):
                errs.append(f'{nid}: upstream_bundle.cli_flag must be a '
                            'non-empty string')
            fp = lub.get('from_probe')
            if not (isinstance(fp, str) and fp):
                errs.append(f'{nid}: upstream_bundle.from_probe must be a '
                            'non-empty string')
            elif fp not in known:
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
    """bundle_validator, when supplied, is called as
    bundle_validator(bundle_path, governing_blob) so historical nodes are
    validated against their own immutable contract (R1). COMPLETE is
    unreachable without a validator: validation is part of the meaning."""
    reg, _ = _load(idea_no, root)
    if reg is None:
        return {}
    verrs = validate(idea_no, root)
    if verrs:
        raise ValueError('registry invalid (validation precedes status '
                         'derivation): ' + ' | '.join(verrs[:4]))
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
        rb = n.get('results_bundle')
        summary = _bundle_summary(root, rb)
        is_terminal = bool(summary) and \
            summary.get('status') in (n.get('terminal_statuses') or [])
        if pin and pin != current_blob and not is_terminal:
            # a missing current contract is a mismatch too
            out[nid] = {'status': 'STALE',
                        'reason': f'pinned contract {pin[:12]} != current '
                                  f'{(current_blob or "MISSING")[:12]} '
                                  'and no terminal evidence -- a live node '
                                  'must track the approved current contract'}
            return 'STALE'
        missing, drifted = artifact_issues(n)
        if summary and (missing or drifted):
            why = ('consumed input missing: ' + ', '.join(missing)) if missing \
                else ('consumed ' + '; '.join(drifted))
            out[nid] = {'status': 'STALE', 'reason': why}
            return 'STALE'
        if is_terminal:
            governing = pin or current_blob
            if not governing:
                out[nid] = {'status': 'STALE',
                            'reason': 'terminal result with no governing '
                                      'contract identity (no pin, no '
                                      'current contract)'}
                return 'STALE'
            if pin and pin not in _attested_hashes(idea_dir):
                out[nid] = {'status': 'STALE',
                            'reason': f'pinned contract {pin[:12]} lacks '
                                      'approval/ratification attestation '
                                      '(HUMAN_APPROVED_PROBE or a '
                                      'REGISTRY_RATIFIED event)'}
                return 'STALE'
            prov = _bundle_provenance_blob(root, rb)
            if prov != governing:
                out[nid] = {'status': 'STALE',
                            'reason': f'bundle provenance contract '
                                      f'{str(prov)[:12]} != governing '
                                      f'{governing[:12]} -- the bundle does '
                                      'not prove execution under this '
                                      "node's contract"}
                return 'STALE'
            if bundle_validator is None:
                out[nid] = {'status': 'RESULT_PRESENT',
                            'reason': 'terminal summary present but '
                                      'unvalidated (no bundle validator '
                                      'supplied; COMPLETE requires '
                                      'validation)'}
                return 'RESULT_PRESENT'
            fails = bundle_validator(root / (rb or ''), governing)
            if fails:
                out[nid] = {'status': 'RESULT_PRESENT',
                            'reason': 'terminal-looking summary but the '
                                      'bundle does not validate: '
                                      + '; '.join(map(str, fails))[:200]}
                return 'RESULT_PRESENT'
            out[nid] = {'status': 'COMPLETE',
                        'reason': f'summary status {summary.get("status")!r} '
                                  f'validated under {governing[:12]}'}
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
    if validate(idea_no, root):
        return None  # an invalid registry confers no completion authority
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
    if validate(idea_no, root):
        return None  # invalid registries provide no launcher plumbing
    for n in reg.get('probes') or []:
        if str(n.get('phase', '')).upper() == str(phase).upper():
            lub = (n.get('launcher') or {}).get('upstream_bundle')
            if lub:
                return {'probe': lub.get('from_probe'),
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
