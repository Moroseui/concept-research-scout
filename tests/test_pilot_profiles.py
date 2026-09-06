import json
from pathlib import Path
import tempfile
import unittest
import sys
import shlex
from scripts import pilot_tool_guard
from scripts.pilot_tool_guard import guard
from scripts.efficiency_review import review
from scripts.future_worker_profile import command


class ProfileTests(unittest.TestCase):
    def test_future_command_has_no_local_file_tools(self):
        with tempfile.TemporaryDirectory() as d:
            config=Path(d)/'mcp.json';config.write_text('{"mcpServers":{}}')
            settings=Path(d)/'settings.json'
            settings.write_text(json.dumps({'permissions':{'allow':['mcp__colab-worker__get_cells']},'hooks':{'PreToolUse':[{'hooks':[{'command':shlex.join([sys.executable,pilot_tool_guard.__file__])}]}]}}))
            args=command(config,settings)
            self.assertEqual(args[args.index('--tools')+1],'ToolSearch')
            self.assertNotIn('*',args[args.index('--allowedTools')+1])

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
