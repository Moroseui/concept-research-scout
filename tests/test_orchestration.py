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
                     "ledger_digest", "SCORING_RUBRIC"):
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
