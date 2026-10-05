"""Conservative administrative finding/example distinction; no model calls."""
import json
import os
from pathlib import Path
import unittest
from orchestrator import autonomy_review as review

SHA='d24e368487e58f932bec804dbf0d7d6d7e86c28c2e1779dfaaaded27a8d89070'
MANIFEST={'source_sha':'a'*40,'runtime_sha256':'b'*64}


def report(body,verdict='APPROVE',declaration='None.'):
    return ('## Verdict: '+verdict+'\nsource_sha: '+MANIFEST['source_sha']+'\nruntime_sha256: '+MANIFEST['runtime_sha256']+'\npacket_sha256: '+review.sha(review.canonical(MANIFEST))+'\n\n## Blockers\n'+declaration+'\n\n## Findings\n'+body)


class QuotedExamples(unittest.TestCase):
    def test_genuine_saved_administrative_report_and_native_evidence(self):
        folder=os.environ.get('ADMIN_EXAMPLE_FIXTURE')
        if not folder:self.skipTest('Private exact native fixture required in focused release verification')
        folder=Path(folder);raw=(folder/'report.md').read_bytes();self.assertEqual(review.sha(raw),SHA)
        manifest=json.loads((folder/'packet-manifest.json').read_bytes())
        self.assertEqual(review.report_verdict(raw.decode(),manifest),'APPROVE')
        result=review.extract_result((folder/'native-stream.jsonl').read_text(),manifest,0)
        self.assertEqual(result['verdict'],'APPROVE');self.assertEqual(result['report'].encode(),raw)
        self.assertEqual((folder/'report.md').read_bytes(),raw)

    def test_corrected_qualification_preserves_originals_and_is_idempotent(self):
        import tempfile
        folder=os.environ.get('ADMIN_EXAMPLE_FIXTURE')
        if not folder:self.skipTest('Private exact native fixture required in focused release verification')
        folder=Path(folder);before=review.inventory(folder);row=json.loads((folder/'original-row.json').read_text());frozen=review.canonical(row)
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);decision=root/'decision.txt';proposal=root/'proposal.md';binding=root/'binding.json'
            decision.write_text('SYNTHETIC TEST AUTHORITY ONLY: requalify saved format refusal without editing originals.')
            proposal.write_text('SYNTHETIC TEST: bounded quoted examples, no new call or charge.')
            binding.write_text(json.dumps({'operator_original_sha256':review.sha(decision.read_bytes()),'proposal_sha256':review.sha(proposal.read_bytes())}))
            authority={'decision':decision,'proposal':proposal,'binding':binding};out=root/'corrected.json'
            first=review.corrected_qualification(folder,row,authority,out)
            self.assertEqual(first['verdict'],'APPROVE');self.assertEqual(first['report_sha256'],SHA)
            self.assertEqual(first['additional_calls'],0);self.assertEqual(first['additional_charges'],0)
            self.assertEqual(review.corrected_qualification(folder,row,authority,out),first)
            self.assertEqual(review.canonical(row),frozen);self.assertEqual(review.inventory(folder),before)

    def test_delimited_rejected_test_examples(self):
        for literal in ['"BLOCKER[budget] excessive cost"', "'BLOCKER[budget] excessive cost'", '`BLOCKER[budget] excessive cost`', '\u201cBLOCKER[budget] excessive cost\u201d', '```text\nBLOCKER[budget] excessive cost\n```']:
            with self.subTest(literal=literal):
                body='Negative test examples: '+literal+'. All examples must be rejected.'
                # A marker at the beginning of a code-fence line still triggers
                # the existing positive-record rule. Never relax that rule.
                if '\nBLOCKER[' in literal:
                    with self.assertRaises(ValueError):review.report_verdict(report(body),MANIFEST)
                else:self.assertEqual(review.report_verdict(report(body),MANIFEST),'APPROVE')

    def test_positive_mixed_ambiguous_and_quoted_real_findings_refuse(self):
        bodies=[
            'BLOCKER[budget] B1: overspend remains.',
            '`BLOCKER[budget]` is an unresolved problem.',
            '"BLOCKER[budget] overspend remains."',
            'Negative test examples: "BLOCKER[budget] overspend".',
            'Negative test examples: "BLOCKER[budget] overspend". All examples must be rejected. However, the current issue persists.',
            'Negative test examples: "BLOCKER[budget] overspend". All examples might be rejected.',
            'Negative test examples: "BLOCKER[budget] overspend". All examples must be rejected. BLOCKER[privacy/secret] leak.',
            'Negative test examples: BLOCKER[budget] overspend. All examples must be rejected.',
            'Negative test examples: "BLOCKER[budget] overspend. All examples must be rejected.',
            'Negative test examples: `BLOCKER[budget] overspend. All examples must be rejected.',
            'Example: "BLOCKER[budget] overspend". All fail.',
            'Tests show "BLOCKER[budget] overspend" and reject the candidate.',
            'Negative test examples: "BLOCKER[budget] overspend". All fail. A real blocker remains.',
            'Negative test examples: "BLOCKER[budget] overspend". All fail.\n\n## Advisories\n`BLOCKER[budget]` is unresolved.',
        ]
        for body in bodies:
            with self.subTest(body=body),self.assertRaisesRegex(ValueError,'^REVIEW_VERDICT_CONFLICT$'):
                review.report_verdict(report(body),MANIFEST)

    def test_exact_approval_none_and_bindings_are_mandatory(self):
        body='Rejected test cases: `BLOCKER[budget] example`. All cases must be refused.'
        good=report(body)
        for bad in [good.replace('source_sha: '+'a'*40,'source_sha: '+'c'*40),good.replace('## Verdict: APPROVE','## Verdict: APPROVE\n## Verdict: APPROVE'),report(body,declaration='No findings.'),report(body,declaration='None.\nNegative test examples: "BLOCKER[budget]". All fail.'),report(body,verdict='CHANGES REQUIRED')]:
            with self.subTest(bad=bad),self.assertRaises(ValueError):review.report_verdict(bad,MANIFEST)
        real=report('Detail.',verdict='CHANGES REQUIRED',declaration='BLOCKER[budget] B1: actual finding')
        self.assertEqual(review.report_verdict(real,MANIFEST),'CHANGES REQUIRED')

    def test_syntax_only_references_and_actual_or_ambiguous_refusal(self):
        good=["The parser rejects the `BLOCKER[` token.", "Column-0 `BLOCKER[...]` always caught by findall.", "The prior `'BLOCKER[' in report` rejection is replaced."]
        for text in good:
            with self.subTest(text=text):self.assertEqual(review.report_verdict(report(text),MANIFEST),'APPROVE')
        bad=["An unresolved issue in the parser: `BLOCKER[...]`.", "The parser says `BLOCKER[...]` exists.", "The parser could hide `BLOCKER[...]`.", "The parser's `BLOCKER[...]` is unresolved.", "The parser's `BLOCKER[` is present.", "The parser may ignore `BLOCKER[...]`.", "The parser rejects `BLOCKER[budget]`.", "The parser rejects `BLOCKER[unknown]`.", "The parser rejects `BLOCKER[budget] excessive cost`.", "The parser discusses `BLOCKER[...]`. A real finding remains.", "`BLOCKER[...]` is unresolved.", "The parser rejects BLOCKER[...]."]
        for text in bad:
            with self.subTest(text=text),self.assertRaisesRegex(ValueError,'^REVIEW_VERDICT_CONFLICT$'):review.report_verdict(report(text),MANIFEST)

    def test_second_genuine_saved_administrative_report_and_native_evidence(self):
        folder=os.environ.get('ADMIN_SYNTAX_FIXTURE')
        if not folder:self.skipTest('Private second exact native fixture required in release verification')
        folder=Path(folder);raw=(folder/'report.md').read_bytes()
        self.assertEqual(review.sha(raw),'31fd46c9cc743db84090080852dd155a9b8017890b5f7c6969702a6d681bdfc8')
        manifest=json.loads((folder/'packet-manifest.json').read_bytes())
        self.assertEqual(review.report_verdict(raw.decode(),manifest),'APPROVE')
        result=review.extract_result((folder/'native-stream.jsonl').read_text(),manifest,0)
        self.assertEqual(result['verdict'],'APPROVE');self.assertEqual(result['report'].encode(),raw)

if __name__=='__main__':unittest.main(verbosity=2)
