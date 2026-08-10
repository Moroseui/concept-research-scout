# Revamp punch-list

> Orientation for newcomers: README.md is the front door (what + how to
> operate); docs/ARCHITECTURE.md is the rationale (why each mechanism
> exists, with the failure or finding that motivated it); this file is the
> status ledger (done vs pending, with designs for pending work).

Living checklist for the post-cycle-one revamp. Future agent cycles: read this
to know what is done versus pending; check items off in the same commit that
completes them.

## Done in this pass

- [x] **Idea ledger** (`ledger.jsonl`, `orchestrator/ledger.py`). Append-only,
  latest-record-wins, git-merge-friendly. Fields include `scrutiny`
  (SCOUTED < CRITIQUED < DEBATED < PROBED) so undebated candidates can never
  masquerade as clean, and `kill_code` from a controlled taxonomy.
  Migration backfills from `ideas/NNN` + `portfolio/ideas.csv` +
  `evidence/decisions.md`; runs automatically on first `cycle` if the ledger
  is absent. `python scout.py ledger {migrate,list,show,search,kill,digest,taxonomy}`.
- [x] **Ledger digest as institutional memory.** `evidence/ledger_digest.md`
  is regenerated each cycle and injected into every non-blind prompt; its
  kill-code frequency table is the generation-time checklist (cycle one:
  USE_VS_ASSOCIATION killed 9/11).
- [x] **Generation-time use-vs-association filter** in `scout.md` (Step 0) and
  `wide_scout.md`; refiner enforces it for fiction candidates.
- [x] **Novelty operationalized** (`novelty_audit.md` stage + wide-scout
  triplet): named closest priors found by search, precise delta, and a
  why-not-done answer in {NEW_CAPABILITY, BLIND_SPOT, TRIED_AND_FAILED}.
  NO_NEIGHBORS_FOUND flags for human check, never counts as proof.
- [x] **Checkpoint/resume** (`cycle`, `resume`, `--resume-or-new`). Every
  stage's completion is a git commit; failed stages commit partial output and
  mark state, so a rate limit / timeout / Actions kill costs one stage.
  `[limits] stage_timeout` in AGENTS.toml.
- [x] **Role rotation** (`[rotation]` in AGENTS.toml): pair swaps on odd
  cycles across all roles including debate sides. Two-cycle A/B before any
  decision about concurrent dual scouts.
- [x] **Wide-mode track** (`wide_scout.md`): raised hypothesis ceiling
  (multi-step mechanisms, mandatory cross-field transplant), unchanged
  evidence floor (charter hard constraint, one-Colab-session envelope).
- [x] **Fiction-mode track** (persona-separated, an experiment — see head-to-
  head below): blind constraint-seeded writer (`fiction_scout.md` +
  `orchestrator/seeds.json` twist deck) -> mechanical extractor
  (`fiction_extract.md`) -> cross-family refiner (`fiction_refine.md`) with a
  first-class NO_TESTABLE_KERNEL exit and `kernel_provenance` for
  post-mortems. Writer never sees charter/rules/ledger; refiner never sees
  story or seed card (enforced by tests).
- [x] **GitHub Actions remote operation** (`.github/workflows/scout-cycle.yml`):
  mobile Run-workflow button (tracks + dry_run inputs), nightly cron,
  subscription auth via `CLAUDE_CODE_OAUTH_TOKEN` and `CODEX_AUTH_JSON`
  secrets, tests-before-cycle, per-stage checkpoint push, resume-or-new.
- [x] Tests extended to 15 (ledger migrate/kill, rotation parity, full fiction
  cycle with blindness assertions, fail-then-resume, dry-run spends nothing).

- [x] **Mobile post-scout pipeline** (`idea-pipeline` workflow +
  `scout.py pipeline`): shortlist the top-N candidates of the latest cycle
  (ranked by audit verdict, then mean rubric score; DUPLICATE_PRIOR excluded)
  and run critique/debate per idea, or target `--candidate` / `--idea`.
  Idempotent: re-running skips shortlisted candidates and stages whose
  artifacts exist, so the same button is also resume.

- [x] **Cross-cycle candidate backlog.** Every scouted candidate of every
  cycle lives in a global ranked queue (verdict, then rubric score; verdicts +
  audit dates backfilled/synced from novelty_audit.md automatically). The
  pipeline's `--top N` draws the next N from this queue, finishing in-flight
  shortlisted ideas first; promoted candidates retire from the queue. The
  digest shows the top of the queue; `python scout.py backlog` lists it all.
  Re-auditing stale verdicts against new literature is deliberately NOT
  automatic (token cost) -- future librarian duty; audit dates make staleness
  visible.

- [x] **Portfolio-aware scouting (revival quota).** `evidence/portfolio_brief.md`
  (auto-generated each cycle; `python scout.py brief`) gives scouts the full
  verdicts, unblock conditions, and unresolved questions of actionable ideas
  (PAUSED/REVISE/DEBATED with consensus; killed ideas excluded -- they stay in
  the kill table). Scout prompt allows at most 2 of 5 candidates as revivals/
  recombinations, each requiring `parent_ids` + a `revival_basis` citing the
  specific changed condition with a source; zero revivals is the mandated
  default when nothing changed. Lineage flows to ledger rows. Blind fiction
  writer still sees none of it. `ledger set-status` added (e.g. PAUSED for
  idea 012). This is the scout-level half of the evolution track; the full
  breeding operators remain pending below.

- [x] **Librarian pipeline** (`librarian` workflow + `scout.py librarian`,
  manual-only by design -- token cost). Whole-corpus pass with a full-detail
  dossier (cards + verdicts + unresolved + kill reasons + backlog with audit
  dates) that no other stage gets. Three duties: connection map
  (librarian_report.md), stale-verdict re-audit (verdict_updates.json applied
  to the ledger with refreshed audited_at), and revival scan producing
  proposals (evidence/librarian_proposals.md, injected into scout prompts;
  adoption counts against the scout revival quota and gets full filtering).
- [x] **Structured debate verdict -> ledger.** debate_summary emits a fenced
  json verdict block; `_close_debate` parses it and sets PAUSED / REJECTED
  (+validated kill code, UNCLASSIFIED fallback) / SHORTLISTED / ACTIVE
  automatically. Manual set-status/kill remain for human overrides.
- [x] **Keystone evidence rule.** INSPECTED_TRUE requires `keystone_evidence`
  (quoted artifact) in scout/wide/fiction-refine prompts; merge mechanically
  demotes unevidenced claims to NOT_INSPECTED (noted in candidates_all
  notes). Response to idea 013's overclaim.
- [x] **Directed fiction seeds.** `cycle --seed-concepts "a,b"` overrides the
  draw; `source: human|random` recorded in fiction_seed.json and stamped as
  `seed_source` on fiction candidates' ledger rows for clean head-to-head
  stats.

- [x] **Fiction v2** (post-run-1): curated seed datasets with scale/access
  annotations; named public model as a third seed prop (discovery must be
  about the model); `adjacent_question` near-miss banking on the honorable
  exit (ledger rows outside the backlog); `fiction_version` stamped through
  seed and ledger for stratified head-to-head stats. Creative core
  (blindness, twist deck, verification scene, cross-family refine) frozen.
- [x] **Taxonomy: IDENTIFIABILITY_FAILURE** added after two occurrences
  (013 localisation, 016 injector confound); debate-summary prompts now
  carry the live taxonomy so verdict blocks pick from the menu.

## Pending (dependency order)

- [ ] **Executable Stage 0 gating.** Probe machinery exists
  (approve/verify/package-colab); pending: feasibility scores capped until a
  probe result is recorded, and `interpret` reads probe results explicitly.
- [ ] **Probe queue for GPU work.** Actions runners are CPU-only: workflow
  writes `probe_queue/` entries for GPU probes; execute in Colab, commit
  results back via `record-result`. Later option: Modal or similar for
  headless GPU execution.
- [ ] **Fiction-mode head-to-head (the demo).** One cycle with matched
  fiction and baseline candidate counts, downstream stages blind to track
  (strip `track` before critique); compare filter survival, novelty-audit
  distance, kill-code distribution, within-track pairwise diversity, blinded
  human surprise rating. Expect a low fiction hit rate (ideation-execution
  gap); win condition is 1-2 survivors per cycle. Null result still
  publishable-adjacent.
- [ ] **Homogenization monitoring.** Track pairwise semantic similarity of
  surviving candidates across cycles; if it rises, weaken agent-to-agent
  information flow (blind-writing before debate).
- [ ] **True intra-stage batching** for the scout stage (generate candidates
  in batches of 3-4 with per-batch checkpoints). Current granularity is
  per-stage, which is acceptable but coarser.
- [ ] **Evolution track.** A fourth scout track ("evolve") that breeds the
  existing corpus instead of generating fresh: draw 2 parent ideas from the
  ledger (weighted by verdict/scrutiny; killed ideas are eligible as gene
  donors -- the kill code says which part died, so the surviving part can be
  recombined), then apply an operator: recombine (cross one idea's mechanism
  with another's dataset/measurement), mutate (vary a single facet: endpoint,
  dataset, measurement, population), or rescue (dead idea's question x live
  idea's viable design). Literature basis: MOOSE-Chem's evolutionary
  population, IdeaSynth's facet recombination, Co-Scientist's evolution
  agent. Record `parent_ids` on every evolved candidate's ledger row so
  lineage is traceable and evolved-vs-fresh survival rates are measurable
  (same built-in experiment structure as fiction-mode's head-to-head).
  Same filters apply downstream -- recombination is exactly where
  use-vs-association slop re-enters. Relationship to the librarian: the
  librarian *proposes* cross-idea connections during its ledger pass; the
  evolve track *operationalizes* them into candidates -- librarian output is
  a natural seed source alongside random parent draws.
- [ ] **VPS self-hosted runner** — only if cycles routinely exceed the 6-hour
  Actions cap or Codex token refresh becomes annoying. Same mobile UX.

## First-run checklist (operator)

1. Push this pass; confirm the `checks` workflow is green.
2. Repo secrets: `CLAUDE_CODE_OAUTH_TOKEN` (`claude setup-token`),
   `CODEX_AUTH_JSON` (`base64 -w0 ~/.codex/auth.json` after
   `codex login --device-auth`; enable device-code login in ChatGPT security
   settings first).
3. Account billing: payment method + Actions spending limit (~$25 tripwire).
4. Mobile app: Actions notifications on.
5. `scout-cycle` with `dry_run=true` — verify both CLIs authenticate and the
   printed plan is sane.
6. First real cycle: **verify zero API spend** on both provider consoles while
   it runs (subscription-vs-API billing footgun). Do not skip.
