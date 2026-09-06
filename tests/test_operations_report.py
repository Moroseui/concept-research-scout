import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor

from orchestrator.operations_report import Queue, finalize


class OperationsReportTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)/'private'
        self.row = {'job_id': 'fixture', 'status': 'COMPLETE', 'source': 'a'*40,
                    'kind': 'synthetic', 'backend': 'linux', 'wall_seconds': 1.2}

    def tearDown(self):
        self.temp.cleanup()

    def report(self, rows=None, **kw):
        return finalize(self.root, 'a'*40, '2026-09-06', [self.row] if rows is None else rows, **kw)

    def test_roundtrip_explicit_synthetic_review_fixture_and_no_recursion(self):
        report = self.report(); queue = Queue(self.root)
        self.assertEqual(report['status'], 'QUEUED')
        body = (self.root/(report['id']+'.md')).read_text()
        self.assertIn('| Job | Status | Backend |', body)
        self.assertIn('1 completed; 0 failed; 0 blocked', body)
        self.assertIn('no patient experiment', body)
        self.assertNotIn('```json', body)
        evidence = list(self.root.glob('*.receipts.json'))
        self.assertEqual(len(evidence), 1)
        self.assertIsNone(json.loads(evidence[0].read_text())[0]['cpu_seconds'])
        self.assertIn(hashlib.sha256(evidence[0].read_bytes()).hexdigest(), body)
        claim = queue.claim(report['id'])
        review = 'Synthetic test adapter output, not an actual Claude execution.'
        receipt = {'family': 'claude', 'model': 'fixture-model', 'source': 'a'*40,
                   'report_sha256': report['id'], 'review_sha256': hashlib.sha256(review.encode()).hexdigest(),
                   'execution_receipt_sha256': 'b'*64, 'session_id': 'synthetic-only', 'status': 'COMPLETE'}
        queue.attach(report['id'], claim['attempt_id'], review, receipt)
        queue.disposition(report['id'], 'Synthetic disposition fixture.')
        self.assertIsNone(queue.claim(report['id']))
        self.assertEqual(self.report()['status'], 'REVIEWED')
        self.assertEqual(queue.db.execute('SELECT count(*) FROM reviews').fetchone()[0], 1)

    def test_rejected_input_leaves_no_output(self):
        for row in ({**self.row, 'raw_console': 'forbidden'},
                    {**self.row, 'reason': 'sub-stroke1234'},
                    {**self.row, 'wall_seconds': float('nan')},
                    {**self.row, 'job_id': '../outside'}):
            with self.assertRaises(ValueError): self.report([row])
            self.assertFalse(self.root.exists())

    def test_duplicate_claim_restart_unavailable_and_cap(self):
        report = self.report(); queue = Queue(self.root)
        for n in range(3):
            claim = queue.claim(report['id'])
            self.assertEqual(claim['attempts'], n+1)
            self.assertIsNone(Queue(self.root).claim(report['id']))
            with self.assertRaises(ValueError): queue.unavailable(report['id'], 'stale', 'AUTH_REQUIRED')
            queue.unavailable(report['id'], claim['attempt_id'], 'AUTH_REQUIRED')
        self.assertIsNone(queue.claim(report['id']))
        self.assertEqual(queue.status(report['id'])['status'], 'NOT_REVIEWED')

    def test_amendment_preserves_original(self):
        original = self.report(); before = (self.root/(original['id']+'.md')).read_bytes()
        amendment = self.report([{**self.row, 'wall_seconds': 2}], amendment_of=original['id'])
        self.assertNotEqual(original['id'], amendment['id'])
        self.assertEqual((self.root/(original['id']+'.md')).read_bytes(), before)
        self.assertEqual(self.report()['id'], original['id'])
        self.assertEqual(len(list(self.root.glob('*.receipts.json'))), 2)

    def test_readable_failure_dependencies_and_missing_measurements(self):
        report = self.report([{**self.row, 'status': 'BLOCKED', 'reason': 'AUTH_REQUIRED',
                              'wall_seconds': None, 'kind': 'unknown'}])
        body = (self.root/(report['id']+'.md')).read_text()
        self.assertIn('0 completed; 0 failed; 1 blocked', body)
        self.assertIn('Recorded block or failure reasons: AUTH_REQUIRED.', body)
        self.assertIn('unavailable', body)
        self.assertIn('Scientific progress is not established', body)

    def test_report_tamper_refused_and_unsafe_review_not_written(self):
        report = self.report(); queue = Queue(self.root); claim = queue.claim(report['id'])
        with self.assertRaises(ValueError):
            queue.attach(report['id'], claim['attempt_id'], 'sub-stroke1234', {})
        self.assertFalse(list(self.root.glob('*.claude-review.*')))
        (self.root/(report['id']+'.md')).write_text('modified')
        with self.assertRaises(ValueError): self.report()

    def test_symlink_root_rejected(self):
        self.root.symlink_to(Path(self.temp.name), target_is_directory=True)
        with self.assertRaises(ValueError): self.report()

    def test_concurrent_claims_have_one_owner(self):
        report = self.report()
        with ThreadPoolExecutor(max_workers=8) as pool:
            claims = list(pool.map(lambda _: Queue(self.root).claim(report['id']), range(16)))
        self.assertEqual(sum(row is not None for row in claims), 1)
        self.assertEqual(Queue(self.root).status(report['id'])['attempts'], 1)

    def test_wrong_source_review_cannot_attach(self):
        report = self.report(); queue = Queue(self.root); claim = queue.claim(report['id'])
        review = 'Synthetic source binding rejection fixture.'
        receipt = {'family': 'claude', 'model': 'fixture-model', 'source': 'b'*40,
                   'report_sha256': report['id'], 'review_sha256': hashlib.sha256(review.encode()).hexdigest(),
                   'execution_receipt_sha256': 'b'*64, 'session_id': 'synthetic-only', 'status': 'COMPLETE'}
        with self.assertRaisesRegex(ValueError, 'REVIEW_BINDING_MISMATCH'):
            queue.attach(report['id'], claim['attempt_id'], review, receipt)
        self.assertFalse(list(self.root.glob('*.claude-review.*')))


if __name__ == '__main__':
    unittest.main()
