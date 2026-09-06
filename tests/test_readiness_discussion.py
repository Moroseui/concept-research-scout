from types import SimpleNamespace
from pathlib import Path
import json
from unittest.mock import patch
from orchestrator.job_store import Store
from orchestrator.readiness_discussion import discuss


def test_one_system_discussion_per_completion_set(tmp_path):
    q=Store(tmp_path/'readiness.sqlite')
    v={'scope':'METADATA_ONLY_NOT_SCIENTIFIC_VALIDATION','binding':{'source':'a'*40,'handler':'context_inventory'},'facts':[],'finished':1}
    q.db.execute('INSERT INTO events VALUES(?,?,?)',('event','task',json.dumps(v)))
    with patch('orchestrator.readiness_discussion.execute',return_value={'status':'REVIEWED_PROPOSAL_NOT_ADOPTED'}) as call:
        first=discuss(SimpleNamespace(ROOT=tmp_path),tmp_path,tmp_path/'output','proposal')
        second=discuss(SimpleNamespace(ROOT=tmp_path),tmp_path,tmp_path/'output','proposal')
        assert call.call_count==1 and second['duplicate'] and first['identity']==second['identity']
        assert call.call_args.args[1]=='discuss'
