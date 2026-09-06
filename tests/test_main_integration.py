import unittest
from pathlib import Path
from scripts.verify_main_integration import workflow_policy, verify

class MainIntegrationTests(unittest.TestCase):
    def test_controls_are_explicit_and_artifact_only_on_main(self):
        r=workflow_policy(Path(__file__).resolve().parents[1])
        self.assertEqual(r['on_main'],'EXPLICIT_DISPATCH')
        self.assertEqual(r['destination'],'actions-artifact')
        self.assertFalse(r['git_publication'])

    def test_branch_names_are_not_review_pins(self):
        with self.assertRaisesRegex(ValueError,'full main and pilot pins'):
            verify(Path(__file__).resolve().parents[1],'main','astra/autonomous-isles-pilot')
