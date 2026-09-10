"""Authority retargeting, attribution, review, policy and reversible-state checks."""
import json
from pathlib import Path
import shutil
import tempfile
import unittest

from orchestrator import scientific_authority as authority

SOURCE = Path(__file__).resolve().parents[1]


class ScientificAuthorityTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        for name in (authority.POLICY_PATH, 'docs/operations/SCIENTIFIC_DELEGATION_20260909.md'):
            dest = self.root / name
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(SOURCE / name, dest)
        self.directory = self.root / 'decision'
        self.directory.mkdir()
        self.bindings = {'contract_blob': 'a' * 40, 'input_sha256': 'b' * 64}
        self.kw = dict(action='accept_interpretation', subject='idea:047', bindings=self.bindings)
        context = authority.decision_context(self.root, **self.kw)
        self.judgment = {'context_sha256': authority.digest(authority.encoded(context)),
                         'decision': 'APPLY', 'rationale': 'Reviewed result supports completing this study.',
                         'transition': {'from': 'ACTIVE', 'to': 'PAUSED'},
                         'reconsideration': 'Reconsider with new evidence or a distinct linked question.'}
        self.author = {'run_id': 'author000001', 'family_effective': 'codex',
                       'model_used': 'gpt-6-astra', 'exit_class': 'ok'}
        self.reviewer = {'run_id': 'review000001', 'family_effective': 'claude',
                         'model_used': 'claude-fable-5', 'exit_class': 'ok'}

    def write(self, name, value):
        (self.directory / name).write_bytes(authority.encoded(value) + b'\n')

    def create(self):
        self.write('judgment.json', self.judgment)
        self.write('review.json', {'verdict': 'APPROVE', 'rationale': 'Evidence and limits support this disposition.',
                   'judgment_sha256': authority.digest((self.directory / 'judgment.json').read_bytes())})
        return authority.seal(self.root, self.directory, **self.kw,
                              author=self.author, reviewer=self.reviewer)

    def verify(self, **kw):
        return authority.verify(self.root, self.directory / 'decision.json', **(self.kw | kw))

    def mutate_record(self, update):
        d = json.loads((self.directory / 'decision.json').read_text())
        update(d)
        self.write('decision.json', d)

    def test_valid_model_disposition_is_attributed_without_human_marker(self):
        result = self.create()
        self.assertEqual(result['actor']['session_id'], self.author['run_id'])
        self.assertEqual(result['actor']['session_id_source'], 'system_stage_run_id')
        self.assertEqual(self.verify()['_decision_sha256'], result['_decision_sha256'])
        self.assertFalse(list(self.root.rglob('HUMAN_APPROVED_PROBE')))
        self.assertNotIn('operator ratified', (self.directory / 'decision.json').read_text())
        for name in ('decision.json', 'decision-author.provenance.json', 'decision-reviewer.provenance.json'):
            self.assertEqual((self.directory / name).stat().st_mode & 0o777, 0o600)

    def test_retargeting_original_decision_to_other_input_or_action_fails(self):
        self.create()
        for key, value in [('subject', 'idea:048'), ('action', 'approve_probe'),
                           ('bindings', {'contract_blob': 'c' * 40})]:
            original = (self.directory / 'decision.json').read_bytes()
            with self.subTest(key=key):
                self.mutate_record(lambda d: d.update({key: value}))
                with self.assertRaisesRegex(ValueError, 'CONTEXT_CHANGED'):
                    self.verify(**{key: value})
            (self.directory / 'decision.json').write_bytes(original)

    def test_changed_model_judgment_cannot_reuse_review(self):
        self.create()
        self.judgment['rationale'] = 'Different judgment'
        self.write('judgment.json', self.judgment)
        self.mutate_record(lambda d: d.update(rationale=self.judgment['rationale'],
                           judgment={'path': 'judgment.json', 'sha256': authority.digest((self.directory / 'judgment.json').read_bytes())}))
        with self.assertRaisesRegex(ValueError, 'JUDGMENT_REVIEW_REQUIRED'):
            self.verify()

    def test_original_stage_actor_cannot_be_renamed(self):
        self.create()
        self.mutate_record(lambda d: d['actor'].update(model='another-model', session_id='fabricated001'))
        with self.assertRaisesRegex(ValueError, 'ACTOR_MISMATCH'):
            self.verify()

    def test_same_family_or_failed_reviewer_refuses(self):
        for update in ({'family_effective': 'codex'}, {'exit_class': 'timeout'}):
            with self.subTest(update=update):
                for path in self.directory.iterdir():
                    path.unlink()
                self.reviewer.update(update)
                with self.assertRaises(ValueError):
                    self.create()
                self.reviewer.update(family_effective='claude', exit_class='ok')

    def test_model_deferral_is_recorded_but_cannot_authorize_execution(self):
        self.judgment['decision'] = 'DEFER'
        self.create()
        with self.assertRaisesRegex(ValueError, 'DEFERRED'):
            self.verify()
        self.assertEqual(self.verify(allow_deferred=True)['decision'], 'DEFER')

    def test_permanent_rejection_and_stale_transition_refuse(self):
        self.judgment['transition']['to'] = 'REJECTED'
        with self.assertRaisesRegex(ValueError, 'TERMINAL_REJECTION'):
            self.create()

    def test_expected_prior_state_cannot_be_ignored(self):
        self.create()
        with self.assertRaisesRegex(ValueError, 'TRANSITION'):
            self.verify(expected_transition={'from': 'HUMAN_STOPPED', 'to': 'ACTIVE'})

    def test_reserved_grants_and_human_signature_fields_refuse(self):
        self.create()
        for key in ('override_human_stop', 'reserved_cohort_access', 'new_paid_resources', 'limiter_reset'):
            original = (self.directory / 'decision.json').read_bytes()
            with self.subTest(key=key):
                self.mutate_record(lambda d: d['scope'].update({key: True}))
                with self.assertRaises(ValueError):
                    self.verify()
            (self.directory / 'decision.json').write_bytes(original)
        self.mutate_record(lambda d: d.update(human_approved=True))
        with self.assertRaises(ValueError):
            self.verify()

    def test_current_policy_and_exact_user_direction_cannot_drift(self):
        self.create()
        path = self.root / 'docs/operations/SCIENTIFIC_DELEGATION_20260909.md'
        path.write_text('An invented broader grant')
        with self.assertRaisesRegex(ValueError, 'DELEGATION_REQUIRED'):
            self.verify()

    def test_repeated_seal_preserves_original_and_refuses_overwrite(self):
        self.create()
        original = (self.directory / 'decision.json').read_bytes()
        with self.assertRaises(FileExistsError):
            authority.seal(self.root, self.directory, **self.kw, author=self.author, reviewer=self.reviewer)
        self.assertEqual((self.directory / 'decision.json').read_bytes(), original)


if __name__ == '__main__':
    unittest.main()
