import unittest
from orchestrator.pilot_jobs import classify


class DriverTests(unittest.TestCase):
    def test_never_promotes_worker_success_to_scientific_success(self):
        self.assertEqual(classify('acquisition',{'status':'COMPLETE','remote':{'status':'RUNNING'}}),'RUNNING')
        self.assertEqual(classify('dispatch',{'status':'COMPLETE','job_status':'DISPATCHED_NOT_YET_VALIDATED'}),'DISPATCHED')
        self.assertEqual(classify('patient',{'status':'COMPLETE'}),'FAILED')
        self.assertEqual(classify('dispatch',{'status':'COMPLETE','job_status':'RUNNING'}),'FAILED')
        self.assertEqual(classify('acquisition',{'status':'FAILED','remote':{'status':'VALIDATED'}}),'FAILED')
