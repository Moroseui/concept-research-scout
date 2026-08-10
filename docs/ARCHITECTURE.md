# Architecture and design rationale

This document explains **why** each mechanism exists. Almost every feature in
this system traces to a specific observed failure, a documented finding in the
agentic-research literature, or both. Reading this alongside the README should
let a newcomer reconstruct not just how the system works but why it is shaped
this way. (Status of pending work: `REVAMP.md`. Research scope: `CHARTER.md`.)

## The founding observation

Cycle one (pre-revamp) debated eleven ideas and killed all eleven — nine of
them for the same reason: designs that measured what a model *associates* with
a concept rather than whether it *uses* it. Cheap deaths are the system
working; the same death nine times is a generation problem being caught at
debate prices. Nearly everything below descends from that post-mortem, plus a
comparative survey of published agentic-research systems (AI Co-Scientist,
AI Scientist v1/v2, Robin, MOOSE-Chem, SciMON, IdeaSynth, and the critical
literature: Si et al.'s novelty-feasibility and ideation-execution-gap
studies, Wenger & Kenett on creative homogeneity).

## Memory: ledger, digest, brief, dossier — four tiers, one source

**Mechanism.** `ledger.jsonl` is an append-only event log (latest record per
id wins). Three rendered views at increasing depth for different consumers:
the **digest** (one line per entry + kill-code table + ranked backlog; every
non-blind prompt), the **portfolio brief** (full verdicts and unblock
conditions for actionable ideas; scouting prompts), and the **librarian
dossier** (everything, including cards, amendments, and the killed pile; the
librarian only).

**Why.** (1) Append-only because cycles run remotely and concurrently with
human edits; appends never merge-conflict and history is never rewritten.
(2) Tiering because full detail for the whole corpus in every prompt would
drown the signal and blow context; each stage gets the depth it can act on.
(3) The **kill-code taxonomy** turns the founding observation into permanent
infrastructure: the digest's kill-frequency table doubles as a generation-time
checklist, and every scout must state per candidate how its design escapes
each recorded pattern. This is sharper than the published analog (Co-
Scientist's meta-review accumulates critique themes as prose).
(4) **Scrutiny level** (SCOUTED < CRITIQUED < DEBATED < PROBED) is a first-
class field because cycle one showed undebated candidates presenting exactly
as polished as debated ones — scrutiny provenance prevents unvetted ideas
from masquerading as vetted.

## Tracks: baseline, wide, fiction — one floor, several ceilings

**Mechanism.** Three generation tracks feeding identical downstream filters.
Baseline scouts conservatively. Wide raises the hypothesis ceiling (multi-step
mechanisms, mandatory cross-field transplants) while keeping the evidence
floor. Fiction is a persona-separated pipeline: a **blind** writer (no
charter, no memory, only a seed card of two concepts + dataset + twist)
writes a story that must contain a verification scene; a mechanical extractor
strips the narrative; a refiner **from the other model family** formalizes
the pitch — with "no testable kernel exists" as a first-class, non-penalized
exit.

**Why.** Cycle one's ideas did not die for being boring — they died on
evidence defects — so the fix raises ambition in hypothesis space while
holding evidence standards fixed, never the reverse. Fiction-mode's design
choices each counter a documented failure: the writer is blind because prior
art functions as a plausibility filter and multi-agent information flow
homogenizes creativity (blind/NGT structures are the published mitigation);
seeds are structurally random because "be creative" prompts demonstrably
mode-collapse (Wenger & Kenett: LLM "wildness" is homogeneous across
families); the **verification scene** smuggles testability in through the
fiction's own logic instead of re-imposing the plausibility filter; the
cross-family handoff exists because a model may half-recognize its own
fictional register; the honorable exit + `kernel_provenance` counter the
refiner's characteristic failure (rationalizing an empty premise) and let
post-mortems distinguish "the fiction was empty" from "translation lost the
kernel". Seed provenance (`human|random`) is recorded so directed seeds
don't contaminate the planned fiction-vs-baseline head-to-head — human-picked
pairs are pre-selected for promise and would inflate survival stats.
The persona-separation itself is, per the survey, undocumented in the
literature; it is run as an experiment, not a certainty.

## Novelty: searched, cited, calibrated — never self-reported

**Mechanism.** A dedicated audit stage per cycle: three closest prior works
per candidate found by actual search with identifiers, a stated delta, a
forced why-not-done answer (NEW_CAPABILITY / BLIND_SPOT / TRIED_AND_FAILED),
and verdicts including `NOVEL_UNVERIFIED` and `NO_NEIGHBORS_FOUND` (a flag
for human check, never proof).

**Why.** LLM novelty self-assessment is documented as unreliable (Si et al.),
and retrieval-grounded checking is the validated pattern (SciMON, AI
Scientist's Semantic Scholar loop; Co-Scientist found search access for the
reviewing agent specifically suppressed implausible "novel" hypotheses). The
deliberately un-flattering verdict vocabulary exists because several
published systems score their own outputs and inflate.

## Backlog: cross-cycle, deterministically ranked

**Mechanism.** Every scouted candidate of every cycle enters a global queue;
rank is recomputed on demand from two stored fields (novelty verdict, then
mean rubric score). Promotion to an idea retires a candidate; the pipeline
finishes in-flight ideas before drawing new ones. The librarian may *change
the stored verdicts* (with citations); nothing hand-authors an ordering.

**Why.** Without it, each cycle's slate silently orphaned the previous
cycle's runners-up. The ranking is deterministic rather than agent-authored
because an agent-authored order is opaque, unstable across runs, and
unauditable; verdict-correction-with-citation keeps every reordering
explainable from inspectable fields. Elo/pairwise tournaments (the validated
method at scale) are deferred until the queue is large enough to need them.

## Debate: cross-model, bounded, machine-legible

**Mechanism.** Proposer and critic are different model families; roles swap
across cycles (`[rotation]`); termination requires both sides (a unilateral
CONVERGED never ends it, but a unilateral IRREDUCIBLE DISAGREEMENT does,
after the other side responds — requiring both to agree that they disagree
would manufacture a different false consensus). Summaries end in a fenced
JSON verdict block that the orchestrator parses into the ledger
(PAUSE/REVISE/KILL+validated code/PROCEED), so debate outcomes self-record.

**Why.** Debate-style ranking is ablation-validated (Co-Scientist). Rotation
is the cheap alternative to doubling the agent count: cycle-one evidence
showed the critique gap was *data contact*, not viewpoint count, so role
diversity is bought with configuration, not tokens. The two-model mix is
known to be weaker protection than it feels (correlated-errors literature:
Claude and GPT share failure modes), which is why the structural mechanisms
(blindness, rotation, filters) carry the diversity burden. Verdict
automation exists because verdicts previously lived only in prose and ledger
status drifted from reality within one week of operation (idea 010 was
REJECT in its consensus and ACTIVE in the ledger).

## Operational honesty: contracts, scope, evidence, logs

Each of these was added after the system's own behavior demonstrated the gap:

- **Artifact contracts** (a stage that writes nothing is a failed stage):
  cycle 005's scout ran 20 minutes, exited 0, wrote nothing (its sandbox
  could not write), and an empty pool sailed through merge and audit.
- **Per-stage agent logs committed with checkpoints**: the same incident was
  initially undiagnosable because the agent's output lived only in a
  scrolled-away CI console.
- **Keystone evidence rule** (`INSPECTED_TRUE` without a quoted artifact is
  demoted at merge): idea 013's card claimed an inspected keystone that
  debate found unsupported.
- **Scope guard** (git-enforced per-stage path allowlists): models are asked
  nicely *and* checked; the guard has caught the system's own test code.
- **Checkpoint = commit**: runners are ephemeral and jobs are killable at
  6 h; committing each stage makes any failure cost one stage and makes the
  same button a resume. Clean-tree enforcement between stages preserves
  attribution of every change to the stage that made it.
- **CI sandbox variant** (`SCOUT_CI` selects a bypassed Codex sandbox on
  runners only): Codex's bubblewrap sandbox cannot initialize on GitHub
  runners (userns restrictions); the ephemeral runner VM is itself the
  sandbox, which is the flag's documented use case. Local runs keep the full
  sandbox — the variant cannot activate off-CI.

## Human gates and the execution boundary

The pipeline never runs expensive compute uninvited: probes require an
explicit human approval marker, probe code is generated only after it, and
results are recorded back by hand. This is the current system's honest
limitation as well as its safety property: per the ideation-execution-gap
literature, idea rankings not anchored to executed feasibility systematically
overrate fragile ideas — which is why **executable Stage 0 gating** is the
top pending item in `REVAMP.md`, not an afterthought.

## The librarian: the only whole-corpus reader

**Mechanism.** On-demand pass with a full-detail dossier: connection map,
stale-verdict re-audit (applied to the ledger with refreshed audit dates),
and a revival scan over killed/paused entries, emitting proposals future
scouts may adopt (adoption counts against the scout's bounded revival quota
and receives full filtering).

**Why.** Every other stage sees either one idea in depth or the whole corpus
at one line each; nobody read *across*. Its duties are manual-only because
they cost tokens per corpus entry — and its outputs are proposals rather
than candidates so that everything still enters through one filtered gate.
The revival scan exists because kill codes like DATA_ACCESS and
COMPUTE_INFEASIBLE describe conditions the world can change, and nothing
else ever revisits the killed pile.

## Testing philosophy

32 deterministic tests run before every remote stage spends a token. Agents
are faked; orchestration, contracts, blindness, rotation, resume, ranking,
and verdict automation are real. Two production incidents were tests
inheriting the live repo's accumulating state (real cycles and ideas leaking
into the harness world), so pipeline tests now construct a hermetic world —
the standing rule: **tests may not depend on what the repository has lived
through.**
