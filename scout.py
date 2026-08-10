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
import argparse, csv, json, os, random, shutil, subprocess, sys, textwrap
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


def scout_dir(i):
    return ROOT/'ideas'/f'scout-{int(i):03d}'


# --------------------------------------------------------------------------
# Prompt building. Fiction-track early stages are BLIND: the writer must not
# see the charter, rules, rubric, or institutional memory, or it will start
# self-censoring toward plausibility -- exactly what the track exists to avoid.
# The refiner sees everything EXCEPT the story: it must judge the pitch, not
# the fiction it came from.
# --------------------------------------------------------------------------

BLIND_STAGES = {'fiction_scout', 'fiction_extract'}
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
    files = [ROOT/'CHARTER.md', ROOT/'docs'/'COLLABORATOR_RULES.md',
             ROOT/'docs'/'SCORING_RUBRIC.md', ROOT/'evidence'/'decisions.md',
             ROOT/'evidence'/'ledger_digest.md', ROOT/'evidence'/'portfolio_brief.md',
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
    path.write_text(build_prompt(stage, target))
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


def run_agent(prompt_path, agent=None, stage=None, log_path=None):
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
    print('Running:', ' '.join(command[:3]), '...')
    stdin_text = prompt_text if use_stdin else None
    timeout = int(cfg.get('limits', {}).get('stage_timeout', 3600))
    lines = []
    import time
    deadline = time.monotonic() + timeout
    proc = subprocess.Popen(command, cwd=ROOT, text=True,
                            stdin=subprocess.PIPE if use_stdin else None,
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    try:
        if use_stdin:
            try:
                proc.stdin.write(stdin_text)
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
    if proc.returncode:
        raise SystemExit(f'Agent exited with code {proc.returncode}. Prompt retained at {prompt_path}')


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
    rot = cfg.get('rotation', {})
    print(f"\nRotation: {'enabled' if rot.get('enabled') else 'disabled'}"
          f" (pair={rot.get('pair', ['claude','codex'])},"
          f" active_cycle={load_state().get('active_cycle')})")
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


def _load_candidates(scout_no, track=None):
    src = scout_dir(scout_no)/'scout_candidates.json'
    merged = scout_dir(scout_no)/'candidates_all.json'
    if merged.exists():
        src = merged
    if not src.exists():
        raise SystemExit(f'Missing {src}. Run or complete the scout stage first.')
    data = json.loads(src.read_text())
    candidates = data.get('candidates', data if isinstance(data, list) else [])
    if track:
        candidates = [c for c in candidates if c.get('track', 'baseline') == track]
    return candidates


def _do_shortlist(scout_no, cand_no, track=None):
    """Shortlist candidate cand_no (1-based) from cycle scout_no. Idempotent per
    cycle: a candidate already shortlisted returns its existing idea number."""
    s = load_state()
    done = s.setdefault('shortlisted', {}).setdefault(str(scout_no), {})
    if str(cand_no) in done:
        print(f'Candidate {cand_no} of cycle {scout_no:03d} already shortlisted as idea {done[str(cand_no)]:03d}.')
        return done[str(cand_no)]
    candidates = _load_candidates(scout_no, track)
    idx = cand_no-1
    if idx < 0 or idx >= len(candidates):
        raise SystemExit('Candidate index out of range.')
    existing = [int(p.name) for p in (ROOT/'ideas').iterdir() if p.is_dir() and p.name.isdigit()]
    n = max(existing, default=0)+1
    d = idea_dir(n); d.mkdir()
    card = candidates[idx]
    (d/'idea_card.json').write_text(json.dumps(card, indent=2)+'\n')
    (d/'README.md').write_text(f"# Idea {n:03d}: {card.get('title','Untitled')}\n\nSelected from scouting cycle {scout_no:03d}, candidate {cand_no}.\n")
    s = load_state()
    s['selected_idea'] = n
    s.setdefault('shortlisted', {}).setdefault(str(scout_no), {})[str(cand_no)] = n
    save_state(s)
    with (ROOT/'portfolio'/'ideas.csv').open('a', newline='') as f:
        csv.writer(f).writerow([f'{n:03d}', card.get('title',''), 'ACTIVE', '', card.get('scores',{}).get('regret',''), 'CRITIQUE', ''])
    ledger_mod.append({'ledger_id': f'idea-{n:03d}', 'title': card.get('title',''),
                       'claim': card.get('deliverable_sentence') or card.get('question',''),
                       'track': card.get('track','baseline'), 'status': 'SHORTLISTED',
                       'scrutiny': 'SCOUTED', 'source': f'ideas/{n:03d}'})
    if track is None:
        # Retire the source candidate from the backlog and point at its idea.
        ledger_mod.append({'ledger_id': f'scout-{scout_no:03d}-c{cand_no:02d}',
                           'status': 'SHORTLISTED', 'notes': f'promoted to idea-{n:03d}'})
    ledger_mod.digest()
    print(f'Shortlisted as idea {n:03d}')
    return n


def shortlist(args):
    _do_shortlist(args.scout, args.candidate, args.track)


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
    _require_clean_tree(args.stage)
    p=write_prompt(args.stage.replace('-','_'), target)
    print('Prompt:',p.relative_to(ROOT))
    run_agent(p, args.agent, stage=args.stage,
              log_path=target / f"log_{args.stage.replace('-', '_')}.txt")
    _check_scope(args.stage)
    _require_artifact(args.stage.replace('-', '_'), target)
    if args.stage=='critique' and args.idea:
        ledger_mod.raise_scrutiny(f'idea-{args.idea:03d}', 'CRITIQUED')


def approve_probe(args):
    d=idea_dir(args.idea)
    if not (d/'feasibility.md').exists(): raise SystemExit('Feasibility memo missing.')
    marker=d/'HUMAN_APPROVED_PROBE'
    marker.write_text(f'Approved by human at {datetime.now(timezone.utc).isoformat()}\n')
    print('Approved probe for',d.name)


def verify_probe(args):
    p=ROOT/'probes'/f'{args.idea:03d}'
    issues=[]
    for f in ['run.py','README.md']:
        if not (p/f).exists(): issues.append(f'missing {f}')
    if (p/'run.py').exists():
        r=subprocess.run([sys.executable,'-m','py_compile',str(p/'run.py')],capture_output=True,text=True)
        if r.returncode: issues.append('syntax error: '+r.stderr[-500:])
        smoke=subprocess.run([sys.executable,str(p/'run.py'),'--smoke-test'],cwd=p,capture_output=True,text=True,timeout=300)
        if smoke.returncode: issues.append('smoke test failed: '+(smoke.stderr or smoke.stdout)[-1000:])
    out={'idea_id':f'{args.idea:03d}','passed':not issues,'issues':issues,'checked_at':datetime.now(timezone.utc).isoformat()}
    (p/'verification.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps(out,indent=2))
    if issues: raise SystemExit(1)


def package_colab(args):
    try:
        import nbformat as nbf
    except ImportError:
        raise SystemExit('Install nbformat: pip install nbformat')
    p=ROOT/'probes'/f'{args.idea:03d}'; p.mkdir(parents=True,exist_ok=True)
    nb=nbf.v4.new_notebook()
    nb.cells=[
      nbf.v4.new_markdown_cell(f'# Feasibility probe {args.idea:03d}\nThis notebook treats Colab only as a compute worker.'),
      nbf.v4.new_code_cell("from google.colab import drive\ndrive.mount('/content/drive')"),
      nbf.v4.new_code_cell("REPO_URL = 'PASTE_YOUR_GITHUB_REPO_URL_HERE'\nBRANCH = 'main'"),
      nbf.v4.new_code_cell("!git clone -b {BRANCH} {REPO_URL} /content/concept-research-scout\n%cd /content/concept-research-scout"),
      nbf.v4.new_code_cell(f"!pip install -r probes/{args.idea:03d}/requirements.txt"),
      nbf.v4.new_code_cell(f"!python probes/{args.idea:03d}/run.py --output-dir /content/drive/MyDrive/concept-research-scout-results/{args.idea:03d}"),
    ]
    out=p/f'colab_probe_{args.idea:03d}.ipynb'; nbf.write(nb,out); print(out.relative_to(ROOT))


def record_result(args):
    src=Path(args.result); d=ROOT/'probes'/f'{args.idea:03d}'/'results'; d.mkdir(parents=True,exist_ok=True)
    shutil.copy2(src,d/src.name); print('Copied to', (d/src.name).relative_to(ROOT))
    ledger_mod.raise_scrutiny(f'idea-{args.idea:03d}', 'PROBED', note=f'result {src.name}')
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
    'probe-code':  ['probes/'],
    'scout':       ['ideas/'],
    'wide-scout':  ['ideas/'],
    'fiction-scout':   ['ideas/'],
    'fiction-extract': ['ideas/'],
    'fiction-refine':  ['ideas/'],
    'novelty-audit':   ['ideas/'],
    'librarian':       ['ideas/'],
    'actioner':        ['ideas/'],
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
    print(json.dumps(load_state(),indent=2))
    print('\nIdeas:')
    print(read_text(ROOT/'portfolio'/'ideas.csv'))


BRIEF = ROOT/'evidence'/'portfolio_brief.md'


def _extract_section(body, header):
    import re
    m = re.search(rf'^## {header}\s*$(.*?)(?=^## |\Z)', body, flags=re.M | re.S)
    return m.group(1).strip() if m else ''


def write_portfolio_brief(max_ideas=8, max_chars=1500):
    """Rich context on ACTIONABLE ideas (those with a debate consensus and a
    live status) for portfolio-aware scouting: the verdict, its unblock
    conditions, and unresolved questions. The digest stays the one-line index;
    this is the detail tier for ideas a scout might revive or recombine."""
    entries = ledger_mod.load()
    lines = ['# Portfolio brief (auto-generated; run `python scout.py brief`)', '',
             'Actionable ideas with debate verdicts. A revival/recombination',
             'candidate MUST cite the specific condition below that has changed.', '']
    dirs = sorted((ROOT/'ideas').glob('[0-9][0-9][0-9]'), reverse=True)
    n = 0
    for d in dirs:
        if n >= max_ideas:
            break
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
        lines += ['(No ideas with debate consensus yet.)', '']
    BRIEF.parent.mkdir(parents=True, exist_ok=True)
    BRIEF.write_text('\n'.join(lines) + '\n')
    return BRIEF


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


def _commit_all(message):
    _git('add', '-A')
    r = _git('diff', '--cached', '--quiet', check=False)
    if r.returncode == 0:
        return False  # nothing to commit
    _git('commit', '-q', '-m', message)
    return True


# A stage "succeeding" while producing nothing is how cycle 005 shipped an
# empty candidate pool to the audit. Exit code 0 is not success; the artifact is.
STAGE_ARTIFACTS = {
    'scout': 'scout_candidates.json',
    'wide_scout': 'wide_candidates.json',
    'fiction_scout': 'fiction_story.md',
    'fiction_extract': 'fiction_pitch.md',
    'fiction_refine': 'fiction_candidates.json',
    'novelty_audit': 'novelty_audit.md',
    'librarian': 'librarian_report.md',
    'actioner': 'actions.md',
    'critique': 'critique.md',
    'feasibility': 'feasibility.md',
}


def _require_artifact(stage, target):
    expected = STAGE_ARTIFACTS.get(stage)
    if expected and not (target / expected).exists():
        raise SystemExit(
            f"Stage {stage!r} exited cleanly but did not write {expected!r}. "
            f"Treating as failed. Check {target.relative_to(ROOT)}/log_{stage}.txt "
            f"for what the agent did instead.")


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
                'ledger_id': f'scout-{cycle_no:03d}-fadj',
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
                if c.get('keystone_status') == 'INSPECTED_TRUE' and not c.get('keystone_evidence'):
                    c['keystone_status'] = 'NOT_INSPECTED'
                    c['keystone_demotion'] = 'claimed INSPECTED_TRUE without keystone_evidence'
                    notes.setdefault('keystone_demotions', []) if isinstance(notes.get('keystone_demotions'), list) else None
                    notes['keystone_demotions'] = notes.get('keystone_demotions', []) + [c.get('title', '')[:60]]
                merged.append(c)
        if skipped:
            notes[f'{track}_skipped_stubs'] = skipped
    out = {'cycle': cycle_no, 'tracks': list(tracks), 'notes': notes, 'candidates': merged}
    (target / 'candidates_all.json').write_text(json.dumps(out, indent=2, ensure_ascii=False) + '\n')
    for i, c in enumerate(merged, 1):
        ledger_mod.append({
            'ledger_id': f'scout-{cycle_no:03d}-c{i:02d}',
            'title': c.get('title', ''),
            'claim': c.get('deliverable_sentence') or c.get('question', ''),
            'track': c.get('track', 'baseline'),
            'dataset': (c.get('dataset', {}) or {}).get('name', '') if isinstance(c.get('dataset'), dict) else str(c.get('dataset', '')),
            'status': 'SCOUT_ONLY',
            'scrutiny': 'SCOUTED',
            'scores_mean': _mean_score(c),
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


def cycle(args):
    cfg = load_agent_config()
    tracks = [t.strip() for t in (args.tracks or 'baseline').split(',') if t.strip()]
    bad = [t for t in tracks if t not in TRACKS]
    if bad:
        raise SystemExit(f'Unknown track(s): {", ".join(bad)}. Known: {", ".join(TRACKS)}')
    s = load_state()
    pending = s.get('cycle') and any(v != 'done' for v in s['cycle']['stages'].values())
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
    d = scout_dir(n)
    d.mkdir(parents=True, exist_ok=False)
    (d / 'README.md').write_text(f'# Scouting cycle {n:03d}\n\nTracks: {", ".join(tracks)}\n')
    if not ledger_mod.LEDGER.exists():
        print('Ledger absent; running first-time migration from existing ideas.')
        ledger_mod.migrate()
    ledger_mod.digest()
    write_portfolio_brief()
    s['next_scout'] = n + 1
    s['active_cycle'] = n
    s['cycle'] = {'scout': n, 'tracks': tracks,
                  'seed_concepts': ([x.strip() for x in args.seed_concepts.split(',')][:2]
                                    if getattr(args, 'seed_concepts', None) else None),
                  'started': datetime.now(timezone.utc).isoformat(timespec='seconds'),
                  'stages': {name: 'pending' for name, _ in _cycle_stage_list(tracks)}}
    save_state(s)
    _commit_all(f'cycle {n:03d}: begin (tracks: {", ".join(tracks)})')
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
    print(f"Resuming cycle {n:03d} (tracks: {', '.join(c['tracks'])})")
    for name, st in c['stages'].items():
        print(f'  {name:<16} {st}')
    _cycle_loop(n, scout_dir(n), c['tracks'], load_agent_config())


# ==========================================================================
# Post-scout pipeline: shortlist the strongest candidates of the latest
# completed cycle and drive each through critique/debate, phone-triggerable
# via the idea-pipeline workflow. Idempotent: re-running skips candidates
# already shortlisted and stages whose artifacts already exist, so the same
# button doubles as resume after a failure or job kill.
# ==========================================================================

VERDICT_RANK = {'NOVEL_VERIFIED': 0, 'NOVEL_UNVERIFIED': 1, 'INCREMENTAL': 2,
                'DUPLICATE_PRIOR': 9}


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


def _mean_score(card):
    vals = [v for v in (card.get('scores') or {}).values()
            if isinstance(v, (int, float))]
    return sum(vals)/len(vals) if vals else 0.0


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
        ranked.append((VERDICT_RANK.get(v, 5), -_mean_score(card), i))
    ranked.sort()
    return [i for _, _, i in ranked]


def _latest_scout_no():
    scouts = sorted((ROOT/'ideas').glob('scout-*'))
    if not scouts:
        raise SystemExit('No scouting cycles exist yet.')
    return int(scouts[-1].name.split('-')[1])


def _sync_backlog():
    """Idempotently upsert every scouted candidate of every cycle into the
    ledger with its rubric score and (when the audit exists) novelty verdict.
    Backfills cycles that ran before these fields existed."""
    entries = ledger_mod.load()
    changed = False
    for d in sorted((ROOT/'ideas').glob('scout-*')):
        if not (d/'candidates_all.json').exists():
            continue
        scout_no = int(d.name.split('-')[1])
        try:
            cands = json.loads((d/'candidates_all.json').read_text()).get('candidates', [])
        except json.JSONDecodeError:
            continue
        verdicts = _audit_verdicts(d)
        audited = datetime.now(timezone.utc).isoformat(timespec='seconds') if verdicts else None
        for i, c in enumerate(cands, 1):
            lid = f'scout-{scout_no:03d}-c{i:02d}'
            cur = entries.get(lid, {})
            rec = {'ledger_id': lid}
            if not cur:
                rec.update({'title': c.get('title',''),
                            'claim': c.get('deliverable_sentence') or c.get('question',''),
                            'track': c.get('track','baseline'),
                            'status': 'SCOUT_ONLY', 'scrutiny': 'SCOUTED',
                            'source': str(d.relative_to(ROOT))})
            if cur.get('scores_mean') in (None, '') and _mean_score(c):
                rec['scores_mean'] = _mean_score(c)
            v = verdicts.get(i)
            if v and cur.get('novelty_verdict') != v:
                rec['novelty_verdict'] = v
                rec['audited_at'] = audited
            if len(rec) > 1:
                ledger_mod.append(rec)
                changed = True
    if changed:
        ledger_mod.digest()


def _ranked_backlog():
    """All unshortlisted scouted candidates across every cycle, best first.
    Returns [(scout_no, cand_no, ledger_entry), ...]."""
    _sync_backlog()
    out = []
    for lid, e in ledger_mod.load().items():
        if e.get('status') != 'SCOUT_ONLY':
            continue
        m = __import__('re').match(r'scout-(\d+)-c(\d+)$', lid)
        if not m:
            continue
        v = e.get('novelty_verdict', 'UNAUDITED')
        if v == 'DUPLICATE_PRIOR':
            continue
        rank = {'NOVEL_VERIFIED': 0, 'NOVEL_UNVERIFIED': 1, 'UNAUDITED': 3,
                'INCREMENTAL': 4}.get(v, 5)
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


def _incomplete_pipeline_ideas(stages):
    """Shortlisted ideas whose requested final artifact is missing -- these are
    in-flight and must be finished before new candidates are drawn."""
    final = STAGE_DONE_MARKER.get(stages[-1])
    out = []
    for lid, e in sorted(ledger_mod.load().items()):
        if e.get('status') != 'SHORTLISTED' or not lid.startswith('idea-'):
            continue
        n = int(lid.split('-')[1])
        if final and not (idea_dir(n)/final).exists():
            out.append(n)
    return out


PIPELINE_STAGES = ('critique', 'revise', 'feasibility', 'debate')
STAGE_DONE_MARKER = {'critique': 'critique.md', 'revise': 'idea_card.json',
                     'feasibility': 'feasibility.md', 'debate': 'consensus.md'}


def _pipeline_stage(idea, stage):
    target = idea_dir(idea)
    if stage == 'debate':
        import types
        debate(types.SimpleNamespace(idea=idea, rounds=None))
        if not (target/'consensus.md').exists():
            raise SystemExit(f'Debate for idea {idea:03d} ended without consensus.md.')
        return
    p = write_prompt(stage, target)
    run_agent(p, None, stage=stage, log_path=target/f'log_{stage}.txt')
    _check_scope(stage)
    _require_artifact(stage, target)
    if stage == 'critique':
        ledger_mod.raise_scrutiny(f'idea-{idea:03d}', 'CRITIQUED')
        ledger_mod.digest()


def pipeline(args):
    stages = [x.strip() for x in (args.stages or 'critique,debate').split(',') if x.strip()]
    bad = [x for x in stages if x not in PIPELINE_STAGES]
    if bad:
        raise SystemExit(f'Unknown stage(s): {", ".join(bad)}. Known: {", ".join(PIPELINE_STAGES)}')
    _require_clean_tree('pipeline')
    if args.idea:
        ideas = [args.idea]
    else:
        if args.candidate:
            scout_no = args.scout or _latest_scout_no()
            picks = [(scout_no, args.candidate)]
        else:
            n = max(1, int(args.top or 1))
            inflight = _incomplete_pipeline_ideas(stages)
            if inflight:
                print('Finishing in-flight idea(s) first: '
                      + ', '.join(f'{i:03d}' for i in inflight[:n]))
            rows = _ranked_backlog()
            if args.scout:
                rows = [r for r in rows if r[0] == args.scout]
            print('Backlog (best first): '
                  + (', '.join(f'{s:03d}-C{c}' for s, c, _ in rows[:8]) or '(empty)'))
            picks = [(s, c) for s, c, _ in rows[:max(0, n - len(inflight[:n]))]]
            ideas_prefix = inflight[:n]
        ideas = list(locals().get('ideas_prefix', []))
        for scout_no, cand in picks:
            ideas.append(_do_shortlist(scout_no, cand))
            _commit_all(f'pipeline: shortlist C{cand} of cycle {scout_no:03d}')
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

VALID_VERDICTS = {'NOVEL_VERIFIED', 'NOVEL_UNVERIFIED', 'INCREMENTAL', 'DUPLICATE_PRIOR'}


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
                           'kill_code': code, 'kill_reason': note})
    elif verdict == 'PAUSE':
        ledger_mod.append({'ledger_id': lid, 'status': 'PAUSED', 'notes': note})
    elif verdict in ('REVISE', 'PROCEED'):
        ledger_mod.append({'ledger_id': lid, 'status': 'SHORTLISTED' if verdict == 'REVISE' else 'ACTIVE',
                           'notes': note})
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
    p=sp.add_parser('shortlist'); p.add_argument('scout',type=int); p.add_argument('candidate',type=int); p.add_argument('--track',choices=TRACKS); p.set_defaults(fn=shortlist)
    p=sp.add_parser('run'); p.add_argument('stage',choices=['scout','wide-scout','fiction-scout','fiction-extract','fiction-refine','novelty-audit','critique','revise','feasibility','probe-plan','probe-code','interpret']); p.add_argument('--idea',type=int); p.add_argument('--agent',choices=['claude','codex']); p.set_defaults(fn=run_stage)
    p=sp.add_parser('approve-probe'); p.add_argument('idea',type=int); p.set_defaults(fn=approve_probe)
    p=sp.add_parser('verify-probe'); p.add_argument('idea',type=int); p.set_defaults(fn=verify_probe)
    p=sp.add_parser('package-colab'); p.add_argument('idea',type=int); p.set_defaults(fn=package_colab)
    p=sp.add_parser('record-result'); p.add_argument('idea',type=int); p.add_argument('result'); p.set_defaults(fn=record_result)
    p=sp.add_parser('debate'); p.add_argument('--idea',type=int); p.add_argument('--rounds',type=int); p.set_defaults(fn=debate)
    p=sp.add_parser('status'); p.set_defaults(fn=status)
    p=sp.add_parser('cycle'); p.add_argument('--tracks',default='baseline',help='comma-separated: baseline,wide,fiction'); p.add_argument('--dry-run',action='store_true'); p.add_argument('--resume-or-new',action='store_true'); p.add_argument('--seed-concepts',default=None,help='comma-separated pair to direct the fiction seed (source recorded as human)'); p.set_defaults(fn=cycle)
    p=sp.add_parser('resume'); p.set_defaults(fn=resume)
    p=sp.add_parser('backlog'); p.set_defaults(fn=backlog_cmd)
    p=sp.add_parser('brief'); p.set_defaults(fn=brief_cmd)
    p=sp.add_parser('librarian'); p.add_argument('--agent',choices=['claude','codex']); p.set_defaults(fn=librarian)
    p=sp.add_parser('actioner'); p.add_argument('--improve',action='store_true'); p.add_argument('--agent',choices=['claude','codex']); p.set_defaults(fn=actioner)
    p=sp.add_parser('pipeline'); p.add_argument('--top',type=int); p.add_argument('--scout',type=int); p.add_argument('--candidate',type=int); p.add_argument('--idea',type=int); p.add_argument('--stages',default='critique,debate'); p.set_defaults(fn=pipeline)
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
