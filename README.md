# Concept Research Scout

A lightweight, human-supervised research discovery loop for finding **interesting, feasible, concept-focused medical-imaging projects**—especially partially completed research stories and meaningful “low-hanging fruit.”

The system deliberately delays coding. It first scouts literature-grounded ideas, stress-tests them through agent debate, verifies data and implementation feasibility, and only then permits a small computational probe.

## What this is

- A research-idea incubator, not an autonomous scientist.
- A structured memory for candidate ideas, evidence, rejected directions, and negative results.
- A way to use Claude Code and/or Codex as research collaborators.
- A bridge to Colab for bounded feasibility experiments.

## What this is not

- A publication generator.
- A license to claim novelty from model memory.
- A system that optimizes until something becomes positive.
- A replacement for human review of medical relevance, leakage, or conclusions.

## The funnel

1. **Scout**: Generate a portfolio of grounded candidate ideas.
2. **Debate**: Proposer and critic refine one idea over multiple rounds.
3. **Verify**: Check closest papers, dataset access, labels, compute, and evaluation.
4. **Probe plan**: Define the smallest test of the riskiest assumption.
5. **Probe**: Generate and run minimal code only after human approval.
6. **Interpret**: Record positive, negative, ambiguous, and invalid outcomes.
7. **Decide**: Advance, revise, pause, or reject.

## Fast setup

Requirements: Python 3.10+, Git, and at least one supported coding-agent CLI.

```bash
unzip concept-research-scout.zip
cd concept-research-scout
python setup.py
python scout.py doctor
```

Optional agent CLIs:

```bash
npm install -g @anthropic-ai/claude-code
npm install -g @openai/codex
```

Then edit `CHARTER.md` and run:

```bash
python scout.py new-scout
python scout.py run scout
```

The command prints the output paths and never launches expensive compute without an explicit command.

## Minimal manual workflow

You can use the repository even without CLI automation:

1. Give `CHARTER.md`, `docs/COLLABORATOR_RULES.md`, and the relevant prompt under `orchestrator/prompts/` to Claude.
2. Ask it to write the named output into the current idea folder.
3. Review the short artifact.
4. Move to the next stage only when satisfied.

## Typical commands

```bash
python scout.py new-scout                 # create a scouting cycle
python scout.py run scout                 # ask an agent for candidate ideas
python scout.py shortlist 001 2           # select candidate 2
python scout.py run critique --idea 001   # adversarial critique
python scout.py run revise --idea 001     # revise after critique
python scout.py run feasibility --idea 001
python scout.py approve-probe 001         # explicit human gate
python scout.py run probe-plan --idea 001
python scout.py run probe-code --idea 001
python scout.py verify-probe 001          # deterministic checks
python scout.py package-colab 001         # create a small Colab launcher
python scout.py record-result 001 result.json
python scout.py run interpret --idea 001
python scout.py status
```

## Repository layout

```text
CHARTER.md                     standing research interests and constraints
AGENTS.toml                    optional agent CLI configuration
scout.py                       lightweight orchestration CLI
setup.py                       one-command local initialization
portfolio/ideas.csv            ranked idea portfolio
ideas/NNN/                     complete record for one idea
  idea_card.json
  critique.md
  revision.md
  feasibility.md
  probe_contract.yaml
  decision.md
probes/NNN/                    minimal probe code and outputs
  run.py
  requirements.txt
  README.md
  results/
evidence/                      literature and dataset evidence ledger
templates/                     schemas and examples
docs/                          rules, scoring rubric, and handoff guide
```

## Recommended operating principle

The objective is not “maximize performance.” It is:

> Resolve a worthwhile scientific uncertainty as cheaply, clearly, and honestly as possible.

A clean negative result is success. An invalid experiment is not a negative result. Exploratory findings remain exploratory until independently tested.

## Revamp additions (cycle 2+)

```
python scout.py cycle --tracks baseline,wide,fiction   # multi-track scouting cycle
python scout.py cycle --dry-run                        # print plan, spend nothing
python scout.py resume                                 # continue after limit/timeout
python scout.py ledger list|show|search|kill|taxonomy  # idea ledger (ledger.jsonl)
```

- Every completed stage is a git commit (the checkpoint). A failed stage
  commits partial output; `resume` picks up at the first incomplete stage.
- `[rotation]` in AGENTS.toml swaps the two model families on odd cycles.
- Fiction track: blind seeded story -> extraction -> cross-family refinement
  with a NO_TESTABLE_KERNEL exit. See REVAMP.md for the design and the
  planned head-to-head demo.
- Remote operation: `.github/workflows/scout-cycle.yml` (mobile Run-workflow
  button + nightly cron). Setup steps: REVAMP.md "First-run checklist".
