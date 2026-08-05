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
else:
    (root / target).mkdir(parents=True, exist_ok=True)
    (root / target / "critique.md").write_text("fake critique" + NL)
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


if __name__ == "__main__":
    unittest.main(verbosity=2)
