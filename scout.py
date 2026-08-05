#!/usr/bin/env python3
"""Lightweight orchestration for Concept Research Scout.

No expensive compute is launched automatically. Agent CLI commands are best-effort
because vendor flags change; every stage also writes a complete prompt file that
can be handed to an agent manually.
"""
from __future__ import annotations
import argparse, csv, json, os, shutil, subprocess, sys, textwrap
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
STATE = ROOT/'orchestrator'/'state.json'
PROMPTS = ROOT/'orchestrator'/'prompts'


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


def build_prompt(stage, target):
    files = [ROOT/'CHARTER.md', ROOT/'docs'/'COLLABORATOR_RULES.md', ROOT/'docs'/'SCORING_RUBRIC.md']
    context = '\n\n'.join(f'===== {p.relative_to(ROOT)} =====\n{read_text(p)}' for p in files)
    if target.exists():
        for p in sorted(target.glob('*')):
            if p.is_file() and not p.name.startswith('prompt_') and p.suffix.lower() in {'.md','.json','.yaml','.yml','.csv'}:
                context += f'\n\n===== {p.relative_to(ROOT)} =====\n{read_text(p)}'
    task = read_text(PROMPTS/f'{stage}.md')
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


def run_agent(prompt_path, agent=None, stage=None):
    cfg = load_agent_config()
    if agent is None and stage:
        agent = cfg.get('roles', {}).get(stage.replace('-', '_'))
    agent = agent or cfg.get('default',{}).get('agent','claude')
    print(f'[stage={stage} agent={agent}]')
    acfg = cfg.get(agent,{})
    if not acfg.get('enabled', False):
        print(f'Agent {agent!r} is disabled. Use this prompt manually:\n{prompt_path}')
        return
    command = acfg.get('command', [])
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
    try:
        proc = subprocess.run(command, cwd=ROOT, text=True, timeout=3600,
                              input=stdin_text)
    except subprocess.TimeoutExpired:
        raise SystemExit('Agent timed out after one hour.')
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
            print(f'  {k:<12} -> {v}' + ('' if en else '   [DISABLED - fix AGENTS.toml]'))
        concrete = [v for v in roles.values() if v != 'alternating']
        if len(set(concrete)) < 2:
            print('  WARNING: one model holds every role. It will be critiquing itself.')
    else:
        print('\nNo [roles] table in AGENTS.toml - all stages use the default agent.')
    print('\nColab execution is intentionally optional. package-colab creates a launcher notebook.')


def new_scout(_):
    s=load_state(); n=s['next_scout']; d=scout_dir(n); d.mkdir(parents=True,exist_ok=False)
    (d/'README.md').write_text(f'# Scouting cycle {n:03d}\n\nCandidate portfolio before idea selection.\n')
    s['next_scout']=n+1; save_state(s)
    p=write_prompt('scout',d)
    print(d.relative_to(ROOT)); print('Prompt:',p.relative_to(ROOT))


def shortlist(args):
    src=scout_dir(args.scout)/'scout_candidates.json'
    if not src.exists(): raise SystemExit(f'Missing {src}. Run or complete the scout stage first.')
    data=json.loads(src.read_text()); candidates=data.get('candidates',data if isinstance(data,list) else [])
    idx=args.candidate-1
    if idx<0 or idx>=len(candidates): raise SystemExit('Candidate index out of range.')
    existing=[int(p.name) for p in (ROOT/'ideas').iterdir() if p.is_dir() and p.name.isdigit()]
    n=max(existing,default=0)+1; d=idea_dir(n); d.mkdir()
    card=candidates[idx]; (d/'idea_card.json').write_text(json.dumps(card,indent=2)+'\n')
    (d/'README.md').write_text(f"# Idea {n:03d}: {card.get('title','Untitled')}\n\nSelected from scouting cycle {args.scout:03d}, candidate {args.candidate}.\n")
    s=load_state(); s['selected_idea']=n; save_state(s)
    with (ROOT/'portfolio'/'ideas.csv').open('a',newline='') as f:
        csv.writer(f).writerow([f'{n:03d}',card.get('title',''), 'ACTIVE','',card.get('scores',{}).get('regret',''),'CRITIQUE',''])
    print(f'Shortlisted as idea {n:03d}')


def stage_target(stage, idea):
    if stage=='scout':
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
    run_agent(p, args.agent, stage=args.stage)
    _check_scope(args.stage)


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



# --------------------------------------------------------------------------
# Debate: bounded alternating exchange between the two model families.
# Both sides read the whole transcript each round. Terminates on agreement,
# on max_rounds, or when a side declares the disagreement irreducible.
# --------------------------------------------------------------------------

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
    proposer = dcfg.get('proposer', 'claude')
    critic = dcfg.get('critic', 'codex')
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
        return _close_debate(target, critic)

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
            return _close_debate(target, critic)
    print(f'\nReached max_rounds={max_rounds} without convergence.')
    _close_debate(target, critic)


def _close_debate(target, critic):
    p = write_prompt('debate_summary', target)
    run_agent(p, critic, stage='debate-summary')
    _check_scope('debate')
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


def main():
    ap=argparse.ArgumentParser(); sp=ap.add_subparsers(dest='cmd',required=True)
    p=sp.add_parser('doctor'); p.set_defaults(fn=doctor)
    p=sp.add_parser('new-scout'); p.set_defaults(fn=new_scout)
    p=sp.add_parser('shortlist'); p.add_argument('scout',type=int); p.add_argument('candidate',type=int); p.set_defaults(fn=shortlist)
    p=sp.add_parser('run'); p.add_argument('stage',choices=['scout','critique','revise','feasibility','probe-plan','probe-code','interpret']); p.add_argument('--idea',type=int); p.add_argument('--agent',choices=['claude','codex']); p.set_defaults(fn=run_stage)
    p=sp.add_parser('approve-probe'); p.add_argument('idea',type=int); p.set_defaults(fn=approve_probe)
    p=sp.add_parser('verify-probe'); p.add_argument('idea',type=int); p.set_defaults(fn=verify_probe)
    p=sp.add_parser('package-colab'); p.add_argument('idea',type=int); p.set_defaults(fn=package_colab)
    p=sp.add_parser('record-result'); p.add_argument('idea',type=int); p.add_argument('result'); p.set_defaults(fn=record_result)
    p=sp.add_parser('debate'); p.add_argument('--idea',type=int); p.add_argument('--rounds',type=int); p.set_defaults(fn=debate)
    p=sp.add_parser('status'); p.set_defaults(fn=status)
    args=ap.parse_args(); args.fn(args)

if __name__=='__main__': main()
