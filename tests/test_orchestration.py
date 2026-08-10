#!/usr/bin/env python3
"""Deterministic tests for the orchestration mechanics.

No network, no real agent. A fake agent script stands in for claude/codex:
it reads the prompt on stdin and writes files dictated by FAKE_AGENT_ACTION.

Run:  python3 tests/test_orchestration.py
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

FAKE_AGENT = r"""#!/usr/bin/env python3
import os, sys, pathlib
prompt = sys.stdin.read()
root = pathlib.Path(os.environ["FAKE_REPO"])
pathlib.Path(os.environ["FAKE_RECEIPT"]).write_text(prompt)
action = os.environ.get("FAKE_AGENT_ACTION", "noop")
target = os.environ.get("FAKE_TARGET", "ideas/001")
NL = chr(10)

def sneak():
    (root / "probes").mkdir(exist_ok=True)
    (root / "probes" / "sneaky.py").write_text("# out of lane" + NL)

def add_round(side, status):
    t = root / target / "debate.md"
    t.parent.mkdir(parents=True, exist_ok=True)
    prev = t.read_text() if t.exists() else "# Debate transcript" + NL + NL
    n = prev.count("## Round ") + 1
    t.write_text(prev + "## Round " + str(n) + " - " + side.upper() + NL + NL
                 + "**Status:** " + status + NL + NL)

if action == "out_of_scope":
    sneak()
elif action == "clean_debate_then_sneak_on_summary":
    # The summary prompt is the only one that mentions consensus.md.
    if "consensus.md" in prompt:
        sneak()
    else:
        t = root / target / "debate.md"
        prev = t.read_text() if t.exists() else ""
        side = "PROPOSER" if prev.count("CRITIC") > prev.count("PROPOSER") else "CRITIC"
        add_round(side, "CONVERGED")
elif action.startswith("debate:"):
    _, side, status = action.split(":", 2)
    add_round(side, status)
elif action == "cycle_auto":
    import re
    m = re.search("<!-- stage: ([a-z_]+) -->", prompt)
    stage = m.group(1) if m else ""
    if stage and stage == os.environ.get("FAKE_FAIL_STAGE", ""):
        sys.exit(1)
    if stage and stage == os.environ.get("FAKE_SKIP_WRITE_STAGE", ""):
        sys.exit(0)  # exit clean but write nothing
    m2 = re.search("Assigned output directory: (\\S+)", prompt)
    outdir = root / (m2.group(1) if m2 else target)
    outdir.mkdir(parents=True, exist_ok=True)
    cand = '{"candidates": [{"title": "Fake STAGE", "question": "q?", "dataset": "D"}]}'
    if stage == "scout":
        (outdir / "scout_candidates.json").write_text(cand.replace("STAGE", "baseline") + NL)
    elif stage == "wide_scout":
        (outdir / "wide_candidates.json").write_text(cand.replace("STAGE", "wide") + NL)
    elif stage == "fiction_scout":
        (outdir / "fiction_story.md").write_text("A story. ZZSTORYMARKERZZ. The check held." + NL)
    elif stage == "fiction_extract":
        (outdir / "fiction_pitch.md").write_text("## Claimed finding" + NL + "Pitch body." + NL)
    elif stage == "fiction_refine":
        (outdir / "fiction_candidates.json").write_text(cand.replace("STAGE", "fiction") + NL)
    elif stage == "novelty_audit":
        (outdir / "novelty_audit.md").write_text("audit" + NL)
    elif stage == "librarian":
        (outdir / "librarian_report.md").write_text("report" + NL)
        (outdir / "verdict_updates.json").write_text(
            '{"updates": [{"ledger_id": "scout-050-c01", "novelty_verdict": "NOVEL_VERIFIED", "reason": "test"}]}' + NL)
        (outdir / "librarian_proposals.json").write_text(
            '{"proposals": [{"title": "revived idea", "question": "q?", "parent_ids": ["idea-011"], "revival_basis": "b", "sketch": "s"}]}' + NL)
    elif "TRANSCRIPT SO FAR" in prompt:
        t = outdir / "debate.md"
        prev = t.read_text() if t.exists() else "# Debate transcript" + NL + NL
        side = "PROPOSER" if prev.count("CRITIC") > prev.count("PROPOSER") else "CRITIC"
        n = prev.count("## Round ") + 1
        t.write_text(prev + "## Round " + str(n) + " - " + side + NL + NL
                     + "**Status:** CONVERGED" + NL + NL)
    elif "consensus.md" in prompt:
        (outdir / "consensus.md").write_text("fake consensus" + NL)
    elif "Adversarially review" in prompt:
        (outdir / "critique.md").write_text("fake critique" + NL)
else:
    (root / target).mkdir(parents=True, exist_ok=True)
    (root / target / "critique.md").write_text("fake critique" + NL)

# Per-stage receipt copy so tests can inspect individual prompts of a cycle.
import re as _re
_m = _re.search("<!-- stage: ([a-z_]+) -->", prompt)
if _m:
    pathlib.Path(os.environ["FAKE_RECEIPT"] + "." + _m.group(1)).write_text(prompt)
"""


class Harness(unittest.TestCase):
    def setUp(self):
        self.dir = Path(tempfile.mkdtemp())
        self.repo = self.dir / "repo"
        self.receipt = self.dir / "receipt.txt"
        shutil.copytree(REPO, self.repo, ignore=shutil.ignore_patterns(
            "__pycache__", "*.pyc", ".git"))

        self.fake = self.dir / "fake_agent.py"
        self.fake.write_text(FAKE_AGENT)
        self.fake.chmod(0o755)

        # Point both agents at the fake, both piping stdin.
        (self.repo / "AGENTS.toml").write_text(f'''
[default]
agent = "claude"
[roles]
critique = "codex"
debate = "alternating"
[debate]
proposer = "claude"
critic = "codex"
max_rounds = 3
[claude]
enabled = true
stdin = true
command = ["{sys.executable}", "{self.fake}"]
[codex]
enabled = true
stdin = true
command = ["{sys.executable}", "{self.fake}"]
''')
        # A shortlisted idea to operate on.
        d = self.repo / "ideas" / "001"
        d.mkdir(parents=True, exist_ok=True)
        (d / "idea_card.json").write_text(json.dumps({"title": "Test idea"}) + "\n")
        (self.repo / "orchestrator" / "state.json").write_text(
            json.dumps({"next_scout": 2, "selected_idea": 1}) + "\n")

        subprocess.run(["git", "init", "-q"], cwd=self.repo, check=True)
        subprocess.run(["git", "config", "user.email", "t@t.t"], cwd=self.repo, check=True)
        subprocess.run(["git", "config", "user.name", "t"], cwd=self.repo, check=True)
        self.commit()

    def tearDown(self):
        shutil.rmtree(self.dir, ignore_errors=True)

    def commit(self):
        subprocess.run(["git", "add", "-A"], cwd=self.repo, check=True)
        subprocess.run(["git", "commit", "-qm", "wip", "--allow-empty"],
                       cwd=self.repo, check=True)

    def scout(self, *args, action="noop", **env):
        e = dict(os.environ, FAKE_REPO=str(self.repo), FAKE_RECEIPT=str(self.receipt),
                 FAKE_AGENT_ACTION=action, **env)
        return subprocess.run(
            [sys.executable, str(self.repo / "scout.py"), *args],
            cwd=self.repo, capture_output=True, text=True, env=e, timeout=120)


class TestStdin(Harness):
    def test_prompt_reaches_agent_via_stdin(self):
        r = self.scout("run", "critique", "--idea", "1")
        self.assertEqual(r.returncode, 0, r.stderr)
        seen = self.receipt.read_text()
        self.assertIn("STAGE TASK", seen)
        self.assertIn("Adversarially review", seen)
        self.assertNotEqual(seen.strip().count("\n"), 0,
                            "agent received a path, not prompt text")


class TestScope(Harness):
    def test_out_of_scope_write_fails_the_stage(self):
        r = self.scout("run", "critique", "--idea", "1", action="out_of_scope")
        self.assertNotEqual(r.returncode, 0, "scope violation did not fail the stage")
        self.assertIn("SCOPE VIOLATION", r.stdout + r.stderr)

    def test_dirty_tree_blocks_a_stage(self):
        (self.repo / "README.md").write_text("edited by the human\n")
        r = self.scout("run", "critique", "--idea", "1")
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("not clean", r.stdout + r.stderr)

    def test_preexisting_edit_is_not_blamed_on_the_stage(self):
        (self.repo / "README.md").write_text("edited by the human\n")
        r = self.scout("run", "critique", "--idea", "1")
        self.assertNotIn("SCOPE VIOLATION", r.stdout + r.stderr,
                         "pre-existing edit was misattributed to the stage")


class TestDebate(Harness):
    def _run_debate(self, action, rounds=3):
        return self.scout("debate", "--idea", "1", "--rounds", str(rounds),
                          action=action, FAKE_TARGET="ideas/001")

    def test_unilateral_convergence_does_not_end_debate(self):
        # Critic converges every turn; proposer stays OPEN. Must not stop.
        e = dict(os.environ, FAKE_REPO=str(self.repo), FAKE_RECEIPT=str(self.receipt),
                 FAKE_TARGET="ideas/001",
                 FAKE_AGENT_ACTION="debate:critic:CONVERGED")
        subprocess.run([sys.executable, str(self.repo / "scout.py"),
                        "debate", "--idea", "1", "--rounds", "1"],
                       cwd=self.repo, capture_output=True, text=True, env=e)
        # Simulate: critic CONVERGED, proposer OPEN -> should_stop is None
        sys.path.insert(0, str(self.repo))
        import importlib, scout as sc
        importlib.reload(sc)
        t = self.repo / "ideas" / "001"
        (t / "debate.md").write_text(
            "# Debate\n\n## Round 1 - CRITIC\n\n**Status:** CONVERGED\n\n"
            "## Round 1 - PROPOSER\n\n**Status:** OPEN\n\n")
        sc.ROOT = self.repo
        self.assertIsNone(sc._debate_should_stop(t),
                          "one-sided CONVERGED wrongly ended the debate")

    def test_bilateral_convergence_ends_debate(self):
        sys.path.insert(0, str(self.repo))
        import importlib, scout as sc
        importlib.reload(sc)
        sc.ROOT = self.repo
        t = self.repo / "ideas" / "001"
        t.mkdir(parents=True, exist_ok=True)
        (t / "debate.md").write_text(
            "# Debate\n\n## Round 1 - CRITIC\n\n**Status:** OPEN\n\n"
            "## Round 1 - PROPOSER\n\n**Status:** OPEN\n\n"
            "## Round 2 - CRITIC\n\n**Status:** CONVERGED\n\n"
            "## Round 2 - PROPOSER\n\n**Status:** CONVERGED\n\n")
        self.assertIsNotNone(sc._debate_should_stop(t),
                             "bilateral CONVERGED failed to end the debate")

    def test_debate_summary_out_of_scope_write_fails(self):
        # Drive both sides to CONVERGED so the debate terminates and
        # _close_debate runs the summary turn, which must also be scoped.
        r = self._run_debate("clean_debate_then_sneak_on_summary", rounds=1)
        self.assertNotEqual(r.returncode, 0,
                            "debate-summary wrote outside scope without failing")
        self.assertIn("SCOPE VIOLATION", r.stdout + r.stderr)

    def test_debate_out_of_scope_write_fails(self):
        r = self._run_debate("out_of_scope", rounds=1)
        self.assertNotEqual(r.returncode, 0,
                            "debate turn wrote outside scope without failing")
        self.assertIn("SCOPE VIOLATION", r.stdout + r.stderr)




class TestLedger(Harness):
    def test_migrate_backfills_from_ideas_and_decisions(self):
        r = self.scout("ledger", "migrate")
        self.assertEqual(r.returncode, 0, r.stderr)
        lj = self.repo / "ledger.jsonl"
        self.assertTrue(lj.exists(), "ledger.jsonl not created")
        recs = [json.loads(x) for x in lj.read_text().splitlines() if x.strip()]
        ids = {x.get("ledger_id") for x in recs}
        self.assertGreaterEqual(len(ids), 11, f"expected >=11 migrated ideas, got {sorted(ids)}")
        by_id = {}
        for rec in recs:
            by_id.setdefault(rec["ledger_id"], {}).update({k: v for k, v in rec.items() if v})
        self.assertEqual(by_id.get("idea-001", {}).get("status"), "REJECTED",
                         "decisions.md REJECTED verdict not picked up for idea 001")
        self.assertTrue((self.repo / "evidence" / "ledger_digest.md").exists())

    def test_kill_records_taxonomy_code_and_refreshes_digest(self):
        self.scout("ledger", "migrate")
        self.commit()
        r = self.scout("ledger", "kill", "idea-003", "USE_VS_ASSOCIATION", "test reason")
        self.assertEqual(r.returncode, 0, r.stderr)
        digest = (self.repo / "evidence" / "ledger_digest.md").read_text()
        self.assertIn("USE_VS_ASSOCIATION", digest)

    def test_unknown_kill_code_is_rejected(self):
        self.scout("ledger", "migrate")
        r = self.scout("ledger", "kill", "idea-003", "NOT_A_CODE", "reason")
        self.assertNotEqual(r.returncode, 0)


class TestPipeline(Harness):
    def setUp(self):
        # Hermetic: the harness copies the real repo, which accumulates real
        # scouting cycles and ledger rows over time. The backlog is global by
        # design, so pipeline tests must start from an empty world or every
        # new real cycle would change their results.
        super().setUp()
        import shutil as _sh
        for d in (self.repo / "ideas").glob("scout-*"):
            _sh.rmtree(d)
        # Also wipe accumulated real ideas (keep 001 for --idea tests): the
        # repo gains numeric idea dirs over time and shortlist numbering,
        # backlog contents, and in-flight detection must not depend on them.
        for d in (self.repo / "ideas").glob("[0-9][0-9][0-9]"):
            if d.name != "001":
                _sh.rmtree(d)
        for f in ("ledger.jsonl", "evidence/ledger_digest.md",
                  "evidence/portfolio_brief.md", "evidence/librarian_proposals.md"):
            (self.repo / f).unlink(missing_ok=True)
        self.commit()

    def make_cycle_outputs(self, scoutdir, verdicts):
        d = self.repo / "ideas" / scoutdir
        d.mkdir(parents=True, exist_ok=True)
        cands = [{"title": f"cand {i}", "question": "q?",
                  "scores": {"interest": 5 - i}} for i in range(1, len(verdicts) + 1)]
        (d / "candidates_all.json").write_text(json.dumps(
            {"cycle": 9, "tracks": ["baseline"], "notes": {}, "candidates": cands}) + "\n")
        rows = "".join(f"| C{i} | `{v}` | `NEW_CAPABILITY` |\n"
                       for i, v in enumerate(verdicts, 1))
        (d / "novelty_audit.md").write_text("# audit\n\n| Candidate | Verdict | code |\n|---|---|---|\n" + rows)

    def test_ranking_prefers_verdict_then_score_and_drops_duplicates(self):
        self.make_cycle_outputs("scout-009",
            ["INCREMENTAL", "NOVEL_UNVERIFIED", "NOVEL_VERIFIED", "DUPLICATE_PRIOR"])
        sys.path.insert(0, str(self.repo))
        import importlib, scout as sc
        importlib.reload(sc)
        sc.ROOT = self.repo
        sc.ledger_mod.ROOT = self.repo
        sc.ledger_mod.LEDGER = self.repo / "ledger.jsonl"
        sc.ledger_mod.DIGEST = self.repo / "evidence" / "ledger_digest.md"
        self.assertEqual(sc._rank_candidates(9), [3, 2, 1])

    def test_top_n_pipeline_shortlists_runs_and_is_idempotent(self):
        self.make_cycle_outputs("scout-009", ["NOVEL_UNVERIFIED", "NOVEL_VERIFIED"])
        (self.repo / "orchestrator" / "state.json").write_text(
            json.dumps({"next_scout": 10, "selected_idea": 1}) + "\n")
        self.commit()
        r = self.scout("pipeline", "--top", "1", action="cycle_auto")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        # C2 (NOVEL_VERIFIED) should have been picked -> new idea 012
        d = self.repo / "ideas" / "002"
        self.assertTrue((d / "idea_card.json").exists(), "first shortlist should create idea 002")
        self.assertIn("cand 2", (d / "idea_card.json").read_text())
        self.assertTrue((d / "critique.md").exists())
        self.assertTrue((d / "consensus.md").exists())
        recs = (self.repo / "ledger.jsonl").read_text()
        self.assertIn('"DEBATED"', recs)
        # Re-run advances the queue: C2 is done, so C1 is drawn next.
        r2 = self.scout("pipeline", "--top", "1", action="cycle_auto")
        self.assertEqual(r2.returncode, 0, r2.stdout + r2.stderr)
        d3 = self.repo / "ideas" / "003"
        self.assertTrue((d3 / "idea_card.json").exists(), "queue did not advance")
        self.assertIn("cand 1", (d3 / "idea_card.json").read_text())
        # Third press: backlog empty, nothing in flight -> clean no-op.
        r3 = self.scout("pipeline", "--top", "1", action="cycle_auto")
        self.assertEqual(r3.returncode, 0, r3.stdout + r3.stderr)
        self.assertIn("Nothing to do", r3.stdout)
        self.assertFalse((self.repo / "ideas" / "004").exists())

    def test_inflight_idea_is_finished_before_new_candidates(self):
        self.make_cycle_outputs("scout-009", ["NOVEL_UNVERIFIED", "NOVEL_VERIFIED"])
        (self.repo / "orchestrator" / "state.json").write_text(
            json.dumps({"next_scout": 10, "selected_idea": 1}) + "\n")
        self.commit()
        # First run dies at debate for idea 012 (C2).
        r = self.scout("pipeline", "--top", "1", action="cycle_auto",
                       FAKE_FAIL_STAGE="")  # critique fine
        # simulate failure: remove consensus to mark debate incomplete
        (self.repo / "ideas" / "002" / "consensus.md").unlink()
        (self.repo / "ideas" / "002" / "debate.md").unlink()
        self.commit()
        r2 = self.scout("pipeline", "--top", "1", action="cycle_auto")
        self.assertEqual(r2.returncode, 0, r2.stdout + r2.stderr)
        self.assertIn("Finishing in-flight", r2.stdout)
        self.assertTrue((self.repo / "ideas" / "002" / "consensus.md").exists())
        self.assertFalse((self.repo / "ideas" / "003").exists(),
                         "drew a new candidate while one was in flight")

    def test_sync_backfills_verdicts_for_old_cycles(self):
        self.make_cycle_outputs("scout-008", ["INCREMENTAL", "NOVEL_VERIFIED"])
        self.commit()
        sys.path.insert(0, str(self.repo))
        import importlib, scout as sc
        importlib.reload(sc)
        sc.ROOT = self.repo
        sc.ledger_mod.ROOT = self.repo
        sc.ledger_mod.LEDGER = self.repo / "ledger.jsonl"
        sc.ledger_mod.DIGEST = self.repo / "evidence" / "ledger_digest.md"
        rows = sc._ranked_backlog()
        pair = [(s, c) for s, c, _ in rows if s == 8]
        self.assertEqual(pair[0], (8, 2), "NOVEL_VERIFIED not ranked first after backfill")
        digest = (self.repo / "evidence" / "ledger_digest.md").read_text()
        self.assertIn("Candidate backlog", digest)
        self.assertIn("scout-008-c02", digest)

    def test_pipeline_specific_idea_runs_stages_only(self):
        self.commit()
        r = self.scout("pipeline", "--idea", "1", "--stages", "critique",
                       action="cycle_auto")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertTrue((self.repo / "ideas" / "001" / "critique.md").exists())


class TestPortfolioBrief(Harness):
    def _sc(self):
        sys.path.insert(0, str(self.repo))
        import importlib, scout as sc
        importlib.reload(sc)
        sc.ROOT = self.repo
        sc.BRIEF = self.repo / "evidence" / "portfolio_brief.md"
        sc.ledger_mod.ROOT = self.repo
        sc.ledger_mod.LEDGER = self.repo / "ledger.jsonl"
        sc.ledger_mod.DIGEST = self.repo / "evidence" / "ledger_digest.md"
        return sc

    def test_brief_extracts_verdicts_and_skips_killed(self):
        d = self.repo / "ideas" / "030"
        d.mkdir(parents=True)
        (d / "idea_card.json").write_text('{"title": "Paused idea"}\n')
        (d / "consensus.md").write_text(
            "# s\n\n## Agreed\n\n- x\n\n## Unresolved\n\n### Open q one\n\nbody\n\n"
            "## Recommendation\n\n**PAUSE.** Await the membership release.\n")
        k = self.repo / "ideas" / "031"
        k.mkdir()
        (k / "idea_card.json").write_text('{"title": "Killed idea"}\n')
        (k / "consensus.md").write_text("# s\n\n## Recommendation\n\n**KILL.**\n")
        sc = self._sc()
        sc.ledger_mod.append({"ledger_id": "idea-030", "status": "PAUSED"})
        sc.ledger_mod.append({"ledger_id": "idea-031", "status": "REJECTED"})
        out = sc.write_portfolio_brief().read_text()
        self.assertIn("idea-030", out)
        self.assertIn("Await the membership release", out)
        self.assertIn("Open q one", out)
        self.assertNotIn("idea-031", out, "killed idea leaked into the brief")

    def test_ledger_set_status(self):
        self.scout("ledger", "migrate")
        self.commit()
        r = self.scout("ledger", "set-status", "idea-002", "PAUSED", "--note", "test")
        self.assertEqual(r.returncode, 0, r.stderr)
        r = self.scout("ledger", "set-status", "idea-002", "NOT_A_STATUS")
        self.assertNotEqual(r.returncode, 0)

    def test_merge_carries_parent_ids_to_ledger(self):
        sc = self._sc()
        d = self.repo / "ideas" / "scout-042"
        d.mkdir(parents=True)
        (d / "scout_candidates.json").write_text(json.dumps({"candidates": [
            {"title": "revival", "question": "q?", "parent_ids": ["idea-012"]}]}))
        (self.repo / "orchestrator" / "state.json").write_text(json.dumps(
            {"next_scout": 43, "selected_idea": 1,
             "cycle": {"scout": 42, "tracks": ["baseline"], "stages": {}}}) + "\n")
        import importlib, scout as sc2
        sc2 = self._sc()
        sc2._merge_candidates(d, ["baseline"], 42)
        e = sc2.ledger_mod.load()["scout-042-c01"]
        self.assertEqual(e.get("parent_ids"), ["idea-012"])


class TestLibrarian(Harness):
    def test_librarian_pass_applies_verdicts_and_publishes_proposals(self):
        (self.repo / "ledger.jsonl").unlink(missing_ok=True)
        with (self.repo / "ledger.jsonl").open("w") as f:
            f.write(json.dumps({"ledger_id": "scout-050-c01", "status": "SCOUT_ONLY",
                                "scrutiny": "SCOUTED", "title": "old cand",
                                "recorded_at": "2026-01-01T00:00:00+00:00"}) + "\n")
        self.commit()
        r = self.scout("librarian", action="cycle_auto")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        d = self.repo / "ideas" / "librarian-001"
        self.assertTrue((d / "dossier.md").exists())
        self.assertTrue((d / "librarian_report.md").exists())
        recs = (self.repo / "ledger.jsonl").read_text()
        self.assertIn("NOVEL_VERIFIED", recs, "verdict update not applied")
        props = (self.repo / "evidence" / "librarian_proposals.md").read_text()
        self.assertIn("revived idea", props)
        self.assertIn("idea-011", props)
        # dossier carries consensus detail for debated ideas (repo has idea 001+)
        self.assertIn("idea-001", (d / "dossier.md").read_text())

    def test_dossier_includes_card_and_backlog_detail(self):
        sys.path.insert(0, str(self.repo))
        import importlib, scout as sc
        importlib.reload(sc)
        sc.ROOT = self.repo
        sc.BRIEF = self.repo / "evidence" / "portfolio_brief.md"
        sc.ledger_mod.ROOT = self.repo
        sc.ledger_mod.LEDGER = self.repo / "ledger.jsonl"
        sc.ledger_mod.DIGEST = self.repo / "evidence" / "ledger_digest.md"
        d = self.repo / "ideas" / "lib-test"; d.mkdir()
        out = sc.write_librarian_dossier(d).read_text()
        self.assertIn("idea-001", out)


class TestVerdictAutomation(Harness):
    def _sc(self):
        sys.path.insert(0, str(self.repo))
        import importlib, scout as sc
        importlib.reload(sc)
        sc.ROOT = self.repo
        sc.BRIEF = self.repo / "evidence" / "portfolio_brief.md"
        sc.ledger_mod.ROOT = self.repo
        sc.ledger_mod.LEDGER = self.repo / "ledger.jsonl"
        sc.ledger_mod.DIGEST = self.repo / "evidence" / "ledger_digest.md"
        return sc

    def test_consensus_json_block_updates_ledger(self):
        sc = self._sc()
        sc.ledger_mod.append({"ledger_id": "idea-001", "status": "SHORTLISTED"})
        (self.repo / "ideas" / "001" / "consensus.md").write_text(
            "# s\n\nprose\n\n```json\n"
            '{"verdict": "PAUSE", "unblock": "await release"}\n```\n')
        self.assertEqual(sc._apply_consensus_verdict(1), "PAUSE")
        self.assertEqual(sc.ledger_mod.load()["idea-001"]["status"], "PAUSED")

    def test_kill_verdict_with_bad_code_falls_back_unclassified(self):
        sc = self._sc()
        sc.ledger_mod.append({"ledger_id": "idea-001", "status": "SHORTLISTED"})
        (self.repo / "ideas" / "001" / "consensus.md").write_text(
            "```json\n{\"verdict\": \"KILL\", \"kill_code\": \"MADE_UP\", \"unblock\": \"n/a\"}\n```\n")
        self.assertEqual(sc._apply_consensus_verdict(1), "KILL")
        e = sc.ledger_mod.load()["idea-001"]
        self.assertEqual(e["status"], "REJECTED")
        self.assertEqual(e["kill_code"], "UNCLASSIFIED")

    def test_merge_demotes_unevidenced_keystone_and_stamps_seed_source(self):
        sc = self._sc()
        d = self.repo / "ideas" / "scout-060"; d.mkdir()
        (d / "fiction_candidates.json").write_text(json.dumps({"candidates": [
            {"title": "f", "question": "q?", "track": "fiction",
             "keystone_status": "INSPECTED_TRUE"}]}))
        (d / "fiction_seed.json").write_text('{"source": "human", "concepts": ["a","b"]}')
        sc._merge_candidates(d, ["fiction"], 60)
        merged = json.loads((d / "candidates_all.json").read_text())
        self.assertEqual(merged["candidates"][0]["keystone_status"], "NOT_INSPECTED")
        e = sc.ledger_mod.load()["scout-060-c01"]
        self.assertEqual(e.get("seed_source"), "human")

    def test_seed_draw_override_records_human_source(self):
        sc = self._sc()
        s = sc.seed_draw(concepts_override=["information entropy", "concept network"])
        self.assertEqual(s["source"], "human")
        self.assertEqual(s["concepts"], ["information entropy", "concept network"])
        self.assertEqual(sc.seed_draw()["source"], "random")


class TestCiCommandVariant(Harness):
    def test_scout_ci_selects_command_ci(self):
        # command_ci writes a marker; SCOUT_CI must select it, absence must not.
        marker = self.dir / "ci_variant_used.txt"
        fake_ci = self.dir / "fake_ci.py"
        fake_ci.write_text(
            "#!/usr/bin/env python3\n"
            "import os, sys, pathlib\n"
            "sys.stdin.read()\n"
            "root = pathlib.Path(os.environ['FAKE_REPO'])\n"
            f"pathlib.Path({str(marker)!r}).write_text('yes')\n"
            "(root / 'ideas' / '001').mkdir(parents=True, exist_ok=True)\n"
            "(root / 'ideas' / '001' / 'critique.md').write_text('ci critique')\n")
        toml = (self.repo / "AGENTS.toml").read_text()
        toml = toml.replace('[codex]\nenabled = true\nstdin = true',
                            '[codex]\nenabled = true\nstdin = true\n'
                            f'command_ci = ["{sys.executable}", "{fake_ci}"]')
        (self.repo / "AGENTS.toml").write_text(toml)
        self.commit()
        r = self.scout("run", "critique", "--idea", "1")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertFalse(marker.exists(), "command_ci used without SCOUT_CI")
        self.commit()
        r = self.scout("run", "critique", "--idea", "1", SCOUT_CI="1")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertTrue(marker.exists(), "SCOUT_CI did not select command_ci")


class TestRotation(Harness):
    def test_pair_swaps_on_odd_cycles_only(self):
        sys.path.insert(0, str(self.repo))
        import importlib, scout as sc
        importlib.reload(sc)
        cfg = {"rotation": {"enabled": True, "pair": ["claude", "codex"]}}
        self.assertEqual(sc.effective_agent("claude", cfg, cycle_no=2), "claude")
        self.assertEqual(sc.effective_agent("claude", cfg, cycle_no=3), "codex")
        self.assertEqual(sc.effective_agent("codex", cfg, cycle_no=3), "claude")
        cfg["rotation"]["enabled"] = False
        self.assertEqual(sc.effective_agent("claude", cfg, cycle_no=3), "claude")


class TestCycle(Harness):
    def start_state(self, n=9):
        (self.repo / "orchestrator" / "state.json").write_text(
            json.dumps({"next_scout": n, "selected_idea": 1}) + "\n")
        self.commit()

    def test_fiction_cycle_is_blind_and_merges(self):
        self.start_state(9)
        r = self.scout("cycle", "--tracks", "fiction", action="cycle_auto")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        d = self.repo / "ideas" / "scout-009"
        merged = json.loads((d / "candidates_all.json").read_text())
        tracks = {c.get("track") for c in merged["candidates"]}
        self.assertEqual(tracks, {"fiction"})
        # Writer prompt must be blind: no charter/rules/memory context.
        writer_prompt = Path(str(self.receipt) + ".fiction_scout").read_text()
        for leak in ("critical research collaborator", "COLLABORATOR_RULES",
                     "ledger_digest", "SCORING_RUBRIC", "portfolio_brief"):
            self.assertNotIn(leak, writer_prompt, f"fiction writer saw {leak}")
        self.assertIn("fiction_seed.json", writer_prompt)
        # Refiner must not see the story or the seed card.
        refiner_prompt = Path(str(self.receipt) + ".fiction_refine").read_text()
        self.assertNotIn("ZZSTORYMARKERZZ", refiner_prompt, "refiner saw the fiction")
        self.assertNotIn('"twist"', refiner_prompt, "refiner saw the seed card")
        self.assertIn("Claimed finding", refiner_prompt)
        # Scouted candidates land in the ledger at SCOUTED scrutiny.
        recs = (self.repo / "ledger.jsonl").read_text()
        self.assertIn("scout-009-c01", recs)

    def test_failed_stage_checkpoints_and_resume_completes(self):
        self.start_state(9)
        r = self.scout("cycle", "--tracks", "fiction", action="cycle_auto",
                       FAKE_FAIL_STAGE="fiction_extract")
        self.assertNotEqual(r.returncode, 0)
        state = json.loads((self.repo / "orchestrator" / "state.json").read_text())
        self.assertEqual(state["cycle"]["stages"]["fiction_scout"], "done")
        self.assertEqual(state["cycle"]["stages"]["fiction_extract"], "failed")
        dirty = subprocess.run(["git", "status", "--porcelain"], cwd=self.repo,
                               capture_output=True, text=True).stdout.strip()
        self.assertEqual(dirty, "", "failed stage left the tree dirty; resume would be blocked")
        r2 = self.scout("resume", action="cycle_auto")
        self.assertEqual(r2.returncode, 0, r2.stdout + r2.stderr)
        d = self.repo / "ideas" / "scout-009"
        self.assertTrue((d / "fiction_candidates.json").exists())
        state = json.loads((self.repo / "orchestrator" / "state.json").read_text())
        self.assertTrue(all(v == "done" for v in state["cycle"]["stages"].values()))

    def test_stage_writing_nothing_is_a_failed_stage(self):
        # Regression for cycle 005: agent exited 0 without writing its artifact
        # and an empty pool sailed through merge and audit.
        self.start_state(9)
        r = self.scout("cycle", action="cycle_auto", FAKE_SKIP_WRITE_STAGE="scout")
        self.assertNotEqual(r.returncode, 0, "silent-empty scout stage passed")
        self.assertIn("did not write", r.stdout + r.stderr)
        state = json.loads((self.repo / "orchestrator" / "state.json").read_text())
        self.assertEqual(state["cycle"]["stages"]["scout"], "failed")
        # Agent output is preserved for post-mortem.
        self.assertTrue((self.repo / "ideas" / "scout-009" / "log_scout.txt").exists())
        # And it is resumable once the agent behaves.
        r2 = self.scout("resume", action="cycle_auto")
        self.assertEqual(r2.returncode, 0, r2.stdout + r2.stderr)
        self.assertTrue((self.repo / "ideas" / "scout-009" / "scout_candidates.json").exists())

    def test_dry_run_with_pending_cycle_does_not_resume(self):
        # Regression: --dry-run --resume-or-new used to resume the real cycle.
        self.start_state(9)
        self.scout("cycle", "--tracks", "fiction", action="cycle_auto",
                   FAKE_FAIL_STAGE="fiction_extract")
        r = self.scout("cycle", "--dry-run", "--resume-or-new", action="cycle_auto")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("unfinished", r.stdout)
        state = json.loads((self.repo / "orchestrator" / "state.json").read_text())
        self.assertEqual(state["cycle"]["stages"]["fiction_extract"], "failed",
                         "dry run resumed the pending cycle")

    def test_baseline_cycle_default_and_dry_run_spends_nothing(self):
        self.start_state(9)
        r = self.scout("cycle", "--dry-run", action="cycle_auto")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertFalse((self.repo / "ideas" / "scout-009").exists(),
                         "dry run created a scout dir")
        r = self.scout("cycle", action="cycle_auto")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        d = self.repo / "ideas" / "scout-009"
        self.assertTrue((d / "scout_candidates.json").exists())
        self.assertTrue((d / "candidates_all.json").exists())
        self.assertTrue((d / "novelty_audit.md").exists())


if __name__ == "__main__":
    unittest.main(verbosity=2)
