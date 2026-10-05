"""No model calls. The genuine report is operator-private and hash-bound externally."""
import hashlib
import json
import os
from pathlib import Path
import unittest
from orchestrator.manual_driver import CATEGORIES, validate_review

GENUINE_SHA = '4a8f8391a34fac210ecc1c8e612b78bdbd6d885469012fd3425b337e2c42b289'

class NegatedReviewMarkers(unittest.TestCase):
    def test_exact_call6_original(self):
        path=os.environ.get('CALL6_REVIEW_FIXTURE')
        if not path:self.skipTest('Private genuine call6 fixture required; focused release check must set it')
        p=Path(path);raw=p.read_bytes()
        self.assertEqual(hashlib.sha256(raw).hexdigest(),GENUINE_SHA)
        self.assertEqual(validate_review(json.loads(raw)),[])
        self.assertEqual(p.read_bytes(),raw)

    def test_explicit_negative_sentences(self):
        for category in CATEGORIES:
            for suffix in ['.', ' in this review.', ' in the candidate.', ' in the stock-take, which performs no execution and makes no new acceptance claim.']:
                with self.subTest(category=category,suffix=suffix):
                    self.assertEqual(validate_review({'verdict':'APPROVE','rationale':'Prior evidence inspected. No BLOCKER['+category+'] is present'+suffix}),[])
        self.assertEqual(validate_review({'verdict':'APPROVE','rationale':'No BLOCKER['+', '.join(CATEGORIES)+'] is present.'}),[])

    def test_real_marker_blocks_approve_and_requires_revise(self):
        for category in CATEGORIES:
            with self.subTest(category=category):
                rationale='BLOCKER['+category+'] The issue remains unresolved.'
                with self.assertRaisesRegex(ValueError,'^REVIEW_CATEGORY_OR_VERDICT_CONFLICT$'):
                    validate_review({'verdict':'APPROVE','rationale':rationale})
                self.assertEqual(validate_review({'verdict':'REVISE','rationale':rationale}),[category])

    def test_ambiguous_quoted_conditional_and_mixed_refuse(self):
        texts=[
            'No BLOCKER[budget] is present?',
            'Perhaps no BLOCKER[budget] is present.',
            'If no BLOCKER[budget] is present, proceed.',
            'The author says No BLOCKER[budget] is present.',
            '"No BLOCKER[budget] is present."',
            'No BLOCKER[budget] is present unless the estimate is wrong.',
            'No BLOCKER[budget] is present, but spending is unresolved.',
            'No BLOCKER[budget] is present in the review except one issue.',
            'No BLOCKER[budget] is present in the review or might be present.',
            'No BLOCKER[budget] is present. BLOCKER[privacy/secret] remains.',
            'BLOCKER[budget] remains. No BLOCKER[privacy/secret] is present.',
            'No BLOCKER[budget] is present but BLOCKER[privacy/secret] is.',
            'No BLOCKER[budget] may be present.',
            'No BLOCKER[unknown] is present.',
            'No BLOCKER[budget, unknown] is present.',
            'No BLOCKER[budget, budget] is present.',
            'No BLOCKER[budget] is present (not verified).',
            'No BLOCKER[budget] is present in a hypothetical candidate.',
        ]
        for text in texts:
            with self.subTest(text=text),self.assertRaisesRegex(ValueError,'^REVIEW_CATEGORY_OR_VERDICT_CONFLICT$'):
                validate_review({'verdict':'APPROVE','rationale':text})

    def test_other_acceptance_rules_unchanged(self):
        self.assertEqual(validate_review({'verdict':'APPROVE','rationale':'All inspected checks pass.'}),[])
        for review in [{'verdict':'REVISE','rationale':'No BLOCKER[budget] is present.'}, {'verdict':'REVISE','rationale':'Advisory only.'}, {'verdict':'REVISE','rationale':'BLOCKER[unknown] finding'}]:
            with self.subTest(review=review),self.assertRaisesRegex(ValueError,'^REVIEW_CATEGORY_OR_VERDICT_CONFLICT$'):validate_review(review)
        for review in [{'verdict':'ACCEPT','rationale':'fine'}, {'verdict':'APPROVE','rationale':''}, {'verdict':'APPROVE','rationale':1}, {'verdict':'APPROVE','rationale':'fine','extra':True}]:
            with self.subTest(review=review),self.assertRaisesRegex(ValueError,'^INVALID_REVIEW$'):validate_review(review)

if __name__=='__main__':unittest.main(verbosity=2)
