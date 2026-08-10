# Revamp punch-list

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
- [ ] **Librarian stage.** Periodic agent pass over the full ledger proposing
  cross-idea connections; candidates it proposes enter as a normal track.
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
