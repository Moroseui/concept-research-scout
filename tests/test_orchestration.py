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

# ---------------------------------------------------------------------------
# P0.4 fixture repo (2026-08-14). The suite used to copytree the entire live
# repo (~29 MB, dominated by ideas/ logs and prompts) into a temp dir for
# EVERY test, so wall time scaled with project history. Tests only actually
# depend on the small structural surface: code-adjacent data (templates,
# orchestrator, docs, evidence, ledger, charter) plus empty ideas/ and
# probes/ that helpers mkdir into. The fixture is built ONCE per session by
# pruning the live repo -- never a hand-maintained synthetic copy, so it
# cannot drift from production the way fabricated fixtures did (see the
# scoring-bug note below). Anything new a test legitimately needs must be
# added to _FIXTURE_KEEP, which is a deliberate, reviewable act.
# ---------------------------------------------------------------------------
_FIXTURE_KEEP = ("CHARTER.md", "AGENTS.toml", "Makefile", ".gitignore",
                 "ledger.jsonl", "requirements.txt",
                 "scout.py", "setup.py",
                 "templates", "orchestrator", "docs", "evidence", "portfolio")
_FIXTURE_CACHE = None


def fixture_repo():
    """Build (once) and return the pruned fixture repo path."""
    global _FIXTURE_CACHE
    if _FIXTURE_CACHE is not None:
        return _FIXTURE_CACHE
    base = Path(tempfile.mkdtemp(prefix="scout-fixture-")) / "repo"
    base.mkdir()
    for name in _FIXTURE_KEEP:
        src = REPO / name
        if not src.exists():
            continue
        if src.is_dir():
            shutil.copytree(src, base / name, ignore=shutil.ignore_patterns(
                "__pycache__", "*.pyc"))
        else:
            shutil.copy2(src, base / name)
    (base / "ideas").mkdir()
    (base / "probes").mkdir()
    _FIXTURE_CACHE = base
    return base

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
    cand = ('{"candidates": [{"title": "Fake STAGE", "question": "is the fake model using fake signal?", '
        '"deliverable_sentence": "the model is using fake signal", "keystone_prerequisite": "the fixture asset exists", "keystone_status": "NOT_INSPECTED", "priority_score": 3.0, "scores": {"interest": {"value": 3, "why": "fx"}}, "dataset": "D", '
        '"keystone_prerequisite": "the fake asset exists and is linkable", '
        '"keystone_status": "NOT_INSPECTED", "priority_score": 3.0, '
        '"scores": {"interest": {"value": 3, "why": "fixture"}}}]}')
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
        (outdir / "novelty_manifest.json").write_text(
            '{"searched_at": "2026-08-10", "queries": [{"query": "q", "source": "s"}], '
            '"neighbors": [{"candidate": "C1", "identifier": "PMID:1", "access": "abstract"}]}' + NL)

        (outdir / "novelty_audit.md").write_text("audit" + NL)
    elif stage == "librarian":
        (outdir / "librarian_report.md").write_text("report" + NL)
        (outdir / "verdict_updates.json").write_text(
            '{"updates": [{"ledger_id": "scout-050-c01", "novelty_verdict": "NOVEL_VERIFIED", "reason": "test"}]}' + NL)
        (outdir / "librarian_proposals.json").write_text(
            '{"proposals": [{"title": "revived idea", "question": "is the model using the fixture signal?", "parent_ids": ["idea-011"], "revival_basis": "b", "sketch": "s"}]}' + NL)
    elif stage == "keystone":
        v = os.environ.get("FAKE_KEYSTONE_VERDICT", "PASS")
        kc = '"kill_code": "DATA_ACCESS", ' if v == "KILL" else ""
        (outdir / "keystone_screen.md").write_text(
            "# screen" + NL + NL + "```json" + NL
            + '{"verdict": "' + v + '", ' + kc
            + '"evidence": "quoted line", "source": "https://x/y#L1", "note": "fake"}'
            + NL + "```" + NL)
    elif stage == "probe_code":
        idea = outdir.name if outdir.name.isdigit() else "001"
        pdir = root / "probes" / idea
        pdir.mkdir(parents=True, exist_ok=True)
        (pdir / "run.py").write_text(
            "import argparse" + NL
            + "ap = argparse.ArgumentParser()" + NL
            + "ap.add_argument('--smoke-test', action='store_true')" + NL
            + "ap.add_argument('--output-dir', default='.')" + NL
            + "print('probe ok')" + NL)
        (pdir / "README.md").write_text("# probe" + NL)
        (pdir / "requirements.txt").write_text("pandas" + NL)
    elif stage == "probe_review":
        v = os.environ.get("FAKE_PROBE_REVIEW", "APPROVE")
        blocking = '["missing summary.json"]' if v == "REVISE" else "[]"
        (outdir / "probe_review.md").write_text(
            "# review" + NL + "```json" + NL
            + '{"verdict": "' + v + '", "blocking": ' + blocking + ', "note": "fake"}'
            + NL + "```" + NL)
    elif stage == "actioner":
        (outdir / "actions.md").write_text("## Decisions waiting on the human" + NL + "- none" + NL)
    elif "TRANSCRIPT SO FAR" in prompt:
        t = outdir / "debate.md"
        prev = t.read_text() if t.exists() else "# Debate transcript" + NL + NL
        side = "PROPOSER" if prev.count("CRITIC") > prev.count("PROPOSER") else "CRITIC"
        n = prev.count("## Round ") + 1
        t.write_text(prev + "## Round " + str(n) + " - " + side + NL + NL
                     + "**Status:** CONVERGED" + NL + NL)
    elif "consensus.md" in prompt:
        v = os.environ.get("FAKE_CONSENSUS_VERDICT", "")
        body = "fake consensus" + NL
        if v:
            body += NL + "```json" + NL + '{"verdict": "' + v + '", "unblock": "sync the card"}' + NL + "```" + NL
        (outdir / "consensus.md").write_text(body)
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
        shutil.copytree(fixture_repo(), self.repo)

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

    def make_cycle_outputs(self, scoutdir, verdicts):
        d = self.repo / "ideas" / scoutdir
        d.mkdir(parents=True, exist_ok=True)
        cands = []
        for i in range(1, len(verdicts) + 1):
            c = dict(GOLDEN_CANDIDATE)
            c["title"] = f"cand {i}"
            c["question"] = "Does the fixture rank correctly?"
            c["deliverable_sentence"] = "the model is using fixture signal"
            c["priority_score"] = float(5 - i)
            c["priority_arithmetic"] = "fixture"
            cands.append(c)
        (d / "candidates_all.json").write_text(json.dumps(
            {"cycle": 9, "tracks": ["baseline"], "notes": {}, "candidates": cands}) + "\n")
        rows = "".join(f"| C{i} | `{v}` | `NEW_CAPABILITY` |\n"
                       for i, v in enumerate(verdicts, 1))
        (d / "novelty_audit.md").write_text("# audit\n\n| Candidate | Verdict | code |\n|---|---|---|\n" + rows)

    def _sc(self):
        """Import the repo-copy scout module with paths patched to the harness."""
        sys.path.insert(0, str(self.repo))
        import importlib, scout as sc
        importlib.reload(sc)
        sc.ROOT = self.repo
        sc.BRIEF = self.repo / "evidence" / "portfolio_brief.md"
        sc.ledger_mod.ROOT = self.repo
        sc.ledger_mod.LEDGER = self.repo / "ledger.jsonl"
        sc.ledger_mod.DIGEST = self.repo / "evidence" / "ledger_digest.md"
        return sc

    def make_hermetic(self, wipe_idea_dirs=False):
        """Erase the live repo's accumulated state from the harness copy.
        Tests must never depend on what the repository has lived through:
        ledger rows, digests, and (optionally) idea/scout dirs accumulate
        from real runs and have now broken three test classes the same way."""
        import shutil as _sh
        for f in ("ledger.jsonl", "evidence/ledger_digest.md",
                  "evidence/portfolio_brief.md", "evidence/librarian_proposals.md",
                  "evidence/actions.md"):
            (self.repo / f).unlink(missing_ok=True)
        # Outputs of the features under test always start from zero: real
        # librarian/actioner passes accumulate in the live repo and broke a
        # fourth test class by shifting run numbering.
        for pat in ("librarian-*", "actioner-*"):
            for d in (self.repo / "ideas").glob(pat):
                _sh.rmtree(d)
        # In-flight real cycles leak through state.json (strain five: a live
        # repo mid-cycle broke TestCycle via a colliding scout dir number).
        # Neutral state, numbered above any real scout dir.
        (self.repo / "orchestrator" / "state.json").write_text(
            '{"next_scout": 50, "selected_idea": 1}\n')
        if wipe_idea_dirs:
            for d in (self.repo / "ideas").glob("scout-*"):
                _sh.rmtree(d)
            for d in (self.repo / "ideas").glob("[0-9][0-9][0-9]"):
                if d.name != "001":
                    _sh.rmtree(d)
        self.commit()

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


# Golden production artifact: a verbatim candidate from real cycle 007.
# Fabricated fixtures encoded stale assumptions and masked the scoring bug
# (flat numbers vs {value, why} objects); tests must also run against what
# the agents actually produce.
GOLDEN_CANDIDATE = json.loads(r"""{
 "id": "C1",
 "parent_ids": [],
 "revival_basis": null,
 "search_mode": "A",
 "entry_point": 1,
 "title": "The knee-pain model may be reading trabecular stress architecture that KL grade throws away",
 "question": "Is the knee-pain model of Pierson et al. using directional medial tibial subchondral trabecular texture, rather than only joint-space narrowing and osteophytes, to recover pain that radiographic Kellgren-Lawrence grading misses?",
 "rung": {
  "target": 3,
  "current": 0,
  "move_up": "A validated texture measurement and score association are exploratory; a selective loss of pain prediction after erasing the texture direction, with matched nuisance-direction controls and bilateral/longitudinal replication, reaches rung 1. Acquisition harmonization and site-held-out replication gate rung 2; the named texture then supplies rung 3."
 },
 "deliverable_sentence": "The knee-pain model is using medial tibial subchondral trabecular texture\u2014directional thickening and rarefaction of the load-bearing bone beneath the cartilage.",
 "X_measurement": {
  "X": "Directional fractal signature of medial tibial subchondral trabecular bone, summarized across horizontal and vertical scales in a landmark-defined ROI.",
  "how": "Locate tibial plateau landmarks with a released knee landmark model or deterministic geometry, place the published subchondral ROI, and compute variance-orientation-transform fractal signatures. Janvier et al. used this measurement on OAI radiographs (DOI 10.1016/j.joca.2017.09.004; PMID 28935435); the OARSI/FNIH consortium used validated semiautomated software (PMID 29024470).",
  "could_compute_today_without_asking_anyone": "Yes in principle: the formula is defined and requires pixels plus geometric landmarks, not a radiologist. The exact validated implementation and landmark model still need to be obtained or reproduced before a confirmatory run."
 },
 "suspected_signal": "Subchondral bone remodels along habitual load paths. Horizontal trabecular thickening and direction-dependent rarefaction alter radiographic texture at scales not represented by the coarse KL vocabulary and may track painful bone stress or marrow pathology.",
 "keystone_prerequisite": "The frozen Pierson pain model or exactly reproducible checkpoint can be run on OAI images that also support stable, automated directional fractal-signature measurement, and the measured texture has enough within-KL and within-person variation to identify a selective model-use effect.",
 "keystone_status": "NOT_INSPECTED",
 "keystone_evidence": "Nearest facts inspected: Pierson et al., Nature Medicine 2021, DOI 10.1038/s41591-020-01192-7, states that OAI images/clinical data reproduce the analysis; Janvier et al., DOI 10.1016/j.joca.2017.09.004, measured subchondral texture in OAI. The actual checkpoint-to-image pipeline and joint distribution were not inspected.",
 "keystone_residual_assumption": "The easy facts are that the pain model and texture literature both use OAI. I am still assuming the exact frozen model is runnable and that texture varies independently of joint-space width, osteophytes, alignment, and acquisition processing. That independence is load-bearing and is therefore included in the keystone.",
 "rung_reached": "No rung yet. Conditional rung 1 after selective internal concept erasure; rung 2 after site/acquisition and alignment controls; rung 3 only then.",
 "dies_like_prior": "It resembles idea-001 in using OAI clinical labels, but pain-label provenance is not the concept measurement and the primary readout is a frozen model's score change after an image-computable texture-direction intervention. It avoids DATA_INSUFFICIENT by gating on the actual model/OAI join and avoids CIRCULARITY because X is not the pain label or KL grade.",
 "closest_prior_work": [
  {
   "citation": "Pierson et al., Nature Medicine 2021",
   "identifier": "DOI 10.1038/s41591-020-01192-7",
   "verified_fact": "A deep model predicted knee pain from OAI radiographs and explained pain variation beyond radiologist-assigned severity.",
   "delta": "The paper did not name or measure directional subchondral trabecular texture as the model-used signal."
  },
  {
   "citation": "Janvier et al., Osteoarthritis and Cartilage 2017",
   "identifier": "DOI 10.1016/j.joca.2017.09.004; PMID 28935435",
   "verified_fact": "Directional trabecular texture on OAI radiographs predicted incident radiographic OA.",
   "delta": "It studied OA incidence, not what a pain-prediction network uses."
  }
 ],
 "existing_assets": [
  "OAI bilateral longitudinal knee radiographs and WOMAC pain data (registration-controlled access, not an unconfirmed DUA-gated dependency for the card)",
  "Published pain-model architecture/reproduction materials",
  "Published fractal-signature formula and OAI texture precedents"
 ],
 "smallest_decisive_experiment": "Stage 0: verify checkpoint inference and texture repeatability, then quantify within-KL texture variation. Exploratory: fit a validation-only probe from frozen embeddings to X. Confirmatory: freeze that direction, erase only it from test embeddings, and compare the change in knee-specific pain score with equal-norm random directions, KL/joint-space directions, and left-right within-person contrasts. The model uses X only if texture erasure selectively harms prediction and the effect scales with measured X.",
 "use_vs_association": "A score-X regression is exploratory. The use claim requires selective frozen-representation erasure of the validation-learned X direction, with matched-direction controls, and must replicate within bilateral or longitudinal comparisons.",
 "standing_confounds_addressed": {
  "scanner_vendor_protocol_reconstruction_site": "Site-held-out evaluation and acquisition/processing strata; not fully ruled out until Stage 0 confirms metadata.",
  "positioning": "Alignment and flexion landmarks are explicit nuisance concepts and matched erasure controls.",
  "habitus": "Bilateral within-person contrasts hold BMI/habitus fixed; residual side-specific loading remains.",
  "prevalence_referral": "Single prospective OAI cohort limits spectrum; not ruled out externally.",
  "label_leakage": "Pain is self-report, not available in pixels or radiology annotations; laterality/joint identifiers must be stripped."
 },
 "alternative_explanations": [
  {
   "alternative": "Texture is a proxy for malalignment or joint-space narrowing.",
   "resolution": "Measure both, learn nuisance directions, and require texture erasure to add harm beyond them."
  },
  {
   "alternative": "Computed-radiography post-processing creates texture differences.",
   "resolution": "Site/acquisition strata and bilateral same-image contrasts address much, but external device replication remains necessary."
  },
  {
   "alternative": "Erasure removes generic image information rather than X.",
   "resolution": "Equal-norm random, landmark, and KL-direction erasures plus retained reconstruction performance test selectivity."
  }
 ],
 "anticipated_negative": {
  "classification": "sensitivity-limited",
  "reason": "A null erasure effect could mean the representation distributes texture nonlinearly. It becomes decisive only after a prespecified probe-reliability floor and minimum score-change equivalence margin are met."
 },
 "cross_domain": {
  "borrowed_construct": "Load-path adaptation from bone mechanobiology.",
  "measurement_implied": "Directional, scale-dependent trabecular fractal signature rather than generic image texture.",
  "if_analogy_dropped": "The experiment would otherwise test undirected texture. The analogy changes the preregistered X to horizontal-versus-vertical signatures and predicts the sign/scales of the effect."
 },
 "remaining_legwork": "2 days to inspect checkpoint/reproduction assets; 3-5 days for an OAI access and join audit; 1 week for texture repeatability and collinearity Stage 0. First scientific decision in about 2 weeks if access is active.",
 "scores": {
  "clarity": {
   "value": 5,
   "why": "One model, one named bone compartment, one defined texture measurement."
  },
  "identifiability": {
   "value": 3,
   "why": "Internal erasure and bilateral controls improve on association, but texture is entangled with alignment and erasure may not be specific."
  },
  "medical_relevance": {
   "value": 4,
   "why": "It could name the missing radiographic substrate behind clinically important pain discordance."
  },
  "interest": {
   "value": 5,
   "why": "It attempts to decode a documented model-human gap with a bone quantity clinicians can recognize."
  },
  "prior_legwork": {
   "value": 4,
   "why": "Both the gap and the exact measurement have OAI precedents."
  },
  "feasibility": {
   "value": 3,
   "why": "Capped: keystone not inspected; access and checkpoint reproducibility remain."
  },
  "data_readiness": {
   "value": 3,
   "why": "OAI is established but registration-controlled."
  },
  "evaluation_readiness": {
   "value": 3,
   "why": "Fractal metrics exist; selective-erasure calibration needs custom controls."
  },
  "negative_result_value": {
   "value": 2,
   "why": "The anticipated null is sensitivity-limited."
  },
  "novelty_confidence": {
   "value": 3,
   "why": "Capped and no exhaustive review; the precise model-to-texture link was not located."
  },
  "regret": {
   "value": 5,
   "why": "Two mature OAI literatures sit one model-use experiment apart."
  }
 },
 "priority_score": 3.65,
 "priority_arithmetic": "0.20*3 + 0.15*3 + 0.15*4 + 0.10*4 + 0.10*5 + 0.10*5 + 0.10*2 + 0.05*3 + 0.05*3 = 3.65",
 "unverified_claims": [
  "A runnable Pierson checkpoint is currently available",
  "Texture varies sufficiently within KL grade and acquisition strata",
  "The validation-learned concept direction is selectively erasable"
 ],
 "track": "baseline"
}""")


GOLDEN_MODE_C = json.loads(r"""{
 "id": "C4",
 "parent_ids": [],
 "revival_basis": null,
 "search_mode": "C",
 "entry_point": 2,
 "title": "The PE model may read contrast flowing backward as a pressure gauge",
 "question": "Is a pulmonary-embolism CTPA model using contrast reflux into the inferior vena cava and hepatic veins as a hydraulic back-pressure signal when it predicts right-heart strain?",
 "rung": {
  "target": 3,
  "current": 0,
  "move_up": "A controlled reflux-direction erasure with bolus-timing and RV/LV controls reaches rung 1; cross-site/protocol replication gates rung 2; IVC/hepatic-vein reflux is already named at rung 3."
 },
 "deliverable_sentence": "The pulmonary-embolism model is using contrast reflux into the inferior vena cava and hepatic veins as a sign of elevated right-sided pressure.",
 "X_measurement": {
  "X": "IVC/hepatic-vein contrast reflux burden: contrast-enhanced volume or cranio-caudal extent below the right atrium, normalized by right-atrial or aortic blood-pool attenuation.",
  "how": "Segment right atrium, IVC, and hepatic veins on CTPA; threshold contrast relative to the right atrium and integrate enhanced venous volume/extent. This is a physical attenuation-and-geometry measurement rather than a reader grade.",
  "could_compute_today_without_asking_anyone": "Yes in definition, but an existing validated open segmentation stack covering hepatic veins on RSNA-STR CTPA was not inspected; feasibility is therefore capped."
 },
 "suspected_signal": "During contrast injection, elevated right-sided pressure and tricuspid regurgitant flow can drive contrast caudally into the IVC and hepatic veins. The visible reflux column is a transient fluid-dynamic readout of right-heart loading, distinct from ventricular enlargement.",
 "specific_artifact_confused_with_signal": "Injection rate, scan delay, saline chaser, cardiac output, and respiratory phase can produce reflux-like enhancement independent of pathologic pressure.",
 "keystone_prerequisite": "RSNA-STR CTPAs retain enough IVC/hepatic-vein coverage and bolus heterogeneity can be controlled well enough that automated reflux burden varies independently from RV/LV ratio and global contrast timing, while a frozen right-heart-strain model/checkpoint remains runnable.",
 "keystone_status": "NOT_INSPECTED",
 "keystone_evidence": "Nearest inspected primary artifact: Colak et al., The RSNA Pulmonary Embolism CT Dataset, Radiology: AI 2021, DOI 10.1148/ryai.2021200254, PMCID PMC8043364, confirms study-level RV/LV >=1 labels and QA-contrast labels. It does not prove adequate hepatic-vein coverage, injection metadata, or a particular frozen checkpoint.",
 "keystone_residual_assumption": "The easy fact is that the dataset labels right-heart strain. I am still assuming the voxels needed to measure reflux are consistently in frame and that bolus timing is recoverable or inferable independently. That, not label availability, is the keystone.",
 "rung_reached": "No rung yet; Mode C tolerates the uninspected gate but not a model-use claim before it passes.",
 "dies_like_prior": "It resembles idea-006 in proposing a model intervention, but does not delete the patient or create a constant-filled OOD image; it intervenes internally on a measured concept direction. It avoids CIRCULARITY because reflux is not RV/LV ratio, although both reflect the same hemodynamic state and must be dissociated.",
 "closest_prior_work": [
  {
   "citation": "Colak et al., RSNA Pulmonary Embolism CT Dataset",
   "identifier": "DOI 10.1148/ryai.2021200254; PMCID PMC8043364",
   "verified_fact": "The public CTPA dataset includes RV/LV and contrast-quality labels.",
   "delta": "It did not quantify IVC reflux or decode what an RV/LV classifier uses."
  },
  {
   "citation": "Prognostic Value of CT-Derived Indicators of Right-Heart Strain and Thrombus Burden",
   "identifier": "PMCID PMC12840362",
   "verified_fact": "IVC contrast reflux and RV/LV ratio were evaluated as separate CT indicators in acute PE.",
   "delta": "It is an outcome association study, not a model-use study."
  }
 ],
 "existing_assets": [
  "RSNA-STR CTPA dataset and labels",
  "Published PE multitask architectures, including DOI-linked open papers",
  "Generic cardiac/vascular CT segmentation models"
 ],
 "smallest_decisive_experiment": "Stage 0: inspect 100 stratified scans for IVC/hepatic coverage, injection metadata, and automated reflux repeatability; quantify reflux-RV/LV-bolus collinearity. Then learn reflux, RV/LV, clot-burden, and contrast-timing directions on validation embeddings. On locked test embeddings erase each direction separately and jointly. The claim requires selective reduction of the model's RV-strain score after reflux erasure beyond RV/LV and timing directions, with no comparable effect on PE-location outputs.",
 "use_vs_association": "The model uses reflux only if selective reflux-direction erasure changes the frozen RV-strain output after RV/LV, clot, and bolus-timing directions are controlled; marginal correlation is explicitly insufficient.",
 "standing_confounds_addressed": {
  "scanner_vendor_protocol_reconstruction_site": "Site/vendor/protocol splits where metadata exist; injection protocol is the dominant unresolved confound.",
  "positioning": "Less important than inspiration and coverage; both measured.",
  "habitus": "May change bolus and noise; body diameter/SNR control.",
  "prevalence_referral": "All are clinically referred CTPA; PE prevalence strata do not remove referral bias.",
  "label_leakage": "RV/LV labels came from image reads but X is computed from voxels and primary readout is model self-change."
 },
 "alternative_explanations": [
  {
   "alternative": "Reflux is only a bolus-timing/injection artifact.",
   "resolution": "Normalize to blood pool, learn timing direction, stratify QA-contrast and protocol; absent metadata may remain fatal."
  },
  {
   "alternative": "The model uses visible RV dilation, with reflux merely correlated.",
   "resolution": "Separate and joint RV/LV versus reflux erasures."
  },
  {
   "alternative": "Erasure removes global contrast information.",
   "resolution": "Test PE localisation and contrast-QA outputs plus equal-norm global-contrast direction controls."
  }
 ],
 "anticipated_negative": {
  "classification": "decisive",
  "reason": "If reflux is reliably encoded yet its selective erasure has an equivalently near-zero effect while RV/LV erasure changes the score, the hydraulic-reflux mechanism is weakened directly."
 },
 "cross_domain": {
  "borrowed_construct": "Hydraulic back-pressure and transient tracer transport.",
  "measurement_implied": "Normalized retrograde contrast volume/extent, not a binary reflux label.",
  "if_analogy_dropped": "The experiment would likely collapse reflux to presence/absence. The fluid-mechanics account requires normalization to input bolus and predicts a dose-like relationship with retrograde extent."
 },
 "remaining_legwork": "2 days for coverage/metadata inspection, 3-5 days to validate segmentation and timing normalization, and 1 week to identify/reproduce a checkpoint. First kill/continue decision in one week.",
 "scores": {
  "mechanism_clarity": {
   "value": 5,
   "why": "A named retrograde contrast volume with an explicit pressure/transport mechanism and normalization."
  },
  "identifiability": {
   "value": 3,
   "why": "Separate erasures address RV dilation, but injection timing may remain inseparable."
  },
  "interest": {
   "value": 5,
   "why": "The model could be reading a fleeting fluid-dynamic sign rather than anatomy."
  },
  "medical_relevance": {
   "value": 4,
   "why": "Right-heart strain changes PE triage and prognosis."
  },
  "clarity": {
   "value": 5,
   "why": "Specific output, vessel compartment, and physical mechanism."
  },
  "feasibility": {
   "value": 2,
   "why": "Coverage, segmentation, metadata, and checkpoint are uninspected."
  },
  "novelty_confidence": {
   "value": 3,
   "why": "Capped; no direct model-use study found, but reflux prognostic studies are established."
  },
  "prior_legwork": {
   "value": 3,
   "why": "Public data and labels exist, but the decisive measurement pipeline does not yet."
  },
  "data_readiness": {
   "value": 3,
   "why": "RSNA data are public; required coverage remains unknown."
  },
  "evaluation_readiness": {
   "value": 3,
   "why": "The erasure comparison is clear; reflux normalization needs validation."
  },
  "negative_result_value": {
   "value": 5,
   "why": "With reliability gates met, RV/LV-positive/reflux-null erasure is a decisive mechanistic negative."
  },
  "regret": {
   "value": 4,
   "why": "A small coverage audit quickly determines whether a striking mechanism is real work or fantasy."
  }
 },
 "mode_c_priority_score": 4.35,
 "priority_arithmetic": "0.30*5 + 0.25*3 + 0.20*5 + 0.15*4 + 0.10*5 = 4.35",
 "unverified_claims": [
  "Hepatic veins are consistently covered",
  "Injection metadata or a valid timing proxy exists",
  "A frozen reproducible RV-strain checkpoint is available"
 ],
 "track": "baseline"
}""")


class TestPipeline(Harness):
    def setUp(self):
        # Hermetic: the harness copies the real repo, which accumulates real
        # scouting cycles and ledger rows over time. The backlog is global by
        # design, so pipeline tests must start from an empty world or every
        # new real cycle would change their results.
        super().setUp()
        self.make_hermetic(wipe_idea_dirs=True)


    def test_golden_candidate_scores_nonzero_and_validates(self):
        # Regression for the 0.0-scoring bug: the REAL production card must
        # produce its own priority_score and pass schema validation.
        sc = self._sc()
        self.assertAlmostEqual(sc._mean_score(GOLDEN_CANDIDATE),
                               GOLDEN_CANDIDATE["priority_score"], places=2)
        self.assertGreater(sc._mean_score(GOLDEN_CANDIDATE), 0.0)
        self.assertIsNone(sc._validate_card(GOLDEN_CANDIDATE),
                          "real production card fails the schema")

    def test_mode_c_golden_uses_mode_c_rubric(self):
        sc = self._sc()
        self.assertAlmostEqual(sc._mean_score(GOLDEN_MODE_C), 4.35, places=2,
                               msg="Mode-C card must rank by the Mode-C rubric")

    def test_unrecomputable_priority_score_is_never_trusted(self):
        sc = self._sc()
        c = {"title": "Bad but valid shape", "question": "does this rank absurdly high?",
             "deliverable_sentence": "the model is using X", "priority_score": 99}
        self.assertLess(sc._mean_score(c), 5.0,
                        "a card without recomputable rubric named its own rank")

    def test_keystone_pass_without_evidence_demotes_not_passes(self):
        sc = self._sc()
        d = self.repo / "ideas" / "001"
        (d / "keystone_screen.md").write_text(
            "# s\n\n```json\n{\"verdict\": \"KILL\", \"kill_code\": \"DATA_ACCESS\", "
            "\"evidence\": \"\", \"source\": \"\"}\n```\n")
        self.assertEqual(sc._apply_keystone_verdict(1), "UNVERIFIABLE")
        self.assertNotEqual(sc.ledger_mod.load().get("idea-001", {}).get("status"),
                            "REJECTED", "evidence-free KILL killed an idea")

    def test_fiction_kernel_without_self_score_merges(self):
        # Regression for the run that killed fiction v2's first kernel: a
        # schema-valid Mode-C card lacking mode_c_priority_score must MERGE
        # (ranking recomputes and never trusts self-scores anyway), with the
        # gap soft-noted.
        sc = self._sc()
        d = self.repo / "ideas" / "scout-065"; d.mkdir()
        c = {"title": "CT-CLIP calc vs diaphragm height",
             "question": "does the calcification head use diaphragm height?",
             "deliverable_sentence": "the model is using diaphragm height",
             "keystone_prerequisite": "per-finding head exists",
             "keystone_status": "NOT_INSPECTED", "search_mode": "C",
             "scores": {"mechanism_clarity": {"value": 4, "why": "x"},
                        "identifiability": {"value": 3, "why": "x"},
                        "interest": {"value": 4, "why": "x"},
                        "medical_relevance": {"value": 3, "why": "x"},
                        "clarity": {"value": 4, "why": "x"}}}
        (d / "fiction_candidates.json").write_text(json.dumps({"candidates": [c]}))
        (d / "fiction_seed.json").write_text('{"source": "random", "fiction_version": 2}')
        sc._merge_candidates(d, ["fiction"], 65)
        merged = json.loads((d / "candidates_all.json").read_text())
        self.assertEqual(len(merged["candidates"]), 1, "kernel was rejected again")
        self.assertEqual(merged["notes"].get("mode_c_score_missing"), 1)
        self.assertAlmostEqual(sc._mean_score(c), 3.60, places=2,
                               msg="Mode-C recompute should rank the scoreless card")

    def test_keystone_done_marker_makes_rerun_skip(self):
        self.assertEqual(self._sc().STAGE_DONE_MARKER["keystone"], "keystone_screen.md")

    def test_disagreeing_priority_score_falls_back_to_rubric(self):
        sc = self._sc()
        c = dict(GOLDEN_CANDIDATE)
        c["priority_score"] = 9.9  # lies about its own arithmetic
        s = sc._mean_score(c)
        self.assertLess(abs(s - 3.65), 0.3, f"rubric fallback not used: {s}")

    def test_merge_rejects_schema_invalid_candidate(self):
        try:
            import jsonschema  # noqa: F401
        except ImportError:
            self.skipTest("jsonschema not installed; validation is best-effort without it")
        sc = self._sc()
        d = self.repo / "ideas" / "scout-064"; d.mkdir()
        good = dict(GOLDEN_CANDIDATE); good["title"] = "valid one"
        bad = {"title": "no question or deliverable"}
        (d / "scout_candidates.json").write_text(json.dumps(
            {"candidates": [good, {"title": "x", "question": "long enough q?",
                                   "deliverable_sentence": 7}, bad]}))
        sc._merge_candidates(d, ["baseline"], 64)
        merged = json.loads((d / "candidates_all.json").read_text())
        self.assertEqual(len(merged["candidates"]), 1)
        self.assertTrue(merged["notes"].get("schema_rejected"))

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

    def test_debate_revise_verdict_triggers_auto_revise(self):
        self.make_cycle_outputs("scout-009", ["NOVEL_VERIFIED"])
        (self.repo / "orchestrator" / "state.json").write_text(
            json.dumps({"next_scout": 10, "selected_idea": 1}) + "\n")
        self.commit()
        # fake debate summary emits REVISE via consensus json in cycle_auto?
        # cycle_auto writes plain consensus; append a REVISE block via a
        # post-consensus hook: easiest is to pre-write the summary the fake
        # will overwrite -- instead patch fake consensus to include REVISE.
        r = self.scout("pipeline", "--top", "1", action="cycle_auto",
                       FAKE_CONSENSUS_VERDICT="REVISE")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("auto-revising card", r.stdout)
        e = json.loads((self.repo / "ledger.jsonl").read_text().splitlines()[-2] if False else "{}") if False else None
        rows = {}
        for ln in (self.repo / "ledger.jsonl").read_text().splitlines():
            rec = json.loads(ln)
            rows.setdefault(rec["ledger_id"], {}).update({k: v for k, v in rec.items() if v is not None})
        self.assertTrue(rows["idea-002"].get("card_synced"),
                        "auto-revise did not mark the card synced")

    def test_revise_debt_batch_finds_pre_automation_revises(self):
        # idea 001 has a consensus with REVISE but no card_synced flag
        (self.repo / "ideas" / "001" / "consensus.md").write_text(
            "# s\n\n## Recommendation\n\n**REVISE.** Update the card.\n")
        self.commit()
        r = self.scout("pipeline", "--revise-debt", action="cycle_auto")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("Revise debt: 001", r.stdout)
        rows = {}
        for ln in (self.repo / "ledger.jsonl").read_text().splitlines():
            rec = json.loads(ln)
            rows.setdefault(rec["ledger_id"], {}).update({k: v for k, v in rec.items() if v is not None})
        self.assertTrue(rows.get("idea-001", {}).get("card_synced"))
        r2 = self.scout("pipeline", "--revise-debt", action="cycle_auto")
        self.assertIn("No revise debt", r2.stdout)

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
            {"title": "revival", "question": "is the model using the fixture signal?", "deliverable_sentence": "the model is using revived signal", "keystone_prerequisite": "the fixture asset exists", "keystone_status": "NOT_INSPECTED", "priority_score": 3.0, "scores": {"interest": {"value": 3, "why": "fx"}}, "parent_ids": ["idea-012"]}]}))
        (self.repo / "orchestrator" / "state.json").write_text(json.dumps(
            {"next_scout": 43, "selected_idea": 1,
             "cycle": {"scout": 42, "tracks": ["baseline"], "stages": {}}}) + "\n")
        import importlib, scout as sc2
        sc2 = self._sc()
        sc2._merge_candidates(d, ["baseline"], 42)
        e = sc2.ledger_mod.load()["scout-042-c01"]
        self.assertEqual(e.get("parent_ids"), ["idea-012"])


class TestLibrarian(Harness):
    def setUp(self):
        super().setUp()
        self.make_hermetic()

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
        self.assertIn("NO_DUPLICATE_FOUND_HIGH_CONFIDENCE", recs,
                      "verdict update not applied (legacy names must normalize to calibrated vocabulary)")
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


class TestKeystoneScreen(Harness):
    def setUp(self):
        super().setUp()
        self.make_hermetic(wipe_idea_dirs=True)

    def test_keystone_kill_stops_pipeline_early(self):
        self.make_cycle_outputs("scout-009", ["NOVEL_VERIFIED"])
        (self.repo / "orchestrator" / "state.json").write_text(
            json.dumps({"next_scout": 10, "selected_idea": 1}) + "\n")
        self.commit()
        r = self.scout("pipeline", "--top", "1", action="cycle_auto",
                       FAKE_KEYSTONE_VERDICT="KILL")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("killed at keystone screen", r.stdout)
        d = self.repo / "ideas" / "002"
        self.assertTrue((d / "keystone_screen.md").exists())
        self.assertFalse((d / "critique.md").exists(),
                         "critique ran despite keystone kill")
        rows = {}
        for ln in (self.repo / "ledger.jsonl").read_text().splitlines():
            rec = json.loads(ln)
            rows.setdefault(rec["ledger_id"], {}).update(
                {k: v for k, v in rec.items() if v is not None})
        e = rows["idea-002"]
        self.assertEqual(e["status"], "REJECTED")
        self.assertEqual(e["death_stage"], "keystone")
        self.assertEqual(e["kill_code"], "DATA_ACCESS")
        self.assertIn("quoted line", e.get("keystone_evidence", ""))


class TestProbeBuild(Harness):
    def setUp(self):
        super().setUp()
        self.make_hermetic()

    def _arm(self):
        d = self.repo / "ideas" / "001"
        (d / "feasibility.md").write_text("# memo\ngoal\n")
        (d / "probe_contract.yaml").write_text("idea_id: '001'\nprimary_metric: 'x'\n")
        (d / "HUMAN_APPROVED_PROBE").write_text("approved\n")
        self.commit()

    def test_probe_build_generates_reviews_and_approves(self):
        self._arm()
        r = self.scout("probe-build", "1", action="cycle_auto")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("APPROVED", r.stdout)
        self.assertTrue((self.repo / "probes" / "001" / "run.py").exists())
        self.assertTrue((self.repo / "ideas" / "001" / "probe_review.md").exists())
        self.assertTrue((self.repo / "probes" / "001" / "verification.json").exists(),
                        "verify-probe did not run at the end of the loop")

    def test_probe_build_resumes_existing_code_and_normalizes_dir(self):
        # Real incident: generator wrote probes/idea-004/, artifact check
        # failed post-generation pre-commit. Rerun must normalize the dir and
        # review the existing code instead of regenerating.
        self._arm()
        alias = self.repo / "probes" / "idea-001"
        alias.mkdir(parents=True)
        (alias / "run.py").write_text(
            "import argparse\nap = argparse.ArgumentParser()\n"
            "ap.add_argument('--smoke', action='store_true')  # only the short flag: exercises verify fallback\n"
            "ap.parse_args()\nprint('recovered probe')\n")
        (alias / "README.md").write_text("# probe\n")
        self.commit()
        r = self.scout("probe-build", "1", action="cycle_auto")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("Normalized", r.stdout)
        self.assertIn("skipping generation", r.stdout)
        self.assertIn("recovered probe",
                      (self.repo / "probes" / "001" / "run.py").read_text())
        self.assertTrue((self.repo / "probes" / "001" / "verification.json").exists())

    def test_probe_build_blocked_without_human_gate(self):
        d = self.repo / "ideas" / "001"
        (d / "feasibility.md").write_text("# memo\n")
        (d / "probe_contract.yaml").write_text("idea_id: '001'\n")
        self.commit()
        r = self.scout("probe-build", "1", action="cycle_auto")
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("approve-probe first", r.stdout + r.stderr)


class TestActioner(Harness):
    def setUp(self):
        super().setUp()
        self.make_hermetic()

    def test_state_collection_and_brief_publication(self):
        # a paused idea with consensus + a live one; state file must carry both facts
        (self.repo / "ideas" / "001" / "consensus.md").write_text(
            "# s\n\n## Recommendation\n\n**PAUSE.** Await the widget.\n")
        self.commit()
        r = self.scout("actioner", action="cycle_auto")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        d = self.repo / "ideas" / "actioner-001"
        state = (d / "action_state.md").read_text()
        self.assertIn("idea-001", state)
        self.assertIn("Await the widget", state)
        self.assertIn("Backlog", state)
        self.assertTrue((self.repo / "evidence" / "actions.md").exists(),
                        "brief not published to evidence/")
        self.assertIn("first brief; no persistence claims", state,
                      "first-brief marker missing from state")

    def test_previous_brief_feeds_next_state(self):
        (self.repo / "evidence" / "actions.md").write_text(
            "## Decisions waiting on the human\n- PREVBRIEFMARKER item\n")
        self.commit()
        r = self.scout("actioner", action="cycle_auto")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        state = (self.repo / "ideas" / "actioner-001" / "action_state.md").read_text()
        self.assertIn("PREVBRIEFMARKER", state, "previous brief not fed into state")

    def test_improve_flag_reaches_prompt(self):
        self.commit()
        r = self.scout("actioner", "--improve", action="cycle_auto")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        prompt = (self.repo / "ideas" / "actioner-001" / "prompt_actioner.md").read_text()
        self.assertIn("IMPROVEMENT MODE ENABLED", prompt)
        self.assertIn("NEVER propose changes to .github/workflows/", prompt)


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
            {"title": "fiction fixture", "question": "is the model using the fixture signal?", "deliverable_sentence": "the model is using fiction signal", "keystone_prerequisite": "the fixture asset exists", "keystone_status": "NOT_INSPECTED", "priority_score": 3.0, "scores": {"interest": {"value": 3, "why": "fx"}}, "track": "fiction", "keystone_status": "INSPECTED_TRUE"}]}))
        (d / "fiction_seed.json").write_text('{"source": "human", "concepts": ["a","b"]}')
        sc._merge_candidates(d, ["fiction"], 60)
        merged = json.loads((d / "candidates_all.json").read_text())
        self.assertEqual(merged["candidates"][0]["keystone_status"], "NOT_INSPECTED")
        e = sc.ledger_mod.load()["scout-060-c01"]
        self.assertEqual(e.get("seed_source"), "human")

    def test_merge_filters_titleless_stubs(self):
        sc = self._sc()
        d = self.repo / "ideas" / "scout-061"; d.mkdir()
        (d / "wide_candidates.json").write_text(json.dumps({"candidates": [
            {"title": "real one", "question": "is the model using the fixture signal?", "deliverable_sentence": "the model is using wide signal", "keystone_prerequisite": "the fixture asset exists", "keystone_status": "NOT_INSPECTED", "priority_score": 3.0, "scores": {"interest": {"value": 3, "why": "fx"}}, "track": "wide"},
            {"question": "dropped: too vague"},
            {"title": "", "question": "", "note": "stub"}]}))
        sc._merge_candidates(d, ["wide"], 61)
        merged = json.loads((d / "candidates_all.json").read_text())
        self.assertEqual(len(merged["candidates"]), 1)
        self.assertEqual(merged["notes"].get("wide_skipped_stubs"), 2)
        rows = [k for k in sc.ledger_mod.load() if k.startswith("scout-061")]
        self.assertEqual(rows, ["scout-061-c01"], "stub reached the ledger")

    def test_audit_parser_handles_drifted_table_formats(self):
        # Real cycle-007 drift: descriptive cells, extra track column, W-numbering.
        sc = self._sc()
        d = self.repo / "ideas" / "scout-062"; d.mkdir()
        cands = [{"title": f"b{i}", "question": "is the model using the fixture signal?", "deliverable_sentence": "the model is using s", "track": "baseline"} for i in range(3)]
        cands += [{"title": "w1", "question": "is the model using the fixture signal?", "deliverable_sentence": "the model is using s", "track": "wide"}]
        (d / "candidates_all.json").write_text(json.dumps({"candidates": cands}))
        (d / "novelty_audit.md").write_text(
            "# audit\n\n| Candidate | Track | Verdict | Why |\n|---|---|---|---|\n"
            "| C1 — long descriptive name | baseline (A) | NOVEL_VERIFIED | BLIND_SPOT |\n"
            "| C2 — another | baseline | `INCREMENTAL` | X |\n"
            "| C3 — third | baseline | NOVEL_UNVERIFIED | X |\n"
            "| W1 — wide one | wide | NOVEL_VERIFIED | NEW_CAPABILITY |\n")
        v = sc._audit_verdicts(d)
        self.assertEqual(v, {1: "NOVEL_VERIFIED", 2: "INCREMENTAL",
                             3: "NOVEL_UNVERIFIED", 4: "NOVEL_VERIFIED"},
                         f"parser returned {v}")

    def test_seed_v2_has_model_prop_and_version(self):
        sc = self._sc()
        s = sc.seed_draw()
        self.assertEqual(s["fiction_version"], 2)
        self.assertIsInstance(s["dataset"], dict)
        self.assertIn("name", s["dataset"])
        self.assertIsInstance(s.get("model"), dict)
        self.assertIn("name", s["model"])

    def test_adjacent_question_banked_but_not_in_backlog(self):
        sc = self._sc()
        d = self.repo / "ideas" / "scout-063"; d.mkdir()
        (d / "fiction_seed.json").write_text('{"source": "random", "fiction_version": 2}')
        (d / "fiction_candidates.json").write_text(json.dumps(
            {"candidates": [], "no_testable_kernel": "nope",
             "adjacent_question": "does automated caliber periodicity on EyePACS track DR grade?"}))
        sc._merge_candidates(d, ["fiction"], 63)
        e = sc.ledger_mod.load().get("scout-063-fadj")
        self.assertIsNotNone(e, "near-miss not banked")
        self.assertEqual(e["status"], "PAUSED")
        self.assertEqual(e["fiction_version"], 2)
        ids = [f"{s:03d}-c{c}" for s, c, _ in sc._ranked_backlog()]
        self.assertTrue(all("063" not in i for i in ids), "near-miss leaked into backlog")

    def test_debate_summary_prompt_carries_taxonomy(self):
        sc = self._sc()
        codes = sc._taxonomy_block()
        self.assertIn("IDENTIFIABILITY_FAILURE", codes)
        self.assertIn("USE_VS_ASSOCIATION", codes)

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
    def setUp(self):
        super().setUp()
        self.make_hermetic(wipe_idea_dirs=True)

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


class TestSchemaNormalization(unittest.TestCase):
    """P0.1 regression tests on the REAL cycle-012 output that failed merge.

    The fixture is the verbatim production file (all five candidates emit
    scores.<dim>.score instead of .value; two emit keystone_evidence:
    null). Fabricated fixtures encoded stale assumptions and masked the
    scoring bug for weeks; this one is the actual drift, frozen. The
    schema is deliberately strict: these tests assert BOTH directions --
    known aliases normalize and validate, unknown shapes still fail."""

    FIXTURE = REPO / "tests" / "fixtures" / "scout012_production_candidates.json"

    def setUp(self):
        sys.path.insert(0, str(REPO))
        import scout as sc
        self.sc = sc
        # Harness tests repoint the shared module's ROOT at their temp
        # repos and do not restore it; pin it so this class is
        # order-independent regardless of what ran before.
        sc.ROOT = REPO
        self.cards = json.loads(self.FIXTURE.read_text())["candidates"]
        self.assertEqual(len(self.cards), 5, "fixture must hold the five real cards")

    def test_production_cards_fail_schema_before_normalization(self):
        errs = [self.sc._validate_card(dict(c)) for c in
                (json.loads(json.dumps(c)) for c in self.cards)]
        self.assertTrue(all(errs), f"expected every raw card to fail; got {errs}")

    def test_normalization_makes_every_production_card_valid(self):
        for c in (json.loads(json.dumps(c)) for c in self.cards):
            fixes = self.sc._normalize_candidate(c)
            self.assertTrue(fixes, "every drifted card should report fixes")
            err = self.sc._validate_card(c)
            self.assertIsNone(err, f"{c.get('id')}: still invalid after "
                                   f"normalization: {err}")

    def test_score_alias_is_renamed_not_duplicated(self):
        c = json.loads(json.dumps(self.cards[0]))
        self.sc._normalize_candidate(c)
        for k, v in c["scores"].items():
            self.assertIn("value", v, f"scores.{k} missing value")
            self.assertNotIn("score", v, f"scores.{k} retains legacy key")

    def test_null_keystone_evidence_dropped_enabling_honest_demotion(self):
        nulls = [c for c in self.cards if c.get("keystone_evidence") is None
                 and "keystone_evidence" in c]
        self.assertEqual(len(nulls), 2, "fixture should hold the two null cards")
        for c in (json.loads(json.dumps(c)) for c in nulls):
            claimed_true = c.get("keystone_status") == "INSPECTED_TRUE"
            fixes = self.sc._normalize_candidate(c)
            self.assertIn("keystone_evidence: null->absent", fixes)
            self.assertNotIn("keystone_evidence", c)
            if claimed_true:
                # The merge loop's existing guard now demotes honestly
                # instead of validation dying on the null.
                self.assertFalse(c.get("keystone_evidence"))

    def test_schema_is_not_loosened_by_normalization(self):
        c = json.loads(json.dumps(self.cards[0]))
        c["scores"]["clarity"] = {"grade": 4, "why": "unknown alias"}
        self.sc._normalize_candidate(c)
        self.assertIsNotNone(self.sc._validate_card(c),
                             "an unknown score alias must still fail")
        c2 = json.loads(json.dumps(self.cards[0]))
        c2["scores"]["clarity"] = {"score": 9, "why": "out of range"}
        self.sc._normalize_candidate(c2)
        self.assertIsNotNone(self.sc._validate_card(c2),
                             "normalized but out-of-range value must still fail")
        c3 = json.loads(json.dumps(self.cards[0]))
        del c3["deliverable_sentence"]
        self.sc._normalize_candidate(c3)
        self.assertIsNotNone(self.sc._validate_card(c3),
                             "missing required field must still fail")

    def test_mean_score_recovers_after_normalization(self):
        c = json.loads(json.dumps(self.cards[0]))
        before = self.sc._mean_score(c)
        self.sc._normalize_candidate(c)
        after = self.sc._mean_score(c)
        self.assertGreater(after, 0.0, "ranking must see normalized values")
        self.assertGreaterEqual(after, before)


if __name__ == "__main__":
    unittest.main(verbosity=2)
