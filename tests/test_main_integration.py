import unittest
import tempfile
import shutil
import yaml
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

    def test_deterministic_ci_boundaries_survive_controls_restoration(self):
        source = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            shutil.copytree(source / '.github', root / '.github')
            file = root / '.github/workflows/check.yml'
            original = file.read_text()
            for mutation in ['permissions', 'credentials', 'secrets', 'indexed_secret', 'whole_context', 'extra_step']:
                with self.subTest(mutation=mutation):
                    data = yaml.safe_load(original)
                    job = data['jobs']['basic']
                    if mutation == 'permissions':
                        job['permissions'] = {'contents': 'write'}
                    elif mutation == 'credentials':
                        job['steps'][0]['with']['persist-credentials'] = True
                    elif mutation == 'secrets':
                        job['env'] = {'KEY': '${{ secrets.ANY_KEY }}'}
                    elif mutation == 'indexed_secret':
                        job['env'] = {'KEY': "${{ secrets['ANY_KEY'] }}"}
                    elif mutation == 'whole_context':
                        job['env'] = {'KEY': '${{ toJSON(secrets) }}'}
                    else:
                        job['steps'].append({'run': 'echo unreviewed_step'})
                    file.write_text(yaml.safe_dump(data))
                    with self.assertRaises(ValueError):
                        workflow_policy(root)
