import json
from pathlib import Path
import tempfile
import unittest
from scripts.pilot_tool_guard import guard
from scripts.efficiency_review import review


class ProfileTests(unittest.TestCase):
    def test_output_guard_fail_closed(self):
        for args in [{},{'includeOutputs':True},{'includeOutputs':'false'}]:
            self.assertEqual(guard({'tool_name':'mcp__colab-worker__get_cells','tool_input':args})['hookSpecificOutput']['permissionDecision'],'deny')
        self.assertEqual(guard({'tool_name':'mcp__colab-worker__get_cells','tool_input':{'includeOutputs':False}}),{})

    def test_efficiency_private_fields_never_copied(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'status.json';p.write_text(json.dumps({'status':'BLOCKED','wall_seconds':2,'secret':'synthetic-do-not-copy'}))
            result=review(Path(d),[p])
            self.assertNotIn('synthetic-do-not-copy',json.dumps(result))
            self.assertEqual(result['receipt_count'],1)
            self.assertEqual(result['mode'],'proposal_only')
