#!/usr/bin/env python3
"""Lightweight orchestration for Concept Research Scout.

No expensive compute is launched automatically. Agent CLI commands are best-effort
because vendor flags change; every stage also writes a complete prompt file that
can be handed to an agent manually.

Revamp additions (see REVAMP.md):
  * `cycle` / `resume`: multi-track scouting (baseline | wide | fiction) with
    per-stage git-commit checkpoints, so a rate limit or timeout costs one
    stage, not the run.
  * Ledger: append-only ledger.jsonl + evidence/ledger_digest.md injected into
    scout prompts (orchestrator/ledger.py).
  * Rotation: [rotation] in AGENTS.toml swaps the two model families on odd
    cycles, so both play scout and critic across cycles.
  * Fiction track: blind, seed-constrained story generation -> mechanical
    extraction -> cross-model refinement with an honorable NO_TESTABLE_KERNEL
    exit.
"""
from __future__ import annotations
import argparse, csv, json, os, random, re, shutil, subprocess, sys, textwrap
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
STATE = ROOT/'orchestrator'/'state.json'
PROMPTS = ROOT/'orchestrator'/'prompts'
SEEDS = ROOT/'orchestrator'/'seeds.json'

sys.path.insert(0, str(ROOT/'orchestrator'))
import ledger as ledger_mod  # noqa: E402
ledger_mod.ROOT = ROOT
ledger_mod.LEDGER = ROOT/'ledger.jsonl'
ledger_mod.DIGEST = ROOT/'evidence'/'ledger_digest.md'


def load_state():
    if not STATE.exists():
        return {'next_scout': 1, 'selected_idea': None}
    return json.loads(STATE.read_text())


def save_state(s):
    STATE.parent.mkdir(parents=True, exist_ok=True)
    STATE.write_text(json.dumps(s, indent=2)+'\n')


def read_text(path):
    return Path(path).read_text() if Path(path).exists() else ''


def idea_dir(i):
    return ROOT/'ideas'/f'{int(i):03d}'


def scout_dir(i, charter=None):
    if charter:
        return ROOT/'ideas'/f'scout-{charter}-{int(i):03d}'
    return ROOT/'ideas'/f'scout-{int(i):03d}'


def _parse_scout_ref(ref):
    """CLI scout reference -> (charter|None, cycle_no).
    '13' / '013' -> (None, 13); 'isles24-001' -> ('isles24', 1)."""
    r = str(ref).strip()
    if r.isdigit():
        return None, int(r)
    parts = r.rsplit('-', 1)
    if len(parts) == 2 and parts[1].isdigit():
        return parts[0], int(parts[1])
    raise SystemExit(f'Bad scout reference {ref!r}: use a cycle number '
                     "(13) or charter-cycle ('isles24-001').")


def _fmt_scout(charter, no):
    return f'{charter}-{no:03d}' if charter else f'{no:03d}'


def charter_path(name):
    """Charter file for a named charter; the baseline lives at ROOT/CHARTER.md."""
    if not name:
        return ROOT/'CHARTER.md'
    p = ROOT/'charters'/name/'CHARTER.md'
    if not p.exists():
        raise SystemExit(f'Unknown charter {name!r}: {p.relative_to(ROOT)} does not exist. '
                         'Create it (a human-authored governance document) before cycling.')
    return p


def _active_charter():
    """Charter of the in-flight cycle, if any (reader-side default: baseline).
    OPERATIONAL use only (cycle-stage bookkeeping). Scientific logic must
    resolve charter from its explicit target: 2026-08-18 audit found every
    downstream prompt for ideas 020-025 carried the baseline charter because
    this function reflects whatever cycle ran last, not the idea at hand."""
    return (load_state().get('cycle') or {}).get('charter')


def _norm_charter(ch):
    """Canonical charter value: None/''/'baseline' are all the baseline."""
    return None if ch in (None, '', 'baseline') else ch


def charter_for_target(target):
    """Authoritative charter resolution for a stage target directory:
    1) an idea card's charter stamp -- and its ABSENCE is equally
       authoritative: a card with no charter IS a baseline idea (the
       2026-08-18 closeout review found legacy ideas falling through to
       whatever cycle was globally active, the mirror image of the
       original bug);
    2) a charter-prefixed scout dir name (prefix absence = baseline);
    3) only for targets that are neither: the active cycle's charter."""
    t = Path(target)
    card = t/'idea_card.json'
    if card.exists():
        try:
            data = json.loads(card.read_text())
        except json.JSONDecodeError as e:
            raise SystemExit(
                f'Cannot resolve charter: malformed {card}. A target whose '
                'identity cannot be established must never silently inherit '
                'the globally active charter (fail-closed, external review '
                '2026-08-18). Fix the card, then rerun.') from e
        return _norm_charter(data.get('charter'))
    if t.name.startswith('scout-'):
        try:
            return _norm_charter(_parse_scout_dir(t.name)[0])
        except (ValueError, SystemExit) as e:
            raise SystemExit(
                f'Cannot resolve charter: unparseable scout dir name '
                f'{t.name!r} (fail-closed).') from e
    # only targets with no persistent identity fall back to the cycle
    return _norm_charter(_active_charter())


# --------------------------------------------------------------------------
# Prompt building. Fiction-track early stages are BLIND: the writer must not
# see the charter, rules, rubric, or institutional memory, or it will start
# self-censoring toward plausibility -- exactly what the track exists to avoid.
# The refiner sees everything EXCEPT the story: it must judge the pitch, not
# the fiction it came from.
# --------------------------------------------------------------------------

BLIND_STAGES = {'fiction_scout', 'fiction_extract'}

# Stages that must form judgments before seeing anyone else's numbers.
# The ledger digest injects sibling ideas as 'score 4.6' lines into every
# prompt; a critiquer that reads those anchors on them (verdict herding).
# Redaction strips filled-in score NUMBERS only -- rubric instructions like
# 'Score each dimension 1-5' carry no number directly after the keyword and
# survive untouched.
SCORE_BLIND_STAGES = {'critique'}

_SCORE_NUM_PATTERNS = [
    (re.compile(r'(?i)\b(score|scores_mean|regret|priority[ _]score)(\s*[:=]?\s*)\d+(?:\.\d+)?'), r'\1\2[withheld]'),
    (re.compile(r'("value"\s*:\s*)\d+(?:\.\d+)?'), r'\1[withheld]'),
    (re.compile(r'\b\d+(?:\.\d+)?\s*/\s*5\b'), '[withheld]/5'),
]

def _redact_scores(text):
    for pat, rep in _SCORE_NUM_PATTERNS:
        text = pat.sub(rep, text)
    return text

STAGE_CONTEXT_EXCLUDE = {
    # The refiner judges the pitch as a colleague's pitch. Neither the story
    # nor the seed card (which reveals the constructed origin) may leak in.
    'fiction_refine': {'fiction_story.md', 'fiction_seed.json'},
}


def _target_context(stage, target):
    parts = []
    include_only = {'fiction_scout': {'fiction_seed.json'},
                    'fiction_extract': {'fiction_story.md'}}.get(stage)
    exclude = STAGE_CONTEXT_EXCLUDE.get(stage, set())
    if target.exists():
        for p in sorted(target.glob('*')):
            if not p.is_file() or p.name.startswith('prompt_'):
                continue
            if p.suffix.lower() not in {'.md', '.json', '.yaml', '.yml', '.csv'}:
                continue
            if include_only is not None and p.name not in include_only:
                continue
            if p.name in exclude:
                continue
            parts.append(f'===== {p.relative_to(ROOT)} =====\n{read_text(p)}')
    return '\n\n'.join(parts)


def _digest_path(charter):
    """Per-charter digest file; falls back to the global one until the
    charter-scoped digest has been generated at least once."""
    if charter:
        # Fail-local: a named charter gets its scoped digest path even if it
        # does not exist yet (read_text renders it empty). Falling back to
        # the global digest would leak cross-charter scores -- the same bug
        # class already fixed for portfolio briefs.
        return ROOT/'evidence'/f'ledger_digest_{charter}.md'
    p = ROOT/'evidence'/'ledger_digest_baseline.md'
    if not charter and p.exists():
        return p
    return ROOT/'evidence'/'ledger_digest.md'


def build_prompt(stage, target):
    task = read_text(PROMPTS/f'{stage}.md')
    if stage in BLIND_STAGES:
        return f"""You are a writer working inside this repository.
Repository root: {ROOT}
Assigned output directory: {target.relative_to(ROOT)}
Write only the file the task names. Preserve all other files.

{_target_context(stage, target)}

===== STAGE TASK =====
{task}
"""
    files = [charter_path(charter_for_target(target)), ROOT/'docs'/'COLLABORATOR_RULES.md',
             ROOT/'docs'/'SCORING_RUBRIC.md', ROOT/'evidence'/'decisions.md',
             _digest_path(charter_for_target(target)), _brief_path(charter_for_target(target)),
             ROOT/'evidence'/'cross_charter_index.md',
             ROOT/'evidence'/'librarian_proposals.md']
    context = '\n\n'.join(f'===== {p.relative_to(ROOT)} =====\n{read_text(p)}' for p in files)
    tctx = _target_context(stage, target)
    if tctx:
        context += '\n\n' + tctx
    return f"""You are a critical research collaborator working inside this repository.
Repository root: {ROOT}
Assigned output directory: {target.relative_to(ROOT)}
Preserve existing files unless the task explicitly requires an update.
Do not claim novelty without verified primary sources.
Do not write code unless this is the probe_code stage and human approval exists.

{context}

===== STAGE TASK =====
{task}
"""


def write_prompt(stage, target):
    target.mkdir(parents=True, exist_ok=True)
    path = target/f'prompt_{stage}.md'
    text = build_prompt(stage, target)
    if stage in SCORE_BLIND_STAGES:
        text = _redact_scores(text)
    path.write_text(text)
    return path


def load_agent_config():
    try:
        import tomllib
        return tomllib.loads((ROOT/'AGENTS.toml').read_text())
    except Exception:
        return {}


# --------------------------------------------------------------------------
# Role rotation: on odd cycles the two model families swap, so each plays
# every role across cycles without any concurrency or extra infrastructure.
# --------------------------------------------------------------------------

def effective_agent(agent, cfg=None, cycle_no=None):
    cfg = cfg or load_agent_config()
    rot = cfg.get('rotation', {})
    if not rot.get('enabled', False) or agent is None:
        return agent
    if cycle_no is None:
        cycle_no = load_state().get('active_cycle') or 0
    if cycle_no % 2 == 1:
        a, b = rot.get('pair', ['claude', 'codex'])[:2]
        if agent == a:
            return b
        if agent == b:
            return a
    return agent


# --------------------------------------------------------------------------
# Workstream D (2026-08-14): model-limit fallback with visible provenance.
# Same-family only by construction: fallback_models lives under the family's
# own AGENTS.toml section and the chain never crosses to the other family --
# adversarial stages (see FAMILY_OPPOSITIONS) fail cleanly and wait for the
# reset instead. Patterns below are PROVISIONAL best guesses to be refined
# from the first real limit event; override via AGENTS.toml [fallback].
# --------------------------------------------------------------------------
LIMIT_PATTERNS = {
    # Account-wide exhaustion: no same-family model can rescue the stage.
    'global': [r'(overall|all[ -]?models?|account|plan)[^\n]{0,60}(usage |weekly )?limit',
               r'weekly (usage )?limit[^\n]{0,50}(account|plan|all models)'],
    # The configured model is not offered to this account: skip it, not a limit.
    'unavailable': [r'unknown model', r'model[^\n]{0,40}not (found|available|recognized)',
                    r'invalid model'],
    # Model-specific allowance: the next model in the chain may rescue.
    'model': [r'(fable|opus|sonnet|haiku|this model)[^\n]{0,60}(usage |weekly )?(limit|allowance)',
              r'limit[^\n]{0,80}switch(ing)? model',
              r'usage limit reached'],
}

LAST_RUN = None  # provenance of the most recent run_agent call; merged into
                 # stage_provenance.jsonl by _record_stage_provenance.


def _classify_agent_failure(output, cfg=None):
    """Classify a nonzero agent exit from its output. Order matters:
    global beats model (an account-wide message often names a model too).
    Returns 'global' | 'unavailable' | 'model' | None."""
    pats = dict(LIMIT_PATTERNS)
    for k, v in (cfg or {}).get('fallback', {}).items():
        if k in pats and isinstance(v, list):
            pats[k] = v
    low = (output or '').lower()
    import re
    for cls in ('global', 'unavailable', 'model'):
        if any(re.search(p, low) for p in pats[cls]):
            return cls
    return None


def _command_model(command):
    """The value following --model in a command list, else None."""
    try:
        return command[command.index('--model') + 1]
    except (ValueError, IndexError):
        return None


def _with_model(command, model):
    out = list(command)
    out[out.index('--model') + 1] = model
    return out


def _quarantine_attempt(qbase, stage, attempt_no, model, exclude=()):
    """Transactional attempt isolation (D2): move everything the failed
    attempt wrote out of the working tree into an attempt directory so a
    fallback model starts clean, never primed by a half-written artifact.
    Stages start from a clean tree, so all dirt is the failed attempt's.
    Untracked files are moved; modified tracked files are copied then
    restored via git. No-op (with a note) when git is unavailable."""
    q = Path(qbase) / 'attempts' / f'{stage or "stage"}-attempt{attempt_no}-{model}'
    st = subprocess.run(['git', 'status', '--porcelain'], cwd=ROOT,
                        capture_output=True, text=True, check=False)
    moved, restored = [], []
    if st.returncode == 0:
        try:
            skip_prefix = str(q.parent.relative_to(ROOT))
        except ValueError:
            skip_prefix = None
        excl = {str(Path(e).resolve()) for e in exclude if e}
        for line in st.stdout.splitlines():
            code, path = line[:2], line[3:].strip().strip('"')
            if not path or (skip_prefix and path.startswith(skip_prefix)):
                continue
            if str((ROOT / path).resolve()) in excl:
                continue  # the stage's own prompt/log, not attempt output
            src = ROOT / path
            if not src.is_file():
                continue
            q.mkdir(parents=True, exist_ok=True)
            dest = q / path.replace('/', '__')
            if code.strip() == '??':
                shutil.move(str(src), dest)
                moved.append(path)
            else:
                shutil.copy2(src, dest)
                subprocess.run(['git', 'checkout', '--', path], cwd=ROOT, check=False)
                restored.append(path)
    if moved or restored:
        q.mkdir(parents=True, exist_ok=True)
        (q / 'ATTEMPT.json').write_text(json.dumps(
            {'stage': stage, 'model': model, 'attempt': attempt_no,
             'moved': moved, 'restored_tracked': restored,
             'ts': datetime.now(timezone.utc).isoformat(timespec='seconds')},
            indent=2) + '\n')
        print(f'Quarantined {len(moved) + len(restored)} partial file(s) from the '
              f'failed attempt into {q.relative_to(ROOT)}')


def _invoke_agent(command, use_stdin, prompt_text, timeout, log_path):
    """One agent attempt. Returns (returncode, combined_output)."""
    lines = []
    import time
    deadline = time.monotonic() + timeout
    proc = subprocess.Popen(command, cwd=ROOT, text=True,
                            stdin=subprocess.PIPE if use_stdin else None,
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    try:
        if use_stdin:
            try:
                proc.stdin.write(prompt_text)
                proc.stdin.close()
            except BrokenPipeError:
                pass
        for line in proc.stdout:
            print(line, end='', flush=True)
            lines.append(line)
            if time.monotonic() > deadline:
                proc.kill()
                raise SystemExit(f'Agent timed out after {timeout}s.')
        proc.wait(timeout=max(1, deadline - time.monotonic()))
    except subprocess.TimeoutExpired:
        proc.kill()
        raise SystemExit(f'Agent timed out after {timeout}s.')
    finally:
        if log_path:
            try:
                Path(log_path).write_text(''.join(lines))
            except OSError as e:
                print(f'(could not write agent log: {e})')
    return proc.returncode, ''.join(lines)


def run_agent(prompt_path, agent=None, stage=None, log_path=None):
    global LAST_RUN
    cfg = load_agent_config()
    if agent is None and stage:
        agent = cfg.get('roles', {}).get(stage.replace('-', '_'))
    agent = agent or cfg.get('default',{}).get('agent','claude')
    agent = effective_agent(agent, cfg)
    print(f'[stage={stage} agent={agent}]')
    acfg = cfg.get(agent,{})
    if not acfg.get('enabled', False):
        print(f'Agent {agent!r} is disabled. Use this prompt manually:\n{prompt_path}')
        return
    if agent == 'claude' and os.environ.get('ANTHROPIC_API_KEY') \
            and not acfg.get('allow_api_billing', False):
        raise SystemExit(
            'ANTHROPIC_API_KEY is set: Claude Code would authenticate against '
            'API billing instead of the subscription (D2 billing guard). Unset '
            'the variable, or set allow_api_billing = true under [claude] in '
            'AGENTS.toml as a deliberate, recorded choice. No tokens were spent.')
    command = acfg.get('command', [])
    if os.environ.get('SCOUT_CI') and acfg.get('command_ci'):
        command = acfg['command_ci']
        print('(SCOUT_CI set: using command_ci variant)')
    if not command:
        print(f'No command configured. Use prompt manually:\n{prompt_path}')
        return
    prompt_text = Path(prompt_path).read_text()
    use_stdin = acfg.get('stdin', True)
    command = [x.replace('{prompt_file}', str(prompt_path))
                .replace('{prompt_text}', prompt_text)
                .replace('{repo}', str(ROOT)) for x in command]
    if shutil.which(command[0]) is None:
        print(f'{command[0]} not found. Use prompt manually:\n{prompt_path}')
        return
    timeout = int(cfg.get('limits', {}).get('stage_timeout', 3600))
    primary = _command_model(command)
    chain = [primary] + list(acfg.get('fallback_models', [])) if primary else [primary]
    qbase = Path(log_path).parent if log_path else ROOT / 'orchestrator'
    attempts = []
    for i, model in enumerate(chain):
        cmd = command if i == 0 else _with_model(command, model)
        print('Running:', ' '.join(cmd[:3]), '...'
              + (f' [fallback attempt {i+1}/{len(chain)}: {model}]' if i else ''))
        rc, output = _invoke_agent(cmd, use_stdin, prompt_text, timeout, log_path)
        attempts.append({'model': model, 'returncode': rc})
        if rc == 0:
            LAST_RUN = {'agent': agent, 'stage': stage,
                        'model_requested': chain[0], 'model_used': model,
                        'fallback': i > 0, 'attempts': attempts}
            if i > 0:
                print(f'FALLBACK: stage completed on {model} '
                      f'(requested {chain[0]}). Recorded in stage provenance; '
                      'rotation identity unchanged (family, not model).')
            return
        cls = _classify_agent_failure(output, cfg)
        attempts[-1]['failure_class'] = cls
        LAST_RUN = {'agent': agent, 'stage': stage,
                    'model_requested': chain[0], 'model_used': None,
                    'fallback': i > 0, 'attempts': attempts}
        if cls == 'global':
            raise SystemExit(
                'Agent hit the ACCOUNT-WIDE usage limit; no same-family '
                'fallback can rescue this stage (D2 limit classification). '
                f'Wait for the weekly reset. Prompt retained at {prompt_path}')
        if cls in ('model', 'unavailable') and i + 1 < len(chain):
            _quarantine_attempt(qbase, stage, i + 1, model,
                                exclude=(prompt_path, log_path))
            reason = ('model-specific limit' if cls == 'model'
                      else 'model unavailable to this account')
            print(f'{reason} on {model}; retrying with {chain[i+1]}.')
            continue
        raise SystemExit(f'Agent exited with code {rc}. Prompt retained at {prompt_path}')


# --------------------------------------------------------------------------
# D3/D4 (2026-08-14): one declarative table of required family oppositions,
# validated identically by doctor, cycle start, and tests, so independent
# guards cannot drift apart. Stages here derive their scientific integrity
# from two DIFFERENT model families opposing each other; they must fail
# cleanly (and wait for quota) rather than ever collapse into one family.
# --------------------------------------------------------------------------
FAMILY_OPPOSITIONS = [
    ('scout', 'critique'),
    ('probe_code', 'probe_review'),
    ('debate_proposer', 'debate_critic'),
    ('fiction_writer', 'fiction_refiner'),
    ('scout', 'connection_check'),   # E3 stage; skipped until the role exists
    ('interpret', 'interpret_review'),
]


def _resolve_role_family(cfg, role, cycle_no=None):
    """Family playing `role` this cycle, or None if the role is not
    configured (e.g. connection_check before E3 lands)."""
    if role in ('debate_proposer', 'debate_critic'):
        side = cfg.get('debate', {}).get(role.split('_')[1])
        return effective_agent(side, cfg, cycle_no) if side else None
    if role in ('fiction_writer', 'fiction_refiner'):
        writer, refiner = _fiction_writer_and_refiner(cfg, cycle_no)
        return writer if role == 'fiction_writer' else refiner
    if role == 'interpret_review':
        explicit = cfg.get('roles', {}).get('interpret_review')
        if explicit:
            return effective_agent(explicit, cfg, cycle_no)
        gen = _resolve_role_family(cfg, 'interpret', cycle_no)
        pair = cfg.get('rotation', {}).get('pair', ['claude', 'codex'])[:2]
        return (pair[1] if gen == pair[0] else pair[0]) if gen else None
    if role == 'probe_review':
        explicit = cfg.get('roles', {}).get('probe_review')
        if explicit:
            return effective_agent(explicit, cfg, cycle_no)
        gen = _resolve_role_family(cfg, 'probe_code', cycle_no)
        pair = cfg.get('rotation', {}).get('pair', ['claude', 'codex'])[:2]
        return (pair[1] if gen == pair[0] else pair[0]) if gen else None
    assigned = cfg.get('roles', {}).get(role)
    return effective_agent(assigned, cfg, cycle_no) if assigned else None


def _check_family_opposition(cfg, cycle_no=None):
    """Raise before any tokens are spent if an adversarial pairing has
    collapsed into one family (misconfiguration, rotation bug, or a
    future fallback path crossing families)."""
    problems = []
    for a, b in FAMILY_OPPOSITIONS:
        fa = _resolve_role_family(cfg, a, cycle_no)
        fb = _resolve_role_family(cfg, b, cycle_no)
        if fa and fb and fa == fb:
            problems.append(f'{a} and {b} would both run as {fa!r}')
    if problems:
        raise SystemExit(
            'FAMILY OPPOSITION VIOLATION (D3): ' + '; '.join(problems) + '. '
            'Adversarial stages require opposite model families; fix '
            'AGENTS.toml roles/rotation. No tokens were spent.')


def doctor(_):
    print('Concept Research Scout doctor')
    print('Python:', sys.version.split()[0])
    for f in ['CHARTER.md','AGENTS.toml','docs/COLLABORATOR_RULES.md','docs/SCORING_RUBRIC.md']:
        print(('OK ' if (ROOT/f).exists() else 'MISSING ')+f)
    for cmd in ['git','claude','codex']:
        print(f'{cmd}:', shutil.which(cmd) or 'not found (optional except git recommended)')
    cfg = load_agent_config()
    roles = cfg.get('roles', {})
    if roles:
        print('\nRole assignment:')
        for k, v in roles.items():
            if v == 'alternating':
                d = cfg.get('debate', {})
                print(f"  {k:<12} -> {d.get('proposer','?')} vs {d.get('critic','?')}"
                      f"  (max {d.get('max_rounds', 3)} rounds)")
                continue
            en = cfg.get(v, {}).get('enabled', False)
            eff = effective_agent(v, cfg)
            note = '' if en else '   [DISABLED - fix AGENTS.toml]'
            if eff != v:
                note += f'   [rotated -> {eff} this cycle]'
            print(f'  {k:<12} -> {v}' + note)
        concrete = [v for v in roles.values() if v != 'alternating']
        if len(set(concrete)) < 2:
            print('  WARNING: one model holds every role. It will be critiquing itself.')
    else:
        print('\nNo [roles] table in AGENTS.toml - all stages use the default agent.')
    print('\nFamily oppositions (D3):')
    try:
        _check_family_opposition(cfg)
        for a, b in FAMILY_OPPOSITIONS:
            fa = _resolve_role_family(cfg, a)
            fb = _resolve_role_family(cfg, b)
            state = 'skipped (role absent)' if not (fa and fb) else f'{fa} vs {fb}  OK'
            print(f'  {a:<16} <-> {b:<16} {state}')
    except SystemExit as e:
        print(f'  {e}')
    fb_chain = cfg.get('claude', {}).get('fallback_models', [])
    _prim = _command_model(cfg.get('claude', {}).get('command', []))
    print('Fallback chain [claude]:',
          ' -> '.join([str(_prim)] + list(fb_chain)) if fb_chain
          else 'none configured (D1 pending)')
    rot = cfg.get('rotation', {})
    print(f"\nRotation: {'enabled' if rot.get('enabled') else 'disabled'}"
          f" (pair={rot.get('pair', ['claude','codex'])},"
          f" active_cycle={load_state().get('active_cycle')})")
    chs = sorted(p.parent.name for p in (ROOT/'charters').glob('*/CHARTER.md')) if (ROOT/'charters').exists() else []
    if chs:
        cst = load_state().get('charters', {})
        print('Charters: ' + ', '.join(
            f"{c} (next cycle {cst.get(c, {}).get('next_scout', 1):03d})" for c in chs))
    entries = ledger_mod.load()
    print(f'Ledger: {len(entries)} entr{"y" if len(entries)==1 else "ies"} '
          f'({"present" if ledger_mod.LEDGER.exists() else "missing - run: python scout.py ledger migrate"})')
    print('\nColab execution is intentionally optional. package-colab creates a launcher notebook.')


def new_scout(_):
    s=load_state(); n=s['next_scout']; d=scout_dir(n); d.mkdir(parents=True,exist_ok=False)
    (d/'README.md').write_text(f'# Scouting cycle {n:03d}\n\nCandidate portfolio before idea selection.\n')
    s['next_scout']=n+1; save_state(s)
    p=write_prompt('scout',d)
    print(d.relative_to(ROOT)); print('Prompt:',p.relative_to(ROOT))


def _load_candidates(scout_no, track=None, charter=None):
    src = scout_dir(scout_no, charter)/'scout_candidates.json'
    merged = scout_dir(scout_no, charter)/'candidates_all.json'
    if merged.exists():
        src = merged
    if not src.exists():
        raise SystemExit(f'Missing {src}. Run or complete the scout stage first.')
    data = json.loads(src.read_text())
    candidates = data.get('candidates', data if isinstance(data, list) else [])
    if track:
        candidates = [c for c in candidates if c.get('track', 'baseline') == track]
    return candidates


def _do_shortlist(scout_no, cand_no, track=None, charter=None):
    """Shortlist candidate cand_no (1-based) from cycle scout_no (optionally a
    named charter's cycle). Idempotent per cycle."""
    s = load_state()
    skey = _fmt_scout(charter, scout_no) if charter else str(scout_no)
    done = s.setdefault('shortlisted', {}).setdefault(skey, {})
    if str(cand_no) in done:
        print(f'Candidate {cand_no} of cycle {_fmt_scout(charter, scout_no)} already shortlisted as idea {done[str(cand_no)]:03d}.')
        return done[str(cand_no)]
    candidates = _load_candidates(scout_no, track, charter)
    idx = cand_no-1
    if idx < 0 or idx >= len(candidates):
        raise SystemExit('Candidate index out of range.')
    err = _validate_card(candidates[idx])
    if err:
        raise SystemExit(f'Candidate {cand_no} fails schema validation ({err}); '
                         'not promoting an invalid card.')
    existing = [int(p.name) for p in (ROOT/'ideas').iterdir() if p.is_dir() and p.name.isdigit()]
    n = max(existing, default=0)+1
    d = idea_dir(n); d.mkdir()
    card = candidates[idx]
    (d/'idea_card.json').write_text(json.dumps(card, indent=2)+'\n')
    (d/'README.md').write_text(f"# Idea {n:03d}: {card.get('title','Untitled')}\n\nSelected from scouting cycle {_fmt_scout(charter, scout_no)}, candidate {cand_no}.\n")
    s = load_state()
    s['selected_idea'] = n
    # charter-qualified key, matching the idempotence read above (the
    # unqualified write here silently broke idempotence and collided
    # baseline cycle N with every charter's cycle N -- 2026-08-18 audit)
    s.setdefault('shortlisted', {}).setdefault(skey, {})[str(cand_no)] = n
    save_state(s)
    with (ROOT/'portfolio'/'ideas.csv').open('a', newline='') as f:
        csv.writer(f).writerow([f'{n:03d}', card.get('title',''), 'ACTIVE', '', card.get('scores',{}).get('regret',''), 'CRITIQUE', ''])
    ledger_mod.append({'ledger_id': f'idea-{n:03d}', 'title': card.get('title',''),
                       'claim': card.get('deliverable_sentence') or card.get('question',''),
                       'deliverable_original': card.get('deliverable_sentence', ''),
                       'track': card.get('track','baseline'), 'status': 'SHORTLISTED',
                       'charter': charter,
                       'scrutiny': 'SCOUTED', 'source': f'ideas/{n:03d}'})
    if track is None:
        # Retire the source candidate. The EXPLICIT charter argument is the
        # only authority here: _active_charter() reflects whatever cycle is
        # globally current and falsely retired six baseline rows for ISLES
        # promotions (2026-08-18 audit; produced zombie idea-026).
        ledger_mod.append({'ledger_id': _scout_lid(charter, scout_no, f'c{cand_no:02d}'),
                           'status': 'SHORTLISTED', 'notes': f'promoted to idea-{n:03d}',
                           'charter': charter})
    ledger_mod.digest()
    print(f'Shortlisted as idea {n:03d}')
    return n


def shortlist(args):
    ch, no = _parse_scout_ref(args.scout)
    _do_shortlist(no, args.candidate, args.track, charter=ch)


def stage_target(stage, idea):
    if stage in ('scout','wide-scout','fiction-scout','fiction-extract','fiction-refine','novelty-audit'):
        scouts=sorted((ROOT/'ideas').glob('scout-*'))
        if not scouts: raise SystemExit('Run new-scout first.')
        return scouts[-1]
    if idea is None:
        idea=load_state().get('selected_idea')
    if idea is None: raise SystemExit('--idea is required or shortlist an idea first.')
    return idea_dir(idea)


def run_stage(args):
    target=stage_target(args.stage,args.idea)
    if args.stage=='probe-code':
        approval=target/'HUMAN_APPROVED_PROBE'
        contract=target/'probe_contract.yaml'
        if not approval.exists() or not contract.exists():
            raise SystemExit('Probe code blocked: probe contract and HUMAN_APPROVED_PROBE are required.')
        bound = next((ln.split(':',1)[1].strip() for ln in
                      approval.read_text().splitlines()
                      if ln.startswith('contract_blob:')), None)
        current = _contract_hash(target)
        if bound != current:
            raise SystemExit(
                'Probe code blocked: HUMAN_APPROVED_PROBE is bound to '
                f'contract blob {str(bound)[:12]} but probe_contract.yaml is now '
                f'{str(current)[:12]}. The contract changed after approval '
                '(or predates hash binding). Re-run approve-probe to approve '
                'the CURRENT contract. Stale approvals never authorize new '
                'contracts.')
    _require_clean_tree(args.stage)
    p=write_prompt(args.stage.replace('-','_'), target)
    print('Prompt:',p.relative_to(ROOT))
    run_agent(p, args.agent, stage=args.stage,
              log_path=target / f"log_{args.stage.replace('-', '_')}.txt")
    _check_scope(args.stage)
    _require_artifact(args.stage.replace('-', '_'), target)
    if args.stage=='critique' and args.idea:
        ledger_mod.raise_scrutiny(f'idea-{args.idea:03d}', 'CRITIQUED')


def _probe_review_verdict(target):
    import re
    body = read_text(target/'probe_review.md')
    m = re.findall(r'```json\s*(\{.*?\})\s*```', body, flags=re.S)
    if not m:
        return None
    try:
        return json.loads(m[-1])
    except json.JSONDecodeError:
        return None


def probe_build(args):
    """Generate Stage 0 probe code with cross-model adversarial review:
    probe-code (one family) -> probe-review (the other) -> at most one
    revision -> deterministic verify. The goal is fixed beforehand by the
    human-approved feasibility memo + contract; review checks fidelity to
    that goal, never expands it."""
    d = idea_dir(args.idea)
    if not (d/'HUMAN_APPROVED_PROBE').exists():
        raise SystemExit('Run approve-probe first: the human gate precedes any code.')
    if not (d/'probe_contract.yaml').exists():
        raise SystemExit('probe_contract.yaml missing: run `run --stage probe-plan` first.')
    _require_clean_tree('probe-build')
    cfg = load_agent_config()
    base = (cfg.get('roles', {}) or {}).get('probe_code', cfg.get('default', {}).get('agent', 'claude'))
    if base not in ('claude', 'codex'):
        base = 'claude'
    # run_agent applies rotation itself; pass base names so gen/rev stay
    # opposite families after any swap (a pre-swap here double-rotated).
    gen = base
    rev = 'codex' if base == 'claude' else 'claude'
    print(f'Probe generator role: {gen}; reviewer role: {rev} '
          '(rotation may swap which family is which; they always differ).')
    pdir = ROOT/'probes'/f'{args.idea:03d}'
    alias = ROOT/'probes'/f'idea-{args.idea:03d}'
    try:
        for round_no in (1, 2):
            if alias.exists() and not pdir.exists():
                alias.rename(pdir)  # normalize the contract's idea-NNN naming
                print(f'Normalized {alias.name}/ -> {pdir.name}/')
            if (pdir/'run.py').exists() and round_no == 1 and not _probe_review_verdict(d):
                print('Existing probe code found; skipping generation, going straight to review.')
            else:
                p1 = write_prompt('probe_code', d)
                if round_no == 2:
                    p1.write_text(p1.read_text() + '\n===== REVISION ROUND =====\n'
                                  'A reviewer found blocking issues (see probe_review.md in your '
                                  'context). Fix ONLY those findings; do not expand scope.\n')
                run_agent(p1, gen, stage='probe_code', log_path=d/'log_probe_code.txt')
                _check_scope('probe-code')
                if alias.exists() and not pdir.exists():
                    alias.rename(pdir)
                    print(f'Normalized {alias.name}/ -> {pdir.name}/')
            for fname in ('run.py', 'README.md'):
                if not (pdir/fname).exists():
                    raise SystemExit(f'probe_code wrote no {fname} in {pdir.relative_to(ROOT)}; '
                                     'the probe contract requires it.')
            _commit_all(f'idea {args.idea:03d}: probe code (round {round_no})')
            p2 = write_prompt('probe_review', d)
            run_agent(p2, rev, stage='probe_review', log_path=d/'log_probe_review.txt')
            _require_artifact('probe_review', d)
            _commit_all(f'idea {args.idea:03d}: probe review (round {round_no})')
            v = _probe_review_verdict(d) or {}
            if v.get('verdict') == 'APPROVE':
                print(f'Probe code APPROVED on round {round_no}.')
                break
            if round_no == 2:
                raise SystemExit('Probe code still has blocking findings after one revision; '
                                 'read probe_review.md and decide by hand.')
            print(f'Reviewer requests revision: {", ".join(v.get("blocking", [])[:3])}')
    except SystemExit:
        _commit_all(f'idea {args.idea:03d}: probe-build FAILED (partial output preserved)')
        raise
    verify_probe(args)


def _contract_hash(d):
    """git blob hash of the idea's probe_contract.yaml, or None."""
    f = d / 'probe_contract.yaml'
    if not f.exists():
        return None
    r = subprocess.run(['git', 'hash-object', str(f)], cwd=ROOT,
                       capture_output=True, text=True, check=False)
    return r.stdout.strip() or None


def _interpret_review_verdict(target):
    import re
    body = read_text(target/'interpret_review.md')
    m = re.findall(r'```json\s*(\{.*?\})\s*```', body, flags=re.S)
    if not m:
        return None
    try:
        return json.loads(m[-1])
    except json.JSONDecodeError:
        return None


def interpret_build(args):
    """Cross-family adversarial interpretation (mirrors probe-build):
    interpret (one family) writes interpretation.md under a hard citation
    mandate -> interpret-review (the other family) resolves every citation
    against the actual analysis files and checks claim bounds -> at most
    one revision. The single most claim-bearing step in the pipeline no
    longer runs unopposed."""
    d = idea_dir(args.idea)
    bundle = ROOT/'probes'/f'{args.idea:03d}'/'results_v2'
    if not bundle.exists():
        cands = sorted((ROOT/'probes'/f'{args.idea:03d}'/'results').glob('*/summary.json'))
        if cands:
            bundle = cands[-1].parent
    fails = validate_bundle(args.idea, bundle) if bundle.exists() else ['no results bundle found']
    if fails:
        raise SystemExit('interpret-build refuses: bundle invalid or missing: '
                         + '; '.join(fails[:3]))
    _require_clean_tree('interpret-build')
    cfg = load_agent_config()
    base = (cfg.get('roles', {}) or {}).get('interpret', cfg.get('default', {}).get('agent', 'codex'))
    if base not in ('claude', 'codex'):
        base = 'codex'
    gen = base
    rev = 'codex' if base == 'claude' else 'claude'
    print(f'Interpreter role: {gen}; reviewer role: {rev} '
          '(rotation may swap which family is which; they always differ).')
    try:
        for round_no in (1, 2):
            p1 = write_prompt('interpret', d)
            if round_no == 2:
                p1.write_text(p1.read_text() + '\n===== REVISION ROUND =====\n'
                              'The checker found blocking issues (see interpret_review.md '
                              'in your context). Fix ONLY those findings in '
                              'interpretation.md and decision.md; do not expand scope.\n')
            run_agent(p1, gen, stage='interpret', log_path=d/'log_interpret.txt')
            _check_scope('interpret')
            if not (d/'interpretation.md').exists():
                raise SystemExit('interpret wrote no interpretation.md; the citation '
                                 'mandate requires it before decision.md.')
            _commit_all(f'idea {args.idea:03d}: interpretation (round {round_no})')
            p2 = write_prompt('interpret_review', d)
            run_agent(p2, rev, stage='interpret_review', log_path=d/'log_interpret_review.txt')
            _require_artifact('interpret_review', d)
            _commit_all(f'idea {args.idea:03d}: interpret review (round {round_no})')
            v = _interpret_review_verdict(d) or {}
            if v.get('verdict') == 'APPROVE':
                print(f'Interpretation APPROVED on round {round_no}. '
                      'Human ratification of the decision entry remains yours.')
                break
            if round_no == 2:
                raise SystemExit('Interpretation still blocked after one revision round; '
                                 'human review of interpret_review.md required.')
            print('Reviewer requested revision; running the one allowed round.')
    except SystemExit:
        _commit_all(f'idea {args.idea:03d}: interpret-build FAILED (partial output preserved)')
        raise


def approve_probe(args):
    d=idea_dir(args.idea)
    if not (d/'feasibility.md').exists(): raise SystemExit('Feasibility memo missing.')
    ch = _contract_hash(d)
    if not ch:
        raise SystemExit('probe_contract.yaml missing: approval binds to a '
                         'specific contract; run probe-plan first.')
    marker=d/'HUMAN_APPROVED_PROBE'
    marker.write_text(f'Approved by human at {datetime.now(timezone.utc).isoformat()}\n'
                      f'contract_blob: {ch}\n')
    print(f'Approved probe for {d.name} (bound to contract blob {ch[:12]})')


def verify_probe(args):
    p=ROOT/'probes'/f'{args.idea:03d}'
    issues=[]
    for f in ['run.py','README.md']:
        if not (p/f).exists(): issues.append(f'missing {f}')
    if (p/'run.py').exists():
        r=subprocess.run([sys.executable,'-m','py_compile',str(p/'run.py')],capture_output=True,text=True)
        if r.returncode: issues.append('syntax error: '+r.stderr[-500:])
        # Interface convention: `run.py --smoke` (canonical; --smoke-test
        # accepted for older probes) must be runnable by this harness. A probe
        # whose smoke writes artifacts gets a throwaway --output-dir. Argparse
        # reports one error at a time, so no stderr classification: just try
        # each flag fully and keep the first failure for honest reporting.
        import tempfile
        smoke=None; first_fail=None
        for flag in ('--smoke','--smoke-test'):
            smoke=subprocess.run([sys.executable,str(p/'run.py'),flag],cwd=p,capture_output=True,text=True,timeout=300)
            if smoke.returncode and '--output-dir' in (smoke.stderr or ''):
                with tempfile.TemporaryDirectory() as td:
                    smoke=subprocess.run([sys.executable,str(p/'run.py'),flag,'--output-dir',td],
                                         cwd=p,capture_output=True,text=True,timeout=300)
            if smoke.returncode==0: break
            if first_fail is None: first_fail=smoke
        if smoke.returncode:
            smoke=first_fail or smoke
            issues.append('smoke test failed: '+(smoke.stderr or smoke.stdout)[-1000:])
    out={'idea_id':f'{args.idea:03d}','passed':not issues,'issues':issues,'checked_at':datetime.now(timezone.utc).isoformat()}
    (p/'verification.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps(out,indent=2))
    if issues: raise SystemExit(1)


def _staging_cells(concept, suffixes):
    """Deterministic Colab staging cells for a Zenodo-hosted archive: pin the
    immutable child record, resumable-download the single .7z to Drive, and
    selectively extract only the declared suffixes. Pure driver plumbing; the
    probe's own provenance gates re-verify everything downstream."""
    sufs = ', '.join(repr(x) for x in suffixes)
    pin = (
        "# --- Generated staging: Zenodo record " + concept + " (Drive-persistent, idempotent) ---\n"
        "import os, json, urllib.request\n"
        "STAGE = '/content/drive/MyDrive/staging-" + concept + "'\n"
        "RECORD_JSON = STAGE + '/zenodo_record.json'\n"
        "DATA_DIR = STAGE + '/extracted'\n"
        "os.makedirs(STAGE, exist_ok=True)\n"
        "if not os.path.exists(RECORD_JSON):\n"
        "    with urllib.request.urlopen('https://zenodo.org/api/records/" + concept + "') as r:\n"
        "        rec = json.load(r)\n"
        "    assert str(rec['id']) != '" + concept + "', 'resolved to the concept record; need an immutable child version'\n"
        "    json.dump(rec, open(RECORD_JSON, 'w'), indent=2)\n"
        "rec = json.load(open(RECORD_JSON))\n"
        "_a = [f for f in rec['files'] if f['key'].endswith('.7z')]\n"
        "assert len(_a) == 1, _a\n"
        "ARCHIVE = STAGE + '/' + _a[0]['key']\n"
        "ARCHIVE_URL = _a[0]['links']['self']\n"
        "print('pinned record', rec['id'], _a[0]['key'], round(_a[0]['size']/1e9, 1), 'GB')")
    download = '!wget -c -O "{ARCHIVE}" "{ARCHIVE_URL}"'
    extract = (
        "SUFFIXES = [" + sufs + "]\n"
        "if not os.path.isdir(DATA_DIR):\n"
        "    !apt-get -qq install -y p7zip-full\n"
        "    _inc = ' '.join('-ir!*' + x for x in SUFFIXES)\n"
        '    !7z x "{ARCHIVE}" -o"{DATA_DIR}" {_inc} -y\n'
        '!find "{DATA_DIR}" -type f | wc -l')
    return [pin, download, extract]


def package_colab(args):
    """E2 launcher generator. The notebook is a THIN DRIVER: it never
    imports the model stack into its own kernel (pip installs feed the
    `!python` child process, so no restart exists in the workflow), pins
    the repo commit and results branch at packaging time, reads the GitHub
    PAT from Colab Secrets (zero credentials in the committed notebook),
    and pushes each session's bundle to a contract-bound results branch
    (E1 transport). Deterministic machinery, not agent output: no review
    cycle applies."""
    try:
        import nbformat as nbf
    except ImportError:
        raise SystemExit('Install nbformat: pip install nbformat')
    p = ROOT / 'probes' / f'{args.idea:03d}'
    p.mkdir(parents=True, exist_ok=True)
    phase = getattr(args, 'phase', 'B') or 'B'
    remote = subprocess.run(['git', 'config', '--get', 'remote.origin.url'],
                            cwd=ROOT, capture_output=True, text=True,
                            check=False).stdout.strip() or 'PASTE_REPO_URL'
    if remote.startswith('git@github.com:'):
        remote = 'https://github.com/' + remote.split(':', 1)[1]
    pin = subprocess.run(['git', 'rev-parse', 'HEAD'], cwd=ROOT,
                         capture_output=True, text=True,
                         check=False).stdout.strip()
    chash = _contract_hash(idea_dir(args.idea)) or 'nocontract'
    branch = f'results/probe-{args.idea:03d}-{chash[:12]}'
    nn = f'{args.idea:03d}'
    staging_cells, extra = [], ''
    if getattr(args, 'staging_zenodo', None):
        sufs = [x.strip() for x in (getattr(args, 'staging_suffixes', '') or '').split(',') if x.strip()]
        if not sufs:
            raise SystemExit('--staging-zenodo requires --staging-suffixes')
        staging_cells = [nbf.v4.new_code_cell(src)
                         for src in _staging_cells(args.staging_zenodo, sufs)]
        extra = ' --data-dir {DATA_DIR} --archive-file {ARCHIVE} --record-json {RECORD_JSON}'
    psd = getattr(args, 'phase_s_dir', None)
    _rp = ROOT / f'probes/{nn}/run.py'
    if (_rp.exists() and '--phase-s-dir' in _rp.read_text()
            and str(phase).upper() not in ('S', 'SMOKE') and not psd):
        raise SystemExit('this probe declares --phase-s-dir and phase '
                         f'{phase} requires it; pass --phase-s-dir (the '
                         'Drive path of the Phase-S bundle)')
    cfg_extra = f"\nPHASE_S_DIR = '{psd}'" if psd else ''
    if psd:
        extra += ' --phase-s-dir {PHASE_S_DIR}'
    nb = nbf.v4.new_notebook()
    nb.cells = [
      nbf.v4.new_markdown_cell(
        f'# Probe {nn} launcher (phase {phase})\n'
        'Colab is a compute worker only. This driver kernel NEVER imports '
        'the model stack -- `run.py` runs as a child process, so no kernel '
        'restart is ever needed.\n\n'
        '**One-time setup:** create a fine-grained GitHub PAT scoped to '
        'this single repository, Contents: Read and write, with an expiry. '
        'In Colab: key icon (Secrets) -> add `SCOUT_RESULTS_PAT` -> enable '
        'notebook access. The PAT never appears in this notebook or its '
        'output.\n\n'
        f'Results branch (contract-bound): `{branch}`\n\n'
        'Per session: run all cells top to bottom. After a disconnect, '
        'rerun all cells -- run.py resumes from the bundle on Drive, and '
        'the transport cell pushes whatever is new.'),
      nbf.v4.new_code_cell(
        f"PHASE = '{phase}'\n"
        f"REPO_URL = '{remote}'\n"
        f"PIN_COMMIT = '{pin}'\n"
        f"RESULTS_BRANCH = '{branch}'\n"
        f"OUTPUT_DIR = '/content/drive/MyDrive/concept-research-scout-results/{nn}_{phase}'{cfg_extra}"),
      nbf.v4.new_code_cell(
        "from google.colab import drive, userdata\n"
        "import os\n"
        "drive.mount('/content/drive')\n"
        "GH_PAT = userdata.get('SCOUT_RESULTS_PAT')  # never printed\n"
        "os.environ['HF_TOKEN'] = userdata.get('HF_TOKEN')  # inherited by the run.py child; never printed"),
      nbf.v4.new_code_cell(
        "!rm -rf /content/scout-repo\n"
        "!git clone {REPO_URL} /content/scout-repo\n"
        "%cd /content/scout-repo\n"
        "!git checkout {PIN_COMMIT}"),
      nbf.v4.new_code_cell(
        f"!pip install -q -r probes/{nn}/requirements.txt"),
      *staging_cells,
      nbf.v4.new_code_cell(
        "# Console (incl. any crash traceback) persists to Drive; refresh-proof.\n"
        f"!mkdir -p {{OUTPUT_DIR}}\n"
        f"!python probes/{nn}/run.py --phase {{PHASE}} --output-dir {{OUTPUT_DIR}}{extra} 2>&1 | tee -a {{OUTPUT_DIR}}/driver_console.log"),
      nbf.v4.new_code_cell(
        "# E1 transport: mirror the bundle onto the contract-bound results\n"
        "# branch. ORDER MATTERS: check out the branch FIRST, then overlay the\n"
        "# bundle (copy-then-checkout fails after session 1: git refuses to\n"
        "# overwrite untracked files the branch already tracks). The PAT rides\n"
        "# in a header, never in argv or output.\n"
        "import shutil, subprocess, pathlib, base64, datetime\n"
        "repo = pathlib.Path('/content/scout-repo')\n"
        f"dest = repo / 'probes/{nn}/results_v2'\n"
        "def git(*a, **k):\n"
        "    r = subprocess.run(['git', *a], cwd=repo, capture_output=True, text=True, **k)\n"
        "    if r.returncode: raise SystemExit(f'git {a[0]} failed: {r.stderr[-400:]}')\n"
        "    return r.stdout\n"
        "git('config', 'user.email', 'colab-runner@scout.local')\n"
        "git('config', 'user.name', 'scout colab runner')\n"
        "auth = base64.b64encode(f'x-access-token:{GH_PAT}'.encode()).decode()\n"
        "hdr = f'http.extraheader=AUTHORIZATION: basic {auth}'\n"
        "if subprocess.run(['git', '-c', hdr, 'fetch', 'origin', RESULTS_BRANCH], cwd=repo, capture_output=True).returncode == 0:\n"
        "    git('checkout', '-B', RESULTS_BRANCH, f'origin/{RESULTS_BRANCH}')\n"
        "else:\n"
        "    git('checkout', '-B', RESULTS_BRANCH, PIN_COMMIT)\n"
        "if dest.exists(): shutil.rmtree(dest)\n"
        "shutil.copytree(OUTPUT_DIR, dest)\n"
        f"git('add', '-f', 'probes/{nn}/results_v2')\n"
        "stamp = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds')\n"
        "subprocess.run(['git', 'commit', '-m', f'session results {stamp}'], cwd=repo, capture_output=True)\n"
        "git('-c', hdr, 'push', 'origin', RESULTS_BRANCH)\n"
        "print('pushed', RESULTS_BRANCH)"),
      nbf.v4.new_markdown_cell(
        'When `run.py` reports the study complete, the results-validate '
        'workflow on the pushed branch verifies the bundle and opens the '
        'record-result PR. Merging that PR is the human gate.'),
    ]
    out = p / f'colab_probe_{args.idea:03d}.ipynb'
    nbf.write(nb, out)
    print(out.relative_to(ROOT))
    print(f'  pinned commit  {pin[:12]}\n  results branch {branch}\n'
          f'  phase          {phase}\n'
          '  secret needed  SCOUT_RESULTS_PAT (Colab Secrets)')


def _contract_field(idea, field):
    """Scalar field from the idea's probe_contract.yaml, or None."""
    try:
        import yaml
    except ImportError:
        raise SystemExit('Install PyYAML: pip install PyYAML')
    f = idea_dir(idea) / 'probe_contract.yaml'
    if not f.exists():
        return None
    def _find(node):
        if isinstance(node, dict):
            for k, v in node.items():
                if k == field and isinstance(v, (str, int, float)):
                    return v
                got = _find(v)
                if got is not None:
                    return got
        elif isinstance(node, list):
            for v in node:
                got = _find(v)
                if got is not None:
                    return got
        return None
    return _find(yaml.safe_load(f.read_text()))


def _contract_required_outputs(idea):
    """Contract-declared result interface (audit R4): a probe contract may
    carry a top-level `required_outputs:` list naming the bundle files it
    produces. When present, validation is driven by the contract; when
    absent, the legacy 004-era interface applies unchanged."""
    c = idea_dir(idea) / 'probe_contract.yaml'
    if not c.exists():
        return []
    try:
        import yaml
        data = yaml.safe_load(c.read_text()) or {}
        req = data.get('required_outputs') or []
        return [str(x) for x in req if isinstance(x, (str,))]
    except Exception:
        return []


def bundle_complete(idea, bundle):
    """Single-sourced completion semantics for CI and record-result.
    Contract-mode (required_outputs declared): complete iff the summary
    status is the contract's terminal positive/negative pattern. Legacy:
    the 004-era rule the results workflow previously inlined."""
    try:
        s = json.loads((Path(bundle) / 'summary.json').read_text())
    except Exception:
        return False
    if _contract_required_outputs(idea):
        return s.get('status') in ('POSITIVE_PATTERN', 'NEGATIVE_PATTERN')
    return bool(s.get('study_complete') or s.get('phase_m_complete')
                or (s.get('phase') == 'B' and 'analysis' in s))


def validate_bundle(idea, bundle):
    """Deterministic results-bundle validation (E1). Single source of truth
    for CI (results-validate workflow) and record-result. Returns a list of
    failure strings; empty list = valid. Checks:
      1. core files present (summary.json, provenance.json,
         resolved_config.json, environment.txt, manifest/pair_manifest.csv)
      2. provenance.contract_blob == the CURRENT contract's git blob
         (results produced under a superseded contract never import)
      3. sha256(manifest/pair_manifest.csv) == the contract's frozen
         pair_manifest_sha256 (when the contract records one)
      4. summary.json sanity: parses, idea matches, phase in {M, B}
      5. every chunk manifest that lists sha256 entries verifies against
         the bundle files it names (phase B)
    """
    bundle = Path(bundle)
    fails = []
    req = _contract_required_outputs(idea)
    if req:  # contract-declared result interface
        core = sorted(set(req) | {'summary.json', 'provenance.json'})
    else:    # legacy 004-era interface, unchanged
        core = ['summary.json', 'provenance.json', 'resolved_config.json',
                'environment.txt', 'manifest/pair_manifest.csv']
    for rel in core:
        if not (bundle / rel).exists():
            fails.append(f'missing required bundle file: {rel}')
    if fails:
        return fails
    try:
        summary = json.loads((bundle / 'summary.json').read_text())
        prov = json.loads((bundle / 'provenance.json').read_text())
    except (json.JSONDecodeError, OSError) as e:
        return [f'unparseable bundle json: {e}']
    current = _contract_hash(idea_dir(idea))
    got = prov.get('contract_blob')
    if not current:
        fails.append('idea has no probe_contract.yaml to validate against')
    elif got != current:
        fails.append(f'contract blob mismatch: bundle produced under '
                     f'{str(got)[:12]}, current contract is {current[:12]} '
                     '(results from a superseded contract never import)')
    pinned_sha = _contract_field(idea, 'pair_manifest_sha256')
    if isinstance(pinned_sha, str) and len(pinned_sha) == 64:
        pf = bundle / 'manifest' / 'pair_manifest.csv'
        actual = sha256_of(pf) if pf.exists() else 'MISSING'
        if actual != pinned_sha:
            fails.append(f'pair_manifest.csv sha {actual[:12]} != contract '
                         f'pin {pinned_sha[:12]}')
    sid = str(summary.get('idea_id', ''))
    if f'{idea:03d}' not in sid:
        fails.append(f'summary idea_id {sid!r} does not name idea {idea:03d}')
    ph = summary.get('phase')
    if req:
        if not (isinstance(ph, str) and len(ph) == 1 and ph.isalpha()):
            fails.append(f'summary phase {ph!r} is not a single-letter phase')
    elif ph not in ('M', 'B'):
        fails.append(f'summary phase {ph!r} not in M/B')
    for cm in sorted(bundle.glob('chunks/*/chunk_manifest.json')):
        try:
            entries = json.loads(cm.read_text())
        except (json.JSONDecodeError, OSError) as e:
            fails.append(f'{cm.relative_to(bundle)}: unparseable: {e}')
            continue
        for rel, sha in (entries.get('sha256') or {}).items():
            f = bundle / rel
            try:
                inside = f.resolve().is_relative_to(bundle.resolve())
            except (OSError, ValueError):
                inside = False
            if not inside:
                fails.append(f'{cm.parent.name}: manifest path escapes bundle: {rel}')
                continue
            if not f.exists():
                fails.append(f'{cm.parent.name}: manifest names missing file {rel}')
            elif sha256_of(f) != sha:
                fails.append(f'{cm.parent.name}: sha mismatch for {rel}')
    return fails


def sha256_of(path):
    import hashlib
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def cmd_diversity(args):
    """Deterministic generation-diversity report (external-review adoption:
    measure the design_template / mechanism distribution BEFORE building any
    evolutionary machinery). Counts recurring design fields across all
    candidates of one charter (None = baseline) so the operator can see
    whether the scout is reusing one experimental grammar in different
    costumes. Read-only; no agent, no tokens."""
    from collections import Counter
    charter = getattr(args, 'charter', None) or None
    dirs = sorted(p for p in (ROOT/'ideas').glob('scout-*')
                  if _parse_scout_dir(p.name)[0] == charter)
    fields = ('design_template', 'mechanism_family', 'search_mode',
              'entry_point', 'track')
    counts = {f: Counter() for f in fields}
    titles = []
    n = 0
    for d in dirs:
        f = d/'candidates_all.json'
        if not f.exists():
            continue
        for c in json.loads(f.read_text()).get('candidates', []):
            n += 1
            titles.append(c.get('title', '')[:60])
            for k in fields:
                v = c.get(k)
                if v not in (None, '', []):
                    counts[k][str(v)] += 1
    scope = charter or 'baseline'
    print(f'Diversity report: charter={scope}, cycles={len(dirs)}, candidates={n}')
    for k in fields:
        if not counts[k]:
            continue
        total = sum(counts[k].values())
        print(f'\n{k} ({total} tagged):')
        for v, c in counts[k].most_common(8):
            bar = '#' * max(1, round(20*c/total))
            print(f'  {c:>3}  {bar:<20} {v[:70]}')
    top = counts['design_template'].most_common(1)
    if top and sum(counts['design_template'].values()) >= 6 and \
       top[0][1] / sum(counts['design_template'].values()) > 0.5:
        print('\nWARNING: one design template carries more than half of all '
              'candidates - generation may be reusing one experimental '
              'grammar in different costumes.')


def cmd_validate_bundle(args):
    fails = validate_bundle(args.idea, args.bundle)
    if fails:
        print(f'BUNDLE INVALID ({len(fails)} failure(s)):')
        for f in fails:
            print(' -', f)
        raise SystemExit(2)
    print('Bundle valid: core files, contract blob, manifest pin, and '
          'chunk manifests all check.')


def amend_contract(args):
    """Deterministically write the Phase-S selected gates and simulation hash
    into the contract's outputs_to_amend placeholders. No agent runs here: the
    amendment is a mechanical, reproducible transform of a validated summary.
    The contract blob changes, so the prior approval goes stale by design;
    review the diff, commit, then run approve-probe again."""
    contract = idea_dir(args.idea) / 'probe_contract.yaml'
    if not contract.exists():
        raise SystemExit('no probe_contract.yaml for this idea')
    summary_path = Path(args.bundle) / 'simulation_summary.json'
    if not summary_path.exists():
        raise SystemExit(f'{summary_path} not found')
    summary = json.loads(summary_path.read_text())
    sel, sha = summary.get('selected'), summary.get('simulation_output_sha256')
    if not sel or len(sel) != 3 or not sha:
        raise SystemExit('summary lacks selected [N, M, width] and sha256')
    text = contract.read_text()
    subs = (('minimum_contributing_patients_per_stratum', str(int(sel[0]))),
            ('minimum_voxels_per_patient_quantile_cell', str(int(sel[1]))),
            ('maximum_primary_ci_width', str(sel[2])),
            ('simulation_output_sha256', f'"{sha}"'))
    for key, value in subs:
        placeholder = f'{key}: "TO_BE_RECORDED_AFTER_PHASE_S"'
        if text.count(placeholder) != 1:
            raise SystemExit(f'expected exactly one placeholder for {key}; '
                             'already amended or contract drifted')
        text = text.replace(placeholder, f'{key}: {value}')
    contract.write_text(text)
    print(f'Amended {contract.relative_to(ROOT)} from {summary_path}:')
    for key, value in subs:
        print(f'  {key}: {value}')
    print('Prior approval is now stale (blob changed). Review the diff, '
          'commit, then approve-probe again before probe-build.')


def record_result(args):
    """E1: import a VALIDATED results bundle and only then raise scrutiny.
    The v1 single-file copy marked PROBED with zero validation and left the
    actual bundle gitignored -- the first at-scale result will not repeat
    that. Import = validate -> copy tree -> force-add (results/ is
    gitignored by default; entering history is a deliberate act) -> commit
    -> PROBED."""
    if not args.bundle:
        raise SystemExit('record-result now imports validated bundles: '
                         'record-result IDEA --bundle DIR  (the single-file '
                         'path is retired; see validate-bundle)')
    bundle = Path(args.bundle)
    fails = validate_bundle(args.idea, bundle)
    if fails:
        print(f'REFUSED: bundle failed validation ({len(fails)}):')
        for f in fails:
            print(' -', f)
        raise SystemExit(2)
    summary = json.loads((bundle / 'summary.json').read_text())
    dest = ROOT / 'probes' / f'{args.idea:03d}' / 'results' / bundle.name
    if dest.exists():
        raise SystemExit(f'{dest.relative_to(ROOT)} already exists; bundles '
                         'are immutable once imported.')
    shutil.copytree(bundle, dest)
    subprocess.run(['git', 'add', '-f', str(dest)], cwd=ROOT, check=True)
    subprocess.run(['git', 'commit', '-m',
                    f'idea {args.idea:03d}: validated results bundle '
                    f'{bundle.name} (phase {summary.get("phase")})'],
                   cwd=ROOT, check=True, capture_output=True)
    print(f'Imported {dest.relative_to(ROOT)} (committed).')
    ledger_mod.raise_scrutiny(
        f'idea-{args.idea:03d}', 'PROBED',
        note=f'validated bundle {bundle.name}, phase '
             f'{summary.get("phase")}, contract '
             f'{str(_contract_hash(idea_dir(args.idea)))[:12]}')
    ledger_mod.digest()



# --------------------------------------------------------------------------
# Debate: bounded alternating exchange between the two model families.
# Both sides read the whole transcript each round. Terminates on agreement,
# on max_rounds, or when a side declares the disagreement irreducible.
# --------------------------------------------------------------------------

def _taxonomy_block():
    lines = ['===== KILL CODE TAXONOMY (use one of these in the verdict block) =====']
    for code, desc in ledger_mod.TAXONOMY.items():
        lines.append(f'{code}: {desc}')
    return '\n'.join(lines)


def _debate_prompt(target, round_no, side, agent_name, other_name):
    transcript = read_text(target / 'debate.md') or '(no rounds yet)'
    base = build_prompt(f'debate_{side}', target)
    return f"""{base}

===== DEBATE STATE =====
You are {agent_name}. Your interlocutor is {other_name}.
This is round {round_no}. Do not restate agreement you already reached.

===== TRANSCRIPT SO FAR =====
{transcript}
"""


DEBATE_STATUSES = ('CONVERGED', 'IRREDUCIBLE DISAGREEMENT', 'CONCEDED', 'OPEN')


def _parse_rounds(target):
    """Return [(side, status), ...] in transcript order."""
    import re
    body = read_text(target / 'debate.md')
    out = []
    blocks = re.split(r'^## Round ', body, flags=re.M)[1:]
    for b in blocks:
        head = b.split('\n', 1)[0].upper()
        side = 'critic' if 'CRITIC' in head else ('proposer' if 'PROPOSER' in head else '?')
        status = None
        m = re.search(r'\*\*Status:\*\*\s*(.+)', b)
        if m:
            claimed = m.group(1).strip().upper()
            for st in DEBATE_STATUSES:
                if st in claimed:
                    status = st
                    break
        out.append((side, status))
    return out


def _debate_should_stop(target):
    """Termination requires BOTH sides. A unilateral CONVERGED is not consensus."""
    rounds = _parse_rounds(target)
    last = {}
    for side, status in rounds:
        if side in ('critic', 'proposer'):
            last[side] = status
    if len(last) < 2:
        return None
    c, p = last['critic'], last['proposer']
    if {c, p} <= {'CONVERGED', 'CONCEDED'}:
        return f'both sides settled (critic={c}, proposer={p})'
    if 'IRREDUCIBLE DISAGREEMENT' in (c, p) and None not in (c, p):
        # one side declared it; the other has now had its turn to respond
        # Only ONE side need declare it. Requiring both to agree that they
        # disagree would just manufacture a different kind of false consensus.
        return ('one side declared the disagreement irreducible; '
                'the other side has responded')
    return None


def debate(args):
    cfg = load_agent_config()
    dcfg = cfg.get('debate', {})
    proposer = effective_agent(dcfg.get('proposer', 'claude'), cfg)
    critic = effective_agent(dcfg.get('critic', 'codex'), cfg)
    max_rounds = args.rounds or int(dcfg.get('max_rounds', 3))
    if proposer == critic:
        raise SystemExit('debate.proposer and debate.critic must differ; '
                         'a model debating itself is theatre.')

    _require_clean_tree('debate')
    target = stage_target('critique', args.idea)
    t = target / 'debate.md'
    if not t.exists():
        t.write_text('# Debate transcript\n\n')

    _pre = _debate_should_stop(target)
    if _pre:
        print('Already settled: ' + _pre)
        return _close_debate(target, critic, args.idea)

    for r in range(1, max_rounds + 1):
        for side, agent, other in (('critic', critic, proposer),
                                   ('proposer', proposer, critic)):
            print(f'\n--- round {r}, {side} ({agent}) ---')
            p = target / f'prompt_debate_r{r}_{side}.md'
            p.write_text(_debate_prompt(target, r, side, agent, other))
            run_agent(p, agent, stage=f'debate-{side}')
            _check_scope('debate')
        # Termination is evaluated only at the end of a full round, so a
        # unilateral declaration never ends the exchange -- the other side
        # always gets to respond to it.
        reason = _debate_should_stop(target)
        if reason:
            print(f'Stopping: {reason}.')
            return _close_debate(target, critic, args.idea)
    print(f'\nReached max_rounds={max_rounds} without convergence.')
    _close_debate(target, critic, args.idea)


def _close_debate(target, critic, idea=None):
    p = write_prompt('debate_summary', target)
    p.write_text(p.read_text() + '\n' + _taxonomy_block() + '\n')
    run_agent(p, critic, stage='debate-summary')
    _check_scope('debate')
    idea = idea or load_state().get('selected_idea')
    if idea:
        ledger_mod.raise_scrutiny(f'idea-{int(idea):03d}', 'DEBATED')
        _apply_consensus_verdict(idea)
        ledger_mod.digest()
    c = target / 'consensus.md'
    if c.exists():
        print('\n' + read_text(c)[:2000])
    print('\n--- READ debate.md AND consensus.md YOURSELF BEFORE PROCEEDING ---')


# --------------------------------------------------------------------------
# File-scope guard: which stages may touch which paths. Enforced by git,
# not by asking the model nicely.
# --------------------------------------------------------------------------

STAGE_SCOPE = {
    'critique':    ['ideas/', 'evidence/'],
    'debate':      ['ideas/'],
    'feasibility': ['ideas/', 'evidence/'],
    'interpret':   ['ideas/', 'evidence/', 'portfolio/'],
    'revise':      ['ideas/'],
    'probe-plan':  ['ideas/', 'probes/'],
    'scout':       ['ideas/'],
    'wide-scout':  ['ideas/'],
    'fiction-scout':   ['ideas/'],
    'fiction-extract': ['ideas/'],
    'fiction-refine':  ['ideas/'],
    'novelty-audit':   ['ideas/'],
    'librarian':       ['ideas/'],
    'actioner':        ['ideas/'],
    'keystone':        ['ideas/'],
    'probe-code':      ['ideas/', 'probes/'],
    'probe-build':     ['ideas/', 'probes/'],
    'context-memo':    ['ideas/'],
    'reconcile':       ['ideas/'],
    'interpret-build':  ['ideas/', 'evidence/', 'portfolio/'],
}


def _touched_files():
    r = subprocess.run(['git', 'status', '--porcelain'], cwd=ROOT,
                       capture_output=True, text=True)
    return [ln[3:].strip().strip('"') for ln in r.stdout.splitlines() if ln.strip()]


def _require_clean_tree(stage):
    """A dirty tree makes it impossible to attribute changes to this stage."""
    if os.environ.get('SCOUT_SKIP_CLEAN_CHECK'):
        return
    dirty = _touched_files()
    if dirty:
        raise SystemExit(
            f"Working tree is not clean; cannot attribute changes to the "
            f"{stage!r} stage.\n  Uncommitted: " + ', '.join(dirty[:10])
            + ("..." if len(dirty) > 10 else "")
            + "\n  Commit or stash first:  git add -A && git commit -m 'wip'"
        )


def _check_scope(stage):
    allowed = STAGE_SCOPE.get(stage)
    if not allowed:
        return
    bad = [f for f in _touched_files()
           if not any(f.startswith(a) for a in allowed)]
    if bad:
        msg = ['', '!! SCOPE VIOLATION -- this stage may only touch '
               + ', '.join(allowed)]
        for f in bad:
            msg.append('   modified outside scope: ' + f)
        msg.append('   Review with `git diff`; revert with `git checkout -- <file>`.')
        msg.append('   Nothing is reverted automatically -- that could destroy your own work.')
        raise SystemExit('\n'.join(msg))


def status(_):
    print(json.dumps(load_state(), indent=2))
    entries = ledger_mod.load()
    ideas = {k: v for k, v in entries.items() if k.startswith('idea-')}
    from collections import Counter
    by_status = Counter(e.get('status', 'UNKNOWN') for e in ideas.values())
    print('\nIdeas (ledger-derived; the CSV view is retired -- external '
          'review found it materially stale):')
    for st, n in sorted(by_status.items()):
        print(f'  {st:<12} {n}')
    for k, e in sorted(ideas.items()):
        if e.get('status') in ('ACTIVE', 'SHORTLISTED') or e.get('scrutiny') == 'PROBED':
            print(f"  {k}: {e.get('status','?'):<12} scrutiny={e.get('scrutiny','-'):<10} "
                  f"{(e.get('title') or e.get('claim') or '')[:60]}")


BRIEF = ROOT/'evidence'/'portfolio_brief.md'


def _extract_section(body, header):
    import re
    m = re.search(rf'^## {header}\s*$(.*?)(?=^## |\Z)', body, flags=re.M | re.S)
    return m.group(1).strip() if m else ''


def _brief_path(charter):
    """A named charter's brief path, UNCONDITIONALLY: if no scoped brief
    exists yet (a brand-new charter's first cycle), the missing path
    yields empty context via read_text -- never the baseline brief.
    External review (2026-08-18) reproduced baseline verdicts leaking
    into a fresh charter's scout prompt under the old fallback."""
    charter = _norm_charter(charter)
    if charter:
        return ROOT/'evidence'/f'portfolio_brief_{charter}.md'
    p = ROOT/'evidence'/'portfolio_brief_baseline.md'
    return p if p.exists() else BRIEF


def write_portfolio_brief(max_ideas=8, max_chars=1500):
    """Rich context on ACTIONABLE ideas (those with a debate consensus and a
    live status) for portfolio-aware scouting: the verdict, its unblock
    conditions, and unresolved questions. The digest stays the one-line index;
    this is the detail tier for ideas a scout might revive or recombine."""
    entries = ledger_mod.load()
    charters = {None}
    for d in (ROOT/'ideas').glob('[0-9][0-9][0-9]'):
        charters.add(charter_for_target(d))
    if (ROOT/'charters').exists():
        for p in (ROOT/'charters').glob('*/CHARTER.md'):
            charters.add(p.parent.name)  # registered charters always get a brief
    out = None
    for scope in sorted(charters, key=lambda c: (c is not None, c or '')):
        p = _write_brief_one(entries, scope, max_ideas, max_chars)
        if scope is None:
            out = p
    return out or BRIEF


def _write_brief_one(entries, scope, max_ideas, max_chars):
    label = scope or 'baseline'
    lines = [f'# Portfolio brief -- charter: {label} (auto-generated; run `python scout.py brief`)', '',
             'Actionable ideas OF THIS CHARTER with debate verdicts (evaluative',
             'framing never crosses charters; facts cross via',
             'evidence/cross_charter_index.md). A revival/recombination',
             'candidate MUST cite the specific condition below that has changed.', '']
    dirs = sorted((ROOT/'ideas').glob('[0-9][0-9][0-9]'), reverse=True)
    n = 0
    for d in dirs:
        if n >= max_ideas:
            break
        if charter_for_target(d) != scope:
            continue
        cpath = d/'consensus.md'
        if not cpath.exists():
            continue
        lid = f'idea-{d.name}'
        e = entries.get(lid, {})
        if e.get('status') == 'REJECTED':
            continue  # killed ideas stay in the digest kill table, not here
        body = read_text(cpath)
        rec = _extract_section(body, 'Recommendation')
        unres = _extract_section(body, 'Unresolved')
        import re
        unres_heads = re.findall(r'^### (.+)$', unres, flags=re.M)
        title = ''
        card = d/'idea_card.json'
        if card.exists():
            try:
                title = json.loads(card.read_text()).get('title', '')
            except json.JSONDecodeError:
                pass
        chunk = [f"## {lid} [{e.get('status','?')}] -- {title}", '']
        if rec:
            chunk += ['**Verdict:** ' + ' '.join(rec.split())[:max_chars], '']
        if unres_heads:
            chunk += ['**Unresolved:** ' + '; '.join(unres_heads)[:400], '']
        lines += chunk
        n += 1
    if n == 0:
        lines += ['(No ideas of this charter with debate consensus yet.)', '']
    BRIEF.parent.mkdir(parents=True, exist_ok=True)
    target = BRIEF if scope is None else BRIEF.parent/f'portfolio_brief_{scope}.md'
    target.write_text('\n'.join(lines) + '\n')
    if scope is None:
        (BRIEF.parent/'portfolio_brief_baseline.md').write_text('\n'.join(lines) + '\n')
    return target


def brief_cmd(_args):
    print(write_portfolio_brief().relative_to(ROOT))


# ==========================================================================
# Cycle orchestration: multi-track scouting with checkpoint/resume.
#
# Design notes:
#  * Every completed stage is committed to git immediately. The commit IS the
#    checkpoint: a rate limit, timeout, or 6-hour Actions kill costs one
#    stage, and it keeps the clean-tree guard satisfied between stages.
#  * A failed stage's partial output is committed too (marked FAILED) so no
#    agent work is ever lost and `resume` starts from a clean tree.
#  * Fiction refine runs on the OPPOSITE model family from the fiction writer:
#    a model may half-recognise its own fictional register, so the cross-model
#    handoff is what makes the persona separation real.
# ==========================================================================

TRACKS = ('baseline', 'wide', 'fiction')


def seed_draw(rng=None, concepts_override=None):
    rng = rng or random.Random()
    seeds = json.loads(read_text(SEEDS) or '{}')
    concepts = list(seeds.get('concepts', []))
    entries = ledger_mod.load()
    for e in entries.values():
        concepts += [t for t in e.get('tags', []) if isinstance(t, str)]
    concepts = sorted(set(c for c in concepts if c)) or ['vessel caliber', 'reconstruction kernel']
    datasets = seeds.get('datasets') or ['CT-RATE (public chest CT + reports)']
    twists = seeds.get('twists') or ['The two measurements disagree, and the disagreement is the signal.']
    if concepts_override:
        chosen, source = list(concepts_override)[:2], 'human'
    else:
        chosen, source = rng.sample(concepts, min(2, len(concepts))), 'random'
    ds = rng.choice(datasets)
    if isinstance(ds, str):
        ds = {'name': ds}
    models = seeds.get('models') or []
    model = rng.choice(models) if models else None
    return {
        'fiction_version': 2,
        'concepts': chosen,
        'source': source,
        'dataset': ds,
        'model': model,
        'twist': rng.choice(twists),
        'drawn_at': datetime.now(timezone.utc).isoformat(timespec='seconds'),
    }


def _fiction_writer_and_refiner(cfg, cycle_no=None):
    writer = cfg.get('roles', {}).get('fiction_scout') or cfg.get('roles', {}).get('scout', 'claude')
    writer = effective_agent(writer, cfg, cycle_no)
    pair = cfg.get('rotation', {}).get('pair', ['claude', 'codex'])[:2]
    refiner = pair[1] if writer == pair[0] else pair[0]
    return writer, refiner


def _cycle_stage_list(tracks):
    stages = []
    if 'baseline' in tracks:
        stages.append(('scout', 'role'))
    if 'wide' in tracks:
        stages.append(('wide_scout', 'role'))
    if 'fiction' in tracks:
        stages += [('fiction_scout', 'fiction_writer'),
                   ('fiction_extract', 'fiction_writer'),
                   ('fiction_refine', 'fiction_refiner')]
    stages.append(('merge', 'python'))
    stages.append(('novelty_audit', 'role'))
    stages.append(('backlog', 'python'))
    return stages


def _git(*cmd, check=True):
    return subprocess.run(['git', *cmd], cwd=ROOT, capture_output=True, text=True, check=check)


def _push_checkpoint():
    """Durability for stage checkpoints on ephemeral runners: a local commit
    that dies with the runner was never a checkpoint. Push after every stage
    commit in CI; retry once through a rebase for pushes racing the human or
    another workflow; a checkpoint that cannot be pushed is a FAILED stage,
    loudly -- never silently swallowed."""
    r = _git('push', check=False)
    if r.returncode == 0:
        return
    rb = _git('pull', '--rebase', check=False)
    if rb.returncode != 0:
        _git('rebase', '--abort', check=False)
        raise SystemExit('Checkpoint rebase conflicted; aborted without '
                         'committing a conflicted tree (fail-closed):\n'
                         + (rb.stderr or rb.stdout or '')[-800:])
    r = _git('push', check=False)
    if r.returncode != 0:
        raise SystemExit('Checkpoint push failed after rebase retry:\n'
                         + (r.stderr or r.stdout or '')[-800:])


def _commit_all(message):
    _git('add', '-A')
    r = _git('diff', '--cached', '--quiet', check=False)
    if r.returncode == 0:
        return False  # nothing to commit
    _git('commit', '-q', '-m', message)
    if os.environ.get('SCOUT_CI'):
        _push_checkpoint()
    return True


# A stage "succeeding" while producing nothing is how cycle 005 shipped an
# empty candidate pool to the audit. Exit code 0 is not success; the artifact is.
STAGE_ARTIFACTS = {
    'scout': 'scout_candidates.json',
    'wide_scout': 'wide_candidates.json',
    'fiction_scout': 'fiction_story.md',
    'fiction_extract': 'fiction_pitch.md',
    'fiction_refine': 'fiction_candidates.json',
    'novelty_audit': ('novelty_audit.md', 'novelty_manifest.json'),
    'keystone': 'keystone_screen.md',
    'probe_review': 'probe_review.md',
    'interpret_review': 'interpret_review.md',
    'librarian': 'librarian_report.md',
    'actioner': 'actions.md',
    'critique': 'critique.md',
    'feasibility': 'feasibility.md',
    'context_memo': 'context_memo.md',
    'reconcile': 'reconciliation.md',
}


def _validate_novelty_manifest(f):
    try:
        d = json.loads(f.read_text())
    except json.JSONDecodeError as e:
        raise SystemExit(f'novelty_manifest.json is not valid JSON: {e}')
    if not (isinstance(d.get('queries'), list) and d.get('queries')):
        raise SystemExit('novelty_manifest.json: "queries" must be a non-empty list -- '
                         'an audit without recorded queries is not a reproducible search.')
    if not isinstance(d.get('neighbors'), list):
        raise SystemExit('novelty_manifest.json: "neighbors" must be a list.')
    for n in d['neighbors']:
        if not (isinstance(n, dict) and n.get('identifier') and n.get('access')):
            raise SystemExit('novelty_manifest.json: every neighbor needs "identifier" and "access".')


def _require_artifact(stage, target):
    expected = STAGE_ARTIFACTS.get(stage)
    if not expected:
        return
    names = (expected,) if isinstance(expected, str) else expected
    for name in names:
        if not (target / name).exists():
            raise SystemExit(
                f"Stage {stage!r} exited cleanly but did not write {name!r}. "
                f"Treating as failed. Check {target.relative_to(ROOT)}/log_{stage}.txt "
                f"for what the agent did instead.")
    if stage == 'novelty_audit':
        _validate_novelty_manifest(target / 'novelty_manifest.json')


def _validate_card(card):
    """Deterministic semantic validation against the production schema.
    Returns None if valid, else a short error string. Existence-level
    artifact contracts caught empty stages; this catches shape drift --
    the scoring-representation change broke ranking silently for weeks
    because nothing validated structure."""
    try:
        import jsonschema
    except ImportError:
        return None  # validation is best-effort if the dep is absent locally
    try:
        schema = json.loads(read_text(ROOT/'templates'/'idea_card.schema.json'))
        jsonschema.validate(card, schema)
    except jsonschema.ValidationError as e:
        path = '.'.join(str(x) for x in e.absolute_path) or '(root)'
        return f'{path}: {e.message[:160]}'
    except Exception as e:
        return f'schema error: {e}'
    return None


def _normalize_candidate(card):
    """Normalize KNOWN legacy aliases to the canonical schema shape, in
    place. Returns a list of fix descriptions (empty if nothing changed).

    P0.1 (2026-08-14): cycle 012 emitted {"score": N, "why": ...} where the
    schema mandates {"value": N, "why": ...}, plus keystone_evidence: null
    against a string-only schema. The schema correctly caught the drift and
    is deliberately NOT loosened. Chain: prompt specifies the canonical
    shape (docs/SCORING_RUBRIC.md) -> this parser maps known aliases onto
    it -> _validate_card validates the canonical form -> the
    production-shaped regression fixture in tests keeps all three aligned.
    Anything not on the known-alias list still fails validation."""
    fixes = []
    scores = card.get('scores')
    if isinstance(scores, dict):
        for k, v in scores.items():
            if (isinstance(v, dict) and 'value' not in v
                    and isinstance(v.get('score'), (int, float))):
                v['value'] = v.pop('score')
                fixes.append(f'scores.{k}: score->value')
    if 'keystone_evidence' in card and card['keystone_evidence'] is None:
        # Schema permits absence but not null. Dropping the key lets the
        # existing INSPECTED_TRUE-without-evidence demotion in the merge
        # loop apply honestly instead of inventing evidence.
        del card['keystone_evidence']
        fixes.append('keystone_evidence: null->absent')
    return fixes


CANDIDATE_FILES = {'baseline': 'scout_candidates.json',
                   'wide': 'wide_candidates.json',
                   'fiction': 'fiction_candidates.json'}


def _merge_candidates(target, tracks, cycle_no):
    merged, notes = [], {}
    for track in tracks:
        f = target / CANDIDATE_FILES[track]
        if not f.exists():
            notes[track] = 'no candidate file produced'
            continue
        try:
            data = json.loads(f.read_text())
        except json.JSONDecodeError:
            notes[track] = 'candidate file was not valid JSON'
            continue
        if data.get('no_testable_kernel'):
            notes[track] = f"NO_TESTABLE_KERNEL: {data['no_testable_kernel']}"
        if track == 'fiction' and data.get('adjacent_question'):
            seed = json.loads(read_text(target/'fiction_seed.json') or '{}')
            ledger_mod.append({
                'ledger_id': _scout_lid(_active_charter(), cycle_no, 'fadj'),
                'title': 'Fiction near-miss (not a candidate)',
                'claim': str(data['adjacent_question'])[:600],
                'track': 'fiction', 'status': 'PAUSED', 'scrutiny': 'SCOUTED',
                'seed_source': seed.get('source', ''),
                'fiction_version': seed.get('fiction_version', 1),
                'notes': 'adjacent question banked from an honorable exit; librarian/scout may adopt',
                'source': str(target.relative_to(ROOT)),
            })
            notes['fiction_adjacent'] = str(data['adjacent_question'])[:200]
        cands = data.get('candidates', data if isinstance(data, list) else [])
        skipped = 0
        for c in cands:
            if isinstance(c, dict):
                if not (c.get('title') and c.get('question')):
                    skipped += 1  # stubs/drop-notes are not candidates
                    continue
                c.setdefault('track', track)
                for soft in ('design_template', 'search_mode'):
                    if not c.get(soft):
                        notes[f'{soft}_missing'] = notes.get(f'{soft}_missing', 0) + 1
                if c.get('search_mode') == 'C' and not isinstance(
                        c.get('mode_c_priority_score'), (int, float)):
                    notes['mode_c_score_missing'] = notes.get('mode_c_score_missing', 0) + 1
                fixes = _normalize_candidate(c)
                if fixes:
                    notes.setdefault('normalized', []).append(
                        f"{track}: {c.get('title','')[:50]} -- {', '.join(fixes)}")
                err = _validate_card(c)
                if err:
                    notes.setdefault('schema_rejected', []).append(
                        f"{track}: {c.get('title','')[:50]} -- {err}")
                    continue
                if c.get('keystone_status') == 'INSPECTED_TRUE' and not c.get('keystone_evidence'):
                    c['keystone_status'] = 'NOT_INSPECTED'
                    c['keystone_demotion'] = 'claimed INSPECTED_TRUE without keystone_evidence'
                    notes.setdefault('keystone_demotions', []) if isinstance(notes.get('keystone_demotions'), list) else None
                    notes['keystone_demotions'] = notes.get('keystone_demotions', []) + [c.get('title', '')[:60]]
                merged.append(c)
        if skipped:
            notes[f'{track}_skipped_stubs'] = skipped
    for track in tracks:
        rej = [x for x in notes.get('schema_rejected', []) if x.startswith(track + ':')]
        f = target / CANDIDATE_FILES[track]
        if rej and f.exists() and not any(c.get('track') == track for c in merged):
            raise SystemExit(
                f'All {track} candidates failed schema validation:\n  '
                + '\n  '.join(rej)
                + '\n  Fix the generating prompt or the schema; nothing merged from this track.')
    out = {'cycle': cycle_no, 'charter': _active_charter(), 'tracks': list(tracks),
           'notes': notes, 'candidates': merged}
    for c in merged:
        c.setdefault('charter', _active_charter())
    (target / 'candidates_all.json').write_text(json.dumps(out, indent=2, ensure_ascii=False) + '\n')
    for i, c in enumerate(merged, 1):
        ledger_mod.append({
            'ledger_id': _scout_lid(_active_charter(), cycle_no, f'c{i:02d}'),
            'title': c.get('title', ''),
            'claim': c.get('deliverable_sentence') or c.get('question', ''),
            'track': c.get('track', 'baseline'),
            'dataset': (c.get('dataset', {}) or {}).get('name', '') if isinstance(c.get('dataset'), dict) else str(c.get('dataset', '')),
            'status': 'SCOUT_ONLY',
            'scrutiny': 'SCOUTED',
            'scores_mean': _mean_score(c),
            'design_template': c.get('design_template', ''),
            'parent_ids': c.get('parent_ids', []),
            'seed_source': (json.loads(read_text(target/'fiction_seed.json') or '{}').get('source', '')
                            if c.get('track') == 'fiction' else ''),
            'fiction_version': (json.loads(read_text(target/'fiction_seed.json') or '{}').get('fiction_version', 1)
                                if c.get('track') == 'fiction' else None),
            'source': str(target.relative_to(ROOT)),
        })
    ledger_mod.digest()
    print(f'Merged {len(merged)} candidate(s) across {len(tracks)} track(s) -> candidates_all.json')
    for track, note in notes.items():
        print(f'  note[{track}]: {note}')


def _print_plan(cycle_no, tracks, stages, cfg):
    print(f'Cycle {cycle_no:03d} plan  (tracks: {", ".join(tracks)})')
    writer, refiner = _fiction_writer_and_refiner(cfg, cycle_no)
    for name, kind in stages:
        if kind == 'python':
            agent = '(python, no agent)'
        elif kind == 'fiction_writer':
            agent = writer
        elif kind == 'fiction_refiner':
            agent = refiner
        else:
            role = cfg.get('roles', {}).get(name, cfg.get('roles', {}).get('scout', 'claude'))
            agent = effective_agent(role, cfg, cycle_no)
        print(f'  {name:<16} -> {agent}')
    if 'fiction' in tracks:
        print('  sample seed draw:', json.dumps(seed_draw(random.Random(cycle_no))))
    rot = cfg.get('rotation', {})
    if rot.get('enabled'):
        print(f'  rotation: enabled (cycle parity {"odd -> swapped" if cycle_no % 2 else "even -> normal"})')


def _run_cycle_stage(name, kind, target, cfg, cycle_no):
    if name == 'merge':
        tracks = load_state()['cycle']['tracks']
        _merge_candidates(target, tracks, cycle_no)
        return
    if name == 'backlog':
        _sync_backlog()
        ledger_mod.digest()
        rows = _ranked_backlog()
        print(f'Backlog now holds {len(rows)} candidate(s); top of queue: '
              + (', '.join(f'{s:03d}-C{c}' for s, c, _ in rows[:5]) or '(empty)'))
        return
    if name == 'fiction_scout':
        override = load_state().get('cycle', {}).get('seed_concepts')
        seed = seed_draw(random.Random(), concepts_override=override)
        (target / 'fiction_seed.json').write_text(json.dumps(seed, indent=2) + '\n')
    writer, refiner = _fiction_writer_and_refiner(cfg, cycle_no)
    agent = {'fiction_writer': writer, 'fiction_refiner': refiner}.get(kind)
    p = write_prompt(name, target)
    run_agent(p, agent, stage=name.replace('_', '-'),
              log_path=target / f'log_{name}.txt')
    _check_scope(name.replace('_', '-'))
    _require_artifact(name, target)


def _cycle_loop(cycle_no, target, tracks, cfg):
    s = load_state()
    stages = _cycle_stage_list(tracks)
    for name, kind in stages:
        st = s['cycle']['stages'].get(name)
        if st == 'done':
            print(f'[skip] {name} already done')
            continue
        s['cycle']['stages'][name] = 'running'
        save_state(s)
        _commit_all(f'cycle {cycle_no:03d}: start {name}')
        try:
            _run_cycle_stage(name, kind, target, cfg, cycle_no)
        except SystemExit as e:
            s = load_state()
            s['cycle']['stages'][name] = 'failed'
            save_state(s)
            _commit_all(f'cycle {cycle_no:03d}: {name} FAILED (partial output preserved)')
            print(f'\nStage {name!r} failed: {e}')
            print('Work so far is committed. Continue later with:\n  python scout.py resume')
            raise SystemExit(1)
        s = load_state()
        s['cycle']['stages'][name] = 'done'
        save_state(s)
        _commit_all(f'cycle {cycle_no:03d}: {name} done')
        print(f'[done] {name} (checkpoint committed)')
    s = load_state()
    s['cycle']['finished'] = datetime.now(timezone.utc).isoformat(timespec='seconds')
    save_state(s)
    _commit_all(f'cycle {cycle_no:03d}: complete')
    print(f'\nCycle {cycle_no:03d} complete. Review {target.relative_to(ROOT)}/candidates_all.json '
          f'and novelty_audit.md, then shortlist:\n  python scout.py shortlist {cycle_no} <n> [--track TRACK]')


DESIGN_TEMPLATES = ('natural-paired', 'cross-reconstruction', 'regional-removal',
                    'regional-substitution', 'representation-erasure',
                    'counterfactual-synthesis', 'conditional-observational',
                    'longitudinal-within-subject', 'cross-model-disagreement',
                    'model-output-perturbation')


def write_run_provenance(target, tracks, seed_concepts=None):
    """Record (never pin) everything a later comparison must stratify by:
    the treatment is allowed to improve under us, but not silently."""
    import hashlib as _h
    def ver(cmd):
        try:
            r = subprocess.run(cmd, capture_output=True, text=True, check=False)
        except (FileNotFoundError, OSError):
            return 'not installed'
        out = (r.stdout or r.stderr or '').strip()
        return out.splitlines()[0] if out else 'unknown'
    prov = {
        'timestamp': datetime.now(timezone.utc).isoformat(timespec='seconds'),
        'git_commit': subprocess.run(['git', 'rev-parse', 'HEAD'], capture_output=True,
                                     text=True, check=False).stdout.strip(),
        'claude_cli': ver(['claude', '--version']),
        'codex_cli': ver(['codex', '--version']),
        'tracks': list(tracks),
        'seed_concepts': seed_concepts,
        'prompt_hashes': {f.name: _h.sha256(f.read_bytes()).hexdigest()[:16]
                          for f in sorted((ROOT/'orchestrator'/'prompts').glob('*.md'))},
        'agents_toml_hash': _h.sha256((ROOT/'AGENTS.toml').read_bytes()).hexdigest()[:16],
    }
    (target/'run_provenance.json').write_text(json.dumps(prov, indent=2) + '\n')


def cycle(args):
    cfg = load_agent_config()
    tracks = [t.strip() for t in (args.tracks or 'baseline').split(',') if t.strip()]
    bad = [t for t in tracks if t not in TRACKS]
    if bad:
        raise SystemExit(f'Unknown track(s): {", ".join(bad)}. Known: {", ".join(TRACKS)}')
    s = load_state()
    charter = getattr(args, 'charter', None) or None
    charter_path(charter)  # existence check before anything spends
    pending = s.get('cycle') and any(v != 'done' for v in s['cycle']['stages'].values())
    if charter:
        n = s.setdefault('charters', {}).setdefault(charter, {}).setdefault('next_scout', 1)
    else:
        n = s['next_scout']
    if args.dry_run:
        if pending:
            print(f"Note: cycle {s['cycle']['scout']:03d} is unfinished; "
                  "a real run with --resume-or-new will resume it.")
        _print_plan(n, tracks, _cycle_stage_list(tracks), cfg)
        return
    if args.resume_or_new and pending:
        print('Unfinished cycle found; resuming it instead of starting a new one.')
        return resume(args)
    _require_clean_tree('cycle')
    _check_family_opposition(cfg, n)
    d = scout_dir(n, charter)
    d.mkdir(parents=True, exist_ok=False)
    cid = f'{charter}-{n:03d}' if charter else f'{n:03d}'
    (d / 'README.md').write_text(
        f'# Scouting cycle {cid}\n\nTracks: {", ".join(tracks)}\n'
        + (f'Charter: {charter} (charters/{charter}/CHARTER.md; scores are scoped '
           f'to this charter and not comparable across charters)\n' if charter else ''))
    if not ledger_mod.LEDGER.exists():
        print('Ledger absent; running first-time migration from existing ideas.')
        ledger_mod.migrate()
    ledger_mod.digest()
    write_portfolio_brief()
    if charter:
        s['charters'][charter]['next_scout'] = n + 1
    else:
        s['next_scout'] = n + 1
    s['active_cycle'] = n  # rotation parity runs on the charter's own counter
    s['cycle'] = {'scout': n, 'charter': charter, 'tracks': tracks,
                  'seed_concepts': ([x.strip() for x in args.seed_concepts.split(',')][:2]
                                    if getattr(args, 'seed_concepts', None) else None),
                  'started': datetime.now(timezone.utc).isoformat(timespec='seconds'),
                  'stages': {name: 'pending' for name, _ in _cycle_stage_list(tracks)}}
    save_state(s)
    write_run_provenance(d, tracks, s['cycle'].get('seed_concepts'))
    _commit_all(f'cycle {cid}: begin (tracks: {", ".join(tracks)})')
    _cycle_loop(n, d, tracks, cfg)


def resume(_args):
    s = load_state()
    c = s.get('cycle')
    if not c:
        raise SystemExit('No cycle recorded. Start one with: python scout.py cycle --tracks baseline')
    if all(v == 'done' for v in c['stages'].values()):
        print(f"Cycle {c['scout']:03d} already complete.")
        return
    n = c['scout']
    s['active_cycle'] = n
    save_state(s)
    _require_clean_tree('resume')
    _check_family_opposition(load_agent_config(), n)
    ch = c.get('charter')
    cid = f'{ch}-{n:03d}' if ch else f'{n:03d}'
    print(f"Resuming cycle {cid} (tracks: {', '.join(c['tracks'])})")
    for name, st in c['stages'].items():
        print(f'  {name:<16} {st}')
    _cycle_loop(n, scout_dir(n, ch), c['tracks'], load_agent_config())


# ==========================================================================
# Post-scout pipeline: shortlist the strongest candidates of the latest
# completed cycle and drive each through critique/debate, phone-triggerable
# via the idea-pipeline workflow. Idempotent: re-running skips candidates
# already shortlisted and stages whose artifacts already exist, so the same
# button doubles as resume after a failure or job kill.
# ==========================================================================



def _audit_verdicts(target):
    """Parse the summary table of novelty_audit.md -> {merged_candidate_no: verdict}.

    Robust to model formatting drift: descriptive first cells, extra columns,
    and per-track renumbering (W1.. for wide, F1.. for fiction) are all
    accepted. W/F indices are mapped onto merged candidates_all order using
    the per-track counts."""
    import re
    body = read_text(target/'novelty_audit.md')
    if not body:
        return {}
    offsets = {'C': 0, 'W': 0, 'F': 0}
    try:
        cands = json.loads(read_text(target/'candidates_all.json') or '{}').get('candidates', [])
        n_base = sum(1 for c in cands if c.get('track', 'baseline') == 'baseline')
        n_wide = sum(1 for c in cands if c.get('track') == 'wide')
        offsets = {'C': 0, 'W': n_base, 'F': n_base + n_wide}
    except json.JSONDecodeError:
        pass
    out = {}
    for line in body.splitlines():
        if not line.lstrip().startswith('|'):
            continue
        cells = [c.strip().strip('`').strip('*') for c in line.strip().strip('|').split('|')]
        if not cells:
            continue
        m = re.match(r'([CWF])\s*-?\s*(\d+)\b', cells[0])
        if not m:
            continue
        verdict = next((c for c in cells[1:] if c in VALID_VERDICTS), None)
        if verdict:
            out[offsets.get(m.group(1), 0) + int(m.group(2))] = verdict
    return out


# Rubric weights (docs/SCORING_RUBRIC.md). Used to VALIDATE the card's own
# priority_score; regret/evaluation_readiness are reported outside the score.
MODE_C_WEIGHTS = {'mechanism_clarity': 0.30, 'identifiability': 0.25,
                  'interest': 0.20, 'medical_relevance': 0.15, 'clarity': 0.10}
RUBRIC_WEIGHTS = {
    'feasibility': 0.20, 'identifiability': 0.15, 'medical_relevance': 0.15,
    'prior_legwork': 0.10, 'interest': 0.10, 'clarity': 0.10,
    'negative_result_value': 0.10, 'data_readiness': 0.05,
    'novelty_confidence': 0.05,
}


def _score_value(v):
    """Scores appear as bare numbers (legacy) or {value, why} objects."""
    if isinstance(v, (int, float)):
        return float(v)
    if isinstance(v, dict) and isinstance(v.get('value'), (int, float)):
        return float(v['value'])
    return None


def _ranking_score(card):
    """Ranking score for a candidate card.

    Preference order (post-review fix -- the old implementation summed bare
    numbers and returned 0.0 for every production card once scores became
    {value, why} objects, silently degrading backlog order for weeks):
      1. The card's own priority_score, ACCEPTED ONLY IF it agrees (±0.25)
         with a recomputation from the rubric weights over its nested scores.
      2. The rubric-weighted recomputation itself.
      3. Unweighted mean over whatever score values exist.
    """
    scores = card.get('scores') or {}
    vals = {k: _score_value(v) for k, v in scores.items()}
    vals = {k: v for k, v in vals.items() if v is not None}
    mode_c = (card.get('search_mode') == 'C'
              or isinstance(card.get('mode_c_priority_score'), (int, float)))
    weights = MODE_C_WEIGHTS if mode_c else RUBRIC_WEIGHTS
    ps = card.get('mode_c_priority_score') if mode_c else card.get('priority_score')
    weighted = None
    if all(k in vals for k in weights):
        weighted = sum(weights[k] * vals[k] for k in weights)
    # Trust policy (consolidation, 2026-08-16, external review finding):
    # the rank is ALWAYS the deterministic rubric recomputation. The
    # model-authored priority score is never returned -- the old +/-0.25
    # acceptance made a self-score load-bearing, contradicting the standing
    # rule that self-scores are advisory. The authored value survives only
    # as an arithmetic cross-check others can read.
    if weighted is not None:
        return weighted
    return sum(vals.values()) / len(vals) if vals else 0.0


# The name _mean_score is historical (it stopped computing a mean long ago);
# callers and the ledger field name migrate in the consolidation arc.
_mean_score = _ranking_score  # compat alias; retired in the consolidation arc


def _rank_candidates(scout_no):
    """Return candidate numbers (1-based), best first. Order: audit verdict,
    then mean rubric score, then original order. DUPLICATE_PRIOR is excluded."""
    candidates = _load_candidates(scout_no)
    verdicts = _audit_verdicts(scout_dir(scout_no))
    ranked = []
    for i, card in enumerate(candidates, 1):
        v = verdicts.get(i, 'UNAUDITED')
        if v == 'DUPLICATE_PRIOR':
            print(f'  skipping C{i}: audit verdict DUPLICATE_PRIOR')
            continue
        ranked.append((ledger_mod.VERDICT_TIER.get(v, 5), -_mean_score(card), i))
    ranked.sort()
    return [i for _, _, i in ranked]


def _parse_scout_dir(name):
    """'scout-013' -> (None, 13); 'scout-isles24-001' -> ('isles24', 1)."""
    parts = name.split('-')
    if len(parts) == 2:
        return None, int(parts[1])
    return '-'.join(parts[1:-1]), int(parts[-1])


def _scout_lid(charter, scout_no, suffix):
    """Charter-prefixed ledger ids: scout-013-c01 / isles24-scout-001-c01."""
    base = f'scout-{scout_no:03d}-{suffix}'
    return f'{charter}-{base}' if charter else base


def _latest_scout_no(charter=None):
    scouts = sorted(p for p in (ROOT/'ideas').glob('scout-*')
                    if _parse_scout_dir(p.name)[0] == charter)
    if not scouts:
        raise SystemExit('No scouting cycles exist yet'
                         + (f' for charter {charter!r}.' if charter else '.'))
    return _parse_scout_dir(scouts[-1].name)[1]


def _sync_backlog():
    """Idempotently upsert every scouted candidate of every cycle into the
    ledger with its rubric score and (when the audit exists) novelty verdict.
    Backfills cycles that ran before these fields existed."""
    entries = ledger_mod.load()
    changed = False
    for d in sorted((ROOT/'ideas').glob('scout-*')):
        if not (d/'candidates_all.json').exists():
            continue
        d_charter, scout_no = _parse_scout_dir(d.name)
        try:
            cands = json.loads((d/'candidates_all.json').read_text()).get('candidates', [])
        except json.JSONDecodeError:
            continue
        verdicts = _audit_verdicts(d)
        audited = datetime.now(timezone.utc).isoformat(timespec='seconds') if verdicts else None
        for i, c in enumerate(cands, 1):
            lid = _scout_lid(d_charter, scout_no, f'c{i:02d}')
            cur = entries.get(lid, {})
            rec = {'ledger_id': lid}
            if not cur:
                rec.update({'title': c.get('title',''),
                            'claim': c.get('deliverable_sentence') or c.get('question',''),
                            'track': c.get('track','baseline'),
                            'status': 'SCOUT_ONLY', 'scrutiny': 'SCOUTED',
                            'source': str(d.relative_to(ROOT))})
            new_score = _mean_score(c)
            if new_score and abs(float(cur.get('scores_mean') or 0) - new_score) > 1e-9:
                rec['scores_mean'] = new_score
            v = verdicts.get(i)
            if v and cur.get('novelty_verdict') != v:
                rec['novelty_verdict'] = v
                rec['audited_at'] = audited
            if len(rec) > 1:
                ledger_mod.append(rec)
                changed = True
    if changed:
        ledger_mod.digest()


def _ranked_backlog(charter=None):
    """Unshortlisted scouted candidates, best first, SCOPED TO ONE CHARTER
    (None = baseline). Scores are never comparable across charters, so no
    global mixed ranking exists by construction.
    Returns [(scout_no, cand_no, ledger_entry), ...]."""
    _sync_backlog()
    import re
    pat = (re.compile(r'scout-(\d+)-c(\d+)$') if charter is None
           else re.compile(re.escape(charter) + r'-scout-(\d+)-c(\d+)$'))
    out = []
    for lid, e in ledger_mod.load().items():
        if e.get('status') != 'SCOUT_ONLY':
            continue
        m = pat.match(lid)
        if not m:
            continue
        v = e.get('novelty_verdict', 'UNAUDITED')
        if VERDICT_TIER.get(v, 5) >= 9:
            continue
        rank = VERDICT_TIER.get(v, 5)
        out.append(((rank, -float(e.get('scores_mean') or 0), -int(m.group(1))),
                    int(m.group(1)), int(m.group(2)), e))
    out.sort(key=lambda x: x[0])
    return [(s, c, e) for _, s, c, e in out]


def backlog_cmd(_args):
    rows = _ranked_backlog()
    if not rows:
        print('Backlog empty: every scouted candidate is shortlisted or killed.')
        return
    for s, c, e in rows:
        v = e.get('novelty_verdict', 'UNAUDITED')
        sm = e.get('scores_mean')
        print(f"cycle {s:03d} C{c}  [{v}{', %.1f' % sm if sm else ''}]  {e.get('title','')[:80]}")


def _incomplete_pipeline_ideas(stages, charter=None):
    """Shortlisted ideas whose requested final artifact is missing -- these are
    in-flight and must be finished before new candidates are drawn."""
    final = STAGE_DONE_MARKER.get(stages[-1])
    out = []
    for lid, e in sorted(ledger_mod.load().items()):
        if e.get('status') != 'SHORTLISTED' or not lid.startswith('idea-'):
            continue
        n = int(lid.split('-')[1])
        # scope to the requested charter: an isles24 pipeline run must
        # never divert to finishing a baseline idea (2026-08-18 audit);
        # normalized so legacy cards without the field are baseline
        if charter_for_target(idea_dir(n)) != _norm_charter(charter):
            continue
        if final and not (idea_dir(n)/final).exists():
            out.append(n)
    return out


PIPELINE_STAGES = ('keystone', 'critique', 'revise', 'feasibility', 'debate')
STAGE_DONE_MARKER = {'keystone': 'keystone_screen.md','critique': 'critique.md', 'revise': 'idea_card.json',
                     'feasibility': 'feasibility.md', 'debate': 'consensus.md'}


PIPELINE_PROMPT = {'keystone': 'keystone_screen'}


def _apply_keystone_verdict(idea):
    import re
    body = read_text(idea_dir(idea)/'keystone_screen.md')
    blocks = re.findall(r'```json\s*(\{.*?\})\s*```', body, flags=re.S)
    if not blocks:
        return None
    try:
        v = json.loads(blocks[-1])
    except json.JSONDecodeError:
        return None
    verdict = str(v.get('verdict', '')).upper()
    if verdict in ('PASS', 'KILL') and not (str(v.get('evidence', '')).strip()
                                            and str(v.get('source', '')).strip()):
        print(f'Keystone verdict {verdict} lacked evidence/source; demoted to UNVERIFIABLE '
              '(the evidence rule is mechanical, not a prompt promise).')
        verdict = 'UNVERIFIABLE'
    lid = f'idea-{int(idea):03d}'
    if verdict == 'KILL':
        code = v.get('kill_code') if v.get('kill_code') in ledger_mod.TAXONOMY else 'UNCLASSIFIED'
        ledger_mod.append({'ledger_id': lid, 'status': 'REJECTED', 'kill_code': code,
                           'kill_reason': ('keystone screen: ' + str(v.get('note', '')))[:400],
                           'death_stage': 'keystone',
                           'keystone_evidence': str(v.get('evidence', ''))[:500]})
        ledger_mod.digest()
    return verdict


_CLI_VERSIONS = None


def _cli_versions():
    global _CLI_VERSIONS
    if _CLI_VERSIONS is None:
        def ver(cmd):
            try:
                r = subprocess.run(cmd, capture_output=True, text=True, check=False)
            except (FileNotFoundError, OSError):
                return 'not installed'
            out = (r.stdout or r.stderr or '').strip()
            return out.splitlines()[0] if out else 'unknown'
        _CLI_VERSIONS = {'claude': ver(['claude', '--version']),
                         'codex': ver(['codex', '--version'])}
    return _CLI_VERSIONS


def _record_stage_provenance(idea, stage):
    rec = dict(_cli_versions())
    rec.update({'stage': stage,
                'ts': datetime.now(timezone.utc).isoformat(timespec='seconds'),
                'git_commit': subprocess.run(['git', 'rev-parse', 'HEAD'],
                                             capture_output=True, text=True,
                                             check=False).stdout.strip()})
    if LAST_RUN and LAST_RUN.get('stage') == stage:
        # D2 visibility: which model actually ran, and whether it was a
        # fallback. record-never-pin extended to graceful degradation.
        rec.update({k: LAST_RUN[k] for k in
                    ('model_requested', 'model_used', 'fallback')
                    if k in LAST_RUN})
        if LAST_RUN.get('fallback'):
            rec['attempts'] = LAST_RUN['attempts']
    with (idea_dir(idea) / 'stage_provenance.jsonl').open('a') as f:
        f.write(json.dumps(rec) + '\n')


def _pipeline_stage(idea, stage):
    target = idea_dir(idea)
    if stage == 'debate':
        import types
        debate(types.SimpleNamespace(idea=idea, rounds=None))
        if not (target/'consensus.md').exists():
            raise SystemExit(f'Debate for idea {idea:03d} ended without consensus.md.')
        return
    p = write_prompt(PIPELINE_PROMPT.get(stage, stage), target)
    run_agent(p, None, stage=stage, log_path=target/f'log_{stage}.txt')
    _check_scope(stage)
    _require_artifact(stage, target)
    _record_stage_provenance(idea, stage)
    if stage == 'keystone':
        kv = _apply_keystone_verdict(idea)
        if kv:
            print(f'Keystone screen verdict: {kv}')
    if stage == 'critique':
        ledger_mod.raise_scrutiny(f'idea-{idea:03d}', 'CRITIQUED')
        ledger_mod.digest()
    if stage == 'revise':
        import re as _re
        rec = {'ledger_id': f'idea-{idea:03d}', 'card_synced': True,
               'notes': 'card revised to debate-converged state'}
        body = read_text(target/'revision.md')
        m2 = _re.findall(r'```json\s*(\{.*?\})\s*```', body, flags=_re.S)
        if m2:
            try:
                cr = json.loads(m2[-1]).get('claim_retention', '')
                if cr in ('same', 'narrowed', 'different'):
                    rec['claim_retention'] = cr
            except json.JSONDecodeError:
                pass
        ledger_mod.append(rec)
        ledger_mod.digest()


def _revise_debt_ideas():
    """Live ideas whose debate verdict is REVISE but whose card has not been
    synced. Covers pre-automation debates by falling back to parsing the
    consensus Recommendation when no ledger flag exists."""
    import re
    entries = ledger_mod.load()
    out = []
    for d in sorted((ROOT/'ideas').glob('[0-9][0-9][0-9]')):
        n = int(d.name)
        lid = f'idea-{d.name}'
        e = entries.get(lid, {})
        if e.get('status') == 'REJECTED':
            continue
        if e.get('card_synced') is True:
            continue
        if e.get('card_synced') is False:
            out.append(n)
            continue
        body = read_text(d/'consensus.md')
        rec = _extract_section(body, 'Recommendation') if body else ''
        if re.search(r'\bREVISE\b', rec):
            out.append(n)
    return out


def pipeline(args):
    stages = [x.strip() for x in (args.stages or 'critique,debate').split(',') if x.strip()]
    bad = [x for x in stages if x not in PIPELINE_STAGES]
    if bad:
        raise SystemExit(f'Unknown stage(s): {", ".join(bad)}. Known: {", ".join(PIPELINE_STAGES)}')
    _require_clean_tree('pipeline')
    if getattr(args, 'revise_debt', False):
        ideas = _revise_debt_ideas()
        if not ideas:
            print('No revise debt: every REVISE-verdicted card is synced.')
            return
        print('Revise debt: ' + ', '.join(f'{i:03d}' for i in ideas))
        stages = ['revise']
    elif args.idea:
        ideas = [args.idea]
    else:
        charter = getattr(args, 'charter', None) or None
        if args.scout:
            sch, sno = _parse_scout_ref(args.scout)
            if charter and sch and sch != charter:
                raise SystemExit(f'--charter {charter} conflicts with --scout {args.scout}.')
            charter = charter or sch
        else:
            sno = None
        if charter:
            charter_path(charter)  # existence check
        if args.candidate:
            scout_no = sno or _latest_scout_no(charter)
            picks = [(scout_no, args.candidate)]
        else:
            n = max(1, int(args.top or 1))
            inflight = _incomplete_pipeline_ideas(stages, charter)
            if inflight:
                print('Finishing in-flight idea(s) first: '
                      + ', '.join(f'{i:03d}' for i in inflight[:n]))
            rows = _ranked_backlog(charter)
            if sno:
                rows = [r for r in rows if r[0] == sno]
            print('Backlog (best first, charter='
                  + (charter or 'baseline') + '): '
                  + (', '.join(f'{_fmt_scout(charter, s)}-C{c}' for s, c, _ in rows[:8]) or '(empty)'))
            picks = [(s, c) for s, c, _ in rows[:max(0, n - len(inflight[:n]))]]
            ideas_prefix = inflight[:n]
        ideas = list(locals().get('ideas_prefix', []))
        for scout_no, cand in picks:
            ideas.append(_do_shortlist(scout_no, cand, charter=charter))
            _commit_all(f'pipeline: shortlist C{cand} of cycle {_fmt_scout(charter, scout_no)}')
        if not ideas:
            print('Nothing to do: backlog empty and no in-flight ideas.')
            return
    failures = []
    for idea in ideas:
        for stage in stages:
            marker = STAGE_DONE_MARKER.get(stage)
            if stage != 'revise' and marker and (idea_dir(idea)/marker).exists():
                print(f'[skip] idea {idea:03d} {stage}: {marker} already exists')
                continue
            print(f'\n=== idea {idea:03d}: {stage} ===')
            try:
                _pipeline_stage(idea, stage)
            except SystemExit as e:
                _commit_all(f'idea {idea:03d}: {stage} FAILED (partial output preserved)')
                print(f'Stage {stage!r} failed for idea {idea:03d}: {e}')
                failures.append((idea, stage))
                break  # later stages of this idea depend on this one
            _commit_all(f'idea {idea:03d}: {stage} done')
            print(f'[done] idea {idea:03d} {stage} (checkpoint committed)')
            if stage == 'keystone':
                if ledger_mod.load().get(f'idea-{idea:03d}', {}).get('status') == 'REJECTED':
                    print(f'idea {idea:03d} killed at keystone screen; skipping remaining stages.')
                    break
            if stage == 'debate' and 'revise' not in stages:
                e = ledger_mod.load().get(f'idea-{idea:03d}', {})
                if e.get('card_synced') is False:
                    print(f'=== idea {idea:03d}: debate verdict REVISE -> auto-revising card ===')
                    try:
                        _pipeline_stage(idea, 'revise')
                    except SystemExit as ex:
                        _commit_all(f'idea {idea:03d}: auto-revise FAILED (partial output preserved)')
                        print(f'Auto-revise failed for idea {idea:03d}: {ex}')
                        failures.append((idea, 'revise'))
                        continue
                    _commit_all(f'idea {idea:03d}: auto-revise done')
                    print(f'[done] idea {idea:03d} auto-revise (checkpoint committed)')
    print('\nPipeline summary:')
    for idea in ideas:
        status = next((f'FAILED at {st}' for i, st in failures if i == idea), 'complete')
        print(f'  idea {idea:03d}: {status}')
    if failures:
        print('Re-run the same pipeline command to resume: completed stages are skipped.')
        raise SystemExit(1)
    print('Read each idea\'s critique.md, debate.md and consensus.md yourself before proceeding.')


# ==========================================================================
# Librarian: an on-demand whole-corpus pass (separate from cycles and the
# idea pipeline). Reads a full-detail dossier no other stage gets, maintains
# the ledger's verdicts, and leaves proposals for future scouts to adopt.
# ==========================================================================

VERDICT_SYNONYMS = {'NOVEL_VERIFIED': 'NO_DUPLICATE_FOUND_HIGH_CONFIDENCE',
                    'NOVEL_UNVERIFIED': 'NO_DUPLICATE_FOUND_LIMITED_SEARCH',
                    'DUPLICATE_PRIOR': 'DUPLICATE_FOUND'}
VALID_VERDICTS = {'NO_DUPLICATE_FOUND_HIGH_CONFIDENCE', 'NO_DUPLICATE_FOUND_LIMITED_SEARCH',
                  'INCREMENTAL', 'DUPLICATE_FOUND'} | set(VERDICT_SYNONYMS)
VERDICT_TIER = ledger_mod.VERDICT_TIER  # canonical table lives in ledger.py


def _dossier_entry_idea(d, entries):
    lid = f'idea-{d.name}'
    e = entries.get(lid, {})
    parts = [f"## {lid} [{e.get('status','?')}/{e.get('scrutiny','?')}]"]
    card = {}
    if (d/'idea_card.json').exists():
        try:
            card = json.loads((d/'idea_card.json').read_text())
        except json.JSONDecodeError:
            pass
    for k in ('title', 'question', 'deliverable_sentence', 'dataset',
              'keystone_prerequisite', 'keystone_status'):
        v = card.get(k)
        if v:
            parts.append(f'- {k}: {json.dumps(v) if not isinstance(v, str) else v}'[:400])
    if e.get('kill_code'):
        parts.append(f"- KILLED: {e['kill_code']} -- {e.get('kill_reason','')[:300]}")
    body = read_text(d/'consensus.md')
    if body:
        for header in ('Recommendation', 'Unresolved', 'Amendments made'):
            sec = _extract_section(body, header)
            if sec:
                parts.append(f'### {header}\n' + ' '.join(sec.split())[:1600])
    return '\n'.join(parts)


def write_librarian_dossier(target):
    entries = ledger_mod.load()
    chunks = ['# Librarian dossier (auto-generated)', '']
    for d in sorted((ROOT/'ideas').glob('[0-9][0-9][0-9]')):
        chunks.append(_dossier_entry_idea(d, entries))
        chunks.append('')
    chunks.append('# Backlog candidates')
    for lid, e in sorted(entries.items()):
        if not lid.startswith('scout-'):
            continue
        chunks.append(f"- {lid} [{e.get('status','?')}] verdict={e.get('novelty_verdict','UNAUDITED')}"
                      f" audited={str(e.get('audited_at',''))[:10]} score={e.get('scores_mean','')}"
                      f" -- {e.get('title','')[:120]}"
                      + (f" (kill: {e['kill_code']})" if e.get('kill_code') else ''))
    out = target/'dossier.md'
    out.write_text('\n'.join(chunks) + '\n')
    return out


def _apply_librarian_outputs(target):
    applied = []
    vpath = target/'verdict_updates.json'
    if vpath.exists():
        try:
            ups = json.loads(vpath.read_text()).get('updates', [])
        except json.JSONDecodeError:
            ups = []
        for u in ups:
            lid, v = u.get('ledger_id'), u.get('novelty_verdict')
            v = VERDICT_SYNONYMS.get(v, v)  # legacy names normalized on ingestion
            if lid and v in VALID_VERDICTS and lid in ledger_mod.load():
                ledger_mod.append({'ledger_id': lid, 'novelty_verdict': v,
                                   'audited_at': datetime.now(timezone.utc).isoformat(timespec='seconds'),
                                   'notes': ('librarian: ' + u.get('reason', ''))[:500]})
                applied.append(f'{lid} -> {v}')
    ppath = target/'librarian_proposals.json'
    if ppath.exists():
        try:
            props = json.loads(ppath.read_text()).get('proposals', [])
        except json.JSONDecodeError:
            props = []
        if props:
            lines = ['# Librarian proposals (for future scouting cycles to adopt or ignore)',
                     f'Generated from {target.relative_to(ROOT)}.', '']
            for pr in props:
                lines.append(f"## {pr.get('title','(untitled)')}")
                lines.append(f"- parents: {', '.join(pr.get('parent_ids', []) or ['(none)'])}")
                if pr.get('revival_basis'):
                    lines.append(f"- basis: {pr['revival_basis'][:500]}")
                if pr.get('sketch'):
                    lines.append(f"- sketch: {pr['sketch'][:500]}")
                lines.append('')
            (ROOT/'evidence'/'librarian_proposals.md').write_text('\n'.join(lines) + '\n')
    ledger_mod.digest()
    write_portfolio_brief()
    if applied:
        print('Verdict updates applied: ' + '; '.join(applied))
    return applied


def librarian(args):
    _require_clean_tree('librarian')
    existing = sorted((ROOT/'ideas').glob('librarian-*'))
    n = (int(existing[-1].name.split('-')[1]) + 1) if existing else 1
    d = ROOT/'ideas'/f'librarian-{n:03d}'
    d.mkdir(parents=True)
    _sync_backlog()
    write_librarian_dossier(d)
    _commit_all(f'librarian {n:03d}: dossier')
    p = write_prompt('librarian', d)
    try:
        run_agent(p, args.agent if hasattr(args, 'agent') else None,
                  stage='librarian', log_path=d/'log_librarian.txt')
        _check_scope('librarian')
        _require_artifact('librarian', d)
    except SystemExit as e:
        _commit_all(f'librarian {n:03d}: FAILED (partial output preserved)')
        print(f'Librarian pass failed: {e}')
        raise SystemExit(1)
    _commit_all(f'librarian {n:03d}: report')
    _apply_librarian_outputs(d)
    _commit_all(f'librarian {n:03d}: verdicts + proposals applied')
    print(f'Librarian pass {n:03d} complete. Read {d.relative_to(ROOT)}/librarian_report.md.')


# ---- structured debate verdict -> ledger ----

def _apply_consensus_verdict(idea):
    """Parse the machine-readable verdict block at the end of consensus.md and
    reflect it on the idea's ledger row. Graceful no-op when absent."""
    import re
    body = read_text(idea_dir(idea)/'consensus.md')
    blocks = re.findall(r'```json\s*(\{.*?\})\s*```', body, flags=re.S)
    if not blocks:
        return None
    try:
        v = json.loads(blocks[-1])
    except json.JSONDecodeError:
        return None
    lid = f'idea-{int(idea):03d}'
    verdict = str(v.get('verdict', '')).upper()
    note = ('debate: ' + str(v.get('unblock', v.get('reason', ''))))[:500]
    if verdict == 'KILL':
        code = v.get('kill_code') if v.get('kill_code') in ledger_mod.TAXONOMY else 'UNCLASSIFIED'
        ledger_mod.append({'ledger_id': lid, 'status': 'REJECTED',
                           'kill_code': code, 'kill_reason': note,
                           'death_stage': 'debate'})
    elif verdict == 'PAUSE':
        ledger_mod.append({'ledger_id': lid, 'status': 'PAUSED', 'notes': note})
    elif verdict in ('REVISE', 'PROCEED'):
        rec = {'ledger_id': lid, 'status': 'SHORTLISTED' if verdict == 'REVISE' else 'ACTIVE',
               'notes': note}
        if verdict == 'REVISE':
            rec['card_synced'] = False
        ledger_mod.append(rec)
    else:
        return None
    ledger_mod.digest()
    print(f'Ledger updated from consensus: {lid} -> {verdict}')
    return verdict


# ==========================================================================
# Actioner: aggregates everything awaiting the human into one phone-readable
# brief. Collection is deterministic python; the agent only synthesizes and
# prioritizes. Improvement mode (separate workflow input) may additionally
# author ONE pull request -- never a commit to main; the merge button is the
# approval gate and the checks workflow gates it with the full test suite.
# ==========================================================================

def _pending_decisions():
    out = []
    entries = ledger_mod.load()
    for d in sorted((ROOT/'ideas').glob('[0-9][0-9][0-9]')):
        lid = f'idea-{d.name}'
        e = entries.get(lid, {})
        if e.get('status') == 'REJECTED':
            continue
        body = read_text(d/'consensus.md')
        if not body:
            continue
        rec = ' '.join(_extract_section(body, 'Recommendation').split())
        if rec:
            out.append((lid, e.get('status', '?'), rec[:900]))
    return out


def write_action_state(target):
    entries = ledger_mod.load()
    lines = ['# Action state (mechanically collected -- facts, not judgments)', '']
    lines.append('## Consensus recommendations for live ideas')
    for lid, status, rec in _pending_decisions():
        lines += [f'- **{lid}** [{status}]: {rec}', '']
    lines.append('## Paused ideas and their unblock notes')
    for lid, e in sorted(entries.items()):
        if e.get('status') == 'PAUSED' and lid.startswith('idea-'):
            lines.append(f"- {lid}: {e.get('notes','(no note)')[:300]}")
    lines.append('')
    lines.append('## Banked fiction near-misses (unadopted)')
    found = False
    for lid, e in sorted(entries.items()):
        if lid.endswith('-fadj'):
            found = True
            lines.append(f"- {lid}: {e.get('claim','')[:250]}")
    if not found:
        lines.append('- (none)')
    lines.append('')
    rows = _ranked_backlog()
    lines.append(f'## Backlog ({len(rows)} candidates, best first)')
    for s, c, e in rows[:12]:
        lines.append(f"- {s:03d}-C{c} [{e.get('novelty_verdict','UNAUDITED')}"
                     f"{', audited ' + str(e.get('audited_at',''))[:10] if e.get('audited_at') else ''}]"
                     f" {e.get('title','')[:90]}")
    lines.append('')
    libs = sorted((ROOT/'ideas').glob('librarian-*'))
    if libs:
        rep = read_text(libs[-1]/'librarian_report.md')
        summ = ' '.join(_extract_section(rep, 'Summary').split())[:700]
        lines += [f'## Latest librarian pass ({libs[-1].name})', f'- {summ}', '']
        conn = _extract_section(rep, 'Duty 1 -- Connection map') or _extract_section(rep, 'Duty 1 — Connection map')
        heads = [ln for ln in conn.splitlines() if ln.startswith('**')]
        if heads:
            lines.append('- Connections mapped: ' + '; '.join(h.strip('*.') for h in heads)[:600])
            lines.append('')
    pend = [ln[6:] for ln in read_text(ROOT/'REVAMP.md').splitlines() if ln.startswith('- [ ] ')]
    if pend:
        lines.append('## REVAMP pending items')
        for x in pend:
            lines.append('- ' + x[:120])
        lines.append('')
    prev = read_text(ROOT/'evidence'/'actions.md')
    if prev:
        lines += ['## Previous brief (verbatim -- ground persistence and resolution claims here)',
                  '', prev[:4000], '']
    else:
        lines += ['## Previous brief', '', '(none -- this is the first brief; no persistence claims are possible)', '']
    out = target/'action_state.md'
    out.write_text('\n'.join(lines) + '\n')
    return out


def actioner(args):
    _require_clean_tree('actioner')
    existing = sorted((ROOT/'ideas').glob('actioner-*'))
    n = (int(existing[-1].name.split('-')[1]) + 1) if existing else 1
    d = ROOT/'ideas'/f'actioner-{n:03d}'
    d.mkdir(parents=True)
    _sync_backlog()
    write_action_state(d)
    _commit_all(f'actioner {n:03d}: state collected')
    p = write_prompt('actioner', d)
    if getattr(args, 'improve', False):
        p.write_text(p.read_text() + '\n===== IMPROVEMENT MODE ENABLED =====\n'
                     'Include the "Proposed improvement" section: ONE change only.\n'
                     'Allowed targets: orchestrator/prompts/*, orchestrator/seeds.json, docs/*.\n'
                     'scout.py or tests/ changes must be single-purpose and prominently flagged.\n'
                     'NEVER propose changes to .github/workflows/, AGENTS.toml auth, or the scope/artifact guards.\n')
    try:
        run_agent(p, getattr(args, 'agent', None), stage='actioner', log_path=d/'log_actioner.txt')
        _check_scope('actioner')
        _require_artifact('actioner', d)
    except SystemExit as e:
        _commit_all(f'actioner {n:03d}: FAILED (partial output preserved)')
        print(f'Actioner pass failed: {e}')
        raise SystemExit(1)
    shutil.copy2(d/'actions.md', ROOT/'evidence'/'actions.md')
    _commit_all(f'actioner {n:03d}: brief published')
    print(f'Actioner brief: evidence/actions.md (source: {d.relative_to(ROOT)})')


def main():
    ap=argparse.ArgumentParser(); sp=ap.add_subparsers(dest='cmd',required=True)
    p=sp.add_parser('doctor'); p.set_defaults(fn=doctor)
    p=sp.add_parser('new-scout'); p.set_defaults(fn=new_scout)
    p=sp.add_parser('shortlist'); p.add_argument('scout'); p.add_argument('candidate',type=int); p.add_argument('--track',choices=TRACKS); p.set_defaults(fn=shortlist)
    p=sp.add_parser('run'); p.add_argument('stage',choices=['scout','wide-scout','fiction-scout','fiction-extract','fiction-refine','novelty-audit','critique','revise','feasibility','probe-plan','probe-code','interpret','context-memo','reconcile']); p.add_argument('--idea',type=int); p.add_argument('--agent',choices=['claude','codex']); p.set_defaults(fn=run_stage)
    p=sp.add_parser('approve-probe'); p.add_argument('idea',type=int); p.set_defaults(fn=approve_probe)
    p=sp.add_parser('verify-probe'); p.add_argument('idea',type=int); p.set_defaults(fn=verify_probe)
    p=sp.add_parser('package-colab'); p.add_argument('idea',type=int); p.add_argument('--phase',default='B'); p.add_argument('--staging-zenodo',help='Zenodo concept id: generate Drive-persistent staging cells'); p.add_argument('--staging-suffixes',help='comma-separated filename suffixes to extract'); p.add_argument('--phase-s-dir',help='Drive path holding the Phase-S bundle this phase must verify'); p.set_defaults(fn=package_colab)
    p=sp.add_parser('record-result'); p.add_argument('idea',type=int); p.add_argument('--bundle'); p.set_defaults(fn=record_result)
    p=sp.add_parser('amend-contract'); p.add_argument('idea',type=int); p.add_argument('--bundle',required=True); p.set_defaults(fn=amend_contract)
    p=sp.add_parser('diversity'); p.add_argument('--charter',default=None); p.set_defaults(fn=cmd_diversity)
    p=sp.add_parser('validate-bundle'); p.add_argument('idea',type=int); p.add_argument('--bundle',required=True); p.set_defaults(fn=cmd_validate_bundle)
    p=sp.add_parser('bundle-complete'); p.add_argument('idea',type=int); p.add_argument('--bundle',required=True); p.set_defaults(fn=lambda a: print(str(bundle_complete(a.idea, a.bundle)).lower()))
    p=sp.add_parser('debate'); p.add_argument('--idea',type=int); p.add_argument('--rounds',type=int); p.set_defaults(fn=debate)
    p=sp.add_parser('status'); p.set_defaults(fn=status)
    p=sp.add_parser('cycle'); p.add_argument('--charter',default=None,help='named charter under charters/<name>/CHARTER.md; omit for the baseline'); p.add_argument('--tracks',default='baseline',help='comma-separated: baseline,wide,fiction'); p.add_argument('--dry-run',action='store_true'); p.add_argument('--resume-or-new',action='store_true'); p.add_argument('--seed-concepts',default=None,help='comma-separated pair to direct the fiction seed (source recorded as human)'); p.set_defaults(fn=cycle)
    p=sp.add_parser('resume'); p.set_defaults(fn=resume)
    p=sp.add_parser('backlog'); p.set_defaults(fn=backlog_cmd)
    p=sp.add_parser('brief'); p.set_defaults(fn=brief_cmd)
    p=sp.add_parser('librarian'); p.add_argument('--agent',choices=['claude','codex']); p.set_defaults(fn=librarian)
    p=sp.add_parser('probe-build'); p.add_argument('idea',type=int); p.set_defaults(fn=probe_build)
    p=sp.add_parser('interpret-build'); p.add_argument('idea',type=int); p.set_defaults(fn=interpret_build)
    p=sp.add_parser('actioner'); p.add_argument('--improve',action='store_true'); p.add_argument('--agent',choices=['claude','codex']); p.set_defaults(fn=actioner)
    p=sp.add_parser('pipeline'); p.add_argument('--top',type=int); p.add_argument('--charter',default=None); p.add_argument('--scout'); p.add_argument('--candidate',type=int); p.add_argument('--idea',type=int); p.add_argument('--stages',default='keystone,critique,debate'); p.add_argument('--revise-debt',action='store_true'); p.set_defaults(fn=pipeline)
    p=sp.add_parser('ledger'); lsp=p.add_subparsers(dest='ledger_cmd',required=True)
    for c in ('migrate','digest','list','taxonomy'):
        q=lsp.add_parser(c)
        if c=='migrate': q.add_argument('--force',action='store_true')
    q=lsp.add_parser('show'); q.add_argument('id')
    q=lsp.add_parser('search'); q.add_argument('query')
    q=lsp.add_parser('kill'); q.add_argument('id'); q.add_argument('code'); q.add_argument('reason')
    q=lsp.add_parser('set-status'); q.add_argument('id'); q.add_argument('status'); q.add_argument('--note',default='')
    p.set_defaults(fn=ledger_mod.cli)
    args=ap.parse_args(); args.fn(args)

if __name__=='__main__': main()
