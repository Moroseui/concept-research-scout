import unittest
from unittest.mock import patch
from scripts.workflow_boundary import verify
from scripts.render_human_workflows import verify as controls
from pathlib import Path

class WorkflowBoundaryTests(unittest.TestCase):
    def test_explicit_binding(self):
        with patch('subprocess.check_output',return_value='a'*40+'\n'):
            self.assertEqual(verify('.', 'a'*40,'astra/autonomous-isles-pilot')['status'],'BOUND_NOT_PUBLISHED')
            for source,dest in [('main','astra/autonomous-isles-pilot'),('a'*40,'main'),('b'*40,'astra/autonomous-isles-pilot')]:
                with self.assertRaises(ValueError):verify('.',source,dest)

    def test_human_results_do_not_enable_git_publication(self):
        r=controls(Path(__file__).resolve().parents[1])
        self.assertFalse(r['git_publication']);self.assertFalse(r['patient_execution'])
