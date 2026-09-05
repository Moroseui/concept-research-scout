import unittest
from pathlib import Path
from unittest.mock import patch
import yaml
from scripts.workflow_boundary import verify


class WorkflowBoundaryTests(unittest.TestCase):
    def test_explicit_binding(self):
        with patch('subprocess.check_output',return_value='a'*40+'\n'):
            self.assertEqual(verify('.', 'a'*40,'astra/autonomous-isles-pilot')['status'],'BOUND_NOT_PUBLISHED')
            for source,dest in [('main','astra/autonomous-isles-pilot'),('a'*40,'main'),('b'*40,'astra/autonomous-isles-pilot')]:
                with self.assertRaises(ValueError):verify('.',source,dest)

    def test_every_model_workflow_fails_closed(self):
        for name in ['interpret','confer','actioner','scout-cycle','idea-pipeline','librarian']:
            text=(Path('.github/workflows')/(name+'.yml')).read_text()
            data=yaml.safe_load(text)
            job=next(iter(data['jobs'].values()))
            self.assertIn('PILOT_REMOTE_RESEARCH_ENABLED',job['if'])
            steps=job['steps'];names=[s.get('name') for s in steps]
            guard=steps[names.index('Campaign route required')]
            self.assertIn('exit 1',guard['run'])
            self.assertNotIn('secrets.',text)
            self.assertNotIn('git push',text)
            self.assertNotIn('git checkout main',text)
            self.assertNotIn('git pull',text)
