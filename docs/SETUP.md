# Setup — from zero to your first idea list

Assumes you have never used a terminal for this kind of thing. Read the whole
of a step before typing anything.

Total time: **60–90 minutes** if Node.js is already installed, **2 hours** if
not. Roughly 40 minutes of that is installing and logging in; the rest is the
first scout cycle.

---

## Step 0 — What you need

- A computer where you can install software (macOS or Linux; on Windows use
  WSL, since the Colab CLI does not support Windows natively).
- Your ChatGPT subscription and your Claude subscription.
- A GitHub account (free tier is fine).

You do **not** need API keys. Both CLIs log in against your existing
subscription.

---

## Step 1 — Open a terminal (2 min)

**macOS:** press ⌘+Space, type `Terminal`, hit enter.
**Linux:** Ctrl+Alt+T.
**Windows:** install WSL first (`wsl --install` in PowerShell as admin, then
reboot), then open "Ubuntu" from the Start menu.

Check what you already have. Type each line, press enter:

```bash
git --version
node --version
python3 --version
```

Anything that says "command not found" needs installing in Step 2.

---

## Step 2 — Install the basics (5–20 min)

**macOS** (installs Homebrew first if you lack it):

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
brew install git node python@3.12
```

**Ubuntu / WSL:**

```bash
sudo apt update
sudo apt install -y git python3 python3-pip curl
curl -fsSL https://deb.nodesource.com/setup_22.x | sudo -E bash -
sudo apt install -y nodejs
```

Verify: `node --version` should print v20 or higher.

---

## Step 3 — Install the two agents (10 min)

```bash
npm install -g @anthropic-ai/claude-code
npm install -g @openai/codex
```

If either errors with a permissions complaint, prefix with `sudo` on Linux,
or set an npm prefix you own:

```bash
mkdir -p ~/.npm-global && npm config set prefix ~/.npm-global
echo 'export PATH=~/.npm-global/bin:$PATH' >> ~/.bashrc && source ~/.bashrc
```

Now log both in. Each opens a browser window; sign in with the account that
holds your subscription.

```bash
claude          # then type /login , follow the browser, then /exit
codex login
```

Verify both work — and test **piped** prompts, because that is how the
orchestrator actually delivers them:

```bash
claude -p "reply with just the word ready"
codex exec "reply with just the word ready"

printf 'Reply with exactly PIPE_WORKS and nothing else.' | claude -p
printf 'Reply with exactly PIPE_WORKS and nothing else.' | codex exec -
```

All four must work. The last two matter most: every stage pipes its prompt on
stdin. If a piped call returns something odd instead of PIPE_WORKS, the agent
is reading the prompt wrongly and every downstream stage will be garbage.

**If the codex command errors**, run `codex exec --help` and note the correct
syntax. Then open `AGENTS.toml` and edit the `[codex] command` line to match.
This is the single most likely thing to break, because these CLIs change.

---

## Step 4 — Get the repo onto your machine (5 min)

Unzip the folder you were given, then:

```bash
cd ~/Desktop/concept-research-scout      # adjust path to wherever you unzipped
python3 tests/test_orchestration.py      # 7 tests, ~1 second, no network
python3 scout.py doctor
```

The tests use a fake agent, so they check the plumbing (stdin delivery, scope
enforcement, debate termination) without touching either real CLI. All 7
must pass. If they don't, stop — nothing downstream will be trustworthy.

You want to see `OK` on the four files, paths for `git`, `claude`, `codex`,
and a role table with **two different model names in it**. If the role table
warns that one model holds every role, stop and fix `AGENTS.toml`.

---

## Step 5 — Put it on GitHub (10 min)

Yes — GitHub is where all of this lives. The repo is the memory: every idea,
critique, contract, and result is a small text file committed there, so the
agents can read the history and so you can review it from anywhere.

1. Go to github.com, click **+** → **New repository**.
2. Name it `concept-research-scout`. Set it to **Private**.
3. Do **not** tick "add a README" — you already have one.
4. Click Create. GitHub shows you a URL like
   `https://github.com/YOURNAME/concept-research-scout.git`.

Back in the terminal:

```bash
git init
git add -A
git commit -m "initial scaffold"
git branch -M main
git remote add origin https://github.com/YOURNAME/concept-research-scout.git
git push -u origin main
```

It will ask for credentials. Use a personal access token, not your password:
GitHub → Settings → Developer settings → Personal access tokens → Tokens
(classic) → Generate new token → tick `repo` → copy it → paste it as the
password.

**Commit before every stage, not just after.** Stages refuse to run on a
dirty working tree, because a stage can only be held to its file scope if the
starting state is known. So the rhythm is: commit, run stage, review, commit.

**After every stage:**

```bash
git add -A && git commit -m "what just happened" && git push
```

Do this even when nothing interesting happened. The commit history is the lab
notebook.

---

## Step 6 — Your first scout cycle (20 min)

```bash
python3 scout.py new-scout
python3 scout.py run scout
```

Claude reads the charter and writes `scout_candidates.json` with six candidate
ideas into `ideas/scout-001/`. Open it and read it properly:

```bash
cat ideas/scout-001/scout_candidates.json
```

**Read every candidate before doing anything else.** Check the "closest prior
work" identifiers against reality — search for one or two of the cited papers
and confirm they exist and say what the agent claims. Fabricated citations are
the most common failure at this stage.

Commit:

```bash
git add -A && git commit -m "scout cycle 001" && git push
```

---

## Step 7 — Put one idea through critique (15 min)

Pick the candidate you find most interesting. If it's the third one:

```bash
python3 scout.py shortlist 1 3
python3 scout.py run critique
cat ideas/001/critique.md

python3 scout.py debate --rounds 3
cat ideas/001/debate.md
cat ideas/001/consensus.md
```

`critique` is one shot. `debate` is the back-and-forth: Codex attacks, Claude
rebuts or concedes, repeat, until they converge, declare the disagreement
irreducible, or hit the round cap. Then Codex writes `consensus.md`
separating what both sides agree on from what they don't.

This is the moment of truth. **Codex is running critique and debate, not
Claude.** Read `debate.md` and check three things:

1. Did the critic raise a specific objection — a named paper, a metric, a
   confound — or a vague worry?
2. When someone conceded, did they concede to an *argument*, or did they just
   fold to be agreeable? `consensus.md` flags this as UNEARNED. Unearned
   concessions are the main failure mode of model debate: both sides drift
   toward agreement because agreement is the socially trained behaviour, and
   a two-round capitulation reads exactly like consensus.
3. Did it converge in round one with nothing raised? That tells you the
   critic is decorative.

If any of those look wrong, sharpen `orchestrator/prompts/debate_critic.md`
and re-run before going further.

A healthy first few cycles kill most candidates. That is the system working.

---

## Where to stop, the first day

Stop after Step 7. Do not run `feasibility`, `probe-plan`, or `probe-code`
yet, and do not touch Colab.

Run three or four scout-and-critique cycles across different days first. You
are testing one thing: **does the critic actually reject things?** If
everything passes, running experiments would just be expensive noise. Fix the
critic before you spend a single GPU-minute.

---

## Later: the rest of the pipeline

Once you trust the critic, the full sequence for an idea is:

```bash
python3 scout.py run revise --idea 1
python3 scout.py run feasibility --idea 1
python3 scout.py run probe-plan --idea 1
cat ideas/001/probe_contract.yaml    # READ THIS. It is the pre-registration.
python3 scout.py approve-probe 1     # your explicit sign-off
python3 scout.py run probe-code --idea 1
python3 scout.py verify-probe 1      # local syntax + smoke test, no GPU
python3 scout.py package-colab 1     # makes a notebook
# open that notebook in Colab, paste your repo URL, run it
python3 scout.py record-result 1 /path/to/summary.json
python3 scout.py run interpret --idea 1
```

`probe-code` is hard-blocked until `approve-probe` has been run, and
`approve-probe` requires a feasibility memo. That gate is deliberate. Do not
route around it.

Read `probe_contract.yaml` carefully before approving — its `positive_pattern`
and `negative_pattern` fields are what the interpretation stage will be scored
against. Getting those wrong is how a loop like this turns into p-hacking with
extra steps.

---

## Troubleshooting

| Symptom | Fix |
|---|---|
| `claude: command not found` | npm global bin not on PATH; see Step 3 |
| codex stage does nothing | run `codex exec --help`, fix `[codex] command` in AGENTS.toml |
| Agent hangs past an hour | it times out on its own; check the printed prompt file and run it manually |
| `doctor` warns one model holds every role | `[codex] enabled` is false, or the `[roles]` table is missing |
| Citations in candidates look wrong | they probably are; verify manually, always |
| Piped test returns a file path or junk | agent isn't reading stdin; check `stdin` flag in AGENTS.toml |
| SCOPE VIOLATION printed after a stage | agent wrote outside its lane; `git diff` then `git checkout -- <file>` |
| Debate converges instantly every time | critic prompt is too soft; make `debate_critic.md` harsher |
| "Working tree is not clean" | commit or stash first: `git add -A && git commit -m wip` |
| git push asks for a password | use a personal access token (Step 5) |

Every stage writes its full prompt to a file before invoking anything. If the
automation breaks, you can always paste that file into the Claude or ChatGPT
web interface by hand and save the output where the stage expected it. The
orchestration is a convenience, not a dependency.
