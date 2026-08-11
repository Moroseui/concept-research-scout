# Concept Research Scout

A human-supervised research discovery loop for finding **interesting,
feasible, concept-focused medical-imaging projects** — run by two AI agent
families (Claude and Codex) under strict evidence rules, operated entirely
from a phone via three GitHub Actions buttons, with every artifact and
decision versioned in this repository.

The system deliberately delays coding. It scouts literature-grounded ideas,
audits their novelty by search, stress-tests survivors through cross-model
debate, and only then permits a small human-approved computational probe.
A clean negative result is success; an invalid experiment is not a negative
result.

**Read next:** `docs/ARCHITECTURE.md` for *why* each mechanism exists (each
one traces to a specific failure or finding), `REVAMP.md` for what is done
versus pending, `CHARTER.md` for the research scope and evidence rules.

## The loop

```
        (nightly cron, or Run workflow)             (Run workflow)
 ┌─────────────── scout-cycle ───────────────┐   ┌─ idea-pipeline ─┐
 │ scout tracks: baseline | wide | fiction   │   │ shortlist top-N │
 │      -> merge -> novelty audit            │──>│ from BACKLOG    │
 │      -> ranked cross-cycle BACKLOG        │   │ -> critique     │
 └───────────────────────────────────────────┘   │ -> debate       │
                                                 │ -> verdict      │
 ┌─────────────── librarian ─────────────────┐   │    -> ledger    │
 │ on demand: whole-corpus dossier ->        │   └────────┬────────┘
 │ connection map + stale-verdict re-audit   │            │ human reads
 │ + revival proposals for future scouts     │            v consensus.md
 └───────────────────────────────────────────┘   PAUSE / REVISE / KILL /
                                                 PROCEED -> feasibility ->
                                                 human-approved probe
```

Everything runs on GitHub-hosted runners using subscription (not API) agent
auth. Every completed stage is a git commit — the commit *is* the
checkpoint, so any failure (rate limit, timeout, job kill) costs one stage
and the same button resumes it.

## Operating it (the three buttons)

**scout-cycle** — feeds the queue. Inputs: `tracks`
(`baseline`,`wide`,`fiction`, comma-separated) and `dry_run` (print the plan,
spend nothing). Also runs nightly (baseline-only) on cron. Each cycle:
scouts per track, merges candidates, audits novelty by literature search,
and files everything into the cross-cycle backlog.

**idea-pipeline** — drains the queue. `top_n: N` processes the next N
candidates from the *global ranked backlog* (best verdict first, then rubric
score; in-flight ideas are finished before new ones are drawn, so the button
doubles as resume). Or target `candidate: K` / `idea: N` with a `stages`
list (`keystone,critique,revise,feasibility,debate`). Every idea first passes a **keystone screen** -- one cheap
evidence-quoting agent pass (clone the repo, read the loader, check the
release page) that can kill at screen prices before critique or debate is
paid for. Debate summaries end in a
machine-readable verdict that updates the ledger automatically; a REVISE
verdict also auto-runs the revise stage in the same job, and a
`revise_debt` toggle batch-syncs any stale REVISE-verdicted cards.

**actioner** — synthesizes the state. Aggregates every pending human
decision, unblock condition, near-miss, queue snapshot, and the latest
librarian findings into one phone-readable brief (`evidence/actions.md`).
With `propose_improvement` enabled it may additionally author **one pull
request** — never a commit to main; the PR diff, the checks workflow's test
run, and your merge button are the approval gate.

**librarian** — curates the corpus. Manual-only (it costs tokens per entry).
Reads a full-detail dossier of every idea and backlog candidate, writes a
connection map, re-audits stale novelty verdicts (applied to the ledger),
and leaves revival/recombination proposals that future scouting cycles may
adopt.

The human gates are: reading each idea's `consensus.md` before acting on it,
`approve-probe` before any code is generated, and interpreting probe
results. Nothing launches expensive compute without an explicit command.

## Institutional memory (what the agents know)

- `ledger.jsonl` — append-only event log; one row per idea/candidate with
  status, scrutiny level (SCOUTED < CRITIQUED < DEBATED < PROBED), novelty
  verdict + audit date, kill code from a controlled taxonomy, and lineage
  (`parent_ids`).
- `evidence/ledger_digest.md` — regenerated each cycle; the one-line index
  of everything plus the **kill-code frequency table** (used as a
  generation-time checklist) and the ranked candidate backlog. In every
  non-blind prompt.
- `evidence/portfolio_brief.md` — full verdicts, unblock conditions, and
  unresolved questions for actionable (paused/revisable) ideas; enables
  bounded revival/recombination candidates in scouting.
- `evidence/librarian_proposals.md` — standing suggestions from the last
  librarian pass.
- `evidence/decisions.md` — human decision log, injected into all prompts.

The one deliberate exception: the fiction-track story writer sees none of
this (enforced by tests) — divergence runs memory-blind.

## Local commands

```bash
python scout.py doctor                      # environment + role/rotation check
python scout.py cycle --tracks baseline,wide,fiction [--dry-run] [--seed-concepts "a,b"]
python scout.py resume                      # continue an interrupted cycle
python scout.py pipeline --top 2            # shortlist+critique+debate next 2 from backlog
python scout.py pipeline --idea 13 --stages revise
python scout.py librarian                   # whole-corpus curation pass
python scout.py backlog                     # print the ranked queue
python scout.py brief                       # regenerate the portfolio brief
python scout.py ledger list|show|search|kill|set-status|taxonomy
python scout.py approve-probe N | verify-probe N | package-colab N | record-result N f
python scout.py status
```

## Repository layout

```text
CHARTER.md                  research scope, hard constraints, evidence rules
AGENTS.toml                 agent commands, roles, [rotation], [limits], CI variants
scout.py                    all orchestration (cycles, pipeline, librarian, ledger glue)
orchestrator/
  ledger.py                 append-only ledger, kill taxonomy, digest
  prompts/*.md              one prompt file per stage (incl. fiction_* and librarian)
  seeds.json                fiction seed deck (concepts, datasets, twist cards)
ledger.jsonl                the event log (created on first cycle)
ideas/
  NNN/                      one idea: card, critique, debate, consensus, logs
  scout-NNN/                one scouting cycle: per-track candidates, merged pool,
                            novelty audit, fiction story/pitch, agent logs
  librarian-NNN/            one librarian pass: dossier, report, updates
probes/NNN/                 human-approved probe code + results
evidence/                   digests, briefs, proposals, decisions, datasets
portfolio/ideas.csv         flat idea list (legacy view; ledger is authoritative)
templates/                  idea-card schema, probe contract
tests/test_orchestration.py deterministic suite (fake agents; run in CI first)
.github/workflows/          scout-cycle, idea-pipeline, librarian, checks
docs/ARCHITECTURE.md        design rationale: every mechanism and why it exists
REVAMP.md                   done/pending punch-list with designs for pending work
```

## Safety and honesty invariants

- **Artifact contracts**: an agent exiting cleanly without writing its
  required output is a *failed* stage, never a silent success.
- **Scope guard**: each stage may touch only its allowed paths; violations
  fail the stage (enforced by git, not by asking nicely).
- **Keystone evidence**: `INSPECTED_TRUE` claims without a quoted artifact
  are mechanically demoted to `NOT_INSPECTED` at merge.
- **No novelty from memory**: novelty claims require searched, cited
  neighbors; `NO_NEIGHBORS_FOUND` flags for human check, never counts as
  proof.
- **Blindness**: fiction writer sees no charter/memory; fiction refiner
  never sees the story or seed; debate cannot end on one side's say-so.
- Full rationale for each: `docs/ARCHITECTURE.md`.

## First-time setup

See `REVAMP.md` "First-run checklist" (secrets, spending cap, smoke test)
and `docs/SETUP.md` for local details. Requirements: Python 3.10+, git, and
the two agent CLIs for local runs (`npm i -g @anthropic-ai/claude-code
@openai/codex`).
