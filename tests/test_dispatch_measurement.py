import unittest
from scripts.measure_dispatch import measure

class MeasurementTests(unittest.TestCase):
    def test_complete_count_and_unresolved_attempt_timing(self):
        row={'id':1,'created_at':'2026-09-06T01:00:00Z','run_attempt':1,'head_branch':'main','path':'.github/workflows/confer.yml','event':'workflow_dispatch','conclusion':'success'}
        page={'total_count':1,'workflow_runs':[row]}
        self.assertEqual(measure([page],'2026-09-06T03:00:00Z')['recommended_n'],4)
        row['run_attempt']=2
        self.assertIsNone(measure([page],'2026-09-06T03:00:00Z')['recommended_n'])
        page['total_count']=2
        with self.assertRaisesRegex(ValueError,'incomplete'):measure([page],'2026-09-06T03:00:00Z')
