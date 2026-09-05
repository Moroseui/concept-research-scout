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

## Acknowledgments

Developed within a supervised undergraduate research program in
medical-imaging AI. Direction and dataset focus are set with the
supervising principal investigator; formal attribution accompanies any
publication arising from this work.

## Operator command reference

Standing rule (R5c): every patch touching the operator surface updates
this reference in the same patch; `TestDocsHygiene` fails CI if any CLI
subcommand is missing here.

### Command index

| command | purpose |
|---|---|
| `actioner` | aggregate everything awaiting the human into a phone-readable brief |
| `amend-contract` | fill a contract's frozen Phase-S placeholders from the simulation summary (blob changes; re-approval required) |
| `approve-probe` | human approval gate binding the contract blob (and registry sha when present) |
| `backlog` | show the ranked cross-cycle idea backlog |
| `brief` | print the current operator brief |
| `bundle-complete` | report whether an idea's imported bundle reached a study-terminal status |
| `card-materialize` | render the deterministic Research Card view (`--check` verifies byte-identity) |
| `confer` | cross-family reviewed, read-only Q&A about one idea, grounded on its card (see below) |
| `cycle` | run one scout generation cycle (tracks → merge → novelty → backlog) |
| `debate` | run the bounded cross-family debate stage for an idea |
| `diversity` | report idea-space diversity metrics |
| `doctor` | environment and configuration sanity checks |
| `interpret-build` | cross-family adversarial interpretation of an imported bundle (`--resume-review` resumes at the review leg) |
| `kill` | record a taxonomy-coded kill for an idea |
| `ledger` | ledger operations (nested subcommands, e.g. `set-status`) |
| `librarian` | build the whole-corpus dossier |
| `new-scout` | seed a new scouted idea entry |
| `package-colab` | render the frozen Colab launcher notebook for an approved probe |
| `pipeline` | run shortlist → critique → debate over backlog picks |
| `probe-build` | cross-family authoring of probe code under the approved contract |
| `ratify-interpretation` | human authority transaction closing an interpretation: event + status + state, one commit |
| `run STAGE --idea N [--unblock-ack "ruling"]` | stages; `revise` refuses under a debate human-unblock until the ruling is acknowledged (round-10 P0) |
| `ratify-registry` | registry-ratification authority transaction: mechanically verified bindings + imports, event, derive-to-COMPLETE, state, one commit |
| `record-result` | validate and import a results bundle; PROBED + digest + state in one transaction |
| `registry-status` | derive a per-idea experiment registry's node statuses |
| `registry-validate` (round-10: mechanically re-proves every ratification's bindings and imports; forged-but-well-formed rows fail loudly) | validate registries (schema, containment, governance events) |
| `resume` | resume an interrupted run |
| `run` | run a single named stage for an idea |
| `search` | novelty/literature search stage |
| `set-status` | (under `ledger`) append a lifecycle status transition |
| `shortlist` | promote top backlog ideas into the pipeline |
| `show` | display an idea's artifacts and summary |
| `state-materialize` | regenerate the derived per-idea state view(s) |
| `state-verify` | byte-verify state views against regeneration (`--require-all`) |
| `status` | print overall system status |
| `validate-bundle` | deterministic bundle validation (the import gate; registry nodes validate under their governing blob) |
| `verify-probe` | verify the built probe against its contract |

### New or changed this sprint

**`confer IDEA "question"`** — a bounded, READ-ONLY, receipted exchange
about one idea. Inputs: idea number; a free-text question (premises that
conflict with the evidence get a cited PREMISE CHECK, not compliance).
Context: `ideas/NNN/CARD.md` (required — run `card-materialize` first)
plus the idea's interpretation/review/decision documents, hash-bound in
`qNNNN_grounding.json`. Two legs, families **swapping across
exchanges** (exchange 1: claude drafts, codex reviews; exchange 2
swaps; `roles.confer` / `roles.confer_review` in AGENTS.toml override):
the draft must lead with a plain-language `## OVERVIEW` any reader can
understand, then cited `## DETAILS`; the opposing family reviews six
meat-level properties (thesis vs evidence, overview fidelity, citations,
premise-check appropriateness, claim bounds, question coverage /
unresolved assumptions) → CONCUR or CONTEST → one
bounded revision → a second CONTEST stops for the operator. Outputs
under `ideas/NNN/confer/`: `qNNNN.md` (answer), `qNNNN_review.md`
(verdict json at tail), prompts, grounding, logs; every leg committed.
Touches no authority surface; suggestions are advisory-only.

**`card-materialize IDEA [--check]`** — renders `ideas/NNN/CARD.md`,
the deterministic Research Card (identity, question, declared-vs-derived
status with drift flagged, contract lineage, position, headline
results, authority hashes, connections via optional
`related_ideas` in `idea_card.json`, documents). `--check` refuses
stale bytes, mirroring the state invariant.

**`ratify-interpretation IDEA --status S`** — verifies six identities
(interpretation, review, its APPROVE verdict, decision, governing
contract, validated bundle), then one transaction: ledger
`INTERPRETATION_RATIFIED` event with all hashes → digest →
re-materialize → verify → commit. Refuses without machine APPROVE.

**`record-result IDEA --bundle DIR [--expected-blob BLOB --source-commit SHA]`**
— the import gate, transactional, and now with the historical lane
(R3b): a pinned import validates under its own contract, must match the
source commit's tree byte-for-byte (verbatim check), the source snapshot
must carry the approval binding that pin (ancestry refusal), the
destination is `results_v2-<blob12>`, and every import writes an
authority receipt (`<dest>.import.json`: source commit, manifest
sha256) that ratification later re-verifies.

**`ratify-registry IDEA --operator NAME`** — the R3b authority
transaction: derives bindings from approval-marker history and verifies
each mechanically (marker bytes at the bound commit hash to the recorded
sha AND textually bind the pin), re-verifies every import receipt
(manifest + ancestry), appends the REGISTRY_RATIFIED event, requires
every node to derive COMPLETE, re-materializes state and the research
card, and commits once. Refusals name their forgery class.

**`interpret-build IDEA [--resume-review]`** — the flag resumes at the
review leg when a committed round-1 interpretation exists (an
infrastructure failure must not burn a good leg).

### Phone surfaces (GitHub Actions → Run workflow)

`interpret` (idea, resume_review) and `confer` (idea, question) run the
corresponding commands on Actions with tests-first and fail-closed
push; `actioner` renders the operator brief. Codex participates in one
leg of every confer and in interpret reviews. Durable auth: set the
`OPENAI_API_KEY` repository secret and Actions uses it (no rotation, no
refresh dance; local codex keeps the ChatGPT login untouched). Without
it, workflows fall back to the `CODEX_AUTH_JSON` OAuth snapshot, which
must be re-exported immediately before dispatch (single-use refresh
chain).

### ISLES autonomous pilot publication safeguards

`package-colab` now preserves outputs on reruns, captures actual child console
output in the sibling `<OUTPUT_DIR>.console.log`, and exports only an explicitly
permitted, contract-bound file set from `probes/NNN/publication.json`. Unknown
files, symlinks and conflicting destinations refuse before publication. It no
longer automatically commits or pushes results. Empty-directory runners require
a new output path for another attempt; resumable runners keep their checkpoints.
Return the verified export and sibling console for validation and import.

Campaign progress: [ISLES pilot](docs/isles-pilot/PROGRESS.md). Dataset attribution:
[ISLES24 notice](docs/isles-pilot/DATASET_NOTICE.md).

`record-result IDEA --bundle DIR --expected-blob BLOB --source-commit SHA
--publication-subset DECLARATION.json` accepts an explicit provenance-bound
publication subset: every source file accounted for, retained bytes identical,
required audit/science retained, and staged-input exclusions tied to preserved
private originals. The 047 policy remains blocked pending its open decisions.
